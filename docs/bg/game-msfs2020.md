---
title: "Microsoft Flight Simulator 2020 (данни на живо)"
nav_order: 31
lang: "bg"
source: game-msfs2020.md
source_hash: "9b9e8389114b"
nav_exclude: true
search_exclude: true
---
# Microsoft Flight Simulator 2020 (данни на живо) {#microsoft-flight-simulator-2020-live-data}

Докато играете Microsoft Flight Simulator 2020, watcher-ът записва данните, които самата игра изпраща навън, за да можете по-късно да ги разгледате на карта в 3DHeat визуализатора.

*Технически подробности: адаптер `msfs2020`, вид [`telemetry`](sources-and-rules.md); работи, докато `FlightSimulator.exe` е стартиран, и търси нови данни на всеки 0.1 s.*

## Какво се записва {#what-is-recorded}

- позицията на собствения самолет на всеки кадър на симулатора, взета на 10 Hz (географска ширина/дължина/височина като метри на изток/нагоре/на север от първата фиксирана точка; ширината, дължината и височината се пазят като колони)
- ориентация, показваща скорост, земна скорост, AGL, g, на земята; истинска скорост, Мах, вертикална скорост, AoA, плъзгане, магнитен курс, скорости по осите на тялото, ускорения и ъглови скорости на около 10 Hz
- тегло, гориво, клапи, шаси, спойлери, стояночна спирачка, автопилот, газ, оборота, времето, ускорението на симулатора, часа и състоянието на камерата веднъж в секунда; заглавието на самолета и типът за ATC, моделът и идентификаторът му
- излитания, кацания, катастрофи, полети, започнати и спрени (session_start/session_end)
- време в полет, време във въздуха, разстояние, най-голяма височина, най-голямо g, кацания
- всяко SimConnect съобщение, цяло, в `heat.raw.parquet`

## Откъде идва {#where-it-comes-from}

SimConnect през собствения SimConnect.dll на играча (папката на симулатора или %MSFS_SDK%\SimConnect SDK\lib)

## Как се включва {#how-to-switch-it-on}

нищо; SimConnect.dll идва с MSFS 2020 (или с SDK на MSFS)

## Как работи {#how-it-works}

Microsoft Flight Simulator 2020 и 2024: SimConnect, през собствения SimConnect.dll на играча.

