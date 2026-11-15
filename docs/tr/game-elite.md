---
title: "Elite Dangerous (günlük dosyaları)"
nav_order: 18
lang: "tr"
source: game-elite.md
source_hash: "bb5bcf75553a"
nav_exclude: true
search_exclude: true
---
# Elite Dangerous (günlük dosyaları) {#elite-dangerous-log-files}

Elite Dangerous oynarken izleyici, oyunun yazdığı dosyaları okur ve olanları kaydeder; böylece bunlara daha sonra 3DHeat görüntüleyicisinde bir harita üzerinde bakabilirsiniz.

*Teknik ayrıntılar: uyarlayıcı `elite`, tür [`log`](sources-and-rules.md); `EliteDangerous64.exe` çalışırken çalışır ve her 0,25 saniyede bir yeni veri arar.*

## Ne kaydedilir {#what-is-recorded}

- her günlük olayı, kendi günlük adıyla, düz alanlarıyla birlikte
- galaktik konum (StarPos, ışık yılı) sıçramalarda, konumlarda, doğuşlarda, ölümlerde, yanaşmada, inişte
- LoadGame/Resurrect'te doğuş, Died'da ölüm, docked/undocked, touchdown/liftoff, jump, session_end
- Status.json'dan gezegen yüzeyi rotası: enlem, boylam, yükseklik, yön ve her gezegen için (oturum = gezegen adı) bir teğet düzlemde metre; ayrıca Status.json'un diğer düz alanları (Flags, Flags2, GuiFocus, LegalState, ...)
- her günlük satırı ve her yardımcı dosya bütün olarak heat.raw.parquet içinde
- sıçramalar, sıçrama mesafesi, ölümler, öldürmeler, kazanılan krediler, tamamlanan görevler, taranan gezegenler, ziyaret edilen sistemler, yanaşmalar, inişler

## Veri nereden gelir {#where-it-comes-from}

Oyuncu günlüğü %USERPROFILE%\Saved Games\Frontier Developments\Elite Dangerous\Journal.\*.log (en yeni dosya, yazıldıkça izlenir), aynı klasördeki Status.json ve diğer yardımcı \*.json dosyaları (Market, Outfitting, Shipyard, NavRoute, Cargo, ModulesInfo, ShipLocker, Backpack, FCMaterials)

## Nasıl açılır {#how-to-switch-it-on}

Hiçbir şeyi açmanız gerekmez: izleyici kaynağı, oyunun veya platformun sunduğu haliyle okur.

## Nasıl çalışır {#how-it-works}

Elite Dangerous: oyunun çalışırken yazdığı Oyuncu Günlüğü ve Status.json.

