---
title: "iRacing (canlı veri)"
nav_order: 28
lang: "tr"
source: game-iracing.md
source_hash: "894d9bc4081f"
nav_exclude: true
search_exclude: true
---
# iRacing (canlı veri) {#iracing-live-data}

iRacing oynarken izleyici, oyunun dışarıya gönderdiği verileri kaydeder; böylece bu verilere daha sonra istatistikler ve bir zaman çizelgesi olarak bakabilirsiniz.

*Teknik ayrıntılar: uyarlayıcı `iracing`, tür [`telemetry`](sources-and-rules.md); `iRacingSim64DX11.exe` veya `iRacingSim64.exe` çalışırken çalışır ve her 0,1 saniyede bir yeni veri arar.*

## Ne kaydedilir {#what-is-recorded}

- sürüş, saniyede 5 kez, konum olmadan (iRacing canlı konum vermez): hız, vites, gaz, fren, tur, turun payı, yarış ve sınıf konumu, olaylar
- oturum başlangıcı, arabaya binme ve inme, pit şeridine giriş ve çıkış, tur süresiyle turlar, puanlarıyla olaylar, damalı bayrak, bitiş
- oturum sırasında yazılan .ibt telemetri dosyaları (enlem, boylam, yükseklik - görüntüleyici bunları okur)
- turlar, en iyi tur, olaylar, yarış konumu, pit durakları, mesafe, en yüksek hız
- bütün paylaşılan bellek heat.raw.parquet içinde: başlık, değişken başlıkları, oturum bilgisi, okunan her telemetri satırı

## Veri nereden gelir {#where-it-comes-from}

paylaşılan bellek Local\IRSDKMemMapFileName (iRacing SDK); .ibt dosyaları %USERPROFILE%\Documents\iRacing\telemetry içinde

## Nasıl açılır {#how-to-switch-it-on}

Canlı veri için bir şey açmanız gerekmez. Konumlar için: arabada telemetriyi kaydedin (Alt+L) veya app.ini içinde irsdkLog=1 yapın

## Nasıl çalışır {#how-it-works}

iRacing, canlı: iRacing SDK'sının paylaşılan belleği, yerel olarak okunur.

iRacing telemetrisini uygulamalar için adlandırılmış bir dosya eşlemesinde, `Local\IRSDKMemMapFileName` içinde yayınlar; simülasyon çalışırken bunu oluşturur ve her güncellemede `Local\IRSDKDataValidEvent` olayını sinyalle (burada gerekmez: izleyici saniyede on kez bakar). Düzen SDK'nın `irsdk_defines.h` dosyasıdır; pyirsdk (MIT) de aynısını izler - buradaki kod bu bilgilerden yeniden yazılmıştır:

```text
irsdk_header (little-endian int32s)
    0 ver, 4 status (bit 0: connected), 8 tickRate,
    12 sessionInfoUpdate, 16 sessionInfoLen, 20 sessionInfoOffset,
    24 numVars, 28 varHeaderOffset, 32 numBuf, 36 bufLen, 40 pad[2],
    48 varBuf[4]: { tickCount, bufOffset, pad[2] } (16 bytes each)
irsdk_varHeader (144 bytes, numVars of them at varHeaderOffset)
    0 type (0 char, 1 bool, 2 int, 3 bitfield, 4 float, 5 double),
    4 offset (into a line), 8 count, 12 countAsTime + 3 pad,
    16 name[32], 48 desc[64], 112 unit[32]
session info: YAML text at sessionInfoOffset, rewritten when
    sessionInfoUpdate changes (track, sessions, drivers)
```

Simülasyon `numBuf` satırı sırayla yazar; en yenisi en yüksek tickCount değerine sahip olandır ve kopyalanırken tickCount'u değişen bir satır yeniden alınır.

