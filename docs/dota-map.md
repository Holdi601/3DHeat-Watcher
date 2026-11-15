---
title: Dota 2 map
nav_order: 6.5
---

# Dota 2's map as a level (`dota-map`)

```bash
python -m heat3d_watch dota-map [<map>] -o <file.glb> [--game FOLDER] [--source2viewer EXE] [--detail UNITS]
```

writes the Dota 2 map as level geometry for the 3DHeat viewer: the ground, the
cliffs, the water, every tree and the buildings, in the frame and units the
[Dota 2 replay tables](game-dota-replays.md) are drawn in. Load the `.glb` in
the viewer's **Background / level** panel (**3D model…**) under a Dota table
and the heroes' heat lies on the lanes, the towers on their towers. The viewer
knows the file by its parts and keeps it in its level library; from then on its
**Dota 2 map** button loads this 3D map instead of OpenDota's drawing. Code:
[`heat3d_watch/decoders/dota_map.py`](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/decoders/dota_map.py).

It needs Dota 2 installed and Source2Viewer's command line. Nothing of the game
is in the tools or downloaded by them: the map comes out of your own install,
and the file it writes is yours to keep, not to share - the map is Valve's.

## What it needs

- **Dota 2**, installed through Steam. Without `--game` it is looked for as
  `steamapps\common\dota 2 beta\game\dota` in every Steam library. `--game` takes
  the `dota 2 beta` folder or its `game\dota` folder.
