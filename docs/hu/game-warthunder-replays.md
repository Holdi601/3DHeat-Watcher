---
title: "War Thunder (visszajátszások)"
nav_order: 46
lang: "hu"
source: game-warthunder-replays.md
source_hash: "81f03926431d"
nav_exclude: true
search_exclude: true
---
# War Thunder (visszajátszások) {#war-thunder-replays}

Miután egy War Thunder-meccs véget ért, a watcher a játék által elmentett visszajátszást olyan fájlokká alakítja, amelyeket a 3DHeat megtekintőben egy térképen is megnézhetsz.

*Technikai részletek: adapter `warthunder-replays`, típus [`replay`](sources-and-rules.md); folyamatosan fut (nem vár arra, hogy játék induljon), és 5 másodpercenként keres új adatot.*

## Mit rögzít {#what-is-recorded}

- minden repülőgép pozícióját és állását másodpercenként körülbelül 4-szer (ahányszor a visszajátszás tartalmazza)
- földi egységek pozícióit a visszajátszás földi szinkronjából (2026-os visszajátszásokban; a 2025-ösekben nincs)
- ki volt az egyes egység (játékos, járműazonosító, csapat), ahol egy ölés vagy találat megnevezi; ölések, halálok és találatok ott, ahol történtek; csevegés; a térkép
- a visszajátszást készítő szerző ölései, halálai, pontszáma és elfoglalásai statisztikaként

## Honnan jön {#where-it-comes-from}

a visszajátszások, amelyeket a War Thunder ment: &lt;War Thunder>/Replays/\*.wrpl (ha a visszajátszás-mentés be van kapcsolva), átalakítva a külső `heat3d-wt-replay` átalakítóval (exporters/ext/warthunder-replay)

## Hogyan kapcsolható be {#how-to-switch-it-on}

kapcsold be a visszajátszások mentését a War Thunder beállításaiban, és telepítsd az átalakítót: pip install -e &lt;3DHeat>/exporters/ext/warthunder-replay

Beállítások környezeti változókból:

- `HEAT3D_WT_REPLAY`: az átalakító mappája (klón vagy kicsomagolt kiadás), ha nincs telepítve, vagy nincs a watcher mellett

## Hogyan működik {#how-it-works}

Visszajátszások és demók: amit a játék egy meccsről elment, a meccs véget érése után átalakítva.

A visszajátszás mindent tartalmaz, amit a több játékos meccseken élő felület visszatart – minden játékos pozícióját, minden ölést ott, ahol történt –, és a játék azt a fájlt a játékosainak írja, így az olvasása nem nyúl a játékhoz. A watcher figyeli azokat a mappákat, ahová a játékok mentik őket, megvárja, amíg egy új fájl nem nő tovább (különben a játék még írja), és egy munkaszálban alakítja át, így egy hosszú átalakítás nem tartja fel a watchert.

Az első alkalommal, amikor egy mappát látnak, a benne lévő visszajátszásokat csak feljegyzik, nem alakítják át: aki évek demóit tárolja, különben a watcher egy napig lenne lefoglalva. A `python -m heat3d_watch replays <adapter> [folder]` kérésre átalakítja a meglévőket.

#### War Thunder {#war-thunder}

A War Thunder minden csatáról visszajátszást ment a `<War Thunder>/Replays/*.wrpl` mappába, ha a visszajátszás-mentés be van kapcsolva a beállításaiban. A watcher maga nem olvassa őket: ezt egy külső átalakító teszi (3DHeat War Thunder visszajátszás-átalakító, `exporters/ext/warthunder-replay`, `heat3d-wt-replay` parancs), külön tartva, hogy egy vele kapcsolatos gond semmi mást ne érintsen. Ha a parancs elérhető a PATH-on, vagy a csomag telepítve van, illetve a watcher mellett van, minden új visszajátszást lefuttat rajta, és az eredmény a munkamenet mappájába kerül `<map>/<match>.parquet` és `<match>.match.json` formában; ha nincs, a watcher egyszer megmondja, hogyan kell telepíteni, és a mappához nem nyúl. Hogy mit olvas be az átalakító, és mit nem, az a README-jében van. A visszajátszást készítő szerző eredménysora – ölések, földi ölések, halálok, asszisztok, pontszám, elfoglalások – lesz a munkamenet statisztikája.

