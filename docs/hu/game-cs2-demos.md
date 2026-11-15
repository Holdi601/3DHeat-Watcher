---
title: "Counter-Strike 2 (visszajátszások)"
nav_order: 8
lang: "hu"
source: game-cs2-demos.md
source_hash: "d115f9085302"
nav_exclude: true
search_exclude: true
---
# Counter-Strike 2 (visszajátszások) {#counter-strike-2-replays}

Miután egy Counter-Strike 2-meccs véget ért, a watcher a játék által elmentett visszajátszást olyan fájlokká alakítja, amelyeket a 3DHeat megtekintőben egy térképen is megnézhetsz.

*Technikai részletek: adapter `cs2-demos`, típus [`replay`](sources-and-rules.md); folyamatosan fut (nem vár arra, hogy játék induljon), és 5 másodpercenként keres új adatot.*

## Mit rögzít {#what-is-recorded}

- minden játékos pozícióját, nézési irányát, életerejét és pénzét (minden 8. ticknél)
- ölések, halálok, sebzés, gránátok, lerakott és hatástalanított bombák ott, ahol történtek
- körök, állás, gazdaság; a bejelentkezett játékos eredménysora statisztikaként

## Honnan jön {#where-it-comes-from}

a demók, amelyeket a CS2 ment: &lt;CS2>/game/csgo/replays/\*.dem (a meccselőzményekből letöltve) és &lt;CS2>/game/csgo/\*.dem (rögzítve)

## Hogyan kapcsolható be {#how-to-switch-it-on}

tölts le egy meccs demóját a CS2-ben (Watch > Your Matches), vagy rögzíts egyet a konzol `record` parancsával

Beállítások környezeti változókból:

- `HEAT3D_CS2`: a 3DHeat CS2 mappája, ha nem a watcher mellett van, vagy nincs telepítve

## Hogyan működik {#how-it-works}

Visszajátszások és demók: amit a játék egy meccsről elment, a meccs véget érése után átalakítva.

A visszajátszás mindent tartalmaz, amit a több játékos meccseken élő felület visszatart – minden játékos pozícióját, minden ölést ott, ahol történt –, és a játék azt a fájlt a játékosainak írja, így az olvasása nem nyúl a játékhoz. A watcher figyeli azokat a mappákat, ahová a játékok mentik őket, megvárja, amíg egy új fájl nem nő tovább (különben a játék még írja), és egy munkaszálban alakítja át, így egy hosszú átalakítás nem tartja fel a watchert.

Az első alkalommal, amikor egy mappát látnak, a benne lévő visszajátszásokat csak feljegyzik, nem alakítják át: aki évek demóit tárolja, különben a watcher egy napig lenne lefoglalva. A `python -m heat3d_watch replays <adapter> [folder]` kérésre átalakítja a meglévőket.

#### Counter-Strike 2 {#counter-strike-2}

A CS2 a játékos által a meccselőzményekből letöltött demókat (Watch fül) a `<CS2>/game/csgo/replays/` mappába, a `record` konzolparanccsal rögzítetteket pedig a `<CS2>/game/csgo/` mappába menti. Mindegyiket ennek a tárolónak a saját CS2-átalakítója alakítja át (3DHeat CS2, github.com/Holdi601/3DHeat-CS2: minden játékos pozíciója, nézési iránya, életereje és pénze minden nyolcadik tickben; ölések, halálok, sebzés, gránátok, lerakott és hatástalanított bombák ott, ahol történtek; körök, állás, gazdaság) a munkamenet mappájába, a megtekintő hő- és meccs-füleinek olvasható `<map>/<match>.parquet` táblává és `<match>.match.json` összefoglalóvá. A meccs eredménytáblája lesz a munkamenet statisztikája: annak a játékosnak, akinek a Steam-fiókja be van jelentkezve ezen a gépen (a Steam `loginusers.vdf` fájljából), a sima nevek alatt – ölések, halálok, asszisztok, ADR, KAST, fejlövési arány, nyitó ölések, clutchek –, valamint az állás és a körök.

Ugyanez a modul szolgálja ki ezeket is: [Dota 2 (visszajátszások)](game-dota-replays.md), [osu! (visszajátszások)](game-osu-replays.md), [Squad (visszajátszások)](game-squad-demos.md), [War Thunder (visszajátszások)](game-warthunder-replays.md), [World of Tanks (visszajátszások)](game-wot-replays.md), [World of Warships (visszajátszások)](game-wows-replays.md).

## Pozíciók és tengelyek {#positions-and-axes}

| | |
|---|---|
| Pozíciók rögzítve | igen |
| Felfelé mutató tengely | `z` |
| Mértékegység | hüvelyk (Source-egységek) |
| Tükrözve a megtekintőnek | `y` |
| Mértékegység-szorzó (`scale`: a megtekintő ezzel szorozza a pozíciókat) | 1 |

Ezek bekerülnek minden munkamenet `meta.json`-jába (`axes`), és ha a munkamenetnek vannak pozíciói, a `heat.parquet` láblécébe is, így a 3DHeat megtekintő maga forgatja és méretezi a sorokat – lásd [Az adatok](the-data.md).

## Többjátékos {#multiplayer}

- Online játszottként jelölve (`multiplayer`): **igen**. A `games --markdown` ezt így mutatja: "allowed (reads only what the game publishes)", vagyis engedélyezett, csak azt olvassa, amit a játék közzétesz.
- `replay` típus: csak azt olvassa, amit a játék vagy a platform kiad (a játék által mentett visszajátszásokat és demókat), így online játékban is rögzít, nemcsak offline; a jelző csak azt dönti el, szabad-e valaha memóriát olvasni.
- Memória: ez az adapter **soha** nem olvas memóriát. Csak a `memory` adapterek olvasnak memóriát, és soha nem olyan játékhoz, amelyet online játszottként jelöltek meg – lásd [Források és szabályok](sources-and-rules.md).

## Rögzített statisztikák {#statistics-recorded}

Statisztikakulcsok, amelyeket ennek az adapternek a kódja név szerint állít be (minden munkamenet `stats`-ja a `meta.json`-ban és a `watcher.sqlite` `stats` táblájában):

`map`, `rounds`, `score.{team}`, `won`

Kapcsos zárójelben lévő kulcsot futás közben egészítünk ki (`score.{team}` csapatonként egy kulcs). A kódnak a játék mezőinek táblázatából vagy a játék saját statisztikanevéből származó kulcsai nincsenek ebben a listában; a fenti "Mit rögzít" részben vannak megnevezve.

## Teljesség {#completeness}

Az átalakító, amelyet ez az adapter futtat, követi a 3DHeat [átalakítási szabályát](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md): amit a visszajátszás tartalmaz, azt beolvassuk vagy megtartjuk, soha nem dobjuk el – a táblába és a meccsdokumentumba olvassuk, minden más egészben megmarad mellettük, külön fájlokban, és a meccsdokumentum `selfCheck.completeness` részében számoljuk. Az átalakító saját dokumentációja felsorolja, mit olvas be, mit tart meg nyersen, és mit nem tud beolvasni.

## Ellenőrizve {#verified}

az átalakítót valódi versenydemókon teszteltük; a mappafigyelés és a statisztikák tesztekkel vannak ellenőrizve

## Forrás {#source}

[heat3d_watch/adapters/replays.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/replays.py)

<!-- A heat3d_watch adapterből készült a tools/gen_game_pages.py által; az adaptert módosítsd, és futtasd újra, ne ezt az oldalt szerkeszd. -->
