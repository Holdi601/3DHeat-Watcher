---
title: "Forza Horizon 4 (livegegevens)"
nav_order: 21
lang: "nl"
source: game-forza-horizon-4.md
source_hash: "ac1890f4d62c"
nav_exclude: true
search_exclude: true
---
# Forza Horizon 4 (livegegevens) {#forza-horizon-4-live-data}

Terwijl je Forza Horizon 4 speelt, slaat de watcher de gegevens op die het spel zelf uitstuurt, zodat je ze later op een kaart in de 3DHeat-viewer kunt bekijken.

*Technische details: adapter `forza-horizon-4`, soort [`telemetry`](sources-and-rules.md); hij draait zolang `ForzaHorizon4.exe` loopt en zoekt elke 0,1 s naar nieuwe gegevens.*

## Wat wordt opgenomen {#what-is-recorded}

- positie van de eigen auto (wereld XYZ, m) 10 keer per seconde, met snelheid, versnelling, gas, rem en ronde
- begin en einde van de rit (session_start/session_end), ronden met de rondetijd van het spel
- start en finish van de race met de race-positie
- teleports (terugspoelen, snelreizen): `teleport` waar de auto was, `spawn` waar hij nu is
- ronden, beste ronde, afstand, topsnelheid, races

## Waar het vandaan komt {#where-it-comes-from}

Forza Data Out, UDP 127.0.0.1:5300 (Dash-formaat); elk pakket ongewijzigd doorgestuurd naar 127.0.0.1:5301

## Hoe je het aanzet {#how-to-switch-it-on}

In het spel: Settings > HUD and Gameplay > Data Out On, IP 127.0.0.1, poort 5300 (Motorsport: formaat Dash). FH Companion of een andere Data Out-app: zet de poort op 5301 - de watcher stuurt elk pakket door; zolang een andere app op 5300 luistert, laat de watcher de poort aan die app over en neemt hij niets op

## Hoe het werkt {#how-it-works}

De eigen telemetrie van racegames: Forza, de Assetto Corsa-spellen, de rallygames en BeamNG, opgeslagen als routes, ronden en etappes.

Elk spel hier publiceert zijn telemetrie met opzet, voor dashboards en bewegingsplatforms; er wordt niets geïnjecteerd en niets wat het spel niet uitgeeft wordt gelezen. De decodering wordt niet twee keer geschreven: het zijn de rondenrecorders van gamecapture in `heat3d_capture/telemetry` van 3DHeat GameCapture, gekopieerd naar `heat3d_watch/decoders` (daar getest tegen pakketten die zijn gebouwd uit de gepubliceerde indelingen), en deze module zet hun frames om in de rijen van de watcher: de positie van de auto een paar keer per seconde met snelheid, versnelling en pedalen, een gebeurtenis per ronde of etappe, en de cijfers die een bestuurder bijhoudt: ronden, beste ronde, afstand en topsnelheid.

#### Forza (Horizon 4/5/6, Motorsport) {#forza-horizon-456-motorsport}

"Data Out"-UDP, aangezet in de HUD- en Gameplay-instellingen van het spel, naar 127.0.0.1 poort 5300, formaat Dash. Eén pakket per simulatiestap; de offset van het dash-blok wordt uit de pakketten gevonden (`forza.detect_layout`). Wereldmeters, Y omhoog; de wereld is linkshandig en wordt getekend zoals hij verstuurd wordt, zoals de rondenrecorder dat ook doet (de "Data Out"-documentatie van Forza Motorsport en Forza Horizon). Het spel stuurt naar één poort, en FH Companion en andere Data Out-apps luisteren op dezelfde poort. Twee programma's kunnen die poort niet delen: op Windows krijgt de socket die aan 127.0.0.1 is gebonden de pakketten, en een socket die aan alle adressen op dezelfde poort is gebonden krijgt er geen, wie er ook het eerst was. Daarom wacht de watcher even nadat het spel is gestart voordat hij de poort neemt, neemt hij de poort nooit af van een app die hem vasthoudt, en laat hij hem los zodra een andere app daar gaat luisteren. Terwijl hij de poort vasthoudt, stuurt hij elk pakket ongewijzigd door naar 127.0.0.1:5301 - zet het poortveld van FH Companion (het telemetrie-tabblad) op 5301 en beide nemen op.

#### Alles bewaard {#everything-kept}

De rijen zijn er een paar per seconde; de spellen sturen veel meer. Elk UDP-pakket dat binnenkomt - in de menu's, tussen ronden, ook pakketten die geen decoder leest - wordt ongewijzigd bewaard in de `heat.raw.parquet` van de sessie, onder zijn formaat (`dash-horizon`, `session_update`, `extradata3`, `H3D1`, ...). Elke pagina gedeeld geheugen (het hele geheugengebied, niet alleen de gedecodeerde bytes) wordt bewaard telkens als hij verandert, onder de naam van zijn geheugengebied (`acpmf_physics`, ...). `used` markeert wat ook rijen is geworden; `selfCheck.completeness` in `meta.json` telt elke soort (de [converterregel](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md) van 3DHeat).

