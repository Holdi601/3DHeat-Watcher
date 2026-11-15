---
title: "Statystyki Steam (platforma)"
nav_order: 43
lang: "pl"
source: game-steam-stats.md
source_hash: "24fa6512bd6d"
nav_exclude: true
search_exclude: true
---
# Statystyki Steam (platforma) {#steam-statistics-platform}

Watcher zapisuje to, co statystyki Steam przechowują o twoich grach, żebyś mógł później przejrzeć historię jako statystyki i oś czasu.

*Szczegóły techniczne: adapter `steam-stats`, rodzaj [`platform`](sources-and-rules.md); działa cały czas (nie czeka na start gry) i szuka nowych danych co 30 s.*

## Co jest zapisywane {#what-is-recorded}

- każda statystyka, którą gra przechowuje w Steam (jej własne nazwy i wartości), dla każdej gry, gdy się zmieni
- odblokowania osiągnięć z nazwą wyświetlaną, opisem i czasem odblokowania
- zmiany statystyk ze starą wartością, nową wartością i różnicą
- czas gry (minuty, ostatnie dwa tygodnie) i czas ostatniego uruchomienia

## Skąd pochodzi {#where-it-comes-from}

lokalna pamięć podręczna statystyk Steam %STEAM%\appcache\stats\UserGameStats_&lt;konto>_&lt;appid>.bin wraz z UserGameStatsSchema_&lt;appid>.bin; czas gry z %STEAM%\userdata\\&lt;konto>\config\localconfig.vdf (%STEAM% z HKCU\Software\Valve\Steam SteamPath)

## Jak to włączyć {#how-to-switch-it-on}

nic nie trzeba włączać: watcher czyta źródło tak, jak dostarcza je gra lub platforma.

## Jak to działa {#how-it-works}

Co program uruchamiający i sterownik karty graficznej przechowują o grze: statystyki Steam, osiągnięcia, czas gry i osie czasu oraz podświetlenia i klipy NVIDIA.

Żadne z tych źródeł nie wymaga, by gra współpracowała albo była uruchomiona, więc trzy adaptery tutaj są zawsze włączone i zaglądają do kilku plików co kilka sekund.

#### Statystyki Steam (`steam-stats`) {#steam-statistics-steam-stats}

`<Steam>\appcache\stats\UserGameStats_<konto>_<appid>.bin`, zapisywany ponownie przez klienta Steam za każdym razem, gdy gra zapisuje swoje statystyki, dekodowany ze schematem `UserGameStatsSchema_<appid>.bin` obok (binarne KeyValues, zob. `_steam.py`). Statystyki są liczbami całkowitymi lub zmiennoprzecinkowymi, tak jak je definiuje gra; osiągnięcia to bity z czasem odblokowania w sekundach Unix. Czas gry jest w `<Steam>\userdata\<konto>\config\localconfig.vdf` pod apps/&lt;appid>: Playtime i Playtime2wks w minutach, LastPlayed w sekundach Unix. Steam jest odnajdywany przez HKCU\Software\Valve\Steam SteamPath. API statystyk: <https://partner.steamgames.com/doc/features/achievements>

Ten sam moduł obsługuje też: [NVIDIA Highlights (platforma)](game-nvidia-highlights.md), [Oś czasu Steam (platforma)](game-steam-timeline.md).

## Pozycje i osie {#positions-and-axes}

| | |
|---|---|
| Zapisywane pozycje | nie |
| Oś w górę | `y` |
| Jednostki | metry |
| Odbicie dla przeglądarki | brak |
| Skala jednostek (`scale`: przeglądarka mnoży przez nią pozycje) | 1 |

Trafiają one do `meta.json` każdej sesji (`axes`) i, gdy sesja ma pozycje, do stopki `heat.parquet`, więc przeglądarka 3DHeat sama obraca i skaluje wiersze – zob. [Dane](the-data.md).

## Gra wieloosobowa {#multiplayer}

