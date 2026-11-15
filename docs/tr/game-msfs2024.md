---
title: "Microsoft Flight Simulator 2024 (canlı veri)"
nav_order: 32
lang: "tr"
source: game-msfs2024.md
source_hash: "011c18a23252"
nav_exclude: true
search_exclude: true
---
# Microsoft Flight Simulator 2024 (canlı veri) {#microsoft-flight-simulator-2024-live-data}

Microsoft Flight Simulator 2024 oynarken izleyici, oyunun kendi gönderdiği veriyi kaydeder. Böylece bunlara daha sonra 3DHeat görüntüleyicisinde bir harita üzerinde bakabilirsiniz.

*Teknik ayrıntılar: adaptör `msfs2024`, tür [`telemetry`](sources-and-rules.md); `FlightSimulator2024.exe` çalışırken çalışır ve her 0.1 s'de bir yeni veri arar.*

## Neler kaydedilir {#what-is-recorded}

- kendi uçağının konumu her simülasyon karesinde, 10 Hz'de alınır (enlem/boylam/yükseklik, ilk tespitten itibaren metre cinsinden doğu/yukarı/kuzey; lat/lon/alt sütun olarak saklanır)
- tutum, gösterilen hava hızı, yer hızı, AGL, g, yerde olup olmadığı; yaklaşık 10 Hz'de gerçek hava hızı, Mach, dikey hız, AoA, kayma, manyetik baş, gövde hızları, ivmeler ve dönüş hızları
- ağırlık, yakıt, flaplar, iniş takımı, spoiler'lar, park freni, otopilot, gaz, RPM, hava durumu, simülasyon hızı, zaman ve kamera durumu saniyede bir; uçağın adı ve ATC tipi, modeli ve kimliği
- kalkışlar, inişler, kazalar, başlatılan ve durdurulan uçuşlar (session_start/session_end)
- uçuş süresi, havada kalma süresi, mesafe, en yüksek irtifa, en yüksek g, inişler
- her SimConnect iletisi, bütün olarak heat.raw.parquet içinde

## Nereden gelir {#where-it-comes-from}

SimConnect, oyuncunun kendi SimConnect.dll dosyası üzerinden (simülatörün klasörü ya da %MSFS2024_SDK%\SimConnect SDK\lib)

## Nasıl açılır {#how-to-switch-it-on}

simülatörde bir şey yok; SimConnect.dll gerekir - MSFS 2020 bunu kendi klasöründe taşır, MSFS 2024 oyuncuları MSFS 2024 SDK'sını kurar

## Nasıl çalışır {#how-it-works}

Microsoft Flight Simulator 2020 ve 2024: SimConnect, oyuncunun kendi SimConnect.dll dosyası üzerinden.

SimConnect, simülatörün yayımlanmış istemci API'sidir (SDK belgeleri:
<https://docs.flightsimulator.com/html/Programming_Tools/SimConnect/SimConnect_SDK.htm>,
<https://docs.flightsimulator.com/msfs2024/html/6_Programming_APIs/SimConnect/SimConnect_SDK.htm>).
İzleyici DLL'i kendisi taşımaz: simülatörle ya da onun SDK'sıyla gelen DLL'i yükler - MSFS 2020 `SimConnect.dll` dosyasını kendi kurulum klasörüne koyar; Steam'deki MSFS 2024 yalnızca kendi dahili sürümünü verir, bu yüzden 2024 oyuncuları MSFS 2024 SDK'sını kurar
(`<SDK>\SimConnect SDK\lib\SimConnect.dll`; 2024 simülatörü 2020 istemcilerini de kabul eder).

SimConnect.h'den çağrılar, hepsi bir HRESULT döndürür (0 = S_OK):

```text
SimConnect_Open(HANDLE*, LPCSTR name, HWND, DWORD, HANDLE, DWORD config)
SimConnect_AddToDataDefinition(HANDLE, DWORD define, LPCSTR var, LPCSTR units,
                               SIMCONNECT_DATATYPE (FLOAT64 = 4), float epsilon, DWORD datum)
SimConnect_RequestDataOnSimObject(HANDLE, DWORD request, DWORD define, DWORD object (0 = user),
                                  SIMCONNECT_PERIOD (SIM_FRAME = 3), DWORD flags, DWORD origin,
                                  DWORD interval, DWORD limit)
SimConnect_SubscribeToSystemEvent(HANDLE, DWORD event, LPCSTR name)
SimConnect_GetNextDispatch(HANDLE, SIMCONNECT_RECV**, DWORD*)   E_FAIL when nothing waits
SimConnect_Close(HANDLE)
```

