"""
EVE Online: the client's game logs, `Documents\\EVE\\logs\\Gamelogs\\*.txt`.

The client writes one file per character per login,
`<yyyymmdd>_<hhmmss>[_<character id>].txt`; logging to file is on by default. Several clients running side by
side each write their own, so every file written since the game started is
followed. Header and lines (EVE time is UTC):

    ------------------------------------------------------------
      Gamelog
      Listener: Character Name
      Session Started: 2024.07.02 19:41:40
    ------------------------------------------------------------
    [ 2024.07.02 20:31:28 ] (combat) <color=0xff00ffff><b>200</b> <color=0x77ffffff><font size=10>to</font>
        <b><color=0xffffffff>Pilot[TICK](Ship)</b><font size=10><color=0x77ffffff> - Weapon - Penetrates
    [ 2024.06.25 15:20:01 ] (combat) <color=0xffcc0000><b>375</b> ... from ... - Weapon - Hits
    [ 2024.06.25 15:21:00 ] (bounty) <font size=12><b><color=0xff00aa00>15,000 ISK</b> added to next bounty payout
    [ 2024.06.25 15:30:00 ] (None) Jumping from System A to System B

(the combat line is one line in the file). Formatting tags are stripped before
matching. The file has been UTF-8 and UTF-16 over the years; both are read.
The format is not documented by CCP; it is the client's plain-text log, read as
community combat-log tools read it (e.g. https://docs.rs/crate/eve-log-parser).
No positions.

Beside it, `Documents\\EVE\\logs\\Chatlogs\\<channel>_<yyyymmdd>_<hhmmss>[_<id>].txt`:
one file per chat channel per login (when chat logging is on, the client's
default), UTF-16, a header naming the channel and the listener, then
`[ yyyy.mm.dd hh:mm:ss ] Sender > message`.

Every line of both is kept whole in the session's raw sidecar (3DHeat's
converter rule): a gamelog line under its channel in brackets (`combat`,
`notify`, `bounty`, `None`, ...), a chat line as `chat` with its channel, the
header lines as `gamelog header` / `chatlog header`.
"""

from __future__ import annotations

import os
import re
import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path

from ..session import Axes, Session
from ._logfollow import Follower, SLACK, game_started
from .base import Adapter, Context

_TAGS = re.compile(r"<[^>]*>")
_LINE = re.compile(r"^\[ (\d{4}\.\d{2}\.\d{2} \d{2}:\d{2}:\d{2}) \] \((\w+)\) ?(.*)$")
_LISTENER = re.compile(r"^\s*Listener: (.+?)\s*$")
_HIT = re.compile(r"^(\d+) (to|from) (.+?) - (.+?)(?: - ([A-Za-z][A-Za-z ]*))?\s*$")
_MISS_OUT = re.compile(r"^Your (?:group of )?(.+?) misses (.+?) completely(?: - (.+))?$")
_MISS_IN = re.compile(r"^(.+?) misses you completely(?: - (.+))?$")
_BOUNTY = re.compile(r"^([\d,.]+) ISK added to next bounty payout")
_JUMP = re.compile(r"Jumping from (.+?) to (.+?)\.?\s*$")
_WHO = re.compile(r"^(?P<name>[^\[(]+?)\s*(?:\[(?P<corp>[^\]]*)\])?\s*(?:\((?P<ship>[^)]*)\))?$")
_STAMP = re.compile(r"^\[ (\d{4}\.\d{2}\.\d{2} \d{2}:\d{2}:\d{2}) \]")
_CHANNEL = re.compile(r"^\s*Channel Name:\s*(.+?)\s*$")


def line_time(line: str) -> float | None:
    m = _STAMP.match(line)
    if not m:
        return None
    return datetime.strptime(m.group(1), "%Y.%m.%d %H:%M:%S").replace(tzinfo=timezone.utc).timestamp()


def gamelog_dirs() -> list[Path]:
    home = Path(os.environ.get("USERPROFILE") or Path.home())
    out = [home / "Documents" / "EVE" / "logs" / "Gamelogs"]
    for env in ("OneDrive", "OneDriveConsumer"):
        if os.environ.get(env):
            out.append(Path(os.environ[env]) / "Documents" / "EVE" / "logs" / "Gamelogs")
    return out


