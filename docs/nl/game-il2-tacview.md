---
title: "IL-2 Sturmovik: Great Battles (replays)"
nav_order: 27
lang: "nl"
source: game-il2-tacview.md
source_hash: "0bb23bddee03"
nav_exclude: true
search_exclude: true
---
# IL-2 Sturmovik: Great Battles (replays) {#il-2-sturmovik-great-battles-replays}

Na een wedstrijd van IL-2 Sturmovik: Great Battles zet de watcher het replay dat het spel heeft opgeslagen om in bestanden die je op een kaart in de 3DHeat-viewer kunt bekijken.

*Technische details: adapter `il2-tacview`, soort [`replay`](sources-and-rules.md); hij draait altijd (hij wacht niet tot een spel start) en zoekt elke 5 s naar nieuwe gegevens.*

## Wat wordt opgenomen {#what-is-recorded}

- elk vliegtuig, voertuig en schip van de opname: posities één keer per seconde (meter oost/omhoog/noord vanaf het referentiepunt van de opname; lat/lon/alt als kolommen)
- spawns, vernietigingen (dood) en vertrekken (left), opstijgingen en landingen wanneer ze zijn opgenomen
- objecten, vernietigd, opstijgingen, landingen en lengte per opname
- elke regel van de opname ongewijzigd bewaard in heat.raw.parquet, op de klok van de rijen

## Waar het vandaan komt {#where-it-comes-from}

de eigen Tacview-opnamen van het spel &lt;game>\data\Tracks\\\*.acmi (ACMI 2.x-tekst, gewoon of gezipt)

## Hoe je het aanzet {#how-to-switch-it-on}

python -m heat3d_watch setup il2-tacview --apply (tacviewrecord = 1 in [KEY = track_record])

Typ de opdracht in een terminal die geopend is in de map van de watcher (zie [Voordat je begint](before-you-start.md)). Als het mislukt, zegt de laatste regel waarom; [Installeren en uitvoeren](installing-and-running.md) beschrijft de gebruikelijke oorzaken.

