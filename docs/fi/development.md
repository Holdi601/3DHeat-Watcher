---
title: "Kehitys"
nav_order: 12
lang: "fi"
source: development.md
source_hash: "cb213e22ddea"
nav_exclude: true
search_exclude: true
---
# Kehitys {#development}

Tämä sivu on tarkoitettu pelin lisäämiseen: miten sovitin rakennetaan, miten se testataan ja miten sen
dokumentaatio tehdään.

## Repositorio {#the-repository}

| Polku | Mitä se sisältää |
|---|---|
| `heat3d_watch/cli.py` | komennot ([Komennot](commands.md)) |
| `heat3d_watch/watcher.py` | taustasilmukka: prosessilista, yksi säie sovitinta kohden, päivitykset |
| `heat3d_watch/session.py` | tallenne: `events.jsonl`, `heat.parquet`, `meta.json`, palautus |
| `heat3d_watch/db.py` | `watcher.sqlite` |
| `heat3d_watch/config.py` | asetukset ja datakansio |
| `heat3d_watch/safety.py`, `heat3d_watch/memory.py` | muistitarkistukset ja vain-luku-lukija ([Muistin lukeminen](memory-reading.md)) |
| `heat3d_watch/notify.py` | Windowsin ilmoitukset |
| `heat3d_watch/adapters/` | yksi moduuli pelia tai pelisarjaa kohden; alaviivalla alkavat moduulit ovat yhteisiä apufunktioita |
| `heat3d_watch/decoders/` | kilpailutelemetrian dekooderit, kopioitu 3DHeat GameCapturen kierrosajureista |
| `heat3d_update/` | päivittäjä ([Päivitykset](updates.md)) |
| `mods/beamng/heat3d/` | BeamNGin protokollamodi, jonka `setup beamng` asentaa |
| `tests/` | testit |
| `tools/gen_game_pages.py` | kirjoittaa tämän dokumentaation pelisivut |

## Sovitin {#an-adapter}

Sovitin on dataclass, joka periytyy luokasta `heat3d_watch.adapters.base.Adapter`. Sen kentät kertovat, mitä se on;
sen metodit tekevät työn.

| Kenttä | Oletus | Mitä se on |
|---|---|---|
| `id` | `""` | lyhyt ja pysyvä: sessiokansiot, `disabled`, `replay_folders` ja `player_names` viittaavat siihen |
| `game` | `""` | pelin nimi, kuten ihmiset sen kirjoittavat; sessiot tallennetaan sen alle |
| `kind` | `"telemetry"` | yksi seuraavista: `telemetry`, `gsi`, `log`, `replay`, `platform`, `memory` ([Lähteet ja säännöt](sources-and-rules.md)) |
| `exes` | `()` | suoritettavien tiedostojen nimet (mikä tahansa kirjainkoko), jotka tarkoittavat, että peli on käynnissä. Tyhjä: sovitin on aina päällä (`always` on tosi) |
| `multiplayer` | `True` | peliä pelataan verkossa: sen muistia ei koskaan lueta |
| `source` | `""` | mistä luvut tulevat, sanottuna kerran |
| `records` | `()` | mitä tallennetaan, yksi kohta kutakin asiatyyppiä kohden |
| `enable` | `""` | miten lähde kytketään päälle; tyhjä, kun mitään ei tarvita |
| `interval` | `0.1` | sekunteja kyselyjen välillä |
| `axes` | `Axes()` | maailman ylösakseli, peilatut akselit, katselimen yksikkömittakaava (pidä 1) ja huomautus yksiköistä |
| `verified` | `""` | mitä on tarkistettu, rehellisesti (katso alla) |
| `completeness` | `{}` | lähteen selostus 3DHeatin [muuntajasäännön](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md) mukaan: `read` (mistä tulee rivejä), `raw` (mikä säilytetään kokonaisena, minkä `type`-nimen alla), `missing` (mitä lähde ei anna, ja miksi), `size` (kuinka suuri raaka syöte on tunnissa). Pelisivun osio "Completeness" kirjoitetaan tästä |

