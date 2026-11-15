---
title: "Dota 2 (oyun durumu)"
nav_order: 13
lang: "tr"
source: game-dota2-gsi.md
source_hash: "100a0d704bbe"
nav_exclude: true
search_exclude: true
---
# Dota 2 (oyun durumu) {#dota-2-game-state}

Dota 2 oynarken izleyici, oyunun bildirdiklerini bilgisayarınızdaki programlara kaydeder. Böylece bunlara daha sonra 3DHeat görüntüleyicisinde bir harita üzerinde bakabilirsiniz.

*Teknik ayrıntılar: adaptör `dota2-gsi`, tür [`gsi`](sources-and-rules.md); `dota2.exe` çalışırken çalışır ve her 0.05 s'de bir yeni veri arar.*

## Neler kaydedilir {#what-is-recorded}

- hayattayken kendi kahramanının konumu (dünya X/Y, Dota birimleri; yükseklik yok)
- kendi kahramanın doğuşu, ölümleri (yeniden doğuş süresiyle birlikte) ve yeniden doğuşları
- öldürmeler, öldürme sayısının artmasından
- yok edilen binalar, Roshan, oyun olayları (roshan_killed, aegis_picked_up, ...), oyun durumları, sonuç
- öldürmeler, ölümler, asistler, son vuruşlar, reddetmeler, altın, GPM, XPM, seviye, kahraman

## Nereden gelir {#where-it-comes-from}

Oyun Durumu Entegrasyonu: `<Dota>\game\dota\cfg\gamestate_integration\gamestate_integration_heat3d.cfg` dosyasında ayarlanan 127.0.0.1:3312 adresine HTTP POST istekleri

## Nasıl açılır {#how-to-switch-it-on}

`python -m heat3d_watch setup dota2-gsi --apply`, ardından Dota 2'yi başlatın (oyun dosyayı başlarken okur)

Komutu, izleyicinin klasöründe açılmış bir terminale yazın (bkz. [Başlamadan önce](before-you-start.md)). Başarısız olursa son satır nedenini söyler; [Kurulum ve çalıştırma](installing-and-running.md) sık görülen nedenleri anlatır.

