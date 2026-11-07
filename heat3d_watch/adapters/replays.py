"""
Replays and demos: what a game saves of a match, converted once the match is over.

A replay holds everything a live interface keeps back in multiplayer games -
every player's position, every kill where it happened - and it is a file the
game writes for its players, so reading it touches nothing in the game. The
watcher looks at the folders games save them to, waits until a new file has
stopped growing (the game is still writing it otherwise), and converts it in a
worker thread, so a long conversion never holds up the rest of the watcher.

The first time a folder is seen, the replays already in it are only noted, not
converted: a player with years of demos would otherwise find the watcher busy
for a day. `python -m heat3d_watch replays <adapter> [folder]` converts the
existing ones on request.

Counter-Strike 2
----------------
CS2 saves the demos a player downloads from the match history (watch tab) to
`<CS2>/game/csgo/replays/` and ones recorded with the `record` console command
to `<CS2>/game/csgo/`. Each is converted with this repository's own CS2
converter (3DHeat CS2, github.com/Holdi601/3DHeat-CS2: every player's position, look direction, health and
money every eighth tick; kills, deaths, damage, grenades, plants and defuses
where they happened; rounds, score, economy) into the session folder, as the
`<map>/<match>.parquet` table and `<match>.match.json` summary the viewer's heat
and match tabs read. The match's scoreboard becomes the session's statistics:
for the player whose Steam account is signed in on this machine (from Steam's
`loginusers.vdf`) under its plain names - kills, deaths, assists, ADR, KAST,
headshot percentage, opening kills, clutches - and the score and rounds.

Dota 2
------
Dota 2 saves the replays a player downloads (a match's details, or Watch >
Replays) to `<Dota>/game/dota/replays/<match id>.dem`; Valve keeps every public
match's replay on its servers for a few weeks, and `python -m heat3d_watch
dota-replay <match id>` fetches one by its id through OpenDota. Each is read with
gem (github.com/whanyu1212/gem-dota, MIT, `pip install gem-dota`) in a process
of its own (`heat3d_watch/decoders/dota_replay.py`): every hero's position,
height, health, level, facing, mana, experience, attributes and items 7.5
times a second while alive, kills and deaths where they happened, towers,
barracks, Roshan and Tormentors where they fell, every ward where it was
planted and where it ended, and the combat log's entries about the heroes
(damage, heals, abilities, items, purchases, runes, gold, experience,
modifiers) - into `dota/<match>.parquet`; every other unit (creeps, summons,
illusions, couriers, buildings) once a second into `<match>.units.parquet`;
the whole combat log into `<match>.combatlog.parquet`; and the match, the
chat, the draft and everything else the parser extracts into
`<match>.match.json`, in the session folder. Positions are Dota's world
units, the same the game-state integration reports. The signed-in player's
scoreboard line becomes the session's statistics: kills, deaths, assists,
last hits, denies, net worth, GPM, XPM, hero damage, wards, and whether the
match was won. A new Dota patch can change the replay's entities before gem
follows; a replay gem cannot read to the end is converted as far as it goes
and marked `incomplete` in its summary.

War Thunder
-----------
War Thunder saves a replay of each battle to `<War Thunder>/Replays/*.wrpl`
when replay saving is on in its options. The watcher does not read them
itself: an external converter does (3DHeat War Thunder replay converter,
`exporters/ext/warthunder-replay`, command `heat3d-wt-replay`), kept apart so
that a problem with it touches nothing else. When the command is on PATH, or
the package is installed or beside the watcher, each new replay is run through
it into the session folder as `<map>/<match>.parquet` and `<match>.match.json`;
when it is not, the watcher says once how to install it and leaves the folder
alone. What the converter reads, and what it does not, is in its README. The
replay's author's line of the results - kills, ground kills, deaths, assists,
score, captures - becomes the session's statistics.

World of Tanks and World of Warships
------------------------------------
Both save a replay of each battle to `<game>/replays/` when recording is on
(`*.wotreplay`, `*.wowsreplay`); the installs are found through the Wargaming
Game Center's list, `C:/Games/World_of_Tanks*` / `World_of_Warships*`, and
Steam. As with War Thunder, the watcher does not read the files itself: an
external converter of each does (`exporters/ext/wot-replay`, command
`heat3d-wot-replay`; `exporters/ext/wows-replay`, command
`heat3d-wows-replay`), kept apart so that a problem with Wargaming's terms
touches only that converter. Found on PATH, installed, or beside the watcher,
it turns each new replay into `<map>/<match>.parquet` and `<match>.match.json`
in the session folder; missing, the watcher says once how to install it. The
recording player's line - vehicle or ship, kills, damage (World of Tanks),
whether they survived, and the result (World of Tanks) - becomes the
session's statistics. What each converter reads, and what it does not, is in
its README.

Squad
-----
Squad's dedicated servers record a demo of a match when an admin with the
`demos` permission runs AdminDemoRec <name> (and AdminDemoStop), into
`<server>/SquadGame/Saved/Demos/<name>.replay` - an Unreal Engine network
replay holding what the server replicated, every player's movement included.
The watcher does not read them itself: an external reader does (3DHeat Squad
demo reader, `exporters/ext/squad-demo`, command `heat3d-squad-demo`), kept
apart so that a problem with it touches nothing else. It is run on each new
demo in the folders a local server writes to, or in a folder the settings add
for demos copied off a rented server, into the session folder as
`<map>/<match>.parquet` and `<match>.match.json`. The layer, the map, the
number of players and the match length become the session's statistics.
"""

from __future__ import annotations

import json
import logging
import os
import queue
import re
import subprocess
import sys
import threading
import time
from dataclasses import dataclass, field
from pathlib import Path

from ..session import Axes
from .base import Adapter, Context

log = logging.getLogger("heat3d_watch")

#: How long a new file must keep its size before it counts as written.
SETTLE_SECONDS = 10.0
#: The watcher's own folder: tools it works with are looked for beside it.
ROOT = Path(__file__).resolve().parents[2]


