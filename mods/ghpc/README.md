# 3DHeat Recorder for Gunner, HEAT, PC!

**Not yet run in the game.** The file it writes is tested: a made-up mission
goes through the mod's own writer and is read back by pyarrow and by the 3DHeat
viewer. What the mod reads in the game comes from the names public mods for the
game use, and was not checked against the game itself. Its first run writes a
probe of what it found (see "Testing it" below).

## What it does

Gunner, HEAT, PC! keeps no replays and sends no telemetry. This mod for
MelonLoader, the game's usual mod loader, records each mission while you play
and writes it into one `.3dheat` file. The 3DHeat viewer opens that file as it
is.

It records:

- **Units.** Every unit in the mission: vehicle, side, crew roles and weapons. It
  records each unit's position, heading, pitch, roll and speed 10 times a second,
  or once a second while the unit stands still. It also records the turret's
  traverse and the gun's elevation, both relative to the hull.
- **Rounds fired.** For each round: the shooter, weapon, ammunition name and
  kind, calibre and muzzle velocity, where it was fired from, and where it ended.
- **Hits.** For each hit:
  - the unit struck, and the point on it in that unit's own frame and in the world;
  - the way the round came;
  - the plate it struck, and the impact angle and speed;
  - whether it penetrated (the game's own penetration level);
  - further plates the same round struck, and the fragments a penetration threw.
- **Damage.** What each hit did: crew knocked out, parts destroyed, fires,
  ammunition going up, units out of the fight, and who did it. It also keeps the
  game's own account of each shot, the text it shows after a shot.
- **The mission.** Its name, its map, its states, how it ended and how long it
  took, and the game's log lines while it ran.

It only reads. Its hooks look at the game's rounds as they fly (`LiveRound`:
when a round starts, when it meets a surface, when the game reports its story).
They never skip, change or replace what the game does. The rest is read once or
a few times a second from the units. No setting, unit, round or input is
changed. A test fails the build if the mod's code sets anything in the game
(`tests/test_ghpc.py`).

It does not slow the game down noticeably:

- The game's thread only fills pooled rows, and writes nothing to disk.
- A background thread puts the rows in a spool file, flushed every second, and
  writes the mission's file when the mission ends.
- A unit is found once and then read, not searched for.

## Installing

1. **MelonLoader.** Download its installer from
   <https://github.com/LavaGang/MelonLoader/releases> and run it.
   - Pick `GHPC.exe` in `<Steam library>\steamapps\common\Gunner HEAT PC\Bin`.
   - Start the game once and close it again. MelonLoader sets itself up, and
     makes the `Mods` folder.
   - The watcher does not ship or download MelonLoader.
