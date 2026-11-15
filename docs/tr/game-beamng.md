---
title: "BeamNG.drive (canlı veri)"
nav_order: 7
lang: "tr"
source: game-beamng.md
source_hash: "1c23a869a62f"
nav_exclude: true
search_exclude: true
---
# BeamNG.drive (canlı veri) {#beamngdrive-live-data}

BeamNG.drive oynarken izleyici, oyunun kendi gönderdiği verileri kaydeder; böylece bu verilere daha sonra 3DHeat görüntüleyicisinde bir harita üzerinde bakabilirsiniz.

*Teknik ayrıntılar: bağdaştırıcı `beamng`, tür [`telemetry`](sources-and-rules.md); `BeamNG.drive.x64.exe` ya da `BeamNG.drive.exe` çalışırken çalışır ve yeni veri için her 0,1 saniyede bir bakar.*

## Ne kaydedilir {#what-is-recorded}

- kendi arabanızın konumu (dünya, m, Y yukarı olacak şekilde çevrilmiş), 10 Hz ile, hız, vites, gaz, fren ile birlikte
- sürüşün başlangıcı, sıfırlamalar (yeniden doğma), sürüşün başladığı yerden geçen turlar
- turlar, en iyi tur, mesafe, en yüksek hız

## Kaynağı {#where-it-comes-from}

127.0.0.1:4460 UDP üzerinden, heat3d protokol modundan (bu depoda mods/beamng/heat3d)

## Nasıl açılır {#how-to-switch-it-on}

`python -m heat3d_watch setup beamng --apply` modu kurar; sonra Options > Other > Protocols > "others"

Komutu, izleyicinin klasöründe açılmış bir terminale yazın (bkz. [Başlamadan önce](before-you-start.md)). Başarısız olursa son satır nedenini söyler; [Kurulum ve çalıştırma](installing-and-running.md) yaygın nedenleri anlatır.

