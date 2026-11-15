---
title: "BeamNG.drive (të dhëna live)"
nav_order: 7
lang: "sq"
source: game-beamng.md
source_hash: "1c23a869a62f"
nav_exclude: true
search_exclude: true
---
# BeamNG.drive (të dhëna live) {#beamngdrive-live-data}

Ndërsa luan BeamNG.drive, watcher ruan të dhënat që vetë loja i dërgon, që t'i shohësh më vonë në një hartë në shikuesin 3DHeat.

*Detaje teknike: adaptori `beamng`, lloji [`telemetry`](sources-and-rules.md); punon sa kohë `BeamNG.drive.x64.exe` ose `BeamNG.drive.exe` është duke u ekzekutuar dhe kërkon të dhëna të reja çdo 0.1 s.*

## Çfarë regjistrohet {#what-is-recorded}

- pozicioni i makinës sate (bota, m, e kthyer me Y lart) me 10 Hz, me shpejtësinë, marshin, gazin, frenin
- fillimi i vozitjes, rivendosjet (respawn), xhirot pranë vendit ku nisi vozitja
- xhirot, xhiroja më e mirë, distanca, shpejtësia maksimale

## Nga vjen {#where-it-comes-from}

UDP 127.0.0.1:4460 nga mod-i i protokollit heat3d (mods/beamng/heat3d në këtë depo)

## Si ta ndezësh {#how-to-switch-it-on}

`python -m heat3d_watch setup beamng --apply` e instalon mod-in; pastaj Options > Other > Protocols > "others"

Shkruaje komandën në një terminal të hapur në dosjen e watcher-it (shih [Para se të nisësh](before-you-start.md)). Nëse dështon, rreshti i fundit tregon pse; [Instalimi dhe nisja](installing-and-running.md) mbulon shkaqet e zakonshme.

`python -m heat3d_watch setup beamng` liston skedarët që do t'i ndryshonte; `python -m heat3d_watch setup beamng --apply` i ndryshon, duke e ruajtur origjinalin si `<file>.heat3d-backup` (shih [Komandat](commands.md#setup)). Printon `beamng: changed: ...` për çdo ndryshim, ose `beamng: nothing to change` kur është tashmë i ndezur.

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

#### BeamNG.drive {#beamngdrive}

Mod-i i protokollit `heat3d` që e dërgon gamecapture (UDP 4460, Options > Other >
Protocols > "others"); bota Z-lart e BeamNG kthehet në Y lart siç e bën `beamng.py`.

#### Gjithçka ruhet {#everything-kept}

Rreshtat janë disa në sekondë; lojërat dërgojnë shumë më tepër. Çdo paketë UDP që
mbërrin - në meny, mes xhirove, edhe ato që asnjë dekoder nuk i lexon - ruhet e plotë
te `heat.raw.parquet` i sesionit nën formatin e vet (`dash-horizon`,
`session_update`, `extradata3`, `H3D1`, ...), dhe çdo faqe e memories së përbashkët
(i gjithë mapimi, jo vetëm bajtet e dekoduara) sa herë që ndryshon, nën emrin e
mapimit të vet (`acpmf_physics`, ...). `used` shënon çfarë u bë edhe rreshta;
`selfCheck.completeness` i `meta.json` numëron çdo lloj (rregulli i konvertuesit të 3DHeat).

Të njëjtin modul e përdorin edhe: [Assetto Corsa (të dhëna live)](game-assetto-corsa.md), [Assetto Corsa Competizione (të dhëna live)](game-assetto-corsa-competizione.md), [Assetto Corsa EVO (të dhëna live)](game-assetto-corsa-evo.md), [Assetto Corsa Rally (të dhëna live)](game-assetto-corsa-rally.md), [DiRT Rally 2.0 (të dhëna live)](game-dirt-rally-2.md), [EA SPORTS WRC (të dhëna live)](game-ea-wrc.md), [Forza Horizon 4 (të dhëna live)](game-forza-horizon-4.md), [Forza Horizon 5 (të dhëna live)](game-forza-horizon-5.md), [Forza Horizon 6 (të dhëna live)](game-forza-horizon-6.md), [Forza Motorsport (të dhëna live)](game-forza-motorsport.md), [Richard Burns Rally (të dhëna live)](game-richard-burns-rally.md).