Ugyanez a modul szolgálja ki ezeket is: [Counter-Strike 2 (visszajátszások)](game-cs2-demos.md), [Dota 2 (visszajátszások)](game-dota-replays.md), [osu! (visszajátszások)](game-osu-replays.md), [Squad (visszajátszások)](game-squad-demos.md), [World of Tanks (visszajátszások)](game-wot-replays.md), [World of Warships (visszajátszások)](game-wows-replays.md).

## Pozíciók és tengelyek {#positions-and-axes}

| | |
|---|---|
| Pozíciók rögzítve | igen |
| Felfelé mutató tengely | `y` |
| Mértékegység | méter (x kelet, y felfelé, z észak) |
| Tükrözve a megtekintőnek | `z` |
| Mértékegység-szorzó (`scale`: a megtekintő ezzel szorozza a pozíciókat) | 1 |

Ezek bekerülnek minden munkamenet `meta.json`-jába (`axes`), és ha a munkamenetnek vannak pozíciói, a `heat.parquet` láblécébe is, így a 3DHeat megtekintő maga forgatja és méretezi a sorokat – lásd [Az adatok](the-data.md).

## Többjátékos {#multiplayer}

- Online játszottként jelölve (`multiplayer`): **igen**. A `games --markdown` ezt így mutatja: "allowed (reads only what the game publishes)", vagyis engedélyezett, csak azt olvassa, amit a játék közzétesz.
- `replay` típus: csak azt olvassa, amit a játék vagy a platform kiad (a játék által mentett visszajátszásokat és demókat), így online játékban is rögzít, nemcsak offline; a jelző csak azt dönti el, szabad-e valaha memóriát olvasni.
- Memória: ez az adapter **soha** nem olvas memóriát. Csak a `memory` adapterek olvasnak memóriát, és soha nem olyan játékhoz, amelyet online játszottként jelöltek meg – lásd [Források és szabályok](sources-and-rules.md).

## Rögzített statisztikák {#statistics-recorded}

Statisztikakulcsok, amelyeket ennek az adapternek a kódja név szerint állít be (minden munkamenet `stats`-ja a `meta.json`-ban és a `watcher.sqlite` `stats` táblájában):

`map`

Kapcsos zárójelben lévő kulcsot futás közben egészítünk ki (`score.{team}` csapatonként egy kulcs). A kódnak a játék mezőinek táblázatából vagy a játék saját statisztikanevéből származó kulcsai nincsenek ebben a listában; a fenti "Mit rögzít" részben vannak megnevezve.

## Teljesség {#completeness}

Az átalakító, amelyet ez az adapter futtat, követi a 3DHeat [átalakítási szabályát](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md): amit a visszajátszás tartalmaz, azt beolvassuk vagy megtartjuk, soha nem dobjuk el – a táblába és a meccsdokumentumba olvassuk, minden más egészben megmarad mellettük, külön fájlokban, és a meccsdokumentum `selfCheck.completeness` részében számoljuk. Az átalakító saját dokumentációja felsorolja, mit olvas be, mit tart meg nyersen, és mit nem tud beolvasni.

## Ellenőrizve {#verified}

az átalakítót több játékverzióból származó nyilvános visszajátszásokon ellenőriztük (az ölések és nevek egyeznek az eredményekkel), és építetett visszajátszásokon futó tesztekkel; a hívást (hook) helyettesítő paranccsal futó tesztekkel

## Forrás {#source}

[heat3d_watch/adapters/replays.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/replays.py)

<!-- A heat3d_watch adapterből készült a tools/gen_game_pages.py által; az adaptert módosítsd, és futtasd újra, ne ezt az oldalt szerkeszd. -->
