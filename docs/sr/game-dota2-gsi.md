---
title: "Dota 2 (стање игре)"
nav_order: 13
lang: "sr"
source: game-dota2-gsi.md
source_hash: "100a0d704bbe"
nav_exclude: true
search_exclude: true
---
# Dota 2 (стање игре) {#dota-2-game-state}

Док играте Dota 2, посматрач чува оно што игра јавља програмима на вашем рачунару, па то касније можете да погледате на мапи у 3DHeat приказивачу.

*Технички детаљи: адаптер `dota2-gsi`, врста [`gsi`](sources-and-rules.md); ради док је `dota2.exe` покренут и тражи нове податке сваких 0,05 s.*

## Шта се снима {#what-is-recorded}

- положај вашег хероја (светске X/Y координате у Dota јединицама; нема висине) док је жив
- појављивање, смрти (са временом до поновног појављивања) и поновна појављивања вашег хероја
- убиства, из раста броја убистава
- уништене зграде, Roshan, догађаји игре (roshan_killed, aegis_picked_up, ...), стања игре, исход
- убиства, смрти, асистенције, last hits, denies, злато, GPM, XPM, ниво, херој

## Одакле долази {#where-it-comes-from}

Game State Integration: HTTP POST захтеви на 127.0.0.1:3312, подешени датотеком &lt;Dota>\game\dota\cfg\gamestate_integration\gamestate_integration_heat3d.cfg

## Како се укључује {#how-to-switch-it-on}

`python -m heat3d_watch setup dota2-gsi --apply`, па покрените Dota 2 (игра датотеку чита при покретању)

Команду укуцајте у терминалу отвореном у фасцикли посматрача (видите [Пре почетка](before-you-start.md)). Ако не успе, последњи ред каже зашто; [Инсталација и покретање](installing-and-running.md) описује уобичајене узроке.

