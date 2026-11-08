"""
Writes one documentation page per game adapter, and the games overview, from the adapters themselves.

    python tools/gen_game_pages.py        (from the repository's root)

For every adapter `heat3d_watch.adapters.load()` returns, `docs/game-<adapter id>.md`
gets what the adapter declares - what it records, where from, how to switch it
on, the axes, whether it is played online, what was verified - with its module's
docstring as "How it works" and the statistic keys its code sets. `docs/games.md`
gets the table of all of them. Pages of adapters that no longer exist are
removed. The pages are written from the code, so they say what the code does:
change the adapter, then run this again.

Memory adapters are left out: they come from the player's own profiles, and
none ship with the tools. The adapters are loaded against an empty data folder
of their own, so no profile or setting on this machine reaches the pages.
"""

from __future__ import annotations

import ast
import inspect
import json
import os
import re
import shutil
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"
BLOB = "https://github.com/Holdi601/3DHeat-Watcher/blob/main/"

#: What each kind of source is, in one line, for the overview.
KIND_TEXT = {
    "telemetry": "a UDP port or shared memory the game publishes",
    "gsi": "a game-state integration or local API the game serves",
    "log": "files the game writes while it runs",
    "replay": "replays and demos the game saves",
    "platform": "what Steam or the graphics driver keeps",
    "memory": "the game's memory, read only (single-player)",
}


# ----------------------------------------------------------------------------- Markdown


_URL = re.compile(r"https?://[^\s<>()\[\]`'\"]+")
_EMPHASIS = re.compile(r"(\*\*[^*\n]+\*\*|(?<![\w\\*])\*[A-Za-z][^*\n]*?[A-Za-z.]\*(?![\w*]))")
_LIST = re.compile(r"^([*-]|\d+\.) ")


def _url(m: re.Match[str]) -> str:
    url = m.group(0)
    tail = ""
    while url and url[-1] in ".,;:":
        tail = url[-1] + tail
        url = url[:-1]
    return f"<{url}>{tail}"


def _plain(text: str) -> str:
    """Text outside code spans: what Markdown would take for markup, escaped."""
    # A Windows path's backslash before punctuation (`\<game>`, `"\,"`) would be read as an escape.
    text = re.sub(r"\\(?=[!-/:-@\[-`{-~])", r"\\\\", text)
    out = []
    for i, part in enumerate(_EMPHASIS.split(text)):
        if i % 2 == 0:
            part = part.replace("*", "\\*")
        out.append(part)
    text = "".join(out).replace("<", "&lt;").replace("|", "\\|")
    return _URL.sub(_url, text)


def inline_open(text: str, in_code: bool, *, table: bool = False) -> tuple[str, bool]:
    """
    One line of prose as Markdown: code spans kept, everything else escaped,
    URLs linked. `in_code`: a code span opened on an earlier line of the same
    paragraph is still open. Returns the line and whether a span is open at its end.
    """
    pieces = text.split("`")
    out = []
    code = in_code
    for i, piece in enumerate(pieces):
        if i:
            code = not code
        if code:
            out.append(piece.replace("|", "\\|") if table else piece)
        else:
            out.append(_plain(piece))
    line = "`".join(out)
    if line.startswith(("#", ">", "+ ")) and not in_code:
        line = "\\" + line
    return line, code


def inline(text: str, *, table: bool = False) -> str:
    return inline_open(text, False, table=table)[0]


def _indent(line: str) -> int:
    return len(line) - len(line.lstrip(" "))


