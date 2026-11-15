---
title: "EVE Online (naplófájlok)"
nav_order: 20
lang: "hu"
source: game-eve.md
source_hash: "a5ab6c312c86"
nav_exclude: true
search_exclude: true
---
# EVE Online (naplófájlok) {#eve-online-log-files}

Amíg az EVE Online-t játszod, a watcher beolvassa a játék által írt fájlokat, és elmenti, mi történt, hogy később statisztikaként és idővonalon megnézhesd.

*Műszaki részletek: adapter `eve`, típus [`log`](sources-and-rules.md); fut, amíg az `exefile.exe` megy, és 0,5 másodpercenként keres új adatot.*

## Mit rögzít {#what-is-recorded}

- az okozott és kapott sebzés a másik hajóval, pilótával, a társaság rövidítésével, fegyverrel és a találat minőségével
- az okozott és kapott mellélövések
- kifizetett vadászjutalmak (NPC-gyilkosságok) ISK-ban
- ugrások rendszerek között
- minden gamelog- és csetnapló-sor egészben a heat.raw.parquet fájlban
- okozott és kapott sebzés, találatok, vadászjutalom-gyilkosságok és ISK, ugrások

## Honnan származik {#where-it-comes-from}

%USERPROFILE%\Documents\EVE\logs\Gamelogs\\\*.txt és a mellettük lévő Chatlogs\\\*.txt fájlok (minden fájl, amely a kliens indítása óta íródott)

## Bekapcsolás {#how-to-switch-it-on}

Semmit sem kell bekapcsolni: a watcher úgy olvassa a forrást, ahogy a játék vagy a platform biztosítja.

## Működés {#how-it-works}

EVE Online: a kliens játéknaplói, `Documents\EVE\logs\Gamelogs\*.txt`.

A kliens karakterenként és bejelentkezésenként egy fájlt ír, `<yyyymmdd>_<hhmmss>[_<karakterazonosító>].txt` névvel; a fájlba írás alapértelmezetten be van kapcsolva. Több egyszerre futó kliens mindegyike a sajátját írja, ezért minden fájlt követ, amely a játék indítása óta íródott. A fejléc és a sorok (az EVE idő UTC):

```text
------------------------------------------------------------
  Gamelog
  Listener: Character Name
  Session Started: 2024.07.02 19:41:40
------------------------------------------------------------
[ 2024.07.02 20:31:28 ] (combat) <color=0xff00ffff><b>200</b> <color=0x77ffffff><font size=10>to</font>
    <b><color=0xffffffff>Pilot[TICK](../Ship)</b><font size=10><color=0x77ffffff> - Weapon - Penetrates
[ 2024.06.25 15:20:01 ] (combat) <color=0xffcc0000><b>375</b> ... from ... - Weapon - Hits
[ 2024.06.25 15:21:00 ] (bounty) <font size=12><b><color=0xff00aa00>15,000 ISK</b> added to next bounty payout
[ 2024.06.25 15:30:00 ] (None) Jumping from System A to System B
```

