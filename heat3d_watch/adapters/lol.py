"""
League of Legends: the Live Client Data API the game client serves during a match.

While a match runs (also in practice tool and spectator mode), `League of
Legends.exe` answers on https://127.0.0.1:2999 with what the player can see in
the game's own interface:

    /liveclientdata/allgamedata          activePlayer (riotId, level, currentGold, championStats),
                                         allPlayers (championName, team ORDER/CHAOS, level,
                                         scores: kills, deaths, assists, creepScore, wardScore),
                                         events, gameData (gameMode, gameTime s, mapName)
    /liveclientdata/eventdata?eventID=N  {"Events": [...]} from EventID N on: GameStart,
                                         MinionsSpawning, FirstBlood, FirstBrick, TurretKilled,
                                         InhibKilled, InhibRespawningSoon, InhibRespawned,
                                         DragonKill, HeraldKill, BaronKill, ChampionKill
                                         (KillerName, VictimName, Assisters), Multikill
                                         (KillStreak), Ace (Acer, AcingTeam), GameEnd (Result)

There are no positions: the API has none, so a League session is events and
statistics, without a heat table. The certificate is self-signed, by Riot's own
root (`riotgames.pem`, published at
https://static.developer.riotgames.com/docs/lol/riotgames.pem). Its terms of
use are not stated, so it is not shipped: put it at `<data>\\riotgames.pem` and
the connection is verified with it; without it verification is off - and only
ever for 127.0.0.1, the one address this adapter talks to.

Riot's policy allows tools to show what the player could know from the game
itself, and nothing computed beyond it (no enemy timers): this records the kill
feed and the scoreboard the player sees, and the player's own numbers.

Every reply is also kept whole (3DHeat's converter rule, docs/converters.md in
the viewer's repository): `heat.raw.parquet`, `type` the endpoint
("allgamedata", "eventdata"), `text` the JSON as the client sent it, `status`
when it was not 200. A reply byte for byte the one before of its endpoint (the
event list while nothing happens) is kept once and counted in meta.json's
`unchanged_replies`. allgamedata holds everything the other endpoints serve
(activeplayer*, playerlist, playerscores, playeritems, playersummonerspells,
playermainrunes, gamestats), so they are not asked separately. Replies before
a match (the loading screen) wait in a backlog and go into the match's session;
after GameEnd the session stays open until the client goes, so the end screen's
replies are kept with it.

Source: https://developer.riotgames.com/docs/lol#game-client-api
"""

from __future__ import annotations

import json
import logging
import re
import ssl
import time
import urllib.error
import urllib.request
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

from ..session import Axes, Session
from .base import Adapter, Context
from .gsi import Backlog, Repeats

log = logging.getLogger("heat3d_watch")

LOCAL_HOSTS = ("127.0.0.1", "localhost")

#: Event fields the kill feed reads by name; every other field of an event goes on its row as it is.
EVENT_READ = {"EventID", "EventName", "EventTime", "KillerName", "VictimName", "Assisters", "Acer", "AcingTeam",
              "Recipient", "Result", "DragonType", "Stolen", "KillStreak", "TurretKilled", "InhibKilled"}
#: Row columns an event field may not take as it is.
RESERVED = {"t", "time", "ms", "event", "x", "y", "z", "player", "team", "session"}

#: Objectives counted for the player's team: event -> statistic.
OBJECTIVES = {
    "DragonKill": "team_dragons",
    "BaronKill": "team_barons",
    "HeraldKill": "team_heralds",
    "TurretKilled": "team_turrets",
    "InhibKilled": "team_inhibitors",
}


def snake(name: str) -> str:
    return re.sub(r"(?<!^)(?=[A-Z])", "_", name).lower()


def structure_owner(name: str) -> str | None:
    """`Turret_T1_L_03_A`, `Barracks_T2_R1`: T1 is ORDER's, T2 CHAOS's."""
    found = re.search(r"_T([12])_", name or "")
    return None if not found else "ORDER" if found.group(1) == "1" else "CHAOS"


