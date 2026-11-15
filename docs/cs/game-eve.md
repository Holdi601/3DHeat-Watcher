---
title: "EVE Online (herní logy)"
nav_order: 20
lang: "cs"
source: game-eve.md
source_hash: "a5ab6c312c86"
nav_exclude: true
search_exclude: true
---
# EVE Online (herní logy) {#eve-online-log-files}

Když hrajete EVE Online, Watcher čte soubory, které hra zapisuje, a uloží, co se stalo, abyste se na to mohli později podívat jako na statistiky a časovou osu.

*Technické podrobnosti: adaptér `eve`, druh [`log`](sources-and-rules.md); běží, dokud běží `exefile.exe`, a hledá nová data každých 0,5 s.*

## Co se zaznamenává {#what-is-recorded}

- způsobené a přijaté poškození s druhou lodí, pilotem, zkratkou korporace, zbraní a kvalitou zásahu
- minutí způsobená a přijatá
- vyplacené odměny za NPC s ISK
- skoky mezi systémy
- každý řádek herního logu a chatu celý v heat.raw.parquet
- způsobené a přijaté poškození, zásahy, minutí, zabití za odměnu a ISK, skoky

## Odkud to pochází {#where-it-comes-from}

%USERPROFILE%\Documents\EVE\logs\Gamelogs\\\*.txt a Chatlogs\\\*.txt vedle nich (každý soubor zapsaný od spuštění klienta)

## Jak to zapnout {#how-to-switch-it-on}

Nic se nemusí zapínat: Watcher čte zdroj tak, jak ho hra nebo platforma poskytuje.

## Jak to funguje {#how-it-works}

EVE Online: herní logy klienta, `Documents\EVE\logs\Gamelogs\*.txt`.

Klient zapisuje jeden soubor na postavu a na každé přihlášení,
`<yyyymmdd>_<hhmmss>[_<id postavy>].txt`; zapisování do souboru je ve výchozím stavu zapnuté. Když běží
vedle sebe více klientů, každý zapisuje svůj vlastní, takže se sleduje každý soubor
zapsaný od spuštění hry. Hlavička a řádky (čas EVE je UTC):

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

