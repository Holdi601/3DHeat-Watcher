---
title: "American Truck Simulator (podaci uživo)"
nav_order: 1
lang: "bs"
source: game-ats.md
source_hash: "974252b355da"
nav_exclude: true
search_exclude: true
---
# American Truck Simulator (podaci uživo) {#american-truck-simulator-live-data}

Dok igrate American Truck Simulator, watcher sprema podatke koje igra sama šalje, da ih kasnije možete pogledati na mapi u preglednik 3DHeat-u.

*Tehnički detalji: adapter `ats`, vrsta [`telemetry`](sources-and-rules.md); radi dok je pokrenut `amtrucks.exe` i svakih 0,1 s traži nove podatke.*

## Šta se bilježi {#what-is-recorded}

- svjetski položaj kamiona (x istok, y gore, z jug, m) na 10 Hz u vožnji, svakih 5 s dok stoji; smjer, brzina, kilometar-sat
- započeti poslovi (teret, odakle, kamo), isporučeni (zarada, XP, km), otkazani; kazne, putarine, trajekti, vozovi, točenja goriva
- trajekti, vozovi i učitani save-ovi prekidaju rutu (teleport, spawn)
- pređena distanca, najveća brzina, isporuke, zarada, XP, kazne
- cijela dijeljena memorija plugina u `heat.raw.parquet`, svaki put kad se promijeni

## Odakle dolazi {#where-it-comes-from}

dijeljena memorija Local\SCSTelemetry koju piše RenCloud scs-sdk-plugin (revizija 12) u &lt;game>\bin\win_x64\plugins

## Kako ga uključiti {#how-to-switch-it-on}

instalirajte scs-telemetry.dll (revizija 12) sa github.com/RenCloud/scs-sdk-plugin u &lt;game>\bin\win_x64\plugins; igra pri svakom pokretanju jednom pita da li dozvoljavate SDK

## Kako radi {#how-it-works}

Euro Truck Simulator 2 i American Truck Simulator: SCS telemetrijski SDK, preko RenCloud plugina.

