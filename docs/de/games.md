---
title: Spiele
nav_order: 4
lang: "de"
source: games.md
source_hash: "c601550fbb4e"
nav_exclude: true
search_exclude: true
---
# Spiele {#games}

Der Watcher kennt 49 Quellen in 44 Spielen und Plattformen. Jede hat eine eigene Seite, aus ihrem Adapter erzeugt: was sie aufzeichnet, woher, wie man sie einschaltet, wie sie funktioniert, ihre Achsen und was geprüft wurde.

Arten: `telemetry`, `gsi`, `log`, `replay` und `platform` - siehe [Quellen und Regeln](sources-and-rules.md). Positionen: *ja*, wenn der Adapter Zeilen mit einem Ort schreibt; *geliehen*, wenn er den Ort aus einer anderen Aufzeichnung desselben Spiels nimmt (siehe [NVIDIA Highlights](nvidia-highlights.md)); *nein*, wenn die Quelle keinen hat. Speicherprofile sind nicht aufgeführt: keines wird mitgeliefert, und jeder Spieler schreibt sein eigenes (siehe [Speicher lesen](memory-reading.md)).

| Spiel | Art | Positionen | Quelle |
|---|---|---|---|
| [American Truck Simulator (Live-Daten)](game-ats.md) | telemetry | ja | Shared Memory `Local\SCSTelemetry`, geschrieben vom RenCloud scs-sdk-plugin (Revision 12) in `<game>\bin\win_x64\plugins` |
| [Assetto Corsa (Live-Daten)](game-assetto-corsa.md) | telemetry | ja | Shared Memory `Local\acpmf_physics`, `Local\acpmf_graphics`, `Local\acpmf_static` |
| [Assetto Corsa Competizione (Live-Daten)](game-assetto-corsa-competizione.md) | telemetry | ja | Shared Memory `Local\acpmf_physics`, `Local\acpmf_graphics`, `Local\acpmf_static` |
| [Assetto Corsa EVO (Live-Daten)](game-assetto-corsa-evo.md) | telemetry | ja | Shared Memory `Local\acevo_pmf_physics`, `Local\acevo_pmf_static` |
| [Assetto Corsa Rally (Live-Daten)](game-assetto-corsa-rally.md) | telemetry | ja | Shared Memory `Local\acpmf_physics`, `Local\acpmf_static` (dieselben Seiten wie AC und ACC) |
| [Automobilista 2 (Live-Daten)](game-automobilista-2.md) | telemetry | ja | Shared Memory $pcars2$ (SMS-SharedMemory.h-Layout) |
| [BeamNG.drive (Live-Daten)](game-beamng.md) | telemetry | ja | UDP 127.0.0.1:4460 aus dem heat3d-Protokoll-Mod (mods/beamng/heat3d in diesem Repository) |
| [Counter-Strike 2 (Replays)](game-cs2-demos.md) | replay | ja | Demos, die CS2 speichert: `<CS2>/game/csgo/replays/*.dem` (aus der Matchhistorie geladen) und `<CS2>/game/csgo/*.dem` (aufgenommen) |
| [Counter-Strike 2 (Spielstand)](game-cs2-gsi.md) | gsi | ja | Game State Integration: HTTP-POSTs an 127.0.0.1:3311, eingestellt in `<CS2>\game\csgo\cfg\gamestate_integration_heat3d.cfg` |
| [DCS World (Live-Daten)](game-dcs.md) | telemetry | ja | der Hook des Watchers `%USERPROFILE%\Saved` `Games\DCS*\Scripts\Hooks\heat3d-watch.lua`, UDP-Zeilen an 127.0.0.1:41993 |
| [DiRT Rally 2.0 (Live-Daten)](game-dirt-rally-2.md) | telemetry | ja | UDP 127.0.0.1:20777, extradata=3 `(Documents\My` `Games\DiRT` Rally `2.0\hardwaresettings\hardware_settings_config.xml`); solange ein anderes Programm 20777 belegt, lässt der Watcher ihm den Port |
| [Dota 2 (Replays)](game-dota-replays.md) | replay | ja | Replays, die Dota 2 speichert: `<Dota>/game/dota/replays/<match id>.dem` (im Client geladen oder mit `dota-replay <match id>`) |
| [Dota 2 (Spielstand)](game-dota2-gsi.md) | gsi | ja | Game State Integration: HTTP-POSTs an 127.0.0.1:3312, eingestellt in `<Dota>\game\dota\cfg\gamestate_integration\gamestate_integration_heat3d.cfg` |
| [EA SPORTS F1 23 (Live-Daten)](game-f1-23.md) | telemetry | ja | UDP-Telemetrie 127.0.0.1:20777 `(Documents\My` `Games\F1` `23\hardwaresettings\hardware_settings_config.xml`) |
| [EA SPORTS F1 24 (Live-Daten)](game-f1-24.md) | telemetry | ja | UDP-Telemetrie 127.0.0.1:20777 `(Documents\My` `Games\F1` `24\hardwaresettings\hardware_settings_config.xml`) |
| [EA SPORTS F1 25 (Live-Daten)](game-f1-25.md) | telemetry | ja | UDP-Telemetrie 127.0.0.1:20777 `(Documents\My` `Games\F1` `25\hardwaresettings\hardware_settings_config.xml`) |
| [EA SPORTS WRC (Live-Daten)](game-ea-wrc.md) | telemetry | ja | UDP 127.0.0.1:20777, das Paket session_update der Standardstruktur `wrc` `(Documents\My` `Games\WRC\telemetry\config.json`); solange ein anderes Programm 20777 belegt, lässt der Watcher ihm den Port |
| [Elite Dangerous (Logdateien)](game-elite.md) | log | ja | Spieler-Journal `%USERPROFILE%\Saved` `Games\Frontier` `Developments\Elite` `Dangerous\Journal.*.log` (neueste Datei, mitgelesen, während sie geschrieben wird), Status.json und die anderen Begleit-`*.json`-Dateien (Market, Outfitting, Shipyard, NavRoute, Cargo, ModulesInfo, ShipLocker, Backpack, FCMaterials) im selben Ordner |
| [Euro Truck Simulator 2 (Live-Daten)](game-ets2.md) | telemetry | ja | Shared Memory `Local\SCSTelemetry`, geschrieben vom RenCloud scs-sdk-plugin (Revision 12) in `<game>\bin\win_x64\plugins` |
| [EVE Online (Logdateien)](game-eve.md) | log | nein | `%USERPROFILE%\Documents\EVE\logs\Gamelogs\*.txt` und die `Chatlogs\*.txt` daneben (jede Datei, seit der Client gestartet wurde) |
| [Forza Horizon 4 (Live-Daten)](game-forza-horizon-4.md) | telemetry | ja | Forza Data Out, UDP 127.0.0.1:5300 (Dash-Format); jedes Paket unverändert an 127.0.0.1:5301 weitergeleitet |
| [Forza Horizon 5 (Live-Daten)](game-forza-horizon-5.md) | telemetry | ja | Forza Data Out, UDP 127.0.0.1:5300 (Dash-Format); jedes Paket unverändert an 127.0.0.1:5301 weitergeleitet |
| [Forza Horizon 6 (Live-Daten)](game-forza-horizon-6.md) | telemetry | ja | Forza Data Out, UDP 127.0.0.1:5300 (Dash-Format); jedes Paket unverändert an 127.0.0.1:5301 weitergeleitet |
| [Forza Motorsport (Live-Daten)](game-forza-motorsport.md) | telemetry | ja | Forza Data Out, UDP 127.0.0.1:5300 (Dash-Format); jedes Paket unverändert an 127.0.0.1:5301 weitergeleitet |
| [Hearthstone (Logdateien)](game-hearthstone.md) | log | nein | `<install>\Logs\Power.log` (oder `Logs\Hearthstone_*\Power.log`), geschrieben, sobald `%LOCALAPPDATA%\Blizzard\Hearthstone\log.config` einen Abschnitt [Power] hat, und jede andere `*.log`, die das Spiel dort schreibt |
| [IL-2 Sturmovik: Great Battles (Live-Daten)](game-il2.md) | telemetry | nein | die UDP-Telemetrieausgabe des Spiels an 127.0.0.1:41995 ([KEY = telemetrydevice] in `<game>\data\startup.cfg`) |
| [IL-2 Sturmovik: Great Battles (Replays)](game-il2-tacview.md) | replay | ja | die eigenen Tacview-Aufnahmen des Spiels `<game>\data\Tracks\*.acmi` (ACMI 2.x als Text, unverpackt oder gezippt) |
| [iRacing (Live-Daten)](game-iracing.md) | telemetry | nein | Shared Memory `Local\IRSDKMemMapFileName` (das iRacing SDK); .ibt-Dateien in `%USERPROFILE%\Documents\iRacing\telemetry` |
| [League of Legends (Spielstand)](game-lol-live.md) | gsi | nein | Live Client Data API des Spiel-Clients, <https://127.0.0.1:2999/liveclientdata/> (allgamedata, eventdata), während eines Matches |
| [League of Legends (Replays)](game-lol-replays.md) | replay | ja | Replays, die der League-Client speichert: %USERPROFILE%/Documents/League of `Legends/Replays/*.rofl` (nur die einfachen Metadaten am Matchende); mit deinem eigenen Riot-API-Schlüssel die offizielle Zeitleiste des Matches aus Riots Match-V5-API |
| [Microsoft Flight Simulator 2020 (Live-Daten)](game-msfs2020.md) | telemetry | ja | SimConnect über die eigene SimConnect.dll des Spielers (der Simulator-Ordner oder `%MSFS_SDK%\SimConnect` `SDK\lib`) |
| [Microsoft Flight Simulator 2024 (Live-Daten)](game-msfs2024.md) | telemetry | ja | SimConnect über die eigene SimConnect.dll des Spielers (der Simulator-Ordner oder `%MSFS2024_SDK%\SimConnect` `SDK\lib`) |
| [Minecraft (Logdateien)](game-minecraft.md) | log | ja | `%APPDATA%\.minecraft\logs\latest.log` (mitgelesen), `saves\<world>\stats\<uuid>.json` und `saves\<world>\playerdata\<uuid>.dat` / level.dat (gzip-NBT), gelesen, wenn das Spiel sie speichert |
| [NVIDIA-Highlights (Plattform)](game-nvidia-highlights.md) | platform | geliehen | `%LOCALAPPDATA%\NVIDIA` `Corporation\NVIDIA` `Overlay\UGCTracker.json`, GallerySettings.json, `Highlights\<game>\config.json`; Clips im Aufnahmeordner `(%USERPROFILE%\Videos\NVIDIA\<Game>\*.mp4`) und `<temp>\Highlights\<game>`; `%LOCALAPPDATA%\NVIDIA` `Corporation\GfeSDK\<exe>_<pid>.log` |
| [Path of Exile (Logdateien)](game-poe.md) | log | nein | `<install>\logs\Client.txt` von Path of Exile oder Path of Exile 2 (mitgelesen; der Installationsordner ist der des laufenden Programms) |
| [Project CARS 2 (Live-Daten)](game-project-cars-2.md) | telemetry | ja | Shared Memory $pcars2$ (SMS SharedMemory.h) |
| [RaceRoom Racing Experience (Live-Daten)](game-raceroom.md) | telemetry | ja | Shared Memory $R3E (Sector3's r3e.h, Version 3) |
| [Richard Burns Rally (Live-Daten)](game-richard-burns-rally.md) | telemetry | ja | NGP-Plugin-UDP-Telemetrie, 127.0.0.1:6776 (RichardBurnsRally.ini [NGP] udpTelemetry=1) |
| [Rocket League (Spielstand)](game-rocketleague-stats.md) | gsi | ja | Stats API: TCP-JSON-Strom von 127.0.0.1:49123 (Port in `<RL>\TAGame\Config\TAStatsAPI.ini` oder DefaultStatsAPI.ini) |
| [Squad (Replays)](game-squad-demos.md) | replay | ja | Serverdemos, die Squad mit dem Admin-Befehl AdminDemoRec aufnimmt: `<server>/SquadGame/Saved/Demos/*.replay`, gelesen vom externen Leser `heat3d-squad-demo` (exporters/ext/squad-demo) |
| [Star Citizen (Logdateien)](game-starcitizen.md) | log | nein | `<install>\StarCitizen\LIVE\Game.log` (der Build-Ordner der laufenden StarCitizen.exe), nur die Logdatei, die das Spiel schreibt - ein Spiel mit Easy Anti-Cheat: nichts berührt seinen Prozess |
| [Steam-Statistiken (Plattform)](game-steam-stats.md) | platform | nein | Steams lokaler Statistik-Cache `%STEAM%\appcache\stats\UserGameStats_<account>_<appid>.bin` mit `UserGameStatsSchema_<appid>.bin`; Spielzeit aus `%STEAM%\userdata\<account>\config\localconfig.vdf` (%STEAM% aus `HKCU\Software\Valve\Steam` SteamPath) |
| [Steam Timeline (Plattform)](game-steam-timeline.md) | platform | nein | `%STEAM%\userdata\<account>\gamerecordings\timelines\timeline_<appid><date>_<time>.json` |
| [VALORANT (Replays)](game-valorant-replays.md) | replay | nein | Replays, die VALORANT speichert: `%LOCALAPPDATA%/VALORANT/Saved/Demos/*.vrf` (nur die Teile, die nicht verschleiert sind) |
| [War Thunder (Replays)](game-warthunder-replays.md) | replay | ja | Replays, die War Thunder speichert: `<War Thunder>/Replays/*.wrpl` (mit eingeschaltetem Replay-Speichern), umgewandelt vom externen Konverter `heat3d-wt-replay` (exporters/ext/warthunder-replay) |
| [War Thunder (Spielstand)](game-warthunder-webmap.md) | gsi | ja | die lokale Web-Karte des Spiels, <http://127.0.0.1:8111> (/map_info.json, /map_obj.json, /state, /indicators, /hudmsg, /gamechat, /mission.json, /map.img) |
| [World of Tanks (Replays)](game-wot-replays.md) | replay | ja | Replays, die World of Tanks speichert: `<World of Tanks>/replays/*.wotreplay` (mit eingeschalteter Gefechtsaufnahme), umgewandelt vom externen Konverter `heat3d-wot-replay` (exporters/ext/wot-replay) |
| [World of Warships (Replays)](game-wows-replays.md) | replay | ja | Replays, die World of Warships speichert: `<World of Warships>/replays/*.wowsreplay` (mit eingeschalteten Replays), umgewandelt vom externen Konverter `heat3d-wows-replay` (exporters/ext/wows-replay) |
| [X-Plane (Live-Daten)](game-xplane.md) | telemetry | ja | die UDP-Schnittstelle von X-Plane auf 127.0.0.1:49000 (RREF-Datarefs und RPOS-Position, dem Watcher beantwortet) |

Spiele, die nicht aufgezeichnet werden, und warum: [Quellen und Regeln](sources-and-rules.md#what-is-declined-and-why). Alles in einer Tabelle, so wie `python -m heat3d_watch games --markdown` es ausgibt: [Alle Spiele in einer Tabelle](watcher.md).

<!-- Generated by tools/gen_game_pages.py; run it again after changing an adapter. -->
