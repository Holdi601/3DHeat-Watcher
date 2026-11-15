---
title: "Project CARS 2 (dane na żywo)"
nav_order: 37
lang: "pl"
source: game-project-cars-2.md
source_hash: "a1990b93b7d1"
nav_exclude: true
search_exclude: true
---
# Project CARS 2 (dane na żywo) {#project-cars-2-live-data}

Gdy grasz w Project CARS 2, watcher zapisuje dane, które sama gra wysyła na zewnątrz, dzięki czemu później możesz je obejrzeć na mapie w przeglądarce 3DHeat.

*Szczegóły techniczne: adapter `project-cars-2`, rodzaj [`telemetry`](sources-and-rules.md); działa, gdy uruchomiony jest `pCARS2AVX.exe` lub `pCARS2.exe`, i sprawdza nowe dane co 0,1 s.*

## Co jest zapisywane {#what-is-recorded}

- pozycja każdego auta (świat XYZ, m) 10 razy na sekundę, według nazwiska kierowcy, własne auto oznaczone, wraz z prędkością i pozycją w wyścigu; własny bieg, gaz, hamulec
- początek sesji z torem, który podaje gra; okrążenia każdego auta z czasem okrążenia; mety; własne postoje w boksach
- teleporty (powrót do boksów, restart): `teleport` – gdzie auto było, `spawn` – gdzie jest teraz
- własne okrążenia, najlepsze okrążenie, pozycja w wyścigu, dystans, prędkość maksymalna
- cała strona pamięci współdzielonej gry w `heat.raw.parquet`, za każdym razem, gdy się zmieni

## Skąd pochodzą dane {#where-it-comes-from}

pamięć współdzielona $pcars2$ (SMS SharedMemory.h)

## Jak to włączyć {#how-to-switch-it-on}

W grze: Opcje > System > Shared Memory: „Project CARS 2”

## Jak to działa {#how-it-works}

Pamięć współdzielona, którą gry wyścigowe publikują dla pulpitów, otwierana tylko do odczytu – i nigdy tworzona.

Kilka symulatorów udostępnia swoją telemetrię jako nazwane mapowanie pliku Windows, które gra tworzy i które każdy może odczytać: strony Kunosa `Local\acpmf_*` (Assetto Corsa,
ACC, AC Rally, `Local\acevo_pmf_*` w AC EVO), `Local\IRSDKMemMapFileName` iRacing,
`$R3E` z RaceRoom, `$pcars2$` z Automobilista 2 / Project CARS 2.

Dlaczego nie `mmap.mmap(-1, size, tagname=...)`, czyli zwykły sposób w Pythonie: gdy mapowanie jeszcze nie istnieje, *tworzy* je – tutaj tylko do odczytu. Gra uruchomiona później otwiera wtedy mapowanie watchera zamiast własnego i nie może do niego pisać, więc jej telemetria jest martwa, dopóki watcher go nie zwolni.
Watcher uruchamia adapter, gdy tylko pojawi się proces gry, czyli dokładnie wtedy, gdy gra jeszcze nie utworzyła swojego mapowania. Dlatego tutaj używane jest `OpenFileMappingW`, które znajduje tylko istniejące mapowanie, mapuje je z `FILE_MAP_READ` i zgłasza „jeszcze nie ma” w przeciwnym razie; adaptery próbują ponownie chwilę później.

Tutaj nic nie może pisać: widok jest mapowany tylko do odczytu i jest tylko kopiowany przez `ctypes.string_at`.

Dwie gry są odczytywane tutaj także; każde auto na torze jest na ich stronach.

#### Automobilista 2 / Project CARS 2 - `$pcars2$` {#automobilista-2--project-cars-2---pcars2}

