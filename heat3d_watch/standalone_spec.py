"""
The standalone app's description of this tool (app/spec.py): the background
recorder. It reads only what games publish for the purpose (telemetry ports,
game-state integrations, journals and logs, saved replays, platform
statistics) and, for single-player games only and when switched on, their
memory read and never written; it extracts no maps. The window starts and
stops watching, opens the sessions folder, and says which games it can see.
`python -m heat3d_watch.standalone_spec` runs the app from a checkout; the
release executables run the same.
"""

from __future__ import annotations

import sys
from pathlib import Path

from . import __version__
from .app.spec import Check, Spec, Task

TOOL = "heat3d-watch"


def _checks(found: dict, levels: Path) -> list[Check]:
    from .config import load

    from . import ghpc

    s = load()
    g = ghpc.check_line()
    return [
        Check("data", "Sessions folder", True, str(s.data_dir)),
        Check("replays", "Saved replays converted", True, "on" if s.replays else "off (config --set replays=true)"),
        Check(g["id"], g["label"], g["ok"], g["detail"]),
    ]


def _apply_source(release) -> str:
    """A checkout or source copy updates the way it always did (heat3d_update in the repository root)."""
    root = str(Path(__file__).resolve().parents[1])
    if root not in sys.path:
        sys.path.append(root)
    import heat3d_update

    return heat3d_update.apply(release)


SPEC = Spec(
    id="heat3d-watcher",
    name="3DHeat Watcher",
    repo="Holdi601/3DHeat-Watcher",
    version=__version__,
    tools={TOOL: "heat3d_watch.cli:main"},
    default_tool=TOOL,
    description="records what games publish about your play, in the background, on your own machine",
    module="heat3d_watch.standalone_spec",
    games=[],
    checks=_checks,
    tasks=[
        Task("run", "Watch my games", [], lambda v, levels: [TOOL, "run"],
             help="records every game it can see while it runs; play as usual, then press Stop",
             kind="live", action="Start watching", output=""),
        Task("status", "Which games are running now", [], lambda v, levels: [TOOL, "status"], kind="quick",
             action="Show", output=""),
        Task("games", "What each game gives, and from where", [], lambda v, levels: [TOOL, "games"], kind="quick",
             action="Show", output=""),
        Task("open", "The sessions folder", [], lambda v, levels: [TOOL, "open"], kind="open", action="Open",
             help="every recorded session, one folder each", output=""),
        Task("stop", "A watcher started elsewhere", [], lambda v, levels: [TOOL, "stop"], kind="quick",
             action="Stop it", help="asks a watcher running in the background to close its sessions and end",
             output=""),
        Task("ghpc-install", "Install or update the GHPC recorder", [],
             lambda v, levels: [TOOL, "ghpc", "install", "--yes"], kind="quick", action="Install",
             help="puts the recorder mod into Gunner, HEAT, PC! (MelonLoader must be installed first); close the game before",
             output=""),
        Task("ghpc-status", "GHPC recorder: what is installed", [], lambda v, levels: [TOOL, "ghpc", "status"],
             kind="quick", action="Show", output=""),
    ],
    min_free_gb=1.0,
    notice="Not affiliated with or endorsed by any game's makers or publishers.",
    # Records in the background: an icon by the clock says so and opens, pauses or quits it.
    tray=True,
)

if __name__ == "__main__":
    from .app.entry import main

    raise SystemExit(main(SPEC, apply_source=_apply_source))
