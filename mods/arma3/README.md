# Heat3D recorder for Arma 3 servers

A server-side mod that records every unit and vehicle of a mission and the
important events. It writes one file per mission, which 3DHeat opens as it
is. **Players install nothing:** the mod is loaded with `-serverMod`, so only
the server has it.

> **Status: untested in Arma 3.** The extension (the part that writes files)
> was built with MSVC and driven the way Arma calls extensions: quoted
> arguments, a mission written in parts, a crash in the middle, a mission
> closed properly. 3DHeat then read its output. The SQF scripts have not run
> in the game yet. See [Testing](#testing).

## What it records

Every `captureDelay` seconds (1 by default), one frame:

- **Every unit**, alive or dead: position (x east, y north, height above sea
  level, metres), compass heading, alive / dead / unconscious, whether it sits
  in a vehicle, name, player or AI, role, group and side.
- **Every vehicle**: position, heading, alive or wrecked, and who is in it.
- Its side is the side of its crew.

Events:

| Event | When |
|---|---|
| `killed` | Any unit or vehicle is destroyed. Records who did it, with which weapon (or vehicle), and from how far. Drone kills count for the drone's operator. |
| `hit` | A unit is hit. Records who hit it, with which weapon, from how far. |
| `getin` / `getout` | A unit gets into or out of a vehicle. |
| `connected` / `disconnected` | A player joins or leaves. |
| Mission start and end | `generalEvent` "Recording started." and `endMission`. |
| Shots fired | Per unit and frame. |

## The file

A recording uses **OCAP's JSON layout** (the format of the OCAP2 recorder, see
github.com/OCAP2/web). It is named like OCAP's own:
`2026_11_07__20_00_<mission>.json`.

- **3DHeat** reads it directly: drop the file on the viewer. Units become
  soldiers and vehicles their type, kills and hits go in the debrief list, and
  one mission is one session.
- **OCAP2's web player** can play it too.

How the extension writes it:

1. During the mission it appends to a journal,
   `<date>_<mission>.heat3d.part`. The journal is flushed on every write, so a
   server crash loses at most the last second.
2. When the mission ends, it turns the journal into the `.json` file.
3. If a server crashes or restarts without ending the mission, the extension
   finishes the leftover journal the next time a mission starts.

The files go to `recordings/` beside the extension, inside the `@heat3d`
folder. To write them somewhere else, set the environment variable
`HEAT3D_DIR` for the server process.

## Install on a server

1. **Build the extension**, once per platform. Arma 3's 64-bit server loads
   `heat3d_x64.dll` on Windows and `heat3d_x64.so` on Linux.
   - Windows: open a "x64 Native Tools Command Prompt for VS", go to
     `mods/arma3/extension`, run `cl /nologo /O2 /LD heat3d.c /Fe:heat3d_x64.dll`
   - Linux: in `mods/arma3/extension`, run
     `gcc -O2 -shared -fPIC -o heat3d_x64.so heat3d.c -ldl`
2. **Build the mod**: `python mods/arma3/build.py`. This writes
   `mods/arma3/@heat3d/` with `addons/heat3d_recorder.pbo` and the extension.
   No Arma 3 Tools are needed.
3. **Copy `@heat3d`** into the server's folder.
4. **Start the server with `-serverMod=@heat3d`**, alongside its other
   parameters.
5. Check the server's `.rpt` log for this line:

   ```
   Heat3D recorder 0.1.0: recording <file> every 1 s
   ```

Players need nothing: no download, no Workshop item, no key.

## Settings

The defaults are in the `Heat3D` class of `config.cpp`. A mission can change
any of them by setting the variable in its `init.sqf`, for example
`heat3d_captureDelay = 0.5;`.

| Setting | Default | What it does |
|---|---|---|
| `captureDelay` | 1 | Seconds between frames. 1 is OCAP's default too; 0.5–2 is sensible. |
| `recordHits` | 1 | 0 turns hit events off. See BattlEye below. |
| `recordShots` | 1 | 0 turns shot counting off. |
| `minPlayers` | 0 | Record only once this many players are on. |

## BattlEye, signatures and keys

**Signatures.** Signature checks apply only to addons that clients load. With
`verifySignatures = 2`, the server checks that each client's addons are signed
by a key in its `keys` folder. A `-serverMod` addon is loaded by the server
alone: it is not in the mod list clients must match, and it needs no `.bikey`
or `.bisign`. This is how OCAP, extDB3 and other server tools are run.

