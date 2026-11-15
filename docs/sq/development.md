---
title: "Zhvillimi"
nav_order: 12
lang: "sq"
source: development.md
source_hash: "cb213e22ddea"
nav_exclude: true
search_exclude: true
---
# Zhvillimi {#development}

Kjo faqe është për shtimin e një loje: si ndërtohet një adapter, si testohet, dhe si bëhet dokumentacioni i tij.

## Depoja {#the-repository}

| Rruga | Çfarë mban |
|---|---|
| `heat3d_watch/cli.py` | komandat ([Komandat](commands.md)) |
| `heat3d_watch/watcher.py` | cikli në sfond: lista e proceseve, një thread për adapter, përditësimet |
| `heat3d_watch/session.py` | një regjistrim: `events.jsonl`, `heat.parquet`, `meta.json`, rikuperimi |
| `heat3d_watch/db.py` | `watcher.sqlite` |
| `heat3d_watch/config.py` | cilësimet dhe dosja e të dhënave |
| `heat3d_watch/safety.py`, `heat3d_watch/memory.py` | kontrollet e memories dhe lexuesi vetëm për lexim ([Leximi i memories](memory-reading.md)) |
| `heat3d_watch/notify.py` | njoftimet e Windows |
| `heat3d_watch/adapters/` | një modul për lojë ose familje lojërash; modulet që fillojnë me `_` janë ndihmës të përbashkët |
| `heat3d_watch/decoders/` | dekoduesit e telemetrisë së garave, kopjuar nga regjistruesit e xhirove të 3DHeat GameCapture |
| `heat3d_update/` | përditësuesi ([Përditësimet](updates.md)) |
| `mods/beamng/heat3d/` | moda e protokollit BeamNG që e instalon `setup beamng` |
| `tests/` | testet |
| `tools/gen_game_pages.py` | shkruan faqet e lojërave të këtij dokumentacioni |

## Një adapter {#an-adapter}

Një adapter është një dataclass i derivuar nga `heat3d_watch.adapters.base.Adapter`. Fushat e tij thonë çfarë
është; metodat e tij bëjnë punën.

| Fusha | Parazgjedhja | Çfarë është |
|---|---|---|
| `id` | `""` | e shkurtër dhe e qëndrueshme: dosjet e seancave, `disabled`, `replay_folders` dhe `player_names` i referohen asaj |
| `game` | `""` | emri i lojës siç e shkruajnë njerëzit; seancat arkivohen nën të |
| `kind` | `"telemetry"` | një nga `telemetry`, `gsi`, `log`, `replay`, `platform`, `memory` ([Burimet dhe rregullat](sources-and-rules.md)) |
| `exes` | `()` | emrat e ekzekutueshmeve (çdo shkronjë) që do të thotë se loja ekzekutohet. E zbrazët: adapteri është gjithmonë aktiv (`always` është true) |
| `multiplayer` | `True` | loja luhet online: memoria e saj nuk lexohet kurrë |
| `source` | `""` | nga vijnë numrat, thënë një herë |
| `records` | `()` | çfarë regjistrohet, një element për çdo lloj gjëje |
| `enable` | `""` | si aktivizohet burimi; e zbrazët kur nuk duhet asgjë |
| `interval` | `0.1` | sekonda mes pyetjeve |
| `axes` | `Axes()` | boshti lart i botës, boshtet e pasqyruara, shkalla e njësisë së shikuesit (mbaje 1) dhe një shënim për njësitë |
| `verified` | `""` | çfarë është kontrolluar, me ndershmëri (shih më poshtë) |
| `completeness` | `{}` | llogaria e burimit sipas [rregullit të konvertuesit](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md) të 3DHeat: `read` (çfarë bëhet rreshta), `raw` (çfarë mbahet i plotë, nën cilin `type`), `missing` (çfarë nuk jep burimi, dhe pse), `size` (sa i madh bëhet burimi bruto në orë). Seksioni "Completeness" i faqes së lojës shkruhet nga ajo |

