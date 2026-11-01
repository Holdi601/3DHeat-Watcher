
# DCS World (telemetry)

Adapter `dcs` - kind [`telemetry`](sources-and-rules) - runs while `DCS.exe` is running - looks for new data every 0.1 s.

## What is recorded

- own position at 10 Hz in DCS world metres (x north, y up, z east), lat/lon/alt as columns
- attitude, indicated airspeed, AGL, g, aircraft type
- takeoffs and landings with the airfield; crashes, ejections, pilot deaths
- kills and being shot down with both unit types and the weapon; other game events as given
- lives per mission (spawn ... session_end), kills, deaths, distance, highest altitude, highest g

## Where it comes from

the watcher's hook %USERPROFILE%\Saved Games\DCS\*\Scripts\Hooks\heat3d-watch.lua, UDP lines to 127.0.0.1:41993

## How to switch it on

python -m heat3d_watch setup dcs --apply (adds Scripts\Hooks\heat3d-watch.lua), then restart DCS

`python -m heat3d_watch setup dcs` lists the files it would change; `python -m heat3d_watch setup dcs --apply` changes them, keeping the original as `<file>.heat3d-backup` (see [Commands](commands#setup)).

## How it works

DCS World: a small hook script of the watcher's own, sending UDP lines to 127.0.0.1:41993.

DCS runs Lua files in `Saved Games\DCS*\Scripts\Hooks\` at start; a hook can
read the export functions (`Export.Lo*`) and receive the simulation's callbacks
(`DCS.setUserCallbacks`: onSimulationStart/Frame/Stop, onGameEvent) - see
`<DCS>\API\DCS_ControlAPI.html` and <https://wiki.hoggitworld.com/view/DCS_Export_Script>.
`setup` writes `heat3d-watch.lua` there (its own file: Export.lua and other
tools' hooks are not touched), which sends ten lines a second and one per game
event, never waiting for an answer. The port is 41993 so JoyPro's hook (41992)
and Tacview (42674) keep working beside it. The lines (fields split by ';'):

```text
hello;v=1                                       the hook was loaded
start;mission=..;map=..;me=<player id>;name=..;mp=0|1
p;t=<model s>;x=;y=;z=;lat=;lon=;alt=;hdg=;pitch=;bank=;ias=;agl=;g=;type=
ev;t=..;name=<onGameEvent name>;args=a|b|c      every onGameEvent
noexport;t=..                                   the server forbids ownship export
stop;t=..                                       the mission ended
```

`p` is LoGetSelfData: Position x/y/z - DCS's own world metres, x north, y up,
z east - plus LatLongAlt (degrees, m), Heading/Pitch/Bank (radians), with
LoGetIndicatedAirSpeed (m/s), LoGetAltitudeAboveGroundLevel (m) and
LoGetAccelerationUnits().y (g). onGameEvent's arguments, as DCS_ControlAPI
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
| Units | metres (DCS world: x north, y up, z east) |
| Mirrored for the viewer | none |
| Unit scale (`scale`: the viewer multiplies positions by it) | 1 |

These go into each session's `meta.json` (`axes`) and, when the session has positions, into `heat.parquet`'s footer, so the 3DHeat viewer turns and scales the rows by itself - see [The data](the-data).

## Multiplayer

- Marked as played online (`multiplayer`): **yes**. `games --markdown` shows this as "allowed (reads only what the game publishes)".
- Kind `telemetry`: it reads only what the game or platform hands out (a UDP port or shared memory the game publishes), so it records in online play as well as offline; the flag decides only whether memory may ever be read.
- Memory: **never** read by this adapter. Only `memory` adapters read memory, and never for a game marked as played online - see [Sources and rules](sources-and-rules).

## Statistics recorded

Statistic keys this adapter's code sets by name (each session's `stats` in `meta.json` and the `stats` table of `watcher.sqlite`):

`airborne_time`, `bad_packets`, `crashes`, `deaths`, `distance_km`, `ejections`, `export_blocked`, `flight_time`, `kills`, `max_altitude_m`, `max_g`, `shot_down`, `{event}s`

A key in braces is completed at run time (`score.{team}` is one key per team). Keys the code takes from a table of the game's fields or from the game's own stat names are not in this list; "What is recorded" above names them.

## Verified

line format tested with synthetic datagrams; the Lua hook is untested inside DCS (written from the DCS hook/export API, not run)

## Source

[heat3d_watch/adapters/dcs.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/dcs.py)

*Generated from the adapter by `tools/gen_game_pages.py`; change the adapter and run it again rather than editing this page.*
