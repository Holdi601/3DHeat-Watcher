---
title: "Harta Dota 2"
nav_order: 6.5
lang: "ro"
source: dota-map.md
source_hash: "c9830d37ea89"
nav_exclude: true
search_exclude: true
---
# Harta Dota 2 ca nivel (`dota-map`) {#dota-2s-map-as-a-level-dota-map}

```bash
python -m heat3d_watch dota-map [<map>] -o <file.glb> [--game FOLDER] [--source2viewer EXE] [--detail UNITS]
```

scrie harta Dota 2 ca geometrie de nivel pentru vizualizatorul 3DHeat: terenul, stâncile, apa, fiecare copac și
clădirile, în sistemul de referință și în unitățile în care sunt desenate
[tabelele de replay Dota 2](game-dota-replays.md). Încărcați fișierul `.glb` în panoul **Fundal / nivel** al
vizualizatorului (**Model 3D…**), sub un tabel Dota, și căldura eroilor cade pe benzi, turnurile pe turnurile lor.
Vizualizatorul recunoaște fișierul după părțile sale și îl păstrează în biblioteca sa de nivele; de atunci, butonul
său **Harta Dota 2** încarcă această hartă 3D în loc de desenul de la OpenDota. Cod:
[`heat3d_watch/decoders/dota_map.py`](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/decoders/dota_map.py).

Sunt nevoie de Dota 2 instalat și de linia de comandă a Source2Viewer. Nimic din joc nu se află în unelte și nu este
descărcat de ele: harta vine din instalarea dumneavoastră, iar fișierul pe care îl scrie este al dumneavoastră de
păstrat, nu de împărtășit - harta este a Valve.

## Ce trebuie {#what-it-needs}

- **Dota 2**, instalat prin Steam. Fără `--game` este căutat ca `steamapps\common\dota 2 beta\game\dota` în fiecare
  bibliotecă Steam. `--game` primește dosarul `dota 2 beta` sau dosarul său `game\dota`.
