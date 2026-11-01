"""
League of Legends and Valorant replays: what of them can be read as it is.

Both games save replays to the player's disk, and both protect what is inside:
the moment-to-moment game data is obfuscated, and differently with every patch,
to keep it from being used to cheat. Getting through that means taking the
game's own code apart, which Riot's terms forbid (Terms of Service 3.1 and 7.1)
- so it is not done here. What each file carries in the open is read, and
nothing else.

League of Legends (.rofl)
-------------------------
`%USERPROFILE%\\Documents\\League of Legends\\Replays\\*.rofl`. Both container
versions carry the end-of-game box score as plain JSON (`statsJson`): for each
of the ten players the champion, kills, deaths, assists, gold, damage to
champions, items, team, role, win, and their Riot ID. ROFL1 (patch 14.9 and
before) has it after a fixed header (`RIOT\\0\\0`, a 256-byte signature, then
the lengths); ROFL2 (14.11 on, `RIOT\\2\\0`) at the end of the file, its length in
the last four bytes (stated by a Riot engineer, ReplayBook issue 299). Layouts
from roflxd.cs (MIT).

Positions do not come from the file. With a Riot developer key of the player's
own (`riot_api_key` in the settings; a personal key is meant for exactly this,
"showing (self) player stats"), the match's official timeline is fetched from
Riot's Match-V5 API: every player's position once a minute and every kill where
it happened, on Summoner's Rift's map coordinates. Without a key nothing is
fetched and nothing is sent.

Valorant (.vrf)
---------------
`%LOCALAPPDATA%\\VALORANT\\Saved\\Demos\\*.vrf`, an Unreal Engine local replay
(layout from vrfkit, Apache-2.0, and ValorantReplayParser, MIT). In the open:
the map, the match id and the agents picked (in the header), and the server's
own event timeline - kills (killer and victim as network ids, not names),
rounds starting, spikes planted, defused and exploding, ultimates used, sides
switching - each with its time. Positions, names, scores and everything else
are in the obfuscated stream and are not read.
"""

from __future__ import annotations

import json
import logging
import os
import re
import struct
import urllib.error
import urllib.request
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from ..session import Axes
from .base import Context
from .replays import ReplayAdapter

log = logging.getLogger("heat3d_watch")

# --------------------------------------------------------------------- League

ROFL1 = b"RIOT\x00\x00"
ROFL2 = b"RIOT\x02\x00"


def read_rofl(buf: bytes) -> dict[str, Any]:
    """The plain metadata of a .rofl: game length, version, and each player's box score."""
    if buf[:6] == ROFL1:
        header_len, file_len, meta_off, meta_len = struct.unpack_from("<HIII", buf, 262)
        meta = json.loads(buf[meta_off : meta_off + meta_len].decode("utf-8"))
        payload_off = struct.unpack_from("<I", buf, 262 + 14)[0]
        game_id = struct.unpack_from("<Q", buf, payload_off)[0] if payload_off + 8 <= len(buf) else None
        version = meta.get("gameVersion", "")
        container = 1
    elif buf[:6] == ROFL2:
        (n,) = struct.unpack_from("<i", buf, len(buf) - 4)
        if n <= 0 or n > len(buf) - 4:
            raise ValueError("no metadata at the end of the replay")
        meta = json.loads(buf[len(buf) - 4 - n : len(buf) - 4].decode("utf-8"))
        version = buf[14:29].split(b"\x00")[0].decode("utf-8", errors="replace").strip()
        game_id = None
        container = 2
    else:
        raise ValueError("not a League of Legends replay")
    stats = meta.get("statsJson", "[]")
    players = json.loads(stats) if isinstance(stats, str) else stats
    return {
        "container": container,
        "version": version,
        "length_ms": meta.get("gameLength"),
        "game_id": game_id,
        "players": players if isinstance(players, list) else [],
    }


def _num(v: Any) -> float | None:
    try:
        return float(v)
    except (TypeError, ValueError):
        return None


def riot_id(p: dict[str, Any]) -> str:
    name = p.get("RIOT_ID_GAME_NAME") or p.get("NAME") or ""
    tag = p.get("RIOT_ID_TAG_LINE") or ""
    return f"{name}#{tag}" if tag else str(name)


#: Platform id -> the regional host Match-V5 lives on.
REGIONS = {
    "NA1": "americas", "BR1": "americas", "LA1": "americas", "LA2": "americas",
    "KR": "asia", "JP1": "asia",
    "EUN1": "europe", "EUW1": "europe", "TR1": "europe", "RU": "europe", "ME1": "europe",
    "OC1": "sea", "SG2": "sea", "TW2": "sea", "VN2": "sea", "PH2": "sea", "TH2": "sea",
}  # fmt: skip


