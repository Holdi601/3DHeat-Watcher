---
title: "EA SPORTS F1 23 (canlı veri)"
nav_order: 14
lang: "tr"
source: game-f1-23.md
source_hash: "d7b523188e51"
nav_exclude: true
search_exclude: true
---
# EA SPORTS F1 23 (canlı veri) {#ea-sports-f1-23-live-data}

EA SPORTS F1 23 oynarken izleyici, oyunun kendi gönderdiği veriyi kaydeder. Böylece bunlara daha sonra 3DHeat görüntüleyicisinde bir harita üzerinde bakabilirsiniz.

*Teknik ayrıntılar: adaptör `f1-23`, tür [`telemetry`](sources-and-rules.md); `F1_23.exe` çalışırken çalışır ve her 0.1 s'de bir yeni veri arar.*

## Neler kaydedilir {#what-is-recorded}

- her arabanın konumu (dünya XYZ, m) 10 Hz'de, sürücü adına, takıma ve kendi arabanın işaretiyle (`own_car` 1, oyuncunun araba dizininden), hız, vites, gaz, fren, direksiyon, rpm, DRS, yaw, pitch, roll (derece) ve g kuvvetleriyle
- her arabanın turları, tur süresi ve yarış sırasıyla; bitirişler ve çekilmeler
- oyunun yarış olayları: oturumun başlangıcı ve sonu, en hızlı tur, cezalar, geçişler, çarpışmalar, güvenlik aracı, kırmızı bayrak, başlangıç ışıkları, damalı bayrak, kazanan, geriye sarmalar (`teleport` arabanın nerede olduğu, `spawn` geri döndüğü yer)
- her oturumun pistı, oturum türü, tur sayısı ve sürücüleri
- kendi turlarınız, en iyi tur, yarış ve başlangıç sırası, pit stop'lar, cezalar, geçişler, çarpışmalar, mesafe, en yüksek hız
- oyunun gönderdiği her paket, bütün olarak, `heat.raw.parquet` içinde - satırlara okunmayanlar da dahil

## Nereden gelir {#where-it-comes-from}

UDP telemetrisi 127.0.0.1:20777 (Documents\My Games\F1 23\hardwaresettings\hardware_settings_config.xml)

## Nasıl açılır {#how-to-switch-it-on}

Oyunda: Ayarlar > Telemetri Ayarları > UDP Telemetrisi Açık, IP 127.0.0.1, port 20777 - ya da `python -m heat3d_watch setup f1-23 --apply` (hardware_settings_config.xml dosyasını düzenler, önce yedeğini alır; oyun kapalı olmalı). Başka bir uygulama 20777'yi tutuyorsa izleyici portu ona bırakır

Komutu, izleyicinin klasöründe açılmış bir terminale yazın (bkz. [Başlamadan önce](before-you-start.md)). Başarısız olursa son satır nedenini söyler; [Kurulum ve çalıştırma](installing-and-running.md) sık görülen nedenleri anlatır.

