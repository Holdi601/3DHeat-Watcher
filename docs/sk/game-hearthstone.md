---
title: "Hearthstone (logy)"
nav_order: 25
lang: "sk"
source: game-hearthstone.md
source_hash: "e79c19776947"
nav_exclude: true
search_exclude: true
---
# Hearthstone (logy) {#hearthstone-log-files}

Počas hry Hearthstone watcher číta súbory, ktoré hra zapisuje, a ukladá, čo sa stalo, aby ste sa na to neskôr mohli pozrieť ako na štatistiky a časovú os.

*Technické údaje: adaptér `hearthstone`, typ [`log`](sources-and-rules.md); beží, kým beží `Hearthstone.exe`, a hľadá nové dáta každých 0,5 s.*

## Čo sa zaznamenáva {#what-is-recorded}

- začiatok a koniec hry s výsledkom (výhra, prehra, remíza), počtom ťahov a menom súpera
- každý ťah
- každý riadok Power.log a ostatných logov celý v heat.raw.parquet
- hry, výhry, prehry, remízy, ťahy, najdlhšia hra

## Odkiaľ to berie {#where-it-comes-from}

&lt;inštalácia>\Logs\Power.log (alebo Logs\Hearthstone_\*\Power.log), zapísaný, keď %LOCALAPPDATA%\Blizzard\Hearthstone\log.config obsahuje sekciu [Power], a každý ďalší \*.log, ktorý hra tam zapisuje

## Ako to zapnúť {#how-to-switch-it-on}

`python -m heat3d_watch setup hearthstone --apply` pridá logovanie [Power] do %LOCALAPPDATA%\Blizzard\Hearthstone\log.config (záloha sa ponechá); reštartujte hru

Príkaz napíšte do terminálu otvoreného v priečinku watchera (pozrite [Pred začiatkom](before-you-start.md)). Ak zlyhá, posledný riadok povie prečo; [Inštalácia a spustenie](installing-and-running.md) popisuje obvyklé príčiny.

