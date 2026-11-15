---
title: "X-Plane (canlı veri)"
nav_order: 49
lang: "tr"
source: game-xplane.md
source_hash: "be1c5b21d2ef"
nav_exclude: true
search_exclude: true
---
# X-Plane (canlı veri) {#x-plane-live-data}

X-Plane oynarken izleyici, oyunun dışarıya gönderdiği verileri kaydeder; böylece bu verilere daha sonra 3DHeat görüntüleyicisinde bir harita üzerinde bakabilirsiniz.

*Teknik ayrıntılar: uyarlayıcı `xplane`, tür [`telemetry`](sources-and-rules.md); `X-Plane.exe` çalışırken çalışır ve her 0,1 saniyede bir yeni veri arar.*

## Ne kaydedilir {#what-is-recorded}

- kendi konumunuz, saniyede 10 kez (enlem/boylam/yükseklik, ilk ölçümden itibaren metre olarak doğu/yukarı/kuzey; lat/lon/alt sütun olarak saklanır)
- tutum, gösterilen ve gerçek hava hızı, yer hızı, Mach, dikey hız, AoA, kayma, manyetik yön, AGL, g (normal, eksenel, yan), hız ve dönme oranları, flaplar, hava freni, gaz, yerde olma
- ağırlıklar (toplam, yakıt, yük), iniş takımı kolu, otopilot, motor devri ve N1, simülasyon zamanı ve tarihi, duraklatma, simülasyon hızı, tekrar, dış hava sıcaklığı ve deniz seviyesi basıncı (X-Plane 12) saniyede bir
- kalkışlar, inişler, kazalar, uçuş sıfırlamaları (her uçuş için session_start/session_end)
- uçuş süresi, havada geçen süre, mesafe, en yüksek irtifa, en yüksek g, inişler
- X-Plane'in gönderdiği her yanıt heat.raw.parquet içinde bütün olarak

## Veri nereden gelir {#where-it-comes-from}

X-Plane'in UDP arayüzü, 127.0.0.1:49000 (RREF veri referansları ve RPOS konumu, izleyiciye yanıt olarak)

## Nasıl açılır {#how-to-switch-it-on}

X-Plane 12: Ayarlar > Ağ > Gelen bağlantıları kabul et (X-Plane 11 varsayılan olarak yanıt verir)

## Nasıl çalışır {#how-it-works}

X-Plane 11 ve 12: simülasyonun kendi UDP arayüzü, port 49000.

