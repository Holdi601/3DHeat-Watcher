---
title: Juegos
nav_order: 4
lang: "es"
source: games.md
source_hash: "dcee7fc45a5b"
nav_exclude: true
search_exclude: true
---
# Juegos {#games}

El watcher conoce 50 fuentes en 45 juegos y plataformas. Cada una tiene su propia página, generada a partir de su adaptador: qué graba, de dónde lo toma, cómo activarla, cómo funciona, sus ejes y lo que está verificado.

Tipos: `telemetry`, `gsi`, `log`, `replay` y `platform`; véase [Fuentes y reglas](sources-and-rules.md). Posiciones: *sí* cuando el adaptador escribe filas con un lugar, *prestada* cuando toma el lugar de otra grabación del mismo juego (véase [NVIDIA Highlights](nvidia-highlights.md)), *no* cuando la fuente no tiene ninguno. Los perfiles de memoria no se listan: ninguno se incluye, y cada jugador escribe el suyo (véase [Lectura de memoria](memory-reading.md)).

| Juego | Tipo | Posiciones | Fuente |
|---|---|---|---|
| [American Truck Simulator (datos en vivo)](game-ats.md) | telemetry | sí | memoria compartida `Local\SCSTelemetry` escrita por el plugin scs-sdk-plugin de RenCloud (revisión 12) en `<game>\bin\win_x64\plugins` |
| [Assetto Corsa (datos en vivo)](game-assetto-corsa.md) | telemetry | sí | memoria compartida `Local\acpmf_physics`, `Local\acpmf_graphics`, `Local\acpmf_static` |
| [Assetto Corsa Competizione (datos en vivo)](game-assetto-corsa-competizione.md) | telemetry | sí | memoria compartida `Local\acpmf_physics`, `Local\acpmf_graphics`, `Local\acpmf_static` |
| [Assetto Corsa EVO (datos en vivo)](game-assetto-corsa-evo.md) | telemetry | sí | memoria compartida `Local\acevo_pmf_physics`, `Local\acevo_pmf_static` |
| [Assetto Corsa Rally (datos en vivo)](game-assetto-corsa-rally.md) | telemetry | sí | memoria compartida `Local\acpmf_physics`, `Local\acpmf_static` (las mismas páginas que AC y ACC) |
| [Automobilista 2 (datos en vivo)](game-automobilista-2.md) | telemetry | sí | memoria compartida $pcars2$ (diseño SMS SharedMemory.h) |
| [BeamNG.drive (datos en vivo)](game-beamng.md) | telemetry | sí | UDP 127.0.0.1:4460 desde el mod de protocolo heat3d (mods/beamng/heat3d en este repositorio) |
| [Counter-Strike 2 (repeticiones)](game-cs2-demos.md) | replay | sí | demos que guarda CS2: `<CS2>/game/csgo/replays/*.dem` (descargadas del historial de partidas) y `<CS2>/game/csgo/*.dem` (grabadas) |
| [Counter-Strike 2 (estado de juego)](game-cs2-gsi.md) | gsi | sí | Game State Integration: envíos HTTP (POST) a 127.0.0.1:3311 configurados por `<CS2>\game\csgo\cfg\gamestate_integration_heat3d.cfg` |
| [DCS World (datos en vivo)](game-dcs.md) | telemetry | sí | el hook del watcher `%USERPROFILE%\Saved` `Games\DCS*\Scripts\Hooks\heat3d-watch.lua`, líneas UDP a 127.0.0.1:41993 |
| [DiRT Rally 2.0 (datos en vivo)](game-dirt-rally-2.md) | telemetry | sí | UDP 127.0.0.1:20777, extradata=3 `(Documents\My` `Games\DiRT` Rally `2.0\hardwaresettings\hardware_settings_config.xml`); mientras otra aplicación tenga el 20777, el watcher deja el puerto a esa aplicación |
| [Dota 2 (repeticiones)](game-dota-replays.md) | replay | sí | repeticiones que guarda Dota 2: `<Dota>/game/dota/replays/<match` id>.dem (descargadas en el cliente, o con `dota-replay <id de partida>`) |
| [Dota 2 (estado de juego)](game-dota2-gsi.md) | gsi | sí | Game State Integration: envíos HTTP (POST) a 127.0.0.1:3312 configurados por `<Dota>\game\dota\cfg\gamestate_integration\gamestate_integration_heat3d.cfg` |
| [EA SPORTS F1 23 (datos en vivo)](game-f1-23.md) | telemetry | sí | telemetría UDP 127.0.0.1:20777 `(Documents\My` `Games\F1` `23\hardwaresettings\hardware_settings_config.xml`) |
| [EA SPORTS F1 24 (datos en vivo)](game-f1-24.md) | telemetry | sí | telemetría UDP 127.0.0.1:20777 `(Documents\My` `Games\F1` `24\hardwaresettings\hardware_settings_config.xml`) |
| [EA SPORTS F1 25 (datos en vivo)](game-f1-25.md) | telemetry | sí | telemetría UDP 127.0.0.1:20777 `(Documents\My` `Games\F1` `25\hardwaresettings\hardware_settings_config.xml`) |
| [EA SPORTS WRC (datos en vivo)](game-ea-wrc.md) | telemetry | sí | UDP 127.0.0.1:20777, el paquete session_update de la estructura `wrc` por defecto `(Documents\My` `Games\WRC\telemetry\config.json`); mientras otra aplicación tenga el 20777, el watcher deja el puerto a esa aplicación |
| [Elite Dangerous (archivos de registro)](game-elite.md) | log | sí | Diario del jugador `%USERPROFILE%\Saved` `Games\Frontier` `Developments\Elite` `Dangerous\Journal.*.log` (el archivo más nuevo, seguido mientras se escribe), Status.json y los demás archivos `*.json` del compañero (Market, Outfitting, Shipyard, NavRoute, Cargo, ModulesInfo, ShipLocker, Backpack, FCMaterials) en la misma carpeta |
| [Euro Truck Simulator 2 (datos en vivo)](game-ets2.md) | telemetry | sí | memoria compartida `Local\SCSTelemetry` escrita por el plugin scs-sdk-plugin de RenCloud (revisión 12) en `<game>\bin\win_x64\plugins` |
| [EVE Online (archivos de registro)](game-eve.md) | log | no | `%USERPROFILE%\Documents\EVE\logs\Gamelogs\*.txt` y los `Chatlogs\*.txt` junto a ellos (cada archivo escrito desde que se abrió el cliente) |
| [Forza Horizon 4 (datos en vivo)](game-forza-horizon-4.md) | telemetry | sí | Forza Data Out, UDP 127.0.0.1:5300 (formato Dash); cada paquete se reenvía sin cambios a 127.0.0.1:5301 |
| [Forza Horizon 5 (datos en vivo)](game-forza-horizon-5.md) | telemetry | sí | Forza Data Out, UDP 127.0.0.1:5300 (formato Dash); cada paquete se reenvía sin cambios a 127.0.0.1:5301 |
| [Forza Horizon 6 (datos en vivo)](game-forza-horizon-6.md) | telemetry | sí | Forza Data Out, UDP 127.0.0.1:5300 (formato Dash); cada paquete se reenvía sin cambios a 127.0.0.1:5301 |
| [Forza Motorsport (datos en vivo)](game-forza-motorsport.md) | telemetry | sí | Forza Data Out, UDP 127.0.0.1:5300 (formato Dash); cada paquete se reenvía sin cambios a 127.0.0.1:5301 |
| [Hearthstone (archivos de registro)](game-hearthstone.md) | log | no | `<install>\Logs\Power.log` (o `Logs\Hearthstone_*\Power.log`), escrito una vez que `%LOCALAPPDATA%\Blizzard\Hearthstone\log.config` tiene una sección [Power], y cualquier otro `*.log` que el juego escriba allí |
| [IL-2 Sturmovik: Great Battles (datos en vivo)](game-il2.md) | telemetry | no | la salida UDP de telemetría del juego a 127.0.0.1:41995 (`KEY = telemetrydevice` en `<game>\data\startup.cfg`) |
| [IL-2 Sturmovik: Great Battles (repeticiones)](game-il2-tacview.md) | replay | sí | las grabaciones Tacview propias del juego `<game>\data\Tracks\*.acmi` (ACMI 2.x en texto, plano o comprimido) |
| [iRacing (datos en vivo)](game-iracing.md) | telemetry | no | memoria compartida `Local\IRSDKMemMapFileName` (el SDK de iRacing); archivos .ibt en `%USERPROFILE%\Documents\iRacing\telemetry` |
| [League of Legends (estado de juego)](game-lol-live.md) | gsi | no | API Live Client Data del cliente del juego, <https://127.0.0.1:2999/liveclientdata/> (allgamedata, eventdata), durante una partida |
| [League of Legends (repeticiones)](game-lol-replays.md) | replay | sí | repeticiones que guarda el cliente de League: %USERPROFILE%/Documents/League of `Legends/Replays/*.rofl` (solo los metadatos sencillos del final de partida); con tu propia clave de la API de Riot, la línea de tiempo oficial de la partida desde la API Match-V5 de Riot |
| [Microsoft Flight Simulator 2020 (datos en vivo)](game-msfs2020.md) | telemetry | sí | SimConnect a través de la SimConnect.dll propia del jugador (la carpeta del simulador, o `%MSFS_SDK%\SimConnect` `SDK\lib`) |
| [Microsoft Flight Simulator 2024 (datos en vivo)](game-msfs2024.md) | telemetry | sí | SimConnect a través de la SimConnect.dll propia del jugador (la carpeta del simulador, o `%MSFS2024_SDK%\SimConnect` `SDK\lib`) |
| [Minecraft (archivos de registro)](game-minecraft.md) | log | sí | `%APPDATA%\.minecraft\logs\latest.log` (seguido), `saves\<world>\stats\<uuid>.json` y `saves\<world>\playerdata\<uuid>.dat` / level.dat (NBT comprimido con gzip), leídos cuando el juego los guarda |
| [NVIDIA highlights (plataforma)](game-nvidia-highlights.md) | platform | prestada | `%LOCALAPPDATA%\NVIDIA` `Corporation\NVIDIA` `Overlay\UGCTracker.json`, GallerySettings.json, `Highlights\<game>\config.json`; clips en la carpeta de captura `(%USERPROFILE%\Videos\NVIDIA\<Game>\*.mp4`) y `<temp>\Highlights\<game>`; `%LOCALAPPDATA%\NVIDIA` `Corporation\GfeSDK\<exe>_<pid>.log` |
| [osu! (repeticiones)](game-osu-replays.md) | replay | sí | repeticiones que guarda osu! (estable): `%LOCALAPPDATA%/osu!/Data/r/*.osr` (cada partida) y `osu!/Replays/*.osr` (exportadas) |
| [Path of Exile (archivos de registro)](game-poe.md) | log | no | `<install>\logs\Client.txt` de Path of Exile o Path of Exile 2 (seguido; la carpeta de instalación es la del ejecutable en marcha) |
| [Project CARS 2 (datos en vivo)](game-project-cars-2.md) | telemetry | sí | memoria compartida $pcars2$ (SMS SharedMemory.h) |
| [RaceRoom Racing Experience (datos en vivo)](game-raceroom.md) | telemetry | sí | memoria compartida $R3E (r3e.h de Sector3, versión 3) |
| [Richard Burns Rally (datos en vivo)](game-richard-burns-rally.md) | telemetry | sí | telemetría UDP del plugin NGP, 127.0.0.1:6776 (RichardBurnsRally.ini [NGP] udpTelemetry=1) |
| [Rocket League (estado de juego)](game-rocketleague-stats.md) | gsi | sí | API de estadísticas: flujo JSON TCP desde 127.0.0.1:49123 (puerto en `<RL>\TAGame\Config\TAStatsAPI.ini` o DefaultStatsAPI.ini) |
| [Squad (repeticiones)](game-squad-demos.md) | replay | sí | demos de servidor que Squad graba con el comando de administrador AdminDemoRec: `<server>/SquadGame/Saved/Demos/*.replay`, leídas por el lector externo `heat3d-squad-demo` (exporters/ext/squad-demo) |
| [Star Citizen (archivos de registro)](game-starcitizen.md) | log | no | `<install>\StarCitizen\LIVE\Game.log` (la carpeta de compilación del StarCitizen.exe en marcha), solo el archivo de registro que escribe el juego - un juego con Easy Anti-Cheat: nada toca su proceso |
| [Estadísticas de Steam (plataforma)](game-steam-stats.md) | platform | no | la caché local de estadísticas de Steam `%STEAM%\appcache\stats\UserGameStats_<account>_<appid>.bin` con `UserGameStatsSchema_<appid>.bin`; tiempo de juego desde `%STEAM%\userdata\<account>\config\localconfig.vdf` (%STEAM% desde `HKCU\Software\Valve\Steam` SteamPath) |
| [Steam Timeline (plataforma)](game-steam-timeline.md) | platform | no | `%STEAM%\userdata\<account>\gamerecordings\timelines\timeline_<appid><date>_<time>.json` |
| [VALORANT (repeticiones)](game-valorant-replays.md) | replay | no | repeticiones que guarda VALORANT: `%LOCALAPPDATA%/VALORANT/Saved/Demos/*.vrf` (solo las partes que no están ofuscadas) |
| [War Thunder (repeticiones)](game-warthunder-replays.md) | replay | sí | repeticiones que guarda War Thunder: `<War` `Thunder>/Replays/*.wrpl` (con el guardado de repeticiones activado), convertidas por el conversor externo `heat3d-wt-replay` (exporters/ext/warthunder-replay) |
| [War Thunder (estado de juego)](game-warthunder-webmap.md) | gsi | sí | el mapa web local del juego, <http://127.0.0.1:8111> (/map_info.json, /map_obj.json, /state, /indicators, /hudmsg, /gamechat, /mission.json, /map.img) |
| [World of Tanks (repeticiones)](game-wot-replays.md) | replay | sí | repeticiones que guarda World of Tanks: `<World` of `Tanks>/replays/*.wotreplay` (con la grabación de batallas activada), convertidas por el conversor externo `heat3d-wot-replay` (exporters/ext/wot-replay) |
| [World of Warships (repeticiones)](game-wows-replays.md) | replay | sí | repeticiones que guarda World of Warships: `<World` of `Warships>/replays/*.wowsreplay` (con las repeticiones activadas), convertidas por el conversor externo `heat3d-wows-replay` (exporters/ext/wows-replay) |
| [X-Plane (datos en vivo)](game-xplane.md) | telemetry | sí | la interfaz UDP de X-Plane en 127.0.0.1:49000 (datarefs RREF y RPOS, respondidos al watcher) |

Juegos que no se graban, y por qué: [Fuentes y reglas](sources-and-rules.md#what-is-declined-and-why). Todo en una sola tabla, tal como lo muestra `python -m heat3d_watch games --markdown`: [Todos los juegos en una tabla](watcher.md).

<!-- Generado por tools/gen_game_pages.py; vuelve a ejecutarlo después de cambiar un adaptador. -->
