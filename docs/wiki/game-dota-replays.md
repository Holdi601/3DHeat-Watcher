# Dota 2 (replays)

After a match of Dota 2, the watcher turns the replay the game saved into files you can look at on a map in the 3DHeat viewer.

*Technical details: adapter `dota-replays`, kind [`replay`](sources-and-rules); it runs all the time (it does not wait for a game to start) and looks for new data every 5 s.*

## What is recorded

- every hero's position, height, health and level, 7.5 times a second while alive
- kills and deaths where they happened; towers, barracks, Roshan and Tormentors where they fell; wards where they were planted
- every player's map pings, map drawings and orders (move, attack, cast, buy, ...) where they pointed
- the score and every player's line; the signed-in player's as statistics
- everything else the replay holds, kept whole beside the table: every frame and network message, every entity property change, every string table entry

## Where it comes from

replays Dota 2 saves: &lt;Dota>/game/dota/replays/&lt;match id>.dem (downloaded in the client, or with `dota-replay <match id>`)

## How to switch it on

download a match's replay in Dota 2, or fetch a public one: `python -m heat3d_watch dota-replay <match id>`; install the reader: github.com/Holdi601/3DHeat-Ext-DotaReplay (`heat3d-dota-replay`, brings gem-dota)

Type the command in a terminal opened in the watcher's folder (see [Before you start](before-you-start)). If it fails, the last line says why; [Installing and running](installing-and-running) covers the usual causes.

Settings from environment variables:

- `HEAT3D_DOTA_REPLAY`: the reader's folder (a clone or unpacked release), when it is not installed or beside the watcher

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

#### Dota 2

Dota 2 saves the replays a player downloads (a match's details, or Watch >
Replays) to `<Dota>/game/dota/replays/<match id>.dem`; Valve keeps every public
match's replay on its servers for a few weeks, and `python -m heat3d_watch
dota-replay <match id>` fetches one by its id through OpenDota. The watcher
does not read them itself: an external reader does (3DHeat Dota Replay,
github.com/Holdi601/3DHeat-Ext-DotaReplay, `exporters/ext/dota-replay`, command
`heat3d-dota-replay`, reading through gem-dota, MIT), a project of its own,
run in a process of its own on each
new replay when it is on PATH, installed, or beside the watcher; missing, the
watcher says once how to install it. It writes every hero's position,
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

The same module also serves: [Counter-Strike 2 (replays)](game-cs2-demos), [Squad (replays)](game-squad-demos), [War Thunder (replays)](game-warthunder-replays), [World of Tanks (replays)](game-wot-replays), [World of Warships (replays)](game-wows-replays).

## Positions and axes

| | |
|---|---|
| Positions recorded | yes |
| Up axis | `z` |
| Units | Dota world units (Hammer units; the map is about 16400 across) |
| Mirrored for the viewer | `y` |
| Unit scale (`scale`: the viewer multiplies positions by it) | 1 |

These go into each session's `meta.json` (`axes`) and, when the session has positions, into `heat.parquet`'s footer, so the 3DHeat viewer turns and scales the rows by itself - see [The data](the-data).

## Multiplayer

- Marked as played online (`multiplayer`): **yes**. `games --markdown` shows this as "allowed (reads only what the game publishes)".
- Kind `replay`: it reads only what the game or platform hands out (replays and demos the game saves), so it records in online play as well as offline; the flag decides only whether memory may ever be read.
- Memory: **never** read by this adapter. Only `memory` adapters read memory, and never for a game marked as played online - see [Sources and rules](sources-and-rules).

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

- `<match>.packets.parquet`: every frame that is not a packet (`type` `frame <n>`) and every network message (`message <n>`, `name` Valve's), whole in `payload`, in file order (`seq`, `frame`), with `decoded` the protobuf as JSON (a bytes field given as its length), every message type decoded: svc_PacketEntities (the entity stream), DOTA_UM_SpectatorPlayerUnitOrders, UM_ParticleManager, the combat log messages, GE_SosStartSoundEvent, DOTA_UM_TE_\* (projectiles, animations, blood), DOTA_UM_OverheadEvent, DOTA_UM_UnitEvent, svc_UpdateStringTable, net_Tick, ...; the send tables, class list and server info a later entity decoder needs are among them
- `<match>.entities.parquet`: every entity's every property each time it changed (`type` the property, `name` the class, `entity` its index; `value`, `vector` or `decoded`), its whole state when created, and each creation, entering, leaving and deletion - millions of rows for a whole match
- `<match>.strings.parquet`: every string table entry from every update and every full snapshot, the value whole; `userinfo`, `ActiveModifiers` and `EconItems` decoded from their protobufs
- `selfCheck.completeness` in the match document counts frames and messages by Valve's name, combat log entries (`combatlog <type>`), game events (`gameevent <name>`), string table entries (`stringtable <name>`) and entity updates (`entity <class>`); a few are kept raw only (full entity snapshots gem skips because it rebuilds from the deltas, and entries of tables whose values nothing reads), lost 0

**Not available**

- voice: the replay has the voice setup but no voice data
- names behind hashes and ids: sounds and particles are named by hashes of the game's files, abilities by ids; the replay does not carry the names (items are named through gem's catalogue where it has them)
- anything only the players' own clients knew (their camera, their screen) beyond what the server broadcast; the cursor and every order are in

**Size**: the sidecars together are somewhat larger than the replay itself, the packets and the entities the biggest; a whole match takes a minute or two in one process

## Verified

checked on a public match's replay: kills, deaths, assists, level, last hits and denies match the game's own end-of-match record for all ten players; every message in the packets sidecar re-serialises byte for byte; the table and statistics by tests on synthetic data

## Source

[heat3d_watch/adapters/replays.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/replays.py)

<!-- Generated from the adapter by tools/gen_game_pages.py; change the adapter and run it again rather than editing this page. -->
