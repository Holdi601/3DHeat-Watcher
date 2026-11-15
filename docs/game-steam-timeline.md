---
title: "Steam Timeline (platform)"
parent: Games
nav_order: 43
---

# Steam Timeline (platform)

The watcher saves what Steam Timeline keeps about your games, so you can look at your history later as statistics and a timeline.

*Technical details: adapter `steam-timeline`, kind [`platform`](sources-and-rules.md); it runs all the time (it does not wait for a game to start) and looks for new data every 10 s.*

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

## Completeness

The watcher follows 3DHeat's [converter rule](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md): what the source holds is read or kept, never dropped. Besides the rows, every packet, page, line or reply the adapter receives is kept whole in the session's `heat.raw.parquet` (columns `time`, `ms`, `type`, `used`, `payload`, `text`, then any field kept by name; `used` marks what also became rows), and `meta.json`'s `selfCheck.completeness` counts each `type` - `lost` is 0.

**Read**

- every entry once, as a row at its time: its type, every plain field (title, description, icon, priority, duration, possible_clip, achievement name, mode, ...), a phase's tags by group, the achievement's display name from the stats schema; the file's start and end

**Kept raw**

- every entry whole as JSON under Steam's own `type` (`gamemode`, `achievement`, `event`, `state_description`, `phase`, `error`, any other): nested fields - a tag's icon and priority, anything a later Steam adds - are only here
- `timeline`: the file's own fields (daterecorded, starttime, endtime, any other), when the session opens and again when they change

**Not available**

- the recording itself (video): Steam keeps it in its own folders; the session refers to the timeline file by name
- a read of a file Steam is writing that cannot be parsed even with its end closed: counted (`bad` in the adapter's state) and read again at the next change, where its entries are taken

**Size**: a few hundred entries of 100-300 bytes per hour of play: well under 1 MB per hour

## Verified

tested on real timeline files from a local install: achievement, gamemode, error, and games' own event, state_description and phase entries; the file format itself is undocumented

## Source

[heat3d_watch/adapters/platform.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/platform.py)

<!-- Generated from the adapter by tools/gen_game_pages.py; change the adapter and run it again rather than editing this page. -->
