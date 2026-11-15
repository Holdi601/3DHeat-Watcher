---
title: "Minecraft (günlük dosyaları)"
nav_order: 33
lang: "tr"
source: game-minecraft.md
source_hash: "35cfea9d36a0"
nav_exclude: true
search_exclude: true
---
# Minecraft (günlük dosyaları) {#minecraft-log-files}

Minecraft oynarken izleyici, oyunun yazdığı dosyaları okur ve olanları kaydeder; böylece bunlara daha sonra 3DHeat görüntüleyicisinde bir harita üzerinde bakabilirsiniz.

*Teknik ayrıntılar: uyarlayıcı `minecraft`, tür [`log`](sources-and-rules.md); `javaw.exe` veya `java.exe` çalışırken çalışır ve her 0,5 saniyede bir yeni veri arar.*

## Ne kaydedilir {#what-is-recorded}

- kendi ve diğer oyuncuların konumu (bloklar = m, y yukarı), dünya her kaydedildiğinde; boyut oturum olarak
- bir oyuncu (tümleşik) sunucuya girdiğinde konumuyla birlikte doğuş
- katılmalar, ayrılmalar, ölüm mesajıyla ölümler, gelişmeler, sohbet satırları
- ölümler, gelişmeler, sohbet mesajları; istatistik dosyasından: oynama süresi, mesafe, yaratık ve oyuncu öldürmeleri, zıplamalar, hasar, kazılan bloklar, yapılan eşyalar (bu oturumun payı)
- her günlük satırı ve kaydedilen her istatistik, gelişme ve oyuncu dosyası heat.raw.parquet içinde bütün olarak

## Veri nereden gelir {#where-it-comes-from}

%APPDATA%\\.minecraft\logs\latest.log (izlenir), saves\\&lt;dünya>\stats\\&lt;uuid>.json ve saves\\&lt;dünya>\playerdata\\&lt;uuid>.dat / level.dat (gzip NBT), oyun kaydettiğinde okunur

## Nasıl açılır {#how-to-switch-it-on}

Hiçbir şeyi açmanız gerekmez: izleyici kaynağı, oyunun veya platformun sunduğu haliyle okur.

## Nasıl çalışır {#how-it-works}

Minecraft (Java Edition): oyunun yazdığı günlük, istatistik ve oyuncu dosyaları.

