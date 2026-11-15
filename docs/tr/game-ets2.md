---
title: "Euro Truck Simulator 2 (canlı veri)"
nav_order: 19
lang: "tr"
source: game-ets2.md
source_hash: "537f0daeedbf"
nav_exclude: true
search_exclude: true
---
# Euro Truck Simulator 2 (canlı veri) {#euro-truck-simulator-2-live-data}

Euro Truck Simulator 2 oynarken izleyici, oyunun kendi gönderdiği verileri kaydeder; böylece bu verilere daha sonra 3DHeat görüntüleyicisinde bir harita üzerinde bakabilirsiniz.

*Teknik ayrıntılar: bağdaştırıcı `ets2`, tür [`telemetry`](sources-and-rules.md); `eurotrucks2.exe` çalışırken çalışır ve yeni veri için her 0,1 saniyede bir bakar.*

## Ne kaydedilir {#what-is-recorded}

- kamyonun dünya konumu (x doğu, y yukarı, z güney, m), hareket halindeyken saniyede 10 kez, dururken her 5 saniyede bir; yön, hız, kilometre sayacı
- başlatılan işler (yük, nereden, nereye), teslim edilenler (gelir, XP, km), iptal edilenler; cezalar, geçiş ücretleri, feribotlar, trenler, yakıt ikmalleri
- feribotlar, trenler ve yüklenen kayıtlar rotayı böler (ışınlanma, `spawn`)
- mesafe, en yüksek hız, teslimatlar, gelir, XP, cezalar
- eklentinin bütün paylaşılan belleği `heat.raw.parquet` dosyasında, her değiştiğinde

## Kaynağı {#where-it-comes-from}

paylaşılan bellek Local\SCSTelemetry; RenCloud scs-sdk-plugin (revizyon 12) yazar, &lt;oyun>\bin\win_x64\plugins içinde

## Nasıl açılır {#how-to-switch-it-on}

scs-telemetry.dll (revizyon 12) dosyasını github.com/RenCloud/scs-sdk-plugin adresinden &lt;oyun>\bin\win_x64\plugins içine kurun; oyun her başlatmada SDK'ya izin vermenizi bir kez ister

## Nasıl çalışır {#how-it-works}

Euro Truck Simulator 2 ve American Truck Simulator: SCS telemetri SDK'sı, RenCloud eklentisi üzerinden.

SCS, oyuncunun `<oyun>\bin\win_x64\plugins\` klasörüne koyduğu eklentiler için bir telemetri SDK'sı yayımlar (<https://modding.scssoft.com/wiki/Documentation/Engine/SDK/Telemetry>). Oyunun kendisi hiçbir şey yayımlamaz; yaygın kullanılan <https://github.com/RenCloud/scs-sdk-plugin> eklentisi (MIT) SDK'nın kanallarını paylaşılan bellek `Local\SCSTelemetry` (32 KiB) içine kopyalar; düzen `scs-telemetry/inc/scs-telemetry-common.hpp` içindedir. Bu bağdaştırıcı yalnızca bu düzenin revizyon 12'sini okur (PLUGIN_REVID 12) ve başka hiçbir şeyi okumaz: eklenti revizyonunu 40. baytta yazar; başka bir revizyon yanlış okunmak yerine hiç okunmaz. Kullanılan ofsetler (bölgeler başlığın gösterdiği gibi; doğal hizalama):

```text
   0  bool sdkActive          4  bool paused
  40  u32  telemetry_plugin_revision, version_major, version_minor, game (1 ETS2, 2 ATS)
  64  u32  common_ui.time_abs (in-game minutes)
 504  i32  truck_i.gear
 640  i32  gameplay_i.jobDeliveredEarnedXp
 948  f32  truck_f.speed (m/s); 952 engineRpm; 1056 truckOdometer (km)
1460  f32  gameplay_f.jobDeliveredDistanceKm
2200  f64  truck_dp.coordinateX/Y/Z (m), rotationX/Y/Z (heading, pitch, roll in turns, 0..1)
2300  char[64] config_s: truckBrand +64, truckName +192, cargo +320, cityDst +448, compDst +576,
      citySrc +704, compSrc +832; 3436 gameplay_s.fineOffence[32]
4200  i64  gameplay_ll: jobCancelledPenalty, jobDeliveredRevenue, fineAmount, tollgatePayAmount,
      ferryPayAmount, trainPayAmount
4300  bool special_b: onJob, jobFinished, jobCancelled, jobDelivered, fined, tollgate, ferry,
      train, refuel, refuelPayed
