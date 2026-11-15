---
title: "DCS World (данни на живо)"
nav_order: 10
lang: "bg"
source: game-dcs.md
source_hash: "87cba160674e"
nav_exclude: true
search_exclude: true
---
# DCS World (данни на живо) {#dcs-world-live-data}

Докато играете DCS World, watcher-ът записва данните, които самата игра изпраща навън, за да можете по-късно да ги разгледате на карта в 3DHeat визуализатора.

*Технически подробности: адаптер `dcs`, вид [`telemetry`](sources-and-rules.md); работи, докато `DCS.exe` е стартиран, и търси нови данни на всеки 0.1 s.*

## Какво се записва {#what-is-recorded}

- собствената позиция на 10 Hz в метри на изток/нагоре/на север от началната точка на театъра (от ширина/дължина/височина); ширина, дължина и височина и собствените световни метри на DCS (dcs_x север, dcs_y нагоре, dcs_z изток) като колони
- ориентация, посочена и истинска въздушна скорост, Мах, вертикална скорост, ъгъл на атака и плъзгане, магнитен курс, височина над земята и радарна височина, g по три оси, скорост и ъглови скорости, във въздух, позицията и посоката на камерата, тип на самолета
- излитания и кацания с летището; катастрофи, катапултирания, смърти на пилоти
- убийства и свалянето на вашия самолет, с двата типа единици и оръжието; други събития в играта, както са дадени
- живота на играча в мисия (spawn ... session_end), убийства, смърти, разстояние, най-голяма височина, най-голямо g
- всеки ред, който изпраща куката, пазен цял в `heat.raw.parquet`, с дъмп веднъж в секунда на експортните таблици на самолета (двигатели, шаси и клапи, товар, контрамерки, маршрут, навигация) и всеки друг callback (пауза, чат, влизане на играчи, зареждане на мисия)

## Откъде идва {#where-it-comes-from}

куката на watcher-а %USERPROFILE%\Saved Games\DCS\*\Scripts\Hooks\heat3d-watch.lua, UDP редове към 127.0.0.1:41993

## Как се включва {#how-to-switch-it-on}

python -m heat3d_watch setup dcs --apply (добавя Scripts\Hooks\heat3d-watch.lua), след това рестартирайте DCS

Напишете командата в терминал, отворен в папката на watcher-а (вижте [Преди да започнете](before-you-start.md)). Ако се провали, последният ред казва защо; [Инсталиране и стартиране](installing-and-running.md) описва честите причини.

