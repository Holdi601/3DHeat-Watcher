---
title: "Rocket League (gsi)"
parent: Games
nav_order: 39
---

# Rocket League (gsi)

Adapter `rocketleague-stats` - kind [`gsi`](sources-and-rules.md) - runs while `RocketLeague.exe` is running - looks for new data every 0.05 s.

## What is recorded

- ball hits with the ball's place (XYZ, Unreal units), who hit it and the speeds
- goals with the impact place, scorer, assister and speed; crossbar hits with the place
- stat feed (demolitions, saves, shots, epic saves, ...), kickoffs, replays, match start and end, winner
- own goals, assists, saves, shots, demos, touches, score and the team scores, from UpdateState
- every player's final line at match end
- your own rows as `me`: the player named in the settings (`config --set player_names.rocketleague-stats=<name>`), else the one the game's camera follows outside replays
- no car positions: the API has none

## Where it comes from

Stats API: TCP JSON stream from 127.0.0.1:49123 (Port in &lt;RL>\TAGame\Config\TAStatsAPI.ini or DefaultStatsAPI.ini)

## How to switch it on

`python -m heat3d_watch setup rocketleague-stats --apply` (sets PacketSendRate=30), then start Rocket League

`python -m heat3d_watch setup rocketleague-stats` lists the files it would change; `python -m heat3d_watch setup rocketleague-stats --apply` changes them, keeping the original as `<file>.heat3d-backup` (see [Commands](commands.md#setup)).

## How it works

Rocket League: the official Stats API, a local socket the game writes match data to.

Switched on in `<RL>\TAGame\Config\TAStatsAPI.ini` - or `DefaultStatsAPI.ini`
when that does not exist, which the game reads only then - under
`[TAGame.MatchStatsExporter_TA]`:

```text
PacketSendRate   UpdateState messages per second; 0 (the default) switches the API off, at most 120
Port             the TCP port the game listens on, default 49123 (WebPort 49124 is a WebSocket copy)
```

The game is the server: a client connects to 127.0.0.1:49123 and reads a stream
of JSON objects `{"Event": name, "Data": {...}}` (some builds send Data as a
JSON string), one after another without separators. Events are sent on the
tick they happen, independent of the rate:

```text
UpdateState   MatchGuid, Players[] (Name, PrimaryId, Shortcut, TeamNum 0 blue / 1 orange,
              Score, Goals, Shots, Assists, Saves, Touches, CarTouches, Demos; car state
              only for spectators), Game (Teams[], TimeSeconds, bOvertime, Ball {Speed,
              TeamNum}, bReplay, bHasWinner, Winner, Arena, bHasTarget, Target)
BallHit       Players[] (Name, Shortcut, TeamNum), Ball {PreHitSpeed, PostHitSpeed, Location {X,Y,Z}}
GoalScored    GoalSpeed, GoalTime, ImpactLocation {X,Y,Z}, Scorer, Assister, BallLastTouch
CrossbarHit   BallLocation {X,Y,Z}, BallSpeed, ImpactForce, BallLastTouch
StatfeedEvent EventName, Type, MainTarget, SecondaryTarget
MatchEnded    WinnerTeamNum
MatchCreated, MatchInitialized, CountdownBegin, RoundStarted, GoalReplayStart/WillEnd/End,
MatchPaused/Unpaused, PodiumStart, ReplayCreated, MatchDestroyed, ClockUpdatedSeconds
```

Locations are Unreal units (centimetres), Z up; the field is about 8200 x 10240
with the goals at Y = +-5120. Cars' positions are not part of the API: what has
a place is the ball where it was hit, scored or hit the crossbar.

Sources: <https://www.rocketleague.com/en/developer/stats-api> (the official page);
field casing and the TCP framing confirmed against the rlstatsapi client
(<https://docs.rs/crate/rlstatsapi>, MIT; read for facts only).

## Positions and axes

| | |
|---|---|
| Positions recorded | yes |
| Up axis | `z` |
| Units | Unreal units (centimetres) |
| Mirrored for the viewer | none |
| Unit scale (`scale`: the viewer multiplies positions by it) | 1 |

These go into each session's `meta.json` (`axes`) and, when the session has positions, into `heat.parquet`'s footer, so the 3DHeat viewer turns and scales the rows by itself - see [The data](the-data.md).

## Multiplayer

- Marked as played online (`multiplayer`): **yes**. `games --markdown` shows this as "allowed (reads only what the game publishes)".
- Kind `gsi`: it reads only what the game or platform hands out (a game-state integration or local API the game serves), so it records in online play as well as offline; the flag decides only whether memory may ever be read.
- Memory: **never** read by this adapter. Only `memory` adapters read memory, and never for a game marked as played online - see [Sources and rules](sources-and-rules.md).

## Statistics recorded

Statistic keys this adapter's code sets by name (each session's `stats` in `meta.json` and the `stats` table of `watcher.sqlite`):

`bad_packets`, `demolished`, `other_goals`, `overtime`, `result`, `team_goals`

A key in braces is completed at run time (`score.{team}` is one key per team). Keys the code takes from a table of the game's fields or from the game's own stat names are not in this list; "What is recorded" above names them.

## Verified

tested on messages in the documented format sent by a fake local server; untested against the game (not installed here)

## Source

[heat3d_watch/adapters/rocketleague.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/rocketleague.py)

*Generated from the adapter by `tools/gen_game_pages.py`; change the adapter and run it again rather than editing this page.*
