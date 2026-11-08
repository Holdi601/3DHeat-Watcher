---
title: "American Truck Simulator (telemetry)"
parent: Games
nav_order: 1
---

# American Truck Simulator (telemetry)

Adapter `ats` - kind [`telemetry`](sources-and-rules.md) - runs while `amtrucks.exe` is running - looks for new data every 0.1 s.

## What is recorded

- the truck's world position (x east, y up, z south, m) at 10 Hz while moving, every 5 s while standing; heading, speed, odometer
- jobs started (cargo, from, to), delivered (revenue, XP, km), cancelled; fines, tolls, ferries, trains, refuels
- ferries, trains and loaded saves cut the route (teleport, spawn)
- distance, top speed, deliveries, revenue, XP, fines
- the plugin's whole shared memory in `heat.raw.parquet`, each time it changes

## Where it comes from

shared memory Local\SCSTelemetry written by the RenCloud scs-sdk-plugin (revision 12) in &lt;game>\bin\win_x64\plugins

## How to switch it on

install scs-telemetry.dll (revision 12) from github.com/RenCloud/scs-sdk-plugin into &lt;game>\bin\win_x64\plugins; the game asks once per start to allow the SDK

## How it works

Euro Truck Simulator 2 and American Truck Simulator: the SCS telemetry SDK, through the RenCloud plugin.

SCS publishes a telemetry SDK (<https://modding.scssoft.com/wiki/Documentation/Engine/SDK/Telemetry>)
for plugins the player puts in `<game>\bin\win_x64\plugins\`. The game itself
publishes nothing; the widely used plugin from <https://github.com/RenCloud/scs-sdk-plugin>
(MIT) copies the SDK's channels into shared memory `Local\SCSTelemetry`
(32 KiB), laid out in `scs-telemetry/inc/scs-telemetry-common.hpp`. This reads
revision 12 of that layout (PLUGIN_REVID 12) and nothing else: the plugin
writes its revision at offset 40, and any other revision is left unread rather
than misread. Offsets used (zones as the header marks them; natural alignment):

```text
   0  bool sdkActive          4  bool paused
  40  u32  telemetry_plugin_revision, version_major, version_minor, game (1 ETS2, 2 ATS)
  64  u32  common_ui.time_abs (in-game minutes)
 504  i32  truck_i.gear
 640  i32  gameplay_i.jobDeliveredEarnedXp
 948  f32  truck_f.speed (m/s); 952 engineRpm; 1056 truckOdometer (km)
1460  f32  gameplay_f.jobDeliveredDistanceKm
2200  f64  truck_dp.coordinateX/Y/Z (m), rotationX/Y/Z (heading, pitch, roll in turns, 0..1)
2300  char[64] config_s: truckBrand +64, truckName +192, cargo +320, cityDst +448, compDst +576,
      citySrc +704, compSrc +832; 3436 gameplay_s.fineOffence[32]
4200  i64  gameplay_ll: jobCancelledPenalty, jobDeliveredRevenue, fineAmount, tollgatePayAmount,
      ferryPayAmount, trainPayAmount
4300  bool special_b: onJob, jobFinished, jobCancelled, jobDelivered, fined, tollgate, ferry,
      train, refuel, refuelPayed
```

The truck's world placement is SCS's world frame: x east, y up, z south, metres
(right-handed, y up - the viewer draws it as it is). Ferries, trains and loading
a save move the truck without driving: the route is cut there.

The whole mapping (the plugin's 32 KiB: every zone above and the ones not
read - truck configuration, wheels, wear, the truck's other channels, and
what the revision lays out after byte 4400, the trailers) is kept in the session's raw sidecar each time it changes,
`type` `SCSTelemetry` with the `revision` beside it - a page of another
revision too, which is kept whole rather than misread.

The same module also serves: [Euro Truck Simulator 2 (telemetry)](game-ets2.md).

## Positions and axes

| | |
|---|---|
| Positions recorded | yes |
| Up axis | `y` |
| Units | metres (SCS world: x east, y up, z south) |
| Mirrored for the viewer | none |
| Unit scale (`scale`: the viewer multiplies positions by it) | 1 |

These go into each session's `meta.json` (`axes`) and, when the session has positions, into `heat.parquet`'s footer, so the 3DHeat viewer turns and scales the rows by itself - see [The data](the-data.md).

## Multiplayer

- Marked as played online (`multiplayer`): **yes**. `games --markdown` shows this as "allowed (reads only what the game publishes)".
- Kind `telemetry`: it reads only what the game or platform hands out (a UDP port or shared memory the game publishes), so it records in online play as well as offline; the flag decides only whether memory may ever be read.
- Memory: **never** read by this adapter. Only `memory` adapters read memory, and never for a game marked as played online - see [Sources and rules](sources-and-rules.md).

## Statistics recorded

Statistic keys this adapter's code sets by name (each session's `stats` in `meta.json` and the `stats` table of `watcher.sqlite`):

`deliveries`, `distance_km`, `fines`, `fines_total`, `jobs_cancelled`, `max_speed_kmh`, `refuels`, `revenue`, `tolls_total`, `xp`

A key in braces is completed at run time (`score.{team}` is one key per team). Keys the code takes from a table of the game's fields or from the game's own stat names are not in this list; "What is recorded" above names them.

## Completeness

The watcher follows 3DHeat's [converter rule](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md): what the source holds is read or kept, never dropped. Besides the rows, every packet, page, line or reply the adapter receives is kept whole in the session's `heat.raw.parquet` (columns `time`, `ms`, `type`, `used`, `payload`, `text`, then any field kept by name; `used` marks what also became rows), and `meta.json`'s `selfCheck.completeness` counts each `type` - `lost` is 0.

**Read**

- SDK and pause state, plugin revision, game and version, in-game time, the truck's world position and heading, speed, odometer, truck brand and name, cargo, source and destination city and company, job revenue, XP and distance, cancellation penalty, fines and their offence, tolls, ferries, trains, the special event flags (rows, events and statistics)
- now also on the position rows: `pitch` and `roll` (degrees, from the SDK's turns), `gear` and `rpm`
- offsets checked against a field-by-field transcription of the plugin's revision 12 header whose zone starts are asserted in the tests; not yet against the game

**Kept raw**

- `SCSTelemetry`: the plugin's whole 32 KiB mapping, each read whose bytes differ from the copy kept last (`unchanged_reads` in meta.json counts the others), `revision` beside it: every zone - truck and trailer configuration, the truck's channels (pedals, steering, fuel, AdBlue, pressures, temperatures, wear, lights, wheels), placement and acceleration vectors, job and gameplay strings, and everything the revision lays out after byte 4400 (the trailers); `used` is true while the SDK is active and the revision is 12
- a page of another plugin revision is kept whole with `used` false instead of being misread

**Not available**

- anything the plugin does not copy out of the SDK, and everything while the plugin is not installed: the game publishes no telemetry of its own
- other players' trucks in TruckersMP or convoys: the SDK gives only the player's own truck

**Size**: 32 KiB up to 10 times a second while driving (every read differs then): about 1.2 GB per hour before compression, one copy while paused; most of the page is zeros and configuration that does not change, so zstd shrinks it many times over (not yet measured on a real session)

## Verified

tested on shared memory built from the plugin's revision 12 header layout; untested against the game (not installed on the test machine)

## Source

[heat3d_watch/adapters/ets2.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/ets2.py)

*Generated from the adapter by `tools/gen_game_pages.py`; change the adapter and run it again rather than editing this page.*
