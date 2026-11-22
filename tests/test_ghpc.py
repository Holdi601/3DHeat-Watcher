"""
Gunner, HEAT, PC!: the recorder mod's file format, its installer and the adapter.

The format tests write a made-up mission through the mod's own writer (the C#
code in mods/ghpc/recorder/Format, built by `dotnet` from
mods/ghpc/tests/synthetic) and read the file back with independent readers:
zipfile, pyarrow, json. They skip where the .NET SDK is not installed. Nothing
here comes from the game.
"""

from __future__ import annotations

import hashlib
import io
import json
import re
import shutil
import subprocess
import zipfile
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
SYNTHETIC = ROOT / "mods" / "ghpc" / "tests" / "synthetic"
MOD = ROOT / "mods" / "ghpc" / "recorder"


def _synthetic(out: Path, *extra: str) -> Path:
    dotnet = shutil.which("dotnet")
    if dotnet is None:
        pytest.skip("the .NET SDK is not installed")
    r = subprocess.run([dotnet, "run", "--project", str(SYNTHETIC), "-v", "q", "--", str(out), *extra],
                       capture_output=True, text=True, timeout=600)
    assert r.returncode == 0, r.stdout + r.stderr
    files = sorted(out.glob("*.3dheat"))
    assert len(files) == 1, (r.stdout, list(out.iterdir()))
    return files[0]


@pytest.fixture(scope="module")
def mission(tmp_path_factory) -> Path:
    return _synthetic(tmp_path_factory.mktemp("ghpc"))


def _read(path: Path):
    import pyarrow.parquet as pq

    z = zipfile.ZipFile(path)
    man = json.loads(z.read("manifest.json"))
    table = pq.read_table(io.BytesIO(z.read(man["roles"]["table"])))
    doc = json.loads(z.read(man["roles"]["match"]))
    raw = pq.read_table(io.BytesIO(z.read(man["roles"]["raw"])))
    return z, man, table, doc, raw


def test_the_container_is_laid_out_as_the_viewer_reads_it(mission):
    z = zipfile.ZipFile(mission)
    assert z.testzip() is None
    infos = z.infolist()
    assert infos[0].filename == "manifest.json"
    man = json.loads(z.read("manifest.json"))
    assert man["format"] == "3dheat" and man["format_version"].startswith("1.") and man["game"] == "ghpc"
    assert man["converter"]["name"] == "heat3d-ghpc-recorder"
    # The table right after the manifest, stored (read in place by byte range); text deflated.
    assert infos[1].filename == man["roles"]["table"] and infos[1].compress_type == zipfile.ZIP_STORED
    assert z.getinfo(man["roles"]["raw"]).compress_type == zipfile.ZIP_STORED
    assert z.getinfo(man["roles"]["match"]).compress_type == zipfile.ZIP_DEFLATED
    for m in man["members"]:
        data = z.read(m["name"])
        assert len(data) == m["bytes"] and hashlib.sha256(data).hexdigest() == m["sha256"], m["name"]
        assert all(f.flag_bits & 0x0800 for f in infos)  # UTF-8 names
    assert man["match"] == "TEST01_synthetic_20260101-120000" and man["map"] == "test_terrain"


def test_the_table_carries_its_reading_instructions_and_the_shared_columns(mission):
    _, man, table, _, _ = _read(mission)
    hints = json.loads(table.schema.metadata[b"heat3d"])
    assert hints["axes"] == {"up": "y", "flipX": False, "flipY": False, "flipZ": True, "scale": 1}
    cols = hints["columns"]
    assert (cols["personId"], cols["teamId"], cols["sessionId"], cols["lookMode"]) == ("track", "team", "match", "vector")
    names = set(table.column_names)
    # The columns the viewer's replay, hit analysis and outcome filters read (as the War Thunder converter writes them).
    for c in ("time", "event", "match", "track", "life", "player", "team", "Vehicle", "VehicleName", "kind", "x", "y", "z",
              "dirX", "heading", "speed", "alive", "turretYaw", "gunPitch", "other", "otherVehicle", "otherLife",
              "hitLocalX", "hitLocalY", "hitLocalZ", "hitDirX", "hitOutcome", "targetX", "calibre", "ammoType",
              "ammoName", "won", "matchWon", "round"):
        assert c in names, c
    assert set(hints["columns"]["extra"]) <= names
    assert table.num_rows == man["members"][0]["rows"]
    assert str(table.schema.field("time").type) == "double" and str(table.schema.field("x").type) == "float"
    assert str(table.schema.field("event").type) == "string"


