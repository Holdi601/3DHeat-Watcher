---
title: "Counter-Strike 2 (powtórki)"
nav_order: 8
lang: "pl"
source: game-cs2-demos.md
source_hash: "d115f9085302"
nav_exclude: true
search_exclude: true
---
# Counter-Strike 2 (powtórki) {#counter-strike-2-replays}

Po meczu Counter-Strike 2 watcher zamienia powtórkę, którą zapisała gra, na pliki, które możesz obejrzeć na mapie w przeglądarce 3DHeat.

*Szczegóły techniczne: adapter `cs2-demos`, rodzaj [`replay`](sources-and-rules.md); działa cały czas (nie czeka na start gry) i szuka nowych danych co 5 s.*

## Co jest zapisywane {#what-is-recorded}

- pozycja, kierunek patrzenia, zdrowie i pieniądze każdego gracza (co ósmy takt)
- zabójstwa, zgony, obrażenia, granaty, zakładanie i rozbrajanie bomby – tam, gdzie się wydarzyły
- rundy, wynik, ekonomia; wiersz tablicy wyników zalogowanego gracza jako statystyki

## Skąd pochodzi {#where-it-comes-from}

dema, które zapisuje CS2: &lt;CS2>/game/csgo/replays/\*.dem (pobrane z historii meczów) i &lt;CS2>/game/csgo/\*.dem (nagrane)

## Jak to włączyć {#how-to-switch-it-on}

pobierz demo meczu w CS2 (Oglądaj > Twoje mecze) albo nagraj je poleceniem konsoli `record`

Ustawienia ze zmiennych środowiskowych:

- `HEAT3D_CS2`: folder 3DHeat CS2, gdy nie leży obok watchera i nie jest zainstalowany

## Jak to działa {#how-it-works}

Powtórki i dema: to, co gra zapisuje o meczu, zamieniane po jego zakończeniu.

Powtórka zawiera wszystko, co interfejs na żywo w grach wieloosobowych zatrzymuje dla siebie – pozycję każdego gracza, każde zabójstwo tam, gdzie się wydarzyło – i jest plikiem, który gra zapisuje dla swoich graczy, więc jej odczyt niczego w grze nie rusza. Watcher zagląda do folderów, w których gry je zapisują, czeka, aż nowy plik przestanie rosnąć (inaczej gra wciąż go zapisuje), i zamienia go w osobnym wątku, więc długa konwersja nigdy nie wstrzymuje reszty watchera.

Za pierwszym razem, gdy watcher widzi folder, powtórki, które już w nim są, tylko zapisuje na liście, nie konwertuje: gracz z latami dem czekałby inaczej cały dzień. `python -m heat3d_watch replays <adapter> [folder]` konwertuje istniejące na żądanie.

#### Counter-Strike 2 {#counter-strike-2}

CS2 zapisuje dema, które gracz pobierze z historii meczów (karta Oglądaj), do `<CS2>/game/csgo/replays/`, a nagrane poleceniem konsoli `record` do `<CS2>/game/csgo/`. Każde jest konwertowane konwerterem CS2 z tego repozytorium (3DHeat CS2, github.com/Holdi601/3DHeat-CS2: pozycja, kierunek patrzenia, zdrowie i pieniądze każdego gracza co ósmy takt; zabójstwa, zgony, obrażenia, granaty, zakładanie i rozbrajanie bomby tam, gdzie się wydarzyły; rundy, wynik, ekonomia) do folderu sesji jako tabela `<map>/<match>.parquet` i podsumowanie `<match>.match.json`, które czytają karty *Mapa cieplna* i *Mecz* w przeglądarce 3DHeat. Tablica wyników meczu staje się statystykami sesji: dla gracza, którego konto Steam jest zalogowane na tym komputerze (z `loginusers.vdf` Steama), pod zwykłymi nazwami – zabójstwa, zgony, asysty, ADR, KAST, procent headshotów, otwierające zabójstwa, clutche – oraz wynik i rundy.

Ten sam moduł obsługuje też: [Dota 2 (powtórki)](game-dota-replays.md), [osu! (powtórki)](game-osu-replays.md), [Squad (powtórki)](game-squad-demos.md), [War Thunder (powtórki)](game-warthunder-replays.md), [World of Tanks (powtórki)](game-wot-replays.md), [World of Warships (powtórki)](game-wows-replays.md).

## Pozycje i osie {#positions-and-axes}

| | |
|---|---|
| Zapisywane pozycje | tak |
| Oś w górę | `z` |
| Jednostki | cale (jednostki Source) |
| Odbicie dla przeglądarki | `y` |
| Skala jednostek (`scale`: przeglądarka mnoży przez nią pozycje) | 1 |

Trafiają one do `meta.json` każdej sesji (`axes`) i, gdy sesja ma pozycje, do stopki `heat.parquet`, więc przeglądarka 3DHeat sama obraca i skaluje wiersze – zob. [Dane](the-data.md).

## Gra wieloosobowa {#multiplayer}

- Oznaczona jako gra online (`multiplayer`): **tak**. `games --markdown` pokazuje to jako „dozwolone (czyta tylko to, co gra publikuje)”.
- Rodzaj `replay`: czyta tylko to, co gra lub platforma udostępnia (powtórki i dema, które gra zapisuje), więc zapisuje także w grze online, a nie tylko offline; flaga decyduje wyłącznie o tym, czy wolno kiedykolwiek czytać pamięć.
- Pamięć: **nigdy** nie jest czytana przez ten adapter. Tylko adaptery `memory` czytają pamięć i nigdy dla gry oznaczonej jako online – zob. [Źródła i zasady](sources-and-rules.md).

## Zapisywane statystyki {#statistics-recorded}

Klucze statystyk, które kod tego adaptera ustawia po nazwie (`stats` każdej sesji w `meta.json` i tabela `stats` w `watcher.sqlite`):

`map`, `rounds`, `score.{team}`, `won`

Klucz w nawiasach klamrowych jest uzupełniany w czasie działania (`score.{team}` to jeden klucz na drużynę). Klucze, które kod bierze z tabeli pól gry albo z nazw statystyk gry, nie są na tej liście; „Co jest zapisywane” wyżej wymienia je.

## Kompletność {#completeness}

Konwerter uruchamiany przez ten adapter stosuje [regułę konwertera](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md) 3DHeat: to, co zawiera powtórka, jest odczytane albo zachowane, nigdy nie porzucone – odczytane do tabeli i dokumentu meczu, a wszystko inne zachowane w całości w plikach pobocznych obok nich, policzone w `selfCheck.completeness` dokumentu meczu. Dokumentacja samego konwertera wymienia, co odczytuje, co zachowuje w surowej postaci i czego nie potrafi odczytać.

## Sprawdzone {#verified}

konwerter jest testowany na prawdziwych demach z turniejów; obserwowanie folderu i statystyki – testami

## Źródło {#source}

[heat3d_watch/adapters/replays.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/replays.py)

<!-- Generated from the adapter by tools/gen_game_pages.py; change the adapter and run it again rather than editing this page. -->
