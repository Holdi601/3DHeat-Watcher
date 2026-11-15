---
title: "Project CARS 2 (date în direct)"
nav_order: 37
lang: "ro"
source: game-project-cars-2.md
source_hash: "a1990b93b7d1"
nav_exclude: true
search_exclude: true
---
# Project CARS 2 (date în direct) {#project-cars-2-live-data}

Cât timp jucați Project CARS 2, watcher-ul salvează datele pe care jocul însuși le trimite, ca să le puteți vedea mai târziu pe o hartă în vizualizatorul 3DHeat.

*Detalii tehnice: adaptorul `project-cars-2`, tipul [`telemetry`](sources-and-rules.md); rulează cât timp `pCARS2AVX.exe` sau `pCARS2.exe` rulează și caută date noi la fiecare 0,1 s.*

## Ce se înregistrează {#what-is-recorded}

- poziția fiecărei mașini (XYZ în lume, m) la 10 Hz, după numele șoferului, mașina proprie marcată, cu viteza și poziția în cursă; treapta, accelerația și frâna proprii
- începutul sesiunii cu pista numită de joc; ture pe fiecare mașină, cu timpul turei; sosiri; opririle proprii la boxe
- teleportările (înapoi la boxe, o repornire): `teleport` unde se afla mașina, `spawn` unde se află acum
- turele proprii, cea mai bună tură, poziția în cursă, distanța, viteza maximă
- toată pagina de memorie partajată a jocului în `heat.raw.parquet`, de fiecare dată când se schimbă

## De unde vine {#where-it-comes-from}

memoria partajată $pcars2$ (SMS SharedMemory.h)

## Cum se activează {#how-to-switch-it-on}

În joc: Options > System > Shared Memory: „Project CARS 2”

## Cum funcționează {#how-it-works}

Memorie partajată pe care jocurile de curse o publică pentru tablouri de bord, deschisă doar pentru citire - și niciodată creată.

Mai mulți simulatori își livrează telemetria ca un mapping de fișier Windows cu nume, pe care jocul îl creează și pe care oricine îl poate citi: paginile `Local\acpmf_*` ale Kunos (Assetto Corsa, ACC, AC Rally, `Local\acevo_pmf_*` ale AC EVO), `Local\IRSDKMemMapFileName` al iRacing, `$R3E` al RaceRoom și `$pcars2$` al Automobilista 2 / Project CARS 2.

De ce nu `mmap.mmap(-1, size, tagname=...)`, modul obișnuit în Python: când mapingul nu există încă, îl *creează* - aici, doar pentru citire. Un joc pornit după aceea deschide mapingul watcher-ului în loc să-l facă pe al său și apoi nu poate scrie în el, deci telemetria lui este moartă până când watcher-ul îl eliberează. Watcher-ul pornește un adaptor imediat ce apare procesul jocului, adică exact momentul în care jocul nu și-a făcut încă mapingul. Așa că aici se deschide cu `OpenFileMappingW`, care găsește doar un mapping existent, îl mapează cu `FILE_MAP_READ` și raportează „încă nu” în rest; adaptoarele încearcă din nou puțin mai târziu.

Nimic de aici nu poate scrie: vederea este mapată doar pentru citire și este copiată doar cu `ctypes.string_at`.

Aici sunt citite și alte două jocuri; fiecare mașină de pe circuit se află în paginile lor.

#### Automobilista 2 / Project CARS 2 - `$pcars2$` {#automobilista-2--project-cars-2---pcars2}

`SharedMemory.h` al SMS (livrat în folderul Support\SharedMemory al jocului; AMS2: Options > System > Shared Memory „Project CARS 2”), `#pragma pack(4)`. `mParticipantInfo[64]` de la octetul 28, câte 100 de octeți fiecare: mIsActive, mName[64], mWorldPosition[3] (m, Y în sus), mCurrentLapDistance, mRacePosition, mLapsCompleted, mCurrentLap, mCurrentSector; mViewedParticipantIndex (20) este mașina jucătorului; pentru fiecare participant mLastLapTimes (9200), mRaceStates (9520), mSpeeds (10800); cea mai bună tură a jucătorului mBestLapTime (6716), mLastLapTime (6720), mSpeed (6848), mBrake, mThrottle, mGear; mSequenceNumber (7320) este impar cât timp jocul scrie. Offsetele au fost stabilite din două copii independente ale antetului (copia jocului nu este instalată aici), care coincid.

Ambele pagini sunt păstrate întregi în plus (docs/converters.md, „Live sources”): toată mapa, la fiecare citire ale cărei octeți diferă de copia păstrată ultima dată, în sidecar-ul brut al sesiunii, cu `type` `r3e` sau `pcars2` - fiecare slot de participant și fiecare câmp al structurii, și cele necitite aici, deci un decodor ulterior are nevoie doar de sidecar.

Același modul servește și: [Automobilista 2 (date în direct)](game-automobilista-2.md), [RaceRoom Racing Experience (date în direct)](game-raceroom.md).

## Poziții și axe {#positions-and-axes}

| | |
|---|---|
| Poziții înregistrate | da |
| Axa verticală | `y` |
| Unități | metri |
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

- pe participant (până la 64): activ, nume, poziție în lume, poziție în cursă, ture terminate; ultimul timp de tură, starea de cursă și viteza
- mașina jucătorului (mViewedParticipantIndex), starea jocului și a sesiunii, locul și varianta pistei, cea mai bună tură și ultima, viteza, frâna, accelerația, treapta; mSequenceNumber pentru a sări peste o copie prinsă în mijlocul scrierii
- offsetele din două copii independente ale SharedMemory.h de la SMS, care coincid, verificate în teste pe o pagină construită din ele; încă nu față de joc

**Păstrat brut**

- `pcars2`: toată mapa $pcars2$ - structura se întinde mult peste cei 11.312 octeți citiți aici - la fiecare citire ale cărei octeți diferă de copia păstrată ultima dată: orientarea fiecărui participant, timpii pe sectoare, numele mașinilor și ale claselor, modurile și indicatorii de la boxe, fizica jucătorului, pneurile, suspensia, avariile, vremea și tot ce au adăugat versiunile ulterioare ale Project CARS 2
- `used` este adevărat pentru o pagină citită în rânduri; fals pentru una din meniuri, pe pauză, într-o reluare, de alt layout sau prinsă în mijlocul scrierii (`torn` 1); `unchanged_reads` din meta.json numără citirile identice octet cu octet cu copia păstrată înainte

**Nu este disponibil**

- inputurile și fizica celorlalți participanți: pagina dă doar mașina privită
- tot ce cât timp opțiunea de memorie partajată a jocului este oprită (Project CARS 2 nu scrie nimic atunci)

**Dimensiune**: mapa are aproximativ 20 până la 30 KB (după versiunea jocului), până la de 10 ori pe secundă în timpul condusului: aproximativ 0,7 până la 1,1 GB pe oră înainte de compresie; zstd micșorează sloturile goale de participanți și numele care nu se schimbă la o fracțiune (nemăsurat încă pe o sesiune reală)

## Verificat {#verified}

testat pe o pagină construită în test; offsetele din două copii independente ale SharedMemory.h care coincid, nu din copia livrată cu jocul; netestat cu jocul

## Sursă {#source}

[heat3d_watch/adapters/simracing_shm.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/simracing_shm.py)

<!-- Generated from the adapter by tools/gen_game_pages.py; change the adapter and run it again rather than editing this page. -->
