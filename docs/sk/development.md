---
title: "Vývoj"
nav_order: 12
lang: "sk"
source: development.md
source_hash: "cb213e22ddea"
nav_exclude: true
search_exclude: true
---
# Vývoj {#development}

Táto stránka je pre pridanie hry: ako sa zostavuje adaptér, ako sa testuje a ako sa píše jeho dokumentácia.

## Repozitár {#the-repository}

| Cesta | Čo obsahuje |
|---|---|
| `heat3d_watch/cli.py` | príkazy ([Príkazy](commands.md)) |
| `heat3d_watch/watcher.py` | slučka na pozadí: zoznam procesov, jedno vlákno na adaptér, aktualizácie |
| `heat3d_watch/session.py` | záznam: `events.jsonl`, `heat.parquet`, `meta.json`, obnova |
| `heat3d_watch/db.py` | `watcher.sqlite` |
| `heat3d_watch/config.py` | nastavenia a dátový priečinok |
| `heat3d_watch/safety.py`, `heat3d_watch/memory.py` | kontroly pamäte a čítačka, ktorá iba číta ([Čítanie pamäte](memory-reading.md)) |
| `heat3d_watch/notify.py` | upozornenia Windows |
| `heat3d_watch/adapters/` | jeden modul na hru alebo skupinu hier; moduly začínajúce na `_` sú spoločné pomocné funkcie |
| `heat3d_watch/decoders/` | dekodéry telemetrie závodov, skopírované z nahrávačov kôl 3DHeat GameCapture |
| `heat3d_update/` | aktualizátor ([Aktualizácie](updates.md)) |
| `mods/beamng/heat3d/` | protokolový mod BeamNG, ktorý inštaluje `setup beamng` |
| `tests/` | testy |
| `tools/gen_game_pages.py` | zapíše stránky hier tejto dokumentácie |

## Adaptér {#an-adapter}

Adaptér je dataclass odvodená od `heat3d_watch.adapters.base.Adapter`. Jej polia hovoria, čo je; jej metódy robia prácu.

| Pole | Predvolené | Čo je |
|---|---|---|
| `id` | `""` | krátke a stále: priečinky relácií, `disabled`, `replay_folders` a `player_names` sa naň odvolávajú |
| `game` | `""` | názov hry tak, ako ho ľudia píšu; relácie sa zaraďujú pod ňu |
| `kind` | `"telemetry"` | jeden z `telemetry`, `gsi`, `log`, `replay`, `platform`, `memory` ([Zdroje a pravidlá](sources-and-rules.md)) |
| `exes` | `()` | názvy spustiteľných súborov (bez ohľadu na veľkosť písmen), ktoré znamenajú, že hra beží. Ak je prázdne: adaptér je vždy zapnutý (`always` je pravda) |
| `multiplayer` | `True` | hra sa hrá online: jej pamäť sa nikdy nečíta |
| `source` | `""` | odkiaľ prichádzajú čísla, povedané raz |
| `records` | `()` | čo sa zaznamenáva, jedna položka na každý druh veci |
| `enable` | `""` | ako zdroj zapnúť; prázdne, ak nič nie je treba |
| `interval` | `0.1` | sekundy medzi dotazmi |
| `axes` | `Axes()` | os hore vo svete, zrkadlené osi, mierka jednotiek pre prehliadač (nechajte 1) a poznámka k jednotkám |
| `verified` | `""` | čo sa overilo, a to poctivo (pozrite nižšie) |
| `completeness` | `{}` | opis zdroja podľa [pravidla konvertorov](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md): `read` (čo sa zmení na riadky), `raw` (čo sa uchová celé, a pod akým `type`), `missing` (čo zdroj nedáva a prečo), `size` (aký veľký je surový tok za hodinu). Sekcia hry „Completeness“ sa z neho píše |

`source`, `records`, `enable`, `verified` a `completeness` sú dokumentácia, nie ozdoba. `games` ich vypíše,
`games --markdown` vytvorí tabuľku v [Všetky hry v jednej tabuľke](watcher.md) a stránky hier sa z nich generujú.
Píšte ich tak, aby presne hovorili, čo kód robí.

Metódy, všetky nepovinné:

| Metóda | Volá sa | Čo má robiť |
|---|---|---|
| `missing(self) -> str \| None` | `games`, `status` a pred spustením | povedať, prečo adaptér tu nemôže bežať (chýba DLL, chýba priečinok), alebo `None` |
| `setup(self, ctx, *, apply) -> list[str]` | `setup` | zapnúť vlastný výstup hry; vrátiť jeden riadok na každú zmenu a súbory meniť, len keď je `apply` pravda. Pred prvou zmenou zálohovať súbor ako `<file>.heat3d-backup` a takú zálohu nikdy neprepísať. Prepisovať ho len vtedy, keď je čo zapnúť: `can_setup` (pravda, keď je `setup` prepísané) rozhoduje, či `setup` spustí, alebo povie, že nie je čo meniť; trieda, ktorá slúži viacerým hrám, prepíše `can_setup` pre tie, ktoré nevie nastaviť (`RallyAdapter` pre Richard Burns Rally). |
| `start(self, ctx)` | keď sa objaví proces hry (adaptéry, ktoré bežia stále: keď sa spustí `run`) | otvoriť sockety, nájsť súbory, zapamätať si, kde začať |
| `poll(self, ctx)` | každých `interval` sekúnd, vo vlákne samotného adaptéra | prevziať, čo hra povedala od posledného dotazu, a zaznamenať to |
| `stop(self, ctx)` | keď hra zmizne alebo sa watcher zastaví | uzavrieť relácie a sockety |

Každý adaptér beží vo vlastnom vlákne (`Runner`). Výnimka v `poll` sa zapíše do záznamu a adaptér počká
`min(5, interval × 10 + 0.5)` sekúnd pred ďalším dotazom. Po 20 zlyhaniach za sebou, alebo pri zlyhaní v `start`,
sa adaptér zastaví a znova sa nespustí, kým sa nezmení id procesu hry. `missing()` sa kontroluje pri každej kontrole,
preto ho držte lacný.

Objekt adaptéra sa znova použije, keď sa hra spustí znova, takže `start` musí vynulovať všetko, čo tam zanechal
predchádzajúci beh.

### Registrácia {#registering-it}

Dajte modul do `heat3d_watch/adapters/` a na jeho konci uveďte adaptéry v zozname:

```python
ADAPTERS = [MyAdapter(id="mygame", game="My Game", ...)]
```

`adapters.load()` načíta každý modul v balíku (okrem `base` a mien začínajúcich na `_`) a pozbiera ich `ADAPTERS`.
Dva adaptéry s rovnakým id zastavia načítanie s `ValueError`. Modul, ktorý sa nepodarí načítať (chýbajúca závislosť),
vynechá svoje hry a `games` ho uvedie aj s chybou, takže problém jednej hry nezastaví ostatné.

## Context a Session {#context-and-session}

`start`, `poll`, `stop` a `setup` dostanú `Context`:

| Člen | Čo je |
|---|---|
| `settings` | `Settings` ([Inštalácia a spustenie](installing-and-running.md#settings)) |
| `data` | dátový priečinok |
| `pid`, `exe` | id procesu hry a cesta k jej spustiteľnému súboru, keď bol adaptér spustený pre bežiacu hru; priečinok inštalácie je vedľa `exe` |
| `open(adapter, *, game=None, when=None, axes=..., source=..., multiplayer=..., meta=..., geo=None)` | nová `Session`. `game` prepíše názov hry adaptéra (pre adaptéry, ktoré pokrývajú veľa hier); `when` nastaví začiatok pre relácie, ktoré opisujú minulosť; `axes`, `source` a `multiplayer` sa predvolene preberú z adaptéra; `meta` je slovník zapísaný do `meta.json`; `geo` (`{"lat0": .., "lon0": ..}`, alebo nastavte `session.geo` neskôr) umiestni reláciu plochej mapy na zemi, v `meta.json` a v pätičke tabuľky |
| `close(session)` | ukončí reláciu: tabuľku, `heat.raw.parquet`, `meta.json` a jej riadok v `watcher.sqlite`. Relácia bez udalostí aj bez surových položiek sa zmaže; relácia len so surovými položkami sa zachová (bez tabuľky a bez riadka v databáze). Prijme `None`. Vráti cestu k tabuľke alebo `None`. |

`Session` zaznamenáva:

| Člen | Čo robí |
|---|---|
| `event(name, *, t=None, ms=None, x=None, y=None, z=None, player=None, team=None, session=None, **attrs)` | jeden riadok. `t` je predvolene sekundy od začiatku relácie, `ms` predvolene teraz. Pozícia sa počíta, len keď sú dané `x`, `y` a `z` všetky a sú konečné. Atribúty `None` sa vynechajú. |
| `position(x, y, z, **kw)` | udalosť s menom `position` |
| `raw(type, payload=None, *, text=None, used=False, t=None, ms=None, **fields)` | uchovať jednu vec, ktorú zdroj poslal, celú: bajty paketu alebo stránky (`payload`), riadok alebo odpoveď JSON tak, ako prišla (`text`), alebo hodnoty čítania podľa mena (`fields`, každá v svojom stĺpci). `type` je slovo zdroja pre ňu (id paketu, názov mapovania, udalosť žurnálu, koncový bod); `used` hovorí, že sa stala aj riadkami. Hneď pri volaní sa zapíše do `raw.bin`, pri zatvorení alebo obnove relácie sa zapíše ako `heat.raw.parquet` (zstd) a počíta sa podľa `type` v `selfCheck.completeness` v `meta.json` |
| `stat(key, value, how="set")` | štatistika: `set` ju nastaví, `add` k nej pripočíta, `max` alebo `min` ponechá najvyššiu alebo najnižšiu hodnotu |
| `now()` | sekundy od začiatku relácie |
| `meta` | slovník zapísaný do `meta.json` |
| `started`, `ended`, `folder`, `id`, `counts`, `positions` | kedy, kde a čo sa doteraz zaznamenalo |

`event`, `stat` a `raw` sú bezpečné pre vlákna a dajú sa volať z pracovného vlákna.

**Každý adaptér si uchová všetko, čo jeho zdroj pošle.** Riadky sú to, čo prehliadač kreslí; nie sú to záznam.
Každý paket, ktorý dorazí na port, každá prečítaná stránka zdieľanej pamäte (celé mapovanie, zakaždým keď sa zmení),
každý riadok skriptu logu alebo exportu (aj tie, ktoré adaptér ignoruje), každá odpoveď JSON alebo odoslaný dokument
ide do `session.raw(...)` hneď, ako prišiel, či sa stane riadkom alebo nie – a nič sa nezreďuje pod rýchlosť, akou
adaptér číta. Položka, ktorá príde skôr, než sa otvorí relácia, ju otvorí (relácia len so surovými položkami sa
zachová), alebo sa podrží, kým sa otvorí; nikdy sa nezahodí. Polia, ktoré sa lacno dekódujú a sú isté významom, sa
dostanú aj do riadkov. Toto je [pravidlo konvertorov](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md)
3DHeat: živý tok je preč hneď, ako sa pošle, takže čo adaptér nepodrží, je stratené navždy, a čo podrží celé, sa dá
dekódovať deň, keď to niekto pochopí. Veľkosť je cena; zstd a kódovanie slovníkom ju držia nízko, nie vynechávaním vecí.
Každý test adaptéra pošle niečo, čo nepoužíva, a overí, že sa to vráti celé z `heat.raw.parquet`, a že
`selfCheck.completeness.lost` je 0. `racing.Driving.raw` robí to isté pre závodné adaptéry (a otvára reláciu),
a `racing.Pages` uchováva stránky zdieľanej pamäte vždy, keď sa zmenia ich bajty, a počíta prečítania, ktoré nenašli
nič nové, v `unchanged_reads` v `meta.json`.

Konvencie, na ktorých sa spolieha zvyšok systému:

- **Riadky hráča sú označené z toho, čo hovorí zdroj.** `player="me"`, kde zdroj je hráčov vlastný; kde sa každý hráč
  zaznamenáva pod menom, `own_car=1` na riadkoch auta hráča (podľa indexu hráča v hre alebo sledovaného účastníka),
  alebo meno hráča ako `session.meta["player"]` (hneď zapísané do `meta.json`), keď zdroj hráča pomenúva. Nikdy
  nehádajte: kde zdroj nehovorí, vezmite meno z nastavenia (`player_names`, `riot_id`), alebo nič neoznačte.
  [NVIDIA highlights](nvidia-highlights.md) si pozície požičiavajú len z takých riadkov (`platform.own_row`). Ostatných
  hráčov rozpoznávame podľa mena alebo id.
- **Trasy sú ohraničené udalosťami s pozíciami**: `spawn`, `respawn` a `session_start` trasu začnú;
  `death`, `finish`, `session_end` a `teleport` ju ukončia. Kedykoľvek sa hráč pohol bez cestovania (reset, pretočenie,
  rýchly presun, načítaný save), zapíšte `teleport` na mieste, ktoré opustil, a potom štart (`spawn`, alebo `respawn`
  pri resete, ktorý hra pomenúva) na mieste, kde prišiel, aby čiara tepla v prehliadači ukončila jednu trasu a začala
  ďalšiu a nekreslila cez mapu. `Driving.jumped` to robí pre vozidlá.
- **Pozície zostávajú v súradniciach a jednotkách sveta hry**, opísaných v `axes`. Nepremieňajte ich do inej sústavy,
  pokiaľ hra nedáva použiteľnú svetovú sústavu (simulátory letu dávajú zemepisnú šírku a dĺžku do plochej mapy,
  `Tangent`, okolo prvého zachytenia – DCS okolo pevného začiatku svojho divadla – a odovzdajú `geo=tangent.geo()`
  do `open`, aby pätička hovorila, kde na zemi mapa je). `axes.scale` je mierka jednotiek prehliadača – násobí každú
  pozíciu – a zostáva 1, takže riadky sedia na úrovni exportovanej z tej istej hry v tých istých jednotkách; jednotku
  uveďte v `axes.units`.
- **Kľúče štatistík** sú malými písmenami s podčiarkami a nesú svoju jednotku, kde sa uplatňuje (`distance_km`,
  `top_speed_kmh`, `max_altitude_m`, `duration_s`). Čas uložený ako najlepší začína na `best_` (uchováva sa cez `min`),
  umiestnenie končí na `_position`: `stats` ukáže najnižšiu z nich ako najlepšiu a najvyššiu z každého iného kľúča
  (`db.lower_is_better`).

## Pomocné funkcie {#helpers}

| Pomocník | Modul | Na čo |
|---|---|---|
| `Follower(find, since, stamp=None)`, `game_started(pid)`, `newest(paths)`, `read_shared(path)`, `steam_libraries()` | `_logfollow` | sledovanie logu, ktorý hra zapisuje: zdieľané čítania, len riadky tohto sedenia, nové a nahradené súbory, len celé riadky |
| `UdpPort(port, forward=None, grace=0.0, recheck=3.0)` s `try_open(who)`, `receive()`, `close()` | `racing` | UDP port telemetrie na 127.0.0.1, zoberie sa len keď je voľný, odovzdá sa inému programu, voliteľne sa preposiela |
| `Driving(adapter, ctx, hz=10.0, jump=50.0)` s `sample(...)`, `event(...)`, `lap(...)`, `count(...)`, `close()` | `racing` | relácie vozidiel: pozície pevnou frekvenciou, vzdialenosť, najvyššia rýchlosť, kolá; pri skoku `teleport` tam, kde auto bolo, a `spawn` tam, kde je teraz (`jumped(...)`) |
| `SharedView.open(name)` | `simracing_shm` | pomenovaná zdieľaná pamäť hry, iba na čítanie, nikdy sa nevytvára |
| `ReplayAdapter` (`patterns`, `folders(ctx)`, `convert(path, ctx)`) | `replays` | sledovaný priečinok s replaymi: súbory sa prevedú, keď prestanú rásť, vo vlákne na pozadí; pri prvom pohľade sa iba zaznamená, čo tam je, a `convert_existing(ctx, folder=None)` – príkaz [`replays`](commands.md#replays) – ich prevedie na požiadanie |
| `load_state`, `save_state` | `platform` | zapamätanie si, čo už adaptér, ktorý beží stále, videl, v `<data>\state\<id>.json` |
| `FlightLog`, `Tangent` | `xplane` | evidencia letov (vzlety, pristátia, havárie, vzdialenosť) a plochá mapa okolo prvého zachytenia (`Tangent.geo()` je `geo` relácie) |
| `backup_once(path)` | `gsi`, `racing` | pravidlo `<file>.heat3d-backup` |
| súbory Steamu | `_steam` | binárne a textové KeyValues, priečinok Steamu z registra |

Minimálny adaptér logu, ako ilustrácia (fiktívna hra):

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

Otvorte reláciu pri prvej veci, ktorá stojí za zaznamenanie, nie v `start`, aby hra, ktorá zostane v menu, nezanechala
nič (prázdna relácia sa aj tak zmaže).

## Testy {#tests}

```bash
python -m pytest
```

`tests/conftest.py` dá každému testu jednorazový dátový priečinok (`HEAT3D_WATCH_HOME`) a vypne kontroly aktualizácií
a upozornenia (`HEAT3D_NO_UPDATE`, `HEAT3D_NO_TOAST`). Test adaptéra vytvorí výstup hry z jej publikovaného formátu –
pakety podľa špecifikácie, riadky logu v hernom formáte, súbory v zdokumentovanom rozložení – a ovláda adaptér priamo
(skrátené z `tests/test_poe.py`; `data` a `install` sú dočasné priečinky):

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

Sieťové adaptéry sa testujú proti falošnému lokálnemu serveru alebo s paketmi poslanými cez UDP na adaptér. Testy,
ktoré kontrolujú proti skutočným herným dátam na počítači vývojára, sú označené `@pytest.mark.local` a preskočia sa
tam, kde tieto dáta chýbajú. Tieto dáta sa nikdy nedostanú do repozitára. `test_core.py` obsahuje aj test, ktorý zlyhá,
ak sa v balíku objaví akýkoľvek kód, ktorý by mohol zapisovať do iného procesu (`test_memory_reading_cannot_write`).

## Poctivé `verified` {#an-honest-verified}

`verified` hovorí, čo sa overilo a ako, a čo nie. Zobrazuje ho `games` a každá stránka hry a hráči sa na ňu spoliehajú.
Príklady z kódu:

- "tested on packets in the 2023, 2024 and 2025 formats built from EA's published specification, sent
  over UDP; untested against the game"
- "tested on documents in the published GSI format posted to the running adapter; untested against the
  running game"
- "tested on real stats files and schemas from a local install; change detection tested on files built
  in the binary KeyValues format"

Pokiaľ adaptér nezaznamenal bežiacu hru, píšte „untested against the game“. Uveďte len spôsob a toleranciu:
nikdy mapu, id zápasu, meno hráča, dátum, veľkosť korpusu alebo presný počet zo skutočných súborov, a nikdy „tento
počítač“ (čítačky to nevedia). Pomenujte zdroj každého posunu a rozloženia a uveďte, kde sa porovnali dva zdroje.
Nikdy netvrďte viac, než sa urobilo. Formát, ktorý bol uhádnutý, alebo prevzatý z komunitných nástrojov, sa tak aj
označí.

## Stránky hier {#the-game-pages}

Každá stránka pod [Hry](games.md) sa generuje z adaptérov, takže sa vždy zhoduje s kódom. Po pridaní alebo zmene
adaptéra ich znova vygenerujte z priečinka repozitára:

```bash
HEAT3D_NO_UPDATE=1 python tools/gen_game_pages.py
```

(V PowerShelle: `$env:HEAT3D_NO_UPDATE = "1"; python tools/gen_game_pages.py`.) Pridajte `--check`, ak chcete len
porovnať: nič nezapíše a skončí s kódom 1, keď je stránka zastaraná (aj tabuľka hier v `docs/watcher.md`).

Skript:

- načíta adaptéry cez `heat3d_watch.adapters.load()` proti prázdnemu dočasnému dátovému priečinku, takže sa do stránok
  nedostane žiadny profil pamäte ani nastavenie z vášho počítača. Adaptéry pamäte sa vynechajú, lebo pochádzajú z profilov
  hráčov;
- nič nezapíše, ak sa niektorý modul adaptéra nedá načítať (stránky by stratili tie hry);
- zapíše `docs/game-<adapter id>.md` pre každý adaptér a `docs/games.md` s prehľadovou tabuľkou, a zmaže stránky
  adaptérov, ktoré už neexistujú;
- berie „What is recorded“, „Where it comes from“, „How to switch it on“, osi, príznak hry online a „Verified“
  z polí adaptéra;
- z docstringu modulu urobí „How it works“. Docstringy píšte v jednoduchom textovom štýle, aký už moduly používajú
  a skript ho prevedie: odseky; zoznamy s `*`, `-` alebo `1.`; rozloženia a príklady odsadené pod riadkom, ktorý ich
  uvádza (stanú sa blokmi kódu); nadpis podčiarknutý pomlčkami, alebo krátky riadok nadpisu s textom odsadeným priamo
  pod ním (stanú sa nadpismi);
- vypíše kľúče štatistík, ktoré kód adaptéra nastavuje podľa mena – `.stat("key", ...)`, obe strany výrazu `if`
  a vzory f-reťazcov ako `score.{team}` – v triedach adaptéra a v pomocných funkciách, ktoré používa. Kľúče, ktoré sa
  berú z premennej (tabuľka polí hry), sa nevypisujú;
- rozhoduje o „Positions“ z `axes.units` adaptéra (poznámka začínajúca na „no“ alebo „none“ znamená žiadne pozície)
  a z toho, čo jeho kód zapisuje.

Vygenerované stránky neupravujte ručne: zmeňte adaptér a skript spustite znova. Tabuľka v
[Všetky hry v jednej tabuľke](watcher.md) je výstup `python -m heat3d_watch games --markdown`.
