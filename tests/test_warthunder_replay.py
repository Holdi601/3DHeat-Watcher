"""
War Thunder replays: the watcher only runs the external converter
(`heat3d-wt-replay`, exporters/ext/warthunder-replay). Here a stand-in command
plays the converter, so these tests pass without it installed.
"""

from __future__ import annotations

import json
import logging
import sys
import textwrap
from pathlib import Path

from heat3d_watch.adapters import load
from heat3d_watch.adapters import replays
from heat3d_watch.adapters.base import Context
from heat3d_watch.config import Settings


def _adapter() -> replays.WarThunderReplays:
    a = load()["warthunder-replays"]
    assert isinstance(a, replays.WarThunderReplays)
    return replays.WarThunderReplays(**{f: getattr(a, f) for f in ("id", "game", "patterns", "source", "axes")})


def test_registered_with_the_replay_folder_pattern():
    a = load()["warthunder-replays"]
    assert a.kind == "replay" and a.patterns == ("*.wrpl",)
    assert all(p.name == "Replays" for p in replays.war_thunder_folders())


def test_without_the_converter_it_says_how_to_install_it_once(monkeypatch, caplog):
    monkeypatch.setattr(replays, "wt_converter", lambda: None)
    a = _adapter()
    with caplog.at_level(logging.INFO, logger="heat3d_watch"):
        assert a.missing() == replays.WT_INSTALL
        assert a.missing() == replays.WT_INSTALL
    said = [r for r in caplog.records if "not installed" in r.getMessage()]
    assert len(said) == 1 and "pip install" in said[0].getMessage()


def test_finds_the_converter_beside_the_watcher_or_by_setting(monkeypatch, tmp_path):
    monkeypatch.setattr("shutil.which", lambda name: None)
    monkeypatch.setattr(replays, "ROOT", tmp_path / "watcher")
    monkeypatch.setattr("importlib.util.find_spec", lambda name: None)
    monkeypatch.delenv("HEAT3D_WT_REPLAY", raising=False)
    assert replays.wt_converter() is None
    src = tmp_path / "elsewhere"
    (src / "heat3d_ext_warthunder").mkdir(parents=True)
    (src / "heat3d_ext_warthunder" / "__init__.py").write_text("", encoding="utf-8")
    monkeypatch.setenv("HEAT3D_WT_REPLAY", str(src))
    assert replays.wt_converter() == [sys.executable, "-m", "heat3d_ext_warthunder"]
    assert replays.wt_folder() == src
    monkeypatch.setattr("shutil.which", lambda name: "/bin/heat3d-wt-replay")
    assert replays.wt_converter() == ["/bin/heat3d-wt-replay"]


#: A stand-in converter: writes the two files of the command's contract.
FAKE = textwrap.dedent(
    """
    import json, sys
    from pathlib import Path
    import pyarrow as pa, pyarrow.parquet as pq
    out = Path(sys.argv[sys.argv.index("-o") + 1]) / "avg_test"
    out.mkdir(parents=True)
    pq.write_table(pa.table({"event": ["position", "position", "kill"], "x": [0.0, 1.0, 1.0]}), out / "m.parquet")
    doc = {"match": "m", "map": "avg_test", "mission": "test_Dom", "battleClass": "base_dom", "teams": ["1", "2"],
           "authorUserId": "111", "counts": {"aircraftUids": 2, "groundUids": 0},
           "players": [{"name": "Pilot One", "userId": "111", "kills": 3, "deaths": 1, "score": 900},
                       {"name": "Other", "userId": "222", "kills": 9}]}
    (out / "m.match.json").write_text(json.dumps(doc), encoding="utf-8")
    print("ok", out / "m.parquet", out / "m.match.json")
    """
)


def test_a_new_replay_is_converted_by_the_command(monkeypatch, tmp_path):
    script = tmp_path / "fake_converter.py"
    script.write_text(FAKE, encoding="utf-8")
    monkeypatch.setattr(replays, "wt_converter", lambda: [sys.executable, str(script)])
    monkeypatch.setattr(replays, "wt_folder", lambda: None)
    replay = tmp_path / "2026.11.07 12.00.00.wrpl"
    replay.write_bytes(b"\xe5\xac\x00\x10")
    ctx = Context(Settings(data=str(tmp_path / "data")), tmp_path / "data")
    _adapter().convert(replay, ctx)
    metas = list((tmp_path / "data" / "sessions").glob("*/*/meta.json"))
    assert len(metas) == 1
    meta = json.loads(metas[0].read_text(encoding="utf-8"))
    assert meta["player"] == "Pilot One"
    assert meta["stats"]["kills"] == 3 and meta["stats"]["map"] == "avg_test"
    assert meta["events"].get("kill") == 1 and meta["positions"] == 3


def test_a_failed_conversion_is_noted(monkeypatch, tmp_path):
    script = tmp_path / "fails.py"
    script.write_text("import sys; print('failed x: bad'); sys.exit(1)", encoding="utf-8")
    monkeypatch.setattr(replays, "wt_converter", lambda: [sys.executable, str(script)])
    monkeypatch.setattr(replays, "wt_folder", lambda: None)
    replay = tmp_path / "a.wrpl"
    replay.write_bytes(b"x")
    ctx = Context(Settings(data=str(tmp_path / "data")), tmp_path / "data")
    _adapter().convert(replay, ctx)
    lines = list((tmp_path / "data" / "sessions").glob("*/*/events.jsonl"))
    assert lines and "replay_failed" in lines[0].read_text(encoding="utf-8")


def test_the_watcher_holds_no_replay_parsing_of_its_own():
    root = Path(replays.__file__).resolve().parents[1]
    for f in root.rglob("*.py"):
        text = f.read_text(encoding="utf-8")
        assert "heat3d_ext_warthunder import" not in text and "import heat3d_ext_warthunder" not in text, f
        assert "0x1000ACE5" not in text, f
