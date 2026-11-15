---
title: "VALORANT (tekrarlar)"
nav_order: 44
lang: "tr"
source: game-valorant-replays.md
source_hash: "617e23a33a4c"
nav_exclude: true
search_exclude: true
---
# VALORANT (tekrarlar) {#valorant-replays}

VALORANT'ta bir maçtan sonra izleyici, oyunun kaydettiği tekrarı, istatistikler ve bir zaman çizelgesi olarak bakabileceğiniz dosyalara çevirir.

*Teknik ayrıntılar: uyarlayıcı `valorant-replays`, tür [`replay`](sources-and-rules.md); her zaman çalışır (bir oyunun başlamasını beklemez) ve her 5 saniyede bir yeni veri arar.*

## Ne kaydedilir {#what-is-recorded}

- harita, maç kimliği ve seçilen ajanlar; tekrarın bilgi bloğu (uzunluk, sürümler, ad, kayıt zamanı, sıkıştırma ve şifreleme bayrakları)
- sunucunun olay zaman çizelgesi: öldürmeler (öldüren ve ölen, ağ kimlikleri olarak), başlayan turlar, dikilen spike'lar, etkisiz hale getirilenler ve patlayanlar, kullanılan ultimate'ler, taraf değiştirmeler - her biri kimliği ve üst verisiyle
- dosyanın her parçası heat.raw.parquet içinde bütün olarak; çözülmeyenler: konumlar, adlar veya skorlar - bunlar karıştırılmış akışın içindedir

## Veri nereden gelir {#where-it-comes-from}

VALORANT'ın kaydettiği tekrarlar: %LOCALAPPDATA%/VALORANT/Saved/Demos/\*.vrf (yalnızca karıştırılmamış kısımlar)

## Nasıl açılır {#how-to-switch-it-on}

VALORANT'ta bir tekrar kaydedin (kariyer > maç > tekrarı indir) ve okuyucuyu kurun: github.com/Holdi601/3DHeat-Ext-Riot (`heat3d-riot-replays`)

Ortam değişkenlerinden ayarlar:

- `HEAT3D_RIOT_REPLAYS`: okuyucunun klasörü (bir klon veya açılmış sürüm), kurulu değilse veya izleyicinin yanında değilse

## Nasıl çalışır {#how-it-works}

League of Legends ve Valorant tekrarları: bunların hangi kısmı olduğu gibi okunabilir.

