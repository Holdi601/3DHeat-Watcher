---
title: Utvikling
nav_order: 12
lang: "no"
source: development.md
source_hash: "cb213e22ddea"
nav_exclude: true
search_exclude: true
---
# Utvikling {#development}

Denne siden er for å legge til et spill: hvordan en adapter bygges, hvordan den testes, og hvordan dokumentasjonen om den lages.

## Repositoryet {#the-repository}

| Sti | Hva den inneholder |
|---|---|
| `heat3d_watch/cli.py` | kommandoene ([Kommandoer](commands.md)) |
| `heat3d_watch/watcher.py` | løkken i bakgrunnen: prosesslisten, én tråd per adapter, oppdateringer |
| `heat3d_watch/session.py` | et opptak: `events.jsonl`, `heat.parquet`, `meta.json`, gjenoppretting |
| `heat3d_watch/db.py` | `watcher.sqlite` |
| `heat3d_watch/config.py` | innstillingene og datamappen |
| `heat3d_watch/safety.py`, `heat3d_watch/memory.py` | minnesjekkene og den skrivebeskyttede leseren ([Lese minne](memory-reading.md)) |
| `heat3d_watch/notify.py` | Windows-varsler |
| `heat3d_watch/adapters/` | én modul per spill eller spillfamilie; moduler som starter med `_` er delte hjelpere |
| `heat3d_watch/decoders/` | telemetridekodere for racing, kopiert fra 3DHeat GameCaptures rundeopptakere |
| `heat3d_update/` | oppdateringsprogrammet ([Oppdateringer](updates.md)) |
| `mods/beamng/heat3d/` | BeamNG-protokollmodden som `setup beamng` installerer |
| `tests/` | testene |
| `tools/gen_game_pages.py` | skriver spillsidene i denne dokumentasjonen |

## En adapter {#an-adapter}

En adapter er en dataclass avledet fra `heat3d_watch.adapters.base.Adapter`. Feltene sier hva den er; metodene gjør arbeidet.

| Felt | Standard | Hva det er |
|---|---|---|
| `id` | `""` | kort og stabil: øktmapper, `disabled`, `replay_folders` og `player_names` viser til den |
| `game` | `""` | spillets navn slik folk skriver det; økter føres under det |
| `kind` | `"telemetry"` | en av `telemetry`, `gsi`, `log`, `replay`, `platform`, `memory` ([Kilder og regler](sources-and-rules.md)) |
| `exes` | `()` | programfilnavn (uansett store eller små bokstaver) som betyr at spillet kjører. Tom: adapteren er alltid på (`always` er sann) |
| `multiplayer` | `True` | spillet spilles på nett: dets minne leses aldri |
| `source` | `""` | hvor tallene kommer fra, sagt én gang |
| `records` | `()` | hva som tas opp, ett punkt per type ting |
| `enable` | `""` | hvordan kilden slås på; tom når ingenting trengs |
| `interval` | `0.1` | sekunder mellom hver avstemming |
| `axes` | `Axes()` | verdens opp-akse, speilede akser, visningens enhetsskala (behold 1) og et notat om enhetene |
| `verified` | `""` | hva som er sjekket, ærlig (se under) |
| `completeness` | `{}` | kildens redegjørelse etter 3DHeats [konverteringsregel](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md): `read` (hva som blir rader), `raw` (hva som beholdes helt, og under hvilken `type`), `missing` (hva kilden ikke gir, og hvorfor), `size` (hvor stor den rå strømmen blir per time). Spillsidens avsnitt «Completeness» skrives ut fra dette |

`source`, `records`, `enable`, `verified` og `completeness` er dokumentasjon, ikke pynt. `games` skriver dem ut, `games --markdown` lager tabellen i [Alle spill i én tabell](watcher.md), og spillsidene genereres fra dem. Skriv dem slik at de sier nøyaktig det koden gjør.

Metodene, alle valgfrie:

| Metode | Kalt | Hva den bør gjøre |
|---|---|---|
| `missing(self) -> str \| None` | av `games`, `status`, og før start | si hvorfor adapteren ikke kan kjøre her (en DLL ikke funnet, en mappe mangler), eller `None` |
| `setup(self, ctx, *, apply) -> list[str]` | av `setup` | slå på spillets egen utdata; returner én linje per endring, og endre filer bare når `apply` er sann. Ta en sikkerhetskopi som `<file>.heat3d-backup` før første endring, og overskriv aldri den kopien. Overstyr den bare når det er noe å slå på: `can_setup` (sann når `setup` er overstyrt) avgjør om `setup` kjører den eller sier at det ikke er noe å endre. En klasse som dekker flere spill, overstyrer `can_setup` for dem den ikke kan sette opp (`RallyAdapter` for Richard Burns Rally). |
| `start(self, ctx)` | når spillets prosess dukker opp (adaptere som alltid er på: når `run` starter) | åpne sokler, finn filer, husk hvor man skal begynne |
| `poll(self, ctx)` | hver `interval` sekund, i adapterens egen tråd | ta det spillet har sagt siden forrige avstemming, og ta det opp |
| `stop(self, ctx)` | når spillet er borte, eller watcheren stopper | lukk økter og sokler |

Hver adapter kjører i sin egen tråd (`Runner`). Et unntak i `poll` logges, og adapteren venter `min(5, interval × 10 + 0.5)` sekunder før neste avstemming. Etter 20 feil på rad, eller en feil i `start`, stoppes adapteren og startes ikke igjen før spillets prosess-id endres. `missing()` sjekkes ved hver skanning, så hold den billig.

Et adapterobjekt gjenbrukes når spillet starter igjen, så `start` må nullstille alt en tidligere kjøring la igjen.

### Registrering {#registering-it}

Legg modulen i `heat3d_watch/adapters/` og list adapterne nederst i den:

```python
ADAPTERS = [MyAdapter(id="mygame", game="My Game", ...)]
```

`adapters.load()` importerer hver modul i pakken (unntatt `base` og navn som starter med `_`) og samler deres `ADAPTERS`. To adaptere med samme id stopper innlastingen med en `ValueError`. En modul som ikke kan importeres (en manglende avhengighet), utelater sine spill og nevnes av `games` med feilen, slik at ett spills problem ikke stopper de andre.

## Context og Session {#context-and-session}

`start`, `poll`, `stop` og `setup` får en `Context`:

| Medlem | Hva det er |
|---|---|
| `settings` | `Settings` ([Installere og kjøre](installing-and-running.md#settings)) |
| `data` | datamappen |
| `pid`, `exe` | spillets prosess-id og sti til programfilen, når adapteren ble startet for et kjørende spill; installasjonsmappen ligger ved siden av `exe` |
| `open(adapter, *, game=None, when=None, axes=..., source=..., multiplayer=..., meta=..., geo=None)` | en ny `Session`. `game` overstyrer adapterens spillnavn (for adaptere som dekker mange spill); `when` setter starten for økter som beskriver fortiden; `axes`, `source` og `multiplayer` tar adapterens verdier; `meta` er en ordbok som skrives i `meta.json`; `geo` (`{"lat0": .., "lon0": ..}`, eller sett `session.geo` senere) plasserer en flatkart-økt på jorden, i `meta.json` og i tabellens fotnote |
| `close(session)` | avslutter en økt: tabellen, `heat.raw.parquet`, `meta.json` og dens linje i `watcher.sqlite`. En økt uten hendelser og uten rå elementer slettes; en med bare rå elementer beholdes (ingen tabell, ingen linje i databasen). Tar imot `None`. Returnerer tabellens sti eller `None`. |

En `Session` tar opp:

| Medlem | Hva det gjør |
|---|---|
| `event(name, *, t=None, ms=None, x=None, y=None, z=None, player=None, team=None, session=None, **attrs)` | én rad. `t` er standard sekunder siden økten startet, `ms` er nå. En posisjon teller bare når `x`, `y` og `z` alle er gitt og endelige. `None`-attributter utelates. |
| `position(x, y, z, **kw)` | en hendelse som heter `position` |
| `raw(type, payload=None, *, text=None, used=False, t=None, ms=None, **fields)` | ta vare på ett ting kilden sendte, helt: en pakkes eller sides bytes (`payload`), en linje eller et JSON-svar slik det kom (`text`), eller en avlesnings verdier ved navn (`fields`, hver sin kolonne). `type` er kildens eget ord for det (en pakke-id, et kartlegs navn, en journalhendelse, et endepunkt); `used` sier at det også ble rader. Innrammet i `raw.bin` i det øyeblikket det kalles, skrevet ut som `heat.raw.parquet` (zstd) når økten lukkes eller gjenopprettes, og talt per `type` i `meta.json`s `selfCheck.completeness` |
| `stat(key, value, how="set")` | en statistikk: `set` den, `add` til den, eller behold `max` eller `min` |
| `now()` | sekunder siden økten startet |
| `meta` | en ordbok som skrives i `meta.json` |
| `started`, `ended`, `folder`, `id`, `counts`, `positions` | når, hvor, og hva som er tatt opp så langt |

`event`, `stat` og `raw` er trådsikre og kan kalles fra en arbeidstråd.

**Hver adapter beholder alt kilden sender.** Radene er det visningen tegner; de er ikke opptaket. Hver pakke som når en port, hver delt minneside som leses (hele mappingen, hver gang den endres), hver linje i en logg eller et eksportskript (også dem adapteren ignorerer), hvert JSON-svar eller postet dokument går til `session.raw(...)` når det kommer, enten det blir en rad eller ikke. Ingenting tynnes under den frekvensen adapteren leser med. Et element som kommer før en økt er åpnet, åpner en (en økt med bare rå elementer beholdes), eller holdes til en åpnes; det droppes aldri. Felter som er billige å dekode og sikre i betydning, legges også på radene. Dette er 3DHeats [konverteringsregel](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md): en live-strøm er borte i det øyeblikket den er sendt, så det en adapter ikke beholder, er tapt for godt, og det den beholder helt, kan dekodes den dagen noen forstår det. Størrelsen er prisen; zstd og ordbokskoding holder den nede uten å utelate noe. Hver adapters test sender noe den ikke bruker, og sjekker at det kommer tilbake helt fra `heat.raw.parquet`, og at `selfCheck.completeness.lost` er 0. `racing.Driving.raw` gjør det samme for racing-adapterne (og åpner økten), og `racing.Pages` beholder delte minnesider når bytesene deres endres, og teller i `meta.json`s `unchanged_reads` de omlesningene som ikke fant noe nytt.

Konvensjoner systemet bygger på:

- **Spillerens egne rader er merket, ut fra det kilden sier.** `player="me"` der kilden er spillerens egen; der hver spiller er tatt opp under et navn, `own_car=1` på radene til spillerens bil (etter spillerens indeks i spillet eller den viste deltakeren), eller spillerens navn som `session.meta["player"]` (skrevet til `meta.json` med en gang) når kilden navngir spilleren. Gjett aldri: der kilden ikke sier det, tas navnet fra en innstilling (`player_names`, `riot_id`), eller ingenting merkes. [NVIDIA-høydepunkter](nvidia-highlights.md) lånar bare posisjoner fra slike rader (`platform.own_row`). Andre spillere gjenkjennes på navn eller id.
- **Ruter avgrenses av hendelser med posisjoner**: `spawn`, `respawn` og `session_start` begynner en; `death`, `finish`, `session_end` og `teleport` avslutter en. Når spilleren har flyttet seg uten å reise (en tilbakestilling, en spoling tilbake, en hurtigreise, en innlastet lagring), skriv `teleport` der spilleren forlot stedet, og deretter en start (`spawn`, eller `respawn` for en tilbakestilling spillet navngir) der spilleren kom frem, slik at linjevarmen i visningen avslutter én rute og begynner den neste, i stedet for å tegne tvers over kartet. `Driving.jumped` gjør dette for kjøretøy.
- **Posisjoner beholdes i spillets egne verdenskoordinater og enheter**, beskrevet av `axes`. Ikke konverter dem til et annet koordinatsystem med mindre spillet ikke gir noe brukbart verdenskoordinatsystem (flysimulatorene legger breddegrad og lengdegrad i et flatt kart, `Tangent`, rundt første fiks - DCS rundt teatrets faste origo - og sender `geo=tangent.geo()` til `open`, slik at fotnoten sier hvor på jorden kartet ligger). `axes.scale` er visningens enhetsskala - den multipliserer hver posisjon - og står på 1, så radene passer med et nivå eksportert fra samme spill i samme enheter. Si enheten i `axes.units`.
- **Statistikknøkler** er små bokstaver med understrek, og bærer sin enhet der den finnes (`distance_km`, `top_speed_kmh`, `max_altitude_m`, `duration_s`). En tid holdt som beste begynner med `best_` (holdes med `min`), en plassering ender på `_position`: `stats` viser den laveste av disse som beste, og den høyeste av alle andre nøkler (`db.lower_is_better`).

## Hjelpere {#helpers}

| Hjelper | Modul | Til |
|---|---|---|
| `Follower(find, since, stamp=None)`, `game_started(pid)`, `newest(paths)`, `read_shared(path)`, `steam_libraries()` | `_logfollow` | å følge en logg spillet skriver: delte lesinger, bare denne sittingens linjer, nye og erstattede filer, hele linjer bare |
| `UdpPort(port, forward=None, grace=0.0, recheck=3.0)` med `try_open(who)`, `receive()`, `close()` | `racing` | en UDP-telemetriport på 127.0.0.1, tatt bare når den er ledig, gitt fra seg til et annet program, eventuelt videresendt |
| `Driving(adapter, ctx, hz=10.0, jump=50.0)` med `sample(...)`, `event(...)`, `lap(...)`, `count(...)`, `close()` | `racing` | kjøretøyøkter: posisjoner med fast hastighet, distanse, toppfart, runder; ved et hopp, `teleport` der bilen var og `spawn` der den er (`jumped(...)`) |
| `SharedView.open(name)` | `simracing_shm` | et spills navngitte delte minne, skrivebeskyttet, aldri opprettet |
| `ReplayAdapter` (`patterns`, `folders(ctx)`, `convert(path, ctx)`) | `replays` | en overvåket replaymappe: filer konverteres når de slutter å vokse, i en arbeidstråd; første gang noteres bare hva som ligger der, og `convert_existing(ctx, folder=None)` (kommandoen [`replays`](commands.md#replays)) konverterer dem på forespørsel |
| `load_state`, `save_state` | `platform` | husker hva en alltid-på-adapter har sett, i `<data>\state\<id>.json` |
| `FlightLog`, `Tangent` | `xplane` | flightbokføring (avganger, landinger, krasj, distanse) og det flate kartet rundt første fiks (`Tangent.geo()` er øktens `geo`) |
| `backup_once(path)` | `gsi`, `racing` | regelen `<file>.heat3d-backup` |
| Steams filer | `_steam` | binære og tekstlige KeyValues, Steam-mappen fra registret |

En minimal loggadapter, som illustrasjon (et oppdiktet spill):

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

Åpne økten med den første tingen som er verdt å ta opp, ikke i `start`, slik at et spill som står i menyene sine ikke etterlater noe (en tom økt slettes uansett).

## Tester {#tests}

```bash
python -m pytest
```

`tests/conftest.py` gir hver test en engangs datamappe (`HEAT3D_WATCH_HOME`) og slår av oppdateringssjekker og varsler (`HEAT3D_NO_UPDATE`, `HEAT3D_NO_TOAST`). En adaptertest bygger spillets utdata fra det publiserte formatet - pakker fra spesifikasjonen, logglinjer i spillets format, filer i den dokumenterte oppsettet - og kjører adapteren direkte (forkortet fra `tests/test_poe.py`; `data` og `install` er midlertidige mapper):

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

Nettverksadaptere testes mot en falsk lokal server, eller med pakker sendt over UDP til adapteren. Tester som sjekker mot ekte spilldata på utviklerens maskin er merket `@pytest.mark.local` og hoppes over der de dataene mangler. De dataene går aldri inn i repositoryet. `test_core.py` har også testen som feiler om kode som kan skrive til en annen prosess dukker opp i pakken (`test_memory_reading_cannot_write`).

## En ærlig `verified` {#an-honest-verified}

`verified` sier hva som er sjekket og hvordan, og hva som ikke er det. Den vises av `games` og på hver spillside, og spillerne stoler på den. Eksempler fra koden:

- «tested on packets in the 2023, 2024 and 2025 formats built from EA's published specification, sent over UDP; untested against the game»
- «tested on documents in the published GSI format posted to the running adapter; untested against the running game»
- «tested on real stats files and schemas from a local install; change detection tested on files built in the binary KeyValues format»

Skriv «untested against the game» til adapteren har tatt opp det kjørende spillet. Oppgi bare metoden og toleransen: aldri et kart, en kamp-id, et spillernavn, en dato, en korpusstørrelse eller et nøyaktig antall fra ekte filer, og aldri «this machine» (lesere kjenner ikke til den). Oppgi kilden til hvert offset og hvert oppsett, og si hvor to kilder ble sammenlignet. Påstå aldri mer enn det som er gjort. Et format som ble gjettet eller hentet fra fellesskapsverktøy, sies å være det.

## Spillsidene {#the-game-pages}

Hver side under [Spill](games.md) genereres fra adapterne, så den alltid stemmer med koden. Etter å ha lagt til eller endret en adapter, lag dem på nytt fra repositoryets mappe:

```bash
HEAT3D_NO_UPDATE=1 python tools/gen_game_pages.py
```

(I PowerShell: `$env:HEAT3D_NO_UPDATE = "1"; python tools/gen_game_pages.py`.) Legg til `--check` for bare å sammenligne: den skriver ingenting og avslutter med 1 når en side er utdatert (også tabellen over spill i `docs/watcher.md`).

Skriptet:

- laster adapterne med `heat3d_watch.adapters.load()`, mot en tom midlertidig datamappe, slik at ingen minneprofil eller innstilling på maskinen din havner i sidene. Minneadaptere utelates, siden de kommer fra spillerens egne profiler;
- nekter å skrive noe om en adaptermodul ikke kan importeres (sidene ville da miste de spillene);
- skriver `docs/game-<adapter id>.md` for hver adapter og `docs/games.md` med oversiktstabellen, og sletter sidene til adaptere som ikke finnes lenger;
- henter «What is recorded», «Where it comes from», «How to switch it on», aksene, nettspillflagget og «Verified» fra adapterens felt;
- gjør modulens docstring om til «How it works». Skriv docstrings i den rene tekststilen modulene allerede bruker, som skriptet konverterer: avsnitt; lister med `*`, `-` eller `1.`; oppsett og eksempler innrykket under linjen som innleder dem (de blir kodeblokker); en tittel understreket med bindestreker, eller en kort tittellinje med teksten innrykket rett under (de blir overskrifter);
- lister statistikknøklene adapterens kode setter ved navn - `.stat("key", ...)`, begge sider av et `if`-uttrykk, og f-streng-mønstre som `score.{team}` - i adapterens klasser og i hjelperne de bruker. Nøkler hentet fra en variabel (en tabell over spillets felt) listes ikke;
- avgjør «Positions» fra adapterens `axes.units` (et notat som starter med «no» eller «none» betyr ingen posisjoner) og fra det koden skriver.

Ikke rediger de genererte sidene for hånd: endre adapteren og kjør skriptet igjen. Tabellen i [Alle spill i én tabell](watcher.md) er utdata fra `python -m heat3d_watch games --markdown`.
