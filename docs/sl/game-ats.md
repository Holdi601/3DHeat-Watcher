---
title: "American Truck Simulator (živi podatki)"
nav_order: 1
lang: "sl"
source: game-ats.md
source_hash: "974252b355da"
nav_exclude: true
search_exclude: true
---
# American Truck Simulator (živi podatki) {#american-truck-simulator-live-data}

Medtem ko igrate American Truck Simulator, watcher shrani podatke, ki jih igra sama pošilja ven, da si jih lahko pozneje ogledate na zemljevidu v pregledovalniku 3DHeat.

*Tehnične podrobnosti: adapter `ats`, vrsta [`telemetry`](sources-and-rules.md); teče, medtem ko se izvaja `amtrucks.exe`, in vsakih 0,1 s preverja nove podatke.*

## Kaj se zapiše {#what-is-recorded}

- svetovni položaj tovornjaka (x vzhod, y navzgor, z jug, m) desetkrat na sekundo med vožnjo, vsakih 5 s med mirovanjem; smer, hitrost, kilometrina
- začeta dela (tovor, od kod, kam), dostavljena (zaslužek, XP, km), preklicana; kazni, cestnine, trajekti, vlaki, točenje goriva
- trajekti, vlaki in naloženi shranjeni položaji prekinejo pot (teleport, spawn)
- razdalja, najvišja hitrost, dostave, zaslužek, XP, kazni
- celotni skupni pomnilnik vtičnika v `heat.raw.parquet`, ob vsaki spremembi

## Od kod prihajajo {#where-it-comes-from}

skupni pomnilnik Local\SCSTelemetry, ki ga zapisuje vtičnik RenCloud scs-sdk-plugin (revizija 12) v &lt;igra&gt;\bin\win_x64\plugins

## Kako vklopiti {#how-to-switch-it-on}

namestite scs-telemetry.dll (revizija 12) iz github.com/RenCloud/scs-sdk-plugin v &lt;igra&gt;\bin\win_x64\plugins; igra ob vsakem zagonu enkrat vpraša, ali dovoli SDK

## Kako deluje {#how-it-works}

Euro Truck Simulator 2 in American Truck Simulator: telemetrijski SDK SCS, prek vtičnika RenCloud.

