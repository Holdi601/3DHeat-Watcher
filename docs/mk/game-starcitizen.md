---
title: "Star Citizen (лог-датотеки)"
nav_order: 42
lang: "mk"
source: game-starcitizen.md
source_hash: "6528f948d2e5"
nav_exclude: true
search_exclude: true
---
# Star Citizen (лог-датотеки) {#star-citizen-log-files}

Додека играте Star Citizen, Watcher ги чита датотеките што ги пишува играта и зачувува што се случило, за подоцна да можете да го погледнете како статистика и временска лента.

*Технички детали: адаптер `starcitizen`, вид [`log`](sources-and-rules.md); работи додека работи `StarCitizen.exe` и бара нови податоци на секои 0,5 s.*

## Што се снима {#what-is-recorded}

- смрти со жртва, убиец, оружје, вид на штета и зона (играчи и NPC)
- оневозможени и уништени возила, со возач, причина и зона
- цели на квантно патување, промени на соларен систем, појавувања, повторни појавувања, онесвестувања
- секоја линија од Game.log цела во heat.raw.parquet
- убиства (на играчи и NPC), смрти, самоубиства, уништени и изгубени возила, квантни скокови

## Од каде доаѓа {#where-it-comes-from}

&lt;install>\StarCitizen\LIVE\Game.log (папката на изданието на StarCitizen.exe што работи), само датотеката со лог што ја пишува играта - игра со Easy Anti-Cheat: ништо не го допира нејзиниот процес

## Како да се вклучи {#how-to-switch-it-on}

Ништо не треба да се вклучува: Watcher го чита изворот онака како што го дава играта или платформата.

## Како работи {#how-it-works}

Star Citizen: сопствениот лог на клиентот, `<install>\StarCitizen\LIVE\Game.log`.

