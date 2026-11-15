---
title: "IL-2 Sturmovik: Great Battles (canlı veri)"
nav_order: 26
lang: "tr"
source: game-il2.md
source_hash: "b6c4de7dcc14"
nav_exclude: true
search_exclude: true
---
# IL-2 Sturmovik: Great Battles (canlı veri) {#il-2-sturmovik-great-battles-live-data}

IL-2 Sturmovik: Great Battles oynarken izleyici, oyunun dışarıya gönderdiği verileri kaydeder; böylece bu verilere daha sonra istatistikler ve bir zaman çizelgesi olarak bakabilirsiniz.

*Teknik ayrıntılar: uyarlayıcı `il2`, tür [`telemetry`](sources-and-rules.md); `Il-2.exe` veya `IL2Series.exe` çalışırken çalışır ve her 0,1 saniyede bir yeni veri arar.*

## Ne kaydedilir {#what-is-recorded}

- uçuş görevleri: alınan uçak (doğuş) ve çıktının durduğu an (session_end) - oyun dünya konumu göndermediği için konum yoktur
- bırakılan bombalar ve fırlatılan roketler (kütle), alınan isabetler ve hasar, patlamalar, silah ateşleme patlamaları - uçağa göre yerel konumlar
- eşdeğer hava hızı, AGL, dikey hız, g, saniyede bir motor devri; paketin taşıdığı diğer bütün göstergelerle birlikte (manifold basıncı, motor titreşimi, vites durumu ve basıncı, AoA, kayma, ivme x/y/z, kokpit sarsıntısı, flaplar, hava frenleri)
- uçuş görevleri, ateşlenen mermi sayısı, bombalar, roketler, alınan isabetler, en yüksek hız, en yüksek g, uçuş süresi; çevrimiçi sunucu başlığı ve pilot adı
- her telemetri paketi heat.raw.parquet içinde bütün olarak

## Veri nereden gelir {#where-it-comes-from}

oyunun telemetri UDP çıktısı, 127.0.0.1:41995 (<oyun>\data\startup.cfg içinde [KEY = telemetrydevice])

## Nasıl açılır {#how-to-switch-it-on}

python -m heat3d_watch setup il2 --apply (addrN = "127.0.0.1:41995" ve enable = true ekler), ardından IL-2'yi yeniden başlatın

Komutu, izleyicinin klasöründe açılmış bir terminale yazın (bkz. [Başlamadan önce](before-you-start.md)). Başarısız olursa, son satır nedenini söyler; [Kurulum ve çalıştırma](installing-and-running.md) sık görülen nedenleri anlatır.