- **Linia de comandă a Source2Viewer** (ValveResourceFormat, MIT,
  [versiuni](https://github.com/ValveResourceFormat/ValveResourceFormat/releases)): `--source2viewer`, apoi variabila de
  mediu `HEAT3D_SOURCE2VIEWER`, apoi `Source2Viewer-CLI` / `Source2Viewer-CLI.exe` în `PATH` - la fel ca comanda `map` a
  uneltei 3DHeat CS2, deci o singură copie servește ambele.
- numpy (deja necesar watcher-ului).

`<map>` este `dota` (implicit: harta normală) sau numele altei hărți din `game\dota\maps\`, ori calea către `.vpk`-ul
unei hărți.

## Cum se face {#how-it-is-made}

1. **Sita de coliziune.** Source2Viewer exportă `maps/<map>/world_physics.vmdl_c` al hărții din `maps/<map>.vpk` ca
   glTF. Grupurile sale sunt numite după suprafață. Grupurile numite `clip` (zidurile invizibile) sau `sky` sunt
   eliminate. Grupurile numite `water`, `slime` sau `window` sunt **apă**: râul și iazurile sunt `water_slime`, pâraiele
   înguste prin junglă sunt `window`; într-un replay, eroii stau cu 10 până la 16 unități sub primele și cu câteva
   unități sub a doua. Sunt păstrate doar fețele lor orientate în sus. Tot restul este terenul, împărțit față cu față:
   o față a cărei normală indică în sus cu cel puțin 0,7 (pante de până la aproximativ 45 de grade) este **teren**
   (`ground`), restul - fețele de stâncă, zidurile hărții - este **structură** (`structure`).
2. **Entitățile.** Source2Viewer decompilează blocurile de entități ale hărții (`maps/<map>/entities/*.vents_c`) în
   text: blocuri cu antetul `====<n>====`, câte un `key value` pe rând. Blocurile folosite sunt `default_ents` și fiecare
   strat al lumii, o entitate `info_world_layer` care apare acolo la început (indicatorul de apariție 1) - straturile
   celor două baze. Straturile care pornesc ascunse conțin ce apare când cade o bază și sunt lăsate afară.
3. **Ce se desenează.** Copacii (`ent_dota_tree`) și clădirile: turnuri, cazărmi, anticii (`npc_dota_fort`), umplutura
   (`npc_dota_building`), avanposturi, fântâni, altarele înțelepciunii, bazinele cu lotus, porțile gemene, observatoarele
   (`npc_dota_lantern`) și depozitele neutre de obiecte. Magazinele (un vânzător este un personaj), sala gloriei,
   steagurile, luminile și particulele nu sunt.
4. **Modelele.** Fiecare model numit de aceste entități este exportat din `game\dota\pak01_dir.vpk` într-o singură
   rulare Source2Viewer. Plasele unui model care sunt o altă stare a aceluiași lucru - butucul unui copac tăiat, planul
   apropiat afișat în inspector, molozul - sunt lăsate afară după nume (`stump`, `inspector`, `destruction`).
5. **Clădirile** sunt propria plasă a modelului lor, subțiată prin **gruparea vârfurilor** (vertex clustering): fiecare
   punct se mută în media punctelor din cubul său de mărime `--detail` (implicit 8 unități, aproximativ o treime din
   lățimea unui erou), iar triunghiurile care se contractă sau se repetă dispar. 0 păstrează fiecare triunghi.
6. **Copacii** sunt conturul fiecărui model, ca un corp plin, scund și rotit: înălțimea sa în cinci benzi, fiecare un
   inel cu șase laturi, cât de lat este majoritatea punctelor modelului la acea înălțime (percentila 90 a distanței lor
   față de axa trunchiului), închis jos și ascuțit sus - 60 de triunghiuri, înălțimea și lățimea reale ale modelului. Un
   pin iese un con, un stejar o minge pe un picior. Plasele reale ar cântări de aproximativ zece ori mai mult pentru
   cei peste 2.000 de copaci.
7. **Așezate** cum le așază jocul: scalate după `scales`, rotite după `angles` (tangajul, gierul și ruliul Source, în
   grade), mutate în `origin`.
8. **În sistemul vizualizatorului.** Source2Viewer scrie glTF în metri, cu Y în sus: (Y, Z, X) al jocului înmulțit cu
   0,0254. Aceasta se anulează, și fiecare punct se scrie ca (X, Z, -Y) al jocului: Y în sus, Y al jocului negat - sistemul
   în care sunt desenate tabelele Dota prin indiciile lor `heat3d` (`up: z`, `flipY: true`, scale 1). O rotație, nu o
   oglindire.

## Fișierul {#the-file}

Un binar glTF 2.0, ca cel al uneltei 3DHeat CS2 (vezi pagina sa de export a hărții): un nod și o plasă pentru fiecare
parte, în rădăcină, fără transformări, cu umbrire plată (un vârf pentru fiecare colț de triunghi, care poartă normala
triunghiului său), indici `uint32`, fără materiale, texturi sau UV, `asset.generator` `heat3d_watch`, unitățile jocului.

| Parte | Ce este |
|---|---|
| `ground:terrain` | terenul pe care se poate merge |
| `structure:terrain` | fețele de stâncă și zidurile hărții |
| `water:water_slime`, `water:window` | râul și iazurile; pâraiele din junglă |
| `structure:tree` | fiecare copac aflat în picioare la început |
| `structure:tower`, `structure:barracks`, `structure:ancient`, `structure:filler`, `structure:outpost`, `structure:fountain`, `structure:shrine`, `structure:lotus_pool`, `structure:twin_gate`, `structure:watcher`, `structure:neutral_stash` | clădirile, pe fel |

Prefixul `ground:` / `structure:` / `water:` este modul în care toți exportatorii de nivele 3DHeat îi spun
vizualizatorului ce este o parte; vizualizatorul îl crede pe cuvânt. Pentru că unitățile sunt ale jocului (aproximativ
un inch fiecare), alt vizualizator glTF arată harta de aproximativ 39 de ori mai mare; în 3DHeat ea se așază exact sub
tabel.

Ce afișează, la o rulare exemplu (cifrele depind de versiunea hărții):

```text
reading dota.vpk: collision mesh and entities
reading 30 models from pak01_dir.vpk
dota.glb: dota, 700,000 triangles (230,000 ground) in 16 parts; 2,400 trees, 70 buildings
```

Primele două rânduri merg în fluxul de erori, ultimul în ieșire. Un model pe care Source2Viewer nu l-a găsit este lăsat
afară și numit la sfârșitul ultimului rând (`; 1 model(s) not found, left out: ...`). Erorile - Dota 2 nu a fost găsit,
harta nu a fost găsită, Source2Viewer nu a fost găsit sau eșuează - afișează `dota-map: <why>` și ies cu codul 1.

## Cum a fost verificată {#how-it-was-checked}

Pe replay-ul unui meci public, convertit de watcher (patch 7.40), și pe harta jocului instalat:

- fiecare probă de poziție a unui erou, privită drept în jos, caută cea mai înaltă față de teren aflată cel mult 64 de
  unități deasupra picioarelor și găsește teren; înălțimea mediană deasupra lui este 0 unități, iar 99,5 % sunt în 16
  unități; cu harta oglindită (Y nenegat) doar aproximativ jumătate găsesc teren, iar restul plutesc sau se scufundă cu
  înălțimea unei stânci;
- cele 22 de turnuri, 12 cazărmi, 2 anticii, 14 umpluturi, 2 avanposturi, 2 fântâni și 10 observatoare pe care le
  plasează tabelul de unități al replay-ului stau pe entitățile hărții de același fel, în limita a 0,02 unități,
  orizontal și în înălțime;
- piciorul fiecărui copac este pe teren.

Testele (`tests/test_dota_map.py`) verifică cititorul de blocuri, sistemele de referință, împărțirea terenului, conturele
și gruparea copacilor, așezarea și exportul complet, cu Source2Viewer înlocuit de un substitut - doar pe date inventate.

## Ce nu face {#what-it-does-not-do}

- Fără texturi sau culori: vizualizatorul umbrește nivelul în felul său.
- Fără copaci tăiați sau clădiri distruse în timpul unui meci: harta așa cum pornește.
- Hărțile de eveniment și cele personalizate nu sunt testate; clasele lor de entități pot diferi.
- Recuzita care doar decorează (stânci, garduri, steaguri) este în hartă doar atât cât face parte din sita de coliziune.
