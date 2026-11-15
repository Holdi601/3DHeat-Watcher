---
title: "League of Legends (powtórki)"
nav_order: 30
lang: "pl"
source: game-lol-replays.md
source_hash: "216b88922360"
nav_exclude: true
search_exclude: true
---
# League of Legends (powtórki) {#league-of-legends-replays}

Po meczu w League of Legends watcher zamienia powtórkę zapisaną przez klienta gry na pliki, które możesz obejrzeć na mapie w przeglądarce 3DHeat.

*Szczegóły techniczne: adapter `lol-replays`, rodzaj [`replay`](sources-and-rules.md); działa cały czas (nie czeka na uruchomienie gry) i sprawdza nowe dane co 5 s.*

## Co jest zapisywane {#what-is-recorded}

- postać każdego gracza, rola, drużyna, zabójstwa, śmierci, asysty, złoto, obrażenia zadane postaciom i wynik, oraz każda inna liczba z tabeli wyników po zakończeniu gry
- Twoja linia jako statystyki, a Twoje wiersze oznaczone jako Twoje (meta.json `player`), z Twoim Riot ID w ustawieniach
- z własnym kluczem Riot API: pozycja każdego gracza co minutę wraz ze statystykami z tej minuty oraz każde zdarzenie z osi czasu (zabójstwa w miejscu, w którym się stały, budynki, potwory, pułapki, przedmioty, umiejętności), o czasie zegarowym podanym przez oś czasu
- każda część pliku powtórki zachowana w całości w heat.raw.parquet; nieodczytane: rozgrywka z chwili na chwilę, która jest zaszyfrowana i zaciemniona przeciw oszustwom

## Skąd pochodzą dane {#where-it-comes-from}

powtórki zapisywane przez klienta League: %USERPROFILE%/Documents/League of Legends/Replays/\*.rofl (tylko jawne metadane z końca gry); z własnym kluczem Riot API oficjalna oś czasu meczu z Match-V5 API Riot

## Jak to włączyć {#how-to-switch-it-on}

zapisz powtórkę w kliencie League (historia meczów > pobierz); dla pozycji ustaw riot_api_key i riot_platform poleceniem `config --set`

## Jak to działa {#how-it-works}

League of Legends i powtórki VALORANT: to, co z nich można odczytać bez zmian.

Obie gry zapisują powtórki na dysku gracza i obie chronią to, co jest w środku: dane rozgrywki z chwili na chwilę są zaciemnione, i to inaczej przy każdej aktualizacji, by nie dało się ich użyć do oszustwa. Przejście przez to oznacza rozbieranie na części kodu gry, czego zabraniają warunki Riot (Warunki usługi 3.1 i 7.1) – więc tego tu nie robimy. Czytane jest to, co każdy plik zawiera jawnie, a reszta jest zachowana tak jak jest: każda część pliku w całości w `heat.raw.parquet` sesji (zasada konwertera 3DHeat, docs/converters.md w repozytorium przeglądarki), liczona w `selfCheck.completeness` w meta.json.

#### League of Legends (.rofl) {#league-of-legends-rofl}

`%USERPROFILE%\Documents\League of Legends\Replays\*.rofl`. Obie wersje kontenera niosą tabelę wyników po zakończeniu gry jako zwykły JSON (`statsJson`): dla każdego z dziesięciu graczy postać, zabójstwa, śmierci, asysty, złoto, obrażenia zadane postaciom, przedmioty, drużynę, rolę, wygraną, ich Riot ID i każdą inną liczbę, jaką gra sumuje (ponad sto na gracza); wszystkie trafiają do wiersza `player_result` gracza. ROFL1 (łatka 14.9 i wcześniejsze) ma ją po stałym nagłówku (`RIOT\0\0`, 256-bajtowy podpis, potem długości); ROFL2 (od 14.11, `RIOT\2\0`) na końcu pliku, jego długość w ostatnich czterech bajtach (podane przez inżyniera Riot, ReplayBook issue 299). Nagłówek ładunku ROFL1 (id gry, długość, liczba fragmentów i klatek kluczy, długość klucza fragmentu) oraz tabela fragmentów (id, typ, długość, następny fragment, przesunięcie) są jawne i odczytywane; same fragmenty są zaszyfrowane i zachowane w całości, nieodczytane. Układy z roflxd.cs (MIT).

Pozycje nie pochodzą z pliku. Z własnym kluczem dewelopera Riot gracza (`riot_api_key` w ustawieniach; klucz osobisty jest przeznaczony dokładnie do „pokazywania (własnych) statystyk gracza”) oficjalna oś czasu meczu jest pobierana z Match-V5 API Riot: pozycja każdego gracza raz na minutę wraz z wszystkim, co klatka tej minuty mówi o nim (złoto, doświadczenie, poziom, stwory, statystyki postaci i obrażeń), oraz każde zdarzenie osi czasu – zabójstwa, budynki, elitarne potwory, pułapki, przedmioty, umiejętności, poziomy – jako wiersz, tam gdzie miało miejsce, jeśli ma miejsce. Bez klucza nic nie jest pobierane i nic nie jest wysyłane.

Ten sam moduł obsługuje też: [VALORANT (powtórki)](game-valorant-replays.md).

## Pozycje i osie {#positions-and-axes}

