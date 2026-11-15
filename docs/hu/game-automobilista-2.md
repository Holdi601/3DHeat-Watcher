---
title: "Automobilista 2 (élő adatok)"
nav_order: 6
lang: "hu"
source: game-automobilista-2.md
source_hash: "5e3ca1507524"
nav_exclude: true
search_exclude: true
---
# Automobilista 2 (élő adatok) {#automobilista-2-live-data}

Amíg az Automobilista 2-t játszod, a watcher elmenti azokat az adatokat, amelyeket maga a játék küld ki, hogy később a 3DHeat-megjelenítőben térképen megnézhesd őket.

*Műszaki részletek: adapter `automobilista-2`, típus [`telemetry`](sources-and-rules.md); fut, amíg az `AMS2AVX.exe` vagy az `AMS2.exe` megy, és 0,1 másodpercenként keres új adatot.*

## Mit rögzít {#what-is-recorded}

- minden autó pozíciója (világ XYZ, m) 10 Hz-en, a versenyző neve szerint, a saját autó megjelölve, sebességgel és versenyben elfoglalt helyezéssel; a saját fokozat, gáz, fék
- a munkamenet kezdete a játék által megnevezett pályával; autónként körök a köridővel; célba érések; a saját boxkiállások
- teleportálások (vissza a boxba, újraindítás): `teleport` ahol az autó volt, `spawn` ahol most van
- saját körök, legjobb kör, versenyben elfoglalt helyezés, távolság, csúcssebesség
- a játék teljes osztott memóriaoldala a `heat.raw.parquet` fájlban, minden változáskor

## Honnan származik {#where-it-comes-from}

osztott memória $pcars2$ (SMS SharedMemory.h elrendezés)

## Bekapcsolás {#how-to-switch-it-on}

A játékban: Beállítások > Rendszer > Osztott memória: "Project CARS 2"

## Működés {#how-it-works}

Osztott memória, amelyet a versenyjátékok a műszerfalaknak tesznek közzé, csak olvasásra megnyitva - és sosem hozzák létre.

Több szimulátor a telemetriáját olyan nevesített Windows-fájlleképezésként adja ki, amelyet a játék hoz létre, és bárki olvashat: Kunos `Local\acpmf_*` oldalai (Assetto Corsa, ACC, AC Rally, az AC EVO `Local\acevo_pmf_*` oldalai), az iRacing `Local\IRSDKMemMapFileName`, a RaceRoom `$R3E`, az Automobilista 2 / Project CARS 2 `$pcars2$`.

Miért nem az `mmap.mmap(-1, size, tagname=...)`, amely a szokásos Python-módszer: ha a leképezés még nem létezik, *létrehozza* - itt csak olvasásra. Egy később elindított játék a watcher leképezését nyitja meg a saját létrehozása helyett, és nem tud írni bele, így a telemetriája addig halott, amíg a watcher el nem engedi. A watcher akkor indít adaptert, amikor a játék folyamata megjelenik, pontosan abban a pillanatban, amikor a játék még nem hozta létre a leképezését. Ezért ez az `OpenFileMappingW`-vel nyit, amely csak létező leképezést talál meg, `FILE_MAP_READ` jogosultsággal képezi le, és egyébként "még nincs" választ ad; az adapterek egy kis idő múlva újra próbálkoznak.

Semmi itt nem tud írni: a nézet csak olvasásra van leképezve, és csak `ctypes.string_at`-tal másolják ki belőle.

Két játék itt is olvasott: minden pályán lévő autó bennük van.

#### Automobilista 2 / Project CARS 2 - `$pcars2$` {#automobilista-2--project-cars-2---pcars2}

SMS `SharedMemory.h` (a játék Support\SharedMemory mappájában található; AMS2: Beállítások > Rendszer > Osztott memória "Project CARS 2"), `#pragma pack(4)`. A `mParticipantInfo[64]` a 28-as bájttól kezdődik, résztvevőnként 100 bájt: mIsActive, mName[64], mWorldPosition[3] (m, Y felfelé), mCurrentLapDistance, mRacePosition, mLapsCompleted, mCurrentLap, mCurrentSector; a mViewedParticipantIndex (20) a játékos autója; résztvevőnként mLastLapTimes (9200), mRaceStates (9520), mSpeeds (10800); a játékos mBestLapTime (6716), mLastLapTime (6720), mSpeed (6848), mBrake, mThrottle, mGear; az mSequenceNumber (7320) páratlan, amíg a játék ír. Az eltolásokat a fejléc két, egymástól független másolatából dolgozták ki (a játék saját másolata itt nincs telepítve), és ezek egyeznek.

Mindkét oldal egészben is megmarad (docs/converters.md, "Live sources"): a teljes leképezés, minden olyan olvasás, amelynek bájtjai eltérnek az utoljára megőrzött másolattól, a munkamenet nyers mellékfájljában `type` `r3e` vagy `pcars2` alatt - minden résztvevői hely és a struktúra minden mezője, azok is, amelyeket itt nem olvas, így egy későbbi dekóderhez csak a mellékfájl kell.

A ugyanez a modul szolgálja ki még: [Project CARS 2 (élő adatok)](game-project-cars-2.md), [RaceRoom Racing Experience (élő adatok)](game-raceroom.md).

