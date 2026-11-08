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
    # An encrypted replay is walked and kept whole, nothing read inside.
    locked = read_vrf(vrf(encrypted=1))
    assert locked["encrypted"] and locked["events"] == [] and locked["map"] is None
    assert [x[0] for x in locked["sections"]] == ["info", "header", "event", "event", "event", "event", "replay_data"]
    a = next(x for x in ADAPTERS if x.id == "valorant-replays")
    replay = tmp_path / "match.vrf"
    replay.write_bytes(vrf())
    data = tmp_path / "data"
    a.convert(replay, Context(Settings(data=str(data)), data))
    meta = json.loads(next((data / "sessions").rglob("meta.json")).read_text(encoding="utf-8"))
    assert meta["stats"]["rounds"] == 2 and meta["stats"]["kills_in_match"] == 1 and meta["stats"]["map"] == "Ascent"


def _raw(data):
    folder = next((data / "sessions").rglob("meta.json")).parent
    meta = json.loads((folder / "meta.json").read_text(encoding="utf-8"))
    return meta, pq.read_table(folder / "heat.raw.parquet").to_pylist()


def test_every_part_of_a_league_replay_is_kept_and_the_timeline_whole(tmp_path):
    """The file's parts tile it; every timeline event and frame is a row and kept; the self-check loses nothing."""
    import struct as st

    # A ROFL1 with a chunk table of one keyframe and one chunk after its payload header, and their bytes.
    meta = json.dumps({**META, "gameVersion": "14.9.580.2108"}).encode()
    meta_off = 288
    ph_off = meta_off + len(meta)
    ph = st.pack("<QIIIIII", 7123456789, 1800000, 1, 1, 2, 3, 60000) + st.pack("<H", 4) + b"QUJD"
    payload_off = ph_off + len(ph)
    table = st.pack("<IBIII", 1, 2, 5, 0, 0) + st.pack("<IBIII", 1, 1, 3, 2, 5)
    data = b"KEYFR" + b"CHK"
    lengths = st.pack("<HIIIIII", 288, 0, meta_off, len(meta), ph_off, len(ph), payload_off)
    buf = b"RIOT\x00\x00" + bytes(256) + lengths + meta + ph + table + data + b"??"
    r = read_rofl(buf)
    kinds = [x[0] for x in r["sections"]]
    assert kinds == ["magic", "signature", "lengths", "metadata", "payload_header", "chunk_header", "chunk_header",
                     "keyframe", "chunk", "unknown"]
    assert r["payload"]["keyframe_interval"] == 60000 and r["payload"]["encryption_key"] == "QUJD"
    assert r["chunks"] == [{"id": 1, "type": "keyframe", "length": 5, "next_chunk_id": 0, "offset": 0},
                           {"id": 1, "type": "chunk", "length": 3, "next_chunk_id": 2, "offset": 5}]

    a = next(x for x in ADAPTERS if x.id == "lol-replays")
    timeline = {
        "metadata": {"matchId": "EUW1_7123456789"},
        "info": {
            "participants": [{"participantId": 1, "puuid": "p1"}, {"participantId": 2, "puuid": "p2"}],
            "frames": [
                {"timestamp": 60000,
                 "participantFrames": {"1": {"position": {"x": 500, "y": 700}, "level": 2, "totalGold": 600,
                                             "championStats": {"armor": 30}},
                                       "2": {"level": 1}},
                 "events": [{"type": "WARD_PLACED", "timestamp": 30000, "creatorId": 2, "wardType": "YELLOW_TRINKET"},
                            {"type": "BUILDING_KILL", "timestamp": 59000, "killerId": 1, "position": {"x": 900, "y": 1000},
                             "assistingParticipantIds": [2]}]},
            ],
        },
    }
    a.opener = lambda request, timeout: _Response(json.dumps(timeline).encode())
    replay = tmp_path / "EUW1-7123456789.rofl"
    replay.write_bytes(buf)
    data_dir = tmp_path / "data"
    a.convert(replay, Context(Settings(data=str(data_dir), riot_api_key="RGAPI-test"), data_dir))
    a.opener = None
    meta, raw = _raw(data_dir)
    c = meta["selfCheck"]["completeness"]
    assert c["lost"] == 0
    assert c["types"]["chunk"] == {"seen": 1, "decoded": 0, "partial": 0, "raw": 1, "lost": 0}
    assert c["types"]["timeline BUILDING_KILL"]["partial"] == 1 and c["types"]["timeline participantFrame"]["seen"] == 2
    parts = sorted((row for row in raw if row["offset"] is not None), key=lambda row: row["offset"])
    assert b"".join(row["payload"] for row in parts) == buf
    assert meta["rofl"]["payload"]["game_id"] == 7123456789 and meta["rofl"]["chunks"] == 2
    # The rest of the timeline, and each event and frame, whole.
    rest = json.loads(next(row for row in raw if row["type"] == "timeline")["text"])
    assert rest["metadata"] == {"matchId": "EUW1_7123456789"} and rest["info"]["frames"] == [{"timestamp": 60000}]
    t = pq.read_table(next((data_dir / "sessions").rglob("heat.parquet"))).to_pylist()
    building = next(row for row in t if row["event"] == "building_kill")
    assert (building["x"], building["z"], building["player"]) == (900.0, 1000.0, "Someone#EUW")
    assert building["assistingParticipantIds"] == "[2]"
    me = next(row for row in t if row["event"] == "position")
    assert me["championStats.armor"] == 30 and me["gold"] == 600
    results = [json.loads(line) for line in next((data_dir / "sessions").rglob("events.jsonl")).read_text(
        encoding="utf-8").splitlines()]
    ahri = next(e for e in results if e["event"] == "player_result" and e["champion"] == "Ahri")
    assert ahri["CHAMPIONS_KILLED"] == 7 and ahri["TEAM_POSITION"] == "MIDDLE" and ahri["PUUID"] == "p1"
    assert any(e["event"] == "ward_placed" and e["player"] == "Other#EUW" for e in results)


def test_every_chunk_of_a_valorant_replay_is_kept(tmp_path):
    buf = vrf() + b"\x09\x00\x00\x00\xff\x00\x00\x00cut"  # a chunk cut short at the end
    r = read_vrf(buf)
    assert [x[0] for x in r["sections"]] == ["info", "header", "event roundStarted", "event characterDeath",
                                              "event spikePlanted", "event roundStarted", "replay_data", "trailing"]
    assert r["info"]["network_version"] == 21 and r["info"]["name"] == "Valorant replay"
    assert r["events"][1]["id"] == "ev-32500" and r["events"][1]["time_ms"] == 32500
    a = next(x for x in ADAPTERS if x.id == "valorant-replays")
    replay = tmp_path / "match.vrf"
    replay.write_bytes(buf)
    data = tmp_path / "data"
    a.convert(replay, Context(Settings(data=str(data)), data))
    meta, raw = _raw(data)
    c = meta["selfCheck"]["completeness"]
    assert c["lost"] == 0
    assert c["types"]["replay_data"] == {"seen": 1, "decoded": 0, "partial": 0, "raw": 1, "lost": 0}
    assert c["types"]["event characterDeath"]["partial"] == 1 and c["types"]["trailing"]["raw"] == 1
    assert b"".join(row["payload"] for row in sorted(raw, key=lambda row: row["offset"])) == buf
    assert meta["vrf"]["changelist"] == 999
