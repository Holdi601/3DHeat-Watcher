---
title: "World of Tanks (replays)"
parent: Games
nav_order: 47
---

# World of Tanks (replays)

After a match of World of Tanks, the watcher turns the replay the game saved into files you can look at on a map in the 3DHeat viewer.

*Technical details: adapter `wot-replays`, kind [`replay`](sources-and-rules.md); it runs all the time (it does not wait for a game to start) and looks for new data every 5 s.*

## What is recorded

- every vehicle's position and heading about 10 times a second while the recording client knew of it: its own team throughout, an enemy while spotted
- player, team and vehicle (nation:tank) of each; deaths where the victim fell and kills where the killer stood, to about a second, from the results
- the map; the recording player's kills, damage, survival and the result as statistics

## Where it comes from

replays World of Tanks saves: &lt;World of Tanks>/replays/\*.wotreplay (with battle recording on), converted by the external converter `heat3d-wot-replay` (exporters/ext/wot-replay)

## How to switch it on

turn on battle recording in World of Tanks' settings (General > Record battles) and install the converter: pip install -e &lt;3DHeat>/exporters/ext/wot-replay

Settings from environment variables:

- `HEAT3D_WOT_REPLAY`: the converter's folder (a clone or unpacked release), when it is not installed or beside the watcher

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

#### World of Tanks and World of Warships

Both save a replay of each battle to `<game>/replays/` when recording is on
(`*.wotreplay`, `*.wowsreplay`); the installs are found through the Wargaming
Game Center's list, `C:/Games/World_of_Tanks*` / `World_of_Warships*`, and
Steam. As with War Thunder, the watcher does not read the files itself: an
external converter of each does (`exporters/ext/wot-replay`, command
`heat3d-wot-replay`; `exporters/ext/wows-replay`, command
`heat3d-wows-replay`), kept apart so that a problem with Wargaming's terms
touches only that converter. Found on PATH, installed, or beside the watcher,
it turns each new replay into `<map>/<match>.parquet` and `<match>.match.json`
in the session folder; missing, the watcher says once how to install it. The
recording player's line - vehicle or ship, kills, damage (World of Tanks),
whether they survived, and the result (World of Tanks) - becomes the
session's statistics. What each converter reads, and what it does not, is in
its README.

The same module also serves: [Counter-Strike 2 (replays)](game-cs2-demos.md), [Dota 2 (replays)](game-dota-replays.md), [Squad (replays)](game-squad-demos.md), [War Thunder (replays)](game-warthunder-replays.md), [World of Warships (replays)](game-wows-replays.md).

## Positions and axes

| | |
|---|---|
| Positions recorded | yes |
| Up axis | `y` |
| Units | metres (x east, y up, z north) |
| Mirrored for the viewer | `z` |
| Unit scale (`scale`: the viewer multiplies positions by it) | 1 |

These go into each session's `meta.json` (`axes`) and, when the session has positions, into `heat.parquet`'s footer, so the 3DHeat viewer turns and scales the rows by itself - see [The data](the-data.md).

## Multiplayer

- Marked as played online (`multiplayer`): **yes**. `games --markdown` shows this as "allowed (reads only what the game publishes)".
- Kind `replay`: it reads only what the game or platform hands out (replays and demos the game saves), so it records in online play as well as offline; the flag decides only whether memory may ever be read.
- Memory: **never** read by this adapter. Only `memory` adapters read memory, and never for a game marked as played online - see [Sources and rules](sources-and-rules.md).

## Statistics recorded

Statistic keys this adapter's code sets by name (each session's `stats` in `meta.json` and the `stats` table of `watcher.sqlite`):

`map`, `survived`, `vehicle`, `won`

A key in braces is completed at run time (`score.{team}` is one key per team). Keys the code takes from a table of the game's fields or from the game's own stat names are not in this list; "What is recorded" above names them.

## Completeness

The converter this adapter runs follows 3DHeat's [converter rule](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md): what the replay holds is read or kept, never dropped - read into the table and the match document, everything else kept whole in sidecars beside them, counted in the match document's `selfCheck.completeness`. The converter's own documentation lists what it reads, keeps raw and cannot read.

## Verified

the converter is checked on public replays from several game versions and by tests on built replays; this hook by tests with a stand-in command

## Source

[heat3d_watch/adapters/replays.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/replays.py)

<!-- Generated from the adapter by tools/gen_game_pages.py; change the adapter and run it again rather than editing this page. -->
