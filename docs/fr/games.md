---
title: "Jeux"
nav_order: 4
lang: "fr"
source: games.md
source_hash: "c601550fbb4e"
nav_exclude: true
search_exclude: true
---
# Jeux {#games}

Le watcher connaît 49 sources dans 44 jeux et plateformes. Chacune a sa propre page, générée à partir de son adaptateur : ce qu'elle enregistre, d'où, comment l'activer, comment elle fonctionne, ses axes, ce qui a été vérifié.

Types : `telemetry`, `gsi`, `log`, `replay` et `platform` - voir [Sources et règles](sources-and-rules.md). Positions : *oui* quand l'adaptateur écrit des lignes avec un lieu, *emprunté* quand il prend le lieu d'un autre enregistrement du même jeu (voir [NVIDIA Highlights](nvidia-highlights.md)), *non* quand la source n'en a pas. Les profils de mémoire ne sont pas listés : aucun n'est livré, et chaque joueur écrit le sien (voir [Lecture de la mémoire](memory-reading.md)).

| Jeu | Type | Positions | Source |
|---|---|---|---|
| [American Truck Simulator (données en direct)](game-ats.md) | telemetry | oui | mémoire partagée `Local\SCSTelemetry` écrite par le plugin scs-sdk-plugin de RenCloud (révision 12) dans `<game>\bin\win_x64\plugins` |
| [Assetto Corsa (données en direct)](game-assetto-corsa.md) | telemetry | oui | mémoire partagée `Local\acpmf_physics`, `Local\acpmf_graphics`, `Local\acpmf_static` |
| [Assetto Corsa Competizione (données en direct)](game-assetto-corsa-competizione.md) | telemetry | oui | mémoire partagée `Local\acpmf_physics`, `Local\acpmf_graphics`, `Local\acpmf_static` |
| [Assetto Corsa EVO (données en direct)](game-assetto-corsa-evo.md) | telemetry | oui | mémoire partagée `Local\acevo_pmf_physics`, `Local\acevo_pmf_static` |
| [Assetto Corsa Rally (données en direct)](game-assetto-corsa-rally.md) | telemetry | oui | mémoire partagée `Local\acpmf_physics`, `Local\acpmf_static` (les mêmes pages que AC et ACC) |
| [Automobilista 2 (données en direct)](game-automobilista-2.md) | telemetry | oui | mémoire partagée $pcars2$ (disposition SMS SharedMemory.h) |
| [BeamNG.drive (données en direct)](game-beamng.md) | telemetry | oui | UDP 127.0.0.1:4460 depuis le mod de protocole heat3d de BeamNG (mods/beamng/heat3d dans ce dépôt) |
| [Counter-Strike 2 (replays)](game-cs2-demos.md) | replay | oui | démos que CS2 sauvegarde : `<CS2>/game/csgo/replays/*.dem` (téléchargées depuis l'historique des matchs) et `<CS2>/game/csgo/*.dem` (enregistrées) |
| [Counter-Strike 2 (état du jeu)](game-cs2-gsi.md) | gsi | oui | intégration d'état de jeu : requêtes HTTP POST vers 127.0.0.1:3311, configurées par `<CS2>\game\csgo\cfg\gamestate_integration_heat3d.cfg` |
| [DCS World (données en direct)](game-dcs.md) | telemetry | oui | le hook du watcher `%USERPROFILE%\Saved` `Games\DCS*\Scripts\Hooks\heat3d-watch.lua`, lignes UDP vers 127.0.0.1:41993 |
| [DiRT Rally 2.0 (données en direct)](game-dirt-rally-2.md) | telemetry | oui | UDP 127.0.0.1:20777, extradata=3 `(Documents\My` `Games\DiRT` Rally `2.0\hardwaresettings\hardware_settings_config.xml`) ; tant qu'une autre application tient le port 20777, le watcher le lui laisse |
| [Dota 2 (replays)](game-dota-replays.md) | replay | oui | replays que Dota 2 sauvegarde : `<Dota>/game/dota/replays/<match id>.dem` (téléchargés dans le client, ou avec `dota-replay <match id>`) |
| [Dota 2 (état du jeu)](game-dota2-gsi.md) | gsi | oui | intégration d'état de jeu : requêtes HTTP POST vers 127.0.0.1:3312, configurées par `<Dota>\game\dota\cfg\gamestate_integration\gamestate_integration_heat3d.cfg` |
| [EA SPORTS F1 23 (données en direct)](game-f1-23.md) | telemetry | oui | télémétrie UDP 127.0.0.1:20777 `(Documents\My` `Games\F1` `23\hardwaresettings\hardware_settings_config.xml`) |
| [EA SPORTS F1 24 (données en direct)](game-f1-24.md) | telemetry | oui | télémétrie UDP 127.0.0.1:20777 `(Documents\My` `Games\F1` `24\hardwaresettings\hardware_settings_config.xml`) |
| [EA SPORTS F1 25 (données en direct)](game-f1-25.md) | telemetry | oui | télémétrie UDP 127.0.0.1:20777 `(Documents\My` `Games\F1` `25\hardwaresettings\hardware_settings_config.xml`) |
| [EA SPORTS WRC (données en direct)](game-ea-wrc.md) | telemetry | oui | UDP 127.0.0.1:20777, le paquet session_update de la structure `wrc` par défaut `(Documents\My` `Games\WRC\telemetry\config.json`) ; tant qu'une autre application tient le port 20777, le watcher le lui laisse |
| [Elite Dangerous (fichiers journaux)](game-elite.md) | log | oui | journal du joueur `%USERPROFILE%\Saved` `Games\Frontier` `Developments\Elite` `Dangerous\Journal.*.log` (le fichier le plus récent, suivi pendant qu'il s'écrit), Status.json et les autres annexes `*.json` (Market, Outfitting, Shipyard, NavRoute, Cargo, ModulesInfo, ShipLocker, Backpack, FCMaterials) dans le même dossier |
| [Euro Truck Simulator 2 (données en direct)](game-ets2.md) | telemetry | oui | mémoire partagée `Local\SCSTelemetry` écrite par le plugin scs-sdk-plugin de RenCloud (révision 12) dans `<game>\bin\win_x64\plugins` |
| [EVE Online (fichiers journaux)](game-eve.md) | log | non | `%USERPROFILE%\Documents\EVE\logs\Gamelogs\*.txt` et les `Chatlogs\*.txt` à côté (chaque fichier écrit depuis le lancement du client) |
| [Forza Horizon 4 (données en direct)](game-forza-horizon-4.md) | telemetry | oui | Forza Data Out, UDP 127.0.0.1:5300 (format Dash) ; chaque paquet relayé sans modification vers 127.0.0.1:5301 |
| [Forza Horizon 5 (données en direct)](game-forza-horizon-5.md) | telemetry | oui | Forza Data Out, UDP 127.0.0.1:5300 (format Dash) ; chaque paquet relayé sans modification vers 127.0.0.1:5301 |
| [Forza Horizon 6 (données en direct)](game-forza-horizon-6.md) | telemetry | oui | Forza Data Out, UDP 127.0.0.1:5300 (format Dash) ; chaque paquet relayé sans modification vers 127.0.0.1:5301 |
| [Forza Motorsport (données en direct)](game-forza-motorsport.md) | telemetry | oui | Forza Data Out, UDP 127.0.0.1:5300 (format Dash) ; chaque paquet relayé sans modification vers 127.0.0.1:5301 |
| [Hearthstone (fichiers journaux)](game-hearthstone.md) | log | non | `<install>\Logs\Power.log` (ou `Logs\Hearthstone_*\Power.log`), écrit une fois que `%LOCALAPPDATA%\Blizzard\Hearthstone\log.config` a une section [Power], et tout autre `*.log` que le jeu écrit là |
| [IL-2 Sturmovik: Great Battles (données en direct)](game-il2.md) | telemetry | non | la sortie de télémétrie UDP du jeu vers 127.0.0.1:41995 (`[KEY = telemetrydevice]` dans `<game>\data\startup.cfg`) |
| [IL-2 Sturmovik: Great Battles (replays)](game-il2-tacview.md) | replay | oui | les enregistrements Tacview du jeu `<game>\data\Tracks\*.acmi` (ACMI 2.x en texte, brut ou zippé) |
| [iRacing (données en direct)](game-iracing.md) | telemetry | non | mémoire partagée `Local\IRSDKMemMapFileName` (le SDK iRacing) ; fichiers .ibt dans `%USERPROFILE%\Documents\iRacing\telemetry` |
| [League of Legends (état du jeu)](game-lol-live.md) | gsi | non | API Live Client Data du client du jeu, <https://127.0.0.1:2999/liveclientdata/> (allgamedata, eventdata), pendant une partie |
| [League of Legends (replays)](game-lol-replays.md) | replay | oui | replays que le client League sauvegarde : %USERPROFILE%/Documents/League of `Legends/Replays/*.rofl` (seulement les métadonnées simples de fin de partie) ; avec votre propre clé d'API Riot, la chronologie officielle du match, depuis l'API Match-V5 de Riot |
| [Microsoft Flight Simulator 2020 (données en direct)](game-msfs2020.md) | telemetry | oui | SimConnect par le SimConnect.dll propre au joueur (le dossier du simulateur, ou `%MSFS_SDK%\SimConnect` `SDK\lib`) |
| [Microsoft Flight Simulator 2024 (données en direct)](game-msfs2024.md) | telemetry | oui | SimConnect par le SimConnect.dll propre au joueur (le dossier du simulateur, ou `%MSFS2024_SDK%\SimConnect` `SDK\lib`) |
| [Minecraft (fichiers journaux)](game-minecraft.md) | log | oui | `%APPDATA%\.minecraft\logs\latest.log` (suivi), `saves\<world>\stats\<uuid>.json` et `saves\<world>\playerdata\<uuid>.dat` / level.dat (NBT gzip), lus quand le jeu les sauvegarde |
| [NVIDIA highlights (plateforme)](game-nvidia-highlights.md) | platform | emprunté | `%LOCALAPPDATA%\NVIDIA` `Corporation\NVIDIA` `Overlay\UGCTracker.json`, GallerySettings.json, `Highlights\<game>\config.json` ; clips dans le dossier de capture `(%USERPROFILE%\Videos\NVIDIA\<Game>\*.mp4`) et `<temp>\Highlights\<game>` ; `%LOCALAPPDATA%\NVIDIA` `Corporation\GfeSDK\<exe>_<pid>.log` |
| [Path of Exile (fichiers journaux)](game-poe.md) | log | non | `<install>\logs\Client.txt` de Path of Exile ou Path of Exile 2 (suivi ; le dossier d'installation est celui de l'exécutable en cours) |
| [Project CARS 2 (données en direct)](game-project-cars-2.md) | telemetry | oui | mémoire partagée $pcars2$ (SMS SharedMemory.h) |
| [RaceRoom Racing Experience (données en direct)](game-raceroom.md) | telemetry | oui | mémoire partagée $R3E (r3e.h de Sector3, version 3) |
| [Richard Burns Rally (données en direct)](game-richard-burns-rally.md) | telemetry | oui | télémétrie UDP du plugin NGP, 127.0.0.1:6776 (RichardBurnsRally.ini [NGP] udpTelemetry=1) |
| [Rocket League (état du jeu)](game-rocketleague-stats.md) | gsi | oui | API de statistiques : flux TCP JSON depuis 127.0.0.1:49123 (port dans `<RL>\TAGame\Config\TAStatsAPI.ini` ou DefaultStatsAPI.ini) |
| [Squad (replays)](game-squad-demos.md) | replay | oui | démos de serveur que Squad enregistre avec la commande d'admin AdminDemoRec : `<server>/SquadGame/Saved/Demos/*.replay`, lues par le lecteur externe `heat3d-squad-demo` (exporters/ext/squad-demo) |
| [Star Citizen (fichiers journaux)](game-starcitizen.md) | log | non | `<install>\StarCitizen\LIVE\Game.log` (le dossier de build de StarCitizen.exe en cours), seulement le fichier journal écrit par le jeu - un jeu protégé par Easy Anti-Cheat : rien ne touche à son processus |
| [Steam statistics (plateforme)](game-steam-stats.md) | platform | non | cache de statistiques local de Steam `%STEAM%\appcache\stats\UserGameStats_<account>_<appid>.bin` avec `UserGameStatsSchema_<appid>.bin` ; temps de jeu depuis `%STEAM%\userdata\<account>\config\localconfig.vdf` (%STEAM% depuis `HKCU\Software\Valve\Steam` SteamPath) |
| [Steam Timeline (plateforme)](game-steam-timeline.md) | platform | non | `%STEAM%\userdata\<account>\gamerecordings\timelines\timeline_<appid><date>_<time>.json` |
| [VALORANT (replays)](game-valorant-replays.md) | replay | non | replays de VALORANT : `%LOCALAPPDATA%/VALORANT/Saved/Demos/*.vrf` (seulement les parties non brouillées) |
| [War Thunder (replays)](game-warthunder-replays.md) | replay | oui | replays que War Thunder sauvegarde : `<War Thunder>/Replays/*.wrpl` (avec la sauvegarde des replays activée), convertis par le convertisseur externe `heat3d-wt-replay` (exporters/ext/warthunder-replay) |
| [War Thunder (état du jeu)](game-warthunder-webmap.md) | gsi | oui | la carte web locale du jeu, <http://127.0.0.1:8111> (/map_info.json, /map_obj.json, /state, /indicators, /hudmsg, /gamechat, /mission.json, /map.img) |
| [World of Tanks (replays)](game-wot-replays.md) | replay | oui | replays que World of Tanks sauvegarde : `<World of Tanks>/replays/*.wotreplay` (avec l'enregistrement des batailles activé), convertis par le convertisseur externe `heat3d-wot-replay` (exporters/ext/wot-replay) |
| [World of Warships (replays)](game-wows-replays.md) | replay | oui | replays que World of Warships sauvegarde : `<World of Warships>/replays/*.wowsreplay` (avec les replays activés), convertis par le convertisseur externe `heat3d-wows-replay` (exporters/ext/wows-replay) |
| [X-Plane (données en direct)](game-xplane.md) | telemetry | oui | l'interface UDP de X-Plane sur 127.0.0.1:49000 (datarefs RREF et position RPOS, répondus au watcher) |

Jeux non enregistrés, et pourquoi : [Sources et règles](sources-and-rules.md#what-is-declined-and-why). Tout dans un seul tableau, tel que `python -m heat3d_watch games --markdown` l'affiche : [Tous les jeux dans un tableau](watcher.md).

<!-- Generated by tools/gen_game_pages.py; run it again after changing an adapter. -->
