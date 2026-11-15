---
title: "EA SPORTS F1 24 (dane na żywo)"
nav_order: 15
lang: "pl"
source: game-f1-24.md
source_hash: "a189298930fc"
nav_exclude: true
search_exclude: true
---
# EA SPORTS F1 24 (dane na żywo) {#ea-sports-f1-24-live-data}

Podczas gry w EA SPORTS F1 24 watcher zapisuje dane, które sama gra wysyła na zewnątrz, dzięki czemu możesz później obejrzeć je na mapie w przeglądarce 3DHeat.

*Szczegóły techniczne: adapter `f1-24`, rodzaj [`telemetry`](sources-and-rules.md); działa, gdy działa `F1_24.exe`, i sprawdza nowe dane co 0,1 s.*

## Co jest zapisywane {#what-is-recorded}

- pozycja każdego samochodu (współrzędne XYZ świata, w metrach) 10 razy na sekundę, z nazwiskiem kierowcy, zespołem i własnym samochodem oznaczonym (`own_car` 1, z indeksu twojego samochodu), z prędkością, biegiem, gazem, hamulcem, skrętem, obrotami, DRS, odchyleniami yaw, pitch, roll (w stopniach) i przeciążeniami g
- okrążenia każdego samochodu z czasem okrążenia i pozycją w wyścigu; mety i wycofania
- zdarzenia wyścigu z gry: początek i koniec sesji, najszybsze okrążenie, kary, wyprzedzenia, kolizje, samochód bezpieczeństwa, czerwona flaga, światła startu, flaga w szachownicę, zwycięzca, cofnięcia czasu (`teleport` - gdzie był samochód, `spawn` - dokąd wrócił)
- tor, typ sesji, okrążenia i kierowcy każdej sesji
- własne okrążenia, najlepsze okrążenie, pozycja w wyścigu i na starcie, pit stopy, kary, wyprzedzenia, kolizje, dystans, prędkość maksymalna
- każdy pakiet wysłany przez grę, w całości, w `heat.raw.parquet` - także te, które nie zostały zamienione na wiersze

## Skąd pochodzą dane {#where-it-comes-from}

Telemetria UDP 127.0.0.1:20777 (Dokumenty\My Games\F1 24\hardwaresettings\hardware_settings_config.xml)

## Jak to włączyć {#how-to-switch-it-on}

W grze: Ustawienia > Ustawienia telemetrii > UDP Telemetry On, IP 127.0.0.1, port 20777 - albo `python -m heat3d_watch setup f1-24 --apply` (zmienia hardware_settings_config.xml, wcześniej robi kopię; gra musi być zamknięta). Jeśli inna aplikacja zajmuje port 20777, watcher zostawia port jej.

Wpisz polecenie w terminalu otwartym w folderze watchera (zobacz [Zanim zaczniesz](before-you-start.md)). Jeśli się nie uda, ostatnia linia powie dlaczego; [Instalacja i uruchamianie](installing-and-running.md) opisuje częste przyczyny.

