---
title: "Dota 2 (powtórki)"
nav_order: 12
lang: "pl"
source: game-dota-replays.md
source_hash: "958b1e1855e8"
nav_exclude: true
search_exclude: true
---
# Dota 2 (powtórki) {#dota-2-replays}

Po meczu Dota 2 watcher zamienia powtórkę zapisaną przez grę na pliki, które możesz obejrzeć na mapie w viewerze 3DHeat.

*Szczegóły techniczne: adapter `dota-replays`, rodzaj [`replay`](sources-and-rules.md); działa cały czas (nie czeka na start gry) i sprawdza nowe dane co 5 s.*

## Co jest zapisywane {#what-is-recorded}

- położenie, wysokość, zdrowie i poziom każdego bohatera, 7,5 razy na sekundę, gdy żyje
- zabójstwa i śmierci w miejscu, w którym się zdarzyły; wieże, koszary, Roshan i Tormentorzy w miejscu, w którym padły; wardy w miejscu postawienia
- pingi na mapie, rysunki na mapie i rozkazy każdego gracza (ruch, atak, czar, zakup, ...) w miejscu, na które wskazywały
- wynik i wiersz każdego gracza; wiersz zalogowanego gracza jako statystyki
- wszystko inne, co zawiera powtórka, zachowane w całości obok tabeli: każda ramka i wiadomość sieciowa, każda zmiana właściwości bytu, każdy wpis tabeli ciągów

## Skąd pochodzi {#where-it-comes-from}

powtórki, które zapisuje Dota 2: &lt;Dota>/game/dota/replays/&lt;match id>.dem (pobrane w kliencie albo przez `dota-replay <match id>`)

## Jak to włączyć {#how-to-switch-it-on}

pobierz powtórkę meczu w Dota 2 albo pobierz publiczną: `python -m heat3d_watch dota-replay <match id>`; potrzebne jest `pip install gem-dota`

Wpisz polecenie w terminalu otwartym w folderze watchera (zob. [Zanim zaczniesz](before-you-start.md)). Jeśli się nie uda, ostatnia linia powie dlaczego; [Instalacja i uruchamianie](installing-and-running.md) opisuje typowe przyczyny.

## Jak to działa {#how-it-works}

Powtórki i dema: to, co gra zapisuje z meczu, konwertowane po zakończeniu meczu.

Powtórka zawiera wszystko, co interfejs na żywo w grach wieloosobowych zatrzymuje dla siebie –
położenie każdego gracza, każde zabójstwo w miejscu, w którym się zdarzyło – i jest plikiem,
który gra zapisuje dla swoich graczy, więc jego odczyt niczego w grze nie rusza. Watcher
patrzy na foldery, do których gry je zapisują, czeka, aż nowy plik przestanie rosnąć (inaczej
gra wciąż go zapisuje), i konwertuje go w osobnym wątku, więc długa konwersja nigdy nie
wstrzymuje reszty watchera.

Gdy folder zostanie zobaczony po raz pierwszy, powtórki, które już w nim są, tylko się
odnotowuje, bez konwertowania: gracz z latami dem zostałby inaczej z watcherem zajętym przez
dobę. `python -m heat3d_watch replays <adapter> [folder]` konwertuje istniejące na żądanie.

#### Dota 2 {#dota-2}

Dota 2 zapisuje powtórki, które gracz pobierze (szczegóły meczu albo Oglądaj > Powtórki), do
`<Dota>/game/dota/replays/<match id>.dem`; Valve trzyma powtórkę każdego publicznego meczu na
swoich serwerach przez kilka tygodni, a `python -m heat3d_watch dota-replay <match id>` pobiera
jedną po jej numerze przez OpenDota. Każda jest czytana przez gem (github.com/whanyu1212/gem-dota,
MIT, `pip install gem-dota`) w osobnym procesie (`heat3d_watch/decoders/dota_replay.py`): położenie
każdego bohatera, wysokość, zdrowie, poziom, kierunek patrzenia, manę, doświadczenie, atrybuty
i przedmioty 7,5 razy na sekundę, gdy żyje; zabójstwa i śmierci w miejscu, w którym się zdarzyły;
wieże, koszary, Roshan i Tormentorzy w miejscu, w którym padły; każdy ward w miejscu postawienia
i w miejscu, w którym się skończył; wpisy dziennika walki dotyczące bohaterów (obrażenia,
leczenie, zdolności, przedmioty, zakupy, runy, złoto, doświadczenie, modyfikatory); oraz pingi na
mapie, rysunki na mapie i rozkazy każdego gracza – do `dota/<match>.parquet`; każda inna jednostka
(stworzenia, przywołania, iluzje, kurierzy, budynki) raz na sekundę do `<match>.units.parquet`;
cały dziennik walki do `<match>.combatlog.parquet`; a mecz, czat, draft, wszystko inne, co wyciągnie
parser, oraz zapis końca meczu z gry do `<match>.match.json`, w folderze sesji. Wszystko inne, co
zawiera powtórka, jest zachowane w całości obok nich (zasada konwertera 3DHeat): każda ramka
i wiadomość sieciowa w `<match>.packets.parquet`, każda zmiana właściwości bytu w
`<match>.entities.parquet`, każdy wpis tabeli ciągów w `<match>.strings.parquet`, policzone w
`selfCheck.completeness` dokumentu meczu. Położenia są w jednostkach świata Dota (te same, które
raportuje game-state integration). Wiersz wynikowy zalogowanego gracza staje się statystykami sesji:
zabójstwa, śmierci, asysty, ostatnie trafienia, odmowy, wartość netto, GPM, XPM, obrażenia w
bohaterach, wardy i to, czy mecz wygrano. Nowa łatka Dota może zmienić byty w powtórce, zanim gem
za nią nadąży; powtórka, której gem nie umie przeczytać do końca, jest konwertowana tak daleko, jak
się da, i oznaczana `incomplete` w swoim podsumowaniu.

