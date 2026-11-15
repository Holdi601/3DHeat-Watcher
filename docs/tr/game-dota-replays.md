---
title: "Dota 2 (tekrarlar)"
nav_order: 12
lang: "tr"
source: game-dota-replays.md
source_hash: "c0ed25c261f6"
nav_exclude: true
search_exclude: true
---
# Dota 2 (tekrarlar) {#dota-2-replays}

Dota 2 maçından sonra izleyici, oyunun kaydettiği tekrarı 3DHeat görüntüleyicisinde bir harita üzerinde bakabileceğiniz dosyalara çevirir.

*Teknik ayrıntılar: adaptör `dota-replays`, tür [`replay`](sources-and-rules.md); her zaman çalışır (bir oyunun başlamasını beklemez) ve her 5 s'de bir yeni veri arar.*

## Neler kaydedilir {#what-is-recorded}

- her kahramanın konumu, yüksekliği, cani ve seviyesi, hayattayken saniyede 7.5 kez
- öldürmeler ve ölümler olduğu yerde; kuleler, kışlalar, Roshan ve Tormentor'lar yıkıldıkları yerde; gözetleme noktaları konulduğu yerde
- her oyuncunun harita işaretleri, harita çizimleri ve emirleri (hareket, saldırı, büyü, satın alma, ...) işaret ettikleri yerde
- skor ve her oyuncunun satırı; oturum açmış oyuncunun satırı istatistik olarak
- tekrarın tuttuğu her şey, tablonun yanında bütün olarak: her çerçeve ve ağ iletisi, her varlık özelliği değişikliği, her dize tablosu girdisi

## Nereden gelir {#where-it-comes-from}

Dota 2'nin kaydettiği tekrarlar: &lt;Dota>/game/dota/replays/&lt;match id>.dem (istemcide indirilmiş ya da `dota-replay <match id>` ile)

## Nasıl açılır {#how-to-switch-it-on}

Dota 2'de bir maçın tekrarını indirin ya da herkese açık birini alın: `python -m heat3d_watch dota-replay <match id>`; okuyucuyu kurun: github.com/Holdi601/3DHeat-Ext-DotaReplay (`heat3d-dota-replay`, gem-dota'yı getirir)

Komutu, izleyicinin klasöründe açılmış bir terminale yazın (bkz. [Başlamadan önce](before-you-start.md)). Başarısız olursa son satır nedenini söyler; [Kurulum ve çalıştırma](installing-and-running.md) sık görülen nedenleri anlatır.

Ortam değişkenlerinden gelen ayarlar:

- `HEAT3D_DOTA_REPLAY`: okuyucunun klasörü (bir klon ya da açılmış sürüm), kurulu değilse ya da izleyicinin yanında değilse

## Nasıl çalışır {#how-it-works}

Tekrarlar ve demolar: oyunun bir maç için kaydettiği şey; maç bittikten sonra bir kez dönüştürülür.

Tekrar, canlı bir arayüzün çok oyunculu oyunlarda sakladığı her şeyi tutar - her oyuncunun konumu, her öldürme olduğu yerde - ve oyuncular için oyunun yazdığı bir dosyadır; bu yüzden onu okumak oyuna dokunmaz. İzleyici, oyunların tekrarları kaydettiği klasörlere bakar, yeni bir dosyanın büyümeyi bırakmasını bekler (aksi halde oyun hâlâ yazıyordur) ve onu bir çalışan iş parçacığında dönüştürür; böylece uzun bir dönüştürme izleyicinin geri kalanını asla durdurmaz.

Bir klasör ilk kez görüldüğünde, içindeki tekrarlar yalnızca not edilir, dönüştürülmez: yıllarca demosu olan bir oyuncu, izleyicinin bir gün boyunca meşgul olduğunu görmesin diye. `python -m heat3d_watch replays <adapter> [folder]`, mevcut olanları istek üzerine dönüştürür.

#### Dota 2 {#dota-2}

