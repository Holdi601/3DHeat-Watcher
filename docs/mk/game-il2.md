---
title: "IL-2 Sturmovik: Great Battles (податоци во живо)"
nav_order: 26
lang: "mk"
source: game-il2.md
source_hash: "b6c4de7dcc14"
nav_exclude: true
search_exclude: true
---
# IL-2 Sturmovik: Great Battles (податоци во живо) {#il-2-sturmovik-great-battles-live-data}

Додека играте IL-2 Sturmovik: Great Battles, Watcher ги зачувува податоците што ги испраќа самата игра, за подоцна да можете да ги погледнете како статистика и временска лента.

*Технички детали: адаптер `il2`, вид [`telemetry`](sources-and-rules.md); работи додека работи `Il-2.exe` или `IL2Series.exe` и бара нови податоци на секои 0,1 s.*

## Што се снима {#what-is-recorded}

- мисии (sorties): земениот авион (spawn) и кога ќе запре излезот (session_end) - без светска позиција: играта не испраќа таква
- испуштени бомби и ракети (маса), погодоци и примена штета, експлозии, рафали од оружје - позиции локални за авионот
- еквивалентна брзина на воздухот, AGL, вертикална брзина, g, вртежи на моторот еднаш во секунда, со секој друг индикатор што го носи пакетот (притисок во колекторот, тресење на моторот, состојба и притисок на стајниот трап, AoA, странично лизгање, забрзување x/y/z, тресење на кабината, закрилца, воздушни сопирачки)
- мисии, истрелани куршуми, бомби, ракети, примени погодоци, највисока брзина, највисоко g, време на летање; наслов на серверот и име на пилотот онлајн
- секој пакет со телеметрија се чува цело во heat.raw.parquet

## Од каде доаѓа {#where-it-comes-from}

UDP излезот за телеметрија на играта кон 127.0.0.1:41995 ([KEY = telemetrydevice] во &lt;game>\data\startup.cfg)

## Како да се вклучи {#how-to-switch-it-on}

python -m heat3d_watch setup il2 --apply (додава addrN = "127.0.0.1:41995", enable = true), рестартирајте го IL-2

Впишете ја командата во терминал отворен во папката на Watcher (види [Пред да почнете](before-you-start.md)). Ако не успее, последната линија кажува зошто; [Инсталирање и стартување](installing-and-running.md) ги опфаќа вообичаените причини.

