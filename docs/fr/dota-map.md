---
title: Carte Dota 2
nav_order: 6.5
lang: "fr"
source: dota-map.md
source_hash: "6c7a1c39d1bf"
nav_exclude: true
search_exclude: true
---
# La carte de Dota 2 en niveau (`dota-map`) {#dota-2s-map-as-a-level-dota-map}

La carte de Dota 2 en 3D - le sol, les falaises, l'eau, chaque arbre et les bâtiments, dans le cadre et les unités où sont dessinées les [tables de replays Dota 2](game-dota-replays.md) - est faite par son propre outil, **3DHeat Dota**
([3DHeat-Ext-Dota](https://github.com/Holdi601/3DHeat-Ext-Dota),
[documentation](https://holdi601.github.io/3DHeat-Ext-Dota/)), un projet à part entière, en dehors du watcher.

Installez-le une fois, comme l'explique sa page [Avant de commencer](https://holdi601.github.io/3DHeat-Ext-Dota/before-you-start.html)
(paquet Python, plus la ligne de commande de Source2Viewer), puis lancez soit

```bash
heat3d-dota-maps level -o dota.glb
```

soit, par le watcher,

```bash
python -m heat3d_watch dota-map [<map>] -o <file.glb> [--game FOLDER] [--source2viewer EXE] [--detail UNITS]
```

ce qui lance `heat3d-dota-maps level` avec les mêmes options et transmet sa sortie et son code de sortie. Le watcher trouve l'outil sous forme de commande `heat3d-dota-maps` dans le `PATH`, de paquet `heat3d_ext_dota` installé, ou de son dossier source indiqué dans `HEAT3D_DOTA_MAPS` ou à côté du watcher (`exporters/ext/dota-maps` dans un dépôt 3DHeat). Rien de lui n'est importé dans le watcher ; il est seulement lancé.
Si l'outil est introuvable, `dota-map` indique où le récupérer et se termine avec le code 2.

Chargez le `.glb` dans le panneau **Arrière-plan / niveau** du visualiseur (**Modèle 3D…**) sous une table Dota : le visualiseur reconnaît le fichier à ses parties, le garde dans sa bibliothèque de niveaux, et son bouton **Carte de Dota 2** le charge à partir de là. Comment le niveau est fait, ses parties et comment il a été vérifié :
[Construire un niveau](https://holdi601.github.io/3DHeat-Ext-Dota/level.html).
