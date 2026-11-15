---
title: "Mapa Dota 2"
nav_order: 6.5
lang: "sk"
source: dota-map.md
source_hash: "c9830d37ea89"
nav_exclude: true
search_exclude: true
---
# Mapa Dota 2 ako level (`dota-map`) {#dota-2s-map-as-a-level-dota-map}

```bash
python -m heat3d_watch dota-map [<map>] -o <file.glb> [--game FOLDER] [--source2viewer EXE] [--detail UNITS]
```

zapíše mapu Dota 2 ako geometriu levelu pre viewer 3DHeat: zem, útesy, vodu, každý
strom a budovy, v rámci a jednotkách, v ktorých sa kreslia
[tabuľky z replayov Dota 2](game-dota-replays.md). Načítajte súbor `.glb` v paneli
viewera **Pozadie / level** (**3D model…**) pod tabuľkou Dota a teplo hrdinov bude
ležať na líniách, veže na svojich vežiach. Viewer pozná súbor podľa jeho častí
a uloží ho do svojej knižnice levelov. Odvtedy tlačidlo **Mapa Dota 2** načíta túto
3D mapu namiesto kresby z OpenDota. Kód:
[`heat3d_watch/decoders/dota_map.py`](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/decoders/dota_map.py).

Potrebuje nainštalovanú hru Dota 2 a príkazový riadok Source2Viewer. Nič z hry nie je
v nástrojoch ani nič z nich nesťahujú: mapa pochádza z vašej vlastnej inštalácie
a zapísaný súbor je váš na uchovanie, nie na zdieľanie - mapa patrí spoločnosti Valve.

## Čo je potrebné {#what-it-needs}

- **Dota 2**, nainštalovaná cez Steam. Bez `--game` sa hľadá ako
  `steamapps\common\dota 2 beta\game\dota` vo všetkých knižniciach Steamu. `--game`
  prijme priečinok `dota 2 beta` alebo jeho priečinok `game\dota`.
