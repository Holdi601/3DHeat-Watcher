---
title: "osu! (replay)"
parent: Games
nav_order: 34
---

# osu! (replay)

Adapter `osu-replays` - kind [`replay`](sources-and-rules.md) - runs always on (it does not wait for a game to start) - looks for new data every 5 s.

## What is recorded

- the cursor's path over the playfield (x 0..512, y 0..384) and the keys held, every frame
- score, combo, 300s/100s/50s/misses, accuracy, mods, full combo

## Where it comes from

replays osu! (stable) saves: %LOCALAPPDATA%/osu!/Data/r/\*.osr (every play) and osu!/Replays/\*.osr (exported)

## How to switch it on

Nothing needs switching on: the watcher reads the source as the game or platform provides it.

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

#### Counter-Strike 2

CS2 saves the demos a player downloads from the match history (watch tab) to
`<CS2>/game/csgo/replays/` and ones recorded with the `record` console command
to `<CS2>/game/csgo/`. Each is converted with this repository's own CS2
converter (3DHeat CS2, github.com/Holdi601/3DHeat-CS2: every player's position, look direction, health and
money every eighth tick; kills, deaths, damage, grenades, plants and defuses
where they happened; rounds, score, economy) into the session folder, as the
`<map>/<match>.parquet` table and `<match>.match.json` summary the viewer's heat
and match tabs read. The match's scoreboard becomes the session's statistics:
for the player whose Steam account is signed in on this machine (from Steam's
`loginusers.vdf`) under its plain names - kills, deaths, assists, ADR, KAST,
headshot percentage, opening kills, clutches - and the score and rounds.

The same module also serves: [Counter-Strike 2 (replay)](game-cs2-demos.md).

## Positions and axes

| | |
|---|---|
| Positions recorded | yes |
| Up axis | `y` |
| Units | osu! pixels (playfield 512 x 384) |
| Mirrored for the viewer | `z` |
| Unit scale (`scale`: the viewer multiplies positions by it) | 1 |

These go into each session's `meta.json` (`axes`) and, when the session has positions, into `heat.parquet`'s footer, so the 3DHeat viewer turns and scales the rows by itself - see [The data](the-data.md).

## Multiplayer

- Marked as played online (`multiplayer`): **yes**. `games --markdown` shows this as "allowed (reads only what the game publishes)".
- Kind `replay`: it reads only what the game or platform hands out (replays and demos the game saves), so it records in online play as well as offline; the flag decides only whether memory may ever be read.
- Memory: **never** read by this adapter. Only `memory` adapters read memory, and never for a game marked as played online - see [Sources and rules](sources-and-rules.md).

## Statistics recorded

Statistic keys this adapter's code sets by name (each session's `stats` in `meta.json` and the `stats` table of `watcher.sqlite`):

`accuracy`, `full_combo`

A key in braces is completed at run time (`score.{team}` is one key per team). Keys the code takes from a table of the game's fields or from the game's own stat names are not in this list; "What is recorded" above names them.

## Verified

tested on replays built to the published .osr format; osu!lazer keeps replays in its own store and is not read

## Source

[heat3d_watch/adapters/replays.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/replays.py)

*Generated from the adapter by `tools/gen_game_pages.py`; change the adapter and run it again rather than editing this page.*
