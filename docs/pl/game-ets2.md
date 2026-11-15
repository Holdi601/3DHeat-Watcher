---
title: "Euro Truck Simulator 2 (dane na żywo)"
nav_order: 19
lang: "pl"
source: game-ets2.md
source_hash: "537f0daeedbf"
nav_exclude: true
search_exclude: true
---
# Euro Truck Simulator 2 (dane na żywo) {#euro-truck-simulator-2-live-data}

Gdy grasz w Euro Truck Simulator 2, watcher zapisuje dane, które sama gra wysyła na zewnątrz, dzięki czemu później możesz je obejrzeć na mapie w przeglądarce 3DHeat.

*Szczegóły techniczne: adapter `ets2`, rodzaj [`telemetry`](sources-and-rules.md); działa, gdy uruchomiony jest `eurotrucks2.exe`, i sprawdza nowe dane co 0,1 s.*

## Co jest zapisywane {#what-is-recorded}

- pozycja ciężarówki w świecie (x na wschód, y w górę, z na południe, m) 10 razy na sekundę podczas jazdy, co 5 s podczas postoju; kierunek, prędkość, przebieg
- rozpoczęte zlecenia (ładunek, skąd, dokąd), dostarczone (przychód, XP, km), anulowane; mandaty, opłaty drogowe, promy, pociągi, tankowania
- promy, pociągi i wczytane zapisy przerywają trasę (teleport, spawn)
- dystans, prędkość maksymalna, dostawy, przychód, XP, mandaty
- cała pamięć współdzielona wtyczki w `heat.raw.parquet`, za każdym razem, gdy się zmieni

## Skąd pochodzą dane {#where-it-comes-from}

pamięć współdzielona Local\SCSTelemetry zapisywana przez wtyczkę RenCloud scs-sdk-plugin (wersja 12) w &lt;game>\bin\win_x64\plugins

## Jak to włączyć {#how-to-switch-it-on}

zainstaluj scs-telemetry.dll (wersja 12) z github.com/RenCloud/scs-sdk-plugin do &lt;game>\bin\win_x64\plugins; gra pyta przy każdym uruchomieniu o zgodę na SDK

## Jak to działa {#how-it-works}

Euro Truck Simulator 2 i American Truck Simulator: telemetryczny SDK SCS, przez wtyczkę RenCloud.

