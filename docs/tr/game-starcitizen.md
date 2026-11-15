---
title: "Star Citizen (günlük dosyaları)"
nav_order: 41
lang: "tr"
source: game-starcitizen.md
source_hash: "7b1ce51dc50a"
nav_exclude: true
search_exclude: true
---
# Star Citizen (günlük dosyaları) {#star-citizen-log-files}

Star Citizen oynarken izleyici, oyunun yazdığı dosyaları okur ve ne olduğunu kaydeder; böylece bunlara daha sonra istatistik ve zaman çizelgesi olarak bakabilirsiniz.

*Teknik ayrıntılar: bağdaştırıcı `starcitizen`, tür [`log`](sources-and-rules.md); `StarCitizen.exe` çalışırken çalışır ve yeni veri için her 0,5 saniyede bir bakar.*

## Ne kaydedilir {#what-is-recorded}

- ölümler; kurban, katil, silah, hasar türü ve bölge ile (oyuncular ve NPC'ler)
- devre dışı kalan ve yok edilen araçlar; sürücü, neden ve bölge ile
- kuantum yolculuk hedefleri, güneş sistemi değişiklikleri, doğmalar, yeniden doğmalar, etkisiz kalmalar
- her Game.log satırı bütün olarak heat.raw.parquet içinde
- öldürmeler (oyuncu ve NPC), ölümler, intiharlar, yok edilen ve kaybedilen araçlar, kuantum atlamaları

## Kaynağı {#where-it-comes-from}

&lt;kurulum>\StarCitizen\LIVE\Game.log (çalışan StarCitizen.exe'nin derleme klasörü), yalnızca oyunun yazdığı günlük dosyası - bir Easy Anti-Cheat oyunu: süreç hiçbir şekilde karıştırılmaz

## Nasıl açılır {#how-to-switch-it-on}

Hiçbir şeyi açmanız gerekmez: izleyici kaynağı, oyunun ya da platformun sunduğu haliyle okur.

## Nasıl çalışır {#how-it-works}

Star Citizen: istemcinin kendi günlüğü, `<kurulum>\StarCitizen\LIVE\Game.log`.

Oyun Game.log dosyasını her açılışta baştan yazar (öncekisi `logbackups\` içine gider). Yalnızca bu dosya okunur: Star Citizen Easy Anti-Cheat çalıştırır ve burada hiçbir şey oyunun sürecine dokunmaz. Satırlar UTC zaman damgasıyla ve bir seviyeyle başlar, ardından açılı parantez içinde bir etiket gelir:

```text
<2025-04-13T17:17:51.279Z> [Notice] <Actor Death> CActor::Kill: 'Victim' [200146297631] in zone
    'ANVL_Hornet_F7A_Mk2_2677329226210' killed by 'Killer' [202061381370] using
    'GATS_BallisticGatling_S3_2677329225797' [Class unknown] with damage type 'VehicleDestruction'
    from direction x: 0.000000, y: 0.000000, z: 0.000000 [Team_ActorTech][Actor]
<...> [Notice] <Vehicle Destruction> CVehicle::OnAdvanceDestroyLevel: Vehicle 'ANVL_Arrow_123' [123] in zone
    'OOC_Stanton_1_Hurston' [pos x: 1.0, y: 2.0, z: 3.0 vel x: 0, y: 0, z: 0] driven by 'Driver' [456]
    advanced from destroy level 0 to 2 caused by 'Attacker' [789] with 'Combat' [Team_VehicleFeatures][Vehicle]
<...> [Notice] <AccountLoginCharacterStatus_Character> Character: createdAt 1 - updatedAt 2 - geid 3 -
    accountId 4 - name Handle - state STATE_CURRENT [Team_GameServices][Login]
<...> [Notice] <Quantum Navtarget> CSCItemQuantumDrive::RmMulticastOnQTToPoint : Local client user
    Handle[200000000001] received QT data for Entity:AEGS_Gladius_123[123] to Target Stanton1b ...
<...> [Notice] <Changing Solar System> ... Client entity Handle ... changing system from Stanton to Pyro ...
```

(burada sarılmış gösterildi; dosyada her biri tek satırdır). Bir ölümün bölgesi çoğunlukla kurbanın oturduğu gemidir, bir yer değildir. Biçim Cloud Imperium tarafından belgelenmemiştir ve yamalarla değişir; kalıplar, topluluk öldürme izleyicilerinin okuduğu satırları izler (ör. <https://github.com/DimmaDont/all-slain>, MIT - yalnızca gerçekler), eşleşmeyen her şey atlanır, tahmin edilmez. Bir aracın `pos` değeri bölgeye görelidir ve yalnızca metin olarak saklanır: hiçbir koordinat çizilmez.

Her satır bütün olarak oturumun ham yan dosyasında saklanır (3DHeat'in dönüştürücü kuralı), eşleşse de eşleşmese de: `type` satırın açılı parantez içindeki etiketidir (`Actor Death`, `Spawn Flow`, ...), yoksa parantez içindeki ilk kelimesi (`Notice`, `CSessionManager::OnClientSpawned`), yoksa `untagged`; zaman damgası olmayan satır `untimed`.

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

`bad_lines`, `deaths`, `incapacitations`, `kills`, `npc_kills`, `player_kills`, `quantum_jumps`, `suicides`, `system_jumps`, `vehicles_destroyed`, `vehicles_lost`

Parantez içindeki bir anahtar çalışma zamanında tamamlanır (`score.{team}` her takım için bir anahtardır). Kodun oyunun alanlarının tablosundan ya da oyunun kendi istatistik adlarından aldığı anahtarlar bu listede yer almaz; yukarıdaki "Ne kaydedilir" bölümü bunları adlandırır.

## Tamlık {#completeness}

İzleyici 3DHeat'in [dönüştürücü kuralını](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md) izler: kaynağın tuttuğu her şey okunur ya da saklanır, asla atılmaz. Satırların yanı sıra, bağdaştırıcının aldığı her paket, sayfa, satır ya da yanıt, oturumun `heat.raw.parquet` dosyasında bütün olarak saklanır (sütunlar `time`, `ms`, `type`, `used`, `payload`, `text` ve adla saklanan her alan; `used` satıra dönüşenleri işaretler). `meta.json` içindeki `selfCheck.completeness` her `type` değerini sayar - `lost` 0'dır.

**Okunan**

- `<Actor Death>`: kurban, katil, silah ve sınıfı, hasar türü, bölge; NPC mi oyuncu mu
- `<Vehicle Destruction>`: araç, bölge, bölgeye göre konum metin olarak, sürücü, neden, nasıl, yıkım seviyesi
- `<Quantum Navtarget>` hedefleri, `<Changing Solar System>`, `OnClientSpawned`, hastane yeniden doğmaları, nedenleriyle etkisiz kalmalar, `EndSession`
- oyuncunun tutamacı (handle), `<AccountLoginCharacterStatus_Character>` ya da giriş satırından

**Ham olarak saklanan**

- her Game.log satırı bütün olarak, `type` = açılı parantez içindeki etiketi (`Actor Death`, `Vehicle Destruction`, `Spawn Flow`, `Jump Drive State Changed`, `SHUDEvent_OnNotification`, `RequestLocationInventory`, ...), yoksa parantez içindeki ilk kelimesi (`Notice`, `CSessionManager::OnClientSpawned`, ...), yoksa `untagged`; zaman damgası olmayan satırlar (günlüğün başlığı, sarılmış metin) `untimed`; bir satıra dönüştüğü yerde `used`

**Kullanılamayanlar**

- konumlar: günlük, çizilebilecek bir çerçevede hiçbirini vermez (yok edilen bir aracın `pos` değeri, yeri kaydedilmeyen bir bölgeye görelidir)
- oyunun sürecinden ya da ağından hiçbir şey: Star Citizen Easy Anti-Cheat çalıştırır; yalnızca günlük dosyası okunur
- önceki açılışların günlükleri (`logbackups`): her açılışın Game.log dosyası oynandığında saklanır
- bir yamanın değiştirdiği biçimdeki satırlar: ham saklanır, yeni biçim bilindiğinde yeniden çözülür

**Boyut**: Game.log oyun saatinde yaklaşık 5-15 MB büyür (yoğun bölgelerde ve hatalarda daha fazla); heat.raw.parquet içindeki zstd bunu yaklaşık onda bire indirir

## Doğrulama {#verified}

topluluk izleyicilerinin belgelediği biçimdeki sentetik Game.log satırlarında test edilmiştir; oyunla test edilmemiştir

## Kaynak {#source}

[heat3d_watch/adapters/starcitizen.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/starcitizen.py)

<!-- Adaptörden tools/gen_game_pages.py ile üretilmiştir; sayfayı elle düzenlemek yerine adaptörü değiştirin ve yeniden çalıştırın. -->
