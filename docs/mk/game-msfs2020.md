---
title: "Microsoft Flight Simulator 2020 (податоци во живо)"
nav_order: 31
lang: "mk"
source: game-msfs2020.md
source_hash: "9b9e8389114b"
nav_exclude: true
search_exclude: true
---
# Microsoft Flight Simulator 2020 (податоци во живо) {#microsoft-flight-simulator-2020-live-data}

Додека играте Microsoft Flight Simulator 2020, watcher-от ги зачувува податоците што самата игра ги испраќа, за подоцна да можете да ги погледнете на мапа во прегледувачот 3DHeat.

*Технички детали: адаптер `msfs2020`, вид [`telemetry`](sources-and-rules.md); работи додека работи `FlightSimulator.exe` и бара нови податоци на секои 0,1 s.*

## Што се снима {#what-is-recorded}

- позицијата на сопственото летало во секој фрејм на симулацијата, земена на 10 Hz (географска ширина/должина/висина како метри исток/горе/север од првото мерење; lat/lon/alt се чуваат како колони)
- положба, indicated брзина на воздух, брзина над земја, AGL, g, на земја; true брзина на воздух, Mach, вертикална брзина, AoA, странично лизгање, магнетна насока, брзини на телото, забрзувања и стапки на ротација на околу 10 Hz
- тежина, гориво, закрилца, стајни трап, спојлери, паркинг-сопирачка, автопилот, гас, RPM, време, брзина на симулацијата, час и состојба на камерата еднаш во секунда; насловот на леталото и ATC тип, модел и id
- полетувања, слетувања, падови, започнати и запрени летови (session_start/session_end)
- време на лет, време во воздух, растојание, највисока висина, највисок g, слетувања
- секоја SimConnect порака се чува целосна во heat.raw.parquet

## Од каде доаѓа {#where-it-comes-from}

SimConnect преку SimConnect.dll на самиот играч (папката на симулаторот, или %MSFS_SDK%\SimConnect SDK\lib)

## Како да се вклучи {#how-to-switch-it-on}

ништо; SimConnect.dll доаѓа со MSFS 2020 (или со MSFS SDK)

## Како работи {#how-it-works}

Microsoft Flight Simulator 2020 и 2024: SimConnect, преку SimConnect.dll на самиот играч.

