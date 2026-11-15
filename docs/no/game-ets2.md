---
title: "Euro Truck Simulator 2 (direkte data)"
nav_order: 19
lang: "no"
source: game-ets2.md
source_hash: "537f0daeedbf"
nav_exclude: true
search_exclude: true
---
# Euro Truck Simulator 2 (direkte data) {#euro-truck-simulator-2-live-data}

Mens du spiller Euro Truck Simulator 2, lagrer watcheren dataene spillet selv sender ut, slik at du senere kan se på dem på et kart i 3DHeat-vieweren.

*Tekniske detaljer: adapter `ets2`, type [`telemetry`](sources-and-rules.md); den kjører mens `eurotrucks2.exe` går og ser etter nye data hvert 0,1 s.*

## Hva som tas opp {#what-is-recorded}

- lastebilens posisjon i verden (x øst, y opp, z sør, m) 10 ganger i sekundet mens den kjører, hvert 5. sekund mens den står; retning, fart, kilometerteller
- jobber startet (last, fra, til), levert (inntekt, XP, km), avbrutt; bøter, bompenger, ferger, tog, drivstoffpåfyll
- ferger, tog og innlastede lagringer kutter ruten (teleport, spawn)
- distanse, toppfart, leveranser, inntekt, XP, bøter
- pluginens hele delte minne i `heat.raw.parquet`, hver gang det endrer seg

## Hvor det kommer fra {#where-it-comes-from}

delt minne Local\SCSTelemetry, skrevet av RenCloud scs-sdk-plugin (revisjon 12) i &lt;spill>\bin\win_x64\plugins

## Slik slår du det på {#how-to-switch-it-on}

installer scs-telemetry.dll (revisjon 12) fra github.com/RenCloud/scs-sdk-plugin i &lt;spill>\bin\win_x64\plugins; spillet spør én gang per start om å tillate SDK-en

## Slik fungerer det {#how-it-works}

Euro Truck Simulator 2 og American Truck Simulator: SCS' telemetri-SDK, gjennom RenCloud-pluginen.

