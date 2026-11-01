---
title: "Star Citizen (log)"
parent: Games
nav_order: 40
---

# Star Citizen (log)

Adapter `starcitizen` - kind [`log`](sources-and-rules.md) - runs while `StarCitizen.exe` is running - looks for new data every 0.5 s.

## What is recorded

- deaths with victim, killer, weapon, damage type and zone (players and NPCs)
- vehicles disabled and destroyed, with driver, cause and zone
- quantum travel targets, solar system changes, spawns, respawns, incapacitations
- kills (player and NPC), deaths, suicides, vehicles destroyed and lost, quantum jumps

## Where it comes from

&lt;install>\StarCitizen\LIVE\Game.log (the build folder of the running StarCitizen.exe), only the log file the game writes - an Easy Anti-Cheat game: nothing touches its process

## How to switch it on

Nothing needs switching on: the watcher reads the source as the game or platform provides it.

## How it works

Star Citizen: the client's own log, `<install>\StarCitizen\LIVE\Game.log`.

The game writes Game.log afresh at each launch (the previous one goes to
`logbackups\`). Only that file is read: Star Citizen runs Easy Anti-Cheat, and
nothing here goes near the game's process. Lines start with a UTC timestamp and
a level, then a tag in angle brackets:

```text
<2025-04-13T17:17:51.279Z> [Notice] <Actor Death> CActor::Kill: 'Victim' [200146297631] in zone
    'ANVL_Hornet_F7A_Mk2_2677329226210' killed by 'Killer' [202061381370] using
    'GATS_BallisticGatling_S3_2677329225797' [Class unknown] with damage type 'VehicleDestruction'
    from direction x: 0.000000, y: 0.000000, z: 0.000000 [Team_ActorTech][Actor]
<...> [Notice] <Vehicle Destruction> CVehicle::OnAdvanceDestroyLevel: Vehicle 'ANVL_Arrow_123' [123] in zone
    'OOC_Stanton_1_Hurston' [pos x: 1.0, y: 2.0, z: 3.0 vel x: 0, y: 0, z: 0] driven by 'Driver' [456]
    advanced from destroy level 0 to 2 caused by 'Attacker' [789] with 'Combat' [Team_VehicleFeatures][Vehicle]
<...> [Notice] <AccountLoginCharacterStatus_Character> Character: createdAt 1 - updatedAt 2 - geid 3 -
    accountId 4 - name Handle - state STATE_CURRENT [Team_GameServices][Login]
<...> [Notice] <Quantum Navtarget> CSCItemQuantumDrive::RmMulticastOnQTToPoint : Local client user
    Handle[200000000001] received QT data for Entity:AEGS_Gladius_123[123] to Target Stanton1b ...
<...> [Notice] <Changing Solar System> ... Client entity Handle ... changing system from Stanton to Pyro ...
```

(wrapped here; one line each in the file). The zone of a death is usually the
ship the victim sat in, not a place. The format is not documented by Cloud
Imperium and changes between patches; the patterns follow the lines community
kill trackers read (e.g. <https://github.com/DimmaDont/all-slain>, MIT - facts
only), and anything that does not match is skipped, not guessed. A vehicle's
`pos` is zone-relative and kept only as text: no coordinates are drawn.

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

`bad_lines`, `deaths`, `incapacitations`, `kills`, `npc_kills`, `player_kills`, `quantum_jumps`, `suicides`, `system_jumps`, `vehicles_destroyed`, `vehicles_lost`

A key in braces is completed at run time (`score.{team}` is one key per team). Keys the code takes from a table of the game's fields or from the game's own stat names are not in this list; "What is recorded" above names them.

## Verified

tested on synthetic Game.log lines in the format community trackers document; untested against the game

## Source

[heat3d_watch/adapters/starcitizen.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/starcitizen.py)

*Generated from the adapter by `tools/gen_game_pages.py`; change the adapter and run it again rather than editing this page.*