Dezelfde module werkt ook voor: [Assetto Corsa (livegegevens)](game-assetto-corsa.md), [Assetto Corsa Competizione (livegegevens)](game-assetto-corsa-competizione.md), [Assetto Corsa EVO (livegegevens)](game-assetto-corsa-evo.md), [Assetto Corsa Rally (livegegevens)](game-assetto-corsa-rally.md), [BeamNG.drive (livegegevens)](game-beamng.md), [DiRT Rally 2.0 (livegegevens)](game-dirt-rally-2.md), [EA SPORTS WRC (livegegevens)](game-ea-wrc.md), [Forza Horizon 5 (livegegevens)](game-forza-horizon-5.md), [Forza Horizon 6 (livegegevens)](game-forza-horizon-6.md), [Forza Motorsport (livegegevens)](game-forza-motorsport.md), [Richard Burns Rally (livegegevens)](game-richard-burns-rally.md).

## Posities en assen {#positions-and-axes}

| | |
|---|---|
| Posities opgenomen | ja |
| Omhoog-as | `y` |
| Eenheden | meter; de wereld van Forza is linkshandig, getekend zoals hij verstuurd wordt, zoals de rondenrecorder dat doet |
| Gespiegeld voor de viewer | geen |
| Eenheidsschaal (`scale`: de viewer vermenigvuldigt posities hiermee) | 1 |

Deze gaan in de `meta.json` van elke sessie (`axes`) en, wanneer de sessie posities heeft, in de footer van `heat.parquet`, zodat de 3DHeat-viewer de rijen zelf draait en schaalt - zie [De data](the-data.md).

## Multiplayer {#multiplayer}

- Als online gespeeld gemarkeerd (`multiplayer`): **ja**. `games --markdown` toont dit als "allowed (reads only what the game publishes)".
- Soort `telemetry`: hij leest alleen wat het spel of platform uitgeeft (een UDP-poort of gedeeld geheugen dat het spel publiceert), dus hij neemt ook op bij online spel, net als offline; de vlag bepaalt alleen of geheugen ooit gelezen mag worden.
- Geheugen: **nooit** gelezen door deze adapter. Alleen `memory`-adapters lezen geheugen, en nooit voor een spel dat als online gespeeld is gemarkeerd - zie [Bronnen en regels](sources-and-rules.md).

## Opgenomen statistieken {#statistics-recorded}

Statistiekensleutels die de code van deze adapter bij naam instelt (de `stats` van elke sessie in `meta.json` en de tabel `stats` in `watcher.sqlite`):

`best_lap`, `distance_km`, `laps`, `races`, `top_speed_kmh`

Een sleutel tussen accolades wordt tijdens het draaien ingevuld (`score.{team}` is één sleutel per team). Sleutels die de code uit een tabel met velden van het spel of uit de eigen statistiekennamen van het spel haalt, staan niet in deze lijst; "Wat wordt opgenomen" hierboven noemt ze.

## Volledigheid {#completeness}

De watcher volgt de [converterregel](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md) van 3DHeat: wat de bron bevat wordt gelezen of bewaard, nooit weggelaten. Naast de rijen wordt elk pakket, elke pagina, regel of antwoord die de adapter ontvangt ongewijzigd bewaard in de `heat.raw.parquet` van de sessie (kolommen `time`, `ms`, `type`, `used`, `payload`, `text`, plus elk veld dat op naam is bewaard; `used` markeert wat ook rijen is geworden), en `selfCheck.completeness` in `meta.json` telt elk `type` - `lost` is 0.

**Gelezen**

- rijen 10 keer per seconde: positie, snelheid, versnelling, gas, rem, ronde, gier/neus/rol (rad), toerental, stuur (-1..1); session_start met de volgnummer, klasse, PI en aandrijving van de auto; ronden met de rondetijd van het spel; race-positie

**Ongewijzigd bewaard**

- elk pakket dat de poort bereikt, geheel, op de snelheid van het spel (één per simulatiestap), onder zijn formaat: `dash-horizon` (324 bytes, Forza Horizon), `dash` (311, Motorsport 7), `dash-fm2023` (331, Forza Motorsport 2023: slijtage van de banden en track-id), `sled` (232, zonder positie), `<n>-byte` voor al het andere - ook menupakketten (isRaceOn 0), de pakketten die worden vastgehouden tot de dash-indeling is bewezen, en de ongeveer 13 bytes van het Horizon-pakket die geen gepubliceerde indeling noemt
- alle wielkanalen van het sled-blok (slipverhouding, slipshoek, gecombineerde slip, ophanging, wielsnelheid, rumble, plas), versnellingen, hoeksnelheid, vermogen, koppel, boost, brandstof, bandtemperaturen, koppeling, handrem, racelijn, AI-remverschil: allemaal in de pakketten, gedecodeerd door `decoders/fulllap.decode_full` uit die pakketten

**Niet beschikbaar**

- andere auto's: Data Out beschrijft alleen de auto van de speler
- de naam van de baan of route: Forza Horizon stuurt die nooit; Motorsport 2023 stuurt alleen een baannummer
- pakketten terwijl een andere app (FH Companion) UDP 5300 vasthoudt: de watcher laat de poort aan die app over

**Grootte**: ongeveer 85 MB per uur vóór compressie (60 pakketten per seconde van 324 bytes plus een itemkop van 70 bytes); opeenvolgende pakketten verschillen weinig, dus zstd houdt een deel ervan over

## Geverifieerd {#verified}

decodering is die van de rondenrecorder van gamecapture (getest met pakketten gebouwd uit de Data Out-indeling); de adapter getest met gesimuleerde pakketten en met opgenomen rondenbanen die als pakketten zijn afgespeeld; nog niet getest tegen het spel zelf

## Bron {#source}

[heat3d_watch/adapters/racing.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/racing.py)

<!-- Generated from the adapter by tools/gen_game_pages.py; change the adapter and run it again rather than editing this page. -->
