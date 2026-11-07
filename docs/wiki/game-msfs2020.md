
# Microsoft Flight Simulator 2020 (telemetry)

Adapter `msfs2020` - kind [`telemetry`](sources-and-rules) - runs while `FlightSimulator.exe` is running - looks for new data every 0.1 s.

## What is recorded

- own aircraft position every sim frame, taken at 10 Hz (latitude/longitude/altitude as metres east/up/north of the first fix; lat/lon/alt kept as columns)
- attitude, indicated airspeed, groundspeed, AGL, g, on-ground
- takeoffs, landings, crashes, flights started and stopped (session_start/session_end)
- flight time, airborne time, distance, highest altitude, highest g, landings

## Where it comes from

SimConnect through the player's own SimConnect.dll (the sim folder, or %MSFS_SDK%\SimConnect SDK\lib)

## How to switch it on

nothing; SimConnect.dll comes with MSFS 2020 (or the MSFS SDK)

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
System events: SimStart, SimStop, Crashed, FlightLoaded.

Positions go into the same flat map as X-Plane's (x east, y altitude, z north
in metres from the sitting's first fix); that fix is the session's `geo`, in
meta.json and the table's footer.

The same module also serves: [Microsoft Flight Simulator 2024 (telemetry)](game-msfs2024).

## Positions and axes

| | |
|---|---|
| Positions recorded | yes |
| Up axis | `y` |
| Units | metres (east, altitude, north from the first fix) |
| Mirrored for the viewer | `z` |
| Unit scale (`scale`: the viewer multiplies positions by it) | 1 |

These go into each session's `meta.json` (`axes`) and, when the session has positions, into `heat.parquet`'s footer, so the 3DHeat viewer turns and scales the rows by itself - see [The data](the-data).

## Multiplayer

- Marked as played online (`multiplayer`): **yes**. `games --markdown` shows this as "allowed (reads only what the game publishes)".
- Kind `telemetry`: it reads only what the game or platform hands out (a UDP port or shared memory the game publishes), so it records in online play as well as offline; the flag decides only whether memory may ever be read.
- Memory: **never** read by this adapter. Only `memory` adapters read memory, and never for a game marked as played online - see [Sources and rules](sources-and-rules).

## Statistics recorded

Statistic keys this adapter's code sets by name (each session's `stats` in `meta.json` and the `stats` table of `watcher.sqlite`):

`airborne_time`, `bad_packets`, `crashes`, `distance_km`, `flight_time`, `max_altitude_m`, `max_g`, `{event}s`

A key in braces is completed at run time (`score.{team}` is one key per team). Keys the code takes from a table of the game's fields or from the game's own stat names are not in this list; "What is recorded" above names them.

## Verified

message decoding tested on buffers built from SimConnect.h's layouts; the live SimConnect connection is untested (no SimConnect.dll on the test machine)

## Source

[heat3d_watch/adapters/msfs.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/msfs.py)

*Generated from the adapter by `tools/gen_game_pages.py`; change the adapter and run it again rather than editing this page.*
