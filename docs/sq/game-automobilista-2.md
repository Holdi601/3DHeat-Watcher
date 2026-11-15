---
title: "Automobilista 2 (të dhëna live)"
nav_order: 6
lang: "sq"
source: game-automobilista-2.md
source_hash: "5e3ca1507524"
nav_exclude: true
search_exclude: true
---
# Automobilista 2 (të dhëna live) {#automobilista-2-live-data}

Ndërsa luan Automobilista 2, watcher ruan të dhënat që vetë loja i dërgon, që t'i shohësh më vonë në një hartë në shikuesin 3DHeat.

*Detaje teknike: adaptori `automobilista-2`, lloji [`telemetry`](sources-and-rules.md); punon sa kohë `AMS2AVX.exe` ose `AMS2.exe` është duke u ekzekutuar dhe kërkon të dhëna të reja çdo 0.1 s.*

## Çfarë regjistrohet {#what-is-recorded}

- pozicioni i çdo makine (XYZ në botë, m) me 10 Hz sipas emrit të shoferit, makina jote e shënuar, me shpejtësinë dhe pozicionin në garë; marshi, gazi, frena i tu
- fillimi i sesionit me pistën që e emërton loja; xhirot për çdo makinë me kohën e xhiros; mbarimet; ndalesat e tua te pit-et
- teleportimet (kthimi te pit-et, një rinisje): `teleport` ku ishte makina, `spawn` ku është tani
- xhirot e tua, xhiroja më e mirë, pozicioni në garë, distanca, shpejtësia maksimale
- e gjithë faqja e memories së përbashkët të lojës te `heat.raw.parquet`, sa herë që ndryshon

## Nga vjen {#where-it-comes-from}

memoria e përbashkët $pcars2$ (struktura SharedMemory.h e SMS)

## Si ta ndezësh {#how-to-switch-it-on}

Në lojë: Options > System > Shared Memory: "Project CARS 2"

## Si funksionon {#how-it-works}

Memoria e përbashkët që lojërat e garave e publikojnë për tabela treguesish, e hapur vetëm për lexim - dhe
kurrë e krijuar.

Disa simulatorë e ndajnë telemetrinë e tyre si një mapim skedari Windows me emër që e krijon
loja dhe që çdokush mund ta lexojë: faqet `Local\acpmf_*` të Kunos (Assetto Corsa,
ACC, AC Rally, `Local\acevo_pmf_*` i AC EVO), `Local\IRSDKMemMapFileName` i iRacing,
`$R3E` i RaceRoom, `$pcars2$` i Automobilista 2 / Project CARS 2.

Pse jo `mmap.mmap(-1, size, tagname=...)`, mënyra e zakonshme në Python: kur
mapimi nuk ekziston ende, ai e *krijon* një - këtu, vetëm për lexim. Një lojë
e nisur pas kësaj e hap mapimin e watcher-it në vend që të bëjë të vetin dhe
pastaj nuk mund të shkruajë në të, kështu që telemetria e saj është e vdekur derisa watcher ta lëshojë.
Watcher e nis një adaptor sapo shfaqet procesi i lojës, që është
pikërisht momenti kur loja nuk e ka bërë ende mapimin e vet. Prandaj ky hapet me
`OpenFileMappingW`, që gjen vetëm një mapim ekzistues, e mapon me
`FILE_MAP_READ`, dhe në të kundërt raporton "ende nuk është aty"; adaptorët provojnë sërish
pak më vonë.

Këtu asgjë nuk mund të shkruajë: pamja mapohet vetëm për lexim dhe kopjohet jashtë
vetëm me `ctypes.string_at`.

Dy lojëra lexohen edhe këtu; çdo makinë në pistë është në faqet e tyre.

#### Automobilista 2 / Project CARS 2 - `$pcars2$` {#automobilista-2--project-cars-2---pcars2}

`SharedMemory.h` i SMS (në dorëzim në dosjen Support\SharedMemory të lojës;
AMS2: Options > System > Shared Memory "Project CARS 2"), `#pragma pack(4)`.
`mParticipantInfo[64]` nga bajti 28, nga 100 bajte secili: mIsActive, mName[64],
mWorldPosition[3] (m, Y lart), mCurrentLapDistance, mRacePosition,
mLapsCompleted, mCurrentLap, mCurrentSector; mViewedParticipantIndex (20)
është makina e lojtarit; për çdo pjesëmarrës mLastLapTimes (9200), mRaceStates
(9520), mSpeeds (10800); mBestLapTime (6716), mLastLapTime
(6720), mSpeed (6848), mBrake, mThrottle, mGear të lojtarit; mSequenceNumber (7320) është
tek sa kohë loja shkruan. Zhvendosjet u nxorën nga dy
kopje të pavarura të header-it (kopja e vetë lojës nuk është e instaluar
këtu), që përputhen.

Të dyja faqet ruhen edhe të plota (docs/converters.md, "Live sources"): i
gjithë mapimi, çdo lexim që bajtet e tij ndryshojnë nga kopja e ruajtur së fundi, te
skedari anësor i papërpunuar i sesionit nën `type` `r3e` ose `pcars2` - çdo vend shoferi dhe
çdo fushë e strukturës, edhe ato që nuk lexohen këtu, kështu që një dekoder i mëvonshëm
ka nevojë vetëm për skedarin anësor.

Të njëjtin modul e përdorin edhe: [Project CARS 2 (të dhëna live)](game-project-cars-2.md), [RaceRoom Racing Experience (të dhëna live)](game-raceroom.md).

