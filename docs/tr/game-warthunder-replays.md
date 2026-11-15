---
title: "War Thunder (tekrarlar)"
nav_order: 45
lang: "tr"
source: game-warthunder-replays.md
source_hash: "23676a6c5441"
nav_exclude: true
search_exclude: true
---
# War Thunder (tekrarlar) {#war-thunder-replays}

Bir War Thunder maçı bittikten sonra watcher, oyunun kaydettiği tekrarı 3DHeat görüntüleyicisinde bir harita üzerinde bakabileceğiniz dosyalara çevirir.

*Teknik ayrıntılar: bağdaştırıcı `warthunder-replays`, tür [`replay`](sources-and-rules.md); sürekli çalışır (bir oyunun başlamasını beklemez) ve her 5 saniyede bir yeni veri arar.*

## Ne kaydedilir {#what-is-recorded}

- her uçağın konumu ve duruşu, saniyede yaklaşık 4 kez (tekrarın tuttuğu kadar)
- kara birimlerinin konumları, tekrarın kara senkronizasyonundan (2026 tekrarlarında; 2025 tekrarlarında yok)
- her birimin kim olduğu (oyuncu, araç kimliği, takım), bir öldürme ya da isabet onu adlandırdığında; öldürmeler, ölümler ve isabetler olduğu yerde; sohbet; harita
- tekrarın yazarının öldürmeleri, ölümleri, skoru ve bölge ele geçirmeleri istatistik olarak

## Nereden gelir {#where-it-comes-from}

War Thunder'ın kaydettiği tekrarlar: &lt;War Thunder>/Replays/\*.wrpl (tekrar kaydetme açıkken), dış çevirici `heat3d-wt-replay` (exporters/ext/warthunder-replay) tarafından çevrilir

## Nasıl açılır {#how-to-switch-it-on}

War Thunder ayarlarında tekrar kaydetmeyi açın ve çeviriciyi kurun: pip install -e &lt;3DHeat>/exporters/ext/warthunder-replay

Ortam değişkenlerinden gelen ayarlar:

- `HEAT3D_WT_REPLAY`: çeviricinin klasörü (klon ya da açılmış sürüm), kurulu değilse ya da watcher'ın yanında değilse

## Nasıl çalışır {#how-it-works}

Tekrarlar ve demolar: bir oyunun bir maç için kaydettikleri, maç bittikten sonra bir kez çevrilir.

Bir tekrar, çok oyunculu oyunlarda canlı arayüzün sakladığı her şeyi tutar: her oyuncunun konumu, olduğu yerde her öldürme. Oyunun oyuncuları için yazdığı bir dosyadır, bu yüzden okunması oyuna dokunmaz. Watcher, oyunların bunları kaydettiği klasörlere bakar, yeni bir dosya büyümeyi bırakana kadar bekler (aksi halde oyun hâlâ yazıyordur) ve bir çalışan iş parçacığında çevirir; böylece uzun bir çeviri watcher'ın geri kalanını durdurmaz.

Bir klasör ilk kez görüldüğünde içindeki tekrarlar yalnızca not edilir, çevrilmez: yıllarca demosu olan bir oyuncu, watcher'ı bir gün boyunca meşgul bulurdu. `python -m heat3d_watch replays <bağdaştırıcı> [klasör]` mevcut olanları istendiğinde çevirir.

#### War Thunder {#war-thunder}

War Thunder, tekrar kaydetme seçeneği açıkken her savaşın tekrarını `<War Thunder>/Replays/*.wrpl` klasörüne kaydeder. Watcher bunları kendisi okumaz: dış bir çevirici okur (3DHeat War Thunder tekrar çeviricisi, `exporters/ext/warthunder-replay`, komut `heat3d-wt-replay`). Bu, çeviricideki bir sorunun başka hiçbir şeye dokunmamasını sağlar. Komut PATH üzerindeyse, ya da paket kuruluysa ya da watcher'ın yanındaysa, her yeni tekrar bu çeviriciden geçirilir ve sonuç `<map>/<match>.parquet` ve `<match>.match.json` olarak oturum klasörüne yazılır. Değilse, watcher bir kez nasıl kurulacağını söyler ve klasöre dokunmaz. Çeviricinin neyi okuyup neyi okumadığı README dosyasındadır. Tekrarın yazarının sonuç satırı — öldürmeler, kara öldürmeleri, ölümler, asistler, skor, bölge ele geçirmeleri — oturumun istatistikleri olur.

