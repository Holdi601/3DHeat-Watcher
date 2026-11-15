---
title: "Minecraft (pliki dziennika)"
nav_order: 33
lang: "pl"
source: game-minecraft.md
source_hash: "35cfea9d36a0"
nav_exclude: true
search_exclude: true
---
# Minecraft (pliki dziennika) {#minecraft-log-files}

Gdy grasz w Minecrafta, watcher czyta pliki, które zapisuje gra, i zachowuje to, co się wydarzyło, dzięki czemu później możesz to obejrzeć na mapie w przeglądarce 3DHeat.

*Szczegóły techniczne: adapter `minecraft`, rodzaj [`log`](sources-and-rules.md); działa, gdy uruchomiony jest `javaw.exe` lub `java.exe`, i sprawdza nowe dane co 0,5 s.*

## Co jest zapisywane {#what-is-recorded}

- pozycja własna i innych graczy (bloki = m, Y w górę) za każdym razem, gdy świat się zapisuje; wymiar jako sesja
- pojawienie się z pozycją, gdy gracz dołącza do (zintegrowanego) serwera
- dołączenia, wyjścia, śmierci z komunikatem o śmierci, osiągnięcia, linie czatu
- śmierci, osiągnięcia, wiadomości czatu; z pliku statystyk: czas gry, dystans, zabójstwa potworów i graczy, skoki, obrażenia, wykopane bloki, wytworzone przedmioty (udział z tej sesji)
- każda linia dziennika oraz każdy zapisany plik statystyk, osiągnięć i gracza w całości w heat.raw.parquet

## Skąd pochodzą dane {#where-it-comes-from}

%APPDATA%\\.minecraft\logs\latest.log (śledzony), saves\\&lt;świat>\stats\\&lt;uuid>.json oraz saves\\&lt;świat>\playerdata\\&lt;uuid>.dat i level.dat (NBT spakowany gzipem), czytane, gdy gra je zapisuje

## Jak to włączyć {#how-to-switch-it-on}

Nic nie trzeba włączać: watcher czyta źródło tak, jak podaje je gra lub platforma.

## Jak to działa {#how-it-works}

Minecraft (wydanie Java): dziennik, statystyki i pliki gracza, które gra zapisuje.

