---
title: "EA SPORTS F1 25 (podaci uživo)"
nav_order: 16
lang: "bs"
source: game-f1-25.md
source_hash: "7476dbb3b308"
nav_exclude: true
search_exclude: true
---
# EA SPORTS F1 25 (podaci uživo) {#ea-sports-f1-25-live-data}

Dok igrate EA SPORTS F1 25, watcher sprema podatke koje igra sama šalje, da ih poslije možete pogledati na mapi u pregledniku 3DHeat.

*Tehnički detalji: adapter `f1-25`, vrsta [`telemetry`](sources-and-rules.md); radi dok radi `F1_25.exe` i svakih 0,1 s traži nove podatke.*

## Šta se snima {#what-is-recorded}

- pozicija svakog automobila (svjetski XYZ, m) na 10 Hz, po imenu vozača, timu, vlastiti automobil označen (`own_car` 1, iz indeksa igračevog automobila), s brzinom, stepenom prijenosa, gasom, kočnicom, upravljanjem, rpm, DRS, yaw, pitch, roll (stepeni) i g-silama
- krugovi po automobilu s vremenom kruga i pozicijom u utrci; ciljevi i odustajanja
- događaji utrke u igri: početak i kraj sesije, najbrži krug, kazne, preticanja, sudari, safety car, crvena zastava, startna svjetla, kockasta zastava, pobjednik, flashbackovi (`teleport` gdje je automobil bio, `spawn` gdje se vratio)
- staza, tip sesije, krugovi i vozači svake sesije
- vlastiti krugovi, najbolji krug, pozicija u utrci i na startu, zaustavljanja u boksu, kazne, preticanja, sudari, udaljenost, najveća brzina
- svaki paket koji igra šalje, cijel, u `heat.raw.parquet` - i oni koji nisu pročitani u redove

## Odakle dolazi {#where-it-comes-from}

UDP telemetrija 127.0.0.1:20777 (Documents\My Games\F1 25\hardwaresettings\hardware_settings_config.xml)

## Kako to uključiti {#how-to-switch-it-on}

U igri: Settings > Telemetry Settings > UDP Telemetry On, IP 127.0.0.1, port 20777 - ili `python -m heat3d_watch setup f1-25 --apply` (uređuje hardware_settings_config.xml, prvo se pravi backup; igra mora biti zatvorena). Dok port 20777 drži druga aplikacija, watcher joj ostavlja port

Komandu upišite u terminal otvoren u folderu watchera (vidite [Prije nego počnete](before-you-start.md)). Ako ne uspije, zadnja linija kaže zašto; [Instalacija i pokretanje](installing-and-running.md) opisuje uobičajene uzroke.

