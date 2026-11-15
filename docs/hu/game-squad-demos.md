---
title: "Squad (visszajátszások)"
nav_order: 41
lang: "hu"
source: game-squad-demos.md
source_hash: "82c24e6df01c"
nav_exclude: true
search_exclude: true
---
# Squad (visszajátszások) {#squad-replays}

Miután egy Squad-meccs véget ért, a watcher a játék által elmentett visszajátszást olyan fájlokká alakítja, amelyeket a 3DHeat megtekintőben egy térképen is megnézhetsz.

*Technikai részletek: adapter `squad-demos`, típus [`replay`](sources-and-rules.md); folyamatosan fut (nem vár arra, hogy játék induljon), és 5 másodpercenként keres új adatot.*

## Mit rögzít {#what-is-recorded}

- minden játékos pozícióját, testének irányszögét és sebességét minden alkalommal, amikor a szerver replikálja (másodpercenként legfeljebb 8-szor), gyalog és földi járművekben
- minden játékos nevét, csapatát, frakcióját és rajját, a csapatváltásokat követve
- nem: helikopterek mozgása, ölések és telepíthető eszközök – lásd az olvasó README-jét

## Honnan jön {#where-it-comes-from}

a szerverdemók, amelyeket a Squad az AdminDemoRec admin paranccsal rögzít: &lt;server>/SquadGame/Saved/Demos/\*.replay, a külső `heat3d-squad-demo` olvasóval (exporters/ext/squad-demo)

## Hogyan kapcsolható be {#how-to-switch-it-on}

rögzíts a szerveren: adj az adminnak `demos` jogosultságot az Admins.cfg fájlban, majd a játék konzoljában AdminDemoRec &lt;name>, és AdminDemoStop; másold ide a demót, és telepítsd az olvasót: pip install -e &lt;3DHeat>/exporters/ext/squad-demo

Beállítások környezeti változókból:

- `HEAT3D_SQUAD_DEMO`: az átalakító mappája (klón vagy kicsomagolt kiadás), ha nincs telepítve, vagy nincs a watcher mellett

## Hogyan működik {#how-it-works}

Visszajátszások és demók: amit a játék egy meccsről elment, a meccs véget érése után átalakítva.

A visszajátszás mindent tartalmaz, amit a több játékos meccseken élő felület visszatart – minden játékos pozícióját, minden ölést ott, ahol történt –, és a játék azt a fájlt a játékosainak írja, így az olvasása nem nyúl a játékhoz. A watcher figyeli azokat a mappákat, ahová a játékok mentik őket, megvárja, amíg egy új fájl nem nő tovább (különben a játék még írja), és egy munkaszálban alakítja át, így egy hosszú átalakítás nem tartja fel a watchert.

Az első alkalommal, amikor egy mappát látnak, a benne lévő visszajátszásokat csak feljegyzik, nem alakítják át: aki évek demóit tárolja, különben a watcher egy napig lenne lefoglalva. A `python -m heat3d_watch replays <adapter> [folder]` kérésre átalakítja a meglévőket.

#### Squad {#squad}

A Squad dedikált szerverei egy meccs demóját rögzítik, amikor egy `demos` jogosultságú admin lefuttatja az AdminDemoRec &lt;name> (és AdminDemoStop) parancsot, és a `<server>/SquadGame/Saved/Demos/<name>.replay` fájlba írják – ez egy Unreal Engine hálózati visszajátszás, benne van mindaz, amit a szerver replikált, minden játékos mozgásával együtt. A watcher maga nem olvassa őket: ezt egy külső olvasó teszi (3DHeat Squad demo olvasó, `exporters/ext/squad-demo`, `heat3d-squad-demo` parancs), külön tartva, hogy egy vele kapcsolatos gond semmi mást ne érintsen. A helyi szerver mappáiban minden új demóra lefut, vagy a beállításokban megadott mappában lévő, bérelt szerverről átmásolt demókra; a munkamenet mappájába `<map>/<match>.parquet` és `<match>.match.json` formában kerül. A réteg (layer), a térkép, a játékosok száma és a meccs hossza lesz a munkamenet statisztikája.

