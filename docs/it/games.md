---
title: Giochi
nav_order: 4
lang: "it"
source: games.md
source_hash: "c601550fbb4e"
nav_exclude: true
search_exclude: true
---
# Giochi {#games}

Il watcher conosce 49 fonti in 44 giochi e piattaforme. Ognuna ha una pagina tutta sua, generata dal suo adattatore: cosa registra, da dove, come attivarla, come funziona, i suoi assi, cosa è stato verificato.

Tipi: `telemetry`, `gsi`, `log`, `replay` e `platform` - vedi [Fonti e regole](sources-and-rules.md). Posizioni: *sì* quando l'adattatore scrive righe con un luogo, *preso in prestito* quando la prende da un'altra registrazione dello stesso gioco (vedi [NVIDIA Highlights](nvidia-highlights.md)), *no* quando la fonte non ne ha. I profili di memoria non sono elencati: nessuno viene distribuito, e ognuno scrive il suo (vedi [Lettura della memoria](memory-reading.md)).

| Gioco | Tipo | Posizioni | Fonte |
|---|---|---|---|
| [American Truck Simulator (dati in tempo reale)](game-ats.md) | telemetry | sì | memoria condivisa `Local\SCSTelemetry` scritta dal plugin scs-sdk-plugin di RenCloud (revisione 12) in `<game>\bin\win_x64\plugins` |
| [Assetto Corsa (dati in tempo reale)](game-assetto-corsa.md) | telemetry | sì | memoria condivisa `Local\acpmf_physics`, `Local\acpmf_graphics`, `Local\acpmf_static` |
| [Assetto Corsa Competizione (dati in tempo reale)](game-assetto-corsa-competizione.md) | telemetry | sì | memoria condivisa `Local\acpmf_physics`, `Local\acpmf_graphics`, `Local\acpmf_static` |
| [Assetto Corsa EVO (dati in tempo reale)](game-assetto-corsa-evo.md) | telemetry | sì | memoria condivisa `Local\acevo_pmf_physics`, `Local\acevo_pmf_static` |
| [Assetto Corsa Rally (dati in tempo reale)](game-assetto-corsa-rally.md) | telemetry | sì | memoria condivisa `Local\acpmf_physics`, `Local\acpmf_static` (le stesse pagine di AC e ACC) |
| [Automobilista 2 (dati in tempo reale)](game-automobilista-2.md) | telemetry | sì | memoria condivisa $pcars2$ (layout SMS SharedMemory.h) |
| [BeamNG.drive (dati in tempo reale)](game-beamng.md) | telemetry | sì | UDP 127.0.0.1:4460 dalla mod di protocollo heat3d (mods/beamng/heat3d in questo repository) |
| [Counter-Strike 2 (replay)](game-cs2-demos.md) | replay | sì | demo salvati da CS2: `<CS2>/game/csgo/replays/*.dem` (scaricati dallo storico delle partite) e `<CS2>/game/csgo/*.dem` (registrati) |
| [Counter-Strike 2 (stato di gioco)](game-cs2-gsi.md) | gsi | sì | Game State Integration: richieste HTTP POST a 127.0.0.1:3311, configurate dal file `<CS2>\game\csgo\cfg\gamestate_integration_heat3d.cfg` |
| [DCS World (dati in tempo reale)](game-dcs.md) | telemetry | sì | l'hook del watcher `%USERPROFILE%\Saved` `Games\DCS*\Scripts\Hooks\heat3d-watch.lua`, righe UDP a 127.0.0.1:41993 |
| [DiRT Rally 2.0 (dati in tempo reale)](game-dirt-rally-2.md) | telemetry | sì | UDP 127.0.0.1:20777, extradata=3 `(Documents\My` `Games\DiRT` Rally `2.0\hardwaresettings\hardware_settings_config.xml`); mentre un'altra app usa la 20777, il watcher lascia la porta a quell'app |
| [Dota 2 (replay)](game-dota-replays.md) | replay | sì | replay salvati da Dota 2: `<Dota>/game/dota/replays/<id partita>.dem` (scaricati nel client, oppure con `dota-replay <id partita>`) |
| [Dota 2 (stato di gioco)](game-dota2-gsi.md) | gsi | sì | Game State Integration: richieste HTTP POST a 127.0.0.1:3312, configurate dal file `<Dota>\game\dota\cfg\gamestate_integration\gamestate_integration_heat3d.cfg` |
| [EA SPORTS F1 23 (dati in tempo reale)](game-f1-23.md) | telemetry | sì | telemetria UDP 127.0.0.1:20777 `(Documents\My` `Games\F1` `23\hardwaresettings\hardware_settings_config.xml`) |
| [EA SPORTS F1 24 (dati in tempo reale)](game-f1-24.md) | telemetry | sì | telemetria UDP 127.0.0.1:20777 `(Documents\My` `Games\F1` `24\hardwaresettings\hardware_settings_config.xml`) |
| [EA SPORTS F1 25 (dati in tempo reale)](game-f1-25.md) | telemetry | sì | telemetria UDP 127.0.0.1:20777 `(Documents\My` `Games\F1` `25\hardwaresettings\hardware_settings_config.xml`) |
| [EA SPORTS WRC (dati in tempo reale)](game-ea-wrc.md) | telemetry | sì | UDP 127.0.0.1:20777, il pacchetto session_update della struttura `wrc` predefinita `(Documents\My` `Games\WRC\telemetry\config.json`); mentre un'altra app usa la 20777, il watcher lascia la porta a quell'app |
| [Elite Dangerous (file di log)](game-elite.md) | log | sì | Player Journal `%USERPROFILE%\Saved` `Games\Frontier` `Developments\Elite` `Dangerous\Journal.*.log` (il file più recente, seguito mentre viene scritto), Status.json e gli altri file `*.json` di supporto (Market, Outfitting, Shipyard, NavRoute, Cargo, ModulesInfo, ShipLocker, Backpack, FCMaterials) nella stessa cartella |
| [Euro Truck Simulator 2 (dati in tempo reale)](game-ets2.md) | telemetry | sì | memoria condivisa `Local\SCSTelemetry` scritta dal plugin scs-sdk-plugin di RenCloud (revisione 12) in `<game>\bin\win_x64\plugins` |
| [EVE Online (file di log)](game-eve.md) | log | no | `%USERPROFILE%\Documents\EVE\logs\Gamelogs\*.txt` e i `Chatlogs\*.txt` accanto ad essi (ogni file scritto da quando il client è partito) |
| [Forza Horizon 4 (dati in tempo reale)](game-forza-horizon-4.md) | telemetry | sì | Forza Data Out, UDP 127.0.0.1:5300 (formato Dash); ogni pacchetto inoltrato invariato a 127.0.0.1:5301 |
| [Forza Horizon 5 (dati in tempo reale)](game-forza-horizon-5.md) | telemetry | sì | Forza Data Out, UDP 127.0.0.1:5300 (formato Dash); ogni pacchetto inoltrato invariato a 127.0.0.1:5301 |
| [Forza Horizon 6 (dati in tempo reale)](game-forza-horizon-6.md) | telemetry | sì | Forza Data Out, UDP 127.0.0.1:5300 (formato Dash); ogni pacchetto inoltrato invariato a 127.0.0.1:5301 |
| [Forza Motorsport (dati in tempo reale)](game-forza-motorsport.md) | telemetry | sì | Forza Data Out, UDP 127.0.0.1:5300 (formato Dash); ogni pacchetto inoltrato invariato a 127.0.0.1:5301 |
| [Hearthstone (file di log)](game-hearthstone.md) | log | no | `<install>\Logs\Power.log` (oppure `Logs\Hearthstone_*\Power.log`), scritto una volta che `%LOCALAPPDATA%\Blizzard\Hearthstone\log.config` ha una sezione [Power], e ogni altro `*.log` che il gioco scrive lì |
| [IL-2 Sturmovik: Great Battles (dati in tempo reale)](game-il2.md) | telemetry | no | l'output UDP di telemetria del gioco verso 127.0.0.1:41995 (`[KEY = telemetrydevice]` in `<game>\data\startup.cfg`) |
| [IL-2 Sturmovik: Great Battles (replay)](game-il2-tacview.md) | replay | sì | le registrazioni Tacview del gioco `<game>\data\Tracks\*.acmi` (testo ACMI 2.x, semplice o compresso) |
| [iRacing (dati in tempo reale)](game-iracing.md) | telemetry | no | memoria condivisa `Local\IRSDKMemMapFileName` (l'SDK di iRacing); file .ibt in `%USERPROFILE%\Documents\iRacing\telemetry` |
| [League of Legends (stato di gioco)](game-lol-live.md) | gsi | no | Live Client Data API del client di gioco, <https://127.0.0.1:2999/liveclientdata/> (allgamedata, eventdata), durante una partita |
| [League of Legends (replay)](game-lol-replays.md) | replay | sì | replay salvati dal client di League: %USERPROFILE%/Documents/League of `Legends/Replays/*.rofl` (solo i normali dati di fine partita); con una tua chiave API Riot, la timeline ufficiale della partita dalla Match-V5 API di Riot |
| [Microsoft Flight Simulator 2020 (dati in tempo reale)](game-msfs2020.md) | telemetry | sì | SimConnect tramite il SimConnect.dll del giocatore (la cartella del simulatore, oppure `%MSFS_SDK%\SimConnect` `SDK\lib`) |
| [Microsoft Flight Simulator 2024 (dati in tempo reale)](game-msfs2024.md) | telemetry | sì | SimConnect tramite il SimConnect.dll del giocatore (la cartella del simulatore, oppure `%MSFS2024_SDK%\SimConnect` `SDK\lib`) |
| [Minecraft (file di log)](game-minecraft.md) | log | sì | `%APPDATA%\.minecraft\logs\latest.log` (seguito), `saves\<mondo>\stats\<uuid>.json` e `saves\<mondo>\playerdata\<uuid>.dat` / level.dat (NBT compresso con gzip), letti quando il gioco li salva |
| [NVIDIA highlights (piattaforma)](game-nvidia-highlights.md) | platform | preso in prestito | `%LOCALAPPDATA%\NVIDIA` `Corporation\NVIDIA` `Overlay\UGCTracker.json`, GallerySettings.json, `Highlights\<game>\config.json`; clip nella cartella di acquisizione `(%USERPROFILE%\Videos\NVIDIA\<Game>\*.mp4`) e `<temp>\Highlights\<game>`; `%LOCALAPPDATA%\NVIDIA` `Corporation\GfeSDK\<exe>_<pid>.log` |
| [Path of Exile (file di log)](game-poe.md) | log | no | `<install>\logs\Client.txt` di Path of Exile o Path of Exile 2 (seguito; la cartella di installazione è quella dell'eseguibile in esecuzione) |
| [Project CARS 2 (dati in tempo reale)](game-project-cars-2.md) | telemetry | sì | memoria condivisa $pcars2$ (SMS SharedMemory.h) |
| [RaceRoom Racing Experience (dati in tempo reale)](game-raceroom.md) | telemetry | sì | memoria condivisa $R3E (r3e.h di Sector3, versione 3) |
| [Richard Burns Rally (dati in tempo reale)](game-richard-burns-rally.md) | telemetry | sì | telemetria UDP del plugin NGP, 127.0.0.1:6776 (RichardBurnsRally.ini [NGP] udpTelemetry=1) |
| [Rocket League (stato di gioco)](game-rocketleague-stats.md) | gsi | sì | Stats API: flusso TCP JSON da 127.0.0.1:49123 (porta in `<RL>\TAGame\Config\TAStatsAPI.ini` o DefaultStatsAPI.ini) |
| [Squad (replay)](game-squad-demos.md) | replay | sì | demo dei server che Squad registra con il comando admin AdminDemoRec: `<server>/SquadGame/Saved/Demos/*.replay`, letti dal lettore esterno `heat3d-squad-demo` (exporters/ext/squad-demo) |
| [Star Citizen (file di log)](game-starcitizen.md) | log | no | `<install>\StarCitizen\LIVE\Game.log` (la cartella di build dello StarCitizen.exe in esecuzione), solo il file di log che il gioco scrive - un gioco con Easy Anti-Cheat: il watcher non tocca il processo del gioco |
| [Statistiche Steam (piattaforma)](game-steam-stats.md) | platform | no | cache locale delle statistiche di Steam `%STEAM%\appcache\stats\UserGameStats_<account>_<appid>.bin` con `UserGameStatsSchema_<appid>.bin`; tempo di gioco da `%STEAM%\userdata\<account>\config\localconfig.vdf` (%STEAM% da `HKCU\Software\Valve\Steam` SteamPath) |
| [Steam Timeline (piattaforma)](game-steam-timeline.md) | platform | no | `%STEAM%\userdata\<account>\gamerecordings\timelines\timeline_<appid><date>_<time>.json` |
| [VALORANT (replay)](game-valorant-replays.md) | replay | no | replay salvati da VALORANT: `%LOCALAPPDATA%/VALORANT/Saved/Demos/*.vrf` (solo le parti che non sono offuscate) |
| [War Thunder (replay)](game-warthunder-replays.md) | replay | sì | replay salvati da War Thunder: `<War` `Thunder>/Replays/*.wrpl` (con il salvataggio dei replay attivo), convertiti dal convertitore esterno `heat3d-wt-replay` (exporters/ext/warthunder-replay) |
| [War Thunder (stato di gioco)](game-warthunder-webmap.md) | gsi | sì | la mappa web locale del gioco, <http://127.0.0.1:8111> (/map_info.json, /map_obj.json, /state, /indicators, /hudmsg, /gamechat, /mission.json, /map.img) |
| [World of Tanks (replay)](game-wot-replays.md) | replay | sì | replay salvati da World of Tanks: `<World` of `Tanks>/replays/*.wotreplay` (con la registrazione delle battaglie attiva), convertiti dal convertitore esterno `heat3d-wot-replay` (exporters/ext/wot-replay) |
| [World of Warships (replay)](game-wows-replays.md) | replay | sì | replay salvati da World of Warships: `<World` of `Warships>/replays/*.wowsreplay` (con i replay attivi), convertiti dal convertitore esterno `heat3d-wows-replay` (exporters/ext/wows-replay) |
| [X-Plane (dati in tempo reale)](game-xplane.md) | telemetry | sì | l'interfaccia UDP di X-Plane su 127.0.0.1:49000 (dataref RREF e posizione RPOS, risposte al watcher) |

Giochi che non vengono registrati, e perché: [Fonti e regole](sources-and-rules.md#what-is-declined-and-why). Tutto in un'unica tabella, come lo stampa `python -m heat3d_watch games --markdown`: [Tutti i giochi in una tabella](watcher.md).

<!-- Generato da tools/gen_game_pages.py; eseguilo di nuovo dopo aver cambiato un adattatore. -->
