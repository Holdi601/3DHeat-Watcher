---
title: "American Truck Simulator (živé dáta)"
nav_order: 1
lang: "sk"
source: game-ats.md
source_hash: "974252b355da"
nav_exclude: true
search_exclude: true
---
# American Truck Simulator (živé dáta) {#american-truck-simulator-live-data}

Počas hry American Truck Simulator watcher ukladá dáta, ktoré samotná hra posiela von, aby ste ich neskôr mohli pozrieť na mape v 3DHeat prehliadači.

*Technické údaje: adaptér `ats`, typ [`telemetry`](sources-and-rules.md); beží, kým beží `amtrucks.exe`, a hľadá nové dáta každých 0,1 s.*

## Čo sa zaznamenáva {#what-is-recorded}

- svetová poloha nákladiaka (x na východ, y nahor, z na juh, m) 10-krát za sekundu počas jazdy, každých 5 s, keď stojí; smer, rýchlosť, stav tachometra
- začaté zákazky (náklad, odkiaľ, kam), doručené (výnos, XP, km), zrušené; pokuty, mýto, trajekty, vlaky, tankovania
- trajekty, vlaky a načítané uložené hry prerušia trasu (teleport, spawn)
- vzdialenosť, najvyššia rýchlosť, doručenia, výnos, XP, pokuty
- celá zdieľaná pamäť pluginu v `heat.raw.parquet` pri každej zmene

## Odkiaľ to berie {#where-it-comes-from}

zdieľaná pamäť Local\SCSTelemetry, ktorú zapisuje RenCloud scs-sdk-plugin (revízia 12) v &lt;hra>\bin\win_x64\plugins

## Ako to zapnúť {#how-to-switch-it-on}

nainštalujte scs-telemetry.dll (revízia 12) z github.com/RenCloud/scs-sdk-plugin do &lt;hra>\bin\win_x64\plugins; hra sa pri každom spustení raz opýta, či povoliť SDK

## Ako to funguje {#how-it-works}

Euro Truck Simulator 2 a American Truck Simulator: telemetrické SDK SCS, cez plugin RenCloud.

