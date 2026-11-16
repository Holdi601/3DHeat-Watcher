---
title: "World of Tanks (powtórki)"
nav_order: 48
lang: "pl"
source: game-wot-replays.md
source_hash: "4cff18c29936"
nav_exclude: true
search_exclude: true
---
# World of Tanks (powtórki) {#world-of-tanks-replays}

Po bitwie w World of Tanks watcher zamienia powtórkę, którą zapisała gra, na pliki, które możesz obejrzeć na mapie w przeglądarce 3DHeat.

*Szczegóły techniczne: adapter `wot-replays`, rodzaj [`replay`](sources-and-rules.md); działa cały czas (nie czeka na start gry) i szuka nowych danych co 5 s.*

## Co jest zapisywane {#what-is-recorded}

- pozycja i kierunek każdego pojazdu około 10 razy na sekundę, dopóki klient nagrywający go znał: swojej drużyny przez cały czas, wroga – gdy był widziany
- gracz, drużyna i pojazd (nacja:czołg) każdego; zgony, gdzie ofiara padła, i zabójstwa, gdzie zabójca stał, z dokładnością do około sekundy, z wyników
- mapa; zabójstwa, obrażenia, przeżycie i wynik nagrywającego gracza jako statystyki

## Skąd pochodzi {#where-it-comes-from}

powtórki, które zapisuje World of Tanks: &lt;World of Tanks>/replays/\*.wotreplay (przy włączonym nagrywaniu bitew), konwertowane zewnętrznym konwerterem `heat3d-wot-replay` (exporters/ext/wot-replay)

## Jak to włączyć {#how-to-switch-it-on}

włącz nagrywanie bitew w ustawieniach World of Tanks (General > Record battles) i zainstaluj konwerter: pip install -e &lt;3DHeat>/exporters/ext/wot-replay

Ustawienia ze zmiennych środowiskowych:

- `HEAT3D_WOT_REPLAY`: folder konwertera (klon albo rozpakowane wydanie), gdy nie jest zainstalowany ani nie leży obok watchera

## Jak to działa {#how-it-works}

Powtórki i dema: to, co gra zapisuje o meczu, zamieniane po jego zakończeniu.

Powtórka zawiera wszystko, co interfejs na żywo w grach wieloosobowych zatrzymuje dla siebie – pozycję każdego gracza, każde zabójstwo tam, gdzie się wydarzyło – i jest plikiem, który gra zapisuje dla swoich graczy, więc jej odczyt niczego w grze nie rusza. Watcher zagląda do folderów, w których gry je zapisują, czeka, aż nowy plik przestanie rosnąć (inaczej gra wciąż go zapisuje), i zamienia go w osobnym wątku, więc długa konwersja nigdy nie wstrzymuje reszty watchera.

Za pierwszym razem, gdy watcher widzi folder, powtórki, które już w nim są, tylko zapisuje na liście, nie konwertuje: gracz z latami dem czekałby inaczej cały dzień. `python -m heat3d_watch replays <adapter> [folder]` konwertuje istniejące na żądanie.

#### World of Tanks i World of Warships {#world-of-tanks-and-world-of-warships}

Obie zapisują powtórkę każdej bitwy do `<gra>/replays/`, gdy nagrywanie jest włączone (`*.wotreplay`, `*.wowsreplay`); instalacje są szukane przez listę Wargaming Game Center, `C:/Games/World_of_Tanks*` / `World_of_Warships*`, oraz przez Steam. Tak jak przy War Thunder, watcher sam ich nie czyta: robi to zewnętrzny konwerter każdej z gier (`exporters/ext/wot-replay`, polecenie `heat3d-wot-replay`; `exporters/ext/wows-replay`, polecenie `heat3d-wows-replay`), każdy jako osobny projekt. Znaleziony w PATH, zainstalowany albo leżący obok watchera zamienia każdą nową powtórkę w `<map>/<match>.parquet` i `<match>.match.json` w folderze sesji; gdy go brak, watcher raz podpowiada, jak go zainstalować. Linia nagrywającego gracza – pojazd albo okręt, zabójstwa, obrażenia (World of Tanks), czy przeżył, i wynik (World of Tanks) – staje się statystykami sesji. Co każdy konwerter czyta, a czego nie, jest w jego README.

Ten sam moduł obsługuje też: [Counter-Strike 2 (powtórki)](game-cs2-demos.md), [Dota 2 (powtórki)](game-dota-replays.md), [osu! (powtórki)](game-osu-replays.md), [Squad (powtórki)](game-squad-demos.md), [War Thunder (powtórki)](game-warthunder-replays.md), [World of Warships (powtórki)](game-wows-replays.md).

## Pozycje i osie {#positions-and-axes}

| | |
|---|---|
| Zapisywane pozycje | tak |
| Oś w górę | `y` |
| Jednostki | metry (x na wschód, y w górę, z na północ) |
| Odbicie dla przeglądarki | `z` |
| Skala jednostek (`scale`: przeglądarka mnoży przez nią pozycje) | 1 |

Trafiają one do `meta.json` każdej sesji (`axes`) i, gdy sesja ma pozycje, do stopki `heat.parquet`, więc przeglądarka 3DHeat sama obraca i skaluje wiersze – zob. [Dane](the-data.md).

## Gra wieloosobowa {#multiplayer}

- Oznaczona jako gra online (`multiplayer`): **tak**. `games --markdown` pokazuje to jako „dozwolone (czyta tylko to, co gra publikuje)”.
- Rodzaj `replay`: czyta tylko to, co gra lub platforma udostępnia (powtórki i dema, które gra zapisuje), więc zapisuje także w grze online, a nie tylko offline; flaga decyduje wyłącznie o tym, czy wolno kiedykolwiek czytać pamięć.
- Pamięć: **nigdy** nie jest czytana przez ten adapter. Tylko adaptery `memory` czytają pamięć i nigdy dla gry oznaczonej jako online – zob. [Źródła i zasady](sources-and-rules.md).

## Zapisywane statystyki {#statistics-recorded}

Klucze statystyk, które kod tego adaptera ustawia po nazwie (`stats` każdej sesji w `meta.json` i tabela `stats` w `watcher.sqlite`):

`map`, `survived`, `vehicle`, `won`

Klucz w nawiasach klamrowych jest uzupełniany w czasie działania (`score.{team}` to jeden klucz na drużynę). Klucze, które kod bierze z tabeli pól gry albo z nazw statystyk gry, nie są na tej liście; „Co jest zapisywane” wyżej wymienia je.

## Kompletność {#completeness}

Konwerter uruchamiany przez ten adapter stosuje [regułę konwertera](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md) 3DHeat: to, co zawiera powtórka, jest odczytane albo zachowane, nigdy nie porzucone – odczytane do tabeli i dokumentu meczu, a wszystko inne zachowane w całości w plikach pobocznych obok nich, policzone w `selfCheck.completeness` dokumentu meczu. Dokumentacja samego konwertera wymienia, co odczytuje, co zachowuje w surowej postaci i czego nie potrafi odczytać.

## Sprawdzone {#verified}

konwerter jest sprawdzany na publicznych powtórkach z kilku wersji gry i testami na zbudowanych powtórkach; ten hak – testami z zastępczym poleceniem

## Źródło {#source}

[heat3d_watch/adapters/replays.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/replays.py)

<!-- Generated from the adapter by tools/gen_game_pages.py; change the adapter and run it again rather than editing this page. -->
