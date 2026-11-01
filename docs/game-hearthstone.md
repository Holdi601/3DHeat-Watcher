---
title: "Hearthstone (log)"
parent: Games
nav_order: 24
---

# Hearthstone (log)

Adapter `hearthstone` - kind [`log`](sources-and-rules.md) - runs while `Hearthstone.exe` is running - looks for new data every 0.5 s.

## What is recorded

- game start and end, with the result (won, lost, tied), turns and the opponent's name
- each turn
- games, wins, losses, ties, turns, longest game

## Where it comes from

&lt;install>\Logs\Power.log (or Logs\Hearthstone_\*\Power.log), written once %LOCALAPPDATA%\Blizzard\Hearthstone\log.config has a [Power] section

## How to switch it on

`python -m heat3d_watch setup hearthstone --apply` adds [Power] logging to %LOCALAPPDATA%\Blizzard\Hearthstone\log.config (backup kept); restart the game

`python -m heat3d_watch setup hearthstone` lists the files it would change; `python -m heat3d_watch setup hearthstone --apply` changes them, keeping the original as `<file>.heat3d-backup` (see [Commands](commands.md#setup)).

## How it works

Hearthstone: the game's Power.log, which it writes once `log.config` asks for it.

Hearthstone reads `%LOCALAPPDATA%\Blizzard\Hearthstone\log.config` at launch;
a `[Power]` section with `LogLevel=1` and `FilePrinting=true` makes it write
every game's state changes to `<install>\Logs\Power.log` (newer clients put
each launch's logs in a folder of their own, `Logs\Hearthstone_<date>\`). This
is the documented debug logging deck trackers have switched on since 2014
(Hearthstone Deck Tracker's setup writes the same section). `setup()` adds the
section, with a backup of the file as it was; the game needs a restart to read it.

The lines used, all from `GameState.DebugPrintPower()` (the `PowerTaskList`
lines repeat them and are skipped):

```text
D 20:15:01.1234567 GameState.DebugPrintPower() - CREATE_GAME
D 20:15:01.1234567 GameState.DebugPrintPower() -     Player EntityID=2 PlayerID=1 GameAccountId=[hi=1 lo=2]
D 20:15:01.1234567 GameState.DebugPrintGame() - PlayerID=1, PlayerName=Name#1234
D 20:15:02.1234567 GameState.DebugPrintPower() -     FULL_ENTITY - Updating [entityName=... id=4 zone=HAND
                   zonePos=0 cardId=CS2_029 player=1] CardID=CS2_029
D 20:16:00.1234567 GameState.DebugPrintPower() - TAG_CHANGE Entity=GameEntity tag=TURN value=3
D 20:25:00.1234567 GameState.DebugPrintPower() - TAG_CHANGE Entity=Name#1234 tag=PLAYSTATE value=WON
D 20:25:00.1234567 GameState.DebugPrintPower() - TAG_CHANGE Entity=GameEntity tag=STATE value=COMPLETE
```

The player's own side is the one whose starting hand has its cards named
(the opponent's are hidden), else the side that is not the AI (account 0) or
"UNKNOWN HUMAN PLAYER". Lines carry only the time of day; the date is today's.
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

`bad_lines`, `games`, `longest_game_turns`, `losses`, `ties`, `turns`, `wins`

A key in braces is completed at run time (`score.{team}` is one key per team). Keys the code takes from a table of the game's fields or from the game's own stat names are not in this list; "What is recorded" above names them.

## Verified

tested on synthetic Power.log lines in the game's format; untested against the game

## Source

[heat3d_watch/adapters/hearthstone.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/hearthstone.py)

*Generated from the adapter by `tools/gen_game_pages.py`; change the adapter and run it again rather than editing this page.*