- **Príkazový riadok Source2Viewer** (ValveResourceFormat, licencia MIT,
  [vydania](https://github.com/ValveResourceFormat/ValveResourceFormat/releases)):
  `--source2viewer`, potom premenná prostredia `HEAT3D_SOURCE2VIEWER`, potom
  `Source2Viewer-CLI` / `Source2Viewer-CLI.exe` v `PATH` - rovnako ako príkaz `map`
  nástroja 3DHeat CS2, takže jedna kópia slúži obom.
- numpy (už ho potrebuje watcher).

`<map>` je `dota` (predvolená: bežná mapa) alebo názov inej mapy v
`game\dota\maps\`, alebo cesta k `.vpk` mapy.

## Ako sa vyrába {#how-it-is-made}

1. **Kolízna sieť.** Source2Viewer exportuje
   `maps/<map>/world_physics.vmdl_c` z `maps/<map>.vpk` ako glTF. Jeho skupiny sú
   pomenované podľa povrchu. Skupiny `clip` (neviditeľné steny) a `sky` sa zahodia.
   Skupiny `water`, `slime` alebo `window` sú **voda**: rieka a jazierka sú
   `water_slime`, úzke potôčiky cez džungľu sú `window`; v replayi stoja hrdinovia
   10 až 16 jednotiek pod prvými a niekoľko jednotiek pod druhými. Zachovajú sa
   len ich plochy smerujúce nahor. Všetko ostatné je terén, rozdelený plochu po
   ploche: plocha, ktorej normála smeruje nahor aspoň o 0,7 (svahy do asi 45
   stupňov), je **zem**; zvyšok - steny útesov, múry mapy - je **konštrukcia**.
2. **Entity.** Source2Viewer prevedie bloky entít mapy
   (`maps/<map>/entities/*.vents_c`) na text: bloky označené `====<n>====`, jeden
   `kľúč hodnota` na riadok. Použijú sa bloky `default_ents` a každá vrstva sveta,
   ktorú entita `info_world_layer` zobrazuje na začiatku (príznak spawnu 1) - vrstvy
   dvoch základní. Vrstvy, ktoré na začiatku skryté, obsahujú to, čo sa objaví, keď
   základňa padne, a vynechajú sa.
3. **Čo sa kreslí.** Stromy (`ent_dota_tree`) a budovy: veže, kasárne, pradávni
   (`npc_dota_fort`), výplne (`npc_dota_building`), výhľadové stanice, fontány,
   svätyne múdrosti, lotosové jazierka, dvojité brány, strážcovia
   (`npc_dota_lantern`) a neutrálne sklady predmetov. Obchody (obchodník je postava),
   sieň slávy, prápory, svetlá a častice nie sú.
4. **Modely.** Každý model, ktorý tieto entity menujú, sa exportuje z
   `game\dota\pak01_dir.vpk` jedným behom Source2Viewer. Tie siete modelu, ktoré sú
   iným stavom tej istej veci - pník zrezaného stromu, detailný záber v inšpektore,
   trosky - sa vynechajú podľa názvu (`stump`, `inspector`, `destruction`).
5. **Budovy** sú vlastná sieť ich modelu, zredukovaná **zhlukovaním vrcholov**:
   každý bod sa presunie na priemer bodov v kocke veľkosti `--detail` (predvolene
   8 jednotiek, asi tretina šírky hrdinu) a trojuholníky, ktoré sa zrútia alebo
   zopakujú, zmiznú. 0 zachová každý trojuholník.
6. **Stromy** sú obrys každého modelu ako nízke otočené teleso: jeho výška v piatich
   pásmach, každé ako šesťuholníkový prstenec tak široký, ako je väčšina bodov
   modelu v tejto výške (90. percentil ich vzdialenosti od osi kmeňa), uzavretý
   dole a zašpicatený hore - 60 trojuholníkov, skutočná výška a šírka modelu. Borovica
   vyjde ako kužeľ, dub ako guľa na stonke. Skutočné siete by vážili asi desaťkrát
   viac pri vyše 2 000 stromoch.
7. **Umiestnené** tak, ako ich hra umiestňuje: zmenšené podľa `scales`, otočené podľa
   `angles` (sklon, odklon a náklon Source v stupňoch), posunuté na `origin`.
8. **Do rámca viewera.** Source2Viewer zapisuje glTF v metroch, os Y nahor: (Y, Z, X)
   hry krát 0,0254. Toto sa vráti späť a každý bod sa zapíše ako (X, Z, -Y) hry: Y
   nahor, Y hry sa otočí na opačnú - rámec, v ktorom sa tabuľky Dota kreslia cez ich
   nápovedy `heat3d` (`up: z`, `flipY: true`, mierka 1). Ide o otočenie, nie o zrkadlenie.

## Súbor {#the-file}

Binárny glTF 2.0 ako u nástroja 3DHeat CS2 (pozrite si jeho stránku o exporte mapy):
jeden uzol a jedna sieť na každú časť v koreni, bez transformácií, s plochým tieňovaním
(vrchol pre každý roh trojuholníka nesie normálu svojho trojuholníka), indexy
`uint32`, bez materiálov, textúr alebo UV, `asset.generator` `heat3d_watch`, jednotky
hry.

| Časť | Čo |
|---|---|
| `ground:terrain` | zem, po ktorej sa dá chodiť |
| `structure:terrain` | steny útesov a múry mapy |
| `water:water_slime`, `water:window` | rieka a jazierka; potôčiky džungle |
| `structure:tree` | každý strom stojaci na začiatku |
| `structure:tower`, `structure:barracks`, `structure:ancient`, `structure:filler`, `structure:outpost`, `structure:fountain`, `structure:shrine`, `structure:lotus_pool`, `structure:twin_gate`, `structure:watcher`, `structure:neutral_stash` | budovy podľa druhu |

Prefix `ground:` / `structure:` / `water:` je spôsob, akým všetky exportéry levelov
3DHeat hovoria vieweru, čo je časť; viewer im verí na slovo. Keďže jednotky sú
jednotky hry (asi palec každá), iný prehliadač glTF zobrazí mapu asi 39-krát väčšiu;
v 3DHeat leží presne pod tabuľkou.

Čo vypíšete pri príklade behu (čísla závisia od verzie mapy):

```text
reading dota.vpk: collision mesh and entities
reading 30 models from pak01_dir.vpk
dota.glb: dota, 700,000 triangles (230,000 ground) in 16 parts; 2,400 trees, 70 buildings
```

Prvé dva riadky idú do chybového výstupu, posledný do výstupu. Model, ktorý
Source2Viewer nenašiel, sa vynechá a na konci posledného riadku je uvedený
(`; 1 model(s) not found, left out: ...`). Pri chybách – Dota 2 sa nenašla, mapa sa nenašla, Source2Viewer sa nenašiel alebo zlyhal – sa vypíše `dota-map: <dôvod>` a
skončí sa s kódom 1.

## Ako sa to overilo {#how-it-was-checked}

Na verejnom zápase zaznamenanom watcherom (patch 7.40) a na mape nainštalovanej hry:

- každá vzorka pozície hrdinu, ktorá sa pozrie kolmo nadol na najvyššiu plochu zeme
  najviac 64 jednotiek nad jeho nohami, nájde zem, stredná výška nad ňou je 0
  jednotiek a 99,5 % je do 16 jednotiek; so zrkadlenou mapou (Y nie je negované) ich
  nájde iba asi polovica a ostatné plávajú alebo sa prepadávajú o výšku útesu;
- 22 veží, 12 kasární, 2 pradávni, 14 výplní, 2 výhľadové stanice, 2 fontány a 10
  strážcov, ktoré tabuľka jednotiek v replayi umiestňuje, stojí na entitách mapy
  rovnakého druhu s presnosťou 0,02 jednotky, vodorovne aj vo výške;
- päta každého stromu je na zemi.

Testy (`tests/test_dota_map.py`) overujú čítač blokov, rámce, rozdelenie terénu,
obrysy stromov a zhlukovanie, umiestnenie a celý export s Source2Viewer nahradeným
pomocníkom - iba na zmyslených dátach.

## Čo nerobí {#what-it-does-not-do}

- Žiadne textúry ani farby: viewer cieni level po svojom.
- Žiadne stromy vyrúbané ani budovy zničené počas zápasu: mapa tak, ako začína.
- Udalostné a vlastné mapy nie sú otestované; ich triedy entít sa môžu líšiť.
- Rekvizity, ktoré len zdobia (kamene, ploty, prápory), sú v nej iba potiaľ, pokiaľ
  sú súčasťou kolíznej siete.
