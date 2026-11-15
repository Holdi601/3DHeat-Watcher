---
title: "Richard Burns Rally (livegegevens)"
nav_order: 39
lang: "nl"
source: game-richard-burns-rally.md
source_hash: "1b9866f5a1f6"
nav_exclude: true
search_exclude: true
---
# Richard Burns Rally (livegegevens) {#richard-burns-rally-live-data}

Terwijl je Richard Burns Rally speelt, slaat de watcher de gegevens op die het spel zelf uitstuurt, zodat je ze later op een kaart in de 3DHeat-viewer kunt bekijken.

*Technische details: adapter `richard-burns-rally`, soort [`telemetry`](sources-and-rules.md); hij draait zolang `RichardBurnsRally_SSE.exe` of `RichardBurnsRally.exe` actief is en zoekt elke 0,1 s naar nieuwe gegevens.*

## Wat wordt opgenomen {#what-is-recorded}

- positie van de eigen auto (wereld XYZ, m) op 10 Hz met snelheid, versnelling, gas, rem en afstand in de etappe
- begin van de etappe (de etappeklok start), finish met de etappetijd, herstarts
- teleports (een reset naar de weg): `teleport` waar de auto was, `spawn` waar hij nu is
- etappes, beste etappetijd, afstand, topsnelheid

## Waar het vandaan komt {#where-it-comes-from}

NGP-plug-in UDP-telemetrie, 127.0.0.1:6776 (RichardBurnsRally.ini [NGP] udpTelemetry=1)

## Hoe je het aanzet {#how-to-switch-it-on}

RSF/NGP: in RichardBurnsRally.ini, sectie [NGP], zet udpTelemetry=1 en het eindpunt op 127.0.0.1:6776

## Hoe het werkt {#how-it-works}

Telemetrie van racespellen zelf: Forza, de Assetto Corsa-spellen, de rallyspellen en BeamNG, opgeslagen als routes, ronden en etappes.

Elk spel hier publiceert zijn telemetrie bewust, voor dashboards en bewegingssimulatoren; er wordt niets geïnjecteerd en niets gelezen wat het spel niet uitgeeft. De decodering wordt niet twee keer geschreven: het zijn de rondenrecorders van gamecapture in `heat3d_capture/telemetry` van 3DHeat GameCapture, gekopieerd naar `heat3d_watch/decoders` (daar getest tegen pakketten die zijn gebouwd uit de gepubliceerde indelingen). Deze module zet hun frames om in de rijen van de watcher: de positie van de auto een paar keer per seconde met snelheid, versnelling en pedalen, een gebeurtenis per ronde of etappe, en de cijfers die een bestuurder bijhoudt: ronden, beste ronde, afstand en topsnelheid.

#### Forza (Horizon 4/5/6, Motorsport) {#forza-horizon-456-motorsport}

"Data Out" UDP, aan te zetten in de HUD- en Gameplay-instellingen van het spel, naar 127.0.0.1 poort 5300, formaat Dash. Eén pakket per simulatietik; de offset van het dashblok wordt uit de pakketten gevonden (`forza.detect_layout`). Wereldmeters, Y omhoog; de wereld is linkshandig en wordt getekend zoals hij verstuurd wordt, zoals de rondenrecorder doet (de documentatie over "Data Out" van Forza Motorsport en Forza Horizon). Het spel stuurt naar één poort, en FH Companion en andere Data Out-apps luisteren op diezelfde poort. Twee programma's kunnen die niet delen: op Windows krijgt de socket die aan 127.0.0.1 gebonden is de pakketten, en een socket die aan alle adressen op dezelfde poort gebonden is krijgt er geen, wat ook het eerst kwam. Daarom wacht de watcher even nadat het spel gestart is voordat hij de poort neemt, neemt hij hem nooit af van een app die hem vasthoudt, en laat hij hem los zodra een andere app daar gaat luisteren. Terwijl hij de poort vasthoudt, stuurt hij elk pakket ongewijzigd door naar 127.0.0.1:5301 - zet het poortveld van FH Companion (het telemetrietabblad) op 5301 en beide leggen vast.

#### EA SPORTS WRC, DiRT Rally 2.0, Richard Burns Rally {#ea-sports-wrc-dirt-rally-20-richard-burns-rally}

UDP: het `config.json` van WRC in `Documents/My Games/WRC/telemetry/` (de `session_update`-pakketstructuur van de `wrc`-struct), het `hardware_settings_config.xml` van DiRT (`<udp enabled="true" extradata="3" port="20777">`), en de NGP-plug-in van RBR (`udpTelemetry=1`, poort 6776). Etappes via de etappeklok van het spel (`rally.StageSplitter`). RBR documenteert zijn assen niet: de omhoog-as is die waarlangs de etappe het minst varieert, en die wordt beslist als de sessie sluit.

#### Alles bewaard {#everything-kept}

De rijen zijn er een paar per seconde; het spel stuurt veel meer. Elk UDP-pakket dat binnenkomt - in de menu's, tussen ronden, ook die welke geen decoder leest - wordt ongewijzigd bewaard in `heat.raw.parquet` van de sessie, onder zijn formaat (`dash-horizon`, `session_update`, `extradata3`, `H3D1`, ...). Elke pagina van het gedeelde geheugen (het volledige gebied, niet alleen de gedecodeerde bytes) wordt bewaard telkens als hij verandert, onder de naam van zijn gebied (`acpmf_physics`, ...). `used` markeert wat ook rijen werd; `selfCheck.completeness` in `meta.json` telt elke soort (de converterregel van 3DHeat).

