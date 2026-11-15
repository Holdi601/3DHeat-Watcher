---
title: "Assetto Corsa (livegegevens)"
nav_order: 2
lang: "nl"
source: game-assetto-corsa.md
source_hash: "9132272cc104"
nav_exclude: true
search_exclude: true
---
# Assetto Corsa (livegegevens) {#assetto-corsa-live-data}

Terwijl je Assetto Corsa speelt, slaat de watcher de gegevens op die het spel zelf uitstuurt, zodat je ze later op een kaart in de 3DHeat-viewer kunt bekijken.

*Technische details: adapter `assetto-corsa`, soort [`telemetry`](sources-and-rules.md); hij draait zolang `acs.exe` of `acs_x86.exe` loopt en zoekt elke 0,1 s naar nieuwe gegevens.*

## Wat wordt opgenomen {#what-is-recorded}

- positie van de eigen auto (wereld XYZ, m: gemiddelde van de bandcontactpunten) 10 keer per seconde, met snelheid, versnelling, gas en rem
- begin en einde van de sessie, met de baan en de auto zoals het spel ze noemt
- ronden volgens de rondenteller van het spel, met de rondetijd
- teleports (terug naar de pits, een herstart): `teleport` waar de auto was, `spawn` waar hij nu is
- ronden, beste ronde, afstand, topsnelheid

## Waar het vandaan komt {#where-it-comes-from}

gedeeld geheugen Local\acpmf_physics, Local\acpmf_graphics, Local\acpmf_static

## Hoe je het aanzet {#how-to-switch-it-on}

Je hoeft niets aan te zetten: de watcher leest de bron zoals het spel of het platform die aanbiedt.

## Hoe het werkt {#how-it-works}

De eigen telemetrie van racegames: Forza, de Assetto Corsa-spellen, de rallygames en BeamNG, opgeslagen als routes, ronden en etappes.

Elk spel hier publiceert zijn telemetrie met opzet, voor dashboards en bewegingsplatforms; er wordt niets geïnjecteerd en niets wat het spel niet uitgeeft wordt gelezen. De decodering wordt niet twee keer geschreven: het zijn de rondenrecorders van gamecapture in `heat3d_capture/telemetry` van 3DHeat GameCapture, gekopieerd naar `heat3d_watch/decoders` (daar getest tegen pakketten die zijn gebouwd uit de gepubliceerde indelingen), en deze module zet hun frames om in de rijen van de watcher: de positie van de auto een paar keer per seconde met snelheid, versnelling en pedalen, een gebeurtenis per ronde of etappe, en de cijfers die een bestuurder bijhoudt: ronden, beste ronde, afstand en topsnelheid.

#### Forza (Horizon 4/5/6, Motorsport) {#forza-horizon-456-motorsport}

"Data Out"-UDP, aangezet in de HUD- en Gameplay-instellingen van het spel, naar 127.0.0.1 poort 5300, formaat Dash. Eén pakket per simulatiestap; de offset van het dash-blok wordt uit de pakketten gevonden (`forza.detect_layout`). Wereldmeters, Y omhoog; de wereld is linkshandig en wordt getekend zoals hij verstuurd wordt, zoals de rondenrecorder dat ook doet (de "Data Out"-documentatie van Forza Motorsport en Forza Horizon). Het spel stuurt naar één poort, en FH Companion en andere Data Out-apps luisteren op dezelfde poort. Twee programma's kunnen die poort niet delen: op Windows krijgt de socket die aan 127.0.0.1 is gebonden de pakketten, en een socket die aan alle adressen op dezelfde poort is gebonden krijgt er geen, wie er ook het eerst was. Daarom wacht de watcher even nadat het spel is gestart voordat hij de poort neemt, neemt hij de poort nooit af van een app die hem vasthoudt, en laat hij hem los zodra een andere app daar gaat luisteren. Terwijl hij de poort vasthoudt, stuurt hij elk pakket ongewijzigd door naar 127.0.0.1:5301 - zet het poortveld van FH Companion (het telemetrie-tabblad) op 5301 en beide nemen op.

#### Assetto Corsa, ACC, AC EVO, AC Rally {#assetto-corsa-acc-ac-evo-ac-rally}

Gedeeld geheugen dat het spel voor apps schrijft: `Local\acpmf_physics`, `Local\acpmf_graphics`, `Local\acpmf_static` (AC EVO: `Local\acevo_pmf_*`). Alleen-lezen geopend, en pas zodra het spel het heeft aangemaakt (`simracing_shm`). De positie is het gemiddelde van de vier bandcontactpunten, in wereldmeters, Y omhoog. Ronden volgens de teller van het spel (AC, ACC) of doordat het startpunt weer wordt gepasseerd (AC EVO, AC Rally), zoals `kunos.py` doet voor de rondenrecorder.

#### Alles bewaard {#everything-kept}

De rijen zijn er een paar per seconde; de spellen sturen veel meer. Elk UDP-pakket dat binnenkomt - in de menu's, tussen ronden, ook pakketten die geen decoder leest - wordt ongewijzigd bewaard in de `heat.raw.parquet` van de sessie, onder zijn formaat (`dash-horizon`, `session_update`, `extradata3`, `H3D1`, ...). Elke pagina gedeeld geheugen (het hele geheugengebied, niet alleen de gedecodeerde bytes) wordt bewaard telkens als hij verandert, onder de naam van zijn geheugengebied (`acpmf_physics`, ...). `used` markeert wat ook rijen is geworden; `selfCheck.completeness` in `meta.json` telt elke soort (de [converterregel](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md) van 3DHeat).

