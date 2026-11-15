---
title: "Steam Timeline (платформа)"
nav_order: 44
lang: "sr"
source: game-steam-timeline.md
source_hash: "3878efe0d7f1"
nav_exclude: true
search_exclude: true
---
# Steam Timeline (платформа) {#steam-timeline-platform}

Посматрач чува оно што Steam Timeline бележи о вашим играма, па можете касније да гледате своју историју као статистику и хронологију.

*Технички детаљи: адаптер `steam-timeline`, врста [`platform`](sources-and-rules.md); ради стално (не чека да почне игра) и тражи нове податке сваких 10 s.*

## Шта се бележи {#what-is-recorded}

- једна сесија по фајлу хронологије: њен почетак и крај (session_start, session_end)
- достигнућа откључана током игре, с временом
- промене режима игре (играње, припрема, менији, екран учитавања)
- догађаји које игре додају преко ISteamTimeline, са насловом и описом, под називом њихове иконице
- фазе игре (меч, мисија) са ознакама; догађаји унутар једне носе њен id као session
- описи стања које игра приказује на хронологији („Round 3")
- Steam-ове сопствене грешке при снимању

## Одакле долази {#where-it-comes-from}

%STEAM%\userdata\\&lt;account>\gamerecordings\timelines\timeline_&lt;appid>&lt;date>_&lt;time>.json

## Како се укључује {#how-to-switch-it-on}

Steam > Settings > Game Recording: снимајте у позадини или на захтев (тада Steam пише хронологије)

## Како ради {#how-it-works}

Оно што покретач и графички драјвер чувају о игрању: Steam-ова статистика, достигнућа, време играња и хронологије, и NVIDIA-ови highlights и клипови.

Ниједан од ових извора не тражи да игра сарађује или да ради, па су три адаптера овде стално укључена и сваких неколико секунди гледају неколико фајлова.

#### Steam Timeline (`steam-timeline`) {#steam-timeline-steam-timeline}

`<Steam>\userdata\<account>\gamerecordings\timelines\timeline_<appid><yyyymmdd>_<hhmmss>.json`, пише се док је Steam Game Recording укључено. Фајл је JSON са бројевима као стринговима: "daterecorded" (Unix секунде), "starttime"/"endtime" (ms) и "entries", свако {"id", "time" (ms од daterecorded), "type", ...}. Типови виђени на правим фајловима:

```text
achievement        achievement_name - Steam adds these for every game
gamemode           mode, an ETimelineGameMode: 1 playing, 2 staging, 3 menus,
                   4 loading screen
error              description - Steam's own ("#GameRecording_RecordingFailed")
event              a game's AddInstantaneousTimelineEvent/AddRangeTimelineEvent:
                   title, description, icon, priority, duration (ms),
                   possible_clip - "You killed <name>" / "with the <weapon>"
state_description  title - SetTimelineTooltip ("Round 3")
phase              a StartGamePhase..EndGamePhase span: duration (ms), tags
                   [{name, icon, group, priority}] (mode, map ...)
```

Структура фајла је Steam-ова и није документована; поља су параметри API-ја. Сваки други тип се бележи под својим именом, са својим пољима.
<https://partner.steamgames.com/doc/api/ISteamTimeline>
<https://partner.steamgames.com/doc/features/timeline>

Исти модул служи и: [NVIDIA highlights (платформа)](game-nvidia-highlights.md), [Steam статистика (платформа)](game-steam-stats.md).

## Положаји и осе {#positions-and-axes}

| | |
|---|---|
| Положаји се бележе | не |
| Оса нагоре | `y` |
| Јединице | метри |
| Огледано за приказивач | нигде |
| Размера јединица (`scale`: приказивач множи положаје с њом) | 1 |

Ово иде у `meta.json` сваке сесије (`axes`) и, кад сесија има положаје, у подножје `heat.parquet`-а, па приказивач сам окреће и скалира редове – видите [Подаци](the-data.md).

## Више играча {#multiplayer}

- Означено као игра на мрежи (`multiplayer`): **не**. `games --markdown` то приказује као „за једног играча".
- Врста `platform`: чита само оно што игра или платформа предају (што Steam или графички драјвер чува), па бележи и у мрежној игри и ван ње; ознака одлучује само да ли меморија сме икада да се чита.
- Меморија: овај адаптер је **никад** не чита. Само адаптери `memory` читају меморију, и никад за игру означену као играна на мрежи – видите [Извори и правила](sources-and-rules.md).

## Забележена статистика {#statistics-recorded}

Кључеви статистике које код овог адаптера поставља по имену (`stats` сваке сесије у `meta.json` и табела `stats` у `watcher.sqlite`):

`achievements`, `game_mode_changes`, `phases`, `recorded_seconds`, `timeline_events`

Кључ у витичастим заградама се попуњава у време рада (`score.{team}` је један кључ по тиму). Кључеви које код узима из табеле поља игре или из назива статистике саме игре нису на овом списку; „Шта се бележи" горе их наводи.

## Потпуност {#completeness}

Посматрач прати 3DHeat-ово [правило конвертера](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md): оно што извор садржи се чита или чува, никад не одбацује. Осим редова, сваки пакет, страница, ред или одговор који адаптер прими чува се цео у `heat.raw.parquet` сесије (колоне `time`, `ms`, `type`, `used`, `payload`, `text`, па свако поље које је сачувано по имену; `used` означава оно што је постало и редове), а `meta.json`-ов `selfCheck.completeness` броји сваки `type` – `lost` је 0.

**Прочитано**

- сваки унос једном, као ред у свом времену: његов тип, свако једноставно поље (title, description, icon, priority, duration, possible_clip, achievement name, mode, ...), ознаке фазе по групи, приказно име достигнућа из шеме статистике; почетак и крај фајла

**Сачувано сирово**

- сваки унос цео као JSON под Steam-овим сопственим `type` (`gamemode`, `achievement`, `event`, `state_description`, `phase`, `error`, било који други): угнежђена поља – иконица и приоритет ознаке, све што касније Steam дода – су само овде
- `timeline`: сопствена поља фајла (daterecorded, starttime, endtime, било које друго), кад се сесија отвори и опет кад се промене

**Није доступно**

- сам снимак (видео): Steam га чува у својим фасциклама; сесија се позива на фајл хронологије по имену
- читање фајла који Steam пише, а који се не може рашчланити ни кад се његов крај затвори: бројањем се бележи (`bad` у стању адаптера) и поново чита при следећој промени, где се узимају његови уноси

**Величина**: неколико стотина уноса од 100–300 бајтова по сату игре: далеко испод 1 MB по сату

## Проверено {#verified}

тестирано на правим фајловима хронологије с локалне инсталације: достигнућа, gamemode, error, и сопствени event, state_description и phase уноси игара; сам формат фајла није документован

## Извор {#source}

[heat3d_watch/adapters/platform.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/platform.py)

<!-- Generated from the adapter by tools/gen_game_pages.py; change the adapter and run it again rather than editing this page. -->
