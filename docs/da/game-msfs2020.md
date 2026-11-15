---
title: "Microsoft Flight Simulator 2020 (live-data)"
nav_order: 31
lang: "da"
source: game-msfs2020.md
source_hash: "9b9e8389114b"
nav_exclude: true
search_exclude: true
---
# Microsoft Flight Simulator 2020 (live-data) {#microsoft-flight-simulator-2020-live-data}

Mens du spiller Microsoft Flight Simulator 2020, gemmer watcheren de data, spillet selv sender ud, så du senere kan se dem på et kort i 3DHeat-vieweren.

*Tekniske detaljer: adapter `msfs2020`, slags [`telemetry`](sources-and-rules.md); den kører, mens `FlightSimulator.exe` kører, og kigger efter nye data hvert 0,1 s.*

## Hvad der optages {#what-is-recorded}

- egen flyveenheds position hver simulationsramme, taget 10 gange i sekundet (breddegrad/længdegrad/højde som meter øst/op/nord fra den første fix; lat/lon/alt gemt som kolonner)
- attitude, angivet lufthastighed, jordhastighed, AGL, g, på jorden; sand lufthastighed, Mach, lodret hastighed, AoA, sideglidning, magnetisk kurs, kropshastigheder, accelerationer og rotationshastigheder cirka 10 gange i sekundet
- vægt, brændstof, klapper, understel, spoilere, parkeringsbremse, autopilot, gas, omdrejninger, vejr, simulationshastighed, tid og kameratilstand én gang i sekundet; flyets titel og ATC-type, model og id
- start, landinger, nedstyrtninger, flyvninger startet og stoppet (session_start/session_end)
- flyvetid, tid i luften, distance, højeste højde, højeste g, landinger
- hver SimConnect-besked gemt helt i heat.raw.parquet

## Hvor det kommer fra {#where-it-comes-from}

SimConnect gennem spillerens egen SimConnect.dll (simulatorens mappe, eller %MSFS_SDK%\SimConnect SDK\lib)

## Sådan slår du det til {#how-to-switch-it-on}

