---
title: "Counter-Strike 2 (stan gry)"
nav_order: 9
lang: "pl"
source: game-cs2-gsi.md
source_hash: "2eda1106e11f"
nav_exclude: true
search_exclude: true
---
# Counter-Strike 2 (stan gry) {#counter-strike-2-game-state}

Podczas gry w Counter-Strike 2 watcher zapisuje to, co gra przekazuje programom na twoim komputerze, dzięki czemu możesz później obejrzeć to na mapie w przeglądarce 3DHeat.

*Szczegóły techniczne: adapter `cs2-gsi`, rodzaj [`gsi`](sources-and-rules.md); działa, gdy działa `cs2.exe`, i sprawdza nowe dane co 0,05 s.*

## Co jest zapisywane {#what-is-recorded}

- własna pozycja (współrzędne XYZ świata, w calach) i kierunek patrzenia, do 10 razy na sekundę, gdy żyjesz
- pojawienia się (pierwsze zauważenie w każdej rundzie, odrodzenia) i śmierci (zdrowie spadło do 0 albo wzrosła liczba śmierci)
- zabójstwa z aktywną bronią, ze statystyk meczu
- rundy (początek, koniec, zwycięzca), podłożenie, rozbrojenie i wybuch bomby, fazy meczu i wynik
- zabójstwa, asysty, śmierci, MVP, wynik, pieniądze, obrażenia, zabójstwa w głowę, wygrane i przegrane rundy

## Skąd pochodzą dane {#where-it-comes-from}

Game State Integration: żądania HTTP POST na 127.0.0.1:3311, ustawione w pliku &lt;CS2>\game\csgo\cfg\gamestate_integration_heat3d.cfg

## Jak to włączyć {#how-to-switch-it-on}

`python -m heat3d_watch setup cs2-gsi --apply`, potem uruchom CS2 (gra czyta plik przy starcie)

Wpisz polecenie w terminalu otwartym w folderze watchera (zobacz [Zanim zaczniesz](before-you-start.md)). Jeśli się nie uda, ostatnia linia powie dlaczego; [Instalacja i uruchamianie](installing-and-running.md) opisuje częste przyczyny.