Играта го пишува Game.log одново при секое стартување (претходниот оди во
`logbackups\`). Се чита само таа датотека: Star Citizen работи со Easy Anti-Cheat, и
ништо тука не се приближува до процесот на играта. Линиите почнуваат со UTC време и
ниво, потоа таг во аголни загради:

```text
<2025-04-13T17:17:51.279Z> [Notice] <Actor Death> CActor::Kill: 'Victim' [200146297631] in zone
    'ANVL_Hornet_F7A_Mk2_2677329226210' killed by 'Killer' [202061381370] using
    'GATS_BallisticGatling_S3_2677329225797' [Class unknown] with damage type 'VehicleDestruction'
    from direction x: 0.000000, y: 0.000000, z: 0.000000 [Team_ActorTech][Actor]
<...> [Notice] <Vehicle Destruction> CVehicle::OnAdvanceDestroyLevel: Vehicle 'ANVL_Arrow_123' [123] in zone
    'OOC_Stanton_1_Hurston' [pos x: 1.0, y: 2.0, z: 3.0 vel x: 0, y: 0, z: 0] driven by 'Driver' [456]
    advanced from destroy level 0 to 2 caused by 'Attacker' [789] with 'Combat' [Team_VehicleFeatures][Vehicle]
<...> [Notice] <AccountLoginCharacterStatus_Character> Character: createdAt 1 - updatedAt 2 - geid 3 -
    accountId 4 - name Handle - state STATE_CURRENT [Team_GameServices][Login]
<...> [Notice] <Quantum Navtarget> CSCItemQuantumDrive::RmMulticastOnQTToPoint : Local client user
    Handle[200000000001] received QT data for Entity:AEGS_Gladius_123[123] to Target Stanton1b ...
<...> [Notice] <Changing Solar System> ... Client entity Handle ... changing system from Stanton to Pyro ...
```

(тука преломено; по една линија во датотеката). Зоната на смртта обично е
бродот во кој седела жртвата, не место. Форматот не е документиран од Cloud
Imperium и се менува меѓу закрпите; шаблоните ги следат линиите што ги читаат
следачите на убиства од заедницата (на пр. <https://github.com/DimmaDont/all-slain>, MIT - само
факти), а сè што не се совпаѓа се прескокнува, не се погодува. `pos` на возилото
е релативно на зоната и се чува само како текст: не се цртаат координати.

Секоја линија се чува цела во суровата датотека на сесијата (правилото на
конверторите на 3DHeat), совпаднала или не: `type` е тагот на линијата во аголни загради (`Actor
Death`, `Spawn Flow`, ...), инаку првиот збор во загради (`Notice`,
`CSessionManager::OnClientSpawned`), инаку `untagged`; линија без
време е `untimed`.

## Позиции и оски {#positions-and-axes}

| | |
|---|---|
| Позициите се снимаат | не |
| Оска нагоре | `y` |
| Единици | не се снимаат позиции |
| Огледално за прегледувачот | нема |
| Размер на единиците (`scale`: прегледувачот ги множи позициите со него) | 1 |

Тие одат во `meta.json` на секоја сесија (`axes`) и, кога сесијата има позиции, во подножјето на `heat.parquet`, па прегледувачот 3DHeat самиот ги врти и размерува редовите - види [Податоците](the-data.md).

## Повеќе играчи {#multiplayer}

- Означено како играно онлајн (`multiplayer`): **да**. `games --markdown` го прикажува ова како „allowed (reads only what the game publishes)".
- Вид `log`: чита само она што играта или платформата го дава (датотеки што играта ги пишува додека работи), па снима и во онлајн игра и офлајн; знамето одлучува само дали меморијата смее некогаш да се чита.
- Меморија: овој адаптер **никогаш** не ја чита. Само адаптерите `memory` читаат меморија, и никогаш за игра означена како играна онлајн - види [Извори и правила](sources-and-rules.md).

## Снимена статистика {#statistics-recorded}

Клучевите на статистиката што кодот на овој адаптер ги поставува по име (`stats` во `meta.json` на секоја сесија и табелата `stats` во `watcher.sqlite`):

`bad_lines`, `deaths`, `incapacitations`, `kills`, `npc_kills`, `player_kills`, `quantum_jumps`, `suicides`, `system_jumps`, `vehicles_destroyed`, `vehicles_lost`

Клуч во загради се дополнува при извршување (`score.{team}` е еден клуч по тим). Клучевите што кодот ги зема од табела со полињата на играта или од сопствените имиња на статистиката на играта не се во овој список; „Што се снима" погоре ги именува.

## Комплетност {#completeness}

Watcher го следи [правилото за конвертори](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md) на 3DHeat: она што го држи изворот се чита или се чува, никогаш не се отфрла. Покрај редовите, секој пакет, страница, линија или одговор што адаптерот ги прима се чува цел во `heat.raw.parquet` на сесијата (колони `time`, `ms`, `type`, `used`, `payload`, `text`, потоа секое поле зачувано по име; `used` означува што станало и редови), а `selfCheck.completeness` во `meta.json` го брои секој `type` - `lost` е 0.

**Читано**

- `<Actor Death>`: жртва, убиец, оружје и неговата класа, вид на штета, зона; NPC или играч
- `<Vehicle Destruction>`: возило, зона, позиција релативна на зоната како текст, возач, причина, како, ниво на уништување
- цели од `<Quantum Navtarget>`, `<Changing Solar System>`, `OnClientSpawned`, повторни појавувања во болница, онесвестувања со нивните причини, `EndSession`
- ознаката на играчот од `<AccountLoginCharacterStatus_Character>` или од линијата за најава

**Чувано сурово**

- секоја линија од Game.log цела, `type` = нејзиниот таг во аголни загради (`Actor Death`, `Vehicle Destruction`, `Spawn Flow`, `Jump Drive State Changed`, `SHUDEvent_OnNotification`, `RequestLocationInventory`, ...), инаку првиот збор во загради (`Notice`, `CSessionManager::OnClientSpawned`, ...), инаку `untagged`; линии без време (заглавието на логот, прекршен текст) како `untimed`; `used` каде што линијата станала ред

**Не е достапно**

- позиции: логот не дава такви во рамка што може да се нацрта (`pos` на уништено возило е релативно на зона чие место не е запишано)
- сè од процесот или мрежата на играта: Star Citizen работи со Easy Anti-Cheat; се чита само датотеката со лог
- логови од претходни стартувања (`logbackups`): Game.log на секое стартување се чува кога се игра
- линии во формат што го менува закрпа: чувани сурови, повторно декодирани штом ќе се знае новата форма

**Големина**: Game.log расте околу 5-15 MB на час игра (повеќе во зафатени подрачја и со грешки); zstd во heat.raw.parquet го прави приближно десеттина од тоа

## Проверено {#verified}

тестирано на синтетички линии од Game.log во форматот што го документираат следачите на заедницата; не е тестирано со играта

## Извор {#source}

[heat3d_watch/adapters/starcitizen.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/starcitizen.py)

<!-- Generated from the adapter by tools/gen_game_pages.py; change the adapter and run it again rather than editing this page. -->
