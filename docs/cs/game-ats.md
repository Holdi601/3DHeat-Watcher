---
title: "American Truck Simulator (živá data)"
nav_order: 1
lang: "cs"
source: game-ats.md
source_hash: "974252b355da"
nav_exclude: true
search_exclude: true
---
# American Truck Simulator (živá data) {#american-truck-simulator-live-data}

Když hrajete American Truck Simulator, Watcher uloží data, která hra sama posílá ven, abyste se na ně mohli později podívat na mapě v prohlížeči 3DHeat.

*Technické podrobnosti: adaptér `ats`, druh [`telemetry`](sources-and-rules.md); běží, dokud běží `amtrucks.exe`, a hledá nová data každých 0,1 s.*

## Co se zaznamenává {#what-is-recorded}

- světová pozice kamionu (x na východ, y nahoru, z na jih, m) 10krát za sekundu při jízdě, každých 5 s při stání; směr, rychlost, tachometr
- zahájené zakázky (náklad, odkud, kam), doručené (odměna, XP, km), zrušené; pokuty, mýtné, trajekty, vlaky, tankování
- trajekty, vlaky a načtené uložené hry přerušují trasu (teleport, spawn)
- vzdálenost, nejvyšší rychlost, doručení, odměna, XP, pokuty
- celá sdílená paměť pluginu v `heat.raw.parquet`, při každé změně

## Odkud to pochází {#where-it-comes-from}

sdílená paměť Local\SCSTelemetry, kterou zapisuje RenCloud scs-sdk-plugin (revize 12) ve složce &lt;hra>\bin\win_x64\plugins

## Jak to zapnout {#how-to-switch-it-on}

nainstalujte scs-telemetry.dll (revize 12) z github.com/RenCloud/scs-sdk-plugin do složky &lt;hra>\bin\win_x64\plugins; hra se při každém startu jednou zeptá, zda povolit SDK

## Jak to funguje {#how-it-works}

Euro Truck Simulator 2 a American Truck Simulator: telemetrické SDK SCS, přes plugin RenCloud.

