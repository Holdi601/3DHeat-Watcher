---
title: "iRacing (telemetry)"
parent: Games
nav_order: 28
---

# iRacing (telemetry)

Adapter `iracing` - kind [`telemetry`](sources-and-rules.md) - runs while `iRacingSim64DX11.exe` or `iRacingSim64.exe` is running - looks for new data every 0.1 s.

## What is recorded

- the driving at 5 Hz without a position (iRacing gives none live): speed, gear, throttle, brake, lap, share of the lap, race and class position, incidents
- session start, getting in and out of the car, pit lane in and out, laps with lap time, incidents with their points, chequered flag, finish
- the .ibt telemetry files written during the sitting (latitude, longitude, altitude - the viewer reads them)
- laps, best lap, incidents, race position, pit stops, distance, top speed
- the whole shared memory in `heat.raw.parquet`: header, variable headers, session info, every telemetry line read

## Where it comes from

shared memory Local\IRSDKMemMapFileName (the iRacing SDK); .ibt files in %USERPROFILE%\Documents\iRacing\telemetry

## How to switch it on

Nothing for the live data. For positions: log telemetry in the car (Alt+L) or set irsdkLog=1 in app.ini

## How it works

iRacing, live: the iRacing SDK's shared memory, read natively.

iRacing publishes its telemetry for apps in a named file mapping,
`Local\IRSDKMemMapFileName`, that the sim creates while it runs (and signals
`Local\IRSDKDataValidEvent` on each update, which is not needed here: the
watcher looks ten times a second). The layout is the SDK's `irsdk_defines.h`,
also followed by pyirsdk (MIT) - written again here from those facts:

```text
irsdk_header (little-endian int32s)
    0 ver, 4 status (bit 0: connected), 8 tickRate,
    12 sessionInfoUpdate, 16 sessionInfoLen, 20 sessionInfoOffset,
    24 numVars, 28 varHeaderOffset, 32 numBuf, 36 bufLen, 40 pad[2],
    48 varBuf[4]: { tickCount, bufOffset, pad[2] } (16 bytes each)
irsdk_varHeader (144 bytes, numVars of them at varHeaderOffset)
    0 type (0 char, 1 bool, 2 int, 3 bitfield, 4 float, 5 double),
    4 offset (into a line), 8 count, 12 countAsTime + 3 pad,
    16 name[32], 48 desc[64], 112 unit[32]
session info: YAML text at sessionInfoOffset, rewritten when
    sessionInfoUpdate changes (track, sessions, drivers)
```

The sim writes `numBuf` lines round-robin; the newest is the one with the
highest tickCount, and a line is taken again if its tickCount moved while it
was being copied.

Live data has no world position - latitude, longitude and altitude are only in
the `.ibt` files iRacing logs to `Documents\iRacing\telemetry` (Alt+L in the
car, or `irsdkLog=1`), which the 3DHeat viewer reads itself. So this records
the driving as events without coordinates - speed, lap, the share of the lap
done, race position, incidents - plus laps, incidents, pit stops and the
chequered flag, and at the end the `.ibt` files written during the sitting as
`telemetry_file` events, for the viewer to open.

Beside the rows the whole memory map is kept, in the session's raw sidecar
(`heat.raw.parquet`): the header's fixed part (`header`, each time it
changes), the variable headers (`var_headers`, whole, and as JSON in `text`,
each time the layout changes), the session info YAML (`session_info`, its
text each time `sessionInfoUpdate` moves) and the newest telemetry line
(`telemetry`, every variable of it, each read that finds a new tick). The var
headers and a line are all a later decoder needs to read any variable.

Source: the iRacing SDK (irsdk_defines.h, "iRacing SDK" forum documentation);
kutu/pyirsdk (MIT) for confirmation of the offsets.

## Positions and axes

| | |
|---|---|
| Positions recorded | no |
| Up axis | `y` |
| Units | no positions live; the .ibt files carry latitude/longitude/altitude |
| Mirrored for the viewer | none |
| Unit scale (`scale`: the viewer multiplies positions by it) | 1 |

