---
title: "Elite Dangerous (pliki dziennika)"
nav_order: 18
lang: "pl"
source: game-elite.md
source_hash: "bb5bcf75553a"
nav_exclude: true
search_exclude: true
---
# Elite Dangerous (pliki dziennika) {#elite-dangerous-log-files}

Gdy grasz w Elite Dangerous, watcher czyta pliki, które zapisuje gra, i zachowuje to, co się wydarzyło, dzięki czemu później możesz to obejrzeć na mapie w przeglądarce 3DHeat.

*Szczegóły techniczne: adapter `elite`, rodzaj [`log`](sources-and-rules.md); działa, gdy uruchomiony jest `EliteDangerous64.exe`, i sprawdza nowe dane co 0,25 s.*

## Co jest zapisywane {#what-is-recorded}

- każde zdarzenie dziennika pod jego nazwą z dziennika, z prostymi polami
- pozycja w galaktyce (StarPos, lata świetlne) przy skokach, lokalizacjach, odrodzeniach, śmierciach, dokowaniu, lądowaniu
- odrodzenie przy LoadGame/Resurrect, śmierć przy Died, zadokowanie/odsunięcie, dotknięcie ziemi/start, skok, session_end
- trasa po powierzchni planety z Status.json: szerokość, długość, wysokość, kierunek, i metry w lokalnej płaszczyźnie stycznej dla każdego ciała (sesja = nazwa ciała), wraz z innymi prostymi polami Status.json (Flags, Flags2, GuiFocus, LegalState, ...)
- każda linia dziennika i każdy plik towarzyszący w całości w heat.raw.parquet
- skoki, przebyty dystans skokami, śmierci, zabójstwa, zarobione kredyty, ukończone misje, zeskanowane ciała, odwiedzone systemy, dokowania, lądowania

## Skąd pochodzą dane {#where-it-comes-from}

Dziennik gracza %USERPROFILE%\Saved Games\Frontier Developments\Elite Dangerous\Journal.\*.log (najnowszy plik, śledzony na bieżąco), Status.json i inne pliki towarzyszące \*.json (Market, Outfitting, Shipyard, NavRoute, Cargo, ModulesInfo, ShipLocker, Backpack, FCMaterials) w tym samym folderze

## Jak to włączyć {#how-to-switch-it-on}

Nic nie trzeba włączać: watcher czyta źródło tak, jak podaje je gra lub platforma.

## Jak to działa {#how-it-works}

Elite Dangerous: dziennik gracza (Player Journal) i Status.json, które gra zapisuje podczas działania.

