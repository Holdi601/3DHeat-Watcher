---
title: "American Truck Simulator (live-data)"
nav_order: 1
lang: "da"
source: game-ats.md
source_hash: "974252b355da"
nav_exclude: true
search_exclude: true
---
# American Truck Simulator (live-data) {#american-truck-simulator-live-data}

Mens du spiller American Truck Simulator, gemmer watcheren de data, som spillet selv sender ud, så du senere kan se dem på et kort i 3DHeat-vieweren.

*Tekniske detaljer: adapter `ats`, type [`telemetry`](sources-and-rules.md); den kører, mens `amtrucks.exe` kører, og leder efter nye data hver 0.1 s.*

## Hvad der registreres {#what-is-recorded}

- lastbilens position i verden (x mod øst, y op, z mod syd, m) 10 gange i sekundet under kørsel, hver 5. sekund når den står stille; retning, hastighed, kilometertæller
- opgaver startet (fragt, fra, til), leveret (løn, XP, km), annulleret; bøder, broafgifter, færger, tog, tankninger
- færger, tog og indlæste gemte spil klipper ruten over (teleport, spawn)
- distance, topfart, leveringer, løn, XP, bøder
- pluginets hele delte hukommelse i `heat.raw.parquet`, hver gang den ændrer sig

## Hvor data kommer fra {#where-it-comes-from}

delt hukommelse Local\SCSTelemetry, skrevet af RenCloud scs-sdk-plugin (revision 12) i &lt;spil>\bin\win_x64\plugins

## Sådan slår du det til {#how-to-switch-it-on}

installér scs-telemetry.dll (revision 12) fra github.com/RenCloud/scs-sdk-plugin i &lt;spil>\bin\win_x64\plugins; spillet spørger én gang pr. start, om SDK'en må bruges

## Sådan virker det {#how-it-works}

Euro Truck Simulator 2 og American Truck Simulator: SCS' telemetri-SDK, via RenCloud-pluginet.

