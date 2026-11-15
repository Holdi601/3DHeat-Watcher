---
title: "RaceRoom Racing Experience (canlı veri)"
nav_order: 37
lang: "tr"
source: game-raceroom.md
source_hash: "f3879cd40a67"
nav_exclude: true
search_exclude: true
---
# RaceRoom Racing Experience (canlı veri) {#raceroom-racing-experience-live-data}

RaceRoom Racing Experience oynarken izleyici, oyunun kendi gönderdiği verileri kaydeder; böylece bu verilere daha sonra 3DHeat görüntüleyicisinde bir harita üzerinde bakabilirsiniz.

*Teknik ayrıntılar: bağdaştırıcı `raceroom`, tür [`telemetry`](sources-and-rules.md); `RRRE64.exe` ya da `RRRE.exe` çalışırken çalışır ve yeni veri için her 0,1 saniyede bir bakar.*

## Ne kaydedilir {#what-is-recorded}

- her arabanın konumu (dünya XYZ, m), 10 Hz ile, sürücü adına göre; kendi arabanız işaretli; hız ve yarış sırasıyla; kendi vitesiniz, gazınız, freniniz
- oyunun adlandırdığı pistle oturumun başlangıcı; her araba için tur süresiyle turlar; bitirişler; kendi pit duraklamalarınız
- ışınlanmalar (pite geri dönme, yeniden başlatma): arabanın olduğu yer için `teleport`, arabanın şimdi olduğu yer için `spawn`
- kendi turlarınız, en iyi tur, yarış sırası, mesafe, en yüksek hız
- oyunun bütün paylaşılan bellek sayfası, her değiştiğinde `heat.raw.parquet` içinde
- kendi olay (incident) puanlarınız

## Kaynağı {#where-it-comes-from}

paylaşılan bellek $R3E (Sector3'ün r3e.h dosyası, sürüm 3)

## Nasıl açılır {#how-to-switch-it-on}

Hiçbir şeyi açmanız gerekmez: izleyici kaynağı, oyunun ya da platformun sunduğu haliyle okur.

## Nasıl çalışır {#how-it-works}

Gösterge panelleri için yarış oyunlarının yayımladığı paylaşılan bellek; salt okunur açılır ve asla oluşturulmaz.

Birkaç simülasyon telemetrisini, oyunun oluşturup herkesin okuyabildiği adlandırılmış bir Windows dosya eşlemesi olarak sunar: Kunos'un `Local\acpmf_*` sayfaları (Assetto Corsa, ACC, AC Rally, AC EVO'nun `Local\acevo_pmf_*` sayfaları), iRacing'in `Local\IRSDKMemMapFileName`'i, RaceRoom'un `$R3E`'si, Automobilista 2 / Project CARS 2'nin `$pcars2$`ı.

Neden `mmap.mmap(-1, size, tagname=...)` değil, Python'da alışılmış yol bu: eşleme henüz yoksa bir tane *oluşturur* - burada salt okunur olarak. Sonra başlayan bir oyun kendi eşlemesini yapmak yerine izleyicinin eşlemesini açar ve ona yazamaz; bu yüzden izleyici portu bırakana kadar telemetrisi ölü kalır. İzleyici bir bağdaştırıcıyı, oyunun işlemi göründüğü anda başlatır; tam da oyunun henüz eşlemesini yapmadığı andır. Bu yüzden burada `OpenFileMappingW` ile açılır: yalnızca var olan bir eşlemeyi bulur, onu `FILE_MAP_READ` ile eşler, bulamazsa "henüz yok" der; bağdaştırıcılar kısa bir süre sonra yeniden dener.

Buradaki hiçbir şey yazamaz: görünüm salt okunur eşlenir ve yalnızca `ctypes.string_at` ile kopyalanarak okunur.

Burada iki oyun daha okunur; pistteki her araba onların sayfalarındadır.

#### RaceRoom Racing Experience - `$R3E` {#raceroom-racing-experience---r3e}

Sector3'ün `r3e.h` dosyası (github.com/sector3studios/r3e-api, sample-c/src/r3e.h, sürüm 3.6), `#pragma pack(1)`. Başlık sürücülerin nerede başladığını ve birinin ne kadar büyük olduğunu söyler (`all_drivers_offset`, `driver_data_size`); bu yüzden sürücülerin bölümü - ad, yuva, sıra, dünya konumu (float x y z, m), tamamlanan turlar, geçerli tur süresi, bitiriş durumu, pit şeridi, hız - bunlarla okunur. Oyuncunun kendi alanları (en iyi ve önceki tur, yarış sırası, olay puanları, vites, pedallar, pist ve düzen adları) yalnızca `all_drivers_offset` düzenin koyduğu 2008 olduğunda, 3.6 ofsetlerinde okunur. Y'nin yukarı olduğu varsayılır; başlık bunu söylemez.

Bu modülün sunduğu diğer sayfalar: [Automobilista 2 (canlı veri)](game-automobilista-2.md), [Project CARS 2 (canlı veri)](game-project-cars-2.md).

## Konumlar ve eksenler {#positions-and-axes}

| | |
|---|---|
| Kaydedilen konumlar | evet |
| Yukarı ekseni | `y` |
| Birimler | metre; Y yukarı varsayılır (r3e.h bunu söylemez) |
| Görüntüleyici için aynalama | yok |
| Birim ölçeği (`scale`: görüntüleyici konumları bununla çarpar) | 1 |