SCS zveřejňuje telemetrické SDK (<https://modding.scssoft.com/wiki/Documentation/Engine/SDK/Telemetry>)
pro pluginy, které hráč vkládá do `<hra>\bin\win_x64\plugins\`. Sama hra
nic nezveřejňuje; široce používaný plugin z <https://github.com/RenCloud/scs-sdk-plugin>
(MIT) kopíruje kanály SDK do sdílené paměti `Local\SCSTelemetry`
(32 KiB), uspořádané podle `scs-telemetry/inc/scs-telemetry-common.hpp`. Watcher čte
revizi 12 tohoto layoutu (PLUGIN_REVID 12) a nic jiného: plugin
zapisuje svou revizi na offset 40 a každá jiná revize zůstane nepřečtena,
místo aby se špatně četla. Použité offsety (zóny, jak je hlavička označuje; přirozené zarovnání):

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

Umístění kamionu ve světě je světový systém SCS: x na východ, y nahoru, z na jih, metry
(pravotočivý, y nahoru - prohlížeč ho kreslí tak, jak je). Trajekty, vlaky a načtení
uložené hry přesunou kamion bez jízdy: trasa se tam přeruší.

Celé mapování (32 KiB pluginu: každá zmíněná zóna i ty nečtené -
konfigurace kamionu, kola, opotřebení, ostatní kanály kamionu a vše, co revize
uspořádá za bajtem 4400, tedy přívěsy) se při každé změně uloží do surového doprovodného souboru relace,
`type` `SCSTelemetry` s `revision` vedle něj - stránka jiné revize se také uloží celá,
místo aby se špatně četla.

Stejný modul slouží také: [Euro Truck Simulator 2 (živá data)](game-ets2.md).

## Pozice a osy {#positions-and-axes}

| | |
|---|---|
| Zaznamenané pozice | ano |
| Osa nahoru | `y` |
| Jednotky | metry (svět SCS: x na východ, y nahoru, z na jih) |
| Zrcadleno pro prohlížeč | žádné |
| Měřítko jednotek (`scale`: prohlížeč pozice tímto násobí) | 1 |

Tyto hodnoty se zapíší do `meta.json` (`axes`) každé relace a, pokud relace obsahuje pozice, do zápatí `heat.parquet`, takže prohlížeč 3DHeat otáčí a měřítko řádků upravuje sám - viz [Data](the-data.md).

## Více hráčů {#multiplayer}

- Označeno jako hraná online (`multiplayer`): **ano**. `games --markdown` to ukazuje jako „povoleno (čte jen to, co hra zveřejňuje)“.
- Druh `telemetry`: čte jen to, co hra nebo platforma vydává (UDP port nebo sdílená paměť, kterou hra zveřejňuje), takže zaznamenává i v online hře i offline; příznak rozhoduje jen o tom, zda se paměť smí vůbec číst.
- Paměť: tento adaptér ji **nikdy** nečte. Paměť čtou jen adaptéry `memory`, a nikdy u hry označené jako hraná online - viz [Zdroje a pravidla](sources-and-rules.md).

## Zaznamenané statistiky {#statistics-recorded}

Klíče statistik, které kód tohoto adaptéru nastavuje podle názvu (`stats` každé relace v `meta.json` a tabulka `stats` v `watcher.sqlite`):

`deliveries`, `distance_km`, `fines`, `fines_total`, `jobs_cancelled`, `max_speed_kmh`, `refuels`, `revenue`, `tolls_total`, `xp`

Klíč ve složených závorkách se doplní za běhu (`score.{team}` je jeden klíč pro každý tým). Klíče, které kód bere z tabulky polí hry nebo z jejích vlastních názvů statistik, v tomto seznamu nejsou; výše v „Co se zaznamenává“ jsou uvedeny.

## Úplnost {#completeness}

Watcher se řídí [pravidlem převodníků](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md): co zdroj obsahuje, se přečte nebo uloží, nikdy se nezahodí. Kromě řádků se každý paket, stránka, řádek nebo odpověď, kterou adaptér přijme, uloží celý do `heat.raw.parquet` relace (sloupce `time`, `ms`, `type`, `used`, `payload`, `text` a případná pole uložená podle názvu; `used` označuje, co se také stalo řádky), a `selfCheck.completeness` v `meta.json` počítá každý `type` - `lost` je 0.

**Načteno**

- stav SDK a pauzy, revize pluginu, hra a verze, herní čas, světová pozice a směr kamionu, rychlost, tachometr, značka a název kamionu, náklad, zdrojové a cílové město a firma, odměna za zakázku, XP a vzdálenost, penalizace za zrušení, pokuty a jejich důvod, mýtné, trajekty, vlaky, zvláštní příznaky událostí (řádky, události a statistiky)
- nově také na řádcích pozice: `pitch` a `roll` (stupně, z otáček SDK), `gear` a `rpm`
- offsety ověřené proti ručnímu přepisu hlavičky pluginu revize 12, jehož začátky zón jsou ověřeny v testech; zatím ne proti hře

**Uchováno surové**

- `SCSTelemetry`: celé mapování pluginu o 32 KiB, při každém čtení, jehož bajty se liší od naposledy uložené kopie (`unchanged_reads` v meta.json počítá ostatní), `revision` vedle něj: každá zóna - konfigurace kamionu a přívěsu, kanály kamionu (pedály, řízení, palivo, AdBlue, tlaky, teploty, opotřebení, světla, kola), vektory umístění a zrychlení, řetězce zakázek a hry, a vše, co revize uspořádá za bajtem 4400 (přívěsy); `used` je pravda, dokud je SDK aktivní a revize je 12
- stránka jiné revize pluginu se uloží celá s `used` nepravdivým, místo aby se špatně četla

**Nedostupné**

- cokoli, co plugin z SDK nekopíruje, a vše, dokud plugin není nainstalovaný: hra sama žádnou telemetrii nezveřejňuje
- kamiony jiných hráčů v TruckersMP nebo konvojích: SDK dává jen kamion hráče

**Velikost**: 32 KiB až 10krát za sekundu při jízdě (každé čtení se pak liší): asi 1,2 GB za hodinu před kompresí, jedna kopie při pauze; většina stránky jsou nuly a konfigurace, která se nemění, takže ji zstd zmenší mnohonásobně (na reálné jízdě zatím neměřeno)

## Ověřeno {#verified}

testováno na sdílené paměti sestavené podle layoutu hlavičky pluginu revize 12; zatím neotestováno ve hře

## Zdroj {#source}

[heat3d_watch/adapters/ets2.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/ets2.py)

<!-- Vygenerováno z adaptéru nástrojem tools/gen_game_pages.py; změňte adaptér a spusťte generování znovu, místo úpravy této stránky. -->
