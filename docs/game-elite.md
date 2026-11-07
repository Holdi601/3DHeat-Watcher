---
title: "Elite Dangerous (log)"
parent: Games
nav_order: 18
---

# Elite Dangerous (log)

Adapter `elite` - kind [`log`](sources-and-rules.md) - runs while `EliteDangerous64.exe` is running - looks for new data every 0.25 s.

## What is recorded

- every journal event, under its journal name, with its plain fields
- galaxy position (StarPos, light years) on jumps, locations, spawns, deaths, docking, landing
- spawn on LoadGame/Resurrect, death on Died, docked/undocked, touchdown/liftoff, jump, session_end
- planet surface route from Status.json: latitude, longitude, altitude, heading, and metres in a tangent plane per body (session = body name)
- jumps, distance jumped, deaths, kills, credits earned, missions completed, bodies scanned, systems visited, dockings, landings

## Where it comes from

Player Journal %USERPROFILE%\Saved Games\Frontier Developments\Elite Dangerous\Journal.\*.log (newest file, followed as it is written) and Status.json in the same folder

## How to switch it on

Nothing needs switching on: the watcher reads the source as the game or platform provides it.

## How it works

Elite Dangerous: the Player Journal and Status.json the game writes while it runs.

Where: `%USERPROFILE%\Saved Games\Frontier Developments\Elite Dangerous\`

* `Journal.<yyyy-mm-ddThhmmss>.<part>.log` - one JSON object per line, one
  file per launch (a long session continues in part .02, .03 ...). Every line
  has `timestamp` (UTC, ISO 8601) and `event`. Galaxy positions are the
  `StarPos` [x, y, z] of the system, in light years from Sol, on `FSDJump`,
  `Location` and `CarrierJump`. Elite's galactic frame is y up (towards
  galactic north), z towards the galactic core and x towards galactic longitude
  270 - a left-handed frame, so the viewer mirrors z to draw it the right way
  round.
* `Status.json` - rewritten whole whenever the ship's state changes: `Flags`,
  and near a planet `Latitude`, `Longitude` (degrees), `Altitude` (metres),
  `Heading`, `BodyName` and `PlanetRadius` (metres).

Surface positions are put into a local tangent plane per body, in metres: the
first fix on a body is its origin, x east, z north, y up (altitude), the same
handedness as the galaxy frame, and the rows carry the body's name as their
`session` so a drive or a walk on a planet draws as a route of its own. Galaxy
rows have session "galaxy". The two scales live in one table; pick the session
in the viewer.

Format: Frontier's "Elite Dangerous Player Journal" manual (published with each
update on the official forums, <https://forums.frontier.co.uk/> - "Journal Manual",
v4.x), events and fields as documented there; Status.json flags per the same
manual's "Status File" chapter.

## Positions and axes

| | |
|---|---|
| Positions recorded | yes |
| Up axis | `y` |
| Units | light years (galaxy rows, session 'galaxy'); metres east/up/north of the first fix on a body (surface rows, session = body name) |
| Mirrored for the viewer | `z` |
| Unit scale (`scale`: the viewer multiplies positions by it) | 1 |

These go into each session's `meta.json` (`axes`) and, when the session has positions, into `heat.parquet`'s footer, so the 3DHeat viewer turns and scales the rows by itself - see [The data](the-data.md).

## Multiplayer

- Marked as played online (`multiplayer`): **yes**. `games --markdown` shows this as "allowed (reads only what the game publishes)".
- Kind `log`: it reads only what the game or platform hands out (files the game writes while it runs), so it records in online play as well as offline; the flag decides only whether memory may ever be read.
- Memory: **never** read by this adapter. Only `memory` adapters read memory, and never for a game marked as played online - see [Sources and rules](sources-and-rules.md).

## Statistics recorded

Statistic keys this adapter's code sets by name (each session's `stats` in `meta.json` and the `stats` table of `watcher.sqlite`):

`bad_lines`, `bodies_scanned`, `carrier_jumps`, `credits`, `credits_earned`, `deaths`, `distance_ly`, `dockings`, `jumps`, `kills`, `landings`, `missions_completed`, `ship`, `surface_fixes`, `systems_visited`

A key in braces is completed at run time (`score.{team}` is one key per team). Keys the code takes from a table of the game's fields or from the game's own stat names are not in this list; "What is recorded" above names them.

## Verified

parser replayed over 43 real journal files on this machine (event counts match the stats); Status.json surface fixes tested on synthetic snapshots only

## Source

[heat3d_watch/adapters/elite.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/elite.py)

*Generated from the adapter by `tools/gen_game_pages.py`; change the adapter and run it again rather than editing this page.*
