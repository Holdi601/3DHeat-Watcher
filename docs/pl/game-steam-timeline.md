---
title: "Oś czasu Steam (platforma)"
nav_order: 44
lang: "pl"
source: game-steam-timeline.md
source_hash: "3878efe0d7f1"
nav_exclude: true
search_exclude: true
---
# Oś czasu Steam (platforma) {#steam-timeline-platform}

Watcher zapisuje to, co Oś czasu Steam przechowuje o twoich grach, żebyś mógł później przejrzeć historię jako statystyki i oś czasu.

*Szczegóły techniczne: adapter `steam-timeline`, rodzaj [`platform`](sources-and-rules.md); działa cały czas (nie czeka na start gry) i szuka nowych danych co 10 s.*

## Co jest zapisywane {#what-is-recorded}

- jedna sesja na plik osi czasu: jej początek i koniec (session_start, session_end)
- osiągnięcia odblokowane podczas gry, z czasem
- zmiany trybu gry (gra, przygotowanie, menu, ekran ładowania)
- zdarzenia, które gry dodają przez ISteamTimeline, z tytułem i opisem, pod nazwą ikony
- fazy gry (mecz, misja) z ich znacznikami; zdarzenia wewnątrz fazy zapisują jej identyfikator w polu session
- opisy stanu, które gra pokazuje na osi czasu („Round 3”)
- własne błędy nagrywania Steam

## Skąd pochodzi {#where-it-comes-from}

%STEAM%\userdata\\&lt;konto>\gamerecordings\timelines\timeline_&lt;appid>&lt;data>_&lt;godzina>.json

## Jak to włączyć {#how-to-switch-it-on}

Steam > Ustawienia > Nagrywanie gry: nagrywaj w tle albo na żądanie (wtedy Steam zapisuje osie czasu)

## Jak to działa {#how-it-works}

Co program uruchamiający i sterownik karty graficznej przechowują o grze: statystyki Steam, osiągnięcia, czas gry i osie czasu oraz podświetlenia i klipy NVIDIA.

Żadne z tych źródeł nie wymaga, by gra współpracowała albo była uruchomiona, więc trzy adaptery tutaj są zawsze włączone i zaglądają do kilku plików co kilka sekund.

#### Oś czasu Steam (`steam-timeline`) {#steam-timeline-steam-timeline}

`<Steam>\userdata\<konto>\gamerecordings\timelines\timeline_<appid><rrrrmmdd>_<gggggg>.json`, zapisywany, gdy włączone jest nagrywanie gry w Steam. Plik to JSON z liczbami zapisanymi jako tekst: „daterecorded” (sekundy Unix), „starttime”/„endtime” (ms) i „entries”, a każdy wpis to {„id”, „time” (ms od daterecorded), „type”, ...}. Typy widziane w prawdziwych plikach:
```text
achievement        achievement_name - Steam adds these for every game
gamemode           mode, an ETimelineGameMode: 1 playing, 2 staging, 3 menus,
                   4 loading screen
error              description - Steam's own ("#GameRecording_RecordingFailed")
event              a game's AddInstantaneousTimelineEvent/AddRangeTimelineEvent:
                   title, description, icon, priority, duration (ms),
                   possible_clip - "You killed <name>" / "with the <weapon>"
state_description  title - SetTimelineTooltip ("Round 3")
phase              a StartGamePhase..EndGamePhase span: duration (ms), tags
                   [{name, icon, group, priority}] (mode, map ...)
```
Układ pliku jest Steamowy i nieudokumentowany; pola to parametry API. Każdy inny typ jest zapisywany pod własną nazwą, z jego polami.
<https://partner.steamgames.com/doc/api/ISteamTimeline>
<https://partner.steamgames.com/doc/features/timeline>

Ten sam moduł obsługuje też: [NVIDIA Highlights (platforma)](game-nvidia-highlights.md), [Statystyki Steam (platforma)](game-steam-stats.md).

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

`achievements`, `game_mode_changes`, `phases`, `recorded_seconds`, `timeline_events`

Klucz w nawiasach klamrowych jest uzupełniany w czasie działania (`score.{team}` to jeden klucz na drużynę). Klucze, które kod bierze z tabeli pól gry albo z nazw statystyk gry, nie są na tej liście; „Co jest zapisywane” wyżej wymienia je.

## Kompletność {#completeness}

Watcher stosuje [regułę konwertera](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md) 3DHeat: to, co źródło zawiera, jest odczytane albo zachowane, nigdy nie porzucone. Poza wierszami każdy pakiet, strona, linia albo odpowiedź, jaką odbiera adapter, jest zachowana w całości w `heat.raw.parquet` sesji (kolumny `time`, `ms`, `type`, `used`, `payload`, `text`, a potem każde pole zachowane po nazwie; `used` oznacza to, co stało się też wierszami), a `selfCheck.completeness` w `meta.json` liczy każdy `type` – `lost` wynosi 0.

**Odczytane**

- każdy wpis raz, jako wiersz w swoim czasie: jego typ, każde zwykłe pole (tytuł, opis, ikona, priorytet, czas trwania, possible_clip, nazwa osiągnięcia, tryb, ...), znaczniki fazy pogrupowane według grupy, nazwa wyświetlana osiągnięcia ze schematu statystyk; początek i koniec pliku

**Zachowane w surowej postaci**

- każdy wpis w całości jako JSON pod typem Steam (`gamemode`, `achievement`, `event`, `state_description`, `phase`, `error` i każdy inny): zagnieżdżone pola – ikona i priorytet znacznika, cokolwiek, co doda późniejszy Steam – są tylko tutaj
- `timeline`: własne pola pliku (daterecorded, starttime, endtime i każde inne), gdy sesja się otwiera i za każdym razem, gdy się zmienią

**Niedostępne**

- samo nagranie (wideo): Steam trzyma je we własnych folderach; sesja odwołuje się do pliku osi czasu po nazwie
- odczyt pliku, który Steam zapisuje, a którego nie da się sparsować nawet po zamknięciu jego końca: liczony (`bad` w stanie adaptera) i czytany ponownie przy następnej zmianie, kiedy pobierane są jego wpisy

**Rozmiar**: kilkaset wpisów po 100–300 bajtów na godzinę gry – znacznie poniżej 1 MB na godzinę

## Sprawdzone {#verified}

testowane na prawdziwych plikach osi czasu z lokalnej instalacji: wpisy achievement, gamemode, error oraz własne zdarzenia, state_description i phase gier; sam format pliku jest nieudokumentowany

## Źródło {#source}

[heat3d_watch/adapters/platform.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/platform.py)

<!-- Generated from the adapter by tools/gen_game_pages.py; change the adapter and run it again rather than editing this page. -->
