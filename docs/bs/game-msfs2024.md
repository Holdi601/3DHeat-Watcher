---
title: "Microsoft Flight Simulator 2024 (podaci uživo)"
nav_order: 32
lang: "bs"
source: game-msfs2024.md
source_hash: "011c18a23252"
nav_exclude: true
search_exclude: true
---
# Microsoft Flight Simulator 2024 (podaci uživo) {#microsoft-flight-simulator-2024-live-data}

Dok igrate Microsoft Flight Simulator 2024, watcher sprema podatke koje igra sama šalje, da ih poslije možete pogledati na mapi u pregledniku 3DHeat.

*Tehnički detalji: adapter `msfs2024`, vrsta [`telemetry`](sources-and-rules.md); radi dok radi `FlightSimulator2024.exe` i svakih 0,1 s traži nove podatke.*

## Šta se snima {#what-is-recorded}

- pozicija vlastite letjelice svakog frejma simulacije, uzeta na 10 Hz (geografska širina/dužina/visina kao metri istok/gore/sjever od prve tačke; lat/lon/alt zadržani kao kolone)
- stav, indicirana brzina zraka, brzina nad tlom, AGL, g, na tlu; prava brzina zraka, Mach, vertikalna brzina, AoA, klizanje, magnetski smjer, brzine tijela, ubrzanja i stope rotacije na oko 10 Hz
- težina, gorivo, zakrilca, stajni trap, spojleri, parkirna kočnica, autopilot, gas, RPM, vrijeme, brzina simulacije, vrijeme i stanje kamere jednom u sekundi; naslov letjelice i ATC tip, model i id
- polijetanja, slijetanja, rušenja, letovi započeti i zaustavljeni (session_start/session_end)
- vrijeme leta, vrijeme u zraku, udaljenost, najveća visina, najveći g, slijetanja
- svaka SimConnect poruka čuva se cijela u heat.raw.parquet

## Odakle dolazi {#where-it-comes-from}

SimConnect preko igračevog vlastitog SimConnect.dll (folder simulatora, ili %MSFS2024_SDK%\SimConnect SDK\lib)

## Kako to uključiti {#how-to-switch-it-on}

ništa u simulatoru; treba SimConnect.dll - MSFS 2020 ga ima u svom folderu, igrači MSFS 2024 instaliraju MSFS 2024 SDK

## Kako radi {#how-it-works}

Microsoft Flight Simulator 2020 i 2024: SimConnect, preko igračevog vlastitog SimConnect.dll.