ingenting; SimConnect.dll følger med MSFS 2020 (eller MSFS SDK'et)

## Sådan virker det {#how-it-works}

Microsoft Flight Simulator 2020 og 2024: SimConnect, gennem spillerens egen SimConnect.dll.

SimConnect er simulatorens offentliggjorte klient-API (SDK-dokumentation:
<https://docs.flightsimulator.com/html/Programming_Tools/SimConnect/SimConnect_SDK.htm>,
<https://docs.flightsimulator.com/msfs2024/html/6_Programming_APIs/SimConnect/SimConnect_SDK.htm>).
Watcheren medbringer ikke DLL'en: den indlæser den, der fulgte med simulatoren eller dens
SDK - MSFS 2020 lægger `SimConnect.dll` i sin installationsmappe; MSFS 2024 på
Steam medbringer kun sin interne, så 2024-spillere installerer MSFS 2024 SDK'et
(`<SDK>\SimConnect SDK\lib\SimConnect.dll`; 2024-simulatoren accepterer også 2020-klienter).

Kaldene, fra SimConnect.h, returnerer alle en HRESULT (0 = S_OK):

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

Hver besked starter med SIMCONNECT_RECV {DWORD dwSize, dwVersion, dwID}
(#pragma pack 1). Dem der læses her:

```text
1  EXCEPTION       dwException, dwSendID, dwIndex
2  OPEN            szApplicationName[256], then version DWORDs
3  QUIT            the sim is closing
4  EVENT           uGroupID, uEventID, dwData
6  EVENT_FILENAME  EVENT + szFileName[260], dwFlags        (FlightLoaded)
8  SIMOBJECT_DATA  dwRequestID, dwObjectID, dwDefineID, dwFlags, dwentrynumber,
                   dwoutof, dwDefineCount, then the values (FLOAT64 each here)
```

Simulationsvariabler (de enheder der bedes om, så ingen omregning er nødvendig): PLANE
LATITUDE/LONGITUDE (grader), PLANE ALTITUDE (meter, over havet), PLANE
ALT ABOVE GROUND (meter), PLANE PITCH/BANK DEGREES og PLANE HEADING DEGREES
TRUE (grader; SimConnects egne fortegn - næsen op er negativ stigning), AIRSPEED
INDICATED og GROUND VELOCITY (knob), G FORCE (gforce), SIM ON GROUND (bool).
Systemhændelser: SimStart, SimStop, Crashed, FlightLoaded, AircraftLoaded,
Pause, CrashReset, PositionChanged, FlightSaved, Sim.

Tre yderligere datadefinitioner beder om resten af flyvningen (`MOTION_VARS`,
hver sjette simulationsramme), flyets langsommere tilstand (`STATE_VARS`, én gang i
sekundet) og dets navne (`NAME_VARS`, 256-byte strenge, når de ændrer sig); hver
er sin egen definition, så en variabel en simulatorversion ikke kender, kun koster
den blok. Hver besked gemmes helt i sessionens rå sidecar.

Positioner lægges i det samme flade kort som X-Planes (x øst, y højde, z nord
i meter fra sessionens første fix); den fix er sessionens `geo`, i
meta.json og tabellens footer.

Det samme modul betjener også: [Microsoft Flight Simulator 2024 (live-data)](game-msfs2024.md).

## Positioner og akser {#positions-and-axes}

| | |
|---|---|
| Positioner optaget | ja |
| Opadakse | `y` |
| Enheder | meter (øst, højde, nord fra den første fix) |
| Spejlet for viewer | `z` |
| Enhedsskala (`scale`: viewer ganger positionerne med den) | 1 |

Disse går ind i hver sessions `meta.json` (`axes`) og, når sessionen har positioner, i `heat.parquet`s footer, så 3DHeat-viewer selv drejer og skalerer rækkerne - se [Dataene](the-data.md).

## Multiplayer {#multiplayer}

- Markeret som spillet online (`multiplayer`): **ja**. `games --markdown` viser dette som "allowed (reads only what the game publishes)".
- Slags `telemetry`: den læser kun det, spillet eller platformen udleverer (en UDP-port eller delt hukommelse, spillet udgiver), så den optager også i online-spil, ligesom offline; flaget afgør kun, om hukommelsen nogensinde må læses.
- Hukommelse: **aldrig** læst af denne adapter. Kun `memory`-adaptere læser hukommelse, og aldrig for et spil markeret som spillet online - se [Kilder og regler](sources-and-rules.md).

## Statistik der optages {#statistics-recorded}

Statistiknøglerne, som denne adapters kode sætter med navn (hver sessions `stats` i `meta.json` og tabellen `stats` i `watcher.sqlite`):

`airborne_time`, `bad_packets`, `crashes`, `distance_km`, `flight_time`, `max_altitude_m`, `max_g`, `{event}s`

En nøgle i klammer udfyldes under kørslen (`score.{team}` er én nøgle pr. hold). Nøgler som koden tager fra en tabel over spillets felter eller fra spillets egne statistiknavne står ikke på listen; "Hvad der optages" ovenfor nævner dem.

## Fuldstændighed {#completeness}

Watcheren følger 3DHeats [konverterregel](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md): det kilden indeholder bliver læst eller gemt, aldrig smidt væk. Ud over rækkerne gemmes hver pakke, side, linje eller svar adapteren modtager, helt i sessionens `heat.raw.parquet` (kolonnerne `time`, `ms`, `type`, `used`, `payload`, `text` og derefter felter der gemmes efter navn; `used` markerer det, der også blev til rækker), og `meta.json`s `selfCheck.completeness` tæller hver `type` - `lost` er 0.

**Læst**

- SIMOBJECT_DATA af positionsdefinitionen (hver simulationsramme): breddegrad, længdegrad, højde, AGL, stigning, rulning, sand kurs, IAS, jordhastighed, g, på jorden - pollens sidste ramme som en række, hver ramme for touchdowns og start
- SIMOBJECT_DATA af bevægelsesdefinitionen (cirka 10 Hz: TAS, Mach, lodret hastighed, AoA, sideglidning, magnetisk kurs, kropshastighed, acceleration og rotationshastighed på tre akser) og af tilstandsdefinitionen (1 Hz: vægte, brændstof, klapper, understel, spoilere, parkeringsbremse, autopilot, motorer, gas og omdrejninger, udetemperatur, vind, havniveautryk, simulationshastighed, zulu- og lokal tid, kameratilstand) på rækkerne som sidst modtaget
- SIMOBJECT_DATA af navnedefinitionen (titel, ATC-type, model og id) ind i meta.json og rækkernes `aircraft`; OPEN (program og version) ind i meta.json
- EVENT og EVENT_FILENAME: SimStart, SimStop, Crashed, FlightLoaded (flyvefilen) og AircraftLoaded (flyets fil) som flyvninger, nedstyrtninger og meta.json
- QUIT afslutter sessionen

**Gemt rå**

- hver besked SimConnect giver watcheren, helt som `payload`, under sit SIMCONNECT_RECV-id-navn: `SIMOBJECT_DATA`, `EVENT`, `EVENT_FILENAME`, `OPEN`, `QUIT`, `EXCEPTION` (en variabel eller hændelse simulatoren ikke accepterede, med send-id og indeks), ethvert andet id efter navn eller `RECV_<id>`
- det kun den rå sidecar indeholder: hver simulationsrames position mellem rækkerne, hændelserne Pause, Sim, CrashReset, PositionChanged og FlightSaved, en definition simulatoren afkortede (én variabel den ikke kendte: blokken læses så ikke efter navn); meta.json's `requests` lister hver definitions variabler og enheder i rækkefølge, så nyttelasterne kan læses uden dette modul
  
**Ikke tilgængeligt**

- andre fly (AI-trafik, andre spillere online): SimConnect_RequestDataOnSimObjectType ville spørge hvert fly i en radius - mere belastning på simulatoren, og andre spilleres flyvninger
- bevægelsesblokken hver simulationsramme: den bedes om hver sjette ramme (cirka 10 Hz, rækkernes hastighed), hvilket holder det rå feed nær en femtedel af størrelsen; positionsblokken er hver ramme
- de tusindvis af andre simulationsvariabler (radioer, lys, hver motors målere, fejl): en definition indeholder det, den beder om; listerne beder om flyvningen, flyets tilstand og simulatorens tid
- vejrobservationer, faciliteter (lufthavne, VOR'er), klientdata fra tilføjelser: separate forespørgsler, ikke lavet

**Størrelse**: cirka 30-55 MB i timen før zstd: positionsblokken hver simulationsramme (cirka 200 bytes med sin ramme, 30-60 i sekundet), bevægelsesblokken cirka 10 Hz (cirka 240 bytes), tilstandsblokken én gang i sekundet; zstd formindsker decimaltallene flere gange

## Verificeret {#verified}

meddelelsesafkodning testet på buffere bygget ud fra SimConnect.h's layouts; den live SimConnect-forbindelse er utestet

## Kilde {#source}

[heat3d_watch/adapters/msfs.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/msfs.py)

<!-- Generated from the adapter by tools/gen_game_pages.py; change the adapter and run it again rather than editing this page. -->
