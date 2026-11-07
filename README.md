# 3DHeat Watcher

A background tool that records what games publish about your play - where you
went, what happened where, and the numbers behind it - into files on your own
machine, for your own statistics and for the 3DHeat viewer's heatmaps.

It runs quietly, notices which game you started, and reads that game's own
outputs: a telemetry port, a game-state integration, the journal or log the
game writes, the replay it saves after a match, the statistics Steam keeps, the
highlights your graphics driver records. Nothing is sent anywhere.

```bash
pip install -r requirements.txt
python -m heat3d_watch games          # what each game gives, and from where
python -m heat3d_watch setup all      # what would have to be switched on (add --apply to do it)
python -m heat3d_watch run            # watch; leave it running
python -m heat3d_watch stats          # totals per game
python -m heat3d_watch stats --csv out   # sessions, events and stats as CSV files
python -m heat3d_watch replays cs2-demos # convert the demos already on disk (new ones are converted by `run`)
python -m heat3d_watch replays warthunder-replays [folder]  # War Thunder replays, through the external converter (see below)
python -m heat3d_watch replays wot-replays [folder]   # World of Tanks replays, through the external converter (see below)
python -m heat3d_watch replays wows-replays [folder]  # World of Warships replays, likewise
python -m heat3d_watch replays dota-replays [folder]  # Dota 2 replays (needs `pip install gem-dota`)
python -m heat3d_watch dota-replay <match id> --convert  # fetch a public Dota 2 match's replay from Valve and convert it
```

Everything goes to `%LOCALAPPDATA%\3DHeat\Watcher` (set `HEAT3D_WATCH_HOME`, or
`python -m heat3d_watch config --set data=D:\somewhere`):

- `sessions/<game>/<date>_<source>/` - one folder per sitting:
  - `events.jsonl` - every event the moment it happens: time, event, position,
    player, team, match, and whatever else the game said
  - `heat.parquet` - the rows with a position, as a table the 3DHeat viewer
    opens directly (heatmaps, and the line mode that draws each player's routes
    between spawn and death)
  - `meta.json` - the game, the source, the axes and units, the counts and the
    statistics of the sitting
- `watcher.sqlite` - the statistics of every session, in three plain tables
  (`sessions`, `events`, `stats`) any SQL tool or spreadsheet reads
- `watcher.log` - what the watcher did

## What it may and may not do

- **Only what games publish.** Telemetry ports and shared memory the game
  creates for dashboards and motion rigs, game-state integrations and local APIs
  the game serves, files the game writes, replays the game saves, what Steam and
  the graphics driver keep. Nothing is injected into a game, nothing is hooked,
  nothing in a game is changed.
- **Multiplayer games: never their memory.** Reading a game's memory is allowed
  only for single-player games, only for builds a profile was checked on, only
  with no anti-cheat installed with the game or running on the machine, and only
  while the game has no connection out. It is off by default
  (`config --set memory=true`), it can only read, and no profiles ship with the
  tools. See [`docs/watcher.md`](docs/watcher.md#reading-memory).
- **Nothing protected is broken open.** Where a replay protects its game stream
  against cheating (League of Legends, VALORANT), only what it carries in the
  open is read - the end-of-game score, the event timeline. Replays encrypted
  with a key are not read by the watcher: Fortnite's are declined, and World
  of Tanks' and World of Warships' are left to separate converters a player
  installs by choice (below).
- **Switching a source on is your decision.** `setup` says which file it would
  change and how; only `setup --apply` changes it, and the original is kept as
  `<file>.heat3d-backup`.

**War Thunder replays** (`.wrpl`) are read by a separate converter, not by the
watcher: `exporters/ext/warthunder-replay` in 3DHeat, which installs the
`heat3d-wt-replay` command (`pip install -e <3DHeat>/exporters/ext/warthunder-replay`).
The format is undocumented and Gaijin's EULA forbids reverse engineering the
game, so it is kept apart: without it the watcher runs as before and says once
that it is missing. With it, each new replay in `<War Thunder>/Replays` becomes
a session with every aircraft's track, the kills and hits where they happened,
and who was who where the replay says so. What it reads and does not read is in
its own README.

**World of Tanks and World of Warships replays** (`.wotreplay`, `.wowsreplay`)
are read the same way, by a converter of each outside the watcher:
`exporters/ext/wot-replay` (`heat3d-wot-replay`) and `exporters/ext/wows-replay`
(`heat3d-wows-replay`), each installed with `pip install -e` on its folder.
Wargaming's licence forbids reverse engineering and "unauthorized software ...
that interacts with a Product", and the replays are enciphered, so these too
are kept apart. With them, each new replay in the game's `replays` folder
becomes a session with every tank's or ship's position while the recording
player's client knew of it - its own team throughout, enemies while spotted -
and the kills where they happened. Their READMEs say what they read, on which
game versions, and what they do not.

**Dota 2 replays** (`.dem`) are read inside the watcher, through gem
(github.com/whanyu1212/gem-dota, MIT, `pip install gem-dota`): Valve's replays
are plain Source 2 demos, kept public for every match for a few weeks, and read
by OpenDota and others for a decade. Each replay in `<Dota>/game/dota/replays`
becomes a session with every hero's track 7.5 times a second (position, height,
health, level), kills and deaths where they happened, towers, barracks, Roshan
and Tormentors where they fell, and every ward where it was planted, as
`dota/<match>.parquet` and `<match>.match.json`. `dota-replay <match id>`
downloads a public match's replay by its id (the cluster and salt come from
OpenDota; Valve answers 404 once a replay has expired). A half-hour match takes
about a minute and 400 MB to convert, in a process of its own. Not read: creeps,
couriers and illusions; what the fog of war hid from whom; items and abilities
over time.

The watcher updates itself while no game is running and starts again - never
in the middle of a game; `config --set auto_update=false` turns that off.

Which game is recorded how, and from where: [`docs/watcher.md`](docs/watcher.md)
and the wiki.

---

## Part of 3DHeat

3DHeat Watcher is one of the free tools around the 3DHeat telemetry viewer. Each is its
own project, with its own releases and licence:

| Tool | What it does |
|---|---|
| [3DHeat GameFiles](https://github.com/Holdi601/3DHeat-GameFiles) | courses and levels out of the archives games ship, as glTF |
| [3DHeat GameCapture](https://github.com/Holdi601/3DHeat-GameCapture) | lap telemetry from racing games' published interfaces; levels reconstructed from gameplay video |
| [3DHeat Unreal Exporter](https://github.com/Holdi601/3DHeat-UnrealExporter) | an Unreal Editor plugin that exports a level as glTF |
| [3DHeat CS2](https://github.com/Holdi601/3DHeat-CS2) | Counter-Strike 2 demos into heatmap tables and match summaries; maps into geometry |
| [3DHeat Watcher](https://github.com/Holdi601/3DHeat-Watcher) | records your play in the background from what games publish, for your own statistics |

## Updates

3DHeat Watcher checks this repository's releases when it starts (at most every few
hours, never holding it up for more than a few seconds), says when a newer
version is out, and offers to update: a clone with `git pull` when it has no
local changes, a downloaded copy by replacing its files from the release archive,
after checking the archive is the version it claims. Your own files - recordings,
settings, exports - are never touched. To update on request: `python -m heat3d_watch update`.
`HEAT3D_NO_UPDATE=1` switches the check off.

## Licence

MIT - see [`LICENSE`](LICENSE), and [`LICENSES.md`](LICENSES.md) for the
third-party packages it uses and what the games it reads oblige.

Documentation: the [wiki](https://github.com/Holdi601/3DHeat-Watcher/wiki).
