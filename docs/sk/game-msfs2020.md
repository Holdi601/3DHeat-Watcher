---
title: "Microsoft Flight Simulator 2020 (živé dáta)"
nav_order: 31
lang: "sk"
source: game-msfs2020.md
source_hash: "9b9e8389114b"
nav_exclude: true
search_exclude: true
---
# Microsoft Flight Simulator 2020 (živé dáta) {#microsoft-flight-simulator-2020-live-data}

Keď hráte Microsoft Flight Simulator 2020, watcher ukladá dáta, ktoré samotná hra vysiela, aby ste si ich neskôr mohli pozrieť na mape vo vieweri 3DHeat.

*Technické podrobnosti: adaptér `msfs2020`, druh [`telemetry`](sources-and-rules.md); beží, kým beží `FlightSimulator.exe`, a hľadá nové dáta každých 0,1 s.*

## Čo sa zaznamenáva {#what-is-recorded}

- pozícia vlastného lietadla pri každom snímku simulácie, brané 10-krát za sekundu (zemepisná šírka/dĺžka/výška ako metre východ/výška/sever od prvého určenia polohy; zemepisná šírka, dĺžka a výška uchované ako stĺpce)
- postoj, indikovaná rýchlosť, pozemná rýchlosť, AGL, g, na zemi; skutočná rýchlosť, Mach, vertikálna rýchlosť, uhol náklonu, uhol bočného sklzu, magnetický kurz, rýchlosti telesa, zrýchlenia a rýchlosti otáčania približne 10-krát za sekundu
- hmotnosť, palivo, klapky, podvozok, spoilery, parkovacia brzda, autopilot, plyn, otáčky, počasie, rýchlosť simulácie, čas a stav kamery raz za sekundu; názov lietadla, typ ATC, model a id
- vzlety, pristátia, havárie, začaté a ukončené lety (session_start/session_end)
- čas letu, čas vo vzduchu, vzdialenosť, najvyššia výška, najvyššie g, pristátia
- každá správa SimConnect, uchovaná celá v heat.raw.parquet

## Odkiaľ to pochádza {#where-it-comes-from}

SimConnect cez vlastný SimConnect.dll hráča (priečinok simulátora, alebo %MSFS_SDK%\SimConnect SDK\lib)

## Ako to zapnúť {#how-to-switch-it-on}

nič; SimConnect.dll je súčasťou MSFS 2020 (alebo MSFS SDK)

## Ako to funguje {#how-it-works}

Microsoft Flight Simulator 2020 a 2024: SimConnect, cez vlastný SimConnect.dll hráča.

