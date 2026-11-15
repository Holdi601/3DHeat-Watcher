---
title: "IL-2 Sturmovik: Great Battles (записи)"
nav_order: 27
lang: "bg"
source: game-il2-tacview.md
source_hash: "0bb23bddee03"
nav_exclude: true
search_exclude: true
---
# IL-2 Sturmovik: Great Battles (записи) {#il-2-sturmovik-great-battles-replays}

След мач в IL-2 Sturmovik: Great Battles watcher-ът превръща записа, който играта е запазила, във файлове, които можете да разгледате на карта във визуализатора 3DHeat.

*Технически подробности: адаптер `il2-tacview`, вид [`replay`](sources-and-rules.md); работи през цялото време (не чака играта да стартира) и търси нови данни на всеки 5 s.*

## Какво се записва {#what-is-recorded}

- всеки самолет, превозно средство и кораб от записа: позиции веднъж в секунда (метри на изток/нагоре/на север от референтната точка на записа; географска ширина, дължина и височина като колони)
- появявания, унищожения (смърт) и напускания (left), излитания и кацания, когато са записани
- обекти, унищожени, излитания, кацания и дължина на всеки запис
- всеки ред от записа цял в heat.raw.parquet, по часовника на редовете

## Откъде идва {#where-it-comes-from}

собствените записи на играта в Tacview &lt;game>\data\Tracks\\\*.acmi (текст ACMI 2.x, обикновен или zip-нат)

## Как се включва {#how-to-switch-it-on}

python -m heat3d_watch setup il2-tacview --apply (tacviewrecord = 1 в [KEY = track_record])

Въведете командата в терминал, отворен в папката на watcher-а (вижте [Преди да започнете](before-you-start.md)). Ако се провали, последният ред казва защо; [Инсталиране и стартиране](installing-and-running.md) описва честите причини.

