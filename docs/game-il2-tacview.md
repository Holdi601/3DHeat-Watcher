---
title: "IL-2 Sturmovik: Great Battles (replay)"
parent: Games
nav_order: 27
---

# IL-2 Sturmovik: Great Battles (replay)

Adapter `il2-tacview` - kind [`replay`](sources-and-rules.md) - runs always on (it does not wait for a game to start) - looks for new data every 5 s.

## What is recorded

- every aircraft, vehicle and ship of the recording: positions once a second (metres east/up/north of the recording's reference point; lat/lon/alt as columns)
- spawns, destructions (death) and departures (left), takeoffs and landings when recorded
- objects, destroyed, takeoffs, landings and length per recording

## Where it comes from

the game's own Tacview recordings &lt;game>\data\Tracks\\\*.acmi (ACMI 2.x text, plain or zipped)

## How to switch it on

python -m heat3d_watch setup il2-tacview --apply (tacviewrecord = 1 in [KEY = track_record])

`python -m heat3d_watch setup il2-tacview` lists the files it would change; `python -m heat3d_watch setup il2-tacview --apply` changes them, keeping the original as `<file>.heat3d-backup` (see [Commands](commands.md#setup)).

## How it works

IL-2 Sturmovik: Great Battles - the game's telemetry UDP output, and its own Tacview recordings.

1. Telemetry ("Telemetry output of IL2 v4.003", revision 1.2, shipped as
   `<game>\Doc\UDP_Output\Il2_TeleOutput.pdf`). Switched on in
   `<game>\data\startup.cfg`, section `[KEY = telemetrydevice]`: `addr`,
   `addr1`, ... = "IP[:port]" (several targets at once), `decimation` (50 Hz /
   n), `enable`, `port`. `setup` adds one target, 127.0.0.1:41995 (JoyPro uses
   41994, the game's default is 4322), and switches the output on. Packets,
   little-endian:

   ```text
   DWORD  Packet_ID 0x54000101
   WORD   Size
   DWORD  Tick (1/50 s)
   BYTE   Indicators_Count, then SIndicator {WORD id, BYTE n, n x 32-bit float}
   BYTE   Events_Count,     then SEvent     {WORD id, BYTE size, size bytes}
   ```

   Indicators: 0 ENG_RPM, 1 ENG_MP, 2/3 engine shake, 4 LGEARS_STATE, 5
   LGEARS_PRESS, 6 EAS (m/s), 7 AOA (rad), 8 ACCELERATION (xyz incl. gravity),
   9 COCKPIT_SHAKE, 10 AGL (m), 11 FLAPS, 12 AIR_BRAKES, 13 AOS (rad), 14
   VERTICAL_SPEED (m/s). Events (2-byte packed): 0 SET_FOCUS (STRING: length
   byte + ASCII), 1-3 SETUP_ENG/GUN/LGEAR, 4 DROP_BOMB and 5 ROCKET_LAUNCH
   {float pos[3], float mass, WORD flags}, 6 HIT and 7 DAMAGE {float pos[3],
   float force[3]}, 8 EXPLOSION {float pos[3], float radius}, 9 GUN_FIRE {BYTE
   gun}, 10 SRV_ADDR, 11 SRV_TITLE, 12 SRS_ADDR (STRING), 13 CLIENT_DAT {long
   client, long server client, char name[32]}, 14 CTRL_DAT {long parent, short
   coalition}. Event positions are local to the player's aircraft; the stream
   has no world position at all - so these are events and numbers, not a track.

2. Tacview recording: `tacviewrecord = 1` in `[KEY = track_record]` makes the
   game write `<game>\data\Tracks\*.acmi` (in multiplayer the server decides).
   A finished file is converted: every aircraft, vehicle and ship with its
   positions, spawn and removal (destroyed or gone), takeoffs and landings when
   the recording has them. ACMI 2.x text format, plain or zipped, per
   <https://www.tacview.net/documentation/acmi/en/> - "#t" lines move the clock,
   "id,Key=Value,..." lines set properties (hex ids, commas escaped "\\,", a
   trailing "\\" continues the line), "-id" removes an object, object 0 carries
   the globals (ReferenceLongitude/Latitude, RecordingTime, ...) and the events
   ("Event=Destroyed\|id\|text"). T = Lon\|Lat\|Alt[\|U\|V] or
   Lon\|Lat\|Alt\|Roll\|Pitch\|Yaw[\|U\|V\|Heading], longitude and latitude relative to
   the reference, empty fields unchanged. Positions go into a flat map around
   the reference point: x east, y altitude, z north, metres. The reference
   point is the session's `geo`, carried in meta.json and the table's footer,
   so the viewer can lay the real world under the tracks.

The same module also serves: [IL-2 Sturmovik: Great Battles (telemetry)](game-il2.md).

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
- Kind `replay`: it reads only what the game or platform hands out (replays and demos the game saves), so it records in online play as well as offline; the flag decides only whether memory may ever be read.
- Memory: **never** read by this adapter. Only `memory` adapters read memory, and never for a game marked as played online - see [Sources and rules](sources-and-rules.md).

## Statistics recorded

Statistic keys this adapter's code sets by name (each session's `stats` in `meta.json` and the `stats` table of `watcher.sqlite`):

`destroyed`, `duration_s`, `objects`, `{r.event}s`

A key in braces is completed at run time (`score.{team}` is one key per team). Keys the code takes from a table of the game's fields or from the game's own stat names are not in this list; "What is recorded" above names them.

## Verified

tested on synthetic ACMI 2.2 files (text and zipped); no IL-2 recording on the test machine

## Source

[heat3d_watch/adapters/il2.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/il2.py)

*Generated from the adapter by `tools/gen_game_pages.py`; change the adapter and run it again rather than editing this page.*
