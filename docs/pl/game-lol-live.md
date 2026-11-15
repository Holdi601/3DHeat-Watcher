---
title: "League of Legends (stan gry)"
nav_order: 29
lang: "pl"
source: game-lol-live.md
source_hash: "75c67c6fe84f"
nav_exclude: true
search_exclude: true
---
# League of Legends (stan gry) {#league-of-legends-game-state}

Gdy grasz w League of Legends, watcher zapisuje to, co gra podaje programom na twoim komputerze, dzięki czemu później możesz to obejrzeć jako statystyki i oś czasu.

*Szczegóły techniczne: adapter `lol-live`, rodzaj [`gsi`](sources-and-rules.md); działa, gdy uruchomiony jest `League of Legends.exe`, i sprawdza nowe dane co 0,5 s.*

## Co jest zapisywane {#what-is-recorded}

- brak pozycji: API ich nie ma
- kanał zabójstw: zabójstwa, zgony i asysty gracza, zabójstwa innych bohaterów z zabójcą, ofiarą i asystującymi
- smoki, heroldy, barony, wieże, inhibitory, multikille, asy, pierwsza krew, start i koniec gry
- własne zabójstwa, zgony, asysty, wynik w creepach, wynik w wardach, poziom, złoto, bohater, czas gry, wynik
- cele zdobyte przez drużynę gracza

## Skąd pochodzą dane {#where-it-comes-from}

Live Client Data API klienta gry, <https://127.0.0.1:2999/liveclientdata/> (allgamedata, eventdata), podczas meczu

## Jak to włączyć {#how-to-switch-it-on}

Nic nie trzeba włączać: watcher odczytuje źródło tak, jak udostępnia je gra lub platforma.

## Jak to działa {#how-it-works}

League of Legends: Live Client Data API, które klient gry udostępnia podczas meczu.

Podczas meczu (także w trybie treningowym i obserwatora) `League of
Legends.exe` odpowiada pod <https://127.0.0.1:2999> tym, co gracz widzi
w interfejsie gry:

```text
/liveclientdata/allgamedata          activePlayer (riotId, level, currentGold, championStats),
                                     allPlayers (championName, team ORDER/CHAOS, level,
                                     scores: kills, deaths, assists, creepScore, wardScore),
                                     events, gameData (gameMode, gameTime s, mapName)
/liveclientdata/eventdata?eventID=N  {"Events": [...]} od EventID N: GameStart,
                                     MinionsSpawning, FirstBlood, FirstBrick, TurretKilled,
                                     InhibKilled, InhibRespawningSoon, InhibRespawned,
                                     DragonKill, HeraldKill, BaronKill, ChampionKill
                                     (KillerName, VictimName, Assisters), Multikill
                                     (KillStreak), Ace (Acer, AcingTeam), GameEnd (Result)
```

