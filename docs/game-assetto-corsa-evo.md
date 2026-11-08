---
title: "Assetto Corsa EVO (telemetry)"
parent: Games
nav_order: 4
---

# Assetto Corsa EVO (telemetry)

Adapter `assetto-corsa-evo` - kind [`telemetry`](sources-and-rules.md) - runs while `AssettoCorsaEVO.exe` is running - looks for new data every 0.1 s.

## What is recorded

- own car's position (world XYZ, m: mean of the tyre contact points) at 10 Hz with speed, gear, throttle, brake
- session start and end with the track and car the game names
- laps when the car passes where the drive began, heading the same way
- teleports (back to the pits, a restart): `teleport` where the car was, `spawn` where it is now
- laps, best lap, distance, top speed

## Where it comes from

shared memory Local\acevo_pmf_physics, Local\acevo_pmf_static

## How to switch it on

Nothing needs switching on: the watcher reads the source as the game or platform provides it.

## How it works

Racing games' own telemetry: Forza, the Assetto Corsa games, the rally games
and BeamNG, recorded as routes, laps and stages.

Every game here publishes its telemetry on purpose, for dashboards and motion
rigs; nothing is injected and nothing the game does not hand out is read. The
decoding is not written twice: it is gamecapture's lap recorders in
3DHeat GameCapture's `heat3d_capture/telemetry`, copied into `heat3d_watch/decoders` (tested there against packets built from
the published layouts), and this module turns their frames into the watcher's
rows - the car's position a few times a second with its speed, gear and pedals,
an event per lap or stage, and the numbers a driver keeps: laps, best lap,
distance, top speed.

#### Forza (Horizon 4/5/6, Motorsport)

"Data Out" UDP, switched on in the game's HUD and Gameplay settings, to
127.0.0.1 port 5300, format Dash. One packet per simulation tick; the dash
block's offset is found from the packets (`forza.detect_layout`). World
metres, Y up; the world is left-handed and is drawn as sent, as the lap recorder
does (Forza Motorsport's and Forza Horizon's "Data Out" documentation).
The game sends to one port, and FH Companion and other Data Out apps listen
on the same one. Two programs cannot share it: on Windows the socket bound
to 127.0.0.1 gets the packets and one bound to all addresses on the same
port gets none, whichever came first. So the watcher waits a little after
the game starts before it takes the port, never takes it from an app that
holds it, and lets go of it as soon as another app starts listening there.
While it holds the port it passes every packet on unchanged to
127.0.0.1:5301 - set FH Companion's port box (its telemetry tab) to 5301 and
both record.

#### Assetto Corsa, ACC, AC EVO, AC Rally

Shared memory the game writes for apps: `Local\acpmf_physics`,
`Local\acpmf_graphics`, `Local\acpmf_static` (AC EVO: `Local\acevo_pmf_*`).
Opened read-only and only once the game has made it (`simracing_shm`). The
position is the mean of the four tyre contact points, world metres, Y up.
Laps by the game's counter (AC, ACC) or by passing the starting point again
(AC EVO, AC Rally), as `kunos.py` does for the lap recorder.

#### EA SPORTS WRC, DiRT Rally 2.0, Richard Burns Rally

UDP: WRC's `Documents/My Games/WRC/telemetry/config.json` (the `wrc`
structure's `session_update` packet), DiRT's `hardware_settings_config.xml`
(`<udp enabled="true" extradata="3" port="20777">`), RBR's NGP plugin
(`udpTelemetry=1`, port 6776). Stages by the game's stage clock
(`rally.StageSplitter`). RBR does not document its axes: the up axis is the
one the stage varies least along, decided when the session closes.

#### BeamNG.drive

The `heat3d` protocol mod gamecapture ships (UDP 4460, Options > Other >
Protocols > "others"); BeamNG's Z-up world turned to Y up as `beamng.py` does.

#### Everything kept

The rows are a few a second; the games send far more. Every UDP packet that
arrives - in the menus, between laps, ones no decoder reads - is kept whole
in the session's `heat.raw.parquet` under its format (`dash-horizon`,
`session_update`, `extradata3`, `H3D1`, ...), and every shared memory page
(the whole mapping, not only the bytes decoded) each time it changes, under
its mapping's name (`acpmf_physics`, ...). `used` marks what also became
rows; `meta.json`'s `selfCheck.completeness` counts each kind (3DHeat's
converter rule).

