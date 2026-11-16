---
title: "World of Warships (tekrarlar)"
nav_order: 48
lang: "tr"
source: game-wows-replays.md
source_hash: "e7d24a56747e"
nav_exclude: true
search_exclude: true
---
# World of Warships (tekrarlar) {#world-of-warships-replays}

Bir World of Warships maçı bittikten sonra watcher, oyunun kaydettiği tekrarı 3DHeat görüntüleyicisinde bir harita üzerinde bakabileceğiniz dosyalara çevirir.

*Teknik ayrıntılar: bağdaştırıcı `wows-replays`, tür [`replay`](sources-and-rules.md); sürekli çalışır (bir oyunun başlamasını beklemez) ve her 5 saniyede bir yeni veri arar.*

## Ne kaydedilir {#what-is-recorded}

- her geminin konumu ve yönü, kayıt yapan istemci onu gördüğü sürece (hareket halindeyken saniyede yaklaşık 6-7 kez); oyuncunun kendi gemisi baştan sona
- oyuncu, müttefik ya da düşman ve gemi (kaydı yapan oyuncunun gemisi adıyla, diğerleri oyunun gemi numarasıyla); batırılan gemiler battıkları yerde ve katilleri, durdukları yerde
- harita; kaydı yapan oyuncunun gemisi, öldürmeleri ve hayatta kalması istatistik olarak

## Nereden gelir {#where-it-comes-from}

World of Warships'in kaydettiği tekrarlar: &lt;World of Warships>/replays/\*.wowsreplay (tekrarlar açıkken), dış çevirici `heat3d-wows-replay` (exporters/ext/wows-replay) tarafından çevrilir

## Nasıl açılır {#how-to-switch-it-on}

World of Warships'te tekrar kaydını açın (`preferences.xml` içindeki `isReplayEnabled`, ya da oyunun kendi ayarı varsa o) ve çeviriciyi kurun: pip install -e &lt;3DHeat>/exporters/ext/wows-replay

Ortam değişkenlerinden gelen ayarlar:

- `HEAT3D_WOWS_REPLAY`: çeviricinin klasörü (klon ya da açılmış sürüm), kurulu değilse ya da watcher'ın yanında değilse

## Nasıl çalışır {#how-it-works}

Tekrarlar ve demolar: bir oyunun bir maç için kaydettikleri, maç bittikten sonra bir kez çevrilir.

Bir tekrar, çok oyunculu oyunlarda canlı arayüzün sakladığı her şeyi tutar: her oyuncunun konumu, olduğu yerde her öldürme. Oyunun oyuncuları için yazdığı bir dosyadır, bu yüzden okunması oyuna dokunmaz. Watcher, oyunların bunları kaydettiği klasörlere bakar, yeni bir dosya büyümeyi bırakana kadar bekler (aksi halde oyun hâlâ yazıyordur) ve bir çalışan iş parçacığında çevirir; böylece uzun bir çeviri watcher'ın geri kalanını durdurmaz.

Bir klasör ilk kez görüldüğünde içindeki tekrarlar yalnızca not edilir, çevrilmez: yıllarca demosu olan bir oyuncu, watcher'ı bir gün boyunca meşgul bulurdu. `python -m heat3d_watch replays <bağdaştırıcı> [klasör]` mevcut olanları istendiğinde çevirir.

#### World of Tanks ve World of Warships {#world-of-tanks-and-world-of-warships}

İkisi de kayıt açıkken her savaşın tekrarını `<oyun>/replays/` klasörüne kaydeder (`*.wotreplay`, `*.wowsreplay`); kurulumlar Wargaming Game Center'ın listesinden, `C:/Games/World_of_Tanks*` / `World_of_Warships*` yollarından ve Steam'den bulunur. War Thunder'da olduğu gibi watcher bu dosyaları kendisi okumaz: her biri için dış bir çevirici okur (`exporters/ext/wot-replay`, komut `heat3d-wot-replay`; `exporters/ext/wows-replay`, komut `heat3d-wows-replay`); her biri kendi başına bir projedir. PATH üzerinde, kurulu ya da watcher'ın yanında bulunursa, her yeni tekrarı oturum klasöründe `<map>/<match>.parquet` ve `<match>.match.json` olarak çevirir; yoksa watcher bir kez nasıl kurulacağını söyler. Kaydı yapan oyuncunun satırı — araç ya da gemi, öldürmeler, hasar (World of Tanks), hayatta kalıp kalmadığı ve sonuç (World of Tanks) — oturumun istatistikleri olur. Her çeviricinin neyi okuyup neyi okumadığı README dosyasındadır.

