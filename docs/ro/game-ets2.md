---
title: "Euro Truck Simulator 2 (date în direct)"
nav_order: 19
lang: "ro"
source: game-ets2.md
source_hash: "537f0daeedbf"
nav_exclude: true
search_exclude: true
---
# Euro Truck Simulator 2 (date în direct) {#euro-truck-simulator-2-live-data}

Cât timp jucați Euro Truck Simulator 2, watcher-ul salvează datele pe care jocul însuși le trimite, ca să le puteți vedea mai târziu pe o hartă în vizualizatorul 3DHeat.

*Detalii tehnice: adaptorul `ets2`, tipul [`telemetry`](sources-and-rules.md); rulează cât timp `eurotrucks2.exe` rulează și caută date noi la fiecare 0,1 s.*

## Ce se înregistrează {#what-is-recorded}

- poziția camionului în lume (x est, y sus, z sud, m) la 10 Hz cât timp se mișcă, la fiecare 5 s cât timp stă pe loc; direcția, viteza, odometrul
- joburi începute (marfă, de unde, unde), livrate (venit, XP, km), anulate; amenzi, taxe de trecere, feriboturi, trenuri, realimentări
- feriboturile, trenurile și salvările încărcate taie traseul (teleport, spawn)
- distanța, viteza maximă, livrări, venit, XP, amenzi
- toată memoria partajată a plugin-ului în `heat.raw.parquet`, de fiecare dată când se schimbă

## De unde vine {#where-it-comes-from}

memoria partajată Local\SCSTelemetry scrisă de pluginul RenCloud scs-sdk-plugin (revizia 12) în &lt;game>\bin\win_x64\plugins

## Cum se activează {#how-to-switch-it-on}

instalați scs-telemetry.dll (revizia 12) de la github.com/RenCloud/scs-sdk-plugin în &lt;game>\bin\win_x64\plugins; jocul întreabă o dată la fiecare pornire dacă permite SDK-ul

## Cum funcționează {#how-it-works}

Euro Truck Simulator 2 și American Truck Simulator: SDK-ul de telemetrie SCS, prin pluginul RenCloud.

