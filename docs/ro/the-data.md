---
title: "Datele"
nav_order: 5
lang: "ro"
source: the-data.md
source_hash: "6150cdc022fc"
nav_exclude: true
search_exclude: true
---
# Datele {#the-data}

Toate înregistrările sunt fișiere simple în dosarul de date (`%LOCALAPPDATA%\3DHeat\Watcher`, dacă nu este schimbat, vezi
[Instalare și rulare](installing-and-running.md#where-everything-is)). Le puteți citi, copia sau șterge fără watcher. Un
fișier `.jsonl` este text simplu, câte un eveniment pe rând (îl deschide Notepad); un fișier `.parquet` este un tabel pe
care îl deschide vizualizatorul 3DHeat (Excel nu - `stats --csv` scrie fișiere CSV pentru tabele).

## Dosarele sesiunilor {#session-folders}
![a session folder](../assets/img/session-folder.svg)


O **sesiune** este o ședință cu o singură sursă: din momentul în care jocul spune ceva prima dată până când se oprește
(jocul se închide, un meci se termină, o cursă sau un zbor este resetat - pagina fiecărui adaptor spune ce începe și ce
încheie sesiunile). Fiecare sesiune primește un dosar:

```text
<data>\sessions\<game>\<YYYY-MM-DD_HH-MM-SS>_<adapter id>\
    events.jsonl
    heat.parquet
    meta.json
```

- `<game>` este numele jocului, cu fiecare caracter în afara literelor, cifrelor, `.`, `_` și `-` înlocuit cu `-` (cel
  mult 60 de caractere): `EA-SPORTS-F1-25`, `Counter-Strike-2`. Adaptoarele care acoperă multe jocuri (statisticile Steam,
  Steam Timeline, evidențele NVIDIA) trec fiecare sesiune sub jocul căruia îi aparține.
- Ora este începutul sesiunii, în ora locală. Sesiunile care descriu trecutul (un replay convertit după meci, un fișier de
  statistici Steam) folosesc ora pe care o dă jocul sau fișierul. Două sesiuni care încep în aceeași secundă primesc
  adăugat `_2`, `_3`, ...
- Id-ul sesiunii, în baza de date a statisticilor, este `<dosarul jocului>/<dosarul sesiunii>`.

O sesiune în care nu s-a înregistrat nimic (jocul a stat în meniuri, sau s-a prăbușit la pornire) este ștearsă când se
închide, ca fiecare lansare să nu lase un dosar gol.

Unele sesiuni țin mai multe fișiere. O sesiune de demo Counter-Strike 2 ține tabelul și rezumatul propriu ale
convertorului (`<map>/<match>.parquet`, `<match>.match.json`). O sesiune iRacing listează fișierele `.ibt` pe care le-a
scris simulatorul în timpul ședinței, ca evenimente `telemetry_file`.

## events.jsonl {#eventsjsonl}

`events.jsonl` are câte un obiect JSON pe rând, câte un rând pentru fiecare eveniment, scris în clipa în care se întâmplă
evenimentul. Fișierul este bufferizat pe rând, deci o prăbușire, o pană de curent sau un proces oprit forțat nu pierde
nimic din ce a fost deja scris; un rând întrerupt de o prăbușire este sărit când fișierul este citit, iar fiecare rând
dinaintea lui rămâne.

Fiecare rând are aceleași coloane de bază:

| Coloană | Tip | Ce este |
|---|---|---|
| `time` | număr | secundele de la începutul sesiunii (4 zecimale), sau ceasul propriu al jocului, acolo unde adaptorul îl trimite |
| `ms` | întreg | ora calendaristică, în milisecunde Unix |
| `event` | text | ce s-a întâmplat: `position`, `spawn`, `death`, `kill`, `lap`, `teleport`, `session_start`, ... |
| `x`, `y`, `z` | număr | unde, în unitățile și axele jocului (vezi `axes` în `meta.json`); prezente doar când toate trei sunt cunoscute și finite |
| `player` | text | cine: un nume, un id, sau `me` pentru persoana care joacă (vezi [Rândurile proprii ale jucătorului](#the-players-own-rows)) |
| `team` | text | tabăra lor, când o spune jocul |
| `session` | text | meciul, runda, etapa, viața sau zborul căruia îi aparține rândul, când o spune jocul |

Orice alt câmp pe care îl raportează jocul urmează sub numele său (`speed_kmh`, `gear`, `lap_time`, `weapon`, `victim`,
`hero`, ...). Câmpurile fără valoare sunt lăsate afară, la fel și numerele care nu sunt finite. Două rânduri inventate:

```json
{"time":12.3456,"ms":1777660501123,"event":"position","x":-412.5,"y":12.1,"z":233.0,"player":"me","session":"1","speed_kmh":187.4,"gear":5}
{"time":15.0,"ms":1777660503667,"event":"lap","x":-380.2,"y":12.0,"z":250.9,"player":"me","session":"1","lap_time":92.418,"lap":3}
```

Rândurile fără poziție (o linie din fluxul de eliminări, o creștere de nivel, o schimbare de statistică) rămân în
`events.jsonl` și se numără în statistici. Doar rândurile cu poziție intră în tabel.

### Rândurile proprii ale jucătorului {#the-players-own-rows}

Care rânduri sunt ale persoanei care joacă spune sursa, niciodată nu se ghicește. Un rând este al jucătorului când

- `player` este `me`: majoritatea adaptoarelor, a căror sursă este jocul propriu al jucătorului (telemetria propriei
  mașini sau aeronave, o integrare a stării jocului, un jurnal);
- are `own_car` 1: jocurile de curse care înregistrează fiecare mașină sub numele pilotului (EA SPORTS F1 după indexul
  mașinii jucătorului în joc, RaceRoom după slotul propriu, Automobilista 2 și Project CARS 2 după participantul văzut)
  marchează astfel mașina jucătorului și păstrează numele pilotului în `player`;
- `player` este `player` din `meta.json`: numele pe care îl dă sursa jucătorului - comandantul din Elite Dangerous
  (jurnalul este mereu al jucătorului), rândul unui replay League of Legends al ID-ului Riot din setări.

War Thunder și Rocket League numesc fiecare jucător și nu spun care sunteți dumneavoastră; cu numele dumneavoastră în
setarea `player_names` (vezi [Setări](installing-and-running.md#settings)), rândurile dumneavoastră devin `me`.
[Evidențele NVIDIA](nvidia-highlights.md) caută un moment exact în aceste rânduri.

## heat.parquet {#heatparquet}

Când o sesiune se închide, rândurile din `events.jsonl` care au `x`, `y` și `z` sunt scrise în `heat.parquet`. Acesta este
tabelul pe care îl deschide vizualizatorul 3DHeat. Dacă sesiunea nu are poziții, nu se scrie niciun tabel.

- Coloanele sunt `time`, `ms`, `event`, `x`, `y`, `z`, `player`, `team`, `session`, urmate de fiecare alt câmp în ordinea în
  care apare prima dată.
- `x`, `y`, `z` și `time` sunt numere reale pe 64 de biți, iar `ms` este un întreg pe 64 de biți. O altă coloană ale cărei
  valori sunt toate numere este un număr real pe 64 de biți; orice altă coloană este text codat cu dicționar (valorile
  lipsă sunt text gol, iar listele sau obiectele sunt scrise ca text JSON).
- Metadatele fișierului au o cheie `heat3d` cu instrucțiunile de citire, deci vizualizatorul asociază singur coloanele și
  axele (un exemplu, cu lista `extra` scurtată):

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

`up` este axa „sus” a jocului, `flipX`/`flipY`/`flipZ` oglindesc o axă, ca o lume cu sistem stâng să nu fie desenată
oglindit, iar `scale` este scara de unități a vizualizatorului: vizualizatorul înmulțește fiecare poziție cu ea când
încarcă tabelul (0,01 ar transforma centimetri în metri). Fiecare adaptor scrie 1 și păstrează unitățile proprii jocului -
metri pentru majoritatea, unități Source (inch) pentru Counter-Strike 2, unități Unreal (centimetri) pentru Rocket League -
pentru că un nivel exportat din joc este în aceleași unități, deci rândurile cad pe el; tabelele convertorului CS2 spun
același lucru. `units` din `meta.json` spune ce înseamnă o unitate. Pagina fiecărui joc își listează valorile sub
"Positions and axes".

Simulatoarele de zbor (DCS World, Microsoft Flight Simulator, X-Plane, înregistrările Tacview ale IL-2) își pun rândurile
pe Pământ, iar subsolul lor spune unde, ca vizualizatorul să poată așeza lumea reală sub ele:

```json
"geo": {"lat0": 42.0, "lon0": 42.0, "projection": "tangent-plane", "east": "x", "north": "z", "up": "y"}
```

`lat0`/`lon0` (grade) sunt originea hărții plate în care se află rândurile; `east`, `north` și `up` numesc coloanele care
țin metri est și nord față de ea și altitudinea deasupra nivelului mării. Originea este primul punct fix pentru X-Plane și
MSFS, punctul de referință al înregistrării pentru IL-2, iar originea fixă a teatrului pentru DCS (primul punct fix
rotunjit la grade întregi, pe un teatru pe care watcher-ul nu îl cunoaște). Un tabel fără un loc pe Pământ nu are cheia
`geo`, iar restul subsolului este la fel în ambele cazuri.

`heat.parquet` poate fi mereu refăcut din `events.jsonl` cu `python -m heat3d_watch table <dosarul sesiunii>` (vezi
[Comenzi](commands.md#table)). Asta este util când `pyarrow` lipsea în timpul înregistrării sesiunii.

## meta.json {#metajson}

`meta.json` rezumă sesiunea. Se scrie când sesiunea se deschide, cel mult la fiecare 30 de secunde cât timp intră
evenimente sau statistici, și când sesiunea se închide. Statisticile sunt păstrate doar în memorie între aceste scrieri,
deci o prăbușire poate pierde cel mult ultima jumătate de minut din ele.

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

O sesiune a cărei sursă numește jucătorul (vezi [Rândurile proprii ale jucătorului](#the-players-own-rows)) are și
`"player"`: numele pe care îl poartă rândurile proprii ale jucătorului. O sesiune pe Pământ (simulatoarele de zbor) are și
`"geo": {"lat0": .., "lon0": ..}`, originea pe care o repetă `geo` din subsol.

- `started` / `ended`: ora locală, până la secundă; `ended` este `null` cât timp sesiunea rulează.
- `events`: de câte ori s-a întâmplat fiecare eveniment, cele mai frecvente primele. `positions` este numărul de rânduri cu
  poziție.
- `stats`: cifrele sesiunii. Un adaptor setează fiecare, adună la ea sau păstrează maximul sau minimul.
- Orice altceva știe adaptorul despre ședință urmează la nivelul de sus: pista, harta, misiunea, id-ul meciului, id-ul
  aplicației Steam, fișierul de replay, profilul de memorie și versiunea. O sesiune terminată prin recuperare are
  `"recovered": true`.

## watcher.sqlite {#watchersqlite}

`watcher.sqlite` este baza de date a statisticilor. Un rând se adaugă pentru fiecare sesiune când se închide. Cele trei
tabele sunt simple, deci orice unealtă SQL, caiet sau tabel poate să le citească fără watcher:

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

Înregistrarea din nou a unei sesiuni (recuperare, un replay convertit din nou) îi înlocuiește rândurile. `multiplayer`
este indicatorul adaptorului (unii adaptori îl setează pe sesiune, de exemplu DCS din misiune), nu o verificare dacă ați
fost online. O valoare adevărat/fals din `stats` este păstrată ca text.

Un exemplu de interogare, cel mai bun tur pe joc din toate sesiunile (mai mic este mai bine):

```sql
SELECT s.game, MIN(t.value) AS best_lap
FROM stats t JOIN sessions s ON s.id = t.session
WHERE t.key = 'best_lap'
GROUP BY s.game;
```

`python -m heat3d_watch stats` afișează totaluri din aceste tabele (vezi [Comenzi](commands.md#stats)); coloana sa `best`
este cea mai mică valoare pentru timpii păstrați ca cei mai buni și pentru locuri, cea mai mare pentru restul.

## Recuperarea după o prăbușire {#recovery-after-a-crash}

Când pornește `run`, caută sesiunile pe care un watcher anterior le-a lăsat deschise: un `meta.json` fără `ended` și un
`events.jsonl` cu cel puțin un rând. Termină fiecare dintre ele:

- numărătoarea evenimentelor și numărul pozițiilor se fac din nou din `events.jsonl`, sărind peste un rând întrerupt;
- sfârșitul este ora calendaristică a ultimului rând (`ms`);
- statisticile sunt cele din ultima scriere a `meta.json` (de cel mult 30 de secunde);
- se adaugă `"recovered": true`, se scrie `heat.parquet`, iar sesiunea intră în `watcher.sqlite`.

Jurnalul spune "finished N session(s) left open by an earlier run". Fișierul de blocare împiedică un al doilea watcher să
"recupereze" sesiunile unuia care încă rulează.

## Export CSV {#csv-export}
![stats --csv and table](../assets/img/csv-and-table.svg)


```bash
python -m heat3d_watch stats --csv out
```

scrie `out\sessions.csv`, `out\events.csv` și `out\stats.csv`. Fiecare fișier este un tabel din `watcher.sqlite`, complet,
cu un rând de antet, în UTF-8. Orele sunt secunde Unix, ca în baza de date. `--game` nu restrânge exportul; fiecare
sesiune este scrisă.

## Deschiderea unei sesiuni în vizualizatorul 3DHeat {#opening-a-session-in-the-3dheat-viewer}

Vizualizatorul: [github.com/Holdi601/3DHeat](https://github.com/Holdi601/3DHeat), documentația
[holdi601.github.io/3DHeat](https://holdi601.github.io/3DHeat/) - pagina sa
[containerul `.3dheat`](https://holdi601.github.io/3DHeat/container.html) descrie formatul cu un fișier pentru fiecare
meci, pe care îl pot scrie convertoarele de replay.

Deschideți `heat.parquet` al unei sesiuni în vizualizatorul 3DHeat. Subsolul îi spune vizualizatorului ce coloană este
poziția, ora, jucătorul, tabăra și sesiunea, și care este sus, deci nu trebuie asociat nimic de mână. Pozițiile sunt în
coordonatele lumii proprii jocului. Desenate peste un nivel exportat cu celelalte unelte 3DHeat (de exemplu din
[3DHeat GameFiles](https://github.com/Holdi601/3DHeat-GameFiles)), ajung unde s-au întâmplat.

- **Hărțile termice** folosesc fiecare rând cu poziție, filtrat după `event`, `player`, `team` sau `session`, ca orice
  altă coloană.
- **Harta termică pe linii** („Line heat”) desenează o linie de la fiecare rând al unui jucător până la următorul, iar la
  redare fiecare jucător este un punct care se mișcă de-a lungul rutei, cu o coadă în urmă. Panoul de **Rute** al
  vizualizatorului alege, după coloana `event`, care evenimente **încep** o rută și care o **încheie**. Watcher-ul scrie
  evenimentele de delimitare ca rânduri cu poziție, ca să poată fi alese acolo:
  - încep: `spawn`, `respawn`, `session_start`. Un început închide ruta care era deschisă, fără să deseneze o linie spre
    locul nou.
  - încheie: `death`, `finish`, `session_end` și `teleport`. Linia merge până la chiar rândul de sfârșit, adică acolo unde
    jucătorul a murit, s-a oprit sau a fost luat.

  Un salt - un loc atins fără să se fi mers până acolo - sunt două rânduri: `teleport` în locul **părăsit**, și un început
  în locul **sosit**, imediat după el. Adaptoarele de curse scriu unul ori de câte ori mașina s-a mutat mai departe decât ar
  fi putut conduce (un rewind sau flashback, o resetare pe drum, întoarcere la boxe, o călătorie rapidă), cu `spawn` la
  sosire (`respawn` pentru resetarea BeamNG); rândul `teleport` poartă sosirea ca `to_x`, `to_y`, `to_z` și distanța ca
  `metres`, iar rândul de început `after: "teleport"`. Adaptoarele de camioane fac la fel pentru un feribot, un tren sau un
  salvat încărcat, iar adaptoarele de zbor pentru un salt pe care niciun avion nu l-ar fi putut zbura. Deci, cu `teleport`
  printre încheieri și `spawn` printre începuturi - ceea ce sugerează singur vizualizatorul - o rută se încheie unde a lăsat
  saltul, iar următoarea începe unde a sosit, și nicio linie nu traversează harta. O rută nu trece niciodată peste o
  schimbare a coloanei `session`. Un rând de poziție se scrie de câteva ori pe secundă (10 Hz pentru majoritatea
  telemetriei), ceea ce dă o linie netedă.
- Coloana `session` împarte o ședință în rundele, etapele, viețile sau corpurile sale (Elite Dangerous ține separate
  rândurile din galaxie și cele de la suprafața fiecărei planete în acest fel). Alegeți una în vizualizator ca să vedeți
  doar acea parte.

Ce face vizualizatorul cu rândurile - filtre, culori, redare - este descris în documentația sa. Sesiunile de demo
Counter-Strike 2 se deschid prin `<map>/<match>.parquet` și `<match>.match.json` ale convertorului, în filele "Hartă
termică" și "Meci" ale vizualizatorului. Pozițiile iRacing vin din fișierele `.ibt` listate în sesiune, pe care
vizualizatorul le citește singur.
