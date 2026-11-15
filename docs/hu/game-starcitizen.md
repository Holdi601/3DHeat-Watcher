---
title: "Star Citizen (naplófájlok)"
nav_order: 42
lang: "hu"
source: game-starcitizen.md
source_hash: "6528f948d2e5"
nav_exclude: true
search_exclude: true
---
# Star Citizen (naplófájlok) {#star-citizen-log-files}

Amíg a Star Citizen-t játszod, a watcher beolvassa a játék által írt fájlokat, és elmenti, mi történt, hogy később statisztikaként és idővonalon megnézhesd.

*Műszaki részletek: adapter `starcitizen`, típus [`log`](sources-and-rules.md); fut, amíg a `StarCitizen.exe` megy, és 0,5 másodpercenként keres új adatot.*

## Mit rögzít {#what-is-recorded}

- halálok az áldozattal, a gyilkossal, a fegyverrel, a sérülés típusával és a zónával (játékosok és NPC-k)
- kiiktatott és megsemmisített járművek a vezetőjükkel, az okkal és a zónával
- kvantumutazási célok, naprendszer-váltások, megjelenések, újraéledések, harcképtelenségek
- minden Game.log-sor egészben a heat.raw.parquet fájlban
- ölések (játékos és NPC), halálok, öngyilkosságok, megsemmisített és elvesztett járművek, kvantumugrások

## Honnan származik {#where-it-comes-from}

&lt;install>\StarCitizen\LIVE\Game.log (a futó StarCitizen.exe build-mappája), csak az a naplófájl, amelyet a játék ír - egy Easy Anti-Cheat-es játék: semmi nem nyúl a folyamatához

## Bekapcsolás {#how-to-switch-it-on}

Semmit sem kell bekapcsolni: a watcher úgy olvassa a forrást, ahogy a játék vagy a platform biztosítja.

## Működés {#how-it-works}

Star Citizen: a kliens saját naplója, `<install>\StarCitizen\LIVE\Game.log`.

