---
title: "Dota 2 (visszajátszások)"
nav_order: 12
lang: "hu"
source: game-dota-replays.md
source_hash: "958b1e1855e8"
nav_exclude: true
search_exclude: true
---
# Dota 2 (visszajátszások) {#dota-2-replays}

Miután egy Dota 2-meccs véget ért, a watcher a játék által elmentett visszajátszást olyan fájlokká alakítja, amelyeket a 3DHeat megtekintőben egy térképen is megnézhetsz.

*Technikai részletek: adapter `dota-replays`, típus [`replay`](sources-and-rules.md); folyamatosan fut (nem vár arra, hogy játék induljon), és 5 másodpercenként keres új adatot.*

## Mit rögzít {#what-is-recorded}

- minden hős pozícióját, magasságát, életerejét és szintjét, élő állapotban 7,5-ször másodpercenként
- az ölések és halálok ott, ahol történtek; a tornyok, kaszárnyák, Roshan és a Tormentorok ott, ahol elestek; a megfigyelők ott, ahol lerakták
- minden játékos térképes jelzéseit, térképrajzolásait és parancsait (mozgás, támadás, varázslat, vásárlás, ...) ott, ahová mutattak
- az eredményt és minden játékos sorát; a bejelentkezett játékosét statisztikaként
- mindent, amit a visszajátszás még tartalmaz: minden képkockát és hálózati üzenetet, minden entitástulajdonság-változást, minden szövegtábla-bejegyzést, egészben, a táblázat mellett

## Honnan jön {#where-it-comes-from}

a visszajátszások, amelyeket a Dota 2 ment: &lt;Dota>/game/dota/replays/&lt;match id>.dem (a kliensben letöltve, vagy a `dota-replay <match id>` paranccsal)

## Hogyan kapcsolható be {#how-to-switch-it-on}

tölts le egy meccs visszajátszását a Dota 2-ben, vagy kérj le egy nyilvánosat: `python -m heat3d_watch dota-replay <match id>`; ehhez `pip install gem-dota` kell

Írd be a parancsot a watcher mappájában megnyitott terminálba (lásd [Mielőtt elkezded](before-you-start.md)). Ha nem sikerül, az utolsó sor megmondja, miért; a [Telepítés és futtatás](installing-and-running.md) a szokásos okokat sorolja fel.

## Hogyan működik {#how-it-works}

Visszajátszások és demók: amit a játék egy meccsről elment, a meccs véget érése után átalakítva.

A visszajátszás mindent tartalmaz, amit a több játékos meccseken élő felület visszatart – minden játékos pozícióját, minden ölést ott, ahol történt –, és a játék azt a fájlt a játékosainak írja, így az olvasása nem nyúl a játékhoz. A watcher figyeli azokat a mappákat, ahová a játékok mentik őket, megvárja, amíg egy új fájl nem nő tovább (különben a játék még írja), és egy munkaszálban alakítja át, így egy hosszú átalakítás nem tartja fel a watchert.

Az első alkalommal, amikor egy mappát látnak, a benne lévő visszajátszásokat csak feljegyzik, nem alakítják át: aki évek demóit tárolja, különben a watcher egy napig lenne lefoglalva. A `python -m heat3d_watch replays <adapter> [folder]` kérésre átalakítja a meglévőket.

#### Dota 2 {#dota-2}

A Dota 2 a játékos által letöltött visszajátszásokat (egy meccs részletei, vagy Nézés > Visszajátszások) a `<Dota>/game/dota/replays/<match id>.dem` fájlba menti; a Valve minden nyilvános meccs visszajátszását néhány hétig a szerverein tartja, a `python -m heat3d_watch dota-replay <match id>` pedig azonosító alapján lekér egyet az OpenDota-n keresztül. Mindegyiket a gem-mel (github.com/whanyu1212/gem-dota, MIT, `pip install gem-dota`) olvassuk, külön folyamatban (`heat3d_watch/decoders/dota_replay.py`): minden hős pozícióját, magasságát, életerejét, szintjét, irányát, mana-értékét, tapasztalatát, tulajdonságait és tárgyait másodpercenként 7,5-ször, élő állapotban; az ölések és halálok ott, ahol történtek; a tornyok, kaszárnyák, Roshan és a Tormentorok ott, ahol elestek; minden megfigyelő ott, ahová lerakták és ahol megszűnt; a harcnapló bejegyzései a hősökről (sebzés, gyógyítás, képességek, tárgyak, vásárlások, rúnák, arany, tapasztalat, módosítók), és minden játékos térképes jelzései, térképrajzolásai és parancsai – a `dota/<match>.parquet` fájlba; minden más egység (creepek, idézések, illúziók, futárok, épületek) másodpercenként a `<match>.units.parquet` fájlba; a teljes harcnapló a `<match>.combatlog.parquet` fájlba; a meccs, a csevegés, a draft, minden más, amit az elemző kiszed, és a játék saját meccs végi feljegyzése a `<match>.match.json` fájlba, a munkamenet mappájában. A visszajátszás minden más része is egészben megmarad mellettük (a 3DHeat átalakítási szabálya): minden képkocka és hálózati üzenet a `<match>.packets.parquet`-ban, minden entitástulajdonság-változás a `<match>.entities.parquet`-ban, minden szövegtábla-bejegyzés a `<match>.strings.parquet`-ban, a meccsdokumentum `selfCheck.completeness` részében számolva. A pozíciók a Dota világegységei, ugyanazok, mint amelyeket a játék-állapot integráció jelent. A bejelentkezett játékos eredménysora a munkamenet statisztikája lesz: ölések, halálok, asszisztok, utolsó ütések, megtagadások, nettó vagyon, GPM, XPM, hősi sebzés, őrök, és hogy nyert-e a meccs. Egy új Dota-javítás megváltoztathatja a visszajátszás entitásait, mielőtt a gem követné; a gem által el nem olvasható visszajátszást addig alakítjuk át, ameddig eljut, és az összefoglalójában `incomplete` jelölést kap.