Ten sam moduł obsługuje także: [Counter-Strike 2 (powtórki)](game-cs2-demos.md), [osu! (powtórki)](game-osu-replays.md), [Squad (powtórki)](game-squad-demos.md), [War Thunder (powtórki)](game-warthunder-replays.md), [World of Tanks (powtórki)](game-wot-replays.md), [World of Warships (powtórki)](game-wows-replays.md).

## Pozycje i osie {#positions-and-axes}

| | |
|---|---|
| Zapisywane pozycje | tak |
| Oś w górę | `z` |
| Jednostki | jednostki świata Dota (jednostki Hammera; mapa ma około 16400 w poprzek) |
| Odbicie dla viewera | `y` |
| Skala jednostki (`scale`: viewer mnoży przez nią pozycje) | 1 |

Trafiają one do `meta.json` każdej sesji (`axes`) i, gdy sesja ma pozycje, do stopki `heat.parquet`, więc viewer 3DHeat sam obraca i skaluje wiersze – zob. [Dane](the-data.md).

## Gra wieloosobowa {#multiplayer}

- Oznaczona jako grana online (`multiplayer`): **tak**. `games --markdown` pokazuje to jako „allowed (reads only what the game publishes)”.
- Rodzaj `replay`: czyta tylko to, co gra lub platforma udostępnia (powtórki i dema, które gra zapisuje), więc działa także w grze online; flaga decyduje tylko o tym, czy pamięć może kiedykolwiek być czytana.
- Pamięć: **nigdy** nie jest czytana przez ten adapter. Tylko adaptery `memory` czytają pamięć i nigdy dla gry oznaczonej jako grana online – zob. [Źródła i zasady](sources-and-rules.md).

## Zapisywane statystyki {#statistics-recorded}

Klucze statystyk, które kod tego adaptera ustawia po nazwie (`stats` każdej sesji w `meta.json` i tabela `stats` w `watcher.sqlite`):

`duration`, `hero`, `score.{team}`, `team`, `won`

Klucz w nawiasach klamrowych jest uzupełniany podczas działania (`score.{team}` to jeden klucz na drużynę). Klucze, które kod bierze z tabeli pól gry albo z jej własnych nazw statystyk, nie są na tej liście; „Co jest zapisywane” wyżej je wymienia.

## Kompletność {#completeness}

Konwerter stosuje [zasadę konwertera](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md) 3DHeat: to, co zawiera powtórka, jest czytane lub zachowywane, nigdy pomijane. Oprócz tabeli wszystko, co zawiera powtórka, jest zachowane w całości w sidecarach obok niej, w folderze `dota/` sesji – `<match>.packets.parquet`, `<match>.entities.parquet`, `<match>.strings.parquet` (kolumny `time`, `tick`, `type`, `name`, `entity`, `decoded`, `payload`, tam gdzie mają zastosowanie) – a `selfCheck.completeness` dokumentu meczu (`<match>.match.json`) liczy każdy `type` – `lost` to 0.

**Odczytane**

