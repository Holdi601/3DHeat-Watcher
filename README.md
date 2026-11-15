# 3DHeat Watcher

**What is it?** You play a game. This program quietly writes down where you
went and what happened. Later you can look at it as a coloured map in the
3DHeat viewer.

**Why would I use it?** To keep your own record of every sitting - where you
drove, flew or fought, what happened where, your totals per game - without
any website and without changing the game.

**Example:** you drive a few laps in a racing game with the watcher running;
afterwards `sessions/<game>/<date>_<source>/heat.parquet` holds your line,
and the viewer draws it.

In more detail: a background tool that records what games publish about your play - where you
went, what happened where, and the numbers behind it - into files on your own
machine, for your own statistics and for the heatmaps of the
[3DHeat viewer](https://github.com/Holdi601/3DHeat) ([documentation](https://holdi601.github.io/3DHeat/)).

It runs quietly, notices which game you started, and reads that game's own
outputs: a telemetry port, a game-state integration, the journal or log the
game writes, the replay it saves after a match, the statistics Steam keeps, the
highlights your graphics driver records. Nothing is sent anywhere.

**Documentation: <https://holdi601.github.io/3DHeat-Watcher/>** - a page per game
(50 of them), per command and per output.

![the watcher: what games publish, into files on your machine](docs/assets/img/overview.svg)

## Install and quick start

New to the command line? Read [Before you start](https://holdi601.github.io/3DHeat-Watcher/before-you-start.html) first.

Windows and Python 3.10 or later. Download the zip from
[Releases](https://github.com/Holdi601/3DHeat-Watcher/releases) and unpack it (or,
if you have Git, `git clone https://github.com/Holdi601/3DHeat-Watcher.git`), open a
terminal in that folder (in File Explorer, type `powershell` in the address bar), then:

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
python -m heat3d_watch dota-replay <match id> --convert  # fetch a public Dota 2 match's replay from Valve and convert it (needs internet)
python -m heat3d_watch dota-map -o dota.glb      # the Dota 2 map from your install as a 3D level (needs the 3DHeat-Ext-Dota tool)
```

`<...>` are placeholders. After `games` you should see a table of games, one line
each; `run` keeps going until you press Ctrl+C or close the window. If `python` is not recognised or
says `No module named ...`, see [Before you start](https://holdi601.github.io/3DHeat-Watcher/before-you-start.html#common-errors).

## Commands

| Command | Options | Does |
|---|---|---|
| `run` | `--once` one look, then stop; `-v` verbose | watch in the background: record every game that is running |
| `games` | `--markdown` the table for the docs | what each game gives and from where |
| `setup <id \| all>` | `--apply` make the changes (backups kept) | switch a game's own output on |
| `status` | | which games are running now, and what would be recorded |
| `sessions` | `--game NAME`, `--limit N` | the recordings so far |
| `stats` | `--game NAME`; `--csv DIR` write sessions, events and stats as CSV | totals per game |
| `table <session folder>` | | rebuild a session's `heat.parquet` from its `events.jsonl` |
| `replays <adapter id> [folder]` | `-v` | convert the replays already on disk |
| `dota-replay <match id> ...` | `-o DIR` where to save; `--convert`; `-v` | download a public Dota 2 match's replay |
| `dota-map [map] -o FILE` | `--game DIR`; `--source2viewer EXE`; `--detail UNITS` | the Dota 2 map as a 3D level, by the separate 3DHeat-Ext-Dota tool |
| `update` | `--check` only ask | update to the newest release |
| `config` | `--set KEY=VALUE ...` (`KEY.ID=VALUE` for one entry of a dictionary) | show or change the settings |

`python -m heat3d_watch --version` prints the version; `<command> --help` the options. Every
command with examples: [Commands](https://holdi601.github.io/3DHeat-Watcher/commands.html).

![stats on synthetic example sessions](docs/assets/img/stats.svg)

## Output


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
  - `heat.raw.parquet` - everything the source sent, kept whole (live feeds);
    converted replays write their table, `<match>.match.json` and sidecars here
- `watcher.sqlite` - the statistics of every session, in three plain tables
  (`sessions`, `events`, `stats`) any SQL tool or spreadsheet reads
- `watcher.log` - what the watcher did

`heat.parquet` has `time`, `ms`, `event`, `x`, `y`, `z`, `player`, `team`, `session` and the
game's own fields as columns; its footer tells the viewer the axes and units, so it opens
with nothing to set. Every file and column: [The data](https://holdi601.github.io/3DHeat-Watcher/the-data.html).
The viewer's one-file-a-match format, which the replay converters can write, is its
[`.3dheat` container](https://holdi601.github.io/3DHeat/container.html)
([spec source](https://github.com/Holdi601/3DHeat/blob/main/docs/container.md)).

![a session folder (synthetic)](docs/assets/img/session-folder.svg)

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
watcher: [3DHeat-Ext-WarThunder](https://github.com/Holdi601/3DHeat-Ext-WarThunder)
(`exporters/ext/warthunder-replay` in 3DHeat), which installs the
`heat3d-wt-replay` command (`pip install -e <3DHeat>/exporters/ext/warthunder-replay`).
The format is undocumented and Gaijin's EULA forbids reverse engineering the
game, so it is kept apart: without it the watcher runs as before and says once
that it is missing. With it, each new replay in `<War Thunder>/Replays` becomes
a session with every aircraft's track, the kills and hits where they happened,
and who was who where the replay says so. What it reads and does not read is in
its own README.

**World of Tanks and World of Warships replays** (`.wotreplay`, `.wowsreplay`)
are read the same way, by a converter of each outside the watcher:
[3DHeat-Ext-WoT](https://github.com/Holdi601/3DHeat-Ext-WoT) (`heat3d-wot-replay`) and
[3DHeat-Ext-WoWs](https://github.com/Holdi601/3DHeat-Ext-WoWs) (`heat3d-wows-replay`), each installed with `pip install -e` on its folder.
Wargaming's licence forbids reverse engineering and "unauthorized software ...
that interacts with a Product", and the replays are enciphered, so these too
are kept apart. With them, each new replay in the game's `replays` folder
becomes a session with every tank's or ship's position while the recording
player's client knew of it - its own team throughout, enemies while spotted -
and the kills where they happened. Their READMEs say what they read, on which
game versions, and what they do not.

**Squad demos** (server recordings) are read the same way by
[3DHeat-Ext-Squad](https://github.com/Holdi601/3DHeat-Ext-Squad) (`heat3d-squad-demo`), when it is
installed. **CS2 demos** go through [3DHeat CS2](https://github.com/Holdi601/3DHeat-CS2), and
**osu! replays** (`.osr`) are read by the watcher itself, to the format the osu! wiki publishes.

![replays and their converters](docs/assets/img/replays.svg)

**Dota 2 replays** (`.dem`) are read inside the watcher, through gem
(github.com/whanyu1212/gem-dota, MIT, `pip install gem-dota`): each replay in
`<Dota>/game/dota/replays` becomes a session with every hero's track, the kills,
objectives, wards and combat log. `dota-replay <match id>` downloads one public
match's replay (it needs internet; the match id is the number on the match's
page in the Dota client or on OpenDota). Details:
[Dota 2 replays](https://holdi601.github.io/3DHeat-Watcher/game-dota-replays.html).
With Dota 2 installed, the separate tool
[3DHeat-Ext-Dota](https://github.com/Holdi601/3DHeat-Ext-Dota) makes the map itself
a 3D level under those tables - ground, cliffs, water, trees and buildings - from
the game's own files; once it is installed, `dota-map -o dota.glb` runs it:
[Dota 2 map](https://holdi601.github.io/3DHeat-Watcher/dota-map.html).

The watcher updates itself while no game is running and starts again - never
in the middle of a game; `config --set auto_update=false` turns that off.

Which game is recorded how, and from where: [all games in one table](https://holdi601.github.io/3DHeat-Watcher/watcher.html)
and a [page per game](https://holdi601.github.io/3DHeat-Watcher/games.html).

**Arma 3 and Arma Reforger servers** can record whole missions with the server mods in
[`mods/`](mods/) (untested in the games so far): [Server recorder mods](https://holdi601.github.io/3DHeat-Watcher/server-mods.html).

Every adapter and replay decoder keeps everything its source holds: what it reads goes into the table and `meta.json`, everything it sent stays whole beside it (`heat.raw.parquet` for live feeds, the replay sidecars for replays), counted in `selfCheck.completeness` - [Converters keep everything](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md); each game's page has a Completeness section.

---

## Part of 3DHeat

3DHeat Watcher is one of the free tools around the 3DHeat viewer. Each is its
own project, with its own releases and licence:

| Tool | What it does | Docs |
|---|---|---|
| [3DHeat](https://github.com/Holdi601/3DHeat) | the viewer: heatmaps, race analysis and match review in 3D | [site](https://holdi601.github.io/3DHeat/) |
| [GameFiles](https://github.com/Holdi601/3DHeat-GameFiles) | courses and levels out of the files games ship, as 3D models | [site](https://holdi601.github.io/3DHeat-GameFiles/) |
| [GameCapture](https://github.com/Holdi601/3DHeat-GameCapture) | lap telemetry from racing games; levels rebuilt from gameplay video | [site](https://holdi601.github.io/3DHeat-GameCapture/) |
| [Unreal Exporter](https://github.com/Holdi601/3DHeat-UnrealExporter) | an Unreal Editor plugin that exports a level as one 3D model | [site](https://holdi601.github.io/3DHeat-UnrealExporter/) |
| [CS2](https://github.com/Holdi601/3DHeat-CS2) | Counter-Strike 2 demos into tables and match documents; maps into 3D models | [site](https://holdi601.github.io/3DHeat-CS2/) |
| [Watcher](https://github.com/Holdi601/3DHeat-Watcher) | records what games publish about your play, in the background | [site](https://holdi601.github.io/3DHeat-Watcher/) |
| [Ext-WarThunder](https://github.com/Holdi601/3DHeat-Ext-WarThunder) | War Thunder replays into tables and match documents | [site](https://holdi601.github.io/3DHeat-Ext-WarThunder/) |
| [Ext-WoT](https://github.com/Holdi601/3DHeat-Ext-WoT) | World of Tanks replays into tables and match documents | [site](https://holdi601.github.io/3DHeat-Ext-WoT/) |
| [Ext-WoWs](https://github.com/Holdi601/3DHeat-Ext-WoWs) | World of Warships replays into tables and match documents | [site](https://holdi601.github.io/3DHeat-Ext-WoWs/) |
| [Ext-Squad](https://github.com/Holdi601/3DHeat-Ext-Squad) | Squad server demos into tables and match documents | [site](https://holdi601.github.io/3DHeat-Ext-Squad/) |
| [Ext-DCS](https://github.com/Holdi601/3DHeat-Ext-DCS) | DCS World maps into 3D models | [site](https://holdi601.github.io/3DHeat-Ext-DCS/) |
| [Ext-IL2](https://github.com/Holdi601/3DHeat-Ext-IL2) | IL-2 Sturmovik maps into 3D models | [site](https://holdi601.github.io/3DHeat-Ext-IL2/) |

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

Documentation: <https://holdi601.github.io/3DHeat-Watcher/> (the source pages are in
[`docs/`](docs/)).
