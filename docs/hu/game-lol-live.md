---
title: "League of Legends (játékállapot)"
nav_order: 29
lang: "hu"
source: game-lol-live.md
source_hash: "75c67c6fe84f"
nav_exclude: true
search_exclude: true
---
# League of Legends (játékállapot) {#league-of-legends-game-state}

Amíg a League of Legends-et játszod, a watcher elmenti, amit a játék a számítógépeden futó programoknak jelent, hogy később statisztikaként és idővonalon megnézhesd.

*Műszaki részletek: adapter `lol-live`, típus [`gsi`](sources-and-rules.md); fut, amíg a `League of Legends.exe` megy, és 0,5 másodpercenként keres új adatot.*

## Mit rögzít {#what-is-recorded}

- nincsenek pozíciók: az API nem ad
- ölési napló: a játékos ölései, halálai és segítései, más bajnokok ölései a gyilkossal, az áldozattal és a segítőkkel
- sárkányok, heraldok, bárók, tornyok, gátlók, többszörös ölések, aszok, első vér, a játék kezdete és vége
- saját ölések, halálok, segítések, creep-pontszám, őrszem-pontszám, szint, arany, bajnok, játékidő, eredmény
- a játékos csapata által elvett célpontok

## Honnan származik {#where-it-comes-from}

A játékkliens Live Client Data API-ja, <https://127.0.0.1:2999/liveclientdata/> (allgamedata, eventdata), mérkőzés közben

## Bekapcsolás {#how-to-switch-it-on}

Semmit sem kell bekapcsolni: a watcher úgy olvassa a forrást, ahogy a játék vagy a platform biztosítja.

## Működés {#how-it-works}

League of Legends: a Live Client Data API, amelyet a játékkliens mérkőzés közben szolgáltat.

Amíg egy mérkőzés fut (gyakorló eszköz és nézői mód is), a `League of Legends.exe` a <https://127.0.0.1:2999> címen válaszol arra, amit a játékos a játék saját felületén lát:

```text
/liveclientdata/allgamedata          activePlayer (riotId, level, currentGold, championStats),
                                     allPlayers (championName, team ORDER/CHAOS, level,
                                     scores: kills, deaths, assists, creepScore, wardScore),
                                     events, gameData (gameMode, gameTime s, mapName)
/liveclientdata/eventdata?eventID=N  {"Events": [...]} from EventID N on: GameStart,
                                     MinionsSpawning, FirstBlood, FirstBrick, TurretKilled,
                                     InhibKilled, InhibRespawningSoon, InhibRespawned,
                                     DragonKill, HeraldKill, BaronKill, ChampionKill
                                     (KillerName, VictimName, Assisters), Multikill
                                     (KillStreak), Ace (Acer, AcingTeam), GameEnd (Result)
```

