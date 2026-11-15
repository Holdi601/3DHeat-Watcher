---
title: "Udvikling"
nav_order: 12
lang: "da"
source: development.md
source_hash: "cb213e22ddea"
nav_exclude: true
search_exclude: true
---
# Udvikling {#development}

Denne side handler om at tilføje et spil: hvordan en adapter er bygget, hvordan den testes, og hvordan dens
dokumentation laves.

## Depotet {#the-repository}

| Sti | Hvad den indeholder |
|---|---|
| `heat3d_watch/cli.py` | kommandoerne ([Kommandoer](commands.md)) |
| `heat3d_watch/watcher.py` | baggrundsløkken: proceslisten, én tråd pr. adapter, opdateringer |
| `heat3d_watch/session.py` | en optagelse: `events.jsonl`, `heat.parquet`, `meta.json`, gendannelse |
| `heat3d_watch/db.py` | `watcher.sqlite` |
| `heat3d_watch/config.py` | indstillingerne og datamappen |
| `heat3d_watch/safety.py`, `heat3d_watch/memory.py` | hukommelseskontrollerne og den skrivebeskyttede læser ([Læsning af hukommelse](memory-reading.md)) |
| `heat3d_watch/notify.py` | Windows-meddelelser |
| `heat3d_watch/adapters/` | ét modul pr. spil eller spilfamilie; moduler, der starter med `_`, er fælles hjælpere |
| `heat3d_watch/decoders/` | dekoderne til racing-telemetri, kopieret fra 3DHeat GameCapture's lap-optagere |
| `heat3d_update/` | opdateringsprogrammet ([Opdateringer](updates.md)) |
| `mods/beamng/heat3d/` | BeamNG-protokolmodet, som `setup beamng` installerer |
| `tests/` | testene |
| `tools/gen_game_pages.py` | skriver spilsiderne i denne dokumentation |

## En adapter {#an-adapter}

En adapter er en dataclass, afledt af `heat3d_watch.adapters.base.Adapter`. Dens felter siger, hvad den er; dens
metoder gør arbejdet.

| Felt | Standard | Hvad det er |
|---|---|---|
| `id` | `""` | kort og stabil: sessionsmapper, `disabled`, `replay_folders` og `player_names` henviser til den |
| `game` | `""` | spillets navn, som folk skriver det; sessioner gemmes under det |
| `kind` | `"telemetry"` | en af `telemetry`, `gsi`, `log`, `replay`, `platform`, `memory` ([Kilder og regler](sources-and-rules.md)) |
| `exes` | `()` | programnavne (uanset store og små bogstaver), der betyder, at spillet kører. Tom: adapteren er altid aktiv (`always` er sand) |
| `multiplayer` | `True` | spillet spilles online: dets hukommelse læses aldrig |
| `source` | `""` | hvor tallene kommer fra, sagt én gang |
| `records` | `()` | hvad der optages, ét punkt pr. slags ting |
| `enable` | `""` | hvordan kilden slås til; tom, når intet er nødvendigt |
| `interval` | `0.1` | sekunder mellem spørgsmålene |
| `axes` | `Axes()` | verdenens op-akse, spejlede akser, fremviserens enhedsskala (behold 1) og en note om enhederne |
| `verified` | `""` | hvad der er kontrolleret, ærligt (se nedenfor) |
| `completeness` | `{}` | kildens redegørelse efter 3DHeats [konverterregel](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md): `read` (hvad der bliver til rækker), `raw` (hvad der gemmes helt, under hvilken `type`), `missing` (hvad kilden ikke giver, og hvorfor), `size` (hvor stort det rå feed bliver på en time). Spilsiden's afsnit "Completeness" skrives ud fra den |

`source`, `records`, `enable`, `verified` og `completeness` er dokumentation, ikke pynt. `games` udskriver dem,
`games --markdown` laver tabellen i [Alle spil i én tabel](watcher.md), og spilsiderne genereres ud fra dem.
Skriv dem, så de siger præcis, hvad koden gør.

Metoderne, alle valgfrie:

