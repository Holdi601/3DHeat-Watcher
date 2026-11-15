---
title: "Steam istatistikleri (platform)"
nav_order: 42
lang: "tr"
source: game-steam-stats.md
source_hash: "09ecf3611c02"
nav_exclude: true
search_exclude: true
---
# Steam istatistikleri (platform) {#steam-statistics-platform}

Watcher, Steam istatistiklerinin oyunlarınız hakkında tuttuğu bilgileri kaydeder; böylece geçmişinize daha sonra istatistik ve zaman çizelgesi olarak bakabilirsiniz.

*Teknik ayrıntılar: bağdaştırıcı `steam-stats`, tür [`platform`](sources-and-rules.md); sürekli çalışır (bir oyunun başlamasını beklemez) ve her 30 saniyede bir yeni veri arar.*

## Ne kaydedilir {#what-is-recorded}

- bir oyunun Steam'de sakladığı her istatistik (oyunun kendi adları ve değerleri), oyun bazında, değiştiğinde
- başarım açmaları, görünen adları, açıklamaları ve açılma zamanlarıyla
- istatistik değişiklikleri: eski değer, yeni değer ve fark
- oynama süresi (dakika, son iki hafta) ve son oynama zamanı

## Nereden gelir {#where-it-comes-from}

Steam'in yerel istatistik önbelleği %STEAM%\appcache\stats\UserGameStats_&lt;account>_&lt;appid>.bin, yanında UserGameStatsSchema_&lt;appid>.bin ile; oynama süresi %STEAM%\userdata\\&lt;account>\config\localconfig.vdf dosyasından (%STEAM%, HKCU\Software\Valve\Steam SteamPath değerinden)

## Nasıl açılır {#how-to-switch-it-on}

Hiçbir şeyi açmanız gerekmez: watcher kaynağı, oyunun veya platformun sunduğu şekliyle okur.

## Nasıl çalışır {#how-it-works}

Başlatıcının ve grafik sürücüsünün oyun hakkında sakladıkları: Steam'in istatistikleri, başarımları, oynama süresi ve zaman çizelgeleri ile NVIDIA'nın öne çıkanları ve klipleri.

Bu kaynaklardan hiçbiri bir oyunun iş birliği yapmasını ya da çalışıyor olmasını gerektirmez; bu yüzden buradaki üç bağdaştırıcı her zaman açıktır ve birkaç dosyaya her birkaç saniyede bir bakar.

#### Steam istatistikleri (`steam-stats`) {#steam-statistics-steam-stats}

`<Steam>\appcache\stats\UserGameStats_<account>_<appid>.bin`; bir oyun istatistiklerini sakladığında Steam istemcisi bunu yeniden yazar ve yanındaki `UserGameStatsSchema_<appid>.bin` şeması ile çözülür (ikili KeyValues, bkz. `_steam.py`). İstatistikler, oyunun tanımladığı gibi tam sayı ya da ondalıklı sayıdır; başarımlar, Unix saniyesi cinsinden açılma zamanı olan bitlerdir. Oynama süresi `<Steam>\userdata\<account>\config\localconfig.vdf` içinde apps/<appid> altındadır: Playtime ve Playtime2wks dakika cinsinden, LastPlayed Unix saniyesi cinsinden. Steam, HKCU\Software\Valve\Steam SteamPath üzerinden bulunur.
Stats API: <https://partner.steamgames.com/doc/features/achievements>

Aynı modül şunlara da hizmet eder: [NVIDIA öne çıkanları (platform)](game-nvidia-highlights.md), [Steam Timeline (platform)](game-steam-timeline.md).

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

`achievements_total`, `achievements_unlocked`, `last_played`, `playtime_2wks_minutes`, `playtime_minutes`

Süslü parantez içindeki anahtar çalışma zamanında tamamlanır (`score.{team}` her takım için ayrı bir anahtardır). Oyunun alanlarından ya da oyunun kendi istatistik adlarından bir tablo alan anahtarlar bu listede yoktur; yukarıdaki "Ne kaydedilir" bölümü onları adlandırır.

## Eksiksizlik {#completeness}

Watcher, 3DHeat'in [çevirici kuralını](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md) izler: kaynakta ne varsa okunur ya da saklanır, asla atılmaz. Satırların yanında, bağdaştırıcının aldığı her paket, sayfa, satır ya da yanıt, oturumun `heat.raw.parquet` dosyasında bütün olarak saklanır (sütunlar `time`, `ms`, `type`, `used`, `payload`, `text` ve adıyla saklanan her alan; `used` satır olanları işaretler). `meta.json` içindeki `selfCheck.completeness` her `type` değerini sayar — `lost` 0'dır.

**Okunur**

- istatistik dosyasındaki her istatistik, API adıyla (int, float, avgrate); her başarım biti açılma zamanıyla, şema tarafından adlandırılmış ve açıklanmış
- son okumaya göre değişiklikler (eski, yeni, fark), yeni açılan başarımlar; localconfig.vdf dosyasından oynama süresi, iki haftalık oynama süresi ve son oynama

**Ham olarak saklanır**

- `UserGameStats`: istatistik dosyasının baytları, bütün olarak, her kaydedildiğinde (`crc`, `PendingChanges`, şemanın artık tanımlamadığı başarım bitleri ve çözücünün atladığı her anahtar bunun içindedir)
- `UserGameStatsSchema`: şema dosyasının baytları yanında, böylece istatistikler yalnızca oturumdan çözülebilir (her istatistiğin ve başarımın her dildeki adları, simgeleri, bayrakları)
- `localconfig_app`: oyunun localconfig.vdf içindeki bütün bloğu JSON olarak (bulut eşitleme durumu, başlatma seçenekleri, rozetler ve Steam'in oyun başına tuttuğu diğer her anahtar), oynama süresi kaydedildiğinde
- çözücünün okuyamadığı bir istatistik dosyası (yazım ortasında kesilmiş ya da yeni bir düzen): baytları ve şeması satır içermeyen bir oturumda (`used` false; `meta.json` içinde `unreadable`)

**Mevcut değil**

- localconfig.vdf dosyasının geri kalanı (arkadaşlar, sohbet, Steam ayarları): oyuna ait değil ve özel
- iki yazma arasındaki istatistik değerleri: Steam, oyun istatistiklerini sakladığında dosyayı yeniden yazar, genellikle oyun kapanırken
- genel başarım yüzdeleri ve diğer oyuncuların istatistikleri: bunlar Steam'in sunucularında, burada değil

**Boyut**: kayıt edilen oturum başına birkaç KB, artı şema (çok başarımı olan bir oyun için birkaç yüz KB'a kadar); saat başına oynama için bir MB'ın çok altında; zstd, şemanın metnini yarıya veya daha fazla küçültür

## Doğrulama {#verified}

Yerel bir kurulumdan alınan gerçek istatistik dosyaları ve şemalarla test edildi; değişiklik algılama, ikili KeyValues biçiminde oluşturulan dosyalarla test edildi.

## Kaynak {#source}

[heat3d_watch/adapters/platform.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/platform.py)

<!-- Generated from the adapter by tools/gen_game_pages.py; change the adapter and run it again rather than editing this page. -->
