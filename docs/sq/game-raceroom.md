---
title: "RaceRoom Racing Experience (të dhëna live)"
nav_order: 37
lang: "sq"
source: game-raceroom.md
source_hash: "f3879cd40a67"
nav_exclude: true
search_exclude: true
---
# RaceRoom Racing Experience (të dhëna live) {#raceroom-racing-experience-live-data}

Ndërsa luan RaceRoom Racing Experience, watcher ruan të dhënat që vetë loja i dërgon, që t'i shohësh më vonë në një hartë në shikuesin 3DHeat.

*Detaje teknike: adaptori `raceroom`, lloji [`telemetry`](sources-and-rules.md); punon sa kohë `RRRE64.exe` ose `RRRE.exe` është duke u ekzekutuar dhe kërkon të dhëna të reja çdo 0.1 s.*

## Çfarë regjistrohet {#what-is-recorded}

- pozicioni i çdo makine (XYZ në botë, m) me 10 Hz sipas emrit të shoferit, makina jote e shënuar, me shpejtësinë dhe pozicionin në garë; marshi, gazi, frena i tu
- fillimi i sesionit me pistën që e emërton loja; xhirot për çdo makinë me kohën e xhiros; mbarimet; ndalesat e tua te pit-et
- teleportimet (kthimi te pit-et, një rinisje): `teleport` ku ishte makina, `spawn` ku është tani
- xhirot e tua, xhiroja më e mirë, pozicioni në garë, distanca, shpejtësia maksimale
- e gjithë faqja e memories së përbashkët të lojës te `heat.raw.parquet`, sa herë që ndryshon
- pikët e incidenteve të tua

## Nga vjen {#where-it-comes-from}

memoria e përbashkët $R3E (r3e.h i Sector3, versioni 3)

## Si ta ndezësh {#how-to-switch-it-on}

Nuk ka asgjë për të ndezur: watcher e lexon burimin ashtu siç e ofron loja ose platforma.

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

#### RaceRoom Racing Experience - `$R3E` {#raceroom-racing-experience---r3e}

`r3e.h` i Sector3 (github.com/sector3studios/r3e-api, sample-c/src/r3e.h,
versioni 3.6), `#pragma pack(1)`. Header-i tregon ku nisin shoferët
dhe sa i madh është njëri (`all_drivers_offset`, `driver_data_size`), kështu që pjesa për
çdo shofer - emri, vendi, pozicioni, pozicioni në botë (float x y z, m),
xhirot e përfunduara, koha e xhiros aktuale, gjendja e mbarimit, korsia e pit-it, shpejtësia - lexohet
me ato. Fushat e vetë lojtarit (xhiroja më e mirë dhe e mëparshme, pozicioni në garë,
pikët e incidenteve, marshi, pedalet, emrat e pistës dhe të layout-it) lexohen te
zhvendosjet e tyre 3.6 vetëm kur `all_drivers_offset` është 2008 që e vendos ai layout.
Y merret si lart; header-i nuk e thotë.

Të njëjtin modul e përdorin edhe: [Automobilista 2 (të dhëna live)](game-automobilista-2.md), [Project CARS 2 (të dhëna live)](game-project-cars-2.md).

## Pozicionet dhe boshtet {#positions-and-axes}

| | |
|---|---|
| Pozicionet e regjistruara | po |
| Boshti lart | `y` |
| Njësitë | metra; Y lart i supozuar (r3e.h nuk e thotë) |
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

- për çdo vend shoferi (sipas zhvendosjes dhe madhësisë së vetë header-it): emri, vendi, gjendja e mbarimit, pozicioni, pozicioni në botë, xhirot e përfunduara, koha e xhiros aktuale, korsia e pit-it, shpejtësia
- fushat e vetë lojtarit, vetëm kur faqja është layout-i r3e.h 3.6: emrat e pistës dhe të layout-it, lloji i sesionit, pozicioni në garë, xhiroja më e mirë dhe e mëparshme, pikët e incidenteve, marshi, gazi, frena, vendi i lojtarit
- zhvendosjet u nxorën nga r3e.h 3.6 i Sector3 dhe u kontrolluan me një faqe të ndërtuar prej tij në teste; ende jo me lojën

**Ruajtur të papërpunuara**

- `r3e`: i gjithë mapimi $R3E, çdo lexim që bajtet e tij ndryshojnë nga kopja e ruajtur së fundi - çdo fushë e r3e.h: fizika e lojtarit (orientimi, shpejtësitë, nxitimet, g-forcat), motori, karburanti, gomat, frenat, dëmtimet, shenjat, menuja e pit-it, kohët e sektorëve, të gjitha të dhënat e shoferit të çdo vendi shoferi (klasa, modeli, ekipi, kohët e sektorëve, hendeqet, ndëshkimet, gomat)
- `used` është e vërtetë për një faqe të lexuar në rreshta; e rreme për një në meny, në pauzë, në riluajtje, të një strukture tjetër, ose të kapur mes shkrimit (`torn` 1); `unchanged_reads` te meta.json numëron leximet që ishin bajt për bajt si kopja e ruajtur më parë

**Nuk ofrohet**

- hyrjet dhe fizika e shoferëve të tjerë: faqja jep vetëm ato të vetë lojtarit
- kohët e sakta të xhirove të makinave të tjera: një vend ka vetëm kohën e xhiros që po vazhdon, kështu që një xhiro është koha e fundit e parë (afërsisht 0.1 s)
- fushat e vetë lojtarit në një layout tjetër nga 3.6: ruhen të papërpunuara, nuk lexohen, derisa të kontrollohen

**Madhësia**: faqja është 44 KB (r3e.h 3.6; mapimi rrumbullakohet lart në faqe të plota 4 KB), deri në 10 herë në sekondë gjatë drejtimit: rreth 1.6 GB në orë para kompresimit; vendet bosh të shoferëve dhe fushat që nuk ndryshojnë kompresohen shumë mirë me zstd (ende i pamatur në një sesion të vërtetë)

## Verifikuar {#verified}

i provuar me një faqe të ndërtuar në test nga r3e.h 3.6 (zhvendosjet u nxorën nga header-i zyrtar); i paprovuar me lojën; kohët e xhirove të makinave të tjera janë koha e fundit e parë e xhiros që po vazhdon (afërsisht 0.1 s)

## Burimi {#source}

[heat3d_watch/adapters/simracing_shm.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/simracing_shm.py)

<!-- Generated from the adapter by tools/gen_game_pages.py; change the adapter and run it again rather than editing this page. -->
