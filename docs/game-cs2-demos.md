---
title: "Counter-Strike 2 (replay)"
parent: Games
nav_order: 8
---

# Counter-Strike 2 (replay)

Adapter `cs2-demos` - kind [`replay`](sources-and-rules.md) - runs always on (it does not wait for a game to start) - looks for new data every 5 s.

## What is recorded

- every player's position, look direction, health and money (every 8th tick)
- kills, deaths, damage, grenades, plants and defuses where they happened
- rounds, score, economy; the signed-in player's scoreboard line as statistics

## Where it comes from

demos CS2 saves: &lt;CS2>/game/csgo/replays/\*.dem (downloaded from the match history) and &lt;CS2>/game/csgo/\*.dem (recorded)

## How to switch it on

download a match's demo in CS2 (Watch > Your Matches), or record one with the console's `record`

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

#### Dota 2

Dota 2 saves the replays a player downloads (a match's details, or Watch >
Replays) to `<Dota>/game/dota/replays/<match id>.dem`; Valve keeps every public
match's replay on its servers for a few weeks, and `python -m heat3d_watch
dota-replay <match id>` fetches one by its id through OpenDota. Each is read with
gem (github.com/whanyu1212/gem-dota, MIT, `pip install gem-dota`) in a process
of its own (`heat3d_watch/decoders/dota_replay.py`): every hero's position,
height, health, level, facing, mana, experience, attributes and items 7.5
times a second while alive, kills and deaths where they happened, towers,
barracks, Roshan and Tormentors where they fell, every ward where it was
planted and where it ended, and the combat log's entries about the heroes
(damage, heals, abilities, items, purchases, runes, gold, experience,
modifiers) - into `dota/<match>.parquet`; every other unit (creeps, summons,
illusions, couriers, buildings) once a second into `<match>.units.parquet`;
the whole combat log into `<match>.combatlog.parquet`; and the match, the
chat, the draft and everything else the parser extracts into
`<match>.match.json`, in the session folder. Positions are Dota's world
units, the same the game-state integration reports. The signed-in player's
scoreboard line becomes the session's statistics: kills, deaths, assists,
last hits, denies, net worth, GPM, XPM, hero damage, wards, and whether the
match was won. A new Dota patch can change the replay's entities before gem
follows; a replay gem cannot read to the end is converted as far as it goes
and marked `incomplete` in its summary.

#### War Thunder

War Thunder saves a replay of each battle to `<War Thunder>/Replays/*.wrpl`
when replay saving is on in its options. The watcher does not read them
itself: an external converter does (3DHeat War Thunder replay converter,
`exporters/ext/warthunder-replay`, command `heat3d-wt-replay`), kept apart so
that a problem with it touches nothing else. When the command is on PATH, or
the package is installed or beside the watcher, each new replay is run through
it into the session folder as `<map>/<match>.parquet` and `<match>.match.json`;
when it is not, the watcher says once how to install it and leaves the folder
alone. What the converter reads, and what it does not, is in its README. The
replay's author's line of the results - kills, ground kills, deaths, assists,
score, captures - becomes the session's statistics.

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

The same module also serves: [Dota 2 (replay)](game-dota-replays.md), [osu! (replay)](game-osu-replays.md), [Squad (replay)](game-squad-demos.md), [War Thunder (replay)](game-warthunder-replays.md), [World of Tanks (replay)](game-wot-replays.md), [World of Warships (replay)](game-wows-replays.md).

## Positions and axes

| | |
|---|---|
| Positions recorded | yes |
| Up axis | `z` |
| Units | inches (Source units) |
| Mirrored for the viewer | `y` |
| Unit scale (`scale`: the viewer multiplies positions by it) | 1 |

These go into each session's `meta.json` (`axes`) and, when the session has positions, into `heat.parquet`'s footer, so the 3DHeat viewer turns and scales the rows by itself - see [The data](the-data.md).

## Multiplayer

- Marked as played online (`multiplayer`): **yes**. `games --markdown` shows this as "allowed (reads only what the game publishes)".
- Kind `replay`: it reads only what the game or platform hands out (replays and demos the game saves), so it records in online play as well as offline; the flag decides only whether memory may ever be read.
- Memory: **never** read by this adapter. Only `memory` adapters read memory, and never for a game marked as played online - see [Sources and rules](sources-and-rules.md).

## Statistics recorded

Statistic keys this adapter's code sets by name (each session's `stats` in `meta.json` and the `stats` table of `watcher.sqlite`):

`map`, `rounds`, `score.{team}`, `won`

A key in braces is completed at run time (`score.{team}` is one key per team). Keys the code takes from a table of the game's fields or from the game's own stat names are not in this list; "What is recorded" above names them.

## Verified

the converter is tested on 165 real tournament demos; the folder watch and statistics by tests

## Source

[heat3d_watch/adapters/replays.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/replays.py)

*Generated from the adapter by `tools/gen_game_pages.py`; change the adapter and run it again rather than editing this page.*