Dota 2, oyuncunun indirdiği tekrarları (bir maçın ayrıntıları ya da İzle > Tekrarlar) `<Dota>/game/dota/replays/<match id>.dem` içine kaydeder; Valve, her herkese açık maçın tekrarını birkaç hafta sunucularında tutar ve `python -m heat3d_watch dota-replay <match id>` komutu, kimliğiyle birini OpenDota üzerinden getirir. İzleyici bunları kendisi okumaz: harici bir okuyucu okur (3DHeat Dota Replay, github.com/Holdi601/3DHeat-Ext-DotaReplay, `exporters/ext/dota-replay`, komut `heat3d-dota-replay`, gem-dota üzerinden okur, MIT lisanslı). Ayrı tutulur, böylece onunla ilgili bir sorun başka hiçbir şeye dokunmaz; PATH'te, kurulu ya da izleyicinin yanında olduğunda her yeni tekrar için kendi süreci içinde çalışır; yoksa izleyici bir kez nasıl kurulacağını söyler. Okuyucu her kahramanın konumunu, yüksekliğini, canını, seviyesini, yönünü, manasını, deneyimini, niteliklerini ve eşyalarını hayattayken saniyede 7.5 kez; öldürmeleri ve ölümleri olduğu yerde; kuleleri, kışlaları, Roshan'ı ve Tormentor'ları yıkıldıkları yerde; her gözetleme noktasının konulduğu ve bittiği yeri; savaş günlüğünün kahramanlarla ilgili girdilerini (hasar, iyileşme, yetenekler, eşyalar, satın almalar, rünler, altın, deneyim, değiştiriciler) ve her oyuncunun harita işaretlerini, harita çizimlerini ve emirlerini `dota/<match>.parquet` dosyasına yazar; diğer her birimi (yaratıklar, çağrılan birimler, hayaletler, kuryeler, binalar) saniyede bir `<match>.units.parquet` dosyasına; bütün savaş günlüğünü `<match>.combatlog.parquet` dosyasına; ve maçı, sohbeti, draftı, ayrıştırıcının çıkardığı her şeyi ve oyunun kendi maç sonu kaydını `<match>.match.json` dosyasına, oturum klasöründe. Tekrarın tuttuğu diğer her şey bunların yanında bütün olarak saklanır (3DHeat'in dönüştürücü kuralı): her çerçeve ve ağ iletisi `<match>.packets.parquet` içinde, her varlık özelliği değişikliği `<match>.entities.parquet` içinde, her dize tablosu girdisi `<match>.strings.parquet` içinde; maç belgesinin `selfCheck.completeness` alanında sayılır. Konumlar, oyun Oyun Koordinatörünün yayınladığı gibi Dota'nın dünya birimleridir. Oturum açmış oyuncunun skor tablosu satırı oturumun istatistikleri olur: öldürmeler, ölümler, asistler, son vuruşlar, reddetmeler, net değer, GPM, XPM, kahraman hasarı, gözetleme noktaları ve maçın kazanılıp kazanılmadığı. Yeni bir Dota yamasının tekrarın varlıklarını değiştirebilmesi; gem'in sonuna kadar okuyamadığı bir tekrar ise gidebildiği yere kadar dönüştürülür ve özetinde `incomplete` olarak işaretlenir.

Aynı modül şunu da çalıştırır: [Counter-Strike 2 (tekrarlar)](game-cs2-demos.md), [Squad (tekrarlar)](game-squad-demos.md), [War Thunder (tekrarlar)](game-warthunder-replays.md), [World of Tanks (tekrarlar)](game-wot-replays.md), [World of Warships (tekrarlar)](game-wows-replays.md).

## Konumlar ve eksenler {#positions-and-axes}

| | |
|---|---|
| Konumlar kaydedilir | evet |
| Yukarı eksen | `z` |
| Birimler | Dota dünya birimleri (Hammer birimleri; harita yaklaşık 16400 genişliğinde) |
| Görüntüleyici için aynalanır | `y` |
| Birim ölçeği (`scale`: görüntüleyici konumları bununla çarpar) | 1 |

