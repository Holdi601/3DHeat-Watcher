---
title: "Squad (replays)"
parent: Games
nav_order: 41
---

# Squad (replays)

After a match of Squad, the watcher turns the replay the game saved into files you can look at on a map in the 3DHeat viewer.

*Technical details: adapter `squad-demos`, kind [`replay`](sources-and-rules.md); it runs all the time (it does not wait for a game to start) and looks for new data every 5 s.*

## What is recorded

- every player's position, body yaw and speed each time the server replicates it (up to 8 times a second), on foot and in ground vehicles
- each player's name, team, faction and squad, following team changes
- not: helicopters' movement, kills and deployables - see the reader's README

## Where it comes from

server demos Squad records with the admin command AdminDemoRec: &lt;server>/SquadGame/Saved/Demos/\*.replay, read by the external reader `heat3d-squad-demo` (exporters/ext/squad-demo)

## How to switch it on

record on the server: give the admin the `demos` permission in Admins.cfg, then AdminDemoRec &lt;name> and AdminDemoStop in the game's console; copy the demo here and install the reader: pip install -e &lt;3DHeat>/exporters/ext/squad-demo

Settings from environment variables:

- `HEAT3D_SQUAD_DEMO`: the converter's folder (a clone or unpacked release), when it is not installed or beside the watcher

## How it works

Replays and demos: what a game saves of a match, converted once the match is over.

A replay holds everything a live interface keeps back in multiplayer games -
every player's position, every kill where it happened - and it is a file the
game writes for its players, so reading it touches nothing in the game. The
watcher looks at the folders games save them to, waits until a new file has
stopped growing (the game is still writing it otherwise), and converts it in a
worker thread, so a long conversion never holds up the rest of the watcher.

The first time a folder is seen, the replays already in it are only noted, not
converted: a player with years of demos would otherwise find the watcher busy
for a day. `python -m heat3d_watch replays <adapter> [folder]` converts the
existing ones on request.

#### Squad

Squad's dedicated servers record a demo of a match when an admin with the
`demos` permission runs AdminDemoRec &lt;name> (and AdminDemoStop), into
`<server>/SquadGame/Saved/Demos/<name>.replay` - an Unreal Engine network
replay holding what the server replicated, every player's movement included.
The watcher does not read them itself: an external reader does (3DHeat Squad
demo reader, `exporters/ext/squad-demo`, command `heat3d-squad-demo`), kept
apart so that a problem with it touches nothing else. It is run on each new
demo in the folders a local server writes to, or in a folder the settings add
for demos copied off a rented server, into the session folder as
`<map>/<match>.parquet` and `<match>.match.json`. The layer, the map, the
number of players and the match length become the session's statistics.

The same module also serves: [Counter-Strike 2 (replays)](game-cs2-demos.md), [Dota 2 (replays)](game-dota-replays.md), [osu! (replays)](game-osu-replays.md), [War Thunder (replays)](game-warthunder-replays.md), [World of Tanks (replays)](game-wot-replays.md), [World of Warships (replays)](game-wows-replays.md).

## Positions and axes

| | |
|---|---|
| Positions recorded | yes |
| Up axis | `z` |
| Units | Unreal units (centimetres) |
| Mirrored for the viewer | none |
| Unit scale (`scale`: the viewer multiplies positions by it) | 1 |

These go into each session's `meta.json` (`axes`) and, when the session has positions, into `heat.parquet`'s footer, so the 3DHeat viewer turns and scales the rows by itself - see [The data](the-data.md).

## Multiplayer

- Marked as played online (`multiplayer`): **yes**. `games --markdown` shows this as "allowed (reads only what the game publishes)".
- Kind `replay`: it reads only what the game or platform hands out (replays and demos the game saves), so it records in online play as well as offline; the flag decides only whether memory may ever be read.
- Memory: **never** read by this adapter. Only `memory` adapters read memory, and never for a game marked as played online - see [Sources and rules](sources-and-rules.md).

## Statistics recorded

Statistic keys this adapter's code sets by name (each session's `stats` in `meta.json` and the `stats` table of `watcher.sqlite`):

`layer`, `map`, `match_seconds`, `players`

A key in braces is completed at run time (`score.{team}` is one key per team). Keys the code takes from a table of the game's fields or from the game's own stat names are not in this list; "What is recorded" above names them.

## Completeness

The converter this adapter runs follows 3DHeat's [converter rule](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md): what the replay holds is read or kept, never dropped - read into the table and the match document, everything else kept whole in sidecars beside them, counted in the match document's `selfCheck.completeness`. The converter's own documentation lists what it reads, keeps raw and cannot read.

## Verified

the reader is checked on public server demos (movement agrees with the velocity it carries; every row's team matches its soldier's faction) and by tests on built demos; this hook by tests with a stand-in command

## Source

[heat3d_watch/adapters/replays.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/replays.py)

<!-- Generated from the adapter by tools/gen_game_pages.py; change the adapter and run it again rather than editing this page. -->