SCS udgiver en telemetri-SDK (<https://modding.scssoft.com/wiki/Documentation/Engine/SDK/Telemetry>)
til plugins, spilleren lægger i `<spil>\bin\win_x64\plugins\`. Selve spillet
udgiver intet; det udbredte plugin fra <https://github.com/RenCloud/scs-sdk-plugin>
(MIT) kopierer SDK'ens kanaler over i delt hukommelse `Local\SCSTelemetry`
(32 KiB), med layoutet i `scs-telemetry/inc/scs-telemetry-common.hpp`. Dette læser
revision 12 af det layout (PLUGIN_REVID 12) og intet andet: pluginet skriver sin
revision på forskydning 40, og enhver anden revision lades ulæst i stedet for
at blive læst forkert. Brugte forskydninger (zoner som headeren angiver dem; naturlig justering):

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

Lastbilens placering i verden følger SCS' verdensakser: x mod øst, y op, z mod syd, meter
(højrehåndet, y op - vieweren tegner den, som den er). Færger, tog og indlæsning af et gemt spil
flytter lastbilen uden at køre: ruten klippes der.

Hele mappingen (pluginets 32 KiB: alle zoner ovenfor og dem, der ikke læses -
lastbilens konfiguration, hjul, slid, lastbilens øvrige kanaler, og det revisionen
lægger efter byte 4400, anhængerne) gemmes i kørslens rå sidefil, hver gang den ændrer sig,
`type` `SCSTelemetry` med `revision` ved siden af - en side fra en anden
revision gemmes også hel i stedet for at blive læst forkert.

Det samme modul bruges også af: [Euro Truck Simulator 2 (live-data)](game-ets2.md).

## Positioner og akser {#positions-and-axes}

| | |
|---|---|
| Positioner registreret | ja |
| Op-akse | `y` |
| Enheder | meter (SCS-verden: x mod øst, y op, z mod syd) |
| Spejlet til vieweren | ingen |
| Enhedsskala (`scale`: vieweren ganger positionerne med den) | 1 |

Disse går ind i hver kørsels `meta.json` (`axes`) og, når kørslen har positioner, i `heat.parquet`s footer, så 3DHeat-vieweren selv drejer og skalerer rækkerne - se [Dataene](the-data.md).

## Flerspiller {#multiplayer}

- Markeret som spillet online (`multiplayer`): **ja**. `games --markdown` viser det som "tilladt (læser kun det spillet udgiver)".
- Type `telemetry`: den læser kun det spillet eller platformen udleverer (en UDP-port eller delt hukommelse spillet udgiver), så den optager også i onlinespil og offline; flaget afgør kun, om hukommelse nogensinde må læses.
- Hukommelse: læses **aldrig** af denne adapter. Kun `memory`-adaptere læser hukommelse, og aldrig for et spil markeret som spillet online - se [Kilder og regler](sources-and-rules.md).

## Registrerede statistikker {#statistics-recorded}

Statistiknøgler, som adapterens kode sætter ved navn (hver kørsels `stats` i `meta.json` og tabellen `stats` i `watcher.sqlite`):

`deliveries`, `distance_km`, `fines`, `fines_total`, `jobs_cancelled`, `max_speed_kmh`, `refuels`, `revenue`, `tolls_total`, `xp`

En nøgle i klammer udfyldes under kørslen (`score.{team}` er én nøgle pr. hold). Nøgler som koden tager fra en tabel over spillets felter eller fra spillets egne statistiknavne står ikke på listen; "Hvad der registreres" ovenfor nævner dem.

## Fuldstændighed {#completeness}

Watcheren følger 3DHeats [konverterregel](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md): det kilden indeholder, læses eller gemmes, og aldrig smides væk. Ud over rækkerne gemmes hver pakke, side, linje eller svar, adapteren modtager, hel i kørslens `heat.raw.parquet` (kolonnerne `time`, `ms`, `type`, `used`, `payload`, `text` og derefter felter, der gemmes under deres navn; `used` markerer, hvad der også blev til rækker), og `selfCheck.completeness` i `meta.json` tæller hver `type` - `lost` er 0.

**Læst**

- SDK- og pausetilstand, pluginets revision, spil og version, tid i spillet, lastbilens position i verden og retning, hastighed, kilometertæller, lastbilens mærke og navn, fragt, afhentnings- og leveringsby og -firma, opgavens løn, XP og distance, annulleringsstraf, bøder og deres forseelse, broafgifter, færger, tog, de særlige hændelsesflag (rækker, hændelser og statistik)
- nu også på positionsrækkerne: `pitch` og `roll` (grader, ud fra SDK'ens omdrejninger), `gear` og `rpm`
- forskydningerne kontrolleret mod en felt-for-felt-udskrift af pluginets revision 12-header, hvis zonestarter testene verificerer; endnu ikke mod spillet

**Gemt råt**

- `SCSTelemetry`: pluginets hele 32 KiB-mapping, hver læsning hvis bytes afviger fra den kopi, der sidst blev gemt (`unchanged_reads` i meta.json tæller de øvrige), med `revision` ved siden af: hver zone - lastbilens og anhængerens konfiguration, lastbilens kanaler (pedaler, styring, brændstof, AdBlue, tryk, temperaturer, slid, lys, hjul), placerings- og accelerationsvektorer, opgave- og spilstrenge, og alt det revisionen lægger efter byte 4400 (anhængerne); `used` er sand, mens SDK'en er aktiv og revisionen er 12
- en side fra en anden plugin-revision gemmes hel med `used` falsk i stedet for at blive læst forkert

**Ikke tilgængeligt**

- alt, pluginet ikke kopierer ud af SDK'en, og alt, mens pluginet ikke er installeret: spillet udgiver ingen egen telemetri
- andre spilleres lastbiler i TruckersMP eller konvojer: SDK'en giver kun spillerens egen lastbil

**Størrelse**: 32 KiB op til 10 gange i sekundet under kørsel (hver læsning afviger da): cirka 1,2 GB i timen før komprimering, én kopi under pause; det meste af siden er nuller og konfiguration, der ikke ændrer sig, så zstd gør den mange gange mindre (endnu ikke målt på en rigtig kørsel)

## Verificeret {#verified}

testet på delt hukommelse bygget ud fra pluginets revision 12-headerlayout; ikke testet mod spillet

## Kilde {#source}

[heat3d_watch/adapters/ets2.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/ets2.py)

<!-- Genereret fra adapteren af tools/gen_game_pages.py; ret adapteren og kør den igen i stedet for at redigere denne side. -->
