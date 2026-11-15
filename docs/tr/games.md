---
title: "Oyunlar"
nav_order: 4
lang: "tr"
source: games.md
source_hash: "c601550fbb4e"
nav_exclude: true
search_exclude: true
---
# Oyunlar {#games}

İzleyici 44 oyun ve platformda 49 kaynağı tanır. Her birinin kendi sayfası vardır; bu sayfa adaptörün kodundan üretilir: neyi kaydettiği, nereden aldığı, nasıl açıldığı, nasıl çalıştığı, eksenleri ve neyin doğrulandığı.

Türler: `telemetry`, `gsi`, `log`, `replay` ve `platform` - bkz. [Kaynaklar ve kurallar](sources-and-rules.md). Konumlar: *evet*, adaptör yer bilgisi olan satırlar yazdığında; *ödünç alınmış*, aynı oyunun başka bir kaydından yer aldığında (bkz. [NVIDIA Highlights](nvidia-highlights.md)); *hayır*, kaynakta hiç konum yoksa. Bellek profilleri listelenmez: hiçbiri gönderilmez, her oyuncu kendi profilini yazar (bkz. [Bellek okuma](memory-reading.md)).

| Oyun | Tür | Konumlar | Kaynak |
|---|---|---|---|
| [American Truck Simulator (canlı veri)](game-ats.md) | telemetry | evet | paylaşılan bellek `Local\SCSTelemetry`, RenCloud scs-sdk-plugin (revizyon 12) tarafından `<game>\bin\win_x64\plugins` içinde yazılır |
| [Assetto Corsa (canlı veri)](game-assetto-corsa.md) | telemetry | evet | paylaşılan bellek `Local\acpmf_physics`, `Local\acpmf_graphics`, `Local\acpmf_static` |
| [Assetto Corsa Competizione (canlı veri)](game-assetto-corsa-competizione.md) | telemetry | evet | paylaşılan bellek `Local\acpmf_physics`, `Local\acpmf_graphics`, `Local\acpmf_static` |
| [Assetto Corsa EVO (canlı veri)](game-assetto-corsa-evo.md) | telemetry | evet | paylaşılan bellek `Local\acevo_pmf_physics`, `Local\acevo_pmf_static` |
| [Assetto Corsa Rally (canlı veri)](game-assetto-corsa-rally.md) | telemetry | evet | paylaşılan bellek `Local\acpmf_physics`, `Local\acpmf_static` (AC ve ACC ile aynı sayfalar) |
| [Automobilista 2 (canlı veri)](game-automobilista-2.md) | telemetry | evet | paylaşılan bellek $pcars2$ (SMS SharedMemory.h düzeni) |
| [BeamNG.drive (canlı veri)](game-beamng.md) | telemetry | evet | 127.0.0.1:4460 üzerinden UDP, heat3d protokol modundan (bu depoda mods/beamng/heat3d) |
| [Counter-Strike 2 (tekrarlar)](game-cs2-demos.md) | replay | evet | CS2'nin kaydettiği demolar: `<CS2>/game/csgo/replays/*.dem` (maç geçmişinden indirilen) ve `<CS2>/game/csgo/*.dem` (kaydedilen) |
| [Counter-Strike 2 (oyun durumu)](game-cs2-gsi.md) | gsi | evet | Oyun Durumu Entegrasyonu: `<CS2>\game\csgo\cfg\gamestate_integration_heat3d.cfg` ile ayarlanan 127.0.0.1:3311 adresine HTTP POST istekleri |
| [DCS World (canlı veri)](game-dcs.md) | telemetry | evet | izleyicinin kancası `%USERPROFILE%\Saved` `Games\DCS*\Scripts\Hooks\heat3d-watch.lua`, 127.0.0.1:41993 adresine UDP satırları |
| [DiRT Rally 2.0 (canlı veri)](game-dirt-rally-2.md) | telemetry | evet | 127.0.0.1:20777 üzerinden UDP, extradata=3 `(Documents\My` `Games\DiRT` Rally `2.0\hardwaresettings\hardware_settings_config.xml`); başka bir uygulama 20777'yi tutuyorsa izleyici portu ona bırakır |
| [Dota 2 (tekrarlar)](game-dota-replays.md) | replay | evet | Dota 2'nin kaydettiği tekrarlar: `<Dota>/game/dota/replays/<match id>.dem` (istemcide indirilen ya da `dota-replay <match id>` ile) |
| [Dota 2 (oyun durumu)](game-dota2-gsi.md) | gsi | evet | Oyun Durumu Entegrasyonu: `<Dota>\game\dota\cfg\gamestate_integration\gamestate_integration_heat3d.cfg` ile ayarlanan 127.0.0.1:3312 adresine HTTP POST istekleri |
| [EA SPORTS F1 23 (canlı veri)](game-f1-23.md) | telemetry | evet | 127.0.0.1:20777 üzerinden UDP telemetrisi `(Documents\My` `Games\F1` `23\hardwaresettings\hardware_settings_config.xml`) |
| [EA SPORTS F1 24 (canlı veri)](game-f1-24.md) | telemetry | evet | 127.0.0.1:20777 üzerinden UDP telemetrisi `(Documents\My` `Games\F1` `24\hardwaresettings\hardware_settings_config.xml`) |
| [EA SPORTS F1 25 (canlı veri)](game-f1-25.md) | telemetry | evet | 127.0.0.1:20777 üzerinden UDP telemetrisi `(Documents\My` `Games\F1` `25\hardwaresettings\hardware_settings_config.xml`) |
| [EA SPORTS WRC (canlı veri)](game-ea-wrc.md) | telemetry | evet | 127.0.0.1:20777 üzerinden UDP, varsayılan `wrc` yapısının session_update paketi `(Documents\My` `Games\WRC\telemetry\config.json`); başka bir uygulama 20777'yi tutuyorsa izleyici portu ona bırakır |
| [Elite Dangerous (günlük dosyaları)](game-elite.md) | log | evet | Oyuncu Günlüğü `%USERPROFILE%\Saved` `Games\Frontier` `Developments\Elite` `Dangerous\Journal.*.log` (en yeni dosya, yazıldıkça izlenir), Status.json ve aynı klasördeki diğer yardımcı `*.json` dosyaları (Market, Outfitting, Shipyard, NavRoute, Cargo, ModulesInfo, ShipLocker, Backpack, FCMaterials) |
| [Euro Truck Simulator 2 (canlı veri)](game-ets2.md) | telemetry | evet | paylaşılan bellek `Local\SCSTelemetry`, RenCloud scs-sdk-plugin (revizyon 12) tarafından `<game>\bin\win_x64\plugins` içinde yazılır |
| [EVE Online (günlük dosyaları)](game-eve.md) | log | hayır | `%USERPROFILE%\Documents\EVE\logs\Gamelogs\*.txt` ve bunların yanındaki `Chatlogs\*.txt` (istemci başladığından beri yazılan her dosya) |
| [Forza Horizon 4 (canlı veri)](game-forza-horizon-4.md) | telemetry | evet | Forza Data Out, 127.0.0.1:5300 üzerinden UDP (Dash biçimi); her paket değiştirilmeden 127.0.0.1:5301 adresine aktarılır |
| [Forza Horizon 5 (canlı veri)](game-forza-horizon-5.md) | telemetry | evet | Forza Data Out, 127.0.0.1:5300 üzerinden UDP (Dash biçimi); her paket değiştirilmeden 127.0.0.1:5301 adresine aktarılır |
| [Forza Horizon 6 (canlı veri)](game-forza-horizon-6.md) | telemetry | evet | Forza Data Out, 127.0.0.1:5300 üzerinden UDP (Dash biçimi); her paket değiştirilmeden 127.0.0.1:5301 adresine aktarılır |
| [Forza Motorsport (canlı veri)](game-forza-motorsport.md) | telemetry | evet | Forza Data Out, 127.0.0.1:5300 üzerinden UDP (Dash biçimi); her paket değiştirilmeden 127.0.0.1:5301 adresine aktarılır |
| [Hearthstone (günlük dosyaları)](game-hearthstone.md) | log | hayır | `<install>\Logs\Power.log` (ya da `Logs\Hearthstone_*\Power.log`), `%LOCALAPPDATA%\Blizzard\Hearthstone\log.config` içinde bir [Power] bölümü olunca yazılır, ve oyunun orada yazdığı diğer her `*.log` |
| [IL-2 Sturmovik: Great Battles (canlı veri)](game-il2.md) | telemetry | hayır | oyunun telemetri UDP çıktısı, 127.0.0.1:41995 adresine ([KEY = telemetrydevice] `<game>\data\startup.cfg` içinde) |
| [IL-2 Sturmovik: Great Battles (tekrarlar)](game-il2-tacview.md) | replay | evet | oyunun kendi Tacview kayıtları `<game>\data\Tracks\*.acmi` (ACMI 2.x metni, düz ya da sıkıştırılmış) |
| [iRacing (canlı veri)](game-iracing.md) | telemetry | hayır | paylaşılan bellek `Local\IRSDKMemMapFileName` (iRacing SDK); `%USERPROFILE%\Documents\iRacing\telemetry` içinde .ibt dosyaları |
| [League of Legends (oyun durumu)](game-lol-live.md) | gsi | hayır | oyun istemcisinin Canlı İstemci Verisi API'si, <https://127.0.0.1:2999/liveclientdata/> (allgamedata, eventdata), bir maç sırasında |
| [League of Legends (tekrarlar)](game-lol-replays.md) | replay | evet | League istemcisinin kaydettiği tekrarlar: %USERPROFILE%/Documents/League of `Legends/Replays/*.rofl` (yalnızca düz maç sonu bilgisi); kendi Riot API anahtarınızla, maçın Riot'un Match-V5 API'sinden resmi zaman çizelgesi |
| [Microsoft Flight Simulator 2020 (canlı veri)](game-msfs2020.md) | telemetry | evet | SimConnect, oyuncunun kendi SimConnect.dll dosyası üzerinden (simülatörün klasörü ya da `%MSFS_SDK%\SimConnect` `SDK\lib`) |
| [Microsoft Flight Simulator 2024 (canlı veri)](game-msfs2024.md) | telemetry | evet | SimConnect, oyuncunun kendi SimConnect.dll dosyası üzerinden (simülatörün klasörü ya da `%MSFS2024_SDK%\SimConnect` `SDK\lib`) |
| [Minecraft (günlük dosyaları)](game-minecraft.md) | log | evet | `%APPDATA%\.minecraft\logs\latest.log` (izlenir), `saves\<world>\stats\<uuid>.json` ve `saves\<world>\playerdata\<uuid>.dat` / level.dat (gzip NBT); oyun kaydettiğinde okunur |
| [NVIDIA highlights (platform)](game-nvidia-highlights.md) | platform | ödünç alınmış | `%LOCALAPPDATA%\NVIDIA` `Corporation\NVIDIA` `Overlay\UGCTracker.json`, GallerySettings.json, `Highlights\<game>\config.json`; kliplerin yakalama klasöründe `(%USERPROFILE%\Videos\NVIDIA\<Game>\*.mp4`) ve `<temp>\Highlights\<game>`; `%LOCALAPPDATA%\NVIDIA` `Corporation\GfeSDK\<exe>_<pid>.log` |
| [Path of Exile (günlük dosyaları)](game-poe.md) | log | hayır | Path of Exile ya da Path of Exile 2'nin `<install>\logs\Client.txt` dosyası (izlenir; kurulum klasörü, çalışan çalıştırılabilir dosyanın klasörüdür) |
| [Project CARS 2 (canlı veri)](game-project-cars-2.md) | telemetry | evet | paylaşılan bellek $pcars2$ (SMS SharedMemory.h) |
| [RaceRoom Racing Experience (canlı veri)](game-raceroom.md) | telemetry | evet | paylaşılan bellek $R3E (Sector3'ün r3e.h dosyası, sürüm 3) |
| [Richard Burns Rally (canlı veri)](game-richard-burns-rally.md) | telemetry | evet | NGP eklentisinin UDP telemetrisi, 127.0.0.1:6776 (RichardBurnsRally.ini [NGP] udpTelemetry=1) |
| [Rocket League (oyun durumu)](game-rocketleague-stats.md) | gsi | evet | İstatistik API'si: 127.0.0.1:49123 adresinden TCP JSON akışı (port `<RL>\TAGame\Config\TAStatsAPI.ini` ya da DefaultStatsAPI.ini içinde) |
| [Squad (tekrarlar)](game-squad-demos.md) | replay | evet | Squad'ın yönetici komutu AdminDemoRec ile kaydettiği sunucu demoları: `<server>/SquadGame/Saved/Demos/*.replay`, harici okuyucu `heat3d-squad-demo` (exporters/ext/squad-demo) tarafından okunur |
| [Star Citizen (günlük dosyaları)](game-starcitizen.md) | log | hayır | `<install>\StarCitizen\LIVE\Game.log` (çalışan StarCitizen.exe'nin derleme klasörü), yalnızca oyunun yazdığı günlük dosyası - Easy Anti-Cheat'li bir oyun: hiçbir şey oyunun sürecine dokunmaz |
| [Steam istatistikleri (platform)](game-steam-stats.md) | platform | hayır | Steam'in yerel istatistik önbelleği `%STEAM%\appcache\stats\UserGameStats_<account>_<appid>.bin`, `UserGameStatsSchema_<appid>.bin` ile; oynama süresi `%STEAM%\userdata\<account>\config\localconfig.vdf` içinden (%STEAM%, `HKCU\Software\Valve\Steam` SteamPath değerinden) |
| [Steam Timeline (platform)](game-steam-timeline.md) | platform | hayır | `%STEAM%\userdata\<account>\gamerecordings\timelines\timeline_<appid><date>_<time>.json` |
| [VALORANT (tekrarlar)](game-valorant-replays.md) | replay | hayır | VALORANT'ın kaydettiği tekrarlar: `%LOCALAPPDATA%/VALORANT/Saved/Demos/*.vrf` (yalnızca karartılmamış kısımlar) |
| [War Thunder (tekrarlar)](game-warthunder-replays.md) | replay | evet | War Thunder'ın kaydettiği tekrarlar: `<War Thunder>/Replays/*.wrpl` (tekrar kaydı açıkken), harici dönüştürücü `heat3d-wt-replay` (exporters/ext/warthunder-replay) tarafından dönüştürülür |
| [War Thunder (oyun durumu)](game-warthunder-webmap.md) | gsi | evet | oyunun yerel web haritası, <http://127.0.0.1:8111> (/map_info.json, /map_obj.json, /state, /indicators, /hudmsg, /gamechat, /mission.json, /map.img) |
| [World of Tanks (tekrarlar)](game-wot-replays.md) | replay | evet | World of Tanks'in kaydettiği tekrarlar: `<World of Tanks>/replays/*.wotreplay` (savaş kaydı açıkken), harici dönüştürücü `heat3d-wot-replay` (exporters/ext/wot-replay) tarafından dönüştürülür |
| [World of Warships (tekrarlar)](game-wows-replays.md) | replay | evet | World of Warships'in kaydettiği tekrarlar: `<World of Warships>/replays/*.wowsreplay` (tekrarlar açıkken), harici dönüştürücü `heat3d-wows-replay` (exporters/ext/wows-replay) tarafından dönüştürülür |
| [X-Plane (canlı veri)](game-xplane.md) | telemetry | evet | X-Plane'in 127.0.0.1:49000 üzerindeki UDP arayüzü (RREF datarefs ve RPOS konumu, izleyiciye yanıt verilerek) |

Kaydedilmeyen oyunlar ve nedenleri: [Kaynaklar ve kurallar](sources-and-rules.md#what-is-declined-and-why). `python -m heat3d_watch games --markdown` komutunun yazdığı gibi her şey tek bir tabloda: [Tüm oyunlar tek tabloda](watcher.md).

<!-- Generated by tools/gen_game_pages.py; run it again after changing an adapter. -->
