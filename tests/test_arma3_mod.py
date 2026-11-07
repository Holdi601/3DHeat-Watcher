"""The Arma 3 recorder mod (mods/arma3): its build, and that its parts agree.

The mod itself runs only inside an Arma 3 server, so what is checked here is
what can be checked without one: the PBO the build writes reads back with a
good checksum and the right prefix, every function the config names has its
file (and the other way round), and the extension's source names the entry
points Arma looks for.
"""

from __future__ import annotations

import importlib.util
import re
from pathlib import Path

MOD = Path(__file__).resolve().parents[1] / "mods" / "arma3"


def _build_module():
    spec = importlib.util.spec_from_file_location("arma3_build", MOD / "build.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_build_packs_the_addon(tmp_path):
    build = _build_module()
    out = build.build(tmp_path / "@heat3d")
    props, files = build.unpack((out / "addons" / "heat3d_recorder.pbo").read_bytes())
    assert props == {"prefix": "heat3d_recorder"}
    assert "config.cpp" in files
    assert "functions\\fn_init.sqf" in files
    assert files["config.cpp"] == (MOD / "addons" / "heat3d_recorder" / "config.cpp").read_bytes()
    assert (out / "mod.cpp").is_file()


def test_config_and_functions_agree():
    addon = MOD / "addons" / "heat3d_recorder"
    config = (addon / "config.cpp").read_text(encoding="utf-8")
    block = config[config.index("class recorder") :]
    named = set(re.findall(r"class (\w+) \{", block[: block.index("};\n    };")])) - {"recorder"}
    present = {p.stem.removeprefix("fn_") for p in (addon / "functions").glob("fn_*.sqf")}
    assert named == present
    # Every function the scripts call exists.
    called = set()
    for p in (addon / "functions").glob("*.sqf"):
        called |= set(re.findall(r"heat3d_fnc_(\w+)", p.read_text(encoding="utf-8")))
    assert called <= present


def test_extension_has_the_entry_points_arma_calls():
    src = (MOD / "extension" / "heat3d.c").read_text(encoding="utf-8")
    for fn in ("RVExtensionVersion(char *output, unsigned int outputSize)", "RVExtension(char *output, unsigned int outputSize, const char *function)", "RVExtensionArgs(char *output, unsigned int outputSize, const char *function, const char **argv, unsigned int argc)"):
        assert fn in src
