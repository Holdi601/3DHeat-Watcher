---
title: "DCS World (canlı veri)"
nav_order: 10
lang: "tr"
source: game-dcs.md
source_hash: "87cba160674e"
nav_exclude: true
search_exclude: true
---
# DCS World (canlı veri) {#dcs-world-live-data}

DCS World oynarken izleyici, oyunun kendi gönderdiği veriyi kaydeder. Böylece bunlara daha sonra 3DHeat görüntüleyicisinde bir harita üzerinde bakabilirsiniz.

*Teknik ayrıntılar: adaptör `dcs`, tür [`telemetry`](sources-and-rules.md); `DCS.exe` çalışırken çalışır ve her 0.1 s'de bir yeni veri arar.*

## Neler kaydedilir {#what-is-recorded}

- kendi konumu 10 Hz'de, sahnenin başlangıç noktasından metre cinsinden doğu/yukarı/kuzey olarak (enlem/boylam/yükseklikten); enlem/boylam/yükseklik ve DCS'nin kendi dünya metreleri (dcs_x kuzey, dcs_y yukarı, dcs_z doğu) sütun olarak
- tutum, gösterilen ve gerçek hava hızı, Mach, dikey hız, hücum açısı ve kayma, manyetik baş, AGL ve radar yüksekliği, üç eksende g, hız ve dönüş hızları, havada olup olmadığı, kameranın konumu ve ileri vektörü, uçak tipi
- hava alanıyla birlikte kalkışlar ve inişler; kazalar, koltuktan fırlamalar, pilot ölümleri
- her iki birim tipi ve silahla birlikte öldürmeler ve düşürülmeler; diğer oyun olayları verildiği gibi
- görev başına yaşamlar (doğuş ... oturum sonu), öldürmeler, ölümler, mesafe, en yüksek irtifa, en yüksek g
- kancanın gönderdiği her satır bütün olarak heat.raw.parquet içinde, ayrıca uçağın dışa aktarma tablolarının (motorlar, iniş takımı ve kanatçıklar, yük, karşı önlemler, rota, seyrüsefer) saniyede bir dökümü ve diğer her geri çağrı (duraklatma, sohbet, oyuncuların katılması, görev yüklenmesi)

## Nereden gelir {#where-it-comes-from}

izleyicinin kancası %USERPROFILE%\Saved Games\DCS\*\Scripts\Hooks\heat3d-watch.lua, 127.0.0.1:41993 adresine UDP satırları

## Nasıl açılır {#how-to-switch-it-on}

python -m heat3d_watch setup dcs --apply (Scripts\Hooks\heat3d-watch.lua dosyasını ekler), ardından DCS'yi yeniden başlatın

Komutu, izleyicinin klasöründe açılmış bir terminale yazın (bkz. [Başlamadan önce](before-you-start.md)). Başarısız olursa son satır nedenini söyler; [Kurulum ve çalıştırma](installing-and-running.md) sık görülen nedenleri anlatır.

