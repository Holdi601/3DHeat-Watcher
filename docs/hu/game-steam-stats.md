---
title: "Steam-statisztikák (platform)"
nav_order: 43
lang: "hu"
source: game-steam-stats.md
source_hash: "24fa6512bd6d"
nav_exclude: true
search_exclude: true
---
# Steam-statisztikák (platform) {#steam-statistics-platform}

A watcher elmenti, amit a Steam-statisztika a játékaidról megőriz, hogy később statisztikaként és idővonalon is megnézhesd a történetedet.

*Technikai részletek: adapter `steam-stats`, típus [`platform`](sources-and-rules.md); folyamatosan fut (nem vár arra, hogy játék induljon), és 30 másodpercenként keres új adatot.*

## Mit rögzít {#what-is-recorded}

- minden statisztikát, amelyet egy játék a Steamben tárol (a saját nevével és értékével), játékonként, változáskor
- eredményfeloldások megjelenítendő névvel, leírással és feloldási idővel
- statisztikai változások régi értékkel, új értékkel és különbséggel
- játékidő (percben, az elmúlt két hétben) és az utolsó játék ideje

## Honnan jön {#where-it-comes-from}

a Steam helyi statisztikai gyorsítótára: %STEAM%\appcache\stats\UserGameStats_&lt;account>_&lt;appid>.bin, a mellette lévő UserGameStatsSchema_&lt;appid>.bin sémával; a játékidő a %STEAM%\userdata\\&lt;account>\config\localconfig.vdf fájlból (a %STEAM% a HKCU\Software\Valve\Steam SteamPath kulcsból)

## Hogyan kapcsolható be {#how-to-switch-it-on}

Semmit nem kell bekapcsolni: a watcher úgy olvassa a forrást, ahogy a játék vagy a platform adja.

## Hogyan működik {#how-it-works}

Amit az indító és a grafikus illesztőprogram tart nyilván a játékról: a Steam statisztikái, eredményei, játékideje és idővonalai, valamint az NVIDIA kiemelései és klipjei.

Egyik forrásnak sem kell, hogy a játék együttműködjön vagy fusson, így az itt lévő három adapter mindig be van kapcsolva, és néhány másodpercenként néhány fájlt néz meg.

#### Steam-statisztikák (`steam-stats`) {#steam-statistics-steam-stats}

`<Steam>\appcache\stats\UserGameStats_<account>_<appid>.bin`, amelyet a Steam kliens újraír, valahányszor a játék eltárolja a statisztikáit, és a mellette lévő `UserGameStatsSchema_<appid>.bin` sémával visszafejtjük (bináris KeyValues, lásd `_steam.py`). A statisztikák a játék által meghatározott egész vagy lebegőpontos számok; az eredmények bitek, feloldási idővel Unix-másodpercben. A játékidő a `<Steam>\userdata\<account>\config\localconfig.vdf` fájlban van, az apps/&lt;appid> alatt: Playtime és Playtime2wks percben, LastPlayed Unix-másodpercben. A Steamet a HKCU\Software\Valve\Steam SteamPath kulcsból találjuk meg.
Statisztikai API: <https://partner.steamgames.com/doc/features/achievements>

Ugyanez a modul szolgálja ki ezeket is: [NVIDIA highlights (platform)](game-nvidia-highlights.md), [Steam Timeline (platform)](game-steam-timeline.md).

## Pozíciók és tengelyek {#positions-and-axes}

| | |
|---|---|
| Pozíciók rögzítve | nem |
| Felfelé mutató tengely | `y` |
| Mértékegység | méter |
| Tükrözve a megtekintőnek | nincs |
| Mértékegység-szorzó (`scale`: a megtekintő ezzel szorozza a pozíciókat) | 1 |

Ezek bekerülnek minden munkamenet `meta.json`-jába (`axes`), és ha a munkamenetnek vannak pozíciói, a `heat.parquet` láblécébe is, így a 3DHeat megtekintő maga forgatja és méretezi a sorokat – lásd [Az adatok](the-data.md).

## Többjátékos {#multiplayer}

