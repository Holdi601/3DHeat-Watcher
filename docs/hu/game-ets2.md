---
title: "Euro Truck Simulator 2 (élő adatok)"
nav_order: 19
lang: "hu"
source: game-ets2.md
source_hash: "537f0daeedbf"
nav_exclude: true
search_exclude: true
---
# Euro Truck Simulator 2 (élő adatok) {#euro-truck-simulator-2-live-data}

Amíg az Euro Truck Simulator 2-t játszod, a watcher elmenti azokat az adatokat, amelyeket maga a játék küld ki, hogy később a 3DHeat-megjelenítőben térképen megnézhesd őket.

*Műszaki részletek: adapter `ets2`, típus [`telemetry`](sources-and-rules.md); fut, amíg az `eurotrucks2.exe` megy, és 0,1 másodpercenként keres új adatot.*

## Mit rögzít {#what-is-recorded}

- a kamion világbeli pozíciója (x keleten, y felfelé, z délen, m) 10 Hz-en mozgás közben, 5 másodpercenként álláskor; irány, sebesség, kilométeróra
- elindított munkák (rakomány, honnan, hová), teljesített munkák (bevétel, XP, km), megszakított munkák; bírságok, útdíjak, komphajók, vonatok, tankolások
- komphajók, vonatok és betöltött mentések megszakítják az útvonalat (teleport, spawn)
- távolság, csúcssebesség, teljesített szállítások, bevétel, XP, bírságok
- a bővítmény teljes osztott memóriája a `heat.raw.parquet` fájlban, minden változáskor

## Honnan származik {#where-it-comes-from}

osztott memória Local\SCSTelemetry, amelyet a RenCloud scs-sdk-plugin ír (12-es revízió) a &lt;game>\bin\win_x64\plugins mappában

## Bekapcsolás {#how-to-switch-it-on}

telepítsd a scs-telemetry.dll fájlt (12-es revízió) a github.com/RenCloud/scs-sdk-plugin oldalról a &lt;game>\bin\win_x64\plugins mappába; a játék minden indításkor egyszer megkérdezi, engedélyezed-e az SDK-t

## Működés {#how-it-works}

Euro Truck Simulator 2 és American Truck Simulator: az SCS telemetriai SDK-ja, a RenCloud bővítményen keresztül.