`python -m heat3d_watch setup dota2-gsi` наводи датотеке које би променио; `python -m heat3d_watch setup dota2-gsi --apply` их мења и чува оригинал као `<file>.heat3d-backup` (видите [Команде](commands.md#setup)). За сваку промену исписује `dota2-gsi: changed: ...`, или `dota2-gsi: nothing to change` кад је већ укључено.

Подешавања из променљивих окружења:

- `HEAT3D_DOTA_GSI_PORT`: порт на који игра шаље податке (подразумевано 3312); датотека cfg у игри мора да наведе исти порт

## Како ради {#how-it-works}

Valve Game State Integration: Counter-Strike 2 и Dota 2 јављају локалном веб серверу шта се дешава.

Обе игре читају сваки `gamestate_integration_*.cfg` у својој cfg фасцикли кад се покрену, и од тада шаљу JSON документ на `uri` сваке датотеке кад се стање промени (највише једном на `throttle` секунди, и на сваких `heartbeat` секунди кад се ништа не промени). Посматрач је тај веб сервер: слуша само на 127.0.0.1, одмах одговара на сваки POST са 200 и посао обавља у својој нити за проверу.

```text
Counter-Strike 2  <CS2>\game\csgo\cfg\gamestate_integration_heat3d.cfg      порт 3311
Dota 2            <Dota>\game\dota\cfg\gamestate_integration\gamestate_integration_heat3d.cfg   порт 3312
```

Шта се шаље играчу - а тиме и шта се може снимити - одлучује игра, по томе шта играчу сме да види:

- CS2: `provider` (ваш steamid), `map` (име, режим, фаза warmup/live/intermission/gameover, круг, резултат team_ct/team_t), `round` (фаза freezetime/live/over, бомба planted/exploded/defused, win_team), `player` (играч кога *гледате*: ви док сте живи, саиграч после смрти) са `state` (здравље, оклоп, новац, round_kills, round_killhs, round_totaldmg), `match_stats` (убиства, асистенције, смрти, mvps, резултат), `position` и `forward` као низови "x, y, z" у светским јединицама (инчи, Z нагоре), `weapons`; `bomb` само за посматраче. Положаји осталих играча (`allplayers_*`) шаљу се само посматрачима и GOTV-у, па се не траже.
- Dota 2: `map` (matchid, game_state, game_time, clock_time, win_team), `player` (kills, deaths, assists, last_hits, denies, gold, gpm, xpm, team_name), `hero` (xpos/ypos у светским јединицама, level, alive, respawn_seconds), `buildings` (здравље по торњу/касарни/древном), `roshan`, `events` (roshan_killed, aegis_picked_up, ...). Висине нема: z је 0. Тражи се и чува цело још: `abilities`, `items`, `draft`, `wearables`, `minimap`, `couriers`, `neutralitems`, `league` (игра шаље оно што има играчев клијент; које од њих нешто садрже док се игра, а не гледа, није проверено).

Сваки документ се чува и цео (правило конвертера 3DHeat-а, docs/converters.md у репозиторијуму приказивача): `heat.raw.parquet`, `type` "gsi", `text` је JSON онако како је послат - само токен из cfg датотеке је избрисан, јер је то тајна посматрача, а не подаци игре. Документи послати док није отворен ниједан меч (менији, учитавање, између мечева) чекају у `Backlog` и иду у сесију следећег меча, пре његовог почетка; што остане кад се игра затвори, добија сесију за себе која садржи само њих. Неочитљиве поруке и поруке с погрешним токеном такође се чувају ("gsi-unreadable", "gsi-bad-auth").

Извори: <https://developer.valvesoftware.com/wiki/Counter-Strike:_Global_Offensive_Game_State_Integration>
(формат који је CS2 задржао), <https://github.com/antonpup/CounterStrike2GSI> и
<https://github.com/antonpup/Dota2GSI> (спискови поља; MIT, коришћени само због чињеница).

Исти модул служи и: [Counter-Strike 2 (стање игре)](game-cs2-gsi.md).

## Положаји и осе {#positions-and-axes}

| | |
|---|---|
| Положаји се бележе | да |
| Оса нагоре | `z` |
| Јединице | Dota светске јединице (z је увек 0) |
| Огледално за приказивач | `y` |
| Размера јединице (`scale`: приказивач множи положаје њом) | 1 |

Ово иде у `meta.json` сваке сесије (`axes`) и, кад сесија има положаје, у подножје `heat.parquet`-а, па 3DHeat приказивач сам окреће и скалира редове - видите [Подаци](the-data.md).

## Више играча {#multiplayer}

- Означено као игра на мрежи (`multiplayer`): **да**. `games --markdown` ово приказује као "allowed (reads only what the game publishes)".
- Врста `gsi`: чита само оно што игра или платформа даје (game-state integration или локални API који игра служи), па снима и у мрежној игри и ван ње; ознака одлучује само да ли се меморија икад сме читати.
- Меморија: **никад** се не чита овим адаптером. Само адаптери `memory` читају меморију, и никад за игру означену као игру на мрежи - видите [Извори и правила](sources-and-rules.md).

## Снимљена статистика {#statistics-recorded}

Кључеви статистике које код овог адаптера поставља по имену (`stats` сваке сесије у `meta.json` и табела `stats` у `watcher.sqlite`):

`bad_auth`, `bad_packets`, `dropped_packets`, `hero`, `level`, `result`, `roshan_kills_seen`

Кључ у витичастим заградама се допуњује за време рада (`score.{team}` је један кључ по тиму). Кључеви које код узима из табеле поља игре или из назива статистике саме игре нису у овом списку; "Шта се снима" горе их наводи.

## Потпуност {#completeness}

Посматрач следи [правило конвертера](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md) 3DHeat-а: оно што извор садржи се чита или чува, никад не одбацује. Осим редова, сваки пакет, страница, линија или одговор који адаптер прими чува се цео у `heat.raw.parquet` сесије (колоне `time`, `ms`, `type`, `used`, `payload`, `text`, па свако поље које се чува по имену; `used` означава оно што је постало и редови), а `selfCheck.completeness` у `meta.json`-у броји сваки `type` - `lost` је 0.

**Чита се**

- положај вашег хероја (x/y), да ли је жив, ниво, здравље, максимално здравље, мана, максимална мана; појављивање, смрти са временом до поновног појављивања, поновна појављивања
- убиства (кад број убистава расте); убиства, смрти, асистенције, last hits, denies, злато, GPM, XPM, нето вредност, ниво и херој као статистика
- уништене зграде, Roshan оборен и враћен, сваки унос из `events` једном, стања игре, победник

**Чува се сирово**

- `gsi`: сваки документ који игра шаље, цео, онако како је послат (`text`), `used` је тачно кад је прочитан у мечу - свих петнаест компоненти које cfg датотека тражи: provider, map (дан/ноћ, паузиран, време хлађења чуварница, резултати), player (поуздано и непоуздано злато, низови, листа убистава, издате команде, ...), hero (бафови, таленти, Aghanim-ови, атрибути), abilities, items, buildings, roshan, events, draft, wearables, minimap, couriers, neutralitems, league, и `previously`/`added` разлику игре
- документи из менија, учитавања и између мечева: чувају се на исти начин, у свом времену пре почетка следећег меча; после последњег меча, у сопственој сесији (`raw_only` у meta.json)
- `gsi-unreadable`: POST који није JSON објекат, са његовим бајтовима као `payload` и `length`
- `gsi-bad-auth`: POST са другим токеном од оног из cfg датотеке

**Није доступно**

- висина: игра шаље само x и y
- други хероји док се игра: игра шаље вашег хероја, а сваког играча само посматрачима (тада се чува сирово, не црта се); неколико компоненти (draft, minimap, couriers) садржи само оно што има играчев клијент - а то, док се игра, није проверено
- стања између POST-ова: највише један на 0,1 s (`throttle`), на сваких 10 s кад се ништа не мења
- токен из cfg датотеке, избрисан у сваком сачуваном документу: тајна посматрача, а не подаци игре
- POST-ови преко 10.000 на чекању (посматрач је застао) броје се као `dropped_packets` и не чувају се; POST већи од 4 MB чува се као `gsi-unreadable` са дужином, али без бајтова

**Величина**: са свим компонентама документ играча има око 5-15 KB и шаље се до 10 пута у секунди (сат се мења при сваком POST-у): око 100-500 MB по сату у `raw.bin` док меч траје, а отприлике десетину у zstd `heat.parquet`; документ посматрача, са свим играчима и minimap-ом, је неколико пута већи (процена из објављеног формата, није мерено на игри)

## Проверено {#verified}

проверено на документима у објављеном GSI формату послатим покренутом адаптеру; није проверено на покренутој игри

## Извор {#source}

[heat3d_watch/adapters/gsi.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/gsi.py)

<!-- Generated from the adapter by tools/gen_game_pages.py; change the adapter and run it again rather than editing this page. -->
