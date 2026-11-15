---
title: "NVIDIA highlights (platforma)"
nav_order: 34
lang: "pl"
source: game-nvidia-highlights.md
source_hash: "5d45211c0e37"
nav_exclude: true
search_exclude: true
---
# NVIDIA highlights (platforma) {#nvidia-highlights-platform}

Watcher zapisuje to, co NVIDIA highlights przechowuje o twoich grach, dzięki czemu później możesz oglądać swoją historię na mapie w przeglądarce 3DHeat.

*Szczegóły techniczne: adapter `nvidia-highlights`, rodzaj [`platform`](sources-and-rules.md); działa cały czas (nie czeka, aż uruchomi się gra) i sprawdza nowe dane co 10 s.*

## Co jest zapisywane {#what-is-recorded}

- każdy nowy klip, highlight lub zrzut ekranu: gra, plik, rodzaj, długość i chwila (czas ścienny w ms)
- id i nazwa highlightu, gdy gra zarejestrowała go w NVIDIA
- gdzie gracz był w tej chwili, gdy inny adapter nagrywał wtedy tę grę
- żądania highlightów z logów GfeSDK, nawet gdy żaden klip nie został zachowany

## Skąd pochodzą dane {#where-it-comes-from}

%LOCALAPPDATA%\NVIDIA Corporation\NVIDIA Overlay\UGCTracker.json, GallerySettings.json, Highlights\\&lt;game>\config.json; klipy w folderze przechwytywania (%USERPROFILE%\Videos\NVIDIA\\&lt;Game>\\\*.mp4) i &lt;temp>\Highlights\\&lt;game>; %LOCALAPPDATA%\NVIDIA Corporation\GfeSDK\\&lt;exe>_&lt;pid>.log

## Jak to włączyć {#how-to-switch-it-on}

NVIDIA App: włączone Instant Replay lub Highlights, klipy zapisywane skrótem klawiszowym albo przez grę

## Jak to działa {#how-it-works}

Co program uruchamiający i sterownik karty graficznej zachowują o grze: statystyki Steam,
osiągnięcia, czas gry i osie czasu, oraz highlighty i klipy NVIDIA.

Żadne z tych źródeł nie wymaga, by gra współpracowała albo działała, więc trzy adaptery tutaj są zawsze włączone i zaglądają do kilku plików co kilka sekund.

#### Klipy i highlighty NVIDIA (`nvidia-highlights`) {#nvidia-highlights-and-clips-nvidia-highlights}

Co zachowuje NVIDIA App / GeForce Experience, wszystko w
`%LOCALAPPDATA%\NVIDIA Corporation\NVIDIA Overlay`:
```text
UGCTracker.json      indeks galerii: {"UGC": [{id, path, type (video,
                     image), subType (InstantReplay, Normal, ...), date
                     (UTC, gdy plik został zapisany), profileName, drsName
                     (exe), shortName, msDuration, ...}], "apps", "info"}
GallerySettings.json settings.currentDirectoryV2 (gdzie zapisywane są klipy),
                     settings.tempDirectory (highlighty czekają w
                     <temp>\Highlights\<game>, aż zostaną zapisane)
Highlights\<game>\config.json  rodzaje highlightów, które gra zarejestrowała:
                     {"highlights": {id: {significance, highlightTags,
                     name: {locale: text}}}, profileName, drsName, shortName}
```
oraz same pliki klipów, `<folder przechwytywania>\<Gra>\<Gra> yyyy.mm.dd -
hh.mm.ss.ff.DVR.mp4` (zrzuty ekranu: `<Gra> Screenshot yyyy.mm.dd - ...png`); czas w nazwie
to lokalny czas zapisania klipu. Gry obsługujące GfeSDK zapisują też swoje wywołania highlightów w
`%LOCALAPPDATA%\NVIDIA Corporation\GfeSDK\<exe>_<pid>.log`.

Co to może, a czego nie może dostarczyć: gra, która obsługuje NVIDIA Highlights
(GfeSDK), rejestruje rodzaje highlightów raz – id, np. „kill”, znaczenie, tagi,
nazwę do wyświetlenia – a potem mówi tylko „highlight <id>, od <ms> przed teraz do <ms> po teraz„. Nie ma tu pozycji, meczu ani rundy, przeciwnika, własnych danych: SDK nie ma dla nich pola. Zapisany klip dodaje tylko plik, nazwę gry, długość i czas. Zapisywane jest więc „ten rodzaj chwili, w tej grze, o tym czasie” – a miejsce tylko przez wyszukanie czasu w zapisie innego adaptera z tej samej gry (`position_at`), co ten adapter robi dla każdego zapisanego klipu.
<https://developer.nvidia.com/highlights>

Każdy adapter zapamiętuje to, co już widział, w `<data>\state\<id>.json`, więc ponowne uruchomienie nie zapisuje niczego dwa razy.

Każda sesja zachowuje też w całości to, z czego pochodzą jej wiersze (zasada konwertera 3DHeat, docs/converters.md w
repozytorium przeglądarki), w `heat.raw.parquet`: bajty pliku statystyk i jego schematu oraz blok localconfig gry
(steam-stats; plik statystyk, którego dekoder nie może odczytać, daje sesję zawierającą tylko swoje bajty),
nagłówek pliku osi czasu i każdy wpis jako JSON (steam-timeline), każdy wpis indeksu galerii klipu, definicje highlightów gry i każdą linię logu GfeSDK, także te, które nie są żądaniami highlightów (nvidia-highlights).

