---
title: "osu! (powtórki)"
nav_order: 35
lang: "pl"
source: game-osu-replays.md
source_hash: "9a1c74c4d5e0"
nav_exclude: true
search_exclude: true
---
# osu! (powtórki) {#osu-replays}

Po meczu osu! watcher zamienia powtórkę zapisaną przez grę na pliki, które możesz obejrzeć na mapie w przeglądarce 3DHeat.

*Szczegóły techniczne: adapter `osu-replays`, rodzaj [`replay`](sources-and-rules.md); działa cały czas (nie czeka, aż uruchomi się gra) i sprawdza nowe dane co 5 s.*

## Co jest zapisywane {#what-is-recorded}

- ścieżka kursora po polu gry (x 0..512, y 0..384) i wciśnięte klawisze, w każdej klatce
- wynik, combo, 300/100/50, gekidy, katu, pudła, celność, modyfikatory, full combo
- pasek życia podczas gry, skróty MD5 mapy i powtórki, ziarno losowości, id wyniku online

## Skąd pochodzą dane {#where-it-comes-from}

powtórki zapisywane przez osu! (wersja stable): %LOCALAPPDATA%/osu!/Data/r/\*.osr (każda gra) oraz osu!/Replays/\*.osr (wyeksportowane)

## Jak to włączyć {#how-to-switch-it-on}

Nic nie trzeba włączać: watcher odczytuje źródło tak, jak udostępnia je gra lub platforma.

## Jak to działa {#how-it-works}

Powtórki i dema: to, co gra zapisuje z meczu, zamieniane raz, gdy mecz się skończy.

Powtórka zawiera wszystko, co w grach wieloosobowych interfejs na żywo zatrzymuje dla siebie –
pozycję każdego gracza, każde zabójstwo w miejscu, w którym się zdarzyło – i jest plikiem, który gra zapisuje
dla swoich graczy, więc jej odczyt nie dotyka gry. Watcher zagląda do folderów, w których gry je zapisują,
czeka, aż nowy plik przestanie rosnąć (inaczej gra wciąż go zapisuje), i konwertuje go w wątku roboczym,
więc długa konwersja nie wstrzymuje reszty watchera.

Za pierwszym razem, gdy zobaczy folder, powtórki już w nim leżące są tylko odnotowywane, a nie konwertowane:
gracz z latami dem zostałby inaczej z watcherem zajętym przez dobę. `python -m heat3d_watch replays <adapter> [folder]` konwertuje istniejące na żądanie.

#### osu! {#osu}

osu! (wersja stable) zapisuje każdą grę do `osu!/Data/r/*.osr`, a wyeksportowane do
`osu!/Replays/`. Watcher czyta je sam, zgodnie z formatem opublikowanym w wiki osu!: ścieżka kursora i klawisze w każdej klatce, linia wyniku, pasek życia, ziarno i id wyniku; plik jest zachowywany w całości obok, część po części, w
surowym pliku pomocniczym sesji `heat.raw.parquet`.

Ten sam moduł obsługuje też: [Counter-Strike 2 (powtórki)](game-cs2-demos.md), [Dota 2 (powtórki)](game-dota-replays.md), [Squad (powtórki)](game-squad-demos.md), [War Thunder (powtórki)](game-warthunder-replays.md), [World of Tanks (powtórki)](game-wot-replays.md), [World of Warships (powtórki)](game-wows-replays.md).

## Pozycje i osie {#positions-and-axes}

| | |
|---|---|
| Zapisane pozycje | tak |
| Oś pionowa | `y` |
| Jednostki | piksele osu! (pole gry 512 x 384) |
| Odbicie dla przeglądarki | `z` |
| Skala jednostki (`scale`: przeglądarka mnoży przez nią pozycje) | 1 |

Te wartości trafiają do `meta.json` każdej sesji (`axes`) i, gdy sesja ma pozycje, do stopki `heat.parquet`. Dzięki temu przeglądarka 3DHeat sama obraca i skaluje wiersze – zob. [Dane](the-data.md).

