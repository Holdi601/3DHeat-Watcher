---
title: "EVE Online (log)"
parent: Games
nav_order: 19
---

# EVE Online (log)

Adapter `eve` - kind [`log`](sources-and-rules.md) - runs while `exefile.exe` is running - looks for new data every 0.5 s.

## What is recorded

- damage dealt and received with the other ship, pilot, weapon and hit quality
- misses dealt and received
- bounties paid (NPC kills) with ISK
- jumps between systems
- damage dealt and received, hits, misses, bounty kills and ISK, jumps

## Where it comes from

%USERPROFILE%\Documents\EVE\logs\Gamelogs\\\*.txt (every file written since the client started)

## How to switch it on

Nothing needs switching on: the watcher reads the source as the game or platform provides it.

## How it works

EVE Online: the client's game logs, `Documents\EVE\logs\Gamelogs\*.txt`.

The client writes one file per character per login,
`<yyyymmdd>_<hhmmss>[_<character id>].txt`; logging to file is on by default. Several clients running side by
side each write their own, so every file written since the game started is
followed. Header and lines (EVE time is UTC):

```text
------------------------------------------------------------
  Gamelog
  Listener: Character Name
  Session Started: 2024.07.02 19:41:40
------------------------------------------------------------
[ 2024.07.02 20:31:28 ] (combat) <color=0xff00ffff><b>200</b> <color=0x77ffffff><font size=10>to</font>
    <b><color=0xffffffff>Pilot[TICK](Ship)</b><font size=10><color=0x77ffffff> - Weapon - Penetrates
[ 2024.06.25 15:20:01 ] (combat) <color=0xffcc0000><b>375</b> ... from ... - Weapon - Hits
[ 2024.06.25 15:21:00 ] (bounty) <font size=12><b><color=0xff00aa00>15,000 ISK</b> added to next bounty payout
[ 2024.06.25 15:30:00 ] (None) Jumping from System A to System B
```

(the combat line is one line in the file). Formatting tags are stripped before
matching. The file has been UTF-8 and UTF-16 over the years; both are read.
The format is not documented by CCP; it is the client's plain-text log, read as
community combat-log tools read it (e.g. <https://docs.rs/crate/eve-log-parser>).
No positions.

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

`bad_lines`, `bounty_isk`, `bounty_kills`, `damage_dealt`, `damage_received`, `hits_dealt`, `hits_received`, `jumps`, `misses_dealt`, `misses_received`

A key in braces is completed at run time (`score.{team}` is one key per team). Keys the code takes from a table of the game's fields or from the game's own stat names are not in this list; "What is recorded" above names them.

## Verified

tested on synthetic gamelog lines in the format published by community parsers; untested against the game

## Source

[heat3d_watch/adapters/eve.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/eve.py)

*Generated from the adapter by `tools/gen_game_pages.py`; change the adapter and run it again rather than editing this page.*
