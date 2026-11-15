---
title: "Hearthstone (лог файлове)"
nav_order: 25
lang: "bg"
source: game-hearthstone.md
source_hash: "e79c19776947"
nav_exclude: true
search_exclude: true
---
# Hearthstone (лог файлове) {#hearthstone-log-files}

Докато играете Hearthstone, watcher-ът чете файловете, които играта записва, и запазва какво се е случило, за да можете по-късно да го разгледате като статистики и хронология.

*Технически подробности: адаптер `hearthstone`, вид [`log`](sources-and-rules.md); работи, докато `Hearthstone.exe` е стартиран, и търси нови данни на всеки 0.5 s.*

## Какво се записва {#what-is-recorded}

- начало и край на играта, с резултата (спечелена, загубена, наравно), ходовете и името на противника
- всеки ход
- всеки ред от Power.log и другите логове цял в heat.raw.parquet
- игри, победи, загуби, равенства, ходове, най-дълга игра

## Откъде идва {#where-it-comes-from}

&lt;install>\Logs\Power.log (или Logs\Hearthstone_\*\Power.log), записван, след като %LOCALAPPDATA%\Blizzard\Hearthstone\log.config има секция [Power], и всеки друг \*.log, който играта записва там

## Как се включва {#how-to-switch-it-on}

`python -m heat3d_watch setup hearthstone --apply` добавя записването на [Power] в %LOCALAPPDATA%\Blizzard\Hearthstone\log.config (запазва се резервно копие); рестартирайте играта

Въведете командата в терминал, отворен в папката на watcher-а (вижте [Преди да започнете](before-you-start.md)). Ако се провали, последният ред казва защо; [Инсталиране и стартиране](installing-and-running.md) описва обичайните причини.

