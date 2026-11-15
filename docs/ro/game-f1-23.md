---
title: "EA SPORTS F1 23 (date în timp real)"
nav_order: 14
lang: "ro"
source: game-f1-23.md
source_hash: "d7b523188e51"
nav_exclude: true
search_exclude: true
---
# EA SPORTS F1 23 (date în timp real) {#ea-sports-f1-23-live-data}

Cât joci EA SPORTS F1 23, watcher-ul salvează datele pe care jocul însuși le trimite afară, ca să te poți uita mai târziu la ele pe o hartă în vizualizatorul 3DHeat.

*Detalii tehnice: adaptorul `f1-23`, tip [`telemetry`](sources-and-rules.md); rulează cât timp `F1_23.exe` este pornit și caută date noi la fiecare 0,1 s.*

## Ce se înregistrează {#what-is-recorded}

- poziția (XYZ în lume, m) fiecărei mașini, de 10 ori pe secundă, după numele pilotului, echipă, cu mașina ta marcată (`own_car` 1, din indexul mașinii jucătorului), cu viteza, treapta, accelerația, frâna, direcția, turația, DRS, yaw, pitch, roll (grade) și forțele g
- ture per mașină, cu timpul de tur și poziția în cursă; sosiri și abandonuri
- evenimentele cursei: începutul și sfârșitul sesiunii, cel mai rapid tur, penalizări, depășiri, coliziuni, mașina de siguranță, steagul roșu, luminile de start, steagul în carouri, câștigătorul, flashback-urile (`teleport` unde era mașina, `spawn` unde a revenit)
- pista, tipul sesiunii, numărul de ture și piloții fiecărei sesiuni
- turele tale, cel mai bun tur, poziția în cursă și la start, opriri la boxe, penalizări, depășiri, coliziuni, distanța, viteza maximă
- fiecare pachet trimis de joc, integral, în `heat.raw.parquet` - și cele care nu intră în rânduri

## De unde vine {#where-it-comes-from}

telemetrie UDP 127.0.0.1:20777 (Documents\My Games\F1 23\hardwaresettings\hardware_settings_config.xml)

## Cum o pornești {#how-to-switch-it-on}

În joc: Settings > Telemetry Settings > UDP Telemetry On, IP 127.0.0.1, port 20777 - sau `python -m heat3d_watch setup f1-23 --apply` (editează hardware_settings_config.xml, cu backup înainte; jocul trebuie închis). Cât timp altă aplicație ține portul 20777, watcher-ul îl lasă ei

Scrie comanda într-un terminal deschis în folderul watcher-ului (vezi [Înainte de a începe](before-you-start.md)). Dacă eșuează, ultima linie spune de ce; [Instalarea și rularea](installing-and-running.md) acoperă cauzele obișnuite.