def test_samples_shots_hits_and_damage_come_back_as_written(mission):
    _, _, table, _, _ = _read(mission)
    rows = table.to_pylist()
    ev = [r["event"] for r in rows]
    for e, n in (("spawn", 4), ("finish", 4), ("launch", 3), ("shot", 3), ("plate_hit", 1), ("crew_ko", 1),
                 ("module_destroyed", 1), ("fire_on", 1), ("destroyed", 1), ("spall", 1), ("story", 2), ("mission_state", 3)):
        assert ev.count(e) == n, e
    assert "log" not in ev  # the game's log goes to the raw sidecar
    samples = [r for r in rows if r["event"] is None]
    assert len(samples) == 601 * 4
    blue = [r for r in samples if r["player"] == "Blue 1"]
    assert blue[0]["x"] == pytest.approx(-500) and blue[-1]["x"] == pytest.approx(-140)
    assert blue[0]["isPlayer"] == 1 and blue[0]["Vehicle"] == "M1IP" and blue[0]["kind"] == "tank"
    hits = [r for r in rows if r["event"] == "shot" and r["otherVehicle"]]
    assert [h["hitOutcome"] for h in hits] == ["ricochet", "penetration"]
    pen = hits[1]
    assert (pen["hitLocalX"], pen["hitLocalY"], pen["hitLocalZ"]) == pytest.approx((2, 1.9, -0.4))
    assert pen["otherLife"] == "u3" and pen["penetrated"] == 1 and pen["penetrationLevel"] == 2
    assert pen["calibre"] == 105 and pen["ammoType"] == "APFSDS" and pen["speed"] == pytest.approx(1490)
    miss = [r for r in rows if r["event"] == "shot" and not r["otherVehicle"]][0]
    assert miss["hitOutcome"] == "ground" and miss["hitLocalX"] is None and miss["targetY"] == 99
    crew = [r for r in rows if r["event"] == "crew_ko"][0]
    assert crew["crewRole"] == "gunner" and crew["other"] == "Blue 1" and crew["player"] == "Red 1"
    mod = [r for r in rows if r["event"] == "module_destroyed"][0]
    assert mod["module"] == mod["weapon"] == "main gun breech"
    dead = [r for r in rows if r["event"] == "destroyed"][0]
    assert dead["player"] == "Red 1" and dead["other"] == "Blue 1" and dead["state"] == "neutralized"
    assert dead["distance"] > 0
    assert [r["spall"] for r in rows if r["event"] == "spall"] == [14]
    story = [r["text"] for r in rows if r["event"] == "story"]
    assert story[1].splitlines()[1] == "Gunner killed"


def test_every_row_with_a_side_says_whether_it_won(mission):
    _, _, table, _, _ = _read(mission)
    for r in table.to_pylist():
        if r["team"]:
            assert r["won"] == (1 if r["team"] == "Blue" else 0) and r["matchWon"] == r["won"]
            assert r["roundEndReason"] == "elimination" and r["round"] == 1


def test_the_match_document_and_the_raw_log(mission):
    _, _, _, doc, raw = _read(mission)
    assert doc["format"] == "heat3d-ghpc-match" and doc["game"] == "ghpc"
    assert (doc["map"], doc["mission"], doc["started"]) == ("test_terrain", "TEST01_synthetic", "2026-01-01T12:00:00Z")
    assert doc["result"]["winner"] == "Blue" and doc["timePlayed"] == 60
    assert [u["uid"] for u in doc["units"]] == [1, 2, 3, 4]
    assert doc["units"][0]["crew"] == ["commander", "gunner", "loader", "driver"]
    assert doc["units"][2]["out"] is True
    assert doc["kills"][0]["killer"] == "Blue 1" and doc["kills"][0]["victimVehicle"] == "T72M1"
    sc = doc["selfCheck"]["completeness"]
    assert sc["lost"] == 0 and sc["types"]["log"]["raw"] == 2 and sc["types"]["shot"]["decoded"] == 3
    assert raw.to_pydict()["text"] == ["MissionState changed to Playing", "a warning line from the game's log"]