Bunlar her oturumun `meta.json` dosyasına (`axes`) ve oturumda konum varsa `heat.parquet` dosyasının altbilgisine yazılır; böylece 3DHeat görüntüleyicisi satırları kendi başına döndürür ve ölçekler - bkz. [Veriler](the-data.md).

## Çok oyunculu {#multiplayer}

- Çevrimiçi oynanan olarak işaretli (`multiplayer`): **evet**. `games --markdown` bunu "allowed (reads only what the game publishes)" olarak gösterir.
- Tür `replay`: yalnızca oyunun ya da platformun verdiğini okur (oyunun kaydettiği tekrarlar ve demolar), bu yüzden çevrimiçi oyunda da, çevrimdışı olduğu gibi kaydeder; bayrak yalnızca belleğin hiç okunup okunamayacağını belirler.
- Bellek: bu adaptör **asla** okumaz. Yalnızca `memory` adaptörleri bellek okur ve çevrimiçi oynanan bir oyun için asla okumaz - bkz. [Kaynaklar ve kurallar](sources-and-rules.md).

## Kaydedilen istatistikler {#statistics-recorded}

Bu adaptörün kodunun adıyla ayarladığı istatistik anahtarları (her oturumun `meta.json` içindeki `stats` ve `watcher.sqlite` içindeki `stats` tablosu):

`duration`, `hero`, `score.{team}`, `team`, `won`

Süslü parantez içindeki bir anahtar çalışma sırasında tamamlanır (`score.{team}` her takım için bir anahtardır). Kodun oyunun alan tablosundan ya da oyunun kendi istatistik adlarından aldığı anahtarlar bu listede yoktur; yukarıdaki "Neler kaydedilir" bölümü onları adlarıyla anar.

## Tamlık {#completeness}

Dönüştürücü, 3DHeat'in [dönüştürücü kuralını](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md) izler: tekrarın tuttuğu okunur ya da saklanır, asla atılmaz. Tablonun yanında, tekrarın tuttuğu diğer her şey, oturumun `dota/` klasöründe yanındaki yan dosyalarda bütün olarak saklanır - `<match>.packets.parquet`, `<match>.entities.parquet`, `<match>.strings.parquet` (sütunlar `time`, `tick`, `type`, `name`, `entity`, `decoded`, `payload`, uygulandıkları gibi) - ve maç belgesindeki (`<match>.match.json`) `selfCheck.completeness` her `type` değerini sayar - `lost` 0'dır.

**Okunanlar**

- tablo (`dota/<match>.parquet`): her kahramanın konumu, yüksekliği, cani, seviyesi, yönü, manası, deneyimi, nitelikleri, zırhı, hızı, hasarı, eşyaları ve oyuncunun imleci saniyede 7.5 kez; öldürmeler, ölümler, hedefler, gözetleme noktaları, savaş günlüğünün kahramanlarla ilgili girdileri; harita işaretleri (`ping`, DOTA_UM_LocationPing), harita çizimleri (`map_line`, DOTA_UM_MapLine) ve her birim emri (`order`, DOTA_UM_SpectatorPlayerUnitOrders: `other` emir türü, `value` yetenek ya da eşya kimliği, `text` hedefin sınıfı; emredilen noktada, yoksa kahramanda)
- `<match>.units.parquet`: diğer her birim saniyede bir; `<match>.combatlog.parquet`: gem'in okuduğu gibi bütün savaş günlüğü, her alanıyla
- maç belgesi: gem'in çıkardığı her şey ve tekrarın kendi kayıtlarının bütünü - `fileHeader` (DEM_FileHeader), `fileInfo` (DEM_FileInfo: oynatma süresi, her oyuncunun adı, kahramanı, Steam kimliği, takımı), `matchDetails` (DOTA_UM_MatchDetails: oyun koordinatörünün maç sonu skor tablosu, her oyuncunun sayıları, eşyaları, türe göre hasarı, seçimleri ve yasakları) ve `matchMetadata` (DOTA_UM_MatchMetadata)
- `selfCheck.crossCheck`: akıştan okunan öldürmeler, ölümler, asistler, seviye, son vuruşlar ve reddetmeler, `matchDetails` ile oyuncu başına karşılaştırılmış