def match_id(path: Path, read: dict[str, Any], platform: str) -> str | None:
    """`EUW1_1234567890`: from the file name the client gives a replay, else the header's game id."""
    m = re.match(r"([A-Za-z]+\d*)-(\d+)", path.stem)
    if m:
        return f"{m.group(1).upper()}_{m.group(2)}"
    if read.get("game_id"):
        return f"{platform.upper()}_{read['game_id']}"
    return None


def fetch_timeline(mid: str, platform: str, key: str, opener=urllib.request.urlopen) -> dict[str, Any] | None:
    region = REGIONS.get(mid.split("_")[0].upper(), REGIONS.get(platform.upper(), "europe"))
    request = urllib.request.Request(
        f"https://{region}.api.riotgames.com/lol/match/v5/matches/{mid}/timeline",
        headers={"X-Riot-Token": key, "User-Agent": "3DHeat-Watcher"},
    )
    try:
        with opener(request, timeout=15) as response:
            return json.loads(response.read())
    except (urllib.error.URLError, OSError, ValueError) as e:
        log.warning("lol-replays: no timeline for %s: %s", mid, e)
        return None


@dataclass
class LolReplays(ReplayAdapter):
    #: Fetches the timeline; replaced in tests.
    opener: Any = None

    def folders(self, ctx: Context) -> list[Path]:
        base = Path(os.environ.get("USERPROFILE", str(Path.home()))) / "Documents" / "League of Legends" / "Replays"
        return [base] + super().folders(ctx)

    def convert(self, path: Path, ctx: Context) -> None:
        r = read_rofl(path.read_bytes())
        s = ctx.open(self, when=path.stat().st_mtime, meta={"replay": str(path), "version": r["version"]})
        try:
            me = ctx.settings.riot_id.strip().lower()
            mid = match_id(path, r, ctx.settings.riot_platform)
            if r["length_ms"]:
                s.stat("game_seconds", round(float(r["length_ms"]) / 1000.0, 1))
            for p in r["players"]:
                who = riot_id(p)
                s.event(
                    "player_result",
                    t=(r["length_ms"] or 0) / 1000.0,
                    player=who,
                    team=p.get("TEAM"),
                    session=mid,
                    champion=p.get("SKIN"),
                    role=p.get("TEAM_POSITION") or p.get("INDIVIDUAL_POSITION"),
                    kills=_num(p.get("CHAMPIONS_KILLED")),
                    deaths=_num(p.get("NUM_DEATHS")),
                    assists=_num(p.get("ASSISTS")),
                    gold=_num(p.get("GOLD_EARNED")),
                    damage_to_champions=_num(p.get("TOTAL_DAMAGE_DEALT_TO_CHAMPIONS")),
                    win=p.get("WIN"),
                )
                if me and who.lower() == me:
                    s.meta["player"] = who
                    s.stat("champion", str(p.get("SKIN") or ""))
                    for key, name in (
                        ("CHAMPIONS_KILLED", "kills"),
                        ("NUM_DEATHS", "deaths"),
                        ("ASSISTS", "assists"),
                        ("GOLD_EARNED", "gold"),
                        ("TOTAL_DAMAGE_DEALT_TO_CHAMPIONS", "damage_to_champions"),
                        ("MINIONS_KILLED", "minions"),
                        ("VISION_SCORE", "vision_score"),
                    ):
                        v = _num(p.get(key))
                        if v is not None:
                            s.stat(name, v)
                    s.stat("won", 1 if str(p.get("WIN", "")).lower() in ("win", "true", "1") else 0)
            key = ctx.settings.riot_api_key.strip()
            if key and mid:
                timeline = fetch_timeline(mid, ctx.settings.riot_platform, key, self.opener or urllib.request.urlopen)
                if timeline:
                    record_timeline(s, timeline, r["players"], mid)
        finally:
            ctx.close(s)


