---
title: "Minecraft (logovací soubory)"
nav_order: 33
lang: "cs"
source: game-minecraft.md
source_hash: "35cfea9d36a0"
nav_exclude: true
search_exclude: true
---
# Minecraft (logovací soubory) {#minecraft-log-files}

Když hrajete Minecraft, Watcher čte soubory, které hra zapisuje, a ukládá, co se stalo, abyste se na to mohli později podívat na mapě v prohlížeči 3DHeat.

*Technické podrobnosti: adaptér `minecraft`, druh [`log`](sources-and-rules.md); běží, když je spuštěný `javaw.exe` nebo `java.exe`, a hledá nová data každých 0,5 s.*

## Co se zaznamenává {#what-is-recorded}

- pozice vlastního a cizích hráčů (bloky = m, osa y nahoru) pokaždé, když svět uloží; dimenze jako relace
- objevení se s pozicí, když se hráč přihlásí na (integrovaný) server
- připojení, odchody, smrti se zprávou o smrti, postupy (advancements), řádky chatu
- smrti, postupy, zprávy v chatu; ze souboru statistik: herní čas, vzdálenost, zabití mobů a hráčů, skoky, poškození, vytěžené bloky, vyrobené předměty (podíl této relace)
- každý řádek logu a každá uložená statistika, postup a soubor hráče celý v heat.raw.parquet

## Odkud to pochází {#where-it-comes-from}

%APPDATA%\\.minecraft\logs\latest.log (sledovaný), saves\\&lt;world>\stats\\&lt;uuid>.json a saves\\&lt;world>\playerdata\\&lt;uuid>.dat / level.dat (gzip NBT), čtené, když je hra uloží

## Jak to zapnout {#how-to-switch-it-on}

Nic se nemusí zapínat: Watcher čte zdroj tak, jak ho hra nebo platforma poskytuje.

## Jak to funguje {#how-it-works}

Minecraft (Java Edition): log, statistiky a soubory hráčů, které hra zapisuje.

