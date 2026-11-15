---
title: Dota 2-kartan
nav_order: 6.5
lang: "sv"
source: dota-map.md
source_hash: "3dcde11c7784"
nav_exclude: true
search_exclude: true
---
# Dota 2:s karta som nivå (`dota-map`) {#dota-2s-map-as-a-level-dota-map}

Dota 2-kartan i 3D – mark, klippor, vatten, varje träd och byggnaderna – i det koordinatsystem och de enheter som [Dota 2-replaytabellerna](game-dota-replays.md) ritas i, görs av ett eget verktyg, **3DHeat Dota** ([3DHeat-Ext-Dota](https://github.com/Holdi601/3DHeat-Ext-Dota), [dokumentation](https://holdi601.github.io/3DHeat-Ext-Dota/)). Det läser Valves spelfiler, så det hålls utanför watchern: om det någon gång måste bort finns watchern kvar.

Installera det en gång, så som sidan [Innan du börjar](https://holdi601.github.io/3DHeat-Ext-Dota/before-you-start.html) säger (ett Python-paket, plus Source2Viewers kommandorad), och kör sedan antingen

```bash
heat3d-dota-maps level -o dota.glb
```

eller, via watchern,

```bash
python -m heat3d_watch dota-map [<map>] -o <file.glb> [--game FOLDER] [--source2viewer EXE] [--detail UNITS]
```

som kör `heat3d-dota-maps level` med samma alternativ och skickar vidare dess utdata och avslutskod. Watchern hittar verktyget som kommandot `heat3d-dota-maps` i `PATH`, som det installerade paketet `heat3d_ext_dota`, eller som dess källmapp i `HEAT3D_DOTA_MAPS` eller bredvid watchern (`exporters/ext/dota-maps` i en 3DHeat-checkout). Ingenting av det importeras in i watchern; det bara körs. När det inte finns någonstans skriver `dota-map` var man får det och avslutar med kod 2.

Läs in `.glb`-filen i visarens panel **Bakgrund / nivå** (**3D-modell…**) under en Dota-tabell: visaren känner igen filen på dess delar, sparar den i sitt nivåbibliotek, och knappen **Dota 2-karta** laddar den därefter. Hur nivån görs, dess delar och hur den kontrollerats: [Bygga en nivå](https://holdi601.github.io/3DHeat-Ext-Dota/level.html).
