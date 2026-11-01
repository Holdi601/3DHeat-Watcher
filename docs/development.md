---
title: Development
nav_order: 10
---

# Development

This page is for adding a game: how an adapter is built, how it is tested, and how its documentation
is made.

## The repository

| Path | What it holds |
|---|---|
| `heat3d_watch/cli.py` | the commands ([Commands](commands.md)) |
| `heat3d_watch/watcher.py` | the background loop: process list, one thread per adapter, updates |
| `heat3d_watch/session.py` | a recording: `events.jsonl`, `heat.parquet`, `meta.json`, recovery |
| `heat3d_watch/db.py` | `watcher.sqlite` |
| `heat3d_watch/config.py` | the settings and the data folder |
| `heat3d_watch/safety.py`, `heat3d_watch/memory.py` | the memory checks and the read-only reader ([Reading memory](memory-reading.md)) |
| `heat3d_watch/notify.py` | Windows notifications |
| `heat3d_watch/adapters/` | one module per game or family of games; modules starting with `_` are shared helpers |
| `heat3d_watch/decoders/` | the racing telemetry decoders, copied from 3DHeat GameCapture's lap recorders |
| `heat3d_update/` | the updater ([Updates](updates.md)) |
| `mods/beamng/heat3d/` | the BeamNG protocol mod `setup beamng` installs |
| `tests/` | the tests |
| `tools/gen_game_pages.py` | writes the game pages of this documentation |

## An adapter

An adapter is a dataclass derived from `heat3d_watch.adapters.base.Adapter`. Its fields say what it
is; its methods do the work.

| Field | Default | What it is |
|---|---|---|
| `id` | `""` | short and stable: session folders, `disabled`, `replay_folders` and `player_names` refer to it |
| `game` | `""` | the game's name as people write it; sessions are filed under it |
| `kind` | `"telemetry"` | one of `telemetry`, `gsi`, `log`, `replay`, `platform`, `memory` ([Sources and rules](sources-and-rules.md)) |
| `exes` | `()` | executable names (any case) that mean the game is running. Empty: the adapter is always on (`always` is true) |
| `multiplayer` | `True` | the game is played online: its memory is never read |
| `source` | `""` | where the numbers come from, said once |
| `records` | `()` | what is recorded, one item per kind of thing |
| `enable` | `""` | how to switch the source on; empty when nothing is needed |
| `interval` | `0.1` | seconds between polls |
| `axes` | `Axes()` | the world's up axis, mirrored axes, the viewer's unit scale (keep 1) and a note on the units |
| `verified` | `""` | what has been checked, honestly (see below) |

`source`, `records`, `enable` and `verified` are documentation, not decoration. `games` prints them,
`games --markdown` makes the table in [All games in one table](watcher.md), and the game pages are
generated from them. Write them so they say exactly what the code does.

The methods, all optional:

| Method | Called | What it should do |
|---|---|---|
| `missing(self) -> str \| None` | by `games`, `status`, and before starting | say why the adapter cannot run here (a DLL not found, a folder missing), or `None` |
| `setup(self, ctx, *, apply) -> list[str]` | by `setup` | switch the game's own output on; return one line per change, and change files only when `apply` is true. Back a file up as `<file>.heat3d-backup` before its first change, and never overwrite that backup. Override it only when there is something to switch on: `can_setup` (true when `setup` is overridden) decides whether `setup` runs it or says that there is nothing to change; a class that serves several games overrides `can_setup` for the ones it cannot set up (`RallyAdapter` for Richard Burns Rally). |
| `start(self, ctx)` | when the game's process appears (always-on adapters: when `run` starts) | open sockets, find files, remember where to begin |
| `poll(self, ctx)` | every `interval` seconds, in the adapter's own thread | take what the game said since the last poll and record it |
| `stop(self, ctx)` | when the game is gone or the watcher stops | close sessions and sockets |

Each adapter runs in its own thread (`Runner`). An exception in `poll` is logged and the adapter waits
`min(5, interval × 10 + 0.5)` seconds before the next poll. After 20 failures in a row, or a failure in
`start`, the adapter is stopped and not started again until the game's process id changes.
`missing()` is checked at every scan, so keep it cheap.

An adapter object is reused when its game starts again, so `start` must reset everything a previous run
left behind.

### Registering it

Put the module in `heat3d_watch/adapters/` and list the adapters at its end:

```python
ADAPTERS = [MyAdapter(id="mygame", game="My Game", ...)]
```

`adapters.load()` imports every module in the package (except `base` and names starting with `_`) and
collects their `ADAPTERS`. Two adapters with the same id stop the load with a `ValueError`. A module that
fails to import (a missing dependency) leaves its games out and is named by `games` with the error, so
one game's problem does not stop the others.

## Context and Session

`start`, `poll`, `stop` and `setup` get a `Context`:

