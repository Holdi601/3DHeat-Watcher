---
title: "Lojërat"
nav_order: 4
lang: "sq"
source: games.md
source_hash: "c601550fbb4e"
nav_exclude: true
search_exclude: true
---
# Lojërat {#games}

Watcher-i njeh 49 burime në 44 lojëra dhe platforma. Secila ka faqen e vet, të gjeneruar nga adapteri i saj: çfarë regjistron, nga ku, si aktivizohet, si funksionon, boshtet e saj, çfarë u verifikua.

Llojet: `telemetry`, `gsi`, `log`, `replay` dhe `platform` - shih [Burimet dhe rregullat](sources-and-rules.md). Pozicionet: *po* kur adapteri shkruan rreshta me vend, *e huazuar* kur e merr vendin nga një regjistrim tjetër i së njëjtës lojë (shih [Momentet e spikatura të NVIDIA](nvidia-highlights.md)), *jo* kur burimi nuk ka. Profilet e memories nuk listohen: asnjë nuk shpërndahet, dhe çdo lojtar shkruan të vetin (shih [Leximi i memories](memory-reading.md)).

| Loja | Lloji | Pozicionet | Burimi |
|---|---|---|---|
| [American Truck Simulator (të dhëna të drejtpërdrejta)](game-ats.md) | telemetry | po | memorie e përbashkët `Local\SCSTelemetry` e shkruar nga scs-sdk-plugin i RenCloud (rishikimi 12) në `<game>\bin\win_x64\plugins` |
| [Assetto Corsa (të dhëna të drejtpërdrejta)](game-assetto-corsa.md) | telemetry | po | memorie e përbashkët `Local\acpmf_physics`, `Local\acpmf_graphics`, `Local\acpmf_static` |
| [Assetto Corsa Competizione (të dhëna të drejtpërdrejta)](game-assetto-corsa-competizione.md) | telemetry | po | memorie e përbashkët `Local\acpmf_physics`, `Local\acpmf_graphics`, `Local\acpmf_static` |
| [Assetto Corsa EVO (të dhëna të drejtpërdrejta)](game-assetto-corsa-evo.md) | telemetry | po | memorie e përbashkët `Local\acevo_pmf_physics`, `Local\acevo_pmf_static` |
| [Assetto Corsa Rally (të dhëna të drejtpërdrejta)](game-assetto-corsa-rally.md) | telemetry | po | memorie e përbashkët `Local\acpmf_physics`, `Local\acpmf_static` (të njëjtat faqe si AC dhe ACC) |
| [Automobilista 2 (të dhëna të drejtpërdrejta)](game-automobilista-2.md) | telemetry | po | memorie e përbashkët $pcars2$ (struktura SharedMemory.h e SMS) |
| [BeamNG.drive (të dhëna të drejtpërdrejta)](game-beamng.md) | telemetry | po | UDP 127.0.0.1:4460 nga moduli i protokollit heat3d (mods/beamng/heat3d në këtë repo) |
| [Counter-Strike 2 (riluajtjet)](game-cs2-demos.md) | replay | po | demot që ruan CS2: `<CS2>/game/csgo/replays/*.dem` (shkarkuar nga historiku i ndeshjeve) dhe `<CS2>/game/csgo/*.dem` (regjistruar) |
| [Counter-Strike 2 (gjendja e lojës)](game-cs2-gsi.md) | gsi | po | Game State Integration: POST-e HTTP te 127.0.0.1:3311, të konfiguruara nga `<CS2>\game\csgo\cfg\gamestate_integration_heat3d.cfg` |
| [DCS World (të dhëna të drejtpërdrejta)](game-dcs.md) | telemetry | po | hook-u i watcher-it `%USERPROFILE%\Saved` `Games\DCS*\Scripts\Hooks\heat3d-watch.lua`, rreshta UDP te 127.0.0.1:41993 |
| [DiRT Rally 2.0 (të dhëna të drejtpërdrejta)](game-dirt-rally-2.md) | telemetry | po | UDP 127.0.0.1:20777, extradata=3 `(Documents\My` `Games\DiRT` Rally `2.0\hardwaresettings\hardware_settings_config.xml`); sa kohë një aplikacion tjetër mban 20777, watcher-i ia lë portën atij |
| [Dota 2 (riluajtjet)](game-dota-replays.md) | replay | po | riluajtjet që ruan Dota 2: `<Dota>/game/dota/replays/<match id>.dem` (shkarkuar në klient, ose me `dota-replay <match id>`) |
| [Dota 2 (gjendja e lojës)](game-dota2-gsi.md) | gsi | po | Game State Integration: POST-e HTTP te 127.0.0.1:3312, të konfiguruara nga `<Dota>\game\dota\cfg\gamestate_integration\gamestate_integration_heat3d.cfg` |
| [EA SPORTS F1 23 (të dhëna të drejtpërdrejta)](game-f1-23.md) | telemetry | po | telemetri UDP 127.0.0.1:20777 `(Documents\My` `Games\F1` `23\hardwaresettings\hardware_settings_config.xml`) |
| [EA SPORTS F1 24 (të dhëna të drejtpërdrejta)](game-f1-24.md) | telemetry | po | telemetri UDP 127.0.0.1:20777 `(Documents\My` `Games\F1` `24\hardwaresettings\hardware_settings_config.xml`) |
| [EA SPORTS F1 25 (të dhëna të drejtpërdrejta)](game-f1-25.md) | telemetry | po | telemetri UDP 127.0.0.1:20777 `(Documents\My` `Games\F1` `25\hardwaresettings\hardware_settings_config.xml`) |
| [EA SPORTS WRC (të dhëna të drejtpërdrejta)](game-ea-wrc.md) | telemetry | po | UDP 127.0.0.1:20777, paketa session_update e strukturës parazgjedhje `wrc` `(Documents\My` `Games\WRC\telemetry\config.json`); sa kohë një aplikacion tjetër mban 20777, watcher-i ia lë portën atij |
| [Elite Dangerous (skedarët e ditarit)](game-elite.md) | log | po | Player Journal `%USERPROFILE%\Saved` `Games\Frontier` `Developments\Elite` `Dangerous\Journal.*.log` (skedari më i ri, ndiqet ndërsa shkruhet), Status.json dhe skedarët e tjerë shoqërues `*.json` (Market, Outfitting, Shipyard, NavRoute, Cargo, ModulesInfo, ShipLocker, Backpack, FCMaterials) në të njëjtën dosje |
| [Euro Truck Simulator 2 (të dhëna të drejtpërdrejta)](game-ets2.md) | telemetry | po | memorie e përbashkët `Local\SCSTelemetry` e shkruar nga scs-sdk-plugin i RenCloud (rishikimi 12) në `<game>\bin\win_x64\plugins` |
| [EVE Online (skedarët e ditarit)](game-eve.md) | log | jo | `%USERPROFILE%\Documents\EVE\logs\Gamelogs\*.txt` dhe `Chatlogs\*.txt` pranë tyre (çdo skedar i shkruar që nga nisja e klientit) |
| [Forza Horizon 4 (të dhëna të drejtpërdrejta)](game-forza-horizon-4.md) | telemetry | po | Forza Data Out, UDP 127.0.0.1:5300 (formati Dash); çdo paketë e përcjellë e pandryshuar te 127.0.0.1:5301 |
| [Forza Horizon 5 (të dhëna të drejtpërdrejta)](game-forza-horizon-5.md) | telemetry | po | Forza Data Out, UDP 127.0.0.1:5300 (formati Dash); çdo paketë e përcjellë e pandryshuar te 127.0.0.1:5301 |
| [Forza Horizon 6 (të dhëna të drejtpërdrejta)](game-forza-horizon-6.md) | telemetry | po | Forza Data Out, UDP 127.0.0.1:5300 (formati Dash); çdo paketë e përcjellë e pandryshuar te 127.0.0.1:5301 |
| [Forza Motorsport (të dhëna të drejtpërdrejta)](game-forza-motorsport.md) | telemetry | po | Forza Data Out, UDP 127.0.0.1:5300 (formati Dash); çdo paketë e përcjellë e pandryshuar te 127.0.0.1:5301 |
| [Hearthstone (skedarët e ditarit)](game-hearthstone.md) | log | jo | `<install>\Logs\Power.log` (ose `Logs\Hearthstone_*\Power.log`), shkruar sapo `%LOCALAPPDATA%\Blizzard\Hearthstone\log.config` ka një seksion [Power], dhe çdo `*.log` tjetër që shkruan loja aty |
| [IL-2 Sturmovik: Great Battles (të dhëna të drejtpërdrejta)](game-il2.md) | telemetry | jo | dalja UDP e telemetrisë së lojës te 127.0.0.1:41995 ([KEY = telemetrydevice] in `<game>\data\startup.cfg`) |
| [IL-2 Sturmovik: Great Battles (riluajtjet)](game-il2-tacview.md) | replay | po | regjistrimet Tacview të vetë lojës `<game>\data\Tracks\*.acmi` (tekst ACMI 2.x, i thjeshtë ose i zipuar) |
| [iRacing (të dhëna të drejtpërdrejta)](game-iracing.md) | telemetry | jo | memorie e përbashkët `Local\IRSDKMemMapFileName` (iRacing SDK); skedarë .ibt në `%USERPROFILE%\Documents\iRacing\telemetry` |
| [League of Legends (gjendja e lojës)](game-lol-live.md) | gsi | jo | Live Client Data API e klientit të lojës, <https://127.0.0.1:2999/liveclientdata/> (allgamedata, eventdata), gjatë një ndeshjeje |
| [League of Legends (riluajtjet)](game-lol-replays.md) | replay | po | riluajtjet që ruan klienti League: %USERPROFILE%/Documents/League of `Legends/Replays/*.rofl` (vetëm metadatat e thjeshta të fundit të lojës); me çelësin tënd Riot API, afatkohëzimi zyrtar i ndeshjes nga Match-V5 API i Riot |
| [Microsoft Flight Simulator 2020 (të dhëna të drejtpërdrejta)](game-msfs2020.md) | telemetry | po | SimConnect përmes SimConnect.dll të vetë lojtarit (dosja e simulatorit, ose `%MSFS_SDK%\SimConnect` `SDK\lib`) |
| [Microsoft Flight Simulator 2024 (të dhëna të drejtpërdrejta)](game-msfs2024.md) | telemetry | po | SimConnect përmes SimConnect.dll të vetë lojtarit (dosja e simulatorit, ose `%MSFS2024_SDK%\SimConnect` `SDK\lib`) |
| [Minecraft (skedarët e ditarit)](game-minecraft.md) | log | po | `%APPDATA%\.minecraft\logs\latest.log` (ndiqet), `saves\<world>\stats\<uuid>.json` dhe `saves\<world>\playerdata\<uuid>.dat` / level.dat (gzip NBT), lexohen kur i ruan loja |
| [NVIDIA highlights (platformë)](game-nvidia-highlights.md) | platform | e huazuar | `%LOCALAPPDATA%\NVIDIA` `Corporation\NVIDIA` `Overlay\UGCTracker.json`, GallerySettings.json, `Highlights\<game>\config.json`; klipet në dosjen e kapjes `(%USERPROFILE%\Videos\NVIDIA\<Game>\*.mp4`) dhe `<temp>\Highlights\<game>`; `%LOCALAPPDATA%\NVIDIA` `Corporation\GfeSDK\<exe>_<pid>.log` |
| [Path of Exile (skedarët e ditarit)](game-poe.md) | log | jo | `<install>\logs\Client.txt` i Path of Exile ose Path of Exile 2 (ndiqet; dosja e instalimit është ajo e ekzekutueses në punë) |
| [Project CARS 2 (të dhëna të drejtpërdrejta)](game-project-cars-2.md) | telemetry | po | memorie e përbashkët $pcars2$ (SharedMemory.h e SMS) |
| [RaceRoom Racing Experience (të dhëna të drejtpërdrejta)](game-raceroom.md) | telemetry | po | memorie e përbashkët $R3E (r3e.h e Sector3, versioni 3) |
| [Richard Burns Rally (të dhëna të drejtpërdrejta)](game-richard-burns-rally.md) | telemetry | po | telemetri UDP e shtesës NGP, 127.0.0.1:6776 (RichardBurnsRally.ini [NGP] udpTelemetry=1) |
| [Rocket League (gjendja e lojës)](game-rocketleague-stats.md) | gsi | po | Stats API: rrjedhë TCP JSON nga 127.0.0.1:49123 (Porta te `<RL>\TAGame\Config\TAStatsAPI.ini` or DefaultStatsAPI.ini) |
| [Squad (riluajtjet)](game-squad-demos.md) | replay | po | demot e serverit që regjistron Squad me komandën e administratorit AdminDemoRec: `<server>/SquadGame/Saved/Demos/*.replay`, lexuar nga lexuesi i jashtëm `heat3d-squad-demo` (exporters/ext/squad-demo) |
| [Star Citizen (skedarët e ditarit)](game-starcitizen.md) | log | jo | `<install>\StarCitizen\LIVE\Game.log` (dosja e build-it të StarCitizen.exe në punë), vetëm skedari i ditarit që shkruan loja - lojë me Easy Anti-Cheat: asgjë nuk e prek procesin e saj |
| [Steam statistics (platformë)](game-steam-stats.md) | platform | jo | cache-i lokal i statistikave të Steam `%STEAM%\appcache\stats\UserGameStats_<account>_<appid>.bin` me `UserGameStatsSchema_<appid>.bin`; koha e luajtur nga `%STEAM%\userdata\<account>\config\localconfig.vdf` (%STEAM% nga `HKCU\Software\Valve\Steam` SteamPath) |
| [Steam Timeline (platformë)](game-steam-timeline.md) | platform | jo | `%STEAM%\userdata\<account>\gamerecordings\timelines\timeline_<appid><date>_<time>.json` |
| [VALORANT (riluajtjet)](game-valorant-replays.md) | replay | jo | riluajtjet që ruan VALORANT: `%LOCALAPPDATA%/VALORANT/Saved/Demos/*.vrf` (vetëm pjesët që nuk janë të errësuara) |
| [War Thunder (riluajtjet)](game-warthunder-replays.md) | replay | po | riluajtjet që ruan War Thunder: `<War Thunder>/Replays/*.wrpl` (me ruajtjen e riluajtjeve të aktivizuar), konvertuar nga konvertuesi i jashtëm `heat3d-wt-replay` (exporters/ext/warthunder-replay) |
| [War Thunder (gjendja e lojës)](game-warthunder-webmap.md) | gsi | po | harta web lokale e lojës, <http://127.0.0.1:8111> (/map_info.json, /map_obj.json, /state, /indicators, /hudmsg, /gamechat, /mission.json, /map.img) |
| [World of Tanks (riluajtjet)](game-wot-replays.md) | replay | po | riluajtjet që ruan World of Tanks: `<World of Tanks>/replays/*.wotreplay` (me regjistrimin e betejave të aktivizuar), konvertuar nga konvertuesi i jashtëm `heat3d-wot-replay` (exporters/ext/wot-replay) |
| [World of Warships (riluajtjet)](game-wows-replays.md) | replay | po | riluajtjet që ruan World of Warships: `<World of Warships>/replays/*.wowsreplay` (me riluajtjet të aktivizuara), konvertuar nga konvertuesi i jashtëm `heat3d-wows-replay` (exporters/ext/wows-replay) |
| [X-Plane (të dhëna të drejtpërdrejta)](game-xplane.md) | telemetry | po | ndërfaqja UDP e X-Plane te 127.0.0.1:49000 (RREF datarefs dhe pozicioni RPOS, përgjigjur watcher-it) |

Lojërat që nuk regjistrohen, dhe pse: [Burimet dhe rregullat](sources-and-rules.md#what-is-declined-and-why). Gjithçka në një tabelë, siç e printon `python -m heat3d_watch games --markdown`: [Të gjitha lojërat në një tabelë](watcher.md).

<!-- Gjeneruar nga tools/gen_game_pages.py; ekzekutoje përsëri pasi ndryshon një adapter. -->