@dataclass
class LolLive(Adapter):
    #: The API's base. Only 127.0.0.1 is ever asked; http is accepted for tests' fake servers.
    url: str = "https://127.0.0.1:2999"
    #: Riot's root certificate, when the player has it. Empty: `<data>\riotgames.pem` if it is there.
    cafile: str = ""
    #: Seconds between scoreboard reads (events are asked for every poll).
    scoreboard_every: float = 2.0
    #: Seconds without an answer before a match counts as over.
    gone_after: float = 30.0
    _ssl: ssl.SSLContext | None = None
    _session: Session | None = None
    _next_event: int = 0
    _seen: set[int] = field(default_factory=set)
    _me: set[str] = field(default_factory=set)
    _team: str | None = None
    _names: dict[str, tuple[str, str]] = field(default_factory=dict)
    _game_time: float = 0.0
    _last_board: float = 0.0
    _last_answer: float = 0.0
    _done: bool = False
    _bad: int = 0
    _backlog: Backlog = field(default_factory=Backlog)
    _repeats: Repeats = field(default_factory=Repeats)

    def missing(self) -> str | None:
        host = urlparse(self.url).hostname or ""
        if host not in LOCAL_HOSTS:
            return f"the Live Client API is local: {self.url} is not 127.0.0.1"
        return None

    # -- talking to the client -----------------------------------------------------

    def _context(self, ctx: Context) -> ssl.SSLContext:
        pem = Path(self.cafile) if self.cafile else ctx.data / "riotgames.pem"
        if pem.is_file():
            c = ssl.create_default_context(cafile=str(pem))
            # The client's certificate is issued to a name, not to 127.0.0.1; the chain is what is checked.
            c.check_hostname = False
            return c
        c = ssl.create_default_context()
        c.check_hostname = False
        c.verify_mode = ssl.CERT_NONE
        return c

    def fetch(self, path: str) -> tuple[float, int, bytes] | None:
        """(wall time, HTTP status, body) of an answer - an error status with its body too - or None for none."""
        if self.missing():
            return None
        url = self.url.rstrip("/") + path
        try:
            kw = {"context": self._ssl} if url.startswith("https:") else {}
            with urllib.request.urlopen(url, timeout=0.5, **kw) as r:
                return time.time(), int(r.status), r.read()
        except urllib.error.HTTPError as e:
            # The loading screen's "RESOURCE_NOT_FOUND": an answer, kept like any other.
            try:
                return time.time(), int(e.code), e.read()
            except OSError:
                return None
        except (urllib.error.URLError, OSError, ValueError):
            return None

    @staticmethod
    def parse(reply: tuple[float, int, bytes] | None) -> Any:
        """A 200 answer's JSON, else None."""
        if reply is None or reply[1] != 200:
            return None
        try:
            return json.loads(reply[2].decode("utf-8"))
        except (ValueError, UnicodeDecodeError):
            return None

    def get(self, path: str) -> Any:
        """The answer as JSON, or None while the client has nothing (loading, no match, gone)."""
        return self.parse(self.fetch(path))

    def _keep(self, ctx: Context, kind: str, reply: tuple[float, int, bytes] | None, used: bool) -> None:
        """One reply, whole: into the match's raw feed, or the backlog before it opens."""
        if reply is None:
            return
        when, status, body = reply
        try:
            text, payload = body.decode("utf-8"), None
        except UnicodeDecodeError:
            text, payload = None, body
        if self._repeats.same(kind, body):
            return
        fields = {"status": status} if status != 200 else {}
        s = self._session
        if s is not None:
            s.raw(kind, payload, text=text, used=used, ms=when * 1000, **fields)
        else:
            self._backlog.add(when, kind, payload, text=text, **fields)
            if self._backlog.full:
                self._flush_backlog(ctx)

    def _flush_backlog(self, ctx: Context) -> None:
        counts = dict(self._repeats.counts)
        self._backlog.flush(ctx, self, **({"unchanged_replies": counts} if counts else {}))
        self._repeats.counts.clear()

    # -- lifecycle -----------------------------------------------------------------

    def start(self, ctx: Context) -> None:
        self._ssl = self._context(ctx)
        self._backlog = Backlog()
        self._repeats = Repeats()
        self._reset()

    def _reset(self) -> None:
        self._session = None
        self._next_event = 0
        self._seen = set()
        self._me = set()
        self._team = None
        self._names = {}
        self._game_time = 0.0
        self._last_board = 0.0
        self._last_answer = time.monotonic()
        self._done = False

    def stop(self, ctx: Context) -> None:
        self._end(ctx)
        # A client that never got past the loading screen: its answers in a session of their own.
        self._flush_backlog(ctx)

    def _end(self, ctx: Context) -> None:
        if self._session is not None:
            if self._bad:
                self._session.stat("bad_packets", self._bad)
            self._repeats.into(self._session)
            self._repeats.reset()
            ctx.close(self._session)
            self._session = None

    def poll(self, ctx: Context) -> None:
        now = time.monotonic()
        board = None
        if self._session is None or now - self._last_board >= self.scoreboard_every:
            reply = self.fetch("/liveclientdata/allgamedata")
            board = self.parse(reply)
            if reply is not None and reply[1] == 200 and board is None:
                self._bad += 1
            self._last_board = now
            used = False
            if isinstance(board, dict) and isinstance(board.get("gameData"), dict):
                used = self._scoreboard(ctx, board)
            else:
                board = None
            self._keep(ctx, "allgamedata", reply, used)
        if self._session is None:
            # Loading screen: nothing to ask for events yet.
            return
        reply = self.fetch(f"/liveclientdata/eventdata?eventID={self._next_event}")
        got = self.parse(reply)
        if reply is not None and reply[1] == 200 and got is None:
            self._bad += 1
        events = got.get("Events") if isinstance(got, dict) else None
        if events is None and board is not None:
            events = (board.get("events") or {}).get("Events")
        seen = len(self._seen)
        if isinstance(events, list):
            self._last_answer = now
            for e in sorted((e for e in events if isinstance(e, dict)), key=lambda e: e.get("EventID", 0)):
                self._event(ctx, e)
        self._keep(ctx, "eventdata", reply, len(self._seen) > seen and isinstance(got, dict))
        if not isinstance(events, list) and board is None and now - self._last_answer > self.gone_after:
            self._end(ctx)
            self._reset()

    # -- what it says ----------------------------------------------------------------

    def _scoreboard(self, ctx: Context, board: dict[str, Any]) -> bool:
        """Read the scoreboard; False when there was nothing to read it into (the match is over)."""
        self._last_answer = time.monotonic()
        gd = board["gameData"]
        gt = float(gd.get("gameTime") or 0)
        if self._session is not None and gt + 5 < self._game_time:
            # The clock went back: another match in the same client.
            self._end(ctx)
            self._reset()
        if self._done:
            return False
        self._game_time = max(self._game_time, gt)
        ap = board.get("activePlayer") if isinstance(board.get("activePlayer"), dict) else {}
        self._me = {str(ap.get(k)) for k in ("riotId", "riotIdGameName", "summonerName") if ap.get(k)}
        players = [p for p in board.get("allPlayers") or [] if isinstance(p, dict)]
        mine = None
        for p in players:
            champ, team = str(p.get("championName") or ""), str(p.get("team") or "")
            for k in ("riotId", "riotIdGameName", "summonerName"):
                if p.get(k):
                    self._names[str(p[k])] = (champ, team)
            if self._me & {str(p.get(k)) for k in ("riotId", "riotIdGameName", "summonerName") if p.get(k)}:
                mine = p
        if self._session is None:
            self._session = ctx.open(self, meta={k: v for k, v in {
                "game_mode": gd.get("gameMode"), "map": gd.get("mapName"),
                "champion": mine.get("championName") if mine else None}.items() if v})
            # The loading screen's answers lead into the match.
            self._backlog.into(self._session)
        s = self._session
        s.stat("game_time", round(gt, 1), "max")
        if mine is not None:
            self._team = str(mine.get("team") or "") or None
            sc = mine.get("scores") if isinstance(mine.get("scores"), dict) else {}
            for key, stat in (("kills", "kills"), ("deaths", "deaths"), ("assists", "assists"),
                              ("creepScore", "creep_score"), ("wardScore", "ward_score")):
                if key in sc:
                    s.stat(stat, round(float(sc[key]), 2))
            if mine.get("championName"):
                s.stat("champion", str(mine["championName"]))
        if "level" in ap:
            s.stat("level", int(ap["level"]), "max")
        if "currentGold" in ap:
            s.stat("gold", round(float(ap["currentGold"]), 1))
        return True

    def _who(self, name: Any) -> dict[str, Any]:
        name = str(name or "")
        champ, team = self._names.get(name, ("", ""))
        return {"name": name, "champion": champ or None, "team": team or None, "me": name in self._me}

    def _event(self, ctx: Context, e: dict[str, Any]) -> None:
        s = self._session
        try:
            eid = int(e.get("EventID"))
            name = str(e["EventName"])
            t = float(e.get("EventTime") or 0)
        except (TypeError, ValueError, KeyError):
            self._bad += 1
            return
        if eid in self._seen or s is None or self._done:
            return
        self._seen.add(eid)
        self._next_event = max(self._next_event, eid + 1)
        attrs: dict[str, Any] = {"event_id": eid}
        kind = snake(name)
        player: str | None = None
        team: str | None = None
        killer = self._who(e.get("KillerName")) if "KillerName" in e else None
        if killer is not None:
            attrs.update(killer=killer["name"], killer_champion=killer["champion"])
            player, team = ("me" if killer["me"] else killer["name"]), killer["team"]
        assisters = [str(a) for a in e.get("Assisters") or [] if a]
        if assisters:
            attrs["assisters"] = assisters
        if name == "ChampionKill":
            victim = self._who(e.get("VictimName"))
            attrs.update(victim=victim["name"], victim_champion=victim["champion"], victim_team=victim["team"])
            if killer and killer["me"]:
                kind = "kill"
            elif victim["me"]:
                kind, player, team = "death", "me", victim["team"]
            elif self._me & set(assisters):
                kind = "assist"
            else:
                kind = "champion_kill"
        elif name in ("TurretKilled", "InhibKilled"):
            building = str(e.get(name) or "")
            owner = structure_owner(building)
            attrs.update(building=building, building_team=owner)
            if owner:
                team = "CHAOS" if owner == "ORDER" else "ORDER"
        elif name == "DragonKill":
            attrs.update(dragon=e.get("DragonType"), stolen=str(e.get("Stolen", "")).lower() == "true")
        elif name in ("BaronKill", "HeraldKill"):
            attrs["stolen"] = str(e.get("Stolen", "")).lower() == "true"
        elif name == "Multikill":
            attrs["streak"] = e.get("KillStreak")
        elif name == "Ace":
            ace = self._who(e.get("Acer"))
            attrs.update(acer=ace["name"], acer_champion=ace["champion"])
            player, team = ("me" if ace["me"] else ace["name"]), str(e.get("AcingTeam") or "") or None
        elif name == "FirstBlood":
            r = self._who(e.get("Recipient"))
            player, team = ("me" if r["me"] else r["name"]), r["team"]
        elif name == "GameEnd":
            res = str(e.get("Result") or "")
            result = "win" if res.lower() == "win" else "loss" if res.lower() in ("lose", "loss") else res.lower()
            attrs["result"] = result
            s.stat("result", result)
        # Fields of events the feed above does not read by name (newer events, newer fields), as they are.
        for k, v in e.items():
            if k in EVENT_READ or not (isinstance(v, (str, int, float, bool)) or (
                    isinstance(v, list) and all(isinstance(x, (str, int, float)) for x in v))):
                continue
            key = snake(k)
            attrs.setdefault(f"game_{key}" if key in RESERVED else key, v)
        s.event(kind, t=t, player=player, team=team, **attrs)
        if name in OBJECTIVES and self._team and team == self._team:
            s.stat(OBJECTIVES[name], 1, "add")
        if name == "GameEnd":
            # No more rows; the session stays open for the end screen's answers until the client goes.
            self._done = True


