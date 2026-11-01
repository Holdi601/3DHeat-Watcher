---
title: Installing and running
nav_order: 2
---

# Installing and running

## Requirements

- **Windows.** The watcher is written for Windows, and most of its sources exist only there: shared
  memory that games create (`Local\...` mappings), the registry (where Steam is), Windows
  notifications, the process list with executable paths. On another system the program starts, but
  those sources find nothing, notifications are only logged, and memory reading refuses ("only
  implemented on Windows").
- **Python 3.** The repository does not state a minimum version. 3.10 or newer is a safe choice;
  older versions have not been checked.
- **Packages** (`requirements.txt`): `psutil>=6.0` (which games are running, which program holds a
  port, a game's connections; an older psutil still works, through its older name for a process's
  connections), `pyarrow>=15` (writing `heat.parquet`), `numpy>=1.24`, and
  `pytest>=8.0` for the tests. `requirements-optional.txt` currently lists no packages.

Without `pyarrow`, sessions are still recorded: `events.jsonl` is the record, and the table can be
built later with [`table`](commands.md#table).

### Extras some games need

| Game | What it needs |
|---|---|
| Counter-Strike 2 demos | [3DHeat CS2](https://github.com/Holdi601/3DHeat-CS2) and its requirements (`demoparser2`). The watcher looks for it in `HEAT3D_CS2`, then in a folder `3DHeat-CS2` or `cs2` next to the watcher's own folder, then anywhere Python can import `heat3d_cs2` from. Without it, `games` lists the adapter as unavailable. |
| Microsoft Flight Simulator 2020 / 2024 | `SimConnect.dll` - not shipped. MSFS 2020 has one in its install folder; for MSFS 2024, install the MSFS 2024 SDK. `MSFS_SDK` / `MSFS2024_SDK` point to the SDK folder. |
| Euro Truck Simulator 2, American Truck Simulator | the RenCloud `scs-telemetry.dll` plugin (revision 12) in `<game>\bin\win_x64\plugins` |
| BeamNG.drive | the `heat3d` protocol mod, installed by `python -m heat3d_watch setup beamng --apply` |
| League of Legends (live) | optional: Riot's root certificate as `<data>\riotgames.pem`, so the local connection is verified |
| Minecraft | a `%APPDATA%\.minecraft` folder (Java Edition) |

Each game's page under [Games](games.md) says what has to be switched on in the game itself.
`python -m heat3d_watch games` marks an adapter `[unavailable: ...]` when something it needs is missing
on this machine.

## Installing

From a clone:

```bash
git clone https://github.com/Holdi601/3DHeat-Watcher.git
cd 3DHeat-Watcher
pip install -r requirements.txt
```

From a release: download the archive from the repository's releases, unpack it, then run
`pip install -r requirements.txt` inside the folder. Both kinds of copy update themselves
(see [Updates](updates.md)).

Run every command from the repository folder: `python -m heat3d_watch` imports the package from there,
and the updater (`heat3d_update`) sits next to it.

## Running

```bash
python -m heat3d_watch run        # watch until stopped
python -m heat3d_watch run -v     # the same, with debug lines in the log
python -m heat3d_watch run --once # one look at the games running now, then stop and exit
```

On start, `run`:

1. writes the [lock file](#the-lock-file);
2. finishes any sessions an earlier run left open, for example after a crash
   (see [Recovery](the-data.md#recovery-after-a-crash));
3. every `scan_seconds` (2 s), reads the process list (names and paths only, no process is opened)
   and starts an adapter, in a thread of its own, for each game it finds. When a game's process is
   gone, its adapter is stopped and the sessions it had open are closed, which writes their table and
   their line in the statistics. Adapters that do not wait for a game (Steam statistics, Steam
   Timeline, NVIDIA highlights, the replay folders) run the whole time;
4. while no game is running, looks for a newer release at most once an hour and, with `auto_update`
   on, installs it and starts itself again (see [Updates](updates.md)).

An adapter that fails is logged and does not stop the others. If an adapter's poll fails 20 times in a
row, or its start fails, the adapter is stopped and not restarted until the game is started again (a
new process id).

Stop the watcher with Ctrl+C. The adapters close their sessions before it exits. If the watcher is
killed instead (Task Manager, a crash, a power cut), nothing that was already written is lost: the
next `run` finishes those sessions.

`--once` takes a single look: it starts the adapters for the games running at that moment (and the
always-on ones), lets each poll once - waiting at most 10 seconds for that - and then stops them the
way a game ending would, so the sessions they opened are closed, their tables written and their lines
counted in the statistics before it exits. Use it to check that a game is detected, not to record.

### Replays already on disk

The first time a replay adapter sees one of its folders, it only notes the replays already in it: a
player with years of demos would otherwise find the watcher busy converting for a day. From then on
every new replay is converted once the game has finished writing it. The old ones are converted on
request with [`replays`](commands.md#replays):

```bash
python -m heat3d_watch replays cs2-demos              # every demo in CS2's folders and replay_folders
python -m heat3d_watch replays osu-replays D:\Old     # the replays in one folder
```

### Running in the background

The watcher has no window of its own; it is a console program that runs until it is stopped. It
writes everything to `watcher.log`, so it does not need a visible console. Ways to keep it out of
the way:

- start it in a console and minimise the console: `start "" /min python -m heat3d_watch run` from
  `cmd`, in the repository folder;
- start it without a console: `pythonw -m heat3d_watch run`. Console output is lost, but `watcher.log`
  is still written. To stop it, end the `pythonw.exe` process; the next start then finishes the
  sessions it left open. The project has not tested this way of running.

### Starting with Windows (an idea)

The watcher does not install itself to start with Windows. To start it automatically:

- **Task Scheduler**: create a task with the trigger *At log on* and the action *Start a program*,
  program `pythonw.exe` (or `python.exe`), arguments `-m heat3d_watch run`, *Start in* set to the
  repository folder;
- **Startup folder**: put a shortcut in `shell:startup` with the same program, arguments and *Start in*
  folder.

Neither is part of the watcher or tested by it. The [lock file](#the-lock-file) makes sure a second copy
started by mistake exits at once.

## The lock file

`<data>\watcher.lock` holds the process id of the running watcher. When `run` starts and the lock file
names a process that still exists and whose name contains `python`, it prints

```text
A watcher is already running (process 12345) for C:\Users\...\3DHeat\Watcher.
```

and exits with code 1. Two watchers on one data folder would record every game twice, and the second
would treat the first one's open sessions as left over from a crash. A lock file whose process is
gone, or belongs to another program, is overwritten. When `run` ends, it removes the lock file if the
file still names its own process.

## The log

`<data>\watcher.log` is written by `run` only; the other commands print to the console. Each line has
the time, the level and a message:

```text
2026-05-01 20:15:01,123 INFO watching; data in C:\Users\...\AppData\Local\3DHeat\Watcher
2026-05-01 20:15:03,456 INFO f1-25: starting (EA SPORTS F1 25)
2026-05-01 21:02:11,789 INFO f1-25: stopping
```

Adapters log what they cannot do and why: "UDP 20777 is in use by ...; not taking it from that program",
"not reading memory: the game is played online", "could not start", "poll failed (3)" with the
traceback. `run -v` adds debug lines. The file is appended to and never rotated or emptied by the
watcher; delete it whenever you like. The same lines also go to the console.

## Where everything is

The home folder is `%LOCALAPPDATA%\3DHeat\Watcher`, or `HEAT3D_WATCH_HOME` when that is set (without
`LOCALAPPDATA`, for example on another system, `~/.local/share/3DHeat/Watcher`). `settings.json` is
always in the home folder. Everything else goes to the data folder, which is the home folder unless the
`data` setting names another one:

| Path | What it is |
|---|---|
| `<home>\settings.json` | the settings |
| `<data>\sessions\` | the recordings, one folder per sitting ([The data](the-data.md)) |
| `<data>\watcher.sqlite` | the statistics database |
| `<data>\watcher.log` | the log of `run` |
| `<data>\watcher.lock` | the lock file, while `run` runs |
| `<data>\state\` | what the always-on and replay adapters have already seen (`steam-stats.json`, `replays-cs2-demos.json`, ...), so a restart records nothing twice |
| `<data>\profiles\*.json` | memory profiles you wrote ([Reading memory](memory-reading.md)) |
| `<data>\riotgames.pem` | optional, Riot's root certificate for the League of Legends live adapter |
| `%LOCALAPPDATA%\3DHeat\update-check-3DHeat-Watcher.json` | the cached answer of the last release check |

The watcher deletes nothing in these folders, except a session folder in which nothing was recorded
(a game left in its menus).

## Settings

`python -m heat3d_watch config` shows the settings; `config --set key=value ...` changes them and saves
`settings.json` (see [config](commands.md#config)). The file is plain JSON and can also be edited by
hand while the watcher is not running. Unknown keys in it are ignored. Settings are read when a command
starts, so restart `run` after changing them.

| Setting | Default | What it does |
|---|---|---|
| `data` | `""` | The data folder. Empty: the home folder. |
| `disabled` | `[]` | Adapter ids that never run, for example `config --set disabled=steam-stats,nvidia-highlights`. Every other adapter runs when it finds its game. |
| `auto_update` | `true` | While no game is running, install a newer release and restart (see [Updates](updates.md)). `false`: only a notice in the log. |
| `scan_seconds` | `2.0` | Seconds between looks at the process list. |
| `memory` | `false` | Allow memory adapters (single-player games with a profile you wrote) to run. Off by default; see [Reading memory](memory-reading.md). |
| `replays` | `true` | Run the `replay` adapters: CS2 demos, osu!, League of Legends and VALORANT replays, IL-2 Tacview recordings. |
| `replay_folders` | `{}` | Extra folders by adapter id, for example `{"cs2-demos": ["D:\\Demos"]}`. Replay adapters watch them in addition to the game's own folders; `il2-tacview` also accepts install folders (it then looks in their `data\Tracks`); for `elite`, the first folder replaces the journal folder. Set one adapter's folders with `config --set replay_folders.cs2-demos=D:\Demos,E:\More`, or the whole dictionary as JSON. |
| `riot_id` | `""` | Your Riot ID (`Name#TAG`), so your own line in a League of Legends replay becomes your statistics. Empty: every player's line is kept, none is marked as yours. |
| `riot_api_key` | `""` | Your own Riot developer API key, to fetch each replayed League match's official timeline (positions each minute, kills where they happened). Empty: nothing is fetched. |
| `riot_platform` | `"EUW1"` | Your League server's platform id (`EUW1`, `EUN1`, `NA1`, `KR`, ...), used to find the regional Match-V5 host. |
| `player_names` | `{}` | Your name in games whose interface names every player but does not say which one is you, by adapter id: `warthunder-webmap` (the kill feed's lines about you become your kills and deaths) and `rocketleague-stats` (your rows become `me`; without it, the player the game's camera follows). Set with `config --set player_names.warthunder-webmap=Name`. |

A `settings.json` with every default:

```json
{
  "data": "",
  "disabled": [],
  "auto_update": true,
  "scan_seconds": 2.0,
  "memory": false,
  "replays": true,
  "replay_folders": {},
  "riot_id": "",
  "riot_api_key": "",
  "riot_platform": "EUW1",
  "player_names": {}
}
```

## Environment variables

| Variable | Effect |
|---|---|
| `HEAT3D_WATCH_HOME` | the home folder (settings, and the data unless `data` says otherwise) |
| `HEAT3D_NO_UPDATE` | any value but empty, `0`, `false` or `no` switches the release check and the automatic update off |
| `HEAT3D_NO_TOAST` | any non-empty value: no Windows notifications, only log lines |
| `HEAT3D_CS2` | the folder of 3DHeat CS2, for CS2 demos |
| `HEAT3D_CS2_GSI_PORT` | the CS2 game-state port (default 3311); the cfg file `setup` writes uses it |
| `HEAT3D_DOTA_GSI_PORT` | the Dota 2 game-state port (default 3312) |
| `MSFS_SDK`, `MSFS2024_SDK` | the MSFS SDK folders, where `SimConnect SDK\lib\SimConnect.dll` is looked for |

Windows notifications are used for updates only: "Updating to 1.2.0", or "1.2.0 is out; not updated:
..." when the update could not be applied. They are shown through PowerShell's own notification API,
so nothing has to be installed. The title and text are passed to PowerShell as environment variables,
never as part of the script.
