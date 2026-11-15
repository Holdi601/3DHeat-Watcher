---
title: "Assetto Corsa (élő adatok)"
nav_order: 2
lang: "hu"
source: game-assetto-corsa.md
source_hash: "9132272cc104"
nav_exclude: true
search_exclude: true
---
# Assetto Corsa (élő adatok) {#assetto-corsa-live-data}

Amíg az Assetto Corsát játszod, a watcher elmenti azokat az adatokat, amelyeket maga a játék kiküld, így később megnézheted őket térképen a 3DHeat megjelenítőben.

*Műszaki részletek: adapter `assetto-corsa`, típus [`telemetry`](sources-and-rules.md); akkor fut, amikor az `acs.exe` vagy az `acs_x86.exe` fut, és 0,1 másodpercenként keres új adatot.*

## Mit rögzít {#what-is-recorded}

- a saját autó helyzete (világ XYZ, m: a négy gumi érintkezési pontjának átlaga) 10 Hz-cel, sebességgel, fokozattal, gázzal, fékkel
- a munkamenet kezdete és vége a pálya és az autó nevével, ahogy a játék nevezi
- körök a játék köszámlálója szerint, a köridővel
- ugrások (vissza a boxba, újraindítás): `teleport`, ahol az autó volt, `spawn`, ahol most van
- körök, a legjobb kör, távolság, legnagyobb sebesség

## Honnan származik {#where-it-comes-from}

megosztott memória: Local\acpmf_physics, Local\acpmf_graphics, Local\acpmf_static

## Hogyan kapcsold be {#how-to-switch-it-on}

Semmit sem kell bekapcsolni: a watcher úgy olvassa a forrást, ahogy a játék vagy a platform biztosítja.

## Hogyan működik {#how-it-works}

A versenyjátékok saját telemetriája: a Forza, az Assetto Corsa játékok, a ralikjátékok és a BeamNG, útvonalakként, körökként és szakaszokként rögzítve.

Itt minden játék szándékosan teszi közzé a telemetriáját, műszerfalakhoz és mozgató szimulátorokhoz; semmit sem injektálnak, és nem olvasnak olyat, amit a játék nem ad ki. A dekódolás nem készül el kétszer: a gamecapture körrögzítői a 3DHeat GameCapture `heat3d_capture/telemetry` mappájából származnak, a `heat3d_watch/decoders` mappába másolva (ott a közzétett elrendezésekből épített csomagokon tesztelve), és ez a modul ezek kereteit a watcher sorainak alakítja: az autó helyzete másodpercenként többször a sebességgel, fokozattal és pedálokkal, egy esemény körönként vagy szakaszonként, valamint a számok, amelyeket a versenyző nyilvántart: körök, legjobb kör, távolság, legnagyobb sebesség.

#### Forza (Horizon 4/5/6, Motorsport) {#forza-horizon-456-motorsport}

"Data Out" UDP, a játék HUD- és játékbeállításaiban bekapcsolva, a 127.0.0.1 1-es porton 5300, Dash formátum. Szimulációs ciklusonként egy csomag; a dash-blokk eltolását a csomagokból találja meg (`forza.detect_layout`). Világ méterben, Y felfelé; a világ balkezes, és úgy rajzolódik ki, ahogy érkezik, ahogy a körrögzítő is teszi (a Forza Motorsport és a Forza Horizon "Data Out" dokumentációja szerint).
A játék egy portra küld, és az FH Companion és más Data Out alkalmazások ugyanazon a porton figyelnek. Két program nem oszthatja meg: Windowsban a 127.0.0.1-hez kötött socket kapja a csomagokat, a minden címre kötött socket ugyanazon a porton egyet sem, bármelyik indult előbb. Ezért a watcher egy kicsit vár, miután a játék elindult, mielőtt elfoglalja a portot, sosem veszi el egy olyan alkalmazástól, amely már tartja, és azonnal elengedi, amint egy másik alkalmazás ott figyelni kezd.
Miközben tartja a portot, minden csomagot változatlanul továbbít a 127.0.0.1:5301 címre: állítsd az FH Companion portmezőjét (a telemetria fülén) 5301-re, és mindkettő rögzít.