(a combat sor a fájlban egy sor.) A illesztés előtt a formázó címkék le lesznek vágva. A fájl az évek során UTF-8 és UTF-16 volt; mindkettő olvasható. A formátumot a CCP nem dokumentálja; ez a kliens egyszerű szöveges naplója, úgy olvasva, ahogy a közösségi harci-napló eszközök olvassák (pl. <https://docs.rs/crate/eve-log-parser>). Pozíció nincs.

Mellette a `Documents\EVE\logs\Chatlogs\<csatorna>_<yyyymmdd>_<hhmmss>[_<azonosító>].txt`: csatornánként és bejelentkezésenként egy fájl (ha a csetnaplózás be van kapcsolva, ami a kliens alapértelmezettje), UTF-16, fejléccel, amely megnevezi a csatornát és a hallgatót, majd `[ yyyy.mm.dd hh:mm:ss ] Feladó > üzenet` sorokkal.

Mindkettő minden sora egészben megmarad a munkamenet nyers mellékfájljában (a 3DHeat konvertáló szabálya szerint): a gamelog-sor a csatornájának nevével szögletes zárójelben (`combat`, `notify`, `bounty`, `None`, ...), a csetsor `chat` néven a csatornájával, a fejlécsorok pedig `gamelog header` / `chatlog header` néven.

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

`bad_lines`, `bounty_isk`, `bounty_kills`, `damage_dealt`, `damage_received`, `hits_dealt`, `hits_received`, `jumps`, `misses_dealt`, `misses_received`

A kapcsos zárójeles kulcsot futásidőben töltik ki (a `score.{team}` csapatonként egy kulcs). Azok a kulcsok, amelyeket a kód a játék mezőinek táblázatából vagy a játék saját statisztikanevei közül vesz, nincsenek ebben a listában; a fenti "Mit rögzít" rész nevezi meg őket.

## Teljesség {#completeness}

A watcher követi a 3DHeat [konvertáló szabályát](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md): amit a forrás tartalmaz, azt beolvassa vagy megőrzi, sosem dobja el. A sorokon kívül minden csomagot, oldalt, sort vagy választ, amelyet az adapter kap, egészben megőriz a munkamenet `heat.raw.parquet` fájlja (oszlopok: `time`, `ms`, `type`, `used`, `payload`, `text`, majd minden név szerint megtartott mező; a `used` jelöli, ami sorrá is vált), és a `meta.json` `selfCheck.completeness` mezője minden `type` értéket megszámol - a `lost` értéke 0.

**Beolvasva**

- gamelog `(combat)` sorok: a kapott és az okozott találatok (mennyiség, másik pilóta, társaság rövidítése, hajó, fegyver, találat minősége) és mindkét irányú mellélövések
- gamelog `(bounty)` kifizetések ISK-val, és a `Jumping from A to B` sorok
- a gamelog fejlécének Listener sora: kié a napló

**Nyersen megőrizve**

- minden gamelog-sor egészben, `type` = a csatornája szögletes zárójelben (`combat`, `notify`, `info`, `bounty`, `mining`, `question`, `hint`, `warning`, `None`, ...), `file` és `listener` mezőkkel; a `used` ott, ahol sorrá vált; a fejlécsorok `gamelog header` néven
- minden csetnapló-sor egészben (helyi, társasági, flotta- és privát csatornák, valamint az `EVE System` értesítések, mint például a helyi csatorna változása ugrás után), `type` `chat`, a `channel`, `listener` és `file` mezőkkel; a fejlécsorok `chatlog header` néven. Még nincsenek sorokká alakítva
- a formázó címkék (`<color>`, `<b>`, `<font>`) a nyers szövegben maradnak; a sorokban le vannak vágva

**Nem elérhető**

- pozíciók: a kliens nem ír ilyet a naplóiba
- más pilóták harcai: a gamelog a hallgató saját naplója
- korábbi bejelentkezések naplói: minden bejelentkezés új fájlokat ír; a kliens e futásánál régebbiek nem kerülnek újraolvasásra
- csevegés, ha a játékos a kliens beállításaiban kikapcsolta a csetnaplózást
- a kliens saját gyorsítótár- és beállítófájljai: nem naplók, és nincsenek dokumentálva

**Méret**: egy gamelog óránként 0,1-2 MB (legtöbb a harcban); a csetnaplók a megnyitott csatornáktól függnek - egy forgalmas helyi vagy flotta csatorna óránként 0,5-3 MB; a zstd a heat.raw.parquet fájlban nagyjából tizedére csökkenti

## Ellenőrzés {#verified}

szintetikus gamelog-sorokon tesztelve, a közösségi elemzők által közzétett formátumban; a játékon nincs tesztelve

## Forrás {#source}

[heat3d_watch/adapters/eve.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/eve.py)

<!-- Generated from the adapter by tools/gen_game_pages.py; change the adapter and run it again rather than editing this page. -->
