---
title: "Harta e Dota 2"
nav_order: 6.5
lang: "sq"
source: dota-map.md
source_hash: "3dcde11c7784"
nav_exclude: true
search_exclude: true
---
# Harta e Dota 2 si nivel (`dota-map`) {#dota-2s-map-as-a-level-dota-map}

Harta e Dota 2 në 3D - toka, shkëmbinjtë, uji, çdo pemë dhe ndërtesat, në
kuadrin dhe njësitë në të cilat vizatohen [tabelat e riluajtjeve të Dota 2](game-dota-replays.md) - bëhet nga mjeti i vet, **3DHeat Dota**
([3DHeat-Ext-Dota](https://github.com/Holdi601/3DHeat-Ext-Dota),
[dokumentacioni](https://holdi601.github.io/3DHeat-Ext-Dota/)). Ai lexon
skedarët e lojës të Valve, ndaj mbahet jashtë watcher-it: nëse ndonjëherë duhet të hiqet, watcher-i
mbetet.

Instalo një herë, siç thotë faqja e tij [Para se të fillosh](https://holdi601.github.io/3DHeat-Ext-Dota/before-you-start.html)
(paketa Python, plus rreshti i komandave i Source2Viewer), pastaj ose

```bash
heat3d-dota-maps level -o dota.glb
```

ose, përmes watcher-it,

```bash
python -m heat3d_watch dota-map [<map>] -o <file.glb> [--game FOLDER] [--source2viewer EXE] [--detail UNITS]
```

që ekzekuton `heat3d-dota-maps level` me të njëjtat opsione dhe e kalon daljen
dhe kodin e daljes të tij. Watcher-i e gjen mjetin si komandën `heat3d-dota-maps`
në `PATH`, si paketën e instaluar `heat3d_ext_dota`, ose si dosjen e tij burimore në `HEAT3D_DOTA_MAPS` ose pranë watcher-it (`exporters/ext/dota-maps` në
një kopje të 3DHeat). Asgjë prej tij nuk importohet në watcher; ai vetëm ekzekutohet.
Kur nuk është askund, `dota-map` printon ku ta marrësh dhe del me kodin 2.

Ngarkoje `.glb` në panelin **Sfondi / niveli** të shikuesit (**Model 3D…**)
nën një tabelë të Dota-s: shikuesi e njeh skedarin nga pjesët e tij, e mban në
bibliotekën e niveleve, dhe butoni i tij **Harta e Dota 2** e ngarkon që nga ajo kohë. Si
bëhet niveli, pjesët e tij dhe si u kontrollua:
[Ndërtimi i një niveli](https://holdi601.github.io/3DHeat-Ext-Dota/level.html).
