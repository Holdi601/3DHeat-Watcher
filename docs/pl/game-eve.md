---
title: "EVE Online (pliki dziennika)"
nav_order: 20
lang: "pl"
source: game-eve.md
source_hash: "a5ab6c312c86"
nav_exclude: true
search_exclude: true
---
# EVE Online (pliki dziennika) {#eve-online-log-files}

Gdy grasz w EVE Online, watcher odczytuje pliki, które zapisuje gra, i zachowuje to, co się wydarzyło, dzięki czemu później możesz to obejrzeć jako statystyki i oś czasu.

*Szczegóły techniczne: adapter `eve`, rodzaj [`log`](sources-and-rules.md); działa, gdy uruchomiony jest `exefile.exe`, i sprawdza nowe dane co 0,5 s.*

## Co jest zapisywane {#what-is-recorded}

- obrażenia zadane i otrzymane wraz z drugim statkiem, pilotem, tikerem korporacji, bronią i jakością trafienia
- chybienia zadane i otrzymane
- nagrody za zabójstwa (zabójstwa NPC) z ISK
- skoki między systemami
- każda linia dziennika gry i czatu w całości w `heat.raw.parquet`
- obrażenia zadane i otrzymane, trafienia, zabójstwa nagradzane i ISK, skoki

## Skąd pochodzą dane {#where-it-comes-from}

%USERPROFILE%\Documents\EVE\logs\Gamelogs\\\*.txt oraz leżące obok nich Chatlogs\\\*.txt (każdy plik zapisany od startu klienta)

## Jak to włączyć {#how-to-switch-it-on}

Nic nie trzeba włączać: watcher odczytuje źródło tak, jak udostępnia je gra lub platforma.

## Jak to działa {#how-it-works}

EVE Online: dzienniki gry klienta, `Documents\EVE\logs\Gamelogs\*.txt`.

Klient zapisuje jeden plik na postać przy każdym logowaniu,
`<yyyymmdd>_<hhmmss>[_<id postaci>].txt`; zapisywanie do pliku jest domyślnie włączone. Kilka
uruchomionych obok siebie klientów zapisuje każdy własny, więc śledzony jest każdy plik zapisany od
startu gry. Nagłówek i linie (czas EVE to UTC):

```text
------------------------------------------------------------
  Gamelog
  Listener: Character Name
  Session Started: 2024.07.02 19:41:40
------------------------------------------------------------
[ 2024.07.02 20:31:28 ] (combat) <color=0xff00ffff><b>200</b> <color=0x77ffffff><font size=10>to</font>
    <b><color=0xffffffff>Pilot[TICK](../Ship)</b><font size=10><color=0x77ffffff> - Weapon - Penetrates
[ 2024.06.25 15:20:01 ] (combat) <color=0xffcc0000><b>375</b> ... from ... - Weapon - Hits
[ 2024.06.25 15:21:00 ] (bounty) <font size=12><b><color=0xff00aa00>15,000 ISK</b> added to next bounty payout
[ 2024.06.25 15:30:00 ] (None) Jumping from System A to System B
```

(linia combat to jedna linia w pliku). Znaczniki formatowania są usuwane przed
dopasowaniem. Plik przez lata był w UTF-8 i UTF-16; czytane są oba.
Format nie jest udokumentowany przez CCP; to zwykły tekstowy dziennik klienta, czytany tak, jak czytają go
społecznościowe narzędzia do logów walk (np. <https://docs.rs/crate/eve-log-parser>).
Brak pozycji.

Obok, `Documents\EVE\logs\Chatlogs\<channel>_<yyyymmdd>_<hhmmss>[_<id>].txt`:
jeden plik na kanał czatu na logowanie (gdy zapis czatu jest włączony, co jest domyślne w kliencie),
UTF-16, nagłówek z nazwą kanału i słuchacza, a potem
`[ yyyy.mm.dd hh:mm:ss ] Sender > message`.

Każda linia obu plików jest zachowana w całości w surowym pliku pomocniczym sesji (zasada konwertera 3DHeat):
linia dziennika gry pod swoim kanałem w nawiasach (`combat`,
`notify`, `bounty`, `None`, ...), linia czatu jako `chat` z kanałem, a
linie nagłówka jako `gamelog header` / `chatlog header`.

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

`bad_lines`, `bounty_isk`, `bounty_kills`, `damage_dealt`, `damage_received`, `hits_dealt`, `hits_received`, `jumps`, `misses_dealt`, `misses_received`

Klucz w nawiasach klamrowych jest uzupełniany w czasie działania (`score.{team}` to jeden klucz na zespół). Klucze, które kod bierze z tabeli pól gry lub z jej własnych nazw statystyk, nie są na tej liście; sekcja „Co jest zapisywane” wyżej wymienia je.

## Kompletność {#completeness}

Watcher stosuje [zasadę konwertera 3DHeat](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md): to, co źródło zawiera, jest odczytywane lub zachowywane, nigdy nie jest pomijane. Oprócz wierszy każdy pakiet, strona, linia lub odpowiedź, którą adapter otrzyma, jest zachowana w całości w `heat.raw.parquet` sesji (kolumny `time`, `ms`, `type`, `used`, `payload`, `text`, a potem każde pole zachowane po nazwie; `used` oznacza to, co stało się też wierszami), a `selfCheck.completeness` w `meta.json` liczy każdy `type` – `lost` wynosi 0.

**Odczytane**

- trafienia `(combat)` zadane i otrzymane z gamelogu (kwota, drugi pilot, tiker korporacji, statek, broń, jakość trafienia) oraz chybienia w obu kierunkach
- wypłaty `(bounty)` z ISK oraz linie `Jumping from A to B`
- `Listener` z nagłówka gamelogu: czyj to dziennik

**Zachowane w surowej postaci**

- każda linia gamelogu w całości, `type` = jej kanał w nawiasach (`combat`, `notify`, `info`, `bounty`, `mining`, `question`, `hint`, `warning`, `None`, ...), z `file` i `listener`; `used` tam, gdzie stała się wierszem; linie nagłówka jako `gamelog header`
- każda linia chatlogu w całości, `type` `chat`, z `channel`, `listener` i `file` (Local, korporacja, flota, kanały prywatne, powiadomienia `EVE System`, na przykład zmiana kanału Local przy skoku); linie nagłówka jako `chatlog header`. Jeszcze nie zamieniane na wiersze
- znaczniki formatowania (`<color>`, `<b>`, `<font>`) zostają w surowym tekście; wiersze mają je usunięte

**Niedostępne**

- pozycje: klient nie zapisuje ich w dziennikach
- walki innych pilotów: gamelog to dziennik słuchacza
- dzienniki wcześniejszych logowań: każde logowanie zapisuje nowe pliki; te starsze niż ten przebieg klienta nie są czytane ponownie
- czat, gdy gracz wyłączył zapis czatu w ustawieniach klienta
- pliki pamięci podręcznej i ustawień klienta: to nie dzienniki i nie są udokumentowane

**Rozmiar**: gamelog to 0,1-2 MB na godzinę (najwięcej podczas walki); chatlogi zależą od otwartych kanałów – zajęty kanał Local lub flota 0,5-3 MB na godzinę; zstd w `heat.raw.parquet` zmniejsza to mniej więcej dziesięciokrotnie

## Sprawdzone {#verified}

przetestowane na syntetycznych liniach gamelogu w formacie opublikowanym przez społecznościowe parsery; nie przetestowane w grze

## Źródło {#source}

[heat3d_watch/adapters/eve.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/eve.py)

<!-- Generated from the adapter by tools/gen_game_pages.py; change the adapter and run it again rather than editing this page. -->
