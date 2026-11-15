---
title: "American Truck Simulator (të dhëna live)"
nav_order: 1
lang: "sq"
source: game-ats.md
source_hash: "974252b355da"
nav_exclude: true
search_exclude: true
---
# American Truck Simulator (të dhëna live) {#american-truck-simulator-live-data}

Ndërsa luan American Truck Simulator, watcher ruan të dhënat që vetë loja i dërgon, që t'i shohësh më vonë në një hartë në shikuesin 3DHeat.

*Detaje teknike: adaptori `ats`, lloji [`telemetry`](sources-and-rules.md); punon sa kohë `amtrucks.exe` është duke u ekzekutuar dhe kërkon të dhëna të reja çdo 0.1 s.*

## Çfarë regjistrohet {#what-is-recorded}

- pozicioni i kamionit në botë (x lindje, y lart, z jug, m) me 10 Hz kur lëviz, çdo 5 s kur qëndron; drejtimi, shpejtësia, odometri
- punët e nisura (ngarkesa, nga, deri), të dorëzuara (të ardhura, XP, km), të anuluara; gjobat, pagesat e rrugës, tragetet, trenat, mbushjet me karburant
- tragetet, trenat dhe ruajtjet e ngarkuara e presin rrugën (teleport, spawn)
- distanca, shpejtësia maksimale, dorëzimet, të ardhurat, XP, gjobat
- e gjithë memoria e përbashkët e plugin-it te `heat.raw.parquet`, sa herë që ndryshon

## Nga vjen {#where-it-comes-from}

memoria e përbashkët Local\SCSTelemetry e shkruar nga plugin-i scs-sdk-plugin i RenCloud (rishikimi 12) te &lt;game>\bin\win_x64\plugins

## Si ta ndezësh {#how-to-switch-it-on}

instalo scs-telemetry.dll (rishikimi 12) nga github.com/RenCloud/scs-sdk-plugin te &lt;game>\bin\win_x64\plugins; loja pyet një herë në çdo nisje nëse lejohet SDK-ja

## Si funksionon {#how-it-works}

Euro Truck Simulator 2 dhe American Truck Simulator: SDK-ja e telemetrisë së SCS, nëpërmjet plugin-it të RenCloud.