def docstring_markdown(doc: str) -> str:
    """
    A module docstring as Markdown.

    The docstrings are written to be read as plain text: paragraphs, `*`/`-`/`1.`
    lists, layouts and examples indented under the text that introduces them,
    a title underlined with dashes, and a short title line with an indented
    paragraph straight under it. Those become paragraphs, lists, fenced code
    blocks and fourth-level headings; nothing is reworded.
    """
    lines = inspect.cleandoc(doc).splitlines()
    out: list[str] = []
    n = len(lines)
    base = 0  # the indent of the current titled block's text (0 outside one)
    ctx = 0  # the indent prose has here: a list item's text, a titled block, or 0
    i = 0
    code_open = False  # a code span runs on from the line before
    while i < n:
        line = lines[i].rstrip()
        if not line.strip():
            out.append("")
            code_open = False
            i += 1
            continue
        ind = _indent(line)
        text = line.strip()
        nxt = lines[i + 1].rstrip() if i + 1 < n else ""
        if base and ind < base:
            base = ctx = 0
        if ctx > base and ind < ctx and not (ind == base and _LIST.match(text)):
            ctx = base
        if ind > ctx:
            # Indented deeper than the text around it: a layout, an example - code.
            block: list[str] = []
            j = i
            while j < n:
                cur = lines[j].rstrip()
                if cur.strip() and _indent(cur) <= ctx:
                    break
                block.append(cur)
                j += 1
            while block and not block[-1].strip():
                block.pop()
                j -= 1
            cut = min(_indent(b) for b in block if b.strip())
            pad = " " * (ctx - base)
            out.append(f"{pad}```text")
            out += [f"{pad}{b[cut:]}" if b.strip() else "" for b in block]
            out.append(f"{pad}```")
            i = j
            continue
        if ind == base and nxt.strip() and re.fullmatch(r"[-=~]{3,}", nxt.strip()) and _indent(nxt) == ind:
            out += [f"#### {inline(text)}", ""]
            i += 2
            continue
        prev_blank = not out or not out[-1].strip()
        if (
            base == 0
            and ind == 0
            and prev_blank
            and nxt.strip()
            and _indent(nxt) >= 4
            and not text.endswith(":")
            and not _LIST.match(text)
            and len(text) < 80
        ):
            # A short title with its text indented straight under it.
            out.append(f"#### {inline(text)}")
            out.append("")
            base = ctx = _indent(nxt)
            i += 1
            continue
        m = _LIST.match(text)
        if m and ind == base and not code_open:
            ctx = ind + len(m.group(0))
            body, code_open = inline_open(text[len(m.group(0)) :], False)
            out.append(m.group(0) + body)
        else:
            body, code_open = inline_open(text, code_open)
            out.append(" " * max(0, ind - base) + body)
        i += 1
    md = "\n".join(out)
    return re.sub(r"\n{3,}", "\n\n", md).strip() + "\n"


# ----------------------------------------------------------------------------- the code


def adapter_modules() -> dict[str, object]:
    """Adapter id -> the module that lists it in `ADAPTERS`."""
    out: dict[str, object] = {}
    for name, module in sorted(sys.modules.items()):
        if not name.startswith("heat3d_watch.adapters.") or module is None:
            continue
        for a in getattr(module, "ADAPTERS", ()) or ():
            out.setdefault(a.id, module)
    return out


def reachable_source(adapter, module) -> str:
    """
    The code that runs for one adapter: its own classes, and the functions and
    helper classes they name - in its module or imported from a sibling adapter
    module - followed name by name. Other adapters' classes are left out, so two
    games in one module do not lend each other their statistics.
    """
    from heat3d_watch.adapters.base import Adapter

    mine = [c for c in type(adapter).__mro__ if c.__module__.startswith("heat3d_watch.adapters.") and c is not Adapter
            and c.__module__ != "heat3d_watch.adapters.base"]
    seen: set[int] = set()
    chunks: list[str] = []
    todo: list[tuple[object, object]] = [(c, sys.modules[c.__module__]) for c in mine]
    while todo:
        obj, home = todo.pop()
        if id(obj) in seen:
            continue
        seen.add(id(obj))
        try:
            src = inspect.getsource(obj)
        except (OSError, TypeError):
            continue
        chunks.append(src)
        for word in set(re.findall(r"\b[A-Za-z_]\w*\b", src)):
            target = getattr(home, word, None)
            if target is None or not (inspect.isfunction(target) or inspect.isclass(target)):
                continue
            where = getattr(target, "__module__", "") or ""
            if not where.startswith("heat3d_watch.adapters.") or where == "heat3d_watch.adapters.base":
                continue
            if inspect.isclass(target) and issubclass(target, Adapter) and target not in mine:
                continue
            todo.append((target, sys.modules[where]))
    if not chunks:
        chunks.append(inspect.getsource(module))
    return "\n".join(chunks)