**BattlEye.** BattlEye's extension whitelist guards the clients: a client may
load only whitelisted DLLs. Extensions the server loads are not affected; OCAP,
extDB3 and Pythia run as server extensions on BattlEye servers. The recorder
sends nothing to the clients and asks nothing of them, with one exception:

- A `hit` event needs an `MPHit` handler on each unit. MP handlers are global,
  so the engine also runs that handler on the clients, where its first line
  (`if (!isServer) exitWith {}`) stops it.
- If the server's BattlEye filters object to that (`scripts.txt`, or a filter
  on MP event handlers), set `recordHits = 0`.
- Kills do not depend on it: they come from the server's own `EntityKilled`
  handler.

## Testing

Everything here can be done free, on one PC, without other players.

1. **Install the server.** In Steam (Library > Tools), install **Arma 3
   Server**, which is free. Or use SteamCMD (`app_update 233780`, which needs a
   Steam login). Arma 3 itself is needed only to join and watch.
2. **Build** the extension and the mod (see [Install on a server](#install-on-a-server)),
   and copy `@heat3d` into the server folder.
3. **Start a local server** with a stock mission:
   ```
   arma3server_x64.exe -port=2302 -config=server.cfg -serverMod=@heat3d -name=test
   ```
   Use a `server.cfg` whose mission cycle runs a vanilla mission with AI.
   The showcase and combat-patrol missions, or any editor mission with AI on
   two sides, will do.
4. **Check the log.** The `.rpt` should say `Heat3D recorder ... recording`.
   While the mission runs, a `.heat3d.part` file should grow in
   `@heat3d/recordings/`.
5. **Join** from Arma 3 (`127.0.0.1:2302`) and do something: drive, shoot,
   get killed. Then end the mission with `#missions` or by finishing it.
6. **Check the file.** `@heat3d/recordings/<date>_<mission>.json` should
   appear. Drop it on 3DHeat: tracks move with headings, vehicles carry their
   crews, and the debrief list shows the kills and the getin/getout events.
7. **Check crash recovery.** Kill the server process in the middle of a
   mission and start it again. The leftover `.part` file should become a
   `.json` file once the next mission starts.

**Still unverified in the game:**

- Whether `FiredMan`, added on the server, fires there for player units local
  to a client. If not, shots appear only for server AI.
- How many `MPHit` events one burst makes.
- How large one `callExtension` argument may be. The recorder sends at most
  about 8 kB per call.
- Whether `Ended` / `MPEnded` fire on a dedicated server for every way a
  mission ends. If one does not, the next mission's start finishes the file.
- The cost per frame with several hundred units.
- The Linux build of the extension. Only the Windows build has been compiled.

## Why this design

There were three ways to get the data out:

1. **A file format of our own** (CSV or Parquet, through an extension).
2. **ACMI**, Tacview's format.
3. **OCAP's JSON**, through a tiny extension. This is the one chosen.

SQF itself cannot write files. So with any of the three, either a native
extension writes them, or everything goes through `diag_log` into the `.rpt`
log. The log is shared with everything else, truncates long lines, and is
turned off on some hosts.

Why OCAP's JSON:

- **3DHeat already reads it**, with the right axes, sides, figures and events.
  So does OCAP's own web player. There is no converter step.
- **It holds what an Arma mission is**: sides, groups, roles, crews, and kills
  with killer, weapon and distance. ACMI is built for aircraft over the real
  earth. Arma's flat map would need invented latitudes and longitudes, and
  ACMI has no killer or crew fields.
- **The extension stays tiny:** one C file with no dependencies. It appends
  lines during the mission and regroups them by entity once at the end. SQF
  composes the JSON, so the extension never parses it.

The cost is that the native part has to be built, once per platform.

## Files

| Path | What it is |
|---|---|
| `addons/heat3d_recorder/` | The SQF addon: `config.cpp`, `functions/fn_*.sqf` |
| `extension/heat3d.c` | The file writer (callExtension), MIT |
| `build.py` | Packs the addon into a PBO and lays out `@heat3d/` |

MIT licence, like the rest of this repository. No code from OCAP's addon (GPL)
was used: the recorder only writes the same data layout, which OCAP2's web
player reads (OCAP2/web is MIT).
