---
title: "Hearthstone (лог-датотеки)"
nav_order: 25
lang: "mk"
source: game-hearthstone.md
source_hash: "e79c19776947"
nav_exclude: true
search_exclude: true
---
# Hearthstone (лог-датотеки) {#hearthstone-log-files}

Додека играте Hearthstone, Watcher ги чита датотеките што ги пишува играта и зачувува што се случило, за подоцна да можете да го погледнете како статистика и временска лента.

*Технички детали: адаптер `hearthstone`, вид [`log`](sources-and-rules.md); работи додека работи `Hearthstone.exe` и бара нови податоци на секои 0,5 s.*

## Што се снима {#what-is-recorded}

- почеток и крај на играта, со резултатот (победа, пораз, нерешено), потези и името на противникот
- секој потег
- секоја линија од Power.log и од другите логови цела во heat.raw.parquet
- игри, победи, порази, нерешени, потези, најдолга игра

## Од каде доаѓа {#where-it-comes-from}

&lt;install>\Logs\Power.log (или Logs\Hearthstone_\*\Power.log), запишан откако %LOCALAPPDATA%\Blizzard\Hearthstone\log.config ќе има секција [Power], и секој друг \*.log што играта го пишува таму

## Како да се вклучи {#how-to-switch-it-on}

`python -m heat3d_watch setup hearthstone --apply` додава запишување на [Power] во %LOCALAPPDATA%\Blizzard\Hearthstone\log.config (се чува резервна копија); рестартирајте ја играта

Впишете ја командата во терминал отворен во папката на Watcher (види [Пред да почнете](before-you-start.md)). Ако не успее, последната линија кажува зошто; [Инсталирање и стартување](installing-and-running.md) ги опфаќа вообичаените причини.

