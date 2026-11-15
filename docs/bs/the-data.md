---
title: "Podaci"
nav_order: 5
lang: "bs"
source: the-data.md
source_hash: "6150cdc022fc"
nav_exclude: true
search_exclude: true
---
# Podaci {#the-data}

Svi snimci su obične datoteke u folderu s podacima (`%LOCALAPPDATA%\3DHeat\Watcher` osim ako nije promijenjeno,
vidite [Instalacija i pokretanje](installing-and-running.md#where-everything-is)). Možete ih čitati, kopirati ili
brisati bez watchera. Datoteka `.jsonl` je običan tekst, jedan događaj u liniji (otvara je Notepad);
datoteka `.parquet` je tabela koju otvara preglednik 3DHeat (Excel ne - `stats --csv` piše CSV
datoteke za tabelarne programe).

## Folderi sesija {#session-folders}
![folder sesije](../assets/img/session-folder.svg)


**Sesija** je jedno sjedenje s jednim izvorom: od trenutka kad igra prvi put nešto kaže dok se
ne zaustavi (igra se zatvori, meč završi, vožnja ili let se resetira - stranica svakog adaptera kaže šta
počinje i završava njegove sesije). Svaka sesija dobija folder:

```text
<data>\sessions\<game>\<YYYY-MM-DD_HH-MM-SS>_<adapter id>\
    events.jsonl
    heat.parquet
    meta.json
```

- `<game>` je naziv igre u kojem je svaki znak osim slova, cifara, `.`, `_` i `-`
  zamijenjen s `-` (najviše 60 znakova): `EA-SPORTS-F1-25`, `Counter-Strike-2`. Adapteri koji pokrivaju
  mnogo igara (Steam statistika, Steam Timeline, NVIDIA highlighti) svrstavaju svaku sesiju pod igru kojoj
  pripada.
- Vrijeme je početak sesije u lokalnom vremenu. Sesije koje opisuju prošlost (snimak pretvoren
  poslije meča, Steam datoteka statistike) koriste vrijeme koje daje igra ili datoteka. Dvije sesije koje počinju u
  istoj sekundi dobijaju dodano `_2`, `_3`, ...
- Id sesije, u bazi statistika, je `<game folder>/<session folder>`.

Sesija u kojoj ništa uopće nije snimljeno (igra je stajala u menijima ili se srušila na početku) se
briše kad se zatvori, da svako pokretanje ne ostavlja prazan folder.

Neke sesije drže više datoteka. Sesija Counter-Strike 2 demoa drži konverterovu vlastitu tabelu i
sažetak (`<map>/<match>.parquet`, `<match>.match.json`). Sesija iRacinga navodi `.ibt` datoteke koje je
simulator napisao tokom sjedenja kao događaje `telemetry_file`.

## events.jsonl {#eventsjsonl}

`events.jsonl` ima jedan JSON objekt po liniji, jednu liniju po događaju, upisanu u trenutku kad se događaj
desi. Datoteka je baferirana po linijama, pa rušenje, nestanak struje ili ubijen proces ne gubi ništa što je
već upisano; linija prekinuta rušenjem preskače se pri čitanju datoteke, a svaka linija prije nje
ostaje.

Svaka linija ima iste osnovne kolone:

| Kolona | Tip | Šta je to |
|---|---|---|
| `time` | broj | sekunde od početka sesije (4 decimale), ili igrin vlastiti sat gdje ga adapter prosljeđuje |
| `ms` | cijeli broj | vrijeme zida (wall-clock), Unix milisekunde |
| `event` | tekst | šta se desilo: `position`, `spawn`, `death`, `kill`, `lap`, `teleport`, `session_start`, ... |
| `x`, `y`, `z` | broj | gdje, u igrinim vlastitim jedinicama i osama (vidite `axes` u `meta.json`); prisutno samo kad su sva tri poznata i konačna |
| `player` | tekst | ko: ime, id, ili `me` za osobu koja igra (vidite [Igračevi vlastiti redovi](#the-players-own-rows)) |
| `team` | tekst | njegova strana, kad igra kaže |
| `session` | tekst | meč, runda, etapa, život ili let kojem red pripada, kad igra kaže |

Svako drugo polje koje igra prijavi slijedi pod vlastitim imenom (`speed_kmh`, `gear`, `lap_time`, `weapon`,
`victim`, `hero`, ...). Polja bez vrijednosti se izostavljaju, a isto i brojevi koji nisu konačni.
Dvije sintetičke linije:

```json
{"time":12.3456,"ms":1777660501123,"event":"position","x":-412.5,"y":12.1,"z":233.0,"player":"me","session":"1","speed_kmh":187.4,"gear":5}
{"time":15.0,"ms":1777660503667,"event":"lap","x":-380.2,"y":12.0,"z":250.9,"player":"me","session":"1","lap_time":92.418,"lap":3}
```

Redovi bez pozicije (linija kill feeda, podizanje nivoa, promjena statistike) ostaju u `events.jsonl` i računaju se
u statistici. Samo redovi s pozicijom idu u tabelu.

### Igračevi vlastiti redovi {#the-players-own-rows}

Koji su redovi osobe koja igra, kaže izvor, nikad se ne pogađa. Red je igračev vlastiti kad

- je njegov `player` `me`: većina adaptera, čiji je izvor igračeva vlastita igra (telemetrija vlastitog
  automobila ili letjelice, game-state integracija, dnevnik);
- nosi `own_car` 1: trkaće igre koje snimaju svaki automobil pod imenom njegovog vozača (EA SPORTS F1
  po indeksu igračevog automobila u igri, RaceRoom po svom slotu, Automobilista 2 i Project CARS 2 po
  posmatranom učesniku) tako označavaju igračev automobil i drže vozačevo ime u `player`;
- je njegov `player` jednak `player` sesije u `meta.json`: ime koje izvor daje igraču - komandant Elite
  Dangerousa (dnevnik je uvijek igračev), linija Riot ID-a iz postavki u League of Legends snimku.

War Thunder i Rocket League imenuju svakog igrača i ne kažu koji ste vi; s vašim imenom u postavci
`player_names` (vidite [Postavke](installing-and-running.md#settings)) vaši redovi postaju `me`.
[NVIDIA highlighti](nvidia-highlights.md) traže trenutak upravo u ovim redovima.

## heat.parquet {#heatparquet}

Kad se sesija zatvori, redovi iz `events.jsonl` koji imaju `x`, `y` i `z` upisuju se u
`heat.parquet`. To je tabela koju otvara preglednik 3DHeat. Ako sesija nema pozicija, tabela
se ne piše.

- Kolone su `time`, `ms`, `event`, `x`, `y`, `z`, `player`, `team`, `session`, a zatim svako
  drugo polje redoslijedom kojim se prvi put pojavi.
- `x`, `y`, `z` i `time` su 64-bitni decimalni brojevi, a `ms` je 64-bitni cijeli broj. Dodatna kolona čije
  su vrijednosti svi brojevi je 64-bitni decimalni broj; svaka druga kolona je tekst kodiran rječnikom (nedostajuće vrijednosti
  su prazan tekst, a liste ili objekti upisuju se kao JSON tekst).
- Metapodaci datoteke imaju ključ `heat3d` s uputama za čitanje, pa preglednik sam mapira kolone
  i ose (primjer, sa skraćenom listom `extra`):

```json
{
  "version": 1,
  "kind": "heat3d-watch",
  "game": "EA SPORTS F1 25",
  "axes": {"up": "y", "flipX": false, "flipY": false, "flipZ": false, "scale": 1.0},
  "columns": {
    "x": "x", "y": "y", "z": "z",
    "time": "time", "timeUnit": "seconds",
    "personId": "player", "teamId": "team", "sessionId": "session",
    "extra": ["event", "speed_kmh", "gear", "lap_time", "lap"]
  }
}
```

`up` je uzdužna osa igre, `flipX`/`flipY`/`flipZ` zrcale osu da lijevi svijet ne bude nacrtan
zrcaljeno, a `scale` je skala jedinice preglednika: preglednik množi svaku poziciju njome kad
učitava tabelu (0.01 bi pretvorilo centimetre u metre). Svaki adapter piše 1 i zadržava igrine
vlastite jedinice - metre za većinu, Source jedinice (inči) za Counter-Strike 2, Unreal jedinice (centimetri) za
Rocket League - jer je nivo izvezen iz igre u istim tim jedinicama, pa redovi sjednu na njega;
isto kažu i tabele CS2 konvertera. `units` u `meta.json` kaže šta je jedna jedinica. Stranica svake igre
navodi njene vrijednosti pod "Positions and axes".

Simulatori leta (DCS World, Microsoft Flight Simulator, X-Plane, Tacview snimci iz IL-2) stavljaju svoje
redove na Zemlju, a njihovo podnožje kaže gdje, pa preglednik može podmetnuti pravi svijet ispod njih:

```json
"geo": {"lat0": 42.0, "lon0": 42.0, "projection": "tangent-plane", "east": "x", "north": "z", "up": "y"}
```

`lat0`/`lon0` (stepeni) su ishodište ravne mape u kojoj su redovi; `east`, `north` i `up` imenuju
kolone koje drže metre istočno i sjeverno od njega i visinu iznad mora. Ishodište je
prva tačka za X-Plane i MSFS, referentna tačka snimka za IL-2, a stalno ishodište teatra
za DCS (prva tačka zaokružena na cijele stepene na teatru koji watcher ne poznaje). Tabela bez
mjesta na Zemlji nema ključ `geo`, a sve ostalo u podnožju je isto u oba slučaja.

`heat.parquet` se uvijek može ponovo napraviti iz `events.jsonl` s
`python -m heat3d_watch table <session folder>` (vidite [Komande](commands.md#table)). Ovo je korisno kad je
`pyarrow` nedostajao dok je sesija snimana.

## meta.json {#metajson}

`meta.json` sažima sesiju. Piše se kad se sesija otvori, najviše svakih 30 sekundi dok
stižu događaji ili statistike, i kad se sesija zatvori. Statistike se između tih upisa drže samo u memoriji,
pa rušenje može izgubiti najviše zadnjih pola minute njih.

```json
{
  "format": "heat3d-watch-session",
  "version": 1,
  "watcher": "1.0.2",
  "game": "EA SPORTS F1 25",
  "adapter": "f1-25",
  "source": "UDP telemetry 127.0.0.1:20777 (...)",
  "multiplayer": true,
  "started": "2026-05-01T20:15:03",
  "ended": "2026-05-01T21:02:11",
  "seconds": 2828.0,
  "axes": {"up": "y", "flip_x": false, "flip_y": false, "flip_z": false, "scale": 1.0, "units": "metres"},
  "events": {"position": 52110, "lap": 412, "teleport": 3},
  "positions": 52530,
  "stats": {"laps": 20, "best_lap": 91.874, "distance_km": 106.3, "race_position": 4},
  "track": "..."
}
```

Sesija čiji izvor imenuje igrača (vidite [Igračevi vlastiti redovi](#the-players-own-rows)) ima i
`"player"`: ime koje nose igračevi vlastiti redovi. Sesija na Zemlji (simulatori leta) ima i
`"geo": {"lat0": .., "lon0": ..}`, ishodište koje ponavlja `geo` njenog podnožja.

- `started` / `ended`: lokalno vrijeme do sekunde; `ended` je `null` dok sesija traje.
- `events`: koliko se puta desio svaki događaj, najčešći prvi. `positions` je broj redova
  s pozicijom.
- `stats`: brojevi sesije. Adapter svaki postavlja, dodaje mu, ili zadržava najveći ili najmanji.
- Sve ostalo što adapter zna o sjedenju slijedi na vrhu: staza, mapa, misija,
  id meča, Steam app id, datoteka snimka, memorijski profil i verzija. Sesija zatvorena
  oporavkom ima `"recovered": true`.

## watcher.sqlite {#watchersqlite}

`watcher.sqlite` je baza statistika. Red se dodaje za svaku sesiju kad se zatvori. Tri
tabele su jednostavne, pa ih svaki SQL alat, bilježnica ili tabelarni program može čitati bez watchera:

```sql
CREATE TABLE sessions (
  id TEXT PRIMARY KEY,          -- <game folder>/<session folder>
  game TEXT NOT NULL,
  adapter TEXT NOT NULL,
  started REAL NOT NULL,        -- Unix seconds
  ended REAL,                   -- Unix seconds
  seconds REAL,
  folder TEXT NOT NULL,         -- the session folder's full path
  events INTEGER NOT NULL DEFAULT 0,
  positions INTEGER NOT NULL DEFAULT 0,
  multiplayer INTEGER NOT NULL DEFAULT 0,
  source TEXT
);
CREATE TABLE events (           -- per session, how many times each event happened
  session TEXT NOT NULL REFERENCES sessions(id) ON DELETE CASCADE,
  event TEXT NOT NULL,
  count INTEGER NOT NULL,
  PRIMARY KEY (session, event)
);
CREATE TABLE stats (            -- per session, every number the game reported or the watcher counted
  session TEXT NOT NULL REFERENCES sessions(id) ON DELETE CASCADE,
  key TEXT NOT NULL,
  value REAL,                   -- numbers
  text TEXT,                    -- everything else (a map name, a result, a hero)
  PRIMARY KEY (session, key)
);
```

Ponovno snimanje sesije (oporavak, ponovo pretvoren snimak) zamjenjuje njene redove. `multiplayer` je
adapterova zastavica (neki adapteri je postavljaju po sesiji, na primjer DCS iz misije), a ne provjera
jeste li bili online. Vrijednost da/ne u `stats` pohranjuje se kao tekst.

Primjer upita, najbolji krug po igri preko svih sesija (niže je bolje):

```sql
SELECT s.game, MIN(t.value) AS best_lap
FROM stats t JOIN sessions s ON s.id = t.session
WHERE t.key = 'best_lap'
GROUP BY s.game;
```

`python -m heat3d_watch stats` ispisuje zbirove iz ovih tabela (vidite [Komande](commands.md#stats)); njegova
kolona `best` je najniža vrijednost za vremena koja se čuvaju kao najbolja i za mjesta, a najviša za ostalo.

## Oporavak poslije rušenja {#recovery-after-a-crash}

Kad se `run` pokrene, traži sesije koje je raniji watcher ostavio otvorenim: `meta.json` bez
`ended` i `events.jsonl` s barem jednom linijom. Svaku zatvara:

- brojevi događaja i broj pozicija ponovo se broje iz `events.jsonl`, preskačući prekinutu
  liniju;
- kraj je vrijeme zida zadnje linije (`ms`);
- statistike su one iz zadnjeg upisa `meta.json` (stare najviše 30 sekundi);
- dodaje se `"recovered": true`, piše se `heat.parquet`, a sesija ide u `watcher.sqlite`.

Log kaže "finished N session(s) left open by an earlier run". Lock datoteka sprječava da drugi
watcher "oporavlja" sesije onog koji još radi.

## CSV izvoz {#csv-export}
![stats --csv i table](../assets/img/csv-and-table.svg)


```bash
python -m heat3d_watch stats --csv out
```

piše `out\sessions.csv`, `out\events.csv` i `out\stats.csv`. Svaka datoteka je jedna tabela iz
`watcher.sqlite`, kompletna, sa zaglavljem, kao UTF-8. Vremena su Unix sekunde kao u bazi.
`--game` ne sužava izvoz; upisuje se svaka sesija.

## Otvaranje sesije u pregledniku 3DHeat {#opening-a-session-in-the-3dheat-viewer}

Preglednik: [github.com/Holdi601/3DHeat](https://github.com/Holdi601/3DHeat), dokumentacija
[holdi601.github.io/3DHeat](https://holdi601.github.io/3DHeat/) - njegova stranica
[`.3dheat` spremnika](https://holdi601.github.io/3DHeat/container.html) opisuje format jedna datoteka
po meču koji konverteri snimaka mogu pisati.

Otvorite `heat.parquet` sesije u pregledniku 3DHeat. Podnožje govori pregledniku koja kolona je
pozicija, vrijeme, igrač, tim i sesija, i na koju stranu je gore, pa se ništa ne mora
mapirati ručno. Pozicije su u igrinim vlastitim koordinatama svijeta. Nacrtane preko nivoa izvezenog
drugim 3DHeat alatima (na primjer iz [3DHeat GameFiles](https://github.com/Holdi601/3DHeat-GameFiles)),
sjedaju tamo gdje su se desile.

- **Toplotne mape** koriste svaki red s pozicijom, filtriran po `event`, `player`, `team` ili `session` kao i svaka
  druga kolona.
- **Linijska toplota** crta liniju od svakog igračevog reda do njegovog sljedećeg, a pri reprodukciji je svaki
  igrač tačka koja se kreće duž rute s repom iza sebe. Panel Rute u pregledniku bira,
  iz kolone `event`, koji događaji **počinju** rutu, a koji je **završavaju**. Watcher piše
  omeđujuće događaje kao redove s pozicijom, pa se mogu birati tamo:
  - počeci: `spawn`, `respawn`, `session_start`. Početak zatvara rutu koja je bila otvorena bez
    crtanja linije do novog mjesta.
  - krajevi: `death`, `finish`, `session_end` i `teleport`. Linija ide sve do samog završnog reda,
    a to je mjesto gdje je igrač poginuo, stao ili bio odveden.

  Skok - mjesto do kojeg se stiglo bez putovanja - su dva reda: `teleport` na mjestu koje je **napušteno**,
  i početak na mjestu na koje se **stiglo**, odmah poslije njega. Trkaći adapteri pišu jedan kad god je
  automobil prešao dalje nego što je mogao voziti (premotavanje ili flashback, reset na cestu, povratak u
  boks, brzo putovanje), sa `spawn` na odredištu (`respawn` za BeamNG-ov reset); red `teleport`
  nosi odredište kao `to_x`, `to_y`, `to_z` i udaljenost kao `metres`, a početni red
  `after: "teleport"`. Adapteri za kamione rade isto za trajekt, voz ili učitano spremanje, a
  adapteri za letove za skok koji nijedna letjelica ne bi mogla preletjeti. Dakle, kad je `teleport` među krajevima
  a `spawn` među počecima - što preglednik sam predlaže - ruta završava gdje je skok
  napustio, a sljedeća počinje gdje je stigao, i nijedna linija ne prelazi preko mape. Ruta nikad ne ide preko
  promjene kolone `session`. Red pozicije piše se nekoliko puta u sekundi
  (10 Hz za većinu telemetrije), što daje glatku liniju.
- Kolona `session` dijeli sjedenje na runde, etape, živote ili tijela (Elite Dangerous
  tako drži redove galaksije i redove površine svake planete odvojeno). Izaberite jednu u pregledniku da vidite
  samo taj dio.

Šta preglednik radi s redovima - filteri, boje, reprodukcija - opisano je u vlastitoj dokumentaciji
preglednika. Sesije Counter-Strike 2 demoa otvaraju se preko konverterovih `<map>/<match>.parquet`
i `<match>.match.json` u tabovima heat i match preglednika. Pozicije iRacinga dolaze iz
`.ibt` datoteka navedenih u sesiji, koje preglednik sam čita.
