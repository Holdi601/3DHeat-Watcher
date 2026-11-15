---
title: "Rocket League (состојба на играта)"
nav_order: 40
lang: "mk"
source: game-rocketleague-stats.md
source_hash: "3da6ea772068"
nav_exclude: true
search_exclude: true
---
# Rocket League (состојба на играта) {#rocket-league-game-state}

Додека играте Rocket League, Watcher го зачувува она што играта им го јавува на програмите на вашиот сопствен компјутер, за подоцна да можете да го погледнете на мапа во прегледувачот 3DHeat.

*Технички детали: адаптер `rocketleague-stats`, вид [`gsi`](sources-and-rules.md); работи додека работи `RocketLeague.exe` и бара нови податоци на секои 0,05 s.*

## Што се снима {#what-is-recorded}

- удари во топката со местото на топката (XYZ, Unreal единици), кој ја удрил и брзините
- голови со местото на удар, стрелецот, асистентот и брзината; удари во пречката со местото
- stat feed (демолирања, одбрани, шутеви, епски одбрани, ...), почетни удари, повторувања, почеток и крај на натпреварот, победникот
- сопствени голови, асистенции, одбрани, шутеви, демоа, допири, резултат и резултатите на тимовите, од UpdateState
- завршната линија на секој играч на крајот на натпреварот
- вашите редови како `me`: играчот именуван во поставките (`config --set player_names.rocketleague-stats=<name>`), инаку оној што го следи камерата на играта надвор од повторувањата
- без позиции на автомобили: API нема такви

## Од каде доаѓа {#where-it-comes-from}

Stats API: TCP JSON тек од 127.0.0.1:49123 (Port во &lt;RL>\TAGame\Config\TAStatsAPI.ini или DefaultStatsAPI.ini)

## Како да се вклучи {#how-to-switch-it-on}

`python -m heat3d_watch setup rocketleague-stats --apply` (поставува PacketSendRate=30), потоа стартувајте го Rocket League

Впишете ја командата во терминал отворен во папката на Watcher (види [Пред да почнете](before-you-start.md)). Ако не успее, последната линија кажува зошто; [Инсталирање и стартување](installing-and-running.md) ги опфаќа вообичаените причини.

