---
title: "DiRT Rally 2.0 (canlı veri)"
nav_order: 11
lang: "tr"
source: game-dirt-rally-2.md
source_hash: "367131ff990b"
nav_exclude: true
search_exclude: true
---
# DiRT Rally 2.0 (canlı veri) {#dirt-rally-20-live-data}

DiRT Rally 2.0 oynarken izleyici, oyunun dışarıya gönderdiği verileri kaydeder; böylece bu verilere daha sonra 3DHeat görüntüleyicisinde bir harita üzerinde bakabilirsiniz.

*Teknik ayrıntılar: uyarlayıcı `dirt-rally-2`, tür [`telemetry`](sources-and-rules.md); `dirtrally2.exe` çalışırken çalışır ve her 0,1 saniyede bir yeni veri arar.*

## Ne kaydedilir {#what-is-recorded}

- kendi arabanın konumu (dünya XYZ, m), saniyede 10 kez; hız, vites, gaz, fren ve etap mesafesiyle birlikte
- etap başlangıcı (etap saatinin başlaması), bitiş ve etap süresi, yeniden başlatmalar
- ışınlanmalar (yola dönüş): `teleport` arabanın önceki yeri, `spawn` ise şimdiki yeri
- etaplar, en iyi etap süresi, mesafe, en yüksek hız

## Veri nereden gelir {#where-it-comes-from}

UDP 127.0.0.1:20777, extradata=3 (Belgeler\My Games\DiRT Rally 2.0\hardwaresettings\hardware_settings_config.xml); başka bir uygulama 20777'yi tuttuğu sürece izleyici portu ona bırakır

## Nasıl açılır {#how-to-switch-it-on}

`python -m heat3d_watch setup dirt-rally-2 --apply` komutu &lt;udp enabled="true" extradata="3"> ayarını yapar (önce yedek alınır)

Komutu, izleyicinin klasöründe açılmış bir terminale yazın (bkz. [Başlamadan önce](before-you-start.md)). Başarısız olursa, son satır nedenini söyler; [Kurulum ve çalıştırma](installing-and-running.md) sık görülen nedenleri anlatır.

