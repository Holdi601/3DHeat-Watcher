---
title: "Assetto Corsa EVO (élő adatok)"
nav_order: 4
lang: "hu"
source: game-assetto-corsa-evo.md
source_hash: "b14d46c10e85"
nav_exclude: true
search_exclude: true
---
# Assetto Corsa EVO (élő adatok) {#assetto-corsa-evo-live-data}

Amíg az Assetto Corsa EVO-t játszod, a watcher elmenti azokat az adatokat, amelyeket maga a játék küld ki, hogy később a 3DHeat-megjelenítőben térképen megnézhesd őket.

*Műszaki részletek: adapter `assetto-corsa-evo`, típus [`telemetry`](sources-and-rules.md); fut, amíg az `AssettoCorsaEVO.exe` megy, és 0,1 másodpercenként keres új adatot.*

## Mit rögzít {#what-is-recorded}

- a saját autó pozíciója (világ XYZ, m: a gumiabroncsok érintkezési pontjainak átlaga) 10 Hz-en, a sebességgel, fokozattal, gázzal, fékkel
- a munkamenet kezdete és vége a játék által megnevezett pályával és autóval
- körök, amikor az autó áthalad azon a helyen, ahol a rajt volt, ugyanabba az irányba haladva
- teleportálások (vissza a boxba, újraindítás): `teleport` ahol az autó volt, `spawn` ahol most van
- körök, legjobb kör, távolság, csúcssebesség

## Honnan származik {#where-it-comes-from}

osztott memória Local\acevo_pmf_physics, Local\acevo_pmf_static

## Bekapcsolás {#how-to-switch-it-on}

Semmit sem kell bekapcsolni: a watcher úgy olvassa a forrást, ahogy a játék vagy a platform biztosítja.

## Működés {#how-it-works}

A versenyjátékok saját telemetriája: a Forza, az Assetto Corsa játékok, a ralijátékok és a BeamNG, útvonalként, körökként és szakaszokként rögzítve.

Minden itt szereplő játék szándékosan teszi közzé a telemetriáját műszerfalaknak és mozgásszimulátoroknak; semmi nincs beillesztve, és a játék által ki nem adott adat sem olvasható. A dekódolás nincs kétszer megírva: ez a gamecapture köridő-rögzítőinek kódja a 3DHeat GameCapture `heat3d_capture/telemetry` mappájából, átmásolva a `heat3d_watch/decoders` mappába (ott a közzétett elrendezések alapján készült csomagokon tesztelve), és ez a modul ezek kockáit a watcher sorainak alakítja: az autó pozíciója másodpercenként többször a sebességével, fokozatával és pedáljaival, egy esemény körönként vagy szakaszonként, valamint a versenyző számai: körök, legjobb kör, távolság, csúcssebesség.

#### Forza (Horizon 4/5/6, Motorsport) {#forza-horizon-456-motorsport}

"Data Out" UDP, a játék HUD- és játékbeállításaiban kapcsolható be, a 127.0.0.1 címre, 5300-as porton, Dash formátumban. Minden szimulációs ciklusban egy csomag; a dash-blokk eltolását a csomagokból találja meg a `forza.detect_layout`. Világ méterben, Y felfelé; a világ balkezes, és úgy rajzolódik ki, ahogy érkezik, ahogy a köridő-rögzítő is teszi (a Forza Motorsport és a Forza Horizon "Data Out" dokumentációja szerint). A játék egy portra küld, és az FH Companion meg más Data Out alkalmazások is ugyanezen hallgatnak. Két program nem oszthatja meg: Windowson a 127.0.0.1-hez kötött socket kapja a csomagokat, az összes címre kötött socket ugyanazon a porton pedig egyet sem, attól függetlenül, melyik indult előbb. Ezért a watcher egy kicsit vár, miután a játék elindult, mielőtt elfoglalja a portot, sosem veszi el egy alkalmazástól, amely már tartja, és azonnal elengedi, amint egy másik alkalmazás hallgatni kezd rajta. Miközben tartja a portot, minden csomagot változatlanul továbbít a 127.0.0.1:5301 címre - állítsd az FH Companion port mezőjét (a telemetria fülén) 5301-re, és mindkettő rögzít.

#### Minden megőrizve {#everything-kept}

A sorok másodpercenként néhányan vannak; a játékok ennél sokkal többet küldenek. Minden UDP-csomag, amely megérkezik - a menükben, köridők között, a dekódolók által nem olvasottak is -, egészben megmarad a munkamenet `heat.raw.parquet` fájljában a formátuma szerinti néven (`dash-horizon`, `session_update`, `extradata3`, `H3D1`, ...), és minden osztott memóriaoldal (az egész leképezés, nem csak a dekódolt bájtok) minden változáskor, a leképezés nevén (`acpmf_physics`, ...). A `used` jelöli azt, ami sorrá is vált; a `meta.json` `selfCheck.completeness` mezője fajtánként megszámolja (a 3DHeat konvertáló szabálya szerint).

