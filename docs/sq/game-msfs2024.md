---
title: "Microsoft Flight Simulator 2024 (të dhëna të drejtpërdrejta)"
nav_order: 32
lang: "sq"
source: game-msfs2024.md
source_hash: "011c18a23252"
nav_exclude: true
search_exclude: true
---
# Microsoft Flight Simulator 2024 (të dhëna të drejtpërdrejta) {#microsoft-flight-simulator-2024-live-data}

Ndërsa luan Microsoft Flight Simulator 2024, watcher-i ruan të dhënat që dërgon vetë loja, që më vonë t'i shohësh në një hartë në shikuesin 3DHeat.

*Detaje teknike: adapteri `msfs2024`, lloji [`telemetry`](sources-and-rules.md); ekzekutohet sa kohë `FlightSimulator2024.exe` është në punë dhe kërkon të dhëna të reja çdo 0.1 s.*

## Çfarë regjistrohet {#what-is-recorded}

- pozicioni i avionit tënd në çdo kuadër të simulimit, marrë në 10 Hz (gjerësia/gjatësia gjeografike/lartësia si metra lindje/lart/veri nga pozicioni i parë; lat/lon/alt të ruajtura si kolona)
- qëndrimi, shpejtësia e treguar, shpejtësia mbi tokë, AGL, g, në tokë; shpejtësia e vërtetë, Mach, shpejtësia vertikale, AoA, rrëshqitja anësore, drejtimi magnetik, shpejtësitë e trupit, përshpejtimet dhe shpejtësitë e rrotullimit në rreth 10 Hz
- pesha, karburanti, flapat, ingranazhi, spoilerat, frena e parkimit, autopiloti, gazi, RPM, moti, shpejtësia e simulimit, ora dhe gjendja e kamerës një herë në sekondë; titulli i avionit dhe lloji, modeli dhe id-ja ATC
- ngritjet, uljet, përplasjet, fluturimet e nisura dhe të ndaluara (session_start/session_end)
- koha e fluturimit, koha në ajër, largësia, lartësia më e madhe, g më i madh, uljet
- çdo mesazh SimConnect i ruajtur i plotë në heat.raw.parquet

## Nga vjen {#where-it-comes-from}

SimConnect përmes SimConnect.dll të vetë lojtarit (dosja e simulatorit, ose %MSFS2024_SDK%\SimConnect SDK\lib)

## Si aktivizohet {#how-to-switch-it-on}

asgjë në simulator; i duhet SimConnect.dll - MSFS 2020 e ka në dosjen e vet, lojtarët e MSFS 2024 instalojnë MSFS 2024 SDK

## Si funksionon {#how-it-works}

Microsoft Flight Simulator 2020 dhe 2024: SimConnect, përmes SimConnect.dll të vetë lojtarit.