`python -m heat3d_watch setup cs2-gsi` pokazuje listę plików, które zostaną zmienione; `python -m heat3d_watch setup cs2-gsi --apply` zmienia je, a oryginał zachowuje jako `<plik>.heat3d-backup` (zobacz [Polecenia](commands.md#setup)). Dla każdej zmiany wypisuje `cs2-gsi: changed: ...`, a gdy wszystko jest już włączone, `cs2-gsi: nothing to change`.

Ustawienia ze zmiennych środowiskowych:

- `HEAT3D_CS2_GSI_PORT`: port, na który gra wysyła dane (domyślnie 3311); plik cfg gry musi podawać ten sam port

## Jak to działa {#how-it-works}

Valve Game State Integration: Counter-Strike 2 i Dota 2 informują lokalny serwer WWW o tym, co się dzieje.

Obie gry przy starcie czytają każdy plik `gamestate_integration_*.cfg` w swoim folderze cfg, a potem przy każdej zmianie stanu wysyłają dokument JSON na `uri` z tego pliku (nie częściej niż co `throttle` sekund, a gdy nic się nie dzieje, co `heartbeat` sekund). Watcher jest tym serwerem WWW: nasłuchuje tylko na 127.0.0.1, od razu odpowiada 200 na każde POST, a pracę wykonuje we własnym wątku.

```text
Counter-Strike 2  <CS2>\game\csgo\cfg\gamestate_integration_heat3d.cfg      port 3311
Dota 2            <Dota>\game\dota\cfg\gamestate_integration\gamestate_integration_heat3d.cfg   port 3312
```

To, co dostaje gracz - a więc to, co może zostać zapisane - decyduje gra, a gracz widzi tylko to, co mu wolno:

- CS2: `provider` (własny steamid), `map` (nazwa, tryb, faza warmup/live/intermission/gameover, runda, wynik drużyn team_ct/team_t), `round` (faza freezetime/live/over, bomba podłożona/wybuchła/rozbrojona, win_team), `player` (obserwowany gracz: ty, gdy żyjesz, kolega z drużyny po śmierci) z `state` (zdrowie, pancerz, pieniądze, round_kills, round_killhs, round_totaldmg), `match_stats` (zabójstwa, asysty, śmierci, mvps, wynik), `position` i `forward` jako ciągi „x, y, z” we współrzędnych świata (w calach, Z w górę), `weapons`; `bomb` tylko dla widzów. Pozycje innych graczy (`allplayers_*`) są wysyłane tylko widzom i GOTV, więc watcher ich nie prosi.
- Dota 2: `map` (matchid, game_state, game_time, clock_time, win_team), `player` (zabójstwa, śmierci, asysty, last_hits, denies, złoto, gpm, xpm, team_name), `hero` (xpos/ypos we współrzędnych świata, poziom, alive, respawn_seconds), `buildings` (zdrowie wież, koszar i ancient), `roshan`, `events` (roshan_killed, aegis_picked_up, ...). Wysokości nie ma: z to 0. Są też pobierane i zachowywane w całości: `abilities`, `items`, `draft`, `wearables`, `minimap`, `couriers`, `neutralitems`, `league` (gra wysyła to, co ma klient gracza; czy któreś z tych pól coś zawiera podczas grania, a nie oglądania, nie zostało sprawdzone).

Każdy dokument jest też zachowywany w całości (zasada konwertera 3DHeat, docs/converters.md w repozytorium przeglądarki): `heat.raw.parquet`, `type` „gsi”, `text` to JSON taki, jaki został wysłany - zamazany jest tylko token z pliku cfg, bo to własny sekret watchera, a nie dane z gry. Dokumenty wysłane, gdy żaden mecz nie jest otwarty (menu, ładowanie, między meczami), czekają w `Backlog` i trafiają do sesji następnego meczu, przed jego początkiem; to, co zostanie, gdy gra się zamknie, dostaje własną sesję, która zawiera tylko je. Nieczytelne posty i posty z błędnym tokenem też są zachowywane („gsi-unreadable”, „gsi-bad-auth”).

Źródła: <https://developer.valvesoftware.com/wiki/Counter-Strike:_Global_Offensive_Game_State_Integration> (format, którego CS2 się trzyma), <https://github.com/antonpup/CounterStrike2GSI> i <https://github.com/antonpup/Dota2GSI> (listy pól; licencja MIT, czytane tylko po faktach).

Ten sam moduł obsługuje też: [Dota 2 (stan gry)](game-dota2-gsi.md).

## Pozycje i osie {#positions-and-axes}

| | |
|---|---|
| Zapisywane pozycje | tak |
| Oś pionowa | `z` |
| Jednostki | cale (jednostki Hammera) |
| Lustrzane odbicie dla przeglądarki | `y` |
| Skala jednostek (`scale`: przeglądarka mnoży przez nią pozycje) | 1 |

Trafiają one do `meta.json` każdej sesji (`axes`) i, gdy sesja ma pozycje, do stopki `heat.parquet`, więc przeglądarka 3DHeat sama obraca i skaluje wiersze - zobacz [Dane](the-data.md).

## Gra wieloosobowa {#multiplayer}

- Oznaczona jako grana online (`multiplayer`): **tak**. `games --markdown` pokazuje to jako „dozwolone (czyta tylko to, co gra publikuje)”.
- Rodzaj `gsi`: czyta tylko to, co gra lub platforma udostępnia (interfejs stanu gry lub lokalne API, które gra udostępnia), więc zapisuje także w grze online, a w trybie offline; flaga decyduje tylko o tym, czy wolno kiedykolwiek czytać pamięć.
- Pamięć: **nigdy** nie jest czytana przez ten adapter. Pamięć czytają tylko adaptery `memory`, i nigdy dla gry oznaczonej jako grana online - zobacz [Źródła i zasady](sources-and-rules.md).

## Zapisywane statystyki {#statistics-recorded}

Klucze statystyk, które kod tego adaptera ustawia po nazwie (`stats` każdej sesji w `meta.json` i tabela `stats` w `watcher.sqlite`):

`bad_auth`, `bad_packets`, `dropped_packets`, `money`, `result`, `score_other`, `score_own`

Klucz w nawiasach klamrowych jest uzupełniany podczas działania (`score.{team}` to jeden klucz na drużynę). Klucze, które kod bierze z tabeli pól gry albo z nazw statystyk gry, nie są na tej liście; „Co jest zapisywane” powyżej podaje je z nazwy.

## Kompletność {#completeness}

Watcher stosuje zasadę konwertera 3DHeat ([zasada konwertera](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md)): to, co zawiera źródło, jest odczytywane albo zachowywane, nigdy pomijane. Oprócz wierszy każdy pakiet, strona, linia czy odpowiedź, którą odbiera adapter, jest zachowywana w całości w `heat.raw.parquet` sesji (kolumny `time`, `ms`, `type`, `used`, `payload`, `text`, a potem pola zachowane po nazwie; `used` oznacza, co też stało się wierszami), a `selfCheck.completeness` w `meta.json` liczy każdy `type` - `lost` wynosi 0.

**Odczytywane**

- zwiedzany gracz: pozycja, kierunek patrzenia, zdrowie, pancerz, pieniądze, aktywna broń, hełm, zestaw do rozbrajania, ilość flashy/dymu/ognia i wartość wyposażenia, w każdym wierszu pozycji, gdy to gracz sam (steamid providera = steamid gracza)
- pojawienia się, śmierci (zdrowie do 0 albo liczba śmierci ze statystyk meczu), zabójstwa (wzrost liczby zabójstw)
- fazy meczu, rundy (czas zamrożenia, live, over, zwycięzca), podłożenie, rozbrojenie i wybuch bomby, wynik
- zabójstwa, asysty, śmierci, MVP, wynik, pieniądze, obrażenia, zabójstwa w głowę, wygrane i przegrane rundy jako statystyki

**Zachowywane w całości**

- `gsi`: każdy dokument wysłany przez grę, w całości, tak jak został wysłany (`text`), `used` ma wartość true, gdy został odczytany w meczu - provider (wersja, znacznik czasu), map (tryb, nazwy drużyn, kolejne przegrane rundy, limity czasu, wygrane serie, `round_wins` z warunkiem wygranej każdej rundy), round, obserwowany gracz (klan, slot obserwatora, aktywność, każda broń ze skórką, amunicją i zapasem), bomb, odliczania faz, a także własne `previously`/`added` gry, czyli różnicę względem poprzedniego posta
- dokumenty z menu, ładowania i z przerw między meczami: zachowywane tak samo, we własnym czasie, przed początkiem następnego meczu; po ostatnim meczu w osobnej sesji (`raw_only` w meta.json)
- `gsi-unreadable`: post, który nie jest obiektem JSON, jego bajty jako `payload` i `length`
- `gsi-bad-auth`: post z innym tokenem niż w pliku cfg

**Niedostępne**

- inni gracze (`allplayers_*`) i granaty (`allgrenades`): gra wysyła je tylko widzom i GOTV, a watcher ich nie prosi (zobacz Źródła i zasady); demo ma wszystkich graczy - zobacz [Counter-Strike 2 (powtórki)](game-cs2-demos.md)
- stany między postami: gra wysyła posty najwyżej co 0,1 s (`throttle`) i tylko przy zmianie, a w przeciwnym razie co 10 s (`heartbeat`)
- token z pliku cfg, zamazany w każdym zachowanym dokumencie: sekret watchera, a nie dane z gry
- posty ponad 10 000 czekających (gdy watcher się zawiesił) są liczone jako `dropped_packets` i nie są zachowywane; post większy niż 4 MB jest zachowywany jako `gsi-unreadable` z długością, ale bez bajtów

**Rozmiar**: dokument gracza ma 2-4 KB i jest wysyłany do 10 razy na sekundę, gdy coś się zmienia: około 30-150 MB na godzinę w `raw.bin`, gdy mecz trwa, a w skompresowanym zstd `heat.raw.parquet` - dziesiątą część tego lub mniej (szacunek na podstawie opublikowanego formatu, nie zmierzony w grze)

## Sprawdzone {#verified}

przetestowane na dokumentach w opublikowanym formacie GSI, wysyłanych do działającego adaptera; instalacja i szukanie folderu cfg przetestowane na lokalnej instalacji; nieprzetestowane z działającą grą

## Źródło {#source}

[heat3d_watch/adapters/gsi.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/gsi.py)

<!-- Generated from the adapter by tools/gen_game_pages.py; change the adapter and run it again rather than editing this page. -->
