---
title: "Razvoj"
nav_order: 12
lang: "sl"
source: development.md
source_hash: "cb213e22ddea"
nav_exclude: true
search_exclude: true
---
# Razvoj {#development}

Ta stran je za dodajanje igre: kako je zgrajen vmesnik (adapter), kako se preizkusi in kako nastane
njegova dokumentacija.

## Repozitorij {#the-repository}

| Pot | Kaj vsebuje |
|---|---|
| `heat3d_watch/cli.py` | ukazi ([Ukazi](commands.md)) |
| `heat3d_watch/watcher.py` | zanka v ozadju: seznam procesov, ena nit na vmesnik, posodobitve |
| `heat3d_watch/session.py` | posnetek: `events.jsonl`, `heat.parquet`, `meta.json`, obnovitev |
| `heat3d_watch/db.py` | `watcher.sqlite` |
| `heat3d_watch/config.py` | nastavitve in mapa podatkov |
| `heat3d_watch/safety.py`, `heat3d_watch/memory.py` | preverjanja pomnilnika in bralnik, ki samo bere ([Branje pomnilnika](memory-reading.md)) |
| `heat3d_watch/notify.py` | obvestila v Windows |
| `heat3d_watch/adapters/` | po en modul za igro ali družino iger; moduli, ki se začnejo z `_`, so skupni pomočniki |
| `heat3d_watch/decoders/` | dekoderji telemetrije vožnje, kopirani iz snemalnikov krogov 3DHeat GameCapture |
| `heat3d_update/` | posodabljalnik ([Posodobitve](updates.md)) |
| `mods/beamng/heat3d/` | protokolna modifikacija BeamNG, ki jo namesti `setup beamng` |
| `tests/` | testi |
| `tools/gen_game_pages.py` | napiše strani iger v tej dokumentaciji |

## Vmesnik {#an-adapter}

Vmesnik je dataclass, izpeljan iz `heat3d_watch.adapters.base.Adapter`. Njegova polja povedo, kaj je;
njegove metode opravijo delo.

| Polje | Privzeto | Kaj je |
|---|---|---|
| `id` | `""` | kratek in stalen: mape sej, `disabled`, `replay_folders` in `player_names` se nanj sklicujejo |
| `game` | `""` | ime igre, kot ga ljudje pišejo; seje se vpišejo pod njim |
| `kind` | `"telemetry"` | ena od vrst `telemetry`, `gsi`, `log`, `replay`, `platform`, `memory` ([Viri in pravila](sources-and-rules.md)) |
| `exes` | `()` | imena izvršljivih datotek (katere koli velikosti črk), ki pomenijo, da igra teče. Prazno: vmesnik je vedno vklopljen (`always` je true) |
| `multiplayer` | `True` | igra se igra prek spleta: njen pomnilnik se nikoli ne bere |
| `source` | `""` | od kod so številke, povedano enkrat |
| `records` | `()` | kaj se zapiše, ena postavka za vsako vrsto stvari |
| `enable` | `""` | kako vir vklopiti; prazno, kadar ni treba ničesar |
| `interval` | `0.1` | sekunde med anketiranji |
| `axes` | `Axes()` | navpična os sveta, zrcaljene osi, merilo enot pregledovalnika (pustite 1) in opomba o enotah |
| `verified` | `""` | kaj je bilo preverjeno, pošteno (glejte spodaj) |
| `completeness` | `{}` | račun vira po [pravilu pretvornika](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md) 3DHeat: `read` (kaj postane vrstice), `raw` (kar se hrani celo, pod katerim `type`), `missing` (česar vir ne da, in zakaj), `size` (kako velik je surovi tok na uro). Razdelek »Completeness« na strani igre je napisan iz tega |

`source`, `records`, `enable`, `verified` in `completeness` so dokumentacija, ne okras. `games` jih izpiše,
`games --markdown` iz njih naredi tabelo v [Vse igre v eni tabeli](watcher.md), strani iger pa so iz njih
ustvarjene. Napišite jih tako, da točno povedo, kaj koda počne.

Metode, vse neobvezne:

