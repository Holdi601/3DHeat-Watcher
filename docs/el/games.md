---
title: Παιχνίδια
nav_order: 4
lang: "el"
source: games.md
source_hash: "0766c0bb0763"
nav_exclude: true
search_exclude: true
---
# Παιχνίδια {#games}

Ο watcher γνωρίζει 50 πηγές σε 45 παιχνίδια και πλατφόρμες. Καθεμία έχει δική της σελίδα, που δημιουργείται από τον adapter της: τι καταγράφει, από πού, πώς την ενεργοποιείτε, πώς λειτουργεί, οι άξονές της, τι επαληθεύτηκε.

Είδη: `telemetry`, `gsi`, `log`, `replay` και `platform` - βλ. [Sources and rules](sources-and-rules.md). Θέσεις: *ναι* όταν ο adapter γράφει γραμμές με τόπο, *δανεικές* όταν τον παίρνει από μια άλλη εγγραφή του ίδιου παιχνιδιού (βλ. [NVIDIA Highlights](nvidia-highlights.md)), *όχι* όταν η πηγή δεν έχει τόπο. Τα προφίλ μνήμης δεν αναφέρονται: κανένα δεν συνοδεύει τον watcher, και ο καθένας γράφει το δικό του (βλ. [Reading memory](memory-reading.md)).