Konum (`%APPDATA%\.minecraft\`):

* `logs\latest.log` - oyunun günlüğü, her açılışta yeni (eski olan tarihli bir .log.gz dosyasına sıkıştırılır). `[hh:mm:ss] [thread/LEVEL]: message` biçiminde satırlar (mod yükleyicileri `[ddMMMyyyy hh:mm:ss.mmm] [thread/LEVEL] [logger/]: ...` yazar). Oyuncuların sohbette gördükleri de buradadır: katılmalar ve ayrılmalar, ölüm mesajları, gelişmeler, sohbet - tek oyunculu bir dünyanın tümleşik sunucusu aynı satırları bir kez daha yazar, bu yüzden aynı saniye içinde tekrarlanan bir satır bir kez sayılır. "Setting user: <ad>" oyuncuyu adlandırır; sunucunun "<ad>[...] logged in with entity id N at (x, y, z)" satırı nerede belirdiklerini verir.
* `saves\<dünya>\stats\<uuid>.json` - istatistik ekranı, dünya kaydedildiğinde yazılır (birkaç dakikada bir otomatik kayıt ve ayrılırken): `stats` -> `minecraft:custom` (play_time tik cinsinden, mob_kills, \*_one_cm mesafeler, jump, ...), `minecraft:mined`, `minecraft:crafted`, ... Dünya için toplamlar; oturumun rakamları, oyun başladığında dosyanın söylediğiyle olan farktır. Biçim: <https://minecraft.wiki/w/Statistics>
* `saves\<dünya>\playerdata\<uuid>.dat` (ve tek oyunculu bir ev sahibi için `level.dat` -> Data -> Player) - aynı kayıtlarda yazılan gzip sıkıştırılmış NBT: `Pos` [x, y, z] çift duyarlıklı sayılar, `Rotation` [yaw, pitch], `Dimension` ("minecraft:overworld"; 1.16 öncesinde 0/-1/1 int). NBT biçimi <https://minecraft.wiki/w/NBT_format> adresine göre - burada bizim küçük okuyucumuzla okunur.
* `saves\<dünya>\advancements\<uuid>.json` - gelişme ekranının ilerlemesi, aynı kayıtlarda yazılır.

Koordinatlar bloktur, bir blok bir metredir, y yukarı; x doğu, z güney - sağ el çerçevesi, olduğu gibi çizilir. Konumlar yalnızca dünya kaydedildiğinde gelir; bu yüzden bir rota, bir iz değil, her otomatik kayıtta birkaç noktadır; boyut `session` olur, böylece Nether, Overworld'ün üstüne çizilmez.

Okunan her şey oturumun ham yan dosyasında bütün olarak saklanır (3DHeat'in dönüştürücü kuralı): her latest.log satırı seviyesi altında (`INFO`, `WARN`, `ERROR`, ...; köşeli parantezli başı olmayan bir satır, örneğin yığın izi, `untagged` olarak), ve kaydedilen her dosya türü altında (`stats`, `advancements`, `playerdata`, `level.dat`) - JSON metin olarak, NBT baytları olarak. Bir istatistik dosyasının sayıları yalnızca oyun başladığında söylediğiyle anlaşılır; bu yüzden o ilk kopya da saklanır (`baseline`), dosya ilk kez değiştiğinde.

## Konumlar ve eksenler {#positions-and-axes}

| | |
|---|---|
| Konumlar kaydedilir | evet |
| Yukarı eksen | `y` |
| Birimler | blok (1 blok = 1 m) |
| Görüntüleyici için aynalama | yok |
| Birim ölçeği (`scale`: görüntüleyici konumları bununla çarpar) | 1 |

Bunlar her oturumun `meta.json` dosyasındaki (`axes`) ve oturumda konum varsa `heat.parquet` dosyasının altbilgisine yazılır; böylece 3DHeat görüntüleyicisi satırları kendi başına döndürür ve ölçekler. Bkz. [Veriler](the-data.md).

## Çok oyunculu {#multiplayer}

- Çevrimiçi oynanan olarak işaretli (`multiplayer`): **evet**. `games --markdown` bunu "izinli (yalnızca oyunun yayınladığını okur)" olarak gösterir.
- Tür `log`: yalnızca oyunun veya platformun dışarı verdiğini okur (oyunun çalışırken yazdığı dosyalar); bu yüzden çevrimiçi oyunda da kaydeder. Bayrak yalnızca belleğin hiç okunup okunamayacağını belirler.
- Bellek: bu uyarlayıcı **asla** okumaz. Yalnızca `memory` uyarlayıcıları bellek okur ve çevrimiçi oynanan olarak işaretli bir oyun için hiçbir zaman. Bkz. [Kaynaklar ve kurallar](sources-and-rules.md).

## Kaydedilen istatistikler {#statistics-recorded}

Bu uyarlayıcının kodunun ada göre ayarladığı istatistik anahtarları (her oturumun `meta.json` dosyasındaki `stats` ve `watcher.sqlite` dosyasındaki `stats` tablosu):

`advancements`, `bad_files`, `bad_lines`, `chat_messages`, `deaths`, `joins`, `others_deaths`, `world`

Süslü parantez içindeki bir anahtar çalışma zamanında tamamlanır (`score.{team}` her takım için ayrı bir anahtardır). Kodun oyunun alan tablosundan veya oyunun kendi istatistik adlarından aldığı anahtarlar bu listede yer almaz; yukarıdaki "Ne kaydedilir" bölümü onları adlandırır.

## Tamlık {#completeness}

İzleyici 3DHeat'in [dönüştürücü kuralını](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md) izler: kaynağın tuttuğu her şey okunur veya saklanır, hiçbir şey atılmaz. Satırların yanında, uyarlayıcının aldığı her paket, sayfa, satır veya yanıt oturumun `heat.raw.parquet` dosyasında bütün olarak saklanır (sütunlar `time`, `ms`, `type`, `used`, `payload`, `text` ve ada göre tutulan her alan; `used` satırlara da dönüşenleri işaretler). `meta.json` içindeki `selfCheck.completeness` her `type` değerini sayar; `lost` 0'dır.

**Okunan**

- latest.log: oyuncunun adı (`Setting user`), konumuyla girişler, katılmalar, ayrılmalar, ölüm mesajıyla ölümler, gelişmeler, sohbet satırları, sunucunun durması
- stats/<uuid>.json: oynama süresi, mesafe, yaratık ve oyuncu öldürmeleri, zıplamalar, verilen ve alınan hasar, kazılan bloklar, yapılan eşyalar - bu oturumun payı
- playerdata/<uuid>.dat ve level.dat (NBT): konum, boyut, yaw, pitch, can, XP seviyesi

**Ham olarak saklanan**

- her latest.log satırı bütün olarak, `type` = seviyesi (`INFO`, `WARN`, `ERROR`, `DEBUG`, `FATAL`), iş parçacığı `thread` içinde, satır olduğu yerde `used`; köşeli parantezli başı olmayan bir satır (yığın izi, bir modun başlığı) `untagged`
- her stats/<uuid>.json metin olarak bütün olarak, `type` `stats` (`used`: sayıları istatistiklerde), oyunun başlangıcındaki ilk kopyası `baseline` olarak
- her advancements/<uuid>.json metin olarak bütün olarak, `type` `advancements` (her ölçüt ve ne zaman karşılandığı; henüz satır yapılmadı)
- her playerdata/<uuid>.dat ve level.dat bayt olarak bütün olarak (gzip NBT), `type` `playerdata` / `level.dat`, konum verdiği yerde `used`: envanter, ender sandığı, efektler, doğuş noktası, oyun kuralları, dünya tohumu ve zamanı yalnızca burada bulunur
- kaydedilen her dosyanın `world` ve `file` (`saves` altındaki yolu) değerleri var

**Mevcut olmayan**

- bir konum izi: oyun oyuncunun konumunu yalnızca dünya kaydedildiğinde yazar (birkaç dakikada bir ve ayrılırken)
- başkasının barındırdığı bir sunucudaki konumlar: dünya dosyaları sunucudadır, burada değil; yalnızca günlük okunur
- dünyanın kendisi (region .mca dosyaları, varlıklar, data/\*.dat haritaları ve baskınlar): büyük ve oyunun değil arazinin verisi
- önceki oturumların günlükleri (logs/\*.log.gz): oynandıklarında saklanır
- Bedrock Edition: böyle bir günlük veya dosya yazmaz

**Boyut**: latest.log saatte 0,1-2 MB (modlarla daha fazla); bir istatistik dosyası otomatik kayıt başına 5-50 KB, bir oyuncu dosyası 5-100 KB, level.dat 1-20 KB - toplamda saatte yaklaşık 1-5 MB; heat.raw.parquet içindeki zstd metni yaklaşık onda bire indirir (NBT dosyaları zaten gzip'lidir)

## Doğrulama {#verified}

sentetik günlük satırları, istatistik JSON'u ve yayınlanmış biçimlerden kurulan NBT dosyalarında test edildi; oyunda test edilmedi

## Kaynak {#source}

[heat3d_watch/adapters/minecraft.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/minecraft.py)

<!-- Adaptörden tools/gen_game_pages.py ile üretilmiştir; sayfayı elle düzenlemek yerine adaptörü değiştirin ve yeniden çalıştırın. -->
