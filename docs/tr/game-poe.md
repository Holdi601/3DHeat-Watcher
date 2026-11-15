---
title: "Path of Exile (günlük dosyaları)"
nav_order: 35
lang: "tr"
source: game-poe.md
source_hash: "b5783b5a5690"
nav_exclude: true
search_exclude: true
---
# Path of Exile (günlük dosyaları) {#path-of-exile-log-files}

Path of Exile oynarken izleyici, oyunun yazdığı dosyaları okur ve ne olduğunu kaydeder; böylece bunlara daha sonra istatistik ve zaman çizelgesi olarak bakabilirsiniz.

*Teknik ayrıntılar: bağdaştırıcı `poe`, tür [`log`](sources-and-rules.md); `PathOfExile.exe`, `PathOfExile_x64.exe`, `PathOfExileSteam.exe`, `PathOfExile_x64Steam.exe`, `PathOfExileEGS.exe`, `PathOfExile_x64EGS.exe`, `PathOfExile_KG.exe` ya da `PathOfExile_x64_KG.exe` çalışırken çalışır ve yeni veri için her 0,5 saniyede bir bakar.*

## Ne kaydedilir {#what-is-recorded}

- girilen bölgeler, bölge seviyesi, bölge kimliği ve tohumuyla
- seviye atlamaları, sınıf ve seviyeyle
- ölümler ("has been slain")
- bölgeye giren ve çıkan oyuncular, içeri ve dışarı fısıltılar, ticaret istekleri, kabul edilen ticaretler
- bu oturumun her Client.txt satırı bütün olarak heat.raw.parquet içinde
- ölümler, kazanılan seviyeler, en yüksek seviye, girilen bölgeler, farklı bölgeler, fısıltılar, ticaret istekleri, ticaretler

## Kaynağı {#where-it-comes-from}

&lt;kurulum>\logs\Client.txt, Path of Exile ya da Path of Exile 2 (izlenir; kurulum klasörü çalışan çalıştırılabilir dosyanın klasörüdür)

## Nasıl açılır {#how-to-switch-it-on}

Hiçbir şeyi açmanız gerekmez: izleyici kaynağı, oyunun ya da platformun sunduğu haliyle okur.

## Nasıl çalışır {#how-it-works}

Path of Exile ve Path of Exile 2: istemci günlüğü, `<kurulum>\logs\Client.txt`.

İkisi de kuruluyken, kurulum klasörlerindeki tek bir Client.txt dosyasına ekler (açılışlar boyunca büyür). Satırlar şöyle görünür:

```text
2024/01/01 12:00:00 123456789 cff94598 [INFO Client 1234] : You have entered Lioneye's Watch.
2024/01/01 12:00:00 123456789 cff94598 [DEBUG Client 1234] Generating level 2 area "1_1_2" with seed 1
2024/01/01 12:00:00 123456789 cff94598 [INFO Client 1234] : Name (Witch) is now level 2
2024/01/01 12:00:00 123456789 cff94598 [INFO Client 1234] : Name has been slain.
2024/01/01 12:00:00 123456789 cff94598 [INFO Client 1234] @From Name: Hi, I would like to buy your ...
```

- yerel saat, bir milisaniye sayacı, bir karma, seviye ve iş parçacığı, ardından sohbet penceresinin gösterdiği şey. Mesajlar İngilizce istemcinin mesajlarıdır; başka bir dildeki istemci bunları çevirilmiş yazar ve burada anlaşılmaz. Hiçbiri bir konum vermez. Biçim Grinding Gear Games tarafından belgelenmemiştir; oyunun düz metin günlüğüdür ve topluluk araçlarının (ticaret yardımcıları, seviye rehberleri) yıllardır okuduğu gibi okunur - ör. olay listesi için <https://github.com/klayveR/poe-log-monitor> (MIT).

Kurulum klasörü, çalışan çalıştırılabilir dosyanın klasörüdür; o yoksa Steam kitaplıkları ve bağımsız istemcinin varsayılan klasörü aranır.

