---
title: "IL-2 Sturmovik: Great Battles (powtórki)"
nav_order: 27
lang: "pl"
source: game-il2-tacview.md
source_hash: "0bb23bddee03"
nav_exclude: true
search_exclude: true
---
# IL-2 Sturmovik: Great Battles (powtórki) {#il-2-sturmovik-great-battles-replays}

Po meczu w IL-2 Sturmovik: Great Battles watcher zamienia powtórkę zapisaną przez grę na pliki, które możesz obejrzeć na mapie w przeglądarce 3DHeat.

*Szczegóły techniczne: adapter `il2-tacview`, rodzaj [`replay`](sources-and-rules.md); działa cały czas (nie czeka na uruchomienie gry) i sprawdza nowe dane co 5 s.*

## Co jest zapisywane {#what-is-recorded}

- każdy samolot, pojazd i okręt z nagrania: pozycje raz na sekundę (metry na wschód/w górę/na północ od punktu odniesienia nagrania; szerokość, długość i wysokość jako kolumny)
- pojawienia się, zniszczenia (śmierć) i odejścia (opuszczenie), starty i lądowania, jeśli zostały nagrane
- obiekty, zniszczenia, starty, lądowania i długość na nagranie
- każda linia nagrania w całości w heat.raw.parquet, według zegara wierszy

## Skąd pochodzą dane {#where-it-comes-from}

własne nagrania Tacview z gry &lt;gra>\data\Tracks\\\*.acmi (tekst ACMI 2.x, zwykły lub spakowany zip)

## Jak to włączyć {#how-to-switch-it-on}

python -m heat3d_watch setup il2-tacview --apply (tacviewrecord = 1 w [KEY = track_record])

Wpisz polecenie w terminalu otwartym w folderze watchera (zob. [Zanim zaczniesz](before-you-start.md)). Jeśli się nie uda, ostatnia linia powie dlaczego; [Instalacja i uruchamianie](installing-and-running.md) opisuje częste przyczyny.

