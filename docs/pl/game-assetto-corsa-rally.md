---
title: "Assetto Corsa Rally (dane na żywo)"
nav_order: 5
lang: "pl"
source: game-assetto-corsa-rally.md
source_hash: "09b8a6d66e31"
nav_exclude: true
search_exclude: true
---
# Assetto Corsa Rally (dane na żywo) {#assetto-corsa-rally-live-data}

Gdy grasz w Assetto Corsa Rally, watcher zapisuje dane, które sama gra wysyła na zewnątrz, dzięki czemu później możesz je obejrzeć na mapie w przeglądarce 3DHeat.

*Szczegóły techniczne: adapter `assetto-corsa-rally`, rodzaj [`telemetry`](sources-and-rules.md); działa, gdy uruchomiony jest `acr.exe`, `ACR-Win64-Shipping.exe`, `AssettoCorsaRally.exe` lub `acrally-Win64-Shipping.exe`, i sprawdza nowe dane co 0,1 s.*

## Co jest zapisywane {#what-is-recorded}

- pozycja własnego auta (świat XYZ, m: średnia z punktów styku opon) 10 razy na sekundę (10 Hz), wraz z prędkością, biegiem, gazem i hamulcem
- początek i koniec sesji z torem i autem, które podaje gra
- odcinki: każdy kończy się tam, gdzie auto zatrzymuje się po nim, z czasem, który zajął
- teleporty (powrót do boksów, restart): `teleport` – gdzie auto było, `spawn` – gdzie jest teraz
- okrążenia, najlepsze okrążenie, dystans, prędkość maksymalna

## Skąd pochodzą dane {#where-it-comes-from}

pamięć współdzielona Local\acpmf_physics, Local\acpmf_static (te same strony co w AC i ACC)

## Jak to włączyć {#how-to-switch-it-on}

Nic nie trzeba włączać: watcher odczytuje źródło tak, jak udostępnia je gra lub platforma.

## Jak to działa {#how-it-works}

Telemetria wyścigowa gier: Forza, gry Assetto Corsa, gry rajdowe i BeamNG, zapisywana jako trasy, okrążenia i odcinki.

Każda z tych gier publikuje telemetrię celowo, dla pulpitów i platform ruchu; nic nie jest wstrzykiwane i nic, czego gra nie udostępnia, nie jest odczytywane. Dekodowanie nie jest napisane dwa razy: to rejestratory okrążeń z GameCapture 3DHeat, w `heat3d_capture/telemetry`, skopiowane do `heat3d_watch/decoders` (przetestowane tam na pakietach zbudowanych z opublikowanych układów), a ten moduł zamienia ich ramki na wiersze watchera: pozycja auta kilka razy na sekundę wraz z prędkością, biegiem i pedałami, zdarzenie na każde okrążenie lub odcinek oraz liczby, które zapisuje kierowca: okrążenia, najlepsze okrążenie, dystans, prędkość maksymalna.

#### Forza (Horizon 4/5/6, Motorsport) {#forza-horizon-456-motorsport}

„Data Out” UDP, włączane w ustawieniach gry HUD i rozgrywka, na 127.0.0.1 port 5300, format Dash. Jeden pakiet na takt symulacji; przesunięcie bloku dash jest odnajdywane z pakietów (`forza.detect_layout`). Metry świata, Y w górę; świat jest lewoskrętny i jest rysowany tak, jak został wysłany, jak robi to rejestrator okrążeń (dokumentacja „Data Out” Forza Motorsport i Forza Horizon). Gra wysyła do jednego portu, a FH Companion i inne aplikacje Data Out nasłuchują na tym samym. Dwa programy nie mogą go dzielić: w Windows gniazdo związane z 127.0.0.1 dostaje pakiety, a gniazdo związane ze wszystkimi adresami na tym samym porcie nie dostaje żadnego, bez względu na to, które uruchomiono pierwsze. Dlatego watcher czeka chwilę po starcie gry, zanim zajmie port, nigdy nie odbiera go aplikacji, która go trzyma, i zwalnia go, gdy inna aplikacja zaczyna tam nasłuchiwać. Dopóki trzyma port, przekazuje każdy pakiet bez zmian na 127.0.0.1:5301 – ustaw pole portu w zakładce telemetrii FH Companion na 5301, a oba nagrają.

#### Wszystko zachowane {#everything-kept}

Wierszy jest kilka na sekundę; gry wysyłają znacznie więcej. Każdy pakiet UDP, który dotrze – w menu, między okrążeniami, te, których żaden dekoder nie czyta – jest zachowany w całości w `heat.raw.parquet` sesji pod swoim formatem (`dash-horizon`, `session_update`, `extradata3`, `H3D1`, ...), a każda strona pamięci współdzielonej (cały obszar mapowania, nie tylko odczytane bajty) za każdym razem, gdy się zmieni, pod nazwą swojego mapowania (`acpmf_physics`, ...). `used` oznacza to, co stało się też wierszami; `selfCheck.completeness` w `meta.json` liczy każdy rodzaj (zasada konwertera 3DHeat).

