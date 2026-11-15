---
title: "Steam Timeline (platform)"
nav_order: 43
lang: "tr"
source: game-steam-timeline.md
source_hash: "3a502e4ad09e"
nav_exclude: true
search_exclude: true
---
# Steam Timeline (platform) {#steam-timeline-platform}

Watcher, Steam Timeline'ın oyunlarınız hakkında tuttuğu bilgileri kaydeder; böylece geçmişinize daha sonra istatistik ve zaman çizelgesi olarak bakabilirsiniz.

*Teknik ayrıntılar: bağdaştırıcı `steam-timeline`, tür [`platform`](sources-and-rules.md); sürekli çalışır (bir oyunun başlamasını beklemez) ve her 10 saniyede bir yeni veri arar.*

## Ne kaydedilir {#what-is-recorded}

- her zaman çizelgesi dosyası için bir oturum: başlangıcı ve bitişi (session_start, session_end)
- oynarken açılan başarımlar, zamanlarıyla
- oyun modu değişiklikleri (oynama, hazırlık, menüler, yükleme ekranı)
- oyunların ISteamTimeline ile eklediği olaylar, başlık ve açıklamayla, simgelerinin adı altında
- oyun evreleri (bir maç, bir görev), etiketleriyle; içindeki olaylar, kimliğini session olarak taşır
- oyunun zaman çizelgesinde gösterdiği durum açıklamaları ("Round 3")
- Steam'in kendi kayıt hataları

## Nereden gelir {#where-it-comes-from}

%STEAM%\userdata\\&lt;account>\gamerecordings\timelines\timeline_&lt;appid>&lt;date>_&lt;time>.json

## Nasıl açılır {#how-to-switch-it-on}

Steam > Ayarlar > Oyun Kaydı: arka planda ya da isteğe bağlı kayıt yapın (Steam o zaman zaman çizelgeleri yazar)

## Nasıl çalışır {#how-it-works}

Başlatıcının ve grafik sürücüsünün oyun hakkında sakladıkları: Steam'in istatistikleri, başarımları, oynama süresi ve zaman çizelgeleri ile NVIDIA'nın öne çıkanları ve klipleri.

Bu kaynaklardan hiçbiri bir oyunun iş birliği yapmasını ya da çalışıyor olmasını gerektirmez; bu yüzden buradaki üç bağdaştırıcı her zaman açıktır ve birkaç dosyaya her birkaç saniyede bir bakar.

#### Steam Timeline (`steam-timeline`) {#steam-timeline-steam-timeline}

`<Steam>\userdata\<account>\gamerecordings\timelines\timeline_<appid><yyyymmdd>_<hhmmss>.json`; Steam Oyun Kaydı açıkken yazılır. Dosya, dize olarak yazılmış sayılara sahip JSON'dur: "daterecorded" (Unix saniyesi), "starttime"/"endtime" (ms) ve "entries", her biri {"id", "time" (daterecorded'dan itibaren ms), "type", ...}. Gerçek dosyalarda görülen türler:
```text
achievement        achievement_name - Steam bunu her oyun için ekler
gamemode           mode, bir ETimelineGameMode: 1 oynama, 2 hazırlık, 3 menüler,
                   4 yükleme ekranı
error              description - Steam'in kendisinin ("#GameRecording_RecordingFailed")
event              bir oyunun AddInstantaneousTimelineEvent/AddRangeTimelineEvent çağrısı:
                   title, description, icon, priority, duration (ms),
                   possible_clip - "You killed <name>" / "with the <weapon>"
state_description  title - SetTimelineTooltip ("Round 3")
phase              bir StartGamePhase..EndGamePhase aralığı: duration (ms), tags
                   [{name, icon, group, priority}] (mode, map ...)
```
Dosya düzeni Steam'indir ve belgelenmemiştir; alanlar API'nin parametreleridir. Diğer her tür, kendi adı ve alanlarıyla kaydedilir.
<https://partner.steamgames.com/doc/api/ISteamTimeline>
<https://partner.steamgames.com/doc/features/timeline>

Aynı modül şunlara da hizmet eder: [NVIDIA öne çıkanları (platform)](game-nvidia-highlights.md), [Steam istatistikleri (platform)](game-steam-stats.md).

## Konumlar ve eksenler {#positions-and-axes}