Pozíciók nincsenek: az API nem ad, ezért a League munkamenet események és statisztikák, térképtábla nélkül. A tanúsítvány önaláírt, a Riot saját gyökértanúsítványával (`riotgames.pem`, közzétéve a <https://static.developer.riotgames.com/docs/lol/riotgames.pem> oldalon). Használati feltételei nincsenek kimondva, ezért nincs szállítva: helyezd a `<data>\riotgames.pem` fájlba, és a kapcsolat ezzel ellenőrződik; anélkül az ellenőrzés ki van kapcsolva - és csak a 127.0.0.1 címen, az egyetlen címen, amellyel ez az adapter beszél.

A Riot szabályzata megengedi, hogy az eszközök azt mutassák meg, amit a játékos a játékból maga is tudhat, és semmi mást, ami azon túl számított (nincsenek ellenséges időzítők): ez a játékos által látott ölési naplót és eredményjelzőt rögzíti, valamint a játékos saját számait.

Minden válasz egészben is megmarad (a 3DHeat konvertáló szabálya szerint, a megjelenítő repójának docs/converters.md fájlja): a `heat.raw.parquet`-ban, a `type` a végpont (`allgamedata`, `eventdata`), a `text` a JSON, ahogy a kliens elküldte, a `status` pedig, ha nem 200 volt. Az a válasz, amely bájtra pontosan megegyezik az ugyanazon végpont előzőjével (az eseménylista, amíg semmi sem történik), egyszer marad meg, és a meta.json `unchanged_replies` mezője számolja. Az allgamedata tartalmazza mindazt, amit a többi végpont szolgáltat (activeplayer\*, playerlist, playerscores, playeritems, playersummonerspells, playermainrunes, gamestats), így azokat nem kérdezi külön. A mérkőzés előtti válaszok (a betöltő képernyő) egy váróláncban várakoznak, és a mérkőzés munkamenetébe kerülnek; a GameEnd után a munkamenet nyitva marad, amíg a kliens el nem megy, így a végképernyő válaszai is benne maradnak.

Forrás: <https://developer.riotgames.com/docs/lol#game-client-api>

## Pozíciók és tengelyek {#positions-and-axes}

| | |
|---|---|
| Rögzített pozíciók | nem |
| Felfelé mutató tengely | `z` |
| Mértékegységek | nincs (nincsenek pozíciók) |
| Tükrözés a megjelenítőhöz | nincs |
| Mértékskála (`scale`: a megjelenítő ezzel szorozza a pozíciókat) | 1 |

Ezek minden munkamenet `meta.json` fájljának `axes` mezőjébe kerülnek, és ha a munkamenetnek vannak pozíciói, a `heat.parquet` láblécébe is, így a 3DHeat-megjelenítő magától forgatja és méretezi a sorokat - lásd [Az adatok](the-data.md).

## Többjátékos {#multiplayer}

- Online játékként jelölve (`multiplayer`): **igen**. A `games --markdown` ezt "engedélyezett (csak azt olvassa, amit a játék közzétesz)" formában mutatja.
- `gsi` típus: csak azt olvassa, amit a játék vagy a platform kiad (a játék által szolgáltatott állapotintegráció vagy helyi API), ezért online játékban is rögzít, nem csak offline; a jelző csak azt dönti el, szabad-e egyáltalán memóriát olvasni.
- Memória: ez az adapter **soha** nem olvas memóriát. Csak a `memory` típusú adapterek olvasnak memóriát, és soha nem olyan játékhoz, amely online játékként van megjelölve - lásd [Forrásak és szabályok](sources-and-rules.md).

## Rögzített statisztikák {#statistics-recorded}

Azok a statisztikakulcsok, amelyeket ez az adapter kódja név szerint állít be (minden munkamenet `stats` mezője a `meta.json`-ban és a `watcher.sqlite` `stats` táblájában):

`bad_packets`, `champion`, `game_time`, `gold`, `level`, `result`

A kapcsos zárójeles kulcsot futásidőben töltik ki (a `score.{team}` csapatonként egy kulcs). Azok a kulcsok, amelyeket a kód a játék mezőinek táblázatából vagy a játék saját statisztikanevei közül vesz, nincsenek ebben a listában; a fenti "Mit rögzít" rész nevezi meg őket.

## Teljesség {#completeness}

A watcher követi a 3DHeat [konvertáló szabályát](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md): amit a forrás tartalmaz, azt beolvassa vagy megőrzi, sosem dobja el. A sorokon kívül minden csomagot, oldalt, sort vagy választ, amelyet az adapter kap, egészben megőriz a munkamenet `heat.raw.parquet` fájlja (oszlopok: `time`, `ms`, `type`, `used`, `payload`, `text`, majd minden név szerint megtartott mező; a `used` jelöli, ami sorrá is vált), és a `meta.json` `selfCheck.completeness` mezője minden `type` értéket megszámol - a `lost` értéke 0.

**Beolvasva**

- az ölési napló az eventdata végpontból: minden esemény egyszer, a nevesített mezői dekódolva (gyilkos, áldozat és segítők a bajnokkal és a csapattal, építmények és oldaluk, sárkánytípus, lopások, többszörös ölések, aszok, első vér, az eredmény), és minden más eseménymező a saját nevén a sorában
- az allgamedatából: saját ölések, halálok, segítések, creep-pontszám, őrszem-pontszám, szint, arany, bajnok, játékidő, játékmód és pálya

**Nyersen megőrizve**

- `allgamedata`: minden válasz egészben (`text`), 2 másodpercenként - activePlayer (képességek, minden bajnoki statisztika, teljes rúnák, arany, szint), allPlayers (tárgyak slotokkal és árakkal, rúnák, idézőbűvölet, pontszámok, szint, halott állapot és újraéledési időzítő, külső, sáv, bot), az események, gameData (mód, idő, pálya, terep); a `used` igaz, amíg a mérkőzés fut, hamis a végképernyőn
- `eventdata`: minden válasz egészben, 0,5 másodpercenként kérve a következő eseményazonosítótól; a `used` igaz, ha új eseményeket hozott
- az a válasz, amely bájtra pontosan megegyezik az ugyanazon végpont előzőjével, egyszer marad meg és számolódik (a meta.json `unchanged_replies` mezője); a hibaválaszok (a betöltő képernyő RESOURCE_NOT_FOUND válasza) a `status` mezőjükkel megmaradnak, a mérkőzés kezdete előtt

**Nem elérhető**

- pozíciók: az API nem ad (nincs kistérkép, nincsenek koordináták)
- a többi végpont (activeplayer, activeplayername, activeplayerabilities, activeplayerrunes, playerlist, playerscores, playersummonerspells, playermainrunes, playeritems, gamestats): mindegyik az allgamedata egy részét szolgáltatja, ezért nem kérdezik külön
- a Replay API (`/replay/*` ugyanezen a porton): visszajátszásokat és megfigyelt játékokat játszik le, ha a game.cfg-ben be van kapcsolva; nem része a játszott mérkőzésnek
- a League kliens lockfile-végpontjai: nem közzétett API (lásd Forrásak és szabályok)
- értékek két olvasás között: az API akkor válaszol, amikor kérdezik, és nem küld magától; az eredményjelzőt 2 másodpercenként, az eseményeket 0,5 másodpercenként kérdezi

**Méret**: az allgamedata 15-40 KB (tartalmazza a teljes eseménylistát, amely nő) 2 másodpercenként: óránként körülbelül 30-70 MB a `raw.bin`-ban; az eventdata keveset ad hozzá, mert a változatlan válaszok számolódnak, nem tárolódnak; a zstd a heat.raw.parquet fájlban az ismétlődő JSON-t néhány MB-ra csökkenti óránként (a dokumentált formátumból becsülve)

## Ellenőrzés {#verified}

szintetikus helyi szerveren tesztelve, amely a dokumentált formátumban szolgált ki válaszokat; a játékon nincs tesztelve

## Forrás {#source}

[heat3d_watch/adapters/lol.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/lol.py)

<!-- Generated from the adapter by tools/gen_game_pages.py; change the adapter and run it again rather than editing this page. -->