Aynı modül şunlara da hizmet eder: [Counter-Strike 2 (tekrarlar)](game-cs2-demos.md), [Dota 2 (tekrarlar)](game-dota-replays.md), [Squad (tekrarlar)](game-squad-demos.md), [War Thunder (tekrarlar)](game-warthunder-replays.md), [World of Tanks (tekrarlar)](game-wot-replays.md).

## Konumlar ve eksenler {#positions-and-axes}

| | |
|---|---|
| Konumlar kaydedilir | evet |
| Yukarı eksen | `y` |
| Birimler | World of Warships dünya birimleri (x doğu, y yukarı, z kuzey; gövde geometrisine göre bir birim 15 m, oyunun menzillerine göre 30 m) |
| Görüntüleyici için aynalanır | `z` |
| Birim ölçeği (`scale`: görüntüleyici konumları bununla çarpar) | 1 |

Bunlar her oturumun `meta.json` dosyasındaki (`axes`) ve oturumda konum varsa `heat.parquet` dosyasının altbilgisine yazılır; böylece 3DHeat görüntüleyicisi satırları kendi başına döndürüp ölçekler — bkz. [Veri](the-data.md).

## Çok oyunculu {#multiplayer}

- Online oynandığı olarak işaretli (`multiplayer`): **evet**. `games --markdown` bunu "izinli (yalnızca oyunun yayımladıklarını okur)" olarak gösterir.
- Tür `replay`: yalnızca oyunun veya platformun dışarı verdiklerini (oyunun kaydettiği tekrarları ve demoları) okur; bu yüzden çevrimiçi oyunda da, çevrimdışıyken de kaydeder. Bayrak yalnızca belleğin hiç okunup okunamayacağını belirler.
- Bellek: bu bağdaştırıcı belleği **asla** okumaz. Yalnızca `memory` bağdaştırıcıları bellek okur ve çevrimiçi oynandığı işaretli bir oyun için asla — bkz. [Kaynaklar ve kurallar](sources-and-rules.md).

## Kaydedilen istatistikler {#statistics-recorded}

Bu bağdaştırıcının kodunun adla ayarladığı istatistik anahtarları (her oturumun `meta.json` içindeki `stats` alanı ve `watcher.sqlite` dosyasındaki `stats` tablosu):

`map`, `survived`, `vehicle`, `won`

Süslü parantez içindeki anahtar çalışma zamanında tamamlanır (`score.{team}` her takım için ayrı bir anahtardır). Oyunun alanlarından ya da oyunun kendi istatistik adlarından bir tablo alan anahtarlar bu listede yoktur; yukarıdaki "Ne kaydedilir" bölümü onları adlandırır.

## Eksiksizlik {#completeness}

Bu bağdaştırıcının çalıştırdığı çevirici, 3DHeat'in [çevirici kuralını](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md) izler: tekrarda ne varsa okunur ya da saklanır, asla atılmaz. Tabloya ve maç belgesine okunur; geri kalan her şey yanlarındaki yan dosyalarda bütün olarak saklanır ve maç belgesinin `selfCheck.completeness` alanında sayılır. Çeviricinin kendi belgesi neyi okuduğunu, neyi ham olarak sakladığını ve neyi okuyamadığını listeler.

## Doğrulama {#verified}

Çevirici, birkaç oyun sürümünden herkese açık tekrarlarda kontrol edilir ve derlenmiş tekrarlarda testlerle; bu kanca ise sahte bir komutla testlerle.

## Kaynak {#source}

[heat3d_watch/adapters/replays.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/replays.py)

<!-- Generated from the adapter by tools/gen_game_pages.py; change the adapter and run it again rather than editing this page. -->
