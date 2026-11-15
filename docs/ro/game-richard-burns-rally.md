---
title: "Richard Burns Rally (date în direct)"
nav_order: 39
lang: "ro"
source: game-richard-burns-rally.md
source_hash: "1b9866f5a1f6"
nav_exclude: true
search_exclude: true
---
# Richard Burns Rally (date în direct) {#richard-burns-rally-live-data}

Cât timp jucați Richard Burns Rally, watcher-ul salvează datele pe care jocul însuși le trimite, ca să le puteți vedea mai târziu pe o hartă în vizualizatorul 3DHeat.

*Detalii tehnice: adaptorul `richard-burns-rally`, tipul [`telemetry`](sources-and-rules.md); rulează cât timp `RichardBurnsRally_SSE.exe` sau `RichardBurnsRally.exe` rulează și caută date noi la fiecare 0,1 s.*

## Ce se înregistrează {#what-is-recorded}

- poziția mașinii proprii (XYZ în lume, m) la 10 Hz, cu viteza, treapta, accelerația, frâna și distanța din etapă
- începutul etapei (pornește cronometrul etapei), sosirea cu timpul etapei, reporniri
- teleportările (o resetare pe drum): `teleport` unde se afla mașina, `spawn` unde se află acum
- etape, cel mai bun timp de etapă, distanța, viteza maximă

## De unde vine {#where-it-comes-from}

Telemetria UDP a pluginului NGP, 127.0.0.1:6776 (RichardBurnsRally.ini [NGP] udpTelemetry=1)

## Cum se activează {#how-to-switch-it-on}

RSF/NGP: în RichardBurnsRally.ini, secțiunea [NGP], setați udpTelemetry=1 și endpoint-ul 127.0.0.1:6776

## Cum funcționează {#how-it-works}

Telemetria proprie a jocurilor de curse: Forza, jocurile Assetto Corsa, jocurile de raliu și BeamNG, înregistrate ca trasee, ture și etape.

Fiecare joc de aici își publică telemetria în mod intenționat, pentru tablouri de bord și platforme de mișcare; nu se injectează nimic și nu se citește nimic din ce jocul nu oferă. Decodarea nu este scrisă de două ori: sunt recorderele de ture ale gamecapture din `heat3d_capture/telemetry` al 3DHeat GameCapture, copiate în `heat3d_watch/decoders` (testate acolo pe pachete construite după structurile publicate), iar acest modul transformă cadrele lor în rândurile watcher-ului: poziția mașinii de câteva ori pe secundă, cu viteza, treapta și pedalele, un eveniment pentru fiecare tură sau etapă și cifrele pe care le notează un șofer: ture, cea mai bună tură, distanța, viteza maximă.

#### Forza (Horizon 4/5/6, Motorsport) {#forza-horizon-456-motorsport}

„Data Out" UDP, activat în meniul HUD și Gameplay al jocului, către 127.0.0.1, portul 5300, formatul Dash. Un pachet pentru fiecare tic de simulare; decalajul blocului de date este găsit din pachete (`forza.detect_layout`). Metri în lume, Y în sus; lumea este stângace și este desenată așa cum vine, ca în recorderul de ture (documentația „Data Out" a Forza Motorsport și Forza Horizon). Jocul trimite către un singur port, iar FH Companion și alte aplicații Data Out ascultă pe același port. Două programe nu pot împărți portul: pe Windows, socketul legat la 127.0.0.1 primește pachetele, iar cel legat la toate adresele pe același port nu primește niciunul, indiferent care a pornit primul. Așadar watcher-ul așteaptă puțin după ce pornește jocul înainte să ia portul, nu îl ia niciodată de la o aplicație care îl ține și îl eliberează îndată ce altă aplicație începe să asculte acolo. Cât timp ține portul, trimite mai departe fiecare pachet neschimbat către 127.0.0.1:5301. Setați caseta de port a FH Companion (fila sa de telemetrie) la 5301 și înregistrează amândouă.

#### EA SPORTS WRC, DiRT Rally 2.0, Richard Burns Rally {#ea-sports-wrc-dirt-rally-20-richard-burns-rally}

UDP: `Documents/My Games/WRC/telemetry/config.json` al WRC (pachetul `session_update` al structurii `wrc`), `hardware_settings_config.xml` al DiRT (`<udp enabled="true" extradata="3" port="20777">`), pluginul NGP al RBR (`udpTelemetry=1`, portul 6776). Etapele după cronometrul etapei jocului (`rally.StageSplitter`). RBR nu își documentează axele: axa verticală este cea de-a lungul căreia etapa variază cel mai puțin, hotărâtă la închiderea sesiunii.

#### Totul se păstrează {#everything-kept}

Rândurile sunt câteva pe secundă; jocurile trimit mult mai multe. Fiecare pachet UDP care sosește (în meniuri, între ture, cele pe care niciun decodor nu le citește) se păstrează întreg în `heat.raw.parquet` al sesiunii, sub formatul său (`dash-horizon`, `session_update`, `extradata3`, `H3D1`, ...), iar fiecare pagină de memorie partajată (toată zona mapată, nu doar octeții decodați) de fiecare dată când se schimbă, sub numele zonei sale (`acpmf_physics`, ...). `used` marchează ce a devenit și rând; `meta.json`, la `selfCheck.completeness`, numără fiecare tip (regula convertorului 3DHeat).