Ugyanez a modul szolgálja ki ezeket is: [Counter-Strike 2 (visszajátszások)](game-cs2-demos.md), [osu! (visszajátszások)](game-osu-replays.md), [Squad (visszajátszások)](game-squad-demos.md), [War Thunder (visszajátszások)](game-warthunder-replays.md), [World of Tanks (visszajátszások)](game-wot-replays.md), [World of Warships (visszajátszások)](game-wows-replays.md).

## Pozíciók és tengelyek {#positions-and-axes}

| | |
|---|---|
| Pozíciók rögzítve | igen |
| Felfelé mutató tengely | `z` |
| Mértékegység | Dota világegységek (Hammer-egységek; a térkép körülbelül 16400 széles) |
| Tükrözve a megtekintőnek | `y` |
| Mértékegység-szorzó (`scale`: a megtekintő ezzel szorozza a pozíciókat) | 1 |

Ezek bekerülnek minden munkamenet `meta.json`-jába (`axes`), és ha a munkamenetnek vannak pozíciói, a `heat.parquet` láblécébe is, így a 3DHeat megtekintő maga forgatja és méretezi a sorokat – lásd [Az adatok](the-data.md).

## Többjátékos {#multiplayer}

- Online játszottként jelölve (`multiplayer`): **igen**. A `games --markdown` ezt így mutatja: "allowed (reads only what the game publishes)", vagyis engedélyezett, csak azt olvassa, amit a játék közzétesz.
- `replay` típus: csak azt olvassa, amit a játék vagy a platform kiad (a játék által mentett visszajátszásokat és demókat), így online játékban is rögzít, nemcsak offline; a jelző csak azt dönti el, szabad-e valaha memóriát olvasni.
- Memória: ez az adapter **soha** nem olvas memóriát. Csak a `memory` adapterek olvasnak memóriát, és soha nem olyan játékhoz, amelyet online játszottként jelöltek meg – lásd [Források és szabályok](sources-and-rules.md).

## Rögzített statisztikák {#statistics-recorded}

Statisztikakulcsok, amelyeket ennek az adapternek a kódja név szerint állít be (minden munkamenet `stats`-ja a `meta.json`-ban és a `watcher.sqlite` `stats` táblájában):

`duration`, `hero`, `score.{team}`, `team`, `won`

A kapcsos zárójeles kulcsot futásidőben egészítjük ki (`score.{team}` csapatonként egy kulcs). A kód által a játék mezőinek táblájából vagy a játék saját statisztikanevéből vett kulcsok nincsenek ebben a listában; a fenti "Mit rögzít" rész nevezi meg őket.

## Teljesség {#completeness}

Az átalakító a 3DHeat [átalakítási szabályát](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md) követi: amit a visszajátszás tartalmaz, azt beolvassuk vagy megtartjuk, soha nem dobjuk el. A táblázaton kívül minden, amit a visszajátszás tartalmaz, egészben megmarad a mellette lévő kísérőfájlokban a munkamenet `dota/` mappájában – `<match>.packets.parquet`, `<match>.entities.parquet`, `<match>.strings.parquet` (oszlopok: `time`, `tick`, `type`, `name`, `entity`, `decoded`, `payload`, ahogy alkalmazandók) –, a meccsdokumentum (`<match>.match.json`) `selfCheck.completeness` része pedig minden `type`-ot megszámol; a `lost` 0.

**Beolvasva**