def test_a_mission_cut_off_is_built_from_its_spool_at_the_next_start(tmp_path, mission):
    crashed = _synthetic(tmp_path, "--crash")
    _, _, a, da, _ = _read(mission)
    _, _, b, db, _ = _read(crashed)
    assert a.num_rows == b.num_rows and a.column("x").to_pylist() == b.column("x").to_pylist()
    assert da["kills"] == db["kills"]
    assert not list((tmp_path / "spool").glob("*.spool"))


# ------------------------------------------------------------------ the mod's own code


def test_the_mod_only_reads_the_game():
    """Hooks return nothing (the game's method always runs) and nothing in the game is set or called."""
    src = "\n".join(p.read_text(encoding="utf-8") for p in (MOD / "Game").glob("*.cs"))
    for forbidden in ("SetValue(", "AddComponent", "Destroy(", "SetActive(", "Instantiate(", "__result =", "ref __result",
                      "SendMessage(", "BroadcastMessage(", "Time.timeScale =", "PlayerPrefs.Set", ".Invoke(round",
                      "GetMethod(\"Fire", "transform.position =", "transform.rotation ="):
        assert forbidden not in src, forbidden
    hooks = (MOD / "Game" / "Hooks.cs").read_text(encoding="utf-8")
    for m in re.finditer(r"static (\w+) (AfterInit|BeforePen|AfterPenBool|AfterPen|AfterStory)\(", hooks):
        assert m.group(1) == "void", m.group(0)
    # Method calls through reflection are getters only (Api.Getter's fallback).
    api = (MOD / "Game" / "Api.cs").read_text(encoding="utf-8")
    assert api.count(".Invoke(") == 1 and "GetGetMethod(true)" in api


def test_the_mod_names_the_game_and_its_version():
    mod = (MOD / "Game" / "Mod.cs").read_text(encoding="utf-8")
    assert '[assembly: MelonGame("Radian Simulations LLC", "GHPC")]' in mod
    version = re.search(r'Version = "([^"]+)"', mod).group(1)
    assert f"<Version>{version}</Version>" in (MOD / "Heat3DRecorder.GHPC.csproj").read_text(encoding="utf-8")


# ------------------------------------------------------------------ the installer


@pytest.fixture
def game(tmp_path, monkeypatch):
    from heat3d_watch import ghpc

    root = tmp_path / "Gunner HEAT PC"
    (root / "Bin").mkdir(parents=True)
    (root / "Bin" / "GHPC.exe").write_bytes(b"MZ")
    bundle = tmp_path / "bundle"
    bundle.mkdir()
    (bundle / ghpc.MOD_DLL).write_bytes(b"mod build 1")
    (bundle / "recorder.json").write_text(json.dumps({"version": "0.1.0"}), encoding="utf-8")
    monkeypatch.setattr(ghpc, "BUNDLED", bundle)
    monkeypatch.setattr(ghpc, "BUILT", tmp_path / "nothing")
    monkeypatch.setattr(ghpc, "game_running", lambda: False)
    monkeypatch.setenv("HEAT3D_GHPC_DIR", str(root))
    return root, bundle


def _melonloader(root: Path) -> None:
    (root / "Bin" / "MelonLoader").mkdir()
    (root / "Bin" / "version.dll").write_bytes(b"MZ")
    (root / "Bin" / "MelonLoader" / "Latest.log").write_text("[00:00:00.000] MelonLoader v0.6.6 Open-Beta\n", encoding="utf-8")


def test_install_needs_melonloader_and_says_where_to_get_it(game):
    from heat3d_watch import ghpc

    root, _ = game
    said = []
    assert ghpc.install(yes=True, log=said.append) == 1
    assert any("MelonLoader is not installed" in s and ghpc.MELONLOADER_URL in s for s in said)
    assert not (root / "Bin" / "Mods").exists()
    assert ghpc.check_line()["ok"] is False


