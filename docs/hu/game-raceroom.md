---
title: "RaceRoom Racing Experience (élő adatok)"
nav_order: 38
lang: "hu"
source: game-raceroom.md
source_hash: "ffd0499ca059"
nav_exclude: true
search_exclude: true
---
# RaceRoom Racing Experience (élő adatok) {#raceroom-racing-experience-live-data}

Amíg a RaceRoom Racing Experience-t játszod, a watcher elmenti azokat az adatokat, amelyeket maga a játék küld ki, hogy később a 3DHeat-megjelenítőben térképen megnézhesd őket.

*Műszaki részletek: adapter `raceroom`, típus [`telemetry`](sources-and-rules.md); fut, amíg a `RRRE64.exe` vagy a `RRRE.exe` megy, és 0,1 másodpercenként keres új adatot.*

## Mit rögzít {#what-is-recorded}

- minden autó pozíciója (világ XYZ, m) 10 Hz-en, a versenyző neve szerint, a saját autó megjelölve, sebességgel és versenyben elfoglalt helyezéssel; a saját fokozat, gáz, fék
- a munkamenet kezdete a játék által megnevezett pályával; autónként körök a köridővel; célba érések; a saját boxkiállások
- teleportálások (vissza a boxba, újraindítás): `teleport` ahol az autó volt, `spawn` ahol most van
- saját körök, legjobb kör, versenyben elfoglalt helyezés, távolság, csúcssebesség
- a játék teljes osztott memóriaoldala a `heat.raw.parquet` fájlban, minden változáskor
- a saját incidenspontok

## Honnan származik {#where-it-comes-from}

osztott memória $R3E (Sector3 r3e.h, 3-as verzió)

## Bekapcsolás {#how-to-switch-it-on}

Semmit sem kell bekapcsolni: a watcher úgy olvassa a forrást, ahogy a játék vagy a platform biztosítja.

## Működés {#how-it-works}

Osztott memória, amelyet a versenyjátékok a műszerfalaknak tesznek közzé, csak olvasásra megnyitva - és sosem hozzák létre.

Több szimulátor a telemetriáját olyan nevesített Windows-fájlleképezésként adja ki, amelyet a játék hoz létre, és bárki olvashat: Kunos `Local\acpmf_*` oldalai (Assetto Corsa, ACC, AC Rally, az AC EVO `Local\acevo_pmf_*` oldalai), az iRacing `Local\IRSDKMemMapFileName`, a RaceRoom `$R3E`, az Automobilista 2 / Project CARS 2 `$pcars2$`.

Miért nem az `mmap.mmap(-1, size, tagname=...)`, amely a szokásos Python-módszer: ha a leképezés még nem létezik, *létrehozza* - itt csak olvasásra. Egy később elindított játék a watcher leképezését nyitja meg a saját létrehozása helyett, és nem tud írni bele, így a telemetriája addig halott, amíg a watcher el nem engedi. A watcher akkor indít adaptert, amikor a játék folyamata megjelenik, pontosan abban a pillanatban, amikor a játék még nem hozta létre a leképezését. Ezért ez az `OpenFileMappingW`-vel nyit, amely csak létező leképezést talál meg, `FILE_MAP_READ` jogosultsággal képezi le, és egyébként "még nincs" választ ad; az adapterek egy kis idő múlva újra próbálkoznak.

Semmi itt nem tud írni: a nézet csak olvasásra van leképezve, és csak `ctypes.string_at`-tal másolják ki belőle.

Két játék itt is olvasott: minden pályán lévő autó bennük van.

#### RaceRoom Racing Experience - `$R3E` {#raceroom-racing-experience---r3e}

