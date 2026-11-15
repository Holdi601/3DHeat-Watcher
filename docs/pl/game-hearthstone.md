---
title: "Hearthstone (pliki dziennika)"
nav_order: 25
lang: "pl"
source: game-hearthstone.md
source_hash: "e79c19776947"
nav_exclude: true
search_exclude: true
---
# Hearthstone (pliki dziennika) {#hearthstone-log-files}

Gdy grasz w Hearthstone, watcher odczytuje pliki, które zapisuje gra, i zachowuje to, co się wydarzyło, dzięki czemu później możesz to obejrzeć jako statystyki i oś czasu.

*Szczegóły techniczne: adapter `hearthstone`, rodzaj [`log`](sources-and-rules.md); działa, gdy uruchomiony jest `Hearthstone.exe`, i sprawdza nowe dane co 0,5 s.*

## Co jest zapisywane {#what-is-recorded}

- start i koniec gry, z wynikiem (wygrana, przegrana, remis), turami i nazwą przeciwnika
- każda tura
- każda linia pliku Power.log i innych logów w całości w `heat.raw.parquet`
- gry, wygrane, przegrane, remisy, tury, najdłuższa gra

## Skąd pochodzą dane {#where-it-comes-from}

&lt;install>\Logs\Power.log (lub Logs\Hearthstone_\*\Power.log), zapisywany, gdy %LOCALAPPDATA%\Blizzard\Hearthstone\log.config ma sekcję [Power], oraz każdy inny \*.log, który gra zapisuje w tym miejscu

## Jak to włączyć {#how-to-switch-it-on}

`python -m heat3d_watch setup hearthstone --apply` dodaje logowanie [Power] do %LOCALAPPDATA%\Blizzard\Hearthstone\log.config (kopia zachowana); uruchom grę ponownie

Wpisz polecenie w terminalu otwartym w folderze watchera (zob. [Zanim zaczniesz](before-you-start.md)). Jeśli się nie uda, ostatnia linia podaje powód; [Instalacja i uruchamianie](installing-and-running.md) opisuje typowe przyczyny.

