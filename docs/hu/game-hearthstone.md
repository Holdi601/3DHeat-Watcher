---
title: "Hearthstone (naplófájlok)"
nav_order: 25
lang: "hu"
source: game-hearthstone.md
source_hash: "e79c19776947"
nav_exclude: true
search_exclude: true
---
# Hearthstone (naplófájlok) {#hearthstone-log-files}

Amíg a Hearthstone-t játszod, a watcher beolvassa a játék által írt fájlokat, és elmenti, mi történt, hogy később statisztikaként és idővonalon megnézhesd.

*Műszaki részletek: adapter `hearthstone`, típus [`log`](sources-and-rules.md); fut, amíg a `Hearthstone.exe` megy, és 0,5 másodpercenként keres új adatot.*

## Mit rögzít {#what-is-recorded}

- a játék kezdete és vége, az eredménnyel (nyert, vesztett, döntetlen), körökkel és az ellenfél nevével
- minden kör
- a Power.log és a többi napló minden sora egészben a heat.raw.parquet fájlban
- játékok, győzelmek, vereségek, döntetlenek, körök, leghosszabb játék

## Honnan származik {#where-it-comes-from}

&lt;install>\Logs\Power.log (vagy Logs\Hearthstone_\*\Power.log), amelyet akkor ír a játék, ha a %LOCALAPPDATA%\Blizzard\Hearthstone\log.config tartalmaz [Power] szakaszt, és az ott írt összes többi \*.log fájl

## Bekapcsolás {#how-to-switch-it-on}

`python -m heat3d_watch setup hearthstone --apply` hozzáadja a [Power] naplózást a %LOCALAPPDATA%\Blizzard\Hearthstone\log.config fájlhoz (a mentett másolattal); indítsd újra a játékot

Írd be a parancsot a watcher mappájában megnyitott terminálba (lásd [Mielőtt elkezdenéd](before-you-start.md)). Ha hibát jelez, az utolsó sor megmondja, miért; az [Telepítés és futtatás](installing-and-running.md) a szokásos okokat írja le.

