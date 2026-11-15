---
title: "Assetto Corsa Rally (canlı veri)"
nav_order: 5
lang: "tr"
source: game-assetto-corsa-rally.md
source_hash: "09b8a6d66e31"
nav_exclude: true
search_exclude: true
---
# Assetto Corsa Rally (canlı veri) {#assetto-corsa-rally-live-data}

Assetto Corsa Rally oynarken izleyici, oyunun kendi gönderdiği verileri kaydeder; böylece bu verilere daha sonra 3DHeat görüntüleyicisinde bir harita üzerinde bakabilirsiniz.

*Teknik ayrıntılar: bağdaştırıcı `assetto-corsa-rally`, tür [`telemetry`](sources-and-rules.md); `acr.exe`, `ACR-Win64-Shipping.exe`, `AssettoCorsaRally.exe` ya da `acrally-Win64-Shipping.exe` çalışırken çalışır ve yeni veri için her 0,1 saniyede bir bakar.*

## Ne kaydedilir {#what-is-recorded}

- kendi arabanızın konumu (dünya XYZ, m: lastik temas noktalarının ortalaması), 10 Hz ile, hız, vites, gaz ve fren ile birlikte
- oturumun başlangıcı ve sonu, oyunun adlandırdığı pist ve araba ile
- etaplar: her etap, arabanın durduğu yerde biter; geçen süre ile birlikte
- ışınlanmalar (pite geri dönme, yeniden başlatma): arabanın olduğu yer için `teleport`, arabanın şimdi olduğu yer için `spawn`
- turlar, en iyi tur, mesafe, en yüksek hız

## Kaynağı {#where-it-comes-from}

paylaşılan bellek Local\acpmf_physics, Local\acpmf_static (AC ve ACC ile aynı sayfalar)

## Nasıl açılır {#how-to-switch-it-on}

Hiçbir şeyi açmanız gerekmez: izleyici kaynağı, oyunun ya da platformun sunduğu haliyle okur.

## Nasıl çalışır {#how-it-works}

Yarış oyunlarının kendi telemetrisi: Forza, Assetto Corsa oyunları, ralli oyunları ve BeamNG; rota, tur ve etap olarak kaydedilir.

Burada her oyun telemetrisini bilerek yayımlar; gösterge panelleri ve hareket düzenekleri için. Hiçbir şey enjekte edilmez, oyunun dışarı vermediği hiçbir şey de okunmaz. Çözümleme iki kez yazılmaz: 3DHeat GameCapture'ın `heat3d_capture/telemetry` içindeki tur kayıt cihazları `heat3d_watch/decoders` içine kopyalanmıştır (orada, yayımlanmış düzenlerden üretilen paketlerle test edilmiştir). Bu modül onların karelerini izleyicinin satırlarına çevirir: arabanın konumu saniyede birkaç kez, hız, vites ve pedallarıyla; her tur ya da etap için bir olay; ve bir sürücünün tuttuğu sayılar: turlar, en iyi tur, mesafe, en yüksek hız.

#### Forza (Horizon 4/5/6, Motorsport) {#forza-horizon-456-motorsport}

