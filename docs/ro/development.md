---
title: "Dezvoltare"
nav_order: 12
lang: "ro"
source: development.md
source_hash: "cb213e22ddea"
nav_exclude: true
search_exclude: true
---
# Dezvoltare {#development}

Această pagină este pentru adăugarea unui joc: cum se construiește un adaptor, cum se testează și cum se face
documentația lui.

## Depozitul {#the-repository}

| Cale | Ce conține |
|---|---|
| `heat3d_watch/cli.py` | comenzile ([Comenzi](commands.md)) |
| `heat3d_watch/watcher.py` | bucla din fundal: lista proceselor, câte un fir de execuție pentru fiecare adaptor, actualizările |
| `heat3d_watch/session.py` | o înregistrare: `events.jsonl`, `heat.parquet`, `meta.json`, recuperarea |
| `heat3d_watch/db.py` | `watcher.sqlite` |
| `heat3d_watch/config.py` | setările și dosarul de date |
| `heat3d_watch/safety.py`, `heat3d_watch/memory.py` | verificările de memorie și cititorul doar în citire ([Citirea memoriei](memory-reading.md)) |
| `heat3d_watch/notify.py` | notificările Windows |
| `heat3d_watch/adapters/` | un modul pentru fiecare joc sau familie de jocuri; modulele al căror nume începe cu `_` sunt funcții ajutătoare comune |
| `heat3d_watch/decoders/` | decodoarele telemetriei de curse, copiate din înregistratoarele de tururi ale 3DHeat GameCapture |
| `heat3d_update/` | actualizatorul ([Actualizări](updates.md)) |
| `mods/beamng/heat3d/` | modificarea de protocol BeamNG pe care o instalează `setup beamng` |
| `tests/` | testele |
| `tools/gen_game_pages.py` | scrie paginile jocurilor din această documentație |

## Un adaptor {#an-adapter}

Un adaptor este o clasă dataclass derivată din `heat3d_watch.adapters.base.Adapter`. Câmpurile sale spun ce este;
metodele sale fac treaba.

| Câmp | Implicit | Ce este |
|---|---|---|
| `id` | `""` | scurt și stabil: dosarele de sesiune, `disabled`, `replay_folders` și `player_names` se referă la el |
| `game` | `""` | numele jocului cum îl scriu oamenii; sesiunile sunt trecute sub acest nume |
| `kind` | `"telemetry"` | unul dintre `telemetry`, `gsi`, `log`, `replay`, `platform`, `memory` ([Surse și reguli](sources-and-rules.md)) |
| `exes` | `()` | numele executabilelor (oricum scrise) care înseamnă că jocul rulează. Gol: adaptorul este mereu pornit (`always` este adevărat) |
| `multiplayer` | `True` | jocul se joacă online: memoria lui nu se citește niciodată |
| `source` | `""` | de unde vin cifrele, spus o singură dată |
| `records` | `()` | ce se înregistrează, câte un element pentru fiecare fel de lucru |
| `enable` | `""` | cum se pornește sursa; gol când nu este nevoie de nimic |
| `interval` | `0.1` | secunde între citiri |
| `axes` | `Axes()` | axa „sus” a lumii, axele oglindite, scara de unități a vizualizatorului (rămâne 1) și o notă despre unități |
| `verified` | `""` | ce a fost verificat, cinstit (vezi mai jos) |
| `completeness` | `{}` | descrierea sursei după [regula de convertor](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md) a 3DHeat: `read` (ce devine rânduri), `raw` (ce se păstrează întreg, sub ce `type`), `missing` (ce nu dă sursa, și de ce), `size` (cât de mare devine fluxul brut pe oră). Secțiunea „Completeness” a paginii jocului este scrisă din ea |

`source`, `records`, `enable`, `verified` și `completeness` sunt documentație, nu decor. `games` le afișează,
`games --markdown` face tabelul din [Toate jocurile într-un tabel](watcher.md), iar paginile jocurilor sunt
generate din ele. Scrieți-le astfel încât să spună exact ce face codul.

Metodele, toate opționale:

| Metodă | Apelată | Ce ar trebui să facă |
|---|---|---|
| `missing(self) -> str \| None` | de `games`, `status` și înainte de pornire | spune de ce nu poate rula adaptorul aici (un DLL nu a fost găsit, lipsește un dosar), sau `None` |
| `setup(self, ctx, *, apply) -> list[str]` | de `setup` | pornește ieșirea proprie a jocului; întoarce câte un rând pentru fiecare schimbare și schimbă fișiere doar când `apply` este adevărat. Faceți o copie de rezervă a unui fișier ca `<file>.heat3d-backup` înainte de prima schimbare și nu suprascrieți niciodată acea copie. Suprascrieți metoda doar când există ceva de pornit: `can_setup` (adevărat când `setup` este suprascris) decide dacă `setup` o rulează sau spune că nu este nimic de schimbat; o clasă care servește mai multe jocuri suprascrie `can_setup` pentru cele pe care nu le poate configura (`RallyAdapter` pentru Richard Burns Rally). |
| `start(self, ctx)` | când apare procesul jocului (adaptoarele mereu pornite: când pornește `run`) | deschide socketurile, găsește fișierele, ține minte de unde să înceapă |
| `poll(self, ctx)` | la fiecare `interval` secunde, în firul propriu al adaptorului | ia ce a spus jocul de la ultima citire și îl înregistrează |
| `stop(self, ctx)` | când jocul a dispărut sau watcher-ul se oprește | închide sesiunile și socketurile |

Fiecare adaptor rulează în firul său (`Runner`). O excepție în `poll` este înregistrată în jurnal, iar adaptorul
așteaptă `min(5, interval × 10 + 0.5)` secunde înainte de următoarea citire. După 20 de eșecuri la rând, sau un
eșec în `start`, adaptorul este oprit și nu mai pornește până când se schimbă id-ul procesului jocului. `missing()`
este verificat la fiecare scanare, deci păstrați-l ieftin.

Un obiect adaptor este refolosit când jocul său pornește din nou, deci `start` trebuie să reseteze tot ce a lăsat în
urmă o rulare anterioară.

### Înregistrarea {#registering-it}

Puneți modulul în `heat3d_watch/adapters/` și enumerați adaptoarele la sfârșitul lui:

```python
ADAPTERS = [MyAdapter(id="mygame", game="My Game", ...)]
```

`adapters.load()` importă fiecare modul din pachet (cu excepția lui `base` și a numelor care încep cu `_`) și adună
`ADAPTERS` lor. Doi adaptori cu același id opresc încărcarea cu o `ValueError`. Un modul care nu poate fi importat
(o dependență lipsă) lasă afară jocurile sale și este numit de `games` împreună cu eroarea, așa că problema unui joc
nu oprește celelalte.

## Context și sesiune {#context-and-session}

`start`, `poll`, `stop` și `setup` primesc un `Context`:

