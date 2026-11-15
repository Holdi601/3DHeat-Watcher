---
title: "American Truck Simulator (livegegevens)"
nav_order: 1
lang: "nl"
source: game-ats.md
source_hash: "974252b355da"
nav_exclude: true
search_exclude: true
---
# American Truck Simulator (livegegevens) {#american-truck-simulator-live-data}

Terwijl je American Truck Simulator speelt, slaat de watcher de gegevens op die het spel zelf uitstuurt, zodat je ze later op een kaart in de 3DHeat-viewer kunt bekijken.

*Technische details: adapter `ats`, soort [`telemetry`](sources-and-rules.md); hij draait zolang `amtrucks.exe` actief is en zoekt elke 0,1 s naar nieuwe gegevens.*

## Wat wordt opgenomen {#what-is-recorded}

- de wereldpositie van de truck (x oost, y omhoog, z zuid, m) op 10 Hz terwijl hij rijdt, elke 5 s terwijl hij stilstaat; koers, snelheid, kilometerteller
- gestarte opdrachten (lading, van, naar), afgeleverde (opbrengst, XP, km), geannuleerde; boetes, tol, veerboten, treinen, tanken
- veerboten, treinen en geladen opgeslagen spellen knippen de route door (teleport, spawn)
- afstand, topsnelheid, leveringen, opbrengst, XP, boetes
- het volledige gedeelde geheugen van de plug-in in `heat.raw.parquet`, telkens als het verandert

## Waar het vandaan komt {#where-it-comes-from}

gedeeld geheugen Local\SCSTelemetry, geschreven door de RenCloud scs-sdk-plugin (revisie 12) in &lt;game>\bin\win_x64\plugins

## Hoe je het aanzet {#how-to-switch-it-on}

installeer scs-telemetry.dll (revisie 12) van github.com/RenCloud/scs-sdk-plugin in &lt;game>\bin\win_x64\plugins; het spel vraagt bij elke start één keer om de SDK toe te staan

## Hoe het werkt {#how-it-works}

Euro Truck Simulator 2 en American Truck Simulator: de telemetrie-SDK van SCS, via de RenCloud-plugin.

