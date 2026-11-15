---
title: "Steam statistics (platform)"
parent: Games
nav_order: 42
---

# Steam statistics (platform)

The watcher saves what Steam statistics keeps about your games, so you can look at your history later as statistics and a timeline.

*Technical details: adapter `steam-stats`, kind [`platform`](sources-and-rules.md); it runs all the time (it does not wait for a game to start) and looks for new data every 30 s.*

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

## Completeness

The watcher follows 3DHeat's [converter rule](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md): what the source holds is read or kept, never dropped. Besides the rows, every packet, page, line or reply the adapter receives is kept whole in the session's `heat.raw.parquet` (columns `time`, `ms`, `type`, `used`, `payload`, `text`, then any field kept by name; `used` marks what also became rows), and `meta.json`'s `selfCheck.completeness` counts each `type` - `lost` is 0.

**Read**

- every stat of the stats file by its API name (int, float, avgrate), every achievement bit with its unlock time, named and described by the schema
- changes against the last read (old, new, difference), new unlocks; playtime, two-week playtime and last played from localconfig.vdf

**Kept raw**

- `UserGameStats`: the stats file's bytes, whole, each time it is recorded (the `crc`, `PendingChanges`, achievement bits the schema no longer defines and any key the decoder skips are in it)
- `UserGameStatsSchema`: the schema file's bytes beside it, so the stats can be decoded from the session alone (every stat's and achievement's names in every language, icons, flags)
- `localconfig_app`: the game's whole block of localconfig.vdf as JSON (cloud sync state, launch options, badges and every other key Steam keeps per game) when its playtime is recorded
- a stats file the decoder cannot read (cut mid-write, or a new layout): its bytes and the schema in a session without rows (`used` false; `unreadable` in meta.json)

**Not available**

- the rest of localconfig.vdf (friends, chat, Steam settings): not the game's, and private
- stat values between two writes: Steam rewrites the file when the game stores its stats, usually when it closes
- global achievement percentages and other players' stats: they are on Steam's servers, not here

**Size**: a few KB per recorded sitting, plus the schema (up to a few hundred KB for a game with many achievements) - well under 1 MB per hour of play; zstd shrinks the schema's text by half or more

## Verified

tested on real stats files and schemas from a local install; change detection tested on files built in the binary KeyValues format

## Source

[heat3d_watch/adapters/platform.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/platform.py)

<!-- Generated from the adapter by tools/gen_game_pages.py; change the adapter and run it again rather than editing this page. -->