SimConnect е објавениот клиентски API на симулаторот (SDK-документација:
<https://docs.flightsimulator.com/html/Programming_Tools/SimConnect/SimConnect_SDK.htm>,
<https://docs.flightsimulator.com/msfs2024/html/6_Programming_APIs/SimConnect/SimConnect_SDK.htm>).
Watcher-от не ја испорачува DLL-датотеката: ја вчитува онаа што дошла со симулаторот или
со неговиот SDK - MSFS 2020 го става `SimConnect.dll` во својата папка на инсталација; MSFS 2024 на
Steam испорачува само свој внатрешен, па играчите на 2024 го инсталираат MSFS 2024 SDK
(`<SDK>\SimConnect SDK\lib\SimConnect.dll`; симулаторот 2024 прифаќа и клиенти од 2020).

Повиците, од SimConnect.h, сите враќаат HRESULT (0 = S_OK):

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

Секоја порака започнува со SIMCONNECT_RECV {DWORD dwSize, dwVersion, dwID}
(#pragma pack 1). Оние што се читаат тука:

```text
1  EXCEPTION       dwException, dwSendID, dwIndex
2  OPEN            szApplicationName[256], then version DWORDs
3  QUIT            the sim is closing
4  EVENT           uGroupID, uEventID, dwData
6  EVENT_FILENAME  EVENT + szFileName[260], dwFlags        (FlightLoaded)
8  SIMOBJECT_DATA  dwRequestID, dwObjectID, dwDefineID, dwFlags, dwentrynumber,
                   dwoutof, dwDefineCount, then the values (FLOAT64 each here)
```

Променливи на симулацијата (единиците се бараат така што конверзија не треба): PLANE
LATITUDE/LONGITUDE (степени), PLANE ALTITUDE (метри, над морето), PLANE
ALT ABOVE GROUND (метри), PLANE PITCH/BANK DEGREES и PLANE HEADING DEGREES
TRUE (степени; сопствените знаци на SimConnect - носот нагоре е негативен pitch), AIRSPEED
INDICATED и GROUND VELOCITY (јазли), G FORCE (gforce), SIM ON GROUND (bool).
Системски настани: SimStart, SimStop, Crashed, FlightLoaded, AircraftLoaded,
Pause, CrashReset, PositionChanged, FlightSaved, Sim.

Уште три дефиниции на податоци бараат остатокот од летот (`MOTION_VARS`,
секој шести фрејм на симулацијата), побавната состојба на леталото (`STATE_VARS`, еднаш во
секунда) и неговите имиња (`NAME_VARS`, низи од 256 бајти, кога ќе се променат); секоја
е своја дефиниција, па променлива што една верзија на симулаторот не ја знае чини
само тој блок. Секоја порака се чува целосна во суровата придружна датотека на сесијата.

Позициите одат во истата рамна мапа како кај X-Plane (x исток, y висина, z север
во метри од првото мерење на сеансата); тоа мерење е `geo` на сесијата, во
meta.json и во подножјето на табелата.

Истиот модул служи и за: [Microsoft Flight Simulator 2024 (податоци во живо)](game-msfs2024.md).

## Позиции и оски {#positions-and-axes}

| | |
|---|---|
| Снимени позиции | да |
| Горна оска | `y` |
| Единици | метри (исток, висина, север од првото мерење) |
| Огледално за прегледувачот | `z` |
| Скала на единици (`scale`: прегледувачот ги множи позициите со неа) | 1 |

Овие одат во `meta.json` на секоја сесија (`axes`) и, кога сесијата има позиции, во подножјето на `heat.parquet`, па прегледувачот 3DHeat сам ги врти и скалира редовите - видете [Податоците](the-data.md).

## Мултиплеер {#multiplayer}

- Означено како играно онлајн (`multiplayer`): **да**. `games --markdown` го прикажува ова како „allowed (reads only what the game publishes)“.
- Вид `telemetry`: чита само она што играта или платформата го дава (UDP-порта или споделена меморија што ја објавува играта), па снима и во онлајн игра и офлајн; знамето одлучува само дали меморијата смее некогаш да се чита.
- Меморија: овој адаптер **никогаш** не ја чита. Само `memory` адаптерите читаат меморија, и никогаш за игра означена како играна онлајн - видете [Извори и правила](sources-and-rules.md).

## Снимена статистика {#statistics-recorded}

Клучеви на статистика што кодот на овој адаптер ги поставува по име (`stats` на секоја сесија во `meta.json` и табелата `stats` во `watcher.sqlite`):

`airborne_time`, `bad_packets`, `crashes`, `distance_km`, `flight_time`, `max_altitude_m`, `max_g`, `{event}s`

Клуч во загради { } се дополнува при извршување (`score.{team}` е еден клуч по тим). Клучевите што кодот ги зема од табела со полињата на играта или од сопствените имиња на статистика на играта не се во овој список; „Што се снима“ погоре ги именува.

## Комплетност {#completeness}

Watcher-от го следи [правилото за конвертори](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md) на 3DHeat: она што го содржи изворот се чита или се чува, никогаш не се отфрла. Покрај редовите, секој пакет, страница, линија или одговор што адаптерот ќе го добие се чува целосен во `heat.raw.parquet` на сесијата (колони `time`, `ms`, `type`, `used`, `payload`, `text`, потоа секое поле зачувано по име; `used` означува што станало и ред), а `selfCheck.completeness` во `meta.json` го брои секој `type` - `lost` е 0.

**Прочитано**

- SIMOBJECT_DATA од дефиницијата за позиција (секој фрејм на симулацијата): географска ширина, должина, висина, AGL, pitch, bank, true насока, IAS, брзина над земја, g, на земја - последниот фрејм од прашањето како ред, секој фрејм за допири на земја и полетувања
- SIMOBJECT_DATA од дефиницијата за движење (околу 10 Hz: TAS, Mach, вертикална брзина, AoA, странично лизгање, магнетна насока, брзина на телото, забрзување и стапка на ротација на три оски) и од дефиницијата за состојба (1 Hz: тежини, гориво, закрилца, стајни трап, спојлери, паркинг-сопирачка, автопилот, мотори, гас и RPM, надворешна температура, ветер, притисок на нивото на морето, брзина на симулацијата, zulu и локално време, состојба на камерата) врз редовите како последно примени
- SIMOBJECT_DATA од дефиницијата за имиња (наслов, ATC тип, модел и id) во meta.json и `aircraft` на редовите; OPEN (апликација и верзија) во meta.json
- EVENT и EVENT_FILENAME: SimStart, SimStop, Crashed, FlightLoaded (датотеката на летот) и AircraftLoaded (датотеката на леталото) како летови, падови и meta.json
- QUIT ја завршува сесијата

**Чувано сурово**

- секоја порака што SimConnect му ја дава на watcher-от, целосна како `payload`, под името на својот SIMCONNECT_RECV_ID: `SIMOBJECT_DATA`, `EVENT`, `EVENT_FILENAME`, `OPEN`, `QUIT`, `EXCEPTION` (променлива или настан што симулаторот не ги прифатил, со send id и индекс), секој друг id по своето име или `RECV_<id>`
- она што го држи само суровата придружна датотека: позицијата од секој фрејм на симулацијата меѓу редовите, настаните Pause, Sim, CrashReset, PositionChanged и FlightSaved, дефиниција што симулаторот ја скратил (една променлива што не ја знаел: блокот тогаш не се чита по име); `requests` во meta.json ги наведува променливите и единиците на секоја дефиниција по ред, па товарите (payload) се читаат и без овој модул

**Недостапно**

- други летала (AI сообраќај, други играчи онлајн): SimConnect_RequestDataOnSimObjectType би ги испрашувал сите летала во радиус - повеќе оптоварување за симулаторот, и летови на други играчи
- блокот за движење во секој фрејм на симулацијата: се бара на секој шести фрејм (околу 10 Hz, стапката на редовите), што ја држи суровата струја на околу петтина од големината; блокот за позиција останува во секој фрејм
- илјадниците други променливи на симулацијата (радија, светла, мерачите на секој мотор, дефекти): дефиницијата го држи она што го бара; листите бараат летот, состојбата на леталото и времето на симулаторот
- метеоролошки набљудувања, објекти (аеродроми, VOR), клиентски податоци на додатоци: посебни барања, не се прават

**Големина**: околу 30-55 MB на час пред zstd: блокот за позиција во секој фрејм на симулацијата (околу 200 бајти со својот фрејм, 30-60 во секунда), блокот за движење на околу 10 Hz (околу 240 бајти), блокот за состојба еднаш во секунда; zstd ги смалува doubles неколкукратно

## Проверено {#verified}

декодирањето на пораките тестирано на бафери изградени од распоредите на SimConnect.h; живата SimConnect врска не е тестирана

## Извор {#source}

[heat3d_watch/adapters/msfs.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/msfs.py)

<!-- Generated from the adapter by tools/gen_game_pages.py; change the adapter and run it again rather than editing this page. -->
