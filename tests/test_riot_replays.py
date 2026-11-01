"""League of Legends and Valorant replays: only what each file carries in the open."""

from __future__ import annotations

import io
import json
import struct

import pyarrow.parquet as pq
import pytest

from heat3d_watch.adapters.base import Context
from heat3d_watch.adapters.riot_replays import (
    ADAPTERS,
    VRF_MAGIC,
    match_id,
    read_rofl,
    read_vrf,
)
from heat3d_watch.config import Settings

PLAYERS = [
    {"RIOT_ID_GAME_NAME": "Someone", "RIOT_ID_TAG_LINE": "EUW", "PUUID": "p1", "SKIN": "Ahri", "TEAM": "100",
     "TEAM_POSITION": "MIDDLE", "CHAMPIONS_KILLED": "7", "NUM_DEATHS": "2", "ASSISTS": "9", "GOLD_EARNED": "12345",
     "TOTAL_DAMAGE_DEALT_TO_CHAMPIONS": "23456", "WIN": "Win"},
    {"RIOT_ID_GAME_NAME": "Other", "RIOT_ID_TAG_LINE": "EUW", "PUUID": "p2", "SKIN": "Zed", "TEAM": "200",
     "TEAM_POSITION": "MIDDLE", "CHAMPIONS_KILLED": "3", "NUM_DEATHS": "6", "ASSISTS": "1", "GOLD_EARNED": "9000",
     "TOTAL_DAMAGE_DEALT_TO_CHAMPIONS": "15000", "WIN": "Fail"},
]
META = {"gameLength": 1800000, "lastGameChunkId": 30, "lastKeyFrameId": 15, "statsJson": json.dumps(PLAYERS)}


def rofl1(game_id: int = 7123456789) -> bytes:
    """ROFL1 as roflxd.cs reads it: magic, signature, lengths, metadata JSON, payload header."""
    meta = json.dumps({**META, "gameVersion": "14.9.580.2108"}).encode()
    header_len = 288
    meta_off = header_len
    payload_off = meta_off + len(meta)
    payload = struct.pack("<QIIIIII", game_id, 1800000, 15, 30, 2, 3, 60000) + struct.pack("<H", 4) + b"QUJD"
    lengths = struct.pack("<HIIIIII", header_len, 0, meta_off, len(meta), payload_off, len(payload), payload_off + len(payload))
    return b"RIOT\x00\x00" + bytes(256) + lengths + meta + payload


def rofl2() -> bytes:
    """ROFL2: version near the start, the metadata at the end with its length in the last four bytes."""
    meta = json.dumps(META).encode()
    head = b"RIOT\x02\x00" + bytes(8) + b"15.3.659.6012\x00\x00" + bytes(40)
    return head + b"\x28\xb5\x2f\xfd" + bytes(64) + meta + struct.pack("<i", len(meta))


def test_both_league_containers_give_the_box_score():
    for buf, version in ((rofl1(), "14.9.580.2108"), (rofl2(), "15.3.659.6012")):
        r = read_rofl(buf)
        assert r["version"] == version
        assert r["length_ms"] == 1800000
        assert [p["SKIN"] for p in r["players"]] == ["Ahri", "Zed"]
    assert read_rofl(rofl1())["game_id"] == 7123456789
    with pytest.raises(ValueError):
        read_rofl(b"not a replay" + bytes(300))


def test_the_match_id_comes_from_the_client_s_file_name(tmp_path):
    assert match_id(tmp_path / "EUW1-7123456789.rofl", {}, "NA1") == "EUW1_7123456789"
    assert match_id(tmp_path / "renamed.rofl", {"game_id": 42}, "eun1") == "EUN1_42"


class _Response(io.BytesIO):
    def __enter__(self):
        return self

    def __exit__(self, *a):
        return False


def test_a_league_replay_becomes_a_session_and_the_timeline_gives_positions(tmp_path):
    a = next(x for x in ADAPTERS if x.id == "lol-replays")
    timeline = {
        "info": {
            "participants": [{"participantId": 1, "puuid": "p1"}, {"participantId": 2, "puuid": "p2"}],
            "frames": [
                {"timestamp": 60000, "participantFrames": {"1": {"position": {"x": 500, "y": 700}, "level": 2},
                                                            "2": {"position": {"x": 14000, "y": 14200}}},
                 "events": [{"type": "CHAMPION_KILL", "timestamp": 61000, "position": {"x": 7000, "y": 7100},
                             "killerId": 1, "victimId": 2},
                            {"type": "GAME_END", "timestamp": 61500, "realTimestamp": 1_700_000_061_500}]},
            ],
        }
    }
    asked = []

    def opener(request, timeout):
        asked.append((request.full_url, request.headers.get("X-riot-token")))
        return _Response(json.dumps(timeline).encode())

    a.opener = opener
    replay = tmp_path / "EUW1-7123456789.rofl"
    replay.write_bytes(rofl2())
    data = tmp_path / "data"
    ctx = Context(Settings(data=str(data), riot_id="someone#euw", riot_api_key="RGAPI-test"), data)
    a.convert(replay, ctx)
    a.opener = None
    assert asked == [("https://europe.api.riotgames.com/lol/match/v5/matches/EUW1_7123456789/timeline", "RGAPI-test")]
    meta = json.loads(next((data / "sessions").rglob("meta.json")).read_text(encoding="utf-8"))
    assert meta["stats"]["kills"] == 7 and meta["stats"]["won"] == 1 and meta["stats"]["champion"] == "Ahri"
    assert meta["events"]["player_result"] == 2
    t = pq.read_table(next((data / "sessions").rglob("heat.parquet"))).to_pylist()
    kill = next(r for r in t if r["event"] == "kill")
    assert (kill["x"], kill["z"], kill["player"], kill["victim"]) == (7000.0, 7100.0, "Someone#EUW", "Other#EUW")
    assert sum(1 for r in t if r["event"] == "position") == 2
    # The wall clock from the timeline's realTimestamp, and the player's rows named in meta.json.
    from datetime import datetime

    assert kill["ms"] == 1_700_000_061_000
    assert meta["started"] == datetime.fromtimestamp(1_700_000_000).isoformat(timespec="seconds")
    assert meta["player"] == "Someone#EUW"


