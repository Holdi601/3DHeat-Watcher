---
title: "Rocket League (stan gry)"
nav_order: 40
lang: "pl"
source: game-rocketleague-stats.md
source_hash: "3da6ea772068"
nav_exclude: true
search_exclude: true
---
# Rocket League (stan gry) {#rocket-league-game-state}

Gdy grasz w Rocket League, watcher zapisuje to, co gra raportuje programom na Twoim komputerze, dzięki czemu później możesz to obejrzeć na mapie w przeglądarce 3DHeat.

*Szczegóły techniczne: adapter `rocketleague-stats`, rodzaj [`gsi`](sources-and-rules.md); działa, gdy uruchomiony jest `RocketLeague.exe`, i sprawdza nowe dane co 0,05 s.*

## Co jest zapisywane {#what-is-recorded}

- uderzenia piłki z jej miejscem (XYZ, jednostki Unreal), kto uderzył i prędkości
- gole z miejscem uderzenia, strzelec, asystujący i prędkość; trafienia w poprzeczkę z miejscem
- kanał statystyk (zburzenia, obrony, strzały, epickie obrony, ...), rozpoczęcia, powtórki, start i koniec meczu, zwycięzca
- samobóje, asysty, obrony, strzały, zburzenia, dotknięcia, wynik i wyniki drużyn z UpdateState
- ostatnia linia każdego gracza po zakończeniu meczu
- Twoje wiersze jako `me`: gracz wskazany w ustawieniach (`config --set player_names.rocketleague-stats=<nazwa>`), a w przeciwnym razie ten, za którym podąża kamera gry poza powtórkami
- brak pozycji aut: API ich nie ma

## Skąd pochodzą dane {#where-it-comes-from}

API statystyk: strumień JSON po TCP z 127.0.0.1:49123 (port w <RL>\TAGame\Config\TAStatsAPI.ini lub DefaultStatsAPI.ini)

## Jak to włączyć {#how-to-switch-it-on}

`python -m heat3d_watch setup rocketleague-stats --apply` (ustawia PacketSendRate=30), potem uruchom Rocket League

Wpisz polecenie w terminalu otwartym w folderze watchera (zob. [Zanim zaczniesz](before-you-start.md)). Jeśli się nie uda, ostatnia linia powie dlaczego; [Instalacja i uruchamianie](installing-and-running.md) opisuje częste przyczyny.

