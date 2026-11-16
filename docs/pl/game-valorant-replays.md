---
title: "VALORANT (powtórki)"
nav_order: 45
lang: "pl"
source: game-valorant-replays.md
source_hash: "10a648aabdf1"
nav_exclude: true
search_exclude: true
---
# VALORANT (powtórki) {#valorant-replays}

Po meczu w VALORANT watcher zamienia powtórkę zapisaną przez grę na pliki, które możesz obejrzeć jako statystyki i oś czasu.

*Szczegóły techniczne: adapter `valorant-replays`, rodzaj [`replay`](sources-and-rules.md); działa cały czas (nie czeka na uruchomienie gry) i sprawdza nowe dane co 5 s.*

## Co jest zapisywane {#what-is-recorded}

- mapa, id meczu i wybrane agentki/agenci; blok informacji o powtórce (długość, wersje, nazwa, czas nagrania, flagi kompresji i szyfrowania)
- oś czasu zdarzeń serwera: zabójstwa (zabójca i ofiara jako id sieciowe), start rund, podłożone, rozbrojone i wybuchające spike'i, użyte ultymate, zmiana stron – każde z id i metadanymi
- każdy fragment pliku w całości w heat.raw.parquet; nieodczytane: pozycje, nazwy i wyniki – są w zaciemnionym strumieniu

## Skąd pochodzą dane {#where-it-comes-from}

powtórki zapisywane przez VALORANT: %LOCALAPPDATA%/VALORANT/Saved/Demos/\*.vrf (tylko części, które nie są zaciemnione)

## Jak to włączyć {#how-to-switch-it-on}

zapisz powtórkę w VALORANT (kariera > mecz > pobierz powtórkę)

## Jak to działa {#how-it-works}

League of Legends i powtórki VALORANT: to, co z nich można odczytać bez zmian.

Obie gry zapisują powtórki na dysku gracza i obie chronią to, co jest w środku: dane rozgrywki z chwili na chwilę są zaciemnione, i to inaczej przy każdej aktualizacji, by nie dało się ich użyć do oszustwa. Ta część nie jest nigdzie w 3DHeat dekodowana. Czytane jest to, co każdy plik zawiera jawnie, a reszta jest zachowana tak jak jest: każda część pliku w całości w `heat.raw.parquet` sesji (zasada konwertera 3DHeat, docs/converters.md w repozytorium przeglądarki), liczona w `selfCheck.completeness` w meta.json.

#### Valorant (.vrf) {#valorant-vrf}

`%LOCALAPPDATA%\VALORANT\Saved\Demos\*.vrf`, lokalna powtórka Unreal Engine (układ z vrfkit, Apache-2.0, i ValorantReplayParser, MIT). Jawnie: blok informacji o powtórce (długość, wersja sieciowa, changelist, nazwa, kiedy została nagrana, czy jest skompresowana lub zaszyfrowana), mapa, id meczu i wybrani agenci (w nagłówku) oraz własna oś czasu serwera – zabójstwa (zabójca i ofiara jako id sieciowe, nie nazwy), start rund, podłożone, rozbrojone i wybuchające spike'i, użyte ultymate, zmiana stron – każde z czasem, id i metadanymi. Pozycje, nazwy, wyniki i wszystko inne są w zaciemnionym strumieniu (fragmenty danych powtórki i punktów kontrolnych), który jest zachowywany w całości i nieczytany.

Ten sam moduł obsługuje też: [League of Legends (powtórki)](game-lol-replays.md).

## Pozycje i osie {#positions-and-axes}

| | |
|---|---|
| Zapisane pozycje | nie |
| Oś pionowa | `z` |
| Jednostki | jednostki świata VALORANT |
| Odbicie dla przeglądarki | brak |
| Skala jednostki (`scale`: przeglądarka mnoży przez nią pozycje) | 1 |

Te wartości trafiają do `meta.json` każdej sesji (`axes`) i, gdy sesja ma pozycje, do stopki `heat.parquet`. Dzięki temu przeglądarka 3DHeat sama obraca i skaluje wiersze – zob. [Dane](the-data.md).

