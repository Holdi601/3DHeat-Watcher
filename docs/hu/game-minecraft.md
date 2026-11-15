---
title: "Minecraft (naplófájlok)"
nav_order: 33
lang: "hu"
source: game-minecraft.md
source_hash: "35cfea9d36a0"
nav_exclude: true
search_exclude: true
---
# Minecraft (naplófájlok) {#minecraft-log-files}

Amíg a Minecraftot játszod, a watcher beolvassa a játék által írt fájlokat, és elmenti, mi történt, így később megnézheted térképen a 3DHeat megjelenítőben.

*Műszaki részletek: adapter `minecraft`, típus [`log`](sources-and-rules.md); akkor fut, amikor a `javaw.exe` vagy a `java.exe` fut, és 0,5 másodpercenként keres új adatot.*

## Mit rögzít {#what-is-recorded}

- saját és más játékosok pozíciója (blokk = m, y felfelé) minden világmentéskor, a dimenzió a munkamenet
- megjelenés a pozícióval, amikor egy játékos belép a (beépített) szerverre
- csatlakozások, kilépések, halálok a halálüzenettel, fejlesztések, csevegősorok
- halálok, fejlesztések, csevegőüzenetek; a statisztikafájlból: játékidő, távolság, mob- és játékos-ölések, ugrások, sebzés, bányászott blokkok, készített tárgyak (ennek a munkamenetnek a része)
- minden naplósor, és minden mentett statisztika-, fejlesztés- és játékosfájl egészben a heat.raw.parquet fájlban

## Honnan származik {#where-it-comes-from}

%APPDATA%\\.minecraft\logs\latest.log (követve), saves\\&lt;világ>\stats\\&lt;uuid>.json és saves\\&lt;világ>\playerdata\\&lt;uuid>.dat / level.dat (gzip NBT), a játék mentésekor olvasva

## Hogyan kapcsold be {#how-to-switch-it-on}

Semmit sem kell bekapcsolni: a watcher úgy olvassa a forrást, ahogy a játék vagy a platform biztosítja.

## Hogyan működik {#how-it-works}

Minecraft (Java Edition): a játék által írt napló-, statisztika- és játékosfájlok.