| Metoda | Kdo jo kliče | Kaj naj naredi |
|---|---|---|
| `missing(self) -> str \| None` | `games`, `status` in pred zagonom | pove, zakaj vmesnik tu ne more teči (ni najdena DLL, manjka mapa), ali `None` |
| `setup(self, ctx, *, apply) -> list[str]` | `setup` | vklopi lastni izhod igre; vrne eno vrstico za vsako spremembo in datoteke spremeni samo, kadar je `apply` true. Pred prvo spremembo datoteko shranite kot `<file>.heat3d-backup` in te varnostne kopije nikoli ne prepišite. Metodo prepišite samo, kadar je kaj za vklopiti: `can_setup` (true, kadar je `setup` prepisan) določi, ali `setup` to izvede ali pove, da ni nič za spremeniti; razred, ki služi več igram, prepiše `can_setup` za tiste, ki jih ne more nastaviti (`RallyAdapter` za Richard Burns Rally). |
| `start(self, ctx)` | ko se pojavi proces igre (vmesniki, ki delujejo vedno: ko se zažene `run`) | odpre vtičnice, poišče datoteke, zapomni si, kje začeti |
| `poll(self, ctx)` | vsakih `interval` sekund, v lastni niti vmesnika | prevzame, kar je igra povedala od zadnjega anketiranja, in to zapiše |
| `stop(self, ctx)` | ko igre ni več ali se watcher ustavi | zapre seje in vtičnice |

Vsak vmesnik teče v svoji niti (`Runner`). Izjema v `poll` se zapiše v dnevnik, vmesnik pa počaka
`min(5, interval × 10 + 0.5)` sekund, preden se ponovno anketira. Po 20 zaporednih napakah ali napaki v
`start` se vmesnik ustavi in ne zažene znova, dokler se ne spremeni id procesa igre. `missing()` se preveri
ob vsakem pregledu, zato naj bo poceni.

Objekt vmesnika se ponovno uporabi, ko se igra spet zažene, zato mora `start` ponastaviti vse, kar je
pustil prejšnji zagon.

### Registracija {#registering-it}

Dajte modul v `heat3d_watch/adapters/` in na koncu navedite vmesnike:

```python
ADAPTERS = [MyAdapter(id="mygame", game="My Game", ...)]
```

`adapters.load()` uvozi vsak modul v paketu (razen `base` in imen, ki se začnejo z `_`) in pobere njihove
`ADAPTERS`. Dva vmesnika z istim id-jem ustavita nalaganje z `ValueError`. Modul, ki se ne uspe uvoziti
(manjka odvisnost), izpusti svoje igre, `games` pa ga z napako imenuje, tako da ena težava pri eni igri ne
ustavi drugih.

## Kontekst in seja {#context-and-session}

`start`, `poll`, `stop` in `setup` dobijo `Context`:

| Član | Kaj je |
|---|---|
| `settings` | `Settings` ([Namestitev in zagon](installing-and-running.md#settings)) |
| `data` | mapa podatkov |
| `pid`, `exe` | id procesa igre in pot do izvršljive datoteke, kadar je bil vmesnik zagnan za tečočo igro; mapa namestitve je poleg `exe` |
| `open(adapter, *, game=None, when=None, axes=..., source=..., multiplayer=..., meta=..., geo=None)` | nova `Session`. `game` prepiše ime igre vmesnika (za vmesnike, ki pokrivajo mnogo iger); `when` nastavi začetek za seje, ki opisujejo preteklost; `axes`, `source` in `multiplayer` privzeto vzamejo vrednosti vmesnika; `meta` je slovar, zapisan v `meta.json`; `geo` (`{"lat0": .., "lon0": ..}`, ali nastavite `session.geo` kasneje) postavi sejo z ravnim zemljevidom na zemljo, v `meta.json` in v nogo tabele |
| `close(session)` | konča sejo: tabela, `heat.raw.parquet`, `meta.json`, njena vrstica v `watcher.sqlite`. Seja brez dogodkov in brez surovih postavk se izbriše; seja z samo surovimi postavkami ostane (brez tabele, brez vrstice v bazi). Sprejme `None`. Vrne pot tabele ali `None`. |

`Session` zapisuje:

| Član | Kaj naredi |
|---|---|
| `event(name, *, t=None, ms=None, x=None, y=None, z=None, player=None, team=None, session=None, **attrs)` | ena vrstica. `t` privzeto pomeni sekunde od začetka seje, `ms` pa zdaj. Položaj šteje samo, kadar so `x`, `y` in `z` vsi podani in končni. Atributi `None` se izpustijo. |
| `position(x, y, z, **kw)` | dogodek z imenom `position` |
| `raw(type, payload=None, *, text=None, used=False, t=None, ms=None, **fields)` | shrani eno stvar, ki jo je vir poslal, celo: bajte paketa ali strani (`payload`), vrstico ali odgovor JSON, kakršen je prišel (`text`), ali vrednosti branja po imenu (`fields`, vsaka v svojem stolpcu). `type` je izvorna beseda vira za to (id paketa, ime preslikave, dnevniški dogodek, končna točka); `used` pove, da je postalo tudi vrstice. Ob klicu se vpiše v `raw.bin`, ob zaprtju ali obnovitvi seje pa se zapiše kot `heat.raw.parquet` (zstd), in šteje se po `type` v `selfCheck.completeness` datoteke `meta.json` |
| `stat(key, value, how="set")` | statistika: `set` jo nastavi, `add` ji prišteje, `max` ali `min` pa obdrži največjo ali najmanjšo |
| `now()` | sekunde od začetka seje |
| `meta` | slovar, zapisan v `meta.json` |
| `started`, `ended`, `folder`, `id`, `counts`, `positions` | kdaj, kje in kaj je bilo doslej zapisano |

`event`, `stat` in `raw` so varni za niti in jih lahko kliče delovna nit.

**Vsak vmesnik hrani vse, kar mu vir pošlje.** Vrstice so tisto, kar pregledovalnik riše; niso zapis.
Vsak paket, ki pride do vrat, vsaka stran skupnega pomnilnika, prebrana celo (vsakič, ko se spremeni), vsaka
vrstica dnevnika ali izvoznega skripta (tudi tiste, ki jih vmesnik ignorira), vsak odgovor JSON ali objavljen
dokument gre v `session.raw(...)`, ko prispe, ne glede na to, ali postane vrstica - in nič se ne redči pod
hitrostjo, s katero vmesnik bere. Postavka, ki prispe, preden je seja odprta, odpre sejo (seja s samo
surovimi postavkami ostane), ali pa čaka, da se seja odpre; nikoli ni izgubljena. Polja, ki so poceni za
dekodirati in gotova po pomenu, gredo tudi v vrstice. To je [pravilo pretvornika](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md)
3DHeat: živ tok je izginil v trenutku, ko je bil poslan, zato je, kar vmesnik ne shrani, za vedno izgubljeno,
kar shrani celo, pa se lahko dekodira tisti dan, ko nekdo to razume. Velikost je cena; zstd in kodiranje s
slovarjem jo držita nizko, ne pa s tem, da se stvari izpuščajo. Test vsakega vmesnika pošlje nekaj, česar ne
uporablja, in preveri, da se to iz `heat.raw.parquet` vrne celo in da je `selfCheck.completeness.lost` 0.
`racing.Driving.raw` naredi isto za vmesnike dirk (in odpre sejo), `racing.Pages` pa shrani strani skupnega
pomnilnika, kadar se spremenijo njihovi bajti, in šteje ponovna branja, ki niso našla ničesar novega, v
`unchanged_reads` v `meta.json`.

Dogovori, na katerih stoji ostali sistem:

- **Lastne vrstice igralca so označene, po tem, kar pove vir.** `player="me"`, kadar je vir igralčev lastni;
  kjer je vsak igralec zapisan pod imenom, `own_car=1` na vrsticah igralčevega avtomobila (po indeksu igralca v
  igri ali po gledanem udeležencu), ali ime igralca kot `session.meta["player"]` (takoj zapisano v `meta.json`),
  kadar vir ime igralca navede. Nikoli ne ugibajte: kjer vir ne pove, vzemite ime iz nastavitve (`player_names`,
  `riot_id`) ali pa ne označite ničesar. [NVIDIA highlights](nvidia-highlights.md) si položaje izposojajo samo
  iz takih vrstic (`platform.own_row`). Drugi igralci gredo po imenu ali id-ju.
- **Poti so omejene z dogodki s položaji**: `spawn`, `respawn` in `session_start` začnejo eno; `death`,
  `finish`, `session_end` in `teleport` končajo eno. Kadar se je igralec premaknil, ne da bi potoval (ponastavitev,
  previjanje, hitro potovanje, naložen shranjeni položaj), zapišite `teleport` na mestu, ki ga je zapustil, in nato
  začetek (`spawn`, ali `respawn` za ponastavitev, ki jo igra imenuje) na mestu, do katerega je prišel, da
  toplotna črta pregledovalnika konča eno pot in začne naslednjo, namesto da bi risala čez zemljevid. `Driving.jumped`
  to naredi za vozila.
- **Položaji ostanejo v lastnih svetovnih koordinatah in enotah igre**, opisanih z `axes`. Ne pretvorite jih v
  drug sistem, razen če igra ne da uporabnega svetovnega sistema (simulatorji letenja dajo zemljepisno širino in
  dolžino v ravni zemljevid, `Tangent`, okoli prvega fiksa - DCS okoli fiksnega izhodišča svojega prizorišča - in
  pošljejo `geo=tangent.geo()` v `open`, da noga pove, kje na Zemlji je zemljevid). `axes.scale` je merilo enot
  pregledovalnika - pomnoži vsak položaj - in ostane 1, da se vrstice ujemajo z nivojem, izvoženim iz iste igre
  v istih enotah; enoto navedite v `axes.units`.
- **Ključi statistik** so z malimi črkami in podčrtaji, in nosijo svojo enoto, kjer velja
  (`distance_km`, `top_speed_kmh`, `max_altitude_m`, `duration_s`). Čas, ki se hrani kot najboljši, se začne z
  `best_` (hrani se z `min`), mesto se konča z `_position`: `stats` pokaže najnižjo od teh kot najboljšo, najvišjo
  pa pri vseh drugih ključih (`db.lower_is_better`).

## Pomočniki {#helpers}

| Pomočnik | Modul | Za kaj |
|---|---|---|
| `Follower(find, since, stamp=None)`, `game_started(pid)`, `newest(paths)`, `read_shared(path)`, `steam_libraries()` | `_logfollow` | sledenje dnevniku, ki ga igra piše: skupna branja, samo vrstice tega zagona, nove in zamenjane datoteke, samo cele vrstice |
| `UdpPort(port, forward=None, grace=0.0, recheck=3.0)` z `try_open(who)`, `receive()`, `close()` | `racing` | vrata telemetrije UDP na 127.0.0.1, zasedena samo, kadar so prosta, predana drugemu programu, po potrebi posredovana |
| `Driving(adapter, ctx, hz=10.0, jump=50.0)` s `sample(...)`, `event(...)`, `lap(...)`, `count(...)`, `close()` | `racing` | seje vozil: položaji pri stalni hitrosti, razdalja, največja hitrost, krogi; ob skoku `teleport` tam, kjer je bil avto, in `spawn` tam, kjer je zdaj (`jumped(...)`) |
| `SharedView.open(name)` | `simracing_shm` | imenovan skupni pomnilnik igre, samo za branje, nikoli ustvarjen |
| `ReplayAdapter` (`patterns`, `folders(ctx)`, `convert(path, ctx)`) | `replays` | nadzorovana mapa ponovitev: datoteke se pretvorijo, ko nehajo rasti, v delovni niti; prvi pogled samo zabeleži, kaj je tam, `convert_existing(ctx, folder=None)` - ukaz [`replays`](commands.md#replays) - pa jih pretvori na zahtevo |
| `load_state`, `save_state` | `platform` | pomnjenje, kaj je vmesnik, ki deluje vedno, že videl, v `<data>\state\<id>.json` |
| `FlightLog`, `Tangent` | `xplane` | knjigovodstvo leta (vzleti, pristanki, trki, razdalja) in ravni zemljevid okoli prvega fiksa (`Tangent.geo()` je `geo` seje) |
| `backup_once(path)` | `gsi`, `racing` | pravilo `<file>.heat3d-backup` |
| datoteke Steama | `_steam` | binarni in besedilni KeyValues, mapa Steama iz registra |

Minimalen vmesnik za dnevnik, kot ponazoritev (izmišljena igra):

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

Sejo odprite s prvo stvarjo, vredno zapisa, ne v `start`, da igra, ki ostane v svojih menijih, ne pusti
ničesar za seboj (prazna seja se tako ali tako izbriše).

## Testi {#tests}

```bash
python -m pytest
```

`tests/conftest.py` da vsakemu testu zavrženo mapo podatkov (`HEAT3D_WATCH_HOME`) in izklopi preverjanja
posodobitev in obvestila (`HEAT3D_NO_UPDATE`, `HEAT3D_NO_TOAST`). Test vmesnika zgradi izhod igre iz njenega
objavljenega formata - paketi iz specifikacije, vrstice dnevnika v obliki igre, datoteke v dokumentirani
postavitvi - in vmesnik poganja neposredno (skrajšano iz `tests/test_poe.py`; `data` in `install` sta začasni
mapi):

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

Mrežni vmesniki se preizkušajo proti lažnemu lokalnemu strežniku ali s paketi, poslanimi preko UDP k
vmesniku. Testi, ki preverjajo prave podatke igre na razvijalčevem računalniku, so označeni z
`@pytest.mark.local` in se preskočijo, kjer teh podatkov ni. Ti podatki nikoli ne gredo v repozitorij.
`test_core.py` vsebuje tudi test, ki pade, če se v paketu pojavi kakršna koli koda, ki bi lahko pisala v
drug proces (`test_memory_reading_cannot_write`).

## Pošten `verified` {#an-honest-verified}

`verified` pove, kaj je bilo preverjeno in kako, in kaj ni. Prikaže ga `games` in vsaka stran igre, igralci
se nanj zanesejo. Primeri iz kode:

- »tested on packets in the 2023, 2024 and 2025 formats built from EA's published specification, sent
  over UDP; untested against the game«
- »tested on documents in the published GSI format posted to the running adapter; untested against the
  running game«
- »tested on real stats files and schemas from a local install; change detection tested on files built
  in the binary KeyValues format«

Dokler vmesnik ni zabeležil tekoče igre, napišite »untested against the game«. Navedite samo metodo in
toleranco: nikoli zemljevida, id-ja tekme, imena igralca, datuma, velikosti korpusa ali natančnega števila iz
pravih datotek, in nikoli »this machine« (bralniki tega ne poznajo). Navedite vir vsakega odmika in postavitve
ter povejte, kje sta primerjana dva vira. Nikoli ne trdite več, kot je bilo storjeno. Format, ki je bil
uganjen ali vzet iz skupnostnih orodij, zapišite kot to.

## Strani iger {#the-game-pages}

Vsaka stran pod [Igre](games.md) je ustvarjena iz vmesnikov, zato se vedno ujema s kodo. Po dodajanju ali
spremembi vmesnika jih iz mape repozitorija znova ustvarite:

```bash
HEAT3D_NO_UPDATE=1 python tools/gen_game_pages.py
```

(V PowerShellu: `$env:HEAT3D_NO_UPDATE = "1"; python tools/gen_game_pages.py`.) Dodajte `--check`, da samo
primerja: ne zapiše ničesar in izide s kodo 1, kadar je stran zastarela (tudi tabela iger v `docs/watcher.md`).

Skript:

- naloži vmesnike z `heat3d_watch.adapters.load()`, proti prazni začasni mapi podatkov, tako da na strani ne
  pride noben profil pomnilnika ali nastavitev z vašega računalnika. Vmesniki pomnilnika so izpuščeni, ker
  pridejo iz profilov igralcev;
- ne zapiše ničesar, če se kateri modul vmesnika ne uspe uvoziti (strani bi izgubile te igre);
- zapiše `docs/game-<adapter id>.md` za vsak vmesnik in `docs/games.md` s pregledno tabelo, ter izbriše strani
  vmesnikov, ki ne obstajajo več;
- vzame »What is recorded«, »Where it comes from«, »How to switch it on«, osi, oznako večigralskosti in
  »Verified« iz polj vmesnika;
- docstring modula spremeni v »How it works«. Docstringe pišite v golem besedilu, kot ga že uporabljajo moduli,
  skript pa ga pretvori: odstavki; seznami z `*`, `-` ali `1.`; postavitve in primeri, zamaknjeni pod vrstico, ki jih
  uvaja (postanejo kodni odseki); naslov, podčrtan s pomišljaji, ali kratka naslovna vrstica, katere besedilo je
  zamaknjeno neposredno pod njo (postanejo naslovi);
- našteje ključe statistik, ki jih koda vmesnika nastavlja po imenu - `.stat("key", ...)`, obe strani pogoja
  `if` in vzorce f-niza, kot je `score.{team}` - v razredih vmesnika in v pomočnikih, ki jih uporablja. Ključi, vzeti iz
  spremenljivke (tabela polj igre), niso našteti;
- odloči o »Positions« iz `axes.units` vmesnika (opomba, ki se začne z »no« ali »none«, pomeni brez položajev) in iz
  tega, kar njegova koda zapisuje.

Strani, ustvarjenih s skriptom, ne urejajte ročno: spremenite vmesnik in skript znova zaženite. Tabela v
[Vse igre v eni tabeli](watcher.md) je izpis ukaza `python -m heat3d_watch games --markdown`.
