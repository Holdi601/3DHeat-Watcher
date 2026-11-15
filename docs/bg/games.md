---
title: "Игри"
nav_order: 4
lang: "bg"
source: games.md
source_hash: "0766c0bb0763"
nav_exclude: true
search_exclude: true
---
# Игри {#games}

Watcher-ът знае 50 източника в 45 игри и платформи. Всеки има собствена страница, създадена от адаптера си: какво записва, откъде, как се включва, как работи, осите му и какво е проверено.

Видове: `telemetry`, `gsi`, `log`, `replay` и `platform` - вижте [Източници и правила](sources-and-rules.md). Позиции: *да*, когато адаптерът записва редове с място, *взета от друг запис*, когато я взима от друг запис на същата игра (вижте [NVIDIA Highlights](nvidia-highlights.md)), *не*, когато източникът няма място. Профили на памет не са изброени: никой не се доставя готов, а всеки играч пише своя (вижте [Четене на памет](memory-reading.md)).

| Игра | Вид | Позиции | Източник |
|---|---|---|---|
| [American Truck Simulator (данни на живо)](game-ats.md) | telemetry | да | споделена памет `Local\SCSTelemetry`, записвана от scs-sdk-plugin на RenCloud (ревизия 12) в `<game>\bin\win_x64\plugins` |
| [Assetto Corsa (данни на живо)](game-assetto-corsa.md) | telemetry | да | споделена памет `Local\acpmf_physics`, `Local\acpmf_graphics`, `Local\acpmf_static` |
| [Assetto Corsa Competizione (данни на живо)](game-assetto-corsa-competizione.md) | telemetry | да | споделена памет `Local\acpmf_physics`, `Local\acpmf_graphics`, `Local\acpmf_static` |
| [Assetto Corsa EVO (данни на живо)](game-assetto-corsa-evo.md) | telemetry | да | споделена памет `Local\acevo_pmf_physics`, `Local\acevo_pmf_static` |
| [Assetto Corsa Rally (данни на живо)](game-assetto-corsa-rally.md) | telemetry | да | споделена памет `Local\acpmf_physics`, `Local\acpmf_static` (същите страници като AC и ACC) |
| [Automobilista 2 (данни на живо)](game-automobilista-2.md) | telemetry | да | споделена памет $pcars2$ (оформление SMS SharedMemory.h) |
| [BeamNG.drive (данни на живо)](game-beamng.md) | telemetry | да | UDP 127.0.0.1:4460 от мода на протокола heat3d (mods/beamng/heat3d в това хранилище) |
| [Counter-Strike 2 (реплеи)](game-cs2-demos.md) | replay | да | демота, които CS2 записва: `<CS2>/game/csgo/replays/*.dem` (свалени от историята на мачовете) и `<CS2>/game/csgo/*.dem` (записани) |
| [Counter-Strike 2 (състояние на играта)](game-cs2-gsi.md) | gsi | да | Game State Integration: HTTP POST заявки към 127.0.0.1:3311, настроени от `<CS2>\game\csgo\cfg\gamestate_integration_heat3d.cfg` |
| [DCS World (данни на живо)](game-dcs.md) | telemetry | да | куката на watcher-а `%USERPROFILE%\Saved` `Games\DCS*\Scripts\Hooks\heat3d-watch.lua`, UDP редове към 127.0.0.1:41993 |
| [DiRT Rally 2.0 (данни на живо)](game-dirt-rally-2.md) | telemetry | да | UDP 127.0.0.1:20777, extradata=3 `(Documents\My` `Games\DiRT` Rally `2.0\hardwaresettings\hardware_settings_config.xml`); докато друго приложение държи 20777, watcher-ът оставя порта на него |
| [Dota 2 (реплеи)](game-dota-replays.md) | replay | да | реплеи, които Dota 2 записва: `<Dota>/game/dota/replays/<match id>.dem` (свалени в клиента или с `dota-replay <match id>`) |
| [Dota 2 (състояние на играта)](game-dota2-gsi.md) | gsi | да | Game State Integration: HTTP POST заявки към 127.0.0.1:3312, настроени от `<Dota>\game\dota\cfg\gamestate_integration\gamestate_integration_heat3d.cfg` |
| [EA SPORTS F1 23 (данни на живо)](game-f1-23.md) | telemetry | да | UDP телеметрия 127.0.0.1:20777 `(Documents\My` `Games\F1` `23\hardwaresettings\hardware_settings_config.xml`) |
| [EA SPORTS F1 24 (данни на живо)](game-f1-24.md) | telemetry | да | UDP телеметрия 127.0.0.1:20777 `(Documents\My` `Games\F1` `24\hardwaresettings\hardware_settings_config.xml`) |
| [EA SPORTS F1 25 (данни на живо)](game-f1-25.md) | telemetry | да | UDP телеметрия 127.0.0.1:20777 `(Documents\My` `Games\F1` `25\hardwaresettings\hardware_settings_config.xml`) |
| [EA SPORTS WRC (данни на живо)](game-ea-wrc.md) | telemetry | да | UDP 127.0.0.1:20777, стандартната структура `wrc` - пакетът session_update `(Documents\My` `Games\WRC\telemetry\config.json`); докато друго приложение държи 20777, watcher-ът оставя порта на него |
| [Elite Dangerous (файлове с дневници)](game-elite.md) | log | да | дневникът на играча `%USERPROFILE%\Saved` `Games\Frontier` `Developments\Elite` `Dangerous\Journal.*.log` (най-новият файл, следен докато се пише), Status.json и другите придружаващи `*.json` файлове (Market, Outfitting, Shipyard, NavRoute, Cargo, ModulesInfo, ShipLocker, Backpack, FCMaterials) в същата папка |
| [Euro Truck Simulator 2 (данни на живо)](game-ets2.md) | telemetry | да | споделена памет `Local\SCSTelemetry`, записвана от scs-sdk-plugin на RenCloud (ревизия 12) в `<game>\bin\win_x64\plugins` |
| [EVE Online (файлове с дневници)](game-eve.md) | log | не | `%USERPROFILE%\Documents\EVE\logs\Gamelogs\*.txt` и `Chatlogs\*.txt` до тях (всеки файл, записан, откакто клиентът е стартирал) |
| [Forza Horizon 4 (данни на живо)](game-forza-horizon-4.md) | telemetry | да | Forza Data Out, UDP 127.0.0.1:5300 (формат Dash); всеки пакет се препраща непроменен към 127.0.0.1:5301 |
| [Forza Horizon 5 (данни на живо)](game-forza-horizon-5.md) | telemetry | да | Forza Data Out, UDP 127.0.0.1:5300 (формат Dash); всеки пакет се препраща непроменен към 127.0.0.1:5301 |
| [Forza Horizon 6 (данни на живо)](game-forza-horizon-6.md) | telemetry | да | Forza Data Out, UDP 127.0.0.1:5300 (формат Dash); всеки пакет се препраща непроменен към 127.0.0.1:5301 |
| [Forza Motorsport (данни на живо)](game-forza-motorsport.md) | telemetry | да | Forza Data Out, UDP 127.0.0.1:5300 (формат Dash); всеки пакет се препраща непроменен към 127.0.0.1:5301 |
| [Hearthstone (файлове с дневници)](game-hearthstone.md) | log | не | `<install>\Logs\Power.log` (или `Logs\Hearthstone_*\Power.log`), записван, след като `%LOCALAPPDATA%\Blizzard\Hearthstone\log.config` има секция [Power], и всеки друг `*.log`, който играта записва там |
| [IL-2 Sturmovik: Great Battles (данни на живо)](game-il2.md) | telemetry | не | телеметричният UDP изход на играта към 127.0.0.1:41995 (`[KEY = telemetrydevice]` в `<game>\data\startup.cfg`) |
| [IL-2 Sturmovik: Great Battles (реплеи)](game-il2-tacview.md) | replay | да | собствените Tacview записи на играта `<game>\data\Tracks\*.acmi` (ACMI 2.x текст, обикновен или zip) |
| [iRacing (данни на живо)](game-iracing.md) | telemetry | не | споделена памет `Local\IRSDKMemMapFileName` (SDK на iRacing); файлове .ibt в `%USERPROFILE%\Documents\iRacing\telemetry` |
| [League of Legends (състояние на играта)](game-lol-live.md) | gsi | не | Live Client Data API на клиента на играта, <https://127.0.0.1:2999/liveclientdata/> (allgamedata, eventdata), по време на мач |
| [League of Legends (реплеи)](game-lol-replays.md) | replay | да | реплеи, които клиентът на League записва: %USERPROFILE%/Documents/League of `Legends/Replays/*.rofl` (само простите метаданни в края на мача); с ваш собствен ключ на Riot API - официалната хронология на мача от Match-V5 API на Riot |
| [Microsoft Flight Simulator 2020 (данни на живо)](game-msfs2020.md) | telemetry | да | SimConnect през собствения SimConnect.dll на играча (папката на симулатора или `%MSFS_SDK%\SimConnect` `SDK\lib`) |
| [Microsoft Flight Simulator 2024 (данни на живо)](game-msfs2024.md) | telemetry | да | SimConnect през собствения SimConnect.dll на играча (папката на симулатора или `%MSFS2024_SDK%\SimConnect` `SDK\lib`) |
| [Minecraft (файлове с дневници)](game-minecraft.md) | log | да | `%APPDATA%\.minecraft\logs\latest.log` (следен), `saves\<world>\stats\<uuid>.json` и `saves\<world>\playerdata\<uuid>.dat` / level.dat (gzip NBT), четени когато играта ги запише |
| [NVIDIA Highlights (платформа)](game-nvidia-highlights.md) | platform | взета от друг запис | `%LOCALAPPDATA%\NVIDIA` `Corporation\NVIDIA` `Overlay\UGCTracker.json`, GallerySettings.json, `Highlights\<game>\config.json`; клиповете в папката за заснемане `(%USERPROFILE%\Videos\NVIDIA\<Game>\*.mp4`) и `<temp>\Highlights\<game>`; `%LOCALAPPDATA%` `NVIDIA Corporation\GfeSDK\<exe>_<pid>.log` |
| [osu! (реплеи)](game-osu-replays.md) | replay | да | реплеи, които записва osu! (stable): `%LOCALAPPDATA%/osu!/Data/r/*.osr` (всяка игра) и `osu!/Replays/*.osr` (експортирани) |
| [Path of Exile (файлове с дневници)](game-poe.md) | log | не | `<install>\logs\Client.txt` на Path of Exile или Path of Exile 2 (следен; папката на инсталацията е тази на работещия изпълним файл) |
| [Project CARS 2 (данни на живо)](game-project-cars-2.md) | telemetry | да | споделена памет $pcars2$ (SMS SharedMemory.h) |
| [RaceRoom Racing Experience (данни на живо)](game-raceroom.md) | telemetry | да | споделена памет $R3E (r3e.h на Sector3, версия 3) |
| [Richard Burns Rally (данни на живо)](game-richard-burns-rally.md) | telemetry | да | UDP телеметрия на NGP добавката, 127.0.0.1:6776 (RichardBurnsRally.ini [NGP] udpTelemetry=1) |
| [Rocket League (състояние на играта)](game-rocketleague-stats.md) | gsi | да | Stats API: TCP JSON поток от 127.0.0.1:49123 (портът е в `<RL>\TAGame\Config\TAStatsAPI.ini` или DefaultStatsAPI.ini) |
| [Squad (реплеи)](game-squad-demos.md) | replay | да | демота на сървър на Squad, записвани с админ командата AdminDemoRec: `<server>/SquadGame/Saved/Demos/*.replay`, четени от външния четец `heat3d-squad-demo` (exporters/ext/squad-demo) |
| [Star Citizen (файлове с дневници)](game-starcitizen.md) | log | не | `<install>\StarCitizen\LIVE\Game.log` (папката на сборката на работещия StarCitizen.exe), само файлът с дневника, който играта записва - игра с Easy Anti-Cheat: нищо не докосва процеса ѝ |
| [Статистики на Steam (платформа)](game-steam-stats.md) | platform | не | локалният кеш на статистиките на Steam `%STEAM%\appcache\stats\UserGameStats_<account>_<appid>.bin` с `UserGameStatsSchema_<appid>.bin`; времето за игра от `%STEAM%\userdata\<account>\config\localconfig.vdf` (%STEAM% от `HKCU\Software\Valve\Steam` SteamPath) |
| [Steam Timeline (платформа)](game-steam-timeline.md) | platform | не | `%STEAM%\userdata\<account>\gamerecordings\timelines\timeline_<appid><date>_<time>.json` |
| [VALORANT (реплеи)](game-valorant-replays.md) | replay | не | реплеи, които записва VALORANT: `%LOCALAPPDATA%/VALORANT/Saved/Demos/*.vrf` (само частите, които не са обфусцирани) |
| [War Thunder (реплеи)](game-warthunder-replays.md) | replay | да | реплеи, които записва War Thunder: `<War Thunder>/Replays/*.wrpl` (със записа на реплеи включен), превръщани от външния конвертор `heat3d-wt-replay` (exporters/ext/warthunder-replay) |
| [War Thunder (състояние на играта)](game-warthunder-webmap.md) | gsi | да | локалната уеб карта на играта, <http://127.0.0.1:8111> (/map_info.json, /map_obj.json, /state, /indicators, /hudmsg, /gamechat, /mission.json, /map.img) |
| [World of Tanks (реплеи)](game-wot-replays.md) | replay | да | реплеи, които записва World of Tanks: `<World of Tanks>/replays/*.wotreplay` (с записа на битки включен), превръщани от външния конвертор `heat3d-wot-replay` (exporters/ext/wot-replay) |
| [World of Warships (реплеи)](game-wows-replays.md) | replay | да | реплеи, които записва World of Warships: `<World of Warships>/replays/*.wowsreplay` (с включени реплеи), превръщани от външния конвертор `heat3d-wows-replay` (exporters/ext/wows-replay) |
| [X-Plane (данни на живо)](game-xplane.md) | telemetry | да | UDP интерфейсът на X-Plane на 127.0.0.1:49000 (RREF datarefs и RPOS позиция, отговаряни към watcher-а) |

Игри, които не се записват, и защо: [Източници и правила](sources-and-rules.md#what-is-declined-and-why). Всичко в една таблица, както го печата `python -m heat3d_watch games --markdown`: [Всички игри в една таблица](watcher.md).

<!-- Generated by tools/gen_game_pages.py; run it again after changing an adapter. -->
