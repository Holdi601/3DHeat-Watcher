---
title: Gunner, HEAT, PC! recorder
nav_order: 11
---

# The Gunner, HEAT, PC! recorder

Gunner, HEAT, PC! keeps no replays and sends no telemetry. The recorder is a mod
you add to the game's mod loader, MelonLoader. It writes each mission into one
`.3dheat` file, and the 3DHeat viewer opens that file as it is: every unit's
track, every round fired, where each hit landed on the vehicle it struck, and
what the hit did.

**Status: not yet run in the game.** The file format is tested: a made-up
mission goes through the mod's own writer and is read back by pyarrow and by
the viewer. Its first run in the game writes a probe of what it found.

```
  GHPC + MelonLoader + recorder  ──>  <mission>_<time>.3dheat  ──>  3DHeat viewer
                                       (one file a mission)         Heatmap, Replay, Vehicles
```

## In short

1. Install MelonLoader from <https://github.com/LavaGang/MelonLoader/releases>.
   Pick `GHPC.exe`, then start the game once and close it.
2. Install the recorder: run **Install or update the GHPC recorder** in the
   watcher's window, or this in a terminal:

   ```
   python -m heat3d_watch ghpc install
   ```

   It finds the game, checks MelonLoader, says what it copies and asks first.
3. Play. Each mission ends up in `%LOCALAPPDATA%\3DHeat\Watcher\recorders\ghpc`.
   The watcher, while it runs, files each one as a session.
4. Open the file in the viewer.

Commands to look after it:

- `ghpc status` says what is installed and whether an update is ready.
- `ghpc install` updates it after asking (without asking when automatic updates
  are on).
- `ghpc remove` takes it out again.

The mod changes nothing in play. Its hooks only look at the game's rounds as they
fly, and the rest is read from the units a few times a second. Writing happens
on a thread of its own, so the game's frames are not held up.

The full documentation is in the mod's README,
[`mods/ghpc`](https://github.com/Holdi601/3DHeat-Watcher/tree/main/mods/ghpc).
It covers what is recorded, the settings, the file's columns and events, and the
test steps.

Gunner, HEAT, PC! is made by Radian Simulations LLC. 3DHeat is not affiliated
with or endorsed by them.
