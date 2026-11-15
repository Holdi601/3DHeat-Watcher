---
title: "Microsoft Flight Simulator 2024 (dane na żywo)"
nav_order: 32
lang: "pl"
source: game-msfs2024.md
source_hash: "011c18a23252"
nav_exclude: true
search_exclude: true
---
# Microsoft Flight Simulator 2024 (dane na żywo) {#microsoft-flight-simulator-2024-live-data}

Podczas gry w Microsoft Flight Simulator 2024 watcher zapisuje dane, które sam symulator wysyła na zewnątrz, dzięki czemu możesz później obejrzeć je na mapie w przeglądarce 3DHeat.

*Szczegóły techniczne: adapter `msfs2024`, rodzaj [`telemetry`](sources-and-rules.md); działa, gdy działa `FlightSimulator2024.exe`, i sprawdza nowe dane co 0,1 s.*

## Co jest zapisywane {#what-is-recorded}

- pozycja twojego samolotu w każdej klatce symulacji, brana 10 razy na sekundę (szerokość/długość geograficzna/wysokość jako metry na wschód/w górę/na północ od pierwszego ustalenia pozycji; lat/lon/alt zapisane jako kolumny)
- postawa, prędkość wskazywana, prędkość względem ziemi, AGL, g, na ziemi; prawdziwa prędkość, Mach, prędkość pionowa, kąt natarcia, ślizg boczny, kurs magnetyczny, prędkości w układzie samolotu, przyspieszenia i prędkości obrotowe, około 10 razy na sekundę
- masa, paliwo, klapy, podwozie, spoilery, hamulec postojowy, autopilot, przepustnica, obroty, pogoda, prędkość symulacji, czas i stan kamery raz na sekundę; tytuł samolotu oraz typ ATC, model i id
- starty, lądowania, katastrofy, loty rozpoczęte i zakończone (session_start/session_end)
- czas lotu, czas w powietrzu, dystans, najwyższa wysokość, najwyższe g, lądowania
- każda wiadomość SimConnect zachowana w całości w heat.raw.parquet

## Skąd pochodzą dane {#where-it-comes-from}

SimConnect przez własną bibliotekę SimConnect.dll gracza (folder symulatora albo %MSFS2024_SDK%\SimConnect SDK\lib)

## Jak to włączyć {#how-to-switch-it-on}

nic w symulatorze; potrzebna jest SimConnect.dll - MSFS 2020 ma ją w swoim folderze, gracze MSFS 2024 instalują SDK MSFS 2024

## Jak to działa {#how-it-works}

Microsoft Flight Simulator 2020 i 2024: SimConnect, przez własną bibliotekę SimConnect.dll gracza.

