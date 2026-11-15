"""`dota-map`: the Dota 2 map is made by the external converter (3DHeat-Ext-Dota), run as a command, never imported."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

from heat3d_watch import cli


def test_says_how_to_install_the_converter_when_it_is_missing(tmp_path, capsys, monkeypatch):
    monkeypatch.setattr(cli, "dota_maps_converter", lambda: None)
    assert cli.main(["dota-map", "-o", str(tmp_path / "x.glb")]) == 2
    err = capsys.readouterr().err
    assert "3DHeat-Ext-Dota" in err and "heat3d-dota-maps" in err


def test_runs_the_converter_with_absolute_paths(tmp_path, monkeypatch):
    calls = []
    monkeypatch.setattr(cli, "dota_maps_converter", lambda: ["heat3d-dota-maps"])
    monkeypatch.setattr(cli, "dota_maps_folder", lambda: None)
    monkeypatch.setattr(subprocess, "run", lambda args, **kw: calls.append(args) or subprocess.CompletedProcess(args, 0))
    monkeypatch.chdir(tmp_path)
    assert cli.main(["dota-map", "-o", "dota.glb", "--game", "game", "--detail", "0"]) == 0
    (args,) = calls
    assert args[:3] == ["heat3d-dota-maps", "level", "dota"]
    assert args[args.index("-o") + 1] == str(tmp_path / "dota.glb")
    assert args[args.index("--game") + 1] == str(tmp_path / "game")
    assert args[args.index("--detail") + 1] == "0.0"
    assert "--source2viewer" not in args


def test_converter_found_beside_the_watcher(tmp_path, monkeypatch):
    folder = tmp_path / "dota-maps"
    (folder / "heat3d_ext_dota").mkdir(parents=True)
    (folder / "heat3d_ext_dota" / "__init__.py").write_text("")
    monkeypatch.setenv("HEAT3D_DOTA_MAPS", str(folder))
    monkeypatch.setattr("shutil.which", lambda _: None)
    assert cli.dota_maps_folder() == folder
    assert cli.dota_maps_converter() == [sys.executable, "-m", "heat3d_ext_dota"]


def test_the_watcher_holds_no_game_file_reader():
    decoders = Path(cli.__file__).parent / "decoders"
    assert not (decoders / "dota_map.py").exists() and not (decoders / "glb.py").exists()
