---
title: "EA SPORTS F1 23 (данни на живо)"
nav_order: 14
lang: "bg"
source: game-f1-23.md
source_hash: "d7b523188e51"
nav_exclude: true
search_exclude: true
---
# EA SPORTS F1 23 (данни на живо) {#ea-sports-f1-23-live-data}

Докато играете EA SPORTS F1 23, watcher-ът записва данните, които самата игра изпраща навън, за да можете по-късно да ги разгледате на карта в 3DHeat визуализатора.

*Технически подробности: адаптер `f1-23`, вид [`telemetry`](sources-and-rules.md); работи, докато `F1_23.exe` е стартиран, и търси нови данни на всеки 0.1 s.*

## Какво се записва {#what-is-recorded}

- позицията на всяка кола (световни XYZ, m) на 10 Hz, по име на пилота, отбор, собствената кола отбелязана (`own_car` 1, от индекса на колата на играча), със скорост, предавка, газ, спирачка, завиване, оборотите, DRS, yaw, pitch, roll (градуси) и g-сили
- обиколки на всяка кола с времето на обиколката и позицията в състезанието; финиши и отпадания
- събитията на състезанието от играта: начало и край на сесията, най-бърза обиколка, наказания, изпреварвания, сблъсъци, safety car, червен флаг, стартови светлини, финалното знаме, победител, flashback-и (`teleport` там, където е била колата, `spawn` там, където се е върнала)
- трасе, вид на сесията, обиколки и пилоти на всяка сесия
- собствените обиколки, най-добрата обиколка, позиция в състезанието и на старта, пит спирания, наказания, изпреварвания, сблъсъци, разстояние, максимална скорост
- всеки пакет, който играта изпраща, цял, в `heat.raw.parquet` - включително тези, които не се прочитат в редове

## Откъде идва {#where-it-comes-from}

UDP телеметрия 127.0.0.1:20777 (Documents\My Games\F1 23\hardwaresettings\hardware_settings_config.xml)

## Как се включва {#how-to-switch-it-on}

В играта: Settings > Telemetry Settings > UDP Telemetry On, IP 127.0.0.1, порт 20777 - или `python -m heat3d_watch setup f1-23 --apply` (редактира hardware_settings_config.xml, предварително се прави резервно копие; играта трябва да е затворена). Докато друго приложение държи 20777, watcher-ът оставя порта на него

Напишете командата в терминал, отворен в папката на watcher-а (вижте [Преди да започнете](before-you-start.md)). Ако се провали, последният ред казва защо; [Инсталиране и стартиране](installing-and-running.md) описва честите причини.

