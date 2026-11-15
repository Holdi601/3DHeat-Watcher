---
title: Spill
nav_order: 4
lang: "no"
source: games.md
source_hash: "c601550fbb4e"
nav_exclude: true
search_exclude: true
---
# Spill {#games}

Watcheren kjenner 49 kilder i 44 spill og plattformer. Hver har sin egen side, generert fra adapteren: hva den tar opp, hvor det kommer fra, hvordan den slås på, hvordan den fungerer, dens akser, og hva som er verifisert.

Typer: `telemetry`, `gsi`, `log`, `replay` og `platform` - se [Kilder og regler](sources-and-rules.md). Posisjoner: *ja* når adapteren skriver rader med et sted, *lånt* når den tar stedet fra en annen opptak av samme spill (se [NVIDIA-høydepunkter](nvidia-highlights.md)), *nei* når kilden ikke har noe. Minneprofiler er ikke oppført: ingen leveres, og hver spiller skriver sin egen (se [Lese minne](memory-reading.md)).

| Spill | Type | Posisjoner | Kilde |
|---|---|---|---|
| [American Truck Simulator (direkte data)](game-ats.md) | telemetry | ja | delt minne `Local\SCSTelemetry`, skrevet av RenCloud scs-sdk-plugin (revisjon 12) i `<game>\bin\win_x64\plugins` |
| [Assetto Corsa (direkte data)](game-assetto-corsa.md) | telemetry | ja | delt minne `Local\acpmf_physics`, `Local\acpmf_graphics`, `Local\acpmf_static` |
| [Assetto Corsa Competizione (direkte data)](game-assetto-corsa-competizione.md) | telemetry | ja | delt minne `Local\acpmf_physics`, `Local\acpmf_graphics`, `Local\acpmf_static` |
| [Assetto Corsa EVO (direkte data)](game-assetto-corsa-evo.md) | telemetry | ja | delt minne `Local\acevo_pmf_physics`, `Local\acevo_pmf_static` |
| [Assetto Corsa Rally (direkte data)](game-assetto-corsa-rally.md) | telemetry | ja | delt minne `Local\acpmf_physics`, `Local\acpmf_static` (de samme sidene som AC og ACC) |
| [Automobilista 2 (direkte data)](game-automobilista-2.md) | telemetry | ja | delt minne $pcars2$ (SMS SharedMemory.h-oppsettet) |
| [BeamNG.drive (direkte data)](game-beamng.md) | telemetry | ja | UDP 127.0.0.1:4460 fra heat3d-protokollmodden (mods/beamng/heat3d i dette repositoriet) |
| [Counter-Strike 2 (repriser)](game-cs2-demos.md) | replay | ja | demoer CS2 lagrer: `<CS2>/game/csgo/replays/*.dem` (lastet ned fra kamphistorikken) og `<CS2>/game/csgo/*.dem` (tatt opp) |
| [Counter-Strike 2 (spilltilstand)](game-cs2-gsi.md) | gsi | ja | Game State Integration: HTTP-POST til 127.0.0.1:3311, satt opp av `<CS2>\game\csgo\cfg\gamestate_integration_heat3d.cfg` |
| [DCS World (direkte data)](game-dcs.md) | telemetry | ja | watcherens hook `%USERPROFILE%\Saved` `Games\DCS*\Scripts\Hooks\heat3d-watch.lua`, UDP-linjer til 127.0.0.1:41993 |
| [DiRT Rally 2.0 (direkte data)](game-dirt-rally-2.md) | telemetry | ja | UDP 127.0.0.1:20777, extradata=3 `(Documents\My` `Games\DiRT` Rally `2.0\hardwaresettings\hardware_settings_config.xml`); mens et annet program holder 20777, lar watcheren porten være hos det |
| [Dota 2 (repriser)](game-dota-replays.md) | replay | ja | repriser Dota 2 lagrer: `<Dota>/game/dota/replays/<match id>.dem` (lastet ned i klienten, eller med `dota-replay <match id>`) |
| [Dota 2 (spilltilstand)](game-dota2-gsi.md) | gsi | ja | Game State Integration: HTTP-POST til 127.0.0.1:3312, satt opp av `<Dota>\game\dota\cfg\gamestate_integration\gamestate_integration_heat3d.cfg` |
| [EA SPORTS F1 23 (direkte data)](game-f1-23.md) | telemetry | ja | UDP-telemetri 127.0.0.1:20777 `(Documents\My` `Games\F1` `23\hardwaresettings\hardware_settings_config.xml`) |
| [EA SPORTS F1 24 (direkte data)](game-f1-24.md) | telemetry | ja | UDP-telemetri 127.0.0.1:20777 `(Documents\My` `Games\F1` `24\hardwaresettings\hardware_settings_config.xml`) |
| [EA SPORTS F1 25 (direkte data)](game-f1-25.md) | telemetry | ja | UDP-telemetri 127.0.0.1:20777 `(Documents\My` `Games\F1` `25\hardwaresettings\hardware_settings_config.xml`) |
| [EA SPORTS WRC (direkte data)](game-ea-wrc.md) | telemetry | ja | UDP 127.0.0.1:20777, standardstrukturen `wrc` sin session_update-pakke `(Documents\My` `Games\WRC\telemetry\config.json`); mens et annet program holder 20777, lar watcheren porten være hos det |
| [Elite Dangerous (loggfiler)](game-elite.md) | log | ja | Player Journal `%USERPROFILE%\Saved` `Games\Frontier` `Developments\Elite` `Dangerous\Journal.*.log` (nyeste fil, fulgt mens den skrives), Status.json og de andre companion-`*.json`-filene (Market, Outfitting, Shipyard, NavRoute, Cargo, ModulesInfo, ShipLocker, Backpack, FCMaterials) i samme mappe |
| [Euro Truck Simulator 2 (direkte data)](game-ets2.md) | telemetry | ja | delt minne `Local\SCSTelemetry`, skrevet av RenCloud scs-sdk-plugin (revisjon 12) i `<game>\bin\win_x64\plugins` |
| [EVE Online (loggfiler)](game-eve.md) | log | nei | `%USERPROFILE%\Documents\EVE\logs\Gamelogs\*.txt` og `Chatlogs\*.txt` ved siden av (hver fil skrevet siden klienten startet) |
| [Forza Horizon 4 (direkte data)](game-forza-horizon-4.md) | telemetry | ja | Forza Data Out, UDP 127.0.0.1:5300 (Dash-format); hver pakke videresendes uendret til 127.0.0.1:5301 |
| [Forza Horizon 5 (direkte data)](game-forza-horizon-5.md) | telemetry | ja | Forza Data Out, UDP 127.0.0.1:5300 (Dash-format); hver pakke videresendes uendret til 127.0.0.1:5301 |
| [Forza Horizon 6 (direkte data)](game-forza-horizon-6.md) | telemetry | ja | Forza Data Out, UDP 127.0.0.1:5300 (Dash-format); hver pakke videresendes uendret til 127.0.0.1:5301 |
| [Forza Motorsport (direkte data)](game-forza-motorsport.md) | telemetry | ja | Forza Data Out, UDP 127.0.0.1:5300 (Dash-format); hver pakke videresendes uendret til 127.0.0.1:5301 |
| [Hearthstone (loggfiler)](game-hearthstone.md) | log | nei | `<install>\Logs\Power.log` (eller `Logs\Hearthstone_*\Power.log`), skrevet når `%LOCALAPPDATA%\Blizzard\Hearthstone\log.config` har en [Power]-seksjon, og hver annen `*.log` spillet skriver der |
| [IL-2 Sturmovik: Great Battles (direkte data)](game-il2.md) | telemetry | nei | spillets telemetri-UDP-utdata til 127.0.0.1:41995 ([KEY = telemetrydevice] i `<game>\data\startup.cfg`) |
| [IL-2 Sturmovik: Great Battles (repriser)](game-il2-tacview.md) | replay | ja | spillets egne Tacview-opptak `<game>\data\Tracks\*.acmi` (ACMI 2.x-tekst, vanlig eller zippet) |
| [iRacing (direkte data)](game-iracing.md) | telemetry | nei | delt minne `Local\IRSDKMemMapFileName` (iRacing SDK); .ibt-filer i `%USERPROFILE%\Documents\iRacing\telemetry` |
| [League of Legends (spilltilstand)](game-lol-live.md) | gsi | nei | Live Client Data API i spillklienten, <https://127.0.0.1:2999/liveclientdata/> (allgamedata, eventdata), under en kamp |
| [League of Legends (repriser)](game-lol-replays.md) | replay | ja | repriser League-klienten lagrer: %USERPROFILE%/Documents/League of `Legends/Replays/*.rofl` (bare de vanlige metadataene etter kampen); med din egen Riot API-nøkkel, kampens offisielle tidslinje fra Riots Match-V5-API |
| [Microsoft Flight Simulator 2020 (direkte data)](game-msfs2020.md) | telemetry | ja | SimConnect gjennom spillerens egen SimConnect.dll (simulatormappen, eller `%MSFS_SDK%\SimConnect` `SDK\lib`) |
| [Microsoft Flight Simulator 2024 (direkte data)](game-msfs2024.md) | telemetry | ja | SimConnect gjennom spillerens egen SimConnect.dll (simulatormappen, eller `%MSFS2024_SDK%\SimConnect` `SDK\lib`) |
| [Minecraft (loggfiler)](game-minecraft.md) | log | ja | `%APPDATA%\.minecraft\logs\latest.log` (fulgt), `saves\<world>\stats\<uuid>.json` og `saves\<world>\playerdata\<uuid>.dat` / level.dat (gzip NBT), lest når spillet lagrer dem |
| [NVIDIA-høydepunkter (plattform)](game-nvidia-highlights.md) | platform | lånt | `%LOCALAPPDATA%\NVIDIA` `Corporation\NVIDIA` `Overlay\UGCTracker.json`, GallerySettings.json, `Highlights\<game>\config.json`; klipp i opptaksmappen `(%USERPROFILE%\Videos\NVIDIA\<Game>\*.mp4`) og `<temp>\Highlights\<game>`; `%LOCALAPPDATA%\NVIDIA` `Corporation\GfeSDK\<exe>_<pid>.log` |
| [Path of Exile (loggfiler)](game-poe.md) | log | nei | `<install>\logs\Client.txt` i Path of Exile eller Path of Exile 2 (fulgt; installasjonsmappen er den kjørende exe-filens) |
| [Project CARS 2 (direkte data)](game-project-cars-2.md) | telemetry | ja | delt minne $pcars2$ (SMS SharedMemory.h) |
| [RaceRoom Racing Experience (direkte data)](game-raceroom.md) | telemetry | ja | delt minne $R3E (Sector3s r3e.h, versjon 3) |
| [Richard Burns Rally (direkte data)](game-richard-burns-rally.md) | telemetry | ja | NGP-plugin-UDP-telemetri, 127.0.0.1:6776 (RichardBurnsRally.ini [NGP] udpTelemetry=1) |
| [Rocket League (spilltilstand)](game-rocketleague-stats.md) | gsi | ja | Stats API: TCP JSON-strøm fra 127.0.0.1:49123 (port i `<RL>\TAGame\Config\TAStatsAPI.ini` eller DefaultStatsAPI.ini) |
| [Squad (repriser)](game-squad-demos.md) | replay | ja | tjenerdemoer Squad tar opp med admin-kommandoen AdminDemoRec: `<server>/SquadGame/Saved/Demos/*.replay`, lest av den eksterne leseren `heat3d-squad-demo` (exporters/ext/squad-demo) |
| [Star Citizen (loggfiler)](game-starcitizen.md) | log | nei | `<install>\StarCitizen\LIVE\Game.log` (byggemappen til den kjørende StarCitizen.exe), bare loggfilen spillet skriver - et spill med Easy Anti-Cheat: ingenting berører prosessen |
| [Steam-statistikk (plattform)](game-steam-stats.md) | platform | nei | Steams lokale statistikkbuffer `%STEAM%\appcache\stats\UserGameStats_<account>_<appid>.bin` med `UserGameStatsSchema_<appid>.bin`; spilletid fra `%STEAM%\userdata\<account>\config\localconfig.vdf` (%STEAM% fra `HKCU\Software\Valve\Steam` SteamPath) |
| [Steam Timeline (plattform)](game-steam-timeline.md) | platform | nei | `%STEAM%\userdata\<account>\gamerecordings\timelines\timeline_<appid><date>_<time>.json` |
| [VALORANT (repriser)](game-valorant-replays.md) | replay | nei | repriser VALORANT lagrer: `%LOCALAPPDATA%/VALORANT/Saved/Demos/*.vrf` (bare de delene som ikke er tilslørt) |
| [War Thunder (repriser)](game-warthunder-replays.md) | replay | ja | repriser War Thunder lagrer: `<War Thunder>/Replays/*.wrpl` (med repriselagring på), konvertert av det eksterne konverteringsverktøyet `heat3d-wt-replay` (exporters/ext/warthunder-replay) |
| [War Thunder (spilltilstand)](game-warthunder-webmap.md) | gsi | ja | spillets lokale webkart, <http://127.0.0.1:8111> (/map_info.json, /map_obj.json, /state, /indicators, /hudmsg, /gamechat, /mission.json, /map.img) |
| [World of Tanks (repriser)](game-wot-replays.md) | replay | ja | repriser World of Tanks lagrer: `<World of Tanks>/replays/*.wotreplay` (med slagopptak på), konvertert av det eksterne konverteringsverktøyet `heat3d-wot-replay` (exporters/ext/wot-replay) |
| [World of Warships (repriser)](game-wows-replays.md) | replay | ja | repriser World of Warships lagrer: `<World of Warships>/replays/*.wowsreplay` (med repriser på), konvertert av det eksterne konverteringsverktøyet `heat3d-wows-replay` (exporters/ext/wows-replay) |
| [X-Plane (direkte data)](game-xplane.md) | telemetry | ja | X-Planes UDP-grensesnitt på 127.0.0.1:49000 (RREF-datarefs og RPOS-posisjon, svart til watcheren) |

Spill som ikke tas opp, og hvorfor: [Kilder og regler](sources-and-rules.md#what-is-declined-and-why). Alt i én tabell, slik `python -m heat3d_watch games --markdown` skriver det ut: [Alle spill i én tabell](watcher.md).

<!-- Generated by tools/gen_game_pages.py; run it again after changing an adapter. -->