SCS publikuje telemetryczny SDK (<https://modding.scssoft.com/wiki/Documentation/Engine/SDK/Telemetry>)
dla wtyczek, które gracz umieszcza w `<game>\bin\win_x64\plugins\`. Sama gra
niczego nie publikuje; powszechnie używana wtyczka z <https://github.com/RenCloud/scs-sdk-plugin>
(MIT) kopiuje kanały SDK do pamięci współdzielonej `Local\SCSTelemetry`
(32 KiB), o układzie opisanym w `scs-telemetry/inc/scs-telemetry-common.hpp`. Odczytuje
wersję 12 tego układu (PLUGIN_REVID 12) i nic poza nią: wtyczka zapisuje swoją wersję
pod przesunięciem 40, a każda inna wersja jest zostawiona nieodczytana, zamiast
być odczytana błędnie. Używane przesunięcia (strefy według nagłówka; wyrównanie naturalne):

```text
   0  bool sdkActive          4  bool paused
  40  u32  telemetry_plugin_revision, version_major, version_minor, game (1 ETS2, 2 ATS)
  64  u32  common_ui.time_abs (in-game minutes)
 504  i32  truck_i.gear
 640  i32  gameplay_i.jobDeliveredEarnedXp
 948  f32  truck_f.speed (m/s); 952 engineRpm; 1056 truckOdometer (km)
1460  f32  gameplay_f.jobDeliveredDistanceKm
2200  f64  truck_dp.coordinateX/Y/Z (m), rotationX/Y/Z (heading, pitch, roll in turns, 0..1)
2300  char[64] config_s: truckBrand +64, truckName +192, cargo +320, cityDst +448, compDst +576,
      citySrc +704, compSrc +832; 3436 gameplay_s.fineOffence[32]
4200  i64  gameplay_ll: jobCancelledPenalty, jobDeliveredRevenue, fineAmount, tollgatePayAmount,
      ferryPayAmount, trainPayAmount
4300  bool special_b: onJob, jobFinished, jobCancelled, jobDelivered, fined, tollgate, ferry,
      train, refuel, refuelPayed
```

Położenie ciężarówki w świecie to układ współrzędnych SCS: x na wschód, y w górę, z na południe, w metrach
(prawoskrętny, y w górę – przeglądarka rysuje go tak, jak jest). Promy, pociągi i wczytanie
zapisu przesuwają ciężarówkę bez jazdy: trasa jest tam przerywana.

Cała mapa pamięci (32 KiB wtyczki: każda strefa powyżej i te nieodczytane – konfiguracja
ciężarówki, koła, zużycie, pozostałe kanały ciężarówki oraz to, co wersja układa po bajcie 4400,
czyli przyczepy) jest zachowywana w surowym pliku pomocniczym sesji za każdym razem, gdy się zmieni,
jako `type` `SCSTelemetry` z obok zapisaną `revision` – także strona innej wersji wtyczki, która
jest zachowana w całości zamiast być odczytana błędnie.

Ten sam moduł obsługuje też: [American Truck Simulator (dane na żywo)](game-ats.md).

## Pozycje i osie {#positions-and-axes}

| | |
|---|---|
| Zapisane pozycje | tak |
| Oś pionowa | `y` |
| Jednostki | metry (świat SCS: x na wschód, y w górę, z na południe) |
| Odbicie dla przeglądarki | brak |
| Skala jednostki (`scale`: przeglądarka mnoży przez nią pozycje) | 1 |

Te wartości trafiają do `meta.json` każdej sesji (`axes`) i, gdy sesja ma pozycje, do stopki `heat.parquet`. Dzięki temu przeglądarka 3DHeat sama obraca i skaluje wiersze – zob. [Dane](the-data.md).

## Tryb wieloosobowy {#multiplayer}

- Oznaczone jako grane online (`multiplayer`): **tak**. `games --markdown` pokazuje to jako „dozwolone (odczytuje tylko to, co gra publikuje)”.
- Rodzaj `telemetry`: odczytuje tylko to, co gra lub platforma udostępnia (port UDP albo pamięć współdzielona, którą gra publikuje), więc nagrywa też w grze online; flaga decyduje tylko o tym, czy wolno kiedykolwiek czytać pamięć.
- Pamięć: **nigdy** nie jest odczytywana przez ten adapter. Tylko adaptery `memory` czytają pamięć, i nigdy dla gry oznaczonej jako grana online – zob. [Źródła i zasady](sources-and-rules.md).

## Co jest zapisywane w statystykach {#statistics-recorded}

Klucze statystyk, które kod tego adaptera ustawia po nazwie (`stats` każdej sesji w `meta.json` i tabela `stats` w `watcher.sqlite`):

`deliveries`, `distance_km`, `fines`, `fines_total`, `jobs_cancelled`, `max_speed_kmh`, `refuels`, `revenue`, `tolls_total`, `xp`

Klucz w nawiasach klamrowych jest uzupełniany w czasie działania (`score.{team}` to jeden klucz na zespół). Klucze, które kod bierze z tabeli pól gry lub z jej własnych nazw statystyk, nie są na tej liście; sekcja „Co jest zapisywane” wyżej wymienia je.

## Kompletność {#completeness}

Watcher stosuje [zasadę konwertera 3DHeat](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md): to, co źródło zawiera, jest odczytywane lub zachowywane, nigdy nie jest pomijane. Oprócz wierszy każdy pakiet, strona, linia lub odpowiedź, którą adapter otrzyma, jest zachowana w całości w `heat.raw.parquet` sesji (kolumny `time`, `ms`, `type`, `used`, `payload`, `text`, a potem każde pole zachowane po nazwie; `used` oznacza to, co stało się też wierszami), a `selfCheck.completeness` w `meta.json` liczy każdy `type` – `lost` wynosi 0.

**Odczytane**

- stan SDK i pauzy, wersja wtyczki, gra i wersja, czas w grze, pozycja ciężarówki w świecie i kierunek, prędkość, przebieg, marka i nazwa ciężarówki, ładunek, miasto i firma źródłowa oraz docelowa, przychód zlecenia, XP i dystans, kara za anulowanie, mandaty i ich powód, opłaty drogowe, promy, pociągi, flagi szczególnych zdarzeń (wiersze, zdarzenia i statystyki)
- teraz także na wierszach pozycji: `pitch` i `roll` (stopnie, z obrotów SDK), `gear` i `rpm`
- przesunięcia sprawdzone względem ręcznie przepisanego nagłówka wtyczki w wersji 12, którego początki stref są sprawdzane w testach; jeszcze nie sprawdzone w grze

**Zachowane w surowej postaci**

- `SCSTelemetry`: cała mapa wtyczki (32 KiB), każdy odczyt, którego bajty różnią się od ostatnio zachowanej kopii (`unchanged_reads` w meta.json liczy pozostałe), z `revision` obok: każda strefa – konfiguracja ciężarówki i przyczepy, kanały ciężarówki (pedały, kierownica, paliwo, AdBlue, ciśnienia, temperatury, zużycie, światła, koła), wektory położenia i przyspieszenia, ciągi znaków zlecenia i rozgrywki oraz wszystko, co wersja układa po bajcie 4400 (przyczepy); `used` jest prawdą, gdy SDK jest aktywne, a wersja to 12
- strona innej wersji wtyczki jest zachowana w całości z `used` ustawionym na false, zamiast być odczytana błędnie

**Niedostępne**

- wszystko, czego wtyczka nie kopiuje z SDK, i wszystko, gdy wtyczka nie jest zainstalowana: gra sama nie publikuje żadnej telemetrii
- ciężarówki innych graczy w TruckersMP lub w konwojach: SDK podaje tylko własną ciężarówkę gracza

**Rozmiar**: 32 KiB do 10 razy na sekundę podczas jazdy (każdy odczyt wtedy się różni): około 1,2 GB na godzinę przed kompresją, jedna kopia podczas pauzy; większość strony to zera i konfiguracja, która się nie zmienia, więc zstd zmniejsza ją wielokrotnie (jeszcze nie zmierzone na prawdziwej sesji)

## Sprawdzone {#verified}

przetestowane na pamięci współdzielonej zbudowanej na podstawie układu nagłówka wtyczki w wersji 12; nie przetestowane w grze

## Źródło {#source}

[heat3d_watch/adapters/ets2.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/ets2.py)

<!-- Generated from the adapter by tools/gen_game_pages.py; change the adapter and run it again rather than editing this page. -->