X-Plane, 127.0.0.1:49000 üzerinden soran herkese, istenen hızda yanıt verir; yanıtı isteğin geldiği adres ve porta gönderir (X-Plane'in "Exchanging Data with X-Plane" belgesi, `<X-Plane>\Instructions\` klasöründe gelir):

```text
RREF  "RREF\0" + int32 freq + int32 index + char[400] dataref path (413 bytes).
      The answer is "RREF" + one internal byte + (int32 index, float32 value)
      pairs; freq 0 stops it.
RPOS  "RPOS\0" + the rate as a NUL-terminated ASCII string ("10\0"). The
      answer is "RPOS" + one internal byte + double lon, lat, elevation (m
      MSL) + float AGL (m), pitch, true heading, roll (deg), vx east, vy up,
      vz south (m/s), P, Q, R (rad/s), tightly packed.
```

RPOS enlemi ve boylamı çift duyarlıklı sayılar olarak verir (RREF yalnızca float olarak, yarım metre kadar uzakta), bu yüzden konumu RPOS yönlendirir; RREF geri kalanı getirir ve RPOS gelmediğinde onun yerini tutar. Veri referansları (adlar X-Plane 12'nin `Resources\plugins\DataRefs.txt` dosyasındaki gibi, <https://developer.x-plane.com/datarefs/>):

```text
sim/flightmodel/position/latitude, longitude, elevation  deg, deg, m MSL
sim/flightmodel/position/true_theta, true_phi, true_psi  pitch, roll, true heading (deg)
sim/flightmodel/position/indicated_airspeed              knots
sim/flightmodel/position/groundspeed                     m/s
sim/flightmodel/position/y_agl                           m above ground
sim/flightmodel/forces/g_nrml                            g, normal to the wings
sim/flightmodel/failures/onground_any                    1 on the ground
sim/flightmodel2/misc/has_crashed                        1 crashed
sim/time/total_flight_time_sec                           since the flight was reset
```

Uçuşun geri kalanı (gerçek hava hızı, dikey hız, AoA, kayma, manyetik yön, Mach, eksenel ve yan g, dönme oranları, flaplar, hava freni, gaz: `DATAREFS`) aynı hızda, uçağın daha yavaş değişen durumu (ağırlıklar, iniş takımı kolu, otopilot, motorlar, simülasyonun zamanı, duraklatma ve hız, hava durumu: `SLOW_DATAREFS`) ise saniyede bir gelir. Her datagram oturumun ham yan dosyasında bütün olarak saklanır ve meta.json her RREF indeksinin hangi veri referansı olduğunu adlandırır.

X-Plane 12 bunları yalnızca Ayarlar > Ağ > "Gelen bağlantıları kabul et" açıkken kabul eder. Konumlar, oturumun ilk ölçümü etrafında (`Tangent`) düz bir haritaya konur: x doğu, z kuzey, metre, y deniz seviyesinden yükseklik - böylece seyir düz kalır, ne kadar giderse gitsin; gerçek bir teğet düzlem ise yeryuvarlağıyla birlikte aşağı eğilirdi. Haritanın başlangıcı oturumun `geo` değeridir: meta.json ve tablonun altbilgisi bunu taşır, böylece görüntüleyici gerçek dünyayı uçuşun altına yerleştirebilir.

Bu modül ayrıca öteki uçuş simülasyonlarının ortak kullandıklarını da barındırır: düz harita, uçuş kayıt tutma (kalkışlar, inişler, kazalar, mesafe), UDP soketi ve Steam kütüphanesi listesi.

## Konumlar ve eksenler {#positions-and-axes}

| | |
|---|---|
| Konumlar kaydedilir | evet |
| Yukarı eksen | `y` |
| Birimler | metre (doğu, yükseklik, ilk ölçümden itibaren kuzey) |
| Görüntüleyici için aynalama | `z` |
| Birim ölçeği (`scale`: görüntüleyici konumları bununla çarpar) | 1 |

Bunlar her oturumun `meta.json` dosyasındaki (`axes`) ve oturumda konum varsa `heat.parquet` dosyasının altbilgisine yazılır; böylece 3DHeat görüntüleyicisi satırları kendi başına döndürür ve ölçekler. Bkz. [Veriler](the-data.md).

## Çok oyunculu {#multiplayer}

- Çevrimiçi oynanan olarak işaretli (`multiplayer`): **hayır**. `games --markdown` bunu "tek oyunculu" olarak gösterir.
- Tür `telemetry`: yalnızca oyunun veya platformun dışarı verdiğini okur (oyunun yayınladığı bir UDP portu veya paylaşılan bellek); bu yüzden çevrimiçi oyunda da kaydeder. Bayrak yalnızca belleğin hiç okunup okunamayacağını belirler.
- Bellek: bu uyarlayıcı **asla** okumaz. Yalnızca `memory` uyarlayıcıları bellek okur ve çevrimiçi oynanan olarak işaretli bir oyun için hiçbir zaman. Bkz. [Kaynaklar ve kurallar](sources-and-rules.md).

## Kaydedilen istatistikler {#statistics-recorded}

Bu uyarlayıcının kodunun ada göre ayarladığı istatistik anahtarları (her oturumun `meta.json` dosyasındaki `stats` ve `watcher.sqlite` dosyasındaki `stats` tablosu):

`airborne_time`, `bad_packets`, `crashes`, `distance_km`, `flight_time`, `max_altitude_m`, `max_g`, `{event}s`

Süslü parantez içindeki bir anahtar çalışma zamanında tamamlanır (`score.{team}` her takım için ayrı bir anahtardır). Kodun oyunun alan tablosundan veya oyunun kendi istatistik adlarından aldığı anahtarlar bu listede yer almaz; yukarıdaki "Ne kaydedilir" bölümü onları adlandırır.

## Tamlık {#completeness}

İzleyici 3DHeat'in [dönüştürücü kuralını](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md) izler: kaynağın tuttuğu her şey okunur veya saklanır, hiçbir şey atılmaz. Satırların yanında, uyarlayıcının aldığı her paket, sayfa, satır veya yanıt oturumun `heat.raw.parquet` dosyasında bütün olarak saklanır (sütunlar `time`, `ms`, `type`, `used`, `payload`, `text` ve ada göre tutulan her alan; `used` satırlara da dönüşenleri işaretler). `meta.json` içindeki `selfCheck.completeness` her `type` değerini sayar; `lost` 0'dır.

**Okunan**

- RPOS (10 Hz): boylam, enlem, yükseklik, AGL, pitch, gerçek yön, roll, hız (doğu, yukarı, güney) ve dönme oranları P/Q/R - hepsi satırlarda
- RREF (10 Hz): `DATAREFS`'in 27 veri referansı - konum, tutum, IAS, yer hızı, TAS, dikey hız, AoA, kayma, manyetik yön, Mach, g normal/eksenel/yan, dönme oranları, flaplar, hava freni, gaz, AGL, kaza, yerde, uçuş süresi - satırlarda
- RREF (1 Hz): `SLOW_DATAREFS`'in 20 veri referansı - ağırlıklar, iniş takımı kolu, otopilot servoları, simülasyon zamanı ve tarihi, duraklatma, simülasyon hızı, tekrar, motor sayısı, 1-4 numaralı motorların devri, 1-2 numaralı motorların N1'i, dış hava sıcaklığı, deniz seviyesi basıncı - son alınan haliyle satırlarda

**Ham olarak saklanan**

- her datagram bütün olarak `payload` olarak, dört harfli başlığı altında: `RREF` ve `RPOS` (sorgu bir satır yaptığında kullanılır; bir konum olmadan menülerde satır yapmazlar), X-Plane'in izleyicinin portuna gönderdiği diğer her şey kendi başlığı altında veya `unknown`; meta.json'ın `requests` alanı her RREF indeksinin hangi veri referansı olduğunu söyler, böylece yükler bu modül olmadan okunur

**Mevcut olmayan**

- diğer her veri referansı (X-Plane binlercesine sahiptir): RREF yalnızca istenenleri gönderir, her abonelik için bir tane; liste uçuşu, uçağın durumunu ve simülasyon zamanını ister - daha fazla kokpit ayrıntısı (radyolar, ışıklar, her motorun göstergeleri, arızalar) istekleri çoğaltırdı
- uçağın adı ve ICAO tipi: bayt dizisi veri referansları, RREF bunları karakter başına bir float olarak gönderir
- diğer uçaklar (AI ve çok oyunculu): istenmeyen sim/multiplayer/position veri referansları
- Veri Çıktısı (Ayarlar > Veri Çıktısı): simülasyonda seçilen sabit bir adrese gönderir, isteyene değil; RREF ve RPOS izleyicinin okuduğu her şeyi kapsar

**Boyut**: RREF ve RPOS 10 Hz'de, sırasıyla yaklaşık 220 ve 70 bayt artı çerçeve (yavaş RREF saniyede bir), X-Plane her sorgunun değerlerini tek pakette gönderdiğinde, zstd öncesinde saatte yaklaşık 17 MB; zstd floatları birkaç kez küçültür

## Doğrulama {#verified}

X-Plane 12'nin 'Exchanging Data with X-Plane' belgesine göre RREF/RPOS yanıtlayan sahte bir X-Plane'e karşı test edildi; veri referansı adları X-Plane 12'nin DataRefs.txt dosyasına göre denetlendi; çalışan simülasyonda test edilmedi

## Kaynak {#source}

[heat3d_watch/adapters/xplane.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/xplane.py)

<!-- Adaptörden tools/gen_game_pages.py ile üretilmiştir; sayfayı elle düzenlemek yerine adaptörü değiştirin ve yeniden çalıştırın. -->