- a táblázat (`dota/<match>.parquet`): minden hős pozíciója, magassága, életereje, szintje, iránya, manája, tapasztalata, tulajdonságai, páncélja, sebessége, sebzése, tárgyai és a játékos kurzora másodpercenként 7,5-ször; ölések, halálok, célok, őrök, a harcnapló hősökre vonatkozó bejegyzései; a térképes jelzések (`ping`, DOTA_UM_LocationPing), a térképrajzolások (`map_line`, DOTA_UM_MapLine) és minden egységparancs (`order`, DOTA_UM_SpectatorPlayerUnitOrders: `other` a parancs típusa, `value` a képesség- vagy tárgyazonosító, `text` a cél osztálya; a parancsolt pontban, különben a hősnél)
- `<match>.units.parquet`: minden más egység másodpercenként; `<match>.combatlog.parquet`: a teljes harcnapló, ahogy a gem olvassa, minden mezővel
- a meccsdokumentum: mindaz, amit a gem kiszed, és a visszajátszás saját bejegyzései egészben – `fileHeader` (DEM_FileHeader), `fileInfo` (DEM_FileInfo: a lejátszás hossza, minden játékos neve, hőse, Steam-azonosítója, csapata), `matchDetails` (DOTA_UM_MatchDetails: a játék-koordinátor meccs végi eredménytáblája, minden játékos számai, tárgyai, sebzése típusonként, választásai és tiltásai) és `matchMetadata` (DOTA_UM_MatchMetadata)
- `selfCheck.crossCheck`: az ölések, halálok, asszisztok, szint, utolsó ütések és megtagadások a folyamból olvasva, a `matchDetails`-szel összevetve, játékosonként

**Nyersen megtartva**

- `<match>.packets.parquet`: minden képkocka, amely nem csomag (`type` `frame <n>`), és minden hálózati üzenet (`message <n>`, `name` a Valve neve), egészben a `payload`-ban, fájlsorrendben (`seq`, `frame`), a `decoded` a protobuf JSON-ként (a bájtmezőt a hosszával adva), minden üzenettípus dekódolva: svc_PacketEntities (az entitásfolyam), DOTA_UM_SpectatorPlayerUnitOrders, UM_ParticleManager, a harcnapló üzenetei, GE_SosStartSoundEvent, DOTA_UM_TE_\* (lövedékek, animációk, vér), DOTA_UM_OverheadEvent, DOTA_UM_UnitEvent, svc_UpdateStringTable, net_Tick, ...; a küldő táblák, az osztálylista és a szerverinformáció, amelyre egy későbbi entitásdekóder szüksége lesz, ezek között vannak
- `<match>.entities.parquet`: minden entitás minden tulajdonsága, valahányszor megváltozott (`type` a tulajdonság, `name` az osztály, `entity` az indexe; `value`, `vector` vagy `decoded`), a teljes állapota létrehozáskor, és minden létrehozás, belépés, kilépés és törlés – egy egész meccs több millió sor
- `<match>.strings.parquet`: minden szövegtábla-bejegyzés minden frissítésből és minden teljes pillanatképből, az értéke egészben; a `userinfo`, `ActiveModifiers` és `EconItems` protobufjaikból dekódolva
- a meccsdokumentum `selfCheck.completeness` része képkockákat és üzeneteket számol Valve nevükön, harcnapló-bejegyzéseket (`combatlog <type>`), játékeseményeket (`gameevent <name>`), szövegtábla-bejegyzéseket (`stringtable <name>`) és entitásfrissítéseket (`entity <class>`); néhány csak nyersen marad meg (a teljes entitás-pillanatképek, amelyeket a gem kihagy, mert a változásokból építi újra, és olyan táblák bejegyzései, amelyek értékeit semmi nem olvassa), a lost 0

**Nem elérhető**

- hang: a visszajátszásban megvan a hangbeállítás, de a hangadat nincs benne
- a kivonatok és azonosítók mögötti nevek: a hangokat és részecskéket a játék fájljainak kivonatai nevezik el, a képességeket azonosítók; a visszajátszás nem tartalmazza a neveket (a tárgyak nevét a gem katalógusán keresztül kapjuk meg, ahol van)
- minden, amit csak a játékosok saját kliensei ismertek (a kamerájuk, a képernyőjük), azon túl, amit a szerver továbbított; a kurzor és minden parancs benne van

**Méret**: a kísérőfájlok együtt valamivel nagyobbak, mint maga a visszajátszás, a legnagyobbak a csomagok és az entitások; egy teljes meccs egy-két percig tart egy folyamatban

## Ellenőrizve {#verified}

Egy nyilvános meccs visszajátszásán: az ölések, halálok, asszisztok, szint, utolsó ütések és megtagadások mind egyeznek a játék saját meccs végi feljegyzésével mind a tíz játékosnál; a csomagok kísérőfájljának minden üzenete bájtra pontosan visszaszerializálódik; a táblázat és a statisztikák szintetikus adatokon tesztelve

## Forrás {#source}

[heat3d_watch/adapters/replays.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/replays.py)

<!-- Generated from the adapter by tools/gen_game_pages.py; change the adapter and run it again rather than editing this page. -->
