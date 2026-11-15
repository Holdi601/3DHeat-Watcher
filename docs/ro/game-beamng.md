---
title: "BeamNG.drive (date în direct)"
nav_order: 7
lang: "ro"
source: game-beamng.md
source_hash: "1c23a869a62f"
nav_exclude: true
search_exclude: true
---
# BeamNG.drive (date în direct) {#beamngdrive-live-data}

Cât timp jucați BeamNG.drive, watcher-ul salvează datele pe care jocul însuși le trimite, ca să le puteți vedea mai târziu pe o hartă în vizualizatorul 3DHeat.

*Detalii tehnice: adaptorul `beamng`, tipul [`telemetry`](sources-and-rules.md); rulează cât timp `BeamNG.drive.x64.exe` sau `BeamNG.drive.exe` rulează și caută date noi la fiecare 0,1 s.*

## Ce se înregistrează {#what-is-recorded}

- poziția mașinii proprii (în lume, m, rotită la Y în sus) la 10 Hz, cu viteza, treapta, accelerația și frâna
- începutul condusului, resetările (respawn), ture după locul unde a început condusul
- ture, cea mai bună tură, distanța, viteza maximă

## De unde vine {#where-it-comes-from}

UDP 127.0.0.1:4460 din modul de protocol heat3d (mods/beamng/heat3d din acest depozit)

## Cum se activează {#how-to-switch-it-on}

`python -m heat3d_watch setup beamng --apply` instalează modul; apoi Options > Other > Protocols > „others”

Scrieți comanda într-un terminal deschis în folderul watcher-ului (vedeți [Înainte de a începe](before-you-start.md)). Dacă eșuează, ultima linie spune de ce; [Instalarea și rularea](installing-and-running.md) acoperă cauzele obișnuite.

