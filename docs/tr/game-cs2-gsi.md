---
title: "Counter-Strike 2 (oyun durumu)"
nav_order: 9
lang: "tr"
source: game-cs2-gsi.md
source_hash: "2eda1106e11f"
nav_exclude: true
search_exclude: true
---
# Counter-Strike 2 (oyun durumu) {#counter-strike-2-game-state}

Counter-Strike 2 oynarken izleyici, oyunun bildirdiklerini bilgisayarınızdaki programlara kaydeder. Böylece bunlara daha sonra 3DHeat görüntüleyicisinde bir harita üzerinde bakabilirsiniz.

*Teknik ayrıntılar: adaptör `cs2-gsi`, tür [`gsi`](sources-and-rules.md); `cs2.exe` çalışırken çalışır ve her 0.05 s'de bir yeni veri arar.*

## Neler kaydedilir {#what-is-recorded}

- hayattayken kendi konumu (dünya XYZ, inç) ve bakış yönü, saniyede en fazla 10 kez (10 Hz)
- doğuşlar (her turun ilk görülmesi, yeniden doğuşlar) ve ölümler (canın 0'a inmesi ya da ölüm sayısı)
- maç istatistiklerinden, kullanılan silahla yapılan öldürmeler
- turlar (başlangıç, bitiş, kazanan), bombanın kurulması, etkisiz hale getirilmesi ve patlaması, maç aşamaları ve sonuç
- öldürmeler, asistler, ölümler, MVP'ler, skor, para, hasar, kafa atışıyla öldürmeler, kazanılan ve kaybedilen turlar

## Nereden gelir {#where-it-comes-from}

Oyun Durumu Entegrasyonu: `<CS2>\game\csgo\cfg\gamestate_integration_heat3d.cfg` dosyasında ayarlanan 127.0.0.1:3311 adresine HTTP POST istekleri

## Nasıl açılır {#how-to-switch-it-on}

`python -m heat3d_watch setup cs2-gsi --apply`, ardından CS2'yi başlatın (oyun dosyayı başlarken okur)

Komutu, izleyicinin klasöründe açılmış bir terminale yazın (bkz. [Başlamadan önce](before-you-start.md)). Başarısız olursa son satır nedenini söyler; [Kurulum ve çalıştırma](installing-and-running.md) sık görülen nedenleri anlatır.

`python -m heat3d_watch setup cs2-gsi` hangi dosyaları değiştireceğini listeler; `python -m heat3d_watch setup cs2-gsi --apply` bunları değiştirir ve özgün dosyayı `<file>.heat3d-backup` adıyla saklar (bkz. [Komutlar](commands.md#setup)). Her değişiklik için `cs2-gsi: changed: ...` yazar, zaten açıksa `cs2-gsi: nothing to change` yazar.

Ortam değişkenlerinden gelen ayarlar:

- `HEAT3D_CS2_GSI_PORT`: oyunun veri gönderdiği port (varsayılan 3311); oyunun cfg dosyasında aynı port yazılı olmalıdır

## Nasıl çalışır {#how-it-works}

Valve Oyun Durumu Entegrasyonu: Counter-Strike 2 ve Dota 2, neler olduğunu yerel bir web sunucusuna bildirir.

İki oyun da başlarken klasörlerindeki her `gamestate_integration_*.cfg` dosyasını okur. Bundan sonra, durum değiştiğinde her dosyanın `uri` adresine bir JSON belgesi gönderir (en fazla her `throttle` saniyede bir, hiçbir şey değişmezse her `heartbeat` saniyede bir). İzleyici bu web sunucusudur: yalnızca 127.0.0.1'i dinler, her POST isteğine hemen 200 ile yanıt verir ve işi kendi yoklama iş parçacığında yapar.

```text
Counter-Strike 2  <CS2>\game\csgo\cfg\gamestate_integration_heat3d.cfg      port 3311
Dota 2            <Dota>\game\dota\cfg\gamestate_integration\gamestate_integration_heat3d.cfg   port 3312
```

Oyuncuya ne gönderildiği - ve dolayısıyla neyin kaydedilebileceği - oyunun bir oyuncunun neyi görebileceğine karar vermesine bağlıdır:

- CS2: `provider` (kendi steamid'iniz), `map` (ad, mod, aşama warmup/live/intermission/gameover, tur, team_ct/team_t skoru), `round` (aşama freezetime/live/over, bomb planted/exploded/defused, win_team), `player` (izlenen oyuncu: hayattayken kendiniz, ölünce bir takım arkadaşınız), şu alanlarla: `state` (can, zırh, para, round_kills, round_killhs, round_totaldmg), `match_stats` (öldürmeler, asistler, ölümler, mvps, skor), `position` ve `forward` dünya birimlerinde (inç, Z yukarı) "x, y, z" metinleri olarak, `weapons`; `bomb` yalnızca izleyiciler için. Diğer oyuncuların konumları (`allplayers_*`) yalnızca izleyicilere ve GOTV'ye gönderilir, bu yüzden istenmez.
- Dota 2: `map` (matchid, game_state, game_time, clock_time, win_team), `player` (kills, deaths, assists, last_hits, denies, gold, gpm, xpm, team_name), `hero` (dünya birimlerinde xpos/ypos, seviye, alive, respawn_seconds), `buildings` (kule, kışla ve ana yapı başına can), `roshan`, `events` (roshan_killed, aegis_picked_up, ...). Yükseklik yoktur: z 0'dır. Ayrıca istenen ve bütün tutulanlar: `abilities`, `items`, `draft`, `wearables`, `minimap`, `couriers`, `neutralitems`, `league` (oyun, oyuncunun kendi istemcisinde olanı gönderir; bunlardan hangisinin oyun oynarken, izlemek yerine, bir şey tuttuğu test edilmedi).

Her belge de bütün olarak saklanır (3DHeat'in dönüştürücü kuralı, görüntüleyicinin deposundaki docs/converters.md): `heat.raw.parquet`, `type` "gsi", `text` gönderildiği gibi JSON. Yalnızca cfg dosyasındaki belirteç boşaltılır; o, izleyicinin kendi sırrıdır, oyun verisi değildir. Açık maç yokken gelen belgeler (menüler, yükleme, maçlar arası) bir `Backlog` içinde bekler ve bir sonraki maçın oturumuna, başlangıcından önce girer; oyun kapandığında kalanlar yalnızca kendilerini tutan kendi oturumlarına girer. Okunamayan gönderiler ve yanlış belirteçli gönderiler de saklanır ("gsi-unreadable", "gsi-bad-auth").

Kaynaklar: <https://developer.valvesoftware.com/wiki/Counter-Strike:_Global_Offensive_Game_State_Integration>
(CS2'nin koruduğu biçim), <https://github.com/antonpup/CounterStrike2GSI> ve
<https://github.com/antonpup/Dota2GSI> (alan listeleri; MIT, yalnızca bilgi için okundu).

Aynı modül şunu da çalıştırır: [Dota 2 (oyun durumu)](game-dota2-gsi.md).

## Konumlar ve eksenler {#positions-and-axes}

| | |
|---|---|
| Konumlar kaydedilir | evet |
| Yukarı eksen | `z` |
| Birimler | inç (Hammer birimleri) |
| Görüntüleyici için aynalanır | `y` |
| Birim ölçeği (`scale`: görüntüleyici konumları bununla çarpar) | 1 |

Bunlar her oturumun `meta.json` dosyasına (`axes`) ve oturumda konum varsa `heat.parquet` dosyasının altbilgisine yazılır; böylece 3DHeat görüntüleyicisi satırları kendi başına döndürür ve ölçekler - bkz. [Veriler](the-data.md).

## Çok oyunculu {#multiplayer}

- Çevrimiçi oynanan olarak işaretli (`multiplayer`): **evet**. `games --markdown` bunu "allowed (reads only what the game publishes)" olarak gösterir.
- Tür `gsi`: yalnızca oyunun ya da platformun verdiğini okur (oyunun sunduğu bir oyun durumu entegrasyonu ya da yerel API), bu yüzden çevrimiçi oyunda da, çevrimdışı olduğu gibi kaydeder; bayrak yalnızca belleğin hiç okunup okunamayacağını belirler.
- Bellek: bu adaptör **asla** okumaz. Yalnızca `memory` adaptörleri bellek okur ve çevrimiçi oynanan bir oyun için asla okumaz - bkz. [Kaynaklar ve kurallar](sources-and-rules.md).

## Kaydedilen istatistikler {#statistics-recorded}

Bu adaptörün kodunun adıyla ayarladığı istatistik anahtarları (her oturumun `meta.json` içindeki `stats` ve `watcher.sqlite` içindeki `stats` tablosu):

`bad_auth`, `bad_packets`, `dropped_packets`, `money`, `result`, `score_other`, `score_own`

Süslü parantez içindeki bir anahtar çalışma sırasında tamamlanır (`score.{team}` her takım için bir anahtardır). Kodun oyunun alan tablosundan ya da oyunun kendi istatistik adlarından aldığı anahtarlar bu listede yoktur; yukarıdaki "Neler kaydedilir" bölümü onları adlarıyla anar.

## Tamlık {#completeness}

İzleyici, 3DHeat'in [dönüştürücü kuralını](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md) izler: kaynağın tuttuğu okunur ya da saklanır, asla atılmaz. Satırların yanında, adaptörün aldığı her paket, sayfa, satır ya da yanıt, oturumun `heat.raw.parquet` dosyasında bütün olarak saklanır (sütunlar `time`, `ms`, `type`, `used`, `payload`, `text`, ardından adıyla saklanan her alan; `used` satırlara dönüşenleri işaretler). `meta.json` içindeki `selfCheck.completeness` her `type` değerini sayar - `lost` 0'dır.

**Okunanlar**

- izlenen oyuncunun konumu, bakış yönü, canı, zırhı, parası, etkin silahı, kaskı, bomba kesicisi, flaş/duman/yangın miktarları ve ekipman değeri, her konum satırında, oyuncunun kendisi olduğu sürece (sağlayıcının steamid'i = oyuncunun steamid'i)
- doğuşlar, ölümler (canın 0'a inmesi ya da maç istatistiklerindeki ölüm sayısı), öldürmeler (öldürme sayısının artması)
- maç aşamaları, turlar (dondurma süresi, canlı, bitti, kazanan), bombanın kurulması/etkisiz hale getirilmesi/patlaması, sonuç
- öldürmeler, asistler, ölümler, MVP'ler, skor, para, hasar, kafa atışıyla öldürmeler, kazanılan ve kaybedilen turlar istatistik olarak

**Ham olarak saklananlar**

- `gsi`: oyunun gönderdiği her belge, bütün olarak, gönderildiği gibi (`text`); bir maçta okunduğunda `used` doğrudur - sağlayıcı (sürüm, zaman damgası), map (mod, takım adları, art arda tur kayıpları, molalar, seri galibiyetleri, her turun galibiyet koşuluyla `round_wins`), round, izlenen oyuncu (klan, izleyici yuvası, etkinlik, her silah, kaplama, mermi ve yedek), bomb, aşama geri sayımları ve oyunun kendi `previously`/`added` farkı
- menülerden, yüklemeden ve maçlar arasından gelen belgeler: aynı şekilde, bir sonraki maçın başlangıcından önce kendi zamanlarında saklanır; son maçtan sonra kendi oturumlarında (meta.json içinde `raw_only`)
- `gsi-unreadable`: JSON nesnesi olmayan bir gönderi, baytları `payload` ve `length` olarak
- `gsi-bad-auth`: cfg dosyasındakinden farklı bir belirteçle gelen gönderi

**Mevcut değil**

- diğer oyuncular (`allplayers_*`) ve el bombaları (`allgrenades`): oyun bunları yalnızca izleyicilere ve GOTV'ye gönderir ve izleyici bunları istemez (Kaynaklar ve kurallar); bir demo her oyuncuyu içerir - bkz. [Counter-Strike 2 (tekrarlar)](game-cs2-demos.md)
- gönderiler arasındaki durumlar: oyun en fazla 0.1 s'de bir (`throttle`) ve yalnızca değişiklikte gönderir, değişiklik yoksa 10 s'de bir (`heartbeat`)
- cfg dosyasının belirteci, her saklanan belgede boşaltılmıştır: izleyicinin kendi sırrıdır, oyun verisi değildir
- bekleyen 10.000'i aşan gönderiler (izleyici takılmışsa) `dropped_packets` olarak sayılır, saklanmaz; 4 MB'ı aşan bir gönderi, uzunluğu ile `gsi-unreadable` olarak saklanır ama baytları saklanmaz

**Boyut**: oyuncunun bir belgesi 2-4 KB'dır, bir şey değiştiğinde saniyede en fazla 10 kez gönderilir: maç sürerken `raw.bin` içinde saatte yaklaşık 30-150 MB, zstd sıkıştırılmış `heat.raw.parquet` içinde bunun onda biri ya da daha az (yayımlanmış biçimden tahmin edildi, oyunda ölçülmedi)

## Doğrulama {#verified}

yayımlanmış GSI biçimindeki belgelerle, çalışan adaptöre gönderilerek test edildi; kurulum ve cfg klasörü araması yerel bir kurulumda test edildi; çalışan oyunla test edilmedi

## Kaynak {#source}

[heat3d_watch/adapters/gsi.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/gsi.py)

<!-- Generated from the adapter by tools/gen_game_pages.py; change the adapter and run it again rather than editing this page. -->
