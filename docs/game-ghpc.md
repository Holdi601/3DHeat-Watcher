---
title: "Gunner, HEAT, PC! (log files)"
parent: Games
nav_order: 25
---

# Gunner, HEAT, PC! (log files)

While you play Gunner, HEAT, PC!, the watcher reads the files the game writes and saves what happened, so you can look at it later on a map in the 3DHeat viewer.

*Technical details: adapter `ghpc`, kind [`log`](sources-and-rules.md); it runs all the time (it does not wait for a game to start) and looks for new data every 5 s.*

## What is recorded

- every unit's position, heading, pitch, roll and speed 10 times a second (1 a second while it stands still), its turret's traverse and gun's elevation, side, vehicle and crew
- every round fired: shooter, weapon, ammunition, calibre, muzzle velocity, and where it ended
- hits: the unit struck, the point on it and the round's way in its own frame, the plate, the impact angle and speed, penetrated or not, further plates and fragments
- what hits did: crew knocked out, parts destroyed, fires, ammunition going up, units out of the fight and who did it; the game's own account of each shot
- the mission, its map, its states, how it ended and how long it took; the game's log lines

## Where it comes from

the 3DHeat recorder, a MelonLoader mod (mods/ghpc) the player installs: one .3dheat file a mission in %LOCALAPPDATA%/3DHeat/Watcher/recorders/ghpc, which the viewer opens directly

## How to switch it on

install MelonLoader (github.com/LavaGang/MelonLoader/releases) and start the game once, then `python -m heat3d_watch setup ghpc --apply` puts the recorder in

Type the command in a terminal opened in the watcher's folder (see [Before you start](before-you-start.md)). If it fails, the last line says why; [Installing and running](installing-and-running.md) covers the usual causes.

`python -m heat3d_watch setup ghpc` lists the files it would change; `python -m heat3d_watch setup ghpc --apply` changes them, keeping the original as `<file>.heat3d-backup` (see [Commands](commands.md#setup)). It prints `ghpc: changed: ...` for each change, or `ghpc: nothing to change` when it is already on.

## How it works

Gunner, HEAT, PC!: the missions the 3DHeat recorder mod writes.

The game keeps no replays and publishes no telemetry. The recorder (a
MelonLoader mod, `mods/ghpc`, installed with `setup ghpc --apply` or
`ghpc install`) writes each mission into one `.3dheat` file in
`%LOCALAPPDATA%/3DHeat/Watcher/recorders/ghpc`; the viewer opens those files
as they are. This adapter watches that folder and files each new mission as a
session: the file linked (or copied) into the session folder, its numbers into
the statistics.

## Positions and axes

| | |
|---|---|
| Positions recorded | yes |
| Up axis | `y` |
| Units | metres (x east, y up, z north) |
| Mirrored for the viewer | `z` |
| Unit scale (`scale`: the viewer multiplies positions by it) | 1 |

These go into each session's `meta.json` (`axes`) and, when the session has positions, into `heat.parquet`'s footer, so the 3DHeat viewer turns and scales the rows by itself - see [The data](the-data.md).

## Multiplayer

- Marked as played online (`multiplayer`): **no**. `games --markdown` shows this as "single-player".
- Kind `log`: it reads only what the game or platform hands out (files the game writes while it runs), so it records in online play as well as offline; the flag decides only whether memory may ever be read.
- Memory: **never** read by this adapter. Only `memory` adapters read memory, and never for a game marked as played online - see [Sources and rules](sources-and-rules.md).

## Statistics recorded

No statistic key is set by name in the code; "What is recorded" above says what is counted.

## Completeness

The watcher follows 3DHeat's [converter rule](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md): what the source holds is read or kept, never dropped. Besides the rows, every packet, page, line or reply the adapter receives is kept whole in the session's `heat.raw.parquet` (columns `time`, `ms`, `type`, `used`, `payload`, `text`, then any field kept by name; `used` marks what also became rows), and `meta.json`'s `selfCheck.completeness` counts each `type` - `lost` is 0.

**Read**

- units
- samples
- rounds fired
- hits and plates
- damage
- kills
- mission states
- result

**Kept raw**

- every line of the game's log while a mission runs, in the file's raw sidecar (a line said more than 20 times is counted)

**Not available**

- what the game does not expose to a mod at the names the recorder knows: those parts stay empty, and the probe in each file lists them

**Size**: about 20 bytes a sample: some 15 MB for half an hour with 40 units

## Verified

the file format by tests (a synthetic mission written by the mod's own writer, read by pyarrow and the viewer); the mod has not run in the game yet, and the names it reads in the game are taken from public mods, so its first run writes a probe of what it found

## Source

[heat3d_watch/adapters/ghpc.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/ghpc.py)

<!-- Generated from the adapter by tools/gen_game_pages.py; change the adapter and run it again rather than editing this page. -->