def record_timeline(s, timeline: dict[str, Any], players: list[dict[str, Any]], mid: str) -> None:
    """Match-V5's timeline into positions: each player each minute, each kill where it happened."""
    info = timeline.get("info", {})
    by_puuid = {p.get("PUUID"): p for p in players if p.get("PUUID")}
    names: dict[int, tuple[str, Any]] = {}
    for part in info.get("participants", []):
        p = by_puuid.get(part.get("puuid"), {})
        pid = int(part.get("participantId", 0))
        names[pid] = (riot_id(p) if p else f"participant {pid}", p.get("TEAM"))
    for frame in info.get("frames", []):
        t = float(frame.get("timestamp", 0)) / 1000.0
        for pid, pf in (frame.get("participantFrames") or {}).items():
            pos = pf.get("position")
            if not pos:
                continue
            who, team = names.get(int(pid), (f"participant {pid}", None))
            s.event("position", t=t, x=pos.get("x"), y=0.0, z=pos.get("y"), player=who, team=team, session=mid,
                    level=pf.get("level"), gold=pf.get("totalGold"))
        for e in frame.get("events", []):
            pos = e.get("position")
            if e.get("type") != "CHAMPION_KILL" or not pos:
                continue
            t_e = float(e.get("timestamp", 0)) / 1000.0
            killer = names.get(int(e.get("killerId", 0)), ("minion or tower", None))
            victim = names.get(int(e.get("victimId", 0)), ("?", None))
            s.event("kill", t=t_e, x=pos["x"], y=0.0, z=pos["y"], player=killer[0], team=killer[1], session=mid,
                    victim=victim[0])
            s.event("death", t=t_e, x=pos["x"], y=0.0, z=pos["y"], player=victim[0], team=victim[1], session=mid,
                    killer=killer[0])


# -------------------------------------------------------------------- Valorant

VRF_MAGIC = 0x43F4EFDD
_GROUP = b"EReplayEventGroup::"


def _fstring(buf: bytes, at: int) -> tuple[str, int]:
    """An Unreal FString: an int32 length (negative: UTF-16), then the characters with their terminator."""
    (n,) = struct.unpack_from("<i", buf, at)
    at += 4
    if n == 0:
        return "", at
    if n > 0:
        raw = buf[at : at + n]
        return raw.split(b"\x00")[0].decode("latin-1"), at + n
    size = -n * 2
    return buf[at : at + size].decode("utf-16-le", errors="replace").split("\x00")[0], at + size


def read_vrf(buf: bytes) -> dict[str, Any]:
    """
    The open parts of a Valorant replay: header facts and the event timeline.

    The replay's info block is read field by field (vrfkit's layout); the chunks
    after it are walked by their type and size. Inside the header chunk the map
    and the match's own JSON are looked up by what they look like, not by offset:
    the fields before them change between builds, and a reader that guessed an
    offset would read a wrong map with confidence.
    """
    (magic, file_version) = struct.unpack_from("<II", buf, 0)
    if magic != VRF_MAGIC:
        raise ValueError("not an Unreal replay")
    at = 8
    (versions,) = struct.unpack_from("<i", buf, at)
    at += 4 + max(0, versions) * 20
    length_ms, _network, _changelist = struct.unpack_from("<iII", buf, at)
    at += 12
    friendly, at = _fstring(buf, at)
    _live, ticks, compressed, encrypted = struct.unpack_from("<IqII", buf, at)
    at += 20
    (key_len,) = struct.unpack_from("<i", buf, at)
    at += 4 + max(0, key_len)
    if encrypted:
        raise ValueError("this replay is encrypted; it is not read")
    out: dict[str, Any] = {
        "file_version": file_version,
        "length_ms": length_ms,
        "name": friendly,
        "recorded_unix": ticks / 1e7 - 62135596800 if ticks > 0 else None,
        "map": None,
        "match_id": None,
        "agents": [],
        "events": [],
    }
    while at + 8 <= len(buf):
        kind, size = struct.unpack_from("<Ii", buf, at)
        at += 8
        if size < 0 or at + size > len(buf):
            break
        chunk = buf[at : at + size]
        at += size
        if kind == 0:
            _header(chunk, out)
        elif kind == 3:
            ev = _event(chunk)
            if ev:
                out["events"].append(ev)
    return out


def _header(chunk: bytes, out: dict[str, Any]) -> None:
    text = chunk.decode("latin-1")
    m = re.search(r"/Game/Maps/[A-Za-z0-9_/]+", text)
    if m:
        out["map"] = m.group(0)
    m = re.search(r'"matchI[Dd]"\s*:\s*"([0-9a-fA-F-]{8,})"', text)
    if m:
        out["match_id"] = m.group(1)
    out["agents"] = sorted(set(re.findall(r'"characterId"\s*:\s*"([0-9a-fA-F-]{36})"', text)))


#: The server's event groups, as the watcher names them.
EVENTS = {
    "characterDeath": "kill",
    "roundStarted": "round_start",
    "spikePlanted": "spike_planted",
    "spikeDefused": "spike_defused",
    "spikeExploded": "spike_exploded",
    "characterUltimateUsed": "ultimate",
    "switchTeams": "switch_sides",
}