Her ileti SIMCONNECT_RECV {DWORD dwSize, dwVersion, dwID} ile başlar
(#pragma pack 1). Burada okunanlar:

```text
1  EXCEPTION       dwException, dwSendID, dwIndex
2  OPEN            szApplicationName[256], then version DWORDs
3  QUIT            the sim is closing
4  EVENT           uGroupID, uEventID, dwData
6  EVENT_FILENAME  EVENT + szFileName[260], dwFlags        (FlightLoaded)
8  SIMOBJECT_DATA  dwRequestID, dwObjectID, dwDefineID, dwFlags, dwentrynumber,
                   dwoutof, dwDefineCount, then the values (FLOAT64 each here)
```

Simülasyon değişkenleri (dönüşüm gerekmemesi için istenen birimlerle): PLANE
LATITUDE/LONGITUDE (derece), PLANE ALTITUDE (metre, deniz seviyesinin üstünde), PLANE
ALT ABOVE GROUND (metre), PLANE PITCH/BANK DEGREES ve PLANE HEADING DEGREES
TRUE (derece; SimConnect'in kendi işaretleri - burnu yukarıda olmak negatif pitch demektir), AIRSPEED
INDICATED ve GROUND VELOCITY (knot), G FORCE (gforce), SIM ON GROUND (bool).
Sistem olayları: SimStart, SimStop, Crashed, FlightLoaded, AircraftLoaded,
Pause, CrashReset, PositionChanged, FlightSaved, Sim.

Uçuşun geri kalanını isteyen üç veri tanımı daha vardır (`MOTION_VARS`, her altıncı simülasyon karesinde), uçağın daha yavaş durumu (`STATE_VARS`, saniyede bir) ve adları (`NAME_VARS`, 256 baytlık metinler, değiştiklerinde); her biri kendi tanımıdır, bu yüzden bir simülatör sürümünün bilmediği bir değişken yalnızca o bloğa mal olur. Her ileti, oturumun ham yan dosyasında bütün olarak saklanır.

Konumlar, X-Plane'in kullandığı düz haritaya girer (x doğu, y irtifa, z kuzey, metre cinsinden, oturumun ilk tespitinden); o tespit, oturumun `geo` değeridir, meta.json ve tablonun altbilgisinde durur.

Aynı modül şunu da çalıştırır: [Microsoft Flight Simulator 2020 (canlı veri)](game-msfs2020.md).

## Konumlar ve eksenler {#positions-and-axes}

| | |
|---|---|
| Konumlar kaydedilir | evet |
| Yukarı eksen | `y` |
| Birimler | metre (doğu, irtifa, kuzey; ilk tespitten) |
| Görüntüleyici için aynalanır | `z` |
| Birim ölçeği (`scale`: görüntüleyici konumları bununla çarpar) | 1 |

Bunlar her oturumun `meta.json` dosyasına (`axes`) ve oturumda konum varsa `heat.parquet` dosyasının altbilgisine yazılır; böylece 3DHeat görüntüleyicisi satırları kendi başına döndürür ve ölçekler - bkz. [Veriler](the-data.md).

## Çok oyunculu {#multiplayer}

- Çevrimiçi oynanan olarak işaretli (`multiplayer`): **evet**. `games --markdown` bunu "allowed (reads only what the game publishes)" olarak gösterir.
- Tür `telemetry`: yalnızca oyunun ya da platformun verdiğini okur (oyunun yayımladığı bir UDP portu ya da paylaşılan bellek), bu yüzden çevrimiçi oyunda da, çevrimdışı olduğu gibi kaydeder; bayrak yalnızca belleğin hiç okunup okunamayacağını belirler.
- Bellek: bu adaptör **asla** okumaz. Yalnızca `memory` adaptörleri bellek okur ve çevrimiçi oynanan bir oyun için asla okumaz - bkz. [Kaynaklar ve kurallar](sources-and-rules.md).

## Kaydedilen istatistikler {#statistics-recorded}

Bu adaptörün kodunun adıyla ayarladığı istatistik anahtarları (her oturumun `meta.json` içindeki `stats` ve `watcher.sqlite` içindeki `stats` tablosu):

`airborne_time`, `bad_packets`, `crashes`, `distance_km`, `flight_time`, `max_altitude_m`, `max_g`, `{event}s`

Süslü parantez içindeki bir anahtar çalışma sırasında tamamlanır (`score.{team}` her takım için bir anahtardır). Kodun oyunun alan tablosundan ya da oyunun kendi istatistik adlarından aldığı anahtarlar bu listede yoktur; yukarıdaki "Neler kaydedilir" bölümü onları adlarıyla anar.

## Tamlık {#completeness}

İzleyici, 3DHeat'in [dönüştürücü kuralını](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md) izler: kaynağın tuttuğu okunur ya da saklanır, asla atılmaz. Satırların yanında, adaptörün aldığı her paket, sayfa, satır ya da yanıt, oturumun `heat.raw.parquet` dosyasında bütün olarak saklanır (sütunlar `time`, `ms`, `type`, `used`, `payload`, `text`, ardından adıyla saklanan her alan; `used` satırlara dönüşenleri işaretler). `meta.json` içindeki `selfCheck.completeness` her `type` değerini sayar - `lost` 0'dır.

**Okunanlar**

- konum tanımının SIMOBJECT_DATA'sı (her simülasyon karesinde): enlem, boylam, irtifa, AGL, pitch, bank, gerçek baş, IAS, yer hızı, g, yerde olup olmadığı - yoklamanın son karesi bir satır olarak, dokunuşlar ve kalkışlar için her kare
- hareket tanımının SIMOBJECT_DATA'sı (yaklaşık 10 Hz: TAS, Mach, dikey hız, AoA, kayma, manyetik baş, gövde hızı, üç eksende ivme ve dönüş hızı) ve durum tanımının (1 Hz: ağırlıklar, yakıt, flaplar, iniş takımı, spoiler'lar, park freni, otopilot, motorlar, gaz ve RPM, dış sıcaklık, rüzgâr, deniz seviyesi basıncı, simülasyon hızı, zulu ve yerel saat, kamera durumu) son alındığı gibi satırlara
- adlar tanımının SIMOBJECT_DATA'sı (ad, ATC tipi, model ve kimlik) meta.json'a ve satırların `aircraft` alanına; OPEN (uygulama ve sürüm) meta.json'a
- EVENT ve EVENT_FILENAME: SimStart, SimStop, Crashed, FlightLoaded (uçuş dosyası) ve AircraftLoaded (uçak dosyası), uçuşlar, kazalar ve meta.json olarak
- QUIT oturumu sonlandırır

**Ham olarak saklananlar**

- SimConnect'in izleyiciye verdiği her ileti, bütün olarak `payload` olarak, SIMCONNECT_RECV_ID adıyla: `SIMOBJECT_DATA`, `EVENT`, `EVENT_FILENAME`, `OPEN`, `QUIT`, `EXCEPTION` (simülatörün kabul etmediği bir değişken ya da olay, gönderim kimliği ve dizinle), başka her kimlik adıyla ya da `RECV_<id>` olarak
- yalnızca ham yan dosyanın tuttukları: satırlar arasındaki her simülasyon karesinin konumu, Pause, Sim, CrashReset, PositionChanged ve FlightSaved olayları, simülatörün kısaltığı bir tanım (bildiği olmayan bir değişken: o blok ada göre okunmaz); meta.json içindeki `requests` her tanımın değişkenlerini ve birimlerini sırasıyla listeler, böylece veriler bu modül olmadan okunabilir

**Mevcut değil**

- diğer uçaklar (yapay zekâ trafiği, çevrimiçi diğer oyuncular): SimConnect_RequestDataOnSimObjectType bir yarıçaptaki her uçağı yoklardı - simülatöre daha çok yük ve diğer oyuncuların uçuşları
- her simülasyon karesindeki hareket bloğu: her altıncı karede istenir (yaklaşık 10 Hz, satırların hızı), bu da ham akışı boyutunun beşte birine yakın tutar; konum bloğu her karede kalır
- simülasyonun binlerce diğer değişkeni (radyolar, ışıklar, her motorun göstergeleri, arızalar): bir tanım yalnızca istediğini tutar; listeler uçuşu, uçağın durumunu ve simülasyonun zamanını ister
- hava durumu gözlemleri, tesisler (havalimanları, VOR'lar), eklentilerin istemci verileri: ayrı istekler, yapılmaz

**Boyut**: zstd öncesi saatte yaklaşık 30-55 MB: her simülasyon karesindeki konum bloğu (çerçevesiyle yaklaşık 200 bayt, saniyede 30-60), yaklaşık 10 Hz'de hareket bloğu (yaklaşık 240 bayt), saniyede bir durum bloğu; zstd, çift duyarlıklı sayıları birkaç kat küçültür

## Doğrulama {#verified}

SimConnect.h'nin düzenlerinden oluşturulan arabelleklerle ileti çözme test edildi; canlı SimConnect bağlantısı test edilmedi

## Kaynak {#source}

[heat3d_watch/adapters/msfs.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/msfs.py)

<!-- Generated from the adapter by tools/gen_game_pages.py; change the adapter and run it again rather than editing this page. -->
