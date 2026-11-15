---
title: "RaceRoom Racing Experience (date în direct)"
nav_order: 38
lang: "ro"
source: game-raceroom.md
source_hash: "ffd0499ca059"
nav_exclude: true
search_exclude: true
---
# RaceRoom Racing Experience (date în direct) {#raceroom-racing-experience-live-data}

Cât timp jucați RaceRoom Racing Experience, watcher-ul salvează datele pe care jocul însuși le trimite, ca să le puteți vedea mai târziu pe o hartă în vizualizatorul 3DHeat.

*Detalii tehnice: adaptorul `raceroom`, tipul [`telemetry`](sources-and-rules.md); rulează cât timp `RRRE64.exe` sau `RRRE.exe` rulează și caută date noi la fiecare 0,1 s.*

## Ce se înregistrează {#what-is-recorded}

- poziția fiecărei mașini (XYZ în lume, m) la 10 Hz, după numele șoferului, mașina proprie marcată, cu viteza și poziția în cursă; treapta, accelerația și frâna proprii
- începutul sesiunii cu pista numită de joc; ture pe fiecare mașină, cu timpul turei; sosiri; opririle proprii la boxe
- teleportările (înapoi la boxe, o repornire): `teleport` unde se afla mașina, `spawn` unde se află acum
- turele proprii, cea mai bună tură, poziția în cursă, distanța, viteza maximă
- toată pagina de memorie partajată a jocului în `heat.raw.parquet`, de fiecare dată când se schimbă
- punctele de incident proprii

## De unde vine {#where-it-comes-from}

memoria partajată $R3E (r3e.h al Sector3, versiunea 3)

## Cum se activează {#how-to-switch-it-on}

Nu trebuie activat nimic: watcher-ul citește sursa așa cum o oferă jocul sau platforma.

## Cum funcționează {#how-it-works}

Memorie partajată pe care jocurile de curse o publică pentru tablouri de bord, deschisă doar pentru citire - și niciodată creată.

Mai mulți simulatori își livrează telemetria ca un mapping de fișier Windows cu nume, pe care jocul îl creează și pe care oricine îl poate citi: paginile `Local\acpmf_*` ale Kunos (Assetto Corsa, ACC, AC Rally, `Local\acevo_pmf_*` ale AC EVO), `Local\IRSDKMemMapFileName` al iRacing, `$R3E` al RaceRoom și `$pcars2$` al Automobilista 2 / Project CARS 2.

De ce nu `mmap.mmap(-1, size, tagname=...)`, modul obișnuit în Python: când mapingul nu există încă, îl *creează* - aici, doar pentru citire. Un joc pornit după aceea deschide mapingul watcher-ului în loc să-l facă pe al său și apoi nu poate scrie în el, deci telemetria lui este moartă până când watcher-ul îl eliberează. Watcher-ul pornește un adaptor imediat ce apare procesul jocului, adică exact momentul în care jocul nu și-a făcut încă mapingul. Așa că aici se deschide cu `OpenFileMappingW`, care găsește doar un mapping existent, îl mapează cu `FILE_MAP_READ` și raportează „încă nu” în rest; adaptoarele încearcă din nou puțin mai târziu.

Nimic de aici nu poate scrie: vederea este mapată doar pentru citire și este copiată doar cu `ctypes.string_at`.

Aici sunt citite și alte două jocuri; fiecare mașină de pe circuit se află în paginile lor.

#### RaceRoom Racing Experience - `$R3E` {#raceroom-racing-experience---r3e}

`r3e.h` al Sector3 (github.com/sector3studios/r3e-api, sample-c/src/r3e.h, versiunea 3.6), `#pragma pack(1)`. Antetul spune unde încep piloții și cât de mare este unul (`all_drivers_offset`, `driver_data_size`), deci partea pentru fiecare pilot - numele, slotul, locul, poziția în lume (float x y z, m), turele terminate, timpul turei curente, starea sosirii, banda boxelor, viteza - este citită după acestea. Câmpurile proprii ale jucătorului (cea mai bună tură și tura anterioară, poziția în cursă, punctele de incident, treapta, pedalele, numele pistei și al traseului) sunt citite la offsetele 3.6 doar când `all_drivers_offset` este cel din 2008 la care le pune acel layout. Y este luat ca sus; antetul nu spune.

Același modul servește și: [Automobilista 2 (date în direct)](game-automobilista-2.md), [Project CARS 2 (date în direct)](game-project-cars-2.md).

## Poziții și axe {#positions-and-axes}

| | |
|---|---|
| Poziții înregistrate | da |
| Axa verticală | `y` |
| Unități | metri; Y în sus presupus (r3e.h nu spune) |
| Oglindit pentru vizualizator | niciunul |
| Scara unității (`scale`: vizualizatorul înmulțește pozițiile cu ea) | 1 |

