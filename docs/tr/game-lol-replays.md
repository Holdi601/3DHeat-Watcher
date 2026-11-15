---
title: "League of Legends (tekrarlar)"
nav_order: 30
lang: "tr"
source: game-lol-replays.md
source_hash: "ed26619fa904"
nav_exclude: true
search_exclude: true
---
# League of Legends (tekrarlar) {#league-of-legends-replays}

League of Legends'ta bir maçtan sonra izleyici, istemcinin kaydettiği tekrarı, 3DHeat görüntüleyicisinde bir harita üzerinde bakabileceğiniz dosyalara çevirir.

*Teknik ayrıntılar: uyarlayıcı `lol-replays`, tür [`replay`](sources-and-rules.md); her zaman çalışır (bir oyunun başlamasını beklemez) ve her 5 saniyede bir yeni veri arar.*

## Ne kaydedilir {#what-is-recorded}

- her oyuncunun şampiyonu, rolü, takımı, öldürmeleri, ölümleri, asistleri, altını, şampiyonlara verilen hasarı ve sonucu; oyun sonu skor tablosunun diğer bütün sayıları
- kendi satırınız istatistik olarak, satırlarınız sizin olarak adlandırılmış (meta.json `player`), Riot ID'niz ayarlarda
- kendi Riot API anahtarınızla: her oyuncunun her dakikadaki konumu ve o dakikanın istatistikleri, ve zaman çizelgesinin verdiği duvar saati zamanında zaman çizelgesinin her olayı (öldürmeler olduğu yerde, binalar, canavarlar, gözetleme totemleri, eşyalar, yetenekler)
- tekrar dosyasının her parçası heat.raw.parquet içinde bütün olarak; çözülmeyenler: an be an oyun, çünkü hile yapmaya karşı şifrelenmiş ve karıştırılmıştır

## Veri nereden gelir {#where-it-comes-from}

League istemcisinin kaydettiği tekrarlar: %USERPROFILE%/Documents/League of Legends/Replays/\*.rofl (yalnızca düz oyun sonu üst verisi); kendi Riot Match-V5 API anahtarınızla Riot'un Match-V5 API'sinden maçın resmî zaman çizelgesi

## Nasıl açılır {#how-to-switch-it-on}

League istemcisinde bir tekrar kaydedin (maç geçmişi > indir) ve okuyucuyu kurun: github.com/Holdi601/3DHeat-Ext-Riot (`heat3d-riot-replays`); konumlar için `config --set` ile riot_api_key ve riot_platform ayarlayın

Ortam değişkenlerinden ayarlar:

- `HEAT3D_RIOT_REPLAYS`: okuyucunun klasörü (bir klon veya açılmış sürüm), kurulu değilse veya izleyicinin yanında değilse

## Nasıl çalışır {#how-it-works}

League of Legends ve Valorant tekrarları: bunların hangi kısmı olduğu gibi okunabilir.

