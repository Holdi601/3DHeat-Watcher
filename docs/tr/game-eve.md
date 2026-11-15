---
title: "EVE Online (günlük dosyaları)"
nav_order: 20
lang: "tr"
source: game-eve.md
source_hash: "a5ab6c312c86"
nav_exclude: true
search_exclude: true
---
# EVE Online (günlük dosyaları) {#eve-online-log-files}

EVE Online oynarken izleyici, oyunun yazdığı dosyaları okur ve ne olduğunu kaydeder; böylece bunlara daha sonra istatistik ve zaman çizelgesi olarak bakabilirsiniz.

*Teknik ayrıntılar: bağdaştırıcı `eve`, tür [`log`](sources-and-rules.md); `exefile.exe` çalışırken çalışır ve yeni veri için her 0,5 saniyede bir bakar.*

## Ne kaydedilir {#what-is-recorded}

- başka bir gemiye verilen ve alınan hasar, o pilot, şirket kısaltması, silah ve isabet kalitesiyle
- verilen ve alınan ıskalamalar
- ödenen ödüller (NPC öldürmeleri) ISK ile
- sistemler arasındaki atlamalar
- her gamelog ve sohbet günlüğü satırı, bütün olarak heat.raw.parquet içinde
- verilen ve alınan hasar, isabetler, ıskalamalar, ödül öldürmeleri ve ISK, atlamalar

## Kaynağı {#where-it-comes-from}

%USERPROFILE%\Documents\EVE\logs\Gamelogs\\\*.txt ve yanlarındaki Chatlogs\\\*.txt (istemci başladığından beri yazılan her dosya)

## Nasıl açılır {#how-to-switch-it-on}

Hiçbir şeyi açmanız gerekmez: izleyici kaynağı, oyunun ya da platformun sunduğu haliyle okur.

## Nasıl çalışır {#how-it-works}

EVE Online: istemcinin oyun günlükleri, `Documents\EVE\logs\Gamelogs\*.txt`.

