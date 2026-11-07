---
title: "Steam statistics (platform)"
parent: Games
nav_order: 43
---

# Steam statistics (platform)

Adapter `steam-stats` - kind [`platform`](sources-and-rules.md) - runs always on (it does not wait for a game to start) - looks for new data every 30 s.

## What is recorded

- every stat a game stores in Steam (its own names and values), per game, when it changes
- achievement unlocks with display name, description and unlock time
- stat changes with old value, new value and difference
- playtime (minutes, last two weeks) and last played time

## Where it comes from

Steam's local stats cache %STEAM%\appcache\stats\UserGameStats_&lt;account>_&lt;appid>.bin with UserGameStatsSchema_&lt;appid>.bin; playtime from %STEAM%\userdata\\&lt;account>\config\localconfig.vdf (%STEAM% from HKCU\Software\Valve\Steam SteamPath)

## How to switch it on

Nothing needs switching on: the watcher reads the source as the game or platform provides it.

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

The same module also serves: [NVIDIA highlights (platform)](game-nvidia-highlights.md), [Steam Timeline (platform)](game-steam-timeline.md).

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

`achievements_total`, `achievements_unlocked`, `last_played`, `playtime_2wks_minutes`, `playtime_minutes`

A key in braces is completed at run time (`score.{team}` is one key per team). Keys the code takes from a table of the game's fields or from the game's own stat names are not in this list; "What is recorded" above names them.

## Verified

decoded all real stats files and schemas on this machine (local test); change detection tested on files built in the binary KeyValues format

## Source

[heat3d_watch/adapters/platform.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/platform.py)

*Generated from the adapter by `tools/gen_game_pages.py`; change the adapter and run it again rather than editing this page.*