Bu oturumun her satırı bütün olarak oturumun ham yan dosyasında saklanır (3DHeat'in dönüştürücü kuralı), bir anlamı burada olsun ya da olmasın: `type` satırın köşeli parantez içindeki seviyesi ve kaydedicisidir (`INFO Client`, `DEBUG Client`, `WARN Client`, ...); parantezsiz damgalı bir satır `untagged`, zaman damgası olmayan bir satır `untimed`.

## Konumlar ve eksenler {#positions-and-axes}

| | |
|---|---|
| Kaydedilen konumlar | hayır |
| Yukarı ekseni | `y` |
| Birimler | konum kaydedilmez |
| Görüntüleyici için aynalama | yok |
| Birim ölçeği (`scale`: görüntüleyici konumları bununla çarpar) | 1 |

Bunlar her oturumun `meta.json` dosyasındaki (`axes`) ve konum içeren oturumlarda `heat.parquet` dosyasının sonundaki (footer) bilgiye yazılır; böylece 3DHeat görüntüleyicisi satırları kendisi döndürür ve ölçekler - bkz. [Veriler](the-data.md).

## Çok oyunculu {#multiplayer}

- Çevrimiçi oynanan olarak işaretlenmiş (`multiplayer`): **evet**. `games --markdown` bunu "izinli (yalnızca oyunun yayımladığını okur)" olarak gösterir.
- Tür `log`: yalnızca oyunun ya da platformun dışarı verdiğini okur (oyunun çalışırken yazdığı dosyalar). Bu yüzden çevrimiçi oyunda da çevrimdışı olduğu gibi kaydeder; bayrak yalnızca belleğin hiç okunup okunamayacağını belirler.
- Bellek: bu bağdaştırıcı **asla** okumaz. Yalnızca `memory` bağdaştırıcıları bellek okur ve çevrimiçi oynanan olarak işaretlenmiş bir oyun için asla okumaz - bkz. [Kaynaklar ve kurallar](sources-and-rules.md).

## Kaydedilen istatistikler {#statistics-recorded}

Bu bağdaştırıcının kodunun adla ayarladığı istatistik anahtarları (her oturumun `meta.json` içindeki `stats` ve `watcher.sqlite` içindeki `stats` tablosu):

`bad_lines`, `character_class`, `deaths`, `level`, `levels_gained`, `trade_requests_received`, `trade_requests_sent`, `trades`, `whispers`, `zones_distinct`, `zones_entered`

Parantez içindeki bir anahtar çalışma zamanında tamamlanır (`score.{team}` her takım için bir anahtardır). Kodun oyunun alanlarının tablosundan ya da oyunun kendi istatistik adlarından aldığı anahtarlar bu listede yer almaz; yukarıdaki "Ne kaydedilir" bölümü bunları adlandırır.

## Tamlık {#completeness}

İzleyici 3DHeat'in [dönüştürücü kuralını](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md) izler: kaynağın tuttuğu her şey okunur ya da saklanır, asla atılmaz. Satırların yanı sıra, bağdaştırıcının aldığı her paket, sayfa, satır ya da yanıt, oturumun `heat.raw.parquet` dosyasında bütün olarak saklanır (sütunlar `time`, `ms`, `type`, `used`, `payload`, `text` ve adla saklanan her alan; `used` satıra dönüşenleri işaretler). `meta.json` içindeki `selfCheck.completeness` her `type` değerini sayar - `lost` 0'dır.

**Okunan**

- `You have entered <bölge>`, önündeki `Generating level` satırının bölge seviyesi, bölge kimliği ve tohumuyla
- `<ad> (<sınıf>) is now level <n>`, `<ad> has been slain`, bölgeye giren ve çıkan oyuncular, içeri ve dışarı fısıltılar (bir ticaret isteği olup olmadığıyla birlikte), kabul edilen ve iptal edilen ticaretler

**Ham olarak saklanan**

- bu oturumun her satırı bütün olarak, `type` = köşeli parantez içindeki seviye ve kaydedici (`INFO Client`, `DEBUG Client`, `WARN Client`, `CRIT Client`, ...), bir satıra dönüştüğü yerde `used`: genel, ticaret, grup ve lonca sohbeti, `Connecting to instance server`, AFK ve DND bildirimleri, `/played` ve `/deaths` gibi sohbet komutlarının yanıtları, istemcinin yükleme ve motor satırları - saklanır, henüz satırlara dönüştürülmedi
- parantezsiz damgalı satır (`***** LOG FILE OPENING *****`) `untagged`, zaman damgası olmayan satır `untimed` olarak

**Kullanılamayanlar**

- konumlar: günlükteki hiçbir şey bir konum vermez
- başka bir dildeki istemcinin yazdıkları: satırlar saklanır, ama yalnızca İngilizce mesajlar satırlara dönüştürülür
- önceki açılışların satırları: Client.txt açılışlar boyunca büyür; oyunun bu çalışmasından önce damgalanmış satırlar bırakılır (oynanırken zaten saklandılar)
- öldürmeler, hasar, ganimet ve pasif ağaç: oyun bunları günlüğe yazmaz

**Boyut**: Client.txt saatte yaklaşık 0,3-3 MB büyür (çoğu bölge yüklenirken DEBUG satırlarından; yoğun ticaret sohbetiyle daha fazla); heat.raw.parquet içindeki zstd bunu yaklaşık onda bire indirir

## Doğrulama {#verified}

oyunun biçiminde sentetik Client.txt satırlarında test edilmiştir; oyunla test edilmemiştir

## Kaynak {#source}

[heat3d_watch/adapters/poe.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/poe.py)

<!-- Adaptörden tools/gen_game_pages.py ile üretilmiştir; sayfayı elle düzenlemek yerine adaptörü değiştirin ve yeniden çalıştırın. -->
