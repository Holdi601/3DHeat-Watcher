---
title: "X-Plane (telemetry)"
parent: Games
nav_order: 50
---

# X-Plane (telemetry)

Adapter `xplane` - kind [`telemetry`](sources-and-rules.md) - runs while `X-Plane.exe` is running - looks for new data every 0.1 s.

## What is recorded

- own position at 10 Hz (latitude/longitude/altitude as metres east/up/north of the first fix; lat/lon/alt kept as columns)
- attitude, indicated airspeed, groundspeed, AGL, normal g, on-ground
- takeoffs, landings, crashes, flight resets (session_start/session_end per flight)
- flight time, airborne time, distance, highest altitude, highest g, landings

## Where it comes from

X-Plane's UDP interface on 127.0.0.1:49000 (RREF datarefs and RPOS position, answered to the watcher)

## How to switch it on

X-Plane 12: Settings > Network > Accept incoming connections (X-Plane 11 answers by default)

## How it works

X-Plane 11 and 12: the sim's own UDP interface on port 49000.

X-Plane answers anyone who asks on 127.0.0.1:49000, at the rate asked for, to
the address and port the request came from (X-Plane's "Exchanging Data with
X-Plane" document, shipped in `<X-Plane>\Instructions\`):

```text
RREF  "RREF\0" + int32 freq + int32 index + char[400] dataref path (413 bytes).
      The answer is "RREF" + one internal byte + (int32 index, float32 value)
      pairs; freq 0 stops it.
RPOS  "RPOS\0" + the rate as a NUL-terminated ASCII string ("10\0"). The
      answer is "RPOS" + one internal byte + double lon, lat, elevation (m
      MSL) + float AGL (m), pitch, true heading, roll (deg), vx east, vy up,
      vz south (m/s), P, Q, R (rad/s), tightly packed.
```

RPOS gives latitude and longitude as doubles (RREF only as floats, half a metre
apart), so it drives the position; RREF brings the rest and stands in when
RPOS does not come. Datarefs (names as in X-Plane 12's `Resources\plugins\DataRefs.txt`,
<https://developer.x-plane.com/datarefs/>):

```text
sim/flightmodel/position/latitude, longitude, elevation  deg, deg, m MSL
sim/flightmodel/position/true_theta, true_phi, true_psi  pitch, roll, true heading (deg)
sim/flightmodel/position/indicated_airspeed              knots
sim/flightmodel/position/groundspeed                     m/s
sim/flightmodel/position/y_agl                           m above ground
sim/flightmodel/forces/g_nrml                            g, normal to the wings
sim/flightmodel/failures/onground_any                    1 on the ground
sim/flightmodel2/misc/has_crashed                        1 crashed
sim/time/total_flight_time_sec                           since the flight was reset
```

X-Plane 12 accepts these only with Settings > Network > "Accept incoming
connections" on. Positions go into a flat map around the sitting's first fix
(`Tangent`): x east, z north in metres, y the altitude above sea level - so a
level flight stays level however far it goes, which a true tangent plane would
bend down with the earth. The map's origin is the session's `geo`: meta.json
and the table's footer carry it, so the viewer can lay the real world under
the flight.

This module also holds what the other flight sims share: the flat map, the
flight bookkeeping (takeoffs, landings, crashes, distance), the UDP socket and
the Steam library list.

## Positions and axes

| | |
|---|---|
| Positions recorded | yes |
| Up axis | `y` |
| Units | metres (east, altitude, north from the first fix) |
| Mirrored for the viewer | `z` |
| Unit scale (`scale`: the viewer multiplies positions by it) | 1 |

These go into each session's `meta.json` (`axes`) and, when the session has positions, into `heat.parquet`'s footer, so the 3DHeat viewer turns and scales the rows by itself - see [The data](the-data.md).

## Multiplayer

- Marked as played online (`multiplayer`): **no**. `games --markdown` shows this as "single-player".
- Kind `telemetry`: it reads only what the game or platform hands out (a UDP port or shared memory the game publishes), so it records in online play as well as offline; the flag decides only whether memory may ever be read.
- Memory: **never** read by this adapter. Only `memory` adapters read memory, and never for a game marked as played online - see [Sources and rules](sources-and-rules.md).

## Statistics recorded

Statistic keys this adapter's code sets by name (each session's `stats` in `meta.json` and the `stats` table of `watcher.sqlite`):

`airborne_time`, `bad_packets`, `crashes`, `distance_km`, `flight_time`, `max_altitude_m`, `max_g`, `{event}s`

A key in braces is completed at run time (`score.{team}` is one key per team). Keys the code takes from a table of the game's fields or from the game's own stat names are not in this list; "What is recorded" above names them.

## Verified

tested against a fake X-Plane answering RREF/RPOS per X-Plane 12's 'Exchanging Data with X-Plane'; dataref names checked against X-Plane 12's DataRefs.txt; untested against the running sim

## Source

[heat3d_watch/adapters/xplane.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/xplane.py)

*Generated from the adapter by `tools/gen_game_pages.py`; change the adapter and run it again rather than editing this page.*
