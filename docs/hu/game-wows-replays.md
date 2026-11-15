---
title: "World of Warships (visszajátszások)"
nav_order: 49
lang: "hu"
source: game-wows-replays.md
source_hash: "c822aca3f6fe"
nav_exclude: true
search_exclude: true
---
# World of Warships (visszajátszások) {#world-of-warships-replays}

Miután egy World of Warships-meccs véget ért, a watcher a játék által elmentett visszajátszást olyan fájlokká alakítja, amelyeket a 3DHeat megtekintőben egy térképen is megnézhetsz.

*Technikai részletek: adapter `wows-replays`, típus [`replay`](sources-and-rules.md); folyamatosan fut (nem vár arra, hogy játék induljon), és 5 másodpercenként keres új adatot.*

## Mit rögzít {#what-is-recorded}

- minden hajó pozícióját és irányát, amíg a rögzítő kliens látta (mozgás közben másodpercenként körülbelül 6-7-szer), a saját hajót egész idő alatt
- játékos, szövetséges vagy ellenség, és hajó (a rögzítő játékosé névvel, a többieké a játék hajószámával); az elsüllyesztett hajók ott, ahol elsüllyedtek, az elsüllyesztőik ott, ahol álltak
- a térkép; a rögzítő játékos hajója, ölései és túlélése statisztikaként

## Honnan jön {#where-it-comes-from}

a visszajátszások, amelyeket a World of Warships ment: &lt;World of Warships>/replays/\*.wowsreplay (ha a visszajátszás be van kapcsolva), átalakítva a külső `heat3d-wows-replay` átalakítóval (exporters/ext/wows-replay)

## Hogyan kapcsolható be {#how-to-switch-it-on}

kapcsold be a visszajátszás-rögzítést a World of Warships-ben (`isReplayEnabled` a preferences.xml fájlban, vagy a játék saját beállítása, ahol van ilyen), és telepítsd az átalakítót: pip install -e &lt;3DHeat>/exporters/ext/wows-replay

Beállítások környezeti változókból:

- `HEAT3D_WOWS_REPLAY`: az átalakító mappája (klón vagy kicsomagolt kiadás), ha nincs telepítve, vagy nincs a watcher mellett

## Hogyan működik {#how-it-works}

Visszajátszások és demók: amit a játék egy meccsről elment, a meccs véget érése után átalakítva.

A visszajátszás mindent tartalmaz, amit a több játékos meccseken élő felület visszatart – minden játékos pozícióját, minden ölést ott, ahol történt –, és a játék azt a fájlt a játékosainak írja, így az olvasása nem nyúl a játékhoz. A watcher figyeli azokat a mappákat, ahová a játékok mentik őket, megvárja, amíg egy új fájl nem nő tovább (különben a játék még írja), és egy munkaszálban alakítja át, így egy hosszú átalakítás nem tartja fel a watchert.

Az első alkalommal, amikor egy mappát látnak, a benne lévő visszajátszásokat csak feljegyzik, nem alakítják át: aki évek demóit tárolja, különben a watcher egy napig lenne lefoglalva. A `python -m heat3d_watch replays <adapter> [folder]` kérésre átalakítja a meglévőket.

#### World of Tanks és World of Warships {#world-of-tanks-and-world-of-warships}

Mindkettő minden csatáról visszajátszást ment a `<game>/replays/` mappába, ha a rögzítés be van kapcsolva (`*.wotreplay`, `*.wowsreplay`); a telepítéseket a Wargaming Game Center listájában keresi a watcher, a `C:/Games/World_of_Tanks*` / `World_of_Warships*` útvonalakon, és a Steamben. A War Thunderhez hasonlóan a watcher maga nem olvassa a fájlokat: mindegyikhez külső átalakító tartozik (`exporters/ext/wot-replay`, `heat3d-wot-replay` parancs; `exporters/ext/wows-replay`, `heat3d-wows-replay` parancs), külön tartva, hogy a Wargaming feltételeivel kapcsolatos gond csak az adott átalakítót érintse. Ha a PATH-on, telepítve, vagy a watcher mellett megtalálható, minden új visszajátszást `<map>/<match>.parquet` és `<match>.match.json` fájlokká alakít a munkamenet mappájában; ha hiányzik, a watcher egyszer megmondja, hogyan kell telepíteni. A visszajátszó játékos sora – jármű vagy hajó, ölések, sebzés (World of Tanks), hogy életben maradt-e, és az eredmény (World of Tanks) – lesz a munkamenet statisztikája. Hogy mit olvas be mindegyik átalakító, és mit nem, az a README-jében van.

