---
title: The data
nav_order: 4
---

# The data

All recordings are plain files in the data folder (`%LOCALAPPDATA%\3DHeat\Watcher` unless changed,
see [Installing and running](installing-and-running.md#where-everything-is)). You can read, copy or
delete them without the watcher.

## Session folders

A **session** is one sitting with one source: from the moment the game first says something until it
stops (the game closes, a match ends, a drive or a flight is reset - each adapter's page says what
starts and ends its sessions). Each session gets a folder:

```text
<data>\sessions\<game>\<YYYY-MM-DD_HH-MM-SS>_<adapter id>\
    events.jsonl
    heat.parquet
    meta.json
```

- `<game>` is the game's name with every character other than letters, digits, `.`, `_` and `-`
  replaced by `-` (at most 60 characters): `EA-SPORTS-F1-25`, `Counter-Strike-2`. Adapters that cover
  many games (Steam statistics, Steam Timeline, NVIDIA highlights) file each session under the game it
  belongs to.
- The time is the session's start in local time. Sessions that describe the past (a replay converted
  after the match, a Steam stats file) use the time the game or file gives. Two sessions starting in the
  same second get `_2`, `_3`, ... appended.
- The session's id, in the statistics database, is `<game folder>/<session folder>`.

A session in which nothing at all was recorded (the game sat in its menus, or crashed at start) is
deleted when it closes, so every launch does not leave an empty folder.

Some sessions hold more files. A Counter-Strike 2 demo session holds the converter's own table and
summary (`<map>/<match>.parquet`, `<match>.match.json`). An iRacing session lists the `.ibt` files the
sim wrote during the sitting as `telemetry_file` events.

## events.jsonl

`events.jsonl` has one JSON object per line, one line per event, written the moment the event
happens. The file is line-buffered, so a crash, a power cut or a killed process loses nothing that was
already written; a line cut short by a crash is skipped when the file is read, and every line before it
stands.

Every line has the same base columns:

| Column | Type | What it is |
|---|---|---|
| `time` | number | seconds since the session began (4 decimals), or the game's own clock where the adapter passes it |
| `ms` | integer | wall-clock time, Unix milliseconds |
| `event` | text | what happened: `position`, `spawn`, `death`, `kill`, `lap`, `teleport`, `session_start`, ... |
| `x`, `y`, `z` | number | where, in the game's own units and axes (see `axes` in `meta.json`); present only when all three are known and finite |
| `player` | text | who: a name, an id, or `me` for the person playing (see [The player's own rows](#the-players-own-rows)) |
| `team` | text | their side, when the game says |
| `session` | text | the match, round, stage, life or flight the row belongs to, when the game says |

Any other field the game reports follows under its own name (`speed_kmh`, `gear`, `lap_time`, `weapon`,
`victim`, `hero`, ...). Fields without a value are left out, and so are numbers that are not finite.
Two synthetic lines:

```json
{"time":12.3456,"ms":1777660501123,"event":"position","x":-412.5,"y":12.1,"z":233.0,"player":"me","session":"1","speed_kmh":187.4,"gear":5}
{"time":15.0,"ms":1777660503667,"event":"lap","x":-380.2,"y":12.0,"z":250.9,"player":"me","session":"1","lap_time":92.418,"lap":3}
```

Rows without a position (a kill-feed line, a level-up, a stat change) stay in `events.jsonl` and count
in the statistics. Only rows with a position go into the table.

### The player's own rows

Which rows are the person playing is said by the source, never guessed. A row is the player's own when

- its `player` is `me`: most adapters, whose source is the player's own game (telemetry of the own
  car or aircraft, a game-state integration, a journal);
- it carries `own_car` 1: the racing games that record every car under its driver's name (EA SPORTS F1
  by the game's player car index, RaceRoom by its own slot, Automobilista 2 and Project CARS 2 by the
  viewed participant) mark the player's car this way and keep the driver's name in `player`;
- its `player` is the session's `player` in `meta.json`: the name the source gives the player - Elite
  Dangerous's commander (the journal is always the player's), a League of Legends replay's line of the
  Riot ID in the settings.

