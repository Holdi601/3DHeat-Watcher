---
title: "Vývoj"
nav_order: 12
lang: "cs"
source: development.md
source_hash: "cb213e22ddea"
nav_exclude: true
search_exclude: true
---
# Vývoj {#development}

Tato stránka je pro přidání hry: jak se staví adaptér, jak se testuje a jak se dělá jeho dokumentace.

## Repozitář {#the-repository}

| Cesta | Co obsahuje |
|---|---|
| `heat3d_watch/cli.py` | příkazy ([Příkazy](commands.md)) |
| `heat3d_watch/watcher.py` | smyčka na pozadí: seznam procesů, jedno vlákno na adaptér, aktualizace |
| `heat3d_watch/session.py` | záznam: `events.jsonl`, `heat.parquet`, `meta.json`, obnova |
| `heat3d_watch/db.py` | `watcher.sqlite` |
| `heat3d_watch/config.py` | nastavení a datová složka |
| `heat3d_watch/safety.py`, `heat3d_watch/memory.py` | kontroly paměti a čtečka jen pro čtení ([Čtení paměti](memory-reading.md)) |
| `heat3d_watch/notify.py` | oznámení ve Windows |
| `heat3d_watch/adapters/` | jeden modul na hru nebo rodinu her; moduly začínající `_` jsou sdílené pomocné funkce |
| `heat3d_watch/decoders/` | dekodéry závodní telemetrie, zkopírované z lap rekordérů 3DHeat GameCapture |
| `heat3d_update/` | aktualizátor ([Aktualizace](updates.md)) |
| `mods/beamng/heat3d/` | protokolový mod BeamNG, který instaluje `setup beamng` |
| `tests/` | testy |
| `tools/gen_game_pages.py` | zapisuje stránky her této dokumentace |

## Adaptér {#an-adapter}

Adaptér je dataclass odvozená od `heat3d_watch.adapters.base.Adapter`. Jeho pole říkají, čím je; jeho metody dělají práci.

| Pole | Výchozí | Co to je |
|---|---|---|
| `id` | `""` | krátké a stálé: složky záznamů, `disabled`, `replay_folders` a `player_names` na něj odkazují |
| `game` | `""` | název hry, jak ho lidé píšou; záznamy se řadí pod něj |
| `kind` | `"telemetry"` | jeden z `telemetry`, `gsi`, `log`, `replay`, `platform`, `memory` ([Zdroje a pravidla](sources-and-rules.md)) |
| `exes` | `()` | názvy spustitelných souborů (bez ohledu na velikost písmen), které znamenají, že hra běží. Prázdné: adaptér běží vždy (`always` je pravda) |
| `multiplayer` | `True` | hra se hraje online: její paměť se nikdy nečte |
| `source` | `""` | odkud čísla pocházejí, řečeno jednou |
| `records` | `()` | co se zaznamenává, jedna položka na každý druh věci |
| `enable` | `""` | jak zdroj zapnout; prázdné, když nic není potřeba |
| `interval` | `0.1` | sekundy mezi dotazy |
| `axes` | `Axes()` | svislá osa světa, zrcadlené osy, měřítko jednotek prohlížeče (nechte 1) a poznámka k jednotkám |
| `verified` | `""` | co bylo ověřeno, poctivě (viz níže) |
| `completeness` | `{}` | popis zdroje podle [pravidla převodníků](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md) 3DHeat: `read` (co se stane řádky), `raw` (co se ukládá celé, pod jakým `type`), `missing` (co zdroj nedává, a proč), `size` (jak velký je surový tok za hodinu). Sekce „Completeness“ na stránce hry se z něj píše |

`source`, `records`, `enable`, `verified` a `completeness` jsou dokumentace, ne ozdoba. `games` je vypíše, `games --markdown` vytvoří tabulku v [Všechny hry v jedné tabulce](watcher.md) a stránky her se z nich generují. Pište je tak, aby přesně říkaly, co kód dělá.

Metody, všechny nepovinné:

| Metoda | Volá se | Co má dělat |
|---|---|---|
| `missing(self) -> str \| None` | `games`, `status` a před spuštěním | říct, proč adaptér tu nejde spustit (DLL nenalezeno, chybí složka), nebo `None` |
| `setup(self, ctx, *, apply) -> list[str]` | `setup` | zapnout vlastní výstup hry; vrátit jeden řádek na každou změnu a soubory měnit jen tehdy, když je `apply` pravda. Před první změnou zazálohovat soubor jako `<file>.heat3d-backup` a tu zálohu nikdy nepřepsat. Přepisujte jen tehdy, když je co zapnout: `can_setup` (pravda, když je `setup` přepsán) rozhoduje, zda `setup` spustí, nebo říká, že není co měnit; třída, která slouží více hrám, přepíše `can_setup` pro ty, které nenastaví (`RallyAdapter` pro Richard Burns Rally). |
| `start(self, ctx)` | když se objeví proces hry (adaptéry, které běží vždy: když začne `run`) | otevřít sokety, najít soubory, zapamatovat si, kde začít |
| `poll(self, ctx)` | každých `interval` sekund, ve vlastním vlákně adaptéru | vzít, co hra řekla od posledního dotazu, a zaznamenat to |
| `stop(self, ctx)` | když hra zmizí nebo se Watcher zastaví | uzavřít záznamy a sokety |

Každý adaptér běží ve vlastním vlákně (`Runner`). Výjimka v `poll` se zaloguje a adaptér počká `min(5, interval × 10 + 0.5)` sekund před dalším dotazem. Po 20 selháních v řadě, nebo selhání v `start`, se adaptér zastaví a znovu nespustí, dokud se nezmění id procesu hry. `missing()` se kontroluje při každém průchodu, takže ať je levná.

Objekt adaptéru se znovu použije, když se hra spustí znovu, takže `start` musí vynulovat vše, co po předchozím běhu zůstalo.

### Registrace {#registering-it}

Dejte modul do `heat3d_watch/adapters/` a na jeho konec vypište adaptéry:

```python
ADAPTERS = [MyAdapter(id="mygame", game="My Game", ...)]
```

`adapters.load()` naimportuje každý modul v balíčku (kromě `base` a názvů začínajících `_`) a sebere jejich `ADAPTERS`. Dva adaptéry se stejným id zastaví načítání s `ValueError`. Modul, který se nepodaří naimportovat (chybí závislost), vynechá své hry a `games` ho uvede i s chybou, takže problém jedné hry nezastaví ostatní.

## Kontext a Session {#context-and-session}

`start`, `poll`, `stop` a `setup` dostanou `Context`:

| Člen | Co je to |
|---|---|
| `settings` | `Settings` ([Instalace a spuštění](installing-and-running.md#settings)) |
| `data` | datová složka |
| `pid`, `exe` | id procesu hry a cesta ke spustitelnému souboru, když byl adaptér spuštěn pro běžící hru; složka instalace je vedle `exe` |
| `open(adapter, *, game=None, when=None, axes=..., source=..., multiplayer=..., meta=..., geo=None)` | nový `Session`. `game` přepíše název hry adaptéru (pro adaptéry, které kryjí více her); `when` nastaví začátek u záznamů, které popisují minulost; `axes`, `source` a `multiplayer` jsou výchozí z adaptéru; `meta` je slovník zapsaný do `meta.json`; `geo` (`{"lat0": .., "lon0": ..}`, nebo nastavte `session.geo` později) umístí záznam ploché mapy na zeměkouli, v `meta.json` a v patičce tabulky |
| `close(session)` | ukončí záznam: tabulku, `heat.raw.parquet`, `meta.json` a jeho řádek v `watcher.sqlite`. Záznam bez událostí i bez surových položek se smaže; s jen surovými položkami se ponechá (bez tabulky, bez řádku v databázi). Přijímá `None`. Vrací cestu k tabulce, nebo `None`. |

`Session` zaznamenává:

| Člen | Co dělá |
|---|---|
| `event(name, *, t=None, ms=None, x=None, y=None, z=None, player=None, team=None, session=None, **attrs)` | jeden řádek. `t` je výchozí sekundy od začátku záznamu, `ms` je výchozí teď. Pozice se počítá, jen když jsou zadány všechny `x`, `y` a `z` a jsou konečné. Atributy `None` se vynechají. |
| `position(x, y, z, **kw)` | událost jménem `position` |
| `raw(type, payload=None, *, text=None, used=False, t=None, ms=None, **fields)` | uchová jednu věc, kterou zdroj poslal, celou: bajty paketu nebo stránky (`payload`), řádek nebo JSON odpověď tak, jak přišly (`text`), nebo hodnoty čtení podle jména (`fields`, každá ve svém sloupci). `type` je vlastní označení zdroje (id paketu, název mapování, událost deníku, koncový bod); `used` říká, že to se také stalo řádky. Při volání se rozloží do `raw.bin`, při uzavření nebo obnově se zapíše jako `heat.raw.parquet` (zstd) a počítá se podle `type` v `meta.json` v `selfCheck.completeness` |
| `stat(key, value, how="set")` | statistika: `set` ji nastaví, `add` k ní přičte, `max` nebo `min` drží extrém |
| `now()` | sekundy od začátku záznamu |
| `meta` | slovník zapsaný do `meta.json` |
| `started`, `ended`, `folder`, `id`, `counts`, `positions` | kdy, kde a co se dosud zaznamenalo |

`event`, `stat` a `raw` jsou bezpečné pro vlákna a lze je volat z pracovního vlákna.

**Každý adaptér si ponechá všechno, co jeho zdroj pošle.** Řádky jsou to, co prohlížeč kreslí; nejsou záznamem. Každý paket, který dorazí na port, každá přečtená stránka sdílené paměti (celé mapování, pokaždé, když se změní), každý řádek logu nebo exportního skriptu (i ty, které adaptér ignoruje), každá JSON odpověď nebo odeslaný dokument jde do `session.raw(...)`, jakmile přijde, ať se z něj stane řádek, nebo ne – a nic se neprořeďuje pod rychlost, jakou adaptér čte. Položka, která přijde dřív, než je záznam otevřen, ho otevře (záznam jen se surovými položkami se ponechá), nebo se podrží, dokud se nějaký neotevře; nikdy se nezahodí. Pole, která se dají levně dekódovat a jsou významově jistá, jdou i na řádky. Toto je [pravidlo převodníků](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md) 3DHeat: živý tok je pryč, jakmile je odeslán, takže co adaptér nepodrží, je ztraceno navždy, a co podrží celé, lze dekódovat v den, kdy ho někdo pochopí. Velikost je cena; zstd a kódování slovníkem ji drží nízko, a ne tím, že se věci vynechají. Test každého adaptéru pošle něco, co nepoužívá, a ověří, že se z `heat.raw.parquet` vrátí celé a že `selfCheck.completeness.lost` je 0. `racing.Driving.raw` dělá totéž pro závodní adaptéry (a záznam otevírá) a `racing.Pages` drží stránky sdílené paměti, kdykoli se změní jejich bajty, a počítá zbytečná čtení, která nic nového nenašla, v `unchanged_reads` v `meta.json`.

Konvence, na kterých se spoléhá zbytek systému:

- **Vlastní řádky hráče jsou označeny podle toho, co říká zdroj.** `player="me"`, kde je zdroj hráčův vlastní; kde se každý hráč zaznamenává pod jménem, `own_car=1` na řádcích auta hráče (podle indexu hráče ve hře nebo zobrazeného účastníka), nebo jméno hráče jako `session.meta["player"]` (zapsané hned do `meta.json`), když zdroj hráče jmenuje. Nikdy nehádejte: kde zdroj neříká, vezměte jméno z nastavení (`player_names`, `riot_id`), nebo neoznačujte nic.
  [NVIDIA highlights](nvidia-highlights.md) si pozice půjčují jen z takových řádků (`platform.own_row`). Ostatní hráči se berou podle jména nebo id.
- **Trasy jsou ohraničeny událostmi s pozicemi**: `spawn`, `respawn` a `session_start` trasu začínají; `death`, `finish`, `session_end` a `teleport` ji končí. Kdykoli se hráč pohnul, aniž by cestoval (reset, přetočení, rychlý přesun, načtená uložená hra), zapište `teleport` na místě, které opustil, a potom začátek (`spawn`, nebo `respawn` u resetu, který hra pojmenuje) na místě, kam dorazil, aby čára tepla v prohlížeči ukončila jednu trasu a začala další, místo aby kreslila přes mapu. `Driving.jumped` to dělá pro vozidla.
- **Pozice zůstávají ve světových souřadnicích a jednotkách hry**, popsaných v `axes`. Nepřevádějte je do jiné soustavy, pokud hra nedává použitelný světový rámec (simulátory letu dávají zeměpisnou šířku a délku do ploché mapy, `Tangent`, kolem první polohy – DCS kolem pevného počátku svého prostoru – a předají `geo=tangent.geo()` do `open`, aby patička řekla, kde na Zemi mapa je). `axes.scale` je měřítko jednotek prohlížeče – násobí každou pozici – a zůstává 1, takže řádky sedí na úroveň exportovanou ze stejné hry ve stejných jednotkách; jednotku uveďte v `axes.units`.
- **Klíče statistik** jsou malá písmena s podtržítky a nesou svou jednotku, kde se hodí (`distance_km`, `top_speed_kmh`, `max_altitude_m`, `duration_s`). Čas uložený jako nejlepší začíná `best_` (drží se `min`), místo končí `_position`: `stats` ukazuje nejnižší z nich jako nejlepší a nejvyšší u každého jiného klíče (`db.lower_is_better`).

## Pomocné funkce {#helpers}

| Pomocná funkce | Modul | Pro |
|---|---|---|
| `Follower(find, since, stamp=None)`, `game_started(pid)`, `newest(paths)`, `read_shared(path)`, `steam_libraries()` | `_logfollow` | sledování logu, který hra píše: sdílená čtení, jen řádky této relace, nové a nahrazené soubory, jen celé řádky |
| `UdpPort(port, forward=None, grace=0.0, recheck=3.0)` s `try_open(who)`, `receive()`, `close()` | `racing` | UDP port telemetrie na 127.0.0.1, převzatý jen když je volný, předaný jinému programu, volitelně přeposílaný |
| `Driving(adapter, ctx, hz=10.0, jump=50.0)` s `sample(...)`, `event(...)`, `lap(...)`, `count(...)`, `close()` | `racing` | záznamy vozidel: pozice v pevném tempu, vzdálenost, nejvyšší rychlost, kola; při skoku `teleport` tam, kde auto bylo, a `spawn` tam, kde je (`jumped(...)`) |
| `SharedView.open(name)` | `simracing_shm` | pojmenovaná sdílená paměť hry, jen pro čtení, nikdy se nevytváří |
| `ReplayAdapter` (`patterns`, `folders(ctx)`, `convert(path, ctx)`) | `replays` | sledovaná složka replayů: soubory se převádějí, jakmile přestanou růst, ve vlákně na pozadí; první pohled jen zaznamená, co tam je, a `convert_existing(ctx, folder=None)` – příkaz [`replays`](commands.md#replays) – je převádí na vyžádání |
| `load_state`, `save_state` | `platform` | pamatování si, co už adaptér, který běží vždy, viděl, v `<data>\state\<id>.json` |
| `FlightLog`, `Tangent` | `xplane` | evidence letů (vzlety, přistání, pády, vzdálenost) a plochá mapa kolem první polohy (`Tangent.geo()` je `geo` záznamu) |
| `backup_once(path)` | `gsi`, `racing` | pravidlo `<file>.heat3d-backup` |
| Soubory Steamu | `_steam` | binární a textové KeyValues, složka Steamu z registru |

Minimální logový adaptér jako ukázka (smyšlená hra):

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

Záznam otevřete s první věcí, která stojí za zápis, ne v `start`, aby hra zůstávající v menu nenechala nic za sebou (prázdný záznam se stejně smaže).

## Testy {#tests}

```bash
python -m pytest
```

`tests/conftest.py` dá každému testu jednorázovou datovou složku (`HEAT3D_WATCH_HOME`) a vypne kontroly aktualizací a oznámení (`HEAT3D_NO_UPDATE`, `HEAT3D_NO_TOAST`). Test adaptéru vytvoří výstup hry z jejího zveřejněného formátu – pakety podle specifikace, řádky logu ve formátu hry, soubory v dokumentovaném rozložení – a řídí adaptér přímo (zkráceno z `tests/test_poe.py`; `data` a `install` jsou dočasné složky):

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

Síťové adaptéry se testují proti falešnému místnímu serveru, nebo s pakety poslanými přes UDP přímo do adaptéru. Testy, které kontrolují proti skutečným datům hry na počítači vývojáře, jsou označeny `@pytest.mark.local` a přeskočí se tam, kde ta data nejsou. Tato data se nikdy nedostanou do repozitáře. `test_core.py` také obsahuje test, který selže, pokud se v balíčku objeví jakýkoli kód, který by mohl zapisovat do jiného procesu (`test_memory_reading_cannot_write`).

## Poctivé `verified` {#an-honest-verified}

`verified` říká, co bylo ověřeno a jak, a co ověřeno nebylo. Ukazuje ho `games` a každá stránka hry a hráči se na něj spoléhají. Příklady z kódu:

- „tested on packets in the 2023, 2024 and 2025 formats built from EA's published specification, sent over UDP; untested against the game“
- „tested on documents in the published GSI format posted to the running adapter; untested against the running game“
- „tested on real stats files and schemas from a local install; change detection tested on files built in the binary KeyValues format“

Dokud adaptér nezaznamenal běžící hru, pište „untested against the game“. Uveďte jen způsob a toleranci: nikdy mapu, id zápasu, jméno hráče, datum, velikost korpusu ani přesné počty z reálných souborů, a nikdy „this machine“ (čtenáři to nemohou vědět). U každého offsetu a rozložení pojmenujte zdroj a řekněte, kde byly porovnány dva zdroje. Nikdy netvrďte víc, než bylo uděláno. Formát, který byl odhadnut, nebo převzat z komunitních nástrojů, se tak označí.

## Stránky her {#the-game-pages}

Každá stránka pod [Hry](games.md) se generuje z adaptérů, takže vždy odpovídá kódu. Po přidání nebo změně adaptéru je přegenerujte ze složky repozitáře:

```bash
HEAT3D_NO_UPDATE=1 python tools/gen_game_pages.py
```

(V PowerShellu: `$env:HEAT3D_NO_UPDATE = "1"; python tools/gen_game_pages.py`.) Přidejte `--check`, pokud chcete jen porovnat: nic nezapíše a skončí s kódem 1, když je stránka zastaralá (také tabulka her v `docs/watcher.md`).

Skript:

- načte adaptéry přes `heat3d_watch.adapters.load()` proti prázdné dočasné datové složce, takže se na stránky nedostane žádný profil paměti ani nastavení z vašeho počítače. Adaptéry paměti se vynechají, protože pocházejí z vlastních profilů hráčů;
- nic nezapíše, když se některý modul adaptéru nepodaří naimportovat (stránky by ztratily ty hry);
- zapíše `docs/game-<adapter id>.md` pro každý adaptér a `docs/games.md` s přehledovou tabulkou a smaže stránky adaptérů, které už neexistují;
- bere „What is recorded“, „Where it comes from“, „How to switch it on“, osy, příznak multiplayer a „Verified“ z polí adaptéru;
- mění docstring modulu na „How it works“. Docstringy pište prostým textem, jaký už moduly používají a který skript převádí: odstavce; seznamy s `*`, `-` nebo `1.`; rozložení a příklady odsazené pod řádkem, který je uvádí (stanou se bloky kódu); název podtržený pomlčkami, nebo krátký titulek s textem odsazeným přímo pod ním (stanou se nadpisy);
- vypíše klíče statistik, které kód adaptéru nastavuje jménem – `.stat("key", ...)`, obě strany výrazu `if` a vzory f-řetězců jako `score.{team}` – ve třídách adaptéru i v pomocných funkcích, které používá. Klíče brané z proměnné (tabulka polí hry) se nevypisují;
- určí „Positions“ z `axes.units` adaptéru (poznámka začínající „no“ nebo „none“ znamená žádné pozice) a z toho, co kód zapisuje.

Stránky vygenerované nerupravujte ručně: změňte adaptér a skript spusťte znovu. Tabulka v [Všechny hry v jedné tabulce](watcher.md) je výstup `python -m heat3d_watch games --markdown`.
