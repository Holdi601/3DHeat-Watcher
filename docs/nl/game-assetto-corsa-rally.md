---
title: "Assetto Corsa Rally (livegegevens)"
nav_order: 5
lang: "nl"
source: game-assetto-corsa-rally.md
source_hash: "09b8a6d66e31"
nav_exclude: true
search_exclude: true
---
# Assetto Corsa Rally (livegegevens) {#assetto-corsa-rally-live-data}

Terwijl je Assetto Corsa Rally speelt, slaat de watcher de gegevens op die het spel zelf uitstuurt, zodat je ze later op een kaart in de 3DHeat-viewer kunt bekijken.

*Technische details: adapter `assetto-corsa-rally`, soort [`telemetry`](sources-and-rules.md); hij draait zolang `acr.exe`, `ACR-Win64-Shipping.exe`, `AssettoCorsaRally.exe` of `acrally-Win64-Shipping.exe` actief is en zoekt elke 0,1 s naar nieuwe gegevens.*

## Wat wordt opgenomen {#what-is-recorded}

- positie van de eigen auto (wereld XYZ, m: het gemiddelde van de contactpunten van de banden) op 10 Hz, met snelheid, versnelling, gas en rem
- begin en einde van de sessie, met de baan en de auto zoals het spel ze noemt
- etappes: één eindigt waar de auto daarna stopt, met de tijd die het kostte
- teleports (terug naar de pits, een herstart): `teleport` waar de auto was, `spawn` waar hij nu is
- ronden, beste ronde, afstand, topsnelheid

## Waar het vandaan komt {#where-it-comes-from}