Dezelfde module werkt ook voor: [Assetto Corsa (livegegevens)](game-assetto-corsa.md), [Assetto Corsa Competizione (livegegevens)](game-assetto-corsa-competizione.md), [Assetto Corsa EVO (livegegevens)](game-assetto-corsa-evo.md), [Assetto Corsa Rally (livegegevens)](game-assetto-corsa-rally.md), [BeamNG.drive (livegegevens)](game-beamng.md), [DiRT Rally 2.0 (livegegevens)](game-dirt-rally-2.md), [EA SPORTS WRC (livegegevens)](game-ea-wrc.md), [Forza Horizon 4 (livegegevens)](game-forza-horizon-4.md), [Forza Horizon 5 (livegegevens)](game-forza-horizon-5.md), [Forza Horizon 6 (livegegevens)](game-forza-horizon-6.md), [Forza Motorsport (livegegevens)](game-forza-motorsport.md).

## Posities en assen {#positions-and-axes}

| | |
|---|---|
| Posities opgenomen | ja |
| Omhoog-as | `y` |
| Eenheden | meter; omhoog-as beslist uit de rit (RBR documenteert zijn assen niet) |
| Gespiegeld voor de viewer | geen |
| Eenheidsschaal (`scale`: de viewer vermenigvuldigt posities ermee) | 1 |

Dit gaat in het `meta.json` (`axes`) van elke sessie en, als de sessie posities heeft, in de footer van `heat.parquet`. De 3DHeat-viewer draait en schaalt de rijen daardoor zelf - zie [De data](the-data.md).

## Multiplayer {#multiplayer}

- Gemarkeerd als online gespeeld (`multiplayer`): **nee**. `games --markdown` toont dit als "single-player".
- Soort `telemetry`: hij leest alleen wat het spel of platform uitgeeft (een UDP-poort of gedeeld geheugen dat het spel publiceert), dus hij legt ook online spel vast; de vlag bepaalt alleen of geheugen ooit gelezen mag worden.
- Geheugen: **nooit** gelezen door deze adapter. Alleen `memory`-adapters lezen geheugen, en nooit voor een spel dat als online gespeeld is gemarkeerd - zie [Bronnen en regels](sources-and-rules.md).

## Opgenomen statistieken {#statistics-recorded}

Statistiekensleutels die de code van deze adapter bij naam instelt (elke `stats` van de sessie in `meta.json` en de tabel `stats` van `watcher.sqlite`):

`best_lap`, `best_stage`, `distance_km`, `laps`, `stages`, `top_speed_kmh`

Een sleutel tussen accolades wordt tijdens het draaien ingevuld (`score.{team}` is één sleutel per team). Sleutels die de code uit een tabel met de velden van het spel of uit de eigen statistiekennamen van het spel haalt, staan niet in deze lijst; "Wat wordt opgenomen" hierboven noemt ze.

## Volledigheid {#completeness}

De watcher volgt de [converterregel](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md) van 3DHeat: wat de bron bevat wordt gelezen of bewaard, nooit weggegooid. Naast de rijen wordt elk pakket, elke pagina, regel of elk antwoord dat de adapter ontvangt, ongewijzigd bewaard in `heat.raw.parquet` van de sessie (kolommen `time`, `ms`, `type`, `used`, `payload`, `text`, plus elk veld dat op naam bewaard wordt; `used` markeert wat ook rijen werd). `selfCheck.completeness` in `meta.json` telt elk `type` - `lost` is 0.

**Gelezen**

- rijen op 10 Hz: positie, snelheid, versnelling, gas, rem, afstand in de etappe, gier, toerental, stuur; begin van de etappe, finish met de etappetijd, herstarts

**Ruw bewaard**

- elk pakket dat de poort bereikt, helemaal, op de snelheid van het spel, onder zijn formaat: `telemetry` (de TelemetryData van NGP, 664 bytes), anders `rbr <n>-byte`
- in het pakket naast de rijen: houding, de eigen snelheden en versnellingen van de auto, per wiel de veerindrukking en -kracht, de voortgang van de etappe en de afstand tot het einde; de rest van de 664 bytes (blokken voor motor, banden en remmen per wiel) wordt nog nergens gedecodeerd

**Niet beschikbaar**

- andere auto's: de spellen sturen alleen de auto van de speler
- de snelheidseenheid en de assen: niet gedocumenteerd - snelheid wordt uit de posities gehaald, omhoog uit de rit

**Grootte**: ongeveer 160 MB per uur bij 60 pakketten per seconde (664 bytes plus een itemkop van 70 bytes); zstd houdt een fractie over

## Getest {#verified}

decodering is van de rondenrecorder van gamecapture (getest op pakketten die zijn gebouwd uit de gedocumenteerde indelingen); de adapter is getest op pakketten die in de test zijn gebouwd en via UDP zijn verstuurd; nog niet getest tegen het spel

## Bron {#source}

[heat3d_watch/adapters/racing.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/racing.py)

<!-- Generated from the adapter by tools/gen_game_pages.py; change the adapter and run it again rather than editing this page. -->
