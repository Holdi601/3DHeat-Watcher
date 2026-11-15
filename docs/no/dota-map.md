---
title: "Dota 2-kart"
nav_order: 6.5
lang: "no"
source: dota-map.md
source_hash: "3dcde11c7784"
nav_exclude: true
search_exclude: true
---
# Dota 2-kartet som nivå (`dota-map`) {#dota-2s-map-as-a-level-dota-map}

Dota 2-kartet i 3D - terreng, klipper, vann, hvert tre og bygningene - i rammen og
enhetene [Dota 2-replay-tabellene](game-dota-replays.md) er tegnet i, lages av sitt eget
verktøy, **3DHeat Dota**
([3DHeat-Ext-Dota](https://github.com/Holdi601/3DHeat-Ext-Dota),
[dokumentasjon](https://holdi601.github.io/3DHeat-Ext-Dota/)). Det leser Valves spillfiler,
så det holdes utenfor watcheren: skulle det noen gang måtte fjernes, blir watcheren stående.

Installer det én gang, slik siden [Før du begynner](https://holdi601.github.io/3DHeat-Ext-Dota/before-you-start.html)
sier (Python-pakke, pluss Source2Viewers kommandolinje), og kjør deretter enten

```bash
heat3d-dota-maps level -o dota.glb
```

eller, via watcheren,

```bash
python -m heat3d_watch dota-map [<map>] -o <file.glb> [--game FOLDER] [--source2viewer EXE] [--detail UNITS]
```

som kjører `heat3d-dota-maps level` med de samme valgene og sender utdata og
avslutningskode videre. Watcheren finner verktøyet som kommandoen `heat3d-dota-maps` på
`PATH`, som den installerte pakken `heat3d_ext_dota`, eller som kildemappen i
`HEAT3D_DOTA_MAPS` eller ved siden av watcheren (`exporters/ext/dota-maps` i en
3DHeat-kopi). Ingenting av det importeres inn i watcheren; det bare kjøres. Finnes det
ingen steder, skriver `dota-map` hvor du henter det, og avslutter med kode 2.

Last `.glb`-filen inn i visningens panel **Bakgrunn / nivå** (**3D-modell…**) under en
Dota-tabell: visningen kjenner filen på delene sine, lagrer den i nivåbiblioteket, og
knappen **Dota 2-kart** laster den fra da av. Hvordan nivået lages, delene og hvordan
det ble kontrollert: [Bygge et nivå](https://holdi601.github.io/3DHeat-Ext-Dota/level.html).
