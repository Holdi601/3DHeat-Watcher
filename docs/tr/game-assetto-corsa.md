---
title: "Assetto Corsa (canlı veri)"
nav_order: 2
lang: "tr"
source: game-assetto-corsa.md
source_hash: "9132272cc104"
nav_exclude: true
search_exclude: true
---
# Assetto Corsa (canlı veri) {#assetto-corsa-live-data}

Assetto Corsa oynarken izleyici, oyunun dışarıya gönderdiği verileri kaydeder; böylece bu verilere daha sonra 3DHeat görüntüleyicisinde bir harita üzerinde bakabilirsiniz.

*Teknik ayrıntılar: uyarlayıcı `assetto-corsa`, tür [`telemetry`](sources-and-rules.md); `acs.exe` veya `acs_x86.exe` çalışırken çalışır ve her 0,1 saniyede bir yeni veri arar.*

## Ne kaydedilir {#what-is-recorded}

- kendi arabanın konumu (dünya XYZ, m: lastiklerin temas noktalarının ortalaması), saniyede 10 kez; hız, vites, gaz ve frenle birlikte
- oturumun başlangıcı ve sonu; oyunun adlandırdığı pist ve araba ile
- oyunun tur sayacına göre turlar ve tur süreleri
- ışınlanmalar (pite geri dönüş, yeniden başlatma): `teleport` arabanın önceki yeri, `spawn` ise şimdiki yeri
- turlar, en iyi tur, mesafe, en yüksek hız

## Veri nereden gelir {#where-it-comes-from}

Paylaşılan bellek: Local\acpmf_physics, Local\acpmf_graphics, Local\acpmf_static

## Nasıl açılır {#how-to-switch-it-on}

Hiçbir şeyi açmanız gerekmez: izleyici kaynağı, oyunun veya platformun sunduğu haliyle okur.

## Nasıl çalışır {#how-it-works}

Yarış oyunlarının kendi telemetrisi: Forza, Assetto Corsa oyunları, ralli oyunları ve BeamNG; rotalar, turlar ve etaplar olarak kaydedilir.

Buradaki her oyun telemetrisini bilerek yayınlar; gösterge panelleri ve hareket platformları içindir. Hiçbir şey enjekte edilmez, oyunun dışarı vermediği hiçbir şey okunmaz. Kod iki kez yazılmaz: tur kaydediciler GameCapture'ın `heat3d_capture/telemetry` klasöründedir (3DHeat GameCapture), `heat3d_watch/decoders` içine kopyalanmıştır ve orada yayınlanan düzenlere göre üretilmiş paketlerle test edilmiştir. Bu modül de çerçeveleri izleyicinin satırlarına çevirir: arabanın konumu saniyede birkaç kez, hızı, vitesi ve pedalları ile birlikte; her tur veya etap için bir olay; ve bir sürücünün tuttuğu sayılar: turlar, en iyi tur, mesafe ve en yüksek hız.

#### Forza (Horizon 4/5/6, Motorsport) {#forza-horizon-456-motorsport}

"Data Out" UDP, oyunun HUD ve Oynanış ayarlarında açılır; 127.0.0.1 port 5300, biçim Dash. Her simülasyon tikinde bir paket gelir; dash bloğunun konumu paketlerden bulunur (`forza.detect_layout`). Dünya metre cinsindendir, Y yukarı gösterir; Forza'nın dünyası sol el koordinat sistemindedir ve tur kaydedicinin yaptığı gibi gönderildiği şekliyle çizilir (Forza Motorsport ve Forza Horizon'un "Data Out" belgeleri).
Oyun tek bir porta gönderir; FH Companion ve diğer Data Out uygulamaları aynı porta dinler. İki program aynı portu paylaşamaz: Windows'ta 127.0.0.1'e bağlanan soket paketleri alır, tüm adreslere bağlanan ve aynı portu kullanan soket ise hiçbirini almaz; hangisi önce açıldıysa. Bu yüzden izleyici, oyun başladıktan sonra portu almadan biraz bekler, portu tutan bir uygulamadan asla almaz ve başka bir uygulama orada dinlemeye başlar başlamaz portu bırakır. Portu tuttuğu sürece her paketi değiştirmeden 127.0.0.1:5301 adresine iletir: FH Companion'un port kutusunu (telemetri sekmesi) 5301 yapın, ikisi de kaydeder.

#### Assetto Corsa, ACC, AC EVO, AC Rally {#assetto-corsa-acc-ac-evo-ac-rally}

Oyunun uygulamalar için yazdığı paylaşılan bellek: `Local\acpmf_physics`, `Local\acpmf_graphics`, `Local\acpmf_static` (AC EVO: `Local\acevo_pmf_*`). Yalnızca okuma izniyle ve oyun belleği oluşturduktan sonra açılır (`simracing_shm`). Konum, dört lastik temas noktasının ortalamasıdır; dünya metre cinsinden, Y yukarı. Turlar, oyunun sayacına göre (AC, ACC) veya başlangıç noktasından yeniden geçilerek (AC EVO, AC Rally) hesaplanır; tur kaydedici için `kunos.py`'nin yaptığı gibi.

#### Her şey saklanır {#everything-kept}

