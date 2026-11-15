---
title: Игри
nav_order: 4
lang: "mk"
source: games.md
source_hash: "0766c0bb0763"
nav_exclude: true
search_exclude: true
---
# Игри {#games}

Watcher-от познава 50 извори во 45 игри и платформи. Секој има своја страница, генерирана од неговиот адаптер: што снима, од каде, како да се вклучи, како работи, неговите оски, што е проверено.

Видови: `telemetry`, `gsi`, `log`, `replay` и `platform` - видете [Извори и правила](sources-and-rules.md). Позиции: *да* кога адаптерот запишува редови со место, *позајмено* кога го зема местото од друго снимање на истата игра (видете [NVIDIA Highlights](nvidia-highlights.md)), *не* кога изворот нема такво. Профилите на меморија не се наведени: ниеден не се испорачува, а секој играч пишува свој (видете [Читање меморија](memory-reading.md)).

| Игра | Вид | Позиции | Извор |
|---|---|---|---|
| [American Truck Simulator (податоци во живо)](game-ats.md) | telemetry | да | споделена меморија `Local\SCSTelemetry` запишана од додатокот RenCloud scs-sdk-plugin (ревизија 12) во `<game>\bin\win_x64\plugins` |
| [Assetto Corsa (податоци во живо)](game-assetto-corsa.md) | telemetry | да | споделена меморија `Local\acpmf_physics`, `Local\acpmf_graphics`, `Local\acpmf_static` |
| [Assetto Corsa Competizione (податоци во живо)](game-assetto-corsa-competizione.md) | telemetry | да | споделена меморија `Local\acpmf_physics`, `Local\acpmf_graphics`, `Local\acpmf_static` |
| [Assetto Corsa EVO (податоци во живо)](game-assetto-corsa-evo.md) | telemetry | да | споделена меморија `Local\acevo_pmf_physics`, `Local\acevo_pmf_static` |
| [Assetto Corsa Rally (податоци во живо)](game-assetto-corsa-rally.md) | telemetry | да | споделена меморија `Local\acpmf_physics`, `Local\acpmf_static` (истите страници како AC и ACC) |
| [Automobilista 2 (податоци во живо)](game-automobilista-2.md) | telemetry | да | споделена меморија $pcars2$ (распоред SMS SharedMemory.h) |
| [BeamNG.drive (податоци во живо)](game-beamng.md) | telemetry | да | UDP 127.0.0.1:4460 од протокол-модот heat3d (mods/beamng/heat3d во ова складиште) |
| [Counter-Strike 2 (повторување)](game-cs2-demos.md) | replay | да | демоа што ги зачувува CS2: `<CS2>/game/csgo/replays/*.dem` (преземени од историјата на натпревари) и `<CS2>/game/csgo/*.dem` (снимени) |
| [Counter-Strike 2 (состојба на играта)](game-cs2-gsi.md) | gsi | да | Game State Integration: HTTP POST-ови до 127.0.0.1:3311, наместени со `<CS2>\game\csgo\cfg\gamestate_integration_heat3d.cfg` |
| [DCS World (податоци во живо)](game-dcs.md) | telemetry | да | куката на watcher-от `%USERPROFILE%\Saved` `Games\DCS*\Scripts\Hooks\heat3d-watch.lua`, UDP-линии до 127.0.0.1:41993 |
| [DiRT Rally 2.0 (податоци во живо)](game-dirt-rally-2.md) | telemetry | да | UDP 127.0.0.1:20777, extradata=3 `(Documents\My` `Games\DiRT` Rally `2.0\hardwaresettings\hardware_settings_config.xml`); додека друга апликација ја држи 20777, watcher-от ѝ ја препушта портата |
| [Dota 2 (повторување)](game-dota-replays.md) | replay | да | повторувања што ги зачувува Dota 2: `<Dota>/game/dota/replays/<match id>.dem` (преземени во клиентот, или со `dota-replay <match id>`) |
| [Dota 2 (состојба на играта)](game-dota2-gsi.md) | gsi | да | Game State Integration: HTTP POST-ови до 127.0.0.1:3312, наместени со `<Dota>\game\dota\cfg\gamestate_integration\gamestate_integration_heat3d.cfg` |
| [EA SPORTS F1 23 (податоци во живо)](game-f1-23.md) | telemetry | да | UDP-телеметрија 127.0.0.1:20777 `(Documents\My` `Games\F1` `23\hardwaresettings\hardware_settings_config.xml`) |
| [EA SPORTS F1 24 (податоци во живо)](game-f1-24.md) | telemetry | да | UDP-телеметрија 127.0.0.1:20777 `(Documents\My` `Games\F1` `24\hardwaresettings\hardware_settings_config.xml`) |
| [EA SPORTS F1 25 (податоци во живо)](game-f1-25.md) | telemetry | да | UDP-телеметрија 127.0.0.1:20777 `(Documents\My` `Games\F1` `25\hardwaresettings\hardware_settings_config.xml`) |
| [EA SPORTS WRC (податоци во живо)](game-ea-wrc.md) | telemetry | да | UDP 127.0.0.1:20777, пакетот session_update од стандардната структура `wrc` `(Documents\My` `Games\WRC\telemetry\config.json`); додека друга апликација ја држи 20777, watcher-от ѝ ја препушта портата |
| [Elite Dangerous (лог-датотеки)](game-elite.md) | log | да | Player Journal `%USERPROFILE%\Saved` `Games\Frontier` `Developments\Elite` `Dangerous\Journal.*.log` (најновата датотека, следена додека се пишува), Status.json и другите придружни `*.json` датотеки (Market, Outfitting, Shipyard, NavRoute, Cargo, ModulesInfo, ShipLocker, Backpack, FCMaterials) во истата папка |
| [Euro Truck Simulator 2 (податоци во живо)](game-ets2.md) | telemetry | да | споделена меморија `Local\SCSTelemetry` запишана од додатокот RenCloud scs-sdk-plugin (ревизија 12) во `<game>\bin\win_x64\plugins` |
| [EVE Online (лог-датотеки)](game-eve.md) | log | не | `%USERPROFILE%\Documents\EVE\logs\Gamelogs\*.txt` и `Chatlogs\*.txt` покрај нив (секоја датотека запишана откако стартувал клиентот) |
| [Forza Horizon 4 (податоци во живо)](game-forza-horizon-4.md) | telemetry | да | Forza Data Out, UDP 127.0.0.1:5300 (формат Dash); секој пакет се препраќа непроменет до 127.0.0.1:5301 |
| [Forza Horizon 5 (податоци во живо)](game-forza-horizon-5.md) | telemetry | да | Forza Data Out, UDP 127.0.0.1:5300 (формат Dash); секој пакет се препраќа непроменет до 127.0.0.1:5301 |
| [Forza Horizon 6 (податоци во живо)](game-forza-horizon-6.md) | telemetry | да | Forza Data Out, UDP 127.0.0.1:5300 (формат Dash); секој пакет се препраќа непроменет до 127.0.0.1:5301 |
| [Forza Motorsport (податоци во живо)](game-forza-motorsport.md) | telemetry | да | Forza Data Out, UDP 127.0.0.1:5300 (формат Dash); секој пакет се препраќа непроменет до 127.0.0.1:5301 |
| [Hearthstone (лог-датотеки)](game-hearthstone.md) | log | не | `<install>\Logs\Power.log` (или `Logs\Hearthstone_*\Power.log`), запишан откако `%LOCALAPPDATA%\Blizzard\Hearthstone\log.config` ќе има секција [Power], и секоја друга `*.log` што играта ја пишува таму |
| [IL-2 Sturmovik: Great Battles (податоци во живо)](game-il2.md) | telemetry | не | UDP-излезот на телеметријата на играта до 127.0.0.1:41995 ([KEY = telemetrydevice] во `<game>\data\startup.cfg`) |
| [IL-2 Sturmovik: Great Battles (повторување)](game-il2-tacview.md) | replay | да | сопствените Tacview-снимки на играта `<game>\data\Tracks\*.acmi` (ACMI 2.x текст, обичен или во zip) |
| [iRacing (податоци во живо)](game-iracing.md) | telemetry | не | споделена меморија `Local\IRSDKMemMapFileName` (iRacing SDK); .ibt датотеки во `%USERPROFILE%\Documents\iRacing\telemetry` |
| [League of Legends (состојба на играта)](game-lol-live.md) | gsi | не | Live Client Data API на клиентот на играта, <https://127.0.0.1:2999/liveclientdata/> (allgamedata, eventdata), за време на натпревар |
| [League of Legends (повторување)](game-lol-replays.md) | replay | да | повторувања што ги зачувува клиентот на League: %USERPROFILE%/Documents/League of `Legends/Replays/*.rofl` (само обичните метаподатоци од крајот на играта); со ваш сопствен Riot API клуч, официјалната временска линија на натпреварот од Match-V5 API на Riot |
| [Microsoft Flight Simulator 2020 (податоци во живо)](game-msfs2020.md) | telemetry | да | SimConnect преку SimConnect.dll на самиот играч (папката на симулаторот, или `%MSFS_SDK%\SimConnect` `SDK\lib`) |
| [Microsoft Flight Simulator 2024 (податоци во живо)](game-msfs2024.md) | telemetry | да | SimConnect преку SimConnect.dll на самиот играч (папката на симулаторот, или `%MSFS2024_SDK%\SimConnect` `SDK\lib`) |
| [Minecraft (лог-датотеки)](game-minecraft.md) | log | да | `%APPDATA%\.minecraft\logs\latest.log` (следен), `saves\<world>\stats\<uuid>.json` и `saves\<world>\playerdata\<uuid>.dat` / level.dat (gzip NBT), читани кога играта ги зачувува |
| [NVIDIA highlights (платформа)](game-nvidia-highlights.md) | platform | позајмено | `%LOCALAPPDATA%\NVIDIA` `Corporation\NVIDIA` `Overlay\UGCTracker.json`, GallerySettings.json, `Highlights\<game>\config.json`; клипови во папката за снимање `(%USERPROFILE%\Videos\NVIDIA\<Game>\*.mp4`) и `<temp>\Highlights\<game>`; `%LOCALAPPDATA%\NVIDIA` `Corporation\GfeSDK\<exe>_<pid>.log` |
| [osu! (повторување)](game-osu-replays.md) | replay | да | повторувања што ги зачувува osu! (stable): `%LOCALAPPDATA%/osu!/Data/r/*.osr` (секоја игра) и `osu!/Replays/*.osr` (извезени) |
| [Path of Exile (лог-датотеки)](game-poe.md) | log | не | `<install>\logs\Client.txt` на Path of Exile или Path of Exile 2 (следен; папката на инсталација е онаа на извршната датотека што работи) |
| [Project CARS 2 (податоци во живо)](game-project-cars-2.md) | telemetry | да | споделена меморија $pcars2$ (SMS SharedMemory.h) |
| [RaceRoom Racing Experience (податоци во живо)](game-raceroom.md) | telemetry | да | споделена меморија $R3E (r3e.h на Sector3, верзија 3) |
| [Richard Burns Rally (податоци во живо)](game-richard-burns-rally.md) | telemetry | да | UDP-телеметрија на NGP-додатокот, 127.0.0.1:6776 (RichardBurnsRally.ini [NGP] udpTelemetry=1) |
| [Rocket League (состојба на играта)](game-rocketleague-stats.md) | gsi | да | Stats API: TCP JSON-струја од 127.0.0.1:49123 (Port во `<RL>\TAGame\Config\TAStatsAPI.ini` или DefaultStatsAPI.ini) |
| [Squad (повторување)](game-squad-demos.md) | replay | да | серверски демоа што Squad ги снима со админ-командата AdminDemoRec: `<server>/SquadGame/Saved/Demos/*.replay`, читани од надворешниот читач `heat3d-squad-demo` (exporters/ext/squad-demo) |
| [Star Citizen (лог-датотеки)](game-starcitizen.md) | log | не | `<install>\StarCitizen\LIVE\Game.log` (папката на изданието на StarCitizen.exe што работи), само лог-датотеката што ја пишува играта - игра со Easy Anti-Cheat: ништо не го допира нејзиниот процес |
| [Steam statistics (платформа)](game-steam-stats.md) | platform | не | локалниот кеш на статистика на Steam `%STEAM%\appcache\stats\UserGameStats_<account>_<appid>.bin` со `UserGameStatsSchema_<appid>.bin`; време на играње од `%STEAM%\userdata\<account>\config\localconfig.vdf` (%STEAM% од `HKCU\Software\Valve\Steam` SteamPath) |
| [Steam Timeline (платформа)](game-steam-timeline.md) | platform | не | `%STEAM%\userdata\<account>\gamerecordings\timelines\timeline_<appid><date>_<time>.json` |
| [VALORANT (повторување)](game-valorant-replays.md) | replay | не | повторувања што ги зачувува VALORANT: `%LOCALAPPDATA%/VALORANT/Saved/Demos/*.vrf` (само деловите што не се замаскирани) |
| [War Thunder (повторување)](game-warthunder-replays.md) | replay | да | повторувања што ги зачувува War Thunder: `<War Thunder>/Replays/*.wrpl` (со вклучено зачувување на повторувања), претворени од надворешниот конвертор `heat3d-wt-replay` (exporters/ext/warthunder-replay) |
| [War Thunder (состојба на играта)](game-warthunder-webmap.md) | gsi | да | локалната веб-мапа на играта, <http://127.0.0.1:8111> (/map_info.json, /map_obj.json, /state, /indicators, /hudmsg, /gamechat, /mission.json, /map.img) |
| [World of Tanks (повторување)](game-wot-replays.md) | replay | да | повторувања што ги зачувува World of Tanks: `<World of Tanks>/replays/*.wotreplay` (со вклучено снимање на битки), претворени од надворешниот конвертор `heat3d-wot-replay` (exporters/ext/wot-replay) |
| [World of Warships (повторување)](game-wows-replays.md) | replay | да | повторувања што ги зачувува World of Warships: `<World of Warships>/replays/*.wowsreplay` (со вклучени повторувања), претворени од надворешниот конвертор `heat3d-wows-replay` (exporters/ext/wows-replay) |
| [X-Plane (податоци во живо)](game-xplane.md) | telemetry | да | UDP-интерфејсот на X-Plane на 127.0.0.1:49000 (RREF datarefs и RPOS позиција, одговорени на watcher-от) |

Игри што не се снимаат, и зошто: [Извори и правила](sources-and-rules.md#what-is-declined-and-why). Сѐ во една табела, како што ја печати `python -m heat3d_watch games --markdown`: [Сите игри во една табела](watcher.md).

<!-- Generated by tools/gen_game_pages.py; run it again after changing an adapter. -->
