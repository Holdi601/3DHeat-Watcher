---
title: "EA SPORTS WRC (livegegevens)"
nav_order: 17
lang: "nl"
source: game-ea-wrc.md
source_hash: "c97300f65c43"
nav_exclude: true
search_exclude: true
---
# EA SPORTS WRC (livegegevens) {#ea-sports-wrc-live-data}

Terwijl je EA SPORTS WRC speelt, slaat de watcher de gegevens op die het spel zelf uitstuurt, zodat je ze later op een kaart in de 3DHeat-viewer kunt bekijken.

*Technische details: adapter `ea-wrc`, soort [`telemetry`](sources-and-rules.md); hij draait zolang `WRC.exe` loopt en zoekt elke 0,1 s naar nieuwe gegevens.*

## Wat wordt opgenomen {#what-is-recorded}

- positie van de eigen auto (wereld XYZ, m) 10 keer per seconde, met snelheid, versnelling, gas, rem en afstand in de etappe
- start van de etappe (de etappeklok start), einde met de etappetijd, herstarts
- teleports (een terugzetting naar de weg): `teleport` waar de auto was, `spawn` waar hij nu is
- etappes, beste etappetijd, afstand, topsnelheid

## Waar het vandaan komt {#where-it-comes-from}

UDP 127.0.0.1:20777, het session_update-pakket van de standaard-`wrc`-structuur (Documents\My Games\WRC\telemetry\config.json); zolang een andere app poort 20777 vasthoudt, laat de watcher de poort aan die app over

## Hoe je het aanzet {#how-to-switch-it-on}

`python -m heat3d_watch setup ea-wrc --apply` zet het session_update-pakket aan in config.json (eerst een back-up)

Typ de opdracht in een terminal die geopend is in de map van de watcher (zie [Voordat je begint](before-you-start.md)). Als het mislukt, zegt de laatste regel waarom; [Installeren en uitvoeren](installing-and-running.md) beschrijft de gebruikelijke oorzaken.

