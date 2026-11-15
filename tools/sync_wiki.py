"""
Rebuilds docs/wiki - the copy of these pages published as the repository's GitHub wiki - from docs/,
so the wiki never says anything the documentation site does not.

    python tools/sync_wiki.py          (from the repository's root)
    python tools/sync_wiki.py --check  (exit 1 when the wiki copy is out of date; writes nothing)

Every docs/*.md page becomes docs/wiki/<page>.md (docs/index.md becomes Home.md) without its front
matter, with links to other pages without `.md` (the wiki's form) and pictures pointing at the
documentation site. _Sidebar.md lists the pages in the site's order.
"""

from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"
WIKI = DOCS / "wiki"


def site() -> str:
    url = subprocess.run(["git", "remote", "get-url", "origin"], cwd=ROOT, capture_output=True, text=True).stdout
    name = url.strip().rstrip("/").removesuffix(".git").rsplit("/", 1)[-1]
    return f"https://holdi601.github.io/{name}/"


def front(text: str) -> tuple[dict[str, str], str]:
    if not text.startswith("---\n"):
        return {}, text
    head, _, body = text[4:].partition("\n---\n")
    meta = {}
    for line in head.splitlines():
        k, _, v = line.partition(":")
        meta[k.strip()] = v.strip().strip('"')
    return meta, body.lstrip("\n")


def wikify(body: str, base: str) -> str:
    body = re.sub(r"\]\(index\.md(#[^)]*)?\)", lambda m: f"](Home{m.group(1) or ''})", body)
    body = re.sub(r"\]\(([\w.-]+)\.md(#[^)]*)?\)", lambda m: f"]({m.group(1)}{m.group(2) or ''})", body)
    return re.sub(r"\]\((assets/[^)]+)\)", lambda m: f"]({base}{m.group(1)})", body)


def build() -> dict[str, str]:
    base = site()
    pages = []
    for p in sorted(DOCS.glob("*.md")):
        meta, body = front(p.read_text(encoding="utf-8"))
        name = "Home" if p.stem == "index" else p.stem
        pages.append((meta, name, wikify(body, base)))
    out = {f"{name}.md": body for _, name, body in pages}
    top = [(float(m.get("nav_order", 999)), m.get("title", n), n) for m, n, _ in pages if not m.get("parent")]
    title = next((m.get("title") for m, n, _ in pages if n == "Home"), "Home")
    side = [f"**[Documentation site]({base})**", ""] + [f"- [{t}]({n})" for _, t, n in sorted(top)]
    out["_Sidebar.md"] = "\n".join(side) + "\n"
    return out


def main() -> int:
    want = build()
    have = {p.name: p.read_text(encoding="utf-8") for p in WIKI.glob("*.md")} if WIKI.exists() else {}
    if "--check" in sys.argv[1:]:
        stale = sorted(n for n in set(want) | set(have) if want.get(n) != have.get(n))
        for n in stale:
            print(f"out of date: docs/wiki/{n}")
        return 1 if stale else 0
    WIKI.mkdir(exist_ok=True)
    for n in set(have) - set(want):
        (WIKI / n).unlink()
    for n, text in want.items():
        (WIKI / n).write_text(text, encoding="utf-8", newline="\n")
    print(f"wrote {len(want)} wiki pages")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