These go into each session's `meta.json` (`axes`) and, when the session has positions, into `heat.parquet`'s footer, so the 3DHeat viewer turns and scales the rows by itself - see [The data](the-data.md).

## Multiplayer

- Marked as played online (`multiplayer`): **yes**. `games --markdown` shows this as "allowed (reads only what the game publishes)".
- Kind `telemetry`: it reads only what the game or platform hands out (a UDP port or shared memory the game publishes), so it records in online play as well as offline; the flag decides only whether memory may ever be read.
- Memory: **never** read by this adapter. Only `memory` adapters read memory, and never for a game marked as played online - see [Sources and rules](sources-and-rules.md).

## Statistics recorded

Statistic keys this adapter's code sets by name (each session's `stats` in `meta.json` and the `stats` table of `watcher.sqlite`):

`best_lap`, `distance_km`, `finishes`, `incidents`, `laps`, `pit_stops`, `race_position`, `sessions`, `top_speed_kmh`

A key in braces is completed at run time (`score.{team}` is one key per team). Keys the code takes from a table of the game's fields or from the game's own stat names are not in this list; "What is recorded" above names them.

## Completeness

The watcher follows 3DHeat's [converter rule](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md): what the source holds is read or kept, never dropped. Besides the rows, every packet, page, line or reply the adapter receives is kept whole in the session's `heat.raw.parquet` (columns `time`, `ms`, `type`, `used`, `payload`, `text`, then any field kept by name; `used` marks what also became rows), and `meta.json`'s `selfCheck.completeness` counts each `type` - `lost` is 0.

**Read**

- from the newest telemetry line: session time, number, state and id, on track, replay, lap, laps completed, share and metres of the lap, last and best lap, speed, gear, throttle, brake, RPM, pit road, track surface, race and class position, own incident count (the `driving` rows at 5 Hz and the events)
- now also on the `driving` rows: `steering_angle`, `yaw`, `yaw_north`, `pitch`, `roll` (degrees, from the sim's radians - only when the variable header gives the unit as rad), `fuel_l` (unit l), `lat_accel` and `lon_accel` (unit m/s^2)
- from the session info YAML: the player's car index, track and configuration, session types, each driver's name, car, team and number (session_start rows, meta.json)
- checked against a block built from irsdk_defines.h in the tests; not yet against the sim

**Kept raw**

- `telemetry`: the newest line whole, every variable the sim publishes (the CarIdx arrays of every car, tyres, suspension, the high-rate `_ST` arrays where the sim has them ...), each read that finds a new tick; `tick` the sim's tick count; `used` is false while a replay plays
- `var_headers`: the variable headers whole (144 bytes each) and, in `text`, as JSON (name, type, offset, count, unit, description), each time the layout changes - enough to read every variable of every kept line
- `session_info`: the YAML text whole each time its update counter moves (weekend, sessions and results, drivers, car setup, radio, camera lists), `update` the counter
- `header`: the 112-byte irsdk header whole each time it changes (version, status, tick rate, offsets, the lines' ticks)

**Not available**

- a world position live: the shared memory has none; latitude, longitude and altitude are only in the .ibt files (logging on), which the viewer reads - the watcher names those written during the sitting
- the ticks between two reads: the sim writes 60 lines a second into 3 or 4 slots and the watcher reads 10 times a second, so most ticks are overwritten before they could be read; the .ibt file has every tick when logging is on

**Size**: a telemetry line is a few KB (about 5 to 10 KB with every car's arrays), kept up to 10 times a second, plus the header (112 bytes) as often and the session info YAML (tens of KB) when it changes: about 0.2 to 0.4 GB per hour on track before compression; zstd brings it to a fraction (not yet measured on a real session)

## Verified

tested on a shared-memory block built in the test from the irsdk layout; untested against the sim

## Source

[heat3d_watch/adapters/iracing.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/iracing.py)

*Generated from the adapter by `tools/gen_game_pages.py`; change the adapter and run it again rather than editing this page.*