| | |
|---|---|
| Zapisane pozycje | tak |
| Oś pionowa | `y` |
| Jednostki | jednostki mapy Summoner's Rift (ok. 15000 w poprzek) |
| Odbicie dla przeglądarki | brak |
| Skala jednostki (`scale`: przeglądarka mnoży przez nią pozycje) | 1 |

Te wartości trafiają do `meta.json` każdej sesji (`axes`) i, gdy sesja ma pozycje, do stopki `heat.parquet`. Dzięki temu przeglądarka 3DHeat sama obraca i skaluje wiersze – zob. [Dane](the-data.md).

## Tryb wieloosobowy {#multiplayer}

- Oznaczona jako gra sieciowa (`multiplayer`): **tak**. `games --markdown` pokazuje to jako „allowed (reads only what the game publishes)”.
- Rodzaj `replay`: czyta tylko to, co gra lub platforma udostępnia (powtórki i dema, które gra zapisuje), więc nagrywa także w grze sieciowej, tak jak w trybie offline. Flaga decyduje tylko o tym, czy pamięć w ogóle może być czytana.
- Pamięć: **nigdy** nie jest czytana przez ten adapter. Tylko adaptery `memory` czytają pamięć, i nigdy dla gry oznaczonej jako sieciowa – zob. [Źródła i zasady](sources-and-rules.md).

## Co jest zapisywane w statystykach {#statistics-recorded}

Klucze statystyk, które kod tego adaptera ustawia po nazwie (`stats` każdej sesji w `meta.json` i tabela `stats` w `watcher.sqlite`):

`champion`, `game_seconds`, `won`

Klucz w nawiasach klamrowych jest uzupełniany podczas działania (`score.{team}` to jeden klucz na zespół). Klucze, które kod bierze z tabeli pól gry albo z nazw statystyk gry, nie są na tej liście; „Co jest zapisywane” wyżej wymienia je.

## Kompletność {#completeness}

Watcher stosuje [zasadę konwertera](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md) 3DHeat: to, co źródło zawiera, jest czytane albo zachowywane, nigdy pomijane. Oprócz wierszy każdy pakiet, strona, linia lub odpowiedź, którą adapter otrzyma, jest zachowana w całości w `heat.raw.parquet` sesji (kolumny `time`, `ms`, `type`, `used`, `payload`, `text`, a potem każde pole zachowane po nazwie; `used` oznacza to, co stało się też wierszami). `selfCheck.completeness` w `meta.json` liczy każdy `type`; `lost` wynosi 0.

**Odczytane**

- metadane JSON: długość gry, wersja, id ostatniego fragmentu i klatki kluczy oraz `statsJson` – każde pole tabeli wyników każdego gracza w wierszu `player_result` (liczby podane jako tekst są czytane jako liczby)
- ROFL1: blok długości, nagłówek ładunku (id gry, długość gry, liczba klatek kluczy i fragmentów, id fragmentów startowych i początku gry, interwał klatek kluczy, klucz fragmentu tak, jak jest zapisany) i tabela fragmentów (id, typ, długość, następny fragment, przesunięcie) – w meta.json `rofl` i w `text` surowych wierszy
- ROFL2: ciąg wersji
- oś czasu Match-V5 (tylko z własnym kluczem API): każda klatka uczestnika w wierszu `position` (albo `participant_frame`, bez miejsca) z wszystkimi polami spłaszczonymi (`championStats.armor`, `damageStats.totalDamageDone`, `currentGold`, `xp`, ...); każde zdarzenie jako wiersz nazwany od swojego typu, umieszczony tam, gdzie ma `position`; CHAMPION_KILL jako zabójstwo i śmierć

**Zachowane w surowej postaci**

- każda część .rofl w całości, w kolejności w pliku (`offset`), tak że części są plikiem: `magic`, `signature`, `lengths`, `metadata`, `payload_header`, `chunk_header`, `chunk`, `keyframe` (ROFL1); `body`, `metadata`, `metadata_length` (ROFL2); każdy fragment, którego żadna część nie obejmuje, jako `unknown`
- oś czasu w całości: `timeline <type>` dla każdego zdarzenia, `timeline participantFrame` dla klatki każdego gracza (`participant` to jego id), `timeline` dla reszty

**Niedostępne**

- sama gra (pozycje, zdolności, każda jednostka, z chwili na chwilę): fragmenty ROFL1 i ciało ROFL2 są zaszyfrowane, a pakiety w środku zaciemnione przy każdej łatce; przejście przez to oznacza rozbieranie klienta na części, czego zabraniają warunki Riot (3.1, 7.1). Zachowane w całości, nieodczytane
- pozycje bez własnego klucza Riot API: plik nie ma ich jawnie

**Rozmiar**: surowy zapis towarzyszący ma w przybliżeniu rozmiar samej powtórki: zaszyfrowane fragmenty się nie kompresują

## Sprawdzone {#verified}

czytnik metadanych testowany na plikach zbudowanych wg układów z roflxd.cs (MIT); oś czasu – na udokumentowanym przez Match-V5 JSON; nie było prawdziwej powtórki do sprawdzenia

## Źródło {#source}

[heat3d_watch/adapters/riot_replays.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/riot_replays.py)

<!-- Generated from the adapter by tools/gen_game_pages.py; change the adapter and run it again rather than editing this page. -->
