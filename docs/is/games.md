---
title: "Leikir"
nav_order: 4
lang: "is"
source: games.md
source_hash: "c601550fbb4e"
nav_exclude: true
search_exclude: true
---
# Leikir {#games}

Watcher þekkir 49 heimildir í 44 leikjum og vettvöngum. Hver hefur sína eigin síðu, búna til úr millistykki sínu: hvað hún skráir, hvaðan, hvernig á að kveikja á henni, hvernig hún virkar, ása hennar og hvað var staðfest.

Gerðir: `telemetry`, `gsi`, `log`, `replay` og `platform` - sjá [Heimildir og reglur](sources-and-rules.md). Staðsetningar: *já* þegar millistykkið skrifar raðir með stað, *fengið að láni* þegar það tekur staðinn úr annarri upptöku af sama leik (sjá [NVIDIA Highlights](nvidia-highlights.md)), *nei* þegar heimildin hefur enga. Minnissnið eru ekki talin upp: engin fylgja með, og hver spilari skrifar sitt eigið (sjá [Minnislestur](memory-reading.md)).

| Leikur | Gerð | Staðsetningar | Heimild |
|---|---|---|---|
| [American Truck Simulator (lifandi gögn)](game-ats.md) | telemetry | já | samnýtt minni `Local\SCSTelemetry` sem RenCloud scs-sdk-plugin (útgáfa 12) skrifar í `<game>\bin\win_x64\plugins` |
| [Assetto Corsa (lifandi gögn)](game-assetto-corsa.md) | telemetry | já | samnýtt minni `Local\acpmf_physics`, `Local\acpmf_graphics`, `Local\acpmf_static` |
| [Assetto Corsa Competizione (lifandi gögn)](game-assetto-corsa-competizione.md) | telemetry | já | samnýtt minni `Local\acpmf_physics`, `Local\acpmf_graphics`, `Local\acpmf_static` |
| [Assetto Corsa EVO (lifandi gögn)](game-assetto-corsa-evo.md) | telemetry | já | samnýtt minni `Local\acevo_pmf_physics`, `Local\acevo_pmf_static` |
| [Assetto Corsa Rally (lifandi gögn)](game-assetto-corsa-rally.md) | telemetry | já | samnýtt minni `Local\acpmf_physics`, `Local\acpmf_static` (sömu síður og AC og ACC) |
| [Automobilista 2 (lifandi gögn)](game-automobilista-2.md) | telemetry | já | samnýtt minni $pcars2$ (SMS SharedMemory.h snið) |
| [BeamNG.drive (lifandi gögn)](game-beamng.md) | telemetry | já | UDP 127.0.0.1:4460 frá heat3d-samskiptamódinu (mods/beamng/heat3d í þessari geymslu) |
| [Counter-Strike 2 (endursýningar)](game-cs2-demos.md) | replay | já | demó sem CS2 vistar: `<CS2>/game/csgo/replays/*.dem` (sótt úr leikjasögunni) og `<CS2>/game/csgo/*.dem` (tekin upp) |
| [Counter-Strike 2 (leikjastaða)](game-cs2-gsi.md) | gsi | já | Game State Integration: HTTP POST á 127.0.0.1:3311, stillt með `<CS2>\game\csgo\cfg\gamestate_integration_heat3d.cfg` |
| [DCS World (lifandi gögn)](game-dcs.md) | telemetry | já | krókur watcher `%USERPROFILE%\Saved` `Games\DCS*\Scripts\Hooks\heat3d-watch.lua`, UDP-línur á 127.0.0.1:41993 |
| [DiRT Rally 2.0 (lifandi gögn)](game-dirt-rally-2.md) | telemetry | já | UDP 127.0.0.1:20777, extradata=3 `(Documents\My` `Games\DiRT` Rally `2.0\hardwaresettings\hardware_settings_config.xml`); meðan annað forrit heldur 20777 lætur watcher það hafa gáttina |
| [Dota 2 (endursýningar)](game-dota-replays.md) | replay | já | endursýningar sem Dota 2 vistar: `<Dota>/game/dota/replays/<match id>.dem` (sóttar í biðlaranum, eða með `dota-replay <match id>`) |
| [Dota 2 (leikjastaða)](game-dota2-gsi.md) | gsi | já | Game State Integration: HTTP POST á 127.0.0.1:3312, stillt með `<Dota>\game\dota\cfg\gamestate_integration\gamestate_integration_heat3d.cfg` |
| [EA SPORTS F1 23 (lifandi gögn)](game-f1-23.md) | telemetry | já | UDP-fjarmæling 127.0.0.1:20777 `(Documents\My` `Games\F1` `23\hardwaresettings\hardware_settings_config.xml`) |
| [EA SPORTS F1 24 (lifandi gögn)](game-f1-24.md) | telemetry | já | UDP-fjarmæling 127.0.0.1:20777 `(Documents\My` `Games\F1` `24\hardwaresettings\hardware_settings_config.xml`) |
| [EA SPORTS F1 25 (lifandi gögn)](game-f1-25.md) | telemetry | já | UDP-fjarmæling 127.0.0.1:20777 `(Documents\My` `Games\F1` `25\hardwaresettings\hardware_settings_config.xml`) |
| [EA SPORTS WRC (lifandi gögn)](game-ea-wrc.md) | telemetry | já | UDP 127.0.0.1:20777, session_update-pakki sjálfgefnu `wrc`-gerðarinnar `(Documents\My` `Games\WRC\telemetry\config.json`); meðan annað forrit heldur 20777 lætur watcher það hafa gáttina |
| [Elite Dangerous (annálaskrár)](game-elite.md) | log | já | Player Journal `%USERPROFILE%\Saved` `Games\Frontier` `Developments\Elite` `Dangerous\Journal.*.log` (nýjasta skráin, fylgt eftir meðan hún er skrifuð), Status.json og hinar fylgiskrárnar `*.json` (Market, Outfitting, Shipyard, NavRoute, Cargo, ModulesInfo, ShipLocker, Backpack, FCMaterials) í sömu möppu |
| [Euro Truck Simulator 2 (lifandi gögn)](game-ets2.md) | telemetry | já | samnýtt minni `Local\SCSTelemetry` sem RenCloud scs-sdk-plugin (útgáfa 12) skrifar í `<game>\bin\win_x64\plugins` |
| [EVE Online (annálaskrár)](game-eve.md) | log | nei | `%USERPROFILE%\Documents\EVE\logs\Gamelogs\*.txt` og `Chatlogs\*.txt` við hliðina (hver skrá sem hefur verið skrifuð frá því biðlarinn ræsti) |
| [Forza Horizon 4 (lifandi gögn)](game-forza-horizon-4.md) | telemetry | já | Forza Data Out, UDP 127.0.0.1:5300 (Dash-snið); hver pakki áframsendur óbreyttur á 127.0.0.1:5301 |
| [Forza Horizon 5 (lifandi gögn)](game-forza-horizon-5.md) | telemetry | já | Forza Data Out, UDP 127.0.0.1:5300 (Dash-snið); hver pakki áframsendur óbreyttur á 127.0.0.1:5301 |
| [Forza Horizon 6 (lifandi gögn)](game-forza-horizon-6.md) | telemetry | já | Forza Data Out, UDP 127.0.0.1:5300 (Dash-snið); hver pakki áframsendur óbreyttur á 127.0.0.1:5301 |
| [Forza Motorsport (lifandi gögn)](game-forza-motorsport.md) | telemetry | já | Forza Data Out, UDP 127.0.0.1:5300 (Dash-snið); hver pakki áframsendur óbreyttur á 127.0.0.1:5301 |
| [Hearthstone (annálaskrár)](game-hearthstone.md) | log | nei | `<install>\Logs\Power.log` (eða `Logs\Hearthstone_*\Power.log`), skrifuð þegar `%LOCALAPPDATA%\Blizzard\Hearthstone\log.config` hefur [Power] hluta, og hver önnur `*.log` sem leikurinn skrifar þar |
| [IL-2 Sturmovik: Great Battles (lifandi gögn)](game-il2.md) | telemetry | nei | UDP-fjarmælingarúttak leiksins á 127.0.0.1:41995 ([KEY = telemetrydevice] í `<game>\data\startup.cfg`) |
| [IL-2 Sturmovik: Great Battles (endursýningar)](game-il2-tacview.md) | replay | já | eigin Tacview-upptökur leiksins `<game>\data\Tracks\*.acmi` (ACMI 2.x texti, venjulegur eða zippaður) |
| [iRacing (lifandi gögn)](game-iracing.md) | telemetry | nei | samnýtt minni `Local\IRSDKMemMapFileName` (iRacing SDK); .ibt-skrár í `%USERPROFILE%\Documents\iRacing\telemetry` |
| [League of Legends (leikjastaða)](game-lol-live.md) | gsi | nei | Live Client Data API leikjabiðlarans, <https://127.0.0.1:2999/liveclientdata/> (allgamedata, eventdata), meðan á viðureign stendur |
| [League of Legends (endursýningar)](game-lol-replays.md) | replay | já | endursýningar sem League-biðlarinn vistar: %USERPROFILE%/Documents/League of `Legends/Replays/*.rofl` (aðeins venjuleg lýsigögn í lok leiks); með þínum eigin Riot API lykli, opinber tímalína viðureignarinnar úr Match-V5 API Riot |
| [Microsoft Flight Simulator 2020 (lifandi gögn)](game-msfs2020.md) | telemetry | já | SimConnect í gegnum SimConnect.dll spilarans sjálfs (hermismappan, eða `%MSFS_SDK%\SimConnect` `SDK\lib`) |
| [Microsoft Flight Simulator 2024 (lifandi gögn)](game-msfs2024.md) | telemetry | já | SimConnect í gegnum SimConnect.dll spilarans sjálfs (hermismappan, eða `%MSFS2024_SDK%\SimConnect` `SDK\lib`) |
| [Minecraft (annálaskrár)](game-minecraft.md) | log | já | `%APPDATA%\.minecraft\logs\latest.log` (fylgt eftir), `saves\<world>\stats\<uuid>.json` og `saves\<world>\playerdata\<uuid>.dat` / level.dat (gzip NBT), lesið þegar leikurinn vistar þær |
| [NVIDIA highlights (vettvangur)](game-nvidia-highlights.md) | platform | fengið að láni | `%LOCALAPPDATA%\NVIDIA` `Corporation\NVIDIA` `Overlay\UGCTracker.json`, GallerySettings.json, `Highlights\<game>\config.json`; klippur í upptökumöppunni `(%USERPROFILE%\Videos\NVIDIA\<Game>\*.mp4`) og `<temp>\Highlights\<game>`; `%LOCALAPPDATA%\NVIDIA` `Corporation\GfeSDK\<exe>_<pid>.log` |
| [Path of Exile (annálaskrár)](game-poe.md) | log | nei | `<install>\logs\Client.txt` í Path of Exile eða Path of Exile 2 (fylgt eftir; uppsetningarmappan er mappa keyrsluskrárinnar sem er í gangi) |
| [Project CARS 2 (lifandi gögn)](game-project-cars-2.md) | telemetry | já | samnýtt minni $pcars2$ (SMS SharedMemory.h) |
| [RaceRoom Racing Experience (lifandi gögn)](game-raceroom.md) | telemetry | já | samnýtt minni $R3E (r3e.h frá Sector3, útgáfa 3) |
| [Richard Burns Rally (lifandi gögn)](game-richard-burns-rally.md) | telemetry | já | UDP-fjarmæling NGP-viðbótarinnar, 127.0.0.1:6776 (RichardBurnsRally.ini [NGP] udpTelemetry=1) |
| [Rocket League (leikjastaða)](game-rocketleague-stats.md) | gsi | já | Stats API: TCP JSON-straumur frá 127.0.0.1:49123 (Port í `<RL>\TAGame\Config\TAStatsAPI.ini` eða DefaultStatsAPI.ini) |
| [Squad (endursýningar)](game-squad-demos.md) | replay | já | þjónademó sem Squad tekur upp með stjórnandaskipuninni AdminDemoRec: `<server>/SquadGame/Saved/Demos/*.replay`, lesin af ytri lesaranum `heat3d-squad-demo` (exporters/ext/squad-demo) |
| [Star Citizen (annálaskrár)](game-starcitizen.md) | log | nei | `<install>\StarCitizen\LIVE\Game.log` (byggingarmappa StarCitizen.exe sem er í gangi), aðeins annálaskráin sem leikurinn skrifar - leikur með Easy Anti-Cheat: ekkert snertir ferli hans |
| [Steam statistics (vettvangur)](game-steam-stats.md) | platform | nei | staðbundið tölfræðiskyndiminni Steam `%STEAM%\appcache\stats\UserGameStats_<account>_<appid>.bin` með `UserGameStatsSchema_<appid>.bin`; spilatími úr `%STEAM%\userdata\<account>\config\localconfig.vdf` (%STEAM% úr `HKCU\Software\Valve\Steam` SteamPath) |
| [Steam Timeline (vettvangur)](game-steam-timeline.md) | platform | nei | `%STEAM%\userdata\<account>\gamerecordings\timelines\timeline_<appid><date>_<time>.json` |
| [VALORANT (endursýningar)](game-valorant-replays.md) | replay | nei | endursýningar sem VALORANT vistar: `%LOCALAPPDATA%/VALORANT/Saved/Demos/*.vrf` (aðeins þeir hlutar sem eru ekki duldir) |
| [War Thunder (endursýningar)](game-warthunder-replays.md) | replay | já | endursýningar sem War Thunder vistar: `<War Thunder>/Replays/*.wrpl` (með endursýningavistun á), umbreyttar af ytri umbreytinum `heat3d-wt-replay` (exporters/ext/warthunder-replay) |
| [War Thunder (leikjastaða)](game-warthunder-webmap.md) | gsi | já | staðbundið vefkort leiksins, <http://127.0.0.1:8111> (/map_info.json, /map_obj.json, /state, /indicators, /hudmsg, /gamechat, /mission.json, /map.img) |
| [World of Tanks (endursýningar)](game-wot-replays.md) | replay | já | endursýningar sem World of Tanks vistar: `<World of Tanks>/replays/*.wotreplay` (með bardagaupptöku á), umbreyttar af ytri umbreytinum `heat3d-wot-replay` (exporters/ext/wot-replay) |
| [World of Warships (endursýningar)](game-wows-replays.md) | replay | já | endursýningar sem World of Warships vistar: `<World of Warships>/replays/*.wowsreplay` (með endursýningar á), umbreyttar af ytri umbreytinum `heat3d-wows-replay` (exporters/ext/wows-replay) |
| [X-Plane (lifandi gögn)](game-xplane.md) | telemetry | já | UDP-viðmót X-Plane á 127.0.0.1:49000 (RREF datarefs og RPOS staða, svarað til watcher) |

Leikir sem eru ekki skráðir, og hvers vegna: [Heimildir og reglur](sources-and-rules.md#what-is-declined-and-why). Allt í einni töflu, eins og `python -m heat3d_watch games --markdown` prentar það: [Allir leikir í einni töflu](watcher.md).

<!-- Generated by tools/gen_game_pages.py; run it again after changing an adapter. -->
