
# iRacing (telemetry)

Adapter `iracing` - kind [`telemetry`](sources-and-rules) - runs while `iRacingSim64DX11.exe` or `iRacingSim64.exe` is running - looks for new data every 0.1 s.

## What is recorded

- the driving at 5 Hz without a position (iRacing gives none live): speed, gear, throttle, brake, lap, share of the lap, race and class position, incidents
- session start, getting in and out of the car, pit lane in and out, laps with lap time, incidents with their points, chequered flag, finish
- the .ibt telemetry files written during the sitting (latitude, longitude, altitude - the viewer reads them)
- laps, best lap, incidents, race position, pit stops, distance, top speed

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

These go into each session's `meta.json` (`axes`) and, when the session has positions, into `heat.parquet`'s footer, so the 3DHeat viewer turns and scales the rows by itself - see [The data](the-data).

## Multiplayer

- Marked as played online (`multiplayer`): **yes**. `games --markdown` shows this as "allowed (reads only what the game publishes)".
- Kind `telemetry`: it reads only what the game or platform hands out (a UDP port or shared memory the game publishes), so it records in online play as well as offline; the flag decides only whether memory may ever be read.
- Memory: **never** read by this adapter. Only `memory` adapters read memory, and never for a game marked as played online - see [Sources and rules](sources-and-rules).

## Statistics recorded

Statistic keys this adapter's code sets by name (each session's `stats` in `meta.json` and the `stats` table of `watcher.sqlite`):

`best_lap`, `distance_km`, `finishes`, `incidents`, `laps`, `pit_stops`, `race_position`, `sessions`, `top_speed_kmh`

A key in braces is completed at run time (`score.{team}` is one key per team). Keys the code takes from a table of the game's fields or from the game's own stat names are not in this list; "What is recorded" above names them.

## Verified

tested on a shared-memory block built in the test from the irsdk layout; untested against the sim

## Source

[heat3d_watch/adapters/iracing.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/iracing.py)

*Generated from the adapter by `tools/gen_game_pages.py`; change the adapter and run it again rather than editing this page.*
