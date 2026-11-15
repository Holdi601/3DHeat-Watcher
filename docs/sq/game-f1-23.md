---
title: "EA SPORTS F1 23 (të dhëna të drejtpërdrejta)"
nav_order: 14
lang: "sq"
source: game-f1-23.md
source_hash: "d7b523188e51"
nav_exclude: true
search_exclude: true
---
# EA SPORTS F1 23 (të dhëna të drejtpërdrejta) {#ea-sports-f1-23-live-data}

Ndërsa luan EA SPORTS F1 23, watcher-i ruan të dhënat që dërgon vetë loja, që më vonë t'i shohësh në një hartë në shikuesin 3DHeat.

*Detaje teknike: adapteri `f1-23`, lloji [`telemetry`](sources-and-rules.md); ekzekutohet sa kohë `F1_23.exe` është në punë dhe kërkon të dhëna të reja çdo 0.1 s.*

## Çfarë regjistrohet {#what-is-recorded}

- pozicioni i çdo makine (XYZ botërore, m) në 10 Hz, sipas emrit të shoferit, ekipit, makina jote e shënuar (`own_car` 1, nga indeksi i makinës së lojtarit), me shpejtësi, marshin, gazin, frenin, timonin, rpm, DRS, yaw, pitch, roll (gradë) dhe forcat g
- xhirot për çdo makinë me kohën e xhiros dhe pozicionin në garë; përfundimet dhe tërheqjet
- ngjarjet e garës të lojës: fillimi dhe mbarimi i seancës, xhiroja më e shpejtë, ndëshkimet, parakalimet, përplasjet, safety car, flamuri i kuq, dritat e nisjes, flamuri me kuadrate, fituesi, flashback-et (`teleport` ku ishte makina, `spawn` ku u kthye)
- pista, lloji i seancës, xhirot dhe shoferët e çdo seance
- xhirot e tua, xhiroja më e mirë, pozicioni në garë dhe në grid, ndalesat në pit, ndëshkimet, parakalimet, përplasjet, largësia, shpejtësia maksimale
- çdo paketë që dërgon loja, e plotë, në `heat.raw.parquet` - edhe ato që nuk lexohen në rreshta

## Nga vjen {#where-it-comes-from}

Telemetri UDP 127.0.0.1:20777 (Documents\My Games\F1 23\hardwaresettings\hardware_settings_config.xml)

## Si aktivizohet {#how-to-switch-it-on}

Në lojë: Settings > Telemetry Settings > UDP Telemetry On, IP 127.0.0.1, port 20777 - ose `python -m heat3d_watch setup f1-23 --apply` (redakton hardware_settings_config.xml, me kopje rezervë së pari; loja duhet të jetë e mbyllur). Sa kohë një aplikacion tjetër mban 20777, watcher-i ia lë portën atij

Shkruaje komandën në një terminal të hapur në dosjen e watcher-it (shih [Para se të fillosh](before-you-start.md)). Nëse dështon, rreshti i fundit tregon pse; [Instalimi dhe ekzekutimi](installing-and-running.md) përmban shkaqet më të zakonshme.

