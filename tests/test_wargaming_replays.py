"""
World of Tanks and World of Warships replays: the watcher only runs the
external converters (`heat3d-wot-replay`, `heat3d-wows-replay`, in
exporters/ext). Here a stand-in command plays the converter, so these tests
pass without either installed.
"""

from __future__ import annotations

import dataclasses
import json
import logging
import sys
import textwrap
from pathlib import Path

import pytest

from heat3d_watch.adapters import load
from heat3d_watch.adapters import replays
from heat3d_watch.adapters.base import Context
from heat3d_watch.config import Settings


def _adapter(id_: str, **change) -> replays.WargamingReplays:
    a = load()[id_]
    assert isinstance(a, replays.WargamingReplays)
    fields = {f.name: getattr(a, f.name) for f in dataclasses.fields(a) if f.init and not f.name.startswith("_")}
    return replays.WargamingReplays(**{**fields, **change})


@pytest.mark.parametrize(
    "id_, pattern, command, module",
    [
        ("wot-replays", "*.wotreplay", "heat3d-wot-replay", "heat3d_ext_wot"),
        ("wows-replays", "*.wowsreplay", "heat3d-wows-replay", "heat3d_ext_wows"),
    ],
)
def test_registered(id_, pattern, command, module):
    a = load()[id_]
    assert a.kind == "replay" and a.patterns == (pattern,)
    assert a.command == command and a.module == module and a.multiplayer
    assert a.axes.up == "y" and a.axes.flip_z


def test_replay_folders_are_the_installs_replays(monkeypatch, tmp_path):
    games = tmp_path / "Games"
    eu = games / "World_of_Tanks_EU"
    eu.mkdir(parents=True)
    (eu / "WorldOfTanks.exe").write_bytes(b"")
    (games / "World_of_Tanks_NA").mkdir()  # no game in it: not an install
    prefs = tmp_path / "ProgramData" / "Wargaming.net" / "GameCenter"
    prefs.mkdir(parents=True)
    other = tmp_path / "D" / "WoT"
    other.mkdir(parents=True)
    (other / "WorldOfTanks.exe").write_bytes(b"")
    (prefs / "preferences.xml").write_text(f"<x><working_dir>{other}</working_dir></x>", encoding="utf-8")
    monkeypatch.setenv("PROGRAMDATA", str(tmp_path / "ProgramData"))
    monkeypatch.setenv("SystemDrive", str(tmp_path))
    monkeypatch.setattr(replays, "steam_libraries", lambda: [])
    a = _adapter("wot-replays")
    ctx = Context(Settings(data=str(tmp_path / "data")), tmp_path / "data")
    assert a.folders(ctx) == [other / "replays", eu / "replays"]


def test_without_the_converter_it_says_how_to_install_it_once(monkeypatch, caplog):
    a = _adapter("wows-replays")
    monkeypatch.setattr(a, "converter", lambda: None)
    with caplog.at_level(logging.INFO, logger="heat3d_watch"):
        assert "pip install -e" in a.missing()
        assert a.missing() == a.install
    said = [r for r in caplog.records if "not installed" in r.getMessage()]
    assert len(said) == 1 and "heat3d-wows-replay" in said[0].getMessage()


def test_finds_the_converter_on_path_beside_the_watcher_or_by_setting(monkeypatch, tmp_path):
    monkeypatch.setattr("shutil.which", lambda name: None)
    monkeypatch.setattr(replays, "ROOT", tmp_path / "watcher")
    monkeypatch.setattr("importlib.util.find_spec", lambda name: None)
    monkeypatch.delenv("HEAT3D_WOT_REPLAY", raising=False)
    a = _adapter("wot-replays")
    assert a.converter() is None
    beside = tmp_path / "ext" / "wot-replay" / "heat3d_ext_wot"
    beside.mkdir(parents=True)
    (beside / "__init__.py").write_text("", encoding="utf-8")
    assert a.converter() == [sys.executable, "-m", "heat3d_ext_wot"]
    assert a.source_folder() == tmp_path / "ext" / "wot-replay"
    src = tmp_path / "elsewhere"
    (src / "heat3d_ext_wot").mkdir(parents=True)
    (src / "heat3d_ext_wot" / "__init__.py").write_text("", encoding="utf-8")
    monkeypatch.setenv("HEAT3D_WOT_REPLAY", str(src))
    assert a.source_folder() == src
    monkeypatch.setattr("shutil.which", lambda name: "/bin/heat3d-wot-replay")
    assert a.converter() == ["/bin/heat3d-wot-replay"]


