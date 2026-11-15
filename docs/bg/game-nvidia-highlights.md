---
title: "NVIDIA highlights (платформа)"
nav_order: 34
lang: "bg"
source: game-nvidia-highlights.md
source_hash: "5d45211c0e37"
nav_exclude: true
search_exclude: true
---
# NVIDIA highlights (платформа) {#nvidia-highlights-platform}

Watcher-ът записва какво пази NVIDIA highlights за вашите игри, за да можете по-късно да видите историята си на карта в визуализатора 3DHeat.

*Технически подробности: адаптер `nvidia-highlights`, вид [`platform`](sources-and-rules.md); работи през цялото време (не чака игра да стартира) и търси нови данни на всеки 10 s.*

## Какво се записва {#what-is-recorded}

- всеки нов клип, highlight или снимка: игра, файл, вид, дължина и моментът (стенен часовник, ms)
- идентификаторът и името на highlight-а, когато играта го е регистрирала при NVIDIA
- къде е бил играчът в този момент, когато друг адаптер е записал същата игра тогава
- заявките за highlight, които игрите с GfeSDK записват в журнала си, дори когато не е запазен клип

## Откъде идва {#where-it-comes-from}

%LOCALAPPDATA%\NVIDIA Corporation\NVIDIA Overlay\UGCTracker.json, GallerySettings.json, Highlights\\&lt;game>\config.json; клиповете в папката за заснемане (%USERPROFILE%\Videos\NVIDIA\\&lt;Game>\\\*.mp4) и &lt;temp>\Highlights\\&lt;game>; %LOCALAPPDATA%\NVIDIA Corporation\GfeSDK\\&lt;exe>_&lt;pid>.log

## Как се включва {#how-to-switch-it-on}

NVIDIA App: Instant Replay или Highlights включени, клиповете се запазват с клавиш или от играта

## Как работи {#how-it-works}

Какво пазят стартерът и графичният драйвер за играта: статистиките на Steam,
постиженията, времето за игра и хронологиите, и highlight-ите и клиповете на NVIDIA.

Нито един от тези източници не изисква играта да съдейства или да работи, затова
трите адаптера тук са винаги включени и разглеждат няколко файла на всеки няколко секунди.

#### Highlight-ите и клиповете на NVIDIA (`nvidia-highlights`) {#nvidia-highlights-and-clips-nvidia-highlights}

Какво пази NVIDIA App / GeForce Experience, всичко в
`%LOCALAPPDATA%\NVIDIA Corporation\NVIDIA Overlay`:
```text
UGCTracker.json      индексът на галерията: {"UGC": [{id, path, type (video,
                     image), subType (InstantReplay, Normal, ...), date
                     (UTC, когато файлът е записан), profileName, drsName
                     (exe-то), shortName, msDuration, ...}], "apps", "info"}
GallerySettings.json settings.currentDirectoryV2 (къде се запазват клиповете),
                     settings.tempDirectory (highlight-ите чакат в
                     <temp>\Highlights\<game>, докато се запазят)
Highlights\<game>\config.json  видовете highlight, които играта е регистрирала:
                     {"highlights": {id: {significance, highlightTags,
                     name: {locale: text}}}, profileName, drsName, shortName}
```
и самите клипови файлове, `<папка за заснемане>\<Game>\<Game> yyyy.mm.dd -
hh.mm.ss.ff.DVR.mp4` (снимките: `<Game> Screenshot yyyy.mm.dd - ...png`), като
часът в името е местното време, когато клипът е запазен. Игрите с GfeSDK записват
и своите highlight заявки в `%LOCALAPPDATA%\NVIDIA Corporation\GfeSDK\<exe>_<pid>.log`.

Какво може и какво не може да даде това: игра, която поддържа NVIDIA Highlights
(GfeSDK), регистрира видовете highlight веднъж - идентификатор като "kill", значимост,
тагове, показвано име - и после казва само "highlight <id>,
от <ms> преди сега до <ms> след". Няма позиции, няма мач или рунд, няма
противник, няма потребителски данни: в SDK няма поле за нищо от това. Запазеният
клип добавя файл, име на игра, дължина и час. Така се записва "този вид момент, в
тази игра, в този час" - а място само като се търси часът в записа на друг адаптер
за същата игра (`position_at`), което този адаптер прави за всеки записан клип.
<https://developer.nvidia.com/highlights>

Всеки адаптер пази какво вече е видял в `<data>\state\<id>.json`, така че при
рестарт нищо не се записва два пъти.

Всяка сесия пази и откъде идват редовете ѝ, цели (правилото за конвертори на 3DHeat,
docs/converters.md в хранилището на визуализатора), в `heat.raw.parquet`: байтовете на
файла със статистики и на неговата схема и блока localconfig на играта
(steam-stats; файл със статистики, който декодерът не може да прочете, дава сесия,
която съдържа само байтовете му), заглавната част на файла на хронологията и всеки
запис като JSON (steam-timeline), записа на всеки клип в индекса на галерията, определенията
на highlight-ите на играта и всеки ред от журнала на GfeSDK, и тези, които не са
заявки за highlight (nvidia-highlights).