Aynı modül şunlara da hizmet eder: [Counter-Strike 2 (tekrarlar)](game-cs2-demos.md), [Dota 2 (tekrarlar)](game-dota-replays.md), [Squad (tekrarlar)](game-squad-demos.md), [World of Tanks (tekrarlar)](game-wot-replays.md), [World of Warships (tekrarlar)](game-wows-replays.md).

## Konumlar ve eksenler {#positions-and-axes}

| | |
|---|---|
| Konumlar kaydedilir | evet |
| Yukarı eksen | `y` |
| Birimler | metre (x doğu, y yukarı, z kuzey) |
| Görüntüleyici için aynalanır | `z` |
| Birim ölçeği (`scale`: görüntüleyici konumları bununla çarpar) | 1 |

Bunlar her oturumun `meta.json` dosyasındaki (`axes`) ve oturumda konum varsa `heat.parquet` dosyasının altbilgisine yazılır; böylece 3DHeat görüntüleyicisi satırları kendi başına döndürüp ölçekler — bkz. [Veri](the-data.md).

## Çok oyunculu {#multiplayer}

- Online oynandığı olarak işaretli (`multiplayer`): **evet**. `games --markdown` bunu "izinli (yalnızca oyunun yayımladıklarını okur)" olarak gösterir.
- Tür `replay`: yalnızca oyunun veya platformun dışarı verdiklerini (oyunun kaydettiği tekrarları ve demoları) okur; bu yüzden çevrimiçi oyunda da, çevrimdışıyken de kaydeder. Bayrak yalnızca belleğin hiç okunup okunamayacağını belirler.
- Bellek: bu bağdaştırıcı belleği **asla** okumaz. Yalnızca `memory` bağdaştırıcıları bellek okur ve çevrimiçi oynandığı işaretli bir oyun için asla — bkz. [Kaynaklar ve kurallar](sources-and-rules.md).

## Kaydedilen istatistikler {#statistics-recorded}

Bu bağdaştırıcının kodunun adla ayarladığı istatistik anahtarları (her oturumun `meta.json` içindeki `stats` alanı ve `watcher.sqlite` dosyasındaki `stats` tablosu):

`map`

Süslü parantez içindeki anahtar çalışma zamanında tamamlanır (`score.{team}` her takım için ayrı bir anahtardır). Oyunun alanlarından ya da oyunun kendi istatistik adlarından bir tablo alan anahtarlar bu listede yoktur; yukarıdaki "Ne kaydedilir" bölümü onları adlandırır.

## Eksiksizlik {#completeness}

Bu bağdaştırıcının çalıştırdığı çevirici, 3DHeat'in [çevirici kuralını](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md) izler: tekrarda ne varsa okunur ya da saklanır, asla atılmaz. Tabloya ve maç belgesine okunur; geri kalan her şey yanlarındaki yan dosyalarda bütün olarak saklanır ve maç belgesinin `selfCheck.completeness` alanında sayılır. Çeviricinin kendi belgesi neyi okuduğunu, neyi ham olarak sakladığını ve neyi okuyamadığını listeler.

## Doğrulama {#verified}

Çevirici, birkaç oyun sürümünden herkese açık tekrarlarda kontrol edilir (öldürmeler ve adlar sonuçlarla uyuşur) ve derlenmiş tekrarlarda testlerle; bu kanca ise sahte bir komutla testlerle.

## Kaynak {#source}

[heat3d_watch/adapters/replays.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/replays.py)

<!-- Generated from the adapter by tools/gen_game_pages.py; change the adapter and run it again rather than editing this page. -->