`python -m heat3d_watch setup f1-25` navodi datoteke koje bi promijenio; `python -m heat3d_watch setup f1-25 --apply` ih mijenja i čuva original kao `<file>.heat3d-backup` (vidite [Komande](commands.md#setup)). Za svaku promjenu ispisuje `f1-25: changed: ...`, ili `f1-25: nothing to change` kad je već uključeno.

## Kako radi {#how-it-works}

EA SPORTS F1 23, F1 24 i F1 25: službena UDP telemetrija, svaki automobil na stazi.

Igre je šalju same (Settings > Telemetry Settings, ili
`Documents/My Games/<F1 xx>/hardwaresettings/hardware_settings_config.xml`,
`<udp enabled="true" ip="127.0.0.1" port="20777" sendRate="20" format="2025" ...>`).
Little-endian, packed, zaglavlje od 29 bajtova na svakom paketu (isto u formatima
2023, 2024 i 2025):

```text
uint16 packetFormat, uint8 gameYear, gameMajorVersion, gameMinorVersion,
packetVersion, packetId, uint64 sessionUID, float sessionTime,
uint32 frameIdentifier, overallFrameIdentifier, uint8 playerCarIndex,
secondaryPlayerCarIndex
```

Šta se čita, po id-u paketa:

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

Svaki paket se čuva i cijel, onako kako je stigao, u sirovom sidecaru sesije
(`heat.raw.parquet`, `type` je ime paketa - `motion`, `car_status` ... -
s `format`, `packet_id`, `frame` i `session_uid`) - i oni koji se čitaju gore i oni koje
još ništa ne čita: 5 Car Setups, 7 Car Status, 8 Final Classification, 9 Lobby
Info, 10 Car Damage, 11 Session History, 12 Tyre Sets, 13 Motion Ex, 14 Time
Trial, 15 Lap Positions, svaki kasniji id, i paketi u formatu koji ovo ne
čita. Tako kasnijem dekoderu treba samo sidecar.

Pozicija svakog automobila je u Motion paketu - i online, gdje ju igra
sama daje (samo podaci o gorivu, ERS-u, šteti i setovima guma zadržavaju se
za igrače kojima je "Your Telemetry" ograničen). Svaki automobil se snima na
oko 10 Hz pod imenom učesnika ("car N" dok imena ne stignu), tim
po imenu, a igračev vlastiti automobil označen je kao `own`.

Izvori: EA-ova "F1 25 UDP Specification" (forums.ea.com, F1 games info hub),
specifikacije za F1 23 i F1 24; iste tabele zrcaljene u
MacManley/f1-25-udp (MIT). Paketi u testovima grade se iz ovih rasporeda.

Isti modul služi i: [EA SPORTS F1 23 (podaci uživo)](game-f1-23.md), [EA SPORTS F1 24 (podaci uživo)](game-f1-24.md).

## Pozicije i ose {#positions-and-axes}

| | |
|---|---|
| Pozicije se snimaju | da |
| Osa gore | `y` |
| Jedinice | metri |
| Zrcaljeno za preglednik | nijedna |
| Skala jedinica (`scale`: preglednik njome množi pozicije) | 1 |

Ovo ide u `meta.json` svake sesije (`axes`) i, kad sesija ima pozicije, u podnožje datoteke `heat.parquet`, pa preglednik 3DHeat sam rotira i skalira redove - vidite [Podaci](the-data.md).

## Multiplayer {#multiplayer}

- Označeno kao igrano online (`multiplayer`): **da**. `games --markdown` to prikazuje kao "dozvoljeno (čita samo ono što igra objavljuje)".
- Vrsta `telemetry`: čita samo ono što igra ili platforma daje (UDP port ili dijeljena memorija koju igra objavljuje), pa snima i u online igri kao i offline; zastavica odlučuje samo smije li se memorija ikad čitati.
- Memorija: ovaj adapter je **nikad** ne čita. Memoriju čitaju samo `memory` adapteri, i to nikad za igru označenu kao igranu online - vidite [Izvori i pravila](sources-and-rules.md).

## Zabilježene statistike {#statistics-recorded}

Ključevi statistika koje kod ovog adaptera postavlja po imenu (`stats` svake sesije u `meta.json` i tabela `stats` u `watcher.sqlite`):

`best_lap`, `collisions`, `distance_km`, `fastest_laps`, `finishes`, `flashbacks`, `grid_position`, `laps`, `overtaken`, `overtakes`, `penalties`, `penalty_seconds`, `pit_stops`, `race_position`, `sessions`, `top_speed_kmh`, `wins`

Ključ u vitičastim zagradama dovršava se za vrijeme rada (`score.{team}` je jedan ključ po timu). Ključevi koje kod uzima iz tabele polja igre ili iz igrinih vlastitih imena statistika nisu na ovoj listi; "Šta se snima" iznad ih navodi.

## Potpunost {#completeness}

Watcher slijedi 3DHeatovo [pravilo konvertera](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md): ono što izvor drži čita se ili čuva, nikad ne odbacuje. Osim redova, svaki paket, stranica, linija ili odgovor koji adapter primi čuva se cijel u `heat.raw.parquet` sesije (kolone `time`, `ms`, `type`, `used`, `payload`, `text`, zatim svako polje čuvano po imenu; `used` označava šta je postalo i redovi), a `selfCheck.completeness` u `meta.json` broji svaki `type` - `lost` je 0.

**Čita se**

- 0 Motion: svjetska pozicija i brzina svakog automobila, a sada i yaw, pitch, roll (stepeni, iz radijana u specifikaciji) i bočna, uzdužna i vertikalna g-sila, na redovima pozicije svakog automobila
- 1 Session: staza, tip sesije, ukupno krugova, dužina staze, online ili ne (meta.json `sessions`)
- 2 Lap Data: zadnje vrijeme kruga, broj kruga, pozicija u utrci i na startu, zaustavljanja u boksu, kazne, status rezultata (krugovi, ciljevi, odustajanja, statistike)
- 3 Event: svaki kod osim BUTN kao vlastiti red, s njegovim detaljima
- 4 Participants: imena vozača, timovi, broj aktivnih automobila (`player` i `team` redova, meta.json `drivers`)
- 6 Car Telemetry: brzina, stepen prijenosa, gas, kočnica, a sada i upravljanje (-1..1), rpm i DRS, na redovima pozicije svakog automobila
- provjereno prema EA-ovim objavljenim UDP specifikacijama za formate 2023, 2024 i 2025 (veličine paketa potvrđene u testovima); još ne prema igri

**Čuva se sirovo**

- svaki paket cijel u `heat.raw.parquet`, `payload` je datagram, `type` je ime njegovog id-a: `motion`, `session`, `lap_data`, `event`, `participants`, `car_setups`, `car_telemetry`, `car_status`, `final_classification`, `lobby_info`, `car_damage`, `session_history`, `tyre_sets`, `motion_ex`, `time_trial`, `lap_positions` (`packet <n>` za id koji specifikacije još ne navode); kolone `format` (2023/2024/2025), `packet_id`, `frame`, `session_uid`
- `used` je true za pakete koji se čitaju gore (Motion, Session, Lap Data, Participants, Car Telemetry i kodovi Event osim BUTN); ostalo - car setups, car status (gorivo, ERS, vrsta i starost guma, zastavice), final classification, lobby, car damage, session history (svako vrijeme kruga i sektora po automobilu), tyre sets, motion ex (ovjes vlastitog automobila, brzine točkova, lokalna brzina, ugaona brzina i ubrzanje), time trial, lap positions, BUTN događaji tastera - čuva se za kasniji dekoder
- `format <year>`: paket u formatu prije 2023 (drugačiji raspored zaglavlja), cijel; `short`: datagram kraći od zaglavlja od 29 bajtova, cijel

**Nije dostupno**

- gorivo, ERS, šteta i setovi guma drugih igrača online kad im je "Your Telemetry" ograničen: igra za njih šalje nule
- paketi poslani dok watcher ne radi, ili dok port 20777 drži druga aplikacija: igra ne sprema UDP

**Veličina**: pri brzini slanja od 60 Hz svaki paket je oko 0,38 MB/s (Motion, Lap Data, Car Telemetry, Car Status i Motion Ex na 60 Hz, Session History i Tyre Sets na 20/s, Car Damage na 10/s, Session i Car Setups na 2/s) plus oko 0,03 MB/s zaglavlja stavki: oko 1,5 GB na sat vožnje prije kompresije, oko 0,55 GB pri zadanih 20 Hz; zstd to svodi na djelić (prazni slotovi automobila i ponovljene vrijednosti dobro se komprimiraju; još nije mjereno na pravoj sesiji)

## Provjereno {#verified}

testirano na paketima u formatima 2023, 2024 i 2025 izgrađenim iz EA-ove objavljene specifikacije, poslanim preko UDP-a; neprovjereno na igri

## Izvor {#source}

[heat3d_watch/adapters/f1.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/f1.py)

<!-- Generated from the adapter by tools/gen_game_pages.py; change the adapter and run it again rather than editing this page. -->
