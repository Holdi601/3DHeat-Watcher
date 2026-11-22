"""
The 3DHeat recorder for Gunner, HEAT, PC!: finding the game, checking that
MelonLoader is there, and putting the recorder mod in (or taking it out).

GHPC has no replays and no telemetry of its own; the recorder is a MelonLoader
mod (sources in `mods/ghpc`) that writes each mission into one `.3dheat` file.
MelonLoader itself is not shipped or downloaded here: the player installs it
from its own releases (MELONLOADER_URL) and starts the game once.

    python -m heat3d_watch ghpc status [--json]
    python -m heat3d_watch ghpc install [--yes] [--game-dir DIR]
    python -m heat3d_watch ghpc remove [--game-dir DIR]

`install` shows what it would do and asks; with `--yes` (or automatic updates
switched on) it does it. The mod's DLL replaced by an update is kept in
`<GHPC>/Bin/UserData/Heat3DRecorder/backup/`.
"""

from __future__ import annotations

import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import time
from pathlib import Path

GAME = "Gunner, HEAT, PC!"
#: The install folder's name in a Steam library (it has had both spellings).
INSTALL_DIRS = ("Gunner HEAT PC", "Gunner, HEAT, PC!")
EXE = "GHPC.exe"
MOD_DLL = "Heat3DRecorder.GHPC.dll"
MELONLOADER_URL = "https://github.com/LavaGang/MelonLoader/releases"
MELONLOADER_WIKI = "https://melonwiki.xyz/"

HERE = Path(__file__).resolve().parent
REPO = HERE.parent
#: Where a release carries the built mod (CI puts it there before packing), and where a checkout builds it.
BUNDLED = HERE / "data" / "ghpc"
PROJECT = REPO / "mods" / "ghpc" / "recorder"
BUILT = PROJECT / "bin" / "Release"


def _env_dir() -> Path | None:
    v = os.environ.get("HEAT3D_GHPC_DIR", "").strip()
    return Path(v) if v else None


def _is_install(p: Path) -> bool:
    return (p / "Bin" / EXE).is_file() or (p / EXE).is_file()


def find_game(given: str | Path | None = None) -> Path | None:
    """The GHPC install folder: one given, `HEAT3D_GHPC_DIR`, else every Steam library."""
    for p in (given, _env_dir()):
        if p and _is_install(Path(p)):
            return Path(p)
    from .app.paths import steam_game_dirs

    for name in INSTALL_DIRS:
        for p in steam_game_dirs(name):
            if _is_install(p):
                return p
    return None


def bin_dir(root: Path) -> Path:
    """The folder with GHPC.exe: MelonLoader and its Mods folder go beside it."""
    return root / "Bin" if (root / "Bin" / EXE).is_file() else root


def melonloader(bin: Path) -> dict:
    """Whether MelonLoader is installed beside the game, and which version its last log names."""
    ml = bin / "MelonLoader"
    proxy = next((n for n in ("version.dll", "winhttp.dll", "dobby.dll") if (bin / n).is_file()), None)
    found = ml.is_dir() and proxy is not None
    version = None
    logs = [ml / "Latest.log"]
    if (ml / "Logs").is_dir():
        logs += sorted((ml / "Logs").glob("*.log"), reverse=True)[:1]
    for log in logs:
        try:
            head = log.read_text(encoding="utf-8", errors="replace")[:4000]
        except OSError:
            continue
        m = re.search(r"MelonLoader v(\d+(?:\.\d+)+)", head)
        if m:
            version = m.group(1)
            break
    return {"found": found, "folder": str(ml), "proxy": proxy, "version": version, "ranOnce": (bin / "Mods").is_dir()}


def _sha(p: Path) -> str:
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 16), b""):
            h.update(b)
    return h.hexdigest()


def project_version() -> str | None:
    try:
        m = re.search(r"<Version>([^<]+)</Version>", (PROJECT / "Heat3DRecorder.GHPC.csproj").read_text(encoding="utf-8"))
    except OSError:
        return None
    return m.group(1).strip() if m else None


def bundled() -> dict | None:
    """The recorder this copy of the watcher carries: {path, version, sha256}, or None."""
    for folder in (BUNDLED, BUILT):
        dll = folder / MOD_DLL
        if not dll.is_file():
            continue
        version = None
        try:
            version = json.loads((folder / "recorder.json").read_text(encoding="utf-8")).get("version")
        except (OSError, ValueError):
            version = project_version()
        return {"path": str(dll), "version": version, "sha256": _sha(dll)}
    return None


