---
title: "NVIDIA Highlights"
nav_order: 8
lang: "tr"
source: nvidia-highlights.md
source_hash: "cd2a5cc2c5fd"
nav_exclude: true
search_exclude: true
---
# NVIDIA Highlights {#nvidia-highlights}

Bazı oyunlar, bir şey olduğunda - örneğin bir öldürme - NVIDIA grafik sürücüsünden kısa bir video kaydetmesini ister.
İzleyici bu anların her birini not eder ve mümkün olduğunda, olduğu yerde haritaya koyar.

`nvidia-highlights` adaptörü, NVIDIA Uygulaması'nın (ya da GeForce Experience'ın) kaydettiği klipleri, öne çıkanları ve ekran görüntülerini kaydeder ve her birine mümkün olduğunda haritada bir yer verir. Bu sayfa, NVIDIA Highlights'ın neler sunabildiğini ve neleri sunamadığını, izleyicinin hangi dosyaları okuduğunu ve bir öne çıkanın nasıl bir konum aldığını açıklar. Adaptörün üretilen sayfası: [NVIDIA highlights (platform)](game-nvidia-highlights.md).

## NVIDIA Highlights neler sunabilir, neler sunamaz {#what-nvidia-highlights-can-and-cannot-deliver}

NVIDIA Uygulaması ile konuşan bir oyun, bunu NVIDIA'nın GfeSDK'sı üzerinden yapar. SDK yalnızca iki tür ileti taşır:

1. **Bir kez, başlangıçta**: oyunun kullanacağı öne çıkan türleri - bir kimlik (örneğin `kill`), bir önem derecesi, etiketler ve dil başına bir görünen ad. NVIDIA Uygulaması bunları oyun başına saklar.
2. **Bir oyun anında**: "öne çıkan `<id>`, şimdiden `<ms>` önce ile `<ms>` sonra arası". İleti bu kadardır: oyunun kaydettiği bir türün kimliği ve NVIDIA Uygulaması'na, yuvarlanan kaydının hangi kısmını tutacağını söyleyen iki zaman farkı.

SDK'da **başka hiçbir alan yoktur**: konum yok, maç ya da tur yok, rakip yok, silah yok, skor yok, hiçbir türde özel veri yok. Bir oyun istese bile bir öne çıkana konum koyamaz. Klip kaydedildiğinde NVIDIA Uygulaması bir dosya, bir oyun adı, bir uzunluk ve bir zaman ekler.

Yani bir öne çıkan yalnızca şunu söyleyebilir: "bu oyunda, bu zamanda, bu türden bir an". Daha fazlası başka bir yerden gelmelidir.

## İzleyicinin ne okuduğu {#what-the-watcher-reads}

Her şey, NVIDIA Uygulaması'nın kendi galerisi için yazdığı dosyalardan okunur. Hiçbir şey sürücüyle ya da uygulamayla konuşmaz. NVIDIA Overlay klasörü `%LOCALAPPDATA%\NVIDIA Corporation\NVIDIA Overlay`'dir.

| Dosya | Ondan alınan |
|---|---|
| `UGCTracker.json` | galeri dizini: her klip ve ekran görüntüsü, yolu, türü (video, görüntü), alt türü (`InstantReplay`, ...), tarihi, oyunun profil adı, çalıştırılabilir dosyası ve kısa adı, ve uzunluğu (`msDuration`) |
| `GallerySettings.json` | `settings.currentDirectoryV2`, yakalama klasörü, ve `settings.tempDirectory`, öne çıkanların kaydedilene kadar beklediği yer (`<temp>\Highlights\<game>`) |
| `Highlights\<game>\config.json` | her oyunun kaydettiği öne çıkan türleri: kimlik ve İngilizce görünen ad (oyun bir ad vermediyse kimlik) |
| yakalama klasörü (varsayılan `%USERPROFILE%\Videos\NVIDIA`) ve `<temp>\Highlights` | klip ve ekran görüntüsü dosyaların kendileri (`.mp4`, `.mkv`, `.mov`, `.png`, `.jpg`, `.jpeg`), oyun başına bir klasör |
| `%LOCALAPPDATA%\NVIDIA Corporation\GfeSDK\<exe>_<pid>.log` | GfeSDK kullanan oyunların kaydettiği istekler - `Posted Request HL...` satırları - böylece oyunun istediği bir öne çıkan, hiçbir klip tutulmasa bile kaydedilir. Yapılandırma istekleri (`HLConfigure`, `HLGetConfig`, `HLGetUserSettings`, `HLSetDefaultLocale`) atlanır. |

Her yeni öğe için adaptör bir satır yazar: video için `highlight`, görüntü için `screenshot`, bir GfeSDK günlük satırı için `highlight_request`. Alanları:

| Alan | Ne olduğu |
|---|---|
| `ms` | an: dosya adındaki zaman (`<Game> 2026.05.01 - 20.31.28.115.DVR.mp4`, klibin kaydedildiği yerel saat), yoksa dizindeki tarih, yoksa dosyanın değiştirilme zamanı |
| `game` | NVIDIA profil adı, klasörün adı ya da dosya adındaki oyun |
| `clip`, `media` | dosyanın yolu; `video`, `image` ya da `file` |
| `kind` | `InstantReplay`, `Screenshot`, `Highlight` (geçici öne çıkanlar klasöründen) ya da dizinin alt türü |
| `duration_s`, `clip_start_ms` | uzunluk, dizinden ya da videonun kendi başlığından (`moov/mvhd`, videoyu okumadan bulunur); klibin başladığı an |
| `highlight_id`, `highlight_name` | öne çıkan türü, bir şey onu adlandırdığında (aşağıya bakın) |
| `exe` | dizinden oyunun çalıştırılabilir dosyası |
| `x`, `y`, `z`, `session`, `position_from`, `position_lag_ms` | bir konum bulunduğunda ödünç alınan konum (aşağıya bakın) |

Oturum istatistikleri `clips`, `screenshots`, `clip_seconds` ve `placed` (bir konum alan öğeler).

**Öne çıkan kimliği** hiçbir belgelenmiş yerde yazılmaz. Adaptör iki belgelenmemiş yeri dener: galeri girdisinin adında "highlight" geçen bir alan ve - yalnızca geçici öne çıkanlar klasöründeki dosyalar için - dosya adında geçen, oyunun kayıtlı kimliklerinden biri (en az 4 karakter). Kaydedilmiş bir klip, oyunun adıyla adlandırılır; bu ad, tesadüfen "kill" gibi bir kimlik içerebilir, bu yüzden adında arama yapılmaz. Bu iki yol gerçek bir makinede henüz çalıştığı görülmedi: öne çıkan kimliği olan klip ve GfeSDK istek satırı, adaptörün test edildiği yerde oluşmadı. Galeri dizini, ayarlar, öne çıkan tanımları ve klipler gerçek dosyalarla test edildi.

### Öğeler ne zaman kaydedilir {#when-items-are-recorded}

