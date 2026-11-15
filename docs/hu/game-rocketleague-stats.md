---
title: "Rocket League (játékállapot)"
nav_order: 40
lang: "hu"
source: game-rocketleague-stats.md
source_hash: "3da6ea772068"
nav_exclude: true
search_exclude: true
---
# Rocket League (játékállapot) {#rocket-league-game-state}

Amíg a Rocket Leaguet játszod, a watcher elmenti, amit a játék a számítógépeden futó programoknak jelent, így később térképen megnézheted a 3DHeat megjelenítőben.

*Műszaki részletek: adapter `rocketleague-stats`, típus [`gsi`](sources-and-rules.md); akkor fut, amikor a `RocketLeague.exe` fut, és 0,05 másodpercenként keres új adatot.*

## Mit rögzít {#what-is-recorded}

- labdaérintések a labda helyével (XYZ, Unreal-egységek), azzal, aki megérintette, és a sebességekkel
- gólok a becsapódás helyével, a góllövővel, a gólpasszolóval és a sebességgel; léctalálatok a helyükkel
- statisztikai üzenetek (lelőttek, védések, lövések, epikus védések, ...), kezdőrúgások, visszajátszások, a meccs kezdete és vége, a győztes
- öngólok, gólpasszok, védések, lövések, bemutatók, érintések, pontszám és a csapatok pontszáma, az UpdateState-ből
- minden játékos végső sora a meccs végén
- a saját sorai `me` néven: a játékos, akit a beállításokban megadtál (`config --set player_names.rocketleague-stats=<név>`), egyébként az, akit a játék kamerája követ a visszajátszásokon kívül
- autópozíciók nincsenek: az API nem ad

## Honnan származik {#where-it-comes-from}

Stats API: JSON-folyam TCP-n a 127.0.0.1:49123 címről (a port a &lt;RL>\TAGame\Config\TAStatsAPI.ini vagy DefaultStatsAPI.ini fájlban)

## Hogyan kapcsold be {#how-to-switch-it-on}

`python -m heat3d_watch setup rocketleague-stats --apply` (a PacketSendRate=30 értéket állítja be), majd indítsd el a Rocket Leaguet

Írd be a parancsot a watcher mappájában megnyitott terminálba (lásd [Mielőtt elkezdenéd](before-you-start.md)). Ha nem sikerül, az utolsó sor megmondja, miért; a [Telepítés és futtatás](installing-and-running.md) a szokásos okokat ismerteti.