gedeeld geheugen Local\acpmf_physics, Local\acpmf_static (dezelfde pagina's als AC en ACC)

## Hoe je het aanzet {#how-to-switch-it-on}

Niets hoeft aangezet te worden: de watcher leest de bron zoals het spel of platform die aanbiedt.

## Hoe het werkt {#how-it-works}

Telemetrie van racespellen zelf: Forza, de Assetto Corsa-spellen, de rallyspellen en BeamNG, opgeslagen als routes, ronden en etappes.

Elk spel hier publiceert zijn telemetrie bewust, voor dashboards en bewegingssimulatoren; er wordt niets geïnjecteerd en niets gelezen wat het spel niet uitgeeft. De decodering wordt niet twee keer geschreven: het zijn de rondenrecorders van gamecapture in `heat3d_capture/telemetry` van 3DHeat GameCapture, gekopieerd naar `heat3d_watch/decoders` (daar getest tegen pakketten die zijn gebouwd uit de gepubliceerde indelingen). Deze module zet hun frames om in de rijen van de watcher: de positie van de auto een paar keer per seconde met snelheid, versnelling en pedalen, een gebeurtenis per ronde of etappe, en de cijfers die een bestuurder bijhoudt: ronden, beste ronde, afstand en topsnelheid.

#### Forza (Horizon 4/5/6, Motorsport) {#forza-horizon-456-motorsport}

"Data Out" UDP, aan te zetten in de HUD- en Gameplay-instellingen van het spel, naar 127.0.0.1 poort 5300, formaat Dash. Eén pakket per simulatietik; de offset van het dashblok wordt uit de pakketten gevonden (`forza.detect_layout`). Wereldmeters, Y omhoog; de wereld is linkshandig en wordt getekend zoals hij verstuurd wordt, zoals de rondenrecorder doet (de documentatie over "Data Out" van Forza Motorsport en Forza Horizon). Het spel stuurt naar één poort, en FH Companion en andere Data Out-apps luisteren op diezelfde poort. Twee programma's kunnen die niet delen: op Windows krijgt de socket die aan 127.0.0.1 gebonden is de pakketten, en een socket die aan alle adressen op dezelfde poort gebonden is krijgt er geen, wat ook het eerst kwam. Daarom wacht de watcher even nadat het spel gestart is voordat hij de poort neemt, neemt hij hem nooit af van een app die hem vasthoudt, en laat hij hem los zodra een andere app daar gaat luisteren. Terwijl hij de poort vasthoudt, stuurt hij elk pakket ongewijzigd door naar 127.0.0.1:5301 - zet het poortveld van FH Companion (het telemetrietabblad) op 5301 en beide leggen vast.

#### Alles bewaard {#everything-kept}

De rijen zijn er een paar per seconde; het spel stuurt veel meer. Elk UDP-pakket dat binnenkomt - in de menu's, tussen ronden, ook die welke geen decoder leest - wordt ongewijzigd bewaard in `heat.raw.parquet` van de sessie, onder zijn formaat (`dash-horizon`, `session_update`, `extradata3`, `H3D1`, ...). Elke pagina van het gedeelde geheugen (het volledige gebied, niet alleen de gedecodeerde bytes) wordt bewaard telkens als hij verandert, onder de naam van zijn gebied (`acpmf_physics`, ...). `used` markeert wat ook rijen werd; `selfCheck.completeness` in `meta.json` telt elke soort (de converterregel van 3DHeat).

Dezelfde module werkt ook voor: [Assetto Corsa (livegegevens)](game-assetto-corsa.md), [Assetto Corsa Competizione (livegegevens)](game-assetto-corsa-competizione.md), [Assetto Corsa EVO (livegegevens)](game-assetto-corsa-evo.md), [BeamNG.drive (livegegevens)](game-beamng.md), [DiRT Rally 2.0 (livegegevens)](game-dirt-rally-2.md), [EA SPORTS WRC (livegegevens)](game-ea-wrc.md), [Forza Horizon 4 (livegegevens)](game-forza-horizon-4.md), [Forza Horizon 5 (livegegevens)](game-forza-horizon-5.md), [Forza Horizon 6 (livegegevens)](game-forza-horizon-6.md), [Forza Motorsport (livegegevens)](game-forza-motorsport.md), [Richard Burns Rally (livegegevens)](game-richard-burns-rally.md).

## Posities en assen {#positions-and-axes}

| | |
|---|---|
| Posities opgenomen | ja |
| Omhoog-as | `y` |
| Eenheden | meter |
| Gespiegeld voor de viewer | geen |
| Eenheidsschaal (`scale`: de viewer vermenigvuldigt posities ermee) | 1 |

Dit gaat in het `meta.json` (`axes`) van elke sessie en, als de sessie posities heeft, in de footer van `heat.parquet`. De 3DHeat-viewer draait en schaalt de rijen daardoor zelf - zie [De data](the-data.md).

## Multiplayer {#multiplayer}

- Gemarkeerd als online gespeeld (`multiplayer`): **ja**. `games --markdown` toont dit als "allowed (reads only what the game publishes)".
- Soort `telemetry`: hij leest alleen wat het spel of platform uitgeeft (een UDP-poort of gedeeld geheugen dat het spel publiceert), dus hij legt ook online spel vast; de vlag bepaalt alleen of geheugen ooit gelezen mag worden.
- Geheugen: **nooit** gelezen door deze adapter. Alleen `memory`-adapters lezen geheugen, en nooit voor een spel dat als online gespeeld is gemarkeerd - zie [Bronnen en regels](sources-and-rules.md).

## Opgenomen statistieken {#statistics-recorded}

Statistiekensleutels die de code van deze adapter bij naam instelt (elke `stats` van de sessie in `meta.json` en de tabel `stats` van `watcher.sqlite`):

`best_lap`, `best_stage`, `distance_km`, `laps`, `stages`, `top_speed_kmh`

Een sleutel tussen accolades wordt tijdens het draaien ingevuld (`score.{team}` is één sleutel per team). Sleutels die de code uit een tabel met de velden van het spel of uit de eigen statistiekennamen van het spel haalt, staan niet in deze lijst; "Wat wordt opgenomen" hierboven noemt ze.

## Volledigheid {#completeness}

De watcher volgt de [converterregel](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md) van 3DHeat: wat de bron bevat wordt gelezen of bewaard, nooit weggegooid. Naast de rijen wordt elk pakket, elke pagina, regel of elk antwoord dat de adapter ontvangt, ongewijzigd bewaard in `heat.raw.parquet` van de sessie (kolommen `time`, `ms`, `type`, `used`, `payload`, `text`, plus elk veld dat op naam bewaard wordt; `used` markeert wat ook rijen werd). `selfCheck.completeness` in `meta.json` telt elk `type` - `lost` is 0.

**Gelezen**

- rijen op 10 Hz uit de fysicapagina: positie (gemiddelde van de contactpunten van de banden), snelheid, versnelling, gas, rem, gier/neus/rol (rad), toerental, stuur (zoals de pagina het heeft); begin van de sessie met de baan en de auto uit de statische pagina; ronden, positie in de race

**Ruw bewaard**

- elke pagina helemaal - het volledige geheugengebied, niet alleen de gedecodeerde bytes - telkens als de bytes veranderen, bij de lezing van de watcher van 10 Hz: `acpmf_physics`, `acpmf_static`; een herlezing die byte voor byte gelijk is aan de vorige, wordt geteld in `unchanged_reads` van meta.json en niet opnieuw opgeslagen
- alles wat alleen voor rondebestanden gedecodeerd wordt (`decoders/kunos.py`: per wiel slip, belasting, druk, temperaturen, camber, ophanging, contactpunten, remtemperaturen, slipverhouding en -hoek; wereld- en lokale snelheid, hoeksnelheid, hulpmiddelen) staat in die pagina's

**Niet beschikbaar**

- posities van andere auto's: de pagina's beschrijven alleen de auto van de speler (de graphics-pagina van ACC heeft in sommige versies auto-id's en coördinaten voor de anderen - bewaard in de ruwe pagina, niet gedecodeerd)
- fysicaticks tussen de lezingen van de watcher: het spel schrijft de pagina op zijn fysicasnelheid (tot 333 Hz) en de watcher leest 10 keer per seconde
- een etappeklok of de etappetijd van het spel: AC Rally publiceert geen graphics-pagina; etappes eindigen waar de auto stopt

**Grootte**: ongeveer 150-300 MB per uur voor compressie (een gebied van 4 KB per pagina bij maximaal 10 wijzigingen per seconde); de pagina's bestaan vooral uit nullen, en zstd houdt er een klein deel van over

## Getest {#verified}

decodering is van de rondenrecorder van gamecapture (getest op synthetische pagina's); de adapter is getest op gedeeld geheugen dat in de test is opgebouwd uit de gedocumenteerde indeling; nog niet getest tegen het spel; de naam van het uitvoerbare bestand is nog niet bevestigd

## Bron {#source}

[heat3d_watch/adapters/racing.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/racing.py)

<!-- Generated from the adapter by tools/gen_game_pages.py; change the adapter and run it again rather than editing this page. -->
