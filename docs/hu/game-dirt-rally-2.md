---
title: "DiRT Rally 2.0 (élő adatok)"
nav_order: 11
lang: "hu"
source: game-dirt-rally-2.md
source_hash: "367131ff990b"
nav_exclude: true
search_exclude: true
---
# DiRT Rally 2.0 (élő adatok)

Amíg a DiRT Rally 2.0-t játszod, a watcher elmenti azokat az adatokat, amelyeket maga a játék kiküld, így később megnézheted őket térképen a 3DHeat megjelenítőben.

*Műszaki részletek: adapter `dirt-rally-2`, típus [`telemetry`](sources-and-rules.md); akkor fut, amikor a `dirtrally2.exe` fut, és 0,1 másodpercenként keres új adatot.*

## Mit rögzít

- a saját autó helyzete (világ XYZ, m) 10 Hz-cel, sebességgel, fokozattal, gázzal, fékkel, szakasz-távolsággal
- szakaszkezdet (a szakaszóra elindul), befejezés a szakaszidővel, újraindítások
- ugrások (visszaállás az útra): `teleport`, ahol az autó volt, `spawn`, ahol most van
- szakaszok, legjobb szakaszidő, távolság, legnagyobb sebesség

## Honnan származik

UDP 127.0.0.1:20777, extradata=3 (Documents\My Games\DiRT Rally 2.0\hardwaresettings\hardware_settings_config.xml); amíg egy másik alkalmazás tartja a 20777-es portot, a watcher otthagyja neki a portot

## Hogyan kapcsold be

`python -m heat3d_watch setup dirt-rally-2 --apply` beállítja: &lt;udp enabled="true" extradata="3"> (előtte biztonsági másolat készül)

Írd be a parancsot a watcher mappájában megnyitott terminálba (lásd [Mielőtt elkezdenéd](before-you-start.md)). Ha nem sikerül, az utolsó sor megmondja, miért; a [Telepítés és futtatás](installing-and-running.md) a szokásos okokat ismerteti.

