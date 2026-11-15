---
title: "Razvoj"
nav_order: 12
lang: "bs"
source: development.md
source_hash: "cb213e22ddea"
nav_exclude: true
search_exclude: true
---
# Razvoj {#development}

Ova stranica je za dodavanje igre: kako se gradi adapter, kako se testira i kako se pravi njegova dokumentacija.

## Repozitorij {#the-repository}

| Putanja | Šta sadrži |
|---|---|
| `heat3d_watch/cli.py` | komande ([Komande](commands.md)) |
| `heat3d_watch/watcher.py` | petlja u pozadini: lista procesa, jedna nit po adapteru, ažuriranja |
| `heat3d_watch/session.py` | snimak: `events.jsonl`, `heat.parquet`, `meta.json`, oporavak |
| `heat3d_watch/db.py` | `watcher.sqlite` |
| `heat3d_watch/config.py` | postavke i folder s podacima |
| `heat3d_watch/safety.py`, `heat3d_watch/memory.py` | memorijske provjere i čitač samo za čitanje ([Čitanje memorije](memory-reading.md)) |
| `heat3d_watch/notify.py` | Windows obavijesti |
| `heat3d_watch/adapters/` | jedan modul po igri ili porodici igara; moduli koji počinju s `_` su zajednički pomoćnici |
| `heat3d_watch/decoders/` | dekoderi trkaće telemetrije, kopirani iz snimača krugova 3DHeat GameCapture |
| `heat3d_update/` | program za ažuriranje ([Ažuriranja](updates.md)) |
| `mods/beamng/heat3d/` | BeamNG protokol mod koji instalira `setup beamng` |
| `tests/` | testovi |
| `tools/gen_game_pages.py` | piše stranice igara ove dokumentacije |

## Adapter {#an-adapter}

Adapter je dataclass izveden iz `heat3d_watch.adapters.base.Adapter`. Njegova polja kažu šta
je on; njegove metode rade posao.

| Polje | Zadano | Šta je to |
|---|---|---|
| `id` | `""` | kratko i stabilno: foldere sesija, `disabled`, `replay_folders` i `player_names` upućuju na njega |
| `game` | `""` | naziv igre kako ga ljudi pišu; sesije se spremaju pod njim |
| `kind` | `"telemetry"` | jedno od `telemetry`, `gsi`, `log`, `replay`, `platform`, `memory` ([Izvori i pravila](sources-and-rules.md)) |
| `exes` | `()` | nazivi izvršnih datoteka (bilo koja veličina slova) koji znače da igra radi. Prazno: adapter je uvijek uključen (`always` je tačno) |
| `multiplayer` | `True` | igra se online: njena memorija se nikad ne čita |
| `source` | `""` | odakle dolaze brojevi, rečeno jednom |
| `records` | `()` | šta se snima, jedna stavka po vrsti stvari |
| `enable` | `""` | kako uključiti izvor; prazno kad ništa ne treba |
| `interval` | `0.1` | sekunde između očitavanja |
| `axes` | `Axes()` | uzdužna osa svijeta, zrcaljene ose, skala jedinice preglednika (ostavite 1) i napomena o jedinicama |
| `verified` | `""` | šta je provjereno, iskreno (vidite dolje) |
| `completeness` | `{}` | račun izvora prema 3DHeat [pravilu konvertera](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md): `read` (šta postaje redovi), `raw` (šta se čuva cijelo, pod kojim `type`), `missing` (šta izvor ne daje, i zašto), `size` (koliko sirovi tok naraste za sat). Odjeljak "Completeness" na stranici igre piše se iz njega |

`source`, `records`, `enable`, `verified` i `completeness` su dokumentacija, a ne ukras. `games` ih ispisuje,
`games --markdown` pravi tabelu u [Sve igre u jednoj tabeli](watcher.md), a stranice igara se
generiraju iz njih. Napišite ih tako da kažu tačno ono što kod radi.

Metode, sve opcionalne:

| Metoda | Poziva se | Šta treba da radi |
|---|---|---|
| `missing(self) -> str \| None` | iz `games`, `status` i prije pokretanja | kaže zašto adapter ne može raditi ovdje (DLL nije nađen, folder nedostaje), ili `None` |
| `setup(self, ctx, *, apply) -> list[str]` | iz `setup` | uključuje vlastiti izlaz igre; vraća jednu liniju po promjeni, a datoteke mijenja samo kad je `apply` tačno. Datoteku sačuvajte kao `<file>.heat3d-backup` prije prve promjene i nikad ne prepisuj taj backup. Nadjačajte ga samo kad ima šta uključiti: `can_setup` (tačno kad je `setup` nadjačan) odlučuje hoće li `setup` pokrenuti ovo ili reći da nema šta mijenjati; klasa koja služi nekoliko igara nadjačava `can_setup` za one koje ne može podesiti (`RallyAdapter` za Richard Burns Rally). |
| `start(self, ctx)` | kad se pojavi proces igre (uvijek uključeni adapteri: kad `run` počne) | otvara sokete, nalazi datoteke, pamti odakle početi |
| `poll(self, ctx)` | svakih `interval` sekundi, u adapterovoj vlastitoj niti | uzima ono što je igra rekla od zadnjeg očitavanja i snima to |
| `stop(self, ctx)` | kad igre nema više ili se watcher zaustavi | zatvara sesije i sokete |

Svaki adapter radi u svojoj niti (`Runner`). Izuzetak u `poll` se zapisuje u log, a adapter čeka
`min(5, interval × 10 + 0.5)` sekundi do sljedećeg očitavanja. Nakon 20 uzastopnih neuspjeha, ili neuspjeha u
`start`, adapter se zaustavlja i ne pokreće se ponovo dok se ne promijeni id procesa igre.
`missing()` se provjerava pri svakom pregledu, zato neka bude jeftin.

Objekt adaptera se ponovo koristi kad se njegova igra opet pokrene, pa `start` mora resetirati sve što je prethodno
pokretanje ostavilo.

### Registriranje {#registering-it}

Stavite modul u `heat3d_watch/adapters/` i navedite adaptere na njegovom kraju:

```python
ADAPTERS = [MyAdapter(id="mygame", game="My Game", ...)]
```

`adapters.load()` uvozi svaki modul u paketu (osim `base` i imena koja počinju s `_`) i
skuplja njihove `ADAPTERS`. Dva adaptera s istim id-om zaustavljaju učitavanje s `ValueError`. Modul koji
se ne uspije uvesti (nedostaje zavisnost) izostavlja svoje igre, a `games` ga navodi s greškom, pa
problem jedne igre ne zaustavlja ostale.

## Context i Session {#context-and-session}

`start`, `poll`, `stop` i `setup` dobivaju `Context`:

| Član | Šta je |
|---|---|
| `settings` | `Settings` ([Instalacija i pokretanje](installing-and-running.md#settings)) |
| `data` | folder s podacima |
| `pid`, `exe` | id procesa i putanja izvršne datoteke igre, kad je adapter pokrenut za igru koja radi; instalacijski folder je pored `exe` |
| `open(adapter, *, game=None, when=None, axes=..., source=..., multiplayer=..., meta=..., geo=None)` | nova `Session`. `game` nadjačava adapterov naziv igre (za adaptere koji pokrivaju mnogo igara); `when` postavlja početak za sesije koje opisuju prošlost; `axes`, `source` i `multiplayer` zadano su adapterovi; `meta` je rječnik koji se upisuje u `meta.json`; `geo` (`{"lat0": .., "lon0": ..}`, ili kasnije postavite `session.geo`) smješta sesiju ravne mape na Zemlju, u `meta.json` i u podnožje tabele |
| `close(session)` | završava sesiju: tabela, `heat.raw.parquet`, `meta.json`, njena linija u `watcher.sqlite`. Sesija bez događaja i bez sirovih stavki se briše; ona samo sa sirovim stavkama se čuva (bez tabele, bez linije u bazi). Prihvata `None`. Vraća putanju tabele ili `None`. |

`Session` snima:

| Član | Šta radi |
|---|---|
| `event(name, *, t=None, ms=None, x=None, y=None, z=None, player=None, team=None, session=None, **attrs)` | jedan red. `t` je zadano u sekundama od početka sesije, `ms` je zadano sad. Pozicija se računa samo kad su `x`, `y` i `z` svi dati i konačni. Atributi `None` se izostavljaju. |
| `position(x, y, z, **kw)` | događaj s imenom `position` |
| `raw(type, payload=None, *, text=None, used=False, t=None, ms=None, **fields)` | čuva jednu stvar koju je izvor poslao, cijelu: bajte paketa ili stranice (`payload`), liniju ili JSON odgovor kako je stigao (`text`), ili vrijednosti jednog očitavanja po imenu (`fields`, svaka u svojoj koloni). `type` je izvorova vlastita riječ za to (id paketa, ime mapiranja, događaj dnevnika, endpoint); `used` kaže da je i postalo redovima. Smješta se u `raw.bin` u trenutku poziva, upisuje se kao `heat.raw.parquet` (zstd) kad se sesija zatvori ili oporavi, i broji se po `type` u `selfCheck.completeness` datoteke `meta.json` |
| `stat(key, value, how="set")` | statistika: `set` postavlja, `add` joj dodaje, `max` ili `min` zadržava |
| `now()` | sekunde od početka sesije |
| `meta` | rječnik koji se upisuje u `meta.json` |
| `started`, `ended`, `folder`, `id`, `counts`, `positions` | kada, gdje, i šta je do sada snimljeno |

`event`, `stat` i `raw` su sigurni za niti i mogu se pozivati iz radničke niti.

**Svaki adapter čuva sve što njegov izvor pošalje.** Redovi su ono što preglednik crta; oni
nisu zapis. Svaki paket koji stigne na port, svaka pročitana stranica dijeljene memorije (cijelo mapiranje,
svaki put kad se promijeni), svaka linija loga ili izvoznog skripta (i one koje adapter ignorira), svaki
JSON odgovor ili poslani dokument ide u `session.raw(...)` kako stiže, bilo da postane
red ili ne - i ništa se ne prorjeđuje ispod učestalosti kojom adapter čita. Stavka koja stigne prije nego što je sesija
otvorena otvara je (sesija samo sa sirovim stavkama se čuva), ili se drži dok se ne otvori; nikad se
ne odbacuje. Polja koja se jeftino dekodiraju i imaju sigurno značenje idu i u redove. Ovo je 3DHeat
[pravilo konvertera](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md): živi tok nestaje
čim je poslan, pa je ono što adapter ne sačuva izgubljeno zauvijek, a ono što čuva cijelo može biti
dekodirano onog dana kad ga neko razumije. Veličina je cijena; zstd i rječničko kodiranje je drže
nisko, a ne izostavljanje stvari. Test svakog adaptera šalje nešto što ne koristi i provjerava da se vraća
cijelo iz `heat.raw.parquet`, i da je `selfCheck.completeness.lost` 0. `racing.Driving.raw`
radi isto za trkaće adaptere (i otvara sesiju), a `racing.Pages` čuva stranice dijeljene memorije
kad god im se bajti promijene, brojeći ponovna čitanja koja nisu našla ništa novo u `unchanged_reads`
iz `meta.json`.

Konvencije na koje se ostatak sistema oslanja:

- **Igračevi vlastiti redovi su označeni, prema onome što izvor kaže.** `player="me"` tamo gdje je izvor
  igračev vlastiti; gdje je svaki igrač snimljen pod imenom, `own_car=1` na redovima igračevog automobila
  (po indeksu igrača igre ili posmatranom učesniku), ili igračevo ime kao `session.meta["player"]`
  (odmah upisano u `meta.json`) kad izvor imenuje igrača. Nikad ne pogađajte: gdje izvor
  ne kaže, uzmite ime iz postavke (`player_names`, `riot_id`) ili ne označavajte ništa.
  [NVIDIA highlighti](nvidia-highlights.md) pozajmljuju pozicije samo iz takvih redova
  (`platform.own_row`). Ostali igrači idu po svom imenu ili id-u.
- **Rute omeđuju događaji s pozicijama**: `spawn`, `respawn` i `session_start` počinju jednu;
  `death`, `finish`, `session_end` i `teleport` je završavaju. Kad god se igrač pomjerio bez putovanja
  (reset, premotavanje, brzo putovanje, učitano spremanje), napišite `teleport` na mjestu koje je napušteno, a zatim
  početak (`spawn`, ili `respawn` za reset koji igra imenuje) na mjestu na koje je stigao, tako da linijska
  toplotna mapa preglednika završi jednu rutu i počne sljedeću umjesto da crta preko mape. `Driving.jumped` to radi
  za vozila.
- **Pozicije ostaju u igrinim vlastitim koordinatama i jedinicama svijeta**, opisanim s `axes`. Ne
  pretvarajte ih u drugi okvir osim ako igra ne daje upotrebljiv okvir svijeta (simulatori leta stavljaju
  geografsku širinu i dužinu u ravnu mapu, `Tangent`, oko prve tačke - DCS oko stalnog ishodišta
  svog teatra - i prosljeđuju `geo=tangent.geo()` u `open`, pa podnožje kaže gdje na Zemlji je
  mapa). `axes.scale` je skala jedinice preglednika
  - množi svaku poziciju njome - i ostaje 1, tako da se redovi poklapaju s nivoom izvezenim
  iz iste igre u istim jedinicama; jedinicu navedite u `axes.units`.
- **Ključevi statistika** su malim slovima s donjim crtama i nose svoju jedinicu gdje se primjenjuje
  (`distance_km`, `top_speed_kmh`, `max_altitude_m`, `duration_s`). Vrijeme koje se čuva kao najbolje počinje s
  `best_` (čuva se s `min`), mjesto završava na `_position`: `stats` pokazuje najniže od njih kao
  najbolje, a najviše od svakog drugog ključa (`db.lower_is_better`).

## Pomoćnici {#helpers}

| Pomoćnik | Modul | Za šta |
|---|---|---|
| `Follower(find, since, stamp=None)`, `game_started(pid)`, `newest(paths)`, `read_shared(path)`, `steam_libraries()` | `_logfollow` | praćenje loga koji igra piše: dijeljena čitanja, samo linije ovog sjedenja, nove i zamijenjene datoteke, samo cijele linije |
| `UdpPort(port, forward=None, grace=0.0, recheck=3.0)` s `try_open(who)`, `receive()`, `close()` | `racing` | UDP telemetrijski port na 127.0.0.1, zauzet samo kad je slobodan, ustupljen drugom programu, po želji prosljeđivan |
| `Driving(adapter, ctx, hz=10.0, jump=50.0)` s `sample(...)`, `event(...)`, `lap(...)`, `count(...)`, `close()` | `racing` | sesije vozila: pozicije stalnom učestalošću, udaljenost, najveća brzina, krugovi; pri skoku `teleport` gdje je auto bio i `spawn` gdje je sad (`jumped(...)`) |
| `SharedView.open(name)` | `simracing_shm` | imenovana dijeljena memorija igre, samo za čitanje, nikad se ne stvara |
| `ReplayAdapter` (`patterns`, `folders(ctx)`, `convert(path, ctx)`) | `replays` | praćeni folder sa snimcima: datoteke se pretvaraju kad prestanu rasti, u radničkoj niti; prvi pregled samo bilježi šta je tu, a `convert_existing(ctx, folder=None)` - komanda [`replays`](commands.md#replays) - pretvara te na zahtjev |
| `load_state`, `save_state` | `platform` | pamćenje onoga što je uvijek uključeni adapter vidio, u `<data>\state\<id>.json` |
| `FlightLog`, `Tangent` | `xplane` | vođenje evidencije leta (polijetanja, slijetanja, rušenja, udaljenost) i ravna mapa oko prve tačke (`Tangent.geo()` je `geo` sesije) |
| `backup_once(path)` | `gsi`, `racing` | pravilo `<file>.heat3d-backup` |
| Steamove datoteke | `_steam` | binarni i tekstualni KeyValues, Steam folder iz registra |

Minimalan adapter za log, kao ilustracija (izmišljena igra):

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

Otvorite sesiju s prvom stvari vrijednom snimanja, a ne u `start`, tako da igra ostavljena u menijima
ne ostavlja ništa iza sebe (prazna sesija se ionako briše).

## Testovi {#tests}

```bash
python -m pytest
```

`tests/conftest.py` daje svakom testu privremeni folder s podacima (`HEAT3D_WATCH_HOME`) i isključuje
provjere ažuriranja i obavijesti (`HEAT3D_NO_UPDATE`, `HEAT3D_NO_TOAST`). Test adaptera gradi
izlaz igre iz njenog objavljenog formata - pakete iz specifikacije, linije loga u formatu
igre, datoteke u dokumentiranom rasporedu - i direktno pokreće adapter (skraćeno iz
`tests/test_poe.py`; `data` i `install` su privremeni folderi):

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

Mrežni adapteri se testiraju prema lažnom lokalnom serveru ili s paketima poslanim preko UDP-a adapteru.
Testovi koji provjeravaju prema pravim podacima igre na računaru programera označeni su s `@pytest.mark.local` i
preskaču se tamo gdje tih podataka nema. Ti podaci nikad ne idu u repozitorij. `test_core.py` također
sadrži test koji pada ako se u paketu pojavi bilo kakav kod koji bi mogao pisati u drugi proces
(`test_memory_reading_cannot_write`).

## Iskren `verified` {#an-honest-verified}

`verified` kaže šta je provjereno i kako, i šta nije. Prikazuje ga `games` i svaka stranica
igre, a igrači se na njega oslanjaju. Primjeri iz koda:

- "tested on packets in the 2023, 2024 and 2025 formats built from EA's published specification, sent
  over UDP; untested against the game"
- "tested on documents in the published GSI format posted to the running adapter; untested against the
  running game"
- "tested on real stats files and schemas from a local install; change detection tested on files built
  in the binary KeyValues format"

Recite "untested against the game" dok adapter nije snimio igru koja radi. Navedite samo metodu i
toleranciju: nikad mapu, id meča, ime igrača, datum, veličinu korpusa ili tačan broj iz pravih
datoteka, i nikad "this machine" (čitaoci je ne poznaju). Imenujte izvor svakog
ofseta i rasporeda, i recite gdje su dva izvora upoređena. Nikad ne tvrdite više nego što je urađeno. Format koji je
pogođen ili preuzet iz alata zajednice kaže se da je to.

## Stranice igara {#the-game-pages}

Svaka stranica pod [Igre](games.md) generira se iz adaptera, pa uvijek odgovara kodu. Nakon
dodavanja ili mijenjanja adaptera, regenerirajte ih iz foldera repozitorija:

```bash
HEAT3D_NO_UPDATE=1 python tools/gen_game_pages.py
```

(U PowerShellu: `$env:HEAT3D_NO_UPDATE = "1"; python tools/gen_game_pages.py`.) Dodajte `--check` da samo
uporedite: ne piše ništa i izlazi s 1 kad je neka stranica zastarjela (također tabela igara u
`docs/watcher.md`).

Skripta:

- učitava adaptere s `heat3d_watch.adapters.load()`, uz prazan privremeni folder s podacima, tako da
  nijedan memorijski profil ni postavka na vašem računaru ne završi na stranicama. Memorijski adapteri se izostavljaju,
  jer dolaze iz vlastitih profila igrača;
- odbija pisati išta ako se neki modul adaptera ne uspije uvesti (stranice bi izgubile te igre);
- piše `docs/game-<adapter id>.md` za svaki adapter i `docs/games.md` s tabelom pregleda, i
  briše stranice adaptera koji više ne postoje;
- uzima "What is recorded", "Where it comes from", "How to switch it on", ose, zastavicu
  multiplayera i "Verified" iz adapterovih polja;
- pretvara docstring modula u "How it works". Pišite docstringove u stilu običnog teksta koji
  moduli već koriste, a koji skripta pretvara: odlomci; liste sa `*`, `-` ili `1.`; rasporedite i
  primjeri uvučeni ispod linije koja ih uvodi (postaju blokovi koda); naslov podvučen
  crticama, ili kratka linija naslova s tekstom uvučenim direktno ispod nje (postaju naslovi);
- navodi ključeve statistika koje adapterov kod postavlja po imenu - `.stat("key", ...)`, obje strane
  izraza `if` i obrasce f-stringova kao `score.{team}` - u adapterovim klasama i u
  pomoćnicima koje koristi. Ključevi uzeti iz varijable (tabela igrinih polja) se ne navode;
- odlučuje o "Positions" iz adapterovog `axes.units` (napomena koja počinje s "no" ili "none" znači da nema
  pozicija) i iz onoga što njegov kod piše.

Ne uređujte generirane stranice ručno: promijenite adapter i ponovo pokrenite skriptu. Tabela u
[Sve igre u jednoj tabeli](watcher.md) je izlaz iz `python -m heat3d_watch games --markdown`.
