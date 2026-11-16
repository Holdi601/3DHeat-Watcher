---
title: "Squad (powtórki)"
nav_order: 41
lang: "pl"
source: game-squad-demos.md
source_hash: "82c24e6df01c"
nav_exclude: true
search_exclude: true
---
# Squad (powtórki) {#squad-replays}

Po meczu Squad watcher zamienia powtórkę, którą zapisała gra, na pliki, które możesz obejrzeć na mapie w przeglądarce 3DHeat.

*Szczegóły techniczne: adapter `squad-demos`, rodzaj [`replay`](sources-and-rules.md); działa cały czas (nie czeka na start gry) i szuka nowych danych co 5 s.*

## Co jest zapisywane {#what-is-recorded}

- pozycja, kąt obrotu korpusu i prędkość każdego gracza za każdym razem, gdy serwer je replikuje (do 8 razy na sekundę), na piechotę i w pojazdach lądowych
- imię, drużyna, frakcja i oddział każdego gracza, z uwzględnieniem zmian drużyny
- nie: ruchu helikopterów, zabójstw i rozstawianych urządzeń – zob. README czytnika

## Skąd pochodzi {#where-it-comes-from}

dema serwerowe, które Squad nagrywa poleceniem administratora AdminDemoRec: &lt;server>/SquadGame/Saved/Demos/\*.replay, czytane przez zewnętrzny czytnik `heat3d-squad-demo` (exporters/ext/squad-demo)

## Jak to włączyć {#how-to-switch-it-on}

nagrywaj na serwerze: daj administratorowi uprawnienie `demos` w Admins.cfg, a potem w konsoli gry wpisz AdminDemoRec &lt;nazwa> i AdminDemoStop; skopiuj demo tutaj i zainstaluj czytnik: pip install -e &lt;3DHeat>/exporters/ext/squad-demo

Ustawienia ze zmiennych środowiskowych:

- `HEAT3D_SQUAD_DEMO`: folder konwertera (klon albo rozpakowane wydanie), gdy nie jest zainstalowany ani nie leży obok watchera

## Jak to działa {#how-it-works}

Powtórki i dema: to, co gra zapisuje o meczu, zamieniane po jego zakończeniu.

Powtórka zawiera wszystko, co interfejs na żywo w grach wieloosobowych zatrzymuje dla siebie – pozycję każdego gracza, każde zabójstwo tam, gdzie się wydarzyło – i jest plikiem, który gra zapisuje dla swoich graczy, więc jej odczyt niczego w grze nie rusza. Watcher zagląda do folderów, w których gry je zapisują, czeka, aż nowy plik przestanie rosnąć (inaczej gra wciąż go zapisuje), i zamienia go w osobnym wątku, więc długa konwersja nigdy nie wstrzymuje reszty watchera.

Za pierwszym razem, gdy watcher widzi folder, powtórki, które już w nim są, tylko zapisuje na liście, nie konwertuje: gracz z latami dem czekałby inaczej cały dzień. `python -m heat3d_watch replays <adapter> [folder]` konwertuje istniejące na żądanie.

#### Squad {#squad}

Dedykowane serwery Squad nagrywają dema meczu, gdy administrator z uprawnieniem `demos` wpisze AdminDemoRec &lt;nazwa> (a potem AdminDemoStop), do `<server>/SquadGame/Saved/Demos/<nazwa>.replay`. To powtórka sieciowa Unreal Engine, zawierająca to, co serwer replikował, w tym cały ruch graczy. Watcher sam jej nie czyta: robi to zewnętrzny czytnik (3DHeat Squad demo reader, `exporters/ext/squad-demo`, polecenie `heat3d-squad-demo`), osobny projekt. Uruchamiany jest dla każdego nowego dema w folderach, do których zapisuje lokalny serwer, albo w folderze dodanym w ustawieniach dla dem skopiowanych z wynajętego serwera, i zapisuje wynik do folderu sesji jako `<map>/<match>.parquet` i `<match>.match.json`. Tryb gry, mapa, liczba graczy i długość meczu stają się statystykami sesji.

Ten sam moduł obsługuje też: [Counter-Strike 2 (powtórki)](game-cs2-demos.md), [Dota 2 (powtórki)](game-dota-replays.md), [osu! (powtórki)](game-osu-replays.md), [War Thunder (powtórki)](game-warthunder-replays.md), [World of Tanks (powtórki)](game-wot-replays.md), [World of Warships (powtórki)](game-wows-replays.md).

## Pozycje i osie {#positions-and-axes}

| | |
|---|---|
| Zapisywane pozycje | tak |
| Oś w górę | `z` |
| Jednostki | jednostki Unreal (centymetry) |
| Odbicie dla przeglądarki | brak |
| Skala jednostek (`scale`: przeglądarka mnoży przez nią pozycje) | 1 |

Trafiają one do `meta.json` każdej sesji (`axes`) i, gdy sesja ma pozycje, do stopki `heat.parquet`, więc przeglądarka 3DHeat sama obraca i skaluje wiersze – zob. [Dane](the-data.md).

## Gra wieloosobowa {#multiplayer}

- Oznaczona jako gra online (`multiplayer`): **tak**. `games --markdown` pokazuje to jako „dozwolone (czyta tylko to, co gra publikuje)”.
- Rodzaj `replay`: czyta tylko to, co gra lub platforma udostępnia (powtórki i dema, które gra zapisuje), więc zapisuje także w grze online, a nie tylko offline; flaga decyduje wyłącznie o tym, czy wolno kiedykolwiek czytać pamięć.
- Pamięć: **nigdy** nie jest czytana przez ten adapter. Tylko adaptery `memory` czytają pamięć i nigdy dla gry oznaczonej jako online – zob. [Źródła i zasady](sources-and-rules.md).

## Zapisywane statystyki {#statistics-recorded}

Klucze statystyk, które kod tego adaptera ustawia po nazwie (`stats` każdej sesji w `meta.json` i tabela `stats` w `watcher.sqlite`):

`layer`, `map`, `match_seconds`, `players`

Klucz w nawiasach klamrowych jest uzupełniany w czasie działania (`score.{team}` to jeden klucz na drużynę). Klucze, które kod bierze z tabeli pól gry albo z nazw statystyk gry, nie są na tej liście; „Co jest zapisywane” wyżej wymienia je.

## Kompletność {#completeness}

Konwerter uruchamiany przez ten adapter stosuje [regułę konwertera](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md) 3DHeat: to, co zawiera powtórka, jest odczytane albo zachowane, nigdy nie porzucone – odczytane do tabeli i dokumentu meczu, a wszystko inne zachowane w całości w plikach pobocznych obok nich, policzone w `selfCheck.completeness` dokumentu meczu. Dokumentacja samego konwertera wymienia, co odczytuje, co zachowuje w surowej postaci i czego nie potrafi odczytać.

## Sprawdzone {#verified}

czytnik jest sprawdzany na publicznych demach serwerów (ruch zgadza się z prędkością, którą niesie; drużyna każdego wiersza zgadza się z frakcją jego żołnierza) i testami na zbudowanych demach; ten hak – testami z zastępczym poleceniem

## Źródło {#source}

[heat3d_watch/adapters/replays.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/replays.py)

<!-- Generated from the adapter by tools/gen_game_pages.py; change the adapter and run it again rather than editing this page. -->
