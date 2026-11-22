---
title: Games
nav_order: 4
has_children: true
---

# Games

The watcher knows 50 sources in 45 games and platforms. Each has a page of its own, generated from its adapter: what it records, where from, how to switch it on, how it works, its axes, what was verified.

Kinds: `telemetry`, `gsi`, `log`, `replay` and `platform` - see [Sources and rules](sources-and-rules.md). Positions: *yes* when the adapter writes rows with a place, *borrowed* when it takes the place from another recording of the same game (see [NVIDIA Highlights](nvidia-highlights.md)), *no* when the source has none. Memory profiles are not listed: none ship, and each player writes their own (see [Reading memory](memory-reading.md)).

| Game | Kind | Positions | Source |
|---|---|---|---|
| [American Truck Simulator (live data)](game-ats.md) | telemetry | yes | shared memory `Local\SCSTelemetry` written by the RenCloud scs-sdk-plugin (revision 12) in `<game>\bin\win_x64\plugins` |
| [Assetto Corsa (live data)](game-assetto-corsa.md) | telemetry | yes | shared memory `Local\acpmf_physics`, `Local\acpmf_graphics`, `Local\acpmf_static` |
| [Assetto Corsa Competizione (live data)](game-assetto-corsa-competizione.md) | telemetry | yes | shared memory `Local\acpmf_physics`, `Local\acpmf_graphics`, `Local\acpmf_static` |
| [Assetto Corsa EVO (live data)](game-assetto-corsa-evo.md) | telemetry | yes | shared memory `Local\acevo_pmf_physics`, `Local\acevo_pmf_static` |
| [Assetto Corsa Rally (live data)](game-assetto-corsa-rally.md) | telemetry | yes | shared memory `Local\acpmf_physics`, `Local\acpmf_static` (the same pages as AC and ACC) |
| [Automobilista 2 (live data)](game-automobilista-2.md) | telemetry | yes | shared memory $pcars2$ (SMS SharedMemory.h layout) |
| [BeamNG.drive (live data)](game-beamng.md) | telemetry | yes | UDP 127.0.0.1:4460 from the heat3d protocol mod (mods/beamng/heat3d in this repository) |
| [Counter-Strike 2 (replays)](game-cs2-demos.md) | replay | yes | demos CS2 saves: `<CS2>/game/csgo/replays/*.dem` (downloaded from the match history) and `<CS2>/game/csgo/*.dem` (recorded) |
| [Counter-Strike 2 (game state)](game-cs2-gsi.md) | gsi | yes | Game State Integration: HTTP POSTs to 127.0.0.1:3311 configured by `<CS2>\game\csgo\cfg\gamestate_integration_heat3d.cfg` |
| [DCS World (live data)](game-dcs.md) | telemetry | yes | the watcher's hook `%USERPROFILE%\Saved` `Games\DCS*\Scripts\Hooks\heat3d-watch.lua`, UDP lines to 127.0.0.1:41993 |
| [DiRT Rally 2.0 (live data)](game-dirt-rally-2.md) | telemetry | yes | UDP 127.0.0.1:20777, extradata=3 `(Documents\My` `Games\DiRT` Rally `2.0\hardwaresettings\hardware_settings_config.xml`); while another app holds 20777 the watcher leaves the port to it |
| [Dota 2 (replays)](game-dota-replays.md) | replay | yes | replays Dota 2 saves: `<Dota>/game/dota/replays/<match id>.dem` (downloaded in the client, or with `dota-replay <match id>`) |
| [Dota 2 (game state)](game-dota2-gsi.md) | gsi | yes | Game State Integration: HTTP POSTs to 127.0.0.1:3312 configured by `<Dota>\game\dota\cfg\gamestate_integration\gamestate_integration_heat3d.cfg` |
| [EA SPORTS F1 23 (live data)](game-f1-23.md) | telemetry | yes | UDP telemetry 127.0.0.1:20777 `(Documents\My` `Games\F1` `23\hardwaresettings\hardware_settings_config.xml`) |
| [EA SPORTS F1 24 (live data)](game-f1-24.md) | telemetry | yes | UDP telemetry 127.0.0.1:20777 `(Documents\My` `Games\F1` `24\hardwaresettings\hardware_settings_config.xml`) |
| [EA SPORTS F1 25 (live data)](game-f1-25.md) | telemetry | yes | UDP telemetry 127.0.0.1:20777 `(Documents\My` `Games\F1` `25\hardwaresettings\hardware_settings_config.xml`) |
| [EA SPORTS WRC (live data)](game-ea-wrc.md) | telemetry | yes | UDP 127.0.0.1:20777, the default `wrc` structure's session_update packet `(Documents\My` `Games\WRC\telemetry\config.json`); while another app holds 20777 the watcher leaves the port to it |
| [Elite Dangerous (log files)](game-elite.md) | log | yes | Player Journal `%USERPROFILE%\Saved` `Games\Frontier` `Developments\Elite` `Dangerous\Journal.*.log` (newest file, followed as it is written), Status.json and the other companion `*.json` files (Market, Outfitting, Shipyard, NavRoute, Cargo, ModulesInfo, ShipLocker, Backpack, FCMaterials) in the same folder |
| [Euro Truck Simulator 2 (live data)](game-ets2.md) | telemetry | yes | shared memory `Local\SCSTelemetry` written by the RenCloud scs-sdk-plugin (revision 12) in `<game>\bin\win_x64\plugins` |
| [EVE Online (log files)](game-eve.md) | log | no | `%USERPROFILE%\Documents\EVE\logs\Gamelogs\*.txt` and the `Chatlogs\*.txt` beside them (every file written since the client started) |
| [Forza Horizon 4 (live data)](game-forza-horizon-4.md) | telemetry | yes | Forza Data Out, UDP 127.0.0.1:5300 (Dash format); every packet relayed unchanged to 127.0.0.1:5301 |
| [Forza Horizon 5 (live data)](game-forza-horizon-5.md) | telemetry | yes | Forza Data Out, UDP 127.0.0.1:5300 (Dash format); every packet relayed unchanged to 127.0.0.1:5301 |
| [Forza Horizon 6 (live data)](game-forza-horizon-6.md) | telemetry | yes | Forza Data Out, UDP 127.0.0.1:5300 (Dash format); every packet relayed unchanged to 127.0.0.1:5301 |
| [Forza Motorsport (live data)](game-forza-motorsport.md) | telemetry | yes | Forza Data Out, UDP 127.0.0.1:5300 (Dash format); every packet relayed unchanged to 127.0.0.1:5301 |
| [Gunner, HEAT, PC! (log files)](game-ghpc.md) | log | yes | the 3DHeat recorder, a MelonLoader mod (mods/ghpc) the player installs: one .3dheat file a mission in %LOCALAPPDATA%/3DHeat/Watcher/recorders/ghpc, which the viewer opens directly |
| [Hearthstone (log files)](game-hearthstone.md) | log | no | `<install>\Logs\Power.log` (or `Logs\Hearthstone_*\Power.log`), written once `%LOCALAPPDATA%\Blizzard\Hearthstone\log.config` has a [Power] section, and every other `*.log` the game writes there |
| [IL-2 Sturmovik: Great Battles (live data)](game-il2.md) | telemetry | no | the game's telemetry UDP output to 127.0.0.1:41995 ([KEY = telemetrydevice] in `<game>\data\startup.cfg`) |
| [IL-2 Sturmovik: Great Battles (replays)](game-il2-tacview.md) | replay | yes | the game's own Tacview recordings `<game>\data\Tracks\*.acmi` (ACMI 2.x text, plain or zipped) |
| [iRacing (live data)](game-iracing.md) | telemetry | no | shared memory `Local\IRSDKMemMapFileName` (the iRacing SDK); .ibt files in `%USERPROFILE%\Documents\iRacing\telemetry` |
| [League of Legends (game state)](game-lol-live.md) | gsi | no | Live Client Data API of the game client, <https://127.0.0.1:2999/liveclientdata/> (allgamedata, eventdata), during a match |
| [League of Legends (replays)](game-lol-replays.md) | replay | yes | replays the League client saves: %USERPROFILE%/Documents/League of `Legends/Replays/*.rofl` (the plain end-of-game metadata only); with your own Riot API key, the match's official timeline from Riot's Match-V5 API |
| [Microsoft Flight Simulator 2020 (live data)](game-msfs2020.md) | telemetry | yes | SimConnect through the player's own SimConnect.dll (the sim folder, or `%MSFS_SDK%\SimConnect` `SDK\lib`) |
| [Microsoft Flight Simulator 2024 (live data)](game-msfs2024.md) | telemetry | yes | SimConnect through the player's own SimConnect.dll (the sim folder, or `%MSFS2024_SDK%\SimConnect` `SDK\lib`) |
| [Minecraft (log files)](game-minecraft.md) | log | yes | `%APPDATA%\.minecraft\logs\latest.log` (followed), `saves\<world>\stats\<uuid>.json` and `saves\<world>\playerdata\<uuid>.dat` / level.dat (gzip NBT), read when the game saves them |
| [NVIDIA highlights (platform)](game-nvidia-highlights.md) | platform | borrowed | `%LOCALAPPDATA%\NVIDIA` `Corporation\NVIDIA` `Overlay\UGCTracker.json`, GallerySettings.json, `Highlights\<game>\config.json`; clips in the capture folder `(%USERPROFILE%\Videos\NVIDIA\<Game>\*.mp4`) and `<temp>\Highlights\<game>`; `%LOCALAPPDATA%\NVIDIA` `Corporation\GfeSDK\<exe>_<pid>.log` |
| [Path of Exile (log files)](game-poe.md) | log | no | `<install>\logs\Client.txt` of Path of Exile or Path of Exile 2 (followed; the install folder is the running executable's) |
| [Project CARS 2 (live data)](game-project-cars-2.md) | telemetry | yes | shared memory $pcars2$ (SMS SharedMemory.h) |
| [RaceRoom Racing Experience (live data)](game-raceroom.md) | telemetry | yes | shared memory $R3E (Sector3's r3e.h, version 3) |
| [Richard Burns Rally (live data)](game-richard-burns-rally.md) | telemetry | yes | NGP plugin UDP telemetry, 127.0.0.1:6776 (RichardBurnsRally.ini [NGP] udpTelemetry=1) |
| [Rocket League (game state)](game-rocketleague-stats.md) | gsi | yes | Stats API: TCP JSON stream from 127.0.0.1:49123 (Port in `<RL>\TAGame\Config\TAStatsAPI.ini` or DefaultStatsAPI.ini) |
| [Squad (replays)](game-squad-demos.md) | replay | yes | server demos Squad records with the admin command AdminDemoRec: `<server>/SquadGame/Saved/Demos/*.replay`, read by the external reader `heat3d-squad-demo` (exporters/ext/squad-demo) |
| [Star Citizen (log files)](game-starcitizen.md) | log | no | `<install>\StarCitizen\LIVE\Game.log` (the build folder of the running StarCitizen.exe), only the log file the game writes - an Easy Anti-Cheat game: nothing touches its process |
| [Steam statistics (platform)](game-steam-stats.md) | platform | no | Steam's local stats cache `%STEAM%\appcache\stats\UserGameStats_<account>_<appid>.bin` with `UserGameStatsSchema_<appid>.bin`; playtime from `%STEAM%\userdata\<account>\config\localconfig.vdf` (%STEAM% from `HKCU\Software\Valve\Steam` SteamPath) |
| [Steam Timeline (platform)](game-steam-timeline.md) | platform | no | `%STEAM%\userdata\<account>\gamerecordings\timelines\timeline_<appid><date>_<time>.json` |
| [VALORANT (replays)](game-valorant-replays.md) | replay | no | replays VALORANT saves: `%LOCALAPPDATA%/VALORANT/Saved/Demos/*.vrf` (only the parts that are not obfuscated) |
| [War Thunder (replays)](game-warthunder-replays.md) | replay | yes | replays War Thunder saves: `<War Thunder>/Replays/*.wrpl` (with replay saving on), converted by the external converter `heat3d-wt-replay` (exporters/ext/warthunder-replay) |
| [War Thunder (game state)](game-warthunder-webmap.md) | gsi | yes | the game's local web map, <http://127.0.0.1:8111> (/map_info.json, /map_obj.json, /state, /indicators, /hudmsg, /gamechat, /mission.json, /map.img) |
| [World of Tanks (replays)](game-wot-replays.md) | replay | yes | replays World of Tanks saves: `<World of Tanks>/replays/*.wotreplay` (with battle recording on), converted by the external converter `heat3d-wot-replay` (exporters/ext/wot-replay) |
| [World of Warships (replays)](game-wows-replays.md) | replay | yes | replays World of Warships saves: `<World of Warships>/replays/*.wowsreplay` (with replays on), converted by the external converter `heat3d-wows-replay` (exporters/ext/wows-replay) |
| [X-Plane (live data)](game-xplane.md) | telemetry | yes | X-Plane's UDP interface on 127.0.0.1:49000 (RREF datarefs and RPOS position, answered to the watcher) |

Games that are not recorded, and why: [Sources and rules](sources-and-rules.md#what-is-declined-and-why). Everything in one table, as `python -m heat3d_watch games --markdown` prints it: [All games in one table](watcher.md).

<!-- Generated by tools/gen_game_pages.py; run it again after changing an adapter. -->