`python -m heat3d_watch setup rocketleague-stats` pokazuje pliki, które zostałyby zmienione; `python -m heat3d_watch setup rocketleague-stats --apply` zmienia je, zachowując oryginał jako `<file>.heat3d-backup` (zob. [Polecenia](commands.md#setup)). Dla każdej zmiany drukuje `rocketleague-stats: changed: ...`, a gdy opcja jest już włączona, `rocketleague-stats: nothing to change`.

## Jak to działa {#how-it-works}

Rocket League: oficjalne API statystyk, lokalne gniazdo, do którego gra wysyła dane meczu.

Włączane w `<RL>\TAGame\Config\TAStatsAPI.ini` – albo w `DefaultStatsAPI.ini`, gdy tamten plik nie istnieje, co gra czyta tylko wtedy – w sekcji `[TAGame.MatchStatsExporter_TA]`:

```text
PacketSendRate   UpdateState messages per second; 0 (the default) switches the API off, at most 120
Port             the TCP port the game listens on, default 49123 (WebPort 49124 is a WebSocket copy)
```

Gra jest serwerem: klient łączy się z 127.0.0.1:49123 i czyta strumień obiektów JSON `{"Event": nazwa, "Data": {...}}` (niektóre wersje wysyłają Data jako ciąg JSON), jeden po drugim, bez separatorów. Zdarzenia są wysyłane w chwili, w której się zdarzą, niezależnie od szybkości:

```text
UpdateState   MatchGuid, Players[] (Name, PrimaryId, Shortcut, TeamNum 0 blue / 1 orange,
              Score, Goals, Shots, Assists, Saves, Touches, CarTouches, Demos; car state
              only for spectators), Game (Teams[], TimeSeconds, bOvertime, Ball {Speed,
              TeamNum}, bReplay, bHasWinner, Winner, Arena, bHasTarget, Target)
BallHit       Players[] (Name, Shortcut, TeamNum), Ball {PreHitSpeed, PostHitSpeed, Location {X,Y,Z}}
GoalScored    GoalSpeed, GoalTime, ImpactLocation {X,Y,Z}, Scorer, Assister, BallLastTouch
CrossbarHit   BallLocation {X,Y,Z}, BallSpeed, ImpactForce, BallLastTouch
StatfeedEvent EventName, Type, MainTarget, SecondaryTarget
MatchEnded    WinnerTeamNum
MatchCreated, MatchInitialized, CountdownBegin, RoundStarted, GoalReplayStart/WillEnd/End,
MatchPaused/Unpaused, PodiumStart, ReplayCreated, MatchDestroyed, ClockUpdatedSeconds
```

Położenia są w jednostkach Unreal (centymetry), Z w górę; pole ma ok. 8200 x 10240, a bramki są przy Y = ±5120. Pozycje aut nie są częścią API: ma miejsce tylko piłka – tam, gdzie została uderzona, zdobyta lub trafiła w poprzeczkę.

Każdy komunikat jest też zachowany w całości (zasada konwertera 3DHeat, docs/converters.md w repozytorium przeglądarki): `heat.raw.parquet`, `type` to nazwa Event komunikatu, `text` to obiekt tak, jak przyszedł ze strumienia. UpdateState identyczny bajt w bajt z poprzednim (mecz wstrzymany, menu) jest zachowany raz i liczony w `unchanged_replies` w meta.json. Komunikaty między meczami czekają w zaległościach na sesję następnego meczu; to, co zostanie, gdy gra się zamknie, dostaje własną sesję. Znaki między obiektami, które nie są JSON-em, są zachowywane jako „junk”.

Źródła: <https://www.rocketleague.com/en/developer/stats-api> (oficjalna strona); wielkość liter w polach i ramkowanie TCP potwierdzone na kliencie rlstatsapi (<https://docs.rs/crate/rlstatsapi>, MIT; czytany tylko dla faktów).

## Pozycje i osie {#positions-and-axes}

| | |
|---|---|
| Zapisane pozycje | tak |
| Oś pionowa | `z` |
| Jednostki | jednostki Unreal (centymetry) |
| Odbicie dla przeglądarki | brak |
| Skala jednostki (`scale`: przeglądarka mnoży przez nią pozycje) | 1 |

Te wartości trafiają do `meta.json` każdej sesji (`axes`) i, gdy sesja ma pozycje, do stopki `heat.parquet`. Dzięki temu przeglądarka 3DHeat sama obraca i skaluje wiersze – zob. [Dane](the-data.md).

## Tryb wieloosobowy {#multiplayer}

- Oznaczona jako gra sieciowa (`multiplayer`): **tak**. `games --markdown` pokazuje to jako „allowed (reads only what the game publishes)”.
- Rodzaj `gsi`: czyta tylko to, co gra lub platforma udostępnia (integracja stanu gry albo lokalne API, które gra obsługuje), więc nagrywa także w grze sieciowej, tak jak w trybie offline. Flaga decyduje tylko o tym, czy pamięć w ogóle może być czytana.
- Pamięć: **nigdy** nie jest czytana przez ten adapter. Tylko adaptery `memory` czytają pamięć, i nigdy dla gry oznaczonej jako sieciowa – zob. [Źródła i zasady](sources-and-rules.md).

## Co jest zapisywane w statystykach {#statistics-recorded}

Klucze statystyk, które kod tego adaptera ustawia po nazwie (`stats` każdej sesji w `meta.json` i tabela `stats` w `watcher.sqlite`):

`bad_packets`, `demolished`, `other_goals`, `overtime`, `result`, `team_goals`

Klucz w nawiasach klamrowych jest uzupełniany podczas działania (`score.{team}` to jeden klucz na zespół). Klucze, które kod bierze z tabeli pól gry albo z nazw statystyk gry, nie są na tej liście; „Co jest zapisywane” wyżej wymienia je.

## Kompletność {#completeness}

Watcher stosuje [zasadę konwertera](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md) 3DHeat: to, co źródło zawiera, jest czytane albo zachowywane, nigdy pomijane. Oprócz wierszy każdy pakiet, strona, linia lub odpowiedź, którą adapter otrzyma, jest zachowana w całości w `heat.raw.parquet` sesji (kolumny `time`, `ms`, `type`, `used`, `payload`, `text`, a potem każde pole zachowane po nazwie; `used` oznacza to, co stało się też wierszami). `selfCheck.completeness` w `meta.json` liczy każdy `type`; `lost` wynosi 0.

**Odczytane**

- BallHit (miejsce, kto, drużyna, prędkości przed i po), GoalScored (miejsce uderzenia, strzelec, asystujący, prędkość, czas gola), CrossbarHit (miejsce, ostatni dotyk, prędkość, siła), StatfeedEvent (zdarzenie, typ, główny i drugorzędny cel), MatchEnded (zwycięzca, wynik); nazwa każdego innego zdarzenia jako wiersz
- z UpdateState: arena, cel kamery poza powtórkami (kim jest `me`), wyniki drużyn, bramki, asysty, obrony, strzały, zburzenia, dotknięcia i dotknięcia piłki oraz wynik każdego gracza (własne jako statystyki, wszystkich jako `player_result` na koniec meczu); dogrywka z ClockUpdatedSeconds

**Zachowane w surowej postaci**

- każdy komunikat w całości, tak jak przyszedł ze strumienia (`text`), pod swoją nazwą Event: `UpdateState` (PrimaryId i Shortcut każdego gracza, zegar, prędkość i drużyna piłki, nazwy i kolory drużyn, flagi powtórki i zwycięzcy oraz stan auta, jeśli gra go wysyła), `BallHit`, `GoalScored` (z ostatnim dotknięciem piłki), `CrossbarHit`, `StatfeedEvent`, `MatchCreated`, `MatchInitialized`, `CountdownBegin`, `RoundStarted`, `GoalReplayStart`, `GoalReplayWillEnd`, `GoalReplayEnd`, `MatchPaused`, `MatchUnpaused`, `MatchEnded`, `PodiumStart`, `ReplayCreated`, `MatchDestroyed`, `ClockUpdatedSeconds` i każde zdarzenie, które dodaje późniejsza wersja
- UpdateState identyczny bajt w bajt z poprzednim (wstrzymanie, menu) jest zachowany raz i liczony (`unchanged_replies` w meta.json)
- komunikaty między meczami: we własnym czasie, przed startem następnego meczu; po ostatnim meczu w sesji własnej (`raw_only` w meta.json)
- `unreadable`: obiekt, który nie jest komunikatem Stats API; `junk`: znaki między obiektami

**Niedostępne**

- pozycje aut i stan auta podczas gry: gra wysyła je tylko obserwatorom
- UpdateState między wysyłkami: gra wysyła PacketSendRate razy na sekundę (`setup` ustawia 30, gra pozwala do 120); zdarzenia są wysyłane w chwili, w której się zdarzą
- kopia WebSocket na WebPort (49124): te same komunikaty co na porcie TCP, nieczytane podwójnie

**Rozmiar**: UpdateState ma 1–3 KB dla sześciu graczy, 30 razy na sekundę: około 100–300 MB na godzinę w `raw.bin`, gdy mecz trwa, a w zstd `heat.raw.parquet` jedną dziesiątą lub mniej (szacowane z udokumentowanego formatu, nie zmierzone w grze)

## Sprawdzone {#verified}

testowane na komunikatach w udokumentowanym formacie, wysyłanych przez lokalny fałszywy serwer; niesprawdzone w grze

## Źródło {#source}

[heat3d_watch/adapters/rocketleague.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/rocketleague.py)

<!-- Generated from the adapter by tools/gen_game_pages.py; change the adapter and run it again rather than editing this page. -->