- Oznaczona jako gra online (`multiplayer`): **nie**. `games --markdown` pokazuje to jako „tylko dla jednego gracza”.
- Rodzaj `platform`: czyta tylko to, co gra lub platforma udostępnia (to, co zachowuje Steam albo sterownik karty), więc zapisuje także w grze online, a nie tylko offline; flaga decyduje wyłącznie o tym, czy wolno kiedykolwiek czytać pamięć.
- Pamięć: **nigdy** nie jest czytana przez ten adapter. Tylko adaptery `memory` czytają pamięć i nigdy dla gry oznaczonej jako online – zob. [Źródła i zasady](sources-and-rules.md).

## Zapisywane statystyki {#statistics-recorded}

Klucze statystyk, które kod tego adaptera ustawia po nazwie (`stats` każdej sesji w `meta.json` i tabela `stats` w `watcher.sqlite`):

`achievements_total`, `achievements_unlocked`, `last_played`, `playtime_2wks_minutes`, `playtime_minutes`

Klucz w nawiasach klamrowych jest uzupełniany w czasie działania (`score.{team}` to jeden klucz na drużynę). Klucze, które kod bierze z tabeli pól gry albo z nazw statystyk gry, nie są na tej liście; „Co jest zapisywane” wyżej wymienia je.

## Kompletność {#completeness}

Watcher stosuje [regułę konwertera](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md) 3DHeat: to, co źródło zawiera, jest odczytane albo zachowane, nigdy nie porzucone. Poza wierszami każdy pakiet, strona, linia albo odpowiedź, jaką odbiera adapter, jest zachowana w całości w `heat.raw.parquet` sesji (kolumny `time`, `ms`, `type`, `used`, `payload`, `text`, a potem każde pole zachowane po nazwie; `used` oznacza to, co stało się też wierszami), a `selfCheck.completeness` w `meta.json` liczy każdy `type` – `lost` wynosi 0.

**Odczytane**

- każda statystyka z pliku statystyk po nazwie API (int, float, avgrate), każdy bit osiągnięcia z czasem odblokowania, nazwane i opisane przez schemat
- zmiany względem ostatniego odczytu (stara wartość, nowa, różnica), nowe odblokowania; czas gry, czas z ostatnich dwóch tygodni i czas ostatniego uruchomienia z localconfig.vdf

**Zachowane w surowej postaci**

- `UserGameStats`: bajty pliku statystyk, w całości, za każdym zapisem (w nim są `crc`, `PendingChanges`, bity osiągnięć, których schemat już nie definiuje, i każdy klucz pominięty przez dekoder)
- `UserGameStatsSchema`: bajty pliku schematu obok, tak by statystyki dało się zdekodować samą sesją (nazwy każdej statystyki i osiągnięcia we wszystkich językach, ikony, flagi)
- `localconfig_app`: cały blok gry z localconfig.vdf jako JSON (stan synchronizacji w chmurze, opcje uruchamiania, odznaki i każdy inny klucz, jaki Steam trzyma dla gry), gdy zapisywany jest czas gry
- plik statystyk, którego dekoder nie potrafi odczytać (ucięty w trakcie zapisu albo w nowym układzie): jego bajty i schemat w sesji bez wierszy (`used` false; `unreadable` w meta.json)

**Niedostępne**

- reszta localconfig.vdf (znajomi, czat, ustawienia Steam): nie należy do gry i jest prywatna
- wartości statystyk między dwoma zapisami: Steam przepisuje plik, gdy gra zapisuje statystyki, zwykle przy zamknięciu
- globalne procenty osiągnięć i statystyki innych graczy: są na serwerach Steam, nie tutaj

**Rozmiar**: kilka KB na zapisaną sesję gry, plus schemat (do kilkuset KB dla gry z wieloma osiągnięciami) – znacznie poniżej 1 MB na godzinę gry; zstd zmniejsza tekst schematu o połowę lub więcej

## Sprawdzone {#verified}

testowane na prawdziwych plikach statystyk i schematach z lokalnej instalacji; wykrywanie zmian – na plikach zbudowanych w binarnym formacie KeyValues

## Źródło {#source}

[heat3d_watch/adapters/platform.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/platform.py)

<!-- Generated from the adapter by tools/gen_game_pages.py; change the adapter and run it again rather than editing this page. -->
