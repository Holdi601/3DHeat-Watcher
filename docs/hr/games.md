---
title: "Igre"
nav_order: 4
lang: "hr"
source: games.md
source_hash: "0766c0bb0763"
nav_exclude: true
search_exclude: true
---
# Igre {#games}

Watcher poznaje 50 izvora u 45 igara i platformi. Svaka ima vlastitu stranicu, generiranu iz njezina adaptera: što bilježi, odakle, kako je uključiti, kako radi, koje su osi, što je provjereno.

Vrste: `telemetry`, `gsi`, `log`, `replay` i `platform` - vidi [Izvori i pravila](sources-and-rules.md). Pozicije: *da* kad adapter piše retke s mjestom, *posuđeno* kad je mjesto uzeto iz druge snimke iste igre (vidi [NVIDIA Highlights](nvidia-highlights.md)), *ne* kad izvor nema mjesta. Profili memorije nisu navedeni: nijedan se ne isporučuje, a svaki igrač piše svoj (vidi [Čitanje memorije](memory-reading.md)).

| Igra | Vrsta | Pozicije | Izvor |
|---|---|---|---|
| [American Truck Simulator (živi podaci)](game-ats.md) | telemetry | da | dijeljena memorija `Local\SCSTelemetry` koju piše RenCloud scs-sdk-plugin (revizija 12) u `<game>\bin\win_x64\plugins` |
| [Assetto Corsa (živi podaci)](game-assetto-corsa.md) | telemetry | da | dijeljena memorija `Local\acpmf_physics`, `Local\acpmf_graphics`, `Local\acpmf_static` |
| [Assetto Corsa Competizione (živi podaci)](game-assetto-corsa-competizione.md) | telemetry | da | dijeljena memorija `Local\acpmf_physics`, `Local\acpmf_graphics`, `Local\acpmf_static` |
| [Assetto Corsa EVO (živi podaci)](game-assetto-corsa-evo.md) | telemetry | da | dijeljena memorija `Local\acevo_pmf_physics`, `Local\acevo_pmf_static` |
| [Assetto Corsa Rally (živi podaci)](game-assetto-corsa-rally.md) | telemetry | da | dijeljena memorija `Local\acpmf_physics`, `Local\acpmf_static` (iste stranice kao AC i ACC) |
| [Automobilista 2 (živi podaci)](game-automobilista-2.md) | telemetry | da | dijeljena memorija $pcars2$ (raspored SMS SharedMemory.h) |
| [BeamNG.drive (živi podaci)](game-beamng.md) | telemetry | da | UDP 127.0.0.1:4460 iz heat3d protokol moda (mods/beamng/heat3d u ovom repozitoriju) |
| [Counter-Strike 2 (replay-i)](game-cs2-demos.md) | replay | da | demo snimke koje CS2 sprema: `<CS2>/game/csgo/replays/*.dem` (preuzete iz povijesti utakmica) i `<CS2>/game/csgo/*.dem` (snimljene) |
| [Counter-Strike 2 (stanje igre)](game-cs2-gsi.md) | gsi | da | Game State Integration: HTTP POST zahtjevi na 127.0.0.1:3311, podešeni datotekom `<CS2>\game\csgo\cfg\gamestate_integration_heat3d.cfg` |
| [DCS World (živi podaci)](game-dcs.md) | telemetry | da | watcherov hook `%USERPROFILE%\Saved` `Games\DCS*\Scripts\Hooks\heat3d-watch.lua`, UDP redovi na 127.0.0.1:41993 |
| [DiRT Rally 2.0 (živi podaci)](game-dirt-rally-2.md) | telemetry | da | UDP 127.0.0.1:20777, extradata=3 `(Documents\My` `Games\DiRT` Rally `2.0\hardwaresettings\hardware_settings_config.xml`); dok druga aplikacija drži 20777, watcher port prepušta njoj |
| [Dota 2 (replay-i)](game-dota-replays.md) | replay | da | replayi koje sprema Dota 2: `<Dota>/game/dota/replays/<match id>.dem` (preuzeti u klijentu, ili naredbom `dota-replay <match id>`) |
| [Dota 2 (stanje igre)](game-dota2-gsi.md) | gsi | da | Game State Integration: HTTP POST zahtjevi na 127.0.0.1:3312, podešeni datotekom `<Dota>\game\dota\cfg\gamestate_integration\gamestate_integration_heat3d.cfg` |
| [EA SPORTS F1 23 (živi podaci)](game-f1-23.md) | telemetry | da | UDP telemetrija 127.0.0.1:20777 `(Documents\My` `Games\F1` `23\hardwaresettings\hardware_settings_config.xml`) |
| [EA SPORTS F1 24 (živi podaci)](game-f1-24.md) | telemetry | da | UDP telemetrija 127.0.0.1:20777 `(Documents\My` `Games\F1` `24\hardwaresettings\hardware_settings_config.xml`) |
| [EA SPORTS F1 25 (živi podaci)](game-f1-25.md) | telemetry | da | UDP telemetrija 127.0.0.1:20777 `(Documents\My` `Games\F1` `25\hardwaresettings\hardware_settings_config.xml`) |
| [EA SPORTS WRC (živi podaci)](game-ea-wrc.md) | telemetry | da | UDP 127.0.0.1:20777, paket session_update zadane strukture `wrc` `(Documents\My` `Games\WRC\telemetry\config.json`); dok druga aplikacija drži 20777, watcher port prepušta njoj |
| [Elite Dangerous (datoteke dnevnika)](game-elite.md) | log | da | Player Journal `%USERPROFILE%\Saved` `Games\Frontier` `Developments\Elite` `Dangerous\Journal.*.log` (najnovija datoteka, prati se dok se piše), Status.json i ostale `*.json` pomoćne datoteke (Market, Outfitting, Shipyard, NavRoute, Cargo, ModulesInfo, ShipLocker, Backpack, FCMaterials) u istoj mapi |
| [Euro Truck Simulator 2 (živi podaci)](game-ets2.md) | telemetry | da | dijeljena memorija `Local\SCSTelemetry` koju piše RenCloud scs-sdk-plugin (revizija 12) u `<game>\bin\win_x64\plugins` |
| [EVE Online (datoteke dnevnika)](game-eve.md) | log | ne | `%USERPROFILE%\Documents\EVE\logs\Gamelogs\*.txt` i `Chatlogs\*.txt` pored njih (svaka datoteka napisana otkad je klijent pokrenut) |
| [Forza Horizon 4 (živi podaci)](game-forza-horizon-4.md) | telemetry | da | Forza Data Out, UDP 127.0.0.1:5300 (Dash format); svaki paket prosljeđen nepromijenjen na 127.0.0.1:5301 |
| [Forza Horizon 5 (živi podaci)](game-forza-horizon-5.md) | telemetry | da | Forza Data Out, UDP 127.0.0.1:5300 (Dash format); svaki paket prosljeđen nepromijenjen na 127.0.0.1:5301 |
| [Forza Horizon 6 (živi podaci)](game-forza-horizon-6.md) | telemetry | da | Forza Data Out, UDP 127.0.0.1:5300 (Dash format); svaki paket prosljeđen nepromijenjen na 127.0.0.1:5301 |
| [Forza Motorsport (živi podaci)](game-forza-motorsport.md) | telemetry | da | Forza Data Out, UDP 127.0.0.1:5300 (Dash format); svaki paket prosljeđen nepromijenjen na 127.0.0.1:5301 |
| [Hearthstone (datoteke dnevnika)](game-hearthstone.md) | log | ne | `<install>\Logs\Power.log` (ili `Logs\Hearthstone_*\Power.log`), piše se kad `%LOCALAPPDATA%\Blizzard\Hearthstone\log.config` ima odjeljak [Power], i svaka ostala `*.log` datoteka koju igra tamo piše |
| [IL-2 Sturmovik: Great Battles (živi podaci)](game-il2.md) | telemetry | ne | telemetrijski UDP izlaz igre na 127.0.0.1:41995 (`KEY = telemetrydevice` u `<game>\data\startup.cfg`) |
| [IL-2 Sturmovik: Great Battles (replay-i)](game-il2-tacview.md) | replay | da | vlastite Tacview snimke igre `<game>\data\Tracks\*.acmi` (ACMI 2.x tekst, običan ili zipan) |
| [iRacing (živi podaci)](game-iracing.md) | telemetry | ne | dijeljena memorija `Local\IRSDKMemMapFileName` (iRacing SDK); .ibt datoteke u `%USERPROFILE%\Documents\iRacing\telemetry` |
| [League of Legends (stanje igre)](game-lol-live.md) | gsi | ne | Live Client Data API klijenta igre, <https://127.0.0.1:2999/liveclientdata/> (allgamedata, eventdata), tijekom utakmice |
| [League of Legends (replay-i)](game-lol-replays.md) | replay | da | replayi koje sprema League klijent: %USERPROFILE%/Documents/League of `Legends/Replays/*.rofl` (samo obični metapodaci na kraju igre); uz vlastiti Riot API ključ, službena vremenska crta utakmice iz Riotova Match-V5 API-ja |
| [Microsoft Flight Simulator 2020 (živi podaci)](game-msfs2020.md) | telemetry | da | SimConnect preko vlastite datoteke SimConnect.dll igrača (mapa simulatora, ili `%MSFS_SDK%\SimConnect` `SDK\lib`) |
| [Microsoft Flight Simulator 2024 (živi podaci)](game-msfs2024.md) | telemetry | da | SimConnect preko vlastite datoteke SimConnect.dll igrača (mapa simulatora, ili `%MSFS2024_SDK%\SimConnect` `SDK\lib`) |
| [Minecraft (datoteke dnevnika)](game-minecraft.md) | log | da | `%APPDATA%\.minecraft\logs\latest.log` (prati se), `saves\<world>\stats\<uuid>.json` i `saves\<world>\playerdata\<uuid>.dat` / level.dat (gzip NBT), čitano kad ih igra spremi |
| [NVIDIA highlights (platforma)](game-nvidia-highlights.md) | platform | posuđeno | `%LOCALAPPDATA%\NVIDIA` `Corporation\NVIDIA` `Overlay\UGCTracker.json`, GallerySettings.json, `Highlights\<game>\config.json`; isječci u mapi za snimanje `(%USERPROFILE%\Videos\NVIDIA\<Game>\*.mp4`) i `<temp>\Highlights\<game>`; `%LOCALAPPDATA%\NVIDIA` `Corporation\GfeSDK\<exe>_<pid>.log` |
| [osu! (replay-i)](game-osu-replays.md) | replay | da | replayi koje sprema osu! (stabilna verzija): `%LOCALAPPDATA%/osu!/Data/r/*.osr` (svaka igra) i `osu!/Replays/*.osr` (izvezeni) |
| [Path of Exile (datoteke dnevnika)](game-poe.md) | log | ne | `<install>\logs\Client.txt` igre Path of Exile ili Path of Exile 2 (prati se; mapa instalacije je mapa pokrenute izvršne datoteke) |
| [Project CARS 2 (živi podaci)](game-project-cars-2.md) | telemetry | da | dijeljena memorija $pcars2$ (SMS SharedMemory.h) |
| [RaceRoom Racing Experience (živi podaci)](game-raceroom.md) | telemetry | da | dijeljena memorija $R3E (Sector3-ov r3e.h, verzija 3) |
| [Richard Burns Rally (živi podaci)](game-richard-burns-rally.md) | telemetry | da | UDP telemetrija NGP dodatka, 127.0.0.1:6776 (RichardBurnsRally.ini [NGP] udpTelemetry=1) |
| [Rocket League (stanje igre)](game-rocketleague-stats.md) | gsi | da | Stats API: TCP JSON tok s 127.0.0.1:49123 (port u `<RL>\TAGame\Config\TAStatsAPI.ini` ili DefaultStatsAPI.ini) |
| [Squad (replay-i)](game-squad-demos.md) | replay | da | demo snimke poslužitelja koje Squad bilježi naredbom administratora AdminDemoRec: `<server>/SquadGame/Saved/Demos/*.replay`, čita ih vanjski čitač `heat3d-squad-demo` (exporters/ext/squad-demo) |
| [Star Citizen (datoteke dnevnika)](game-starcitizen.md) | log | ne | `<install>\StarCitizen\LIVE\Game.log` (mapa izgradnje pokrenutog StarCitizen.exe), samo datoteka zapisnika koju igra piše - igra sa Easy Anti-Cheat: ništa ne dira njezin proces |
| [Steam statistika (platforma)](game-steam-stats.md) | platform | ne | Steamova lokalna predmemorija statistike `%STEAM%\appcache\stats\UserGameStats_<account>_<appid>.bin` uz `UserGameStatsSchema_<appid>.bin`; vrijeme igranja iz `%STEAM%\userdata\<account>\config\localconfig.vdf` (%STEAM% iz `HKCU\Software\Valve\Steam` SteamPath) |
| [Steam Timeline (platforma)](game-steam-timeline.md) | platform | ne | `%STEAM%\userdata\<account>\gamerecordings\timelines\timeline_<appid><date>_<time>.json` |
| [VALORANT (replay-i)](game-valorant-replays.md) | replay | ne | replayi koje sprema VALORANT: `%LOCALAPPDATA%/VALORANT/Saved/Demos/*.vrf` (samo dijelovi koji nisu zamagljeni) |
| [War Thunder (replay-i)](game-warthunder-replays.md) | replay | da | replayi koje sprema War Thunder: `<War Thunder>/Replays/*.wrpl` (uz uključeno spremanje replaya), pretvara ih vanjski pretvarač `heat3d-wt-replay` (exporters/ext/warthunder-replay) |
| [War Thunder (stanje igre)](game-warthunder-webmap.md) | gsi | da | lokalna web karta igre, <http://127.0.0.1:8111> (/map_info.json, /map_obj.json, /state, /indicators, /hudmsg, /gamechat, /mission.json, /map.img) |
| [World of Tanks (replay-i)](game-wot-replays.md) | replay | da | replayi koje sprema World of Tanks: `<World of Tanks>/replays/*.wotreplay` (uz uključeno snimanje bitaka), pretvara ih vanjski pretvarač `heat3d-wot-replay` (exporters/ext/wot-replay) |
| [World of Warships (replay-i)](game-wows-replays.md) | replay | da | replayi koje sprema World of Warships: `<World of Warships>/replays/*.wowsreplay` (uz uključene replaye), pretvara ih vanjski pretvarač `heat3d-wows-replay` (exporters/ext/wows-replay) |
| [X-Plane (živi podaci)](game-xplane.md) | telemetry | da | UDP sučelje X-Planea na 127.0.0.1:49000 (RREF datarefi i RPOS pozicija, odgovara watcheru) |

Igre koje se ne bilježe, i zašto: [Izvori i pravila](sources-and-rules.md#what-is-declined-and-why). Sve u jednoj tablici, kako ga ispisuje `python -m heat3d_watch games --markdown`: [Sve igre u jednoj tablici](watcher.md).

<!-- Generated by tools/gen_game_pages.py; run it again after changing an adapter. -->
