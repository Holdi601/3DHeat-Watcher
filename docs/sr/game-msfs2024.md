---
title: "Microsoft Flight Simulator 2024 (живи подаци)"
nav_order: 32
lang: "sr"
source: game-msfs2024.md
source_hash: "011c18a23252"
nav_exclude: true
search_exclude: true
---
# Microsoft Flight Simulator 2024 (живи подаци) {#microsoft-flight-simulator-2024-live-data}

Док играте Microsoft Flight Simulator 2024, посматрач чува податке које сама игра шаље, па то касније можете да погледате на мапи у 3DHeat приказивачу.

*Технички детаљи: адаптер `msfs2024`, врста [`telemetry`](sources-and-rules.md); ради док је `FlightSimulator2024.exe` покренут и тражи нове податке сваких 0,1 s.*

## Шта се снима {#what-is-recorded}

- положај сопственог авиона при сваком кадру симулације, узет 10 пута у секунди (географска ширина/дужина/висина као метри источно/горе/северно од прве тачке; lat/lon/alt сачуване као колоне)
- став, индициран ваздушни брзина, брзина у односу на земљу, висина изнад земље, g, на земљи или не; прави ваздушна брзина, Mach, вертикална брзина, напад, клизање, магнетни курс, брзине тела, убрзања и брзине ротације око 10 пута у секунди
- тежина, гориво, закрилца, стајни трап, спојлери, паркирна кочница, аутопилот, гас, обртаји, временске прилике, брзина симулације, време и стање камере сваке секунде; назив летелице и ATC тип, модел и ид
- полетања, слетања, падови, почети и завршени летови (session_start/session_end)
- време лета, време у ваздуху, дистанца, највећа висина, највећи g, слетања
- свака SimConnect порука, цела, у heat.raw.parquet

## Одакле долази {#where-it-comes-from}

SimConnect преко сопственог SimConnect.dll играча (фасцикла симулатора, или %MSFS2024_SDK%\SimConnect SDK\lib)

## Како се укључује {#how-to-switch-it-on}

ништа у симулатору; треба SimConnect.dll - MSFS 2020 га има у својој фасцикли, играчи MSFS 2024 инсталирају MSFS 2024 SDK

## Како ради {#how-it-works}

Microsoft Flight Simulator 2020 и 2024: SimConnect, преко сопственог SimConnect.dll играча.

