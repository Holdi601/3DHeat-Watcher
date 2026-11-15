---
title: "IL-2 Sturmovik: Great Battles (повторувања)"
nav_order: 27
lang: "mk"
source: game-il2-tacview.md
source_hash: "0bb23bddee03"
nav_exclude: true
search_exclude: true
---
# IL-2 Sturmovik: Great Battles (повторувања) {#il-2-sturmovik-great-battles-replays}

По натпреварот во IL-2 Sturmovik: Great Battles, Watcher го претвора повторувањето што го зачувала играта во датотеки што можете да ги погледнете на мапа во прегледувачот 3DHeat.

*Технички детали: адаптер `il2-tacview`, вид [`replay`](sources-and-rules.md); работи постојано (не чека да почне игра) и бара нови податоци на секои 5 s.*

## Што се снима {#what-is-recorded}

- секој авион, возило и брод од снимката: позиции еднаш во секунда (метри исток/нагоре/север од референтната точка на снимката; lat/lon/alt како колони)
- појавувања, уништувања (death) и заминувања (left), полетувања и слетувања кога се снимени
- објекти, уништени, полетувања, слетувања и должина по снимка
- секоја линија од снимката цела во heat.raw.parquet, на часовникот на редовите

## Од каде доаѓа {#where-it-comes-from}

сопствените Tacview снимки на играта &lt;game>\data\Tracks\\\*.acmi (ACMI 2.x текст, обичен или збиен во zip)

## Како да се вклучи {#how-to-switch-it-on}

python -m heat3d_watch setup il2-tacview --apply (tacviewrecord = 1 во [KEY = track_record])

Впишете ја командата во терминал отворен во папката на Watcher (види [Пред да почнете](before-you-start.md)). Ако не успее, последната линија кажува зошто; [Инсталирање и стартување](installing-and-running.md) ги опфаќа вообичаените причини.