SMS-owy `SharedMemory.h` (dostarczany w folderze gry Support\SharedMemory;
AMS2: Opcje > System > Shared Memory „Project CARS 2”), `#pragma pack(4)`.
`mParticipantInfo[64]` od bajtu 28, po 100 bajtów każdy: mIsActive, mName[64],
mWorldPosition[3] (m, Y w górę), mCurrentLapDistance, mRacePosition,
mLapsCompleted, mCurrentLap, mCurrentSector; mViewedParticipantIndex (20)
to auto gracza; dla każdego uczestnika mLastLapTimes (9200), mRaceStates
(9520), mSpeeds (10800); najlepszy czas gracza mBestLapTime (6716), mLastLapTime
(6720), mSpeed (6848), mBrake, mThrottle, mGear; mSequenceNumber (7320) jest
nieparzysty, gdy gra pisze. Przesunięcia wyliczono z dwóch niezależnych kopii
nagłówka (własnej kopii gry nie ma zainstalowanej tutaj), które się zgadzają.

Obie strony są dodatkowo zachowywane w całości (docs/converters.md, „Live sources”):
cała mapa, każdy odczyt, którego bajty różnią się od ostatnio zachowanej kopii, w
surowym pliku pomocniczym sesji pod `type` `r3e` lub `pcars2` – każdy slot kierowcy
i każde pole struktury, także te nieodczytane tutaj, więc późniejszy dekoder potrzebuje
tylko tego pliku.

Ten sam moduł obsługuje też: [Automobilista 2 (dane na żywo)](game-automobilista-2.md), [RaceRoom Racing Experience (dane na żywo)](game-raceroom.md).

## Pozycje i osie {#positions-and-axes}

| | |
|---|---|
| Zapisane pozycje | tak |
| Oś pionowa | `y` |
| Jednostki | metry |
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

- dla każdego uczestnika (do 64): aktywność, nazwa, pozycja w świecie, pozycja w wyścigu, ukończone okrążenia; jego ostatni czas okrążenia, stan wyścigu i prędkość
- auto gracza (mViewedParticipantIndex), stan gry i sesji, położenie i wariant toru, najlepsze i ostatnie okrążenie, prędkość, hamulec, gaz, bieg; mSequenceNumber, by pominąć kopię złapaną w trakcie zapisu
- przesunięcia z dwóch niezależnych kopii SharedMemory.h SMS, które się zgadzają, sprawdzone na stronie zbudowanej z nich w testach; jeszcze nie sprawdzone w grze

**Zachowane w surowej postaci**

- `pcars2`: cała mapa $pcars2$ – struktura sięga znacznie dalej niż 11 312 odczytanych tutaj bajtów – każdy odczyt, którego bajty różnią się od ostatnio zachowanej kopii: orientacja każdego uczestnika, czasy sektorów, nazwy aut i klas, tryby i flagi boksów, fizyka gracza, opony, zawieszenie, uszkodzenia, pogoda oraz wszystko, co późniejsze wersje Project CARS 2 dopisały
- `used` jest prawdą dla strony odczytanej do wierszy; fałszem dla strony z menu, podczas pauzy, w powtórce, o innym układzie lub złapanej w trakcie zapisu (`torn` 1); `unchanged_reads` w meta.json liczy odczyty bajt w bajt takie jak kopia zachowana wcześniej

**Niedostępne**

- wejścia i fizyka innych uczestników: strona podaje tylko oglądane auto
- wszystko, gdy opcja pamięci współdzielonej w grze jest wyłączona (Project CARS 2 wtedy niczego nie zapisuje)

**Rozmiar**: mapa ma około 20 do 30 KB (zależnie od wersji gry), do 10 razy na sekundę podczas jazdy: mniej więcej 0,7 do 1,1 GB na godzinę przed kompresją; zstd zmniejsza puste sloty uczestników i nazwy, które się nie zmieniają, do ułamka (jeszcze nie zmierzone na prawdziwej sesji)

## Sprawdzone {#verified}

przetestowane na stronie zbudowanej w teście; przesunięcia z dwóch niezależnych kopii SharedMemory.h, które się zgadzają, a nie z kopii dostarczanej przez grę; nie przetestowane w grze

## Źródło {#source}

[heat3d_watch/adapters/simracing_shm.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/simracing_shm.py)

<!-- Generated from the adapter by tools/gen_game_pages.py; change the adapter and run it again rather than editing this page. -->
