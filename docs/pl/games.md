---
title: Gry
nav_order: 4
lang: "pl"
source: games.md
source_hash: "dcee7fc45a5b"
nav_exclude: true
search_exclude: true
---
# Gry {#games}

Watcher zna 50 źródeł w 45 grach i platformach. Każde ma własną stronę, wygenerowaną z jego adaptera: co zapisuje, skąd, jak to włączyć, jak działa, jakie ma osie, co zostało sprawdzone.

Rodzaje: `telemetry`, `gsi`, `log`, `replay` i `platform` - zobacz [Źródła i zasady](sources-and-rules.md). Pozycje: *tak*, gdy adapter zapisuje wiersze z miejscem, *pożyczone*, gdy bierze miejsce z innego nagrania tej samej gry (zobacz [NVIDIA Highlights](nvidia-highlights.md)), *nie*, gdy źródło nie ma miejsc. Profile pamięci nie są tu wymienione: żaden nie jest dostarczany, a każdy gracz pisze własny (zobacz [Czytanie pamięci](memory-reading.md)).

| Gra | Rodzaj | Pozycje | Źródło |
|---|---|---|---|
| [American Truck Simulator (dane na żywo)](game-ats.md) | telemetry | tak | pamięć współdzielona `Local\SCSTelemetry` zapisywana przez wtyczkę RenCloud scs-sdk-plugin (wersja 12) w `<gra>\bin\win_x64\plugins` |
| [Assetto Corsa (dane na żywo)](game-assetto-corsa.md) | telemetry | tak | pamięć współdzielona `Local\acpmf_physics`, `Local\acpmf_graphics`, `Local\acpmf_static` |
| [Assetto Corsa Competizione (dane na żywo)](game-assetto-corsa-competizione.md) | telemetry | tak | pamięć współdzielona `Local\acpmf_physics`, `Local\acpmf_graphics`, `Local\acpmf_static` |
| [Assetto Corsa EVO (dane na żywo)](game-assetto-corsa-evo.md) | telemetry | tak | pamięć współdzielona `Local\acevo_pmf_physics`, `Local\acevo_pmf_static` |
| [Assetto Corsa Rally (dane na żywo)](game-assetto-corsa-rally.md) | telemetry | tak | pamięć współdzielona `Local\acpmf_physics`, `Local\acpmf_static` (te same strony co AC i ACC) |
| [Automobilista 2 (dane na żywo)](game-automobilista-2.md) | telemetry | tak | pamięć współdzielona $pcars2$ (układ SMS SharedMemory.h) |
| [BeamNG.drive (dane na żywo)](game-beamng.md) | telemetry | tak | UDP 127.0.0.1:4460 z modu protokołu heat3d (mods/beamng/heat3d w tym repozytorium) |
| [Counter-Strike 2 (powtórki)](game-cs2-demos.md) | replay | tak | dema, które zapisuje CS2: `<CS2>/game/csgo/replays/*.dem` (pobrane z historii meczów) i `<CS2>/game/csgo/*.dem` (nagrane) |
| [Counter-Strike 2 (stan gry)](game-cs2-gsi.md) | gsi | tak | Game State Integration: żądania HTTP POST na 127.0.0.1:3311, ustawione w `<CS2>\game\csgo\cfg\gamestate_integration_heat3d.cfg` |
| [DCS World (dane na żywo)](game-dcs.md) | telemetry | tak | hak watchera `%USERPROFILE%\Saved` `Games\DCS*\Scripts\Hooks\heat3d-watch.lua`, linie UDP na 127.0.0.1:41993 |
| [DiRT Rally 2.0 (dane na żywo)](game-dirt-rally-2.md) | telemetry | tak | UDP 127.0.0.1:20777, extradata=3 `(Dokumenty\My` `Games\DiRT` Rally `2.0\hardwaresettings\hardware_settings_config.xml`); gdy inna aplikacja zajmuje port 20777, watcher zostawia port jej |
| [Dota 2 (powtórki)](game-dota-replays.md) | replay | tak | powtórki, które zapisuje Dota 2: `<Dota>/game/dota/replays/<id meczu>.dem` (pobrane w kliencie albo poleceniem `dota-replay <id meczu>`) |
| [Dota 2 (stan gry)](game-dota2-gsi.md) | gsi | tak | Game State Integration: żądania HTTP POST na 127.0.0.1:3312, ustawione w `<Dota>\game\dota\cfg\gamestate_integration\gamestate_integration_heat3d.cfg` |
| [EA SPORTS F1 23 (dane na żywo)](game-f1-23.md) | telemetry | tak | telemetria UDP 127.0.0.1:20777 `(Dokumenty\My` `Games\F1` `23\hardwaresettings\hardware_settings_config.xml`) |
| [EA SPORTS F1 24 (dane na żywo)](game-f1-24.md) | telemetry | tak | telemetria UDP 127.0.0.1:20777 `(Dokumenty\My` `Games\F1` `24\hardwaresettings\hardware_settings_config.xml`) |
| [EA SPORTS F1 25 (dane na żywo)](game-f1-25.md) | telemetry | tak | telemetria UDP 127.0.0.1:20777 `(Dokumenty\My` `Games\F1` `25\hardwaresettings\hardware_settings_config.xml`) |
| [EA SPORTS WRC (dane na żywo)](game-ea-wrc.md) | telemetry | tak | UDP 127.0.0.1:20777, pakiet session_update domyślnej struktury `wrc` `(Dokumenty\My` `Games\WRC\telemetry\config.json`); gdy inna aplikacja zajmuje port 20777, watcher zostawia port jej |
| [Elite Dangerous (pliki dziennika)](game-elite.md) | log | tak | dziennik gracza `%USERPROFILE%\Saved` `Games\Frontier` `Developments\Elite` `Dangerous\Journal.*.log` (najnowszy plik, śledzony w miarę zapisu), Status.json i inne pliki `*.json` towarzyszące (Market, Outfitting, Shipyard, NavRoute, Cargo, ModulesInfo, ShipLocker, Backpack, FCMaterials) w tym samym folderze |
| [Euro Truck Simulator 2 (dane na żywo)](game-ets2.md) | telemetry | tak | pamięć współdzielona `Local\SCSTelemetry` zapisywana przez wtyczkę RenCloud scs-sdk-plugin (wersja 12) w `<gra>\bin\win_x64\plugins` |
| [EVE Online (pliki dziennika)](game-eve.md) | log | nie | `%USERPROFILE%\Documents\EVE\logs\Gamelogs\*.txt` i `Chatlogs\*.txt` obok (każdy plik zapisany od startu klienta) |
| [Forza Horizon 4 (dane na żywo)](game-forza-horizon-4.md) | telemetry | tak | Forza Data Out, UDP 127.0.0.1:5300 (format Dash); każdy pakiet przekazywany bez zmian na 127.0.0.1:5301 |
| [Forza Horizon 5 (dane na żywo)](game-forza-horizon-5.md) | telemetry | tak | Forza Data Out, UDP 127.0.0.1:5300 (format Dash); każdy pakiet przekazywany bez zmian na 127.0.0.1:5301 |
| [Forza Horizon 6 (dane na żywo)](game-forza-horizon-6.md) | telemetry | tak | Forza Data Out, UDP 127.0.0.1:5300 (format Dash); każdy pakiet przekazywany bez zmian na 127.0.0.1:5301 |
| [Forza Motorsport (dane na żywo)](game-forza-motorsport.md) | telemetry | tak | Forza Data Out, UDP 127.0.0.1:5300 (format Dash); każdy pakiet przekazywany bez zmian na 127.0.0.1:5301 |
| [Hearthstone (pliki dziennika)](game-hearthstone.md) | log | nie | `<instalacja>\Logs\Power.log` (albo `Logs\Hearthstone_*\Power.log`), zapisywany, gdy `%LOCALAPPDATA%\Blizzard\Hearthstone\log.config` ma sekcję [Power], oraz każdy inny `*.log`, który gra tam zapisuje |
| [IL-2 Sturmovik: Great Battles (dane na żywo)](game-il2.md) | telemetry | nie | wyjście telemetrii gry przez UDP na 127.0.0.1:41995 ([KEY = telemetrydevice] w `<gra>\data\startup.cfg`) |
| [IL-2 Sturmovik: Great Battles (powtórki)](game-il2-tacview.md) | replay | tak | nagrania Tacview zapisywane przez grę `<gra>\data\Tracks\*.acmi` (ACMI 2.x, tekst zwykły albo spakowany) |
| [iRacing (dane na żywo)](game-iracing.md) | telemetry | nie | pamięć współdzielona `Local\IRSDKMemMapFileName` (SDK iRacing); pliki .ibt w `%USERPROFILE%\Documents\iRacing\telemetry` |
| [League of Legends (stan gry)](game-lol-live.md) | gsi | nie | Live Client Data API klienta gry, <https://127.0.0.1:2999/liveclientdata/> (allgamedata, eventdata), podczas meczu |
| [League of Legends (powtórki)](game-lol-replays.md) | replay | tak | powtórki, które zapisuje klient League: %USERPROFILE%/Documents/League of `Legends/Replays/*.rofl` (tylko zwykłe dane z końca meczu); z własnym kluczem Riot API - oficjalna oś czasu meczu z Match-V5 API Riot |
| [Microsoft Flight Simulator 2020 (dane na żywo)](game-msfs2020.md) | telemetry | tak | SimConnect przez własną bibliotekę SimConnect.dll gracza (folder symulatora albo `%MSFS_SDK%\SimConnect` `SDK\lib`) |
| [Microsoft Flight Simulator 2024 (dane na żywo)](game-msfs2024.md) | telemetry | tak | SimConnect przez własną bibliotekę SimConnect.dll gracza (folder symulatora albo `%MSFS2024_SDK%\SimConnect` `SDK\lib`) |
| [Minecraft (pliki dziennika)](game-minecraft.md) | log | tak | `%APPDATA%\.minecraft\logs\latest.log` (śledzony), `saves\<świat>\stats\<uuid>.json` i `saves\<świat>\playerdata\<uuid>.dat` / level.dat (NBT w gzip), czytane, gdy gra je zapisze |
| [NVIDIA highlights (platforma)](game-nvidia-highlights.md) | platform | pożyczone | `%LOCALAPPDATA%\NVIDIA` `Corporation\NVIDIA` `Overlay\UGCTracker.json`, GallerySettings.json, `Highlights\<gra>\config.json`; klipy w folderze nagrań `(%USERPROFILE%\Videos\NVIDIA\<Gra>\*.mp4`) i `<temp>\Highlights\<gra>`; `%LOCALAPPDATA%\NVIDIA` `Corporation\GfeSDK\<exe>_<pid>.log` |
| [osu! (powtórki)](game-osu-replays.md) | replay | tak | powtórki, które zapisuje osu! (stabilna wersja): `%LOCALAPPDATA%/osu!/Data/r/*.osr` (każda gra) i `osu!/Replays/*.osr` (wyeksportowane) |
| [Path of Exile (pliki dziennika)](game-poe.md) | log | nie | `<instalacja>\logs\Client.txt` Path of Exile albo Path of Exile 2 (śledzony; folder instalacji to folder uruchomionego pliku wykonywalnego) |
| [Project CARS 2 (dane na żywo)](game-project-cars-2.md) | telemetry | tak | pamięć współdzielona $pcars2$ (SMS SharedMemory.h) |
| [RaceRoom Racing Experience (dane na żywo)](game-raceroom.md) | telemetry | tak | pamięć współdzielona $R3E (r3e.h Sector3, wersja 3) |
| [Richard Burns Rally (dane na żywo)](game-richard-burns-rally.md) | telemetry | tak | telemetria UDP wtyczki NGP, 127.0.0.1:6776 (RichardBurnsRally.ini [NGP] udpTelemetry=1) |
| [Rocket League (stan gry)](game-rocketleague-stats.md) | gsi | tak | Stats API: strumień JSON po TCP z 127.0.0.1:49123 (port w `<RL>\TAGame\Config\TAStatsAPI.ini` albo DefaultStatsAPI.ini) |
| [Squad (powtórki)](game-squad-demos.md) | replay | tak | dema z serwerów, które Squad nagrywa poleceniem administratora AdminDemoRec: `<serwer>/SquadGame/Saved/Demos/*.replay`, czytane przez zewnętrzny czytnik `heat3d-squad-demo` (exporters/ext/squad-demo) |
| [Star Citizen (pliki dziennika)](game-starcitizen.md) | log | nie | `<instalacja>\StarCitizen\LIVE\Game.log` (folder wersji uruchomionego StarCitizen.exe), tylko plik dziennika, który zapisuje gra - gra z Easy Anti-Cheat: nic nie dotyka jej procesu |
| [Statystyki Steam (platforma)](game-steam-stats.md) | platform | nie | lokalna pamięć podręczna statystyk Steam `%STEAM%\appcache\stats\UserGameStats_<konto>_<appid>.bin` z `UserGameStatsSchema_<appid>.bin`; czas gry z `%STEAM%\userdata\<konto>\config\localconfig.vdf` (%STEAM% z `HKCU\Software\Valve\Steam` SteamPath) |
| [Oś czasu Steam (platforma)](game-steam-timeline.md) | platform | nie | `%STEAM%\userdata\<konto>\gamerecordings\timelines\timeline_<appid><data>_<czas>.json` |
| [VALORANT (powtórki)](game-valorant-replays.md) | replay | nie | powtórki, które zapisuje VALORANT: `%LOCALAPPDATA%/VALORANT/Saved/Demos/*.vrf` (tylko części, które nie są zaciemnione) |
| [War Thunder (powtórki)](game-warthunder-replays.md) | replay | tak | powtórki, które zapisuje War Thunder: `<War` `Thunder>/Replays/*.wrpl` (z włączonym zapisem powtórek), konwertowane przez zewnętrzny konwerter `heat3d-wt-replay` (exporters/ext/warthunder-replay) |
| [War Thunder (stan gry)](game-warthunder-webmap.md) | gsi | tak | lokalna mapa webowa gry, <http://127.0.0.1:8111> (/map_info.json, /map_obj.json, /state, /indicators, /hudmsg, /gamechat, /mission.json, /map.img) |
| [World of Tanks (powtórki)](game-wot-replays.md) | replay | tak | powtórki, które zapisuje World of Tanks: `<World` of `Tanks>/replays/*.wotreplay` (z włączonym nagrywaniem bitew), konwertowane przez zewnętrzny konwerter `heat3d-wot-replay` (exporters/ext/wot-replay) |
| [World of Warships (powtórki)](game-wows-replays.md) | replay | tak | powtórki, które zapisuje World of Warships: `<World` of `Warships>/replays/*.wowsreplay` (z włączonymi powtórkami), konwertowane przez zewnętrzny konwerter `heat3d-wows-replay` (exporters/ext/wows-replay) |
| [X-Plane (dane na żywo)](game-xplane.md) | telemetry | tak | interfejs UDP X-Plane na 127.0.0.1:49000 (datarefy RREF i RPOS), odpowiadany do watchera |

Gry, których nie zapisujemy, i dlaczego: [Źródła i zasady](sources-and-rules.md#what-is-declined-and-why). Wszystko w jednej tabeli, tak jak wypisuje ją `python -m heat3d_watch games --markdown`: [Wszystkie gry w jednej tabeli](watcher.md).

<!-- Generated by tools/gen_game_pages.py; run it again after changing an adapter. -->
