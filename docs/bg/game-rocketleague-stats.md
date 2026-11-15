---
title: "Rocket League (състояние на играта)"
nav_order: 40
lang: "bg"
source: game-rocketleague-stats.md
source_hash: "3da6ea772068"
nav_exclude: true
search_exclude: true
---
# Rocket League (състояние на играта) {#rocket-league-game-state}

Докато играете Rocket League, watcher-ът записва това, което играта докладва на програмите на вашия компютър, за да можете по-късно да го разгледате на карта във визуализатора 3DHeat.

*Технически подробности: адаптер `rocketleague-stats`, вид [`gsi`](sources-and-rules.md); работи, докато `RocketLeague.exe` е стартиран, и търси нови данни на всеки 0.05 s.*

## Какво се записва {#what-is-recorded}

- удари на топката с мястото на топката (XYZ, единици на Unreal), кой я е ударил и скоростите
- голове с мястото на удара, стрелец, асистент и скорост; удари в напречната греда с мястото
- статистиките от фийда (разрушения, спасявания, удари, епични спасявания ...), начални удари, повторения, начало и край на мача, победител
- собствени голове, асистенции, спасявания, удари, разрушения, докосвания, резултат и резултатите на отборите, от UpdateState
- последният ред на всеки играч в края на мача
- вашите собствени редове като `me`: играчът, посочен в настройките (`config --set player_names.rocketleague-stats=<name>`), иначе този, който камерата на играта следва извън повторенията
- няма позиции на колите: API-то няма такива

## Откъде идва {#where-it-comes-from}

API на статистиките: TCP поток от JSON от 127.0.0.1:49123 (порт в <RL>\TAGame\Config\TAStatsAPI.ini или DefaultStatsAPI.ini)

## Как се включва {#how-to-switch-it-on}

`python -m heat3d_watch setup rocketleague-stats --apply` (задава PacketSendRate=30), после стартирайте Rocket League

Въведете командата в терминал, отворен в папката на watcher-а (вижте [Преди да започнете](before-you-start.md)). Ако се провали, последният ред казва защо; [Инсталиране и стартиране](installing-and-running.md) описва честите причини.

