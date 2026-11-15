---
title: "DiRT Rally 2.0 (dane na żywo)"
nav_order: 11
lang: "pl"
source: game-dirt-rally-2.md
source_hash: "367131ff990b"
nav_exclude: true
search_exclude: true
---
# DiRT Rally 2.0 (dane na żywo) {#dirt-rally-20-live-data}

Gdy grasz w DiRT Rally 2.0, watcher zapisuje dane, które sama gra wysyła na zewnątrz, dzięki czemu później możesz je obejrzeć na mapie w przeglądarce 3DHeat.

*Szczegóły techniczne: adapter `dirt-rally-2`, rodzaj [`telemetry`](sources-and-rules.md); działa, gdy uruchomiony jest `dirtrally2.exe`, i sprawdza nowe dane co 0,1 s.*

## Co jest zapisywane {#what-is-recorded}

- pozycja własnego auta (XYZ w świecie, m) 10 razy na sekundę (10 Hz), wraz z prędkością, biegiem, gazem, hamulcem i dystansem na odcinku
- start odcinka (uruchomienie zegara odcinka), koniec z czasem odcinka, restarty
- teleporty (reset na drogę): `teleport` – gdzie auto było, `spawn` – gdzie jest teraz
- odcinki, najlepszy czas odcinka, dystans, prędkość maksymalna

## Skąd pochodzą dane {#where-it-comes-from}

UDP 127.0.0.1:20777, extradata=3 (Dokumenty\My Games\DiRT Rally 2.0\hardwaresettings\hardware_settings_config.xml); dopóki inna aplikacja trzyma port 20777, watcher zostawia mu port

## Jak to włączyć {#how-to-switch-it-on}

`python -m heat3d_watch setup dirt-rally-2 --apply` ustawia &lt;udp enabled=„true” extradata=„3”> (najpierw tworzy kopię zapasową)

Wpisz polecenie w terminalu otwartym w folderze watchera (zob. [Zanim zaczniesz](before-you-start.md)). Jeśli się nie uda, ostatnia linia powie dlaczego; [Instalacja i uruchamianie](installing-and-running.md) opisuje częste przyczyny.