SimConnect е публикуваният клиентски API на симулатора (SDK документация:
<https://docs.flightsimulator.com/html/Programming_Tools/SimConnect/SimConnect_SDK.htm>,
<https://docs.flightsimulator.com/msfs2024/html/6_Programming_APIs/SimConnect/SimConnect_SDK.htm>).
Watcher-ът не носи DLL-а: зарежда този, който идва със симулатора или с неговия SDK - MSFS 2020 слага `SimConnect.dll` в папката си за инсталация; MSFS 2024 в Steam носи само вътрешния си, затова играчите на 2024 инсталират SDK-то на MSFS 2024 (`<SDK>\SimConnect SDK\lib\SimConnect.dll`; симулаторът от 2024 приема и клиенти от 2020).

Извикванията, от SimConnect.h, всички връщат HRESULT (0 = S_OK):

```text
SimConnect_Open(HANDLE*, LPCSTR name, HWND, DWORD, HANDLE, DWORD config)
SimConnect_AddToDataDefinition(HANDLE, DWORD define, LPCSTR var, LPCSTR units,
                               SIMCONNECT_DATATYPE (FLOAT64 = 4), float epsilon, DWORD datum)
SimConnect_RequestDataOnSimObject(HANDLE, DWORD request, DWORD define, DWORD object (0 = user),
                                  SIMCONNECT_PERIOD (SIM_FRAME = 3), DWORD flags, DWORD origin,
                                  DWORD interval, DWORD limit)
SimConnect_SubscribeToSystemEvent(HANDLE, DWORD event, LPCSTR name)
SimConnect_GetNextDispatch(HANDLE, SIMCONNECT_RECV**, DWORD*)   E_FAIL when nothing waits
SimConnect_Close(HANDLE)
```

Всяко съобщение започва със SIMCONNECT_RECV {DWORD dwSize, dwVersion, dwID}
(#pragma pack 1). Тези, които се четат тук:

```text
1  EXCEPTION       dwException, dwSendID, dwIndex
2  OPEN            szApplicationName[256], then version DWORDs
3  QUIT            the sim is closing
4  EVENT           uGroupID, uEventID, dwData
6  EVENT_FILENAME  EVENT + szFileName[260], dwFlags        (FlightLoaded)
8  SIMOBJECT_DATA  dwRequestID, dwObjectID, dwDefineID, dwFlags, dwentrynumber,
                   dwoutof, dwDefineCount, then the values (FLOAT64 each here)
```

Симулационни променливи (поискани с мерните единици, за да не е нужно преобразуване): PLANE
LATITUDE/LONGITUDE (градуси), PLANE ALTITUDE (метри, над морското равнище), PLANE
ALT ABOVE GROUND (метри), PLANE PITCH/BANK DEGREES и PLANE HEADING DEGREES
TRUE (градуси; собствените знаци на SimConnect - носът нагоре е отрицателен pitch), AIRSPEED
INDICATED и GROUND VELOCITY (възли), G FORCE (gforce), SIM ON GROUND (bool).
Системни събития: SimStart, SimStop, Crashed, FlightLoaded, AircraftLoaded,
Pause, CrashReset, PositionChanged, FlightSaved, Sim.

Още три дефиниции на данни искат останалата част от полета (`MOTION_VARS`,
на всеки шести кадър на симулатора), по-бавното състояние на самолета (`STATE_VARS`, веднъж в
секунда) и имената му (`NAME_VARS`, низове от 256 байта, когато се променят); всяка е
собствена дефиниция, така че променлива, която една версия на симулатора не знае, струва
само своя блок. Всяко съобщение се пази цяло в суровия страничен файл на сесията.

Позициите влизат в същата плоска карта като тази на X-Plane (x на изток, y височина, z на север
в метри от първата фиксирана точка на сесията); тази точка е `geo` на сесията, в meta.json и
в края на таблицата.

Същият модул обслужва и: [Microsoft Flight Simulator 2024 (данни на живо)](game-msfs2024.md).

## Позиции и оси {#positions-and-axes}

| | |
|---|---|
| Записани позиции | да |
| Вертикална ос | `y` |
| Единици | метри (изток, височина, север от първата фиксирана точка) |
| Огледално за визуализатора | `z` |
| Мащаб на единицата (`scale`: визуализаторът умножава позициите по него) | 1 |

Те отиват в `meta.json` (`axes`) на всяка сесия и, когато сесията има позиции, в долния колонтитул на `heat.parquet`, така че 3DHeat визуализаторът сам завърта и мащабира редовете - вижте [Данните](the-data.md).

## Мултиплейър {#multiplayer}

- Маркиран като игран онлайн (`multiplayer`): **да**. `games --markdown` показва това като "разрешено (чете само това, което играта публикува)".
- Вид `telemetry`: чете само това, което играта или платформата предава (UDP порт или споделена памет, които играта публикува), затова записва и в онлайн игра, както и офлайн; флагът решава само дали паметта може изобщо да се чете.
- Памет: **никога** не се чете от този адаптер. Само адаптерите от вид `memory` четат памет, и никога за игра, маркирана като играна онлайн - вижте [Източници и правила](sources-and-rules.md).

## Записана статистика {#statistics-recorded}

Ключове на статистиката, които кодът на този адаптер задава по име (`stats` на всяка сесия в `meta.json` и таблицата `stats` в `watcher.sqlite`):

`airborne_time`, `bad_packets`, `crashes`, `distance_km`, `flight_time`, `max_altitude_m`, `max_g`, `{event}s`

Ключ във фигурни скоби се допълва по време на работа (`score.{team}` е по един ключ за всеки отбор). Ключовете, които кодът взема от таблица с полетата на играта или от собствените имена на статистики на играта, не са в този списък; "Какво се записва" по-горе ги изброява.

## Пълнота {#completeness}

Watcher-ът следва [правилото за конвертори](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md) на 3DHeat: това, което източникът съдържа, се чете или се пази, никога не се изхвърля. Освен редовете, всеки пакет, страница, ред или отговор, който адаптерът получава, се пази цял в `heat.raw.parquet` на сесията (колони `time`, `ms`, `type`, `used`, `payload`, `text` и всяко поле, запазено по име; `used` отбелязва какво е станало и ред), а `selfCheck.completeness` в `meta.json` брои всеки `type` - `lost` е 0.

**Прочетено**

- SIMOBJECT_DATA на дефиницията на позицията (всеки кадър на симулатора): географска ширина, дължина, височина, AGL, pitch, bank, истинския курс, IAS, земната скорост, g, на земята - последният кадър от опроса като ред, всеки кадър за приземявания и излитания
- SIMOBJECT_DATA на дефиницията на движението (около 10 Hz: TAS, Mach, вертикална скорост, AoA, плъзгане, магнитен курс, скорост по осите на тялото, ускорение и ъглова скорост по три оси) и на дефиницията на състоянието (1 Hz: тегла, гориво, клапи, шаси, спойлери, стояночна спирачка, автопилот, двигатели, газ и оборота, външна температура, вятър, налягане на морското равнище, ускорение на симулатора, zulu и местно време, състояние на камерата) - като редове, както са получени последно
- SIMOBJECT_DATA на дефиницията на имената (заглавие, тип за ATC, модел и идентификатор) в meta.json и в `aircraft` на редовете; OPEN (приложение и версия) в meta.json
- EVENT и EVENT_FILENAME: SimStart, SimStop, Crashed, FlightLoaded (файлът на полета) и AircraftLoaded (файлът на самолета) като полети, катастрофи и в meta.json
- QUIT прекратява сесията

**Пазено цяло**

- всяко съобщение, което SimConnect предава на watcher-а, цяло като `payload`, под името на идентификатора му SIMCONNECT_RECV: `SIMOBJECT_DATA`, `EVENT`, `EVENT_FILENAME`, `OPEN`, `QUIT`, `EXCEPTION` (променлива или събитие, които симулаторът не е приел, с идентификатора на изпращането и индекса), всеки друг идентификатор по името му или `RECV_<id>`
- какво държи само суровият страничен файл: позицията на всеки кадър на симулатора между редовете, събитията Pause, Sim, CrashReset, PositionChanged и FlightSaved, дефиниция, която симулаторът е прекъснал (една променлива, която не знае: блокът тогава не се чете по име); `requests` в meta.json изброява всяка дефиниция с променливите и мерните им единици по ред, така че данните се четат и без този модул

**Не е налично**

- други самолети (AI трафик, други играчи онлайн): SimConnect_RequestDataOnSimObjectType би опросил всеки самолет в радиус - повече натоварване на симулатора и полетите на други играчи
- блокът за движение на всеки кадър на симулатора: иска се на всеки шести кадър (около 10 Hz, скоростта на редовете), което държи суровия поток близо до една пета от размера; блокът за позицията остава на всеки кадър
- хилядите други симулационни променливи (радиа, светлини, всеки измервател на двигател, повреди): дефиницията съдържа само това, което иска; списъците искат полета, състоянието на самолета и времето на симулатора
- наблюдения на времето, обекти (летища, VOR), клиентски данни на добавки: отделни заявки, не се правят

**Размер**: около 30-55 MB на час преди zstd: блокът за позицията на всеки кадър на симулатора (около 200 байта с кадъра си, 30-60 в секунда), блокът за движението на около 10 Hz (около 240 байта), блокът за състоянието веднъж в секунда; zstd смалява дабълите няколко пъти

## Проверено {#verified}

декодирането на съобщенията проверено на буфери, изградени по оформленията от SimConnect.h; live връзката със SimConnect непроверена

## Източник {#source}

[heat3d_watch/adapters/msfs.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/msfs.py)

<!-- Generated from the adapter by tools/gen_game_pages.py; change the adapter and run it again rather than editing this page. -->
