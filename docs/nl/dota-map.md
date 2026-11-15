---
title: "Dota 2-kaart"
nav_order: 6.5
lang: "nl"
source: dota-map.md
source_hash: "c9830d37ea89"
nav_exclude: true
search_exclude: true
---
# De Dota 2-kaart als level (`dota-map`) {#dota-2s-map-as-a-level-dota-map}

```bash
python -m heat3d_watch dota-map [<map>] -o <file.glb> [--game FOLDER] [--source2viewer EXE] [--detail UNITS]
```

schrijft de Dota 2-kaart als levelgeometrie voor de 3DHeat-viewer: de grond, de
kliffen, het water, elke boom en de gebouwen, in het coördinatenstelsel en de eenheden waarin
de [Dota 2-replaytabellen](game-dota-replays.md) worden getekend. Laad de `.glb`
in het paneel **Achtergrond / level** van de viewer (**3D-model…**) onder een
Dota-tabel, en de hitte van de helden ligt op de lanes, de torens op hun torens.
De viewer herkent het bestand aan zijn onderdelen en houdt het in zijn
levelbibliotheek; vanaf dan laadt de knop **Dota 2-kaart** van de viewer deze
3D-kaart in plaats van OpenDota's tekening. Code:
[`heat3d_watch/decoders/dota_map.py`](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/decoders/dota_map.py).

Het heeft Dota 2 nodig, geïnstalleerd via Steam, en de opdrachtregel van
Source2Viewer. Niets van het spel zit in de tools of wordt door hen gedownload:
de kaart komt uit je eigen installatie, en het bestand dat het schrijft is van
jou om te bewaren, niet om te delen - de kaart is van Valve.

## Wat er nodig is {#what-it-needs}

- **Dota 2**, geïnstalleerd via Steam. Zonder `--game` wordt het gezocht als
  `steamapps\common\dota 2 beta\game\dota` in elke Steam-bibliotheek. `--game`
  neemt de map `dota 2 beta` of de map `game\dota` ervan.
