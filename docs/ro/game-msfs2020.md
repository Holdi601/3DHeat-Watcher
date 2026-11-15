---
title: "Microsoft Flight Simulator 2020 (date în timp real)"
nav_order: 31
lang: "ro"
source: game-msfs2020.md
source_hash: "9b9e8389114b"
nav_exclude: true
search_exclude: true
---
# Microsoft Flight Simulator 2020 (date în timp real) {#microsoft-flight-simulator-2020-live-data}

Cât joci Microsoft Flight Simulator 2020, watcher-ul salvează datele pe care jocul însuși le trimite afară, ca să te poți uita mai târziu la ele pe o hartă în vizualizatorul 3DHeat.

*Detalii tehnice: adaptorul `msfs2020`, tip [`telemetry`](sources-and-rules.md); rulează cât timp `FlightSimulator.exe` este pornit și caută date noi la fiecare 0,1 s.*

## Ce se înregistrează {#what-is-recorded}

- poziția propriei aeronave la fiecare cadru al simulatorului, luată la 10 Hz (latitudine/longitudine/altitudine ca metri est/sus/nord față de prima măsurătoare; lat/lon/alt păstrate ca coloane)
- atitudine, viteza indicată, viteza față de sol, AGL, g, la sol sau nu; viteza reală, Mach, viteza verticală, AoA, alunecarea, capul magnetic, vitezele pe axele corpului, accelerațiile și vitezele de rotație, la circa 10 Hz
- greutatea, combustibilul, flapsurile, trenul, spoilerele, frâna de parcare, pilotul automat, accelerația, turația, vremea, viteza simulării, timpul și starea camerei, o dată pe secundă; titlul aeronavei, tipul ATC, modelul și id-ul ei
- decolări, aterizări, prăbușiri, zboruri începute și oprite (session_start/session_end)
- timpul de zbor, timpul în aer, distanța, altitudinea cea mai mare, g-ul cel mai mare, aterizările
- fiecare mesaj SimConnect, păstrat integral în heat.raw.parquet

## De unde vine {#where-it-comes-from}

SimConnect prin propriul SimConnect.dll al jucătorului (folderul simulatorului, sau %MSFS_SDK%\SimConnect SDK\lib)

## Cum o pornești {#how-to-switch-it-on}

nimic; SimConnect.dll vine cu MSFS 2020 (sau cu SDK-ul MSFS)

## Cum funcționează {#how-it-works}

Microsoft Flight Simulator 2020 și 2024: SimConnect, prin propriul SimConnect.dll al jucătorului.

