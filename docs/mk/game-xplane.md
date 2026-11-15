---
title: "X-Plane (податоци во живо)"
nav_order: 50
lang: "mk"
source: game-xplane.md
source_hash: "4e7246cce10c"
nav_exclude: true
search_exclude: true
---
# X-Plane (податоци во живо) {#x-plane-live-data}

Додека играте X-Plane, Watcher ги зачувува податоците што ги испраќа самата игра, за подоцна да можете да ги погледнете на мапа во прегледувачот 3DHeat.

*Технички детали: адаптер `xplane`, вид [`telemetry`](sources-and-rules.md); работи додека работи `X-Plane.exe` и бара нови податоци на секои 0,1 s.*

## Што се снима {#what-is-recorded}

- сопствената позиција со 10 Hz (географска ширина/должина/висина како метри исток/нагоре/север од првата положба; lat/lon/alt чувани како колони)
- положба (attitude), indicated и true airspeed, брзина над земја, Mach, вертикална брзина, AoA, странично лизгање, магнетна насока, AGL, g (нормално, аксијално, странично), брзини и стапки на ротација, закрилца, воздушна сопирачка, гас, на земја
- тежини (вкупна, гориво, товар), рачка за стајниот трап, автопилот, вртежи на моторот и N1, време и датум на симулаторот, пауза, брзина на симулацијата, повторување, надворешна температура и притисок на морско ниво (X-Plane 12) еднаш во секунда
- полетувања, слетувања, паѓања, ресетирања на летот (session_start/session_end по лет)
- време на летање, време во воздух, растојание, највисока висина, највисоко g, слетувања
- секој одговор што X-Plane го праќа се чува цело во heat.raw.parquet

## Од каде доаѓа {#where-it-comes-from}

UDP интерфејсот на X-Plane на 127.0.0.1:49000 (RREF datarefs и RPOS позиција, одговорени на Watcher)

## Како да се вклучи {#how-to-switch-it-on}

X-Plane 12: Settings > Network > Accept incoming connections (X-Plane 11 одговара стандардно)

## Како работи {#how-it-works}

X-Plane 11 и 12: сопствениот UDP интерфејс на симулаторот на порта 49000.

