---
title: "Richard Burns Rally (canlı veri)"
nav_order: 38
lang: "tr"
source: game-richard-burns-rally.md
source_hash: "4f2a2e46f8c8"
nav_exclude: true
search_exclude: true
---
# Richard Burns Rally (canlı veri) {#richard-burns-rally-live-data}

Richard Burns Rally oynarken izleyici, oyunun kendi gönderdiği verileri kaydeder; böylece bu verilere daha sonra 3DHeat görüntüleyicisinde bir harita üzerinde bakabilirsiniz.

*Teknik ayrıntılar: bağdaştırıcı `richard-burns-rally`, tür [`telemetry`](sources-and-rules.md); `RichardBurnsRally_SSE.exe` ya da `RichardBurnsRally.exe` çalışırken çalışır ve yeni veri için her 0,1 saniyede bir bakar.*

## Ne kaydedilir {#what-is-recorded}

- kendi arabanızın konumu (dünya XYZ, m), 10 Hz ile, hız, vites, gaz, fren ve etap mesafesiyle birlikte
- etap başlangıcı (etap saatinin başlaması), etap bitişi ve etap süresiyle, yeniden başlatmalar
- ışınlanmalar (yola geri dönme): arabanın olduğu yer için `teleport`, arabanın şimdi olduğu yer için `spawn`
- etaplar, en iyi etap süresi, mesafe, en yüksek hız

## Kaynağı {#where-it-comes-from}

NGP eklentisinin UDP telemetrisi, 127.0.0.1:6776 (RichardBurnsRally.ini [NGP] udpTelemetry=1)

## Nasıl açılır {#how-to-switch-it-on}

RSF/NGP: RichardBurnsRally.ini içinde, [NGP] bölümünde udpTelemetry=1 yapın ve uç noktayı 127.0.0.1:6776 olarak ayarlayın

## Nasıl çalışır {#how-it-works}

Yarış oyunlarının kendi telemetrisi: Forza, Assetto Corsa oyunları, ralli oyunları ve BeamNG; rota, tur ve etap olarak kaydedilir.

Burada her oyun telemetrisini bilerek yayımlar; gösterge panelleri ve hareket düzenekleri için. Hiçbir şey enjekte edilmez, oyunun dışarı vermediği hiçbir şey de okunmaz. Çözümleme iki kez yazılmaz: 3DHeat GameCapture'ın `heat3d_capture/telemetry` içindeki tur kayıt cihazları `heat3d_watch/decoders` içine kopyalanmıştır (orada, yayımlanmış düzenlerden üretilen paketlerle test edilmiştir). Bu modül onların karelerini izleyicinin satırlarına çevirir: arabanın konumu saniyede birkaç kez, hız, vites ve pedallarıyla; her tur ya da etap için bir olay; ve bir sürücünün tuttuğu sayılar: turlar, en iyi tur, mesafe, en yüksek hız.

#### Forza (Horizon 4/5/6, Motorsport) {#forza-horizon-456-motorsport}

