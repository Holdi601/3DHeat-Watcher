"""
Squad server demos: the watcher only runs the external reader
(`heat3d-squad-demo`, exporters/ext/squad-demo). Here a stand-in command plays
the reader, so these tests pass without it installed.
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


def _adapter() -> replays.SquadDemos:
    a = load()["squad-demos"]
    assert isinstance(a, replays.SquadDemos)
    return replays.SquadDemos(**{f: getattr(a, f) for f in ("id", "game", "patterns", "source", "axes")})


def test_registered_with_the_demo_folder_pattern():
    a = load()["squad-demos"]
    assert a.kind == "replay" and a.patterns == ("*.replay",)
    assert all(p.parts[-3:] == ("SquadGame", "Saved", "Demos") for p in replays.squad_demo_folders())


def test_without_the_reader_it_says_how_to_install_it_once(monkeypatch, caplog):
    monkeypatch.setattr(replays, "squad_converter", lambda: None)
    a = _adapter()
    with caplog.at_level(logging.INFO, logger="heat3d_watch"):
        assert a.missing() == replays.SQUAD_INSTALL
        assert a.missing() == replays.SQUAD_INSTALL
    said = [r for r in caplog.records if "not installed" in r.getMessage()]
    assert len(said) == 1 and "pip install" in said[0].getMessage()


def test_finds_the_reader_beside_the_watcher_or_by_setting(monkeypatch, tmp_path):
    monkeypatch.setattr("shutil.which", lambda name: None)
    monkeypatch.setattr(replays, "ROOT", tmp_path / "watcher")
    monkeypatch.setattr("importlib.util.find_spec", lambda name: None)
    monkeypatch.delenv("HEAT3D_SQUAD_DEMO", raising=False)
    assert replays.squad_converter() is None
    src = tmp_path / "elsewhere"
    (src / "heat3d_ext_squad").mkdir(parents=True)
    (src / "heat3d_ext_squad" / "__init__.py").write_text("", encoding="utf-8")
    monkeypatch.setenv("HEAT3D_SQUAD_DEMO", str(src))
    assert replays.squad_converter() == [sys.executable, "-m", "heat3d_ext_squad"]
    assert replays.squad_folder() == src
    monkeypatch.setattr("shutil.which", lambda name: "/bin/heat3d-squad-demo")
    assert replays.squad_converter() == ["/bin/heat3d-squad-demo"]


#: A stand-in reader: writes the two files of the command's contract.
FAKE = textwrap.dedent(
    """
    import json, sys
    from pathlib import Path
    import pyarrow as pa, pyarrow.parquet as pq
    out = Path(sys.argv[sys.argv.index("-o") + 1]) / "Test_Map"
    out.mkdir(parents=True)
    pq.write_table(pa.table({"event": ["position", "position", "vehicle"], "x": [0.0, 1.0, 2.0]}),
                   out / "m.parquet")
    doc = {"match": "m", "map": "Test_Map", "layer": "Test_Map_Layer_v1", "game_version": "v1",
           "recorded_unix": 1775576610.5, "duration_s": 600.25,
           "teams": [{"number": 1, "faction": "A"}, {"number": 2, "faction": "B"}],
           "players": [{"name": "One", "team": 1}, {"name": "Two", "team": 2}, {"name": ""}]}
    (out / "m.match.json").write_text(json.dumps(doc), encoding="utf-8")
    print("ok")
    """
)


def test_a_new_demo_is_converted_by_the_command(monkeypatch, tmp_path):
    script = tmp_path / "fake_reader.py"
    script.write_text(FAKE, encoding="utf-8")
    monkeypatch.setattr(replays, "squad_converter", lambda: [sys.executable, str(script)])
    monkeypatch.setattr(replays, "squad_folder", lambda: None)
    demo = tmp_path / "match.replay"
    demo.write_bytes(b"\x7f\xe2\xa2\x1c")
    ctx = Context(Settings(data=str(tmp_path / "data")), tmp_path / "data")
    _adapter().convert(demo, ctx)
    metas = list((tmp_path / "data" / "sessions").glob("*/*/meta.json"))
    assert len(metas) == 1
    meta = json.loads(metas[0].read_text(encoding="utf-8"))
    assert meta["stats"]["map"] == "Test_Map" and meta["stats"]["layer"] == "Test_Map_Layer_v1"
    assert meta["stats"]["players"] == 2 and meta["stats"]["match_seconds"] == 600.2
    assert meta["events"].get("vehicle") == 1 and meta["positions"] == 3


def test_a_failed_conversion_is_noted(monkeypatch, tmp_path):
    script = tmp_path / "fails.py"
    script.write_text("import sys; print('x.replay: not read - bad'); sys.exit(1)", encoding="utf-8")
    monkeypatch.setattr(replays, "squad_converter", lambda: [sys.executable, str(script)])
    monkeypatch.setattr(replays, "squad_folder", lambda: None)
    demo = tmp_path / "a.replay"
    demo.write_bytes(b"x")
    ctx = Context(Settings(data=str(tmp_path / "data")), tmp_path / "data")
    _adapter().convert(demo, ctx)
    lines = list((tmp_path / "data" / "sessions").glob("*/*/events.jsonl"))
    assert lines and "replay_failed" in lines[0].read_text(encoding="utf-8")


def test_the_watcher_holds_no_demo_parsing_of_its_own():
    root = Path(replays.__file__).resolve().parents[1]
    for f in root.rglob("*.py"):
        text = f.read_text(encoding="utf-8")
        assert "heat3d_ext_squad import" not in text and "import heat3d_ext_squad" not in text, f
        assert "0x1CA2E27F" not in text.upper().replace("0X", "0x"), f
