---
title: "Microsoft Flight Simulator 2020 (živi podaci)"
nav_order: 31
lang: "hr"
source: game-msfs2020.md
source_hash: "9b9e8389114b"
nav_exclude: true
search_exclude: true
---
# Microsoft Flight Simulator 2020 (živi podaci) {#microsoft-flight-simulator-2020-live-data}

Dok igrate Microsoft Flight Simulator 2020, watcher sprema podatke koje sama igra šalje van, pa to kasnije možete pogledati na karti u 3DHeat pregledniku.

*Tehnički podaci: adapter `msfs2020`, vrsta [`telemetry`](sources-and-rules.md); radi dok je `FlightSimulator.exe` pokrenut i traži nove podatke svakih 0,1 s.*

## Što se bilježi {#what-is-recorded}

- vlastita pozicija zrakoplova u svakom okviru simulacije, uzeta 10 puta u sekundi (geografska širina/dužina/visina kao metri istočno/gore/sjeverno od prvog mjerenja; lat/lon/alt sačuvani kao stupci)
- stav, indicirana brzina zraka, brzina po tlu, AGL, g, na tlu; stvarna brzina zraka, Mach, vertikalna brzina, napadni kut, klizanje, magnetski kurs, brzine tijela, ubrzanja i brzine rotacije oko 10 puta u sekundi
- težina, gorivo, zakrilca, podvozje, spojleri, parkirna kočnica, autopilot, gas, okretaji, vremenski uvjeti, brzina simulacije, vrijeme i stanje kamere jednom u sekundi; naziv zrakoplova i ATC tip, model i ID
- polijetanja, slijetanja, padovi, započeti i zaustavljeni letovi (session_start/session_end)
- vrijeme leta, vrijeme u zraku, udaljenost, najveća visina, najveći g, slijetanja
- svaka SimConnect poruka, cjelovita u heat.raw.parquet

## Odakle dolazi {#where-it-comes-from}

SimConnect preko vlastite datoteke SimConnect.dll igrača (mapa simulatora, ili %MSFS_SDK%\SimConnect SDK\lib)

## Kako ga uključiti {#how-to-switch-it-on}

ništa; SimConnect.dll dolazi uz MSFS 2020 (ili uz MSFS SDK)

## Kako radi {#how-it-works}

Microsoft Flight Simulator 2020 i 2024: SimConnect, preko vlastite datoteke SimConnect.dll igrača.

