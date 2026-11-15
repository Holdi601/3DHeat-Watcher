---
title: "Assetto Corsa (dane na żywo)"
nav_order: 2
lang: "pl"
source: game-assetto-corsa.md
source_hash: "9132272cc104"
nav_exclude: true
search_exclude: true
---
# Assetto Corsa (dane na żywo) {#assetto-corsa-live-data}

Gdy grasz w Assetto Corsa, watcher zapisuje dane, które sama gra wysyła na zewnątrz, dzięki czemu później możesz je obejrzeć na mapie w przeglądarce 3DHeat.

*Szczegóły techniczne: adapter `assetto-corsa`, rodzaj [`telemetry`](sources-and-rules.md); działa, gdy uruchomiony jest `acs.exe` lub `acs_x86.exe`, i sprawdza nowe dane co 0,1 s.*

## Co jest zapisywane {#what-is-recorded}

- pozycja własnego auta (XYZ w świecie, m: średnia z punktów styku opon) 10 razy na sekundę (10 Hz), wraz z prędkością, biegiem, gazem i hamulcem
- początek i koniec sesji z torem i autem, które podaje gra
- okrążenia według licznika okrążeń gry, z jego czasem
- teleporty (powrót do boksów, restart): `teleport` – gdzie auto było, `spawn` – gdzie jest teraz
- okrążenia, najlepsze okrążenie, dystans, prędkość maksymalna

## Skąd pochodzą dane {#where-it-comes-from}

pamięć dzielona Local\acpmf_physics, Local\acpmf_graphics, Local\acpmf_static

## Jak to włączyć {#how-to-switch-it-on}

Nic nie trzeba włączać: watcher czyta źródło tak, jak podaje je gra lub platforma.

## Jak to działa {#how-it-works}

Telemetria wyścigowa gier: Forza, gry Assetto Corsa, gry rajdowe i BeamNG, zapisywana jako trasy, okrążenia i odcinki.

Każda z tych gier publikuje telemetrię celowo, dla pulpitów i platform ruchu; nic nie jest wstrzykiwane i nic, czego gra nie udostępnia, nie jest odczytywane. Dekodowanie nie jest napisane dwa razy: to rejestratory okrążeń z GameCapture 3DHeat, w `heat3d_capture/telemetry`, skopiowane do `heat3d_watch/decoders` (przetestowane tam na pakietach zbudowanych z opublikowanych układów). Ten moduł zamienia ich klatki na wiersze watchera: pozycję auta kilka razy na sekundę wraz z prędkością, biegiem i pedałami, zdarzenie na każde okrążenie lub odcinek oraz liczby, które kierowca zachowuje: okrążenia, najlepsze okrążenie, dystans, prędkość maksymalną.

#### Forza (Horizon 4/5/6, Motorsport) {#forza-horizon-456-motorsport}

„Data Out” UDP, włączane w ustawieniach gry HUD i rozgrywki, na 127.0.0.1 port 5300, format Dash. Jeden pakiet na każdy takt symulacji; przesunięcie bloku dash jest odnajdywane z pakietów (`forza.detect_layout`). Metry świata, Y w górę; świat jest lewoskrętny i jest rysowany tak, jak został wysłany, tak jak robi to rejestrator okrążeń (dokumentacja „Data Out” Forza Motorsport i Forza Horizon).
Gra wysyła do jednego portu, a FH Companion i inne aplikacje Data Out nasłuchują na tym samym. Dwa programy nie mogą go dzielić: w Windows gniazdo związane z 127.0.0.1 dostaje pakiety, a gniazdo związane ze wszystkimi adresami na tym samym porcie nie dostaje żadnego, bez względu na to, które było pierwsze. Dlatego watcher czeka chwilę po starcie gry, zanim zajmie port, nigdy nie zabiera go aplikacji, która go trzyma, i zwalnia go, gdy inna aplikacja zacznie tam nasłuchiwać. Dopóki trzyma port, przekazuje każdy pakiet bez zmian na 127.0.0.1:5301 – ustaw pole portu FH Companion (zakładka telemetrii) na 5301, a oba nagrywają.

#### Assetto Corsa, ACC, AC EVO, AC Rally {#assetto-corsa-acc-ac-evo-ac-rally}

Pamięć dzielona, którą gra zapisuje dla aplikacji: `Local\acpmf_physics`, `Local\acpmf_graphics`, `Local\acpmf_static` (AC EVO: `Local\acevo_pmf_*`). Otwierana tylko do odczytu i dopiero wtedy, gdy gra ją utworzy (`simracing_shm`). Pozycja to średnia z czterech punktów styku opon, metry świata, Y w górę. Okrążenia według licznika gry (AC, ACC) albo przez ponowne przejechanie punktu startu (AC EVO, AC Rally), tak jak robi to `kunos.py` dla rejestratora okrążeń.

#### Wszystko zachowane {#everything-kept}

Wiersze to kilka na sekundę; gry wysyłają znacznie więcej. Każdy pakiet UDP, który dotrze – w menu, między okrążeniami, te, których żaden dekoder nie czyta – jest zachowany w całości w `heat.raw.parquet` sesji pod swoim formatem (`dash-horizon`, `session_update`, `extradata3`, `H3D1`, ...). Każda strona pamięci dzielonej (cały obszar mapowania, nie tylko zdekodowane bajty) jest zachowywana za każdym razem, gdy się zmieni, pod nazwą swojego mapowania (`acpmf_physics`, ...). `used` oznacza to, co stało się też wierszami; `selfCheck.completeness` w `meta.json` liczy każdy rodzaj (zasada konwertera 3DHeat).

