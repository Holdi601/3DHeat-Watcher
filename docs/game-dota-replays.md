---
title: "Dota 2 (replay)"
parent: Games
nav_order: 12
---

# Dota 2 (replay)

Adapter `dota-replays` - kind [`replay`](sources-and-rules.md) - runs always on (it does not wait for a game to start) - looks for new data every 5 s.

## What is recorded

- every hero's position, height, health and level, 7.5 times a second while alive
- kills and deaths where they happened; towers, barracks, Roshan and Tormentors where they fell; wards where they were planted
- every player's map pings, map drawings and orders (move, attack, cast, buy, ...) where they pointed
- the score and every player's line; the signed-in player's as statistics
- everything else the replay holds, kept whole beside the table: every frame and network message, every entity property change, every string table entry

## Where it comes from

replays Dota 2 saves: &lt;Dota>/game/dota/replays/&lt;match id>.dem (downloaded in the client, or with `dota-replay <match id>`)

## How to switch it on

download a match's replay in Dota 2, or fetch a public one: `python -m heat3d_watch dota-replay <match id>`; needs `pip install gem-dota`

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
planted and where it ended, the combat log's entries about the heroes
(damage, heals, abilities, items, purchases, runes, gold, experience,
modifiers), and every player's map pings, map drawings and orders - into
`dota/<match>.parquet`; every other unit (creeps, summons, illusions,
couriers, buildings) once a second into `<match>.units.parquet`; the whole
combat log into `<match>.combatlog.parquet`; and the match, the chat, the
draft, everything else the parser extracts and the game's own end-of-match
record into `<match>.match.json`, in the session folder. Everything else
the replay holds is kept whole beside them (3DHeat's converter rule):
every frame and network message in `<match>.packets.parquet`, every entity
property change in `<match>.entities.parquet`, every string table entry in
`<match>.strings.parquet`, counted in the match document's
`selfCheck.completeness`. Positions are Dota's world
units, the same the game-state integration reports. The signed-in player's
scoreboard line becomes the session's statistics: kills, deaths, assists,
last hits, denies, net worth, GPM, XPM, hero damage, wards, and whether the
match was won. A new Dota patch can change the replay's entities before gem
follows; a replay gem cannot read to the end is converted as far as it goes
and marked `incomplete` in its summary.

#### osu!

osu! (stable) saves every play to `osu!/Data/r/*.osr` and exported ones to
`osu!/Replays/`. The watcher reads them itself, to the format the osu! wiki
publishes: the cursor's path and keys every frame, the score line, the life
bar, the seed and the score id; the file is kept whole beside, part by part,
in the session's `heat.raw.parquet`.

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

The same module also serves: [Counter-Strike 2 (replay)](game-cs2-demos.md), [osu! (replay)](game-osu-replays.md), [Squad (replay)](game-squad-demos.md), [War Thunder (replay)](game-warthunder-replays.md), [World of Tanks (replay)](game-wot-replays.md), [World of Warships (replay)](game-wows-replays.md).

## Positions and axes

| | |
|---|---|
| Positions recorded | yes |
| Up axis | `z` |
| Units | Dota world units (Hammer units; the map is about 16400 across) |
| Mirrored for the viewer | `y` |
| Unit scale (`scale`: the viewer multiplies positions by it) | 1 |

These go into each session's `meta.json` (`axes`) and, when the session has positions, into `heat.parquet`'s footer, so the 3DHeat viewer turns and scales the rows by itself - see [The data](the-data.md).

## Multiplayer

- Marked as played online (`multiplayer`): **yes**. `games --markdown` shows this as "allowed (reads only what the game publishes)".
- Kind `replay`: it reads only what the game or platform hands out (replays and demos the game saves), so it records in online play as well as offline; the flag decides only whether memory may ever be read.
- Memory: **never** read by this adapter. Only `memory` adapters read memory, and never for a game marked as played online - see [Sources and rules](sources-and-rules.md).

## Statistics recorded

Statistic keys this adapter's code sets by name (each session's `stats` in `meta.json` and the `stats` table of `watcher.sqlite`):

`duration`, `hero`, `score.{team}`, `team`, `won`

A key in braces is completed at run time (`score.{team}` is one key per team). Keys the code takes from a table of the game's fields or from the game's own stat names are not in this list; "What is recorded" above names them.

## Completeness