`python -m heat3d_watch setup il2-tacview` показва кои файлове би променил; `python -m heat3d_watch setup il2-tacview --apply` ги променя, като запазва оригинала като `<file>.heat3d-backup` (вижте [Командите](commands.md#setup)). За всяка промяна печата `il2-tacview: changed: ...`, или `il2-tacview: nothing to change`, когато вече е включено.

## Как работи {#how-it-works}

IL-2 Sturmovik: Great Battles - телеметричният UDP изход на играта и собствените ѝ записи в Tacview.

1. Телеметрия ("Telemetry output of IL2 v4.003", ревизия 1.2, доставяна като `<game>\Doc\UDP_Output\Il2_TeleOutput.pdf`). Включва се в `<game>\data\startup.cfg`, секция `[KEY = telemetrydevice]`: `addr`, `addr1`, ... = "IP[:port]" (няколко цели едновременно), `decimation` (50 Hz / n), `enable`, `port`. `setup` добавя една цел, 127.0.0.1:41995 (JoyPro ползва 41994, по подразбиране играта ползва 4322), и включва изхода. Пакетите, little-endian:

   ```text
   DWORD  Packet_ID 0x54000101
   WORD   Size
   DWORD  Tick (1/50 s)
   BYTE   Indicators_Count, then SIndicator {WORD id, BYTE n, n x 32-bit float}
   BYTE   Events_Count,     then SEvent     {WORD id, BYTE size, size bytes}
   ```

   Индикатори: 0 ENG_RPM, 1 ENG_MP, 2/3 вибрация на двигателя, 4 LGEARS_STATE, 5 LGEARS_PRESS, 6 EAS (m/s), 7 AOA (rad), 8 ACCELERATION (xyz, включително гравитацията), 9 COCKPIT_SHAKE, 10 AGL (m), 11 FLAPS, 12 AIR_BRAKES, 13 AOS (rad), 14 VERTICAL_SPEED (m/s). Събития (2-байтово пакетиране): 0 SET_FOCUS (STRING: байт за дължина и ASCII), 1 SETUP_ENG {short index, short id, float pos[3], float max_rpm}, 2 SETUP_GUN {short index, float pos[3], float projectile mass, float muzzle velocity}, 3 SETUP_LGEAR {short index, short id, float pos[3]}, 4 DROP_BOMB и 5 ROCKET_LAUNCH {float pos[3], float mass, WORD flags}, 6 HIT и 7 DAMAGE {float pos[3], float force[3]}, 8 EXPLOSION {float pos[3], float radius}, 9 GUN_FIRE {BYTE gun}, 10 SRV_ADDR, 11 SRV_TITLE, 12 SRS_ADDR (STRING), 13 CLIENT_DAT {long client, long server client, char name[32]}, 14 CTRL_DAT {long parent, short coalition}. Позициите на събитията са локални за самолета на играча; потокът изобщо няма световна позиция - затова това са събития и числа, а не траектория.

2. Запис в Tacview: `tacviewrecord = 1` в `[KEY = track_record]` кара играта да пише `<game>\data\Tracks\*.acmi` (в мултиплейър решава сървърът). Завършен файл се преобразува: всеки самолет, превозно средство и кораб с позициите си, появяване и премахване (унищожен или изчезнал), излитания и кацания, когато записът ги има. Текстов формат ACMI 2.x, обикновен или zip-нат, според <https://www.tacview.net/documentation/acmi/en/> - редовете "#t" движат часовника, редовете "id,Key=Value,..." задават свойства (шестнайсетични идентификатори, запетаите се екранират "\\,", крайното "\\" продължава реда), "-id" премахва обект, обект 0 носи глобалните данни (ReferenceLongitude/Latitude, RecordingTime ...) и събитията ("Event=Destroyed\|id\|text"). T = Lon\|Lat\|Alt[\|U\|V] или Lon\|Lat\|Alt\|Roll\|Pitch\|Yaw[\|U\|V\|Heading], дължината и ширината са спрямо референтната точка, празните полета не се променят. Позициите отиват в плоска карта около референтната точка: x на изток, y височина, z на север, метри. Референтната точка е `geo` на сесията, пази се в meta.json и във долния колонтитул на таблицата, така че визуализаторът може да сложи истинския свят под траекториите.

Същият модул обслужва и: [IL-2 Sturmovik: Great Battles (живи данни)](game-il2.md).

## Позиции и оси {#positions-and-axes}

| | |
|---|---|
| Записват се позиции | да |
| Ос нагоре | `y` |
| Мерни единици | метри (изток, височина, север от първата точка) |
| Огледален за визуализатора | `z` |
| Мащаб на единицата (`scale`: визуализаторът умножава позициите по него) | 1 |

Те отиват в `meta.json` на всяка сесия (`axes`) и, когато сесията има позиции, в долния колонтитул на `heat.parquet`, така че визуализаторът 3DHeat сам завърта и мащабира редовете - вижте [Данните](the-data.md).

## Мултиплейър {#multiplayer}

- Отбелязана като игра, играна онлайн (`multiplayer`): **да**. `games --markdown` показва това като "разрешено (чете само това, което играта публикува)".
- Вид `replay`: чете само това, което играта или платформата предоставя (реплеи и демота, които играта запазва), затова записва и в онлайн игра, както и в офлайн; флагът решава само дали паметта изобщо може да се чете.
- Памет: адаптерът **никога** не чете паметта. Само адаптерите от вид `memory` четат памет, и никога за игра, отбелязана като играна онлайн - вижте [Източници и правила](sources-and-rules.md).

## Записани статистики {#statistics-recorded}

Ключовете на статистиките, които кодът на адаптера задава по име (`stats` на всяка сесия в `meta.json` и таблицата `stats` в `watcher.sqlite`):

`destroyed`, `duration_s`, `objects`, `{r.event}s`

Ключ в фигурни скоби се допълва по време на работа (`score.{team}` е по един ключ за всеки отбор). Ключовете, които кодът взема от таблица с полетата на играта или от собствените имена на статистиките ѝ, не са в този списък; "Какво се записва" по-горе ги посочва.

## Пълнота {#completeness}

watcher-ът следва [правилото за конвертори](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md) на 3DHeat: това, което източникът съдържа, се чете или се пази, никога не се изхвърля. Освен редовете, всеки пакет, страница, ред или отговор, който адаптерът получава, се пази цял в `heat.raw.parquet` на сесията (колони `time`, `ms`, `type`, `used`, `payload`, `text`, а след тях всяко поле, запазено по име; `used` отбелязва какво е станало и ред), а `selfCheck.completeness` в `meta.json` брои всеки `type` - `lost` е 0.

**Прочетено**

- T на всеки обект (географска дължина, ширина, височина, roll, pitch, yaw, U, V, посока) като позиции веднъж в секунда за всеки обект, с Name, Type, Pilot, Coalition/Color, Country, Group и Parent
- появявания, премахвания (смърт, когато е дошло събитие Destroyed преди това, иначе напускане), събитията TakenOff и Landed, събитията Message и Bookmark като редове
- глобалните ReferenceLongitude/Latitude (началото на картата), RecordingTime/ReferenceTime (кога), DataSource, DataRecorder и Title в meta.json

**Пазено цяло**

- всеки непразен логически ред цял като `text` (ред, продължен с крайна обратна черта, се слепва, както го чете ACMI), под своя вид: `header` (FileType, FileVersion), `comment`, `time` (#t), `remove` (-id), `global` и `event` (обект 0), `object` (id,Key=Value,...)
- само суровият придружител пази: позициите между редовете от веднъж в секунда, оръжия, снаряди, светлини, отражатели и други обекти, които не се рисуват като траектории, всяко друго свойство (телеметрия като IAS, AOA, газ, гориво, когато записът я има), други глобални данни (Comments, Briefing, Author, Category), събития, различни от прочетените (Timeout, LeftArea ...)

**Няма го**

- нищо от това, което записът съдържа; това, което играта не пише в записите си, не е в тях

**Размер**: около текста на самия запис плюс около 70 байта на ред, преди zstd: запис от 100 MB прави около 150-250 MB суров текст, който zstd свива почти до размера на zip-натия запис

## Проверено {#verified}

тествано със синтетични ACMI 2.2 файлове (текстови и zip-нати); непроверено с запис от играта

## Източник {#source}

[heat3d_watch/adapters/il2.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/il2.py)

<!-- Generated from the adapter by tools/gen_game_pages.py; change the adapter and run it again rather than editing this page. -->
