---
title: "iRacing (livegegevens)"
nav_order: 28
lang: "nl"
source: game-iracing.md
source_hash: "894d9bc4081f"
nav_exclude: true
search_exclude: true
---
# iRacing (livegegevens) {#iracing-live-data}

Terwijl je iRacing speelt, slaat de watcher de gegevens op die het spel zelf uitstuurt, zodat je ze later kunt bekijken als statistieken en een tijdlijn.

*Technische details: adapter `iracing`, soort [`telemetry`](sources-and-rules.md); hij draait zolang `iRacingSim64DX11.exe` of `iRacingSim64.exe` loopt en zoekt elke 0,1 s naar nieuwe gegevens.*

## Wat wordt opgenomen {#what-is-recorded}

- het rijden 5 keer per seconde zonder positie (iRacing geeft er live geen): snelheid, versnelling, gas, rem, ronde, aandeel van de ronde, race- en klasse-positie, incidenten
- start van de sessie, in- en uitstappen, de pitstraat in en uit, ronden met rondetijd, incidenten met hun punten, de geblokte vlag, finish
- de .ibt-telemetriebestanden die tijdens de sessie zijn geschreven (breedtegraad, lengtegraad, hoogte - de viewer leest ze)
- ronden, beste ronde, incidenten, race-positie, pitstops, afstand, topsnelheid
- het volledige gedeelde geheugen in `heat.raw.parquet`: header, variabele-headers, sessie-info, elke gelezen telemetrieregel

## Waar het vandaan komt {#where-it-comes-from}

gedeeld geheugen Local\IRSDKMemMapFileName (de iRacing SDK); .ibt-bestanden in %USERPROFILE%\Documents\iRacing\telemetry

## Hoe je het aanzet {#how-to-switch-it-on}

Niets voor de livegegevens. Voor posities: log de telemetrie in de auto (Alt+L) of zet irsdkLog=1 in app.ini

## Hoe het werkt {#how-it-works}

iRacing, live: het gedeelde geheugen van de iRacing SDK, native gelezen.

iRacing publiceert zijn telemetrie voor apps in een benoemde bestandstoewijzing,
`Local\IRSDKMemMapFileName`, die de simulator aanmaakt terwijl hij draait (en bij elke
update het signaal `Local\IRSDKDataValidEvent` geeft, dat hier niet nodig is: de
watcher kijkt tien keer per seconde). De indeling is die van `irsdk_defines.h` uit de SDK,
ook gevolgd door pyirsdk (MIT) - hier opnieuw geschreven uit die feiten:

```text
irsdk_header (little-endian int32s)
    0 ver, 4 status (bit 0: connected), 8 tickRate,
    12 sessionInfoUpdate, 16 sessionInfoLen, 20 sessionInfoOffset,
    24 numVars, 28 varHeaderOffset, 32 numBuf, 36 bufLen, 40 pad[2],
    48 varBuf[4]: { tickCount, bufOffset, pad[2] } (16 bytes each)
irsdk_varHeader (144 bytes, numVars of them at varHeaderOffset)
    0 type (0 char, 1 bool, 2 int, 3 bitfield, 4 float, 5 double),
    4 offset (into a line), 8 count, 12 countAsTime + 3 pad,
    16 name[32], 48 desc[64], 112 unit[32]
session info: YAML text at sessionInfoOffset, rewritten when
    sessionInfoUpdate changes (track, sessions, drivers)
```

De simulator schrijft `numBuf` regels om en om; de nieuwste is die met de hoogste
tickCount, en een regel wordt opnieuw genomen als zijn tickCount is veranderd terwijl hij
werd gekopieerd.

Live data heeft geen positie in de wereld - breedtegraad, lengtegraad en hoogte staan
alleen in de `.ibt`-bestanden die iRacing logt in `Documents\iRacing\telemetry` (Alt+L in de
auto, of `irsdkLog=1`), die de 3DHeat-viewer zelf leest. Daarom legt dit het rijden vast als
gebeurtenissen zonder coördinaten - snelheid, ronde, het aandeel van de ronde dat af is,
race-positie, incidenten - plus ronden, incidenten, pitstops en de geblokte vlag, en aan het
eind de `.ibt`-bestanden die tijdens de sessie zijn geschreven als `telemetry_file`-gebeurtenissen,
zodat de viewer ze kan openen.

Naast de rijen wordt het hele geheugenoverzicht bewaard, in het ruwe bijbestand van de sessie
(`heat.raw.parquet`): het vaste deel van de header (`header`, telkens als het verandert), de
variabele-headers (`var_headers`, geheel, en als JSON in `text`, telkens als de indeling
verandert), de YAML van de sessie-info (`session_info`, zijn tekst telkens als
`sessionInfoUpdate` verschuift) en de nieuwste telemetrieregel (`telemetry`, elke variabele
ervan, bij elke leesbeurt die een nieuwe tick vindt). De variabele-headers en een regel
zijn alles wat een latere decoder nodig heeft om elke variabele te lezen.

Bron: de iRacing SDK (irsdk_defines.h, documentatie in het iRacing SDK-forum);
kutu/pyirsdk (MIT) ter bevestiging van de offsets.

## Posities en assen {#positions-and-axes}

| | |
|---|---|
| Posities opgenomen | nee |
| Omhoog-as | `y` |
| Eenheden | geen posities live; de .ibt-bestanden bevatten breedtegraad/lengtegraad/hoogte |
| Gespiegeld voor de viewer | geen |
| Eenheidsschaal (`scale`: de viewer vermenigvuldigt posities hiermee) | 1 |