`python -m heat3d_watch setup f1-24` pokazuje listę plików, które zostaną zmienione; `python -m heat3d_watch setup f1-24 --apply` zmienia je, a oryginał zachowuje jako `<plik>.heat3d-backup` (zobacz [Polecenia](commands.md#setup)). Dla każdej zmiany wypisuje `f1-24: changed: ...`, a gdy wszystko jest już włączone, `f1-24: nothing to change`.

## Jak to działa {#how-it-works}

EA SPORTS F1 23, F1 24 i F1 25: oficjalna telemetria UDP, każdy samochód na torze.

Gry wysyłają ją same (Ustawienia > Ustawienia telemetrii, albo
`Dokumenty/My Games/<F1 xx>/hardwaresettings/hardware_settings_config.xml`,
`<udp enabled="true" ip="127.0.0.1" port="20777" sendRate="20" format="2025" ...>`).
Little-endian, bez wypełnienia, nagłówek 29 bajtów w każdym pakiecie (taki sam w formatach 2023, 2024 i 2025):

```text
uint16 packetFormat, uint8 gameYear, gameMajorVersion, gameMinorVersion,
packetVersion, packetId, uint64 sessionUID, float sessionTime,
uint32 frameIdentifier, overallFrameIdentifier, uint8 playerCarIndex,
secondaryPlayerCarIndex
```

Co jest odczytywane, według identyfikatora pakietu:

```text
0 Motion        CarMotionData[22], 60 bajtów każdy: pozycja świata x y z
                (metry; Y jest w górę), prędkość świata, wektory kierunku
                przód i prawo (int16 / 32767), przeciążenia g, yaw pitch roll
1 Session       pogoda, temperatury, łączna liczba okrążeń, długość toru, typ
                sesji, id toru, ... gra sieciowa
2 Lap Data      LapData[22]: czas ostatniego okrążenia, dystans na okrążeniu,
                pozycja w wyścigu, numer bieżącego okrążenia, pit stopy, kary,
                pozycja na starcie, status kierowcy i wyniku. 50 bajtów na
                samochód w 2023; 57 w 2024 i 2025, które dodały części minut
                w różnicach czasu i pułapkę prędkości.
3 Event         czteroliterowy kod i unia szczegółów: SSTA SEND FTLP
                RTMT DRSE DRSD TMPT CHQF RCWN PENA SPTP STLG LGOT DTSV SGSV
                FLBK BUTN RDFL OVTK SCAR COLL
4 Participants  ParticipantData[22]: AI albo człowiek, kierowca, zespół, numer
                startowy, nazwa (48 bajtów w 2023 i 2024, 32 w 2025; 58, 60
                i 57 bajtów na samochód)
6 Car Telemetry CarTelemetryData[22], 60 bajtów: prędkość km/h, gaz, skręt,
                hamulec, sprzęgło, bieg, obroty, DRS ...
```

Każdy pakiet jest też zachowywany w całości, tak jak przyszedł, w surowym pliku dodatkowym sesji (`heat.raw.parquet`, `type` to nazwa pakietu - `motion`, `car_status` ... - z `format`, `packet_id`, `frame` i `session_uid`) - zarówno te odczytane powyżej, jak i te, których nic jeszcze nie czyta: 5 Car Setups, 7 Car Status, 8 Final Classification, 9 Lobby Info, 10 Car Damage, 11 Session History, 12 Tyre Sets, 13 Motion Ex, 14 Time Trial, 15 Lap Positions, każdy późniejszy id oraz pakiety w formacie, którego watcher nie czyta. Dlatego późniejszy dekoder potrzebuje tylko pliku dodatkowego.

Pozycja każdego samochodu jest w pakiecie Motion - także online, gdy sama gra ją udostępnia (tylko dane o paliwie, ERS, uszkodzeniach i zestawach opon są wstrzymywane dla graczy, których „Your Telemetry” jest ograniczona). Każdy samochód jest zapisywany około 10 razy na sekundę pod nazwą uczestnika („car N”, dopóki nazwy nie przyjdą), z zespołem po nazwie, a własny samochód gracza jest oznaczony jako `own`.

Źródła: „F1 25 UDP Specification” EA (forums.ea.com, centrum informacji o grach F1), specyfikacje F1 23 i F1 24; te same tabele w repozytorium MacManley/f1-25-udp (MIT). Pakiety w testach są budowane według tych układów.

Ten sam moduł obsługuje też: [EA SPORTS F1 23 (dane na żywo)](game-f1-23.md), [EA SPORTS F1 25 (dane na żywo)](game-f1-25.md).

## Pozycje i osie {#positions-and-axes}

| | |
|---|---|
| Zapisywane pozycje | tak |
| Oś pionowa | `y` |
| Jednostki | metry |
| Lustrzane odbicie dla przeglądarki | brak |
| Skala jednostek (`scale`: przeglądarka mnoży przez nią pozycje) | 1 |

Trafiają one do `meta.json` każdej sesji (`axes`) i, gdy sesja ma pozycje, do stopki `heat.parquet`, więc przeglądarka 3DHeat sama obraca i skaluje wiersze - zobacz [Dane](the-data.md).

## Gra wieloosobowa {#multiplayer}

- Oznaczona jako grana online (`multiplayer`): **tak**. `games --markdown` pokazuje to jako „dozwolone (czyta tylko to, co gra publikuje)”.
- Rodzaj `telemetry`: czyta tylko to, co gra lub platforma udostępnia (port UDP albo pamięć współdzielona, które gra publikuje), więc zapisuje także w grze online, a w trybie offline; flaga decyduje tylko o tym, czy wolno kiedykolwiek czytać pamięć.
- Pamięć: **nigdy** nie jest czytana przez ten adapter. Pamięć czytają tylko adaptery `memory`, i nigdy dla gry oznaczonej jako grana online - zobacz [Źródła i zasady](sources-and-rules.md).

## Zapisywane statystyki {#statistics-recorded}

Klucze statystyk, które kod tego adaptera ustawia po nazwie (`stats` każdej sesji w `meta.json` i tabela `stats` w `watcher.sqlite`):

`best_lap`, `collisions`, `distance_km`, `fastest_laps`, `finishes`, `flashbacks`, `grid_position`, `laps`, `overtaken`, `overtakes`, `penalties`, `penalty_seconds`, `pit_stops`, `race_position`, `sessions`, `top_speed_kmh`, `wins`

Klucz w nawiasach klamrowych jest uzupełniany podczas działania (`score.{team}` to jeden klucz na drużynę). Klucze, które kod bierze z tabeli pól gry albo z nazw statystyk gry, nie są na tej liście; „Co jest zapisywane” powyżej podaje je z nazwy.

## Kompletność {#completeness}

Watcher stosuje zasadę konwertera 3DHeat ([zasada konwertera](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md)): to, co zawiera źródło, jest odczytywane albo zachowywane, nigdy pomijane. Oprócz wierszy każdy pakiet, strona, linia czy odpowiedź, którą odbiera adapter, jest zachowywana w całości w `heat.raw.parquet` sesji (kolumny `time`, `ms`, `type`, `used`, `payload`, `text`, a potem pola zachowane po nazwie; `used` oznacza, co też stało się wierszami), a `selfCheck.completeness` w `meta.json` liczy każdy `type` - `lost` wynosi 0.

**Odczytywane**

- 0 Motion: pozycja i prędkość świata każdego samochodu, a teraz także yaw, pitch, roll (w stopniach, z radianów specyfikacji) oraz przeciążenia boczne, wzdłużne i pionowe g, w wierszach pozycji każdego samochodu
- 1 Session: tor, typ sesji, łączna liczba okrążeń, długość toru, online albo nie (`sessions` w meta.json)
- 2 Lap Data: czas ostatniego okrążenia, numer okrążenia, pozycja w wyścigu i na starcie, pit stopy, kary, status wyniku (okrążenia, mety, wycofania, statystyki)
- 3 Event: każdy kod oprócz BUTN jako osobny wiersz, ze szczegółami
- 4 Participants: nazwiska kierowców, zespoły, liczba aktywnych samochodów (`player` i `team` w wierszach, `drivers` w meta.json)
- 6 Car Telemetry: prędkość, bieg, gaz, hamulec, a teraz także skręt (-1..1), obroty i DRS, w wierszach pozycji każdego samochodu
- sprawdzone z opublikowanymi przez EA specyfikacjami UDP dla formatów 2023, 2024 i 2025 (rozmiary pakietów sprawdzane w testach); jeszcze nie sprawdzone z grą

**Zachowywane w całości**

- każdy pakiet w całości w `heat.raw.parquet`, `payload` to datagram, `type` to nazwa jego identyfikatora: `motion`, `session`, `lap_data`, `event`, `participants`, `car_setups`, `car_telemetry`, `car_status`, `final_classification`, `lobby_info`, `car_damage`, `session_history`, `tyre_sets`, `motion_ex`, `time_trial`, `lap_positions` (`packet <n>` dla identyfikatora, którego specyfikacje jeszcze nie podają); kolumny `format` (2023/2024/2025), `packet_id`, `frame`, `session_uid`
- `used` jest prawdziwe dla pakietów odczytanych powyżej (Motion, Session, Lap Data, Participants, Car Telemetry i kodów Event innych niż BUTN); reszta - ustawienia samochodu, stan samochodu (paliwo, ERS, mieszanka i wiek opon, flagi), wynik końcowy, lobby, uszkodzenia samochodu, historia sesji (każdy czas okrążenia i sektora każdego samochodu), zestawy opon, motion ex (zawieszenie własnego samochodu, prędkości kół, prędkość lokalna, prędkość kątowa i przyspieszenie), time trial, pozycje na okrążeniu, zdarzenia przycisków BUTN - jest zachowywana dla późniejszego dekodera
- `format <rok>`: pakiet w formacie sprzed 2023 (inny układ nagłówka), w całości; `short`: datagram krótszy niż 29-bajtowy nagłówek, w całości

**Niedostępne**

- paliwo, ERS, uszkodzenia i zestawy opon innych graczy online, gdy ich „Your Telemetry” jest ograniczona: gra wysyła dla nich zera
- pakiety wysyłane, gdy watcher nie działa albo gdy inna aplikacja zajmuje port 20777: gra nie przechowuje UDP

**Rozmiar**: przy częstotliwości wysyłania 60 Hz każdy pakiet to około 0,38 MB/s (Motion, Lap Data, Car Telemetry, Car Status i Motion Ex po 60 Hz, Session History i Tyre Sets po 20/s, Car Damage po 10/s, Session i Car Setups po 2/s) plus około 0,03 MB/s nagłówków elementów: około 1,5 GB na godzinę jazdy przed kompresją, około 0,55 GB przy domyślnych 20 Hz; zstd zmniejsza to do ułamka (puste miejsca samochodów i powtarzające się wartości dobrze się kompresują; nie zmierzone jeszcze na prawdziwej sesji)

## Sprawdzone {#verified}

przetestowane na pakietach w formatach 2023, 2024 i 2025, zbudowanych według opublikowanej przez EA specyfikacji i wysłanych przez UDP; nieprzetestowane z grą

## Źródło {#source}

[heat3d_watch/adapters/f1.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/f1.py)

<!-- Generated from the adapter by tools/gen_game_pages.py; change the adapter and run it again rather than editing this page. -->
