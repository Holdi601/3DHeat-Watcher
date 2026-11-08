---
title: "DCS World (telemetry)"
parent: Games
nav_order: 10
---

# DCS World (telemetry)

Adapter `dcs` - kind [`telemetry`](sources-and-rules.md) - runs while `DCS.exe` is running - looks for new data every 0.1 s.

## What is recorded

- own position at 10 Hz as metres east/up/north of the theatre's origin (from latitude/longitude/altitude); lat/lon/alt and DCS's own world metres (dcs_x north, dcs_y up, dcs_z east) as columns
- attitude, indicated and true airspeed, Mach, vertical speed, angle of attack and sideslip, magnetic heading, AGL and radar altitude, g on three axes, velocity and rotation rates, in the air, the camera's position and forward vector, aircraft type
- takeoffs and landings with the airfield; crashes, ejections, pilot deaths
- kills and being shot down with both unit types and the weapon; other game events as given
- lives per mission (spawn ... session_end), kills, deaths, distance, highest altitude, highest g
- every line the hook sends kept whole in heat.raw.parquet, with a once-a-second dump of the aircraft's export tables (engines, gear and flaps, payload, countermeasures, route, navigation) and every other callback (pause, chat, players joining, mission loading)

## Where it comes from

the watcher's hook %USERPROFILE%\Saved Games\DCS\*\Scripts\Hooks\heat3d-watch.lua, UDP lines to 127.0.0.1:41993

## How to switch it on

python -m heat3d_watch setup dcs --apply (adds Scripts\Hooks\heat3d-watch.lua), then restart DCS

