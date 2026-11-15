---
title: "Dota 2 (stan gry)"
nav_order: 13
lang: "pl"
source: game-dota2-gsi.md
source_hash: "100a0d704bbe"
nav_exclude: true
search_exclude: true
---
# Dota 2 (stan gry) {#dota-2-game-state}

Podczas gry w Dota 2 watcher zapisuje to, co gra raportuje do programów na twoim komputerze, abyś mógł później obejrzeć to na mapie w viewerze 3DHeat.

*Szczegóły techniczne: adapter `dota2-gsi`, rodzaj [`gsi`](sources-and-rules.md); działa, gdy `dota2.exe` jest uruchomiony, i sprawdza nowe dane co 0,05 s.*

## Co jest zapisywane {#what-is-recorded}

- położenie własnego bohatera (X/Y świata, jednostki Dota; bez wysokości), gdy żyje
- pojawienie się, śmierci (z czasem odrodzenia) i odrodzenia własnego bohatera
- zabójstwa, wykrywane po wzroście licznika zabójstw
- zniszczone budynki, Roshan, zdarzenia gry (roshan_killed, aegis_picked_up, ...), stany gry, wynik
- zabójstwa, śmierci, asysty, ostatnie trafienia, odmowy, złoto, GPM, XPM, poziom, bohater

## Skąd pochodzi {#where-it-comes-from}

Game State Integration: żądania HTTP POST na 127.0.0.1:3312, ustawione przez &lt;Dota>\game\dota\cfg\gamestate_integration\gamestate_integration_heat3d.cfg

## Jak to włączyć {#how-to-switch-it-on}

`python -m heat3d_watch setup dota2-gsi --apply`, potem uruchom Dota 2 (plik jest czytany przy starcie)

Wpisz polecenie w terminalu otwartym w folderze watchera (zob. [Zanim zaczniesz](before-you-start.md)). Jeśli się nie uda, ostatnia linia powie dlaczego; [Instalacja i uruchamianie](installing-and-running.md) opisuje typowe przyczyny.

