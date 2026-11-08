---
title: "League of Legends (replay)"
parent: Games
nav_order: 30
---

# League of Legends (replay)

Adapter `lol-replays` - kind [`replay`](sources-and-rules.md) - runs always on (it does not wait for a game to start) - looks for new data every 5 s.

## What is recorded

- each player's champion, role, team, kills, deaths, assists, gold, damage to champions and result, and every other number of the end-of-game box score
- your own line as statistics, and your rows named as yours (meta.json `player`), with your Riot ID in the settings
- with your own Riot API key: every player's position each minute with the minute's statistics, and every event of the timeline (kills where they happened, buildings, monsters, wards, items, skills), at the wall-clock time the timeline gives
- every part of the replay file kept whole in heat.raw.parquet; not decoded: the moment-to-moment game, which is encrypted and obfuscated against cheating

## Where it comes from

replays the League client saves: %USERPROFILE%/Documents/League of Legends/Replays/\*.rofl (the plain end-of-game metadata only); with your own Riot API key, the match's official timeline from Riot's Match-V5 API

## How to switch it on

save a replay in the League client (match history > download); for positions set riot_api_key and riot_platform with `config --set`

## How it works

League of Legends and Valorant replays: what of them can be read as it is.

Both games save replays to the player's disk, and both protect what is inside:
the moment-to-moment game data is obfuscated, and differently with every patch,
to keep it from being used to cheat. Getting through that means taking the
game's own code apart, which Riot's terms forbid (Terms of Service 3.1 and 7.1)
- so it is not done here. What each file carries in the open is read, and
the rest is kept as it is: every part of the file, whole, in the session's
`heat.raw.parquet` (3DHeat's converter rule, docs/converters.md in the
viewer's repository), counted in meta.json's `selfCheck.completeness`.

#### League of Legends (.rofl)

`%USERPROFILE%\Documents\League of Legends\Replays\*.rofl`. Both container
versions carry the end-of-game box score as plain JSON (`statsJson`): for each
of the ten players the champion, kills, deaths, assists, gold, damage to
champions, items, team, role, win, their Riot ID, and every other number the
game totals (over a hundred per player); all of them become the player's
`player_result` row. ROFL1 (patch 14.9 and before) has it after a fixed header
(`RIOT\0\0`, a 256-byte signature, then the lengths); ROFL2 (14.11 on,
`RIOT\2\0`) at the end of the file, its length in the last four bytes (stated
by a Riot engineer, ReplayBook issue 299). ROFL1's payload header (game id,
length, chunk and keyframe counts, the chunk key's length) and its table of
chunks (id, type, length, next chunk, offset) are in the open and read; the
chunks themselves are encrypted, and kept whole unread. Layouts from
roflxd.cs (MIT).

Positions do not come from the file. With a Riot developer key of the player's
own (`riot_api_key` in the settings; a personal key is meant for exactly this,
"showing (self) player stats"), the match's official timeline is fetched from
Riot's Match-V5 API: every player's position once a minute with everything the
minute's frame says of them (gold, experience, level, minions, champion and
damage statistics), and every event of the timeline - kills, buildings, elite
monsters, wards, items, skills, levels - each a row, where it happened when it
has a place. Without a key nothing is fetched and nothing is sent.

#### Valorant (.vrf)

`%LOCALAPPDATA%\VALORANT\Saved\Demos\*.vrf`, an Unreal Engine local replay
(layout from vrfkit, Apache-2.0, and ValorantReplayParser, MIT). In the open:
the replay's info block (length, network version, changelist, its name, when it
was recorded, whether it is compressed or encrypted), the map, the match id and
the agents picked (in the header), and the server's own event timeline - kills
(killer and victim as network ids, not names), rounds starting, spikes planted,
defused and exploding, ultimates used, sides switching - each with its time,
id and metadata. Positions, names, scores and everything else are in the
obfuscated stream (the replay data and checkpoint chunks), which is kept whole
and not read.