Canlı veride dünya konumu yoktur - enlem, boylam ve yükseklik yalnızca iRacing'in `Documents\iRacing\telemetry` klasörüne kaydettiği .ibt dosyalarındadır (arabada Alt+L veya `irsdkLog=1`), bunları 3DHeat görüntüleyicisi kendisi okur. Bu yüzden izleyici sürüşü koordinatsız olaylar olarak kaydeder: hız, tur, turun yapılan payı, yarış konumu, olaylar - ayrıca turlar, olaylar, pit durakları ve damalı bayrak; ve sonunda oturum sırasında yazılan .ibt dosyaları, görüntüleyicinin açması için `telemetry_file` olayları olarak.

Satırların yanında bütün bellek haritası, oturumun ham yan dosyasında (`heat.raw.parquet`) saklanır: başlığın sabit kısmı (`header`, her değiştiğinde), değişken başlıkları (`var_headers`, bütün olarak ve `text` içinde JSON olarak, düzen her değiştiğinde), oturum bilgisi YAML'ı (`session_info`, metni `sessionInfoUpdate` değeri her değiştiğinde) ve en yeni telemetri satırı (`telemetry`, her değişkeniyle birlikte, yeni bir tik bulan her okumada). Değişken başlıkları ve bir satır, sonraki bir çözücünün herhangi bir değişkeni okuması için yeterlidir.

Kaynak: iRacing SDK (irsdk_defines.h, "iRacing SDK" forum belgeleri); ofsetleri doğrulamak için kutu/pyirsdk (MIT).

## Konumlar ve eksenler {#positions-and-axes}

| | |
|---|---|
| Konumlar kaydedilir | hayır |
| Yukarı eksen | `y` |
| Birimler | canlı konum yok; .ibt dosyaları enlem/boylam/yükseklik taşır |
| Görüntüleyici için aynalama | yok |
| Birim ölçeği (`scale`: görüntüleyici konumları bununla çarpar) | 1 |

Bunlar her oturumun `meta.json` dosyasındaki (`axes`) ve oturumda konum varsa `heat.parquet` dosyasının altbilgisine yazılır; böylece 3DHeat görüntüleyicisi satırları kendi başına döndürür ve ölçekler. Bkz. [Veriler](the-data.md).

## Çok oyunculu {#multiplayer}

- Çevrimiçi oynanan olarak işaretli (`multiplayer`): **evet**. `games --markdown` bunu "izinli (yalnızca oyunun yayınladığını okur)" olarak gösterir.
- Tür `telemetry`: yalnızca oyunun veya platformun dışarı verdiğini okur (oyunun yayınladığı bir UDP portu veya paylaşılan bellek); bu yüzden çevrimiçi oyunda da kaydeder. Bayrak yalnızca belleğin hiç okunup okunamayacağını belirler.
- Bellek: bu uyarlayıcı **asla** okumaz. Yalnızca `memory` uyarlayıcıları bellek okur ve çevrimiçi oynanan olarak işaretli bir oyun için hiçbir zaman. Bkz. [Kaynaklar ve kurallar](sources-and-rules.md).

## Kaydedilen istatistikler {#statistics-recorded}

Bu uyarlayıcının kodunun ada göre ayarladığı istatistik anahtarları (her oturumun `meta.json` dosyasındaki `stats` ve `watcher.sqlite` dosyasındaki `stats` tablosu):

`best_lap`, `distance_km`, `finishes`, `incidents`, `laps`, `pit_stops`, `race_position`, `sessions`, `top_speed_kmh`

Süslü parantez içindeki bir anahtar çalışma zamanında tamamlanır (`score.{team}` her takım için ayrı bir anahtardır). Kodun oyunun alan tablosundan veya oyunun kendi istatistik adlarından aldığı anahtarlar bu listede yer almaz; yukarıdaki "Ne kaydedilir" bölümü onları adlandırır.

## Tamlık {#completeness}