def cs2_tool() -> Path | None:
    """
    The folder of 3DHeat CS2 (github.com/Holdi601/3DHeat-CS2), the converter CS2
    demos go through: `HEAT3D_CS2` when set, else a clone beside the watcher's
    (`3DHeat-CS2` or `cs2`), else wherever Python can import it from.
    """
    import importlib.util

    candidates = [Path(os.environ["HEAT3D_CS2"])] if os.environ.get("HEAT3D_CS2") else []
    candidates += [ROOT.parent / "3DHeat-CS2", ROOT.parent / "cs2"]
    for c in candidates:
        if (c / "heat3d_cs2" / "__init__.py").is_file():
            return c
    spec = importlib.util.find_spec("heat3d_cs2")
    if spec is not None and spec.origin:
        return Path(spec.origin).resolve().parents[1]
    return None


def steam_root() -> Path | None:
    """Steam's own folder, from the registry or the usual place."""
    if os.name == "nt":
        try:
            import winreg

            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Valve\Steam") as k:
                path = Path(winreg.QueryValueEx(k, "SteamPath")[0])
                if path.is_dir():
                    return path
        except OSError:
            pass
    for p in (Path(r"C:\Program Files (x86)\Steam"), Path.home() / ".steam" / "steam"):
        if p.is_dir():
            return p
    return None


def steam_libraries() -> list[Path]:
    """Every Steam library's `steamapps/common`, from `libraryfolders.vdf`."""
    root = steam_root()
    if root is None:
        return []
    found = [root]
    vdf = root / "steamapps" / "libraryfolders.vdf"
    try:
        text = vdf.read_text(encoding="utf-8", errors="replace")
        found += [Path(m.replace("\\\\", "\\")) for m in re.findall(r'"path"\s+"([^"]+)"', text)]
    except OSError:
        pass
    out, seen = [], set()
    for lib in found:
        common = lib / "steamapps" / "common"
        key = str(common).lower()
        if key not in seen and common.is_dir():
            seen.add(key)
            out.append(common)
    return out


def signed_in_steam_ids() -> set[str]:
    """The 64-bit ids of the Steam accounts signed in on this machine (`loginusers.vdf`)."""
    root = steam_root()
    if root is None:
        return set()
    try:
        text = (root / "config" / "loginusers.vdf").read_text(encoding="utf-8", errors="replace")
    except OSError:
        return set()
    return set(re.findall(r'"(7656\d{13})"', text))


@dataclass
class ReplayAdapter(Adapter):
    """A folder of replays, watched; each new one converted into a session."""

    kind: str = "replay"
    interval: float = 5.0
    #: File name patterns of this game's replays.
    patterns: tuple[str, ...] = ()
    _seen: dict[str, list[float]] = field(default_factory=dict)
    _pending: dict[str, tuple[float, float]] = field(default_factory=dict)
    _queue: "queue.Queue[Path]" = field(default_factory=queue.Queue)
    _worker: threading.Thread | None = None
    _halt: threading.Event = field(default_factory=threading.Event)

    def folders(self, ctx: Context) -> list[Path]:
        """Where this game saves replays, plus the folders the settings add."""
        return [Path(p) for p in ctx.settings.replay_folders.get(self.id, [])]

    def convert(self, path: Path, ctx: Context) -> None:
        """Turn one replay into a session. Runs in the worker thread."""
        raise NotImplementedError

    # -- the folder watch, shared by every game ---------------------------------

    def _state_path(self, ctx: Context) -> Path:
        return ctx.data / "state" / f"replays-{self.id}.json"

    def _files(self, ctx: Context) -> list[Path]:
        out: list[Path] = []
        for folder in self.folders(ctx):
            if not folder.is_dir():
                continue
            for pattern in self.patterns:
                out += [p for p in folder.glob(pattern) if p.is_file()]
        return out

    def start(self, ctx: Context) -> None:
        path = self._state_path(ctx)
        first = not path.exists()
        try:
            self._seen = json.loads(path.read_text(encoding="utf-8")) if not first else {}
        except (OSError, ValueError):
            self._seen = {}
        if first:
            # Only note what is already there; see the module docstring.
            for f in self._files(ctx):
                st = f.stat()
                self._seen[str(f)] = [st.st_size, st.st_mtime]
            self._save(ctx)
        self._halt.clear()
        self._worker = threading.Thread(target=self._work, args=(ctx,), name=f"convert-{self.id}", daemon=True)
        self._worker.start()

    def poll(self, ctx: Context) -> None:
        now = time.time()
        for f in self._files(ctx):
            key = str(f)
            try:
                st = f.stat()
            except OSError:
                continue
            if self._seen.get(key) == [st.st_size, st.st_mtime]:
                continue
            last = self._pending.get(key)
            if last is None or last[0] != st.st_size:
                self._pending[key] = (st.st_size, now)
                continue
            if now - last[1] < SETTLE_SECONDS:
                continue
            del self._pending[key]
            self._seen[key] = [st.st_size, st.st_mtime]
            self._save(ctx)
            self._queue.put(f)

    def _work(self, ctx: Context) -> None:
        while not self._halt.is_set():
            try:
                f = self._queue.get(timeout=0.5)
            except queue.Empty:
                continue
            try:
                log.info("%s: converting %s", self.id, f.name)
                self.convert(f, ctx)
            except Exception:  # noqa: BLE001 - one bad replay does not stop the next
                log.exception("%s: could not convert %s", self.id, f.name)

    def _save(self, ctx: Context) -> None:
        p = self._state_path(ctx)
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(json.dumps(self._seen), encoding="utf-8")

    def stop(self, ctx: Context) -> None:
        self._halt.set()
        if self._worker is not None:
            self._worker.join(5)

    def convert_existing(self, ctx: Context, folder: Path | None = None) -> int:
        """
        Convert every replay in the folders (or `folder`) now, in this thread -
        `python -m heat3d_watch replays <adapter> [folder]`. Each one converted
        is noted as seen, so the folder watch does not convert it a second
        time. Returns how many were converted.
        """
        files = (
            [p for pat in self.patterns for p in folder.glob(pat) if p.is_file()]
            if folder is not None else self._files(ctx)
        )
        try:
            seen = json.loads(self._state_path(ctx).read_text(encoding="utf-8"))
        except (OSError, ValueError):
            seen = {}
        if not self._state_path(ctx).exists():
            # The folder watch's first look, taken now: what is there counts as noted, as in `start`.
            for f in self._files(ctx):
                st = f.stat()
                seen[str(f)] = [st.st_size, st.st_mtime]
        done = 0
        for f in sorted(set(files)):
            try:
                log.info("%s: converting %s", self.id, f.name)
                self.convert(f, ctx)
            except Exception:  # noqa: BLE001 - one bad replay does not stop the next
                log.exception("%s: could not convert %s", self.id, f.name)
                continue
            st = f.stat()
            seen[str(f)] = [st.st_size, st.st_mtime]
            done += 1
        self._seen = seen
        self._save(ctx)
        return done


