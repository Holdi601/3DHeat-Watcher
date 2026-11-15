---
title: "IL-2 Sturmovik: Great Battles (dane na żywo)"
nav_order: 26
lang: "pl"
source: game-il2.md
source_hash: "b6c4de7dcc14"
nav_exclude: true
search_exclude: true
---
# IL-2 Sturmovik: Great Battles (dane na żywo) {#il-2-sturmovik-great-battles-live-data}

Gdy grasz w IL-2 Sturmovik: Great Battles, watcher zapisuje dane, które sama gra wysyła na zewnątrz, dzięki czemu później możesz je obejrzeć jako statystyki i oś czasu.

*Szczegóły techniczne: adapter `il2`, rodzaj [`telemetry`](sources-and-rules.md); działa, gdy uruchomiony jest `Il-2.exe` lub `IL2Series.exe`, i sprawdza nowe dane co 0,1 s.*

## Co jest zapisywane {#what-is-recorded}

- loty: samolot, który został przejęty (spawn), i moment, w którym wyjście przestaje wysyłać dane (session_end) – bez pozycji w świecie: gra jej nie wysyła
- zrzucone bomby i wystrzelone rakiety (masa), trafienia i otrzymane obrażenia, eksplozje, serie ognia z broni – pozycje lokalne względem samolotu
- prędkość wskazywana (EAS), AGL, prędkość pionowa, g, obroty silnika raz na sekundę, wraz z każdym innym wskaźnikiem w pakiecie (ciśnienie w kolektorze, drgania silnika, stan i ciśnienie podwozia, AoA, ślizg boczny, przyspieszenie x/y/z, drgania kabiny, klapy, hamulce aerodynamiczne)
- loty, wystrzelone serie, bomby, rakiety, otrzymane trafienia, najwyższa prędkość, najwyższe g, czas lotu; w sieci tytuł serwera i nazwa pilota
- każdy pakiet telemetrii w całości w heat.raw.parquet

## Skąd pochodzą dane {#where-it-comes-from}

wyjście telemetrii gry przez UDP na 127.0.0.1:41995 ([KEY = telemetrydevice] w &lt;gra>\data\startup.cfg)

## Jak to włączyć {#how-to-switch-it-on}

python -m heat3d_watch setup il2 --apply (dodaje addrN = „127.0.0.1:41995”, enable = true), potem uruchom IL-2 ponownie

Wpisz polecenie w terminalu otwartym w folderze watchera (zob. [Zanim zaczniesz](before-you-start.md)). Jeśli się nie uda, ostatnia linia powie dlaczego; [Instalacja i uruchamianie](installing-and-running.md) opisuje częste przyczyny.

