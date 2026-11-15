---
title: "Hearthstone (herní logy)"
nav_order: 25
lang: "cs"
source: game-hearthstone.md
source_hash: "e79c19776947"
nav_exclude: true
search_exclude: true
---
# Hearthstone (herní logy) {#hearthstone-log-files}

Když hrajete Hearthstone, Watcher čte soubory, které hra zapisuje, a uloží, co se stalo, abyste se na to mohli později podívat jako na statistiky a časovou osu.

*Technické podrobnosti: adaptér `hearthstone`, druh [`log`](sources-and-rules.md); běží, dokud běží `Hearthstone.exe`, a hledá nová data každých 0,5 s.*

## Co se zaznamenává {#what-is-recorded}

- začátek a konec hry s výsledkem (výhra, prohra, remíza), počtem tahů a jménem soupeře
- každý tah
- každý řádek souboru Power.log a dalších logů celý v heat.raw.parquet
- hry, výhry, prohry, remízy, tahy, nejdelší hra

## Odkud to pochází {#where-it-comes-from}

&lt;instalace>\Logs\Power.log (nebo Logs\Hearthstone_\*\Power.log), zapisovaný, jakmile %LOCALAPPDATA%\Blizzard\Hearthstone\log.config obsahuje sekci [Power], a každý další \*.log, který hra tam zapisuje

## Jak to zapnout {#how-to-switch-it-on}

`python -m heat3d_watch setup hearthstone --apply` přidá logování [Power] do %LOCALAPPDATA%\Blizzard\Hearthstone\log.config (záloha se uchová); hru restartujte

Příkaz zadejte v terminálu otevřeném ve složce Watcheru (viz [Než začnete](before-you-start.md)). Když selže, poslední řádek řekne proč; [Instalace a spuštění](installing-and-running.md) popisuje obvyklé příčiny.

`python -m heat3d_watch setup hearthstone` vypíše soubory, které by změnil; `python -m heat3d_watch setup hearthstone --apply` je skutečně změní a původní uloží jako `<soubor>.heat3d-backup` (viz [Příkazy](commands.md#setup)). Pro každou změnu vypíše `hearthstone: changed: ...`, nebo `hearthstone: nothing to change`, když je už zapnuto.

## Jak to funguje {#how-it-works}

Hearthstone: herní soubor Power.log, který hra zapisuje, jakmile o to log.config požádá.

Hearthstone při startu čte `%LOCALAPPDATA%\Blizzard\Hearthstone\log.config`;
sekce `[Power]` s `LogLevel=1` a `FilePrinting=true` způsobí, že zapisuje
každou změnu stavu hry do `<instalace>\Logs\Power.log` (novější klienty ukládají
logy každého spuštění do vlastní složky `Logs\Hearthstone_<datum>\`). Toto je
dokumentované ladicí logování, které deck trackery zapínají od roku 2014
(nastavení Hearthstone Deck Tracker zapisuje tutéž sekci). `setup()` sekci přidá,
se zálohou souboru v podobě, v jaké byl; hra ji čte až po restartu.

Použité řádky, všechny z `GameState.DebugPrintPower()` (řádky `PowerTaskList`
je opakují a přeskakují se):

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

Hráčova strana je ta, jejíž počáteční ruka má pojmenované karty
(karty soupeře jsou skryté), jinak strana, která není AI (účet 0), nebo
„UNKNOWN HUMAN PLAYER“. Řádky nesou jen denní čas; datum je dnešní.
Žádné pozice.

Každý řádek souboru Power.log se ukládá celý do surového doprovodného souboru relace (pravidlo
převodníků 3DHeat), včetně opakování `PowerTaskList`, voleb, výběrů a aktualizací
entit: `type` je metoda, která ho zapsala (`GameState.DebugPrintPower`,
`PowerTaskList.DebugPrintPower`, `GameState.DebugPrintOptions`, ...). Každý další
log, který hra vedle něj zapisuje - `LoadingScreen.log`, `Decks.log`, `Zone.log`,
`Arena.log`, ..., každý tam, pokud o to log.config požádá (deck trackery to
často dělají) - se sleduje stejně a ukládá se pod svým názvem v `log`.

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

`bad_lines`, `games`, `longest_game_turns`, `losses`, `ties`, `turns`, `wins`

Klíč ve složených závorkách se doplní za běhu (`score.{team}` je jeden klíč pro každý tým). Klíče, které kód bere z tabulky polí hry nebo z jejích vlastních názvů statistik, v tomto seznamu nejsou; výše v „Co se zaznamenává“ jsou uvedeny.

## Úplnost {#completeness}

Watcher se řídí [pravidlem převodníků](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md): co zdroj obsahuje, se přečte nebo uloží, nikdy se nezahodí. Kromě řádků se každý paket, stránka, řádek nebo odpověď, kterou adaptér přijme, uloží celý do `heat.raw.parquet` relace (sloupce `time`, `ms`, `type`, `used`, `payload`, `text` a případná pole uložená podle názvu; `used` označuje, co se také stalo řádky), a `selfCheck.completeness` v `meta.json` počítá každý `type` - `lost` je 0.

**Načteno**

- `CREATE_GAME`, hráči (entita, ID hráče, účet; účet 0 je AI) a jejich jména (`DebugPrintGame`)
- čí strana je hráčova, podle pojmenovaných karet počáteční ruky
- `TAG_CHANGE` u TURN, PLAYSTATE (won, lost, tied) a STATE COMPLETE: tahy, výsledek, soupeř

**Uchováno surové**

- každý řádek Power.log celý, `type` = metoda, která ho zapsala (`GameState.DebugPrintPower`, `PowerTaskList.DebugPrintPower`, `GameState.DebugPrintGame`, `GameState.DebugPrintOptions`, `GameState.SendChoices`, `GameState.DebugPrintEntityChoices`, `PowerProcessor.DoTaskListForCard`, ...), `log` `Power`, `used` tam, kde se stal řádkem: každá zahraná, dobytá a odhalená karta, každá změna značky, útok, volba a výběr jsou tu, zatím ne v řádcích
- každý řádek ostatních logů ve stejné složce (`LoadingScreen`, `Decks`, `Zone`, `Arena`, `Achievements`, `FullScreenFX`, ... - cokoli, co log.config zapne), stejné `type`, s názvem logu v `log`
- řádek bez úrovně a denního času jako `untimed`, řádek bez metody jako `untagged`

**Nedostupné**

- pozice: karetní hra žádné nemá
- skryté karty soupeře: log uvádí kartu jen tehdy, je-li odhalená
- logy, které log.config nezapíná: `setup` žádá jen [Power]; ostatní logy přijdou, když je zapne jiný nástroj (deck tracker)
- logy předchozích spuštění: každé spuštění zapíše novou složku; ty starší než tento běh hry se znovu nečtou

**Velikost**: Power.log s Verbose má asi 1-5 MB na hru, 10-40 MB za hodinu hraní; ostatní logy přidají málo; zstd v heat.raw.parquet ho zmenší asi na desetinu nebo méně (řádky se hodně opakují)

## Ověřeno {#verified}

testováno na syntetických řádcích Power.log v herním formátu; zatím neotestováno ve hře

## Zdroj {#source}

[heat3d_watch/adapters/hearthstone.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/hearthstone.py)

<!-- Vygenerováno z adaptéru nástrojem tools/gen_game_pages.py; změňte adaptér a spusťte generování znovu, místo úpravy této stránky. -->