## Tryb wieloosobowy {#multiplayer}

- Oznaczone jako grane online (`multiplayer`): **tak**. `games --markdown` pokazuje to jako „dozwolone (odczytuje tylko to, co gra publikuje)”.
- Rodzaj `replay`: odczytuje tylko to, co gra lub platforma udostępnia (powtórki i dema, które gra zapisuje), więc nagrywa też w grze online; flaga decyduje tylko o tym, czy wolno kiedykolwiek czytać pamięć.
- Pamięć: **nigdy** nie jest odczytywana przez ten adapter. Tylko adaptery `memory` czytają pamięć, i nigdy dla gry oznaczonej jako grana online – zob. [Źródła i zasady](sources-and-rules.md).

## Co jest zapisywane w statystykach {#statistics-recorded}

Klucze statystyk, które kod tego adaptera ustawia po nazwie (`stats` każdej sesji w `meta.json` i tabela `stats` w `watcher.sqlite`):

`accuracy`, `full_combo`

Klucz w nawiasach klamrowych jest uzupełniany w czasie działania (`score.{team}` to jeden klucz na zespół). Klucze, które kod bierze z tabeli pól gry lub z jej własnych nazw statystyk, nie są na tej liście; sekcja „Co jest zapisywane” wyżej wymienia je.

## Kompletność {#completeness}

Watcher stosuje [zasadę konwertera 3DHeat](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md): to, co źródło zawiera, jest odczytywane lub zachowywane, nigdy nie jest pomijane. Oprócz wierszy każdy pakiet, strona, linia lub odpowiedź, którą adapter otrzyma, jest zachowana w całości w `heat.raw.parquet` sesji (kolumny `time`, `ms`, `type`, `used`, `payload`, `text`, a potem każde pole zachowane po nazwie; `used` oznacza to, co stało się też wierszami), a `selfCheck.completeness` w `meta.json` liczy każdy `type` – `lost` wynosi 0.

**Odczytane**

- każda klatka: wiersz w swoim czasie (milisekundy zsumowane), x i y na polu gry, `keys` – bity klawiszy (mysz 1 i 2, klawisze 1 i 2, dym); w mania x zawiera wciśnięte klawisze zamiast miejsca
- nagłówek, każde pole: tryb, wersja, MD5 mapy (plik nazywa mapę tylko tym skrótem), gracz, MD5 powtórki, 300, 100, 50, gekidy, katu, pudła, wynik, maksymalne combo, full combo, modyfikatory (po nazwie w `osu.modNames` w meta.json), czas gry – jako statystyki i w meta.json `osu`
- wykres paska życia: wiersz `life` na każdy punkt (czas, życie 0..1)
- klatka `-12345`: ziarno losowości (`osu.seed`); id wyniku online (`osu.scoreId`); przy Target Practice jego celność (`osu.targetPracticeAccuracy`)

**Zachowane w surowej postaci**

- plik w całości, część po części, w heat.raw.parquet (`offset`, gdzie każda się zaczyna, więc części tworzą plik): `header`, `replay_data` (klatki skompresowane LZMA tak, jak są zapisane), `score_id`, `mod_info`, a `trailing` to wszystko, co następuje po częściach opisanych przez format (eksporty osu!lazer dopisują tam dane) – zachowane, nieodczytane

**Niedostępne**

- sama mapa (obiekty trafień, czasy): nie ma jej w powtórce; jest tylko wskazana skrótem MD5
- powtórki osu!lazer: zapisane w jego bazie danych, a nie jako pliki

**Rozmiar**: surowy plik pomocniczy ma mniej więcej rozmiar powtórki (dziesiątki do setek kilobajtów)

## Sprawdzone {#verified}

przetestowane na powtórkach zbudowanych zgodnie z opublikowanym formatem .osr; osu!lazer przechowuje powtórki we własnym magazynie i nie jest czytany

## Źródło {#source}

[heat3d_watch/adapters/replays.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/replays.py)

<!-- Generated from the adapter by tools/gen_game_pages.py; change the adapter and run it again rather than editing this page. -->
