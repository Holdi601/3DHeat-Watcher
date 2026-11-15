---
title: "DCS World (живи подаци)"
nav_order: 10
lang: "sr"
source: game-dcs.md
source_hash: "87cba160674e"
nav_exclude: true
search_exclude: true
---
# DCS World (живи подаци) {#dcs-world-live-data}

Док играте DCS World, посматрач чува податке које сама игра шаље, па то касније можете да погледате на мапи у 3DHeat приказивачу.

*Технички детаљи: адаптер `dcs`, врста [`telemetry`](sources-and-rules.md); ради док је `DCS.exe` покренут и тражи нове податке сваких 0,1 s.*

## Шта се снима {#what-is-recorded}

- сопствени положај 10 пута у секунди, у метрима источно/горе/северно од почетне тачке позоришта (из географске ширине/дужине/висине); lat/lon/alt и DCS-ови светски метри (dcs_x север, dcs_y горе, dcs_z исток) као колоне
- став, индициран и прави ваздушни брзина, Mach, вертикална брзина, напад и клизање, магнетни курс, висина над земљом и радарска висина, g у три осе, брзина и брзине ротације, у ваздуху, положај камере и вектор њеног правца, тип летелице
- полетања и слетања са аеродромом; судари, катапултирања, погибије пилота
- убиства и обарања са оба типа јединица и оружјем; други догађаји игре онако како су дати
- животи по мисији (spawn ... session_end), убиства, смрти, пређена дистанца, највећа висина, највећи g
- свака линија коју хук шаље, цела, у heat.raw.parquet, са дампом табела извоза летелице сваке секунде (мотори, стајни трап и закрилца, терет, мере против ометања, рута, навигација) и сваким другим callback-ом (пауза, ћаскање, улазак играча, учитавање мисије)

## Одакле долази {#where-it-comes-from}

хук посматрача %USERPROFILE%\Saved Games\DCS\*\Scripts\Hooks\heat3d-watch.lua, UDP линије на 127.0.0.1:41993

## Како се укључује {#how-to-switch-it-on}

python -m heat3d_watch setup dcs --apply (додаје Scripts\Hooks\heat3d-watch.lua), па поново покрените DCS

Команду укуцајте у терминалу отвореном у фасцикли посматрача (видите [Пре почетка](before-you-start.md)). Ако не успе, последњи ред каже зашто; [Инсталација и покретање](installing-and-running.md) описује уобичајене узроке.