Ten sam moduł obsługuje też: [Assetto Corsa Competizione (dane na żywo)](game-assetto-corsa-competizione.md), [Assetto Corsa EVO (dane na żywo)](game-assetto-corsa-evo.md), [Assetto Corsa Rally (dane na żywo)](game-assetto-corsa-rally.md), [BeamNG.drive (dane na żywo)](game-beamng.md), [DiRT Rally 2.0 (dane na żywo)](game-dirt-rally-2.md), [EA SPORTS WRC (dane na żywo)](game-ea-wrc.md), [Forza Horizon 4 (dane na żywo)](game-forza-horizon-4.md), [Forza Horizon 5 (dane na żywo)](game-forza-horizon-5.md), [Forza Horizon 6 (dane na żywo)](game-forza-horizon-6.md), [Forza Motorsport (dane na żywo)](game-forza-motorsport.md), [Richard Burns Rally (dane na żywo)](game-richard-burns-rally.md).

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

- Oznaczona jako gra sieciowa (`multiplayer`): **tak**. `games --markdown` pokazuje to jako „allowed (reads only what the game publishes)”.
- Rodzaj `telemetry`: czyta tylko to, co gra lub platforma udostępnia (port UDP albo pamięć dzielona, które gra publikuje), więc nagrywa także w grze sieciowej, tak jak w trybie offline. Flaga decyduje tylko o tym, czy pamięć w ogóle może być czytana.
- Pamięć: **nigdy** nie jest czytana przez ten adapter. Tylko adaptery `memory` czytają pamięć, i nigdy dla gry oznaczonej jako sieciowa – zob. [Źródła i zasady](sources-and-rules.md).

## Co jest zapisywane w statystykach {#statistics-recorded}

Klucze statystyk, które kod tego adaptera ustawia po nazwie (`stats` każdej sesji w `meta.json` i tabela `stats` w `watcher.sqlite`):

`best_lap`, `best_stage`, `distance_km`, `laps`, `race_position`, `stages`, `top_speed_kmh`

Klucz w nawiasach klamrowych jest uzupełniany podczas działania (`score.{team}` to jeden klucz na zespół). Klucze, które kod bierze z tabeli pól gry albo z nazw statystyk gry, nie są na tej liście; „Co jest zapisywane” wyżej wymienia je.

## Kompletność {#completeness}

Watcher stosuje [zasadę konwertera](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md) 3DHeat: to, co źródło zawiera, jest czytane albo zachowywane, nigdy pomijane. Oprócz wierszy każdy pakiet, strona, linia lub odpowiedź, którą adapter otrzyma, jest zachowana w całości w `heat.raw.parquet` sesji (kolumny `time`, `ms`, `type`, `used`, `payload`, `text`, a potem każde pole zachowane po nazwie; `used` oznacza to, co stało się też wierszami). `selfCheck.completeness` w `meta.json` liczy każdy `type`; `lost` wynosi 0.

**Odczytane**

- wiersze 10 razy na sekundę ze strony physics: pozycja (średnia z punktów styku opon), prędkość, bieg, gaz, hamulec, yaw/pitch/roll (rad), obroty, skręt (tak, jak podaje go strona); początek sesji z torem i autem ze strony static; okrążenia, pozycja w wyścigu

**Zachowane w surowej postaci**

- każda strona w całości – cały obszar mapowania, nie tylko zdekodowane bajty – za każdym razem, gdy jej bajty się zmienią, przy odczycie watchera 10 razy na sekundę: `acpmf_physics`, `acpmf_graphics`, `acpmf_static`; odczyt bajt w bajt taki sam jak poprzedni jest liczony w `unchanged_reads` w meta.json, a nie zapisywany ponownie
- wszystko, co zdekodowano tylko dla plików okrążeń (`decoders/kunos.py`: poślizg, obciążenie, ciśnienie, temperatury, pochylenie, zawieszenie, punkty styku, temperatury hamulców, współczynnik i kąt poślizgu każdego koła; prędkość w świecie i lokalna, prędkość kątowa, wspomaganie jazdy), znajduje się na tych stronach

**Niedostępne**

- pozycje innych aut: strony opisują tylko auto gracza (strona graficzna ACC ma w niektórych wersjach id aut i ich współrzędne – zachowane w surowej stronie, nie dekodowane)
- ticki fizyki między odczytami watchera: gra przepisuje stronę z częstotliwością fizyki (do 333 Hz), a watcher czyta 10 razy na sekundę

**Rozmiar**: około 150–300 MB na godzinę przed kompresją (obszar 4 KB na stronę, przy zmianach do 10 razy na sekundę); strony są w większości zerami, a zstd zostawia z nich niewielki ułamek

## Sprawdzone {#verified}

dekodowanie pochodzi z rejestratora okrążeń GameCapture (testowanego na syntetycznych stronach); adapter testowany na pamięci dzielonej zbudowanej w teście wg opisanego układu; niesprawdzone w grze

## Źródło {#source}

[heat3d_watch/adapters/racing.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/racing.py)

<!-- Generated from the adapter by tools/gen_game_pages.py; change the adapter and run it again rather than editing this page. -->
