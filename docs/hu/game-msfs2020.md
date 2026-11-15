---
title: "Microsoft Flight Simulator 2020 (élő adatok)"
nav_order: 31
lang: "hu"
source: game-msfs2020.md
source_hash: "9b9e8389114b"
nav_exclude: true
search_exclude: true
---
# Microsoft Flight Simulator 2020 (élő adatok) {#microsoft-flight-simulator-2020-live-data}

Miközben a Microsoft Flight Simulator 2020-at játszod, a watcher elmenti azokat az adatokat, amelyeket maga a játék küld ki, így később a 3DHeat megtekintőben egy térképen is megnézheted őket.

*Technikai részletek: adapter `msfs2020`, típus [`telemetry`](sources-and-rules.md); a `FlightSimulator.exe` futása alatt fut, és 0,1 másodpercenként keres új adatot.*

## Mit rögzít {#what-is-recorded}

- a saját repülőgép pozíciója minden szimulációs képkockánál, 10 Hz-cel vett mintákban (szélesség/hosszúság/magasság méterben kelet/magasság/észak irányban az első pozícióhoz képest; a szélesség, hosszúság és magasság oszlopokként megmaradnak)
- hozzáállás, műszerelt légsebesség, talajsebesség, AGL, g, a földön van-e; valódi légsebesség, Mach, emelkedési sebesség, támadási szög, oldalcsúszás, mágneses irány, test-sebességek, gyorsulások és forgási sebességek körülbelül 10 Hz-cel
- súly, üzemanyag, lapok, futómű, légfékek, parkolófék, autopilóta, gázkar, fordulatszám, időjárás, szimulációs sebesség, idő és kameraállapot másodpercenként; a repülőgép neve és ATC-típusa, modellje és azonosítója
- felszállások, leszállások, lezuhanások, elindított és leállított repülések (session_start/session_end)
- repülési idő, levegőben töltött idő, megtett táv, legnagyobb magasság, legnagyobb g, leszállások száma
- minden SimConnect-üzenet egészben a heat.raw.parquet-ban

## Honnan jön {#where-it-comes-from}

SimConnect a játékos saját SimConnect.dll-jén keresztül (a szimulátor mappája, vagy %MSFS_SDK%\SimConnect SDK\lib)

## Hogyan kapcsolható be {#how-to-switch-it-on}

semmit; a SimConnect.dll az MSFS 2020-szal jön (vagy az MSFS SDK-val)

## Hogyan működik {#how-it-works}

Microsoft Flight Simulator 2020 és 2024: SimConnect, a játékos saját SimConnect.dll-jén keresztül.

