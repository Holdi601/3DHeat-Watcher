---
title: "Развој"
nav_order: 12
lang: "sr"
source: development.md
source_hash: "cb213e22ddea"
nav_exclude: true
search_exclude: true
---
# Развој {#development}

Ова страница је за додавање игре: како се прави адаптер, како се испитује и како се прави његова
документација.

## Репозиторијум {#the-repository}

| Путања | Шта садржи |
|---|---|
| `heat3d_watch/cli.py` | команде ([Команде](commands.md)) |
| `heat3d_watch/watcher.py` | позадинска петља: листа процеса, једна нит по адаптеру, ажурирања |
| `heat3d_watch/session.py` | снимак: `events.jsonl`, `heat.parquet`, `meta.json`, опоравак |
| `heat3d_watch/db.py` | `watcher.sqlite` |
| `heat3d_watch/config.py` | подешавања и фолдер с подацима |
| `heat3d_watch/safety.py`, `heat3d_watch/memory.py` | провере меморије и читач само за читање ([Читање меморије](memory-reading.md)) |
| `heat3d_watch/notify.py` | обавештења Windows-а |
| `heat3d_watch/adapters/` | по један модул за игру или породицу игара; модули који почињу са `_` су заједничке помоћне функције |
| `heat3d_watch/decoders/` | декодери телеметрије трке, копирани из снимача кругова 3DHeat GameCapture |
| `heat3d_update/` | ажурирач ([Ажурирања](updates.md)) |
| `mods/beamng/heat3d/` | мод протокола BeamNG-а који инсталира `setup beamng` |
| `tests/` | тестови |
| `tools/gen_game_pages.py` | пише странице игара ове документације |

## Адаптер {#an-adapter}

Адаптер је dataclass изведен из `heat3d_watch.adapters.base.Adapter`. Његова поља кажу шта је; његове
методе раде посао.

| Поље | Подразумевано | Шта је |
|---|---|---|
| `id` | `""` | кратак и стабилан: фолдери сесија, `disabled`, `replay_folders` и `player_names` се на њега позивају |
| `game` | `""` | име игре како га људи пишу; сесије се сврставају под њим |
| `kind` | `"telemetry"` | једна од врста `telemetry`, `gsi`, `log`, `replay`, `platform`, `memory` ([Извори и правила](sources-and-rules.md)) |
| `exes` | `()` | имена извршних фајлова (било које величине слова) која значе да игра ради. Празно: адаптер је увек укључен (`always` је тачно) |
| `multiplayer` | `True` | игра се играње онлајн: њена меморија се никада не чита |
| `source` | `""` | одакле долазе бројеви, речено једном |
| `records` | `()` | шта се бележи, по једна ставка за сваку врсту ствари |
| `enable` | `""` | како се извор укључује; празно када ништа не треба |
| `interval` | `0.1` | секунди између провера |
| `axes` | `Axes()` | вертикална оса света, огледане осе, јединична скала приказивача (држите 1) и напомена о јединицама |
| `verified` | `""` | шта је проверено, поштено (видите испод) |
| `completeness` | `{}` | извештај извора према [правилу претварача](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md) 3DHeat-а: `read` (шта постаје редови), `raw` (шта се чува цело, под којим `type`-ом), `missing` (шта извор не даје, и зашто), `size` (колико велик сирови ток постане за један сат). Одељак "Completeness" на страници игре пише се из њега |

`source`, `records`, `enable`, `verified` и `completeness` су документација, а не украс. `games` их
исписује, `games --markdown` прави табелу у [Све игре у једној табели](watcher.md), а странице игара се
праве из њих. Пишите их тако да тачно кажу шта код ради.

Методе, све опционе:

| Метода | Позива се | Шта треба даради |
|---|---|---|
| `missing(self) -> str \| None` | `games`, `status` и пре покретања | каже зашто адаптер не може да ради овде (DLL није нађен, фолдер недостаје), или `None` |
| `setup(self, ctx, *, apply) -> list[str]` | `setup` | укључује сопствени излаз игре; врати по једну линију за сваку измену, и мењај фајлове само када је `apply` тачно. Направи резерву `<file>.heat3d-backup` пре прве измене, и никада не преписуј ту резерву. Преписуј га само када има шта да се укључи: `can_setup` (тачно када је `setup` преписан) одлучује да ли `setup` то изводи или каже да нема шта да се мења; класа која служи за више игара преписује `can_setup` за оне које не може да подеси (`RallyAdapter` за Richard Burns Rally). |
| `start(self, ctx)` | када се појави процес игре (адаптери који су увек укључени: када `run` почне) | отвара сокете, налази фајлове, памти одакле да почне |
| `poll(self, ctx)` | на сваких `interval` секунди, у сопственој нити адаптера | узима шта је игра рекла од последње провере и бележи то |
| `stop(self, ctx)` | када игре нема или watcher стаје | затвара сесије и сокете |

Сваки адаптер ради у својој нити (`Runner`). Грешка у `poll` се бележи и адаптер чека
`min(5, interval × 10 + 0.5)` секунди пре следеће провере. После 20 узастопних грешака, или грешке у
`start`, адаптер се зауставља и не покреће се поново док не промени ид процеса игре.
`missing()` се проверава при сваком прегледу, па га држите јефтиним.

Објекат адаптера се поново користи када се игра поново покрене, па `start` мора да поништи све што је
претходно покретање оставило.

### Регистровање {#registering-it}

Ставите модул у `heat3d_watch/adapters/` и наведите адаптере на његовом крају:

```python
ADAPTERS = [MyAdapter(id="mygame", game="My Game", ...)]
```

`adapters.load()` увози сваки модул у пакету (осим `base` и имена која почињу са `_`) и скупља њихове
`ADAPTERS`. Два адаптера истог ида заустављају учитавање са `ValueError`. Модул који не може да се увезе
(недостаје зависност) изоставља своје игре и `games` га наводи са грешком, па проблем једне игре не
зауставља друге.

## Context и Session {#context-and-session}

`start`, `poll`, `stop` и `setup` добијају `Context`:

| Члан | Шта је |
|---|---|
| `settings` | `Settings` ([Инсталација и покретање](installing-and-running.md#settings)) |
| `data` | фолдер с подацима |
| `pid`, `exe` | ид процеса игре и путања извршног фајла, када је адаптер покренут за рад игру; фолдер инсталације је поред `exe` |
| `open(adapter, *, game=None, when=None, axes=..., source=..., multiplayer=..., meta=..., geo=None)` | нова `Session`. `game` преписује име игре адаптера (за адаптере који покривају много игара); `when` поставља почетак за сесије које описују прошлост; `axes`, `source` и `multiplayer` подразумевано узимају адаптерове; `meta` је речник који се уписује у `meta.json`; `geo` (`{"lat0": .., "lon0": ..}`, или постави `session.geo` касније) смешта сесију са равном мапом на Земљу, у `meta.json` и подножје табеле |
| `close(session)` | завршава сесију: табелу, `heat.raw.parquet`, `meta.json`, њен ред у `watcher.sqlite`. Сесија без догађаја и без сирових ставки се брише; она са само сировим ставкама се чува (без табеле, без реда у бази). Прима `None`. Враћа путању табеле или `None`. |

`Session` бележи:

| Члан | Шта ради |
|---|---|
| `event(name, *, t=None, ms=None, x=None, y=None, z=None, player=None, team=None, session=None, **attrs)` | један ред. `t` подразумевано је секунде од почетка сесије, `ms` је сада. Позиција се рачуна само када су `x`, `y` и `z` сви дати и коначни. Атрибути `None` се изостављају. |
| `position(x, y, z, **kw)` | догађај по имену `position` |
| `raw(type, payload=None, *, text=None, used=False, t=None, ms=None, **fields)` | чува једну ствар коју је извор послао, целу: бајтове пакета или странице (`payload`), ред или JSON одговор онакав какав је стигао (`text`), или вредности читања по имену (`fields`, свака у својој колони). `type` је изворна реч за то (ид пакета, име мапирања, догађај у журналу, крајња тачка); `used` каже да је то такође постало редови. Уоквирава се у `raw.bin` чим се позове, пише се као `heat.raw.parquet` (zstd) када се сесија затвори или опорави, и броји се по `type` у `meta.json`-овом `selfCheck.completeness` |
| `stat(key, value, how="set")` | статистика: `set` поставља, `add` додаје, задржи `max` или `min` |
| `now()` | секунде од почетка сесије |
| `meta` | речник који се уписује у `meta.json` |
| `started`, `ended`, `folder`, `id`, `counts`, `positions` | када, где и шта је до сада снимљено |

`event`, `stat` и `raw` су сигурни за нити и могу се позивати из радне нити.

**Сваки адаптер чува све што његов извор шаље.** Редови су оно што приказивач црта; нису запис. Сваки
пакет који стигне на порт, свака страница дељене меморије која се чита (цео мапирани простор, сваки пут
кад се промени), свака линија лога или извозне скрипте (и оне које адаптер игнорише), сваки JSON одговор
или послат документ иде у `session.raw(...)` чим стигне - било да постаје ред или не - и ништа се не
прореди испод брзине по којој адаптер чита. Ставка која стигне пре него што је сесија отворена отвара
једну (сесија са само сировим ставкама се чува), или се држи док се не отвори; никада се не баца. Поља
која су јефтина за декодирање и сигурна по значењу иду и у редове. Ово је [правило претварача](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md)
3DHeat-а: жив ток је нестао чим се пошаље, па оно што адаптер не сачува је изгубљено заувек, а оно што
сачува цело може да се декодира оног дана кад неко разуме шта је. Величина је цена; zstd и кодирање
речника је држе ниском, а не избацују ствари. Тест сваког адаптера пошаље нешто што он не користи и
проверава да се врати цело из `heat.raw.parquet`, и да је `selfCheck.completeness.lost` 0. `racing.Driving.raw`
ради исто за адаптере трка (и отвара сесију), а `racing.Pages` чува странице дељене меморије кад год се
њихови бајтови промене, и броји поновна читања која нису ништа нова нашла у `meta.json`-овом
`unchanged_reads`.

Конвенције на којима се остатак система ослања:

- **Редови играча самог обележени су према ономе што извор каже.** `player="me"` где је извор сам играч;
  где се сваки играч бележи под именом, `own_car=1` на редовима аутомобила играча (по индексу играча у
  игри или по посматраном учеснику), или име играча као `session.meta["player"]` (уписано у `meta.json`
  одмах) када извор наводи играча. Никад не погађај: где извор не каже, узми име из подешавања
  (`player_names`, `riot_id`) или ништа не обележавај. [NVIDIA highlights](nvidia-highlights.md) узимају
  позиције само из таквих редова (`platform.own_row`). Други играчи се разликују по имену или ид-у.
- **Путање су ограничене догађајима са позицијама**: `spawn`, `respawn` и `session_start` почињу једну;
  `death`, `finish`, `session_end` и `teleport` је завршавају. Кад год је играч се померио без путовања
  (ресет, премотавање, брзо путовање, учитана игра), упиши `teleport` на месту одакле је отишао, па почетак
  (`spawn`, или `respawn` за ресет који игра именује) на месту где је стигао, тако да линија топлоте на
  приказивачу затвори једну путању и почне следећу, уместо да црта преко мапе. `Driving.jumped` то ради
  за возила.
- **Позиције остају у светским координатама и јединицама саме игре**, описаним са `axes`. Не претварајте их у
  други оквир осим ако игра не даје користан светски оквир (игре летења дају географску ширину и дужину у
  Тангентну раван, `Tangent`, око прве тачке - DCS око фиксног почетка свог терена - и проследе
  `geo=tangent.geo()` у `open`, тако да подножје каже где је мапа на Земљи). `axes.scale` је јединична скала
  приказивача - множи сваку позицију - и остаје 1, па се редови поклапају са нивоом извезеним из исте игре у
  истим јединицама; јединицу наведите у `axes.units`.
- **Кључеви статистике** су мала слова са доњим цртама, и носе своју јединицу где важи
  (`distance_km`, `top_speed_kmh`, `max_altitude_m`, `duration_s`). Време које се чува као најбоље почиње
  са `best_` (чува се са `min`), а место се завршава са `_position`: `stats` најнижу од тих приказује као
  најбољу, а највишу од сваког другог кључа (`db.lower_is_better`).

## Помоћне функције {#helpers}

| Помоћна | Модул | За |
|---|---|---|
| `Follower(find, since, stamp=None)`, `game_started(pid)`, `newest(paths)`, `read_shared(path)`, `steam_libraries()` | `_logfollow` | праћење лога који игра пише: дељена читања, само редови ове седнице, нови и замењени фајлови, само цели редови |
| `UdpPort(port, forward=None, grace=0.0, recheck=3.0)` са `try_open(who)`, `receive()`, `close()` | `racing` | UDP порт за телеметрију на 127.0.0.1, узима се само када је слободан, предаје се другом програму, по жељи се прослеђује |
| `Driving(adapter, ctx, hz=10.0, jump=50.0)` са `sample(...)`, `event(...)`, `lap(...)`, `count(...)`, `close()` | `racing` | сесије возила: позиције на фиксној брзини, пређени пут, највећа брзина, кругови; при скоку, `teleport` где је возило било и `spawn` где је сада (`jumped(...)`) |
| `SharedView.open(name)` | `simracing_shm` | именована дељена меморија игре, само за читање, никада није створена |
| `ReplayAdapter` (`patterns`, `folders(ctx)`, `convert(path, ctx)`) | `replays` | праћен фолдер реплеја: фајлови се претварају кад престану да расту, у радној нити; први преглед само бележи шта је тамо, а `convert_existing(ctx, folder=None)` - команда [`replays`](commands.md#replays) - претвара оне на захтев |
| `load_state`, `save_state` | `platform` | памћење онога што је адаптер који ради увек видео, у `<data>\state\<id>.json` |
| `FlightLog`, `Tangent` | `xplane` | књиговодство лета (полетања, слетања, падови, пређени пут) и равна мапа око прве тачке (`Tangent.geo()` је `geo` сесије) |
| `backup_once(path)` | `gsi`, `racing` | правило `<file>.heat3d-backup` |
| Steam-ови фајлови | `_steam` | бинарни и текстуални KeyValues, фолдер Steam-а из регистра |

Минималан адаптер логова, као илустрација (измишљена игра):

```python
from dataclasses import dataclass, field
from pathlib import Path

from ..session import Axes, Session
from ._logfollow import Follower, game_started, newest
from .base import Adapter, Context


@dataclass
class ExampleAdapter(Adapter):
    _session: Session | None = field(default=None, repr=False)
    _follow: Follower | None = field(default=None, repr=False)

    def start(self, ctx: Context) -> None:
        log = (ctx.exe.parent if ctx.exe else Path(".")) / "logs" / "game.log"
        self._session = None
        self._follow = Follower(lambda: newest(p for p in [log] if p.exists()), game_started(ctx.pid))

    def poll(self, ctx: Context) -> None:
        for line in self._follow.lines() if self._follow else []:
            if line.startswith("DIED "):
                if self._session is None:
                    self._session = ctx.open(self)
                self._session.event("death", player="me")
                self._session.stat("deaths", 1, "add")

    def stop(self, ctx: Context) -> None:
        self.poll(ctx)
        ctx.close(self._session)
        self._session = None


ADAPTERS = [
    ExampleAdapter(
        id="example",
        game="Example Game",
        kind="log",
        exes=("ExampleGame.exe",),
        source=r"<install>\logs\game.log (followed)",
        records=("deaths",),
        interval=0.5,
        axes=Axes(units="no positions recorded"),
        verified="tested on synthetic log lines in the game's format; untested against the game",
    )
]
```

Отворите сесију првом вредном ствари за снимање, а не у `start`, тако да игра која стоји у менијима
не оставља ништа иза себе (празна сесија се ионако брише).

## Тестови {#tests}

```bash
python -m pytest
```

`tests/conftest.py` даје сваком тесту привремени фолдер с подацима (`HEAT3D_WATCH_HOME`) и искључује
провере ажурирања и обавештења (`HEAT3D_NO_UPDATE`, `HEAT3D_NO_TOAST`). Тест адаптера прави излаз игре
од њеног објављеног формата - пакети из спецификације, линије лога у формату игре, фајлови у
документованом распореду - и директно покреће адаптер (скраћено из `tests/test_poe.py`; `data` и `install`
су привремени фолдери):

```python
from dataclasses import replace
from heat3d_watch.adapters import poe
from heat3d_watch.adapters.base import Context
from heat3d_watch.config import Settings
from heat3d_watch.session import read_rows

ctx = Context(Settings(data=str(data)), data, exe=install / "PathOfExileSteam.exe")
a = replace(poe.ADAPTERS[0])   # a fresh copy of the adapter
a.start(ctx); a.poll(ctx); a.stop(ctx)
[session] = list((data / "sessions").glob("*/*"))
rows = read_rows(session)      # then check the rows and meta.json's stats
```

Мрежни адаптери се испитују на лажном локалном серверу или на пакетима послатим преко UDP-а адаптеру.
Тестови који проверавају наспрам правих података игре на рачунару програмера означени су са
`@pytest.mark.local` и прескачу се где тих података нема. Ти подаци никада не иду у репозиторијум.
`test_core.py` такође садржи тест који пада ако било који код који би могао да пише у други процес уђе у
пакет (`test_memory_reading_cannot_write`).

## Поштен `verified` {#an-honest-verified}

`verified` каже шта је проверено и како, и шта није. Приказује га `games` и свака страница игре, а играчи
се на њега ослањају. Примери из кода:

- "tested on packets in the 2023, 2024 and 2025 formats built from EA's published specification, sent
  over UDP; untested against the game"
- "tested on documents in the published GSI format posted to the running adapter; untested against the
  running game"
- "tested on real stats files and schemas from a local install; change detection tested on files built
  in the binary KeyValues format"

Пишите "untested against the game" док адаптер није снимио игру која ради. Наведите само метод и толеранцију:
никад мапу, ид партије, име играча, датум, величину корпуса или тачан број из правих фајлова, и никад "this
machine" (читачи то не знају). Наведите извор сваког офсета и распореда, и где су два извора упоређена.
Никада не тврдите више него што је урађено. Формат који је претпостављен или узет из алата заједнице
означава се као такав.

## Странице игара {#the-game-pages}

Свака страница под [Игре](games.md) се прави од адаптера, па се увек слаже са кодом. После додавања или
измене адаптера, поново их направите из фолдера репозиторијума:

```bash
HEAT3D_NO_UPDATE=1 python tools/gen_game_pages.py
```

(У PowerShell-у: `$env:HEAT3D_NO_UPDATE = "1"; python tools/gen_game_pages.py`.) Додајте `--check` да само
упореди: ништа не пише и излази са 1 када је страница застарела (и табела игара у `docs/watcher.md`).

Скрипта:

- учитава адаптере са `heat3d_watch.adapters.load()`, против празног привременог фолдера с подацима, тако
  да ниједан профил меморије или подешавање на вашем рачунару не доспе у странице. Адаптери меморије се
  изостављају, јер долазе из профила играча;
- ништа не пише ако модул адаптера не може да се увезе (странице би изгубиле те игре);
- пише `docs/game-<adapter id>.md` за сваки адаптер и `docs/games.md` са прегледном табелом, и брише
  странице адаптера који више не постоје;
- узима "What is recorded", "Where it comes from", "How to switch it on", осе, ознаку онлајн игре и
  "Verified" из поља адаптера;
- претвара документациони стринг модула у "How it works". Пишите документационе стрингове у обичном
  текстуалном стилу који модули већ користе, а који скрипта претвара: параграфи; листе са `*`, `-` или
  `1.`; распореди и примери увучени испод реда који их уводи (постају блокови кода); наслов подвучен
  цртицама, или кратак наслов са текстом увученим директно испод (постају наслови);
- наводи кључеве статистике које код адаптера поставља именом - `.stat("key", ...)`, обе стране `if` израза,
  и f-string обрасци као `score.{team}` - у класама адаптера и помоћним функцијама које користе. Кључеви
  узети из променљиве (табела поља игре) се не наводе;
- одлучује "Positions" из `axes.units` адаптера (напомена која почиње са "no" или "none" значи без позиција)
  и из онога што његов код пише.

Не уређујте генерисане странице ручно: промените адаптер и поново покрените скрипту. Табела у
[Све игре у једној табели](watcher.md) је излаз `python -m heat3d_watch games --markdown`.
