---
title: "Steam Timeline (platform)"
parent: Games
nav_order: 42
---

# Steam Timeline (platform)

Adapter `steam-timeline` - kind [`platform`](sources-and-rules.md) - runs always on (it does not wait for a game to start) - looks for new data every 10 s.

## What is recorded

- one session per timeline file: its start and end (session_start, session_end)
- achievements unlocked during play, with time
- game mode changes (playing, staging, menus, loading screen)
- events games add through ISteamTimeline, with title and description, under their icon's name
- game phases (a match, a mission) with their tags; events inside one carry its id as session
- state descriptions the game shows on the timeline ("Round 3")
- Steam's own recording errors

## Where it comes from

%STEAM%\userdata\\&lt;account>\gamerecordings\timelines\timeline_&lt;appid>&lt;date>_&lt;time>.json

## How to switch it on

Steam > Settings > Game Recording: record in background or on demand (Steam writes timelines then)

## How it works

What the launcher and the graphics driver keep about play: Steam's statistics,
achievements, playtime and timelines, and NVIDIA's highlights and clips.

None of these sources needs a game to cooperate or to be running, so the three
adapters here are always on and look at a few files every few seconds.

#### Steam statistics (`steam-stats`)

`<Steam>\appcache\stats\UserGameStats_<account>_<appid>.bin`, rewritten by
the Steam client whenever a game stores its stats, decoded with the schema
`UserGameStatsSchema_<appid>.bin` next to it (binary KeyValues, see `_steam.py`).
Stats are integers or floats as the game defines them; achievements are bits
with an unlock time in Unix seconds. Playtime is in
`<Steam>\userdata\<account>\config\localconfig.vdf` under apps/&lt;appid>:
Playtime and Playtime2wks in minutes, LastPlayed in Unix seconds.
Steam is found through HKCU\Software\Valve\Steam SteamPath.
Stats API: <https://partner.steamgames.com/doc/features/achievements>

#### Steam Timeline (`steam-timeline`)

`<Steam>\userdata\<account>\gamerecordings\timelines\timeline_<appid><yyyymmdd>_<hhmmss>.json`,
written while Steam Game Recording is on. The file is JSON with string
numbers: "daterecorded" (Unix seconds), "starttime"/"endtime" (ms) and
"entries", each {"id", "time" (ms since daterecorded), "type", ...}. Types
seen on real files:
```text
achievement        achievement_name - Steam adds these for every game
gamemode           mode, an ETimelineGameMode: 1 playing, 2 staging, 3 menus,
                   4 loading screen
error              description - Steam's own ("#GameRecording_RecordingFailed")
event              a game's AddInstantaneousTimelineEvent/AddRangeTimelineEvent:
                   title, description, icon, priority, duration (ms),
                   possible_clip - "You killed <name>" / "with the <weapon>"
state_description  title - SetTimelineTooltip ("Round 3")
phase              a StartGamePhase..EndGamePhase span: duration (ms), tags
                   [{name, icon, group, priority}] (mode, map ...)
```
The file layout is Steam's and undocumented; the fields are the API's
parameters. Any other type is recorded under its own name with its fields.
<https://partner.steamgames.com/doc/api/ISteamTimeline>
<https://partner.steamgames.com/doc/features/timeline>

#### NVIDIA highlights and clips (`nvidia-highlights`)

What NVIDIA App / GeForce Experience keeps, all under
`%LOCALAPPDATA%\NVIDIA Corporation\NVIDIA Overlay`:
```text
UGCTracker.json      the gallery index: {"UGC": [{id, path, type (video,
                     image), subType (InstantReplay, Normal, ...), date
                     (UTC, when the file was written), profileName, drsName
                     (the exe), shortName, msDuration, ...}], "apps", "info"}
GallerySettings.json settings.currentDirectoryV2 (where clips are saved),
                     settings.tempDirectory (highlights wait in
                     <temp>\Highlights\<game> until saved)
Highlights\<game>\config.json  the highlight kinds a game registered:
                     {"highlights": {id: {significance, highlightTags,
                     name: {locale: text}}}, profileName, drsName, shortName}
```
and the clip files themselves, `<capture folder>\<Game>\<Game> yyyy.mm.dd -
hh.mm.ss.ff.DVR.mp4` (screenshots: `<Game> Screenshot yyyy.mm.dd - ...png`), the
name's time being the local time the clip was saved. GfeSDK games also log
their highlight calls in `%LOCALAPPDATA%\NVIDIA Corporation\GfeSDK\<exe>_<pid>.log`.

What this can and cannot deliver: a game that supports NVIDIA Highlights
(GfeSDK) registers highlight kinds once - an id like "kill", a
significance, tags, a display name - and later says only "highlight &lt;id>,
from &lt;ms> before now to &lt;ms> after". There are no positions, no match or
round, no opponent, no custom data: the SDK has no field for any of it. A
saved clip adds a file, a game name, a length and a time. So what is
recorded is "this kind of moment, in this game, at this time" - and a place
only by looking the time up in another adapter's recording of the same game
(`position_at`), which this adapter does for every clip it records.
<https://developer.nvidia.com/highlights>

Each adapter keeps what it has already seen in `<data>\state\<id>.json`, so a
restart records nothing twice.

The same module also serves: [NVIDIA highlights (platform)](game-nvidia-highlights.md), [Steam statistics (platform)](game-steam-stats.md).

## Positions and axes

| | |
|---|---|
| Positions recorded | no |
| Up axis | `y` |
| Units | metres |
| Mirrored for the viewer | none |
| Unit scale (`scale`: the viewer multiplies positions by it) | 1 |

These go into each session's `meta.json` (`axes`) and, when the session has positions, into `heat.parquet`'s footer, so the 3DHeat viewer turns and scales the rows by itself - see [The data](the-data.md).

## Multiplayer

- Marked as played online (`multiplayer`): **no**. `games --markdown` shows this as "single-player".
- Kind `platform`: it reads only what the game or platform hands out (what Steam or the graphics driver keeps), so it records in online play as well as offline; the flag decides only whether memory may ever be read.
- Memory: **never** read by this adapter. Only `memory` adapters read memory, and never for a game marked as played online - see [Sources and rules](sources-and-rules.md).

## Statistics recorded

Statistic keys this adapter's code sets by name (each session's `stats` in `meta.json` and the `stats` table of `watcher.sqlite`):

`achievements`, `game_mode_changes`, `phases`, `recorded_seconds`, `timeline_events`

A key in braces is completed at run time (`score.{team}` is one key per team). Keys the code takes from a table of the game's fields or from the game's own stat names are not in this list; "What is recorded" above names them.

## Verified

tested on the real timeline files on this machine (local test): achievement, gamemode, error, and one game's own event, state_description and phase entries; the file format itself is undocumented

## Source

[heat3d_watch/adapters/platform.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/platform.py)

*Generated from the adapter by `tools/gen_game_pages.py`; change the adapter and run it again rather than editing this page.*
