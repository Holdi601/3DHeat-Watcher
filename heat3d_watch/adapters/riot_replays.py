"""
League of Legends and Valorant replays: what of them can be read as it is.

Both games save replays to the player's disk, and both protect what is inside:
the moment-to-moment game data is obfuscated, and differently with every patch,
to keep it from being used to cheat. Getting through that means taking the
game's own code apart, which Riot's terms forbid (Terms of Service 3.1 and 7.1)
- so it is not done here. What each file carries in the open is read, and
the rest is kept as it is: every part of the file, whole, in the session's
`heat.raw.parquet` (3DHeat's converter rule, docs/converters.md in the
viewer's repository), counted in meta.json's `selfCheck.completeness`.

League of Legends (.rofl)
-------------------------
`%USERPROFILE%\\Documents\\League of Legends\\Replays\\*.rofl`. Both container
versions carry the end-of-game box score as plain JSON (`statsJson`): for each
of the ten players the champion, kills, deaths, assists, gold, damage to
champions, items, team, role, win, their Riot ID, and every other number the
game totals (over a hundred per player); all of them become the player's
`player_result` row. ROFL1 (patch 14.9 and before) has it after a fixed header
(`RIOT\\0\\0`, a 256-byte signature, then the lengths); ROFL2 (14.11 on,
`RIOT\\2\\0`) at the end of the file, its length in the last four bytes (stated
by a Riot engineer, ReplayBook issue 299). ROFL1's payload header (game id,
length, chunk and keyframe counts, the chunk key's length) and its table of
chunks (id, type, length, next chunk, offset) are in the open and read; the
chunks themselves are encrypted, and kept whole unread. Layouts from
roflxd.cs (MIT).

Positions do not come from the file. With a Riot developer key of the player's
own (`riot_api_key` in the settings; a personal key is meant for exactly this,
"showing (self) player stats"), the match's official timeline is fetched from
Riot's Match-V5 API: every player's position once a minute with everything the
minute's frame says of them (gold, experience, level, minions, champion and
damage statistics), and every event of the timeline - kills, buildings, elite
monsters, wards, items, skills, levels - each a row, where it happened when it
has a place. Without a key nothing is fetched and nothing is sent.

Valorant (.vrf)
---------------
`%LOCALAPPDATA%\\VALORANT\\Saved\\Demos\\*.vrf`, an Unreal Engine local replay
(layout from vrfkit, Apache-2.0, and ValorantReplayParser, MIT). In the open:
the replay's info block (length, network version, changelist, its name, when it
was recorded, whether it is compressed or encrypted), the map, the match id and
the agents picked (in the header), and the server's own event timeline - kills
(killer and victim as network ids, not names), rounds starting, spikes planted,
defused and exploding, ultimates used, sides switching - each with its time,
id and metadata. Positions, names, scores and everything else are in the
obfuscated stream (the replay data and checkpoint chunks), which is kept whole
and not read.
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


def _gaps(sections: list[tuple[str, int, int]], size: int) -> list[tuple[str, int, int]]:
    """
    A file's parts in order, with every stretch no part covers added as
    `unknown`: kept whole, so that the parts together are the whole file.
    Parts that overlap an earlier one are cut to what is new of them.
    """
    out: list[tuple[str, int, int]] = []
    at = 0
    for kind, start, end in sorted((s for s in sections if s[2] > s[1]), key=lambda s: (s[1], s[2])):
        start = max(start, at)
        end = min(end, size)
        if end <= start:
            continue
        if start > at:
            out.append(("unknown", at, start))
        out.append((kind, start, end))
        at = end
    if at < size:
        out.append(("unknown", at, size))
    return out


# --------------------------------------------------------------------- League

ROFL1 = b"RIOT\x00\x00"
ROFL2 = b"RIOT\x02\x00"
#: ROFL1's chunk table entry: id, type (1 chunk, 2 keyframe), length, next chunk id, offset from the data's start.
_CHUNK = struct.Struct("<IBIII")
_CHUNK_TYPES = {1: "chunk", 2: "keyframe"}


def read_rofl(buf: bytes) -> dict[str, Any]:
    """
    The plain parts of a .rofl: game length, version, each player's box score,
    the whole metadata; for ROFL1 also the payload header and the chunk
    table. `sections` names every part of the file by its byte range, each
    with what is read of it (`decoded`), so each can be kept whole.
    """
    sections: list[tuple[str, int, int]] = []
    decoded: dict[tuple[str, int], Any] = {}
    payload: dict[str, Any] = {}
    chunks: list[dict[str, Any]] = []
    if buf[:6] == ROFL1:
        header_len, file_len, meta_off, meta_len, ph_off, ph_len, payload_off = struct.unpack_from("<HIIIIII", buf, 262)
        meta = json.loads(buf[meta_off : meta_off + meta_len].decode("utf-8"))
        sections += [("magic", 0, 6), ("signature", 6, 262), ("lengths", 262, 288), ("metadata", meta_off, meta_off + meta_len)]
        decoded[("lengths", 262)] = {"header_length": header_len, "file_length": file_len, "metadata_offset": meta_off,
                                     "metadata_length": meta_len, "payload_header_offset": ph_off,
                                     "payload_header_length": ph_len, "payload_offset": payload_off}
        decoded[("magic", 0)] = {"container": 1}
        game_id = None
        if ph_off + 34 <= len(buf):
            game_id, length, keyframes, nchunks, end_startup, start_game, interval, key_len = struct.unpack_from(
                "<QIIIIIIH", buf, ph_off)
            key = buf[ph_off + 34 : ph_off + 34 + key_len]
            payload = {"game_id": game_id, "game_length": length, "keyframe_count": keyframes, "chunk_count": nchunks,
                       "end_startup_chunk_id": end_startup, "start_game_chunk_id": start_game,
                       "keyframe_interval": interval, "encryption_key_length": key_len,
                       "encryption_key": key.decode("latin-1")}
            sections.append(("payload_header", ph_off, ph_off + max(ph_len, 34 + key_len)))
            decoded[("payload_header", ph_off)] = payload
            table = payload_off
            data_start = payload_off + _CHUNK.size * (keyframes + nchunks)
            for i in range(keyframes + nchunks):
                at = table + i * _CHUNK.size
                if at + _CHUNK.size > len(buf):
                    break
                cid, ctype, clen, nxt, coff = _CHUNK.unpack_from(buf, at)
                entry = {"id": cid, "type": _CHUNK_TYPES.get(ctype, ctype), "length": clen, "next_chunk_id": nxt,
                         "offset": coff}
                chunks.append(entry)
                sections.append(("chunk_header", at, at + _CHUNK.size))
                decoded[("chunk_header", at)] = entry
                start = data_start + coff
                # The chunk's bytes: encrypted, kept whole.
                sections.append((str(_CHUNK_TYPES.get(ctype, f"chunk type {ctype}")), start, start + clen))
        version = meta.get("gameVersion", "")
        container = 1
    elif buf[:6] == ROFL2:
        (n,) = struct.unpack_from("<i", buf, len(buf) - 4)
        if n <= 0 or n > len(buf) - 4:
            raise ValueError("no metadata at the end of the replay")
        meta_off = len(buf) - 4 - n
        meta = json.loads(buf[meta_off : len(buf) - 4].decode("utf-8"))
        version = buf[14:29].split(b"\x00")[0].decode("utf-8", errors="replace").strip()
        game_id = None
        container = 2
        # Before the metadata: the game itself, in a layout not published; only the version is read of it.
        sections += [("body", 0, meta_off), ("metadata", meta_off, len(buf) - 4), ("metadata_length", len(buf) - 4, len(buf))]
        decoded[("body", 0)] = {"container": 2, "version": version}
        decoded[("metadata_length", len(buf) - 4)] = {"metadata_length": n}
    else:
        raise ValueError("not a League of Legends replay")
    decoded[("metadata", meta_off)] = {k: v for k, v in meta.items() if k != "statsJson"}
    stats = meta.get("statsJson", "[]")
    players = json.loads(stats) if isinstance(stats, str) else stats
    return {
        "container": container,
        "version": version,
        "length_ms": meta.get("gameLength"),
        "game_id": game_id,
        "players": players if isinstance(players, list) else [],
        "metadata": meta,
        "payload": payload,
        "chunks": chunks,
        "sections": [(kind, start, end, decoded.get((kind, start))) for kind, start, end in _gaps(sections, len(buf))],
    }


def _num(v: Any) -> float | None:
    try:
        return float(v)
    except (TypeError, ValueError):
        return None


def _plain(v: Any) -> Any:
    """A box score value as it is meant: numbers given as text become numbers."""
    if isinstance(v, str):
        n = _num(v)
        if n is not None and v.strip() and v.strip().lower() not in ("nan", "inf", "-inf", "infinity"):
            return int(n) if n.is_integer() and "." not in v else n
    return v


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

#: A row's own columns, which a box score's or timeline's field of the same name must not replace.
_RESERVED = {"t", "ms", "x", "y", "z", "player", "team", "session", "event"}


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


def _keep(s, buf: bytes, sections: list[tuple[str, int, int, Any]]) -> None:
    """Every part of a replay file whole in the raw sidecar, with what is read of it; the parts tile the file."""
    for kind, start, end, decoded in sections:
        s.raw(kind, buf[start:end], text=json.dumps(decoded, ensure_ascii=False) if decoded is not None else None,
              used=decoded is not None, t=0.0, offset=start)


@dataclass
class LolReplays(ReplayAdapter):
    #: Fetches the timeline; replaced in tests.
    opener: Any = None

    def folders(self, ctx: Context) -> list[Path]:
        base = Path(os.environ.get("USERPROFILE", str(Path.home()))) / "Documents" / "League of Legends" / "Replays"
        return [base] + super().folders(ctx)

    def convert(self, path: Path, ctx: Context) -> None:
        buf = path.read_bytes()
        r = read_rofl(buf)
        s = ctx.open(self, when=path.stat().st_mtime, meta={"replay": str(path), "version": r["version"]})
        try:
            me = ctx.settings.riot_id.strip().lower()
            mid = match_id(path, r, ctx.settings.riot_platform)
            s.meta["rofl"] = {"container": r["container"], "metadata": {k: v for k, v in r["metadata"].items()
                                                                        if k != "statsJson"},
                              "payload": r["payload"], "chunks": len(r["chunks"])}
            if r["length_ms"]:
                s.stat("game_seconds", round(float(r["length_ms"]) / 1000.0, 1))
            for p in r["players"]:
                who = riot_id(p)
                # Every number and name of the box score, under the game's own key; then the plain names.
                fields = {k: _plain(v) for k, v in p.items() if k not in _RESERVED}
                fields.update(
                    champion=p.get("SKIN"),
                    role=p.get("TEAM_POSITION") or p.get("INDIVIDUAL_POSITION"),
                    kills=_num(p.get("CHAMPIONS_KILLED")),
                    deaths=_num(p.get("NUM_DEATHS")),
                    assists=_num(p.get("ASSISTS")),
                    gold=_num(p.get("GOLD_EARNED")),
                    damage_to_champions=_num(p.get("TOTAL_DAMAGE_DEALT_TO_CHAMPIONS")),
                    win=p.get("WIN"),
                )
                s.event("player_result", t=(r["length_ms"] or 0) / 1000.0, player=who, team=p.get("TEAM"),
                        session=mid, **fields)
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
            _keep(s, buf, r["sections"])
            key = ctx.settings.riot_api_key.strip()
            if key and mid:
                timeline = fetch_timeline(mid, ctx.settings.riot_platform, key, self.opener or urllib.request.urlopen)
                if timeline:
                    record_timeline(s, timeline, r["players"], mid)
        finally:
            ctx.close(s)


def _flat(d: dict[str, Any], prefix: str = "") -> dict[str, Any]:
    """A timeline object's fields as one level: `championStats.armor`, `position.x`, ..."""
    out: dict[str, Any] = {}
    for k, v in d.items():
        if isinstance(v, dict):
            out.update(_flat(v, f"{prefix}{k}."))
        else:
            out[f"{prefix}{k}"] = v
    return out


