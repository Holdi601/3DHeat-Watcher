---
title: "Squad (tekrarlar)"
nav_order: 40
lang: "tr"
source: game-squad-demos.md
source_hash: "a908f7e6d9c3"
nav_exclude: true
search_exclude: true
---
# Squad (tekrarlar) {#squad-replays}

Bir Squad maçı bittikten sonra watcher, oyunun kaydettiği tekrarı 3DHeat görüntüleyicisinde bir harita üzerinde bakabileceğiniz dosyalara çevirir.

*Teknik ayrıntılar: bağdaştırıcı `squad-demos`, tür [`replay`](sources-and-rules.md); sürekli çalışır (bir oyunun başlamasını beklemez) ve her 5 saniyede bir yeni veri arar.*

## Ne kaydedilir {#what-is-recorded}

- her oyuncunun konumu, gövde dönüşü ve hızı, sunucu her çoğalttığında (saniyede en fazla 8 kez), yaya olarak ve kara araçlarında
- her oyuncunun adı, takımı, fraksiyonu ve birliği; takım değişikliklerini izleyerek
- kaydedilmez: helikopterlerin hareketi, öldürmeler ve yerleştirilebilir nesneler — okuyucunun README dosyasına bakın

## Nereden gelir {#where-it-comes-from}

Squad'ın sunucu demoları, yönetici komutu AdminDemoRec ile kaydedilir: &lt;server>/SquadGame/Saved/Demos/\*.replay; dış okuyucu `heat3d-squad-demo` (exporters/ext/squad-demo) tarafından okunur

## Nasıl açılır {#how-to-switch-it-on}

Sunucuda kayıt alın: yöneticiye Admins.cfg dosyasında `demos` yetkisi verin, sonra oyunun konsolunda AdminDemoRec &lt;name> ve AdminDemoStop komutlarını çalıştırın; demoyu buraya kopyalayın ve okuyucuyu kurun: pip install -e &lt;3DHeat>/exporters/ext/squad-demo

Ortam değişkenlerinden gelen ayarlar:

- `HEAT3D_SQUAD_DEMO`: çeviricinin klasörü (klon ya da açılmış sürüm), kurulu değilse ya da watcher'ın yanında değilse

## Nasıl çalışır {#how-it-works}

Tekrarlar ve demolar: bir oyunun bir maç için kaydettikleri, maç bittikten sonra bir kez çevrilir.

Bir tekrar, çok oyunculu oyunlarda canlı arayüzün sakladığı her şeyi tutar: her oyuncunun konumu, olduğu yerde her öldürme. Oyunun oyuncuları için yazdığı bir dosyadır, bu yüzden okunması oyuna dokunmaz. Watcher, oyunların bunları kaydettiği klasörlere bakar, yeni bir dosya büyümeyi bırakana kadar bekler (aksi halde oyun hâlâ yazıyordur) ve bir çalışan iş parçacığında çevirir; böylece uzun bir çeviri watcher'ın geri kalanını durdurmaz.

Bir klasör ilk kez görüldüğünde içindeki tekrarlar yalnızca not edilir, çevrilmez: yıllarca demosu olan bir oyuncu, watcher'ı bir gün boyunca meşgul bulurdu. `python -m heat3d_watch replays <bağdaştırıcı> [klasör]` mevcut olanları istendiğinde çevirir.

#### Squad {#squad}

Squad'ın özel sunucuları, `demos` yetkisi olan bir yönetici AdminDemoRec &lt;name> (ve AdminDemoStop) komutunu çalıştırdığında, bir maçın demosunu `<server>/SquadGame/Saved/Demos/<name>.replay` klasörüne kaydeder. Bu, sunucunun çoğaltığı her şeyi, her oyuncunun hareketi dahil, tutan bir Unreal Engine ağ tekrarıdır. Watcher bunları kendisi okumaz: dış bir okuyucu okur (3DHeat Squad demo okuyucusu, `exporters/ext/squad-demo`, komut `heat3d-squad-demo`). Bu, okuyucudaki bir sorunun başka hiçbir şeye dokunmamasını sağlar. Yerel bir sunucunun yazdığı klasörlerdeki her yeni demo için, ya da kiralık bir sunucudan kopyalanan demolar için ayarlara eklenen bir klasörde çalıştırılır; sonuç `<map>/<match>.parquet` ve `<match>.match.json` olarak oturum klasörüne yazılır. Katman, harita, oyuncu sayısı ve maç süresi oturumun istatistikleri olur.

