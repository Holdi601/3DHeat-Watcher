---
title: "Dota 2-térkép"
nav_order: 6.5
lang: "hu"
source: dota-map.md
source_hash: "c9830d37ea89"
nav_exclude: true
search_exclude: true
---
# A Dota 2 térképe pályaként (`dota-map`) {#dota-2s-map-as-a-level-dota-map}

```bash
python -m heat3d_watch dota-map [<map>] -o <file.glb> [--game FOLDER] [--source2viewer EXE] [--detail UNITS]
```

ez a parancs a Dota 2 térképét pályageometriaként írja ki a 3DHeat megtekintőnek: a talajt, a sziklafalakat, a vizet, minden fát és az épületeket, abban a keretben és mértékegységben, amelyben a [Dota 2 visszajátszási táblázatai](game-dota-replays.md) készülnek. Töltsd be a `.glb` fájlt a megtekintő **Háttér / pálya** paneljén (**3D-modell…**) egy Dota-táblázat alatt, és a hősök hője a sávokon fekszik, a tornyok pedig a saját tornyaikon. A megtekintő a részeiről ismeri fel a fájlt, és a pályakönyvtárában tartja; onnantól a **Dota 2-térkép** gombja ezt a 3D-s térképet tölti be az OpenDota rajza helyett. Kód: [`heat3d_watch/decoders/dota_map.py`](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/decoders/dota_map.py).

Telepített Dota 2 és a Source2Viewer parancssori programja kell hozzá. A játékból semmi nincs a eszközben, és nem is töltik le: a térkép a saját telepítésedből származik, a kész fájl a tiéd, megtartásra, nem megosztásra – a térkép a Valve-é.

## Mire van szükség {#what-it-needs}

