---
title: "NVIDIA Highlights (platform)"
nav_order: 34
lang: "tr"
source: game-nvidia-highlights.md
source_hash: "5d45211c0e37"
nav_exclude: true
search_exclude: true
---
# NVIDIA Highlights (platform) {#nvidia-highlights-platform}

İzleyici, NVIDIA Highlights'ın oyunlarınız hakkında tuttuklarını kaydeder; böylece geçmişinize daha sonra 3DHeat görüntüleyicisinde bir harita üzerinde bakabilirsiniz.

*Teknik ayrıntılar: bağdaştırıcı `nvidia-highlights`, tür [`platform`](sources-and-rules.md); her zaman çalışır (bir oyunun başlamasını beklemez) ve yeni veri için her 10 saniyede bir bakar.*

## Ne kaydedilir {#what-is-recorded}

- her yeni klip, öne çıkan an ya da ekran görüntüsü: oyun, dosya, tür, uzunluk ve an (duvar saati ms)
- oyun NVIDIA'ya kaydettiğinde öne çıkanın kimliği ve adı
- başka bir bağdaştırıcı o anda aynı oyunu kaydettiyse, oyuncunun o andaki konumu
- GfeSDK oyunlarının günlüğe yazdığı öne çıkan istekleri, klip tutulmasa bile

## Kaynağı {#where-it-comes-from}

%LOCALAPPDATA%\NVIDIA Corporation\NVIDIA Overlay\UGCTracker.json, GallerySettings.json, Highlights\\&lt;oyun>\config.json; klipler yakalama klasöründe (%USERPROFILE%\Videos\NVIDIA\\&lt;Oyun>\\\*.mp4) ve &lt;temp>\Highlights\\&lt;oyun> içinde; %LOCALAPPDATA%\NVIDIA Corporation\GfeSDK\\&lt;exe>_&lt;pid>.log

## Nasıl açılır {#how-to-switch-it-on}

NVIDIA App: Instant Replay ya da Highlights açık, klipler tuşla ya da oyun tarafından kaydedilmiş olmalı

## Nasıl çalışır {#how-it-works}

Başlatıcının ve ekran kartı sürücüsünün oyun hakkında tuttukları: Steam'in istatistikleri, başarımları, oyun süresi ve zaman çizelgeleri, ve NVIDIA'nın öne çıkanları ve klipleri.

Bu kaynakların hiçbiri bir oyunun iş birliği yapmasını ya da çalışıyor olmasını gerektirmez; bu yüzden buradaki üç bağdaştırıcı her zaman açıktır ve birkaç saniyede bir birkaç dosyaya bakar.

#### NVIDIA öne çıkanları ve klipleri (`nvidia-highlights`) {#nvidia-highlights-and-clips-nvidia-highlights}

NVIDIA App / GeForce Experience'ın tuttukları, hepsi `%LOCALAPPDATA%\NVIDIA Corporation\NVIDIA Overlay` altında:
```text
UGCTracker.json      the gallery index: {"UGC": [{id, path, type (video,
                     image), subType (InstantReplay, Normal, ...), date
                     (UTC, when the file was written), profileName, drsName
                     (the exe), shortName, msDuration, ...}], "apps", "info"}
GallerySettings.json settings.currentDirectoryV2 (where clips are saved),
                     settings.tempDirectory (highlights wait in
                     <temp>\Highlights\<game> until saved)
Highlights\<game>\config.json  the highlight kinds a game registered:
                     {"highlights": {id: {significance, highlightTags,
                     name: {locale: text}}}, profileName, drsName, shortName}
```
Klip dosyaların kendileri ise `<yakalama klasörü>\<Oyun>\<Oyun> yyyy.mm.dd -
hh.mm.ss.ff.DVR.mp4` (ekran görüntüleri: `<Oyun> Screenshot yyyy.mm.dd - ...png`); dosya adındaki zaman, klibin kaydedildiği yerel saattir. GfeSDK oyunları öne çıkan çağrılarını ayrıca `%LOCALAPPDATA%\NVIDIA Corporation\GfeSDK\<exe>_<pid>.log` içine yazar.

