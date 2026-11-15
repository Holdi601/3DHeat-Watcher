---
title: "NVIDIA highlights (платформа)"
nav_order: 34
lang: "mk"
source: game-nvidia-highlights.md
source_hash: "5d45211c0e37"
nav_exclude: true
search_exclude: true
---
# NVIDIA highlights (платформа) {#nvidia-highlights-platform}

Watcher го зачувува она што NVIDIA highlights го чува за вашите игри, за подоцна да ја погледнете вашата историја на мапа во прегледувачот 3DHeat.

*Технички детали: адаптер `nvidia-highlights`, вид [`platform`](sources-and-rules.md); работи постојано (не чека да започне игра) и бара нови податоци на секои 10 s.*

## Што се снима {#what-is-recorded}

- секој нов клип, highlight или слика од екранот: игра, датотека, вид, должина и моментот (wall-clock ms)
- идот и името на highlight-от кога играта го регистрирала кај NVIDIA
- каде бил играчот во тој момент, кога друг адаптер ја снимал истата игра тогаш
- барањата за highlight што ги запишуваат игрите со GfeSDK, дури и кога не се чува клип

## Од каде доаѓа {#where-it-comes-from}

%LOCALAPPDATA%\NVIDIA Corporation\NVIDIA Overlay\UGCTracker.json, GallerySettings.json, Highlights\\&lt;game>\config.json; клипови во папката за снимање (%USERPROFILE%\Videos\NVIDIA\\&lt;Game>\\\*.mp4) и &lt;temp>\Highlights\\&lt;game>; %LOCALAPPDATA%\NVIDIA Corporation\GfeSDK\\&lt;exe>_&lt;pid>.log

## Како да се вклучи {#how-to-switch-it-on}

NVIDIA App: вклучен Instant Replay или Highlights, клипови зачувани со кратенка или од играта

## Како работи {#how-it-works}

Она што стартерот и драјверот за графика го чуваат за играњето: статистиката,
достигнувањата, времето на играње и временските линии на Steam, и highlights и клиповите на NVIDIA.

Ниту еден од овие извори не бара играта да соработува или да работи, па трите
адаптери овде се секогаш вклучени и гледаат неколку датотеки на секои неколку секунди.

#### NVIDIA highlights и клипови (`nvidia-highlights`) {#nvidia-highlights-and-clips-nvidia-highlights}

Она што го чува NVIDIA App / GeForce Experience, сè под
`%LOCALAPPDATA%\NVIDIA Corporation\NVIDIA Overlay`:
```text
UGCTracker.json      the gallery index: {"UGC": [{id, path, type (video,
                     image), subType (InstantReplay, Normal, ...), date
                     (UTC, when the file was written), profileName, drsName
                     (the exe), shortName, msDuration, ...}], "apps", "info"}
GallerySettings.json settings.currentDirectoryV2 (where clips are saved),
                     settings.tempDirectory (highlights wait in
                     <temp>\Highlights\<game> until saved)
Highlights\<game>\config.json  the highlight kinds a game registered:
                     {"highlights": {id: {significance, highlightTags,
                     name: {locale: text}}}, profileName, drsName, shortName}
```
и самите датотеки на клиповите, `<capture folder>\<Game>\<Game> yyyy.mm.dd -
hh.mm.ss.ff.DVR.mp4` (слики од екранот: `<Game> Screenshot yyyy.mm.dd - ...png`), каде што
времето во името е локалното време кога клипот бил зачуван. Игрите со GfeSDK ги запишуваат
и своите повици за highlight во `%LOCALAPPDATA%\NVIDIA Corporation\GfeSDK\<exe>_<pid>.log`.

Што може и што не може да даде ова: игра што поддржува NVIDIA Highlights
(GfeSDK) регистрира видови highlight еднаш - ид како „kill", значајност,
ознаки, прикажано име - а подоцна вели само „highlight &lt;id>,
од &lt;ms> пред сега до &lt;ms> потоа". Нема позиции, нема натпревар или
рунда, нема противник, нема прилагодени податоци: SDK нема поле за ништо од тоа. Зачуван
клип додава датотека, име на игра, должина и време. Значи она што се
снима е „овој вид момент, во оваа игра, во ова време" - а место
само со барање на времето во снимката на друг адаптер од истата игра
(`position_at`), што овој адаптер го прави за секој клип што го снима.
<https://developer.nvidia.com/highlights>

Секој адаптер го чува она што веќе го видел во `<data>\state\<id>.json`, па
рестарт не снима ништо двапати.

