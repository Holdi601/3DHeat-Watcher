---
title: "League of Legends (oyun durumu)"
nav_order: 29
lang: "tr"
source: game-lol-live.md
source_hash: "75c67c6fe84f"
nav_exclude: true
search_exclude: true
---
# League of Legends (oyun durumu) {#league-of-legends-game-state}

League of Legends oynarken izleyici, oyunun kendi bilgisayarınızdaki programlara bildirdiklerini kaydeder; böylece bunlara daha sonra istatistik ve zaman çizelgesi olarak bakabilirsiniz.

*Teknik ayrıntılar: bağdaştırıcı `lol-live`, tür [`gsi`](sources-and-rules.md); `League of Legends.exe` çalışırken çalışır ve yeni veri için her 0,5 saniyede bir bakar.*

## Ne kaydedilir {#what-is-recorded}

- konum yok: API'de konum yoktur
- öldürme akışı: oyuncunun öldürmeleri, ölümleri ve asistleri; katil, kurban ve asistlerle diğer şampiyon öldürmeleri
- ejderhalar, haraberler, baronlar, kuleler, inhibitörler, çoklu öldürmeler, aceler, ilk kan, oyunun başlangıcı ve sonu
- kendi öldürme, ölüm, asist, canavar skoru, gözcü skoru, seviye, altın, şampiyon, oyun süresi, sonuç
- oyuncunun takımının aldığı hedefler

## Kaynağı {#where-it-comes-from}

Oyun istemcisinin Live Client Data API'si, <https://127.0.0.1:2999/liveclientdata/> (allgamedata, eventdata), maç sırasında

## Nasıl açılır {#how-to-switch-it-on}

Hiçbir şeyi açmanız gerekmez: izleyici kaynağı, oyunun ya da platformun sunduğu haliyle okur.

## Nasıl çalışır {#how-it-works}

League of Legends: maç sırasında oyun istemcisinin sunduğu Live Client Data API.

Bir maç sürerken (alıştırma aracı ve izleyici modunda da), `League of Legends.exe` <https://127.0.0.1:2999> adresinde, oyuncunun oyunun kendi arayüzünde görebildiklerini yanıtlar:

```text
/liveclientdata/allgamedata          activePlayer (riotId, level, currentGold, championStats),
                                     allPlayers (championName, team ORDER/CHAOS, level,
                                     scores: kills, deaths, assists, creepScore, wardScore),
                                     events, gameData (gameMode, gameTime s, mapName)
/liveclientdata/eventdata?eventID=N  {"Events": [...]} from EventID N on: GameStart,
                                     MinionsSpawning, FirstBlood, FirstBrick, TurretKilled,
                                     InhibKilled, InhibRespawningSoon, InhibRespawned,
                                     DragonKill, HeraldKill, BaronKill, ChampionKill
                                     (KillerName, VictimName, Assisters), Multikill
                                     (KillStreak), Ace (Acer, AcingTeam), GameEnd (Result)
```

