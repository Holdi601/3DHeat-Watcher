---
title: "IL-2 Sturmovik: Great Battles (telemetry)"
parent: Games
nav_order: 26
---

# IL-2 Sturmovik: Great Battles (telemetry)

Adapter `il2` - kind [`telemetry`](sources-and-rules.md) - runs while `Il-2.exe` or `IL2Series.exe` is running - looks for new data every 0.1 s.

## What is recorded

- sorties: the aircraft taken (spawn) and when the output stops (session_end) - no world position: the game does not send one
- bombs and rockets released (mass), hits and damage taken, explosions, gunfire bursts - positions local to the aircraft
- equivalent airspeed, AGL, vertical speed, g, engine RPM once a second, with every other indicator the packet carries (manifold pressure, engine shake, gear state and pressure, AoA, sideslip, acceleration x/y/z, cockpit shake, flaps, air brakes)
- sorties, rounds fired, bombs, rockets, hits taken, highest speed, highest g, flight time; server title and pilot name online
- every telemetry packet kept whole in heat.raw.parquet

## Where it comes from

the game's telemetry UDP output to 127.0.0.1:41995 ([KEY = telemetrydevice] in &lt;game>\data\startup.cfg)

## How to switch it on

python -m heat3d_watch setup il2 --apply (adds addrN = "127.0.0.1:41995", enable = true), restart IL-2

`python -m heat3d_watch setup il2` lists the files it would change; `python -m heat3d_watch setup il2 --apply` changes them, keeping the original as `<file>.heat3d-backup` (see [Commands](commands.md#setup)).

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
   byte + ASCII), 1 SETUP_ENG {short index, short id, float pos[3], float
   max_rpm}, 2 SETUP_GUN {short index, float pos[3], float projectile mass,
   float muzzle velocity}, 3 SETUP_LGEAR {short index, short id, float
   pos[3]}, 4 DROP_BOMB and 5 ROCKET_LAUNCH
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

The same module also serves: [IL-2 Sturmovik: Great Battles (replay)](game-il2-tacview.md).

## Positions and axes

| | |
|---|---|
| Positions recorded | no |
| Up axis | `y` |
| Units | none: the telemetry has no world positions |
| Mirrored for the viewer | none |
| Unit scale (`scale`: the viewer multiplies positions by it) | 1 |

These go into each session's `meta.json` (`axes`) and, when the session has positions, into `heat.parquet`'s footer, so the 3DHeat viewer turns and scales the rows by itself - see [The data](the-data.md).

## Multiplayer

- Marked as played online (`multiplayer`): **yes**. `games --markdown` shows this as "allowed (reads only what the game publishes)".
- Kind `telemetry`: it reads only what the game or platform hands out (a UDP port or shared memory the game publishes), so it records in online play as well as offline; the flag decides only whether memory may ever be read.
- Memory: **never** read by this adapter. Only `memory` adapters read memory, and never for a game marked as played online - see [Sources and rules](sources-and-rules.md).

## Statistics recorded

Statistic keys this adapter's code sets by name (each session's `stats` in `meta.json` and the `stats` table of `watcher.sqlite`):

`bad_packets`, `bombs_dropped`, `damage_taken`, `explosions`, `flight_time`, `hits_taken`, `max_agl_m`, `max_eas_kmh`, `max_g`, `ordnance_kg`, `rockets_fired`, `rounds_fired`, `sorties`

A key in braces is completed at run time (`score.{team}` is one key per team). Keys the code takes from a table of the game's fields or from the game's own stat names are not in this list; "What is recorded" above names them.

## Completeness

The watcher follows 3DHeat's [converter rule](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md): what the source holds is read or kept, never dropped. Besides the rows, every packet, page, line or reply the adapter receives is kept whole in the session's `heat.raw.parquet` (columns `time`, `ms`, `type`, `used`, `payload`, `text`, then any field kept by name; `used` marks what also became rows), and `meta.json`'s `selfCheck.completeness` counts each `type` - `lost` is 0.

**Read**

- SET_FOCUS (the aircraft taken: a sortie), DROP_BOMB and ROCKET_LAUNCH (mass, local position), HIT and DAMAGE (local position, force), EXPLOSION (local position, radius), GUN_FIRE (rounds per poll) as rows
- SETUP_ENG (index, id, local position, maximum RPM), SETUP_GUN (index, local position, projectile mass, muzzle velocity) and SETUP_LGEAR (index, id, local position) as rows: the aircraft's engines, guns and gear legs as the sortie begins
- SRV_TITLE, SRV_ADDR, SRS_ADDR and CLIENT_DAT (pilot name) into meta.json; CTRL_DAT's coalition as the sortie's team
- all fifteen indicators of the spec on the once-a-second `state` row (one value as a number, one per engine, gear leg or axis as a list); highest speed, g and AGL from every packet

**Kept raw**

- every datagram whole as `payload`, under its Packet_ID: `0x54000101` for telemetry (used when it made a row or a meta.json entry), any other id as itself, a datagram too short for one as `short`
- what only the raw sidecar holds: the indicators between the once-a-second rows (the game sends them at 50 Hz / decimation), a SETUP event shorter than the spec's layout, event ids the spec does not list

**Not available**

- a world position: the telemetry output has none (event positions are local to the aircraft); the il2-tacview adapter reads positions from the game's own Tacview recordings
- other aircraft and players: the output describes only the player's own aircraft

**Size**: about 8 MB an hour at setup's 10 Hz (decimation 5; a packet is about 160 bytes plus its frame), 40 MB at the game's full 50 Hz, before zstd; zstd shrinks the repetitive floats to a fraction

## Verified

tested on packets built from the game's own Il2_TeleOutput spec (rev 1.2); startup.cfg edits checked on a copy of a real one; untested against the running game

## Source

[heat3d_watch/adapters/il2.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/il2.py)

*Generated from the adapter by `tools/gen_game_pages.py`; change the adapter and run it again rather than editing this page.*