A játék minden indításkor újraírja a Game.log fájlt (az előző a `logbackups\` mappába kerül). Csak ez a fájl olvasódik: a Star Citizen Easy Anti-Cheat-et futtat, és itt semmi nem nyúl a játék folyamatához. A sorok UTC időbélyeggel és szinttel kezdődnek, majd egy címkével szögletes zárójelben:

```text
<2025-04-13T17:17:51.279Z> [Notice] <Actor Death> CActor::Kill: 'Victim' [200146297631] in zone
    'ANVL_Hornet_F7A_Mk2_2677329226210' killed by 'Killer' [202061381370] using
    'GATS_BallisticGatling_S3_2677329225797' [Class unknown] with damage type 'VehicleDestruction'
    from direction x: 0.000000, y: 0.000000, z: 0.000000 [Team_ActorTech][Actor]
<...> [Notice] <Vehicle Destruction> CVehicle::OnAdvanceDestroyLevel: Vehicle 'ANVL_Arrow_123' [123] in zone
    'OOC_Stanton_1_Hurston' [pos x: 1.0, y: 2.0, z: 3.0 vel x: 0, y: 0, z: 0] driven by 'Driver' [456]
    advanced from destroy level 0 to 2 caused by 'Attacker' [789] with 'Combat' [Team_VehicleFeatures][Vehicle]
<...> [Notice] <AccountLoginCharacterStatus_Character> Character: createdAt 1 - updatedAt 2 - geid 3 -
    accountId 4 - name Handle - state STATE_CURRENT [Team_GameServices][Login]
<...> [Notice] <Quantum Navtarget> CSCItemQuantumDrive::RmMulticastOnQTToPoint : Local client user
    Handle[200000000001] received QT data for Entity:AEGS_Gladius_123[123] to Target Stanton1b ...
<...> [Notice] <Changing Solar System> ... Client entity Handle ... changing system from Stanton to Pyro ...
```

(itt tördelve; a fájlban soronként egy sor.) Egy halál zónája általában nem egy hely, hanem az a hajó, amelyben az áldozat ült. A formátumot a Cloud Imperium nem dokumentálja, és a patchek között változik; a minták azoknak a közösségi kill-követőknek a sorait követik, amelyek a sorokat olvassák (pl. <https://github.com/DimmaDont/all-slain>, MIT - csak tények), és ami nem illeszkedik, azt átugorja, nem találgatja. Egy jármű `pos` értéke zónához viszonyított, és csak szövegként van megőrizve: nincsenek koordináták rajzolva.

Minden sor egészben megmarad a munkamenet nyers mellékfájljában (a 3DHeat konvertáló szabálya szerint), illeszkedjen vagy sem: a `type` a sor címkéje szögletes zárójelben (`Actor Death`, `Spawn Flow`, ...), különben a sor első zárójeles szava (`Notice`, `CSessionManager::OnClientSpawned`), különben `untagged`; az időbélyeg nélküli sor `untimed`.

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

`bad_lines`, `deaths`, `incapacitations`, `kills`, `npc_kills`, `player_kills`, `quantum_jumps`, `suicides`, `system_jumps`, `vehicles_destroyed`, `vehicles_lost`

A kapcsos zárójeles kulcsot futásidőben töltik ki (a `score.{team}` csapatonként egy kulcs). Azok a kulcsok, amelyeket a kód a játék mezőinek táblázatából vagy a játék saját statisztikanevei közül vesz, nincsenek ebben a listában; a fenti "Mit rögzít" rész nevezi meg őket.

## Teljesség {#completeness}

A watcher követi a 3DHeat [konvertáló szabályát](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md): amit a forrás tartalmaz, azt beolvassa vagy megőrzi, sosem dobja el. A sorokon kívül minden csomagot, oldalt, sort vagy választ, amelyet az adapter kap, egészben megőriz a munkamenet `heat.raw.parquet` fájlja (oszlopok: `time`, `ms`, `type`, `used`, `payload`, `text`, majd minden név szerint megtartott mező; a `used` jelöli, ami sorrá is vált), és a `meta.json` `selfCheck.completeness` mezője minden `type` értéket megszámol - a `lost` értéke 0.

**Beolvasva**

- `<Actor Death>`: áldozat, gyilkos, fegyver és annak osztálya, a sérülés típusa, zóna; NPC vagy játékos
- `<Vehicle Destruction>`: jármű, zóna, zónához viszonyított pozíció szövegként, vezető, ok, mód, pusztítási szint
- `<Quantum Navtarget>` célok, `<Changing Solar System>`, `OnClientSpawned`, kórházi újraéledések, harcképtelenségek az okaikkal, `EndSession`
- a játékos azonosítója az `<AccountLoginCharacterStatus_Character>` sorból vagy a bejelentkezési sorból

**Nyersen megőrizve**

- minden Game.log-sor egészben, `type` = a címkéje szögletes zárójelben (`Actor Death`, `Vehicle Destruction`, `Spawn Flow`, `Jump Drive State Changed`, `SHUDEvent_OnNotification`, `RequestLocationInventory`, ...), különben a sor első zárójeles szava (`Notice`, `CSessionManager::OnClientSpawned`, ...), különben `untagged`; az időbélyeg nélküli sorok (a napló fejléce, a tördelt szöveg) `untimed` néven; a `used` ott, ahol a sor sorrá vált

**Nem elérhető**

- pozíciók: a napló egy olyan keretben sem ad, amelyet ki lehetne rajzolni (egy megsemmisített jármű `pos` értéke olyan zónához képest van, amelynek helye nincs naplózva)
- bármi a játék folyamatából vagy hálózatából: a Star Citizen Easy Anti-Cheat-et futtat; csak a naplófájl olvasódik
- korábbi indítások naplói (`logbackups`): minden indítás Game.log-ját akkor őrizzük meg, amikor lejátsszák
- egy patch által megváltoztatott formátumú sorok: nyersen megőrizve, újra dekódolva, ha az új forma ismert

**Méret**: a Game.log játékidőben óránként körülbelül 5-15 MB-tal nő (több a forgalmas területeken és hibák esetén); a zstd a heat.raw.parquet fájlban tizedére csökkenti

## Ellenőrzés {#verified}

szintetikus Game.log-sorokon tesztelve, a közösségi követők által dokumentált formátumban; a játékon nincs tesztelve

## Forrás {#source}

[heat3d_watch/adapters/starcitizen.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/starcitizen.py)

<!-- Generated from the adapter by tools/gen_game_pages.py; change the adapter and run it again rather than editing this page. -->
