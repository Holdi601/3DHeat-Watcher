"""Dota 2 replays: the download, the hero sampler, the table and summary, and the adapter - on made-up data."""

from __future__ import annotations

import bz2
import io
import json
import sys
from pathlib import Path
from types import SimpleNamespace

import pyarrow.parquet as pq
import pytest

from heat3d_watch.adapters.base import Context
from heat3d_watch.adapters.replays import DotaReplays, record_dota_match
from heat3d_watch.config import Settings
from heat3d_watch.decoders import dota_replay as d

DEMO = d.DEMO_MAGIC + b"\x00" * 64


# ------------------------------------------------------------------ download


def _match(**kw):
    return lambda url: {"match_id": 42, **kw}


def test_replay_url_from_cluster_and_salt():
    assert d.replay_url(42, get=_match(cluster=445, replay_salt=1577)) == "http://replay445.valve.net/570/42_1577.dem.bz2"
    assert d.replay_url(42, get=_match(replay_url="http://x/y.dem.bz2")) == "http://x/y.dem.bz2"
    with pytest.raises(LookupError, match="request"):
        d.replay_url(42, get=_match(cluster=445))
    with pytest.raises(LookupError):
        d.replay_url(42, get=lambda url: {"error": "Not Found"})


class _Response(io.BytesIO):
    def __enter__(self):
        return self

    def __exit__(self, *exc):
        self.close()


@pytest.mark.parametrize("pack", ["bz2", "zstd", "raw"])
def test_fetch_unpacks_whatever_the_cdn_sends(tmp_path, pack):
    if pack == "bz2":
        body = bz2.compress(DEMO)
    elif pack == "zstd":
        zstandard = pytest.importorskip("zstandard")
        body = zstandard.ZstdCompressor().compress(DEMO)
    else:
        body = DEMO
    asked = []
    out = d.fetch_replay(42, tmp_path, get=_match(cluster=1, replay_salt=2),
                         opener=lambda url: asked.append(url) or _Response(body))
    assert out == tmp_path / "42.dem" and out.read_bytes() == DEMO
    assert asked == ["http://replay1.valve.net/570/42_2.dem.bz2"]
    # Already there: kept, nothing asked.
    assert d.fetch_replay(42, tmp_path, get=lambda url: pytest.fail("asked again")) == out


def test_fetch_refuses_what_is_not_a_demo_and_leaves_nothing(tmp_path):
    with pytest.raises(d.FormatError):
        d.fetch_replay(42, tmp_path, get=_match(cluster=1, replay_salt=2),
                       opener=lambda url: _Response(bz2.compress(b"<html>gone</html>")))
    assert list(tmp_path.iterdir()) == []


# ------------------------------------------------------------------ the sampler


class _Entity:
    def __init__(self, index, cls, **fields):
        self.index, self.cls, self.fields = index, cls, fields

    def get(self, name):
        return self.fields.get(name)

    def get_class_name(self):
        return self.cls

    def get_index(self):
        return self.index


def _body(x, y, z=128.0):
    """Fields placing an entity at world (x, y, z), as cell and offset."""
    out = {}
    for axis, v in (("X", x), ("Y", y), ("Z", z)):
        cell, off = divmod(v + d.CELL_ORIGIN, d.CELL_SIZE)
        out[f"CBodyComponent.m_cell{axis}"] = int(cell)
        out[f"CBodyComponent.m_vec{axis}"] = off
    return out


class _Parser:
    def __init__(self):
        self.tick = 0
        self.entities = {}
        self.string_tables = SimpleNamespace(get_by_name=lambda name: SimpleNamespace(items={7: ("dota_goodguys_tower1_top", b"")}))
        self.entity_manager = SimpleNamespace(find_by_handle=lambda h: self.entities.get(h))
        self.entity_hooks, self.tick_hooks = [], []

    def _on_entity_filtered(self, cb, class_names=(), class_prefixes=()):
        self.entity_hooks.append((cb, set(class_names)))

    def on_tick_start(self, cb):
        self.tick_hooks.append(cb)

    def push(self, e, op=0x02):
        for cb, names in self.entity_hooks:
            if e.get_class_name() in names:
                cb(e, op)

    def run(self, ticks):
        for t in ticks:
            self.tick = t
            for cb in self.tick_hooks:
                cb(t)


