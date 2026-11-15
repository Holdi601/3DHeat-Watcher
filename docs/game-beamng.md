---
title: "BeamNG.drive (live data)"
parent: Games
nav_order: 7
---

# BeamNG.drive (live data)

While you play BeamNG.drive, the watcher saves the data the game itself sends out, so you can look at it later on a map in the 3DHeat viewer.

*Technical details: adapter `beamng`, kind [`telemetry`](sources-and-rules.md); it runs while `BeamNG.drive.x64.exe` or `BeamNG.drive.exe` is running and looks for new data every 0.1 s.*

## What is recorded

- own car's position (world, m, turned to Y up) at 10 Hz with speed, gear, throttle, brake
- drive start, resets (respawn), laps past where the drive began
- laps, best lap, distance, top speed

## Where it comes from

UDP 127.0.0.1:4460 from the heat3d protocol mod (mods/beamng/heat3d in this repository)

## How to switch it on

`python -m heat3d_watch setup beamng --apply` installs the mod; then Options > Other > Protocols > "others"

Type the command in a terminal opened in the watcher's folder (see [Before you start](before-you-start.md)). If it fails, the last line says why; [Installing and running](installing-and-running.md) covers the usual causes.

`python -m heat3d_watch setup beamng` lists the files it would change; `python -m heat3d_watch setup beamng --apply` changes them, keeping the original as `<file>.heat3d-backup` (see [Commands](commands.md#setup)). It prints `beamng: changed: ...` for each change, or `beamng: nothing to change` when it is already on.

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

The same module also serves: [Assetto Corsa (live data)](game-assetto-corsa.md), [Assetto Corsa Competizione (live data)](game-assetto-corsa-competizione.md), [Assetto Corsa EVO (live data)](game-assetto-corsa-evo.md), [Assetto Corsa Rally (live data)](game-assetto-corsa-rally.md), [DiRT Rally 2.0 (live data)](game-dirt-rally-2.md), [EA SPORTS WRC (live data)](game-ea-wrc.md), [Forza Horizon 4 (live data)](game-forza-horizon-4.md), [Forza Horizon 5 (live data)](game-forza-horizon-5.md), [Forza Horizon 6 (live data)](game-forza-horizon-6.md), [Forza Motorsport (live data)](game-forza-motorsport.md), [Richard Burns Rally (live data)](game-richard-burns-rally.md).

## Positions and axes

| | |
|---|---|
| Positions recorded | yes |
| Up axis | `y` |
| Units | metres (BeamNG's Z-up world turned about X, as the lap recorder does) |
| Mirrored for the viewer | none |
| Unit scale (`scale`: the viewer multiplies positions by it) | 1 |

These go into each session's `meta.json` (`axes`) and, when the session has positions, into `heat.parquet`'s footer, so the 3DHeat viewer turns and scales the rows by itself - see [The data](the-data.md).

## Multiplayer

- Marked as played online (`multiplayer`): **no**. `games --markdown` shows this as "single-player".
- Kind `telemetry`: it reads only what the game or platform hands out (a UDP port or shared memory the game publishes), so it records in online play as well as offline; the flag decides only whether memory may ever be read.
- Memory: **never** read by this adapter. Only `memory` adapters read memory, and never for a game marked as played online - see [Sources and rules](sources-and-rules.md).

## Statistics recorded

Statistic keys this adapter's code sets by name (each session's `stats` in `meta.json` and the `stats` table of `watcher.sqlite`):

`best_lap`, `distance_km`, `laps`, `top_speed_kmh`

A key in braces is completed at run time (`score.{team}` is one key per team). Keys the code takes from a table of the game's fields or from the game's own stat names are not in this list; "What is recorded" above names them.

## Completeness

The watcher follows 3DHeat's [converter rule](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md): what the source holds is read or kept, never dropped. Besides the rows, every packet, page, line or reply the adapter receives is kept whole in the session's `heat.raw.parquet` (columns `time`, `ms`, `type`, `used`, `payload`, `text`, then any field kept by name; `used` marks what also became rows), and `meta.json`'s `selfCheck.completeness` counts each `type` - `lost` is 0.

**Read**

- rows at 10 Hz: position, speed, gear, throttle, brake, yaw, rpm, steer; drive start, resets, laps

**Kept raw**

- every packet that reaches the port, whole, at the mod's 100 Hz: `H3D1` (the mod's 160-byte struct: clock, position, velocity, the car's axes, yaw rate, nine inputs, per wheel surface speed, rotation, load and ground material), `<n>-byte` for anything else

**Not available**

- what the mod does not send: BeamNG has no fixed telemetry packet, so the channels are the ones the heat3d mod chose (other vehicles, damage, the map's name are not in it)

**Size**: about 80 MB an hour before compression (100 packets a second of 160 bytes plus a 70-byte item header)

## Verified

decoding is gamecapture's lap recorder's (tested on packets built from the mod's struct); adapter tested on such packets; the mod is untested in the game

## Source

[heat3d_watch/adapters/racing.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/racing.py)

<!-- Generated from the adapter by tools/gen_game_pages.py; change the adapter and run it again rather than editing this page. -->
