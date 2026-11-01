
# Project CARS 2 (telemetry)

Adapter `project-cars-2` - kind [`telemetry`](sources-and-rules) - runs while `pCARS2AVX.exe` or `pCARS2.exe` is running - looks for new data every 0.1 s.

## What is recorded

- every car's position (world XYZ, m) at 10 Hz by driver name, own car marked, with speed and race position; own gear, throttle, brake
- session start with the track the game names; laps per car with lap time; finishes; own pit stops
- teleports (back to the pits, a restart): `teleport` where the car was, `spawn` where it is now
- own laps, best lap, race position, distance, top speed

## Where it comes from

shared memory $pcars2$ (SMS SharedMemory.h)

## How to switch it on

In the game: Options > System > Shared Memory: "Project CARS 2"

## How it works

Shared memory that racing games publish for dashboards, opened read-only - and
never created.

Several sims hand out their telemetry as a named Windows file mapping that the
game creates and anyone may read: Kunos's `Local\acpmf_*` pages (Assetto Corsa,
ACC, AC Rally, AC EVO's `Local\acevo_pmf_*`), iRacing's
`Local\IRSDKMemMapFileName`, RaceRoom's `$R3E`, Automobilista 2 / Project CARS 2's
`$pcars2$`.

Why not `mmap.mmap(-1, size, tagname=...)`, which is the usual Python way: when
the mapping does not exist yet it *creates* one - here, read-only. A game
started after that opens the watcher's mapping instead of making its own and
then cannot write to it, so its telemetry is dead until the watcher lets go.
The watcher starts an adapter as soon as the game's process appears, which is
exactly the moment the game has not made its mapping yet. So this opens with
`OpenFileMappingW`, which only ever finds an existing mapping, maps it with
`FILE_MAP_READ`, and reports "not there yet" otherwise; the adapters try again
a moment later.

Nothing here can write: the view is mapped read-only and is only ever copied
out of with `ctypes.string_at`.

Two games are read here as well; every car on track is in their pages.

#### RaceRoom Racing Experience - `$R3E`

Sector3's `r3e.h` (github.com/sector3studios/r3e-api, sample-c/src/r3e.h,
version 3.6), `#pragma pack(1)`. The header says where the drivers start
and how big one is (`all_drivers_offset`, `driver_data_size`), so the
per-driver part - name, slot, place, world position (float x y z, m),
completed laps, current lap time, finish status, pit lane, speed - is read
by those. The player's own fields (best and previous lap, race position,
incident points, gear, pedals, track and layout names) are read at their
3.6 offsets only when `all_drivers_offset` is the 2008 that layout puts it
at. Y is taken as up; the header does not say.

#### Automobilista 2 / Project CARS 2 - `$pcars2$`

SMS's `SharedMemory.h` (shipped in the game's Support\SharedMemory folder;
AMS2: Options > System > Shared Memory "Project CARS 2"), `#pragma pack(4)`.
`mParticipantInfo[64]` from byte 28, 100 bytes each: mIsActive, mName[64],
mWorldPosition[3] (m, Y up), mCurrentLapDistance, mRacePosition,
mLapsCompleted, mCurrentLap, mCurrentSector; mViewedParticipantIndex (20)
is the player's car; per participant mLastLapTimes (9200), mRaceStates
(9520), mSpeeds (10800); the player's mBestLapTime (6716), mLastLapTime
(6720), mSpeed (6848), mBrake, mThrottle, mGear; mSequenceNumber (7320) is
odd while the game writes. The offsets were worked out from two
independent copies of the header (the game's own copy is not installed
here), which agree.

The same module also serves: [Automobilista 2 (telemetry)](game-automobilista-2), [RaceRoom Racing Experience (telemetry)](game-raceroom).

## Positions and axes

| | |
|---|---|
| Positions recorded | yes |
| Up axis | `y` |
| Units | metres |
| Mirrored for the viewer | none |
| Unit scale (`scale`: the viewer multiplies positions by it) | 1 |

These go into each session's `meta.json` (`axes`) and, when the session has positions, into `heat.parquet`'s footer, so the 3DHeat viewer turns and scales the rows by itself - see [The data](the-data).

## Multiplayer

- Marked as played online (`multiplayer`): **yes**. `games --markdown` shows this as "allowed (reads only what the game publishes)".
- Kind `telemetry`: it reads only what the game or platform hands out (a UDP port or shared memory the game publishes), so it records in online play as well as offline; the flag decides only whether memory may ever be read.
- Memory: **never** read by this adapter. Only `memory` adapters read memory, and never for a game marked as played online - see [Sources and rules](sources-and-rules).

## Statistics recorded

Statistic keys this adapter's code sets by name (each session's `stats` in `meta.json` and the `stats` table of `watcher.sqlite`):

`best_lap`, `distance_km`, `finishes`, `incidents`, `laps`, `pit_stops`, `race_position`, `top_speed_kmh`

A key in braces is completed at run time (`score.{team}` is one key per team). Keys the code takes from a table of the game's fields or from the game's own stat names are not in this list; "What is recorded" above names them.

## Verified

tested on a page built in the test; offsets from two independent copies of SharedMemory.h that agree, not from the copy the game ships (not installed here); untested against the game

## Source

[heat3d_watch/adapters/simracing_shm.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/simracing_shm.py)

*Generated from the adapter by `tools/gen_game_pages.py`; change the adapter and run it again rather than editing this page.*