@dataclass
class Cs2Demos(ReplayAdapter):
    def folders(self, ctx: Context) -> list[Path]:
        out = []
        for common in steam_libraries():
            csgo = common / "Counter-Strike Global Offensive" / "game" / "csgo"
            if csgo.is_dir():
                out += [csgo / "replays", csgo]
        return out + super().folders(ctx)

    def missing(self) -> str | None:
        try:
            import demoparser2  # noqa: F401
        except ImportError:
            return "install 3DHeat CS2 and its requirements (github.com/Holdi601/3DHeat-CS2)"
        if cs2_tool() is None:
            return "3DHeat CS2 not found: clone github.com/Holdi601/3DHeat-CS2 beside the watcher, or set HEAT3D_CS2"
        return None

    def convert(self, path: Path, ctx: Context) -> None:
        when = path.stat().st_mtime
        session = ctx.open(self, when=when, meta={"replay": str(path)})
        try:
            out = subprocess.run(
                [sys.executable, "-m", "heat3d_cs2", "demos", str(path), "-o", str(session.folder), "--jobs", "1"],
                cwd=cs2_tool(),
                capture_output=True,
                text=True,
                timeout=3600,
                env={**os.environ, "HEAT3D_NO_UPDATE": "1"},
            )
            session.meta["converter"] = (out.stdout + out.stderr).strip()[-2000:]
            summaries = sorted(session.folder.glob("*/*.match.json"))
            if out.returncode != 0 or not summaries:
                session.event("replay_failed", file=path.name)
                return
            record_match(session, json.loads(summaries[0].read_text(encoding="utf-8")), signed_in_steam_ids())
            tables = sorted(session.folder.glob("*/*.parquet"))
            if tables:
                count_events(session, tables[0])
        finally:
            ctx.close(session)


def record_match(session, match: dict, me: set[str]) -> None:
    """A CS2 match summary into the session: what happened, the score, and the signed-in player's line."""
    session.meta["match"] = {k: match.get(k) for k in ("match", "map", "teams", "score")}
    session.stat("map", str(match.get("map") or ""))
    session.stat("rounds", len(match.get("rounds") or []))
    for team, score in (match.get("score") or {}).items():
        session.stat(f"score.{team}", score)
    for p in match.get("players") or []:
        if str(p.get("steamid")) not in me:
            continue
        session.meta["player"] = p.get("name")
        for key, name in (
            ("kills", "kills"),
            ("deaths", "deaths"),
            ("assists", "assists"),
            ("adr", "adr"),
            ("kast", "kast"),
            ("headshotPct", "headshot_pct"),
            ("openingKills", "opening_kills"),
            ("openingDeaths", "opening_deaths"),
            ("tradeKills", "trade_kills"),
            ("clutchesWon", "clutches_won"),
            ("utilityDamage", "utility_damage"),
            ("enemiesFlashed", "enemies_flashed"),
            ("plants", "plants"),
            ("defuses", "defuses"),
            ("roundsPlayed", "rounds_played"),
        ):
            value = p.get(key)
            if isinstance(value, (int, float)):
                session.stat(name, value)
        won = None
        for team, score in (match.get("score") or {}).items():
            if team == p.get("team"):
                others = [s for t, s in (match.get("score") or {}).items() if t != team]
                won = bool(others) and score > max(others)
        if won is not None:
            session.stat("won", 1 if won else 0)


def count_events(session, table: Path) -> None:
    """The converter's table's events, counted for the statistics without copying its rows."""
    import pyarrow.parquet as pq

    events = pq.read_table(table, columns=["event"]).column("event").to_pylist()
    counts: dict[str, int] = {}
    for e in events:
        counts[str(e)] = counts.get(str(e), 0) + 1
    with session._lock:
        for e, n in counts.items():
            session.counts[e] = session.counts.get(e, 0) + n
        session.positions += len(events)


def dota_replay_folders() -> list[Path]:
    """`<Dota>/game/dota/replays` in every Steam library Dota 2 is installed in."""
    out = []
    for common in steam_libraries():
        game = common / "dota 2 beta" / "game" / "dota"
        if game.is_dir():
            out.append(game / "replays")
    return out


@dataclass
class DotaReplays(ReplayAdapter):
    def folders(self, ctx: Context) -> list[Path]:
        return dota_replay_folders() + super().folders(ctx)

    def missing(self) -> str | None:
        try:
            import gem  # noqa: F401
        except ImportError:
            return "pip install gem-dota (the Dota 2 replay parser, MIT)"
        return None

    def convert(self, path: Path, ctx: Context) -> None:
        session = ctx.open(self, when=path.stat().st_mtime, meta={"replay": str(path)})
        try:
            # A process of its own: a long match's parse takes several hundred megabytes, given back when it ends.
            out = subprocess.run(
                [sys.executable, "-m", "heat3d_watch.decoders.dota_replay", str(path), "-o", str(session.folder / "dota")],
                cwd=ROOT,
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                timeout=3600,
                env={**os.environ, "HEAT3D_NO_UPDATE": "1", "PYTHONIOENCODING": "utf-8"},
            )
            session.meta["converter"] = (out.stdout + out.stderr).strip()[-2000:]
            summaries = sorted((session.folder / "dota").glob("*.match.json"))
            if out.returncode != 0 or not summaries:
                session.event("replay_failed", file=path.name)
                return
            record_dota_match(session, json.loads(summaries[0].read_text(encoding="utf-8")), signed_in_steam_ids())
            # The match's own table, not its units' or its combat log's (`<match>.units.parquet`, ...).
            tables = sorted(t for t in (session.folder / "dota").glob("*.parquet") if t.name.count(".") == 1)
            if tables:
                count_events(session, tables[0])
        finally:
            ctx.close(session)


