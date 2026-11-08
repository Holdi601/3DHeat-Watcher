"""
Single-player games read from memory, one adapter per profile the player has.

Profiles live in `<data>/profiles/*.json` (format: `heat3d_watch.memory`). None
ship with the tools - see there for why. Reading is off until `memory` is
switched on in the settings, and even then `safety.memory_allowed` decides per
launch; this adapter adds the checks that need the process open: that the
build is one the profile was written for, and that no anti-cheat module is
loaded in it.

Every read is kept besides the rows, in the session's raw sidecar
(`heat.raw.parquet`, `type` `values`): each value the profile names, by its
name as its own column - also the ones no event uses - and `unread` naming
those the chain did not reach that time. Nothing beyond the profile's values
is read for it: the raw sidecar keeps what was read, it never reads more.
"""

from __future__ import annotations

import logging
import time
from dataclasses import dataclass, field
from typing import Any

from ..config import load
from ..memory import Profile, ReadError, Reader, Resolver, main_module, read_image
from ..safety import loaded_anticheat
from ..session import Axes, Session
from .base import Adapter, Context

log = logging.getLogger("heat3d_watch")

#: Names the raw sidecar takes for itself: a profile value called so is kept as `value_<name>`.
_TAKEN = frozenset({"type", "payload", "text", "used", "t", "ms", "time", "unread"})


def raw_fields(now: dict[str, Any]) -> dict[str, Any]:
    """One read's values as the raw sidecar's columns: each by its name, and `unread` for those not reached."""
    out: dict[str, Any] = {}
    for name, v in now.items():
        if v is not None:
            out[f"value_{name}" if name in _TAKEN else name] = list(v) if isinstance(v, tuple) else v
    unread = [name for name, v in now.items() if v is None]
    if unread:
        out["unread"] = ",".join(unread)
    return out


@dataclass
class MemoryAdapter(Adapter):
    profile: Profile | None = None
    #: Played online sometimes: read only while it has no connection out (see safety).
    offline_check: bool = False
    _reader: Reader | None = None
    _resolver: Resolver | None = None
    _session: Session | None = None
    _last: dict[str, Any] = field(default_factory=dict)
    _next_try: float = 0.0

    def start(self, ctx: Context) -> None:
        self._close_reader()
        p = self.profile
        if p is None or ctx.pid is None or ctx.exe is None:
            return
        version = p.version_of(ctx.exe)
        if version is None:
            raise ReadError(f"{ctx.exe.name} is a build the profile does not list; not reading it")
        modules = loaded_anticheat(ctx.pid)
        if modules:
            raise ReadError("anti-cheat loaded in the game: " + ", ".join(modules))
        self._reader = Reader(ctx.pid)
        module = main_module(ctx.pid, ctx.exe)
        self._resolver = Resolver(self._reader, p, module.base, read_image(self._reader, module))
        self._session = ctx.open(self, meta={"profile": p.id, "build": version, "provenance": p.provenance})
        self._last = {}

    def poll(self, ctx: Context) -> None:
        if self._resolver is None or self._session is None:
            return
        s = self._session
        now: dict[str, Any] = {}
        for name in self.profile.values:  # type: ignore[union-attr]
            try:
                now[name] = self._resolver.read(name)
            except ReadError:
                # Between levels, in a menu, loading: the chain is not there yet.
                now[name] = None
        pos = now.get("pos")
        used = pos is not None
        if pos is not None:
            s.position(*pos, player="me")
        for rule in self.profile.events:  # type: ignore[union-attr]
            name, when = rule.get("value"), rule.get("when")
            old, new = self._last.get(name), now.get(name)
            if new is None or old is None:
                continue
            fired = (when == "change" and new != old) or (
                when == "to_zero" and isinstance(new, (int, float)) and new <= 0 < (old or 0)
            )
            if fired:
                at = pos if pos is not None else (None, None, None)
                s.event(rule["event"], x=at[0], y=at[1], z=at[2], player="me", value=new)
                s.stat(rule["event"], 1, "add")
                used = True
        # Every read whole: each value the profile names, the ones no row uses as well (docs/converters.md).
        s.raw("values", used=used, **raw_fields(now))
        self._last = now

    def stop(self, ctx: Context) -> None:
        ctx.close(self._session)
        self._session = None
        self._close_reader()

    def _close_reader(self) -> None:
        if self._reader is not None:
            self._reader.close()
        self._reader = None
        self._resolver = None


def _profiles() -> list[Profile]:
    folder = load().data_dir / "profiles"
    out = []
    for path in sorted(folder.glob("*.json")) if folder.is_dir() else []:
        try:
            out.append(Profile.load(path))
        except (ValueError, OSError) as e:
            log.warning("profile %s not used: %s", path.name, e)
    return out


def completeness(p: Profile) -> dict:
    """The converter rule's account of one profile (docs/converters.md)."""
    rate = max(1.0, min(60.0, float(p.rate)))
    # One item: about 90 bytes of head, and some 25 bytes per value as a named field.
    mb = rate * 3600 * (90 + 25 * len(p.values)) / 1e6
    return {
        "read": (
            "`pos` as the position rows; the values the profile's events watch, as those events (with the new "
            "value) and their counts",
            f"{len(p.values)} values, checked by the profile's author on the builds it lists; the game's build is "
            "matched by size or SHA-256 before anything is read",
        ),
        "raw": (
            "`values`: every read, each value the profile names as its own column (vectors as JSON lists) - "
            "also those no row uses - and `unread` naming the values whose chain was not there that time (a menu, "
            "a load); `used` is true when the read became a row or an event",
        ),
        "missing": (
            "everything in the game's memory the profile does not name: the watcher reads only the profile's "
            "values, read-only, single-player only, never near an anti-cheat (safety.py)",
            "reads on a build the profile does not list: nothing is read then",
        ),
        "size": f"{rate:g} reads a second of about {90 + 25 * len(p.values)} bytes: about {mb:.1f} MB per hour "
        "before compression, less with zstd",
    }


def _adapter(p: Profile) -> MemoryAdapter:
    axes = Axes(up=p.axes.get("up", "y"), units=p.axes.get("units", "game units"), scale=float(p.axes.get("scale", 1)))
    return MemoryAdapter(
        id=f"mem-{p.id}",
        game=p.game,
        kind="memory",
        exes=(p.exe,),
        multiplayer=bool(p.online),
        offline_check=bool(p.online),
        source=f"memory, read only, by the profile {p.id} (single-player only)",
        records=tuple(f"{k} ({v.get('type')})" for k, v in p.values.items()) + tuple(e["event"] for e in p.events),
        interval=1.0 / max(1.0, min(60.0, float(p.rate))),
        axes=axes,
        verified="by the profile's author, for the builds it lists",
        completeness=completeness(p),
        profile=p,
    )


ADAPTERS = [_adapter(p) for p in _profiles()]