Bu neyi verebilir, neyi veremez: Highlights'ı destekleyen bir oyun (GfeSDK) öne çıkan türlerini bir kez kaydeder - "kill" gibi bir kimlik, bir önem derecesi, etiketler, bir görünen ad - ve sonra yalnızca "highlight <kimlik>, <ms> önce ile <ms> sonra arası" der. Konum, maç ya da tur, rakip, özel veri yoktur: SDK'nın bunlar için bir alanı yoktur. Kaydedilen bir klip, bir dosya, bir oyun adı, bir uzunluk ve bir zaman ekler. Yani kaydedilen şey "bu tür bir an, bu oyunda, bu zamanda"dır - ve bir yer ancak zamanı aynı oyunun başka bir bağdaştırıcısının kaydında aratarak bulunur (`position_at`), bu bağdaştırıcı kaydettiği her klip için bunu yapar.
<https://developer.nvidia.com/highlights>

Her bağdaştırıcı gördüğünü `<veri>\state\<kimlik>.json` içinde tutar; böylece yeniden başlatma hiçbir şeyi iki kez kaydetmez.

Her oturum ayrıca satırlarının geldiği her şeyi bütün olarak, `heat.raw.parquet` içinde saklar (3DHeat'in dönüştürücü kuralı, görüntüleyicinin deposundaki docs/converters.md): istatistik dosyasının ve şemasının baytları ve oyunun localconfig bloğu (steam-stats; okunamayan bir istatistik dosyası yalnızca baytları tutan bir oturum verir), zaman çizelgesi dosyasının başlığı ve her girdi JSON olarak (steam-timeline), her klibin galeri dizini girdisi, oyunun öne çıkan tanımları ve her GfeSDK günlük satırı, öne çıkan istekleri olmayanlar da dahil (nvidia-highlights).

Bu modülün sunduğu diğer sayfalar: [Steam istatistikleri (platform)](game-steam-stats.md), [Steam Timeline (platform)](game-steam-timeline.md).

## Konumlar ve eksenler {#positions-and-axes}

| | |
|---|---|
| Kaydedilen konumlar | yalnızca ödünç alınmış: aynı oyunun başka bir kaydının o an için sahip olduğu yer |
| Yukarı ekseni | `y` |
| Birimler | metre |
| Görüntüleyici için aynalama | yok |
| Birim ölçeği (`scale`: görüntüleyici konumları bununla çarpar) | 1 |

Bunlar her oturumun `meta.json` dosyasındaki (`axes`) ve konum içeren oturumlarda `heat.parquet` dosyasının sonundaki (footer) bilgiye yazılır; böylece 3DHeat görüntüleyicisi satırları kendisi döndürür ve ölçekler - bkz. [Veriler](the-data.md).

## Çok oyunculu {#multiplayer}

- Çevrimiçi oynanan olarak işaretlenmiş (`multiplayer`): **hayır**. `games --markdown` bunu "tek oyunculu" olarak gösterir.
- Tür `platform`: yalnızca Steam'in ya da ekran kartı sürücüsünün tuttuğunu okur; bu yüzden çevrimiçi oyunda da çevrimdışı olduğu gibi kaydeder; bayrak yalnızca belleğin hiç okunup okunamayacağını belirler.
- Bellek: bu bağdaştırıcı **asla** okumaz. Yalnızca `memory` bağdaştırıcıları bellek okur ve çevrimiçi oynanan olarak işaretlenmiş bir oyun için asla okumaz - bkz. [Kaynaklar ve kurallar](sources-and-rules.md).

## Kaydedilen istatistikler {#statistics-recorded}

Bu bağdaştırıcının kodunun adla ayarladığı istatistik anahtarları (her oturumun `meta.json` içindeki `stats` ve `watcher.sqlite` içindeki `stats` tablosu):

`clip_seconds`, `clips`, `placed`, `screenshots`

Parantez içindeki bir anahtar çalışma zamanında tamamlanır (`score.{team}` her takım için bir anahtardır). Kodun oyunun alanlarının tablosundan ya da oyunun kendi istatistik adlarından aldığı anahtarlar bu listede yer almaz; yukarıdaki "Ne kaydedilir" bölümü bunları adlandırır.

## Tamlık {#completeness}

İzleyici 3DHeat'in [dönüştürücü kuralını](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md) izler: kaynağın tuttuğu her şey okunur ya da saklanır, asla atılmaz. Satırların yanı sıra, bağdaştırıcının aldığı her paket, sayfa, satır ya da yanıt, oturumun `heat.raw.parquet` dosyasında bütün olarak saklanır (sütunlar `time`, `ms`, `type`, `used`, `payload`, `text` ve adla saklanan her alan; `used` satıra dönüşenleri işaretler). `meta.json` içindeki `selfCheck.completeness` her `type` değerini sayar - `lost` 0'dır.

**Okunan**

- her yeni klip ve ekran görüntüsü: oyun, dosya, tür, ortam, uzunluk (dizinden, yoksa MP4 başlığından), dosya adındaki an, oyunun kaydettiği yerde öne çıkan kimliği ve adı, o andaki oyuncunun yeri (başka bir bağdaştırıcının kaydından)
- GfeSDK öne çıkan istekleri (yapılandırma çağrıları hariç her `Posted Request HL...`) zamanlarıyla

**Ham olarak saklanan**

- `UGC`: klibin UGCTracker.json galeri dizinindeki bütün girdisi, NVIDIA'nın yazdığı her alan
- `clip_file`: dizinin listelemediği bir klip için dosyanın yolu, boyutu, zamanı ve klasörü
- `highlights_config`: oyunun `Highlights\<oyun>\config.json` dosyası yazıldığı gibi (önem derecesi, etiketler, her dildeki adlar), oturum başına bir kez
- `gfesdk_log`: ilk çalıştırmadan sonra okunan GfeSDK günlüklerinin her satırı; öne çıkan istekler için `used` doğru, diğerleri için yanlış (yapılandırma, video ayarları, SDK'nın kendi iletileri)

**Kullanılamayanlar**

- klipler ve ekran görüntüleri kendileri: video ve resimler NVIDIA'nın kaydettiği yerde kalır; satırlar dosyayı adlandırır
- bağdaştırıcının ilk çalıştırmasından önce olanlar: görülmüş sayılır, böylece yıllarca biriken klipler birden oturumlara dönüşmez (`baseline`; False kaydeder)
- UGCTracker.json'ın `apps` ve `info` bölümleri ile GallerySettings.json: uygulamanın ayarları, oyun anları değil; adını verdikleri yakalama klasörü kullanılır
- konumlar, turlar, rakipler: GfeSDK bunlar için bir alan sunmaz

**Boyut**: klip ve ekran görüntüsü başına yaklaşık 1 KB, oyun her açıldığında birkaç KB tanım ve günlük satırı: saatte 1 MB'ın çok altında

## Doğrulama {#verified}

gerçek bir galeri dizini, ayarlar, öne çıkan tanımları ve yerel bir kurulumdan alınan klipler üzerinde test edilmiştir; GfeSDK öne çıkan istek satırları ve kliplerdeki öne çıkan kimlikleri test edilmemiştir

## Kaynak {#source}

[heat3d_watch/adapters/platform.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/platform.py)

<!-- Adaptörden tools/gen_game_pages.py ile üretilmiştir; sayfayı elle düzenlemek yerine adaptörü değiştirin ve yeniden çalıştırın. -->