def test_install_asks_then_copies_and_an_update_keeps_the_old_one(game):
    from heat3d_watch import ghpc

    root, bundle = game
    _melonloader(root)
    st = ghpc.status()
    assert st["melonloader"]["version"] == "0.6.6"
    assert ghpc.install(ask=lambda q: "n", log=lambda s: None) == 0
    assert not (root / "Bin" / "Mods" / ghpc.MOD_DLL).exists()
    assert ghpc.install(ask=lambda q: "y", log=lambda s: None) == 0
    dll = root / "Bin" / "Mods" / ghpc.MOD_DLL
    assert dll.read_bytes() == b"mod build 1"
    assert ghpc.status()["current"] and ghpc.check_line()["ok"]
    said = []
    assert ghpc.install(log=said.append, ask=lambda q: pytest.fail("asked although nothing changes")) == 0
    assert "installed and current" in said[0]
    (bundle / ghpc.MOD_DLL).write_bytes(b"mod build 2")
    (bundle / "recorder.json").write_text(json.dumps({"version": "0.2.0"}), encoding="utf-8")
    assert "update is ready" in ghpc.check_line()["detail"]
    asked = []
    assert ghpc.install(ask=lambda q: asked.append(q) or "y", log=lambda s: None) == 0
    assert asked and dll.read_bytes() == b"mod build 2"
    backups = list((root / "Bin" / "UserData" / "Heat3DRecorder" / "backup").glob("*.dll"))
    assert [b.read_bytes() for b in backups] == [b"mod build 1"]
    info = json.loads((root / "Bin" / "UserData" / "Heat3DRecorder" / "installed.json").read_text(encoding="utf-8"))
    assert info["version"] == "0.2.0"


def test_nothing_is_changed_while_the_game_runs(game, monkeypatch):
    from heat3d_watch import ghpc

    root, _ = game
    _melonloader(root)
    monkeypatch.setattr(ghpc, "game_running", lambda: True)
    said = []
    assert ghpc.install(yes=True, log=said.append) == 1
    assert any("is running" in s for s in said)


def test_remove_keeps_a_copy(game):
    from heat3d_watch import ghpc

    root, _ = game
    _melonloader(root)
    ghpc.install(yes=True, log=lambda s: None)
    assert ghpc.remove(yes=True, log=lambda s: None) == 0
    assert not (root / "Bin" / "Mods" / ghpc.MOD_DLL).exists()
    assert list((root / "Bin" / "UserData" / "Heat3DRecorder" / "backup").glob("*.dll"))


def test_setup_through_the_adapter(game, tmp_path):
    from heat3d_watch import ghpc
    from heat3d_watch.adapters import load
    from heat3d_watch.adapters.base import Context
    from heat3d_watch.config import Settings

    root, _ = game
    a = load()["ghpc"]
    ctx = Context(Settings(data=str(tmp_path / "data")), tmp_path / "data")
    assert a.setup(ctx, apply=False)[0].startswith("cannot: MelonLoader")
    _melonloader(root)
    plan = a.setup(ctx, apply=False)
    assert plan and plan[0].startswith("copy the recorder")
    a.setup(ctx, apply=True)
    assert (root / "Bin" / "Mods" / ghpc.MOD_DLL).is_file()
    assert a.setup(ctx, apply=False) == []


# ------------------------------------------------------------------ the adapter


def test_a_new_mission_file_becomes_a_session(tmp_path, mission, monkeypatch):
    from heat3d_watch import ghpc
    from heat3d_watch.adapters import load
    from heat3d_watch.adapters.base import Context
    from heat3d_watch.config import Settings

    inbox = tmp_path / "inbox"
    inbox.mkdir()
    shutil.copy2(mission, inbox / mission.name)
    monkeypatch.setattr(ghpc, "output_folder", lambda: inbox)
    a = load()["ghpc"]
    ctx = Context(Settings(data=str(tmp_path / "data")), tmp_path / "data")
    assert a.convert_existing(ctx) == 1
    files = list((tmp_path / "data").rglob("*.3dheat"))
    assert len(files) == 1 and files[0].read_bytes() == mission.read_bytes()
    meta = json.loads((files[0].parent / "meta.json").read_text(encoding="utf-8"))
    stats = meta.get("stats") or {}
    assert stats.get("map") == "test_terrain" and stats.get("kills") == 1 and stats.get("won") == 1
    assert stats.get("shots") == 3 and stats.get("vehicle") == "M1IP Abrams"
