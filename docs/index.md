---
title: Home
nav_order: 1
---

# 3DHeat Watcher

3DHeat Watcher is a background program that records what games publish about your play - where you
went, what happened where, and the numbers behind it - into files on your own machine. The files are
for your own statistics and for the heatmaps and route lines of the 3DHeat viewer.

It runs quietly, notices which game you started, and reads that game's own outputs: a telemetry port
or shared memory the game publishes for dashboards, a game-state integration, the journal or log the
game writes, the replay it saves after a match, the statistics Steam keeps, the clips the NVIDIA App
saves. Recordings stay on your machine. The program contacts only two outside services, and only in
these cases: GitHub, to look for a newer release (see [Updates](updates.md)), and Riot's Match-V5 API,
and only if you enter your own Riot API key (see [League of Legends replays](game-lol-replays.md)).

## What it records

- **Positions**: the car, aircraft, hero or player, several times a second where the game publishes
  them, with speed, heading and whatever else the game sends alongside.
- **Events**: spawns, deaths, kills, laps, stages, rounds, goals, jobs, takeoffs and landings, zone
  changes, achievements, highlights. Each event is stored with its time, and with its place when the
  game gives one.
- **Statistics per session**: kills, deaths, laps, best lap, distance, top speed, playtime, and the
  game's own stats where it keeps them.

What each game gives, and from where, is on its own page under [Games](games.md). One source cannot
record everything: multiplayer games are recorded only through what they publish, and the watcher
never reads their memory (see [Sources and rules](sources-and-rules.md)).

## Install

The watcher is a Python program for Windows. Many of its sources exist only on Windows: shared
memory, the registry, Windows notifications.

```bash
git clone https://github.com/Holdi601/3DHeat-Watcher.git
cd 3DHeat-Watcher
pip install -r requirements.txt
```

A downloaded release archive works the same way: unpack it, then run `pip install -r requirements.txt`
inside the folder. The details, and the extras some games need, are in
[Installing and running](installing-and-running.md).

## Quick start

```bash
python -m heat3d_watch games            # what each game gives, and from where
python -m heat3d_watch setup all        # what would have to be switched on (nothing is changed)
python -m heat3d_watch setup f1-25 --apply   # switch one game's output on (the original file is backed up)
python -m heat3d_watch run              # watch; leave it running while you play
python -m heat3d_watch stats            # totals per game
python -m heat3d_watch stats --csv out  # sessions, events and stats as CSV files
```

Everything is written to `%LOCALAPPDATA%\3DHeat\Watcher`. To use another folder, set the
`HEAT3D_WATCH_HOME` environment variable or run `python -m heat3d_watch config --set data=D:\somewhere`.

- `sessions\<game>\<date>_<adapter>\` - one folder per sitting, holding `events.jsonl` (every event
  as it happens), `heat.parquet` (the rows with a position, ready for the 3DHeat viewer) and
  `meta.json` (game, source, axes, counts, statistics)
- `watcher.sqlite` - the statistics of every session, in three plain tables
- `watcher.log` - what the watcher did

## The documentation

| Page | What it covers |
|---|---|
| [Installing and running](installing-and-running.md) | requirements, running in the background, starting with Windows, the lock file, the log, every setting and environment variable |
| [Games](games.md) | one page per game: what is recorded, where from, how to switch it on, how it works, axes, statistics, what was verified |
| [The data](the-data.md) | session folders, `events.jsonl`, `heat.parquet` and its footer, `meta.json`, `watcher.sqlite`, recovery after a crash, CSV export, opening a session in the 3DHeat viewer |
| [Commands](commands.md) | every command and option of `python -m heat3d_watch` |
| [Sources and rules](sources-and-rules.md) | the six kinds of source, the multiplayer rules, which games are left out and why |
| [NVIDIA Highlights](nvidia-highlights.md) | what NVIDIA Highlights can and cannot deliver, and how a highlight gets a position |
| [Reading memory](memory-reading.md) | single-player memory profiles: the format, the checks, how to write and verify one |
| [Updates](updates.md) | how the watcher looks for new releases and updates itself |
| [Development](development.md) | writing an adapter: the API, tests, an honest `verified`, regenerating the game pages |
| [All games in one table](watcher.md) | every game in one table, as `games --markdown` prints it, plus the games researched but not yet built |

## Part of 3DHeat

3DHeat Watcher is one of several free tools around the 3DHeat telemetry viewer. Each tool is a
separate project with its own releases and licence: [3DHeat GameFiles](https://github.com/Holdi601/3DHeat-GameFiles),
[3DHeat GameCapture](https://github.com/Holdi601/3DHeat-GameCapture),
[3DHeat Unreal Exporter](https://github.com/Holdi601/3DHeat-UnrealExporter),
[3DHeat CS2](https://github.com/Holdi601/3DHeat-CS2) (the watcher uses it to convert CS2 demos) and
3DHeat Watcher.

Licence: MIT ([LICENSE](https://github.com/Holdi601/3DHeat-Watcher/blob/main/LICENSE)). The licences
of the third-party packages it uses, and what the games it reads require, are listed in
[LICENSES.md](https://github.com/Holdi601/3DHeat-Watcher/blob/main/LICENSES.md).