`python -m heat3d_watch setup f1-23` показва кои файлове би променил; `python -m heat3d_watch setup f1-23 --apply` ги променя и запазва оригинала като `<file>.heat3d-backup` (вижте [Команди](commands.md#setup)). Печата `f1-23: changed: ...` за всяка промяна или `f1-23: nothing to change`, когато вече е включено.

## Как работи {#how-it-works}

EA SPORTS F1 23, F1 24 и F1 25: официалната UDP телеметрия, всяка кола на трасето.

Игрите я изпращат сами (Settings > Telemetry Settings, или
`Documents/My Games/<F1 xx>/hardwaresettings/hardware_settings_config.xml`,
`<udp enabled="true" ip="127.0.0.1" port="20777" sendRate="20" format="2025" ...>`).
Little-endian, опаковано (packed), с 29-байтов заглавен блок във всеки пакет (същият във
формати 2023, 2024 и 2025):

```text
uint16 packetFormat, uint8 gameYear, gameMajorVersion, gameMinorVersion,
packetVersion, packetId, uint64 sessionUID, float sessionTime,
uint32 frameIdentifier, overallFrameIdentifier, uint8 playerCarIndex,
secondaryPlayerCarIndex
```

Какво се чете, по идентификатор на пакета:

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

Всеки пакет се пази и цял, както е дошъл, в суровия страничен файл на сесията
(`heat.raw.parquet`, `type` е името на пакета - `motion`, `car_status` ... -
с `format`, `packet_id`, `frame` и `session_uid`) - и тези, които са прочетени горе, и тези,
които още никой не чете: 5 Car Setups, 7 Car Status, 8 Final Classification, 9 Lobby
Info, 10 Car Damage, 11 Session History, 12 Tyre Sets, 13 Motion Ex, 14 Time
Trial, 15 Lap Positions, всеки по-късен идентификатор и пакети във формат, който
watcher-ът не чете. Затова по-късен декодер се нуждае само от страничния файл.

Позицията на всяка кола е в Motion пакета - и онлайн, където играта сама я предава
(само горивото, ERS, повредите и данните за гумите се пазят за играчи с ограничена
"Your Telemetry"). Всяка кола се записва на около 10 Hz под името си от участника ("car N",
докато имената пристигнат), отборът по име, а собствената кола на играча - маркирана `own`.

Източници: "F1 25 UDP Specification" на EA (forums.ea.com, F1 games info hub),
спецификациите на F1 23 и F1 24; същите таблици, огледално копирани в
MacManley/f1-25-udp (MIT). Пакетите в тестовете са изградени по тези оформления.

Същият модул обслужва и: [EA SPORTS F1 24 (данни на живо)](game-f1-24.md), [EA SPORTS F1 25 (данни на живо)](game-f1-25.md).

## Позиции и оси {#positions-and-axes}

| | |
|---|---|
| Записани позиции | да |
| Вертикална ос | `y` |
| Единици | метри |
| Огледално за визуализатора | няма |
| Мащаб на единицата (`scale`: визуализаторът умножава позициите по него) | 1 |

Те отиват в `meta.json` (`axes`) на всяка сесия и, когато сесията има позиции, в долния колонтитул на `heat.parquet`, така че 3DHeat визуализаторът сам завърта и мащабира редовете - вижте [Данните](the-data.md).

## Мултиплейър {#multiplayer}

- Маркиран като игран онлайн (`multiplayer`): **да**. `games --markdown` показва това като "разрешено (чете само това, което играта публикува)".
- Вид `telemetry`: чете само това, което играта или платформата предава (UDP порт или споделена памет, които играта публикува), затова записва и в онлайн игра, както и офлайн; флагът решава само дали паметта може изобщо да се чете.
- Памет: **никога** не се чете от този адаптер. Само адаптерите от вид `memory` четат памет, и никога за игра, маркирана като играна онлайн - вижте [Източници и правила](sources-and-rules.md).

## Записана статистика {#statistics-recorded}

Ключове на статистиката, които кодът на този адаптер задава по име (`stats` на всяка сесия в `meta.json` и таблицата `stats` в `watcher.sqlite`):

`best_lap`, `collisions`, `distance_km`, `fastest_laps`, `finishes`, `flashbacks`, `grid_position`, `laps`, `overtaken`, `overtakes`, `penalties`, `penalty_seconds`, `pit_stops`, `race_position`, `sessions`, `top_speed_kmh`, `wins`

Ключ във фигурни скоби се допълва по време на работа (`score.{team}` е по един ключ за всеки отбор). Ключовете, които кодът взема от таблица с полетата на играта или от собствените имена на статистики на играта, не са в този списък; "Какво се записва" по-горе ги изброява.

## Пълнота {#completeness}

Watcher-ът следва [правилото за конвертори](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md) на 3DHeat: това, което източникът съдържа, се чете или се пази, никога не се изхвърля. Освен редовете, всеки пакет, страница, ред или отговор, който адаптерът получава, се пази цял в `heat.raw.parquet` на сесията (колони `time`, `ms`, `type`, `used`, `payload`, `text` и всяко поле, запазено по име; `used` отбелязва какво е станало и ред), а `selfCheck.completeness` в `meta.json` брои всеки `type` - `lost` е 0.

**Прочетено**

- 0 Motion: световната позиция и скорост на всяка кола, а сега и yaw, pitch, roll (градуси, от радианите в спецификацията) и страничната, надлъжната и вертикалната g-сила, във всеки ред с позиция на колата
- 1 Session: трасе, вид на сесията, общ брой обиколки, дължина на трасето, онлайн или не (`sessions` в meta.json)
- 2 Lap Data: времето на последната обиколка, номер на обиколката, позиция в състезанието и на старта, пит спирания, наказания, статус на резултата (обиколки, финиши, отпадания, статистика)
- 3 Event: всеки код, освен BUTN, като собствен ред, с подробностите си
- 4 Participants: имена на пилотите, отбори, брой активни коли (`player` и `team` на редовете, `drivers` в meta.json)
- 6 Car Telemetry: скорост, предавка, газ, спирачка, а сега и завиване (-1..1), оборотите и DRS, във всеки ред с позиция на колата
- проверено по публикуваните от EA UDP спецификации за форматите 2023, 2024 и 2025 (размерите на пакетите са потвърдени в тестовете); още не е проверено с играта

**Пазено цяло**

- всеки пакет цял в `heat.raw.parquet`, `payload` е датаграмата, `type` е името на идентификатора му: `motion`, `session`, `lap_data`, `event`, `participants`, `car_setups`, `car_telemetry`, `car_status`, `final_classification`, `lobby_info`, `car_damage`, `session_history`, `tyre_sets`, `motion_ex`, `time_trial`, `lap_positions` (`packet <n>` за идентификатор, който спецификациите още не изброяват); колоните `format` (2023/2024/2025), `packet_id`, `frame`, `session_uid`
- `used` е вярно за пакетите, прочетени горе (Motion, Session, Lap Data, Participants, Car Telemetry и кодовете на Event, различни от BUTN); останалите - настройки на колите, състояние на колите (гориво, ERS, вид и възраст на гумата, флагове), крайната класация, лобито, повредите на колите, историята на сесията (всяко време на обиколка и сектор за всяка кола), наборите гуми, motion ex (окачването на собствената кола, скоростите на колелата, локалната скорост, ъгловата скорост и ускорението), time trial, позициите по обиколки, събитията BUTN - се пазят за по-късен декодер
- `format <year>`: пакет във формат преди 2023 (друго оформление на заглавието), цял; `short`: датаграма по-къса от 29-байтовото заглавие, цяла

**Не е налично**

- горивото, ERS, повредите и наборите гуми на други играчи онлайн, когато "Your Telemetry" е ограничен: играта изпраща нули за тях
- пакети, изпратени, докато watcher-ът не работи, или докато друго приложение държи порт 20777: UDP не се пази от играта

**Размер**: при скорост на изпращане 60 Hz всеки пакет е около 0.38 MB/s (Motion, Lap Data, Car Telemetry, Car Status и Motion Ex на 60 Hz, Session History и Tyre Sets по 20/s, Car Damage по 10/s, Session и Car Setups по 2/s) плюс около 0.03 MB/s заглавия на записите: около 1.5 GB на час шофиране преди компресия, около 0.55 GB при стандартните 20 Hz; zstd го свежда до малка част от това (празните слотове за коли и повтарящите се стойности се свиват добре; още не е измерено на истинска сесия)

## Проверено {#verified}

проверено на пакети във формати 2023, 2024 и 2025, изградени по публикуваната от EA спецификация и изпратени по UDP; непроверено с играта

## Източник {#source}

[heat3d_watch/adapters/f1.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/f1.py)

<!-- Generated from the adapter by tools/gen_game_pages.py; change the adapter and run it again rather than editing this page. -->
