---
title: Hry
nav_order: 4
lang: "sk"
source: games.md
source_hash: "0766c0bb0763"
nav_exclude: true
search_exclude: true
---
# Hry {#games}

Watcher pozná 50 zdrojov v 45 hrách a platformách. Každý má vlastnú stránku, generovanú z jeho adaptéra: čo zaznamenáva, odkiaľ, ako ho zapnúť, ako funguje, jeho osi a čo bolo overené.

Druhy: `telemetry`, `gsi`, `log`, `replay` a `platform` – pozrite [Pravidlá a zdroje](sources-and-rules.md). Pozície: *áno*, keď adaptér zapisuje riadky s miestom, *prevzaté*, keď berie miesto z iného záznamu tej istej hry (pozrite [NVIDIA Highlights](nvidia-highlights.md)), *nie*, keď zdroj nemá žiadne. Profily pamäte sa tu neuvádzajú: nedodávajú sa žiadne a každý hráč si píše vlastný (pozrite [Čítanie pamäte](memory-reading.md)).

| Hra | Druh | Pozície | Zdroj |
|---|---|---|---|
| [American Truck Simulator (živé dáta)](game-ats.md) | telemetry | áno | zdieľaná pamäť `Local\SCSTelemetry`, ktorú zapisuje RenCloud scs-sdk-plugin (revízia 12) v `<game>\bin\win_x64\plugins` |
| [Assetto Corsa (živé dáta)](game-assetto-corsa.md) | telemetry | áno | zdieľaná pamäť `Local\acpmf_physics`, `Local\acpmf_graphics`, `Local\acpmf_static` |
| [Assetto Corsa Competizione (živé dáta)](game-assetto-corsa-competizione.md) | telemetry | áno | zdieľaná pamäť `Local\acpmf_physics`, `Local\acpmf_graphics`, `Local\acpmf_static` |
| [Assetto Corsa EVO (živé dáta)](game-assetto-corsa-evo.md) | telemetry | áno | zdieľaná pamäť `Local\acevo_pmf_physics`, `Local\acevo_pmf_static` |
| [Assetto Corsa Rally (živé dáta)](game-assetto-corsa-rally.md) | telemetry | áno | zdieľaná pamäť `Local\acpmf_physics`, `Local\acpmf_static` (tie isté stránky ako AC a ACC) |
| [Automobilista 2 (živé dáta)](game-automobilista-2.md) | telemetry | áno | zdieľaná pamäť $pcars2$ (rozloženie SMS SharedMemory.h) |
| [BeamNG.drive (živé dáta)](game-beamng.md) | telemetry | áno | UDP 127.0.0.1:4460 z protokolového modu heat3d (mods/beamng/heat3d v tomto repozitári) |
| [Counter-Strike 2 (replaye)](game-cs2-demos.md) | replay | áno | dema, ktoré CS2 ukladá: `<CS2>/game/csgo/replays/*.dem` (stiahnuté z histórie zápasov) a `<CS2>/game/csgo/*.dem` (nahrané) |
| [Counter-Strike 2 (herný stav)](game-cs2-gsi.md) | gsi | áno | Game State Integration: HTTP POST na 127.0.0.1:3311, nastavené v `<CS2>\game\csgo\cfg\gamestate_integration_heat3d.cfg` |
| [DCS World (živé dáta)](game-dcs.md) | telemetry | áno | hook watchera `%USERPROFILE%\Saved` `Games\DCS*\Scripts\Hooks\heat3d-watch.lua`, riadky UDP na 127.0.0.1:41993 |
| [DiRT Rally 2.0 (živé dáta)](game-dirt-rally-2.md) | telemetry | áno | UDP 127.0.0.1:20777, extradata=3 `(Documents\My` `Games\DiRT` Rally `2.0\hardwaresettings\hardware_settings_config.xml`); kým iná aplikácia drží port 20777, watcher ho nechá tej aplikácii |
| [Dota 2 (replaye)](game-dota-replays.md) | replay | áno | replaye, ktoré Dota 2 ukladá: `<Dota>/game/dota/replays/<match id>.dem` (stiahnuté v klientovi, alebo príkazom `dota-replay <match id>`) |
| [Dota 2 (herný stav)](game-dota2-gsi.md) | gsi | áno | Game State Integration: HTTP POST na 127.0.0.1:3312, nastavené v `<Dota>\game\dota\cfg\gamestate_integration\gamestate_integration_heat3d.cfg` |
| [EA SPORTS F1 23 (živé dáta)](game-f1-23.md) | telemetry | áno | UDP telemetria 127.0.0.1:20777 `(Documents\My` `Games\F1` `23\hardwaresettings\hardware_settings_config.xml`) |
| [EA SPORTS F1 24 (živé dáta)](game-f1-24.md) | telemetry | áno | UDP telemetria 127.0.0.1:20777 `(Documents\My` `Games\F1` `24\hardwaresettings\hardware_settings_config.xml`) |
| [EA SPORTS F1 25 (živé dáta)](game-f1-25.md) | telemetry | áno | UDP telemetria 127.0.0.1:20777 `(Documents\My` `Games\F1` `25\hardwaresettings\hardware_settings_config.xml`) |
| [EA SPORTS WRC (živé dáta)](game-ea-wrc.md) | telemetry | áno | UDP 127.0.0.1:20777, paket session_update predvolenej štruktúry `wrc` `(Documents\My` `Games\WRC\telemetry\config.json`); kým iná aplikácia drží port 20777, watcher ho nechá tej aplikácii |
| [Elite Dangerous (súbory logov)](game-elite.md) | log | áno | denník hráča `%USERPROFILE%\Saved` `Games\Frontier` `Developments\Elite` `Dangerous\Journal.*.log` (najnovší súbor, sledovaný počas zápisu), Status.json a ďalšie spoločnícke súbory `*.json` (Market, Outfitting, Shipyard, NavRoute, Cargo, ModulesInfo, ShipLocker, Backpack, FCMaterials) v rovnakom priečinku |
| [Euro Truck Simulator 2 (živé dáta)](game-ets2.md) | telemetry | áno | zdieľaná pamäť `Local\SCSTelemetry`, ktorú zapisuje RenCloud scs-sdk-plugin (revízia 12) v `<game>\bin\win_x64\plugins` |
| [EVE Online (súbory logov)](game-eve.md) | log | nie | `%USERPROFILE%\Documents\EVE\logs\Gamelogs\*.txt` a súbory `Chatlogs\*.txt` vedľa nich (každý súbor zapísaný od spustenia klienta) |
| [Forza Horizon 4 (živé dáta)](game-forza-horizon-4.md) | telemetry | áno | Forza Data Out, UDP 127.0.0.1:5300 (formát Dash); každý paket preposlaný nezmenený na 127.0.0.1:5301 |
| [Forza Horizon 5 (živé dáta)](game-forza-horizon-5.md) | telemetry | áno | Forza Data Out, UDP 127.0.0.1:5300 (formát Dash); každý paket preposlaný nezmenený na 127.0.0.1:5301 |
| [Forza Horizon 6 (živé dáta)](game-forza-horizon-6.md) | telemetry | áno | Forza Data Out, UDP 127.0.0.1:5300 (formát Dash); každý paket preposlaný nezmenený na 127.0.0.1:5301 |
| [Forza Motorsport (živé dáta)](game-forza-motorsport.md) | telemetry | áno | Forza Data Out, UDP 127.0.0.1:5300 (formát Dash); každý paket preposlaný nezmenený na 127.0.0.1:5301 |
| [Hearthstone (súbory logov)](game-hearthstone.md) | log | nie | `<install>\Logs\Power.log` (alebo `Logs\Hearthstone_*\Power.log`), zapisovaný, keď `%LOCALAPPDATA%\Blizzard\Hearthstone\log.config` obsahuje sekciu [Power], a každý ďalší `*.log`, ktorý tam hra zapíše |
| [IL-2 Sturmovik: Great Battles (živé dáta)](game-il2.md) | telemetry | nie | telemetrický UDP výstup hry na 127.0.0.1:41995 ([KEY = telemetrydevice] v `<game>\data\startup.cfg`) |
| [IL-2 Sturmovik: Great Battles (replaye)](game-il2-tacview.md) | replay | áno | vlastné nahrávky Tacview hry `<game>\data\Tracks\*.acmi` (text ACMI 2.x, prostý alebo zazipovaný) |
| [iRacing (živé dáta)](game-iracing.md) | telemetry | nie | zdieľaná pamäť `Local\IRSDKMemMapFileName` (iRacing SDK); súbory .ibt v `%USERPROFILE%\Documents\iRacing\telemetry` |
| [League of Legends (herný stav)](game-lol-live.md) | gsi | nie | Live Client Data API klienta hry, <https://127.0.0.1:2999/liveclientdata/> (allgamedata, eventdata), počas zápasu |
| [League of Legends (replaye)](game-lol-replays.md) | replay | áno | replaye, ktoré ukladá klient League: %USERPROFILE%/Documents/League of `Legends/Replays/*.rofl` (len prosté metadáta na konci hry); s vlastným kľúčom vývojára Riot API oficiálna časová os zápasu z Riot Match-V5 API |
| [Microsoft Flight Simulator 2020 (živé dáta)](game-msfs2020.md) | telemetry | áno | SimConnect cez vlastný SimConnect.dll hráča (priečinok simulátora, alebo `%MSFS_SDK%\SimConnect` `SDK\lib`) |
| [Microsoft Flight Simulator 2024 (živé dáta)](game-msfs2024.md) | telemetry | áno | SimConnect cez vlastný SimConnect.dll hráča (priečinok simulátora, alebo `%MSFS2024_SDK%\SimConnect` `SDK\lib`) |
| [Minecraft (súbory logov)](game-minecraft.md) | log | áno | `%APPDATA%\.minecraft\logs\latest.log` (sledovaný), `saves\<world>\stats\<uuid>.json` a `saves\<world>\playerdata\<uuid>.dat` / level.dat (gzip NBT), čítané, keď ich hra uloží |
| [NVIDIA highlights (platforma)](game-nvidia-highlights.md) | platform | prevzaté | `%LOCALAPPDATA%\NVIDIA` `Corporation\NVIDIA` `Overlay\UGCTracker.json`, GallerySettings.json, `Highlights\<game>\config.json`; klipy v priečinku záznamov `(%USERPROFILE%\Videos\NVIDIA\<Game>\*.mp4`) a `<temp>\Highlights\<game>`; `%LOCALAPPDATA%\NVIDIA` `Corporation\GfeSDK\<exe>_<pid>.log` |
| [osu! (replaye)](game-osu-replays.md) | replay | áno | replaye, ktoré ukladá osu! (stable): `%LOCALAPPDATA%/osu!/Data/r/*.osr` (každá hra) a `osu!/Replays/*.osr` (exportované) |
| [Path of Exile (súbory logov)](game-poe.md) | log | nie | `<install>\logs\Client.txt` hry Path of Exile alebo Path of Exile 2 (sledovaný; priečinok inštalácie je priečinok bežiaceho spustiteľného súboru) |
| [Project CARS 2 (živé dáta)](game-project-cars-2.md) | telemetry | áno | zdieľaná pamäť $pcars2$ (SMS SharedMemory.h) |
| [RaceRoom Racing Experience (živé dáta)](game-raceroom.md) | telemetry | áno | zdieľaná pamäť $R3E (r3e.h od Sector3, verzia 3) |
| [Richard Burns Rally (živé dáta)](game-richard-burns-rally.md) | telemetry | áno | UDP telemetria pluginu NGP, 127.0.0.1:6776 (RichardBurnsRally.ini [NGP] udpTelemetry=1) |
| [Rocket League (herný stav)](game-rocketleague-stats.md) | gsi | áno | Stats API: prúd JSON cez TCP z 127.0.0.1:49123 (port v `<RL>\TAGame\Config\TAStatsAPI.ini` alebo DefaultStatsAPI.ini) |
| [Squad (replaye)](game-squad-demos.md) | replay | áno | serverové dema, ktoré Squad nahráva administrátorským príkazom AdminDemoRec: `<server>/SquadGame/Saved/Demos/*.replay`, čítané externým čítačom `heat3d-squad-demo` (exporters/ext/squad-demo) |
| [Star Citizen (súbory logov)](game-starcitizen.md) | log | nie | `<install>\StarCitizen\LIVE\Game.log` (priečinok zostavy bežiaceho StarCitizen.exe), len súbor logu, ktorý hra zapisuje – hra s Easy Anti-Cheat: nič sa nedotýka jej procesu |
| [Steam štatistiky (platforma)](game-steam-stats.md) | platform | nie | lokálna cache štatistík Steamu `%STEAM%\appcache\stats\UserGameStats_<account>_<appid>.bin` s `UserGameStatsSchema_<appid>.bin`; herný čas z `%STEAM%\userdata\<account>\config\localconfig.vdf` (%STEAM% z `HKCU\Software\Valve\Steam` SteamPath) |
| [Steam Timeline (platforma)](game-steam-timeline.md) | platform | nie | `%STEAM%\userdata\<account>\gamerecordings\timelines\timeline_<appid><date>_<time>.json` |
| [VALORANT (replaye)](game-valorant-replays.md) | replay | nie | replaye, ktoré ukladá VALORANT: `%LOCALAPPDATA%/VALORANT/Saved/Demos/*.vrf` (len časti, ktoré nie sú zaobfuskované) |
| [War Thunder (replaye)](game-warthunder-replays.md) | replay | áno | replaye, ktoré ukladá War Thunder: `<War Thunder>/Replays/*.wrpl` (so zapnutým ukladaním replayov), prevádzané externým konvertorom `heat3d-wt-replay` (exporters/ext/warthunder-replay) |
| [War Thunder (herný stav)](game-warthunder-webmap.md) | gsi | áno | lokálna webová mapa hry, <http://127.0.0.1:8111> (/map_info.json, /map_obj.json, /state, /indicators, /hudmsg, /gamechat, /mission.json, /map.img) |
| [World of Tanks (replaye)](game-wot-replays.md) | replay | áno | replaye, ktoré ukladá World of Tanks: `<World of Tanks>/replays/*.wotreplay` (so zapnutým nahrávaním bitiek), prevádzané externým konvertorom `heat3d-wot-replay` (exporters/ext/wot-replay) |
| [World of Warships (replaye)](game-wows-replays.md) | replay | áno | replaye, ktoré ukladá World of Warships: `<World of Warships>/replays/*.wowsreplay` (so zapnutými replaymi), prevádzané externým konvertorom `heat3d-wows-replay` (exporters/ext/wows-replay) |
| [X-Plane (živé dáta)](game-xplane.md) | telemetry | áno | UDP rozhranie X-Plane na 127.0.0.1:49000 (datarefy RREF a pozícia RPOS, na ktoré odpovedá watcher) |

Hry, ktoré sa nezaznamenávajú, a prečo: [Pravidlá a zdroje](sources-and-rules.md#what-is-declined-and-why). Všetko v jednej tabuľke, tak ako ju vypíše `python -m heat3d_watch games --markdown`: [Všetky hry v jednej tabuľke](watcher.md).

<!-- Generated by tools/gen_game_pages.py; run it again after changing an adapter. -->
