---
title: "Fejlesztés"
nav_order: 12
lang: "hu"
source: development.md
source_hash: "cb213e22ddea"
nav_exclude: true
search_exclude: true
---
# Fejlesztés {#development}

Ez az oldal egy játék hozzáadásához szól: hogyan épül fel egy adapter, hogyan tesztelik, és hogyan készül
hozzá a dokumentáció.

## A tároló {#the-repository}

| Útvonal | Mit tartalmaz |
|---|---|
| `heat3d_watch/cli.py` | a parancsok ([Parancsok](commands.md)) |
| `heat3d_watch/watcher.py` | a háttérhurok: folyamatlista, egy szál adapterenként, frissítések |
| `heat3d_watch/session.py` | egy felvétel: `events.jsonl`, `heat.parquet`, `meta.json`, helyreállítás |
| `heat3d_watch/db.py` | `watcher.sqlite` |
| `heat3d_watch/config.py` | a beállítások és az adatmappa |
| `heat3d_watch/safety.py`, `heat3d_watch/memory.py` | a memória-ellenőrzések és a csak olvasó olvasó ([Memória olvasása](memory-reading.md)) |
| `heat3d_watch/notify.py` | Windows-értesítések |
| `heat3d_watch/adapters/` | egy modul játékonként vagy játékcsaládonként; az `_`-rel kezdődő modulok megosztott segédek |
| `heat3d_watch/decoders/` | a versenyzési telemetria-dekóderek, a 3DHeat GameCapture köridő-rögzítőiből másolva |
| `heat3d_update/` | a frissítő ([Frissítések](updates.md)) |
| `mods/beamng/heat3d/` | a BeamNG protokoll-mod, amelyet a `setup beamng` telepít |
| `tests/` | a tesztek |
| `tools/gen_game_pages.py` | ennek a dokumentációnak a játékoldalait írja |

## Egy adapter {#an-adapter}

Az adapter a `heat3d_watch.adapters.base.Adapter` osztályból származó dataclass. A mezői azt mondják meg, mi,
a metódusai pedig a munkát végzik.

| Mező | Alapérték | Mit jelent |
|---|---|---|
| `id` | `""` | rövid és állandó: a munkamenet-mappák, a `disabled`, a `replay_folders` és a `player_names` erre hivatkozik |
| `game` | `""` | a játék neve úgy, ahogy az emberek írják; a munkamenetek ez alatt kerülnek elmentésre |
| `kind` | `"telemetry"` | ezek egyike: `telemetry`, `gsi`, `log`, `replay`, `platform`, `memory` ([Források és szabályok](sources-and-rules.md)) |
| `exes` | `()` | futtatható fájlnevek (bármilyen kis-nagybetűvel), amelyek azt jelentik, hogy a játék fut. Üres: az adapter mindig be van kapcsolva (`always` igaz) |
| `multiplayer` | `True` | a játék online játszható: a memóriája soha nem olvasódik |
| `source` | `""` | honnan jönnek az adatok, egyszer leírva |
| `records` | `()` | mit rögzít, egy elem dolgonként |
| `enable` | `""` | hogyan kapcsolható be a forrás; üres, ha semmire sincs szükség |
| `interval` | `0.1` | másodpercek a lekérdezések között |
| `axes` | `Axes()` | a világ felfelé mutató tengelye, a tükrözött tengelyek, a nézegető mértékegység-skálája (maradjon 1) és egy megjegyzés a mértékegységekről |
| `verified` | `""` | mit ellenőriztek, őszintén (lásd lent) |
| `completeness` | `{}` | a forrás leírása a 3DHeat [konverter-szabálya](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md) szerint: `read` (mi lesz sorokká), `raw` (mi marad meg teljesen, milyen `type` alatt), `missing` (mit nem ad a forrás, és miért), `size` (mekkora egy óra alatt a nyers adatfolyam). A játékoldal „Completeness” (Teljesség) szakasza ebből készül |