Același modul servește și: [Assetto Corsa (date în direct)](game-assetto-corsa.md), [Assetto Corsa Competizione (date în direct)](game-assetto-corsa-competizione.md), [Assetto Corsa EVO (date în direct)](game-assetto-corsa-evo.md), [Assetto Corsa Rally (date în direct)](game-assetto-corsa-rally.md), [BeamNG.drive (date în direct)](game-beamng.md), [DiRT Rally 2.0 (date în direct)](game-dirt-rally-2.md), [EA SPORTS WRC (date în direct)](game-ea-wrc.md), [Forza Horizon 4 (date în direct)](game-forza-horizon-4.md), [Forza Horizon 5 (date în direct)](game-forza-horizon-5.md), [Forza Horizon 6 (date în direct)](game-forza-horizon-6.md), [Forza Motorsport (date în direct)](game-forza-motorsport.md).

## Poziții și axe {#positions-and-axes}

| | |
|---|---|
| Poziții înregistrate | da |
| Axa verticală | `y` |
| Unități | metri; axa verticală stabilită din mers (RBR nu își documentează axele) |
| Oglindit pentru vizualizator | niciunul |
| Scara unității (`scale`: vizualizatorul înmulțește pozițiile cu ea) | 1 |

Acestea intră în `meta.json` al fiecărei sesiuni (`axes`) și, când sesiunea are poziții, în subsolul `heat.parquet`, ca vizualizatorul 3DHeat să rotească și să scaleze rândurile singur; vedeți [Datele](the-data.md).

## Multiplayer {#multiplayer}

- Marcat ca jucat online (`multiplayer`): **nu**. `games --markdown` arată asta ca „un singur jucător”.
- Tipul `telemetry`: citește doar ce oferă jocul sau platforma (un port UDP sau memoria partajată pe care o publică jocul), deci înregistrează și în jocul online, nu doar offline; marcajul decide doar dacă memoria poate fi citită vreodată.
- Memoria: **niciodată** citită de acest adaptor. Doar adaptoarele de tip `memory` citesc memoria, și niciodată pentru un joc marcat ca jucat online; vedeți [Surse și reguli](sources-and-rules.md).

## Statistici înregistrate {#statistics-recorded}

Cheile de statistici pe care codul adaptorului le setează pe nume (fiecare `stats` din sesiune, în `meta.json`, și tabelul `stats` din `watcher.sqlite`):

`best_lap`, `best_stage`, `distance_km`, `laps`, `stages`, `top_speed_kmh`

O cheie între acolade se completează la rulare (`score.{team}` este câte o cheie pentru fiecare echipă). Cheile pe care codul le ia dintr-un tabel de câmpuri ale jocului sau din numele statisticilor proprii ale jocului nu sunt în listă; „Ce se înregistrează” de mai sus le numește.

## Completitudine {#completeness}

Watcher-ul urmează regula de convertor a 3DHeat: ce conține sursa este citit sau păstrat, niciodată eliminat. Pe lângă rânduri, fiecare pachet, pagină, linie sau răspuns pe care îl primește adaptorul este păstrat întreg în `heat.raw.parquet` al sesiunii (coloanele `time`, `ms`, `type`, `used`, `payload`, `text`, apoi orice câmp păstrat pe nume; `used` marchează ce a devenit și rând), iar `selfCheck.completeness` din `meta.json` numără fiecare `type`; `lost` este 0.

**Citit**

- rânduri la 10 Hz: poziție, viteză, treaptă, accelerație, frână, distanța din etapă, yaw, turație, direcție; începutul etapei, sosirea cu timpul etapei, reporniri

**Păstrat brut**

- fiecare pachet care ajunge la port, întreg, la rata jocului, sub formatul său: `telemetry` (TelemetryData NGP de 664 de octeți), `rbr <n>-byte` în rest
- în pachet, dincolo de rânduri: atitudinea, vitezele și accelerațiile proprii ale mașinii, deformarea și forța amortizorului pentru fiecare roată, progresul etapei și distanța până la final; restul celor 664 de octeți (blocurile motorului, ale pneurilor și ale frânelor pe fiecare roată) nu este decodat încă

**Nu este disponibil**

- alte mașini: jocurile trimit doar mașina jucătorului
- unitatea vitezei și axele lor: nedocumentate - viteza este luată din poziții, verticala din mers

**Dimensiune**: aproximativ 160 MB pe oră la 60 de pachete pe secundă (664 de octeți plus un antet de element de 70 de octeți); zstd păstrează o fracțiune

## Verificat {#verified}

decodarea este cea a recorderului de ture din gamecapture (testată pe pachete construite după structurile documentate); adaptorul testat pe pachete construite în test, trimise prin UDP; netestat cu jocul

## Sursă {#source}

[heat3d_watch/adapters/racing.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/racing.py)

<!-- Generated from the adapter by tools/gen_game_pages.py; change the adapter and run it again rather than editing this page. -->
