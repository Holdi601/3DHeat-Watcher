---
title: Dota 2 map
nav_order: 6.5
---

# Dota 2's map as a level (`dota-map`)

The Dota 2 map in 3D - ground, cliffs, water, every tree and the buildings, in
the frame and units the [Dota 2 replay tables](game-dota-replays.md) are drawn
in - is made by its own tool, **3DHeat Dota**
([3DHeat-Ext-Dota](https://github.com/Holdi601/3DHeat-Ext-Dota),
[documentation](https://holdi601.github.io/3DHeat-Ext-Dota/)), a project of
its own outside the watcher.

Install it once, as its [Before you start](https://holdi601.github.io/3DHeat-Ext-Dota/before-you-start.html)
page says (Python package, plus Source2Viewer's command line), then either

```bash
heat3d-dota-maps level -o dota.glb
```

or, through the watcher,

```bash
python -m heat3d_watch dota-map [<map>] -o <file.glb> [--game FOLDER] [--source2viewer EXE] [--detail UNITS]
```

which runs `heat3d-dota-maps level` with the same options and passes its output
and exit status through. The watcher finds the tool as the `heat3d-dota-maps`
command on `PATH`, as the installed `heat3d_ext_dota` package, or as its source
folder in `HEAT3D_DOTA_MAPS` or beside the watcher (`exporters/ext/dota-maps` in
a 3DHeat checkout). Nothing of it is imported into the watcher; it is only run.
When it is nowhere, `dota-map` prints where to get it and exits with code 2.

Load the `.glb` in the viewer's **Background / level** panel (**3D model…**)
under a Dota table: the viewer knows the file by its parts, keeps it in its
level library, and its **Dota 2 map** button loads it from then on. How the
level is made, its parts and how it was checked:
[Building a level](https://holdi601.github.io/3DHeat-Ext-Dota/level.html).