## Pozíciók és tengelyek {#positions-and-axes}

| | |
|---|---|
| Rögzített pozíciók | igen |
| Felfelé mutató tengely | `y` |
| Mértékegységek | méter |
| Tükrözés a megjelenítőhöz | nincs |
| Mértékskála (`scale`: a megjelenítő ezzel szorozza a pozíciókat) | 1 |

Ezek minden munkamenet `meta.json` fájljának `axes` mezőjébe kerülnek, és ha a munkamenetnek vannak pozíciói, a `heat.parquet` láblécébe is, így a 3DHeat-megjelenítő magától forgatja és méretezi a sorokat - lásd [Az adatok](the-data.md).

## Többjátékos {#multiplayer}

- Online játékként jelölve (`multiplayer`): **igen**. A `games --markdown` ezt "engedélyezett (csak azt olvassa, amit a játék közzétesz)" formában mutatja.
- `telemetry` típus: csak azt olvassa, amit a játék vagy a platform kiad (a játék által közzétett UDP-port vagy osztott memória), ezért online játékban is rögzít, nem csak offline; a jelző csak azt dönti el, szabad-e egyáltalán memóriát olvasni.
- Memória: ez az adapter **soha** nem olvas memóriát. Csak a `memory` típusú adapterek olvasnak memóriát, és soha nem olyan játékhoz, amely online játékként van megjelölve - lásd [Forrásak és szabályok](sources-and-rules.md).

## Rögzített statisztikák {#statistics-recorded}

Azok a statisztikakulcsok, amelyeket ez az adapter kódja név szerint állít be (minden munkamenet `stats` mezője a `meta.json`-ban és a `watcher.sqlite` `stats` táblájában):

`best_lap`, `distance_km`, `finishes`, `incidents`, `laps`, `pit_stops`, `race_position`, `top_speed_kmh`

A kapcsos zárójeles kulcsot futásidőben töltik ki (a `score.{team}` csapatonként egy kulcs). Azok a kulcsok, amelyeket a kód a játék mezőinek táblázatából vagy a játék saját statisztikanevei közül vesz, nincsenek ebben a listában; a fenti "Mit rögzít" rész nevezi meg őket.

## Teljesség {#completeness}

A watcher követi a 3DHeat [konvertáló szabályát](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md): amit a forrás tartalmaz, azt beolvassa vagy megőrzi, sosem dobja el. A sorokon kívül minden csomagot, oldalt, sort vagy választ, amelyet az adapter kap, egészben megőriz a munkamenet `heat.raw.parquet` fájlja (oszlopok: `time`, `ms`, `type`, `used`, `payload`, `text`, majd minden név szerint megtartott mező; a `used` jelöli, ami sorrá is vált), és a `meta.json` `selfCheck.completeness` mezője minden `type` értéket megszámol - a `lost` értéke 0.

**Beolvasva**

- résztvevőnként (legfeljebb 64): aktív, név, világ pozíció, versenyben elfoglalt helyezés, teljesített körök; utolsó köridő, versenyállapot és sebesség
- a játékos autója (mViewedParticipantIndex), játék- és munkamenet-állapot, pálya helye és változata, legjobb és utolsó kör, sebesség, fék, gáz, fokozat; az mSequenceNumber átugorja az írás közben elkapott másolatot
- az eltolások SMS SharedMemory.h két egymástól független, egyező másolatából, a tesztekben az ezek alapján épített oldalon ellenőrizve; még nem a játékon

**Nyersen megőrizve**

- `pcars2`: a teljes $pcars2$ leképezés - a struktúra jóval túlmegy az itt olvasott 11 312 bájton -, minden olyan olvasás, amelynek bájtjai eltérnek az utoljára megőrzött másolattól: minden résztvevő tájolása, szektoridők, autó- és osztálynevek, boxmódok és jelzők, a játékos fizikája, gumijai, felfüggesztése, sérülései, időjárása, és minden később az Automobilista 2 verziókba került adat
- a `used` igaz, ha az oldal be lett olvasva sorokba; hamis a menüben, szünetelve, visszajátszásban, más elrendezésű vagy írás közben elkapott (`torn` 1) oldalnál; a meta.json `unchanged_reads` számolja azokat az olvasásokat, amelyek bájtra pontosan megegyeznek a korábban megőrzött másolattal

**Nem elérhető**

- más résztvevők bemenetei és fizikája: az oldal csak a megtekintett autóét adja
- minden, amíg a játék osztott memória beállítása ki van kapcsolva (az Automobilista 2 ilyenkor nem ír semmit)

**Méret**: a leképezés a játék verziójától függően 20-30 KB, vezetés közben legfeljebb másodpercenként 10-szer: tömörítés előtt nagyjából óránként 0,7-1,1 GB; a zstd a üres résztvevői helyeket és a változatlan neveket töredékére csökkenti (valódi munkamenetben még nem mérték)

## Ellenőrzés {#verified}

a tesztben épített oldalon tesztelve; az eltolások az SharedMemory.h két független másolatából, nem a játék által szállított példányból; a játékon nincs tesztelve

## Forrás {#source}

[heat3d_watch/adapters/simracing_shm.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/simracing_shm.py)

<!-- Generated from the adapter by tools/gen_game_pages.py; change the adapter and run it again rather than editing this page. -->