`python -m heat3d_watch setup ea-wrc` toont welke bestanden het zou wijzigen; `python -m heat3d_watch setup ea-wrc --apply` wijzigt ze en bewaart het origineel als `<file>.heat3d-backup` (zie [Opdrachten](commands.md#setup)). Het schrijft `ea-wrc: changed: ...` voor elke wijziging, of `ea-wrc: nothing to change` wanneer het al aanstaat.

## Hoe het werkt {#how-it-works}

De eigen telemetrie van racegames: Forza, de Assetto Corsa-spellen, de rallygames en BeamNG, opgeslagen als routes, ronden en etappes.

Elk spel hier publiceert zijn telemetrie met opzet, voor dashboards en bewegingsplatforms; er wordt niets geïnjecteerd en niets wat het spel niet uitgeeft wordt gelezen. De decodering wordt niet twee keer geschreven: het zijn de rondenrecorders van gamecapture in `heat3d_capture/telemetry` van 3DHeat GameCapture, gekopieerd naar `heat3d_watch/decoders` (daar getest tegen pakketten die zijn gebouwd uit de gepubliceerde indelingen), en deze module zet hun frames om in de rijen van de watcher: de positie van de auto een paar keer per seconde met snelheid, versnelling en pedalen, een gebeurtenis per ronde of etappe, en de cijfers die een bestuurder bijhoudt: ronden, beste ronde, afstand en topsnelheid.

#### Forza (Horizon 4/5/6, Motorsport) {#forza-horizon-456-motorsport}

"Data Out"-UDP, aangezet in de HUD- en Gameplay-instellingen van het spel, naar 127.0.0.1 poort 5300, formaat Dash. Eén pakket per simulatiestap; de offset van het dash-blok wordt uit de pakketten gevonden (`forza.detect_layout`). Wereldmeters, Y omhoog; de wereld is linkshandig en wordt getekend zoals hij verstuurd wordt, zoals de rondenrecorder dat ook doet (de "Data Out"-documentatie van Forza Motorsport en Forza Horizon). Het spel stuurt naar één poort, en FH Companion en andere Data Out-apps luisteren op dezelfde poort. Twee programma's kunnen die poort niet delen: op Windows krijgt de socket die aan 127.0.0.1 is gebonden de pakketten, en een socket die aan alle adressen op dezelfde poort is gebonden krijgt er geen, wie er ook het eerst was. Daarom wacht de watcher even nadat het spel is gestart voordat hij de poort neemt, neemt hij de poort nooit af van een app die hem vasthoudt, en laat hij hem los zodra een andere app daar gaat luisteren. Terwijl hij de poort vasthoudt, stuurt hij elk pakket ongewijzigd door naar 127.0.0.1:5301 - zet het poortveld van FH Companion (het telemetrie-tabblad) op 5301 en beide nemen op.

#### EA SPORTS WRC, DiRT Rally 2.0, Richard Burns Rally {#ea-sports-wrc-dirt-rally-20-richard-burns-rally}

UDP: het `wrc`-structuur-pakket `session_update` uit WRC's `Documents/My Games/WRC/telemetry/config.json`, DiRT's `hardware_settings_config.xml` (`<udp enabled="true" extradata="3" port="20777">`), en de NGP-plugin van RBR (`udpTelemetry=1`, poort 6776). Etappes via de etappeklok van het spel (`rally.StageSplitter`). RBR documenteert zijn assen niet: de omhoog-as is de as waarlangs de etappe het minst varieert, die wordt bepaald als de sessie sluit.

#### Alles bewaard {#everything-kept}

De rijen zijn er een paar per seconde; de spellen sturen veel meer. Elk UDP-pakket dat binnenkomt - in de menu's, tussen ronden, ook pakketten die geen decoder leest - wordt ongewijzigd bewaard in de `heat.raw.parquet` van de sessie, onder zijn formaat (`dash-horizon`, `session_update`, `extradata3`, `H3D1`, ...). Elke pagina gedeeld geheugen (het hele geheugengebied, niet alleen de gedecodeerde bytes) wordt bewaard telkens als hij verandert, onder de naam van zijn geheugengebied (`acpmf_physics`, ...). `used` markeert wat ook rijen is geworden; `selfCheck.completeness` in `meta.json` telt elke soort (de [converterregel](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md) van 3DHeat).

Dezelfde module werkt ook voor: [Assetto Corsa (livegegevens)](game-assetto-corsa.md), [Assetto Corsa Competizione (livegegevens)](game-assetto-corsa-competizione.md), [Assetto Corsa EVO (livegegevens)](game-assetto-corsa-evo.md), [Assetto Corsa Rally (livegegevens)](game-assetto-corsa-rally.md), [BeamNG.drive (livegegevens)](game-beamng.md), [DiRT Rally 2.0 (livegegevens)](game-dirt-rally-2.md), [Forza Horizon 4 (livegegevens)](game-forza-horizon-4.md), [Forza Horizon 5 (livegegevens)](game-forza-horizon-5.md), [Forza Horizon 6 (livegegevens)](game-forza-horizon-6.md), [Forza Motorsport (livegegevens)](game-forza-motorsport.md), [Richard Burns Rally (livegegevens)](game-richard-burns-rally.md).

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

- rijen 10 keer per seconde: positie, snelheid, versnelling, gas, rem, afstand in de etappe, gier, toerental, stuur; start van de etappe, einde met de etappetijd, herstarts

**Ongewijzigd bewaard**

- elk pakket dat de poort bereikt, geheel, op de snelheid van het spel, onder zijn formaat: `session_update` (de standaard-`wrc`-structuur, 237 bytes), `wrc <n>-byte` voor elk ander pakket dat de config stuurt
- in het pakket naast de rijen: wereldsnelheid en -versnelling, de assen van de auto, positie en snelheid van de naaf per wiel, snelheid van het contactvlak, remtemperatuur, koppeling, handrem, de spelklok; 22 bytes (offsets 16-36 en 40) die geen gepubliceerde kanaallijst noemt

**Niet beschikbaar**

- andere auto's: het spel stuurt alleen de auto van de speler
- de andere structuren en pakketten die de telemetrie-config kan definiëren (session_start, session_end, pauze): alleen `session_update` wordt door `setup` aangezet; elk ander pakket dat naar de poort gaat, wordt bewaard

**Grootte**: ongeveer 65 MB per uur bij 60 pakketten per seconde (237 bytes plus een itemkop van 70 bytes; de rate van -1 in de config stuurt één pakket per frame, dus meer bij een hogere framerate); zstd houdt een deel over

## Geverifieerd {#verified}

decodering is die van de rondenrecorder van gamecapture (getest met pakketten gebouwd uit de gedocumenteerde indelingen); de adapter getest met pakketten die in de test zijn gemaakt en over UDP zijn verstuurd; nog niet getest tegen het spel

## Bron {#source}

[heat3d_watch/adapters/racing.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/racing.py)

<!-- Generated from the adapter by tools/gen_game_pages.py; change the adapter and run it again rather than editing this page. -->