The same module also serves: [VALORANT (replay)](game-valorant-replays.md).

## Positions and axes

| | |
|---|---|
| Positions recorded | yes |
| Up axis | `y` |
| Units | Summoner's Rift map units (about 15000 across) |
| Mirrored for the viewer | none |
| Unit scale (`scale`: the viewer multiplies positions by it) | 1 |

These go into each session's `meta.json` (`axes`) and, when the session has positions, into `heat.parquet`'s footer, so the 3DHeat viewer turns and scales the rows by itself - see [The data](the-data.md).

## Multiplayer

- Marked as played online (`multiplayer`): **yes**. `games --markdown` shows this as "allowed (reads only what the game publishes)".
- Kind `replay`: it reads only what the game or platform hands out (replays and demos the game saves), so it records in online play as well as offline; the flag decides only whether memory may ever be read.
- Memory: **never** read by this adapter. Only `memory` adapters read memory, and never for a game marked as played online - see [Sources and rules](sources-and-rules.md).

## Statistics recorded

Statistic keys this adapter's code sets by name (each session's `stats` in `meta.json` and the `stats` table of `watcher.sqlite`):

`champion`, `game_seconds`, `won`

A key in braces is completed at run time (`score.{team}` is one key per team). Keys the code takes from a table of the game's fields or from the game's own stat names are not in this list; "What is recorded" above names them.

## Completeness

The watcher follows 3DHeat's [converter rule](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md): what the source holds is read or kept, never dropped. Besides the rows, every packet, page, line or reply the adapter receives is kept whole in the session's `heat.raw.parquet` (columns `time`, `ms`, `type`, `used`, `payload`, `text`, then any field kept by name; `used` marks what also became rows), and `meta.json`'s `selfCheck.completeness` counts each `type` - `lost` is 0.

**Read**

- the metadata JSON: game length, version, last chunk and keyframe ids, and `statsJson` - every field of every player's box score on their `player_result` row (numbers given as text read as numbers)
- ROFL1: the lengths block, the payload header (game id, game length, keyframe and chunk counts, startup and game start chunk ids, keyframe interval, the chunk key as it is stored) and the chunk table (id, type, length, next chunk, offset) - in meta.json `rofl` and the raw rows' `text`
- ROFL2: the version string
- the Match-V5 timeline (own API key only): every participant frame on a `position` row (or `participant_frame` without a place) with all its fields flattened (`championStats.armor`, `damageStats.totalDamageDone`, `currentGold`, `xp`, ...); every event as a row named after its type, placed where it has a `position`, CHAMPION_KILL as a kill and a death

**Kept raw**

- every part of the .rofl, whole, in file order (`offset`), so the parts are the file: `magic`, `signature`, `lengths`, `metadata`, `payload_header`, `chunk_header`, `chunk`, `keyframe` (ROFL1); `body`, `metadata`, `metadata_length` (ROFL2); any stretch no part covers as `unknown`
- the timeline whole: `timeline <type>` for each event, `timeline participantFrame` for each player's frame (`participant` its id), `timeline` for the rest

**Not available**

- the game itself (positions, abilities, every unit, moment to moment): ROFL1's chunks and ROFL2's body are encrypted and the packets inside obfuscated with every patch; getting through means taking the client apart, which Riot's terms forbid (3.1, 7.1). Kept whole, not read
- positions without your own Riot API key: the file has none in the open

**Size**: the raw sidecar is about the replay's own size: the encrypted chunks do not compress

## Verified

the metadata reader tested on files built to the layouts in roflxd.cs (MIT); the timeline on Match-V5's documented JSON; no real replay was available to check against

## Source

[heat3d_watch/adapters/riot_replays.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/riot_replays.py)

*Generated from the adapter by `tools/gen_game_pages.py`; change the adapter and run it again rather than editing this page.*