Acestea intră în `meta.json` al fiecărei sesiuni (`axes`) și, când sesiunea are poziții, în subsolul `heat.parquet`, ca vizualizatorul 3DHeat să rotească și să scaleze rândurile singur; vedeți [Datele](the-data.md).

## Multiplayer {#multiplayer}

- Marcat ca jucat online (`multiplayer`): **da**. `games --markdown` arată asta ca „permis (citește doar ce publică jocul)”.
- Tipul `telemetry`: citește doar ce oferă jocul sau platforma (un port UDP sau memoria partajată pe care o publică jocul), deci înregistrează și în jocul online, nu doar offline; marcajul decide doar dacă memoria poate fi citită vreodată.
- Memoria: **niciodată** citită de acest adaptor. Doar adaptoarele de tip `memory` citesc memoria, și niciodată pentru un joc marcat ca jucat online; vedeți [Surse și reguli](sources-and-rules.md).

## Statistici înregistrate {#statistics-recorded}

Cheile de statistici pe care codul adaptorului le setează pe nume (fiecare `stats` din sesiune, în `meta.json`, și tabelul `stats` din `watcher.sqlite`):

`best_lap`, `distance_km`, `finishes`, `incidents`, `laps`, `pit_stops`, `race_position`, `top_speed_kmh`

O cheie între acolade se completează la rulare (`score.{team}` este câte o cheie pentru fiecare echipă). Cheile pe care codul le ia dintr-un tabel de câmpuri ale jocului sau din numele statisticilor proprii ale jocului nu sunt în listă; „Ce se înregistrează” de mai sus le numește.

## Completitudine {#completeness}

Watcher-ul urmează regula de convertor a 3DHeat: ce conține sursa este citit sau păstrat, niciodată eliminat. Pe lângă rânduri, fiecare pachet, pagină, linie sau răspuns pe care îl primește adaptorul este păstrat întreg în `heat.raw.parquet` al sesiunii (coloanele `time`, `ms`, `type`, `used`, `payload`, `text`, apoi orice câmp păstrat pe nume; `used` marchează ce a devenit și rând), iar `selfCheck.completeness` din `meta.json` numără fiecare `type`; `lost` este 0.

**Citit**

- pe slot de pilot (după offsetul și dimensiunea din antetul paginii): nume, slot, starea sosirii, loc, poziție în lume, ture terminate, timpul turei curente, banda boxelor, viteza
- câmpurile proprii ale jucătorului, doar când pagina este layout-ul r3e.h 3.6: numele pistei și al traseului, tipul sesiunii, poziția în cursă, cea mai bună tură și tura anterioară, punctele de incident, treapta, accelerația, frâna, slotul jucătorului
- offsetele stabilite din r3e.h 3.6 al Sector3 și verificate în teste pe o pagină construită după el; încă nu față de joc

**Păstrat brut**

- `r3e`: toată mapa $R3E, la fiecare citire ale cărei octeți diferă de copia păstrată ultima dată - fiecare câmp din r3e.h: fizica jucătorului (orientare, viteze, accelerații, forțe g), motorul, combustibilul, pneurile, frânele, avariile, indicatorii, meniul de la boxe, timpii pe sectoare, întreaga dată de pilot a fiecărui slot (clasă, model, echipă, timpi pe sectoare, diferențe, penalizări, pneuri)
- `used` este adevărat pentru o pagină citită în rânduri; fals pentru una din meniuri, pe pauză, într-o reluare, de alt layout sau prinsă în mijlocul scrierii (`torn` 1); `unchanged_reads` din meta.json numără citirile identice octet cu octet cu copia păstrată înainte

**Nu este disponibil**

- inputurile și fizica celorlalți piloți: pagina dă doar pe cea a jucătorului
- timpii exacți ai celorlalte mașini: un slot are doar timpul turei curente în desfășurare, deci o tură este ultimul timp în desfășurare văzut (cu o precizie de aproximativ 0,1 s)
- câmpurile proprii ale jucătorului pe alt layout decât 3.6: păstrate brut, necitite, până se verifică

**Dimensiune**: pagina are 44 KB (r3e.h 3.6; mapa este rotunjită în sus la pagini întregi de 4 KB), până la de 10 ori pe secundă în timpul condusului: aproximativ 1,6 GB pe oră înainte de compresie; sloturile de piloți goale și câmpurile care nu se schimbă se comprimă foarte bine cu zstd (nemăsurat încă pe o sesiune reală)

## Verificat {#verified}

testat pe o pagină construită în test din r3e.h 3.6 (offsetele stabilite din antetul oficial); netestat cu jocul; timpii celorlalte mașini sunt ultimul timp de tură în desfășurare văzut (cu o precizie de aproximativ 0,1 s)

## Sursă {#source}

[heat3d_watch/adapters/simracing_shm.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/simracing_shm.py)

<!-- Generated from the adapter by tools/gen_game_pages.py; change the adapter and run it again rather than editing this page. -->