**Ham olarak saklananlar**

- `<match>.packets.parquet`: paket olmayan her çerçeve (`type` `frame <n>`) ve her ağ iletisi (`message <n>`, `name` Valve'ın adı), `payload` içinde bütün olarak, dosya sırasında (`seq`, `frame`), `decoded` protobuf'un JSON hâli (bayt alanı uzunluğuyla verilir) ile; her ileti türü çözülmüş: svc_PacketEntities (varlık akışı), DOTA_UM_SpectatorPlayerUnitOrders, UM_ParticleManager, savaş günlüğü iletileri, GE_SosStartSoundEvent, DOTA_UM_TE_\* (mermiler, canlandırmalar, kan), DOTA_UM_OverheadEvent, DOTA_UM_UnitEvent, svc_UpdateStringTable, net_Tick, ...; sonraki bir varlık çözücünün ihtiyaç duyduğu gönderme tabloları, sınıf listesi ve sunucu bilgisi bunlar arasındadır
- `<match>.entities.parquet`: her varlığın her özelliği, her değiştiğinde (`type` özellik, `name` sınıf, `entity` dizini; `value`, `vector` ya da `decoded`), oluşturulduğundaki bütün durumu ve her oluşturma, girme, çıkma ve silinme - bir maç için milyonlarca satır
- `<match>.strings.parquet`: her güncellemeden ve her tam anlık görüntüden her dize tablosu girdisi, değeri bütün olarak; `userinfo`, `ActiveModifiers` ve `EconItems` protobuf'larından çözülmüş
- maç belgesindeki `selfCheck.completeness`, çerçeveleri ve iletileri Valve'ın adıyla, savaş günlüğü girdilerini (`combatlog <type>`), oyun olaylarını (`gameevent <name>`), dize tablosu girdilerini (`stringtable <name>`) ve varlık güncellemelerini (`entity <class>`) sayar; birkaçı yalnızca ham olarak saklanır (gem'in deltalardan yeniden oluşturduğu için atladığı tam varlık anlık görüntüleri ve hiçbir şeyin okumadığı tabloların girdileri), kayıp 0

**Mevcut değil**

- ses: tekrarda ses ayarı vardır ama ses verisi yoktur
- karma değerlerin ve kimliklerin arkasındaki adlar: sesler ve parçacıklar, oyunun dosyalarının karma değerleriyle adlandırılır, yetenekler kimliklerle; tekrar adları taşımaz (eşyalar, gem'in kataloğu üzerinden, varsa adlandırılır)
- oyuncuların kendi istemcilerinin bildiği her şey (kameraları, ekranları), sunucunun yayınladığının ötesinde; imleç ve her emir içindedir

**Boyut**: yan dosyalar birlikte tekrarın kendisinden biraz daha büyüktür, en büyükleri paketler ve varlıklar; bütün bir maç tek bir süreçte bir ya da iki dakika sürer

## Doğrulama {#verified}

herkese açık bir maçın tekrarında kontrol edildi: öldürmeler, ölümler, asistler, seviye, son vuruşlar ve reddetmeler, Valve'ın maç sonu kaydıyla on oyuncunun hepsi için eşleşiyor; paketler yan dosyasındaki her ileti bayt bayt yeniden serileştirilir; tablo ve istatistikler sentetik verilerle yapılan testlerle doğrulandı

## Kaynak {#source}

[heat3d_watch/adapters/replays.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/replays.py)

<!-- Generated from the adapter by tools/gen_game_pages.py; change the adapter and run it again rather than editing this page. -->