İki oyun da tekrarları oyuncunun diskine kaydeder ve ikisi de içindekini korur: an be an oyun verisi karıştırılmıştır ve her yamayla farklı şekilde, hile yapmak için kullanılmasın diye. Bunu aşmak, oyunun kendi kodunu tersine mühendislikle açmak demektir; Riot'un koşulları bunu yasaklar (Hizmet Koşulları 3.1 ve 7.1) - bu yüzden 3DHeat'te hiçbir yerde yapılmaz. Her dosyanın açıkta taşıdığı şey okunur, geri kalanı olduğu gibi saklanır: dosyanın her parçası, bütün olarak, oturumun `heat.raw.parquet` dosyasında (3DHeat'in dönüştürücü kuralı; görüntüleyicinin deposundaki docs/converters.md), meta.json içindeki `selfCheck.completeness` ile sayılır.

İzleyici dosyaları kendisi okumaz: bunu harici bir okuyucu yapar (3DHeat Riot, github.com/Holdi601/3DHeat-Ext-Riot, `exporters/ext/riot-replays`, komut `heat3d-riot-replays`). Riot'un koşullarıyla ilgili bir sorunun yalnızca bu okuyucuya dokunması için ayrı tutulur. PATH üzerinde bulunursa, kuruluysa veya izleyicinin yanındaysa, her yeni tekrarı okur; yoksa izleyici nasıl kurulacağını bir kez söyler. Okuduğunu izleyici oturuma kaydeder; aşağıdaki Match-V5 zaman çizelgesi dosyada bulunmadığı için izleyicinin kendisi getirir.

#### League of Legends (.rofl) {#league-of-legends-rofl}

`%USERPROFILE%\Documents\League of Legends\Replays\*.rofl`. Her iki kap sürümü de oyun sonu skor tablosunu düz JSON olarak (`statsJson`) taşır: on oyuncunun her biri için şampiyon, öldürmeler, ölümler, asistler, altın, şampiyonlara verilen hasar, eşyalar, takım, rol, galibiyet, Riot ID'leri ve oyunun topladığı diğer her sayı (oyuncu başına yüzün üzerinde); hepsi oyuncunun `player_result` satırı olur. ROFL1 (yama 14.9 ve öncesi) sabit bir başlıktan sonra taşır (`RIOT\0\0`, 256 baytlık imza, ardından uzunluklar); ROFL2 (14.11 ve sonrası, `RIOT\2\0`) dosyanın sonundadır, uzunluğu son dört bayttadır (bir Riot mühendisi tarafından belirtildi, ReplayBook sorunu 299). ROFL1'in yük başlığı (oyun kimliği, uzunluk, parça ve keyframe sayıları, parça anahtarının uzunluğu) ve parça tablosu (kimlik, tür, uzunluk, sonraki parça, ofset) açıktadır ve okunur; parçaların kendisi şifrelidir ve okunmadan bütün olarak saklanır.

Konumlar dosyadan gelmez. Oyuncunun kendi Riot geliştirici anahtarıyla (ayarlardaki `riot_api_key`; kişisel bir anahtar tam da bunun için tasarlanmıştır, "(kendi) oyuncu istatistiklerini göstermek") maçın resmî zaman çizelgesi Riot'un Match-V5 API'sinden alınır: her oyuncunun dakikada bir konumu ve o dakikanın karesinin onlar hakkında söylediği her şey (altın, deneyim, seviye, minyonlar, şampiyon ve hasar istatistikleri), ve zaman çizelgesinin her olayı - öldürmeler, binalar, elit canavarlar, gözetleme totemleri, eşyalar, yetenekler, seviyeler - her biri bir satır, yeri varsa olduğu yerde. Anahtar yoksa hiçbir şey alınmaz ve hiçbir şey gönderilmez.

Bu modül şunlara da hizmet eder: [VALORANT (tekrarlar)](game-valorant-replays.md).

## Konumlar ve eksenler {#positions-and-axes}

| | |
|---|---|
| Konumlar kaydedilir | evet |
| Yukarı eksen | `y` |
| Birimler | Summoner's Rift harita birimleri (yaklaşık 15000 genişlik) |
| Görüntüleyici için aynalama | yok |
| Birim ölçeği (`scale`: görüntüleyici konumları bununla çarpar) | 1 |

Bunlar her oturumun `meta.json` dosyasındaki (`axes`) ve oturumda konum varsa `heat.parquet` dosyasının altbilgisine yazılır; böylece 3DHeat görüntüleyicisi satırları kendi başına döndürür ve ölçekler. Bkz. [Veriler](the-data.md).

## Çok oyunculu {#multiplayer}

- Çevrimiçi oynanan olarak işaretli (`multiplayer`): **evet**. `games --markdown` bunu "izinli (yalnızca oyunun yayınladığını okur)" olarak gösterir.
- Tür `replay`: yalnızca oyunun veya platformun dışarı verdiğini okur (oyunun kaydettiği tekrarlar ve demolar); bu yüzden çevrimiçi oyunda da kaydeder. Bayrak yalnızca belleğin hiç okunup okunamayacağını belirler.
- Bellek: bu uyarlayıcı **asla** okumaz. Yalnızca `memory` uyarlayıcıları bellek okur ve çevrimiçi oynanan olarak işaretli bir oyun için hiçbir zaman. Bkz. [Kaynaklar ve kurallar](sources-and-rules.md).

## Kaydedilen istatistikler {#statistics-recorded}

Bu uyarlayıcının kodunun ada göre ayarladığı istatistik anahtarları (her oturumun `meta.json` dosyasındaki `stats` ve `watcher.sqlite` dosyasındaki `stats` tablosu):

`champion`, `game_seconds`, `won`

Süslü parantez içindeki bir anahtar çalışma zamanında tamamlanır (`score.{team}` her takım için ayrı bir anahtardır). Kodun oyunun alan tablosundan veya oyunun kendi istatistik adlarından aldığı anahtarlar bu listede yer almaz; yukarıdaki "Ne kaydedilir" bölümü onları adlandırır.

## Tamlık {#completeness}

İzleyici 3DHeat'in [dönüştürücü kuralını](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md) izler: kaynağın tuttuğu her şey okunur veya saklanır, hiçbir şey atılmaz. Satırların yanında, uyarlayıcının aldığı her paket, sayfa, satır veya yanıt oturumun `heat.raw.parquet` dosyasında bütün olarak saklanır (sütunlar `time`, `ms`, `type`, `used`, `payload`, `text` ve ada göre tutulan her alan; `used` satırlara da dönüşenleri işaretler). `meta.json` içindeki `selfCheck.completeness` her `type` değerini sayar; `lost` 0'dır.

**Okunan**

- üst veri JSON'u: oyunun süresi, sürüm, son parça ve keyframe kimlikleri ve `statsJson` - her oyuncunun skor tablosunun her alanı, kendi `player_result` satırında (metin olarak verilen sayılar sayı olarak okunur)
- ROFL1: uzunluklar bloğu, yük başlığı (oyun kimliği, oyun uzunluğu, keyframe ve parça sayıları, başlangıç ve oyun başlangıcı parça kimlikleri, keyframe aralığı, parça anahtarı olduğu gibi) ve parça tablosu (kimlik, tür, uzunluk, sonraki parça, ofset) - meta.json içindeki `rofl` ve ham satırların `text` alanında
- ROFL2: sürüm metni
- Match-V5 zaman çizelgesi (yalnızca kendi API anahtarıyla): her katılımcı karesi bir `position` satırında (ya da yeri olmadığında `participant_frame`), bütün alanlarıyla düzleştirilmiş (`championStats.armor`, `damageStats.totalDamageDone`, `currentGold`, `xp`, ...); her olay, türünden adlandırılmış bir satır olarak, bir `position` varsa orada; CHAMPION_KILL bir öldürme ve bir ölüm olarak

**Ham olarak saklanan**

- .rofl dosyasının her parçası, dosya sırasında (`offset`) bütün olarak, böylece parçalar dosyanın kendisidir: `magic`, `signature`, `lengths`, `metadata`, `payload_header`, `chunk_header`, `chunk`, `keyframe` (ROFL1); `body`, `metadata`, `metadata_length` (ROFL2); hiçbir parçanın kapsamadığı her bölge `unknown`
- zaman çizelgesi bütün olarak: her olay için `timeline <type>`, her oyuncu karesi için `timeline participantFrame` (`participant` kimliği), kalanı için `timeline`

**Mevcut olmayan**

- oyunun kendisi (konumlar, yetenekler, her birim, an be an): ROFL1'in parçaları ve ROFL2'nin gövdesi şifrelidir ve içindeki paketler her yamayla karıştırılır; bunu aşmak, istemciyi tersine mühendislikle açmak demektir, Riot'un koşulları (3.1, 7.1) bunu yasaklar. Bütün olarak saklanır, okunmaz
- kendi Riot API anahtarınız olmadan konumlar: dosyada açıkta yoktur

**Boyut**: ham yan dosya kabaca tekrarın kendi boyutudur: şifreli parçalar sıkışmaz

## Doğrulama {#verified}

okuyucu (heat3d-riot-replays), roflxd.cs'deki (MIT) düzenlere göre kurulan dosyalarda test edildi; zaman çizelgesi Match-V5'in belgelenmiş JSON'unda; karşılaştırılacak gerçek bir tekrar bulunamadı

## Kaynak {#source}

[heat3d_watch/adapters/riot_replays.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/riot_replays.py)

<!-- Adaptörden tools/gen_game_pages.py ile üretilmiştir; sayfayı elle düzenlemek yerine adaptörü değiştirin ve yeniden çalıştırın. -->
