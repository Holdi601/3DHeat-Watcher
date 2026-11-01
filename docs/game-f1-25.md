---
title: "EA SPORTS F1 25 (telemetry)"
parent: Games
nav_order: 15
---

# EA SPORTS F1 25 (telemetry)

Adapter `f1-25` - kind [`telemetry`](sources-and-rules.md) - runs while `F1_25.exe` is running - looks for new data every 0.1 s.

## What is recorded

- every car's position (world XYZ, m) at 10 Hz, by driver name, team, own car marked (`own_car` 1, from the player car index), with speed, gear, throttle, brake
- laps per car with the lap time and race position; finishes and retirements
- the game's race events: session start and end, fastest lap, penalties, overtakes, collisions, safety car, red flag, start lights, chequered flag, winner, flashbacks (`teleport` where the car was, `spawn` where it went back to)
- track, session type, laps and drivers of each session
- own laps, best lap, race and grid position, pit stops, penalties, overtakes, collisions, distance, top speed

## Where it comes from

UDP telemetry 127.0.0.1:20777 (Documents\My Games\F1 25\hardwaresettings\hardware_settings_config.xml)

## How to switch it on

In the game: Settings > Telemetry Settings > UDP Telemetry On, IP 127.0.0.1, port 20777 - or `python -m heat3d_watch setup f1-25 --apply` (edits hardware_settings_config.xml, backed up first; the game must be closed). While another app holds 20777 the watcher leaves the port to it

`python -m heat3d_watch setup f1-25` lists the files it would change; `python -m heat3d_watch setup f1-25 --apply` changes them, keeping the original as `<file>.heat3d-backup` (see [Commands](commands.md#setup)).

## How it works

EA SPORTS F1 23, F1 24 and F1 25: the official UDP telemetry, every car on track.

The games send it themselves (Settings > Telemetry Settings, or
`Documents/My Games/<F1 xx>/hardwaresettings/hardware_settings_config.xml`,
`<udp enabled="true" ip="127.0.0.1" port="20777" sendRate="20" format="2025" ...>`).
Little-endian, packed, a 29-byte header on every packet (the same in the 2023,
2024 and 2025 formats):

```text
uint16 packetFormat, uint8 gameYear, gameMajorVersion, gameMinorVersion,
packetVersion, packetId, uint64 sessionUID, float sessionTime,
uint32 frameIdentifier, overallFrameIdentifier, uint8 playerCarIndex,
secondaryPlayerCarIndex
```

What is read, by packet id:

```text
0 Motion        CarMotionData[22], 60 bytes each: world position x y z
                (metres; Y is up), world velocity, forward and right
                vectors (int16 / 32767), g-forces, yaw pitch roll
1 Session       weather, temperatures, total laps, track length, session
                type, track id, ... network game
2 Lap Data      LapData[22]: last lap time, lap distance, race position,
                current lap number, pit stops, penalties, grid position,
                driver and result status. 50 bytes per car in 2023; 57 in
                2024 and 2025, which added the minutes parts of the deltas
                and the speed trap.
3 Event         a four-letter code and a union of details: SSTA SEND FTLP
                RTMT DRSE DRSD TMPT CHQF RCWN PENA SPTP STLG LGOT DTSV SGSV
                FLBK BUTN RDFL OVTK SCAR COLL
4 Participants  ParticipantData[22]: AI or human, driver, team, race
                number, name (48 bytes in 2023 and 2024, 32 in 2025; 58,
                60 and 57 bytes per car)
6 Car Telemetry CarTelemetryData[22], 60 bytes: speed km/h, throttle,
                steer, brake, clutch, gear, rpm ...
```

Every car's position is in the Motion packet - online too, where the game
itself hands it out (only fuel, ERS, damage and tyre-set data are held back
for players whose "Your Telemetry" is restricted). Each car is recorded at
about 10 Hz under its participant name ("car N" until the names arrive), the
team by name, and the player's own car marked `own`.

Sources: EA's "F1 25 UDP Specification" (forums.ea.com, F1 games info hub),
the F1 23 and F1 24 specifications; the same tables mirrored in
MacManley/f1-25-udp (MIT). Packets in tests are built from these layouts.

The same module also serves: [EA SPORTS F1 23 (telemetry)](game-f1-23.md), [EA SPORTS F1 24 (telemetry)](game-f1-24.md).

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

`best_lap`, `collisions`, `distance_km`, `fastest_laps`, `finishes`, `flashbacks`, `grid_position`, `laps`, `overtaken`, `overtakes`, `penalties`, `penalty_seconds`, `pit_stops`, `race_position`, `sessions`, `top_speed_kmh`, `wins`

A key in braces is completed at run time (`score.{team}` is one key per team). Keys the code takes from a table of the game's fields or from the game's own stat names are not in this list; "What is recorded" above names them.

## Verified

tested on packets in the 2023, 2024 and 2025 formats built from EA's published specification, sent over UDP; untested against the game

## Source

[heat3d_watch/adapters/f1.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/f1.py)

*Generated from the adapter by `tools/gen_game_pages.py`; change the adapter and run it again rather than editing this page.*
