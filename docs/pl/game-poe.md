---
title: "Path of Exile (pliki dziennika)"
nav_order: 36
lang: "pl"
source: game-poe.md
source_hash: "9facfd5a1551"
nav_exclude: true
search_exclude: true
---
# Path of Exile (pliki dziennika) {#path-of-exile-log-files}

Gdy grasz w Path of Exile, watcher odczytuje pliki, które zapisuje gra, i zachowuje to, co się wydarzyło, dzięki czemu później możesz to obejrzeć jako statystyki i oś czasu.

*Szczegóły techniczne: adapter `poe`, rodzaj [`log`](sources-and-rules.md); działa, gdy uruchomiony jest `PathOfExile.exe`, `PathOfExile_x64.exe`, `PathOfExileSteam.exe`, `PathOfExile_x64Steam.exe`, `PathOfExileEGS.exe`, `PathOfExile_x64EGS.exe`, `PathOfExile_KG.exe` lub `PathOfExile_x64_KG.exe`, i sprawdza nowe dane co 0,5 s.*

## Co jest zapisywane {#what-is-recorded}

- strefy, do których wchodzisz, z poziomem obszaru, id obszaru i jego ziarnem
- awanse z klasą i poziomem
- zgony („has been slain”)
- gracze wchodzący i wychodzący z obszaru, szepty przychodzące i wychodzące, prośby o handel, zaakceptowane handle
- każda linia Client.txt z tej sesji w całości w `heat.raw.parquet`
- zgony, zdobyte poziomy, najwyższy poziom, odwiedzone strefy, różne strefy, szepty, prośby o handel, handle

## Skąd pochodzą dane {#where-it-comes-from}

&lt;install>\logs\Client.txt Path of Exile lub Path of Exile 2 (śledzony; folder instalacji to folder uruchomionego pliku wykonywalnego)

## Jak to włączyć {#how-to-switch-it-on}

Nic nie trzeba włączać: watcher odczytuje źródło tak, jak udostępnia je gra lub platforma.

## Jak to działa {#how-it-works}

Path of Exile i Path of Exile 2: dziennik klienta, `<install>\logs\Client.txt`.

Obie gry dopisują do jednego Client.txt w swoim folderze instalacji tak długo,
jak są zainstalowane (plik rośnie przez kolejne uruchomienia). Linie wyglądają tak

```text
2024/01/01 12:00:00 123456789 cff94598 [INFO Client 1234] : You have entered Lioneye's Watch.
2024/01/01 12:00:00 123456789 cff94598 [DEBUG Client 1234] Generating level 2 area "1_1_2" with seed 1
2024/01/01 12:00:00 123456789 cff94598 [INFO Client 1234] : Name (Witch) is now level 2
2024/01/01 12:00:00 123456789 cff94598 [INFO Client 1234] : Name has been slain.
2024/01/01 12:00:00 123456789 cff94598 [INFO Client 1234] @From Name: Hi, I would like to buy your ...
```

- czas lokalny, licznik milisekund, skrót, poziom i wątek, a potem to, co pokazuje
  okno czatu. Komunikaty są z angielskiego klienta; klient w innym języku zapisuje je
  przetłumaczone i nie są tutaj rozpoznawane. Nic nie podaje pozycji. Format nie jest
  udokumentowany przez Grinding Gear Games; to zwykły tekstowy dziennik gry, tak jak czytają go od lat
  społecznościowe narzędzia (pomocnicy handlu, przewodniki po poziomach) – np.
  <https://github.com/klayveR/poe-log-monitor> (MIT) dla listy zdarzeń.

Folder instalacji to folder uruchomionego pliku wykonywalnego; bez niego przeszukiwane są biblioteki Steam
i domyślny folder samodzielnego klienta.

Każda linia tej sesji jest zachowana w całości w surowym pliku pomocniczym sesji (zasada konwertera 3DHeat),
niezależnie od tego, czy coś tutaj znaczy: `type` to poziom i logger w nawiasach
(`INFO Client`, `DEBUG Client`, `WARN Client`, ...), linia z czasem bez nawiasów to
`untagged`, a linia bez znacznika czasu to `untimed`.

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

`bad_lines`, `character_class`, `deaths`, `level`, `levels_gained`, `trade_requests_received`, `trade_requests_sent`, `trades`, `whispers`, `zones_distinct`, `zones_entered`

Klucz w nawiasach klamrowych jest uzupełniany w czasie działania (`score.{team}` to jeden klucz na zespół). Klucze, które kod bierze z tabeli pól gry lub z jej własnych nazw statystyk, nie są na tej liście; sekcja „Co jest zapisywane” wyżej wymienia je.

## Kompletność {#completeness}

Watcher stosuje [zasadę konwertera 3DHeat](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md): to, co źródło zawiera, jest odczytywane lub zachowywane, nigdy nie jest pomijane. Oprócz wierszy każdy pakiet, strona, linia lub odpowiedź, którą adapter otrzyma, jest zachowana w całości w `heat.raw.parquet` sesji (kolumny `time`, `ms`, `type`, `used`, `payload`, `text`, a potem każde pole zachowane po nazwie; `used` oznacza to, co stało się też wierszami), a `selfCheck.completeness` w `meta.json` liczy każdy `type` – `lost` wynosi 0.

**Odczytane**

- `You have entered <zone>`, z poziomem obszaru, id obszaru i ziarnem z linii `Generating level` przed nią
- `<name> (<class>) is now level <n>`, `<name> has been slain`, gracze wchodzący i wychodzący z obszaru, szepty przychodzące i wychodzące (z tym, czy są prośbą o handel), zaakceptowane i anulowane handle

**Zachowane w surowej postaci**

- każda linia tej sesji w całości, `type` = poziom i logger w nawiasach (`INFO Client`, `DEBUG Client`, `WARN Client`, `CRIT Client`, ...), `used` tam, gdzie stała się wierszem: czat globalny, handlowy, grupy i gildii, `Connecting to instance server`, komunikaty AFK i DND, odpowiedzi na komendy czatu, takie jak `/played` i `/deaths`, linie ładowania i silnika klienta – zachowane, jeszcze nie zamienione na wiersze
- linia z czasem bez nawiasów (`***** LOG FILE OPENING *****`) jako `untagged`, linia bez znacznika czasu jako `untimed`

**Niedostępne**

- pozycje: nic w dzienniku ich nie podaje
- to, co zapisuje klient w innym języku: linie są zachowane, ale na wiersze zamieniane są tylko angielskie komunikaty
- linie wcześniejszych uruchomień: Client.txt rośnie przez kolejne uruchomienia; linie z czasem sprzed tego przebiegu gry są pomijane (zostały zachowane, gdy były grane)
- zabójstwa, obrażenia, łupy i drzewko pasywne: gra ich nie zapisuje

**Rozmiar**: Client.txt rośnie o około 0,3-3 MB na godzinę (najwięcej z linii DEBUG podczas ładowania obszarów, więcej przy zajętym czacie handlowym); zstd w `heat.raw.parquet` zmniejsza to mniej więcej dziesięciokrotnie

## Sprawdzone {#verified}

przetestowane na syntetycznych liniach Client.txt w formacie gry; nie przetestowane w grze

## Źródło {#source}

[heat3d_watch/adapters/poe.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/poe.py)

<!-- Generated from the adapter by tools/gen_game_pages.py; change the adapter and run it again rather than editing this page. -->
