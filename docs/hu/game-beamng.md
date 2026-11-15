---
title: "BeamNG.drive (élő adatok)"
nav_order: 7
lang: "hu"
source: game-beamng.md
source_hash: "1c23a869a62f"
nav_exclude: true
search_exclude: true
---
# BeamNG.drive (élő adatok) {#beamngdrive-live-data}

Amíg a BeamNG.drive-ot játszod, a watcher elmenti azokat az adatokat, amelyeket maga a játék küld ki, hogy később a 3DHeat-megjelenítőben térképen megnézhesd őket.

*Műszaki részletek: adapter `beamng`, típus [`telemetry`](sources-and-rules.md); fut, amíg a `BeamNG.drive.x64.exe` vagy a `BeamNG.drive.exe` megy, és 0,1 másodpercenként keres új adatot.*

## Mit rögzít {#what-is-recorded}

- a saját autó pozíciója (világ, m, Y felfelé fordítva) 10 Hz-en, a sebességgel, fokozattal, gázzal, fékkel
- vezetés kezdete, visszaállítások (újraéledés), a vezetés kezdetén túli körök
- körök, legjobb kör, távolság, csúcssebesség

## Honnan származik {#where-it-comes-from}

UDP 127.0.0.1:4460 a heat3d protokollmódból (ez a repó mods/beamng/heat3d mappájában)

## Bekapcsolás {#how-to-switch-it-on}

`python -m heat3d_watch setup beamng --apply` telepíti a módot; utána Beállítások > Egyéb > Protokollok > "others"

Írd be a parancsot a watcher mappájában megnyitott terminálba (lásd [Mielőtt elkezdenéd](before-you-start.md)). Ha hibát jelez, az utolsó sor megmondja, miért; az [Telepítés és futtatás](installing-and-running.md) a szokásos okokat írja le.

