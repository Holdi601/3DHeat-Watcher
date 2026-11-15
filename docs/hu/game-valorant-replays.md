---
title: "VALORANT (visszajátszások)"
nav_order: 45
lang: "hu"
source: game-valorant-replays.md
source_hash: "10a648aabdf1"
nav_exclude: true
search_exclude: true
---
# VALORANT (visszajátszások) {#valorant-replays}

Egy VALORANT-meccs után a watcher a játék által mentett visszajátszást olyan fájlokká alakítja, amelyeket statisztikaként és idővonalként megnézhetsz.

*Műszaki részletek: adapter `valorant-replays`, típus [`replay`](sources-and-rules.md); mindig fut (nem vár a játék indulására), és 5 másodpercenként keres új adatot.*

## Mit rögzít {#what-is-recorded}

- a pálya, a meccs azonosítója és a kiválasztott ügynökök; a visszajátszás információs blokkja (hossz, verziók, név, felvételi idő, tömörítési és titkosítási jelzők)
- a szerver eseményidővonala: ölések (ölő és áldozat hálózati azonosítóval), körök kezdete, felrakott spike-ok, hatástalanítva, és felrobbanva, használt ultimate-ek, oldalcsere – mindegyik az azonosítójával és metaadataival
- a fájl minden darabja egészben a heat.raw.parquet fájlban; nincs dekódolva: a pozíciók, nevek vagy pontszámok a megzavarozott folyamban vannak

## Honnan származik {#where-it-comes-from}

a VALORANT által mentett visszajátszások: %LOCALAPPDATA%/VALORANT/Saved/Demos/\*.vrf (csak azok a részek, amelyek nincsenek megzavarozva)

## Hogyan kapcsold be {#how-to-switch-it-on}

Mentsd el a visszajátszást a VALORANTban (karrier > meccs > visszajátszás letöltése)

## Hogyan működik {#how-it-works}

League of Legends és VALORANT visszajátszások: amit belőlük nyíltan lehet olvasni.

Mindkét játék a játékos lemezére menti a visszajátszásokat, és mindkettő védi a tartalmát: a pillanatról pillanatra zajló játékadatok megzavarozottak, és minden javítással másképp, hogy ne lehessen csalásra használni. Ezen átjutni azt jelentené, hogy a játék saját kódját szedjük szét, amit a Riot szerződési feltételei tiltanak (Szolgáltatási feltételek 3.1 és 7.1 pont) – ezért ezt nem tesszük meg. Amit minden fájl nyíltan hordoz, azt beolvassuk, a többit érintetlenül megtartjuk: a fájl minden része egészben, a munkamenet `heat.raw.parquet` fájljában (a 3DHeat konvertálási szabálya, a megjelenítő tárolójában a docs/converters.md), és a meta.json `selfCheck.completeness` adatai számolják.

#### Valorant (.vrf) {#valorant-vrf}

`%LOCALAPPDATA%\VALORANT\Saved\Demos\*.vrf`, egy Unreal Engine helyi visszajátszás (az elrendezés a vrfkit (Apache-2.0) és a ValorantReplayParser (MIT) alapján). Nyíltan: a visszajátszás információs blokkja (hossz, hálózati verzió, changelist, neve, mikor vették fel, tömörített-e vagy titkosított), a pálya, a meccs azonosítója és a kiválasztott ügynökök (a fejlécben), valamint a szerver saját eseményidővonala – ölések (ölő és áldozat hálózati azonosítóval, nem névvel), körök kezdete, felrakott spike-ok, hatástalanítva és felrobbanva, használt ultimate-ek, oldalcsere – mindegyik az idejével, azonosítójával és metaadataival. A pozíciók, nevek, pontszámok és minden más a megzavarozott folyamban van (a visszajátszás-adat és ellenőrzőpont darabjai), ami egészben megmarad és nincs olvasva.

Ugyanez a modul szolgálja ki még: [League of Legends (visszajátszások)](game-lol-replays.md).

## Pozíciók és tengelyek {#positions-and-axes}

| | |
|---|---|
| Rögzített pozíciók | nem |
| Felfelé mutató tengely | `z` |
| Mértékegység | VALORANT világegységek |
| Tükrözés a megjelenítőnek | nincs |
| Mértékskála (`scale`: a megjelenítő ezzel szorozza a pozíciókat) | 1 |

