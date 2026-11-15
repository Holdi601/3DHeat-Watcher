---
title: "IL-2 Sturmovik: Great Battles (реплеји)"
nav_order: 27
lang: "sr"
source: game-il2-tacview.md
source_hash: "0bb23bddee03"
nav_exclude: true
search_exclude: true
---
# IL-2 Sturmovik: Great Battles (реплеји) {#il-2-sturmovik-great-battles-replays}

Након меча IL-2 Sturmovik: Great Battles, посматрач претвара реплеј који је игра сачувала у датотеке које можете погледати на мапи у 3DHeat прегледачу.

*Технички детаљи: адаптер `il2-tacview`, врста [`replay`](sources-and-rules.md); ради стално (не чека да се игра покрене) и тражи нове податке сваких 5 s.*

## Шта се бележи {#what-is-recorded}

- сваки авион, возило и брод из снимка: положаји сваке секунде (метри источно/горе/северно од референтне тачке снимка; географска ширина и дужина и висина као колоне)
- појављивања, уништења (смрт) и одласци (left), полетања и слетања кад су снимљени
- објекти, уништени, полетања, слетања и дужина по снимку
- сваки ред снимка цео у heat.raw.parquet, на сату редова

## Одакле долази {#where-it-comes-from}

сопствени Tacview снимци игре `<game>\data\Tracks\\\*.acmi` (ACMI 2.x текст, обичан или спакован)

## Како се укључује {#how-to-switch-it-on}

python -m heat3d_watch setup il2-tacview --apply (tacviewrecord = 1 у [KEY = track_record])

Укуцајте команду у терминалу отвореном у фасцикли посматрача (видети [Пре почетка](before-you-start.md)). Ако не успе, последњи ред каже зашто; [Инсталација и покретање](installing-and-running.md) објашњава уобичајене узроке.