`python -m heat3d_watch setup dcs` hangi dosyaları değiştireceğini listeler; `python -m heat3d_watch setup dcs --apply` bunları değiştirir ve özgün dosyayı `<file>.heat3d-backup` adıyla saklar (bkz. [Komutlar](commands.md#setup)). Her değişiklik için `dcs: changed: ...` yazar, zaten açıksa `dcs: nothing to change` yazar.

## Nasıl çalışır {#how-it-works}

DCS World: izleyicinin kendi küçük kanca betiği; 127.0.0.1:41993 adresine UDP satırları gönderir.

DCS, başlarken `Saved Games\DCS*\Scripts\Hooks\` içindeki Lua dosyalarını çalıştırır; bir kanca, dışa aktarma işlevlerini (`Export.Lo*`) okuyabilir ve simülasyonun geri çağrılarını alabilir (`DCS.setUserCallbacks`: onSimulationStart/Frame/Stop, onGameEvent) - bkz. `<DCS>\API\DCS_ControlAPI.html` ve <https://wiki.hoggitworld.com/view/DCS_Export_Script>.
`setup` orada `heat3d-watch.lua` dosyasını yazar (kendi dosyası: Export.lua ve diğer araçların kancalarına dokunulmaz). Bu dosya saniyede on satır, bir satır da saniyede bir ve her oyun olayı ya da geri çağrı için bir satır gönderir; hiçbir zaman cevap beklemez. Port 41993'tür; böylece JoyPro'nun kancası (41992) ve Tacview (42674) yanında çalışmaya devam eder. Satırlar (alanlar ';' ile ayrılır):

```text
hello;v=2                                       the hook was loaded
start;mission=..;map=..;me=<player id>;name=..;mp=0|1;file=..;server=0|1
mis;t=..;date.Day=..;start_time=..;weather...   the mission's date, start time and weather, flattened
p;t=<model s>;x=;y=;z=;lat=;lon=;alt=;hdg=;pitch=;bank=;ias=;agl=;g=;type=;tas=;mach=;vv=;aoa=;aos=;
  mhdg=;ralt=;gx=;gz=;vx=;vy=;vz=;wx=;wy=;wz=;air=;cx=;cy=;cz=;cfx=;cfy=;cfz=
d;t=..;self.Name=..;eng.RPM.left=..;mech.gear.value=..;pay.Stations.1.count=..;...   once a second
ev;t=..;name=<onGameEvent name>;args=a|b|c      every onGameEvent
cb;t=..;name=<callback>;args=a|b                every other callback (pause, chat, players, loading)
noexport;t=..                                   the server forbids ownship export
stop;t=..                                       the mission ended
```

`p`, LoGetSelfData'dır: Position x/y/z - DCS'nin kendi dünya metreleri, x kuzey, y yukarı, z doğu - ayrıca LatLongAlt (derece, m), Heading/Pitch/Bank (radyan), LoGetIndicatedAirSpeed (m/s), LoGetAltitudeAboveGroundLevel (m) ve LoGetAccelerationUnits() x/y/z (g) ile; ve `Scripts\Export.lua`'nın belgelediği gibi LoGetTrueAirSpeed (m/s), LoGetMachNumber, LoGetVerticalVelocity (m/s), LoGetAngleOfAttack ve LoGetAngleOfSideSlip (rad), LoGetMagneticYaw (rad), LoGetRadarAltimeter (m), LoGetVectorVelocity (dünya m/s), LoGetAngularVelocity (rad/s), LoGetInAir ve LoGetCameraPosition'ın noktası ve ileri vektörü (dünya metreleri). `d` tabloların saniyede bir dökümüdür, noktalı anahtarlara düzleştirilmiş: LoGetSelfData (ülke, koalisyon, birim ve grup adları, tip seviyeleri, bayraklar), LoGetEngineInfo, LoGetMechInfo, LoGetPayloadInfo, LoGetSnares, LoGetWingInfo, LoGetVectorWindVelocity, LoGetFMData, LoGetNavigationInfo, LoGetRoute, LoGetMCPState, LoGetControlPanel_HSI, LoGetRadioBeaconsStatus ve birkaç sayı (duraklatma, zaman hızlandırması, koltuk, basınç, sapmalar). İzleyici her satırı ham arşivde bütün olarak tutar; `p` ayrıca satırlara dönüşür.

Konumlar, öteki uçuş simülatörlerininkiyle aynı düz haritaya girer (`Tangent`: x doğu, y deniz seviyesinin üstündeki yükseklik, z kuzey, metre cinsinden), LatLongAlt'tan, sahnenin sabit başlangıç noktası etrafında (`THEATRES`, başlangıç satırının `map` alanından). Böylece aynı sahnedeki her görev tek bir harita paylaşır ve görüntüleyici gerçek dünyayı altına yerleştirebilir. Tabloda olmayan bir sahne, ilk konumun enlem ve boylamını tam dereceye yuvarlar. DCS'nin kendi x/y/z değerleri `dcs_x`, `dcs_y`, `dcs_z` olarak saklanır; LatLongAlt'ı olmayan bir konum yerleştirilemez ve yalnızca sayılır (`fixes_without_latlon`). Başlangıç noktası oturumun `geo` değeridir; meta.json ve tablonun altbilgisinde durur.

onGameEvent'in argümanları, DCS_ControlAPI'nin verdiği gibi: takeoff/landing (playerID, unit_missionID, airdromeName), crash/eject/pilot_death (playerID, unit_missionID), kill (killerPlayerID, killerUnitType, killerSide, victimPlayerID, victimUnitType, victimSide, weaponName), self_kill (playerID), change_slot (playerID, slotID, prevSide), mission_end (winner, msg).

Çok oyunculu bir sunucu, kendi uçağının dışa aktarılmasını yasaklayabilir (LoIsOwnshipExportAllowed false döner); o zaman konum yoktur, yalnızca olaylar vardır ve oturum bunu söyler.

## Konumlar ve eksenler {#positions-and-axes}

| | |
|---|---|
| Konumlar kaydedilir | evet |
| Yukarı eksen | `y` |
| Birimler | metre (doğu, yükseklik, kuzey; sahnenin başlangıç noktasından) |
| Görüntüleyici için aynalanır | `z` |
| Birim ölçeği (`scale`: görüntüleyici konumları bununla çarpar) | 1 |

Bunlar her oturumun `meta.json` dosyasına (`axes`) ve oturumda konum varsa `heat.parquet` dosyasının altbilgisine yazılır; böylece 3DHeat görüntüleyicisi satırları kendi başına döndürür ve ölçekler - bkz. [Veriler](the-data.md).

## Çok oyunculu {#multiplayer}

- Çevrimiçi oynanan olarak işaretli (`multiplayer`): **evet**. `games --markdown` bunu "allowed (reads only what the game publishes)" olarak gösterir.
- Tür `telemetry`: yalnızca oyunun ya da platformun verdiğini okur (oyunun yayımladığı bir UDP portu ya da paylaşılan bellek), bu yüzden çevrimiçi oyunda da, çevrimdışı olduğu gibi kaydeder; bayrak yalnızca belleğin hiç okunup okunamayacağını belirler.
- Bellek: bu adaptör **asla** okumaz. Yalnızca `memory` adaptörleri bellek okur ve çevrimiçi oynanan bir oyun için asla okumaz - bkz. [Kaynaklar ve kurallar](sources-and-rules.md).

## Kaydedilen istatistikler {#statistics-recorded}

Bu adaptörün kodunun adıyla ayarladığı istatistik anahtarları (her oturumun `meta.json` içindeki `stats` ve `watcher.sqlite` içindeki `stats` tablosu):

`airborne_time`, `bad_packets`, `crashes`, `deaths`, `distance_km`, `ejections`, `export_blocked`, `fixes_without_latlon`, `flight_time`, `kills`, `max_altitude_m`, `max_g`, `shot_down`, `{event}s`

Süslü parantez içindeki bir anahtar çalışma sırasında tamamlanır (`score.{team}` her takım için bir anahtardır). Kodun oyunun alan tablosundan ya da oyunun kendi istatistik adlarından aldığı anahtarlar bu listede yoktur; yukarıdaki "Neler kaydedilir" bölümü onları adlarıyla anar.

## Tamlık {#completeness}

İzleyici, 3DHeat'in [dönüştürücü kuralını](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md) izler: kaynağın tuttuğu okunur ya da saklanır, asla atılmaz. Satırların yanında, adaptörün aldığı her paket, sayfa, satır ya da yanıt, oturumun `heat.raw.parquet` dosyasında bütün olarak saklanır (sütunlar `time`, `ms`, `type`, `used`, `payload`, `text`, ardından adıyla saklanan her alan; `used` satırlara dönüşenleri işaretler). `meta.json` içindeki `selfCheck.completeness` her `type` değerini sayar - `lost` 0'dır.

**Okunanlar**

- `p` (10 Hz): konum, LatLongAlt, tutum, IAS, AGL, g (x/y/z), uçak tipi ve kanca 2'nin TAS, Mach, dikey hız, AoA, kayma, manyetik baş, radar yüksekliği, dünya hızı, dönüş hızları, havada olma ve kamera noktası/ileri vektörü - hepsi satır sütunu olarak (birimler Export.lua'nın verdiği gibi)
- `start`: görev, sahne, kendi oyuncu kimliği ve adı, çok oyunculu olup olmadığı, görev dosyası, sunucu; `mis`: görevin tarihi ve başlangıç saati meta.json'a
- `ev`: her onGameEvent bir satır olarak (takeoff, landing, crash, eject, pilot_death, kill, self_kill, change_slot, connect, disconnect, friendly_fire, mission_end, verilen başka her ad)
- `noexport` ve `stop`: satır olarak ve meta.json'da

**Ham olarak saklananlar**

- kancanın gönderdiği her satır, bütün olarak, türü altında `text` olarak: `hello`, `start`, `mis`, `p`, `d`, `ev`, `cb`, `noexport`, `stop`; başka türde bir satır `unknown` altında
- `d` (saniyede 1, yalnızca ham): LoGetSelfData bütün olarak (ülke, koalisyon, birim ve grup adı, tip seviyeleri, bayraklar), LoGetEngineInfo, LoGetMechInfo, LoGetPayloadInfo, LoGetSnares, LoGetWingInfo, rüzgâr vektörü, LoGetFMData, LoGetNavigationInfo, LoGetRoute, LoGetMCPState, HSI, radyo işaretçileri, duraklatma, zaman hızlandırması, koltuk, basınç, sapmalar - noktalı anahtarlara düzleştirilmiş
- `mis`: görevin hava durumu tablosu, düzleştirilmiş; `cb`: onSimulationPause/Resume, onMissionLoad\*, onNet\*, onPlayerConnect/Disconnect/Start/Stop/ChangeSlot, onChatMessage, onTriggerMessage, onRadioMessage, onRadioCommand, onShowMessage, argümanlarıyla birlikte

**Mevcut değil**

- diğer birimler (LoGetWorldObjects, LoGetObjectById) ve sensör verisi (LoGetTargetInformation, LoGetLockedTargetInformation, LoGetTWSInfo, LoGetWingTargets, LoGetSightingSystemInfo): istenmez - bir görevin her nesnesini saniyede 10 kez almak DCS'nin kendi çerçevesi içinde pahalıdır ve bir sunucu bunları kapatır (allow_object_export, allow_sensor_export); Tacview bunları kaydeder
- görevin bütün tablosu (DCS.getCurrentMission her birimi ve tetikleyiciyi, megabaytlarca veri içerir): yalnızca tarihi, başlangıç saati, hava durumu, sortie, sahne ve sürüm gönderilir
- `onPlayerTry*` geri çağrıları: DCS'ye izin verir ya da reddeder, bu yüzden kanca onlara dokunmaz
- diğer oyuncuların adresleri ve UCID'leri: net.get_player_info bunları yalnızca bir sunucuya verir ve bunlar oyuncunun saklayacağı şeyler değildir
- bir `d` satırındaki bir tablonun 800 anahtarı ya da 6 seviyeyi aşan girdileri kesilir; böylece bir satır bir datagram olarak kalır

**Boyut**: `p` satırlarından saatte yaklaşık 20 MB (saniyede 10, çerçevesiyle birlikte satır başına yaklaşık 500 bayt) ve `d` dökümlerinden 15-40 MB (saniyede bir, uçağın yüküne ve rotasına göre 4-10 KB), zstd öncesi; tekrarlanan anahtarlar yaklaşık on kat sıkışır

## Doğrulama {#verified}

satır biçimi sentetik datagramlarla test edildi; Lua kancası DCS içinde test edilmedi (DCS kanca/dışa aktarma API'sinden ve Scripts\Export.lua'nın Lo* işlevleri listesinden yazıldı, çalıştırılmadı)

## Kaynak {#source}

[heat3d_watch/adapters/dcs.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/dcs.py)

<!-- Generated from the adapter by tools/gen_game_pages.py; change the adapter and run it again rather than editing this page. -->