`python -m heat3d_watch setup dota2-gsi` hangi dosyaları değiştireceğini listeler; `python -m heat3d_watch setup dota2-gsi --apply` bunları değiştirir ve özgün dosyayı `<file>.heat3d-backup` adıyla saklar (bkz. [Komutlar](commands.md#setup)). Her değişiklik için `dota2-gsi: changed: ...` yazar, zaten açıksa `dota2-gsi: nothing to change` yazar.

Ortam değişkenlerinden gelen ayarlar:

- `HEAT3D_DOTA_GSI_PORT`: oyunun veri gönderdiği port (varsayılan 3312); oyunun cfg dosyasında aynı port yazılı olmalıdır

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

Aynı modül şunu da çalıştırır: [Counter-Strike 2 (oyun durumu)](game-cs2-gsi.md).

## Konumlar ve eksenler {#positions-and-axes}

| | |
|---|---|
| Konumlar kaydedilir | evet |
| Yukarı eksen | `z` |
| Birimler | Dota dünya birimleri (z her zaman 0) |
| Görüntüleyici için aynalanır | `y` |
| Birim ölçeği (`scale`: görüntüleyici konumları bununla çarpar) | 1 |

Bunlar her oturumun `meta.json` dosyasına (`axes`) ve oturumda konum varsa `heat.parquet` dosyasının altbilgisine yazılır; böylece 3DHeat görüntüleyicisi satırları kendi başına döndürür ve ölçekler - bkz. [Veriler](the-data.md).

## Çok oyunculu {#multiplayer}

- Çevrimiçi oynanan olarak işaretli (`multiplayer`): **evet**. `games --markdown` bunu "allowed (reads only what the game publishes)" olarak gösterir.
- Tür `gsi`: yalnızca oyunun ya da platformun verdiğini okur (oyunun sunduğu bir oyun durumu entegrasyonu ya da yerel API), bu yüzden çevrimiçi oyunda da, çevrimdışı olduğu gibi kaydeder; bayrak yalnızca belleğin hiç okunup okunamayacağını belirler.
- Bellek: bu adaptör **asla** okumaz. Yalnızca `memory` adaptörleri bellek okur ve çevrimiçi oynanan bir oyun için asla okumaz - bkz. [Kaynaklar ve kurallar](sources-and-rules.md).

## Kaydedilen istatistikler {#statistics-recorded}

Bu adaptörün kodunun adıyla ayarladığı istatistik anahtarları (her oturumun `meta.json` içindeki `stats` ve `watcher.sqlite` içindeki `stats` tablosu):

`bad_auth`, `bad_packets`, `dropped_packets`, `hero`, `level`, `result`, `roshan_kills_seen`

Süslü parantez içindeki bir anahtar çalışma sırasında tamamlanır (`score.{team}` her takım için bir anahtardır). Kodun oyunun alan tablosundan ya da oyunun kendi istatistik adlarından aldığı anahtarlar bu listede yoktur; yukarıdaki "Neler kaydedilir" bölümü onları adlarıyla anar.

## Tamlık {#completeness}

İzleyici, 3DHeat'in [dönüştürücü kuralını](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md) izler: kaynağın tuttuğu okunur ya da saklanır, asla atılmaz. Satırların yanında, adaptörün aldığı her paket, sayfa, satır ya da yanıt, oturumun `heat.raw.parquet` dosyasında bütün olarak saklanır (sütunlar `time`, `ms`, `type`, `used`, `payload`, `text`, ardından adıyla saklanan her alan; `used` satırlara dönüşenleri işaretler). `meta.json` içindeki `selfCheck.completeness` her `type` değerini sayar - `lost` 0'dır.

**Okunanlar**

- kendi kahramanının konumu (x/y), hayatta olup olmadığı, seviyesi, canı, en yüksek canı, manası, en yüksek manası; doğuş, yeniden doğuş süresiyle birlikte ölümler, yeniden doğuşlar
- öldürmeler (öldürme sayısının artması); öldürmeler, ölümler, asistler, son vuruşlar, reddetmeler, altın, GPM, XPM, net değer, seviye ve kahraman istatistik olarak
- yok edilen binalar, Roshan'ın düşüp geri gelmesi, `events` içindeki her girdi bir kez, oyun durumları, kazanan

**Ham olarak saklananlar**

- `gsi`: oyunun gönderdiği her belge, bütün olarak, gönderildiği gibi (`text`); bir maçta okunduğunda `used` doğrudur - cfg dosyasının istediği on beş bileşenin hepsi: sağlayıcı, map (gündüz/gece, duraklatma, gözetleme noktası bekleme süreleri, skorlar), player (güvenilir ve güvenilmez altın, seriler, öldürme listesi, verilen komutlar, ...), hero (buff'lar, yetenek ağacı, Aghanim's, nitelikler), abilities, items, buildings, roshan, events, draft, wearables, minimap, couriers, neutralitems, league ve oyunun kendi `previously`/`added` farkı
- menülerden, yüklemeden ve maçlar arasından gelen belgeler: aynı şekilde, bir sonraki maçın başlangıcından önce kendi zamanlarında saklanır; son maçtan sonra kendi oturumlarında (meta.json içinde `raw_only`)
- `gsi-unreadable`: JSON nesnesi olmayan bir gönderi, baytları `payload` ve `length` olarak
- `gsi-bad-auth`: cfg dosyasındakinden farklı bir belirteçle gelen gönderi

**Mevcut değil**

- yükseklik: oyun yalnızca x ve y gönderir
- oynarken diğer kahramanlar: oyun yalnızca kendi kahramanı gönderir, her oyuncunun durumunu yalnızca izleyicilere gönderir (o zaman ham olarak saklanır, çizilmez); birkaç bileşen (draft, minimap, couriers) yalnızca oyuncunun kendi istemcisinde olanı taşır - oynarken bunun ne olduğu test edilmedi
- gönderiler arasındaki durumlar: en fazla 0.1 s'de bir (`throttle`), hiçbir şey değişmezse 10 s'de bir
- cfg dosyasının belirteci, her saklanan belgede boşaltılmıştır: izleyicinin kendi sırrıdır, oyun verisi değildir
- bekleyen 10.000'i aşan gönderiler (izleyici takılmışsa) `dropped_packets` olarak sayılır, saklanmaz; 4 MB'ı aşan bir gönderi, uzunluğu ile `gsi-unreadable` olarak saklanır ama baytları saklanmaz

**Boyut**: bütün bileşenlerle bir oyuncunun belgesi yaklaşık 5-15 KB'dır, saniyede en fazla 10 kez gönderilir (saat her gönderide değişir): maç sürerken `raw.bin` içinde saatte yaklaşık 100-500 MB, zstd sıkıştırılmış `heat.raw.parquet` içinde bunun yaklaşık onda biri; bir izleyicinin belgesi, bütün oyuncuları ve minimap ile birlikte bunun birkaç katıdır (yayımlanmış biçimden tahmin edildi, oyunda ölçülmedi)

## Doğrulama {#verified}

yayımlanmış GSI biçimindeki belgelerle, çalışan adaptöre gönderilerek test edildi; çalışan oyunla test edilmedi

## Kaynak {#source}

[heat3d_watch/adapters/gsi.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/gsi.py)

<!-- Generated from the adapter by tools/gen_game_pages.py; change the adapter and run it again rather than editing this page. -->
