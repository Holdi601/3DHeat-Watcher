---
title: "Minecraft (súbory záznamov)"
nav_order: 33
lang: "sk"
source: game-minecraft.md
source_hash: "35cfea9d36a0"
nav_exclude: true
search_exclude: true
---
# Minecraft (súbory záznamov) {#minecraft-log-files}

Počas hry Minecraft watcher číta súbory, ktoré hra zapisuje, a ukladá, čo sa stalo, aby ste to neskôr mohli pozrieť na mape v 3DHeat prehliadači.

*Technické údaje: adaptér `minecraft`, typ [`log`](sources-and-rules.md); beží, kým beží `javaw.exe` alebo `java.exe`, a hľadá nové dáta každých 0,5 s.*

## Čo sa zaznamenáva {#what-is-recorded}

- poloha vlastného a ostatných hráčov (bloky = m, y nahor) pri každom uložení sveta, dimenzia ako relácia
- zrodenie s polohou, keď sa hráč prihlási na (integrovaný) server
- pripojenia, odpojenia, smrti so správou o smrti, postupy, riadky chatu
- smrti, postupy, správy v chate; zo súboru štatistík: čas hry, vzdialenosť, zabitia príšer a hráčov, skoky, poškodenie, vyťažené bloky, vyrobené predmety (podiel tohto sedenia)
- každý riadok záznamu a každá uložená štatistika, postup a súbor hráča celé v heat.raw.parquet

## Odkiaľ to berie {#where-it-comes-from}

%APPDATA%\\.minecraft\logs\latest.log (sleduje sa), saves\\&lt;world>\stats\\&lt;uuid>.json a saves\\&lt;world>\playerdata\\&lt;uuid>.dat / level.dat (gzip NBT), čítané, keď hra uloží

## Ako to zapnúť {#how-to-switch-it-on}

Nič netreba zapínať: watcher číta zdroj tak, ako ho hra alebo platforma poskytuje.

## Ako to funguje {#how-it-works}

Minecraft (Java Edition): záznam, štatistiky a súbory hráča, ktoré hra zapisuje.

