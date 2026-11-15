---
title: Játékok
nav_order: 4
lang: "hu"
source: games.md
source_hash: "0766c0bb0763"
nav_exclude: true
search_exclude: true
---
# Játékok {#games}

A watcher 45 játékból és platformból 50 forrást ismer. Mindegyiknek saját oldala van, az adapterének kódjából generálva: mit rögzít, honnan, hogyan kell bekapcsolni, hogyan működik, a tengelyei és mi lett ellenőrizve.

Típusok: `telemetry`, `gsi`, `log`, `replay` és `platform` – lásd [Források és szabályok](sources-and-rules.md). Pozíciók: *igen*, ha az adapter helyes sorokat ír; *kölcsönzött*, ha a helyet egy másik, ugyanarról a játékról készült felvétel adja (lásd [NVIDIA Highlights](nvidia-highlights.md)); *nincs*, ha a forrásnak nincs helye. A memóriaprofilok nincsenek felsorolva: egy sem jön a csomaggal, és mindenki maga írja meg a sajátját (lásd [Memória olvasása](memory-reading.md)).

| Játék | Típus | Pozíciók | Forrás |
|---|---|---|---|
| [American Truck Simulator (élő adatok)](game-ats.md) | telemetry | igen | megosztott memória `Local\SCSTelemetry`, amelyet a RenCloud scs-sdk-plugin (12-es revízió) ír a `<game>\bin\win_x64\plugins` mappában |
| [Assetto Corsa (élő adatok)](game-assetto-corsa.md) | telemetry | igen | megosztott memória `Local\acpmf_physics`, `Local\acpmf_graphics`, `Local\acpmf_static` |
| [Assetto Corsa Competizione (élő adatok)](game-assetto-corsa-competizione.md) | telemetry | igen | megosztott memória `Local\acpmf_physics`, `Local\acpmf_graphics`, `Local\acpmf_static` |
| [Assetto Corsa EVO (élő adatok)](game-assetto-corsa-evo.md) | telemetry | igen | megosztott memória `Local\acevo_pmf_physics`, `Local\acevo_pmf_static` |
| [Assetto Corsa Rally (élő adatok)](game-assetto-corsa-rally.md) | telemetry | igen | megosztott memória `Local\acpmf_physics`, `Local\acpmf_static` (ugyanazok a lapok, mint az AC és ACC esetén) |
| [Automobilista 2 (élő adatok)](game-automobilista-2.md) | telemetry | igen | megosztott memória $pcars2$ (SMS SharedMemory.h kiosztás) |
| [BeamNG.drive (élő adatok)](game-beamng.md) | telemetry | igen | UDP 127.0.0.1:4460, a heat3d protokollmodból (a mods/beamng/heat3d mappa ebben a tárolóban) |
| [Counter-Strike 2 (visszajátszások)](game-cs2-demos.md) | replay | igen | a CS2 által mentett demók: `<CS2>/game/csgo/replays/*.dem` (a meccselőzményekből letöltve) és `<CS2>/game/csgo/*.dem` (rögzítve) |
| [Counter-Strike 2 (játékállapot)](game-cs2-gsi.md) | gsi | igen | Game State Integration: HTTP POST-ok a 127.0.0.1:3311 címre, a `<CS2>\game\csgo\cfg\gamestate_integration_heat3d.cfg` állítja be |
| [DCS World (élő adatok)](game-dcs.md) | telemetry | igen | a watcher hookja `%USERPROFILE%\Saved` `Games\DCS*\Scripts\Hooks\heat3d-watch.lua`, UDP-sorok a 127.0.0.1:41993 címre |
| [DiRT Rally 2.0 (élő adatok)](game-dirt-rally-2.md) | telemetry | igen | UDP 127.0.0.1:20777, extradata=3 `(Documents\My` `Games\DiRT` Rally `2.0\hardwaresettings\hardware_settings_config.xml`); ha egy másik alkalmazás tartja a 20777-es portot, a watcher átengedi neki |
| [Dota 2 (visszajátszások)](game-dota-replays.md) | replay | igen | a Dota 2 által mentett visszajátszások: `<Dota>/game/dota/replays/<match id>.dem` (a kliensben letöltve, vagy a `dota-replay <match id>` paranccsal) |
| [Dota 2 (játékállapot)](game-dota2-gsi.md) | gsi | igen | Game State Integration: HTTP POST-ok a 127.0.0.1:3312 címre, a `<Dota>\game\dota\cfg\gamestate_integration\gamestate_integration_heat3d.cfg` állítja be |
| [EA SPORTS F1 23 (élő adatok)](game-f1-23.md) | telemetry | igen | UDP-telemetria 127.0.0.1:20777 `(Documents\My` `Games\F1` `23\hardwaresettings\hardware_settings_config.xml`) |
| [EA SPORTS F1 24 (élő adatok)](game-f1-24.md) | telemetry | igen | UDP-telemetria 127.0.0.1:20777 `(Documents\My` `Games\F1` `24\hardwaresettings\hardware_settings_config.xml`) |
| [EA SPORTS F1 25 (élő adatok)](game-f1-25.md) | telemetry | igen | UDP-telemetria 127.0.0.1:20777 `(Documents\My` `Games\F1` `25\hardwaresettings\hardware_settings_config.xml`) |
| [EA SPORTS WRC (élő adatok)](game-ea-wrc.md) | telemetry | igen | UDP 127.0.0.1:20777, a `wrc` alapértelmezett struktúra session_update csomagja `(Documents\My` `Games\WRC\telemetry\config.json`); ha egy másik alkalmazás tartja a 20777-es portot, a watcher átengedi neki |
| [Elite Dangerous (naplófájlok)](game-elite.md) | log | igen | Player Journal `%USERPROFILE%\Saved` `Games\Frontier` `Developments\Elite` `Dangerous\Journal.*.log` (a legújabb fájl, írás közben követve), Status.json és a többi társalkalmazás-`*.json` (Market, Outfitting, Shipyard, NavRoute, Cargo, ModulesInfo, ShipLocker, Backpack, FCMaterials) ugyanabban a mappában |
| [Euro Truck Simulator 2 (élő adatok)](game-ets2.md) | telemetry | igen | megosztott memória `Local\SCSTelemetry`, amelyet a RenCloud scs-sdk-plugin (12-es revízió) ír a `<game>\bin\win_x64\plugins` mappában |
| [EVE Online (naplófájlok)](game-eve.md) | log | nincs | `%USERPROFILE%\Documents\EVE\logs\Gamelogs\*.txt` és a mellette lévő `Chatlogs\*.txt` (minden fájl, amely a kliens indulása óta készült) |
| [Forza Horizon 4 (élő adatok)](game-forza-horizon-4.md) | telemetry | igen | Forza Data Out, UDP 127.0.0.1:5300 (Dash formátum); minden csomag változatlanul továbbítva a 127.0.0.1:5301 címre |
| [Forza Horizon 5 (élő adatok)](game-forza-horizon-5.md) | telemetry | igen | Forza Data Out, UDP 127.0.0.1:5300 (Dash formátum); minden csomag változatlanul továbbítva a 127.0.0.1:5301 címre |
| [Forza Horizon 6 (élő adatok)](game-forza-horizon-6.md) | telemetry | igen | Forza Data Out, UDP 127.0.0.1:5300 (Dash formátum); minden csomag változatlanul továbbítva a 127.0.0.1:5301 címre |
| [Forza Motorsport (élő adatok)](game-forza-motorsport.md) | telemetry | igen | Forza Data Out, UDP 127.0.0.1:5300 (Dash formátum); minden csomag változatlanul továbbítva a 127.0.0.1:5301 címre |
| [Hearthstone (naplófájlok)](game-hearthstone.md) | log | nincs | `<install>\Logs\Power.log` (vagy `Logs\Hearthstone_*\Power.log`), amelyet akkor ír, ha a `%LOCALAPPDATA%\Blizzard\Hearthstone\log.config` tartalmaz egy [Power] szakaszt, és minden más `*.log`, amelyet a játék ott ír |
| [IL-2 Sturmovik: Great Battles (élő adatok)](game-il2.md) | telemetry | nincs | a játék telemetriai UDP-kimenete a 127.0.0.1:41995 címre (a `<game>\data\startup.cfg` [KEY = telemetrydevice] beállítása) |
| [IL-2 Sturmovik: Great Battles (visszajátszások)](game-il2-tacview.md) | replay | igen | a játék saját Tacview-felvételei `<game>\data\Tracks\*.acmi` (ACMI 2.x szöveg, sima vagy tömörítve) |
| [iRacing (élő adatok)](game-iracing.md) | telemetry | nincs | megosztott memória `Local\IRSDKMemMapFileName` (az iRacing SDK); a .ibt fájlok a `%USERPROFILE%\Documents\iRacing\telemetry` mappában |
| [League of Legends (játékállapot)](game-lol-live.md) | gsi | nincs | a játékkliens Live Client Data API-ja, <https://127.0.0.1:2999/liveclientdata/> (allgamedata, eventdata), meccs közben |
| [League of Legends (visszajátszások)](game-lol-replays.md) | replay | igen | a League kliens által mentett visszajátszások: %USERPROFILE%/Documents/League of `Legends/Replays/*.rofl` (csak a szokásos meccs végi metaadatok); a saját Riot API-kulcsoddal a meccs hivatalos idővonala a Riot Match-V5 API-jából |
| [Microsoft Flight Simulator 2020 (élő adatok)](game-msfs2020.md) | telemetry | igen | SimConnect a játékos saját SimConnect.dll-jén keresztül (a szimulátor mappája, vagy `%MSFS_SDK%\SimConnect` `SDK\lib`) |
| [Microsoft Flight Simulator 2024 (élő adatok)](game-msfs2024.md) | telemetry | igen | SimConnect a játékos saját SimConnect.dll-jén keresztül (a szimulátor mappája, vagy `%MSFS2024_SDK%\SimConnect` `SDK\lib`) |
| [Minecraft (naplófájlok)](game-minecraft.md) | log | igen | `%APPDATA%\.minecraft\logs\latest.log` (követve), `saves\<world>\stats\<uuid>.json` és `saves\<world>\playerdata\<uuid>.dat` / level.dat (gzip NBT), amelyeket a játék mentéskor olvas |
| [NVIDIA highlights (platform)](game-nvidia-highlights.md) | platform | kölcsönzött | `%LOCALAPPDATA%\NVIDIA` `Corporation\NVIDIA` `Overlay\UGCTracker.json`, GallerySettings.json, `Highlights\<game>\config.json`; a klipek a rögzítési mappában `(%USERPROFILE%\Videos\NVIDIA\<Game>\*.mp4`) és `<temp>\Highlights\<game>`; `%LOCALAPPDATA%\NVIDIA` `Corporation\GfeSDK\<exe>_<pid>.log` |
| [osu! (visszajátszások)](game-osu-replays.md) | replay | igen | az osu! (régi) által mentett visszajátszások: `%LOCALAPPDATA%/osu!/Data/r/*.osr` (minden játék) és `osu!/Replays/*.osr` (exportálva) |
| [Path of Exile (naplófájlok)](game-poe.md) | log | nincs | a Path of Exile vagy a Path of Exile 2 `<install>\logs\Client.txt` fájlja (követve; a telepítési mappa a futó végrehajtható fájlé) |
| [Project CARS 2 (élő adatok)](game-project-cars-2.md) | telemetry | igen | megosztott memória $pcars2$ (SMS SharedMemory.h) |
| [RaceRoom Racing Experience (élő adatok)](game-raceroom.md) | telemetry | igen | megosztott memória $R3E (Sector3 r3e.h, 3-as verzió) |
| [Richard Burns Rally (élő adatok)](game-richard-burns-rally.md) | telemetry | igen | NGP-bővítmény UDP-telemetriája, 127.0.0.1:6776 (RichardBurnsRally.ini [NGP] udpTelemetry=1) |
| [Rocket League (játékállapot)](game-rocketleague-stats.md) | gsi | igen | Stats API: TCP JSON-folyam a 127.0.0.1:49123 címről (a port a `<RL>\TAGame\Config\TAStatsAPI.ini` vagy DefaultStatsAPI.ini fájlban) |
| [Squad (visszajátszások)](game-squad-demos.md) | replay | igen | a Squad szerverdemói, amelyeket az AdminDemoRec admin paranccsal rögzítenek: `<server>/SquadGame/Saved/Demos/*.replay`, a külső `heat3d-squad-demo` olvasó olvassa (exporters/ext/squad-demo) |
| [Star Citizen (naplófájlok)](game-starcitizen.md) | log | nincs | `<install>\StarCitizen\LIVE\Game.log` (a futó StarCitizen.exe build-mappája), csak a játék által írt naplófájl – egy Easy Anti-Cheat játék: semmi nem nyúl a folyamatához |
| [Steam statisztikák (platform)](game-steam-stats.md) | platform | nincs | a Steam helyi statisztikai gyorsítótára, `%STEAM%\appcache\stats\UserGameStats_<account>_<appid>.bin` a `UserGameStatsSchema_<appid>.bin` mellett; a játékidő a `%STEAM%\userdata\<account>\config\localconfig.vdf` fájlból (a %STEAM% a `HKCU\Software\Valve\Steam` SteamPath értékéből) |
| [Steam Timeline (platform)](game-steam-timeline.md) | platform | nincs | `%STEAM%\userdata\<account>\gamerecordings\timelines\timeline_<appid><date>_<time>.json` |
| [VALORANT (visszajátszások)](game-valorant-replays.md) | replay | nincs | a VALORANT által mentett visszajátszások: `%LOCALAPPDATA%/VALORANT/Saved/Demos/*.vrf` (csak a nem elrejtett részek) |
| [War Thunder (visszajátszások)](game-warthunder-replays.md) | replay | igen | a War Thunder mentett visszajátszásai: `<War Thunder>/Replays/*.wrpl` (a visszajátszás-mentéssel), a `heat3d-wt-replay` külső átalakító alakítja (exporters/ext/warthunder-replay) |
| [War Thunder (játékállapot)](game-warthunder-webmap.md) | gsi | igen | a játék helyi webes térképe, <http://127.0.0.1:8111> (/map_info.json, /map_obj.json, /state, /indicators, /hudmsg, /gamechat, /mission.json, /map.img) |
| [World of Tanks (visszajátszások)](game-wot-replays.md) | replay | igen | a World of Tanks mentett visszajátszásai: `<World of Tanks>/replays/*.wotreplay` (a csatafelvétel bekapcsolásával), a `heat3d-wot-replay` külső átalakító alakítja (exporters/ext/wot-replay) |
| [World of Warships (visszajátszások)](game-wows-replays.md) | replay | igen | a World of Warships mentett visszajátszásai: `<World of Warships>/replays/*.wowsreplay` (a visszajátszásokkal), a `heat3d-wows-replay` külső átalakító alakítja (exporters/ext/wows-replay) |
| [X-Plane (élő adatok)](game-xplane.md) | telemetry | igen | az X-Plane UDP-felülete a 127.0.0.1:49000 címen (RREF datarefek és RPOS pozíció, a watcher felé válaszolva) |

Azok a játékok, amelyeket nem rögzítünk, és az okuk: [Források és szabályok](sources-and-rules.md#what-is-declined-and-why). Minden egy táblázatban, ahogy a `python -m heat3d_watch games --markdown` kiírja: [Minden játék egy táblázatban](watcher.md).

<!-- Generated by tools/gen_game_pages.py; run it again after changing an adapter. -->
