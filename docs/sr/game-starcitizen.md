---
title: "Star Citizen (фајлови дневника)"
nav_order: 42
lang: "sr"
source: game-starcitizen.md
source_hash: "6528f948d2e5"
nav_exclude: true
search_exclude: true
---
# Star Citizen (фајлови дневника) {#star-citizen-log-files}

Док играте Star Citizen, watcher чита фајлове које игра пише и чува шта се дешавало, да бисте то касније погледали као статистику и временску линију.

*Технички подаци: адаптер `starcitizen`, врста [`log`](sources-and-rules.md); ради док је `StarCitizen.exe` покренут и тражи нове податке сваких 0,5 s.*

## Шта се бележи {#what-is-recorded}

- смрти са жртвом, убицом, оружјем, врстом штете и зоном (играчи и NPC-јеви)
- возила онеспособљена и уништена, са возачем, узроком и зоном
- циљеви квантног путовања, промене соларног система, појављивања, поновна појављивања, онеспособљавања
- сваки ред Game.log-а цео у heat.raw.parquet
- убиства (играч и NPC), смрти, самоубиства, уништена и изгубљена возила, квантни скокови

## Одакле долазе подаци {#where-it-comes-from}

&lt;install>\StarCitizen\LIVE\Game.log (фасцикла верзије покренутог StarCitizen.exe), само фајл дневника који игра пише - игра са Easy Anti-Cheat-ом: ништа не дира њен процес

## Како га укључити {#how-to-switch-it-on}

Ништа не треба укључивати: watcher чита извор онако како га игра или платформа даје.

## Како ради {#how-it-works}

Star Citizen: сопствени дневник клијента, `<install>\StarCitizen\LIVE\Game.log`.

Игра Game.log пише испочетка при сваком покретању (претходни иде у `logbackups\`). Чита се само тај фајл: Star Citizen користи Easy Anti-Cheat, а ово ни на који начин не дира процес игре. Редови почињу UTC ознаком времена и нивоом, затим ознаком у угластим заградама:

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

(прелом је овде ради приказа; у фајлу је сваки ред у једном реду). Зона смрти је обично брод у којем је жртва сједила, а не место. Формат Cloud Imperium не документује и мијења се између закрпа; обрасци прате редове које читају алатке заједнице за праћење убистава (нпр. <https://github.com/DimmaDont/all-slain>, MIT - само чињенице), а све што се не поклапа прескаче се, не погађа се. `pos` возила је релативан у односу на зону и чува се само као текст: ниједна координата се не црта.

Сваки ред се чува цео у сировом прилогу сесије (правило конвертера у 3DHeat-у), било да се поклапа или не: `type` је ознака реда у угластим заградама (`Actor Death`, `Spawn Flow`, ...), иначе његова прва реч у заградама (`Notice`, `CSessionManager::OnClientSpawned`), иначе `untagged`; ред без ознаке времена је `untimed`.

## Положаји и осе {#positions-and-axes}

| | |
|---|---|
| Положаји се бележе | не |
| Оса горе | `y` |
| Јединице | положаји се не бележе |
| Огледање за прегледач | нема |
| Размера јединица (`scale`: прегледач помножи положаје с њом) | 1 |

Ово иде у `meta.json` сваке сесије (`axes`) и, када сесија има положаје, у подножје `heat.parquet`, па 3DHeat прегледач сам окреће и размењује редове - видите [Подаци](the-data.md).

## Више играча {#multiplayer}

- Означено као игра на мрежи (`multiplayer`): **да**. `games --markdown` то приказује као „дозвољено (чита само оно што игра објављује)”.
- Врста `log`: чита само оно што игра или платформа даје (фајлови које игра пише док ради), па снима и у мрежној игри и ван ње; ознака одлучује само о томе смије ли се икад читати меморија.
- Меморија: овај адаптер је **никада** не чита. Само адаптери врсте `memory` читају меморију, и никад за игру означену као мрежну - видите [Извори и правила](sources-and-rules.md).

## Забиљежена статистика {#statistics-recorded}

Кључеви статистике које код овог адаптера поставља по имену (свака `stats` сесија у `meta.json` и табела `stats` у `watcher.sqlite`):

`bad_lines`, `deaths`, `incapacitations`, `kills`, `npc_kills`, `player_kills`, `quantum_jumps`, `suicides`, `system_jumps`, `vehicles_destroyed`, `vehicles_lost`

Кључ у витичастим заградама се допуњује у време рада (`score.{team}` је један кључ по тиму). Кључеви које код узима из табеле поља игре или из имена статистике саме игре нису на овом списку; „Шта се бележи” горе их именује.

## Потпуност {#completeness}

Watcher прати [правило конвертера](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md) из 3DHeat-а: оно што извор садржи се чита или чува, никад се не одбацује. Осим редова, сваки пакет, страница, ред или одговор које адаптер прими чува се цео у `heat.raw.parquet` сесије (колоне `time`, `ms`, `type`, `used`, `payload`, `text`, па свако поље које се чува по имену; `used` означава оно што је постало редови), а `selfCheck.completeness` у `meta.json` броји сваки `type` - `lost` је 0.

**Чита се**

- `<Actor Death>`: жртва, убица, оружје и његова класа, врста штете, зона; NPC или играч
- `<Vehicle Destruction>`: возило, зона, положај релативан у зони као текст, возач, узрок, начин, ниво уништења
- циљеви из `<Quantum Navtarget>`, `<Changing Solar System>`, `OnClientSpawned`, поновна појављивања у болници, онеспособљавања са својим узроцима, `EndSession`
- играчев ид из `<AccountLoginCharacterStatus_Character>` или реда за пријаву

**Чува се сирово**

- сваки ред Game.log-а цео, `type` = његова ознака у угластим заградама (`Actor Death`, `Vehicle Destruction`, `Spawn Flow`, `Jump Drive State Changed`, `SHUDEvent_OnNotification`, `RequestLocationInventory`, ...), иначе његова прва реч у заградама (`Notice`, `CSessionManager::OnClientSpawned`, ...), иначе `untagged`; редови без ознаке времена (заглавље дневника, прелом текста) као `untimed`; `used` тамо где је ред постао ред

**Није доступно**

- положаји: дневник их не даје ни у једном кадру који се може нацртати (`pos` уништеног возила је релативан у односу на зону чије место није забиљежено)
- било шта из процеса или мреже игре: Star Citizen користи Easy Anti-Cheat; чита се само фајл дневника
- дневници ранијих покретања (`logbackups`): Game.log сваког покретања се чува кад се одигра
- редови у формату који закрпа мијења: чувају се сирово и декодују се поново кад се нови облик зна

**Величина**: Game.log расте 5-15 MB на сат игре (више у гужвама и уз грешке); zstd у heat.raw.parquet га смањи на око десетину

## Провјерено {#verified}

тестирано на синтетичким редовима Game.log-а у формату који документују алатке заједнице; није тестирано са игром

## Извор {#source}

[heat3d_watch/adapters/starcitizen.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/starcitizen.py)

<!-- Generated from the adapter by tools/gen_game_pages.py; change the adapter and run it again rather than editing this page. -->