Ezek bekerülnek minden munkamenet `meta.json` fájljának `axes` mezőjébe, és ha a munkamenetnek vannak pozíciói, a `heat.parquet` láblécébe, így a 3DHeat megjelenítő maga forgatja és méretezi a sorokat – lásd [Az adatok](the-data.md).

## Többjátékos mód {#multiplayer}

- Online játékként jelölve (`multiplayer`): **igen**. A `games --markdown` ezt így jeleníti meg: "engedélyezett (csak azt olvassa, amit a játék közzétesz)".
- Típus `replay`: csak azt olvassa, amit a játék vagy a platform kiad (a játék által mentett visszajátszásokat és demókat), ezért online játék közben is rögzít, nem csak offline; a jelző csak azt dönti el, szabad-e egyáltalán memóriát olvasni.
- Memória: ez az adapter **soha** nem olvas memóriát. Csak a `memory` adapterek olvasnak memóriát, és soha nem olyan játékhoz, amely online játékként van jelölve – lásd [Források és szabályok](sources-and-rules.md).

## Rögzített statisztikák {#statistics-recorded}

Ennek az adapternek a kódja névről név beállított statisztikakulcsai (minden munkamenet `stats` mezője a `meta.json`-ban és a `watcher.sqlite` `stats` táblájában):

`kills_in_match`, `map`, `match_seconds`, `rounds`, `spikes_planted`

A kapcsos zárójelben lévő kulcsot futásidőben töltik ki (`score.{team}` csapatonként egy kulcs). Azok a kulcsok, amelyeket a kód a játék mezőinek táblázatából vagy a játék saját statisztikanevéből vesz, nincsenek ebben a listában; a fenti "Mit rögzít" rész nevezi meg őket.

## Teljesség {#completeness}

A watcher követi a 3DHeat [konvertálási szabályát](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md): amit a forrás tartalmaz, azt beolvassa vagy megtartja, soha nem dobja el. A sorokon kívül minden csomagot, lapot, sort vagy választ, amelyet az adapter kap, egészben megtart a munkamenet `heat.raw.parquet` fájljában (oszlopai `time`, `ms`, `type`, `used`, `payload`, `text`, majd minden név szerint megtartott mező; a `used` jelöli, ami sorrá is vált), a `meta.json` `selfCheck.completeness` adatai pedig minden `type`-ot számolnak – a `lost` értéke 0.

**Beolvasva**

- az információs blokk, minden mezője (meta.json `vrf`): fájlverzió, egyedi verziók, hossz, hálózati verzió, changelist, név, élő-jelző, felvételi idő, tömörített és titkosított jelzők, a kulcs ahogy tárolva van
- a fejléc-darab: a pálya, a meccs azonosítója és a kiválasztott ügynökök (alakjuk alapján keresve)
- minden eseménydarab: azonosító, csoport, metaadatok, kezdő- és végidő, és az adatából az esemény neve, az időpontja másodpercben és az előtte álló számok (ölő és áldozat hálózati azonosítója) – soronként egy

**Nyers formában megtartva**

- minden darab egészben, a fájl sorrendjében (`offset`), így a részek kiadják a fájlt: `info`, `header`, `event <group>`, `replay_data`, `checkpoint`, `chunk <n>` a típusra, amelyet az elrendezés nem nevez meg, `trailing` az utolsó teljes darab utáni bájtokra

**Nem elérhető**

- pozíciók, nevek, pontszámok, képességek, a játék minden képkockája: a visszajátszás-adat és az ellenőrzőpont-darabok megzavarozottak; ezek olvasása azt jelentené, hogy a kliens szét van szedve, amit a Riot feltételei tiltanak. Egészben megtartva, nincs olvasva
- titkosított visszajátszás tartalma: bejárva és egészben megtartva, belül semmi sincs olvasva

**Méret**: a nyers melléklet nagyjából a visszajátszás saját mérete: a megzavarozott folyam nem tömörül

## Ellenőrizve {#verified}

a vrfkit (Apache-2.0) által dokumentált konténer-elrendezésből épített fájlokon; valódi visszajátszáson még nem tesztelve, nem állt rendelkezésre – olvasás előtt ellenőriz, és azt, ami nem egyezik, kihagyja

## Forrás {#source}

[heat3d_watch/adapters/riot_replays.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/riot_replays.py)

<!-- Generated from the adapter by tools/gen_game_pages.py; change the adapter and run it again rather than editing this page. -->
