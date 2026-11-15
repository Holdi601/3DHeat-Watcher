# Command and column reference

Generated from the code by `tools/gen_docs_reference.py`. [Commands](commands) explains
each command step by step; this page lists everything exactly as the program has it.

## `python -m heat3d_watch`

```text
usage: heat3d_watch [-h] [--version]
                    {run,games,setup,status,sessions,stats,table,replays,dota-replay,dota-map,update,config} ...

`python -m heat3d_watch <command>`

    run        watch in the background: record every game that is running
    games      what each game gives and from where (--markdown for the docs)
    setup      switch a game's own output on (--apply to change files)
    status     which games are running now and what would be recorded
    sessions   the recordings so far
    stats      totals per game; --game for one, --csv DIR to write the tables out
    table      rebuild a session's heat.parquet from its events.jsonl
    replays    convert the replays already on disk for one adapter (or a folder of them)
    dota-replay  download a public Dota 2 match's replay by its id (--convert to convert it now)
    dota-map   the Dota 2 map from your install as a level (.glb) under the replay tables
    update     update the tools to the newest release (--check to only ask)
    config     show the settings, or change them (--set key=value ...)

positional arguments:
  {run,games,setup,status,sessions,stats,table,replays,dota-replay,dota-map,update,config}
    run                 watch in the background
    games               what each game gives and from where
    setup               switch a game's own output on
    status              which games are running now
    sessions            the recordings so far
    stats               totals per game
    table               rebuild a session's heat.parquet
    replays             convert the replays already on disk
    dota-replay         download a public Dota 2 match's replay
    dota-map            the Dota 2 map from your install as a level (.glb)
    update              update to the newest release
    config              show or change the settings

options:
  -h, --help            show this help message and exit
  --version             show program's version number and exit
```

## `run`

```text
usage: heat3d_watch run [-h] [--once] [-v]

options:
  -h, --help     show this help message and exit
  --once         one look at the running games, then stop
  -v, --verbose
```

## `games`

```text
usage: heat3d_watch games [-h] [--markdown]

options:
  -h, --help  show this help message and exit
  --markdown
```

## `setup`

```text
usage: heat3d_watch setup [-h] [--apply] adapter

positional arguments:
  adapter     an adapter id from `games`, or all

options:
  -h, --help  show this help message and exit
  --apply     make the changes (backups are kept)
```

## `status`

```text
usage: heat3d_watch status [-h]

options:
  -h, --help  show this help message and exit
```

## `sessions`

```text
usage: heat3d_watch sessions [-h] [--game GAME] [--limit LIMIT]

options:
  -h, --help     show this help message and exit
  --game GAME
  --limit LIMIT
```

## `stats`

```text
usage: heat3d_watch stats [-h] [--game GAME] [--csv DIR]

options:
  -h, --help   show this help message and exit
  --game GAME
  --csv DIR    write sessions, events and stats as CSV files
```

## `table`

```text
usage: heat3d_watch table [-h] folder

positional arguments:
  folder

options:
  -h, --help  show this help message and exit
```

## `replays`

```text
usage: heat3d_watch replays [-h] [-v] adapter [folder]

positional arguments:
  adapter        a replay adapter's id from `games` (cs2-demos, lol-replays, ...)
  folder         convert the replays in this folder instead of the game's own

options:
  -h, --help     show this help message and exit
  -v, --verbose
```

## `dota-replay`

```text
usage: heat3d_watch dota-replay [-h] [-o OUT] [--convert] [-v] match [match ...]

positional arguments:
  match          match ids (from the client, OpenDota or Dotabuff)

options:
  -h, --help     show this help message and exit
  -o, --out OUT  the folder to save to (default: Dota's own replays folder)
  --convert      convert the folder's replays now
  -v, --verbose
```

## `dota-map`

```text
usage: heat3d_watch dota-map [-h] -o OUT [--game GAME] [--source2viewer SOURCE2VIEWER]
                             [--detail DETAIL]
                             [map]

positional arguments:
  map                   the map's name (default: dota) or the path to its .vpk

options:
  -h, --help            show this help message and exit
  -o, --out OUT         the .glb to write
  --game GAME           the Dota 2 folder (default: found in your Steam libraries)
  --source2viewer SOURCE2VIEWER
                        Source2Viewer-CLI's path (default: HEAT3D_SOURCE2VIEWER, then
                        PATH)
  --detail DETAIL       buildings' vertex clustering cell in game units (default 8; 0
                        keeps every triangle)
```

## `update`

```text
usage: heat3d_watch update [-h] [--check]

options:
  -h, --help  show this help message and exit
  --check
```

## `config`

```text
usage: heat3d_watch config [-h] [--set [KEY=VALUE ...]]

options:
  -h, --help            show this help message and exit
  --set [KEY=VALUE ...]
                        read by the setting's type: true/false, a number, a list (a,b
                        or JSON), a dictionary as JSON; KEY.ID=VALUE sets one entry of
                        a dictionary
```

## Columns every table has

`heat.parquet` starts with these columns, in this order; the game's own fields follow under their own names ([The data](the-data)):

`time`, `ms`, `event`, `x`, `y`, `z`, `player`, `team`, `session`

`heat.raw.parquet`, the raw sidecar of a live feed, starts with:

`time`, `ms`, `type`, `used`, `payload`, `text`
