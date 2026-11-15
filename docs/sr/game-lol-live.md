---
title: "League of Legends (стање игре)"
nav_order: 29
lang: "sr"
source: game-lol-live.md
source_hash: "75c67c6fe84f"
nav_exclude: true
search_exclude: true
---
# League of Legends (стање игре) {#league-of-legends-game-state}

Док играте League of Legends, watcher чува оно што игра извештава програмима на вашем рачунару, да бисте то касније погледали као статистику и временску линију.

*Технички подаци: адаптер `lol-live`, врста [`gsi`](sources-and-rules.md); ради док је `League of Legends.exe` покренут и тражи нове податке сваких 0,5 s.*

## Шта се бележи {#what-is-recorded}

- без положаја: API их нема
- фид убистава: убиства, смрти и асистенције играча, убиства других шампиона са убицом, жртвом и асистентима
- змајеви, хералди, бародови, торњеви, инхибитори, вишеструка убиства, aces, први крв, почетак и крај игре
- сопствена убиства, смрти, асистенције, резултат крипова, резултат чуварства, ниво, злато, шампион, време игре, исход
- циљеви које је узео тим играча

## Одакле долазе подаци {#where-it-comes-from}

Live Client Data API клијента игре, <https://127.0.0.1:2999/liveclientdata/> (allgamedata, eventdata), током утакмице

## Како га укључити {#how-to-switch-it-on}

Ништа не треба укључивати: watcher чита извор онако како га игра или платформа даје.

## Како ради {#how-it-works}

League of Legends: Live Client Data API који клијент игре служи током утакмице.

Док утакмица траје (и у тренинг алату и у режиму посматрача), `League of
Legends.exe` одговара на <https://127.0.0.1:2999> оним што играч може да види у самој
сучељу игре:

```text
/liveclientdata/allgamedata          activePlayer (riotId, level, currentGold, championStats),
                                     allPlayers (championName, team ORDER/CHAOS, level,
                                     scores: kills, deaths, assists, creepScore, wardScore),
                                     events, gameData (gameMode, gameTime s, mapName)
/liveclientdata/eventdata?eventID=N  {"Events": [...]} од EventID N: GameStart,
                                     MinionsSpawning, FirstBlood, FirstBrick, TurretKilled,
                                     InhibKilled, InhibRespawningSoon, InhibRespawned,
                                     DragonKill, HeraldKill, BaronKill, ChampionKill
                                     (KillerName, VictimName, Assisters), Multikill
                                     (KillStreak), Ace (Acer, AcingTeam), GameEnd (Result)
```