SCS objavlja telemetrijski SDK (<https://modding.scssoft.com/wiki/Documentation/Engine/SDK/Telemetry>)
za vtičnike, ki jih igralec da v `<igra>\bin\win_x64\plugins\`. Sama igra
ne objavlja ničesar; splošno uporabljen vtičnik iz <https://github.com/RenCloud/scs-sdk-plugin>
(MIT) kanale SDK kopira v skupni pomnilnik `Local\SCSTelemetry`
(32 KiB), postavljen po `scs-telemetry/inc/scs-telemetry-common.hpp`. To bere
revizijo 12 te postavitve (PLUGIN_REVID 12) in nič drugega: vtičnik svojo revizijo
zapiše na odmik 40, katera koli druga revizija pa ostane neprebrana, namesto da bi bila
napačno prebrana. Uporabljeni odmiki (cone, kot jih označuje glava; naravno poravnanje):

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

Položaj tovornjaka v svetu je svetovni okvir SCS: x vzhod, y navzgor, z jug, metri
(desnosučen, y navzgor - pregledovalnik ga riše tak, kot je). Trajekti, vlaki in nalaganje
shranjenega položaja premaknejo tovornjak brez vožnje: tam se pot prekine.

Celotna preslikava (32 KiB vtičnika: vse zgoraj omenjene cone in tiste, ki niso prebrane - konfiguracija
tovornjaka, kolesa, obraba, drugi kanali tovornjaka, in kar revizija postavi za bajtom 4400, prikolice)
se ob vsaki spremembi shrani v surovo spremljevalno datoteko seje, `type` `SCSTelemetry` z
`revision` ob sebi - tudi stran druge revizije, ki se shrani cela, namesto da bi bila napačno prebrana.

Isti modul streže tudi: [Euro Truck Simulator 2 (živi podatki)](game-ets2.md).

## Položaji in osi {#positions-and-axes}

| | |
|---|---|
| Zabeleženi položaji | da |
| Navpična os | `y` |
| Enote | metri (svet SCS: x vzhod, y navzgor, z jug) |
| Zrcaljenje za pregledovalnik | brez |
| Merilo enote (`scale`: pregledovalnik z njim pomnoži položaje) | 1 |

Te vrednosti gredo v `meta.json` vsake seje (`axes`) in, kadar seja vsebuje položaje, v nogo `heat.parquet`, zato pregledovalnik 3DHeat vrti in meri vrstice sam - glejte [Podatki](the-data.md).

## Več igralcev {#multiplayer}

- Označeno kot igranje na spletu (`multiplayer`): **da**. `games --markdown` to prikaže kot "dovoljeno (bere samo to, kar igra objavi)".
- Vrsta `telemetry`: bere samo, kar igra ali platforma ponudi (UDP vrata ali skupni pomnilnik, ki ga igra objavlja), zato zapisuje tudi pri igri na spletu in ne samo offline; zastavica odloča samo o tem, ali sme kdaj brati pomnilnik.
- Pomnilnik: tega adapterja **nikoli** ne bere. Samo adapterji vrste `memory` berejo pomnilnik, in nikoli za igro, označeno kot igranje na spletu - glejte [Viri in pravila](sources-and-rules.md).

## Zabeležene statistike {#statistics-recorded}

Ključi statistik, ki jih koda tega adapterja nastavlja po imenu (`stats` v `meta.json` vsake seje in tabela `stats` v `watcher.sqlite`):

`deliveries`, `distance_km`, `fines`, `fines_total`, `jobs_cancelled`, `max_speed_kmh`, `refuels`, `revenue`, `tolls_total`, `xp`

Ključ v zavitih oklepajih se dokonča med delovanjem (`score.{team}` je en ključ za vsako ekipo). Ključi, ki jih koda vzame iz tabele polj igre ali iz imen statistik igre, na tem seznamu niso; zgoraj v "Kaj se zapiše" so našteti.

## Popolnost {#completeness}

Watcher sledi [pravilu pretvornikov](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md) 3DHeat: kar vir ima, se prebere ali shrani, nikoli ne izgine. Poleg vrstic se vsak paket, stran, vrstica ali odgovor, ki ga adapter prejme, shrani nedotaknjen v `heat.raw.parquet` seje (stolpci `time`, `ms`, `type`, `used`, `payload`, `text` in polja, shranjena po imenu; `used` označuje, kaj je postalo tudi vrstica), `selfCheck.completeness` v `meta.json` pa šteje vsak `type` - `lost` je 0.

**Prebrano**

- stanje SDK in pavze, revizija vtičnika, igra in različica, čas v igri, svetovni položaj in smer tovornjaka, hitrost, kilometrina,blagovna znamka in ime tovornjaka, tovor, izvorno in ciljno mesto in podjetje, zaslužek posla, XP in razdalja, kazen za preklic, kazni in njihov razlog, cestnine, trajekti, vlaki, posebne zastavice dogodkov (vrstice, dogodki in statistike)
- zdaj tudi v vrsticah položaja: `pitch` in `roll` (stopinje, iz obratov SDK), `gear` in `rpm`
- odmiki preverjeni na podlagi ročno prepisane glave vtičnika, revizija 12, katere začetki con so potrjeni v testih; še ne na igri

**Shranjeno surovo**

- `SCSTelemetry`: celotna 32 KiB preslikava vtičnika, ob vsakem branju, katerega bajti se razlikujejo od zadnje shranjene kopije (`unchanged_reads` v meta.json šteje ostala); `revision` ob njej: vsaka cona - konfiguracija tovornjaka in prikolice, kanali tovornjaka (pedali, krmilo, gorivo, AdBlue, tlaki, temperature, obraba, luči, kolesa), vektorji položaja in pospeška, nizi o poslu in igri ter vse, kar revizija postavi za bajtom 4400 (prikolice); `used` je resničen, medtem ko je SDK aktiven in je revizija 12
- stran druge revizije vtičnika se shrani cela z `used` false, namesto da bi bila napačno prebrana

**Ni na voljo**

- vse, kar vtičnik ne kopira iz SDK, in vse, medtem ko vtičnik ni nameščen: igra sama ne objavlja nobene telemetrije
- tovornjaki drugih igralcev v TruckersMP ali konvojih: SDK daje samo tovornjak igralca

**Velikost**: 32 KiB do 10-krat na sekundo med vožnjo (vsako branje se takrat razlikuje): približno 1,2 GB na uro pred stiskanjem, ena kopija med pavzo; večina strani so ničle in konfiguracija, ki se ne spreminja, zato jo zstd močno skrči (še ni izmerjeno na pravi seji)

## Preverjeno {#verified}

preizkušeno na skupnem pomnilniku, zgrajenem iz glave revizije 12 vtičnika; nepreizkušeno z igro

## Vir {#source}

[heat3d_watch/adapters/ets2.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/ets2.py)

<!-- Generated from the adapter by tools/gen_game_pages.py; change the adapter and run it again rather than editing this page. -->