`python -m heat3d_watch setup rocketleague-stats` felsorolja, mely fájlokat módosítaná; `python -m heat3d_watch setup rocketleague-stats --apply` módosítja őket, az eredetit `<file>.heat3d-backup` néven megtartva (lásd [Parancsok](commands.md#setup)). Minden módosításról kiírja a `rocketleague-stats: changed: ...` sort, vagy a `rocketleague-stats: nothing to change` sort, ha már be van kapcsolva.

## Hogyan működik {#how-it-works}

Rocket League: a hivatalos Stats API, egy helyi socket, amelybe a játék a meccsadatokat írja.

A `<RL>\TAGame\Config\TAStatsAPI.ini` fájlban kapcsolódik be – vagy a `DefaultStatsAPI.ini` fájlban, ha az előbbi nem létezik, amelyet a játék csak akkor olvas – a `[TAGame.MatchStatsExporter_TA]` szakaszban:

```text
PacketSendRate   UpdateState messages per second; 0 (the default) switches the API off, at most 120
Port             the TCP port the game listens on, default 49123 (WebPort 49124 is a WebSocket copy)
```

A játék a szerver: a kliens csatlakozik a 127.0.0.1:49123 címre, és egymás után, elválasztók nélkül olvassa a `{"Event": név, "Data": {...}}` JSON-objektumok folyamát (egyes verziók a Data-t JSON-szövegként küldik). Az események abban a ciklusban mennek ki, amikor történnek, a sebességtől függetlenül:

```text
UpdateState   MatchGuid, Players[] (Name, PrimaryId, Shortcut, TeamNum 0 kék / 1 narancs,
              Score, Goals, Shots, Assists, Saves, Touches, CarTouches, Demos; car state
              only for spectators), Game (Teams[], TimeSeconds, bOvertime, Ball {Speed,
              TeamNum}, bReplay, bHasWinner, Winner, Arena, bHasTarget, Target)
BallHit       Players[] (Name, Shortcut, TeamNum), Ball {PreHitSpeed, PostHitSpeed, Location {X,Y,Z}}
GoalScored    GoalSpeed, GoalTime, ImpactLocation {X,Y,Z}, Scorer, Assister, BallLastTouch
CrossbarHit   BallLocation {X,Y,Z}, BallSpeed, ImpactForce, BallLastTouch
StatfeedEvent EventName, Type, MainTarget, SecondaryTarget
MatchEnded    WinnerTeamNum
MatchCreated, MatchInitialized, CountdownBegin, RoundStarted, GoalReplayStart/WillEnd/End,
MatchPaused/Unpaused, PodiumStart, ReplayCreated, MatchDestroyed, ClockUpdatedSeconds
```

A helyek Unreal-egységek (centiméter), Z felfelé; a pálya kb. 8200 x 10240, a kapuk Y = ±5120-nál vannak. Az autók pozíciói nem részei az API-nak: van helye annak, ahol a labdát megütötték, gólt lőttek vagy a lécet találták el.

Minden üzenet egészben is megmarad (a 3DHeat konvertálási szabálya, a megjelenítő tárolójában a docs/converters.md): a `heat.raw.parquet` fájlban a `type` az üzenet Event neve, a `text` az objektum úgy, ahogy a folyamról jött. Egy UpdateState, amely bájtról bájtra megegyezik az előzővel (szünetelő meccs, menü), egyszer marad meg, és a meta.json `unchanged_replies` mezője számolja. A meccsek között érkező üzenetek a következő meccs munkamenetéig várakoznak egy sorban; ami a játék bezárásakor marad, saját munkamenetet kap. A JSON-nak nem megfelelő karakterek az objektumok között "junk" néven megmaradnak.

Források: <https://www.rocketleague.com/en/developer/stats-api> (a hivatalos oldal); a mezők kis- és nagybetűs írásmódját és a TCP-keretezést az rlstatsapi kliens igazolta (<https://docs.rs/crate/rlstatsapi>, MIT; csak a tényekhez olvasva).

## Pozíciók és tengelyek {#positions-and-axes}

| | |
|---|---|
| Rögzített pozíciók | igen |
| Felfelé mutató tengely | `z` |
| Mértékegység | Unreal-egységek (centiméter) |
| Tükrözés a megjelenítőnek | nincs |
| Mértékskála (`scale`: a megjelenítő ezzel szorozza a pozíciókat) | 1 |

Ezek bekerülnek minden munkamenet `meta.json` fájljának `axes` mezőjébe, és ha a munkamenetnek vannak pozíciói, a `heat.parquet` láblécébe, így a 3DHeat megjelenítő maga forgatja és méretezi a sorokat – lásd [Az adatok](the-data.md).

## Többjátékos mód {#multiplayer}

- Online játékként jelölve (`multiplayer`): **igen**. A `games --markdown` ezt így jeleníti meg: "engedélyezett (csak azt olvassa, amit a játék közzétesz)".
- Típus `gsi`: csak azt olvassa, amit a játék vagy a platform kiad (egy játékállapot-integráció vagy helyi API, amelyet a játék szolgáltat), ezért online játék közben is rögzít, nem csak offline; a jelző csak azt dönti el, szabad-e egyáltalán memóriát olvasni.
- Memória: ez az adapter **soha** nem olvas memóriát. Csak a `memory` adapterek olvasnak memóriát, és soha nem olyan játékhoz, amely online játékként van jelölve – lásd [Források és szabályok](sources-and-rules.md).

## Rögzített statisztikák {#statistics-recorded}

Ennek az adapternek a kódja névről név beállított statisztikakulcsai (minden munkamenet `stats` mezője a `meta.json`-ban és a `watcher.sqlite` `stats` táblájában):

`bad_packets`, `demolished`, `other_goals`, `overtime`, `result`, `team_goals`

A kapcsos zárójelben lévő kulcsot futásidőben töltik ki (`score.{team}` csapatonként egy kulcs). Azok a kulcsok, amelyeket a kód a játék mezőinek táblázatából vagy a játék saját statisztikanevéből vesz, nincsenek ebben a listában; a fenti "Mit rögzít" rész nevezi meg őket.

## Teljesség {#completeness}

A watcher követi a 3DHeat [konvertálási szabályát](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md): amit a forrás tartalmaz, azt beolvassa vagy megtartja, soha nem dobja el. A sorokon kívül minden csomagot, lapot, sort vagy választ, amelyet az adapter kap, egészben megtart a munkamenet `heat.raw.parquet` fájljában (oszlopai `time`, `ms`, `type`, `used`, `payload`, `text`, majd minden név szerint megtartott mező; a `used` jelöli, ami sorrá is vált), a `meta.json` `selfCheck.completeness` adatai pedig minden `type`-ot számolnak – a `lost` értéke 0.

**Beolvasva**

- BallHit (a hely, ki, csapat, a sebességek az ütés előtt és után), GoalScored (becsapódás helye, góllövő, gólpasszoló, sebesség, a gól ideje), CrossbarHit (hely, utolsó érintés, sebesség, erő), StatfeedEvent (esemény, típus, főcél és másodlagos cél), MatchEnded (győztes, eredmény); minden más esemény neve sorként
- az UpdateState-ből: a aréna, a kamera célpontja a visszajátszásokon kívül (ebből derül ki, ki a `me`), a csapatok pontszáma, minden játékos gólja, gólpassza, védése, lövése, bemutatója, érintése, autóérintése és pontszáma (a sajátod statisztikaként, mindenkié a `player_result` sorként a meccs végén); a túlóra a ClockUpdatedSeconds-ból

**Nyers formában megtartva**

- minden üzenet egészben, ahogy a folyamról érkezett (`text`), a saját Event nevén: `UpdateState` (minden játékos PrimaryId-je és Shortcut-ja, az óra, a labda sebessége és csapata, a csapatnevek és színek, a visszajátszás- és győztes-jelzők, és az autó állapota, ahol a játék küldi), `BallHit`, `GoalScored` (a labda utolsó érintésével), `CrossbarHit`, `StatfeedEvent`, `MatchCreated`, `MatchInitialized`, `CountdownBegin`, `RoundStarted`, `GoalReplayStart`, `GoalReplayWillEnd`, `GoalReplayEnd`, `MatchPaused`, `MatchUnpaused`, `MatchEnded`, `PodiumStart`, `ReplayCreated`, `MatchDestroyed`, `ClockUpdatedSeconds`, és minden későbbi build által hozzáadott esemény
- egy UpdateState, amely bájtról bájtra megegyezik az előzővel (szünet, menük), egyszer marad meg és számolódik (`unchanged_replies` a meta.json-ban)
- meccsek közötti üzenetek: a következő meccs kezdetekor, a saját idejükön; az utolsó meccs után egy saját munkamenetben (`raw_only` a meta.json-ban)
- `unreadable`: olyan objektum, amely nem Stats API-üzenet; `junk`: karakterek az objektumok között

**Nem elérhető**

- autópozíciók és autóállapot játék közben: a játék ezeket csak nézőknek küldi
- az UpdateState két küldés között: a játék másodpercenként PacketSendRate-et küld (a `setup` 30-ra állítja, a játék legfeljebb 120-at enged); az események abban a ciklusban mennek ki, amikor történnek
- a WebSocket-másolat a WebPort (49124) porton: ugyanazok az üzenetek, mint a TCP-porton, nem olvasva kétszer

**Méret**: egy UpdateState 1–3 KB hat játékosnál, másodpercenként 30: óránként nagyjából 100–300 MB a `raw.bin` fájlban, amíg meccs fut, a zstd `heat.raw.parquet` fájljában ennek egytizede vagy kevesebb (a dokumentált formátumból becsülve, a játékon nem mérve)

## Ellenőrizve {#verified}

a dokumentált formátumú üzeneteken tesztelve, amelyeket egy helyi szerver-utánzat küldött; a játékon még nem tesztelve

## Forrás {#source}

[heat3d_watch/adapters/rocketleague.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/rocketleague.py)

<!-- Generated from the adapter by tools/gen_game_pages.py; change the adapter and run it again rather than editing this page. -->