The same module also serves: [Assetto Corsa (telemetry)](game-assetto-corsa.md), [Assetto Corsa Competizione (telemetry)](game-assetto-corsa-competizione.md), [Assetto Corsa Rally (telemetry)](game-assetto-corsa-rally.md), [BeamNG.drive (telemetry)](game-beamng.md), [DiRT Rally 2.0 (telemetry)](game-dirt-rally-2.md), [EA SPORTS WRC (telemetry)](game-ea-wrc.md), [Forza Horizon 4 (telemetry)](game-forza-horizon-4.md), [Forza Horizon 5 (telemetry)](game-forza-horizon-5.md), [Forza Horizon 6 (telemetry)](game-forza-horizon-6.md), [Forza Motorsport (telemetry)](game-forza-motorsport.md), [Richard Burns Rally (telemetry)](game-richard-burns-rally.md).

## Positions and axes

| | |
|---|---|
| Positions recorded | yes |
| Up axis | `y` |
| Units | metres |
| Mirrored for the viewer | none |
| Unit scale (`scale`: the viewer multiplies positions by it) | 1 |

These go into each session's `meta.json` (`axes`) and, when the session has positions, into `heat.parquet`'s footer, so the 3DHeat viewer turns and scales the rows by itself - see [The data](the-data.md).

## Multiplayer

- Marked as played online (`multiplayer`): **yes**. `games --markdown` shows this as "allowed (reads only what the game publishes)".
- Kind `telemetry`: it reads only what the game or platform hands out (a UDP port or shared memory the game publishes), so it records in online play as well as offline; the flag decides only whether memory may ever be read.
- Memory: **never** read by this adapter. Only `memory` adapters read memory, and never for a game marked as played online - see [Sources and rules](sources-and-rules.md).

## Statistics recorded

Statistic keys this adapter's code sets by name (each session's `stats` in `meta.json` and the `stats` table of `watcher.sqlite`):

`best_lap`, `best_stage`, `distance_km`, `laps`, `race_position`, `stages`, `top_speed_kmh`

A key in braces is completed at run time (`score.{team}` is one key per team). Keys the code takes from a table of the game's fields or from the game's own stat names are not in this list; "What is recorded" above names them.

## Completeness

The watcher follows 3DHeat's [converter rule](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md): what the source holds is read or kept, never dropped. Besides the rows, every packet, page, line or reply the adapter receives is kept whole in the session's `heat.raw.parquet` (columns `time`, `ms`, `type`, `used`, `payload`, `text`, then any field kept by name; `used` marks what also became rows), and `meta.json`'s `selfCheck.completeness` counts each `type` - `lost` is 0.

**Read**

- rows at 10 Hz from the physics page: position (mean of the tyre contact points), speed, gear, throttle, brake, yaw/pitch/roll (rad), rpm, steer (as the page has it); session start with the track and car from the static page; laps, race position

**Kept raw**

- each page whole - the full mapping region, not only the bytes decoded - every time its bytes change, at the watcher's 10 Hz read: `acevo_pmf_physics`, `acevo_pmf_static`; a reread that is byte for byte the last one is counted in meta.json's `unchanged_reads`, not stored again
- everything decoded only for lap files (`decoders/kunos.py`: per wheel slip, load, pressure, temperatures, camber, suspension, contact points, brake temperatures, slip ratio and angle; world and local velocity, angular velocity, aids) is in those pages

**Not available**

- other cars' positions: the pages describe the player's car only (ACC's graphics page has car ids and coordinates for others in some versions - kept in the raw page, not decoded)
- physics ticks between the watcher's reads: the game rewrites the page at its physics rate (up to 333 Hz) and the watcher reads 10 times a second
- a lap counter or the game's lap time: AC EVO's pages as read have no graphics page; laps are split by position

**Size**: about 150-300 MB an hour before compression (a 4 KB region per page at up to 10 changes a second); the pages are mostly zeros and zstd keeps a small fraction

## Verified

decoding is gamecapture's lap recorder's (tested on synthetic pages); the adapter tested on shared memory built in the test from the documented layout; untested against the game; the executable name is from player reports

## Source

[heat3d_watch/adapters/racing.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/racing.py)

*Generated from the adapter by `tools/gen_game_pages.py`; change the adapter and run it again rather than editing this page.*
