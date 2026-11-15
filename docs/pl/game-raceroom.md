---
title: "RaceRoom Racing Experience (dane na żywo)"
nav_order: 38
lang: "pl"
source: game-raceroom.md
source_hash: "ffd0499ca059"
nav_exclude: true
search_exclude: true
---
# RaceRoom Racing Experience (dane na żywo) {#raceroom-racing-experience-live-data}

Gdy grasz w RaceRoom Racing Experience, watcher zapisuje dane, które sama gra wysyła na zewnątrz, dzięki czemu później możesz je obejrzeć na mapie w przeglądarce 3DHeat.

*Szczegóły techniczne: adapter `raceroom`, rodzaj [`telemetry`](sources-and-rules.md); działa, gdy uruchomiony jest `RRRE64.exe` lub `RRRE.exe`, i sprawdza nowe dane co 0,1 s.*

## Co jest zapisywane {#what-is-recorded}

- pozycja każdego auta (świat XYZ, m) 10 razy na sekundę, według nazwiska kierowcy, własne auto oznaczone, wraz z prędkością i pozycją w wyścigu; własny bieg, gaz, hamulec
- początek sesji z torem, który podaje gra; okrążenia każdego auta z czasem okrążenia; mety; własne postoje w boksach
- teleporty (powrót do boksów, restart): `teleport` – gdzie auto było, `spawn` – gdzie jest teraz
- własne okrążenia, najlepsze okrążenie, pozycja w wyścigu, dystans, prędkość maksymalna
- cała strona pamięci współdzielonej gry w `heat.raw.parquet`, za każdym razem, gdy się zmieni
- własne punkty za incydenty

## Skąd pochodzą dane {#where-it-comes-from}

pamięć współdzielona $R3E (r3e.h Sector3, wersja 3)

## Jak to włączyć {#how-to-switch-it-on}

Nic nie trzeba włączać: watcher odczytuje źródło tak, jak udostępnia je gra lub platforma.

## Jak to działa {#how-it-works}

Pamięć współdzielona, którą gry wyścigowe publikują dla pulpitów, otwierana tylko do odczytu – i nigdy tworzona.

Kilka symulatorów udostępnia swoją telemetrię jako nazwane mapowanie pliku Windows, które gra tworzy i które każdy może odczytać: strony Kunosa `Local\acpmf_*` (Assetto Corsa,
ACC, AC Rally, `Local\acevo_pmf_*` w AC EVO), `Local\IRSDKMemMapFileName` iRacing,
`$R3E` z RaceRoom, `$pcars2$` z Automobilista 2 / Project CARS 2.

Dlaczego nie `mmap.mmap(-1, size, tagname=...)`, czyli zwykły sposób w Pythonie: gdy mapowanie jeszcze nie istnieje, *tworzy* je – tutaj tylko do odczytu. Gra uruchomiona później otwiera wtedy mapowanie watchera zamiast własnego i nie może do niego pisać, więc jej telemetria jest martwa, dopóki watcher go nie zwolni.
Watcher uruchamia adapter, gdy tylko pojawi się proces gry, czyli dokładnie wtedy, gdy gra jeszcze nie utworzyła swojego mapowania. Dlatego tutaj używane jest `OpenFileMappingW`, które znajduje tylko istniejące mapowanie, mapuje je z `FILE_MAP_READ` i zgłasza „jeszcze nie ma” w przeciwnym razie; adaptery próbują ponownie chwilę później.

Tutaj nic nie może pisać: widok jest mapowany tylko do odczytu i jest tylko kopiowany przez `ctypes.string_at`.

Dwie gry są odczytywane tutaj także; każde auto na torze jest na ich stronach.

#### RaceRoom Racing Experience - `$R3E` {#raceroom-racing-experience---r3e}

Sector3 `r3e.h` (github.com/sector3studios/r3e-api, sample-c/src/r3e.h,
wersja 3.6), `#pragma pack(1)`. Nagłówek mówi, gdzie zaczynają się kierowcy i jak duży
jest jeden (`all_drivers_offset`, `driver_data_size`), więc część każdego kierowcy – nazwa, slot, miejsce, pozycja w świecie (float x y z, m), ukończone okrążenia, aktualny czas okrążenia, status mety, pas pitów, prędkość – jest czytana według tych wartości. Własne pola gracza (najlepsze i poprzednie okrążenie, pozycja w wyścigu, punkty za incydenty, bieg, pedały, nazwy toru i wariantu) są czytane z przesunięć 3.6 tylko wtedy, gdy `all_drivers_offset` wynosi 2008, czyli tyle, ile wynosi w tym układzie. Y przyjęte jako oś w górę; nagłówek tego nie mówi.

Ten sam moduł obsługuje też: [Automobilista 2 (dane na żywo)](game-automobilista-2.md), [Project CARS 2 (dane na żywo)](game-project-cars-2.md).

## Pozycje i osie {#positions-and-axes}

| | |
|---|---|
| Zapisane pozycje | tak |
| Oś pionowa | `y` |
| Jednostki | metry; przyjęta oś Y w górę (r3e.h tego nie mówi) |
| Odbicie dla przeglądarki | brak |
| Skala jednostki (`scale`: przeglądarka mnoży przez nią pozycje) | 1 |

