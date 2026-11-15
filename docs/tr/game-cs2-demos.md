---
title: "Counter-Strike 2 (tekrarlar)"
nav_order: 8
lang: "tr"
source: game-cs2-demos.md
source_hash: "82fe00f0f2f0"
nav_exclude: true
search_exclude: true
---
# Counter-Strike 2 (tekrarlar) {#counter-strike-2-replays}

Bir Counter-Strike 2 maçı bittikten sonra watcher, oyunun kaydettiği tekrarı 3DHeat görüntüleyicisinde bir harita üzerinde bakabileceğiniz dosyalara çevirir.

*Teknik ayrıntılar: bağdaştırıcı `cs2-demos`, tür [`replay`](sources-and-rules.md); sürekli çalışır (bir oyunun başlamasını beklemez) ve her 5 saniyede bir yeni veri arar.*

## Ne kaydedilir {#what-is-recorded}

- her oyuncunun konumu, bakış yönü, canı ve parası (her 8. tikte bir)
- öldürmeler, ölümler, hasar, el bombaları, bomba koyma ve etkisizleştirmeler olduğu yerde
- turlar, skor, ekonomi; giriş yapmış oyuncunun skor tablosu satırı istatistik olarak

## Nereden gelir {#where-it-comes-from}

CS2'nin kaydettiği demolar: &lt;CS2>/game/csgo/replays/\*.dem (maç geçmişinden indirilen) ve &lt;CS2>/game/csgo/\*.dem (kaydedilen)

## Nasıl açılır {#how-to-switch-it-on}

Bir maçın demosunu CS2'de indirin (Watch > Your Matches), ya da konsoldaki `record` komutuyla kaydedin

Ortam değişkenlerinden gelen ayarlar:

- `HEAT3D_CS2`: 3DHeat CS2 klasörü; watcher'ın yanında değilse ya da kurulu değilse

## Nasıl çalışır {#how-it-works}

Tekrarlar ve demolar: bir oyunun bir maç için kaydettikleri, maç bittikten sonra bir kez çevrilir.

Bir tekrar, çok oyunculu oyunlarda canlı arayüzün sakladığı her şeyi tutar: her oyuncunun konumu, olduğu yerde her öldürme. Oyunun oyuncuları için yazdığı bir dosyadır, bu yüzden okunması oyuna dokunmaz. Watcher, oyunların bunları kaydettiği klasörlere bakar, yeni bir dosya büyümeyi bırakana kadar bekler (aksi halde oyun hâlâ yazıyordur) ve bir çalışan iş parçacığında çevirir; böylece uzun bir çeviri watcher'ın geri kalanını durdurmaz.

Bir klasör ilk kez görüldüğünde içindeki tekrarlar yalnızca not edilir, çevrilmez: yıllarca demosu olan bir oyuncu, watcher'ı bir gün boyunca meşgul bulurdu. `python -m heat3d_watch replays <bağdaştırıcı> [klasör]` mevcut olanları istendiğinde çevirir.

#### Counter-Strike 2 {#counter-strike-2}

CS2, oyuncunun maç geçmişinden (izle sekmesi) indirdiği demoları `<CS2>/game/csgo/replays/` klasörüne, `record` konsol komutuyla kaydedilenleri `<CS2>/game/csgo/` klasörüne yazar. Her biri bu deponun kendi CS2 çeviricisiyle çevrilir (3DHeat CS2, github.com/Holdi601/3DHeat-CS2: her oyuncunun konumu, bakış yönü, canı ve parası her sekizinci tikte; öldürmeler, ölümler, hasar, el bombaları, bomba koyma ve etkisizleştirmeler olduğu yerde; turlar, skor, ekonomi). Sonuç oturum klasörüne, görüntüleyicinin Isı haritası ve Maç sekmelerinin okuduğu `<map>/<match>.parquet` tablosu ve `<match>.match.json` özeti olarak yazılır. Maçın skor tablosu oturumun istatistiği olur: bu bilgisayarda Steam hesabı giriş yapmış olan oyuncu için (Steam'in `loginusers.vdf` dosyasından), düz adlarıyla — öldürme, ölüm, asist, ADR, KAST, kafa isabet yüzdesi, açılış öldürmeleri, clutch'lar — ve skor ile turlar.

Aynı modül şunlara da hizmet eder: [Dota 2 (tekrarlar)](game-dota-replays.md), [Squad (tekrarlar)](game-squad-demos.md), [War Thunder (tekrarlar)](game-warthunder-replays.md), [World of Tanks (tekrarlar)](game-wot-replays.md), [World of Warships (tekrarlar)](game-wows-replays.md).

## Konumlar ve eksenler {#positions-and-axes}

| | |
|---|---|
| Konumlar kaydedilir | evet |
| Yukarı eksen | `z` |
| Birimler | inç (Source birimleri) |
| Görüntüleyici için aynalanır | `y` |
| Birim ölçeği (`scale`: görüntüleyici konumları bununla çarpar) | 1 |

Bunlar her oturumun `meta.json` dosyasındaki (`axes`) ve oturumda konum varsa `heat.parquet` dosyasının altbilgisine yazılır; böylece 3DHeat görüntüleyicisi satırları kendi başına döndürüp ölçekler — bkz. [Veri](the-data.md).

## Çok oyunculu {#multiplayer}

- Online oynandığı olarak işaretli (`multiplayer`): **evet**. `games --markdown` bunu "izinli (yalnızca oyunun yayımladıklarını okur)" olarak gösterir.
- Tür `replay`: yalnızca oyunun veya platformun dışarı verdiklerini (oyunun kaydettiği tekrarları ve demoları) okur; bu yüzden çevrimiçi oyunda da, çevrimdışıyken de kaydeder. Bayrak yalnızca belleğin hiç okunup okunamayacağını belirler.
- Bellek: bu bağdaştırıcı belleği **asla** okumaz. Yalnızca `memory` bağdaştırıcıları bellek okur ve çevrimiçi oynandığı işaretli bir oyun için asla — bkz. [Kaynaklar ve kurallar](sources-and-rules.md).

## Kaydedilen istatistikler {#statistics-recorded}

Bu bağdaştırıcının kodunun adla ayarladığı istatistik anahtarları (her oturumun `meta.json` içindeki `stats` alanı ve `watcher.sqlite` dosyasındaki `stats` tablosu):

`map`, `rounds`, `score.{team}`, `won`

Süslü parantez içindeki anahtar çalışma zamanında tamamlanır (`score.{team}` her takım için ayrı bir anahtardır). Oyunun alanlarından ya da oyunun kendi istatistik adlarından bir tablo alan anahtarlar bu listede yoktur; yukarıdaki "Ne kaydedilir" bölümü onları adlandırır.

## Eksiksizlik {#completeness}

Bu bağdaştırıcının çalıştırdığı çevirici, 3DHeat'in [çevirici kuralını](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md) izler: tekrarda ne varsa okunur ya da saklanır, asla atılmaz. Tabloya ve maç belgesine okunur; geri kalan her şey yanlarındaki yan dosyalarda bütün olarak saklanır ve maç belgesinin `selfCheck.completeness` alanında sayılır. Çeviricinin kendi belgesi neyi okuduğunu, neyi ham olarak sakladığını ve neyi okuyamadığını listeler.

## Doğrulama {#verified}

Çevirici gerçek turnuva demolarında test edilir; klasör izleme ve istatistikler testlerle.

## Kaynak {#source}

[heat3d_watch/adapters/replays.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/replays.py)

<!-- Generated from the adapter by tools/gen_game_pages.py; change the adapter and run it again rather than editing this page. -->
