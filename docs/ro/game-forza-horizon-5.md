---
title: "Forza Horizon 5 (date în direct)"
nav_order: 22
lang: "ro"
source: game-forza-horizon-5.md
source_hash: "0083724478e7"
nav_exclude: true
search_exclude: true
---
# Forza Horizon 5 (date în direct) {#forza-horizon-5-live-data}

Cât timp jucați Forza Horizon 5, watcher-ul salvează datele pe care jocul însuși le trimite, ca să le puteți vedea mai târziu pe o hartă în vizualizatorul 3DHeat.

*Detalii tehnice: adaptorul `forza-horizon-5`, tipul [`telemetry`](sources-and-rules.md); rulează cât timp `ForzaHorizon5.exe` este pornit și caută date noi la fiecare 0,1 s.*

## Ce se înregistrează {#what-is-recorded}

- poziția mașinii proprii (XYZ în lume, m) la 10 Hz, cu viteza, treapta, accelerația, frâna, tura
- începutul și sfârșitul conducerii (session_start/session_end), ture cu timpul de tură al jocului
- începutul și sosirea cursei, cu poziția în cursă
- teleportările (derularea, călătoria rapidă): `teleport` unde se afla mașina, `spawn` unde se află acum
- ture, cea mai bună tură, distanța, viteza maximă, curse

## De unde vine {#where-it-comes-from}

Forza Data Out, UDP 127.0.0.1:5300 (formatul Dash); fiecare pachet trimis mai departe neschimbat către 127.0.0.1:5301

## Cum se activează {#how-to-switch-it-on}

În joc: Settings > HUD and Gameplay > Data Out On, IP 127.0.0.1, portul 5300 (Motorsport: formatul Dash). FH Companion sau altă aplicație Data Out: setați portul ei la 5301 - watcher-ul trece mai departe fiecare pachet; cât timp o altă aplicație ascultă pe 5300, watcher-ul îi lasă portul și nu înregistrează nimic

## Cum funcționează {#how-it-works}

Telemetria proprie a jocurilor de curse: Forza, jocurile Assetto Corsa, jocurile de raliu și BeamNG, înregistrate ca trasee, ture și etape.

Fiecare joc de aici își publică telemetria în mod intenționat, pentru tablouri de bord și platforme de mișcare; nu se injectează nimic și nu se citește nimic din ce jocul nu oferă. Decodarea nu este scrisă de două ori: sunt recorderele de ture ale gamecapture din `heat3d_capture/telemetry` al 3DHeat GameCapture, copiate în `heat3d_watch/decoders` (testate acolo pe pachete construite după structurile publicate), iar acest modul transformă cadrele lor în rândurile watcher-ului: poziția mașinii de câteva ori pe secundă, cu viteza, treapta și pedalele, un eveniment pentru fiecare tură sau etapă și cifrele pe care le notează un șofer: ture, cea mai bună tură, distanța, viteza maximă.

#### Forza (Horizon 4/5/6, Motorsport) {#forza-horizon-456-motorsport}

„Data Out" UDP, activat în meniul HUD și Gameplay al jocului, către 127.0.0.1, portul 5300, formatul Dash. Un pachet pentru fiecare tic de simulare; decalajul blocului de date este găsit din pachete (`forza.detect_layout`). Metri în lume, Y în sus; lumea este stângace și este desenată așa cum vine, ca în recorderul de ture (documentația „Data Out" a Forza Motorsport și Forza Horizon). Jocul trimite către un singur port, iar FH Companion și alte aplicații Data Out ascultă pe același port. Două programe nu pot împărți portul: pe Windows, socketul legat la 127.0.0.1 primește pachetele, iar cel legat la toate adresele pe același port nu primește niciunul, indiferent care a pornit primul. Așadar watcher-ul așteaptă puțin după ce pornește jocul înainte să ia portul, nu îl ia niciodată de la o aplicație care îl ține și îl eliberează îndată ce altă aplicație începe să asculte acolo. Cât timp ține portul, trimite mai departe fiecare pachet neschimbat către 127.0.0.1:5301. Setați caseta de port a FH Companion (fila sa de telemetrie) la 5301 și înregistrează amândouă.

#### Totul se păstrează {#everything-kept}

Rândurile sunt câteva pe secundă; jocurile trimit mult mai multe. Fiecare pachet UDP care sosește (în meniuri, între ture, cele pe care niciun decodor nu le citește) se păstrează întreg în `heat.raw.parquet` al sesiunii, sub formatul său (`dash-horizon`, `session_update`, `extradata3`, `H3D1`, ...), iar fiecare pagină de memorie partajată (toată zona mapată, nu doar octeții decodați) de fiecare dată când se schimbă, sub numele zonei sale (`acpmf_physics`, ...). `used` marchează ce a devenit și rând; `meta.json`, la `selfCheck.completeness`, numără fiecare tip (regula convertorului 3DHeat).

Același modul servește și: [Assetto Corsa (date în direct)](game-assetto-corsa.md), [Assetto Corsa Competizione (date în direct)](game-assetto-corsa-competizione.md), [Assetto Corsa EVO (date în direct)](game-assetto-corsa-evo.md), [Assetto Corsa Rally (date în direct)](game-assetto-corsa-rally.md), [BeamNG.drive (date în direct)](game-beamng.md), [DiRT Rally 2.0 (date în direct)](game-dirt-rally-2.md), [EA SPORTS WRC (date în direct)](game-ea-wrc.md), [Forza Horizon 4 (date în direct)](game-forza-horizon-4.md), [Forza Horizon 6 (date în direct)](game-forza-horizon-6.md), [Forza Motorsport (date în direct)](game-forza-motorsport.md), [Richard Burns Rally (date în direct)](game-richard-burns-rally.md).

