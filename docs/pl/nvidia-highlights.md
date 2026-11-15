---
title: NVIDIA Highlights
nav_order: 8
lang: "pl"
source: nvidia-highlights.md
source_hash: "a3b769ab065c"
nav_exclude: true
search_exclude: true
---
# NVIDIA Highlights {#nvidia-highlights}

Niektóre gry proszą sterownik karty graficznej NVIDIA, by zapisał krótki film, gdy coś się wydarzy, na przykład zabójstwo. Watcher notuje każdy taki moment i, jeśli może, umieszcza go na mapie w miejscu, w którym się zdarzył.

Adapter `nvidia-highlights` zapisuje klipy, highlighty i zrzuty ekranu, które zapisuje aplikacja NVIDIA App (albo GeForce Experience), i nadaje każdemu z nich miejsce na mapie, jeśli to możliwe. Ta strona wyjaśnia, co NVIDIA Highlights może dostarczyć, a czego nie może, które pliki czyta watcher i jak highlight dostaje pozycję. Wygenerowana strona adaptera to [NVIDIA highlights (platforma)](game-nvidia-highlights.md).

## Co NVIDIA Highlights może, a czego nie może dostarczyć {#what-nvidia-highlights-can-and-cannot-deliver}

Gra, która obsługuje NVIDIA Highlights, rozmawia z aplikacją NVIDIA App przez GfeSDK firmy NVIDIA. SDK przenosi tylko dwa rodzaje wiadomości:

1. **Raz, na starcie**: rodzaje highlightów, których gra będzie używać - identyfikator (na przykład `kill`), znaczenie, tagi i nazwę wyświetlaną w każdym języku. Aplikacja NVIDIA App zapisuje je dla każdej gry.
2. **W chwili gry**: "highlight `<id>`, od `<ms>` przed teraz do `<ms>` po teraz". To cała wiadomość: identyfikator rodzaju zarejestrowanego przez grę i dwa przesunięcia czasu, które mówią aplikacji NVIDIA App, jaki fragment jej przewijanego nagrania zachować.

SDK **nie ma pola na nic innego**: żadnej pozycji, meczu ani rundy, przeciwnika, broni, wyniku ani żadnych własnych danych. Gra nie może wpisać pozycji do highlightu, nawet gdyby chciała. Gdy klip jest zapisywany, aplikacja NVIDIA App dodaje plik, nazwę gry, długość i czas.

Highlight może więc powiedzieć tylko: „taki rodzaj momentu, w tej grze, o tej porze”. Wszystko więcej musi pochodzić skądś indziej.

## Co czyta watcher {#what-the-watcher-reads}

Wszystko jest czytane z plików, które aplikacja NVIDIA App zapisuje dla swojej galerii. Nic nie rozmawia ze sterownikiem ani z aplikacją. Folder nakładki NVIDIA to `%LOCALAPPDATA%\NVIDIA Corporation\NVIDIA Overlay`.

| Plik | Co z niego bierzemy |
|---|---|
| `UGCTracker.json` | indeks galerii: każdy klip i zrzut z jego ścieżką, typem (wideo, obraz), podtypem (`InstantReplay`, ...), datą, nazwą profilu gry, plikiem wykonywalnym i krótką nazwą, oraz długością (`msDuration`) |
| `GallerySettings.json` | `settings.currentDirectoryV2`, folder nagrań, i `settings.tempDirectory`, gdzie czekają highlighty (`<temp>\Highlights\<gra>`), aż zostaną zapisane |
| `Highlights\<gra>\config.json` | rodzaje highlightów, które każda gra zarejestrowała: identyfikator i angielską nazwę wyświetlaną (albo identyfikator, gdy gra nie podała nazwy) |
| folder nagrań (domyślnie `%USERPROFILE%\Videos\NVIDIA`) i `<temp>\Highlights` | same pliki klipów i zrzutów (`.mp4`, `.mkv`, `.mov`, `.png`, `.jpg`, `.jpeg`), po jednym folderze na grę |
| `%LOCALAPPDATA%\NVIDIA Corporation\GfeSDK\<exe>_<pid>.log` | żądania, które zapisują gry korzystające z GfeSDK - linie `Posted Request HL...` - dzięki czemu highlight, o który gra poprosiła, zostaje zapisany nawet wtedy, gdy klip nie został zachowany. Żądania konfiguracyjne (`HLConfigure`, `HLGetConfig`, `HLGetUserSettings`, `HLSetDefaultLocale`) są pomijane. |

