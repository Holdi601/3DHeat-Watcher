---
title: "Veriler"
nav_order: 5
lang: "tr"
source: the-data.md
source_hash: "6150cdc022fc"
nav_exclude: true
search_exclude: true
---
# Veriler {#the-data}

Bütün kayıtlar veri klasöründe düz dosyalardır (`%LOCALAPPDATA%\3DHeat\Watcher`, değiştirilmediği sürece; bkz. [Kurulum ve çalıştırma](installing-and-running.md#where-everything-is)). Watcher olmadan da okuyabilir, kopyalayabilir ya da silebilirsiniz. Bir `.jsonl` dosyası düz metindir, her satırda bir olay (Not Defteri açar); bir `.parquet` dosyası, 3DHeat görüntüleyicisinin açtığı bir tablodur (Excel açmaz - tablolar için `stats --csv` CSV dosyaları yazar).

## Oturum klasörleri {#session-folders}
![a session folder](../assets/img/session-folder.svg)


Bir **oturum**, tek bir kaynaktan tek bir oturumdur: oyun ilk kez bir şey söylediği andan, durana kadar (oyun kapanır, bir maç biter, bir sürüş ya da uçuş sıfırlanır - her adaptörün sayfası neyin oturumları başlattığını ve bitirdiğini söyler). Her oturumun bir klasörü olur:

```text
<data>\sessions\<game>\<YYYY-MM-DD_HH-MM-SS>_<adapter id>\
    events.jsonl
    heat.parquet
    meta.json
```

- `<game>`, oyunun adıdır; harf, rakam, `.`, `_` ve `-` dışındaki her karakter `-` ile değiştirilir (en fazla 60 karakter): `EA-SPORTS-F1-25`, `Counter-Strike-2`. Birçok oyunu kapsayan adaptörler (Steam istatistikleri, Steam Timeline, NVIDIA highlights) her oturumu ait olduğu oyunun altına kaydeder.
- Zaman, oturumun başlangıcının yerel saatidir. Geçmişi anlatan oturumlar (maçtan sonra dönüştürülen bir replay, bir Steam istatistik dosyası) oyunun ya da dosyanın verdiği zamanı kullanır. Aynı saniyede başlayan iki oturuma `_2`, `_3`, ... eklenir.
- Oturumun kimliği, istatistik veritabanında `<game folder>/<session folder>` biçimindedir.

Hiçbir şeyin kaydedilmediği bir oturum (oyun menülerinde beklemiş ya da başlarken çökmüş) kapandığında silinir; böylece her başlatma boş bir klasör bırakmaz.

Bazı oturumlar daha fazla dosya tutar. Bir Counter-Strike 2 demo oturumu, dönüştürücünün kendi tablosunu ve özetini tutar (`<map>/<match>.parquet`, `<match>.match.json`). Bir iRacing oturumu, oturum sırasında simülatörün yazdığı `.ibt` dosyalarını `telemetry_file` olayları olarak listeler.

## events.jsonl {#eventsjsonl}

`events.jsonl`, her satırda bir JSON nesnesi olacak şekilde, her olay bir satır, olay olduğu anda yazılır. Dosya satır tamponludur; bu yüzden bir çökme, bir elektrik kesintisi ya da öldürülen bir işlem, zaten yazılmış hiçbir şeyi kaybettirmez. Bir çökmede yarım kalan bir satır, dosya okunurken atlanır ve ondan önceki her satır geçerli kalır.

Her satırın aynı temel sütunları vardır:

| Sütun | Tür | Ne demek |
|---|---|---|
| `time` | sayı | oturumun başlamasından beri saniye (4 ondalık basamak), ya da adaptörün ilettiği durumda oyunun kendi saati |
| `ms` | tam sayı | duvar saati, Unix milisaniyesi |
| `event` | metin | ne oldu: `position`, `spawn`, `death`, `kill`, `lap`, `teleport`, `session_start`, ... |
| `x`, `y`, `z` | sayı | nerede, oyunun kendi birimlerinde ve eksenlerinde (`meta.json` içindeki `axes`'e bakın); yalnızca üçü de biliniyorsa ve sonluysa bulunur |
| `player` | metin | kim: bir ad, bir kimlik ya da oynayan kişi için `me` (bkz. [Oyuncunun kendi satırları](#the-players-own-rows)) |
| `team` | metin | tarafları, oyun söylüyorsa |
| `session` | metin | satırın ait olduğu maç, tur, aşama, yaşam ya da uçuş, oyun söylüyorsa |

Oyunun bildirdiği her başka alan kendi adıyla gelir (`speed_kmh`, `gear`, `lap_time`, `weapon`, `victim`, `hero`, ...). Değeri olmayan alanlar dışarıda bırakılır; sonlu olmayan sayılar da öyle. İki uydurma satır:

```json
{"time":12.3456,"ms":1777660501123,"event":"position","x":-412.5,"y":12.1,"z":233.0,"player":"me","session":"1","speed_kmh":187.4,"gear":5}
{"time":15.0,"ms":1777660503667,"event":"lap","x":-380.2,"y":12.0,"z":250.9,"player":"me","session":"1","lap_time":92.418,"lap":3}
```

Konumu olmayan satırlar (bir öldürme akışı satırı, bir seviye atlama, bir istatistik değişikliği) `events.jsonl` içinde kalır ve istatistiklerde sayılır. Tabloya yalnızca konumu olan satırlar girer.

### Oyuncunun kendi satırları {#the-players-own-rows}

Oynayan kişiye ait satırları kaynak söyler; asla tahmin edilmez. Bir satır, şunlardan biri doğruysa oyuncunun kendisine aittir:

- `player` alanı `me`'dir: çoğu adaptör, çünkü kaynağı oyuncunun kendi oyunudur (kendi arabasının ya da uçağının telemetrisi, bir oyun durumu entegrasyonu, bir günlük);
- `own_car` 1 taşır: her arabayı sürücüsünün adıyla kaydeden yarış oyunları (EA SPORTS F1, oyunun oyuncu araba dizinine göre; RaceRoom, kendi yuvasına göre; Automobilista 2 ve Project CARS 2, görüntülenen katılımcıya göre) oyuncunun arabasını bu şekilde işaretler ve sürücünün adını `player` içinde tutar;
- `player` alanı, `meta.json` içindeki oturumun `player` değeridir: kaynağın oyuncuya verdiği ad - Elite Dangerous'ta komutan (günlük her zaman oyuncunun kendisidir), ayarlardaki Riot ID'nizle eşleşen bir League of Legends replay satırı.

War Thunder ve Rocket League her oyuncuyu adlandırır ve hangisinin siz olduğunuzu söylemez; `player_names` ayarında kendi adınız varsa (bkz. [Ayarlar](installing-and-running.md#settings)), satırlarınız `me` olur. [NVIDIA highlights](nvidia-highlights.md), bir anı bu tür satırlarda arar.

## heat.parquet {#heatparquet}

Bir oturum kapandığında, `events.jsonl` içinde `x`, `y` ve `z` değerleri olan satırlar `heat.parquet` dosyasına yazılır. Bu, 3DHeat görüntüleyicisinin açtığı tablodur. Oturumda hiç konum yoksa tablo yazılmaz.

- Sütunlar `time`, `ms`, `event`, `x`, `y`, `z`, `player`, `team`, `session` ve ardından ilk göründükleri sırayla diğer her alandır.
- `x`, `y`, `z` ve `time` 64 bitlik kayan noktalı sayılardır, `ms` ise 64 bitlik bir tam sayıdır. Değerleri hepsi sayı olan başka bir sütun 64 bitlik kayan noktalı sayıdır; öbür her sütun sözlük kodlamalı metindir (eksik değerler boş metin olur, listeler ve nesneler JSON metni olarak yazılır).
- Dosyanın meta verilerinde, okuma talimatlarını taşıyan `heat3d` anahtarı vardır; böylece görüntüleyici sütunları ve eksenleri kendisi eşler (`extra` listesi kısaltılmış bir örnek):

```json
{
  "version": 1,
  "kind": "heat3d-watch",
  "game": "EA SPORTS F1 25",
  "axes": {"up": "y", "flipX": false, "flipY": false, "flipZ": false, "scale": 1.0},
  "columns": {
    "x": "x", "y": "y", "z": "z",
    "time": "time", "timeUnit": "seconds",
    "personId": "player", "teamId": "team", "sessionId": "session",
    "extra": ["event", "speed_kmh", "gear", "lap_time", "lap"]
  }
}
```

`up`, oyunun yukarı eksenidir; `flipX`/`flipY`/`flipZ`, bir ekseni aynalar ki sol elli bir dünya ters çizilmesin; `scale` ise görüntüleyicinin birim ölçeğidir: görüntüleyici tabloyu yüklediğinde her konumu onunla çarpar (0.01, santimetreyi metreye çevirir). Her adaptör 1 yazar ve oyunun kendi birimlerini korur - çoğu için metre, Counter-Strike 2 için Source birimleri (inç), Rocket League için Unreal birimleri (santimetre) - çünkü oyundan aynı birimlerle dışa aktarılan bir seviye bu birimlerdedir, böylece satırlar ona oturur; CS2 dönüştürücüsünün kendi tabloları da aynısını söyler. `meta.json` içindeki `units`, bir birimin ne olduğunu söyler. Her oyunun sayfası değerlerini "Positions and axes" (Konumlar ve eksenler) altında listeler.

Uçuş simülatörleri (DCS World, Microsoft Flight Simulator, X-Plane, IL-2'nin Tacview kayıtları) satırlarını dünya üzerine koyar ve altbilgileri nerede olduklarını söyler; böylece görüntüleyici gerçek dünyayı altlarına serebilir:

```json
"geo": {"lat0": 42.0, "lon0": 42.0, "projection": "tangent-plane", "east": "x", "north": "z", "up": "y"}
```

`lat0`/`lon0` (derece), satırların içinde olduğu düz haritanın başlangıç noktasıdır; `east`, `north` ve `up`, başlangıçtan doğuya ve kuzeye metreleri ve deniz seviyesinden yüksekliği tutan sütunların adlarıdır. Başlangıç noktası X-Plane ve MSFS için ilk konumdur, IL-2 için kaydın referans noktasıdır, DCS için teatrin sabit başlangıç noktasıdır (watcher'ın bilmediği bir teatrde ilk konum, tam dereceye yuvarlanmış). Dünya üzerinde bir yeri olmayan bir tablonun `geo` anahtarı yoktur; altbilginin geri kalanı iki durumda da aynıdır.

`heat.parquet`, `events.jsonl` dosyasından her zaman `python -m heat3d_watch table <session folder>` ile yeniden oluşturulabilir (bkz. [Komutlar](commands.md#table)). Oturum kaydedilirken `pyarrow` eksikse bu kullanışlıdır.

## meta.json {#metajson}

`meta.json`, oturumu özetler. Oturum açıldığında yazılır, olaylar ya da istatistikler geldikçe en fazla 30 saniyede bir ve oturum kapandığında yazılır. İstatistikler yalnızca bu yazımlar arasında bellekte tutulur; bu yüzden bir çökme en fazla son yarım dakikalık istatistiği kaybettirebilir.

```json
{
  "format": "heat3d-watch-session",
  "version": 1,
  "watcher": "1.0.2",
  "game": "EA SPORTS F1 25",
  "adapter": "f1-25",
  "source": "UDP telemetry 127.0.0.1:20777 (...)",
  "multiplayer": true,
  "started": "2026-05-01T20:15:03",
  "ended": "2026-05-01T21:02:11",
  "seconds": 2828.0,
  "axes": {"up": "y", "flip_x": false, "flip_y": false, "flip_z": false, "scale": 1.0, "units": "metres"},
  "events": {"position": 52110, "lap": 412, "teleport": 3},
  "positions": 52530,
  "stats": {"laps": 20, "best_lap": 91.874, "distance_km": 106.3, "race_position": 4},
  "track": "..."
}
```

Kaynağı oyuncuyu adlandıran bir oturumda (bkz. [Oyuncunun kendi satırları](#the-players-own-rows)), oyuncunun kendi satırlarının taşıdığı adı içeren `"player"` de vardır. Uçuş simülatörlerinin oturumlarında dünya üzerinde bir yer vardır ve `"geo": {"lat0": .., "lon0": ..}` bulunur; altbilgideki `geo` bunu tekrarlar.

- `started` / `ended`: yerel saat, saniyeye kadar; oturum çalışırken `ended` `null`'dır.
- `events`: her olayın kaç kez olduğu, en sık olan önce. `positions`, konumu olan satırların sayısıdır.
- `stats`: oturumun sayıları. Bir adaptör her birini ayarlar, ekler ya da en büyüğünü ya da en küçüğünü tutar.
- Adaptörün oturum hakkında bildiği diğer her şey üst düzeyde yer alır: pist, harita, görev, maç kimliği, Steam uygulama kimliği, replay dosyası, bellek profili ve sürümü. Kurtarma ile bitirilen bir oturumda `"recovered": true` bulunur.

## watcher.sqlite {#watchersqlite}

`watcher.sqlite`, istatistik veritabanıdır. Her oturum kapandığında bir satır eklenir. Üç tablo düzdür; bu yüzden her SQL aracı, defter ya da elektronik tablo watcher olmadan okuyabilir:

```sql
CREATE TABLE sessions (
  id TEXT PRIMARY KEY,          -- <game folder>/<session folder>
  game TEXT NOT NULL,
  adapter TEXT NOT NULL,
  started REAL NOT NULL,        -- Unix seconds
  ended REAL,                   -- Unix seconds
  seconds REAL,
  folder TEXT NOT NULL,         -- the session folder's full path
  events INTEGER NOT NULL DEFAULT 0,
  positions INTEGER NOT NULL DEFAULT 0,
  multiplayer INTEGER NOT NULL DEFAULT 0,
  source TEXT
);
CREATE TABLE events (           -- per session, how many times each event happened
  session TEXT NOT NULL REFERENCES sessions(id) ON DELETE CASCADE,
  event TEXT NOT NULL,
  count INTEGER NOT NULL,
  PRIMARY KEY (session, event)
);
CREATE TABLE stats (            -- per session, every number the game reported or the watcher counted
  session TEXT NOT NULL REFERENCES sessions(id) ON DELETE CASCADE,
  key TEXT NOT NULL,
  value REAL,                   -- numbers
  text TEXT,                    -- everything else (a map name, a result, a hero)
  PRIMARY KEY (session, key)
);
```

Bir oturumun yeniden kaydedilmesi (kurtarma, yeniden dönüştürülen bir replay) satırlarını değiştirir. `multiplayer`, adaptörün bayrağıdır (bazı adaptörler bunu oturum başına ayarlar, örneğin DCS görevden), çevrimiçi olup olmadığınızın denetimi değildir. `stats` içindeki doğru/yanlış bir değer metin olarak tutulur.

Örnek bir sorgu, bütün oturumlar üzerinde oyun başına en iyi tur (küçük olan daha iyidir):

```sql
SELECT s.game, MIN(t.value) AS best_lap
FROM stats t JOIN sessions s ON s.id = t.session
WHERE t.key = 'best_lap'
GROUP BY s.game;
```

`python -m heat3d_watch stats`, bu tablolardan toplamları yazar (bkz. [Komutlar](commands.md#stats)); onun `best` sütunu, en iyi süre olarak tutulan süreler ve sıralamalar için en küçük, öbürleri için en büyük değerdir.

## Bir çökmeden sonra kurtarma {#recovery-after-a-crash}

`run` başladığında, önceki bir watcher'ın açık bıraktığı oturumlara bakar: `ended` alanı olmayan bir `meta.json` ve en az bir satırı olan bir `events.jsonl`. Her birini tamamlar:

- olay sayıları ve konum sayısı `events.jsonl`'den yeniden sayılır, yarım kalan satır atlanarak;
- bitiş, son satırın duvar saati zamanıdır (`ms`);
- istatistikler, son `meta.json` yazımındakilerdir (en fazla 30 saniye eski);
- `"recovered": true` eklenir, `heat.parquet` yazılır ve oturum `watcher.sqlite` içine girer.

Günlük "finished N session(s) left open by an earlier run" (önceki bir çalıştırmanın açık bıraktığı N oturum tamamlandı) yazar. Kilit dosyası, çalışan bir watcher'ın başka bir watcher'ın oturumlarını "kurtarmasını" engeller.

## CSV dışa aktarma {#csv-export}
![stats --csv and table](../assets/img/csv-and-table.svg)


```bash
python -m heat3d_watch stats --csv out
```

`out\sessions.csv`, `out\events.csv` ve `out\stats.csv` dosyalarını yazar. Her dosya, `watcher.sqlite` içindeki bir tablonun tamamıdır, başlık satırıyla, UTF-8 olarak. Zamanlar veritabanındaki gibi Unix saniyesidir. `--game` dışa aktarmayı daraltmaz; her oturum yazılır.

## Bir oturumu 3DHeat görüntüleyicisinde açmak {#opening-a-session-in-the-3dheat-viewer}

Görüntüleyici: [github.com/Holdi601/3DHeat](https://github.com/Holdi601/3DHeat), belgeleri [holdi601.github.io/3DHeat](https://holdi601.github.io/3DHeat/) - [`.3dheat` kapsayıcısı](https://holdi601.github.io/3DHeat/container.html) sayfası, replay dönüştürücülerinin yazabildiği maç başına tek dosya biçimini anlatır.

Bir oturumun `heat.parquet` dosyasını 3DHeat görüntüleyicisinde açın. Altbilgi, görüntüleyiciye hangi sütunun konum, zaman, oyuncu, taraf ve oturum olduğunu ve yukarının hangi yön olduğunu söyler; bu yüzden hiçbir şeyin elle eşlenmesi gerekmez. Konumlar oyunun kendi dünya koordinatlarındadır. Diğer 3DHeat araçlarıyla dışa aktarılmış bir seviyenin (örneğin [3DHeat GameFiles](https://github.com/Holdi601/3DHeat-GameFiles) ile) üzerine çizildiğinde, olduğu yerlere oturur.

- **Isı haritaları**, konumu olan her satırı kullanır; `event`, `player`, `team` ya da `session` ile, herhangi bir öbür sütun gibi süzülür.
- **Çizgi ısısı**, bir oyuncunun her satırından bir sonrakine bir çizgi çeker; oynatmada her oyuncu, arkasında bir kuyruk olan, rota boyunca hareket eden bir noktadır. Görüntüleyicinin Güzergâhlar (Routes) paneli, `event` sütunundan hangi olayların bir rotayı **başlattığını** ve hangilerinin **bitirdiğini** seçer. Watcher sınırlayıcı olayları konumu olan satırlar olarak yazar, böylece orada seçilebilirler:
  - başlangıçlar: `spawn`, `respawn`, `session_start`. Bir başlangıç, açık olan rotayı, yeni yere çizgi çekmeden kapatır.
  - bitişler: `death`, `finish`, `session_end` ve `teleport`. Çizgi, bitiş satırının kendisine kadar uzanır; oyuncunun öldüğü, durduğu ya da götürüldüğü yer.

  Bir sıçrama - seyahat etmeden ulaşılan bir yer - iki satırdır: bırakılan yerde bir `teleport` ve hemen ardından ulaşılan yerde bir başlangıç. Yarış adaptörleri, araba beklenenden daha uzağa gittiğinde bir tane yazar (geri sarma ya da flashback, pistteki bir sıfırlama, boxlara dönüş, hızlı seyahat), varış yerinde `spawn` ile (BeamNG'nin sıfırlaması için `respawn`); `teleport` satırı varışı `to_x`, `to_y`, `to_z` olarak ve mesafeyi `metres` olarak taşır, başlangıç satırı ise `after: "teleport"`. Kamyon adaptörleri bir feribot, tren ya da yüklenen bir kayıt için aynısını yapar, uçuş adaptörleri ise hiçbir uçağın uçamayacağı bir sıçrama için. Yani bitişler arasında `teleport`, başlangıçlar arasında `spawn` olduğunda - görüntüleyicinin kendiliğinden önerdiği şey budur - bir rota sıçramanın bıraktığı yerde biter, bir sonrakisi vardığı yerde başlar ve hiçbir çizgi haritayı kesmez. Bir rota, `session` sütununun değiştiği yerin üzerinden hiçbir zaman geçmez. Bir konum satırı saniyede birkaç kez yazılır (çoğu telemetri için 10 Hz), bu da pürüzsüz bir çizgi verir.
- `session` sütunu, bir oturumu turlarına, aşamalarına, yaşamlarına ya da bedenlerine böler (Elite Dangerous, galaktik satırlarla her gezegenin yüzey satırlarını bu şekilde ayırır). Görüntüleyicide birini seçerseniz yalnızca o parçaya bakarsınız.

Satırlarla görüntüleyicinin ne yaptığı - süzgeçler, renkler, oynatma - görüntüleyicinin kendi belgelerinde anlatılır. Counter-Strike 2 demo oturumları, görüntüleyicinin ısı ve maç sekmelerinde dönüştürücünün `<map>/<match>.parquet` ve `<match>.match.json` dosyaları üzerinden açılır. iRacing'in konumları, oturumda listelenen `.ibt` dosyalarından gelir ve görüntüleyici bunları kendisi okur.
