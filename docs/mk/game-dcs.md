---
title: "DCS World (податоци во живо)"
nav_order: 10
lang: "mk"
source: game-dcs.md
source_hash: "87cba160674e"
nav_exclude: true
search_exclude: true
---
# DCS World (податоци во живо) {#dcs-world-live-data}

Додека играте DCS World, watcher-от ги зачувува податоците што самата игра ги испраќа, за подоцна да можете да ги погледнете на мапа во прегледувачот 3DHeat.

*Технички детали: адаптер `dcs`, вид [`telemetry`](sources-and-rules.md); работи додека работи `DCS.exe` и бара нови податоци на секои 0,1 s.*

## Што се снима {#what-is-recorded}

- сопствена позиција на 10 Hz како метри исток/горе/север од почетокот на театарот (од географска ширина/должина/висина); lat/lon/alt и сопствените светски метри на DCS (dcs_x север, dcs_y горе, dcs_z исток) како колони
- положба на леталото, indicated и true брзина на воздух, Mach, вертикална брзина, агол на напад и странично лизгање, магнетна насока, AGL и висина по радар, g на три оски, брзина и стапки на ротација, во воздух, позиција и вектор напред на камерата, тип на летало
- полетувања и слетувања со аеродромот; падови, катапултирања, смрти на пилотот
- убиства и соборувања со двата типа единици и оружјето; други настани на играта како што се дадени
- животи по мисија (spawn ... session_end), убиства, смрти, растојание, највисока висина, највисок g
- секоја линија што ја праќа куката (hook) се чува целосна во heat.raw.parquet, со еднаш во секунда испишување на извозните табели на леталото (мотори, стајни трап и закрилца, товар, противмерки, рута, навигација) и секој друг callback (пауза, разговор, влегување на играчи, вчитување на мисија)

## Од каде доаѓа {#where-it-comes-from}

куката на watcher-от %USERPROFILE%\Saved Games\DCS\*\Scripts\Hooks\heat3d-watch.lua, UDP-линии до 127.0.0.1:41993

## Како да се вклучи {#how-to-switch-it-on}

python -m heat3d_watch setup dcs --apply (додава Scripts\Hooks\heat3d-watch.lua), потоа рестартирајте го DCS

Напишете ја командата во терминал отворен во папката на watcher-от (видете [Пред да започнете](before-you-start.md)). Ако не успее, последната линија кажува зошто; [Инсталирање и пуштање](installing-and-running.md) ги опфаќа вообичаените причини.

