---
title: "Forza Horizon 6 (élő adatok)"
nav_order: 23
lang: "hu"
source: game-forza-horizon-6.md
source_hash: "164d188cb521"
nav_exclude: true
search_exclude: true
---
# Forza Horizon 6 (élő adatok) {#forza-horizon-6-live-data}

Amíg a Forza Horizon 6-ot játszod, a watcher elmenti azokat az adatokat, amelyeket maga a játék kiküld, így később megnézheted őket térképen a 3DHeat megjelenítőben.

*Műszaki részletek: adapter `forza-horizon-6`, típus [`telemetry`](sources-and-rules.md); akkor fut, amikor a `forzahorizon6.exe` fut, és 0,1 másodpercenként keres új adatot.*

## Mit rögzít {#what-is-recorded}

- a saját autó helyzete (világ XYZ, m) 10 Hz-cel, sebességgel, fokozattal, gázzal, fékkel, körrel
- vezetés kezdete és vége (session_start/session_end), körök a játék köridejével
- verseny kezdete és vége a versenyhelyezéssel
- ugrások (visszatekerés, gyorsutazás): `teleport`, ahol az autó volt, `spawn`, ahol most van
- körök, legjobb kör, távolság, legnagyobb sebesség, versenyek

## Honnan származik {#where-it-comes-from}

Forza Data Out, UDP 127.0.0.1:5300 (Dash formátum); minden csomag változatlanul továbbítva a 127.0.0.1:5301 címre

## Hogyan kapcsold be {#how-to-switch-it-on}

A játékban: Beállítások > HUD és játékmenet > Data Out Be, IP 127.0.0.1, port 5300 (Motorsport: Dash formátum). FH Companion vagy más Data Out alkalmazás: állítsd a portját 5301-re – a watcher továbbít minden csomagot; amíg egy másik alkalmazás az 5300-as porton figyel, a watcher otthagyja neki a portot, és nem rögzít semmit

## Hogyan működik {#how-it-works}

A versenyjátékok saját telemetriája: a Forza, az Assetto Corsa játékok, a ralikjátékok és a BeamNG, útvonalakként, körökként és szakaszokként rögzítve.

Itt minden játék szándékosan teszi közzé a telemetriáját, műszerfalakhoz és mozgató szimulátorokhoz; semmit sem injektálnak, és nem olvasnak olyat, amit a játék nem ad ki. A dekódolás nem készül el kétszer: a gamecapture körrögzítői a 3DHeat GameCapture `heat3d_capture/telemetry` mappájából származnak, a `heat3d_watch/decoders` mappába másolva (ott a közzétett elrendezésekből épített csomagokon tesztelve), és ez a modul ezek kereteit a watcher sorainak alakítja: az autó helyzete másodpercenként többször a sebességgel, fokozattal és pedálokkal, egy esemény körönként vagy szakaszonként, valamint a számok, amelyeket a versenyző nyilvántart: körök, legjobb kör, távolság, legnagyobb sebesség.

#### Forza (Horizon 4/5/6, Motorsport) {#forza-horizon-456-motorsport}

"Data Out" UDP, a játék HUD- és játékbeállításaiban bekapcsolva, a 127.0.0.1 1-es porton 5300, Dash formátum. Szimulációs ciklusonként egy csomag; a dash-blokk eltolását a csomagokból találja meg (`forza.detect_layout`). Világ méterben, Y felfelé; a világ balkezes, és úgy rajzolódik ki, ahogy érkezik, ahogy a körrögzítő is teszi (a Forza Motorsport és a Forza Horizon "Data Out" dokumentációja szerint).
A játék egy portra küld, és az FH Companion és más Data Out alkalmazások ugyanazon a porton figyelnek. Két program nem oszthatja meg: Windowsban a 127.0.0.1-hez kötött socket kapja a csomagokat, a minden címre kötött socket ugyanazon a porton egyet sem, bármelyik indult előbb. Ezért a watcher egy kicsit vár, miután a játék elindult, mielőtt elfoglalja a portot, sosem veszi el egy olyan alkalmazástól, amely már tartja, és azonnal elengedi, amint egy másik alkalmazás ott figyelni kezd.
Miközben tartja a portot, minden csomagot változatlanul továbbít a 127.0.0.1:5301 címre: állítsd az FH Companion portmezőjét (a telemetria fülén) 5301-re, és mindkettő rögzít.

#### Minden megtartva {#everything-kept}

A sorok másodpercenként néhányan vannak; a játékok ennél sokkal többet küldenek. Minden UDP-csomag, amely megérkezik – a menükben, körök között, azok, amelyeket egyetlen dekóder sem olvas –, egészben megmarad a munkamenet `heat.raw.parquet` fájljában a formátuma alatt (`dash-horizon`, `session_update`, `extradata3`, `H3D1`, ...), és minden megosztott memórialap (a teljes leképezés, nem csak a dekódolt bájtok), amikor változik, a leképezése nevén (`acpmf_physics`, ...). A `used` jelöli azt, ami sorrá is vált; a `meta.json` `selfCheck.completeness` adatai típusonként számolják (a 3DHeat konvertálási szabálya).

Ugyanez a modul szolgálja ki még: [Assetto Corsa (élő adatok)](game-assetto-corsa.md), [Assetto Corsa Competizione (élő adatok)](game-assetto-corsa-competizione.md), [Assetto Corsa EVO (élő adatok)](game-assetto-corsa-evo.md), [Assetto Corsa Rally (élő adatok)](game-assetto-corsa-rally.md), [BeamNG.drive (élő adatok)](game-beamng.md), [DiRT Rally 2.0 (élő adatok)](game-dirt-rally-2.md), [EA SPORTS WRC (élő adatok)](game-ea-wrc.md), [Forza Horizon 4 (élő adatok)](game-forza-horizon-4.md), [Forza Horizon 5 (élő adatok)](game-forza-horizon-5.md), [Forza Motorsport (élő adatok)](game-forza-motorsport.md), [Richard Burns Rally (élő adatok)](game-richard-burns-rally.md).

