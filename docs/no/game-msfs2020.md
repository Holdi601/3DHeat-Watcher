---
title: "Microsoft Flight Simulator 2020 (direkte data)"
nav_order: 31
lang: "no"
source: game-msfs2020.md
source_hash: "9b9e8389114b"
nav_exclude: true
search_exclude: true
---
# Microsoft Flight Simulator 2020 (direkte data) {#microsoft-flight-simulator-2020-live-data}

Mens du spiller Microsoft Flight Simulator 2020, lagrer watcheren dataene spillet selv sender ut, slik at du senere kan se på dem på et kart i 3DHeat-vieweren.

*Tekniske detaljer: adapter `msfs2020`, type [`telemetry`](sources-and-rules.md); den kjører mens `FlightSimulator.exe` går og ser etter nye data hvert 0,1 s.*

## Hva som tas opp {#what-is-recorded}

- eget flys posisjon i hver simuleringsramme, tatt 10 ganger i sekundet (breddegrad/lengdegrad/høyde som meter øst/opp/nord fra den første fixen; lat/lon/alt tatt vare på som kolonner)
- stilling, indikert flyhastighet, bakkehastighet, AGL, g, på bakken; sann flyhastighet, Mach, vertikal hastighet, AoA, sideglidning, magnetisk kurs, kroppshastigheter, akselerasjoner og rotasjonshastigheter omtrent 10 ganger i sekundet
- vekt, drivstoff, klaffer, understell, spoilere, parkeringsbrems, autopilot, gass, turtall, vær, simuleringshastighet, tid og kamerastatus én gang i sekundet; flyets tittel og ATC-type, modell og id
- start, landinger, krasj, flyvninger startet og stoppet (session_start/session_end)
- flytid, tid i luften, distanse, høyeste høyde, høyeste g, landinger
- hver SimConnect-melding, hel, i heat.raw.parquet

## Hvor det kommer fra {#where-it-comes-from}

SimConnect gjennom spillerens egen SimConnect.dll (simulatormappen, eller %MSFS_SDK%\SimConnect SDK\lib)

## Slik slår du det på {#how-to-switch-it-on}

ingenting; SimConnect.dll følger med MSFS 2020 (eller MSFS SDK)

## Slik fungerer det {#how-it-works}

Microsoft Flight Simulator 2020 og 2024: SimConnect, gjennom spillerens egen SimConnect.dll.