`python -m heat3d_watch setup hearthstone` vypíše, ktoré súbory by zmenil; `python -m heat3d_watch setup hearthstone --apply` ich zmení a pôvodný súbor ponechá ako `<file>.heat3d-backup` (pozrite [Príkazy](commands.md#setup)). Pri každej zmene vypíše `hearthstone: changed: ...`, alebo `hearthstone: nothing to change`, ak je už zapnuté.

## Ako to funguje {#how-it-works}

Hearthstone: Power.log hry, ktorý sa zapisuje, keď o to `log.config` požiada.

Hearthstone číta `%LOCALAPPDATA%\Blizzard\Hearthstone\log.config` pri spustení;
sekcia `[Power]` s `LogLevel=1` a `FilePrinting=true` spôsobí, že zapisuje
každú zmenu stavu hry do `<inštalácia>\Logs\Power.log` (novšie klienty dávajú logy každého spustenia do vlastného priečinka, `Logs\Hearthstone_<dátum>\`). Toto je zdokumentované ladiace logovanie, ktoré používajú sledovače balíčkov od roku 2014 (nastavenie Hearthstone Deck Tracker zapisuje rovnakú sekciu). `setup()` pridá sekciu so zálohou súboru v pôvodnom stave; hra potrebuje reštart, aby ju načítala.

Použité riadky, všetky z `GameState.DebugPrintPower()` (riadky `PowerTaskList` ich opakujú a preskakujú sa):

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

Vlastná strana hráča je tá, ktorej štartovacia ruka má pomenované karty (karty súpera sú skryté), inak strana, ktorá nie je AI (účet 0) ani „UNKNOWN HUMAN PLAYER“. Riadky nesú len čas dňa; dátum je dnešný.
Žiadne polohy.

Každý riadok Power.log sa uchová celý v surovom sprievodnom súbore relácie (pravidlo konvertorov 3DHeat), vrátane opakovaní `PowerTaskList`, možností, volieb a aktualizácií entít: `type` je metóda, ktorá ho zapísala (`GameState.DebugPrintPower`, `PowerTaskList.DebugPrintPower`, `GameState.DebugPrintOptions`, ...). Každý iný log, ktorý hra vedľa zapisuje – `LoadingScreen.log`, `Decks.log`, `Zone.log`, `Arena.log`, ... – sleduje sa rovnako, keď ho log.config zapne (sledovače balíčkov to často robia), a uchová sa s názvom v `log`.

## Polohy a osi {#positions-and-axes}

| | |
|---|---|
| Zaznamenané polohy | nie |
| Os nahor | `y` |
| Jednotky | polohy sa nezaznamenávajú |
| Zrkadlenie pre prehliadač | žiadne |
| Mierka jednotiek (`scale`: prehliadač polohy touto hodnotou násobí) | 1 |

Tieto údaje idú do `meta.json` každej relácie (`axes`) a, ak má relácia polohy, do päty súboru `heat.parquet`, takže 3DHeat prehliadač si riadky sám otočí a zmení ich mierku – pozrite [Dáta](the-data.md).

## Viachráčová hra {#multiplayer}

- Označené ako hrané online (`multiplayer`): **áno**. `games --markdown` to zobrazí ako „povolené (číta len to, čo hra zverejňuje)“.
- Typ `log`: číta len to, čo hra alebo platforma vydáva (súbory, ktoré hra zapisuje počas behu), takže zaznamenáva aj v online hre, nielen offline; príznak rozhoduje len o tom, či sa pamäť smie čítať.
- Pamäť: adaptér ju **nikdy** nečíta. Pamäť čítajú len adaptéry typu `memory` a nikdy pre hru označenú ako hranú online – pozrite [Zdroje a pravidlá](sources-and-rules.md).

## Zaznamenané štatistiky {#statistics-recorded}

Kľúče štatistík, ktoré kód tohto adaptéra nastavuje podľa mena (štatistiky každej relácie `stats` v `meta.json` a tabuľka `stats` v `watcher.sqlite`):

`bad_lines`, `games`, `longest_game_turns`, `losses`, `ties`, `turns`, `wins`

Kľúč v zložených zátvorkách sa dopĺňa za behu (`score.{team}` je jeden kľúč na tím). Kľúče, ktoré kód berie z tabuľky polí hry alebo z názvov štatistík hry, v tomto zozname nie sú; „Čo sa zaznamenáva“ vyššie ich pomenúva.

## Úplnosť {#completeness}

Watcher sa riadi [pravidlom konvertorov](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md) 3DHeat: to, čo zdroj obsahuje, sa číta alebo uchováva, nikdy sa nezahadzuje. Okrem riadkov sa každý paket, stránka, riadok alebo odpoveď, ktorú adaptér dostane, uchová celá v `heat.raw.parquet` relácie (stĺpce `time`, `ms`, `type`, `used`, `payload`, `text` a ďalšie polia, ktoré sa uchovávajú podľa mena; `used` označuje to, čo sa stalo aj riadkami), a `selfCheck.completeness` v `meta.json` počíta každý `type` – `lost` je 0.

**Čítané**

- `CREATE_GAME`, hráči (entita, ID hráča, účet; účet 0 je AI) a ich mená (`DebugPrintGame`)
- ktorá strana je hráčova, podľa pomenovaných kariet štartovacej ruky
- `TAG_CHANGE` TURN, PLAYSTATE (won, lost, tied) a STATE COMPLETE: ťahy, výsledok, súper

**Uchované surové**

- každý riadok Power.log celý, `type` = metóda, ktorá ho zapísala (`GameState.DebugPrintPower`, `PowerTaskList.DebugPrintPower`, `GameState.DebugPrintGame`, `GameState.DebugPrintOptions`, `GameState.SendChoices`, `GameState.DebugPrintEntityChoices`, `PowerProcessor.DoTaskListForCard`, ...), `log` `Power`, `used` tam, kde sa stal riadkom: každá zahraná, potiahnutá a odhalená karta, každá zmena značky, útok, možnosť a voľba sú tu, zatiaľ nie v riadkoch
- každý riadok ostatných logov v rovnakom priečinku (`LoadingScreen`, `Decks`, `Zone`, `Arena`, `Achievements`, `FullScreenFX`, ... – čokoľvek, čo log.config zapne), rovnaké `type`, s názvom logu v `log`
- riadok bez úrovne a času dňa ako `untimed`, riadok bez metódy ako `untagged`

**Nedostupné**

- polohy: karetná hra žiadne nemá
- skryté karty súpera: log pomenuje kartu až vtedy, keď sa odhalí
- logy, ktoré log.config nezapína: `setup` žiada len [Power]; ostatné logy prídu vtedy, keď ich zapne iný nástroj (sledovač balíčkov)
- logy skorších spustení: každé spustenie zapíše nový priečinok; tie staršie ako toto spustenie hry sa znova nečítajú

**Veľkosť**: Power.log s Verbose je približne 1 až 5 MB za hru, 10 až 40 MB za hodinu hry; ostatné logy pridajú málo; zstd v heat.raw.parquet ich zmenší na desatinu alebo menej (riadky sa veľmi opakujú)

## Overené {#verified}

testované na syntetických riadkoch Power.log v hernom formáte; neotestované proti hre

## Zdroj {#source}

[heat3d_watch/adapters/hearthstone.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/hearthstone.py)

<!-- Generované z adaptéra nástrojom tools/gen_game_pages.py; zmeňte adaptér a spustite to znova, namiesto úpravy tejto stránky. -->
