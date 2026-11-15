---
title: "Elite Dangerous (naplófájlok)"
nav_order: 18
lang: "hu"
source: game-elite.md
source_hash: "bb5bcf75553a"
nav_exclude: true
search_exclude: true
---
# Elite Dangerous (naplófájlok) {#elite-dangerous-log-files}

Amíg az Elite Dangerous-t játszod, a watcher beolvassa a játék által írt fájlokat, és elmenti, mi történt, így később megnézheted térképen a 3DHeat megjelenítőben.

*Műszaki részletek: adapter `elite`, típus [`log`](sources-and-rules.md); akkor fut, amikor az `EliteDangerous64.exe` fut, és 0,25 másodpercenként keres új adatot.*

## Mit rögzít {#what-is-recorded}

- minden naplóesemény a maga naplónevén, egyszerű mezőivel
- galaxisbeli pozíció (StarPos, fényév) ugráskor, helyszíneknél, megjelenéseknél, halálnál, dokkolásnál, leszállásnál
- megjelenés a LoadGame/Resurrect eseményen, halál a Died eseményen, dokkolás/kidokkolás, érintkezés/felszállás, ugrás, session_end
- bolygófelszíni útvonal a Status.json-ból: szélesség, hosszúság, magasság, irány, és méterben egy érintősíkban testenként (munkamenet = a test neve), a Status.json többi egyszerű mezőjével (Flags, Flags2, GuiFocus, LegalState, ...)
- minden naplósor és minden társfájl egészben a heat.raw.parquet fájlban
- ugrások, megtett ugrástávolság, halálok, ölések, megszerzett kreditek, teljesített küldetések, átvizsgált testek, meglátogatott rendszerek, dokkolások, leszállások

## Honnan származik {#where-it-comes-from}

Játékosnapló %USERPROFILE%\Saved Games\Frontier Developments\Elite Dangerous\Journal.\*.log (a legújabb fájl, íráskor követve), Status.json és a többi társ-\*.json fájl (Market, Outfitting, Shipyard, NavRoute, Cargo, ModulesInfo, ShipLocker, Backpack, FCMaterials) ugyanabban a mappában

## Hogyan kapcsold be {#how-to-switch-it-on}

Semmit sem kell bekapcsolni: a watcher úgy olvassa a forrást, ahogy a játék vagy a platform biztosítja.

## Hogyan működik {#how-it-works}

Elite Dangerous: a Player Journal és a Status.json, amelyeket a játék futás közben ír.

