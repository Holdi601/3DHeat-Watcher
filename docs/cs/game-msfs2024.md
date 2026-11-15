---
title: "Microsoft Flight Simulator 2024 (živá data)"
nav_order: 32
lang: "cs"
source: game-msfs2024.md
source_hash: "011c18a23252"
nav_exclude: true
search_exclude: true
---
# Microsoft Flight Simulator 2024 (živá data) {#microsoft-flight-simulator-2024-live-data}

Když hrajete Microsoft Flight Simulator 2024, Watcher ukládá data, která samotný simulátor vysílá, abyste se na ně mohli později podívat na mapě v prohlížeči 3DHeat.

*Technické podrobnosti: adaptér `msfs2024`, druh [`telemetry`](sources-and-rules.md); běží, dokud běží `FlightSimulator2024.exe`, a hledá nová data každých 0,1 s.*

## Co se zaznamenává {#what-is-recorded}

- pozice vlastního letadla v každém snímku simulace, brána 10krát za sekundu (zeměpisná šířka/délka/výška jako metry na východ/nahoru/na sever od prvního určení; zeměpisná šířka/délka/výška uložené jako sloupce)
- orientace, indikovaná rychlost vzduchem, pozemní rychlost, AGL, g, na zemi; pravá rychlost vzduchem, Mach, vertikální rychlost, AoA, skluz, magnetický kurz, rychlosti těla, zrychlení a rychlosti otáčení přibližně 10krát za sekundu
- hmotnost, palivo, klapky, podvozek, spoilery, parkovací brzda, autopilot, plyn, otáčky, počasí, rychlost simulace, čas a stav kamery jednou za sekundu; název letadla a typ, model a id ATC
- vzlety, přistání, havárie, začaté a ukončené lety (session_start/session_end)
- doba letu, doba ve vzduchu, vzdálenost, nejvyšší výška, nejvyšší g, přistání
- každá zpráva SimConnect uchovaná celá v heat.raw.parquet

## Odkud to pochází {#where-it-comes-from}

SimConnect přes vlastní SimConnect.dll hráče (složka simulátoru, nebo %MSFS2024_SDK%\SimConnect SDK\lib)

## Jak to zapnout {#how-to-switch-it-on}

nic v simulátoru; potřebuje SimConnect.dll – MSFS 2020 ho má ve své složce, hráči MSFS 2024 instalují SDK MSFS 2024

## Jak to funguje {#how-it-works}

Microsoft Flight Simulator 2020 a 2024: SimConnect, přes vlastní SimConnect.dll hráče.