Dezelfde module werkt ook voor: [Assetto Corsa Competizione (livegegevens)](game-assetto-corsa-competizione.md), [Assetto Corsa EVO (livegegevens)](game-assetto-corsa-evo.md), [Assetto Corsa Rally (livegegevens)](game-assetto-corsa-rally.md), [BeamNG.drive (livegegevens)](game-beamng.md), [DiRT Rally 2.0 (livegegevens)](game-dirt-rally-2.md), [EA SPORTS WRC (livegegevens)](game-ea-wrc.md), [Forza Horizon 4 (livegegevens)](game-forza-horizon-4.md), [Forza Horizon 5 (livegegevens)](game-forza-horizon-5.md), [Forza Horizon 6 (livegegevens)](game-forza-horizon-6.md), [Forza Motorsport (livegegevens)](game-forza-motorsport.md), [Richard Burns Rally (livegegevens)](game-richard-burns-rally.md).

## Posities en assen {#positions-and-axes}

| | |
|---|---|
| Posities opgenomen | ja |
| Omhoog-as | `y` |
| Eenheden | meter |
| Gespiegeld voor de viewer | geen |
| Eenheidsschaal (`scale`: de viewer vermenigvuldigt posities hiermee) | 1 |

Deze gaan in de `meta.json` van elke sessie (`axes`) en, wanneer de sessie posities heeft, in de footer van `heat.parquet`, zodat de 3DHeat-viewer de rijen zelf draait en schaalt - zie [De data](the-data.md).

## Multiplayer {#multiplayer}

- Als online gespeeld gemarkeerd (`multiplayer`): **ja**. `games --markdown` toont dit als "allowed (reads only what the game publishes)".
- Soort `telemetry`: hij leest alleen wat het spel of platform uitgeeft (een UDP-poort of gedeeld geheugen dat het spel publiceert), dus hij neemt ook op bij online spel, net als offline; de vlag bepaalt alleen of geheugen ooit gelezen mag worden.
- Geheugen: **nooit** gelezen door deze adapter. Alleen `memory`-adapters lezen geheugen, en nooit voor een spel dat als online gespeeld is gemarkeerd - zie [Bronnen en regels](sources-and-rules.md).

## Opgenomen statistieken {#statistics-recorded}

Statistiekensleutels die de code van deze adapter bij naam instelt (de `stats` van elke sessie in `meta.json` en de tabel `stats` in `watcher.sqlite`):

`best_lap`, `best_stage`, `distance_km`, `laps`, `race_position`, `stages`, `top_speed_kmh`

Een sleutel tussen accolades wordt tijdens het draaien ingevuld (`score.{team}` is één sleutel per team). Sleutels die de code uit een tabel met velden van het spel of uit de eigen statistiekennamen van het spel haalt, staan niet in deze lijst; "Wat wordt opgenomen" hierboven noemt ze.

## Volledigheid {#completeness}

De watcher volgt de [converterregel](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md) van 3DHeat: wat de bron bevat wordt gelezen of bewaard, nooit weggelaten. Naast de rijen wordt elk pakket, elke pagina, regel of antwoord die de adapter ontvangt ongewijzigd bewaard in de `heat.raw.parquet` van de sessie (kolommen `time`, `ms`, `type`, `used`, `payload`, `text`, plus elk veld dat op naam is bewaard; `used` markeert wat ook rijen is geworden), en `selfCheck.completeness` in `meta.json` telt elk `type` - `lost` is 0.

**Gelezen**

- rijen 10 keer per seconde uit de physics-pagina: positie (gemiddelde van de bandcontactpunten), snelheid, versnelling, gas, rem, gier/neus/rol (rad), toerental, stuur (zoals de pagina het heeft); begin van de sessie met de baan en de auto uit de statische pagina; ronden, race-positie

**Ongewijzigd bewaard**

- elke pagina geheel - het volledige geheugengebied, niet alleen de gedecodeerde bytes - telkens als de bytes veranderen, bij de leesbeurt van de watcher van 10 Hz: `acpmf_physics`, `acpmf_graphics`, `acpmf_static`; een herlezing die byte voor byte gelijk is aan de vorige wordt geteld in `unchanged_reads` in meta.json, niet opnieuw opgeslagen
- alles wat alleen voor rondenbestanden wordt gedecodeerd (`decoders/kunos.py`: slip, belasting, druk, temperaturen, camber, ophanging, contactpunten, remtemperaturen, slipverhouding en slipshoek per wiel; wereld- en lokale snelheid, hoeksnelheid, hulpmiddelen) staat in die pagina's

**Niet beschikbaar**

- posities van andere auto's: de pagina's beschrijven alleen de auto van de speler (de graphics-pagina van ACC heeft in sommige versies auto-id's en coördinaten van anderen - bewaard in de ruwe pagina, niet gedecodeerd)
- fysica-ticks tussen de leesbeurten van de watcher: het spel schrijft de pagina op zijn fysicasnelheid (tot 333 Hz) en de watcher leest 10 keer per seconde

**Grootte**: ongeveer 150-300 MB per uur vóór compressie (een pagina van 4 KB per keer dat hij verandert, tot 10 keer per seconde); de pagina's bestaan meestal uit nullen en zstd houdt er een klein deel van over

## Geverifieerd {#verified}

decodering is die van de rondenrecorder van gamecapture (getest met gesimuleerde pagina's); de adapter getest met gedeeld geheugen dat in de test is opgebouwd volgens de gedocumenteerde indeling; nog niet getest tegen het spel

## Bron {#source}

[heat3d_watch/adapters/racing.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/racing.py)

<!-- Generated from the adapter by tools/gen_game_pages.py; change the adapter and run it again rather than editing this page. -->