- Bir klip, tuşa basıldıktan sonra bir süre hâlâ yazılıyordur. Adaptör, bir dosyanın iki bakışta (her 10 s'de bir) aynı boyut ve zamana sahip olmasını bekler ve dosya en az 5 s eski olmalıdır.
- Adaptör ilk çalıştığında, galeride ve günlüklerde zaten olan her şey yalnızca not edilir, kaydedilmez; böylece yıllarca eski klipler istatistikleri doldurmaz. Gördüklerini `<data>\state\nvidia-highlights.json` içinde tutar; böylece yeniden başlatma hiçbir şeyi iki kez kaydetmez.
- Öğeler oyun başına bir oturumda gruplanır. Bir oyunun oturumu, yeni bir öğe gelmeden 30 dakika sonra kapanır ve oyun kapandığında değil, son anında biter. Birbirinden 30 dakikadan fazla uzak anlar ayrı oturumlara girer.

## Bir öne çıkan nasıl konum alır {#how-a-highlight-gets-a-position}

Öne çıkanın kendisinin bir yeri yoktur. Adaptör, anı aynı zamanda izleyicinin aynı oyun için yaptığı diğer kayıtlarda arar:

1. **Aynı oyun**: oyun adı öne çıkanınkiyle eşleşen, `<data>\sessions\` altındaki oturum klasörleri. Adlar küçük harfe çevrilir, yalnızca harf ve rakamlar karşılaştırılır. Eşleşme, eşit olduklarında ya da kısa olanın en az 5 karakteri olup uzun olanın içinde geçtiğinde olur (`Counter-Strike 2` ve `Counter-Strike-2`).
2. **Aynı zaman**: başlangıcı ve bitişi (meta.json'dan, iki uçta birer saniye pay ile) anı kapsayan oturumlar. Konumsuz biten oturumlar ve adaptörün kendi oturumları atlanır.
3. **Oyuncunun kendi satırı**: oyuncunun `events.jsonl` dosyasında, anın en fazla 5 saniye öncesine kadar olan ve bir konumu olan, oyuncunun kendi son satırı. Bir satır, kaynağı bunu söylediğinde oyuncunun kendisidir: `"player": "me"`, ya da `"own_car": 1` (her arabayı sürücüsüyle kaydeden yarış oyunları), ya da oturumun `meta.json` içindeki `player` değerine (kaynağın oyuncuya verdiği ad) eşit bir `player`. Bkz. [Oyuncunun kendi satırları](the-data.md#the-players-own-rows).

Bir satır bulunursa öne çıkanın `x`, `y`, `z` değerleri, `session` (ya da klasörün adı), `position_from` (geldiği klasör) ve `position_lag_ms` (anın ne kadar önceki bir satır olduğu) alır. Öne çıkan oturumu, o kaydın eksenlerini alır; böylece aynı yönde çizilir. Satır bulunamazsa öne çıkan, yeri olmayan bir zaman çizelgesi anı olarak kalır.

Ödünç alınan konum hakkında bilmeniz gerekenler:

- **Klip kaydedildiğindeki yerinizdir**, aksiyonun başladığı yer değil. An, dosya adındaki kaydetme zamanıdır; bir Instant Replay için bu, sonudur. `clip_start_ms` klibin nerede başladığını söyler.
- **Aynı oyunu o zaman başka bir adaptörün kaydetmiş olması gerekir.** Oyuncunun kendi satırlarını işaretleyen ve bu yüzden bir öne çıkanı yerleştirebilen olanlar: Counter-Strike 2 ve Dota 2 oyun durumu entegrasyonu, Forza, Assetto Corsa oyunları, EA SPORTS WRC, DiRT Rally 2.0, Richard Burns Rally, BeamNG.drive, Euro Truck Simulator 2, American Truck Simulator, DCS World, X-Plane, Microsoft Flight Simulator, War Thunder, Minecraft ve bellek profilleri (`me` olarak); F1 23/24/25, RaceRoom, Automobilista 2 ve Project CARS 2 (arabanızın satırları `own_car` 1 taşır; oyunun oyuncu araba dizinine, kendi yuvasına ya da izlenen katılımcıya göre); Elite Dangerous (komutanın adı, meta.json'da `player` olarak, çünkü günlük her zaman oyuncunundur).
- **Bir tekrar maçtan sonra dönüştürülür**, bu yüzden yalnızca dönüştürmeden sonra aranan bir klibi yerleştirebilir: klip kaydedildiğinde yerleştirilir, sonra kaydedilen bir tekrara tekrar bakılmaz. League of Legends tekrarları satırlarını ayarlardaki Riot ID'siyle adlandırır ve bir Riot API anahtarıyla, maç zaman çizelgesinin belirttiği duvar saatini verir; böylece o zaman bulunurlar. Bir CS2 demosu bir öne çıkanı hiç yerleştiremez: konumları dönüştürücünün kendi tablosundadır, `events.jsonl` içinde değil ve bir demonun, bir klibin anını eşleştirebileceği bir duvar saati yoktur, yalnızca oyunun tikleri vardır.
- Rocket League'de konumu olan tek satırlar top olaylarıdır. Topa vurduğunuz bir vuruş sizin bir satırınızdır, bu yüzden bir öne çıkan, topa en son vurduğunuz yere konabilir.
- Hiç konumsal kaynağı olmayan oyunlar (Overwatch 2, Call of Duty, Hunt: Showdown, ...) öne çıkanlarını bir an zaman çizelgesi olarak tutar.

## Çok oyunculu oyunlarda bellek neden bir konum veremez {#why-memory-cannot-give-a-position-in-multiplayer}

Konumu almanın diğer yolu bellekten okumak olurdu. İki bellek de işe yaramaz:

- **NVIDIA'nın belleğinde konum yoktur.** NVIDIA Uygulaması, GfeSDK'nın taşıdığını alır - bir öne çıkan kimliği ve iki zaman farkı - artı kaydettiği video. NVIDIA tarafında okunacak bir konum hiçbir yerde yoktur. (İzleyici zaten NVIDIA'nın belleğini okumaz; yukarıdaki dosyaları okur.)
- **Oyunun belleği çok oyunculuda yasaktır.** Konum oyunun süreci içindedir, ama izleyici çok oyunculu bir oyunun belleğini asla okumaz: çevrimiçi oynanan olarak işaretli bir oyun için bir bellek adaptörü, hiçbir şey açılmadan reddedilir (bkz. [Bellek okuma](memory-reading.md)). Çok oyunculu oyunlar anti-hile sistemleri altında çalışır (Easy Anti-Cheat, BattlEye, Vanguard, ...); bunlar, başka bir programın oyunun sürecini açmasını hile sayar ve hesabın yasaklanmasına yol açabilir. Bu yüzden çok oyunculu bir oyundaki öne çıkan, yalnızca oyunun yayımladığından - oyun durumu entegrasyonundan ya da telemetrisinden, aynı zamanda başka bir adaptörün kaydettiğinden - bir yer alır.
