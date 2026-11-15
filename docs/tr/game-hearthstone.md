---
title: "Hearthstone (günlük dosyaları)"
nav_order: 25
lang: "tr"
source: game-hearthstone.md
source_hash: "e79c19776947"
nav_exclude: true
search_exclude: true
---
# Hearthstone (günlük dosyaları) {#hearthstone-log-files}

Hearthstone oynarken izleyici, oyunun yazdığı dosyaları okur ve ne olduğunu kaydeder; böylece bunlara daha sonra istatistik ve zaman çizelgesi olarak bakabilirsiniz.

*Teknik ayrıntılar: bağdaştırıcı `hearthstone`, tür [`log`](sources-and-rules.md); `Hearthstone.exe` çalışırken çalışır ve yeni veri için her 0,5 saniyede bir bakar.*

## Ne kaydedilir {#what-is-recorded}

- oyunun başlangıcı ve sonu, sonuçla birlikte (kazandı, kaybetti, berabere), turlar ve rakibin adı
- her tur
- Power.log ve diğer günlüklerin her satırı bütün olarak heat.raw.parquet içinde
- oyunlar, galibiyetler, mağlubiyetler, beraberlikler, turlar, en uzun oyun

## Kaynağı {#where-it-comes-from}

&lt;kurulum>\Logs\Power.log (ya da Logs\Hearthstone_\*\Power.log), %LOCALAPPDATA%\Blizzard\Hearthstone\log.config içinde bir [Power] bölümü olduğunda yazılır; oyunun orada yazdığı diğer her \*.log dosyası da

## Nasıl açılır {#how-to-switch-it-on}

`python -m heat3d_watch setup hearthstone --apply` komutu %LOCALAPPDATA%\Blizzard\Hearthstone\log.config dosyasına [Power] günlük tutmayı ekler (yedek alınır); oyunu yeniden başlatın

Komutu, izleyicinin klasöründe açılmış bir terminale yazın (bkz. [Başlamadan önce](before-you-start.md)). Başarısız olursa son satır nedenini söyler; [Kurulum ve çalıştırma](installing-and-running.md) yaygın nedenleri anlatır.