Същият модул обслужва и: [Steam статистики (платформа)](game-steam-stats.md), [Steam Timeline (платформа)](game-steam-timeline.md).

## Позиции и оси {#positions-and-axes}

| | |
|---|---|
| Записани позиции | само заимствани: мястото, което друг запис на същата игра има за този момент |
| Вертикална ос | `y` |
| Единици | метри |
| Огледално за визуализатора | няма |
| Мащаб на единицата (`scale`: визуализаторът умножава позициите по него) | 1 |

Тези стойности отиват в `meta.json` на всяка сесия (`axes`) и, когато сесията има позиции, в footer-а на `heat.parquet`, така че визуализаторът на 3DHeat сам завърта и мащабира редовете - вижте [Данните](the-data.md).

## Многоиграчка {#multiplayer}

- Отбелязано като игра онлайн (`multiplayer`): **не**. `games --markdown` показва това като "single-player".
- Вид `platform`: чете само това, което играта или платформата предоставят (това, което пазят Steam или графичният драйвер), затова записва и при онлайн игра, и офлайн; флагът решава само дали паметта изобщо може да се чете.
- Памет: **никога** не се чете от този адаптер. Само адаптерите от вид `memory` четат памет, и никога за игра, отбелязана като игра онлайн - вижте [Източници и правила](sources-and-rules.md).

## Записвана статистика {#statistics-recorded}

Ключовете на статистиките, които кодът на този адаптер задава по име (`stats` на всяка сесия в `meta.json` и таблицата `stats` в `watcher.sqlite`):

`clip_seconds`, `clips`, `placed`, `screenshots`

Ключ в фигурни скоби се допълва по време на работа (`score.{team}` е по един ключ за всеки отбор). Ключовете, които кодът взема от таблица с полетата на играта или от имената на статистиките на самата игра, не са в този списък; "Какво се записва" по-горе ги посочва.

## Пълнота {#completeness}

Watcher-ът следва [правилото за конвертори](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md) на 3DHeat: това, което източникът съдържа, се чете или се пази, никога не се изхвърля. Освен редовете, всеки пакет, страница, ред или отговор, който адаптерът получава, се пази цял в `heat.raw.parquet` на сесията (колоните `time`, `ms`, `type`, `used`, `payload`, `text`, а после всяко поле, запазено по име; `used` отбелязва какво е станало и ред), а `selfCheck.completeness` в `meta.json` брои всеки `type` - `lost` е 0.

**Прочетено**

- всеки нов клип и снимка: игра, файл, вид, медия, дължина (индекс, а ако няма - MP4 заглавната част), моментът от името на файла, идентификаторът и името на highlight-а, когато играта ги е регистрирала, и мястото на играча тогава от записа на друг адаптер
- заявките за highlight на GfeSDK (всеки `Posted Request HL...`, без конфигурационните извиквания) с техния час

**Пазено цяло**

- `UGC`: целият запис на клипа от индекса на галерията UGCTracker.json, всяко поле, което NVIDIA записва
- `clip_file`: за клип, който индексът не съдържа, пътят на файла, размерът, часът и папката му
- `highlights_config`: `Highlights\<game>\config.json` на играта, както е записан (значимост, тагове, имена на всички езици), веднъж за сесия
- `gfesdk_log`: всеки ред от журналите на GfeSDK, прочетени след първото стартиране, с `used` true за заявките за highlight и false за останалите (конфигурация, настройки на видеото, собствените съобщения на SDK)

**Няма налично**

- самите клипове и снимки: видеото и изображенията остават там, където NVIDIA ги е запазила; редовете назовават файла
- какво е имало преди първото стартиране на адаптера: приема се за вече видяно, така че години клипове не се превръщат в сесии наведнъж (`baseline`; False ги записва)
- `apps` и `info` от UGCTracker.json и GallerySettings.json: настройките на приложението, а не моменти от игра; използва се папката за заснемане, която те назовават
- позиции, рунди, противници: GfeSDK няма поле за тях

**Размер**: около 1 KB на клип и няколко KB определения и редове от журнала на всяко стартиране на игра: далеч под 1 MB на час

## Проверено {#verified}

тествано на реален индекс на галерията, настройки, определения на highlight-и и клипове от локална инсталация; редовете на заявките за highlight в GfeSDK и идентификаторите на highlight-ите в клиповете са непроверени

## Източник {#source}

[heat3d_watch/adapters/platform.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/platform.py)

<!-- Generated from the adapter by tools/gen_game_pages.py; change the adapter and run it again rather than editing this page. -->