SimConnect je objavljeni klijentski API simulatora (SDK dokumentacija:
<https://docs.flightsimulator.com/html/Programming_Tools/SimConnect/SimConnect_SDK.htm>,
<https://docs.flightsimulator.com/msfs2024/html/6_Programming_APIs/SimConnect/SimConnect_SDK.htm>).
Watcher ne isporučuje DLL: učitava onaj koji je došao sa simulatorom ili
njegovim SDK-om - MSFS 2020 stavlja `SimConnect.dll` u svoj instalacijski folder; MSFS 2024 na
Steamu isporučuje samo svoj interni, pa igrači 2024 instaliraju MSFS 2024 SDK
(`<SDK>\SimConnect SDK\lib\SimConnect.dll`; simulator 2024 prihvata i klijente iz 2020).

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

Svaka poruka počinje s SIMCONNECT_RECV {DWORD dwSize, dwVersion, dwID}
(#pragma pack 1). One koje se ovdje čitaju:

```text
1  EXCEPTION       dwException, dwSendID, dwIndex
2  OPEN            szApplicationName[256], then version DWORDs
3  QUIT            the sim is closing
4  EVENT           uGroupID, uEventID, dwData
6  EVENT_FILENAME  EVENT + szFileName[260], dwFlags        (FlightLoaded)
8  SIMOBJECT_DATA  dwRequestID, dwObjectID, dwDefineID, dwFlags, dwentrynumber,
                   dwoutof, dwDefineCount, then the values (FLOAT64 each here)
```

Simulacijske varijable (jedinice se traže tako da konverzija nije potrebna): PLANE
LATITUDE/LONGITUDE (stepeni), PLANE ALTITUDE (metri, iznad mora), PLANE
ALT ABOVE GROUND (metri), PLANE PITCH/BANK DEGREES i PLANE HEADING DEGREES
TRUE (stepeni; SimConnectovi vlastiti predznaci - nos gore je negativan pitch), AIRSPEED
INDICATED i GROUND VELOCITY (čvorovi), G FORCE (gforce), SIM ON GROUND (bool).
Sistemski događaji: SimStart, SimStop, Crashed, FlightLoaded, AircraftLoaded,
Pause, CrashReset, PositionChanged, FlightSaved, Sim.

Još tri definicije podataka traže ostatak leta (`MOTION_VARS`,
svaki šesti frejm simulacije), sporije stanje letjelice (`STATE_VARS`, jednom u
sekundi) i njena imena (`NAME_VARS`, stringovi od 256 bajtova, kad se promijene); svaka
je vlastita definicija, pa varijabla koju jedna verzija simulatora ne poznaje košta
samo taj blok. Svaka poruka čuva se cijela u sirovom sidecaru sesije.

Pozicije idu u istu ravnu mapu kao kod X-Planea (x istok, y visina, z sjever
u metrima od prve tačke sjedenja); ta tačka je `geo` sesije, u
meta.json i podnožju tabele.

Isti modul služi i: [Microsoft Flight Simulator 2020 (podaci uživo)](game-msfs2020.md).

## Pozicije i ose {#positions-and-axes}

| | |
|---|---|
| Pozicije se snimaju | da |
| Osa gore | `y` |
| Jedinice | metri (istok, visina, sjever od prve tačke) |
| Zrcaljeno za preglednik | `z` |
| Skala jedinica (`scale`: preglednik njome množi pozicije) | 1 |

Ovo ide u `meta.json` svake sesije (`axes`) i, kad sesija ima pozicije, u podnožje datoteke `heat.parquet`, pa preglednik 3DHeat sam rotira i skalira redove - vidite [Podaci](the-data.md).

## Multiplayer {#multiplayer}

- Označeno kao igrano online (`multiplayer`): **da**. `games --markdown` to prikazuje kao "dozvoljeno (čita samo ono što igra objavljuje)".
- Vrsta `telemetry`: čita samo ono što igra ili platforma daje (UDP port ili dijeljena memorija koju igra objavljuje), pa snima i u online igri kao i offline; zastavica odlučuje samo smije li se memorija ikad čitati.
- Memorija: ovaj adapter je **nikad** ne čita. Memoriju čitaju samo `memory` adapteri, i to nikad za igru označenu kao igranu online - vidite [Izvori i pravila](sources-and-rules.md).

## Zabilježene statistike {#statistics-recorded}

Ključevi statistika koje kod ovog adaptera postavlja po imenu (`stats` svake sesije u `meta.json` i tabela `stats` u `watcher.sqlite`):

`airborne_time`, `bad_packets`, `crashes`, `distance_km`, `flight_time`, `max_altitude_m`, `max_g`, `{event}s`

Ključ u vitičastim zagradama dovršava se za vrijeme rada (`score.{team}` je jedan ključ po timu). Ključevi koje kod uzima iz tabele polja igre ili iz igrinih vlastitih imena statistika nisu na ovoj listi; "Šta se snima" iznad ih navodi.

## Potpunost {#completeness}

Watcher slijedi 3DHeatovo [pravilo konvertera](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md): ono što izvor drži čita se ili čuva, nikad ne odbacuje. Osim redova, svaki paket, stranica, linija ili odgovor koji adapter primi čuva se cijel u `heat.raw.parquet` sesije (kolone `time`, `ms`, `type`, `used`, `payload`, `text`, zatim svako polje čuvano po imenu; `used` označava šta je postalo i redovi), a `selfCheck.completeness` u `meta.json` broji svaki `type` - `lost` je 0.

**Čita se**

- SIMOBJECT_DATA definicije pozicije (svaki frejm simulacije): geografska širina, dužina, visina, AGL, pitch, bank, pravi smjer, IAS, brzina nad tlom, g, na tlu - zadnji frejm poll-a kao red, svaki frejm za dodire tla i polijetanja
- SIMOBJECT_DATA definicije kretanja (oko 10 Hz: TAS, Mach, vertikalna brzina, AoA, klizanje, magnetski smjer, brzina tijela, ubrzanje i stopa rotacije na tri ose) i definicije stanja (1 Hz: težine, gorivo, zakrilca, stajni trap, spojleri, parkirna kočnica, autopilot, motori, gas i RPM, vanjska temperatura, vjetar, pritisak na nivou mora, brzina simulacije, zulu i lokalno vrijeme, stanje kamere) na redove kako je zadnje primljeno
- SIMOBJECT_DATA definicije imena (naslov, ATC tip, model i id) u meta.json i `aircraft` redova; OPEN (aplikacija i verzija) u meta.json
- EVENT i EVENT_FILENAME: SimStart, SimStop, Crashed, FlightLoaded (datoteka leta) i AircraftLoaded (datoteka letjelice) kao letovi, rušenja i meta.json
- QUIT završava sesiju

**Čuva se sirovo**

- svaka poruka koju SimConnect preda watcheru, cijela kao `payload`, pod imenom svog SIMCONNECT_RECV_ID: `SIMOBJECT_DATA`, `EVENT`, `EVENT_FILENAME`, `OPEN`, `QUIT`, `EXCEPTION` (varijabla ili događaj koji simulator nije prihvatio, sa send id-om i indeksom), svaki drugi id pod svojim imenom ili `RECV_<id>`
- ono što drži samo sirovi sidecar: pozicija svakog frejma simulacije između redova, događaji Pause, Sim, CrashReset, PositionChanged i FlightSaved, definicija koju je simulator skratio (jedna varijabla koju nije poznavao: blok se tada ne čita po imenu); `requests` u meta.json navodi varijable i jedinice svake definicije redom, pa se payloadi čitaju i bez ovog modula

**Nije dostupno**

- druge letjelice (AI promet, drugi igrači online): SimConnect_RequestDataOnSimObjectType bi pitao svaku letjelicu u radijusu - veće opterećenje simulatora, i letovi drugih igrača
- blok kretanja svakog frejma simulacije: traži se svaki šesti frejm (oko 10 Hz, brzina redova), što drži sirovi tok na oko petini veličine; blok pozicije ostaje svaki frejm
- hiljade drugih simulacijskih varijabli (radiji, svjetla, mjerači svakog motora, kvarovi): definicija drži ono što traži; liste traže let, stanje letjelice i vrijeme simulatora
- vremenska osmatranja, objekti (aerodromi, VOR-ovi), klijentski podaci dodataka: zasebni zahtjevi, ne šalju se

**Veličina**: oko 30-55 MB na sat prije zstd: blok pozicije svakog frejma simulacije (oko 200 bajtova s okvirom, 30-60 u sekundi), blok kretanja na oko 10 Hz (oko 240 bajtova), blok stanja jednom u sekundi; zstd smanji double vrijednosti nekoliko puta

## Provjereno {#verified}

dekodiranje poruka testirano na baferima izgrađenim iz rasporeda SimConnect.h; živa SimConnect veza je neprovjerena

## Izvor {#source}

[heat3d_watch/adapters/msfs.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/msfs.py)

<!-- Generated from the adapter by tools/gen_game_pages.py; change the adapter and run it again rather than editing this page. -->