SCS objavljuje telemetrijski SDK (<https://modding.scssoft.com/wiki/Documentation/Engine/SDK/Telemetry>)
za plugine koje igrač stavlja u `<game>\bin\win_x64\plugins\`. Sama igra
ne objavljuje ništa; često korišteni plugin sa <https://github.com/RenCloud/scs-sdk-plugin>
(MIT) kopira kanale SDK-a u dijeljenu memoriju `Local\SCSTelemetry`
(32 KiB), raspoređenu u `scs-telemetry/inc/scs-telemetry-common.hpp`. Ovo čita
reviziju 12 tog rasporeda (PLUGIN_REVID 12) i ništa drugo: plugin
piše svoju reviziju na pomaku 40, a svaka druga revizija ostaje nepročitana umjesto
da se pogrešno pročita. Korišteni pomaci (zone kako ih označava zaglavlje; prirodno poravnanje):

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

Svjetski položaj kamiona je SCS-ov svjetski okvir: x istok, y gore, z jug, metri
(desnoruki, y gore - preglednik ga crta onakav kakav jest). Trajekti, vozovi i učitavanje
save-a pomjeraju kamion bez vožnje: ruta se tu prekida.

Cijelo mapiranje (32 KiB plugina: sve gore navedene zone i one koje se ne
čitaju - konfiguracija kamiona, točkovi, habanje, ostali kanali kamiona, i
ono što revizija raspoređuje poslije bajta 4400, prikolice) čuva se u sirovom sidecaru sesije svaki put kad se promijeni,
`type` `SCSTelemetry` s `revision` pored njega - i stranica druge
revizije, koja se čuva cijela umjesto da se pogrešno pročita.

Isti modul služi i za: [Euro Truck Simulator 2 (podaci uživo)](game-ets2.md).

## Položaji i ose {#positions-and-axes}

| | |
|---|---|
| Položaji se bilježe | da |
| Osa gore | `y` |
| Jedinice | metri (SCS svijet: x istok, y gore, z jug) |
| Zrcaljeno za preglednik | nijedna |
| Skala jedinica (`scale`: preglednik njome množi položaje) | 1 |

Ovo ide u `meta.json` svake sesije (`axes`) i, kad sesija ima položaje, u podnožje datoteke `heat.parquet`, pa preglednik 3DHeat sam okreće i skalira redove - vidite [Podaci](the-data.md).

## Multiplayer {#multiplayer}

- Označena kao igrana online (`multiplayer`): **da**. `games --markdown` to prikazuje kao "allowed (reads only what the game publishes)".
- Vrsta `telemetry`: čita samo ono što igra ili platforma daje (UDP port ili dijeljenu memoriju koju igra objavljuje), pa snima i u online igri kao i offline; oznaka odlučuje samo smije li se memorija ikad čitati.
- Memorija: ovaj je adapter **nikad** ne čita. Memoriju čitaju samo `memory` adapteri, i nikad za igru označenu kao igranu online - vidite [Izvori i pravila](sources-and-rules.md).

## Zabilježena statistika {#statistics-recorded}

Ključevi statistike koje kod ovog adaptera postavlja po imenu (`stats` svake sesije u `meta.json` i tabela `stats` u `watcher.sqlite`):

`deliveries`, `distance_km`, `fines`, `fines_total`, `jobs_cancelled`, `max_speed_kmh`, `refuels`, `revenue`, `tolls_total`, `xp`

Ključ u vitičastim zagradama dovršava se pri izvođenju (`score.{team}` je jedan ključ po timu). Ključevi koje kod uzima iz tabele polja igre ili iz vlastitih naziva statistike igre nisu na ovom popisu; "Šta se bilježi" iznad ih navodi.

## Potpunost {#completeness}

Watcher slijedi 3DHeat-ovo [pravilo konvertera](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md): ono što izvor sadrži se čita ili čuva, nikad ne odbacuje. Osim redova, svaki paket, stranica, linija ili odgovor koji adapter primi čuva se cijel u `heat.raw.parquet` sesije (kolone `time`, `ms`, `type`, `used`, `payload`, `text`, pa svako polje čuvano po imenu; `used` označava šta je također postalo redovi), a `selfCheck.completeness` u `meta.json` broji svaki `type` - `lost` je 0.

**Čita se**

- stanje SDK-a i pauze, revizija plugina, igra i verzija, vrijeme u igri, svjetski položaj i smjer kamiona, brzina, kilometar-sat, marka i naziv kamiona, teret, izvorni i odredišni grad i firma, zarada od posla, XP i distanca, kazna za otkazivanje, kazne i njihov prekršaj, putarine, trajekti, vozovi, posebne oznake događaja (redovi, događaji i statistika)
- sada i u redovima položaja: `pitch` i `roll` (stepeni, iz obrtaja SDK-a), `gear` i `rpm`
- pomaci provjereni prema prijepisu zaglavlja revizije 12 plugina polje po polje, čiji se počeci zona provjeravaju u testovima; još ne prema igri

**Čuva se sirovo**

- `SCSTelemetry`: cijelo mapiranje plugina od 32 KiB, svako čitanje čiji se bajtovi razlikuju od zadnje sačuvane kopije (`unchanged_reads` u meta.json broji ostala), `revision` pored njega: svaka zona - konfiguracija kamiona i prikolice, kanali kamiona (pedale, upravljanje, gorivo, AdBlue, pritisci, temperature, habanje, svjetla, točkovi), vektori položaja i ubrzanja, tekstovi posla i igre, i sve što revizija raspoređuje poslije bajta 4400 (prikolice); `used` je istinito dok je SDK aktivan i revizija je 12
- stranica druge revizije plugina čuva se cijela s `used` neistinitim umjesto da se pogrešno pročita

**Nije dostupno**

- sve što plugin ne kopira iz SDK-a, i sve dok plugin nije instaliran: igra sama ne objavljuje telemetriju
- kamioni drugih igrača u TruckersMP ili konvojima: SDK daje samo igračev vlastiti kamion

**Veličina**: 32 KiB do 10 puta u sekundi u vožnji (tada se svako čitanje razlikuje): oko 1,2 GB na sat prije kompresije, jedna kopija dok je pauzirano; većina stranice su nule i konfiguracija koja se ne mijenja, pa je zstd smanjuje mnogo puta (još nije izmjereno na pravoj sesiji)

## Provjereno {#verified}

testirano na dijeljenoj memoriji izgrađenoj prema rasporedu zaglavlja revizije 12 plugina; nije testirano na igri

## Izvor {#source}

[heat3d_watch/adapters/ets2.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/ets2.py)

<!-- Generated from the adapter by tools/gen_game_pages.py; change the adapter and run it again rather than editing this page. -->