`python -m heat3d_watch setup beamng` arată fișierele pe care le-ar schimba; `python -m heat3d_watch setup beamng --apply` le schimbă, păstrând originalul ca `<file>.heat3d-backup` (vedeți [Comenzi](commands.md#setup)). Afișează `beamng: changed: ...` pentru fiecare schimbare sau `beamng: nothing to change` când este deja activat.

## Cum funcționează {#how-it-works}

Telemetria proprie a jocurilor de curse: Forza, jocurile Assetto Corsa, jocurile de raliu și BeamNG, înregistrate ca trasee, ture și etape.

Fiecare joc de aici își publică telemetria în mod intenționat, pentru tablouri de bord și platforme de mișcare; nu se injectează nimic și nu se citește nimic din ce jocul nu oferă. Decodarea nu este scrisă de două ori: sunt recorderele de ture ale gamecapture din `heat3d_capture/telemetry` al 3DHeat GameCapture, copiate în `heat3d_watch/decoders` (testate acolo pe pachete construite după structurile publicate), iar acest modul transformă cadrele lor în rândurile watcher-ului: poziția mașinii de câteva ori pe secundă, cu viteza, treapta și pedalele, un eveniment pentru fiecare tură sau etapă și cifrele pe care le notează un șofer: ture, cea mai bună tură, distanța, viteza maximă.

#### Forza (Horizon 4/5/6, Motorsport) {#forza-horizon-456-motorsport}

„Data Out" UDP, activat în meniul HUD și Gameplay al jocului, către 127.0.0.1, portul 5300, formatul Dash. Un pachet pentru fiecare tic de simulare; decalajul blocului de date este găsit din pachete (`forza.detect_layout`). Metri în lume, Y în sus; lumea este stângace și este desenată așa cum vine, ca în recorderul de ture (documentația „Data Out" a Forza Motorsport și Forza Horizon). Jocul trimite către un singur port, iar FH Companion și alte aplicații Data Out ascultă pe același port. Două programe nu pot împărți portul: pe Windows, socketul legat la 127.0.0.1 primește pachetele, iar cel legat la toate adresele pe același port nu primește niciunul, indiferent care a pornit primul. Așadar watcher-ul așteaptă puțin după ce pornește jocul înainte să ia portul, nu îl ia niciodată de la o aplicație care îl ține și îl eliberează îndată ce altă aplicație începe să asculte acolo. Cât timp ține portul, trimite mai departe fiecare pachet neschimbat către 127.0.0.1:5301. Setați caseta de port a FH Companion (fila sa de telemetrie) la 5301 și înregistrează amândouă.

#### BeamNG.drive {#beamngdrive}

Modul de protocol `heat3d` pe care îl livrează gamecapture (UDP 4460, Options > Other > Protocols > „others”); lumea BeamNG cu Z în sus, rotită la Y în sus, cum face `beamng.py`.

#### Totul se păstrează {#everything-kept}

Rândurile sunt câteva pe secundă; jocurile trimit mult mai multe. Fiecare pachet UDP care sosește (în meniuri, între ture, cele pe care niciun decodor nu le citește) se păstrează întreg în `heat.raw.parquet` al sesiunii, sub formatul său (`dash-horizon`, `session_update`, `extradata3`, `H3D1`, ...), iar fiecare pagină de memorie partajată (toată zona mapată, nu doar octeții decodați) de fiecare dată când se schimbă, sub numele zonei sale (`acpmf_physics`, ...). `used` marchează ce a devenit și rând; `meta.json`, la `selfCheck.completeness`, numără fiecare tip (regula convertorului 3DHeat).

Același modul servește și: [Assetto Corsa (date în direct)](game-assetto-corsa.md), [Assetto Corsa Competizione (date în direct)](game-assetto-corsa-competizione.md), [Assetto Corsa EVO (date în direct)](game-assetto-corsa-evo.md), [Assetto Corsa Rally (date în direct)](game-assetto-corsa-rally.md), [DiRT Rally 2.0 (date în direct)](game-dirt-rally-2.md), [EA SPORTS WRC (date în direct)](game-ea-wrc.md), [Forza Horizon 4 (date în direct)](game-forza-horizon-4.md), [Forza Horizon 5 (date în direct)](game-forza-horizon-5.md), [Forza Horizon 6 (date în direct)](game-forza-horizon-6.md), [Forza Motorsport (date în direct)](game-forza-motorsport.md), [Richard Burns Rally (date în direct)](game-richard-burns-rally.md).

## Poziții și axe {#positions-and-axes}

| | |
|---|---|
| Poziții înregistrate | da |
| Axa verticală | `y` |
| Unități | metri (lumea BeamNG cu Z în sus, rotită în jurul axei X, cum face recorderul de ture) |
| Oglindit pentru vizualizator | niciunul |
| Scara unității (`scale`: vizualizatorul înmulțește pozițiile cu ea) | 1 |

Acestea intră în `meta.json` al fiecărei sesiuni (`axes`) și, când sesiunea are poziții, în subsolul `heat.parquet`, ca vizualizatorul 3DHeat să rotească și să scaleze rândurile singur; vedeți [Datele](the-data.md).

## Multiplayer {#multiplayer}

- Marcat ca jucat online (`multiplayer`): **nu**. `games --markdown` arată asta ca „un singur jucător”.
- Tipul `telemetry`: citește doar ce oferă jocul sau platforma (un port UDP sau memoria partajată pe care o publică jocul), deci înregistrează și în jocul online, nu doar offline; marcajul decide doar dacă memoria poate fi citită vreodată.
- Memoria: **niciodată** citită de acest adaptor. Doar adaptoarele de tip `memory` citesc memoria, și niciodată pentru un joc marcat ca jucat online; vedeți [Surse și reguli](sources-and-rules.md).

## Statistici înregistrate {#statistics-recorded}

Cheile de statistici pe care codul adaptorului le setează pe nume (fiecare `stats` din sesiune, în `meta.json`, și tabelul `stats` din `watcher.sqlite`):

`best_lap`, `distance_km`, `laps`, `top_speed_kmh`

O cheie între acolade se completează la rulare (`score.{team}` este câte o cheie pentru fiecare echipă). Cheile pe care codul le ia dintr-un tabel de câmpuri ale jocului sau din numele statisticilor proprii ale jocului nu sunt în listă; „Ce se înregistrează” de mai sus le numește.

## Completitudine {#completeness}

Watcher-ul urmează regula de convertor a 3DHeat: ce conține sursa este citit sau păstrat, niciodată eliminat. Pe lângă rânduri, fiecare pachet, pagină, linie sau răspuns pe care îl primește adaptorul este păstrat întreg în `heat.raw.parquet` al sesiunii (coloanele `time`, `ms`, `type`, `used`, `payload`, `text`, apoi orice câmp păstrat pe nume; `used` marchează ce a devenit și rând), iar `selfCheck.completeness` din `meta.json` numără fiecare `type`; `lost` este 0.

**Citit**

- rânduri la 10 Hz: poziție, viteză, treaptă, accelerație, frână, yaw, turație, direcție; începutul condusului, resetările, ture

**Păstrat brut**

- fiecare pachet care ajunge la port, întreg, la 100 Hz ai modului: `H3D1` (structura de 160 de octeți a modulului: ceas, poziție, viteză, axele mașinii, viteza de rotație pe yaw, nouă intrări, viteza suprafeței fiecărei roți, rotația, sarcina și materialul de sub roată), `<n>-byte` pentru orice altceva

**Nu este disponibil**

- ce nu trimite modulul: BeamNG nu are pachet fix de telemetrie, deci canalele sunt cele pe care le-a ales modulul heat3d (alte vehicule, avariile, numele hărții nu sunt în el)

**Dimensiune**: aproximativ 80 MB pe oră înainte de compresie (100 de pachete pe secundă de 160 de octeți plus un antet de element de 70 de octeți)

## Verificat {#verified}

decodarea este cea a recorderului de ture din gamecapture (testată pe pachete construite după structura modulului); adaptorul este testat pe asemenea pachete; modulul este netestat în joc

## Sursă {#source}

[heat3d_watch/adapters/racing.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/racing.py)

<!-- Generated from the adapter by tools/gen_game_pages.py; change the adapter and run it again rather than editing this page. -->