`python -m heat3d_watch setup beamng` hangi dosyaları değiştireceğini listeler; `python -m heat3d_watch setup beamng --apply` onları değiştirir ve özgün dosyayı `<file>.heat3d-backup` olarak saklar (bkz. [Komutlar](commands.md#setup)). Her değişiklik için `beamng: changed: ...` yazar; zaten açıksa `beamng: nothing to change` yazar.

## Nasıl çalışır {#how-it-works}

Yarış oyunlarının kendi telemetrisi: Forza, Assetto Corsa oyunları, ralli oyunları ve BeamNG; rota, tur ve etap olarak kaydedilir.

Burada her oyun telemetrisini bilerek yayımlar; gösterge panelleri ve hareket düzenekleri için. Hiçbir şey enjekte edilmez, oyunun dışarı vermediği hiçbir şey de okunmaz. Çözümleme iki kez yazılmaz: 3DHeat GameCapture'ın `heat3d_capture/telemetry` içindeki tur kayıt cihazları `heat3d_watch/decoders` içine kopyalanmıştır (orada, yayımlanmış düzenlerden üretilen paketlerle test edilmiştir). Bu modül onların karelerini izleyicinin satırlarına çevirir: arabanın konumu saniyede birkaç kez, hız, vites ve pedallarıyla; her tur ya da etap için bir olay; ve bir sürücünün tuttuğu sayılar: turlar, en iyi tur, mesafe, en yüksek hız.

#### Forza (Horizon 4/5/6, Motorsport) {#forza-horizon-456-motorsport}

Oyunun HUD ve Oynanış ayarlarında açılan "Data Out" UDP, 127.0.0.1 portuna, biçim Dash. Her simülasyon tikinde bir paket gelir; gösterge bloğunun ofseti paketlerden bulunur (`forza.detect_layout`). Dünya metre cinsindendir, Y yukarı; dünya sol elli bir koordinat sistemidir ve tur kayıt cihazının yaptığı gibi, gönderildiği şekliyle çizilir (Forza Motorsport ve Forza Horizon'un "Data Out" belgelerine göre).
Oyun tek bir porta gönderir; FH Companion ve diğer Data Out uygulamaları da aynı porta dinler. İki program bunu paylaşamaz: Windows'ta 127.0.0.1'e bağlanan soket paketleri alır, aynı porta tüm adreslere bağlanan soket ise hiç almaz; hangisi önce gelmişse. Bu yüzden izleyici, oyun başladıktan kısa bir süre sonra portu alır, portu tutan bir uygulamadan asla almaz ve orada dinlemeye başlayan başka bir uygulama açılır açılmaz portu bırakır. Portu tuttuğu sürece her paketi değiştirmeden 127.0.0.1:5301 adresine iletir - FH Companion'ın port kutusunu (telemetri sekmesi) 5301 yapın, ikisi de kaydeder.

#### BeamNG.drive {#beamngdrive}

gamecapture'ın gönderdiği `heat3d` protokol modu (UDP 4460, Options > Other > Protocols > "others"); BeamNG'nin Z yukarı olan dünyası, `beamng.py`'nin yaptığı gibi Y yukarı olacak şekilde çevrilir.

#### Her şey saklanır {#everything-kept}

Satırlar saniyede birkaç tanedir; oyunlar çok daha fazlasını gönderir. Ulaşan her UDP paketi - menülerde, turlar arasında, hiçbir çözücünün okumadığı paketler dahil - bütün olarak oturumun `heat.raw.parquet` dosyasında, kendi biçimi altında saklanır (`dash-horizon`, `session_update`, `extradata3`, `H3D1`, ...). Her paylaşılan bellek sayfası da değiştiğinde (yalnızca çözülen baytlar değil, bütün eşleme), eşleme adı altında saklanır (`acpmf_physics`, ...). `used` satıra dönüşenleri işaretler; `meta.json` içindeki `selfCheck.completeness` her türü sayar (3DHeat'in dönüştürücü kuralı).

Bu modülün sunduğu diğer sayfalar: [Assetto Corsa (canlı veri)](game-assetto-corsa.md), [Assetto Corsa Competizione (canlı veri)](game-assetto-corsa-competizione.md), [Assetto Corsa EVO (canlı veri)](game-assetto-corsa-evo.md), [Assetto Corsa Rally (canlı veri)](game-assetto-corsa-rally.md), [DiRT Rally 2.0 (canlı veri)](game-dirt-rally-2.md), [EA SPORTS WRC (canlı veri)](game-ea-wrc.md), [Forza Horizon 4 (canlı veri)](game-forza-horizon-4.md), [Forza Horizon 5 (canlı veri)](game-forza-horizon-5.md), [Forza Horizon 6 (canlı veri)](game-forza-horizon-6.md), [Forza Motorsport (canlı veri)](game-forza-motorsport.md), [Richard Burns Rally (canlı veri)](game-richard-burns-rally.md).

## Konumlar ve eksenler {#positions-and-axes}

| | |
|---|---|
| Kaydedilen konumlar | evet |
| Yukarı ekseni | `y` |
| Birimler | metre (BeamNG'nin Z yukarı dünyası, gamecapture'ın tur kayıt cihazının yaptığı gibi X etrafında çevrilmiş) |
| Görüntüleyici için aynalama | yok |
| Birim ölçeği (`scale`: görüntüleyici konumları bununla çarpar) | 1 |

Bunlar her oturumun `meta.json` dosyasındaki (`axes`) ve konum içeren oturumlarda `heat.parquet` dosyasının sonundaki (footer) bilgiye yazılır; böylece 3DHeat görüntüleyicisi satırları kendisi döndürür ve ölçekler - bkz. [Veriler](the-data.md).

## Çok oyunculu {#multiplayer}

- Çevrimiçi oynanan olarak işaretlenmiş (`multiplayer`): **hayır**. `games --markdown` bunu "tek oyunculu" olarak gösterir.
- Tür `telemetry`: yalnızca oyunun ya da platformun dışarı verdiğini okur (oyunun yayımladığı bir UDP portu ya da paylaşılan bellek). Bu yüzden çevrimiçi oyunda da çevrimdışı olduğu gibi kaydeder; bayrak yalnızca belleğin hiç okunup okunamayacağını belirler.
- Bellek: bu bağdaştırıcı **asla** okumaz. Yalnızca `memory` bağdaştırıcıları bellek okur ve çevrimiçi oynanan olarak işaretlenmiş bir oyun için asla okumaz - bkz. [Kaynaklar ve kurallar](sources-and-rules.md).

## Kaydedilen istatistikler {#statistics-recorded}

Bu bağdaştırıcının kodunun adla ayarladığı istatistik anahtarları (her oturumun `meta.json` içindeki `stats` ve `watcher.sqlite` içindeki `stats` tablosu):

`best_lap`, `distance_km`, `laps`, `top_speed_kmh`

Parantez içindeki bir anahtar çalışma zamanında tamamlanır (`score.{team}` her takım için bir anahtardır). Kodun oyunun alanlarının tablosundan ya da oyunun kendi istatistik adlarından aldığı anahtarlar bu listede yer almaz; yukarıdaki "Ne kaydedilir" bölümü bunları adlandırır.

## Tamlık {#completeness}

İzleyici 3DHeat'in [dönüştürücü kuralını](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md) izler: kaynağın tuttuğu her şey okunur ya da saklanır, asla atılmaz. Satırların yanı sıra, bağdaştırıcının aldığı her paket, sayfa, satır ya da yanıt, oturumun `heat.raw.parquet` dosyasında bütün olarak saklanır (sütunlar `time`, `ms`, `type`, `used`, `payload`, `text` ve adla saklanan her alan; `used` satıra dönüşenleri işaretler). `meta.json` içindeki `selfCheck.completeness` her `type` değerini sayar - `lost` 0'dır.

**Okunan**

- saniyede 10 satır: konum, hız, vites, gaz, fren, dönüş, rpm, direksiyon; sürüşün başlangıcı, sıfırlamalar, turlar

**Ham olarak saklanan**

- moddan 100 Hz'de, porta ulaşan her paket bütün olarak: `H3D1` (modun 160 baytlık yapısı: saat, konum, hız, arabanın eksenleri, dönüş hızı, dokuz girdi, tekerlek başına yüzey hızı, dönüş, yük ve zemin malzemesi), diğer her şey için `<n>-byte`

**Kullanılamayanlar**

- modun göndermediği şeyler: BeamNG'nin sabit bir telemetri paketi yoktur, kanallar heat3d modunun seçtikleridir (diğer araçlar, hasar, haritanın adı bunda yoktur)

**Boyut**: sıkıştırmadan önce saat başına yaklaşık 80 MB (saniyede 100 paket, her biri 160 bayt artı 70 baytlık bir öğe başlığı)

## Doğrulama {#verified}

çözümleme gamecapture'ın tur kayıt cihazınındır (modun yapısından üretilen paketlerle test edilmiştir); bağdaştırıcı bu tür paketlerle test edilmiştir; mod oyunda test edilmemiştir

## Kaynak {#source}

[heat3d_watch/adapters/racing.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/racing.py)

<!-- Adaptörden tools/gen_game_pages.py ile üretilmiştir; sayfayı elle düzenlemek yerine adaptörü değiştirin ve yeniden çalıştırın. -->
