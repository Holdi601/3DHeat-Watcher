---
title: "Dota 2-kort"
nav_order: 6.5
lang: "is"
source: dota-map.md
source_hash: "3dcde11c7784"
nav_exclude: true
search_exclude: true
---
# Dota 2-kortið sem borð (`dota-map`) {#dota-2s-map-as-a-level-dota-map}

Dota 2-kortið í þrívídd - jörðin, klettarnir, vatnið, hvert einasta tré og byggingarnar, í sama
ramma og sömu einingum og [Dota 2 endursýningartöflurnar](game-dota-replays.md) eru teiknaðar í - er búið til með
sérstöku verkfæri, **3DHeat Dota**
([3DHeat-Ext-Dota](https://github.com/Holdi601/3DHeat-Ext-Dota),
[skjölun](https://holdi601.github.io/3DHeat-Ext-Dota/)). Það les leikjaskrár Valve og er því
haldið utan við watcher: ef það þarf einhvern tíma að hverfa, þá stendur watcher eftir.

Settu það upp einu sinni, eins og síðan [Áður en þú byrjar](https://holdi601.github.io/3DHeat-Ext-Dota/before-you-start.html)
segir til um (Python-pakki, auk skipanalínu Source2Viewer), og keyrðu svo annað hvort

```bash
heat3d-dota-maps level -o dota.glb
```

eða, í gegnum watcher,

```bash
python -m heat3d_watch dota-map [<map>] -o <file.glb> [--game FOLDER] [--source2viewer EXE] [--detail UNITS]
```

sem keyrir `heat3d-dota-maps level` með sömu valkostum og skilar úttaki þess og
skilakóða áfram óbreyttu. Watcher finnur verkfærið sem skipunina `heat3d-dota-maps`
á `PATH`, sem uppsetta pakkann `heat3d_ext_dota`, eða sem upprunamöppu þess í `HEAT3D_DOTA_MAPS` eða við hliðina á watcher (`exporters/ext/dota-maps` í
3DHeat-afriti). Engu úr því er hlaðið inn í watcher; það er aðeins keyrt.
Ef það finnst hvergi, prentar `dota-map` hvar hægt er að fá það og hættir með kóðann 2.

Hladdu `.glb` skránni í **Bakgrunnur / borð** spjaldinu í skoðaranum (**Þrívíddarlíkan…**)
undir Dota-töflu: skoðarinn þekkir skrána á hlutum hennar, geymir hana í
borðasafni sínu, og hnappurinn **Dota 2-kort** hleður henni þaðan í framhaldinu. Hvernig borðið er búið til, hlutar þess og hvernig það var athugað:
[Að byggja borð](https://holdi601.github.io/3DHeat-Ext-Dota/level.html).