def record_dota_match(session, match: dict, me: set[str]) -> None:
    """A Dota 2 match summary into the session: the result, and the signed-in player's line."""
    session.meta["match"] = {k: match.get(k) for k in ("match", "winner", "score", "teams", "duration")}
    if isinstance(match.get("duration"), (int, float)):
        session.stat("duration", match["duration"])
    for team, score in (match.get("score") or {}).items():
        session.stat(f"score.{team}", score)
    for p in match.get("players") or []:
        if str(p.get("steamid")) not in me:
            continue
        session.meta["player"] = p.get("name")
        session.stat("hero", str(p.get("heroName") or p.get("hero") or ""))
        session.stat("team", str(p.get("team") or ""))
        for key, name in (
            ("kills", "kills"),
            ("deaths", "deaths"),
            ("assists", "assists"),
            ("level", "level"),
            ("lastHits", "last_hits"),
            ("denies", "denies"),
            ("netWorth", "net_worth"),
            ("goldPerMin", "gpm"),
            ("xpPerMin", "xpm"),
            ("heroDamage", "hero_damage"),
            ("towerDamage", "tower_damage"),
            ("heroHealing", "hero_healing"),
            ("observersPlaced", "observers_placed"),
            ("sentriesPlaced", "sentries_placed"),
            ("campsStacked", "camps_stacked"),
        ):
            value = p.get(key)
            if isinstance(value, (int, float)) and not isinstance(value, bool):
                session.stat(name, value)
        if match.get("winner"):
            session.stat("won", 1 if match["winner"] == p.get("team") else 0)


#: Seconds from 0001-01-01 (the start of .NET's ticks) to the Unix epoch.
_TICKS_TO_UNIX = 62135596800


def _osr_string(buf: bytes, at: int) -> tuple[str, int]:
    """An .osr string: 0x00 for none, or 0x0b, a ULEB128 length and that many UTF-8 bytes."""
    kind = buf[at]
    at += 1
    if kind == 0x00:
        return "", at
    if kind != 0x0B:
        raise ValueError(f"not an osu! string at {at - 1}")
    length = shift = 0
    while True:
        b = buf[at]
        at += 1
        length |= (b & 0x7F) << shift
        shift += 7
        if not b & 0x80:
            break
    return buf[at : at + length].decode("utf-8", errors="replace"), at + length


def parse_osr(buf: bytes) -> dict:
    """
    An osu! replay (.osr), per the file format on the osu! wiki
    (https://osu.ppy.sh/wiki/en/Client/File_formats/osr_(file_format)):
    the header, and the cursor frames - milliseconds since the previous frame,
    x 0..512, y 0..384 on the playfield, and the keys held.
    """
    import lzma
    import struct as st

    at = 0
    mode, version = st.unpack_from("<Bi", buf, at)
    at += 5
    beatmap, at = _osr_string(buf, at)
    player, at = _osr_string(buf, at)
    _replay_hash, at = _osr_string(buf, at)
    n300, n100, n50, geki, katu, miss = st.unpack_from("<6h", buf, at)
    at += 12
    score, combo, perfect, mods = st.unpack_from("<ihBi", buf, at)
    at += 11
    _life, at = _osr_string(buf, at)
    ticks, length = st.unpack_from("<qi", buf, at)
    at += 12
    data = lzma.decompress(buf[at : at + length]) if length > 0 else b""
    frames = []
    t = 0
    for part in data.decode("ascii", errors="replace").split(","):
        fields = part.split("|")
        if len(fields) != 4:
            continue
        w, x, y, z = fields
        if w == "-12345":
            continue  # the RNG seed, not a frame
        t += int(w)
        frames.append((t, float(x), float(y), int(float(z))))
    hits = n300 + n100 + n50 + miss
    return {
        "mode": mode,
        "version": version,
        "beatmap": beatmap,
        "player": player,
        "count_300": n300,
        "count_100": n100,
        "count_50": n50,
        "count_geki": geki,
        "count_katu": katu,
        "misses": miss,
        "score": score,
        "max_combo": combo,
        "perfect": perfect,
        "mods": mods,
        "played_at": ticks / 1e7 - _TICKS_TO_UNIX if ticks > 0 else None,
        # Standard mode's accuracy; the other modes weigh their judgements differently.
        "accuracy": (300 * n300 + 100 * n100 + 50 * n50) / (300 * hits) if mode == 0 and hits else None,
        "frames": frames,
    }


@dataclass
class OsuReplays(ReplayAdapter):
    def folders(self, ctx: Context) -> list[Path]:
        base = Path(os.environ.get("LOCALAPPDATA", "")) / "osu!"
        return [base / "Data" / "r", base / "Replays"] + super().folders(ctx)

    def convert(self, path: Path, ctx: Context) -> None:
        r = parse_osr(path.read_bytes())
        session = ctx.open(self, when=r["played_at"] or path.stat().st_mtime, meta={"replay": str(path)})
        try:
            play = r["beatmap"] or path.stem
            frames = r["frames"]
            # The playfield drawn on the ground: x across, its y away from the viewer.
            for i, (t, x, y, keys) in enumerate(frames):
                event = "session_start" if i == 0 else "finish" if i == len(frames) - 1 else "position"
                session.event(event, t=t / 1000.0, x=x, y=0.0, z=y, player=r["player"] or "me", session=play, keys=keys)
            for key in ("score", "max_combo", "count_300", "count_100", "count_50", "misses", "mode", "mods"):
                session.stat(key, r[key])
            if r["accuracy"] is not None:
                session.stat("accuracy", round(r["accuracy"], 5))
            session.stat("full_combo", 1 if r["perfect"] else 0)
        finally:
            ctx.close(session)