`python -m heat3d_watch setup rocketleague-stats` ги наведува датотеките што би ги променил; `python -m heat3d_watch setup rocketleague-stats --apply` ги менува, чувајќи го оригиналот како `<file>.heat3d-backup` (види [Команди](commands.md#setup)). Печати `rocketleague-stats: changed: ...` за секоја промена, или `rocketleague-stats: nothing to change` кога веќе е вклучено.

## Како работи {#how-it-works}

Rocket League: официјалниот Stats API, локален сокет во кој играта ги пишува податоците за натпреварот.

Се вклучува во `<RL>\TAGame\Config\TAStatsAPI.ini` - или `DefaultStatsAPI.ini`
кога тој не постои, што играта го чита само тогаш - под
`[TAGame.MatchStatsExporter_TA]`:

```text
PacketSendRate   UpdateState messages per second; 0 (the default) switches the API off, at most 120
Port             the TCP port the game listens on, default 49123 (WebPort 49124 is a WebSocket copy)
```

Играта е серверот: клиентот се поврзува на 127.0.0.1:49123 и чита тек
од JSON објекти `{"Event": name, "Data": {...}}` (некои изданија праќаат Data како
JSON низа), еден по друг без разделувачи. Настаните се праќаат во
тактот кога се случуваат, независно од брзината:

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

Местата се Unreal единици (сантиметри), Z нагоре; теренот е околу 8200 x 10240
со голови на Y = +-5120. Позициите на автомобилите не се дел од API: она што има
место е топката таму каде што била удрена, постигнат гол или удрена во пречката.

Секоја порака се чува и цела (правилото на конверторите на 3DHeat, docs/converters.md
во складот на прегледувачот): `heat.raw.parquet`, `type` е името на Event на пораката,
`text` е објектот онака како што дошол од тековите. UpdateState бајт по бајт ист
со претходниот (паузиран натпревар, мени) се чува еднаш и се брои во `unchanged_replies` на meta.json.
Пораките меѓу натпреварите чекаат во заостаток за сесијата на следниот
натпревар; она што останува кога играта ќе се затвори добива своја сесија.
Знаците меѓу објектите што не се JSON се чуваат како „junk".

Извори: <https://www.rocketleague.com/en/developer/stats-api> (официјалната страница);
големината на буквите во полињата и TCP рамкувањето потврдени спрема клиентот rlstatsapi
(<https://docs.rs/crate/rlstatsapi>, MIT; читан само за факти).

## Позиции и оски {#positions-and-axes}

| | |
|---|---|
| Позициите се снимаат | да |
| Оска нагоре | `z` |
| Единици | Unreal единици (сантиметри) |
| Огледално за прегледувачот | нема |
| Размер на единиците (`scale`: прегледувачот ги множи позициите со него) | 1 |

Тие одат во `meta.json` на секоја сесија (`axes`) и, кога сесијата има позиции, во подножјето на `heat.parquet`, па прегледувачот 3DHeat самиот ги врти и размерува редовите - види [Податоците](the-data.md).

## Повеќе играчи {#multiplayer}

- Означено како играно онлајн (`multiplayer`): **да**. `games --markdown` го прикажува ова како „allowed (reads only what the game publishes)".
- Вид `gsi`: чита само она што играта или платформата го дава (интеграција на состојбата на играта или локален API што играта го нуди), па снима и во онлајн игра и офлајн; знамето одлучува само дали меморијата смее некогаш да се чита.
- Меморија: овој адаптер **никогаш** не ја чита. Само адаптерите `memory` читаат меморија, и никогаш за игра означена како играна онлајн - види [Извори и правила](sources-and-rules.md).

## Снимена статистика {#statistics-recorded}

Клучевите на статистиката што кодот на овој адаптер ги поставува по име (`stats` во `meta.json` на секоја сесија и табелата `stats` во `watcher.sqlite`):

`bad_packets`, `demolished`, `other_goals`, `overtime`, `result`, `team_goals`

Клуч во загради се дополнува при извршување (`score.{team}` е еден клуч по тим). Клучевите што кодот ги зема од табела со полињата на играта или од сопствените имиња на статистиката на играта не се во овој список; „Што се снима" погоре ги именува.

## Комплетност {#completeness}

Watcher го следи [правилото за конвертори](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md) на 3DHeat: она што го држи изворот се чита или се чува, никогаш не се отфрла. Покрај редовите, секој пакет, страница, линија или одговор што адаптерот ги прима се чува цел во `heat.raw.parquet` на сесијата (колони `time`, `ms`, `type`, `used`, `payload`, `text`, потоа секое поле зачувано по име; `used` означува што станало и редови), а `selfCheck.completeness` во `meta.json` го брои секој `type` - `lost` е 0.

**Читано**

- BallHit (место, кој, тим, брзини пред и по), GoalScored (место на удар, стрелец, асистент, брзина, време на гол), CrossbarHit (место, последен допир, брзина, сила), StatfeedEvent (настан, тип, главна и споредна цел), MatchEnded (победник, резултат), името на секој друг настан како ред
- од UpdateState: теренот (arena), целта на камерата надвор од повторувањата (кој е `me`), резултатите на тимовите, головите, асистенциите, одбраните, шутевите, демоата, допирите, допирите на автомобилот и резултатот на секој играч (сопствените како статистика, на сите како `player_result` на крајот на натпреварот); продолжението (overtime) од ClockUpdatedSeconds

**Чувано сурово**

- секоја порака цела онака како што дошла од тековите (`text`), под своето име на Event: `UpdateState` (PrimaryId и Shortcut на секој играч, часовникот, брзината и тимот на топката, имињата и боите на тимовите, знамињата за повторување и победник, и состојбата на автомобилот каде што играта ја праќа), `BallHit`, `GoalScored` (со последниот допир на топката), `CrossbarHit`, `StatfeedEvent`, `MatchCreated`, `MatchInitialized`, `CountdownBegin`, `RoundStarted`, `GoalReplayStart`, `GoalReplayWillEnd`, `GoalReplayEnd`, `MatchPaused`, `MatchUnpaused`, `MatchEnded`, `PodiumStart`, `ReplayCreated`, `MatchDestroyed`, `ClockUpdatedSeconds` и секој настан што подоцнежно издание ќе го додаде
- UpdateState бајт по бајт ист со претходниот (пауза, менија) се чува еднаш и се брои (`unchanged_replies` во meta.json)
- пораки меѓу натпреварите: на своето време пред почетокот на следниот натпревар; по последниот натпревар, во сопствена сесија (`raw_only` во meta.json)
- `unreadable`: објект што не е порака на Stats API; `junk`: знаци меѓу објектите

**Не е достапно**

- позиции на автомобили и состојба на автомобилот додека се игра: играта ги праќа само на гледачи
- UpdateState меѓу две праќања: играта праќа PacketSendRate во секунда (`setup` поставува 30, играта дозволува до 120); настаните се праќаат во тактот кога се случуваат
- копијата преку WebSocket на WebPort (49124): истите пораки како TCP портата, не се читаат двапати

**Големина**: UpdateState е 1-3 KB за шест играчи, 30 во секунда: околу 100-300 MB на час во `raw.bin` додека трае натпревар, десеттина или помалку во zstd `heat.raw.parquet` (проценето од документираниот формат, не измерено на играта)

## Проверено {#verified}

тестирано на пораки во документираниот формат испратени од лажен локален сервер; не е тестирано со играта

## Извор {#source}

[heat3d_watch/adapters/rocketleague.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/rocketleague.py)

<!-- Generated from the adapter by tools/gen_game_pages.py; change the adapter and run it again rather than editing this page. -->
