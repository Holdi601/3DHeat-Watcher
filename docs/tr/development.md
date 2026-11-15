---
title: "Geliştirme"
nav_order: 12
lang: "tr"
source: development.md
source_hash: "cb213e22ddea"
nav_exclude: true
search_exclude: true
---
# Geliştirme {#development}

Bu sayfa bir oyun eklemek içindir: bir adaptörün nasıl kurulduğu, nasıl sınandığı ve belgelerinin nasıl üretildiği.

## Depo {#the-repository}

| Yol | Ne tutar |
|---|---|
| `heat3d_watch/cli.py` | komutlar ([Komutlar](commands.md)) |
| `heat3d_watch/watcher.py` | arka plan döngüsü: işlem listesi, her adaptör için bir iş parçacığı, güncellemeler |
| `heat3d_watch/session.py` | bir kayıt: `events.jsonl`, `heat.parquet`, `meta.json`, kurtarma |
| `heat3d_watch/db.py` | `watcher.sqlite` |
| `heat3d_watch/config.py` | ayarlar ve veri klasörü |
| `heat3d_watch/safety.py`, `heat3d_watch/memory.py` | bellek denetimleri ve salt okunur okuyucu ([Bellek okuma](memory-reading.md)) |
| `heat3d_watch/notify.py` | Windows bildirimleri |
| `heat3d_watch/adapters/` | oyun ya da oyun ailesi başına bir modül; `_` ile başlayan modüller ortak yardımcılardır |
| `heat3d_watch/decoders/` | yarış telemetri çözücüleri, 3DHeat GameCapture'ın tur kaydedicilerinden kopyalanmış |
| `heat3d_update/` | güncelleyici ([Güncellemeler](updates.md)) |
| `mods/beamng/heat3d/` | `setup beamng`'in kurduğu BeamNG protokol modu |
| `tests/` | testler |
| `tools/gen_game_pages.py` | bu belgelerdeki oyun sayfalarını yazar |

## Bir adaptör {#an-adapter}

Bir adaptör, `heat3d_watch.adapters.base.Adapter` sınıfından türetilmiş bir dataclass'tır. Alanları ne olduğunu söyler; yöntemleri işi yapar.

| Alan | Varsayılan | Ne demek |
|---|---|---|
| `id` | `""` | kısa ve sabit: oturum klasörleri, `disabled`, `replay_folders` ve `player_names` buna göndermede bulunur |
| `game` | `""` | oyunun adı, insanların yazdığı gibi; oturumlar bu adla kaydedilir |
| `kind` | `"telemetry"` | `telemetry`, `gsi`, `log`, `replay`, `platform`, `memory`'den biri ([Kaynaklar ve kurallar](sources-and-rules.md)) |
| `exes` | `()` | oyunun çalıştığını gösteren çalıştırılabilir dosya adları (büyük/küçük harf farketmez). Boşsa adaptör her zaman açıktır (`always` doğru olur) |
| `multiplayer` | `True` | oyun çevrimiçi oynanır: belleği asla okunmaz |
| `source` | `""` | sayıların nereden geldiği, bir kez söylenir |
| `records` | `()` | neyin kaydedildiği, her şey türü için bir öğe |
| `enable` | `""` | kaynağın nasıl açılacağı; bir şey gerekmiyorsa boş |
| `interval` | `0.1` | yoklamalar arasındaki saniye |
| `axes` | `Axes()` | dünyanın yukarı ekseni, aynalanmış eksenler, görüntüleyicinin birim ölçeği (1 tutun) ve birimler hakkında bir not |
| `verified` | `""` | ne denetlendiği, dürüstçe (aşağıya bakın) |
| `completeness` | `{}` | kaynağın, 3DHeat'in [dönüştürücü kuralına](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md) göre hesabı: `read` (satırlara dönüşenler), `raw` (olduğu gibi tutulanlar ve hangi `type` altında), `missing` (kaynağın vermediği ve nedeni), `size` (ham akışın bir saatte ne kadar büyüdüğü). Oyun sayfasındaki "Completeness" (Tamlık) bölümü bundan yazılır |

`source`, `records`, `enable`, `verified` ve `completeness` süs değil, belgelerdir. `games` bunları yazar, `games --markdown` [Tek tabloda tüm oyunlar](watcher.md) tablosunu üretir ve oyun sayfaları bunlardan oluşturulur. Kodun yaptığını tam olarak anlatacak şekilde yazın.

