---
title: "Forza Horizon 5 (të dhëna live)"
nav_order: 22
lang: "sq"
source: game-forza-horizon-5.md
source_hash: "0083724478e7"
nav_exclude: true
search_exclude: true
---
# Forza Horizon 5 (të dhëna live) {#forza-horizon-5-live-data}

Ndërsa luan Forza Horizon 5, watcher ruan të dhënat që vetë loja i dërgon, që t'i shohësh më vonë në një hartë në shikuesin 3DHeat.

*Detaje teknike: adaptori `forza-horizon-5`, lloji [`telemetry`](sources-and-rules.md); punon sa kohë `ForzaHorizon5.exe` është duke u ekzekutuar dhe kërkon të dhëna të reja çdo 0.1 s.*

## Çfarë regjistrohet {#what-is-recorded}

- pozicioni i makinës sate (XYZ në botë, m) me 10 Hz, me shpejtësinë, marshin, gazin, frenin, xhiron
- fillimi dhe fundi i vozitjes (session_start/session_end), xhirot me kohën e xhiros të lojës
- fillimi dhe mbarimi i garës me pozicionin në garë
- teleportimet (rewind, udhëtim i shpejtë): `teleport` ku ishte makina, `spawn` ku është tani
- xhirot, xhiroja më e mirë, distanca, shpejtësia maksimale, garat

## Nga vjen {#where-it-comes-from}

Forza Data Out, UDP 127.0.0.1:5300 (formati Dash); çdo paketë ritransmetohet e pandryshuar te 127.0.0.1:5301

## Si ta ndezësh {#how-to-switch-it-on}

Në lojë: Settings > HUD and Gameplay > Data Out On, IP 127.0.0.1, port 5300 (Motorsport: format Dash). FH Companion ose një aplikacion tjetër Data Out: vendos portën e tij në 5301 - watcher i kalon të gjitha paketat; sa kohë një aplikacion tjetër dëgjon në 5300, watcher ia lë portën atij dhe nuk regjistron asgjë

## Si funksionon {#how-it-works}

Telemetria e vetë lojërave të garave: Forza, lojërat Assetto Corsa, lojërat e rally-t
dhe BeamNG, e regjistruar si rrugë, xhiro dhe etapa.

Çdo lojë këtu e publikon telemetrinë me qëllim, për tabela treguesish dhe platforma
lëvizjeje; asgjë nuk injektohet dhe nuk lexohet asgjë që loja nuk e jep vetë. Dekodimi
nuk është shkruar dy herë: janë regjistruesit e xhiros të gamecapture,
në `heat3d_capture/telemetry` të 3DHeat GameCapture, të kopjuar te `heat3d_watch/decoders` (të provuar atje me paketa të ndërtuara sipas
strukturave të publikuara), dhe ky modul i kthen kuadrot e tyre në rreshtat e watcher-it
- pozicioni i makinës disa herë në sekondë me shpejtësinë, marshin dhe pedalet,
një ngjarje për çdo xhiro ose etapë, dhe numrat që një shofer i mban: xhirot, xhiroja
më e mirë, distanca, shpejtësia maksimale.

#### Forza (Horizon 4/5/6, Motorsport) {#forza-horizon-456-motorsport}

UDP "Data Out", i ndezur te cilësimet HUD and Gameplay të lojës, drejt
127.0.0.1 portës 5300, formati Dash. Një paketë për çdo hap simulimi; zhvendosja e
bllokut dash gjendet nga paketat (`forza.detect_layout`). Metra në botë,
Y lart; bota është e majtë dhe vizatohet siç dërgohet, ashtu si e bën regjistruesi i xhiros
(dokumentimi "Data Out" i Forza Motorsport dhe Forza Horizon).
Loja dërgon te një port, dhe FH Companion e aplikacione të tjera Data Out dëgjojnë
në të njëjtin. Dy programe nuk mund ta ndajnë: në Windows soketi i lidhur
me 127.0.0.1 merr paketat dhe ai i lidhur me të gjitha adresat në të njëjtën
portë nuk merr asnjë, cili të ketë ardhur i pari. Prandaj watcher pret pak pasi
nis loja para se ta marrë portën, nuk e merr kurrë nga një aplikacion që
e mban, dhe e lëshon sapo një aplikacion tjetër fillon të dëgjojë aty.
Ndërsa e mban portën, ia kalon çdo paketë të pandryshuar te
127.0.0.1:5301 - vendose kutinë e portës së FH Companion (skeda e telemetrisë) në 5301 dhe
të dy regjistrojnë.