A `source`, `records`, `enable`, `verified` és `completeness` dokumentáció, nem díszítés. A `games` kiírja őket, a
`games --markdown` készíti az [Összes játék egy táblázatban](watcher.md) táblázatát, a játékoldalak pedig ezekből
generálódnak. Úgy írd meg őket, hogy pontosan azt mondják, amit a kód csinál.

A metódusok, mind opcionálisak:

| Metódus | Hívja | Mit kell csinálnia |
|---|---|---|
| `missing(self) -> str \| None` | a `games`, a `status`, és az indítás előtt | megmondja, miért nem futhat az adapter itt (DLL nem található, mappa hiányzik), vagy `None` |
| `setup(self, ctx, *, apply) -> list[str]` | a `setup` | bekapcsolja a játék saját kimenetét; változásonként egy sort ad vissza, és csak akkor módosít fájlt, ha az `apply` igaz. Mielőtt egy fájlt először módosítasz, készíts róla `<file>.heat3d-backup` másolatot, és soha ne írd felül azt a másolatot. Csak akkor írd felül, ha van mit bekapcsolni: a `can_setup` (igaz, ha a `setup` felül van írva) dönti el, hogy a `setup` lefuttatja-e, vagy azt mondja, hogy nincs mit változtatni; a több játékot kiszolgáló osztály a `can_setup`-ot azokra a játékokra írja felül, amelyeket nem tud beállítani (a `RallyAdapter` a Richard Burns Rally-hoz). |
| `start(self, ctx)` | amikor a játék folyamata megjelenik (mindig futó adapterek: amikor a `run` indul) | socketek megnyitása, fájlok megtalálása, emlékezés arra, honnan kezdjen |
| `poll(self, ctx)` | minden `interval` másodpercben, az adapter saját szálában | átveszi, amit a játék az utolsó lekérdezés óta mondott, és rögzíti |
| `stop(self, ctx)` | amikor a játék eltűnt, vagy a watcher leáll | munkamenetek és socketek lezárása |

Minden adapter a saját szálában fut (`Runner`). A `poll`-ban keletkező kivételt naplózza, és az adapter a következő
lekérdezés előtt `min(5, interval × 10 + 0.5)` másodpercet vár. 20 egymás utáni hiba után, vagy ha a `start` hibázik, az
adaptert leállítják, és csak akkor indítják újra, ha a játék folyamatazonosítója megváltozik. A `missing()`-t minden
ellenőrzésnél meghívják, ezért legyen olcsó.

Egy adapter-objektum újrahasználódik, amikor a játék újra elindul, ezért a `start`-nak alaphelyzetbe kell állítania
mindent, amit az előző futás hagyott maga után.

### Regisztrálás {#registering-it}

Tedd a modult a `heat3d_watch/adapters/` mappába, és a végén sorold fel az adaptereket:

```python
ADAPTERS = [MyAdapter(id="mygame", game="My Game", ...)]
```

Az `adapters.load()` importálja a csomag minden modulját (a `base` és az `_`-rel kezdődő nevek kivételével), és
összegyűjti az `ADAPTERS`-eiket. Két azonos azonosítójú adapter a betöltést `ValueError`-ral állítja meg. Az a modul, amely
nem importálható (hiányzó függőség), kihagyja a játékait, és a `games` a hibával együtt megnevezi, így egy játék
problémája nem állítja meg a többit.

## Context és Session {#context-and-session}

A `start`, `poll`, `stop` és `setup` egy `Context`-et kap:

| Tag | Mit jelent |
|---|---|
| `settings` | a `Settings` ([Telepítés és futtatás](installing-and-running.md#settings)) |
| `data` | az adatmappa |
| `pid`, `exe` | a játék folyamatazonosítója és futtatható fájljának elérési útja, ha az adaptert egy futó játékhoz indították; a telepítési mappa az `exe` mellett van |
| `open(adapter, *, game=None, when=None, axes=..., source=..., multiplayer=..., meta=..., geo=None)` | új `Session`. A `game` felülírja az adapter játéknevét (sok játékot lefedő adaptereknél); a `when` a kezdetet állítja be a múltat leíró munkameneteknél; az `axes`, `source` és `multiplayer` alapértelmezés szerint az adapteréi; a `meta` a `meta.json`-ba írt szótár; a `geo` (`{"lat0": .., "lon0": ..}`, vagy később állítható a `session.geo`) egy lapos térképes munkamenetet a Földön helyez el, a `meta.json`-ban és a tábla láblécében |
| `close(session)` | befejezi a munkamenetet: a tábla, a `heat.raw.parquet`, a `meta.json` és a sora a `watcher.sqlite`-ban. Az, amelynek sem eseménye, sem nyers eleme nincs, törlődik; amelyiknek csak nyers eleme van, megmarad (nincs tábla, nincs sor az adatbázisban). Elfogadja a `None`-t. A tábla elérési útját vagy `None`-t ad vissza. |

A `Session` rögzít:

| Tag | Mit csinál |
|---|---|
| `event(name, *, t=None, ms=None, x=None, y=None, z=None, player=None, team=None, session=None, **attrs)` | egy sor. A `t` alapértelmezés szerint a munkamenet kezdete óta eltelt másodperc, az `ms` a jelen idő. Pozíciónak akkor számít, ha az `x`, `y` és `z` mind meg van adva és véges. A `None` attribútumok kimaradnak. |
| `position(x, y, z, **kw)` | `position` nevű esemény |
| `raw(type, payload=None, *, text=None, used=False, t=None, ms=None, **fields)` | egy dolog megőrzése, ahogy a forrás küldte: egy csomag vagy oldal bájtjai (`payload`), egy sor vagy JSON-válasz úgy, ahogy érkezett (`text`), vagy egy olvasás értékei névvel (`fields`, mindegyik saját oszlop). A `type` a forrás saját szava rá (csomagazonosító, egy leképezés neve, egy naplóesemény, egy végpont); a `used` jelzi, hogy sorrá is vált. A hívás pillanatában a `raw.bin`-be keretezve kerül, a munkamenet lezárásakor vagy helyreállításakor `heat.raw.parquet` (zstd) fájlként íródik ki, és `type` szerint számolódik a `meta.json` `selfCheck.completeness` részében |
| `stat(key, value, how="set")` | statisztika: `set`-tel beállítja, `add`-dal hozzáadja, megtartja a `max`-ot vagy a `min`-t |
| `now()` | másodpercek a munkamenet kezdete óta |
| `meta` | a `meta.json`-ba írt szótár |
| `started`, `ended`, `folder`, `id`, `counts`, `positions` | mikor, hol, és eddig mi lett rögzítve |

Az `event`, `stat` és `raw` szálbiztos, és egy munkaszálból is hívhatók.

**Minden adapter megőriz mindent, amit a forrása küld.** A sorok azok, amiket a nézegető rajzol; nem ezek a felvétel.
Minden csomag, amely egy portra érkezik, minden megosztott memóriaoldal, amit beolvasnak (a teljes leképezés, minden
változáskor), minden napló- vagy exportszkript-sor (amelyeket az adapter szintén figyelmen kívül hagy), minden JSON-válasz
vagy beküldött dokumentum megérkezéskor a `session.raw(...)`-hoz kerül, akár lesz belőle sor, akár nem - és semmi sem
ritul az adapter olvasási sebessége alá. Az a elem, amely munkamenet megnyitása előtt érkezik, megnyit egyet (a csak nyers
elemeket tartalmazó munkamenet megmarad), vagy addig tartja, amíg nyílik egy; soha nem vész el. Azok a mezők, amelyek
olcsón dekódolhatók és jelentésük biztos, a sorokra is kerülnek. Ez a 3DHeat [konverter-szabálya](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md):
az élő adatfolyam a küldés pillanatában elvész, így amit egy adapter nem tart meg, az örökre elveszik, és amit egészben
megőriz, azt a nap bármikor dekódolhatja, amikor valaki megérti. A méret az ár; a zstd és a szótár-kódolás ezt
alacsonyan tartja, nem úgy, hogy kihagy dolgokat. Minden adapter tesztje küld valamit, amit nem használ, és ellenőrzi,
hogy épségben visszajön a `heat.raw.parquet`-ból, és hogy a `selfCheck.completeness.lost` 0. A `racing.Driving.raw` ugyanezt
teszi a versenyzési adaptereknél (és megnyitja a munkamenetet), a `racing.Pages` pedig megőrzi a megosztott memóriaoldalakat,
valahányszor a bájtjaik változnak, és a `meta.json` `unchanged_reads` mezőjében számolja azokat az újraolvasásokat, amelyek
nem találtak újat.

A rendszer többi része által használt konvenciók:

- **A játékos saját sorait a forrás mondja meg jelölni.** `player="me"`, ahol a forrás a játékosé; ahol minden játékos
  név alatt van rögzítve, `own_car=1` a játékos autójának sorain (a játék játékosindexe vagy a megtekintett résztvevő alapján),
  vagy a játékos neve `session.meta["player"]`-ként (azonnal a `meta.json`-ba írva), ha a forrás megnevezi a játékost.
  Soha ne találgass: ahol a forrás nem mondja meg, a nevet a beállításból vedd (`player_names`, `riot_id`), vagy ne jelölj semmit.
  Az [NVIDIA-kiemelések](nvidia-highlights.md) csak ilyen sorokból kölcsönöznek pozíciókat (`platform.own_row`). A többi
  játékost a nevükön vagy azonosítójukon kell felismerni.
- **Az útvonalakat pozíciókkal rendelkező események határolják**: a `spawn`, `respawn` és `session_start` kezd egyet;
  a `death`, `finish`, `session_end` és `teleport` zár le. Valahányszor a játékos úgy mozdult el, hogy nem utazott
  (visszaállítás, visszatekerés, gyorsutazás, betöltött mentés), írj `teleport`-ot arra a helyre, ahonnan távozott, majd
  egy kezdetet (`spawn`, vagy `respawn` a játék által megnevezett visszaállításnál) arra a helyre, ahová megérkezett, hogy a
  nézegető útvonal-hője egy útvonalat lezárjon és a következőt kezdjen, ahelyett, hogy átrajzolná a térképet. A `Driving.jumped`
  ezt jármüveknél elvégzi.
- **A pozíciók a játék saját világkoordinátáiban és mértékegységeiben maradnak**, amelyeket az `axes` ír le. Ne konvertáld
  őket más koordinátarendszerbe, hacsak a játék nem ad használható világkeretet (a repülőszimulátorok a szélességi és
  hosszúsági fokot az első pozíció körül egy lapos térképbe teszik, `Tangent`-ba - a DCS a hadszíntere rögzített origója
  körül -, és a `geo=tangent.geo()` értéket adják át az `open`-nek, hogy a lábléc megmondja, hol van a térkép a Földön). Az
  `axes.scale` a nézegető mértékegység-skálája - minden pozíciót megszoroz vele -, és 1 marad, hogy a sorok ugyanabban a
  mértékegységben ugyanabból a játékból exportált szinttel essenek egybe; a mértékegységet az `axes.units`-ban mondd meg.
- **A statisztikakulcsok** kisbetűsek, aláhúzással, és ahol van mértékegység, azt is hordozzák (`distance_km`,
  `top_speed_kmh`, `max_altitude_m`, `duration_s`). A legjobbként megtartott idő `best_`-tel kezdődik (`min`-nel tartva),
  a helyezés `_position`-re végződik: a `stats` ezek legkisebbjét mutatja legjobbnak, minden más kulcs legnagyobbját
  (`db.lower_is_better`).

## Segédek {#helpers}

| Segéd | Modul | Mire |
|---|---|---|
| `Follower(find, since, stamp=None)`, `game_started(pid)`, `newest(paths)`, `read_shared(path)`, `steam_libraries()` | `_logfollow` | a játék által írt napló követése: megosztott olvasások, csak ennek az ülésnek a sorai, új és cserélt fájlok, csak teljes sorok |
| `UdpPort(port, forward=None, grace=0.0, recheck=3.0)` a `try_open(who)`, `receive()`, `close()` metódusokkal | `racing` | egy UDP-telemetriaport a 127.0.0.1-en, csak ha szabad, egy másik programnak átadva, opcionálisan továbbítva |
| `Driving(adapter, ctx, hz=10.0, jump=50.0)` a `sample(...)`, `event(...)`, `lap(...)`, `count(...)`, `close()` metódusokkal | `racing` | járműmunkamenetek: pozíciók állandó sebességgel, távolság, végsebesség, körök; ugrásnál `teleport` ott, ahol az autó volt, és `spawn` ott, ahol most van (`jumped(...)`) |
| `SharedView.open(name)` | `simracing_shm` | egy játék nevesített megosztott memóriája, csak olvasható, soha nem hoz létre újat |
| `ReplayAdapter` (`patterns`, `folders(ctx)`, `convert(path, ctx)`) | `replays` | figyelt visszajátszás-mappa: a fájlok akkor konvertálódnak egyszer, amikor már nem nőnek, egy munkaszálban; az első ellenőrzés csak feljegyzi, mi van benne, a `convert_existing(ctx, folder=None)` - a [`replays`](commands.md#replays) parancs - kérésre konvertálja ezeket |
| `load_state`, `save_state` | `platform` | emlékezés arra, mit látott egy mindig futó adapter, a `<data>\state\<id>.json` fájlban |
| `FlightLog`, `Tangent` | `xplane` | repülési nyilvántartás (felszállások, leszállások, lezuhanások, távolság) és az első pozíció körüli lapos térkép (a `Tangent.geo()` a munkamenet `geo`-ja) |
| `backup_once(path)` | `gsi`, `racing` | a `<file>.heat3d-backup` szabály |
| A Steam fájljai | `_steam` | bináris és szöveges KeyValues, a Steam-mappa a beállításjegyzékből |

Egy minimális naplóadapter, példaként (kitalált játék):

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

A munkamenetet az első, érdemes rögzíteni valót követően nyisd meg, ne a `start`-ban, így a menükben ragadt játék nem hagy
maga után semmit (az üres munkamenet úgyis törlődik).

## Tesztek {#tests}

```bash
python -m pytest
```

A `tests/conftest.py` minden tesztnek eldobható adatmappát ad (`HEAT3D_WATCH_HOME`), és kikapcsolja a frissítés-
ellenőrzést és az értesítéseket (`HEAT3D_NO_UPDATE`, `HEAT3D_NO_TOAST`). Egy adaptertest a játék kimenetét a közzétett
formátumából építi fel - csomagok a specifikációból, naplósorok a játék formátumában, fájlok a dokumentált elrendezésben -,
és közvetlenül hajtja az adaptert (a `tests/test_poe.py`-ból rövidítve; a `data` és az `install` ideiglenes mappák):

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

A hálózati adaptereket egy helyi, hamis szerverrel vagy az adapterhez UDP-n küldött csomagokkal tesztelik. A fejlesztő
gépén lévő valódi játékadatokkal ellenőrző teszteket `@pytest.mark.local` jelöli, és ott kihagyják, ahol ezek az adatok
hiányoznak. Ezek az adatok soha nem kerülnek a tárolóba. A `test_core.py` tartalmazza azt a tesztet is, amely elbukik, ha
a csomagban bármilyen olyan kód megjelenik, amely más folyamatba írhatna (`test_memory_reading_cannot_write`).

## Egy őszinte `verified` {#an-honest-verified}

A `verified` azt mondja meg, mit és hogyan ellenőriztek, és mit nem. A `games` kiírja, minden játékoldalon megjelenik,
a játékosok pedig erre támaszkodnak. Példák a kódból:

- „tested on packets in the 2023, 2024 and 2025 formats built from EA's published specification, sent
  over UDP; untested against the game”
- „tested on documents in the published GSI format posted to the running adapter; untested against the
  running game”
- „tested on real stats files and schemas from a local install; change detection tested on files built
  in the binary KeyValues format”

Mondd azt, hogy „untested against the game”, amíg az adapter nem rögzítette a futó játékot. Csak a módszert és a
tűrést add meg: soha ne adj meg térképet, mérkőzésazonosítót, játékosnevet, dátumot, korpusz-méretet vagy pontos számot
valódi fájlokból, és soha ne mondd, hogy „this machine” (az olvasók nem ismerik azt). Nevezd meg minden eltolás és elrendezés
forrását, és mondd meg, ha két forrást összehasonlítottak. Soha ne állíts többet, mint ami megtörtént. Egy kitalált vagy
közösségi eszközökből átvett formátumot úgy nevezz meg, ahogy van.

## A játékoldalak {#the-game-pages}

Minden oldal a [Játékok](games.md) alatt az adapterekből generálódik, így mindig egyezik a kóddal. Egy adapter
hozzáadása vagy módosítása után generáld újra őket a tároló mappájából:

```bash
HEAT3D_NO_UPDATE=1 python tools/gen_game_pages.py
```

(PowerShellben: `$env:HEAT3D_NO_UPDATE = "1"; python tools/gen_game_pages.py`.) A `--check` kapcsolóval csak összehasonlít:
nem ír semmit, és 1-gyel lép ki, ha egy oldal elavult (a `docs/watcher.md` játéktáblázatát is beleértve).

A szkript:

- betölti az adaptereket a `heat3d_watch.adapters.load()` függvénnyel, egy üres ideiglenes adatmappa ellen, így a gépeden
  lévő memória-profil vagy beállítás nem kerül az oldalakra. A memória-adaptereket kihagyja, mert azok a játékosok saját
  profiljaiból jönnek;
- nem ír semmit, ha egy adaptermodul nem importálható (az oldalak elveszítenék azokat a játékokat);
- minden adapterhez megírja a `docs/game-<adapter id>.md` fájlt, a `docs/games.md`-t pedig az áttekintő táblázattal, és
  törli azoknak az adaptereknek az oldalait, amelyek már nem léteznek;
- a „What is recorded” (Mit rögzít), „Where it comes from” (Honnan származik), „How to switch it on” (Hogyan kapcsolható be),
  a tengelyek, a többjátékos jelző és a „Verified” (Ellenőrizve) részeket az adapter mezőiből veszi;
- a modul docstringjét „How it works” (Hogyan működik) szöveggé alakítja. A docstringeket az eddig is használt, egyszerű
  szöveges stílusban írd, amelyet a szkript átalakít: bekezdések; listák `*`, `-` vagy `1.` jellel; az elrendezések és
  példák a bevezető sor alá behúzva (kódblokkok lesznek); a kötőjelekkel aláhúzott cím, vagy egy rövid címsor, amelynek a
  szövege közvetlenül alá van húzva (címsorok lesznek);
- felsorolja azokat a statisztikakulcsokat, amelyeket az adapter kódja név szerint állít - `.stat("key", ...)`, egy `if`
  kifejezés mindkét oldala, és az f-string minták, például `score.{team}` - az adapter osztályaiban és az általuk használt
  segédekben. A változóból vett kulcsokat (a játék mezőinek egy táblázata) nem sorolja fel;
- az `axes.units` alapján dönti el a „Positions” (Pozíciók) részt (a „no” vagy „none” kezdetű megjegyzés azt jelenti, nincs
  pozíció), és abból, amit a kódja ír.

A generált oldalakat ne szerkeszd kézzel: változtasd meg az adaptert, és futtasd újra a szkriptet. Az [Összes játék egy
táblázatban](watcher.md) táblázat a `python -m heat3d_watch games --markdown` kimenete.
