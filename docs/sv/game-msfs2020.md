---
title: "Microsoft Flight Simulator 2020 (livedata)"
nav_order: 31
lang: "sv"
source: game-msfs2020.md
source_hash: "9b9e8389114b"
nav_exclude: true
search_exclude: true
---
# Microsoft Flight Simulator 2020 (livedata) {#microsoft-flight-simulator-2020-live-data}

Medan du spelar Microsoft Flight Simulator 2020 sparar watchern den data som spelet själv skickar ut, så att du senare kan titta på den på en karta i 3DHeat-visaren.

*Teknisk information: adaptern `msfs2020`, typ [`telemetry`](sources-and-rules.md); den körs medan `FlightSimulator.exe` är igång och letar efter ny data var 0,1 s.*

## Vad som spelas in {#what-is-recorded}

- egna flygplanets position vid varje simulatorram, taget 10 gånger per sekund (latitud/longitud/höjd som meter öster/upp/norr från första fixen; lat/lon/alt sparade som kolumner)
- attityd, visad lufthastighet, markhastighet, AGL, g, på marken; sann lufthastighet, Mach, vertikal hastighet, AoA, glidvinkel, magnetisk kurs, kroppshastigheter, accelerationer och rotationshastigheter cirka 10 gånger per sekund
- vikt, bränsle, klaffar, understräll, spoilers, parkeringsbroms, autopilot, gas, varvtal, väder, simulatorhastighet, tid och kamerastatus en gång per sekund; flygplanets titel och ATC-typ, modell och id
- start, landningar, krascher, flygningar som startas och stoppas (session_start/session_end)
- flygtid, lufttid, sträcka, högsta höjd, högsta g, landningar
- varje SimConnect-meddelande sparat helt i heat.raw.parquet

## Varifrån det kommer {#where-it-comes-from}

SimConnect genom spelarens egen SimConnect.dll (simulatorns mapp, eller %MSFS_SDK%\SimConnect SDK\lib)

## Så slår du på det {#how-to-switch-it-on}

inget; SimConnect.dll följer med MSFS 2020 (eller MSFS SDK)

## Så fungerar det {#how-it-works}

Microsoft Flight Simulator 2020 och 2024: SimConnect, genom spelarens egen SimConnect.dll.