#### Assetto Corsa, ACC, AC EVO, AC Rally {#assetto-corsa-acc-ac-evo-ac-rally}

Megosztott memória, amelyet a játék alkalmazásoknak ír: `Local\acpmf_physics`, `Local\acpmf_graphics`, `Local\acpmf_static` (AC EVO: `Local\acevo_pmf_*`).
Csak olvashatóan nyitja meg, és csak miután a játék létrehozta (`simracing_shm`). A helyzet a négy gumi érintkezési pontjának átlaga, világ méterben, Y felfelé.
A körök a játék számlálója szerint (AC, ACC), vagy azzal, hogy újra átmész a kiindulópont-on (AC EVO, AC Rally), ahogy a `kunos.py` teszi a körrögzítőhöz.

#### Minden megtartva {#everything-kept}

A sorok másodpercenként néhányan vannak; a játékok ennél sokkal többet küldenek. Minden UDP-csomag, amely megérkezik – a menükben, körök között, azok, amelyeket egyetlen dekóder sem olvas –, egészben megmarad a munkamenet `heat.raw.parquet` fájljában a formátuma alatt (`dash-horizon`, `session_update`, `extradata3`, `H3D1`, ...), és minden megosztott memórialap (a teljes leképezés, nem csak a dekódolt bájtok), amikor változik, a leképezése nevén (`acpmf_physics`, ...). A `used` jelöli azt, ami sorrá is vált; a `meta.json` `selfCheck.completeness` adatai típusonként számolják (a 3DHeat konvertálási szabálya).

Ugyanez a modul szolgálja ki még: [Assetto Corsa Competizione (élő adatok)](game-assetto-corsa-competizione.md), [Assetto Corsa EVO (élő adatok)](game-assetto-corsa-evo.md), [Assetto Corsa Rally (élő adatok)](game-assetto-corsa-rally.md), [BeamNG.drive (élő adatok)](game-beamng.md), [DiRT Rally 2.0 (élő adatok)](game-dirt-rally-2.md), [EA SPORTS WRC (élő adatok)](game-ea-wrc.md), [Forza Horizon 4 (élő adatok)](game-forza-horizon-4.md), [Forza Horizon 5 (élő adatok)](game-forza-horizon-5.md), [Forza Horizon 6 (élő adatok)](game-forza-horizon-6.md), [Forza Motorsport (élő adatok)](game-forza-motorsport.md), [Richard Burns Rally (élő adatok)](game-richard-burns-rally.md).

## Pozíciók és tengelyek {#positions-and-axes}

| | |
|---|---|
| Rögzített pozíciók | igen |
| Felfelé mutató tengely | `y` |
| Mértékegység | méter |
| Tükrözés a megjelenítőnek | nincs |
| Mértékskála (`scale`: a megjelenítő ezzel szorozza a pozíciókat) | 1 |

Ezek bekerülnek minden munkamenet `meta.json` fájljának `axes` mezőjébe, és ha a munkamenetnek vannak pozíciói, a `heat.parquet` láblécébe, így a 3DHeat megjelenítő maga forgatja és méretezi a sorokat – lásd [Az adatok](the-data.md).

## Többjátékos mód {#multiplayer}

- Online játékként jelölve (`multiplayer`): **igen**. A `games --markdown` ezt így jeleníti meg: "engedélyezett (csak azt olvassa, amit a játék közzétesz)".
- Típus `telemetry`: csak azt olvassa, amit a játék vagy a platform kiad (egy UDP-port vagy megosztott memória, amelyet a játék közzétesz), ezért online játék közben is rögzít, nem csak offline; a jelző csak azt dönti el, szabad-e egyáltalán memóriát olvasni.
- Memória: ez az adapter **soha** nem olvas memóriát. Csak a `memory` adapterek olvasnak memóriát, és soha nem olyan játékhoz, amely online játékként van jelölve – lásd [Források és szabályok](sources-and-rules.md).

