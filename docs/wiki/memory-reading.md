
# Reading memory

For single-player games that publish nothing, the watcher can read positions and values from the
game's memory, through a **profile** you write for your own build of the game. Of all the sources this
is the only one the game did not hand out, so it is fenced in more than the others:

- it is **off by default** (`python -m heat3d_watch config --set memory=true` switches it on);
- it reads, and has no way to write;
- **no profiles ship with the tools.**

Profiles do not ship because an offset is only right for the build it was found on. After a patch,
a profile that was right before reads garbage, and garbage looks just like numbers. A profile has to
be checked on the build a player has, by that player.

## The checks, in order

Every check below must pass. The first four are made **before** the game is opened, because opening a
protected game for reading is itself what an anti-cheat notices, and refusing afterwards would be too
late.

1. **The setting**: `memory` is true. Otherwise memory adapters are never started.
2. **A profile for the game**, whose `exe` names the running process. A profile states whether the
   game can be played online at all (`"online"`); one that leaves this out is rejected.
3. **No anti-cheat anywhere near it**:
   - no anti-cheat file in the game's folder or up to three folders above it (stopping at a Steam
     library's `common` folder, or at a folder with `steamapps` in it, since other games live above
     that): `EasyAntiCheat`, `EasyAntiCheat_EOS_Setup.exe`, `start_protected_game.exe`, `BattlEye`,
     `BEClient_x64.dll`, `BEService_x64.exe`, `EAAntiCheat.GameServiceLauncher.exe`, `AntiCheatExpert`,
     `SGuard64.exe`, `GameGuard`, `GameMon.des`, `XIGNCODE`, `xhunter1.sys`, `Vanguard`, `FACEIT`
     (compared in lower case, also as the start of a name). If the game's folder is unknown, the game is
     refused;
   - no anti-cheat driver or service running on the machine at all, as listed by
     `sc query type= driver state= active` and `sc query type= service state= active`: EasyAntiCheat,
     EasyAntiCheat_EOS, BEService, BEDaisy, vgk, vgc, ACE-BASE, ACE-GAME, xhunter1, FACEIT,
     FACEITService, EAAntiCheatService, Denuvo Anti-Cheat, npggsvc, Ricochet. A kernel anti-cheat
     installed for another game still watches every process. If the services cannot be listed, the
     game is refused.
4. **Not online**: a game whose profile says `"online": true` is read only while it has no connection
   to anything but this machine (any remote address other than `127.x`, `::1`). If its connections
   cannot be read, it is refused.
5. Then, as the adapter starts:
   - **the exact build**: the executable's file size, or its SHA-256, must match a version the profile
     lists. An unknown build is not read;
   - **the modules once more**: the game's loaded modules are listed (a Toolhelp snapshot, which asks
     for no access rights of its own) and checked for an anti-cheat client (`BEClient_x64.dll`,
     `BEClient.dll`, `EasyAntiCheat_x64.dll`, `EasyAntiCheat.dll`, `EOSAntiCheat...`). A protected
     process refuses the snapshot, which is also a refusal;
   - only then is the process opened, with `PROCESS_VM_READ | PROCESS_QUERY_LIMITED_INFORMATION` and
     nothing else.

Checks 1 to 4 are repeated at every scan (every 2 s) while the game runs. If one starts failing (the
game connects to a server, an anti-cheat service starts), the adapter is stopped at the next scan. A
refusal is logged: `mem-<id>: not reading memory: <reason>`. A failure while starting (unknown build,
an anti-cheat module, a pattern not found) is logged as `mem-<id>: could not start`, and the adapter
is not tried again until the game is started again.

There is no write, no allocation in the other process, no thread started in it, no library loaded into
it, no debug privilege and no elevation. A test (`test_memory_reading_cannot_write` in
`tests/test_core.py`) fails if any call that writes to, allocates in or runs code in another process -
`WriteProcessMemory`, `VirtualAllocEx`, `CreateRemoteThread`, `PROCESS_VM_WRITE`, `SeDebugPrivilege`,
`LoadLibrary`, ... - appears anywhere in the package.

Never read, whatever a profile says: games played online, and games whose single-player mode runs
under an anti-cheat, such as GTA V, or Elden Ring started through its launcher. The checks above refuse
them anyway.

## The profile format

