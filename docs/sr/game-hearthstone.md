---
title: "Hearthstone (фајлови дневника)"
nav_order: 25
lang: "sr"
source: game-hearthstone.md
source_hash: "e79c19776947"
nav_exclude: true
search_exclude: true
---
# Hearthstone (фајлови дневника) {#hearthstone-log-files}

Док играте Hearthstone, watcher чита фајлове које игра пише и чува шта се дешавало, да бисте то касније погледали као статистику и временску линију.

*Технички подаци: адаптер `hearthstone`, врста [`log`](sources-and-rules.md); ради док је `Hearthstone.exe` покренут и тражи нове податке сваких 0,5 s.*

## Шта се бележи {#what-is-recorded}

- почетак и крај игре, са исходом (побједа, пораз, нерешено), потезима и именом противника
- сваки потез
- сваки ред Power.log-а и осталих дневника цео у heat.raw.parquet
- игре, побједе, порази, нерешено, потези, најдужа игра

## Одакле долазе подаци {#where-it-comes-from}

&lt;install>\Logs\Power.log (или Logs\Hearthstone_\*\Power.log), који се пише чим log.config у %LOCALAPPDATA%\Blizzard\Hearthstone има одјељак [Power], и сваки други \*.log који игра тамо пише

## Како га укључити {#how-to-switch-it-on}

`python -m heat3d_watch setup hearthstone --apply` додаје запис о [Power] дневнику у %LOCALAPPDATA%\Blizzard\Hearthstone\log.config (резервна копија се чува); поново покрените игру

Команду укуцајте у терминалу отвореном у фасцикли watcher-а (видите [Пре почетка](before-you-start.md)). Ако не успе, последњи ред каже зашто; [Инсталација и покретање](installing-and-running.md) објашњава најчешће узроке.