Az SCS telemetriai SDK-t tesz közzé (<https://modding.scssoft.com/wiki/Documentation/Engine/SDK/Telemetry>) azoknak a bővítményeknek, amelyeket a játékos a `<game>\bin\win_x64\plugins\` mappába tesz. Maga a játék nem tesz közzé semmit; a széles körben használt bővítmény a <https://github.com/RenCloud/scs-sdk-plugin> oldalról (MIT) másolja az SDK csatornáit az osztott memóriába, `Local\SCSTelemetry` néven (32 KiB), amelynek elrendezése a `scs-telemetry/inc/scs-telemetry-common.hpp` fájlban van leírva. Ez a kód ennek az elrendezésnek a 12-es revízióját olvassa (PLUGIN_REVID 12), mást nem: a bővítmény a 40-es bájtnál írja ki a revízióját, és minden más revíziót olvasatlanul hagy, nem pedig félreolvasva. A használt eltolások (a zónák úgy, ahogy a fejléc jelöli őket; természetes igazítás):

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

A kamion világbeli helyzete az SCS világkerete: x keleten, y felfelé, z délen, méterben (jobbkezes, y felfelé - a megjelenítő úgy rajzolja, ahogy van). A komphajók, vonatok és a mentés betöltése úgy mozgatja a kamiont, hogy nem vezet: ott az útvonal megszakad.

A teljes leképezés (a bővítmény 32 KiB-ja: minden fent említett zóna és azok, amelyeket nem olvas - a kamion konfigurációja, kerekek, kopás, a kamion többi csatornája, és amit a revízió a 4400-as bájt után rögzít, a pótkocsik) minden változáskor a munkamenet nyers mellékfájljában marad, `type` `SCSTelemetry` és mellette a `revision` - egy másik revíziójú oldal is így marad meg egészben, nem pedig félreolvasva.

A ugyanez a modul szolgálja ki még: [American Truck Simulator (élő adatok)](game-ats.md).

## Pozíciók és tengelyek {#positions-and-axes}

| | |
|---|---|
| Rögzített pozíciók | igen |
| Felfelé mutató tengely | `y` |
| Mértékegységek | méter (SCS világ: x keleten, y felfelé, z délen) |
| Tükrözés a megjelenítőhöz | nincs |
| Mértékskála (`scale`: a megjelenítő ezzel szorozza a pozíciókat) | 1 |

Ezek minden munkamenet `meta.json` fájljának `axes` mezőjébe kerülnek, és ha a munkamenetnek vannak pozíciói, a `heat.parquet` láblécébe is, így a 3DHeat-megjelenítő magától forgatja és méretezi a sorokat - lásd [Az adatok](the-data.md).

## Többjátékos {#multiplayer}

- Online játékként jelölve (`multiplayer`): **igen**. A `games --markdown` ezt "engedélyezett (csak azt olvassa, amit a játék közzétesz)" formában mutatja.
- `telemetry` típus: csak azt olvassa, amit a játék vagy a platform kiad (a játék által közzétett UDP-port vagy osztott memória), ezért online játékban is rögzít, nem csak offline; a jelző csak azt dönti el, szabad-e egyáltalán memóriát olvasni.
- Memória: ez az adapter **soha** nem olvas memóriát. Csak a `memory` típusú adapterek olvasnak memóriát, és soha nem olyan játékhoz, amely online játékként van megjelölve - lásd [Forrásak és szabályok](sources-and-rules.md).

## Rögzített statisztikák {#statistics-recorded}

Azok a statisztikakulcsok, amelyeket ez az adapter kódja név szerint állít be (minden munkamenet `stats` mezője a `meta.json`-ban és a `watcher.sqlite` `stats` táblájában):

`deliveries`, `distance_km`, `fines`, `fines_total`, `jobs_cancelled`, `max_speed_kmh`, `refuels`, `revenue`, `tolls_total`, `xp`

A kapcsos zárójeles kulcsot futásidőben töltik ki (a `score.{team}` csapatonként egy kulcs). Azok a kulcsok, amelyeket a kód a játék mezőinek táblázatából vagy a játék saját statisztikanevei közül vesz, nincsenek ebben a listában; a fenti "Mit rögzít" rész nevezi meg őket.

## Teljesség {#completeness}

A watcher követi a 3DHeat [konvertáló szabályát](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md): amit a forrás tartalmaz, azt beolvassa vagy megőrzi, sosem dobja el. A sorokon kívül minden csomagot, oldalt, sort vagy választ, amelyet az adapter kap, egészben megőriz a munkamenet `heat.raw.parquet` fájlja (oszlopok: `time`, `ms`, `type`, `used`, `payload`, `text`, majd minden név szerint megtartott mező; a `used` jelöli, ami sorrá is vált), és a `meta.json` `selfCheck.completeness` mezője minden `type` értéket megszámol - a `lost` értéke 0.

**Beolvasva**

- SDK- és szüneteltetési állapot, bővítmény-revízió, játék és verzió, játékbeli idő, a kamion világbeli pozíciója és iránya, sebesség, kilométeróra, a kamion márkája és neve, rakomány, forrás- és célváros és cég, munka bevétele, XP és távolsága, a megszakítási büntetés, bírságok és azok oka, útdíjak, komphajók, vonatok, a különleges eseményjelzők (sorok, események és statisztikák)
- most már a pozíciósorokon is: `pitch` és `roll` (fokban, az SDK fordulataiból), `gear` és `rpm`
- az eltolások a bővítmény 12-es revíziós fejlécének mezőnkénti átírásával vannak ellenőrizve, a zónák kezdeteit a tesztek állítják; még nem a játékon

**Nyersen megőrizve**

- `SCSTelemetry`: a bővítmény teljes 32 KiB-os leképezése, minden olyan olvasás, amelynek bájtjai eltérnek az utoljára megőrzött másolattól (a meta.json `unchanged_reads` a többit számolja), mellette a `revision`: minden zóna - a kamion és a pótkocsi konfigurációja, a kamion csatornái (pedálok, kormány, üzemanyag, AdBlue, nyomások, hőmérsékletek, kopás, lámpák, kerekek), a helyzet- és gyorsulásvektorok, a munka- és játékszövegek, és minden, amit a revízió a 4400-as bájt után rögzít (a pótkocsik); a `used` akkor igaz, ha az SDK aktív és a revízió 12
- más bővítmény-revíziós oldal egészben, `used` értékkel hamis marad meg, nem pedig félreolvasva

**Nem elérhető**

- minden, amit a bővítmény nem másol ki az SDK-ból, és minden, amíg a bővítmény nincs telepítve: a játék maga nem tesz közzé telemetriát
- más játékosok kamionjai a TruckersMP-ben vagy konvojokban: az SDK csak a játékos saját kamionját adja

**Méret**: 32 KiB legfeljebb másodpercenként 10-szer vezetés közben (akkor minden olvasás eltér): tömörítés előtt óránként körülbelül 1,2 GB, szüneteltetve egy másolat; az oldal nagy része nulla és olyan konfiguráció, amely nem változik, ezért a zstd sokszorosára csökkenti (valódi munkamenetben még nem mérték)

## Ellenőrzés {#verified}

a bővítmény 12-es revíziós fejléce alapján épített osztott memórián tesztelve; a játékon nincs tesztelve

## Forrás {#source}

[heat3d_watch/adapters/ets2.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/ets2.py)

<!-- Generated from the adapter by tools/gen_game_pages.py; change the adapter and run it again rather than editing this page. -->
