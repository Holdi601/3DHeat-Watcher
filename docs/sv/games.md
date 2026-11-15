---
title: Spel
nav_order: 4
lang: "sv"
source: games.md
source_hash: "c601550fbb4e"
nav_exclude: true
search_exclude: true
---
# Spel {#games}

Watchern känner till 49 källor i 44 spel och plattformar. Varje har en egen sida, genererad från dess adapter: vad den spelar in, varifrån, hur man slår på den, hur den fungerar, dess axlar, vad som verifierats.

Typer: `telemetry`, `gsi`, `log`, `replay` och `platform` - se [Källor och regler](sources-and-rules.md). Positioner: *ja* när adaptern skriver rader med en plats, *lånad* när den tar platsen från en annan inspelning av samma spel (se [NVIDIA Highlights](nvidia-highlights.md)), *nej* när källan saknar den. Minnesprofiler listas inte: inga levereras, och varje spelare skriver sina egna (se [Läsa minne](memory-reading.md)).

| Spel | Typ | Positioner | Källa |
|---|---|---|---|
| [American Truck Simulator (livedata)](game-ats.md) | telemetry | ja | delat minne `Local\SCSTelemetry`, skrivet av RenCloud scs-sdk-plugin (revision 12) i `<game>\bin\win_x64\plugins` |
| [Assetto Corsa (livedata)](game-assetto-corsa.md) | telemetry | ja | delat minne `Local\acpmf_physics`, `Local\acpmf_graphics`, `Local\acpmf_static` |
| [Assetto Corsa Competizione (livedata)](game-assetto-corsa-competizione.md) | telemetry | ja | delat minne `Local\acpmf_physics`, `Local\acpmf_graphics`, `Local\acpmf_static` |
| [Assetto Corsa EVO (livedata)](game-assetto-corsa-evo.md) | telemetry | ja | delat minne `Local\acevo_pmf_physics`, `Local\acevo_pmf_static` |
| [Assetto Corsa Rally (livedata)](game-assetto-corsa-rally.md) | telemetry | ja | delat minne `Local\acpmf_physics`, `Local\acpmf_static` (samma sidor som AC och ACC) |
| [Automobilista 2 (livedata)](game-automobilista-2.md) | telemetry | ja | delat minne $pcars2$ (SMS SharedMemory.h-layouten) |
| [BeamNG.drive (livedata)](game-beamng.md) | telemetry | ja | UDP 127.0.0.1:4460 från heat3d-protokollmodden (mods/beamng/heat3d i det här repositoryt) |
| [Counter-Strike 2 (replayer)](game-cs2-demos.md) | replay | ja | demos som CS2 sparar: `<CS2>/game/csgo/replays/*.dem` (nedladdade från matchhistoriken) och `<CS2>/game/csgo/*.dem` (inspelade) |
| [Counter-Strike 2 (spelstatus)](game-cs2-gsi.md) | gsi | ja | Game State Integration: HTTP-POST till 127.0.0.1:3311, inställt i `<CS2>\game\csgo\cfg\gamestate_integration_heat3d.cfg` |
| [DCS World (livedata)](game-dcs.md) | telemetry | ja | watcherns hook `%USERPROFILE%\Saved` `Games\DCS*\Scripts\Hooks\heat3d-watch.lua`, UDP-rader till 127.0.0.1:41993 |
| [DiRT Rally 2.0 (livedata)](game-dirt-rally-2.md) | telemetry | ja | UDP 127.0.0.1:20777, extradata=3 `(Documents\My` `Games\DiRT` Rally `2.0\hardwaresettings\hardware_settings_config.xml`); medan ett annat program har 20777 lämnar watchern porten åt det |
| [Dota 2 (replayer)](game-dota-replays.md) | replay | ja | replayer som Dota 2 sparar: `<Dota>/game/dota/replays/<match id>.dem` (nedladdade i klienten, eller med `dota-replay <match id>`) |
| [Dota 2 (spelstatus)](game-dota2-gsi.md) | gsi | ja | Game State Integration: HTTP-POST till 127.0.0.1:3312, inställt i `<Dota>\game\dota\cfg\gamestate_integration\gamestate_integration_heat3d.cfg` |
| [EA SPORTS F1 23 (livedata)](game-f1-23.md) | telemetry | ja | UDP-telemetri 127.0.0.1:20777 `(Documents\My` `Games\F1` `23\hardwaresettings\hardware_settings_config.xml`) |
| [EA SPORTS F1 24 (livedata)](game-f1-24.md) | telemetry | ja | UDP-telemetri 127.0.0.1:20777 `(Documents\My` `Games\F1` `24\hardwaresettings\hardware_settings_config.xml`) |
| [EA SPORTS F1 25 (livedata)](game-f1-25.md) | telemetry | ja | UDP-telemetri 127.0.0.1:20777 `(Documents\My` `Games\F1` `25\hardwaresettings\hardware_settings_config.xml`) |
| [EA SPORTS WRC (livedata)](game-ea-wrc.md) | telemetry | ja | UDP 127.0.0.1:20777, standardstrukturen `wrc`:s session_update-paket `(Documents\My` `Games\WRC\telemetry\config.json`); medan ett annat program har 20777 lämnar watchern porten åt det |
| [Elite Dangerous (loggfiler)](game-elite.md) | log | ja | Player Journal `%USERPROFILE%\Saved` `Games\Frontier` `Developments\Elite` `Dangerous\Journal.*.log` (nyaste filen, följd medan den skrivs), Status.json och de andra companion-`*.json`-filerna (Market, Outfitting, Shipyard, NavRoute, Cargo, ModulesInfo, ShipLocker, Backpack, FCMaterials) i samma mapp |
| [Euro Truck Simulator 2 (livedata)](game-ets2.md) | telemetry | ja | delat minne `Local\SCSTelemetry`, skrivet av RenCloud scs-sdk-plugin (revision 12) i `<game>\bin\win_x64\plugins` |
| [EVE Online (loggfiler)](game-eve.md) | log | nej | `%USERPROFILE%\Documents\EVE\logs\Gamelogs\*.txt` och `Chatlogs\*.txt` bredvid dem (varje fil skriven sedan klienten startade) |
| [Forza Horizon 4 (livedata)](game-forza-horizon-4.md) | telemetry | ja | Forza Data Out, UDP 127.0.0.1:5300 (Dash-format); varje paket vidarebefordras oförändrat till 127.0.0.1:5301 |
| [Forza Horizon 5 (livedata)](game-forza-horizon-5.md) | telemetry | ja | Forza Data Out, UDP 127.0.0.1:5300 (Dash-format); varje paket vidarebefordras oförändrat till 127.0.0.1:5301 |
| [Forza Horizon 6 (livedata)](game-forza-horizon-6.md) | telemetry | ja | Forza Data Out, UDP 127.0.0.1:5300 (Dash-format); varje paket vidarebefordras oförändrat till 127.0.0.1:5301 |
| [Forza Motorsport (livedata)](game-forza-motorsport.md) | telemetry | ja | Forza Data Out, UDP 127.0.0.1:5300 (Dash-format); varje paket vidarebefordras oförändrat till 127.0.0.1:5301 |
| [Hearthstone (loggfiler)](game-hearthstone.md) | log | nej | `<install>\Logs\Power.log` (eller `Logs\Hearthstone_*\Power.log`), skriven när `%LOCALAPPDATA%\Blizzard\Hearthstone\log.config` har en [Power]-sektion, och varje annan `*.log` som spelet skriver där |
| [IL-2 Sturmovik: Great Battles (livedata)](game-il2.md) | telemetry | nej | spelets telemetri-UDP-utdata till 127.0.0.1:41995 ([KEY = telemetrydevice] i `<game>\data\startup.cfg`) |
| [IL-2 Sturmovik: Great Battles (replayer)](game-il2-tacview.md) | replay | ja | spelets egna Tacview-inspelningar `<game>\data\Tracks\*.acmi` (ACMI 2.x-text, vanlig eller zippad) |
| [iRacing (livedata)](game-iracing.md) | telemetry | nej | delat minne `Local\IRSDKMemMapFileName` (iRacing SDK); .ibt-filer i `%USERPROFILE%\Documents\iRacing\telemetry` |
| [League of Legends (spelstatus)](game-lol-live.md) | gsi | nej | Live Client Data API i spelklienten, <https://127.0.0.1:2999/liveclientdata/> (allgamedata, eventdata), under en match |
| [League of Legends (replayer)](game-lol-replays.md) | replay | ja | replayer som League-klienten sparar: %USERPROFILE%/Documents/League of `Legends/Replays/*.rofl` (bara den vanliga metadatan i slutet av spelet); med din egen Riot API-nyckel matchens officiella tidslinje från Riots Match-V5 API |
| [Microsoft Flight Simulator 2020 (livedata)](game-msfs2020.md) | telemetry | ja | SimConnect genom spelarens egen SimConnect.dll (simulatorns mapp, eller `%MSFS_SDK%\SimConnect` `SDK\lib`) |
| [Microsoft Flight Simulator 2024 (livedata)](game-msfs2024.md) | telemetry | ja | SimConnect genom spelarens egen SimConnect.dll (simulatorns mapp, eller `%MSFS2024_SDK%\SimConnect` `SDK\lib`) |
| [Minecraft (loggfiler)](game-minecraft.md) | log | ja | `%APPDATA%\.minecraft\logs\latest.log` (följd), `saves\<world>\stats\<uuid>.json` och `saves\<world>\playerdata\<uuid>.dat` / level.dat (gzip NBT), lästa när spelet sparar dem |
| [NVIDIA highlights (plattform)](game-nvidia-highlights.md) | platform | lånad | `%LOCALAPPDATA%\NVIDIA` `Corporation\NVIDIA` `Overlay\UGCTracker.json`, GallerySettings.json, `Highlights\<game>\config.json`; klipp i inspelningsmappen `(%USERPROFILE%\Videos\NVIDIA\<Game>\*.mp4`) och `<temp>\Highlights\<game>`; `%LOCALAPPDATA%\NVIDIA` `Corporation\GfeSDK\<exe>_<pid>.log` |
| [Path of Exile (loggfiler)](game-poe.md) | log | nej | `<install>\logs\Client.txt` i Path of Exile eller Path of Exile 2 (följd; installationsmappen är den körande programfilens) |
| [Project CARS 2 (livedata)](game-project-cars-2.md) | telemetry | ja | delat minne $pcars2$ (SMS SharedMemory.h) |
| [RaceRoom Racing Experience (livedata)](game-raceroom.md) | telemetry | ja | delat minne $R3E (Sector3:s r3e.h, version 3) |
| [Richard Burns Rally (livedata)](game-richard-burns-rally.md) | telemetry | ja | NGP-pluginets UDP-telemetri, 127.0.0.1:6776 (RichardBurnsRally.ini [NGP] udpTelemetry=1) |
| [Rocket League (spelstatus)](game-rocketleague-stats.md) | gsi | ja | Stats API: TCP-JSON-ström från 127.0.0.1:49123 (porten i `<RL>\TAGame\Config\TAStatsAPI.ini` eller DefaultStatsAPI.ini) |
| [Squad (replayer)](game-squad-demos.md) | replay | ja | serverdemos som Squad spelar in med adminkommandot AdminDemoRec: `<server>/SquadGame/Saved/Demos/*.replay`, lästa av den externa läsaren `heat3d-squad-demo` (exporters/ext/squad-demo) |
| [Star Citizen (loggfiler)](game-starcitizen.md) | log | nej | `<install>\StarCitizen\LIVE\Game.log` (byggmappen för den körande StarCitizen.exe), bara loggfilen som spelet skriver - ett Easy Anti-Cheat-spel: ingenting rör dess process |
| [Steam-statistik (plattform)](game-steam-stats.md) | platform | nej | Steams lokala statistikcache `%STEAM%\appcache\stats\UserGameStats_<account>_<appid>.bin` med `UserGameStatsSchema_<appid>.bin`; speltid från `%STEAM%\userdata\<account>\config\localconfig.vdf` (%STEAM% från `HKCU\Software\Valve\Steam` SteamPath) |
| [Steam Timeline (plattform)](game-steam-timeline.md) | platform | nej | `%STEAM%\userdata\<account>\gamerecordings\timelines\timeline_<appid><date>_<time>.json` |
| [VALORANT (replayer)](game-valorant-replays.md) | replay | nej | replayer som VALORANT sparar: `%LOCALAPPDATA%/VALORANT/Saved/Demos/*.vrf` (bara de delar som inte är förvrängda) |
| [War Thunder (replayer)](game-warthunder-replays.md) | replay | ja | replayer som War Thunder sparar: `<War Thunder>/Replays/*.wrpl` (med replaysparning på), omvandlade av den externa omvandlaren `heat3d-wt-replay` (exporters/ext/warthunder-replay) |
| [War Thunder (spelstatus)](game-warthunder-webmap.md) | gsi | ja | spelets lokala webbkarta, <http://127.0.0.1:8111> (/map_info.json, /map_obj.json, /state, /indicators, /hudmsg, /gamechat, /mission.json, /map.img) |
| [World of Tanks (replayer)](game-wot-replays.md) | replay | ja | replayer som World of Tanks sparar: `<World of Tanks>/replays/*.wotreplay` (med stridsinspelning på), omvandlade av den externa omvandlaren `heat3d-wot-replay` (exporters/ext/wot-replay) |
| [World of Warships (replayer)](game-wows-replays.md) | replay | ja | replayer som World of Warships sparar: `<World of Warships>/replays/*.wowsreplay` (med replayer på), omvandlade av den externa omvandlaren `heat3d-wows-replay` (exporters/ext/wows-replay) |
| [X-Plane (livedata)](game-xplane.md) | telemetry | ja | X-Planes UDP-gränssnitt på 127.0.0.1:49000 (RREF-datarefs och RPOS-position, besvarade till watchern) |

Spel som inte spelas in, och varför: [Källor och regler](sources-and-rules.md#what-is-declined-and-why). Allt i en tabell, så som `python -m heat3d_watch games --markdown` skriver ut det: [Alla spel i en tabell](watcher.md).

<!-- Generated by tools/gen_game_pages.py; run it again after changing an adapter. -->