Секоја сесија го чува и она од што дошле нејзините редови, цело (правилото на
конверторите на 3DHeat, docs/converters.md во складиштето на прегледувачот), во `heat.raw.parquet`:
бајтите на датотеката со статистика и на нејзината шема и блокот localconfig на играта
(steam-stats; датотека со статистика што декодерот не може да ја прочита добива сесија што ги држи само
нејзините бајти), заглавието на датотеката со временска линија и секој запис како JSON
(steam-timeline), записот на секој клип во индексот на галеријата, дефинициите на highlight на играта
и секоја линија од логот на GfeSDK, и оние што не се барања за highlight
(nvidia-highlights).

Истиот модул служи и за: [Steam статистика (платформа)](game-steam-stats.md), [Steam Timeline (платформа)](game-steam-timeline.md).

## Позиции и оски {#positions-and-axes}

| | |
|---|---|
| Позициите се снимаат | само позајмени: местото што друга снимка од истата игра го има за тој момент |
| Оска нагоре | `y` |
| Единици | метри |
| Огледално за прегледувачот | нема |
| Размер на единиците (`scale`: прегледувачот ги множи позициите со него) | 1 |

Тие одат во `meta.json` на секоја сесија (`axes`) и, кога сесијата има позиции, во подножјето на `heat.parquet`, па прегледувачот 3DHeat самиот ги врти и размерува редовите - види [Податоците](the-data.md).

## Повеќе играчи {#multiplayer}

- Означено како играно онлајн (`multiplayer`): **не**. `games --markdown` го прикажува ова како „single-player".
- Вид `platform`: чита само она што играта или платформата го дава (она што го чуваат Steam или драјверот за графика), па снима и во онлајн игра и офлајн; знамето одлучува само дали меморијата смее некогаш да се чита.
- Меморија: овој адаптер **никогаш** не ја чита. Само адаптерите `memory` читаат меморија, и никогаш за игра означена како играна онлајн - види [Извори и правила](sources-and-rules.md).

## Снимена статистика {#statistics-recorded}

Клучевите на статистиката што кодот на овој адаптер ги поставува по име (`stats` во `meta.json` на секоја сесија и табелата `stats` во `watcher.sqlite`):

`clip_seconds`, `clips`, `placed`, `screenshots`

Клуч во загради се дополнува при извршување (`score.{team}` е еден клуч по тим). Клучевите што кодот ги зема од табела со полињата на играта или од сопствените имиња на статистиката на играта не се во овој список; „Што се снима" погоре ги именува.

## Комплетност {#completeness}

Watcher го следи [правилото за конвертори](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md) на 3DHeat: она што го држи изворот се чита или се чува, никогаш не се отфрла. Покрај редовите, секој пакет, страница, линија или одговор што адаптерот ги прима се чува цел во `heat.raw.parquet` на сесијата (колони `time`, `ms`, `type`, `used`, `payload`, `text`, потоа секое поле зачувано по име; `used` означува што станало и редови), а `selfCheck.completeness` во `meta.json` го брои секој `type` - `lost` е 0.

**Читано**

- секој нов клип и слика од екранот: игра, датотека, вид, медиум, должина (индекс, инаку заглавието на MP4), моментот од името на датотеката, идот и името на highlight-от каде што играта ги регистрирала, и местото на играчот тогаш од снимката на друг адаптер
- барањата за highlight на GfeSDK (секое `Posted Request HL...` освен повиците за конфигурација) со нивното време

**Чувано сурово**

- `UGC`: целиот запис на клипот од индексот на галеријата UGCTracker.json, секое поле што го пишува NVIDIA
- `clip_file`: за клип што индексот не го наведува, патеката, големината, времето и папката на датотеката
- `highlights_config`: `Highlights\<game>\config.json` на играта како што е запишан (значајност, ознаки, имиња на секој јазик), еднаш по сесија
- `gfesdk_log`: секоја линија од логовите на GfeSDK прочитана по првото стартување, `used` е true за барањата за highlight и false за остатокот (конфигурација, видео поставки, сопствените пораки на SDK)

**Не е достапно**

- самите клипови и слики од екранот: видеото и сликите остануваат таму каде што ги зачувал NVIDIA; редовите ја именуваат датотеката
- она што постоело пред првото стартување на адаптерот: се зема како веќе видено, па годините клипови не се претвораат одеднаш во сесии (`baseline`; False ги снима)
- `apps` и `info` во UGCTracker.json и GallerySettings.json: поставки на апликацијата, не моменти од играње; папката за снимање што ја именуваат се користи
- позиции, рунди, противници: GfeSDK нема поле за нив

**Големина**: околу 1 KB по клип и неколку KB дефиниции и линии од лог по стартување на игра: многу под 1 MB на час

## Проверено {#verified}

тестирано на вистински индекс на галерија, поставки, дефиниции на highlight и клипови од локална инсталација; линиите за барање highlight на GfeSDK и идовите на highlight во клиповите не се тестирани

## Извор {#source}

[heat3d_watch/adapters/platform.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/platform.py)

<!-- Generated from the adapter by tools/gen_game_pages.py; change the adapter and run it again rather than editing this page. -->
