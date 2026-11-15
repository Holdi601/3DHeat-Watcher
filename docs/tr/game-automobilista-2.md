---
title: "Automobilista 2 (canlı veri)"
nav_order: 6
lang: "tr"
source: game-automobilista-2.md
source_hash: "5e3ca1507524"
nav_exclude: true
search_exclude: true
---
# Automobilista 2 (canlı veri) {#automobilista-2-live-data}

Automobilista 2 oynarken izleyici, oyunun kendi gönderdiği verileri kaydeder; böylece bu verilere daha sonra 3DHeat görüntüleyicisinde bir harita üzerinde bakabilirsiniz.

*Teknik ayrıntılar: bağdaştırıcı `automobilista-2`, tür [`telemetry`](sources-and-rules.md); `AMS2AVX.exe` ya da `AMS2.exe` çalışırken çalışır ve yeni veri için her 0,1 saniyede bir bakar.*

## Ne kaydedilir {#what-is-recorded}

- her arabanın konumu (dünya XYZ, m), 10 Hz ile, sürücü adına göre; kendi arabanız işaretli; hız ve yarış sırasıyla; kendi vitesiniz, gazınız, freniniz
- oyunun adlandırdığı pistle oturumun başlangıcı; her araba için tur süresiyle turlar; bitirişler; kendi pit duraklamalarınız
- ışınlanmalar (pite geri dönme, yeniden başlatma): arabanın olduğu yer için `teleport`, arabanın şimdi olduğu yer için `spawn`
- kendi turlarınız, en iyi tur, yarış sırası, mesafe, en yüksek hız
- oyunun bütün paylaşılan bellek sayfası, her değiştiğinde `heat.raw.parquet` içinde

## Kaynağı {#where-it-comes-from}

paylaşılan bellek $pcars2$ (SMS SharedMemory.h düzeni)

## Nasıl açılır {#how-to-switch-it-on}

Oyunda: Options > System > Shared Memory: "Project CARS 2"

## Nasıl çalışır {#how-it-works}

Gösterge panelleri için yarış oyunlarının yayımladığı paylaşılan bellek; salt okunur açılır ve asla oluşturulmaz.

Birkaç simülasyon telemetrisini, oyunun oluşturup herkesin okuyabildiği adlandırılmış bir Windows dosya eşlemesi olarak sunar: Kunos'un `Local\acpmf_*` sayfaları (Assetto Corsa, ACC, AC Rally, AC EVO'nun `Local\acevo_pmf_*` sayfaları), iRacing'in `Local\IRSDKMemMapFileName`'i, RaceRoom'un `$R3E`'si, Automobilista 2 / Project CARS 2'nin `$pcars2$`'ı.

Neden `mmap.mmap(-1, size, tagname=...)` değil, Python'da alışılmış yol bu: eşleme henüz yoksa bir tane *oluşturur* - burada salt okunur olarak. Sonra başlayan bir oyun kendi eşlemesini yapmak yerine izleyicinin eşlemesini açar ve ona yazamaz; bu yüzden izleyici portu bırakana kadar telemetrisi ölü kalır. İzleyici bir bağdaştırıcıyı, oyunun işlemi göründüğü anda başlatır; tam da oyunun henüz eşlemesini yapmadığı andır. Bu yüzden burada `OpenFileMappingW` ile açılır: yalnızca var olan bir eşlemeyi bulur, onu `FILE_MAP_READ` ile eşler, bulamazsa "henüz yok" der; bağdaştırıcılar kısa bir süre sonra yeniden dener.

Buradaki hiçbir şey yazamaz: görünüm salt okunur eşlenir ve yalnızca `ctypes.string_at` ile kopyalanarak okunur.

Burada iki oyun daha okunur; pistteki her araba onların sayfalarındadır.

#### Automobilista 2 / Project CARS 2 - `$pcars2$` {#automobilista-2--project-cars-2---pcars2}

SMS'in `SharedMemory.h` dosyası (oyunun Support\SharedMemory klasöründe gelir; AMS2: Options > System > Shared Memory "Project CARS 2"), `#pragma pack(4)`. `mParticipantInfo[64]` 28. bayttan başlar, her biri 100 bayt: mIsActive, mName[64], mWorldPosition[3] (m, Y yukarı), mCurrentLapDistance, mRacePosition, mLapsCompleted, mCurrentLap, mCurrentSector; mViewedParticipantIndex (20) oyuncunun arabasıdır; her katılımcı için mLastLapTimes (9200), mRaceStates (9520), mSpeeds (10800); oyuncunun mBestLapTime (6716), mLastLapTime (6720), mSpeed (6848), mBrake, mThrottle, mGear; mSequenceNumber (7320) oyun yazarken tektir. Ofsetler başlığın iki bağımsız kopyasından çıkarıldı; bu kopyalar birbiriyle uyuşuyor (oyunun kendi kopyası burada kurulu değil).

