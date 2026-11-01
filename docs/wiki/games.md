
# Games

The watcher knows 45 sources in 42 games and platforms. Each has a page of its own, generated from its adapter: what it records, where from, how to switch it on, how it works, its axes, what was verified.

Kinds: `telemetry`, `gsi`, `log`, `replay` and `platform` - see [Sources and rules](sources-and-rules). Positions: *yes* when the adapter writes rows with a place, *borrowed* when it takes the place from another recording of the same game (see [NVIDIA Highlights](nvidia-highlights)), *no* when the source has none. Memory profiles are not listed: none ship, and each player writes their own (see [Reading memory](memory-reading)).

| Game | Kind | Positions | Source |
|---|---|---|---|
| [American Truck Simulator](game-ats) | telemetry | yes | shared memory Local\SCSTelemetry written by the RenCloud scs-sdk-plugin (revision 12) in &lt;game>\bin\win_x64\plugins |
| [Assetto Corsa](game-assetto-corsa) | telemetry | yes | shared memory Local\acpmf_physics, Local\acpmf_graphics, Local\acpmf_static |
| [Assetto Corsa Competizione](game-assetto-corsa-competizione) | telemetry | yes | shared memory Local\acpmf_physics, Local\acpmf_graphics, Local\acpmf_static |
| [Assetto Corsa EVO](game-assetto-corsa-evo) | telemetry | yes | shared memory Local\acevo_pmf_physics, Local\acevo_pmf_static |
| [Assetto Corsa Rally](game-assetto-corsa-rally) | telemetry | yes | shared memory Local\acpmf_physics, Local\acpmf_static (the same pages as AC and ACC) |
| [Automobilista 2](game-automobilista-2) | telemetry | yes | shared memory $pcars2$ (SMS SharedMemory.h layout) |
| [BeamNG.drive](game-beamng) | telemetry | yes | UDP 127.0.0.1:4460 from the heat3d protocol mod (mods/beamng/heat3d in this repository) |
| [Counter-Strike 2](game-cs2-demos) | replay | yes | demos CS2 saves: &lt;CS2>/game/csgo/replays/\*.dem (downloaded from the match history) and &lt;CS2>/game/csgo/\*.dem (recorded) |
| [Counter-Strike 2](game-cs2-gsi) | gsi | yes | Game State Integration: HTTP POSTs to 127.0.0.1:3311 configured by &lt;CS2>\game\csgo\cfg\gamestate_integration_heat3d.cfg |
| [DCS World](game-dcs) | telemetry | yes | the watcher's hook %USERPROFILE%\Saved Games\DCS\*\Scripts\Hooks\heat3d-watch.lua, UDP lines to 127.0.0.1:41993 |
| [DiRT Rally 2.0](game-dirt-rally-2) | telemetry | yes | UDP 127.0.0.1:20777, extradata=3 (Documents\My Games\DiRT Rally 2.0\hardwaresettings\hardware_settings_config.xml) |
| [Dota 2](game-dota2-gsi) | gsi | yes | Game State Integration: HTTP POSTs to 127.0.0.1:3312 configured by &lt;Dota>\game\dota\cfg\gamestate_integration\gamestate_integration_heat3d.cfg |
| [EA SPORTS F1 23](game-f1-23) | telemetry | yes | UDP telemetry 127.0.0.1:20777 (Documents\My Games\F1 23\hardwaresettings\hardware_settings_config.xml) |
| [EA SPORTS F1 24](game-f1-24) | telemetry | yes | UDP telemetry 127.0.0.1:20777 (Documents\My Games\F1 24\hardwaresettings\hardware_settings_config.xml) |
| [EA SPORTS F1 25](game-f1-25) | telemetry | yes | UDP telemetry 127.0.0.1:20777 (Documents\My Games\F1 25\hardwaresettings\hardware_settings_config.xml) |
| [EA SPORTS WRC](game-ea-wrc) | telemetry | yes | UDP 127.0.0.1:20777, the default `wrc` structure's session_update packet (Documents\My Games\WRC\telemetry\config.json) |
| [Elite Dangerous](game-elite) | log | yes | Player Journal %USERPROFILE%\Saved Games\Frontier Developments\Elite Dangerous\Journal.\*.log (newest file, followed as it is written) and Status.json in the same folder |
| [Euro Truck Simulator 2](game-ets2) | telemetry | yes | shared memory Local\SCSTelemetry written by the RenCloud scs-sdk-plugin (revision 12) in &lt;game>\bin\win_x64\plugins |
| [EVE Online](game-eve) | log | no | %USERPROFILE%\Documents\EVE\logs\Gamelogs\\\*.txt (every file written since the client started) |
| [Forza Horizon 4](game-forza-horizon-4) | telemetry | yes | Forza Data Out, UDP 127.0.0.1:5300 (Dash format); every packet relayed unchanged to 127.0.0.1:5301 |
| [Forza Horizon 5](game-forza-horizon-5) | telemetry | yes | Forza Data Out, UDP 127.0.0.1:5300 (Dash format); every packet relayed unchanged to 127.0.0.1:5301 |
| [Forza Horizon 6](game-forza-horizon-6) | telemetry | yes | Forza Data Out, UDP 127.0.0.1:5300 (Dash format); every packet relayed unchanged to 127.0.0.1:5301 |
| [Forza Motorsport](game-forza-motorsport) | telemetry | yes | Forza Data Out, UDP 127.0.0.1:5300 (Dash format); every packet relayed unchanged to 127.0.0.1:5301 |
| [Hearthstone](game-hearthstone) | log | no | &lt;install>\Logs\Power.log (or Logs\Hearthstone_\*\Power.log), written once %LOCALAPPDATA%\Blizzard\Hearthstone\log.config has a [Power] section |
| [IL-2 Sturmovik: Great Battles](game-il2) | telemetry | no | the game's telemetry UDP output to 127.0.0.1:41995 ([KEY = telemetrydevice] in &lt;game>\data\startup.cfg) |
| [IL-2 Sturmovik: Great Battles](game-il2-tacview) | replay | yes | the game's own Tacview recordings &lt;game>\data\Tracks\\\*.acmi (ACMI 2.x text, plain or zipped) |
| [iRacing](game-iracing) | telemetry | no | shared memory Local\IRSDKMemMapFileName (the iRacing SDK); .ibt files in %USERPROFILE%\Documents\iRacing\telemetry |
| [League of Legends](game-lol-live) | gsi | no | Live Client Data API of the game client, <https://127.0.0.1:2999/liveclientdata/> (allgamedata, eventdata), during a match |
| [League of Legends](game-lol-replays) | replay | yes | replays the League client saves: %USERPROFILE%/Documents/League of Legends/Replays/\*.rofl (the plain end-of-game metadata only); with your own Riot API key, the match's official timeline from Riot's Match-V5 API |
| [Microsoft Flight Simulator 2020](game-msfs2020) | telemetry | yes | SimConnect through the player's own SimConnect.dll (the sim folder, or %MSFS_SDK%\SimConnect SDK\lib) |
| [Microsoft Flight Simulator 2024](game-msfs2024) | telemetry | yes | SimConnect through the player's own SimConnect.dll (the sim folder, or %MSFS2024_SDK%\SimConnect SDK\lib) |
| [Minecraft](game-minecraft) | log | yes | %APPDATA%\\.minecraft\logs\latest.log (followed), saves\\&lt;world>\stats\\&lt;uuid>.json and saves\\&lt;world>\playerdata\\&lt;uuid>.dat / level.dat (gzip NBT), read when the game saves them |
| [NVIDIA highlights](game-nvidia-highlights) | platform | borrowed | %LOCALAPPDATA%\NVIDIA Corporation\NVIDIA Overlay\UGCTracker.json, GallerySettings.json, Highlights\\&lt;game>\config.json; clips in the capture folder (%USERPROFILE%\Videos\NVIDIA\\&lt;Game>\\\*.mp4) and &lt;temp>\Highlights\\&lt;game>; %LOCALAPPDATA%\NVIDIA Corporation\GfeSDK\\&lt;exe>_&lt;pid>.log |
| [osu!](game-osu-replays) | replay | yes | replays osu! (stable) saves: %LOCALAPPDATA%/osu!/Data/r/\*.osr (every play) and osu!/Replays/\*.osr (exported) |
| [Path of Exile](game-poe) | log | no | &lt;install>\logs\Client.txt of Path of Exile or Path of Exile 2 (followed; the install folder is the running executable's) |
| [Project CARS 2](game-project-cars-2) | telemetry | yes | shared memory $pcars2$ (SMS SharedMemory.h) |
| [RaceRoom Racing Experience](game-raceroom) | telemetry | yes | shared memory $R3E (Sector3's r3e.h, version 3) |
| [Richard Burns Rally](game-richard-burns-rally) | telemetry | yes | NGP plugin UDP telemetry, 127.0.0.1:6776 (RichardBurnsRally.ini [NGP] udpTelemetry=1) |
| [Rocket League](game-rocketleague-stats) | gsi | yes | Stats API: TCP JSON stream from 127.0.0.1:49123 (Port in &lt;RL>\TAGame\Config\TAStatsAPI.ini or DefaultStatsAPI.ini) |
| [Star Citizen](game-starcitizen) | log | no | &lt;install>\StarCitizen\LIVE\Game.log (the build folder of the running StarCitizen.exe), only the log file the game writes - an Easy Anti-Cheat game: nothing touches its process |
| [Steam statistics](game-steam-stats) | platform | no | Steam's local stats cache %STEAM%\appcache\stats\UserGameStats_&lt;account>_&lt;appid>.bin with UserGameStatsSchema_&lt;appid>.bin; playtime from %STEAM%\userdata\\&lt;account>\config\localconfig.vdf (%STEAM% from HKCU\Software\Valve\Steam SteamPath) |
| [Steam Timeline](game-steam-timeline) | platform | no | %STEAM%\userdata\\&lt;account>\gamerecordings\timelines\timeline_&lt;appid>&lt;date>_&lt;time>.json |
| [VALORANT](game-valorant-replays) | replay | no | replays VALORANT saves: %LOCALAPPDATA%/VALORANT/Saved/Demos/\*.vrf (only the parts that are not obfuscated) |
| [War Thunder](game-warthunder-webmap) | gsi | yes | the game's local web map, <http://127.0.0.1:8111> (/map_info.json, /map_obj.json, /state, /indicators, /hudmsg) |
| [X-Plane](game-xplane) | telemetry | yes | X-Plane's UDP interface on 127.0.0.1:49000 (RREF datarefs and RPOS position, answered to the watcher) |

Games that are not recorded, and why: [Sources and rules](sources-and-rules#what-is-declined-and-why). Everything in one table, as `python -m heat3d_watch games --markdown` prints it: [All games in one table](watcher).

*Generated by `tools/gen_game_pages.py`; run it again after changing an adapter.*
