# War Thunder (replays)

After a match of War Thunder, the watcher turns the replay the game saved into files you can look at on a map in the 3DHeat viewer.

*Technical details: adapter `warthunder-replays`, kind [`replay`](sources-and-rules); it runs all the time (it does not wait for a game to start) and looks for new data every 5 s.*

## What is recorded

- every aircraft's position and attitude about 4 times a second (as many as the replay holds)
- ground units' positions from the replay's ground sync (in 2026 replays; not in 2025 ones)
- who each unit was (player, vehicle id, team) where a kill or hit names it; kills, deaths and hits where they happened; chat; the map
- the replay author's kills, deaths, score and captures as statistics

## Where it comes from

replays War Thunder saves: &lt;War Thunder>/Replays/\*.wrpl (with replay saving on), converted by the external converter `heat3d-wt-replay` (exporters/ext/warthunder-replay)

## How to switch it on

turn on saving replays in War Thunder's options and install the converter: pip install -e &lt;3DHeat>/exporters/ext/warthunder-replay

Settings from environment variables:

- `HEAT3D_WT_REPLAY`: the converter's folder (a clone or unpacked release), when it is not installed or beside the watcher

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

#### War Thunder

War Thunder saves a replay of each battle to `<War Thunder>/Replays/*.wrpl`
when replay saving is on in its options. The watcher does not read them
itself: an external converter does (3DHeat War Thunder replay converter,
`exporters/ext/warthunder-replay`, command `heat3d-wt-replay`), a project of
its own. When the command is on PATH, or
the package is installed or beside the watcher, each new replay is run through
it into the session folder as `<map>/<match>.parquet` and `<match>.match.json`;
when it is not, the watcher says once how to install it and leaves the folder
alone. What the converter reads, and what it does not, is in its README. The
replay's author's line of the results - kills, ground kills, deaths, assists,
score, captures - becomes the session's statistics.

The same module also serves: [Counter-Strike 2 (replays)](game-cs2-demos), [Dota 2 (replays)](game-dota-replays), [Squad (replays)](game-squad-demos), [World of Tanks (replays)](game-wot-replays), [World of Warships (replays)](game-wows-replays).

## Positions and axes

| | |
|---|---|
| Positions recorded | yes |
| Up axis | `y` |
| Units | metres (x east, y up, z north) |
| Mirrored for the viewer | `z` |
| Unit scale (`scale`: the viewer multiplies positions by it) | 1 |

These go into each session's `meta.json` (`axes`) and, when the session has positions, into `heat.parquet`'s footer, so the 3DHeat viewer turns and scales the rows by itself - see [The data](the-data).

## Multiplayer

- Marked as played online (`multiplayer`): **yes**. `games --markdown` shows this as "allowed (reads only what the game publishes)".
- Kind `replay`: it reads only what the game or platform hands out (replays and demos the game saves), so it records in online play as well as offline; the flag decides only whether memory may ever be read.
- Memory: **never** read by this adapter. Only `memory` adapters read memory, and never for a game marked as played online - see [Sources and rules](sources-and-rules).

## Statistics recorded

Statistic keys this adapter's code sets by name (each session's `stats` in `meta.json` and the `stats` table of `watcher.sqlite`):

`map`

A key in braces is completed at run time (`score.{team}` is one key per team). Keys the code takes from a table of the game's fields or from the game's own stat names are not in this list; "What is recorded" above names them.

## Completeness

The converter this adapter runs follows 3DHeat's [converter rule](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md): what the replay holds is read or kept, never dropped - read into the table and the match document, everything else kept whole in sidecars beside them, counted in the match document's `selfCheck.completeness`. The converter's own documentation lists what it reads, keeps raw and cannot read.

## Verified

the converter is checked on public replays from several game versions (kills and names agree with the results) and by tests on built replays; this hook by tests with a stand-in command

## Source

[heat3d_watch/adapters/replays.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/replays.py)

<!-- Generated from the adapter by tools/gen_game_pages.py; change the adapter and run it again rather than editing this page. -->