İzleyici 3DHeat'in [dönüştürücü kuralını](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md) izler: kaynağın tuttuğu her şey okunur veya saklanır, hiçbir şey atılmaz. Satırların yanında, uyarlayıcının aldığı her paket, sayfa, satır veya yanıt oturumun `heat.raw.parquet` dosyasında bütün olarak saklanır (sütunlar `time`, `ms`, `type`, `used`, `payload`, `text` ve ada göre tutulan her alan; `used` satırlara da dönüşenleri işaretler). `meta.json` içindeki `selfCheck.completeness` her `type` değerini sayar; `lost` 0'dır.

**Okunan**

- en yeni telemetri satırından: oturum süresi, numara, durum ve kimlik, pistte, tekrar, tur, tamamlanan turlar, turun payı ve metresi, son ve en iyi tur, hız, vites, gaz, fren, devir, pit yolu, pist yüzeyi, yarış ve sınıf konumu, arabanın kendi olay sayısı (saniyede 5 `driving` satırı ve olaylar)
- şimdi `driving` satırlarında da: `steering_angle`, `yaw`, `yaw_north`, `pitch`, `roll` (derece, simülasyonun radyanlarından - yalnızca değişken başlığı birimi rad olarak verdiğinde), `fuel_l` (birim l), `lat_accel` ve `lon_accel` (birim m/s^2)
- oturum bilgisi YAML'ından: oyuncunun araba sırası, pist ve konfigürasyonu, oturum türleri, her sürücünün adı, arabası, takımı ve numarası (session_start satırları, meta.json)
- testlerde irsdk_defines.h'den kurulan bir blokla kontrol edildi; henüz simülasyonla kontrol edilmedi

**Ham olarak saklanan**

- `telemetry`: en yeni satır bütün olarak, simülasyonun yayınladığı her değişken (her arabanın CarIdx dizileri, lastikler, süspansiyon, yüksek hızlı `_ST` dizileri nerede varsa ...), yeni bir tik bulan her okumada; `tick` simülasyonun tik sayısı; bir tekrar oynatılırken `used` yanlıştır
- `var_headers`: değişken başlıkları bütün olarak (her biri 144 bayt) ve `text` içinde JSON olarak (ad, tür, ofset, sayı, birim, açıklama), düzen her değiştiğinde - saklanan her satırın her değişkenini okumak için yeterli
- `session_info`: YAML metni bütün olarak, güncelleme sayacı her hareket ettiğinde (hafta sonu, oturumlar ve sonuçlar, sürücüler, araba ayarı, telsiz, kamera listeleri), `update` sayacın kendisi
- `header`: 112 baytlık irsdk başlığı bütün olarak, her değiştiğinde (sürüm, durum, tik hızı, ofsetler, satırların tikleri)

**Mevcut olmayan**

- canlı dünya konumu: paylaşılan bellekte yoktur; enlem, boylam ve yükseklik yalnızca .ibt dosyalarındadır (kayıt açıkken), görüntüleyici bunları okur - izleyici oturum sırasında yazılanları adlandırır
- iki okuma arasındaki tikler: simülasyon saniyede 60 satırı 3 veya 4 yuvaya yazar ve izleyici saniyede 10 kez okur; bu yüzden tiklerin çoğu okunamadan üzerine yazılır; kayıt açıkken .ibt dosyası her tiki içerir

**Boyut**: bir telemetri satırı birkaç KB'dır (her arabanın dizileriyle birlikte yaklaşık 5-10 KB), saniyede en fazla 10 kez saklanır; ayrıca başlık (112 bayt) aynı sıklıkta ve oturum bilgisi YAML'ı (on KB'lar) değiştiğinde: pistte saatte yaklaşık 0,2-0,4 GB, sıkıştırmadan önce; zstd bunu küçük bir bölüme indirir (gerçek bir oturumda henüz ölçülmedi)

## Doğrulama {#verified}

test içinde irsdk düzeninden kurulan bir paylaşılan bellek bloğunda test edildi; simülasyonda test edilmedi

## Kaynak {#source}

[heat3d_watch/adapters/iracing.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/iracing.py)

<!-- Adaptörden tools/gen_game_pages.py ile üretilmiştir; sayfayı elle düzenlemek yerine adaptörü değiştirin ve yeniden çalıştırın. -->