SimConnect је објављени клијентски API симулатора (документација SDK-а:
<https://docs.flightsimulator.com/html/Programming_Tools/SimConnect/SimConnect_SDK.htm>,
<https://docs.flightsimulator.com/msfs2024/html/6_Programming_APIs/SimConnect/SimConnect_SDK.htm>).
Посматрач не испоручује DLL: учитава онај који је дошао уз симулатор или његов SDK - MSFS 2020 ставља `SimConnect.dll` у своју фасциклу за инсталацију; MSFS 2024 на Steam-у испоручује само свој интерни, па играчи 2024 инсталирају MSFS 2024 SDK (`<SDK>\SimConnect SDK\lib\SimConnect.dll`; симулатор 2024 прихвата и клијенте за 2020).

Позиви, из SimConnect.h, сви враћају HRESULT (0 = S_OK):

```text
SimConnect_Open(HANDLE*, LPCSTR name, HWND, DWORD, HANDLE, DWORD config)
SimConnect_AddToDataDefinition(HANDLE, DWORD define, LPCSTR var, LPCSTR units,
                               SIMCONNECT_DATATYPE (FLOAT64 = 4), float epsilon, DWORD datum)
SimConnect_RequestDataOnSimObject(HANDLE, DWORD request, DWORD define, DWORD object (0 = user),
                                  SIMCONNECT_PERIOD (SIM_FRAME = 3), DWORD flags, DWORD origin,
                                  DWORD interval, DWORD limit)
SimConnect_SubscribeToSystemEvent(HANDLE, DWORD event, LPCSTR name)
SimConnect_GetNextDispatch(HANDLE, SIMCONNECT_RECV**, DWORD*)   E_FAIL кад ништа не чека
SimConnect_Close(HANDLE)
```

Свака порука почиње са SIMCONNECT_RECV {DWORD dwSize, dwVersion, dwID} (#pragma pack 1). Оне које се овде читају:

```text
1  EXCEPTION       dwException, dwSendID, dwIndex
2  OPEN            szApplicationName[256], па DWORD-ови верзије
3  QUIT            симулатор се затвара
4  EVENT           uGroupID, uEventID, dwData
6  EVENT_FILENAME  EVENT + szFileName[260], dwFlags        (FlightLoaded)
8  SIMOBJECT_DATA  dwRequestID, dwObjectID, dwDefineID, dwFlags, dwentrynumber,
                   dwoutof, dwDefineCount, па вредности (овде сваки FLOAT64)
```

Променљиве симулације (тражене јединице, па није потребна претварање): PLANE LATITUDE/LONGITUDE (степени), PLANE ALTITUDE (метри, изнад мора), PLANE ALT ABOVE GROUND (метри), PLANE PITCH/BANK DEGREES и PLANE HEADING DEGREES TRUE (степени; SimConnect-ови сопствени знаци - нос горе је негативан нагиб), AIRSPEED INDICATED и GROUND VELOCITY (чворови), G FORCE (gforce), SIM ON GROUND (bool). Системски догађаји: SimStart, SimStop, Crashed, FlightLoaded, AircraftLoaded, Pause, CrashReset, PositionChanged, FlightSaved, Sim.

Три даља дефиниције података траже остатак лета (`MOTION_VARS`, сваки шести кадар симулације), спорије стање летелице (`STATE_VARS`, једном у секунди) и њена имена (`NAME_VARS`, стрингови од 256 бајтова, кад се промене); свака је своја дефиниција, па променљива коју нека верзија симулатора не познаје кошта само тај блок. Свака порука се чува цела у сировој пратећој датотеци сесије.

Положаји иду у исту равну мапу као и X-Plane-ова (x исток, y висина, z север, у метрима од прве тачке лета); та тачка је `geo` сесије, у meta.json-у и подножју табеле.

Исти модул служи и: [Microsoft Flight Simulator 2020 (живи подаци)](game-msfs2020.md).

## Положаји и осе {#positions-and-axes}

| | |
|---|---|
| Положаји се бележе | да |
| Оса нагоре | `y` |
| Јединице | метри (исток, висина, север од прве тачке) |
| Огледално за приказивач | `z` |
| Размера јединице (`scale`: приказивач множи положаје њом) | 1 |

Ово иде у `meta.json` сваке сесије (`axes`) и, кад сесија има положаје, у подножје `heat.parquet`-а, па 3DHeat приказивач сам окреће и скалира редове - видите [Подаци](the-data.md).

## Више играча {#multiplayer}

- Означено као игра на мрежи (`multiplayer`): **да**. `games --markdown` ово приказује као "allowed (reads only what the game publishes)".
- Врста `telemetry`: чита само оно што игра или платформа даје (UDP порт или дељена меморија коју игра објављује), па снима и у мрежној игри и ван ње; ознака одлучује само да ли се меморија икад сме читати.
- Меморија: **никад** се не чита овим адаптером. Само адаптери `memory` читају меморију, и никад за игру означену као игру на мрежи - видите [Извори и правила](sources-and-rules.md).

## Снимљена статистика {#statistics-recorded}

Кључеви статистике које код овог адаптера поставља по имену (`stats` сваке сесије у `meta.json` и табела `stats` у `watcher.sqlite`):

`airborne_time`, `bad_packets`, `crashes`, `distance_km`, `flight_time`, `max_altitude_m`, `max_g`, `{event}s`

Кључ у витичастим заградама се допуњује за време рада (`score.{team}` је један кључ по тиму). Кључеви које код узима из табеле поља игре или из назива статистике саме игре нису у овом списку; "Шта се снима" горе их наводи.

## Потпуност {#completeness}

Посматрач следи [правило конвертера](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md) 3DHeat-а: оно што извор садржи се чита или чува, никад не одбацује. Осим редова, сваки пакет, страница, линија или одговор који адаптер прими чува се цео у `heat.raw.parquet` сесије (колоне `time`, `ms`, `type`, `used`, `payload`, `text`, па свако поље које се чува по имену; `used` означава оно што је постало и редови), а `selfCheck.completeness` у `meta.json`-у броји сваки `type` - `lost` је 0.

**Чита се**

- SIMOBJECT_DATA дефиниције положаја (сваки кадар симулације): географска ширина, дужина, висина, висина изнад земље, нагиб, ваљање, прави курс, IAS, брзина у односу на земљу, g, на земљи - последњи кадар анкете као ред, сваки кадар за додире и полетања
- SIMOBJECT_DATA дефиниције кретања (око 10 Hz: TAS, Mach, вертикална брзина, напад, клизање, магнетни курс, брзина тела, убрзање и брзина ротације на три осе) и дефиниције стања (1 Hz: тежине, гориво, закрилца, стајни трап, спојлери, паркирна кочница, аутопилот, мотори, гас и обртаји, спољна температура, ветар, притисак на нивоу мора, брзина симулације, зулу и локално време, стање камере) на редове онако како су последњи пут стигли
- SIMOBJECT_DATA дефиниције имена (назив, ATC тип, модел и ид) у meta.json и у `aircraft` редова; OPEN (апликација и верзија) у meta.json
- EVENT и EVENT_FILENAME: SimStart, SimStop, Crashed, FlightLoaded (датотека лета) и AircraftLoaded (датотека летелице) као летови, падови и meta.json
- QUIT завршава сесију

**Чува се сирово**

- свака порука коју SimConnect достави посматрачу, цела као `payload`, под називом њеног SIMCONNECT_RECV_ID: `SIMOBJECT_DATA`, `EVENT`, `EVENT_FILENAME`, `OPEN`, `QUIT`, `EXCEPTION` (променљива или догађај који симулатор није прихватио, са ид-ом слања и индексом), сваки други ид по називу или `RECV_<id>`
- што само сирова пратећа датотека садржи: положај сваког кадра симулације између редова, догађаји Pause, Sim, CrashReset, PositionChanged и FlightSaved, дефиниција коју је симулатор скратио (једна променљива коју није познавао: тај блок се онда не чита по имену); `requests` у meta.json наводи променљиве и јединице сваке дефиниције по реду, па се корисни товари читају и без овог модула

**Није доступно**

- други авиони (саобраћај AI-ја, други играчи на мрежи): SimConnect_RequestDataOnSimObjectType би анкетирао сваку летелицу у кругу - више оптерећења симулатора и туђи летови
- блок кретања сваки кадар симулације: тражи се сваки шести кадар (око 10 Hz, брзина редова), што сирови ток задржава близу једне петине; блок положаја остаје сваки кадар
- хиљаде других променљивих симулације (радио, светла, сваки мерач мотора, квартови): дефиниција садржи само оно што тражи; списци траже лет, стање летелице и време симулатора
- подаци о времену (осматрања), објекти (аеродроми, VOR-ови), клијентски подаци додатака: засебни захтеви, не шаљу се

**Величина**: око 30-55 MB по сату пре zstd: блок положаја сваки кадар симулације (око 200 бајтова са оквиром, 30-60 у секунди), блок кретања око 10 Hz (око 240 бајтова), блок стања једном у секунди; zstd смањује дупле вредности неколико пута

## Проверено {#verified}

декодирање порука проверено на баферима направљеним по распоредима из SimConnect.h; жива SimConnect веза није проверена

## Извор {#source}

[heat3d_watch/adapters/msfs.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/msfs.py)

<!-- Generated from the adapter by tools/gen_game_pages.py; change the adapter and run it again rather than editing this page. -->