Aynı modül şunlara da hizmet eder: [Counter-Strike 2 (tekrarlar)](game-cs2-demos.md), [Dota 2 (tekrarlar)](game-dota-replays.md), [War Thunder (tekrarlar)](game-warthunder-replays.md), [World of Tanks (tekrarlar)](game-wot-replays.md), [World of Warships (tekrarlar)](game-wows-replays.md).

## Konumlar ve eksenler {#positions-and-axes}

| | |
|---|---|
| Konumlar kaydedilir | evet |
| Yukarı eksen | `z` |
| Birimler | Unreal birimleri (santimetre) |
| Görüntüleyici için aynalanır | yok |
| Birim ölçeği (`scale`: görüntüleyici konumları bununla çarpar) | 1 |

Bunlar her oturumun `meta.json` dosyasındaki (`axes`) ve oturumda konum varsa `heat.parquet` dosyasının altbilgisine yazılır; böylece 3DHeat görüntüleyicisi satırları kendi başına döndürüp ölçekler — bkz. [Veri](the-data.md).

## Çok oyunculu {#multiplayer}

- Online oynandığı olarak işaretli (`multiplayer`): **evet**. `games --markdown` bunu "izinli (yalnızca oyunun yayımladıklarını okur)" olarak gösterir.
- Tür `replay`: yalnızca oyunun veya platformun dışarı verdiklerini (oyunun kaydettiği tekrarları ve demoları) okur; bu yüzden çevrimiçi oyunda da, çevrimdışıyken de kaydeder. Bayrak yalnızca belleğin hiç okunup okunamayacağını belirler.
- Bellek: bu bağdaştırıcı belleği **asla** okumaz. Yalnızca `memory` bağdaştırıcıları bellek okur ve çevrimiçi oynandığı işaretli bir oyun için asla — bkz. [Kaynaklar ve kurallar](sources-and-rules.md).

## Kaydedilen istatistikler {#statistics-recorded}

Bu bağdaştırıcının kodunun adla ayarladığı istatistik anahtarları (her oturumun `meta.json` içindeki `stats` alanı ve `watcher.sqlite` dosyasındaki `stats` tablosu):

`layer`, `map`, `match_seconds`, `players`

Süslü parantez içindeki anahtar çalışma zamanında tamamlanır (`score.{team}` her takım için ayrı bir anahtardır). Oyunun alanlarından ya da oyunun kendi istatistik adlarından bir tablo alan anahtarlar bu listede yoktur; yukarıdaki "Ne kaydedilir" bölümü onları adlandırır.

## Eksiksizlik {#completeness}

Bu bağdaştırıcının çalıştırdığı çevirici, 3DHeat'in [çevirici kuralını](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md) izler: tekrarda ne varsa okunur ya da saklanır, asla atılmaz. Tabloya ve maç belgesine okunur; geri kalan her şey yanlarındaki yan dosyalarda bütün olarak saklanır ve maç belgesinin `selfCheck.completeness` alanında sayılır. Çeviricinin kendi belgesi neyi okuduğunu, neyi ham olarak sakladığını ve neyi okuyamadığını listeler.

## Doğrulama {#verified}

Okuyucu, herkese açık sunucu demolarında kontrol edilir (hareket, verinin taşıdığı hızla uyuşur; her satırın takımı askerinin fraksiyonuyla eşleşir) ve derlenmiş demolarda testlerle; bu kanca ise sahte bir komutla testlerle.

## Kaynak {#source}

[heat3d_watch/adapters/replays.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/replays.py)

<!-- Generated from the adapter by tools/gen_game_pages.py; change the adapter and run it again rather than editing this page. -->