- Online játszottként jelölve (`multiplayer`): **nem**. A `games --markdown` ezt "single-player" jelöléssel mutatja.
- `platform` típus: csak azt olvassa, amit a játék vagy a platform kiad (amit a Steam vagy a grafikus illesztőprogram tart nyilván), így online játékban is rögzít, nemcsak offline; a jelző csak azt dönti el, szabad-e valaha memóriát olvasni.
- Memória: ez az adapter **soha** nem olvas memóriát. Csak a `memory` adapterek olvasnak memóriát, és soha nem olyan játékhoz, amelyet online játszottként jelöltek meg – lásd [Források és szabályok](sources-and-rules.md).

## Rögzített statisztikák {#statistics-recorded}

Statisztikakulcsok, amelyeket ennek az adapternek a kódja név szerint állít be (minden munkamenet `stats`-ja a `meta.json`-ban és a `watcher.sqlite` `stats` táblájában):

`achievements_total`, `achievements_unlocked`, `last_played`, `playtime_2wks_minutes`, `playtime_minutes`

Kapcsos zárójelben lévő kulcsot futás közben egészítünk ki (`score.{team}` csapatonként egy kulcs). A kódnak a játék mezőinek táblázatából vagy a játék saját statisztikanevéből származó kulcsai nincsenek ebben a listában; a fenti "Mit rögzít" részben vannak megnevezve.

## Teljesség {#completeness}

A watcher követi a 3DHeat [átalakítási szabályát](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md): amit a forrás tartalmaz, azt beolvassuk vagy megtartjuk, soha nem dobjuk el. A sorokon kívül minden csomagot, oldalt, sort vagy választ, amelyet az adapter kap, egészben megőrzünk a munkamenet `heat.raw.parquet` fájljában (oszlopok: `time`, `ms`, `type`, `used`, `payload`, `text`, és minden név szerint megtartott mező; a `used` jelöli, ami sorrá is lett), a `meta.json` `selfCheck.completeness` része pedig típusonként számolja – a `lost` értéke 0.

**Beolvasva**

- a statisztikafájl minden statisztikája az API-nevén (int, float, avgrate), minden eredménybit a feloldási idejével, a séma nevezi el és írja le
- változások az utolsó olvasáshoz képest (régi, új, különbség), az új feloldások; a játékidő, a két hetes játékidő és az utolsó játék a localconfig.vdf fájlból

**Nyersen megőrizve**

- `UserGameStats`: a statisztikafájl bájtjai egészben, minden rögzítéskor (a `crc`, a `PendingChanges`, a séma által már nem definiált eredménybitek és minden kulcs, amelyet a dekódoló átugrik, benne van)
- `UserGameStatsSchema`: a sémafájl bájtjai mellette, így a statisztikák csak a munkamenetből is visszafejthetők (minden statisztika és eredmény neve minden nyelven, ikonjai, jelzői)
- `localconfig_app`: a játék teljes localconfig.vdf-blokkja JSON-ként (felhős szinkron állapota, indítási opciók, jelvények és minden más kulcs, amelyet a Steam játékonként tart), amikor a játékideje rögzítve van
- olyan statisztikafájl, amelyet a dekódoló nem tud olvasni (félbevágva íráskor, vagy új elrendezés): a bájtjai és a séma egy sorok nélküli munkamenetben (`used` false; `unreadable` a meta.json-ban)

**Nem elérhető**

- a localconfig.vdf többi része (barátok, csevegés, Steam-beállítások): nem a játéké, és magánjellegű
- statisztikai értékek két írás között: a Steam akkor írja újra a fájlt, amikor a játék eltárolja a statisztikáit, általában bezáráskor
- globális eredményarányok és mások statisztikái: azok a Steam szerverein vannak, nem itt

**Méret**: rögzített játékonként néhány KB, plusz a séma (sok eredményű játéknál akár néhány száz KB) – játékban töltött óránként jóval 1 MB alatt; a zstd a séma szövegét felére vagy annál is jobban tömöríti

## Ellenőrizve {#verified}

helyi telepítésből származó valódi statisztikafájlokon és sémákon tesztelve; a változásfelismerés bináris KeyValues formátumban épített fájlokon tesztelve

## Forrás {#source}

[heat3d_watch/adapters/platform.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/platform.py)

<!-- A heat3d_watch adapterből készült a tools/gen_game_pages.py által; az adaptert módosítsd, és futtasd újra, ne ezt az oldalt szerkeszd. -->