def _key_texts(node: ast.AST) -> list[str]:
    """The key(s) a `.stat(...)` first argument names: a string, either side of an `if`, an f-string's pattern."""
    if isinstance(node, ast.Constant) and isinstance(node.value, str):
        return [node.value]
    if isinstance(node, ast.IfExp):
        return _key_texts(node.body) + _key_texts(node.orelse)
    if isinstance(node, ast.JoinedStr):
        text = ""
        for v in node.values:
            if isinstance(v, ast.Constant):
                text += str(v.value)
            elif isinstance(v, ast.FormattedValue):
                text += "{" + ast.unparse(v.value) + "}"
        return [text]
    return []


def stat_keys(source: str) -> list[str]:
    """Every statistic key `.stat(...)` is called with by name in `source`."""
    keys: set[str] = set()
    try:
        tree = ast.parse(source)
    except SyntaxError:
        return sorted(k for _, k in re.findall(r"\.stat\(\s*(f?)\"([^\"]+)\"", source))
    for node in ast.walk(tree):
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute) and node.func.attr == "stat" and node.args:
            keys.update(_key_texts(node.args[0]))
    return sorted(keys)


_POSITION = re.compile(r"\.position\(|\.sample\(|\.positions\s*\+=|\bx\s*=\s*(?!None\b)|[\"']x[\"']\s*:|\*\*where\b|\*\*pos\b|row\(\"position\"")


def positions(adapter, source: str) -> str:
    """Whether the adapter records positions: from its axes note and what its code writes."""
    units = adapter.axes.units.strip().lower()
    if units.startswith(("no ", "no:", "none")):
        return "no"
    if "position_at(" in source:
        return "borrowed"
    return "yes" if _POSITION.search(source) else "no"


# ----------------------------------------------------------------------------- the pages


def page_name(adapter) -> str:
    return f"game-{adapter.id}.md"


def title_of(adapter) -> str:
    return f"{adapter.game} ({adapter.kind})"


def runs_when(adapter) -> str:
    if not adapter.exes:
        return "always on (it does not wait for a game to start)"
    names = [f"`{e}`" for e in adapter.exes]
    listed = names[0] if len(names) == 1 else ", ".join(names[:-1]) + " or " + names[-1]
    return f"while {listed} is running"


def multiplayer_text(adapter) -> str:
    kind = adapter.kind
    if kind == "memory":
        return (
            "This adapter reads the game's memory. That is allowed only for a single-player build its profile "
            "lists, with no anti-cheat installed or running, and - for a game that can be played online - only "
            "while the game has no connection out. See [Reading memory](memory-reading.md)."
        )
    flag = "yes" if adapter.multiplayer else "no"
    online = "allowed (reads only what the game publishes)" if adapter.multiplayer else "single-player"
    lines = [
        f"- Marked as played online (`multiplayer`): **{flag}**. `games --markdown` shows this as \"{online}\".",
        f"- Kind `{kind}`: it reads only what the game or platform hands out ({KIND_TEXT.get(kind, kind)}), so it "
        "records in online play as well as offline; the flag decides only whether memory may ever be read.",
        "- Memory: **never** read by this adapter. Only `memory` adapters read memory, and never for a game "
        "marked as played online - see [Sources and rules](sources-and-rules.md).",
    ]
    return "\n".join(lines)


RULE = "https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md"


def completeness_section(adapter) -> list[str]:
    """The converter rule's three lists, from the adapter's `completeness`."""
    c = getattr(adapter, "completeness", None) or {}
    lines = [
        "## Completeness",
        "",
        f"The watcher follows 3DHeat's [converter rule]({RULE}): what the source holds is read or kept, never "
        "dropped. Besides the rows, every packet, page, line or reply the adapter receives is kept whole in the "
        "session's `heat.raw.parquet` (columns `time`, `ms`, `type`, `used`, `payload`, `text`, then any field kept "
        "by name; `used` marks what also became rows), and `meta.json`'s `selfCheck.completeness` counts each "
        "`type` - `lost` is 0.",
        "",
    ]
    if not c:
        return lines + ["The adapter does not list its source's contents yet."]
    for key, head in (("read", "Read"), ("raw", "Kept raw"), ("missing", "Not available")):
        items = c.get(key) or ()
        if isinstance(items, str):
            items = (items,)
        lines.append(f"**{head}**")
        lines.append("")
        lines += [f"- {inline(i)}" for i in items] or ["- nothing"]
        lines.append("")
    if c.get("size"):
        lines += [f"**Size**: {inline(c['size'])}", ""]
    return lines[:-1] if lines[-1] == "" else lines