Bunlar her oturumun `meta.json` dosyasındaki (`axes`) ve konum içeren oturumlarda `heat.parquet` dosyasının sonundaki (footer) bilgiye yazılır; böylece 3DHeat görüntüleyicisi satırları kendisi döndürür ve ölçekler - bkz. [Veriler](the-data.md).

## Çok oyunculu {#multiplayer}

- Çevrimiçi oynanan olarak işaretlenmiş (`multiplayer`): **evet**. `games --markdown` bunu "izinli (yalnızca oyunun yayımladığını okur)" olarak gösterir.
- Tür `telemetry`: yalnızca oyunun ya da platformun dışarı verdiğini okur (oyunun yayımladığı bir UDP portu ya da paylaşılan bellek). Bu yüzden çevrimiçi oyunda da çevrimdışı olduğu gibi kaydeder; bayrak yalnızca belleğin hiç okunup okunamayacağını belirler.
- Bellek: bu bağdaştırıcı **asla** okumaz. Yalnızca `memory` bağdaştırıcıları bellek okur ve çevrimiçi oynanan olarak işaretlenmiş bir oyun için asla okumaz - bkz. [Kaynaklar ve kurallar](sources-and-rules.md).

## Kaydedilen istatistikler {#statistics-recorded}

Bu bağdaştırıcının kodunun adla ayarladığı istatistik anahtarları (her oturumun `meta.json` içindeki `stats` ve `watcher.sqlite` içindeki `stats` tablosu):

`best_lap`, `distance_km`, `finishes`, `incidents`, `laps`, `pit_stops`, `race_position`, `top_speed_kmh`

Parantez içindeki bir anahtar çalışma zamanında tamamlanır (`score.{team}` her takım için bir anahtardır). Kodun oyunun alanlarının tablosundan ya da oyunun kendi istatistik adlarından aldığı anahtarlar bu listede yer almaz; yukarıdaki "Ne kaydedilir" bölümü bunları adlandırır.

## Tamlık {#completeness}

İzleyici 3DHeat'in [dönüştürücü kuralını](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md) izler: kaynağın tuttuğu her şey okunur ya da saklanır, asla atılmaz. Satırların yanı sıra, bağdaştırıcının aldığı her paket, sayfa, satır ya da yanıt, oturumun `heat.raw.parquet` dosyasında bütün olarak saklanır (sütunlar `time`, `ms`, `type`, `used`, `payload`, `text` ve adla saklanan her alan; `used` satıra dönüşenleri işaretler). `meta.json` içindeki `selfCheck.completeness` her `type` değerini sayar - `lost` 0'dır.

**Okunan**

- sürücü yuvası başına (başlığın kendi ofseti ve boyutuyla): ad, yuva, bitiriş durumu, sıra, dünya konumu, tamamlanan tur sayısı, geçerli tur süresi, pit şeridi, hız
- oyuncunun kendi alanları, yalnızca sayfa r3e.h 3.6 düzeniyse: pist ve düzen adları, oturum türü, yarış sırası, en iyi ve önceki tur, olay puanları, vites, gaz, fren, oyuncunun yuvası
- ofsetler, Sector3'ün r3e.h 3.6 dosyasından çıkarıldı ve ondan kurulan bir sayfa üzerinde testlerde kontrol edildi; henüz oyuna karşı değil

**Ham olarak saklanan**

- `r3e`: bütün $R3E eşlemesi, bir önceki kopyayla bayt bayt farklı olan her okuma - r3e.h'nin her alanı: oyuncunun fiziği (yönelim, hızlar, ivmeler, g-kuvvetleri), motor, yakıt, lastikler, frenler, hasar, bayraklar, pit menüsü, sektör süreleri, her sürücü yuvasının bütün sürücü verisi (sınıf, model, takım, sektör süreleri, aralıklar, cezalar, lastikler)
- `used` bir sayfa satırlara okunduğunda doğrudur; menülerdeki, duraklatılmış, tekrardaki, başka bir düzendeki ya da yazılırken yakalanmış bir sayfa için yanlıştır (`torn` 1); meta.json içindeki `unchanged_reads`, önceden saklanan kopyayla bayt bayt aynı olan okumaları sayar

**Kullanılamayanlar**

- diğer sürücülerin girdileri ve fiziği: sayfa yalnızca oyuncunun kendisini verir
- diğer arabaların kesin tur süreleri: bir yuvada yalnızca çalışan tur süresi vardır, bu yüzden bir tur, görülen son çalışan süredir (yaklaşık 0,1 sn'ye kadar)
- 3.6 dışındaki bir düzendeki oyuncu alanları: ham saklanır, doğrulanana kadar okunmaz

**Boyut**: sayfa 44 KB (r3e.h 3.6; eşleme tam 4 KB sayfalara yuvarlanır), sürerken saniyede en fazla 10 kez: sıkıştırmadan önce saat başına yaklaşık 1,6 GB; boş sürücü yuvaları ve değişmeyen alanlar zstd ile çok iyi sıkışır (gerçek bir oturumda henüz ölçülmedi)

## Doğrulama {#verified}

r3e.h 3.6'dan (resmi başlıktan çıkarılan ofsetlerle) bir testte kurulan sayfa üzerinde test edilmiştir; oyunla test edilmemiştir; diğer arabaların tur süreleri görülen son çalışan tur süresidir (yaklaşık 0,1 sn'ye kadar)

## Kaynak {#source}

[heat3d_watch/adapters/simracing_shm.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/simracing_shm.py)

<!-- Adaptörden tools/gen_game_pages.py ile üretilmiştir; sayfayı elle düzenlemek yerine adaptörü değiştirin ve yeniden çalıştırın. -->
