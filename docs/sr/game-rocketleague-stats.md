---
title: "Rocket League (стање игре)"
nav_order: 40
lang: "sr"
source: game-rocketleague-stats.md
source_hash: "3da6ea772068"
nav_exclude: true
search_exclude: true
---
# Rocket League (стање игре) {#rocket-league-game-state}

Док играте Rocket League, посматрач чува оно што игра јавља програмима на вашем рачунару, да бисте то касније погледали на мапи у 3DHeat прегледачу.

*Технички детаљи: адаптер `rocketleague-stats`, врста [`gsi`](sources-and-rules.md); ради док је `RocketLeague.exe` покренут и тражи нове податке сваких 0,05 s.*

## Шта се бележи {#what-is-recorded}

- ударци у лопту са местом лопте (XYZ, Unreal јединице), ко ју је ударио и брзине
- голови са местом удара, стрелац, асистент и брзина; ударци у пречку са местом
- статистички фид (рушења, одбране, шутеви, епске одбране, ...), почеци, реплеји, почетак и крај утакмице, победник
- сопствени голови, асистенције, одбране, шутеви, рушења, додири, резултат и резултати тимова, из UpdateState
- завршна линија сваког играча на крају утакмице
- ваши редови као `me`: играч именован у подешавањима (`config --set player_names.rocketleague-stats=<name>`), иначе онај кога камера игре прати ван реплеја
- без положаја аутомобила: API их нема

## Одакле долази {#where-it-comes-from}

Stats API: TCP JSON ток са 127.0.0.1:49123 (порт у <RL>\TAGame\Config\TAStatsAPI.ini или DefaultStatsAPI.ini)

## Како се укључује {#how-to-switch-it-on}

`python -m heat3d_watch setup rocketleague-stats --apply` (поставља PacketSendRate=30), па покрените Rocket League

Укуцајте команду у терминалу отвореном у фасцикли посматрача (видети [Пре почетка](before-you-start.md)). Ако не успе, последњи ред каже зашто; [Инсталација и покретање](installing-and-running.md) објашњава уобичајене узроке.

