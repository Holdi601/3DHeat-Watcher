---
title: "Dota 2 (gsi)"
parent: Games
nav_order: 13
---

# Dota 2 (gsi)

Adapter `dota2-gsi` - kind [`gsi`](sources-and-rules.md) - runs while `dota2.exe` is running - looks for new data every 0.05 s.

## What is recorded

- own hero position (world X/Y, Dota units; no height) while alive
- spawn, deaths (with respawn time) and respawns of the own hero
- kills, from the kill count growing
- buildings destroyed, Roshan, game events (roshan_killed, aegis_picked_up, ...), game states, result
- kills, deaths, assists, last hits, denies, gold, GPM, XPM, level, hero

## Where it comes from

Game State Integration: HTTP POSTs to 127.0.0.1:3312 configured by &lt;Dota>\game\dota\cfg\gamestate_integration\gamestate_integration_heat3d.cfg

## How to switch it on

`python -m heat3d_watch setup dota2-gsi --apply`, then start Dota 2 (it reads the file at start)

`python -m heat3d_watch setup dota2-gsi` lists the files it would change; `python -m heat3d_watch setup dota2-gsi --apply` changes them, keeping the original as `<file>.heat3d-backup` (see [Commands](commands.md#setup)).

## How it works

Valve Game State Integration: Counter-Strike 2 and Dota 2 tell a local web server what happens.

Both games read every `gamestate_integration_*.cfg` in their cfg folder when they
start, and from then on POST a JSON document to each file's `uri` whenever the
state changes (at most every `throttle` seconds, and every `heartbeat` seconds
when nothing does). The watcher is that web server: it listens on 127.0.0.1 only,
answers every POST with 200 at once and does the work in its own poll thread.

```text
Counter-Strike 2  <CS2>\game\csgo\cfg\gamestate_integration_heat3d.cfg      port 3311
Dota 2            <Dota>\game\dota\cfg\gamestate_integration\gamestate_integration_heat3d.cfg   port 3312
```

What a player is sent - and so what can be recorded - is what the game decides
a player may see:

- CS2: `provider` (the own steamid), `map` (name, mode, phase warmup/live/
  intermission/gameover, round, team_ct/team_t score), `round` (phase
  freezetime/live/over, bomb planted/exploded/defused, win_team), `player` (the
  player being *watched*: oneself while alive, a teammate after death) with
  `state` (health, armor, money, round_kills, round_killhs, round_totaldmg),
  `match_stats` (kills, assists, deaths, mvps, score), `position` and `forward`
  as "x, y, z" strings in world units (inches, Z up), `weapons`; `bomb` only for
  spectators. Other players' positions (`allplayers_*`) are sent only to
  spectators and GOTV, so they are not asked for.
- Dota 2: `map` (matchid, game_state, game_time, clock_time, win_team), `player`
  (kills, deaths, assists, last_hits, denies, gold, gpm, xpm, team_name), `hero`
  (xpos/ypos in world units, level, alive, respawn_seconds), `buildings`
  (health per tower/barracks/ancient), `roshan`, `events` (roshan_killed,
  aegis_picked_up, ...). There is no height: z is 0. Also asked for, and kept
  whole: `abilities`, `items`, `draft`, `wearables`, `minimap`, `couriers`,
  `neutralitems`, `league` (the game sends what the player's own client has;
  which of them hold anything while playing rather than spectating is untested).

Every document is kept whole as well (3DHeat's converter rule,
docs/converters.md in the viewer's repository): `heat.raw.parquet`, `type`
"gsi", `text` the JSON as posted - only the cfg file's token blanked, it is the
watcher's own secret, not game data. Documents posted while no match is open
(menus, loading, between matches) wait in a `Backlog` and go into the next
match's session, before its start; what is left when the game closes gets a
session of its own that holds only them. Unreadable posts and posts with a
wrong token are kept too ("gsi-unreadable", "gsi-bad-auth").

Sources: <https://developer.valvesoftware.com/wiki/Counter-Strike:_Global_Offensive_Game_State_Integration>
(the format CS2 kept), <https://github.com/antonpup/CounterStrike2GSI> and
<https://github.com/antonpup/Dota2GSI> (field lists; MIT, read for facts only).

The same module also serves: [Counter-Strike 2 (gsi)](game-cs2-gsi.md).

## Positions and axes

| | |
|---|---|
| Positions recorded | yes |
| Up axis | `z` |
| Units | Dota world units (z always 0) |
| Mirrored for the viewer | `y` |
| Unit scale (`scale`: the viewer multiplies positions by it) | 1 |

These go into each session's `meta.json` (`axes`) and, when the session has positions, into `heat.parquet`'s footer, so the 3DHeat viewer turns and scales the rows by itself - see [The data](the-data.md).

## Multiplayer

- Marked as played online (`multiplayer`): **yes**. `games --markdown` shows this as "allowed (reads only what the game publishes)".
- Kind `gsi`: it reads only what the game or platform hands out (a game-state integration or local API the game serves), so it records in online play as well as offline; the flag decides only whether memory may ever be read.
- Memory: **never** read by this adapter. Only `memory` adapters read memory, and never for a game marked as played online - see [Sources and rules](sources-and-rules.md).

## Statistics recorded

Statistic keys this adapter's code sets by name (each session's `stats` in `meta.json` and the `stats` table of `watcher.sqlite`):

`bad_auth`, `bad_packets`, `dropped_packets`, `hero`, `level`, `result`, `roshan_kills_seen`

A key in braces is completed at run time (`score.{team}` is one key per team). Keys the code takes from a table of the game's fields or from the game's own stat names are not in this list; "What is recorded" above names them.

## Completeness

The watcher follows 3DHeat's [converter rule](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md): what the source holds is read or kept, never dropped. Besides the rows, every packet, page, line or reply the adapter receives is kept whole in the session's `heat.raw.parquet` (columns `time`, `ms`, `type`, `used`, `payload`, `text`, then any field kept by name; `used` marks what also became rows), and `meta.json`'s `selfCheck.completeness` counts each `type` - `lost` is 0.

**Read**

- the own hero's position (x/y), alive, level, health, max health, mana, max mana; spawn, deaths with the respawn time, respawns
- kills (the kill count growing); kills, deaths, assists, last hits, denies, gold, GPM, XPM, net worth, level and hero as statistics
- buildings destroyed, Roshan down and back, every entry of `events` once, game states, the winner

**Kept raw**

- `gsi`: every document the game posts, whole, as posted (`text`), `used` true when it was read in a match - all fifteen components the cfg file asks for: provider, map (day/night, paused, ward cooldowns, scores), player (reliable and unreliable gold, streaks, kill list, commands issued, ...), hero (buffs, talents, Aghanim's, attributes), abilities, items, buildings, roshan, events, draft, wearables, minimap, couriers, neutralitems, league, and the game's `previously`/`added` diff
- documents from menus, loading and between matches: kept the same way, at their own time before the next match's start; after the last match, in a session of their own (`raw_only` in meta.json)
- `gsi-unreadable`: a post that is not a JSON object, its bytes as `payload` and `length`
- `gsi-bad-auth`: a post with another token than the cfg file's

**Not available**

- height: the game sends x and y only
- the other heroes while playing: the game sends the own hero, and every player's only to spectators (kept raw then, not drawn); several components (draft, minimap, couriers) carry only what the player's own client has - which, while playing, is untested (Dota 2 is not installed here)
- states between posts: at most one every 0.1 s (`throttle`), every 10 s when nothing changes
- the cfg file's token, blanked in each kept document: the watcher's own secret, not game data
- posts beyond 10,000 waiting (the watcher stalled) are counted as `dropped_packets`, not kept; a post over 4 MB is kept as `gsi-unreadable` with its length but without its bytes

**Size**: with every component a player's document is about 5-15 KB, posted up to 10 times a second (the clock changes every post): about 100-500 MB per hour in `raw.bin` while the match runs, roughly a tenth in the zstd `heat.raw.parquet`; a spectator's, with every player and the minimap, several times that (estimated from the published format, not measured on the game)

## Verified

tested on documents in the published GSI format posted to the running adapter; untested against the running game (not installed here)

## Source

[heat3d_watch/adapters/gsi.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/gsi.py)

*Generated from the adapter by `tools/gen_game_pages.py`; change the adapter and run it again rather than editing this page.*