def record_timeline(s, timeline: dict[str, Any], players: list[dict[str, Any]], mid: str) -> None:
    """
    Match-V5's timeline into rows: each player each minute, with everything the
    minute's frame says of them, and every event, where it happened when it has
    a place (a kill also as the victim's death).

    Its times are milliseconds into the game; the events that carry a
    `realTimestamp` too (the game's first PAUSE_END, its GAME_END) give the
    wall clock, so the rows get their real `ms` and the session its real start,
    and an NVIDIA highlight saved during the game finds the player's rows.

    The timeline is kept whole besides, in the raw sidecar: each event under
    `timeline <type>`, each player's frame under `timeline participantFrame`,
    and the rest (metadata, participants, the frames' times) under `timeline`.
    """
    info = timeline.get("info", {})
    start_ms = next(
        (float(e["realTimestamp"]) - float(e.get("timestamp", 0))
         for frame in info.get("frames", []) for e in frame.get("events", [])
         if isinstance(e.get("realTimestamp"), (int, float)) and e["realTimestamp"] > 0),
        None,
    )
    if start_ms is not None:
        s.started = start_ms / 1000.0

    def wall(t: float) -> float | None:
        return start_ms + t * 1000.0 if start_ms is not None else None

    by_puuid = {p.get("PUUID"): p for p in players if p.get("PUUID")}
    names: dict[int, tuple[str, Any]] = {}
    for part in info.get("participants", []):
        p = by_puuid.get(part.get("puuid"), {})
        pid = int(part.get("participantId", 0))
        names[pid] = (riot_id(p) if p else f"participant {pid}", p.get("TEAM"))

    def who(pid: Any, default: str = "?") -> tuple[str, Any]:
        try:
            return names.get(int(pid), (f"participant {pid}", None)) if pid else (default, None)
        except (TypeError, ValueError):
            return default, None

    rest = {k: v for k, v in timeline.items() if k != "info"}
    rest["info"] = {k: v for k, v in info.items() if k != "frames"}
    rest["info"]["frames"] = [{k: v for k, v in f.items() if k not in ("events", "participantFrames")}
                              for f in info.get("frames", [])]
    s.raw("timeline", text=json.dumps(rest, ensure_ascii=False), used=True, t=0.0)
    for frame in info.get("frames", []):
        t = float(frame.get("timestamp", 0)) / 1000.0
        for pid, pf in (frame.get("participantFrames") or {}).items():
            s.raw("timeline participantFrame", text=json.dumps(pf, ensure_ascii=False), used=True, t=t, ms=wall(t),
                  participant=str(pid))
            name, team = who(pid, f"participant {pid}")
            fields = {k: v for k, v in _flat(pf).items() if k not in _RESERVED and not k.startswith("position.")}
            fields["gold"] = pf.get("totalGold")
            pos = pf.get("position")
            if pos:
                s.event("position", t=t, ms=wall(t), x=pos.get("x"), y=0.0, z=pos.get("y"), player=name, team=team,
                        session=mid, **fields)
            else:
                s.event("participant_frame", t=t, ms=wall(t), player=name, team=team, session=mid, **fields)
        for e in frame.get("events", []):
            kind = str(e.get("type", ""))
            t_e = float(e.get("timestamp", 0)) / 1000.0
            s.raw(f"timeline {kind}", text=json.dumps(e, ensure_ascii=False), used=True, t=t_e, ms=wall(t_e))
            pos = e.get("position") or {}
            fields = {k: (json.dumps(v) if isinstance(v, (list, dict)) else v) for k, v in _flat(e).items()
                      if k not in _RESERVED and k != "type" and not k.startswith("position.")}
            place = {"x": pos.get("x"), "y": 0.0, "z": pos.get("y")} if pos else {}
            if kind == "CHAMPION_KILL" and pos:
                killer = who(e.get("killerId"), "minion or tower")
                victim = who(e.get("victimId"))
                s.event("kill", t=t_e, ms=wall(t_e), **place, player=killer[0], team=killer[1], session=mid,
                        **{**fields, "victim": victim[0]})
                s.event("death", t=t_e, ms=wall(t_e), **place, player=victim[0], team=victim[1], session=mid,
                        **{**fields, "killer": killer[0]})
                continue
            actor = next((e[k] for k in ("participantId", "killerId", "creatorId") if e.get(k)), None)
            name, team = who(actor, "") if actor else ("", None)
            s.event(kind.lower() or "timeline_event", t=t_e, ms=wall(t_e), **place, player=name or None, team=team,
                    session=mid, **fields)