| | |
|---|---|
| Konumlar kaydedilir | hayır |
| Yukarı eksen | `y` |
| Birimler | metre |
| Görüntüleyici için aynalanır | yok |
| Birim ölçeği (`scale`: görüntüleyici konumları bununla çarpar) | 1 |

Bunlar her oturumun `meta.json` dosyasındaki (`axes`) ve oturumda konum varsa `heat.parquet` dosyasının altbilgisine yazılır; böylece 3DHeat görüntüleyicisi satırları kendi başına döndürüp ölçekler — bkz. [Veri](the-data.md).

## Çok oyunculu {#multiplayer}

- Online oynandığı olarak işaretli (`multiplayer`): **hayır**. `games --markdown` bunu "tek oyunculu" olarak gösterir.
- Tür `platform`: yalnızca oyunun veya platformun dışarı verdiklerini (Steam'in veya grafik sürücüsünün tuttuklarını) okur; bu yüzden çevrimiçi oyunda da, çevrimdışıyken de kaydeder. Bayrak yalnızca belleğin hiç okunup okunamayacağını belirler.
- Bellek: bu bağdaştırıcı belleği **asla** okumaz. Yalnızca `memory` bağdaştırıcıları bellek okur ve çevrimiçi oynandığı işaretli bir oyun için asla — bkz. [Kaynaklar ve kurallar](sources-and-rules.md).

## Kaydedilen istatistikler {#statistics-recorded}

Bu bağdaştırıcının kodunun adla ayarladığı istatistik anahtarları (her oturumun `meta.json` içindeki `stats` alanı ve `watcher.sqlite` dosyasındaki `stats` tablosu):

`achievements`, `game_mode_changes`, `phases`, `recorded_seconds`, `timeline_events`

Süslü parantez içindeki anahtar çalışma zamanında tamamlanır (`score.{team}` her takım için ayrı bir anahtardır). Oyunun alanlarından ya da oyunun kendi istatistik adlarından bir tablo alan anahtarlar bu listede yoktur; yukarıdaki "Ne kaydedilir" bölümü onları adlandırır.

## Eksiksizlik {#completeness}

Watcher, 3DHeat'in [çevirici kuralını](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md) izler: kaynakta ne varsa okunur ya da saklanır, asla atılmaz. Satırların yanında, bağdaştırıcının aldığı her paket, sayfa, satır ya da yanıt, oturumun `heat.raw.parquet` dosyasında bütün olarak saklanır (sütunlar `time`, `ms`, `type`, `used`, `payload`, `text` ve adıyla saklanan her alan; `used` satır olanları işaretler). `meta.json` içindeki `selfCheck.completeness` her `type` değerini sayar — `lost` 0'dır.

**Okunur**

- her girdi bir kez, zamanında bir satır olarak: türü, her düz alan (title, description, icon, priority, duration, possible_clip, başarım adı, mode, ...), bir evrenin etiketleri grup adına göre, başarımın görünen adı istatistik şemasından; dosyanın başlangıcı ve bitişi

**Ham olarak saklanır**

- her girdi, Steam'in kendi `type` değeri altında bütün bir JSON olarak (`gamemode`, `achievement`, `event`, `state_description`, `phase`, `error`, diğer her tür): iç içe alanlar — bir etiketin simgesi ve önceliği, sonradan eklenen her şey — yalnızca burada bulunur
- `timeline`: dosyanın kendi alanları (daterecorded, starttime, endtime, diğer her alan); oturum açıldığında ve değiştiğinde yeniden

**Mevcut değil**

- kayıt kendisi (video): Steam bunu kendi klasörlerinde tutar; oturum zaman çizelgesi dosyasına adıyla atıfta bulunur
- Steam'in yazmakta olduğu ve sonu kapalı olsa bile ayrıştırılamayan bir dosyanın okunması: sayılır (bağdaştırıcının durumunda `bad`) ve bir sonraki değişiklikte yeniden okunur; girdileri orada alınır

**Boyut**: saat başına birkaç yüz girdi, her biri 100-300 bayt: saat başına bir MB'ın çok altında

## Doğrulama {#verified}

Yerel bir kurulumdan alınan gerçek zaman çizelgesi dosyalarıyla test edildi: başarım, gamemode, error ve oyunların kendi event, state_description ve phase girdileri; dosya biçimi kendisi belgelenmemiştir.

## Kaynak {#source}

[heat3d_watch/adapters/platform.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/platform.py)

<!-- Generated from the adapter by tools/gen_game_pages.py; change the adapter and run it again rather than editing this page. -->