(řádek combat je v souboru jeden řádek). Formátovací značky se před porovnáním odstraní.
Soubor byl v průběhu let v UTF-8 i UTF-16; čtou se oba.
Formát CCP nedokumentuje; je to prostý textový log klienta, čtený tak, jak ho čtou
komunitní nástroje pro boj (např. <https://docs.rs/crate/eve-log-parser>).
Žádné pozice.

Vedle něj `Documents\EVE\logs\Chatlogs\<kanál>_<yyyymmdd>_<hhmmss>[_<id>].txt`:
jeden soubor na chatovací kanál a na přihlášení (když je logování chatu zapnuté, což je výchozí nastavení klienta),
UTF-16, hlavička s názvem kanálu a posluchačem, pak
`[ yyyy.mm.dd hh:mm:ss ] Odesílatel > zpráva`.

Každý řádek obou se ukládá celý do surového doprovodného souboru relace (pravidlo
převodníků 3DHeat): řádek herního logu pod svým kanálem v hranatých závorkách (`combat`,
`notify`, `bounty`, `None`, ...), řádek chatu jako `chat` se svým kanálem, řádky hlavičky
jako `gamelog header` / `chatlog header`.

## Pozice a osy {#positions-and-axes}

| | |
|---|---|
| Zaznamenané pozice | ne |
| Osa nahoru | `y` |
| Jednotky | žádné pozice se nezaznamenávají |
| Zrcadleno pro prohlížeč | žádné |
| Měřítko jednotek (`scale`: prohlížeč pozice tímto násobí) | 1 |

Tyto hodnoty se zapíší do `meta.json` (`axes`) každé relace a, pokud relace obsahuje pozice, do zápatí `heat.parquet`, takže prohlížeč 3DHeat otáčí a měřítko řádků upravuje sám - viz [Data](the-data.md).

## Více hráčů {#multiplayer}

- Označeno jako hraná online (`multiplayer`): **ano**. `games --markdown` to ukazuje jako „povoleno (čte jen to, co hra zveřejňuje)“.
- Druh `log`: čte jen to, co hra nebo platforma vydává (soubory, které hra zapisuje za běhu), takže zaznamenává i v online hře i offline; příznak rozhoduje jen o tom, zda se paměť smí vůbec číst.
- Paměť: tento adaptér ji **nikdy** nečte. Paměť čtou jen adaptéry `memory`, a nikdy u hry označené jako hraná online - viz [Zdroje a pravidla](sources-and-rules.md).

## Zaznamenané statistiky {#statistics-recorded}

Klíče statistik, které kód tohoto adaptéru nastavuje podle názvu (`stats` každé relace v `meta.json` a tabulka `stats` v `watcher.sqlite`):

`bad_lines`, `bounty_isk`, `bounty_kills`, `damage_dealt`, `damage_received`, `hits_dealt`, `hits_received`, `jumps`, `misses_dealt`, `misses_received`

Klíč ve složených závorkách se doplní za běhu (`score.{team}` je jeden klíč pro každý tým). Klíče, které kód bere z tabulky polí hry nebo z jejích vlastních názvů statistik, v tomto seznamu nejsou; výše v „Co se zaznamenává“ jsou uvedeny.

## Úplnost {#completeness}

Watcher se řídí [pravidlem převodníků](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md): co zdroj obsahuje, se přečte nebo uloží, nikdy se nezahodí. Kromě řádků se každý paket, stránka, řádek nebo odpověď, kterou adaptér přijme, uloží celý do `heat.raw.parquet` relace (sloupce `time`, `ms`, `type`, `used`, `payload`, `text` a případná pole uložená podle názvu; `used` označuje, co se také stalo řádky), a `selfCheck.completeness` v `meta.json` počítá každý `type` - `lost` je 0.

**Načteno**

- zásahy `(combat)` způsobené a přijaté z gamelogu (částka, druhý pilot, zkratka korporace, loď, zbraň, kvalita zásahu) a minutí oběma směry
- výplaty `(bounty)` s ISK a řádky `Jumping from A to B`
- hodnota Listener z hlavičky gamelogu: čí log to je

**Uchováno surové**

- každý řádek gamelogu celý, `type` = jeho kanál v hranatých závorkách (`combat`, `notify`, `info`, `bounty`, `mining`, `question`, `hint`, `warning`, `None`, ...), s `file` a `listener`; `used` tam, kde se stal řádkem; řádky hlavičky jako `gamelog header`
- každý řádek chatlogu celý (Local, korporace, flotila, soukromé kanály, oznámení `EVE System`, například změna kanálu Local při skoku), `type` `chat`, s `channel`, `listener` a `file`; řádky hlavičky jako `chatlog header`. Zatím nejsou převedeny na řádky
- formátovací značky (`<color>`, `<b>`, `<font>`) zůstávají v surovém textu; řádky je mají odstraněné

**Nedostupné**

- pozice: klient je do svých logů nezapisuje
- souboje jiných pilotů: gamelog je vlastní záznam posluchače
- logy předchozích přihlášení: každé přihlášení zapíše nové soubory; ty starší než tento běh klienta se znovu nečtou
- chat, když hráč má v nastavení klienta vypnuté logování chatu
- vlastní cache a soubory nastavení klienta: nejsou logy a nejsou zdokumentované

**Velikost**: gamelog je 0,1-2 MB za hodinu (většina v boji); chatlogy závisí na otevřených kanálech - živý Local nebo flotila 0,5-3 MB za hodinu; zstd v heat.raw.parquet ho zmenší asi na desetinu

## Ověřeno {#verified}

testováno na syntetických řádcích gamelogu v formátu, který zveřejňují komunitní parsery; zatím neotestováno ve hře

## Zdroj {#source}

[heat3d_watch/adapters/eve.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/eve.py)

<!-- Vygenerováno z adaptéru nástrojem tools/gen_game_pages.py; změňte adaptér a spusťte generování znovu, místo úpravy této stránky. -->