## Tryb wieloosobowy {#multiplayer}

- Oznaczona jako gra sieciowa (`multiplayer`): **tak**. `games --markdown` pokazuje to jako „allowed (reads only what the game publishes)”.
- Rodzaj `replay`: czyta tylko to, co gra lub platforma udostępnia (powtórki i dema, które gra zapisuje), więc nagrywa także w grze sieciowej, tak jak w trybie offline. Flaga decyduje tylko o tym, czy pamięć w ogóle może być czytana.
- Pamięć: **nigdy** nie jest czytana przez ten adapter. Tylko adaptery `memory` czytają pamięć, i nigdy dla gry oznaczonej jako sieciowa – zob. [Źródła i zasady](sources-and-rules.md).

## Co jest zapisywane w statystykach {#statistics-recorded}

Klucze statystyk, które kod tego adaptera ustawia po nazwie (`stats` każdej sesji w `meta.json` i tabela `stats` w `watcher.sqlite`):

`kills_in_match`, `map`, `match_seconds`, `rounds`, `spikes_planted`

Klucz w nawiasach klamrowych jest uzupełniany podczas działania (`score.{team}` to jeden klucz na zespół). Klucze, które kod bierze z tabeli pól gry albo z nazw statystyk gry, nie są na tej liście; „Co jest zapisywane” wyżej wymienia je.

## Kompletność {#completeness}

Watcher stosuje [zasadę konwertera](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md) 3DHeat: to, co źródło zawiera, jest czytane albo zachowywane, nigdy pomijane. Oprócz wierszy każdy pakiet, strona, linia lub odpowiedź, którą adapter otrzyma, jest zachowana w całości w `heat.raw.parquet` sesji (kolumny `time`, `ms`, `type`, `used`, `payload`, `text`, a potem każde pole zachowane po nazwie; `used` oznacza to, co stało się też wierszami). `selfCheck.completeness` w `meta.json` liczy każdy `type`; `lost` wynosi 0.

**Odczytane**

- blok informacji, każde pole (meta.json `vrf`): wersja pliku, wersje niestandardowe, długość, wersja sieciowa, changelist, nazwa, flaga na żywo, czas nagrania, flagi kompresji i szyfrowania, klucz tak, jak jest zapisany
- fragment nagłówka: mapa, id meczu i wybrani agenci (rozpoznawani po swojej postaci)
- każdy fragment zdarzeń: id, grupa, metadane, czas startu i końca, a z jego danych nazwa zdarzenia, czas w sekundach i liczby przed nim (id sieciowe zabójcy i ofiary) – jeden wiersz na zdarzenie

**Zachowane w surowej postaci**

- każdy fragment w całości, w kolejności w pliku (`offset`), tak że części są plikiem: `info`, `header`, `event <group>`, `replay_data`, `checkpoint`, `chunk <n>` dla typu, którego układ nie nazywa, `trailing` dla bajtów za ostatnim pełnym fragmentem

**Niedostępne**

- pozycje, nazwy, wyniki, zdolności, każda klatka gry: fragmenty danych powtórki i punktów kontrolnych są zaciemnione. Zachowane w całości, nieodczytane
- zawartość zaszyfrowanej powtórki: przejrzana i zachowana w całości, nic w środku nie jest odczytywane

**Rozmiar**: surowy zapis towarzyszący ma w przybliżeniu rozmiar samej powtórki: zaciemniony strumień się nie kompresuje

## Sprawdzone {#verified}

zbudowane wg układu kontenera udokumentowanego przez vrfkit (Apache-2.0); niesprawdzone na prawdziwej powtórce, bo żadnej nie było – watcher sprawdza przed odczytem i pomija to, co nie pasuje

## Źródło {#source}

[heat3d_watch/adapters/riot_replays.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/riot_replays.py)

<!-- Generated from the adapter by tools/gen_game_pages.py; change the adapter and run it again rather than editing this page. -->