`python -m heat3d_watch setup dirt-rally-2` pokazuje pliki, które zostałyby zmienione; `python -m heat3d_watch setup dirt-rally-2 --apply` zmienia je, zachowując oryginał jako `<file>.heat3d-backup` (zob. [Polecenia](commands.md#setup)). Dla każdej zmiany drukuje `dirt-rally-2: changed: ...`, a gdy opcja jest już włączona, `dirt-rally-2: nothing to change`.

## Jak to działa {#how-it-works}

Telemetria wyścigowa gier: Forza, gry Assetto Corsa, gry rajdowe i BeamNG, zapisywana jako trasy, okrążenia i odcinki.

Każda z tych gier publikuje telemetrię celowo, dla pulpitów i platform ruchu; nic nie jest wstrzykiwane i nic, czego gra nie udostępnia, nie jest odczytywane. Dekodowanie nie jest napisane dwa razy: to rejestratory okrążeń z GameCapture 3DHeat, w `heat3d_capture/telemetry`, skopiowane do `heat3d_watch/decoders` (przetestowane tam na pakietach zbudowanych z opublikowanych układów). Ten moduł zamienia ich klatki na wiersze watchera: pozycję auta kilka razy na sekundę wraz z prędkością, biegiem i pedałami, zdarzenie na każde okrążenie lub odcinek oraz liczby, które kierowca zachowuje: okrążenia, najlepsze okrążenie, dystans, prędkość maksymalną.

#### Forza (Horizon 4/5/6, Motorsport) {#forza-horizon-456-motorsport}

„Data Out” UDP, włączane w ustawieniach gry HUD i rozgrywki, na 127.0.0.1 port 5300, format Dash. Jeden pakiet na każdy takt symulacji; przesunięcie bloku dash jest odnajdywane z pakietów (`forza.detect_layout`). Metry świata, Y w górę; świat jest lewoskrętny i jest rysowany tak, jak został wysłany, tak jak robi to rejestrator okrążeń (dokumentacja „Data Out” Forza Motorsport i Forza Horizon).
Gra wysyła do jednego portu, a FH Companion i inne aplikacje Data Out nasłuchują na tym samym. Dwa programy nie mogą go dzielić: w Windows gniazdo związane z 127.0.0.1 dostaje pakiety, a gniazdo związane ze wszystkimi adresami na tym samym porcie nie dostaje żadnego, bez względu na to, które było pierwsze. Dlatego watcher czeka chwilę po starcie gry, zanim zajmie port, nigdy nie zabiera go aplikacji, która go trzyma, i zwalnia go, gdy inna aplikacja zacznie tam nasłuchiwać. Dopóki trzyma port, przekazuje każdy pakiet bez zmian na 127.0.0.1:5301 – ustaw pole portu FH Companion (zakładka telemetrii) na 5301, a oba nagrywają.

#### EA SPORTS WRC, DiRT Rally 2.0, Richard Burns Rally {#ea-sports-wrc-dirt-rally-20-richard-burns-rally}

UDP: `Documents/My Games/WRC/telemetry/config.json` w WRC (pakiet `session_update` struktury `wrc`), `hardware_settings_config.xml` w DiRT (`<udp enabled="true" extradata="3" port="20777">`), wtyczka NGP w RBR (`udpTelemetry=1`, port 6776). Odcinki według zegara odcinka gry (`rally.StageSplitter`). RBR nie dokumentuje swoich osi: oś pionowa to ta, wzdłuż której odcinek zmienia się najmniej, ustalana po zamknięciu sesji.

#### Wszystko zachowane {#everything-kept}

Wiersze to kilka na sekundę; gry wysyłają znacznie więcej. Każdy pakiet UDP, który dotrze – w menu, między okrążeniami, te, których żaden dekoder nie czyta – jest zachowany w całości w `heat.raw.parquet` sesji pod swoim formatem (`dash-horizon`, `session_update`, `extradata3`, `H3D1`, ...). Każda strona pamięci dzielonej (cały obszar mapowania, nie tylko zdekodowane bajty) jest zachowywana za każdym razem, gdy się zmieni, pod nazwą swojego mapowania (`acpmf_physics`, ...). `used` oznacza to, co stało się też wierszami; `selfCheck.completeness` w `meta.json` liczy każdy rodzaj (zasada konwertera 3DHeat).

Ten sam moduł obsługuje też: [Assetto Corsa (dane na żywo)](game-assetto-corsa.md), [Assetto Corsa Competizione (dane na żywo)](game-assetto-corsa-competizione.md), [Assetto Corsa EVO (dane na żywo)](game-assetto-corsa-evo.md), [Assetto Corsa Rally (dane na żywo)](game-assetto-corsa-rally.md), [BeamNG.drive (dane na żywo)](game-beamng.md), [EA SPORTS WRC (dane na żywo)](game-ea-wrc.md), [Forza Horizon 4 (dane na żywo)](game-forza-horizon-4.md), [Forza Horizon 5 (dane na żywo)](game-forza-horizon-5.md), [Forza Horizon 6 (dane na żywo)](game-forza-horizon-6.md), [Forza Motorsport (dane na żywo)](game-forza-motorsport.md), [Richard Burns Rally (dane na żywo)](game-richard-burns-rally.md).

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

`best_lap`, `best_stage`, `distance_km`, `laps`, `stages`, `top_speed_kmh`

Klucz w nawiasach klamrowych jest uzupełniany podczas działania (`score.{team}` to jeden klucz na zespół). Klucze, które kod bierze z tabeli pól gry albo z nazw statystyk gry, nie są na tej liście; „Co jest zapisywane” wyżej wymienia je.

## Kompletność {#completeness}

Watcher stosuje [zasadę konwertera](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md) 3DHeat: to, co źródło zawiera, jest czytane albo zachowywane, nigdy pomijane. Oprócz wierszy każdy pakiet, strona, linia lub odpowiedź, którą adapter otrzyma, jest zachowana w całości w `heat.raw.parquet` sesji (kolumny `time`, `ms`, `type`, `used`, `payload`, `text`, a potem każde pole zachowane po nazwie; `used` oznacza to, co stało się też wierszami). `selfCheck.completeness` w `meta.json` liczy każdy `type`; `lost` wynosi 0.

**Odczytane**

- wiersze 10 Hz: pozycja, prędkość, bieg, gaz, hamulec, dystans na odcinku, yaw, obroty, skręt; start odcinka, koniec z czasem odcinka, restarty

**Zachowane w surowej postaci**

- każdy pakiet, który dotrze do portu, w całości, z tempem gry, pod swoim formatem: `extradata3` (66 floatów, 264 bajty), `extradata3-64` (64 w DiRT Rally), `<n>-byte` w pozostałych przypadkach
- w pakiecie, poza wierszami: wszystkie 66 floatów – prędkość w świecie, wektory boczny i przedni, położenie i prędkość zawieszenia każdego koła, prędkość na styku opony i temperatura hamulców, siły g, okrążenia, długość odcinka; floaty bez ustalonej nazwy są w plikach okrążeń jako `float<i>`

**Niedostępne**

- inne auta: gra wysyła tylko auto gracza
- kanał ręcznego hamulca: pakiet go nie ma

**Rozmiar**: około 70 MB na godzinę przy 60 pakietach na sekundę (264 bajty plus 70-bajtowy nagłówek elementu); zstd zostawia z tego ułamek

## Sprawdzone {#verified}

dekodowanie pochodzi z rejestratora okrążeń GameCapture (testowanego na pakietach zbudowanych z opisanych układów); adapter testowany na pakietach zbudowanych w teście i wysyłanych przez UDP; niesprawdzone w grze

## Źródło {#source}

[heat3d_watch/adapters/racing.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/racing.py)

<!-- Generated from the adapter by tools/gen_game_pages.py; change the adapter and run it again rather than editing this page. -->
