---
title: "X-Plane (élő adatok)"
nav_order: 50
lang: "hu"
source: game-xplane.md
source_hash: "4e7246cce10c"
nav_exclude: true
search_exclude: true
---
# X-Plane (élő adatok) {#x-plane-live-data}

Amíg az X-Plane-t játszod, a watcher elmenti azokat az adatokat, amelyeket maga a játék kiküld, így később megnézheted őket térképen a 3DHeat megjelenítőben.

*Műszaki részletek: adapter `xplane`, típus [`telemetry`](sources-and-rules.md); akkor fut, amikor az `X-Plane.exe` fut, és 0,1 másodpercenként keres új adatot.*

## Mit rögzít {#what-is-recorded}

- a saját pozíció 10 Hz-cel (szélesség/hosszúság/magasság méterben kelet/fel/észak az első rögzítéstől; a szélesség/hosszúság/magasság oszlopokként megtartva)
- hozzáállás, műszerelt és valódi légsebesség, földi sebesség, Mach, függőleges sebesség, AoA, oldalcsúszás, mágneses irány, AGL, g (normál, tengelyirányú, oldalirányú), sebesség és forgási sebességek, csűrők, légfék, gáz, a földön-e
- súlyok (összes, üzemanyag, rakomány), futómű-kar, autopilóta, motorfordulatszám és N1, a szimulációs idő és dátum, szünet, szimulációs sebesség, visszajátszás, külső hőmérséklet és tengerszinti nyomás (X-Plane 12) másodpercenként egyszer
- felszállások, leszállások, lezuhanások, repülésállítások (session_start/session_end repülésenként)
- repülési idő, levegőben töltött idő, távolság, legmagasabb pont, legnagyobb g, leszállások
- minden válasz, amelyet az X-Plane küld, egészben a heat.raw.parquet fájlban

## Honnan származik {#where-it-comes-from}

Az X-Plane UDP-felülete a 127.0.0.1:49000 címen (RREF datarefek és RPOS pozíció, a watchernek válaszolva)

## Hogyan kapcsold be {#how-to-switch-it-on}

X-Plane 12: Beállítások > Hálózat > Bejövő kapcsolatok elfogadása (az X-Plane 11 alapból válaszol)

## Hogyan működik {#how-it-works}

X-Plane 11 és 12: a szimulátor saját UDP-felülete a 49000-es porton.