Ten sam moduł obsługuje też: [Assetto Corsa (dane na żywo)](game-assetto-corsa.md), [Assetto Corsa Competizione (dane na żywo)](game-assetto-corsa-competizione.md), [Assetto Corsa EVO (dane na żywo)](game-assetto-corsa-evo.md), [BeamNG.drive (dane na żywo)](game-beamng.md), [DiRT Rally 2.0 (dane na żywo)](game-dirt-rally-2.md), [EA SPORTS WRC (dane na żywo)](game-ea-wrc.md), [Forza Horizon 4 (dane na żywo)](game-forza-horizon-4.md), [Forza Horizon 5 (dane na żywo)](game-forza-horizon-5.md), [Forza Horizon 6 (dane na żywo)](game-forza-horizon-6.md), [Forza Motorsport (dane na żywo)](game-forza-motorsport.md), [Richard Burns Rally (dane na żywo)](game-richard-burns-rally.md).

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

`best_lap`, `best_stage`, `distance_km`, `laps`, `race_position`, `stages`, `top_speed_kmh`

Klucz w nawiasach klamrowych jest uzupełniany w czasie działania (`score.{team}` to jeden klucz na zespół). Klucze, które kod bierze z tabeli pól gry lub z jej własnych nazw statystyk, nie są na tej liście; sekcja „Co jest zapisywane” wyżej wymienia je.

## Kompletność {#completeness}

Watcher stosuje [zasadę konwertera 3DHeat](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md): to, co źródło zawiera, jest odczytywane lub zachowywane, nigdy nie jest pomijane. Oprócz wierszy każdy pakiet, strona, linia lub odpowiedź, którą adapter otrzyma, jest zachowana w całości w `heat.raw.parquet` sesji (kolumny `time`, `ms`, `type`, `used`, `payload`, `text`, a potem każde pole zachowane po nazwie; `used` oznacza to, co stało się też wierszami), a `selfCheck.completeness` w `meta.json` liczy każdy `type` – `lost` wynosi 0.

**Odczytane**

- wiersze 10 Hz ze strony fizyki: pozycja (średnia z punktów styku opon), prędkość, bieg, gaz, hamulec, yaw/pitch/roll (rad), obroty, skręt (tak, jak strona go ma); początek sesji z torem i autem ze strony statycznej; okrążenia, pozycja w wyścigu

**Zachowane w surowej postaci**

- każda strona w całości – cały obszar mapowania, nie tylko odczytane bajty – za każdym razem, gdy zmienią się jej bajty, przy odczycie watchera 10 razy na sekundę: `acpmf_physics`, `acpmf_static`; odczyt bajt w bajt taki sam jak poprzedni jest liczony w `unchanged_reads` w meta.json, a nie zapisywany ponownie
- wszystko dekodowane tylko dla plików okrążeń (`decoders/kunos.py`: poślizg każdego koła, obciążenie, ciśnienie, temperatury, pochylenie, zawieszenie, punkty styku, temperatury hamulców, współczynnik i kąt poślizgu; prędkość w świecie i lokalna, prędkość kątowa, wspomagania) jest na tych stronach

**Niedostępne**

- pozycje innych aut: strony opisują tylko auto gracza (strona graficzna ACC ma w niektórych wersjach id i współrzędne innych aut – zachowane w surowej stronie, nie dekodowane)
- ticki fizyki między odczytami watchera: gra przepisuje stronę z częstotliwością fizyki (do 333 Hz), a watcher czyta 10 razy na sekundę
- zegar odcinka ani czas odcinka z gry: AC Rally nie publikuje strony graficznej; odcinki kończą się tam, gdzie auto się zatrzymuje

**Rozmiar**: około 150-300 MB na godzinę przed kompresją (region 4 KB na stronę, do 10 zmian na sekundę); strony są w większości zerami, a zstd zostawia z nich niewielki ułamek

## Sprawdzone {#verified}

dekodowanie pochodzi z rejestratora okrążeń GameCapture (przetestowane na syntetycznych stronach); adapter przetestowany na pamięci współdzielonej zbudowanej w teście na podstawie opisanego układu; nie przetestowany w grze; nazwa pliku wykonywalnego nie jest potwierdzona

## Źródło {#source}

[heat3d_watch/adapters/racing.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/racing.py)

<!-- Generated from the adapter by tools/gen_game_pages.py; change the adapter and run it again rather than editing this page. -->
