---
title: "War Thunder (oyun durumu)"
nav_order: 46
lang: "tr"
source: game-warthunder-webmap.md
source_hash: "34a876e38f09"
nav_exclude: true
search_exclude: true
---
# War Thunder (oyun durumu) {#war-thunder-game-state}

War Thunder oynarken izleyici, oyunun bildirdiklerini bilgisayarınızdaki programlara kaydeder. Böylece bunlara daha sonra 3DHeat görüntüleyicisinde bir harita üzerinde bakabilirsiniz.

*Teknik ayrıntılar: adaptör `warthunder-webmap`, tür [`gsi`](sources-and-rules.md); `aces.exe` çalışırken çalışır ve her 0.5 s'de bir yeni veri arar.*

## Neler kaydedilir {#what-is-recorded}

- kendi konumu (harita doğu/kuzey metre cinsinden; uçakta /state'ten yükseklik, yoksa 0), iki kez saniyede, baş, hız
- doğuşlar ve kendi aracın haritadan çıkışı (yok edildi, indi, hangara döndü), her biri bir sortie
- minimaptaki diğer uçaklar ve kara birimleri, izlenen kimlikler ve tarafla birlikte konumlar olarak (yükseklik yok)
- hava alanları, ele geçirme bölgeleri ve üsler bir kez, ve bölgelerin taraf değiştirmesi
- öldürme ve hasar akışı satırları (kim, araç, fiil); senin adın ayarlanmışsa oyuncunun öldürmeleri ve ölümleri (`config --set player_names.warthunder-webmap=<name>`)
- doğuşlar, mesafe, en yüksek irtifa, en yüksek gerçek hava hızı, araç; adın ayarlıysa öldürmeler ve ölümler
- web haritasının her yanıtı, bütün olarak heat.raw.parquet içinde - tam /state ve /indicators, sohbet, savaşın hedefleri ve haritanın resmi dahil; savaşlar arasında kendi oturumunda

## Nereden gelir {#where-it-comes-from}

oyunun yerel web haritası, <http://127.0.0.1:8111> (/map_info.json, /map_obj.json, /state, /indicators, /hudmsg, /gamechat, /mission.json, /map.img)

## Nasıl açılır {#how-to-switch-it-on}

Hiçbir şeyi açmanız gerekmez: izleyici kaynağı, oyunun ya da platformun sunduğu gibi okur.

## Nasıl çalışır {#how-it-works}

War Thunder: oyunun kendi yerel web haritası, <http://127.0.0.1:8111> üzerinde.

Oyun, ikinci bir ekranın ya da telefonun gösterebileceği sayfayı ("web haritası") ve onun arkasındaki JSON'u, çalıştığı sürece sunar - her modda, çok oyunculu olanlar dahil:

```text
/map_info.json   {"map_min": [x, y], "map_max": [x, y], "grid_steps", "grid_zero", "map_generation",
                  "hud_type", "valid"}: the map's extent in metres; valid false in the hangar
/map_obj.json    [{"type": aircraft|ground_model|airfield|capture_zone|bombing_point|defending_point|
                  respawn_base_*|..., "icon": Player|Fighter|Bomber|Mediumtank|SPAA|..., "color": "#rrggbb",
                  "x", "y" (0..1 of the map picture, y down), "dx", "dy" (direction),
                  airfields "sx", "sy", "ex", "ey"}]: what the minimap shows, the player's own
                  vehicle with icon "Player"; no ids, no heights
/state           {"valid", "H, m", "TAS, km/h", "IAS, km/h", "M", "Vy, m/s", ...}: flight values,
                  valid only in an aircraft
/indicators      {"valid", "army": air|tank|..., "type": the vehicle}
/hudmsg?lastEvt=N&lastDmg=M   {"events": [...], "damage": [...]} newer than the ids given, each
                  {"id", "msg", "sender", "enemy", "mode", "time"}; damage lines read like
                  "Name (Vehicle) shot down Name (Vehicle)"
/gamechat?lastId=N  the chat newer than the id given, [{"id", "msg", "sender", "enemy", "mode", "time"}]
/mission.json    the battle's objectives and their status
/map.img         the map's picture the page draws the objects on
```

Her yanıt, oturumun ham yan dosyasında, uç noktasının adıyla bütün olarak saklanır (map_info, map_obj, state, indicators, hudmsg, gamechat, mission, map_img);
savaşlar arasında yanıtlar kendi oturumlarına gider.

Bir harita konumu, uzantıyla metreye çevrilir: u = min_x + x \* (max_x - min_x)
doğu, v = max_y - y \* (max_y - min_y) kuzey (resmin y'si aşağı doğru gider). Satırlar
x = u, y = yükseklik (kendi uçağın "H, m"; diğer her şey için 0), z = v, böylece
Y yukarıdır; z görüntüleyici için aynalanır, böylece kuzey güney gibi çizilmez.

Renkler, tarafları oyuncunun gördüğü gibi gösterir: kendi sarısı (varsayılan #faC81E), squad yeşili, müttefikler mavi (#174DFF), düşmanlar kırmızı (#f40C00); renk körü paletleri onları değiştirir, bu yüzden kesin değer değil, ton belirleyicidir. Oyun haritadaki kimseyi adlandırmaz ve nesnelere kimlik vermez: diğer nesneler, her yoklamadan diğerine izlenerek burada kimlik alır (aynı türdeki ve simgedeki en yakın olan), bu da yakından geçen iki uçağın yerini değiştirebilir. Oyuncunun kendi adı API'de de yoktur: ayarlarda verin (`config --set player_names.warthunder-webmap=<your name>`) ve oyuncu hakkındaki öldürme akışı satırları öldürme ve ölüm olur; yoksa öldürme akışı olarak kaydedilir.

Kaynaklar: oyunun kendi sayfası <http://127.0.0.1:8111> ve JSON'u; alan bilgileri JoyPro 2 projesinin belgelediği gibi (docs/telemetry-recording.md; GPL, yalnızca bilgi için kullanıldı).

## Konumlar ve eksenler {#positions-and-axes}

| | |
|---|---|
| Konumlar kaydedilir | evet |
| Yukarı eksen | `y` |
| Birimler | metre (harita doğu/kuzey; yükseklik yalnızca kendi uçak için) |
| Görüntüleyici için aynalanır | `z` |
| Birim ölçeği (`scale`: görüntüleyici konumları bununla çarpar) | 1 |

Bunlar her oturumun `meta.json` dosyasına (`axes`) ve oturumda konum varsa `heat.parquet` dosyasının altbilgisine yazılır; böylece 3DHeat görüntüleyicisi satırları kendi başına döndürür ve ölçekler - bkz. [Veriler](the-data.md).

## Çok oyunculu {#multiplayer}

- Çevrimiçi oynanan olarak işaretli (`multiplayer`): **evet**. `games --markdown` bunu "allowed (reads only what the game publishes)" olarak gösterir.
- Tür `gsi`: yalnızca oyunun ya da platformun verdiğini okur (oyunun sunduğu bir oyun durumu entegrasyonu ya da yerel API), bu yüzden çevrimiçi oyunda da, çevrimdışı olduğu gibi kaydeder; bayrak yalnızca belleğin hiç okunup okunamayacağını belirler.
- Bellek: bu adaptör **asla** okumaz. Yalnızca `memory` adaptörleri bellek okur ve çevrimiçi oynanan bir oyun için asla okumaz - bkz. [Kaynaklar ve kurallar](sources-and-rules.md).

## Kaydedilen istatistikler {#statistics-recorded}

Bu adaptörün kodunun adıyla ayarladığı istatistik anahtarları (her oturumun `meta.json` içindeki `stats` ve `watcher.sqlite` içindeki `stats` tablosu):

`bad_packets`, `deaths`, `distance_m`, `hits_dealt`, `hits_taken`, `kills`, `max_altitude_m`, `max_tas_kmh`, `spawns`, `vehicle`

Süslü parantez içindeki bir anahtar çalışma sırasında tamamlanır (`score.{team}` her takım için bir anahtardır). Kodun oyunun alan tablosundan ya da oyunun kendi istatistik adlarından aldığı anahtarlar bu listede yoktur; yukarıdaki "Neler kaydedilir" bölümü onları adlarıyla anar.

## Tamlık {#completeness}

İzleyici, 3DHeat'in [dönüştürücü kuralını](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md) izler: kaynağın tuttuğu okunur ya da saklanır, asla atılmaz. Satırların yanında, adaptörün aldığı her paket, sayfa, satır ya da yanıt, oturumun `heat.raw.parquet` dosyasında bütün olarak saklanır (sütunlar `time`, `ms`, `type`, `used`, `payload`, `text`, ardından adıyla saklanan her alan; `used` satırlara dönüşenleri işaretler). `meta.json` içindeki `selfCheck.completeness` her `type` değerini sayar - `lost` 0'dır.

**Okunanlar**

- /map_info.json: haritanın kapsamı ve ızgarası (metre, harita kimliği) meta.json'a; geçersiz olanı savaşı bitirir
- /map_obj.json (saniyede iki kez): kendi aracınız, diğer uçaklar ve kara birimleri (izlenen kimlikler, renkten taraf, simge, yön, renk) ve hava alanları, bölgeler ve üsler satır olarak
- /state (saniyede iki kez, bir uçakta): kendi satırlarınızda yükseklik, TAS, IAS, Mach ve Vy
- /indicators (her 2 s'de bir): ordu ve araç tipi
- /hudmsg (saniyede bir): öldürme ve hasar akışı satırları, öldürme, ölüm, isabet ve akış satırları olarak; diğer HUD olayları satır olarak

**Ham olarak saklananlar**

- her yanıt bütün olarak, `text` oyunun gönderdiği JSON, uç noktasının adıyla: `map_info`, `map_obj`, `state`, `indicators`, `hudmsg`, `gamechat`, `mission`; `map_img` bir savaşta bir kez, harita resminin baytları `payload` olarak
- yalnızca ham yan dosyanın tuttukları: okunan beşin ötesindeki her /state alanı (AoA, AoS, Ny, Wx, gaz, RPM, yakıt, ... - bir uçaktan diğerine değişir), her /indicators alanı (uçakların kokpit göstergeleri, tankların hızı, vitesi, mürettebatı ve stabilizatörü), harita nesnelerinin diğer anahtarları (color[], blink, icon_bg, airfield ends), hudmsg'nin sender, enemy ve mode alanları, sohbet (/gamechat, saniyede bir), savaşın hedefleri ve durumları (/mission.json, bir savaşta her 10 s'de bir), izleyici başlamadan önce söylenen satırlar
- savaşlar arasında (hangar, yükleme) yanıtlar, meta.json'da `between_battles` ile işaretli, satırı olmayan kendi oturumuna gider

**Mevcut değil**

- diğer oyuncuların araçlarının adları, kimlikleri ve yükseklikleri: web haritasında yoktur (kimlikler burada nesneleri yoklamadan yoklamaya izleyerek verilir); öldürme akışı oyuncuları konumsuz adlandırır
- web haritasının dışındaki her şey: oyunun tekrarları War Thunder tekrar dönüştürücüsü tarafından okunur, oyunun belleği hiç okunmaz (çevrimiçi bir oyun)
- /map_obj.json'un saniyede ikiden sık okunması: yoklama hızı düşük tutulur, böylece oyunun kendi web sunucusu yüklenmez

**Boyut**: bir savaşta zstd öncesi saatte yaklaşık 50-120 MB JSON (map_obj 5-15 KB, saniyede iki kez; state yaklaşık 1.5 KB, saniyede iki kez; indicators her 2 s'de bir; sohbet ve HUD satırları küçük), bir savaşta bir kez harita resmi (2 MB'ın altında); savaşlar arasında saatte 1-2 MB (harita görünümü saniyede iki kez, HUD ve sohbet bir kez, her biri kısa bir yanıt); zstd tekrarlanan JSON'u on kattan fazla küçültür

## Doğrulama {#verified}

oyunun web haritasının biçiminde yanıtlar veren sahte bir yerel sunucuya karşı test edildi; çalışan oyunla test edilmedi

## Kaynak {#source}

[heat3d_watch/adapters/warthunder.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/warthunder.py)

<!-- Generated from the adapter by tools/gen_game_pages.py; change the adapter and run it again rather than editing this page. -->
