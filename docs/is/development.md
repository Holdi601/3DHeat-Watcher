---
title: "Þróun"
nav_order: 12
lang: "is"
source: development.md
source_hash: "cb213e22ddea"
nav_exclude: true
search_exclude: true
---
# Þróun {#development}

Þessi síða er til að bæta við leik: hvernig millistykki er smíðað, hvernig það er prófað og hvernig skjölun þess
er búin til.

## Geymslan {#the-repository}

| Slóð | Hvað hún geymir |
|---|---|
| `heat3d_watch/cli.py` | skipanirnar ([Skipanir](commands.md)) |
| `heat3d_watch/watcher.py` | bakgrunnslykkjan: ferlalistinn, einn þráður fyrir hvert millistykki, uppfærslur |
| `heat3d_watch/session.py` | upptaka: `events.jsonl`, `heat.parquet`, `meta.json`, endurheimt |
| `heat3d_watch/db.py` | `watcher.sqlite` |
| `heat3d_watch/config.py` | stillingarnar og gagnamappan |
| `heat3d_watch/safety.py`, `heat3d_watch/memory.py` | minnisathuganirnar og lesarinn sem aðeins les ([Minnislestur](memory-reading.md)) |
| `heat3d_watch/notify.py` | Windows-tilkynningar |
| `heat3d_watch/adapters/` | ein eining fyrir hvern leik eða leikjafjölskyldu; einingar sem byrja á `_` eru sameiginleg hjálparforrit |
| `heat3d_watch/decoders/` | afkóðarar kappakstursfjarmælingar, afritaðir úr hringjaupptökum 3DHeat GameCapture |
| `heat3d_update/` | uppfærslan ([Uppfærslur](updates.md)) |
| `mods/beamng/heat3d/` | BeamNG samskiptareglumóddið sem `setup beamng` setur upp |
| `tests/` | prófanirnar |
| `tools/gen_game_pages.py` | skrifar leikjasíður þessarar skjölunar |

## Millistykki {#an-adapter}

Millistykki er dataclass sem erfir frá `heat3d_watch.adapters.base.Adapter`. Svið þess segja hvað það
er; aðferðir þess vinna verkið.

| Svið | Sjálfgefið | Hvað það er |
|---|---|---|
| `id` | `""` | stutt og stöðugt: lotumöppur, `disabled`, `replay_folders` og `player_names` vísa í það |
| `game` | `""` | nafn leiksins eins og fólk skrifar það; loturnar eru skráðar undir því |
| `kind` | `"telemetry"` | eitt af `telemetry`, `gsi`, `log`, `replay`, `platform`, `memory` ([Heimildir og reglur](sources-and-rules.md)) |
| `exes` | `()` | nöfn keyrsluskráa (hvaða há-/lágstafir sem er) sem þýða að leikurinn er í gangi. Tómt: millistykkið er alltaf í gangi (`always` er true) |
| `multiplayer` | `True` | leikurinn er spilaður á netinu: minni hans er aldrei lesið |
| `source` | `""` | hvaðan tölurnar koma, sagt einu sinni |
| `records` | `()` | hvað er skráð, eitt atriði fyrir hverja tegund hluta |
| `enable` | `""` | hvernig á að kveikja á heimildinni; tómt þegar ekkert þarf |
| `interval` | `0.1` | sekúndur milli kannana |
| `axes` | `Axes()` | upp-ás heimsins, speglaðir ásar, einingakvarði skoðarans (hafðu 1) og athugasemd um einingarnar |
| `verified` | `""` | hvað hefur verið athugað, af hreinskilni (sjá hér að neðan) |
| `completeness` | `{}` | frásögn heimildarinnar undir [breytireglu](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md) 3DHeat: `read` (hvað verður að röðum), `raw` (hvað er geymt heilt, undir hvaða `type`), `missing` (hvað heimildin gefur ekki, og hvers vegna), `size` (hversu stórt hráa straumurinn verður á klukkustund). Hlutinn „Completeness“ á leikjasíðunni er skrifaður út frá því |

`source`, `records`, `enable`, `verified` og `completeness` eru skjölun, ekki skraut. `games` prentar þau,
`games --markdown` býr til töfluna í [Allir leikir í einni töflu](watcher.md), og leikjasíðurnar eru
búnar til úr þeim. Skrifaðu þau svo að þau segi nákvæmlega hvað kóðinn gerir.

Aðferðirnar, allar valfrjálsar:

| Aðferð | Kölluð | Hvað hún á að gera |
|---|---|---|
| `missing(self) -> str \| None` | af `games`, `status`, og áður en ræst er | segja hvers vegna millistykkið getur ekki keyrt hér (DLL fannst ekki, mappa vantar), eða `None` |
| `setup(self, ctx, *, apply) -> list[str]` | af `setup` | kveikja á eigin úttaki leiksins; skila einni línu fyrir hverja breytingu, og breyta skrám aðeins þegar `apply` er true. Taktu afrit af skrá sem `<file>.heat3d-backup` áður en hún er breytt í fyrsta sinn, og skrifaðu aldrei yfir það afrit. Yfirskrifaðu hana aðeins þegar eitthvað er til að kveikja á: `can_setup` (true þegar `setup` er yfirskrifuð) ræður hvort `setup` keyrir hana eða segir að ekkert sé til að breyta; klasi sem þjónar nokkrum leikjum yfirskrifar `can_setup` fyrir þá sem hann getur ekki sett upp (`RallyAdapter` fyrir Richard Burns Rally). |
| `start(self, ctx)` | þegar ferli leiksins birtist (alltaf-í-gangi millistykki: þegar `run` ræsist) | opna sökkla (sockets), finna skrár, muna hvar á að byrja |
| `poll(self, ctx)` | á `interval` sekúndna fresti, í eigin þræði millistykkisins | taka það sem leikurinn sagði frá síðustu könnun og skrá það |
| `stop(self, ctx)` | þegar leikurinn er horfinn eða watcher stöðvast | loka lotum og sökklum |

Hvert millistykki keyrir í eigin þræði (`Runner`). Undantekning í `poll` er skráð í logg og millistykkið bíður
`min(5, interval × 10 + 0.5)` sekúndur fyrir næstu könnun. Eftir 20 bilanir í röð, eða bilun í
`start`, er millistykkið stöðvað og ekki ræst aftur fyrr en ferlisauðkenni leiksins breytist.
`missing()` er athugað við hverja skönnun, svo hafðu það ódýrt.

Millistykkishlutur er endurnotaður þegar leikurinn ræsist aftur, svo `start` verður að endurstilla allt sem fyrri keyrsla
skildi eftir.

### Að skrá það {#registering-it}

Settu eininguna í `heat3d_watch/adapters/` og taktu saman millistykkin aftast í henni:

```python
ADAPTERS = [MyAdapter(id="mygame", game="My Game", ...)]
```

`adapters.load()` flytur inn hverja einingu í pakkanum (nema `base` og nöfn sem byrja á `_`) og
safnar `ADAPTERS` þeirra. Tvö millistykki með sama auðkenni stöðva hleðsluna með `ValueError`. Eining sem
tekst ekki að flytja inn (háðleiki vantar) skilur leiki sína eftir úti og `games` nefnir hana með villunni, svo
vandamál eins leiks stöðvar ekki hina.

## Context og Session {#context-and-session}

`start`, `poll`, `stop` og `setup` fá `Context`:

| Meðlimur | Hvað það er |
|---|---|
| `settings` | `Settings` ([Uppsetning og keyrsla](installing-and-running.md#settings)) |
| `data` | gagnamappan |
| `pid`, `exe` | ferlisauðkenni leiksins og slóð keyrsluskrárinnar, þegar millistykkið var ræst fyrir leik sem er í gangi; uppsetningarmappan er við hliðina á `exe` |
| `open(adapter, *, game=None, when=None, axes=..., source=..., multiplayer=..., meta=..., geo=None)` | ný `Session`. `game` yfirskrifar leikjaheiti millistykkisins (fyrir millistykki sem ná yfir marga leiki); `when` stillir upphafið fyrir lotur sem lýsa fortíðinni; `axes`, `source` og `multiplayer` eru sjálfgefið þau sem millistykkið hefur; `meta` er orðabók sem er skrifuð í `meta.json`; `geo` (`{"lat0": .., "lon0": ..}`, eða stilltu `session.geo` síðar) setur lotu á flötu korti á jörðina, í `meta.json` og fót töflunnar |
| `close(session)` | ljúka lotu: taflan, `heat.raw.parquet`, `meta.json`, lína hennar í `watcher.sqlite`. Lota án atburða og án hrárra atriða er eytt; lota með aðeins hrá atriði er geymd (engin tafla, engin lína í gagnagrunninum). Tekur við `None`. Skilar slóð töflunnar eða `None`. |

`Session` skráir:

| Meðlimur | Hvað það gerir |
|---|---|
| `event(name, *, t=None, ms=None, x=None, y=None, z=None, player=None, team=None, session=None, **attrs)` | ein röð. `t` er sjálfgefið sekúndur síðan lotan hófst, `ms` núna. Staðsetning telst aðeins þegar `x`, `y` og `z` eru öll gefin og endanleg. `None` eigindi eru sleppt. |
| `position(x, y, z, **kw)` | atburður sem heitir `position` |
| `raw(type, payload=None, *, text=None, used=False, t=None, ms=None, **fields)` | geyma eitt sem heimildin sendi, heilt: bæti pakka eða síðu (`payload`), línu eða JSON-svar eins og það kom (`text`), eða gildi úr lestri eftir nafni (`fields`, hvert sinn dálkur). `type` er eigið orð heimildarinnar fyrir það (pakkaauðkenni, nafn vörpunar, dagbókaratburður, endapunktur); `used` segir að það hafi líka orðið að röðum. Rammað inn í `raw.bin` um leið og kallað er, skrifað út sem `heat.raw.parquet` (zstd) þegar lotunni lýkur eða hún er endurheimt, og talið eftir `type` í `selfCheck.completeness` í `meta.json` |
| `stat(key, value, how="set")` | tölfræði: `set` stillir hana, `add` leggur við hana, `max` eða `min` heldur hámarki eða lágmarki |
| `now()` | sekúndur síðan lotan hófst |
| `meta` | orðabók sem er skrifuð í `meta.json` |
| `started`, `ended`, `folder`, `id`, `counts`, `positions` | hvenær, hvar, og hvað hefur verið skráð hingað til |

`event`, `stat` og `raw` eru þráðaöruggar og má kalla á þær úr vinnuþræði.

**Hvert millistykki geymir allt sem heimildin sendir.** Raðirnar eru það sem skoðarinn teiknar; þær eru
ekki skráin sjálf. Hver pakki sem berst á gátt, hver samnýtt minnissíða sem er lesin (allt vörpunin,
í hvert sinn sem hún breytist), hver lína í loggi eða útflutningsskriftu (líka þær sem millistykkið hunsar), hvert
JSON-svar eða sent skjal fer í `session.raw(...)` um leið og það berst, hvort sem það verður að
röð eða ekki - og ekkert er þynnt niður fyrir tíðnina sem millistykkið les á. Atriði sem berst áður en lota
er opin opnar eina (lota með aðeins hrá atriði er geymd), eða er haldið þar til ein opnast; því er aldrei
sleppt. Svið sem er ódýrt að afkóða og merking þeirra er örugg fara líka á raðirnar. Þetta er
[breytiregla](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md) 3DHeat: bein útsending er farin
um leið og hún er send, svo það sem millistykki geymir ekki er tapað fyrir fullt og allt, og það sem það geymir heilt er hægt að
afkóða daginn sem einhver skilur það. Stærðin er verðið; zstd og orðabókarkóðun halda henni
niðri, ekki að sleppa hlutum. Próf hvers millistykkis sendir eitthvað sem það notar ekki og athugar að það
komi heilt til baka úr `heat.raw.parquet`, og að `selfCheck.completeness.lost` sé 0. `racing.Driving.raw`
gerir það sama fyrir kappakstursmillistykkin (og opnar lotuna), og `racing.Pages` geymir samnýttar minnissíður
þegar bæti þeirra breytast, og telur endurlestrana sem fundu ekkert nýtt í `unchanged_reads` í `meta.json`.

Venjur sem restin af kerfinu treystir á:

- **Eigin raðir spilarans eru merktar, út frá því sem heimildin segir.** `player="me"` þar sem heimildin er
  eigin leikur spilarans; þar sem hver leikmaður er skráður undir nafni, `own_car=1` á röðum bíls spilarans
  (eftir spilaravísi leiksins eða þátttakandanum sem er skoðaður), eða nafn spilarans sem `session.meta["player"]`
  (skrifað strax í `meta.json`) þegar heimildin nefnir spilarann. Aldrei giska: þar sem heimildin segir
  það ekki, taktu nafnið úr stillingu (`player_names`, `riot_id`) eða merktu ekkert.
  [NVIDIA hápunktar](nvidia-highlights.md) fá lánaðar staðsetningar aðeins úr slíkum röðum
  (`platform.own_row`). Aðrir leikmenn eru auðkenndir með nafni eða auðkenni.
- **Leiðir eru afmarkaðar með atburðum með staðsetningu**: `spawn`, `respawn` og `session_start` hefja eina;
  `death`, `finish`, `session_end` og `teleport` enda eina. Hvenær sem spilarinn færðist án þess að ferðast
  (endurstilling, afturspólun, hraðferð, hlaðin vistun), skrifaðu `teleport` á staðnum sem var yfirgefinn og svo
  upphaf (`spawn`, eða `respawn` fyrir endurstillingu sem leikurinn nefnir) á staðnum sem komið var á, svo línuhiti
  skoðarans endi eina leið og byrji þá næstu í stað þess að teikna þvert yfir kortið. `Driving.jumped` gerir það
  fyrir farartæki.
- **Staðsetningar haldast í eigin heimshnitum og einingum leiksins**, lýst með `axes`. Ekki
  umbreyta þeim í annan ramma nema leikurinn gefi engan nothæfan heimsramma (flughermarnir setja
  breiddar- og lengdargráðu á flatt kort, `Tangent`, í kringum fyrstu mælingu - DCS í kringum fast upphaf
  sviðsins - og senda `geo=tangent.geo()` til `open`, svo fóturinn segi hvar á jörðinni
  kortið er). `axes.scale` er einingakvarði
  skoðarans - hann margfaldar hverja staðsetningu með honum - og helst 1, svo raðirnar passi við borð sem er flutt út
  úr sama leik í sömu einingum; segðu eininguna í `axes.units`.
- **Tölfræðilyklar** eru með litlum stöfum og undirstrikum, og bera eininguna sína þar sem hún á við
  (`distance_km`, `top_speed_kmh`, `max_altitude_m`, `duration_s`). Tími sem er geymdur sem met byrjar á
  `best_` (geymdur með `min`), sæti endar á `_position`: `stats` sýnir lægsta þeirra sem
  besta, og hæsta hvers annars lykils (`db.lower_is_better`).

## Hjálparforrit {#helpers}

| Hjálparforrit | Eining | Fyrir |
|---|---|---|
| `Follower(find, since, stamp=None)`, `game_started(pid)`, `newest(paths)`, `read_shared(path)`, `steam_libraries()` | `_logfollow` | að fylgja loggi sem leikurinn skrifar: samnýttir lestrar, aðeins línur þessarar setu, nýjar og endurnýjaðar skrár, aðeins heilar línur |
| `UdpPort(port, forward=None, grace=0.0, recheck=3.0)` með `try_open(who)`, `receive()`, `close()` | `racing` | UDP fjarmælingagátt á 127.0.0.1, aðeins tekin þegar hún er laus, látin öðru forriti í té, valfrjálst endursend |
| `Driving(adapter, ctx, hz=10.0, jump=50.0)` með `sample(...)`, `event(...)`, `lap(...)`, `count(...)`, `close()` | `racing` | farartækjalotur: staðsetningar á föstum hraða, vegalengd, hámarkshraði, hringir; við stökk, `teleport` þar sem bíllinn var og `spawn` þar sem hann er (`jumped(...)`) |
| `SharedView.open(name)` | `simracing_shm` | nefnt samnýtt minni leiks, aðeins lesið, aldrei búið til |
| `ReplayAdapter` (`patterns`, `folders(ctx)`, `convert(path, ctx)`) | `replays` | vöktuð endursýningarmappa: skrár umbreyttar þegar þær hætta að stækka, í vinnuþræði; fyrsta litið skráir aðeins hvað er þar, og `convert_existing(ctx, folder=None)` - skipunin [`replays`](commands.md#replays) - umbreytir þeim að beiðni |
| `load_state`, `save_state` | `platform` | að muna hvað alltaf-í-gangi millistykki hefur séð, í `<data>\state\<id>.json` |
| `FlightLog`, `Tangent` | `xplane` | bókhald flugs (flugtök, lendingar, brotlendingar, vegalengd) og flata kortið í kringum fyrstu mælingu (`Tangent.geo()` er `geo` lotunnar) |
| `backup_once(path)` | `gsi`, `racing` | reglan um `<file>.heat3d-backup` |
| Skrár Steam | `_steam` | tvíundar og texta KeyValues, Steam-mappan úr nýskráningunni |

Lágmarks logg-millistykki, til útskýringar (tilbúinn leikur):

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

Opnaðu lotuna með því fyrsta sem er þess virði að skrá, ekki í `start`, svo leikur sem er skilinn eftir í valmyndum
skilur ekkert eftir (tóm lota er samt eytt).

## Prófanir {#tests}

```bash
python -m pytest
```

`tests/conftest.py` gefur hverju prófi einnota gagnamöppu (`HEAT3D_WATCH_HOME`) og slekkur á
útgáfuleit og tilkynningum (`HEAT3D_NO_UPDATE`, `HEAT3D_NO_TOAST`). Millistykkispróf byggir
úttak leiksins út frá útgefnu sniði hans - pakka úr forskriftinni, logglínur í sniði leiksins,
skrár í skjalfestu skipulagi - og keyrir millistykkið beint (stytt úr
`tests/test_poe.py`; `data` og `install` eru tímabundnar möppur):

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

Netmillistykki eru prófuð gegn gervi staðbundnum þjóni eða með pökkum sem eru sendir yfir UDP til millistykkisins.
Próf sem bera saman við raunveruleg leikjagögn á vél þróunaraðilans eru merkt `@pytest.mark.local` og
er sleppt þar sem þau gögn vantar. Þau gögn fara aldrei í geymsluna. `test_core.py` geymir líka
prófið sem fellur ef einhver kóði sem gæti skrifað í annað ferli birtist í pakkanum
(`test_memory_reading_cannot_write`).

## Heiðarlegt `verified` {#an-honest-verified}

`verified` segir hvað var athugað og hvernig, og hvað var ekki athugað. Það er sýnt af `games` og á hverri leikjasíðu,
og spilarar reiða sig á það. Dæmi úr kóðanum:

- "tested on packets in the 2023, 2024 and 2025 formats built from EA's published specification, sent
  over UDP; untested against the game"
- "tested on documents in the published GSI format posted to the running adapter; untested against the
  running game"
- "tested on real stats files and schemas from a local install; change detection tested on files built
  in the binary KeyValues format"

Segðu „untested against the game“ þar til millistykkið hefur skráð leikinn í gangi. Nefndu aðeins aðferðina og
vikmörkin: aldrei kort, leikjaauðkenni, nafn leikmanns, dagsetningu, stærð safns eða nákvæma talningu úr raunverulegum
skrám, og aldrei „þessa vél“ (lesendur þekkja hana ekki). Nefndu heimild hvers
offsets og skipulags, og segðu hvar tvær heimildir voru bornar saman. Fullyrtu aldrei meira en var gert. Snið
sem var giskað á eða tekið úr samfélagstólum er sagt vera það.

## Leikjasíðurnar {#the-game-pages}

Hver síða undir [Leikir](games.md) er búin til úr millistykkjunum, svo hún passar alltaf við kóðann. Eftir að
þú bætir við eða breytir millistykki skaltu endurgera þær úr möppu geymslunnar:

```bash
HEAT3D_NO_UPDATE=1 python tools/gen_game_pages.py
```

(Í PowerShell: `$env:HEAT3D_NO_UPDATE = "1"; python tools/gen_game_pages.py`.) Bættu við `--check` til að aðeins
bera saman: það skrifar ekkert og hættir með 1 þegar síða er úrelt (líka leikjataflan í `docs/watcher.md`).

Skriftan:

- hleður millistykkjunum með `heat3d_watch.adapters.load()`, gegn tómri tímabundinni gagnamöppu, svo
  ekkert minnissnið eða stilling á þinni vél endar á síðunum. Minnismillistykki eru skilin eftir úti,
  því þau koma úr eigin sniðum spilara;
- neitar að skrifa nokkuð ef millistykkiseining tekst ekki að flytja inn (síðurnar myndu missa þá leiki);
- skrifar `docs/game-<adapter id>.md` fyrir hvert millistykki og `docs/games.md` með yfirlitstöflunni, og
  eyðir síðum millistykkja sem eru ekki lengur til;
- tekur „What is recorded“, „Where it comes from“, „How to switch it on“, ásana, multiplayer-
  fánann og „Verified“ úr sviðum millistykkisins;
- breytir docstring einingarinnar í „How it works“. Skrifaðu docstrings í látlausa textastílnum sem
  einingarnar nota þegar, sem skriftan umbreytir: málsgreinar; listar með `*`, `-` eða `1.`; skipulag og
  dæmi inndregin undir línunni sem kynnir þau (þau verða kóðablokkir); titill undirstrikaður
  með strikum, eða stutt titillína með textanum inndregnum beint undir (þau verða fyrirsagnir);
- telur upp tölfræðilyklana sem kóði millistykkisins stillir með nafni - `.stat("key", ...)`, báðar hliðar
  `if` segðar, og f-strengjamynstur eins og `score.{team}` - í klösum millistykkisins og í
  hjálparforritunum sem þeir nota. Lyklar teknir úr breytu (tafla yfir svið leiksins) eru ekki taldir upp;
- ákveður „Positions“ út frá `axes.units` millistykkisins (athugasemd sem byrjar á „no“ eða „none“ þýðir engar
  staðsetningar) og út frá því sem kóði þess skrifar.

Ekki breyta búnu síðunum í höndunum: breyttu millistykkinu og keyrðu skriftuna aftur. Taflan í
[Allir leikir í einni töflu](watcher.md) er úttak `python -m heat3d_watch games --markdown`.