`python -m heat3d_watch setup dcs` lists the files it would change; `python -m heat3d_watch setup dcs --apply` changes them, keeping the original as `<file>.heat3d-backup` (see [Commands](commands.md#setup)).

## How it works

DCS World: a small hook script of the watcher's own, sending UDP lines to 127.0.0.1:41993.

DCS runs Lua files in `Saved Games\DCS*\Scripts\Hooks\` at start; a hook can
read the export functions (`Export.Lo*`) and receive the simulation's callbacks
(`DCS.setUserCallbacks`: onSimulationStart/Frame/Stop, onGameEvent) - see
`<DCS>\API\DCS_ControlAPI.html` and <https://wiki.hoggitworld.com/view/DCS_Export_Script>.
`setup` writes `heat3d-watch.lua` there (its own file: Export.lua and other
tools' hooks are not touched), which sends ten lines a second, one more a
second, and one per game event or callback, never waiting for an answer. The
port is 41993 so JoyPro's hook (41992) and Tacview (42674) keep working beside
it. The lines (fields split by ';'):

```text
hello;v=2                                       the hook was loaded
start;mission=..;map=..;me=<player id>;name=..;mp=0|1;file=..;server=0|1
mis;t=..;date.Day=..;start_time=..;weather...   the mission's date, start time and weather, flattened
p;t=<model s>;x=;y=;z=;lat=;lon=;alt=;hdg=;pitch=;bank=;ias=;agl=;g=;type=;tas=;mach=;vv=;aoa=;aos=;
  mhdg=;ralt=;gx=;gz=;vx=;vy=;vz=;wx=;wy=;wz=;air=;cx=;cy=;cz=;cfx=;cfy=;cfz=
d;t=..;self.Name=..;eng.RPM.left=..;mech.gear.value=..;pay.Stations.1.count=..;...   once a second
ev;t=..;name=<onGameEvent name>;args=a|b|c      every onGameEvent
cb;t=..;name=<callback>;args=a|b                every other callback (pause, chat, players, loading)
noexport;t=..                                   the server forbids ownship export
stop;t=..                                       the mission ended
```

`p` is LoGetSelfData: Position x/y/z - DCS's own world metres, x north, y up,
z east - plus LatLongAlt (degrees, m), Heading/Pitch/Bank (radians), with
LoGetIndicatedAirSpeed (m/s), LoGetAltitudeAboveGroundLevel (m) and
LoGetAccelerationUnits() x/y/z (g); and, as `Scripts\Export.lua` documents
them, LoGetTrueAirSpeed (m/s), LoGetMachNumber, LoGetVerticalVelocity (m/s),
LoGetAngleOfAttack and LoGetAngleOfSideSlip (rad), LoGetMagneticYaw (rad),
LoGetRadarAltimeter (m), LoGetVectorVelocity (world m/s), LoGetAngularVelocity
(rad/s), LoGetInAir, and LoGetCameraPosition's point and forward vector (world
metres). `d` is a once-a-second dump of whole tables, flattened to dotted keys:
LoGetSelfData (country, coalition, unit and group names, type levels, flags),
LoGetEngineInfo, LoGetMechInfo, LoGetPayloadInfo, LoGetSnares, LoGetWingInfo,
LoGetVectorWindVelocity, LoGetFMData, LoGetNavigationInfo, LoGetRoute,
LoGetMCPState, LoGetControlPanel_HSI, LoGetRadioBeaconsStatus and a few
numbers (pause, time acceleration, seat, pressure, deviations). The watcher
keeps every line whole in the raw sidecar; `p` also becomes the rows.

Positions go into the same flat map as the other flight sims' (`Tangent`: x
east, y altitude above sea level, z north, metres) from LatLongAlt, around the
theatre's fixed origin (`THEATRES`, from the `map` of the start line), so every
mission on one theatre shares one map, and one the viewer can lay the real
world under. A theatre not in the table takes the first fix's latitude and
longitude rounded to whole degrees. DCS's own x/y/z are kept as `dcs_x`,
`dcs_y`, `dcs_z`; a fix without LatLongAlt cannot be placed and is only
counted (`fixes_without_latlon`). The origin is the session's `geo`, in
meta.json and the table's footer.

onGameEvent's arguments, as DCS_ControlAPI
gives them: takeoff/landing (playerID, unit_missionID, airdromeName),
crash/eject/pilot_death (playerID, unit_missionID), kill (killerPlayerID,
killerUnitType, killerSide, victimPlayerID, victimUnitType, victimSide,
weaponName), self_kill (playerID), change_slot (playerID, slotID, prevSide),
mission_end (winner, msg).

A multiplayer server can forbid ownship export (LoIsOwnshipExportAllowed is
false); then there are no positions, only events, and the session says so.

## Positions and axes

| | |
|---|---|
| Positions recorded | yes |
| Up axis | `y` |
| Units | metres (east, altitude, north from the theatre's origin) |
| Mirrored for the viewer | `z` |
| Unit scale (`scale`: the viewer multiplies positions by it) | 1 |

These go into each session's `meta.json` (`axes`) and, when the session has positions, into `heat.parquet`'s footer, so the 3DHeat viewer turns and scales the rows by itself - see [The data](the-data.md).

## Multiplayer

- Marked as played online (`multiplayer`): **yes**. `games --markdown` shows this as "allowed (reads only what the game publishes)".
- Kind `telemetry`: it reads only what the game or platform hands out (a UDP port or shared memory the game publishes), so it records in online play as well as offline; the flag decides only whether memory may ever be read.
- Memory: **never** read by this adapter. Only `memory` adapters read memory, and never for a game marked as played online - see [Sources and rules](sources-and-rules.md).

## Statistics recorded

Statistic keys this adapter's code sets by name (each session's `stats` in `meta.json` and the `stats` table of `watcher.sqlite`):

`airborne_time`, `bad_packets`, `crashes`, `deaths`, `distance_km`, `ejections`, `export_blocked`, `fixes_without_latlon`, `flight_time`, `kills`, `max_altitude_m`, `max_g`, `shot_down`, `{event}s`

A key in braces is completed at run time (`score.{team}` is one key per team). Keys the code takes from a table of the game's fields or from the game's own stat names are not in this list; "What is recorded" above names them.

## Completeness

The watcher follows 3DHeat's [converter rule](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md): what the source holds is read or kept, never dropped. Besides the rows, every packet, page, line or reply the adapter receives is kept whole in the session's `heat.raw.parquet` (columns `time`, `ms`, `type`, `used`, `payload`, `text`, then any field kept by name; `used` marks what also became rows), and `meta.json`'s `selfCheck.completeness` counts each `type` - `lost` is 0.

**Read**

- `p` (10 Hz): position, LatLongAlt, attitude, IAS, AGL, g (x/y/z), aircraft type, and hook 2's TAS, Mach, vertical speed, AoA, sideslip, magnetic heading, radar altitude, world velocity, rotation rates, in-air and camera point/forward vector - all as row columns (units as Export.lua gives them)
- `start`: mission, theatre, own player id and name, multiplayer, mission file, server; `mis`: the mission's date and start time into meta.json
- `ev`: every onGameEvent as a row (takeoff, landing, crash, eject, pilot_death, kill, self_kill, change_slot, connect, disconnect, friendly_fire, mission_end, any other name as given)
- `noexport` and `stop` as rows and meta.json

**Kept raw**

- every line the hook sends, whole, as `text` under its kind: `hello`, `start`, `mis`, `p`, `d`, `ev`, `cb`, `noexport`, `stop`; a line of any other kind under `unknown`
- `d` (1 Hz, raw only): LoGetSelfData whole (country, coalition, unit and group name, type levels, flags), LoGetEngineInfo, LoGetMechInfo, LoGetPayloadInfo, LoGetSnares, LoGetWingInfo, wind vector, LoGetFMData, LoGetNavigationInfo, LoGetRoute, LoGetMCPState, HSI, radio beacons, pause, time acceleration, seat, pressure, deviations - flattened to dotted keys
- `mis`: the mission's weather table, flattened; `cb`: onSimulationPause/Resume, onMissionLoad\*, onNet\*, onPlayerConnect/Disconnect/Start/Stop/ChangeSlot, onChatMessage, onTriggerMessage, onRadioMessage, onRadioCommand, onShowMessage with their arguments

**Not available**

- other units (LoGetWorldObjects, LoGetObjectById) and sensor data (LoGetTargetInformation, LoGetLockedTargetInformation, LoGetTWSInfo, LoGetWingTargets, LoGetSightingSystemInfo): not requested - every object of a mission at 10 Hz is costly inside DCS's own frame, and a server gates them (allow_object_export, allow_sensor_export); Tacview records them
- the whole mission table (DCS.getCurrentMission holds every unit and trigger, megabytes): only its date, start time, weather, sortie, theatre and version are sent
- the onPlayerTry\* callbacks: they answer DCS (allow or refuse), so the hook leaves them alone
- other players' addresses and UCIDs: net.get_player_info gives them only to a server, and they are not the player's to keep
- a table's entries past 800 keys or 6 levels deep in one `d` line are cut, so one line stays one datagram

**Size**: about 20 MB an hour of `p` lines (10 a second, about 500 bytes each with its frame) and 15-40 MB of `d` dumps (one a second, 4-10 KB depending on the aircraft's payload and route), before zstd; the repeated keys compress about tenfold

## Verified

line format tested with synthetic datagrams; the Lua hook is untested inside DCS (written from the DCS hook/export API and Scripts\Export.lua's list of Lo\* functions, not run)

## Source

[heat3d_watch/adapters/dcs.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/dcs.py)

*Generated from the adapter by `tools/gen_game_pages.py`; change the adapter and run it again rather than editing this page.*