#: A stand-in converter: writes the two files of the command's contract.
FAKE = textwrap.dedent(
    """
    import json, sys
    from pathlib import Path
    import pyarrow as pa, pyarrow.parquet as pq
    out = Path(sys.argv[sys.argv.index("-o") + 1]) / "99_testmap"
    out.mkdir(parents=True)
    pq.write_table(pa.table({"event": ["position", "position", "death"], "x": [0.0, 1.0, 1.0]}), out / "m.parquet")
    doc = {"match": "m", "map": "99_testmap", "mapName": "Test Map", "clientVersion": "2.4.1.0",
           "vehicle": "ussr-R1_Test", "duration": 300, "hz": 10.0, "winnerTeam": 1,
           "players": [{"name": "me", "team": 1, "own": True, "kills": 2, "damageDealt": 1500, "survived": False},
                       {"name": "other", "team": 2, "own": False, "kills": 5}]}
    (out / "m.match.json").write_text(json.dumps(doc), encoding="utf-8")
    print("ok")
    """
)


def test_a_new_replay_is_converted_by_the_command(monkeypatch, tmp_path):
    script = tmp_path / "fake_converter.py"
    script.write_text(FAKE, encoding="utf-8")
    a = _adapter("wot-replays")
    monkeypatch.setattr(a, "converter", lambda: [sys.executable, str(script)])
    monkeypatch.setattr(a, "source_folder", lambda: None)
    replay = tmp_path / "20261107_1200_ussr-R1_Test_99_testmap.wotreplay"
    replay.write_bytes(b"\x12\x32\x34\x11")
    ctx = Context(Settings(data=str(tmp_path / "data")), tmp_path / "data")
    a.convert(replay, ctx)
    metas = list((tmp_path / "data" / "sessions").glob("*/*/meta.json"))
    assert len(metas) == 1
    meta = json.loads(metas[0].read_text(encoding="utf-8"))
    assert meta["player"] == "me" and meta["game"] == "World of Tanks"
    assert meta["stats"]["kills"] == 2 and meta["stats"]["damage"] == 1500 and meta["stats"]["map"] == "Test Map"
    assert meta["stats"]["survived"] == 0 and meta["stats"]["won"] == 1 and meta["stats"]["vehicle"] == "ussr-R1_Test"
    assert meta["events"].get("death") == 1 and meta["positions"] == 3


def test_a_failed_conversion_is_noted(monkeypatch, tmp_path):
    script = tmp_path / "fails.py"
    script.write_text("import sys; print('x: not converted: bad', file=sys.stderr); sys.exit(1)", encoding="utf-8")
    a = _adapter("wows-replays")
    monkeypatch.setattr(a, "converter", lambda: [sys.executable, str(script)])
    monkeypatch.setattr(a, "source_folder", lambda: None)
    replay = tmp_path / "a.wowsreplay"
    replay.write_bytes(b"x")
    ctx = Context(Settings(data=str(tmp_path / "data")), tmp_path / "data")
    a.convert(replay, ctx)
    lines = list((tmp_path / "data" / "sessions").glob("*/*/events.jsonl"))
    assert lines and "replay_failed" in lines[0].read_text(encoding="utf-8")


def test_the_watcher_holds_no_wargaming_replay_parsing_of_its_own():
    root = Path(replays.__file__).resolve().parents[1]
    for f in root.rglob("*.py"):
        text = f.read_text(encoding="utf-8")
        for module in ("heat3d_ext_wot", "heat3d_ext_wows"):
            assert f"{module} import" not in text and f"import {module}" not in text, f
        # Neither game's replay key is in the watcher.
        assert "DE72BEA0" not in text.upper() and "29B7C909" not in text.upper(), f