`python -m heat3d_watch setup f1-23` liston skedarët që do të ndryshonte; `python -m heat3d_watch setup f1-23 --apply` i ndryshon, duke e ruajtur origjinalin si `<file>.heat3d-backup` (shih [Komandat](commands.md#setup)). Shfaq `f1-23: changed: ...` për çdo ndryshim, ose `f1-23: nothing to change` kur është tashmë i aktivizuar.

## Si funksionon {#how-it-works}

EA SPORTS F1 23, F1 24 dhe F1 25: telemetria zyrtare UDP, çdo makinë në pistë.

Lojërat e dërgojnë vetë (Settings > Telemetry Settings, ose
`Documents/My Games/<F1 xx>/hardwaresettings/hardware_settings_config.xml`,
`<udp enabled="true" ip="127.0.0.1" port="20777" sendRate="20" format="2025" ...>`).
Little-endian, të paketuara, një header 29 bajtësh në çdo paketë (i njëjtë në formatet
2023, 2024 dhe 2025):

```text
uint16 packetFormat, uint8 gameYear, gameMajorVersion, gameMinorVersion,
packetVersion, packetId, uint64 sessionUID, float sessionTime,
uint32 frameIdentifier, overallFrameIdentifier, uint8 playerCarIndex,
secondaryPlayerCarIndex
```

Çfarë lexohet, sipas id-së së paketës:

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

Çdo paketë ruhet edhe e plotë, siç erdhi, në skedarin raw anësor të seancës
(`heat.raw.parquet`, `type` emri i paketës - `motion`, `car_status` ... -
me `format`, `packet_id`, `frame` dhe `session_uid`) - ato që lexohen më sipër dhe ato që
nuk i lexon ende askush: 5 Car Setups, 7 Car Status, 8 Final Classification, 9 Lobby
Info, 10 Car Damage, 11 Session History, 12 Tyre Sets, 13 Motion Ex, 14 Time
Trial, 15 Lap Positions, çdo id e mëvonshme, dhe paketa në një format që ky nuk
e lexon. Kështu një dekodues i mëvonshëm ka nevojë vetëm për skedarin anësor.

Pozicioni i çdo makine është në paketën Motion - edhe online, ku vetë loja
e jep (vetëm të dhënat e karburantit, ERS, dëmtimeve dhe gomave mbahen të fshehura
për lojtarët që e kanë "Your Telemetry" të kufizuar). Çdo makinë regjistrohet
në rreth 10 Hz nën emrin e pjesëmarrësit ("car N" derisa të vijnë emrat), ekipi
me emër, dhe makina e vetë lojtarit shënohet `own`.

Burimet: "F1 25 UDP Specification" e EA (forums.ea.com, qendra e informacionit të lojërave F1),
specifikimet e F1 23 dhe F1 24; të njëjtat tabela të pasqyruara te
MacManley/f1-25-udp (MIT). Paketat në teste ndërtohen nga këto struktura.

I njëjti modul shërben edhe: [EA SPORTS F1 24 (të dhëna të drejtpërdrejta)](game-f1-24.md), [EA SPORTS F1 25 (të dhëna të drejtpërdrejta)](game-f1-25.md).

## Pozicionet dhe boshtet {#positions-and-axes}

| | |
|---|---|
| Pozicionet regjistrohen | po |
| Boshti lart | `y` |
| Njësitë | metra |
| Pasqyruar për shikuesin | asnjë |
| Shkalla e njësisë (`scale`: shikuesi i shumëzon pozicionet me të) | 1 |

Këto shkojnë në `meta.json` të çdo seance (`axes`) dhe, kur seanca ka pozicione, në fundin e `heat.parquet`, që shikuesi 3DHeat t'i rrotullojë dhe shkallëzojë rreshtat vetë - shih [Të dhënat](the-data.md).

## Lojë me shumë lojtarë {#multiplayer}

- Shënuar si luajtur online (`multiplayer`): **po**. `games --markdown` e shfaq këtë si "allowed (reads only what the game publishes)".
- Lloji `telemetry`: lexon vetëm çfarë jep loja ose platforma (një port UDP ose memorie e përbashkët që e boton loja), ndaj regjistron edhe në lojë online edhe offline; flamuri vendos vetëm nëse mund të lexohet ndonjëherë memoria.
- Memoria: **kurrë** nuk lexohet nga ky adapter. Vetëm adapterat `memory` lexojnë memorie, dhe kurrë për një lojë të shënuar si e luajtur online - shih [Burimet dhe rregullat](sources-and-rules.md).

## Statistikat e regjistruara {#statistics-recorded}

Çelësat e statistikave që kodi i këtij adapteri i vendos me emër (`stats` e çdo seance në `meta.json` dhe tabela `stats` e `watcher.sqlite`):

`best_lap`, `collisions`, `distance_km`, `fastest_laps`, `finishes`, `flashbacks`, `grid_position`, `laps`, `overtaken`, `overtakes`, `penalties`, `penalty_seconds`, `pit_stops`, `race_position`, `sessions`, `top_speed_kmh`, `wins`

Një çelës në kllapa gjarpëruese plotësohet gjatë ekzekutimit (`score.{team}` është një çelës për çdo ekip). Çelësat që kodi i merr nga një tabelë fushash të lojës ose nga emrat e statistikave të vetë lojës nuk janë në këtë listë; "Çfarë regjistrohet" më sipër i emërton.

## Plotësia {#completeness}

Watcher-i ndjek [rregullin e konvertuesve](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md) të 3DHeat: çfarë mban burimi lexohet ose ruhet, nuk hidhet kurrë. Përveç rreshtave, çdo paketë, faqe, rresht ose përgjigje që merr adapteri ruhet e plotë në `heat.raw.parquet` të seancës (kolonat `time`, `ms`, `type`, `used`, `payload`, `text`, pastaj çdo fushë e mbajtur me emër; `used` shënon çfarë u bë edhe rresht), dhe `selfCheck.completeness` i `meta.json` numëron çdo `type` - `lost` është 0.

**Lexohet**

- 0 Motion: pozicioni dhe shpejtësia botërore e çdo makine, dhe tani edhe yaw, pitch, roll (gradë, nga radianët e specifikimit) dhe forca g anësore, gjatësore dhe vertikale, në rreshtat e pozicionit të çdo makine
- 1 Session: pista, lloji i seancës, xhirot gjithsej, gjatësia e pistës, online ose jo (`sessions` në meta.json)
- 2 Lap Data: koha e xhiros së fundit, numri i xhiros, pozicioni në garë dhe në grid, ndalesat në pit, ndëshkimet, statusi i rezultatit (xhirot, përfundimet, tërheqjet, statistikat)
- 3 Event: çdo kod përveç BUTN si rresht më vete, me detajet e tij
- 4 Participants: emrat e shoferëve, ekipet, numri i makinave aktive (`player` dhe `team` të rreshtave, `drivers` në meta.json)
- 6 Car Telemetry: shpejtësia, marshi, gazi, frena, dhe tani edhe timoni (-1..1), rpm dhe DRS, në rreshtat e pozicionit të çdo makine
- kontrolluar me specifikimet UDP të publikuara nga EA për formatet 2023, 2024 dhe 2025 (madhësitë e paketave të verifikuara në teste); ende jo me lojën

**Ruhet i papërpunuar**

- çdo paketë e plotë në `heat.raw.parquet`, `payload` datagrami, `type` emri i id-së së saj: `motion`, `session`, `lap_data`, `event`, `participants`, `car_setups`, `car_telemetry`, `car_status`, `final_classification`, `lobby_info`, `car_damage`, `session_history`, `tyre_sets`, `motion_ex`, `time_trial`, `lap_positions` (`packet <n>` për një id që specifikimet nuk e listojnë ende); kolonat `format` (2023/2024/2025), `packet_id`, `frame`, `session_uid`
- `used` është e vërtetë për paketat e lexuara më sipër (Motion, Session, Lap Data, Participants, Car Telemetry, dhe kodet Event përveç BUTN); pjesa tjetër - car setups, car status (karburanti, ERS, përbërja dhe mosha e gomave, flamujt), final classification, lobby, car damage, session history (çdo kohë xhiroje dhe sektori për makinë), tyre sets, motion ex (pezullimi i makinës tënde, shpejtësitë e rrotave, shpejtësia lokale, shpejtësia këndore dhe përshpejtimi), time trial, lap positions, ngjarjet e butonave BUTN - ruhen për një dekodues të mëvonshëm
- `format <year>`: një paketë në një format para 2023 (strukturë tjetër e header-it), e plotë; `short`: një datagram më i shkurtër se header-i 29 bajtësh, i plotë

**Nuk disponohet**

- karburanti, ERS, dëmtimet dhe gomat e lojtarëve të tjerë online kur "Your Telemetry" e tyre është e kufizuar: loja dërgon zero për ta
- paketat e dërguara kur watcher-i nuk është në punë, ose kur një aplikacion tjetër mban portën 20777: UDP nuk ruhet nga loja

**Madhësia**: me shpejtësi dërgimi 60 Hz çdo paketë është rreth 0.38 MB/s (Motion, Lap Data, Car Telemetry, Car Status dhe Motion Ex në 60 Hz, Session History dhe Tyre Sets në 20/s, Car Damage në 10/s, Session dhe Car Setups në 2/s) plus rreth 0.03 MB/s header-a elementësh: rreth 1.5 GB në orë vozitjeje para kompresimit, rreth 0.55 GB në 20 Hz parazgjedhje; zstd e sjell në një pjesë të vogël të kësaj (vendet bosh të makinave dhe vlerat e përsëritura ngjeshen mirë; ende i pamatur në një seancë të vërtetë)

## Verifikuar {#verified}

provuar me paketa në formatet 2023, 2024 dhe 2025 të ndërtuara nga specifikimi i publikuar i EA, të dërguara përmes UDP; i paprovuar me lojën

## Burimi {#source}

[heat3d_watch/adapters/f1.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/f1.py)

<!-- Gjeneruar nga adapteri me tools/gen_game_pages.py; ndrysho adapterin dhe ekzekuto përsëri, mos e redakto këtë faqe. -->