`python -m heat3d_watch setup il2-tacview` toont welke bestanden het zou wijzigen; `python -m heat3d_watch setup il2-tacview --apply` wijzigt ze en bewaart het origineel als `<file>.heat3d-backup` (zie [Opdrachten](commands.md#setup)). Het schrijft `il2-tacview: changed: ...` voor elke wijziging, of `il2-tacview: nothing to change` wanneer het al aanstaat.

## Hoe het werkt {#how-it-works}

IL-2 Sturmovik: Great Battles - de telemetrie-uitvoer van het spel via UDP, en de eigen Tacview-opnamen.

1. Telemetrie ("Telemetry output of IL2 v4.003", revisie 1.2, meegeleverd als
   `<game>\Doc\UDP_Output\Il2_TeleOutput.pdf`). Aangezet in
   `<game>\data\startup.cfg`, sectie `[KEY = telemetrydevice]`: `addr`,
   `addr1`, ... = "IP[:poort]" (meerdere doelen tegelijk), `decimation` (50 Hz /
   n), `enable`, `port`. `setup` voegt één doel toe, 127.0.0.1:41995 (JoyPro gebruikt
   41994, de standaardpoort van het spel is 4322), en zet de uitvoer aan. Pakketten,
   little-endian:

   ```text
   DWORD  Packet_ID 0x54000101
   WORD   Size
   DWORD  Tick (1/50 s)
   BYTE   Indicators_Count, then SIndicator {WORD id, BYTE n, n x 32-bit float}
   BYTE   Events_Count,     then SEvent     {WORD id, BYTE size, size bytes}
   ```

   Indicators: 0 ENG_RPM, 1 ENG_MP, 2/3 engine shake, 4 LGEARS_STATE, 5
   LGEARS_PRESS, 6 EAS (m/s), 7 AOA (rad), 8 ACCELERATION (xyz incl. gravity),
   9 COCKPIT_SHAKE, 10 AGL (m), 11 FLAPS, 12 AIR_BRAKES, 13 AOS (rad), 14
   VERTICAL_SPEED (m/s). Events (2-byte packed): 0 SET_FOCUS (STRING: length
   byte + ASCII), 1 SETUP_ENG {short index, short id, float pos[3], float
   max_rpm}, 2 SETUP_GUN {short index, float pos[3], float projectile mass,
   float muzzle velocity}, 3 SETUP_LGEAR {short index, short id, float
   pos[3]}, 4 DROP_BOMB and 5 ROCKET_LAUNCH
   {float pos[3], float mass, WORD flags}, 6 HIT and 7 DAMAGE {float pos[3],
   float force[3]}, 8 EXPLOSION {float pos[3], float radius}, 9 GUN_FIRE {BYTE
   gun}, 10 SRV_ADDR, 11 SRV_TITLE, 12 SRS_ADDR (STRING), 13 CLIENT_DAT {long
   client, long server client, char name[32]}, 14 CTRL_DAT {long parent, short
   coalition}. Event-posities zijn lokaal ten opzichte van het vliegtuig van de speler; de stroom
   heeft helemaal geen positie in de wereld - dit zijn dus gebeurtenissen en getallen, geen spoor.

2. Tacview-opname: `tacviewrecord = 1` in `[KEY = track_record]` laat het spel
   `<game>\data\Tracks\*.acmi` schrijven (in multiplayer beslist de server).
   Een afgerond bestand wordt omgezet: elk vliegtuig, voertuig en schip met zijn
   posities, spawn en verwijdering (vernietigd of weg), opstijgingen en landingen wanneer
   de opname ze heeft. ACMI 2.x-tekstformaat, gewoon of gezipt, volgens
   <https://www.tacview.net/documentation/acmi/en/> - regels "#t" zetten de klok vooruit,
   regels "id,Key=Value,..." zetten eigenschappen (hex-id's, komma's ge-escaped "\\,", een
   slot "\\" zet de regel voort), "-id" verwijdert een object, object 0 draagt de
   globals (ReferenceLongitude/Latitude, RecordingTime, ...) en de gebeurtenissen
   ("Event=Destroyed\|id\|text"). T = Lon\|Lat\|Alt[\|U\|V] of
   Lon\|Lat\|Alt\|Roll\|Pitch\|Yaw[\|U\|V\|Heading], lengte- en breedtegraad ten opzichte van
   de referentie, lege velden ongewijzigd. Posities gaan in een vlakke kaart rond
   het referentiepunt: x oost, y hoogte, z noord, meter. Het referentiepunt is de `geo`
   van de sessie, opgeslagen in meta.json en in de footer van de tabel, zodat de
   viewer de echte wereld onder de sporen kan leggen.

De module werkt ook voor: [IL-2 Sturmovik: Great Battles (livegegevens)](game-il2.md).

## Posities en assen {#positions-and-axes}

| | |
|---|---|
| Posities opgenomen | ja |
| Omhoog-as | `y` |
| Eenheden | meter (oost, hoogte, noord vanaf het eerste vaste punt) |
| Gespiegeld voor de viewer | `z` |
| Eenheidsschaal (`scale`: de viewer vermenigvuldigt posities hiermee) | 1 |

Deze gaan in de `meta.json` van elke sessie (`axes`) en, wanneer de sessie posities heeft, in de footer van `heat.parquet`, zodat de 3DHeat-viewer de rijen zelf draait en schaalt - zie [De data](the-data.md).

## Multiplayer {#multiplayer}

- Als online gespeeld gemarkeerd (`multiplayer`): **ja**. `games --markdown` toont dit als "allowed (reads only what the game publishes)".
- Soort `replay`: hij leest alleen wat het spel of platform uitgeeft (replays en demo's die het spel opslaat), dus hij neemt ook op bij online spel, net als offline; de vlag bepaalt alleen of geheugen ooit gelezen mag worden.
- Geheugen: **nooit** gelezen door deze adapter. Alleen `memory`-adapters lezen geheugen, en nooit voor een spel dat als online gespeeld is gemarkeerd - zie [Bronnen en regels](sources-and-rules.md).

## Opgenomen statistieken {#statistics-recorded}

Statistiekensleutels die de code van deze adapter bij naam instelt (de `stats` van elke sessie in `meta.json` en de tabel `stats` in `watcher.sqlite`):

`destroyed`, `duration_s`, `objects`, `{r.event}s`

Een sleutel tussen accolades wordt tijdens het draaien ingevuld (`score.{team}` is één sleutel per team). Sleutels die de code uit een tabel met velden van het spel of uit de eigen statistiekennamen van het spel haalt, staan niet in deze lijst; "Wat wordt opgenomen" hierboven noemt ze.

## Volledigheid {#completeness}

De watcher volgt de [converterregel](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md) van 3DHeat: wat de bron bevat wordt gelezen of bewaard, nooit weggelaten. Naast de rijen wordt elk pakket, elke pagina, regel of antwoord die de adapter ontvangt ongewijzigd bewaard in de `heat.raw.parquet` van de sessie (kolommen `time`, `ms`, `type`, `used`, `payload`, `text`, plus elk veld dat op naam is bewaard; `used` markeert wat ook rijen is geworden), en `selfCheck.completeness` in `meta.json` telt elk `type` - `lost` is 0.

**Gelezen**

- de T van elk object (lengtegraad, breedtegraad, hoogte, roll, pitch, yaw, U, V, koers) als posities één keer per seconde per object, met Name, Type, Pilot, Coalition/Color, Country, Group en Parent
- spawns, verwijderingen (dood als een Destroyed-gebeurtenis eerder kwam, anders weg), TakenOff- en Landed-gebeurtenissen, Message- en Bookmark-gebeurtenissen als rijen
- de globals ReferenceLongitude/Latitude (de oorsprong van de kaart), RecordingTime/ReferenceTime (wanneer), DataSource, DataRecorder en Title in meta.json

**Ongewijzigd bewaard**

- elke niet-lege logische regel geheel als `text` (een regel die met een "\\" aan het eind wordt voortgezet, wordt samengevoegd, zoals ACMI hem leest), onder zijn soort: `header` (FileType, FileVersion), `comment`, `time` (#t), `remove` (-id), `global` en `event` (object 0), `object` (id,Key=Value,...)
- wat alleen het ruwe bijbestand bevat: de posities tussen de rijen van één keer per seconde, wapens, granaten, flares, chaff en andere objecten die niet als spoor zijn getekend, elke andere eigenschap (telemetrie zoals IAS, AOA, gas, brandstof waar de opname die heeft), andere globals (Comments, Briefing, Author, Category), gebeurtenissen die niet zijn gelezen (Timeout, LeftArea, ...)

**Niet beschikbaar**

- niets wat de opname bevat; wat het spel niet in zijn opnamen schrijft, staat er ook niet in

**Grootte**: ongeveer de eigen tekst van de opname plus ongeveer 70 bytes per regel, vóór zstd: een opname van 100 MB wordt ongeveer 150-250 MB ruw, wat zstd bijna tot de grootte van de gezipte opname terugbrengt

## Geverifieerd {#verified}

getest op gesimuleerde ACMI 2.2-bestanden (tekst en gezipt); nog niet getest op een opname van het spel

## Bron {#source}

[heat3d_watch/adapters/il2.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/il2.py)

<!-- Generated from the adapter by tools/gen_game_pages.py; change the adapter and run it again rather than editing this page. -->