SimConnect to publiczne API klienckie symulatora (dokumentacja SDK:
<https://docs.flightsimulator.com/html/Programming_Tools/SimConnect/SimConnect_SDK.htm>,
<https://docs.flightsimulator.com/msfs2024/html/6_Programming_APIs/SimConnect/SimConnect_SDK.htm>).
Watcher nie dołącza tej DLL: ładuje tę, która przyszła z symulatorem albo jego SDK - MSFS 2020 umieszcza `SimConnect.dll` w swoim folderze instalacyjnym; MSFS 2024 w wersji Steam dostarcza tylko własną wewnętrzną, więc gracze 2024 instalują SDK MSFS 2024 (`<SDK>\SimConnect SDK\lib\SimConnect.dll`; symulator 2024 przyjmuje też klientów 2020).

Wywołania z SimConnect.h, wszystkie zwracają HRESULT (0 = S_OK):

```text
SimConnect_Open(HANDLE*, LPCSTR name, HWND, DWORD, HANDLE, DWORD config)
SimConnect_AddToDataDefinition(HANDLE, DWORD define, LPCSTR var, LPCSTR units,
                               SIMCONNECT_DATATYPE (FLOAT64 = 4), float epsilon, DWORD datum)
SimConnect_RequestDataOnSimObject(HANDLE, DWORD request, DWORD define, DWORD object (0 = user),
                                  SIMCONNECT_PERIOD (SIM_FRAME = 3), DWORD flags, DWORD origin,
                                  DWORD interval, DWORD limit)
SimConnect_SubscribeToSystemEvent(HANDLE, DWORD event, LPCSTR name)
SimConnect_GetNextDispatch(HANDLE, SIMCONNECT_RECV**, DWORD*)   E_FAIL, gdy nic nie czeka
SimConnect_Close(HANDLE)
```

Każda wiadomość zaczyna się od SIMCONNECT_RECV {DWORD dwSize, dwVersion, dwID} (#pragma pack 1). Odczytywane tutaj są:

```text
1  EXCEPTION       dwException, dwSendID, dwIndex
2  OPEN            szApplicationName[256], potem wersje DWORD
3  QUIT            symulator się zamyka
4  EVENT           uGroupID, uEventID, dwData
6  EVENT_FILENAME  EVENT + szFileName[260], dwFlags        (FlightLoaded)
8  SIMOBJECT_DATA  dwRequestID, dwObjectID, dwDefineID, dwFlags, dwentrynumber,
                   dwoutof, dwDefineCount, potem wartości (po FLOAT64 każda)
```

Zmienne symulacji (żądane jednostki, więc bez przeliczania): PLANE LATITUDE/LONGITUDE (stopnie), PLANE ALTITUDE (metry nad poziomem morza), PLANE ALT ABOVE GROUND (metry), PLANE PITCH/BANK DEGREES i PLANE HEADING DEGREES TRUE (stopnie; własne znaki SimConnect - nos w górę to ujemny pitch), AIRSPEED INDICATED i GROUND VELOCITY (węzły), G FORCE (gforce), SIM ON GROUND (bool). Zdarzenia systemowe: SimStart, SimStop, Crashed, FlightLoaded, AircraftLoaded, Pause, CrashReset, PositionChanged, FlightSaved, Sim.

Trzy kolejne definicje danych pobierają resztę lotu (`MOTION_VARS`, co szóstą klatkę symulacji), wolniejszy stan samolotu (`STATE_VARS`, raz na sekundę) i jego nazwy (`NAME_VARS`, ciągi 256 bajtów, gdy się zmienią); każda jest osobną definicją, więc zmienna, której jedna wersja symulatora nie zna, kosztuje tylko ten jeden blok. Każda wiadomość jest zachowywana w całości w surowym pliku dodatkowym sesji.

Pozycje trafiają do tej samej płaskiej mapy co w X-Plane (x na wschód, y wysokość, z na północ, w metrach od pierwszego ustalenia pozycji w czasie siedzenia w samolocie); to ustalenie jest `geo` sesji, zapisane w meta.json i stopce tabeli.

Ten sam moduł obsługuje też: [Microsoft Flight Simulator 2020 (dane na żywo)](game-msfs2020.md).

## Pozycje i osie {#positions-and-axes}

| | |
|---|---|
| Zapisywane pozycje | tak |
| Oś pionowa | `y` |
| Jednostki | metry (wschód, wysokość, północ od pierwszego ustalenia pozycji) |
| Lustrzane odbicie dla przeglądarki | `z` |
| Skala jednostek (`scale`: przeglądarka mnoży przez nią pozycje) | 1 |

Trafiają one do `meta.json` każdej sesji (`axes`) i, gdy sesja ma pozycje, do stopki `heat.parquet`, więc przeglądarka 3DHeat sama obraca i skaluje wiersze - zobacz [Dane](the-data.md).

## Gra wieloosobowa {#multiplayer}

- Oznaczona jako grana online (`multiplayer`): **tak**. `games --markdown` pokazuje to jako „dozwolone (czyta tylko to, co gra publikuje)”.
- Rodzaj `telemetry`: czyta tylko to, co gra lub platforma udostępnia (port UDP albo pamięć współdzielona, które gra publikuje), więc zapisuje także w grze online, a w trybie offline; flaga decyduje tylko o tym, czy wolno kiedykolwiek czytać pamięć.
- Pamięć: **nigdy** nie jest czytana przez ten adapter. Pamięć czytają tylko adaptery `memory`, i nigdy dla gry oznaczonej jako grana online - zobacz [Źródła i zasady](sources-and-rules.md).

## Zapisywane statystyki {#statistics-recorded}

Klucze statystyk, które kod tego adaptera ustawia po nazwie (`stats` każdej sesji w `meta.json` i tabela `stats` w `watcher.sqlite`):

`airborne_time`, `bad_packets`, `crashes`, `distance_km`, `flight_time`, `max_altitude_m`, `max_g`, `{event}s`

Klucz w nawiasach klamrowych jest uzupełniany podczas działania (`score.{team}` to jeden klucz na drużynę). Klucze, które kod bierze z tabeli pól gry albo z nazw statystyk gry, nie są na tej liście; „Co jest zapisywane” powyżej podaje je z nazwy.

## Kompletność {#completeness}

Watcher stosuje zasadę konwertera 3DHeat ([zasada konwertera](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md)): to, co zawiera źródło, jest odczytywane albo zachowywane, nigdy pomijane. Oprócz wierszy każdy pakiet, strona, linia czy odpowiedź, którą odbiera adapter, jest zachowywana w całości w `heat.raw.parquet` sesji (kolumny `time`, `ms`, `type`, `used`, `payload`, `text`, a potem pola zachowane po nazwie; `used` oznacza, co też stało się wierszami), a `selfCheck.completeness` w `meta.json` liczy każdy `type` - `lost` wynosi 0.

**Odczytywane**

- SIMOBJECT_DATA definicji pozycji (w każdej klatce symulacji): szerokość, długość, wysokość, AGL, pitch, bank, prawdziwy kurs, IAS, prędkość względem ziemi, g, na ziemi - ostatnia klatka odpytania jako wiersz, każda klatka przy dotknięciu ziemi i starcie
- SIMOBJECT_DATA definicji ruchu (około 10 razy na sekundę: TAS, Mach, prędkość pionowa, kąt natarcia, ślizg, kurs magnetyczny, prędkość w układzie samolotu, przyspieszenie i prędkość obrotowa na trzech osiach) oraz definicji stanu (1 raz na sekundę: masy, paliwo, klapy, podwozie, spoilery, hamulec postojowy, autopilot, silniki, przepustnica i obroty, temperatura zewnętrzna, wiatr, ciśnienie na poziomie morza, prędkość symulacji, czas zulu i lokalny, stan kamery) - na wiersze jako ostatnio otrzymane
- SIMOBJECT_DATA definicji nazw (tytuł, typ ATC, model i id) do meta.json i do `aircraft` w wierszach; OPEN (aplikacja i wersja) do meta.json
- EVENT i EVENT_FILENAME: SimStart, SimStop, Crashed, FlightLoaded (plik lotu) i AircraftLoaded (plik samolotu) jako loty, katastrofy i meta.json
- QUIT kończy sesję

**Zachowywane w całości**

- każda wiadomość, jaką SimConnect przekazuje watcherowi, w całości jako `payload`, pod nazwą z SIMCONNECT_RECV_ID: `SIMOBJECT_DATA`, `EVENT`, `EVENT_FILENAME`, `OPEN`, `QUIT`, `EXCEPTION` (zmienna albo zdarzenie, których symulator nie przyjął, z id wysłania i indeksem), każdy inny id po nazwie albo `RECV_<id>`
- to, co trzyma tylko surowy plik dodatkowy: każda pozycja klatki symulacji między wierszami, zdarzenia Pause, Sim, CrashReset, PositionChanged i FlightSaved, definicja przerwana przez symulator (jedna zmienna, której nie znał: blok nie jest wtedy odczytywany po nazwie); `requests` w meta.json wymienia zmienne i jednostki każdej definicji w kolejności, więc ładunki da się odczytać bez tego modułu

**Niedostępne**

- inne statki powietrzne (ruch AI, inni gracze online): SimConnect_RequestDataOnSimObjectType odpytywałby każdy samolot w promieniu - większe obciążenie symulatora i cudze loty
- blok ruchu w każdej klatce symulacji: jest pobierany co szóstą klatkę (około 10 Hz, tempo wierszy), co utrzymuje surowy strumień blisko jednej piątej rozmiaru; blok pozycji zostaje w każdej klatce
- tysiące innych zmiennych symulacji (radia, światła, wskaźniki każdego silnika, awarie): definicja zawiera to, o co prosi; listy pytają o lot, stan samolotu i czas symulacji
- obserwacje pogody, obiekty (lotniska, VOR-y), dane klienta dodatków: osobne żądania, niewykonywane

**Rozmiar**: około 30-55 MB na godzinę przed zstd: blok pozycji w każdej klatce symulacji (około 200 bajtów z jej numerem, 30-60 na sekundę), blok ruchu około 10 razy na sekundę (około 240 bajtów), blok stanu raz na sekundę; zstd zmniejsza liczby zmiennoprzecinkowe kilkukrotnie

## Sprawdzone {#verified}

dekodowanie wiadomości przetestowane na buforach zbudowanych według układów z SimConnect.h; żywe połączenie SimConnect nieprzetestowane

## Źródło {#source}

[heat3d_watch/adapters/msfs.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/msfs.py)

<!-- Generated from the adapter by tools/gen_game_pages.py; change the adapter and run it again rather than editing this page. -->