Oyunun HUD ve Oynanış ayarlarında açılan "Data Out" UDP, 127.0.0.1 portuna, biçim Dash. Her simülasyon tikinde bir paket gelir; gösterge bloğunun ofseti paketlerden bulunur (`forza.detect_layout`). Dünya metre cinsindendir, Y yukarı; dünya sol elli bir koordinat sistemidir ve tur kayıt cihazının yaptığı gibi, gönderildiği şekliyle çizilir (Forza Motorsport ve Forza Horizon'un "Data Out" belgelerine göre).
Oyun tek bir porta gönderir; FH Companion ve diğer Data Out uygulamaları da aynı porta dinler. İki program bunu paylaşamaz: Windows'ta 127.0.0.1'e bağlanan soket paketleri alır, aynı porta tüm adreslere bağlanan soket ise hiç almaz; hangisi önce gelmişse. Bu yüzden izleyici, oyun başladıktan kısa bir süre sonra portu alır, portu tutan bir uygulamadan asla almaz ve orada dinlemeye başlayan başka bir uygulama açılır açılmaz portu bırakır. Portu tuttuğu sürece her paketi değiştirmeden 127.0.0.1:5301 adresine iletir - FH Companion'ın port kutusunu (telemetri sekmesi) 5301 yapın, ikisi de kaydeder.

#### EA SPORTS WRC, DiRT Rally 2.0, Richard Burns Rally {#ea-sports-wrc-dirt-rally-20-richard-burns-rally}

UDP: WRC'nin `Documents/My Games/WRC/telemetry/config.json` dosyası (`wrc` yapısının `session_update` paketi), DiRT'ün `hardware_settings_config.xml` dosyası (`<udp enabled="true" extradata="3" port="20777">`), RBR'nin NGP eklentisi (`udpTelemetry=1`, port 6776). Etaplar oyunun etap saatine göre ayrılır (`rally.StageSplitter`). RBR eksenlerini belgelemez: yukarı ekseni, sürüşte en az değişen eksendir ve oturum kapandığında belirlenir.

#### Her şey saklanır {#everything-kept}

Satırlar saniyede birkaç tanedir; oyunlar çok daha fazlasını gönderir. Ulaşan her UDP paketi - menülerde, turlar arasında, hiçbir çözücünün okumadığı paketler dahil - bütün olarak oturumun `heat.raw.parquet` dosyasında, kendi biçimi altında saklanır (`dash-horizon`, `session_update`, `extradata3`, `H3D1`, ...). Her paylaşılan bellek sayfası da değiştiğinde (yalnızca çözülen baytlar değil, bütün eşleme), eşleme adı altında saklanır (`acpmf_physics`, ...). `used` satıra dönüşenleri işaretler; `meta.json` içindeki `selfCheck.completeness` her türü sayar (3DHeat'in dönüştürücü kuralı).

Bu modülün sunduğu diğer sayfalar: [Assetto Corsa (canlı veri)](game-assetto-corsa.md), [Assetto Corsa Competizione (canlı veri)](game-assetto-corsa-competizione.md), [Assetto Corsa EVO (canlı veri)](game-assetto-corsa-evo.md), [Assetto Corsa Rally (canlı veri)](game-assetto-corsa-rally.md), [BeamNG.drive (canlı veri)](game-beamng.md), [DiRT Rally 2.0 (canlı veri)](game-dirt-rally-2.md), [EA SPORTS WRC (canlı veri)](game-ea-wrc.md), [Forza Horizon 4 (canlı veri)](game-forza-horizon-4.md), [Forza Horizon 5 (canlı veri)](game-forza-horizon-5.md), [Forza Horizon 6 (canlı veri)](game-forza-horizon-6.md), [Forza Motorsport (canlı veri)](game-forza-motorsport.md).

## Konumlar ve eksenler {#positions-and-axes}

| | |
|---|---|
| Kaydedilen konumlar | evet |
| Yukarı ekseni | `y` |
| Birimler | metre; yukarı ekseni sürüşten belirlenir (RBR eksenlerini belgelemez) |
| Görüntüleyici için aynalama | yok |
| Birim ölçeği (`scale`: görüntüleyici konumları bununla çarpar) | 1 |

Bunlar her oturumun `meta.json` dosyasındaki (`axes`) ve konum içeren oturumlarda `heat.parquet` dosyasının sonundaki (footer) bilgiye yazılır; böylece 3DHeat görüntüleyicisi satırları kendisi döndürür ve ölçekler - bkz. [Veriler](the-data.md).

## Çok oyunculu {#multiplayer}

- Çevrimiçi oynanan olarak işaretlenmiş (`multiplayer`): **hayır**. `games --markdown` bunu "tek oyunculu" olarak gösterir.
- Tür `telemetry`: yalnızca oyunun ya da platformun dışarı verdiğini okur (oyunun yayımladığı bir UDP portu ya da paylaşılan bellek). Bu yüzden çevrimiçi oyunda da çevrimdışı olduğu gibi kaydeder; bayrak yalnızca belleğin hiç okunup okunamayacağını belirler.
- Bellek: bu bağdaştırıcı **asla** okumaz. Yalnızca `memory` bağdaştırıcıları bellek okur ve çevrimiçi oynanan olarak işaretlenmiş bir oyun için asla okumaz - bkz. [Kaynaklar ve kurallar](sources-and-rules.md).

## Kaydedilen istatistikler {#statistics-recorded}

Bu bağdaştırıcının kodunun adla ayarladığı istatistik anahtarları (her oturumun `meta.json` içindeki `stats` ve `watcher.sqlite` içindeki `stats` tablosu):

`best_lap`, `best_stage`, `distance_km`, `laps`, `stages`, `top_speed_kmh`

Parantez içindeki bir anahtar çalışma zamanında tamamlanır (`score.{team}` her takım için bir anahtardır). Kodun oyunun alanlarının tablosundan ya da oyunun kendi istatistik adlarından aldığı anahtarlar bu listede yer almaz; yukarıdaki "Ne kaydedilir" bölümü bunları adlandırır.

## Tamlık {#completeness}

İzleyici 3DHeat'in [dönüştürücü kuralını](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md) izler: kaynağın tuttuğu her şey okunur ya da saklanır, asla atılmaz. Satırların yanı sıra, bağdaştırıcının aldığı her paket, sayfa, satır ya da yanıt, oturumun `heat.raw.parquet` dosyasında bütün olarak saklanır (sütunlar `time`, `ms`, `type`, `used`, `payload`, `text` ve adla saklanan her alan; `used` satıra dönüşenleri işaretler). `meta.json` içindeki `selfCheck.completeness` her `type` değerini sayar - `lost` 0'dır.

**Okunan**

- saniyede 10 satır: konum, hız, vites, gaz, fren, etap mesafesi, dönüş, rpm, direksiyon; etap başlangıcı, etap süresiyle bitiş, yeniden başlatmalar

**Ham olarak saklanan**

- porta ulaşan her paket, oyunun hızında bütün olarak, kendi biçimi altında: `telemetry` (NGP'nin 664 baytlık TelemetryData'sı), diğerleri için `rbr <n>-byte`
- satırların ötesinde pakette: tutum, arabanın kendi hızları ve ivmeleri, tekerlek başına yay sapması ve kuvveti, etabın ilerlemesi ve bitişe kalan mesafe; 664 baytın geri kalanı (motor, tekerlek ve fren blokları tekerlek başına) henüz hiçbir yerde çözülmez

**Kullanılamayanlar**

- diğer arabalar: oyunlar yalnızca oyuncunun arabasını gönderir
- hız birimi ve eksenleri: belgelenmemiştir - hız konumlardan alınır, yukarı sürüşten

**Boyut**: saniyede 60 paketle (664 bayt artı 70 baytlık öğe başlığı) saatte yaklaşık 160 MB; zstd bunun küçük bir kısmını tutar

## Doğrulama {#verified}

çözümleme gamecapture'ın tur kayıt cihazınındır (belgelenmiş düzenlerden üretilen paketlerle test edilmiştir); bağdaştırıcı, testte kurulan ve UDP ile gönderilen paketlerle test edilmiştir; oyunla test edilmemiştir

## Kaynak {#source}

[heat3d_watch/adapters/racing.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/racing.py)

<!-- Adaptörden tools/gen_game_pages.py ile üretilmiştir; sayfayı elle düzenlemek yerine adaptörü değiştirin ve yeniden çalıştırın. -->