`python -m heat3d_watch setup hearthstone` показва файловете, които би променил; `python -m heat3d_watch setup hearthstone --apply` ги променя, като запазва оригинала като `<file>.heat3d-backup` (вижте [Команди](commands.md#setup)). Печата `hearthstone: changed: ...` за всяка промяна или `hearthstone: nothing to change`, когато вече е включено.

## Как работи {#how-it-works}

Hearthstone: Power.log на играта, който тя записва, след като `log.config` ѝ поиска това.

Hearthstone чете `%LOCALAPPDATA%\Blizzard\Hearthstone\log.config` при стартиране;
секция `[Power]` с `LogLevel=1` и `FilePrinting=true` кара играта да записва
всяка промяна на състоянието в `<install>\Logs\Power.log` (по-новите клиенти слагат
логовете на всяко стартиране в папка със собствено име, `Logs\Hearthstone_<date>\`). Това е
документираното логване за отстраняване на грешки, което проследяващите тестета включват от 2014 г.
(настройката на Hearthstone Deck Tracker записва същата секция). `setup()` добавя
секцията, с резервно копие на файла такъв, какъвто е бил; играта трябва да се рестартира, за да я прочете.

Използваните редове, всички от `GameState.DebugPrintPower()` (редовете `PowerTaskList`
ги повтарят и се пропускат):

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

Страната на самия играч е тази, чиято начална ръка има назовани карти
(тези на противника са скрити), иначе страната, която не е AI (акаунт 0) или
"UNKNOWN HUMAN PLAYER". Редовете носят само часа на деня; датата е днешната.
Няма позиции.

Всеки ред от Power.log се пази цял в суровата странична част на сесията (правилото за конвертори на 3DHeat): редовете `PowerTaskList` за повторенията, опциите, избора и обновленията на обектите са включени; `type` е методът, който го е записал (`GameState.DebugPrintPower`,
`PowerTaskList.DebugPrintPower`, `GameState.DebugPrintOptions`, ...). Всеки друг
лог, който играта записва до него - `LoadingScreen.log`, `Decks.log`, `Zone.log`,
`Arena.log`, ..., всеки там, когато log.config го поиска (проследяващите тестета
често го правят) - се следва по същия начин и се пази с името си в `log`.

## Позиции и оси {#positions-and-axes}

| | |
|---|---|
| Записват се позиции | не |
| Вертикална ос | `y` |
| Мерни единици | без записани позиции |
| Огледално за визуализатора | няма |
| Мащаб на единицата (`scale`: визуализаторът умножава позициите по него) | 1 |

Те отиват в `meta.json` на всяка сесия (`axes`) и, когато сесията има позиции, в края на `heat.parquet`, така че визуализаторът на 3DHeat сам завърта и мащабира редовете - вижте [Данните](the-data.md).

## Онлайн игра {#multiplayer}

- Отбелязано като играно онлайн (`multiplayer`): **да**. `games --markdown` показва това като "разрешено (чете само това, което играта публикува)".
- Вид `log`: чете само това, което играта или платформата предоставят (файлове, които играта записва, докато работи), затова записва и в онлайн игра, както и офлайн; флагът решава само дали паметта изобщо може да се чете.
- Памет: адаптерът **никога** не чете паметта. Само адаптерите от вид `memory` четат памет, и никога за игра, отбелязана като играна онлайн - вижте [Източници и правила](sources-and-rules.md).

## Записвани статистики {#statistics-recorded}

Ключовете на статистиките, които кодът на този адаптер задава по име (`stats` на всяка сесия в `meta.json` и таблицата `stats` в `watcher.sqlite`):

`bad_lines`, `games`, `longest_game_turns`, `losses`, `ties`, `turns`, `wins`

Ключ във фигурни скоби се довършва по време на работа (`score.{team}` е по един ключ за всеки отбор). Ключовете, които кодът взема от таблица с полетата на играта или от собствените имена на статистиките ѝ, не са в този списък; "Какво се записва" по-горе ги посочва.

## Пълнота {#completeness}

Watcher-ът следва [правилото за конвертори](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md) на 3DHeat: това, което източникът съдържа, се чете или се пази, никога не се изхвърля. Освен редовете, всеки пакет, страница, ред или отговор, който адаптерът получава, се пази цял в `heat.raw.parquet` на сесията (колони `time`, `ms`, `type`, `used`, `payload`, `text` и всяко поле, запазено по име; `used` отбелязва какво е станало и на редове), а `selfCheck.completeness` в `meta.json` брои всеки `type` - `lost` е 0.

**Чете се**

- `CREATE_GAME`, играчите (обект, идентификатор на играч, акаунт; акаунт 0 е AI) и имената им (`DebugPrintGame`)
- чия страна е на играча - от назованите карти в началната ръка
- `TAG_CHANGE` за TURN, PLAYSTATE (won, lost, tied) и STATE COMPLETE: ходове, резултат, противник

**Пази се сурово**

- всеки ред от Power.log цял, `type` = методът, който го е записал (`GameState.DebugPrintPower`, `PowerTaskList.DebugPrintPower`, `GameState.DebugPrintGame`, `GameState.DebugPrintOptions`, `GameState.SendChoices`, `GameState.DebugPrintEntityChoices`, `PowerProcessor.DoTaskListForCard`, ...), `log` `Power`, `used` там, където е станал ред: всяка изиграна, теглена и показана карта, всяка промяна на таг, атака, опция и избор са тук, но още не са в редове
- всеки ред от другите логове в същата папка (`LoadingScreen`, `Decks`, `Zone`, `Arena`, `Achievements`, `FullScreenFX`, ... - каквото log.config включи), със същите `type`, с името на лога в `log`
- ред без нивото и часа на деня се пази като `untimed`, ред без метод - като `untagged`

**Не е налично**

- позиции: карточната игра няма такива
- скритите карти на противника: логът назовава карта само след като е била показана
- логове, които log.config не включва: `setup` иска само [Power]; другите логове идват, когато друг инструмент (проследяващ тесте) ги е включил
- логове от по-ранни стартирания: всяко стартиране записва нова папка; тези, по-стари от това стартиране на играта, не се четат отново

**Размер**: Power.log с Verbose е около 1-5 MB на игра, 10-40 MB на час игра; другите логове добавят малко; zstd в heat.raw.parquet го свива приблизително до една десета или по-малко (редовете много се повтарят)

## Проверено {#verified}

тествано на синтетични редове от Power.log във формата на играта; не е тествано срещу самата игра

## Източник {#source}

[heat3d_watch/adapters/hearthstone.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/hearthstone.py)

<!-- Generated from the adapter by tools/gen_game_pages.py; change the adapter and run it again rather than editing this page. -->