def build(log=print) -> dict | None:
    """Builds the mod from `mods/ghpc` with the .NET SDK (a checkout only)."""
    dotnet = shutil.which("dotnet")
    if dotnet is None or not PROJECT.is_dir():
        return None
    log("building the recorder mod (dotnet build -c Release) ...")
    r = subprocess.run([dotnet, "build", str(PROJECT), "-c", "Release", "-nologo", "-v", "q"], capture_output=True, text=True)
    if r.returncode != 0:
        log((r.stdout + r.stderr)[-2000:])
        return None
    return bundled()


def installed(bin: Path) -> dict | None:
    dll = bin / "Mods" / MOD_DLL
    if not dll.is_file():
        return None
    info: dict = {}
    try:
        info = json.loads((bin / "UserData" / "Heat3DRecorder" / "installed.json").read_text(encoding="utf-8"))
    except (OSError, ValueError):
        pass
    return {"path": str(dll), "version": info.get("version"), "sha256": _sha(dll)}


def game_running() -> bool:
    try:
        import psutil
    except ImportError:
        return False
    for p in psutil.process_iter(["name"]):
        if (p.info.get("name") or "").lower() == EXE.lower():
            return True
    return False


def status(given: str | Path | None = None) -> dict:
    """Everything `install` needs to know, as plain data (also `ghpc status --json`)."""
    root = find_game(given)
    out: dict = {"game": GAME, "install": str(root) if root else None, "melonloader": None, "installed": None,
                 "bundled": bundled(), "current": False, "running": game_running(), "output": str(output_folder())}
    if root is None:
        return out
    b = bin_dir(root)
    out["bin"] = str(b)
    out["melonloader"] = melonloader(b)
    out["installed"] = installed(b)
    if out["installed"] and out["bundled"]:
        out["current"] = out["installed"]["sha256"] == out["bundled"]["sha256"]
    return out


def output_folder() -> Path:
    """Where the recorder writes its mission files by default (its OutputFolder setting)."""
    base = os.environ.get("LOCALAPPDATA") or str(Path.home() / "AppData" / "Local")
    return Path(base) / "3DHeat" / "Watcher" / "recorders" / "ghpc"


def check_line() -> dict:
    """One line for the standalone app's `--check --json`."""
    st = status()
    if st["install"] is None:
        return {"id": "ghpc", "label": f"{GAME} recorder", "ok": True, "detail": "the game is not installed here; only needed to record it"}
    ml = st["melonloader"] or {}
    if not ml.get("found"):
        return {"id": "ghpc", "label": f"{GAME} recorder", "ok": False,
                "detail": f"MelonLoader is not installed in {st['bin']}: install it from {MELONLOADER_URL}, start the game once, then install the recorder"}
    if st["installed"] is None:
        return {"id": "ghpc", "label": f"{GAME} recorder", "ok": False, "detail": "not installed: `ghpc install` (or the window's Install the GHPC recorder)"}
    if st["bundled"] and not st["current"]:
        return {"id": "ghpc", "label": f"{GAME} recorder", "ok": False,
                "detail": f"an update is ready ({st['bundled'].get('version') or 'newer build'}): `ghpc install`"}
    return {"id": "ghpc", "label": f"{GAME} recorder", "ok": True, "detail": f"installed in {st['installed']['path']}"}


def plan(st: dict, *, remove: bool = False) -> tuple[list[str], list[str]]:
    """(what would be done, why it cannot be) for an install, update or removal."""
    todo: list[str] = []
    blocked: list[str] = []
    if st["install"] is None:
        blocked.append(f"{GAME} not found in any Steam library: pass --game-dir <folder with Bin\\{EXE}> or set HEAT3D_GHPC_DIR")
        return todo, blocked
    b = Path(st["bin"])
    if st["running"]:
        blocked.append(f"{GAME} is running: close it first (its mods are in use while it runs)")
    if remove:
        if st["installed"] is None:
            blocked.append("the recorder is not installed")
        else:
            todo.append(f"remove {st['installed']['path']} (a copy goes to UserData\\Heat3DRecorder\\backup)")
        return todo, blocked
    ml = st["melonloader"] or {}
    if not ml.get("found"):
        blocked.append(f"MelonLoader is not installed in {b}. Install it with its own installer from {MELONLOADER_URL} "
                       f"(pick {EXE}), start the game once so it sets itself up, then run this again")
    if st["bundled"] is None:
        blocked.append("this copy of the watcher has no built recorder: run `ghpc install --build` with the .NET SDK installed, "
                       "or use a release of the watcher")
    if blocked:
        return todo, blocked
    target = b / "Mods" / MOD_DLL
    if st["installed"] is None:
        todo.append(f"copy the recorder {st['bundled'].get('version') or ''} to {target}".replace("  ", " "))
    elif not st["current"]:
        todo.append(f"update {target} to {st['bundled'].get('version') or 'the newer build'} "
                    f"(installed: {st['installed'].get('version') or 'another build'}; the old one is kept in UserData\\Heat3DRecorder\\backup)")
    return todo, blocked