SCS zverejňuje telemetrické SDK (<https://modding.scssoft.com/wiki/Documentation/Engine/SDK/Telemetry>) pre pluginy, ktoré hráč vkladá do `<hra>\bin\win_x64\plugins\`. Sama hra nič nezverejňuje; široko používaný plugin z <https://github.com/RenCloud/scs-sdk-plugin> (MIT) kopíruje kanály SDK do zdieľanej pamäte `Local\SCSTelemetry` (32 KiB), rozloženej podľa `scs-telemetry/inc/scs-telemetry-common.hpp`. Toto číta revíziu 12 tohto rozloženia (PLUGIN_REVID 12) a nič iné: plugin zapisuje svoju revíziu na posun 40 a každá iná revízia sa nečíta, namiesto toho, aby sa čítala zle. Použité posuny (zóny podľa hlavičky; prirodzené zarovnanie):

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

Svetové umiestnenie nákladiaka je svetový rámec SCS: x na východ, y nahor, z na juh, metre (pravotočivý, y nahor – prehliadač ho kreslí tak, ako je). Trajekty, vlaky a načítanie uloženej hry premiestnia nákladiak bez jazdy: trasa sa tam preruší.

Celá mapa pamäte (32 KiB pluginu: každá zóna vyššie aj tie, ktoré sa nečítajú – konfigurácia nákladiaka, kolesá, opotrebenie, ostatné kanály nákladiaka, a to, čo revízia rozkladá za bajtom 4400, návesy) sa uchová v surovom sprievodnom súbore relácie pri každej zmene, ako `type` `SCSTelemetry` s `revision` vedľa – stránka inej revízie sa tiež uchová celá, namiesto toho, aby sa čítala zle.

Rovnaký modul slúži aj: [Euro Truck Simulator 2 (živé dáta)](game-ets2.md).

## Polohy a osi {#positions-and-axes}

| | |
|---|---|
| Zaznamenané polohy | áno |
| Os nahor | `y` |
| Jednotky | metre (svet SCS: x na východ, y nahor, z na juh) |
| Zrkadlenie pre prehliadač | žiadne |
| Mierka jednotiek (`scale`: prehliadač polohy touto hodnotou násobí) | 1 |

Tieto údaje idú do `meta.json` každej relácie (`axes`) a, ak má relácia polohy, do päty súboru `heat.parquet`, takže 3DHeat prehliadač si riadky sám otočí a zmení ich mierku – pozrite [Dáta](the-data.md).

## Viachráčová hra {#multiplayer}

- Označené ako hrané online (`multiplayer`): **áno**. `games --markdown` to zobrazí ako „povolené (číta len to, čo hra zverejňuje)“.
- Typ `telemetry`: číta len to, čo hra alebo platforma vydáva (UDP port alebo zdieľaná pamäť, ktorú hra zverejňuje), takže zaznamenáva aj v online hre, nielen offline; príznak rozhoduje len o tom, či sa pamäť smie čítať.
- Pamäť: adaptér ju **nikdy** nečíta. Pamäť čítajú len adaptéry typu `memory` a nikdy pre hru označenú ako hranú online – pozrite [Zdroje a pravidlá](sources-and-rules.md).

## Zaznamenané štatistiky {#statistics-recorded}

Kľúče štatistík, ktoré kód tohto adaptéra nastavuje podľa mena (štatistiky každej relácie `stats` v `meta.json` a tabuľka `stats` v `watcher.sqlite`):

`deliveries`, `distance_km`, `fines`, `fines_total`, `jobs_cancelled`, `max_speed_kmh`, `refuels`, `revenue`, `tolls_total`, `xp`

Kľúč v zložených zátvorkách sa dopĺňa za behu (`score.{team}` je jeden kľúč na tím). Kľúče, ktoré kód berie z tabuľky polí hry alebo z názvov štatistík hry, v tomto zozname nie sú; „Čo sa zaznamenáva“ vyššie ich pomenúva.

## Úplnosť {#completeness}

Watcher sa riadi [pravidlom konvertorov](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md) 3DHeat: to, čo zdroj obsahuje, sa číta alebo uchováva, nikdy sa nezahadzuje. Okrem riadkov sa každý paket, stránka, riadok alebo odpoveď, ktorú adaptér dostane, uchová celá v `heat.raw.parquet` relácie (stĺpce `time`, `ms`, `type`, `used`, `payload`, `text` a ďalšie polia, ktoré sa uchovávajú podľa mena; `used` označuje to, čo sa stalo aj riadkami), a `selfCheck.completeness` v `meta.json` počíta každý `type` – `lost` je 0.

**Čítané**

- stav SDK a pauzy, revízia pluginu, hra a verzia, herný čas, svetová poloha a smer nákladiaka, rýchlosť, stav tachometra, značka a názov nákladiaka, náklad, zdrojové a cieľové mesto a firma, výnos zákazky, XP a vzdialenosť, penalizácia za zrušenie, pokuty a ich dôvod, mýto, trajekty, vlaky, príznaky osobitných udalostí (riadky, udalosti a štatistiky)
- teraz aj na riadkoch polohy: `pitch` a `roll` (stupne, z otáčok SDK), `gear` a `rpm`
- posuny overené proti prepisu hlavičky pole po poli revízie 12 pluginu, ktorej začiatky zón sú potvrdené v testoch; zatiaľ nie proti hre

**Uchované surové**

- `SCSTelemetry`: celá 32 KiB zdieľaná pamäť pluginu, pri každom čítaní, ktorého bajty sa líšia od kópie uchovanej naposledy (`unchanged_reads` v meta.json počíta ostatné); `revision` vedľa: každá zóna – konfigurácia nákladiaka a návesu, kanály nákladiaka (pedále, riadenie, palivo, AdBlue, tlaky, teploty, opotrebenie, svetlá, kolesá), vektory umiestnenia a zrýchlenia, reťazce zákazky a hry, a všetko, čo revízia rozkladá za bajtom 4400 (návesy); `used` je pravda, kým je SDK aktívne a revízia je 12
- stránka inej revízie pluginu sa uchová celá s `used` nepravda, namiesto toho, aby sa čítala zle

**Nedostupné**

- čokoľvek, čo plugin z SDK nekopíruje, a všetko, kým plugin nie je nainštalovaný: hra sama žiadnu telemetriu nezverejňuje
- nákladiaky iných hráčov v TruckersMP alebo konvojoch: SDK dáva len nákladiak hráča

**Veľkosť**: 32 KiB až 10-krát za sekundu počas jazdy (každé čítanie sa vtedy líši): približne 1,2 GB za hodinu pred kompresiou, jedna kópia počas pauzy; väčšina stránky sú nuly a konfigurácia, ktorá sa nemení, takže zstd ju mnohonásobne zmenší (na skutočnej relácii ešte nezmerané)

## Overené {#verified}

testované na zdieľanej pamäti zostavenej podľa hlavičky revízie 12 pluginu; neotestované proti hre

## Zdroj {#source}

[heat3d_watch/adapters/ets2.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/ets2.py)

<!-- Generované z adaptéra nástrojom tools/gen_game_pages.py; zmeňte adaptér a spustite to znova, namiesto úpravy tejto stránky. -->
