---
title: "Microsoft Flight Simulator 2024 (telemetry)"
parent: Games
nav_order: 32
---

# Microsoft Flight Simulator 2024 (telemetry)

Adapter `msfs2024` - kind [`telemetry`](sources-and-rules.md) - runs while `FlightSimulator2024.exe` is running - looks for new data every 0.1 s.

## What is recorded

- own aircraft position every sim frame, taken at 10 Hz (latitude/longitude/altitude as metres east/up/north of the first fix; lat/lon/alt kept as columns)
- attitude, indicated airspeed, groundspeed, AGL, g, on-ground; true airspeed, Mach, vertical speed, AoA, sideslip, magnetic heading, body velocities, accelerations and rotation rates at about 10 Hz
- weight, fuel, flaps, gear, spoilers, parking brake, autopilot, throttle, RPM, weather, sim rate, time and camera state once a second; the aircraft's title and ATC type, model and id
- takeoffs, landings, crashes, flights started and stopped (session_start/session_end)
- flight time, airborne time, distance, highest altitude, highest g, landings
- every SimConnect message kept whole in heat.raw.parquet

## Where it comes from

SimConnect through the player's own SimConnect.dll (the sim folder, or %MSFS2024_SDK%\SimConnect SDK\lib)

## How to switch it on

nothing in the sim; it needs SimConnect.dll - MSFS 2020 has it in its folder, MSFS 2024 players install the MSFS 2024 SDK

## How it works

Microsoft Flight Simulator 2020 and 2024: SimConnect, through the player's own SimConnect.dll.

SimConnect is the sim's published client API (SDK documentation:
<https://docs.flightsimulator.com/html/Programming_Tools/SimConnect/SimConnect_SDK.htm>,
<https://docs.flightsimulator.com/msfs2024/html/6_Programming_APIs/SimConnect/SimConnect_SDK.htm>).
The watcher does not ship the DLL: it loads the one that came with the sim or
its SDK - MSFS 2020 puts `SimConnect.dll` in its install folder; MSFS 2024 on
Steam ships only its internal one, so 2024 players install the MSFS 2024 SDK
(`<SDK>\SimConnect SDK\lib\SimConnect.dll`; the 2024 sim also accepts 2020 clients).

The calls, from SimConnect.h, all returning an HRESULT (0 = S_OK):

```text
SimConnect_Open(HANDLE*, LPCSTR name, HWND, DWORD, HANDLE, DWORD config)
SimConnect_AddToDataDefinition(HANDLE, DWORD define, LPCSTR var, LPCSTR units,
                               SIMCONNECT_DATATYPE (FLOAT64 = 4), float epsilon, DWORD datum)
SimConnect_RequestDataOnSimObject(HANDLE, DWORD request, DWORD define, DWORD object (0 = user),
                                  SIMCONNECT_PERIOD (SIM_FRAME = 3), DWORD flags, DWORD origin,
                                  DWORD interval, DWORD limit)
SimConnect_SubscribeToSystemEvent(HANDLE, DWORD event, LPCSTR name)
SimConnect_GetNextDispatch(HANDLE, SIMCONNECT_RECV**, DWORD*)   E_FAIL when nothing waits
SimConnect_Close(HANDLE)
```

Every message starts with SIMCONNECT_RECV {DWORD dwSize, dwVersion, dwID}
(#pragma pack 1). The ones read here:

```text
1  EXCEPTION       dwException, dwSendID, dwIndex
2  OPEN            szApplicationName[256], then version DWORDs
3  QUIT            the sim is closing
4  EVENT           uGroupID, uEventID, dwData
6  EVENT_FILENAME  EVENT + szFileName[260], dwFlags        (FlightLoaded)
8  SIMOBJECT_DATA  dwRequestID, dwObjectID, dwDefineID, dwFlags, dwentrynumber,
                   dwoutof, dwDefineCount, then the values (FLOAT64 each here)
```

Simulation variables (units asked for so no conversion is needed): PLANE
LATITUDE/LONGITUDE (degrees), PLANE ALTITUDE (meters, above sea level), PLANE
ALT ABOVE GROUND (meters), PLANE PITCH/BANK DEGREES and PLANE HEADING DEGREES
TRUE (degrees; SimConnect's own signs - nose up is negative pitch), AIRSPEED
INDICATED and GROUND VELOCITY (knots), G FORCE (gforce), SIM ON GROUND (bool).
System events: SimStart, SimStop, Crashed, FlightLoaded, AircraftLoaded,
Pause, CrashReset, PositionChanged, FlightSaved, Sim.

Three more data definitions ask for the rest of the flight (`MOTION_VARS`,
every sixth sim frame), the aircraft's slower state (`STATE_VARS`, once a
second) and its names (`NAME_VARS`, 256-byte strings, when they change); each
is its own definition, so a variable one sim version does not know costs
only that block. Every message is kept whole in the session's raw sidecar.

Positions go into the same flat map as X-Plane's (x east, y altitude, z north
in metres from the sitting's first fix); that fix is the session's `geo`, in
meta.json and the table's footer.

The same module also serves: [Microsoft Flight Simulator 2020 (telemetry)](game-msfs2020.md).

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

- Marked as played online (`multiplayer`): **yes**. `games --markdown` shows this as "allowed (reads only what the game publishes)".
- Kind `telemetry`: it reads only what the game or platform hands out (a UDP port or shared memory the game publishes), so it records in online play as well as offline; the flag decides only whether memory may ever be read.
- Memory: **never** read by this adapter. Only `memory` adapters read memory, and never for a game marked as played online - see [Sources and rules](sources-and-rules.md).

## Statistics recorded

Statistic keys this adapter's code sets by name (each session's `stats` in `meta.json` and the `stats` table of `watcher.sqlite`):