Az X-Plane válaszol mindenkinek, aki a 127.0.0.1:49000 címen kérdez, a kért ütemben, arra a címre és portra, ahonnan a kérés jött (az X-Plane "Exchanging Data with X-Plane" dokumentuma szerint, amely a `<X-Plane>\Instructions\` mappában van):

```text
RREF  "RREF\0" + int32 freq + int32 index + char[400] dataref path (413 bytes).
      The answer is "RREF" + one internal byte + (int32 index, float32 value)
      pairs; freq 0 stops it.
RPOS  "RPOS\0" + the rate as a NUL-terminated ASCII string ("10\0"). The
      answer is "RPOS" + one internal byte + double lon, lat, elevation (m
      MSL) + float AGL (m), pitch, true heading, roll (deg), vx east, vy up,
      vz south (m/s), P, Q, R (rad/s), tightly packed.
```

Az RPOS szélességet és hosszúságot dupla pontossággal ad (az RREF csak float-ban, fél méterre egymástól), ezért ez hajtja a pozíciót; az RREF hozza a többit, és helyettesíti az RPOS-t, ha az nem jön. Datarefek (a nevek az X-Plane 12 `Resources\plugins\DataRefs.txt` fájlja szerint, <https://developer.x-plane.com/datarefs/>):

```text
sim/flightmodel/position/latitude, longitude, elevation  deg, deg, m MSL
sim/flightmodel/position/true_theta, true_phi, true_psi  pitch, roll, true heading (deg)
sim/flightmodel/position/indicated_airspeed              knots
sim/flightmodel/position/groundspeed                     m/s
sim/flightmodel/position/y_agl                           m above ground
sim/flightmodel/forces/g_nrml                            g, normal to the wings
sim/flightmodel/failures/onground_any                    1 on the ground
sim/flightmodel2/misc/has_crashed                        1 crashed
sim/time/total_flight_time_sec                           since the flight was reset
```

A repülés többi része ugyanabban az ütemben (valódi légsebesség, függőleges sebesség, AoA, oldalcsúszás, mágneses irány, Mach, tengelyirányú és oldalirányú g, forgási sebességek, csűrők, légfék, gáz: `DATAREFS`), a gép lassabb állapota másodpercenként egyszer (súlyok, futómű-kar, autopilóta, motorok, a szimuláció ideje, szünet és sebessége, időjárás: `SLOW_DATAREFS`). Minden datagram egészben megmarad a munkamenet nyers mellékletében, és a meta.json megnevezi, melyik dataref van az egyes RREF-indexek mögött.

Az X-Plane 12 ezeket csak akkor fogadja el, ha a Beállítások > Hálózat > "Bejövő kapcsolatok elfogadása" be van kapcsolva. A pozíciók a munkamenet első rögzítése körüli lapos térképbe kerülnek (`Tangent`): x kelet, z észak méterben, y a tengerszint feletti magasság – így a vízszintes repülés vízszintes marad, bármilyen messzire megy, amit egy valódi érintősík a Föld görbülete miatt lefelé hajlítana. A térkép kezdőpontja a munkamenet `geo` mezője: a meta.json és a tábla láblécében van, így a megjelenítő a valódi világot ki tudja rakni a repülés alá.

Ez a modul azt is tartalmazza, amit a többi repülőszimulátor közösen használ: a lapos térkép, a repülés nyilvántartása (felszállások, leszállások, lezuhanások, távolság), az UDP-socket és a Steam-könyvtár listája.

## Pozíciók és tengelyek {#positions-and-axes}

| | |
|---|---|
| Rögzített pozíciók | igen |
| Felfelé mutató tengely | `y` |
| Mértékegység | méter (kelet, magasság, észak az első rögzítéstől) |
| Tükrözés a megjelenítőnek | `z` |
| Mértékskála (`scale`: a megjelenítő ezzel szorozza a pozíciókat) | 1 |

Ezek bekerülnek minden munkamenet `meta.json` fájljának `axes` mezőjébe, és ha a munkamenetnek vannak pozíciói, a `heat.parquet` láblécébe, így a 3DHeat megjelenítő maga forgatja és méretezi a sorokat – lásd [Az adatok](the-data.md).

## Többjátékos mód {#multiplayer}

- Online játékként jelölve (`multiplayer`): **nem**. A `games --markdown` ezt így jeleníti meg: "egyjátékos".
- Típus `telemetry`: csak azt olvassa, amit a játék vagy a platform kiad (egy UDP-port vagy megosztott memória, amelyet a játék közzétesz), ezért online játék közben is rögzít, nem csak offline; a jelző csak azt dönti el, szabad-e egyáltalán memóriát olvasni.
- Memória: ez az adapter **soha** nem olvas memóriát. Csak a `memory` adapterek olvasnak memóriát, és soha nem olyan játékhoz, amely online játékként van jelölve – lásd [Források és szabályok](sources-and-rules.md).

## Rögzített statisztikák {#statistics-recorded}

Ennek az adapternek a kódja névről név beállított statisztikakulcsai (minden munkamenet `stats` mezője a `meta.json`-ban és a `watcher.sqlite` `stats` táblájában):

`airborne_time`, `bad_packets`, `crashes`, `distance_km`, `flight_time`, `max_altitude_m`, `max_g`, `{event}s`

A kapcsos zárójelben lévő kulcsot futásidőben töltik ki (`score.{team}` csapatonként egy kulcs). Azok a kulcsok, amelyeket a kód a játék mezőinek táblázatából vagy a játék saját statisztikanevéből vesz, nincsenek ebben a listában; a fenti "Mit rögzít" rész nevezi meg őket.

## Teljesség {#completeness}

A watcher követi a 3DHeat [konvertálási szabályát](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md): amit a forrás tartalmaz, azt beolvassa vagy megtartja, soha nem dobja el. A sorokon kívül minden csomagot, lapot, sort vagy választ, amelyet az adapter kap, egészben megtart a munkamenet `heat.raw.parquet` fájljában (oszlopai `time`, `ms`, `type`, `used`, `payload`, `text`, majd minden név szerint megtartott mező; a `used` jelöli, ami sorrá is vált), a `meta.json` `selfCheck.completeness` adatai pedig minden `type`-ot számolnak – a `lost` értéke 0.

**Beolvasva**

- RPOS (10 Hz): hosszúság, szélesség, magasság, AGL, pitch, valódi irány, roll, sebesség (kelet, fel, dél) és forgási sebességek P/Q/R – mind a sorokon
- RREF (10 Hz): a `DATAREFS` 27 datarefje – pozíció, hozzáállás, IAS, földi sebesség, TAS, függőleges sebesség, AoA, oldalcsúszás, mágneses irány, Mach, g normál/tengelyirányú/oldalirányú, forgási sebességek, csűrők, légfék, gáz, AGL, lezuhant, a földön, repülési idő – a sorokon
- RREF (1 Hz): a `SLOW_DATAREFS` 20 datarefje – súlyok, futómű-kar, autopilóta-szervók, a szimuláció ideje és dátuma, szünet, szimulációs sebesség, visszajátszás, motorszám, az 1–4-es motorok fordulatszáma, az 1–2-es motorok N1-e, külső levegőhőmérséklet, tengerszinti nyomás – az utolsó érték szerint a sorokon

**Nyers formában megtartva**

- minden datagram egészben `payload`-ként, a négybetűs fejléce alatt: `RREF` és `RPOS` (akkor használt, ha a lekérdezés sort készített; a menükben, pozíció nélkül, nem készítenek sort), bármi más, amit az X-Plane a watcher portjára küld, a saját fejlécén vagy `unknown` alatt; a meta.json `requests` mezője megmondja, melyik dataref van az egyes RREF-indexek mögött, így a payloadok ennek a modulnak a nélkül is olvashatók

**Nem elérhető**

- minden más dataref (az X-Plane-ben több ezer van): az RREF csak azt küldi, amit kérnek, egy-egy feliratkozásra; a lista a repülést, a gép állapotát és a szimuláció idejét kéri – több pilótafülke-részlet (rádiók, lámpák, minden motor műszerei, meghibásodások) megszorozná a kéréseket
- a gép neve és az ICAO-típusa: bájttömb-datarefek, amelyeket az RREF karakterenként egy floatként küld
- más gépek (AI és többjátékos): a sim/multiplayer/position datarefek nincsenek kérve
- a DATA kimenet (Beállítások > Adatkimenet): fix címre küld, amelyet a szimulátorban választanak, nem arra, aki kérdez; az RREF és az RPOS lefedi, amit a watcher olvas

**Méret**: óránként körülbelül 17 MB zstd előtt (RREF és RPOS 10 Hz-cel, nagyjából 220 és 70 bájt plusz egy keret mindegyik, a lassú RREF másodpercenként egyszer), ha az X-Plane egy lekérdezés értékeit egy csomagban küldi, ahogy teszi; a zstd a floatokat többszörösére csökkenti

## Ellenőrizve {#verified}

egy hamis X-Plane-en tesztelve, amely az X-Plane 12 'Exchanging Data with X-Plane' dokumentuma szerint válaszol az RREF/RPOS kérésekre; a dataref-nevek az X-Plane 12 DataRefs.txt fájljával egyeztetve; a futó szimulátoron még nem tesztelve

## Forrás {#source}

[heat3d_watch/adapters/xplane.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/xplane.py)

<!-- Generated from the adapter by tools/gen_game_pages.py; change the adapter and run it again rather than editing this page. -->
