---
title: "EA SPORTS F1 25 (telemetry)"
parent: Games
nav_order: 16
---

# EA SPORTS F1 25 (telemetry)

Adapter `f1-25` - kind [`telemetry`](sources-and-rules.md) - runs while `F1_25.exe` is running - looks for new data every 0.1 s.

## What is recorded

- every car's position (world XYZ, m) at 10 Hz, by driver name, team, own car marked (`own_car` 1, from the player car index), with speed, gear, throttle, brake, steer, rpm, DRS, yaw, pitch, roll (degrees) and g-forces
- laps per car with the lap time and race position; finishes and retirements
- the game's race events: session start and end, fastest lap, penalties, overtakes, collisions, safety car, red flag, start lights, chequered flag, winner, flashbacks (`teleport` where the car was, `spawn` where it went back to)
- track, session type, laps and drivers of each session
- own laps, best lap, race and grid position, pit stops, penalties, overtakes, collisions, distance, top speed
- every packet the game sends, whole, in `heat.raw.parquet` - also the ones not read into rows

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
                steer, brake, clutch, gear, rpm, DRS ...
```

Every packet is also kept whole, as it came, in the session's raw sidecar
(`heat.raw.parquet`, `type` the packet's name - `motion`, `car_status` ... -
with `format`, `packet_id`, `frame` and `session_uid`) - the ones read above and the ones
nothing reads yet: 5 Car Setups, 7 Car Status, 8 Final Classification, 9 Lobby
Info, 10 Car Damage, 11 Session History, 12 Tyre Sets, 13 Motion Ex, 14 Time
Trial, 15 Lap Positions, any later id, and packets in a format this does not
read. So a later decoder needs only the sidecar.

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

## Completeness

The watcher follows 3DHeat's [converter rule](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md): what the source holds is read or kept, never dropped. Besides the rows, every packet, page, line or reply the adapter receives is kept whole in the session's `heat.raw.parquet` (columns `time`, `ms`, `type`, `used`, `payload`, `text`, then any field kept by name; `used` marks what also became rows), and `meta.json`'s `selfCheck.completeness` counts each `type` - `lost` is 0.

**Read**

- 0 Motion: every car's world position and velocity, and now also yaw, pitch, roll (degrees, from the spec's radians) and the lateral, longitudinal and vertical g-force, on each car's position rows
- 1 Session: track, session type, total laps, track length, online or not (meta.json `sessions`)
- 2 Lap Data: last lap time, lap number, race and grid position, pit stops, penalties, result status (laps, finishes, retirements, statistics)
- 3 Event: every code but BUTN as its own row, with its details
- 4 Participants: driver names, teams, number of active cars (rows' `player` and `team`, meta.json `drivers`)
- 6 Car Telemetry: speed, gear, throttle, brake, and now also steer (-1..1), rpm and DRS, on each car's position rows
- checked against EA's published UDP specifications for the 2023, 2024 and 2025 formats (packet sizes asserted in the tests); not yet against the game

**Kept raw**

- every packet whole in `heat.raw.parquet`, `payload` the datagram, `type` its id's name: `motion`, `session`, `lap_data`, `event`, `participants`, `car_setups`, `car_telemetry`, `car_status`, `final_classification`, `lobby_info`, `car_damage`, `session_history`, `tyre_sets`, `motion_ex`, `time_trial`, `lap_positions` (`packet <n>` for an id the specifications do not list yet); columns `format` (2023/2024/2025), `packet_id`, `frame`, `session_uid`
- `used` is true for the packets read above (Motion, Session, Lap Data, Participants, Car Telemetry, and Event codes other than BUTN); the rest - car setups, car status (fuel, ERS, tyre compound and age, flags), final classification, lobby, car damage, session history (every lap and sector time per car), tyre sets, motion ex (the own car's suspension, wheel speeds, local velocity, angular velocity and acceleration), time trial, lap positions, BUTN button events - are kept for a later decoder
- `format <year>`: a packet in a format before 2023 (another header layout), whole; `short`: a datagram shorter than the 29-byte header, whole

**Not available**

- other players' fuel, ERS, damage and tyre sets online when their "Your Telemetry" is restricted: the game sends zeros for them
- packets sent while the watcher is not running, or while another app holds port 20777: UDP is not stored by the game

**Size**: at a send rate of 60 Hz every packet is about 0.38 MB/s (Motion, Lap Data, Car Telemetry, Car Status and Motion Ex at 60 Hz, Session History and Tyre Sets at 20/s, Car Damage at 10/s, Session and Car Setups at 2/s) plus about 0.03 MB/s of item headers: about 1.5 GB per hour of driving before compression, about 0.55 GB at the default 20 Hz; zstd brings it to a fraction of that (empty car slots and repeated values compress well; not yet measured on a real session)

## Verified

tested on packets in the 2023, 2024 and 2025 formats built from EA's published specification, sent over UDP; untested against the game

## Source

[heat3d_watch/adapters/f1.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/f1.py)

*Generated from the adapter by `tools/gen_game_pages.py`; change the adapter and run it again rather than editing this page.*