ADAPTERS = [
    Cs2Demos(
        id="cs2-demos",
        game="Counter-Strike 2",
        patterns=("*.dem",),
        source="demos CS2 saves: <CS2>/game/csgo/replays/*.dem (downloaded from the match history) and <CS2>/game/csgo/*.dem (recorded)",
        records=(
            "every player's position, look direction, health and money (every 8th tick)",
            "kills, deaths, damage, grenades, plants and defuses where they happened",
            "rounds, score, economy; the signed-in player's scoreboard line as statistics",
        ),
        enable="download a match's demo in CS2 (Watch > Your Matches), or record one with the console's `record`",
        # As the converter's own tables say in their footer, and the CS2 game-state adapter: Source units, scale 1.
        axes=Axes(up="z", flip_y=True, units="inches (Source units)"),
        verified="the converter is tested on 165 real tournament demos; the folder watch and statistics by tests",
        multiplayer=True,
    ),
    DotaReplays(
        id="dota-replays",
        game="Dota 2",
        patterns=("*.dem",),
        source="replays Dota 2 saves: <Dota>/game/dota/replays/<match id>.dem (downloaded in the client, or with `dota-replay <match id>`)",
        records=(
            "every hero's position, height, health and level, 7.5 times a second while alive",
            "kills and deaths where they happened; towers, barracks, Roshan and Tormentors where they fell; wards where they were planted",
            "the score and every player's line; the signed-in player's as statistics",
        ),
        enable="download a match's replay in Dota 2, or fetch a public one: `python -m heat3d_watch dota-replay <match id>`; needs `pip install gem-dota`",
        # As the converter's table says in its footer, and the Dota game-state adapter: Source 2 world units.
        axes=Axes(up="z", flip_y=True, units="Dota world units (Hammer units; the map is about 16400 across)"),
        verified="checked on a public match's replay (patch 7.40, November 2026): kills and deaths per hero match the scoreboard; the table and statistics by tests on synthetic data",
        multiplayer=True,
    ),
    OsuReplays(
        id="osu-replays",
        game="osu!",
        patterns=("*.osr",),
        source="replays osu! (stable) saves: %LOCALAPPDATA%/osu!/Data/r/*.osr (every play) and osu!/Replays/*.osr (exported)",
        records=(
            "the cursor's path over the playfield (x 0..512, y 0..384) and the keys held, every frame",
            "score, combo, 300s/100s/50s/misses, accuracy, mods, full combo",
        ),
        axes=Axes(up="y", flip_z=True, units="osu! pixels (playfield 512 x 384)"),
        verified="tested on replays built to the published .osr format; osu!lazer keeps replays in its own store and is not read",
        multiplayer=True,
    ),
]


# -- War Thunder: an external converter, run as a command -----------------------

#: The command the War Thunder replay converter installs.
WT_COMMAND = "heat3d-wt-replay"
WT_INSTALL = (
    "the War Thunder replay converter is not installed: "
    "pip install -e <3DHeat>/exporters/ext/warthunder-replay (it installs the `heat3d-wt-replay` command)"
)


def wt_converter() -> list[str] | None:
    """
    How to run the War Thunder replay converter, an extension kept outside the
    watcher (exporters/ext/warthunder-replay): its `heat3d-wt-replay` command
    when it is on PATH, else `python -m heat3d_ext_warthunder` when the package
    is installed, or found in `HEAT3D_WT_REPLAY` or beside the watcher
    (`ext/warthunder-replay`). None when it is nowhere. Nothing of it is
    imported here; it is only run.
    """
    import importlib.util
    import shutil

    found = shutil.which(WT_COMMAND)
    if found:
        return [found]
    candidates = [Path(os.environ["HEAT3D_WT_REPLAY"])] if os.environ.get("HEAT3D_WT_REPLAY") else []
    candidates += [ROOT.parent / "ext" / "warthunder-replay", ROOT.parent / "3DHeat-WarThunder-Replay"]
    for c in candidates:
        if (c / "heat3d_ext_warthunder" / "__init__.py").is_file():
            return [sys.executable, "-m", "heat3d_ext_warthunder"]
    if importlib.util.find_spec("heat3d_ext_warthunder") is not None:
        return [sys.executable, "-m", "heat3d_ext_warthunder"]
    return None


def wt_folder() -> Path | None:
    """The folder the converter runs in, when it is a source folder rather than installed."""
    candidates = [Path(os.environ["HEAT3D_WT_REPLAY"])] if os.environ.get("HEAT3D_WT_REPLAY") else []
    candidates += [ROOT.parent / "ext" / "warthunder-replay", ROOT.parent / "3DHeat-WarThunder-Replay"]
    return next((c for c in candidates if (c / "heat3d_ext_warthunder" / "__init__.py").is_file()), None)


def war_thunder_folders() -> list[Path]:
    """Where War Thunder saves client replays: `<game>/Replays`, in Steam's libraries or the launcher's install."""
    out = [common / "War Thunder" / "Replays" for common in steam_libraries()]
    local = os.environ.get("LOCALAPPDATA")
    if local:
        out.append(Path(local) / "WarThunder" / "Replays")
    return out


