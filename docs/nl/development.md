---
title: Ontwikkeling
nav_order: 12
lang: "nl"
source: development.md
source_hash: "cb213e22ddea"
nav_exclude: true
search_exclude: true
---
# Ontwikkeling {#development}

Deze pagina is voor het toevoegen van een spel: hoe een adapter is gebouwd, hoe hij wordt getest, en hoe zijn
documentatie wordt gemaakt.

## De repository {#the-repository}

| Pad | Wat het bevat |
|---|---|
| `heat3d_watch/cli.py` | de commando's ([Commando's](commands.md)) |
| `heat3d_watch/watcher.py` | de achtergrondlus: de lijst met processen, één thread per adapter, updates |
| `heat3d_watch/session.py` | een opname: `events.jsonl`, `heat.parquet`, `meta.json`, herstel |
| `heat3d_watch/db.py` | `watcher.sqlite` |
| `heat3d_watch/config.py` | de instellingen en de datamap |
| `heat3d_watch/safety.py`, `heat3d_watch/memory.py` | de geheugencontroles en de alleen-lezen lezer ([Geheugen lezen](memory-reading.md)) |
| `heat3d_watch/notify.py` | Windows-meldingen |
| `heat3d_watch/adapters/` | één module per spel of groep spellen; modules die met `_` beginnen zijn gedeelde hulpfuncties |
| `heat3d_watch/decoders/` | de decoders voor racetelemetrie, gekopieerd uit de lap-recorders van 3DHeat GameCapture |
| `heat3d_update/` | de updater ([Updates](updates.md)) |
| `mods/beamng/heat3d/` | de BeamNG-protocolmod die `setup beamng` installeert |
| `tests/` | de tests |
| `tools/gen_game_pages.py` | schrijft de spelpagina's van deze documentatie |

## Een adapter {#an-adapter}

Een adapter is een dataclass die afgeleid is van `heat3d_watch.adapters.base.Adapter`. Zijn velden zeggen wat
hij is; zijn methoden doen het werk.

| Veld | Standaard | Wat het is |
|---|---|---|
| `id` | `""` | kort en stabiel: sessiemappen, `disabled`, `replay_folders` en `player_names` verwijzen ernaar |
| `game` | `""` | de naam van het spel zoals mensen die schrijven; sessies worden daaronder opgeslagen |
| `kind` | `"telemetry"` | een van `telemetry`, `gsi`, `log`, `replay`, `platform`, `memory` ([Bronnen en regels](sources-and-rules.md)) |
| `exes` | `()` | executablenamen (in elke schrijfwijze) die betekenen dat het spel draait. Leeg: de adapter staat altijd aan (`always` is waar) |
| `multiplayer` | `True` | het spel wordt online gespeeld: het geheugen wordt nooit gelezen |
| `source` | `""` | waar de getallen vandaan komen, één keer gezegd |
| `records` | `()` | wat er wordt opgenomen, één item per soort ding |
| `enable` | `""` | hoe je de bron aanzet; leeg als er niets nodig is |
| `interval` | `0.1` | seconden tussen de peilingen |
| `axes` | `Axes()` | de opwaartse as van de wereld, gespiegelde assen, de eenheidsschaal van de viewer (houd 1) en een opmerking over de eenheden |
| `verified` | `""` | wat er is gecontroleerd, eerlijk (zie hieronder) |
| `completeness` | `{}` | het verslag van de bron volgens de [converterregel](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md) van 3DHeat: `read` (wat rijen wordt), `raw` (wat ongewijzigd wordt bewaard, en onder welk `type`), `missing` (wat de bron niet geeft, en waarom), `size` (hoe groot de ruwe feed per uur wordt). De sectie Completeness van de spelpagina wordt hieruit geschreven |

`source`, `records`, `enable`, `verified` en `completeness` zijn documentatie, geen versiering. `games` drukt ze af,
`games --markdown` maakt de tabel op [Alle spellen in één tabel](watcher.md), en de spelpagina's worden eruit
gegenereerd. Schrijf ze zo dat ze precies zeggen wat de code doet.

De methoden, allemaal optioneel:

| Methode | Wordt aangeroepen | Wat ze moet doen |
|---|---|---|
| `missing(self) -> str \| None` | door `games`, `status` en vóór het starten | zeggen waarom de adapter hier niet kan draaien (een DLL niet gevonden, een map ontbreekt), of `None` |
| `setup(self, ctx, *, apply) -> list[str]` | door `setup` | de eigen uitvoer van het spel aanzetten; geef één regel per wijziging terug, en wijzig bestanden alleen als `apply` waar is. Zet een bestand vóór de eerste wijziging terug als `<file>.heat3d-backup`, en overschrijf die back-up nooit. Overschrijf deze methode alleen als er iets aan te zetten is: `can_setup` (waar als `setup` is overschreven) bepaalt of `setup` hem uitvoert of zegt dat er niets te veranderen valt; een klasse die meerdere spellen bedient, overschrijft `can_setup` voor de spellen die het niet kan instellen (`RallyAdapter` voor Richard Burns Rally). |
| `start(self, ctx)` | wanneer het proces van het spel verschijnt (altijd-aan adapters: wanneer `run` start) | sockets openen, bestanden zoeken, onthouden waar te beginnen |
| `poll(self, ctx)` | elke `interval` seconden, in de eigen thread van de adapter | wat het spel sinds de vorige peiling zei, pakken en opnemen |
| `stop(self, ctx)` | wanneer het spel weg is of de watcher stopt | sessies en sockets sluiten |

Elke adapter draait in zijn eigen thread (`Runner`). Een uitzondering in `poll` wordt gelogd, en de adapter
wacht `min(5, interval × 10 + 0.5)` seconden voor de volgende peiling. Na 20 mislukkingen achter elkaar, of
een mislukking in `start`, wordt de adapter gestopt en pas weer gestart wanneer het proces-id van het spel
verandert. `missing()` wordt bij elke scan gecontroleerd, dus houd het goedkoop.

Een adapterobject wordt hergebruikt wanneer het spel opnieuw start, dus `start` moet alles resetten wat een
vorige run heeft achtergelaten.

### Registreren {#registering-it}

Zet de module in `heat3d_watch/adapters/` en noem de adapters aan het eind:

```python
ADAPTERS = [MyAdapter(id="mygame", game="My Game", ...)]
```

`adapters.load()` importeert elke module in het pakket (behalve `base` en namen die met `_` beginnen) en
verzamelt hun `ADAPTERS`. Twee adapters met hetzelfde id stoppen het laden met een `ValueError`. Een module die
niet kan worden geïmporteerd (een ontbrekende afhankelijkheid) laat zijn spellen weg en `games` noemt hem met de
fout, zodat het probleem van één spel de andere niet stopt.

## Context en Session {#context-and-session}

`start`, `poll`, `stop` en `setup` krijgen een `Context`:

| Onderdeel | Wat het is |
|---|---|
| `settings` | de `Settings` ([Installeren en uitvoeren](installing-and-running.md#settings)) |
| `data` | de datamap |
| `pid`, `exe` | het proces-id en het pad van het executable van het spel, wanneer de adapter voor een draaiend spel is gestart; de installatiemap staat naast `exe` |
| `open(adapter, *, game=None, when=None, axes=..., source=..., multiplayer=..., meta=..., geo=None)` | een nieuwe `Session`. `game` overschrijft de spelnaam van de adapter (voor adapters die veel spellen dekken); `when` zet het begin voor sessies die het verleden beschrijven; `axes`, `source` en `multiplayer` zijn standaard die van de adapter; `meta` is een woordenboek dat in `meta.json` wordt geschreven; `geo` (`{"lat0": .., "lon0": ..}`, of `session.geo` later zetten) plaatst een sessie op een platte kaart op de aarde, in `meta.json` en de voettekst van de tabel |
| `close(session)` | beëindigt een sessie: de tabel, `heat.raw.parquet`, `meta.json`, de regel in `watcher.sqlite`. Een sessie zonder gebeurtenissen en zonder ruwe items wordt verwijderd; een sessie met alleen ruwe items blijft bewaard (geen tabel, geen regel in de database). Accepteert `None`. Geeft het pad van de tabel of `None` terug. |

Een `Session` legt vast:

| Onderdeel | Wat het doet |
|---|---|
| `event(name, *, t=None, ms=None, x=None, y=None, z=None, player=None, team=None, session=None, **attrs)` | één rij. `t` is standaard de seconden sinds de sessie begon, `ms` is standaard nu. Een positie telt alleen wanneer `x`, `y` en `z` alle drie zijn gegeven en eindig zijn. `None`-attributen worden weggelaten. |
| `position(x, y, z, **kw)` | een gebeurtenis met de naam `position` |
| `raw(type, payload=None, *, text=None, used=False, t=None, ms=None, **fields)` | bewaart één ding dat de bron stuurde, ongewijzigd: de bytes van een pakket of pagina (`payload`), een regel of een JSON-antwoord zoals het binnenkwam (`text`), of de waarden van een lezing bij naam (`fields`, elk een eigen kolom). `type` is het eigen woord van de bron ervoor (een pakket-id, de naam van een geheugengebied, een journaalgebeurtenis, een eindpunt); `used` zegt dat het ook rijen werd. Wordt meteen in `raw.bin` ingepakt wanneer het wordt aangeroepen, weggeschreven als `heat.raw.parquet` (zstd) wanneer de sessie sluit of wordt hersteld, en per `type` geteld in `selfCheck.completeness` van `meta.json` |
| `stat(key, value, how="set")` | een statistiek: `set` zet hem, `add` telt erbij op, `max` of `min` houdt het hoogste of laagste bij |
| `now()` | seconden sinds de sessie begon |
| `meta` | een woordenboek dat in `meta.json` wordt geschreven |
| `started`, `ended`, `folder`, `id`, `counts`, `positions` | wanneer, waar, en wat er tot nu toe is opgenomen |

`event`, `stat` en `raw` zijn thread-veilig en kunnen vanuit een werkthread worden aangeroepen.

**Elke adapter bewaart alles wat zijn bron stuurt.** De rijen zijn wat de viewer tekent; ze zijn niet het
archief. Elk pakket dat een poort bereikt, elke gedeelde-geheugenpagina die wordt gelezen (het hele geheugengebied,
elke keer dat die verandert), elke regel van een logboek of exportscript (ook die welke de adapter negeert),
elk JSON-antwoord of verzonden document gaat naar `session.raw(...)` zodra het binnenkomt, of het nu een rij
wordt of niet - en niets wordt uitgedund onder de snelheid waarmee de adapter leest. Een item dat binnenkomt
voordat een sessie open is, opent er een (een sessie met alleen ruwe items wordt bewaard), of wordt vastgehouden
tot er een opent; het wordt nooit weggegooid. Velden die goedkoop te decoderen en zeker in betekenis zijn, gaan
ook op de rijen. Dit is de [converterregel](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md) van
3DHeat: een live feed is weg zodra hij is verstuurd, dus wat een adapter niet bewaart, is voor altijd verloren,
en wat hij ongewijzigd bewaart, kan worden gedecodeerd op de dag dat iemand het begrijpt. De grootte is de prijs;
zstd en woordenboekcodering houden die klein, door dingen niet weg te laten. Elke test van een adapter stuurt
iets wat hij niet gebruikt, en controleert dat het ongewijzigd terugkomt uit `heat.raw.parquet`, en dat
`selfCheck.completeness.lost` 0 is. `racing.Driving.raw` doet hetzelfde voor de racing-adapters (en opent de
sessie), en `racing.Pages` bewaart gedeelde-geheugenpagina's telkens wanneer hun bytes veranderen, en telt de
herlezingen die niets nieuws vonden in `unchanged_reads` van `meta.json`.

Conventies waar de rest van het systeem op rekent:

- **De eigen rijen van de speler worden gemarkeerd, uit wat de bron zegt.** `player="me"` waar de bron de eigen
  van de speler is; waar elke speler onder een naam wordt opgenomen, `own_car=1` op de rijen van de auto van de
  speler (op de spelersindex van het spel of de bekeken deelnemer), of de naam van de speler als
  `session.meta["player"]` (meteen naar `meta.json` geschreven) wanneer de bron de speler noemt. Gok nooit: waar de
  bron het niet zegt, neem de naam uit een instelling (`player_names`, `riot_id`) of markeer niets.
  [NVIDIA highlights](nvidia-highlights.md) lenen alleen posities uit zulke rijen (`platform.own_row`). Andere
  spelers worden op hun naam of id herkend.
- **Routes worden begrensd door gebeurtenissen met posities**: `spawn`, `respawn` en `session_start` beginnen er
  een; `death`, `finish`, `session_end` en `teleport` beëindigen er een. Wanneer de speler is verplaatst zonder te
  reizen (een reset, een terugspoel, een snelreis, een geladen save), schrijf `teleport` op de plek die is verlaten,
  en daarna een start (`spawn`, of `respawn` voor een reset die het spel noemt) op de plek die is bereikt, zodat de
  routelijn van de viewer de ene route beëindigt en de volgende begint, in plaats van over de kaart te tekenen.
  `Driving.jumped` doet dat voor voertuigen.
- **Posities blijven in de eigen wereldcoördinaten en eenheden van het spel**, beschreven door `axes`. Reken ze
  niet om naar een ander stelsel, tenzij het spel geen bruikbaar wereldstelsel geeft (de vluchtsimulators zetten
  breedte- en lengtegraad om in een platte kaart, `Tangent`, rond de eerste fix - DCS rond de vaste oorsprong van
  zijn theater - en geven `geo=tangent.geo()` aan `open`, zodat de voettekst zegt waar de kaart op de aarde ligt).
  `axes.scale` is de eenheidsschaal van de viewer - hij vermenigvuldigt elke positie ermee - en blijft 1, zodat de
  rijen samenvallen met een level dat uit hetzelfde spel is geëxporteerd, in dezelfde eenheden; zeg de eenheid in
  `axes.units`.
- **Statistiekensleutels** zijn kleine letters met underscores, en dragen hun eenheid waar die geldt
  (`distance_km`, `top_speed_kmh`, `max_altitude_m`, `duration_s`). Een tijd die als beste wordt bewaard begint met
  `best_` (bewaard met `min`), een plaats eindigt op `_position`: `stats` toont de laagste van die als beste, en
  de hoogste van elke andere sleutel (`db.lower_is_better`).

## Hulpfuncties {#helpers}

| Hulpfunctie | Module | Waarvoor |
|---|---|---|
| `Follower(find, since, stamp=None)`, `game_started(pid)`, `newest(paths)`, `read_shared(path)`, `steam_libraries()` | `_logfollow` | het volgen van een logboek dat het spel schrijft: gedeelde lezingen, alleen de regels van deze sessie, nieuwe en vervangen bestanden, alleen hele regels |
| `UdpPort(port, forward=None, grace=0.0, recheck=3.0)` met `try_open(who)`, `receive()`, `close()` | `racing` | een UDP-telemetriepoort op 127.0.0.1, alleen genomen wanneer vrij, afgestaan aan een ander programma, optioneel doorgestuurd |
| `Driving(adapter, ctx, hz=10.0, jump=50.0)` met `sample(...)`, `event(...)`, `lap(...)`, `count(...)`, `close()` | `racing` | voertuigsessies: posities op een vaste snelheid, afstand, topsnelheid, ronden; bij een sprong `teleport` waar de auto was en `spawn` waar hij nu is (`jumped(...)`) |
| `SharedView.open(name)` | `simracing_shm` | het gedeelde geheugen met naam van een spel, alleen lezen, nooit aangemaakt |
| `ReplayAdapter` (`patterns`, `folders(ctx)`, `convert(path, ctx)`) | `replays` | een gevolgde replaymap: bestanden worden omgezet zodra ze niet meer groeien, in een werkthread; de eerste keer wordt alleen genoteerd wat er staat, en `convert_existing(ctx, folder=None)` - het commando [`replays`](commands.md#replays) - zet die op verzoek om |
| `load_state`, `save_state` | `platform` | onthouden wat een altijd-aan adapter heeft gezien, in `<data>\state\<id>.json` |
| `FlightLog`, `Tangent` | `xplane` | de vluchtadministratie (opstijgen, landen, neerstorten, afstand) en de platte kaart rond de eerste fix (`Tangent.geo()` is de `geo` van de sessie) |
| `backup_once(path)` | `gsi`, `racing` | de back-up `<file>.heat3d-backup` |
| Steam-bestanden | `_steam` | binaire en tekst-KeyValues, de Steam-installatiemap uit het register |

Een minimale logboekadapter, ter illustratie (een verzonnen spel):

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

Open de sessie met het eerste dat het opnemen waard is, niet in `start`, zodat een spel dat in zijn menu's blijft
niets achterlaat (een lege sessie wordt toch verwijderd).

## Tests {#tests}

```bash
python -m pytest
```

`tests/conftest.py` geeft elke test een wegwerp-datamap (`HEAT3D_WATCH_HOME`) en zet de updatecontroles en
meldingen uit (`HEAT3D_NO_UPDATE`, `HEAT3D_NO_TOAST`). Een adaptertest bouwt de uitvoer van het spel op uit
het gepubliceerde formaat - pakketten uit de specificatie, logregels in het formaat van het spel, bestanden in de
gedocumenteerde indeling - en stuurt de adapter rechtstreeks aan (ingekort uit `tests/test_poe.py`; `data` en
`install` zijn tijdelijke mappen):

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

Netwerkadapters worden getest tegen een nep-server op de eigen computer, of met pakketten die over UDP naar de
adapter worden gestuurd. Tests die tegen echte spelgegevens op de computer van de ontwikkelaar controleren, zijn
gemarkeerd met `@pytest.mark.local` en worden overgeslagen waar die gegevens ontbreken. Die gegevens gaan nooit
in de repository. `test_core.py` bevat ook de test die faalt als er code in het pakket staat die naar een ander
proces kan schrijven (`test_memory_reading_cannot_write`).

## Een eerlijke `verified` {#an-honest-verified}

`verified` zegt wat er is gecontroleerd en hoe, en wat niet. Het wordt getoond door `games` en op elke spelpagina,
en spelers vertrouwen erop. Voorbeelden uit de code:

- "tested on packets in the 2023, 2024 and 2025 formats built from EA's published specification, sent
  over UDP; untested against the game"
- "tested on documents in the published GSI format posted to the running adapter; untested against the
  running game"
- "tested on real stats files and schemas from a local install; change detection tested on files built
  in the binary KeyValues format"

Schrijf "untested against the game" zolang de adapter het draaiende spel niet heeft opgenomen. Noem alleen de
methode en de tolerantie: nooit een kaart, wedstrijd-id, spelersnaam, datum, grootte van een verzameling of een
exact aantal uit echte bestanden, en nooit "deze computer" (de lezers weten dat niet). Noem de bron van elke
verschuiving en elke indeling, en zeg waar twee bronnen zijn vergeleken. Beweer nooit meer dan er is gedaan. Een
formaat dat is geraden of uit gemeenschapstools komt, wordt als zodanig genoemd.

## De spelpagina's {#the-game-pages}

Elke pagina onder [Spellen](games.md) wordt uit de adapters gegenereerd, dus die klopt altijd met de code. Na het
toevoegen of wijzigen van een adapter maak je ze opnieuw vanuit de map van de repository:

```bash
HEAT3D_NO_UPDATE=1 python tools/gen_game_pages.py
```

(In PowerShell: `$env:HEAT3D_NO_UPDATE = "1"; python tools/gen_game_pages.py`.) Voeg `--check` toe om alleen te
vergelijken: het schrijft niets en eindigt met 1 wanneer een pagina verouderd is (ook de spellentabel in
`docs/watcher.md`).

Het script:

- laadt de adapters met `heat3d_watch.adapters.load()`, tegen een lege tijdelijke datamap, zodat geen
  geheugenprofiel of instelling op jouw computer in de pagina's terechtkomt. Geheugenadapters worden weggelaten,
  omdat die uit de eigen profielen van spelers komen;
- weigert iets te schrijven als een adaptermodule niet kan worden geïmporteerd (de pagina's zouden die spellen
  verliezen);
- schrijft `docs/game-<adapter id>.md` voor elke adapter en `docs/games.md` met het overzichtstabel, en verwijdert
  de pagina's van adapters die niet meer bestaan;
- haalt "What is recorded", "Where it comes from", "How to switch it on", de assen, de multiplayer-vlag en
  "Verified" uit de velden van de adapter;
- maakt van de docstring van de module "How it works". Schrijf docstrings in de platte-tekststijl die de modules al
  gebruiken, die het script omzet: alinea's; lijsten met `*`, `-` of `1.`; indelingen en voorbeelden die onder de
  regel staan die ze inleidt (ze worden codeblokken); een titel die met streepjes is onderstreept, of een korte
  titelregel waarvan de tekst direct eronder is ingesprongen (ze worden koppen);
- somt de statistiekensleutels op die de code van de adapter bij naam zet - `.stat("key", ...)`, beide kanten van een
  `if`-expressie, en f-string-patronen zoals `score.{team}` - in de klassen van de adapter en in de hulpfuncties die
  ze gebruiken. Sleutels die uit een variabele komen (een tabel met velden van het spel) worden niet opgesomd;
- bepaalt "Positions" uit `axes.units` van de adapter (een opmerking die begint met "no" of "none" betekent geen
  posities) en uit wat de code schrijft.

Bewerk de gegenereerde pagina's niet met de hand: verander de adapter en draai het script opnieuw. De tabel op
[Alle spellen in één tabel](watcher.md) is de uitvoer van `python -m heat3d_watch games --markdown`.