Satırlar saniyede birkaç tanedir; oyunlar çok daha fazlasını gönderir. Porta gelen her UDP paketi (menülerde, turlar arasında, hiçbir çözücünün okumadığı paketler dahil) oturumun `heat.raw.parquet` dosyasında, biçimi altında (`dash-horizon`, `session_update`, `extradata3`, `H3D1`, ...) bütün olarak saklanır. Değişen her paylaşılan bellek sayfası da (yalnızca çözülen baytlar değil, bütün eşleme), eşleme adı altında (`acpmf_physics`, ...) her değiştiğinde saklanır. `used` satırlara da dönüşenleri işaretler; `meta.json` içindeki `selfCheck.completeness` her türü sayar (3DHeat'in dönüştürücü kuralı).

Bu modül şunlara da hizmet eder: [Assetto Corsa Competizione (canlı veri)](game-assetto-corsa-competizione.md), [Assetto Corsa EVO (canlı veri)](game-assetto-corsa-evo.md), [Assetto Corsa Rally (canlı veri)](game-assetto-corsa-rally.md), [BeamNG.drive (canlı veri)](game-beamng.md), [DiRT Rally 2.0 (canlı veri)](game-dirt-rally-2.md), [EA SPORTS WRC (canlı veri)](game-ea-wrc.md), [Forza Horizon 4 (canlı veri)](game-forza-horizon-4.md), [Forza Horizon 5 (canlı veri)](game-forza-horizon-5.md), [Forza Horizon 6 (canlı veri)](game-forza-horizon-6.md), [Forza Motorsport (canlı veri)](game-forza-motorsport.md), [Richard Burns Rally (canlı veri)](game-richard-burns-rally.md).

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

`best_lap`, `best_stage`, `distance_km`, `laps`, `race_position`, `stages`, `top_speed_kmh`

Süslü parantez içindeki bir anahtar çalışma zamanında tamamlanır (`score.{team}` her takım için ayrı bir anahtardır). Kodun oyunun alan tablosundan veya oyunun kendi istatistik adlarından aldığı anahtarlar bu listede yer almaz; yukarıdaki "Ne kaydedilir" bölümü onları adlandırır.

## Tamlık {#completeness}

İzleyici 3DHeat'in [dönüştürücü kuralını](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md) izler: kaynağın tuttuğu her şey okunur veya saklanır, hiçbir şey atılmaz. Satırların yanında, uyarlayıcının aldığı her paket, sayfa, satır veya yanıt oturumun `heat.raw.parquet` dosyasında bütün olarak saklanır (sütunlar `time`, `ms`, `type`, `used`, `payload`, `text` ve ada göre tutulan her alan; `used` satırlara da dönüşenleri işaretler). `meta.json` içindeki `selfCheck.completeness` her `type` değerini sayar; `lost` 0'dır.

**Okunan**

- ana bellek sayfasından saniyede 10 satır: konum (lastik temas noktalarının ortalaması), hız, vites, gaz, fren, yalpa/yunuslama/yuvarlanma (rad), devir, direksiyon (sayfanın tuttuğu haliyle); statik sayfadan pist ve arabayla oturum başlangıcı; turlar, yarış konumu

**Ham olarak saklanan**

- her sayfa bütün olarak - yalnızca çözülen baytlar değil, tam eşleme bölgesi - baytları her değiştiğinde, izleyicinin saniyede 10 okumasında: `acpmf_physics`, `acpmf_graphics`, `acpmf_static`; bir okuma bir öncekiyle bayt bayt aynıysa, meta.json içindeki `unchanged_reads` sayılır, yeniden saklanmaz
- yalnızca tur dosyaları için çözülen her şey (`decoders/kunos.py`: tekerlek başına kayma, yük, basınç, sıcaklık, kamber, süspansiyon, temas noktaları, fren sıcaklıkları, kayma oranı ve açısı; dünya ve yerel hız, açısal hız, yardımcılar) bu sayfalarda bulunur

**Mevcut olmayan**

- diğer arabaların konumları: sayfalar yalnızca oyuncunun arabasını tarif eder (ACC'nin grafik sayfasında bazı sürümlerde diğer arabaların kimlikleri ve koordinatları vardır - ham sayfada saklanır, çözülmez)
- izleyicinin okumaları arasındaki fizik tikleri: oyun sayfayı kendi fizik hızında (333 Hz'e kadar) yeniden yazar, izleyici ise saniyede 10 kez okur

**Boyut**: sıkıştırmadan önce saatte yaklaşık 150-300 MB (sayfa başına 4 KB bölge, saniyede en fazla 10 değişiklik); sayfalar çoğunlukla sıfırdır ve zstd küçük bir kısmını tutar

## Doğrulama {#verified}

çözümleme gamecapture'ın tur kaydedicisinin çözümlemesidir (sentetik sayfalarda test edildi); uyarlayıcı, testte yerleşime göre kurulan paylaşılan bellekte test edildi; oyunda test edilmedi

## Kaynak {#source}

[heat3d_watch/adapters/racing.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/racing.py)

<!-- Adaptörden tools/gen_game_pages.py ile üretilmiştir; sayfayı elle düzenlemek yerine adaptörü değiştirin ve yeniden çalıştırın. -->