`python -m heat3d_watch setup hearthstone` ги наведува датотеките што би ги променил; `python -m heat3d_watch setup hearthstone --apply` ги менува, чувајќи го оригиналот како `<file>.heat3d-backup` (види [Команди](commands.md#setup)). Печати `hearthstone: changed: ...` за секоја промена, или `hearthstone: nothing to change` кога веќе е вклучено.

## Како работи {#how-it-works}

Hearthstone: Power.log на играта, што таа го пишува штом `log.config` ќе го побара.

Hearthstone го чита `%LOCALAPPDATA%\Blizzard\Hearthstone\log.config` при стартот;
секција `[Power]` со `LogLevel=1` и `FilePrinting=true` ја тера да ги пишува
промените на состојбата на секоја игра во `<install>\Logs\Power.log` (поновите клиенти ги ставаат
логовите од секое стартување во своја папка, `Logs\Hearthstone_<date>\`). Ова
е документираното дебаг-запишување што алатките за следење шпилови го вклучуваат од 2014
(поставувањето на Hearthstone Deck Tracker ја пишува истата секција). `setup()` ја додава
секцијата, со резервна копија на датотеката каква што била; играта бара рестарт за да ја прочита.

Користените линии, сите од `GameState.DebugPrintPower()` (линиите `PowerTaskList`
ги повторуваат и се прескокнуваат):

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

Сопствената страна на играчот е онаа чија почетна рака има именувани карти
(картите на противникот се скриени), а во спротивно страната што не е AI (сметка 0) или
„UNKNOWN HUMAN PLAYER". Линиите носат само време од денот; датумот е денешниот.
Без позиции.

Секоја линија од Power.log се чува цела во суровата датотека на сесијата (правилото на
конверторите на 3DHeat), вклучувајќи ги повторувањата на `PowerTaskList`, опциите, изборите и
ажурирањата на ентитети: `type` е методот што ја напишал (`GameState.DebugPrintPower`,
`PowerTaskList.DebugPrintPower`, `GameState.DebugPrintOptions`, ...). Секој друг
лог што играта го пишува покрај него - `LoadingScreen.log`, `Decks.log`, `Zone.log`,
`Arena.log`, ..., секој таму кога log.config го бара (алатките за следење шпилови често
го прават тоа) - се следи на ист начин и се чува со своето име во `log`.

## Позиции и оски {#positions-and-axes}

| | |
|---|---|
| Позициите се снимаат | не |
| Оска нагоре | `y` |
| Единици | не се снимаат позиции |
| Огледално за прегледувачот | нема |
| Размер на единиците (`scale`: прегледувачот ги множи позициите со него) | 1 |

Тие одат во `meta.json` на секоја сесија (`axes`) и, кога сесијата има позиции, во подножјето на `heat.parquet`, па прегледувачот 3DHeat самиот ги врти и размерува редовите - види [Податоците](the-data.md).

## Повеќе играчи {#multiplayer}

- Означено како играно онлајн (`multiplayer`): **да**. `games --markdown` го прикажува ова како „allowed (reads only what the game publishes)".
- Вид `log`: чита само она што играта или платформата го дава (датотеки што играта ги пишува додека работи), па снима и во онлајн игра и офлајн; знамето одлучува само дали меморијата смее некогаш да се чита.
- Меморија: овој адаптер **никогаш** не ја чита. Само адаптерите `memory` читаат меморија, и никогаш за игра означена како играна онлајн - види [Извори и правила](sources-and-rules.md).

## Снимена статистика {#statistics-recorded}

Клучевите на статистиката што кодот на овој адаптер ги поставува по име (`stats` во `meta.json` на секоја сесија и табелата `stats` во `watcher.sqlite`):

`bad_lines`, `games`, `longest_game_turns`, `losses`, `ties`, `turns`, `wins`

Клуч во загради се дополнува при извршување (`score.{team}` е еден клуч по тим). Клучевите што кодот ги зема од табела со полињата на играта или од сопствените имиња на статистиката на играта не се во овој список; „Што се снима" погоре ги именува.

## Комплетност {#completeness}

Watcher го следи [правилото за конвертори](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md) на 3DHeat: она што го држи изворот се чита или се чува, никогаш не се отфрла. Покрај редовите, секој пакет, страница, линија или одговор што адаптерот ги прима се чува цел во `heat.raw.parquet` на сесијата (колони `time`, `ms`, `type`, `used`, `payload`, `text`, потоа секое поле зачувано по име; `used` означува што станало и редови), а `selfCheck.completeness` во `meta.json` го брои секој `type` - `lost` е 0.

**Читано**

- `CREATE_GAME`, играчите (ентитет, ид на играч, сметка; сметка 0 е AI) и нивните имиња (`DebugPrintGame`)
- чија страна е на играчот, според именуваните карти од почетната рака
- `TAG_CHANGE` на TURN, PLAYSTATE (победа, пораз, нерешено) и STATE COMPLETE: потези, резултат, противник

**Чувано сурово**

- секоја линија од Power.log цела, `type` = методот што ја напишал (`GameState.DebugPrintPower`, `PowerTaskList.DebugPrintPower`, `GameState.DebugPrintGame`, `GameState.DebugPrintOptions`, `GameState.SendChoices`, `GameState.DebugPrintEntityChoices`, `PowerProcessor.DoTaskListForCard`, ...), `log` `Power`, `used` каде што станала ред: секоја одиграна, повлечена и откриена карта, секоја промена на таг, напад, опција и избор е тука, сè уште не во редовите
- секоја линија од другите логови во истата папка (`LoadingScreen`, `Decks`, `Zone`, `Arena`, `Achievements`, `FullScreenFX`, ... - што и да вклучи log.config), исти `type`, со името на логот во `log`
- линија без ниво и време од денот како `untimed`, а без метод како `untagged`

**Не е достапно**

- позиции: картовната игра нема такви
- скриените карти на противникот: логот една карта ја именува дури откако ќе се открие
- логови што log.config не ги вклучува: `setup` бара само [Power]; другите логови доаѓаат кога друга алатка (следач на шпилови) ги вклучила
- логови од претходни стартувања: секое стартување пишува нова папка; оние постари од ова стартување на играта не се читаат пак

**Големина**: Power.log со Verbose е околу 1-5 MB по игра, 10-40 MB на час игра; другите логови додаваат малку; zstd во heat.raw.parquet го прави приближно десеттина или помалку (линиите многу се повторуваат)

## Проверено {#verified}

тестирано на синтетички линии од Power.log во форматот на играта; не е тестирано со играта

## Извор {#source}

[heat3d_watch/adapters/hearthstone.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/hearthstone.py)

<!-- Generated from the adapter by tools/gen_game_pages.py; change the adapter and run it again rather than editing this page. -->
