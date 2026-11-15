---
title: "Zemljevid Dota 2"
nav_order: 6.5
lang: "sl"
source: dota-map.md
source_hash: "c9830d37ea89"
nav_exclude: true
search_exclude: true
---
# Zemljevid Dota 2 kot nivo (`dota-map`) {#dota-2s-map-as-a-level-dota-map}

```bash
python -m heat3d_watch dota-map [<map>] -o <file.glb> [--game FOLDER] [--source2pregledovalnik EXE] [--detail UNITS]
```

zapiše zemljevid Dota 2 kot geometrijo nivoja za pregledovalnik 3DHeat: tla,
pečine, vodo, vsako drevo in stavbe, v okvirju in enotah, v katerih so narisane
[tabele replayev Dota 2](game-dota-replays.md). Datoteko `.glb` naložite v plošči
**Ozadje / nivo** (**3D-model…**) pod tabelo Dote, in toplota herojev leži na
linijah, stolpi pa na svojih stolpih. Pregledovalnik datoteko prepozna po delih
in jo hrani v svoji knjižnici nivojev; od takrat naprej gumb **Zemljevid Dota 2**
naloži ta 3D-zemljevid namesto risbe, ki jo prikazuje OpenDota. Koda:
[`heat3d_watch/decoders/dota_map.py`](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/decoders/dota_map.py).

Potrebna je nameščena igra Dota 2 in ukazna vrstica Source2Viewer. Ničesar iz
igre ne vsebujeta orodji in ne prenašata; zemljevid pride iz vaše lastne
namestitve, datoteka, ki nastane, pa je vaša, da jo hranite, ne da jo delite -
zemljevid je last Valva.

## Kaj potrebuje {#what-it-needs}

- **Dota 2**, nameščena prek Steama. Brez `--game` se išče kot
  `steamapps\common\dota 2 beta\game\dota` v vseh Steamovih knjižnicah. `--game`
  sprejme mapo `dota 2 beta` ali njeno mapo `game\dota`.