- tabela (`dota/<match>.parquet`): położenie, wysokość, zdrowie, poziom, kierunek patrzenia, mana, doświadczenie, atrybuty, pancerz, prędkość, obrażenia, przedmioty i kursor gracza 7,5 razy na sekundę; zabójstwa, śmierci, cele, wardy, wpisy dziennika walki dotyczące bohaterów; pingi na mapie (`ping`, DOTA_UM_LocationPing), rysunki na mapie (`map_line`, DOTA_UM_MapLine) i każdy rozkaz jednostki (`order`, DOTA_UM_SpectatorPlayerUnitOrders: `other` – typ rozkazu, `value` – id zdolności lub przedmiotu, `text` – klasa celu; w punkcie, do którego wydano rozkaz, a w przeciwnym razie w bohaterze)
- `<match>.units.parquet`: każda inna jednostka raz na sekundę; `<match>.combatlog.parquet`: cały dziennik walki tak, jak czyta go gem, każde pole
- dokument meczu: wszystko, co wyciąga gem, oraz w całości zapisy samej powtórki – `fileHeader` (DEM_FileHeader), `fileInfo` (DEM_FileInfo: długość odtwarzania, nazwa, bohater, Steam id i drużyna każdego gracza), `matchDetails` (DOTA_UM_MatchDetails: koncowy wynik z serwera koordynującego gry, liczby każdego gracza, przedmioty, obrażenia według typu, wybory i bany) oraz `matchMetadata` (DOTA_UM_MatchMetadata)
- `selfCheck.crossCheck`: zabójstwa, śmierci, asysty, poziom, ostatnie trafienia i odmowy odczytane ze strumienia porównane z `matchDetails`, dla każdego gracza

**Zachowane surowo**

- `<match>.packets.parquet`: każda ramka, która nie jest pakietem (`type` `frame <n>`), i każda wiadomość sieciowa (`message <n>`, nazwa Valve), w całości w `payload`, w kolejności pliku (`seq`, `frame`), a `decoded` to protobuf jako JSON (pole bajtowe jako jego długość); zdekodowany jest każdy typ wiadomości: svc_PacketEntities (strumień bytów), DOTA_UM_SpectatorPlayerUnitOrders, UM_ParticleManager, wiadomości dziennika walki, GE_SosStartSoundEvent, DOTA_UM_TE_\* (pociski, animacje, krew), DOTA_UM_OverheadEvent, DOTA_UM_UnitEvent, svc_UpdateStringTable, net_Tick, ...; tablice wysyłania, lista klas i informacje o serwerze, których potrzebuje późniejszy dekoder bytów, są wśród nich
- `<match>.entities.parquet`: każda właściwość każdego bytu za każdym razem, gdy się zmieniła (`type` – właściwość, `name` – klasa, `entity` – jego indeks; `value`, `vector` albo `decoded`), jego pełny stan przy utworzeniu oraz każde utworzenie, wejście, wyjście i usunięcie – miliony wierszy na cały mecz
- `<match>.strings.parquet`: każdy wpis tabeli ciągów z każdej aktualizacji i każdej pełnej migawki, wartość w całości; `userinfo`, `ActiveModifiers` i `EconItems` zdekodowane z ich protobufów
- `selfCheck.completeness` w dokumencie meczu liczy ramki i wiadomości według nazw Valve, wpisy dziennika walki (`combatlog <type>`), zdarzenia gry (`gameevent <name>`), wpisy tabel ciągów (`stringtable <name>`) i aktualizacje bytów (`entity <class>`); kilka z nich jest zachowanych tylko surowo (pełne migawki bytów, które gem pomija, bo odbudowuje je z delt, oraz wpisy tabel, których wartości nic nie czyta), `lost` 0

**Niedostępne**

- głos: powtórka ma ustawienia głosu, ale nie dane głosowe
- nazwy kryjące się za haszami i id: dźwięki i cząsteczki są nazwane haszami plików gry, zdolności – id; powtórka nie niesie nazw (przedmioty są nazwane przez katalog gema tam, gdzie go ma)
- wszystko, co znali tylko klienci graczy (ich kamera, ich ekran), ponad to, co nadawał serwer; kursor i każdy rozkaz są w danych

**Rozmiar**: sidecary razem są nieco większe od samej powtórki, najbardziej pakiety i byty; cały mecz zajmuje minutę lub dwie w jednym procesie

## Sprawdzone {#verified}

sprawdzone na publicznej powtórce meczu: zabójstwa, śmierci, asysty, poziom, ostatnie trafienia i odmowy zgadzają się z zapisem końca meczu z gry dla wszystkich dziesięciu graczy; każda wiadomość w sidecarze pakietów serializuje się ponownie co do bajta; tabela i statystyki przez testy na syntetycznych danych

## Źródło {#source}

[heat3d_watch/adapters/replays.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/replays.py)

<!-- Generated from the adapter by tools/gen_game_pages.py; change the adapter and run it again rather than editing this page. -->