| Παιχνίδι | Είδος | Θέσεις | Πηγή |
|---|---|---|---|
| [American Truck Simulator (ζωντανά δεδομένα)](game-ats.md) | telemetry | ναι | κοινή μνήμη `Local\SCSTelemetry` που γράφει το RenCloud scs-sdk-plugin (έκδοση 12) στο `<game>\bin\win_x64\plugins` |
| [Assetto Corsa (ζωντανά δεδομένα)](game-assetto-corsa.md) | telemetry | ναι | κοινή μνήμη `Local\acpmf_physics`, `Local\acpmf_graphics`, `Local\acpmf_static` |
| [Assetto Corsa Competizione (ζωντανά δεδομένα)](game-assetto-corsa-competizione.md) | telemetry | ναι | κοινή μνήμη `Local\acpmf_physics`, `Local\acpmf_graphics`, `Local\acpmf_static` |
| [Assetto Corsa EVO (ζωντανά δεδομένα)](game-assetto-corsa-evo.md) | telemetry | ναι | κοινή μνήμη `Local\acevo_pmf_physics`, `Local\acevo_pmf_static` |
| [Assetto Corsa Rally (ζωντανά δεδομένα)](game-assetto-corsa-rally.md) | telemetry | ναι | κοινή μνήμη `Local\acpmf_physics`, `Local\acpmf_static` (ίδιες σελίδες με AC και ACC) |
| [Automobilista 2 (ζωντανά δεδομένα)](game-automobilista-2.md) | telemetry | ναι | κοινή μνήμη $pcars2$ (διάταξη SMS SharedMemory.h) |
| [BeamNG.drive (ζωντανά δεδομένα)](game-beamng.md) | telemetry | ναι | UDP 127.0.0.1:4460 από το mod πρωτοκόλλου heat3d (mods/beamng/heat3d σε αυτό το αποθετήριο) |
| [Counter-Strike 2 (replays)](game-cs2-demos.md) | replay | ναι | demos που αποθηκεύει το CS2: `<CS2>/game/csgo/replays/*.dem` (κατεβασμένα από το ιστορικό αγώνων) και `<CS2>/game/csgo/*.dem` (εγγεγραμμένα) |
| [Counter-Strike 2 (κατάσταση παιχνιδιού)](game-cs2-gsi.md) | gsi | ναι | Game State Integration: HTTP POST στο 127.0.0.1:3311, ρυθμισμένο από το `<CS2>\game\csgo\cfg\gamestate_integration_heat3d.cfg` |
| [DCS World (ζωντανά δεδομένα)](game-dcs.md) | telemetry | ναι | το hook του watcher `%USERPROFILE%\Saved` `Games\DCS*\Scripts\Hooks\heat3d-watch.lua`, γραμμές UDP στο 127.0.0.1:41993 |
| [DiRT Rally 2.0 (ζωντανά δεδομένα)](game-dirt-rally-2.md) | telemetry | ναι | UDP 127.0.0.1:20777, extradata=3 `(Documents\My` `Games\DiRT` Rally `2.0\hardwaresettings\hardware_settings_config.xml`)· όσο άλλη εφαρμογή κρατά την 20777, ο watcher αφήνει τη θύρα σε εκείνη |
| [Dota 2 (replays)](game-dota-replays.md) | replay | ναι | replays που αποθηκεύει το Dota 2: `<Dota>/game/dota/replays/<match id>.dem` (κατεβασμένα στον client, ή με `dota-replay <match id>`) |
| [Dota 2 (κατάσταση παιχνιδιού)](game-dota2-gsi.md) | gsi | ναι | Game State Integration: HTTP POST στο 127.0.0.1:3312, ρυθμισμένο από το `<Dota>\game\dota\cfg\gamestate_integration\gamestate_integration_heat3d.cfg` |
| [EA SPORTS F1 23 (ζωντανά δεδομένα)](game-f1-23.md) | telemetry | ναι | UDP telemetry 127.0.0.1:20777 `(Documents\My` `Games\F1` `23\hardwaresettings\hardware_settings_config.xml`) |
| [EA SPORTS F1 24 (ζωντανά δεδομένα)](game-f1-24.md) | telemetry | ναι | UDP telemetry 127.0.0.1:20777 `(Documents\My` `Games\F1` `24\hardwaresettings\hardware_settings_config.xml`) |
| [EA SPORTS F1 25 (ζωντανά δεδομένα)](game-f1-25.md) | telemetry | ναι | UDP telemetry 127.0.0.1:20777 `(Documents\My` `Games\F1` `25\hardwaresettings\hardware_settings_config.xml`) |
| [EA SPORTS WRC (ζωντανά δεδομένα)](game-ea-wrc.md) | telemetry | ναι | UDP 127.0.0.1:20777, το προεπιλεγμένο `wrc` structure του πακέτου session_update `(Documents\My` `Games\WRC\telemetry\config.json`)· όσο άλλη εφαρμογή κρατά την 20777, ο watcher αφήνει τη θύρα σε εκείνη |
| [Elite Dangerous (αρχεία καταγραφής)](game-elite.md) | log | ναι | Player Journal `%USERPROFILE%\Saved` `Games\Frontier` `Developments\Elite` `Dangerous\Journal.*.log` (το νεότερο αρχείο, παρακολουθείται καθώς γράφεται), Status.json και τα άλλα συνοδευτικά `*.json` (Market, Outfitting, Shipyard, NavRoute, Cargo, ModulesInfo, ShipLocker, Backpack, FCMaterials) στον ίδιο φάκελο |
| [Euro Truck Simulator 2 (ζωντανά δεδομένα)](game-ets2.md) | telemetry | ναι | κοινή μνήμη `Local\SCSTelemetry` που γράφει το RenCloud scs-sdk-plugin (έκδοση 12) στο `<game>\bin\win_x64\plugins` |
| [EVE Online (αρχεία καταγραφής)](game-eve.md) | log | όχι | `%USERPROFILE%\Documents\EVE\logs\Gamelogs\*.txt` και τα `Chatlogs\*.txt` δίπλα τους (κάθε αρχείο που γράφτηκε από την εκκίνηση του client) |
| [Forza Horizon 4 (ζωντανά δεδομένα)](game-forza-horizon-4.md) | telemetry | ναι | Forza Data Out, UDP 127.0.0.1:5300 (μορφή Dash)· κάθε πακέτο προωθείται αμετάβλητο στο 127.0.0.1:5301 |
| [Forza Horizon 5 (ζωντανά δεδομένα)](game-forza-horizon-5.md) | telemetry | ναι | Forza Data Out, UDP 127.0.0.1:5300 (μορφή Dash)· κάθε πακέτο προωθείται αμετάβλητο στο 127.0.0.1:5301 |
| [Forza Horizon 6 (ζωντανά δεδομένα)](game-forza-horizon-6.md) | telemetry | ναι | Forza Data Out, UDP 127.0.0.1:5300 (μορφή Dash)· κάθε πακέτο προωθείται αμετάβλητο στο 127.0.0.1:5301 |
| [Forza Motorsport (ζωντανά δεδομένα)](game-forza-motorsport.md) | telemetry | ναι | Forza Data Out, UDP 127.0.0.1:5300 (μορφή Dash)· κάθε πακέτο προωθείται αμετάβλητο στο 127.0.0.1:5301 |
| [Hearthstone (αρχεία καταγραφής)](game-hearthstone.md) | log | όχι | `<install>\Logs\Power.log` (ή `Logs\Hearthstone_*\Power.log`), που γράφεται μόλις το `%LOCALAPPDATA%\Blizzard\Hearthstone\log.config` έχει ενότητα [Power], και κάθε άλλο `*.log` που γράφει το παιχνίδι εκεί |
| [IL-2 Sturmovik: Great Battles (ζωντανά δεδομένα)](game-il2.md) | telemetry | όχι | η έξοδος telemetry UDP του παιχνιδιού στο 127.0.0.1:41995 ([KEY = telemetrydevice] στο `<game>\data\startup.cfg`) |
| [IL-2 Sturmovik: Great Battles (replays)](game-il2-tacview.md) | replay | ναι | οι δικές του εγγραφές Tacview του παιχνιδιού `<game>\data\Tracks\*.acmi` (ACMI 2.x κείμενο, απλό ή συμπιεσμένο) |
| [iRacing (ζωντανά δεδομένα)](game-iracing.md) | telemetry | όχι | κοινή μνήμη `Local\IRSDKMemMapFileName` (το SDK του iRacing)· αρχεία .ibt στο `%USERPROFILE%\Documents\iRacing\telemetry` |
| [League of Legends (κατάσταση παιχνιδιού)](game-lol-live.md) | gsi | όχι | Live Client Data API του client του παιχνιδιού, <https://127.0.0.1:2999/liveclientdata/> (allgamedata, eventdata), κατά τη διάρκεια αγώνα |
| [League of Legends (replays)](game-lol-replays.md) | replay | ναι | replays που αποθηκεύει ο client του League: %USERPROFILE%/Documents/League of `Legends/Replays/*.rofl` (μόνο τα απλά μεταδεδομένα τέλους αγώνα)· με δικό σας κλειδί API της Riot, η επίσημη χρονολογία του αγώνα από το Match-V5 API της Riot |
| [Microsoft Flight Simulator 2020 (ζωντανά δεδομένα)](game-msfs2020.md) | telemetry | ναι | SimConnect μέσω του δικού σας SimConnect.dll (ο φάκελος του προσομοιωτή, ή `%MSFS_SDK%\SimConnect` `SDK\lib`) |
| [Microsoft Flight Simulator 2024 (ζωντανά δεδομένα)](game-msfs2024.md) | telemetry | ναι | SimConnect μέσω του δικού σας SimConnect.dll (ο φάκελος του προσομοιωτή, ή `%MSFS2024_SDK%\SimConnect` `SDK\lib`) |
| [Minecraft (αρχεία καταγραφής)](game-minecraft.md) | log | ναι | `%APPDATA%\.minecraft\logs\latest.log` (παρακολουθείται), `saves\<world>\stats\<uuid>.json` και `saves\<world>\playerdata\<uuid>.dat` / level.dat (NBT σε gzip), διαβάζονται όταν το παιχνίδι τα αποθηκεύει |
| [NVIDIA highlights (πλατφόρμα)](game-nvidia-highlights.md) | platform | δανεικές | `%LOCALAPPDATA%\NVIDIA` `Corporation\NVIDIA` `Overlay\UGCTracker.json`, GallerySettings.json, `Highlights\<game>\config.json`· τα κλιπ στον φάκελο λήψης `(%USERPROFILE%\Videos\NVIDIA\<Game>\*.mp4`) και `<temp>\Highlights\<game>`· `%LOCALAPPDATA%\NVIDIA` `Corporation\GfeSDK\<exe>_<pid>.log` |
| [osu! (replays)](game-osu-replays.md) | replay | ναι | replays του osu! (παλιά έκδοση) που αποθηκεύει: `%LOCALAPPDATA%/osu!/Data/r/*.osr` (κάθε παιχνίδι) και `osu!/Replays/*.osr` (εξαγμένα) |
| [Path of Exile (αρχεία καταγραφής)](game-poe.md) | log | όχι | `<install>\logs\Client.txt` του Path of Exile ή του Path of Exile 2 (παρακολουθείται· ο φάκελος εγκατάστασης είναι αυτός του εκτελούμενου εκτελέσιμου) |
| [Project CARS 2 (ζωντανά δεδομένα)](game-project-cars-2.md) | telemetry | ναι | κοινή μνήμη $pcars2$ (SMS SharedMemory.h) |
| [RaceRoom Racing Experience (ζωντανά δεδομένα)](game-raceroom.md) | telemetry | ναι | κοινή μνήμη $R3E (r3e.h της Sector3, έκδοση 3) |
| [Richard Burns Rally (ζωντανά δεδομένα)](game-richard-burns-rally.md) | telemetry | ναι | UDP telemetry του πρόσθετου NGP, 127.0.0.1:6776 (RichardBurnsRally.ini [NGP] udpTelemetry=1) |
| [Rocket League (κατάσταση παιχνιδιού)](game-rocketleague-stats.md) | gsi | ναι | Stats API: ροή JSON TCP από το 127.0.0.1:49123 (η θύρα είναι στο `<RL>\TAGame\Config\TAStatsAPI.ini` ή DefaultStatsAPI.ini) |
| [Squad (replays)](game-squad-demos.md) | replay | ναι | demos διακομιστή που καταγράφει το Squad με την εντολή διαχειριστή AdminDemoRec: `<server>/SquadGame/Saved/Demos/*.replay`, διαβάζονται από τον εξωτερικό αναγνώστη `heat3d-squad-demo` (exporters/ext/squad-demo) |
| [Star Citizen (αρχεία καταγραφής)](game-starcitizen.md) | log | όχι | `<install>\StarCitizen\LIVE\Game.log` (ο φάκελος της έκδοσης του εκτελούμενου StarCitizen.exe)· μόνο το αρχείο καταγραφής που γράφει το παιχνίδι - ένα παιχνίδι με Easy Anti-Cheat: τίποτα δεν αγγίζει τη διεργασία του |
| [Steam statistics (πλατφόρμα)](game-steam-stats.md) | platform | όχι | η τοπική μνήμη στατιστικών του Steam `%STEAM%\appcache\stats\UserGameStats_<account>_<appid>.bin` με `UserGameStatsSchema_<appid>.bin`· ο χρόνος παιξίματος από το `%STEAM%\userdata\<account>\config\localconfig.vdf` (%STEAM% από το `HKCU\Software\Valve\Steam` SteamPath) |
| [Steam Timeline (πλατφόρμα)](game-steam-timeline.md) | platform | όχι | `%STEAM%\userdata\<account>\gamerecordings\timelines\timeline_<appid><date>_<time>.json` |
| [VALORANT (replays)](game-valorant-replays.md) | replay | όχι | replays που αποθηκεύει το VALORANT: `%LOCALAPPDATA%/VALORANT/Saved/Demos/*.vrf` (μόνο τα μέρη που δεν είναι θολωμένα) |
| [War Thunder (replays)](game-warthunder-replays.md) | replay | ναι | replays που αποθηκεύει το War Thunder: `<War Thunder>/Replays/*.wrpl` (με ενεργή αποθήκευση replay), μετατρέπονται από τον εξωτερικό μετατροπέα `heat3d-wt-replay` (exporters/ext/warthunder-replay) |
| [War Thunder (κατάσταση παιχνιδιού)](game-warthunder-webmap.md) | gsi | ναι | το τοπικό web map του παιχνιδιού, <http://127.0.0.1:8111> (/map_info.json, /map_obj.json, /state, /indicators, /hudmsg, /gamechat, /mission.json, /map.img) |
| [World of Tanks (replays)](game-wot-replays.md) | replay | ναι | replays που αποθηκεύει το World of Tanks: `<World of Tanks>/replays/*.wotreplay` (με ενεργή καταγραφή μάχης), μετατρέπονται από τον εξωτερικό μετατροπέα `heat3d-wot-replay` (exporters/ext/wot-replay) |
| [World of Warships (replays)](game-wows-replays.md) | replay | ναι | replays που αποθηκεύει το World of Warships: `<World of Warships>/replays/*.wowsreplay` (με ενεργά replays), μετατρέπονται από τον εξωτερικό μετατροπέα `heat3d-wows-replay` (exporters/ext/wows-replay) |
| [X-Plane (ζωντανά δεδομένα)](game-xplane.md) | telemetry | ναι | η διεπαφή UDP του X-Plane στο 127.0.0.1:49000 (RREF datarefs και RPOS θέση, που απαντά στον watcher) |

Παιχνίδια που δεν καταγράφονται, και γιατί: [Sources and rules](sources-and-rules.md#what-is-declined-and-why). Όλα σε έναν πίνακα, όπως τα τυπώνει το `python -m heat3d_watch games --markdown`: [All games in one table](watcher.md).

<!-- Generated by tools/gen_game_pages.py; run it again after changing an adapter. -->