`python -m heat3d_watch setup beamng` felsorolja a fájlokat, amelyeket módosítana; a `python -m heat3d_watch setup beamng --apply` megváltoztatja őket, az eredetit `<file>.heat3d-backup` néven megtartva (lásd [Parancsok](commands.md#setup)). Minden változásra kiírja a `beamng: changed: ...` sort, vagy a `beamng: nothing to change` sort, ha már be van kapcsolva.

## Működés {#how-it-works}

A versenyjátékok saját telemetriája: a Forza, az Assetto Corsa játékok, a ralijátékok és a BeamNG, útvonalként, körökként és szakaszokként rögzítve.

Minden itt szereplő játék szándékosan teszi közzé a telemetriáját műszerfalaknak és mozgásszimulátoroknak; semmi nincs beillesztve, és a játék által ki nem adott adat sem olvasható. A dekódolás nincs kétszer megírva: ez a gamecapture köridő-rögzítőinek kódja a 3DHeat GameCapture `heat3d_capture/telemetry` mappájából, átmásolva a `heat3d_watch/decoders` mappába (ott a közzétett elrendezések alapján készült csomagokon tesztelve), és ez a modul ezek kockáit a watcher sorainak alakítja: az autó pozíciója másodpercenként többször a sebességével, fokozatával és pedáljaival, egy esemény körönként vagy szakaszonként, valamint a versenyző számai: körök, legjobb kör, távolság, csúcssebesség.

#### Forza (Horizon 4/5/6, Motorsport) {#forza-horizon-456-motorsport}

"Data Out" UDP, a játék HUD- és játékbeállításaiban kapcsolható be, a 127.0.0.1 címre, 5300-as porton, Dash formátumban. Minden szimulációs ciklusban egy csomag; a dash-blokk eltolását a csomagokból találja meg a `forza.detect_layout`. Világ méterben, Y felfelé; a világ balkezes, és úgy rajzolódik ki, ahogy érkezik, ahogy a köridő-rögzítő is teszi (a Forza Motorsport és a Forza Horizon "Data Out" dokumentációja szerint). A játék egy portra küld, és az FH Companion meg más Data Out alkalmazások is ugyanezen hallgatnak. Két program nem oszthatja meg: Windowson a 127.0.0.1-hez kötött socket kapja a csomagokat, az összes címre kötött socket ugyanazon a porton pedig egyet sem, attól függetlenül, melyik indult előbb. Ezért a watcher egy kicsit vár, miután a játék elindult, mielőtt elfoglalja a portot, sosem veszi el egy alkalmazástól, amely már tartja, és azonnal elengedi, amint egy másik alkalmazás hallgatni kezd rajta. Miközben tartja a portot, minden csomagot változatlanul továbbít a 127.0.0.1:5301 címre - állítsd az FH Companion port mezőjét (a telemetria fülén) 5301-re, és mindkettő rögzít.

#### BeamNG.drive {#beamngdrive}

A `heat3d` protokollmód, amelyet a gamecapture szállít (UDP 4460, Beállítások > Egyéb > Protokollok > "others"); a BeamNG Z felfelé mutató világa Y felfelé fordítva, ahogy a `beamng.py` teszi.

#### Minden megőrizve {#everything-kept}

A sorok másodpercenként néhányan vannak; a játékok ennél sokkal többet küldenek. Minden UDP-csomag, amely megérkezik - a menükben, köridők között, a dekódolók által nem olvasottak is -, egészben megmarad a munkamenet `heat.raw.parquet` fájljában a formátuma szerinti néven (`dash-horizon`, `session_update`, `extradata3`, `H3D1`, ...), és minden osztott memóriaoldal (az egész leképezés, nem csak a dekódolt bájtok) minden változáskor, a leképezés nevén (`acpmf_physics`, ...). A `used` jelöli azt, ami sorrá is vált; a `meta.json` `selfCheck.completeness` mezője fajtánként megszámolja (a 3DHeat konvertáló szabálya szerint).

A ugyanez a modul szolgálja ki még: [Assetto Corsa (élő adatok)](game-assetto-corsa.md), [Assetto Corsa Competizione (élő adatok)](game-assetto-corsa-competizione.md), [Assetto Corsa EVO (élő adatok)](game-assetto-corsa-evo.md), [Assetto Corsa Rally (élő adatok)](game-assetto-corsa-rally.md), [DiRT Rally 2.0 (élő adatok)](game-dirt-rally-2.md), [EA SPORTS WRC (élő adatok)](game-ea-wrc.md), [Forza Horizon 4 (élő adatok)](game-forza-horizon-4.md), [Forza Horizon 5 (élő adatok)](game-forza-horizon-5.md), [Forza Horizon 6 (élő adatok)](game-forza-horizon-6.md), [Forza Motorsport (élő adatok)](game-forza-motorsport.md), [Richard Burns Rally (élő adatok)](game-richard-burns-rally.md).

## Pozíciók és tengelyek {#positions-and-axes}

| | |
|---|---|
| Rögzített pozíciók | igen |
| Felfelé mutató tengely | `y` |
| Mértékegységek | méter (a BeamNG Z felfelé mutató világa az X körül elforgatva, ahogy a köridő-rögzítő teszi) |
| Tükrözés a megjelenítőhöz | nincs |
| Mértékskála (`scale`: a megjelenítő ezzel szorozza a pozíciókat) | 1 |

Ezek minden munkamenet `meta.json` fájljának `axes` mezőjébe kerülnek, és ha a munkamenetnek vannak pozíciói, a `heat.parquet` láblécébe is, így a 3DHeat-megjelenítő magától forgatja és méretezi a sorokat - lásd [Az adatok](the-data.md).

## Többjátékos {#multiplayer}

- Online játékként jelölve (`multiplayer`): **nem**. A `games --markdown` ezt "egyjátékos" formában mutatja.
- `telemetry` típus: csak azt olvassa, amit a játék vagy a platform kiad (a játék által közzétett UDP-port vagy osztott memória), ezért online játékban is rögzít, nem csak offline; a jelző csak azt dönti el, szabad-e egyáltalán memóriát olvasni.
- Memória: ez az adapter **soha** nem olvas memóriát. Csak a `memory` típusú adapterek olvasnak memóriát, és soha nem olyan játékhoz, amely online játékként van megjelölve - lásd [Forrásak és szabályok](sources-and-rules.md).

## Rögzített statisztikák {#statistics-recorded}

Azok a statisztikakulcsok, amelyeket ez az adapter kódja név szerint állít be (minden munkamenet `stats` mezője a `meta.json`-ban és a `watcher.sqlite` `stats` táblájában):

`best_lap`, `distance_km`, `laps`, `top_speed_kmh`

A kapcsos zárójeles kulcsot futásidőben töltik ki (a `score.{team}` csapatonként egy kulcs). Azok a kulcsok, amelyeket a kód a játék mezőinek táblázatából vagy a játék saját statisztikanevei közül vesz, nincsenek ebben a listában; a fenti "Mit rögzít" rész nevezi meg őket.

## Teljesség {#completeness}

A watcher követi a 3DHeat [konvertáló szabályát](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md): amit a forrás tartalmaz, azt beolvassa vagy megőrzi, sosem dobja el. A sorokon kívül minden csomagot, oldalt, sort vagy választ, amelyet az adapter kap, egészben megőriz a munkamenet `heat.raw.parquet` fájlja (oszlopok: `time`, `ms`, `type`, `used`, `payload`, `text`, majd minden név szerint megtartott mező; a `used` jelöli, ami sorrá is vált), és a `meta.json` `selfCheck.completeness` mezője minden `type` értéket megszámol - a `lost` értéke 0.

**Beolvasva**

- sorok 10 Hz-en: pozíció, sebesség, fokozat, gáz, fék, yaw, fordulatszám, kormány; vezetés kezdete, visszaállítások, körök

**Nyersen megőrizve**

- minden csomag, amely a porthoz ér, egészben, a mód 100 Hz-es sebességén: `H3D1` (a mód 160 bájtos struktúrája: óra, pozíció, sebesség, az autó tengelyei, yaw-sebesség, kilenc bemenet, kerekenkénti felületi sebesség, forgás, terhelés és talajanyag), minden más `<n>-byte` néven

**Nem elérhető**

- ami a mód nem küld: a BeamNG-nek nincs rögzített telemetriai csomagja, ezért a csatornák azok, amelyeket a heat3d mód kiválasztott (más járművek, sérülés, a pálya neve nincs benne)

**Méret**: tömörítés előtt óránként körülbelül 80 MB (másodpercenként 100 csomag, 160 bájtosan, plusz 70 bájtos elemfejléc)

## Ellenőrzés {#verified}

a dekódolás a gamecapture köridő-rögzítőjéé (a mód struktúrájából épített csomagokon tesztelve); az adapter ilyen csomagokon tesztelve; a mód a játékban nincs tesztelve

## Forrás {#source}

[heat3d_watch/adapters/racing.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/racing.py)

<!-- Generated from the adapter by tools/gen_game_pages.py; change the adapter and run it again rather than editing this page. -->
