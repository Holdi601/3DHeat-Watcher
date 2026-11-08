---
title: "Minecraft (log)"
parent: Games
nav_order: 33
---

# Minecraft (log)

Adapter `minecraft` - kind [`log`](sources-and-rules.md) - runs while `javaw.exe` or `java.exe` is running - looks for new data every 0.5 s.

## What is recorded

- own and other players' position (blocks = m, y up) each time the world saves, dimension as session
- spawn with position when a player logs in to the (integrated) server
- joins, leaves, deaths with the death message, advancements, chat lines
- deaths, advancements, chat messages; from the stats file: play time, distance, mob and player kills, jumps, damage, blocks mined, items crafted (this session's share)
- every log line and every saved stats, advancements and player file whole in heat.raw.parquet

## Where it comes from

%APPDATA%\\.minecraft\logs\latest.log (followed), saves\\&lt;world>\stats\\&lt;uuid>.json and saves\\&lt;world>\playerdata\\&lt;uuid>.dat / level.dat (gzip NBT), read when the game saves them

## How to switch it on

Nothing needs switching on: the watcher reads the source as the game or platform provides it.

## How it works

Minecraft (Java Edition): the log, statistics and player files the game writes.

Where (`%APPDATA%\.minecraft\`):

* `logs\latest.log` - the game's log, new at each launch (the old one is
  packed into a dated .log.gz). Lines `[hh:mm:ss] [thread/LEVEL]: message`
  (mod loaders write `[ddMMMyyyy hh:mm:ss.mmm] [thread/LEVEL] [logger/]: ...`).
  What players see in chat is in it: joins and leaves, death messages,
  advancements, chat - the integrated server of a single-player world writes
  the same lines once more, so a line repeated within the same second counts
  once. "Setting user: &lt;name>" names the player; the server's
  "&lt;name>[...] logged in with entity id N at (x, y, z)" gives where they
  appeared.
* `saves\<world>\stats\<uuid>.json` - the statistics screen, written when
  the world saves (autosave every few minutes, and on leaving): `stats` ->
  `minecraft:custom` (play_time in ticks, mob_kills, \*_one_cm distances, jump,
  ...), `minecraft:mined`, `minecraft:crafted`, ... Totals for the world; the
  session's figures are the difference to what the file said when the game
  started. Format: <https://minecraft.wiki/w/Statistics>
* `saves\<world>\playerdata\<uuid>.dat` (and `level.dat` -> Data -> Player
  for a single-player host) - gzip-compressed NBT, written on the same saves:
  `Pos` [x, y, z] doubles, `Rotation` [yaw, pitch], `Dimension`
  ("minecraft:overworld"; an int 0/-1/1 before 1.16). NBT per
  <https://minecraft.wiki/w/NBT_format> - read here by a small reader of our own.
* `saves\<world>\advancements\<uuid>.json` - the advancement screen's progress,
  written on the same saves.

Coordinates are blocks, one block a metre, y up; x east, z south - a right-
handed frame, drawn as it is. Positions come only when the world saves, so a
route is a few points per autosave, not a trail; the dimension is the
`session`, so the Nether is not drawn over the Overworld.

Everything read is kept whole in the session's raw sidecar (3DHeat's converter
rule): every log line under its level (`INFO`, `WARN`, `ERROR`, ...; a line
without the bracketed head, such as a stack trace, as `untagged`), and each
saved file under its kind (`stats`, `advancements`, `playerdata`,
`level.dat`) - JSON as text, NBT as its bytes. A stats file's numbers are only
understood against what it said when the game started, so that first copy is
kept too (`baseline`), the first time the file changes.

## Positions and axes

| | |
|---|---|
| Positions recorded | yes |
| Up axis | `y` |
| Units | blocks (1 block = 1 m) |
| Mirrored for the viewer | none |
| Unit scale (`scale`: the viewer multiplies positions by it) | 1 |

These go into each session's `meta.json` (`axes`) and, when the session has positions, into `heat.parquet`'s footer, so the 3DHeat viewer turns and scales the rows by itself - see [The data](the-data.md).

## Multiplayer

- Marked as played online (`multiplayer`): **yes**. `games --markdown` shows this as "allowed (reads only what the game publishes)".
- Kind `log`: it reads only what the game or platform hands out (files the game writes while it runs), so it records in online play as well as offline; the flag decides only whether memory may ever be read.
- Memory: **never** read by this adapter. Only `memory` adapters read memory, and never for a game marked as played online - see [Sources and rules](sources-and-rules.md).

## Statistics recorded

Statistic keys this adapter's code sets by name (each session's `stats` in `meta.json` and the `stats` table of `watcher.sqlite`):

`advancements`, `bad_files`, `bad_lines`, `chat_messages`, `deaths`, `joins`, `others_deaths`, `world`

A key in braces is completed at run time (`score.{team}` is one key per team). Keys the code takes from a table of the game's fields or from the game's own stat names are not in this list; "What is recorded" above names them.

## Completeness

The watcher follows 3DHeat's [converter rule](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md): what the source holds is read or kept, never dropped. Besides the rows, every packet, page, line or reply the adapter receives is kept whole in the session's `heat.raw.parquet` (columns `time`, `ms`, `type`, `used`, `payload`, `text`, then any field kept by name; `used` marks what also became rows), and `meta.json`'s `selfCheck.completeness` counts each `type` - `lost` is 0.

**Read**

- latest.log: the player's name (`Setting user`), logins with position, joins, leaves, deaths with the death message, advancements, chat lines, the server stopping
- stats/&lt;uuid>.json: play time, distance, mob and player kills, jumps, damage dealt and taken, blocks mined, items crafted - this sitting's share
- playerdata/&lt;uuid>.dat and level.dat (NBT): position, dimension, yaw, pitch, health, XP level

**Kept raw**

- every latest.log line whole, `type` = its level (`INFO`, `WARN`, `ERROR`, `DEBUG`, `FATAL`) with the logger's thread in `thread`, `used` where it became a row; a line without the bracketed head (a stack trace, a mod's banner) as `untagged`
- each stats/&lt;uuid>.json whole as text, `type` `stats` (`used`: its numbers are in the statistics), with its first copy from the game's start as `baseline`
- each advancements/&lt;uuid>.json whole as text, `type` `advancements` (every criterion and when it was met; not made into rows yet)
- each playerdata/&lt;uuid>.dat and level.dat whole as bytes (gzip NBT), `type` `playerdata` / `level.dat`, `used` where it gave a position: inventory, ender chest, effects, spawn point, game rules, world seed and time are only here
- every saved file has `world` and `file` (its path under `saves`)

**Not available**

- a position trail: the game writes the player's position only when the world saves (every few minutes and on leaving)
- positions on a server someone else hosts: its world files are on the server, not here; only the log is read then
- the world itself (region .mca files, entities, data/\*.dat maps and raids): large, and the terrain, not the play
- earlier sittings' logs (logs/\*.log.gz): kept when they were played
- Bedrock Edition: it writes no such log or files

**Size**: latest.log 0.1-2 MB per hour (more with mods); a stats file 5-50 KB and a player file 5-100 KB per autosave, level.dat 1-20 KB - about 1-5 MB per hour in all; zstd in heat.raw.parquet makes the text roughly a tenth (the NBT files are gzip already)

## Verified

tested on synthetic log lines, stats JSON and NBT files built from the published formats; untested against the game

## Source

[heat3d_watch/adapters/minecraft.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/minecraft.py)

*Generated from the adapter by `tools/gen_game_pages.py`; change the adapter and run it again rather than editing this page.*