`python -m heat3d_watch setup rocketleague-stats` исписује датотеке које би променио; `python -m heat3d_watch setup rocketleague-stats --apply` их мења, а оригинал чува као `<file>.heat3d-backup` (видети [Команде](commands.md#setup)). За сваку промену исписује `rocketleague-stats: changed: ...`, или `rocketleague-stats: nothing to change` ако је већ укључено.

## Како ради {#how-it-works}

Rocket League: званични Stats API, локална утичница у коју игра пише податке о утакмици.

Укључује се у `<RL>\TAGame\Config\TAStatsAPI.ini` – или у `DefaultStatsAPI.ini` ако први не постоји, што игра чита само тада – у одељку `[TAGame.MatchStatsExporter_TA]`:

```text
PacketSendRate   UpdateState messages per second; 0 (the default) switches the API off, at most 120
Port             the TCP port the game listens on, default 49123 (WebPort 49124 is a WebSocket copy)
```

Игра је сервер: клијент се повезује на 127.0.0.1:49123 и чита ток JSON објеката `{"Event": name, "Data": {...}}` (неке верзије шаљу Data као JSON стринг), један за другим, без раздвајача. Догађаји се шаљу на такту кад се десе, без обзира на брзину:

```text
UpdateState   MatchGuid, Players[] (Name, PrimaryId, Shortcut, TeamNum 0 blue / 1 orange,
              Score, Goals, Shots, Assists, Saves, Touches, CarTouches, Demos; car state
              only for spectators), Game (Teams[], TimeSeconds, bOvertime, Ball {Speed,
              TeamNum}, bReplay, bHasWinner, Winner, Arena, bHasTarget, Target)
BallHit       Players[] (Name, Shortcut, TeamNum), Ball {PreHitSpeed, PostHitSpeed, Location {X,Y,Z}}
GoalScored    GoalSpeed, GoalTime, ImpactLocation {X,Y,Z}, Scorer, Assister, BallLastTouch
CrossbarHit   BallLocation {X,Y,Z}, BallSpeed, ImpactForce, BallLastTouch
StatfeedEvent EventName, Type, MainTarget, SecondaryTarget
MatchEnded    WinnerTeamNum
MatchCreated, MatchInitialized, CountdownBegin, RoundStarted, GoalReplayStart/WillEnd/End,
MatchPaused/Unpaused, PodiumStart, ReplayCreated, MatchDestroyed, ClockUpdatedSeconds
```

Положаји су Unreal јединице (центиметри), z горе; поље је око 8200 x 10240, са голом на Y = ±5120. Положаји аутомобила нису део API-ја: има место само лопта, где је ударена, где је постигла гол или где је ударила пречку.

Свака порука се чува и цела (правило конвертора 3DHeat-а, docs/converters.md у репозиторијуму прегледача): `heat.raw.parquet`, `type` је назив Event-а поруке, `text` је објекат како је дошао из тока. UpdateState бајт за бајтом исти као претходни (паузирана утакмица, мени) чува се једном и броји у `unchanged_replies` у meta.json-у. Поруке између утакмица чекају у заостатку за почетак следеће утакмице; оно што остане кад се игра затвори добија сопствену сесију. Знакови између објеката који нису JSON чувају се као „junk“.

Извори: <https://www.rocketleague.com/en/developer/stats-api> (званична страница); назив поља и TCP оквир потврђени су према rlstatsapi клијенту (<https://docs.rs/crate/rlstatsapi>, MIT; читан само због чињеница).

## Положаји и осе {#positions-and-axes}

| | |
|---|---|
| Бележени положаји | да |
| Вертикална оса | `z` |
| Јединице | Unreal јединице (центиметри) |
| Огледало за прегледач | нема |
| Размера јединице (`scale`: прегледач множи положаје са њом) | 1 |

Ово иде у `meta.json` (`axes`) сваке сесије и, кад сесија има положаје, у подножје `heat.parquet`-а, па прегледач 3DHeat сам окреће и размерава редове – видети [Подаци](the-data.md).

## Више играча {#multiplayer}

- Означено као игра на мрежи (`multiplayer`): **да**. `games --markdown` ово приказује као „дозвољено (чита само оно што игра објављује)“.
- Врста `gsi`: чита само оно што игра или платформа даје (интеграција стања игре или локални API који игра служи), па бележи и у игри на мрежи и ван ње; застава одлучује само да ли меморија сме икада да се чита.
- Меморија: **никад** је овај адаптер не чита. Само `memory` адаптери читају меморију, и никад за игру означену као игра на мрежи – видети [Извори и правила](sources-and-rules.md).

## Бележена статистика {#statistics-recorded}

Кључеви статистике које код овог адаптера поставља по имену (`stats` сваке сесије у `meta.json`-у и табела `stats` у `watcher.sqlite`-у):

`bad_packets`, `demolished`, `other_goals`, `overtime`, `result`, `team_goals`

Кључ у витичастим заградама се допуњава у време рада (`score.{team}` је један кључ по тиму). Кључеви које код узима из табеле поља игре или из назива статистике саме игре нису на овом списку; у „Шта се бележи“ горе они су наведени.

## Потпуност {#completeness}

Посматрач прати [правило конвертора](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md) из 3DHeat-а: оно што извор садржи се чита или чува, никад се не одбацује. Осим редова, сваки пакет, страница, ред или одговор који адаптер прими чува се цео у `heat.raw.parquet` сесије (колоне `time`, `ms`, `type`, `used`, `payload`, `text`, па свако поље које се чува по имену; `used` означава оно што је постало и редове), а `selfCheck.completeness` у `meta.json`-у броји сваки `type` – `lost` је 0.

**Чита се**

- BallHit (место, ко, тим, брзине пре и после), GoalScored (место удара, стрелац, асистент, брзина, време гола), CrossbarHit (место, последњи додир, брзина, сила), StatfeedEvent (догађај, врста, главна и секундарна мета), MatchEnded (победник, исход), сваки други назив догађаја као ред
- из UpdateState: арена, циљ камере ван реплеја (ко је `me`), резултати тимова, голови, асистенције, одбране, шутеви, рушења, додири, додири аутомобила и резултат сваког играча (сопствени као статистика, свих као `player_result` на крају утакмице); продужетак из ClockUpdatedSeconds

**Чува се сирово**

- свака порука цела како је дошла из тока (`text`), под својим назívom Event-а: `UpdateState` (ид-ови PrimaryId и Shortcut сваког играча, сат, брзина и тим лопте, називи и боје тимова, заставице реплеја и победника, и стање аутомобила где га игра шаље), `BallHit`, `GoalScored` (са последњим додиром лопте), `CrossbarHit`, `StatfeedEvent`, `MatchCreated`, `MatchInitialized`, `CountdownBegin`, `RoundStarted`, `GoalReplayStart`, `GoalReplayWillEnd`, `GoalReplayEnd`, `MatchPaused`, `MatchUnpaused`, `MatchEnded`, `PodiumStart`, `ReplayCreated`, `MatchDestroyed`, `ClockUpdatedSeconds` и сваки догађај који каснија верзија дода
- UpdateState бајт за бајтом исти као претходни (паузирано, мени) чува се једном и броји се (`unchanged_replies` у meta.json-у)
- поруке између утакмица: у свом времену, пре почетка следеће утакмице; после последње утакмице, у сопственој сесији (`raw_only` у meta.json-у)
- `unreadable`: објекат који није порука Stats API-ја; `junk`: знакови између објеката

**Није доступно**

- положаји аутомобила и стање аутомобила док се игра: игра их шаље само гледаоцима
- UpdateState између два слања: игра шаље PacketSendRate у секунди (`setup` поставља 30, игра дозвољава до 120); догађаји се шаљу на такту кад се десе
- WebSocket копија на WebPort-у (49124): исте поруке као на TCP порту, није читана два пута

**Величина**: UpdateState је 1–3 KB за шест играча, 30 у секунди: око 100–300 MB по сату у `raw.bin` док утакмица траје, а десетина или мање у zstd `heat.raw.parquet` (процењено према документованом формату, није измерено на игри)

## Проверено {#verified}

тестирано на порукама у документованом формату које је послао лажни локални сервер; није тестирано на самој игри

## Извор {#source}

[heat3d_watch/adapters/rocketleague.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/rocketleague.py)

<!-- Generated from the adapter by tools/gen_game_pages.py; change the adapter and run it again rather than editing this page. -->