`python -m heat3d_watch setup f1-23` arată ce fișiere ar schimba; `python -m heat3d_watch setup f1-23 --apply` le schimbă, păstrând originalul ca `<file>.heat3d-backup` (vezi [Comenzi](commands.md#setup)). Afișează `f1-23: changed: ...` pentru fiecare modificare, sau `f1-23: nothing to change` dacă este deja pornit.

## Cum funcționează {#how-it-works}

EA SPORTS F1 23, F1 24 și F1 25: telemetria UDP oficială, fiecare mașină de pe pistă.

Jocurile o trimit singure (Settings > Telemetry Settings, sau `Documents/My Games/<F1 xx>/hardwaresettings/hardware_settings_config.xml`, `<udp enabled="true" ip="127.0.0.1" port="20777" sendRate="20" format="2025" ...>`). Little-endian, împachetat, cu un antet de 29 de octeți la fiecare pachet (același în formatele 2023, 2024 și 2025):

```text
uint16 packetFormat, uint8 gameYear, gameMajorVersion, gameMinorVersion,
packetVersion, packetId, uint64 sessionUID, float sessionTime,
uint32 frameIdentifier, overallFrameIdentifier, uint8 playerCarIndex,
secondaryPlayerCarIndex
```

Ce se citește, pe id de pachet:

```text
0 Motion        CarMotionData[22], 60 bytes each: world position x y z
                (metres; Y is up), world velocity, forward and right
                vectors (int16 / 32767), g-forces, yaw pitch roll
1 Session       weather, temperatures, total laps, track length, session
                type, track id, ... network game
2 Lap Data      LapData[22]: last lap time, lap distance, race position,
                current lap number, pit stops, penalties, grid position,
                driver and result status. 50 bytes per car in 2023; 57 in
                2024 and 2025, which added the minutes parts of the deltas
                and the speed trap.
3 Event         a four-letter code and a union of details: SSTA SEND FTLP
                RTMT DRSE DRSD TMPT CHQF RCWN PENA SPTP STLG LGOT DTSV SGSV
                FLBK BUTN RDFL OVTK SCAR COLL
4 Participants  ParticipantData[22]: AI or human, driver, team, race
                number, name (48 bytes in 2023 and 2024, 32 in 2025; 58,
                60 and 57 bytes per car)
6 Car Telemetry CarTelemetryData[22], 60 bytes: speed km/h, throttle,
                steer, brake, clutch, gear, rpm, DRS ...
```

Fiecare pachet este păstrat și integral, cum a venit, în sidecar-ul brut al sesiunii (`heat.raw.parquet`, `type` numele pachetului - `motion`, `car_status` ... - cu `format`, `packet_id`, `frame` și `session_uid`) - cele citite mai sus și cele pe care nimic nu le citește încă: 5 Car Setups, 7 Car Status, 8 Final Classification, 9 Lobby Info, 10 Car Damage, 11 Session History, 12 Tyre Sets, 13 Motion Ex, 14 Time Trial, 15 Lap Positions, orice id ulterior și pachetele într-un format pe care nu-l citește acest modul. Deci un decodor ulterior are nevoie doar de sidecar.

Poziția fiecărei mașini este în pachetul Motion - și online, acolo unde jocul o scoate singur (doar combustibilul, ERS, daunele și datele setului de anvelope sunt ținute ascunse pentru jucătorii al căror „Your Telemetry” este restricționat). Fiecare mașină este înregistrată la circa 10 Hz sub numele ei de participant („car N” până sosesc numele), echipa după nume, iar mașina jucătorului este marcată `own`.

Surse: „F1 25 UDP Specification” al EA (forums.ea.com, hub-ul de informații despre jocurile F1), specificațiile F1 23 și F1 24; aceleași tabele oglindite în MacManley/f1-25-udp (MIT). Pachetele din teste sunt construite după aceste layout-uri.

Același modul servește și: [EA SPORTS F1 24 (date în timp real)](game-f1-24.md), [EA SPORTS F1 25 (date în timp real)](game-f1-25.md).

## Poziții și axe {#positions-and-axes}

| | |
|---|---|
| Poziții înregistrate | da |
| Axa în sus | `y` |
| Unități | metri |
| Oglindită pentru vizualizator | niciuna |
| Scara unității (`scale`: vizualizatorul înmulțește pozițiile cu ea) | 1 |

Acestea intră în `meta.json` al fiecărei sesiuni (`axes`) și, când sesiunea are poziții, în subsolul `heat.parquet`, așa că vizualizatorul 3DHeat rotește și scalează singur rândurile - vezi [Datele](the-data.md).

## Joc online {#multiplayer}

- Marcat ca jucat online (`multiplayer`): **da**. `games --markdown` arată asta ca „permis (citește doar ce publică jocul)”.
- Tip `telemetry`: citește doar ce scoate jocul sau platforma (un port UDP sau o memorie partajată publicată de joc), deci înregistrează și în jocul online, nu doar offline; steagul decide doar dacă memoria are voie să fie citită vreodată.
- Memorie: **niciodată** citită de acest adaptor. Doar adaptoarele `memory` citesc memoria, și niciodată pentru un joc marcat ca jucat online - vezi [Surse și reguli](sources-and-rules.md).

## Statistici înregistrate {#statistics-recorded}

Cheile de statistică pe care codul acestui adaptor le setează după nume (`stats` din `meta.json` al fiecărei sesiuni și tabelul `stats` din `watcher.sqlite`):

`best_lap`, `collisions`, `distance_km`, `fastest_laps`, `finishes`, `flashbacks`, `grid_position`, `laps`, `overtaken`, `overtakes`, `penalties`, `penalty_seconds`, `pit_stops`, `race_position`, `sessions`, `top_speed_kmh`, `wins`

O cheie între acolade se completează la rulare (`score.{team}` este câte o cheie pentru fiecare echipă). Cheile pe care codul le ia dintr-un tabel de câmpuri ale jocului sau din numele statisticilor jocului nu sunt în această listă; „Ce se înregistrează” de mai sus le numește.

## Completitudine {#completeness}

Watcher-ul urmează [regula de convertor](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md) a 3DHeat: ce are sursa este citit sau păstrat, niciodată aruncat. În afară de rânduri, fiecare pachet, pagină, linie sau răspuns pe care îl primește adaptorul este păstrat integral în `heat.raw.parquet` al sesiunii (coloanele `time`, `ms`, `type`, `used`, `payload`, `text`, apoi orice câmp păstrat după nume; `used` marchează ce a devenit și rând), iar `selfCheck.completeness` din `meta.json` numără fiecare `type` - `lost` este 0.

**Citit**

- 0 Motion: poziția și viteza lumii ale fiecărei mașini, și acum și yaw, pitch, roll (grade, din radianii specificației) și forța g laterală, longitudinală și verticală, pe rândurile de poziție ale fiecărei mașini
- 1 Session: pista, tipul sesiunii, numărul total de ture, lungimea pistei, online sau nu (`sessions` în meta.json)
- 2 Lap Data: ultimul timp de tur, numărul turului, poziția în cursă și la start, opriri la boxe, penalizări, starea rezultatului (ture, sosiri, abandonuri, statistici)
- 3 Event: fiecare cod, în afară de BUTN, ca rând propriu, cu detaliile lui
- 4 Participants: numele piloților, echipele, numărul de mașini active (`player` și `team` din rânduri, `drivers` în meta.json)
- 6 Car Telemetry: viteza, treapta, accelerația, frâna, și acum și direcția (-1..1), turația și DRS, pe rândurile de poziție ale fiecărei mașini
- verificat cu specificațiile UDP publicate de EA pentru formatele 2023, 2024 și 2025 (dimensiunile pachetelor, afirmate în teste); încă nu pe joc

**Păstrat brut**

- fiecare pachet integral în `heat.raw.parquet`, `payload` datagrama, `type` numele id-ului său: `motion`, `session`, `lap_data`, `event`, `participants`, `car_setups`, `car_telemetry`, `car_status`, `final_classification`, `lobby_info`, `car_damage`, `session_history`, `tyre_sets`, `motion_ex`, `time_trial`, `lap_positions` (`packet <n>` pentru un id pe care specificațiile nu-l listează încă); coloanele `format` (2023/2024/2025), `packet_id`, `frame`, `session_uid`
- `used` este adevărat pentru pachetele citite mai sus (Motion, Session, Lap Data, Participants, Car Telemetry și codurile de Event, în afară de BUTN); restul - setările mașinii, starea mașinii (combustibil, ERS, tipul și vârsta anvelopelor, steaguri), clasificarea finală, lobby-ul, daunele mașinii, istoricul sesiunii (fiecare timp de tur și de sector per mașină), seturile de anvelope, motion ex (suspensia mașinii proprii, vitezele roților, viteza locală, viteza și accelerația unghiulară), time trial, pozițiile pe ture, evenimentele de buton BUTN - sunt păstrate pentru un decodor ulterior
- `format <an>`: un pachet într-un format dinainte de 2023 (alt layout de antet), integral; `short`: o datagramă mai scurtă decât antetul de 29 de octeți, integral

**Nedisponibil**

- combustibilul, ERS-ul, daunele și seturile de anvelope ale altor jucători, online, când „Your Telemetry” lor este restricționat: jocul trimite zerouri pentru ei
- pachetele trimise cât watcher-ul nu rulează sau cât altă aplicație ține portul 20777: UDP nu este stocat de joc

**Dimensiune**: la o rată de trimitere de 60 Hz, fiecare pachet are aproximativ 0,38 MB/s (Motion, Lap Data, Car Telemetry, Car Status și Motion Ex la 60 Hz, Session History și Tyre Sets la 20/s, Car Damage la 10/s, Session și Car Setups la 2/s) plus circa 0,03 MB/s de antete de elemente: aproximativ 1,5 GB pe oră de condus înainte de compresie, aproximativ 0,55 GB la rata implicită de 20 Hz; zstd o reduce la o fracțiune din asta (sloturile goale de mașini și valorile care se repetă se comprimă bine; încă nemăsurat pe o sesiune reală)

## Verificat {#verified}

testat pe pachete în formatele 2023, 2024 și 2025 construite după specificația publicată de EA, trimise prin UDP; netestat cu jocul

## Sursă {#source}

[heat3d_watch/adapters/f1.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/f1.py)

<!-- Generated from the adapter by tools/gen_game_pages.py; change the adapter and run it again rather than editing this page. -->