`python -m heat3d_watch setup rocketleague-stats` показва кои файлове би променил; `python -m heat3d_watch setup rocketleague-stats --apply` ги променя, като запазва оригинала като `<file>.heat3d-backup` (вижте [Командите](commands.md#setup)). За всяка промяна печата `rocketleague-stats: changed: ...`, или `rocketleague-stats: nothing to change`, когато вече е включено.

## Как работи {#how-it-works}

Rocket League: официалното Stats API, локален сокет, в който играта пише данните на мача.

Включва се в `<RL>\TAGame\Config\TAStatsAPI.ini` - или в `DefaultStatsAPI.ini`, когато първият не съществува (играта чете втория само тогава) - под `[TAGame.MatchStatsExporter_TA]`:

```text
PacketSendRate   съобщения UpdateState в секунда; 0 (по подразбиране) изключва API-то, най-много 120
Port             TCP портът, на който играта слуша, по подразбиране 49123 (WebPort 49124 е копие по WebSocket)
```

Играта е сървърът: клиентът се свързва към 127.0.0.1:49123 и чете поток от JSON обекти `{"Event": name, "Data": {...}}` (някои версии пращат Data като JSON низ), един след друг без разделители. Събитията се изпращат в такта, в който станат, независимо от честотата:

```text
UpdateState   MatchGuid, Players[] (Name, PrimaryId, Shortcut, TeamNum 0 син / 1 оранжев,
              Score, Goals, Shots, Assists, Saves, Touches, CarTouches, Demos; състояние
              на колата само за зрители), Game (Teams[], TimeSeconds, bOvertime, Ball {Speed,
              TeamNum}, bReplay, bHasWinner, Winner, Arena, bHasTarget, Target)
BallHit       Players[] (Name, Shortcut, TeamNum), Ball {PreHitSpeed, PostHitSpeed, Location {X,Y,Z}}
GoalScored    GoalSpeed, GoalTime, ImpactLocation {X,Y,Z}, Scorer, Assister, BallLastTouch
CrossbarHit   BallLocation {X,Y,Z}, BallSpeed, ImpactForce, BallLastTouch
StatfeedEvent EventName, Type, MainTarget, SecondaryTarget
MatchEnded    WinnerTeamNum
MatchCreated, MatchInitialized, CountdownBegin, RoundStarted, GoalReplayStart/WillEnd/End,
MatchPaused/Unpaused, PodiumStart, ReplayCreated, MatchDestroyed, ClockUpdatedSeconds
```

Местоположенията са в единици на Unreal (сантиметри), Z нагоре; полето е около 8200 x 10240, с вратите при Y = +-5120. Позициите на колите не са част от API-то: има място само топката - където е била ударена, отбелязана или ударила гредата.

Всяко съобщение се пази и цяло (правилото за конвертори на 3DHeat, docs/converters.md в хранилището на визуализатора): `heat.raw.parquet`, `type` е името на събитието на съобщението, `text` е обектът, както е дошъл от потока. UpdateState, който е байт по байт същият като предишния (спрян мач, меню), се пази веднъж и се брои в `unchanged_replies` в meta.json. Съобщенията между мачовете чакат в опашка за сесията на следващия мач; каквото остане, когато играта се затвори, получава сесия за себе си. Символите между обектите, които не са JSON, се пазят като "junk".

Източници: <https://www.rocketleague.com/en/developer/stats-api> (официалната страница); имената на полетата и рамкирането на TCP потвърдени по клиента rlstatsapi (<https://docs.rs/crate/rlstatsapi>, MIT; прочетен само за факти).

## Позиции и оси {#positions-and-axes}

| | |
|---|---|
| Записват се позиции | да |
| Ос нагоре | `z` |
| Мерни единици | единици на Unreal (сантиметри) |
| Огледален за визуализатора | няма |
| Мащаб на единицата (`scale`: визуализаторът умножава позициите по него) | 1 |

Те отиват в `meta.json` на всяка сесия (`axes`) и, когато сесията има позиции, в долния колонтитул на `heat.parquet`, така че визуализаторът 3DHeat сам завърта и мащабира редовете - вижте [Данните](the-data.md).

## Мултиплейър {#multiplayer}

- Отбелязана като игра, играна онлайн (`multiplayer`): **да**. `games --markdown` показва това като "разрешено (чете само това, което играта публикува)".
- Вид `gsi`: чете само това, което играта или платформата предоставя (интеграция със състоянието на играта или локален API, който играта сервира), затова записва и в онлайн игра, както и в офлайн; флагът решава само дали паметта изобщо може да се чете.
- Памет: адаптерът **никога** не чете паметта. Само адаптерите от вид `memory` четат памет, и никога за игра, отбелязана като играна онлайн - вижте [Източници и правила](sources-and-rules.md).

## Записани статистики {#statistics-recorded}

Ключовете на статистиките, които кодът на адаптера задава по име (`stats` на всяка сесия в `meta.json` и таблицата `stats` в `watcher.sqlite`):

`bad_packets`, `demolished`, `other_goals`, `overtime`, `result`, `team_goals`

Ключ в фигурни скоби се допълва по време на работа (`score.{team}` е по един ключ за всеки отбор). Ключовете, които кодът взема от таблица с полетата на играта или от собствените имена на статистиките ѝ, не са в този списък; "Какво се записва" по-горе ги посочва.

## Пълнота {#completeness}

watcher-ът следва [правилото за конвертори](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md) на 3DHeat: това, което източникът съдържа, се чете или се пази, никога не се изхвърля. Освен редовете, всеки пакет, страница, ред или отговор, който адаптерът получава, се пази цял в `heat.raw.parquet` на сесията (колони `time`, `ms`, `type`, `used`, `payload`, `text`, а след тях всяко поле, запазено по име; `used` отбелязва какво е станало и ред), а `selfCheck.completeness` в `meta.json` брои всеки `type` - `lost` е 0.

**Прочетено**

- BallHit (място, кой, отбор, скорости преди и след), GoalScored (място на удара, стрелец, асистент, скорост, време на гола), CrossbarHit (място, последно докосване, скорост, сила), StatfeedEvent (събитие, вид, основна и вторична цел), MatchEnded (победител, резултат), името на всяко друго събитие като ред
- от UpdateState: аренета, целта на камерата извън повторенията (кой е `me`), резултатите на отборите, голове, асистенции, спасявания, удари, разрушения, докосвания, докосвания на колата и резултат на всеки играч (собствените като статистики, на всички като `player_result` в края на мача); овъртайм от ClockUpdatedSeconds

**Пазено цяло**

- всяко съобщение цяло, както е дошло от потока (`text`), под собственото си име на събитие: `UpdateState` (PrimaryId и Shortcut на всеки играч, часовникът, скоростта и отборът на топката, имената и цветовете на отборите, флаговете за повторение и победител, и състоянието на колата, където играта го изпраща), `BallHit`, `GoalScored` (с последното докосване на топката), `CrossbarHit`, `StatfeedEvent`, `MatchCreated`, `MatchInitialized`, `CountdownBegin`, `RoundStarted`, `GoalReplayStart`, `GoalReplayWillEnd`, `GoalReplayEnd`, `MatchPaused`, `MatchUnpaused`, `MatchEnded`, `PodiumStart`, `ReplayCreated`, `MatchDestroyed`, `ClockUpdatedSeconds` и всяко събитие, което по-късна версия добави
- UpdateState, който е байт по байт същият като предишния (на пауза, в менюта), се пази веднъж и се брои (`unchanged_replies` в meta.json)
- съобщения между мачовете: в собственото си време преди началото на следващия мач; след последния мач - в сесия за себе си (`raw_only` в meta.json)
- `unreadable`: обект, който не е съобщение от Stats API; `junk`: символи между обектите

**Няма го**

- позициите на колите и състоянието им при игра: играта ги изпраща само на зрители
- UpdateState между две изпращания: играта изпраща PacketSendRate пъти в секунда (setup задава 30, играта позволява до 120); събитията се изпращат в такта, в който станат
- копието по WebSocket на WebPort (49124): същите съобщения като на TCP порта, не се чете два пъти

**Размер**: UpdateState е 1-3 KB за шест играча, 30 в секунда: около 100-300 MB на час в `raw.bin`, докато мачът върви, а в zstd `heat.raw.parquet` - една десета или по-малко (оценено по документирания формат, не е измерено на играта)

## Проверено {#verified}

тествано със съобщения в документирания формат, изпратени от фалшив локален сървър; непроверено с играта

## Източник {#source}

[heat3d_watch/adapters/rocketleague.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/rocketleague.py)

<!-- Generated from the adapter by tools/gen_game_pages.py; change the adapter and run it again rather than editing this page. -->
