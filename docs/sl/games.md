---
title: "Igre"
nav_order: 4
lang: "sl"
source: games.md
source_hash: "0766c0bb0763"
nav_exclude: true
search_exclude: true
---
# Igre {#games}

Watcher pozna 50 virov v 45 igrah in platformah. Vsak ima svojo stran, ki jo ustvari adapter: kaj zapiše, od kod, kako ga vklopiti, kako deluje, njegove osi in kaj je bilo preverjeno.

Vrste: `telemetry`, `gsi`, `log`, `replay` in `platform` - glej [Viri in pravila](sources-and-rules.md). Položaji: *da*, kadar adapter zapisuje vrstice s krajem; *posredno*, kadar kraj vzame iz drugega posnetka iste igre (glej [NVIDIA Highlights](nvidia-highlights.md)); *ne*, kadar vir nima položaja. Profili pomnilnika niso navedeni: nobeden ni priložen, vsak igralec zapiše svojega (glej [Branje pomnilnika](memory-reading.md)).

| Igra | Vrsta | Položaji | Vir |
|---|---|---|---|
| [American Truck Simulator (live data)](game-ats.md) | telemetry | da | deljeni pomnilnik `Local\SCSTelemetry`, ki ga zapisuje RenCloud scs-sdk-plugin (revizija 12) v `<game>\bin\win_x64\plugins` |
| [Assetto Corsa (live data)](game-assetto-corsa.md) | telemetry | da | deljeni pomnilnik `Local\acpmf_physics`, `Local\acpmf_graphics`, `Local\acpmf_static` |
| [Assetto Corsa Competizione (live data)](game-assetto-corsa-competizione.md) | telemetry | da | deljeni pomnilnik `Local\acpmf_physics`, `Local\acpmf_graphics`, `Local\acpmf_static` |
| [Assetto Corsa EVO (live data)](game-assetto-corsa-evo.md) | telemetry | da | deljeni pomnilnik `Local\acevo_pmf_physics`, `Local\acevo_pmf_static` |
| [Assetto Corsa Rally (live data)](game-assetto-corsa-rally.md) | telemetry | da | deljeni pomnilnik `Local\acpmf_physics`, `Local\acpmf_static` (iste strani kot AC in ACC) |
| [Automobilista 2 (live data)](game-automobilista-2.md) | telemetry | da | deljeni pomnilnik $pcars2$ (postavitev SMS SharedMemory.h) |
| [BeamNG.drive (live data)](game-beamng.md) | telemetry | da | UDP 127.0.0.1:4460 iz protokolnega moda heat3d (mods/beamng/heat3d v tem repozitoriju) |
| [Counter-Strike 2 (replays)](game-cs2-demos.md) | replay | da | demo posnetki, ki jih CS2 shrani: `<CS2>/game/csgo/replays/*.dem` (preneseni iz zgodovine tekem) in `<CS2>/game/csgo/*.dem` (posneti) |
| [Counter-Strike 2 (game state)](game-cs2-gsi.md) | gsi | da | Game State Integration: HTTP POST-i na 127.0.0.1:3311, nastavljeni v `<CS2>\game\csgo\cfg\gamestate_integration_heat3d.cfg` |
| [DCS World (live data)](game-dcs.md) | telemetry | da | hook watcherja `%USERPROFILE%\Saved` `Games\DCS*\Scripts\Hooks\heat3d-watch.lua`, UDP vrstice na 127.0.0.1:41993 |
| [DiRT Rally 2.0 (live data)](game-dirt-rally-2.md) | telemetry | da | UDP 127.0.0.1:20777, extradata=3 `(Documents\My` `Games\DiRT` Rally `2.0\hardwaresettings\hardware_settings_config.xml`); medtem ko drug program drži 20777, watcher vrata prepusti njemu |
| [Dota 2 (replays)](game-dota-replays.md) | replay | da | replay posnetki, ki jih shrani Dota 2: `<Dota>/game/dota/replays/<match id>.dem` (preneseni v odjemalcu ali z `dota-replay <match id>`) |
| [Dota 2 (game state)](game-dota2-gsi.md) | gsi | da | Game State Integration: HTTP POST-i na 127.0.0.1:3312, nastavljeni v `<Dota>\game\dota\cfg\gamestate_integration\gamestate_integration_heat3d.cfg` |
| [EA SPORTS F1 23 (live data)](game-f1-23.md) | telemetry | da | UDP telemetrija 127.0.0.1:20777 `(Documents\My` `Games\F1` `23\hardwaresettings\hardware_settings_config.xml`) |
| [EA SPORTS F1 24 (live data)](game-f1-24.md) | telemetry | da | UDP telemetrija 127.0.0.1:20777 `(Documents\My` `Games\F1` `24\hardwaresettings\hardware_settings_config.xml`) |
| [EA SPORTS F1 25 (live data)](game-f1-25.md) | telemetry | da | UDP telemetrija 127.0.0.1:20777 `(Documents\My` `Games\F1` `25\hardwaresettings\hardware_settings_config.xml`) |
| [EA SPORTS WRC (live data)](game-ea-wrc.md) | telemetry | da | UDP 127.0.0.1:20777, paket session_update privzete strukture `wrc` `(Documents\My` `Games\WRC\telemetry\config.json`); medtem ko drug program drži 20777, watcher vrata prepusti njemu |
| [Elite Dangerous (log files)](game-elite.md) | log | da | dnevnik igralca `%USERPROFILE%\Saved` `Games\Frontier` `Developments\Elite` `Dangerous\Journal.*.log` (najnovejša datoteka, spremljana med pisanjem), Status.json in druge spremljevalne datoteke `*.json` (Market, Outfitting, Shipyard, NavRoute, Cargo, ModulesInfo, ShipLocker, Backpack, FCMaterials) v isti mapi |
| [Euro Truck Simulator 2 (live data)](game-ets2.md) | telemetry | da | deljeni pomnilnik `Local\SCSTelemetry`, ki ga zapisuje RenCloud scs-sdk-plugin (revizija 12) v `<game>\bin\win_x64\plugins` |
| [EVE Online (log files)](game-eve.md) | log | ne | `%USERPROFILE%\Documents\EVE\logs\Gamelogs\*.txt` in `Chatlogs\*.txt` poleg njih (vsaka datoteka, zapisana od zagona odjemalca) |
| [Forza Horizon 4 (live data)](game-forza-horizon-4.md) | telemetry | da | Forza Data Out, UDP 127.0.0.1:5300 (format Dash); vsak paket se nespremenjen posreduje na 127.0.0.1:5301 |
| [Forza Horizon 5 (live data)](game-forza-horizon-5.md) | telemetry | da | Forza Data Out, UDP 127.0.0.1:5300 (format Dash); vsak paket se nespremenjen posreduje na 127.0.0.1:5301 |
| [Forza Horizon 6 (live data)](game-forza-horizon-6.md) | telemetry | da | Forza Data Out, UDP 127.0.0.1:5300 (format Dash); vsak paket se nespremenjen posreduje na 127.0.0.1:5301 |
| [Forza Motorsport (live data)](game-forza-motorsport.md) | telemetry | da | Forza Data Out, UDP 127.0.0.1:5300 (format Dash); vsak paket se nespremenjen posreduje na 127.0.0.1:5301 |
| [Hearthstone (log files)](game-hearthstone.md) | log | ne | `<install>\Logs\Power.log` (ali `Logs\Hearthstone_*\Power.log`), zapisan, ko ima `%LOCALAPPDATA%\Blizzard\Hearthstone\log.config` odsek [Power], in vsaka druga datoteka `*.log`, ki jo igra tam zapiše |
| [IL-2 Sturmovik: Great Battles (live data)](game-il2.md) | telemetry | ne | telemetrijski izhod igre na UDP 127.0.0.1:41995 (`[KEY = telemetrydevice]` v `<game>\data\startup.cfg`) |
| [IL-2 Sturmovik: Great Battles (replays)](game-il2-tacview.md) | replay | da | lastni posnetki Tacview igre `<game>\data\Tracks\*.acmi` (besedilo ACMI 2.x, navadno ali stisnjeno) |
| [iRacing (live data)](game-iracing.md) | telemetry | ne | deljeni pomnilnik `Local\IRSDKMemMapFileName` (iRacing SDK); datoteke .ibt v `%USERPROFILE%\Documents\iRacing\telemetry` |
| [League of Legends (game state)](game-lol-live.md) | gsi | ne | Live Client Data API odjemalca igre, <https://127.0.0.1:2999/liveclientdata/> (allgamedata, eventdata), med tekmo |
| [League of Legends (replays)](game-lol-replays.md) | replay | da | replay posnetki, ki jih shrani odjemalec League: %USERPROFILE%/Documents/League of `Legends/Replays/*.rofl` (samo navadni podatki o koncu igre); z lastnim ključem Riot API uradna časovnica tekme iz Riotovega Match-V5 API |
| [Microsoft Flight Simulator 2020 (live data)](game-msfs2020.md) | telemetry | da | SimConnect prek lastne datoteke SimConnect.dll igralca (mapa simulatorja ali `%MSFS_SDK%\SimConnect` `SDK\lib`) |
| [Microsoft Flight Simulator 2024 (live data)](game-msfs2024.md) | telemetry | da | SimConnect prek lastne datoteke SimConnect.dll igralca (mapa simulatorja ali `%MSFS2024_SDK%\SimConnect` `SDK\lib`) |
| [Minecraft (log files)](game-minecraft.md) | log | da | `%APPDATA%\.minecraft\logs\latest.log` (spremljano), `saves\<world>\stats\<uuid>.json` in `saves\<world>\playerdata\<uuid>.dat` / level.dat (gzip NBT), prebrano, ko jih igra shrani |
| [NVIDIA highlights (platform)](game-nvidia-highlights.md) | platform | posredno | `%LOCALAPPDATA%\NVIDIA` `Corporation\NVIDIA` `Overlay\UGCTracker.json`, GallerySettings.json, `Highlights\<game>\config.json`; posnetki v mapi za zajem `(%USERPROFILE%\Videos\NVIDIA\<Game>\*.mp4`) in `<temp>\Highlights\<game>`; `%LOCALAPPDATA%\NVIDIA` `Corporation\GfeSDK\<exe>_<pid>.log` |
| [osu! (replays)](game-osu-replays.md) | replay | da | replay posnetki osu! (stabilna različica), ki jih shrani igra: `%LOCALAPPDATA%/osu!/Data/r/*.osr` (vsaka igra) in `osu!/Replays/*.osr` (izvoženi) |
| [Path of Exile (log files)](game-poe.md) | log | ne | `<install>\logs\Client.txt` igre Path of Exile ali Path of Exile 2 (spremljano; mapa namestitve je mapa zagnane izvršljive datoteke) |
| [Project CARS 2 (live data)](game-project-cars-2.md) | telemetry | da | deljeni pomnilnik $pcars2$ (SMS SharedMemory.h) |
| [RaceRoom Racing Experience (live data)](game-raceroom.md) | telemetry | da | deljeni pomnilnik $R3E (r3e.h podjetja Sector3, različica 3) |
| [Richard Burns Rally (live data)](game-richard-burns-rally.md) | telemetry | da | UDP telemetrija vtičnika NGP, 127.0.0.1:6776 (RichardBurnsRally.ini [NGP] udpTelemetry=1) |
| [Rocket League (game state)](game-rocketleague-stats.md) | gsi | da | Stats API: TCP JSON tok iz 127.0.0.1:49123 (vrata v `<RL>\TAGame\Config\TAStatsAPI.ini` ali DefaultStatsAPI.ini) |
| [Squad (replays)](game-squad-demos.md) | replay | da | demo posnetki strežnika, ki jih Squad snema z admin ukazom AdminDemoRec: `<server>/SquadGame/Saved/Demos/*.replay`, bere jih zunanji bralnik `heat3d-squad-demo` (exporters/ext/squad-demo) |
| [Star Citizen (log files)](game-starcitizen.md) | log | ne | `<install>\StarCitizen\LIVE\Game.log` (mapa gradnje zagnane datoteke StarCitizen.exe), samo dnevniška datoteka, ki jo igra zapiše - igra z zaščito Easy Anti-Cheat: nič se ne dotakne njenega procesa |
| [Steam statistics (platform)](game-steam-stats.md) | platform | ne | lokalni predpomnilnik statistik Steama `%STEAM%\appcache\stats\UserGameStats_<account>_<appid>.bin` z `UserGameStatsSchema_<appid>.bin`; čas igranja iz `%STEAM%\userdata\<account>\config\localconfig.vdf` (%STEAM% iz `HKCU\Software\Valve\Steam` SteamPath) |
| [Steam Timeline (platform)](game-steam-timeline.md) | platform | ne | `%STEAM%\userdata\<account>\gamerecordings\timelines\timeline_<appid><date>_<time>.json` |
| [VALORANT (replays)](game-valorant-replays.md) | replay | ne | replay posnetki, ki jih shrani VALORANT: `%LOCALAPPDATA%/VALORANT/Saved/Demos/*.vrf` (samo deli, ki niso zakriti) |
| [War Thunder (replays)](game-warthunder-replays.md) | replay | da | replay posnetki, ki jih shrani War Thunder: `<War Thunder>/Replays/*.wrpl` (ko je shranjevanje replayev vklopljeno), pretvori zunanji pretvornik `heat3d-wt-replay` (exporters/ext/warthunder-replay) |
| [War Thunder (game state)](game-warthunder-webmap.md) | gsi | da | lokalni spletni zemljevid igre, <http://127.0.0.1:8111> (/map_info.json, /map_obj.json, /state, /indicators, /hudmsg, /gamechat, /mission.json, /map.img) |
| [World of Tanks (replays)](game-wot-replays.md) | replay | da | replay posnetki, ki jih shrani World of Tanks: `<World of Tanks>/replays/*.wotreplay` (ko je snemanje bitk vklopljeno), pretvori zunanji pretvornik `heat3d-wot-replay` (exporters/ext/wot-replay) |
| [World of Warships (replays)](game-wows-replays.md) | replay | da | replay posnetki, ki jih shrani World of Warships: `<World of Warships>/replays/*.wowsreplay` (ko so replayi vklopljeni), pretvori zunanji pretvornik `heat3d-wows-replay` (exporters/ext/wows-replay) |
| [X-Plane (live data)](game-xplane.md) | telemetry | da | UDP vmesnik X-Plane na 127.0.0.1:49000 (RREF datarefi in RPOS položaj, odgovarja watcherju) |

Igre, ki se ne snemajo, in zakaj: [Viri in pravila](sources-and-rules.md#what-is-declined-and-why). Vse v eni tabeli, kakor jo izpiše `python -m heat3d_watch games --markdown`: [Vse igre v eni tabeli](watcher.md).

<!-- Generated by tools/gen_game_pages.py; run it again after changing an adapter. -->
