---
title: "IL-2 Sturmovik: Great Battles (подаци уживо)"
nav_order: 26
lang: "sr"
source: game-il2.md
source_hash: "b6c4de7dcc14"
nav_exclude: true
search_exclude: true
---
# IL-2 Sturmovik: Great Battles (подаци уживо) {#il-2-sturmovik-great-battles-live-data}

Док играте IL-2 Sturmovik: Great Battles, watcher чува податке које сама игра шаље ка спољном свету, да бисте их касније погледали као статистику и временску линију.

*Технички подаци: адаптер `il2`, врста [`telemetry`](sources-and-rules.md); ради док је `Il-2.exe` или `IL2Series.exe` покренут и тражи нове податке сваких 0,1 s.*

## Шта се бележи {#what-is-recorded}

- летови: авион који је узет (spawn) и када излаз података стане (session_end) - без положаја у свету, јер игра га не шаље
- бомбе и ракете које су испуштене (маса), погоци и примљена оштећења, експлозије, рафали из митраљеза - положаји локални за авион
- еквивалентна брзина, AGL, вертикална брзина, g, број обрта мотора сваке секунде, са сваким другим индикатором који пакет носи (притисак у усисној грани, потрес мотора, стање и притисак мјењача, AoA, клизање, убрзање x/y/z, потрес кабине, закрилца, ваздушне кочнице)
- летови, испаљени меци, бомбе, ракете, примљени погоци, највећа брзина, највећи g, време лета; назив сервера и име пилота на мрежи
- сваки телеметријски пакет цео у heat.raw.parquet

## Одакле долазе подаци {#where-it-comes-from}

телеметријски UDP излаз игре на 127.0.0.1:41995 ([KEY = telemetrydevice] у &lt;game>\data\startup.cfg)

## Како га укључити {#how-to-switch-it-on}

python -m heat3d_watch setup il2 --apply (додаје addrN = "127.0.0.1:41995", enable = true), па поново покрените IL-2

Команду укуцајте у терминалу отвореном у фасцикли watcher-а (видите [Пре почетка](before-you-start.md)). Ако не успе, последњи ред каже зашто; [Инсталација и покретање](installing-and-running.md) објашњава најчешће узроке.