`airborne_time`, `bad_packets`, `crashes`, `distance_km`, `flight_time`, `max_altitude_m`, `max_g`, `{event}s`

A key in braces is completed at run time (`score.{team}` is one key per team). Keys the code takes from a table of the game's fields or from the game's own stat names are not in this list; "What is recorded" above names them.

## Completeness

The watcher follows 3DHeat's [converter rule](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md): what the source holds is read or kept, never dropped. Besides the rows, every packet, page, line or reply the adapter receives is kept whole in the session's `heat.raw.parquet` (columns `time`, `ms`, `type`, `used`, `payload`, `text`, then any field kept by name; `used` marks what also became rows), and `meta.json`'s `selfCheck.completeness` counts each `type` - `lost` is 0.

**Read**

- SIMOBJECT_DATA of the position definition (every sim frame): latitude, longitude, altitude, AGL, pitch, bank, true heading, IAS, groundspeed, g, on-ground - the poll's last frame as a row, every frame for touchdowns and takeoffs
- SIMOBJECT_DATA of the motion definition (about 10 Hz: TAS, Mach, vertical speed, AoA, sideslip, magnetic heading, body velocity, acceleration and rotation rate on three axes) and of the state definition (1 Hz: weights, fuel, flaps, gear, spoilers, parking brake, autopilot, engines, throttle and RPM, outside temperature, wind, sea-level pressure, sim rate, zulu and local time, camera state) onto the rows as last received
- SIMOBJECT_DATA of the names definition (title, ATC type, model and id) into meta.json and the rows' `aircraft`; OPEN (application and version) into meta.json
- EVENT and EVENT_FILENAME: SimStart, SimStop, Crashed, FlightLoaded (the flight file) and AircraftLoaded (the aircraft file) as flights, crashes and meta.json
- QUIT ends the session

**Kept raw**

- every message SimConnect hands the watcher, whole as `payload`, under its SIMCONNECT_RECV_ID name: `SIMOBJECT_DATA`, `EVENT`, `EVENT_FILENAME`, `OPEN`, `QUIT`, `EXCEPTION` (a variable or event the sim did not accept, with the send id and index), any other id by its name or `RECV_<id>`
- what only the raw sidecar holds: every sim frame's position between the rows, the Pause, Sim, CrashReset, PositionChanged and FlightSaved events, a definition the sim cut short (one variable it did not know: the block is then not read by name); meta.json's `requests` lists every definition's variables and units in order, so the payloads read without this module

**Not available**

- other aircraft (AI traffic, other players online): SimConnect_RequestDataOnSimObjectType would poll every aircraft in a radius - more load on the sim, and other players' flights
- the motion block every sim frame: it is asked for every sixth frame (about 10 Hz, the rows' rate), which keeps the raw feed near a fifth of the size; the position block stays every frame
- the thousands of other simulation variables (radios, lights, every engine's gauges, failures): a definition holds what it asks for; the lists ask for the flight, the aircraft's state and the sim's time
- weather observations, facilities (airports, VORs), client data of add-ons: separate requests, not made

**Size**: about 30-55 MB an hour before zstd: the position block every sim frame (about 200 bytes with its frame, 30-60 a second), the motion block at about 10 Hz (about 240 bytes), the state block once a second; zstd shrinks the doubles several times

## Verified

message decoding tested on buffers built from SimConnect.h's layouts; the live SimConnect connection is untested (no SimConnect.dll on the test machine)

## Source

[heat3d_watch/adapters/msfs.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/msfs.py)

*Generated from the adapter by `tools/gen_game_pages.py`; change the adapter and run it again rather than editing this page.*
