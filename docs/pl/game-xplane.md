---
title: "X-Plane (dane na żywo)"
nav_order: 50
lang: "pl"
source: game-xplane.md
source_hash: "4e7246cce10c"
nav_exclude: true
search_exclude: true
---
# X-Plane (dane na żywo) {#x-plane-live-data}

Gdy grasz w X-Plane, watcher zapisuje dane, które sama gra wysyła na zewnątrz, dzięki czemu później możesz je obejrzeć na mapie w przeglądarce 3DHeat.

*Szczegóły techniczne: adapter `xplane`, rodzaj [`telemetry`](sources-and-rules.md); działa, gdy uruchomiony jest `X-Plane.exe`, i sprawdza nowe dane co 0,1 s.*

## Co jest zapisywane {#what-is-recorded}

- własna pozycja 10 razy na sekundę (10 Hz): szerokość, długość, wysokość jako metry na wschód, w górę i na północ od pierwszego odczytu; szerokość, długość i wysokość zachowane jako kolumny
- postawa, prędkość wskazywana i prawdziwa, prędkość względem ziemi, Mach, prędkość pionowa, AoA, ślizg boczny, kurs magnetyczny, AGL, g (normalne, osiowe, boczne), prędkości i prędkości obrotowe, klapy, hamulce aerodynamiczne, gaz, na ziemi
- masy (całkowita, paliwo, ładunek), dźwignia podwozia, autopilot, obroty silnika i N1, czas i data symulacji, pauza, prędkość symulacji, powtórka, temperatura zewnętrzna i ciśnienie na poziomie morza (X-Plane 12) raz na sekundę
- starty, lądowania, rozbicia, resety lotu (session_start/session_end dla każdego lotu)
- czas lotu, czas w powietrzu, dystans, najwyższa wysokość, najwyższe g, lądowania
- każda odpowiedź, jaką wysyła X-Plane, w całości w heat.raw.parquet

## Skąd pochodzą dane {#where-it-comes-from}

interfejs UDP X-Plane na 127.0.0.1:49000 (RREF dla datarefów i RPOS dla pozycji, odpowiadany do watchera)

## Jak to włączyć {#how-to-switch-it-on}

X-Plane 12: Ustawienia > Sieć > Akceptuj połączenia przychodzące (X-Plane 11 odpowiada domyślnie)

## Jak to działa {#how-it-works}

X-Plane 11 i 12: własny interfejs UDP symulatora na porcie 49000.