`python -m heat3d_watch setup il2-tacview` pokazuje pliki, które zostałyby zmienione; `python -m heat3d_watch setup il2-tacview --apply` zmienia je, zachowując oryginał jako `<file>.heat3d-backup` (zob. [Polecenia](commands.md#setup)). Dla każdej zmiany drukuje `il2-tacview: changed: ...`, a gdy opcja jest już włączona, `il2-tacview: nothing to change`.

## Jak to działa {#how-it-works}

IL-2 Sturmovik: Great Battles – wyjście telemetrii gry przez UDP oraz własne nagrania Tacview gry.

1. Telemetria („Telemetry output of IL2 v4.003”, wersja 1.2, dostarczana jako `<gra>\Doc\UDP_Output\Il2_TeleOutput.pdf`). Włączana w `<gra>\data\startup.cfg`, sekcja `[KEY = telemetrydevice]`: `addr`, `addr1`, ... = „IP[:port]” (kilka celów naraz), `decimation` (50 Hz / n), `enable`, `port`. `setup` dodaje jeden cel, 127.0.0.1:41995 (JoyPro używa 41994, domyślny port gry to 4322), i włącza wyjście. Pakiety, little-endian:

   ```text
   DWORD  Packet_ID 0x54000101
   WORD   Size
   DWORD  Tick (1/50 s)
   BYTE   Indicators_Count, then SIndicator {WORD id, BYTE n, n x 32-bit float}
   BYTE   Events_Count,     then SEvent     {WORD id, BYTE size, size bytes}
   ```

   Wskaźniki: 0 ENG_RPM, 1 ENG_MP, 2/3 drgania silnika, 4 LGEARS_STATE, 5 LGEARS_PRESS, 6 EAS (m/s), 7 AOA (rad), 8 ACCELERATION (xyz wraz z grawitacją), 9 COCKPIT_SHAKE, 10 AGL (m), 11 FLAPS, 12 AIR_BRAKES, 13 AOS (rad), 14 VERTICAL_SPEED (m/s). Zdarzenia (pakowane po 2 bajty): 0 SET_FOCUS (STRING: bajt długości + ASCII), 1 SETUP_ENG {short index, short id, float pos[3], float max_rpm}, 2 SETUP_GUN {short index, float pos[3], float projectile mass, float muzzle velocity}, 3 SETUP_LGEAR {short index, short id, float pos[3]}, 4 DROP_BOMB i 5 ROCKET_LAUNCH {float pos[3], float mass, WORD flags}, 6 HIT i 7 DAMAGE {float pos[3], float force[3]}, 8 EXPLOSION {float pos[3], float radius}, 9 GUN_FIRE {BYTE gun}, 10 SRV_ADDR, 11 SRV_TITLE, 12 SRS_ADDR (STRING), 13 CLIENT_DAT {long client, long server client, char name[32]}, 14 CTRL_DAT {long parent, short coalition}. Pozycje zdarzeń są lokalne względem samolotu gracza; strumień nie ma wcale pozycji w świecie – to więc zdarzenia i liczby, a nie trasa.

2. Nagranie Tacview: `tacviewrecord = 1` w `[KEY = track_record]` sprawia, że gra zapisuje `<gra>\data\Tracks\*.acmi` (w grze wieloosobowej decyduje serwer). Gotowy plik jest konwertowany: każdy samolot, pojazd i okręt z pozycjami, pojawieniem się i usunięciem (zniszczony lub zniknął), startami i lądowaniami, jeśli nagranie je ma. Format ACMI 2.x w tekście, zwykły lub spakowany, wg <https://www.tacview.net/documentation/acmi/en/> – linie „#t” przesuwają zegar, linie „id,Key=Value,...” ustawiają właściwości (id w zapisie szesnastkowym, przecinki zapisane jako „\\,”, końcowe „\\” kontynuuje linię), „-id” usuwa obiekt, obiekt 0 niesie globalne wartości (ReferenceLongitude/Latitude, RecordingTime, ...) i zdarzenia („Event=Destroyed\|id\|text”). T = Lon\|Lat\|Alt[\|U\|V] albo Lon\|Lat\|Alt\|Roll\|Pitch\|Yaw[\|U\|V\|Heading], długość i szerokość względem punktu odniesienia, puste pola bez zmian. Pozycje trafiają do płaskiej mapy wokół punktu odniesienia: x na wschód, y wysokość, z na północ, w metrach. Punkt odniesienia to `geo` sesji, zapisany w meta.json i w stopce tabeli, więc przeglądarka może położyć prawdziwy świat pod trasami.

Ten sam moduł obsługuje też: [IL-2 Sturmovik: Great Battles (dane na żywo)](game-il2.md).

## Pozycje i osie {#positions-and-axes}

| | |
|---|---|
| Zapisane pozycje | tak |
| Oś pionowa | `y` |
| Jednostki | metry (wschód, wysokość, północ od pierwszego odczytu) |
| Odbicie dla przeglądarki | `z` |
| Skala jednostki (`scale`: przeglądarka mnoży przez nią pozycje) | 1 |

Te wartości trafiają do `meta.json` każdej sesji (`axes`) i, gdy sesja ma pozycje, do stopki `heat.parquet`. Dzięki temu przeglądarka 3DHeat sama obraca i skaluje wiersze – zob. [Dane](the-data.md).

## Tryb wieloosobowy {#multiplayer}

- Oznaczona jako gra sieciowa (`multiplayer`): **tak**. `games --markdown` pokazuje to jako „allowed (reads only what the game publishes)”.
- Rodzaj `replay`: czyta tylko to, co gra lub platforma udostępnia (powtórki i dema, które gra zapisuje), więc nagrywa także w grze sieciowej, tak jak w trybie offline. Flaga decyduje tylko o tym, czy pamięć w ogóle może być czytana.
- Pamięć: **nigdy** nie jest czytana przez ten adapter. Tylko adaptery `memory` czytają pamięć, i nigdy dla gry oznaczonej jako sieciowa – zob. [Źródła i zasady](sources-and-rules.md).

## Co jest zapisywane w statystykach {#statistics-recorded}

Klucze statystyk, które kod tego adaptera ustawia po nazwie (`stats` każdej sesji w `meta.json` i tabela `stats` w `watcher.sqlite`):

`destroyed`, `duration_s`, `objects`, `{r.event}s`

Klucz w nawiasach klamrowych jest uzupełniany podczas działania (`score.{team}` to jeden klucz na zespół). Klucze, które kod bierze z tabeli pól gry albo z nazw statystyk gry, nie są na tej liście; „Co jest zapisywane” wyżej wymienia je.

## Kompletność {#completeness}

Watcher stosuje [zasadę konwertera](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md) 3DHeat: to, co źródło zawiera, jest czytane albo zachowywane, nigdy pomijane. Oprócz wierszy każdy pakiet, strona, linia lub odpowiedź, którą adapter otrzyma, jest zachowana w całości w `heat.raw.parquet` sesji (kolumny `time`, `ms`, `type`, `used`, `payload`, `text`, a potem każde pole zachowane po nazwie; `used` oznacza to, co stało się też wierszami). `selfCheck.completeness` w `meta.json` liczy każdy `type`; `lost` wynosi 0.

**Odczytane**

- T każdego obiektu (długość, szerokość, wysokość, roll, pitch, yaw, U, V, heading) jako pozycje raz na sekundę na obiekt, z Name, Type, Pilot, Coalition/Color, Country, Group i Parent
- pojawienia się, usunięcia (śmierć, gdy wcześniej przyszło zdarzenie Destroyed, w przeciwnym razie odejście), zdarzenia TakenOff i Landed, zdarzenia Message i Bookmark jako wiersze
- globalne ReferenceLongitude/Latitude (początek mapy), RecordingTime/ReferenceTime (kiedy), DataSource, DataRecorder i Title do meta.json

**Zachowane w surowej postaci**

- każda niepusta logiczna linia w całości jako `text` (linia kontynuowana końcowym „\\” jest łączona, tak jak czyta ją ACMI), pod swoim rodzajem: `header` (FileType, FileVersion), `comment`, `time` (#t), `remove` (-id), `global` i `event` (obiekt 0), `object` (id,Key=Value,...)
- to, co trzyma tylko surowy plik sesji: pozycje między wierszami raz na sekundę, uzbrojenie, pociski, flary, plewy i inne obiekty nierysowane jako trasy, każda inna właściwość (telemetria, np. IAS, AOA, gaz, paliwo, jeśli nagranie je ma), pozostałe globalne (Comments, Briefing, Author, Category), zdarzenia inne niż odczytywane (Timeout, LeftArea, ...)

**Niedostępne**

- nic poza tym, co zawiera nagranie; czego gra nie zapisuje w nagraniach, tego w nich nie ma

**Rozmiar**: w przybliżeniu tekst samego nagrania plus ok. 70 bajtów na linię, przed zstd: nagranie 100 MB daje ok. 150–250 MB surowych danych, które zstd zmniejsza prawie do rozmiaru spakowanego nagrania

## Sprawdzone {#verified}

przetestowane na syntetycznych plikach ACMI 2.2 (tekstowych i spakowanych); niesprawdzone na nagraniu z gry

## Źródło {#source}

[heat3d_watch/adapters/il2.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/il2.py)

<!-- Generated from the adapter by tools/gen_game_pages.py; change the adapter and run it again rather than editing this page. -->