Yöntemlerin hepsi isteğe bağlıdır:

| Yöntem | Kim çağırır | Ne yapmalı |
|---|---|---|
| `missing(self) -> str \| None` | `games`, `status` ve başlatmadan önce | adaptörün bu bilgisayarda neden çalışamadığını söyler (bir DLL bulunamadı, bir klasör yok) ya da `None` |
| `setup(self, ctx, *, apply) -> list[str]` | `setup` | oyunun kendi çıktısını açar; her değişiklik için bir satır döndürür, dosyaları yalnızca `apply` doğruyken değiştirir. Bir dosyayı ilk değişikliğinden önce `<file>.heat3d-backup` olarak yedekleyin ve o yedeğin üzerine asla yazmayın. `setup`'ı yalnızca açacak bir şey varsa geçersiz kılın: `can_setup` (`setup` geçersiz kılındıysa doğru olur) `setup`'ın onu çalıştırıp çalıştırmayacağına ya da hiçbir şey değiştirilmeyeceğine karar verir; birden çok oyuna hizmet eden bir sınıf, kuramadığı oyunlar için `can_setup`'ı geçersiz kılar (Richard Burns Rally için `RallyAdapter`). |
| `start(self, ctx)` | oyunun işlemi göründüğünde (her zaman açık adaptörlerde: `run` başladığında) | soketleri açar, dosyaları bulur, nereden başlanacağını hatırlar |
| `poll(self, ctx)` | her `interval` saniyede, adaptörün kendi iş parçacığında | son yoklamadan beri oyunun söylediklerini alır ve kaydeder |
| `stop(self, ctx)` | oyun yok olduğunda ya da watcher durduğunda | oturumları ve soketleri kapatır |

Her adaptör kendi iş parçacığında (`Runner`) çalışır. `poll` içindeki bir hata günlüğe yazılır ve adaptör bir sonraki yoklamadan önce `min(5, interval × 10 + 0.5)` saniye bekler. Art arda 20 hatadan sonra ya da `start` içinde bir hatada adaptör durdurulur ve oyunun işlem kimliği değişene kadar yeniden başlatılmaz. `missing()` her taramada denetlenir, bu yüzden ucuz tutun.

Bir adaptör nesnesi oyun yeniden başladığında yeniden kullanılır; bu yüzden `start`, önceki çalıştırmadan kalan her şeyi sıfırlamalıdır.

### Kaydetmek {#registering-it}

Modülü `heat3d_watch/adapters/` klasörüne koyun ve adaptörleri modülün sonunda listeleyin:

```python
ADAPTERS = [MyAdapter(id="mygame", game="My Game", ...)]
```

`adapters.load()`, paketteki her modülü (`base` ve `_` ile başlayanlar hariç) içe aktarır ve onların `ADAPTERS` listelerini toplar. Aynı kimliğe sahip iki adaptör yüklemeyi `ValueError` ile durdurur. Modülü içe aktarılamayan bir modül (eksik bir bağımlılık) kendi oyunlarını dışarıda bırakır ve `games` bunu hatasıyla birlikte adlandırır; böylece bir oyunun sorunu öbürlerini durdurmaz.

## Context ve Session {#context-and-session}

`start`, `poll`, `stop` ve `setup`, bir `Context` alır:

| Üye | Ne demek |
|---|---|
| `settings` | `Settings` ([Kurulum ve çalıştırma](installing-and-running.md#settings)) |
| `data` | veri klasörü |
| `pid`, `exe` | oyunun işlem kimliği ve çalıştırılabilir dosya yolu; adaptör çalışan bir oyun için başlatıldığında. Kurulum klasörü `exe`'nin yanındadır |
| `open(adapter, *, game=None, when=None, axes=..., source=..., multiplayer=..., meta=..., geo=None)` | yeni bir `Session`. `game`, adaptörün oyun adını geçersiz kılar (birçok oyunu kapsayan adaptörler için); `when`, geçmişi anlatan oturumların başlangıcını ayarlar; `axes`, `source` ve `multiplayer` varsayılan olarak adaptörünkidir; `meta`, `meta.json`'a yazılan bir sözlüktür; `geo` (`{"lat0": .., "lon0": ..}`, ya da daha sonra `session.geo` ile ayarlanır) düz harita oturumunu dünyaya yerleştirir: `meta.json` ve tablonun altbilgisinde |
| `close(session)` | bir oturumu bitirir: tablo, `heat.raw.parquet`, `meta.json` ve `watcher.sqlite`'daki satırı. Ne olay ne de ham öğe olan bir oturum silinir; yalnızca ham öğeleri olan bir oturum tutulur (tablo yok, veritabanında satır yok). `None` kabul eder. Tablonun yolunu ya da `None` döndürür. |

Bir `Session` şunları kaydeder:

| Üye | Ne yapar |
|---|---|
| `event(name, *, t=None, ms=None, x=None, y=None, z=None, player=None, team=None, session=None, **attrs)` | bir satır. `t` varsayılan olarak oturumun başlamasından beri geçen saniyedir, `ms` ise şimdi. Bir konum, yalnızca `x`, `y` ve `z` üçü de verilmiş ve sonlu ise sayılır. `None` öznitelikler dışarıda bırakılır. |
| `position(x, y, z, **kw)` | adı `position` olan bir olay |
| `raw(type, payload=None, *, text=None, used=False, t=None, ms=None, **fields)` | kaynağın gönderdiği bir şeyi bütün olarak tutar: bir paketin ya da sayfanın baytları (`payload`), bir satır ya da bir JSON yanıtı olduğu gibi (`text`), ya da bir okumanın adlarıyla değerleri (`fields`, her biri kendi sütunu). `type`, kaynağın bu şey için kendi sözüdür (bir paket kimliği, bir eşlemenin adı, bir günlük olayı, bir uç nokta); `used`, bunun satırlara da dönüştüğünü söyler. Çağrıldığı anda `raw.bin` içine çerçevelenir, oturum kapandığında ya da kurtarıldığında `heat.raw.parquet` (zstd) olarak yazılır ve `meta.json` içindeki `selfCheck.completeness` altında `type` başına sayılır |
| `stat(key, value, how="set")` | bir istatistik: `set` ile ayarlanır, `add` ile eklenir, `max` ya da `min` tutulur |
| `now()` | oturumun başlamasından beri geçen saniye |
| `meta` | `meta.json`'a yazılan bir sözlük |
| `started`, `ended`, `folder`, `id`, `counts`, `positions` | ne zaman, nerede ve o ana kadar ne kaydedildi |

`event`, `stat` ve `raw` iş parçacığı için güvenlidir ve bir çalışan iş parçacığından çağrılabilir.

**Her adaptör kaynağının gönderdiği her şeyi tutar.** Satırlar görüntüleyicinin çizdiği şeylerdir; kayıt değildir. Bir bağlantı noktasına ulaşan her paket, okunan her paylaşımlı bellek sayfası (her değiştiğinde bütün eşleme), bir günlüğün ya da dışa aktarma betiğinin her satırı (adaptörün yok saydıkları da dahil), her JSON yanıtı ya da gönderilen her belge, geldiği anda `session.raw(...)`'a gider; satır olsun ya da olmasın ve adaptörün okuma hızının altına hiçbir şey indirilmeden. Bir oturum açılmadan önce gelen bir öğe bir oturum açar (yalnızca ham öğeleri olan bir oturum tutulur) ya da biri açılana kadar bekletilir; asla atılmaz. Ucuz çözülebilen ve anlamı kesin olan alanlar satırlara da konur. Bu, 3DHeat'in [dönüştürücü kuralıdır](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md): canlı bir akış gönderildiği anda kaybolur, bu yüzden bir adaptörün tutmadığı şey sonsuza dek kaybolur; bütün tuttuğu ise birisi onu anladığı gün çözülebilir. Boyut bedeli budur; zstd ve sözlük kodlaması bunu küçük tutar, şeyleri atlamaz. Her adaptörün testi kullanmadığı bir şey gönderir ve onun `heat.raw.parquet`'ten bütün olarak geri geldiğini ve `selfCheck.completeness.lost` değerinin 0 olduğunu denetler. `racing.Driving.raw` yarış adaptörleri için aynısını yapar (ve oturumu açar); `racing.Pages`, paylaşımlı bellek sayfalarını baytları değiştiğinde tutar ve boşa okumaları, `meta.json`'daki `unchanged_reads` içinde sayar.

Sistemin dayandığı kurallar:

- **Oyuncunun kendi satırları, kaynağın söylediğinden işaretlenir.** Kaynak oyuncunun kendisiyse `player="me"`; her oyuncu bir adla kaydediliyorsa, oyuncunun arabasının satırlarında `own_car=1` (oyunun oyuncu dizini ya da görüntülenen katılımcıya göre), ya da kaynak oyuncuyu adlandırıyorsa oyuncunun adı `session.meta["player"]` olarak (hemen `meta.json`'a yazılır). Asla tahmin etmeyin: kaynak söylemiyorsa adı bir ayardan (`player_names`, `riot_id`) alın ya da hiçbir şey işaretlemeyin. [NVIDIA highlights](nvidia-highlights.md) konumları yalnızca bu tür satırlardan alır (`platform.own_row`). Öbür oyuncular adlarıyla ya da kimlikleriyle gider.
- **Rotalar, konumu olan olaylarla sınırlanır**: `spawn`, `respawn` ve `session_start` bir rota başlatır; `death`, `finish`, `session_end` ve `teleport` bir rotayı bitirir. Oyuncu seyahat etmeden hareket ettiğinde (sıfırlama, geri sarma, hızlı seyahat, yüklenen bir kayıt), bıraktığı yerde `teleport`, vardığı yerde bir başlangıç (`spawn`, ya da oyunun adlandırdığı bir sıfırlama için `respawn`) yazın; böylece görüntüleyicinin çizgi ısısı bir rotayı bitirir ve yenisini başlatır, haritanın üzerinden çizgi çekmez. Araçlar için `Driving.jumped` bunu yapar.
- **Konumlar, oyunun kendi dünya koordinatlarında ve birimlerinde kalır**, `axes` ile anlatılır. Oyun kullanılabilir bir dünya çerçevesi vermediği durum dışında başka bir çerçeveye çevirmeyin (uçuş simülatörleri enlem ve boylamı, ilk konumun etrafında düz bir haritaya, `Tangent`'e koyar - DCS, teatrinin sabit başlangıcının etrafında - ve `open`'a `geo=tangent.geo()` verilir; böylece altbilgi haritanın dünyada nerede olduğunu söyler). `axes.scale`, görüntüleyicinin birim ölçeğidir - her konumu onunla çarpar - ve 1 kalır; böylece satırlar aynı oyundan aynı birimlerle dışa aktarılmış bir seviyeyle hizalanır; birimi `axes.units` içinde söyleyin.
- **İstatistik anahtarları** küçük harfli ve alt çizgili yazılır; bir birim varsa onu taşır (`distance_km`, `top_speed_kmh`, `max_altitude_m`, `duration_s`). En iyi değer olarak tutulan bir süre `best_` ile başlar (`min` ile tutulur), bir sıralama `_position` ile biter: `stats` bunların en küçüğünü, öbür her anahtarın en büyüğünü en iyi değer olarak gösterir (`db.lower_is_better`).

## Yardımcılar {#helpers}

| Yardımcı | Modül | Ne için |
|---|---|---|
| `Follower(find, since, stamp=None)`, `game_started(pid)`, `newest(paths)`, `read_shared(path)`, `steam_libraries()` | `_logfollow` | oyunun yazdığı bir günlüğü izlemek: paylaşımlı okumalar, yalnızca bu oturumun satırları, yeni ve yer değiştirmiş dosyalar, yalnızca tam satırlar |
| `UdpPort(port, forward=None, grace=0.0, recheck=3.0)`, `try_open(who)`, `receive()`, `close()` | `racing` | 127.0.0.1 üzerinde bir UDP telemetri bağlantı noktası, yalnızca boşsa alınır, başka bir programa bırakılabilir, isteğe bağlı olarak aktarılabilir |
| `Driving(adapter, ctx, hz=10.0, jump=50.0)`, `sample(...)`, `event(...)`, `lap(...)`, `count(...)`, `close()` | `racing` | araç oturumları: sabit hızda konumlar, mesafe, en yüksek hız, turlar; bir sıçrama olduğunda aracın bulunduğu yerde `teleport`, şimdi bulunduğu yerde `spawn` (`jumped(...)`) |
| `SharedView.open(name)` | `simracing_shm` | bir oyunun adlandırılmış paylaşımlı belleği, salt okunur, asla oluşturulmaz |
| `ReplayAdapter` (`patterns`, `folders(ctx)`, `convert(path, ctx)`) | `replays` | izlenen bir replay klasörü: dosyalar büyümeyi bıraktığında bir iş parçacığında dönüştürülür; ilk bakış yalnızca ne olduğunu not eder, `convert_existing(ctx, folder=None)` - [`replays`](commands.md#replays) komutu - bunları istek üzerine dönüştürür |
| `load_state`, `save_state` | `platform` | her zaman açık bir adaptörün ne gördüğünü hatırlamak, `<data>\state\<id>.json` içinde |
| `FlightLog`, `Tangent` | `xplane` | uçuş kayıtları (kalkışlar, inişler, kazalar, mesafe) ve ilk konum etrafındaki düz harita (`Tangent.geo()` oturumun `geo`'sudur) |
| `backup_once(path)` | `gsi`, `racing` | `<file>.heat3d-backup` kuralı |
| Steam'in dosyaları | `_steam` | ikili ve metin KeyValues, kayıt defterinden Steam klasörü |

Minimal bir günlük adaptörü, örnek olarak (uydurma bir oyun):

```python
from dataclasses import dataclass, field
from pathlib import Path

from ..session import Axes, Session
from ._logfollow import Follower, game_started, newest
from .base import Adapter, Context


@dataclass
class ExampleAdapter(Adapter):
    _session: Session | None = field(default=None, repr=False)
    _follow: Follower | None = field(default=None, repr=False)

    def start(self, ctx: Context) -> None:
        log = (ctx.exe.parent if ctx.exe else Path(".")) / "logs" / "game.log"
        self._session = None
        self._follow = Follower(lambda: newest(p for p in [log] if p.exists()), game_started(ctx.pid))

    def poll(self, ctx: Context) -> None:
        for line in self._follow.lines() if self._follow else []:
            if line.startswith("DIED "):
                if self._session is None:
                    self._session = ctx.open(self)
                self._session.event("death", player="me")
                self._session.stat("deaths", 1, "add")

    def stop(self, ctx: Context) -> None:
        self.poll(ctx)
        ctx.close(self._session)
        self._session = None


ADAPTERS = [
    ExampleAdapter(
        id="example",
        game="Example Game",
        kind="log",
        exes=("ExampleGame.exe",),
        source=r"<install>\logs\game.log (followed)",
        records=("deaths",),
        interval=0.5,
        axes=Axes(units="no positions recorded"),
        verified="tested on synthetic log lines in the game's format; untested against the game",
    )
]
```

Oturumu `start` içinde değil, kaydedilecek ilk şey ortaya çıktığında açın; böylece menülerinde kalan bir oyun hiçbir şey bırakmaz (boş bir oturum zaten silinir).

## Testler {#tests}

```bash
python -m pytest
```

`tests/conftest.py`, her teste geçici bir veri klasörü (`HEAT3D_WATCH_HOME`) verir ve güncelleme denetimlerini ve bildirimleri kapatır (`HEAT3D_NO_UPDATE`, `HEAT3D_NO_TOAST`). Bir adaptör testi, oyunun çıktısını yayımlanmış biçiminden kurar - spesifikasyondan paketler, oyunun biçimindeki günlük satırları, belgelenmiş düzendeki dosyalar - ve adaptörü doğrudan sürer (`tests/test_poe.py`'den kısaltılmış; `data` ve `install` geçici klasörlerdir):

```python
from dataclasses import replace
from heat3d_watch.adapters import poe
from heat3d_watch.adapters.base import Context
from heat3d_watch.config import Settings
from heat3d_watch.session import read_rows

ctx = Context(Settings(data=str(data)), data, exe=install / "PathOfExileSteam.exe")
a = replace(poe.ADAPTERS[0])   # a fresh copy of the adapter
a.start(ctx); a.poll(ctx); a.stop(ctx)
[session] = list((data / "sessions").glob("*/*"))
rows = read_rows(session)      # then check the rows and meta.json's stats
```

Ağ adaptörleri, sahte bir yerel sunucuya karşı ya da adaptöre UDP üzerinden gönderilen paketlerle test edilir. Geliştiricinin bilgisayarındaki gerçek oyun verisine karşı denetleyen testler `@pytest.mark.local` ile işaretlenir ve o veri yoksa atlanır. Bu veri depoya asla girmez. `test_core.py`, paketin içinde başka bir işleme yazabilecek herhangi bir kod görünürse başarısız olan testi de içerir (`test_memory_reading_cannot_write`).

## Dürüst bir `verified` {#an-honest-verified}

`verified`, neyin, nasıl denetlendiğini ve neyin denetlenmediğini söyler. `games` tarafından ve her oyun sayfasında gösterilir; oyuncular buna güvenir. Koddan örnekler:

- "tested on packets in the 2023, 2024 and 2025 formats built from EA's published specification, sent over UDP; untested against the game"
- "tested on documents in the published GSI format posted to the running adapter; untested against the running game"
- "tested on real stats files and schemas from a local install; change detection tested on files built in the binary KeyValues format"

Adaptör çalışan oyunu kaydedene kadar "untested against the game" (oyuna karşı denenmedi) deyin. Yalnızca yöntemi ve toleransı yazın: gerçek dosyalardan bir harita, maç kimliği, oyuncu adı, tarih, veri kümesi büyüklüğü ya da kesin bir sayı asla, ve asla "bu makine" (okuyucular onu bilmez). Her düzenin ve her yerleşimin kaynağını adlandırın ve iki kaynağın nerede karşılaştırıldığını söyleyin. Yapılandan fazlasını asla iddia etmeyin. Tahmin edilmiş ya da topluluk araçlarından alınmış bir biçim, öyle olduğu söylenir.

## Oyun sayfaları {#the-game-pages}

[Oyunlar](games.md) altındaki her sayfa adaptörlerden üretilir, bu yüzden her zaman koda uyar. Bir adaptörü ekledikten ya da değiştirdikten sonra, depo klasöründen yeniden üretin:

```bash
HEAT3D_NO_UPDATE=1 python tools/gen_game_pages.py
```

(PowerShell'de: `$env:HEAT3D_NO_UPDATE = "1"; python tools/gen_game_pages.py`.) Yalnızca karşılaştırmak için `--check` ekleyin: hiçbir şey yazmaz ve bir sayfa eskiyse 1 ile çıkar (`docs/watcher.md`'deki oyun tablosu da denetlenir).

Betik şunları yapar:

- `heat3d_watch.adapters.load()` ile adaptörleri, boş bir geçici veri klasörüne karşı yükler; böylece makinenizdeki hiçbir bellek profili ya da ayar sayfalara girmez. Bellek adaptörleri dışarıda bırakılır, çünkü onlar oyuncuların kendi profillerinden gelir;
- bir adaptör modülü içe aktarılamazsa hiçbir şey yazmayı reddeder (sayfalar o oyunları kaybederdi);
- her adaptör için `docs/game-<adapter id>.md` ve genel tabloyla `docs/games.md` yazar; artık var olmayan adaptörlerin sayfalarını siler;
- "What is recorded" (Neyin kaydedildiği), "Where it comes from" (Nereden geldiği), "How to switch it on" (Nasıl açılacağı), eksenleri, çevrimiçi oyun bayrağını ve "Verified" (Denetlenme) bilgisini adaptörün alanlarından alır;
- modülün belge dizgisini "How it works" (Nasıl çalışır) bölümüne çevirir. Belge dizgilerini modüllerin zaten kullandığı düz metin biçiminde yazın; betik bunları çevirir: paragraflar; `*`, `-` ya da `1.` ile listeler; tanıtan satırın altında girintili düzenler ve örnekler (kod bloklarına dönüşürler); tireyle altı çizili bir başlık ya da hemen altında girintili metni olan kısa bir başlık satırı (başlıklara dönüşürler);
- adaptörün sınıflarında ve kullandığı yardımcılarda kodun adla ayarladığı istatistik anahtarlarını listeler - `.stat("key", ...)`, bir `if` ifadesinin iki tarafı ve `score.{team}` gibi f-string kalıpları. Bir değişkenden alınan anahtarlar (oyunun alanlarından oluşan bir tablo) listelenmez;
- "Positions" (Konumlar) bölümünü adaptörün `axes.units` değerinden (`no` ya da `none` ile başlayan bir not konum olmadığı anlamına gelir) ve kodunun neyi yazdığından belirler.

Üretilen sayfaları elle düzenlemeyin: adaptörü değiştirin ve betiği yeniden çalıştırın. [Tek tabloda tüm oyunlar](watcher.md) içindeki tablo, `python -m heat3d_watch games --markdown` komutunun çıktısıdır.