Nie ma pozycji: API ich nie podaje, więc sesja League to zdarzenia i statystyki, bez tabeli heat. Certyfikat jest
podpisany przez siebie, przez główny certyfikat Riot (`riotgames.pem`, opublikowany pod
<https://static.developer.riotgames.com/docs/lol/riotgames.pem>). Warunki jego użycia nie są podane, więc nie jest dołączany: umieść go w `<data>\riotgames.pem`, a połączenie
zostanie nim zweryfikowane; bez niego weryfikacja jest wyłączona – i tylko
dla 127.0.0.1, jedynego adresu, z którym ten adapter rozmawia.

Zasady Riot pozwalają narzędziom pokazywać to, co gracz mógłby wiedzieć z samej gry, i nic
wyliczonego ponad to (żadnych timerów wroga): zapisywany jest kanał zabójstw i tablica wyników, którą widzi
gracz, oraz jego własne liczby.

Każda odpowiedź jest też zachowywana w całości (zasada konwertera 3DHeat, docs/converters.md w
repozytorium przeglądarki): `heat.raw.parquet`, `type` to endpoint
(„allgamedata„, „eventdata”), `text` to JSON tak, jak wysłał go klient, `status`
gdy nie było 200. Odpowiedź bajt w bajt taka sama jak poprzednia z tego samego endpointu (lista zdarzeń, gdy nic się nie dzieje) jest zachowana raz i liczona w `unchanged_replies` w meta.json. allgamedata zawiera wszystko, co podają pozostałe endpointy (activeplayer\*, playerlist, playerscores, playeritems, playersummonerspells,
playermainrunes, gamestats), więc nie są pytane osobno. Odpowiedzi przed
meczem (ekran ładowania) czekają w zaległościach i trafiają do sesji meczu;
po GameEnd sesja pozostaje otwarta, dopóki klient nie zniknie, więc odpowiedzi z ekranu końcowego są zachowywane razem z nią.

Źródło: <https://developer.riotgames.com/docs/lol#game-client-api>

## Pozycje i osie {#positions-and-axes}

| | |
|---|---|
| Zapisane pozycje | nie |
| Oś pionowa | `z` |
| Jednostki | brak (bez pozycji) |
| Odbicie dla przeglądarki | brak |
| Skala jednostki (`scale`: przeglądarka mnoży przez nią pozycje) | 1 |

Te wartości trafiają do `meta.json` każdej sesji (`axes`) i, gdy sesja ma pozycje, do stopki `heat.parquet`. Dzięki temu przeglądarka 3DHeat sama obraca i skaluje wiersze – zob. [Dane](the-data.md).

## Tryb wieloosobowy {#multiplayer}

- Oznaczone jako grane online (`multiplayer`): **tak**. `games --markdown` pokazuje to jako „dozwolone (odczytuje tylko to, co gra publikuje)”.
- Rodzaj `gsi`: odczytuje tylko to, co gra lub platforma udostępnia (integrację stanu gry albo lokalne API, które gra udostępnia), więc nagrywa też w grze online; flaga decyduje tylko o tym, czy wolno kiedykolwiek czytać pamięć.
- Pamięć: **nigdy** nie jest odczytywana przez ten adapter. Tylko adaptery `memory` czytają pamięć, i nigdy dla gry oznaczonej jako grana online – zob. [Źródła i zasady](sources-and-rules.md).

## Co jest zapisywane w statystykach {#statistics-recorded}

Klucze statystyk, które kod tego adaptera ustawia po nazwie (`stats` każdej sesji w `meta.json` i tabela `stats` w `watcher.sqlite`):

`bad_packets`, `champion`, `game_time`, `gold`, `level`, `result`

Klucz w nawiasach klamrowych jest uzupełniany w czasie działania (`score.{team}` to jeden klucz na zespół). Klucze, które kod bierze z tabeli pól gry lub z jej własnych nazw statystyk, nie są na tej liście; sekcja „Co jest zapisywane” wyżej wymienia je.

## Kompletność {#completeness}

Watcher stosuje [zasadę konwertera 3DHeat](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md): to, co źródło zawiera, jest odczytywane lub zachowywane, nigdy nie jest pomijane. Oprócz wierszy każdy pakiet, strona, linia lub odpowiedź, którą adapter otrzyma, jest zachowana w całości w `heat.raw.parquet` sesji (kolumny `time`, `ms`, `type`, `used`, `payload`, `text`, a potem każde pole zachowane po nazwie; `used` oznacza to, co stało się też wierszami), a `selfCheck.completeness` w `meta.json` liczy każdy `type` – `lost` wynosi 0.

**Odczytane**

- kanał zabójstw z eventdata: każde zdarzenie raz, z zdekodowanymi nazwanymi polami (zabójca, ofiara i asystujący z bohaterem i drużyną, konstrukcje i ich strona, rodzaj smoka, przejęcia, multikille, asy, pierwsza krew, wynik), a każde inne pole zdarzenia na jego wierszu pod własną nazwą
- z allgamedata: własne zabójstwa, zgony, asysty, wynik w creepach, wynik w wardach, poziom, złoto, bohater, czas gry, tryb i mapa gry

**Zachowane w surowej postaci**

- `allgamedata`: każda odpowiedź w całości (`text`), co 2 s – activePlayer (zdolności, każda statystyka bohatera, pełne runy, złoto, poziom), allPlayers (przedmioty z slotami i cenami, runy, czary przywoływacza, wyniki, poziom, martwy i czas odrodzenia, skórka, pas, bot), zdarzenia, gameData (tryb, czas, mapa, teren); `used` prawda, gdy mecz trwa, fałsz na ekranie końcowym
- `eventdata`: każda odpowiedź w całości, pytana co 0,5 s od następnego id zdarzenia; `used` prawda, gdy przyniosła nowe zdarzenia
- odpowiedź bajt w bajt taka sama jak poprzednia z tego endpointu jest zachowana raz i liczona (`unchanged_replies` w meta.json); odpowiedzi błędu (RESOURCE_NOT_FOUND z ekranu ładowania) są zachowane z `status`, przed startem meczu

**Niedostępne**

- pozycje: API ich nie ma (brak minimapy, brak współrzędnych)
- pozostałe endpointy (activeplayer, activeplayername, activeplayerabilities, activeplayerrunes, playerlist, playerscores, playersummonerspells, playermainrunes, playeritems, gamestats): każdy podaje część allgamedata, więc nie są pytane
- Replay API (`/replay/*` na tym samym porcie): odtwarza powtórki i oglądane mecze po włączeniu w game.cfg; nie jest częścią rozgrywanego meczu
- endpointy lockfile klienta League: to nie jest opublikowane API (zob. Źródła i zasady)
- wartości między dwoma odczytami: API odpowiada na zapytanie i niczego nie wysyła samo; wynik jest pytany co 2 s, zdarzenia co 0,5 s

**Rozmiar**: allgamedata to 15-40 KB (zawiera całą listę zdarzeń, która rośnie) co 2 s: około 30-70 MB na godzinę w `raw.bin`; eventdata dodaje niewiele, bo niezmienione odpowiedzi są liczone, a nie zapisywane; zstd zmniejsza powtarzający się JSON w `heat.raw.parquet` do kilku MB na godzinę (oszacowane na podstawie udokumentowanego formatu)

## Sprawdzone {#verified}

przetestowane na fałszywym lokalnym serwerze, który podaje odpowiedzi w udokumentowanym formacie; nie przetestowane w grze

## Źródło {#source}

[heat3d_watch/adapters/lol.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/lol.py)

<!-- Generated from the adapter by tools/gen_game_pages.py; change the adapter and run it again rather than editing this page. -->
