---
title: "BeamNG.drive (livegegevens)"
nav_order: 7
lang: "nl"
source: game-beamng.md
source_hash: "1c23a869a62f"
nav_exclude: true
search_exclude: true
---
# BeamNG.drive (livegegevens) {#beamngdrive-live-data}

Terwijl je BeamNG.drive speelt, slaat de watcher de gegevens op die het spel zelf uitstuurt, zodat je ze later op een kaart in de 3DHeat-viewer kunt bekijken.

*Technische details: adapter `beamng`, soort [`telemetry`](sources-and-rules.md); hij draait zolang `BeamNG.drive.x64.exe` of `BeamNG.drive.exe` actief is en zoekt elke 0,1 s naar nieuwe gegevens.*

## Wat wordt opgenomen {#what-is-recorded}

- positie van de eigen auto (wereld, m, omgedraaid naar Y omhoog) op 10 Hz met snelheid, versnelling, gas en rem
- begin van de rit, resets (herspawn), ronden voorbij de plek waar de rit begon
- ronden, beste ronde, afstand, topsnelheid

## Waar het vandaan komt {#where-it-comes-from}

UDP 127.0.0.1:4460 uit de heat3d-protocolmod (mods/beamng/heat3d in deze repository)

## Hoe je het aanzet {#how-to-switch-it-on}

`python -m heat3d_watch setup beamng --apply` installeert de mod; daarna Options > Other > Protocols > "others"

Typ het commando in een terminal die geopend is in de map van de watcher (zie [Voordat je begint](before-you-start.md)). Als het mislukt, zegt de laatste regel waarom; [Installeren en uitvoeren](installing-and-running.md) beschrijft de gebruikelijke oorzaken.