@dataclass
class WarThunderReplays(ReplayAdapter):
    """
    War Thunder's .wrpl replays, converted by the external converter
    (exporters/ext/warthunder-replay, `heat3d-wt-replay`) into the session
    folder as `<map>/<match>.parquet` and `.match.json`. The watcher only runs
    the command: reading the replay format lives in the converter alone.
    """

    _said: bool = False

    def folders(self, ctx: Context) -> list[Path]:
        return war_thunder_folders() + super().folders(ctx)

    def missing(self) -> str | None:
        if wt_converter() is None:
            if not self._said:
                log.info("%s: %s", self.id, WT_INSTALL)
                self._said = True
            return WT_INSTALL
        return None

    def convert(self, path: Path, ctx: Context) -> None:
        command = wt_converter()
        if command is None:
            log.warning("%s: %s", self.id, WT_INSTALL)
            return
        session = ctx.open(self, when=path.stat().st_mtime, meta={"replay": str(path)})
        try:
            out = subprocess.run(
                [*command, str(path), "-o", str(session.folder)],
                cwd=wt_folder(),
                capture_output=True,
                text=True,
                timeout=3600,
            )
            session.meta["converter"] = (out.stdout + out.stderr).strip()[-2000:]
            summaries = sorted(session.folder.glob("*/*.match.json"))
            if out.returncode != 0 or not summaries:
                session.event("replay_failed", file=path.name)
                return
            record_wt_match(session, json.loads(summaries[0].read_text(encoding="utf-8")))
            tables = sorted(session.folder.glob("*/*.parquet"))
            if tables:
                count_events(session, tables[0])
        finally:
            ctx.close(session)


def record_wt_match(session, match: dict) -> None:
    """A War Thunder match summary into the session: the battle, and the replay's author's line."""
    session.meta["match"] = {k: match.get(k) for k in ("match", "map", "mission", "battleClass", "teams")}
    session.stat("map", str(match.get("map") or ""))
    counts = match.get("counts") or {}
    for key in ("aircraftUids", "groundUids", "aircraftSamples", "groundSamples"):
        if isinstance(counts.get(key), (int, float)):
            session.stat(key, counts[key])
    author = str(match.get("authorUserId") or "")
    for p in match.get("players") or []:
        if not author or str(p.get("userId")) != author:
            continue
        session.meta["player"] = p.get("name")
        for key, name in (("kills", "kills"), ("groundKills", "ground_kills"), ("deaths", "deaths"),
                          ("assists", "assists"), ("score", "score"), ("captureZone", "captures")):
            if isinstance(p.get(key), (int, float)):
                session.stat(name, p[key])


ADAPTERS.append(
    WarThunderReplays(
        id="warthunder-replays",
        game="War Thunder",
        patterns=("*.wrpl",),
        source="replays War Thunder saves: <War Thunder>/Replays/*.wrpl (with replay saving on), converted by the "
        "external converter `heat3d-wt-replay` (exporters/ext/warthunder-replay)",
        records=(
            "every aircraft's position and attitude about 4 times a second (as many as the replay holds)",
            "ground units' positions from the replay's ground sync (in 2026 replays; not in 2025 ones)",
            "who each unit was (player, vehicle id, team) where a kill or hit names it; kills, deaths and hits "
            "where they happened; chat; the map",
            "the replay author's kills, deaths, score and captures as statistics",
        ),
        enable="turn on saving replays in War Thunder's options and install the converter: "
        "pip install -e <3DHeat>/exporters/ext/warthunder-replay",
        # The converter's table: the game's metres, x east, y up, z north; z mirrored for the viewer.
        axes=Axes(up="y", flip_z=True, units="metres (x east, y up, z north)"),
        verified="the converter is checked on public replays from 2025 (an air battle: 30 aircraft, 4 per second, "
        "kills and names agree with the results) and by tests on built replays; this hook by tests with a "
        "stand-in command",
        multiplayer=True,
    )
)


# -- World of Tanks and World of Warships: external converters, run as commands --


def wargaming_installs(exe: str, steam_name: str, prefix: str) -> list[Path]:
    """
    Where a Wargaming game is installed: what the Wargaming Game Center lists
    (`%PROGRAMDATA%/Wargaming.net/GameCenter/preferences.xml`, its
    `working_dir`s), the usual `C:/Games/<prefix>*`, and Steam's libraries.
    Only folders with the game's `exe` in them count.
    """
    found: list[Path] = []
    prefs = Path(os.environ.get("PROGRAMDATA", r"C:\ProgramData")) / "Wargaming.net" / "GameCenter" / "preferences.xml"
    try:
        text = prefs.read_text(encoding="utf-8", errors="replace")
        found += [Path(p.strip()) for p in re.findall(r"<working_dir>([^<]+)</working_dir>", text)]
    except OSError:
        pass
    games = Path(os.environ.get("SystemDrive", "C:") + os.sep) / "Games"
    if games.is_dir():
        found += sorted(games.glob(f"{prefix}*"))
    found += [common / steam_name for common in steam_libraries()]
    out, seen = [], set()
    for f in found:
        key = str(f).lower()
        if key not in seen and (f / exe).is_file():
            seen.add(key)
            out.append(f)
    return out


