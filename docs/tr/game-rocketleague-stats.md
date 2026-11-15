---
title: "Rocket League (oyun durumu)"
nav_order: 39
lang: "tr"
source: game-rocketleague-stats.md
source_hash: "fd70d0540bb9"
nav_exclude: true
search_exclude: true
---
# Rocket League (oyun durumu) {#rocket-league-game-state}

Rocket League oynarken izleyici, oyunun bilgisayarınızdaki programlara bildirdiklerini kaydeder; böylece bunlara daha sonra 3DHeat görüntüleyicisinde bir harita üzerinde bakabilirsiniz.

*Teknik ayrıntılar: uyarlayıcı `rocketleague-stats`, tür [`gsi`](sources-and-rules.md); `RocketLeague.exe` çalışırken çalışır ve her 0,05 saniyede bir yeni veri arar.*

## Ne kaydedilir {#what-is-recorded}

- top vuruşları, topun yeriyle (XYZ, Unreal birimleri), vuranla ve hızlarla
- goller, etki yeriyle, golü atanla, asistle ve hızla; direk vuruşları yeriyle
- istatistik akışı (demolamalar, kurtarışlar, şutlar, epik kurtarışlar, ...), kickoff'lar, tekrarlar, maçın başlangıcı ve sonu, kazanan
- kendi golleriniz, asistleriniz, kurtarışlarınız, şutlarınız, demolarınız, dokunuşlarınız, skorunuz ve takım skorları, UpdateState'ten
- maç sonunda her oyuncunun son satırı
- sizin satırlarınız `me` olarak: ayarlarda adı verilen oyuncu (`config --set player_names.rocketleague-stats=<ad>`), yoksa tekrarların dışında oyun kamerasının takip ettiği oyuncu
- araba konumları yok: API bunları vermez

## Veri nereden gelir {#where-it-comes-from}

İstatistik API'si: 127.0.0.1:49123 adresinden TCP JSON akışı (Port: <RL>\TAGame\Config\TAStatsAPI.ini veya DefaultStatsAPI.ini içinde)

## Nasıl açılır {#how-to-switch-it-on}

`python -m heat3d_watch setup rocketleague-stats --apply` (PacketSendRate=30 ayarlar), ardından Rocket League'i başlatın

Komutu, izleyicinin klasöründe açılmış bir terminale yazın (bkz. [Başlamadan önce](before-you-start.md)). Başarısız olursa, son satır nedenini söyler; [Kurulum ve çalıştırma](installing-and-running.md) sık görülen nedenleri anlatır.