Oyunun HUD ve Oynanış ayarlarında açılan "Data Out" UDP, 127.0.0.1 portuna, biçim Dash. Her simülasyon tikinde bir paket gelir; gösterge bloğunun ofseti paketlerden bulunur (`forza.detect_layout`). Dünya metre cinsindendir, Y yukarı; dünya sol elli bir koordinat sistemidir ve tur kayıt cihazının yaptığı gibi, gönderildiği şekliyle çizilir (Forza Motorsport ve Forza Horizon'un "Data Out" belgelerine göre).
Oyun tek bir porta gönderir; FH Companion ve diğer Data Out uygulamaları da aynı porta dinler. İki program bunu paylaşamaz: Windows'ta 127.0.0.1'e bağlanan soket paketleri alır, aynı porta tüm adreslere bağlanan soket ise hiç almaz; hangisi önce gelmişse. Bu yüzden izleyici, oyun başladıktan kısa bir süre sonra portu alır, portu tutan bir uygulamadan asla almaz ve orada dinlemeye başlayan başka bir uygulama açılır açılmaz portu bırakır. Portu tuttuğu sürece her paketi değiştirmeden 127.0.0.1:5301 adresine iletir - FH Companion'ın port kutusunu (telemetri sekmesi) 5301 yapın, ikisi de kaydeder.

#### Her şey saklanır {#everything-kept}

Satırlar saniyede birkaç tanedir; oyunlar çok daha fazlasını gönderir. Ulaşan her UDP paketi - menülerde, turlar arasında, hiçbir çözücünün okumadığı paketler dahil - bütün olarak oturumun `heat.raw.parquet` dosyasında, kendi biçimi altında saklanır (`dash-horizon`, `session_update`, `extradata3`, `H3D1`, ...). Her paylaşılan bellek sayfası da değiştiğinde (yalnızca çözülen baytlar değil, bütün eşleme), eşleme adı altında saklanır (`acpmf_physics`, ...). `used` satıra dönüşenleri işaretler; `meta.json` içindeki `selfCheck.completeness` her türü sayar (3DHeat'in dönüştürücü kuralı).

Bu modülün sunduğu diğer sayfalar: [Assetto Corsa (canlı veri)](game-assetto-corsa.md), [Assetto Corsa Competizione (canlı veri)](game-assetto-corsa-competizione.md), [Assetto Corsa EVO (canlı veri)](game-assetto-corsa-evo.md), [BeamNG.drive (canlı veri)](game-beamng.md), [DiRT Rally 2.0 (canlı veri)](game-dirt-rally-2.md), [EA SPORTS WRC (canlı veri)](game-ea-wrc.md), [Forza Horizon 4 (canlı veri)](game-forza-horizon-4.md), [Forza Horizon 5 (canlı veri)](game-forza-horizon-5.md), [Forza Horizon 6 (canlı veri)](game-forza-horizon-6.md), [Forza Motorsport (canlı veri)](game-forza-motorsport.md), [Richard Burns Rally (canlı veri)](game-richard-burns-rally.md).

## Konumlar ve eksenler {#positions-and-axes}

| | |
|---|---|
| Kaydedilen konumlar | evet |
| Yukarı ekseni | `y` |
| Birimler | metre |
| Görüntüleyici için aynalama | yok |
| Birim ölçeği (`scale`: görüntüleyici konumları bununla çarpar) | 1 |

Bunlar her oturumun `meta.json` dosyasındaki (`axes`) ve konum içeren oturumlarda `heat.parquet` dosyasının sonundaki (footer) bilgiye yazılır; böylece 3DHeat görüntüleyicisi satırları kendisi döndürür ve ölçekler - bkz. [Veriler](the-data.md).

## Çok oyunculu {#multiplayer}

- Çevrimiçi oynanan olarak işaretlenmiş (`multiplayer`): **evet**. `games --markdown` bunu "izinli (yalnızca oyunun yayımladığını okur)" olarak gösterir.
- Tür `telemetry`: yalnızca oyunun ya da platformun dışarı verdiğini okur (oyunun yayımladığı bir UDP portu ya da paylaşılan bellek). Bu yüzden çevrimiçi oyunda da çevrimdışı olduğu gibi kaydeder; bayrak yalnızca belleğin hiç okunup okunamayacağını belirler.
- Bellek: bu bağdaştırıcı **asla** okumaz. Yalnızca `memory` bağdaştırıcıları bellek okur ve çevrimiçi oynanan olarak işaretlenmiş bir oyun için asla okumaz - bkz. [Kaynaklar ve kurallar](sources-and-rules.md).

## Kaydedilen istatistikler {#statistics-recorded}

Bu bağdaştırıcının kodunun adla ayarladığı istatistik anahtarları (her oturumun `meta.json` içindeki `stats` ve `watcher.sqlite` içindeki `stats` tablosu):

`best_lap`, `best_stage`, `distance_km`, `laps`, `race_position`, `stages`, `top_speed_kmh`

Parantez içindeki bir anahtar çalışma zamanında tamamlanır (`score.{team}` her takım için bir anahtardır). Kodun oyunun alanlarının tablosundan ya da oyunun kendi istatistik adlarından aldığı anahtarlar bu listede yer almaz; yukarıdaki "Ne kaydedilir" bölümü bunları adlandırır.

## Tamlık {#completeness}

İzleyici 3DHeat'in [dönüştürücü kuralını](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md) izler: kaynağın tuttuğu her şey okunur ya da saklanır, asla atılmaz. Satırların yanı sıra, bağdaştırıcının aldığı her paket, sayfa, satır ya da yanıt, oturumun `heat.raw.parquet` dosyasında bütün olarak saklanır (sütunlar `time`, `ms`, `type`, `used`, `payload`, `text` ve adla saklanan her alan; `used` satıra dönüşenleri işaretler). `meta.json` içindeki `selfCheck.completeness` her `type` değerini sayar - `lost` 0'dır.

**Okunan**

- ana sayfadan saniyede 10 satır: konum (lastik temas noktalarının ortalaması), hız, vites, gaz, fren, dönüş (yaw/pitch/roll, rad), rpm, direksiyon (sayfada göründüğü gibi); statik sayfadan oturumun başlangıcı, pist ve araba; turlar, yarış sırası

**Ham olarak saklanan**

- her sayfa bütün olarak - yalnızca çözülen baytlar değil, bütün eşleme bölgesi - baytları değiştiğinde, izleyicinin saniyede 10 okumasında: `acpmf_physics`, `acpmf_static`; bir önceki okumayla bayt bayt aynı olan okuma, meta.json içindeki `unchanged_reads` olarak sayılır, yeniden saklanmaz
- yalnızca tur dosyaları için çözülen her şey (`decoders/kunos.py`: tekerlek başına kayma, yük, basınç, sıcaklıklar, kamber, süspansiyon, temas noktaları, fren sıcaklıkları, kayma oranı ve açısı; dünya ve yerel hız, açısal hız, yardımcılar) bu sayfalarda bulunur

**Kullanılamayanlar**

- diğer arabaların konumları: sayfalar yalnızca oyuncunun arabasını anlatır (ACC'nin grafik sayfası bazı sürümlerde diğer arabaların kimliklerini ve koordinatlarını taşır - ham sayfada saklanır, çözülmez)
- izleyicinin okumaları arasındaki fizik tikleri: oyun sayfayı kendi fizik hızında (333 Hz'e kadar) yeniden yazar, izleyici ise saniyede 10 kez okur
- bir etap saati ya da oyunun etap süresi: AC Rally grafik sayfası yayımlamaz; etaplar arabanın durduğu yerde biter

**Boyut**: saat başına yaklaşık 150-300 MB, sıkıştırmadan önce (değişen her sayfa için 4 KB'lık bir bölge, saniyede en fazla 10 değişiklik); sayfalar çoğunlukla sıfırdır ve zstd onların küçük bir kısmını tutar

## Doğrulama {#verified}

çözümleme gamecapture'ın tur kayıt cihazınındır (sentetik sayfalarla test edilmiştir); bağdaştırıcı, testte belgelenmiş düzene göre kurulan paylaşılan bellek üzerinde test edilmiştir; oyunla test edilmemiştir; çalıştırılabilir dosya adı doğrulanmamıştır

## Kaynak {#source}

[heat3d_watch/adapters/racing.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/racing.py)

<!-- Adaptörden tools/gen_game_pages.py ile üretilmiştir; sayfayı elle düzenlemek yerine adaptörü değiştirin ve yeniden çalıştırın. -->