Положаја нема: API их нема, па је League сесија догађаји и статистика, без табеле положаја. Сертификат је самопотписан, по Riot-овом сопственом корену (`riotgames.pem`, објављен на <https://static.developer.riotgames.com/docs/lol/riotgames.pem>). Услови његове употребе нису наведени, па се не испоручује: ставите га у `<data>\riotgames.pem` и веза се проверава помоћу њега; без њега провјера је искључена - и то само за 127.0.0.1, једину адресу с којом адаптер разговара.

Riot-ова политика дозвољава алаткама да прикажу оно што играч може да зна из саме игре, и ништа израчунато преко тога (нема непријатељских тајмера): ово бележи фид убистава и резултатску табелу коју играч види, и бројеве самог играча.

Сваки одговор се такође чува цео (правило конвертера у 3DHeat-у, docs/converters.md у репозиторијуму прегледача): `heat.raw.parquet`, `type` је крајња тачка („allgamedata”, „eventdata”), `text` је JSON онако како га је клијент послао, `status` кад није 200. Одговор који је бајт за бајт исти као претходни исте крајње тачке (листа догађаја док се ништа не дешава) чува се једном и броји се у `unchanged_replies` у meta.json. allgamedata садржи све што остале крајње тачке служе (activeplayer\*, playerlist, playerscores, playeritems, playersummonerspells, playermainrunes, gamestats), па се оне не траже посебно. Одговори пре утакмице (екран учитавања) чекају у залеђу и иду у сесију утакмице; после GameEnd сесија остаје отворена док клијент не оде, па се одговори екрана на крају чувају уз њу.

Извор: <https://developer.riotgames.com/docs/lol#game-client-api>

## Положаји и осе {#positions-and-axes}

| | |
|---|---|
| Положаји се бележе | не |
| Оса горе | `z` |
| Јединице | нема (нема положаја) |
| Огледање за прегледач | нема |
| Размера јединица (`scale`: прегледач помножи положаје с њом) | 1 |

Ово иде у `meta.json` сваке сесије (`axes`) и, када сесија има положаје, у подножје `heat.parquet`, па 3DHeat прегледач сам окреће и размењује редове - видите [Подаци](the-data.md).

## Више играча {#multiplayer}

- Означено као игра на мрежи (`multiplayer`): **да**. `games --markdown` то приказује као „дозвољено (чита само оно што игра објављује)”.
- Врста `gsi`: чита само оно што игра или платформа даје (интеграцију стања игре или локални API који игра служи), па снима и у мрежној игри и ван ње; ознака одлучује само о томе смије ли се икад читати меморија.
- Меморија: овај адаптер је **никада** не чита. Само адаптери врсте `memory` читају меморију, и никад за игру означену као мрежну - видите [Извори и правила](sources-and-rules.md).

## Забиљежена статистика {#statistics-recorded}

Кључеви статистике које код овог адаптера поставља по имену (свака `stats` сесија у `meta.json` и табела `stats` у `watcher.sqlite`):

`bad_packets`, `champion`, `game_time`, `gold`, `level`, `result`

Кључ у витичастим заградама се допуњује у време рада (`score.{team}` је један кључ по тиму). Кључеви које код узима из табеле поља игре или из имена статистике саме игре нису на овом списку; „Шта се бележи” горе их именује.

## Потпуност {#completeness}

Watcher прати [правило конвертера](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md) из 3DHeat-а: оно што извор садржи се чита или чува, никад се не одбацује. Осим редова, сваки пакет, страница, ред или одговор које адаптер прими чува се цео у `heat.raw.parquet` сесије (колоне `time`, `ms`, `type`, `used`, `payload`, `text`, па свако поље које се чува по имену; `used` означава оно што је постало редови), а `selfCheck.completeness` у `meta.json` броји сваки `type` - `lost` је 0.

**Чита се**

- фид убистава из eventdata: сваки догађај једном, са декодованим именованим пољима (убица, жртва и асистенти са шампионом и тимом, објекти и њихова страна, врста змаја, украђени циљеви, вишеструка убиства, aces, први крв, исход), а свако друго поље догађаја на његовом реду под својим именом
- из allgamedata: сопствена убиства, смрти, асистенције, резултат крипова, резултат чуварства, ниво, злато, шампион, време игре, мод и мапа игре

**Чува се сирово**

- `allgamedata`: сваки одговор цео (`text`), на сваке 2 s - activePlayer (способности, свака статистика шампиона, све руне, злато, ниво), allPlayers (предмети са слотовима и ценама, руне, призивачке чини, резултати, ниво, мртав и тајмер повратка, скин, линија, бот), догађаји, gameData (мод, време, мапа, терен); `used` је тачно док утакмица тече, нетачно на екрану са крајем
- `eventdata`: сваки одговор цео, тражи се на сваких 0,5 s од следећег ид-а догађаја; `used` је тачно кад је донео нове догађаје
- одговор који је бајт за бајт исти као претходни исте крајње тачке чува се једном и броји се (`unchanged_replies` у meta.json); одговори о грешци (RESOURCE_NOT_FOUND на екрану учитавања) чувају се са својим `status`-ом, пре почетка утакмице

**Није доступно**

- положаји: API их нема (нема мини-мапе, нема координата)
- остале крајње тачке (activeplayer, activeplayername, activeplayerabilities, activeplayerrunes, playerlist, playerscores, playersummonerspells, playermainrunes, playeritems, gamestats): свака служи део allgamedata, па се не траже
- Replay API (`/replay/*` на истом порту): пушта реплеје и гледане игре кад се укључи у game.cfg, није део одигране утакмице
- крајње тачке lockfile-а League клијента: нису објављен API (видите [Извори и правила](sources-and-rules.md))
- вредности између два читања: API одговара кад га питате и не шаље сам; резултатска табела се пита на сваке 2 s, догађаји на сваких 0,5 s

**Величина**: allgamedata је 15-40 KB (носи целу листу догађаја, која расте) на сваке 2 s: око 30-70 MB на сат у `raw.bin`; eventdata додаје мало, јер се непромијењени одговори броје, не чувају; zstd смањи понављани JSON у `heat.raw.parquet` на неколико MB на сат (процена по објављеном формату)

## Провјерено {#verified}

тестирано на серверу који одговара лажно, са одговорима у документованом формату; није тестирано са игром

## Извор {#source}

[heat3d_watch/adapters/lol.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/lol.py)

<!-- Generated from the adapter by tools/gen_game_pages.py; change the adapter and run it again rather than editing this page. -->