SCS publiceert een telemetrie-SDK (<https://modding.scssoft.com/wiki/Documentation/Engine/SDK/Telemetry>) voor plugins die de speler in `<game>\bin\win_x64\plugins\` zet. Het spel zelf publiceert niets; de veelgebruikte plugin van <https://github.com/RenCloud/scs-sdk-plugin> (MIT) kopieert de kanalen van de SDK naar het gedeelde geheugen `Local\SCSTelemetry` (32 KiB), met de indeling uit `scs-telemetry/inc/scs-telemetry-common.hpp`. Dit leest revisie 12 van die indeling (PLUGIN_REVID 12) en niets anders: de plugin schrijft zijn revisie op offset 40, en elke andere revisie wordt ongelezen gelaten in plaats van verkeerd gelezen. Gebruikte offsets (zones zoals de kop ze aangeeft; natuurlijke uitlijning):

```text
   0  bool sdkActive          4  bool paused
  40  u32  telemetry_plugin_revision, version_major, version_minor, game (1 ETS2, 2 ATS)
  64  u32  common_ui.time_abs (in-game minutes)
 504  i32  truck_i.gear
 640  i32  gameplay_i.jobDeliveredEarnedXp
 948  f32  truck_f.speed (m/s); 952 engineRpm; 1056 truckOdometer (km)
1460  f32  gameplay_f.jobDeliveredDistanceKm
2200  f64  truck_dp.coordinateX/Y/Z (m), rotationX/Y/Z (heading, pitch, roll in turns, 0..1)
2300  char[64] config_s: truckBrand +64, truckName +192, cargo +320, cityDst +448, compDst +576,
      citySrc +704, compSrc +832; 3436 gameplay_s.fineOffence[32]
4200  i64  gameplay_ll: jobCancelledPenalty, jobDeliveredRevenue, fineAmount, tollgatePayAmount,
      ferryPayAmount, trainPayAmount
4300  bool special_b: onJob, jobFinished, jobCancelled, jobDelivered, fined, tollgate, ferry,
      train, refuel, refuelPayed
```

De wereldpositie van de truck is het wereldassenstelsel van SCS: x oost, y omhoog, z zuid, in meter (rechtshandig, y omhoog - de viewer tekent het zoals het is). Veerboten, treinen en het laden van een opgeslagen spel verplaatsen de truck zonder te rijden: daar wordt de route doorgeknipt.

Het volledige geheugen (de 32 KiB van de plugin: elke zone hierboven en de zones die niet gelezen worden - configuratie van de truck, wielen, slijtage, de andere kanalen van de truck, en wat de revisie na byte 4400 indeelt, de trailers) wordt telkens als het verandert bewaard in het ruwe bijbestand van de sessie, `type` `SCSTelemetry` met de `revision` ernaast - een pagina van een andere revisie ook, die ongewijzigd bewaard wordt in plaats van verkeerd gelezen.

De module werkt ook voor: [Euro Truck Simulator 2 (livegegevens)](game-ets2.md).

## Posities en assen {#positions-and-axes}

| | |
|---|---|
| Posities opgenomen | ja |
| Omhoog-as | `y` |
| Eenheden | meter (SCS-wereld: x oost, y omhoog, z zuid) |
| Gespiegeld voor de viewer | geen |
| Eenheidsschaal (`scale`: de viewer vermenigvuldigt posities ermee) | 1 |

Dit gaat in het `meta.json` (`axes`) van elke sessie en, als de sessie posities heeft, in de footer van `heat.parquet`. De 3DHeat-viewer draait en schaalt de rijen daardoor zelf - zie [De data](the-data.md).

## Multiplayer {#multiplayer}

- Gemarkeerd als online gespeeld (`multiplayer`): **ja**. `games --markdown` toont dit als "allowed (reads only what the game publishes)".
- Soort `telemetry`: hij leest alleen wat het spel of platform uitgeeft (een UDP-poort of gedeeld geheugen dat het spel publiceert), dus hij legt ook online spel vast; de vlag bepaalt alleen of geheugen ooit gelezen mag worden.
- Geheugen: **nooit** gelezen door deze adapter. Alleen `memory`-adapters lezen geheugen, en nooit voor een spel dat als online gespeeld is gemarkeerd - zie [Bronnen en regels](sources-and-rules.md).

## Opgenomen statistieken {#statistics-recorded}

Statistiekensleutels die de code van deze adapter bij naam instelt (elke `stats` van de sessie in `meta.json` en de tabel `stats` van `watcher.sqlite`):

`deliveries`, `distance_km`, `fines`, `fines_total`, `jobs_cancelled`, `max_speed_kmh`, `refuels`, `revenue`, `tolls_total`, `xp`

Een sleutel tussen accolades wordt tijdens het draaien ingevuld (`score.{team}` is één sleutel per team). Sleutels die de code uit een tabel met de velden van het spel of uit de eigen statistiekennamen van het spel haalt, staan niet in deze lijst; "Wat wordt opgenomen" hierboven noemt ze.

## Volledigheid {#completeness}

De watcher volgt de [converterregel](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md) van 3DHeat: wat de bron bevat wordt gelezen of bewaard, nooit weggegooid. Naast de rijen wordt elk pakket, elke pagina, regel of elk antwoord dat de adapter ontvangt, ongewijzigd bewaard in `heat.raw.parquet` van de sessie (kolommen `time`, `ms`, `type`, `used`, `payload`, `text`, plus elk veld dat op naam bewaard wordt; `used` markeert wat ook rijen werd). `selfCheck.completeness` in `meta.json` telt elk `type` - `lost` is 0.

**Gelezen**

- SDK- en pauzestatus, revisie van de plugin, spel en versie, tijd in het spel, de wereldpositie en koers van de truck, snelheid, kilometerteller, merk en naam van de truck, lading, bron- en bestemmingsstad en -bedrijf, opbrengst van de opdracht, XP en afstand, annuleringsboete, boetes en hun overtreding, tol, veerboten, treinen, de speciale gebeurtenisvlaggen (rijen, gebeurtenissen en statistieken)
- nu ook op de positierijen: `pitch` en `roll` (graden, uit de turns van de SDK), `gear` en `rpm`
- offsets gecontroleerd aan een veld-voor-veld overschrijving van de header van de plugin, revisie 12, waarvan de beginpunten van de zones in de tests vastliggen; nog niet tegen het spel

**Ruw bewaard**

- `SCSTelemetry`: het volledige geheugen van de plugin van 32 KiB, elke lezing waarvan de bytes verschillen van de kopie die als laatste bewaard is (`unchanged_reads` in meta.json telt de andere), met `revision` ernaast: elke zone - configuratie van truck en trailer, de kanalen van de truck (pedalen, stuur, brandstof, AdBlue, drukken, temperaturen, slijtage, lichten, wielen), positie- en versnellingsvectoren, tekst van opdracht en spel, en alles wat de revisie na byte 4400 indeelt (de trailers); `used` is waar zolang de SDK actief is en de revisie 12 is
- een pagina van een andere revisie van de plugin wordt helemaal bewaard met `used` op false, in plaats van verkeerd gelezen te worden

**Niet beschikbaar**

- alles wat de plugin niet uit de SDK kopieert, en alles terwijl de plugin niet geïnstalleerd is: het spel publiceert zelf geen telemetrie
- andere spelers' trucks in TruckersMP of konvooien: de SDK geeft alleen de truck van de speler zelf

**Grootte**: 32 KiB tot 10 keer per seconde tijdens het rijden (elke lezing verschilt dan): ongeveer 1,2 GB per uur voor compressie, één kopie tijdens pauze; het meeste van de pagina bestaat uit nullen en configuratie die niet verandert, dus zstd maakt hem vele keren kleiner (nog niet gemeten op een echte sessie)

## Getest {#verified}

getest op gedeeld geheugen dat is opgebouwd uit de header van revisie 12 van de plugin; nog niet getest tegen het spel

## Bron {#source}

[heat3d_watch/adapters/ets2.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/ets2.py)

<!-- Generated from the adapter by tools/gen_game_pages.py; change the adapter and run it again rather than editing this page. -->