2. **The recorder.** Close the game, then use one of these:
   - the watcher's window: **Install or update the GHPC recorder**;
   - a terminal in the watcher's folder:

     ```
     python -m heat3d_watch ghpc install
     ```

     It finds the game in your Steam libraries, checks MelonLoader, says what it
     will copy and asks first. `--game-dir <folder>` names the game's folder when
     it is not in a Steam library. `python -m heat3d_watch setup ghpc --apply`
     does the same.
   - by hand: copy `Heat3DRecorder.GHPC.dll` into `<game>\Bin\Mods\`.
3. **Updates.** A newer watcher release brings a newer recorder.
   - `ghpc status` and the watcher's `--check` say when one is ready.
   - `ghpc install` updates it after asking, without asking when automatic updates
     are on (`--auto-update`, the window's checkbox, `HEAT3D_AUTO_UPDATE=1`).
   - The old DLL is kept in `<game>\Bin\UserData\Heat3DRecorder\backup\`.
4. **Removing it.** `python -m heat3d_watch ghpc remove`, or delete the DLL from
   `Mods`.

From a source checkout, `ghpc install --build` builds the mod first (needs the
[.NET SDK](https://dotnet.microsoft.com/download)):

```
dotnet build mods/ghpc/recorder -c Release
```

## Settings

The settings are in `<game>\Bin\UserData\MelonPreferences.cfg`, section
`[Heat3DRecorder]`. MelonLoader writes this section at the first start.

| Setting | Default | What it does |
|---|---|---|
| `Enabled` | `true` | Turns recording on or off. |
| `SampleHz` | `10` | Samples a second of each moving unit, 1 to 20. |
| `IdleHz` | `1` | Samples a second of a unit that does not move or turn. |
| `OutputFolder` | `%LOCALAPPDATA%\3DHeat\Watcher\recorders\ghpc` | Where the mission files go. |

## Output

Each mission becomes one file, `<mission>_<UTC start>.3dheat`, written when the
mission ends: you go back to the menu, restart it, or close the game. A mission
cut off by a crash is built at the next start from the spool that was left
behind (`<OutputFolder>\.spool\`). While the watcher runs, it files each new
mission as a session, so its statistics count it.

The file is a [3DHeat container](https://holdi601.github.io/3DHeat/container.html):

| Member | What it holds |
|---|---|
| `manifest.json` | `game: "ghpc"`, the match, the map, the start, the members with their SHA-256. |
| `<match>.parquet` | The table: one row per sample or event. Its `heat3d` footer tells the viewer the columns and axes. |
| `<match>.match.json` | The match document: the mission, the units, the kills, the result, the self-check. |
| `<match>.raw.parquet` | The game's log lines while the mission ran, kept whole. A line said more than 20 times is counted, not repeated. |
| `<match>.probe.json` | What the recorder found of the game (below). |

The table's columns follow the War Thunder converter's, so the viewer's replay,
Vehicles tab (hit analysis) and filters read them as they are:

| Columns | What |
|---|---|
| `time`, `event`, `match`, `mission`, `map`, `track`, `life`, `uid` | When (seconds since the mission began), what the row is, and which unit. |
| `player`, `team`, `ai`, `isPlayer`, `kind`, `type`, `Vehicle`, `VehicleName`, `crew` | Who and what. |
| `x`, `y`, `z`, `dirX/Y/Z`, `heading`, `pitch`, `roll`, `speed`, `alive`, `turretYaw`, `gunPitch` | Where and which way. Metres in Unity's axes (x east, y up, z north), angles in degrees, the turret + to the right. |
| `shotId`, `weapon`, `weaponName`, `calibre`, `ammoType`, `ammoName`, `muzzleVelocity`, `penetrationRha` | The round. |
| `other`, `otherVehicle`, `otherLife`, `otherTeam` | The other unit of an event. |
| `targetX/Y/Z`, `hitLocalX/Y/Z`, `hitDirX/Y/Z`, `hitOutcome`, `impactAngle`, `impactSpeed`, `plate`, `penetrated`, `penetrationLevel`, `spall`, `distance` | Where a round ended and what it struck. `hitLocal` and `hitDir` are in the struck unit's frame: x forward, y up, z right. |
| `crewRole`, `module`, `detail`, `text`, `state` | What a hit did, the game's own words, and mission states. |
| `won`, `matchWon`, `round`, `roundEndReason` | How the mission ended, for the row's side. |

The table's events:

| `event` | Row | What |
|---|---|---|
| (empty) | the unit | A sample. |
| `spawn` | the unit | First seen. |
| `launch` | the shooter | A round leaves the gun. |
| `shot` | the shooter | Where the round ended. `targetX/Y/Z` is the impact. On a unit it also has `otherVehicle`, `hitLocal*`, `hitDir*`, and `hitOutcome` (`penetration`, `nonpenetration`, `ricochet`); in the ground, `hitOutcome` is `ground`. |
| `plate_hit` | the unit struck | A further plate the same round struck. |
| `spall` | the unit struck | Fragments thrown by a penetration (`spall` = how many). |
| `crew_ko` | the unit struck | A crew member out (`crewRole`). |
| `module_destroyed` | the unit struck | A part destroyed (`module`). |
| `fire_on`, `fire_off` | the unit | Burning. |
| `ammo_detonation` | the unit | Its ammunition went up. |
| `destroyed` | the unit | Out of the fight. `other` is the unit that did it, and `state` says `neutralized` or `destroyed`. |
| `wrecked` | the unit | Destroyed later, after it was already out. |
| `story` | the shooter | The game's account of the shot (`text`). |
| `mission_state` | the player's unit | The mission's state changed (`state`). |
| `finish` | the unit | Its last row when the mission ends. |

What a hit did comes from two places: the unit's parts, watched for half a
minute after each hit, and the lines of the game's account of the shot. `detail`
says which one (`watched` or `shot story: ...`).

## Testing it

You need the game and MelonLoader installed; it takes about ten minutes.

1. Install as above. Start the game.
   - MelonLoader's console window should list **3DHeat Recorder 0.1.0**.
   - It also shows a line like `3DHeat Recorder 0.1.0: 3 hooks in, 0 names not found; files go to ...`.
   - Lines starting `left out:` say what it could not hook.
2. Play a short mission. An instant action or training range with a few enemies
   is enough. Fire some rounds: one that misses, one that bounces off, one that
   penetrates, and a kill if you can.
3. Go back to the main menu. The console says `wrote ...\<mission>_<time>.3dheat`.
4. Open that file in the 3DHeat viewer. Drop it on the Source panel, then check:
   - **Heatmap:** the tracks of every unit, coloured by side.
   - **Replay:** units move and turn their turrets; tracers fly from the shooter to where each round ended.
   - **Vehicles tab:** pick the unit you hit. It shows marks where your rounds struck, and **Who hit it** names you.
5. Send these two files to the developer. They hold nothing but what the game
   showed you, and the game's type and member names:
   - the mission file;
   - `<game>\Bin\UserData\Heat3DRecorder\probe-<game version>.json`: what the recorder found.
6. Things to note while you test, if you can:
   - whether the frame rate changed with the mod in (MelonLoader's console shows nothing about that; your own overlay does);
   - whether the mission's name and map in the file match what the game showed;
   - whether a hit's place on the Vehicles tab figure matches where you aimed.

If a part of the record is empty, the probe says why:

- `lookups` lists each name the recorder looked for and what it found. An empty
  value means not found.
- `hooks.skipped` lists what was not hooked.
- `types` lists the fields and methods of the game's types around units, rounds,
  armour, crews and damage. The names can be corrected from there without guessing.

## Files

```
recorder/Heat3DRecorder.GHPC.csproj   the mod (net472; MelonLoader, HarmonyX and Unity references only for the build)
recorder/Game/Mod.cs                  MelonLoader entry: settings, scenes, the mission's start and end
recorder/Game/Session.cs              one mission: units, samples, rounds, hits, damage, states
recorder/Game/Hooks.cs                the read-only hooks on the game's rounds
recorder/Game/Ghpc.cs, Api.cs         the game's types and members, found by name; compiled getters
recorder/Game/Probe.cs                what was found, written for the next fix
recorder/Format/*.cs                  the file: rows, spool, Parquet, Snappy, ZIP, container (no game, no Unity)
tests/synthetic/                      a made-up mission through the same writer, for the tests
```

## Licence

MIT, like the rest of the watcher. Built against MelonLoader's reference
package (Apache-2.0), HarmonyX (MIT) and Unity's module references. None of them
is copied into the DLL or shipped: MelonLoader brings its own copies when it is
installed. No code of the game or of other mods is included. The game's type and
member names the recorder looks for are the ones public mods for the game use.

Gunner, HEAT, PC! is made by Radian Simulations LLC. 3DHeat is not affiliated
with or endorsed by them.