- **Source2Viewer's CLI** (ValveResourceFormat, MIT,
  [releases](https://github.com/ValveResourceFormat/ValveResourceFormat/releases)):
  `--source2viewer`, then the `HEAT3D_SOURCE2VIEWER` environment variable, then
  `Source2Viewer-CLI` / `Source2Viewer-CLI.exe` on `PATH` - the same as the
  3DHeat CS2 tool's `map` command, so one copy serves both.
- numpy (already needed by the watcher).

`<map>` is `dota` (the default: the normal map) or another map's name in
`game\dota\maps\`, or the path to a map's `.vpk`.

## How it is made

1. **The collision mesh.** Source2Viewer exports the map's
   `maps/<map>/world_physics.vmdl_c` from `maps/<map>.vpk` as glTF. Its groups
   are named by surface. Groups named `clip` (the invisible walls) or `sky` are
   dropped. Groups named `water`, `slime` or `window` are **water**: the river
   and the ponds are `water_slime`, the narrow streams through the jungle are
   `window`; on a replay, heroes stand 10 to 16 units under the first and a few
   units under the second. Only their upward faces are kept. Everything else is the
   terrain, split face by face: a face whose normal points up by at least 0.7
   (slopes up to about 45 degrees) is **ground**, the rest - cliff faces, the
   map's walls - is **structure**.
2. **The entities.** Source2Viewer decompiles the map's entity lumps
   (`maps/<map>/entities/*.vents_c`) to text: blocks headed `====<n>====`, one
   `key value` per line. The lumps used are `default_ents` and each world layer
   an `info_world_layer` entity there shows at the start (spawn flag 1) - the
   two bases' layers. The layers that start hidden hold what appears when a
   base falls and are left out.
3. **What is drawn.** Trees (`ent_dota_tree`) and the buildings: towers,
   barracks, the ancients (`npc_dota_fort`), the fillers (`npc_dota_building`),
   outposts, fountains, the wisdom shrines, lotus pools, twin gates, watchers
   (`npc_dota_lantern`) and neutral item stashes. Shops (a shopkeeper is a
   character), the hall of fame, banners, lights and particles are not.
4. **The models.** Every model these entities name is exported from
   `game\dota\pak01_dir.vpk` in one Source2Viewer run. A model's meshes that are
   another state of the same thing - a cut tree's stump, the close-up shown in
   the inspector, rubble - are left out by name (`stump`, `inspector`,
   `destruction`).
5. **Buildings** are their model's own mesh, thinned by **vertex clustering**:
   every point moves to the mean of the points in its `--detail`-sized cube
   (default 8 units, about a third of a hero's width), and triangles that
   collapse or repeat go. 0 keeps every triangle.
6. **Trees** are each model's outline as a low turned solid: its height in five
   bands, each a six-sided ring as wide as most of the model's points at that
   height (the 90th percentile of their distance from the trunk's axis), closed
   at the bottom and pointed at the top - 60 triangles, the model's true height
   and width. A pine comes out a cone, an oak a ball on a stem. The real meshes
   would weigh about ten times as much over 2,000-odd trees.
7. **Placed** as the game places them: scaled by `scales`, turned by `angles`
   (Source's pitch, yaw, roll in degrees), moved to `origin`.
8. **Into the viewer's frame.** Source2Viewer writes glTF in metres, Y up: the
   game's (Y, Z, X) times 0.0254. That is undone, and every point written as
   (X, Z, -Y) of the game: Y up, the game's Y negated - the frame the Dota tables
   are drawn in through their `heat3d` hints (`up: z`, `flipY: true`, scale 1).
   A rotation, not a mirror.

## The file

A glTF 2.0 binary like the 3DHeat CS2 tool's (see its map export page): one
node and one mesh per part at the root, no transforms, flat-shaded (a vertex
per triangle corner carrying its triangle's normal), `uint32` indices, no
materials, textures or UVs, `asset.generator` `heat3d_watch`, units the game's.

| Part | What |
|---|---|
| `ground:terrain` | the walkable ground |
| `structure:terrain` | cliff faces and the map's walls |
| `water:water_slime`, `water:window` | the river and ponds; the jungle streams |
| `structure:tree` | every tree standing at the start |
| `structure:tower`, `structure:barracks`, `structure:ancient`, `structure:filler`, `structure:outpost`, `structure:fountain`, `structure:shrine`, `structure:lotus_pool`, `structure:twin_gate`, `structure:watcher`, `structure:neutral_stash` | the buildings, by kind |

The `ground:` / `structure:` / `water:` prefix is how all 3DHeat level
exporters tell the viewer what a part is; it takes them at their word. Because
the units are the game's (about an inch each), another glTF viewer shows the map
about 39 times too large; in 3DHeat it lies exactly under the table.

What it prints, on an example run (the numbers depend on the map's version):

```text
reading dota.vpk: collision mesh and entities
reading 30 models from pak01_dir.vpk
dota.glb: dota, 700,000 triangles (230,000 ground) in 16 parts; 2,400 trees, 70 buildings
```

The first two lines go to the error stream, the last to the output. A model
Source2Viewer could not find is left out and named at the end of the last line
(`; 1 model(s) not found, left out: ...`). Errors - Dota 2 not found, the map not
found, Source2Viewer not found or failing - print `dota-map: <why>` and exit
with code 1.

## How it was checked

On a public match's replay converted by the watcher (patch 7.40) and the map of
the installed game:

- every hero position sample looked straight down for the highest ground face
  at most 64 units above its feet finds ground, the median height above it is
  0 units, and 99.5 % are within 16 units; with the map mirrored (Y not
  negated) only about half find ground and the rest float or sink by a cliff's
  height;
- the 22 towers, 12 barracks, 2 ancients, 14 fillers, 2 outposts, 2 fountains
  and 10 watchers the replay's unit table places stand on the map's entities of
  the same kind to within 0.02 units, horizontally and in height;
- every tree's foot is on the ground.

The tests (`tests/test_dota_map.py`) check the lump reader, the frames, the
terrain split, the tree outlines and clustering, the placement, and the whole
export with Source2Viewer played by a stand-in - on made-up data only.

## What it does not do

- No textures or colours: the viewer shades the level its own way.
- No trees cut or buildings destroyed during a match: the map as it starts.
- Event and custom maps are untested; their entity classes may differ.
- The props that only decorate (rocks, fences, banners) are in it only as far
  as they are part of the collision mesh.