Konum yoktur: API'de yoktur; bu yüzden bir League oturumu, bir ısı tablosu olmadan, olaylar ve istatistiklerden oluşur. Sertifika kendinden imzalıdır, Riot'un kendi kökü tarafından (`riotgames.pem`, <https://static.developer.riotgames.com/docs/lol/riotgames.pem> adresinde yayımlanır). Kullanım koşulları belirtilmediği için dosya paketle gelmez: `<veri>\riotgames.pem` konumuna koyun, bağlantı onunla doğrulanır; o olmadan doğrulama kapalıdır - ve yalnızca bu bağdaştırıcının konuştuğu tek adres olan 127.0.0.1 için.

Riot'un politikası, araçların oyunun kendisinden oyuncunun bilebileceklerini göstermesine izin verir; onun ötesinde hesaplanmış hiçbir şeye izin vermez (düşman zamanlayıcısı yok): bu, oyuncunun gördüğü öldürme akışını ve skor tablosunu ve oyuncunun kendi sayılarını kaydeder.

Her yanıt da bütün olarak saklanır (3DHeat'in dönüştürücü kuralı; görüntüleyicinin deposundaki docs/converters.md): `heat.raw.parquet`, `type` uç noktadır ("allgamedata", "eventdata"), `text` istemcinin gönderdiği haliyle JSON, 200 değilse `status`. Uç noktasının bir önceki yanıtıyla bayt bayt aynı olan yanıt (hiçbir şey olmadığında olay listesi) bir kez saklanır ve meta.json içindeki `unchanged_replies` olarak sayılır. allgamedata, diğer uç noktaların sunduğu her şeyi taşır (activeplayer\*, playerlist, playerscores, playeritems, playersummonerspells, playermainrunes, gamestats), bu yüzden onlar ayrıca sorulmaz. Maçtan önceki yanıtlar (yükleme ekranı) bir bekleme kuyruğunda bekler ve maçın oturumuna girer; GameEnd'den sonra oturum, istemci kapanana kadar açık kalır, böylece bitiş ekranının yanıtları onunla birlikte saklanır.

Kaynak: <https://developer.riotgames.com/docs/lol#game-client-api>

## Konumlar ve eksenler {#positions-and-axes}

| | |
|---|---|
| Kaydedilen konumlar | hayır |
| Yukarı ekseni | `z` |
| Birimler | yok (konum yok) |
| Görüntüleyici için aynalama | yok |
| Birim ölçeği (`scale`: görüntüleyici konumları bununla çarpar) | 1 |

Bunlar her oturumun `meta.json` dosyasındaki (`axes`) ve konum içeren oturumlarda `heat.parquet` dosyasının sonundaki (footer) bilgiye yazılır; böylece 3DHeat görüntüleyicisi satırları kendisi döndürür ve ölçekler - bkz. [Veriler](the-data.md).

## Çok oyunculu {#multiplayer}

- Çevrimiçi oynanan olarak işaretlenmiş (`multiplayer`): **evet**. `games --markdown` bunu "izinli (yalnızca oyunun yayımladığını okur)" olarak gösterir.
- Tür `gsi`: yalnızca oyunun ya da platformun dışarı verdiğini okur (oyunun sunduğu bir oyun durumu entegrasyonu ya da yerel API). Bu yüzden çevrimiçi oyunda da çevrimdışı olduğu gibi kaydeder; bayrak yalnızca belleğin hiç okunup okunamayacağını belirler.
- Bellek: bu bağdaştırıcı **asla** okumaz. Yalnızca `memory` bağdaştırıcıları bellek okur ve çevrimiçi oynanan olarak işaretlenmiş bir oyun için asla okumaz - bkz. [Kaynaklar ve kurallar](sources-and-rules.md).

## Kaydedilen istatistikler {#statistics-recorded}

Bu bağdaştırıcının kodunun adla ayarladığı istatistik anahtarları (her oturumun `meta.json` içindeki `stats` ve `watcher.sqlite` içindeki `stats` tablosu):

`bad_packets`, `champion`, `game_time`, `gold`, `level`, `result`

Parantez içindeki bir anahtar çalışma zamanında tamamlanır (`score.{team}` her takım için bir anahtardır). Kodun oyunun alanlarının tablosundan ya da oyunun kendi istatistik adlarından aldığı anahtarlar bu listede yer almaz; yukarıdaki "Ne kaydedilir" bölümü bunları adlandırır.

## Tamlık {#completeness}

İzleyici 3DHeat'in [dönüştürücü kuralını](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md) izler: kaynağın tuttuğu her şey okunur ya da saklanır, asla atılmaz. Satırların yanı sıra, bağdaştırıcının aldığı her paket, sayfa, satır ya da yanıt, oturumun `heat.raw.parquet` dosyasında bütün olarak saklanır (sütunlar `time`, `ms`, `type`, `used`, `payload`, `text` ve adla saklanan her alan; `used` satıra dönüşenleri işaretler). `meta.json` içindeki `selfCheck.completeness` her `type` değerini sayar - `lost` 0'dır.

**Okunan**

- eventdata'daki öldürme akışı: her olay bir kez, adlandırılmış alanları çözülmüş (katil, kurban ve asistler şampiyon ve takımla birlikte; yapılar ve tarafları, ejderha türü, çalmalar, çoklu öldürmeler, aceler, ilk kan, sonuç) ve her olayın diğer her alanı kendi adıyla kendi satırında
- allgamedata'dan: kendi öldürme, ölüm, asist, canavar skoru, gözcü skoru, seviye, altın, şampiyon, oyun süresi, oyun modu ve harita

**Ham olarak saklanan**

- `allgamedata`: her yanıt bütün olarak (`text`), her 2 saniyede bir - activePlayer (yetenekler, her şampiyon istatistiği, tam rünler, altın, seviye), allPlayers (slotlu ve fiyatlı eşyalar, rünler, büyücü yetenekleri, skorlar, seviye, ölü ve yeniden doğma sayacı, kostüm, şerit, bot), olaylar, gameData (mod, süre, harita, arazi); maç sürerken `used` doğru, bitiş ekranında yanlış
- `eventdata`: her yanıt bütün olarak, her 0,5 saniyede bir, istenen olay kimliğinden itibaren; yeni olay getirdiğinde `used` doğru
- bir uç noktanın bir önceki yanıtıyla bayt bayt aynı olan yanıt bir kez saklanır ve sayılır (meta.json içindeki `unchanged_replies`); hata yanıtları (yükleme ekranının RESOURCE_NOT_FOUND'u), maçın başlangıcından önce `status` ile saklanır

**Kullanılamayanlar**

- konumlar: API'de yoktur (mini harita yok, koordinat yok)
- diğer uç noktalar (activeplayer, activeplayername, activeplayerabilities, activeplayerrunes, playerlist, playerscores, playersummonerspells, playermainrunes, playeritems, gamestats): her biri allgamedata'nın bir parçasını sunar, bu yüzden sorulmaz
- Replay API (aynı porttaki `/replay/*`): oyunda game.cfg içinde açıldığında replay'leri ve izlenen oyunları oynatır; oynanan bir maçın parçası değildir
- League istemcisinin lockfile uç noktaları: yayımlanmış bir API değil ([Kaynaklar ve kurallar](sources-and-rules.md))
- iki okuma arasındaki değerler: API istendiğinde yanıt verir, kendiliğinden göndermez; skor tablosu her 2 saniyede bir, olaylar her 0,5 saniyede bir sorulur

**Boyut**: allgamedata her 2 saniyede bir 15-40 KB (bütün olay listesini taşır, o büyür): `raw.bin` içinde saatte yaklaşık 30-70 MB; eventdata az yer ekler, çünkü değişmeyen yanıtlar saklanmaz, sayılır; heat.raw.parquet içindeki zstd tekrarlayan JSON'u saatte birkaç MB'a indirir (belgelenen biçimden tahmin edildi)

## Doğrulama {#verified}

belgelenen biçimde yanıtlar veren sahte bir yerel sunucuya karşı test edilmiştir; oyunla test edilmemiştir

## Kaynak {#source}

[heat3d_watch/adapters/lol.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/lol.py)

<!-- Adaptörden tools/gen_game_pages.py ile üretilmiştir; sayfayı elle düzenlemek yerine adaptörü değiştirin ve yeniden çalıştırın. -->