Gdzie (`%APPDATA%\.minecraft\`):

* `logs\latest.log` – dziennik gry, nowy przy każdym uruchomieniu (stary jest spakowany do datowanego .log.gz). Linie `[hh:mm:ss] [wątek/POZIOM]: wiadomość` (mod loadery zapisują `[ddMMMyyyy hh:mm:ss.mmm] [wątek/POZIOM] [logger/]: ...`). To, co gracze widzą na czacie, jest w nim: dołączenia i wyjścia, komunikaty o śmierci, osiągnięcia, czat – zintegrowany serwer pojedynczego świata zapisuje te same linie jeszcze raz, więc linia powtórzona w tej samej sekundzie liczy się raz. „Setting user: <nazwa>” wskazuje gracza; wpis serwera „<nazwa>[...] logged in with entity id N at (x, y, z)” podaje, gdzie się pojawił.
* `saves\<świat>\stats\<uuid>.json` – ekran statystyk, zapisywany, gdy świat się zapisuje (autozapis co kilka minut i przy wyjściu): `stats` -> `minecraft:custom` (play_time w tickach, mob_kills, dystanse \*_one_cm, jump, ...), `minecraft:mined`, `minecraft:crafted`, ... Sumy dla świata; liczby tej sesji to różnica względem tego, co plik mówił, gdy gra się uruchomiła. Format: <https://minecraft.wiki/w/Statistics>
* `saves\<świat>\playerdata\<uuid>.dat` (i `level.dat` -> Data -> Player dla hosta pojedynczego świata) – NBT spakowany gzipem, zapisywany przy tych samych zapisach: `Pos` [x, y, z] jako double, `Rotation` [yaw, pitch], `Dimension` („minecraft:overworld”; int 0/-1/1 przed wersją 1.16). NBT wg <https://minecraft.wiki/w/NBT_format> – czytany tutaj przez własny mały czytnik.
* `saves\<świat>\advancements\<uuid>.json` – postęp z ekranu osiągnięć, zapisywany przy tych samych zapisach.

Współrzędne to bloki, jeden blok to metr, Y w górę; X na wschód, Z na południe – układ prawoskrętny, rysowany tak, jak jest. Pozycje pojawiają się tylko przy zapisie świata, więc trasa to kilka punktów na autozapis, a nie ślad; wymiar jest `session`, więc Nether nie rysuje się na Overworldzie.

Wszystko, co odczytane, jest zachowane w całości w surowym pliku sesji (zasada konwertera 3DHeat): każda linia dziennika pod swoim poziomem (`INFO`, `WARN`, `ERROR`, ...; linia bez nawiasowego nagłówka, np. ślad stosu, jako `untagged`), a każdy zapisany plik pod swoim rodzajem (`stats`, `advancements`, `playerdata`, `level.dat`) – JSON jako tekst, NBT jako bajty. Liczby z pliku statystyk mają sens tylko w porównaniu z tym, co mówił na starcie gry, więc ta pierwsza kopia też jest zachowana (`baseline`), przy pierwszej zmianie pliku.

## Pozycje i osie {#positions-and-axes}

| | |
|---|---|
| Zapisane pozycje | tak |
| Oś pionowa | `y` |
| Jednostki | bloki (1 blok = 1 m) |
| Odbicie dla przeglądarki | brak |
| Skala jednostki (`scale`: przeglądarka mnoży przez nią pozycje) | 1 |

Te wartości trafiają do `meta.json` każdej sesji (`axes`) i, gdy sesja ma pozycje, do stopki `heat.parquet`. Dzięki temu przeglądarka 3DHeat sama obraca i skaluje wiersze – zob. [Dane](the-data.md).

## Tryb wieloosobowy {#multiplayer}

- Oznaczona jako gra sieciowa (`multiplayer`): **tak**. `games --markdown` pokazuje to jako „allowed (reads only what the game publishes)”.
- Rodzaj `log`: czyta tylko to, co gra lub platforma udostępnia (pliki, które gra zapisuje podczas działania), więc nagrywa także w grze sieciowej, tak jak w trybie offline. Flaga decyduje tylko o tym, czy pamięć w ogóle może być czytana.
- Pamięć: **nigdy** nie jest czytana przez ten adapter. Tylko adaptery `memory` czytają pamięć, i nigdy dla gry oznaczonej jako sieciowa – zob. [Źródła i zasady](sources-and-rules.md).

## Co jest zapisywane w statystykach {#statistics-recorded}

Klucze statystyk, które kod tego adaptera ustawia po nazwie (`stats` każdej sesji w `meta.json` i tabela `stats` w `watcher.sqlite`):

`advancements`, `bad_files`, `bad_lines`, `chat_messages`, `deaths`, `joins`, `others_deaths`, `world`

Klucz w nawiasach klamrowych jest uzupełniany podczas działania (`score.{team}` to jeden klucz na zespół). Klucze, które kod bierze z tabeli pól gry albo z nazw statystyk gry, nie są na tej liście; „Co jest zapisywane” wyżej wymienia je.

## Kompletność {#completeness}

Watcher stosuje [zasadę konwertera](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md) 3DHeat: to, co źródło zawiera, jest czytane albo zachowywane, nigdy pomijane. Oprócz wierszy każdy pakiet, strona, linia lub odpowiedź, którą adapter otrzyma, jest zachowana w całości w `heat.raw.parquet` sesji (kolumny `time`, `ms`, `type`, `used`, `payload`, `text`, a potem każde pole zachowane po nazwie; `used` oznacza to, co stało się też wierszami). `selfCheck.completeness` w `meta.json` liczy każdy `type`; `lost` wynosi 0.

**Odczytane**

- latest.log: nazwa gracza (`Setting user`), logowania z pozycją, dołączenia, wyjścia, śmierci z komunikatem o śmierci, osiągnięcia, linie czatu, zatrzymanie serwera
- stats/<uuid>.json: czas gry, dystans, zabójstwa potworów i graczy, skoki, zadane i otrzymane obrażenia, wykopane bloki, wytworzone przedmioty – udział tej sesji
- playerdata/<uuid>.dat i level.dat (NBT): pozycja, wymiar, yaw, pitch, zdrowie, poziom doświadczenia

**Zachowane w surowej postaci**

- każda linia latest.log w całości, `type` = jej poziom (`INFO`, `WARN`, `ERROR`, `DEBUG`, `FATAL`), wątek loggera w `thread`, `used`, gdy stała się wierszem; linia bez nawiasowego nagłówka (ślad stosu, baner moda) jako `untagged`
- każdy stats/<uuid>.json w całości jako tekst, `type` `stats` (`used`: jego liczby są w statystykach), z pierwszą kopią z początku gry jako `baseline`
- każdy advancements/<uuid>.json w całości jako tekst, `type` `advancements` (każde kryterium i kiedy zostało spełnione; jeszcze nie zamienione na wiersze)
- każdy playerdata/<uuid>.dat i level.dat w całości jako bajty (NBT gzip), `type` `playerdata` / `level.dat`, `used`, gdy podał pozycję: ekwipunek, skrzynka kresu, efekty, punkt odrodzenia, reguły gry, ziarno świata i czas są tylko tutaj
- każdy zapisany plik ma `world` i `file` (jego ścieżkę w `saves`)

**Niedostępne**

- ślad pozycji: gra zapisuje pozycję gracza tylko wtedy, gdy świat się zapisuje (co kilka minut i przy wyjściu)
- pozycje na serwerze, który hostuje ktoś inny: jego pliki świata są na serwerze, nie tutaj; wtedy czytany jest tylko dziennik
- sam świat (pliki regionów .mca, encje, mapy i najazdy data/\*.dat): duże, a to teren, nie gra
- dzienniki wcześniejszych sesji (logs/\*.log.gz): zachowywane, gdy były rozgrywane
- Minecraft Bedrock Edition: nie zapisuje takiego dziennika ani plików

**Rozmiar**: latest.log 0,1–2 MB na godzinę (więcej z modami); plik statystyk 5–50 KB i plik gracza 5–100 KB na autozapis, level.dat 1–20 KB – około 1–5 MB na godzinę łącznie; zstd w heat.raw.parquet zmniejsza tekst mniej więcej dziesięciokrotnie (pliki NBT są już spakowane gzipem)

## Sprawdzone {#verified}

testowane na syntetycznych liniach dziennika, JSON-ie statystyk i plikach NBT zbudowanych wg opublikowanych formatów; niesprawdzone w grze

## Źródło {#source}

[heat3d_watch/adapters/minecraft.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/minecraft.py)

<!-- Generated from the adapter by tools/gen_game_pages.py; change the adapter and run it again rather than editing this page. -->
