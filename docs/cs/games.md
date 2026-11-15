---
title: Hry
nav_order: 4
lang: "cs"
source: games.md
source_hash: "dcee7fc45a5b"
nav_exclude: true
search_exclude: true
---
# Hry {#games}

Watcher zná 50 zdrojů v 45 hrách a platformách. Každý má vlastní stránku, vygenerovanou z jeho adaptéru: co zaznamenává, odkud to bere, jak se zapíná, jak funguje, jeho osy a co bylo ověřeno.

Druhy: `telemetry`, `gsi`, `log`, `replay` a `platform` – viz [Zdroje a pravidla](sources-and-rules.md). Pozice: *ano*, když adaptér píše řádky s místem; *vypůjčeno*, když ho bere z jiného záznamu téže hry (viz [NVIDIA Highlights](nvidia-highlights.md)); *ne*, když zdroj žádné nemá. Profily paměti se tu nevypisují: žádné se nedodávají a každý hráč si píše vlastní (viz [Čtení paměti](memory-reading.md)).

| Hra | Druh | Pozice | Zdroj |
|---|---|---|---|
| [American Truck Simulator (živá data)](game-ats.md) | telemetry | ano | sdílená paměť `Local\SCSTelemetry`, kterou zapisuje plugin RenCloud scs-sdk-plugin (revize 12) ve složce `<game>\bin\win_x64\plugins` |
| [Assetto Corsa (živá data)](game-assetto-corsa.md) | telemetry | ano | sdílená paměť `Local\acpmf_physics`, `Local\acpmf_graphics`, `Local\acpmf_static` |
| [Assetto Corsa Competizione (živá data)](game-assetto-corsa-competizione.md) | telemetry | ano | sdílená paměť `Local\acpmf_physics`, `Local\acpmf_graphics`, `Local\acpmf_static` |
| [Assetto Corsa EVO (živá data)](game-assetto-corsa-evo.md) | telemetry | ano | sdílená paměť `Local\acevo_pmf_physics`, `Local\acevo_pmf_static` |
| [Assetto Corsa Rally (živá data)](game-assetto-corsa-rally.md) | telemetry | ano | sdílená paměť `Local\acpmf_physics`, `Local\acpmf_static` (stejné stránky jako AC a ACC) |
| [Automobilista 2 (živá data)](game-automobilista-2.md) | telemetry | ano | sdílená paměť $pcars2$ (rozložení SMS SharedMemory.h) |
| [BeamNG.drive (živá data)](game-beamng.md) | telemetry | ano | UDP 127.0.0.1:4460 z protokolového modu heat3d (mods/beamng/heat3d v tomto repozitáři) |
| [Counter-Strike 2 (replaye)](game-cs2-demos.md) | replay | ano | dema, která CS2 ukládá: `<CS2>/game/csgo/replays/*.dem` (stažená z historie zápasů) a `<CS2>/game/csgo/*.dem` (nahraná) |
| [Counter-Strike 2 (stav hry)](game-cs2-gsi.md) | gsi | ano | Game State Integration: HTTP POSTy na 127.0.0.1:3311, nastavené souborem `<CS2>\game\csgo\cfg\gamestate_integration_heat3d.cfg` |
| [DCS World (živá data)](game-dcs.md) | telemetry | ano | hook Watcheru `%USERPROFILE%\Saved` `Games\DCS*\Scripts\Hooks\heat3d-watch.lua`, řádky UDP na 127.0.0.1:41993 |
| [DiRT Rally 2.0 (živá data)](game-dirt-rally-2.md) | telemetry | ano | UDP 127.0.0.1:20777, extradata=3 `(Documents\My` `Games\DiRT` Rally `2.0\hardwaresettings\hardware_settings_config.xml`); dokud port 20777 drží jiná aplikace, Watcher ho jí nechá |
| [Dota 2 (replaye)](game-dota-replays.md) | replay | ano | replaye, které ukládá Dota 2: `<Dota>/game/dota/replays/<match id>.dem` (staženo v klientovi, nebo příkazem `dota-replay <match id>`) |
| [Dota 2 (stav hry)](game-dota2-gsi.md) | gsi | ano | Game State Integration: HTTP POSTy na 127.0.0.1:3312, nastavené souborem `<Dota>\game\dota\cfg\gamestate_integration\gamestate_integration_heat3d.cfg` |
| [EA SPORTS F1 23 (živá data)](game-f1-23.md) | telemetry | ano | UDP telemetrie 127.0.0.1:20777 `(Documents\My` `Games\F1` `23\hardwaresettings\hardware_settings_config.xml`) |
| [EA SPORTS F1 24 (živá data)](game-f1-24.md) | telemetry | ano | UDP telemetrie 127.0.0.1:20777 `(Documents\My` `Games\F1` `24\hardwaresettings\hardware_settings_config.xml`) |
| [EA SPORTS F1 25 (živá data)](game-f1-25.md) | telemetry | ano | UDP telemetrie 127.0.0.1:20777 `(Documents\My` `Games\F1` `25\hardwaresettings\hardware_settings_config.xml`) |
| [EA SPORTS WRC (živá data)](game-ea-wrc.md) | telemetry | ano | UDP 127.0.0.1:20777, výchozí struktura `wrc`, paket session_update `(Documents\My` `Games\WRC\telemetry\config.json`); dokud port 20777 drží jiná aplikace, Watcher ho jí nechá |
| [Elite Dangerous (soubory logů)](game-elite.md) | log | ano | Deník hráče `%USERPROFILE%\Saved` `Games\Frontier` `Developments\Elite` `Dangerous\Journal.*.log` (nejnovější soubor, sledovaný, jak se zapisuje), Status.json a ostatní soubory `*.json` společníka (Market, Outfitting, Shipyard, NavRoute, Cargo, ModulesInfo, ShipLocker, Backpack, FCMaterials) ve stejné složce |
| [Euro Truck Simulator 2 (živá data)](game-ets2.md) | telemetry | ano | sdílená paměť `Local\SCSTelemetry`, kterou zapisuje plugin RenCloud scs-sdk-plugin (revize 12) ve složce `<game>\bin\win_x64\plugins` |
| [EVE Online (soubory logů)](game-eve.md) | log | ne | `%USERPROFILE%\Documents\EVE\logs\Gamelogs\*.txt` a `Chatlogs\*.txt` vedle nich (každý soubor zapsaný od spuštění klienta) |
| [Forza Horizon 4 (živá data)](game-forza-horizon-4.md) | telemetry | ano | Forza Data Out, UDP 127.0.0.1:5300 (formát Dash); každý paket předán beze změny na 127.0.0.1:5301 |
| [Forza Horizon 5 (živá data)](game-forza-horizon-5.md) | telemetry | ano | Forza Data Out, UDP 127.0.0.1:5300 (formát Dash); každý paket předán beze změny na 127.0.0.1:5301 |
| [Forza Horizon 6 (živá data)](game-forza-horizon-6.md) | telemetry | ano | Forza Data Out, UDP 127.0.0.1:5300 (formát Dash); každý paket předán beze změny na 127.0.0.1:5301 |
| [Forza Motorsport (živá data)](game-forza-motorsport.md) | telemetry | ano | Forza Data Out, UDP 127.0.0.1:5300 (formát Dash); každý paket předán beze změny na 127.0.0.1:5301 |
| [Hearthstone (soubory logů)](game-hearthstone.md) | log | ne | `<install>\Logs\Power.log` (nebo `Logs\Hearthstone_*\Power.log`), zapisovaný, jakmile `%LOCALAPPDATA%\Blizzard\Hearthstone\log.config` obsahuje sekci [Power], a každý další `*.log`, který tam hra zapisuje |
| [IL-2 Sturmovik: Great Battles (živá data)](game-il2.md) | telemetry | ne | telemetrický UDP výstup hry na 127.0.0.1:41995 (`KEY = telemetrydevice` v `<game>\data\startup.cfg`) |
| [IL-2 Sturmovik: Great Battles (replaye)](game-il2-tacview.md) | replay | ano | vlastní Tacview nahrávky hry `<game>\data\Tracks\*.acmi` (ACMI 2.x text, prostý nebo zabalený) |
| [iRacing (živá data)](game-iracing.md) | telemetry | ne | sdílená paměť `Local\IRSDKMemMapFileName` (SDK iRacing); soubory .ibt v `%USERPROFILE%\Documents\iRacing\telemetry` |
| [League of Legends (stav hry)](game-lol-live.md) | gsi | ne | Live Client Data API klienta hry, <https://127.0.0.1:2999/liveclientdata/> (allgamedata, eventdata), během zápasu |
| [League of Legends (replaye)](game-lol-replays.md) | replay | ano | replaye, které ukládá klient League: %USERPROFILE%/Documents/League of `Legends/Replays/*.rofl` (jen obyčejná metadata z konce hry); s vlastním klíčem Riot API oficiální časová osa zápasu z Match-V5 API společnosti Riot |
| [Microsoft Flight Simulator 2020 (živá data)](game-msfs2020.md) | telemetry | ano | SimConnect přes vlastní SimConnect.dll hráče (složka simulátoru, nebo `%MSFS_SDK%\SimConnect` `SDK\lib`) |
| [Microsoft Flight Simulator 2024 (živá data)](game-msfs2024.md) | telemetry | ano | SimConnect přes vlastní SimConnect.dll hráče (složka simulátoru, nebo `%MSFS2024_SDK%\SimConnect` `SDK\lib`) |
| [Minecraft (soubory logů)](game-minecraft.md) | log | ano | `%APPDATA%\.minecraft\logs\latest.log` (sledovaný), `saves\<world>\stats\<uuid>.json` a `saves\<world>\playerdata\<uuid>.dat` / level.dat (gzip NBT), čtené, když je hra uloží |
| [NVIDIA highlights (platforma)](game-nvidia-highlights.md) | platform | vypůjčeno | `%LOCALAPPDATA%\NVIDIA` `Corporation\NVIDIA` `Overlay\UGCTracker.json`, GallerySettings.json, `Highlights\<game>\config.json`; klipy ve složce záznamů `(%USERPROFILE%\Videos\NVIDIA\<Game>\*.mp4` a `<temp>\Highlights\<game>`; `%LOCALAPPDATA%\NVIDIA` `Corporation\GfeSDK\<exe>_<pid>.log` |
| [osu! (replaye)](game-osu-replays.md) | replay | ano | replaye, které ukládá osu! (stabilní verze): `%LOCALAPPDATA%/osu!/Data/r/*.osr` (každá hra) a `osu!/Replays/*.osr` (exportované) |
| [Path of Exile (soubory logů)](game-poe.md) | log | ne | `<install>\logs\Client.txt` hry Path of Exile nebo Path of Exile 2 (sledovaný; instalační složka je složka běžícího programu) |
| [Project CARS 2 (živá data)](game-project-cars-2.md) | telemetry | ano | sdílená paměť $pcars2$ (SMS SharedMemory.h) |
| [RaceRoom Racing Experience (živá data)](game-raceroom.md) | telemetry | ano | sdílená paměť $R3E (r3e.h od Sector3, verze 3) |
| [Richard Burns Rally (živá data)](game-richard-burns-rally.md) | telemetry | ano | UDP telemetrie modulu NGP, 127.0.0.1:6776 (RichardBurnsRally.ini [NGP] udpTelemetry=1) |
| [Rocket League (stav hry)](game-rocketleague-stats.md) | gsi | ano | Stats API: TCP proud JSON z 127.0.0.1:49123 (port v `<RL>\TAGame\Config\TAStatsAPI.ini` nebo DefaultStatsAPI.ini) |
| [Squad (replaye)](game-squad-demos.md) | replay | ano | serverová dema, která Squad nahrává administrátorským příkazem AdminDemoRec: `<server>/SquadGame/Saved/Demos/*.replay`, čte je externí čtečka `heat3d-squad-demo` (exporters/ext/squad-demo) |
| [Star Citizen (soubory logů)](game-starcitizen.md) | log | ne | `<install>\StarCitizen\LIVE\Game.log` (složka sestavení běžícího StarCitizen.exe), jen soubor logu, který hra zapisuje – hra s Easy Anti-Cheat: nic se nedotýká jejího procesu |
| [Steam statistics (platforma)](game-steam-stats.md) | platform | ne | místní cache statistik Steamu `%STEAM%\appcache\stats\UserGameStats_<account>_<appid>.bin` se `UserGameStatsSchema_<appid>.bin`; čas hraní z `%STEAM%\userdata\<account>\config\localconfig.vdf` (%STEAM% z `HKCU\Software\Valve\Steam` SteamPath) |
| [Steam Timeline (platforma)](game-steam-timeline.md) | platform | ne | `%STEAM%\userdata\<account>\gamerecordings\timelines\timeline_<appid><date>_<time>.json` |
| [VALORANT (replaye)](game-valorant-replays.md) | replay | ne | replaye, které ukládá VALORANT: `%LOCALAPPDATA%/VALORANT/Saved/Demos/*.vrf` (jen části, které nejsou zakryté) |
| [War Thunder (replaye)](game-warthunder-replays.md) | replay | ano | replaye, které ukládá War Thunder: `<War` `Thunder>/Replays/*.wrpl` (se zapnutým ukládáním replayů), převádí externí převodník `heat3d-wt-replay` (exporters/ext/warthunder-replay) |
| [War Thunder (stav hry)](game-warthunder-webmap.md) | gsi | ano | místní webová mapa hry, <http://127.0.0.1:8111> (/map_info.json, /map_obj.json, /state, /indicators, /hudmsg, /gamechat, /mission.json, /map.img) |
| [World of Tanks (replaye)](game-wot-replays.md) | replay | ano | replaye, které ukládá World of Tanks: `<World` of `Tanks>/replays/*.wotreplay` (se zapnutým nahráváním bitev), převádí externí převodník `heat3d-wot-replay` (exporters/ext/wot-replay) |
| [World of Warships (replaye)](game-wows-replays.md) | replay | ano | replaye, které ukládá World of Warships: `<World` of `Warships>/replays/*.wowsreplay` (se zapnutými replay), převádí externí převodník `heat3d-wows-replay` (exporters/ext/wows-replay) |
| [X-Plane (živá data)](game-xplane.md) | telemetry | ano | UDP rozhraní X-Plane na 127.0.0.1:49000 (datarefy RREF a RPOS, odpovídá Watcheru) |

Hry, které se nenahrávají, a proč: [Zdroje a pravidla](sources-and-rules.md#what-is-declined-and-why). Všechno v jedné tabulce, jak ji vypisuje `python -m heat3d_watch games --markdown`: [Všechny hry v jedné tabulce](watcher.md).

<!-- Vygenerováno nástrojem tools/gen_game_pages.py; po změně adaptéru ho spusťte znovu. -->