`python -m heat3d_watch setup il2` değiştirilecek dosyaları listeler; `python -m heat3d_watch setup il2 --apply` bunları değiştirir ve özgün dosyayı `<file>.heat3d-backup` adıyla saklar (bkz. [Komutlar](commands.md#setup)). Her değişiklik için `il2: changed: ...` yazar; zaten açıksa `il2: nothing to change` yazar.

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

Bu modül şunlara da hizmet eder: [IL-2 Sturmovik: Great Battles (tekrarlar)](game-il2-tacview.md).

## Konumlar ve eksenler {#positions-and-axes}

| | |
|---|---|
| Konumlar kaydedilir | hayır |
| Yukarı eksen | `y` |
| Birimler | yok: telemetride dünya konumu yoktur |
| Görüntüleyici için aynalama | yok |
| Birim ölçeği (`scale`: görüntüleyici konumları bununla çarpar) | 1 |

Bunlar her oturumun `meta.json` dosyasındaki (`axes`) ve oturumda konum varsa `heat.parquet` dosyasının altbilgisine yazılır; böylece 3DHeat görüntüleyicisi satırları kendi başına döndürür ve ölçekler. Bkz. [Veriler](the-data.md).

## Çok oyunculu {#multiplayer}

- Çevrimiçi oynanan olarak işaretli (`multiplayer`): **evet**. `games --markdown` bunu "izinli (yalnızca oyunun yayınladığını okur)" olarak gösterir.
- Tür `telemetry`: yalnızca oyunun veya platformun dışarı verdiğini okur (oyunun yayınladığı bir UDP portu veya paylaşılan bellek); bu yüzden çevrimiçi oyunda da kaydeder. Bayrak yalnızca belleğin hiç okunup okunamayacağını belirler.
- Bellek: bu uyarlayıcı **asla** okumaz. Yalnızca `memory` uyarlayıcıları bellek okur ve çevrimiçi oynanan olarak işaretli bir oyun için hiçbir zaman. Bkz. [Kaynaklar ve kurallar](sources-and-rules.md).

## Kaydedilen istatistikler {#statistics-recorded}

Bu uyarlayıcının kodunun ada göre ayarladığı istatistik anahtarları (her oturumun `meta.json` dosyasındaki `stats` ve `watcher.sqlite` dosyasındaki `stats` tablosu):

`bad_packets`, `bombs_dropped`, `damage_taken`, `explosions`, `flight_time`, `hits_taken`, `max_agl_m`, `max_eas_kmh`, `max_g`, `ordnance_kg`, `rockets_fired`, `rounds_fired`, `sorties`

Süslü parantez içindeki bir anahtar çalışma zamanında tamamlanır (`score.{team}` her takım için ayrı bir anahtardır). Kodun oyunun alan tablosundan veya oyunun kendi istatistik adlarından aldığı anahtarlar bu listede yer almaz; yukarıdaki "Ne kaydedilir" bölümü onları adlandırır.

## Tamlık {#completeness}

İzleyici 3DHeat'in [dönüştürücü kuralını](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md) izler: kaynağın tuttuğu her şey okunur veya saklanır, hiçbir şey atılmaz. Satırların yanında, uyarlayıcının aldığı her paket, sayfa, satır veya yanıt oturumun `heat.raw.parquet` dosyasında bütün olarak saklanır (sütunlar `time`, `ms`, `type`, `used`, `payload`, `text` ve ada göre tutulan her alan; `used` satırlara da dönüşenleri işaretler). `meta.json` içindeki `selfCheck.completeness` her `type` değerini sayar; `lost` 0'dır.

**Okunan**

- SET_FOCUS (alınan uçak: bir uçuş görevi), DROP_BOMB ve ROCKET_LAUNCH (kütle, yerel konum), HIT ve DAMAGE (yerel konum, kuvvet), EXPLOSION (yerel konum, yarıçap), GUN_FIRE (sorgu başına mermi) satır olarak
- SETUP_ENG (sıra, kimlik, yerel konum, en yüksek devir), SETUP_GUN (sıra, yerel konum, mermi kütlesi, namlu çıkış hızı) ve SETUP_LGEAR (sıra, kimlik, yerel konum) satır olarak: uçuş görevi başlarken uçağın motorları, silahları ve iniş takımı bacakları
- SRV_TITLE, SRV_ADDR, SRS_ADDR ve CLIENT_DAT (pilot adı) meta.json'a; CTRL_DAT'ın koalisyonu uçuş görevinin takımı olarak
- belirtimin on beş göstergesinin hepsi, saniyede bir `state` satırında (tek değer sayı olarak; her motor, iniş takımı bacağı veya eksen için liste olarak); her paketten en yüksek hız, g ve AGL

**Ham olarak saklanan**

- her datagram bütün olarak `payload` olarak, Packet_ID altında: telemetri için `0x54000101` (bir satır veya meta.json girdisi yaptığında kullanılır), diğer her kimlik kendi adıyla, bir nesne için çok kısa bir datagram `short`
- yalnızca ham yan dosyanın tuttukları: saniyelik satırlar arasındaki göstergeler (oyun 50 Hz / decimation hızında gönderir), belirtimdeki düzenden kısa bir SETUP olayı, belirtimin listelemediği olay kimlikleri

**Mevcut olmayan**

- dünya konumu: telemetri çıktısında yoktur (olay konumları uçağa göredir); il2-tacview uyarlayıcısı konumları oyunun kendi Tacview kayıtlarından okur
- diğer uçaklar ve oyuncular: çıktı yalnızca oyuncunun kendi uçağını tarif eder

**Boyut**: setup'ın 10 Hz'inde (decimation 5) saatte yaklaşık 8 MB (paket yaklaşık 160 bayt artı çerçevesi), oyunun tam 50 Hz hızında 40 MB, sıkıştırmadan önce; zstd tekrarlayan kayan noktalı sayıları küçük bir bölüme indirir

## Doğrulama {#verified}

oyunun kendi Il2_TeleOutput belirtimi (rev 1.2) üzerinden kurulan paketlerde test edildi; startup.cfg düzenlemeleri dosyanın bir kopyası üzerinde test edildi; çalışan oyunda test edilmedi

## Kaynak {#source}

[heat3d_watch/adapters/il2.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/il2.py)

<!-- Adaptörden tools/gen_game_pages.py ile üretilmiştir; sayfayı elle düzenlemek yerine adaptörü değiştirin ve yeniden çalıştırın. -->
