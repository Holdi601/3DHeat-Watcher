
# Minecraft (log)

Adapter `minecraft` - kind [`log`](sources-and-rules) - runs while `javaw.exe` or `java.exe` is running - looks for new data every 0.5 s.

## What is recorded

- own and other players' position (blocks = m, y up) each time the world saves, dimension as session
- spawn with position when a player logs in to the (integrated) server
- joins, leaves, deaths with the death message, advancements, chat lines
- deaths, advancements, chat messages; from the stats file: play time, distance, mob and player kills, jumps, damage, blocks mined, items crafted (this session's share)

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

Coordinates are blocks, one block a metre, y up; x east, z south - a right-
handed frame, drawn as it is. Positions come only when the world saves, so a
route is a few points per autosave, not a trail; the dimension is the
`session`, so the Nether is not drawn over the Overworld.

## Positions and axes

| | |
|---|---|
| Positions recorded | yes |
| Up axis | `y` |
| Units | blocks (1 block = 1 m) |
| Mirrored for the viewer | none |
| Unit scale (`scale`: the viewer multiplies positions by it) | 1 |

These go into each session's `meta.json` (`axes`) and, when the session has positions, into `heat.parquet`'s footer, so the 3DHeat viewer turns and scales the rows by itself - see [The data](the-data).

## Multiplayer

- Marked as played online (`multiplayer`): **yes**. `games --markdown` shows this as "allowed (reads only what the game publishes)".
- Kind `log`: it reads only what the game or platform hands out (files the game writes while it runs), so it records in online play as well as offline; the flag decides only whether memory may ever be read.
- Memory: **never** read by this adapter. Only `memory` adapters read memory, and never for a game marked as played online - see [Sources and rules](sources-and-rules).

## Statistics recorded

Statistic keys this adapter's code sets by name (each session's `stats` in `meta.json` and the `stats` table of `watcher.sqlite`):

`advancements`, `bad_files`, `bad_lines`, `chat_messages`, `deaths`, `joins`, `others_deaths`, `world`

A key in braces is completed at run time (`score.{team}` is one key per team). Keys the code takes from a table of the game's fields or from the game's own stat names are not in this list; "What is recorded" above names them.

## Verified

tested on synthetic log lines, stats JSON and NBT files built from the published formats; untested against the game

## Source

[heat3d_watch/adapters/minecraft.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/minecraft.py)

*Generated from the adapter by `tools/gen_game_pages.py`; change the adapter and run it again rather than editing this page.*