def _backup(bin: Path, dll: Path) -> None:
    folder = bin / "UserData" / "Heat3DRecorder" / "backup"
    folder.mkdir(parents=True, exist_ok=True)
    shutil.copy2(dll, folder / f"{dll.stem}-{time.strftime('%Y%m%d-%H%M%S')}{dll.suffix}")


def install(given: str | Path | None = None, *, yes: bool = False, ask=input, log=print, build_first: bool = False) -> int:
    """Puts the recorder in (or updates it), after saying what it does and asking unless `yes`."""
    if build_first:
        build(log)
    st = status(given)
    todo, blocked = plan(st)
    for b in blocked:
        log(f"cannot install: {b}")
    if blocked:
        return 1
    if not todo:
        log(f"the recorder is installed and current: {st['installed']['path']}")
        return 0
    for t in todo:
        log(f"will {t}")
    if not yes:
        try:
            if ask("Go ahead? [y/N] ").strip().lower() not in ("y", "yes", "j", "ja"):
                log("nothing changed")
                return 0
        except EOFError:
            log("nothing changed (no answer)")
            return 0
    b = Path(st["bin"])
    target = b / "Mods" / MOD_DLL
    target.parent.mkdir(parents=True, exist_ok=True)
    if target.exists():
        _backup(b, target)
    tmp = target.with_suffix(".tmp")
    shutil.copy2(st["bundled"]["path"], tmp)
    os.replace(tmp, target)
    info = b / "UserData" / "Heat3DRecorder" / "installed.json"
    info.parent.mkdir(parents=True, exist_ok=True)
    info.write_text(json.dumps({"version": st["bundled"].get("version"), "sha256": st["bundled"]["sha256"],
                                "installed": time.strftime("%Y-%m-%dT%H:%M:%S"), "from": st["bundled"]["path"]}, indent=1),
                    encoding="utf-8")
    log(f"installed {target}")
    log(f"missions are written to {st['output']} (the recorder's OutputFolder setting in UserData\\MelonPreferences.cfg)")
    return 0


def remove(given: str | Path | None = None, *, yes: bool = False, ask=input, log=print) -> int:
    st = status(given)
    todo, blocked = plan(st, remove=True)
    for b in blocked:
        log(f"cannot remove: {b}")
    if blocked:
        return 1
    for t in todo:
        log(f"will {t}")
    if not yes:
        try:
            if ask("Go ahead? [y/N] ").strip().lower() not in ("y", "yes", "j", "ja"):
                log("nothing changed")
                return 0
        except EOFError:
            return 0
    b = Path(st["bin"])
    dll = Path(st["installed"]["path"])
    _backup(b, dll)
    dll.unlink()
    log(f"removed {dll}")
    return 0


def main(argv: list[str]) -> int:
    import argparse

    ap = argparse.ArgumentParser(prog="heat3d_watch ghpc", description=f"the 3DHeat recorder mod for {GAME}")
    ap.add_argument("action", choices=("status", "install", "update", "remove"), nargs="?", default="status")
    ap.add_argument("--game-dir", help=f"the {GAME} folder (the one with Bin\\{EXE}), when it is not in a Steam library")
    ap.add_argument("--yes", action="store_true", help="do it without asking")
    ap.add_argument("--build", action="store_true", help="build the mod from mods/ghpc first (needs the .NET SDK)")
    ap.add_argument("--json", action="store_true", help="status as JSON")
    a = ap.parse_args(argv)
    if a.action == "status":
        st = status(a.game_dir)
        if a.json:
            print(json.dumps(st, indent=1))
            return 0
        print(f"{GAME}: {st['install'] or 'not found'}")
        if st["install"]:
            ml = st["melonloader"]
            print(f"MelonLoader: {'installed' + (' ' + ml['version'] if ml['version'] else '') if ml['found'] else 'not installed (' + MELONLOADER_URL + ')'}")
            inst = st["installed"]
            print(f"Recorder: {'installed' + (' ' + inst['version'] if inst and inst['version'] else '') if inst else 'not installed'}"
                  + ("" if not inst or st["current"] or not st["bundled"] else " - an update is ready (ghpc install)"))
        print(f"Missions are written to: {st['output']}")
        return 0
    from .app import update

    yes = a.yes or update.auto_enabled("heat3d-watcher")
    if a.action == "remove":
        return remove(a.game_dir, yes=a.yes)
    return install(a.game_dir, yes=yes, build_first=a.build)