Te wartości trafiają do `meta.json` każdej sesji (`axes`) i, gdy sesja ma pozycje, do stopki `heat.parquet`. Dzięki temu przeglądarka 3DHeat sama obraca i skaluje wiersze – zob. [Dane](the-data.md).

## Tryb wieloosobowy {#multiplayer}

- Oznaczone jako grane online (`multiplayer`): **tak**. `games --markdown` pokazuje to jako „dozwolone (odczytuje tylko to, co gra publikuje)”.
- Rodzaj `telemetry`: odczytuje tylko to, co gra lub platforma udostępnia (port UDP albo pamięć współdzielona, którą gra publikuje), więc nagrywa też w grze online; flaga decyduje tylko o tym, czy wolno kiedykolwiek czytać pamięć.
- Pamięć: **nigdy** nie jest odczytywana przez ten adapter. Tylko adaptery `memory` czytają pamięć, i nigdy dla gry oznaczonej jako grana online – zob. [Źródła i zasady](sources-and-rules.md).

## Co jest zapisywane w statystykach {#statistics-recorded}

Klucze statystyk, które kod tego adaptera ustawia po nazwie (`stats` każdej sesji w `meta.json` i tabela `stats` w `watcher.sqlite`):

`best_lap`, `distance_km`, `finishes`, `incidents`, `laps`, `pit_stops`, `race_position`, `top_speed_kmh`

Klucz w nawiasach klamrowych jest uzupełniany w czasie działania (`score.{team}` to jeden klucz na zespół). Klucze, które kod bierze z tabeli pól gry lub z jej własnych nazw statystyk, nie są na tej liście; sekcja „Co jest zapisywane” wyżej wymienia je.

## Kompletność {#completeness}

Watcher stosuje [zasadę konwertera 3DHeat](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md): to, co źródło zawiera, jest odczytywane lub zachowywane, nigdy nie jest pomijane. Oprócz wierszy każdy pakiet, strona, linia lub odpowiedź, którą adapter otrzyma, jest zachowana w całości w `heat.raw.parquet` sesji (kolumny `time`, `ms`, `type`, `used`, `payload`, `text`, a potem każde pole zachowane po nazwie; `used` oznacza to, co stało się też wierszami), a `selfCheck.completeness` w `meta.json` liczy każdy `type` – `lost` wynosi 0.

**Odczytane**

- dla każdego slotu kierowcy (według własnego przesunięcia i rozmiaru nagłówka): nazwa, slot, status mety, miejsce, pozycja w świecie, ukończone okrążenia, aktualny czas okrążenia, pas pitów, prędkość
- własne pola gracza, tylko gdy strona ma układ r3e.h 3.6: nazwy toru i wariantu, rodzaj sesji, pozycja w wyścigu, najlepsze i poprzednie okrążenie, punkty za incydenty, bieg, gaz, hamulec, slot gracza
- przesunięcia wyliczone z r3e.h 3.6 firmy Sector3 i sprawdzone na stronie zbudowanej z niego w testach; jeszcze nie sprawdzone w grze

**Zachowane w surowej postaci**

- `r3e`: cała mapa $R3E, każdy odczyt, którego bajty różnią się od ostatnio zachowanej kopii – każde pole r3e.h: fizyka gracza (orientacja, prędkości, przyspieszenia, siły g), silnik, paliwo, opony, hamulce, uszkodzenia, flagi, menu pitów, czasy sektorów, pełne dane kierowcy z każdego slotu (klasa, model, zespół, czasy sektorów, straty, kary, opony)
- `used` jest prawdą dla strony odczytanej do wierszy; fałszem dla strony z menu, podczas pauzy, w powtórce, o innym układzie lub złapanej w trakcie zapisu (`torn` 1); `unchanged_reads` w meta.json liczy odczyty bajt w bajt takie jak kopia zachowana wcześniej

**Niedostępne**

- wejścia i fizyka innych kierowców: strona podaje tylko własne auto gracza
- dokładne czasy okrążeń innych aut: slot ma tylko bieżący czas okrążenia, więc okrążenie to ostatni zobaczony bieżący czas (z dokładnością do ok. 0,1 s)
- własne pola gracza w układzie innym niż 3.6: zachowane w surowej postaci, nieodczytane, dopóki nie zostaną sprawdzone

**Rozmiar**: strona ma 44 KB (r3e.h 3.6; mapowanie jest zaokrąglone do pełnych stron 4 KB), do 10 razy na sekundę podczas jazdy: około 1,6 GB na godzinę przed kompresją; puste sloty kierowców i pola, które się nie zmieniają, zstd kompresuje bardzo dobrze (jeszcze nie zmierzone na prawdziwej sesji)

## Sprawdzone {#verified}

przetestowane na stronie zbudowanej w teście z r3e.h 3.6 (przesunięcia wyliczone z oficjalnego nagłówka); nie przetestowane w grze; czasy okrążeń innych aut to ostatni zobaczony bieżący czas okrążenia (z dokładnością do ok. 0,1 s)

## Źródło {#source}

[heat3d_watch/adapters/simracing_shm.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/simracing_shm.py)

<!-- Generated from the adapter by tools/gen_game_pages.py; change the adapter and run it again rather than editing this page. -->
