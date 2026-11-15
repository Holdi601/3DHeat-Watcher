---
title: "IL-2 Sturmovik: Great Battles (livegegevens)"
nav_order: 26
lang: "nl"
source: game-il2.md
source_hash: "b6c4de7dcc14"
nav_exclude: true
search_exclude: true
---
# IL-2 Sturmovik: Great Battles (livegegevens) {#il-2-sturmovik-great-battles-live-data}

Terwijl je IL-2 Sturmovik: Great Battles speelt, slaat de watcher de gegevens op die het spel zelf uitstuurt, zodat je ze later kunt bekijken als statistieken en een tijdlijn.

*Technische details: adapter `il2`, soort [`telemetry`](sources-and-rules.md); hij draait zolang `Il-2.exe` of `IL2Series.exe` loopt en zoekt elke 0,1 s naar nieuwe gegevens.*

## Wat wordt opgenomen {#what-is-recorded}

- vluchten: het vliegtuig dat je neemt (spawn) en het moment waarop de uitvoer stopt (session_end) - geen positie in de wereld: het spel stuurt er geen
- bommen en raketten die zijn losgelaten (massa), treffers en ontvangen schade, explosies, salvo's kanonvuur - posities lokaal ten opzichte van het vliegtuig
- equivalente luchtsnelheid, AGL, verticale snelheid, g, motortoerental één keer per seconde, met elke andere indicator die het pakket bevat (spruitstukdruk, motortrillingen, stand van het landingsgestel en de druk daarop, AoA, zijslip, versnelling x/y/z, cockpittrillingen, kleppen, luchtremmen)
- vluchten, verschoten munitie, raketten, bommen, treffers ontvangen, hoogste snelheid, hoogste g, vliegtijd; servernaam en piloot online
- elk telemetriepakket geheel bewaard in heat.raw.parquet

## Waar het vandaan komt {#where-it-comes-from}

de telemetrie-uitvoer van het spel via UDP naar 127.0.0.1:41995 ([KEY = telemetrydevice] in &lt;game>\data\startup.cfg)

## Hoe je het aanzet {#how-to-switch-it-on}

python -m heat3d_watch setup il2 --apply (voegt addrN = "127.0.0.1:41995" toe, enable = true), start IL-2 opnieuw

Typ de opdracht in een terminal die geopend is in de map van de watcher (zie [Voordat je begint](before-you-start.md)). Als het mislukt, zegt de laatste regel waarom; [Installeren en uitvoeren](installing-and-running.md) beschrijft de gebruikelijke oorzaken.