def test_sampler_follows_each_players_own_hero_and_skips_the_dead():
    p = _Parser()
    s = d._Sampler(p, step=4)
    hero = _Entity(300, "CDOTA_Unit_Hero_Axe", m_lifeState=0, m_iHealth=600, m_iMaxHealth=700, m_iCurrentLevel=3,
                   **_body(-6700.5, -6650.25, 384.0))
    illusion = _Entity(301, "CDOTA_Unit_Hero_Axe", m_lifeState=0, **_body(0, 0))
    p.entities = {1001: hero, 1002: illusion}
    p.push(_Entity(2, "CDOTAPlayerController", m_nPlayerID=3, m_hAssignedHero=1001))
    p.push(_Entity(3, "CDOTAPlayerController", m_nPlayerID=13, m_hAssignedHero=0xFFFFFF))  # a spectator
    p.push(_Entity(700, "CDOTA_BaseNPC_Tower", **{"m_pEntity.m_nameStringTableIndex": 7, **_body(-6100, 1800, 256)}))
    p.run(range(0, 9))
    assert [(r[0], r[1]) for r in s.raw] == [(0, 3), (4, 3), (8, 3)]
    tick, slot, x, y, z, hp, mhp, lvl = s.raw[0]
    assert (x, y, z, hp, mhp, lvl) == pytest.approx((-6700.5, -6650.25, 384.0, 600, 700, 3))
    assert s.structures == {"goodguys_tower1_top": pytest.approx((-6100, 1800, 256))}
    hero.fields["m_lifeState"] = 2
    p.run([12])
    assert len(s.raw) == 3


def test_tracks_drop_the_paused_clock_and_end_with_the_game():
    raw = [(t, 0, float(t), 0.0, 0.0, None, None, None) for t in range(0, 40, 4)]
    clock = {0: -1.0, 4: -0.8, 8: -0.8, 12: -0.8, 16: -0.6}  # paused from tick 4 to 12
    samples = d.tracks(raw, lambda t: clock.get(t, t / 30), end=24)
    assert [s.tick for s in samples] == [0, 4, 16, 20, 24]


# ------------------------------------------------------------------ the table and the summary


def _replay():
    players = [
        {"slot": 0, "name": "Ann", "steamid": "76561190000000001", "hero": "npc_dota_hero_axe", "heroName": "Axe",
         "team": "Radiant", "kills": 1, "deaths": 0},
        {"slot": 5, "name": "Bob", "steamid": "76561190000000002", "hero": "npc_dota_hero_lina", "heroName": "Lina",
         "team": "Dire", "kills": 0, "deaths": 1},
    ]
    samples = []
    for i in range(10):
        t = -1.0 + i * 0.5
        samples.append(d.Sample(i * 15, t, 0, 100.0 + i, 200.0, 128.0, 600, 700, 2))
        if i < 6 or i > 7:  # Bob is dead between ticks 90 and 105
            samples.append(d.Sample(i * 15, t, 5, -100.0 - i, 50.0, 256.0, 500, 520, 2))
    events = [
        d.Event(80, 1.66, "death", 5, other="hero_axe"),
        d.Event(80, 1.66, "kill", 0, other="hero_lina"),
        d.Event(50, 0.66, "observer_ward", 5, 1000.0, 1200.0, other="observer"),
        d.Event(120, 3.0, "tower_kill", 0, -6100.0, 1800.0, 256.0, other="goodguys_tower1_top"),
        d.Event(121, 3.0, "tower_kill", -1, other="badguys_tower1_mid"),  # a creep's, the tower not seen
    ]
    return d.Replay(match_id=42, players=players, samples=samples, events=events,
                    info={"winner": "Radiant", "score": {"Radiant": 1, "Dire": 0}, "duration": 5}, hz=2.0)