# -------------------------------------------------------------------- Valorant

VRF_MAGIC = 0x43F4EFDD
_GROUP = b"EReplayEventGroup::"
#: The chunk types of an Unreal local replay.
VRF_CHUNKS = {0: "header", 1: "replay_data", 2: "checkpoint", 3: "event"}


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

    An encrypted replay is walked the same way, its chunks' contents left
    unread. `sections` names every part of the file by its byte range, each with
    what is read of it, so each can be kept whole.
    """
    (magic, file_version) = struct.unpack_from("<II", buf, 0)
    if magic != VRF_MAGIC:
        raise ValueError("not an Unreal replay")
    at = 8
    (versions,) = struct.unpack_from("<i", buf, at)
    custom = [buf[at + 4 + i * 20 : at + 24 + i * 20].hex() for i in range(max(0, versions))]
    at += 4 + max(0, versions) * 20
    length_ms, network, changelist = struct.unpack_from("<iII", buf, at)
    at += 12
    friendly, at = _fstring(buf, at)
    live, ticks, compressed, encrypted = struct.unpack_from("<IqII", buf, at)
    at += 20
    (key_len,) = struct.unpack_from("<i", buf, at)
    key = buf[at + 4 : at + 4 + max(0, key_len)]
    at += 4 + max(0, key_len)
    info = {"magic": magic, "file_version": file_version, "custom_versions": custom, "length_ms": length_ms,
            "network_version": network, "changelist": changelist, "name": friendly, "is_live": bool(live),
            "timestamp_ticks": ticks, "compressed": bool(compressed), "encrypted": bool(encrypted),
            "encryption_key_length": key_len, "encryption_key": key.hex()}
    out: dict[str, Any] = {
        "file_version": file_version,
        "length_ms": length_ms,
        "name": friendly,
        "recorded_unix": ticks / 1e7 - 62135596800 if ticks > 0 else None,
        "encrypted": bool(encrypted),
        "info": info,
        "map": None,
        "match_id": None,
        "agents": [],
        "events": [],
        "sections": [("info", 0, at, info)],
    }
    while at + 8 <= len(buf):
        kind, size = struct.unpack_from("<Ii", buf, at)
        if size < 0 or at + 8 + size > len(buf):
            break
        start = at
        at += 8
        chunk = buf[at : at + size]
        at += size
        name = VRF_CHUNKS.get(kind, f"chunk {kind}")
        decoded: Any = None
        if not encrypted and kind == 0:
            _header(chunk, out)
            decoded = {k: out[k] for k in ("map", "match_id", "agents")}
        elif not encrypted and kind == 3:
            ev = _event(chunk)
            if ev:
                out["events"].append(ev)
                decoded = ev
                name = f"event {ev['group']}"
        out["sections"].append((name, start, at, decoded))
    if at < len(buf):
        # After the last whole chunk: a chunk cut short, or bytes the layout does not describe.
        out["sections"].append(("trailing", at, len(buf), None))
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
        event_id, at = _fstring(chunk, 0)
        group, at = _fstring(chunk, at)
        meta, at = _fstring(chunk, at)
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
            "words": words, "chunk_group": group, "id": event_id, "metadata": meta}


@dataclass
class ValorantReplays(ReplayAdapter):
    def folders(self, ctx: Context) -> list[Path]:
        base = Path(os.environ.get("LOCALAPPDATA", "")) / "VALORANT" / "Saved" / "Demos"
        return [base] + super().folders(ctx)

    def convert(self, path: Path, ctx: Context) -> None:
        buf = path.read_bytes()
        r = read_vrf(buf)
        when = r["recorded_unix"] or path.stat().st_mtime
        s = ctx.open(self, when=when, meta={"replay": str(path), "map": r["map"], "match_id": r["match_id"],
                                            "agents": r["agents"], "vrf": r["info"]})
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
                s.event(ev["event"], t=t, session=f"{mid} round {max(1, rounds)}", **extra, group=ev["group"],
                        event_id=ev["id"], metadata=ev["metadata"], time_ms=ev["time_ms"], end_ms=ev["end_ms"],
                        words=ev["words"])
            s.stat("rounds", rounds)
            s.stat("kills_in_match", sum(1 for e in r["events"] if e["event"] == "kill"))
            s.stat("spikes_planted", sum(1 for e in r["events"] if e["event"] == "spike_planted"))
            if r["length_ms"]:
                s.stat("match_seconds", round(r["length_ms"] / 1000.0, 1))
            if r["map"]:
                s.stat("map", r["map"].rsplit("/", 1)[-1])
            _keep(s, buf, r["sections"])
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
            "each player's champion, role, team, kills, deaths, assists, gold, damage to champions and result, "
            "and every other number of the end-of-game box score",
            "your own line as statistics, and your rows named as yours (meta.json `player`), with your Riot ID "
            "in the settings",
            "with your own Riot API key: every player's position each minute with the minute's statistics, and "
            "every event of the timeline (kills where they happened, buildings, monsters, wards, items, skills), "
            "at the wall-clock time the timeline gives",
            "every part of the replay file kept whole in heat.raw.parquet; not decoded: the moment-to-moment game, "
            "which is encrypted and obfuscated against cheating",
        ),
        enable="save a replay in the League client (match history > download); for positions set riot_api_key "
        "and riot_platform with `config --set`",
        axes=Axes(up="y", units="Summoner's Rift map units (about 15000 across)"),
        verified="the metadata reader tested on files built to the layouts in roflxd.cs (MIT); the timeline on "
        "Match-V5's documented JSON; no real replay was available to check against",
        multiplayer=True,
        completeness={
            "read": (
                "the metadata JSON: game length, version, last chunk and keyframe ids, and `statsJson` - every "
                "field of every player's box score on their `player_result` row (numbers given as text read as "
                "numbers)",
                "ROFL1: the lengths block, the payload header (game id, game length, keyframe and chunk counts, "
                "startup and game start chunk ids, keyframe interval, the chunk key as it is stored) and the chunk "
                "table (id, type, length, next chunk, offset) - in meta.json `rofl` and the raw rows' `text`",
                "ROFL2: the version string",
                "the Match-V5 timeline (own API key only): every participant frame on a `position` row (or "
                "`participant_frame` without a place) with all its fields flattened (`championStats.armor`, "
                "`damageStats.totalDamageDone`, `currentGold`, `xp`, ...); every event as a row named after its "
                "type, placed where it has a `position`, CHAMPION_KILL as a kill and a death",
            ),
            "raw": (
                "every part of the .rofl, whole, in file order (`offset`), so the parts are the file: `magic`, "
                "`signature`, `lengths`, `metadata`, `payload_header`, `chunk_header`, `chunk`, `keyframe` "
                "(ROFL1); `body`, `metadata`, `metadata_length` (ROFL2); any stretch no part covers as `unknown`",
                "the timeline whole: `timeline <type>` for each event, `timeline participantFrame` for each "
                "player's frame (`participant` its id), `timeline` for the rest",
            ),
            "missing": (
                "the game itself (positions, abilities, every unit, moment to moment): ROFL1's chunks and ROFL2's "
                "body are encrypted and the packets inside obfuscated with every patch; getting through means "
                "taking the client apart, which Riot's terms forbid (3.1, 7.1). Kept whole, not read",
                "positions without your own Riot API key: the file has none in the open",
            ),
            "size": "the raw sidecar is about the replay's own size: the encrypted chunks do not compress",
        },
    ),
    ValorantReplays(
        id="valorant-replays",
        game="VALORANT",
        patterns=("*.vrf",),
        source="replays VALORANT saves: %LOCALAPPDATA%/VALORANT/Saved/Demos/*.vrf (only the parts that are not "
        "obfuscated)",
        records=(
            "the map, the match id and the agents picked; the replay's info block (length, versions, name, "
            "recording time, compression and encryption flags)",
            "the server's event timeline: kills (killer and victim as network ids), rounds starting, spikes "
            "planted, defused and exploding, ultimates used, sides switching - each with its id and metadata",
            "every chunk of the file kept whole in heat.raw.parquet; not decoded: positions, names or scores - "
            "they are in the obfuscated stream",
        ),
        enable="save a replay in VALORANT (career > match > download replay)",
        axes=Axes(up="z", units="VALORANT world units"),
        verified="built from the container layout documented by vrfkit (Apache-2.0); untested on a real "
        "replay, none was available - checks before reading and skips what does not match",
        multiplayer=True,
        completeness={
            "read": (
                "the info block, every field (meta.json `vrf`): file version, custom versions, length, network "
                "version, changelist, name, live flag, recording time, compressed and encrypted flags, the key as "
                "stored",
                "the header chunk: the map, the match id and the agents picked (looked up by their form)",
                "every event chunk: id, group, metadata, start and end time, and of its data the event's name, "
                "its time in seconds and the numbers before it (killer and victim network ids) - a row each",
            ),
            "raw": (
                "every chunk whole, in file order (`offset`), so the parts are the file: `info`, `header`, "
                "`event <group>`, `replay_data`, `checkpoint`, `chunk <n>` for a type the layout does not name, "
                "`trailing` for bytes after the last whole chunk",
            ),
            "missing": (
                "positions, names, scores, abilities, every frame of the game: the replay data and checkpoint "
                "chunks are obfuscated; reading them means taking the client apart, which Riot's terms forbid. "
                "Kept whole, not read",
                "an encrypted replay's contents: walked and kept whole, nothing read inside",
            ),
            "size": "the raw sidecar is about the replay's own size: the obfuscated stream does not compress",
        },
    ),
]