def game_page(adapter, module, nav: int, siblings: list) -> str:
    source = reachable_source(adapter, module)
    rel = module.__name__.replace(".", "/") + ".py"
    ax = adapter.axes
    flips = [a for a, on in (("x", ax.flip_x), ("y", ax.flip_y), ("z", ax.flip_z)) if on]
    has = positions(adapter, source)
    has_text = {
        "yes": "yes",
        "no": "no",
        "borrowed": "only borrowed: the place another recording of the same game has for that moment",
    }[has]
    parts = [
        "---",
        f"title: {json.dumps(title_of(adapter), ensure_ascii=False)}",
        "parent: Games",
        f"nav_order: {nav}",
        "---",
        "",
        f"# {inline(title_of(adapter))}",
        "",
        f"Adapter `{adapter.id}` - kind [`{adapter.kind}`](sources-and-rules.md) - runs {runs_when(adapter)} - "
        f"looks for new data every {adapter.interval:g} s.",
        "",
        "## What is recorded",
        "",
        *[f"- {inline(r)}" for r in adapter.records],
        "",
        "## Where it comes from",
        "",
        inline(adapter.source) if adapter.source else "Not stated by the adapter.",
        "",
        "## How to switch it on",
        "",
    ]
    if adapter.enable:
        parts.append(inline(adapter.enable))
    else:
        parts.append("Nothing needs switching on: the watcher reads the source as the game or platform provides it.")
    if adapter.can_setup and f"setup {adapter.id}" in adapter.enable:
        parts += [
            "",
            f"`python -m heat3d_watch setup {adapter.id}` lists the files it would change; "
            f"`python -m heat3d_watch setup {adapter.id} --apply` changes them, keeping the original as "
            "`<file>.heat3d-backup` (see [Commands](commands.md#setup)).",
        ]
    parts += ["", "## How it works", ""]
    doc = module.__doc__ or ""
    parts.append(docstring_markdown(doc).rstrip() if doc.strip() else "The module has no description.")
    others = [s for s in siblings if s.id != adapter.id]
    if others:
        links = ", ".join(f"[{inline(title_of(s))}]({page_name(s)})" for s in others)
        parts += ["", f"The same module also serves: {links}."]
    parts += [
        "",
        "## Positions and axes",
        "",
        "| | |",
        "|---|---|",
        f"| Positions recorded | {has_text} |",
        f"| Up axis | `{ax.up}` |",
        f"| Units | {inline(ax.units, table=True)} |",
        f"| Mirrored for the viewer | {', '.join(f'`{f}`' for f in flips) if flips else 'none'} |",
        f"| Unit scale (`scale`: the viewer multiplies positions by it) | {ax.scale:g} |",
        "",
        "These go into each session's `meta.json` (`axes`) and, when the session has positions, into "
        "`heat.parquet`'s footer, so the 3DHeat viewer turns and scales the rows by itself - see "
        "[The data](the-data.md).",
        "",
        "## Multiplayer",
        "",
        multiplayer_text(adapter),
        "",
        "## Statistics recorded",
        "",
    ]
    keys = stat_keys(source)
    if keys:
        parts += [
            "Statistic keys this adapter's code sets by name (each session's `stats` in `meta.json` and the "
            "`stats` table of `watcher.sqlite`):",
            "",
            ", ".join(f"`{k}`" for k in keys),
            "",
            "A key in braces is completed at run time (`score.{team}` is one key per team). Keys the code takes "
            "from a table of the game's fields or from the game's own stat names are not in this list; "
            "\"What is recorded\" above names them.",
        ]
    else:
        parts.append("No statistic key is set by name in the code; \"What is recorded\" above says what is counted.")
    parts += ["", *completeness_section(adapter)]
    parts += [
        "",
        "## Verified",
        "",
        inline(adapter.verified) if adapter.verified else "Nothing is stated.",
        "",
        "## Source",
        "",
        f"[{rel}]({BLOB}{rel})",
        "",
        "*Generated from the adapter by `tools/gen_game_pages.py`; change the adapter and run it again rather "
        "than editing this page.*",
        "",
    ]
    return "\n".join(parts)