`python -m heat3d_watch setup dcs` наводи датотеке које би променио; `python -m heat3d_watch setup dcs --apply` их мења и чува оригинал као `<file>.heat3d-backup` (видите [Команде](commands.md#setup)). За сваку промену исписује `dcs: changed: ...`, или `dcs: nothing to change` кад је већ укључено.

## Како ради {#how-it-works}

DCS World: мала скрипта хука посматрачевог власништва, која шаље UDP линије на 127.0.0.1:41993.

DCS при покретању учитава Lua датотеке из `Saved Games\DCS*\Scripts\Hooks\`; хук може да чита функције извоза (`Export.Lo*`) и да прима повратне позиве симулације (`DCS.setUserCallbacks`: onSimulationStart/Frame/Stop, onGameEvent) - видите `<DCS>\API\DCS_ControlAPI.html` и <https://wiki.hoggitworld.com/view/DCS_Export_Script>. `setup` тамо записује `heat3d-watch.lua` (сопствена датотека: Export.lua и хукови других алата се не дирају), која шаље десет линија у секунди, још једну сваке секунде, и по једну за сваки догађај игре или повратни позив, никад не чекајући одговор. Порт је 41993 да би JoyPro-ов хук (41992) и Tacview (42674) радили поред њега. Линије (поља раздвојена са ';'):

```text
hello;v=2                                       хук је учитан
start;mission=..;map=..;me=<player id>;name=..;mp=0|1;file=..;server=0|1
mis;t=..;date.Day=..;start_time=..;weather...   датум мисије, време почетка и време, спљоштено
p;t=<model s>;x=;y=;z=;lat=;lon=;alt=;hdg=;pitch=;bank=;ias=;agl=;g=;type=;tas=;mach=;vv=;aoa=;aos=;
  mhdg=;ralt=;gx=;gz=;vx=;vy=;vz=;wx=;wy=;wz=;air=;cx=;cy=;cz=;cfx=;cfy=;cfz=
d;t=..;self.Name=..;eng.RPM.left=..;mech.gear.value=..;pay.Stations.1.count=..;...   сваке секунде
ev;t=..;name=<onGameEvent name>;args=a|b|c      сваки onGameEvent
cb;t=..;name=<callback>;args=a|b                сваки други повратни позив (пауза, ћаскање, играчи, учитавање)
noexport;t=..                                   сервер забрањује извоз сопствене летелице
stop;t=..                                       мисија се завршила
```

`p` је LoGetSelfData: Position x/y/z - DCS-ови светски метри, x север, y горе, z исток - плус LatLongAlt (степени, m), Heading/Pitch/Bank (радијани), са LoGetIndicatedAirSpeed (m/s), LoGetAltitudeAboveGroundLevel (m) и LoGetAccelerationUnits() x/y/z (g); и, како их `Scripts\Export.lua` наводи, LoGetTrueAirSpeed (m/s), LoGetMachNumber, LoGetVerticalVelocity (m/s), LoGetAngleOfAttack и LoGetAngleOfSideSlip (rad), LoGetMagneticYaw (rad), LoGetRadarAltimeter (m), LoGetVectorVelocity (светски m/s), LoGetAngularVelocity (rad/s), LoGetInAir, и тачку и вектор правца LoGetCameraPosition-а (светски метри). `d` је дамп целих табела сваке секунде, спљоштен у тачкасте кључеве: LoGetSelfData (држава, коалиција, називи јединице и групе, нивои типа, заставице), LoGetEngineInfo, LoGetMechInfo, LoGetPayloadInfo, LoGetSnares, LoGetWingInfo, LoGetVectorWindVelocity, LoGetFMData, LoGetNavigationInfo, LoGetRoute, LoGetMCPState, LoGetControlPanel_HSI, LoGetRadioBeaconsStatus и неколико бројева (пауза, убрзање времена, седиште, притисак, одступања). Посматрач чува сваку линију целу у сировој пратећој датотеци; `p` постаје и редови.

Положаји иду у исту равну мапу као и остали летачки симулатори (`Tangent`: x исток, y висина изнад мора, z север, метри) из LatLongAlt, око фиксне почетне тачке позоришта (`THEATRES`, из `map` линије `start`), па сваки мисија на једном позоришту дели једну мапу, коју приказивач може да прекрије правим светом. Позориште које није у табели узима географску ширину и дужину прве тачке заокружене на цео степен. DCS-ови x/y/z чувају се као `dcs_x`, `dcs_y`, `dcs_z`; тачка без LatLongAlt не може да се смести и само се броји (`fixes_without_latlon`). Почетна тачка је `geo` сесије, у meta.json-у и подножју табеле.

Аргументи onGameEvent-а, онако како их даје DCS_ControlAPI: takeoff/landing (playerID, unit_missionID, airdromeName), crash/eject/pilot_death (playerID, unit_missionID), kill (killerPlayerID, killerUnitType, killerSide, victimPlayerID, victimUnitType, victimSide, weaponName), self_kill (playerID), change_slot (playerID, slotID, prevSide), mission_end (winner, msg).

Сервер за више играча може да забрани извоз сопствене летелице (LoIsOwnshipExportAllowed је false); тада нема положаја, само догађаји, и сесија то каже.

## Положаји и осе {#positions-and-axes}

| | |
|---|---|
| Положаји се бележе | да |
| Оса нагоре | `y` |
| Јединице | метри (исток, висина, север од почетне тачке позоришта) |
| Огледално за приказивач | `z` |
| Размера јединице (`scale`: приказивач множи положаје њом) | 1 |

Ово иде у `meta.json` сваке сесије (`axes`) и, кад сесија има положаје, у подножје `heat.parquet`-а, па 3DHeat приказивач сам окреће и скалира редове - видите [Подаци](the-data.md).

## Више играча {#multiplayer}

- Означено као игра на мрежи (`multiplayer`): **да**. `games --markdown` ово приказује као "allowed (reads only what the game publishes)".
- Врста `telemetry`: чита само оно што игра или платформа даје (UDP порт или дељена меморија коју игра објављује), па снима и у мрежној игри и ван ње; ознака одлучује само да ли се меморија икад сме читати.
- Меморија: **никад** се не чита овим адаптером. Само адаптери `memory` читају меморију, и никад за игру означену као игру на мрежи - видите [Извори и правила](sources-and-rules.md).

## Снимљена статистика {#statistics-recorded}

Кључеви статистике које код овог адаптера поставља по имену (`stats` сваке сесије у `meta.json` и табела `stats` у `watcher.sqlite`):

`airborne_time`, `bad_packets`, `crashes`, `deaths`, `distance_km`, `ejections`, `export_blocked`, `fixes_without_latlon`, `flight_time`, `kills`, `max_altitude_m`, `max_g`, `shot_down`, `{event}s`

Кључ у витичастим заградама се допуњује за време рада (`score.{team}` је један кључ по тиму). Кључеви које код узима из табеле поља игре или из назива статистике саме игре нису у овом списку; "Шта се снима" горе их наводи.

## Потпуност {#completeness}

Посматрач следи [правило конвертера](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md) 3DHeat-а: оно што извор садржи се чита или чува, никад не одбацује. Осим редова, сваки пакет, страница, линија или одговор који адаптер прими чува се цео у `heat.raw.parquet` сесије (колоне `time`, `ms`, `type`, `used`, `payload`, `text`, па свако поље које се чува по имену; `used` означава оно што је постало и редови), а `selfCheck.completeness` у `meta.json`-у броји сваки `type` - `lost` је 0.

**Чита се**

- `p` (10 Hz): положај, LatLongAlt, став, IAS, AGL, g (x/y/z), тип летелице, и TAS, Mach, вертикалну брзину, напад, клизање, магнетни курс, радарску висину, светску брзину, брзине ротације, у ваздуху и тачку и правац камере из хука 2 - све као колоне редова (јединице онако како их даје Export.lua)
- `start`: мисија, позориште, сопствени ид и име играча, режим за више играча, датотека мисије, сервер; `mis`: датум и време почетка мисије у meta.json
- `ev`: сваки onGameEvent као ред (takeoff, landing, crash, eject, pilot_death, kill, self_kill, change_slot, connect, disconnect, friendly_fire, mission_end, сваки други назив онако како је дат)
- `noexport` и `stop` као редови и у meta.json

**Чува се сирово**

- свака линија коју хук шаље, цела, као `text` под својом врстом: `hello`, `start`, `mis`, `p`, `d`, `ev`, `cb`, `noexport`, `stop`; линија било које друге врсте под `unknown`
- `d` (1 Hz, само сирово): LoGetSelfData цео (држава, коалиција, називи јединице и групе, нивои типа, заставице), LoGetEngineInfo, LoGetMechInfo, LoGetPayloadInfo, LoGetSnares, LoGetWingInfo, вектор ветра, LoGetFMData, LoGetNavigationInfo, LoGetRoute, LoGetMCPState, HSI, радио светионици, пауза, убрзање времена, седиште, притисак, одступања - спљоштено у тачкасте кључеве
- `mis`: табела времена мисије, спљоштена; `cb`: onSimulationPause/Resume, onMissionLoad\*, onNet\*, onPlayerConnect/Disconnect/Start/Stop/ChangeSlot, onChatMessage, onTriggerMessage, onRadioMessage, onRadioCommand, onShowMessage са њиховим аргументима

**Није доступно**

- други објекти (LoGetWorldObjects, LoGetObjectById) и подаци сензора (LoGetTargetInformation, LoGetLockedTargetInformation, LoGetTWSInfo, LoGetWingTargets, LoGetSightingSystemInfo): не траже се - сваки објекат мисије 10 пута у секунди је скуп унутар DCS-овог кадра, а сервер их контролише (allow_object_export, allow_sensor_export); Tacview их снима
- цела табела мисије (DCS.getCurrentMission садржи сваку јединицу и окидач, мегабајти): шаљу се само датум, време почетка, време, излет, позориште и верзија
- повратни позиви onPlayerTry\*: они одговарају DCS-у (дозволи или одбију), па их хук не дира
- адресе и UCID-ови других играча: net.get_player_info их даје само серверу, а нису ваши да их чувате
- уноси табеле преко 800 кључева или 6 нивоа дубине у једној `d` линији се секу, да једна линија остане један датаграм

**Величина**: око 20 MB по сату `p` линија (10 у секунди, око 500 бајтова са оквиром) и 15-40 MB `d` дампова (једном у секунди, 4-10 KB у зависности од терета и рута летелице), пре zstd; поновљени кључеви се компресују око десет пута

## Проверено {#verified}

формат линија проверен синтетичким датаграмима; Lua хук није проверен унутар DCS-а (написан по API-ју DCS хукова и извоза и по списку Lo\* функција из Scripts\Export.lua, није покретан)

## Извор {#source}

[heat3d_watch/adapters/dcs.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/dcs.py)

<!-- Generated from the adapter by tools/gen_game_pages.py; change the adapter and run it again rather than editing this page. -->