`python -m heat3d_watch setup hearthstone` hangi dosyaları değiştireceğini listeler; `python -m heat3d_watch setup hearthstone --apply` onları değiştirir ve özgün dosyayı `<file>.heat3d-backup` olarak saklar (bkz. [Komutlar](commands.md#setup)). Her değişiklik için `hearthstone: changed: ...` yazar; zaten açıksa `hearthstone: nothing to change` yazar.

## Nasıl çalışır {#how-it-works}

Hearthstone: oyunun Power.log dosyası; `log.config` bunu istediğinde yazılır.

Hearthstone açılışta `%LOCALAPPDATA%\Blizzard\Hearthstone\log.config` dosyasını okur; `LogLevel=1` ve `FilePrinting=true` içeren bir `[Power]` bölümü, her oyunun durum değişikliklerini `<kurulum>\Logs\Power.log` dosyasına yazdırır (yeni istemciler her açılışın günlüklerini kendi klasöründe tutar: `Logs\Hearthstone_<tarih>\`). Bu, 2014'ten beri deste izleyicilerinin açtığı belgelenmiş hata ayıklama günlüğüdür (Hearthstone Deck Tracker'ın kurulumu aynı bölümü yazar). `setup()` bölümü ekler; dosyanın eski hâlinin yedeğini alır; oyunun bunu okuyabilmesi için yeniden başlatılması gerekir.

Kullanılan satırlar, hepsi `GameState.DebugPrintPower()` içindendir (`PowerTaskList` satırları bunları tekrarlar ve atlanır):

```text
D 20:15:01.1234567 GameState.DebugPrintPower() - CREATE_GAME
D 20:15:01.1234567 GameState.DebugPrintPower() -     Player EntityID=2 PlayerID=1 GameAccountId=[hi=1 lo=2]
D 20:15:01.1234567 GameState.DebugPrintGame() - PlayerID=1, PlayerName=Name#1234
D 20:15:02.1234567 GameState.DebugPrintPower() -     FULL_ENTITY - Updating [entityName=... id=4 zone=HAND
                   zonePos=0 cardId=CS2_029 player=1] CardID=CS2_029
D 20:16:00.1234567 GameState.DebugPrintPower() - TAG_CHANGE Entity=GameEntity tag=TURN value=3
D 20:25:00.1234567 GameState.DebugPrintPower() - TAG_CHANGE Entity=Name#1234 tag=PLAYSTATE value=WON
D 20:25:00.1234567 GameState.DebugPrintPower() - TAG_CHANGE Entity=GameEntity tag=STATE value=COMPLETE
```

Oyuncunun kendi tarafı, adları görünen kartlara sahip başlangıç eliyle belirlenir (rakibinkiler gizlidir); yoksa hesabı 0 olmayan (yapay zeka hesabı 0'dır) ya da "UNKNOWN HUMAN PLAYER" olmayan taraftır. Satırlar yalnızca günün saatini taşır; tarih bugünün tarihidir. Konum yoktur.

Power.log'un her satırı bütün olarak oturumun ham yan dosyasında saklanır (3DHeat'in dönüştürücü kuralı); `PowerTaskList` tekrarları, seçenekler, seçimler ve varlık güncellemeleri dahildir. `type` satırı yazan metottur (`GameState.DebugPrintPower`, `PowerTaskList.DebugPrintPower`, `GameState.DebugPrintOptions`, ...). Oyunun yanında yazdığı diğer günlükler - `LoadingScreen.log`, `Decks.log`, `Zone.log`, `Arena.log`, ... her biri log.config istediğinde yazılır (deste izleyicileri çoğu zaman ister) - adlarıyla birlikte `log` içinde aynı şekilde izlenir ve saklanır.

## Konumlar ve eksenler {#positions-and-axes}

| | |
|---|---|
| Kaydedilen konumlar | hayır |
| Yukarı ekseni | `y` |
| Birimler | konum kaydedilmez |
| Görüntüleyici için aynalama | yok |
| Birim ölçeği (`scale`: görüntüleyici konumları bununla çarpar) | 1 |

Bunlar her oturumun `meta.json` dosyasındaki (`axes`) ve konum içeren oturumlarda `heat.parquet` dosyasının sonundaki (footer) bilgiye yazılır; böylece 3DHeat görüntüleyicisi satırları kendisi döndürür ve ölçekler - bkz. [Veriler](the-data.md).

## Çok oyunculu {#multiplayer}

- Çevrimiçi oynanan olarak işaretlenmiş (`multiplayer`): **evet**. `games --markdown` bunu "izinli (yalnızca oyunun yayımladığını okur)" olarak gösterir.
- Tür `log`: yalnızca oyunun ya da platformun dışarı verdiğini okur (oyunun çalışırken yazdığı dosyalar). Bu yüzden çevrimiçi oyunda da çevrimdışı olduğu gibi kaydeder; bayrak yalnızca belleğin hiç okunup okunamayacağını belirler.
- Bellek: bu bağdaştırıcı **asla** okumaz. Yalnızca `memory` bağdaştırıcıları bellek okur ve çevrimiçi oynanan olarak işaretlenmiş bir oyun için asla okumaz - bkz. [Kaynaklar ve kurallar](sources-and-rules.md).

## Kaydedilen istatistikler {#statistics-recorded}

Bu bağdaştırıcının kodunun adla ayarladığı istatistik anahtarları (her oturumun `meta.json` içindeki `stats` ve `watcher.sqlite` içindeki `stats` tablosu):

`bad_lines`, `games`, `longest_game_turns`, `losses`, `ties`, `turns`, `wins`

Parantez içindeki bir anahtar çalışma zamanında tamamlanır (`score.{team}` her takım için bir anahtardır). Kodun oyunun alanlarının tablosundan ya da oyunun kendi istatistik adlarından aldığı anahtarlar bu listede yer almaz; yukarıdaki "Ne kaydedilir" bölümü bunları adlandırır.

## Tamlık {#completeness}

İzleyici 3DHeat'in [dönüştürücü kuralını](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md) izler: kaynağın tuttuğu her şey okunur ya da saklanır, asla atılmaz. Satırların yanı sıra, bağdaştırıcının aldığı her paket, sayfa, satır ya da yanıt, oturumun `heat.raw.parquet` dosyasında bütün olarak saklanır (sütunlar `time`, `ms`, `type`, `used`, `payload`, `text` ve adla saklanan her alan; `used` satıra dönüşenleri işaretler). `meta.json` içindeki `selfCheck.completeness` her `type` değerini sayar - `lost` 0'dır.

**Okunan**

- `CREATE_GAME`, oyuncular (varlık, oyuncu kimliği, hesap; hesap 0 yapay zekadır) ve adları (`DebugPrintGame`)
- oyuncunun tarafı, başlangıç elindeki adlandırılmış kartlardan
- TURN, PLAYSTATE (kazandı, kaybetti, berabere) ve STATE COMPLETE için `TAG_CHANGE`: turlar, sonuç, rakip

**Ham olarak saklanan**

- Power.log'un her satırı bütün olarak, `type` = onu yazan metot (`GameState.DebugPrintPower`, `PowerTaskList.DebugPrintPower`, `GameState.DebugPrintGame`, `GameState.DebugPrintOptions`, `GameState.SendChoices`, `GameState.DebugPrintEntityChoices`, `PowerProcessor.DoTaskListForCard`, ...), `log` `Power` ve bir satıra dönüştüğü yerde `used`: oynanan, çekilen ve açığa çıkan her kart, her etiket değişikliği, her saldırı, seçenek ve seçim burada, henüz satırlarda değil
- aynı klasördeki diğer günlüklerin her satırı (`LoadingScreen`, `Decks`, `Zone`, `Arena`, `Achievements`, `FullScreenFX`, ... - log.config'in açtığı her ne ise), aynı `type`'lar, günlüğün adı `log` içinde
- seviyesi ve günün saati olmayan satır `untimed`, metodu olmayan satır `untagged` olarak

**Kullanılamayanlar**

- konumlar: bir kart oyununun konumu yoktur
- rakibin gizli kartları: günlük bir kartı yalnızca açığa çıktığında adlandırır
- log.config'in açmadığı günlükler: `setup` yalnızca [Power] ister; diğer günlükler başka bir araç (bir deste izleyicisi) onları açtığında gelir
- önceki açılışların günlükleri: her açılış yeni bir klasör yazar; oyunun bu çalışmasından önce olanlar yeniden okunmaz

**Boyut**: Verbose açıkken Power.log oyun başına yaklaşık 1-5 MB, saatte 10-40 MB; diğer günlükler az yer kaplar; heat.raw.parquet içindeki zstd bunu yaklaşık onda bire veya daha aza indirir (satırlar çok tekrar eder)

## Doğrulama {#verified}

oyunun biçiminde sentetik Power.log satırlarında test edilmiştir; oyunla test edilmemiştir

## Kaynak {#source}

[heat3d_watch/adapters/hearthstone.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/hearthstone.py)

<!-- Adaptörden tools/gen_game_pages.py ile üretilmiştir; sayfayı elle düzenlemek yerine adaptörü değiştirin ve yeniden çalıştırın. -->
