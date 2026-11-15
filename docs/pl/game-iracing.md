---
title: "iRacing (dane na żywo)"
nav_order: 28
lang: "pl"
source: game-iracing.md
source_hash: "894d9bc4081f"
nav_exclude: true
search_exclude: true
---
# iRacing (dane na żywo) {#iracing-live-data}

Gdy grasz w iRacing, watcher zapisuje dane, które sama gra wysyła na zewnątrz, dzięki czemu później możesz je obejrzeć jako statystyki i oś czasu.

*Szczegóły techniczne: adapter `iracing`, rodzaj [`telemetry`](sources-and-rules.md); działa, gdy uruchomiony jest `iRacingSim64DX11.exe` lub `iRacingSim64.exe`, i sprawdza nowe dane co 0,1 s.*

## Co jest zapisywane {#what-is-recorded}

- jazda 5 razy na sekundę bez pozycji (iRacing nie podaje jej na żywo): prędkość, bieg, gaz, hamulec, okrążenie, udział w okrążeniu, pozycja w wyścigu i w klasie, incydenty
- początek sesji, wsiadanie i wysiadanie z auta, wjazd i zjazd z alei serwisowej, okrążenia z czasem, incydenty z punktami, flaga w kratkę, meta
- pliki telemetrii .ibt zapisane podczas sesji (szerokość, długość, wysokość – przeglądarka je odczytuje)
- okrążenia, najlepsze okrążenie, incydenty, pozycja w wyścigu, postoje w alei, dystans, prędkość maksymalna
- cała pamięć dzielona w `heat.raw.parquet`: nagłówek, nagłówki zmiennych, informacje o sesji, każda odczytana linia telemetrii

## Skąd pochodzą dane {#where-it-comes-from}

pamięć dzielona Local\IRSDKMemMapFileName (iRacing SDK); pliki .ibt w %USERPROFILE%\Documents\iRacing\telemetry

## Jak to włączyć {#how-to-switch-it-on}

Nic dla danych na żywo. Dla pozycji: nagrywaj telemetrię w aucie (Alt+L) albo ustaw irsdkLog=1 w app.ini

## Jak to działa {#how-it-works}

iRacing na żywo: pamięć dzielona iRacing SDK, czytana natywnie.

Symulator publikuje telemetrię dla aplikacji w nazwanym mapowaniu pliku, `Local\IRSDKMemMapFileName`, które tworzy podczas działania (i sygnalizuje `Local\IRSDKDataValidEvent` przy każdej aktualizacji; tutaj nie jest to potrzebne: watcher sprawdza dane dziesięć razy na sekundę). Układ pochodzi z `irsdk_defines.h` z SDK, także wg pyirsdk (MIT) – tu zapisany ponownie na podstawie tych faktów:

```text
irsdk_header (little-endian int32s)
    0 ver, 4 status (bit 0: connected), 8 tickRate,
    12 sessionInfoUpdate, 16 sessionInfoLen, 20 sessionInfoOffset,
    24 numVars, 28 varHeaderOffset, 32 numBuf, 36 bufLen, 40 pad[2],
    48 varBuf[4]: { tickCount, bufOffset, pad[2] } (16 bytes each)
irsdk_varHeader (144 bytes, numVars of them at varHeaderOffset)
    0 type (0 char, 1 bool, 2 int, 3 bitfield, 4 float, 5 double),
    4 offset (into a line), 8 count, 12 countAsTime + 3 pad,
    16 name[32], 48 desc[64], 112 unit[32]
session info: YAML text at sessionInfoOffset, rewritten when
    sessionInfoUpdate changes (track, sessions, drivers)
```

Symulator zapisuje `numBuf` linii cyklicznie; najnowsza to ta z najwyższym tickCount, a linia jest pobierana ponownie, jeśli jej tickCount zmienił się podczas kopiowania.

Dane na żywo nie mają pozycji w świecie – szerokość, długość i wysokość są tylko w plikach `.ibt`, które iRacing zapisuje w `Documents\iRacing\telemetry` (Alt+L w aucie albo `irsdkLog=1`), a które przeglądarka 3DHeat czyta sama. Watcher zapisuje więc jazdę jako zdarzenia bez współrzędnych – prędkość, okrążenie, udział przejechanej części okrążenia, pozycja w wyścigu, incydenty – plus okrążenia, incydenty, postoje i flagę w kratkę, a na końcu pliki `.ibt` zapisane podczas sesji jako zdarzenia `telemetry_file`, by przeglądarka mogła je otworzyć.

Źródło: iRacing SDK (irsdk_defines.h, dokumentacja „iRacing SDK” na forum); kutu/pyirsdk (MIT) do potwierdzenia przesunięć.

## Pozycje i osie {#positions-and-axes}

| | |
|---|---|
| Zapisane pozycje | nie |
| Oś pionowa | `y` |
| Jednostki | brak pozycji na żywo; pliki .ibt mają szerokość/długość/wysokość |
| Odbicie dla przeglądarki | brak |
| Skala jednostki (`scale`: przeglądarka mnoży przez nią pozycje) | 1 |

Te wartości trafiają do `meta.json` każdej sesji (`axes`) i, gdy sesja ma pozycje, do stopki `heat.parquet`. Dzięki temu przeglądarka 3DHeat sama obraca i skaluje wiersze – zob. [Dane](the-data.md).

## Tryb wieloosobowy {#multiplayer}

