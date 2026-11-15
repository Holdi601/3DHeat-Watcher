---
title: "Path of Exile (herní logy)"
nav_order: 36
lang: "cs"
source: game-poe.md
source_hash: "9facfd5a1551"
nav_exclude: true
search_exclude: true
---
# Path of Exile (herní logy) {#path-of-exile-log-files}

Když hrajete Path of Exile, Watcher čte soubory, které hra zapisuje, a uloží, co se stalo, abyste se na to mohli později podívat jako na statistiky a časovou osu.

*Technické podrobnosti: adaptér `poe`, druh [`log`](sources-and-rules.md); běží, dokud běží `PathOfExile.exe`, `PathOfExile_x64.exe`, `PathOfExileSteam.exe`, `PathOfExile_x64Steam.exe`, `PathOfExileEGS.exe`, `PathOfExile_x64EGS.exe`, `PathOfExile_KG.exe` nebo `PathOfExile_x64_KG.exe`, a hledá nová data každých 0,5 s.*

## Co se zaznamenává {#what-is-recorded}

- zóny, do kterých jste vstoupili, s úrovní oblasti, ID oblasti a jejím semínkem
- zvýšení úrovně s třídou a úrovní
- smrti („has been slain“)
- hráči, kteří do oblasti vstoupí a z ní odejdou, šepoty dovnitř a ven, žádosti o obchod, přijaté obchody
- každý řádek Client.txt z této relace celý v heat.raw.parquet
- smrti, získané úrovně, nejvyšší úroveň, navštívené zóny, různé zóny, šepoty, žádosti o obchod, obchody

## Odkud to pochází {#where-it-comes-from}

&lt;instalace>\logs\Client.txt hry Path of Exile nebo Path of Exile 2 (sleduje se; instalační složka je ta spuštěného programu)

## Jak to zapnout {#how-to-switch-it-on}

Nic se nemusí zapínat: Watcher čte zdroj tak, jak ho hra nebo platforma poskytuje.

## Jak to funguje {#how-it-works}

Path of Exile a Path of Exile 2: log klienta, `<instalace>\logs\Client.txt`.

Obě hry připisují do jednoho Client.txt ve své instalační složce, dokud jsou nainstalované
(roste napříč spuštěními). Řádky vypadají takto

```text
2024/01/01 12:00:00 123456789 cff94598 [INFO Client 1234] : You have entered Lioneye's Watch.
2024/01/01 12:00:00 123456789 cff94598 [DEBUG Client 1234] Generating level 2 area "1_1_2" with seed 1
2024/01/01 12:00:00 123456789 cff94598 [INFO Client 1234] : Name (Witch) is now level 2
2024/01/01 12:00:00 123456789 cff94598 [INFO Client 1234] : Name has been slain.
2024/01/01 12:00:00 123456789 cff94598 [INFO Client 1234] @From Name: Hi, I would like to buy your ...
```

- místní čas, čítač milisekund, hash, úroveň a vlákno, pak to, co ukazuje
  okno chatu. Zprávy jsou z anglického klienta; klient v jiném jazyce je zapisuje
  přeložené a zde se nečtou. Nic nedává pozici. Formát Grinding Gear Games
  nedokumentuje; je to prostý textový log hry, jak ho už roky čtou komunitní nástroje
  (obchodní pomocníci, průvodci úrovněmi) - např. <https://github.com/klayveR/poe-log-monitor> (MIT) pro
  seznam událostí.

Instalační složka je složka spuštěného programu; bez něj se hledají knihovny Steamu
a výchozí složka samostatného klienta.

Každý řádek této relace se ukládá celý do surového doprovodného souboru (pravidlo
převodníků 3DHeat), ať už pro zde něco znamená, nebo ne: `type` je úroveň a logger v jeho
závorkách (`INFO Client`, `DEBUG Client`, `WARN Client`, ...), řádek s časovým razítkem bez
závorek je `untagged`, řádek bez časového razítka `untimed`.

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

`bad_lines`, `character_class`, `deaths`, `level`, `levels_gained`, `trade_requests_received`, `trade_requests_sent`, `trades`, `whispers`, `zones_distinct`, `zones_entered`

Klíč ve složených závorkách se doplní za běhu (`score.{team}` je jeden klíč pro každý tým). Klíče, které kód bere z tabulky polí hry nebo z jejích vlastních názvů statistik, v tomto seznamu nejsou; výše v „Co se zaznamenává“ jsou uvedeny.

## Úplnost {#completeness}

Watcher se řídí [pravidlem převodníků](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md): co zdroj obsahuje, se přečte nebo uloží, nikdy se nezahodí. Kromě řádků se každý paket, stránka, řádek nebo odpověď, kterou adaptér přijme, uloží celý do `heat.raw.parquet` relace (sloupce `time`, `ms`, `type`, `used`, `payload`, `text` a případná pole uložená podle názvu; `used` označuje, co se také stalo řádky), a `selfCheck.completeness` v `meta.json` počítá každý `type` - `lost` je 0.

**Načteno**

- `You have entered <zóna>`, s úrovní oblasti, ID oblasti a semínkem z řádku `Generating level` těsně před ním
- `<jméno> (<třída>) is now level <n>`, `<jméno> has been slain`, hráči, kteří do oblasti vstoupí a odejdou, šepoty dovnitř a ven (s tím, zda jde o žádost o obchod), přijaté a zrušené obchody

**Uchováno surové**

- každý řádek této relace celý, `type` = úroveň a logger v jeho závorkách (`INFO Client`, `DEBUG Client`, `WARN Client`, `CRIT Client`, ...), `used` tam, kde se stal řádkem: globální, obchodní, party a guild chat, `Connecting to instance server`, hlášky AFK a DND, odpovědi na chatové příkazy jako `/played` a `/deaths`, načítací a motorové řádky klienta - uloženo, zatím ne převedeno na řádky
- řádek s časovým razítkem bez závorek (`***** LOG FILE OPENING *****`) jako `untagged`, řádek bez časového razítka jako `untimed`

**Nedostupné**

- pozice: nic v logu žádnou nedává
- co píše klient v jiném jazyce: řádky se ukládají, ale na řádky se převádějí jen anglické zprávy
- řádky předchozích spuštění: Client.txt roste napříč spuštěními; řádky s časovým razítkem před tímto během hry zůstanou nedotčené (byly uloženy, když se hrálo)
- zabití, poškození, kořist a strom pasivních schopností: hra je nezaznamenává

**Velikost**: Client.txt roste asi o 0,3-3 MB za hodinu (většina z řádků DEBUG při načítání oblastí, víc při rušném obchodním chatu); zstd v heat.raw.parquet ho zmenší asi na desetinu

## Ověřeno {#verified}

testováno na syntetických řádcích Client.txt v herním formátu; zatím neotestováno ve hře

## Zdroj {#source}

[heat3d_watch/adapters/poe.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/poe.py)

<!-- Vygenerováno z adaptéru nástrojem tools/gen_game_pages.py; změňte adaptér a spusťte generování znovu, místo úpravy této stránky. -->