SCS publikon një SDK telemetrie (<https://modding.scssoft.com/wiki/Documentation/Engine/SDK/Telemetry>)
për plugin-e që lojtari i vendos te `<game>\bin\win_x64\plugins\`. Vetë loja
nuk publikon asgjë; plugin-i i përdorur gjerësisht nga <https://github.com/RenCloud/scs-sdk-plugin>
(MIT) i kopjon kanalet e SDK-së në memorien e përbashkët `Local\SCSTelemetry`
(32 KiB), të vendosur sipas `scs-telemetry/inc/scs-telemetry-common.hpp`. Ky lexon
rishikimin 12 të asaj strukture (PLUGIN_REVID 12) dhe asgjë tjetër: plugin-i
e shkruan rishikimin e vet në zhvendosjen 40, dhe çdo rishikim tjetër lihet pa lexuar në vend që
të lexohet gabim. Zhvendosjet e përdorura (zonat siç i shënon header-i; shtrirje natyrale):

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

Vendosja e kamionit në botë është kuadri i botës së SCS: x lindje, y lart, z jug, metra
(me dorë të djathtë, y lart - shikuesi e vizaton siç është). Tragetet, trenat dhe ngarkimi
i një ruajtjeje e lëvizin kamionin pa e drejtuar: rruga pritet aty.

I gjithë mapimi (32 KiB i plugin-it: çdo zonë më sipër dhe ato që nuk lexohen -
konfigurimi i kamionit, rrotat, konsumimi, kanalet e tjera të kamionit, dhe
çfarë vendos rishikimi pas bajtit 4400, rimorkiot) ruhet te skedari anësor i papërpunuar i sesionit sa herë që ndryshon,
`type` `SCSTelemetry` me `revision` pranë tij - edhe faqja e një rishikimi tjetër,
që ruhet e plotë në vend që të lexohet gabim.

Të njëjtin modul e përdorin edhe: [Euro Truck Simulator 2 (të dhëna live)](game-ets2.md).

## Pozicionet dhe boshtet {#positions-and-axes}

| | |
|---|---|
| Pozicionet e regjistruara | po |
| Boshti lart | `y` |
| Njësitë | metra (bota SCS: x lindje, y lart, z jug) |
| Pasqyruar për shikuesin | asnjë |
| Shkalla e njësisë (`scale`: shikuesi i shumëzon pozicionet me të) | 1 |

Këto hyjnë te `meta.json` i çdo sesioni (`axes`) dhe, kur sesioni ka pozicione, te fundi (footer) i `heat.parquet`, kështu që shikuesi 3DHeat i rrotullon dhe i shkallëzon rreshtat vetë - shih [Të dhënat](the-data.md).

## Lojë me shumë lojtarë {#multiplayer}

- Shënuar si lojë që luhet online (`multiplayer`): **po**. `games --markdown` e shfaq këtë si "allowed (reads only what the game publishes)".
- Lloji `telemetry`: lexon vetëm atë që loja ose platforma e jep vetë (një port UDP ose memorie e përbashkët që loja e publikon), kështu që regjistron si në lojën online ashtu edhe offline; shenja vendos vetëm nëse memoria lejohet ndonjëherë të lexohet.
- Memoria: **asnjëherë** nuk lexohet nga ky adaptor. Vetëm adaptorët `memory` lexojnë memorie, dhe kurrë për një lojë të shënuar si e luajtur online - shih [Burimet dhe rregullat](sources-and-rules.md).

## Statistikat e regjistruara {#statistics-recorded}

Çelësat e statistikave që kodi i këtij adaptori i vendos me emër (`stats` i çdo sesioni te `meta.json` dhe tabela `stats` e `watcher.sqlite`):

`deliveries`, `distance_km`, `fines`, `fines_total`, `jobs_cancelled`, `max_speed_kmh`, `refuels`, `revenue`, `tolls_total`, `xp`

Një çelës në kllapa gjarpërore plotësohet gjatë punës (`score.{team}` është një çelës për çdo ekip). Çelësat që kodi i merr nga një tabelë me fushat e lojës ose nga emrat e statistikave të vetë lojës nuk janë në këtë listë; "Çfarë regjistrohet" më sipër i emërton.

## Plotësia {#completeness}

Watcher ndjek [rregullin e konvertuesit](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md) të 3DHeat: çfarë mban burimi lexohet ose ruhet, kurrë nuk hidhet. Përveç rreshtave, çdo paketë, faqe, rresht ose përgjigje që e merr adaptori ruhet e plotë te `heat.raw.parquet` i sesionit (kolonat `time`, `ms`, `type`, `used`, `payload`, `text`, pastaj çdo fushë e ruajtur me emër; `used` shënon çfarë u bë edhe rreshta), dhe `selfCheck.completeness` i `meta.json` numëron çdo `type` - `lost` është 0.

**Lexuar**

- gjendja e SDK-së dhe e pauzës, rishikimi i plugin-it, loja dhe versioni, ora brenda lojës, pozicioni dhe drejtimi i kamionit në botë, shpejtësia, odometri, marka dhe emri i kamionit, ngarkesa, qyteti dhe kompania e burimit dhe e destinacionit, të ardhurat, XP dhe distanca e punës, gjoba e anulimit, gjobat dhe shkelja e tyre, pagesat e rrugës, tragetet, trenat, shenjat e ngjarjeve të veçanta (rreshta, ngjarje dhe statistika)
- tani edhe te rreshtat e pozicionit: `pitch` dhe `roll` (gradë, nga rrotullimet e SDK-së), `gear` dhe `rpm`
- zhvendosjet u kontrolluan me një transkriptim fushë për fushë të header-it të rishikimit 12 të plugin-it, ku fillimet e zonave verifikohen në teste; ende jo me lojën

**Ruajtur të papërpunuara**

- `SCSTelemetry`: i gjithë mapimi 32 KiB i plugin-it, çdo lexim që bajtet e tij ndryshojnë nga kopja e ruajtur së fundi (`unchanged_reads` te meta.json numëron të tjerët), `revision` pranë tij: çdo zonë - konfigurimi i kamionit dhe i rimorkiove, kanalet e kamionit (pedalet, timoni, karburanti, AdBlue, presionet, temperaturat, konsumimi, dritat, rrotat), vektorët e vendosjes dhe të nxitimit, vargjet e punës dhe të lojës, dhe çdo gjë që rishikimi vendos pas bajtit 4400 (rimorkiot); `used` është e vërtetë sa kohë SDK-ja është aktive dhe rishikimi është 12
- faqja e një rishikimi tjetër të plugin-it ruhet e plotë me `used` të rremë në vend që të lexohet gabim

**Nuk ofrohet**

- çdo gjë që plugin-i nuk e kopjon nga SDK-ja, dhe çdo gjë kur plugin-i nuk është i instaluar: loja nuk publikon telemetri të vetën
- kamionët e lojtarëve të tjerë në TruckersMP ose në konvoje: SDK-ja jep vetëm kamionin e vetë lojtarit

**Madhësia**: 32 KiB deri në 10 herë në sekondë gjatë drejtimit (atëherë çdo lexim ndryshon): rreth 1.2 GB në orë para kompresimit, një kopje gjatë pauzës; pjesa më e madhe e faqes janë zero dhe konfigurim që nuk ndryshon, kështu që zstd e zvogëlon shumë herë (ende i pamatur në një sesion të vërtetë)

## Verifikuar {#verified}

i provuar me memorie të përbashkët të ndërtuar sipas strukturës së header-it të rishikimit 12 të plugin-it; i paprovuar me lojën

## Burimi {#source}

[heat3d_watch/adapters/ets2.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/ets2.py)

<!-- Generated from the adapter by tools/gen_game_pages.py; change the adapter and run it again rather than editing this page. -->