`source`, `records`, `enable`, `verified` dhe `completeness` janë dokumentacion, jo dekor. `games` i printon,
`games --markdown` bën tabelën te [Të gjitha lojërat në një tabelë](watcher.md), dhe faqet e lojërave
gjenerohen nga ato. Shkruaji që të thonë saktësisht çfarë bën kodi.

Metodat, të gjitha opsionale:

| Metoda | Thirret | Çfarë duhet të bëjë |
|---|---|---|
| `missing(self) -> str \| None` | nga `games`, `status`, dhe para nisjes | të thotë pse adapteri nuk mund të ekzekutohet këtu (një DLL nuk u gjet, një dosje mungon), ose `None` |
| `setup(self, ctx, *, apply) -> list[str]` | nga `setup` | të aktivizojë daljen e vetë lojës; të kthejë një rresht për ndryshim, dhe të ndryshojë skedarë vetëm kur `apply` është true. Bëj kopje rezervë të një skedari si `<file>.heat3d-backup` para ndryshimit të parë, dhe mos e mbishkruaj kurrë atë kopje. Mbishkruaje vetëm kur ka diçka për të aktivizuar: `can_setup` (true kur `setup` është i mbishkruar) vendos nëse `setup` e ekzekuton ose thotë se nuk ka çfarë të ndryshohet; një klasë që shërben disa lojëra mbishkruan `can_setup` për ato që nuk mund t'i konfigurojë (`RallyAdapter` për Richard Burns Rally). |
| `start(self, ctx)` | kur shfaqet procesi i lojës (adapterat gjithmonë të aktivë: kur niset `run`) | të hapë sokete, të gjejë skedarë, të mbajë mend ku të fillojë |
| `poll(self, ctx)` | çdo `interval` sekonda, në threadin e vetë adapterit | të marrë çfarë ka thënë loja që nga pyetja e fundit dhe ta regjistrojë |
| `stop(self, ctx)` | kur loja ka ikur ose watcher-i ndalon | të mbyllë seancat dhe soketet |

Çdo adapter ekzekutohet në threadin e vet (`Runner`). Një përjashtim në `poll` regjistrohet dhe adapteri pret
`min(5, interval × 10 + 0.5)` sekonda para pyetjes tjetër. Pas 20 dështimesh radhazi, ose një dështimi në
`start`, adapteri ndalohet dhe nuk niset përsëri derisa të ndryshojë id-ja e procesit të lojës.
`missing()` kontrollohet në çdo skanim, ndaj mbaje të lirë.

Një objekt adapteri ripërdoret kur loja niset përsëri, ndaj `start` duhet të rivendosë gjithçka që një ekzekutim i mëparshëm
la pas.

### Regjistrimi i tij {#registering-it}

Vendose modulin te `heat3d_watch/adapters/` dhe listo adapterat në fund të tij:

```python
ADAPTERS = [MyAdapter(id="mygame", game="My Game", ...)]
```

`adapters.load()` importon çdo modul në paketë (përveç `base` dhe emrave që fillojnë me `_`) dhe
mbledh `ADAPTERS` e tyre. Dy adaptera me të njëjtën id e ndalojnë ngarkimin me një `ValueError`. Një modul që
dështon të importohet (një varësi që mungon) i lë lojërat e tij jashtë dhe emërtohet nga `games` me gabimin, ndaj
problemi i një loje nuk i ndalon të tjerat.

## Context dhe Session {#context-and-session}

`start`, `poll`, `stop` dhe `setup` marrin një `Context`:

| Anëtari | Çfarë është |
|---|---|
| `settings` | `Settings` ([Instalimi dhe ekzekutimi](installing-and-running.md#settings)) |
| `data` | dosja e të dhënave |
| `pid`, `exe` | id-ja e procesit dhe rruga e ekzekutueshmes së lojës, kur adapteri u nis për një lojë që ekzekutohet; dosja e instalimit është pranë `exe` |
| `open(adapter, *, game=None, when=None, axes=..., source=..., multiplayer=..., meta=..., geo=None)` | një `Session` i ri. `game` mbishkruan emrin e lojës së adapterit (për adapterat që mbulojnë shumë lojëra); `when` vendos fillimin për seancat që përshkruajnë të shkuarën; `axes`, `source` dhe `multiplayer` marrin parazgjedhjet e adapterit; `meta` është një fjalor që shkruhet te `meta.json`; `geo` (`{"lat0": .., "lon0": ..}`, ose vendos `session.geo` më vonë) e vendos një seancë me hartë të sheshtë në tokë, te `meta.json` dhe fundi i tabelës |
| `close(session)` | mbyll një seancë: tabelën, `heat.raw.parquet`, `meta.json`, rreshtin e saj te `watcher.sqlite`. Një seancë pa ngjarje e pa elemente raw fshihet; një me vetëm elemente raw mbahet (pa tabelë, pa rresht në bazën e të dhënave). Pranon `None`. Kthen rrugën e tabelës ose `None`. |

Një `Session` regjistron:

| Anëtari | Çfarë bën |
|---|---|
| `event(name, *, t=None, ms=None, x=None, y=None, z=None, player=None, team=None, session=None, **attrs)` | një rresht. `t` ka parazgjedhje sekondat që nga fillimi i seancës, `ms` tani. Një pozicion llogaritet vetëm kur `x`, `y` dhe `z` janë dhënë të tria dhe janë të fundme. Atributet `None` lihen jashtë. |
| `position(x, y, z, **kw)` | një ngjarje me emrin `position` |
| `raw(type, payload=None, *, text=None, used=False, t=None, ms=None, **fields)` | mban një gjë që dërgoi burimi, të plotë: bajtet e një pakete ose faqeje (`payload`), një rresht ose një përgjigje JSON siç erdhi (`text`), ose vlerat e një leximi sipas emrit (`fields`, secila kolonë më vete). `type` është fjala e vetë burimit për të (një id pakete, emri i një mapimi, një ngjarje ditari, një endpoint); `used` thotë se u bë edhe rreshta. Futet në `raw.bin` në çastin kur thirret, shkruhet si `heat.raw.parquet` (zstd) kur seanca mbyllet ose rikuperohet, dhe numërohet sipas `type` te `selfCheck.completeness` i `meta.json` |
| `stat(key, value, how="set")` | një statistikë: `set` e vendos, `add` i shton, mban `max` ose `min` |
| `now()` | sekonda që nga fillimi i seancës |
| `meta` | një fjalor që shkruhet te `meta.json` |
| `started`, `ended`, `folder`, `id`, `counts`, `positions` | kur, ku, dhe çfarë u regjistrua deri tani |

`event`, `stat` dhe `raw` janë thread-safe dhe mund të thirren nga një thread punëtor.

**Çdo adapter mban gjithçka që dërgon burimi i tij.** Rreshtat janë ato që vizaton shikuesi; nuk janë
regjistri. Çdo paketë që arrin një port, çdo faqe memorieje e përbashkët e lexuar (i gjithë mapimi,
çdo herë që ndryshon), çdo rresht i një logu ose skripti eksporti (edhe ato që adapteri i injoron), çdo
përgjigje JSON ose dokument i postuar shkon te `session.raw(...)` siç mbërrin, qoftë se bëhet
rresht apo jo - dhe asgjë nuk hollohet nën shpejtësinë me të cilën lexon adapteri. Një element që mbërrin para se një seancë
të jetë e hapur e hap një (një seancë me vetëm elemente raw mbahet), ose mbahet derisa të hapet një; nuk
hidhet kurrë. Fushat që janë të lira për t'u dekoduar dhe të sigurta në kuptim shkojnë edhe te rreshtat. Ky është
[rregulli i konvertuesit](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md) i 3DHeat: një burim live humbet
në çastin kur dërgohet, ndaj ajo që një adapter nuk e mban humbet përgjithmonë, dhe ajo që mban të plotë mund të
dekodohet ditën kur dikush e kupton. Madhësia është çmimi; zstd dhe kodimi me fjalor e mbajnë
poshtë, jo lënia jashtë e gjërave. Testi i secilit adapter dërgon diçka që nuk e përdor dhe kontrollon që kthehet
i plotë nga `heat.raw.parquet`, dhe që `selfCheck.completeness.lost` është 0. `racing.Driving.raw`
bën të njëjtën për adapterat e garave (dhe hap seancën), dhe `racing.Pages` mban faqet e memories së përbashkët
sa herë që bajtet e tyre ndryshojnë, duke numëruar rileximet që nuk gjetën asgjë të re te `unchanged_reads` i `meta.json`.

Konventat mbi të cilat mbështetet pjesa tjetër e sistemit:

- **Rreshtat e vetë lojtarit shënohen, nga ajo që thotë burimi.** `player="me"` aty ku burimi është
  i vetë lojtarit; aty ku çdo lojtar regjistrohet nën një emër, `own_car=1` te rreshtat e makinës së lojtarit
  (sipas indeksit të lojtarit të lojës ose pjesëmarrësit të shikuar), ose emri i lojtarit si `session.meta["player"]`
  (shkruhet menjëherë te `meta.json`) kur burimi e emërton lojtarin. Kurrë mos merr me mend: aty ku burimi nuk
  e thotë, merre emrin nga një cilësim (`player_names`, `riot_id`) ose mos shëno asgjë.
  [NVIDIA highlights](nvidia-highlights.md) marrin pozicione hua vetëm nga rreshta të tillë
  (`platform.own_row`). Lojtarët e tjerë shkojnë me emrin ose id-në e tyre.
- **Rrugët kufizohen nga ngjarje me pozicione**: `spawn`, `respawn` dhe `session_start` fillojnë një;
  `death`, `finish`, `session_end` dhe `teleport` mbarojnë një. Sa herë që lojtari lëvizi pa udhëtuar
  (një rivendosje, një rikthim, një udhëtim i shpejtë, një ruajtje e ngarkuar), shkruaj `teleport` te vendi i lënë dhe pastaj një
  fillim (`spawn`, ose `respawn` për një rivendosje që loja e emërton) te vendi ku mbërriti, që nxehtësia e vijës
  e shikuesit të mbarojë një rrugë dhe të fillojë tjetrën në vend që të vizatojë përtej hartës. `Driving.jumped` e bën këtë
  për automjetet.
- **Pozicionet mbeten në koordinatat dhe njësitë e botës së vetë lojës**, të përshkruara nga `axes`. Mos i
  konverto në një kuadër tjetër përveç nëse loja nuk jep kuadër bote të përdorshëm (simulatorët e fluturimit e vendosin
  gjerësinë dhe gjatësinë gjeografike në një hartë të sheshtë, `Tangent`, rreth pikës së parë - DCS rreth origjinës
  fikse të teatrit të vet - dhe i kalojnë `geo=tangent.geo()` te `open`, ndaj fundi thotë ku në tokë është
  harta). `axes.scale` është shkalla e njësisë së shikuesit
  - e shumëzon çdo pozicion me të - dhe mbetet 1, që rreshtat të përputhen me një nivel të eksportuar
  nga e njëjta lojë në të njëjtat njësi; thuaje njësinë te `axes.units`.
- **Çelësat e statistikave** janë me shkronja të vogla me nënvija, dhe mbajnë njësinë e tyre aty ku vlen
  (`distance_km`, `top_speed_kmh`, `max_altitude_m`, `duration_s`). Një kohë e mbajtur si më e mira fillon me
  `best_` (mbahet me `min`), një vend mbaron me `_position`: `stats` tregon më të ulëtën e tyre si
  më të mirën, dhe më të lartën e çdo çelësi tjetër (`db.lower_is_better`).

## Ndihmësit {#helpers}

| Ndihmësi | Moduli | Për |
|---|---|---|
| `Follower(find, since, stamp=None)`, `game_started(pid)`, `newest(paths)`, `read_shared(path)`, `steam_libraries()` | `_logfollow` | ndjekjen e një logu që shkruan loja: lexime të përbashkëta, vetëm rreshtat e kësaj uljeje, skedarë të rinj e të zëvendësuar, vetëm rreshta të plotë |
| `UdpPort(port, forward=None, grace=0.0, recheck=3.0)` me `try_open(who)`, `receive()`, `close()` | `racing` | një port telemetrie UDP në 127.0.0.1, i marrë vetëm kur është i lirë, i lëshuar për një program tjetër, opsionalisht i transmetuar |
| `Driving(adapter, ctx, hz=10.0, jump=50.0)` me `sample(...)`, `event(...)`, `lap(...)`, `count(...)`, `close()` | `racing` | seanca automjetesh: pozicione me shpejtësi fikse, largësi, shpejtësi maksimale, xhiro; në një kërcim, `teleport` ku ishte makina dhe `spawn` ku është (`jumped(...)`) |
| `SharedView.open(name)` | `simracing_shm` | memoria e përbashkët e emërtuar e një loje, vetëm për lexim, nuk krijohet kurrë |
| `ReplayAdapter` (`patterns`, `folders(ctx)`, `convert(path, ctx)`) | `replays` | një dosje riluajtjesh e vëzhguar: skedarët konvertohen sapo ndalojnë së rrituri, në një thread punëtor; shikimi i parë vetëm shënon çfarë ka aty, dhe `convert_existing(ctx, folder=None)` - komanda [`replays`](commands.md#replays) - i konverton ato sipas kërkesës |
| `load_state`, `save_state` | `platform` | mbajtja mend e asaj që ka parë një adapter gjithmonë aktiv, në `<data>\state\<id>.json` |
| `FlightLog`, `Tangent` | `xplane` | llogaritja e fluturimit (ngritje, uljet, rrëzime, largësi) dhe harta e sheshtë rreth pikës së parë (`Tangent.geo()` është `geo` i seancës) |
| `backup_once(path)` | `gsi`, `racing` | rregulli `<file>.heat3d-backup` |
| Skedarët e Steam | `_steam` | KeyValues binare e tekst, dosja Steam nga regjistri |

Një adapter minimal logu, si ilustrim (një lojë e shpikur):

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

Hape seancën me gjënë e parë që ia vlen të regjistrohet, jo te `start`, që një lojë e lënë në menutë e saj
të mos lërë asgjë pas (një seancë e zbrazët fshihet gjithsesi).

## Testet {#tests}

```bash
python -m pytest
```

`tests/conftest.py` i jep çdo testi një dosje të dhënash të përkohshme (`HEAT3D_WATCH_HOME`) dhe çaktivizon
kontrollet e përditësimit dhe njoftimet (`HEAT3D_NO_UPDATE`, `HEAT3D_NO_TOAST`). Një test adapteri ndërton
daljen e lojës nga formati i saj i botuar - paketa nga specifikimi, rreshta logu në formatin e lojës,
skedarë në strukturën e dokumentuar - dhe e drejton adapterin drejtpërdrejt (shkurtuar nga
`tests/test_poe.py`; `data` dhe `install` janë dosje të përkohshme):

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

Adapterat e rrjetit testohen kundrejt një serveri lokal të rremë ose me paketa të dërguara me UDP te adapteri.
Testet që kontrollojnë kundrejt të dhënave të vërteta të lojës në kompjuterin e zhvilluesit shënohen `@pytest.mark.local` dhe
kapërcehen aty ku ato të dhëna mungojnë. Ato të dhëna nuk hyjnë kurrë në depo. `test_core.py` mban gjithashtu
testin që dështon nëse çdo kod që mund të shkruante në një proces tjetër shfaqet në paketë
(`test_memory_reading_cannot_write`).

## Një `verified` i ndershëm {#an-honest-verified}

`verified` thotë çfarë u kontrollua dhe si, dhe çfarë jo. Shfaqet nga `games` dhe në çdo faqe loje, dhe
lojtarët mbështeten te ai. Shembuj nga kodi:

- "tested on packets in the 2023, 2024 and 2025 formats built from EA's published specification, sent
  over UDP; untested against the game"
- "tested on documents in the published GSI format posted to the running adapter; untested against the
  running game"
- "tested on real stats files and schemas from a local install; change detection tested on files built
  in the binary KeyValues format"

Thuaj "untested against the game" derisa adapteri të ketë regjistruar lojën që ekzekutohet. Thuaj vetëm metodën dhe
tolerancën: kurrë një hartë, id ndeshjeje, emër lojtari, datë, madhësi korpusi ose numër të saktë nga skedarë
të vërtetë, dhe kurrë "this machine" (lexuesit nuk e njohin). Emërto burimin e
çdo offset-i dhe strukture, dhe thuaj ku u krahasuan dy burime. Mos pretendo kurrë më shumë se u bë. Një
format që u mendua ose u mor nga mjete të komunitetit thuhet se është i tillë.

## Faqet e lojërave {#the-game-pages}

Çdo faqe nën [Lojërat](games.md) gjenerohet nga adapterat, ndaj përputhet gjithmonë me kodin. Pasi
të shtosh ose ndryshosh një adapter, rigjeneroji nga dosja e depos:

```bash
HEAT3D_NO_UPDATE=1 python tools/gen_game_pages.py
```

(Në PowerShell: `$env:HEAT3D_NO_UPDATE = "1"; python tools/gen_game_pages.py`.) Shto `--check` që vetëm të
krahasojë: nuk shkruan asgjë dhe del me 1 kur një faqe është e vjetruar (edhe tabela e lojërave te `docs/watcher.md`).

Skripti:

- ngarkon adapterat me `heat3d_watch.adapters.load()`, kundrejt një dosjeje të dhënash të përkohshme bosh, ndaj
  asnjë profil memorieje ose cilësim në kompjuterin tënd nuk përfundon në faqe. Adapterat e memories lihen jashtë,
  pasi vijnë nga profilet e vetë lojtarëve;
- refuzon të shkruajë ndonjë gjë nëse një modul adapteri dështon të importohet (faqet do t'i humbnin ato lojëra);
- shkruan `docs/game-<adapter id>.md` për çdo adapter dhe `docs/games.md` me tabelën e pasqyrës, dhe
  fshin faqet e adapterave që nuk ekzistojnë më;
- merr "What is recorded", "Where it comes from", "How to switch it on", boshtet, flamurin multiplayer
  dhe "Verified" nga fushat e adapterit;
- e kthen docstring-un e modulit në "How it works". Shkruaj docstring-et në stilin e tekstit të thjeshtë që
  modulet e përdorin tashmë, të cilin skripti e konverton: paragrafë; lista me `*`, `-` ose `1.`; struktura dhe
  shembuj me kalim të brendshëm nën rreshtin që i prezanton (bëhen blloqe kodi); një titull i nënvizuar
  me viza, ose një rresht i shkurtër titulli me tekstin e tij me kalim të brendshëm drejtpërdrejt nën të (bëhen tituj);
- liston çelësat e statistikave që kodi i adapterit vendos me emër - `.stat("key", ...)`, të dyja anët e një
  shprehjeje `if`, dhe modele f-string si `score.{team}` - në klasat e adapterit dhe në
  ndihmësit që përdor. Çelësat e marrë nga një ndryshore (një tabelë e fushave të lojës) nuk listohen;
- vendos "Positions" nga `axes.units` i adapterit (një shënim që fillon me "no" ose "none" do të thotë pa
  pozicione) dhe nga ajo që shkruan kodi i tij.

Mos i redakto faqet e gjeneruara me dorë: ndrysho adapterin dhe ekzekuto përsëri skriptin. Tabela te
[Të gjitha lojërat në një tabelë](watcher.md) është dalja e `python -m heat3d_watch games --markdown`.