`python -m heat3d_watch setup dirt-rally-2` felsorolja, mely fájlokat módosítaná; `python -m heat3d_watch setup dirt-rally-2 --apply` módosítja őket, az eredetit `<file>.heat3d-backup` néven megtartva (lásd [Parancsok](commands.md#setup)). Minden módosításról kiírja a `dirt-rally-2: changed: ...` sort, vagy a `dirt-rally-2: nothing to change` sort, ha már be van kapcsolva.

## Hogyan működik

A versenyjátékok saját telemetriája: a Forza, az Assetto Corsa játékok, a ralikjátékok és a BeamNG, útvonalakként, körökként és szakaszokként rögzítve.

Itt minden játék szándékosan teszi közzé a telemetriáját, műszerfalakhoz és mozgató szimulátorokhoz; semmit sem injektálnak, és nem olvasnak olyat, amit a játék nem ad ki. A dekódolás nem készül el kétszer: a gamecapture körrögzítői a 3DHeat GameCapture `heat3d_capture/telemetry` mappájából származnak, a `heat3d_watch/decoders` mappába másolva (ott a közzétett elrendezésekből épített csomagokon tesztelve), és ez a modul ezek kereteit a watcher sorainak alakítja: az autó helyzete másodpercenként többször a sebességgel, fokozattal és pedálokkal, egy esemény körönként vagy szakaszonként, valamint a számok, amelyeket a versenyző nyilvántart: körök, legjobb kör, távolság, legnagyobb sebesség.

#### Forza (Horizon 4/5/6, Motorsport)

"Data Out" UDP, a játék HUD- és játékbeállításaiban bekapcsolva, a 127.0.0.1 1-es porton 5300, Dash formátum. Szimulációs ciklusonként egy csomag; a dash-blokk eltolását a csomagokból találja meg (`forza.detect_layout`). Világ méterben, Y felfelé; a világ balkezes, és úgy rajzolódik ki, ahogy érkezik, ahogy a körrögzítő is teszi (a Forza Motorsport és a Forza Horizon "Data Out" dokumentációja szerint).
A játék egy portra küld, és az FH Companion és más Data Out alkalmazások ugyanazon a porton figyelnek. Két program nem oszthatja meg: Windowsban a 127.0.0.1-hez kötött socket kapja a csomagokat, a minden címre kötött socket ugyanazon a porton egyet sem, bármelyik indult előbb. Ezért a watcher egy kicsit vár, miután a játék elindult, mielőtt elfoglalja a portot, sosem veszi el egy olyan alkalmazástól, amely már tartja, és azonnal elengedi, amint egy másik alkalmazás ott figyelni kezd.
Miközben tartja a portot, minden csomagot változatlanul továbbít a 127.0.0.1:5301 címre: állítsd az FH Companion portmezőjét (a telemetria fülén) 5301-re, és mindkettő rögzít.

#### Minden megtartva

A sorok másodpercenként néhányan vannak; a játékok ennél sokkal többet küldenek. Minden UDP-csomag, amely megérkezik – a menükben, körök között, azok, amelyeket egyetlen dekóder sem olvas –, egészben megmarad a munkamenet `heat.raw.parquet` fájljában a formátuma alatt (`dash-horizon`, `session_update`, `extradata3`, `H3D1`, ...), és minden megosztott memórialap (a teljes leképezés, nem csak a dekódolt bájtok), amikor változik, a leképezése nevén (`acpmf_physics`, ...). A `used` jelöli azt, ami sorrá is vált; a `meta.json` `selfCheck.completeness` adatai típusonként számolják (a 3DHeat konvertálási szabálya).

Ugyanez a modul szolgálja ki még: [Assetto Corsa (élő adatok)](game-assetto-corsa.md), [Assetto Corsa Competizione (élő adatok)](game-assetto-corsa-competizione.md), [Assetto Corsa EVO (élő adatok)](game-assetto-corsa-evo.md), [Assetto Corsa Rally (élő adatok)](game-assetto-corsa-rally.md), [BeamNG.drive (élő adatok)](game-beamng.md), [EA SPORTS WRC (élő adatok)](game-ea-wrc.md), [Forza Horizon 4 (élő adatok)](game-forza-horizon-4.md), [Forza Horizon 5 (élő adatok)](game-forza-horizon-5.md), [Forza Horizon 6 (élő adatok)](game-forza-horizon-6.md), [Forza Motorsport (élő adatok)](game-forza-motorsport.md), [Richard Burns Rally (élő adatok)](game-richard-burns-rally.md).

## Pozíciók és tengelyek

| | |
|---|---|
| Rögzített pozíciók | igen |
| Felfelé mutató tengely | `y` |
| Mértékegység | méter |
| Tükrözés a megjelenítőnek | nincs |
| Mértékskála (`scale`: a megjelenítő ezzel szorozza a pozíciókat) | 1 |

Ezek bekerülnek minden munkamenet `meta.json` fájljának `axes` mezőjébe, és ha a munkamenetnek vannak pozíciói, a `heat.parquet` láblécébe, így a 3DHeat megjelenítő maga forgatja és méretezi a sorokat – lásd [Az adatok](the-data.md).

## Többjátékos mód

- Online játékként jelölve (`multiplayer`): **igen**. A `games --markdown` ezt így jeleníti meg: "engedélyezett (csak azt olvassa, amit a játék közzétesz)".
- Típus `telemetry`: csak azt olvassa, amit a játék vagy a platform kiad (egy UDP-port vagy megosztott memória, amelyet a játék közzétesz), ezért online játék közben is rögzít, nem csak offline; a jelző csak azt dönti el, szabad-e egyáltalán memóriát olvasni.
- Memória: ez az adapter **soha** nem olvas memóriát. Csak a `memory` adapterek olvasnak memóriát, és soha nem olyan játékhoz, amely online játékként van jelölve – lásd [Források és szabályok](sources-and-rules.md).

## Rögzített statisztikák

Ennek az adapternek a kódja névről név beállított statisztikakulcsai (minden munkamenet `stats` mezője a `meta.json`-ban és a `watcher.sqlite` `stats` táblájában):

`best_lap`, `best_stage`, `distance_km`, `laps`, `stages`, `top_speed_kmh`

A kapcsos zárójelben lévő kulcsot futásidőben töltik ki (`score.{team}` csapatonként egy kulcs). Azok a kulcsok, amelyeket a kód a játék mezőinek táblázatából vagy a játék saját statisztikanevéből vesz, nincsenek ebben a listában; a fenti "Mit rögzít" rész nevezi meg őket.

## Teljesség

A watcher követi a 3DHeat [konvertálási szabályát](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md): amit a forrás tartalmaz, azt beolvassa vagy megtartja, soha nem dobja el. A sorokon kívül minden csomagot, lapot, sort vagy választ, amelyet az adapter kap, egészben megtart a munkamenet `heat.raw.parquet` fájljában (oszlopai `time`, `ms`, `type`, `used`, `payload`, `text`, majd minden név szerint megtartott mező; a `used` jelöli, ami sorrá is vált), a `meta.json` `selfCheck.completeness` adatai pedig minden `type`-ot számolnak – a `lost` értéke 0.

**Beolvasva**

- 10 Hz-es sorok: pozíció, sebesség, fokozat, gáz, fék, szakasz-távolság, yaw, fordulatszám, kormányzás; szakaszkezdet, befejezés a szakaszidővel, újraindítások

**Nyers formában megtartva**

- minden csomag, amely eléri a portot, egészben, a játék ütemében, a formátuma alatt: `extradata3` (66 float, 264 bájt), `extradata3-64` (a DiRT Rally 64-es változata), egyébként `<n>-byte`
- a soron túli csomagban: mind a 66 float – világsebesség, oldal- és előrevektor, kerekenkénti felfüggesztési pozíció és sebesség, érintkezési felület sebessége és fékhőmérséklet, g-erők, körök, szakaszhossz; a névtelen floatok a körfájlokban `float<i>` néven szerepelnek

**Nem elérhető**

- más autók: a játékok csak a játékos autóját küldik
- kézifék-csatorna: a csomagban nincs

**Méret**: óránként körülbelül 70 MB 60 csomag/másodperces ütemnél (264 bájt plusz 70 bájtos elemfejléc); a zstd egy töredékére tömöríti

## Ellenőrizve

a dekódolás a gamecapture körrögzítőjéé (a dokumentált elrendezésekből épített csomagokon tesztelve); az adapter a tesztben épített csomagokon tesztelve, UDP-n küldve; a játékon még nem tesztelve

## Forrás

[heat3d_watch/adapters/racing.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/racing.py)

<!-- Generated from the adapter by tools/gen_game_pages.py; change the adapter and run it again rather than editing this page. -->
