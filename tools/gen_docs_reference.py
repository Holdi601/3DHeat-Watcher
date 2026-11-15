"""
Writes docs/cli-reference.md from the code, so the reference cannot drift:
every command's `--help`, and the columns every session table and raw sidecar has.
The game pages have their own generator, tools/gen_game_pages.py.

    python tools/gen_docs_reference.py          (from the repository's root)
    python tools/gen_docs_reference.py --check  (exit 1 when the page is out of date; writes nothing)
"""

from __future__ import annotations

import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "docs" / "cli-reference.md"
PROG = "python -m heat3d_watch"


def help_text(args: list[str], env: dict) -> str:
    r = subprocess.run([sys.executable, "-m", "heat3d_watch", *args, "--help"], cwd=ROOT, env=env,
                       capture_output=True, text=True, encoding="utf-8")
    return (r.stdout or r.stderr).rstrip()


def build() -> str:
    with tempfile.TemporaryDirectory(prefix="heat3d-docs-") as home:
        # An empty data folder and a fixed width: nothing of this machine reaches the page.
        env = dict(os.environ, HEAT3D_NO_UPDATE="1", HEAT3D_WATCH_HOME=home, COLUMNS="88", PYTHONIOENCODING="utf-8")
        top = help_text([], env)
        verbs = re.search(r"\{([a-z0-9_,-]+)\}", top).group(1).split(",")
        out = ["---", "title: Reference", "nav_order: 14", "---", "", "# Command and column reference", "",
               "Generated from the code by `tools/gen_docs_reference.py`. [Commands](commands.md) explains",
               "each command step by step; this page lists everything exactly as the program has it.", "",
               f"## `{PROG}`", "", "```text", top, "```", ""]
        for v in verbs:
            out += [f"## `{v}`", "", "```text", help_text([v], env), "```", ""]
    sys.path.insert(0, str(ROOT))
    from heat3d_watch import session

    out += ["## Columns every table has", "",
            "`heat.parquet` starts with these columns, in this order; the game's own fields follow under their "
            "own names ([The data](the-data.md)):", "",
            ", ".join(f"`{c}`" for c in session.BASE_COLUMNS), "",
            f"`{session.RAW_TABLE}`, the raw sidecar of a live feed, starts with:", "",
            ", ".join(f"`{c}`" for c in session.RAW_COLUMNS), ""]
    return "\n".join(out)


def main() -> int:
    text = build()
    if "--check" in sys.argv[1:]:
        old = OUT.read_text(encoding="utf-8") if OUT.exists() else ""
        if old != text:
            print(f"out of date: {OUT.relative_to(ROOT)}")
            return 1
        return 0
    OUT.write_text(text, encoding="utf-8", newline="\n")
    print(f"wrote {OUT.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