class Gamelog:
    """Lines of one character's gamelog into the session: damage, misses, bounties, jumps; every line kept whole."""

    def __init__(self, session_for, file: str = ""):
        self.session_for = session_for
        self.file = file
        self.me: str | None = None
        self.used = False

    def line(self, text: str) -> None:
        if not text.strip():
            return
        m = _LINE.match(text)
        ts = line_time(text) if m else None
        self.used = False
        try:
            self._line(text, m, ts or time.time())
        finally:
            # The line whole, whatever became of it (docs/converters.md, "Live sources").
            s = self.session_for(ts)
            when = ts or time.time()
            s.raw(m.group(2) if m else "gamelog header", text=text, used=self.used, t=when - s.started,
                  ms=when * 1000, file=self.file, listener=self.me)

    def _line(self, text: str, m: re.Match | None, ts: float) -> None:
        if self.me is None and (h := _LISTENER.match(text)) is not None:
            self.me = h.group(1)
            return
        if not m:
            return
        kind, body = m.group(2), _TAGS.sub("", m.group(3)).strip()
        body = re.sub(r"\s+", " ", body)
        me = self.me or "me"

        def ev(name: str, **kw) -> Session:
            s = self.session_for(ts)
            s.event(name, t=ts - s.started, ms=ts * 1000, **kw)
            self.used = True
            return s

        if kind == "combat":
            if (h := _HIT.match(body)) is not None:
                amount, way, other, weapon, quality = h.groups()
                who = _WHO.match(other.strip())
                name = who.group("name").strip() if who else other
                ship = who.group("ship") if who else None
                corp = (who.group("corp") or None) if who else None  # the ticker in brackets after the pilot
                if way == "to":
                    s = ev("damage_dealt", player=me, target=name, target_ship=ship, target_corp=corp,
                           damage=int(amount), weapon=weapon, quality=quality)
                    s.stat("damage_dealt", int(amount), "add")
                    s.stat("hits_dealt", 1, "add")
                else:
                    s = ev("damage_received", player=me, attacker=name, attacker_ship=ship, attacker_corp=corp,
                           damage=int(amount), weapon=weapon, quality=quality)
                    s.stat("damage_received", int(amount), "add")
                    s.stat("hits_received", 1, "add")
            elif (h := _MISS_IN.match(body)) is not None:
                s = ev("miss_received", player=me, attacker=h.group(1))
                s.stat("misses_received", 1, "add")
            elif (h := _MISS_OUT.match(body)) is not None:
                s = ev("miss_dealt", player=me, weapon=h.group(1), target=h.group(2))
                s.stat("misses_dealt", 1, "add")
        elif kind == "bounty" and (b := _BOUNTY.match(body)) is not None:
            isk = float(b.group(1).replace(",", ""))
            s = ev("bounty", player=me, isk=isk)
            s.stat("bounty_kills", 1, "add")
            s.stat("bounty_isk", isk, "add")
        elif (j := _JUMP.search(body)) is not None:
            s = ev("jump", player=me, origin=j.group(1), destination=j.group(2))
            s.stat("jumps", 1, "add")


class Chatlog:
    """Lines of one chat channel's log: kept whole, with the channel and the listener; nothing made of them yet."""

    def __init__(self, session_for, file: str = ""):
        self.session_for = session_for
        self.file = file
        self.channel: str | None = None
        self.me: str | None = None

    def line(self, text: str) -> None:
        if not text.strip():
            return
        ts = line_time(text)
        if ts is None:
            if (h := _CHANNEL.match(text)) is not None:
                self.channel = h.group(1)
            elif (h := _LISTENER.match(text)) is not None:
                self.me = h.group(1)
        s = self.session_for(ts)
        when = ts or time.time()
        s.raw("chat" if ts is not None else "chatlog header", text=text, t=when - s.started, ms=when * 1000,
              file=self.file, channel=self.channel, listener=self.me)