## Pozicionet dhe boshtet {#positions-and-axes}

| | |
|---|---|
| Pozicionet e regjistruara | po |
| Boshti lart | `y` |
| Njësitë | metra |
| Pasqyruar për shikuesin | asnjë |
| Shkalla e njësisë (`scale`: shikuesi i shumëzon pozicionet me të) | 1 |

Këto hyjnë te `meta.json` i çdo sesioni (`axes`) dhe, kur sesioni ka pozicione, te fundi (footer) i `heat.parquet`, kështu që shikuesi 3DHeat i rrotullon dhe i shkallëzon rreshtat vetë - shih [Të dhënat](the-data.md).

## Lojë me shumë lojtarë {#multiplayer}

- Shënuar si lojë që luhet online (`multiplayer`): **po**. `games --markdown` e shfaq këtë si "allowed (reads only what the game publishes)".
- Lloji `telemetry`: lexon vetëm atë që loja ose platforma e jep vetë (një port UDP ose memorie e përbashkët që loja e publikon), kështu që regjistron si në lojën online ashtu edhe offline; shenja vendos vetëm nëse memoria lejohet ndonjëherë të lexohet.
- Memoria: **asnjëherë** nuk lexohet nga ky adaptor. Vetëm adaptorët `memory` lexojnë memorie, dhe kurrë për një lojë të shënuar si e luajtur online - shih [Burimet dhe rregullat](sources-and-rules.md).

## Statistikat e regjistruara {#statistics-recorded}

Çelësat e statistikave që kodi i këtij adaptori i vendos me emër (`stats` i çdo sesioni te `meta.json` dhe tabela `stats` e `watcher.sqlite`):

`best_lap`, `distance_km`, `finishes`, `incidents`, `laps`, `pit_stops`, `race_position`, `top_speed_kmh`

Një çelës në kllapa gjarpërore plotësohet gjatë punës (`score.{team}` është një çelës për çdo ekip). Çelësat që kodi i merr nga një tabelë me fushat e lojës ose nga emrat e statistikave të vetë lojës nuk janë në këtë listë; "Çfarë regjistrohet" më sipër i emërton.

## Plotësia {#completeness}

Watcher ndjek [rregullin e konvertuesit](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md) të 3DHeat: çfarë mban burimi lexohet ose ruhet, kurrë nuk hidhet. Përveç rreshtave, çdo paketë, faqe, rresht ose përgjigje që e merr adaptori ruhet e plotë te `heat.raw.parquet` i sesionit (kolonat `time`, `ms`, `type`, `used`, `payload`, `text`, pastaj çdo fushë e ruajtur me emër; `used` shënon çfarë u bë edhe rreshta), dhe `selfCheck.completeness` i `meta.json` numëron çdo `type` - `lost` është 0.

**Lexuar**

- për çdo pjesëmarrës (deri në 64): aktiv, emri, pozicioni në botë, pozicioni në garë, xhirot e përfunduara; koha e xhiros së fundi, gjendja e garës dhe shpejtësia e tij
- makina e lojtarit (mViewedParticipantIndex), gjendja e lojës dhe e sesionit, vendndodhja dhe varianti i pistës, xhiroja më e mirë dhe e fundit, shpejtësia, frena, gazi, marshi; mSequenceNumber për të anashkaluar një kopje të kapur mes shkrimit
- zhvendosjet nga dy kopje të pavarura të SharedMemory.h të SMS që përputhen, të kontrolluara me një faqe të ndërtuar prej tyre në teste; ende jo me lojën

**Ruajtur të papërpunuara**

- `pcars2`: i gjithë mapimi $pcars2$ - struktura vazhdon shumë përtej 11,312 bajteve që lexohen këtu - çdo lexim që bajtet e tij ndryshojnë nga kopja e ruajtur së fundi: orientimi i çdo pjesëmarrësi, kohët e sektorëve, emrat e makinave dhe të klasave, mënyrat dhe shenjat e pit-eve, fizika e lojtarit, gomat, pezullimi, dëmtimet, moti dhe gjithçka që versionet e mëvonshme të Automobilista 2 i shtuan
- `used` është e vërtetë për një faqe të lexuar në rreshta; e rreme për një në meny, në pauzë, në riluajtje, të një strukture tjetër, ose të kapur mes shkrimit (`torn` 1); `unchanged_reads` te meta.json numëron leximet që ishin bajt për bajt si kopja e ruajtur më parë

**Nuk ofrohet**

- hyrjet dhe fizika e pjesëmarrësve të tjerë: faqja jep vetëm makinën që shihet
- gjithçka sa kohë opsioni i memories së përbashkët të lojës është i fikur (Automobilista 2 atëherë nuk shkruan asgjë)

**Madhësia**: mapimi është rreth 20 deri 30 KB (sipas versionit të lojës), deri në 10 herë në sekondë gjatë drejtimit: afërsisht 0.7 deri 1.1 GB në orë para kompresimit; zstd i zvogëlon vendet bosh të pjesëmarrësve dhe emrat që nuk ndryshojnë në një pjesë të vogël (ende i pamatur në një sesion të vërtetë)

## Verifikuar {#verified}

i provuar me një faqe të ndërtuar në test; zhvendosjet nga dy kopje të pavarura të SharedMemory.h që përputhen, jo nga kopja që e dërgon loja; i paprovuar me lojën

## Burimi {#source}

[heat3d_watch/adapters/simracing_shm.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/simracing_shm.py)

<!-- Generated from the adapter by tools/gen_game_pages.py; change the adapter and run it again rather than editing this page. -->