`python -m heat3d_watch setup il2-tacview` ги наведува датотеките што би ги променил; `python -m heat3d_watch setup il2-tacview --apply` ги менува, чувајќи го оригиналот како `<file>.heat3d-backup` (види [Команди](commands.md#setup)). Печати `il2-tacview: changed: ...` за секоја промена, или `il2-tacview: nothing to change` кога веќе е вклучено.

## Како работи {#how-it-works}

IL-2 Sturmovik: Great Battles - UDP излезот за телеметрија на играта и нејзините сопствени Tacview снимки.

1. Телеметрија („Telemetry output of IL2 v4.003", ревизија 1.2, испорачана како
   `<game>\Doc\UDP_Output\Il2_TeleOutput.pdf`). Се вклучува во
   `<game>\data\startup.cfg`, дел `[KEY = telemetrydevice]`: `addr`,
   `addr1`, ... = „IP[:port]" (повеќе цели одеднаш), `decimation` (50 Hz /
   n), `enable`, `port`. `setup` додава една цел, 127.0.0.1:41995 (JoyPro користи
   41994, стандардната на играта е 4322), и го вклучува излезот. Пакети,
   little-endian:

   ```text
   DWORD  Packet_ID 0x54000101
   WORD   Size
   DWORD  Tick (1/50 s)
   BYTE   Indicators_Count, then SIndicator {WORD id, BYTE n, n x 32-bit float}
   BYTE   Events_Count,     then SEvent     {WORD id, BYTE size, size bytes}
   ```

   Индикатори: 0 ENG_RPM, 1 ENG_MP, 2/3 engine shake, 4 LGEARS_STATE, 5
   LGEARS_PRESS, 6 EAS (m/s), 7 AOA (rad), 8 ACCELERATION (xyz вклучувајќи гравитација),
   9 COCKPIT_SHAKE, 10 AGL (m), 11 FLAPS, 12 AIR_BRAKES, 13 AOS (rad), 14
   VERTICAL_SPEED (m/s). Настани (спакувани по 2 бајти): 0 SET_FOCUS (STRING: бајт за должина
   + ASCII), 1 SETUP_ENG {short index, short id, float pos[3], float
   max_rpm}, 2 SETUP_GUN {short index, float pos[3], float projectile mass,
   float muzzle velocity}, 3 SETUP_LGEAR {short index, short id, float
   pos[3]}, 4 DROP_BOMB и 5 ROCKET_LAUNCH
   {float pos[3], float mass, WORD flags}, 6 HIT и 7 DAMAGE {float pos[3],
   float force[3]}, 8 EXPLOSION {float pos[3], float radius}, 9 GUN_FIRE {BYTE
   gun}, 10 SRV_ADDR, 11 SRV_TITLE, 12 SRS_ADDR (STRING), 13 CLIENT_DAT {long
   client, long server client, char name[32]}, 14 CTRL_DAT {long parent, short
   coalition}. Положбите на настаните се локални за авионот на играчот; потокот
   воопшто нема светска позиција - затоа ова се настани и броеви, не патека.

2. Tacview снимка: `tacviewrecord = 1` во `[KEY = track_record]` прави играта
   да пишува `<game>\data\Tracks\*.acmi` (во повеќе играчи одлучува серверот).
   Завршената датотека се претвора: секој авион, возило и брод со своите
   позиции, појавување и отстранување (уништен или заминат), полетувања и слетувања кога
   снимката ги има. ACMI 2.x текстуален формат, обичен или збиен во zip, според
   <https://www.tacview.net/documentation/acmi/en/> - линиите „#t" го поместуваат часовникот,
   линиите „id,Key=Value,..." поставуваат својства (хексадецимални ид-ови, запирки со escape „\\,", 
   завршно „\\" ја продолжува линијата), „-id" отстранува објект, објектот 0 ги носи
   глобалите (ReferenceLongitude/Latitude, RecordingTime, ...) и настаните
   („Event=Destroyed\|id\|text"). T = Lon\|Lat\|Alt[\|U\|V] или
   Lon\|Lat\|Alt\|Roll\|Pitch\|Yaw[\|U\|V\|Heading], географска должина и ширина релативно спрема
   референцата, празните полиња се непроменети. Позициите одат во рамна мапа околу
   референтната точка: x исток, y висина, z север, метри. Референтната
   точка е `geo` на сесијата, носена во meta.json и подножјето на табелата,
   за прегледувачот да може да го постави вистинскиот свет под патеките.

Истиот модул служи и за: [IL-2 Sturmovik: Great Battles (податоци во живо)](game-il2.md).

## Позиции и оски {#positions-and-axes}

| | |
|---|---|
| Позициите се снимаат | да |
| Оска нагоре | `y` |
| Единици | метри (исток, висина, север од првата положба) |
| Огледално за прегледувачот | `z` |
| Размер на единиците (`scale`: прегледувачот ги множи позициите со него) | 1 |

Тие одат во `meta.json` на секоја сесија (`axes`) и, кога сесијата има позиции, во подножјето на `heat.parquet`, па прегледувачот 3DHeat самиот ги врти и размерува редовите - види [Податоците](the-data.md).

## Повеќе играчи {#multiplayer}

- Означено како играно онлајн (`multiplayer`): **да**. `games --markdown` го прикажува ова како „allowed (reads only what the game publishes)".
- Вид `replay`: чита само она што играта или платформата го дава (повторувања и демо-снимки што играта ги зачувува), па снима и во онлајн игра и офлајн; знамето одлучува само дали меморијата смее некогаш да се чита.
- Меморија: овој адаптер **никогаш** не ја чита. Само адаптерите `memory` читаат меморија, и никогаш за игра означена како играна онлајн - види [Извори и правила](sources-and-rules.md).

## Снимена статистика {#statistics-recorded}

Клучевите на статистиката што кодот на овој адаптер ги поставува по име (`stats` во `meta.json` на секоја сесија и табелата `stats` во `watcher.sqlite`):

`destroyed`, `duration_s`, `objects`, `{r.event}s`

Клуч во загради се дополнува при извршување (`score.{team}` е еден клуч по тим). Клучевите што кодот ги зема од табела со полињата на играта или од сопствените имиња на статистиката на играта не се во овој список; „Што се снима" погоре ги именува.

## Комплетност {#completeness}

Watcher го следи [правилото за конвертори](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md) на 3DHeat: она што го држи изворот се чита или се чува, никогаш не се отфрла. Покрај редовите, секој пакет, страница, линија или одговор што адаптерот ги прима се чува цел во `heat.raw.parquet` на сесијата (колони `time`, `ms`, `type`, `used`, `payload`, `text`, потоа секое поле зачувано по име; `used` означува што станало и редови), а `selfCheck.completeness` во `meta.json` го брои секој `type` - `lost` е 0.

**Читано**

- T на секој објект (географска должина, ширина, висина, roll, pitch, yaw, U, V, heading) како позиции еднаш во секунда по објект, со Name, Type, Pilot, Coalition/Color, Country, Group и Parent
- појавувања, отстранувања (death кога прво дошол настан Destroyed, инаку left), настаните TakenOff и Landed, настаните Message и Bookmark како редови
- глобалите ReferenceLongitude/Latitude (потеклото на мапата), RecordingTime/ReferenceTime (кога), DataSource, DataRecorder и Title во meta.json

**Чувано сурово**

- секоја непразна логичка линија цела како `text` (линија продолжена со завршна обратна коса црта се спојува, како што ја чита ACMI), под својот вид: `header` (FileType, FileVersion), `comment`, `time` (#t), `remove` (-id), `global` и `event` (објект 0), `object` (id,Key=Value,...)
- она што го држи само суровата придружна датотека: позициите меѓу редовите од еднаш во секунда, оружје, гранати, сигнални ракети, дипол-ленти и други објекти што не се цртаат како патеки, секое друго својство (телеметрија како IAS, AOA, гас, гориво кога снимката ја има), други глобали (Comments, Briefing, Author, Category), настани освен прочитаните (Timeout, LeftArea, ...)

**Не е достапно**

- ништо што снимката го држи; она што играта не го пишува во своите снимки не е во нив

**Големина**: околу сопствениот текст на снимката плус некои 70 бајти по линија, пред zstd: снимка од 100 MB дава околу 150-250 MB суров текст, што zstd го доведува близу до големината на збиената снимка

## Проверено {#verified}

тестирано на синтетички ACMI 2.2 датотеки (текст и збиени); не е тестирано на снимка од играта

## Извор {#source}

[heat3d_watch/adapters/il2.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/il2.py)

<!-- Generated from the adapter by tools/gen_game_pages.py; change the adapter and run it again rather than editing this page. -->