`python -m heat3d_watch setup il2-tacview` исписује датотеке које би променио; `python -m heat3d_watch setup il2-tacview --apply` их мења, а оригинал чува као `<file>.heat3d-backup` (видети [Команде](commands.md#setup)). За сваку промену исписује `il2-tacview: changed: ...`, или `il2-tacview: nothing to change` ако је већ укључено.

## Како ради {#how-it-works}

IL-2 Sturmovik: Great Battles – телеметријски UDP излаз игре и њени сопствени Tacview снимци.

1. Телеметрија („Telemetry output of IL2 v4.003“, ревизија 1.2, испоручена као `<game>\Doc\UDP_Output\Il2_TeleOutput.pdf`). Укључује се у `<game>\data\startup.cfg`, одељак `[KEY = telemetrydevice]`: `addr`, `addr1`, ... = „IP[:port]“ (више одредишта истовремено), `decimation` (50 Hz / n), `enable`, `port`. `setup` додаје једно одредиште, 127.0.0.1:41995 (JoyPro користи 41994, а подразумевани порт игре је 4322), и укључује излаз. Пакети, little-endian:

   ```text
   DWORD  Packet_ID 0x54000101
   WORD   Size
   DWORD  Tick (1/50 s)
   BYTE   Indicators_Count, then SIndicator {WORD id, BYTE n, n x 32-bit float}
   BYTE   Events_Count,     then SEvent     {WORD id, BYTE size, size bytes}
   ```

   Индикатори: 0 ENG_RPM, 1 ENG_MP, 2/3 engine shake, 4 LGEARS_STATE, 5 LGEARS_PRESS, 6 EAS (m/s), 7 AOA (rad), 8 ACCELERATION (xyz укључујући гравитацију), 9 COCKPIT_SHAKE, 10 AGL (m), 11 FLAPS, 12 AIR_BRAKES, 13 AOS (rad), 14 VERTICAL_SPEED (m/s). Догађаји (спаковани по 2 бајта): 0 SET_FOCUS (STRING: бајт дужине + ASCII), 1 SETUP_ENG {short index, short id, float pos[3], float max_rpm}, 2 SETUP_GUN {short index, float pos[3], float projectile mass, float muzzle velocity}, 3 SETUP_LGEAR {short index, short id, float pos[3]}, 4 DROP_BOMB и 5 ROCKET_LAUNCH {float pos[3], float mass, WORD flags}, 6 HIT и 7 DAMAGE {float pos[3], float force[3]}, 8 EXPLOSION {float pos[3], float radius}, 9 GUN_FIRE {BYTE gun}, 10 SRV_ADDR, 11 SRV_TITLE, 12 SRS_ADDR (STRING), 13 CLIENT_DAT {long client, long server client, char name[32]}, 14 CTRL_DAT {long parent, short coalition}. Положаји догађаја су локални у односу на авион играча; ток нема уопште светски положај – зато су ово догађаји и бројеви, а не путања.

2. Tacview снимак: `tacviewrecord = 1` у `[KEY = track_record]` тера игру да пише `<game>\data\Tracks\*.acmi` (у мултиплејеру сервер одлучује). Завршена датотека се претвара: сваки авион, возило и брод са својим положајима, појављивањем и уклањањем (уништен или отишао), полетањима и слетањима кад их снимак има. ACMI 2.x текстуални формат, обичан или спакован, према <https://www.tacview.net/documentation/acmi/en/> – редови „#t“ померају сат, редови „id,Key=Value,...“ постављају својства (ид-ови у хексу, зарези се бекслеш-ескејпују „\\,“, а завршни „\\“ наставља ред), „-id“ уклања објекат, објекат 0 носи глобалне податке (ReferenceLongitude/Latitude, RecordingTime, ...) и догађаје („Event=Destroyed\|id\|text“). T = Lon\|Lat\|Alt[\|U\|V] или Lon\|Lat\|Alt\|Roll\|Pitch\|Yaw[\|U\|V\|Heading], дужина и географска ширина су у односу на референцу, празна поља се не мењају. Положаји иду у раван мапу око референтне тачке: x источно, y висина, z северно, у метрима. Референтна тачка је `geo` сесије, сачувана у meta.json-у и у подножју табеле, па прегледач може да постави стварни свет испод путања.

Исти модул служи и: [IL-2 Sturmovik: Great Battles (подаци уживо)](game-il2.md).

## Положаји и осе {#positions-and-axes}

| | |
|---|---|
| Бележени положаји | да |
| Вертикална оса | `y` |
| Јединице | метри (источно, висина, северно од прве тачке) |
| Огледало за прегледач | `z` |
| Размера јединице (`scale`: прегледач множи положаје са њом) | 1 |

Ово иде у `meta.json` (`axes`) сваке сесије и, кад сесија има положаје, у подножје `heat.parquet`-а, па прегледач 3DHeat сам окреће и размерава редове – видети [Подаци](the-data.md).

## Више играча {#multiplayer}

- Означено као игра на мрежи (`multiplayer`): **да**. `games --markdown` ово приказује као „дозвољено (чита само оно што игра објављује)“.
- Врста `replay`: чита само оно што игра или платформа даје (реплеји и демои које игра сачува), па бележи и у игри на мрежи и ван ње; застава одлучује само да ли меморија сме икада да се чита.
- Меморија: **никад** је овај адаптер не чита. Само `memory` адаптери читају меморију, и никад за игру означену као игра на мрежи – видети [Извори и правила](sources-and-rules.md).

## Бележена статистика {#statistics-recorded}

Кључеви статистике које код овог адаптера поставља по имену (`stats` сваке сесије у `meta.json`-у и табела `stats` у `watcher.sqlite`-у):

`destroyed`, `duration_s`, `objects`, `{r.event}s`

Кључ у витичастим заградама се допуњава у време рада (`score.{team}` је један кључ по тиму). Кључеви које код узима из табеле поља игре или из назива статистике саме игре нису на овом списку; у „Шта се бележи“ горе они су наведени.

## Потпуност {#completeness}

Посматрач прати [правило конвертора](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md) из 3DHeat-а: оно што извор садржи се чита или чува, никад се не одбацује. Осим редова, сваки пакет, страница, ред или одговор који адаптер прими чува се цео у `heat.raw.parquet` сесије (колоне `time`, `ms`, `type`, `used`, `payload`, `text`, па свако поље које се чува по имену; `used` означава оно што је постало и редове), а `selfCheck.completeness` у `meta.json`-у броји сваки `type` – `lost` је 0.

**Чита се**

- T сваког објекта (дужина, географска ширина, висина, roll, pitch, yaw, U, V, heading) као положај сваке секунде по објекту, са Name, Type, Pilot, Coalition/Color, Country, Group и Parent
- појављивања, уклањања (смрт кад је први пристигао догађај Destroyed, иначе left), догађаји TakenOff и Landed, Message и Bookmark догађаји као редови
- глобални подаци ReferenceLongitude/Latitude (почетак мапе), RecordingTime/ReferenceTime (када), DataSource, DataRecorder и Title у meta.json

**Чува се сирово**

- сваки непразан логички ред цео као `text` (ред настављен завршним обрнутом косом цртом спаја се, како га ACMI чита), под својом врстом: `header` (FileType, FileVersion), `comment`, `time` (#t), `remove` (-id), `global` и `event` (објекат 0), `object` (id,Key=Value,...)
- што само сирови део садржи: положаји између редова који се бележе једном у секунди, оружје, гранате, бакље, плеве и остали објекти који се не црта као путање, свако друго својство (телеметрију као IAS, AOA, гас, гориво где снимак то има), остали глобални подаци (Comments, Briefing, Author, Category), догађаји осим прочитаних (Timeout, LeftArea, ...)

**Није доступно**

- ништа што снимак не садржи; што игра не упише у своје снимке, није у њима

**Величина**: око текста самог снимка плус око 70 бајтова по реду, пре zstd: снимак од 100 MB прави око 150–250 MB сировог текста, који zstd сабије близу величине спакованог снимка

## Проверено {#verified}

тестирано на синтетичким ACMI 2.2 датотекама (текст и спаковане); није тестирано на снимку из игре

## Извор {#source}

[heat3d_watch/adapters/il2.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/il2.py)

<!-- Generated from the adapter by tools/gen_game_pages.py; change the adapter and run it again rather than editing this page. -->
