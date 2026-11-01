
# War Thunder (gsi)

Adapter `warthunder-webmap` - kind [`gsi`](sources-and-rules) - runs while `aces.exe` is running - looks for new data every 0.5 s.

## What is recorded

- own position (map east/north in metres; height from /state in aircraft, else 0) twice a second, heading, speed
- spawns and the own vehicle leaving the map (destroyed, landed, back to the hangar), one sortie each
- other aircraft and ground units on the minimap as positions with tracked ids and side (no height)
- airfields, capture zones and bases once, and zones changing side
- kill and damage feed lines (who, vehicle, verb); the player's kills and deaths when your name is set (`config --set player_names.warthunder-webmap=<name>`)
- spawns, distance, top altitude, top true airspeed, vehicle; kills and deaths with your name set

## Where it comes from

the game's local web map, <http://127.0.0.1:8111> (/map_info.json, /map_obj.json, /state, /indicators, /hudmsg)

## How to switch it on

Nothing needs switching on: the watcher reads the source as the game or platform provides it.

## How it works

War Thunder: the game's own local web map on <http://127.0.0.1:8111>.

The game serves the page a second screen or a phone can show (the "web map"),
and the JSON behind it, while it runs - in every mode, multiplayer included:

```text
/map_info.json   {"map_min": [x, y], "map_max": [x, y], "grid_steps", "grid_zero", "map_generation",
                  "hud_type", "valid"}: the map's extent in metres; valid false in the hangar
/map_obj.json    [{"type": aircraft|ground_model|airfield|capture_zone|bombing_point|defending_point|
                  respawn_base_*|..., "icon": Player|Fighter|Bomber|Mediumtank|SPAA|..., "color": "#rrggbb",
                  "x", "y" (0..1 of the map picture, y down), "dx", "dy" (direction),
                  airfields "sx", "sy", "ex", "ey"}]: what the minimap shows, the player's own
                  vehicle with icon "Player"; no ids, no heights
/state           {"valid", "H, m", "TAS, km/h", "IAS, km/h", "M", "Vy, m/s", ...}: flight values,
                  valid only in an aircraft
/indicators      {"valid", "army": air|tank|..., "type": the vehicle}
/hudmsg?lastEvt=N&lastDmg=M   {"events": [...], "damage": [...]} newer than the ids given, each
                  {"id", "msg", "sender", "enemy", "mode", "time"}; damage lines read like
                  "Name (Vehicle) shot down Name (Vehicle)"
```

A map position becomes metres with the extent: u = min_x + x \* (max_x - min_x)
east, v = max_y - y \* (max_y - min_y) north (the picture's y runs down). Rows are
x = u, y = height (the own aircraft's "H, m"; 0 for everything else), z = v, so
Y is up; z is mirrored for the viewer so that north is not drawn south.

Colours tell the sides as the player sees them: own yellow (#faC81E by default),
squad green, allies blue (#174DFF), enemies red (#f40C00); colour-blind palettes
change them, so the hue decides, not the exact value. The game names nobody on
the map and gives objects no ids: other objects get ids here by following them
from poll to poll (nearest of the same type and icon), which may swap two
aircraft of one type that pass close by. The player's own name is not in the
API either: give it in the settings (`config --set
player_names.warthunder-webmap=<your name>`) and kill-feed lines about the
player become kills and deaths; without it they are recorded as the kill feed.

Sources: the game's own page at <http://127.0.0.1:8111> and its JSON; field facts
as documented by the JoyPro 2 project (docs/telemetry-recording.md; GPL, used for
facts only).

## Positions and axes

| | |
|---|---|
| Positions recorded | yes |
| Up axis | `y` |
| Units | metres (map east/north; height only for the own aircraft) |
| Mirrored for the viewer | `z` |
| Unit scale (`scale`: the viewer multiplies positions by it) | 1 |

These go into each session's `meta.json` (`axes`) and, when the session has positions, into `heat.parquet`'s footer, so the 3DHeat viewer turns and scales the rows by itself - see [The data](the-data).

## Multiplayer

- Marked as played online (`multiplayer`): **yes**. `games --markdown` shows this as "allowed (reads only what the game publishes)".
- Kind `gsi`: it reads only what the game or platform hands out (a game-state integration or local API the game serves), so it records in online play as well as offline; the flag decides only whether memory may ever be read.
- Memory: **never** read by this adapter. Only `memory` adapters read memory, and never for a game marked as played online - see [Sources and rules](sources-and-rules).

## Statistics recorded

Statistic keys this adapter's code sets by name (each session's `stats` in `meta.json` and the `stats` table of `watcher.sqlite`):

`bad_packets`, `deaths`, `distance_m`, `hits_dealt`, `hits_taken`, `kills`, `max_altitude_m`, `max_tas_kmh`, `spawns`, `vehicle`

A key in braces is completed at run time (`score.{team}` is one key per team). Keys the code takes from a table of the game's fields or from the game's own stat names are not in this list; "What is recorded" above names them.

## Verified

tested against a fake local server serving answers in the format of the game's web map; War Thunder is installed here but was not run

## Source

[heat3d_watch/adapters/warthunder.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/warthunder.py)

*Generated from the adapter by `tools/gen_game_pages.py`; change the adapter and run it again rather than editing this page.*