def test_table_places_events_and_counts_lives(tmp_path):
    data, doc = d.write(_replay(), tmp_path)
    t = pq.read_table(data)
    hints = json.loads(t.schema.metadata[b"heat3d"])
    assert hints["kind"] == "dota2-replay" and hints["axes"]["up"] == "z" and hints["axes"]["flipY"] is True
    assert hints["columns"]["personId"] == "player" and hints["columns"]["sessionId"] == "life"
    assert hints["entity"]["size"] == 48 and hints["hz"] == 2.0
    for c in (hints["columns"]["x"], hints["columns"]["time"], *hints["columns"]["extra"]):
        assert c in t.column_names
    rows = t.to_pylist()
    assert [r["tick"] for r in rows] == sorted(r["tick"] for r in rows)
    events = {r["event"]: r for r in rows if r["event"] != "position"}
    assert "tower_kill" in events and len([r for r in rows if r["event"] == "tower_kill"]) == 1  # the unplaced one left out
    death, kill, ward = events["death"], events["kill"], events["observer_ward"]
    # The death where Bob last stood (tick 75), the kill where Ann stood then.
    assert (death["x"], death["y"], death["player"], death["other"]) == (-105.0, 50.0, "Bob", "hero_axe")
    assert (kill["x"], kill["player"], kill["team"]) == (105.0, "Ann", "Radiant")
    # The ward where it was planted, at its planter's height.
    assert (ward["x"], ward["y"], ward["z"]) == (1000.0, 1200.0, 256.0)
    bob = [r for r in rows if r["slot"] == 5 and r["event"] == "position"]
    assert [r["life"] for r in bob] == [1] * 6 + [2] * 2
    assert death["life"] == 1 and all(r["life"] == 1 for r in rows if r["slot"] == 0)
    assert bob[0]["health"] == 500 and events["death"]["health"] is None

    summary = json.loads(doc.read_text(encoding="utf-8"))
    assert summary["format"] == "heat3d-dota-match" and summary["match"] == "42" and summary["winner"] == "Radiant"
    assert summary["deaths"] == [{"time": 1.7, "slot": 5, "x": -105.0, "y": 50.0, "by": "hero_axe"}]
    assert [o["what"] for o in summary["objectives"]] == ["goodguys_tower1_top", "badguys_tower1_mid"]
    assert summary["objectives"][1]["x"] is None
    assert summary["wards"][0]["type"] == "observer" and summary["samples"]["rows"] == 18


def test_events_from_the_combat_log_and_objectives():
    def death(tick, target, attacker, source=None, **kw):
        return SimpleNamespace(tick=tick, log_type=SimpleNamespace(value="DEATH"), target_name=target, attacker_name=attacker,
                               damage_source_name=source if source is not None else attacker,
                               target_is_hero=target.startswith("npc_dota_hero"), target_is_illusion=kw.get("illusion", False),
                               will_reincarnate=kw.get("reincarnate", False))

    match = SimpleNamespace(
        combat_log=[
            death(100, "npc_dota_hero_lina", "npc_dota_hero_axe"),
            death(110, "npc_dota_hero_lina", "npc_dota_hero_axe", illusion=True),  # an illusion of Lina
            death(120, "npc_dota_hero_axe", "npc_dota_hero_lina", reincarnate=True),  # the aegis brings him back
            death(130, "npc_dota_hero_axe", "npc_dota_badguys_tower1_mid"),  # a tower's kill: a death, no kill
            death(140, "npc_dota_hero_lina", "npc_dota_lina_illusion", source="npc_dota_hero_axe"),
            death(150, "npc_dota_creep_badguys_melee", "npc_dota_hero_axe"),
            SimpleNamespace(tick=1, log_type=SimpleNamespace(value="DAMAGE")),
        ],
        towers=[SimpleNamespace(tick=200, tower_name="npc_dota_goodguys_tower1_top", killer="npc_dota_creep_badguys_melee",
                                killer_source="npc_dota_creep_badguys_melee")],
        barracks=[],
        roshans=[SimpleNamespace(tick=300, killer="npc_dota_hero_axe", killer_source="npc_dota_hero_axe", kill_number=1)],
        tormentors=[SimpleNamespace(tick=310, killer="npc_dota_hero_lina", killer_player_id=5, kill_number=1)],
        wards=[SimpleNamespace(tick=50, player_id=5, placer="npc_dota_hero_lina", ward_type="sentry", x=16384.0 + 10, y=16384.0 - 20)],
    )
    sampler = SimpleNamespace(structures={"goodguys_tower1_top": (-6100.0, 1800.0, 256.0)},
                              roshan=[(290, -2800.0, 2300.0, 0.0), (305, 0.0, 0.0, 0.0)])
    events = d._events(match, {"npc_dota_hero_axe": 0, "npc_dota_hero_lina": 5}, lambda t: t / 30, sampler)
    got = [(e.tick, e.event, e.slot, e.other) for e in events]
    assert got == [
        (50, "sentry_ward", 5, "sentry"),
        (100, "death", 5, "hero_axe"), (100, "kill", 0, "hero_lina"),
        (130, "death", 0, "badguys_tower1_mid"),
        (140, "death", 5, "hero_axe"), (140, "kill", 0, "hero_lina"),
        (200, "tower_kill", -1, "goodguys_tower1_top"),
        (300, "roshan_kill", 0, "roshan 1"),
        (310, "tormentor_kill", 5, "tormentor 1"),
    ]
    by = {e.event: e for e in events}
    assert (by["sentry_ward"].x, by["sentry_ward"].y) == (10.0, -20.0)
    assert (by["tower_kill"].x, by["tower_kill"].z) == (-6100.0, 256.0)
    assert (by["roshan_kill"].x, by["roshan_kill"].y) == (-2800.0, 2300.0)