`source`, `records`, `enable`, `verified` ja `completeness` ovat dokumentaatiota, eivät koristeita. `games` tulostaa
ne, `games --markdown` tekee taulukon kohdassa [Kaikki pelit yhdessä taulukossa](watcher.md), ja pelisivut
generoidaan niistä. Kirjoita ne niin, että ne sanovat tarkalleen, mitä koodi tekee.

Metodit, kaikki valinnaisia:

| Metodi | Kutsutaan | Mitä sen pitäisi tehdä |
|---|---|---|
| `missing(self) -> str \| None` | `games`:n, `status`:n ja ennen käynnistystä | kertoo, miksi sovitin ei voi toimia täällä (DLL ei löydy, kansio puuttuu), tai `None` |
| `setup(self, ctx, *, apply) -> list[str]` | `setup`:n kautta | kytkee pelin oman tulostuksen päälle; palauttaa yhden rivin kullekin muutokselle, ja muuttaa tiedostoja vain kun `apply` on tosi. Varmuuskopioi tiedosto nimellä `<file>.heat3d-backup` ennen sen ensimmäistä muutosta, äläkä koskaan ylikirjoita sitä varmuuskopiota. Ylikirjoita vain silloin, kun on jotain kytkettävää: `can_setup` (tosi, kun `setup` on ylikirjoitettu) päättää, ajaako `setup` sen vai kertooko se, ettei muutettavaa ole; luokka, joka palvelee useita pelejä, ylikirjoittaa `can_setup`:n niille, joita se ei voi asettaa (`RallyAdapter` Richard Burns Rallylle). |
| `start(self, ctx)` | kun pelin prosessi ilmestyy (aina päällä olevat sovittimet: kun `run` käynnistyy) | avaa socketit, etsii tiedostot, muistaa mistä aloitetaan |
| `poll(self, ctx)` | joka `interval`-sekunti, sovittimen omassa säikeessä | ottaa, mitä peli sanoi edellisen kyselyn jälkeen, ja tallentaa sen |
| `stop(self, ctx)` | kun peli on poissa tai watcher pysähtyy | sulkee sessiot ja socketit |

Jokainen sovitin ajaa omassa säikeessään (`Runner`). `poll`:n poikkeus kirjataan lokiin, ja sovitin odottaa
`min(5, interval × 10 + 0.5)` sekuntia ennen seuraavaa kyselyä. Kahdenkymmenen peräkkäisen virheen jälkeen tai
virheen jälkeen `start`:ssa sovitin pysäytetään, eikä sitä käynnistetä uudelleen ennen kuin pelin prosessin tunnus
vaihtuu. `missing()` tarkistetaan jokaisella skannauksella, joten pidä se kevyenä.

Sovitinolio käytetään uudelleen, kun peli käynnistyy uudelleen, joten `start`:n on nollattava kaikki, mitä edellinen
ajo jätti jälkeensä.

### Rekisteröinti {#registering-it}

Laita moduuli kansioon `heat3d_watch/adapters/` ja listaa sovittimet sen lopussa:

```python
ADAPTERS = [MyAdapter(id="mygame", game="My Game", ...)]
```

`adapters.load()` tuo jokaisen moduulin paketista (paitsi `base` ja alaviivalla alkavat nimet) ja kerää niiden
`ADAPTERS`-listat. Kaksi sovitinta samalla tunnuksella pysäyttää latauksen `ValueError`-virheellä. Moduuli, jonka
tuonti epäonnistuu (puuttuva riippuvuus), jättää pelinsä pois ja `games` nimeää sen virheen kanssa, joten yhden pelin
ongelma ei pysäytä muita.

## Context ja Session {#context-and-session}

`start`, `poll`, `stop` ja `setup` saavat `Context`-olion:

| Jäsen | Mitä se on |
|---|---|
| `settings` | `Settings` ([Asennus ja käynnistys](installing-and-running.md#settings)) |
| `data` | datakansio |
| `pid`, `exe` | pelin prosessin tunnus ja suoritettavan tiedoston polku, kun sovitin käynnistettiin käynnissä olevalle pelille; asennuskansio on `exe`:n vieressä |
| `open(adapter, *, game=None, when=None, axes=..., source=..., multiplayer=..., meta=..., geo=None)` | uusi `Session`. `game` ohittaa sovittimen pelin nimen (sovittimille, jotka kattavat monta peliä); `when` asettaa alun sessioille, jotka kuvaavat menneisyyttä; `axes`, `source` ja `multiplayer` ovat oletuksena sovittimen omat; `meta` on sanakirja, joka kirjoitetaan tiedostoon `meta.json`; `geo` (`{"lat0": .., "lon0": ..}`, tai aseta `session.geo` myöhemmin) sijoittaa lentokartta-session maapallolle, tiedostoon `meta.json` ja taulun alatunnisteeseen |
| `close(session)` | lopettaa session: taulun, `heat.raw.parquet`:n, `meta.json`:n ja sen rivin tiedostossa `watcher.sqlite`. Sessio, jossa ei ole tapahtumia eikä raakakohteita, poistetaan; sessio, jossa on vain raakakohteita, säilytetään (ei taulua, ei riviä tietokannassa). Hyväksyy `None`:n. Palauttaa taulun polun tai `None`. |

`Session` tallentaa:

| Jäsen | Mitä se tekee |
|---|---|
| `event(name, *, t=None, ms=None, x=None, y=None, z=None, player=None, team=None, session=None, **attrs)` | yksi rivi. `t` on oletuksena sekunteja session alusta, `ms` on oletuksena nyt. Sijainti lasketaan vain, kun `x`, `y` ja `z` ovat kaikki annettu ja äärellisiä. `None`-attribuutit jätetään pois. |
| `position(x, y, z, **kw)` | tapahtuma nimeltä `position` |
| `raw(type, payload=None, *, text=None, used=False, t=None, ms=None, **fields)` | säilytä yksi asia, jonka lähde lähetti, kokonaisena: paketin tai sivun tavut (`payload`), rivi tai JSON-vastaus sellaisenaan (`text`), tai lukeman arvot nimillä (`fields`, jokainen omana sarakkeenaan). `type` on lähteen oma sana sille (paketin tunnus, kartoituksen nimi, lokitapahtuma, päätepiste); `used` kertoo, että se tuli myös riveiksi. Kehystetään tiedostoon `raw.bin` heti kun se kutsutaan, kirjoitetaan `heat.raw.parquet`:ksi (zstd), kun sessio suljetaan tai palautetaan, ja lasketaan `type`-kohtaisesti tiedoston `meta.json` kohtaan `selfCheck.completeness` |
| `stat(key, value, how="set")` | tilasto: `set` asettaa, `add` lisää siihen, `max` tai `min` pitää ennätyksen |
| `now()` | sekunteja session alusta |
| `meta` | sanakirja, joka kirjoitetaan tiedostoon `meta.json` |
| `started`, `ended`, `folder`, `id`, `counts`, `positions` | milloin, missä ja mitä on tallennettu tähän mennessä |

`event`, `stat` ja `raw` ovat säieturvallisia ja niitä voi kutsua työsäikeestä.

**Jokainen sovitin säilyttää kaiken, minkä sen lähde lähettää.** Rivit ovat sitä, mitä katselin piirtää; ne eivät ole
tallenne. Jokainen paketti, joka saapuu porttiin, jokainen jaetun muistin sivu, joka luetaan (koko kuvaus, joka kerta kun
se muuttuu), jokainen lokin tai vientiskriptin rivi (myös ne, joita sovitin ei käytä), jokainen JSON-vastaus tai lähetetty
asiakirja menee `session.raw(...)`-kutsuun sellaisenaan kuin se saapuu, riippumatta siitä, tuleeko siitä rivi - eikä mitään
harvenneta sovittimen lukunopeutta alemmas. Kohde, joka saapuu ennen kuin sessio on auki, avaa sen (sessio, jossa on vain
raakakohteita, säilytetään), tai se pidetään, kunnes sessio aukeaa; sitä ei koskaan pudoteta. Kentät, jotka ovat halpoja
dekoodata ja varmoja merkitykseltään, menevät myös riveille. Tämä on 3DHeatin [muuntajasääntö](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md):
suora syöte katoaa heti, kun se on lähetetty, joten mitä sovitin ei säilytä, on menetetty lopullisesti, ja mitä se säilyttää
kokonaisena, voidaan dekoodata sinä päivänä, kun joku ymmärtää sen. Koko on hinta; zstd ja sanakirjakoodaus pitävät sen
pienenä, eivät jättämällä asioita pois. Jokaisen sovittimen testi lähettää jotain, mitä se ei käytä, ja tarkistaa, että se
tulee takaisin kokonaisena tiedostosta `heat.raw.parquet`, ja että `selfCheck.completeness.lost` on 0. `racing.Driving.raw`
tekee saman kilpailusovittimille (ja avaa session), ja `racing.Pages` säilyttää jaetun muistin sivut aina, kun niiden
tavut muuttuvat, ja laskee tiedoston `meta.json` kohtaan `unchanged_reads` lukukerrat, jotka eivät löytäneet mitään uutta.

Säännöt, joihin muu järjestelmä luottaa:

- **Pelaajan oma rivit on merkitty sen mukaan, mitä lähde sanoo.** `player="me"`, kun lähde on pelaajan oma; kun jokainen
  pelaaja on tallennettu nimellä, `own_car=1` pelaajan auton riveille (pelin pelaajaindeksin tai katsotun osallistujan
  mukaan), tai pelaajan nimi `session.meta["player"]`:na (kirjoitetaan tiedostoon `meta.json` heti), kun lähde nimeää
  pelaajan. Älä arvaa koskaan: jos lähde ei sano, ota nimi asetuksesta (`player_names`, `riot_id`) tai älä merkitse mitään.
  [NVIDIA-kohokohdat](nvidia-highlights.md) lainaavat sijainteja vain tällaisilta riveiltä (`platform.own_row`). Muut
  pelaajat tunnistetaan nimellä tai tunnuksella.
- **Reitit rajautuvat tapahtumilla, joissa on sijainti**: `spawn`, `respawn` ja `session_start` aloittavat reitin;
  `death`, `finish`, `session_end` ja `teleport` lopettavat sen. Aina kun pelaaja liikkui matkustamatta (nollaus,
  takaisinkelaus, pikamatka, ladattu tallennus), kirjoita `teleport` lähtöpaikkaan ja sitten aloitus (`spawn`, tai
  `respawn` pelin nimeämälle nollaukselle) saapumispaikkaan, jotta katselimen reittiviiva päättää yhden reitin ja aloittaa
  seuraavan sen sijaan, että se piirtäisi kartan yli. `Driving.jumped` tekee sen ajoneuvoille.
- **Sijainnit pysyvät pelin omissa maailmankoordinaateissa ja yksiköissä**, kuvattuna `axes`:illa. Älä muunna niitä toiseen
  koordinaatistoon, ellei peli anna käyttökelpoista maailmakoordinaatistoa (lentosimulaattorit tuovat leveys- ja
  pituusasteet tasokarttaan, `Tangent`, ensimmäisen kiinnityksen ympärille - DCS:n kiinteän teatterin origon ympärille -
  ja antavat `geo=tangent.geo()` kutsuun `open`, jolloin alatunniste kertoo, missä kohdassa maapalloa kartta on). `axes.scale`
  on katselimen yksikkömittakaava - se kertoo jokaisen sijainnin sillä - ja pysyy 1:nä, jotta rivit osuvat kohdalleen samasta
  pelistä samoissa yksiköissä viedyn tason kanssa; kerro yksikkö kohdassa `axes.units`.
- **Tilastoavaimet** ovat pienaakkosia alaviivoilla, ja niissä on yksikkö, missä sellainen on (`distance_km`,
  `top_speed_kmh`, `max_altitude_m`, `duration_s`). Aika, joka pidetään parhaana, alkaa `best_`:llä (pidetään `min`:llä),
  sijoitus päättyy `_position`:iin: `stats` näyttää niistä pienimmän parhaana ja kaikista muista avaimista suurimman
  (`db.lower_is_better`).

## Apufunktiot {#helpers}

| Apufunktio | Moduuli | Käyttötarkoitus |
|---|---|---|
| `Follower(find, since, stamp=None)`, `game_started(pid)`, `newest(paths)`, `read_shared(path)`, `steam_libraries()` | `_logfollow` | pelin kirjoittaman lokin seuraamiseen: jaetut lukemat, vain tämän istunnon rivit, uudet ja korvatut tiedostot, vain kokonaiset rivit |
| `UdpPort(port, forward=None, grace=0.0, recheck=3.0)` metodeineen `try_open(who)`, `receive()`, `close()` | `racing` | UDP-telemetriaportti osoitteessa 127.0.0.1, otetaan vain kun se on vapaa, annetaan toiselle ohjelmalle, valinnaisesti välitettynä |
| `Driving(adapter, ctx, hz=10.0, jump=50.0)` metodeineen `sample(...)`, `event(...)`, `lap(...)`, `count(...)`, `close()` | `racing` | ajoneuvosessiot: sijainnit kiinteällä taajuudella, matka, huippunopeus, kierrokset; hypyssä `teleport` siinä, missä auto oli, ja `spawn` siinä, missä se on (`jumped(...)`) |
| `SharedView.open(name)` | `simracing_shm` | pelin nimetty jaettu muisti, vain luku, ei koskaan luoda |
| `ReplayAdapter` (`patterns`, `folders(ctx)`, `convert(path, ctx)`) | `replays` | valvottu replay-kansio: tiedostot muunnetaan kerran, kun ne lakkaavat kasvamasta, työsäikeessä; ensimmäinen katsaus vain merkitsee, mitä siellä on, ja `convert_existing(ctx, folder=None)` - [`replays`](commands.md#replays)-komento - muuntaa ne pyynnöstä |
| `load_state`, `save_state` | `platform` | muistaa, mitä aina päällä oleva sovitin on nähnyt, tiedostossa `<data>\state\<id>.json` |
| `FlightLog`, `Tangent` | `xplane` | lentokirjanpito (lähdöt, laskut, syöksyt, matka) ja tasokartta ensimmäisen kiinnityksen ympärillä (`Tangent.geo()` on session `geo`) |
| `backup_once(path)` | `gsi`, `racing` | sääntö `<file>.heat3d-backup` |
| Steamin tiedostot | `_steam` | binäärinen ja tekstimuotoinen KeyValues, Steamin kansio rekisteristä |

Minimaalinen lokisovitin esimerkkinä (kuvitteellinen peli):

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

Avaa sessio ensimmäisellä tallennettavalla asialla, älä `start`:ssa, jotta peli, joka jää valikkoihinsa, ei jätä
mitään jälkeensä (tyhjä sessio poistetaan joka tapauksessa).

## Testit {#tests}

```bash
python -m pytest
```

`tests/conftest.py` antaa jokaiselle testille heitettävän datakansion (`HEAT3D_WATCH_HOME`) ja kytkee pois
päivitystarkistukset ja ilmoitukset (`HEAT3D_NO_UPDATE`, `HEAT3D_NO_TOAST`). Sovitintesti rakentaa pelin tulosteen sen
julkaistusta muodosta - paketit määrityksestä, lokirivit pelin muodossa, tiedostot dokumentoidussa asettelussa - ja ajaa
sovitinta suoraan (lyhennetty tiedostosta `tests/test_poe.py`; `data` ja `install` ovat väliaikaisia kansioita):

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

Verkkosovittimia testataan väärennettyä paikallista palvelinta vastaan tai sovittimelle UDP:n yli lähetetyillä paketeilla.
Testit, jotka tarkistavat oikeaa pelidataa kehittäjän koneella, on merkitty `@pytest.mark.local`:lla ja ne ohitetaan,
kun tuota dataa ei ole. Se data ei mene koskaan repositorioon. `test_core.py` sisältää myös testin, joka epäonnistuu,
jos paketissa on mitä tahansa koodia, joka voisi kirjoittaa toiseen prosessiin (`test_memory_reading_cannot_write`).

## Rehellinen `verified` {#an-honest-verified}

`verified` kertoo, mitä on tarkistettu ja miten, ja mitä ei. `games` näyttää sen ja jokainen pelisivu, ja pelaajat luottavat
siihen. Esimerkkejä koodista:

- "tested on packets in the 2023, 2024 and 2025 formats built from EA's published specification, sent over UDP; untested
  against the game"
- "tested on documents in the published GSI format posted to the running adapter; untested against the running game"
- "tested on real stats files and schemas from a local install; change detection tested on files built in the binary
  KeyValues format"

Sano "untested against the game", kunnes sovitin on tallentanut käynnissä olevan pelin. Kerro menetelmä ja toleranssi
vain: älä koskaan karttaa, ottelutunnusta, pelaajan nimeä, päivämäärää, aineiston kokoa tai tarkkaa lukua oikeista
tiedostoista, äläkä koskaan "tämä kone" (lukijat eivät tiedä sitä). Nimeä jokaisen offsetin ja asettelun lähde, ja kerro,
missä kaksi lähdettä vertailtiin. Älä koskaan väitä enempää kuin on tehty. Muoto, joka arvattiin tai otettiin
yhteisön työkaluista, kerrotaan sellaisena.

## Pelisivut {#the-game-pages}

Jokainen sivu kohdassa [Pelit](games.md) on generoitu sovittimista, joten se vastaa aina koodia. Lisättyäsi tai muutettuasi
sovitinta, generoi sivut uudelleen repositorion kansiosta:

```bash
HEAT3D_NO_UPDATE=1 python tools/gen_game_pages.py
```

(PowerShellissä: `$env:HEAT3D_NO_UPDATE = "1"; python tools/gen_game_pages.py`.) Lisää `--check`, jos haluat vain vertailla:
se ei kirjoita mitään ja päättyy paluukoodilla 1, jos sivu on vanhentunut (myös `docs/watcher.md`:n pelitaulukko).

Skripti:

- lataa sovittimet `heat3d_watch.adapters.load()`-funktiolla tyhjää väliaikaista datakansiota vasten, joten yksikään muistiprofiili
  tai asetus koneellasi ei päädy sivuille. Muistisovittimet jätetään pois, koska ne tulevat pelaajien omista profiileista;
- ei kirjoita mitään, jos sovitinmoduulin tuonti epäonnistuu (sivuilta katoaisivat ne pelit);
- kirjoittaa `docs/game-<adapter id>.md` jokaiselle sovittimelle ja `docs/games.md`:n yleistaulukon kanssa, ja poistaa
  sellaisten sovittimien sivut, joita ei enää ole;
- ottaa osiot "What is recorded", "Where it comes from", "How to switch it on", akselit, moninpelilippu ja "Verified" sovittimen
  kentistä;
- muuttaa moduulin docstringin osioksi "How it works". Kirjoita docstringit samassa pelkässä tekstityylissä, jota moduulit jo
  käyttävät ja jonka skripti muuntaa: kappaleet; listat `*`:llä, `-`:llä tai `1.`:llä; asettelut ja esimerkit sisennettyinä
  rivin alle, joka esittelee ne (ne muuttuvat koodilohkoiksi); otsikko, joka on alleviivattu viivoilla, tai lyhyt otsikkorivi,
  jonka teksti on sisennetty suoraan sen alle (ne muuttuvat otsikoiksi);
- luettelee tilastoavaimet, jotka sovittimen koodi asettaa nimeltä - `.stat("key", ...)`, `if`-lausekkeen molemmat puolet ja
  f-merkkijonomallit kuten `score.{team}` - sovittimen luokista ja sen käyttämistä apufunktioista. Avaimia, jotka otetaan
  muuttujasta (pelin kenttien taulukko), ei luetella;
- päättää kohdan "Positions" sovittimen `axes.units`-kentästä (huomautus, joka alkaa "no" tai "none", tarkoittaa ei sijainteja)
  ja siitä, mitä sen koodi kirjoittaa.

Älä muokaa generoituja sivuja käsin: muuta sovitinta ja aja skripti uudelleen. Taulukko kohdassa
[Kaikki pelit yhdessä taulukossa](watcher.md) on komennon `python -m heat3d_watch games --markdown` tuloste.