Hol (`%APPDATA%\.minecraft\`):

* `logs\latest.log` – a játék naplója, minden indításkor újként (a régit egy dátumozott .log.gz-be csomagolja). A sorok `[hh:mm:ss] [szál/SZINT]: üzenet` alakúak (a modulbetöltők `[ddMMMyyyy hh:mm:ss.mmm] [szál/SZINT] [naplózó/]: ...` alakot írnak). Itt van az, amit a játékosok a csevegésben látnak: csatlakozások és kilépések, halálüzenetek, fejlesztések, csevegés – az egyjátékos világ beépített szervere ugyanezeket a sorokat még egyszer írja, így az ugyanabban a másodpercben ismétlődő sor egyszer számít. A "Setting user: <név>" megnevezi a játékost; a szerver "<név>[...] logged in with entity id N at (x, y, z)" sora megadja, hol jelentek meg.
* `saves\<világ>\stats\<uuid>.json` – a statisztikaképernyő, a világ mentésekor íródik (néhány percenként automatikusan, és kilépéskor): `stats` -> `minecraft:custom` (play_time tickben, mob_kills, \*_one_cm távolságok, jump, ...), `minecraft:mined`, `minecraft:crafted`, ... A világ összesítései; a munkamenet adatai a különbség ahhoz képest, amit a fájl a játék indulásakor mondott. Formátum: <https://minecraft.wiki/w/Statistics>
* `saves\<világ>\playerdata\<uuid>.dat` (és a `level.dat` -> Data -> Player egyjátékos-gazdagépnél) – gzip-tömörített NBT, ugyanazokkor a mentéseknél íródik: `Pos` [x, y, z] dupla számok, `Rotation` [yaw, pitch], `Dimension` ("minecraft:overworld"; 1.16 előtt egész 0/-1/1). Az NBT a <https://minecraft.wiki/w/NBT_format> szerint – itt egy saját kis olvasó olvassa.
* `saves\<világ>\advancements\<uuid>.json` – a fejlesztésképernyő haladása, ugyanazokkor a mentéseknél íródik.

A koordináták blokkban értendők, egy blokk egy méter, y felfelé; x kelet, z dél – jobbkezes rendszer, úgy rajzolva, ahogy van. A pozíciók csak a világ mentésekor kerülnek elő, ezért egy útvonal néhány pont az automatikus mentésenként, nem nyomvonal; a dimenzió a `session`, így a Nether nem rajzolódik a Felvilág fölé.

Mindent, amit beolvas, egészben megtart a munkamenet nyers mellékletében (a 3DHeat konvertálási szabálya): minden naplósor a szintje alatt (`INFO`, `WARN`, `ERROR`, ...; a szögletes zárójeles fejléc nélküli sor, mint egy verem-nyomkövetés, `untagged` alatt), és minden mentett fájl a típusa alatt (`stats`, `advancements`, `playerdata`, `level.dat`) – a JSON szövegként, az NBT bájtjaiként. Egy statisztikafájl számait csak ahhoz képest lehet érteni, amit a játék indulásakor mondott, ezért ennek első példánya is megmarad (`baseline`), az első alkalommal, amikor a fájl változik.

## Pozíciók és tengelyek {#positions-and-axes}

| | |
|---|---|
| Rögzített pozíciók | igen |
| Felfelé mutató tengely | `y` |
| Mértékegység | blokk (1 blokk = 1 m) |
| Tükrözés a megjelenítőnek | nincs |
| Mértékskála (`scale`: a megjelenítő ezzel szorozza a pozíciókat) | 1 |

Ezek bekerülnek minden munkamenet `meta.json` fájljának `axes` mezőjébe, és ha a munkamenetnek vannak pozíciói, a `heat.parquet` láblécébe, így a 3DHeat megjelenítő maga forgatja és méretezi a sorokat – lásd [Az adatok](the-data.md).

## Többjátékos mód {#multiplayer}

- Online játékként jelölve (`multiplayer`): **igen**. A `games --markdown` ezt így jeleníti meg: "engedélyezett (csak azt olvassa, amit a játék közzétesz)".
- Típus `log`: csak azt olvassa, amit a játék vagy a platform kiad (fájlok, amelyeket a játék futás közben ír), ezért online játék közben is rögzít, nem csak offline; a jelző csak azt dönti el, szabad-e egyáltalán memóriát olvasni.
- Memória: ez az adapter **soha** nem olvas memóriát. Csak a `memory` adapterek olvasnak memóriát, és soha nem olyan játékhoz, amely online játékként van jelölve – lásd [Források és szabályok](sources-and-rules.md).

## Rögzített statisztikák {#statistics-recorded}

Ennek az adapternek a kódja névről név beállított statisztikakulcsai (minden munkamenet `stats` mezője a `meta.json`-ban és a `watcher.sqlite` `stats` táblájában):

`advancements`, `bad_files`, `bad_lines`, `chat_messages`, `deaths`, `joins`, `others_deaths`, `world`

A kapcsos zárójelben lévő kulcsot futásidőben töltik ki (`score.{team}` csapatonként egy kulcs). Azok a kulcsok, amelyeket a kód a játék mezőinek táblázatából vagy a játék saját statisztikanevéből vesz, nincsenek ebben a listában; a fenti "Mit rögzít" rész nevezi meg őket.

## Teljesség {#completeness}

A watcher követi a 3DHeat [konvertálási szabályát](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md): amit a forrás tartalmaz, azt beolvassa vagy megtartja, soha nem dobja el. A sorokon kívül minden csomagot, lapot, sort vagy választ, amelyet az adapter kap, egészben megtart a munkamenet `heat.raw.parquet` fájljában (oszlopai `time`, `ms`, `type`, `used`, `payload`, `text`, majd minden név szerint megtartott mező; a `used` jelöli, ami sorrá is vált), a `meta.json` `selfCheck.completeness` adatai pedig minden `type`-ot számolnak – a `lost` értéke 0.

**Beolvasva**

- latest.log: a játékos neve (`Setting user`), belépések pozícióval, csatlakozások, kilépések, halálok a halálüzenettel, fejlesztések, csevegősorok, a szerver leállása
- stats/<uuid>.json: játékidő, távolság, mob- és játékos-ölések, ugrások, okozott és elszenvedett sebzés, bányászott blokkok, készített tárgyak – ennek a munkamenetnek a része
- playerdata/<uuid>.dat és level.dat (NBT): pozíció, dimenzió, yaw, pitch, életerő, XP-szint

**Nyers formában megtartva**

- minden latest.log-sor egészben, `type` = a szintje (`INFO`, `WARN`, `ERROR`, `DEBUG`, `FATAL`), a naplózó szála a `thread` mezőben, `used`, ahol sorrá vált; a szögletes zárójeles fejléc nélküli sor (verem-nyomkövetés, egy mod bannere) `untagged`-ként
- minden stats/<uuid>.json egészben szövegként, `type` `stats` (`used`: a számai a statisztikákban vannak), a játék indulásakori első példánya `baseline`-ként
- minden advancements/<uuid>.json egészben szövegként, `type` `advancements` (minden kritérium és az, hogy mikor teljesült; még nincs sorokká alakítva)
- minden playerdata/<uuid>.dat és level.dat egészben bájtokként (gzip NBT), `type` `playerdata` / `level.dat`, `used`, ahol pozíciót adott: a leltár, az ender láda, a hatások, a spawn-pont, a játékszabályok, a világ magja és ideje csak itt vannak meg
- minden mentett fájlnak van `world` és `file` mezője (az elérési útja a `saves` alatt)

**Nem elérhető**

- pozícióvonal: a játék a játékos pozícióját csak a világ mentésekor írja (néhány percenként és kilépéskor)
- pozíciók más által üzemeltetett szerveren: a világfájlok a szerveren vannak, nem itt; ilyenkor csak a napló olvasódik
- maga a világ (region .mca fájlok, entitások, data/\*.dat térképek és rajdok): nagy, és a terep, nem a játék
- korábbi munkamenetek naplói (logs/\*.log.gz): akkor rögzülnek, amikor játszottak velük
- Bedrock Edition: nem ír ilyen naplót vagy fájlokat

**Méret**: latest.log óránként 0,1–2 MB (modokkal több); egy statisztikafájl 5–50 KB, egy játékosfájl 5–100 KB automatikus mentésenként, a level.dat 1–20 KB – összesen nagyjából 1–5 MB óránként; a zstd a heat.raw.parquet fájlban a szöveget nagyjából a tizedére tömöríti (az NBT-fájlok már gzip-pel tömörítettek)

## Ellenőrizve {#verified}

szintetikus naplósorokon, statisztikai JSON-on és a közzétett formátumok szerint épített NBT-fájlokon tesztelve; a játékon még nem tesztelve

## Forrás {#source}

[heat3d_watch/adapters/minecraft.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/minecraft.py)

<!-- Generated from the adapter by tools/gen_game_pages.py; change the adapter and run it again rather than editing this page. -->
