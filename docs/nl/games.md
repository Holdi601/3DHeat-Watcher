---
title: Spellen
nav_order: 4
lang: "nl"
source: games.md
source_hash: "dcee7fc45a5b"
nav_exclude: true
search_exclude: true
---
# Spellen {#games}

De watcher kent 50 bronnen in 45 spellen en platforms. Elk heeft een eigen pagina, gegenereerd uit zijn adapter: wat het opslaat, waar het vandaan komt, hoe je het aanzet, hoe het werkt, zijn assen, wat er geverifieerd is.

Soorten: `telemetry`, `gsi`, `log`, `replay` en `platform` - zie [Bronnen en regels](sources-and-rules.md). Posities: *ja* wanneer de adapter rijen met een plek schrijft, *geleend* wanneer hij de plek overneemt van een andere opname van hetzelfde spel (zie [NVIDIA Highlights](nvidia-highlights.md)), *nee* wanneer de bron er geen heeft. Geheugenprofielen staan hier niet: er worden er geen meegeleverd, en elke speler schrijft er zelf een (zie [Geheugen lezen](memory-reading.md)).

| Spel | Soort | Posities | Bron |
|---|---|---|---|
| [American Truck Simulator (live data)](game-ats.md) | telemetry | ja | gedeeld geheugen `Local\SCSTelemetry`, geschreven door de RenCloud scs-sdk-plugin (revisie 12) in `<game>\bin\win_x64\plugins` |
| [Assetto Corsa (live data)](game-assetto-corsa.md) | telemetry | ja | gedeeld geheugen `Local\acpmf_physics`, `Local\acpmf_graphics`, `Local\acpmf_static` |
| [Assetto Corsa Competizione (live data)](game-assetto-corsa-competizione.md) | telemetry | ja | gedeeld geheugen `Local\acpmf_physics`, `Local\acpmf_graphics`, `Local\acpmf_static` |
| [Assetto Corsa EVO (live data)](game-assetto-corsa-evo.md) | telemetry | ja | gedeeld geheugen `Local\acevo_pmf_physics`, `Local\acevo_pmf_static` |
| [Assetto Corsa Rally (live data)](game-assetto-corsa-rally.md) | telemetry | ja | gedeeld geheugen `Local\acpmf_physics`, `Local\acpmf_static` (dezelfde pagina's als AC en ACC) |
| [Automobilista 2 (live data)](game-automobilista-2.md) | telemetry | ja | gedeeld geheugen $pcars2$ (indeling SMS SharedMemory.h) |
| [BeamNG.drive (live data)](game-beamng.md) | telemetry | ja | UDP 127.0.0.1:4460 van de heat3d-protocolmod (mods/beamng/heat3d in deze repository) |
| [Counter-Strike 2 (replays)](game-cs2-demos.md) | replay | ja | demo's die CS2 opslaat: `<CS2>/game/csgo/replays/*.dem` (gedownload uit de wedstrijdgeschiedenis) en `<CS2>/game/csgo/*.dem` (opgenomen) |
| [Counter-Strike 2 (spelstatus)](game-cs2-gsi.md) | gsi | ja | Game State Integration: HTTP-POST's naar 127.0.0.1:3311, ingesteld door `<CS2>\game\csgo\cfg\gamestate_integration_heat3d.cfg` |
| [DCS World (live data)](game-dcs.md) | telemetry | ja | de hook van de watcher `%USERPROFILE%\Saved` `Games\DCS*\Scripts\Hooks\heat3d-watch.lua`, UDP-regels naar 127.0.0.1:41993 |
| [DiRT Rally 2.0 (live data)](game-dirt-rally-2.md) | telemetry | ja | UDP 127.0.0.1:20777, extradata=3 `(Documents\My` `Games\DiRT` Rally `2.0\hardwaresettings\hardware_settings_config.xml`); zolang een andere app poort 20777 vasthoudt, laat de watcher de poort aan die app over |
| [Dota 2 (replays)](game-dota-replays.md) | replay | ja | replays die Dota 2 opslaat: `<Dota>/game/dota/replays/<match` id>.dem (gedownload in de client, of met `dota-replay <match id>`) |
| [Dota 2 (spelstatus)](game-dota2-gsi.md) | gsi | ja | Game State Integration: HTTP-POST's naar 127.0.0.1:3312, ingesteld door `<Dota>\game\dota\cfg\gamestate_integration\gamestate_integration_heat3d.cfg` |
| [EA SPORTS F1 23 (live data)](game-f1-23.md) | telemetry | ja | UDP-telemetrie 127.0.0.1:20777 `(Documents\My` `Games\F1` `23\hardwaresettings\hardware_settings_config.xml`) |
| [EA SPORTS F1 24 (live data)](game-f1-24.md) | telemetry | ja | UDP-telemetrie 127.0.0.1:20777 `(Documents\My` `Games\F1` `24\hardwaresettings\hardware_settings_config.xml`) |
| [EA SPORTS F1 25 (live data)](game-f1-25.md) | telemetry | ja | UDP-telemetrie 127.0.0.1:20777 `(Documents\My` `Games\F1` `25\hardwaresettings\hardware_settings_config.xml`) |
| [EA SPORTS WRC (live data)](game-ea-wrc.md) | telemetry | ja | UDP 127.0.0.1:20777, het standaard `wrc`-schema van het session_update-pakket `(Documents\My` `Games\WRC\telemetry\config.json`); zolang een andere app poort 20777 vasthoudt, laat de watcher de poort aan die app over |
| [Elite Dangerous (logbestanden)](game-elite.md) | log | ja | Player Journal `%USERPROFILE%\Saved` `Games\Frontier` `Developments\Elite` `Dangerous\Journal.*.log` (nieuwste bestand, gevolgd terwijl het geschreven wordt), Status.json en de andere companion-`*.json`-bestanden (Market, Outfitting, Shipyard, NavRoute, Cargo, ModulesInfo, ShipLocker, Backpack, FCMaterials) in dezelfde map |
| [Euro Truck Simulator 2 (live data)](game-ets2.md) | telemetry | ja | gedeeld geheugen `Local\SCSTelemetry`, geschreven door de RenCloud scs-sdk-plugin (revisie 12) in `<game>\bin\win_x64\plugins` |
| [EVE Online (logbestanden)](game-eve.md) | log | nee | `%USERPROFILE%\Documents\EVE\logs\Gamelogs\*.txt` en de `Chatlogs\*.txt` ernaast (elk bestand dat geschreven is sinds de client startte) |
| [Forza Horizon 4 (live data)](game-forza-horizon-4.md) | telemetry | ja | Forza Data Out, UDP 127.0.0.1:5300 (Dash-formaat); elk pakket ongewijzigd doorgestuurd naar 127.0.0.1:5301 |
| [Forza Horizon 5 (live data)](game-forza-horizon-5.md) | telemetry | ja | Forza Data Out, UDP 127.0.0.1:5300 (Dash-formaat); elk pakket ongewijzigd doorgestuurd naar 127.0.0.1:5301 |
| [Forza Horizon 6 (live data)](game-forza-horizon-6.md) | telemetry | ja | Forza Data Out, UDP 127.0.0.1:5300 (Dash-formaat); elk pakket ongewijzigd doorgestuurd naar 127.0.0.1:5301 |
| [Forza Motorsport (live data)](game-forza-motorsport.md) | telemetry | ja | Forza Data Out, UDP 127.0.0.1:5300 (Dash-formaat); elk pakket ongewijzigd doorgestuurd naar 127.0.0.1:5301 |
| [Hearthstone (logbestanden)](game-hearthstone.md) | log | nee | `<install>\Logs\Power.log` (of `Logs\Hearthstone_*\Power.log`), geschreven zodra `%LOCALAPPDATA%\Blizzard\Hearthstone\log.config` een [Power]-sectie heeft, en elk ander `*.log`-bestand dat het spel daar schrijft |
| [IL-2 Sturmovik: Great Battles (live data)](game-il2.md) | telemetry | nee | de telemetrie-uitvoer van het spel via UDP naar 127.0.0.1:41995 ([KEY = telemetrydevice] in `<game>\data\startup.cfg`) |
| [IL-2 Sturmovik: Great Battles (replays)](game-il2-tacview.md) | replay | ja | de eigen Tacview-opnamen van het spel `<game>\data\Tracks\*.acmi` (ACMI 2.x-tekst, gewoon of gezipt) |
| [iRacing (live data)](game-iracing.md) | telemetry | nee | gedeeld geheugen `Local\IRSDKMemMapFileName` (de iRacing SDK); .ibt-bestanden in `%USERPROFILE%\Documents\iRacing\telemetry` |
| [League of Legends (spelstatus)](game-lol-live.md) | gsi | nee | Live Client Data API van de spelclient, <https://127.0.0.1:2999/liveclientdata/> (allgamedata, eventdata), tijdens een wedstrijd |
| [League of Legends (replays)](game-lol-replays.md) | replay | ja | replays die de League-client opslaat: %USERPROFILE%/Documents/League of `Legends/Replays/*.rofl` (alleen de gewone metadata van het einde van het spel); met je eigen Riot API-sleutel de officiële tijdlijn van de wedstrijd uit de Match-V5 API van Riot |
| [Microsoft Flight Simulator 2020 (live data)](game-msfs2020.md) | telemetry | ja | SimConnect via de eigen SimConnect.dll van de speler (de simulatiemap, of `%MSFS_SDK%\SimConnect` `SDK\lib`) |
| [Microsoft Flight Simulator 2024 (live data)](game-msfs2024.md) | telemetry | ja | SimConnect via de eigen SimConnect.dll van de speler (de simulatiemap, of `%MSFS2024_SDK%\SimConnect` `SDK\lib`) |
| [Minecraft (logbestanden)](game-minecraft.md) | log | ja | `%APPDATA%\.minecraft\logs\latest.log` (gevolgd), `saves\<world>\stats\<uuid>.json` en `saves\<world>\playerdata\<uuid>.dat` / level.dat (gzip-NBT), gelezen wanneer het spel ze opslaat |
| [NVIDIA highlights (platform)](game-nvidia-highlights.md) | platform | geleend | `%LOCALAPPDATA%\NVIDIA` `Corporation\NVIDIA` `Overlay\UGCTracker.json`, GallerySettings.json, `Highlights\<game>\config.json`; clips in de opslagmap `(%USERPROFILE%\Videos\NVIDIA\<Game>\*.mp4`) en `<temp>\Highlights\<game>`; `%LOCALAPPDATA%\NVIDIA` `Corporation\GfeSDK\<exe>_<pid>.log` |
| [osu! (replays)](game-osu-replays.md) | replay | ja | replays die osu! (stable) opslaat: `%LOCALAPPDATA%/osu!/Data/r/*.osr` (elk speelmoment) en `osu!/Replays/*.osr` (geëxporteerd) |
| [Path of Exile (logbestanden)](game-poe.md) | log | nee | `<install>\logs\Client.txt` van Path of Exile of Path of Exile 2 (gevolgd; de installatiemap is die van het draaiende uitvoerbare bestand) |
| [Project CARS 2 (live data)](game-project-cars-2.md) | telemetry | ja | gedeeld geheugen $pcars2$ (SMS SharedMemory.h) |
| [RaceRoom Racing Experience (live data)](game-raceroom.md) | telemetry | ja | gedeeld geheugen $R3E (r3e.h van Sector3, versie 3) |
| [Richard Burns Rally (live data)](game-richard-burns-rally.md) | telemetry | ja | UDP-telemetrie van de NGP-plugin, 127.0.0.1:6776 (RichardBurnsRally.ini [NGP] udpTelemetry=1) |
| [Rocket League (spelstatus)](game-rocketleague-stats.md) | gsi | ja | Stats API: TCP-JSON-stroom van 127.0.0.1:49123 (poort in `<RL>\TAGame\Config\TAStatsAPI.ini` of DefaultStatsAPI.ini) |
| [Squad (replays)](game-squad-demos.md) | replay | ja | serverdemo's die Squad opneemt met het beheerdersbevel AdminDemoRec: `<server>/SquadGame/Saved/Demos/*.replay`, gelezen door de externe lezer `heat3d-squad-demo` (exporters/ext/squad-demo) |
| [Star Citizen (logbestanden)](game-starcitizen.md) | log | nee | `<install>\StarCitizen\LIVE\Game.log` (de buildmap van het draaiende StarCitizen.exe), alleen het logbestand dat het spel schrijft - een spel met Easy Anti-Cheat: niets raakt het proces aan |
| [Steam-statistieken (platform)](game-steam-stats.md) | platform | nee | Steam's lokale statistiekencache `%STEAM%\appcache\stats\UserGameStats_<account>_<appid>.bin` met `UserGameStatsSchema_<appid>.bin`; speeltijd uit `%STEAM%\userdata\<account>\config\localconfig.vdf` (%STEAM% uit `HKCU\Software\Valve\Steam` SteamPath) |
| [Steam Timeline (platform)](game-steam-timeline.md) | platform | nee | `%STEAM%\userdata\<account>\gamerecordings\timelines\timeline_<appid><date>_<time>.json` |
| [VALORANT (replays)](game-valorant-replays.md) | replay | nee | replays die VALORANT opslaat: `%LOCALAPPDATA%/VALORANT/Saved/Demos/*.vrf` (alleen de delen die niet versleuteld zijn) |
| [War Thunder (replays)](game-warthunder-replays.md) | replay | ja | replays die War Thunder opslaat: `<War` `Thunder>/Replays/*.wrpl` (met replay-opslaan aan), omgezet door de externe converter `heat3d-wt-replay` (exporters/ext/warthunder-replay) |
| [War Thunder (spelstatus)](game-warthunder-webmap.md) | gsi | ja | de lokale webmap van het spel, <http://127.0.0.1:8111> (/map_info.json, /map_obj.json, /state, /indicators, /hudmsg, /gamechat, /mission.json, /map.img) |
| [World of Tanks (replays)](game-wot-replays.md) | replay | ja | replays die World of Tanks opslaat: `<World` of `Tanks>/replays/*.wotreplay` (met gevechtsopname aan), omgezet door de externe converter `heat3d-wot-replay` (exporters/ext/wot-replay) |
| [World of Warships (replays)](game-wows-replays.md) | replay | ja | replays die World of Warships opslaat: `<World` of `Warships>/replays/*.wowsreplay` (met replays aan), omgezet door de externe converter `heat3d-wows-replay` (exporters/ext/wows-replay) |
| [X-Plane (live data)](game-xplane.md) | telemetry | ja | de UDP-interface van X-Plane op 127.0.0.1:49000 (RREF-datarefs en RPOS-positie, beantwoord aan de watcher) |

Spellen die niet worden vastgelegd, en waarom: [Bronnen en regels](sources-and-rules.md#what-is-declined-and-why). Alles in één tabel, zoals `python -m heat3d_watch games --markdown` het afdrukt: [Alle spellen in één tabel](watcher.md).

<!-- Gegenereerd door tools/gen_game_pages.py; voer het opnieuw uit na het wijzigen van een adapter. -->