SimConnect je zverejnené klientske API simulátora (dokumentácia SDK:
<https://docs.flightsimulator.com/html/Programming_Tools/SimConnect/SimConnect_SDK.htm>,
<https://docs.flightsimulator.com/msfs2024/html/6_Programming_APIs/SimConnect/SimConnect_SDK.htm>).
Watcher DLL neobsahuje: načíta ten, ktorý prišiel so simulátorom alebo jeho SDK – MSFS 2020 má `SimConnect.dll` vo svojom inštalačnom priečinku; MSFS 2024 zo Steamu obsahuje len svoj interný, takže hráči 2024 inštalujú SDK MSFS 2024 (`<SDK>\SimConnect SDK\lib\SimConnect.dll`; simulátor 2024 prijíma aj klienty 2020).

Volania z SimConnect.h, všetky vracajú HRESULT (0 = S_OK):

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

Každá správa začína SIMCONNECT_RECV {DWORD dwSize, dwVersion, dwID}
(#pragma pack 1). Tieto sa tu čítajú:

```text
1  EXCEPTION       dwException, dwSendID, dwIndex
2  OPEN            szApplicationName[256], then version DWORDs
3  QUIT            the sim is closing
4  EVENT           uGroupID, uEventID, dwData
6  EVENT_FILENAME  EVENT + szFileName[260], dwFlags        (FlightLoaded)
8  SIMOBJECT_DATA  dwRequestID, dwObjectID, dwDefineID, dwFlags, dwentrynumber,
                   dwoutof, dwDefineCount, then the values (FLOAT64 each here)
```

Premenné simulácie (požadované jednotky, takže netreba žiadny prepočet): PLANE
LATITUDE/LONGITUDE (stupne), PLANE ALTITUDE (metre, nad morom), PLANE
ALT ABOVE GROUND (metre), PLANE PITCH/BANK DEGREES a PLANE HEADING DEGREES
TRUE (stupne; vlastné znamienka SimConnect – nos nahor je záporný pitch), AIRSPEED
INDICATED a GROUND VELOCITY (uzly), G FORCE (gforce), SIM ON GROUND (bool).
Systémové udalosti: SimStart, SimStop, Crashed, FlightLoaded, AircraftLoaded,
Pause, CrashReset, PositionChanged, FlightSaved, Sim.

Tri ďalšie definície údajov žiadajú zvyšok letu (`MOTION_VARS`,
každý šiesty snímok simulácie), pomalší stav lietadla (`STATE_VARS`, raz za sekundu)
a jeho názvy (`NAME_VARS`, 256-bajtové reťazce, keď sa zmenia); každá je
vlastnou definíciou, takže premenná, ktorú jedna verzia simulácie nepozná, stojí
len ten blok. Každá správa sa uchová celá v surovom sprievodnom súbore relácie.

Pozície idú do rovnakej plochej mapy ako pri X-Plane (x východ, y výška, z sever
v metroch od prvého určenia polohy v tomto sedení); to určenie je `geo` relácie, v meta.json a päte tabuľky.

Rovnaký modul slúži aj: [Microsoft Flight Simulator 2024 (živé dáta)](game-msfs2024.md).

## Pozície a osi {#positions-and-axes}

| | |
|---|---|
| Pozície sa zaznamenávajú | áno |
| Os nahor | `y` |
| Jednotky | metre (východ, výška, sever od prvého určenia polohy) |
| Zrkadlené pre viewer | `z` |
| Mierka (`scale`: viewer pozície násobí týmto číslom) | 1 |

Tieto hodnoty idú do `meta.json` každej relácie (`axes`) a, ak relácia obsahuje pozície, do päty `heat.parquet`, takže viewer 3DHeat riadky otáča a mení mierku sám – pozrite [Dáta](the-data.md).

## Viachráčová hra {#multiplayer}

- Označené ako hraná online (`multiplayer`): **áno**. `games --markdown` to zobrazí ako „povolené (číta len to, čo hra zverejňuje)“.
- Druh `telemetry`: číta len to, čo hra alebo platforma vydáva (UDP port alebo zdieľaná pamäť, ktorú hra zverejňuje), takže zaznamenáva aj online hru, aj offline; príznak rozhoduje len o tom, či sa smie čítať pamäť.
- Pamäť: tento adaptér ju **nikdy** nečíta. Pamäť čítajú len adaptéry `memory` a nikdy pre hru označenú ako hranú online – pozrite [Pravidlá a zdroje](sources-and-rules.md).

## Zaznamenané štatistiky {#statistics-recorded}

Štatistické kľúče, ktoré kód tohto adaptéra nastavuje podľa názvu (`stats` každej relácie v `meta.json` a tabuľka `stats` v `watcher.sqlite`):

`airborne_time`, `bad_packets`, `crashes`, `distance_km`, `flight_time`, `max_altitude_m`, `max_g`, `{event}s`

Kľúč v zložených zátvorkách sa doplní až za behu (`score.{team}` je jeden kľúč pre každý tím). Kľúče, ktoré kód berie z tabuľky polí hry alebo z vlastných názvov štatistík hry, v tomto zozname nie sú; „Čo sa zaznamenáva“ vyššie ich uvádza.

## Úplnosť {#completeness}

Watcher sa riadi [pravidlom konvertorov](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md) 3DHeat: čo zdroj obsahuje, sa prečíta alebo uchová, nikdy sa nezahodí. Okrem riadkov sa každý paket, stránka, riadok alebo odpoveď, ktorú adaptér dostane, uchová celý v `heat.raw.parquet` relácie (stĺpce `time`, `ms`, `type`, `used`, `payload`, `text` a potom každé pole, ktoré sa podľa názvu ponechalo; `used` označuje, čo sa stalo aj riadkami), a `selfCheck.completeness` v `meta.json` počíta každý `type` – `lost` je 0.

**Prečítané**

- SIMOBJECT_DATA definície pozície (pri každom snímku simulácie): zemepisná šírka, dĺžka, výška, AGL, pitch, náklon, pravý kurz, IAS, pozemná rýchlosť, g, na zemi – posledný snímok dopytu ako riadok, každý snímok pri dotykoch a vzletoch
- SIMOBJECT_DATA definície pohybu (asi 10 Hz: TAS, Mach, vertikálna rýchlosť, uhol náklonu, uhol bočného sklzu, magnetický kurz, rýchlosť telesa, zrýchlenie a rýchlosť otáčania na troch osiach) a definície stavu (1 Hz: hmotnosti, palivo, klapky, podvozok, spoilery, parkovacia brzda, autopilot, motory, plyn a otáčky, vonkajšia teplota, vietor, tlak na hladine mora, rýchlosť simulácie, zulu a miestny čas, stav kamery) na riadky, ako sa naposledy prijali
- SIMOBJECT_DATA definície názvov (názov, typ ATC, model a id) do meta.json a do `aircraft` riadkov; OPEN (aplikácia a verzia) do meta.json
- EVENT a EVENT_FILENAME: SimStart, SimStop, Crashed, FlightLoaded (súbor letu) a AircraftLoaded (súbor lietadla) ako lety, havárie a meta.json
- QUIT ukončí reláciu

**Uchované surové**

- každá správa, ktorú SimConnect dá watcheru, celá ako `payload`, pod názvom jej SIMCONNECT_RECV_ID: `SIMOBJECT_DATA`, `EVENT`, `EVENT_FILENAME`, `OPEN`, `QUIT`, `EXCEPTION` (premenná alebo udalosť, ktorú simulátor neprijal, s id odoslania a indexom), každé iné id podľa názvu alebo `RECV_<id>`
- čo drží len surový sprievodný súbor: každá pozícia snímku simulácie medzi riadkami, udalosti Pause, Sim, CrashReset, PositionChanged a FlightSaved, definícia, ktorú simulátor skrátil (jedna premenná, ktorú nepoznal: blok sa potom nečíta podľa názvu); `requests` v meta.json vypisuje každú definíciu s jej premennými a jednotkami v poradí, takže sa payloady dajú čítať aj bez tohto modulu

**Nie je k dispozícii**

- iné lietadlá (AI doprava, iní hráči online): SimConnect_RequestDataOnSimObjectType by dopytoval každé lietadlo v okruhu – väčšia záťaž simulátora a lety iných hráčov
- blok pohybu pri každom snímku simulácie: žiada sa každý šiesty snímok (asi 10 Hz, tempo riadkov), čo drží surový tok asi na pätine veľkosti; blok pozície zostáva pri každom snímku
- tisícky ďalších premenných simulácie (rádiá, svetlá, každý ukazovateľ motora, poruchy): definícia drží len to, čo žiada; zoznamy žiadajú let, stav lietadla a čas simulácie
- pozorovania počasia, zariadenia (letiská, VOR), dáta doplnkov: samostatné dopyty, nerobia sa

**Veľkosť**: asi 30–55 MB za hodinu pred zstd: blok pozície pri každom snímku simulácie (asi 200 bajtov s rámcom, 30–60 za sekundu), blok pohybu asi 10 Hz (asi 240 bajtov), blok stavu raz za sekundu; zstd zmenší double-hodnoty niekoľkonásobne

## Overené {#verified}

dekódovanie správ testované na bufferoch postavených podľa rozložení zo SimConnect.h; živé pripojenie SimConnect netestované

## Zdroj {#source}

[heat3d_watch/adapters/msfs.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/msfs.py)

<!-- Generated from the adapter by tools/gen_game_pages.py; change the adapter and run it again rather than editing this page. -->
