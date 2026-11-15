# osu! (replays)

After a match of osu!, the watcher turns the replay the game saved into files you can look at on a map in the 3DHeat viewer.

*Technical details: adapter `osu-replays`, kind [`replay`](sources-and-rules); it runs all the time (it does not wait for a game to start) and looks for new data every 5 s.*

## What is recorded

- the cursor's path over the playfield (x 0..512, y 0..384) and the keys held, every frame
- score, combo, 300s/100s/50s/gekis/katus/misses, accuracy, mods, full combo
- the life bar over the play, the beatmap's and the replay's hashes, the random seed, the online score id

## Where it comes from

replays osu! (stable) saves: %LOCALAPPDATA%/osu!/Data/r/\*.osr (every play) and osu!/Replays/\*.osr (exported), read by the external reader `heat3d-osu-replays` (exporters/ext/osu-replays)

## How to switch it on

play in osu! (stable): it saves every play; install the reader: github.com/Holdi601/3DHeat-Ext-Osu (`heat3d-osu-replays`)

Settings from environment variables:

- `HEAT3D_OSU_REPLAYS`: the reader's folder (a clone or unpacked release), when it is not installed or beside the watcher

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

#### osu!

osu! (stable) saves every play to `osu!/Data/r/*.osr` and exported ones to
`osu!/Replays/`. The watcher does not read them itself: an external reader
does (3DHeat osu!, github.com/Holdi601/3DHeat-Ext-Osu, `exporters/ext/osu-replays`,
command `heat3d-osu-replays`), to the format the osu! wiki publishes, found on
PATH, installed, or beside the watcher; missing, the watcher says once how to
install it. What it reads becomes the session: the cursor's path and keys
every frame, the score line, the life bar, the seed and the score id; the file
is kept whole beside, part by part, in the session's `heat.raw.parquet`.

The same module also serves: [Counter-Strike 2 (replays)](game-cs2-demos), [Dota 2 (replays)](game-dota-replays), [Squad (replays)](game-squad-demos), [War Thunder (replays)](game-warthunder-replays), [World of Tanks (replays)](game-wot-replays), [World of Warships (replays)](game-wows-replays).

## Positions and axes

| | |
|---|---|
| Positions recorded | yes |
| Up axis | `y` |
| Units | osu! pixels (playfield 512 x 384) |
| Mirrored for the viewer | `z` |
| Unit scale (`scale`: the viewer multiplies positions by it) | 1 |

These go into each session's `meta.json` (`axes`) and, when the session has positions, into `heat.parquet`'s footer, so the 3DHeat viewer turns and scales the rows by itself - see [The data](the-data).

## Multiplayer

- Marked as played online (`multiplayer`): **yes**. `games --markdown` shows this as "allowed (reads only what the game publishes)".
- Kind `replay`: it reads only what the game or platform hands out (replays and demos the game saves), so it records in online play as well as offline; the flag decides only whether memory may ever be read.
- Memory: **never** read by this adapter. Only `memory` adapters read memory, and never for a game marked as played online - see [Sources and rules](sources-and-rules).

## Statistics recorded

Statistic keys this adapter's code sets by name (each session's `stats` in `meta.json` and the `stats` table of `watcher.sqlite`):

`accuracy`, `full_combo`

A key in braces is completed at run time (`score.{team}` is one key per team). Keys the code takes from a table of the game's fields or from the game's own stat names are not in this list; "What is recorded" above names them.

## Completeness

The watcher follows 3DHeat's [converter rule](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md): what the source holds is read or kept, never dropped. Besides the rows, every packet, page, line or reply the adapter receives is kept whole in the session's `heat.raw.parquet` (columns `time`, `ms`, `type`, `used`, `payload`, `text`, then any field kept by name; `used` marks what also became rows), and `meta.json`'s `selfCheck.completeness` counts each `type` - `lost` is 0.

**Read**

- every frame: a row at its time (milliseconds summed), x and y on the playfield, `keys` the key bits (mouse 1 and 2, keys 1 and 2, smoke); in mania x holds the keys held instead of a place
- the header, every field: mode, version, the beatmap's MD5 (the file names the beatmap only by it), the player, the replay's MD5, 300s, 100s, 50s, gekis, katus, misses, score, max combo, full combo, mods (by name in meta.json `osu.modNames`), the play's time - as statistics and in meta.json `osu`
- the life bar graph: a `life` row per point (time, life 0..1)
- the frame `-12345`: the random seed (`osu.seed`); the online score id (`osu.scoreId`); with Target Practice, its accuracy (`osu.targetPracticeAccuracy`)

**Kept raw**

- the file whole, part by part, in heat.raw.parquet (`offset` where each starts, so the parts are the file): `header`, `replay_data` (the LZMA-compressed frames as stored), `score_id`, `mod_info`, and `trailing` for whatever follows the parts the format describes (osu!lazer's exports add data there) - kept, not read

**Not available**

- the beatmap itself (hit objects, timing): not in a replay; it is named only by its MD5
- osu!lazer's own replays: kept in its database, not as files

**Size**: the raw sidecar is about the replay's size (tens to hundreds of kilobytes)

## Verified

the reader is tested on replays built to the published .osr format; this hook by tests with the reader and a stand-in; osu!lazer keeps replays in its own store and is not read

## Source

[heat3d_watch/adapters/replays.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/replays.py)

<!-- Generated from the adapter by tools/gen_game_pages.py; change the adapter and run it again rather than editing this page. -->