## Pozíciók és tengelyek {#positions-and-axes}

| | |
|---|---|
| Rögzített pozíciók | igen |
| Felfelé mutató tengely | `y` |
| Mértékegység | méter; a Forza világa balkezes, úgy rajzolódik ki, ahogy érkezik, ahogy a körrögzítő is teszi |
| Tükrözés a megjelenítőnek | nincs |
| Mértékskála (`scale`: a megjelenítő ezzel szorozza a pozíciókat) | 1 |

Ezek bekerülnek minden munkamenet `meta.json` fájljának `axes` mezőjébe, és ha a munkamenetnek vannak pozíciói, a `heat.parquet` láblécébe, így a 3DHeat megjelenítő maga forgatja és méretezi a sorokat – lásd [Az adatok](the-data.md).

## Többjátékos mód {#multiplayer}

- Online játékként jelölve (`multiplayer`): **igen**. A `games --markdown` ezt így jeleníti meg: "engedélyezett (csak azt olvassa, amit a játék közzétesz)".
- Típus `telemetry`: csak azt olvassa, amit a játék vagy a platform kiad (egy UDP-port vagy megosztott memória, amelyet a játék közzétesz), ezért online játék közben is rögzít, nem csak offline; a jelző csak azt dönti el, szabad-e egyáltalán memóriát olvasni.
- Memória: ez az adapter **soha** nem olvas memóriát. Csak a `memory` adapterek olvasnak memóriát, és soha nem olyan játékhoz, amely online játékként van jelölve – lásd [Források és szabályok](sources-and-rules.md).

## Rögzített statisztikák {#statistics-recorded}

Ennek az adapternek a kódja névről név beállított statisztikakulcsai (minden munkamenet `stats` mezője a `meta.json`-ban és a `watcher.sqlite` `stats` táblájában):

`best_lap`, `distance_km`, `laps`, `races`, `top_speed_kmh`

A kapcsos zárójelben lévő kulcsot futásidőben töltik ki (`score.{team}` csapatonként egy kulcs). Azok a kulcsok, amelyeket a kód a játék mezőinek táblázatából vagy a játék saját statisztikanevéből vesz, nincsenek ebben a listában; a fenti "Mit rögzít" rész nevezi meg őket.

## Teljesség {#completeness}

A watcher követi a 3DHeat [konvertálási szabályát](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md): amit a forrás tartalmaz, azt beolvassa vagy megtartja, soha nem dobja el. A sorokon kívül minden csomagot, lapot, sort vagy választ, amelyet az adapter kap, egészben megtart a munkamenet `heat.raw.parquet` fájljában (oszlopai `time`, `ms`, `type`, `used`, `payload`, `text`, majd minden név szerint megtartott mező; a `used` jelöli, ami sorrá is vált), a `meta.json` `selfCheck.completeness` adatai pedig minden `type`-ot számolnak – a `lost` értéke 0.

**Beolvasva**

- 10 Hz-es sorok: pozíció, sebesség, fokozat, gáz, fék, kör, yaw/pitch/roll (rad), fordulatszám, kormányzás (-1..1); session_start az autó sorszámával, osztályával, PI-jével és hajtásláncával; körök a játék köridejével; versenyhelyezés

**Nyers formában megtartva**

- minden csomag, amely eléri a portot, egészben, a játék ütemében (szimulációs ciklusonként egy), a formátuma alatt: `dash-horizon` (324 bájt, Forza Horizon), `dash` (311, Motorsport 7), `dash-fm2023` (331, Forza Motorsport 2023: gumikopás és pályaazonosító), `sled` (232, pozíció nélkül), `<n>-byte` minden másnál – beleértve a menü-csomagokat (isRaceOn 0), a csomagokat, amelyeket addig tartanak, amíg a műszerfal-elrendezés nincs bizonyítva, és a Horizon-csomag ~13 bájtját, amelyet semmilyen közzétett elrendezés nem nevez meg
- a Sled-blokk minden kerék-csatornája (csúszási arány, csúszási szög, kombinált csúszás, felfüggesztés, kerékse-besség, zörgés, pocsolya), gyorsulások, szögsebesség, teljesítmény, nyomaték, turbó, üzemanyag, gumihőmérséklet, kuplung, kézifék, vezetési vonal, AI-fékkülönbség: mind a csomagokban, a `decoders/fulllap.decode_full` dekódolja belőlük

**Nem elérhető**

- más autók: a Data Out csak a játékos autóját írja le
- a pálya vagy az útvonal neve: a Forza Horizon soha nem küld ilyet; a Motorsport 2023 csak egy pályaszámot küld
- csomagok, amíg egy másik alkalmazás (FH Companion) tartja az UDP 5300-as portot: a watcher otthagyja neki a portot

**Méret**: óránként körülbelül 85 MB tömörítés előtt (60 csomag/másodperc, 324 bájt plusz 70 bájtos elemfejléc); az egymást követő csomagok alig térnek el, így a zstd ennek töredékét tartja meg

## Ellenőrizve {#verified}

a dekódolás a gamecapture körrögzítőjéé (a Data Out elrendezéséből épített csomagokon tesztelve); az adapter szintetikus csomagokon és rögzített körpályák csomagokként visszajátszott felvételein tesztelve; a játékon magán még nem tesztelve

## Forrás {#source}

[heat3d_watch/adapters/racing.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/racing.py)

<!-- Generated from the adapter by tools/gen_game_pages.py; change the adapter and run it again rather than editing this page. -->
