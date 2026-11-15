---
title: "IL-2 Sturmovik: Great Battles (tekrarlar)"
nav_order: 27
lang: "tr"
source: game-il2-tacview.md
source_hash: "0bb23bddee03"
nav_exclude: true
search_exclude: true
---
# IL-2 Sturmovik: Great Battles (tekrarlar) {#il-2-sturmovik-great-battles-replays}

IL-2 Sturmovik: Great Battles'ta bir maçtan sonra izleyici, oyunun kaydettiği tekrarı, 3DHeat görüntüleyicisinde bir harita üzerinde bakabileceğiniz dosyalara çevirir.

*Teknik ayrıntılar: uyarlayıcı `il2-tacview`, tür [`replay`](sources-and-rules.md); her zaman çalışır (bir oyunun başlamasını beklemez) ve her 5 saniyede bir yeni veri arar.*

## Ne kaydedilir {#what-is-recorded}

- kaydedilen her uçak, araç ve gemi: saniyede bir konum (kaydın referans noktasının doğusunda/yukarısında/kuzeyinde metre; enlem/boylam/yükseklik sütun olarak)
- doğuşlar, yok edilmeler (ölüm) ve ayrılmalar (sol), varsa kalkışlar ve inişler
- kayıt başına nesneler, yok edilenler, kalkışlar, inişler ve uzunluk
- kaydın her satırı, kayıt saatinde heat.raw.parquet içinde bütün olarak

## Veri nereden gelir {#where-it-comes-from}

Oyunun kendi Tacview kayıtları &lt;oyun>\data\Tracks\\\*.acmi (ACMI 2.x metni, düz veya zipli)

## Nasıl açılır {#how-to-switch-it-on}

python -m heat3d_watch setup il2-tacview --apply ([KEY = track_record] içinde tacviewrecord = 1)

Komutu, izleyicinin klasöründe açılmış bir terminale yazın (bkz. [Başlamadan önce](before-you-start.md)). Başarısız olursa, son satır nedenini söyler; [Kurulum ve çalıştırma](installing-and-running.md) sık görülen nedenleri anlatır.