Sector3 `r3e.h` (github.com/sector3studios/r3e-api, sample-c/src/r3e.h, 3.6-os verzió), `#pragma pack(1)`. A fejléc megmondja, hol kezdődnek a versenyzők és mekkora egyenként (`all_drivers_offset`, `driver_data_size`), így a versenyzőnkénti rész - név, slot, helyezés, világ pozíció (float x y z, m), teljesített körök, aktuális köridő, célbaérés állapota, boxsáv, sebesség - ezek alapján olvasódik. A játékos saját mezői (a legjobb és az előző kör, versenyben elfoglalt helyezés, incidenspontok, fokozat, pedálok, pálya- és elrendezésnevek) csak akkor olvashatók a 3.6-os eltolásaikon, ha az `all_drivers_offset` az az 2008-as érték, amelyre az elrendezés teszi. Az Y-t felfelé mutatónak vesszük; a fejléc ezt nem mondja meg.

A ugyanez a modul szolgálja ki még: [Automobilista 2 (élő adatok)](game-automobilista-2.md), [Project CARS 2 (élő adatok)](game-project-cars-2.md).

## Pozíciók és tengelyek {#positions-and-axes}

| | |
|---|---|
| Rögzített pozíciók | igen |
| Felfelé mutató tengely | `y` |
| Mértékegységek | méter; Y felfelé feltételezve (az r3e.h nem mondja meg) |
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

- versenyzőhelyenként (a fejléc saját eltolása és mérete szerint): név, slot, célbaérés állapota, helyezés, világ pozíció, teljesített körök, aktuális köridő, boxsáv, sebesség
- a játékos saját mezői, csak akkor, ha az oldal az r3e.h 3.6-os elrendezésű: pálya- és elrendezésnevek, munkamenet-típus, versenyben elfoglalt helyezés, legjobb és előző kör, incidenspontok, fokozat, gáz, fék, a játékos slotja
- az eltolások Sector3 r3e.h 3.6-os verziójából lettek kidolgozva, és a tesztekben az abból épített oldalon ellenőrizve; még nem a játékon

**Nyersen megőrizve**

- `r3e`: a teljes $R3E leképezés, minden olyan olvasás, amelynek bájtjai eltérnek az utoljára megőrzött másolattól - az r3e.h minden mezője: a játékos fizikája (tájolás, sebességek, gyorsulások, g-erők), motor, üzemanyag, gumik, fékek, sérülések, jelzők, boxmenü, szektoridők, minden versenyzőhely teljes versenyzőadata (osztály, modell, csapat, szektoridők, hátrányok, büntetések, gumik)
- a `used` igaz, ha az oldal be lett olvasva sorokba; hamis a menüben, szünetelve, visszajátszásban, más elrendezésű vagy írás közben elkapott (`torn` 1) oldalnál; a meta.json `unchanged_reads` számolja azokat az olvasásokat, amelyek bájtra pontosan megegyeznek a korábban megőrzött másolattal

**Nem elérhető**

- más versenyzők bemenetei és fizikája: az oldal csak a játékosét adja
- más autók pontos köridői: egy slotnak csak a futó köridője van, ezért a kör az utolsó látott futó idő (kb. 0,1 másodpercig pontos)
- a játékos saját mezői a 3.6-tól eltérő elrendezésen: nyersen megőrizve, nem olvasva, amíg nincs ellenőrizve

**Méret**: az oldal 44 KB (r3e.h 3.6; a leképezés a teljes 4 KB-os oldalakra kerekítve), vezetés közben legfeljebb másodpercenként 10-szer: tömörítés előtt nagyjából óránként 1,6 GB; az üres versenyzőslotok és a változatlan mezők a zstd-vel nagyon jól tömörülnek (valódi munkamenetben még nem mérték)

## Ellenőrzés {#verified}

a tesztben épített oldalon tesztelve, az r3e.h 3.6-os verziójából (az eltolások a hivatalos fejlécből lettek kidolgozva); a játékon nincs tesztelve; más autók köridői a látott utolsó futó köridő (kb. 0,1 másodpercig pontos)

## Forrás {#source}

[heat3d_watch/adapters/simracing_shm.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/simracing_shm.py)

<!-- Generated from the adapter by tools/gen_game_pages.py; change the adapter and run it again rather than editing this page. -->
