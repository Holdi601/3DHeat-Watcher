---
title: "Forza Horizon 5 (telemetry)"
parent: Games
nav_order: 22
---

# Forza Horizon 5 (telemetry)

Adapter `forza-horizon-5` - kind [`telemetry`](sources-and-rules.md) - runs while `ForzaHorizon5.exe` is running - looks for new data every 0.1 s.

## What is recorded

- own car's position (world XYZ, m) at 10 Hz with speed, gear, throttle, brake, lap
- drive start and end (session_start/session_end), laps with the game's lap time
- race start and finish with the race position
- teleports (rewind, fast travel): `teleport` where the car was, `spawn` where it is now
- laps, best lap, distance, top speed, races

## Where it comes from

Forza Data Out, UDP 127.0.0.1:5300 (Dash format); every packet relayed unchanged to 127.0.0.1:5301

## How to switch it on

In the game: Settings > HUD and Gameplay > Data Out On, IP 127.0.0.1, port 5300 (Motorsport: format Dash). FH Companion or another Data Out app: set its port to 5301 - the watcher passes every packet on; while another app listens on 5300 the watcher leaves the port to it and records nothing

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

The same module also serves: [Assetto Corsa (telemetry)](game-assetto-corsa.md), [Assetto Corsa Competizione (telemetry)](game-assetto-corsa-competizione.md), [Assetto Corsa EVO (telemetry)](game-assetto-corsa-evo.md), [Assetto Corsa Rally (telemetry)](game-assetto-corsa-rally.md), [BeamNG.drive (telemetry)](game-beamng.md), [DiRT Rally 2.0 (telemetry)](game-dirt-rally-2.md), [EA SPORTS WRC (telemetry)](game-ea-wrc.md), [Forza Horizon 4 (telemetry)](game-forza-horizon-4.md), [Forza Horizon 6 (telemetry)](game-forza-horizon-6.md), [Forza Motorsport (telemetry)](game-forza-motorsport.md), [Richard Burns Rally (telemetry)](game-richard-burns-rally.md).

## Positions and axes

| | |
|---|---|
| Positions recorded | yes |
| Up axis | `y` |
| Units | metres; Forza's world is left-handed, drawn as sent like the lap recorder does |
| Mirrored for the viewer | none |
| Unit scale (`scale`: the viewer multiplies positions by it) | 1 |

These go into each session's `meta.json` (`axes`) and, when the session has positions, into `heat.parquet`'s footer, so the 3DHeat viewer turns and scales the rows by itself - see [The data](the-data.md).

## Multiplayer

- Marked as played online (`multiplayer`): **yes**. `games --markdown` shows this as "allowed (reads only what the game publishes)".
- Kind `telemetry`: it reads only what the game or platform hands out (a UDP port or shared memory the game publishes), so it records in online play as well as offline; the flag decides only whether memory may ever be read.
- Memory: **never** read by this adapter. Only `memory` adapters read memory, and never for a game marked as played online - see [Sources and rules](sources-and-rules.md).

## Statistics recorded

Statistic keys this adapter's code sets by name (each session's `stats` in `meta.json` and the `stats` table of `watcher.sqlite`):

`best_lap`, `distance_km`, `laps`, `races`, `top_speed_kmh`

A key in braces is completed at run time (`score.{team}` is one key per team). Keys the code takes from a table of the game's fields or from the game's own stat names are not in this list; "What is recorded" above names them.

## Completeness

The watcher follows 3DHeat's [converter rule](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md): what the source holds is read or kept, never dropped. Besides the rows, every packet, page, line or reply the adapter receives is kept whole in the session's `heat.raw.parquet` (columns `time`, `ms`, `type`, `used`, `payload`, `text`, then any field kept by name; `used` marks what also became rows), and `meta.json`'s `selfCheck.completeness` counts each `type` - `lost` is 0.

**Read**

- rows at 10 Hz: position, speed, gear, throttle, brake, lap, yaw/pitch/roll (rad), rpm, steer (-1..1); session_start with the car's ordinal, class, PI and drivetrain; laps with the game's lap time; race position

**Kept raw**

- every packet that reaches the port, whole, at the game's rate (one per simulation tick), under its format: `dash-horizon` (324 bytes, Forza Horizon), `dash` (311, Motorsport 7), `dash-fm2023` (331, Forza Motorsport 2023: tyre wear and track id), `sled` (232, no position), `<n>-byte` for anything else - including menu packets (isRaceOn 0), the packets held until the dash layout is proven, and the ~13 bytes of the Horizon packet no published layout names
- the Sled block's every wheel channel (slip ratio, slip angle, combined slip, suspension, wheel speed, rumble, puddle), accelerations, angular velocity, power, torque, boost, fuel, tyre temperatures, clutch, handbrake, driving line, AI brake difference: all in the packets, decoded by `decoders/fulllap.decode_full` from them

**Not available**

- other cars: Data Out describes the player's car only
- the track or route name: Forza Horizon never sends one; Motorsport 2023 sends only a track number
- packets while another app (FH Companion) holds UDP 5300: the watcher leaves the port to it

**Size**: about 85 MB an hour before compression (60 packets a second of 324 bytes plus a 70-byte item header); consecutive packets differ little, so zstd keeps a fraction of it

## Verified

decoding is gamecapture's lap recorder's (tested on packets built from the Data Out layout); the adapter tested on synthetic packets and on real FH Companion lap trajectories replayed as packets; untested against the game itself

## Source

[heat3d_watch/adapters/racing.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/racing.py)

*Generated from the adapter by `tools/gen_game_pages.py`; change the adapter and run it again rather than editing this page.*