```

Kamyonun dünya konumu SCS'nin dünya çerçevesindedir: x doğu, y yukarı, z güney, metre cinsinden (sağ elli, y yukarı - görüntüleyici onu olduğu gibi çizer). Feribotlar, trenler ve bir kaydın yüklenmesi kamyonu sürmeden taşır: rota orada kesilir.

Eklentinin bütün paylaşılan belleği (32 KiB: yukarıdaki bütün bölgeler ve okunmayanlar - kamyon yapılandırması, tekerlekler, aşınma, kamyonun diğer kanalları ve revizyonun 4400. bayttan sonra yerleştirdiği, römorklar dahil) her değiştiğinde oturumun ham yan dosyasında saklanır; `type` `SCSTelemetry`, yanında `revision` ile. Başka bir revizyonun sayfası da bütün olarak saklanır; yanlış okunmaz.

Bu modülün sunduğu diğer sayfa: [American Truck Simulator (canlı veri)](game-ats.md).

## Konumlar ve eksenler {#positions-and-axes}

| | |
|---|---|
| Kaydedilen konumlar | evet |
| Yukarı ekseni | `y` |
| Birimler | metre (SCS dünyası: x doğu, y yukarı, z güney) |
| Görüntüleyici için aynalama | yok |
| Birim ölçeği (`scale`: görüntüleyici konumları bununla çarpar) | 1 |

Bunlar her oturumun `meta.json` dosyasındaki (`axes`) ve konum içeren oturumlarda `heat.parquet` dosyasının sonundaki (footer) bilgiye yazılır; böylece 3DHeat görüntüleyicisi satırları kendisi döndürür ve ölçekler - bkz. [Veriler](the-data.md).

## Çok oyunculu {#multiplayer}

- Çevrimiçi oynanan olarak işaretlenmiş (`multiplayer`): **evet**. `games --markdown` bunu "izinli (yalnızca oyunun yayımladığını okur)" olarak gösterir.
- Tür `telemetry`: yalnızca oyunun ya da platformun dışarı verdiğini okur (oyunun yayımladığı bir UDP portu ya da paylaşılan bellek). Bu yüzden çevrimiçi oyunda da çevrimdışı olduğu gibi kaydeder; bayrak yalnızca belleğin hiç okunup okunamayacağını belirler.
- Bellek: bu bağdaştırıcı **asla** okumaz. Yalnızca `memory` bağdaştırıcıları bellek okur ve çevrimiçi oynanan olarak işaretlenmiş bir oyun için asla okumaz - bkz. [Kaynaklar ve kurallar](sources-and-rules.md).

## Kaydedilen istatistikler {#statistics-recorded}

Bu bağdaştırıcının kodunun adla ayarladığı istatistik anahtarları (her oturumun `meta.json` içindeki `stats` ve `watcher.sqlite` içindeki `stats` tablosu):

`deliveries`, `distance_km`, `fines`, `fines_total`, `jobs_cancelled`, `max_speed_kmh`, `refuels`, `revenue`, `tolls_total`, `xp`

Parantez içindeki bir anahtar çalışma zamanında tamamlanır (`score.{team}` her takım için bir anahtardır). Kodun oyunun alanlarının tablosundan ya da oyunun kendi istatistik adlarından aldığı anahtarlar bu listede yer almaz; yukarıdaki "Ne kaydedilir" bölümü bunları adlandırır.

## Tamlık {#completeness}

İzleyici 3DHeat'in [dönüştürücü kuralını](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md) izler: kaynağın tuttuğu her şey okunur ya da saklanır, asla atılmaz. Satırların yanı sıra, bağdaştırıcının aldığı her paket, sayfa, satır ya da yanıt, oturumun `heat.raw.parquet` dosyasında bütün olarak saklanır (sütunlar `time`, `ms`, `type`, `used`, `payload`, `text` ve adla saklanan her alan; `used` satıra dönüşenleri işaretler). `meta.json` içindeki `selfCheck.completeness` her `type` değerini sayar - `lost` 0'dır.

**Okunan**

- SDK ve duraklatma durumu, eklenti revizyonu, oyun ve sürüm, oyun içi zaman, kamyonun dünya konumu ve yönü, hız, kilometre sayacı, kamyonun markası ve adı, yük, kaynak ve hedef şehir ve şirket, iş geliri, XP ve mesafe, iptal cezası, cezalar ve suç türleri, geçiş ücretleri, feribotlar, trenler, özel olay bayrakları (satırlar, olaylar ve istatistikler olarak)
- artık konum satırlarında da: `pitch` ve `roll` (derece, SDK'nın turlarından), `gear` ve `rpm`
- ofsetler, eklentinin revizyon 12 başlığının alan alan bir dökümüne karşı kontrol edildi; bölge başlangıçları testlerde doğrulanır; henüz oyuna karşı değil

**Ham olarak saklanan**

- `SCSTelemetry`: eklentinin bütün 32 KiB eşlemesi; bir önceki kopyayla bayt bayt farklı olan her okuma (meta.json içindeki `unchanged_reads` diğerlerini sayar), yanında `revision`: her bölge - kamyon ve römork yapılandırması, kamyonun kanalları (pedallar, direksiyon, yakıt, AdBlue, basınçlar, sıcaklıklar, aşınma, ışıklar, tekerlekler), yerleşim ve ivme vektörleri, iş ve oyun dizgileri, ve revizyonun 4400. bayttan sonra yerleştirdiği her şey (römorklar); `used` SDK etkin ve revizyon 12 iken doğrudur
- başka bir eklenti revizyonunun sayfası bütün olarak, `used` false ile saklanır; yanlış okunmaz

**Kullanılamayanlar**

- eklentinin SDK'dan kopyalamadığı hiçbir şey ve eklenti kurulu değilken hiçbir şey: oyun kendi telemetrisini yayımlamaz
- TruckersMP'deki ya da konvoylardaki diğer oyuncuların kamyonları: SDK yalnızca oyuncunun kendi kamyonunu verir

**Boyut**: sürerken saniyede en fazla 10 kez 32 KiB (her okuma o zaman farklıdır): sıkıştırmadan önce saat başına yaklaşık 1,2 GB; duraklatılmışken tek kopya; sayfanın çoğu değişmeyen sıfırlar ve yapılandırmadır, bu yüzden zstd onu birçok kez küçültür (henüz gerçek bir oturumda ölçülmedi)

## Doğrulama {#verified}

SCS revizyon 12 başlık düzeninden oluşturulmuş paylaşılan bellek üzerinde test edilmiştir; oyunla test edilmemiştir

## Kaynak {#source}

[heat3d_watch/adapters/ets2.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/ets2.py)

<!-- Adaptörden tools/gen_game_pages.py ile üretilmiştir; sayfayı elle düzenlemek yerine adaptörü değiştirin ve yeniden çalıştırın. -->