`python -m heat3d_watch setup f1-23` hangi dosyaları değiştireceğini listeler; `python -m heat3d_watch setup f1-23 --apply` bunları değiştirir ve özgün dosyayı `<file>.heat3d-backup` adıyla saklar (bkz. [Komutlar](commands.md#setup)). Her değişiklik için `f1-23: changed: ...` yazar, zaten açıksa `f1-23: nothing to change` yazar.

## Nasıl çalışır {#how-it-works}

EA SPORTS F1 23, F1 24 ve F1 25: resmi UDP telemetrisi, pistteki her araba.

Oyunların kendisi gönderir (Ayarlar > Telemetri Ayarları ya da
`Documents/My Games/<F1 xx>/hardwaresettings/hardware_settings_config.xml`,
`<udp enabled="true" ip="127.0.0.1" port="20777" sendRate="20" format="2025" ...>`).
Little-endian, paketlenmiş, her pakette 29 baytlık bir başlık (2023, 2024 ve 2025 biçimlerinde aynı):

```text
uint16 packetFormat, uint8 gameYear, gameMajorVersion, gameMinorVersion,
packetVersion, packetId, uint64 sessionUID, float sessionTime,
uint32 frameIdentifier, overallFrameIdentifier, uint8 playerCarIndex,
secondaryPlayerCarIndex
```

Paket kimliğine göre okunanlar:

```text
0 Motion        CarMotionData[22], 60 bytes each: world position x y z
                (metres; Y is up), world velocity, forward and right
                vectors (int16 / 32767), g-forces, yaw pitch roll
1 Session       weather, temperatures, total laps, track length, session
                type, track id, ... network game
2 Lap Data      LapData[22]: last lap time, lap distance, race position,
                current lap number, pit stops, penalties, grid position,
                driver and result status. 50 bytes per car in 2023; 57 in
                2024 and 2025, which added the minutes parts of the deltas
                and the speed trap.
3 Event         a four-letter code and a union of details: SSTA SEND FTLP
                RTMT DRSE DRSD TMPT CHQF RCWN PENA SPTP STLG LGOT DTSV SGSV
                FLBK BUTN RDFL OVTK SCAR COLL
4 Participants  ParticipantData[22]: AI or human, driver, team, race
                number, name (48 bytes in 2023 and 2024, 32 in 2025; 58,
                60 and 57 bytes per car)
6 Car Telemetry CarTelemetryData[22], 60 bytes: speed km/h, throttle,
                steer, brake, clutch, gear, rpm, DRS ...
```

Her paket de, geldiği gibi, oturumun ham yan dosyasında bütün olarak saklanır (`heat.raw.parquet`, `type` paketin adı - `motion`, `car_status` ... -
`format`, `packet_id`, `frame` ve `session_uid` ile) - yukarıda okunanlar ve henüz hiçbir şeyin okumadığı olanlar: 5 Car Setups, 7 Car Status, 8 Final Classification, 9 Lobby
Info, 10 Car Damage, 11 Session History, 12 Tyre Sets, 13 Motion Ex, 14 Time
Trial, 15 Lap Positions, sonraki her kimlik ve bu biçimi okumayan bir biçimdeki paketler. Böylece sonraki bir çözücü yalnızca yan dosyaya ihtiyaç duyar.

Her arabanın konumu Motion paketindedir - çevrimiçi de, oyun bunu kendisi verdiği yerde (yalnızca yakıt, ERS, hasar ve lastik seti verileri "Your Telemetry" kısıtlı oyuncular için saklanır). Her araba, sürücü adı altında yaklaşık 10 Hz'de kaydedilir ("car N" adlar gelene kadar), takım adıyla ve oyuncunun kendi arabası `own` işaretiyle.

Kaynaklar: EA'nın "F1 25 UDP Specification" belgesi (forums.ea.com, F1 games info hub),
F1 23 ve F1 24 belgeleri; aynı tablolar MacManley/f1-25-udp'de yansıtılmıştır (MIT). Testlerdeki paketler bu düzenlerden oluşturulur.

Aynı modül şunları da çalıştırır: [EA SPORTS F1 24 (canlı veri)](game-f1-24.md), [EA SPORTS F1 25 (canlı veri)](game-f1-25.md).

## Konumlar ve eksenler {#positions-and-axes}

| | |
|---|---|
| Konumlar kaydedilir | evet |
| Yukarı eksen | `y` |
| Birimler | metre |
| Görüntüleyici için aynalanır | yok |
| Birim ölçeği (`scale`: görüntüleyici konumları bununla çarpar) | 1 |

Bunlar her oturumun `meta.json` dosyasına (`axes`) ve oturumda konum varsa `heat.parquet` dosyasının altbilgisine yazılır; böylece 3DHeat görüntüleyicisi satırları kendi başına döndürür ve ölçekler - bkz. [Veriler](the-data.md).

## Çok oyunculu {#multiplayer}

- Çevrimiçi oynanan olarak işaretli (`multiplayer`): **evet**. `games --markdown` bunu "allowed (reads only what the game publishes)" olarak gösterir.
- Tür `telemetry`: yalnızca oyunun ya da platformun verdiğini okur (oyunun yayımladığı bir UDP portu ya da paylaşılan bellek), bu yüzden çevrimiçi oyunda da, çevrimdışı olduğu gibi kaydeder; bayrak yalnızca belleğin hiç okunup okunamayacağını belirler.
- Bellek: bu adaptör **asla** okumaz. Yalnızca `memory` adaptörleri bellek okur ve çevrimiçi oynanan bir oyun için asla okumaz - bkz. [Kaynaklar ve kurallar](sources-and-rules.md).

## Kaydedilen istatistikler {#statistics-recorded}

Bu adaptörün kodunun adıyla ayarladığı istatistik anahtarları (her oturumun `meta.json` içindeki `stats` ve `watcher.sqlite` içindeki `stats` tablosu):

`best_lap`, `collisions`, `distance_km`, `fastest_laps`, `finishes`, `flashbacks`, `grid_position`, `laps`, `overtaken`, `overtakes`, `penalties`, `penalty_seconds`, `pit_stops`, `race_position`, `sessions`, `top_speed_kmh`, `wins`

Süslü parantez içindeki bir anahtar çalışma sırasında tamamlanır (`score.{team}` her takım için bir anahtardır). Kodun oyunun alan tablosundan ya da oyunun kendi istatistik adlarından aldığı anahtarlar bu listede yoktur; yukarıdaki "Neler kaydedilir" bölümü onları adlarıyla anar.

## Tamlık {#completeness}

İzleyici, 3DHeat'in [dönüştürücü kuralını](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md) izler: kaynağın tuttuğu okunur ya da saklanır, asla atılmaz. Satırların yanında, adaptörün aldığı her paket, sayfa, satır ya da yanıt, oturumun `heat.raw.parquet` dosyasında bütün olarak saklanır (sütunlar `time`, `ms`, `type`, `used`, `payload`, `text`, ardından adıyla saklanan her alan; `used` satırlara dönüşenleri işaretler). `meta.json` içindeki `selfCheck.completeness` her `type` değerini sayar - `lost` 0'dır.

**Okunanlar**

- 0 Motion: her arabanın dünya konumu ve hızı; şimdi yaw, pitch, roll (derece, belgedeki radyanlardan) ve yanal, boylamsal ve dikey g kuvveti de, her arabanın konum satırlarında
- 1 Session: pist, oturum türü, toplam tur, pist uzunluğu, çevrimiçi olup olmadığı (meta.json `sessions`)
- 2 Lap Data: son tur süresi, tur numarası, yarış ve başlangıç sırası, pit stop'lar, cezalar, sonuç durumu (turlar, bitirişler, çekilmeler, istatistikler)
- 3 Event: BUTN dışındaki her kod, ayrıntılarıyla kendi satırı olarak
- 4 Participants: sürücü adları, takımlar, etkin araba sayısı (satırların `player` ve `team` alanları, meta.json `drivers`)
- 6 Car Telemetry: hız, vites, gaz, fren ve şimdi direksiyon (-1..1), rpm ve DRS de, her arabanın konum satırlarında
- EA'nın yayımlanmış UDP belgelerine, 2023, 2024 ve 2025 biçimleri için karşı kontrol edildi (paket boyutları testlerde doğrulanır); henüz oyunla karşılaştırılmadı

**Ham olarak saklananlar**

- her paket, bütün olarak `heat.raw.parquet` içinde, `payload` datagram, `type` kimliğinin adı: `motion`, `session`, `lap_data`, `event`, `participants`, `car_setups`, `car_telemetry`, `car_status`, `final_classification`, `lobby_info`, `car_damage`, `session_history`, `tyre_sets`, `motion_ex`, `time_trial`, `lap_positions` (belgelerin henüz listelemediği bir kimlik için `packet <n>`); sütunlar `format` (2023/2024/2025), `packet_id`, `frame`, `session_uid`
- `used` yukarıda okunan paketler için doğrudur (Motion, Session, Lap Data, Participants, Car Telemetry ve BUTN dışındaki Event kodları); geri kalanlar - araba kurulumları, araba durumu (yakıt, ERS, lastik bileşiği ve yaşı, bayraklar), son sınıflandırma, lobi, araba hasarı, oturum geçmişi (her arabanın her tur ve sektör süresi), lastik setleri, motion ex (kendi arabanın süspansiyonu, tekerlek hızları, yerel hız, açısal hız ve ivme), zaman denemesi, tur konumları, BUTN düğme olayları - sonraki bir çözücü için saklanır
- `format <year>`: 2023'ten önceki bir biçimde paket (başka bir başlık düzeni), bütün olarak; `short`: 29 baytlık başlıktan kısa bir datagram, bütün olarak

**Mevcut değil**

- çevrimiçi "Your Telemetry" kısıtlı olan diğer oyuncuların yakıtı, ERS'si, hasarı ve lastik setleri: oyun onlar için sıfır gönderir
- izleyici çalışmıyorken ya da başka bir uygulama 20777 portunu tutarken gönderilen paketler: UDP'yi oyun saklamaz

**Boyut**: 60 Hz gönderme hızında her paket yaklaşık 0.38 MB/s (Motion, Lap Data, Car Telemetry, Car Status ve Motion Ex 60 Hz'de, Session History ve Tyre Sets saniyede 20, Car Damage saniyede 10, Session ve Car Setups saniyede 2) artı yaklaşık 0.03 MB/s öğe başlığı: sıkıştırılmadan sürüş saati başına yaklaşık 1.5 GB, varsayılan 20 Hz'de yaklaşık 0.55 GB; zstd bunu küçük bir kesire indirir (boş araba yuvaları ve tekrarlanan değerler iyi sıkışır; gerçek bir oturumda henüz ölçülmedi)

## Doğrulama {#verified}

EA'nın yayımlanmış belgesinden oluşturulan 2023, 2024 ve 2025 biçimlerindeki paketlerle, UDP üzerinden gönderilerek test edildi; oyunla test edilmedi

## Kaynak {#source}

[heat3d_watch/adapters/f1.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/f1.py)

<!-- Generated from the adapter by tools/gen_game_pages.py; change the adapter and run it again rather than editing this page. -->