#### Gjithçka ruhet {#everything-kept}

Rreshtat janë disa në sekondë; lojërat dërgojnë shumë më tepër. Çdo paketë UDP që
mbërrin - në meny, mes xhirove, edhe ato që asnjë dekoder nuk i lexon - ruhet e plotë
te `heat.raw.parquet` i sesionit nën formatin e vet (`dash-horizon`,
`session_update`, `extradata3`, `H3D1`, ...), dhe çdo faqe e memories së përbashkët
(i gjithë mapimi, jo vetëm bajtet e dekoduara) sa herë që ndryshon, nën emrin e
mapimit të vet (`acpmf_physics`, ...). `used` shënon çfarë u bë edhe rreshta;
`selfCheck.completeness` i `meta.json` numëron çdo lloj (rregulli i konvertuesit të 3DHeat).

Të njëjtin modul e përdorin edhe: [Assetto Corsa (të dhëna live)](game-assetto-corsa.md), [Assetto Corsa Competizione (të dhëna live)](game-assetto-corsa-competizione.md), [Assetto Corsa EVO (të dhëna live)](game-assetto-corsa-evo.md), [Assetto Corsa Rally (të dhëna live)](game-assetto-corsa-rally.md), [BeamNG.drive (të dhëna live)](game-beamng.md), [DiRT Rally 2.0 (të dhëna live)](game-dirt-rally-2.md), [EA SPORTS WRC (të dhëna live)](game-ea-wrc.md), [Forza Horizon 4 (të dhëna live)](game-forza-horizon-4.md), [Forza Horizon 6 (të dhëna live)](game-forza-horizon-6.md), [Forza Motorsport (të dhëna live)](game-forza-motorsport.md), [Richard Burns Rally (të dhëna live)](game-richard-burns-rally.md).

## Pozicionet dhe boshtet {#positions-and-axes}

| | |
|---|---|
| Pozicionet e regjistruara | po |
| Boshti lart | `y` |
| Njësitë | metra; bota e Forza është e majtë, vizatohet siç dërgohet, ashtu si e bën regjistruesi i xhiros |
| Pasqyruar për shikuesin | asnjë |
| Shkalla e njësisë (`scale`: shikuesi i shumëzon pozicionet me të) | 1 |

Këto hyjnë te `meta.json` i çdo sesioni (`axes`) dhe, kur sesioni ka pozicione, te fundi (footer) i `heat.parquet`, kështu që shikuesi 3DHeat i rrotullon dhe i shkallëzon rreshtat vetë - shih [Të dhënat](the-data.md).

## Lojë me shumë lojtarë {#multiplayer}

- Shënuar si lojë që luhet online (`multiplayer`): **po**. `games --markdown` e shfaq këtë si "allowed (reads only what the game publishes)".
- Lloji `telemetry`: lexon vetëm atë që loja ose platforma e jep vetë (një port UDP ose memorie e përbashkët që loja e publikon), kështu që regjistron si në lojën online ashtu edhe offline; shenja vendos vetëm nëse memoria lejohet ndonjëherë të lexohet.
- Memoria: **asnjëherë** nuk lexohet nga ky adaptor. Vetëm adaptorët `memory` lexojnë memorie, dhe kurrë për një lojë të shënuar si e luajtur online - shih [Burimet dhe rregullat](sources-and-rules.md).