## Rögzített statisztikák {#statistics-recorded}

Ennek az adapternek a kódja névről név beállított statisztikakulcsai (minden munkamenet `stats` mezője a `meta.json`-ban és a `watcher.sqlite` `stats` táblájában):

`best_lap`, `best_stage`, `distance_km`, `laps`, `race_position`, `stages`, `top_speed_kmh`

A kapcsos zárójelben lévő kulcsot futásidőben töltik ki (`score.{team}` csapatonként egy kulcs). Azok a kulcsok, amelyeket a kód a játék mezőinek táblázatából vagy a játék saját statisztikanevéből vesz, nincsenek ebben a listában; a fenti "Mit rögzít" rész nevezi meg őket.

## Teljesség {#completeness}

A watcher követi a 3DHeat [konvertálási szabályát](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md): amit a forrás tartalmaz, azt beolvassa vagy megtartja, soha nem dobja el. A sorokon kívül minden csomagot, lapot, sort vagy választ, amelyet az adapter kap, egészben megtart a munkamenet `heat.raw.parquet` fájljában (oszlopai `time`, `ms`, `type`, `used`, `payload`, `text`, majd minden név szerint megtartott mező; a `used` jelöli, ami sorrá is vált), a `meta.json` `selfCheck.completeness` adatai pedig minden `type`-ot számolnak – a `lost` értéke 0.

**Beolvasva**

- 10 Hz-es sorok a fizikai lapból: pozíció (a gumi-érintkezési pontok átlaga), sebesség, fokozat, gáz, fék, yaw/pitch/roll (rad), fordulatszám, kormányzás (ahogy a lap tartalmazza); a munkamenet kezdete a pálya és az autó nevével a statikus lapról; körök, versenyhelyezés

**Nyers formában megtartva**

- minden lap egészben – a teljes memórialap-tartomány, nem csak a dekódolt bájtok – minden alkalommal, amikor a bájtjai változnak, a watcher 10 Hz-es olvasásakor: `acpmf_physics`, `acpmf_graphics`, `acpmf_static`; egy olvasás, amely bájtról bájtra megegyezik az előzővel, a meta.json `unchanged_reads` mezőjében számolódik, és nem tárolódik újra
- minden, ami csak a körfájlokhoz dekódolódik (`decoders/kunos.py`: kerekenkénti csúszás, terhelés, nyomás, hőmérséklet, dőlés, felfüggesztés, érintkezési pontok, fékhőmérséklet, csúszási arány és szög; világ- és helyi sebesség, szögsebesség, segédeszközök) ezekben a lapokban van

**Nem elérhető**

- más autók pozíciói: a lapok csak a játékos autóját írják le (az ACC grafikus lapja egyes verziókban más autók azonosítóit és koordinátáit is tartalmazza – a nyers lapban megmarad, nincs dekódolva)
- fizikai ciklusok a watcher olvasásai között: a játék a saját fizikai ütemében írja újra a lapot (legfeljebb 333 Hz), a watcher pedig másodpercenként tízszer olvas

**Méret**: óránként körülbelül 150–300 MB tömörítés előtt (laponként 4 KB-os régió, másodpercenként legfeljebb 10 változással); a lapok többnyire nullák, a zstd kis töredékre tömöríti

## Ellenőrizve {#verified}

a dekódolás a gamecapture körrögzítőjéé (szintetikus lapokon tesztelve); az adapter olyan megosztott memórián tesztelve, amelyet a teszt a dokumentált elrendezés szerint épít; a játékon még nem tesztelve

## Forrás {#source}

[heat3d_watch/adapters/racing.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/racing.py)

<!-- Generated from the adapter by tools/gen_game_pages.py; change the adapter and run it again rather than editing this page. -->
