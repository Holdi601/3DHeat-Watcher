"""
Gunner, HEAT, PC!: the missions the 3DHeat recorder mod writes.

The game keeps no replays and publishes no telemetry. The recorder (a
MelonLoader mod, `mods/ghpc`, installed with `setup ghpc --apply` or
`ghpc install`) writes each mission into one `.3dheat` file in
`%LOCALAPPDATA%/3DHeat/Watcher/recorders/ghpc`; the viewer opens those files
as they are. This adapter watches that folder and files each new mission as a
session: the file linked (or copied) into the session folder, its numbers into
the statistics.
"""

from __future__ import annotations

import io
import json
import logging
import os
import shutil
import zipfile
from dataclasses import dataclass
from pathlib import Path

from .. import ghpc
from ..session import Axes
from .base import Context
from .replays import ReplayAdapter

log = logging.getLogger("heat3d_watch")

ADAPTERS: list = []


def read_container(path: Path) -> tuple[dict, dict, bytes | None]:
    """A recorder file's manifest, match document and table bytes."""
    with zipfile.ZipFile(path) as z:
        man = json.loads(z.read("manifest.json"))
        roles = man.get("roles") or {}
        doc = json.loads(z.read(roles["match"])) if roles.get("match") in z.namelist() else {}
        table = z.read(roles["table"]) if roles.get("table") in z.namelist() else None
    return man, doc, table


def mission_stats(doc: dict, events: dict[str, int]) -> dict[str, float | str]:
    """The numbers a mission gives the statistics: what it was, how it went, the player's own line."""
    out: dict[str, float | str] = {"map": str(doc.get("map") or ""), "mission": str(doc.get("mission") or "")}
    result = doc.get("result") or {}
    if result.get("outcome"):
        out["outcome"] = str(result["outcome"])
    if isinstance(doc.get("timePlayed"), (int, float)):
        out["seconds"] = float(doc["timePlayed"])
    units = doc.get("units") or []
    me = next((u for u in units if u.get("isPlayer")), None)
    out["units"] = len(units)
    out["shots"] = events.get("launch", 0)
    out["kills_total"] = len(doc.get("kills") or [])
    if me:
        out["vehicle"] = str(me.get("vehicleName") or me.get("vehicle") or "")
        out["kills"] = sum(1 for k in doc.get("kills") or [] if k.get("killer") == me.get("name"))
        out["deaths"] = 1 if me.get("out") else 0
        if result.get("winner"):
            out["won"] = 1 if result.get("winner") == me.get("team") else 0
    return out


@dataclass
class GhpcRecorder(ReplayAdapter):
    _said: bool = False

    def folders(self, ctx: Context) -> list[Path]:
        return [ghpc.output_folder()] + super().folders(ctx)

    def setup(self, ctx: Context, *, apply: bool) -> list[str]:
        st = ghpc.status()
        todo, blocked = ghpc.plan(st)
        if blocked:
            return [f"cannot: {b}" for b in blocked]
        if apply and todo:
            ghpc.install(yes=True, log=lambda s: log.info("ghpc: %s", s))
        return todo

    def start(self, ctx: Context) -> None:
        super().start(ctx)
        if self._said:
            return
        self._said = True
        line = ghpc.check_line()
        if not line["ok"]:
            log.info("%s: %s", self.id, line["detail"])

    def convert(self, path: Path, ctx: Context) -> None:
        man, doc, table = read_container(path)
        session = ctx.open(self, when=path.stat().st_mtime, meta={"recording": str(path), "match": man.get("match")})
        try:
            target = session.folder / path.name
            try:
                os.link(path, target)  # same disk: the file once, two names
            except OSError:
                shutil.copy2(path, target)
            events: dict[str, int] = {}
            rows = 0
            if table is not None:
                import pyarrow.parquet as pq

                col = pq.read_table(io.BytesIO(table), columns=["event"]).column("event").to_pylist()
                rows = len(col)
                for e in col:
                    if e is not None:
                        events[e] = events.get(e, 0) + 1
            with session._lock:
                for e, n in events.items():
                    session.counts[e] = session.counts.get(e, 0) + n
                session.positions += rows
            for k, v in mission_stats(doc, events).items():
                session.stat(k, v)
            session.meta["mission"] = {k: doc.get(k) for k in ("match", "mission", "map", "started", "timePlayed", "result", "gameVersion")}
        finally:
            ctx.close(session)


ADAPTERS.append(
    GhpcRecorder(
        id="ghpc",
        game="Gunner, HEAT, PC!",
        kind="log",
        patterns=("*.3dheat",),
        source="the 3DHeat recorder, a MelonLoader mod (mods/ghpc) the player installs: one .3dheat file a "
        "mission in %LOCALAPPDATA%/3DHeat/Watcher/recorders/ghpc, which the viewer opens directly",
        records=(
            "every unit's position, heading, pitch, roll and speed 10 times a second (1 a second while it "
            "stands still), its turret's traverse and gun's elevation, side, vehicle and crew",
            "every round fired: shooter, weapon, ammunition, calibre, muzzle velocity, and where it ended",
            "hits: the unit struck, the point on it and the round's way in its own frame, the plate, the "
            "impact angle and speed, penetrated or not, further plates and fragments",
            "what hits did: crew knocked out, parts destroyed, fires, ammunition going up, units out of the "
            "fight and who did it; the game's own account of each shot",
            "the mission, its map, its states, how it ended and how long it took; the game's log lines",
        ),
        enable="install MelonLoader (github.com/LavaGang/MelonLoader/releases) and start the game once, "
        "then `python -m heat3d_watch setup ghpc --apply` puts the recorder in",
        axes=Axes(up="y", flip_z=True, units="metres (x east, y up, z north)"),
        verified="the file format by tests (a synthetic mission written by the mod's own writer, read by "
        "pyarrow and the viewer); the mod has not run in the game yet, and the names it reads in the game "
        "are taken from public mods, so its first run writes a probe of what it found",
        multiplayer=False,
        completeness={
            "read": ("units", "samples", "rounds fired", "hits and plates", "damage", "kills", "mission states", "result"),
            "raw": ("every line of the game's log while a mission runs, in the file's raw sidecar (a line said "
                    "more than 20 times is counted)",),
            "missing": ("what the game does not expose to a mod at the names the recorder knows: those parts stay empty, "
                        "and the probe in each file lists them",),
            "size": "about 20 bytes a sample: some 15 MB for half an hour with 40 units",
        },
    )
)