İki oyun da tekrarları oyuncunun diskine kaydeder ve ikisi de içindekini korur: an be an oyun verisi karıştırılmıştır ve her yamayla farklı şekilde, hile yapmak için kullanılmasın diye. Bunu aşmak, oyunun kendi kodunu tersine mühendislikle açmak demektir; Riot'un koşulları bunu yasaklar (Hizmet Koşulları 3.1 ve 7.1) - bu yüzden 3DHeat'te hiçbir yerde yapılmaz. Her dosyanın açıkta taşıdığı şey okunur, geri kalanı olduğu gibi saklanır: dosyanın her parçası, bütün olarak, oturumun `heat.raw.parquet` dosyasında (3DHeat'in dönüştürücü kuralı; görüntüleyicinin deposundaki docs/converters.md), meta.json içindeki `selfCheck.completeness` ile sayılır.

İzleyici dosyaları kendisi okumaz: bunu harici bir okuyucu yapar (3DHeat Riot, github.com/Holdi601/3DHeat-Ext-Riot, `exporters/ext/riot-replays`, komut `heat3d-riot-replays`). Riot'un koşullarıyla ilgili bir sorunun yalnızca bu okuyucuya dokunması için ayrı tutulur. PATH üzerinde bulunursa, kuruluysa veya izleyicinin yanındaysa, her yeni tekrarı okur; yoksa izleyici nasıl kurulacağını bir kez söyler. Okuduğunu izleyici oturuma kaydeder; aşağıdaki Match-V5 zaman çizelgesi dosyada bulunmadığı için izleyicinin kendisi getirir.

#### Valorant (.vrf) {#valorant-vrf}

`%LOCALAPPDATA%\VALORANT\Saved\Demos\*.vrf`, bir Unreal Engine yerel tekrarı. Açıkta olanlar: tekrarın bilgi bloğu (uzunluk, ağ sürümü, değişiklik listesi, adı, ne zaman kaydedildiği, sıkıştırılmış veya şifreli olup olmadığı), harita, maç kimliği ve seçilen ajanlar (başlıkta), ve sunucunun kendi olay zaman çizelgesi - öldürmeler (öldüren ve ölen, ad değil ağ kimlikleri olarak), başlayan turlar, dikilen spike'lar, etkisiz hale getirilenler ve patlayanlar, kullanılan ultimate'ler, taraf değiştirmeler - her biri zamanı, kimliği ve üst verisiyle. Konumlar, adlar, skorlar ve diğer her şey karıştırılmış akıştadır (tekrar verisi ve kontrol noktası parçaları), bunlar bütün olarak saklanır ve okunmaz.

Bu modül şunlara da hizmet eder: [League of Legends (tekrarlar)](game-lol-replays.md).

## Konumlar ve eksenler {#positions-and-axes}

| | |
|---|---|
| Konumlar kaydedilir | hayır |
| Yukarı eksen | `z` |
| Birimler | VALORANT dünya birimleri |
| Görüntüleyici için aynalama | yok |
| Birim ölçeği (`scale`: görüntüleyici konumları bununla çarpar) | 1 |

Bunlar her oturumun `meta.json` dosyasındaki (`axes`) ve oturumda konum varsa `heat.parquet` dosyasının altbilgisine yazılır; böylece 3DHeat görüntüleyicisi satırları kendi başına döndürür ve ölçekler. Bkz. [Veriler](the-data.md).

## Çok oyunculu {#multiplayer}

- Çevrimiçi oynanan olarak işaretli (`multiplayer`): **evet**. `games --markdown` bunu "izinli (yalnızca oyunun yayınladığını okur)" olarak gösterir.
- Tür `replay`: yalnızca oyunun veya platformun dışarı verdiğini okur (oyunun kaydettiği tekrarlar ve demolar); bu yüzden çevrimiçi oyunda da kaydeder. Bayrak yalnızca belleğin hiç okunup okunamayacağını belirler.
- Bellek: bu uyarlayıcı **asla** okumaz. Yalnızca `memory` uyarlayıcıları bellek okur ve çevrimiçi oynanan olarak işaretli bir oyun için hiçbir zaman. Bkz. [Kaynaklar ve kurallar](sources-and-rules.md).

## Kaydedilen istatistikler {#statistics-recorded}

Bu uyarlayıcının kodunun ada göre ayarladığı istatistik anahtarları (her oturumun `meta.json` dosyasındaki `stats` ve `watcher.sqlite` dosyasındaki `stats` tablosu):

`kills_in_match`, `map`, `match_seconds`, `rounds`, `spikes_planted`

Süslü parantez içindeki bir anahtar çalışma zamanında tamamlanır (`score.{team}` her takım için ayrı bir anahtardır). Kodun oyunun alan tablosundan veya oyunun kendi istatistik adlarından aldığı anahtarlar bu listede yer almaz; yukarıdaki "Ne kaydedilir" bölümü onları adlandırır.

## Tamlık {#completeness}

İzleyici 3DHeat'in [dönüştürücü kuralını](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md) izler: kaynağın tuttuğu her şey okunur veya saklanır, hiçbir şey atılmaz. Satırların yanında, uyarlayıcının aldığı her paket, sayfa, satır veya yanıt oturumun `heat.raw.parquet` dosyasında bütün olarak saklanır (sütunlar `time`, `ms`, `type`, `used`, `payload`, `text` ve ada göre tutulan her alan; `used` satırlara da dönüşenleri işaretler). `meta.json` içindeki `selfCheck.completeness` her `type` değerini sayar; `lost` 0'dır.

**Okunan**

- bilgi bloğu, her alanı (meta.json `vrf`): dosya sürümü, özel sürümler, uzunluk, ağ sürümü, değişiklik listesi, ad, canlı bayrağı, kayıt zamanı, sıkıştırılmış ve şifreli bayrakları, kayıtlı haliyle anahtar
- başlık parçası: harita, maç kimliği ve seçilen ajanlar (biçimlerinden bulunarak)
- her olay parçası: kimlik, grup, üst veri, başlangıç ve bitiş zamanı ve verisinin olayın adı, saniye cinsinden zamanı ve önündeki sayılar (öldüren ve ölen ağ kimlikleri) - her biri bir satır

**Ham olarak saklanan**

- her parça bütün olarak, dosya sırasında (`offset`), böylece parçalar dosyanın kendisidir: `info`, `header`, `event <group>`, `replay_data`, `checkpoint`, düzenin adlandırmadığı bir tür için `chunk <n>`, son tam parçadan sonraki baytlar için `trailing`

**Mevcut olmayan**

- konumlar, adlar, skorlar, yetenekler, oyunun her karesi: tekrar verisi ve kontrol noktası parçaları karıştırılmıştır; bunları okumak, istemciyi tersine mühendislikle açmak demektir ve Riot'un koşulları bunu yasaklar. Bütün olarak saklanır, okunmaz
- şifreli bir tekrarın içeriği: yürünür ve bütün olarak saklanır, içinde hiçbir şey okunmaz

**Boyut**: ham yan dosya kabaca tekrarın kendi boyutudur: karıştırılmış akış sıkışmaz

## Doğrulama {#verified}

okuyucu (heat3d-riot-replays), vrfkit'in (Apache-2.0) belgelediği kap düzeninden kuruldu; gerçek bir tekrarda test edilmedi, hiçbiri bulunamadı - okumadan önce kontrol eder ve uymayanı atlar

## Kaynak {#source}

[heat3d_watch/adapters/riot_replays.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/riot_replays.py)

<!-- Adaptörden tools/gen_game_pages.py ile üretilmiştir; sayfayı elle düzenlemek yerine adaptörü değiştirin ve yeniden çalıştırın. -->