## Statistikat e regjistruara {#statistics-recorded}

Çelësat e statistikave që kodi i këtij adaptori i vendos me emër (`stats` i çdo sesioni te `meta.json` dhe tabela `stats` e `watcher.sqlite`):

`best_lap`, `distance_km`, `laps`, `races`, `top_speed_kmh`

Një çelës në kllapa gjarpërore plotësohet gjatë punës (`score.{team}` është një çelës për çdo ekip). Çelësat që kodi i merr nga një tabelë me fushat e lojës ose nga emrat e statistikave të vetë lojës nuk janë në këtë listë; "Çfarë regjistrohet" më sipër i emërton.

## Plotësia {#completeness}

Watcher ndjek [rregullin e konvertuesit](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md) të 3DHeat: çfarë mban burimi lexohet ose ruhet, kurrë nuk hidhet. Përveç rreshtave, çdo paketë, faqe, rresht ose përgjigje që e merr adaptori ruhet e plotë te `heat.raw.parquet` i sesionit (kolonat `time`, `ms`, `type`, `used`, `payload`, `text`, pastaj çdo fushë e ruajtur me emër; `used` shënon çfarë u bë edhe rreshta), dhe `selfCheck.completeness` i `meta.json` numëron çdo `type` - `lost` është 0.

**Lexuar**

- rreshta me 10 Hz: pozicioni, shpejtësia, marshi, gazi, frena, xhiroja, yaw/pitch/roll (rad), rpm, steer (-1..1); session_start me ordinalin e makinës, klasën, PI dhe transmisionin; xhirot me kohën e xhiros të lojës; pozicioni në garë

**Ruajtur të papërpunuara**

- çdo paketë që mbërrin te porta, e plotë, me ritmin e lojës (një për çdo hap simulimi), nën formatin e vet: `dash-horizon` (324 bajte, Forza Horizon), `dash` (311, Motorsport 7), `dash-fm2023` (331, Forza Motorsport 2023: konsumimi i gomave dhe id e pistës), `sled` (232, pa pozicion), `<n>-byte` për çdo gjë tjetër - përfshirë paketat e menysë (isRaceOn 0), paketat e mbajtura derisa struktura dash të provohet, dhe rreth 13 bajtet e paketës Horizon që asnjë strukturë e publikuar nuk i emërton
- çdo kanal i rrotave i bllokut Sled (slip ratio, slip angle, combined slip, pezullimi, shpejtësia e rrotës, rumble, puddle), nxitimet, shpejtësia këndore, fuqia, çifti (torque), boost, karburanti, temperaturat e gomave, friksioni (clutch), freni i dorës, vija e vozitjes, ndryshimi i frenimit të AI: të gjitha në paketa, të dekoduara prej tyre nga `decoders/fulllap.decode_full`

**Nuk ofrohet**

- makinat e tjera: Data Out përshkruan vetëm makinën e lojtarit
- emri i pistës ose i rrugës: Forza Horizon nuk dërgon asnjë; Motorsport 2023 dërgon vetëm një numër të pistës
- paketat sa kohë një aplikacion tjetër (FH Companion) e mban UDP 5300: watcher ia lë portën atij

**Madhësia**: rreth 85 MB në orë para kompresimit (60 paketa në sekondë me 324 bajte plus një kokë 70 bajte për element); paketat njëra pas tjetrës ndryshojnë pak, kështu që zstd ruan një pjesë të vogël të tyre

## Verifikuar {#verified}

dekodimi është ai i regjistruesit të xhiros të gamecapture (i provuar me paketa të ndërtuara sipas strukturës Data Out); adaptori u provua me paketa sintetike dhe me trajektore xhirosh të regjistruara të riluajtura si paketa; i paprovuar me vetë lojën

## Burimi {#source}

[heat3d_watch/adapters/racing.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/racing.py)

<!-- Generated from the adapter by tools/gen_game_pages.py; change the adapter and run it again rather than editing this page. -->
