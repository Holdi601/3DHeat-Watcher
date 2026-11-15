---
title: "EA SPORTS F1 25 (податоци во живо)"
nav_order: 16
lang: "mk"
source: game-f1-25.md
source_hash: "7476dbb3b308"
nav_exclude: true
search_exclude: true
---
# EA SPORTS F1 25 (податоци во живо) {#ea-sports-f1-25-live-data}

Додека играте EA SPORTS F1 25, watcher-от ги зачувува податоците што самата игра ги испраќа, за подоцна да можете да ги погледнете на мапа во прегледувачот 3DHeat.

*Технички детали: адаптер `f1-25`, вид [`telemetry`](sources-and-rules.md); работи додека работи `F1_25.exe` и бара нови податоци на секои 0,1 s.*

## Што се снима {#what-is-recorded}

- позицијата на секој болид (светски XYZ, m) на 10 Hz, по име на возач, тим, со означен сопствен болид (`own_car` 1, од индексот на болидот на играчот), со брзина, степен на пренос, гас, сопирачка, воланот, вртежи (rpm), DRS, yaw, pitch, roll (степени) и g-сили
- кругови по болид со времето на кругот и позицијата во трката; завршувања и повлекувања
- настаните на трката од играта: почеток и крај на сесија, најбрз круг, казни, престигнувања, судири, безбедносен автомобил, црвено знаме, стартни светла, карирано знаме, победник, flashback-ови (`teleport` каде бил болидот, `spawn` каде се вратил)
- патека, тип на сесија, кругови и возачи на секоја сесија
- сопствени кругови, најдобар круг, позиција во трката и на стартната решетка, пит-стопови, казни, престигнувања, судири, растојание, највисока брзина
- секој пакет што го праќа играта, целосен, во `heat.raw.parquet` - и оние што не се читаат во редови

## Од каде доаѓа {#where-it-comes-from}

UDP-телеметрија 127.0.0.1:20777 (Documents\My Games\F1 25\hardwaresettings\hardware_settings_config.xml)

## Како да се вклучи {#how-to-switch-it-on}

Во играта: Settings > Telemetry Settings > UDP Telemetry On, IP 127.0.0.1, port 20777 - или `python -m heat3d_watch setup f1-25 --apply` (ја уредува hardware_settings_config.xml, прво прави резерва; играта мора да биде затворена). Додека друга апликација ја држи портата 20777, watcher-от ѝ ја препушта портата

Напишете ја командата во терминал отворен во папката на watcher-от (видете [Пред да започнете](before-you-start.md)). Ако не успее, последната линија кажува зошто; [Инсталирање и пуштање](installing-and-running.md) ги опфаќа вообичаените причини.