`python -m heat3d_watch setup hearthstone` исписује фајлове које би променио; `python -m heat3d_watch setup hearthstone --apply` их мења, а оригинал чува као `<file>.heat3d-backup` (видите [Команде](commands.md#setup)). За сваку измјену исписује `hearthstone: changed: ...`, или `hearthstone: nothing to change` када је већ укључено.

## Како ради {#how-it-works}

Hearthstone: Power.log игре, који игра пише чим log.config то затражи.

Hearthstone чита `%LOCALAPPDATA%\Blizzard\Hearthstone\log.config` при покретању; одјељак `[Power]` са `LogLevel=1` и `FilePrinting=true` наводи га да пише промене стања сваке игре у `<install>\Logs\Power.log` (новији клијенти стављају дневнике сваког покретања у фасциклу за себе, `Logs\Hearthstone_<date>\`). Ово је документовано дебаг снимање које алатке за праћење шпила користе још од 2014. (подешавање Hearthstone Deck Tracker-а пише исти одјељак). `setup()` додаје одјељак, уз резервну копију фајла каквог је био; игра мора да се поново покрене да би га прочитала.

Користе се ови редови, сви из `GameState.DebugPrintPower()` (редови `PowerTaskList` се понављају и прескачу се):

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

Своја страна играча је она чије су почетне руке именоване карте (карте противника су скривене); иначе је то страна која није AI (налог 0) или „UNKNOWN HUMAN PLAYER”. Редови носе само доба дана; датум је данашњи. Нема положаја.

Сваки ред Power.log-а чува се цео у сировом прилогу сесије (правило конвертера у 3DHeat-у), укључујући понављања `PowerTaskList`, опције, изборе и измјене ентитета: `type` је метода која га је написала (`GameState.DebugPrintPower`, `PowerTaskList.DebugPrintPower`, `GameState.DebugPrintOptions`, ...). Сваки други дневник који игра пише поред њега - `LoadingScreen.log`, `Decks.log`, `Zone.log`, `Arena.log`, ..., сваки присутан кад log.config то затражи (алатке за праћење шпилова га често укључују) - прати се на исти начин и чува се са својим именом у `log`.

## Положаји и осе {#positions-and-axes}

| | |
|---|---|
| Положаји се бележе | не |
| Оса горе | `y` |
| Јединице | положаји се не бележе |
| Огледање за прегледач | нема |
| Размера јединица (`scale`: прегледач помножи положаје с њом) | 1 |

Ово иде у `meta.json` сваке сесије (`axes`) и, када сесија има положаје, у подножје `heat.parquet`, па 3DHeat прегледач сам окреће и размењује редове - видите [Подаци](the-data.md).

## Више играча {#multiplayer}

- Означено као игра на мрежи (`multiplayer`): **да**. `games --markdown` то приказује као „дозвољено (чита само оно што игра објављује)”.
- Врста `log`: чита само оно што игра или платформа даје (фајлови које игра пише док ради), па снима и у мрежној игри и ван ње; ознака одлучује само о томе смије ли се икад читати меморија.
- Меморија: овај адаптер је **никада** не чита. Само адаптери врсте `memory` читају меморију, и никад за игру означену као мрежну - видите [Извори и правила](sources-and-rules.md).

## Забиљежена статистика {#statistics-recorded}

Кључеви статистике које код овог адаптера поставља по имену (свака `stats` сесија у `meta.json` и табела `stats` у `watcher.sqlite`):

`bad_lines`, `games`, `longest_game_turns`, `losses`, `ties`, `turns`, `wins`

Кључ у витичастим заградама се допуњује у време рада (`score.{team}` је један кључ по тиму). Кључеви које код узима из табеле поља игре или из имена статистике саме игре нису на овом списку; „Шта се бележи” горе их именује.

## Потпуност {#completeness}

Watcher прати [правило конвертера](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md) из 3DHeat-а: оно што извор садржи се чита или чува, никад се не одбацује. Осим редова, сваки пакет, страница, ред или одговор које адаптер прими чува се цео у `heat.raw.parquet` сесије (колоне `time`, `ms`, `type`, `used`, `payload`, `text`, па свако поље које се чува по имену; `used` означава оно што је постало редови), а `selfCheck.completeness` у `meta.json` броји сваки `type` - `lost` је 0.

**Чита се**

- `CREATE_GAME`, играчи (ентитет, ид играча, налог; налог 0 је AI) и њихова имена (`DebugPrintGame`)
- чија је страна играчева, по именованим картама из почетне руке
- `TAG_CHANGE` за TURN, PLAYSTATE (won, lost, tied) и STATE COMPLETE: потези, исход, противник

**Чува се сирово**

- сваки ред Power.log-а цео, `type` = метода која га је написала (`GameState.DebugPrintPower`, `PowerTaskList.DebugPrintPower`, `GameState.DebugPrintGame`, `GameState.DebugPrintOptions`, `GameState.SendChoices`, `GameState.DebugPrintEntityChoices`, `PowerProcessor.DoTaskListForCard`, ...), `log` `Power`, `used` тамо где је постао ред: свака одиграна, извучена и откривена карта, свака измјена ознаке, напад, опција и избор су ту, још нису у редовима
- сваки ред осталих дневника у истој фасцикли (`LoadingScreen`, `Decks`, `Zone`, `Arena`, `Achievements`, `FullScreenFX`, ... - шта год log.config укључи), исти `type`, са именом дневника у `log`
- ред без нивоа и времена дана као `untimed`, ред без методе као `untagged`

**Није доступно**

- положаји: карташка игра их нема
- скривене карте противника: дневник именује карту тек кад се открије
- дневници које log.config не укључује: `setup` тражи само [Power]; остали дневници стижу кад их укључи друга алатка (алатка за праћење шпила)
- дневници претходних покретања: свако покретање пише нову фасциклу; они старији од овог покретања игре се не читају поново

**Величина**: Power.log са Verbose је око 1-5 MB по игри, 10-40 MB по сату игре; остали дневници додају мало; zstd у heat.raw.parquet га смањи на око десетину или мање (редови се много понављају)

## Провјерено {#verified}

тестирано на синтетичким редовима Power.log-а у игрином формату; није тестирано са игром

## Извор {#source}

[heat3d_watch/adapters/hearthstone.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/hearthstone.py)

<!-- Generated from the adapter by tools/gen_game_pages.py; change the adapter and run it again rather than editing this page. -->
