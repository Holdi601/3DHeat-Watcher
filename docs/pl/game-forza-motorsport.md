---
title: "Forza Motorsport (dane na żywo)"
nav_order: 24
lang: "pl"
source: game-forza-motorsport.md
source_hash: "d411fbb6ebea"
nav_exclude: true
search_exclude: true
---
# Forza Motorsport (dane na żywo) {#forza-motorsport-live-data}

Gdy grasz w Forza Motorsport, watcher zapisuje dane, które sama gra wysyła na zewnątrz, dzięki czemu później możesz je obejrzeć na mapie w przeglądarce 3DHeat.

*Szczegóły techniczne: adapter `forza-motorsport`, rodzaj [`telemetry`](sources-and-rules.md); działa, gdy uruchomiony jest `forza_steamworks_release_final.exe`, `forza_gaming.desktop.x64_release_final.exe` lub `ForzaMotorsport7.exe`, i sprawdza nowe dane co 0,1 s.*

## Co jest zapisywane {#what-is-recorded}

- pozycja własnego auta (XYZ w świecie, m) 10 razy na sekundę (10 Hz), wraz z prędkością, biegiem, gazem, hamulcem i okrążeniem
- początek i koniec jazdy (session_start/session_end), okrążenia z czasem podanym przez grę
- start i meta wyścigu wraz z pozycją w wyścigu
- teleporty (cofnięcie czasu, szybka podróż): `teleport` – gdzie auto było, `spawn` – gdzie jest teraz
- okrążenia, najlepsze okrążenie, dystans, prędkość maksymalna, wyścigi

## Skąd pochodzą dane {#where-it-comes-from}

Forza Data Out, UDP 127.0.0.1:5300 (format Dash); każdy pakiet przekazywany bez zmian na 127.0.0.1:5301

## Jak to włączyć {#how-to-switch-it-on}

W grze: Ustawienia > HUD i rozgrywka > Data Out Wł., IP 127.0.0.1, port 5300 (Motorsport: format Dash). FH Companion lub inna aplikacja Data Out: ustaw jej port na 5301 – watcher przekazuje każdy pakiet dalej; gdy inna aplikacja nasłuchuje na 5300, watcher zostawia jej port i nic nie nagrywa

## Jak to działa {#how-it-works}

Telemetria wyścigowa gier: Forza, gry Assetto Corsa, gry rajdowe i BeamNG, zapisywana jako trasy, okrążenia i odcinki.

Każda z tych gier publikuje telemetrię celowo, dla pulpitów i platform ruchu; nic nie jest wstrzykiwane i nic, czego gra nie udostępnia, nie jest odczytywane. Dekodowanie nie jest napisane dwa razy: to rejestratory okrążeń z GameCapture 3DHeat, w `heat3d_capture/telemetry`, skopiowane do `heat3d_watch/decoders` (przetestowane tam na pakietach zbudowanych z opublikowanych układów). Ten moduł zamienia ich klatki na wiersze watchera: pozycję auta kilka razy na sekundę wraz z prędkością, biegiem i pedałami, zdarzenie na każde okrążenie lub odcinek oraz liczby, które kierowca zachowuje: okrążenia, najlepsze okrążenie, dystans, prędkość maksymalną.

#### Forza (Horizon 4/5/6, Motorsport) {#forza-horizon-456-motorsport}

„Data Out” UDP, włączane w ustawieniach gry HUD i rozgrywki, na 127.0.0.1 port 5300, format Dash. Jeden pakiet na każdy takt symulacji; przesunięcie bloku dash jest odnajdywane z pakietów (`forza.detect_layout`). Metry świata, Y w górę; świat jest lewoskrętny i jest rysowany tak, jak został wysłany, tak jak robi to rejestrator okrążeń (dokumentacja „Data Out” Forza Motorsport i Forza Horizon).
Gra wysyła do jednego portu, a FH Companion i inne aplikacje Data Out nasłuchują na tym samym. Dwa programy nie mogą go dzielić: w Windows gniazdo związane z 127.0.0.1 dostaje pakiety, a gniazdo związane ze wszystkimi adresami na tym samym porcie nie dostaje żadnego, bez względu na to, które było pierwsze. Dlatego watcher czeka chwilę po starcie gry, zanim zajmie port, nigdy nie zabiera go aplikacji, która go trzyma, i zwalnia go, gdy inna aplikacja zacznie tam nasłuchiwać. Dopóki trzyma port, przekazuje każdy pakiet bez zmian na 127.0.0.1:5301 – ustaw pole portu FH Companion (zakładka telemetrii) na 5301, a oba nagrywają.

#### Wszystko zachowane {#everything-kept}

Wiersze to kilka na sekundę; gry wysyłają znacznie więcej. Każdy pakiet UDP, który dotrze – w menu, między okrążeniami, te, których żaden dekoder nie czyta – jest zachowany w całości w `heat.raw.parquet` sesji pod swoim formatem (`dash-horizon`, `session_update`, `extradata3`, `H3D1`, ...). Każda strona pamięci dzielonej (cały obszar mapowania, nie tylko zdekodowane bajty) jest zachowywana za każdym razem, gdy się zmieni, pod nazwą swojego mapowania (`acpmf_physics`, ...). `used` oznacza to, co stało się też wierszami; `selfCheck.completeness` w `meta.json` liczy każdy rodzaj (zasada konwertera 3DHeat).