- **De opdrachtregel van Source2Viewer** (ValveResourceFormat, MIT,
  [releases](https://github.com/ValveResourceFormat/ValveResourceFormat/releases)):
  `--source2viewer`, dan de omgevingsvariabele `HEAT3D_SOURCE2VIEWER`, dan
  `Source2Viewer-CLI` / `Source2Viewer-CLI.exe` op `PATH` - hetzelfde als het
  `map`-commando van de 3DHeat CS2-tool, zodat één kopie voor beide dient.
- numpy (heeft de watcher al nodig).

`<map>` is `dota` (de standaard: de normale kaart) of de naam van een andere kaart in
`game\dota\maps\`, of het pad naar de `.vpk` van een kaart.

## Hoe het gemaakt wordt {#how-it-is-made}

1. **Het botsingsmesh.** Source2Viewer exporteert de `maps/<map>/world_physics.vmdl_c`
   van de kaart uit `maps/<map>.vpk` als glTF. De groepen heten naar hun oppervlak.
   Groepen die `clip` (de onzichtbare muren) of `sky` heten vallen weg. Groepen die
   `water`, `slime` of `window` heten zijn **water**: de rivier en de vijvers zijn
   `water_slime`, de smalle stroompjes door de jungle zijn `window`; in een replay
   staan helden 10 tot 16 eenheden onder de eerste en een paar eenheden onder de
   tweede. Alleen hun opwaartse vlakken blijven. Al het andere is het terrein, vlak
   voor vlak verdeeld: een vlak waarvan de normaal minstens 0,7 omhoog wijst (hellingen
   tot ongeveer 45 graden) is **grond**, de rest - kliffenvlakken, de muren van de
   kaart - is **structuur**.
2. **De entiteiten.** Source2Viewer decompileert de entiteitsblokken van de kaart
   (`maps/<map>/entities/*.vents_c`) naar tekst: blokken met kop `====<n>====`, één
   `key value` per regel. De gebruikte blokken zijn `default_ents` en elke wereldlaag
   die een `info_world_layer`-entiteit daar aan het begin toont (spawn-vlag 1) - de
   lagen van de twee basissen. De lagen die verborgen beginnen bevatten wat verschijnt
   als een basis valt en worden weggelaten.
3. **Wat getekend wordt.** Bomen (`ent_dota_tree`) en de gebouwen: torens, barracks,
   de ancients (`npc_dota_fort`), de vulgebouwen (`npc_dota_building`), buitenposten,
   fonteinen, de wijsheidsschrijnen, lotusvijvers, tweelingpoorten, wachters
   (`npc_dota_lantern`) en neutrale item-opslagplaatsen. Winkels (een winkelier is een
   personage), de hall of fame, banners, lichten en partikels niet.
4. **De modellen.** Elk model dat deze entiteiten noemen wordt in één Source2Viewer-run
   geëxporteerd uit `game\dota\pak01_dir.vpk`. De meshes van een model die een andere
   staat van hetzelfde zijn - de stomp van een gekapte boom, de close-up in de
   inspector, puin - worden op naam weggelaten (`stump`, `inspector`, `destruction`).
5. **Gebouwen** zijn hun eigen model-mesh, uitgedund door **vertex-clustering**: elk
   punt verschuift naar het gemiddelde van de punten in zijn kubus van `--detail`
   eenheden (standaard 8 eenheden, ongeveer een derde van de breedte van een held),
   en driehoeken die ineenvallen of dubbel zijn verdwijnen. 0 houdt elke driehoek.
6. **Bomen** zijn de contour van elk model als een laag gedraaid lichaam: zijn hoogte
   in vijf banden, elk een zeszijdige ring zo breed als het grootste deel van de punten
   van het model op die hoogte (het 90e percentiel van hun afstand tot de as van de
   stam), aan de onderkant gesloten en aan de bovenkant puntig - 60 driehoeken, de
   echte hoogte en breedte van het model. Een den wordt een kegel, een eik een bol op
   een stam. De echte meshes zouden ruim tien keer zoveel wegen over ruim 2.000 bomen.
7. **Geplaatst** zoals het spel ze plaatst: geschaald door `scales`, gedraaid door
   `angles` (Source's pitch, yaw, roll in graden), verplaatst naar `origin`.
8. **In het coördinatenstelsel van de viewer.** Source2Viewer schrijft glTF in meters, Y omhoog:
   de (Y, Z, X) van het spel maal 0,0254. Dat wordt ongedaan gemaakt, en elk punt
   wordt geschreven als (X, Z, -Y) van het spel: Y omhoog, de Y van het spel omgekeerd
   - het coördinatenstelsel waarin de Dota-tabellen worden getekend, via hun `heat3d`-hints
   (`up: z`, `flipY: true`, schaal 1). Een rotatie, geen spiegeling.

## Het bestand {#the-file}

Een glTF 2.0 binary zoals die van de 3DHeat CS2-tool (zie zijn pagina over de
kaartexport): één node en één mesh per onderdeel aan de wortel, geen transformaties,
flat-shaded (een vertex per hoek van een driehoek, met de normaal van die driehoek),
`uint32`-indices, geen materialen, texturen of UV's, `asset.generator` `heat3d_watch`,
eenheden van het spel.

| Onderdeel | Wat |
|---|---|
| `ground:terrain` | het begaanbare terrein |
| `structure:terrain` | kliffenvlakken en de muren van de kaart |
| `water:water_slime`, `water:window` | de rivier en de vijvers; de stroompjes in de jungle |
| `structure:tree` | elke boom die aan het begin staat |
| `structure:tower`, `structure:barracks`, `structure:ancient`, `structure:filler`, `structure:outpost`, `structure:fountain`, `structure:shrine`, `structure:lotus_pool`, `structure:twin_gate`, `structure:watcher`, `structure:neutral_stash` | de gebouwen, per soort |

Het voorvoegsel `ground:` / `structure:` / `water:` is hoe alle 3DHeat-level-exporters
de viewer vertellen wat een onderdeel is; de viewer neemt ze op hun woord. Omdat de
eenheden die van het spel zijn (ongeveer een inch elk), toont een andere glTF-viewer
de kaart ongeveer 39 keer te groot; in 3DHeat ligt hij precies onder de tabel.

Wat het afdrukt, bij een voorbeeldrun (de getallen hangen af van de versie van de kaart):

```text
reading dota.vpk: collision mesh and entities
reading 30 models from pak01_dir.vpk
dota.glb: dota, 700,000 triangles (230,000 ground) in 16 parts; 2,400 trees, 70 buildings
```

De eerste twee regels gaan naar de foutstroom, de laatste naar de uitvoer. Een model
dat Source2Viewer niet kon vinden wordt weggelaten en aan het eind van de laatste
regel genoemd (`; 1 model(s) not found, left out: ...`). Fouten - Dota 2 niet
gevonden, de kaart niet gevonden, Source2Viewer niet gevonden of mislukt - tonen
`dota-map: <why>` en eindigen met afsluitcode 1.

## Hoe het gecontroleerd is {#how-it-was-checked}

Op een openbare wedstrijd-replay die de watcher omzette (patch 7.40) en de kaart van
het geïnstalleerde spel:

- elk positiemonster van een held, recht naar beneden gekeken naar het hoogste grondvlak
  tot 64 eenheden boven zijn voeten, vindt grond; de mediane hoogte erboven is 0
  eenheden, en 99,5 % ligt binnen 16 eenheden. Met de kaart gespiegeld (Y niet
  omgekeerd) vindt maar ongeveer de helft grond, en zweeft of zakt de rest met de
  hoogte van een klif;
- de 22 torens, 12 barracks, 2 ancients, 14 vulgebouwen, 2 buitenposten, 2 fonteinen en
  10 wachters die de unit-tabel van de replay plaatst, staan op de entiteiten van de
  kaart van dezelfde soort, tot op 0,02 eenheden, horizontaal en in hoogte;
- de voet van elke boom staat op de grond.

De tests (`tests/test_dota_map.py`) controleren de blokkenlezer, de frames, de
terreinverdeling, de boomcontouren en de clustering, de plaatsing, en de hele export
met Source2Viewer, nagebootst door een vervanger - alleen op verzonnen data.

## Wat het niet doet {#what-it-does-not-do}

- Geen texturen of kleuren: de viewer schaduwt het level op zijn eigen manier.
- Geen bomen gekapt en geen gebouwen vernield tijdens een wedstrijd: de kaart zoals hij begint.
- Event- en eigen kaarten zijn niet getest; hun entiteitsklassen kunnen anders zijn.
- De props die alleen versieren (rotsen, hekken, banners) zitten erin alleen voor zover
  ze deel uitmaken van het botsingsmesh.