The converter follows 3DHeat's [converter rule](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md): what the replay holds is read or kept, never dropped. Besides the table, everything else the replay holds is kept whole in sidecars beside it in the session's `dota/` folder - `<match>.packets.parquet`, `<match>.entities.parquet`, `<match>.strings.parquet` (columns `time`, `tick`, `type`, `name`, `entity`, `decoded`, `payload`, as each applies) - and the match document's (`<match>.match.json`) `selfCheck.completeness` counts each `type` - `lost` is 0.

**Read**

- the table (`dota/<match>.parquet`): every hero's position, height, health, level, facing, mana, experience, attributes, armour, speed, damage, items and the player's cursor 7.5 times a second; kills, deaths, objectives, wards, the combat log's entries about heroes; map pings (`ping`, DOTA_UM_LocationPing), map drawings (`map_line`, DOTA_UM_MapLine) and every unit order (`order`, DOTA_UM_SpectatorPlayerUnitOrders: `other` the order type, `value` the ability or item id, `text` the target's class; at the ordered point, else at the hero)
- `<match>.units.parquet`: every other unit once a second; `<match>.combatlog.parquet`: the whole combat log as gem reads it, every field
- the match document: everything gem extracts, and whole the replay's own records - `fileHeader` (DEM_FileHeader), `fileInfo` (DEM_FileInfo: playback length, every player's name, hero, Steam id, team), `matchDetails` (DOTA_UM_MatchDetails: the game coordinator's end-of-match scoreboard, every player's numbers, items, damage by type, picks and bans) and `matchMetadata` (DOTA_UM_MatchMetadata)
- `selfCheck.crossCheck`: kills, deaths, assists, level, last hits and denies as read from the stream against `matchDetails`, per player

**Kept raw**

- `<match>.packets.parquet`: every frame that is not a packet (`type` `frame <n>`) and every network message (`message <n>`, `name` Valve's), whole in `payload`, in file order (`seq`, `frame`), with `decoded` the protobuf as JSON (a bytes field given as its length) - on the sample 553,048 rows of 52 message types, every one decoded: svc_PacketEntities (the entity stream), DOTA_UM_SpectatorPlayerUnitOrders, UM_ParticleManager, DOTA_UM_CombatLogDataHLTV, GE_SosStartSoundEvent, DOTA_UM_TE_\* (projectiles, animations, blood), DOTA_UM_OverheadEvent, DOTA_UM_UnitEvent, svc_UpdateStringTable, net_Tick, ...; the send tables, class list and server info a later entity decoder needs are among them
- `<match>.entities.parquet`: every entity's every property each time it changed (`type` the property, `name` the class, `entity` its index; `value`, `vector` or `decoded`), its whole state when created, and each creation, entering, leaving and deletion - on the sample 10.2 million rows, 379 classes, 12,598 property names
- `<match>.strings.parquet`: every string table entry from every update and every full snapshot, the value whole; `userinfo`, `ActiveModifiers` and `EconItems` decoded from their protobufs - on the sample 243,842 rows of 20 tables
- `selfCheck.completeness` in the match document counts frames and messages by Valve's name, combat log entries (`combatlog <type>`), game events (`gameevent <name>`), string table entries (`stringtable <name>`) and entity updates (`entity <class>`): on the sample 5,487,369 items of 478 types, 57 kept raw only (53 full entity snapshots gem skips because it rebuilds from the deltas, 4 entries of two tables with values nothing reads), lost 0

**Not available**

- voice: the replay has the voice setup but no voice data
- names behind hashes and ids: sounds and particles are named by hashes of the game's files, abilities by ids; the replay does not carry the names (items are named through gem's catalogue where it has them)
- anything only the players' own clients knew (their camera, their screen) beyond what the server broadcast; the cursor and every order are in

**Size**: on a 70.3 MB replay of a 27-minute match: packets 58.4 MB, entities 40.3 MB, strings 5.3 MB, the table 5.8 MB, units 2.9 MB, combat log 0.8 MB, match document 8.1 MB; about a minute and a half in one process (gem's parse alone about 40 s)

## Verified

checked on a public match's replay (patch 7.40, November 2026): kills and deaths per hero match the scoreboard; every frame and message in the packets sidecar is byte for byte the replay's and every one of the 553,048 re-serialises exactly from its protobuf; the last kills, deaths, assists, level, last hits and denies in the entities sidecar match the game's own end-of-match record (DOTA_UM_MatchDetails) for all ten players; after 90% of 59,898 move orders the hero is closer to the point a second later; the table and statistics by tests on synthetic data

## Source

[heat3d_watch/adapters/replays.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/replays.py)

*Generated from the adapter by `tools/gen_game_pages.py`; change the adapter and run it again rather than editing this page.*