İki sayfa da ayrıca bütün olarak saklanır (docs/converters.md, "Live sources"): bütün eşleme, bir önceki kopyayla bayt bayt farklı olan her okuma, oturumun ham yan dosyasında `type` `r3e` ya da `pcars2` olarak - her katılımcı yuvası ve yapının her alanı, burada okunmayanlar dahil; böylece sonraki bir çözücü yalnızca yan dosyaya ihtiyaç duyar.

Bu modülün sunduğu diğer sayfalar: [Project CARS 2 (canlı veri)](game-project-cars-2.md), [RaceRoom Racing Experience (canlı veri)](game-raceroom.md).

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

`best_lap`, `distance_km`, `finishes`, `incidents`, `laps`, `pit_stops`, `race_position`, `top_speed_kmh`

Parantez içindeki bir anahtar çalışma zamanında tamamlanır (`score.{team}` her takım için bir anahtardır). Kodun oyunun alanlarının tablosundan ya da oyunun kendi istatistik adlarından aldığı anahtarlar bu listede yer almaz; yukarıdaki "Ne kaydedilir" bölümü bunları adlandırır.

## Tamlık {#completeness}

İzleyici 3DHeat'in [dönüştürücü kuralını](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md) izler: kaynağın tuttuğu her şey okunur ya da saklanır, asla atılmaz. Satırların yanı sıra, bağdaştırıcının aldığı her paket, sayfa, satır ya da yanıt, oturumun `heat.raw.parquet` dosyasında bütün olarak saklanır (sütunlar `time`, `ms`, `type`, `used`, `payload`, `text` ve adla saklanan her alan; `used` satıra dönüşenleri işaretler). `meta.json` içindeki `selfCheck.completeness` her `type` değerini sayar - `lost` 0'dır.

**Okunan**

- her katılımcı için (en fazla 64): etkin olup olmadığı, ad, dünya konumu, yarış sırası, tamamlanan tur sayısı; son tur süresi, yarış durumu ve hız
- oyuncunun arabası (mViewedParticipantIndex), oyun ve oturum durumu, pist konumu ve varyasyonu, en iyi ve son tur, hız, fren, gaz, vites; yazılırken yakalanan bir kopyayı atlamak için mSequenceNumber
- ofsetler, SMS'in SharedMemory.h dosyasının birbiriyle uyuşan iki bağımsız kopyasından; testlerde bunlarla kurulan bir sayfa üzerinde kontrol edildi; henüz oyuna karşı değil

**Ham olarak saklanan**

- `pcars2`: bütün $pcars2$ eşlemesi - yapı burada okunan 11.312 bayttan çok daha ileri gider - bir önceki kopyayla bayt bayt farklı olan her okuma: her katılımcının yönelimi, sektör süreleri, araba ve sınıf adları, pit modları ve bayrakları, oyuncunun fiziği, lastikler, süspansiyon, hasar, hava durumu ve Automobilista 2'nin sonraki sürümlerinde eklenen her şey
- `used` bir sayfa satırlara okunduğunda doğrudur; menülerdeki, duraklatılmış, tekrardaki, başka bir düzendeki ya da yazılırken yakalanmış bir sayfa için yanlıştır (`torn` 1); meta.json içindeki `unchanged_reads`, önceden saklanan kopyayla bayt bayt aynı olan okumaları sayar

**Kullanılamayanlar**

- diğer katılımcıların girdileri ve fiziği: sayfa yalnızca izlenen arabayı verir
- oyunun paylaşılan bellek seçeneği kapalıyken her şey (Automobilista 2 o zaman hiçbir şey yazmaz)

**Boyut**: eşleme oyunun sürümüne göre yaklaşık 20 ile 30 KB, sürerken saniyede en fazla 10 kez: sıkıştırmadan önce saat başına yaklaşık 0,7 ile 1,1 GB; zstd boş katılımcı yuvalarını ve değişmeyen adları küçük bir kısmına indirir (gerçek bir oturumda henüz ölçülmedi)

## Doğrulama {#verified}

bir test içinde kurulan sayfa üzerinde test edilmiştir; ofsetler oyunun getirdiği kopyadan değil, SharedMemory.h'nin birbiriyle uyuşan iki bağımsız kopyasından alınmıştır; oyunla test edilmemiştir

## Kaynak {#source}

[heat3d_watch/adapters/simracing_shm.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/simracing_shm.py)

<!-- Adaptörden tools/gen_game_pages.py ile üretilmiştir; sayfayı elle düzenlemek yerine adaptörü değiştirin ve yeniden çalıştırın. -->
