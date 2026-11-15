---
title: Utveckling
nav_order: 12
lang: "sv"
source: development.md
source_hash: "cb213e22ddea"
nav_exclude: true
search_exclude: true
---
# Utveckling {#development}

Den här sidan är för att lägga till ett spel: hur en adapter byggs, hur den testas och hur dess dokumentation görs.

## Förrådet {#the-repository}

| Sökväg | Vad den innehåller |
|---|---|
| `heat3d_watch/cli.py` | kommandona ([Kommandon](commands.md)) |
| `heat3d_watch/watcher.py` | bakgrundsloopen: processlistan, en tråd per adapter, uppdateringar |
| `heat3d_watch/session.py` | en inspelning: `events.jsonl`, `heat.parquet`, `meta.json`, återställning |
| `heat3d_watch/db.py` | `watcher.sqlite` |
| `heat3d_watch/config.py` | inställningarna och datamappen |
| `heat3d_watch/safety.py`, `heat3d_watch/memory.py` | minneskontrollerna och den skrivskyddade läsaren ([Läsa minne](memory-reading.md)) |
| `heat3d_watch/notify.py` | Windows-notiser |
| `heat3d_watch/adapters/` | en modul per spel eller spelfamilj; moduler som börjar med `_` är delade hjälpare |
| `heat3d_watch/decoders/` | avkodarna för racingtelemetri, kopierade från 3DHeat GameCaptures varvinspelare |
| `heat3d_update/` | uppdateraren ([Uppdateringar](updates.md)) |
| `mods/beamng/heat3d/` | BeamNG-protokollmodden som `setup beamng` installerar |
| `tests/` | testerna |
| `tools/gen_game_pages.py` | skriver spelsidorna i den här dokumentationen |

## En adapter {#an-adapter}

En adapter är en dataclass som ärver från `heat3d_watch.adapters.base.Adapter`. Dess fält säger vad den är; dess metoder gör jobbet.

| Fält | Standard | Vad det är |
|---|---|---|
| `id` | `""` | kort och stabilt: sessionsmappar, `disabled`, `replay_folders` och `player_names` refererar till det |
| `game` | `""` | spelets namn så som folk skriver det; sessioner sorteras under det |
| `kind` | `"telemetry"` | ett av `telemetry`, `gsi`, `log`, `replay`, `platform`, `memory` ([Källor och regler](sources-and-rules.md)) |
| `exes` | `()` | körbara filnamn (oavsett versaler) som betyder att spelet körs. Tomt: adaptern är alltid påslagen (`always` är sant) |
| `multiplayer` | `True` | spelet spelas online: dess minne läses aldrig |
| `source` | `""` | varifrån siffrorna kommer, sagt en gång |
| `records` | `()` | vad som spelas in, en post per sorts sak |
| `enable` | `""` | hur källan slås på; tomt när inget behövs |
| `interval` | `0.1` | sekunder mellan avläsningarna |
| `axes` | `Axes()` | världens upp-axel, speglade axlar, visarens enhetsskala (behåll 1) och en anteckning om enheterna |
| `verified` | `""` | vad som har kontrollerats, ärligt (se nedan) |
| `completeness` | `{}` | källans redogörelse enligt 3DHeats [konverterarregel](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md): `read` (vad som blir rader), `raw` (vad som sparas helt, under vilken `type`), `missing` (vad källan inte ger, och varför), `size` (hur stort det råa flödet blir per timme). Spelsidans avsnitt "Completeness" skrivs utifrån det |

`source`, `records`, `enable`, `verified` och `completeness` är dokumentation, inte dekoration. `games` skriver ut dem, `games --markdown` gör tabellen i [Alla spel i en tabell](watcher.md), och spelsidorna genereras från dem. Skriv dem så att de säger exakt vad koden gör.

Metoderna, alla valfria:

| Metod | Anropas | Vad den ska göra |
|---|---|---|
| `missing(self) -> str \| None` | av `games`, `status` och innan start | säga varför adaptern inte kan köra här (en DLL hittades inte, en mapp saknas), eller `None` |
| `setup(self, ctx, *, apply) -> list[str]` | av `setup` | slå på spelets egen utdata; returnera en rad per ändring, och ändra filer bara när `apply` är sant. Säkerhetskopiera en fil som `<file>.heat3d-backup` före dess första ändring, och skriv aldrig över den backupen. Åsidosätt den bara när det finns något att slå på: `can_setup` (sant när `setup` åsidosätts) avgör om `setup` kör den eller säger att det inte finns något att ändra; en klass som betjänar flera spel åsidosätter `can_setup` för dem den inte kan ställa in (`RallyAdapter` för Richard Burns Rally). |
| `start(self, ctx)` | när spelets process dyker upp (alltid påslagna adaptrar: när `run` startar) | öppna sockets, hitta filer, minnas var man ska börja |
| `poll(self, ctx)` | var `interval` sekund, i adapterns egen tråd | ta det spelet har sagt sedan förra avläsningen och spela in det |
| `stop(self, ctx)` | när spelet är borta eller watchern stoppas | stäng sessioner och sockets |

Varje adapter körs i sin egen tråd (`Runner`). Ett undantag i `poll` loggas, och adaptern väntar `min(5, interval × 10 + 0.5)` sekunder innan nästa avläsning. Efter 20 fel i rad, eller ett fel i `start`, stoppas adaptern och startas inte om förrän spelets process-id ändras.
`missing()` kontrolleras vid varje skanning, så håll den billig.

Ett adapterobjekt återanvänds när dess spel startar igen, så `start` måste nollställa allt en tidigare körning lämnade kvar.

### Registrera den {#registering-it}

Lägg modulen i `heat3d_watch/adapters/` och lista adaptrarna i slutet av den:

```python
ADAPTERS = [MyAdapter(id="mygame", game="My Game", ...)]
```

`adapters.load()` importerar varje modul i paketet (utom `base` och namn som börjar med `_`) och samlar deras `ADAPTERS`. Två adaptrar med samma id stoppar inläsningen med ett `ValueError`. En modul som inte går att importera (ett saknat beroende) utelämnar sina spel och nämns av `games` med felet, så ett spels problem stoppar inte de andra.

## Context och Session {#context-and-session}

`start`, `poll`, `stop` och `setup` får en `Context`:

| Medlem | Vad den är |
|---|---|
| `settings` | `Settings` ([Installera och köra](installing-and-running.md#settings)) |
| `data` | datamappen |
| `pid`, `exe` | spelets process-id och körbara sökväg, när adaptern startades för ett körande spel; installationsmappen ligger bredvid `exe` |
| `open(adapter, *, game=None, when=None, axes=..., source=..., multiplayer=..., meta=..., geo=None)` | en ny `Session`. `game` åsidosätter adapterns spelnamn (för adaptrar som täcker många spel); `when` sätter starten för sessioner som beskriver det förflutna; `axes`, `source` och `multiplayer` är adapterns som standard; `meta` är en ordbok som skrivs i `meta.json`; `geo` (`{"lat0": .., "lon0": ..}`, eller sätt `session.geo` senare) placerar en plan kartsession på jordklotet, i `meta.json` och tabellens sidfot |
| `close(session)` | avslutar en session: tabellen, `heat.raw.parquet`, `meta.json`, dess rad i `watcher.sqlite`. En session utan händelser och utan råa poster raderas; en med bara råa poster behålls (ingen tabell, ingen rad i databasen). Tar emot `None`. Returnerar tabellens sökväg eller `None`. |

En `Session` spelar in:

| Medlem | Vad den gör |
|---|---|
| `event(name, *, t=None, ms=None, x=None, y=None, z=None, player=None, team=None, session=None, **attrs)` | en rad. `t` är som standard sekunder sedan sessionen började, `ms` är nu. En position räknas bara när `x`, `y` och `z` alla anges och är ändliga. `None`-attribut utelämnas. |
| `position(x, y, z, **kw)` | en händelse med namnet `position` |
| `raw(type, payload=None, *, text=None, used=False, t=None, ms=None, **fields)` | spara en sak källan skickade, hel: ett paket eller en sidas bytes (`payload`), en rad eller ett JSON-svar som det kom (`text`), eller en avläsnings värden med namn (`fields`, var och en en egen kolumn). `type` är källans eget ord för den (ett paketid, namnet på en mappning, en journalhändelse, en endpoint); `used` säger att den också blev rader. Inramas i `raw.bin` i samma ögonblick den anropas, skrivs ut som `heat.raw.parquet` (zstd) när sessionen stängs eller återställs, och räknas per `type` i `meta.json`:s `selfCheck.completeness` |
| `stat(key, value, how="set")` | en statistik: `set` den, `add` till den, behåll `max` eller `min` |
| `now()` | sekunder sedan sessionen började |
| `meta` | en ordbok som skrivs i `meta.json` |
| `started`, `ended`, `folder`, `id`, `counts`, `positions` | när, var, och vad som spelats in hittills |

`event`, `stat` och `raw` är trådsäkra och kan anropas från en arbetstråd.

**Varje adapter behåller allt dess källa skickar.** Raderna är det visaren ritar; de är inte inspelningen. Varje paket som når en port, varje delad minnessida som läses (hela mappningen, varje gång den ändras), varje rad i en logg eller ett exportskript (även de som adaptern ignorerar), varje JSON-svar eller postat dokument går till `session.raw(...)` när det kommer, oavsett om det blir en rad eller inte – och inget gallras under den takt adaptern läser i. En post som kommer innan en session är öppen öppnar en (en session med bara råa poster behålls), eller hålls tills en öppnas; den släpps aldrig. Fält som är billiga att avkoda och säkra i betydelse läggs också på raderna. Det är 3DHeats [konverterarregel](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md): ett livflöde är borta i samma ögonblick det skickas, så det en adapter inte behåller är förlorat för gott, och det den behåller helt kan avkodas den dag någon förstår det. Storleken är priset; zstd och ordbokskodning håller den nere, och det är inte att utelämna saker. Varje adapters test skickar något den inte använder och kontrollerar att det kommer tillbaka helt ur `heat.raw.parquet`, och att `selfCheck.completeness.lost` är 0. `racing.Driving.raw` gör detsamma för racingadaptrarna (och öppnar sessionen), och `racing.Pages` sparar delade minnessidor när deras bytes ändras, och räknar i `meta.json`:s `unchanged_reads` de omläsningar som inte hittade något nytt.

Konventioner som resten av systemet förlitar sig på:

- **Spelarens egna rader markeras utifrån vad källan säger.** `player="me"` där källan är spelarens egen; där varje spelare spelas in under ett namn, `own_car=1` på spelarens bils rader (efter spelets spelarindex eller den visade deltagaren), eller spelarens namn som `session.meta["player"]` (skrivs till `meta.json` direkt) när källan nämner spelaren. Gissa aldrig: där källan inte säger det, ta namnet från en inställning (`player_names`, `riot_id`) eller markera inget.
  [NVIDIA-höjdpunkter](nvidia-highlights.md) lånar bara positioner från sådana rader (`platform.own_row`). Andra spelare identifieras med namn eller id.
- **Rutter avgränsas av händelser med positioner**: `spawn`, `respawn` och `session_start` börjar en; `death`, `finish`, `session_end` och `teleport` avslutar en. Närhelst spelaren förflyttade sig utan att resa (en återställning, en spolning bakåt, en snabbresa, en laddad sparfil), skriv `teleport` på platsen som lämnades och sedan en start (`spawn`, eller `respawn` för en återställning spelet namnger) på platsen som nåddes, så att visarens linjevärme avslutar en rutt och börjar nästa i stället för att rita över kartan. `Driving.jumped` gör det för fordon.
- **Positionerna behåller spelets egna världskoordinater och enheter**, beskrivna av `axes`. Konvertera dem inte till ett annat koordinatsystem om inte spelet ger någon användbar världsram (flygsimmarna lägger latitud och longitud i en platt karta, `Tangent`, runt första fixen – DCS runt teaterns fasta origo – och skickar `geo=tangent.geo()` till `open`, så att sidfoten säger var på jordklotet kartan ligger). `axes.scale` är visarens enhetsskala – den multiplicerar varje position med sig – och förblir 1, så raderna stämmer med en nivå exporterad från samma spel i samma enheter; säg enheten i `axes.units`.
- **Statistiknycklar** är gemener med understreck, och bär sin enhet där en gäller (`distance_km`, `top_speed_kmh`, `max_altitude_m`, `duration_s`). En tid som sparas som bästa börjar med `best_` (sparas med `min`), en placering slutar på `_position`: `stats` visar den lägsta av dem som bästa, och den högsta av alla andra nycklar (`db.lower_is_better`).

## Hjälpare {#helpers}

| Hjälpare | Modul | För |
|---|---|---|
| `Follower(find, since, stamp=None)`, `game_started(pid)`, `newest(paths)`, `read_shared(path)`, `steam_libraries()` | `_logfollow` | att följa en logg som spelet skriver: delade läsningar, bara den här sittningens rader, nya och ersatta filer, bara hela rader |
| `UdpPort(port, forward=None, grace=0.0, recheck=3.0)` med `try_open(who)`, `receive()`, `close()` | `racing` | en UDP-telemetriport på 127.0.0.1, tagen bara när den är ledig, lämnad till ett annat program, valfritt vidarebefordrad |
| `Driving(adapter, ctx, hz=10.0, jump=50.0)` med `sample(...)`, `event(...)`, `lap(...)`, `count(...)`, `close()` | `racing` | fordonssessioner: positioner i fast takt, distans, högsta hastighet, varv; vid ett hopp, `teleport` där bilen var och `spawn` där den är (`jumped(...)`) |
| `SharedView.open(name)` | `simracing_shm` | ett spels namngivna delade minne, skrivskyddat, aldrig skapat |
| `ReplayAdapter` (`patterns`, `folders(ctx)`, `convert(path, ctx)`) | `replays` | en bevakad replaymapp: filer konverteras när de slutat växa, i en arbetstråd; första genomgången noterar bara vad som finns, och `convert_existing(ctx, folder=None)` – kommandot [`replays`](commands.md#replays) – konverterar dem på begäran |
| `load_state`, `save_state` | `platform` | att minnas vad en alltid påslagen adapter har sett, i `<data>\state\<id>.json` |
| `FlightLog`, `Tangent` | `xplane` | flygbokföring (start, landningar, krascher, distans) och den platta kartan runt första fixen (`Tangent.geo()` är sessionens `geo`) |
| `backup_once(path)` | `gsi`, `racing` | regeln `<file>.heat3d-backup` |
| Steams filer | `_steam` | binära och textbaserade KeyValues, Steam-mappen från registret |

En minimal loggadapter, som illustration (ett påhittat spel):

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

Öppna sessionen med det första som är värt att spela in, inte i `start`, så att ett spel som står kvar i sina menyer inte lämnar något efter sig (en tom session raderas ändå).

## Tester {#tests}

```bash
python -m pytest
```

`tests/conftest.py` ger varje test en tillfällig datamapp (`HEAT3D_WATCH_HOME`) och stänger av uppdateringskontroller och notiser (`HEAT3D_NO_UPDATE`, `HEAT3D_NO_TOAST`). Ett adaptertest bygger spelets utdata från dess publicerade format – paket från specifikationen, loggrader i spelets format, filer i den dokumenterade layouten – och kör adaptern direkt (förkortat från `tests/test_poe.py`; `data` och `install` är tillfälliga mappar):

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

Nätverksadaptrar testas mot en falsk lokal server eller med paket som skickas över UDP till adaptern.
Tester som kontrollerar mot riktiga speldata på utvecklarens dator markeras `@pytest.mark.local` och hoppas över där de datan saknas. Den datan går aldrig in i förrådet. `test_core.py` innehåller också testet som fallerar om någon kod som kan skriva till en annan process finns i paketet (`test_memory_reading_cannot_write`).

## Ett ärligt `verified` {#an-honest-verified}

`verified` säger vad som kontrollerats och hur, och vad som inte gjorts. Det visas av `games` och på varje spelsida, och spelare förlitar sig på det. Exempel från koden:

- "tested on packets in the 2023, 2024 and 2025 formats built from EA's published specification, sent over UDP; untested against the game"
- "tested on documents in the published GSI format posted to the running adapter; untested against the running game"
- "tested on real stats files and schemas from a local install; change detection tested on files built in the binary KeyValues format"

Skriv "untested against the game" tills adaptern har spelat in det körande spelet. Ange metoden och toleransen bara: aldrig en karta, ett match-id, ett spelarnamn, ett datum, en korpusstorlek eller ett exakt antal från riktiga filer, och aldrig "this machine" (läsare vet inte vilken dator det är). Ange källan till varje offset och layout, och säg var två källor jämfördes. Påstå aldrig mer än vad som gjordes. Ett format som gissats eller tagits från community-verktyg sägs vara just det.

## Spelsidorna {#the-game-pages}

Varje sida under [Spel](games.md) genereras från adaptrarna, så den stämmer alltid med koden. Efter att du lagt till eller ändrat en adapter, generera dem igen från förrådsmappen:

```bash
HEAT3D_NO_UPDATE=1 python tools/gen_game_pages.py
```

(I PowerShell: `$env:HEAT3D_NO_UPDATE = "1"; python tools/gen_game_pages.py`.) Lägg till `--check` för att bara jämföra: den skriver ingenting och avslutar med 1 när en sida är föråldrad (även `docs/watcher.md`:s spelstabell).

Skriptet:

- laddar adaptrarna med `heat3d_watch.adapters.load()`, mot en tom tillfällig datamapp, så att ingen minnesprofil eller inställning på din dator hamnar på sidorna. Minnesadaptrar utelämnas, eftersom de kommer från spelarnas egna profiler;
- vägrar skriva något om en adaptermodul inte kan importeras (sidorna skulle förlora de spelen);
- skriver `docs/game-<adapter id>.md` för varje adapter och `docs/games.md` med översiktstabellen, och raderar sidorna för adaptrar som inte längre finns;
- tar "What is recorded", "Where it comes from", "How to switch it on", axlarna, flaggan för flerspelarläge och "Verified" från adapterns fält;
- gör modulens docstring till "How it works". Skriv docstrings i den enkla textstil modulerna redan använder, som skriptet omvandlar: stycken; listor med `*`, `-` eller `1.`; layouter och exempel indragna under raden som inleder dem (de blir kodblock); en titel understruken med bindestreck, eller en kort titelrad med sin text indragen direkt under den (de blir rubriker);
- listar de statistiknycklar adapterkoden sätter med namn – `.stat("key", ...)`, båda sidorna av ett `if`-uttryck och f-strängsmönster som `score.{team}` – i adapterns klasser och i hjälparna den använder. Nycklar som tas från en variabel (en tabell över spelets fält) listas inte;
- avgör "Positions" från adapterns `axes.units` (en anteckning som börjar med "no" eller "none" betyder inga positioner) och från vad dess kod skriver.

Redigera inte de genererade sidorna för hand: ändra adaptern och kör skriptet igen. Tabellen i [Alla spel i en tabell](watcher.md) är utdatan från `python -m heat3d_watch games --markdown`.