Kde (`%APPDATA%\.minecraft\`):

* `logs\latest.log` – log hry, nový při každém spuštění (starý se zabalí do
  datovaného .log.gz). Řádky `[hh:mm:ss] [vlákno/LEVEL]: zpráva`
  (mod loadery píší `[ddMMMyyyy hh:mm:ss.mmm] [vlákno/LEVEL] [logger/]: ...`).
  To, co hráči vidí v chatu, je v něm: připojení a odchody, zprávy o smrti,
  postupy, chat – integrovaný server jednohráčkového světa zapíše tytéž řádky ještě
  jednou, takže řádek opakovaný ve stejné sekundě se počítá jednou. „Setting user: <name>“
  pojmenuje hráče; řádek serveru „<name>[...] logged in with entity id N at (x, y, z)“
  říká, kde se objevil.
* `saves\<world>\stats\<uuid>.json` – obrazovka statistik, zapsaná, když se svět
  ukládá (automatické ukládání každých pár minut a při odchodu): `stats` ->
  `minecraft:custom` (play_time v tickách, mob_kills, \*_one_cm vzdálenosti, jump,
  ...), `minecraft:mined`, `minecraft:crafted`, ... Součty pro svět; čísla
  relace jsou rozdíl oproti tomu, co soubor říkal, když hra začala. Formát: <https://minecraft.wiki/w/Statistics>
* `saves\<world>\playerdata\<uuid>.dat` (a `level.dat` -> Data -> Player
  u hostitele jednohráčkové hry) – NBT komprimované gzipem, zapisované při stejných
  uloženích: `Pos` [x, y, z] jako doubly, `Rotation` [yaw, pitch], `Dimension`
  („minecraft:overworld“; int 0/-1/1 před verzí 1.16). NBT podle
  <https://minecraft.wiki/w/NBT_format> – čte ho tady malá čtečka vlastní výroby.
* `saves\<world>\advancements\<uuid>.json` – pokrok na obrazovce postupů,
  zapisovaný při stejných uloženích.

Souřadnice jsou v blocích, jeden blok je jeden metr, osa y nahoru; x na východ,
z na jih – pravotočivý rámec, kreslí se tak, jak je. Pozice přicházejí jen tehdy,
když se svět ukládá, takže trasa je několik bodů na každé automatické uložení, ne
stopa; dimenze je `session`, takže Nether se nekreslí přes Overworld.

Vše přečtené se uloží celé v surové příloze relace (pravidlo převaděče 3DHeat):
každý řádek logu pod svou úrovní (`INFO`, `WARN`, `ERROR`, ...; řádek bez hranaté
hlavičky, jako výpis zásobníku, jako `untagged`), a každý uložený soubor pod svým
druhem (`stats`, `advancements`, `playerdata`, `level.dat`) – JSON jako text, NBT jako
své bajty. Čísla souboru statistik se dají pochopit jen podle toho, co soubor říkal,
když hra začala, takže i ta první kopie se uloží (`baseline`), a to poprvé, kdy se soubor
změní.

## Pozice a osy {#positions-and-axes}

| | |
|---|---|
| Zaznamenané pozice | ano |
| Osa nahoru | `y` |
| Jednotky | bloky (1 blok = 1 m) |
| Zrcadleno pro prohlížeč | žádné |
| Měřítko jednotek (`scale`: prohlížeč pozice tímto násobí) | 1 |

Tyto údaje se zapíšou do `meta.json` každé relace (`axes`) a, pokud má relace pozice, do zápatí `heat.parquet`, takže prohlížeč 3DHeat otáčí a měřítko řádků nastavuje sám – viz [Data](the-data.md).

## Více hráčů {#multiplayer}

- Označeno jako hraná online (`multiplayer`): **ano**. `games --markdown` to ukazuje jako „povoleno (čte jen to, co hra zveřejňuje)“.
- Druh `log`: čte jen to, co hra nebo platforma vydává (soubory, které hra zapisuje za běhu), takže zaznamenává i v online hře, nejen offline; příznak rozhoduje jen o tom, zda se paměť smí vůbec číst.
- Paměť: tento adaptér ji **nikdy** nečte. Paměť čtou jen adaptéry typu `memory` a nikdy u hry označené jako hraná online – viz [Zdroje a pravidla](sources-and-rules.md).

## Zaznamenané statistiky {#statistics-recorded}

Klíče statistik, které kód tohoto adaptéru nastavuje podle názvu (u každé relace `stats` v `meta.json` a v tabulce `stats` souboru `watcher.sqlite`):

`advancements`, `bad_files`, `bad_lines`, `chat_messages`, `deaths`, `joins`, `others_deaths`, `world`

Klíč ve složených závorkách se doplní za běhu (`score.{team}` je jeden klíč pro každý tým). Klíče, které kód bere z tabulky polí hry nebo z jejích vlastních názvů statistik, v tomto seznamu nejsou; výše v části „Co se zaznamenává“ jsou pojmenovány.

## Úplnost {#completeness}

Watcher se řídí [pravidlem převaděče](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md) 3DHeat: co zdroj obsahuje, se přečte nebo uloží, nikdy se nezahodí. Kromě řádků se každý paket, stránka, řádek nebo odpověď, které adaptér přijme, uloží celý do `heat.raw.parquet` relace (sloupce `time`, `ms`, `type`, `used`, `payload`, `text` a případná pole uložená podle názvu; `used` označuje, co se také stalo řádky) a `selfCheck.completeness` v `meta.json` počítá každý `type` – `lost` je 0.

**Načteno**

- latest.log: jméno hráče (`Setting user`), přihlášení s pozicí, připojení, odchody, smrti se zprávou o smrti, postupy, řádky chatu, zastavení serveru
- stats/<uuid>.json: herní čas, vzdálenost, zabití mobů a hráčů, skoky, způsobené a přijaté poškození, vytěžené bloky, vyrobené předměty – podíl této relace
- playerdata/<uuid>.dat a level.dat (NBT): pozice, dimenze, yaw, pitch, zdraví, úroveň zkušeností

**Uchováno surové**

- každý řádek latest.log celý, `type` = jeho úroveň (`INFO`, `WARN`, `ERROR`, `DEBUG`, `FATAL`) s vláknem loggeru v `thread`, `used`, kde se stal řádkem; řádek bez hranaté hlavičky (výpis zásobníku, banner modu) jako `untagged`
- každý stats/<uuid>.json celý jako text, `type` `stats` (`used`: jeho čísla jsou ve statistikách), s první kopií od začátku hry jako `baseline`
- každý advancements/<uuid>.json celý jako text, `type` `advancements` (každé kritérium a kdy bylo splněno; zatím nejsou převedeny na řádky)
- každý playerdata/<uuid>.dat a level.dat celý jako bajty (NBT gzip), `type` `playerdata` / `level.dat`, `used`, kde dal pozici: inventář, truhla na Enderu, efekty, bod spawnu, herní pravidla, seed světa a čas jsou jen tady
- každý uložený soubor má `world` a `file` (jeho cestu pod `saves`)

**Nedostupné**

- stopa pohybu: hra zapisuje pozici hráče jen tehdy, když se svět ukládá (každých pár minut a při odchodu)
- pozice na serveru, který hostí někdo jiný: jeho soubory světa jsou na serveru, ne tady; čte se jen log
- samotný svět (soubory region .mca, entity, data/\*.dat s mapami a nájezdy): velké a jde o terén, ne o hru
- logy dřívějších relací (logs/\*.log.gz): uloží se, když se hrálo
- Bedrock Edition: nezapisuje takový log ani soubory

**Velikost**: latest.log 0,1–2 MB za hodinu (s mody víc); soubor statistik 5–50 KB a soubor hráče 5–100 KB na jedno automatické uložení, level.dat 1–20 KB – celkem asi 1–5 MB za hodinu; zstd v heat.raw.parquet z textu udělá zhruba desetinu (soubory NBT jsou už zabalené gzipem)

## Ověřeno {#verified}

testováno na syntetických řádcích logu, JSON statistik a souborech NBT sestavených podle zveřejněných formátů; netestováno proti hře

## Zdroj {#source}

[heat3d_watch/adapters/minecraft.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/minecraft.py)

<!-- Generated from the adapter by tools/gen_game_pages.py; change the adapter and run it again rather than editing this page. -->