Ugyanez a modul szolgálja ki ezeket is: [Counter-Strike 2 (visszajátszások)](game-cs2-demos.md), [Dota 2 (visszajátszások)](game-dota-replays.md), [osu! (visszajátszások)](game-osu-replays.md), [Squad (visszajátszások)](game-squad-demos.md), [War Thunder (visszajátszások)](game-warthunder-replays.md), [World of Tanks (visszajátszások)](game-wot-replays.md).

## Pozíciók és tengelyek {#positions-and-axes}

| | |
|---|---|
| Pozíciók rögzítve | igen |
| Felfelé mutató tengely | `y` |
| Mértékegység | World of Warships világegységek (x kelet, y felfelé, z észak; egy egység 15 m a hajótest geometriája szerint, 30 m a játék hatótávolságai szerint) |
| Tükrözve a megtekintőnek | `z` |
| Mértékegység-szorzó (`scale`: a megtekintő ezzel szorozza a pozíciókat) | 1 |

Ezek bekerülnek minden munkamenet `meta.json`-jába (`axes`), és ha a munkamenetnek vannak pozíciói, a `heat.parquet` láblécébe is, így a 3DHeat megtekintő maga forgatja és méretezi a sorokat – lásd [Az adatok](the-data.md).

## Többjátékos {#multiplayer}

- Online játszottként jelölve (`multiplayer`): **igen**. A `games --markdown` ezt így mutatja: "allowed (reads only what the game publishes)", vagyis engedélyezett, csak azt olvassa, amit a játék közzétesz.
- `replay` típus: csak azt olvassa, amit a játék vagy a platform kiad (a játék által mentett visszajátszásokat és demókat), így online játékban is rögzít, nemcsak offline; a jelző csak azt dönti el, szabad-e valaha memóriát olvasni.
- Memória: ez az adapter **soha** nem olvas memóriát. Csak a `memory` adapterek olvasnak memóriát, és soha nem olyan játékhoz, amelyet online játszottként jelöltek meg – lásd [Források és szabályok](sources-and-rules.md).

## Rögzített statisztikák {#statistics-recorded}

Statisztikakulcsok, amelyeket ennek az adapternek a kódja név szerint állít be (minden munkamenet `stats`-ja a `meta.json`-ban és a `watcher.sqlite` `stats` táblájában):

`map`, `survived`, `vehicle`, `won`

Kapcsos zárójelben lévő kulcsot futás közben egészítünk ki (`score.{team}` csapatonként egy kulcs). A kódnak a játék mezőinek táblázatából vagy a játék saját statisztikanevéből származó kulcsai nincsenek ebben a listában; a fenti "Mit rögzít" részben vannak megnevezve.

## Teljesség {#completeness}

Az átalakító, amelyet ez az adapter futtat, követi a 3DHeat [átalakítási szabályát](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md): amit a visszajátszás tartalmaz, azt beolvassuk vagy megtartjuk, soha nem dobjuk el – a táblába és a meccsdokumentumba olvassuk, minden más egészben megmarad mellettük, külön fájlokban, és a meccsdokumentum `selfCheck.completeness` részében számoljuk. Az átalakító saját dokumentációja felsorolja, mit olvas be, mit tart meg nyersen, és mit nem tud beolvasni.

## Ellenőrizve {#verified}

az átalakítót több játékverzióból származó nyilvános visszajátszásokon ellenőriztük, és építetett visszajátszásokon futó tesztekkel; a hívást (hook) helyettesítő paranccsal futó tesztekkel

## Forrás {#source}

[heat3d_watch/adapters/replays.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/replays.py)

<!-- A heat3d_watch adapterből készült a tools/gen_game_pages.py által; az adaptert módosítsd, és futtasd újra, ne ezt az oldalt szerkeszd. -->
