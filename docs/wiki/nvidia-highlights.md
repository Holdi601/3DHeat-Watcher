
# NVIDIA Highlights

The `nvidia-highlights` adapter records the clips, highlights and screenshots the NVIDIA App (or
GeForce Experience) saves, and gives each one a place on the map when it can. This page explains what
NVIDIA Highlights can deliver and what it cannot, which files the watcher reads, and how a highlight
gets a position. The adapter's generated page is [NVIDIA highlights (platform)](game-nvidia-highlights).

## What NVIDIA Highlights can and cannot deliver

A game that supports NVIDIA Highlights talks to the NVIDIA App through NVIDIA's GfeSDK. The SDK
carries only two kinds of message:

1. **Once, at start**: the highlight kinds the game will use - an id (such as `kill`), a
   significance, tags, and a display name per language. The NVIDIA App stores these per game.
2. **At a moment of play**: "highlight `<id>`, from `<ms>` before now to `<ms>` after". That is the
   whole message: the id of a kind the game registered, and two time offsets that tell the NVIDIA App
   which stretch of its rolling recording to keep.

The SDK has **no field for anything else**: no position, no match or round, no opponent, no weapon, no
score, no custom data of any kind. A game cannot put a position into a highlight even if it wanted to.
When the clip is saved, the NVIDIA App adds a file, a game name, a length and a time.

So all a highlight can say is "this kind of moment, in this game, at this time". Everything more has
to come from somewhere else.

## What the watcher reads

Everything is read from files the NVIDIA App writes for its own gallery. Nothing talks to the
driver or the app. The NVIDIA Overlay folder is
`%LOCALAPPDATA%\NVIDIA Corporation\NVIDIA Overlay`.

| File | What is taken from it |
|---|---|
| `UGCTracker.json` | the gallery index: every clip and screenshot with its path, type (video, image), sub-type (`InstantReplay`, ...), date, the game's profile name, executable and short name, and length (`msDuration`) |
| `GallerySettings.json` | `settings.currentDirectoryV2`, the capture folder, and `settings.tempDirectory`, where highlights wait (`<temp>\Highlights\<game>`) until they are saved |
| `Highlights\<game>\config.json` | the highlight kinds each game registered: id, and the English display name (or the id where the game gave none) |
| the capture folder (default `%USERPROFILE%\Videos\NVIDIA`) and `<temp>\Highlights` | the clip and screenshot files themselves (`.mp4`, `.mkv`, `.mov`, `.png`, `.jpg`, `.jpeg`), one folder per game |
| `%LOCALAPPDATA%\NVIDIA Corporation\GfeSDK\<exe>_<pid>.log` | the requests GfeSDK games log - `Posted Request HL...` lines - so a highlight the game asked for is recorded even when no clip was kept. Configuration requests (`HLConfigure`, `HLGetConfig`, `HLGetUserSettings`, `HLSetDefaultLocale`) are skipped. |

For each new item the adapter writes one row: `highlight` for a video, `screenshot` for an image, or
`highlight_request` for a GfeSDK log line. Its fields:

| Field | What it is |
|---|---|
| `ms` | the moment: the time in the file name (`<Game> 2026.05.01 - 20.31.28.115.DVR.mp4`, the local time the clip was saved), else the index's date, else the file's modification time |
| `game` | the NVIDIA profile name, the folder's name or the file name's game |
| `clip`, `media` | the file's path; `video`, `image` or `file` |
| `kind` | `InstantReplay`, `Screenshot`, `Highlight` (from the temporary highlights folder) or the index's sub-type |
| `duration_s`, `clip_start_ms` | the length, from the index or from the video's own header (`moov/mvhd`, found without reading the video); the moment the clip begins |
| `highlight_id`, `highlight_name` | the highlight kind, when something names it (see below) |
| `exe` | the game's executable, from the index |
| `x`, `y`, `z`, `session`, `position_from`, `position_lag_ms` | the borrowed position, when one was found (see below) |

The session statistics are `clips`, `screenshots`, `clip_seconds` and `placed` (items that got a
position).

**The highlight id** is not written in any documented place. The adapter tries two undocumented
ones: a field of the gallery entry whose name contains "highlight", and - only for files in the
temporary highlights folder - one of the game's registered ids (at least 4 characters long) that
appears in the file name. A saved clip is named after the game, which could contain an id like "kill"
by chance, so its name is not searched. These two ways have not been seen to work on a real machine
yet: no clip with a highlight id, and no GfeSDK request line, has occurred where the adapter was
tested. The gallery index, settings, highlight definitions and clips were tested on real files.

### When items are recorded