ADAPTERS = [
    LolLive(
        id="lol-live",
        game="League of Legends",
        kind="gsi",
        exes=("League of Legends.exe",),
        interval=0.5,
        source="Live Client Data API of the game client, https://127.0.0.1:2999/liveclientdata/ "
        "(allgamedata, eventdata), during a match",
        records=(
            "no positions: the API has none",
            "kill feed: kills, deaths and assists of the player, other champion kills with killer, victim, assisters",
            "dragons, heralds, barons, turrets, inhibitors, multikills, aces, first blood, game start and end",
            "own kills, deaths, assists, creep score, ward score, level, gold, champion, game time, result",
            "objectives taken by the player's team",
        ),
        enable="",
        axes=Axes(up="z", units="none (no positions)"),
        verified="tested against a fake local server serving answers in the documented format; "
        "untested against the game (not installed here)",
        completeness={
            "read": (
                "the kill feed from eventdata: every event once, its named fields decoded (killer, victim and "
                "assisters with champion and team, structures and their side, dragon type, steals, multikills, "
                "aces, first blood, the result) and every other field of an event on its row under its own name",
                "from allgamedata: the own kills, deaths, assists, creep score, ward score, level, gold, champion, "
                "the game time, game mode and map",
            ),
            "raw": (
                "`allgamedata`: every answer whole (`text`), every 2 s - activePlayer (abilities, every champion "
                "stat, full runes, gold, level), allPlayers (items with slots and prices, runes, summoner spells, "
                "scores, level, dead and respawn timer, skin, lane, bot), the events, gameData (mode, time, map, "
                "terrain); `used` true while the match runs, false on the end screen",
                "`eventdata`: every answer whole, asked every 0.5 s from the next event id on; `used` true when "
                "it brought new events",
                "an answer byte for byte the one before of its endpoint is kept once and counted "
                "(`unchanged_replies` in meta.json); error answers (the loading screen's RESOURCE_NOT_FOUND) are "
                "kept with their `status`, before the match's start",
            ),
            "missing": (
                "positions: the API has none (no minimap, no coordinates)",
                "the other endpoints (activeplayer, activeplayername, activeplayerabilities, activeplayerrunes, "
                "playerlist, playerscores, playersummonerspells, playermainrunes, playeritems, gamestats): each "
                "serves a part of allgamedata, so they are not asked",
                "the Replay API (`/replay/*` on the same port): it plays back replays and spectated games once "
                "switched on in game.cfg, it is not part of a played match",
                "the League client's lockfile endpoints: not a published API (Sources and rules)",
                "values between two reads: the API answers when asked and does not push; the scoreboard is asked "
                "every 2 s, the events every 0.5 s",
            ),
            "size": "allgamedata is 15-40 KB (it carries the whole event list, which grows) every 2 s: about "
            "30-70 MB per hour in `raw.bin`; eventdata adds little, as unchanged answers are counted, not stored; "
            "zstd shrinks the repeated JSON in `heat.raw.parquet` to a few MB per hour (estimated from the "
            "documented format)",
        },
    ),
]