X-Plane му одговара на секој што пита на 127.0.0.1:49000, со бараната
брзина, на адресата и портата од која дошло барањето (документот „Exchanging Data with
X-Plane" на X-Plane, испорачан во `<X-Plane>\Instructions\`):

```text
RREF  "RREF\0" + int32 freq + int32 index + char[400] dataref path (413 bytes).
      The answer is "RREF" + one internal byte + (int32 index, float32 value)
      pairs; freq 0 stops it.
RPOS  "RPOS\0" + the rate as a NUL-terminated ASCII string ("10\0"). The
      answer is "RPOS" + one internal byte + double lon, lat, elevation (m
      MSL) + float AGL (m), pitch, true heading, roll (deg), vx east, vy up,
      vz south (m/s), P, Q, R (rad/s), tightly packed.
```

RPOS дава географска ширина и должина како double (RREF само како float, на половина
метар еден од друг), па тој ја води позицијата; RREF го носи остатокот и го заменува кога
RPOS не доаѓа. Datarefs (имиња како во `Resources\plugins\DataRefs.txt` на X-Plane 12,
<https://developer.x-plane.com/datarefs/>):

```text
sim/flightmodel/position/latitude, longitude, elevation  deg, deg, m MSL
sim/flightmodel/position/true_theta, true_phi, true_psi  pitch, roll, true heading (deg)
sim/flightmodel/position/indicated_airspeed              knots
sim/flightmodel/position/groundspeed                     m/s
sim/flightmodel/position/y_agl                           m above ground
sim/flightmodel/forces/g_nrml                            g, normal to the wings
sim/flightmodel/failures/onground_any                    1 on the ground
sim/flightmodel2/misc/has_crashed                        1 crashed
sim/time/total_flight_time_sec                           since the flight was reset
```

и остатокот од летот со истата брзина (true airspeed, вертикална брзина, AoA,
странично лизгање, магнетна насока, Mach, аксијално и странично g, стапки на ротација, закрилца,
воздушна сопирачка, гас: `DATAREFS`), со побавната состојба на авионот еднаш во
секунда (тежини, рачка за стајниот трап, автопилот, мотори, времето на симулаторот, пауза и
брзина, време/метео: `SLOW_DATAREFS`). Секоја дејтаграма се чува и цела во
суровата придружна датотека на сесијата, а meta.json го именува dataref зад секој RREF индекс.

X-Plane 12 ги прифаќа овие само со вклучено Settings > Network > „Accept incoming
connections". Позициите одат во рамна мапа околу првата положба на седењето
(`Tangent`): x исток, z север во метри, y висината над морското ниво - па
рамниот лет останува рамен колку и да оди далеку, што вистинска тангентна рамнина би го
свиткала надолу со земјата. Потеклото на мапата е `geo` на сесијата: meta.json
и подножјето на табелата го носат, за прегледувачот да може да го постави вистинскиот свет под
летот.

Овој модул го содржи и она што другите симулатори на летање го делат: рамната мапа,
водењето на летот (полетувања, слетувања, паѓања, растојание), UDP сокетот и
списокот на библиотеки на Steam.

## Позиции и оски {#positions-and-axes}

| | |
|---|---|
| Позициите се снимаат | да |
| Оска нагоре | `y` |
| Единици | метри (исток, висина, север од првата положба) |
| Огледално за прегледувачот | `z` |
| Размер на единиците (`scale`: прегледувачот ги множи позициите со него) | 1 |

Тие одат во `meta.json` на секоја сесија (`axes`) и, кога сесијата има позиции, во подножјето на `heat.parquet`, па прегледувачот 3DHeat самиот ги врти и размерува редовите - види [Податоците](the-data.md).

## Повеќе играчи {#multiplayer}

- Означено како играно онлајн (`multiplayer`): **не**. `games --markdown` го прикажува ова како „single-player".
- Вид `telemetry`: чита само она што играта или платформата го дава (UDP порта или споделена меморија што играта ја објавува), па снима и во онлајн игра и офлајн; знамето одлучува само дали меморијата смее некогаш да се чита.
- Меморија: овој адаптер **никогаш** не ја чита. Само адаптерите `memory` читаат меморија, и никогаш за игра означена како играна онлајн - види [Извори и правила](sources-and-rules.md).

## Снимена статистика {#statistics-recorded}

Клучевите на статистиката што кодот на овој адаптер ги поставува по име (`stats` во `meta.json` на секоја сесија и табелата `stats` во `watcher.sqlite`):

`airborne_time`, `bad_packets`, `crashes`, `distance_km`, `flight_time`, `max_altitude_m`, `max_g`, `{event}s`

Клуч во загради се дополнува при извршување (`score.{team}` е еден клуч по тим). Клучевите што кодот ги зема од табела со полињата на играта или од сопствените имиња на статистиката на играта не се во овој список; „Што се снима" погоре ги именува.

## Комплетност {#completeness}

Watcher го следи [правилото за конвертори](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md) на 3DHeat: она што го држи изворот се чита или се чува, никогаш не се отфрла. Покрај редовите, секој пакет, страница, линија или одговор што адаптерот ги прима се чува цел во `heat.raw.parquet` на сесијата (колони `time`, `ms`, `type`, `used`, `payload`, `text`, потоа секое поле зачувано по име; `used` означува што станало и редови), а `selfCheck.completeness` во `meta.json` го брои секој `type` - `lost` е 0.

**Читано**

- RPOS (10 Hz): географска должина, ширина, елевација, AGL, pitch, true heading, roll, брзина (исток, нагоре, југ) и стапки на ротација P/Q/R - сè на редовите
- RREF (10 Hz): 27-те datarefs од `DATAREFS` - позиција, положба, IAS, брзина над земја, TAS, вертикална брзина, AoA, странично лизгање, магнетна насока, Mach, g нормално/аксијално/странично, стапки на ротација, закрилца, воздушна сопирачка, гас, AGL, паднат, на земја, време на летање - на редовите
- RREF (1 Hz): 20-те datarefs од `SLOW_DATAREFS` - тежини, рачка за стајниот трап, серво на автопилотот, време и датум на симулаторот, пауза, брзина на симулацијата, повторување, број на мотори, вртежи на моторите 1-4, N1 на моторите 1-2, надворешна температура на воздухот, притисок на морско ниво - на редовите како последно примени

**Чувано сурово**

- секоја дејтаграма цела како `payload`, под своето заглавие од четири букви: `RREF` и `RPOS` (`used` кога анкетата направила ред; во менијата, без положба, не прават ниеден), сè друго што X-Plane го праќа до портата на Watcher под свое заглавие или `unknown`; `requests` во meta.json кажува кој dataref е секој RREF индекс, па payload-ите се читаат и без овој модул

**Не е достапно**

- секој друг dataref (X-Plane има илјадници): RREF праќа само она што е побарано, по една претплата; списокот бара летот, состојбата на авионот и времето на симулаторот - повеќе детали од кабината (радија, светла, мерачите на секој мотор, дефекти) би ги помножиле барањата
- името на авионот и ICAO типот: dataref-и од низи од бајти, кои RREF ги праќа по еден float за знак
- други авиони (AI и повеќе играчи): dataref-ите sim/multiplayer/position не се бараат
- излезот DATA (Settings > Data Output): праќа на фиксна адреса избрана во симулаторот, не на секој што пита; RREF и RPOS го покриваат она што Watcher го чита

**Големина**: околу 17 MB на час пред zstd (RREF и RPOS со 10 Hz, околу 220 и 70 бајти плус рамка секој, побавниот RREF еднаш во секунда), ако X-Plane ги праќа вредностите од секоја анкета во еден пакет како што прави; zstd ги намалува децималните броеви неколкупати

## Проверено {#verified}

тестирано спрема лажен X-Plane што одговара на RREF/RPOS според „Exchanging Data with X-Plane" на X-Plane 12; имињата на dataref-ите проверени спрема DataRefs.txt на X-Plane 12; не е тестирано со симулаторот во работа

## Извор {#source}

[heat3d_watch/adapters/xplane.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/xplane.py)

<!-- Generated from the adapter by tools/gen_game_pages.py; change the adapter and run it again rather than editing this page. -->