SimConnect este API-ul client publicat al simulatorului (documentația SDK: <https://docs.flightsimulator.com/html/Programming_Tools/SimConnect/SimConnect_SDK.htm>, <https://docs.flightsimulator.com/msfs2024/html/6_Programming_APIs/SimConnect/SimConnect_SDK.htm>). Watcher-ul nu livrează DLL-ul: încarcă pe cel care a venit cu simulatorul sau cu SDK-ul lui - MSFS 2020 pune `SimConnect.dll` în folderul de instalare; MSFS 2024 de pe Steam livrează doar pe cel intern, deci jucătorii de 2024 instalează SDK-ul MSFS 2024 (`<SDK>\SimConnect SDK\lib\SimConnect.dll`; simulatorul din 2024 acceptă și clienți din 2020).

Apelurile, din SimConnect.h, întorc toate un HRESULT (0 = S_OK):

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

Fiecare mesaj începe cu SIMCONNECT_RECV {DWORD dwSize, dwVersion, dwID} (#pragma pack 1). Cele citite aici:

```text
1  EXCEPTION       dwException, dwSendID, dwIndex
2  OPEN            szApplicationName[256], then version DWORDs
3  QUIT            the sim is closing
4  EVENT           uGroupID, uEventID, dwData
6  EVENT_FILENAME  EVENT + szFileName[260], dwFlags        (FlightLoaded)
8  SIMOBJECT_DATA  dwRequestID, dwObjectID, dwDefineID, dwFlags, dwentrynumber,
                   dwoutof, dwDefineCount, then the values (FLOAT64 each here)
```

Variabilele simulatorului (unitățile cerute, ca să nu fie nevoie de conversie): PLANE LATITUDE/LONGITUDE (grade), PLANE ALTITUDE (metri, deasupra nivelului mării), PLANE ALT ABOVE GROUND (metri), PLANE PITCH/BANK DEGREES și PLANE HEADING DEGREES TRUE (grade; semnele proprii ale SimConnect - nasul sus înseamnă pitch negativ), AIRSPEED INDICATED și GROUND VELOCITY (noduri), G FORCE (gforce), SIM ON GROUND (bool). Evenimente de sistem: SimStart, SimStop, Crashed, FlightLoaded, AircraftLoaded, Pause, CrashReset, PositionChanged, FlightSaved, Sim.

Trei definiții de date în plus cer restul zborului (`MOTION_VARS`, la fiecare a șasea cadru al simulatorului), starea mai lentă a aeronavei (`STATE_VARS`, o dată pe secundă) și numele ei (`NAME_VARS`, șiruri de 256 de octeți, când se schimbă); fiecare este o definiție proprie, deci o variabilă pe care o versiune a simulatorului nu o cunoaște costă doar acel bloc. Fiecare mesaj este păstrat integral în sidecar-ul brut al sesiunii.

Pozițiile intră în aceeași hartă plată ca cea a X-Plane (x est, y altitudine, z nord, în metri de la prima măsurătoare a zborului); acea primă măsurătoare este `geo` al sesiunii, în meta.json și în subsolul tabelului.

Același modul servește și: [Microsoft Flight Simulator 2024 (date în timp real)](game-msfs2024.md).

## Poziții și axe {#positions-and-axes}

| | |
|---|---|
| Poziții înregistrate | da |
| Axa în sus | `y` |
| Unități | metri (est, altitudine, nord față de prima măsurătoare) |
| Oglindită pentru vizualizator | `z` |
| Scara unității (`scale`: vizualizatorul înmulțește pozițiile cu ea) | 1 |

Acestea intră în `meta.json` al fiecărei sesiuni (`axes`) și, când sesiunea are poziții, în subsolul `heat.parquet`, așa că vizualizatorul 3DHeat rotește și scalează singur rândurile - vezi [Datele](the-data.md).

## Joc online {#multiplayer}

- Marcat ca jucat online (`multiplayer`): **da**. `games --markdown` arată asta ca „permis (citește doar ce publică jocul)”.
- Tip `telemetry`: citește doar ce scoate jocul sau platforma (un port UDP sau o memorie partajată publicată de joc), deci înregistrează și în jocul online, nu doar offline; steagul decide doar dacă memoria are voie să fie citită vreodată.
- Memorie: **niciodată** citită de acest adaptor. Doar adaptoarele `memory` citesc memoria, și niciodată pentru un joc marcat ca jucat online - vezi [Surse și reguli](sources-and-rules.md).

## Statistici înregistrate {#statistics-recorded}

Cheile de statistică pe care codul acestui adaptor le setează după nume (`stats` din `meta.json` al fiecărei sesiuni și tabelul `stats` din `watcher.sqlite`):

`airborne_time`, `bad_packets`, `crashes`, `distance_km`, `flight_time`, `max_altitude_m`, `max_g`, `{event}s`

O cheie între acolade se completează la rulare (`score.{team}` este câte o cheie pentru fiecare echipă). Cheile pe care codul le ia dintr-un tabel de câmpuri ale jocului sau din numele statisticilor jocului nu sunt în această listă; „Ce se înregistrează” de mai sus le numește.

## Completitudine {#completeness}

Watcher-ul urmează [regula de convertor](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md) a 3DHeat: ce are sursa este citit sau păstrat, niciodată aruncat. În afară de rânduri, fiecare pachet, pagină, linie sau răspuns pe care îl primește adaptorul este păstrat integral în `heat.raw.parquet` al sesiunii (coloanele `time`, `ms`, `type`, `used`, `payload`, `text`, apoi orice câmp păstrat după nume; `used` marchează ce a devenit și rând), iar `selfCheck.completeness` din `meta.json` numără fiecare `type` - `lost` este 0.

**Citit**

- SIMOBJECT_DATA al definiției de poziție (la fiecare cadru al simulatorului): latitudine, longitudine, altitudine, AGL, pitch, bank, cap adevărat, IAS, viteza față de sol, g, la sol - ultimul cadru al interogării ca rând, fiecare cadru pentru atingeri și decolări
- SIMOBJECT_DATA al definiției de mișcare (la circa 10 Hz: TAS, Mach, viteza verticală, AoA, alunecarea, capul magnetic, viteza pe axele corpului, accelerația și viteza de rotație pe trei axe) și al definiției de stare (1 Hz: greutăți, combustibil, flapsuri, tren, spoilere, frâna de parcare, pilotul automat, motoare, accelerație și turație, temperatura exterioară, vântul, presiunea la nivelul mării, viteza simulării, ora zulu și ora locală, starea camerei) pe rânduri, ca ultima primită
- SIMOBJECT_DATA al definiției de nume (titlu, tip ATC, model și id) în meta.json și în `aircraft` al rândurilor; OPEN (aplicația și versiunea) în meta.json
- EVENT și EVENT_FILENAME: SimStart, SimStop, Crashed, FlightLoaded (fișierul zborului) și AircraftLoaded (fișierul aeronavei) ca zboruri, prăbușiri și meta.json
- QUIT încheie sesiunea

**Păstrat brut**

- fiecare mesaj pe care îl trimite SimConnect watcher-ului, integral ca `payload`, sub numele lui SIMCONNECT_RECV_ID: `SIMOBJECT_DATA`, `EVENT`, `EVENT_FILENAME`, `OPEN`, `QUIT`, `EXCEPTION` (o variabilă sau un eveniment pe care simulatorul nu le-a acceptat, cu id-ul trimiterii și indexul), orice alt id după nume sau `RECV_<id>`
- ce are doar sidecar-ul brut: poziția fiecărui cadru al simulatorului între rânduri, evenimentele Pause, Sim, CrashReset, PositionChanged și FlightSaved, o definiție pe care simulatorul a scurtat-o (o variabilă pe care nu o cunoaște: blocul nu mai este citit după nume); `requests` din meta.json listează variabilele și unitățile fiecărei definiții, în ordine, ca payload-urile să se poată citi fără acest modul

**Nedisponibil**

- alte aeronave (trafic AI, alți jucători online): SimConnect_RequestDataOnSimObjectType ar interoga fiecare aeronavă dintr-o rază - mai multă încărcare pentru simulator și zborurile altor jucători
- blocul de mișcare la fiecare cadru al simulatorului: se cere la fiecare a șasea cadru (circa 10 Hz, rata rândurilor), ceea ce păstrează fluxul brut aproape la o cincime din mărime; blocul de poziție rămâne la fiecare cadru
- celelalte mii de variabile ale simulatorului (radiouri, lumini, cadranele fiecărui motor, defecțiuni): o definiție cuprinde ce cere; listele cer zborul, starea aeronavei și timpul simulatorului
- observații meteo, facilități (aeroporturi, VOR-uri), datele add-on-urilor: cereri separate, neefectuate

**Dimensiune**: circa 30-55 MB pe oră înainte de zstd: blocul de poziție la fiecare cadru al simulatorului (circa 200 de octeți cu cadrul lui, 30-60 pe secundă), blocul de mișcare la circa 10 Hz (circa 240 de octeți), blocul de stare o dată pe secundă; zstd micșorează dublele de câteva ori

## Verificat {#verified}

decodarea mesajelor testată pe buffere construite după layout-urile din SimConnect.h; conexiunea SimConnect live netestată

## Sursă {#source}

[heat3d_watch/adapters/msfs.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/msfs.py)

<!-- Generated from the adapter by tools/gen_game_pages.py; change the adapter and run it again rather than editing this page. -->
