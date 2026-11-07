# 3DHeat Recorder for Arma Reforger

**Untested. It has never been compiled or run.** The scripts were written from Bohemia's published script API (game version 1.9.0.37) without Workbench, so expect to fix compile errors on the first build. Do not put it on a public server until the test steps below pass.

## What it does

The mod records a match on the server. It doesn't run on players' machines, and they don't have to set anything up.

- Every second it writes the position, compass direction, life state (alive, unconscious or dead), vehicle and player id of every character. For every vehicle it writes the position, direction, whether it is destroyed, and its crew.
- It also logs these events: kills (with the killer, the weapon and the distance), hits on characters, getting in and out of vehicles, players joining and leaving, and the end of the mission (with the winning faction).
- Each session goes into its own file: `$profile:heat3d/<UTC date>_<UTC time>_<world>.jsonl`. The format is described in "Output" below.

It changes `SCR_BaseGameMode` with a `modded class`, so any scenario built on it records, including Conflict, Game Master, Combat Ops and most community scenarios. Recording starts only on the machine that owns the game mode: the dedicated server, or the host in a hosted or single player game. The mod adds no prefabs and no replicated data.

## Do players have to download it?

Yes, but the game handles it for them. Every mod in a server's `config.json` `mods` list is downloaded and turned on when a player joins (BI wiki, *Arma Reforger:Server Config*, `mods`). `"required": false` does not make a mod server-only. It only means the server still starts, minus that mod, if the Workshop download fails. The mod is a few small script files and does nothing on clients.

## Files

```
Heat3DRecorder.gproj                    project file (GUID 5D09A24C49D7FF18, depends on Arma Reforger 58D0FB3206B6F859)
license.txt                             MIT, used when publishing with "Custom license"
Scripts/Game/Heat3D/Heat3D_Recorder.c   sampling, events, file writing
Scripts/Game/Heat3D/Heat3D_GameMode.c   starts the recorder when a scenario starts
Scripts/Game/Heat3D/Heat3D_Damage.c     hit events from the character damage manager
```

I wrote the `.gproj` by hand, copying the layout of the game's own `addons/rally/RallyDLC.gproj`. If Workbench rejects it, use Create New in the Workbench launcher, pick Arma Reforger as the dependency, and copy the `Scripts` folder into the new project.

## Building and testing

You need:

- **Arma Reforger Tools**, the Workbench. It is free in Steam's Tools section if you own the game.
- **Arma Reforger Server**. It is free: Steam Tools, or SteamCMD app `1874900` with `login anonymous`.

1. Open Workbench, choose Add Existing, and pick `Heat3DRecorder.gproj`. Open the project and fix whatever the script compiler reports.
2. Quick check without a server: in Workbench's World Editor, open a small scenario and press Play. The recorder runs there as well, because single player is the authority. Look in the Workbench console log for `[Heat3D] recording to ...` and find the `heat3d` folder under the Workbench profile.
3. Local dedicated server with the unpublished mod (BI wiki, *Startup Parameters* and *Server Hosting*):
   ```
   ArmaReforgerServer.exe -server "worlds/MP/MPTest.ent" -addonsDir "C:\MyMods" -addons 5D09A24C49D7FF18 -profile "C:\ArmaServerProfile" -maxFPS 60
   ArmaReforgerSteam.exe -client 127.0.0.1 -addonsDir "C:\MyMods" -addons 5D09A24C49D7FF18
   ```
   `C:\MyMods` is the folder that contains this project's folder. The client also loads the local mod here because it is not on the Workshop yet. The wiki says `-addons` takes the ID from the `.gproj`, but its own example passes a project name, so if the GUID is not accepted, try `-addons Heat3DRecorder`.
4. Play for a few minutes: get in and out of a vehicle, kill an AI, get hit, disconnect. Then stop the server and check the `.jsonl` file. Look for it under `C:\ArmaServerProfile\profile\heat3d\` or `C:\ArmaServerProfile\heat3d\`; which of the two `$profile:` points to still has to be confirmed.
5. Publish it with Workbench > Publish Project. This needs a Bohemia account, which you link under Workbench > Link. Choose "Unlisted" visibility while testing (unlisted mods still work on dedicated servers) and "Custom license", which uses `license.txt`.
6. On a real server, add it to `config.json`:
   ```json
   "mods": [ { "modId": "5D09A24C49D7FF18", "name": "3DHeat Recorder" } ]
   ```
   then start with `ArmaReforgerServer.exe -config config.json -profile <dir>`.

## Output

The output is one JSON object per line, in this order: a `header` line, then `entity`, `frame` and `event` lines as they happen, and an `end` line.

```
{"type":"header","format":"heat3d-reforger","version":1,"world":"Eden","worldFile":"...","mission":"...","captureDelay":1.00,"startedUtc":"2026-11-07T20:00:00Z","axes":"x east, y up, z north; dir compass degrees"}
{"type":"entity","id":0,"kind":"unit","frame":0,"name":"Player","playerId":1,"faction":"US","group":0,"prefab":"Character_US_Rifleman"}
{"type":"entity","id":1,"kind":"vehicle","frame":0,"name":"M151A2","class":"car","faction":"US","prefab":"M151A2"}
{"type":"frame","frame":0,"ms":12345,"units":[[0,4825.10,15.30,6930.42,271,1,1,1]],"vehicles":[[1,4825.0,15.1,6930.0,270,1,[0]]]}
{"type":"event","event":[0,"getin",0,1]}
{"type":"event","event":[42,"killed",7,[0,"Rifle_M16A2"],153.2]}
{"type":"event","event":[42,"hit",8,[0,"Rifle_M16A2"],87.0]}
{"type":"event","event":[50,"connected","Name",3]}
{"type":"event","event":[90,"endMission",["US","ENDREASON_..."]]}
{"type":"end","frame":3600,"reason":"game end"}
```

- Unit rows are `[id, x, y, z, dir, alive (0 dead, 1 alive, 2 unconscious), vehicleId or -1, playerId or 0]`.
- Vehicle rows are `[id, x, y, z, dir, alive, [crew ids]]`.
- Coordinates are the engine's own: x east, y height, z north. In OCAP2's `[x, y, z]` that becomes `[x, z, y]`.
- The event arrays follow OCAP2's event layout, so 3DHeat's OCAP2 importer can pass them through. `getin` and `getout` are additions of this mod.
- An unknown killer is written as id `-1`, with an empty weapon and distance `-1`.

## Not verified yet

- That it compiles at all. In particular: `modded class` overrides of `protected` methods, `set<string>`, and the invoker signatures.
- Whether `$profile:` is the `-profile` folder itself or its `profile` subfolder on a dedicated server.
- Whether `OnControllableDestroyed` also fires for players (the code assumes it does and ignores `OnPlayerKilled`) and for vehicles.
- Whether `AIWorld.GetAIAgents` lists all AI or only AI near players. The 30-second world sweep is there as a fallback, and its cost on a full map is unmeasured.
- Whether `OnDamage` runs on the server for every hit, and how many calls one bullet makes.
- Whether characters face their entity's +Z axis, and whether vehicles do too.
- File size and frame time with 100+ players and AI.
- Whether `FileMode.APPEND` behaves as expected after the first `WRITE`.