Ugyanez a modul szolgálja ki ezeket is: [Counter-Strike 2 (visszajátszások)](game-cs2-demos.md), [Dota 2 (visszajátszások)](game-dota-replays.md), [osu! (visszajátszások)](game-osu-replays.md), [War Thunder (visszajátszások)](game-warthunder-replays.md), [World of Tanks (visszajátszások)](game-wot-replays.md), [World of Warships (visszajátszások)](game-wows-replays.md).

## Pozíciók és tengelyek {#positions-and-axes}

| | |
|---|---|
| Pozíciók rögzítve | igen |
| Felfelé mutató tengely | `z` |
| Mértékegység | Unreal-egységek (centiméter) |
| Tükrözve a megtekintőnek | nincs |
| Mértékegység-szorzó (`scale`: a megtekintő ezzel szorozza a pozíciókat) | 1 |

Ezek bekerülnek minden munkamenet `meta.json`-jába (`axes`), és ha a munkamenetnek vannak pozíciói, a `heat.parquet` láblécébe is, így a 3DHeat megtekintő maga forgatja és méretezi a sorokat – lásd [Az adatok](the-data.md).

## Többjátékos {#multiplayer}

- Online játszottként jelölve (`multiplayer`): **igen**. A `games --markdown` ezt így mutatja: "allowed (reads only what the game publishes)", vagyis engedélyezett, csak azt olvassa, amit a játék közzétesz.
- `replay` típus: csak azt olvassa, amit a játék vagy a platform kiad (a játék által mentett visszajátszásokat és demókat), így online játékban is rögzít, nemcsak offline; a jelző csak azt dönti el, szabad-e valaha memóriát olvasni.
- Memória: ez az adapter **soha** nem olvas memóriát. Csak a `memory` adapterek olvasnak memóriát, és soha nem olyan játékhoz, amelyet online játszottként jelöltek meg – lásd [Források és szabályok](sources-and-rules.md).

## Rögzített statisztikák {#statistics-recorded}

Statisztikakulcsok, amelyeket ennek az adapternek a kódja név szerint állít be (minden munkamenet `stats`-ja a `meta.json`-ban és a `watcher.sqlite` `stats` táblájában):

`layer`, `map`, `match_seconds`, `players`

Kapcsos zárójelben lévő kulcsot futás közben egészítünk ki (`score.{team}` csapatonként egy kulcs). A kódnak a játék mezőinek táblázatából vagy a játék saját statisztikanevéből származó kulcsai nincsenek ebben a listában; a fenti "Mit rögzít" részben vannak megnevezve.

## Teljesség {#completeness}

Az átalakító, amelyet ez az adapter futtat, követi a 3DHeat [átalakítási szabályát](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md): amit a visszajátszás tartalmaz, azt beolvassuk vagy megtartjuk, soha nem dobjuk el – a táblába és a meccsdokumentumba olvassuk, minden más egészben megmarad mellettük, külön fájlokban, és a meccsdokumentum `selfCheck.completeness` részében számoljuk. Az átalakító saját dokumentációja felsorolja, mit olvas be, mit tart meg nyersen, és mit nem tud beolvasni.

## Ellenőrizve {#verified}

az olvasót nyilvános szerverdemókon ellenőriztük (a mozgás egyezik a hordozott sebességgel; minden sor csapata egyezik a katonája frakciójával), és építetett demókon futó tesztekkel; a hívást (hook) helyettesítő paranccsal futó tesztekkel

## Forrás {#source}

[heat3d_watch/adapters/replays.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/replays.py)

<!-- A heat3d_watch adapterből készült a tools/gen_game_pages.py által; az adaptert módosítsd, és futtasd újra, ne ezt az oldalt szerkeszd. -->