## Poziții și axe {#positions-and-axes}

| | |
|---|---|
| Poziții înregistrate | da |
| Axa verticală | `y` |
| Unități | metri; lumea Forza este stângace, desenată așa cum vine, ca în recorderul de ture |
| Oglindit pentru vizualizator | niciunul |
| Scara unității (`scale`: vizualizatorul înmulțește pozițiile cu ea) | 1 |

Acestea intră în `meta.json` al fiecărei sesiuni (`axes`) și, când sesiunea are poziții, în subsolul `heat.parquet`, ca vizualizatorul 3DHeat să rotească și să scaleze rândurile singur; vedeți [Datele](the-data.md).

## Multiplayer {#multiplayer}

- Marcat ca jucat online (`multiplayer`): **da**. `games --markdown` arată asta ca „permis (citește doar ce publică jocul)".
- Tipul `telemetry`: citește doar ce oferă jocul sau platforma (un port UDP sau memoria partajată pe care o publică jocul), deci înregistrează și în jocul online, nu doar offline; marcajul decide doar dacă memoria poate fi citită vreodată.
- Memoria: **niciodată** citită de acest adaptor. Doar adaptoarele de tip `memory` citesc memoria, și niciodată pentru un joc marcat ca jucat online; vedeți [Surse și reguli](sources-and-rules.md).

## Statistici înregistrate {#statistics-recorded}

Cheile de statistici pe care codul adaptorului le setează pe nume (fiecare `stats` din sesiune, în `meta.json`, și tabelul `stats` din `watcher.sqlite`):

`best_lap`, `distance_km`, `laps`, `races`, `top_speed_kmh`

O cheie între acolade se completează la rulare (`score.{team}` este câte o cheie pentru fiecare echipă). Cheile pe care codul le ia dintr-un tabel de câmpuri ale jocului sau din numele statisticilor proprii ale jocului nu sunt în listă; „Ce se înregistrează" de mai sus le numește.

## Completitudine {#completeness}

Watcher-ul urmează regula de convertor a 3DHeat: ce conține sursa este citit sau păstrat, niciodată eliminat. Pe lângă rânduri, fiecare pachet, pagină, linie sau răspuns pe care îl primește adaptorul este păstrat întreg în `heat.raw.parquet` al sesiunii (coloanele `time`, `ms`, `type`, `used`, `payload`, `text`, apoi orice câmp păstrat pe nume; `used` marchează ce a devenit și rând), iar `selfCheck.completeness` din `meta.json` numără fiecare `type`; `lost` este 0.

**Citit**

- rânduri la 10 Hz: poziția, viteza, treapta, accelerația, frâna, tura, yaw/pitch/roll (rad), turația, direcția (-1..1); session_start cu ordinalul mașinii, clasa, PI-ul și transmisia; ture cu timpul de tură al jocului; poziția în cursă

**Păstrat brut**

- fiecare pachet care ajunge la port, întreg, la rata jocului (un pachet pe tic de simulare), sub formatul său: `dash-horizon` (324 de octeți, Forza Horizon), `dash` (311, Motorsport 7), `dash-fm2023` (331, Forza Motorsport 2023: uzura pneurilor și id-ul pistei), `sled` (232, fără poziție), `<n>-byte` pentru orice altceva - inclusiv pachetele din meniuri (isRaceOn 0), pachetele ținute până când layoutul tabloului de bord este dovedit și cei ~13 octeți ai pachetului Horizon pe care niciun layout publicat nu îi numește
- fiecare canal al fiecărei roți din blocul Sled (raportul și unghiul de alunecare, alunecarea combinată, suspensia, viteza roții, rumble, puddle), accelerațiile, viteza unghiulară, puterea, cuplul, boost-ul, combustibilul, temperaturile pneurilor, ambreiajul, frâna de mână, linia de conducere, diferența de frânare a AI-ului: toate sunt în pachete, decodate din ele de `decoders/fulllap.decode_full`

**Nu este disponibil**

- alte mașini: Data Out descrie doar mașina jucătorului
- numele pistei sau al traseului: Forza Horizon nu trimite niciodată unul; Motorsport 2023 trimite doar un număr de pistă
- pachetele cât timp o altă aplicație (FH Companion) ține UDP 5300: watcher-ul îi lasă portul

**Dimensiune**: aproximativ 85 MB pe oră înainte de compresie (60 de pachete pe secundă de 324 de octeți plus un antet de 70 de octeți pe element); pachetele consecutive diferă puțin, deci zstd păstrează o fracțiune din ele

## Verificat {#verified}

decodarea este cea a recorderului de ture din gamecapture (testată pe pachete construite după layoutul Data Out); adaptorul a fost testat pe pachete sintetice și pe traiectorii de ture reale redate ca pachete; netestat încă cu jocul

## Sursă {#source}

[heat3d_watch/adapters/racing.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/racing.py)

<!-- Generated from the adapter by tools/gen_game_pages.py; change the adapter and run it again rather than editing this page. -->