Ten sam moduł obsługuje też: [Assetto Corsa (dane na żywo)](game-assetto-corsa.md), [Assetto Corsa Competizione (dane na żywo)](game-assetto-corsa-competizione.md), [Assetto Corsa EVO (dane na żywo)](game-assetto-corsa-evo.md), [Assetto Corsa Rally (dane na żywo)](game-assetto-corsa-rally.md), [BeamNG.drive (dane na żywo)](game-beamng.md), [DiRT Rally 2.0 (dane na żywo)](game-dirt-rally-2.md), [EA SPORTS WRC (dane na żywo)](game-ea-wrc.md), [Forza Horizon 4 (dane na żywo)](game-forza-horizon-4.md), [Forza Horizon 5 (dane na żywo)](game-forza-horizon-5.md), [Forza Horizon 6 (dane na żywo)](game-forza-horizon-6.md), [Richard Burns Rally (dane na żywo)](game-richard-burns-rally.md).

## Pozycje i osie {#positions-and-axes}

| | |
|---|---|
| Zapisane pozycje | tak |
| Oś pionowa | `y` |
| Jednostki | metry; świat Forzy jest lewoskrętny, rysowany tak, jak został wysłany, jak robi to rejestrator okrążeń |
| Odbicie dla przeglądarki | brak |
| Skala jednostki (`scale`: przeglądarka mnoży przez nią pozycje) | 1 |

Te wartości trafiają do `meta.json` każdej sesji (`axes`) i, gdy sesja ma pozycje, do stopki `heat.parquet`. Dzięki temu przeglądarka 3DHeat sama obraca i skaluje wiersze – zob. [Dane](the-data.md).

## Tryb wieloosobowy {#multiplayer}

- Oznaczona jako gra sieciowa (`multiplayer`): **tak**. `games --markdown` pokazuje to jako „allowed (reads only what the game publishes)”.
- Rodzaj `telemetry`: czyta tylko to, co gra lub platforma udostępnia (port UDP albo pamięć dzielona, które gra publikuje), więc nagrywa także w grze sieciowej, tak jak w trybie offline. Flaga decyduje tylko o tym, czy pamięć w ogóle może być czytana.
- Pamięć: **nigdy** nie jest czytana przez ten adapter. Tylko adaptery `memory` czytają pamięć, i nigdy dla gry oznaczonej jako sieciowa – zob. [Źródła i zasady](sources-and-rules.md).

## Co jest zapisywane w statystykach {#statistics-recorded}

Klucze statystyk, które kod tego adaptera ustawia po nazwie (`stats` każdej sesji w `meta.json` i tabela `stats` w `watcher.sqlite`):

`best_lap`, `distance_km`, `laps`, `races`, `top_speed_kmh`

Klucz w nawiasach klamrowych jest uzupełniany podczas działania (`score.{team}` to jeden klucz na zespół). Klucze, które kod bierze z tabeli pól gry albo z nazw statystyk gry, nie są na tej liście; „Co jest zapisywane” wyżej wymienia je.

## Kompletność {#completeness}

Watcher stosuje [zasadę konwertera](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md) 3DHeat: to, co źródło zawiera, jest czytane albo zachowywane, nigdy pomijane. Oprócz wierszy każdy pakiet, strona, linia lub odpowiedź, którą adapter otrzyma, jest zachowana w całości w `heat.raw.parquet` sesji (kolumny `time`, `ms`, `type`, `used`, `payload`, `text`, a potem każde pole zachowane po nazwie; `used` oznacza to, co stało się też wierszami). `selfCheck.completeness` w `meta.json` liczy każdy `type`; `lost` wynosi 0.

**Odczytane**

- wiersze 10 Hz: pozycja, prędkość, bieg, gaz, hamulec, okrążenie, yaw/pitch/roll (rad), obroty, skręt (-1..1); session_start z porządkowym numerem auta, klasą, PI i napędem; okrążenia z czasem podanym przez grę; pozycja w wyścigu

**Zachowane w surowej postaci**

- każdy pakiet, który dotrze do portu, w całości, z tempem gry (jeden na takt symulacji), pod swoim formatem: `dash-horizon` (324 bajty, Forza Horizon), `dash` (311, Motorsport 7), `dash-fm2023` (331, Forza Motorsport 2023: zużycie opon i id toru), `sled` (232, bez pozycji), `<n>-byte` dla wszystkiego innego – w tym pakiety z menu (isRaceOn 0), pakiety wstrzymane, dopóki układ dash nie zostanie potwierdzony, i ok. 13 bajtów pakietu Horizon, których żaden opublikowany układ nie nazywa
- każdy kanał koła z bloku Sled (współczynnik i kąt poślizgu, połączony poślizg, zawieszenie, prędkość koła, rumble, puddle), przyspieszenia, prędkość kątowa, moc, moment, doładowanie, paliwo, temperatury opon, sprzęgło, ręczny hamulec, linia jazdy, różnica hamowania AI: wszystko jest w pakietach, dekodowane z nich przez `decoders/fulllap.decode_full`

**Niedostępne**

- inne auta: Data Out opisuje tylko auto gracza
- nazwa toru lub trasy: Forza Horizon nigdy jej nie wysyła; Motorsport 2023 wysyła tylko numer toru
- pakiety, gdy inna aplikacja (FH Companion) trzyma port UDP 5300: watcher zostawia mu port

**Rozmiar**: około 85 MB na godzinę przed kompresją (60 pakietów na sekundę po 324 bajty plus 70-bajtowy nagłówek elementu); kolejne pakiety różnią się niewiele, więc zstd zostawia z nich ułamek

## Sprawdzone {#verified}

dekodowanie pochodzi z rejestratora okrążeń GameCapture (testowanego na pakietach zbudowanych z układu Data Out); adapter testowany na syntetycznych pakietach i na nagranych trajektoriach okrążeń odtwarzanych jako pakiety; niesprawdzone w samej grze

## Źródło {#source}

[heat3d_watch/adapters/racing.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/racing.py)

<!-- Generated from the adapter by tools/gen_game_pages.py; change the adapter and run it again rather than editing this page. -->