- **Dota 2**, Steamen keresztül telepítve. A `--game` nélkül minden Steam-könyvtárban a `steamapps\common\dota 2 beta\game\dota` útvonalon keresi. A `--game` a `dota 2 beta` mappát vagy annak `game\dota` mappáját fogadja el.
- **Source2Viewer parancssori programja** (ValveResourceFormat, MIT, [kiadások](https://github.com/ValveResourceFormat/ValveResourceFormat/releases)): a `--source2viewer` kapcsoló, utána a `HEAT3D_SOURCE2VIEWER` környezeti változó, utána a `Source2Viewer-CLI` / `Source2Viewer-CLI.exe` a `PATH`-on. Ugyanaz, mint a 3DHeat CS2-eszközének `map` parancsa, így egy példány mindkettőhöz elég.
- numpy (a watcher már igényli).

A `<map>` a `dota` (az alapértelmezett: a szokásos térkép), vagy egy másik térkép neve a `game\dota\maps\` mappában, vagy egy térkép `.vpk` fájljának útvonala.

## Hogyan készül {#how-it-is-made}

1. **Az ütközési háló.** A Source2Viewer a térkép `maps/<map>/world_physics.vmdl_c` fájlját exportálja glTF-ben a `maps/<map>.vpk` fájlból. A csoportjai felület szerint vannak elnevezve. A `clip` (a láthatatlan falak) és a `sky` nevű csoportok kimaradnak. A `water`, `slime` vagy `window` nevű csoportok **víz**: a folyó és a tavak `water_slime`, a dzsungelen átfolyó keskeny patakok `window`. Replay-en a hősök az elsők alatt 10–16 egységgel, a másodikak alatt néhány egységgel állnak. Csak a felfelé néző lapjaik maradnak meg. Minden más a terep, lapról lapra szétválasztva: az a lap, amelynek normálvektora legalább 0,7-tel felfelé mutat (körülbelül 45 fokos lejtőig), a **talaj**; a többi – a sziklafalak, a térkép falai – a **szerkezet**.
2. **Az entitások.** A Source2Viewer a térkép entitásblokkjait (`maps/<map>/entities/*.vents_c`) szöveggé fejti vissza: `====<n>====` fejlécű blokkok, soronként egy `kulcs érték`. A felhasznált blokkok a `default_ents`, és minden `info_world_layer` entitás, amely a kezdetkor látszik (spawn flag 1) – ez a két bázis rétege. A kezdetben rejtett rétegek azt tartalmazzák, ami akkor jelenik meg, amikor egy bázis elesik; ezek kimaradnak.
3. **Mi kerül kirajzolásra.** A fák (`ent_dota_tree`) és az épületek: a tornyok, a kaszárnyák, az ősök (`npc_dota_fort`), a kitöltő épületek (`npc_dota_building`), az előőrsök, a szökőkutak, a bölcsesség-szentélyek, a lótuszmedencék, az ikerkapuk, az őrök (`npc_dota_lantern`) és a semleges tárgytárolók. Nem kerülnek be az üzletek (a boltos egy szereplő), a dicsőségcsarnok, a zászlók, a fények és a részecskék.
4. **A modellek.** Minden modellt, amelyet ezek az entitások megneveznek, egyetlen Source2Viewer-futtatással exportál a `game\dota\pak01_dir.vpk`-ból. Egy modell azon hálói, amelyek ugyanannak a dolognak egy másik állapotát mutatják – egy kivágott fa tuskója, a vizsgálónézetben látható közelkép, a romok – név szerint kimaradnak (`stump`, `inspector`, `destruction`).
5. **Az épületek** a saját modelljük hálója, amelyet **csúcspont-csoportosítással** ritkítunk: minden pont a `--detail` méretű kocka pontjainak átlagába kerül (alapértelmezés 8 egység, nagyjából egy hős szélességének harmada), a összeeső vagy ismétlődő háromszögek pedig eltűnnek. A 0 minden háromszöget megtart.
6. **A fák** modellenként a körvonalukként jelennek meg, alacsony, forgatott testként: öt magassági sávban, mindegyik egy hatszögű gyűrű, amely akkora, mint a modell pontjainak nagy része az adott magasságban (a törzs tengelyétől mért távolságuk 90. percentilise). Alul le van zárva, felül hegyesen végződik – 60 háromszög, a modell valódi magassága és szélessége. A fenyő kúp lesz, a tölgy gömb szárral. A valódi hálók nagyjából tízszer ennyi helyet foglalnának, 2000 körüli fánál.
7. **Elhelyezés** úgy, ahogy a játék helyezi: a `scales` szerint méretezve, az `angles` szerint elforgatva (a Source pitch, yaw, roll fokban), az `origin` pontra mozgatva.
8. **A megtekintő koordinátarendszerébe.** A Source2Viewer méterben, Y felfelé írja a glTF-et: a játék (Y, Z, X) értékei szorozva 0,0254-del. Ezt visszacsinálják, és minden pont (X, Z, -Y) alakban íródik: a játék Y felfelé, a játék Y-ja negálva. Ez az a keret, amelyben a Dota-táblázatok a `heat3d` tippjeik szerint (`up: z`, `flipY: true`, scale 1) rajzolódnak. Forgatás, nem tükrözés.

## A fájl {#the-file}

A 3DHeat CS2-eszköze által is használt glTF 2.0 bináris (lásd annak térkép-exportoldalát): a gyökérben minden részhez egy csomópont és egy háló, transzformáció nélkül, lapos árnyalással (a háromszögsarkonként egy csúcs, amely a háromszög normálját viszi), `uint32` indexekkel, anyagok, textúrák és UV-k nélkül, az `asset.generator` értéke `heat3d_watch`, a játék mértékegységeiben.

| Rész | Mi |
|---|---|
| `ground:terrain` | a bejárható talaj |
| `structure:terrain` | a sziklafalak és a térkép falai |
| `water:water_slime`, `water:window` | a folyó és a tavak; a dzsungelpatakok |
| `structure:tree` | minden fa, amely a kezdetkor áll |
| `structure:tower`, `structure:barracks`, `structure:ancient`, `structure:filler`, `structure:outpost`, `structure:fountain`, `structure:shrine`, `structure:lotus_pool`, `structure:twin_gate`, `structure:watcher`, `structure:neutral_stash` | az épületek, fajtánként |

A `ground:` / `structure:` / `water:` előtag az, ahogyan minden 3DHeat-pályaexportáló megmondja a megtekintőnek, mi az egyes rész; a megtekintő ezt szó szerint veszi. Mivel a mértékegységek a játékéi (egyenként körülbelül egy hüvelyk), egy másik glTF-megtekintő a térképet nagyjából 39-szer túl nagynak mutatja; a 3DHeat-ben pontosan a táblázat alatt fekszik.

Egy példafuttatás kiírása (a számok a térkép verziójától függnek):

```text
reading dota.vpk: collision mesh and entities
reading 30 models from pak01_dir.vpk
dota.glb: dota, 700,000 triangles (230,000 ground) in 16 parts; 2,400 trees, 70 buildings
```

Az első két sor a hibafolyamra megy, az utolsó a kimenetre. Amelyik modellt a Source2Viewer nem talál, kimarad, és az utolsó sor végén név szerint szerepel (`; 1 model(s) not found, left out: ...`). A hibák – nincs Dota 2, a térkép nincs meg, a Source2Viewer nincs meg vagy hibázik – `dota-map: <ok>` alakban íródnak ki, és 1-es kóddal lépnek ki.

## Ellenőrzés {#how-it-was-checked}

Egy nyilvános meccs watcher által átalakított replay-jén (7.40-es javítás) és a telepített játék térképén:

- minden hős-pozíciómintánál, ha függőlegesen lefelé nézve keressük a legmagasabb talajlapot, legfeljebb 64 egységgel a lába felett, talajt találunk; az ahhoz mért medián magasság 0 egység, és a minták 99,5%-a 16 egységen belül van. Ha a térképet tükrözzük (Y nincs negálva), csak nagyjából a fele talál talajt, a többi a szikla magasságával lebeg vagy süllyed;
- a replay egységtáblázatában szereplő 22 torony, 12 kaszárnya, 2 ős, 14 kitöltő épület, 2 előőrs, 2 szökőkút és 10 őr a térkép azonos fajtájú entitásain áll, 0,02 egységen belül, vízszintesen és magasságban egyaránt;
- minden fa talpa a talajon van.

A tesztek (`tests/test_dota_map.py`) ellenőrzik az entitásblokk-olvasót, a keretezést, a terep szétválasztását, a fák körvonalait és csúcspont-csoportosítását, az elhelyezést, valamint az egész exportot egy helyettesítővel játszott Source2Viewerrel – csak kitalált adatokon.

## Amit nem csinál {#what-it-does-not-do}

- Nincs textúra vagy szín: a megtekintő a pályát a saját módján árnyalja.
- Nem vágja ki a fákat és nem rombolja le az épületeket a meccs alatt: a térkép úgy van, ahogy indul.
- Az esemény- és egyedi térképek nincsenek tesztelve; az entitásosztályaik eltérhetnek.
- A puszta díszek (sziklák, kerítések, zászlók) csak annyiban vannak benne, amennyiben az ütközési háló részei.