| Membru | Ce este |
|---|---|
| `settings` | `Settings` ([Instalare și rulare](installing-and-running.md#settings)) |
| `data` | dosarul de date |
| `pid`, `exe` | id-ul procesului jocului și calea executabilului, când adaptorul a fost pornit pentru un joc care rulează; dosarul de instalare este lângă `exe` |
| `open(adapter, *, game=None, when=None, axes=..., source=..., multiplayer=..., meta=..., geo=None)` | o sesiune nouă. `game` înlocuiește numele jocului al adaptorului (pentru adaptoarele care acoperă multe jocuri); `when` fixează începutul pentru sesiunile care descriu trecutul; `axes`, `source` și `multiplayer` au implicit valorile adaptorului; `meta` este un dicționar scris în `meta.json`; `geo` (`{"lat0": .., "lon0": ..}`, sau setat mai târziu cu `session.geo`) așază o sesiune de hartă plată pe Pământ, în `meta.json` și în subsolul tabelului |
| `close(session)` | încheie o sesiune: tabelul, `heat.raw.parquet`, `meta.json`, rândul său din `watcher.sqlite`. O sesiune fără evenimente și fără elemente brute este ștearsă; una cu doar elemente brute este păstrată (fără tabel, fără rând în baza de date). Acceptă `None`. Întoarce calea tabelului sau `None`. |

Un `Session` înregistrează:

| Membru | Ce face |
|---|---|
| `event(name, *, t=None, ms=None, x=None, y=None, z=None, player=None, team=None, session=None, **attrs)` | un rând. `t` implicit sunt secundele de la începutul sesiunii, `ms` implicit este acum. O poziție contează doar când `x`, `y` și `z` sunt toate date și finite. Atributele `None` sunt lăsate afară. |
| `position(x, y, z, **kw)` | un eveniment numit `position` |
| `raw(type, payload=None, *, text=None, used=False, t=None, ms=None, **fields)` | păstrează un lucru trimis de sursă, întreg: octeții unui pachet sau ai unei pagini (`payload`), o linie sau un răspuns JSON așa cum a venit (`text`), sau valorile unei citiri după nume (`fields`, fiecare cu propria coloană). `type` este cuvântul sursei pentru el (id-ul unui pachet, numele unei mapări, un eveniment din jurnal, un punct final); `used` spune că a devenit și rânduri. Încadrat în `raw.bin` în clipa apelului, scris ca `heat.raw.parquet` (zstd) când sesiunea se închide sau este recuperată, și numărat pe `type` în `selfCheck.completeness` din `meta.json` |
| `stat(key, value, how="set")` | o statistică: o setați (`set`), o adunați (`add`) sau păstrați maximul (`max`) ori minimul (`min`) |
| `now()` | secundele de la începutul sesiunii |
| `meta` | un dicționar scris în `meta.json` |
| `started`, `ended`, `folder`, `id`, `counts`, `positions` | când, unde și ce s-a înregistrat până acum |

`event`, `stat` și `raw` sunt sigure pentru fire de execuție și pot fi apelate dintr-un fir de lucru.

**Fiecare adaptor păstrează tot ce trimite sursa.** Rândurile sunt ceea ce desenează vizualizatorul; ele nu sunt
înregistrarea. Fiecare pachet care ajunge la un port, fiecare pagină de memorie partajată citită (toată maparea, de
fiecare dată când se schimbă), fiecare linie a unui script de jurnal sau de export (și pe cele pe care adaptorul le
ignoră), fiecare răspuns JSON sau document trimis merg la `session.raw(...)` pe măsură ce sosesc, indiferent dacă
devin sau nu un rând - și nimic nu este rărit sub rata la care citește adaptorul. Un element care sosește înainte ca
o sesiune să fie deschisă deschide una (o sesiune cu doar elemente brute este păstrată), sau este reținut până se
deschide una; nu se pierde niciodată. Câmpurile care sunt ieftin de decodat și sigure ca înțeles merg și în rânduri.
Aceasta este [regula de convertor](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md) a 3DHeat: un
flux live dispare în clipa în care este trimis, deci ce nu păstrează un adaptor se pierde definitiv, iar ce păstrează
întreg poate fi decodat în ziua în care cineva îl înțelege. Dimensiunea este prețul; codarea zstd și cea cu dicționar
o țin mică, fără a lăsa lucruri pe din afară. Testul fiecărui adaptor trimite ceva ce nu folosește și verifică dacă
se întoarce întreg din `heat.raw.parquet`, iar `selfCheck.completeness.lost` este 0. `racing.Driving.raw` face același
lucru pentru adaptoarele de curse (și deschide sesiunea), iar `racing.Pages` păstrează paginile de memorie partajată
ori de câte ori li se schimbă octeții, numărând recitirile care nu au găsit nimic nou în `unchanged_reads` din
`meta.json`.

Convenții de care depinde restul sistemului:

- **Rândurile proprii ale jucătorului sunt marcate, după ce spune sursa.** `player="me"` unde sursa este a
  jucătorului; unde fiecare jucător este înregistrat sub un nume, `own_car=1` pe rândurile mașinii jucătorului (după
  indexul jucătorului în joc sau participantul văzut), ori numele jucătorului ca `session.meta["player"]` (scris în
  `meta.json` imediat) când sursa numește jucătorul. Nu ghiciți niciodată: unde sursa nu spune, luați numele dintr-o
  setare (`player_names`, `riot_id`) sau nu marcați nimic. [Evidențele NVIDIA](nvidia-highlights.md) împrumută
  poziții doar din astfel de rânduri (`platform.own_row`). Ceilalți jucători sunt identificați după nume sau id.
- **Rutele sunt delimitate de evenimente cu poziții**: `spawn`, `respawn` și `session_start` încep una; `death`,
  `finish`, `session_end` și `teleport` o încheie. Ori de câte ori jucătorul s-a mutat fără să parcurgă drumul (o
  resetare, un rewind, o călătorie rapidă, un salvat încărcat), scrieți `teleport` în locul părăsit și apoi un început
  (`spawn`, sau `respawn` pentru o resetare pe care o numește jocul) în locul sosit, ca harta termică pe linii
  („Line heat”) a vizualizatorului să încheie o rută și să înceapă următoarea, în loc să deseneze peste hartă.
  `Driving.jumped` face asta pentru vehicule.
- **Pozițiile rămân în coordonatele și unitățile lumii proprii jocului**, descrise de `axes`. Nu le convertiți într-un
  alt sistem decât dacă jocul nu dă niciun sistem de lume utilizabil (simulatoarele de zbor pun latitudinea și
  longitudinea într-o hartă plată, `Tangent`, în jurul primului punct fix - DCS în jurul originii fixe a teatrului său -
  și transmit `geo=tangent.geo()` către `open`, ca subsolul să spună unde pe Pământ se află harta). `axes.scale` este
  scara de unități a vizualizatorului - înmulțește fiecare poziție cu ea - și rămâne 1, ca rândurile să se potrivească
  cu un nivel exportat din același joc în aceleași unități; spuneți unitatea în `axes.units`.
- **Cheile statisticilor** sunt cu litere mici și cu liniuțe de subliniere și poartă unitatea lor acolo unde se
  aplică (`distance_km`, `top_speed_kmh`, `max_altitude_m`, `duration_s`). Un timp păstrat ca cel mai bun începe cu
  `best_` (păstrat cu `min`), un loc se termină în `_position`: `stats` arată cea mai mică dintre acestea ca cea mai
  bună, iar cea mai mare pentru toate celelalte chei (`db.lower_is_better`).

## Funcții ajutătoare {#helpers}

| Funcție | Modul | Pentru |
|---|---|---|
| `Follower(find, since, stamp=None)`, `game_started(pid)`, `newest(paths)`, `read_shared(path)`, `steam_libraries()` | `_logfollow` | urmărirea unui jurnal scris de joc: citiri partajate, doar liniile acestei sesiuni, fișiere noi și înlocuite, doar linii întregi |
| `UdpPort(port, forward=None, grace=0.0, recheck=3.0)` cu `try_open(who)`, `receive()`, `close()` | `racing` | un port UDP de telemetrie pe 127.0.0.1, luat doar când este liber, predat altui program, transmis opțional mai departe |
| `Driving(adapter, ctx, hz=10.0, jump=50.0)` cu `sample(...)`, `event(...)`, `lap(...)`, `count(...)`, `close()` | `racing` | sesiuni de vehicule: poziții la o rată fixă, distanță, viteză maximă, tururi; la un salt, `teleport` unde era mașina și `spawn` unde este (`jumped(...)`) |
| `SharedView.open(name)` | `simracing_shm` | memoria partajată cu nume a unui joc, doar în citire, niciodată creată |
| `ReplayAdapter` (`patterns`, `folders(ctx)`, `convert(path, ctx)`) | `replays` | un dosar de replay-uri urmărit: fișierele se convertesc când încetează să mai crească, într-un fir de lucru; prima privire doar notează ce este acolo, iar `convert_existing(ctx, folder=None)` - comanda [`replays`](commands.md#replays) - le convertește la cerere |
| `load_state`, `save_state` | `platform` | ținerea minte a ce a văzut un adaptor mereu pornit, în `<data>\state\<id>.json` |
| `FlightLog`, `Tangent` | `xplane` | evidența zborurilor (decolări, aterizări, prăbușiri, distanță) și harta plată în jurul primului punct fix (`Tangent.geo()` este `geo` sesiunii) |
| `backup_once(path)` | `gsi`, `racing` | regula `<file>.heat3d-backup` |
| fișierele Steam | `_steam` | KeyValues binare și text, dosarul Steam din registru |

Un adaptor minimal pentru jurnal, ca exemplu (un joc inventat):

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

Deschideți sesiunea cu primul lucru care merită înregistrat, nu în `start`, ca un joc lăsat în meniuri să nu lase
nimic în urmă (oricum, o sesiune goală este ștearsă).

## Teste {#tests}

```bash
python -m pytest
```

`tests/conftest.py` dă fiecărui test un dosar de date de unică folosință (`HEAT3D_WATCH_HOME`) și oprește verificările
de actualizare și notificările (`HEAT3D_NO_UPDATE`, `HEAT3D_NO_TOAST`). Un test de adaptor construiește ieșirea
jocului din formatul său publicat - pachete din specificație, linii de jurnal în formatul jocului, fișiere în structura
documentată - și conduce adaptorul direct (scurtat din `tests/test_poe.py`; `data` și `install` sunt dosare temporare):

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

Adaptoarele de rețea se testează cu un server local fals sau cu pachete trimise prin UDP către adaptor. Testele care
verifică date reale de joc de pe calculatorul dezvoltatorului sunt marcate cu `@pytest.mark.local` și sunt sărite
acolo unde lipsesc acele date. Aceste date nu intră niciodată în depozit. `test_core.py` conține și testul care
eșuează dacă apare în pachet vreun cod care ar putea scrie în alt proces (`test_memory_reading_cannot_write`).

## Un `verified` onest {#an-honest-verified}

`verified` spune ce a fost verificat și cum, și ce nu. Este afișat de `games` și pe fiecare pagină de joc, iar
jucătorii se bazează pe el. Exemple din cod:

- testat pe pachete în formatele din 2023, 2024 și 2025, construite după specificația publicată de EA, trimise prin
  UDP; netestat pe joc
- testat pe documente în formatul GSI publicat, trimise adaptorului care rulează; netestat pe jocul care rulează
- testat pe fișiere reale de statistici și scheme dintr-o instalare locală; detectarea schimbărilor testată pe fișiere
  construite în formatul binar KeyValues

Spuneți "untested against the game" până când adaptorul a înregistrat jocul care rulează. Scrieți doar metoda și
toleranța: niciodată o hartă, un id de meci, un nume de jucător, o dată, dimensiunea unui corpus sau un număr exact
din fișiere reale și niciodată "this machine" (cititorii nu îl cunosc). Numiți sursa fiecărui decalaj și fiecărei
structuri și spuneți unde au fost comparate două surse. Nu pretindeți niciodată mai mult decât s-a făcut. Un format
ghicit sau luat din instrumente ale comunității se spune că este exact asta.

## Paginile jocurilor {#the-game-pages}

Fiecare pagină de sub [Jocuri](games.md) este generată din adaptoare, deci se potrivește mereu cu codul. După ce
adăugați sau schimbați un adaptor, regenerați-le din dosarul depozitului:

```bash
HEAT3D_NO_UPDATE=1 python tools/gen_game_pages.py
```

(În PowerShell: `$env:HEAT3D_NO_UPDATE = "1"; python tools/gen_game_pages.py`.) Adăugați `--check` ca să doar
comparați: nu scrie nimic și iese cu codul 1 când o pagină este învechită (la fel și tabelul de jocuri din
`docs/watcher.md`).

Scriptul:

- încarcă adaptoarele cu `heat3d_watch.adapters.load()`, pe un dosar de date temporar gol, ca niciun profil de
  memorie sau nicio setare de pe calculatorul dumneavoastră să nu ajungă în pagini. Adaptoarele de memorie sunt lăsate
  afară, întrucât vin din profilurile proprii ale jucătorilor;
- refuză să scrie ceva dacă un modul de adaptor nu poate fi importat (paginile ar pierde acele jocuri);
- scrie `docs/game-<adapter id>.md` pentru fiecare adaptor și `docs/games.md` cu tabelul de prezentare generală, și
  șterge paginile adaptoarelor care nu mai există;
- ia "What is recorded", "Where it comes from", "How to switch it on", axele, indicatorul multiplayer și "Verified"
  din câmpurile adaptorului;
- transformă docstring-ul modulului în "How it works". Scrieți docstring-urile în stilul text simplu pe care îl
  folosesc deja modulele, pe care scriptul îl convertește: paragrafe; liste cu `*`, `-` sau `1.`; machetele și
  exemplele indentate sub rândul care le introduce (devin blocuri de cod); un titlu subliniat cu liniuțe, sau un rând
  scurt de titlu cu textul indentat direct sub el (devin titluri);
- listează cheile statisticilor pe care codul adaptorului le setează pe nume - `.stat("key", ...)`, ambele ramuri ale
  unei expresii `if` și modelele f-string precum `score.{team}` - în clasele adaptorului și în funcțiile ajutătoare pe
  care le folosesc. Cheile luate dintr-o variabilă (un tabel cu câmpurile jocului) nu sunt listate;
- decide "Positions" după `axes.units` al adaptorului (o notă care începe cu "no" sau "none" înseamnă fără poziții) și
  după ce scrie codul său.

Nu editați de mână paginile generate: schimbați adaptorul și rulați din nou scriptul. Tabelul din
[Toate jocurile într-un tabel](watcher.md) este rezultatul comenzii `python -m heat3d_watch games --markdown`.