`python -m heat3d_watch setup beamng` somt de bestanden op die het zou wijzigen; `python -m heat3d_watch setup beamng --apply` wijzigt ze en bewaart het origineel als `<file>.heat3d-backup` (zie [Commando's](commands.md#setup)). Het toont `beamng: changed: ...` voor elke wijziging, of `beamng: nothing to change` als de mod al aan staat.

## Hoe het werkt {#how-it-works}

Telemetrie van racespellen zelf: Forza, de Assetto Corsa-spellen, de rallyspellen en BeamNG, opgeslagen als routes, ronden en etappes.

Elk spel hier publiceert zijn telemetrie bewust, voor dashboards en bewegingssimulatoren; er wordt niets geïnjecteerd en niets gelezen wat het spel niet uitgeeft. De decodering wordt niet twee keer geschreven: het zijn de rondenrecorders van gamecapture in `heat3d_capture/telemetry` van 3DHeat GameCapture, gekopieerd naar `heat3d_watch/decoders` (daar getest tegen pakketten die zijn gebouwd uit de gepubliceerde indelingen). Deze module zet hun frames om in de rijen van de watcher: de positie van de auto een paar keer per seconde met snelheid, versnelling en pedalen, een gebeurtenis per ronde of etappe, en de cijfers die een bestuurder bijhoudt: ronden, beste ronde, afstand en topsnelheid.

#### Forza (Horizon 4/5/6, Motorsport) {#forza-horizon-456-motorsport}

"Data Out" UDP, aan te zetten in de HUD- en Gameplay-instellingen van het spel, naar 127.0.0.1 poort 5300, formaat Dash. Eén pakket per simulatietik; de offset van het dashblok wordt uit de pakketten gevonden (`forza.detect_layout`). Wereldmeters, Y omhoog; de wereld is linkshandig en wordt getekend zoals hij verstuurd wordt, zoals de rondenrecorder doet (de documentatie over "Data Out" van Forza Motorsport en Forza Horizon). Het spel stuurt naar één poort, en FH Companion en andere Data Out-apps luisteren op diezelfde poort. Twee programma's kunnen die niet delen: op Windows krijgt de socket die aan 127.0.0.1 gebonden is de pakketten, en een socket die aan alle adressen op dezelfde poort gebonden is krijgt er geen, wat ook het eerst kwam. Daarom wacht de watcher even nadat het spel gestart is voordat hij de poort neemt, neemt hij hem nooit af van een app die hem vasthoudt, en laat hij hem los zodra een andere app daar gaat luisteren. Terwijl hij de poort vasthoudt, stuurt hij elk pakket ongewijzigd door naar 127.0.0.1:5301 - zet het poortveld van FH Companion (het telemetrietabblad) op 5301 en beide leggen vast.

#### BeamNG.drive {#beamngdrive}

De `heat3d`-protocolmod die gamecapture meelevert (UDP 4460, Options > Other > Protocols > "others"); de Z-omhoog-wereld van BeamNG wordt naar Y omhoog gedraaid, zoals `beamng.py` doet.

#### Alles bewaard {#everything-kept}

De rijen zijn er een paar per seconde; het spel stuurt veel meer. Elk UDP-pakket dat binnenkomt - in de menu's, tussen ronden, ook die welke geen decoder leest - wordt ongewijzigd bewaard in `heat.raw.parquet` van de sessie, onder zijn formaat (`dash-horizon`, `session_update`, `extradata3`, `H3D1`, ...). Elke pagina van het gedeelde geheugen (het volledige gebied, niet alleen de gedecodeerde bytes) wordt bewaard telkens als hij verandert, onder de naam van zijn gebied (`acpmf_physics`, ...). `used` markeert wat ook rijen werd; `selfCheck.completeness` in `meta.json` telt elke soort (de converterregel van 3DHeat).

Dezelfde module werkt ook voor: [Assetto Corsa (livegegevens)](game-assetto-corsa.md), [Assetto Corsa Competizione (livegegevens)](game-assetto-corsa-competizione.md), [Assetto Corsa EVO (livegegevens)](game-assetto-corsa-evo.md), [Assetto Corsa Rally (livegegevens)](game-assetto-corsa-rally.md), [DiRT Rally 2.0 (livegegevens)](game-dirt-rally-2.md), [EA SPORTS WRC (livegegevens)](game-ea-wrc.md), [Forza Horizon 4 (livegegevens)](game-forza-horizon-4.md), [Forza Horizon 5 (livegegevens)](game-forza-horizon-5.md), [Forza Horizon 6 (livegegevens)](game-forza-horizon-6.md), [Forza Motorsport (livegegevens)](game-forza-motorsport.md), [Richard Burns Rally (livegegevens)](game-richard-burns-rally.md).

## Posities en assen {#positions-and-axes}

| | |
|---|---|
| Posities opgenomen | ja |
| Omhoog-as | `y` |
| Eenheden | meter (de Z-omhoog-wereld van BeamNG, om de X-as gedraaid zoals de rondenrecorder doet) |
| Gespiegeld voor de viewer | geen |
| Eenheidsschaal (`scale`: de viewer vermenigvuldigt posities ermee) | 1 |

Dit gaat in het `meta.json` (`axes`) van elke sessie en, als de sessie posities heeft, in de footer van `heat.parquet`. De 3DHeat-viewer draait en schaalt de rijen daardoor zelf - zie [De data](the-data.md).

## Multiplayer {#multiplayer}

- Gemarkeerd als online gespeeld (`multiplayer`): **nee**. `games --markdown` toont dit als "single-player".
- Soort `telemetry`: hij leest alleen wat het spel of platform uitgeeft (een UDP-poort of gedeeld geheugen dat het spel publiceert), dus hij legt ook online spel vast; de vlag bepaalt alleen of geheugen ooit gelezen mag worden.
- Geheugen: **nooit** gelezen door deze adapter. Alleen `memory`-adapters lezen geheugen, en nooit voor een spel dat als online gespeeld is gemarkeerd - zie [Bronnen en regels](sources-and-rules.md).

## Opgenomen statistieken {#statistics-recorded}

Statistiekensleutels die de code van deze adapter bij naam instelt (elke `stats` van de sessie in `meta.json` en de tabel `stats` van `watcher.sqlite`):

`best_lap`, `distance_km`, `laps`, `top_speed_kmh`

Een sleutel tussen accolades wordt tijdens het draaien ingevuld (`score.{team}` is één sleutel per team). Sleutels die de code uit een tabel met de velden van het spel of uit de eigen statistiekennamen van het spel haalt, staan niet in deze lijst; "Wat wordt opgenomen" hierboven noemt ze.

## Volledigheid {#completeness}

De watcher volgt de [converterregel](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md) van 3DHeat: wat de bron bevat wordt gelezen of bewaard, nooit weggegooid. Naast de rijen wordt elk pakket, elke pagina, regel of elk antwoord dat de adapter ontvangt, ongewijzigd bewaard in `heat.raw.parquet` van de sessie (kolommen `time`, `ms`, `type`, `used`, `payload`, `text`, plus elk veld dat op naam bewaard wordt; `used` markeert wat ook rijen werd). `selfCheck.completeness` in `meta.json` telt elk `type` - `lost` is 0.

**Gelezen**

- rijen op 10 Hz: positie, snelheid, versnelling, gas, rem, gier, toerental, stuur; begin van de rit, resets, ronden

**Ruw bewaard**

- elk pakket dat de poort bereikt, helemaal, op de 100 Hz van de mod: `H3D1` (de struct van 160 bytes van de mod: klok, positie, snelheid, de assen van de auto, gier-snelheid, negen invoeren, per wiel de oppervlaktesnelheid, rotatie, belasting en ondergrondmateriaal), `<n>-byte` voor al het andere

**Niet beschikbaar**

- wat de mod niet verstuurt: BeamNG heeft geen vast telemetriepakket, dus de kanalen zijn die welke de heat3d-mod heeft gekozen (andere voertuigen, schade en de naam van de kaart zitten er niet in)

**Grootte**: ongeveer 80 MB per uur voor compressie (100 pakketten per seconde van 160 bytes plus een itemkop van 70 bytes)

## Getest {#verified}

decodering is van de rondenrecorder van gamecapture (getest op pakketten die zijn gebouwd uit de struct van de mod); de adapter is getest op zulke pakketten; de mod is nog niet getest in het spel

## Bron {#source}

[heat3d_watch/adapters/racing.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/racing.py)

<!-- Generated from the adapter by tools/gen_game_pages.py; change the adapter and run it again rather than editing this page. -->
