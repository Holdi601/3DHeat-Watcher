---
title: "EA SPORTS F1 24 (živi podaci)"
nav_order: 15
lang: "hr"
source: game-f1-24.md
source_hash: "a189298930fc"
nav_exclude: true
search_exclude: true
---
# EA SPORTS F1 24 (živi podaci) {#ea-sports-f1-24-live-data}

Dok igrate EA SPORTS F1 24, watcher sprema podatke koje sama igra šalje van, pa to kasnije možete pogledati na karti u 3DHeat pregledniku.

*Tehnički podaci: adapter `f1-24`, vrsta [`telemetry`](sources-and-rules.md); radi dok je `F1_24.exe` pokrenut i traži nove podatke svakih 0,1 s.*

## Što se bilježi {#what-is-recorded}

- pozicija svakog automobila (svjetski XYZ, m) 10 puta u sekundi, po imenu vozača, timu, vlastiti automobil označen (`own_car` 1, iz indeksa igračeva automobila), s brzinom, brzinom u stupnju, gasom, kočnicom, upravljanjem, okretajima, DRS-om, skretanjem, nagibom i rotacijom (stupnjevi) te g-silama
- krugovi po automobilu s vremenom kruga i pozicijom u utrci; završetci i odustajanja
- događaji utrke iz igre: početak i kraj sesije, najbrži krug, kazne, preticanja, sudari, sigurnosni automobil, crvena zastava, svjetla na startu, karirana zastava, pobjednik, povratak u prošlost (`teleport` gdje je automobil bio, `spawn` gdje se vratio)
- staza, vrsta sesije, krugovi i vozači svake sesije
- vlastiti krugovi, najbolji krug, pozicija u utrci i na startu, zaustavljanja u boksu, kazne, preticanja, sudari, udaljenost, najveća brzina
- svaki paket koji igra šalje, cjelovit, u `heat.raw.parquet` - i oni koji nisu pročitani u retke

## Odakle dolazi {#where-it-comes-from}

UDP telemetrija 127.0.0.1:20777 (Documents\My Games\F1 24\hardwaresettings\hardware_settings_config.xml)

## Kako ga uključiti {#how-to-switch-it-on}

U igri: Settings > Telemetry Settings > UDP Telemetry On, IP 127.0.0.1, port 20777 - ili `python -m heat3d_watch setup f1-24 --apply` (mijenja hardware_settings_config.xml, prije toga se sprema sigurnosna kopija; igra mora biti zatvorena). Dok druga aplikacija drži 20777, watcher port prepušta njoj.

Upišite naredbu u terminal otvoren u mapi watchera (vidi [Prije nego što počnete](before-you-start.md)). Ako ne uspije, zadnji redak kaže zašto; [Instalacija i pokretanje](installing-and-running.md) opisuje najčešće uzroke.