`python -m heat3d_watch setup il2` исписује фајлове које би променио; `python -m heat3d_watch setup il2 --apply` их мења, а оригинал чува као `<file>.heat3d-backup` (видите [Команде](commands.md#setup)). За сваку измјену исписује `il2: changed: ...`, или `il2: nothing to change` када је већ укључено.

## Како ради {#how-it-works}

IL-2 Sturmovik: Great Battles - телеметријски UDP излаз игре и њени сопствени Tacview снимци.

1. Телеметрија („Telemetry output of IL2 v4.003”, ревизија 1.2, испоручена као `<game>\Doc\UDP_Output\Il2_TeleOutput.pdf`). Укључује се у `<game>\data\startup.cfg`, одјељак `[KEY = telemetrydevice]`: `addr`, `addr1`, ... = „IP[:port]” (више одредишта истовремено), `decimation` (50 Hz / n), `enable`, `port`. `setup` додаје једно одредиште, 127.0.0.1:41995 (JoyPro користи 41994, подразумевани порт игре је 4322), и укључује излаз. Пакети, little-endian:

   ```text
   DWORD  Packet_ID 0x54000101
   WORD   Size
   DWORD  Tick (1/50 s)
   BYTE   Indicators_Count, then SIndicator {WORD id, BYTE n, n x 32-bit float}
   BYTE   Events_Count,     then SEvent     {WORD id, BYTE size, size bytes}
   ```

   Индикатори: 0 ENG_RPM, 1 ENG_MP, 2/3 потрес мотора, 4 LGEARS_STATE, 5 LGEARS_PRESS, 6 EAS (m/s), 7 AOA (rad), 8 ACCELERATION (xyz укључујући гравитацију), 9 COCKPIT_SHAKE, 10 AGL (m), 11 FLAPS, 12 AIR_BRAKES, 13 AOS (rad), 14 VERTICAL_SPEED (m/s). Догађаји (спаковани у 2 бајта): 0 SET_FOCUS (STRING: бајт дужине + ASCII), 1 SETUP_ENG {short index, short id, float pos[3], float max_rpm}, 2 SETUP_GUN {short index, float pos[3], float projectile mass, float muzzle velocity}, 3 SETUP_LGEAR {short index, short id, float pos[3]}, 4 DROP_BOMB и 5 ROCKET_LAUNCH {float pos[3], float mass, WORD flags}, 6 HIT и 7 DAMAGE {float pos[3], float force[3]}, 8 EXPLOSION {float pos[3], float radius}, 9 GUN_FIRE {BYTE gun}, 10 SRV_ADDR, 11 SRV_TITLE, 12 SRS_ADDR (STRING), 13 CLIENT_DAT {long client, long server client, char name[32]}, 14 CTRL_DAT {long parent, short coalition}. Положаји догађаја су локални за авион играча; овај ток нема никакав положај у свету - зато су ово догађаји и бројеви, а не путања.

2. Tacview снимак: `tacviewrecord = 1` у `[KEY = track_record]` тера игру да пише `<game>\data\Tracks\*.acmi` (на мрежи то одлучује сервер). Завршен фајл се претвара: сваки авион, возило и брод са својим положајима, појавом и уклањањем (уништен или нестао), полетањима и слетањима кад их снимак има. Формат ACMI 2.x текст, обичан или зип, по <https://www.tacview.net/documentation/acmi/en/> - линије „#t” померају сат, линије „id,Key=Value,...” постављају својства (хекс ид-ови, зарези escape-овани као „\\,”, а завршни „\\” наставља линију), „-id” уклања објекат, објекат 0 носи глобалне податке (ReferenceLongitude/Latitude, RecordingTime, ...) и догађаје („Event=Destroyed\|id\|text”). T = Lon\|Lat\|Alt[\|U\|V] или Lon\|Lat\|Alt\|Roll\|Pitch\|Yaw[\|U\|V\|Heading], дужина и ширина релативно у односу на референцу, празна поља се не мјењају. Положаји иду у раван мапу око референтне тачке: x источно, y висина, z сјеверно, метри. Референтна тачка је `geo` сесије, носи се у meta.json и у подножју табеле, па прегледач може да постави стварни свет испод путања.

Исти модул служи и: [IL-2 Sturmovik: Great Battles (реплеји)](game-il2-tacview.md).

## Положаји и осе {#positions-and-axes}

| | |
|---|---|
| Положаји се бележе | не |
| Оса горе | `y` |
| Јединице | нема: телеметрија нема положаје у свету |
| Огледање за прегледач | нема |
| Размера јединица (`scale`: прегледач помножи положаје с њом) | 1 |

Ово иде у `meta.json` сваке сесије (`axes`) и, када сесија има положаје, у подножје `heat.parquet`, па 3DHeat прегледач сам окреће и размењује редове - видите [Подаци](the-data.md).

## Више играча {#multiplayer}

- Означено као игра на мрежи (`multiplayer`): **да**. `games --markdown` то приказује као „дозвољено (чита само оно што игра објављује)”.
- Врста `telemetry`: чита само оно што игра или платформа даје (UDP порт или дијељену меморију коју игра објављује), па снима и у мрежној игри и ван ње; ознака одлучује само о томе смије ли се икад читати меморија.
- Меморија: овај адаптер је **никада** не чита. Само адаптери врсте `memory` читају меморију, и никад за игру означену као мрежну - видите [Извори и правила](sources-and-rules.md).

## Забиљежена статистика {#statistics-recorded}

Кључеви статистике које код овог адаптера поставља по имену (свака `stats` сесија у `meta.json` и табела `stats` у `watcher.sqlite`):

`bad_packets`, `bombs_dropped`, `damage_taken`, `explosions`, `flight_time`, `hits_taken`, `max_agl_m`, `max_eas_kmh`, `max_g`, `ordnance_kg`, `rockets_fired`, `rounds_fired`, `sorties`

Кључ у витичастим заградама се допуњује у време рада (`score.{team}` је један кључ по тиму). Кључеви које код узима из табеле поља игре или из имена статистике саме игре нису на овом списку; „Шта се бележи” горе их именује.

## Потпуност {#completeness}

Watcher прати [правило конвертера](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md) из 3DHeat-а: оно што извор садржи се чита или чува, никад се не одбацује. Осим редова, сваки пакет, страница, ред или одговор које адаптер прими чува се цео у `heat.raw.parquet` сесије (колоне `time`, `ms`, `type`, `used`, `payload`, `text`, па свако поље које се чува по имену; `used` означава оно што је постало редови), а `selfCheck.completeness` у `meta.json` броји сваки `type` - `lost` је 0.

**Чита се**

- SET_FOCUS (авион узет: лет), DROP_BOMB и ROCKET_LAUNCH (маса, локални положај), HIT и DAMAGE (локални положај, сила), EXPLOSION (локални положај, полупречник), GUN_FIRE (рафали по анкети) као редови
- SETUP_ENG (индекс, ид, локални положај, највећи број обрта), SETUP_GUN (индекс, локални положај, маса пројектила, почетна брзина) и SETUP_LGEAR (индекс, ид, локални положај) као редови: мотори, топови и ноге стајног трапа авиона кад лет почне
- SRV_TITLE, SRV_ADDR, SRS_ADDR и CLIENT_DAT (име пилота) у meta.json; коалиција из CTRL_DAT као тим лета
- свих петнаест индикатора из спецификације на редовима `state` сваке секунде (једна вредност као број, једна по мотору, ноги мјењача или оси као листа); највећа брзина, g и AGL из сваког пакета

**Чува се сирово**

- сваки датаграм цео као `payload`, под својим Packet_ID: `0x54000101` за телеметрију (користи се кад је направио ред или унос у meta.json), сваки други ид као он сам, датаграм прекратак за један као `short`
- што само сирови прилог држи: индикатори између редова од сваке секунде (игра их шаље на 50 Hz / decimation), SETUP догађај краћи од распореда у спецификацији, ид-ови догађаја које спецификација не наводи

**Није доступно**

- положај у свету: излаз телеметрије га нема (положаји догађаја су локални за авион); адаптер il2-tacview чита положаје из Tacview снимака саме игре
- други авиони и играчи: излаз описује само сопствени авион играча

**Величина**: око 8 MB на сат при 10 Hz из подешавања setup-а (decimation 5; пакет је око 160 бајтова плус његов оквир), 40 MB при пуних 50 Hz игре, пре zstd-а; zstd смањи понављајуће децималне бројеве на мали дио

## Провјерено {#verified}

тестирано на пакетима састављеним од спецификације Il2_TeleOutput саме игре (рев. 1.2); измјене startup.cfg тестиране на копији фајла; није тестирано са покренутом игром

## Извор {#source}

[heat3d_watch/adapters/il2.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/il2.py)

<!-- Generated from the adapter by tools/gen_game_pages.py; change the adapter and run it again rather than editing this page. -->
