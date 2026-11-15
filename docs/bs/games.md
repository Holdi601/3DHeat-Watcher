---
title: "Igre"
nav_order: 4
lang: "bs"
source: games.md
source_hash: "0766c0bb0763"
nav_exclude: true
search_exclude: true
---
# Igre {#games}

Watcher poznaje 50 izvora u 45 igara i platformi. Svaki ima vlastitu stranicu, generiranu iz njegovog adaptera: šta snima, odakle, kako ga uključiti, kako radi, njegove ose, šta je provjereno.

Vrste: `telemetry`, `gsi`, `log`, `replay` i `platform` - vidite [Izvori i pravila](sources-and-rules.md). Pozicije: *da* kad adapter piše redove s mjestom, *posuđeno* kad mjesto uzima iz drugog snimka iste igre (vidite [NVIDIA Highlights](nvidia-highlights.md)), *ne* kad izvor nema nijedno. Profili memorije nisu navedeni: nijedan se ne isporučuje, a svaki igrač piše svoj (vidite [Čitanje memorije](memory-reading.md)).

| Igra | Vrsta | Pozicije | Izvor |
|---|---|---|---|
| [American Truck Simulator (podaci uživo)](game-ats.md) | telemetry | da | dijeljena memorija `Local\SCSTelemetry` koju piše RenCloud scs-sdk-plugin (revizija 12) u `<game>\bin\win_x64\plugins` |
| [Assetto Corsa (podaci uživo)](game-assetto-corsa.md) | telemetry | da | dijeljena memorija `Local\acpmf_physics`, `Local\acpmf_graphics`, `Local\acpmf_static` |
| [Assetto Corsa Competizione (podaci uživo)](game-assetto-corsa-competizione.md) | telemetry | da | dijeljena memorija `Local\acpmf_physics`, `Local\acpmf_graphics`, `Local\acpmf_static` |
| [Assetto Corsa EVO (podaci uživo)](game-assetto-corsa-evo.md) | telemetry | da | dijeljena memorija `Local\acevo_pmf_physics`, `Local\acevo_pmf_static` |
| [Assetto Corsa Rally (podaci uživo)](game-assetto-corsa-rally.md) | telemetry | da | dijeljena memorija `Local\acpmf_physics`, `Local\acpmf_static` (iste stranice kao AC i ACC) |
| [Automobilista 2 (podaci uživo)](game-automobilista-2.md) | telemetry | da | dijeljena memorija $pcars2$ (raspored SMS SharedMemory.h) |
| [BeamNG.drive (podaci uživo)](game-beamng.md) | telemetry | da | UDP 127.0.0.1:4460 iz heat3d protokol moda (mods/beamng/heat3d u ovom repozitoriju) |
| [Counter-Strike 2 (snimci)](game-cs2-demos.md) | replay | da | demoi koje CS2 sprema: `<CS2>/game/csgo/replays/*.dem` (preuzeti iz historije mečeva) i `<CS2>/game/csgo/*.dem` (snimljeni) |
| [Counter-Strike 2 (stanje igre)](game-cs2-gsi.md) | gsi | da | Game State Integration: HTTP POST-ovi na 127.0.0.1:3311 podešeni datotekom `<CS2>\game\csgo\cfg\gamestate_integration_heat3d.cfg` |
| [DCS World (podaci uživo)](game-dcs.md) | telemetry | da | watcherov hook `%USERPROFILE%\Saved` `Games\DCS*\Scripts\Hooks\heat3d-watch.lua`, UDP linije na 127.0.0.1:41993 |
| [DiRT Rally 2.0 (podaci uživo)](game-dirt-rally-2.md) | telemetry | da | UDP 127.0.0.1:20777, extradata=3 `(Documents\My` `Games\DiRT` Rally `2.0\hardwaresettings\hardware_settings_config.xml`); dok port 20777 drži druga aplikacija, watcher joj ostavlja port |
| [Dota 2 (snimci)](game-dota-replays.md) | replay | da | snimci koje Dota 2 sprema: `<Dota>/game/dota/replays/<match id>.dem` (preuzeti u klijentu, ili s `dota-replay <match id>`) |
| [Dota 2 (stanje igre)](game-dota2-gsi.md) | gsi | da | Game State Integration: HTTP POST-ovi na 127.0.0.1:3312 podešeni datotekom `<Dota>\game\dota\cfg\gamestate_integration\gamestate_integration_heat3d.cfg` |
| [EA SPORTS F1 23 (podaci uživo)](game-f1-23.md) | telemetry | da | UDP telemetrija 127.0.0.1:20777 `(Documents\My` `Games\F1` `23\hardwaresettings\hardware_settings_config.xml`) |
| [EA SPORTS F1 24 (podaci uživo)](game-f1-24.md) | telemetry | da | UDP telemetrija 127.0.0.1:20777 `(Documents\My` `Games\F1` `24\hardwaresettings\hardware_settings_config.xml`) |
| [EA SPORTS F1 25 (podaci uživo)](game-f1-25.md) | telemetry | da | UDP telemetrija 127.0.0.1:20777 `(Documents\My` `Games\F1` `25\hardwaresettings\hardware_settings_config.xml`) |
| [EA SPORTS WRC (podaci uživo)](game-ea-wrc.md) | telemetry | da | UDP 127.0.0.1:20777, paket session_update zadane `wrc` strukture `(Documents\My` `Games\WRC\telemetry\config.json`); dok port 20777 drži druga aplikacija, watcher joj ostavlja port |
| [Elite Dangerous (log datoteke)](game-elite.md) | log | da | Player Journal `%USERPROFILE%\Saved` `Games\Frontier` `Developments\Elite` `Dangerous\Journal.*.log` (najnovija datoteka, prati se kako se piše), Status.json i druge prateće `*.json` datoteke (Market, Outfitting, Shipyard, NavRoute, Cargo, ModulesInfo, ShipLocker, Backpack, FCMaterials) u istom folderu |
| [Euro Truck Simulator 2 (podaci uživo)](game-ets2.md) | telemetry | da | dijeljena memorija `Local\SCSTelemetry` koju piše RenCloud scs-sdk-plugin (revizija 12) u `<game>\bin\win_x64\plugins` |
| [EVE Online (log datoteke)](game-eve.md) | log | ne | `%USERPROFILE%\Documents\EVE\logs\Gamelogs\*.txt` i `Chatlogs\*.txt` pored njih (svaka datoteka pisana otkako je klijent pokrenut) |
| [Forza Horizon 4 (podaci uživo)](game-forza-horizon-4.md) | telemetry | da | Forza Data Out, UDP 127.0.0.1:5300 (Dash format); svaki paket prosljeđuje se nepromijenjen na 127.0.0.1:5301 |
| [Forza Horizon 5 (podaci uživo)](game-forza-horizon-5.md) | telemetry | da | Forza Data Out, UDP 127.0.0.1:5300 (Dash format); svaki paket prosljeđuje se nepromijenjen na 127.0.0.1:5301 |
| [Forza Horizon 6 (podaci uživo)](game-forza-horizon-6.md) | telemetry | da | Forza Data Out, UDP 127.0.0.1:5300 (Dash format); svaki paket prosljeđuje se nepromijenjen na 127.0.0.1:5301 |
| [Forza Motorsport (podaci uživo)](game-forza-motorsport.md) | telemetry | da | Forza Data Out, UDP 127.0.0.1:5300 (Dash format); svaki paket prosljeđuje se nepromijenjen na 127.0.0.1:5301 |
| [Hearthstone (log datoteke)](game-hearthstone.md) | log | ne | `<install>\Logs\Power.log` (ili `Logs\Hearthstone_*\Power.log`), piše se kad `%LOCALAPPDATA%\Blizzard\Hearthstone\log.config` ima sekciju [Power], i svaki drugi `*.log` koji igra tamo piše |
| [IL-2 Sturmovik: Great Battles (podaci uživo)](game-il2.md) | telemetry | ne | telemetrijski UDP izlaz igre na 127.0.0.1:41995 ([KEY = telemetrydevice] u `<game>\data\startup.cfg`) |
| [IL-2 Sturmovik: Great Battles (snimci)](game-il2-tacview.md) | replay | da | igrini vlastiti Tacview snimci `<game>\data\Tracks\*.acmi` (ACMI 2.x tekst, običan ili zipovan) |
| [iRacing (podaci uživo)](game-iracing.md) | telemetry | ne | dijeljena memorija `Local\IRSDKMemMapFileName` (iRacing SDK); .ibt datoteke u `%USERPROFILE%\Documents\iRacing\telemetry` |
| [League of Legends (stanje igre)](game-lol-live.md) | gsi | ne | Live Client Data API klijenta igre, <https://127.0.0.1:2999/liveclientdata/> (allgamedata, eventdata), tokom meča |
| [League of Legends (snimci)](game-lol-replays.md) | replay | da | snimci koje League klijent sprema: %USERPROFILE%/Documents/League of `Legends/Replays/*.rofl` (samo običan metapodatak s kraja igre); s vašim vlastitim Riot API ključem, službena vremenska linija meča iz Riotovog Match-V5 API-ja |
| [Microsoft Flight Simulator 2020 (podaci uživo)](game-msfs2020.md) | telemetry | da | SimConnect preko igračevog vlastitog SimConnect.dll (folder simulatora, ili `%MSFS_SDK%\SimConnect` `SDK\lib`) |
| [Microsoft Flight Simulator 2024 (podaci uživo)](game-msfs2024.md) | telemetry | da | SimConnect preko igračevog vlastitog SimConnect.dll (folder simulatora, ili `%MSFS2024_SDK%\SimConnect` `SDK\lib`) |
| [Minecraft (log datoteke)](game-minecraft.md) | log | da | `%APPDATA%\.minecraft\logs\latest.log` (prati se), `saves\<world>\stats\<uuid>.json` i `saves\<world>\playerdata\<uuid>.dat` / level.dat (gzip NBT), čitaju se kad ih igra sprema |
| [NVIDIA highlights (platforma)](game-nvidia-highlights.md) | platform | posuđeno | `%LOCALAPPDATA%\NVIDIA` `Corporation\NVIDIA` `Overlay\UGCTracker.json`, GallerySettings.json, `Highlights\<game>\config.json`; klipovi u folderu snimanja `(%USERPROFILE%\Videos\NVIDIA\<Game>\*.mp4`) i `<temp>\Highlights\<game>`; `%LOCALAPPDATA%\NVIDIA` `Corporation\GfeSDK\<exe>_<pid>.log` |
| [osu! (snimci)](game-osu-replays.md) | replay | da | snimci koje osu! (stable) sprema: `%LOCALAPPDATA%/osu!/Data/r/*.osr` (svaka igra) i `osu!/Replays/*.osr` (izvezeni) |
| [Path of Exile (log datoteke)](game-poe.md) | log | ne | `<install>\logs\Client.txt` igre Path of Exile ili Path of Exile 2 (prati se; instalacijski folder je folder izvršne datoteke koja radi) |
| [Project CARS 2 (podaci uživo)](game-project-cars-2.md) | telemetry | da | dijeljena memorija $pcars2$ (SMS SharedMemory.h) |
| [RaceRoom Racing Experience (podaci uživo)](game-raceroom.md) | telemetry | da | dijeljena memorija $R3E (Sector3-ov r3e.h, verzija 3) |
| [Richard Burns Rally (podaci uživo)](game-richard-burns-rally.md) | telemetry | da | UDP telemetrija NGP plugina, 127.0.0.1:6776 (RichardBurnsRally.ini [NGP] udpTelemetry=1) |
| [Rocket League (stanje igre)](game-rocketleague-stats.md) | gsi | da | Stats API: TCP JSON tok sa 127.0.0.1:49123 (port u `<RL>\TAGame\Config\TAStatsAPI.ini` ili DefaultStatsAPI.ini) |
| [Squad (snimci)](game-squad-demos.md) | replay | da | serverski demoi koje Squad snima admin komandom AdminDemoRec: `<server>/SquadGame/Saved/Demos/*.replay`, čita ih vanjski čitač `heat3d-squad-demo` (exporters/ext/squad-demo) |
| [Star Citizen (log datoteke)](game-starcitizen.md) | log | ne | `<install>\StarCitizen\LIVE\Game.log` (folder builda pokrenutog StarCitizen.exe), samo log datoteka koju igra piše - igra s Easy Anti-Cheat: ništa ne dira njen proces |
| [Steam statistike (platforma)](game-steam-stats.md) | platform | ne | Steamov lokalni keš statistika `%STEAM%\appcache\stats\UserGameStats_<account>_<appid>.bin` s `UserGameStatsSchema_<appid>.bin`; vrijeme igranja iz `%STEAM%\userdata\<account>\config\localconfig.vdf` (%STEAM% iz `HKCU\Software\Valve\Steam` SteamPath) |
| [Steam Timeline (platforma)](game-steam-timeline.md) | platform | ne | `%STEAM%\userdata\<account>\gamerecordings\timelines\timeline_<appid><date>_<time>.json` |
| [VALORANT (snimci)](game-valorant-replays.md) | replay | ne | snimci koje VALORANT sprema: `%LOCALAPPDATA%/VALORANT/Saved/Demos/*.vrf` (samo dijelovi koji nisu obfuscirani) |
| [War Thunder (snimci)](game-warthunder-replays.md) | replay | da | snimci koje War Thunder sprema: `<War Thunder>/Replays/*.wrpl` (uz uključeno spremanje snimaka), pretvara ih vanjski konverter `heat3d-wt-replay` (exporters/ext/warthunder-replay) |
| [War Thunder (stanje igre)](game-warthunder-webmap.md) | gsi | da | lokalna web mapa igre, <http://127.0.0.1:8111> (/map_info.json, /map_obj.json, /state, /indicators, /hudmsg, /gamechat, /mission.json, /map.img) |
| [World of Tanks (snimci)](game-wot-replays.md) | replay | da | snimci koje World of Tanks sprema: `<World of Tanks>/replays/*.wotreplay` (uz uključeno snimanje bitaka), pretvara ih vanjski konverter `heat3d-wot-replay` (exporters/ext/wot-replay) |
| [World of Warships (snimci)](game-wows-replays.md) | replay | da | snimci koje World of Warships sprema: `<World of Warships>/replays/*.wowsreplay` (uz uključene snimke), pretvara ih vanjski konverter `heat3d-wows-replay` (exporters/ext/wows-replay) |
| [X-Plane (podaci uživo)](game-xplane.md) | telemetry | da | X-Planeov UDP interfejs na 127.0.0.1:49000 (RREF datarefi i RPOS pozicija, odgovara se watcheru) |

Igre koje se ne snimaju, i zašto: [Izvori i pravila](sources-and-rules.md#what-is-declined-and-why). Sve u jednoj tabeli, kako je ispisuje `python -m heat3d_watch games --markdown`: [Sve igre u jednoj tabeli](watcher.md).

<!-- Generated by tools/gen_game_pages.py; run it again after changing an adapter. -->
