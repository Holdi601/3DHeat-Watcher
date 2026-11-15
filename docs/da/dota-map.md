---
title: "Dota 2-kort"
nav_order: 6.5
lang: "da"
source: dota-map.md
source_hash: "3dcde11c7784"
nav_exclude: true
search_exclude: true
---
# Dota 2-kortet som bane (`dota-map`) {#dota-2s-map-as-a-level-dota-map}

Dota 2-kortet i 3D - terræn, klipper, vand, hvert træ og bygningerne, i de
koordinater og enheder som [Dota 2-replay-tabellerne](game-dota-replays.md)
er tegnet i - laves af sit eget værktøj, **3DHeat Dota**
([3DHeat-Ext-Dota](https://github.com/Holdi601/3DHeat-Ext-Dota),
[dokumentation](https://holdi601.github.io/3DHeat-Ext-Dota/)). Det læser Valves
spilfiler, så det holdes ude af watcheren: skulle det en dag fjernes, bliver
watcheren, som den er.

Installer det én gang, som siden [Før du begynder](https://holdi601.github.io/3DHeat-Ext-Dota/before-you-start.html)
beskriver (en Python-pakke og Source2Viewers kommandolinje), og kør derefter enten

```bash
heat3d-dota-maps level -o dota.glb
```

eller, gennem watcheren,

```bash
python -m heat3d_watch dota-map [<map>] -o <file.glb> [--game FOLDER] [--source2viewer EXE] [--detail UNITS]
```

Det sidste kører `heat3d-dota-maps level` med de samme indstillinger og sender
dets output og afslutningskode videre. Watcheren finder værktøjet som kommandoen
`heat3d-dota-maps` på `PATH`, som den installerede pakke `heat3d_ext_dota`, eller
som dets kildemappe i `HEAT3D_DOTA_MAPS` eller ved siden af watcheren
(`exporters/ext/dota-maps` i et 3DHeat-checkout). Intet af det importeres til
watcheren; det bliver kun kørt. Findes værktøjet ingen steder, skriver
`dota-map` hvor man henter det og afslutter med kode 2.

Indlæs `.glb`-filen i viewerens panel **Baggrund / bane** (**3D-model …**) under
en Dota-tabel. Vieweren kender filen på dens dele, gemmer den i sit banebibliotek,
og knappen **Dota 2-kort** indlæser den derfra fremover. Hvordan banen laves, dens
dele og hvordan den er kontrolleret:
[Bygning af en bane](https://holdi601.github.io/3DHeat-Ext-Dota/level.html).