`python -m heat3d_watch setup il2` ги наведува датотеките што би ги променил; `python -m heat3d_watch setup il2 --apply` ги менува, чувајќи го оригиналот како `<file>.heat3d-backup` (види [Команди](commands.md#setup)). Печати `il2: changed: ...` за секоја промена, или `il2: nothing to change` кога веќе е вклучено.

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

Истиот модул служи и за: [IL-2 Sturmovik: Great Battles (повторувања)](game-il2-tacview.md).

## Позиции и оски {#positions-and-axes}

| | |
|---|---|
| Позициите се снимаат | не |
| Оска нагоре | `y` |
| Единици | никакви: телеметријата нема светски позиции |
| Огледално за прегледувачот | нема |
| Размер на единиците (`scale`: прегледувачот ги множи позициите со него) | 1 |

Тие одат во `meta.json` на секоја сесија (`axes`) и, кога сесијата има позиции, во подножјето на `heat.parquet`, па прегледувачот 3DHeat самиот ги врти и размерува редовите - види [Податоците](the-data.md).

## Повеќе играчи {#multiplayer}

- Означено како играно онлајн (`multiplayer`): **да**. `games --markdown` го прикажува ова како „allowed (reads only what the game publishes)".
- Вид `telemetry`: чита само она што играта или платформата го дава (UDP порта или споделена меморија што играта ја објавува), па снима и во онлајн игра и офлајн; знамето одлучува само дали меморијата смее некогаш да се чита.
- Меморија: овој адаптер **никогаш** не ја чита. Само адаптерите `memory` читаат меморија, и никогаш за игра означена како играна онлајн - види [Извори и правила](sources-and-rules.md).

## Снимена статистика {#statistics-recorded}

Клучевите на статистиката што кодот на овој адаптер ги поставува по име (`stats` во `meta.json` на секоја сесија и табелата `stats` во `watcher.sqlite`):

`bad_packets`, `bombs_dropped`, `damage_taken`, `explosions`, `flight_time`, `hits_taken`, `max_agl_m`, `max_eas_kmh`, `max_g`, `ordnance_kg`, `rockets_fired`, `rounds_fired`, `sorties`

Клуч во загради се дополнува при извршување (`score.{team}` е еден клуч по тим). Клучевите што кодот ги зема од табела со полињата на играта или од сопствените имиња на статистиката на играта не се во овој список; „Што се снима" погоре ги именува.

## Комплетност {#completeness}

Watcher го следи [правилото за конвертори](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md) на 3DHeat: она што го држи изворот се чита или се чува, никогаш не се отфрла. Покрај редовите, секој пакет, страница, линија или одговор што адаптерот ги прима се чува цел во `heat.raw.parquet` на сесијата (колони `time`, `ms`, `type`, `used`, `payload`, `text`, потоа секое поле зачувано по име; `used` означува што станало и редови), а `selfCheck.completeness` во `meta.json` го брои секој `type` - `lost` е 0.

**Читано**

- SET_FOCUS (земениот авион: мисија), DROP_BOMB и ROCKET_LAUNCH (маса, локална позиција), HIT и DAMAGE (локална позиција, сила), EXPLOSION (локална позиција, радиус), GUN_FIRE (куршуми по анкета) како редови
- SETUP_ENG (индекс, ид, локална позиција, максимални вртежи), SETUP_GUN (индекс, локална позиција, маса на проектилот, почетна брзина) и SETUP_LGEAR (индекс, ид, локална позиција) како редови: моторите, оружјето и ногарките на стајниот трап на авионот при почетокот на мисијата
- SRV_TITLE, SRV_ADDR, SRS_ADDR и CLIENT_DAT (име на пилот) во meta.json; coalition од CTRL_DAT како тим на мисијата
- сите петнаесет индикатори од спецификацијата на редот `state` еднаш во секунда (една вредност како број, по една за мотор, ногарка на трап или оска како листа); највисока брзина, g и AGL од секој пакет

**Чувано сурово**

- секоја дејтаграма цела како `payload`, под својот Packet_ID: `0x54000101` за телеметрија (`used` кога направила ред или запис во meta.json), секој друг ид како самиот себе, дејтаграма прекратка за еден како `short`
- она што го држи само суровата придружна датотека: индикаторите меѓу редовите од еднаш во секунда (играта ги праќа со 50 Hz / decimation), настан SETUP пократок од распоредот во спецификацијата, ид-ови на настани што спецификацијата не ги наведува

**Не е достапно**

- светска позиција: излезот за телеметрија нема (положбите на настаните се локални за авионот); адаптерот il2-tacview чита позиции од сопствените Tacview снимки на играта
- други авиони и играчи: излезот го опишува само сопствениот авион на играчот

**Големина**: околу 8 MB на час со 10 Hz од `setup` (decimation 5; пакетот е околу 160 бајти плус неговата рамка), 40 MB со целите 50 Hz на играта, пред zstd; zstd ги собира повторливите децимални броеви на мал дел

## Проверено {#verified}

тестирано на пакети изградени според сопствената спецификација Il2_TeleOutput на играта (рев. 1.2); измените на startup.cfg се тестирани на копија од датотеката; не е тестирано со играта во работа

## Извор {#source}

[heat3d_watch/adapters/il2.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/il2.py)

<!-- Generated from the adapter by tools/gen_game_pages.py; change the adapter and run it again rather than editing this page. -->
