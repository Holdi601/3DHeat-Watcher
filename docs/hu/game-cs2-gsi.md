---
title: "Counter-Strike 2 (játékállapot)"
nav_order: 9
lang: "hu"
source: game-cs2-gsi.md
source_hash: "2eda1106e11f"
nav_exclude: true
search_exclude: true
---
# Counter-Strike 2 (játékállapot) {#counter-strike-2-game-state}

Miközben a Counter-Strike 2-t játszod, a watcher elmenti, amit a játék a saját számítógépeden futó programoknak jelent, így később a 3DHeat megtekintőben egy térképen is megnézheted.

*Technikai részletek: adapter `cs2-gsi`, típus [`gsi`](sources-and-rules.md); a `cs2.exe` futása alatt fut, és 0,05 másodpercenként keres új adatot.*

## Mit rögzít {#what-is-recorded}

- a saját pozíció (világ XYZ, hüvelyk) és nézési irány legfeljebb 10 Hz-cel, amíg élsz
- a megjelenések (minden kör első észlelése, az újraéledések) és a halálok (az életerő 0-ra csökken, vagy a halálszámláló nő)
- az ölések az aktív fegyverrel, a meccsstatisztikából
- a körök (kezdete, vége, győztese), a bomba lerakása, hatástalanítása és robbanása, a meccs fázisai és az eredmény
- ölések, asszisztok, halálok, MVP-k, pontszám, pénz, sebzés, fejlövéses ölések, megnyert és elvesztett körök

## Honnan jön {#where-it-comes-from}

Game State Integration: HTTP POST-ok a 127.0.0.1:3311 címre, amelyet a &lt;CS2>\game\csgo\cfg\gamestate_integration_heat3d.cfg állít be

## Hogyan kapcsolható be {#how-to-switch-it-on}

`python -m heat3d_watch setup cs2-gsi --apply`, majd indítsd el a CS2-t (induláskor olvassa be a fájlt)

Írd be a parancsot a watcher mappájában megnyitott terminálba (lásd [Mielőtt elkezded](before-you-start.md)). Ha nem sikerül, az utolsó sor megmondja, miért; a [Telepítés és futtatás](installing-and-running.md) a szokásos okokat sorolja fel.