War Thunder and Rocket League name every player and do not say which one is you; with your name in the
`player_names` setting (see [Settings](installing-and-running.md#settings)) your rows become `me`.
[NVIDIA highlights](nvidia-highlights.md) look a moment up in exactly these rows.

## heat.parquet

When a session closes, the rows of `events.jsonl` that have `x`, `y` and `z` are written to
`heat.parquet`. This is the table the 3DHeat viewer opens. If the session has no positions, no table
is written.

- The columns are `time`, `ms`, `event`, `x`, `y`, `z`, `player`, `team`, `session`, followed by every
  other field in the order it first appears.
- `x`, `y`, `z` and `time` are 64-bit floats and `ms` is a 64-bit integer. A further column whose
  values are all numbers is a 64-bit float; any other column is dictionary-encoded text (missing values
  are empty text, and lists or objects are written as JSON text).
- The file's metadata has a key `heat3d` with the reading instructions, so the viewer maps columns
  and axes by itself (an example, with the `extra` list shortened):

```json
{
  "version": 1,
  "kind": "heat3d-watch",
  "game": "EA SPORTS F1 25",
  "axes": {"up": "y", "flipX": false, "flipY": false, "flipZ": false, "scale": 1.0},
  "columns": {
    "x": "x", "y": "y", "z": "z",
    "time": "time", "timeUnit": "seconds",
    "personId": "player", "teamId": "team", "sessionId": "session",
    "extra": ["event", "speed_kmh", "gear", "lap_time", "lap"]
  }
}
```

`up` is the game's up axis, `flipX`/`flipY`/`flipZ` mirror an axis so a left-handed world is not drawn
mirrored, and `scale` is the viewer's unit scale: the viewer multiplies every position by it when it
loads the table (0.01 would turn centimetres into metres). Every adapter writes 1 and keeps the game's
own units - metres for most, Source units (inches) for Counter-Strike 2, Unreal units (centimetres) for
Rocket League - because a level exported from the game is in those same units, so the rows land on it;
the CS2 converter's own tables say the same. `units` in `meta.json` says what one unit is. Each game's
page lists its values under "Positions and axes".

`heat.parquet` can always be rebuilt from `events.jsonl` with
`python -m heat3d_watch table <session folder>` (see [Commands](commands.md#table)). This is useful when
`pyarrow` was missing while the session was recorded.

## meta.json

`meta.json` summarises the session. It is written when the session opens, at most every 30 seconds while
events or statistics come in, and when the session closes. Statistics are only kept in memory between
those writes, so a crash can lose at most the last half minute of them.

```json
{
  "format": "heat3d-watch-session",
  "version": 1,
  "watcher": "1.0.1",
  "game": "EA SPORTS F1 25",
  "adapter": "f1-25",
  "source": "UDP telemetry 127.0.0.1:20777 (...)",
  "multiplayer": true,
  "started": "2026-05-01T20:15:03",
  "ended": "2026-05-01T21:02:11",
  "seconds": 2828.0,
  "axes": {"up": "y", "flip_x": false, "flip_y": false, "flip_z": false, "scale": 1.0, "units": "metres"},
  "events": {"position": 52110, "lap": 412, "teleport": 3},
  "positions": 52530,
  "stats": {"laps": 20, "best_lap": 91.874, "distance_km": 106.3, "race_position": 4},
  "track": "..."
}
```

A session whose source names the player (see [The player's own rows](#the-players-own-rows)) also has
`"player"`: the name the player's own rows carry.

- `started` / `ended`: local time to the second; `ended` is `null` while the session runs.
- `events`: how many times each event happened, most frequent first. `positions` is the number of rows
  with a position.
- `stats`: the session's numbers. An adapter sets each one, adds to it, or keeps the maximum or minimum.
- Whatever else the adapter knows about the sitting follows at the top level: the track, map, mission,
  match id, the Steam app id, the replay file, the memory profile and build. A session finished by
  recovery has `"recovered": true`.

## watcher.sqlite

`watcher.sqlite` is the statistics database. A row is added for every session when it closes. The
three tables are plain, so any SQL tool, notebook or spreadsheet can read them without the watcher:

```sql
CREATE TABLE sessions (
  id TEXT PRIMARY KEY,          -- <game folder>/<session folder>
  game TEXT NOT NULL,
  adapter TEXT NOT NULL,
  started REAL NOT NULL,        -- Unix seconds
  ended REAL,                   -- Unix seconds
  seconds REAL,
  folder TEXT NOT NULL,         -- the session folder's full path
  events INTEGER NOT NULL DEFAULT 0,
  positions INTEGER NOT NULL DEFAULT 0,
  multiplayer INTEGER NOT NULL DEFAULT 0,
  source TEXT
);
CREATE TABLE events (           -- per session, how many times each event happened
  session TEXT NOT NULL REFERENCES sessions(id) ON DELETE CASCADE,
  event TEXT NOT NULL,
  count INTEGER NOT NULL,
  PRIMARY KEY (session, event)
);
CREATE TABLE stats (            -- per session, every number the game reported or the watcher counted
  session TEXT NOT NULL REFERENCES sessions(id) ON DELETE CASCADE,
  key TEXT NOT NULL,
  value REAL,                   -- numbers
  text TEXT,                    -- everything else (a map name, a result, a hero)
  PRIMARY KEY (session, key)
);
```

Recording a session again (recovery, a replay converted again) replaces its rows. `multiplayer` is the
adapter's flag (some adapters set it per session, for example DCS from the mission), not a check of
whether you were online. A true/false value in `stats` is stored as text.

An example query, the best lap per game over all sessions (lower is better):

```sql
SELECT s.game, MIN(t.value) AS best_lap
FROM stats t JOIN sessions s ON s.id = t.session
WHERE t.key = 'best_lap'
GROUP BY s.game;
```

`python -m heat3d_watch stats` prints totals from these tables (see [Commands](commands.md#stats)); its
`best` column is the lowest value for times kept as a best and for places, the highest for the rest.

## Recovery after a crash

When `run` starts, it looks for sessions that an earlier watcher left open: a `meta.json` with no
`ended`, and an `events.jsonl` with at least one line. It finishes each one:

- the event counts and the number of positions are counted again from `events.jsonl`, skipping a line
  cut short;
- the end is the wall-clock time of the last line (`ms`);
- the statistics are those of the last `meta.json` write (at most 30 seconds old);
- `"recovered": true` is added, `heat.parquet` is written, and the session goes into `watcher.sqlite`.

The log says "finished N session(s) left open by an earlier run". The lock file keeps a second
watcher from "recovering" the sessions of one that is still running.

## CSV export

```bash
python -m heat3d_watch stats --csv out
```

writes `out\sessions.csv`, `out\events.csv` and `out\stats.csv`. Each file is one table of
`watcher.sqlite`, complete, with a header row, as UTF-8. Times are Unix seconds as in the database.
`--game` does not narrow the export; every session is written.

## Opening a session in the 3DHeat viewer

Open a session's `heat.parquet` in the 3DHeat viewer. The footer tells the viewer which column is the
position, the time, the player, the team and the session, and which way is up, so nothing has to be
mapped by hand. Positions are in the game's own world coordinates. Drawn over a level exported with
the other 3DHeat tools (for example from [3DHeat GameFiles](https://github.com/Holdi601/3DHeat-GameFiles)),
they land where they happened.

- **Heatmaps** use every row with a position, filtered by `event`, `player`, `team` or `session` like any
  other column.
- **Line heat** draws a line from each of a player's rows to their next one, and in playback each
  player is a point moving along the route with a tail behind it. The viewer's Routes panel chooses,
  from the `event` column, which events **start** a route and which **end** one. The watcher writes
  the bounding events as rows with a position, so they can be chosen there:
  - starts: `spawn`, `respawn`, `session_start`. A start closes the route that was open without
    drawing a line to the new place.
  - ends: `death`, `finish`, `session_end`, and `teleport`. The line runs up to the end row itself,
    which is where the player died, stopped or was taken away.

  A jump - a place reached without travelling there - is two rows: `teleport` at the place **left**,
  and a start at the place **arrived** at, right after it. The racing adapters write one whenever the
  car moved further than it could have driven (a rewind or flashback, a reset to the road, back to the
  pits, a fast travel), with `spawn` at the arrival (`respawn` for BeamNG's reset); the `teleport` row
  carries the arrival as `to_x`, `to_y`, `to_z` and the distance as `metres`, the start row
  `after: "teleport"`. The truck adapters do the same for a ferry, a train or a loaded save, and the
  flight adapters for a jump no aircraft could fly. So with `teleport` among the ends and `spawn`
  among the starts - which is what the viewer suggests by itself - a route ends where the jump left
  and the next begins where it arrived, and no line crosses the map. A route never runs across a
  change of the `session` column. A position row is written a few times a second
  (10 Hz for most telemetry), which gives a smooth line.
- The `session` column splits a sitting into its rounds, stages, lives or bodies (Elite Dangerous
  keeps galaxy rows and each planet's surface rows apart this way). Pick one in the viewer to look at
  that part alone.

What the viewer does with the rows - filters, colours, playback - is described in the viewer's own
documentation. Counter-Strike 2 demo sessions are opened through the converter's `<map>/<match>.parquet`
and `<match>.match.json` in the viewer's heat and match tabs. iRacing's positions come from the
`.ibt` files listed in the session, which the viewer reads itself.
