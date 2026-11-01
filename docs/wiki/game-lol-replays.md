
# League of Legends (replay)

Adapter `lol-replays` - kind [`replay`](sources-and-rules) - runs always on (it does not wait for a game to start) - looks for new data every 5 s.

## What is recorded

- each player's champion, role, team, kills, deaths, assists, gold, damage to champions and result
- your own line as statistics, and your rows named as yours (meta.json `player`), with your Riot ID in the settings
- with your own Riot API key: every player's position each minute and every kill where it happened, at the wall-clock time the timeline gives
- not: the moment-to-moment game, which is obfuscated against cheating and not decoded

## Where it comes from

replays the League client saves: %USERPROFILE%/Documents/League of Legends/Replays/\*.rofl (the plain end-of-game metadata only); with your own Riot API key, the match's official timeline from Riot's Match-V5 API

## How to switch it on

save a replay in the League client (match history > download); for positions set riot_api_key and riot_platform with `config --set`

## How it works

League of Legends and Valorant replays: what of them can be read as it is.

Both games save replays to the player's disk, and both protect what is inside:
the moment-to-moment game data is obfuscated, and differently with every patch,
to keep it from being used to cheat. Getting through that means taking the
game's own code apart, which Riot's terms forbid (Terms of Service 3.1 and 7.1)
- so it is not done here. What each file carries in the open is read, and
nothing else.

#### League of Legends (.rofl)

`%USERPROFILE%\Documents\League of Legends\Replays\*.rofl`. Both container
versions carry the end-of-game box score as plain JSON (`statsJson`): for each
of the ten players the champion, kills, deaths, assists, gold, damage to
champions, items, team, role, win, and their Riot ID. ROFL1 (patch 14.9 and
before) has it after a fixed header (`RIOT\0\0`, a 256-byte signature, then
the lengths); ROFL2 (14.11 on, `RIOT\2\0`) at the end of the file, its length in
the last four bytes (stated by a Riot engineer, ReplayBook issue 299). Layouts
from roflxd.cs (MIT).

Positions do not come from the file. With a Riot developer key of the player's
own (`riot_api_key` in the settings; a personal key is meant for exactly this,
"showing (self) player stats"), the match's official timeline is fetched from
Riot's Match-V5 API: every player's position once a minute and every kill where
it happened, on Summoner's Rift's map coordinates. Without a key nothing is
fetched and nothing is sent.

#### Valorant (.vrf)

`%LOCALAPPDATA%\VALORANT\Saved\Demos\*.vrf`, an Unreal Engine local replay
(layout from vrfkit, Apache-2.0, and ValorantReplayParser, MIT). In the open:
the map, the match id and the agents picked (in the header), and the server's
own event timeline - kills (killer and victim as network ids, not names),
rounds starting, spikes planted, defused and exploding, ultimates used, sides
switching - each with its time. Positions, names, scores and everything else
are in the obfuscated stream and are not read.

The same module also serves: [VALORANT (replay)](game-valorant-replays).

## Positions and axes

| | |
|---|---|
| Positions recorded | yes |
| Up axis | `y` |
| Units | Summoner's Rift map units (about 15000 across) |
| Mirrored for the viewer | none |
| Unit scale (`scale`: the viewer multiplies positions by it) | 1 |

These go into each session's `meta.json` (`axes`) and, when the session has positions, into `heat.parquet`'s footer, so the 3DHeat viewer turns and scales the rows by itself - see [The data](the-data).

## Multiplayer

- Marked as played online (`multiplayer`): **yes**. `games --markdown` shows this as "allowed (reads only what the game publishes)".
- Kind `replay`: it reads only what the game or platform hands out (replays and demos the game saves), so it records in online play as well as offline; the flag decides only whether memory may ever be read.
- Memory: **never** read by this adapter. Only `memory` adapters read memory, and never for a game marked as played online - see [Sources and rules](sources-and-rules).

## Statistics recorded

Statistic keys this adapter's code sets by name (each session's `stats` in `meta.json` and the `stats` table of `watcher.sqlite`):

`champion`, `game_seconds`, `won`

A key in braces is completed at run time (`score.{team}` is one key per team). Keys the code takes from a table of the game's fields or from the game's own stat names are not in this list; "What is recorded" above names them.

## Verified

the metadata reader tested on files built to the layouts in roflxd.cs (MIT); the timeline on Match-V5's documented JSON; no real replay was available to check against

## Source

[heat3d_watch/adapters/riot_replays.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/riot_replays.py)

*Generated from the adapter by `tools/gen_game_pages.py`; change the adapter and run it again rather than editing this page.*