`python -m heat3d_watch setup f1-24` navodi datoteke koje bi promijenio; `python -m heat3d_watch setup f1-24 --apply` ih mijenja i čuva original kao `<file>.heat3d-backup` (vidi [Naredbe](commands.md#setup)). Za svaku promjenu ispisuje `f1-24: changed: ...`, a kad je već uključeno, `f1-24: nothing to change`.

## Kako radi {#how-it-works}

EA SPORTS F1 23, F1 24 i F1 25: službena UDP telemetrija, svaki automobil na stazi.

Igre je šalju same (Settings > Telemetry Settings, ili `Documents/My Games/<F1 xx>/hardwaresettings/hardware_settings_config.xml`, `<udp enabled="true" ip="127.0.0.1" port="20777" sendRate="20" format="2025" ...>`). Little-endian, zbijeno, zaglavlje od 29 bajtova na svakom paketu (isto u formatima 2023, 2024 i 2025):

```text
uint16 packetFormat, uint8 gameYear, gameMajorVersion, gameMinorVersion,
packetVersion, packetId, uint64 sessionUID, float sessionTime,
uint32 frameIdentifier, overallFrameIdentifier, uint8 playerCarIndex,
secondaryPlayerCarIndex
```

Što se čita, po ID-u paketa:

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

Svaki paket se čuva i cjelovito, kako je došao, u sirovoj pomoćnoj datoteci sesije (`heat.raw.parquet`, `type` je ime paketa - `motion`, `car_status` ... - uz `format`, `packet_id`, `frame` i `session_uid`) - i oni koje gore čitamo i oni koje ništa još ne čita: 5 Car Setups, 7 Car Status, 8 Final Classification, 9 Lobby Info, 10 Car Damage, 11 Session History, 12 Tyre Sets, 13 Motion Ex, 14 Time Trial, 15 Lap Positions, svaki kasniji ID, i paketi u formatu koji ovo ne čita. Zato kasniji dekoder treba samo sirovu datoteku.

Pozicija svakog automobila je u Motion paketu - i na mreži, gdje je igra sama daje (samo gorivo, ERS, oštećenja i podaci o gumama zadržavaju se za igrače čija je "Your Telemetry" ograničena). Svaki se automobil bilježi oko 10 Hz pod imenom sudionika ("car N" dok imena ne stignu), tim po imenu, a vlastiti automobil igrača označen je kao `own`.

Izvori: EA-ova "F1 25 UDP Specification" (forums.ea.com, F1 games info hub), specifikacije za F1 23 i F1 24; iste tablice zrcaljene u MacManley/f1-25-udp (MIT). Paketi u testovima grade se prema ovim rasporedima.

Isti modul služi i za: [EA SPORTS F1 23 (živi podaci)](game-f1-23.md), [EA SPORTS F1 25 (živi podaci)](game-f1-25.md).

## Pozicije i osi {#positions-and-axes}

| | |
|---|---|
| Pozicije se bilježe | da |
| Os prema gore | `y` |
| Jedinice | metri |
| Zrcaljeno za preglednik | nijedna |
| Mjerilo jedinice (`scale`: preglednik pozicije množi njime) | 1 |

Ovo ide u `meta.json` svake sesije (`axes`) i, kad sesija ima pozicije, u podnožje `heat.parquet`, pa 3DHeat preglednik sam okreće i skalira retke - vidi [Podaci](the-data.md).

## Više igrača {#multiplayer}

- Označeno kao igra na mreži (`multiplayer`): **da**. `games --markdown` to prikazuje kao "allowed (reads only what the game publishes)".
- Vrsta `telemetry`: čita samo ono što igra ili platforma daje (UDP port ili dijeljena memorija koju igra objavljuje), pa bilježi i u igri na mreži i izvan nje; zastavica odlučuje samo smije li se ikad čitati memorija.
- Memorija: ovaj adapter je **nikad** ne čita. Samo adapteri `memory` čitaju memoriju, i nikad za igru označenu kao igra na mreži - vidi [Izvori i pravila](sources-and-rules.md).

## Statistika koja se bilježi {#statistics-recorded}

Ključevi statistike koje kod ovog adaptera postavlja po imenu (`stats` svake sesije u `meta.json` i tablica `stats` u `watcher.sqlite`):

`best_lap`, `collisions`, `distance_km`, `fastest_laps`, `finishes`, `flashbacks`, `grid_position`, `laps`, `overtaken`, `overtakes`, `penalties`, `penalty_seconds`, `pit_stops`, `race_position`, `sessions`, `top_speed_kmh`, `wins`

Ključ u vitičastim zagradama dovršava se pri radu (`score.{team}` je jedan ključ za svaki tim). Ključevi koje kod uzima iz tablice polja igre ili iz vlastitih imena statistike igre nisu na ovom popisu; navedeni su u odjeljku "Što se bilježi" gore.

## Potpunost {#completeness}

Watcher slijedi [pravilo pretvarača 3DHeata](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md): ono što izvor sadrži se čita ili čuva, nikad se ne odbacuje. Osim redaka, svaki paket, stranica, redak ili odgovor koji adapter primi čuva se cjelovito u `heat.raw.parquet` sesije (stupci `time`, `ms`, `type`, `used`, `payload`, `text`, pa svako polje koje je sačuvano po imenu; `used` označava što je postalo i retkom), a `selfCheck.completeness` u `meta.json` broji svaki `type` - `lost` je 0.

**Čita se**

- 0 Motion: svaka pozicija i brzina svakog automobila u svijetu, a sada i zakret, nagib, valjanje (stupnjevi, iz radijana u specifikaciji) i bočna, uzdužna i vertikalna g-sila, na retcima pozicije svakog automobila
- 1 Session: staza, vrsta sesije, ukupni krugovi, duljina staze, na mreži ili ne (`sessions` u meta.json)
- 2 Lap Data: vrijeme zadnjeg kruga, broj kruga, pozicija u utrci i na startu, zaustavljanja u boksu, kazne, status rezultata (krugovi, završetci, odustajanja, statistika)
- 3 Event: svaki kod osim BUTN kao zaseban redak, s detaljima
- 4 Participants: imena vozača, timovi, broj aktivnih automobila (`player` i `team` u retcima, `drivers` u meta.json)
- 6 Car Telemetry: brzina, brzina u stupnju, gas, kočnica, a sada i upravljanje (-1..1), okretaji i DRS, na retcima pozicije svakog automobila
- provjereno prema EA-ovim objavljenim UDP specifikacijama za formate 2023, 2024 i 2025 (veličine paketa tvrde se u testovima); još nije provjereno na igri

**Čuva se u izvornom obliku**

- svaki paket cjelovit u `heat.raw.parquet`, `payload` je datagram, `type` je ime njegova ID-a: `motion`, `session`, `lap_data`, `event`, `participants`, `car_setups`, `car_telemetry`, `car_status`, `final_classification`, `lobby_info`, `car_damage`, `session_history`, `tyre_sets`, `motion_ex`, `time_trial`, `lap_positions` (`packet <n>` za ID koji specifikacije još ne navode); stupci `format` (2023/2024/2025), `packet_id`, `frame`, `session_uid`
- `used` je true za pakete pročitane gore (Motion, Session, Lap Data, Participants, Car Telemetry, i kodove događaja osim BUTN); ostalo - postavke automobila, stanje automobila (gorivo, ERS, spojevi i starost guma, zastavice), konačna klasifikacija, predvorje, oštećenja automobila, povijest sesije (svaki krug i svako vrijeme sektora po automobilu), setovi guma, motion ex (ovjes vlastitog automobila, brzine kotača, lokalna brzina, kutna brzina i ubrzanje), time trial, pozicije u krugu, događaji gumba BUTN - čuva se za kasniji dekoder
- `format <year>`: paket u formatu prije 2023 (drugačiji raspored zaglavlja), cjelovit; `short`: datagram kraći od 29-bajtnog zaglavlja, cjelovit

**Nije dostupno**

- gorivo, ERS, oštećenja i setovi guma drugih igrača na mreži kad je njihova "Your Telemetry" ograničena: igra za njih šalje nule
- paketi poslani dok watcher ne radi ili dok druga aplikacija drži port 20777: UDP igra ne sprema

**Veličina**: pri brzini slanja od 60 Hz svaki paket je oko 0,38 MB/s (Motion, Lap Data, Car Telemetry, Car Status i Motion Ex na 60 Hz, Session History i Tyre Sets 20/s, Car Damage 10/s, Session i Car Setups 2/s) plus oko 0,03 MB/s zaglavlja stavki: oko 1,5 GB na sat vožnje prije sažimanja, oko 0,55 GB pri zadanih 20 Hz; zstd to svede na djelić (prazna mjesta automobila i ponovljene vrijednosti dobro se stisnu; još nije izmjereno na pravoj sesiji)

## Provjereno {#verified}

testirano na paketima u formatima 2023, 2024 i 2025 izgrađenima iz EA-ove objavljene specifikacije, poslanim preko UDP-a; nije testirano na igri

## Izvor {#source}

[heat3d_watch/adapters/f1.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/f1.py)

<!-- Generated from the adapter by tools/gen_game_pages.py; change the adapter and run it again rather than editing this page. -->