`python -m heat3d_watch setup f1-25` ги наведува датотеките што би ги променила; `python -m heat3d_watch setup f1-25 --apply` ги менува, чувајќи го оригиналот како `<file>.heat3d-backup` (видете [Команди](commands.md#setup)). Печати `f1-25: changed: ...` за секоја промена, или `f1-25: nothing to change` кога веќе е вклучено.

## Како работи {#how-it-works}

EA SPORTS F1 23, F1 24 и F1 25: официјалната UDP-телеметрија, секој болид на патеката.

Игрите ја праќаат самите (Settings > Telemetry Settings, или
`Documents/My Games/<F1 xx>/hardwaresettings/hardware_settings_config.xml`,
`<udp enabled="true" ip="127.0.0.1" port="20777" sendRate="20" format="2025" ...>`).
Little-endian, збиено (packed), заглавие од 29 бајти на секој пакет (исто во форматите
2023, 2024 и 2025):

```text
uint16 packetFormat, uint8 gameYear, gameMajorVersion, gameMinorVersion,
packetVersion, packetId, uint64 sessionUID, float sessionTime,
uint32 frameIdentifier, overallFrameIdentifier, uint8 playerCarIndex,
secondaryPlayerCarIndex
```

Што се чита, по id на пакетот:

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

Секој пакет се чува и целосен, како што дошол, во суровата придружна датотека на сесијата
(`heat.raw.parquet`, `type` името на пакетот - `motion`, `car_status` ... -
со `format`, `packet_id`, `frame` и `session_uid`) - оние прочитани погоре и оние што
сè уште никој не ги чита: 5 Car Setups, 7 Car Status, 8 Final Classification, 9 Lobby
Info, 10 Car Damage, 11 Session History, 12 Tyre Sets, 13 Motion Ex, 14 Time
Trial, 15 Lap Positions, секој подоцнежен id, и пакети во формат што ова не
го чита. Така подоцнежен декодер му треба само придружната датотека.

Позицијата на секој болид е во пакетот Motion - и онлајн, каде што играта
сама ја дава (само податоците за гориво, ERS, оштетување и сетови гуми се задржуваат
за играчи чија „Your Telemetry“ е ограничена). Секој болид се снима на
околу 10 Hz под името на учесникот („car N“ додека не стигнат имињата), тимот
по име, а сопствениот болид на играчот означен како `own`.

Извори: „F1 25 UDP Specification“ на EA (forums.ea.com, F1 games info hub),
спецификациите за F1 23 и F1 24; истите табели огледани во
MacManley/f1-25-udp (MIT). Пакетите во тестовите се градат од овие распореди.

Истиот модул служи и за: [EA SPORTS F1 23 (податоци во живо)](game-f1-23.md), [EA SPORTS F1 24 (податоци во живо)](game-f1-24.md).

## Позиции и оски {#positions-and-axes}

| | |
|---|---|
| Снимени позиции | да |
| Горна оска | `y` |
| Единици | метри |
| Огледално за прегледувачот | нема |
| Скала на единици (`scale`: прегледувачот ги множи позициите со неа) | 1 |

Овие одат во `meta.json` на секоја сесија (`axes`) и, кога сесијата има позиции, во подножјето на `heat.parquet`, па прегледувачот 3DHeat сам ги врти и скалира редовите - видете [Податоците](the-data.md).

## Мултиплеер {#multiplayer}

- Означено како играно онлајн (`multiplayer`): **да**. `games --markdown` го прикажува ова како „allowed (reads only what the game publishes)“.
- Вид `telemetry`: чита само она што играта или платформата го дава (UDP-порта или споделена меморија што ја објавува играта), па снима и во онлајн игра и офлајн; знамето одлучува само дали меморијата смее некогаш да се чита.
- Меморија: овој адаптер **никогаш** не ја чита. Само `memory` адаптерите читаат меморија, и никогаш за игра означена како играна онлајн - видете [Извори и правила](sources-and-rules.md).

## Снимена статистика {#statistics-recorded}

Клучеви на статистика што кодот на овој адаптер ги поставува по име (`stats` на секоја сесија во `meta.json` и табелата `stats` во `watcher.sqlite`):

`best_lap`, `collisions`, `distance_km`, `fastest_laps`, `finishes`, `flashbacks`, `grid_position`, `laps`, `overtaken`, `overtakes`, `penalties`, `penalty_seconds`, `pit_stops`, `race_position`, `sessions`, `top_speed_kmh`, `wins`

Клуч во загради { } се дополнува при извршување (`score.{team}` е еден клуч по тим). Клучевите што кодот ги зема од табела со полињата на играта или од сопствените имиња на статистика на играта не се во овој список; „Што се снима“ погоре ги именува.

## Комплетност {#completeness}

Watcher-от го следи [правилото за конвертори](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md) на 3DHeat: она што го содржи изворот се чита или се чува, никогаш не се отфрла. Покрај редовите, секој пакет, страница, линија или одговор што адаптерот ќе го добие се чува целосен во `heat.raw.parquet` на сесијата (колони `time`, `ms`, `type`, `used`, `payload`, `text`, потоа секое поле зачувано по име; `used` означува што станало и ред), а `selfCheck.completeness` во `meta.json` го брои секој `type` - `lost` е 0.

**Прочитано**

- 0 Motion: светската позиција и брзина на секој болид, а сега и yaw, pitch, roll (степени, од радијаните во спецификацијата) и странична, подолжна и вертикална g-сила, на редовите со позиција на секој болид
- 1 Session: патека, тип на сесија, вкупно кругови, должина на патеката, онлајн или не (`sessions` во meta.json)
- 2 Lap Data: последно време на круг, број на круг, позиција во трката и на стартната решетка, пит-стопови, казни, статус на резултат (кругови, завршувања, повлекувања, статистика)
- 3 Event: секој код освен BUTN како свој ред, со своите детали
- 4 Participants: имиња на возачи, тимови, број на активни болиди (`player` и `team` на редовите, `drivers` во meta.json)
- 6 Car Telemetry: брзина, степен на пренос, гас, сопирачка, а сега и воланот (-1..1), rpm и DRS, на редовите со позиција на секој болид
- проверено наспроти објавените UDP-спецификации на EA за форматите 2023, 2024 и 2025 (големините на пакетите се потврдуваат во тестовите); сè уште не наспроти играта

**Чувано сурово**

- секој пакет целосен во `heat.raw.parquet`, `payload` датаграмот, `type` името на неговиот id: `motion`, `session`, `lap_data`, `event`, `participants`, `car_setups`, `car_telemetry`, `car_status`, `final_classification`, `lobby_info`, `car_damage`, `session_history`, `tyre_sets`, `motion_ex`, `time_trial`, `lap_positions` (`packet <n>` за id што спецификациите сè уште не го наведуваат); колони `format` (2023/2024/2025), `packet_id`, `frame`, `session_uid`
- `used` е точно за пакетите прочитани погоре (Motion, Session, Lap Data, Participants, Car Telemetry, и кодовите на Event освен BUTN); остатокот - car setups, car status (гориво, ERS, мешавина и старост на гумите, знамиња), final classification, lobby, car damage, session history (секое време на круг и сектор по болид), tyre sets, motion ex (суспензијата на сопствениот болид, брзините на тркалата, локалната брзина, аголната брзина и забрзувањето), time trial, lap positions, BUTN настани со копчиња - се чуваат за подоцнежен декодер
- `format <year>`: пакет во формат пред 2023 (друг распоред на заглавието), целосен; `short`: датаграм пократок од заглавието од 29 бајти, целосен

**Недостапно**

- горивото, ERS, оштетувањето и сетовите гуми на другите играчи онлајн кога нивната „Your Telemetry“ е ограничена: играта за нив праќа нули
- пакети испратени додека watcher-от не работи, или додека друга апликација ја држи портата 20777: играта не ги складира UDP-пакетите

**Големина**: при брзина на праќање од 60 Hz сите пакети се околу 0,38 MB/s (Motion, Lap Data, Car Telemetry, Car Status и Motion Ex на 60 Hz, Session History и Tyre Sets на 20/s, Car Damage на 10/s, Session и Car Setups на 2/s) плус околу 0,03 MB/s заглавија на ставки: околу 1,5 GB на час возење пред компресија, околу 0,55 GB при стандардните 20 Hz; zstd го сведува на дел од тоа (празните места за болиди и повторените вредности се компресираат добро; сè уште не е измерено на вистинска сесија)

## Проверено {#verified}

тестирано на пакети во форматите 2023, 2024 и 2025 изградени од објавената спецификација на EA, испратени преку UDP; не е тестирано со играта

## Извор {#source}

[heat3d_watch/adapters/f1.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/f1.py)

<!-- Generated from the adapter by tools/gen_game_pages.py; change the adapter and run it again rather than editing this page. -->
