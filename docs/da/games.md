---
title: Spil
nav_order: 4
lang: "da"
source: games.md
source_hash: "c601550fbb4e"
nav_exclude: true
search_exclude: true
---
# Spil {#games}

Watcheren kender 49 kilder i 44 spil og platforme. Hver har sin egen side, genereret ud fra dens adapter: hvad den optager, hvor det kommer fra, hvordan den slås til, hvordan den virker, dens akser, og hvad der er verificeret.

Slags: `telemetry`, `gsi`, `log`, `replay` og `platform` - se [Kilder og regler](sources-and-rules.md). Positioner: *ja* når adapteren skriver rækker med et sted, *lånt* når den tager stedet fra en anden optagelse af samme spil (se [NVIDIA Highlights](nvidia-highlights.md)), *nej* når kilden ikke har nogen. Hukommelsesprofiler står ikke på listen: ingen leveres, og hver spiller skriver sin egen (se [Læsning af hukommelse](memory-reading.md)).

| Spil | Slags | Positioner | Kilde |
|---|---|---|---|
| [American Truck Simulator (live-data)](game-ats.md) | telemetry | ja | delt hukommelse `Local\SCSTelemetry`, skrevet af RenCloud scs-sdk-plugin (revision 12) i `<game>\bin\win_x64\plugins` |
| [Assetto Corsa (live-data)](game-assetto-corsa.md) | telemetry | ja | delt hukommelse `Local\acpmf_physics`, `Local\acpmf_graphics`, `Local\acpmf_static` |
| [Assetto Corsa Competizione (live-data)](game-assetto-corsa-competizione.md) | telemetry | ja | delt hukommelse `Local\acpmf_physics`, `Local\acpmf_graphics`, `Local\acpmf_static` |
| [Assetto Corsa EVO (live-data)](game-assetto-corsa-evo.md) | telemetry | ja | delt hukommelse `Local\acevo_pmf_physics`, `Local\acevo_pmf_static` |
| [Assetto Corsa Rally (live-data)](game-assetto-corsa-rally.md) | telemetry | ja | delt hukommelse `Local\acpmf_physics`, `Local\acpmf_static` (de samme sider som AC og ACC) |
| [Automobilista 2 (live-data)](game-automobilista-2.md) | telemetry | ja | delt hukommelse $pcars2$ (SMS SharedMemory.h-layout) |
| [BeamNG.drive (live-data)](game-beamng.md) | telemetry | ja | UDP 127.0.0.1:4460 fra heat3d-protokolmodden (mods/beamng/heat3d i dette repository) |
| [Counter-Strike 2 (replays)](game-cs2-demos.md) | replay | ja | demoer CS2 gemmer: `<CS2>/game/csgo/replays/*.dem` (hentet fra kamphistorikken) og `<CS2>/game/csgo/*.dem` (optaget) |
| [Counter-Strike 2 (spiltilstand)](game-cs2-gsi.md) | gsi | ja | Game State Integration: HTTP-POST'er til 127.0.0.1:3311, sat op af `<CS2>\game\csgo\cfg\gamestate_integration_heat3d.cfg` |
| [DCS World (live-data)](game-dcs.md) | telemetry | ja | watcherens hook `%USERPROFILE%\Saved` `Games\DCS*\Scripts\Hooks\heat3d-watch.lua`, UDP-linjer til 127.0.0.1:41993 |
| [DiRT Rally 2.0 (live-data)](game-dirt-rally-2.md) | telemetry | ja | UDP 127.0.0.1:20777, extradata=3 `(Documents\My` `Games\DiRT` Rally `2.0\hardwaresettings\hardware_settings_config.xml`); mens et andet program holder 20777, lader watcheren porten være til det |
| [Dota 2 (replays)](game-dota-replays.md) | replay | ja | replays Dota 2 gemmer: `<Dota>/game/dota/replays/<match id>.dem` (hentet i klienten, eller med `dota-replay <match id>`) |
| [Dota 2 (spiltilstand)](game-dota2-gsi.md) | gsi | ja | Game State Integration: HTTP-POST'er til 127.0.0.1:3312, sat op af `<Dota>\game\dota\cfg\gamestate_integration\gamestate_integration_heat3d.cfg` |
| [EA SPORTS F1 23 (live-data)](game-f1-23.md) | telemetry | ja | UDP-telemetri 127.0.0.1:20777 `(Documents\My` `Games\F1` `23\hardwaresettings\hardware_settings_config.xml`) |
| [EA SPORTS F1 24 (live-data)](game-f1-24.md) | telemetry | ja | UDP-telemetri 127.0.0.1:20777 `(Documents\My` `Games\F1` `24\hardwaresettings\hardware_settings_config.xml`) |
| [EA SPORTS F1 25 (live-data)](game-f1-25.md) | telemetry | ja | UDP-telemetri 127.0.0.1:20777 `(Documents\My` `Games\F1` `25\hardwaresettings\hardware_settings_config.xml`) |
| [EA SPORTS WRC (live-data)](game-ea-wrc.md) | telemetry | ja | UDP 127.0.0.1:20777, standardstrukturen `wrc`s session_update-pakke `(Documents\My` `Games\WRC\telemetry\config.json`); mens et andet program holder 20777, lader watcheren porten være til det |
| [Elite Dangerous (logfiler)](game-elite.md) | log | ja | Player Journal `%USERPROFILE%\Saved` `Games\Frontier` `Developments\Elite` `Dangerous\Journal.*.log` (nyeste fil, fulgt mens den skrives), Status.json og de andre companion-`*.json`-filer (Market, Outfitting, Shipyard, NavRoute, Cargo, ModulesInfo, ShipLocker, Backpack, FCMaterials) i samme mappe |
| [Euro Truck Simulator 2 (live-data)](game-ets2.md) | telemetry | ja | delt hukommelse `Local\SCSTelemetry`, skrevet af RenCloud scs-sdk-plugin (revision 12) i `<game>\bin\win_x64\plugins` |
| [EVE Online (logfiler)](game-eve.md) | log | nej | `%USERPROFILE%\Documents\EVE\logs\Gamelogs\*.txt` og `Chatlogs\*.txt` ved siden af (hver fil skrevet siden klienten startede) |
| [Forza Horizon 4 (live-data)](game-forza-horizon-4.md) | telemetry | ja | Forza Data Out, UDP 127.0.0.1:5300 (Dash-format); hver pakke videresendes uændret til 127.0.0.1:5301 |
| [Forza Horizon 5 (live-data)](game-forza-horizon-5.md) | telemetry | ja | Forza Data Out, UDP 127.0.0.1:5300 (Dash-format); hver pakke videresendes uændret til 127.0.0.1:5301 |
| [Forza Horizon 6 (live-data)](game-forza-horizon-6.md) | telemetry | ja | Forza Data Out, UDP 127.0.0.1:5300 (Dash-format); hver pakke videresendes uændret til 127.0.0.1:5301 |
| [Forza Motorsport (live-data)](game-forza-motorsport.md) | telemetry | ja | Forza Data Out, UDP 127.0.0.1:5300 (Dash-format); hver pakke videresendes uændret til 127.0.0.1:5301 |
| [Hearthstone (logfiler)](game-hearthstone.md) | log | nej | `<install>\Logs\Power.log` (eller `Logs\Hearthstone_*\Power.log`), skrevet når `%LOCALAPPDATA%\Blizzard\Hearthstone\log.config` har et [Power]-afsnit, og enhver anden `*.log`, spillet skriver der |
| [IL-2 Sturmovik: Great Battles (live-data)](game-il2.md) | telemetry | nej | spillets telemetri-UDP-output til 127.0.0.1:41995 ([KEY = telemetrydevice] i `<game>\data\startup.cfg`) |
| [IL-2 Sturmovik: Great Battles (replays)](game-il2-tacview.md) | replay | ja | spillets egne Tacview-optagelser `<game>\data\Tracks\*.acmi` (ACMI 2.x-tekst, almindelig eller zippet) |
| [iRacing (live-data)](game-iracing.md) | telemetry | nej | delt hukommelse `Local\IRSDKMemMapFileName` (iRacing SDK); .ibt-filer i `%USERPROFILE%\Documents\iRacing\telemetry` |
| [League of Legends (spiltilstand)](game-lol-live.md) | gsi | nej | Live Client Data API i spilklienten, <https://127.0.0.1:2999/liveclientdata/> (allgamedata, eventdata), under en kamp |
| [League of Legends (replays)](game-lol-replays.md) | replay | ja | replays League-klienten gemmer: %USERPROFILE%/Documents/League of `Legends/Replays/*.rofl` (kun de simple slutdata for kampen); med din egen Riot API-nøgle, kampens officielle tidslinje fra Riots Match-V5 API |
| [Microsoft Flight Simulator 2020 (live-data)](game-msfs2020.md) | telemetry | ja | SimConnect gennem spillerens egen SimConnect.dll (simulatorens mappe, eller `%MSFS_SDK%\SimConnect` `SDK\lib`) |
| [Microsoft Flight Simulator 2024 (live-data)](game-msfs2024.md) | telemetry | ja | SimConnect gennem spillerens egen SimConnect.dll (simulatorens mappe, eller `%MSFS2024_SDK%\SimConnect` `SDK\lib`) |
| [Minecraft (logfiler)](game-minecraft.md) | log | ja | `%APPDATA%\.minecraft\logs\latest.log` (fulgt), `saves\<world>\stats\<uuid>.json` og `saves\<world>\playerdata\<uuid>.dat` / level.dat (gzip NBT), læst når spillet gemmer dem |
| [NVIDIA highlights (platform)](game-nvidia-highlights.md) | platform | lånt | `%LOCALAPPDATA%\NVIDIA` `Corporation\NVIDIA` `Overlay\UGCTracker.json`, GallerySettings.json, `Highlights\<game>\config.json`; klip i optagemappen `(%USERPROFILE%\Videos\NVIDIA\<Game>\*.mp4`) og `<temp>\Highlights\<game>`; `%LOCALAPPDATA%\NVIDIA` `Corporation\GfeSDK\<exe>_<pid>.log` |
| [Path of Exile (logfiler)](game-poe.md) | log | nej | `<install>\logs\Client.txt` i Path of Exile eller Path of Exile 2 (fulgt; installationsmappen er den kørende programfils) |
| [Project CARS 2 (live-data)](game-project-cars-2.md) | telemetry | ja | delt hukommelse $pcars2$ (SMS SharedMemory.h) |
| [RaceRoom Racing Experience (live-data)](game-raceroom.md) | telemetry | ja | delt hukommelse $R3E (Sector3's r3e.h, version 3) |
| [Richard Burns Rally (live-data)](game-richard-burns-rally.md) | telemetry | ja | NGP-plugin UDP-telemetri, 127.0.0.1:6776 (RichardBurnsRally.ini [NGP] udpTelemetry=1) |
| [Rocket League (spiltilstand)](game-rocketleague-stats.md) | gsi | ja | Stats API: TCP JSON-strøm fra 127.0.0.1:49123 (port i `<RL>\TAGame\Config\TAStatsAPI.ini` eller DefaultStatsAPI.ini) |
| [Squad (replays)](game-squad-demos.md) | replay | ja | serverdemoer Squad optager med admin-kommandoen AdminDemoRec: `<server>/SquadGame/Saved/Demos/*.replay`, læst af den eksterne læser `heat3d-squad-demo` (exporters/ext/squad-demo) |
| [Star Citizen (logfiler)](game-starcitizen.md) | log | nej | `<install>\StarCitizen\LIVE\Game.log` (build-mappen for den kørende StarCitizen.exe), kun logfilen spillet skriver - et Easy Anti-Cheat-spil: intet rører dets proces |
| [Steam-statistik (platform)](game-steam-stats.md) | platform | nej | Steams lokale statistik-cache `%STEAM%\appcache\stats\UserGameStats_<account>_<appid>.bin` med `UserGameStatsSchema_<appid>.bin`; spilletid fra `%STEAM%\userdata\<account>\config\localconfig.vdf` (%STEAM% fra `HKCU\Software\Valve\Steam` SteamPath) |
| [Steam Timeline (platform)](game-steam-timeline.md) | platform | nej | `%STEAM%\userdata\<account>\gamerecordings\timelines\timeline_<appid><date>_<time>.json` |
| [VALORANT (replays)](game-valorant-replays.md) | replay | nej | replays VALORANT gemmer: `%LOCALAPPDATA%/VALORANT/Saved/Demos/*.vrf` (kun de dele, der ikke er slørede) |
| [War Thunder (replays)](game-warthunder-replays.md) | replay | ja | replays War Thunder gemmer: `<War Thunder>/Replays/*.wrpl` (med replay-optagelse slået til), konverteret af den eksterne konverter `heat3d-wt-replay` (exporters/ext/warthunder-replay) |
| [War Thunder (spiltilstand)](game-warthunder-webmap.md) | gsi | ja | spillets lokale webkort, <http://127.0.0.1:8111> (/map_info.json, /map_obj.json, /state, /indicators, /hudmsg, /gamechat, /mission.json, /map.img) |
| [World of Tanks (replays)](game-wot-replays.md) | replay | ja | replays World of Tanks gemmer: `<World of Tanks>/replays/*.wotreplay` (med kampoptagelse slået til), konverteret af den eksterne konverter `heat3d-wot-replay` (exporters/ext/wot-replay) |
| [World of Warships (replays)](game-wows-replays.md) | replay | ja | replays World of Warships gemmer: `<World of Warships>/replays/*.wowsreplay` (med replays slået til), konverteret af den eksterne konverter `heat3d-wows-replay` (exporters/ext/wows-replay) |
| [X-Plane (live-data)](game-xplane.md) | telemetry | ja | X-Planes UDP-grænseflade på 127.0.0.1:49000 (RREF-datarefs og RPOS-position, besvaret til watcheren) |

Spil der ikke optages, og hvorfor: [Kilder og regler](sources-and-rules.md#what-is-declined-and-why). Alt i én tabel, som `python -m heat3d_watch games --markdown` udskriver: [Alle spil i én tabel](watcher.md).

<!-- Generated by tools/gen_game_pages.py; run it again after changing an adapter. -->
