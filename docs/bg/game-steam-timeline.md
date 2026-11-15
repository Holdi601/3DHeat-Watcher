---
title: "Steam Timeline (платформа)"
nav_order: 44
lang: "bg"
source: game-steam-timeline.md
source_hash: "3878efe0d7f1"
nav_exclude: true
search_exclude: true
---
# Steam Timeline (платформа) {#steam-timeline-platform}

Watcher-ът запазва това, което Steam Timeline пази за вашите игри, за да можете по-късно да разгледате историята си като статистика и времева линия.

*Технически подробности: адаптер `steam-timeline`, вид [`platform`](sources-and-rules.md); работи през цялото време (не чака игра да започне) и търси нови данни на всеки 10 s.*

## Какво се записва {#what-is-recorded}

- една сесия на всеки файл на времевата линия: началото и краят ѝ (session_start, session_end)
- постиженията, отключени по време на игра, с времето им
- промените в режима на играта (игра, подготовка, менюта, екран за зареждане)
- събития, които играта добавя чрез ISteamTimeline, с заглавие и описание, под името на иконата ѝ
- фази на играта (мач, мисия) с техните етикети; събитията в една фаза носят нейния идентификатор като session
- описания на състоянието, които играта показва на времевата линия („Round 3“)
- собствените грешки при записване на Steam

## Откъде идва {#where-it-comes-from}

%STEAM%\userdata\\&lt;account>\gamerecordings\timelines\timeline_&lt;appid>&lt;date>_&lt;time>.json

## Как се включва {#how-to-switch-it-on}

Steam > Settings > Game Recording: записвайте във фонов режим или при поискване (тогава Steam пише времевите линии)

## Как работи {#how-it-works}

Това, което стартерът и графичният драйвер пазят за играта: статистиките, постиженията, времето за игра и времевите линии на Steam, както и акценти и клипове на NVIDIA.

Нито един от тези източници не изисква играта да сътрудничи или да работи, затова трите адаптера тук са винаги включени и четат няколко файла на всеки няколко секунди.

#### Steam Timeline (`steam-timeline`) {#steam-timeline-steam-timeline}

`<Steam>\userdata\<account>\gamerecordings\timelines\timeline_<appid><yyyymmdd>_<hhmmss>.json`, който се пише, докато Steam Game Recording е включен. Файлът е JSON с числа като низове: "daterecorded" (Unix секунди), "starttime"/"endtime" (ms) и "entries", всеки {"id", "time" (ms от daterecorded), "type", ...}. Типове, видени в истински файлове:
```text
achievement        achievement_name - Steam добавя такива за всяка игра
gamemode           mode, ETimelineGameMode: 1 игра, 2 подготовка,
                   3 менюта, 4 екран за зареждане
error              description - на Steam ("#GameRecording_RecordingFailed")
event              AddInstantaneousTimelineEvent/AddRangeTimelineEvent на играта:
                   title, description, icon, priority, duration (ms),
                   possible_clip - "You killed <name>" / "with the <weapon>"
state_description  title - SetTimelineTooltip ("Round 3")
phase              отрязък StartGamePhase..EndGamePhase: duration (ms), tags
                   [{name, icon, group, priority}] (режим, карта ...)
```
Структурата на файла е на Steam и не е документирана; полетата са параметрите на API. Всеки друг тип се записва под собственото си име с полетата си.
<https://partner.steamgames.com/doc/api/ISteamTimeline>
<https://partner.steamgames.com/doc/features/timeline>

Същият модул обслужва още: [Акценти на NVIDIA (платформа)](game-nvidia-highlights.md), [Статистика на Steam (платформа)](game-steam-stats.md).

## Позиции и оси {#positions-and-axes}

| | |
|---|---|
| Записани позиции | не |
| Ос нагоре | `y` |
| Единици | метри |
| Огледално за визуализатора | няма |
| Мащаб на единицата (`scale`: визуализаторът умножава позициите по него) | 1 |

Те се записват в `meta.json` на всяка сесия (`axes`) и, когато сесията има позиции, в края на `heat.parquet`, така че визуализаторът на 3DHeat сам завърта и мащабира редовете - вижте [Данните](the-data.md).

## Многоиграчки режим {#multiplayer}

- Отбелязано като игра онлайн (`multiplayer`): **не**. `games --markdown` показва това като „за един играч“.
- Вид `platform`: чете само това, което играта или платформата предава (това, което пази Steam или графичният драйвер), затова записва и в онлайн игра, и офлайн; флагът решава само дали паметта изобщо може да се чете.
- Памет: **никога** не се чете от този адаптер. Само `memory` адаптерите четат паметта и никога за игра, отбелязана като онлайн - вижте [Източници и правила](sources-and-rules.md).

## Записана статистика {#statistics-recorded}

Ключове на статистиката, които кодът на този адаптер задава по име (`stats` на всяка сесия в `meta.json` и таблицата `stats` в `watcher.sqlite`):

`achievements`, `game_mode_changes`, `phases`, `recorded_seconds`, `timeline_events`

Ключ във фигурни скоби се попълва по време на работа (`score.{team}` е по един ключ за всеки отбор). Ключовете, които кодът взима от таблица с полетата на играта или от собствените имена на статистиките ѝ, не са в този списък; „Какво се записва“ по-горе ги посочва.

## Пълнота {#completeness}

Watcher-ът следва [правилото за конвертори](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md) на 3DHeat: това, което източникът съдържа, се чете или се пази, никога не се изхвърля. Освен редовете, всеки пакет, страница, ред или отговор, който адаптерът получава, се пази цял в `heat.raw.parquet` на сесията (колони `time`, `ms`, `type`, `used`, `payload`, `text`, плюс всяко поле, запазено по име; `used` отбелязва какво е станало и ред), а `selfCheck.completeness` в `meta.json` брои всеки `type` - `lost` е 0.

**Прочетено**

- всеки запис веднъж, като ред в неговото време: типът му, всяко просто поле (title, description, icon, priority, duration, possible_clip, име на постижението, режим ...), етикетите на фаза по група, показваното име на постижението от схемата на статистиките; началото и краят на файла

**Пазено цяло**

- всеки запис цял като JSON под собствения `type` на Steam (`gamemode`, `achievement`, `event`, `state_description`, `phase`, `error`, всеки друг): вложените полета - иконата и приоритетът на етикет, всичко, което добави по-късен Steam - са само тук
- `timeline`: собствените полета на файла (daterecorded, starttime, endtime, всяко друго), когато сесията се отваря и отново, когато се променят

**Не е налично**

- самият запис (видео): Steam го пази в собствените си папки; сесията посочва файла на времевата линия по име
- четене на файл, който Steam все още пише и който не може да се разчете дори когато краят му е затворен: отчита се (`bad` в състоянието на адаптера) и се чете отново при следващата промяна, където се вземат записите му

**Размер**: няколко стотин записа по 100-300 байта на час игра: далеч под 1 MB на час

## Проверено {#verified}

тествано на истински файлове на времеви линии от локална инсталация: постижение, gamemode, error и собствените записи на играта event, state_description и phase; самият формат на файла не е документиран

## Източник {#source}

[heat3d_watch/adapters/platform.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/platform.py)

<!-- Генерирано от адаптера с tools/gen_game_pages.py; променете адаптера и го пуснете отново, вместо да редактирате тази страница. -->