`python -m heat3d_watch setup il2` toont welke bestanden het zou wijzigen; `python -m heat3d_watch setup il2 --apply` wijzigt ze en bewaart het origineel als `<file>.heat3d-backup` (zie [Opdrachten](commands.md#setup)). Het schrijft `il2: changed: ...` voor elke wijziging, of `il2: nothing to change` wanneer het al aanstaat.

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

De module werkt ook voor: [IL-2 Sturmovik: Great Battles (replays)](game-il2-tacview.md).

## Posities en assen {#positions-and-axes}

| | |
|---|---|
| Posities opgenomen | nee |
| Omhoog-as | `y` |
| Eenheden | geen: de telemetrie heeft geen posities in de wereld |
| Gespiegeld voor de viewer | geen |
| Eenheidsschaal (`scale`: de viewer vermenigvuldigt posities hiermee) | 1 |

Deze gaan in de `meta.json` van elke sessie (`axes`) en, wanneer de sessie posities heeft, in de footer van `heat.parquet`, zodat de 3DHeat-viewer de rijen zelf draait en schaalt - zie [De data](the-data.md).

## Multiplayer {#multiplayer}

- Als online gespeeld gemarkeerd (`multiplayer`): **ja**. `games --markdown` toont dit als "allowed (reads only what the game publishes)".
- Soort `telemetry`: hij leest alleen wat het spel of platform uitgeeft (een UDP-poort of gedeeld geheugen dat het spel publiceert), dus hij neemt ook op bij online spel, net als offline; de vlag bepaalt alleen of geheugen ooit gelezen mag worden.
- Geheugen: **nooit** gelezen door deze adapter. Alleen `memory`-adapters lezen geheugen, en nooit voor een spel dat als online gespeeld is gemarkeerd - zie [Bronnen en regels](sources-and-rules.md).

## Opgenomen statistieken {#statistics-recorded}

Statistiekensleutels die de code van deze adapter bij naam instelt (de `stats` van elke sessie in `meta.json` en de tabel `stats` in `watcher.sqlite`):

`bad_packets`, `bombs_dropped`, `damage_taken`, `explosions`, `flight_time`, `hits_taken`, `max_agl_m`, `max_eas_kmh`, `max_g`, `ordnance_kg`, `rockets_fired`, `rounds_fired`, `sorties`

Een sleutel tussen accolades wordt tijdens het draaien ingevuld (`score.{team}` is één sleutel per team). Sleutels die de code uit een tabel met velden van het spel of uit de eigen statistiekennamen van het spel haalt, staan niet in deze lijst; "Wat wordt opgenomen" hierboven noemt ze.

## Volledigheid {#completeness}

De watcher volgt de [converterregel](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md) van 3DHeat: wat de bron bevat wordt gelezen of bewaard, nooit weggelaten. Naast de rijen wordt elk pakket, elke pagina, regel of antwoord die de adapter ontvangt ongewijzigd bewaard in de `heat.raw.parquet` van de sessie (kolommen `time`, `ms`, `type`, `used`, `payload`, `text`, plus elk veld dat op naam is bewaard; `used` markeert wat ook rijen is geworden), en `selfCheck.completeness` in `meta.json` telt elk `type` - `lost` is 0.

**Gelezen**

- SET_FOCUS (het vliegtuig dat je neemt: een vlucht), DROP_BOMB en ROCKET_LAUNCH (massa, lokale positie), HIT en DAMAGE (lokale positie, kracht), EXPLOSION (lokale positie, straal), GUN_FIRE (schoten per peiling) als rijen
- SETUP_ENG (index, id, lokale positie, maximumtoerental), SETUP_GUN (index, lokale positie, massa van het projectiel, mondingssnelheid) en SETUP_LGEAR (index, id, lokale positie) als rijen: de motoren, kanonnen en landingsgestelpoten van het vliegtuig bij het begin van de vlucht
- SRV_TITLE, SRV_ADDR, SRS_ADDR en CLIENT_DAT (naam van de piloot) in meta.json; de coalitie van CTRL_DAT als het team van de vlucht
- alle vijftien indicatoren van de specificatie op de `state`-rij die één keer per seconde komt (één waarde als getal, één per motor, poot van het landingsgestel of as als lijst); hoogste snelheid, g en AGL uit elk pakket

**Ongewijzigd bewaard**

- elk datagram geheel als `payload`, onder zijn Packet_ID: `0x54000101` voor telemetrie (gebruikt wanneer het een rij of een meta.json-regel maakte), elk ander id als zichzelf, een datagram dat te kort is voor één id als `short`
- wat alleen het ruwe bijbestand bevat: de indicatoren tussen de rijen van één keer per seconde (het spel stuurt ze op 50 Hz / decimation), een SETUP-gebeurtenis die korter is dan de indeling van de specificatie, gebeurtenis-id's die de specificatie niet noemt

**Niet beschikbaar**

- een positie in de wereld: de telemetrie-uitvoer heeft er geen (event-posities zijn lokaal ten opzichte van het vliegtuig); de adapter il2-tacview leest posities uit de eigen Tacview-opnamen van het spel
- andere vliegtuigen en spelers: de uitvoer beschrijft alleen het eigen vliegtuig van de speler

**Grootte**: ongeveer 8 MB per uur bij 10 Hz van de setup (decimation 5; een pakket is ongeveer 160 bytes plus zijn frame), 40 MB bij de volle 50 Hz van het spel, vóór zstd; zstd krimpt de repetitieve floats tot een deel ervan

## Geverifieerd {#verified}

getest op pakketten gebouwd uit de eigen Il2_TeleOutput-specificatie van het spel (rev 1.2); wijzigingen in startup.cfg getest op een kopie van het bestand; nog niet getest tegen het draaiende spel

## Bron {#source}

[heat3d_watch/adapters/il2.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/il2.py)

<!-- Generated from the adapter by tools/gen_game_pages.py; change the adapter and run it again rather than editing this page. -->
