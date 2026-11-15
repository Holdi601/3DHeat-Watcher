---
title: "War Thunder (powtórki)"
nav_order: 46
lang: "pl"
source: game-warthunder-replays.md
source_hash: "81f03926431d"
nav_exclude: true
search_exclude: true
---
# War Thunder (powtórki) {#war-thunder-replays}

Po bitwie w War Thunder watcher zamienia powtórkę, którą zapisała gra, na pliki, które możesz obejrzeć na mapie w przeglądarce 3DHeat.

*Szczegóły techniczne: adapter `warthunder-replays`, rodzaj [`replay`](sources-and-rules.md); działa cały czas (nie czeka na start gry) i szuka nowych danych co 5 s.*

## Co jest zapisywane {#what-is-recorded}

- pozycja i położenie każdego samolotu około 4 razy na sekundę (tyle, ile zawiera powtórka)
- pozycje jednostek naziemnych z synchronizacji naziemnej powtórki (w powtórkach z 2026; nie w tych z 2025)
- kim była każda jednostka (gracz, id pojazdu, drużyna), tam gdzie zabójstwo lub trafienie ją nazywa; zabójstwa, zgony i trafienia tam, gdzie się wydarzyły; czat; mapa
- zabójstwa, zgony, wynik i przejęcia autora powtórki jako statystyki

## Skąd pochodzi {#where-it-comes-from}

powtórki, które zapisuje War Thunder: &lt;War Thunder>/Replays/\*.wrpl (przy włączonym zapisywaniu powtórek), konwertowane zewnętrznym konwerterem `heat3d-wt-replay` (exporters/ext/warthunder-replay)

## Jak to włączyć {#how-to-switch-it-on}

włącz zapisywanie powtórek w opcjach War Thunder i zainstaluj konwerter: pip install -e &lt;3DHeat>/exporters/ext/warthunder-replay

Ustawienia ze zmiennych środowiskowych:

- `HEAT3D_WT_REPLAY`: folder konwertera (klon albo rozpakowane wydanie), gdy nie jest zainstalowany ani nie leży obok watchera

## Jak to działa {#how-it-works}

Powtórki i dema: to, co gra zapisuje o meczu, zamieniane po jego zakończeniu.

Powtórka zawiera wszystko, co interfejs na żywo w grach wieloosobowych zatrzymuje dla siebie – pozycję każdego gracza, każde zabójstwo tam, gdzie się wydarzyło – i jest plikiem, który gra zapisuje dla swoich graczy, więc jej odczyt niczego w grze nie rusza. Watcher zagląda do folderów, w których gry je zapisują, czeka, aż nowy plik przestanie rosnąć (inaczej gra wciąż go zapisuje), i zamienia go w osobnym wątku, więc długa konwersja nigdy nie wstrzymuje reszty watchera.

Za pierwszym razem, gdy watcher widzi folder, powtórki, które już w nim są, tylko zapisuje na liście, nie konwertuje: gracz z latami dem czekałby inaczej cały dzień. `python -m heat3d_watch replays <adapter> [folder]` konwertuje istniejące na żądanie.

#### War Thunder {#war-thunder}

War Thunder zapisuje powtórkę każdej bitwy do `<War Thunder>/Replays/*.wrpl`, gdy zapisywanie powtórek jest włączone w jego opcjach. Watcher sam ich nie czyta: robi to zewnętrzny konwerter (3DHeat War Thunder replay converter, `exporters/ext/warthunder-replay`, polecenie `heat3d-wt-replay`), trzymany osobno, żeby problem z nim nie dotykał reszty. Gdy polecenie jest w PATH albo pakiet jest zainstalowany lub leży obok watchera, każda nowa powtórka przechodzi przez niego do folderu sesji jako `<map>/<match>.parquet` i `<match>.match.json`; gdy nie jest, watcher raz podpowiada, jak go zainstalować, i zostawia folder w spokoju. Co konwerter czyta, a czego nie, jest w jego README. Linia wyników autora powtórki – zabójstwa, zabójstwa naziemne, zgony, asysty, wynik, przejęcia – staje się statystykami sesji.

Ten sam moduł obsługuje też: [Counter-Strike 2 (powtórki)](game-cs2-demos.md), [Dota 2 (powtórki)](game-dota-replays.md), [osu! (powtórki)](game-osu-replays.md), [Squad (powtórki)](game-squad-demos.md), [World of Tanks (powtórki)](game-wot-replays.md), [World of Warships (powtórki)](game-wows-replays.md).

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

`map`

Klucz w nawiasach klamrowych jest uzupełniany w czasie działania (`score.{team}` to jeden klucz na drużynę). Klucze, które kod bierze z tabeli pól gry albo z nazw statystyk gry, nie są na tej liście; „Co jest zapisywane” wyżej wymienia je.

## Kompletność {#completeness}

Konwerter uruchamiany przez ten adapter stosuje [regułę konwertera](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md) 3DHeat: to, co zawiera powtórka, jest odczytane albo zachowane, nigdy nie porzucone – odczytane do tabeli i dokumentu meczu, a wszystko inne zachowane w całości w plikach pobocznych obok nich, policzone w `selfCheck.completeness` dokumentu meczu. Dokumentacja samego konwertera wymienia, co odczytuje, co zachowuje w surowej postaci i czego nie potrafi odczytać.

## Sprawdzone {#verified}

konwerter jest sprawdzany na publicznych powtórkach z kilku wersji gry (zabójstwa i nazwy zgadzają się z wynikami) i testami na zbudowanych powtórkach; ten hak – testami z zastępczym poleceniem

## Źródło {#source}

[heat3d_watch/adapters/replays.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/replays.py)

<!-- Generated from the adapter by tools/gen_game_pages.py; change the adapter and run it again rather than editing this page. -->