Kde (`%APPDATA%\.minecraft\`):

* `logs\latest.log` - záznam hry, nový pri každom spustení (starý sa zabalí do datovaného .log.gz). Riadky `[hh:mm:ss] [thread/LEVEL]: správa` (mod loadery zapisujú `[ddMMMyyyy hh:mm:ss.mmm] [thread/LEVEL] [logger/]: ...`). Čo hráči vidia v chate, je v ňom: pripojenia a odpojenia, správy o smrti, postupy, chat - integrovaný server jedného hráča zapíše tie isté riadky ešte raz, takže riadok zopakovaný v tej istej sekunde sa počíta raz. „Setting user: <name>" pomenúva hráča; riadok servera „<name>[...] logged in with entity id N at (x, y, z)" hovorí, kde sa objavil.
* `saves\<world>\stats\<uuid>.json` - obrazovka štatistík, zapísaná pri uložení sveta (automatické ukladanie každých pár minút a pri odchode): `stats` -> `minecraft:custom` (play_time v tickoch, mob_kills, \*_one_cm vzdialenosti, jump, ...), `minecraft:mined`, `minecraft:crafted`, ... Súčty za svet; čísla sedenia sú rozdiel oproti tomu, čo súbor hovoril pri spustení hry. Formát: <https://minecraft.wiki/w/Statistics>
* `saves\<world>\playerdata\<uuid>.dat` (a `level.dat` -> Data -> Player pre hostiteľa jednohráčovej hry) - NBT komprimované gzipom, zapisované pri tých istých uloženiach: `Pos` [x, y, z] doubles, `Rotation` [yaw, pitch], `Dimension` („minecraft:overworld"; int 0/-1/1 pred 1.16). NBT podľa <https://minecraft.wiki/w/NBT_format> - tu čítané malou vlastnou čítačkou.
* `saves\<world>\advancements\<uuid>.json` - postup na obrazovke postupov, zapisovaný pri tých istých uloženiach.

Súradnice sú bloky, jeden blok je jeden meter, y nahor; x na východ, z na juh - pravotočivý rámec, kreslí sa tak, ako je. Polohy prichádzajú len pri uložení sveta, takže trasa je niekoľko bodov na každé automatické uloženie, nie stopa; dimenzia je `session`, takže Nether sa nekreslí cez Overworld.

Všetko čítané sa uchováva celé v surovom sprievodnom súbore relácie (pravidlo konvertorov 3DHeat): každý riadok záznamu pod svojou úrovňou (`INFO`, `WARN`, `ERROR`, ...; riadok bez hlavičky v hranatých zátvorkách, napríklad výpis zásobníka, ako `untagged`), a každý uložený súbor pod svojím druhom (`stats`, `advancements`, `playerdata`, `level.dat`) - JSON ako text, NBT ako bajty. Čísla zo súboru štatistík majú zmysel len oproti tomu, čo súbor hovoril pri spustení hry, takže aj táto prvá kópia sa uchováva (`baseline`), pri prvej zmene súboru.

## Polohy a osi {#positions-and-axes}

| | |
|---|---|
| Zaznamenané polohy | áno |
| Osa nahor | `y` |
| Jednotky | bloky (1 blok = 1 m) |
| Zrkadlenie pre prehliadač | žiadne |
| Mierka jednotiek (`scale`: prehliadač ňou násobí polohy) | 1 |

Tieto hodnoty idú do `meta.json` každej relácie (`axes`) a, keď relácia obsahuje polohy, do päty `heat.parquet`, takže 3DHeat prehliadač ich otáča a škáluje sám - pozrite [Dáta](the-data.md).

## Multiplayer {#multiplayer}

- Označené ako hrané online (`multiplayer`): **áno**. `games --markdown` to zobrazí ako „povolené (číta len to, čo hra zverejňuje)".
- Druh `log`: číta len to, čo hra alebo platforma sprístupňuje (súbory, ktoré hra zapisuje počas behu), takže zaznamenáva aj v online hre, nielen offline; príznak rozhoduje len o tom, či sa pamäť smie vôbec čítať.
- Pamäť: adaptér ju **nikdy** nečíta. Pamäť čítajú len adaptéry typu `memory` a nikdy pre hru označenú ako hranú online - pozrite [Zdroje a pravidlá](sources-and-rules.md).

## Zaznamenané štatistiky {#statistics-recorded}

Kľúče štatistík, ktoré kód tohto adaptéra nastavuje podľa mena (`stats` každej relácie v `meta.json` a tabuľka `stats` v `watcher.sqlite`):

`advancements`, `bad_files`, `bad_lines`, `chat_messages`, `deaths`, `joins`, `others_deaths`, `world`

Kľúč v zložených zátvorkách sa dopĺňa za behu (`score.{team}` je jeden kľúč pre každý tím). Kľúče, ktoré kód berie z tabuľky polí hry alebo z jej vlastných názvov štatistík, v tomto zozname nie sú; čo sa zaznamenáva, uvádza vyššie časť „Čo sa zaznamenáva".

## Úplnosť {#completeness}

Watcher sa riadi pravidlom konvertorov 3DHeat ([pravidlo konvertorov](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md)): čo zdroj obsahuje, sa načíta alebo uchová, nikdy sa nezahodí. Okrem riadkov sa každý paket, stránka, riadok alebo odpoveď, ktorú adaptér dostane, uchová celá v `heat.raw.parquet` relácie (stĺpce `time`, `ms`, `type`, `used`, `payload`, `text` a ďalšie polia uchované podľa mena; `used` označuje, čo sa stalo aj riadkami), a `selfCheck.completeness` v `meta.json` počíta každý `type` - `lost` je 0.

**Načítané**

- latest.log: meno hráča (`Setting user`), prihlásenia s polohou, pripojenia, odpojenia, smrti so správou o smrti, postupy, riadky chatu, zastavenie servera
- stats/<uuid>.json: čas hry, vzdialenosť, zabitia príšer a hráčov, skoky, uštedrené a prijaté poškodenie, vyťažené bloky, vyrobené predmety - podiel tohto sedenia
- playerdata/<uuid>.dat a level.dat (NBT): poloha, dimenzia, yaw, pitch, zdravie, úroveň XP

**Uchované surové**

- každý riadok latest.log celý, `type` = jeho úroveň (`INFO`, `WARN`, `ERROR`, `DEBUG`, `FATAL`), vlákno logu v `thread`, `used`, keď sa z neho stal riadok; riadok bez hlavičky v hranatých zátvorkách (výpis zásobníka, banner modu) ako `untagged`
- každý stats/<uuid>.json celý ako text, `type` `stats` (`used`: jeho čísla sú v štatistikách), s jeho prvou kópiou zo spustenia hry ako `baseline`
- každý advancements/<uuid>.json celý ako text, `type` `advancements` (každé kritérium a kedy bolo splnené; zatiaľ sa nepremieňa na riadky)
- každý playerdata/<uuid>.dat a level.dat celý ako bajty (gzip NBT), `type` `playerdata` / `level.dat`, `used`, keď dal polohu: inventár, ender truhla, efekty, bod odrodenia, pravidlá hry, seed sveta a čas sú len tu
- každý uložený súbor má `world` a `file` (jeho cestu pod `saves`)

**Nie je k dispozícii**

- trasa polôh: hra zapisuje polohu hráča len pri uložení sveta (každých pár minút a pri odchode)
- polohy na serveri, ktorý hostí niekto iný: jeho súbory sveta sú na serveri, nie tu; vtedy sa číta len záznam
- samotný svet (súbory regiónov .mca, entity, mapy data/\*.dat a nájazdy): veľké a ide o terén, nie o hru
- záznamy predchádzajúcich sedení (logs/\*.log.gz): uchované, keď sa hrali
- Bedrock Edition: takýto záznam ani súbory nezapisuje

**Veľkosť**: latest.log 0,1-2 MB za hodinu (viac s modmi); súbor štatistík 5-50 KB a súbor hráča 5-100 KB pri každom automatickom uložení, level.dat 1-20 KB - približne 1-5 MB za hodinu dokopy; zstd v heat.raw.parquet zmenší text zhruba na desatinu (súbory NBT sú už gzip)

## Overené {#verified}

overené na syntetických riadkoch záznamu, JSON štatistikách a súboroch NBT zostavených podľa zverejnených formátov; nevyskúšané na samotnej hre

## Zdroj {#source}

[heat3d_watch/adapters/minecraft.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/minecraft.py)

<!-- Generated from the adapter by tools/gen_game_pages.py; change the adapter and run it again rather than editing this page. -->