`python -m heat3d_watch setup rocketleague-stats` değiştirilecek dosyaları listeler; `python -m heat3d_watch setup rocketleague-stats --apply` bunları değiştirir ve özgün dosyayı `<file>.heat3d-backup` adıyla saklar (bkz. [Komutlar](commands.md#setup)). Her değişiklik için `rocketleague-stats: changed: ...` yazar; zaten açıksa `rocketleague-stats: nothing to change` yazar.

## Nasıl çalışır {#how-it-works}

Rocket League: resmî İstatistik API'si, oyunun maç verilerini yazdığı yerel bir soket.

`<RL>\TAGame\Config\TAStatsAPI.ini` içinde açılır - ya da bu dosya yoksa `DefaultStatsAPI.ini` (oyun yalnızca o zaman okur) - `[TAGame.MatchStatsExporter_TA]` bölümü altında:

```text
PacketSendRate   UpdateState messages per second; 0 (the default) switches the API off, at most 120
Port             the TCP port the game listens on, default 49123 (WebPort 49124 is a WebSocket copy)
```

Oyun sunucudur: bir istemci 127.0.0.1:49123'e bağlanır ve ayırıcı olmadan, art arda gelen `{"Event": name, "Data": {...}}` JSON nesnelerinin akışını okur (bazı sürümler Data'yı JSON metni olarak gönderir). Olaylar, olduğu tikte gönderilir, hızdan bağımsız:

```text
UpdateState   MatchGuid, Players[] (Name, PrimaryId, Shortcut, TeamNum 0 blue / 1 orange,
              Score, Goals, Shots, Assists, Saves, Touches, CarTouches, Demos; car state
              only for spectators), Game (Teams[], TimeSeconds, bOvertime, Ball {Speed,
              TeamNum}, bReplay, bHasWinner, Winner, Arena, bHasTarget, Target)
BallHit       Players[] (Name, Shortcut, TeamNum), Ball {PreHitSpeed, PostHitSpeed, Location {X,Y,Z}}
GoalScored    GoalSpeed, GoalTime, ImpactLocation {X,Y,Z}, Scorer, Assister, BallLastTouch
CrossbarHit   BallLocation {X,Y,Z}, BallSpeed, ImpactForce, BallLastTouch
StatfeedEvent EventName, Type, MainTarget, SecondaryTarget
MatchEnded    WinnerTeamNum
MatchCreated, MatchInitialized, CountdownBegin, RoundStarted, GoalReplayStart/WillEnd/End,
MatchPaused/Unpaused, PodiumStart, ReplayCreated, MatchDestroyed, ClockUpdatedSeconds
```

Konumlar Unreal birimleridir (santimetre), Z yukarı; saha yaklaşık 8200 x 10240 ve kaleler Y = ±5120'de. Arabaların konumları API'nin parçası değildir: bir yeri olan, vurulduğu, gol olduğu veya direğe çarptığı andaki toptur.

Her mesaj da bütün olarak saklanır (3DHeat'in dönüştürücü kuralı, görüntüleyicinin deposundaki docs/converters.md): `heat.raw.parquet`, `type` mesajın Event adı, `text` akıştan geldiği gibi nesne. Bayt bayt bir öncekiyle aynı olan bir UpdateState (duraklatılmış bir maç, bir menü) bir kez saklanır ve meta.json içindeki `unchanged_replies` ile sayılır. Maçlar arasındaki mesajlar, bir sonraki maçın oturumu için bir bekleme listesinde durur; oyun kapandığında kalan şey kendi oturumunu alır. JSON olmayan nesneler arasındaki karakterler "junk" olarak saklanır.

Kaynaklar: <https://www.rocketleague.com/en/developer/stats-api> (resmî sayfa); alan büyük/küçük harf yazımı ve TCP çerçevelemesi rlstatsapi istemcisiyle doğrulandı (<https://docs.rs/crate/rlstatsapi>, MIT; yalnızca gerçekler için okundu).

## Konumlar ve eksenler {#positions-and-axes}

| | |
|---|---|
| Konumlar kaydedilir | evet |
| Yukarı eksen | `z` |
| Birimler | Unreal birimleri (santimetre) |
| Görüntüleyici için aynalama | yok |
| Birim ölçeği (`scale`: görüntüleyici konumları bununla çarpar) | 1 |

Bunlar her oturumun `meta.json` dosyasındaki (`axes`) ve oturumda konum varsa `heat.parquet` dosyasının altbilgisine yazılır; böylece 3DHeat görüntüleyicisi satırları kendi başına döndürür ve ölçekler. Bkz. [Veriler](the-data.md).

## Çok oyunculu {#multiplayer}

- Çevrimiçi oynanan olarak işaretli (`multiplayer`): **evet**. `games --markdown` bunu "izinli (yalnızca oyunun yayınladığını okur)" olarak gösterir.
- Tür `gsi`: yalnızca oyunun veya platformun dışarı verdiğini okur (oyunun sunduğu bir oyun durumu entegrasyonu veya yerel API); bu yüzden çevrimiçi oyunda da kaydeder. Bayrak yalnızca belleğin hiç okunup okunamayacağını belirler.
- Bellek: bu uyarlayıcı **asla** okumaz. Yalnızca `memory` uyarlayıcıları bellek okur ve çevrimiçi oynanan olarak işaretli bir oyun için hiçbir zaman. Bkz. [Kaynaklar ve kurallar](sources-and-rules.md).

## Kaydedilen istatistikler {#statistics-recorded}

Bu uyarlayıcının kodunun ada göre ayarladığı istatistik anahtarları (her oturumun `meta.json` dosyasındaki `stats` ve `watcher.sqlite` dosyasındaki `stats` tablosu):

`bad_packets`, `demolished`, `other_goals`, `overtime`, `result`, `team_goals`

Süslü parantez içindeki bir anahtar çalışma zamanında tamamlanır (`score.{team}` her takım için ayrı bir anahtardır). Kodun oyunun alan tablosundan veya oyunun kendi istatistik adlarından aldığı anahtarlar bu listede yer almaz; yukarıdaki "Ne kaydedilir" bölümü onları adlandırır.

## Tamlık {#completeness}

İzleyici 3DHeat'in [dönüştürücü kuralını](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md) izler: kaynağın tuttuğu her şey okunur veya saklanır, hiçbir şey atılmaz. Satırların yanında, uyarlayıcının aldığı her paket, sayfa, satır veya yanıt oturumun `heat.raw.parquet` dosyasında bütün olarak saklanır (sütunlar `time`, `ms`, `type`, `used`, `payload`, `text` ve ada göre tutulan her alan; `used` satırlara da dönüşenleri işaretler). `meta.json` içindeki `selfCheck.completeness` her `type` değerini sayar; `lost` 0'dır.

**Okunan**

- BallHit (yer, kim, takım, vuruştan önceki ve sonraki hızlar), GoalScored (etki yeri, golü atan, asist, hız, gol zamanı), CrossbarHit (yer, son dokunuş, hız, kuvvet), StatfeedEvent (olay, tür, ana ve ikincil hedef), MatchEnded (kazanan, sonuç); diğer her olayın adı satır olarak
- UpdateState'ten: arena, tekrarların dışındaki kamera hedefi (`me`'nin kim olduğu), takım skorları, her oyuncunun golleri, asistleri, kurtarışları, şutları, demoları, dokunuşları, araba dokunuşları ve skoru (kendisininki istatistik olarak, herkesinki maç sonunda `player_result` olarak); ClockUpdatedSeconds'tan uzatma

**Ham olarak saklanan**

- her mesaj akıştan geldiği gibi bütün olarak (`text`), kendi Event adı altında: `UpdateState` (her oyuncunun PrimaryId ve Shortcut değerleri, saat, topun hızı ve takımı, takım adları ve renkleri, tekrar ve kazanan bayrakları ve oyunun gönderdiği yerlerde araba durumu), `BallHit`, `GoalScored` (topun son dokunuşuyla), `CrossbarHit`, `StatfeedEvent`, `MatchCreated`, `MatchInitialized`, `CountdownBegin`, `RoundStarted`, `GoalReplayStart`, `GoalReplayWillEnd`, `GoalReplayEnd`, `MatchPaused`, `MatchUnpaused`, `MatchEnded`, `PodiumStart`, `ReplayCreated`, `MatchDestroyed`, `ClockUpdatedSeconds` ve sonraki bir sürümün eklediği her olay
- bayt bayt bir öncekiyle aynı olan bir UpdateState (duraklatılmış, menüler) bir kez saklanır ve sayılır (meta.json içinde `unchanged_replies`)
- maçlar arasındaki mesajlar: bir sonraki maçın başlangıcından önce kendi zamanlarında; son maçtan sonra kendi oturumlarında (meta.json içinde `raw_only`)
- `unreadable`: bir Stats API mesajı olmayan nesne; `junk`: nesneler arasındaki karakterler

**Mevcut olmayan**

- oynarken araba konumları ve araba durumu: oyun bunları yalnızca izleyicilere gönderir
- iki gönderim arasındaki UpdateState: oyun saniyede PacketSendRate kadar gönderir (`setup` 30 ayarlar, oyun 120'ye kadar izin verir); olaylar olduğu tikte gönderilir
- WebPort (49124) üzerindeki WebSocket kopyası: TCP portuyla aynı mesajlar, iki kez okunmaz

**Boyut**: bir UpdateState altı oyuncu için 1-3 KB, saniyede 30; bir maç sürerken saatte yaklaşık 100-300 MB `raw.bin` içinde, zstd `heat.raw.parquet` içinde bunun onda biri veya daha azı (belgelenmiş biçimden tahmin edildi, oyunda ölçülmedi)

## Doğrulama {#verified}

belgelenmiş biçimde gelen mesajlarda, sahte bir yerel sunucu tarafından gönderilerek test edildi; oyunda test edilmedi

## Kaynak {#source}

[heat3d_watch/adapters/rocketleague.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/rocketleague.py)

<!-- Adaptörden tools/gen_game_pages.py ile üretilmiştir; sayfayı elle düzenlemek yerine adaptörü değiştirin ve yeniden çalıştırın. -->