SimConnect është API-ja e klientit e publikuar e simulatorit (dokumentacioni i SDK:
<https://docs.flightsimulator.com/html/Programming_Tools/SimConnect/SimConnect_SDK.htm>,
<https://docs.flightsimulator.com/msfs2024/html/6_Programming_APIs/SimConnect/SimConnect_SDK.htm>).
Watcher-i nuk e shpërndan DLL-në: ngarkon atë që erdhi me simulatorin ose
SDK-në e tij - MSFS 2020 e vendos `SimConnect.dll` në dosjen e instalimit; MSFS 2024 në
Steam sjell vetëm atë të brendshmen, ndaj lojtarët e 2024 instalojnë MSFS 2024 SDK
(`<SDK>\SimConnect SDK\lib\SimConnect.dll`; simulatori 2024 pranon edhe klientë të 2020).

Thirrjet, nga SimConnect.h, të gjitha kthejnë një HRESULT (0 = S_OK):

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

Çdo mesazh fillon me SIMCONNECT_RECV {DWORD dwSize, dwVersion, dwID}
(#pragma pack 1). Ata që lexohen këtu:

```text
1  EXCEPTION       dwException, dwSendID, dwIndex
2  OPEN            szApplicationName[256], then version DWORDs
3  QUIT            the sim is closing
4  EVENT           uGroupID, uEventID, dwData
6  EVENT_FILENAME  EVENT + szFileName[260], dwFlags        (FlightLoaded)
8  SIMOBJECT_DATA  dwRequestID, dwObjectID, dwDefineID, dwFlags, dwentrynumber,
                   dwoutof, dwDefineCount, then the values (FLOAT64 each here)
```

Variablat e simulimit (njësitë janë kërkuar që të mos duhet konvertim): PLANE
LATITUDE/LONGITUDE (gradë), PLANE ALTITUDE (metra, mbi nivelin e detit), PLANE
ALT ABOVE GROUND (metra), PLANE PITCH/BANK DEGREES dhe PLANE HEADING DEGREES
TRUE (gradë; shenjat e vetë SimConnect - hundë lart është pitch negativ), AIRSPEED
INDICATED dhe GROUND VELOCITY (nyje), G FORCE (gforce), SIM ON GROUND (bool).
Ngjarjet e sistemit: SimStart, SimStop, Crashed, FlightLoaded, AircraftLoaded,
Pause, CrashReset, PositionChanged, FlightSaved, Sim.

Tri përkufizime të tjera të dhënash kërkojnë pjesën tjetër të fluturimit (`MOTION_VARS`,
çdo kuadër të gjashtë të simulimit), gjendjen më të ngadaltë të avionit (`STATE_VARS`, një herë në
sekondë) dhe emrat e tij (`NAME_VARS`, vargje 256 bajtësh, kur ndryshojnë); secili
është përkufizim më vete, ndaj një variabël që një version simulatori nuk e njeh kushton
vetëm atë bllok. Çdo mesazh ruhet i plotë në skedarin raw anësor të seancës.

Pozicionet shkojnë në të njëjtën hartë të sheshtë si ato të X-Plane (x lindje, y lartësia, z veri
në metra nga pozicioni i parë i ulëses); ai pozicion është `geo` e seancës, në
meta.json dhe në fundin e tabelës.

I njëjti modul shërben edhe: [Microsoft Flight Simulator 2020 (të dhëna të drejtpërdrejta)](game-msfs2020.md).

## Pozicionet dhe boshtet {#positions-and-axes}

| | |
|---|---|
| Pozicionet regjistrohen | po |
| Boshti lart | `y` |
| Njësitë | metra (lindje, lartësi, veri nga pozicioni i parë) |
| Pasqyruar për shikuesin | `z` |
| Shkalla e njësisë (`scale`: shikuesi i shumëzon pozicionet me të) | 1 |

Këto shkojnë në `meta.json` të çdo seance (`axes`) dhe, kur seanca ka pozicione, në fundin e `heat.parquet`, që shikuesi 3DHeat t'i rrotullojë dhe shkallëzojë rreshtat vetë - shih [Të dhënat](the-data.md).

## Lojë me shumë lojtarë {#multiplayer}

- Shënuar si luajtur online (`multiplayer`): **po**. `games --markdown` e shfaq këtë si "allowed (reads only what the game publishes)".
- Lloji `telemetry`: lexon vetëm çfarë jep loja ose platforma (një port UDP ose memorie e përbashkët që e boton loja), ndaj regjistron edhe në lojë online edhe offline; flamuri vendos vetëm nëse mund të lexohet ndonjëherë memoria.
- Memoria: **kurrë** nuk lexohet nga ky adapter. Vetëm adapterat `memory` lexojnë memorie, dhe kurrë për një lojë të shënuar si e luajtur online - shih [Burimet dhe rregullat](sources-and-rules.md).

## Statistikat e regjistruara {#statistics-recorded}

Çelësat e statistikave që kodi i këtij adapteri i vendos me emër (`stats` e çdo seance në `meta.json` dhe tabela `stats` e `watcher.sqlite`):

`airborne_time`, `bad_packets`, `crashes`, `distance_km`, `flight_time`, `max_altitude_m`, `max_g`, `{event}s`

Një çelës në kllapa gjarpëruese plotësohet gjatë ekzekutimit (`score.{team}` është një çelës për çdo ekip). Çelësat që kodi i merr nga një tabelë fushash të lojës ose nga emrat e statistikave të vetë lojës nuk janë në këtë listë; "Çfarë regjistrohet" më sipër i emërton.

## Plotësia {#completeness}

Watcher-i ndjek [rregullin e konvertuesve](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md) të 3DHeat: çfarë mban burimi lexohet ose ruhet, nuk hidhet kurrë. Përveç rreshtave, çdo paketë, faqe, rresht ose përgjigje që merr adapteri ruhet e plotë në `heat.raw.parquet` të seancës (kolonat `time`, `ms`, `type`, `used`, `payload`, `text`, pastaj çdo fushë e mbajtur me emër; `used` shënon çfarë u bë edhe rresht), dhe `selfCheck.completeness` i `meta.json` numëron çdo `type` - `lost` është 0.

**Lexohet**

- SIMOBJECT_DATA e përkufizimit të pozicionit (çdo kuadër simulimi): gjerësia, gjatësia, lartësia, AGL, pitch, bank, drejtimi i vërtetë, IAS, shpejtësia mbi tokë, g, në tokë - kuadri i fundit i pyetjes si rresht, çdo kuadër për uljet dhe ngritjet
- SIMOBJECT_DATA e përkufizimit të lëvizjes (rreth 10 Hz: TAS, Mach, shpejtësia vertikale, AoA, rrëshqitja anësore, drejtimi magnetik, shpejtësia e trupit, përshpejtimi dhe shpejtësia e rrotullimit në tri boshte) dhe e përkufizimit të gjendjes (1 Hz: peshat, karburanti, flapat, ingranazhi, spoilerat, frena e parkimit, autopiloti, motorët, gazi dhe RPM, temperatura e jashtme, era, presioni në nivelin e detit, shpejtësia e simulimit, ora zulu dhe vendore, gjendja e kamerës) mbi rreshta siç u morën së fundi
- SIMOBJECT_DATA e përkufizimit të emrave (titulli, lloji ATC, modeli dhe id-ja) në meta.json dhe `aircraft` të rreshtave; OPEN (aplikacioni dhe versioni) në meta.json
- EVENT dhe EVENT_FILENAME: SimStart, SimStop, Crashed, FlightLoaded (skedari i fluturimit) dhe AircraftLoaded (skedari i avionit) si fluturime, përplasje dhe meta.json
- QUIT e mbyll seancën

**Ruhet i papërpunuar**

- çdo mesazh që i jep SimConnect watcher-it, i plotë si `payload`, nën emrin e tij SIMCONNECT_RECV_ID: `SIMOBJECT_DATA`, `EVENT`, `EVENT_FILENAME`, `OPEN`, `QUIT`, `EXCEPTION` (një variabël ose ngjarje që simulatori nuk e pranoi, me send id dhe indeksin), çdo id tjetër me emrin e vet ose `RECV_<id>`
- çfarë mban vetëm skedari raw anësor: pozicioni i çdo kuadri simulimi mes rreshtave, ngjarjet Pause, Sim, CrashReset, PositionChanged dhe FlightSaved, një përkufizim që simulatori e preu (një variabël që nuk e njihte: blloku atëherë nuk lexohet me emër); `requests` në meta.json liston variablat dhe njësitë e çdo përkufizimi me radhë, që payload-et të lexohen pa këtë modul

**Nuk disponohet**

- avionët e tjerë (trafiku AI, lojtarët e tjerë online): SimConnect_RequestDataOnSimObjectType do të pyeste çdo avion brenda një rrezeje - më shumë ngarkesë për simulatorin, dhe fluturimet e lojtarëve të tjerë
- blloku i lëvizjes në çdo kuadër simulimi: kërkohet çdo kuadër të gjashtë (rreth 10 Hz, shpejtësia e rreshtave), që e mban rrjedhën raw rreth një të pestën e madhësisë; blloku i pozicionit mbetet në çdo kuadër
- mijëra variablat e tjera të simulimit (radiot, dritat, instrumentet e çdo motori, defektet): një përkufizim mban vetëm çfarë kërkon; listat kërkojnë fluturimin, gjendjen e avionit dhe kohën e simulatorit
- vëzhgimet e motit, objektet (aeroporte, VOR), të dhënat e klientit të shtesave: kërkesa të veçanta, nuk bëhen

**Madhësia**: rreth 30-55 MB në orë para zstd: blloku i pozicionit në çdo kuadër simulimi (rreth 200 bajte me kuadrin e vet, 30-60 në sekondë), blloku i lëvizjes në rreth 10 Hz (rreth 240 bajte), blloku i gjendjes një herë në sekondë; zstd i zvogëlon double-t disa herë

## Verifikuar {#verified}

dekodimi i mesazheve i provuar me buffer-a të ndërtuar nga strukturat e SimConnect.h; lidhja e drejtpërdrejtë SimConnect është e paprovuar

## Burimi {#source}

[heat3d_watch/adapters/msfs.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/msfs.py)

<!-- Gjeneruar nga adapteri me tools/gen_game_pages.py; ndrysho adapterin dhe ekzekuto përsëri, mos e redakto këtë faqe. -->