@dataclass
class WargamingReplays(ReplayAdapter):
    """
    World of Tanks' and World of Warships' replays, converted by an external
    converter of each (exporters/ext/wot-replay, `heat3d-wot-replay`;
    exporters/ext/wows-replay, `heat3d-wows-replay`) into the session folder as
    `<map>/<match>.parquet` and `.match.json`. The watcher only runs the
    command: reading the replay format lives in the converter alone, so a
    problem with one touches nothing else.
    """

    #: The converter's command, its Python package, and its folder beside the watcher (`ext/<folder>`).
    command: str = ""
    module: str = ""
    ext_folder: str = ""
    #: An environment variable that may name the converter's source folder.
    env: str = ""
    #: The game's executable and Steam folder name, and the start of its folder under C:/Games.
    game_exe: str = ""
    steam_name: str = ""
    games_prefix: str = ""
    _said: bool = False

    @property
    def install(self) -> str:
        return (f"the {self.game} replay converter is not installed: pip install -e "
                f"<3DHeat>/exporters/ext/{self.ext_folder} (it installs the `{self.command}` command)")

    def source_folder(self) -> Path | None:
        """The converter's source folder, when it is one rather than installed: `env`, or beside the watcher."""
        candidates = [Path(os.environ[self.env])] if self.env and os.environ.get(self.env) else []
        candidates.append(ROOT.parent / "ext" / self.ext_folder)
        return next((c for c in candidates if (c / self.module / "__init__.py").is_file()), None)

    def converter(self) -> list[str] | None:
        """
        How to run the converter: its command when it is on PATH, else
        `python -m <module>` when it is installed or its source folder is
        found. None when it is nowhere. Nothing of it is imported here.
        """
        import importlib.util
        import shutil

        found = shutil.which(self.command)
        if found:
            return [found]
        if self.source_folder() is not None or importlib.util.find_spec(self.module) is not None:
            return [sys.executable, "-m", self.module]
        return None

    def folders(self, ctx: Context) -> list[Path]:
        installs = wargaming_installs(self.game_exe, self.steam_name, self.games_prefix)
        return [f / "replays" for f in installs] + super().folders(ctx)

    def missing(self) -> str | None:
        if self.converter() is None:
            if not self._said:
                log.info("%s: %s", self.id, self.install)
                self._said = True
            return self.install
        return None

    def convert(self, path: Path, ctx: Context) -> None:
        command = self.converter()
        if command is None:
            log.warning("%s: %s", self.id, self.install)
            return
        session = ctx.open(self, when=path.stat().st_mtime, meta={"replay": str(path)})
        try:
            out = subprocess.run(
                [*command, str(path), "-o", str(session.folder)],
                cwd=self.source_folder(),
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                timeout=3600,
                env={**os.environ, "PYTHONIOENCODING": "utf-8"},
            )
            session.meta["converter"] = (out.stdout + out.stderr).strip()[-2000:]
            summaries = sorted(session.folder.glob("*/*.match.json"))
            if out.returncode != 0 or not summaries:
                session.event("replay_failed", file=path.name)
                return
            record_wargaming_match(session, json.loads(summaries[0].read_text(encoding="utf-8")))
            tables = sorted(session.folder.glob("*/*.parquet"))
            if tables:
                count_events(session, tables[0])
        finally:
            ctx.close(session)


def record_wargaming_match(session, match: dict) -> None:
    """A World of Tanks or Warships match summary into the session: the battle, and the recording player's line."""
    session.meta["match"] = {k: match.get(k) for k in ("match", "map", "mapName", "clientVersion", "recorded")}
    session.stat("map", str(match.get("mapName") or match.get("map") or ""))
    for key in ("duration", "hz"):
        if isinstance(match.get(key), (int, float)):
            session.stat(key, match[key])
    for p in match.get("players") or []:
        if not p.get("own"):
            continue
        session.meta["player"] = p.get("name")
        session.stat("vehicle", str(match.get("vehicle") or p.get("vehicle") or ""))
        for key, name in (("kills", "kills"), ("damageDealt", "damage")):
            if isinstance(p.get(key), (int, float)) and not isinstance(p.get(key), bool):
                session.stat(name, p[key])
        if isinstance(p.get("survived"), bool):
            session.stat("survived", 1 if p["survived"] else 0)
        if match.get("winnerTeam") is not None and p.get("team") is not None:
            session.stat("won", 1 if match["winnerTeam"] == p["team"] else 0)


ADAPTERS += [
    WargamingReplays(
        id="wot-replays",
        game="World of Tanks",
        patterns=("*.wotreplay",),
        command="heat3d-wot-replay",
        module="heat3d_ext_wot",
        ext_folder="wot-replay",
        env="HEAT3D_WOT_REPLAY",
        game_exe="WorldOfTanks.exe",
        steam_name="World of Tanks",
        games_prefix="World_of_Tanks",
        source="replays World of Tanks saves: <World of Tanks>/replays/*.wotreplay (with battle recording on), "
        "converted by the external converter `heat3d-wot-replay` (exporters/ext/wot-replay)",
        records=(
            "every vehicle's position and heading about 10 times a second while the recording client knew of it: "
            "its own team throughout, an enemy while spotted",
            "player, team and vehicle (nation:tank) of each; deaths where the victim fell and kills where the "
            "killer stood, to about a second, from the results",
            "the map; the recording player's kills, damage, survival and the result as statistics",
        ),
        enable="turn on battle recording in World of Tanks' settings (General > Record battles) and install the "
        "converter: pip install -e <3DHeat>/exporters/ext/wot-replay",
        axes=Axes(up="y", flip_z=True, units="metres (x east, y up, z north)"),
        verified="the converter is checked on public replays of 1.12.0 (2021) and 2.4.1 (2026) and by tests on "
        "built replays; this hook by tests with a stand-in command",
        multiplayer=True,
    ),
    WargamingReplays(
        id="wows-replays",
        game="World of Warships",
        patterns=("*.wowsreplay",),
        command="heat3d-wows-replay",
        module="heat3d_ext_wows",
        ext_folder="wows-replay",
        env="HEAT3D_WOWS_REPLAY",
        game_exe="WorldOfWarships.exe",
        steam_name="World of Warships",
        games_prefix="World_of_Warships",
        source="replays World of Warships saves: <World of Warships>/replays/*.wowsreplay (with replays on), "
        "converted by the external converter `heat3d-wows-replay` (exporters/ext/wows-replay)",
        records=(
            "every ship's position and heading while the recording client saw it (about 6 to 7 times a second "
            "while moving), the player's own ship throughout",
            "player, ally or enemy, and ship (the recording player's by name, the others by the game's ship "
            "number); ships sunk where they sank and their killers where they stood",
            "the map; the recording player's ship, kills and survival as statistics",
        ),
        enable="turn on replay recording in World of Warships (`isReplayEnabled` in its preferences.xml, or "
        "the game's own setting where it has one) and install the converter: "
        "pip install -e <3DHeat>/exporters/ext/wows-replay",
        axes=Axes(up="y", flip_z=True, units="World of Warships world units (x east, y up, z north; one is 15 m "
                  "by hull geometry, 30 m by the game's ranges)"),
        verified="the converter is checked on public replays of 0.9.6 (2020), 0.10.11, 15.9 and 15.10 (2026) "
        "and by tests on built replays; this hook by tests with a stand-in command",
        multiplayer=True,
    ),
]


