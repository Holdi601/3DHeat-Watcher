---
title: "Forza Horizon 5 (canlı veri)"
nav_order: 22
lang: "tr"
source: game-forza-horizon-5.md
source_hash: "0083724478e7"
nav_exclude: true
search_exclude: true
---
# Forza Horizon 5 (canlı veri) {#forza-horizon-5-live-data}

Forza Horizon 5 oynarken izleyici, oyunun dışarıya gönderdiği verileri kaydeder; böylece bu verilere daha sonra 3DHeat görüntüleyicisinde bir harita üzerinde bakabilirsiniz.

*Teknik ayrıntılar: uyarlayıcı `forza-horizon-5`, tür [`telemetry`](sources-and-rules.md); `ForzaHorizon5.exe` çalışırken çalışır ve her 0,1 saniyede bir yeni veri arar.*

## Ne kaydedilir {#what-is-recorded}

- kendi arabanın konumu (dünya XYZ, m), saniyede 10 kez; hız, vites, gaz, fren ve turla birlikte
- sürüşün başlangıcı ve sonu (session_start/session_end), oyunun tur süresiyle turlar
- yarış başlangıcı ve bitişi, yarış konumuyla birlikte
- ışınlanmalar (geri sarma, hızlı seyahat): `teleport` arabanın önceki yeri, `spawn` ise şimdiki yeri
- turlar, en iyi tur, mesafe, en yüksek hız, yarışlar

## Veri nereden gelir {#where-it-comes-from}

Forza Data Out, UDP 127.0.0.1:5300 (Dash biçimi); her paket değiştirilmeden 127.0.0.1:5301 adresine iletilir

## Nasıl açılır {#how-to-switch-it-on}

Oyunda: Ayarlar > HUD ve Oynanış > Data Out Açık, IP 127.0.0.1, port 5300 (Motorsport: biçim Dash). FH Companion veya başka bir Data Out uygulaması: portunu 5301 yapın - izleyici her paketi iletir; başka bir uygulama 5300'de dinlediği sürece izleyici portu ona bırakır ve hiçbir şey kaydetmez

## Nasıl çalışır {#how-it-works}

Yarış oyunlarının kendi telemetrisi: Forza, Assetto Corsa oyunları, ralli oyunları ve BeamNG; rotalar, turlar ve etaplar olarak kaydedilir.

Buradaki her oyun telemetrisini bilerek yayınlar; gösterge panelleri ve hareket platformları içindir. Hiçbir şey enjekte edilmez, oyunun dışarı vermediği hiçbir şey okunmaz. Kod iki kez yazılmaz: tur kaydediciler GameCapture'ın `heat3d_capture/telemetry` klasöründedir (3DHeat GameCapture), `heat3d_watch/decoders` içine kopyalanmıştır ve orada yayınlanan düzenlere göre üretilmiş paketlerle test edilmiştir. Bu modül de çerçeveleri izleyicinin satırlarına çevirir: arabanın konumu saniyede birkaç kez, hızı, vitesi ve pedalları ile; her tur veya etap için bir olay; ve bir sürücünün tuttuğu sayılar: turlar, en iyi tur, mesafe ve en yüksek hız.

#### Forza (Horizon 4/5/6, Motorsport) {#forza-horizon-456-motorsport}

"Data Out" UDP, oyunun HUD ve Oynanış ayarlarında açılır; 127.0.0.1 port 5300, biçim Dash. Her simülasyon tikinde bir paket gelir; dash bloğunun konumu paketlerden bulunur (`forza.detect_layout`). Dünya metre cinsindendir, Y yukarı gösterir; Forza'nın dünyası sol el koordinat sistemindedir ve tur kaydedicinin yaptığı gibi gönderildiği şekliyle çizilir (Forza Motorsport ve Forza Horizon'un "Data Out" belgeleri).
Oyun tek bir porta gönderir; FH Companion ve diğer Data Out uygulamaları aynı porta dinler. İki program aynı portu paylaşamaz: Windows'ta 127.0.0.1'e bağlanan soket paketleri alır, tüm adreslere bağlanan ve aynı portu kullanan soket ise hiçbirini almaz; hangisi önce açıldıysa. Bu yüzden izleyici, oyun başladıktan sonra portu almadan biraz bekler, portu tutan bir uygulamadan asla almaz ve başka bir uygulama orada dinlemeye başlar başlamaz portu bırakır. Portu tuttuğu sürece her paketi değiştirmeden 127.0.0.1:5301 adresine iletir: FH Companion'un port kutusunu (telemetri sekmesi) 5301 yapın, ikisi de kaydeder.