İstemci her karakter ve her girişte bir dosya yazar: `<yyyymmdd>_<hhmmss>[_<karakter kimliği>].txt`; günlük tutma varsayılan olarak açıktır. Yan yana çalışan birkaç istemci her biri kendi dosyasını yazar; bu yüzden oyun başladığından beri yazılan her dosya izlenir. Başlık ve satırlar (EVE saati UTC'dir):

```text
------------------------------------------------------------
  Gamelog
  Listener: Character Name
  Session Started: 2024.07.02 19:41:40
------------------------------------------------------------
[ 2024.07.02 20:31:28 ] (combat) <color=0xff00ffff><b>200</b> <color=0x77ffffff><font size=10>to</font>
    <b><color=0xffffffff>Pilot[TICK](../Ship)</b><font size=10><color=0x77ffffff> - Weapon - Penetrates
[ 2024.06.25 15:20:01 ] (combat) <color=0xffcc0000><b>375</b> ... from ... - Weapon - Hits
[ 2024.06.25 15:21:00 ] (bounty) <font size=12><b><color=0xff00aa00>15,000 ISK</b> added to next bounty payout
[ 2024.06.25 15:30:00 ] (None) Jumping from System A to System B
```

(combat satırı dosyada tek satırdır). Eşleştirmeden önce biçim etiketleri (`<color>`, `<b>`, `<font>`) silinir. Dosya yıllar içinde hem UTF-8 hem UTF-16 olmuştur; ikisi de okunur. Biçim CCP tarafından belgelenmemiştir; istemcinin düz metin günlüğüdür ve topluluk savaş günlüğü araçlarının okuduğu gibi okunur (ör. <https://docs.rs/crate/eve-log-parser>). Konum yoktur.

Yanında, `Documents\EVE\logs\Chatlogs\<kanal>_<yyyymmdd>_<hhmmss>[_<kimlik>].txt`: sohbet kanalı başına ve giriş başına bir dosya (sohbet günlüğü açıkken, istemcinin varsayılanı); UTF-16, kanalın ve dinleyicinin adını taşıyan bir başlık, ardından `[ yyyy.mm.dd hh:mm:ss ] Sender > message`.

İkisinin her satırı bütün olarak oturumun ham yan dosyasında saklanır (3DHeat'in dönüştürücü kuralı): bir gamelog satırı, köşeli parantez içindeki kanalı altında (`combat`, `notify`, `bounty`, `None`, ...), bir sohbet satırı `chat` ve kanalıyla birlikte, başlık satırları `gamelog header` / `chatlog header` olarak.

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

`bad_lines`, `bounty_isk`, `bounty_kills`, `damage_dealt`, `damage_received`, `hits_dealt`, `hits_received`, `jumps`, `misses_dealt`, `misses_received`

Parantez içindeki bir anahtar çalışma zamanında tamamlanır (`score.{team}` her takım için bir anahtardır). Kodun oyunun alanlarının tablosundan ya da oyunun kendi istatistik adlarından aldığı anahtarlar bu listede yer almaz; yukarıdaki "Ne kaydedilir" bölümü bunları adlandırır.

## Tamlık {#completeness}

İzleyici 3DHeat'in [dönüştürücü kuralını](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md) izler: kaynağın tuttuğu her şey okunur ya da saklanır, asla atılmaz. Satırların yanı sıra, bağdaştırıcının aldığı her paket, sayfa, satır ya da yanıt, oturumun `heat.raw.parquet` dosyasında bütün olarak saklanır (sütunlar `time`, `ms`, `type`, `used`, `payload`, `text` ve adla saklanan her alan; `used` satıra dönüşenleri işaretler). `meta.json` içindeki `selfCheck.completeness` her `type` değerini sayar - `lost` 0'dır.

**Okunan**

- gamelog `(combat)` satırlarındaki verilen ve alınan isabetler (miktar, diğer pilot, şirket kısaltması, gemi, silah, isabet kalitesi) ve iki yönde ıskalamalar
- gamelog `(bounty)` ödemeleri ISK ile, ve `Jumping from A to B` satırları
- gamelog başlığındaki Listener: bu günlüğün kime ait olduğu

**Ham olarak saklanan**

- her gamelog satırı bütün olarak, `type` = köşeli parantez içindeki kanalı (`combat`, `notify`, `info`, `bounty`, `mining`, `question`, `hint`, `warning`, `None`, ...), `file` ve `listener` ile; bir satıra dönüştüğü yerde `used`; başlık satırları `gamelog header` olarak
- her sohbet günlüğü satırı bütün olarak (Local, corporation, fleet, özel kanallar, `EVE System` bildirimleri, örneğin bir atlamada Local kanalının değişmesi), `type` `chat`, `channel`, `listener` ve `file` ile; başlık satırları `chatlog header` olarak. Henüz satırlara dönüştürülmedi
- biçim etiketleri (`<color>`, `<b>`, `<font>`) ham metinde kalır; satırlarda silinir

**Kullanılamayanlar**

- konumlar: istemci günlüklerine hiç yazmaz
- diğer pilotların savaşları: bir gamelog dinleyicinin kendisine aittir
- önceki girişlerin günlükleri: her giriş yeni dosyalar yazar; istemcinin bu çalışmasından önce olanlar yeniden okunmaz
- oyuncu istemcinin ayarlarında sohbet günlüğünü kapattıysa sohbet
- istemcinin kendi önbellek ve ayar dosyaları: günlük değil ve belgelenmemiştir

**Boyut**: bir gamelog saatte 0,1-2 MB (çoğu savaşta); sohbet günlükleri açık kanallara bağlıdır - yoğun bir Local ya da fleet kanalı saatte 0,5-3 MB; heat.raw.parquet içindeki zstd bunu yaklaşık onda bire indirir

## Doğrulama {#verified}

topluluk ayrıştırıcılarının yayımladığı biçimdeki sentetik gamelog satırlarında test edilmiştir; oyunla test edilmemiştir

## Kaynak {#source}

[heat3d_watch/adapters/eve.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/eve.py)

<!-- Adaptörden tools/gen_game_pages.py ile üretilmiştir; sayfayı elle düzenlemek yerine adaptörü değiştirin ve yeniden çalıştırın. -->