Gdzie: `%USERPROFILE%\Saved Games\Frontier Developments\Elite Dangerous\`

* `Journal.<yyyy-mm-ddThhmmss>.<part>.log` – jeden obiekt JSON w wierszu, jeden plik na każde uruchomienie (długa sesja jest kontynuowana w części .02, .03 ...). Każda linia ma `timestamp` (UTC, ISO 8601) i `event`. Pozycje w galaktyce to `StarPos` [x, y, z] systemu, w latach świetlnych od Sol, przy `FSDJump`, `Location` i `CarrierJump`. Galaktyczny układ Elite ma oś y w górę (ku północy galaktycznej), z ku centrum galaktyki i x ku długości galaktycznej 270 – to układ lewoskrętny, więc przeglądarka odbija z, by rysować go we właściwą stronę.
* `Status.json` – zapisywany w całości za każdym razem, gdy zmienia się stan statku: `Flags`, a w pobliżu planety `Latitude`, `Longitude` (stopnie), `Altitude` (metry), `Heading`, `BodyName` i `PlanetRadius` (metry).
* Pozostałe pliki towarzyszące, każdy zapisywany w całości, gdy odpowiadające mu zdarzenie dziennika zostanie zapisane: `Market.json`, `Outfitting.json`, `Shipyard.json`, `NavRoute.json`, `Cargo.json`, `ModulesInfo.json`, `ShipLocker.json`, `Backpack.json`, `FCMaterials.json`. Każdy plik `*.json` z tego folderu, który gra zapisuje podczas tej sesji, jest zachowywany w całości za każdym razem, gdy się zmieni (zasada konwertera 3DHeat: to, co źródło zawiera, jest czytane albo zachowywane), pod swoją nazwą pliku.

Każda linia dziennika jest zachowywana w całości w surowym pliku sesji pod swoim `event`, każdy plik towarzyszący pod swoją nazwą; linia, która nie jest JSON-em, trafia pod `unparsed`.

Pozycje na powierzchni są umieszczane w lokalnej płaszczyźnie stycznej dla każdego ciała, w metrach: pierwszy odczyt na ciele jest jego początkiem, x na wschód, z na północ, y w górę (wysokość), ta sama skrętność co układ galaktyczny; wiersze mają nazwę ciała jako `session`, więc przejazd lub spacer po planecie rysuje się jako osobna trasa. Wiersze galaktyczne mają sesję „galaxy”. Obie skale są w jednej tabeli; sesję wybierasz w przeglądarce.

Format: podręcznik Frontiera „Elite Dangerous Player Journal” (publikowany z każdą aktualizacją na oficjalnym forum, <https://forums.frontier.co.uk/> – „Journal Manual”, v4.x), zdarzenia i pola według tego podręcznika; flagi Status.json według rozdziału „Status File” z tego samego podręcznika.

## Pozycje i osie {#positions-and-axes}

| | |
|---|---|
| Zapisane pozycje | tak |
| Oś pionowa | `y` |
| Jednostki | lata świetlne (wiersze galaktyczne, sesja „galaxy”); metry na wschód/w górę/na północ od pierwszego odczytu na ciele (wiersze powierzchni, sesja = nazwa ciała) |
| Odbicie dla przeglądarki | `z` |
| Skala jednostki (`scale`: przeglądarka mnoży przez nią pozycje) | 1 |

Te wartości trafiają do `meta.json` każdej sesji (`axes`) i, gdy sesja ma pozycje, do stopki `heat.parquet`. Dzięki temu przeglądarka 3DHeat sama obraca i skaluje wiersze – zob. [Dane](the-data.md).

## Tryb wieloosobowy {#multiplayer}

- Oznaczona jako gra sieciowa (`multiplayer`): **tak**. `games --markdown` pokazuje to jako „allowed (reads only what the game publishes)”.
- Rodzaj `log`: czyta tylko to, co gra lub platforma udostępnia (pliki, które gra zapisuje podczas działania), więc nagrywa także w grze sieciowej, tak jak w trybie offline. Flaga decyduje tylko o tym, czy pamięć w ogóle może być czytana.
- Pamięć: **nigdy** nie jest czytana przez ten adapter. Tylko adaptery `memory` czytają pamięć, i nigdy dla gry oznaczonej jako sieciowa – zob. [Źródła i zasady](sources-and-rules.md).

## Co jest zapisywane w statystykach {#statistics-recorded}

Klucze statystyk, które kod tego adaptera ustawia po nazwie (`stats` każdej sesji w `meta.json` i tabela `stats` w `watcher.sqlite`):

`bad_lines`, `bodies_scanned`, `carrier_jumps`, `credits`, `credits_earned`, `deaths`, `distance_ly`, `dockings`, `jumps`, `kills`, `landings`, `missions_completed`, `ship`, `surface_fixes`, `systems_visited`

Klucz w nawiasach klamrowych jest uzupełniany podczas działania (`score.{team}` to jeden klucz na zespół). Klucze, które kod bierze z tabeli pól gry albo z nazw statystyk gry, nie są na tej liście; „Co jest zapisywane” wyżej wymienia je.

## Kompletność {#completeness}

Watcher stosuje [zasadę konwertera](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md) 3DHeat: to, co źródło zawiera, jest czytane albo zachowywane, nigdy pomijane. Oprócz wierszy każdy pakiet, strona, linia lub odpowiedź, którą adapter otrzyma, jest zachowana w całości w `heat.raw.parquet` sesji (kolumny `time`, `ms`, `type`, `used`, `payload`, `text`, a potem każde pole zachowane po nazwie; `used` oznacza to, co stało się też wierszami). `selfCheck.completeness` w `meta.json` liczy każdy `type`; `lost` wynosi 0.

**Odczytane**

- każda linia dziennika jako wiersz pod swoim `event`, z prostymi polami (tekst zlokalizowany, jeśli gra go podaje; teksty dłuższe niż 300 znaków są w wierszu skracane)
- wiersze galaktyczne (StarPos) przy FSDJump, CarrierJump, Location, LoadGame, Resurrect, Died, Docked, Undocked, Touchdown, Liftoff, Shutdown; wiersze powierzchni z Status.json oraz Touchdown/Liftoff
- proste pola Status.json (Flags, Flags2, GuiFocus, LegalState, Cargo, FireGroup, Oxygen, Health, Temperature, Gravity, SelectedWeapon, ...) na wierszach powierzchni
- statystyki: skoki, dystans, śmierci, zabójstwa, zarobione kredyty, misje, zeskanowane ciała, odwiedzone systemy, dokowania, lądowania

**Zachowane w surowej postaci**

- każda linia dziennika w całości, `type` = jej `event` (FSDJump, Scan, Music, ReceiveText, ...), `used` ma wartość true: listy i obiekty, które pomijają wiersze (StarPos, Factions, Rewards, Killers, Materials, Modules, ...), są tylko tutaj
- linia dziennika, która nie jest JSON-em, `type` `unparsed`
- każdy plik towarzyszący w całości za każdym razem, gdy gra go przepisze, `type` = jego nazwa pliku: `Status.json` (`used`, gdy utworzył wiersz powierzchni), `Market.json`, `Outfitting.json`, `Shipyard.json`, `NavRoute.json`, `Cargo.json`, `ModulesInfo.json`, `ShipLocker.json`, `Backpack.json`, `FCMaterials.json` i każdy inny `*.json`, który gra tam zapisuje

**Niedostępne**

- pozycja między skokami (w systemie, w supercruise lub w zwykłej przestrzeni): gra zapisuje tylko StarPos systemu i, w pobliżu planety, szerokość, długość i wysokość
- pozycje innych statków i graczy: dziennik to własna relacja dowódcy
- prędkość, gaz i inne dane lotu: gra ich nie zapisuje
- dzienniki i pliki towarzyszące wcześniejszych sesji: zachowywane, gdy były rozgrywane (śledzenie zaczyna się od końca pliku starszego niż to uruchomienie gry)
- webowe API Frontiera (cAPI): wymaga logowania gracza do Frontiera; to nie jest plik zapisywany przez grę

**Rozmiar**: około 1–5 MB surowego tekstu na godzinę: dziennik 0,2–2 MB, Status.json (poniżej 1 KB, przepisywany co sekundę) 1–2 MB, zestaw market/outfitting/shipyard 20–150 KB na każdą odwiedzoną stację; zstd w heat.raw.parquet zmniejsza to mniej więcej dziesięciokrotnie

## Sprawdzone {#verified}

parser odtworzony na prawdziwych plikach dziennika z lokalnej instalacji (liczba zdarzeń zgadza się ze statystykami); poprawki powierzchni z Status.json testowane tylko na syntetycznych migawkach

## Źródło {#source}

[heat3d_watch/adapters/elite.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/elite.py)

<!-- Generated from the adapter by tools/gen_game_pages.py; change the adapter and run it again rather than editing this page. -->