`python -m heat3d_watch setup dcs` показва кои файлове би променил; `python -m heat3d_watch setup dcs --apply` ги променя и запазва оригинала като `<file>.heat3d-backup` (вижте [Команди](commands.md#setup)). Печата `dcs: changed: ...` за всяка промяна или `dcs: nothing to change`, когато вече е включено.

## Как работи {#how-it-works}

DCS World: малък скрипт-кука на самия watcher, който изпраща UDP редове към 127.0.0.1:41993.

DCS изпълнява Lua файлове от `Saved Games\DCS*\Scripts\Hooks\` при стартиране; кука може да чете експортните функции (`Export.Lo*`) и да получава callback-ите на симулацията (`DCS.setUserCallbacks`: onSimulationStart/Frame/Stop, onGameEvent) - вижте `<DCS>\API\DCS_ControlAPI.html` и <https://wiki.hoggitworld.com/view/DCS_Export_Script>.
`setup` записва `heat3d-watch.lua` там (собствен файл: Export.lua и куките на другите инструменти не се пипат), който изпраща десет реда в секунда, още един в секунда и по един за всяко игрово събитие или callback, без да чака отговор. Портът е 41993, за да работят куката на JoyPro (41992) и Tacview (42674) до нея. Редовете (полетата са разделени с ';'):

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

`p` е LoGetSelfData: Position x/y/z - собствените световни метри на DCS, x на север, y нагоре, z на изток - плюс LatLongAlt (градуси, m), Heading/Pitch/Bank (радиани), с LoGetIndicatedAirSpeed (m/s), LoGetAltitudeAboveGroundLevel (m) и LoGetAccelerationUnits() x/y/z (g); и, както ги описва `Scripts\Export.lua`, LoGetTrueAirSpeed (m/s), LoGetMachNumber, LoGetVerticalVelocity (m/s), LoGetAngleOfAttack и LoGetAngleOfSideSlip (rad), LoGetMagneticYaw (rad), LoGetRadarAltimeter (m), LoGetVectorVelocity (световни m/s), LoGetAngularVelocity (rad/s), LoGetInAir и точката и посоката на камерата от LoGetCameraPosition (световни метри). `d` е дъмп веднъж в секунда на цели таблици, изравнени до точкови ключове: LoGetSelfData (държава, коалиция, имена на единица и група, нива на типа, флагове), LoGetEngineInfo, LoGetMechInfo, LoGetPayloadInfo, LoGetSnares, LoGetWingInfo, LoGetVectorWindVelocity, LoGetFMData, LoGetNavigationInfo, LoGetRoute, LoGetMCPState, LoGetControlPanel_HSI, LoGetRadioBeaconsStatus и няколко числа (пауза, ускорение на времето, място, налягане, отклонения). Watcher-ът пази всеки ред цял в страничния файл за суров запис; `p` също става редове.

Позициите влизат в същата плоска карта като тези на другите симулатори на полет (`Tangent`: x на изток, y височина над морското равнище, z на север, в метри) от LatLongAlt, около фиксираната начална точка на театъра (`THEATRES`, от `map` на стартовия ред), така че всяка мисия на един театър споделя една карта и визуализаторът може да подложи под нея реалния свят. Театър, който го няма в таблицата, взима първата географска ширина и дължина, закръглени до цели градуси. DCS-овите x/y/z се пазят като `dcs_x`, `dcs_y`, `dcs_z`; позиция без LatLongAlt не може да се постави и само се брои (`fixes_without_latlon`). Началната точка е `geo` на сесията, в meta.json и в края на таблицата.

Аргументите на onGameEvent, както ги дава DCS_ControlAPI: takeoff/landing (playerID, unit_missionID, airdromeName), crash/eject/pilot_death (playerID, unit_missionID), kill (killerPlayerID, killerUnitType, killerSide, victimPlayerID, victimUnitType, victimSide, weaponName), self_kill (playerID), change_slot (playerID, slotID, prevSide), mission_end (winner, msg).

Многопотребителски сървър може да забрани експорта на собствения самолет (LoIsOwnshipExportAllowed е false); тогава няма позиции, само събития, и сесията го казва.

## Позиции и оси {#positions-and-axes}

| | |
|---|---|
| Записани позиции | да |
| Вертикална ос | `y` |
| Единици | метри (изток, височина, север от началната точка на театъра) |
| Огледално за визуализатора | `z` |
| Мащаб на единицата (`scale`: визуализаторът умножава позициите по него) | 1 |

Те отиват в `meta.json` (`axes`) на всяка сесия и, когато сесията има позиции, в долния колонтитул на `heat.parquet`, така че 3DHeat визуализаторът сам завърта и мащабира редовете - вижте [Данните](the-data.md).

## Мултиплейър {#multiplayer}

- Маркиран като игран онлайн (`multiplayer`): **да**. `games --markdown` показва това като "разрешено (чете само това, което играта публикува)".
- Вид `telemetry`: чете само това, което играта или платформата предава (UDP порт или споделена памет, които играта публикува), затова записва и в онлайн игра, както и офлайн; флагът решава само дали паметта може изобщо да се чете.
- Памет: **никога** не се чете от този адаптер. Само адаптерите от вид `memory` четат памет, и никога за игра, маркирана като играна онлайн - вижте [Източници и правила](sources-and-rules.md).

## Записана статистика {#statistics-recorded}

Ключове на статистиката, които кодът на този адаптер задава по име (`stats` на всяка сесия в `meta.json` и таблицата `stats` в `watcher.sqlite`):

`airborne_time`, `bad_packets`, `crashes`, `deaths`, `distance_km`, `ejections`, `export_blocked`, `fixes_without_latlon`, `flight_time`, `kills`, `max_altitude_m`, `max_g`, `shot_down`, `{event}s`

Ключ във фигурни скоби се допълва по време на работа (`score.{team}` е по един ключ за всеки отбор). Ключовете, които кодът взема от таблица с полетата на играта или от собствените имена на статистики на играта, не са в този списък; "Какво се записва" по-горе ги изброява.

## Пълнота {#completeness}

Watcher-ът следва [правилото за конвертори](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md) на 3DHeat: това, което източникът съдържа, се чете или се пази, никога не се изхвърля. Освен редовете, всеки пакет, страница, ред или отговор, който адаптерът получава, се пази цял в `heat.raw.parquet` на сесията (колони `time`, `ms`, `type`, `used`, `payload`, `text` и всяко поле, запазено по име; `used` отбелязва какво е станало и ред), а `selfCheck.completeness` в `meta.json` брои всеки `type` - `lost` е 0.

**Прочетено**

- `p` (10 Hz): позиция, LatLongAlt, ориентация, IAS, AGL, g (x/y/z), тип на самолета, и TAS, Мах, вертикална скорост, AoA, плъзгане, магнитен курс, радарна височина, световна скорост, ъглови скорости, във въздух и точката и посоката на камерата от куката 2 - всичко като колони на редовете (единиците както ги дава Export.lua)
- `start`: мисия, театър, собствен идентификатор и име на играча, мултиплейър, файл на мисията, сървър; `mis`: датата и часът на началото на мисията в meta.json
- `ev`: всеки onGameEvent като ред (takeoff, landing, crash, eject, pilot_death, kill, self_kill, change_slot, connect, disconnect, friendly_fire, mission_end, всяко друго име както е дадено)
- `noexport` и `stop` като редове и в meta.json

**Пазено цяло**

- всеки ред, който куката изпраща, цял, като `text` под своя вид: `hello`, `start`, `mis`, `p`, `d`, `ev`, `cb`, `noexport`, `stop`; ред от друг вид - под `unknown`
- `d` (1 Hz, само суров запис): LoGetSelfData цяло (държава, коалиция, име на единица и група, нива на типа, флагове), LoGetEngineInfo, LoGetMechInfo, LoGetPayloadInfo, LoGetSnares, LoGetWingInfo, векторът на вятъра, LoGetFMData, LoGetNavigationInfo, LoGetRoute, LoGetMCPState, HSI, радиомаяците, пауза, ускорение на времето, място, налягане, отклонения - изравнени до точкови ключове
- `mis`: таблицата с времето на мисията, изравнена; `cb`: onSimulationPause/Resume, onMissionLoad\*, onNet\*, onPlayerConnect/Disconnect/Start/Stop/ChangeSlot, onChatMessage, onTriggerMessage, onRadioMessage, onRadioCommand, onShowMessage с техните аргументи

**Не е налично**

- други единици (LoGetWorldObjects, LoGetObjectById) и сензорни данни (LoGetTargetInformation, LoGetLockedTargetInformation, LoGetTWSInfo, LoGetWingTargets, LoGetSightingSystemInfo): не са заявени - всеки обект на мисията на 10 Hz е скъп в собствения кадър на DCS, а сървърът ги ограничава (allow_object_export, allow_sensor_export); Tacview ги записва
- цялата таблица на мисията (DCS.getCurrentMission съдържа всяка единица и тригер, мегабайти): изпращат се само датата, часът на началото, времето, сортията, театърът и версията
- callback-ите onPlayerTry\*: те отговарят на DCS (разрешават или отказват), затова куката ги оставя на мира
- адреси и UCID на другите играчи: net.get_player_info ги дава само на сървър и не са за пазене от играча
- записите на таблица над 800 ключа или 6 нива на дълбочина в един ред `d` се отрязват, за да остане един ред един UDP пакет

**Размер**: около 20 MB на час редове `p` (10 в секунда, около 500 байта всеки с кадъра си) и 15-40 MB дъмп `d` (по един в секунда, 4-10 KB според товара и маршрута на самолета), преди zstd; повтарящите се ключове се свиват около десет пъти

## Проверено {#verified}

форматът на редовете проверен със синтетични датаграми; Lua куката непроверена в DCS (написана по API-то на куката и списъка на Lo* функциите от Scripts\Export.lua на DCS, не е пускана)

## Източник {#source}

[heat3d_watch/adapters/dcs.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/dcs.py)

<!-- Generated from the adapter by tools/gen_game_pages.py; change the adapter and run it again rather than editing this page. -->
