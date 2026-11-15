---
title: "Star Citizen (лог файлове)"
nav_order: 42
lang: "bg"
source: game-starcitizen.md
source_hash: "6528f948d2e5"
nav_exclude: true
search_exclude: true
---
# Star Citizen (лог файлове) {#star-citizen-log-files}

Докато играете Star Citizen, watcher-ът чете файловете, които играта записва, и запазва какво се е случило, за да можете по-късно да го разгледате като статистики и хронология.

*Технически подробности: адаптер `starcitizen`, вид [`log`](sources-and-rules.md); работи, докато `StarCitizen.exe` е стартиран, и търси нови данни на всеки 0.5 s.*

## Какво се записва {#what-is-recorded}

- смъртни случаи с жертва, убиец, оръжие, вид повреда и зона (играчи и NPC)
- превозни средства, извадени от строя и унищожени, с водач, причина и зона
- целите на квантовото пътуване, смени на слънчевата система, появявания, възраждания, обезсилвания
- всеки ред от Game.log цял в heat.raw.parquet
- убийства (на играчи и NPC), смъртни случаи, самоубийства, унищожени и загубени превозни средства, квантови скокове

## Откъде идва {#where-it-comes-from}

&lt;install>\StarCitizen\LIVE\Game.log (папката на сборката на работещия StarCitizen.exe), само файлът с лога, който играта записва - игра с Easy Anti-Cheat: нищо не докосва процеса ѝ

## Как се включва {#how-to-switch-it-on}

Нищо не трябва да се включва: watcher-ът чете източника така, както го предоставя играта или платформата.

## Как работи {#how-it-works}

Star Citizen: собственият лог на клиента, `<install>\StarCitizen\LIVE\Game.log`.

Играта записва Game.log наново при всяко стартиране (предишният отива в
`logbackups\`). Чете се само този файл: Star Citizen използва Easy Anti-Cheat и
нищо тук не се доближава до процеса на играта. Редовете започват с UTC времево клеймо и
ниво, после таг в ъглови скоби:

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

(тук е пренесено на няколко реда; във файла всеки е на един ред). Зоната на смъртен случай обикновено е
корабът, в който е седяла жертвата, а не място. Форматът не е документиран от Cloud
Imperium и се променя между пачовете; шаблоните следват редовете, които четат общностни
проследяващи убийства (напр. <https://github.com/DimmaDont/all-slain>, MIT - само
факти), а всичко, което не съвпада, се пропуска, не се налага да се отгатва. `pos` на превозно средство е
спрямо зоната и се пази само като текст: никакви координати не се рисуват.

Всеки ред се пази цял в суровата странична част на сесията (правилото за конвертори на 3DHeat),
съвпаднал или не: `type` е tagът на реда в ъглови скоби (`Actor
Death`, `Spawn Flow`, ...), иначе първата дума в скоби (`Notice`,
`CSessionManager::OnClientSpawned`), иначе `untagged`; ред без
времево клеймо е `untimed`.

## Позиции и оси {#positions-and-axes}

| | |
|---|---|
| Записват се позиции | не |
| Вертикална ос | `y` |
| Мерни единици | без записани позиции |
| Огледално за визуализатора | няма |
| Мащаб на единицата (`scale`: визуализаторът умножава позициите по него) | 1 |

Те отиват в `meta.json` на всяка сесия (`axes`) и, когато сесията има позиции, в края на `heat.parquet`, така че визуализаторът на 3DHeat сам завърта и мащабира редовете - вижте [Данните](the-data.md).

## Онлайн игра {#multiplayer}

- Отбелязано като играно онлайн (`multiplayer`): **да**. `games --markdown` показва това като "разрешено (чете само това, което играта публикува)".
- Вид `log`: чете само това, което играта или платформата предоставят (файлове, които играта записва, докато работи), затова записва и в онлайн игра, както и офлайн; флагът решава само дали паметта изобщо може да се чете.
- Памет: адаптерът **никога** не чете паметта. Само адаптерите от вид `memory` четат памет, и никога за игра, отбелязана като играна онлайн - вижте [Източници и правила](sources-and-rules.md).

## Записвани статистики {#statistics-recorded}

Ключовете на статистиките, които кодът на този адаптер задава по име (`stats` на всяка сесия в `meta.json` и таблицата `stats` в `watcher.sqlite`):

`bad_lines`, `deaths`, `incapacitations`, `kills`, `npc_kills`, `player_kills`, `quantum_jumps`, `suicides`, `system_jumps`, `vehicles_destroyed`, `vehicles_lost`

Ключ във фигурни скоби се довършва по време на работа (`score.{team}` е по един ключ за всеки отбор). Ключовете, които кодът взема от таблица с полетата на играта или от собствените имена на статистиките ѝ, не са в този списък; "Какво се записва" по-горе ги посочва.

## Пълнота {#completeness}

Watcher-ът следва [правилото за конвертори](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md) на 3DHeat: това, което източникът съдържа, се чете или се пази, никога не се изхвърля. Освен редовете, всеки пакет, страница, ред или отговор, който адаптерът получава, се пази цял в `heat.raw.parquet` на сесията (колони `time`, `ms`, `type`, `used`, `payload`, `text` и всяко поле, запазено по име; `used` отбелязва какво е станало и на редове), а `selfCheck.completeness` в `meta.json` брои всеки `type` - `lost` е 0.

**Чете се**

- `<Actor Death>`: жертва, убиец, оръжие и неговият клас, вид повреда, зона; NPC или играч
- `<Vehicle Destruction>`: превозно средство, зона, позиция спрямо зоната като текст, водач, причина, начин, ниво на унищожение
- целите на `<Quantum Navtarget>`, `<Changing Solar System>`, `OnClientSpawned`, възраждания в болница, обезсилвания с техните причини, `EndSession`
- псевдонимът на играча от `<AccountLoginCharacterStatus_Character>` или реда за вход

**Пази се сурово**

- всеки ред от Game.log цял, `type` = неговият таг в ъглови скоби (`Actor Death`, `Vehicle Destruction`, `Spawn Flow`, `Jump Drive State Changed`, `SHUDEvent_OnNotification`, `RequestLocationInventory`, ...), иначе първата дума в скоби (`Notice`, `CSessionManager::OnClientSpawned`, ...), иначе `untagged`; редове без времево клеймо (заглавната част на лога, пренесен текст) като `untimed`; `used` там, където редът е станал ред

**Не е налично**

- позиции: логът не дава такава в кадър, който може да се нарисува (`pos` на унищожено превозно средство е спрямо зона, чието място не се записва)
- нищо от процеса или мрежата на играта: Star Citizen използва Easy Anti-Cheat; чете се само файлът с лога
- логове от по-ранни стартирания (`logbackups`): Game.log на всяко стартиране се пази, когато то е било играно
- редове във формат, който пачът променя: пазят се сурово и се декодират отново, когато новата форма е известна

**Размер**: Game.log расте с около 5-15 MB на час игра (повече в натоварени зони и при грешки); zstd в heat.raw.parquet го свива приблизително до една десета

## Проверено {#verified}

тествано на синтетични редове от Game.log във формата, документиран от общностните проследяващи; не е тествано срещу самата игра

## Източник {#source}

[heat3d_watch/adapters/starcitizen.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/starcitizen.py)

<!-- Generated from the adapter by tools/gen_game_pages.py; change the adapter and run it again rather than editing this page. -->
