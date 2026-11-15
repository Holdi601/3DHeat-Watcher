---
title: "Jocuri"
nav_order: 4
lang: "ro"
source: games.md
source_hash: "0766c0bb0763"
nav_exclude: true
search_exclude: true
---
# Jocuri {#games}

Watcher-ul cunoaște 50 de surse din 45 de jocuri și platforme. Fiecare are o pagină proprie, generată din adaptorul ei: ce înregistrează, de unde, cum o pornești, cum funcționează, axele ei, ce a fost verificat.

Tipuri: `telemetry`, `gsi`, `log`, `replay` și `platform` - vezi [Surse și reguli](sources-and-rules.md). Poziții: *da* când adaptorul scrie rânduri cu un loc, *împrumutată* când ia locul dintr-o altă înregistrare a aceluiași joc (vezi [NVIDIA Highlights](nvidia-highlights.md)), *nu* când sursa nu are niciunul. Profilele de memorie nu sunt listate: niciunul nu se livrează, iar fiecare jucător scrie pe al lui (vezi [Citirea memoriei](memory-reading.md)).

| Joc | Tip | Poziții | Sursă |
|---|---|---|---|
| [American Truck Simulator (date în timp real)](game-ats.md) | telemetry | da | memorie partajată `Local\SCSTelemetry`, scrisă de pluginul scs-sdk-plugin al RenCloud (revizia 12) din `<game>\bin\win_x64\plugins` |
| [Assetto Corsa (date în timp real)](game-assetto-corsa.md) | telemetry | da | memorie partajată `Local\acpmf_physics`, `Local\acpmf_graphics`, `Local\acpmf_static` |
| [Assetto Corsa Competizione (date în timp real)](game-assetto-corsa-competizione.md) | telemetry | da | memorie partajată `Local\acpmf_physics`, `Local\acpmf_graphics`, `Local\acpmf_static` |
| [Assetto Corsa EVO (date în timp real)](game-assetto-corsa-evo.md) | telemetry | da | memorie partajată `Local\acevo_pmf_physics`, `Local\acevo_pmf_static` |
| [Assetto Corsa Rally (date în timp real)](game-assetto-corsa-rally.md) | telemetry | da | memorie partajată `Local\acpmf_physics`, `Local\acpmf_static` (aceleași pagini ca AC și ACC) |
| [Automobilista 2 (date în timp real)](game-automobilista-2.md) | telemetry | da | memorie partajată $pcars2$ (layout-ul SMS SharedMemory.h) |
| [BeamNG.drive (date în timp real)](game-beamng.md) | telemetry | da | UDP 127.0.0.1:4460 din modul-ul de protocol heat3d (mods/beamng/heat3d din acest depozit) |
| [Counter-Strike 2 (reluări)](game-cs2-demos.md) | replay | da | demo-urile salvate de CS2: `<CS2>/game/csgo/replays/*.dem` (descărcate din istoricul meciurilor) și `<CS2>/game/csgo/*.dem` (înregistrate) |
| [Counter-Strike 2 (starea jocului)](game-cs2-gsi.md) | gsi | da | Game State Integration: cereri HTTP POST către 127.0.0.1:3311, configurate de `<CS2>\game\csgo\cfg\gamestate_integration_heat3d.cfg` |
| [DCS World (date în timp real)](game-dcs.md) | telemetry | da | hook-ul watcher-ului `%USERPROFILE%\Saved` `Games\DCS*\Scripts\Hooks\heat3d-watch.lua`, linii UDP către 127.0.0.1:41993 |
| [DiRT Rally 2.0 (date în timp real)](game-dirt-rally-2.md) | telemetry | da | UDP 127.0.0.1:20777, extradata=3 `(Documents\My` `Games\DiRT` Rally `2.0\hardwaresettings\hardware_settings_config.xml`); cât timp altă aplicație ține portul 20777, watcher-ul îl lasă ei |
| [Dota 2 (reluări)](game-dota-replays.md) | replay | da | reluările salvate de Dota 2: `<Dota>/game/dota/replays/<match id>.dem` (descărcate în client, sau cu `dota-replay <match id>`) |
| [Dota 2 (starea jocului)](game-dota2-gsi.md) | gsi | da | Game State Integration: cereri HTTP POST către 127.0.0.1:3312, configurate de `<Dota>\game\dota\cfg\gamestate_integration\gamestate_integration_heat3d.cfg` |
| [EA SPORTS F1 23 (date în timp real)](game-f1-23.md) | telemetry | da | telemetrie UDP 127.0.0.1:20777 `(Documents\My` `Games\F1` `23\hardwaresettings\hardware_settings_config.xml`) |
| [EA SPORTS F1 24 (date în timp real)](game-f1-24.md) | telemetry | da | telemetrie UDP 127.0.0.1:20777 `(Documents\My` `Games\F1` `24\hardwaresettings\hardware_settings_config.xml`) |
| [EA SPORTS F1 25 (date în timp real)](game-f1-25.md) | telemetry | da | telemetrie UDP 127.0.0.1:20777 `(Documents\My` `Games\F1` `25\hardwaresettings\hardware_settings_config.xml`) |
| [EA SPORTS WRC (date în timp real)](game-ea-wrc.md) | telemetry | da | UDP 127.0.0.1:20777, pachetul session_update al structurii implicite `wrc` `(Documents\My` `Games\WRC\telemetry\config.json`); cât timp altă aplicație ține portul 20777, watcher-ul îl lasă ei |
| [Elite Dangerous (fișiere de jurnal)](game-elite.md) | log | da | Jurnalul jucătorului `%USERPROFILE%\Saved` `Games\Frontier` `Developments\Elite` `Dangerous\Journal.*.log` (cel mai nou fișier, urmărit pe măsură ce se scrie), Status.json și celelalte fișiere `*.json` ale companionului (Market, Outfitting, Shipyard, NavRoute, Cargo, ModulesInfo, ShipLocker, Backpack, FCMaterials) din același folder |
| [Euro Truck Simulator 2 (date în timp real)](game-ets2.md) | telemetry | da | memorie partajată `Local\SCSTelemetry`, scrisă de pluginul scs-sdk-plugin al RenCloud (revizia 12) din `<game>\bin\win_x64\plugins` |
| [EVE Online (fișiere de jurnal)](game-eve.md) | log | nu | `%USERPROFILE%\Documents\EVE\logs\Gamelogs\*.txt` și `Chatlogs\*.txt` de lângă ele (fiecare fișier scris de când a pornit clientul) |
| [Forza Horizon 4 (date în timp real)](game-forza-horizon-4.md) | telemetry | da | Forza Data Out, UDP 127.0.0.1:5300 (formatul Dash); fiecare pachet retransmis neschimbat către 127.0.0.1:5301 |
| [Forza Horizon 5 (date în timp real)](game-forza-horizon-5.md) | telemetry | da | Forza Data Out, UDP 127.0.0.1:5300 (formatul Dash); fiecare pachet retransmis neschimbat către 127.0.0.1:5301 |
| [Forza Horizon 6 (date în timp real)](game-forza-horizon-6.md) | telemetry | da | Forza Data Out, UDP 127.0.0.1:5300 (formatul Dash); fiecare pachet retransmis neschimbat către 127.0.0.1:5301 |
| [Forza Motorsport (date în timp real)](game-forza-motorsport.md) | telemetry | da | Forza Data Out, UDP 127.0.0.1:5300 (formatul Dash); fiecare pachet retransmis neschimbat către 127.0.0.1:5301 |
| [Hearthstone (fișiere de jurnal)](game-hearthstone.md) | log | nu | `<install>\Logs\Power.log` (sau `Logs\Hearthstone_*\Power.log`), scris după ce `%LOCALAPPDATA%\Blizzard\Hearthstone\log.config` are o secțiune [Power], și orice alt `*.log` pe care îl scrie jocul acolo |
| [IL-2 Sturmovik: Great Battles (date în timp real)](game-il2.md) | telemetry | nu | ieșirea UDP de telemetrie a jocului către 127.0.0.1:41995 ([KEY = telemetrydevice] în `<game>\data\startup.cfg`) |
| [IL-2 Sturmovik: Great Battles (reluări)](game-il2-tacview.md) | replay | da | înregistrările Tacview ale jocului `<game>\data\Tracks\*.acmi` (text ACMI 2.x, simplu sau zipat) |
| [iRacing (date în timp real)](game-iracing.md) | telemetry | nu | memorie partajată `Local\IRSDKMemMapFileName` (SDK-ul iRacing); fișierele .ibt din `%USERPROFILE%\Documents\iRacing\telemetry` |
| [League of Legends (starea jocului)](game-lol-live.md) | gsi | nu | API-ul Live Client Data al clientului de joc, <https://127.0.0.1:2999/liveclientdata/> (allgamedata, eventdata), în timpul unui meci |
| [League of Legends (reluări)](game-lol-replays.md) | replay | da | reluările salvate de clientul League: %USERPROFILE%/Documents/League of `Legends/Replays/*.rofl` (doar metadatele simple de la sfârșitul jocului); cu propria ta cheie de API Riot, cronologia oficială a meciului din API-ul Match-V5 al Riot |
| [Microsoft Flight Simulator 2020 (date în timp real)](game-msfs2020.md) | telemetry | da | SimConnect prin propriul SimConnect.dll al jucătorului (folderul simulatorului, sau `%MSFS_SDK%\SimConnect` `SDK\lib`) |
| [Microsoft Flight Simulator 2024 (date în timp real)](game-msfs2024.md) | telemetry | da | SimConnect prin propriul SimConnect.dll al jucătorului (folderul simulatorului, sau `%MSFS2024_SDK%\SimConnect` `SDK\lib`) |
| [Minecraft (fișiere de jurnal)](game-minecraft.md) | log | da | `%APPDATA%\.minecraft\logs\latest.log` (urmărit), `saves\<world>\stats\<uuid>.json` și `saves\<world>\playerdata\<uuid>.dat` / level.dat (NBT comprimat cu gzip), citite când jocul le salvează |
| [NVIDIA highlights (platformă)](game-nvidia-highlights.md) | platform | împrumutată | `%LOCALAPPDATA%\NVIDIA` `Corporation\NVIDIA` `Overlay\UGCTracker.json`, GallerySettings.json, `Highlights\<game>\config.json`; clipurile din folderul de capturi `(%USERPROFILE%\Videos\NVIDIA\<Game>\*.mp4`) și `<temp>\Highlights\<game>`; `%LOCALAPPDATA%\NVIDIA` `Corporation\GfeSDK\<exe>_<pid>.log` |
| [osu! (reluări)](game-osu-replays.md) | replay | da | reluările salvate de osu! (versiunea stabilă): `%LOCALAPPDATA%/osu!/Data/r/*.osr` (fiecare joc) și `osu!/Replays/*.osr` (exportate) |
| [Path of Exile (fișiere de jurnal)](game-poe.md) | log | nu | `<install>\logs\Client.txt` din Path of Exile sau Path of Exile 2 (urmărit; folderul de instalare este cel al executabilului care rulează) |
| [Project CARS 2 (date în timp real)](game-project-cars-2.md) | telemetry | da | memorie partajată $pcars2$ (SMS SharedMemory.h) |
| [RaceRoom Racing Experience (date în timp real)](game-raceroom.md) | telemetry | da | memorie partajată $R3E (r3e.h al Sector3, versiunea 3) |
| [Richard Burns Rally (date în timp real)](game-richard-burns-rally.md) | telemetry | da | telemetrie UDP a pluginului NGP, 127.0.0.1:6776 (RichardBurnsRally.ini [NGP] udpTelemetry=1) |
| [Rocket League (starea jocului)](game-rocketleague-stats.md) | gsi | da | API-ul de statistici: flux TCP JSON de la 127.0.0.1:49123 (portul din `<RL>\TAGame\Config\TAStatsAPI.ini` sau DefaultStatsAPI.ini) |
| [Squad (reluări)](game-squad-demos.md) | replay | da | demo-urile de server pe care le înregistrează Squad cu comanda de admin AdminDemoRec: `<server>/SquadGame/Saved/Demos/*.replay`, citite de cititorul extern `heat3d-squad-demo` (exporters/ext/squad-demo) |
| [Star Citizen (fișiere de jurnal)](game-starcitizen.md) | log | nu | `<install>\StarCitizen\LIVE\Game.log` (folderul de build al StarCitizen.exe care rulează), doar fișierul de jurnal pe care îl scrie jocul - un joc cu Easy Anti-Cheat: nimic nu atinge procesul lui |
| [Statistici Steam (platformă)](game-steam-stats.md) | platform | nu | cache-ul local de statistici al Steam `%STEAM%\appcache\stats\UserGameStats_<account>_<appid>.bin` cu `UserGameStatsSchema_<appid>.bin`; timpul de joc din `%STEAM%\userdata\<account>\config\localconfig.vdf` (%STEAM% din `HKCU\Software\Valve\Steam` SteamPath) |
| [Steam Timeline (platformă)](game-steam-timeline.md) | platform | nu | `%STEAM%\userdata\<account>\gamerecordings\timelines\timeline_<appid><date>_<time>.json` |
| [VALORANT (reluări)](game-valorant-replays.md) | replay | nu | reluările salvate de VALORANT: `%LOCALAPPDATA%/VALORANT/Saved/Demos/*.vrf` (doar părțile care nu sunt ofuscate) |
| [War Thunder (reluări)](game-warthunder-replays.md) | replay | da | reluările salvate de War Thunder: `<War Thunder>/Replays/*.wrpl` (cu salvarea reluărilor pornită), convertite de convertorul extern `heat3d-wt-replay` (exporters/ext/warthunder-replay) |
| [War Thunder (starea jocului)](game-warthunder-webmap.md) | gsi | da | harta web locală a jocului, <http://127.0.0.1:8111> (/map_info.json, /map_obj.json, /state, /indicators, /hudmsg, /gamechat, /mission.json, /map.img) |
| [World of Tanks (reluări)](game-wot-replays.md) | replay | da | reluările salvate de World of Tanks: `<World of Tanks>/replays/*.wotreplay` (cu înregistrarea bătăliilor pornită), convertite de convertorul extern `heat3d-wot-replay` (exporters/ext/wot-replay) |
| [World of Warships (reluări)](game-wows-replays.md) | replay | da | reluările salvate de World of Warships: `<World of Warships>/replays/*.wowsreplay` (cu reluările pornite), convertite de convertorul extern `heat3d-wows-replay` (exporters/ext/wows-replay) |
| [X-Plane (date în timp real)](game-xplane.md) | telemetry | da | interfața UDP a X-Plane pe 127.0.0.1:49000 (datarefs RREF și RPOS pentru poziție, răspunsuri către watcher) |

Jocurile care nu sunt înregistrate, și de ce: [Surse și reguli](sources-and-rules.md#what-is-declined-and-why). Totul într-un singur tabel, așa cum îl afișează `python -m heat3d_watch games --markdown`: [Toate jocurile într-un tabel](watcher.md).

<!-- Generated by tools/gen_game_pages.py; run it again after changing an adapter. -->
