---
title: "Euro Truck Simulator 2 (livedata)"
nav_order: 19
lang: "sv"
source: game-ets2.md
source_hash: "537f0daeedbf"
nav_exclude: true
search_exclude: true
---
# Euro Truck Simulator 2 (livedata) {#euro-truck-simulator-2-live-data}

När du kör Euro Truck Simulator 2 sparar watchern den data som spelet själv skickar ut, så att du senare kan titta på den på en karta i 3DHeat-visaren.

*Tekniska detaljer: adapter `ets2`, slag [`telemetry`](sources-and-rules.md); den körs medan `eurotrucks2.exe` är igång och letar efter ny data var 0,1 s.*

## Vad som spelas in {#what-is-recorded}

- lastbilens världsposition (x öster, y upp, z söder, m) 10 gånger per sekund medan den rör sig, var 5 s när den står still; riktning, hastighet, vägmätare
- uppdrag påbörjade (last, från, till), levererade (intäkt, XP, km), avbrutna; böter, vägtullar, färjor, tåg, tankningar
- färjor, tåg och inladdade sparningar bryter rutten (teleport, spawn)
- sträcka, högsta hastighet, leveranser, intäkt, XP, böter
- pluginens hela delade minne i `heat.raw.parquet`, varje gång det ändras

## Var datan kommer ifrån {#where-it-comes-from}

delat minne Local\SCSTelemetry skrivet av RenCloud scs-sdk-plugin (revision 12) i &lt;game>\bin\win_x64\plugins

## Så slår du på det {#how-to-switch-it-on}

installera scs-telemetry.dll (revision 12) från github.com/RenCloud/scs-sdk-plugin i &lt;game>\bin\win_x64\plugins; spelet frågar en gång per start om SDK:n får användas

## Så fungerar det {#how-it-works}

Euro Truck Simulator 2 och American Truck Simulator: SCS:s telemetri-SDK, via RenCloud-pluginen.