| Metode | Kaldes | Hvad den bør gøre |
|---|---|---|
| `missing(self) -> str \| None` | af `games`, `status` og før start | sig, hvorfor adapteren ikke kan køre her (en DLL ikke fundet, en mappe mangler), eller `None` |
| `setup(self, ctx, *, apply) -> list[str]` | af `setup` | slå spillets eget output til; returnér én linje pr. ændring, og ændr kun filer, når `apply` er sand. Tag en backup som `<file>.heat3d-backup` før første ændring, og overskriv aldrig den backup. Overskriv kun, når der er noget at slå til: `can_setup` (sand, når `setup` er overskrevet) afgør, om `setup` kører den, eller siger, at der intet er at ændre; en klasse, der dækker flere spil, overskriver `can_setup` for dem, den ikke kan opsætte (`RallyAdapter` for Richard Burns Rally). |
| `start(self, ctx)` | når spillets proces dukker op (altid-aktive adaptere: når `run` starter) | åbn sokler, find filer, husk hvor der skal begyndes |
| `poll(self, ctx)` | hvert `interval` sekund, i adapterens egen tråd | tag det, spillet har sagt siden sidste spørgsmål, og optag det |
| `stop(self, ctx)` | når spillet er væk, eller watcheren stopper | luk sessioner og sokler |

Hver adapter kører i sin egen tråd (`Runner`). En undtagelse i `poll` logges, og adapteren venter
`min(5, interval × 10 + 0.5)` sekunder før næste spørgsmål. Efter 20 fejl i træk, eller en fejl i `start`, stoppes
adapteren og startes ikke igen, før spillets proces-id ændrer sig. `missing()` kontrolleres ved hver scanning,
så hold den billig.

En adapterobjekt genbruges, når dets spil starter igen, så `start` skal nulstille alt, en tidligere kørsel
efterlod.

### Registrering {#registering-it}

Læg modulet i `heat3d_watch/adapters/` og list adaptererne til sidst:

```python
ADAPTERS = [MyAdapter(id="mygame", game="My Game", ...)]
```

`adapters.load()` importerer hvert modul i pakken (undtagen `base` og navne, der starter med `_`) og samler deres
`ADAPTERS`. To adaptere med samme id stopper indlæsningen med en `ValueError`. Et modul, der ikke kan importeres
(en manglende afhængighed), udelader sine spil og nævnes af `games` med fejlen, så ét spils problem ikke stopper
de andre.

## Kontekst og Session {#context-and-session}

`start`, `poll`, `stop` og `setup` får en `Context`:

| Medlem | Hvad det er |
|---|---|
| `settings` | `Settings` ([Installation og kørsel](installing-and-running.md#settings)) |
| `data` | datamappen |
| `pid`, `exe` | spillets proces-id og programsti, når adapteren blev startet for et kørende spil; installationsmappen ligger ved siden af `exe` |
| `open(adapter, *, game=None, when=None, axes=..., source=..., multiplayer=..., meta=..., geo=None)` | en ny `Session`. `game` overstyrer adapterens spilnavn (for adaptere, der dækker mange spil); `when` sætter starten for sessioner, der beskriver fortiden; `axes`, `source` og `multiplayer` er som standard adapterens; `meta` er en ordbog, der skrives til `meta.json`; `geo` (`{"lat0": .., "lon0": ..}`, eller sæt `session.geo` senere) placerer en session på et fladt kort på jorden, i `meta.json` og i tabellens fodnote |
| `close(session)` | afslut en session: tabellen, `heat.raw.parquet`, `meta.json` og dens linje i `watcher.sqlite`. En session uden hverken hændelser eller rå elementer slettes; en med kun rå elementer beholdes (ingen tabel, ingen linje i databasen). Accepterer `None`. Returnerer tabellens sti eller `None`. |

En `Session` optager:

| Medlem | Hvad det gør |
|---|---|
| `event(name, *, t=None, ms=None, x=None, y=None, z=None, player=None, team=None, session=None, **attrs)` | én række. `t` er som standard sekunder siden sessionens start, `ms` er nu. En position tæller kun, når `x`, `y` og `z` alle er givet og endelige. `None`-attributter udelades. |
| `position(x, y, z, **kw)` | en hændelse ved navn `position` |
| `raw(type, payload=None, *, text=None, used=False, t=None, ms=None, **fields)` | gem ét ting, kilden sendte, helt: en pakkes eller sides bytes (`payload`), en linje eller et JSON-svar, som det kom (`text`), eller en læsnings værdier efter navn (`fields`, hver sin kolonne). `type` er kildens eget ord for det (et pakke-id, et mappings navn, en journalhændelse, et endpoint); `used` siger, at det også blev til rækker. Indrammes til `raw.bin` i det øjeblik, det kaldes, skrives ud som `heat.raw.parquet` (zstd), når sessionen lukkes eller gendannes, og tælles pr. `type` i `meta.json`s `selfCheck.completeness` |
| `stat(key, value, how="set")` | en statistik: `set` den, `add` til den, behold `max` eller `min` |
| `now()` | sekunder siden sessionens start |
| `meta` | en ordbog, der skrives til `meta.json` |
| `started`, `ended`, `folder`, `id`, `counts`, `positions` | hvornår, hvor, og hvad der er optaget indtil nu |

`event`, `stat` og `raw` er trådsikre og kan kaldes fra en arbejdstråd.

**Hver adapter gemmer alt, kilden sender.** Rækkerne er det, fremviseren tegner; de er ikke optagelsen. Hver pakke,
der når en port, hver delt hukommelsesside, der læses (hele mappingen, hver gang den ændres), hver linje i et log
eller eksportscript (også dem adapteren ignorerer), hvert JSON-svar eller hvert sendt dokument går til
`session.raw(...)`, når det kommer - uanset om det bliver til en række - og intet tyndes under den hastighed,
adapteren læser med. Et element, der kommer, før en session er åben, åbner en (en session med kun rå elementer
beholdes), eller holdes, indtil en åbnes; det kastes aldrig. Felter, der er billige at afkode og sikre i betydningen,
lægges også på rækkerne. Dette er 3DHeats [konverterregel](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md):
et live-feed er væk i det øjeblik, det er sendt, så det, en adapter ikke gemmer, er tabt for altid, og det, den
gemmer helt, kan afkodes den dag, nogen forstår det. Prisen er størrelsen; zstd og ordbogskodning holder den nede,
i stedet for at udelade ting. Hver adapters test sender noget, den ikke bruger, og kontrollerer, at det kommer
tilbage helt fra `heat.raw.parquet`, og at `selfCheck.completeness.lost` er 0. `racing.Driving.raw` gør det samme for
racingadaptere (og åbner sessionen), og `racing.Pages` gemmer delte hukommelsessider, når deres bytes ændrer sig, og
tæller de genlæsninger, der ikke fandt noget nyt, i `meta.json`s `unchanged_reads`.

Konventioner, som resten af systemet bygger på:

- **Spillerens egne rækker markeres ud fra, hvad kilden siger.** `player="me"`, hvor kilden er spillerens egen; hvor
  hver spiller optages under et navn, `own_car=1` på spillerens bils rækker (efter spillets spillerbil-indeks eller
  den viste deltager), eller spillerens navn som `session.meta["player"]` (skrevet til `meta.json` med det samme),
  når kilden nævner spilleren. Gæt aldrig: hvor kilden ikke siger det, tag navnet fra en indstilling (`player_names`,
  `riot_id`), eller markér intet. [NVIDIA-højdepunkter](nvidia-highlights.md) låner kun positioner fra sådanne rækker
  (`platform.own_row`). Andre spillere genkendes på navn eller id.
- **Ruter afgrænses af hændelser med positioner**: `spawn`, `respawn` og `session_start` begynder en; `death`, `finish`,
  `session_end` og `teleport` afslutter en. Når spilleren er flyttet uden at rejse (en nulstilling, et tilbagespol, en
  hurtigrejse, en indlæst gemning), skriv `teleport` ved stedet, der blev forladt, og derefter en start (`spawn`, eller
  `respawn` for en nulstilling, spillet nævner) ved stedet, der blev nået, så fremviserens linjevarme afslutter den ene
  rute og begynder den næste, i stedet for at tegne hen over kortet. `Driving.jumped` gør det for køretøjer.
- **Positioner forbliver i spillets egne verdenskoordinater og enheder**, beskrevet af `axes`. Omregn dem ikke til et
  andet koordinatsystem, medmindre spillet ikke giver en brugbar verdensramme (flysimulatorerne lægger bredde- og
  længdegrad ind i et fladt kort, `Tangent`, omkring første fix - DCS omkring teatrets faste origo - og sender
  `geo=tangent.geo()` til `open`, så fodnoten siger, hvor på jorden kortet ligger). `axes.scale` er fremviserens
  enhedsskala - den ganger hver position med den - og bliver 1, så rækkerne passer til et level, der er eksporteret fra
  det samme spil i de samme enheder; sig enheden i `axes.units`.
- **Statistiknøgler** er små bogstaver med understreger og bærer deres enhed, hvor en gælder (`distance_km`,
  `top_speed_kmh`, `max_altitude_m`, `duration_s`). En tid, der gemmes som bedste, starter med `best_` (gemmes med `min`),
  en placering slutter med `_position`: `stats` viser den laveste af dem som bedst, og den højeste af alle andre nøgler
  (`db.lower_is_better`).

## Hjælpere {#helpers}

| Hjælper | Modul | Til |
|---|---|---|
| `Follower(find, since, stamp=None)`, `game_started(pid)`, `newest(paths)`, `read_shared(path)`, `steam_libraries()` | `_logfollow` | at følge et log, spillet skriver: delte læsninger, kun denne omgangs linjer, nye og erstattede filer, kun hele linjer |
| `UdpPort(port, forward=None, grace=0.0, recheck=3.0)` med `try_open(who)`, `receive()`, `close()` | `racing` | en UDP-telemetriport på 127.0.0.1, kun taget når den er ledig, overgivet til et andet program, eventuelt videresendt |
| `Driving(adapter, ctx, hz=10.0, jump=50.0)` med `sample(...)`, `event(...)`, `lap(...)`, `count(...)`, `close()` | `racing` | køretøjssessioner: positioner med fast hastighed, distance, topfart, omgange; ved et hop, `teleport` hvor bilen var og `spawn` hvor den er (`jumped(...)`) |
| `SharedView.open(name)` | `simracing_shm` | et spils navngivne delte hukommelse, skrivebeskyttet, aldrig oprettet |
| `ReplayAdapter` (`patterns`, `folders(ctx)`, `convert(path, ctx)`) | `replays` | en overvåget replay-mappe: filer konverteres én gang, når de holder op med at vokse, i en arbejdstråd; første kig noterer kun, hvad der er der, og `convert_existing(ctx, folder=None)` - kommandoen [`replays`](commands.md#replays) - konverterer dem efter ønske |
| `load_state`, `save_state` | `platform` | at huske, hvad en altid-aktiv adapter har set, i `<data>\state\<id>.json` |
| `FlightLog`, `Tangent` | `xplane` | flight-bogføring (start, landinger, nedstyrtninger, distance) og det flade kort omkring første fix (`Tangent.geo()` er sessionens `geo`) |
| `backup_once(path)` | `gsi`, `racing` | reglen `<file>.heat3d-backup` |
| Steams filer | `_steam` | binære og tekst-KeyValues, Steam-mappen fra registreringsdatabasen |

Et minimalt log-adapter, som illustration (et opdigtet spil):

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

Åbn sessionen med det første, der er værd at optage, ikke i `start`, så et spil, der bliver i sine menuer, ikke
efterlader noget (en tom session slettes alligevel).

## Tests {#tests}

```bash
python -m pytest
```

`tests/conftest.py` giver hver test en engangs-datamappe (`HEAT3D_WATCH_HOME`) og slår opdateringstjek og meddelelser
fra (`HEAT3D_NO_UPDATE`, `HEAT3D_NO_TOAST`). En adaptertest bygger spillets output ud fra dets offentliggjorte format -
pakker fra specifikationen, loglinjer i spillets format, filer i det dokumenterede layout - og kører adapteren direkte
(forkortet fra `tests/test_poe.py`; `data` og `install` er midlertidige mapper):

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

Netværksadaptere testes mod en falsk lokal server eller med pakker sendt over UDP til adapteren. Tests, der
kontrollerer mod rigtige spildata på udviklerens maskine, er markeret `@pytest.mark.local` og springes over, hvor
de data mangler. De data går aldrig ind i depotet. `test_core.py` indeholder også testen, der fejler, hvis nogen
kode, der kunne skrive til en anden proces, findes i pakken (`test_memory_reading_cannot_write`).

## Et ærligt `verified` {#an-honest-verified}

`verified` siger, hvad der er kontrolleret, og hvordan, og hvad der ikke er. Det vises af `games` og på hver
spilside, og spillerne stoler på det. Eksempler fra koden:

- "tested on packets in the 2023, 2024 and 2025 formats built from EA's published specification, sent
  over UDP; untested against the game"
- "tested on documents in the published GSI format posted to the running adapter; untested against the
  running game"
- "tested on real stats files and schemas from a local install; change detection tested on files built
  in the binary KeyValues format"

Skriv "untested against the game", indtil adapteren har optaget det kørende spil. Angiv metoden og tolerancen og
intet mere: aldrig et kort, et kamp-id, et spillernavn, en dato, en korpusstørrelse eller et nøjagtigt antal fra rigtige
filer, og aldrig "this machine" (læsere kender den ikke). Navngiv kilden til hver offset og hvert layout, og sig, hvor
to kilder blev sammenlignet. Påstå aldrig mere, end der blev gjort. Et format, der blev gættet eller taget fra
fællesskabsværktøjer, siges at være det.

## Spilsiderne {#the-game-pages}

Hver side under [Spil](games.md) genereres ud fra adapterne, så den altid passer med koden. Efter at have tilføjet eller
ændret en adapter, generér dem igen fra depotmappen:

```bash
HEAT3D_NO_UPDATE=1 python tools/gen_game_pages.py
```

(I PowerShell: `$env:HEAT3D_NO_UPDATE = "1"; python tools/gen_game_pages.py`.) Tilføj `--check` for kun at
sammenligne: den skriver intet og afslutter med 1, når en side er forældet (også tabellen over spil i `docs/watcher.md`).

Scriptet:

- indlæser adaptererne med `heat3d_watch.adapters.load()` mod en tom, midlertidig datamappe, så ingen hukommelsesprofil
  eller indstilling på din maskine havner på siderne. Hukommelsesadaptere udelades, da de kommer fra spillernes egne
  profiler;
- nægter at skrive noget, hvis et adaptermodul ikke kan importeres (siderne ville miste de spil);
- skriver `docs/game-<adapter id>.md` for hver adapter og `docs/games.md` med oversigtstabellen, og sletter siderne for
  adaptere, der ikke længere findes;
- henter "What is recorded", "Where it comes from", "How to switch it on", akserne, multiplayer-flaget og "Verified" fra
  adapterens felter;
- gør modulets docstring til "How it works". Skriv docstrings i den rene tekststil, modulerne allerede bruger, og som
  scriptet omdanner: afsnit; lister med `*`, `-` eller `1.`; layouts og eksempler indrykket under linjen, der indleder
  dem (de bliver til kodeblokke); en titel understreget med bindestreger, eller en kort titellinje med sin tekst indrykket
  direkte under (de bliver til overskrifter);
- lister de statistiknøgler, adapteren sætter ved navn - `.stat("key", ...)`, begge sider af et `if`-udtryk og
  f-string-mønstre som `score.{team}` - i adapterens klasser og i de hjælpere, de bruger. Nøgler, der tages fra en variabel
  (en tabel over spillets felter), listes ikke;
- afgør "Positions" ud fra adapterens `axes.units` (en note, der starter med "no" eller "none", betyder ingen positioner) og
  ud fra, hvad dens kode skriver.

Redigér ikke de genererede sider i hånden: ændr adapteren og kør scriptet igen. Tabellen i
[Alle spil i én tabel](watcher.md) er outputtet af `python -m heat3d_watch games --markdown`.