A profile is a JSON file in `<data>\profiles\` (`<data>` is the data folder, see
[Installing and running](installing-and-running#where-everything-is)), one per game, any file name
ending in `.json`. A synthetic example:

```json
{
  "schema": "heat3d.memprofile/1",
  "id": "mygame",
  "game": "My Game",
  "exe": "MyGame.exe",
  "online": false,
  "versions": [ { "label": "1.06", "size": 123456789 } ],
  "anchors": {
    "World": { "aob": "48 8B 05 ?? ?? ?? ?? 48 85 C0", "rip": [3, 7] }
  },
  "values": {
    "pos": { "type": "vec3f", "base": "World", "chain": ["0x10", "0x68", "0x70"] },
    "hp":  { "type": "i32",   "base": "World", "chain": ["0x10", "0x138"] },
    "map": { "type": "u32",   "base": "World", "chain": ["0x10", "0x1C0"] }
  },
  "events": [
    { "event": "death", "value": "hp",  "when": "to_zero" },
    { "event": "zone",  "value": "map", "when": "change" }
  ],
  "axes": { "up": "y", "units": "metres" },
  "rate": 10,
  "provenance": [ { "source": "https://example.com/my-notes", "verified_on": "1.06" } ]
}
```

| Key | Required | What it is |
|---|---|---|
| `schema` | yes | exactly `heat3d.memprofile/1` |
| `id` | yes | short and stable; the adapter is called `mem-<id>` |
| `game` | yes | the game's name, which the session folder is named after |
| `exe` | yes | the executable's file name, which also says the game is running |
| `online` | yes | `true` if the game can be played online at all; it is then read only while offline |
| `versions` | yes | the builds the profile was checked on: each with a `label`, and a `size` (the executable's size in bytes) and/or a `sha256`. When both are given, both must match. An entry with neither matches nothing. |
| `anchors` | yes | named addresses in the main module. `aob`: a byte pattern, hex bytes separated by spaces, `?` or `??` for any byte; it must occur **exactly once** in the module image (several matches count as a failure, like none). `rip: [d, n]`: the pattern points at an instruction with a 32-bit RIP-relative displacement at byte `d` and length `n`; the anchor becomes the address that instruction refers to. `offset`: added afterwards (hex or decimal text). Instead of `aob`, `module_offset` gives a fixed offset from the module's base. |
| `values` | yes | what is read each poll: `type` (`i32`, `u32`, `i64`, `u64`, `u8`, `f32`, `f64`, `vec3f`, `vec3d`), `base` (an anchor's name), `chain` (offsets as hex or decimal text) |
| `events` | no | rules that turn changes into events: `when` `change` (the value differs from the last poll) or `to_zero` (a number drops from above 0 to 0 or below) |
| `axes` | no | `up` (default `y`), `units` (default `game units`), `scale` (the viewer's unit scale, which multiplies every position; default 1, the game's own units) |
| `rate` | no | polls per second, 1 to 60 (default 10) |
| `provenance` | no | where the offsets come from and on which build you verified them; it is copied into each session's `meta.json` |

**How a value is read.** The anchor's address is the start. If `chain` is empty, the value is read
right there. Otherwise the pointer stored at the anchor is read first. Then, for every offset but the
last, the pointer at `address + offset` is read. The last offset is added to give the value's address.
A null pointer on the way (the game is between levels or in a menu) leaves the value empty for that
poll.

**What is recorded.** A value named `pos` (a `vec3f` or `vec3d`) becomes a `position` row of player
`me` at every poll. Each event rule writes its `event` row, with the new value and, where `pos` is
known, the position, and adds 1 to a statistic of the same name. The module image is read once at start
to find the anchors, in 64 KiB blocks; blocks that cannot be read count as zeros. The session's
`meta.json` names the profile, the build label and the provenance.

A profile that cannot be used (bad JSON, the wrong `schema`, a required key missing) is skipped and
logged as `profile <file> not used: <reason>`. Profiles are loaded when the watcher starts, so restart
`run` after adding or changing one.

## Writing and verifying a profile

1. **Only for a single-player game without anti-cheat.** If the game has an anti-cheat, or you play it
   online, stop here: the watcher will refuse it, and it should.
2. **Find the values on your own build.** Work offline. Use your own debugging tools, or published notes
   on the game, to find the player's position and the values you care about, and a pointer path to
   each from a static place in the executable. Prefer a byte pattern (`aob`) over a fixed
   `module_offset`: a pattern still finds its place when code moves a little.
3. **Make the pattern unique.** It must match exactly once in the module. Wildcard the bytes that
   change (addresses, displacements) and keep enough fixed bytes around them.
4. **Pin the build.** Put the executable's exact size in `versions`; PowerShell
   `(Get-Item .\MyGame.exe).Length` gives it, and `Get-FileHash .\MyGame.exe -Algorithm SHA256` gives
   the hash. After a patch, the profile simply stops being used until you check it again and add the
   new build.
5. **Say whether the game goes online** (`online`), honestly.
6. **Try it**: switch reading on (`config --set memory=true`), put the file in `<data>\profiles\`, and
   check that `python -m heat3d_watch games` lists `mem-<id>`. Start the game and run
   `python -m heat3d_watch run -v`. In `watcher.log`, look for `mem-<id>: starting`, or for the reason
   it was refused or could not start.
7. **Check the numbers against the game.** Walk to a known place and look at the `position` rows in the
   session's `events.jsonl`. Do they move as you move, by the right amount, along the right axes? Open
   `heat.parquet` in the viewer and check that the route matches where you went. Trigger each event
   (lose all health, change zone) and check that it appears once. Garbage looks like numbers, and only
   this comparison tells the two apart.
8. **Write down what you verified** in `provenance`: the source of the offsets and the build you
   checked them on.

A memory adapter's `verified` text, as `games` prints it, is always "by the profile's author, for the
builds it lists". The watcher cannot know more than that.