`python -m heat3d_watch setup hearthstone` felsorolja a fájlokat, amelyeket módosítana; a `python -m heat3d_watch setup hearthstone --apply` megváltoztatja őket, az eredetit `<file>.heat3d-backup` néven megtartva (lásd [Parancsok](commands.md#setup)). Minden változásra kiírja a `hearthstone: changed: ...` sort, vagy a `hearthstone: nothing to change` sort, ha már be van kapcsolva.

## Működés {#how-it-works}

Hearthstone: a játék Power.log fájlja, amelyet akkor ír, ha a log.config ezt kéri.

A Hearthstone indításkor beolvassa a `%LOCALAPPDATA%\Blizzard\Hearthstone\log.config` fájlt; a `LogLevel=1` és `FilePrinting=true` beállítású `[Power]` szakasz miatt minden játék állapotváltozását a `<install>\Logs\Power.log` fájlba írja (az újabb kliensek az egyes indítások naplóit saját mappába teszik, `Logs\Hearthstone_<dátum>\`). Ez a dokumentált hibakeresési naplózás, amelyet a paklikövető eszközök 2014 óta bekapcsolnak (a Hearthstone Deck Tracker beállítása ugyanezt a szakaszt írja). A `setup()` hozzáadja a szakaszt, a fájl eredeti állapotáról készült másolattal; a játéknak újraindítás kell, hogy beolvassa.

A használt sorok, mind a `GameState.DebugPrintPower()` híváshoz tartoznak (a `PowerTaskList` sorok ezeket ismétlik, és ki vannak hagyva):

```text
D 20:15:01.1234567 GameState.DebugPrintPower() - CREATE_GAME
D 20:15:01.1234567 GameState.DebugPrintPower() -     Player EntityID=2 PlayerID=1 GameAccountId=[hi=1 lo=2]
D 20:15:01.1234567 GameState.DebugPrintGame() - PlayerID=1, PlayerName=Name#1234
D 20:15:02.1234567 GameState.DebugPrintPower() -     FULL_ENTITY - Updating [entityName=... id=4 zone=HAND
                   zonePos=0 cardId=CS2_029 player=1] CardID=CS2_029
D 20:16:00.1234567 GameState.DebugPrintPower() - TAG_CHANGE Entity=GameEntity tag=TURN value=3
D 20:25:00.1234567 GameState.DebugPrintPower() - TAG_CHANGE Entity=Name#1234 tag=PLAYSTATE value=WON
D 20:25:00.1234567 GameState.DebugPrintPower() - TAG_CHANGE Entity=GameEntity tag=STATE value=COMPLETE
```

A játékos saját oldala az, amelynek a kezdőkéz lapjai nevesítve vannak (az ellenfélé rejtett), különben az, amelyik nem az MI (0-s fiók) vagy az "UNKNOWN HUMAN PLAYER". A sorok csak a napszak idejét viszik; a dátum a mai nap.

A Power.log minden sora egészben megmarad a munkamenet nyers mellékfájljában (a 3DHeat konvertáló szabálya szerint), a `PowerTaskList` ismétlésekkel, opciókkal, választásokkal és entitásfrissítésekkel együtt: a `type` az a metódus, amely írta (`GameState.DebugPrintPower`, `PowerTaskList.DebugPrintPower`, `GameState.DebugPrintOptions`, ...). Bármely más napló, amelyet a játék mellette ír - `LoadingScreen.log`, `Decks.log`, `Zone.log`, `Arena.log`, ..., mindegyik csak akkor, ha a log.config kéri (a paklikövetők gyakran kérik) -, ugyanígy követve van, és a nevével a `log` mezőben kerül megőrzésre.

## Pozíciók és tengelyek {#positions-and-axes}

| | |
|---|---|
| Rögzített pozíciók | nem |
| Felfelé mutató tengely | `y` |
| Mértékegységek | nincs rögzített pozíció |
| Tükrözés a megjelenítőhöz | nincs |
| Mértékskála (`scale`: a megjelenítő ezzel szorozza a pozíciókat) | 1 |

Ezek minden munkamenet `meta.json` fájljának `axes` mezőjébe kerülnek, és ha a munkamenetnek vannak pozíciói, a `heat.parquet` láblécébe is, így a 3DHeat-megjelenítő magától forgatja és méretezi a sorokat - lásd [Az adatok](the-data.md).

## Többjátékos {#multiplayer}

- Online játékként jelölve (`multiplayer`): **igen**. A `games --markdown` ezt "engedélyezett (csak azt olvassa, amit a játék közzétesz)" formában mutatja.
- `log` típus: csak azt olvassa, amit a játék vagy a platform kiad (a játék futása közben írt fájlok), ezért online játékban is rögzít, nem csak offline; a jelző csak azt dönti el, szabad-e egyáltalán memóriát olvasni.
- Memória: ez az adapter **soha** nem olvas memóriát. Csak a `memory` típusú adapterek olvasnak memóriát, és soha nem olyan játékhoz, amely online játékként van megjelölve - lásd [Forrásak és szabályok](sources-and-rules.md).

## Rögzített statisztikák {#statistics-recorded}

Azok a statisztikakulcsok, amelyeket ez az adapter kódja név szerint állít be (minden munkamenet `stats` mezője a `meta.json`-ban és a `watcher.sqlite` `stats` táblájában):

`bad_lines`, `games`, `longest_game_turns`, `losses`, `ties`, `turns`, `wins`

A kapcsos zárójeles kulcsot futásidőben töltik ki (a `score.{team}` csapatonként egy kulcs). Azok a kulcsok, amelyeket a kód a játék mezőinek táblázatából vagy a játék saját statisztikanevei közül vesz, nincsenek ebben a listában; a fenti "Mit rögzít" rész nevezi meg őket.

## Teljesség {#completeness}

A watcher követi a 3DHeat [konvertáló szabályát](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md): amit a forrás tartalmaz, azt beolvassa vagy megőrzi, sosem dobja el. A sorokon kívül minden csomagot, oldalt, sort vagy választ, amelyet az adapter kap, egészben megőriz a munkamenet `heat.raw.parquet` fájlja (oszlopok: `time`, `ms`, `type`, `used`, `payload`, `text`, majd minden név szerint megtartott mező; a `used` jelöli, ami sorrá is vált), és a `meta.json` `selfCheck.completeness` mezője minden `type` értéket megszámol - a `lost` értéke 0.

**Beolvasva**

- `CREATE_GAME`, a játékosok (entitás, játékosazonosító, fiók; a 0-s fiók az MI) és a nevük (`DebugPrintGame`)
- hogy melyik oldal a játékosé, a kezdőkéz nevesített lapjai alapján
- a `TAG_CHANGE` a TURN, PLAYSTATE (nyert, vesztett, döntetlen) és STATE COMPLETE értékekre: körök, eredmény, ellenfél

**Nyersen megőrizve**

- minden Power.log-sor egészben, `type` = az a metódus, amely írta (`GameState.DebugPrintPower`, `PowerTaskList.DebugPrintPower`, `GameState.DebugPrintGame`, `GameState.DebugPrintOptions`, `GameState.SendChoices`, `GameState.DebugPrintEntityChoices`, `PowerProcessor.DoTaskListForCard`, ...), `log` mezője `Power`, `used` ott, ahol sorrá vált: minden kijátszott, húzott és felfedett lap, minden tagváltozás, támadás, opció és választás itt van, még nincs sorokban
- a mappa többi naplójának minden sora (`LoadingScreen`, `Decks`, `Zone`, `Arena`, `Achievements`, `FullScreenFX`, ... - bármi, amit a log.config bekapcsol), ugyanazokkal a `type` értékekkel, a napló nevével a `log` mezőben
- szint és napszak nélküli sor `untimed`, metódus nélküli sor `untagged` néven

**Nem elérhető**

- pozíciók: egy kártyajátéknak nincs
- az ellenfél rejtett lapjai: a napló egy lapot csak akkor nevez meg, ha az felfedésre került
- azok a naplók, amelyeket a log.config nem kapcsol be: a `setup` csak a [Power] szakaszt kéri; a többi napló akkor jön, ha egy másik eszköz (paklikövető) bekapcsolta
- korábbi indítások naplói: minden indítás új mappát ír; a játék e futásánál régebbiek nem kerülnek újraolvasásra

**Méret**: a Power.log Verbose módban játékonként körülbelül 1-5 MB, játékidőben óránként 10-40 MB; a többi napló keveset ad hozzá; a zstd a heat.raw.parquet fájlban tizedére vagy még kevesebbre csökkenti (a sorok sokat ismétlődnek)

## Ellenőrzés {#verified}

szintetikus Power.log-sorokon tesztelve a játék formátumában; a játékon nincs tesztelve

## Forrás {#source}

[heat3d_watch/adapters/hearthstone.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/hearthstone.py)

<!-- Generated from the adapter by tools/gen_game_pages.py; change the adapter and run it again rather than editing this page. -->