SCS publică un SDK de telemetrie (<https://modding.scssoft.com/wiki/Documentation/Engine/SDK/Telemetry>) pentru pluginurile pe care jucătorul le pune în `<game>\bin\win_x64\plugins\`. Jocul în sine nu publică nimic; pluginul larg folosit de la <https://github.com/RenCloud/scs-sdk-plugin> (MIT) copiază canalele SDK-ului în memoria partajată `Local\SCSTelemetry` (32 KiB), aranjată după `scs-telemetry/inc/scs-telemetry-common.hpp`. Acesta citește revizia 12 a acelui layout (PLUGIN_REVID 12) și nimic altceva: pluginul își scrie revizia la offsetul 40, iar orice altă revizie rămâne necitită, în loc să fie citită greșit. Offsetele folosite (zonele, așa cum le marchează antetul; aliniere naturală):

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

Plasarea camionului în lume este cea a sistemului de coordonate SCS: x est, y sus, z sud, metri (dreptunghic, y în sus - vizualizatorul îl desenează așa cum este). Feriboturile, trenurile și încărcarea unei salvări mută camionul fără să conducă: traseul se taie acolo.

Toată mapa (cei 32 KiB ai pluginului: fiecare zonă de mai sus și cele necitite - configurația camionului, roțile, uzura, celelalte canale ale camionului, și ce așază revizia după octetul 4400, remorcile) este păstrată în sidecar-ul brut al sesiunii de fiecare dată când se schimbă, cu `type` `SCSTelemetry` și `revision` alături - o pagină a unei alte revizii, păstrată întreagă în loc să fie citită greșit.

Același modul servește și: [American Truck Simulator (date în direct)](game-ats.md).

## Poziții și axe {#positions-and-axes}

| | |
|---|---|
| Poziții înregistrate | da |
| Axa verticală | `y` |
| Unități | metri (lumea SCS: x est, y sus, z sud) |
| Oglindit pentru vizualizator | niciunul |
| Scara unității (`scale`: vizualizatorul înmulțește pozițiile cu ea) | 1 |

Acestea intră în `meta.json` al fiecărei sesiuni (`axes`) și, când sesiunea are poziții, în subsolul `heat.parquet`, ca vizualizatorul 3DHeat să rotească și să scaleze rândurile singur; vedeți [Datele](the-data.md).

## Multiplayer {#multiplayer}

- Marcat ca jucat online (`multiplayer`): **da**. `games --markdown` arată asta ca „permis (citește doar ce publică jocul)”.
- Tipul `telemetry`: citește doar ce oferă jocul sau platforma (un port UDP sau memoria partajată pe care o publică jocul), deci înregistrează și în jocul online, nu doar offline; marcajul decide doar dacă memoria poate fi citită vreodată.
- Memoria: **niciodată** citită de acest adaptor. Doar adaptoarele de tip `memory` citesc memoria, și niciodată pentru un joc marcat ca jucat online; vedeți [Surse și reguli](sources-and-rules.md).

## Statistici înregistrate {#statistics-recorded}

Cheile de statistici pe care codul adaptorului le setează pe nume (fiecare `stats` din sesiune, în `meta.json`, și tabelul `stats` din `watcher.sqlite`):

`deliveries`, `distance_km`, `fines`, `fines_total`, `jobs_cancelled`, `max_speed_kmh`, `refuels`, `revenue`, `tolls_total`, `xp`

O cheie între acolade se completează la rulare (`score.{team}` este câte o cheie pentru fiecare echipă). Cheile pe care codul le ia dintr-un tabel de câmpuri ale jocului sau din numele statisticilor proprii ale jocului nu sunt în listă; „Ce se înregistrează” de mai sus le numește.

## Completitudine {#completeness}

Watcher-ul urmează regula de convertor a 3DHeat: ce conține sursa este citit sau păstrat, niciodată eliminat. Pe lângă rânduri, fiecare pachet, pagină, linie sau răspuns pe care îl primește adaptorul este păstrat întreg în `heat.raw.parquet` al sesiunii (coloanele `time`, `ms`, `type`, `used`, `payload`, `text`, apoi orice câmp păstrat pe nume; `used` marchează ce a devenit și rând), iar `selfCheck.completeness` din `meta.json` numără fiecare `type`; `lost` este 0.

**Citit**

- SDK-ul și starea de pauză, revizia pluginului, jocul și versiunea, ora din joc, poziția și direcția camionului în lume, viteza, odometrul, marca și numele camionului, marfa, orașul și compania de plecare și de destinație, venitul jobului, XP și distanța, penalizarea de anulare, amenzile și motivul lor, taxele, feriboturile, trenurile, indicatorii speciali de eveniment (rânduri, evenimente și statistici)
- acum și pe rândurile de poziție: `pitch` și `roll` (grade, din rotațiile SDK), `gear` și `rpm`
- decalajele verificate față de o transcriere câmp cu câmp a antetului pluginului, revizia 12, al cărui început de zone este verificat în teste; încă nu față de joc

**Păstrat brut**

- `SCSTelemetry`: toată mapa de 32 KiB a pluginului, la fiecare citire ale cărei octeți diferă de copia păstrată ultima dată (`unchanged_reads` din meta.json numără celelalte), cu `revision` alături: fiecare zonă - configurația camionului și a remorcii, canalele camionului (pedalele, direcția, combustibilul, AdBlue, presiunile, temperaturile, uzura, luminile, roțile), vectorii de poziție și accelerație, șirurile de joburi și de joc și tot ce layout-ul reviziei așază după octetul 4400 (remorcile); `used` este adevărat cât timp SDK-ul este activ și revizia este 12
- o pagină a unei alte revizii de plugin este păstrată întreagă, cu `used` fals, în loc să fie citită greșit

**Nu este disponibil**

- orice nu copiază pluginul din SDK, și tot ce cât timp pluginul nu este instalat: jocul nu publică telemetrie proprie
- camioanele altor jucători din TruckersMP sau din convoaie: SDK-ul dă doar camionul jucătorului

**Dimensiune**: 32 KiB până la de 10 ori pe secundă în timpul condusului (fiecare citire diferă atunci): aproximativ 1,2 GB pe oră înainte de compresie, o singură copie pe pauză; cea mai mare parte a paginii este zerouri și configurație care nu se schimbă, deci zstd o micșorează de multe ori (nemăsurat încă pe o sesiune reală)

## Verificat {#verified}

testat pe memorie partajată construită după antetul pluginului, revizia 12; netestat cu jocul

## Sursă {#source}

[heat3d_watch/adapters/ets2.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/ets2.py)

<!-- Generated from the adapter by tools/gen_game_pages.py; change the adapter and run it again rather than editing this page. -->
