---
title: "Path of Exile (naplófájlok)"
nav_order: 36
lang: "hu"
source: game-poe.md
source_hash: "9facfd5a1551"
nav_exclude: true
search_exclude: true
---
# Path of Exile (naplófájlok) {#path-of-exile-log-files}

Amíg a Path of Exile-t játszod, a watcher beolvassa a játék által írt fájlokat, és elmenti, mi történt, hogy később statisztikaként és idővonalon megnézhesd.

*Műszaki részletek: adapter `poe`, típus [`log`](sources-and-rules.md); fut, amíg a `PathOfExile.exe`, `PathOfExile_x64.exe`, `PathOfExileSteam.exe`, `PathOfExile_x64Steam.exe`, `PathOfExileEGS.exe`, `PathOfExile_x64EGS.exe`, `PathOfExile_KG.exe` vagy `PathOfExile_x64_KG.exe` megy, és 0,5 másodpercenként keres új adatot.*

## Mit rögzít {#what-is-recorded}

- belépett zónák a területszinttel, a terület azonosítójával és a magjával
- szintlépések osztállyal és szinttel
- halálok ("has been slain")
- játékosok belépése és kilépése a területről, bejövő és kimenő suttogások, kereskedési kérések, elfogadott kereskedések
- ennek az ülésnek minden Client.txt-sora egészben a heat.raw.parquet fájlban
- halálok, megszerzett szintek, legmagasabb szint, bejárt zónák, különböző zónák, suttogások, kereskedési kérések, kereskedések

## Honnan származik {#where-it-comes-from}

&lt;install>\logs\Client.txt a Path of Exile vagy a Path of Exile 2 játékból (követve; a telepítési mappa a futó végrehajtható fájlé)

## Bekapcsolás {#how-to-switch-it-on}

Semmit sem kell bekapcsolni: a watcher úgy olvassa a forrást, ahogy a játék vagy a platform biztosítja.

## Működés {#how-it-works}

Path of Exile és Path of Exile 2: a kliens naplója, `<install>\logs\Client.txt`.

Mindkét játék ugyanabba a Client.txt fájlba ír a telepítési mappájában, amíg telepítve van (átível az indításokon). A sorok így néznek ki:

```text
2024/01/01 12:00:00 123456789 cff94598 [INFO Client 1234] : You have entered Lioneye's Watch.
2024/01/01 12:00:00 123456789 cff94598 [DEBUG Client 1234] Generating level 2 area "1_1_2" with seed 1
2024/01/01 12:00:00 123456789 cff94598 [INFO Client 1234] : Name (Witch) is now level 2
2024/01/01 12:00:00 123456789 cff94598 [INFO Client 1234] : Name has been slain.
2024/01/01 12:00:00 123456789 cff94598 [INFO Client 1234] @From Name: Hi, I would like to buy your ...
```

- helyi idő, egy ezredmásodperces számláló, egy hash, a szint és a szál, majd az, amit a csetablak mutat. Az üzenetek az angol kliensé; más nyelvű kliens lefordítva írja őket, és azok itt nem értelmezhetők. Pozíciót egyik sem ad. A formátumot a Grinding Gear Games nem dokumentálja; ez a játék egyszerű szöveges naplója, ahogy a közösségi eszközök (kereskedési segédek, szintútmutatók) évek óta olvassák - pl. <https://github.com/klayveR/poe-log-monitor> (MIT) az eseménylistához.

A telepítési mappa a futó végrehajtható fájlé; anélkül a Steam-könyvtárakat és az önálló kliens alapértelmezett mappáját keresi.

Ennek az ülésnek minden sora egészben megmarad a munkamenet nyers mellékfájljában (a 3DHeat konvertáló szabálya szerint), függetlenül attól, hogy itt van-e jelentése: a `type` a szint és a naplózó a szögletes zárójelben (`INFO Client`, `DEBUG Client`, `WARN Client`, ...), a zárójel nélküli bélyeges sor `untagged`, az idő nélküli sor `untimed` néven.

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

`bad_lines`, `character_class`, `deaths`, `level`, `levels_gained`, `trade_requests_received`, `trade_requests_sent`, `trades`, `whispers`, `zones_distinct`, `zones_entered`

A kapcsos zárójeles kulcsot futásidőben töltik ki (a `score.{team}` csapatonként egy kulcs). Azok a kulcsok, amelyeket a kód a játék mezőinek táblázatából vagy a játék saját statisztikanevei közül vesz, nincsenek ebben a listában; a fenti "Mit rögzít" rész nevezi meg őket.

## Teljesség {#completeness}

A watcher követi a 3DHeat [konvertáló szabályát](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md): amit a forrás tartalmaz, azt beolvassa vagy megőrzi, sosem dobja el. A sorokon kívül minden csomagot, oldalt, sort vagy választ, amelyet az adapter kap, egészben megőriz a munkamenet `heat.raw.parquet` fájlja (oszlopok: `time`, `ms`, `type`, `used`, `payload`, `text`, majd minden név szerint megtartott mező; a `used` jelöli, ami sorrá is vált), és a `meta.json` `selfCheck.completeness` mezője minden `type` értéket megszámol - a `lost` értéke 0.

**Beolvasva**

- `You have entered <zone>`, a területszinttel, a terület azonosítójával és a magjával a megelőző `Generating level` sorból
- `<name> (<class>) is now level <n>`, `<name> has been slain`, játékosok belépése és kilépése a területről, bejövő és kimenő suttogások (azzal, hogy kereskedési kérés-e), elfogadott és megszakított kereskedések

**Nyersen megőrizve**

- ennek az ülésnek minden sora egészben, `type` = a szint és a naplózó a szögletes zárójelben (`INFO Client`, `DEBUG Client`, `WARN Client`, `CRIT Client`, ...), a `used` ott, ahol sorrá vált: globális, kereskedési, csapat- és céhcsevegés, `Connecting to instance server`, AFK- és DND-értesítések, a csevegési parancsokra adott válaszok, mint a `/played` és a `/deaths`, a kliens betöltési és motorsorai - megőrizve, még nincsenek sorokká alakítva
- bélyeges sor zárójel nélkül (`***** LOG FILE OPENING *****`) `untagged`, időbélyeg nélküli sor `untimed` néven
- a napló kliens-indítása nélküli sorai: nincsenek

**Nem elérhető**

- pozíciók: a naplóban semmi nem ad egyet
- amit más nyelvű kliens ír: a sorok megmaradnak, de csak az angol üzenetek lesznek sorokká
- korábbi indítások sorai: a Client.txt átível az indításokon; a játék e futása előtt bélyegzett sorok kimaradnak (játékkor már megőrződtek)
- ölések, sebzés, zsákmány és a passzív fa: a játék nem naplózza őket

**Méret**: a Client.txt óránként körülbelül 0,3-3 MB-tal nő (legtöbbet a területek betöltésekor írt DEBUG-sorok adják, és a forgalmas kereskedési csevegés); a zstd a heat.raw.parquet fájlban tizedére csökkenti

## Ellenőrzés {#verified}

szintetikus Client.txt-sorokon tesztelve a játék formátumában; a játékon nincs tesztelve

## Forrás {#source}

[heat3d_watch/adapters/poe.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/poe.py)

<!-- Generated from the adapter by tools/gen_game_pages.py; change the adapter and run it again rather than editing this page. -->