`python -m heat3d_watch setup hearthstone` pokazuje pliki, które by zmienił; `python -m heat3d_watch setup hearthstone --apply` zmienia je, zachowując oryginał jako `<file>.heat3d-backup` (zob. [Polecenia](commands.md#setup)). Dla każdej zmiany wypisuje `hearthstone: changed: ...`, a gdy już jest włączone – `hearthstone: nothing to change`.

## Jak to działa {#how-it-works}

Hearthstone: plik Power.log gry, który gra zapisuje, gdy log.config o to prosi.

Hearthstone odczytuje `%LOCALAPPDATA%\Blizzard\Hearthstone\log.config` przy starcie;
sekcja `[Power]` z `LogLevel=1` i `FilePrinting=true` powoduje, że gra zapisuje
zmiany stanu każdej gry do `<install>\Logs\Power.log` (nowsze klienty zapisują
logi każdego uruchomienia w osobnym folderze, `Logs\Hearthstone_<data>\`). To jest
udokumentowane logowanie debugowe, które trackery talii włączają od 2014 roku
(konfiguracja Hearthstone Deck Tracker zapisuje tę samą sekcję). `setup()` dodaje
sekcję, z kopią pliku w stanie, w jakim był; gra musi zostać uruchomiona ponownie, by ją odczytać.

Używane linie, wszystkie z `GameState.DebugPrintPower()` (linie `PowerTaskList`
powtarzają je i są pomijane):

```text
D 20:15:01.1234567 GameState.DebugPrintPower() - CREATE_GAME
D 20:15:01.1234567 GameState.DebugPrintPower() -     Player EntityID=2 PlayerID=1 GameAccountId=[hi=1 lo=2]
D 20:15:01.1234567 GameState.DebugPrintGame() - PlayerID=1, PlayerName=Name#1234
D 20:15:02.1234567 GameState.DebugPrintPower() -     FULL_ENTITY - Updating [entityName=... id=4 zone=HAND
                   zonePos=0 cardId=CS2_029 player=1] CardID=CS2_029
D 20:16:00.1234567 GameState.DebugPrintPower() - TAG_CHANGE Entity=GameEntity tag=TURN value=3
D 20:25:00.1234567 GameState.DebugPrintPower() - TAG_CHANGE Entity=Name#1234 tag=PLAYSTATE value=WON
D 20:25:00.1234567 GameState.DebugPrintPower() - TAG_CHANGE Entity=GameEntity tag=STATE value=COMPLETE
```

Stroną gracza jest ta, której początkowa ręka ma nazwane karty (karty przeciwnika
są ukryte), a w przeciwnym razie strona, która nie jest AI (konto 0) ani
„UNKNOWN HUMAN PLAYER”. Linie niosą tylko porę dnia; data to dzisiejsza.
Brak pozycji.

Każda linia Power.log jest zachowana w całości w surowym pliku pomocniczym sesji (zasada konwertera 3DHeat),
łącznie z powtórzeniami `PowerTaskList`, opcjami, wyborami i aktualizacjami encji: `type` to metoda, która ją zapisała
(`GameState.DebugPrintPower`, `PowerTaskList.DebugPrintPower`, `GameState.DebugPrintOptions`, ...). Każdy inny
log, który gra zapisuje obok – `LoadingScreen.log`, `Decks.log`, `Zone.log`,
`Arena.log`, ..., każdy z nich, gdy log.config o to prosi (trackery talii
często tak robią) – jest śledzony tak samo i zachowany z nazwą w `log`.

## Pozycje i osie {#positions-and-axes}

| | |
|---|---|
| Zapisane pozycje | nie |
| Oś pionowa | `y` |
| Jednostki | brak zapisanych pozycji |
| Odbicie dla przeglądarki | brak |
| Skala jednostki (`scale`: przeglądarka mnoży przez nią pozycje) | 1 |

Te wartości trafiają do `meta.json` każdej sesji (`axes`) i, gdy sesja ma pozycje, do stopki `heat.parquet`. Dzięki temu przeglądarka 3DHeat sama obraca i skaluje wiersze – zob. [Dane](the-data.md).

## Tryb wieloosobowy {#multiplayer}

- Oznaczone jako grane online (`multiplayer`): **tak**. `games --markdown` pokazuje to jako „dozwolone (odczytuje tylko to, co gra publikuje)”.
- Rodzaj `log`: odczytuje tylko to, co gra lub platforma udostępnia (pliki, które gra zapisuje podczas działania), więc nagrywa też w grze online; flaga decyduje tylko o tym, czy wolno kiedykolwiek czytać pamięć.
- Pamięć: **nigdy** nie jest odczytywana przez ten adapter. Tylko adaptery `memory` czytają pamięć, i nigdy dla gry oznaczonej jako grana online – zob. [Źródła i zasady](sources-and-rules.md).

## Co jest zapisywane w statystykach {#statistics-recorded}

Klucze statystyk, które kod tego adaptera ustawia po nazwie (`stats` każdej sesji w `meta.json` i tabela `stats` w `watcher.sqlite`):

`bad_lines`, `games`, `longest_game_turns`, `losses`, `ties`, `turns`, `wins`

Klucz w nawiasach klamrowych jest uzupełniany w czasie działania (`score.{team}` to jeden klucz na zespół). Klucze, które kod bierze z tabeli pól gry lub z jej własnych nazw statystyk, nie są na tej liście; sekcja „Co jest zapisywane” wyżej wymienia je.

## Kompletność {#completeness}

Watcher stosuje [zasadę konwertera 3DHeat](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md): to, co źródło zawiera, jest odczytywane lub zachowywane, nigdy nie jest pomijane. Oprócz wierszy każdy pakiet, strona, linia lub odpowiedź, którą adapter otrzyma, jest zachowana w całości w `heat.raw.parquet` sesji (kolumny `time`, `ms`, `type`, `used`, `payload`, `text`, a potem każde pole zachowane po nazwie; `used` oznacza to, co stało się też wierszami), a `selfCheck.completeness` w `meta.json` liczy każdy `type` – `lost` wynosi 0.

**Odczytane**

- `CREATE_GAME`, gracze (encja, id gracza, konto; konto 0 to AI) i ich nazwy (`DebugPrintGame`)
- czyja strona jest graczem, z nazwanych kart początkowej ręki
- `TAG_CHANGE` dla TURN, PLAYSTATE (won, lost, tied) i STATE COMPLETE: tury, wynik, przeciwnik

**Zachowane w surowej postaci**

- każda linia Power.log w całości, `type` = metoda, która ją zapisała (`GameState.DebugPrintPower`, `PowerTaskList.DebugPrintPower`, `GameState.DebugPrintGame`, `GameState.DebugPrintOptions`, `GameState.SendChoices`, `GameState.DebugPrintEntityChoices`, `PowerProcessor.DoTaskListForCard`, ...), `log` `Power`, `used` tam, gdzie stała się wierszem: każda zagrana, dobrana i odkryta karta, każda zmiana tagu, atak, opcja i wybór są tutaj, jeszcze nie jako wiersze
- każda linia innych logów w tym samym folderze (`LoadingScreen`, `Decks`, `Zone`, `Arena`, `Achievements`, `FullScreenFX`, ... – cokolwiek log.config włącza), te same `type`, z nazwą logu w `log`
- linia bez poziomu i pory dnia jako `untimed`, linia bez metody jako `untagged`

**Niedostępne**

- pozycje: gra karciana ich nie ma
- ukryte karty przeciwnika: log nazywa kartę dopiero po jej odkryciu
- logi, których log.config nie włącza: `setup` pyta tylko o [Power]; pozostałe logi pojawiają się, gdy inne narzędzie (tracker talii) je włączy
- logi wcześniejszych uruchomień: każde uruchomienie zapisuje nowy folder; te starsze niż ten przebieg gry nie są czytane ponownie

**Rozmiar**: Power.log z opcją Verbose to około 1-5 MB na grę, 10-40 MB na godzinę gry; pozostałe logi dodają niewiele; zstd w `heat.raw.parquet` zmniejsza to do dziesiątej części lub mniej (linie często się powtarzają)

## Sprawdzone {#verified}

przetestowane na syntetycznych liniach Power.log w formacie gry; nie przetestowane w grze

## Źródło {#source}

[heat3d_watch/adapters/hearthstone.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/hearthstone.py)

<!-- Generated from the adapter by tools/gen_game_pages.py; change the adapter and run it again rather than editing this page. -->
