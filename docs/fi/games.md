---
title: Pelit
nav_order: 4
lang: "fi"
source: games.md
source_hash: "c601550fbb4e"
nav_exclude: true
search_exclude: true
---
# Pelit {#games}

Watcher tuntee 49 lähdettä 44 pelissä ja alustassa. Jokaisella on oma sivunsa, joka on luotu sen adapterista: mitä se tallentaa, mistä, miten se kytketään päälle, miten se toimii, sen akselit ja mitä on todennettu.

Tyypit: `telemetry`, `gsi`, `log`, `replay` ja `platform`. Katso [Lähteet ja säännöt](sources-and-rules.md). Sijainnit: *kyllä*, kun adapteri kirjoittaa rivejä, joilla on paikka; *lainattu*, kun paikka otetaan saman pelin toisesta tallenteesta (katso [NVIDIA Highlights](nvidia-highlights.md)); *ei*, kun lähteessä ei ole paikkaa. Muistiprofiileja ei luetella: niitä ei toimiteta mukana, ja jokainen pelaaja kirjoittaa omansa (katso [Muistin lukeminen](memory-reading.md)).

| Peli | Tyyppi | Sijainnit | Lähde |
|---|---|---|---|
| [American Truck Simulator (live-data)](game-ats.md) | telemetry | kyllä | jaettu muisti `Local\SCSTelemetry`, jonka kirjoittaa RenCloud scs-sdk-plugin (revisio 12) kansiossa `<game>\bin\win_x64\plugins` |
| [Assetto Corsa (live-data)](game-assetto-corsa.md) | telemetry | kyllä | jaettu muisti `Local\acpmf_physics`, `Local\acpmf_graphics`, `Local\acpmf_static` |
| [Assetto Corsa Competizione (live-data)](game-assetto-corsa-competizione.md) | telemetry | kyllä | jaettu muisti `Local\acpmf_physics`, `Local\acpmf_graphics`, `Local\acpmf_static` |
| [Assetto Corsa EVO (live-data)](game-assetto-corsa-evo.md) | telemetry | kyllä | jaettu muisti `Local\acevo_pmf_physics`, `Local\acevo_pmf_static` |
| [Assetto Corsa Rally (live-data)](game-assetto-corsa-rally.md) | telemetry | kyllä | jaettu muisti `Local\acpmf_physics`, `Local\acpmf_static` (samat sivut kuin AC ja ACC) |
| [Automobilista 2 (live-data)](game-automobilista-2.md) | telemetry | kyllä | jaettu muisti $pcars2$ (SMS SharedMemory.h -asettelu) |
| [BeamNG.drive (live-data)](game-beamng.md) | telemetry | kyllä | UDP 127.0.0.1:4460 heat3d-protokollamodista (mods/beamng/heat3d tässä repositoriossa) |
| [Counter-Strike 2 (toistot)](game-cs2-demos.md) | replay | kyllä | demot, jotka CS2 tallentaa: `<CS2>/game/csgo/replays/*.dem` (ladattu otteluhistoriasta) ja `<CS2>/game/csgo/*.dem` (tallennettu) |
| [Counter-Strike 2 (pelitila)](game-cs2-gsi.md) | gsi | kyllä | Game State Integration: HTTP-POST-pyynnöt osoitteeseen 127.0.0.1:3311, asetukset tiedostossa `<CS2>\game\csgo\cfg\gamestate_integration_heat3d.cfg` |
| [DCS World (live-data)](game-dcs.md) | telemetry | kyllä | watcherin koukku `%USERPROFILE%\Saved` `Games\DCS*\Scripts\Hooks\heat3d-watch.lua`, UDP-rivit osoitteeseen 127.0.0.1:41993 |
| [DiRT Rally 2.0 (live-data)](game-dirt-rally-2.md) | telemetry | kyllä | UDP 127.0.0.1:20777, extradata=3 `(Documents\My` `Games\DiRT` Rally `2.0\hardwaresettings\hardware_settings_config.xml`); kun toinen sovellus pitää porttia 20777 hallussaan, watcher jättää portin sille |
| [Dota 2 (toistot)](game-dota-replays.md) | replay | kyllä | toistot, jotka Dota 2 tallentaa: `<Dota>/game/dota/replays/<match id>.dem` (ladattu asiakkaassa tai komennolla `dota-replay <match id>`) |
| [Dota 2 (pelitila)](game-dota2-gsi.md) | gsi | kyllä | Game State Integration: HTTP-POST-pyynnöt osoitteeseen 127.0.0.1:3312, asetukset tiedostossa `<Dota>\game\dota\cfg\gamestate_integration\gamestate_integration_heat3d.cfg` |
| [EA SPORTS F1 23 (live-data)](game-f1-23.md) | telemetry | kyllä | UDP-telemetria 127.0.0.1:20777 `(Documents\My` `Games\F1` `23\hardwaresettings\hardware_settings_config.xml`) |
| [EA SPORTS F1 24 (live-data)](game-f1-24.md) | telemetry | kyllä | UDP-telemetria 127.0.0.1:20777 `(Documents\My` `Games\F1` `24\hardwaresettings\hardware_settings_config.xml`) |
| [EA SPORTS F1 25 (live-data)](game-f1-25.md) | telemetry | kyllä | UDP-telemetria 127.0.0.1:20777 `(Documents\My` `Games\F1` `25\hardwaresettings\hardware_settings_config.xml`) |
| [EA SPORTS WRC (live-data)](game-ea-wrc.md) | telemetry | kyllä | UDP 127.0.0.1:20777, oletusrakenteen `wrc` session_update-paketti `(Documents\My` `Games\WRC\telemetry\config.json`); kun toinen sovellus pitää porttia 20777 hallussaan, watcher jättää portin sille |
| [Elite Dangerous (lokitiedostot)](game-elite.md) | log | kyllä | pelaajan päiväkirja `%USERPROFILE%\Saved` `Games\Frontier` `Developments\Elite` `Dangerous\Journal.*.log` (uusin tiedosto, seurataan kun sitä kirjoitetaan), Status.json sekä muut kumppanitiedostot `*.json` (Market, Outfitting, Shipyard, NavRoute, Cargo, ModulesInfo, ShipLocker, Backpack, FCMaterials) samassa kansiossa |
| [Euro Truck Simulator 2 (live-data)](game-ets2.md) | telemetry | kyllä | jaettu muisti `Local\SCSTelemetry`, jonka kirjoittaa RenCloud scs-sdk-plugin (revisio 12) kansiossa `<game>\bin\win_x64\plugins` |
| [EVE Online (lokitiedostot)](game-eve.md) | log | ei | `%USERPROFILE%\Documents\EVE\logs\Gamelogs\*.txt` ja niiden vieressä olevat `Chatlogs\*.txt` (jokainen tiedosto, joka on kirjoitettu asiakkaan käynnistyksestä asti) |
| [Forza Horizon 4 (live-data)](game-forza-horizon-4.md) | telemetry | kyllä | Forza Data Out, UDP 127.0.0.1:5300 (Dash-muoto); jokainen paketti välitetään muuttumattomana osoitteeseen 127.0.0.1:5301 |
| [Forza Horizon 5 (live-data)](game-forza-horizon-5.md) | telemetry | kyllä | Forza Data Out, UDP 127.0.0.1:5300 (Dash-muoto); jokainen paketti välitetään muuttumattomana osoitteeseen 127.0.0.1:5301 |
| [Forza Horizon 6 (live-data)](game-forza-horizon-6.md) | telemetry | kyllä | Forza Data Out, UDP 127.0.0.1:5300 (Dash-muoto); jokainen paketti välitetään muuttumattomana osoitteeseen 127.0.0.1:5301 |
| [Forza Motorsport (live-data)](game-forza-motorsport.md) | telemetry | kyllä | Forza Data Out, UDP 127.0.0.1:5300 (Dash-muoto); jokainen paketti välitetään muuttumattomana osoitteeseen 127.0.0.1:5301 |
| [Hearthstone (lokitiedostot)](game-hearthstone.md) | log | ei | `<install>\Logs\Power.log` (tai `Logs\Hearthstone_*\Power.log`), kirjoitettuna kun `%LOCALAPPDATA%\Blizzard\Hearthstone\log.config` sisältää [Power]-osion, ja jokainen muu `*.log`, jonka peli kirjoittaa siihen kansioon |
| [IL-2 Sturmovik: Great Battles (live-data)](game-il2.md) | telemetry | ei | pelin telemetrian UDP-tuloste osoitteeseen 127.0.0.1:41995 (`[KEY = telemetrydevice]` tiedostossa `<game>\data\startup.cfg`) |
| [IL-2 Sturmovik: Great Battles (toistot)](game-il2-tacview.md) | replay | kyllä | pelin oma Tacview-tallenne `<game>\data\Tracks\*.acmi` (ACMI 2.x -teksti, tavallinen tai pakattu) |
| [iRacing (live-data)](game-iracing.md) | telemetry | ei | jaettu muisti `Local\IRSDKMemMapFileName` (iRacing SDK); .ibt-tiedostot kansiossa `%USERPROFILE%\Documents\iRacing\telemetry` |
| [League of Legends (pelitila)](game-lol-live.md) | gsi | ei | peliasiakkaan Live Client Data API, <https://127.0.0.1:2999/liveclientdata/> (allgamedata, eventdata), ottelun aikana |
| [League of Legends (toistot)](game-lol-replays.md) | replay | kyllä | toistot, jotka League-asiakas tallentaa: %USERPROFILE%/Documents/League of `Legends/Replays/*.rofl` (vain tavallinen lopun metatieto); oman Riot API -avaimen kanssa ottelun virallinen aikajana Riotin Match-V5 API:sta |
| [Microsoft Flight Simulator 2020 (live-data)](game-msfs2020.md) | telemetry | kyllä | SimConnect pelaajan oman SimConnect.dll-tiedoston kautta (simulaattorin kansio tai `%MSFS_SDK%\SimConnect` `SDK\lib`) |
| [Microsoft Flight Simulator 2024 (live-data)](game-msfs2024.md) | telemetry | kyllä | SimConnect pelaajan oman SimConnect.dll-tiedoston kautta (simulaattorin kansio tai `%MSFS2024_SDK%\SimConnect` `SDK\lib`) |
| [Minecraft (lokitiedostot)](game-minecraft.md) | log | kyllä | `%APPDATA%\.minecraft\logs\latest.log` (seurataan), `saves\<world>\stats\<uuid>.json` ja `saves\<world>\playerdata\<uuid>.dat` / level.dat (gzip NBT), luetaan kun peli tallentaa ne |
| [NVIDIA highlights (alusta)](game-nvidia-highlights.md) | platform | lainattu | `%LOCALAPPDATA%\NVIDIA` `Corporation\NVIDIA` `Overlay\UGCTracker.json`, GallerySettings.json, `Highlights\<game>\config.json`; klipit tallennuskansiossa `(%USERPROFILE%\Videos\NVIDIA\<Game>\*.mp4`) ja `<temp>\Highlights\<game>`; `%LOCALAPPDATA%\NVIDIA` `Corporation\GfeSDK\<exe>_<pid>.log` |
| [Path of Exile (lokitiedostot)](game-poe.md) | log | ei | `<install>\logs\Client.txt` pelistä Path of Exile tai Path of Exile 2 (seurataan; asennuskansio on käynnissä olevan suoritettavan tiedoston kansio) |
| [Project CARS 2 (live-data)](game-project-cars-2.md) | telemetry | kyllä | jaettu muisti $pcars2$ (SMS SharedMemory.h) |
| [RaceRoom Racing Experience (live-data)](game-raceroom.md) | telemetry | kyllä | jaettu muisti $R3E (Sector3:n r3e.h, versio 3) |
| [Richard Burns Rally (live-data)](game-richard-burns-rally.md) | telemetry | kyllä | NGP-liitännäisen UDP-telemetria, 127.0.0.1:6776 (RichardBurnsRally.ini [NGP] udpTelemetry=1) |
| [Rocket League (pelitila)](game-rocketleague-stats.md) | gsi | kyllä | Stats API: TCP JSON -virta osoitteesta 127.0.0.1:49123 (portti tiedostossa `<RL>\TAGame\Config\TAStatsAPI.ini` tai DefaultStatsAPI.ini) |
| [Squad (toistot)](game-squad-demos.md) | replay | kyllä | palvelindemot, jotka Squad tallentaa admin-komennolla AdminDemoRec: `<server>/SquadGame/Saved/Demos/*.replay`, luetaan ulkoisella lukijalla `heat3d-squad-demo` (exporters/ext/squad-demo) |
| [Star Citizen (lokitiedostot)](game-starcitizen.md) | log | ei | `<install>\StarCitizen\LIVE\Game.log` (käynnissä olevan StarCitizen.exe:n buildikansio), vain pelin kirjoittama lokitiedosto. Easy Anti-Cheat -peli: mikään ei koske sen prosessiin |
| [Steam-tilastot (alusta)](game-steam-stats.md) | platform | ei | Steamin paikallinen tilastovälimuisti `%STEAM%\appcache\stats\UserGameStats_<account>_<appid>.bin` ja `UserGameStatsSchema_<appid>.bin`; peliaika tiedostosta `%STEAM%\userdata\<account>\config\localconfig.vdf` (%STEAM% kohdasta `HKCU\Software\Valve\Steam` SteamPath) |
| [Steam Timeline (alusta)](game-steam-timeline.md) | platform | ei | `%STEAM%\userdata\<account>\gamerecordings\timelines\timeline_<appid><date>_<time>.json` |
| [VALORANT (toistot)](game-valorant-replays.md) | replay | ei | toistot, jotka VALORANT tallentaa: `%LOCALAPPDATA%/VALORANT/Saved/Demos/*.vrf` (vain ne osat, jotka eivät ole hämärrettyjä) |
| [War Thunder (toistot)](game-warthunder-replays.md) | replay | kyllä | toistot, jotka War Thunder tallentaa: `<War Thunder>/Replays/*.wrpl` (toistojen tallennus päällä), muunnetaan ulkoisella muuntimella `heat3d-wt-replay` (exporters/ext/warthunder-replay) |
| [War Thunder (pelitila)](game-warthunder-webmap.md) | gsi | kyllä | pelin paikallinen web-kartta, <http://127.0.0.1:8111> (/map_info.json, /map_obj.json, /state, /indicators, /hudmsg, /gamechat, /mission.json, /map.img) |
| [World of Tanks (toistot)](game-wot-replays.md) | replay | kyllä | toistot, jotka World of Tanks tallentaa: `<World of Tanks>/replays/*.wotreplay` (taistelutallennus päällä), muunnetaan ulkoisella muuntimella `heat3d-wot-replay` (exporters/ext/wot-replay) |
| [World of Warships (toistot)](game-wows-replays.md) | replay | kyllä | toistot, jotka World of Warships tallentaa: `<World of Warships>/replays/*.wowsreplay` (toistot päällä), muunnetaan ulkoisella muuntimella `heat3d-wows-replay` (exporters/ext/wows-replay) |
| [X-Plane (live-data)](game-xplane.md) | telemetry | kyllä | X-Planen UDP-rajapinta osoitteessa 127.0.0.1:49000 (RREF-datarefit ja RPOS-sijainti, vastataan watcherille) |

Pelit, joita ei tallenneta, ja syyt: [Lähteet ja säännöt](sources-and-rules.md#what-is-declined-and-why). Kaikki yhdessä taulussa, kuten `python -m heat3d_watch games --markdown` tulostaa sen: [Kaikki pelit yhdessä taulussa](watcher.md).

<!-- Generated by tools/gen_game_pages.py; run it again after changing an adapter. -->