- Oznaczona jako gra sieciowa (`multiplayer`): **tak**. `games --markdown` pokazuje to jako „allowed (reads only what the game publishes)”.
- Rodzaj `telemetry`: czyta tylko to, co gra lub platforma udostępnia (port UDP albo pamięć dzielona, które gra publikuje), więc nagrywa także w grze sieciowej, tak jak w trybie offline. Flaga decyduje tylko o tym, czy pamięć w ogóle może być czytana.
- Pamięć: **nigdy** nie jest czytana przez ten adapter. Tylko adaptery `memory` czytają pamięć, i nigdy dla gry oznaczonej jako sieciowa – zob. [Źródła i zasady](sources-and-rules.md).

## Co jest zapisywane w statystykach {#statistics-recorded}

Klucze statystyk, które kod tego adaptera ustawia po nazwie (`stats` każdej sesji w `meta.json` i tabela `stats` w `watcher.sqlite`):

`best_lap`, `distance_km`, `finishes`, `incidents`, `laps`, `pit_stops`, `race_position`, `sessions`, `top_speed_kmh`

Klucz w nawiasach klamrowych jest uzupełniany podczas działania (`score.{team}` to jeden klucz na zespół). Klucze, które kod bierze z tabeli pól gry albo z nazw statystyk gry, nie są na tej liście; „Co jest zapisywane” wyżej wymienia je.

## Kompletność {#completeness}

Watcher stosuje [zasadę konwertera](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md) 3DHeat: to, co źródło zawiera, jest czytane albo zachowywane, nigdy pomijane. Oprócz wierszy każdy pakiet, strona, linia lub odpowiedź, którą adapter otrzyma, jest zachowana w całości w `heat.raw.parquet` sesji (kolumny `time`, `ms`, `type`, `used`, `payload`, `text`, a potem każde pole zachowane po nazwie; `used` oznacza to, co stało się też wierszami). `selfCheck.completeness` w `meta.json` liczy każdy `type`; `lost` wynosi 0.

**Odczytane**

- z najnowszej linii telemetrii: czas sesji, numer, stan i id, na torze, replay, okrążenie, ukończone okrążenia, udział i metry okrążenia, ostatni i najlepszy czas okrążenia, prędkość, bieg, gaz, hamulec, obroty, pit road, nawierzchnia toru, pozycja w wyścigu i w klasie, liczba własnych incydentów (wiersze `driving` 5 razy na sekundę i zdarzenia)
- teraz także na wierszach `driving`: `steering_angle`, `yaw`, `yaw_north`, `pitch`, `roll` (stopnie, z radianów symulatora – tylko gdy nagłówek zmiennej podaje jednostkę rad), `fuel_l` (jednostka l), `lat_accel` i `lon_accel` (jednostka m/s^2)
- z YAML informacji o sesji: indeks auta gracza, tor i konfiguracja, typy sesji, nazwa, auto, zespół i numer każdego kierowcy (wiersze session_start, meta.json)
- sprawdzone na bloku zbudowanym z irsdk_defines.h w testach; jeszcze nie sprawdzone w symulatorze

**Zachowane w surowej postaci**

- `telemetry`: najnowsza linia w całości, każda zmienna, jaką publikuje symulator (tablice CarIdx każdego auta, opony, zawieszenie, tablice o wysokiej częstotliwości `_ST` tam, gdzie je ma ...), przy każdym odczycie, który znajduje nowy tick; `tick` to licznik ticków symulatora; `used` jest fałszywe, gdy odtwarzana jest powtórka
- `var_headers`: nagłówki zmiennych w całości (144 bajty każdy) i, w `text`, jako JSON (nazwa, typ, przesunięcie, liczba, jednostka, opis), za każdym razem, gdy układ się zmienia – wystarczy, by przeczytać każdą zmienną każdej zachowanej linii
- `session_info`: tekst YAML w całości za każdym razem, gdy zmienia się jego licznik aktualizacji (weekend, sesje i wyniki, kierowcy, ustawienia auta, radio, listy kamer), `update` to ten licznik
- `header`: nagłówek irsdk o długości 112 bajtów w całości za każdym razem, gdy się zmieni (wersja, status, tick rate, przesunięcia, ticki linii)

**Niedostępne**

- pozycja w świecie na żywo: pamięć dzielona jej nie ma; szerokość, długość i wysokość są tylko w plikach .ibt (przy włączonym logowaniu), które czyta przeglądarka – watcher nazywa te, które powstały podczas sesji
- ticki między dwoma odczytami: symulator zapisuje 60 linii na sekundę w 3 lub 4 slotach, a watcher czyta 10 razy na sekundę, więc większość ticków jest nadpisywana, zanim zdąży je odczytać; plik .ibt ma każdy tick, gdy logowanie jest włączone

**Rozmiar**: linia telemetrii to kilka KB (ok. 5–10 KB z tablicami każdego auta), zachowywana do 10 razy na sekundę, plus nagłówek (112 bajtów) równie często i YAML informacji o sesji (dziesiątki KB), gdy się zmieni: około 0,2–0,4 GB na godzinę na torze przed kompresją; zstd zmniejsza to do ułamka (jeszcze nie zmierzone na prawdziwej sesji)

## Sprawdzone {#verified}

przetestowane na bloku pamięci dzielonej zbudowanym w teście wg układu irsdk; niesprawdzone z symulatorem

## Źródło {#source}

[heat3d_watch/adapters/iracing.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/iracing.py)

<!-- Generated from the adapter by tools/gen_game_pages.py; change the adapter and run it again rather than editing this page. -->
