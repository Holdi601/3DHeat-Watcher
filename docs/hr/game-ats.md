---
title: "American Truck Simulator (živi podaci)"
nav_order: 1
lang: "hr"
source: game-ats.md
source_hash: "974252b355da"
nav_exclude: true
search_exclude: true
---
# American Truck Simulator (živi podaci) {#american-truck-simulator-live-data}

Dok igrate American Truck Simulator, watcher sprema podatke koje sama igra šalje, pa ih kasnije možete pogledati na karti u 3DHeat pregledniku.

*Tehnički detalji: adapter `ats`, vrsta [`telemetry`](sources-and-rules.md); radi dok je `amtrucks.exe` pokrenut i traži nove podatke svakih 0,1 s.*

## Što se bilježi {#what-is-recorded}

- svjetska pozicija kamiona (x istok, y gore, z jug, m) 10 puta u sekundi dok se vozi, svakih 5 s dok stoji; smjer, brzina, kilometraža
- započeti poslovi (teret, polazište, odredište), dovršeni (zarada, XP, km), otkazani; kazne, cestarine, trajekti, vlakovi, punjenja goriva
- trajekti, vlakovi i učitane spremljene igre prekidaju trasu (teleport, spawn)
- udaljenost, najveća brzina, dostave, zarada, XP, kazne
- cijela dijeljena memorija dodatka u `heat.raw.parquet`, svaki put kad se promijeni

## Odakle dolazi {#where-it-comes-from}

dijeljena memorija Local\SCSTelemetry koju piše RenCloud scs-sdk-plugin (revizija 12) u &lt;game>\bin\win_x64\plugins

## Kako to uključiti {#how-to-switch-it-on}

instalirajte scs-telemetry.dll (revizija 12) s github.com/RenCloud/scs-sdk-plugin u &lt;game>\bin\win_x64\plugins; igra pri svakom pokretanju jednom pita smije li se SDK koristiti

## Kako radi {#how-it-works}

Euro Truck Simulator 2 i American Truck Simulator: SCS telemetrijski SDK, preko RenCloud dodatka.

