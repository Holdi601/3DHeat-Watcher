---
title: "Игре"
nav_order: 4
lang: "sr"
source: games.md
source_hash: "0766c0bb0763"
nav_exclude: true
search_exclude: true
---
# Игре {#games}

Посматрач познаје 50 извора у 45 игара и платформи. Сваки има своју страницу, генерисану из његовог адаптера: шта снима, одакле, како се укључује, како ради, своје осе, шта је проверено.

Врсте: `telemetry`, `gsi`, `log`, `replay` и `platform` - видите [Извори и правила](sources-and-rules.md). Положаји: *да* кад адаптер пише редове са местом, *позајмљено* кад га узима из другог снимка исте игре (видите [NVIDIA Highlights](nvidia-highlights.md)), *не* кад извор нема места. Профили меморије се не наводе: ниједан се не испоручује, а сваки играч пише свој (видите [Читање меморије](memory-reading.md)).

| Игра | Врста | Положаји | Извор |
|---|---|---|---|
| [American Truck Simulator (живи подаци)](game-ats.md) | telemetry | да | дељена меморија `Local\SCSTelemetry` коју пише RenCloud scs-sdk-plugin (ревизија 12) у `<game>\bin\win_x64\plugins` |
| [Assetto Corsa (живи подаци)](game-assetto-corsa.md) | telemetry | да | дељена меморија `Local\acpmf_physics`, `Local\acpmf_graphics`, `Local\acpmf_static` |
| [Assetto Corsa Competizione (живи подаци)](game-assetto-corsa-competizione.md) | telemetry | да | дељена меморија `Local\acpmf_physics`, `Local\acpmf_graphics`, `Local\acpmf_static` |
| [Assetto Corsa EVO (живи подаци)](game-assetto-corsa-evo.md) | telemetry | да | дељена меморија `Local\acevo_pmf_physics`, `Local\acevo_pmf_static` |
| [Assetto Corsa Rally (живи подаци)](game-assetto-corsa-rally.md) | telemetry | да | дељена меморија `Local\acpmf_physics`, `Local\acpmf_static` (исте странице као AC и ACC) |
| [Automobilista 2 (живи подаци)](game-automobilista-2.md) | telemetry | да | дељена меморија $pcars2$ (распоред SMS SharedMemory.h) |
| [BeamNG.drive (живи подаци)](game-beamng.md) | telemetry | да | UDP 127.0.0.1:4460 из heat3d протокол мода (mods/beamng/heat3d у овом репозиторијуму) |
| [Counter-Strike 2 (реплеји)](game-cs2-demos.md) | replay | да | демои које CS2 чува: `<CS2>/game/csgo/replays/*.dem` (преузети из историје мечева) и `<CS2>/game/csgo/*.dem` (снимљени) |
| [Counter-Strike 2 (стање игре)](game-cs2-gsi.md) | gsi | да | Game State Integration: HTTP POST захтеви на 127.0.0.1:3311, подешени датотеком `<CS2>\game\csgo\cfg\gamestate_integration_heat3d.cfg` |
| [DCS World (живи подаци)](game-dcs.md) | telemetry | да | хук посматрача `%USERPROFILE%\Saved` `Games\DCS*\Scripts\Hooks\heat3d-watch.lua`, UDP линије на 127.0.0.1:41993 |
| [DiRT Rally 2.0 (живи подаци)](game-dirt-rally-2.md) | telemetry | да | UDP 127.0.0.1:20777, extradata=3 `(Documents\My` `Games\DiRT` Rally `2.0\hardwaresettings\hardware_settings_config.xml`); док други програм држи 20777, посматрач порт препушта њему |
| [Dota 2 (реплеји)](game-dota-replays.md) | replay | да | реплеји које Dota 2 чува: `<Dota>/game/dota/replays/<match id>.dem` (преузети у клијенту, или са `dota-replay <match id>`) |
| [Dota 2 (стање игре)](game-dota2-gsi.md) | gsi | да | Game State Integration: HTTP POST захтеви на 127.0.0.1:3312, подешени датотеком `<Dota>\game\dota\cfg\gamestate_integration\gamestate_integration_heat3d.cfg` |
| [EA SPORTS F1 23 (живи подаци)](game-f1-23.md) | telemetry | да | UDP телеметрија 127.0.0.1:20777 `(Documents\My` `Games\F1` `23\hardwaresettings\hardware_settings_config.xml`) |
| [EA SPORTS F1 24 (живи подаци)](game-f1-24.md) | telemetry | да | UDP телеметрија 127.0.0.1:20777 `(Documents\My` `Games\F1` `24\hardwaresettings\hardware_settings_config.xml`) |
| [EA SPORTS F1 25 (живи подаци)](game-f1-25.md) | telemetry | да | UDP телеметрија 127.0.0.1:20777 `(Documents\My` `Games\F1` `25\hardwaresettings\hardware_settings_config.xml`) |
| [EA SPORTS WRC (живи подаци)](game-ea-wrc.md) | telemetry | да | UDP 127.0.0.1:20777, пакет session_update подразумеване структуре `wrc` `(Documents\My` `Games\WRC\telemetry\config.json`); док други програм држи 20777, посматрач порт препушта њему |
| [Elite Dangerous (датотеке дневника)](game-elite.md) | log | да | дневник играча `%USERPROFILE%\Saved` `Games\Frontier` `Developments\Elite` `Dangerous\Journal.*.log` (најновија датотека, прати се док се пише), Status.json и остале пратеће `*.json` датотеке (Market, Outfitting, Shipyard, NavRoute, Cargo, ModulesInfo, ShipLocker, Backpack, FCMaterials) у истој фасцикли |
| [Euro Truck Simulator 2 (живи подаци)](game-ets2.md) | telemetry | да | дељена меморија `Local\SCSTelemetry` коју пише RenCloud scs-sdk-plugin (ревизија 12) у `<game>\bin\win_x64\plugins` |
| [EVE Online (датотеке дневника)](game-eve.md) | log | не | `%USERPROFILE%\Documents\EVE\logs\Gamelogs\*.txt` и `Chatlogs\*.txt` поред њих (свака датотека написана откад је клијент покренут) |
| [Forza Horizon 4 (живи подаци)](game-forza-horizon-4.md) | telemetry | да | Forza Data Out, UDP 127.0.0.1:5300 (формат Dash); сваки пакет се непромењен прослеђује на 127.0.0.1:5301 |
| [Forza Horizon 5 (живи подаци)](game-forza-horizon-5.md) | telemetry | да | Forza Data Out, UDP 127.0.0.1:5300 (формат Dash); сваки пакет се непромењен прослеђује на 127.0.0.1:5301 |
| [Forza Horizon 6 (живи подаци)](game-forza-horizon-6.md) | telemetry | да | Forza Data Out, UDP 127.0.0.1:5300 (формат Dash); сваки пакет се непромењен прослеђује на 127.0.0.1:5301 |
| [Forza Motorsport (живи подаци)](game-forza-motorsport.md) | telemetry | да | Forza Data Out, UDP 127.0.0.1:5300 (формат Dash); сваки пакет се непромењен прослеђује на 127.0.0.1:5301 |
| [Hearthstone (датотеке дневника)](game-hearthstone.md) | log | не | `<install>\Logs\Power.log` (или `Logs\Hearthstone_*\Power.log`), писан кад `%LOCALAPPDATA%\Blizzard\Hearthstone\log.config` има одељак [Power], и сваки други `*.log` који игра тамо пише |
| [IL-2 Sturmovik: Great Battles (живи подаци)](game-il2.md) | telemetry | не | телеметријски UDP излаз игре на 127.0.0.1:41995 (`[KEY = telemetrydevice]` у `<game>\data\startup.cfg`) |
| [IL-2 Sturmovik: Great Battles (реплеји)](game-il2-tacview.md) | replay | да | Tacview снимци саме игре `<game>\data\Tracks\*.acmi` (ACMI 2.x текст, обичан или спакован) |
| [iRacing (живи подаци)](game-iracing.md) | telemetry | не | дељена меморија `Local\IRSDKMemMapFileName` (iRacing SDK); .ibt датотеке у `%USERPROFILE%\Documents\iRacing\telemetry` |
| [League of Legends (стање игре)](game-lol-live.md) | gsi | не | Live Client Data API клијента игре, <https://127.0.0.1:2999/liveclientdata/> (allgamedata, eventdata), током меча |
| [League of Legends (реплеји)](game-lol-replays.md) | replay | да | реплеји које сачува League клијент: %USERPROFILE%/Documents/League of `Legends/Replays/*.rofl` (само обични крајњи подаци о мечу); са вашим Riot API кључем, званична временска линија меча са Riot-овог Match-V5 API-ја |
| [Microsoft Flight Simulator 2020 (живи подаци)](game-msfs2020.md) | telemetry | да | SimConnect преко сопственог SimConnect.dll играча (фасцикла симулатора, или `%MSFS_SDK%\SimConnect` `SDK\lib`) |
| [Microsoft Flight Simulator 2024 (живи подаци)](game-msfs2024.md) | telemetry | да | SimConnect преко сопственог SimConnect.dll играча (фасцикла симулатора, или `%MSFS2024_SDK%\SimConnect` `SDK\lib`) |
| [Minecraft (датотеке дневника)](game-minecraft.md) | log | да | `%APPDATA%\.minecraft\logs\latest.log` (прати се), `saves\<world>\stats\<uuid>.json` и `saves\<world>\playerdata\<uuid>.dat` / level.dat (gzip NBT), читају се кад игра их сачува |
| [NVIDIA highlights (платформа)](game-nvidia-highlights.md) | platform | позајмљено | `%LOCALAPPDATA%\NVIDIA` `Corporation\NVIDIA` `Overlay\UGCTracker.json`, GallerySettings.json, `Highlights\<game>\config.json`; клипови у фасцикли за снимке `(%USERPROFILE%\Videos\NVIDIA\<Game>\*.mp4`) и `<temp>\Highlights\<game>`; `%LOCALAPPDATA%\NVIDIA` `Corporation\GfeSDK\<exe>_<pid>.log` |
| [osu! (реплеји)](game-osu-replays.md) | replay | да | реплеји osu! (стабилна верзија) које сачува: `%LOCALAPPDATA%/osu!/Data/r/*.osr` (свака игра) и `osu!/Replays/*.osr` (извезени) |
| [Path of Exile (датотеке дневника)](game-poe.md) | log | не | `<install>\logs\Client.txt` игре Path of Exile или Path of Exile 2 (прати се; фасцикла инсталације је фасцикла покренутог извршног програма) |
| [Project CARS 2 (живи подаци)](game-project-cars-2.md) | telemetry | да | дељена меморија $pcars2$ (SMS SharedMemory.h) |
| [RaceRoom Racing Experience (живи подаци)](game-raceroom.md) | telemetry | да | дељена меморија $R3E (Sector3-ов r3e.h, верзија 3) |
| [Richard Burns Rally (живи подаци)](game-richard-burns-rally.md) | telemetry | да | NGP додатак, UDP телеметрија 127.0.0.1:6776 (RichardBurnsRally.ini [NGP] udpTelemetry=1) |
| [Rocket League (стање игре)](game-rocketleague-stats.md) | gsi | да | Stats API: TCP JSON ток са 127.0.0.1:49123 (порт у `<RL>\TAGame\Config\TAStatsAPI.ini` или DefaultStatsAPI.ini) |
| [Squad (реплеји)](game-squad-demos.md) | replay | да | демои сервера које Squad снима админ наредбом AdminDemoRec: `<server>/SquadGame/Saved/Demos/*.replay`, читају се спољним читачем `heat3d-squad-demo` (exporters/ext/squad-demo) |
| [Star Citizen (датотеке дневника)](game-starcitizen.md) | log | не | `<install>\StarCitizen\LIVE\Game.log` (фасцикла верзије покренутог StarCitizen.exe), само датотека дневника коју игра пише - игра са Easy Anti-Cheat: ништа не дира њен процес |
| [Steam статистика (платформа)](game-steam-stats.md) | platform | не | Steam-ов локални кеш статистике `%STEAM%\appcache\stats\UserGameStats_<account>_<appid>.bin` са `UserGameStatsSchema_<appid>.bin`; време игре из `%STEAM%\userdata\<account>\config\localconfig.vdf` (%STEAM% из `HKCU\Software\Valve\Steam` SteamPath) |
| [Steam Timeline (платформа)](game-steam-timeline.md) | platform | не | `%STEAM%\userdata\<account>\gamerecordings\timelines\timeline_<appid><date>_<time>.json` |
| [VALORANT (реплеји)](game-valorant-replays.md) | replay | не | реплеји које VALORANT чува: `%LOCALAPPDATA%/VALORANT/Saved/Demos/*.vrf` (само делови који нису замућени) |
| [War Thunder (реплеји)](game-warthunder-replays.md) | replay | да | реплеји које War Thunder чува: `<War Thunder>/Replays/*.wrpl` (с укљученим чувањем реплеја), претвара их спољни конвертер `heat3d-wt-replay` (exporters/ext/warthunder-replay) |
| [War Thunder (стање игре)](game-warthunder-webmap.md) | gsi | да | локална веб мапа саме игре, <http://127.0.0.1:8111> (/map_info.json, /map_obj.json, /state, /indicators, /hudmsg, /gamechat, /mission.json, /map.img) |
| [World of Tanks (реплеји)](game-wot-replays.md) | replay | да | реплеји које World of Tanks чува: `<World of Tanks>/replays/*.wotreplay` (с укљученим снимањем битки), претвара их спољни конвертер `heat3d-wot-replay` (exporters/ext/wot-replay) |
| [World of Warships (реплеји)](game-wows-replays.md) | replay | да | реплеји које World of Warships чува: `<World of Warships>/replays/*.wowsreplay` (с укљученим реплејима), претвара их спољни конвертер `heat3d-wows-replay` (exporters/ext/wows-replay) |
| [X-Plane (живи подаци)](game-xplane.md) | telemetry | да | UDP интерфејс X-Plane-а на 127.0.0.1:49000 (RREF datarefs и RPOS положај, одговара посматрачу) |

Игре које се не снимају, и зашто: [Извори и правила](sources-and-rules.md#what-is-declined-and-why). Све у једној табели, онако како га исписује `python -m heat3d_watch games --markdown`: [Све игре у једној табели](watcher.md).

<!-- Generated by tools/gen_game_pages.py; run it again after changing an adapter. -->