SimConnect je objavljeni klijentski API simulatora (dokumentacija SDK-a: <https://docs.flightsimulator.com/html/Programming_Tools/SimConnect/SimConnect_SDK.htm>, <https://docs.flightsimulator.com/msfs2024/html/6_Programming_APIs/SimConnect/SimConnect_SDK.htm>). Watcher ne isporučuje DLL: učitava onaj koji je došao sa simulatorom ili njegovim SDK-om - MSFS 2020 stavlja `SimConnect.dll` u svoju mapu za instalaciju; MSFS 2024 na Steamu isporučuje samo svoju internu verziju, pa igrači 2024 instaliraju MSFS 2024 SDK (`<SDK>\SimConnect SDK\lib\SimConnect.dll`; simulator 2024 prihvaća i klijente 2020).

Pozivi, iz SimConnect.h, svi vraćaju HRESULT (0 = S_OK):

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

Svaka poruka počinje sa SIMCONNECT_RECV {DWORD dwSize, dwVersion, dwID} (#pragma pack 1). Ovdje se čitaju ove:

```text
1  EXCEPTION       dwException, dwSendID, dwIndex
2  OPEN            szApplicationName[256], then version DWORDs
3  QUIT            the sim is closing
4  EVENT           uGroupID, uEventID, dwData
6  EVENT_FILENAME  EVENT + szFileName[260], dwFlags        (FlightLoaded)
8  SIMOBJECT_DATA  dwRequestID, dwObjectID, dwDefineID, dwFlags, dwentrynumber,
                   dwoutof, dwDefineCount, then the values (FLOAT64 each here)
```

Varijable simulacije (traže se u jedinicama koje ne trebaju pretvorbu): PLANE LATITUDE/LONGITUDE (stupnjevi), PLANE ALTITUDE (metri, iznad mora), PLANE ALT ABOVE GROUND (metri), PLANE PITCH/BANK DEGREES i PLANE HEADING DEGREES TRUE (stupnjevi; SimConnectovi vlastiti predznaci - nos gore je negativan nagib), AIRSPEED INDICATED i GROUND VELOCITY (čvorovi), G FORCE (gforce), SIM ON GROUND (bool). Sistemski događaji: SimStart, SimStop, Crashed, FlightLoaded, AircraftLoaded, Pause, CrashReset, PositionChanged, FlightSaved, Sim.

Tri daljnje definicije podataka traže ostatak leta (`MOTION_VARS`, svaki šesti okvir simulacije), sporije stanje zrakoplova (`STATE_VARS`, jednom u sekundi) i njegova imena (`NAME_VARS`, nizovi od 256 bajtova, kad se promijene); svaka je zasebna definicija, pa varijabla koju jedna verzija simulatora ne poznaje košta samo taj blok. Svaka poruka čuva se cjelovito u sirovoj pomoćnoj datoteci sesije.

Pozicije idu u istu ravnu kartu kao X-Plane (x istok, y visina, z sjever, u metrima od prvog mjerenja sjedenja); to mjerenje je `geo` sesije, u meta.json i u podnožju tablice.

Isti modul služi i za: [Microsoft Flight Simulator 2024 (živi podaci)](game-msfs2024.md).

## Pozicije i osi {#positions-and-axes}

| | |
|---|---|
| Pozicije se bilježe | da |
| Os prema gore | `y` |
| Jedinice | metri (istok, visina, sjever od prvog mjerenja) |
| Zrcaljeno za preglednik | `z` |
| Mjerilo jedinice (`scale`: preglednik pozicije množi njime) | 1 |

Ovo ide u `meta.json` svake sesije (`axes`) i, kad sesija ima pozicije, u podnožje `heat.parquet`, pa 3DHeat preglednik sam okreće i skalira retke - vidi [Podaci](the-data.md).

## Više igrača {#multiplayer}

- Označeno kao igra na mreži (`multiplayer`): **da**. `games --markdown` to prikazuje kao "allowed (reads only what the game publishes)".
- Vrsta `telemetry`: čita samo ono što igra ili platforma daje (UDP port ili dijeljena memorija koju igra objavljuje), pa bilježi i u igri na mreži i izvan nje; zastavica odlučuje samo smije li se ikad čitati memorija.
- Memorija: ovaj adapter je **nikad** ne čita. Samo adapteri `memory` čitaju memoriju, i nikad za igru označenu kao igra na mreži - vidi [Izvori i pravila](sources-and-rules.md).

## Statistika koja se bilježi {#statistics-recorded}

Ključevi statistike koje kod ovog adaptera postavlja po imenu (`stats` svake sesije u `meta.json` i tablica `stats` u `watcher.sqlite`):

`airborne_time`, `bad_packets`, `crashes`, `distance_km`, `flight_time`, `max_altitude_m`, `max_g`, `{event}s`

Ključ u vitičastim zagradama dovršava se pri radu (`score.{team}` je jedan ključ za svaki tim). Ključevi koje kod uzima iz tablice polja igre ili iz vlastitih imena statistike igre nisu na ovom popisu; navedeni su u odjeljku "Što se bilježi" gore.

## Potpunost {#completeness}

Watcher slijedi [pravilo pretvarača 3DHeata](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md): ono što izvor sadrži se čita ili čuva, nikad se ne odbacuje. Osim redaka, svaki paket, stranica, redak ili odgovor koji adapter primi čuva se cjelovito u `heat.raw.parquet` sesije (stupci `time`, `ms`, `type`, `used`, `payload`, `text`, pa svako polje koje je sačuvano po imenu; `used` označava što je postalo i retkom), a `selfCheck.completeness` u `meta.json` broji svaki `type` - `lost` je 0.

**Čita se**

- SIMOBJECT_DATA definicije pozicije (svaki okvir simulacije): geografska širina, dužina, visina, AGL, nagib, valjanje, pravi kurs, IAS, brzina po tlu, g, na tlu - zadnji okvir očitavanja kao redak, svaki okvir za dodir kotačima i polijetanja
- SIMOBJECT_DATA definicije kretanja (oko 10 Hz: TAS, Mach, vertikalna brzina, napadni kut, klizanje, magnetski kurs, brzina tijela, ubrzanje i brzina rotacije na tri osi) i definicije stanja (1 Hz: težine, gorivo, zakrilca, podvozje, spojleri, parkirna kočnica, autopilot, motori, gas i okretaji, vanjska temperatura, vjetar, tlak na razini mora, brzina simulacije, zulu i lokalno vrijeme, stanje kamere) na retke kako su zadnji put primljeni
- SIMOBJECT_DATA definicije naziva (naziv, ATC tip, model i ID) u meta.json i stupac `aircraft` redaka; OPEN (aplikacija i verzija) u meta.json
- EVENT i EVENT_FILENAME: SimStart, SimStop, Crashed, FlightLoaded (datoteka leta) i AircraftLoaded (datoteka zrakoplova) kao letovi, padovi i meta.json
- QUIT završava sesiju

**Čuva se u izvornom obliku**

- svaka poruka koju SimConnect predaje watcheru, cjelovita kao `payload`, pod imenom njezina SIMCONNECT_RECV_ID: `SIMOBJECT_DATA`, `EVENT`, `EVENT_FILENAME`, `OPEN`, `QUIT`, `EXCEPTION` (varijabla ili događaj koji simulator nije prihvatio, s ID-om slanja i indeksom), svaki ostali ID po imenu ili `RECV_<id>`
- što drži samo sirova pomoćna datoteka: svaka pozicija svakog okvira simulacije između redaka, događaji Pause, Sim, CrashReset, PositionChanged i FlightSaved, definicija koju je simulator skratio (jedna varijabla koju nije poznavao: blok se tada ne čita po imenu); `requests` u meta.json navodi svaku varijablu i jedinicu svake definicije redom, pa se korisni podaci čitaju i bez ovog modula

**Nije dostupno**

- drugi zrakoplovi (AI promet, drugi igrači na mreži): SimConnect_RequestDataOnSimObjectType bi očitavao svaki zrakoplov u radijusu - veće opterećenje simulatora, i tuđi letovi
- blok kretanja na svakom okviru simulacije: traži se svaki šesti okvir (oko 10 Hz, brzina redaka), što sirovi tok drži blizu petine veličine; blok pozicije ostaje na svakom okviru
- tisuće drugih varijabli simulacije (radio, svjetla, svaki mjerač motora, kvarovi): definicija sadrži ono što traži; popisi traže let, stanje zrakoplova i vrijeme simulacije
- vremenska opažanja, objekti (aerodromi, VOR-ovi), podaci klijenata dodataka: zasebni zahtjevi, nisu traženi

**Veličina**: oko 30-55 MB na sat prije zstd: blok pozicije na svakom okviru (oko 200 bajtova s okvirom, 30-60 u sekundi), blok kretanja oko 10 Hz (oko 240 bajtova), blok stanja jednom u sekundi; zstd smanji decimalne brojeve nekoliko puta

## Provjereno {#verified}

dekodiranje poruka testirano na međuspremnicima izgrađenima prema rasporedima iz SimConnect.h; živa veza sa SimConnectom nije testirana

## Izvor {#source}

[heat3d_watch/adapters/msfs.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/msfs.py)

<!-- Generated from the adapter by tools/gen_game_pages.py; change the adapter and run it again rather than editing this page. -->