`python -m heat3d_watch setup il2-tacview` değiştirilecek dosyaları listeler; `python -m heat3d_watch setup il2-tacview --apply` bunları değiştirir ve özgün dosyayı `<file>.heat3d-backup` adıyla saklar (bkz. [Komutlar](commands.md#setup)). Her değişiklik için `il2-tacview: changed: ...` yazar; zaten açıksa `il2-tacview: nothing to change` yazar.

## Nasıl çalışır {#how-it-works}

IL-2 Sturmovik: Great Battles - oyunun telemetri UDP çıktısı ve kendi Tacview kayıtları.

1. Telemetri ("Telemetry output of IL2 v4.003", revizyon 1.2; `<oyun>\Doc\UDP_Output\Il2_TeleOutput.pdf` olarak gelir). `<oyun>\data\startup.cfg` içinde, `[KEY = telemetrydevice]` bölümünde açılır: `addr`, `addr1`, ... = "IP[:port]" (aynı anda birkaç hedef), `decimation` (50 Hz / n), `enable`, `port`. `setup` bir hedef ekler, 127.0.0.1:41995 (JoyPro 41994'ü kullanır, oyunun varsayılanı 4322'dir) ve çıktıyı açar. Paketler, little-endian:

   ```text
   DWORD  Packet_ID 0x54000101
   WORD   Size
   DWORD  Tick (1/50 s)
   BYTE   Indicators_Count, then SIndicator {WORD id, BYTE n, n x 32-bit float}
   BYTE   Events_Count,     then SEvent     {WORD id, BYTE size, size bytes}
   ```

   Göstergeler: 0 ENG_RPM, 1 ENG_MP, 2/3 motor titreşimi, 4 LGEARS_STATE, 5 LGEARS_PRESS, 6 EAS (m/s), 7 AOA (rad), 8 ACCELERATION (yerçekimi dahil xyz), 9 COCKPIT_SHAKE, 10 AGL (m), 11 FLAPS, 12 AIR_BRAKES, 13 AOS (rad), 14 VERTICAL_SPEED (m/s). Olaylar (2 baytlık paketli): 0 SET_FOCUS (STRING: uzunluk baytı + ASCII), 1 SETUP_ENG {short index, short id, float pos[3], float max_rpm}, 2 SETUP_GUN {short index, float pos[3], float projectile mass, float muzzle velocity}, 3 SETUP_LGEAR {short index, short id, float pos[3]}, 4 DROP_BOMB ve 5 ROCKET_LAUNCH {float pos[3], float mass, WORD flags}, 6 HIT ve 7 DAMAGE {float pos[3], float force[3]}, 8 EXPLOSION {float pos[3], float radius}, 9 GUN_FIRE {BYTE gun}, 10 SRV_ADDR, 11 SRV_TITLE, 12 SRS_ADDR (STRING), 13 CLIENT_DAT {long client, long server client, char name[32]}, 14 CTRL_DAT {long parent, short coalition}. Olay konumları oyuncunun uçağına göredir; akışta hiç dünya konumu yoktur - yani bunlar bir iz değil, olaylar ve sayılardır.

2. Tacview kaydı: `[KEY = track_record]` içinde `tacviewrecord = 1` oyunun `<oyun>\data\Tracks\*.acmi` dosyasını yazmasını sağlar (çok oyunculuda sunucu karar verir). Biten bir dosya dönüştürülür: kayıtta bulunan her uçak, araç ve gemi konumlarıyla, doğuş ve kaldırılma (yok edilmiş veya gitmiş) ve varsa kalkış ve inişlerle birlikte. ACMI 2.x metin biçimi, düz veya zipli; <https://www.tacview.net/documentation/acmi/en/> adresine göre - "#t" satırları saati ilerletir, "id,Key=Value,..." satırları özellikleri ayarlar (onaltılık kimlikler, virgüller "\\," olarak kaçırılır, sondaki "\\" satırı devam ettirir), "-id" bir nesneyi kaldırır, nesne 0 genel değerleri (ReferenceLongitude/Latitude, RecordingTime, ...) ve olayları ("Event=Destroyed\|id\|text") taşır. T = Lon\|Lat\|Alt[\|U\|V] veya Lon\|Lat\|Alt\|Roll\|Pitch\|Yaw[\|U\|V\|Heading]; boylam ve enlem referansa görelidir, boş alanlar değişmez. Konumlar referans noktasının etrafında düz bir haritaya konur: x doğu, y yükseklik, z kuzey, metre. Referans noktası oturumun `geo` değeridir; meta.json'da ve tablonun altbilgisinde taşınır, böylece görüntüleyici gerçek dünyayı izlerin altına yerleştirebilir.

Bu modül şunlara da hizmet eder: [IL-2 Sturmovik: Great Battles (canlı veri)](game-il2.md).

## Konumlar ve eksenler {#positions-and-axes}

| | |
|---|---|
| Konumlar kaydedilir | evet |
| Yukarı eksen | `y` |
| Birimler | metre (doğu, yükseklik, ilk ölçümden itibaren kuzey) |
| Görüntüleyici için aynalama | `z` |
| Birim ölçeği (`scale`: görüntüleyici konumları bununla çarpar) | 1 |

Bunlar her oturumun `meta.json` dosyasındaki (`axes`) ve oturumda konum varsa `heat.parquet` dosyasının altbilgisine yazılır; böylece 3DHeat görüntüleyicisi satırları kendi başına döndürür ve ölçekler. Bkz. [Veriler](the-data.md).

## Çok oyunculu {#multiplayer}

- Çevrimiçi oynanan olarak işaretli (`multiplayer`): **evet**. `games --markdown` bunu "izinli (yalnızca oyunun yayınladığını okur)" olarak gösterir.
- Tür `replay`: yalnızca oyunun veya platformun dışarı verdiğini okur (oyunun kaydettiği tekrarlar ve demolar); bu yüzden çevrimiçi oyunda da kaydeder. Bayrak yalnızca belleğin hiç okunup okunamayacağını belirler.
- Bellek: bu uyarlayıcı **asla** okumaz. Yalnızca `memory` uyarlayıcıları bellek okur ve çevrimiçi oynanan olarak işaretli bir oyun için hiçbir zaman. Bkz. [Kaynaklar ve kurallar](sources-and-rules.md).

## Kaydedilen istatistikler {#statistics-recorded}

Bu uyarlayıcının kodunun ada göre ayarladığı istatistik anahtarları (her oturumun `meta.json` dosyasındaki `stats` ve `watcher.sqlite` dosyasındaki `stats` tablosu):

`destroyed`, `duration_s`, `objects`, `{r.event}s`

Süslü parantez içindeki bir anahtar çalışma zamanında tamamlanır (`score.{team}` her takım için ayrı bir anahtardır). Kodun oyunun alan tablosundan veya oyunun kendi istatistik adlarından aldığı anahtarlar bu listede yer almaz; yukarıdaki "Ne kaydedilir" bölümü onları adlandırır.

## Tamlık {#completeness}

İzleyici 3DHeat'in [dönüştürücü kuralını](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md) izler: kaynağın tuttuğu her şey okunur veya saklanır, hiçbir şey atılmaz. Satırların yanında, uyarlayıcının aldığı her paket, sayfa, satır veya yanıt oturumun `heat.raw.parquet` dosyasında bütün olarak saklanır (sütunlar `time`, `ms`, `type`, `used`, `payload`, `text` ve ada göre tutulan her alan; `used` satırlara da dönüşenleri işaretler). `meta.json` içindeki `selfCheck.completeness` her `type` değerini sayar; `lost` 0'dır.

**Okunan**

- her nesnenin T değeri (boylam, enlem, yükseklik, yalpa, yunuslama, yuvarlanma, U, V, yön) saniyede bir konum olarak, nesne başına; Name, Type, Pilot, Coalition/Color, Country, Group ve Parent ile
- doğuşlar, kaldırılmalar (önce bir Destroyed olayı geldiyse ölüm, yoksa sol), TakenOff ve Landed olayları, Message ve Bookmark olayları satır olarak
- genel değerler ReferenceLongitude/Latitude (haritanın başlangıcı), RecordingTime/ReferenceTime (ne zaman), DataSource, DataRecorder ve Title meta.json'a

**Ham olarak saklanan**

- boş olmayan her mantıksal satır bütün olarak `text` olarak, türü altında (ACMI'nin okuduğu gibi sondaki ters eğik çizgiyle devam eden satır birleştirilmiş): `header` (FileType, FileVersion), `comment`, `time` (#t), `remove` (-id), `global` ve `event` (nesne 0), `object` (id,Key=Value,...)
- yalnızca ham yan dosyanın tuttukları: saniyelik satırlar arasındaki konumlar, silahlar, mermiler, parlamalar, samanlar ve çizgi olarak çizilmeyen diğer nesneler, diğer her özellik (IAS, AOA, gaz, yakıt gibi telemetri, kayıtta varsa), diğer genel değerler (Comments, Briefing, Author, Category), okunanlar dışındaki olaylar (Timeout, LeftArea, ...)

**Mevcut olmayan**

- kayıtta bulunan her şey; oyunun kayıtlarına yazmadığı şey kayıtlarda yoktur

**Boyut**: kaydın kendi metni artı satır başına yaklaşık 70 bayt, sıkıştırmadan önce: 100 MB'lık bir kayıt, yaklaşık 150-250 MB ham veri yapar; zstd bunu zipli kaydın boyutuna yakın bir değere indirir

## Doğrulama {#verified}

sentetik ACMI 2.2 dosyalarında test edildi (metin ve zipli); oyunun bir kaydında test edilmedi

## Kaynak {#source}

[heat3d_watch/adapters/il2.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/il2.py)

<!-- Adaptörden tools/gen_game_pages.py ile üretilmiştir; sayfayı elle düzenlemek yerine adaptörü değiştirin ve yeniden çalıştırın. -->