| Member | What it is |
|---|---|
| `settings` | the `Settings` ([Installing and running](installing-and-running.md#settings)) |
| `data` | the data folder |
| `pid`, `exe` | the game's process id and executable path, when the adapter was started for a running game; the install folder is next to `exe` |
| `open(adapter, *, game=None, when=None, axes=..., source=..., multiplayer=..., meta=...)` | a new `Session`. `game` overrides the adapter's game name (for adapters covering many games); `when` sets the start for sessions that describe the past; `axes`, `source` and `multiplayer` default to the adapter's; `meta` is a dictionary written into `meta.json` |
| `close(session)` | end a session: the table, `meta.json`, its line in `watcher.sqlite`. A session with no events is deleted. Accepts `None`. Returns the table's path or `None`. |

A `Session` records:

| Member | What it does |
|---|---|
| `event(name, *, t=None, ms=None, x=None, y=None, z=None, player=None, team=None, session=None, **attrs)` | one row. `t` defaults to seconds since the session began, `ms` to now. A position counts only when `x`, `y` and `z` are all given and finite. `None` attributes are left out. |
| `position(x, y, z, **kw)` | an event named `position` |
| `stat(key, value, how="set")` | a statistic: `set` it, `add` to it, keep the `max` or the `min` |
| `now()` | seconds since the session began |
| `meta` | a dictionary written into `meta.json` |
| `started`, `ended`, `folder`, `id`, `counts`, `positions` | when, where, and what was recorded so far |

`event` and `stat` are thread-safe and can be called from a worker thread.

Conventions that the rest of the system relies on:

- **The player's own rows are marked, from what the source says.** `player="me"` where the source is
  the player's own; where every player is recorded under a name, `own_car=1` on the player's car's rows
  (by the game's player index or viewed participant), or the player's name as `session.meta["player"]`
  (written to `meta.json` at once) when the source names the player. Never guess: where the source does
  not say, take the name from a setting (`player_names`, `riot_id`) or mark nothing.
  [NVIDIA highlights](nvidia-highlights.md) borrow positions only from such rows
  (`platform.own_row`). Other players go by their name or id.
- **Routes are bounded by events with positions**: `spawn`, `respawn` and `session_start` begin one;
  `death`, `finish`, `session_end` and `teleport` end one. Whenever the player moved without travelling
  (a reset, a rewind, a fast travel, a loaded save), write `teleport` at the place left and then a
  start (`spawn`, or `respawn` for a reset the game names) at the place arrived at, so the viewer's line
  heat ends one route and begins the next instead of drawing across the map. `Driving.jumped` does it
  for vehicles.
- **Positions stay in the game's own world coordinates and units**, described by `axes`. Do not
  convert them to another frame unless the game gives no usable world frame (the flight sims put
  latitude and longitude into a flat map around the first fix). `axes.scale` is the viewer's unit
  scale - it multiplies every position by it - and stays 1, so the rows line up with a level exported
  from the same game in the same units; say the unit in `axes.units`.
- **Statistic keys** are lower case with underscores, and carry their unit where one applies
  (`distance_km`, `top_speed_kmh`, `max_altitude_m`, `duration_s`). A time kept as a best starts with
  `best_` (kept with `min`), a place ends in `_position`: `stats` shows the lowest of those as the
  best, and the highest of every other key (`db.lower_is_better`).

## Helpers

| Helper | Module | For |
|---|---|---|
| `Follower(find, since, stamp=None)`, `game_started(pid)`, `newest(paths)`, `read_shared(path)`, `steam_libraries()` | `_logfollow` | following a log the game writes: shared reads, only this sitting's lines, new and replaced files, whole lines only |
| `UdpPort(port, forward=None, grace=0.0, recheck=3.0)` with `try_open(who)`, `receive()`, `close()` | `racing` | a UDP telemetry port on 127.0.0.1, taken only when free, given up to another program, optionally relayed |
| `Driving(adapter, ctx, hz=10.0, jump=50.0)` with `sample(...)`, `event(...)`, `lap(...)`, `count(...)`, `close()` | `racing` | vehicle sessions: positions at a fixed rate, distance, top speed, laps; on a jump, `teleport` where the car was and `spawn` where it is (`jumped(...)`) |
| `SharedView.open(name)` | `simracing_shm` | a game's named shared memory, read-only, never created |
| `ReplayAdapter` (`patterns`, `folders(ctx)`, `convert(path, ctx)`) | `replays` | a watched replay folder: files converted once they stop growing, in a worker thread; the first look only notes what is there, and `convert_existing(ctx, folder=None)` - the [`replays`](commands.md#replays) command - converts those on request |
| `load_state`, `save_state` | `platform` | remembering what an always-on adapter has seen, in `<data>\state\<id>.json` |
| `FlightLog`, `Tangent` | `xplane` | flight bookkeeping (takeoffs, landings, crashes, distance) and the flat map around the first fix |
| `backup_once(path)` | `gsi`, `racing` | the `<file>.heat3d-backup` rule |
| Steam's files | `_steam` | binary and text KeyValues, the Steam folder from the registry |

A minimal log adapter, as an illustration (a made-up game):

```python
from dataclasses import dataclass, field
from pathlib import Path

from ..session import Axes, Session
from ._logfollow import Follower, game_started, newest
from .base import Adapter, Context


@dataclass
class ExampleAdapter(Adapter):
    _session: Session | None = field(default=None, repr=False)
    _follow: Follower | None = field(default=None, repr=False)

    def start(self, ctx: Context) -> None:
        log = (ctx.exe.parent if ctx.exe else Path(".")) / "logs" / "game.log"
        self._session = None
        self._follow = Follower(lambda: newest(p for p in [log] if p.exists()), game_started(ctx.pid))

    def poll(self, ctx: Context) -> None:
        for line in self._follow.lines() if self._follow else []:
            if line.startswith("DIED "):
                if self._session is None:
                    self._session = ctx.open(self)
                self._session.event("death", player="me")
                self._session.stat("deaths", 1, "add")

    def stop(self, ctx: Context) -> None:
        self.poll(ctx)
        ctx.close(self._session)
        self._session = None


ADAPTERS = [
    ExampleAdapter(
        id="example",
        game="Example Game",
        kind="log",
        exes=("ExampleGame.exe",),
        source=r"<install>\logs\game.log (followed)",
        records=("deaths",),
        interval=0.5,
        axes=Axes(units="no positions recorded"),
        verified="tested on synthetic log lines in the game's format; untested against the game",
    )
]
```

Open the session with the first thing worth recording, not in `start`, so a game left in its menus
leaves nothing behind (an empty session is deleted anyway).

## Tests

```bash
python -m pytest
```

`tests/conftest.py` gives every test a throwaway data folder (`HEAT3D_WATCH_HOME`) and switches off
update checks and notifications (`HEAT3D_NO_UPDATE`, `HEAT3D_NO_TOAST`). An adapter test builds the
game's output from its published format - packets from the specification, log lines in the game's
format, files in the documented layout - and drives the adapter directly (shortened from
`tests/test_poe.py`; `data` and `install` are temporary folders):

```python
from dataclasses import replace
from heat3d_watch.adapters import poe
from heat3d_watch.adapters.base import Context
from heat3d_watch.config import Settings
from heat3d_watch.session import read_rows

ctx = Context(Settings(data=str(data)), data, exe=install / "PathOfExileSteam.exe")
a = replace(poe.ADAPTERS[0])   # a fresh copy of the adapter
a.start(ctx); a.poll(ctx); a.stop(ctx)
[session] = list((data / "sessions").glob("*/*"))
rows = read_rows(session)      # then check the rows and meta.json's stats
```

Network adapters are tested against a fake local server or with packets sent over UDP to the adapter.
Tests that check against real game data on the developer's machine are marked `@pytest.mark.local` and
are skipped where that data is absent. That data never goes into the repository. `test_core.py` also
holds the test that fails if any code that could write to another process appears in the package
(`test_memory_reading_cannot_write`).

## An honest `verified`

`verified` says what was checked and how, and what was not. It is shown by `games` and on every game
page, and players rely on it. Examples from the code:

- "tested on packets in the 2023, 2024 and 2025 formats built from EA's published specification, sent
  over UDP; untested against the game"
- "tested on documents in the published GSI format posted to the running adapter; untested against the
  running game (not installed here)"
- "decoded all real stats files and schemas on this machine (local test); change detection tested on
  files built in the binary KeyValues format"

Say "untested against the game" until the adapter has recorded the running game. Name the source of
every offset and layout, and say where two sources were compared. Never claim more than was done. A
format that was guessed or taken from community tools is said to be that.

## The game pages

Every page under [Games](games.md) is generated from the adapters, so it always matches the code. After
adding or changing an adapter, regenerate them from the repository folder:

```bash
HEAT3D_NO_UPDATE=1 python tools/gen_game_pages.py
```

(In PowerShell: `$env:HEAT3D_NO_UPDATE = "1"; python tools/gen_game_pages.py`.)

The script:

- loads the adapters with `heat3d_watch.adapters.load()`, against an empty temporary data folder, so
  no memory profile or setting on your machine ends up in the pages. Memory adapters are left out,
  since they come from players' own profiles;
- refuses to write anything if an adapter module fails to import (the pages would lose those games);
- writes `docs/game-<adapter id>.md` for every adapter and `docs/games.md` with the overview table, and
  deletes the pages of adapters that no longer exist;
- takes "What is recorded", "Where it comes from", "How to switch it on", the axes, the multiplayer
  flag and "Verified" from the adapter's fields;
- turns the module's docstring into "How it works". Write docstrings in the plain-text style the
  modules already use, which the script converts: paragraphs; lists with `*`, `-` or `1.`; layouts and
  examples indented under the line that introduces them (they become code blocks); a title underlined
  with dashes, or a short title line with its text indented directly under it (they become headings);
- lists the statistic keys the adapter's code sets by name - `.stat("key", ...)`, both sides of an
  `if` expression, and f-string patterns such as `score.{team}` - in the adapter's classes and in the
  helpers they use. Keys taken from a variable (a table of the game's fields) are not listed;
- decides "Positions" from the adapter's `axes.units` (a note starting with "no" or "none" means no
  positions) and from what its code writes.

Do not edit the generated pages by hand: change the adapter and run the script again. The table in
[All games in one table](watcher.md) is the output of `python -m heat3d_watch games --markdown`.
