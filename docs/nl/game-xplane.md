---
title: "X-Plane (livegegevens)"
nav_order: 50
lang: "nl"
source: game-xplane.md
source_hash: "4e7246cce10c"
nav_exclude: true
search_exclude: true
---
# X-Plane (livegegevens) {#x-plane-live-data}

Terwijl je X-Plane speelt, slaat de watcher de gegevens op die het spel zelf uitstuurt, zodat je ze later op een kaart in de 3DHeat-viewer kunt bekijken.

*Technische details: adapter `xplane`, soort [`telemetry`](sources-and-rules.md); hij draait zolang `X-Plane.exe` loopt en zoekt elke 0,1 s naar nieuwe gegevens.*

## Wat wordt opgenomen {#what-is-recorded}

- de eigen positie 10 keer per seconde (breedtegraad/lengtegraad/hoogte als meter oost/omhoog/noord vanaf het eerste vaste punt; lat/lon/alt bewaard als kolommen)
- houding, aangegeven en ware luchtsnelheid, grondsnelheid, Mach, verticale snelheid, AoA, zijslip, magnetische koers, AGL, g (normaal, axiaal, zijwaarts), snelheid en draaisnelheden, kleppen, luchtremmen, gas, op de grond
- gewichten (totaal, brandstof, lading), hendel van het landingsgestel, automatische piloot, motortoerental en N1, simulatietijd en -datum, pauze, simulatiesnelheid, replay, buitentemperatuur en zeeniveaudruk (X-Plane 12) één keer per seconde
- opstijgingen, landingen, crashes, resets van de vlucht (session_start/session_end per vlucht)
- vliegtijd, tijd in de lucht, afstand, hoogste hoogte, hoogste g, landingen
- elk antwoord dat X-Plane stuurt, geheel bewaard in heat.raw.parquet

## Waar het vandaan komt {#where-it-comes-from}

de UDP-interface van X-Plane op 127.0.0.1:49000 (RREF-datarefs en RPOS-positie, beantwoord aan de watcher)

## Hoe je het aanzet {#how-to-switch-it-on}

X-Plane 12: Settings > Network > Accept incoming connections (X-Plane 11 antwoordt standaard)

## Hoe het werkt {#how-it-works}

X-Plane 11 en 12: de eigen UDP-interface van de simulator op poort 49000.