def _entry(tick, kind, attacker="", target="", value=0, **kw):
    fields = dict(tick=tick, log_type=SimpleNamespace(value=kind), attacker_name=attacker, target_name=target,
                  damage_source_name=kw.pop("source", attacker), inflictor_name=kw.pop("inflictor", ""), value=value,
                  value_name=kw.pop("value_name", ""), attacker_is_illusion=False, target_is_illusion=False,
                  target_is_hero=target.startswith("npc_dota_hero"), attacker_is_hero=attacker.startswith("npc_dota_hero"),
                  location_x=None, location_y=None, ability_level=0, gold_reason=0, xp_reason=0, rune_type=None)
    fields.update(kw)
    return SimpleNamespace(**fields)


def test_the_combat_log_about_heroes_becomes_rows():
    axe, lina = "npc_dota_hero_axe", "npc_dota_hero_lina"
    match = SimpleNamespace(
        combat_log=[
            _entry(10, "DAMAGE", axe, lina, 120, inflictor="axe_battle_hunger"),
            _entry(11, "HEAL", lina, lina, 50, inflictor="item_flask"),
            _entry(12, "PURCHASE", target=axe, value_name="item_blink"),
            _entry(13, "GOLD", target=lina, value=40, gold_reason=12, location_x=-6700.0, location_y=-6650.0),
            _entry(14, "DEATH", "npc_dota_axe_illusion", "npc_dota_creep_badguys_melee", source=axe),
            _entry(15, "DAMAGE", "npc_dota_creep_badguys_melee", "npc_dota_creep_goodguys_melee", 20),
        ],
        chat=[SimpleNamespace(tick=20, player_slot=5, channel="all", text="gg")],
    )
    events = d._more_events(match, {axe: 0, lina: 5}, lambda t: t / 30)
    got = [(e.tick, e.event, e.slot, e.other, e.value, e.text) for e in events]
    assert got == [
        (10, "hurt", 5, "hero_axe", 120, "axe_battle_hunger"),
        (10, "damage", 0, "hero_lina", 120, "axe_battle_hunger"),
        (11, "heal", 5, "hero_lina", 50, "item_flask"),
        (12, "purchase", 0, "", None, "item_blink"),
        (13, "gold", 5, "", 40, ""),
        (14, "unit_kill", 0, "creep_badguys_melee", 0, ""),
        (20, "chat", 5, "all", None, "gg"),
    ]
    gold = events[4]
    assert (gold.x, gold.y) == (-6700.0, -6650.0)
    columns = d.combat_columns(match.combat_log, lambda t: t / 30)
    assert len(columns["tick"]) == 6 and columns["log_type"][0] == "DAMAGE" and columns["value_name"][2] == "item_blink"


def test_the_heros_state_and_the_units_are_written(tmp_path):
    r = _replay()
    r.samples[0].extra = {"mana": 300.0, "yaw": 90.0, "items": "item_blink||item_tango", "moveSpeed": 300}
    r.units = [(30, 1.0, 400, "CDOTA_BaseNPC_Creep_Lane", "npc_dota_creep_goodguys_melee", 2, 10.0, 20.0, 128.0, 550,
                550, 180.0, -1)]
    r.combat_log = {"tick": [10], "log_type": ["DAMAGE"]}
    data, doc = d.write(r, tmp_path)
    rows = pq.read_table(data).to_pylist()
    first = [x for x in rows if x["event"] == "position" and x["slot"] == 0][0]
    assert first["mana"] == 300.0 and first["items"] == "item_blink||item_tango"
    assert first["dirY"] == pytest.approx(1.0) and first["dirX"] == pytest.approx(0.0, abs=1e-6)
    units = pq.read_table(tmp_path / "42.units.parquet")
    hints = json.loads(units.schema.metadata[b"heat3d"])
    assert hints["columns"]["personId"] == "unit" and units.column("unit").to_pylist() == ["npc_dota_creep_goodguys_melee #400"]
    assert units.column("team").to_pylist() == ["Radiant"] and units.column("dirX").to_pylist()[0] == pytest.approx(-1.0)
    assert pq.read_table(tmp_path / "42.combatlog.parquet").num_rows == 1
    assert json.loads(doc.read_text(encoding="utf-8"))["combatLog"] == {"file": "42.combatlog.parquet", "rows": 1}


def test_read_refuses_other_files(tmp_path):
    f = tmp_path / "x.dem"
    f.write_bytes(b"HL2DEMO\0" + b"\0" * 32)  # a Source 1 demo
    with pytest.raises(d.FormatError):
        d.read(f)


