---
title: "Path of Exile (log)"
parent: Games
nav_order: 36
---

# Path of Exile (log)

Adapter `poe` - kind [`log`](sources-and-rules.md) - runs while `PathOfExile.exe`, `PathOfExile_x64.exe`, `PathOfExileSteam.exe`, `PathOfExile_x64Steam.exe`, `PathOfExileEGS.exe`, `PathOfExile_x64EGS.exe`, `PathOfExile_KG.exe` or `PathOfExile_x64_KG.exe` is running - looks for new data every 0.5 s.

## What is recorded

- zones entered with area level
- level-ups with class and level
- deaths ("has been slain")
- players joining and leaving the area, whispers in and out, trade requests, trades accepted
- deaths, levels gained, highest level, zones entered, distinct zones, whispers, trade requests, trades

## Where it comes from

&lt;install>\logs\Client.txt of Path of Exile or Path of Exile 2 (followed; the install folder is the running executable's)

## How to switch it on

Nothing needs switching on: the watcher reads the source as the game or platform provides it.

## How it works

Path of Exile and Path of Exile 2: the client log, `<install>\logs\Client.txt`.

Both games append to one Client.txt in their install folder for as long as
they are installed (it grows across launches). Lines look like

```text
2024/01/01 12:00:00 123456789 cff94598 [INFO Client 1234] : You have entered Lioneye's Watch.
2024/01/01 12:00:00 123456789 cff94598 [DEBUG Client 1234] Generating level 2 area "1_1_2" with seed 1
2024/01/01 12:00:00 123456789 cff94598 [INFO Client 1234] : Name (Witch) is now level 2
2024/01/01 12:00:00 123456789 cff94598 [INFO Client 1234] : Name has been slain.
2024/01/01 12:00:00 123456789 cff94598 [INFO Client 1234] @From Name: Hi, I would like to buy your ...
```

- local time, a millisecond counter, a hash, the level and thread, then what the
  chat window shows. The messages are the English client's; another language's
  client writes them translated and is not understood here. Nothing gives a
  position. The format is not documented by Grinding Gear Games; it is the
  game's plain-text log, as community tools (trade helpers, level guides) have
  read it for years - e.g. <https://github.com/klayveR/poe-log-monitor> (MIT) for
  the event list.

The install folder is the running executable's; without one the Steam
libraries and the standalone client's default folder are searched.

## Positions and axes

| | |
|---|---|
| Positions recorded | no |
| Up axis | `y` |
| Units | no positions recorded |
| Mirrored for the viewer | none |
| Unit scale (`scale`: the viewer multiplies positions by it) | 1 |

These go into each session's `meta.json` (`axes`) and, when the session has positions, into `heat.parquet`'s footer, so the 3DHeat viewer turns and scales the rows by itself - see [The data](the-data.md).

## Multiplayer

- Marked as played online (`multiplayer`): **yes**. `games --markdown` shows this as "allowed (reads only what the game publishes)".
- Kind `log`: it reads only what the game or platform hands out (files the game writes while it runs), so it records in online play as well as offline; the flag decides only whether memory may ever be read.
- Memory: **never** read by this adapter. Only `memory` adapters read memory, and never for a game marked as played online - see [Sources and rules](sources-and-rules.md).

## Statistics recorded

Statistic keys this adapter's code sets by name (each session's `stats` in `meta.json` and the `stats` table of `watcher.sqlite`):

`bad_lines`, `character_class`, `deaths`, `level`, `levels_gained`, `trade_requests_received`, `trade_requests_sent`, `trades`, `whispers`, `zones_distinct`, `zones_entered`

A key in braces is completed at run time (`score.{team}` is one key per team). Keys the code takes from a table of the game's fields or from the game's own stat names are not in this list; "What is recorded" above names them.

## Verified

tested on synthetic Client.txt lines in the game's format; untested against the game

## Source

[heat3d_watch/adapters/poe.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/poe.py)

*Generated from the adapter by `tools/gen_game_pages.py`; change the adapter and run it again rather than editing this page.*