SimConnect er simulatorens publiserte klient-API (SDK-dokumentasjonen: <https://docs.flightsimulator.com/html/Programming_Tools/SimConnect/SimConnect_SDK.htm>, <https://docs.flightsimulator.com/msfs2024/html/6_Programming_APIs/SimConnect/SimConnect_SDK.htm>). Watcheren leverer ikke DLL-en selv: den laster den som fulgte med simulatoren eller dens SDK - MSFS 2020 legger `SimConnect.dll` i installasjonsmappen sin; MSFS 2024 på Steam leverer bare sin interne, så 2024-spillere installerer MSFS 2024 SDK (`<SDK>\SimConnect SDK\lib\SimConnect.dll`; 2024-simulatoren godtar også 2020-klienter).

Kallene, fra SimConnect.h, returnerer alle en HRESULT (0 = S_OK):

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

Hver melding starter med SIMCONNECT_RECV {DWORD dwSize, dwVersion, dwID} (#pragma pack 1). De som leses her:

```text
1  EXCEPTION       dwException, dwSendID, dwIndex
2  OPEN            szApplicationName[256], then version DWORDs
3  QUIT            the sim is closing
4  EVENT           uGroupID, uEventID, dwData
6  EVENT_FILENAME  EVENT + szFileName[260], dwFlags        (FlightLoaded)
8  SIMOBJECT_DATA  dwRequestID, dwObjectID, dwDefineID, dwFlags, dwentrynumber,
                   dwoutof, dwDefineCount, then the values (FLOAT64 each here)
```

Simuleringsvariabler (med enhetene det spørres om, så ingen omregning trengs): PLANE LATITUDE/LONGITUDE (grader), PLANE ALTITUDE (meter, over havet), PLANE ALT ABOVE GROUND (meter), PLANE PITCH/BANK DEGREES og PLANE HEADING DEGREES TRUE (grader; SimConnects egne fortegn - nesen opp er negativ stigning), AIRSPEED INDICATED og GROUND VELOCITY (knop), G FORCE (gforce), SIM ON GROUND (bool). Systemhendelser: SimStart, SimStop, Crashed, FlightLoaded, AircraftLoaded, Pause, CrashReset, PositionChanged, FlightSaved, Sim.

Tre flere datadefinisjoner ber om resten av flygningen (`MOTION_VARS`, hver sjette simuleringsramme), flyets tregere tilstand (`STATE_VARS`, én gang i sekundet) og navnene (`NAME_VARS`, 256-byte strenger, når de endrer seg); hver er sin egen definisjon, så en variabel en simuleringsversjon ikke kjenner, koster bare den blokken. Hver melding tas vare på hel i øktens rå sidefil.

Posisjoner havner i det samme flate kartet som X-Planes (x øst, y høyde, z nord i meter fra øktens første fix); den fixen er øktens `geo`, i meta.json og tabellens footer.

Samme modul brukes også av: [Microsoft Flight Simulator 2024 (direkte data)](game-msfs2024.md).

## Posisjoner og akser {#positions-and-axes}

| | |
|---|---|
| Posisjoner registreres | ja |
| Opp-akse | `y` |
| Enheter | meter (øst, høyde, nord fra den første fixen) |
| Speilet for visningen | `z` |
| Enhetsskala (`scale`: visningen ganger posisjonene med den) | 1 |

Disse havner i hver økts `meta.json` (`axes`) og, når økten har posisjoner, i `heat.parquet`s footer, slik at 3DHeat-vieweren snur og skalerer radene selv - se [Dataene](the-data.md).

## Flerspiller {#multiplayer}

- Merket som spilt på nett (`multiplayer`): **ja**. `games --markdown` viser dette som "allowed (reads only what the game publishes)".
- Type `telemetry`: den leser bare det spillet eller plattformen gir ut (en UDP-port eller delt minne som spillet publiserer), så den tar opp også i nettspill, både på nett og offline; flagget avgjør bare om minnet noen gang kan leses.
- Minne: **aldri** lest av denne adapteren. Bare `memory`-adaptere leser minne, og aldri for et spill som er merket som spilt på nett - se [Kilder og regler](sources-and-rules.md).

## Statistikk som registreres {#statistics-recorded}

Statistikknøkler som denne adapterens kode setter med navn (hver økts `stats` i `meta.json` og tabellen `stats` i `watcher.sqlite`):

`airborne_time`, `bad_packets`, `crashes`, `distance_km`, `flight_time`, `max_altitude_m`, `max_g`, `{event}s`

En nøkkel i klammer fylles ut ved kjøretid (`score.{team}` er én nøkkel per lag). Nøkler som koden henter fra en tabell over spillets felt eller fra spillets egne statistikknavn står ikke i denne listen; "Hva som tas opp" over nevner dem.

## Fullstendighet {#completeness}

Watcheren følger 3DHeats [konverteringsregel](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md): det kilden inneholder, leses eller tas vare på, og slettes aldri. I tillegg til radene tas hver pakke, side, linje eller svar adapteren mottar, vare på hel i øktens `heat.raw.parquet` (kolonnene `time`, `ms`, `type`, `used`, `payload`, `text`, pluss felt som tas vare på med navn; `used` markerer det som også ble til rader), og `selfCheck.completeness` i `meta.json` teller hver `type` - `lost` er 0.

**Leses**

- SIMOBJECT_DATA for posisjonsdefinisjonen (hver simuleringsramme): breddegrad, lengdegrad, høyde, AGL, stigning, rulling, sann kurs, IAS, bakkehastighet, g, på bakken - pollens siste ramme som en rad, hver ramme for landinger og avganger
- SIMOBJECT_DATA for bevegelsesdefinisjonen (omtrent 10 Hz: TAS, Mach, vertikal hastighet, AoA, sideglidning, magnetisk kurs, kroppshastighet, akselerasjon og rotasjonshastighet på tre akser) og for tilstandsdefinisjonen (1 Hz: vekter, drivstoff, klaffer, understell, spoilere, parkeringsbrems, autopilot, motorer, gass og turtall, utetemperatur, vind, havnivåtrykk, simuleringshastighet, zulu- og lokaltid, kamerastatus) inn på radene som sist mottatt
- SIMOBJECT_DATA for navnedefinisjonen (tittel, ATC-type, modell og id) inn i meta.json og radenes `aircraft`; OPEN (program og versjon) inn i meta.json
- EVENT og EVENT_FILENAME: SimStart, SimStop, Crashed, FlightLoaded (flyfilen) og AircraftLoaded (flyfilen for flyet) som flyvninger, krasj og meta.json
- QUIT avslutter økten

**Tatt vare på rått**

- hver melding SimConnect gir watcheren, hel som `payload`, under sitt SIMCONNECT_RECV_ID-navn: `SIMOBJECT_DATA`, `EVENT`, `EVENT_FILENAME`, `OPEN`, `QUIT`, `EXCEPTION` (en variabel eller hendelse simulatoren ikke godtok, med send-id og indeks), alle andre id-er etter navn eller `RECV_<id>`
- det bare den rå sidefilen har: hver simuleringsramme sin posisjon mellom radene, hendelsene Pause, Sim, CrashReset, PositionChanged og FlightSaved, en definisjon simulatoren kuttet av (én variabel den ikke kjente: blokken leses da ikke med navn); meta.json sin `requests` lister hver definisjons variabler og enheter i rekkefølge, så nyttelastene kan leses uten denne modulen
  
**Ikke tilgjengelig**

- andre fly (AI-trafikk, andre spillere på nett): SimConnect_RequestDataOnSimObjectType ville spørre hvert fly i en radius - mer belastning på simulatoren, og andre spilleres flygninger
- bevegelsesblokken i hver simuleringsramme: den spørres hver sjette ramme (omtrent 10 Hz, radenes frekvens), noe som holder den rå strømmen nær en femtedel av størrelsen; posisjonsblokken er fortsatt i hver ramme
- de tusenvis av andre simuleringsvariablene (radioer, lys, hver motors målere, feil): en definisjon holder det den ber om; listene ber om flyet, flyets tilstand og simuleringens tid
- værobservasjoner, fasiliteter (flyplasser, VOR-er), klientdata fra tillegg: egne forespørsler, ikke gjort

**Størrelse**: omtrent 30-55 MB per time før zstd: posisjonsblokken i hver simuleringsramme (omtrent 200 byte med sin ramme, 30-60 i sekundet), bevegelsesblokken omtrent 10 Hz (omtrent 240 byte), tilstandsblokken én gang i sekundet; zstd krymper dobbelttallene flere ganger

## Verifisert {#verified}

meldingsdekoding testet på buffere bygget fra SimConnect.h sine oppsett; den direkte SimConnect-forbindelsen er ikke testet

## Kilde {#source}

[heat3d_watch/adapters/msfs.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/msfs.py)

<!-- Generated from the adapter by tools/gen_game_pages.py; change the adapter and run it again rather than editing this page. -->
