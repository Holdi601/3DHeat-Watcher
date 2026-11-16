---
title: "VALORANT (replays)"
parent: Games
nav_order: 44
---

# VALORANT (replays)

After a match of VALORANT, the watcher turns the replay the game saved into files you can look at as statistics and a timeline.

*Technical details: adapter `valorant-replays`, kind [`replay`](sources-and-rules.md); it runs all the time (it does not wait for a game to start) and looks for new data every 5 s.*

## What is recorded

- the map, the match id and the agents picked; the replay's info block (length, versions, name, recording time, compression and encryption flags)
- the server's event timeline: kills (killer and victim as network ids), rounds starting, spikes planted, defused and exploding, ultimates used, sides switching - each with its id and metadata
- every chunk of the file kept whole in heat.raw.parquet; not decoded: positions, names or scores - they are in the obfuscated stream

## Where it comes from

replays VALORANT saves: %LOCALAPPDATA%/VALORANT/Saved/Demos/\*.vrf (only the parts that are not obfuscated)

## How to switch it on

save a replay in VALORANT (career > match > download replay) and install the reader: github.com/Holdi601/3DHeat-Ext-Riot (`heat3d-riot-replays`)

Settings from environment variables:

- `HEAT3D_RIOT_REPLAYS`: the reader's folder (a clone or unpacked release), when it is not installed or beside the watcher

## How it works

League of Legends and Valorant replays: what of them can be read as it is.

Both games save replays to the player's disk, and both protect what is inside:
the moment-to-moment game data is obfuscated, and differently with every patch,
to keep it from being used to cheat. That part is not decoded anywhere in
3DHeat. What each file carries in the open
is read, and the rest is kept as it is: every part of the file, whole, in the
session's `heat.raw.parquet` (3DHeat's converter rule, docs/converters.md in
the viewer's repository), counted in meta.json's `selfCheck.completeness`.

The watcher does not read the files itself: an external reader does (3DHeat
Riot, github.com/Holdi601/3DHeat-Ext-Riot, `exporters/ext/riot-replays`,
command `heat3d-riot-replays`), a project of its own. Found on PATH,
installed, or beside the watcher, it
reads each new replay; missing, the watcher says once how to install it. What
it reads, the watcher records into the session; the Match-V5 timeline below is
fetched by the watcher itself, as it is not in the file.

#### Valorant (.vrf)

`%LOCALAPPDATA%\VALORANT\Saved\Demos\*.vrf`, an Unreal Engine local replay. In the open:
the replay's info block (length, network version, changelist, its name, when it
was recorded, whether it is compressed or encrypted), the map, the match id and
the agents picked (in the header), and the server's own event timeline - kills
(killer and victim as network ids, not names), rounds starting, spikes planted,
defused and exploding, ultimates used, sides switching - each with its time,
id and metadata. Positions, names, scores and everything else are in the
obfuscated stream (the replay data and checkpoint chunks), which is kept whole
and not read.

The same module also serves: [League of Legends (replays)](game-lol-replays.md).

## Positions and axes

| | |
|---|---|
| Positions recorded | no |
| Up axis | `z` |
| Units | VALORANT world units |
| Mirrored for the viewer | none |
| Unit scale (`scale`: the viewer multiplies positions by it) | 1 |

These go into each session's `meta.json` (`axes`) and, when the session has positions, into `heat.parquet`'s footer, so the 3DHeat viewer turns and scales the rows by itself - see [The data](the-data.md).

## Multiplayer

- Marked as played online (`multiplayer`): **yes**. `games --markdown` shows this as "allowed (reads only what the game publishes)".
- Kind `replay`: it reads only what the game or platform hands out (replays and demos the game saves), so it records in online play as well as offline; the flag decides only whether memory may ever be read.
- Memory: **never** read by this adapter. Only `memory` adapters read memory, and never for a game marked as played online - see [Sources and rules](sources-and-rules.md).

## Statistics recorded

Statistic keys this adapter's code sets by name (each session's `stats` in `meta.json` and the `stats` table of `watcher.sqlite`):

`kills_in_match`, `map`, `match_seconds`, `rounds`, `spikes_planted`

A key in braces is completed at run time (`score.{team}` is one key per team). Keys the code takes from a table of the game's fields or from the game's own stat names are not in this list; "What is recorded" above names them.

## Completeness

The watcher follows 3DHeat's [converter rule](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md): what the source holds is read or kept, never dropped. Besides the rows, every packet, page, line or reply the adapter receives is kept whole in the session's `heat.raw.parquet` (columns `time`, `ms`, `type`, `used`, `payload`, `text`, then any field kept by name; `used` marks what also became rows), and `meta.json`'s `selfCheck.completeness` counts each `type` - `lost` is 0.

**Read**

- the info block, every field (meta.json `vrf`): file version, custom versions, length, network version, changelist, name, live flag, recording time, compressed and encrypted flags, the key as stored
- the header chunk: the map, the match id and the agents picked (looked up by their form)
- every event chunk: id, group, metadata, start and end time, and of its data the event's name, its time in seconds and the numbers before it (killer and victim network ids) - a row each

**Kept raw**

- every chunk whole, in file order (`offset`), so the parts are the file: `info`, `header`, `event <group>`, `replay_data`, `checkpoint`, `chunk <n>` for a type the layout does not name, `trailing` for bytes after the last whole chunk

**Not available**

- positions, names, scores, abilities, every frame of the game: the replay data and checkpoint chunks are obfuscated. Kept whole, not read
- an encrypted replay's contents: walked and kept whole, nothing read inside

**Size**: the raw sidecar is about the replay's own size: the obfuscated stream does not compress

## Verified

the reader (heat3d-riot-replays) is built from the container layout documented by vrfkit (Apache-2.0); untested on a real replay, none was available - checks before reading and skips what does not match

## Source

[heat3d_watch/adapters/riot_replays.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/riot_replays.py)

<!-- Generated from the adapter by tools/gen_game_pages.py; change the adapter and run it again rather than editing this page. -->