X-Plane odpowiada każdemu, kto pyta, na 127.0.0.1:49000, z żądaną częstotliwością, na adres i port, z których przyszło żądanie (dokument X-Plane „Exchanging Data with X-Plane”, dołączony w `<X-Plane>\Instructions\`):

```text
RREF  "RREF\0" + int32 freq + int32 index + char[400] dataref path (413 bytes).
      The answer is "RREF" + one internal byte + (int32 index, float32 value)
      pairs; freq 0 stops it.
RPOS  "RPOS\0" + the rate as a NUL-terminated ASCII string ("10\0"). The
      answer is "RPOS" + one internal byte + double lon, lat, elevation (m
      MSL) + float AGL (m), pitch, true heading, roll (deg), vx east, vy up,
      vz south (m/s), P, Q, R (rad/s), tightly packed.
```

RPOS podaje szerokość i długość jako double (RREF tylko jako float, co daje błąd pół metra), więc to RPOS napędza pozycję; RREF dostarcza resztę i zastępuje RPOS, gdy ten nie przychodzi. Datarefy (nazwy jak w `Resources\plugins\DataRefs.txt` X-Plane 12, <https://developer.x-plane.com/datarefs/>):

```text
sim/flightmodel/position/latitude, longitude, elevation  deg, deg, m MSL
sim/flightmodel/position/true_theta, true_phi, true_psi  pitch, roll, true heading (deg)
sim/flightmodel/position/indicated_airspeed              knots
sim/flightmodel/position/groundspeed                     m/s
sim/flightmodel/position/y_agl                           m above ground
sim/flightmodel/forces/g_nrml                            g, normal to the wings
sim/flightmodel/failures/onground_any                    1 on the ground
sim/flightmodel2/misc/has_crashed                        1 crashed
sim/time/total_flight_time_sec                           since the flight was reset
```

Reszta lotu w tym samym tempie (prawdziwa prędkość, prędkość pionowa, AoA, ślizg boczny, kurs magnetyczny, Mach, g osiowe i boczne, prędkości obrotowe, klapy, hamulce aerodynamiczne, gaz: `DATAREFS`), a wolniejszy stan statku raz na sekundę (masy, dźwignia podwozia, autopilot, silniki, czas symulatora, pauza i prędkość, pogoda: `SLOW_DATAREFS`). Każdy datagram jest też zachowany w całości w surowym pliku sesji, a meta.json podaje, który dataref stoi za każdym indeksem RREF.

X-Plane 12 przyjmuje to tylko przy włączonej opcji Ustawienia > Sieć > „Akceptuj połączenia przychodzące”. Pozycje trafiają do płaskiej mapy wokół pierwszego odczytu lotu (`Tangent`): x na wschód, z na północ w metrach, y to wysokość nad poziomem morza – więc lot poziomy pozostaje poziomy, bez względu na to, jak daleko poleci, co prawdziwa płaszczyzna styczna by zakrzywiała wraz z Ziemią. Punkt początkowy mapy to `geo` sesji: meta.json i stopka tabeli go niosą, więc przeglądarka może położyć prawdziwy świat pod lotem.

Ten moduł zawiera też to, co dzielą inne symulatory lotu: płaską mapę, księgowość lotu (starty, lądowania, rozbicia, dystans), gniazdo UDP i listę bibliotek Steam.

## Pozycje i osie {#positions-and-axes}

| | |
|---|---|
| Zapisane pozycje | tak |
| Oś pionowa | `y` |
| Jednostki | metry (wschód, wysokość, północ od pierwszego odczytu) |
| Odbicie dla przeglądarki | `z` |
| Skala jednostki (`scale`: przeglądarka mnoży przez nią pozycje) | 1 |

Te wartości trafiają do `meta.json` każdej sesji (`axes`) i, gdy sesja ma pozycje, do stopki `heat.parquet`. Dzięki temu przeglądarka 3DHeat sama obraca i skaluje wiersze – zob. [Dane](the-data.md).

## Tryb wieloosobowy {#multiplayer}

- Oznaczona jako gra sieciowa (`multiplayer`): **nie**. `games --markdown` pokazuje to jako „single-player”.
- Rodzaj `telemetry`: czyta tylko to, co gra lub platforma udostępnia (port UDP albo pamięć dzielona, które gra publikuje), więc nagrywa także w grze sieciowej, tak jak w trybie offline. Flaga decyduje tylko o tym, czy pamięć w ogóle może być czytana.
- Pamięć: **nigdy** nie jest czytana przez ten adapter. Tylko adaptery `memory` czytają pamięć, i nigdy dla gry oznaczonej jako sieciowa – zob. [Źródła i zasady](sources-and-rules.md).

## Co jest zapisywane w statystykach {#statistics-recorded}

Klucze statystyk, które kod tego adaptera ustawia po nazwie (`stats` każdej sesji w `meta.json` i tabela `stats` w `watcher.sqlite`):

`airborne_time`, `bad_packets`, `crashes`, `distance_km`, `flight_time`, `max_altitude_m`, `max_g`, `{event}s`

Klucz w nawiasach klamrowych jest uzupełniany podczas działania (`score.{team}` to jeden klucz na zespół). Klucze, które kod bierze z tabeli pól gry albo z nazw statystyk gry, nie są na tej liście; „Co jest zapisywane” wyżej wymienia je.

## Kompletność {#completeness}

Watcher stosuje [zasadę konwertera](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md) 3DHeat: to, co źródło zawiera, jest czytane albo zachowywane, nigdy pomijane. Oprócz wierszy każdy pakiet, strona, linia lub odpowiedź, którą adapter otrzyma, jest zachowana w całości w `heat.raw.parquet` sesji (kolumny `time`, `ms`, `type`, `used`, `payload`, `text`, a potem każde pole zachowane po nazwie; `used` oznacza to, co stało się też wierszami). `selfCheck.completeness` w `meta.json` liczy każdy `type`; `lost` wynosi 0.

**Odczytane**

- RPOS (10 Hz): długość, szerokość, wysokość, AGL, pitch, kurs prawdziwy, roll, prędkość (wschód, w górę, południe) i prędkości obrotowe P/Q/R – wszystko na wierszach
- RREF (10 Hz): 27 datarefów `DATAREFS` – pozycja, postawa, IAS, prędkość względem ziemi, TAS, prędkość pionowa, AoA, ślizg boczny, kurs magnetyczny, Mach, g normalne/osiowe/boczne, prędkości obrotowe, klapy, hamulce aerodynamiczne, gaz, AGL, rozbicie, na ziemi, czas lotu – na wierszach
- RREF (1 Hz): 20 datarefów `SLOW_DATAREFS` – masy, dźwignia podwozia, serwa autopilota, czas i data symulacji, pauza, prędkość symulacji, powtórka, liczba silników, obroty silników 1–4, N1 silników 1–2, temperatura powietrza zewnętrznego, ciśnienie na poziomie morza – na wierszach, jako ostatnio otrzymane

**Zachowane w surowej postaci**

- każdy datagram w całości jako `payload`, pod swoim czteroliterowym nagłówkiem: `RREF` i `RPOS` (używany, gdy odpytanie utworzyło wiersz; w menu, bez ustalonej pozycji, nie tworzą wierszy), a wszystko inne, co X-Plane wysyła na port watchera, pod swoim nagłówkiem lub `unknown`; `requests` w meta.json mówi, który dataref stoi za każdym indeksem RREF, więc ładunki da się odczytać bez tego modułu

**Niedostępne**

- każdy inny dataref (X-Plane ma tysiące): RREF wysyła tylko to, o co poproszono, po jednej subskrypcji każde; lista prosi o lot, stan statku i czas symulatora – więcej szczegółów kabiny (radia, światła, każdy wskaźnik silnika, awarie) pomnożyłoby żądania
- nazwa statku i typ ICAO: datarefy będące tablicami bajtów, które RREF wysyła jako po jednym floacie na znak
- inne statki (AI i wieloosobowe): datarefy sim/multiplayer/position nie są żądane
- wyjście DATA (Ustawienia > Wyjście danych): wysyła na stały adres wybrany w symulatorze, a nie do tego, kto pyta; RREF i RPOS obejmują to, co czyta watcher

**Rozmiar**: około 17 MB na godzinę przed zstd (RREF i RPOS przy 10 Hz, po ok. 220 i 70 bajtów plus ramka każdy, wolny RREF raz na sekundę), jeśli X-Plane wysyła wartości każdego odpytania w jednym pakiecie, jak to robi; zstd zmniejsza floaty kilkukrotnie

## Sprawdzone {#verified}

testowane na fałszywym X-Plane odpowiadającym na RREF/RPOS wg „Exchanging Data with X-Plane” z X-Plane 12; nazwy datarefów sprawdzone w DataRefs.txt z X-Plane 12; niesprawdzone z działającym symulatorem

## Źródło {#source}

[heat3d_watch/adapters/xplane.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/xplane.py)

<!-- Generated from the adapter by tools/gen_game_pages.py; change the adapter and run it again rather than editing this page. -->