SCS objavljuje telemetrijski SDK (<https://modding.scssoft.com/wiki/Documentation/Engine/SDK/Telemetry>) za dodatke koje igrač stavlja u `<game>\bin\win_x64\plugins\`. Sama igra ništa ne objavljuje; široko korišten dodatak s <https://github.com/RenCloud/scs-sdk-plugin> (MIT) kopira kanale SDK-a u dijeljenu memoriju `Local\SCSTelemetry` (32 KiB), raspoređenu kao što piše u `scs-telemetry/inc/scs-telemetry-common.hpp`. Ovo čita reviziju 12 tog rasporeda (PLUGIN_REVID 12) i ništa drugo: dodatak svoju reviziju piše na pomaku 40, a svaka ostala revizija ostaje nepročitana umjesto da se pogrešno pročita. Korišteni pomaci (zone kako ih zaglavlje označava; prirodno poravnanje):

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

Svjetski položaj kamiona je SCS-ov svjetski okvir: x istok, y gore, z jug, metri (desnoruk, y gore - preglednik ga crta kakav jest). Trajekti, vlakovi i učitavanje spremljene igre pomiču kamion bez vožnje: trasa se tu prekida.

Cijelo preslikavanje (32 KiB dodatka: svaka zona gore i one koje se ne čitaju - konfiguracija kamiona, kotači, habanje, ostali kanali kamiona, i ono što revizija raspoređuje iza bajta 4400, prikolice) čuva se u sirovom pratećem dijelu sesije svaki put kad se promijeni, kao `type` `SCSTelemetry` uz `revision` - i stranica druge revizije čuva se cijela umjesto da se pogrešno pročita.

Istim modulom služi i: [Euro Truck Simulator 2 (živi podaci)](game-ets2.md).

## Pozicije i osi {#positions-and-axes}

| | |
|---|---|
| Bilježe se pozicije | da |
| Os prema gore | `y` |
| Jedinice | metri (SCS svijet: x istok, y gore, z jug) |
| Zrcaljeno za preglednik | nema |
| Mjerilo jedinice (`scale`: preglednik ovim množi pozicije) | 1 |

Ovo ide u `meta.json` (`axes`) svake sesije i, kad sesija ima pozicije, u podnožje `heat.parquet`, pa 3DHeat preglednik sam okreće i skalira retke - vidi [Podaci](the-data.md).

## Više igrača {#multiplayer}

- Označeno kao igranje na mreži (`multiplayer`): **da**. `games --markdown` to prikazuje kao "allowed (reads only what the game publishes)".
- Vrsta `telemetry`: čita samo ono što igra ili platforma daje (UDP port ili dijeljena memorija koju igra objavljuje), pa bilježi i u igri na mreži i izvan nje; zastavica odlučuje samo smije li se ikad čitati memorija.
- Memorija: adapter je **nikad** ne čita. Memoriju čitaju samo adapteri vrste `memory`, i nikad za igru označenu kao igranu na mreži - vidi [Izvori i pravila](sources-and-rules.md).

## Statistika {#statistics-recorded}

Ključevi statistike koje kod ovog adaptera postavlja po imenu (`stats` u `meta.json` svake sesije i tablica `stats` u `watcher.sqlite`):

`deliveries`, `distance_km`, `fines`, `fines_total`, `jobs_cancelled`, `max_speed_kmh`, `refuels`, `revenue`, `tolls_total`, `xp`

Ključ u vitičastim zagradama dovršava se pri radu (`score.{team}` je jedan ključ po timu). Ključevi koje kod uzima iz tablice polja igre ili iz imena statistike same igre nisu na ovom popisu; odjeljak „Što se bilježi“ ih navodi.

## Potpunost {#completeness}

Watcher slijedi [pravilo pretvarača](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md) iz 3DHeata: što izvor sadrži, to se čita ili čuva, nikad se ne odbacuje. Osim redaka, svaki paket, stranica, redak ili odgovor koji adapter primi čuva se cijel u `heat.raw.parquet` sesije (stupci `time`, `ms`, `type`, `used`, `payload`, `text`, pa svako polje sačuvano po imenu; `used` označava što je postalo i retkom), a `selfCheck.completeness` u `meta.json`-u broji svaki `type` - `lost` je 0.

**Čita se**

- stanje SDK-a i pauze, revizija dodatka, igra i verzija, vrijeme u igri, svjetska pozicija i smjer kamiona, brzina, kilometraža, marka i ime kamiona, teret, grad i tvrtka polazišta i odredišta, zarada posla, XP i udaljenost, kazna za otkazivanje, kazne i njihov prekršaj, cestarine, trajekti, vlakovi, posebne zastavice događaja (retci, događaji i statistika)
- sada i na retcima pozicije: `pitch` i `roll` (stupnjevi, iz okretaja SDK-a), `gear` i `rpm`
- pomaci provjereni prema ručnom prijepisu zaglavlja dodatka revizije 12, čiji su početci zona potvrđeni u testovima; još nije provjereno u samoj igri

**Čuva se sirovo**

- `SCSTelemetry`: cijelo 32 KiB preslikavanje dodatka, svako čitanje čiji se bajtovi razlikuju od zadnje sačuvane kopije (`unchanged_reads` u meta.json broji ostala), uz `revision`: svaka zona - konfiguracija kamiona i prikolice, kanali kamiona (pedale, upravljanje, gorivo, AdBlue, tlakovi, temperature, habanje, svjetla, kotači), vektori položaja i ubrzanja, tekstovi o poslu i igri, i sve što revizija raspoređuje iza bajta 4400 (prikolice); `used` je istinit dok je SDK aktivan i revizija je 12
- stranica druge revizije dodatka čuva se cijela s `used` false umjesto da se pogrešno pročita

**Nije dostupno**

- sve što dodatak ne kopira iz SDK-a, i sve dok dodatak nije instaliran: igra sama ne objavljuje nikakvu telemetriju
- kamioni drugih igrača u TruckersMP-u ili konvojima: SDK daje samo kamion igrača

**Veličina**: 32 KiB do 10 puta u sekundi dok se vozi (tada se svako čitanje razlikuje): oko 1,2 GB po satu prije sažimanja, jedna kopija dok je pauza; većina stranice su nule i konfiguracija koja se ne mijenja, pa je zstd višestruko smanji (još nije izmjereno na pravoj sesiji)

## Provjereno {#verified}

testirano na dijeljenoj memoriji izrađenoj prema zaglavlju dodatka revizije 12; neprovjereno u samoj igri

## Izvor {#source}

[heat3d_watch/adapters/ets2.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/ets2.py)

<!-- Generated from the adapter by tools/gen_game_pages.py; change the adapter and run it again rather than editing this page. -->