Hol: `%USERPROFILE%\Saved Games\Frontier Developments\Elite Dangerous\`

* `Journal.<yyyy-mm-ddThhmmss>.<part>.log` – soronként egy JSON-objektum, indításonként egy fájl (a hosszú munkamenet a .02, .03 ... részben folytatódik). Minden sornak van `timestamp` (UTC, ISO 8601) és `event` mezője. A galaxisbeli pozíciók a rendszer `StarPos` [x, y, z] értékei, fényévben, a Sol-tól mérve, az `FSDJump`, a `Location` és a `CarrierJump` eseményeknél. Az Elite galaktikus koordinátarendszere y felfelé mutat (a galaktikus észak felé), z a galaxis magja felé, x pedig a 270-es galaktikus hosszúság felé – ez balkezes rendszer, ezért a megjelenítő tükrözi a z tengelyt, hogy a helyes irányban rajzolja ki.
* `Status.json` – az egészben újraírt fájl, valahányszor a hajó állapota változik: `Flags`, bolygó közelében pedig `Latitude`, `Longitude` (fok), `Altitude` (méter), `Heading`, `BodyName` és `PlanetRadius` (méter).
* A többi társfájl, mindegyik egészben újraíródik, amikor a megfelelő naplóesemény íródik: `Market.json`, `Outfitting.json`, `Shipyard.json`, `NavRoute.json`, `Cargo.json`, `ModulesInfo.json`, `ShipLocker.json`, `Backpack.json`, `FCMaterials.json`. A mappa minden olyan `*.json` fájlja, amelyet a játék ebben a játékmenetben ír, egészben megmarad, valahányszor változik (3DHeat konvertálási szabálya: amit a forrás tartalmaz, azt beolvassák vagy megtartják), a fájlnevén.

Minden naplósor egészben megmarad a munkamenet nyers melléklet-fájljában az `event` neve alatt, minden társfájl a fájlnevén; a nem JSON-sor az `unparsed` alatt.

A felszíni pozíciókat testenként egy helyi érintősíkba tesszük, méterben: egy testen az első rögzítés a kezdőpont, x kelet, z észak, y felfelé (magasság), ugyanaz a kézrendszer, mint a galaxis-koordinátáké; a sorok a test nevét viszik `session` mezőjükbe, így egy bolygón tett autózás vagy séta saját útvonalként rajzolódik ki. A galaxis-sorok `session` értéke "galaxy". A két skála ugyanabban a táblában van; a munkamenetet a megjelenítőben válaszd ki.

Formátum: Frontier "Elite Dangerous Player Journal" kézikönyve (minden frissítéssel közzéteszik a hivatalos fórumon, <https://forums.frontier.co.uk/> – "Journal Manual", v4.x), az események és mezők ott leírtak szerint; a Status.json jelzőit ugyanannak a kézikönyvnek a "Status File" fejezete szerint.

## Pozíciók és tengelyek {#positions-and-axes}

| | |
|---|---|
| Rögzített pozíciók | igen |
| Felfelé mutató tengely | `y` |
| Mértékegység | fényév (galaxis-sorok, munkamenet 'galaxy'); méter kelet/fel/észak irányban a testen az első rögzítéstől (felszíni sorok, munkamenet = a test neve) |
| Tükrözés a megjelenítőnek | `z` |
| Mértékskála (`scale`: a megjelenítő ezzel szorozza a pozíciókat) | 1 |

Ezek bekerülnek minden munkamenet `meta.json` fájljának `axes` mezőjébe, és ha a munkamenetnek vannak pozíciói, a `heat.parquet` láblécébe, így a 3DHeat megjelenítő maga forgatja és méretezi a sorokat – lásd [Az adatok](the-data.md).

## Többjátékos mód {#multiplayer}

- Online játékként jelölve (`multiplayer`): **igen**. A `games --markdown` ezt így jeleníti meg: "engedélyezett (csak azt olvassa, amit a játék közzétesz)".
- Típus `log`: csak azt olvassa, amit a játék vagy a platform kiad (fájlok, amelyeket a játék futás közben ír), ezért online játék közben is rögzít, nem csak offline; a jelző csak azt dönti el, szabad-e egyáltalán memóriát olvasni.
- Memória: ez az adapter **soha** nem olvas memóriát. Csak a `memory` adapterek olvasnak memóriát, és soha nem olyan játékhoz, amely online játékként van jelölve – lásd [Források és szabályok](sources-and-rules.md).

## Rögzített statisztikák {#statistics-recorded}

Ennek az adapternek a kódja névről név beállított statisztikakulcsai (minden munkamenet `stats` mezője a `meta.json`-ban és a `watcher.sqlite` `stats` táblájában):

`bad_lines`, `bodies_scanned`, `carrier_jumps`, `credits`, `credits_earned`, `deaths`, `distance_ly`, `dockings`, `jumps`, `kills`, `landings`, `missions_completed`, `ship`, `surface_fixes`, `systems_visited`

A kapcsos zárójelben lévő kulcsot futásidőben töltik ki (`score.{team}` csapatonként egy kulcs). Azok a kulcsok, amelyeket a kód a játék mezőinek táblázatából vagy a játék saját statisztikanevéből vesz, nincsenek ebben a listában; a fenti "Mit rögzít" rész nevezi meg őket.

## Teljesség {#completeness}

A watcher követi a 3DHeat [konvertálási szabályát](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md): amit a forrás tartalmaz, azt beolvassa vagy megtartja, soha nem dobja el. A sorokon kívül minden csomagot, lapot, sort vagy választ, amelyet az adapter kap, egészben megtart a munkamenet `heat.raw.parquet` fájljában (oszlopai `time`, `ms`, `type`, `used`, `payload`, `text`, majd minden név szerint megtartott mező; a `used` jelöli, ami sorrá is vált), a `meta.json` `selfCheck.completeness` adatai pedig minden `type`-ot számolnak – a `lost` értéke 0.

**Beolvasva**

- minden naplósor sorként a maga `event` neve alatt, egyszerű mezőivel (ahol a játék ad helyi szöveget, azt; a 300 karakternél hosszabb szövegek a sorban csonkolva)
- galaxis-sorok (StarPos) az FSDJump, CarrierJump, Location, LoadGame, Resurrect, Died, Docked, Undocked, Touchdown, Liftoff, Shutdown eseményeknél; felszíni sorok a Status.json-ból és a Touchdown/Liftoff eseményekből
- a Status.json egyszerű mezői (Flags, Flags2, GuiFocus, LegalState, Cargo, FireGroup, Oxygen, Health, Temperature, Gravity, SelectedWeapon, ...) a felszíni sorokon
- a statisztikák: ugrások, távolság, halálok, ölések, megszerzett kreditek, küldetések, átvizsgált testek, meglátogatott rendszerek, dokkolások, leszállások

**Nyers formában megtartva**

- minden naplósor egészben, `type` = az `event` (FSDJump, Scan, Music, ReceiveText, ...), `used` igaz: a listák és objektumok, amelyeket a sorok kihagynak (StarPos, Factions, Rewards, Killers, Materials, Modules, ...), csak itt vannak meg
- nem JSON-naplósor, `type` `unparsed`
- minden társfájl egészben, valahányszor a játék újraírja, `type` = a fájlneve: `Status.json` (`used`, ha felszíni sort készített), `Market.json`, `Outfitting.json`, `Shipyard.json`, `NavRoute.json`, `Cargo.json`, `ModulesInfo.json`, `ShipLocker.json`, `Backpack.json`, `FCMaterials.json`, és minden más `*.json`, amelyet a játék ott ír

**Nem elérhető**

- pozíció ugrások között (rendszeren belül, supercruise-ban vagy normál térben): a játék csak a rendszer StarPos-át írja, bolygó közelében pedig szélességet, hosszúságot és magasságot
- más hajók és játékosok pozíciói: a napló a parancsnok saját beszámolója
- sebesség, gáz és más repülési telemetria: a játék ezeket nem írja
- korábbi játékmenetek naplói és társfájljai: akkor rögzülnek, amikor játszottak velük (a követő a fájl végén kezd, amely régebbi, mint ennek a játéknak a futása)
- a Frontier társ-webes API-ja (cAPI): a játékos Frontier-bejelentkezést igényel; nem a játék által írt fájl

**Méret**: óránként körülbelül 1–5 MB nyers szöveg: a napló 0,2–2 MB, a Status.json (1 KB alatt, másodpercenként legfeljebb egyszer újraírva) 1–2 MB, egy piac/felszerelés/hajógyár készlet 20–150 KB állomásonként; a zstd a heat.raw.parquet fájlban nagyjából a tizedére tömöríti

## Ellenőrizve {#verified}

a naplóelemző valódi telepített játék naplófájljain lefuttatva (az eseményszámok egyeznek a statisztikákkal); a Status.json felszíni rögzítései csak szintetikus pillanatképeken tesztelve

## Forrás {#source}

[heat3d_watch/adapters/elite.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/elite.py)

<!-- Generated from the adapter by tools/gen_game_pages.py; change the adapter and run it again rather than editing this page. -->