def test_read_says_what_to_install(tmp_path, monkeypatch):
    f = tmp_path / "x.dem"
    f.write_bytes(DEMO)
    monkeypatch.setitem(sys.modules, "gem", None)
    with pytest.raises(d.Missing, match="gem-dota"):
        d.read(f)


# ------------------------------------------------------------------ the adapter


def _summary():
    return {
        "match": "42", "winner": "Dire", "score": {"Radiant": 5, "Dire": 28}, "duration": 1643,
        "players": [
            {"slot": 0, "name": "Ann", "steamid": "76561190000000001", "heroName": "Axe", "team": "Radiant", "kills": 1,
             "deaths": 7, "assists": 0, "lastHits": 150, "netWorth": 11781, "goldPerMin": 430, "won": False},
            {"slot": 5, "name": "Bob", "steamid": "76561190000000002", "heroName": "Lina", "team": "Dire", "kills": 6},
        ],
    }


def test_the_signed_in_players_line_becomes_the_statistics(tmp_path):
    stats, meta = {}, {}
    session = SimpleNamespace(meta=meta, stat=lambda k, v: stats.__setitem__(k, v))
    record_dota_match(session, _summary(), {"76561190000000001"})
    assert stats["kills"] == 1 and stats["deaths"] == 7 and stats["net_worth"] == 11781 and stats["gpm"] == 430
    assert stats["hero"] == "Axe" and stats["won"] == 0 and stats["score.Dire"] == 28 and stats["duration"] == 1643
    assert meta["player"] == "Ann" and meta["match"]["winner"] == "Dire"


def test_adapter_converts_in_a_process_of_its_own(tmp_path, monkeypatch):
    replay = tmp_path / "replays" / "42.dem"
    replay.parent.mkdir()
    replay.write_bytes(DEMO)
    calls = []

    def run(cmd, **kw):
        calls.append(cmd)
        out = Path(cmd[cmd.index("-o") + 1])
        out.mkdir(parents=True)
        (out / "42.match.json").write_text(json.dumps(_summary()), encoding="utf-8")
        import pyarrow as pa

        pq.write_table(pa.table({"event": ["position", "position", "death", "kill"]}), out / "42.parquet")
        # The side tables, which sort before the match's own: not counted.
        pq.write_table(pa.table({"tick": [1, 2, 3]}), out / "42.combatlog.parquet")
        pq.write_table(pa.table({"unit": ["a"]}), out / "42.units.parquet")
        return SimpleNamespace(returncode=0, stdout="", stderr="")

    monkeypatch.setattr("heat3d_watch.adapters.replays.subprocess.run", run)
    monkeypatch.setattr("heat3d_watch.adapters.replays.signed_in_steam_ids", lambda: {"76561190000000002"})
    a = DotaReplays(id="dota-replays", game="Dota 2", patterns=("*.dem",))
    ctx = Context(Settings(data=str(tmp_path / "data")), tmp_path / "data")
    a.convert(replay, ctx)
    assert calls and calls[0][1:3] == ["-m", "heat3d_watch.decoders.dota_replay"]
    folders = list((tmp_path / "data" / "sessions").glob("*/*"))
    assert len(folders) == 1
    meta = json.loads((folders[0] / "meta.json").read_text(encoding="utf-8"))
    assert meta["stats"]["kills"] == 6 and meta["stats"]["won"] == 1
    assert meta["events"]["death"] == 1 and meta["positions"] == 4


def test_adapter_looks_in_the_dota_install(tmp_path, monkeypatch):
    common = tmp_path / "steamapps" / "common"
    (common / "dota 2 beta" / "game" / "dota").mkdir(parents=True)
    monkeypatch.setattr("heat3d_watch.adapters.replays.steam_libraries", lambda: [common])
    a = DotaReplays(id="dota-replays", game="Dota 2", patterns=("*.dem",))
    ctx = Context(Settings(data=str(tmp_path / "data")), tmp_path / "data")
    assert a.folders(ctx) == [common / "dota 2 beta" / "game" / "dota" / "replays"]


def test_dota_replay_command_downloads_where_asked(tmp_path, monkeypatch, capsys):
    from heat3d_watch import cli

    got = []

    def fetch(match_id, folder):
        got.append((match_id, Path(folder)))
        return Path(folder) / f"{match_id}.dem"

    monkeypatch.setattr("heat3d_watch.decoders.dota_replay.fetch_replay", fetch)
    assert cli.main(["dota-replay", "42", "43", "-o", str(tmp_path)]) == 0
    assert got == [(42, tmp_path), (43, tmp_path)]
    assert "43.dem" in capsys.readouterr().out