#### Her şey saklanır {#everything-kept}

Satırlar saniyede birkaç tanedir; oyunlar çok daha fazlasını gönderir. Porta gelen her UDP paketi (menülerde, turlar arasında, hiçbir çözücünün okumadığı paketler dahil) oturumun `heat.raw.parquet` dosyasında, biçimi altında (`dash-horizon`, `session_update`, `extradata3`, `H3D1`, ...) bütün olarak saklanır. Değişen her paylaşılan bellek sayfası da (yalnızca çözülen baytlar değil, bütün eşleme), eşleme adı altında (`acpmf_physics`, ...) saklanır. `used` satırlara da dönüşenleri işaretler; `meta.json` içindeki `selfCheck.completeness` her türü sayar (3DHeat'in dönüştürücü kuralı).

Bu modül şunlara da hizmet eder: [Assetto Corsa (canlı veri)](game-assetto-corsa.md), [Assetto Corsa Competizione (canlı veri)](game-assetto-corsa-competizione.md), [Assetto Corsa EVO (canlı veri)](game-assetto-corsa-evo.md), [Assetto Corsa Rally (canlı veri)](game-assetto-corsa-rally.md), [BeamNG.drive (canlı veri)](game-beamng.md), [DiRT Rally 2.0 (canlı veri)](game-dirt-rally-2.md), [EA SPORTS WRC (canlı veri)](game-ea-wrc.md), [Forza Horizon 4 (canlı veri)](game-forza-horizon-4.md), [Forza Horizon 6 (canlı veri)](game-forza-horizon-6.md), [Forza Motorsport (canlı veri)](game-forza-motorsport.md), [Richard Burns Rally (canlı veri)](game-richard-burns-rally.md).

## Konumlar ve eksenler {#positions-and-axes}

| | |
|---|---|
| Konumlar kaydedilir | evet |
| Yukarı eksen | `y` |
| Birimler | metre; Forza'nın dünyası sol el koordinat sistemindedir, tur kaydedicinin yaptığı gibi gönderildiği şekliyle çizilir |
| Görüntüleyici için aynalama | yok |
| Birim ölçeği (`scale`: görüntüleyici konumları bununla çarpar) | 1 |

Bunlar her oturumun `meta.json` dosyasındaki (`axes`) ve oturumda konum varsa `heat.parquet` dosyasının altbilgisine yazılır; böylece 3DHeat görüntüleyicisi satırları kendi başına döndürür ve ölçekler. Bkz. [Veriler](the-data.md).

## Çok oyunculu {#multiplayer}

- Çevrimiçi oynanan olarak işaretli (`multiplayer`): **evet**. `games --markdown` bunu "izinli (yalnızca oyunun yayınladığını okur)" olarak gösterir.
- Tür `telemetry`: yalnızca oyunun veya platformun dışarı verdiğini okur (oyunun yayınladığı bir UDP portu veya paylaşılan bellek); bu yüzden çevrimiçi oyunda da kaydeder. Bayrak yalnızca belleğin hiç okunup okunamayacağını belirler.
- Bellek: bu uyarlayıcı **asla** okumaz. Yalnızca `memory` uyarlayıcıları bellek okur ve çevrimiçi oynanan olarak işaretli bir oyun için hiçbir zaman. Bkz. [Kaynaklar ve kurallar](sources-and-rules.md).

## Kaydedilen istatistikler {#statistics-recorded}

Bu uyarlayıcının kodunun ada göre ayarladığı istatistik anahtarları (her oturumun `meta.json` dosyasındaki `stats` ve `watcher.sqlite` dosyasındaki `stats` tablosu):

`best_lap`, `distance_km`, `laps`, `races`, `top_speed_kmh`

Süslü parantez içindeki bir anahtar çalışma zamanında tamamlanır (`score.{team}` her takım için ayrı bir anahtardır). Kodun oyunun alan tablosundan veya oyunun kendi istatistik adlarından aldığı anahtarlar bu listede yer almaz; yukarıdaki "Ne kaydedilir" bölümü onları adlandırır.

## Tamlık {#completeness}

İzleyici 3DHeat'in [dönüştürücü kuralını](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md) izler: kaynağın tuttuğu her şey okunur veya saklanır, hiçbir şey atılmaz. Satırların yanında, uyarlayıcının aldığı her paket, sayfa, satır veya yanıt oturumun `heat.raw.parquet` dosyasında bütün olarak saklanır (sütunlar `time`, `ms`, `type`, `used`, `payload`, `text` ve ada göre tutulan her alan; `used` satırlara da dönüşenleri işaretler). `meta.json` içindeki `selfCheck.completeness` her `type` değerini sayar; `lost` 0'dır.

**Okunan**

- saniyede 10 satır: konum, hız, vites, gaz, fren, tur, yalpa/yunuslama/yuvarlanma (rad), devir, direksiyon (-1..1); session_start, arabanın sırası, sınıfı, PI ve aktarma organı ile; oyunun tur süresiyle turlar; yarış konumu

**Ham olarak saklanan**

- porta ulaşan her paket bütün olarak, oyunun hızında (simülasyon tikinde bir), biçimi altında: `dash-horizon` (324 bayt, Forza Horizon), `dash` (311, Motorsport 7), `dash-fm2023` (331, Forza Motorsport 2023: lastik aşınması ve pist kimliği), `sled` (232, konum yok), diğer her şey için `<n>-byte` - menü paketleri (isRaceOn 0), düzen kanıtlanana kadar tutulan paketler ve hiçbir yayınlanmış düzenin adlandırmadığı Horizon paketindeki ~13 bayt dahil
- Sled bloğunun her tekerlek kanalı (kayma oranı, kayma açısı, birleşik kayma, süspansiyon, tekerlek hızı, rumble, su birikintisi), ivmeler, açısal hız, güç, tork, turbo, yakıt, lastik sıcaklıkları, debriyaj, el freni, sürüş çizgisi, AI fren farkı: hepsi paketlerde, `decoders/fulllap.decode_full` tarafından onlardan çözülür

**Mevcut olmayan**

- diğer arabalar: Data Out yalnızca oyuncunun arabasını tarif eder
- pist veya rota adı: Forza Horizon hiçbir zaman göndermez; Motorsport 2023 yalnızca bir pist numarası gönderir
- başka bir uygulama (FH Companion) UDP 5300'ü tuttuğunda gelen paketler: izleyici portu ona bırakır

**Boyut**: sıkıştırmadan önce saatte yaklaşık 85 MB (saniyede 60 paket, her biri 324 bayt artı 70 baytlık öğe başlığı); ardışık paketler çok az farklılık gösterir, bu yüzden zstd bunun bir kısmını tutar

## Doğrulama {#verified}

çözümleme gamecapture'ın tur kaydedicisinin çözümlemesidir (Data Out düzeninden kurulan paketlerde test edildi); uyarlayıcı sentetik paketlerde ve kaydedilmiş tur yörüngelerinin paket olarak tekrar oynatılmasıyla test edildi; oyunun kendisinde test edilmedi

## Kaynak {#source}

[heat3d_watch/adapters/racing.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/racing.py)

<!-- Adaptörden tools/gen_game_pages.py ile üretilmiştir; sayfayı elle düzenlemek yerine adaptörü değiştirin ve yeniden çalıştırın. -->