## Pozicionet dhe boshtet {#positions-and-axes}

| | |
|---|---|
| Pozicionet e regjistruara | po |
| Boshti lart | `y` |
| Njësitë | metra (bota Z-lart e BeamNG e rrotulluar rreth X, siç e bën regjistruesi i xhiros) |
| Pasqyruar për shikuesin | asnjë |
| Shkalla e njësisë (`scale`: shikuesi i shumëzon pozicionet me të) | 1 |

Këto hyjnë te `meta.json` i çdo sesioni (`axes`) dhe, kur sesioni ka pozicione, te fundi (footer) i `heat.parquet`, kështu që shikuesi 3DHeat i rrotullon dhe i shkallëzon rreshtat vetë - shih [Të dhënat](the-data.md).

## Lojë me shumë lojtarë {#multiplayer}

- Shënuar si lojë që luhet online (`multiplayer`): **jo**. `games --markdown` e shfaq këtë si "single-player".
- Lloji `telemetry`: lexon vetëm atë që loja ose platforma e jep vetë (një port UDP ose memorie e përbashkët që loja e publikon), kështu që regjistron si në lojën online ashtu edhe offline; shenja vendos vetëm nëse memoria lejohet ndonjëherë të lexohet.
- Memoria: **asnjëherë** nuk lexohet nga ky adaptor. Vetëm adaptorët `memory` lexojnë memorie, dhe kurrë për një lojë të shënuar si e luajtur online - shih [Burimet dhe rregullat](sources-and-rules.md).

## Statistikat e regjistruara {#statistics-recorded}

Çelësat e statistikave që kodi i këtij adaptori i vendos me emër (`stats` i çdo sesioni te `meta.json` dhe tabela `stats` e `watcher.sqlite`):

`best_lap`, `distance_km`, `laps`, `top_speed_kmh`

Një çelës në kllapa gjarpërore plotësohet gjatë punës (`score.{team}` është një çelës për çdo ekip). Çelësat që kodi i merr nga një tabelë me fushat e lojës ose nga emrat e statistikave të vetë lojës nuk janë në këtë listë; "Çfarë regjistrohet" më sipër i emërton.

## Plotësia {#completeness}

Watcher ndjek [rregullin e konvertuesit](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md) të 3DHeat: çfarë mban burimi lexohet ose ruhet, kurrë nuk hidhet. Përveç rreshtave, çdo paketë, faqe, rresht ose përgjigje që e merr adaptori ruhet e plotë te `heat.raw.parquet` i sesionit (kolonat `time`, `ms`, `type`, `used`, `payload`, `text`, pastaj çdo fushë e ruajtur me emër; `used` shënon çfarë u bë edhe rreshta), dhe `selfCheck.completeness` i `meta.json` numëron çdo `type` - `lost` është 0.

**Lexuar**

- rreshta me 10 Hz: pozicioni, shpejtësia, marshi, gazi, frena, yaw, rpm, steer; fillimi i vozitjes, rivendosjet, xhirot

**Ruajtur të papërpunuara**

- çdo paketë që mbërrin te porta, e plotë, me 100 Hz të mod-it: `H3D1` (struktura 160 bajte e mod-it: sahati, pozicioni, shpejtësia, boshtet e makinës, shpejtësia e yaw, nëntë hyrje, për çdo rrotë shpejtësia e sipërfaqes, rrotullimi, ngarkesa dhe materiali i tokës), `<n>-byte` për çdo gjë tjetër

**Nuk ofrohet**

- çfarë mod-i nuk dërgon: BeamNG nuk ka paketë telemetrie të fiksuar, kështu që kanalet janë ato që zgjodhi mod-i heat3d (automjetet e tjera, dëmtimet, emri i hartës nuk janë aty)

**Madhësia**: rreth 80 MB në orë para kompresimit (100 paketa në sekondë me nga 160 bajte plus një header 70 bajte për element)

## Verifikuar {#verified}

dekodimi është ai i regjistruesit të xhiros të gamecapture (i provuar me paketa të ndërtuara nga struktura e mod-it); adaptori u provua me paketa të tilla; mod-i është i paprovuar në lojë

## Burimi {#source}

[heat3d_watch/adapters/racing.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/racing.py)

<!-- Generated from the adapter by tools/gen_game_pages.py; change the adapter and run it again rather than editing this page. -->