`python -m heat3d_watch setup dota2-gsi` wypisuje pliki, które by zmienił; `python -m heat3d_watch setup dota2-gsi --apply` zmienia je, zachowując oryginał jako `<file>.heat3d-backup` (zob. [Polecenia](commands.md#setup)). Dla każdej zmiany wypisuje `dota2-gsi: changed: ...`, a gdy już jest włączone, `dota2-gsi: nothing to change`.

Ustawienia ze zmiennych środowiskowych:

- `HEAT3D_DOTA_GSI_PORT`: port, na który gra wysyła żądania (domyślnie 3312); plik cfg gry musi podawać ten sam port

## Jak to działa {#how-it-works}

Valve Game State Integration: Counter-Strike 2 i Dota 2 mówią lokalnemu serwerowi WWW, co się dzieje.

Obie gry czytają każdy plik `gamestate_integration_*.cfg` w swoim folderze cfg przy starcie
i od tej pory wysyłają dokument JSON POST na `uri` każdego pliku, gdy stan się zmienia (najwyżej
co `throttle` sekund, a co `heartbeat` sekund, gdy nic się nie zmienia). Watcher jest tym
serwerem WWW: nasłuchuje tylko na 127.0.0.1, na każdy POST odpowiada od razu kodem 200 i wykonuje
pracę we własnym wątku odpytującym.

```text
Counter-Strike 2  <CS2>\game\csgo\cfg\gamestate_integration_heat3d.cfg      port 3311
Dota 2            <Dota>\game\dota\cfg\gamestate_integration\gamestate_integration_heat3d.cfg   port 3312
```

To, co jest wysyłane do gracza – a więc to, co może być zapisane – decyduje gra, na co gracz
może patrzeć:

- CS2: `provider` (własny steamid), `map` (nazwa, tryb, faza rozgrzewka/żywo/
  przerwa/koniec gry, runda, wynik team_ct/team_t), `round` (faza freezetime/live/over,
  bomba podłożona/zdetonowana/rozbrojona, win_team), `player` (obserwowany gracz: sam siebie
  żywego, kolegę po śmierci) z `state` (zdrowie, pancerz, pieniądze, round_kills, round_killhs,
  round_totaldmg), `match_stats` (zabójstwa, asysty, śmierci, mvp, wynik), `position` i `forward`
  jako napisy „x, y, z” w jednostkach świata (cale, Z w górę), `weapons`; `bomb` tylko dla
  widzów. Pozycje innych graczy (`allplayers_*`) są wysyłane tylko widzom i GOTV, więc nie są
  żądane.
- Dota 2: `map` (matchid, game_state, game_time, clock_time, win_team), `player`
  (kills, deaths, assists, last_hits, denies, gold, gpm, xpm, team_name), `hero`
  (xpos/ypos w jednostkach świata, level, alive, respawn_seconds), `buildings`
  (zdrowie każdej wieży, koszar, starożytnego), `roshan`, `events` (roshan_killed,
  aegis_picked_up, ...). Nie ma wysokości: z to zawsze 0. Także żądane i zachowywane w całości:
  `abilities`, `items`, `draft`, `wearables`, `minimap`, `couriers`, `neutralitems`, `league`
  (gra wysyła to, co ma klient własnego gracza; które z nich coś zawierają podczas grania, a nie
  oglądania, jest nieprzetestowane).

Każdy dokument jest też zachowany w całości (zasada konwertera 3DHeat, docs/converters.md w
repozytorium viewera): `heat.raw.parquet`, `type` „gsi”, `text` to JSON tak, jak wysłany – tylko
token z pliku cfg zamazany, bo to sekret samego watchera, a nie dane gry. Dokumenty wysłane, gdy
żaden mecz nie jest otwarty (menu, ładowanie, między meczami), czekają w `Backlog` i trafiają do
sesji następnego meczu, przed jego startem; to, co zostanie, gdy gra się zamknie, dostaje własną
sesję, która zawiera tylko je. Niezrozumiałe posty i posty z błędnym tokenem też są zachowane
(„gsi-unreadable”, „gsi-bad-auth”).

Źródła: <https://developer.valvesoftware.com/wiki/Counter-Strike:_Global_Offensive_Game_State_Integration>
(format, którego używa CS2), <https://github.com/antonpup/CounterStrike2GSI> i
<https://github.com/antonpup/Dota2GSI> (listy pól; MIT, czytane tylko dla faktów).

To samo moduł obsługuje też: [Counter-Strike 2 (stan gry)](game-cs2-gsi.md).

## Pozycje i osie {#positions-and-axes}

| | |
|---|---|
| Zapisywane pozycje | tak |
| Oś w górę | `z` |
| Jednostki | jednostki świata Dota (z zawsze 0) |
| Odbicie dla viewera | `y` |
| Skala jednostki (`scale`: viewer mnoży przez nią pozycje) | 1 |

Trafiają one do `meta.json` każdej sesji (`axes`) i, gdy sesja ma pozycje, do stopki `heat.parquet`, więc viewer 3DHeat sam obraca i skaluje wiersze – zob. [Dane](the-data.md).

## Gra wieloosobowa {#multiplayer}

- Oznaczona jako grana online (`multiplayer`): **tak**. `games --markdown` pokazuje to jako „allowed (reads only what the game publishes)”.
- Rodzaj `gsi`: czyta tylko to, co gra lub platforma udostępnia (interfejs game-state integration lub lokalne API, które gra obsługuje), więc nagrywa także w grze online; flaga decyduje tylko o tym, czy pamięć może kiedykolwiek być czytana.
- Pamięć: **nigdy** nie jest czytana przez ten adapter. Tylko adaptery `memory` czytają pamięć i nigdy dla gry oznaczonej jako grana online – zob. [Źródła i zasady](sources-and-rules.md).

## Zapisywane statystyki {#statistics-recorded}

Klucze statystyk, które kod tego adaptera ustawia po nazwie (`stats` każdej sesji w `meta.json` i tabela `stats` w `watcher.sqlite`):

`bad_auth`, `bad_packets`, `dropped_packets`, `hero`, `level`, `result`, `roshan_kills_seen`

Klucz w nawiasach klamrowych jest uzupełniany podczas działania (`score.{team}` to jeden klucz na drużynę). Klucze, które kod bierze z tabeli pól gry albo z jej własnych nazw statystyk, nie są na tej liście; „Co jest zapisywane” wyżej je wymienia.

## Kompletność {#completeness}

Watcher stosuje [zasadę konwertera](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md) 3DHeat: to, co zawiera źródło, jest czytane lub zachowywane, nigdy pomijane. Oprócz wierszy każdy pakiet, strona, linia lub odpowiedź, którą adapter otrzymuje, jest zachowywana w całości w `heat.raw.parquet` sesji (kolumny `time`, `ms`, `type`, `used`, `payload`, `text` i każde pole zachowane po nazwie; `used` oznacza to, co stało się także wierszami), a `selfCheck.completeness` w `meta.json` liczy każdy `type` – `lost` to 0.

**Odczytane**

- położenie (x/y) własnego bohatera, żywy, poziom, zdrowie, maks. zdrowie, mana, maks. mana; pojawienie się, śmierci z czasem odrodzenia, odrodzenia
- zabójstwa (wzrost licznika zabójstw); zabójstwa, śmierci, asysty, ostatnie trafienia, odmowy, złoto, GPM, XPM, wartość netto, poziom i bohater jako statystyki
- zniszczone budynki, Roshan zabity i wrócony, każdy wpis `events` raz, stany gry, zwycięzca

**Zachowane surowo**

- `gsi`: każdy dokument wysłany przez grę, w całości, tak jak wysłany (`text`), `used` prawda, gdy został odczytany w trakcie meczu – wszystkie piętnaście komponentów, o które prosi plik cfg: provider, map (dzień/noc, pauza, czasy odnowienia wardów, wyniki), player (złoto pewne i niepewne, serie, lista zabójstw, wydane komendy, ...), hero (bufy, talenty, Aghanim, atrybuty), abilities, items, buildings, roshan, events, draft, wearables, minimap, couriers, neutralitems, league oraz różnicę gry `previously`/`added`
- dokumenty z menu, ładowania i z przerw między meczami: zachowane tak samo, w swoim czasie, przed startem następnego meczu; po ostatnim meczu – w osobnej sesji (`raw_only` w meta.json)
- `gsi-unreadable`: post, który nie jest obiektem JSON, jego bajty jako `payload` i `length`
- `gsi-bad-auth`: post z innym tokenem niż w pliku cfg

**Niedostępne**

- wysokość: gra wysyła tylko x i y
- inni bohaterowie podczas grania: gra wysyła własnego bohatera, a każdego gracza tylko widzom (wtedy zachowywani surowo, nie rysowani); kilka komponentów (draft, minimap, couriers) zawiera tylko to, co ma klient własnego gracza – a to podczas grania jest nieprzetestowane
- stany między postami: najwyżej jeden co 0,1 s (`throttle`), co 10 s, gdy nic się nie zmienia
- token z pliku cfg, zamazany w każdym zachowanym dokumencie: sekret samego watchera, a nie dane gry
- posty ponad 10 000 czekających (gdy watcher się zaciął) są liczone jako `dropped_packets`, nie zachowywane; post większy niż 4 MB jest zachowany jako `gsi-unreadable` z długością, ale bez bajtów

**Rozmiar**: z każdym komponentem dokument gracza ma około 5–15 KB i jest wysyłany do 10 razy na sekundę (zegar zmienia się w każdym poście): około 100–500 MB na godzinę w `raw.bin`, w trakcie meczu, z czego około jedna dziesiąta w skompresowanym zstd `heat.raw.parquet`; dokument widza, z każdym graczem i minimapą, jest kilka razy większy (oszacowane z opublikowanego formatu, nie zmierzone w grze)

## Sprawdzone {#verified}

przetestowane na dokumentach w opublikowanym formacie GSI wysłanych do działającego adaptera; nieprzetestowane z działającą grą

## Źródło {#source}

[heat3d_watch/adapters/gsi.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/gsi.py)

<!-- Generated from the adapter by tools/gen_game_pages.py; change the adapter and run it again rather than editing this page. -->