SimConnect je zveřejněné klientské API simulátoru (dokumentace SDK:
<https://docs.flightsimulator.com/html/Programming_Tools/SimConnect/SimConnect_SDK.htm>,
<https://docs.flightsimulator.com/msfs2024/html/6_Programming_APIs/SimConnect/SimConnect_SDK.htm>).
Watcher DLL nedodává: načte tu, která přišla se simulátorem nebo jeho SDK – MSFS 2020 ji dává do své instalační složky `SimConnect.dll`; MSFS 2024 na Steamu dodává jen svou interní, takže hráči 2024 instalují SDK MSFS 2024
(`<SDK>\SimConnect SDK\lib\SimConnect.dll`; simulátor 2024 přijímá i klienty 2020).

Volání z SimConnect.h, všechna vracejí HRESULT (0 = S_OK):

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

Každá zpráva začíná SIMCONNECT_RECV {DWORD dwSize, dwVersion, dwID}
(#pragma pack 1). Tady čtené:

```text
1  EXCEPTION       dwException, dwSendID, dwIndex
2  OPEN            szApplicationName[256], then version DWORDs
3  QUIT            the sim is closing
4  EVENT           uGroupID, uEventID, dwData
6  EVENT_FILENAME  EVENT + szFileName[260], dwFlags        (FlightLoaded)
8  SIMOBJECT_DATA  dwRequestID, dwObjectID, dwDefineID, dwFlags, dwentrynumber,
                   dwoutof, dwDefineCount, then the values (FLOAT64 each here)
```

Simulační proměnné (jednotky se žádají tak, aby nebylo nutné převádět): PLANE
LATITUDE/LONGITUDE (stupně), PLANE ALTITUDE (metry nad hladinou moře), PLANE
ALT ABOVE GROUND (metry), PLANE PITCH/BANK DEGREES a PLANE HEADING DEGREES
TRUE (stupně; vlastní znaménka SimConnect – nos nahoru je záporný sklon), AIRSPEED
INDICATED a GROUND VELOCITY (uzly), G FORCE (gforce), SIM ON GROUND (bool).
Systémové události: SimStart, SimStop, Crashed, FlightLoaded, AircraftLoaded,
Pause, CrashReset, PositionChanged, FlightSaved, Sim.

Tři další datové definice žádají zbytek letu (`MOTION_VARS`,
každý šestý snímek simulace), pomalejší stav letadla (`STATE_VARS`, jednou za sekundu)
a jeho názvy (`NAME_VARS`, řetězce 256 bajtů, když se změní); každá je vlastní
definice, takže proměnná, kterou jedna verze simulátoru nezná, stojí jen ten blok.
Každá zpráva se uchová celá ve vedlejším surovém souboru relace.

Pozice jdou do stejné ploché mapy jako u X-Plane (x východ, y výška nad hladinou moře, z sever,
v metrech od prvního určení relace); to určení je `geo` relace, v meta.json a v patičce tabulky.

Stejný modul slouží také: [Microsoft Flight Simulator 2020 (živá data)](game-msfs2020.md).

## Pozice a osy {#positions-and-axes}

| | |
|---|---|
| Zaznamenané pozice | ano |
| Osa nahoru | `y` |
| Jednotky | metry (východ, výška, sever od prvního určení) |
| Zrcadleno pro prohlížeč | `z` |
| Měřítko jednotek (`scale`: prohlížeč pozice tímto násobí) | 1 |

Tyto hodnoty se zapisují do `meta.json` každé relace (`axes`) a, když relace má pozice, do patičky `heat.parquet`, takže prohlížeč 3DHeat otáčí a měřítkuje řádky sám – viz [Data](the-data.md).

## Více hráčů {#multiplayer}

- Označeno jako hraná online (`multiplayer`): **ano**. `games --markdown` to ukáže jako „povoleno (čte jen to, co hra zveřejňuje)“.
- Druh `telemetry`: čte jen to, co hra nebo platforma vydává (UDP port nebo sdílená paměť, kterou hra zveřejňuje), takže nahrává i v online hře, stejně jako offline; příznak rozhoduje jen o tom, zda se smí číst paměť.
- Paměť: tento adaptér ji **nikdy** nečte. Paměť čtou jen adaptéry `memory` a nikdy u hry označené jako hraná online – viz [Zdroje a pravidla](sources-and-rules.md).

## Zaznamenané statistiky {#statistics-recorded}

Klíče statistik, které kód tohoto adaptéru nastavuje podle jména (každé relace `stats` v `meta.json` a tabulka `stats` v `watcher.sqlite`):

`airborne_time`, `bad_packets`, `crashes`, `distance_km`, `flight_time`, `max_altitude_m`, `max_g`, `{event}s`

Klíč ve složených závorkách se doplní za běhu (`score.{team}` je jeden klíč na každý tým). Klíče, které kód bere z tabulky polí hry nebo z jejích vlastních názvů statistik, v tomto seznamu nejsou; výše v „Co se zaznamenává“ jsou uvedené jménem.

## Úplnost {#completeness}

Watcher dodržuje [pravidlo převodníků](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md) 3DHeat: co zdroj obsahuje, se načte nebo uchová, nikdy se nezahodí. Kromě řádků se každý paket, stránka, řádek nebo odpověď, kterou adaptér dostane, uchovává celý v `heat.raw.parquet` relace (sloupce `time`, `ms`, `type`, `used`, `payload`, `text` a případná pole uchovaná podle jména; `used` označuje, co se také stalo řádky), a `selfCheck.completeness` v `meta.json` počítá každý `type` – `lost` je 0.

**Načteno**

- SIMOBJECT_DATA definice pozice (každý snímek simulace): zeměpisná šířka, délka, výška, AGL, sklon, náklon, pravý kurz, IAS, pozemní rychlost, g, na zemi – poslední snímek dotazu jako řádek, každý snímek pro dotyky a vzlety
- SIMOBJECT_DATA definice pohybu (asi 10krát za sekundu: TAS, Mach, vertikální rychlost, AoA, skluz, magnetický kurz, rychlost těla, zrychlení a rychlost otáčení na třech osách) a definice stavu (1 Hz: hmotnosti, palivo, klapky, podvozek, spoilery, parkovací brzda, autopilot, motory, plyn a otáčky, venkovní teplota, vítr, tlak na hladině moře, rychlost simulace, zulu a místní čas, stav kamery) do řádků, jak přišly naposledy
- SIMOBJECT_DATA definice názvů (název, typ ATC, model a id) do meta.json a `aircraft` v řádcích; OPEN (aplikace a verze) do meta.json
- EVENT a EVENT_FILENAME: SimStart, SimStop, Crashed, FlightLoaded (soubor letu) a AircraftLoaded (soubor letadla) jako lety, havárie a meta.json
- QUIT ukončí relace

**Uchováno surové**

- každá zpráva, kterou SimConnect Watcheru předá, celá jako `payload`, pod názvem svého SIMCONNECT_RECV_ID: `SIMOBJECT_DATA`, `EVENT`, `EVENT_FILENAME`, `OPEN`, `QUIT`, `EXCEPTION` (proměnná nebo událost, které simulátor nepřijal, s id odeslání a indexem), jakékoli jiné id podle jména nebo `RECV_<id>`
- co drží jen surový vedlejší soubor: pozice každého snímku simulace mezi řádky, události Pause, Sim, CrashReset, PositionChanged a FlightSaved, definice, kterou simulátor zkrátil (jedna proměnná, kterou neznal: blok se pak podle jména nečte); `requests` v meta.json vypisuje každou definici s jejími proměnnými a jednotkami v pořadí, takže se payloady dají číst i bez tohoto modulu

**Nedostupné**

- ostatní letadla (provoz AI, ostatní hráči online): SimConnect_RequestDataOnSimObjectType by dotazoval každé letadlo v okruhu – větší zátěž simulátoru a cizí lety
- blok pohybu v každém snímku simulace: žádá se každý šestý snímek (asi 10 Hz, rychlost řádků), což drží surový proud zhruba na pětině; blok pozice zůstává v každém snímku
- tisíce dalších simulačních proměnných (rádia, světla, každý ukazatel motoru, poruchy): definice drží jen to, co žádá; seznamy žádají let, stav letadla a čas simulace
- pozorování počasí, zařízení (letiště, VOR), klientská data doplňků: samostatné dotazy, nedělají se

**Velikost**: asi 30–55 MB za hodinu před zstd: blok pozice v každém snímku (asi 200 bajtů i s rámcem, 30–60 za sekundu), blok pohybu asi 10krát za sekundu (asi 240 bajtů), blok stavu jednou za sekundu; zstd zmenší čísla s plovoucí desetinnou čárkou několikrát

## Ověřeno {#verified}

dekódování zpráv testováno na bufferech postavených podle rozložení SimConnect.h; živé spojení SimConnect neotestováno

## Zdroj {#source}

[heat3d_watch/adapters/msfs.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/msfs.py)

<!-- Vygenerováno z adaptéru nástrojem tools/gen_game_pages.py; změňte adaptér a spusťte ho znovu, místo úprav této stránky. -->