Deze gaan in de `meta.json` van elke sessie (`axes`) en, wanneer de sessie posities heeft, in de footer van `heat.parquet`, zodat de 3DHeat-viewer de rijen zelf draait en schaalt - zie [De data](the-data.md).

## Multiplayer {#multiplayer}

- Als online gespeeld gemarkeerd (`multiplayer`): **ja**. `games --markdown` toont dit als "allowed (reads only what the game publishes)".
- Soort `telemetry`: hij leest alleen wat het spel of platform uitgeeft (een UDP-poort of gedeeld geheugen dat het spel publiceert), dus hij neemt ook op bij online spel, net als offline; de vlag bepaalt alleen of geheugen ooit gelezen mag worden.
- Geheugen: **nooit** gelezen door deze adapter. Alleen `memory`-adapters lezen geheugen, en nooit voor een spel dat als online gespeeld is gemarkeerd - zie [Bronnen en regels](sources-and-rules.md).

## Opgenomen statistieken {#statistics-recorded}

Statistiekensleutels die de code van deze adapter bij naam instelt (de `stats` van elke sessie in `meta.json` en de tabel `stats` in `watcher.sqlite`):

`best_lap`, `distance_km`, `finishes`, `incidents`, `laps`, `pit_stops`, `race_position`, `sessions`, `top_speed_kmh`

Een sleutel tussen accolades wordt tijdens het draaien ingevuld (`score.{team}` is één sleutel per team). Sleutels die de code uit een tabel met velden van het spel of uit de eigen statistiekennamen van het spel haalt, staan niet in deze lijst; "Wat wordt opgenomen" hierboven noemt ze.

## Volledigheid {#completeness}

De watcher volgt de [converterregel](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md) van 3DHeat: wat de bron bevat wordt gelezen of bewaard, nooit weggelaten. Naast de rijen wordt elk pakket, elke pagina, regel of antwoord die de adapter ontvangt ongewijzigd bewaard in de `heat.raw.parquet` van de sessie (kolommen `time`, `ms`, `type`, `used`, `payload`, `text`, plus elk veld dat op naam is bewaard; `used` markeert wat ook rijen is geworden), en `selfCheck.completeness` in `meta.json` telt elk `type` - `lost` is 0.

**Gelezen**

- uit de nieuwste telemetrieregel: sessietijd, nummer, status en id, op de baan, replay, ronde, voltooide ronden, aandeel en meters van de ronde, laatste en beste ronde, snelheid, versnelling, gas, rem, toerental, pitweg, baanoppervlak, race- en klasse-positie, het eigen aantal incidenten (de `driving`-rijen van 5 Hz en de gebeurtenissen)
- nu ook op de `driving`-rijen: `steering_angle`, `yaw`, `yaw_north`, `pitch`, `roll` (graden, uit de radialen van de simulator - alleen wanneer de variabele-header de eenheid als rad geeft), `fuel_l` (eenheid l), `lat_accel` en `lon_accel` (eenheid m/s^2)
- uit de YAML van de sessie-info: de autoindex van de speler, baan en configuratie, sessietypes, de naam, auto, team en nummer van elke coureur (rijen session_start, meta.json)
- gecontroleerd tegen een blok dat in de tests uit irsdk_defines.h is opgebouwd; nog niet tegen de simulator zelf

**Ongewijzigd bewaard**

- `telemetry`: de nieuwste regel geheel, elke variabele die de simulator publiceert (de CarIdx-arrays van elke auto, banden, ophanging, de snelle `_ST`-arrays waar de simulator ze heeft ...), bij elke leesbeurt die een nieuwe tick vindt; `tick` het tikaantal van de simulator; `used` is onwaar tijdens het afspelen van een replay
- `var_headers`: de variabele-headers geheel (144 bytes elk) en, in `text`, als JSON (naam, type, offset, aantal, eenheid, beschrijving), telkens als de indeling verandert - genoeg om elke variabele van elke bewaarde regel te lezen
- `session_info`: de YAML-tekst geheel telkens als zijn updateteller verschuift (weekend, sessies en resultaten, coureurs, autosetup, radio, cameralijsten), `update` de teller
- `header`: de 112-byte irsdk-header geheel telkens als hij verandert (versie, status, tickrate, offsets, de ticks van de regels)

**Niet beschikbaar**

- een positie in de wereld live: het gedeelde geheugen heeft er geen; breedtegraad, lengtegraad en hoogte staan alleen in de .ibt-bestanden (met loggen aan), die de viewer leest - de watcher noemt die welke tijdens de sessie zijn geschreven
- de ticks tussen twee leesbeurten: de simulator schrijft 60 regels per seconde in 3 of 4 plekken en de watcher leest 10 keer per seconde, dus de meeste ticks worden overschreven voordat ze gelezen kunnen worden; het .ibt-bestand heeft elke tick als loggen aan staat

**Grootte**: een telemetrieregel is enkele KB (ongeveer 5 tot 10 KB met de arrays van elke auto), tot 10 keer per seconde bewaard, plus de header (112 bytes) even vaak en de YAML van de sessie-info (tientallen KB) wanneer die verandert: ongeveer 0,2 tot 0,4 GB per uur op de baan vóór compressie; zstd brengt het tot een deel ervan (nog niet gemeten op een echte sessie)

## Geverifieerd {#verified}

getest op een blok gedeeld geheugen dat in de test is opgebouwd uit de irsdk-indeling; nog niet getest tegen de simulator

## Bron {#source}

[heat3d_watch/adapters/iracing.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/iracing.py)

<!-- Generated from the adapter by tools/gen_game_pages.py; change the adapter and run it again rather than editing this page. -->