SCS publiserer en telemetri-SDK (<https://modding.scssoft.com/wiki/Documentation/Engine/SDK/Telemetry>) for plugins spilleren legger i `<spill>\bin\win_x64\plugins\`. Spillet selv publiserer ingenting; den mye brukte pluginen fra <https://github.com/RenCloud/scs-sdk-plugin> (MIT) kopierer SDK-ens kanaler over i delt minne `Local\SCSTelemetry` (32 KiB), lagt ut i `scs-telemetry/inc/scs-telemetry-common.hpp`. Dette leser revisjon 12 av den layouten (PLUGIN_REVID 12) og ingenting annet: pluginen skriver sin revisjon ved forskyvning 40, og enhver annen revisjon leses ikke i stedet for å leses feil. Brukte forskyvninger (soner slik headeren angir dem; naturlig justering):

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

Lastebilens plassering i verden er SCS' verdensramme: x øst, y opp, z sør, meter (høyrehåndet, y opp - vieweren tegner den slik den er). Ferger, tog og innlasting av en lagring flytter lastebilen uten å kjøre: ruten kuttes der.

Hele området (pluginens 32 KiB: hver sone over, og de som ikke leses - lastebilens konfigurasjon, hjul, slitasje, lastebilens øvrige kanaler, og det revisjonen legger ut etter byte 4400, tilhengerne) tas vare på i øktens rå sidefil hver gang det endrer seg, `type` `SCSTelemetry` med `revision` ved siden av - en side av en annen revisjon tas også vare på hel i stedet for å leses feil.

Samme modul brukes også av: [American Truck Simulator (direkte data)](game-ats.md).

## Posisjoner og akser {#positions-and-axes}

| | |
|---|---|
| Posisjoner tatt opp | ja |
| Opp-akse | `y` |
| Enheter | meter (SCS-verden: x øst, y opp, z sør) |
| Speilet for vieweren | ingen |
| Enhetsskala (`scale`: vieweren ganger posisjonene med den) | 1 |

Disse legges i hver økts `meta.json` (`axes`) og, når økten har posisjoner, i `heat.parquet`s fotnote, slik at 3DHeat-vieweren selv vender og skalerer radene - se [Dataene](the-data.md).

## Flerspiller {#multiplayer}

- Merket som spilt på nett (`multiplayer`): **ja**. `games --markdown` viser dette som "tillatt (leser bare det spillet publiserer)".
- Type `telemetry`: den leser bare det spillet eller plattformen gir ut (en UDP-port eller delt minne spillet publiserer), så den tar opp også i nettspill, ikke bare frakoblet; flagget avgjør bare om minne noensinne får leses.
- Minne: **aldri** lest av denne adapteren. Bare `memory`-adaptere leser minne, og aldri for et spill merket som spilt på nett - se [Kilder og regler](sources-and-rules.md).

## Statistikk som registreres {#statistics-recorded}

Statistikknøkler som adapterens kode setter med navn (hver økts `stats` i `meta.json` og tabellen `stats` i `watcher.sqlite`):

`deliveries`, `distance_km`, `fines`, `fines_total`, `jobs_cancelled`, `max_speed_kmh`, `refuels`, `revenue`, `tolls_total`, `xp`

En nøkkel i klammer fullføres ved kjøretid (`score.{team}` er én nøkkel per lag). Nøkler som koden henter fra en tabell over spillets felt, eller fra spillets egne statistikknavn, står ikke på denne listen; "Hva som tas opp" over nevner dem.

## Fullstendighet {#completeness}

Watcheren følger 3DHeats [konverteringsregel](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md): det kilden inneholder, leses eller tas vare på, og slippes aldri. I tillegg til radene tas hver pakke, side, linje eller svar adapteren mottar, vare på hel i øktens `heat.raw.parquet` (kolonnene `time`, `ms`, `type`, `used`, `payload`, `text`, og alle felt tatt vare på med navn; `used` markerer det som også ble rader), og `meta.json`s `selfCheck.completeness` teller hver `type` - `lost` er 0.

**Leses**

- SDK- og pausestatus, pluginrevisjon, spill og versjon, tid i spillet, lastebilens posisjon i verden og retning, fart, kilometerteller, lastebilens merke og navn, last, by og firma for avsender og mottaker, jobbinntekt, XP og distanse, avbestillingsstraff, bøter og deres årsak, bompenger, ferger, tog, de spesielle hendelsesflaggene (rader, hendelser og statistikk)
- nå også på posisjonsradene: `pitch` og `roll` (grader, fra SDK-ens turns), `gear` og `rpm`
- forskyvninger kontrollert mot en felt-for-felt-overføring av pluginens revisjon 12-header, der sonestartene er kontrollert i testene; ikke ennå mot spillet

**Tatt vare på rått**

- `SCSTelemetry`: pluginens hele 32 KiB-område, hver lesing hvis bytes avviker fra kopien sist tatt vare på (`unchanged_reads` i meta.json teller de andre), `revision` ved siden av: hver sone - lastebils- og tilhengerkonfigurasjon, lastebilens kanaler (pedaler, styring, drivstoff, AdBlue, trykk, temperaturer, slitasje, lys, hjul), plasserings- og akselerasjonsvektorer, jobb- og spillstrenger, og alt revisjonen legger ut etter byte 4400 (tilhengerne); `used` er sann mens SDK-en er aktiv og revisjonen er 12
- en side av en annen pluginrevisjon tas vare på hel med `used` usann i stedet for å leses feil

**Ikke tilgjengelig**

- alt pluginen ikke kopierer ut av SDK-en, og alt mens pluginen ikke er installert: spillet publiserer ingen telemetri selv
- andre spilleres lastebiler i TruckersMP eller konvoier: SDK-en gir bare spillerens egen lastebil

**Størrelse**: 32 KiB opptil 10 ganger i sekundet mens man kjører (hver lesing avviker da): omtrent 1,2 GB i timen før komprimering, én kopi mens det er pause; mesteparten av siden er nuller og konfigurasjon som ikke endrer seg, så zstd krymper den mange ganger (ikke ennå målt på en ekte økt)

## Verifisert {#verified}

testet på delt minne bygd fra pluginens revisjon 12-headerlayout; ikke testet mot spillet

## Kilde {#source}

[heat3d_watch/adapters/ets2.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/ets2.py)

<!-- Generated from the adapter by tools/gen_game_pages.py; change the adapter and run it again rather than editing this page. -->
