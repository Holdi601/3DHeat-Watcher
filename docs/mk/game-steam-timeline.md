---
title: "Steam Timeline (платформа)"
nav_order: 44
lang: "mk"
source: game-steam-timeline.md
source_hash: "3878efe0d7f1"
nav_exclude: true
search_exclude: true
---
# Steam Timeline (платформа) {#steam-timeline-platform}

Watcher-от го зачувува она што Steam Timeline го чува за вашите игри, за подоцна да ја погледнете историјата како статистика и временска линија.

*Технички детали: адаптер `steam-timeline`, вид [`platform`](sources-and-rules.md); работи постојано (не чека да почне игра) и бара нови податоци на секои 10 s.*

## Што се снима {#what-is-recorded}

- една сесија по датотека на временската линија: нејзиниот почеток и крај (session_start, session_end)
- достигнувања отклучени за време на играње, со време
- промени на режимот на играта (играње, подготовка, менија, екран за вчитување)
- настани што игрите ги додаваат преку ISteamTimeline, со наслов и опис, под името на нивната икона
- фази на играта (натпревар, мисија) со нивните ознаки; настаните во една го носат нејзиниот id како сесија
- описи на состојба што играта ги покажува на временската линија („Round 3“)
- сопствените грешки на Steam при снимање

## Од каде доаѓа {#where-it-comes-from}

%STEAM%\userdata\\&lt;account>\gamerecordings\timelines\timeline_&lt;appid>&lt;date>_&lt;time>.json

## Како да се вклучи {#how-to-switch-it-on}

Steam > Settings > Game Recording: снимајте во позадина или на барање (тогаш Steam пишува временски линии)

## Како работи {#how-it-works}

Она што стартерот и драјверот за графика го чуваат за играњето: статистиката, достигнувањата,
времето на играње и временските линии на Steam, и highlights и клиповите на NVIDIA.

Ниту еден од овие извори не бара играта да соработува или да работи, па трите
адаптери овде се секогаш вклучени и гледаат неколку датотеки на секои неколку секунди.

#### Steam Timeline (`steam-timeline`) {#steam-timeline-steam-timeline}

`<Steam>\userdata\<account>\gamerecordings\timelines\timeline_<appid><yyyymmdd>_<hhmmss>.json`,
пишувана додека Steam Game Recording е вклучен. Датотеката е JSON со броеви
како низи: "daterecorded" (Unix секунди), "starttime"/"endtime" (ms) и
"entries", секој {"id", "time" (ms од daterecorded), "type", ...}. Типови
виде во вистински датотеки:
```text
achievement        achievement_name - Steam ги додава за секоја игра
gamemode           mode, ETimelineGameMode: 1 playing, 2 staging, 3 menus,
                   4 loading screen
error              description - на самиот Steam ("#GameRecording_RecordingFailed")
event              AddInstantaneousTimelineEvent/AddRangeTimelineEvent на играта:
                   title, description, icon, priority, duration (ms),
                   possible_clip - "You killed <name>" / "with the <weapon>"
state_description  title - SetTimelineTooltip ("Round 3")
phase              распон StartGamePhase..EndGamePhase: duration (ms), tags
                   [{name, icon, group, priority}] (mode, map ...)
```
Распоредот на датотеката е на Steam и недокументиран; полињата се параметрите
на API-то. Секој друг тип се снима под своето име со своите полиња.
<https://partner.steamgames.com/doc/api/ISteamTimeline>
<https://partner.steamgames.com/doc/features/timeline>

Истиот модул служи и за: [NVIDIA highlights (платформа)](game-nvidia-highlights.md), [Steam статистика (платформа)](game-steam-stats.md).

## Позиции и оски {#positions-and-axes}

| | |
|---|---|
| Снимени позиции | не |
| Горна оска | `y` |
| Единици | метри |
| Огледално за прегледувачот | нема |
| Скала на единици (`scale`: прегледувачот ги множи позициите со неа) | 1 |

Овие одат во `meta.json` на секоја сесија (`axes`) и, кога сесијата има позиции, во подножјето на `heat.parquet`, па прегледувачот 3DHeat сам ги врти и скалира редовите - видете [Податоците](the-data.md).

## Мултиплеер {#multiplayer}

- Означено како играно онлајн (`multiplayer`): **не**. `games --markdown` го прикажува ова како „single-player“.
- Вид `platform`: чита само она што играта или платформата го дава (она што го чуваат Steam или драјверот за графика), па снима и во онлајн игра и офлајн; знамето одлучува само дали меморијата смее некогаш да се чита.
- Меморија: овој адаптер **никогаш** не ја чита. Само `memory` адаптерите читаат меморија, и никогаш за игра означена како играна онлајн - видете [Извори и правила](sources-and-rules.md).

## Снимена статистика {#statistics-recorded}

Клучеви на статистика што кодот на овој адаптер ги поставува по име (`stats` на секоја сесија во `meta.json` и табелата `stats` во `watcher.sqlite`):

`achievements`, `game_mode_changes`, `phases`, `recorded_seconds`, `timeline_events`

Клуч во загради { } се дополнува при извршување (`score.{team}` е еден клуч по тим). Клучевите што кодот ги зема од табела со полињата на играта или од сопствените имиња на статистика на играта не се во овој список; „Што се снима“ погоре ги именува.

## Комплетност {#completeness}

Watcher-от го следи [правилото за конвертори](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md) на 3DHeat: она што го содржи изворот се чита или се чува, никогаш не се отфрла. Покрај редовите, секој пакет, страница, линија или одговор што адаптерот ги прима се чува целосно во `heat.raw.parquet` на сесијата (колони `time`, `ms`, `type`, `used`, `payload`, `text`, па секое поле зачувано по име; `used` означува што станало и редови), а `selfCheck.completeness` во `meta.json` го брои секој `type` - `lost` е 0.

**Прочитано**

- секој запис еднаш, како ред во своето време: неговиот тип, секое обично поле (title, description, icon, priority, duration, possible_clip, име на достигнување, mode, ...), ознаките на фазата по група, прикажаното име на достигнувањето од шемата на статистиките; почетокот и крајот на датотеката

**Чувано сурово**

- секој запис целосен како JSON под сопствениот `type` на Steam (`gamemode`, `achievement`, `event`, `state_description`, `phase`, `error`, секој друг): вгнездените полиња - иконата и приоритетот на ознаката, сѐ што подоцнежен Steam ќе додаде - се само овде
- `timeline`: сопствените полиња на датотеката (daterecorded, starttime, endtime, секое друго), кога сесијата се отвора и повторно кога ќе се променат

**Недостапно**

- самото снимање (видео): Steam го чува во свои папки; сесијата упатува на датотеката на временската линија по име
- читање на датотека што Steam ја пишува, а која не може да се анализира дури ни со затворен крај: се брои (`bad` во состојбата на адаптерот) и се чита повторно при следната промена, кога се земаат нејзините записи

**Големина**: неколку стотици записи од 100-300 бајти на час играње: далеку под 1 MB на час

## Проверено {#verified}

тестирано на вистински датотеки на временска линија од локална инсталација: записи achievement, gamemode, error, и записи event, state_description и phase на самите игри; форматот на датотеката е недокументиран

## Извор {#source}

[heat3d_watch/adapters/platform.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/platform.py)

<!-- Generated from the adapter by tools/gen_game_pages.py; change the adapter and run it again rather than editing this page. -->