`python -m heat3d_watch setup dirt-rally-2` değiştirilecek dosyaları listeler; `python -m heat3d_watch setup dirt-rally-2 --apply` bunları değiştirir ve özgün dosyayı `<file>.heat3d-backup` adıyla saklar (bkz. [Komutlar](commands.md#setup)). Her değişiklik için `dirt-rally-2: changed: ...` yazar; zaten açıksa `dirt-rally-2: nothing to change` yazar.

## Nasıl çalışır {#how-it-works}

Yarış oyunlarının kendi telemetrisi: Forza, Assetto Corsa oyunları, ralli oyunları ve BeamNG; rotalar, turlar ve etaplar olarak kaydedilir.

Buradaki her oyun telemetrisini bilerek yayınlar; gösterge panelleri ve hareket platformları içindir. Hiçbir şey enjekte edilmez, oyunun dışarı vermediği hiçbir şey okunmaz. Kod iki kez yazılmaz: tur kaydediciler GameCapture'ın `heat3d_capture/telemetry` klasöründedir (3DHeat GameCapture), `heat3d_watch/decoders` içine kopyalanmıştır ve orada yayınlanan düzenlere göre üretilmiş paketlerle test edilmiştir. Bu modül de çerçeveleri izleyicinin satırlarına çevirir: arabanın konumu saniyede birkaç kez, hızı, vitesi ve pedalları ile; her tur veya etap için bir olay; ve bir sürücünün tuttuğu sayılar: turlar, en iyi tur, mesafe ve en yüksek hız.

#### Forza (Horizon 4/5/6, Motorsport) {#forza-horizon-456-motorsport}

"Data Out" UDP, oyunun HUD ve Oynanış ayarlarında açılır; 127.0.0.1 port 5300, biçim Dash. Her simülasyon tikinde bir paket gelir; dash bloğunun konumu paketlerden bulunur (`forza.detect_layout`). Dünya metre cinsindendir, Y yukarı gösterir; Forza'nın dünyası sol el koordinat sistemindedir ve tur kaydedicinin yaptığı gibi gönderildiği şekliyle çizilir (Forza Motorsport ve Forza Horizon'un "Data Out" belgeleri).
Oyun tek bir porta gönderir; FH Companion ve diğer Data Out uygulamaları aynı porta dinler. İki program aynı portu paylaşamaz: Windows'ta 127.0.0.1'e bağlanan soket paketleri alır, tüm adreslere bağlanan ve aynı portu kullanan soket ise hiçbirini almaz; hangisi önce açıldıysa. Bu yüzden izleyici, oyun başladıktan sonra portu almadan biraz bekler, portu tutan bir uygulamadan asla almaz ve başka bir uygulama orada dinlemeye başlar başlamaz portu bırakır. Portu tuttuğu sürece her paketi değiştirmeden 127.0.0.1:5301 adresine iletir: FH Companion'un port kutusunu (telemetri sekmesi) 5301 yapın, ikisi de kaydeder.

#### EA SPORTS WRC, DiRT Rally 2.0, Richard Burns Rally {#ea-sports-wrc-dirt-rally-20-richard-burns-rally}

UDP: WRC'nin `Belgeler/My Games/WRC/telemetry/config.json` dosyası (`wrc` yapısının `session_update` paketi), DiRT'ün `hardware_settings_config.xml` dosyası (`<udp enabled="true" extradata="3" port="20777">`), RBR'nin NGP eklentisi (`udpTelemetry=1`, port 6776). Etaplar, oyunun etap saatine göre (`rally.StageSplitter`) belirlenir. RBR eksenlerini belgelemez: yukarı eksen, oturum kapanınca belirlenen ve etap boyunca en az değişen eksendir.

#### Her şey saklanır {#everything-kept}

Satırlar saniyede birkaç tanedir; oyunlar çok daha fazlasını gönderir. Porta gelen her UDP paketi (menülerde, turlar arasında, hiçbir çözücünün okumadığı paketler dahil) oturumun `heat.raw.parquet` dosyasında, biçimi altında (`dash-horizon`, `session_update`, `extradata3`, `H3D1`, ...) bütün olarak saklanır. Değişen her paylaşılan bellek sayfası da (yalnızca çözülen baytlar değil, bütün eşleme), eşleme adı altında (`acpmf_physics`, ...) saklanır. `used` satırlara da dönüşenleri işaretler; `meta.json` içindeki `selfCheck.completeness` her türü sayar (3DHeat'in dönüştürücü kuralı).

Bu modül şunlara da hizmet eder: [Assetto Corsa (canlı veri)](game-assetto-corsa.md), [Assetto Corsa Competizione (canlı veri)](game-assetto-corsa-competizione.md), [Assetto Corsa EVO (canlı veri)](game-assetto-corsa-evo.md), [Assetto Corsa Rally (canlı veri)](game-assetto-corsa-rally.md), [BeamNG.drive (canlı veri)](game-beamng.md), [EA SPORTS WRC (canlı veri)](game-ea-wrc.md), [Forza Horizon 4 (canlı veri)](game-forza-horizon-4.md), [Forza Horizon 5 (canlı veri)](game-forza-horizon-5.md), [Forza Horizon 6 (canlı veri)](game-forza-horizon-6.md), [Forza Motorsport (canlı veri)](game-forza-motorsport.md), [Richard Burns Rally (canlı veri)](game-richard-burns-rally.md).

## Konumlar ve eksenler {#positions-and-axes}

| | |
|---|---|
| Konumlar kaydedilir | evet |
| Yukarı eksen | `y` |
| Birimler | metre |
| Görüntüleyici için aynalama | yok |
| Birim ölçeği (`scale`: görüntüleyici konumları bununla çarpar) | 1 |

Bunlar her oturumun `meta.json` dosyasındaki (`axes`) ve oturumda konum varsa `heat.parquet` dosyasının altbilgisine yazılır; böylece 3DHeat görüntüleyicisi satırları kendi başına döndürür ve ölçekler. Bkz. [Veriler](the-data.md).

## Çok oyunculu {#multiplayer}

- Çevrimiçi oynanan olarak işaretli (`multiplayer`): **evet**. `games --markdown` bunu "izinli (yalnızca oyunun yayınladığını okur)" olarak gösterir.
- Tür `telemetry`: yalnızca oyunun veya platformun dışarı verdiğini okur (oyunun yayınladığı bir UDP portu veya paylaşılan bellek); bu yüzden çevrimiçi oyunda da kaydeder. Bayrak yalnızca belleğin hiç okunup okunamayacağını belirler.
- Bellek: bu uyarlayıcı **asla** okumaz. Yalnızca `memory` uyarlayıcıları bellek okur ve çevrimiçi oynanan olarak işaretli bir oyun için hiçbir zaman. Bkz. [Kaynaklar ve kurallar](sources-and-rules.md).

## Kaydedilen istatistikler {#statistics-recorded}

Bu uyarlayıcının kodunun ada göre ayarladığı istatistik anahtarları (her oturumun `meta.json` dosyasındaki `stats` ve `watcher.sqlite` dosyasındaki `stats` tablosu):

`best_lap`, `best_stage`, `distance_km`, `laps`, `stages`, `top_speed_kmh`

Süslü parantez içindeki bir anahtar çalışma zamanında tamamlanır (`score.{team}` her takım için ayrı bir anahtardır). Kodun oyunun alan tablosundan veya oyunun kendi istatistik adlarından aldığı anahtarlar bu listede yer almaz; yukarıdaki "Ne kaydedilir" bölümü onları adlandırır.

## Tamlık {#completeness}

İzleyici 3DHeat'in [dönüştürücü kuralını](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md) izler: kaynağın tuttuğu her şey okunur veya saklanır, hiçbir şey atılmaz. Satırların yanında, uyarlayıcının aldığı her paket, sayfa, satır veya yanıt oturumun `heat.raw.parquet` dosyasında bütün olarak saklanır (sütunlar `time`, `ms`, `type`, `used`, `payload`, `text` ve ada göre tutulan her alan; `used` satırlara da dönüşenleri işaretler). `meta.json` içindeki `selfCheck.completeness` her `type` değerini sayar; `lost` 0'dır.

**Okunan**

- saniyede 10 satır: konum, hız, vites, gaz, fren, etap mesafesi, yalpa, devir, direksiyon; etap başlangıcı, etap süresiyle bitiş, yeniden başlatmalar

**Ham olarak saklanan**

- porta ulaşan her paket bütün olarak, oyunun hızında, biçimi altında: `extradata3` (66 float, 264 bayt), `extradata3-64` (DiRT Rally'nin 64'ü), aksi halde `<n>-byte`
- satırların ötesinde paketteki 66 float'ın hepsi: dünya hızı, yan ve ileri vektörler, tekerlek başına süspansiyon konumu ve hızı, temas yaması hızı ve fren sıcaklığı, g kuvvetleri, turlar, etap uzunluğu; adı kesin olarak bilinmeyen float'lar tur dosyalarında `float<i>` adıyla bulunur

**Mevcut olmayan**

- diğer arabalar: oyunlar yalnızca oyuncunun arabasını gönderir
- el freni kanalı: paketinde yoktur

**Boyut**: saatte yaklaşık 70 MB (saniyede 60 paket, her biri 264 bayt artı 70 baytlık öğe başlığı); zstd bir kısmını tutar

## Doğrulama {#verified}

çözümleme gamecapture'ın tur kaydedicisinin çözümlemesidir (belgelenmiş düzenlerden kurulan paketlerde test edildi); uyarlayıcı, testte kurulan paketlerle UDP üzerinden gönderilerek test edildi; oyunda test edilmedi

## Kaynak {#source}

[heat3d_watch/adapters/racing.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/racing.py)

<!-- Adaptörden tools/gen_game_pages.py ile üretilmiştir; sayfayı elle düzenlemek yerine adaptörü değiştirin ve yeniden çalıştırın. -->
