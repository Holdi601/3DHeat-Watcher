---
title: "League of Legends (gsi)"
parent: Games
nav_order: 29
---

# League of Legends (gsi)

Adapter `lol-live` - kind [`gsi`](sources-and-rules.md) - runs while `League of Legends.exe` is running - looks for new data every 0.5 s.

## What is recorded

- no positions: the API has none
- kill feed: kills, deaths and assists of the player, other champion kills with killer, victim, assisters
- dragons, heralds, barons, turrets, inhibitors, multikills, aces, first blood, game start and end
- own kills, deaths, assists, creep score, ward score, level, gold, champion, game time, result
- objectives taken by the player's team

## Where it comes from

Live Client Data API of the game client, <https://127.0.0.1:2999/liveclientdata/> (allgamedata, eventdata), during a match

## How to switch it on

Nothing needs switching on: the watcher reads the source as the game or platform provides it.

## How it works

League of Legends: the Live Client Data API the game client serves during a match.

While a match runs (also in practice tool and spectator mode), `League of
Legends.exe` answers on <https://127.0.0.1:2999> with what the player can see in
the game's own interface:

```text
/liveclientdata/allgamedata          activePlayer (riotId, level, currentGold, championStats),
                                     allPlayers (championName, team ORDER/CHAOS, level,
                                     scores: kills, deaths, assists, creepScore, wardScore),
                                     events, gameData (gameMode, gameTime s, mapName)
/liveclientdata/eventdata?eventID=N  {"Events": [...]} from EventID N on: GameStart,
                                     MinionsSpawning, FirstBlood, FirstBrick, TurretKilled,
                                     InhibKilled, InhibRespawningSoon, InhibRespawned,
                                     DragonKill, HeraldKill, BaronKill, ChampionKill
                                     (KillerName, VictimName, Assisters), Multikill
                                     (KillStreak), Ace (Acer, AcingTeam), GameEnd (Result)
```

There are no positions: the API has none, so a League session is events and
statistics, without a heat table. The certificate is self-signed, by Riot's own
root (`riotgames.pem`, published at
<https://static.developer.riotgames.com/docs/lol/riotgames.pem>). Its terms of
use are not stated, so it is not shipped: put it at `<data>\riotgames.pem` and
the connection is verified with it; without it verification is off - and only
ever for 127.0.0.1, the one address this adapter talks to.

Riot's policy allows tools to show what the player could know from the game
itself, and nothing computed beyond it (no enemy timers): this records the kill
feed and the scoreboard the player sees, and the player's own numbers.

Source: <https://developer.riotgames.com/docs/lol#game-client-api>

## Positions and axes

| | |
|---|---|
| Positions recorded | no |
| Up axis | `z` |
| Units | none (no positions) |
| Mirrored for the viewer | none |
| Unit scale (`scale`: the viewer multiplies positions by it) | 1 |

These go into each session's `meta.json` (`axes`) and, when the session has positions, into `heat.parquet`'s footer, so the 3DHeat viewer turns and scales the rows by itself - see [The data](the-data.md).

## Multiplayer

- Marked as played online (`multiplayer`): **yes**. `games --markdown` shows this as "allowed (reads only what the game publishes)".
- Kind `gsi`: it reads only what the game or platform hands out (a game-state integration or local API the game serves), so it records in online play as well as offline; the flag decides only whether memory may ever be read.
- Memory: **never** read by this adapter. Only `memory` adapters read memory, and never for a game marked as played online - see [Sources and rules](sources-and-rules.md).

## Statistics recorded

Statistic keys this adapter's code sets by name (each session's `stats` in `meta.json` and the `stats` table of `watcher.sqlite`):

`bad_packets`, `champion`, `game_time`, `gold`, `level`, `result`

A key in braces is completed at run time (`score.{team}` is one key per team). Keys the code takes from a table of the game's fields or from the game's own stat names are not in this list; "What is recorded" above names them.

## Verified

tested against a fake local server serving answers in the documented format; untested against the game (not installed here)

## Source

[heat3d_watch/adapters/lol.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/lol.py)

*Generated from the adapter by `tools/gen_game_pages.py`; change the adapter and run it again rather than editing this page.*