A `python -m heat3d_watch setup cs2-gsi` felsorolja, mely fájlokat változtatná meg; a `python -m heat3d_watch setup cs2-gsi --apply` meg is változtatja őket, az eredetit `<file>.heat3d-backup` néven megtartva (lásd [Parancsok](commands.md#setup)). Minden változásnál `cs2-gsi: changed: ...` sort ír ki, vagy `cs2-gsi: nothing to change`-et, ha már be van kapcsolva.

Beállítások környezeti változókból:

- `HEAT3D_CS2_GSI_PORT`: a port, amelyre a játék küld (alapértelmezés 3311); a játék cfg-fájljának ugyanezt a portot kell megneveznie

## Hogyan működik {#how-it-works}

Valve Game State Integration: a Counter-Strike 2 és a Dota 2 egy helyi webkiszolgálónak mondja el, mi történik.

Mindkét játék induláskor beolvassa a cfg-mappájában lévő összes `gamestate_integration_*.cfg` fájlt, és onnantól JSON-dokumentumot küld minden fájl `uri`-jára, valahányszor az állapot változik (legfeljebb `throttle` másodpercenként, és `heartbeat` másodpercenként, ha nem változik semmi). A watcher az a webkiszolgáló: csak a 127.0.0.1-en figyel, minden POST-ra azonnal 200-zal válaszol, a munkát pedig a saját lekérdező szálában végzi.

```text
Counter-Strike 2  <CS2>\game\csgo\cfg\gamestate_integration_heat3d.cfg      port 3311
Dota 2            <Dota>\game\dota\cfg\gamestate_integration\gamestate_integration_heat3d.cfg   port 3312
```

Azt, amit a játékos kap – és így azt, amit rögzíteni lehet –, a játék dönti el, mit láthat a játékos:

- CS2: `provider` (a saját steamid), `map` (név, mód, fázis: warmup/live/intermission/gameover, kör, team_ct/team_t pontszám), `round` (fázis: freezetime/live/over, bomba lerakva/felrobbantva/hatástalanítva, win_team), `player` (a *figyelt* játékos: magad, amíg élsz, egy csapattárs a halálod után), a következőkkel: `state` (életerő, páncél, pénz, round_kills, round_killhs, round_totaldmg), `match_stats` (ölések, asszisztok, halálok, mvps, pontszám), `position` és `forward` "x, y, z" szövegként, világegységekben (hüvelyk, Z felfelé), `weapons`; a `bomb` csak nézőknek. Más játékosok pozíciói (`allplayers_*`) csak nézőknek és a GOTV-nak küldődnek, ezért nem kérjük őket.
- Dota 2: `map` (matchid, game_state, game_time, clock_time, win_team), `player` (kills, deaths, assists, last_hits, denies, gold, gpm, xpm, team_name), `hero` (xpos/ypos világegységekben, szint, alive, respawn_seconds), `buildings` (életerő tornyonként, kaszárnyánként, ősönként), `roshan`, `events` (roshan_killed, aegis_picked_up, ...). Nincs magasság: a z mindig 0. Szintén kérjük és egészben megtartjuk: `abilities`, `items`, `draft`, `wearables`, `minimap`, `couriers`, `neutralitems`, `league` (a játék azt küldi, amit a játékos saját kliense lát; hogy ezek közül melyik tartalmaz valamit játék közben, a nézés helyett, az nincs tesztelve).

Minden dokumentum egészben is megmarad (a 3DHeat átalakítási szabálya, a megtekintő tárolójának docs/converters.md fájlja): `heat.raw.parquet`, `type` "gsi", `text` a JSON úgy, ahogy elküldték – csak a cfg-fájl tokenje törölve, mert az a watcher saját titka, nem játékadat. A meccs nélküli időben (menük, betöltés, meccsek között) érkező dokumentumok a `Backlog`-ban várnak, és a következő meccs munkamenetébe kerülnek, annak kezdete elé; ami a játék bezárásakor marad, saját munkamenetet kap, amely csak ezeket tartalmazza. A feldolgozhatatlan POST-ok és a rossz tokennel érkezők is megmaradnak ("gsi-unreadable", "gsi-bad-auth").

Források: <https://developer.valvesoftware.com/wiki/Counter-Strike:_Global_Offensive_Game_State_Integration> (a formátum, amelyet a CS2 megtartott), <https://github.com/antonpup/CounterStrike2GSI> és <https://github.com/antonpup/Dota2GSI> (mezőlisták; MIT, csak tényekért olvasva).

Ugyanez a modul szolgálja ki ezt is: [Dota 2 (játékállapot)](game-dota2-gsi.md).

## Pozíciók és tengelyek {#positions-and-axes}

| | |
|---|---|
| Pozíciók rögzítve | igen |
| Felfelé mutató tengely | `z` |
| Mértékegység | hüvelyk (Hammer-egység) |
| Tükrözve a megtekintőnek | `y` |
| Mértékegység-szorzó (`scale`: a megtekintő ezzel szorozza a pozíciókat) | 1 |

Ezek bekerülnek minden munkamenet `meta.json`-jába (`axes`), és ha a munkamenetnek vannak pozíciói, a `heat.parquet` láblécébe is, így a 3DHeat megtekintő maga forgatja és méretezi a sorokat – lásd [Az adatok](the-data.md).

## Többjátékos {#multiplayer}

- Online játszottként jelölve (`multiplayer`): **igen**. A `games --markdown` ezt így mutatja: "allowed (reads only what the game publishes)", vagyis engedélyezett, csak azt olvassa, amit a játék közzétesz.
- `gsi` típus: csak azt olvassa, amit a játék vagy a platform kiad (game-state integration vagy helyi API, amelyet a játék a játékos gépének szolgáltat), így online játékban is rögzít, nemcsak offline; a jelző csak azt dönti el, szabad-e valaha memóriát olvasni.
- Memória: ez az adapter **soha** nem olvas memóriát. Csak a `memory` adapterek olvasnak memóriát, és soha nem olyan játékhoz, amelyet online játszottként jelöltek meg – lásd [Források és szabályok](sources-and-rules.md).

## Rögzített statisztikák {#statistics-recorded}

Statisztikakulcsok, amelyeket ennek az adapternek a kódja név szerint állít be (minden munkamenet `stats`-ja a `meta.json`-ban és a `watcher.sqlite` `stats` táblájában):

`bad_auth`, `bad_packets`, `dropped_packets`, `money`, `result`, `score_other`, `score_own`

A kapcsos zárójeles kulcsot futásidőben egészítjük ki (`score.{team}` csapatonként egy kulcs). A kód által a játék mezőinek táblájából vagy a játék saját statisztikanevéből vett kulcsok nincsenek ebben a listában; a fenti "Mit rögzít" rész nevezi meg őket.

## Teljesség {#completeness}

A watcher a 3DHeat [átalakítási szabályát](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md) követi: amit a forrás tartalmaz, azt beolvassuk vagy megtartjuk, soha nem dobjuk el. A sorokon kívül minden csomagot, oldalt, sort vagy választ, amelyet az adapter kap, egészben megőrzünk a munkamenet `heat.raw.parquet`-jában (oszlopok: `time`, `ms`, `type`, `used`, `payload`, `text`, majd minden név szerint megtartott mező; a `used` jelzi, amiből sor is lett). A `meta.json` `selfCheck.completeness` része minden `type`-ot megszámol; a `lost` 0.

**Beolvasva**

- a figyelt játékos pozíciója, nézési iránya, életereje, páncélja, pénze, aktív fegyvere, sisakja, bombaszerelő-készlete, villanó-, füst- és tűzmennyisége, a felszerelés értéke minden pozíciósornál, amíg ez a játékos saját (provider steamid = játékos steamid)
- megjelenések, halálok (az életerő 0-ra csökken, vagy a statisztikák halálszáma nő), ölések (az ölésszám nő)
- meccsfázisok, körök (fagyasztási idő, élő, vége, győztes), a bomba lerakása, hatástalanítása, felrobbanása, az eredmény
- ölések, asszisztok, halálok, MVP-k, pontszám, pénz, sebzés, fejlövéses ölések, megnyert és elvesztett körök statisztikaként

**Nyersen megtartva**

- `gsi`: minden dokumentum, amelyet a játék küld, egészben, ahogy elküldte (`text`); `used` igaz, ha meccsen beolvasták. Ide tartozik a provider (verzió, időbélyeg), a map (mód, csapatnevek, egymást követő körvesztések, időkérések, sorozatgyőzelmek, `round_wins` minden kör győzelmi feltételével), a round, a figyelt játékos (klán, megfigyelő-hely, tevékenység, minden fegyver skinnel, lőszerrel és tartalékkal), a bomb, a fázis-visszaszámlálók, és a játék saját `previously`/`added` különbsége az előző POST-hoz képest
- menükből, betöltésből és meccsek közül érkező dokumentumok: ugyanígy megőrizve, a következő meccs kezdete előtti saját idejükben; az utolsó meccs után saját munkamenetben (`raw_only` a meta.json-ban)
- `gsi-unreadable`: olyan POST, amely nem JSON-objektum; bájtjai `payload`-ként, hossza `length`-ként
- `gsi-bad-auth`: olyan POST, amelynek a cfg-fájléétól eltérő token van

**Nem elérhető**

- más játékosok (`allplayers_*`) és gránátok (`allgrenades`): a játék csak nézőknek és a GOTV-nak küldi őket, a watcher nem kéri (lásd Források és szabályok); egy demó minden játékost tartalmaz – lásd [Counter-Strike 2 (visszajátszások)](game-cs2-demos.md)
- az állapotok a POST-ok között: a játék legfeljebb 0,1 másodpercenként küld (`throttle`), és csak változáskor, egyébként 10 másodpercenként (`heartbeat`)
- a cfg-fájl tokenje, minden megőrzött dokumentumban törölve: a watcher saját titka, nem játékadat
- a 10 000-et meghaladó várakozó POST-ok (ha a watcher megakadt) `dropped_packets`-ként számolódnak, nem őrződnek meg; a 4 MB-nál nagyobb POST `gsi-unreadable`-ként marad meg a hosszával, de bájtjai nélkül

**Méret**: egy játékos dokumentuma 2–4 KB, legfeljebb másodpercenként 10-szer küldve, ha valami változik: meccs közben óránként körülbelül 30–150 MB a `raw.bin`-ben, a zstd-tömörített `heat.raw.parquet`-ban ennek tizede vagy kevesebb (a közzétett formátumból becsülve, nem a játékon mérve)

## Ellenőrizve {#verified}

Tesztelve a futó adapterhez küldött, a közzétett GSI-formátumú dokumentumokon; a telepítés és a cfg-mappa keresése helyi telepítésen tesztelve; a futó játékon nincs tesztelve.

## Forrás {#source}

[heat3d_watch/adapters/gsi.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/gsi.py)

<!-- Generated from the adapter by tools/gen_game_pages.py; change the adapter and run it again rather than editing this page. -->