def test_without_a_key_nothing_is_fetched(tmp_path):
    a = next(x for x in ADAPTERS if x.id == "lol-replays")
    a.opener = lambda *args, **kw: pytest.fail("fetched without a key")
    replay = tmp_path / "EUW1-1.rofl"
    replay.write_bytes(rofl1())
    data = tmp_path / "data"
    a.convert(replay, Context(Settings(data=str(data)), data))
    a.opener = None
    assert not list((data / "sessions").rglob("heat.parquet"))


def _fstring(text: str) -> bytes:
    raw = text.encode("latin-1") + b"\x00"
    return struct.pack("<i", len(raw)) + raw


def _event(group: str, words: list[int], seconds: float, time_ms: int) -> bytes:
    payload = struct.pack("<I", 1) + b"".join(struct.pack("<I", w) for w in words)
    payload += _fstring(f"EReplayEventGroup::{group}") + struct.pack("<f", seconds)
    return _fstring(f"ev-{time_ms}") + _fstring(group) + _fstring("") + struct.pack("<IIi", time_ms, time_ms, len(payload)) + payload


def vrf(encrypted: int = 0) -> bytes:
    """A replay in the layout vrfkit documents: the info block, then type/size chunks."""
    info = struct.pack("<II", VRF_MAGIC, 7) + struct.pack("<i", 1) + bytes(20)
    info += struct.pack("<iII", 2100000, 21, 999) + _fstring("Valorant replay")
    info += struct.pack("<IqII", 0, int((1_700_000_000 + 62135596800) * 1e7), 1, encrypted) + struct.pack("<i", 0)
    header = (struct.pack("<I", 0x2CF5A13D) + _fstring("++Ares-Core+release-13.01") + bytes(16)
              + _fstring("/Game/Maps/Ascent/Ascent") + b'{"matchID":"0a1b2c3d-1111-2222-3333-444455556666",'
              b'"playerLoadouts":{"x":{"characterId":"add6443a-41bd-e414-f6ad-e58d267f4e95"}}}')
    chunks = struct.pack("<Ii", 0, len(header)) + header
    for ev in (_event("roundStarted", [], 0.0, 1000), _event("characterDeath", [11, 22], 31.5, 32500),
               _event("spikePlanted", [11], 70.0, 71000), _event("roundStarted", [], 120.0, 121000)):
        chunks += struct.pack("<Ii", 3, len(ev)) + ev
    chunks += struct.pack("<Ii", 1, 4) + b"\x00\x01\x02\x03"  # replay data: not read
    return info + chunks


def test_a_valorant_replay_gives_its_open_facts_and_timeline(tmp_path):
    r = read_vrf(vrf())
    assert r["map"] == "/Game/Maps/Ascent/Ascent"
    assert r["match_id"] == "0a1b2c3d-1111-2222-3333-444455556666"
    assert r["agents"] == ["add6443a-41bd-e414-f6ad-e58d267f4e95"]
    assert [e["event"] for e in r["events"]] == ["round_start", "kill", "spike_planted", "round_start"]
    kill = r["events"][1]
    assert kill["words"] == [11, 22] and kill["seconds"] == pytest.approx(31.5)
    with pytest.raises(ValueError, match="encrypted"):
        read_vrf(vrf(encrypted=1))
    a = next(x for x in ADAPTERS if x.id == "valorant-replays")
    replay = tmp_path / "match.vrf"
    replay.write_bytes(vrf())
    data = tmp_path / "data"
    a.convert(replay, Context(Settings(data=str(data)), data))
    meta = json.loads(next((data / "sessions").rglob("meta.json")).read_text(encoding="utf-8"))
    assert meta["stats"]["rounds"] == 2 and meta["stats"]["kills_in_match"] == 1 and meta["stats"]["map"] == "Ascent"