SCS publicerar en telemetri-SDK (<https://modding.scssoft.com/wiki/Documentation/Engine/SDK/Telemetry>) för plugin-program som spelaren lägger i `<game>\bin\win_x64\plugins\`. Spelet självt publicerar ingenting; den allmänt använda pluginen från <https://github.com/RenCloud/scs-sdk-plugin> (MIT) kopierar SDK:ns kanaler till delat minne `Local\SCSTelemetry` (32 KiB), med layouten i `scs-telemetry/inc/scs-telemetry-common.hpp`. Detta läser revision 12 av den layouten (PLUGIN_REVID 12) och ingenting annat: pluginen skriver sin revision vid offset 40, och varje annan revision lämnas oläst i stället för att läsas fel. Använda offset (zoner så som huvudet anger dem; naturlig justering):

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

Lastbilens placering i världen följer SCS:s världsram: x öster, y upp, z söder, meter (högerhänt, y upp - visaren ritar den som den är). Färjor, tåg och inladdning av en sparning flyttar lastbilen utan att köra: rutten bryts där.

Hela mappningen (pluginens 32 KiB: varje zon ovan och de som inte läses - lastbilens konfiguration, hjul, slitage, lastbilens övriga kanaler, och det revisionen lägger ut efter byte 4400, släpvagnarna) sparas i sessionens råa sidfil varje gång den ändras, `type` `SCSTelemetry` med `revision` bredvid - en sida av en annan revision också, den sparas helt i stället för att läsas fel.

Samma modul används också av: [American Truck Simulator (livedata)](game-ats.md).

## Positioner och axlar {#positions-and-axes}

| | |
|---|---|
| Positioner sparas | ja |
| Upp-axel | `y` |
| Enheter | meter (SCS-världen: x öster, y upp, z söder) |
| Speglad för visaren | ingen |
| Enhetsskala (`scale`: visaren multiplicerar positionerna med den) | 1 |

Dessa läggs i varje sessions `meta.json` (`axes`) och, när sessionen har positioner, i `heat.parquet`:s fotnot, så att 3DHeat-visaren vrider och skalar raderna själv - se [Datan](the-data.md).

## Flerspelarläge {#multiplayer}

- Markerat som spelat online (`multiplayer`): **ja**. `games --markdown` visar detta som "allowed (reads only what the game publishes)".
- Slag `telemetry`: den läser bara det spelet eller plattformen lämnar ut (en UDP-port eller delat minne som spelet publicerar), så den spelar in även i onlinespel som offline; flaggan avgör bara om minne någonsin får läsas.
- Minne: **aldrig** läst av den här adaptern. Bara `memory`-adaptrar läser minne, och aldrig för ett spel som är markerat som spelat online - se [Källor och regler](sources-and-rules.md).

## Statistik som sparas {#statistics-recorded}

Statistiknycklar som den här adapterns kod sätter med namn (varje sessions `stats` i `meta.json` och tabellen `stats` i `watcher.sqlite`):

`deliveries`, `distance_km`, `fines`, `fines_total`, `jobs_cancelled`, `max_speed_kmh`, `refuels`, `revenue`, `tolls_total`, `xp`

En nyckel i klammer fylls i vid körning (`score.{team}` är en nyckel per lag). Nycklar som koden tar från en tabell med spelets fält eller från spelets egna statistiknamn finns inte i listan; "Vad som spelas in" ovan nämner dem.

## Fullständighet {#completeness}

watchern följer 3DHeats [konverterarregel](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md): det källan innehåller läses eller sparas, aldrig slängs. Utöver raderna sparas varje paket, sida, rad eller svar som adaptern tar emot helt i sessionens `heat.raw.parquet` (kolumnerna `time`, `ms`, `type`, `used`, `payload`, `text` och sedan eventuella fält som sparats med namn; `used` markerar det som också blev rader), och `meta.json`:s `selfCheck.completeness` räknar varje `type` - `lost` är 0.

**Läses**

- SDK- och pausläge, pluginens revision, spel och version, tid i spelet, lastbilens världsposition och riktning, hastighet, vägmätare, lastbilens märke och namn, last, käll- och målstad och -företag, uppdragets intäkt, XP och sträcka, avbrottsstraff, böter och deras brott, vägtullar, färjor, tåg, de särskilda händelseflaggorna (rader, händelser och statistik)
- nu också på positionsraderna: `pitch` och `roll` (grader, från SDK:ns varv), `gear` och `rpm`
- offset kontrollerade mot en fält-för-fält-avskrift av pluginens revision 12-huvud, vars zonstarter är kontrollerade i testerna; ännu inte mot spelet

**Sparas råa**

- `SCSTelemetry`: pluginens hela 32 KiB-mappning, varje läsning vars byte skiljer sig från den senast sparade kopian (`unchanged_reads` i meta.json räknar de andra), med `revision` bredvid: varje zon - lastbilens och släpvagnens konfiguration, lastbilens kanaler (pedaler, styrning, bränsle, AdBlue, tryck, temperaturer, slitage, ljus, hjul), placerings- och accelerationsvektorer, uppdrags- och spelsträngar, och allt revisionen lägger ut efter byte 4400 (släpvagnarna); `used` är sann medan SDK:n är aktiv och revisionen är 12
- en sida av en annan pluginrevision sparas helt med `used` falskt i stället för att läsas fel

**Finns inte**

- allt pluginen inte kopierar ur SDK:n, och allt medan pluginen inte är installerad: spelet publicerar ingen egen telemetri
- andra spelares lastbilar i TruckersMP eller konvojer: SDK:n ger bara spelarens egen lastbil

**Storlek**: 32 KiB upp till 10 gånger per sekund under körning (varje läsning skiljer sig då): ungefär 1,2 GB per timme före komprimering, en kopia medan spelet är pausat; största delen av sidan är nollor och konfiguration som inte ändras, så zstd krymper den många gånger (ännu inte mätt på en verklig session)

## Verifierat {#verified}

testad på delat minne byggt från pluginens revision 12-huvudlayout; ännu inte testad mot spelet

## Källa {#source}

[heat3d_watch/adapters/ets2.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/ets2.py)

<!-- Generated from the adapter by tools/gen_game_pages.py; change the adapter and run it again rather than editing this page. -->