def overview(adapters: list, modules: dict[str, object]) -> str:
    rows = []
    for a in adapters:
        has = positions(a, reachable_source(a, modules[a.id]))
        rows.append(f"| [{inline(a.game, table=True)}]({page_name(a)}) | {a.kind} | {has} | {inline(a.source, table=True)} |")
    return "\n".join(
        [
            "---",
            "title: Games",
            "nav_order: 3",
            "has_children: true",
            "---",
            "",
            "# Games",
            "",
            f"The watcher knows {len(adapters)} sources in {len({a.game for a in adapters})} games and platforms. "
            "Each has a page of its own, generated from its adapter: what it records, where from, how to switch "
            "it on, how it works, its axes, what was verified.",
            "",
            "Kinds: `telemetry`, `gsi`, `log`, `replay` and `platform` - see [Sources and rules](sources-and-rules.md). "
            "Positions: *yes* when the adapter writes rows with a place, *borrowed* when it takes the place from "
            "another recording of the same game (see [NVIDIA Highlights](nvidia-highlights.md)), *no* when the "
            "source has none. Memory profiles are not listed: none ship, and each player writes their own "
            "(see [Reading memory](memory-reading.md)).",
            "",
            "| Game | Kind | Positions | Source |",
            "|---|---|---|---|",
            *rows,
            "",
            "Games that are not recorded, and why: [Sources and rules](sources-and-rules.md#what-is-declined-and-why). "
            "Everything in one table, as `python -m heat3d_watch games --markdown` prints it: "
            "[All games in one table](watcher.md).",
            "",
            "*Generated by `tools/gen_game_pages.py`; run it again after changing an adapter.*",
            "",
        ]
    )


def main(only: list[str] | None = None) -> int:
    """
    Every page and the overview; given adapter ids (`python tools/gen_game_pages.py dcs il2`),
    only those pages, leaving every other page and the overview as they are.
    """
    home = tempfile.mkdtemp(prefix="heat3d-docs-")
    # An empty data folder: the player's profiles and settings stay out of the pages.
    os.environ["HEAT3D_WATCH_HOME"] = home
    os.environ.setdefault("HEAT3D_NO_UPDATE", "1")
    if str(ROOT) not in sys.path:
        sys.path.insert(0, str(ROOT))
    try:
        from heat3d_watch.adapters import broken, load

        registry = load()
        if broken:
            for module, why in broken.items():
                print(f"adapter module {module} did not load: {why}", file=sys.stderr)
            print("not writing pages: they would leave those games out", file=sys.stderr)
            return 1
        modules = adapter_modules()
        adapters = sorted(
            (a for a in registry.values() if a.kind != "memory"), key=lambda a: (a.game.lower(), a.id)
        )
        by_module: dict[str, list] = {}
        for a in adapters:
            by_module.setdefault(modules[a.id].__name__, []).append(a)
        DOCS.mkdir(exist_ok=True)
        written = set()
        unknown = sorted(set(only or ()) - {a.id for a in adapters})
        if unknown:
            print(f"no such adapter: {', '.join(unknown)}", file=sys.stderr)
            return 1
        for nav, a in enumerate(adapters, 1):
            if only and a.id not in only:
                continue
            module = modules[a.id]
            path = DOCS / page_name(a)
            path.write_text(game_page(a, module, nav, by_module[module.__name__]), encoding="utf-8", newline="\n")
            written.add(path.name)
        if only:
            print(f"wrote {len(written)} game pages to {DOCS}")
            return 0
        for old in DOCS.glob("game-*.md"):
            if old.name not in written:
                old.unlink()
                print(f"removed {old.name}")
        (DOCS / "games.md").write_text(overview(adapters, modules), encoding="utf-8", newline="\n")
        print(f"wrote games.md and {len(written)} game pages to {DOCS}")
        return 0
    finally:
        shutil.rmtree(home, ignore_errors=True)


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:] or None))