- A clip is still being written for a while after the key press. The adapter waits until a file has
  the same size and time at two looks (every 10 s) and is at least 5 s old.
- The first time the adapter runs, everything already in the gallery and the logs is only noted, not
  recorded, so years of old clips do not flood the statistics. What it has seen is kept in
  `<data>\state\nvidia-highlights.json`, so a restart records nothing twice.
- Items are grouped into one session per game. A game's session closes after 30 minutes without a new
  item, and ends at its last moment rather than when it closed. Moments more than 30 minutes apart go
  into separate sessions.

## How a highlight gets a position

The highlight itself has no place. The adapter looks the moment up in the other recordings the
watcher made of the same game at the same time:

1. **The same game**: the session folders under `<data>\sessions\` whose game name matches the
   highlight's. Names are compared in lower case, letters and digits only. They match when they are
   equal, or when the shorter one has at least 5 characters and is contained in the longer
   (`Counter-Strike 2` and `Counter-Strike-2`).
2. **The same time**: sessions whose start and end (from `meta.json`, with a second's slack at both
   ends) cover the moment. Sessions that ended without positions, and the adapter's own sessions, are
   skipped.
3. **The player's own row**: in their `events.jsonl`, the latest of the player's own rows with a
   position, at or before the moment and no more than 5 seconds before it. A row is the player's own
   when its source says so: `"player": "me"`, or `"own_car": 1` (racing games that record every car by
   its driver), or a `player` that is the session's `player` in `meta.json` (the name the source gives
   the player). See [The player's own rows](the-data#the-players-own-rows).

If a row is found, the highlight gets its `x`, `y`, `z`, its `session` (or the folder's name),
`position_from` (the folder it came from) and `position_lag_ms` (how long before the moment that row
was). The highlight session takes that recording's axes, so it is drawn the same way round. If no row
is found, the highlight stays a moment on the timeline without a place.

Things to know about the borrowed position:

- **It is where you were when the clip was saved**, not where the action began. The moment is the
  save time in the file name, which for an Instant Replay is its end. `clip_start_ms` says when the
  clip begins.
- **Another adapter has to have been recording the same game at the time.** The ones that mark the
  player's own rows, and so can place a highlight: Counter-Strike 2 and Dota 2 game-state integration,
  Forza, the Assetto Corsa games, EA SPORTS WRC, DiRT Rally 2.0, Richard Burns Rally, BeamNG.drive,
  Euro Truck Simulator 2, American Truck Simulator, DCS World, X-Plane, Microsoft Flight Simulator, War
  Thunder, Minecraft and memory profiles (as `me`); F1 23/24/25, RaceRoom, Automobilista 2 and Project
  CARS 2 (your car's rows carry `own_car` 1, by the game's player car index, its own slot or the viewed
  participant); Elite Dangerous (the commander's name, in `meta.json` as `player`, since the journal is
  always the player's).
- **A replay is converted after the match**, so it can only place a clip that is looked up after the
  conversion: the clip is placed when it is recorded, and a replay saved later is not looked at again.
  League of Legends replays name your rows by the Riot ID in the settings and, with a Riot API key, give
  them the wall-clock time the match timeline states, so they are found then. A CS2 demo cannot place a
  highlight at all: its positions are in the converter's own table, not in `events.jsonl`, and a demo
  has the game's ticks but no wall-clock time to match a clip's moment against.
- In Rocket League the only rows with a place are ball events. A ball hit of yours is a row of yours,
  so a highlight can be placed where you last hit the ball.
- Games with no positional source at all (Overwatch 2, Call of Duty, Hunt: Showdown, ...) keep their
  highlights as a timeline of moments.

## Why memory cannot give a position in multiplayer

The other way to get a position would be to read it out of memory. Neither memory works:

- **NVIDIA's memory has no position in it.** The NVIDIA App receives what the GfeSDK carries - a
  highlight id and two time offsets - plus the video it records. There is no position anywhere on
  NVIDIA's side to read. (The watcher does not read NVIDIA's memory anyway; it reads the files above.)
- **The game's memory is off limits in multiplayer.** The position is in the game's process, but the
  watcher never reads a multiplayer game's memory: a memory adapter for a game marked as played online
  is refused before anything is opened (see [Reading memory](memory-reading)). Multiplayer games run
  under anti-cheats (Easy Anti-Cheat, BattlEye, Vanguard, ...) that treat another program opening the
  game's process as cheating, which can get the account banned. Reading the game's state from outside
  is also what the games' terms forbid. A highlight in a multiplayer game therefore gets a place only
  from what the game publishes: its game-state integration or telemetry, recorded by another adapter at
  the same time.