# -- Squad: server demos, read by an external converter run as a command --

#: The command the Squad demo reader installs.
SQUAD_COMMAND = "heat3d-squad-demo"
SQUAD_INSTALL = (
    "the Squad demo reader is not installed: "
    "pip install -e <3DHeat>/exporters/ext/squad-demo (it installs the `heat3d-squad-demo` command)"
)


def _squad_sources() -> list[Path]:
    candidates = [Path(os.environ["HEAT3D_SQUAD_DEMO"])] if os.environ.get("HEAT3D_SQUAD_DEMO") else []
    return candidates + [ROOT.parent / "ext" / "squad-demo", ROOT.parent / "3DHeat-Squad-Demo"]


def squad_converter() -> list[str] | None:
    """
    How to run the Squad demo reader, an extension kept outside the watcher
    (exporters/ext/squad-demo): its `heat3d-squad-demo` command when it is on
    PATH, else `python -m heat3d_ext_squad` when the package is installed, or
    found in `HEAT3D_SQUAD_DEMO` or beside the watcher. None when it is
    nowhere. Nothing of it is imported here; it is only run.
    """
    import importlib.util
    import shutil

    found = shutil.which(SQUAD_COMMAND)
    if found:
        return [found]
    if squad_folder() is not None or importlib.util.find_spec("heat3d_ext_squad") is not None:
        return [sys.executable, "-m", "heat3d_ext_squad"]
    return None


def squad_folder() -> Path | None:
    """The folder the reader runs in, when it is a source folder rather than installed."""
    return next((c for c in _squad_sources() if (c / "heat3d_ext_squad" / "__init__.py").is_file()), None)


def squad_demo_folders() -> list[Path]:
    """
    Where Squad demos land on this machine: a dedicated server's
    `SquadGame/Saved/Demos` (a local server installed through Steam, or one in
    Steam's libraries), and the game client's own `Saved/Demos` for demos
    recorded with RecordingStart. Demos copied off a rented server go in a
    folder listed under `squad-demos` in the settings' `replay_folders`, or
    are converted with `python -m heat3d_watch replays squad-demos <folder>`.
    """
    out = []
    for common in steam_libraries():
        for install in ("Squad Dedicated Server", "Squad"):
            out.append(common / install / "SquadGame" / "Saved" / "Demos")
    local = os.environ.get("LOCALAPPDATA")
    if local:
        out.append(Path(local) / "SquadGame" / "Saved" / "Demos")
    return out


@dataclass
class SquadDemos(ReplayAdapter):
    """
    Squad server demos (`.replay`, recorded with the admin command
    AdminDemoRec), converted by the external reader (exporters/ext/squad-demo,
    `heat3d-squad-demo`) into the session folder as `<map>/<match>.parquet`
    and `.match.json`. The watcher only runs the command: reading Unreal's
    replay format lives in the reader alone.
    """

    _said: bool = False

    def folders(self, ctx: Context) -> list[Path]:
        return squad_demo_folders() + super().folders(ctx)

    def missing(self) -> str | None:
        if squad_converter() is None:
            if not self._said:
                log.info("%s: %s", self.id, SQUAD_INSTALL)
                self._said = True
            return SQUAD_INSTALL
        return None

    def convert(self, path: Path, ctx: Context) -> None:
        command = squad_converter()
        if command is None:
            log.warning("%s: %s", self.id, SQUAD_INSTALL)
            return
        session = ctx.open(self, when=path.stat().st_mtime, meta={"replay": str(path)})
        try:
            out = subprocess.run(
                [*command, str(path), "-o", str(session.folder)],
                cwd=squad_folder(),
                capture_output=True,
                text=True,
                timeout=3600,
            )
            session.meta["converter"] = (out.stdout + out.stderr).strip()[-2000:]
            summaries = sorted(session.folder.glob("*/*.match.json"))
            if out.returncode != 0 or not summaries:
                session.event("replay_failed", file=path.name)
                return
            record_squad_match(session, json.loads(summaries[0].read_text(encoding="utf-8")))
            tables = sorted(session.folder.glob("*/*.parquet"))
            if tables:
                count_events(session, tables[0])
        finally:
            ctx.close(session)


def record_squad_match(session, match: dict) -> None:
    """A Squad demo's summary into the session: the layer, the teams, and each player's line."""
    session.meta["match"] = {k: match.get(k) for k in ("match", "map", "layer", "game_version", "teams")}
    if match.get("recorded_unix"):
        session.started = float(match["recorded_unix"])
    session.stat("map", str(match.get("map") or ""))
    session.stat("layer", str(match.get("layer") or ""))
    players = [p for p in match.get("players") or [] if p.get("name")]
    session.stat("players", len(players))
    if isinstance(match.get("duration_s"), (int, float)):
        session.stat("match_seconds", round(match["duration_s"], 1))


ADAPTERS.append(
    SquadDemos(
        id="squad-demos",
        game="Squad",
        patterns=("*.replay",),
        source="server demos Squad records with the admin command AdminDemoRec: "
        "<server>/SquadGame/Saved/Demos/*.replay, read by the external reader `heat3d-squad-demo` "
        "(exporters/ext/squad-demo)",
        records=(
            "every player's position, body yaw and speed each time the server replicates it (up to 8 times a "
            "second), on foot and in ground vehicles",
            "each player's name, team, faction and squad, following team changes",
            "not: helicopters' movement, kills and deployables - see the reader's README",
        ),
        enable="record on the server: give the admin the `demos` permission in Admins.cfg, then AdminDemoRec "
        "<name> and AdminDemoStop in the game's console; copy the demo here and install the reader: "
        "pip install -e <3DHeat>/exporters/ext/squad-demo",
        axes=Axes(up="z", units="Unreal units (centimetres)"),
        verified="the reader is checked on public Squad v10.3.1 server demos (movement agrees with the velocity "
        "it carries; every row's team matches its soldier's faction) and by tests on built demos; this hook by "
        "tests with a stand-in command",
        multiplayer=True,
    )
)