def _event(chunk: bytes) -> dict[str, Any] | None:
    try:
        _id, at = _fstring(chunk, 0)
        group, at = _fstring(chunk, at)
        _meta, at = _fstring(chunk, at)
        time1, time2, size = struct.unpack_from("<IIi", chunk, at)
        at += 12
        payload = chunk[at : at + max(0, size)]
    except struct.error:
        return None
    mark = payload.find(_GROUP)
    if mark < 4:
        return None
    end = payload.find(b"\x00", mark)
    name = payload[mark + len(_GROUP) : end].decode("latin-1")
    words_end = mark - 4  # the FString's length sits before its text
    words = list(struct.unpack_from(f"<{max(0, (words_end - 4) // 4)}I", payload, 4)) if words_end > 4 else []
    seconds = None
    if end + 5 <= len(payload):
        (seconds,) = struct.unpack_from("<f", payload, end + 1)
    return {"group": name, "event": EVENTS.get(name, name), "time_ms": time1, "end_ms": time2, "seconds": seconds,
            "words": words, "chunk_group": group}


@dataclass
class ValorantReplays(ReplayAdapter):
    def folders(self, ctx: Context) -> list[Path]:
        base = Path(os.environ.get("LOCALAPPDATA", "")) / "VALORANT" / "Saved" / "Demos"
        return [base] + super().folders(ctx)

    def convert(self, path: Path, ctx: Context) -> None:
        r = read_vrf(path.read_bytes())
        when = r["recorded_unix"] or path.stat().st_mtime
        s = ctx.open(self, when=when, meta={"replay": str(path), "map": r["map"], "match_id": r["match_id"],
                                            "agents": r["agents"]})
        try:
            mid = r["match_id"] or path.stem
            rounds = 0
            for ev in r["events"]:
                t = ev["seconds"] if ev["seconds"] is not None else ev["time_ms"] / 1000.0
                extra: dict[str, Any] = {}
                if ev["event"] == "kill" and len(ev["words"]) >= 2:
                    extra = {"player": f"netguid {ev['words'][0]}", "victim": f"netguid {ev['words'][1]}"}
                if ev["event"] == "round_start":
                    rounds += 1
                s.event(ev["event"], t=t, session=f"{mid} round {max(1, rounds)}", **extra)
            s.stat("rounds", rounds)
            s.stat("kills_in_match", sum(1 for e in r["events"] if e["event"] == "kill"))
            s.stat("spikes_planted", sum(1 for e in r["events"] if e["event"] == "spike_planted"))
            if r["length_ms"]:
                s.stat("match_seconds", round(r["length_ms"] / 1000.0, 1))
            if r["map"]:
                s.stat("map", r["map"].rsplit("/", 1)[-1])
        finally:
            ctx.close(s)


ADAPTERS = [
    LolReplays(
        id="lol-replays",
        game="League of Legends",
        patterns=("*.rofl",),
        source="replays the League client saves: %USERPROFILE%/Documents/League of Legends/Replays/*.rofl "
        "(the plain end-of-game metadata only); with your own Riot API key, the match's official timeline "
        "from Riot's Match-V5 API",
        records=(
            "each player's champion, role, team, kills, deaths, assists, gold, damage to champions and result",
            "your own line as statistics, with your Riot ID in the settings",
            "with your own Riot API key: every player's position each minute and every kill where it happened",
            "not: the moment-to-moment game, which is obfuscated against cheating and not decoded",
        ),
        enable="save a replay in the League client (match history > download); for positions set riot_api_key "
        "and riot_platform with `config --set`",
        axes=Axes(up="y", units="Summoner's Rift map units (about 15000 across)"),
        verified="the metadata reader tested on files built to the layouts in roflxd.cs (MIT); the timeline on "
        "Match-V5's documented JSON; no real replay was available to check against",
        multiplayer=True,
    ),
    ValorantReplays(
        id="valorant-replays",
        game="VALORANT",
        patterns=("*.vrf",),
        source="replays VALORANT saves: %LOCALAPPDATA%/VALORANT/Saved/Demos/*.vrf (only the parts that are not "
        "obfuscated)",
        records=(
            "the map, the match id and the agents picked",
            "the server's event timeline: kills (killer and victim as network ids), rounds starting, spikes "
            "planted, defused and exploding, ultimates used, sides switching",
            "not: positions, names or scores - they are in the obfuscated stream, which is not decoded",
        ),
        enable="save a replay in VALORANT (career > match > download replay)",
        axes=Axes(up="z", units="VALORANT world units"),
        verified="built from the container layout documented by vrfkit (Apache-2.0); untested on a real "
        "replay, none was available - checks before reading and skips what does not match",
        multiplayer=True,
    ),
]
