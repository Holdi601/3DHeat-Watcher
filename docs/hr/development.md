---
title: "Razvoj"
nav_order: 12
lang: "hr"
source: development.md
source_hash: "cb213e22ddea"
nav_exclude: true
search_exclude: true
---
# Razvoj {#development}

Ova stranica je za dodavanje igre: kako se gradi adapter, kako se testira i kako nastaje njegova dokumentacija.

## Repozitorij {#the-repository}

| Putanja | Što sadrži |
|---|---|
| `heat3d_watch/cli.py` | naredbe ([Naredbe](commands.md)) |
| `heat3d_watch/watcher.py` | pozadinska petlja: popis procesa, jedna nit po adapteru, ažuriranja |
| `heat3d_watch/session.py` | snimka: `events.jsonl`, `heat.parquet`, `meta.json`, oporavak |
| `heat3d_watch/db.py` | `watcher.sqlite` |
| `heat3d_watch/config.py` | postavke i mapa podataka |
| `heat3d_watch/safety.py`, `heat3d_watch/memory.py` | provjere memorije i čitač memorije samo za čitanje ([Čitanje memorije](memory-reading.md)) |
| `heat3d_watch/notify.py` | Windows obavijesti |
| `heat3d_watch/adapters/` | jedan modul po igri ili obitelji igara; moduli koji počinju s `_` su zajednički pomoćni dijelovi |
| `heat3d_watch/decoders/` | dekoderi telemetrije vožnje, preuzeti iz snimača krugova 3DHeat GameCapture |
| `heat3d_update/` | ažuriranje ([Ažuriranja](updates.md)) |
| `mods/beamng/heat3d/` | protokol-mod za BeamNG koji instalira `setup beamng` |
| `tests/` | testovi |
| `tools/gen_game_pages.py` | piše stranice igara ove dokumentacije |

## Adapter {#an-adapter}

Adapter je dataclass izveden iz `heat3d_watch.adapters.base.Adapter`. Njegova polja kažu što je, a metode obavljaju posao.

| Polje | Zadano | Što je |
|---|---|---|
| `id` | `""` | kratko i stalno: mape sesija, `disabled`, `replay_folders` i `player_names` se na njega pozivaju |
| `game` | `""` | naziv igre kako ga ljudi pišu; sesije se spremaju pod njim |
| `kind` | `"telemetry"` | jedno od: `telemetry`, `gsi`, `log`, `replay`, `platform`, `memory` ([Izvori i pravila](sources-and-rules.md)) |
| `exes` | `()` | nazivi izvršnih datoteka (bez obzira na velika i mala slova) koji znače da igra radi. Prazno: adapter je uvijek uključen (`always` je true) |
| `multiplayer` | `True` | igra se na mreži: njezina memorija se nikad ne čita |
| `source` | `""` | odakle dolaze brojevi, kaže se jednom |
| `records` | `()` | što se bilježi, jedna stavka po vrsti stvari |
| `enable` | `""` | kako se izvor uključuje; prazno kad ništa ne treba |
| `interval` | `0.1` | sekunde između provjera |
| `axes` | `Axes()` | glavna os svijeta, zrcaljene osi, mjerilo jedinica prikaza (držite 1) i napomena o jedinicama |
| `verified` | `""` | što je provjereno, iskreno (vidi dolje) |
| `completeness` | `{}` | izvještaj izvora prema [pravilu pretvarača](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md) 3DHeat-a: `read` (što postaje retci), `raw` (što se čuva cijelo, pod kojim `type`-om), `missing` (što izvor ne daje, i zašto), `size` (koliko je veliki sirovi tok u jednom satu). Odjeljak "Completeness" na stranici igre piše se iz toga |

`source`, `records`, `enable`, `verified` i `completeness` su dokumentacija, a ne ukras. `games` ih ispisuje, `games --markdown` pravi tablicu u [Sve igre u jednoj tablici](watcher.md), a stranice igara se generiraju iz njih. Pišite ih tako da točno kažu što kod radi.

Metode, sve neobavezne:

| Metoda | Poziva se | Što treba raditi |
|---|---|---|
| `missing(self) -> str \| None` | `games`, `status` i prije pokretanja | reći zašto adapter ovdje ne može raditi (nije nađen DLL, nedostaje mapa), ili `None` |
| `setup(self, ctx, *, apply) -> list[str]` | `setup` | uključuje vlastiti izlaz igre; vraća po jedan redak za svaku promjenu, a datoteke mijenja samo ako je `apply` istina. Prije prve promjene datoteku sigurnosno kopira kao `<file>.heat3d-backup` i nikad ne prepisuje tu kopiju. Nadjačajte ga samo kad ima što uključiti: `can_setup` (istina kad je `setup` nadjačan) odlučuje hoće li `setup` to izvršiti ili reći da nema što mijenjati; klasa koja služi za više igara nadjačava `can_setup` za one koje ne može postaviti (`RallyAdapter` za Richard Burns Rally). |
| `start(self, ctx)` | kad se pojavi proces igre (adapteri uvijek uključeni: kad krene `run`) | otvoriti utičnice, naći datoteke, zapamtiti odakle početi |
| `poll(self, ctx)` | svakih `interval` sekundi, u vlastitoj niti adaptera | uzeti što je igra rekla od zadnje provjere i zabilježiti to |
| `stop(self, ctx)` | kad igre nema ili se watcher zaustavlja | zatvoriti sesije i utičnice |

Svaki adapter radi u vlastitoj niti (`Runner`). Iznimka u `poll` se zapiše u dnevnik, a adapter čeka `min(5, interval × 10 + 0.5)` sekundi prije sljedeće provjere. Nakon 20 uzastopnih neuspjeha, ili neuspjeha u `start`, adapter se zaustavlja i ne pokreće se ponovno dok se ID procesa igre ne promijeni.
`missing()` se provjerava pri svakom pregledu, pa neka bude jeftin.

Objekt adaptera se ponovno koristi kad igra ponovno krene, pa `start` mora resetirati sve što je ostavilo prethodno pokretanje.

### Registriranje {#registering-it}

Stavite modul u `heat3d_watch/adapters/` i na njegovom kraju navedite adaptere:

```python
ADAPTERS = [MyAdapter(id="mygame", game="My Game", ...)]
```

`adapters.load()` uvozi svaki modul u paketu (osim `base` i naziva koji počinju s `_`) i skuplja njihove `ADAPTERS`. Dva adaptera s istim ID-om zaustavljaju učitavanje s `ValueError`. Modul koji se ne može uvesti (nedostaje ovisnost) izostavlja svoje igre, a `games` ga imenuje s greškom, pa problem jedne igre ne zaustavlja ostale.

## Kontekst i sesija {#context-and-session}

`start`, `poll`, `stop` i `setup` dobivaju `Context`:

| Član | Što je |
|---|---|
| `settings` | `Settings` ([Instalacija i pokretanje](installing-and-running.md#settings)) |
| `data` | mapa podataka |
| `pid`, `exe` | ID procesa igre i putanja izvršne datoteke, kad je adapter pokrenut za igru koja radi; mapa instalacije je pored `exe` |
| `open(adapter, *, game=None, when=None, axes=..., source=..., multiplayer=..., meta=..., geo=None)` | nova `Session`. `game` nadjačava naziv igre adaptera (za adaptere koji pokrivaju više igara); `when` postavlja početak za sesije koje opisuju prošlost; `axes`, `source` i `multiplayer` su zadani iz adaptera; `meta` je rječnik zapisan u `meta.json`; `geo` (`{"lat0": .., "lon0": ..}`, ili postavi `session.geo` kasnije) smješta sesiju ravne karte na Zemlju, u `meta.json` i podnožje tablice |
| `close(session)` | završava sesiju: tablica, `heat.raw.parquet`, `meta.json`, njezin redak u `watcher.sqlite`. Sesija bez događaja i bez sirovih stavki se briše; ona s samo sirovim stavkama se čuva (bez tablice, bez retka u bazi). Prima `None`. Vraća put do tablice ili `None`. |

`Session` bilježi:

| Član | Što radi |
|---|---|
| `event(name, *, t=None, ms=None, x=None, y=None, z=None, player=None, team=None, session=None, **attrs)` | jedan redak. `t` je zadano sekunde od početka sesije, `ms` je zadano sada. Pozicija se računa samo kad su `x`, `y` i `z` svi zadani i konačni. Atributi `None` se izostavljaju. |
| `position(x, y, z, **kw)` | događaj imena `position` |
| `raw(type, payload=None, *, text=None, used=False, t=None, ms=None, **fields)` | sačuvati jednu stvar koju je izvor poslao, cijelu: bajtove paketa ili stranice (`payload`), redak ili JSON odgovor kako je došao (`text`), ili vrijednosti očitanja po imenu (`fields`, svaka u svom stupcu). `type` je izvorna riječ za to (ID paketa, naziv mapiranja, događaj iz dnevnika, krajnja točka); `used` kaže je li to također postalo retcima. Uokvirava se u `raw.bin` čim se pozove, zapisuje se kao `heat.raw.parquet` (zstd) kad se sesija zatvori ili oporavi, i broji se po `type` u `selfCheck.completeness` datoteke `meta.json` |
| `stat(key, value, how="set")` | statistika: `set` je postavlja, `add` dodaje, `max` ili `min` zadržava najveću ili najmanju |
| `now()` | sekunde od početka sesije |
| `meta` | rječnik zapisan u `meta.json` |
| `started`, `ended`, `folder`, `id`, `counts`, `positions` | kad, gdje i što je dosad zabilježeno |

`event`, `stat` i `raw` su sigurni za niti i mogu se pozivati iz radne niti.

**Svaki adapter čuva sve što mu izvor pošalje.** Retci su ono što preglednik crta; nisu zapis. Svaki paket koji stigne na port, svaka pročitana stranica dijeljene memorije (cijelo mapiranje, svaki put kad se promijeni), svaki redak dnevnika ili skripte izvoza (i one koje adapter ignorira), svaki JSON odgovor ili poslani dokument ide u `session.raw(...)` čim stigne - bez obzira na to postaje li redak - i ništa se ne proređuje ispod brzine kojom adapter čita. Stavka koja stigne prije nego što je sesija otvorena otvara jednu (sesija sa samo sirovim stavkama se čuva), ili se zadrži dok se jedna ne otvori; nikad se ne baca. Polja koja su jeftina za dekodiranje i sigurna u značenju idu i u retke. Ovo je [pravilo pretvarača](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md) 3DHeat-a: uživo poslani tok nestaje čim se pošalje, pa ono što adapter ne sačuva, zauvijek je izgubljeno, a ono što sačuva cijelo može se dekodirati onog dana kad netko shvati format. Veličina je cijena; zstd i kodiranje rječnikom je drže niskom, a ne izostavljanjem. Test svakog adaptera pošalje nešto što ne koristi i provjeri da se vrati cijelo iz `heat.raw.parquet`, te da je `selfCheck.completeness.lost` 0. `racing.Driving.raw` radi isto za adaptere za utrke (i otvara sesiju), a `racing.Pages` čuva stranice dijeljene memorije kad god se promijene njihovi bajtovi, brojeći u `meta.json`-u pod `unchanged_reads` ponovna čitanja koja nisu našla ništa novo.

Pravila o kojima se ostatak sustava oslanja:

- **Vlastiti retci igrača su označeni prema onome što izvor kaže.** `player="me"` gdje je izvor igračev vlastiti; gdje je svaki igrač zabilježen pod imenom, `own_car=1` na retcima automobila igrača (po igračevom indeksu u igri ili gledanom sudioniku), ili ime igrača kao `session.meta["player"]` (odmah zapisano u `meta.json`) kad izvor imenuje igrača. Nikad ne pogađajte: gdje izvor to ne kaže, uzmite ime iz postavke (`player_names`, `riot_id`) ili ne označavajte ništa. [NVIDIA highlights](nvidia-highlights.md) posuđuju pozicije samo iz takvih redaka (`platform.own_row`). Drugi igrači se prepoznaju po imenu ili ID-u.
- **Rute su omeđene događajima s pozicijama**: `spawn`, `respawn` i `session_start` počinju jednu; `death`, `finish`, `session_end` i `teleport` je završavaju. Kad se igrač pomakne bez putovanja (resetiranje, vraćanje unatrag, brzo putovanje, učitan spremljeni), zapišite `teleport` na mjestu koje je napustio, a zatim početak (`spawn`, ili `respawn` za resetiranje koje igra imenuje) na mjestu na koje je stigao, kako toplinska linija preglednika završi jednu rutu i počne sljedeću umjesto da crta preko karte. `Driving.jumped` to radi za vozila.
- **Pozicije ostaju u svjetskim koordinatama i jedinicama same igre**, opisanim s `axes`. Ne pretvarajte ih u drugi koordinatni sustav osim ako igra ne daje nikakav upotrebljiv svjetski sustav (simulatori letenja stavljaju zemljopisnu širinu i dužinu u ravnu kartu, `Tangent`, oko prvog očitanja - DCS oko fiksnog ishodišta svog bojišta - i predaju `geo=tangent.geo()` u `open`, pa podnožje kaže gdje je karta na Zemlji). `axes.scale` je mjerilo jedinica preglednika - množi svaku poziciju - i ostaje 1, pa se retci poklapaju s razinom izvezenom iz iste igre u istim jedinicama; jedinicu navedite u `axes.units`.
- **Ključevi statistike** su mala slova s donjim crticama, i nose svoju jedinicu gdje ona vrijedi (`distance_km`, `top_speed_kmh`, `max_altitude_m`, `duration_s`). Vrijeme koje se čuva kao najbolje počinje s `best_` (zadržava se s `min`), a mjesto završava s `_position`: `stats` pokazuje najmanji od tih kao najbolji, a najveći od svih ostalih ključeva (`db.lower_is_better`).

## Pomoćne funkcije {#helpers}

| Pomoćnik | Modul | Za što |
|---|---|---|
| `Follower(find, since, stamp=None)`, `game_started(pid)`, `newest(paths)`, `read_shared(path)`, `steam_libraries()` | `_logfollow` | praćenje dnevnika koji igra piše: dijeljena čitanja, samo retci ovog sjedenja, nove i zamijenjene datoteke, samo cijeli retci |
| `UdpPort(port, forward=None, grace=0.0, recheck=3.0)` s `try_open(who)`, `receive()`, `close()` | `racing` | UDP port za telemetriju na 127.0.0.1, uzima se samo kad je slobodan, predaje se drugom programu, opcionalno se prosljeđuje |
| `Driving(adapter, ctx, hz=10.0, jump=50.0)` s `sample(...)`, `event(...)`, `lap(...)`, `count(...)`, `close()` | `racing` | sesije vožnje: pozicije po fiksnoj brzini, udaljenost, najveća brzina, krugovi; pri skoku, `teleport` na mjestu gdje je auto bio i `spawn` gdje je sada (`jumped(...)`) |
| `SharedView.open(name)` | `simracing_shm` | imenovana dijeljena memorija igre, samo za čitanje, nikad se ne stvara |
| `ReplayAdapter` (`patterns`, `folders(ctx)`, `convert(path, ctx)`) | `replays` | praćena mapa replayeva: datoteke se pretvaraju kad prestanu rasti, u radnoj niti; prvi pregled samo bilježi što je tu, a `convert_existing(ctx, folder=None)` - naredba [`replays`](commands.md#replays) - pretvara te na zahtjev |
| `load_state`, `save_state` | `platform` | pamćenje onoga što je adapter koji je uvijek uključen vidio, u `<data>\state\<id>.json` |
| `FlightLog`, `Tangent` | `xplane` | evidencija leta (polijetanja, slijetanja, padovi, udaljenost) i ravna karta oko prvog očitanja (`Tangent.geo()` je `geo` sesije) |
| `backup_once(path)` | `gsi`, `racing` | pravilo `<file>.heat3d-backup` |
| Steamove datoteke | `_steam` | binarni i tekstualni KeyValues, mapa Steama iz registra |

Minimalni adapter za dnevnik, kao primjer (izmišljena igra):

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

Sesiju otvorite pri prvoj stvari vrijednoj zapisa, a ne u `start`, pa igra koja ostane u svojim izbornicima ne ostavlja ništa za sobom (prazna sesija se svakako briše).

## Testovi {#tests}

```bash
python -m pytest
```

`tests/conftest.py` daje svakom testu jednokratnu mapu podataka (`HEAT3D_WATCH_HOME`) i isključuje provjere ažuriranja i obavijesti (`HEAT3D_NO_UPDATE`, `HEAT3D_NO_TOAST`). Test adaptera gradi izlaz igre iz njezinog objavljenog formata - paketi iz specifikacije, redci dnevnika u formatu igre, datoteke u dokumentiranom rasporedu - i pokreće adapter izravno (skraćeno iz `tests/test_poe.py`; `data` i `install` su privremene mape):

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

Mrežni adapteri se testiraju prema lažnom lokalnom poslužitelju ili paketima poslanim preko UDP-a adapteru. Testovi koji provjeravaju prema stvarnim podacima igre na računalu razvojnog programera označeni su s `@pytest.mark.local` i preskaču se tamo gdje tih podataka nema. Ti podaci nikad ne idu u repozitorij. `test_core.py` također sadrži test koji pada ako se u paketu pojavi bilo koji kod koji bi mogao pisati u drugi proces (`test_memory_reading_cannot_write`).

## Iskren `verified` {#an-honest-verified}

`verified` kaže što je provjereno i kako, i što nije. Prikazuje ga `games` i svaka stranica igre, a igrači se na to oslanjaju. Primjeri iz koda:

- "tested on packets in the 2023, 2024 and 2025 formats built from EA's published specification, sent over UDP; untested against the game"
- "tested on documents in the published GSI format posted to the running adapter; untested against the running game"
- "tested on real stats files and schemas from a local install; change detection tested on files built in the binary KeyValues format"

Pišite "untested against the game" dok adapter nije zabilježio pokrenutu igru. Navedite samo metodu i toleranciju: nikad kartu, ID meča, ime igrača, datum, veličinu skupa podataka ili točan broj iz stvarnih datoteka, i nikad "ovo računalo" (čitatelji to ne znaju). Navedite izvor svakog pomaka i rasporeda i recite gdje su uspoređena dva izvora. Nikad ne tvrdite više nego što je učinjeno. Format koji je nagađan ili preuzet iz zajedničkih alata mora se tako i reći.

## Stranice igara {#the-game-pages}

Svaka stranica pod [Igre](games.md) generira se iz adaptera, pa uvijek odgovara kodu. Nakon dodavanja ili promjene adaptera, generirajte ih ponovno iz mape repozitorija:

```bash
HEAT3D_NO_UPDATE=1 python tools/gen_game_pages.py
```

(U PowerShellu: `$env:HEAT3D_NO_UPDATE = "1"; python tools/gen_game_pages.py`.) Dodajte `--check` da samo usporedi: ništa ne piše, a izlazi s kodom 1 kad je stranica zastarjela (također tablica igara u `docs/watcher.md`).

Skripta:

- učitava adaptere s `heat3d_watch.adapters.load()`, protiv prazne privremene mape podataka, pa u stranice ne završi nikakav profil memorije ni postavka s vašeg računala. Adapteri za memoriju se izostavljaju, jer dolaze iz profila igrača;
- ne piše ništa ako se modul adaptera ne može uvesti (stranice bi izgubile te igre);
- piše `docs/game-<adapter id>.md` za svaki adapter i `docs/games.md` s pregledom u tablici, a briše stranice adaptera koji više ne postoje;
- uzima "What is recorded", "Where it comes from", "How to switch it on", osi, oznaku igranja na mreži i "Verified" iz polja adaptera;
- pretvara docstring modula u "How it works". Pišite docstringe u običnom tekstualnom stilu koji moduli već koriste, a skripta ga pretvara: odlomci; popisi s `*`, `-` ili `1.`; rasporedi i primjeri uvučeni pod redak koji ih uvodi (postaju blokovi koda); naslov podcrtan crticama, ili kratki naslov s tekstom uvučenim odmah pod njim (postaju naslovi);
- popisuje ključeve statistike koje kod adaptera postavlja po imenu - `.stat("key", ...)`, obje strane `if` izraza i obrasce f-stringova kao `score.{team}` - u klasama adaptera i u pomoćnicima koje koriste. Ključevi uzeti iz varijable (tablica polja igre) se ne popisuju;
- odlučuje "Positions" iz `axes.units` adaptera (napomena koja počinje s "no" ili "none" znači bez pozicija) i iz onoga što njegov kod piše.

Ne uređujte generirane stranice ručno: promijenite adapter i ponovno pokrenite skriptu. Tablica u [Sve igre u jednoj tablici](watcher.md) je ispis naredbe `python -m heat3d_watch games --markdown`.