- **ukazna vrstica Source2Viewer** (ValveResourceFormat, MIT,
  [izdaje](https://github.com/ValveResourceFormat/ValveResourceFormat/releases)):
  najprej `--source2pregledovalnik`, nato spremenljivka okolja `HEAT3D_SOURCE2VIEWER`, nato
  `Source2Viewer-CLI` / `Source2Viewer-CLI.exe` na `PATH` - enako kot pri ukazu
  `map` orodja 3DHeat CS2, zato ena kopija služi obema.
- numpy (watcher ga že potrebuje).

`<map>` je `dota` (privzeto: običajni zemljevid) ali ime drugega zemljevida v
`game\dota\maps\` ali pot do `.vpk` zemljevida.

## Kako nastane {#how-it-is-made}

1. **Mreža trkov.** Source2Viewer iz `maps/<map>.vpk` izvozi
   `maps/<map>/world_physics.vmdl_c` kot glTF. Njene skupine so poimenovane po
   površini. Skupine z imenom `clip` (nevidne stene) ali `sky` se izpustijo.
   Skupine z imenom `water`, `slime` ali `window` so **voda**: reka in ribniki
   so `water_slime`, ozki potoki skozi džunglo pa `window`; na replayu heroji
   stojijo 10 do 16 enot pod prvo in nekaj enot pod drugo. Ohranijo se samo
   njihove zgornje ploskve. Vse ostalo je teren, razdeljen ploskev za ploskvijo:
   ploskev, katere normala kaže navzgor vsaj za 0,7 (nakloni do približno 45
   stopinj), je **tla**, ostalo - pečinske ploskve, zidovi zemljevida - pa je
   **struktura**.
2. **Entitete.** Source2Viewer dekompilira entitetne bloke zemljevida
   (`maps/<map>/entities/*.vents_c`) v besedilo: bloki z glavo `====<n>====`, po
   en `ključ vrednost` na vrstico. Uporabljeta se `default_ents` in vsaka plast
   sveta (`info_world_layer`), ki je na začetku prikazana (zastavica začetka 1) -
   plasti obeh baz. Plasti, ki so na začetku skrite, držijo to, kar se pojavi, ko
   baza pade, in so izpuščene.
3. **Kaj se riše.** Drevesa (`ent_dota_tree`) in stavbe: stolpi, barake, prastari
   (`npc_dota_fort`), zapolnjevalne stavbe (`npc_dota_building`), izpostave,
   vodnjaki, svetišča modrosti, lotosovi bazeni, dvojna vrata, stražarji
   (`npc_dota_lantern`) in skladišča nevtralnih predmetov. Trgovine (trgovec je
   lik), dvorana slave, prapori, luči in delci niso vključeni.
4. **Modeli.** Vsak model, ki ga imenujejo te entitete, se izvozi iz
   `game\dota\pak01_dir.vpk` v enem zagonu Source2Viewer. Mrežice modela, ki so
   drugo stanje iste stvari - štor posekanega drevesa, bližnji posnetek, prikazan
   v inšpektorju, ruševine -, se izpustijo po imenu (`stump`, `inspector`,
   `destruction`).
5. **Stavbe** so mrežica njihovega lastnega modela, zredčena z **gručenjem
   točk**: vsaka točka se premakne na povprečje točk v kocki velikosti `--detail`
   (privzeto 8 enot, približno tretjina širine heroja), trikotniki, ki se
   sesedejo ali ponovijo, pa izginejo. 0 ohrani vse trikotnike.
6. **Drevesa** so obris vsakega modela kot nizka obrnjena telesa: njegova višina
   v petih pasovih, vsak je šesterokotni obroč, širok kot večina točk modela na
   tej višini (90. percentil njihove razdalje od osi debla), spodaj zaprt in zgoraj
   koničast - 60 trikotnikov, prava višina in širina modela. Bor postane stožec,
   hrast kroglo na deblu. Prave mrežice bi bile približno desetkrat težje pri
   nekaj več kot 2.000 drevesih.
7. **Postavljeno** tako, kot jih postavi igra: skalirano z `scales`, obrnjeno z
   `angles` (Sourceov nagib, zasuk in valjanje v stopinjah), premaknjeno na
   `origin`.
8. **V okvir pregledovalnika.** Source2Viewer zapiše glTF v metrih, z Y navzgor:
   (Y, Z, X) igre krat 0,0254. To se razveljavi, vsaka točka pa se zapiše kot
   (X, Z, -Y) igre: Y navzgor, Y igre obrnjen. Okvir je isti, v katerem so tabele
   Dote narisane prek njihovih namigov `heat3d` (`up: z`, `flipY: true`, skala 1).
   Gre za vrtenje, ne za zrcaljenje.

## Datoteka {#the-file}

Binarni glTF 2.0, kot ga ustvarja orodje 3DHeat CS2 (glejte njegovo stran o
izvozu zemljevida): po en vozlišče in ena mrežica za vsak del v korenu, brez
transformacij, ploskovno senčena (vsaka točka kota trikotnika nosi normalo
svojega trikotnika), indeksi `uint32`, brez materialov, tekstur in UV-jev,
`asset.generator` `heat3d_watch`, enote igre.

| Del | Kaj |
|---|---|
| `ground:terrain` | tla, po katerih se hodi |
| `structure:terrain` | pečinske ploskve in zidovi zemljevida |
| `water:water_slime`, `water:window` | reka in ribniki; potoki v džungli |
| `structure:tree` | vsako drevo, ki stoji na začetku |
| `structure:tower`, `structure:barracks`, `structure:ancient`, `structure:filler`, `structure:outpost`, `structure:fountain`, `structure:shrine`, `structure:lotus_pool`, `structure:twin_gate`, `structure:watcher`, `structure:neutral_stash` | stavbe, po vrsti |

Predpona `ground:` / `structure:` / `water:` pove pregledovalniku 3DHeat, kaj je
posamezen del; vsi pretvorniki nivojev 3DHeat to uporabljajo tako, kot je
zapisano. Ker so enote igre (približno palec vsaka), drug pregledovalnik
glTF prikaže zemljevid približno 39-krat prevelik; v 3DHeat leži natančno pod
tabelo.

Primer izpisa (številke so odvisne od različice zemljevida):

```text
reading dota.vpk: collision mesh and entities
reading 30 models from pak01_dir.vpk
dota.glb: dota, 700,000 triangles (230,000 ground) in 16 parts; 2,400 trees, 70 buildings
```

Prvi dve vrstici gresta v tok napak, zadnja v izhod. Model, ki ga Source2Viewer
ne najde, se izpusti in na koncu zadnje vrstice navede
(`; 1 model(s) not found, left out: ...`). Napake - Dota 2 ni najdena, zemljevid
ni najden, Source2Viewer ni najden ali ne deluje - izpišejo `dota-map: <razlog>`
in se končajo s kodo 1.

## Kako je preverjeno {#how-it-was-checked}

Na javnem replayu tekme, ki ga je watcher pretvoril (zakrpa 7.40), in na
zemljevidu nameščene igre:

- vsak vzorec položaja heroja, gledan navpično navzdol, najde tla na najvišji
  ploskvi, ki je največ 64 enot nad njegovimi nogami; srednja višina nad njimi je
  0 enot, 99,5 % pa je znotraj 16 enot; če je zemljevid zrcaljen (Y ni obrnjen),
  jih le približno polovica najde tla, ostali pa lebdijo ali potonejo za višino
  pečine;
- 22 stolpov, 12 barak, 2 prastara, 14 zapolnjevalnih stavb, 2 izpostavi, 2
  vodnjaka in 10 stražarjev, ki jih postavi tabela enot replaya, stojijo na
  entitetah zemljevida iste vrste do 0,02 enote, vodoravno in po višini;
- stopalo vsakega drevesa je na tleh.

Testi (`tests/test_dota_map.py`) preverjajo bralnik blokov, okvire, delitev
terena, obrise dreves in gručenje, postavitev ter celoten izvoz s Source2Viewer,
ki ga nadomešča nadomestek - samo na izmišljenih podatkih.

## Česa ne počne {#what-it-does-not-do}

- Brez tekstur in barv: pregledovalnik senči nivo po svoje.
- Med tekmo ni posekanih dreves in porušenih stavb: zemljevid je takšen, kot se
  začne.
- Dogodkovni in zemljevidi po meri niso preizkušeni; njihovi razredi entitet so
  lahko drugačni.
- Rekviziti, ki samo krasijo (skale, ograje, prapori), so v njem le toliko, kolikor
  so del mreže trkov.