@dataclass
class EveAdapter(Adapter):
    #: Gamelogs folder; empty: Documents\EVE\logs\Gamelogs. The chat logs are its sibling Chatlogs.
    folder: Path | None = None
    _session: Session | None = field(default=None, repr=False)
    _files: dict[Path, tuple[Follower, Gamelog | Chatlog]] = field(default_factory=dict, repr=False)
    _since: float = field(default=0.0, repr=False)
    _next_scan: float = field(default=0.0, repr=False)
    #: Logs of earlier logins: never written again (each login writes new files), so not looked at again.
    _old: set[Path] = field(default_factory=set, repr=False)

    def folders(self) -> list[Path]:
        return [Path(self.folder)] if self.folder else gamelog_dirs()

    def chat_folders(self) -> list[Path]:
        return [f.parent / "Chatlogs" for f in self.folders()]

    def start(self, ctx: Context) -> None:
        self._session = None
        self._files = {}
        self._old = set()
        self._next_scan = 0.0
        self._since = game_started(ctx.pid)

    def _session_for(self, ctx: Context):
        def session_for(ts: float | None) -> Session:
            if self._session is None:
                self._session = ctx.open(self, when=ts if ts and abs(time.time() - ts) < 86400 else None)
            return self._session

        return session_for

    def _scan(self, ctx: Context) -> None:
        for kind, folders in ((Gamelog, self.folders()), (Chatlog, self.chat_folders())):
            for folder in folders:
                for path in folder.glob("*.txt"):
                    if path in self._files or path in self._old:
                        continue
                    try:
                        if path.stat().st_mtime < self._since - SLACK:
                            self._old.add(path)
                            continue
                    except OSError:
                        continue
                    follower = Follower(lambda p=path: p, self._since, line_time)
                    self._files[path] = (follower, kind(self._session_for(ctx), path.name))

    def poll(self, ctx: Context) -> None:
        if time.monotonic() >= self._next_scan:
            self._next_scan = time.monotonic() + 2.0
            self._scan(ctx)
        for follower, log in self._files.values():
            for line in follower.iter_lines():
                try:
                    log.line(line)
                except (ValueError, IndexError):
                    if self._session is not None:
                        self._session.stat("bad_lines", 1, "add")

    def stop(self, ctx: Context) -> None:
        self._next_scan = 0.0  # a channel opened since the last look still counts
        self.poll(ctx)
        ctx.close(self._session)
        self._session = None
        self._files = {}
        self._old = set()


ADAPTERS = [
    EveAdapter(
        id="eve",
        game="EVE Online",
        kind="log",
        exes=("exefile.exe",),
        multiplayer=True,
        source=r"%USERPROFILE%\Documents\EVE\logs\Gamelogs\*.txt and the Chatlogs\*.txt beside them (every file "
        r"written since the client started)",
        records=(
            "damage dealt and received with the other ship, pilot, corporation ticker, weapon and hit quality",
            "misses dealt and received",
            "bounties paid (NPC kills) with ISK",
            "jumps between systems",
            "every gamelog and chat log line whole in heat.raw.parquet",
            "damage dealt and received, hits, misses, bounty kills and ISK, jumps",
        ),
        enable="",
        interval=0.5,
        axes=Axes(units="no positions recorded"),
        verified="tested on synthetic gamelog lines in the format published by community parsers; untested "
        "against the game",
        completeness={
            "read": (
                "gamelog `(combat)` hits dealt and received (amount, other pilot, corporation ticker, ship, weapon, "
                "hit quality) and misses both ways",
                "gamelog `(bounty)` payouts with ISK, and the `Jumping from A to B` lines",
                "the gamelog header's Listener: whose log it is",
            ),
            "raw": (
                "every gamelog line whole, `type` = its channel in brackets (`combat`, `notify`, `info`, "
                "`bounty`, `mining`, `question`, `hint`, `warning`, `None`, ...), with `file` and `listener`; "
                "`used` where it became a row; the header lines as `gamelog header`",
                "every chat log line whole (Local, corporation, fleet, private channels, the `EVE System` notices "
                "such as a change of Local channel on a jump), `type` `chat`, with `channel`, `listener` and "
                "`file`; the header lines as `chatlog header`. Not made into rows yet",
                "the formatting tags (`<color>`, `<b>`, `<font>`) stay in the raw text; rows have them stripped",
            ),
            "missing": (
                "positions: the client writes none to its logs",
                "other pilots' fights: a gamelog is the listener's own",
                "logs of earlier logins: each login writes new files; those older than this run of the client "
                "are not read again",
                "chat when the player has switched chat logging off in the client's settings",
                "the client's own cache and settings files: not logs, and not documented",
            ),
            "size": "a gamelog is 0.1-2 MB per hour (most in combat); chat logs depend on the channels open - "
            "a busy Local or fleet channel 0.5-3 MB per hour; zstd in heat.raw.parquet makes it roughly a tenth",
        },
    )
]