Konum: `%USERPROFILE%\Saved Games\Frontier Developments\Elite Dangerous\`

* `Journal.<yyyy-mm-ddThhmmss>.<part>.log` - satır başına bir JSON nesnesi, oyunun her açılışı için bir dosya (uzun bir oturum .02, .03 ... bölümleriyle devam eder). Her satırda `timestamp` (UTC, ISO 8601) ve `event` vardır. Galaktik konumlar, `FSDJump`, `Location` ve `CarrierJump` olaylarında sistemin Sol'den ışık yılı cinsinden `StarPos` [x, y, z] değerleridir. Elite'in galaktik çerçevesi y yukarı (galaktik kuzeye doğru), z galaktik merkeze doğru ve x galaktik boylam 270'e doğrudur - sol el çerçevesi; bu yüzden görüntüleyici z'yi aynalayarak doğru yönde çizer.
* `Status.json` - geminin durumu her değiştiğinde baştan yazılır: `Flags` ve bir gezegenin yakınındayken `Latitude`, `Longitude` (derece), `Altitude` (metre), `Heading`, `BodyName` ve `PlanetRadius` (metre).
* Diğer yardımcı dosyalar, her biri ilgili günlük olayı yazıldığında baştan yazılır: `Market.json`, `Outfitting.json`, `Shipyard.json`, `NavRoute.json`, `Cargo.json`, `ModulesInfo.json`, `ShipLocker.json`, `Backpack.json`, `FCMaterials.json`. Klasördeki, bu oturumda oyunun yazdığı her `*.json` dosyası değiştiğinde bütün olarak saklanır (3DHeat'in dönüştürücü kuralı: kaynağın tuttuğu okunur veya saklanır), dosya adı altında.

Her günlük satırı, oturumun ham yan dosyasında `event` adı altında bütün olarak saklanır; her yardımcı dosya dosya adı altında saklanır; JSON olmayan bir satır `unparsed` altında tutulur.

Yüzey konumları, gezegen başına yerel bir teğet düzleme yerleştirilir ve metre cinsindendir: bir gezegendeki ilk ölçüm o gezegenin başlangıç noktasıdır; x doğu, z kuzey, y yukarı (yükseklik); galaktik çerçeveyle aynı el yapısında. Satırlar gezegenin adını `session` olarak taşır; böylece bir gezegende sürüş veya yürüyüş kendi rotası olarak çizilir. Galaktik satırların oturumu "galaxy"dir. İki ölçek tek bir tabloda durur; görüntüleyicide oturumu seçin.

Biçim: Frontier'in "Elite Dangerous Player Journal" kılavuzu (her güncellemeyle resmî forumlarda yayınlanır, <https://forums.frontier.co.uk/> - "Journal Manual", v4.x); olaylar ve alanlar orada belgelendiği gibi; Status.json bayrakları aynı kılavuzun "Status File" bölümüne göredir.

## Konumlar ve eksenler {#positions-and-axes}

| | |
|---|---|
| Konumlar kaydedilir | evet |
| Yukarı eksen | `y` |
| Birimler | ışık yılı (galaktik satırlar, oturum 'galaxy'); bir gezegendeki ilk ölçümden itibaren doğu/yukarı/kuzey metre (yüzey satırları, oturum = gezegen adı) |
| Görüntüleyici için aynalama | `z` |
| Birim ölçeği (`scale`: görüntüleyici konumları bununla çarpar) | 1 |

Bunlar her oturumun `meta.json` dosyasındaki (`axes`) ve oturumda konum varsa `heat.parquet` dosyasının altbilgisine yazılır; böylece 3DHeat görüntüleyicisi satırları kendi başına döndürür ve ölçekler. Bkz. [Veriler](the-data.md).

## Çok oyunculu {#multiplayer}

- Çevrimiçi oynanan olarak işaretli (`multiplayer`): **evet**. `games --markdown` bunu "izinli (yalnızca oyunun yayınladığını okur)" olarak gösterir.
- Tür `log`: yalnızca oyunun veya platformun dışarı verdiğini okur (oyunun çalışırken yazdığı dosyalar); bu yüzden çevrimiçi oyunda da kaydeder. Bayrak yalnızca belleğin hiç okunup okunamayacağını belirler.
- Bellek: bu uyarlayıcı **asla** okumaz. Yalnızca `memory` uyarlayıcıları bellek okur ve çevrimiçi oynanan olarak işaretli bir oyun için hiçbir zaman. Bkz. [Kaynaklar ve kurallar](sources-and-rules.md).

## Kaydedilen istatistikler {#statistics-recorded}

Bu uyarlayıcının kodunun ada göre ayarladığı istatistik anahtarları (her oturumun `meta.json` dosyasındaki `stats` ve `watcher.sqlite` dosyasındaki `stats` tablosu):

`bad_lines`, `bodies_scanned`, `carrier_jumps`, `credits`, `credits_earned`, `deaths`, `distance_ly`, `dockings`, `jumps`, `kills`, `landings`, `missions_completed`, `ship`, `surface_fixes`, `systems_visited`

Süslü parantez içindeki bir anahtar çalışma zamanında tamamlanır (`score.{team}` her takım için ayrı bir anahtardır). Kodun oyunun alan tablosundan veya oyunun kendi istatistik adlarından aldığı anahtarlar bu listede yer almaz; yukarıdaki "Ne kaydedilir" bölümü onları adlandırır.

## Tamlık {#completeness}

İzleyici 3DHeat'in [dönüştürücü kuralını](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md) izler: kaynağın tuttuğu her şey okunur veya saklanır, hiçbir şey atılmaz. Satırların yanında, uyarlayıcının aldığı her paket, sayfa, satır veya yanıt oturumun `heat.raw.parquet` dosyasında bütün olarak saklanır (sütunlar `time`, `ms`, `type`, `used`, `payload`, `text` ve ada göre tutulan her alan; `used` satırlara da dönüşenleri işaretler). `meta.json` içindeki `selfCheck.completeness` her `type` değerini sayar; `lost` 0'dır.

**Okunan**

- her günlük satırı, `event` adı altında bir satır olarak, düz alanlarıyla (oyunun verdiği yerelleştirilmiş metin varsa o; 300 karakterden uzun metinler satırda kesilir)
- galaktik satırlar (StarPos): FSDJump, CarrierJump, Location, LoadGame, Resurrect, Died, Docked, Undocked, Touchdown, Liftoff, Shutdown olaylarında; yüzey satırları Status.json'dan ve Touchdown/Liftoff'tan
- Status.json'un düz alanları (Flags, Flags2, GuiFocus, LegalState, Cargo, FireGroup, Oxygen, Health, Temperature, Gravity, SelectedWeapon, ...) yüzey satırlarında
- istatistikler: sıçramalar, mesafe, ölümler, öldürmeler, kazanılan krediler, görevler, taranan gezegenler, ziyaret edilen sistemler, yanaşmalar, inişler

**Ham olarak saklanan**

- her günlük satırı bütün olarak, `type` = `event` değeri (FSDJump, Scan, Music, ReceiveText, ...), `used` true: satırların dışarıda bıraktığı listeler ve nesneler (StarPos, Factions, Rewards, Killers, Materials, Modules, ...) yalnızca burada bulunur
- JSON olmayan bir günlük satırı, `type` `unparsed`
- oyun her yeniden yazdığında bütün yardımcı dosya, `type` = dosya adı: `Status.json` (yüzey satırı yaptığında `used`), `Market.json`, `Outfitting.json`, `Shipyard.json`, `NavRoute.json`, `Cargo.json`, `ModulesInfo.json`, `ShipLocker.json`, `Backpack.json`, `FCMaterials.json` ve oyunun orada yazdığı diğer her `*.json`

**Mevcut olmayan**

- sıçramalar arasındaki konum (bir sistemin içinde, supercruise'da veya normal uzayda): oyun yalnızca sistemin StarPos değerini ve bir gezegenin yakınındayken enlem, boylam ve yüksekliği yazar
- diğer gemilerin ve oyuncuların konumları: günlük komutanın kendi kaydıdır
- hız, gaz ve diğer uçuş telemetrisi: oyun bunları yazmaz
- önceki oturumların günlükleri ve yardımcı dosyaları: oyun oynandığında saklanır (izleyici, bu oyun çalışmasından eski bir dosyanın sonundan başlar)
- Frontier'in şirket web API'si (cAPI): oyuncunun Frontier girişini gerektirir; oyunun yazdığı bir dosya değildir

**Boyut**: saatte yaklaşık 1-5 MB ham metin: günlük 0,2-2 MB, Status.json (1 KB'den küçük, saniyede en fazla bir kez yeniden yazılır) 1-2 MB, ziyaret edilen istasyon başına bir market/outfitting/shipyard seti 20-150 KB; heat.raw.parquet içindeki zstd bunu yaklaşık onda bire indirir

## Doğrulama {#verified}

çözümleyici, yerel bir kurulumdan alınan gerçek günlük dosyaları üzerinde tekrar oynatıldı (olay sayıları istatistiklerle eşleşiyor); Status.json'daki yüzey konumları yalnızca sentetik anlık görüntülerde test edildi

## Kaynak {#source}

[heat3d_watch/adapters/elite.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/elite.py)

<!-- Adaptörden tools/gen_game_pages.py ile üretilmiştir; sayfayı elle düzenlemek yerine adaptörü değiştirin ve yeniden çalıştırın. -->