X-Plane antwoordt iedereen die vraagt op 127.0.0.1:49000, met de gevraagde snelheid, naar
het adres en de poort waarvandaan het verzoek kwam (het document van X-Plane "Exchanging Data with
X-Plane", meegeleverd in `<X-Plane>\Instructions\`):

```text
RREF  "RREF\0" + int32 freq + int32 index + char[400] dataref path (413 bytes).
      The answer is "RREF" + one internal byte + (int32 index, float32 value)
      pairs; freq 0 stops it.
RPOS  "RPOS\0" + the rate as a NUL-terminated ASCII string ("10\0"). The
      answer is "RPOS" + one internal byte + double lon, lat, elevation (m
      MSL) + float AGL (m), pitch, true heading, roll (deg), vx east, vy up,
      vz south (m/s), P, Q, R (rad/s), tightly packed.
```

RPOS geeft breedte- en lengtegraad als doubles (RREF alleen als floats, een halve meter
uiteen), dus RPOS stuurt de positie; RREF brengt de rest en springt in wanneer
RPOS niet komt. Datarefs (namen zoals in `Resources\plugins\DataRefs.txt` van X-Plane 12,
<https://developer.x-plane.com/datarefs/>):

```text
sim/flightmodel/position/latitude, longitude, elevation  deg, deg, m MSL
sim/flightmodel/position/true_theta, true_phi, true_psi  pitch, roll, true heading (deg)
sim/flightmodel/position/indicated_airspeed              knots
sim/flightmodel/position/groundspeed                     m/s
sim/flightmodel/position/y_agl                           m above ground
sim/flightmodel/forces/g_nrml                            g, normal to the wings
sim/flightmodel/failures/onground_any                    1 on the ground
sim/flightmodel2/misc/has_crashed                        1 crashed
sim/time/total_flight_time_sec                           since the flight was reset
```

en de rest van de vlucht in dezelfde snelheid (ware luchtsnelheid, verticale snelheid, AoA,
zijslip, magnetische koers, Mach, axiale en zijwaartse g, draaisnelheden, kleppen,
luchtremmen, gas: `DATAREFS`), met de langzamere toestand van het vliegtuig één keer per
seconde (gewichten, hendel van het landingsgestel, automatische piloot, motoren, de tijd van de simulator, pauze en
snelheid, weer: `SLOW_DATAREFS`). Elk datagram wordt ook geheel bewaard in de
ruwe bijbestand van de sessie, en meta.json noemt de dataref achter elke RREF-index.

X-Plane 12 accepteert dit alleen met Settings > Network > "Accept incoming
connections" aan. Posities gaan in een vlakke kaart rond het eerste vaste punt van de sessie
(`Tangent`): x oost, z noord in meters, y de hoogte boven zeeniveau - zodat een horizontale
vlucht horizontaal blijft, hoe ver hij ook gaat, wat een echt raakvlak door de kromming van
de aarde zou laten zakken. Het oorsprongspunt van de kaart is de `geo` van de sessie: meta.json
en de footer van de tabel dragen die, zodat de viewer de echte wereld onder de vlucht kan leggen.

Deze module bevat ook wat de andere vluchtsimulators gemeen hebben: de vlakke kaart, de
vluchtadministratie (opstijgingen, landingen, crashes, afstand), de UDP-socket en de lijst
van de Steam-bibliotheek.

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

- Als online gespeeld gemarkeerd (`multiplayer`): **nee**. `games --markdown` toont dit als "single-player".
- Soort `telemetry`: hij leest alleen wat het spel of platform uitgeeft (een UDP-poort of gedeeld geheugen dat het spel publiceert), dus hij neemt ook op bij online spel, net als offline; de vlag bepaalt alleen of geheugen ooit gelezen mag worden.
- Geheugen: **nooit** gelezen door deze adapter. Alleen `memory`-adapters lezen geheugen, en nooit voor een spel dat als online gespeeld is gemarkeerd - zie [Bronnen en regels](sources-and-rules.md).

## Opgenomen statistieken {#statistics-recorded}

Statistiekensleutels die de code van deze adapter bij naam instelt (de `stats` van elke sessie in `meta.json` en de tabel `stats` in `watcher.sqlite`):

`airborne_time`, `bad_packets`, `crashes`, `distance_km`, `flight_time`, `max_altitude_m`, `max_g`, `{event}s`

Een sleutel tussen accolades wordt tijdens het draaien ingevuld (`score.{team}` is één sleutel per team). Sleutels die de code uit een tabel met velden van het spel of uit de eigen statistiekennamen van het spel haalt, staan niet in deze lijst; "Wat wordt opgenomen" hierboven noemt ze.

## Volledigheid {#completeness}

De watcher volgt de [converterregel](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md) van 3DHeat: wat de bron bevat wordt gelezen of bewaard, nooit weggelaten. Naast de rijen wordt elk pakket, elke pagina, regel of antwoord die de adapter ontvangt ongewijzigd bewaard in de `heat.raw.parquet` van de sessie (kolommen `time`, `ms`, `type`, `used`, `payload`, `text`, plus elk veld dat op naam is bewaard; `used` markeert wat ook rijen is geworden), en `selfCheck.completeness` in `meta.json` telt elk `type` - `lost` is 0.

**Gelezen**

- RPOS (10 Hz): lengtegraad, breedtegraad, hoogte, AGL, pitch, ware koers, roll, snelheid (oost, omhoog, zuid) en draaisnelheden P/Q/R - allemaal op de rijen
- RREF (10 Hz): de 27 datarefs van `DATAREFS` - positie, houding, IAS, grondsnelheid, TAS, verticale snelheid, AoA, zijslip, magnetische koers, Mach, g normaal/axiaal/zijwaarts, draaisnelheden, kleppen, luchtremmen, gas, AGL, gecrasht, op de grond, vliegtijd - op de rijen
- RREF (1 Hz): de 20 datarefs van `SLOW_DATAREFS` - gewichten, hendel van het landingsgestel, servo's van de automatische piloot, tijd en datum van de simulator, pauze, simulatiesnelheid, replay, aantal motoren, toerental van motoren 1-4, N1 van motoren 1-2, buitenluchttemperatuur, zeeniveaudruk - op de rijen zoals voor het laatst ontvangen

**Ongewijzigd bewaard**

- elk datagram geheel als `payload`, onder zijn vierletterige kop: `RREF` en `RPOS` (gebruikt wanneer de peiling een rij maakte; in de menu's, zonder positie, maken ze er geen), al het andere dat X-Plane naar de poort van de watcher stuurt onder zijn eigen kop of `unknown`; de `requests` in meta.json zegt welke dataref elke RREF-index is, zodat de payloads zonder deze module te lezen zijn

**Niet beschikbaar**

- elke andere dataref (X-Plane heeft er duizenden): RREF stuurt alleen wat gevraagd wordt, één abonnement per stuk; de lijst vraagt de vlucht, de staat van het vliegtuig en de tijd van de simulator - meer cockpitdetail (radio's, lampjes, elke motormeter, storingen) zou de verzoeken vermenigvuldigen
- de naam van het vliegtuig en het ICAO-type: datarefs als bytearray, die RREF als één float per teken stuurt
- andere vliegtuigen (AI en multiplayer): datarefs van sim/multiplayer/position niet gevraagd
- de DATA-uitvoer (Settings > Data Output): die stuurt naar een vast adres dat in de simulator is gekozen, niet naar wie er vraagt; RREF en RPOS dekken wat de watcher leest

**Grootte**: ongeveer 17 MB per uur vóór zstd (RREF en RPOS op 10 Hz, ongeveer 220 en 70 bytes plus een frame elk, de trage RREF één keer per seconde), als X-Plane de waarden van elke peiling in één pakket stuurt zoals het doet; zstd verkleint de floats enkele keren

## Geverifieerd {#verified}

getest tegen een nep-X-Plane die RREF/RPOS beantwoordt volgens 'Exchanging Data with X-Plane' van X-Plane 12; de namen van de datarefs gecontroleerd tegen DataRefs.txt van X-Plane 12; nog niet getest tegen de draaiende simulator

## Bron {#source}

[heat3d_watch/adapters/xplane.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/xplane.py)

<!-- Generated from the adapter by tools/gen_game_pages.py; change the adapter and run it again rather than editing this page. -->