A SimConnect a szimulátor közzétett kliens-API-ja (SDK-dokumentáció:
<https://docs.flightsimulator.com/html/Programming_Tools/SimConnect/SimConnect_SDK.htm>,
<https://docs.flightsimulator.com/msfs2024/html/6_Programming_APIs/SimConnect/SimConnect_SDK.htm>).
A watcher nem szállítja a DLL-t: azt tölti be, amely a szimulátorral vagy annak SDK-jával érkezett – az MSFS 2020 a `SimConnect.dll`-t a telepítési mappájában tartja; az MSFS 2024 a Steamen csak a saját belső változatát szállítja, ezért a 2024-es játékosok az MSFS 2024 SDK-t telepítik (`<SDK>\SimConnect SDK\lib\SimConnect.dll`; a 2024-es szimulátor a 2020-as klienseket is elfogadja).

A hívások a SimConnect.h-ból, mind HRESULT-ot adnak vissza (0 = S_OK):

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

Minden üzenet SIMCONNECT_RECV {DWORD dwSize, dwVersion, dwID} fejléccel kezdődik (#pragma pack 1). Az itt olvasottak:

```text
1  EXCEPTION       dwException, dwSendID, dwIndex
2  OPEN            szApplicationName[256], then version DWORDs
3  QUIT            the sim is closing
4  EVENT           uGroupID, uEventID, dwData
6  EVENT_FILENAME  EVENT + szFileName[260], dwFlags        (FlightLoaded)
8  SIMOBJECT_DATA  dwRequestID, dwObjectID, dwDefineID, dwFlags, dwentrynumber,
                   dwoutof, dwDefineCount, then the values (FLOAT64 each here)
```

Szimulációs változók (az igényelt mértékegységekben, így nincs átváltás): PLANE LATITUDE/LONGITUDE (fok), PLANE ALTITUDE (méter, tengerszint felett), PLANE ALT ABOVE GROUND (méter), PLANE PITCH/BANK DEGREES és PLANE HEADING DEGREES TRUE (fok; a SimConnect saját előjelei – az orr felfelé negatív pitch), AIRSPEED INDICATED és GROUND VELOCITY (csomó), G FORCE (gforce), SIM ON GROUND (logikai). Rendszeresemények: SimStart, SimStop, Crashed, FlightLoaded, AircraftLoaded, Pause, CrashReset, PositionChanged, FlightSaved, Sim.

A repülés többi részéhez három további adatdefiníció kér adatot: a `MOTION_VARS` (minden hatodik szimulációs képkockánál), a repülőgép lassabban változó állapota (`STATE_VARS`, másodpercenként egyszer) és a nevei (`NAME_VARS`, 256 bájtos szövegek, változáskor). Mindegyik saját definíció, így egy változó, amelyet a szimulátor egy verziója nem ismer, csak azt a blokkot érinti. Minden üzenet egészben megmarad a szakasz nyers kísérőfájljában.

A pozíciók ugyanabba a lapos térképbe kerülnek, mint az X-Plane-é (x kelet, y magasság, z észak, méterben a repülés első pozíciójától); ez a pozíció a munkamenet `geo` adata, a meta.json-ban és a tábla láblécében.

Ugyanez a modul szolgálja ki ezt is: [Microsoft Flight Simulator 2024 (élő adatok)](game-msfs2024.md).

## Pozíciók és tengelyek {#positions-and-axes}

| | |
|---|---|
| Pozíciók rögzítve | igen |
| Felfelé mutató tengely | `y` |
| Mértékegység | méter (kelet, magasság, észak az első pozíciótól) |
| Tükrözve a megtekintőnek | `z` |
| Mértékegység-szorzó (`scale`: a megtekintő ezzel szorozza a pozíciókat) | 1 |

Ezek bekerülnek minden munkamenet `meta.json`-jába (`axes`), és ha a munkamenetnek vannak pozíciói, a `heat.parquet` láblécébe is, így a 3DHeat megtekintő maga forgatja és méretezi a sorokat – lásd [Az adatok](the-data.md).

## Többjátékos {#multiplayer}

- Online játszottként jelölve (`multiplayer`): **igen**. A `games --markdown` ezt így mutatja: "allowed (reads only what the game publishes)", vagyis engedélyezett, csak azt olvassa, amit a játék közzétesz.
- `telemetry` típus: csak azt olvassa, amit a játék vagy a platform kiad (egy UDP-port vagy megosztott memória, amelyet a játék közzétesz), így online játékban is rögzít, nemcsak offline; a jelző csak azt dönti el, szabad-e valaha memóriát olvasni.
- Memória: ez az adapter **soha** nem olvas memóriát. Csak a `memory` adapterek olvasnak memóriát, és soha nem olyan játékhoz, amelyet online játszottként jelöltek meg – lásd [Források és szabályok](sources-and-rules.md).

## Rögzített statisztikák {#statistics-recorded}

Statisztikakulcsok, amelyeket ennek az adapternek a kódja név szerint állít be (minden munkamenet `stats`-ja a `meta.json`-ban és a `watcher.sqlite` `stats` táblájában):

`airborne_time`, `bad_packets`, `crashes`, `distance_km`, `flight_time`, `max_altitude_m`, `max_g`, `{event}s`

A kapcsos zárójeles kulcsot futásidőben egészítjük ki (`score.{team}` csapatonként egy kulcs). A kód által a játék mezőinek táblájából vagy a játék saját statisztikanevéből vett kulcsok nincsenek ebben a listában; a fenti "Mit rögzít" rész nevezi meg őket.

## Teljesség {#completeness}

A watcher a 3DHeat [átalakítási szabályát](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md) követi: amit a forrás tartalmaz, azt beolvassuk vagy megtartjuk, soha nem dobjuk el. A sorokon kívül minden csomagot, oldalt, sort vagy választ, amelyet az adapter kap, egészben megőrzünk a munkamenet `heat.raw.parquet`-jában (oszlopok: `time`, `ms`, `type`, `used`, `payload`, `text`, majd minden név szerint megtartott mező; a `used` jelzi, amiből sor is lett). A `meta.json` `selfCheck.completeness` része minden `type`-ot megszámol; a `lost` 0.

**Beolvasva**

- a POSITION-definíció SIMOBJECT_DATA-ja (minden szimulációs képkockánál): szélesség, hosszúság, magasság, AGL, pitch, bank, valódi irány, IAS, talajsebesség, g, a földön van-e – a lekérdezés utolsó képkockája sorként, és minden képkocka érintésnél és felszállásnál
- a mozgás-definíció SIMOBJECT_DATA-ja (körülbelül 10 Hz: TAS, Mach, emelkedési sebesség, AoA, oldalcsúszás, mágneses irány, test-sebesség, gyorsulás és forgási sebesség három tengelyen), és az állapot-definíció (1 Hz: súlyok, üzemanyag, lapok, futómű, légfékek, parkolófék, autopilóta, motorok, gázkar és fordulatszám, külső hőmérséklet, szél, tengerszinti légnyomás, szimulációs sebesség, zulu- és helyi idő, kameraállapot) az utoljára érkezett értékekkel a sorokra
- a nevek-definíció SIMOBJECT_DATA-ja (cím, ATC-típus, modell és azonosító) a meta.json-ba és a sorok `aircraft` mezőjébe; az OPEN (alkalmazás és verzió) a meta.json-ba
- EVENT és EVENT_FILENAME: SimStart, SimStop, Crashed, FlightLoaded (a repülési fájl) és AircraftLoaded (a repülőgép-fájl) repülésekként, lezuhanásokként és a meta.json-ban
- a QUIT lezárja a munkamenetet

**Nyersen megtartva**

- minden üzenet, amelyet a SimConnect a watchernek ad, egészben, `payload`-ként, a SIMCONNECT_RECV_ID nevén: `SIMOBJECT_DATA`, `EVENT`, `EVENT_FILENAME`, `OPEN`, `QUIT`, `EXCEPTION` (olyan változó vagy esemény, amelyet a szimulátor nem fogadott el, a küldési azonosítóval és indexszel), minden más azonosító a nevén vagy `RECV_<id>` alatt
- csak a nyers kísérőfájl tartalmazza: a szimulációs képkockák pozícióit a sorok között, a Pause, Sim, CrashReset, PositionChanged és FlightSaved eseményeket, azt a definíciót, amelyet a szimulátor megrövidített (egy ismeretlen változó miatt: az a blokk nevek szerint nem olvasható); a meta.json `requests` tétele minden definíció változóit és mértékegységeit sorrendben felsorolja, így a payloadok ez a modul nélkül is olvashatók

**Nem elérhető**

- más repülőgépek (MI-forgalom, más játékosok online): a SimConnect_RequestDataOnSimObjectType egy sugárban lévő minden gépet lekérdezne – több terhelés a szimulátoron, és más játékosok repülései
- a mozgásblokk minden szimulációs képkockánál: minden hatodik képkockánál kérjük (körülbelül 10 Hz, a sorok üteme), ami a nyers adatfolyamot a méret ötödén tartja; a pozícióblokk minden képkockánál marad
- a többi több ezer szimulációs változó (rádiók, fények, minden motor műszerei, meghibásodások): egy definíció azt tartalmazza, amit kér; a listák a repülést, a repülőgép állapotát és a szimulátor idejét kérik
- időjárási megfigyelések, létesítmények (repülőterek, VOR-ok), kiegészítők kliensadatai: külön kérések, nem készülnek

**Méret**: óránként körülbelül 30–55 MB a zstd előtt: a pozícióblokk minden szimulációs képkockánál (kb. 200 bájt a keretével, másodpercenként 30–60), a mozgásblokk körülbelül 10 Hz-cel (kb. 240 bájt), az állapotblokk másodpercenként; a zstd a duplákat többszörösen csökkenti

## Ellenőrizve {#verified}

üzenetdekódolás a SimConnect.h kiosztásai szerint épített pufferekeken tesztelve; az élő SimConnect-kapcsolat nincs tesztelve

## Forrás {#source}

[heat3d_watch/adapters/msfs.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/msfs.py)

<!-- Generated from the adapter by tools/gen_game_pages.py; change the adapter and run it again rather than editing this page. -->