A ugyanez a modul szolgálja ki még: [Assetto Corsa (élő adatok)](game-assetto-corsa.md), [Assetto Corsa Competizione (élő adatok)](game-assetto-corsa-competizione.md), [Assetto Corsa Rally (élő adatok)](game-assetto-corsa-rally.md), [BeamNG.drive (élő adatok)](game-beamng.md), [DiRT Rally 2.0 (élő adatok)](game-dirt-rally-2.md), [EA SPORTS WRC (élő adatok)](game-ea-wrc.md), [Forza Horizon 4 (élő adatok)](game-forza-horizon-4.md), [Forza Horizon 5 (élő adatok)](game-forza-horizon-5.md), [Forza Horizon 6 (élő adatok)](game-forza-horizon-6.md), [Forza Motorsport (élő adatok)](game-forza-motorsport.md), [Richard Burns Rally (élő adatok)](game-richard-burns-rally.md).

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

`best_lap`, `best_stage`, `distance_km`, `laps`, `race_position`, `stages`, `top_speed_kmh`

A kapcsos zárójeles kulcsot futásidőben töltik ki (a `score.{team}` csapatonként egy kulcs). Azok a kulcsok, amelyeket a kód a játék mezőinek táblázatából vagy a játék saját statisztikanevei közül vesz, nincsenek ebben a listában; a fenti "Mit rögzít" rész nevezi meg őket.

## Teljesség {#completeness}

A watcher követi a 3DHeat [konvertáló szabályát](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md): amit a forrás tartalmaz, azt beolvassa vagy megőrzi, sosem dobja el. A sorokon kívül minden csomagot, oldalt, sort vagy választ, amelyet az adapter kap, egészben megőriz a munkamenet `heat.raw.parquet` fájlja (oszlopok: `time`, `ms`, `type`, `used`, `payload`, `text`, majd minden név szerint megtartott mező; a `used` jelöli, ami sorrá is vált), és a `meta.json` `selfCheck.completeness` mezője minden `type` értéket megszámol - a `lost` értéke 0.

**Beolvasva**

- sorok 10 Hz-en a fizikai oldalról: pozíció (a gumiabroncsok érintkezési pontjainak átlaga), sebesség, fokozat, gáz, fék, yaw/pitch/roll (rad), fordulatszám, kormány (ahogy az oldal tartalmazza); munkamenet kezdete a pályával és az autóval a statikus oldalról; körök, versenyben elfoglalt helyezés

**Nyersen megőrizve**

- minden oldal egészben - a teljes leképezési tartomány, nem csak a dekódolt bájtok - minden alkalommal, amikor a bájtjai változnak, a watcher 10 Hz-es olvasásánál: `acevo_pmf_physics`, `acevo_pmf_static`; a bájtra pontosan az előzővel egyező újraolvasás a meta.json `unchanged_reads` mezőjében számolódik, nem tárolódik újra
- minden, amit csak köridő-fájlokhoz dekódolnak (`decoders/kunos.py`: kerekenkénti csúszás, terhelés, nyomás, hőmérséklet, dőlés, felfüggesztés, érintkezési pontok, fék-hőmérsékletek, csúszási arány és szög; világ- és helyi sebesség, szögsebesség, segédek) ezeken az oldalakon van

**Nem elérhető**

- más autók pozíciói: az oldalak csak a játékos autóját írják le (az ACC grafikai oldala egyes verziókban más autók azonosítóit és koordinátáit is tartalmazza - a nyers oldalon megőrizve, nincs dekódolva)
- fizikai ciklusok az watcher olvasásai között: a játék a fizikai sebességén írja át az oldalt (legfeljebb 333 Hz), a watcher pedig másodpercenként 10-szer olvas
- körszámláló vagy a játék köridője: az AC EVO eddig olvasott oldalai között nincs grafikai oldal; a köröket pozíció alapján osztja fel

**Méret**: óránként körülbelül 150-300 MB tömörítés előtt (oldalanként 4 KB-os tartomány legfeljebb másodpercenként 10 változással); az oldalak nagyrészt nullák, és a zstd csak töredéküket tartja meg

## Ellenőrzés {#verified}

a dekódolás a gamecapture köridő-rögzítőjéé (szintetikus oldalakon tesztelve); az adapter olyan osztott memórián tesztelve, amelyet a teszt a dokumentált elrendezés alapján épített; a játékon nincs tesztelve; a végrehajtható fájl neve játékosok beszámolóiból származik

## Forrás {#source}

[heat3d_watch/adapters/racing.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/racing.py)

<!-- Generated from the adapter by tools/gen_game_pages.py; change the adapter and run it again rather than editing this page. -->