SimConnect är simulatorns publicerade klient-API (SDK-dokumentation: <https://docs.flightsimulator.com/html/Programming_Tools/SimConnect/SimConnect_SDK.htm>, <https://docs.flightsimulator.com/msfs2024/html/6_Programming_APIs/SimConnect/SimConnect_SDK.htm>). Watchern levererar inte DLL:en: den laddar den som följde med simulatorn eller dess SDK - MSFS 2020 lägger `SimConnect.dll` i sin installationsmapp; MSFS 2024 på Steam levererar bara sin interna, så 2024-spelare installerar MSFS 2024 SDK (`<SDK>\SimConnect SDK\lib\SimConnect.dll`; 2024-simulatorn accepterar också 2020-klienter).

Anropen, från SimConnect.h, returnerar alla en HRESULT (0 = S_OK):

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

Varje meddelande börjar med SIMCONNECT_RECV {DWORD dwSize, dwVersion, dwID} (#pragma pack 1). De som läses här:

```text
1  EXCEPTION       dwException, dwSendID, dwIndex
2  OPEN            szApplicationName[256], then version DWORDs
3  QUIT            the sim is closing
4  EVENT           uGroupID, uEventID, dwData
6  EVENT_FILENAME  EVENT + szFileName[260], dwFlags        (FlightLoaded)
8  SIMOBJECT_DATA  dwRequestID, dwObjectID, dwDefineID, dwFlags, dwentrynumber,
                   dwoutof, dwDefineCount, then the values (FLOAT64 each here)
```

Simuleringsvariabler (enheterna som begärs, så att ingen omvandling behövs): PLANE LATITUDE/LONGITUDE (grader), PLANE ALTITUDE (meter, över havet), PLANE ALT ABOVE GROUND (meter), PLANE PITCH/BANK DEGREES och PLANE HEADING DEGREES TRUE (grader; SimConnects egna tecken - nosen upp är negativ stigning), AIRSPEED INDICATED och GROUND VELOCITY (knop), G FORCE (gforce), SIM ON GROUND (bool). Systemhändelser: SimStart, SimStop, Crashed, FlightLoaded, AircraftLoaded, Pause, CrashReset, PositionChanged, FlightSaved, Sim.

Tre datadefinitioner till begär resten av flygningen (`MOTION_VARS`, var sjätte simulatorram), flygplanets långsammare tillstånd (`STATE_VARS`, en gång per sekund) och dess namn (`NAME_VARS`, 256-byte strängar, när de ändras); var och en är en egen definition, så att en variabel som en simulatorversion inte känner till bara kostar det blocket. Varje meddelande sparas helt i sessionens råa sidovagn.

Positionerna går in i samma platta karta som X-Planes (x öster, y höjd, z norr i meter från sittningens första fix); den fixen är sessionens `geo`, i meta.json och tabellens footer.

Samma modul används också av: [Microsoft Flight Simulator 2024 (livedata)](game-msfs2024.md).

## Positioner och axlar {#positions-and-axes}

| | |
|---|---|
| Positioner sparas | ja |
| Uppåtaxel | `y` |
| Enheter | meter (öster, höjd, norr från första fixen) |
| Speglad för visaren | `z` |
| Enhetsskala (`scale`: visaren multiplicerar positionerna med den) | 1 |

Dessa läggs i varje sessions `meta.json` (`axes`) och, när sessionen har positioner, i `heat.parquet`:s footer, så att 3DHeat-visaren vrider och skalar raderna själv - se [Datan](the-data.md).

## Multiplayer {#multiplayer}

- Markerad som spelad online (`multiplayer`): **ja**. `games --markdown` visar detta som "tillåten (läser bara det spelet publicerar)".
- Typ `telemetry`: den läser bara det spelet eller plattformen lämnar ut (en UDP-port eller delat minne som spelet publicerar), så den spelar in även i onlinespel så väl som offline; flaggan avgör bara om minnet någonsin får läsas.
- Minne: läses **aldrig** av den här adaptern. Bara `memory`-adaptrar läser minne, och aldrig för ett spel som är markerat som spelat online - se [Källor och regler](sources-and-rules.md).

## Statistik som sparas {#statistics-recorded}

Statistiknycklar som adapterns kod sätter med namn (varje sessions `stats` i `meta.json` och tabellen `stats` i `watcher.sqlite`):

`airborne_time`, `bad_packets`, `crashes`, `distance_km`, `flight_time`, `max_altitude_m`, `max_g`, `{event}s`

En nyckel inom klammerparenteser fylls i vid körning (`score.{team}` är en nyckel per lag). Nycklar som koden tar från en tabell med spelets fält eller från spelets egna statistiknamn finns inte med i den här listan; "Vad som spelas in" ovan nämner dem.

## Fullständighet {#completeness}

Watchern följer 3DHeats [omvandlarregel](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md): det källan innehåller läses eller sparas, aldrig slängs. Utöver raderna sparas varje paket, sida, rad eller svar som adaptern tar emot helt i sessionens `heat.raw.parquet` (kolumnerna `time`, `ms`, `type`, `used`, `payload`, `text`, plus eventuella fält som sparas med namn; `used` markerar det som också blev rader), och `meta.json`:s `selfCheck.completeness` räknar varje `type` - `lost` är 0.

**Läses**

- SIMOBJECT_DATA för positionsdefinitionen (varje simulatorram): latitud, longitud, höjd, AGL, stigning, rulle, sann kurs, IAS, markhastighet, g, på marken - sista ramen i poll:en som en rad, varje ram för nedslag och start
- SIMOBJECT_DATA för rörelsedefinitionen (cirka 10 Hz: TAS, Mach, vertikal hastighet, AoA, glidvinkel, magnetisk kurs, kroppshastighet, acceleration och rotationshastighet på tre axlar) och för tillståndsdefinitionen (1 Hz: vikter, bränsle, klaffar, understräll, spoilers, parkeringsbroms, autopilot, motorer, gas och varvtal, utetemperatur, vind, havsnivåtryck, simulatorhastighet, zulu- och lokaltid, kamerastatus) på raderna som senast togs emot
- SIMOBJECT_DATA för namndefinitionen (titel, ATC-typ, modell och id) till meta.json och radernas `aircraft`; OPEN (program och version) till meta.json
- EVENT och EVENT_FILENAME: SimStart, SimStop, Crashed, FlightLoaded (flygfilen) och AircraftLoaded (flygplansfilen) som flygningar, krascher och meta.json
- QUIT avslutar sessionen

**Sparas råa**

- varje meddelande SimConnect ger watchern, helt som `payload`, under sitt SIMCONNECT_RECV_ID-namn: `SIMOBJECT_DATA`, `EVENT`, `EVENT_FILENAME`, `OPEN`, `QUIT`, `EXCEPTION` (en variabel eller händelse som simulatorn inte accepterade, med sänd-id och index), varje annat id med sitt namn eller `RECV_<id>`
- det bara den råa sidovagnen har: varje simulatorrams position mellan raderna, händelserna Pause, Sim, CrashReset, PositionChanged och FlightSaved, en definition som simulatorn kortade (en variabel den inte kände till: blocket läses då inte med namn); meta.json:s `requests` listar varje definitions variabler och enheter i ordning, så att nyttolasterna går att läsa utan den här modulen

**Inte tillgängligt**

- andra flygplan (AI-trafik, andra spelare online): SimConnect_RequestDataOnSimObjectType skulle fråga varje flygplan i en radie - mer belastning på simulatorn, och andra spelares flygningar
- rörelseblocket för varje simulatorram: det begärs var sjätte ram (cirka 10 Hz, radernas takt), vilket håller det råa flödet nära en femtedel av storleken; positionsblocket är kvar för varje ram
- de tusentals andra simuleringsvariablerna (radior, lampor, varje motors mätare, fel): en definition innehåller det den begär; listorna begär flygningen, flygplanets tillstånd och simulatorns tid
- väderobservationer, anläggningar (flygplatser, VOR:ar), klientdata från tillägg: separata begäranden, inte gjorda

**Storlek**: cirka 30-55 MB per timme före zstd: positionsblocket för varje simulatorram (cirka 200 byte med sin ram, 30-60 per sekund), rörelseblocket vid cirka 10 Hz (cirka 240 byte), tillståndsblocket en gång per sekund; zstd krymper flyttalen flera gånger

## Verifierad {#verified}

meddelandeavkodningen testad på buffrar byggda från SimConnect.h:s layouter; den levande SimConnect-anslutningen är otestad

## Källa {#source}

[heat3d_watch/adapters/msfs.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/msfs.py)

<!-- Generated from the adapter by tools/gen_game_pages.py; change the adapter and run it again rather than editing this page. -->