`python -m heat3d_watch setup il2` pokazuje pliki, które zostałyby zmienione; `python -m heat3d_watch setup il2 --apply` zmienia je, zachowując oryginał jako `<file>.heat3d-backup` (zob. [Polecenia](commands.md#setup)). Dla każdej zmiany drukuje `il2: changed: ...`, a gdy opcja jest już włączona, `il2: nothing to change`.

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

Ten sam moduł obsługuje też: [IL-2 Sturmovik: Great Battles (powtórki)](game-il2-tacview.md).

## Pozycje i osie {#positions-and-axes}

| | |
|---|---|
| Zapisane pozycje | nie |
| Oś pionowa | `y` |
| Jednostki | brak: telemetria nie ma pozycji w świecie |
| Odbicie dla przeglądarki | brak |
| Skala jednostki (`scale`: przeglądarka mnoży przez nią pozycje) | 1 |

Te wartości trafiają do `meta.json` każdej sesji (`axes`) i, gdy sesja ma pozycje, do stopki `heat.parquet`. Dzięki temu przeglądarka 3DHeat sama obraca i skaluje wiersze – zob. [Dane](the-data.md).

## Tryb wieloosobowy {#multiplayer}

- Oznaczona jako gra sieciowa (`multiplayer`): **tak**. `games --markdown` pokazuje to jako „allowed (reads only what the game publishes)”.
- Rodzaj `telemetry`: czyta tylko to, co gra lub platforma udostępnia (port UDP albo pamięć dzielona, które gra publikuje), więc nagrywa także w grze sieciowej, tak jak w trybie offline. Flaga decyduje tylko o tym, czy pamięć w ogóle może być czytana.
- Pamięć: **nigdy** nie jest czytana przez ten adapter. Tylko adaptery `memory` czytają pamięć, i nigdy dla gry oznaczonej jako sieciowa – zob. [Źródła i zasady](sources-and-rules.md).

## Co jest zapisywane w statystykach {#statistics-recorded}

Klucze statystyk, które kod tego adaptera ustawia po nazwie (`stats` każdej sesji w `meta.json` i tabela `stats` w `watcher.sqlite`):

`bad_packets`, `bombs_dropped`, `damage_taken`, `explosions`, `flight_time`, `hits_taken`, `max_agl_m`, `max_eas_kmh`, `max_g`, `ordnance_kg`, `rockets_fired`, `rounds_fired`, `sorties`

Klucz w nawiasach klamrowych jest uzupełniany podczas działania (`score.{team}` to jeden klucz na zespół). Klucze, które kod bierze z tabeli pól gry albo z nazw statystyk gry, nie są na tej liście; „Co jest zapisywane” wyżej wymienia je.

## Kompletność {#completeness}

Watcher stosuje [zasadę konwertera](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md) 3DHeat: to, co źródło zawiera, jest czytane albo zachowywane, nigdy pomijane. Oprócz wierszy każdy pakiet, strona, linia lub odpowiedź, którą adapter otrzyma, jest zachowana w całości w `heat.raw.parquet` sesji (kolumny `time`, `ms`, `type`, `used`, `payload`, `text`, a potem każde pole zachowane po nazwie; `used` oznacza to, co stało się też wierszami). `selfCheck.completeness` w `meta.json` liczy każdy `type`; `lost` wynosi 0.

**Odczytane**

- SET_FOCUS (samolot przejęty: lot), DROP_BOMB i ROCKET_LAUNCH (masa, pozycja lokalna), HIT i DAMAGE (pozycja lokalna, siła), EXPLOSION (pozycja lokalna, promień), GUN_FIRE (wystrzały na odpytanie) jako wiersze
- SETUP_ENG (indeks, id, pozycja lokalna, maksymalne obroty), SETUP_GUN (indeks, pozycja lokalna, masa pocisku, prędkość wylotowa) i SETUP_LGEAR (indeks, id, pozycja lokalna) jako wiersze: silniki, działka i podwozie samolotu w chwili startu lotu
- SRV_TITLE, SRV_ADDR, SRS_ADDR i CLIENT_DAT (nazwa pilota) do meta.json; koalicja z CTRL_DAT jako drużyna lotu
- wszystkie piętnaście wskaźników ze specyfikacji w wierszu `state` raz na sekundę (jedna wartość jako liczba, po jednej na silnik, nogę podwozia lub oś jako lista); najwyższa prędkość, g i AGL z każdego pakietu

**Zachowane w surowej postaci**

- każdy datagram w całości jako `payload`, pod swoim Packet_ID: `0x54000101` dla telemetrii (używany, gdy utworzył wiersz lub wpis w meta.json), każdy inny id jako on sam, datagram za krótki na pakiet jako `short`
- to, co trzyma tylko surowy plik sesji: wskaźniki między wierszami raz na sekundę (gra wysyła je z częstotliwością 50 Hz / decimation), zdarzenie SETUP krótsze niż układ ze specyfikacji, id zdarzeń, których specyfikacja nie wymienia

**Niedostępne**

- pozycja w świecie: wyjście telemetrii jej nie ma (pozycje zdarzeń są lokalne względem samolotu); adapter il2-tacview czyta pozycje z własnych nagrań Tacview gry
- inne samoloty i gracze: wyjście opisuje tylko samolot gracza

**Rozmiar**: około 8 MB na godzinę przy 10 Hz z ustawienia `setup` (decimation 5; pakiet ma ok. 160 bajtów plus ramka), 40 MB przy pełnych 50 Hz gry, przed zstd; zstd zmniejsza powtarzające się liczby zmiennoprzecinkowe do ułamka

## Sprawdzone {#verified}

przetestowane na pakietach zbudowanych wg własnej specyfikacji gry Il2_TeleOutput (rev 1.2); edycje startup.cfg testowane na kopii pliku; niesprawdzone z działającą grą

## Źródło {#source}

[heat3d_watch/adapters/il2.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/il2.py)

<!-- Generated from the adapter by tools/gen_game_pages.py; change the adapter and run it again rather than editing this page. -->