Ten sam moduł obsługuje też: [Steam – statystyki (platforma)](game-steam-stats.md), [Steam Timeline (platforma)](game-steam-timeline.md).

## Pozycje i osie {#positions-and-axes}

| | |
|---|---|
| Zapisane pozycje | tylko pożyczone: miejsce, które inne zapisy tej samej gry mają dla tej chwili |
| Oś pionowa | `y` |
| Jednostki | metry |
| Odbicie dla przeglądarki | brak |
| Skala jednostki (`scale`: przeglądarka mnoży przez nią pozycje) | 1 |

Te wartości trafiają do `meta.json` każdej sesji (`axes`) i, gdy sesja ma pozycje, do stopki `heat.parquet`. Dzięki temu przeglądarka 3DHeat sama obraca i skaluje wiersze – zob. [Dane](the-data.md).

## Tryb wieloosobowy {#multiplayer}

- Oznaczone jako grane online (`multiplayer`): **nie**. `games --markdown` pokazuje to jako „jednoosobowe”.
- Rodzaj `platform`: odczytuje tylko to, co gra lub platforma udostępnia (to, co zachowują Steam lub sterownik karty graficznej), więc nagrywa też w grze online; flaga decyduje tylko o tym, czy wolno kiedykolwiek czytać pamięć.
- Pamięć: **nigdy** nie jest odczytywana przez ten adapter. Tylko adaptery `memory` czytają pamięć, i nigdy dla gry oznaczonej jako grana online – zob. [Źródła i zasady](sources-and-rules.md).

## Co jest zapisywane w statystykach {#statistics-recorded}

Klucze statystyk, które kod tego adaptera ustawia po nazwie (`stats` każdej sesji w `meta.json` i tabela `stats` w `watcher.sqlite`):

`clip_seconds`, `clips`, `placed`, `screenshots`

Klucz w nawiasach klamrowych jest uzupełniany w czasie działania (`score.{team}` to jeden klucz na zespół). Klucze, które kod bierze z tabeli pól gry lub z jej własnych nazw statystyk, nie są na tej liście; sekcja „Co jest zapisywane” wyżej wymienia je.

## Kompletność {#completeness}

Watcher stosuje [zasadę konwertera 3DHeat](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md): to, co źródło zawiera, jest odczytywane lub zachowywane, nigdy nie jest pomijane. Oprócz wierszy każdy pakiet, strona, linia lub odpowiedź, którą adapter otrzyma, jest zachowana w całości w `heat.raw.parquet` sesji (kolumny `time`, `ms`, `type`, `used`, `payload`, `text`, a potem każde pole zachowane po nazwie; `used` oznacza to, co stało się też wierszami), a `selfCheck.completeness` w `meta.json` liczy każdy `type` – `lost` wynosi 0.

**Odczytane**

- każdy nowy klip i zrzut ekranu: gra, plik, rodzaj, nośnik, długość (z indeksu, a jeśli go nie ma – z nagłówka MP4), chwila z nazwy pliku, id i nazwa highlightu, jeśli gra je zarejestrowała, oraz miejsce gracza w tym momencie z zapisu innego adaptera
- żądania highlightów GfeSDK (każda linia `Posted Request HL...` oprócz wywołań konfiguracyjnych) z ich czasem

**Zachowane w surowej postaci**

- `UGC`: cały wpis klipu z indeksu galerii UGCTracker.json, każde pole, jakie zapisuje NVIDIA
- `clip_file`: dla klipu, którego indeks nie wymienia, ścieżka pliku, rozmiar, czas i folder
- `highlights_config`: plik `Highlights\<game>\config.json` gry w postaci zapisanej (znaczenie, tagi, nazwy we wszystkich językach), raz na sesję
- `gfesdk_log`: każda linia logów GfeSDK przeczytana po pierwszym uruchomieniu, `used` prawda dla żądań highlightów i fałsz dla reszty (konfiguracja, ustawienia wideo, własne komunikaty SDK)

**Niedostępne**

- same klipy i zrzuty ekranu: wideo i obrazy zostają tam, gdzie NVIDIA je zapisała; wiersze podają plik
- to, co było przed pierwszym uruchomieniem adaptera: traktowane jako już widziane, więc lata klipów nie zamieniają się naraz w sesje (`baseline`; False je zapisuje)
- `apps` i `info` z UGCTracker.json oraz GallerySettings.json: ustawienia aplikacji, a nie chwile gry; używany jest folder przechwytywania, który podają
- pozycje, rundy, przeciwnicy: GfeSDK nie ma dla nich pola

**Rozmiar**: około 1 KB na klip i kilka KB definicji oraz linii logu na uruchomienie gry: znacznie poniżej 1 MB na godzinę

## Sprawdzone {#verified}

przetestowane na prawdziwym indeksie galerii, ustawieniach, definicjach highlightów i klipach z lokalnej instalacji; linie żądań highlightów GfeSDK i id highlightów w klipach nie są jeszcze sprawdzone

## Źródło {#source}

[heat3d_watch/adapters/platform.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/platform.py)

<!-- Generated from the adapter by tools/gen_game_pages.py; change the adapter and run it again rather than editing this page. -->