`python -m heat3d_watch setup dcs` ги наведува датотеките што би ги променила; `python -m heat3d_watch setup dcs --apply` ги менува, чувајќи го оригиналот како `<file>.heat3d-backup` (видете [Команди](commands.md#setup)). Печати `dcs: changed: ...` за секоја промена, или `dcs: nothing to change` кога веќе е вклучено.

## Како работи {#how-it-works}

DCS World: мала скрипта-кука на самиот watcher, што праќа UDP-линии до 127.0.0.1:41993.

DCS при стартување извршува Lua-датотеки од `Saved Games\DCS*\Scripts\Hooks\`; куката може да
ги чита извозните функции (`Export.Lo*`) и да ги прима callback-овите на симулацијата
(`DCS.setUserCallbacks`: onSimulationStart/Frame/Stop, onGameEvent) - видете
`<DCS>\API\DCS_ControlAPI.html` и <https://wiki.hoggitworld.com/view/DCS_Export_Script>.
`setup` ја запишува таму `heat3d-watch.lua` (своја датотека: Export.lua и куките на други
алатки не се допираат), која праќа десет линии во секунда, уште една во
секунда, и по една за секој настан на играта или callback, никогаш не чекајќи одговор. Портата
е 41993, за куката на JoyPro (41992) и Tacview (42674) да продолжат да работат покрај
неа. Линиите (полињата поделени со „;“):

```text
hello;v=2                                       the hook was loaded
start;mission=..;map=..;me=<player id>;name=..;mp=0|1;file=..;server=0|1
mis;t=..;date.Day=..;start_time=..;weather...   the mission's date, start time and weather, flattened
p;t=<model s>;x=;y=;z=;lat=;lon=;alt=;hdg=;pitch=;bank=;ias=;agl=;g=;type=;tas=;mach=;vv=;aoa=;aos=;
  mhdg=;ralt=;gx=;gz=;vx=;vy=;vz=;wx=;wy=;wz=;air=;cx=;cy=;cz=;cfx=;cfy=;cfz=
d;t=..;self.Name=..;eng.RPM.left=..;mech.gear.value=..;pay.Stations.1.count=..;...   once a second
ev;t=..;name=<onGameEvent name>;args=a|b|c      every onGameEvent
cb;t=..;name=<callback>;args=a|b                every other callback (pause, chat, players, loading)
noexport;t=..                                   the server forbids ownship export
stop;t=..                                       the mission ended
```

`p` е LoGetSelfData: Position x/y/z - сопствените светски метри на DCS, x север, y горе,
z исток - плус LatLongAlt (степени, m), Heading/Pitch/Bank (радијани), со
LoGetIndicatedAirSpeed (m/s), LoGetAltitudeAboveGroundLevel (m) и
LoGetAccelerationUnits() x/y/z (g); и, како што ги документира `Scripts\Export.lua`,
LoGetTrueAirSpeed (m/s), LoGetMachNumber, LoGetVerticalVelocity (m/s),
LoGetAngleOfAttack и LoGetAngleOfSideSlip (rad), LoGetMagneticYaw (rad),
LoGetRadarAltimeter (m), LoGetVectorVelocity (светски m/s), LoGetAngularVelocity
(rad/s), LoGetInAir, и точката и векторот напред од LoGetCameraPosition (светски
метри). `d` е еднаш во секунда испишување на цели табели, спрешани во клучеви со точки:
LoGetSelfData (земја, коалиција, имиња на единица и група, нивоа на тип, знамиња),
LoGetEngineInfo, LoGetMechInfo, LoGetPayloadInfo, LoGetSnares, LoGetWingInfo,
LoGetVectorWindVelocity, LoGetFMData, LoGetNavigationInfo, LoGetRoute,
LoGetMCPState, LoGetControlPanel_HSI, LoGetRadioBeaconsStatus и неколку
броеви (пауза, забрзување на времето, седиште, притисок, отстапувања). Watcher-от
ја чува секоја линија целосна во суровата придружна датотека; `p` станува и редови.

Позициите одат во истата рамна мапа како кај другите симулатори на летање (`Tangent`: x
исток, y висина над морето, z север, метри) од LatLongAlt, околу
фиксниот почеток на театарот (`THEATRES`, од `map` на линијата start), па секоја
мисија на еден театар дели една мапа, и таква под која прегледувачот може да го постави
вистинскиот свет. Театар што не е во табелата ги зема географската ширина и
должина на првото мерење заокружени на цели степени. Сопствените x/y/z на DCS се чуваат како `dcs_x`,
`dcs_y`, `dcs_z`; мерење без LatLongAlt не може да се постави и само се
брои (`fixes_without_latlon`). Почетокот е `geo` на сесијата, во
meta.json и во подножјето на табелата.

Аргументите на onGameEvent, како што ги дава DCS_ControlAPI:
takeoff/landing (playerID, unit_missionID, airdromeName),
crash/eject/pilot_death (playerID, unit_missionID), kill (killerPlayerID,
killerUnitType, killerSide, victimPlayerID, victimUnitType, victimSide,
weaponName), self_kill (playerID), change_slot (playerID, slotID, prevSide),
mission_end (winner, msg).

Мултиплеер серверот може да го забрани извозот на сопственото летало (LoIsOwnshipExportAllowed е
false); тогаш нема позиции, само настани, а сесијата го кажува тоа.

## Позиции и оски {#positions-and-axes}

| | |
|---|---|
| Снимени позиции | да |
| Горна оска | `y` |
| Единици | метри (исток, висина, север од почетокот на театарот) |
| Огледално за прегледувачот | `z` |
| Скала на единици (`scale`: прегледувачот ги множи позициите со неа) | 1 |

Овие одат во `meta.json` на секоја сесија (`axes`) и, кога сесијата има позиции, во подножјето на `heat.parquet`, па прегледувачот 3DHeat сам ги врти и скалира редовите - видете [Податоците](the-data.md).

## Мултиплеер {#multiplayer}

- Означено како играно онлајн (`multiplayer`): **да**. `games --markdown` го прикажува ова како „allowed (reads only what the game publishes)“.
- Вид `telemetry`: чита само она што играта или платформата го дава (UDP-порта или споделена меморија што ја објавува играта), па снима и во онлајн игра и офлајн; знамето одлучува само дали меморијата смее некогаш да се чита.
- Меморија: овој адаптер **никогаш** не ја чита. Само `memory` адаптерите читаат меморија, и никогаш за игра означена како играна онлајн - видете [Извори и правила](sources-and-rules.md).

## Снимена статистика {#statistics-recorded}

Клучеви на статистика што кодот на овој адаптер ги поставува по име (`stats` на секоја сесија во `meta.json` и табелата `stats` во `watcher.sqlite`):

`airborne_time`, `bad_packets`, `crashes`, `deaths`, `distance_km`, `ejections`, `export_blocked`, `fixes_without_latlon`, `flight_time`, `kills`, `max_altitude_m`, `max_g`, `shot_down`, `{event}s`

Клуч во загради { } се дополнува при извршување (`score.{team}` е еден клуч по тим). Клучевите што кодот ги зема од табела со полињата на играта или од сопствените имиња на статистика на играта не се во овој список; „Што се снима“ погоре ги именува.

## Комплетност {#completeness}

Watcher-от го следи [правилото за конвертори](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md) на 3DHeat: она што го содржи изворот се чита или се чува, никогаш не се отфрла. Покрај редовите, секој пакет, страница, линија или одговор што адаптерот ќе го добие се чува целосен во `heat.raw.parquet` на сесијата (колони `time`, `ms`, `type`, `used`, `payload`, `text`, потоа секое поле зачувано по име; `used` означува што станало и ред), а `selfCheck.completeness` во `meta.json` го брои секој `type` - `lost` е 0.

**Прочитано**

- `p` (10 Hz): позиција, LatLongAlt, положба, IAS, AGL, g (x/y/z), тип на летало, и TAS, Mach, вертикална брзина, AoA, странично лизгање, магнетна насока, висина по радар, светска брзина, стапки на ротација, во воздух и точка/вектор напред на камерата од куката 2 - сѐ како колони на редовите (единици како што ги дава Export.lua)
- `start`: мисија, театар, сопствен id и име на играч, мултиплеер, датотека на мисијата, сервер; `mis`: датумот и времето на почеток на мисијата во meta.json
- `ev`: секој onGameEvent како ред (takeoff, landing, crash, eject, pilot_death, kill, self_kill, change_slot, connect, disconnect, friendly_fire, mission_end, секое друго име како што е дадено)
- `noexport` и `stop` како редови и во meta.json

**Чувано сурово**

- секоја линија што ја праќа куката, целосна, како `text` под својот вид: `hello`, `start`, `mis`, `p`, `d`, `ev`, `cb`, `noexport`, `stop`; линија од кој било друг вид под `unknown`
- `d` (1 Hz, само сурово): LoGetSelfData целосен (земја, коалиција, име на единица и група, нивоа на тип, знамиња), LoGetEngineInfo, LoGetMechInfo, LoGetPayloadInfo, LoGetSnares, LoGetWingInfo, вектор на ветер, LoGetFMData, LoGetNavigationInfo, LoGetRoute, LoGetMCPState, HSI, радио-светилници, пауза, забрзување на времето, седиште, притисок, отстапувања - спрешани во клучеви со точки
- `mis`: табелата со времето на мисијата, спрешана; `cb`: onSimulationPause/Resume, onMissionLoad\*, onNet\*, onPlayerConnect/Disconnect/Start/Stop/ChangeSlot, onChatMessage, onTriggerMessage, onRadioMessage, onRadioCommand, onShowMessage со нивните аргументи

**Недостапно**

- други единици (LoGetWorldObjects, LoGetObjectById) и податоци од сензори (LoGetTargetInformation, LoGetLockedTargetInformation, LoGetTWSInfo, LoGetWingTargets, LoGetSightingSystemInfo): не се бараат - секој објект од мисија на 10 Hz е скап во самиот фрејм на DCS, а серверот ги ограничува (allow_object_export, allow_sensor_export); Tacview ги снима
- целата табела на мисијата (DCS.getCurrentMission ја држи секоја единица и активатор, мегабајти): се праќаат само нејзиниот датум, времето на почеток, времето, sortie, театарот и верзијата
- callback-овите onPlayerTry\*: тие му одговараат на DCS (дозволи или одбиј), па куката ги остава на мира
- адресите и UCID-ите на другите играчи: net.get_player_info ги дава само на сервер, и не се за чување од играчот
- записи на табела над 800 клучеви или подлабоко од 6 нивоа во една `d` линија се сечат, за една линија да остане еден датаграм

**Големина**: околу 20 MB на час од `p` линии (10 во секунда, околу 500 бајти секоја со својот фрејм) и 15-40 MB од `d` испишувања (едно во секунда, 4-10 KB зависно од товарот и рутата на леталото), пред zstd; повторените клучеви се компресираат десетина пати

## Проверено {#verified}

форматот на линиите тестиран со синтетички датаграми; Lua-куката не е тестирана во DCS (напишана според API-то на куки/извоз на DCS и списокот на функции Lo\* во Scripts\Export.lua, не пуштана)

## Извор {#source}

[heat3d_watch/adapters/dcs.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/dcs.py)

<!-- Generated from the adapter by tools/gen_game_pages.py; change the adapter and run it again rather than editing this page. -->