Dla każdej nowej pozycji watcher zapisuje jeden wiersz: `highlight` dla wideo, `screenshot` dla obrazu albo `highlight_request` dla linii z logu GfeSDK. Jego pola:

| Pole | Co to jest |
|---|---|
| `ms` | moment: czas z nazwy pliku (`<Gra> 2026.05.01 - 20.31.28.115.DVR.mp4`, czas lokalny zapisania klipu), w przeciwnym razie data z indeksu, w ostateczności czas modyfikacji pliku |
| `game` | nazwa profilu NVIDIA, nazwa folderu albo nazwa gry z nazwy pliku |
| `clip`, `media` | ścieżka pliku; `video`, `image` albo `file` |
| `kind` | `InstantReplay`, `Screenshot`, `Highlight` (z tymczasowego folderu highlightów) albo podtyp z indeksu |
| `duration_s`, `clip_start_ms` | długość z indeksu albo z nagłówka samego wideo (`moov/mvhd`, znalezionego bez czytania wideo); moment, w którym zaczyna się klip |
| `highlight_id`, `highlight_name` | rodzaj highlightu, gdy coś go nazywa (zobacz niżej) |
| `exe` | plik wykonywalny gry, z indeksu |
| `x`, `y`, `z`, `session`, `position_from`, `position_lag_ms` | pożyczona pozycja, gdy została znaleziona (zobacz niżej) |

Statystyki sesji to `clips`, `screenshots`, `clip_seconds` i `placed` (pozycje, które dostały miejsce).

**Identyfikator highlightu** nie jest zapisany w żadnym udokumentowanym miejscu. Adapter próbuje dwóch nieudokumentowanych sposobów: pola wpisu galerii, którego nazwa zawiera „highlight”, oraz - tylko dla plików w tymczasowym folderze highlightów - jednego z zarejestrowanych identyfikatorów gry (co najmniej 4 znaki), który występuje w nazwie pliku. Zapisany klip nosi nazwę gry, która przypadkiem może zawierać identyfikator, np. „kill”, więc jego nazwa nie jest przeszukiwana. Te dwa sposoby nie zostały jeszcze zauważone działające na prawdziwym komputerze: nie wystąpił klip z identyfikatorem highlightu ani linia żądania GfeSDK w miejscu, gdzie adapter był testowany. Indeks galerii, ustawienia, definicje highlightów i klipy zostały sprawdzone na prawdziwych plikach.

### Kiedy pozycje są zapisywane {#when-items-are-recorded}

- Klip wciąż jest zapisywany przez chwilę po naciśnięciu klawisza. Adapter czeka, aż plik ma ten sam rozmiar i czas przy dwóch sprawdzeniach (co 10 s) i ma co najmniej 5 s.
- Za pierwszym razem, gdy adapter działa, wszystko, co już jest w galerii i logach, jest tylko zauważane, a nie zapisywane, aby lata starych klipów nie zalały statystyk. To, co zobaczył, zapisuje się w `<data>\state\nvidia-highlights.json`, więc po ponownym uruchomieniu nic nie zostanie zapisane dwa razy.
- Pozycje są grupowane w jedną sesję na grę. Sesja gry zamyka się po 30 minutach bez nowej pozycji i kończy się w swoim ostatnim momencie, a nie wtedy, gdy gra się zamknęła. Momenty oddalone o więcej niż 30 minut trafiają do osobnych sesji.

## Jak highlight dostaje pozycję {#how-a-highlight-gets-a-position}

Sam highlight nie ma miejsca. Adapter szuka tego momentu w innych nagraniach, które watcher zrobił z tej samej gry w tym samym czasie:

1. **Ta sama gra**: foldery sesji w `<data>\sessions\`, których nazwa gry pasuje do nazwy gry highlightu. Nazwy są porównywane małymi literami, tylko litery i cyfry. Pasują, gdy są równe albo gdy krótsza ma co najmniej 5 znaków i zawiera się w dłuższej (`Counter-Strike 2` i `Counter-Strike-2`).
2. **Ten sam czas**: sesje, których początek i koniec (z `meta.json`, z sekundą luzu na obu końcach) obejmują ten moment. Sesje, które zakończyły się bez pozycji, oraz sesje samego adaptera są pomijane.
3. **Własny wiersz gracza**: w jego `events.jsonl` najnowszy z własnych wierszy gracza z pozycją, nie późniejszy niż moment i nie wcześniejszy niż 5 sekund przed nim. Wiersz jest własny, gdy jego źródło tak mówi: `"player": "me"`, albo `"own_car": 1` (gry wyścigowe, które zapisują każdy samochód po kierowcy), albo `player` równy `player` z `meta.json` sesji (nazwa, jaką źródło podaje dla gracza). Zobacz [Własne wiersze gracza](the-data.md#the-players-own-rows).

Gdy wiersz zostanie znaleziony, highlight dostaje `x`, `y`, `z`, swoją `session` (albo nazwę folderu), `position_from` (folder, z którego pochodzi) i `position_lag_ms` (jak długo przed momentem był ten wiersz). Sesja highlightu przejmuje osie tego nagrania, więc jest rysowana tak samo. Gdy nie znaleziono wiersza, highlight zostaje momentem na osi czasu bez miejsca.

Rzeczy, które warto wiedzieć o pożyczonej pozycji:

- **To miejsce, w którym byłeś, gdy klip został zapisany**, a nie miejsce, w którym zaczęła się akcja. Moment to czas zapisania z nazwy pliku, który dla Instant Replay jest jego końcem. `clip_start_ms` mówi, kiedy klip się zaczyna.
- **Inny adapter musiał w tym czasie nagrywać tę samą grę.** Te, które oznaczają własne wiersze gracza i mogą więc umieścić highlight: stan gry Counter-Strike 2 i Dota 2, Forza, gry Assetto Corsa, EA SPORTS WRC, DiRT Rally 2.0, Richard Burns Rally, BeamNG.drive, Euro Truck Simulator 2, American Truck Simulator, DCS World, X-Plane, Microsoft Flight Simulator, War Thunder, Minecraft oraz profile pamięci (jako `me`); F1 23/24/25, RaceRoom, Automobilista 2 i Project CARS 2 (wiersze twojego samochodu mają `own_car` 1, według indeksu samochodu gracza w grze, jego własnego slotu albo oglądanego uczestnika); Elite Dangerous (nazwa dowódcy, w `meta.json` jako `player`, bo dziennik zawsze należy do gracza).
- **Powtórka jest konwertowana po meczu**, więc może umieścić tylko klip, który jest szukany po konwersji: klip dostaje miejsce, gdy jest nagrywany, a powtórka zapisana później nie jest już oglądana ponownie. Powtórki League of Legends nazywają twoje wiersze po Riot ID z ustawień i, z kluczem Riot API, dają im czas ścienny z osi czasu meczu, więc wtedy są znajdowane. Demo CS2 nie może w ogóle umieścić highlightu: jego pozycje są w tabeli konwertera, a nie w `events.jsonl`, a demo ma ticki gry, ale nie czas ścienny, do którego można dopasować moment klipu.
- W Rocket League jedyne wiersze z miejscem to zdarzenia z piłką. Uderzenie piłki przez ciebie jest twoim wierszem, więc highlight może dostać miejsce tam, gdzie ostatnio uderzyłeś piłkę.
- Gry bez żadnego źródła pozycji (Overwatch 2, Call of Duty, Hunt: Showdown, ...) zachowują swoje highlighty jako oś czasu momentów.

## Dlaczego pamięć nie może dać pozycji w grze wieloosobowej {#why-memory-cannot-give-a-position-in-multiplayer}

Drugim sposobem na pozycję byłoby odczytanie jej z pamięci. Żaden z nich nie działa:

- **Pamięć NVIDIA nie ma pozycji.** Aplikacja NVIDIA App dostaje to, co przenosi GfeSDK - identyfikator highlightu i dwa przesunięcia czasu - plus wideo, które nagrywa. Nie ma nigdzie po stronie NVIDIA pozycji do odczytania. (Watcher i tak nie czyta pamięci NVIDIA; czyta pliki wymienione wyżej.)
- **Pamięć gry jest nietykalna w grze wieloosobowej.** Pozycja jest w procesie gry, ale watcher nigdy nie czyta pamięci gry wieloosobowej: adapter `memory` dla gry oznaczonej jako grana online jest odrzucany, zanim cokolwiek zostanie otwarte (zobacz [Czytanie pamięci](memory-reading.md)). Gry wieloosobowe działają z systemami anty-cheat (Easy Anti-Cheat, BattlEye, Vanguard, ...), które traktują inny program otwierający proces gry jako oszustwo, co może skutkować zbanowaniem konta. Odczyt stanu gry z zewnątrz jest też zakazany przez regulaminy gier. Highlight w grze wieloosobowej dostaje więc miejsce tylko z tego, co gra publikuje: jej interfejsu stanu gry albo telemetrii, zapisanych przez inny adapter w tym samym czasie.
