---
title: "Dataene"
nav_order: 5
lang: "da"
source: the-data.md
source_hash: "6150cdc022fc"
nav_exclude: true
search_exclude: true
---
# Dataene {#the-data}

Alle optagelser er almindelige filer i datamappen (`%LOCALAPPDATA%\3DHeat\Watcher`, medmindre det er ændret; se
[Installation og kørsel](installing-and-running.md#where-everything-is)). Du kan læse, kopiere eller slette dem uden watcheren.
En `.jsonl`-fil er almindelig tekst, én hændelse pr. linje (Notesblok åbner den); en `.parquet`-fil er en tabel, som
3DHeat-fremviseren åbner (Excel gør ikke - `stats --csv` skriver CSV-filer til regneark).

## Sessionsmapper {#session-folders}
![en sessionsmappe](../assets/img/session-folder.svg)


En **session** er én omgang med én kilde: fra det øjeblik, spillet første gang siger noget, til det stopper (spillet lukker, en kamp
slutter, en kørsel eller flyvning nulstilles - hver adapters side siger, hvad der starter og slutter dens sessioner). Hver session får
en mappe:

```text
<data>\sessions\<game>\<YYYY-MM-DD_HH-MM-SS>_<adapter id>\
    events.jsonl
    heat.parquet
    meta.json
```

- `<game>` er spillets navn, hvor alle tegn undtagen bogstaver, cifre, `.`, `_` og `-` er erstattet med `-` (højst 60 tegn):
  `EA-SPORTS-F1-25`, `Counter-Strike-2`. Adaptere, der dækker mange spil (Steam-statistik, Steam Timeline, NVIDIA-højdepunkter),
  gemmer hver session under det spil, den hører til.
- Tiden er sessionens start i lokal tid. Sessioner, der beskriver fortiden (et replay konverteret efter kampen, en Steam-statistikfil),
  bruger det tidspunkt, spillet eller filen angiver. To sessioner, der starter i samme sekund, får `_2`, `_3`, ... føjet til.
- Sessionens id i statistikdatabasen er `<game folder>/<session folder>`.

En session, hvor intet overhovedet blev optaget (spillet stod i sine menuer, eller det gik ned ved start), slettes, når den lukkes, så
hver start ikke efterlader en tom mappe.

Nogle sessioner har flere filer. En Counter-Strike 2-demo-session har konverterens egen tabel og opsummering
(`<map>/<match>.parquet`, `<match>.match.json`). En iRacing-session lister de `.ibt`-filer, simulatoren skrev i omgangen, som
`telemetry_file`-hændelser.

## events.jsonl {#eventsjsonl}

`events.jsonl` har ét JSON-objekt pr. linje, én linje pr. hændelse, skrevet i det øjeblik, hændelsen sker. Filen er linjebufferet, så et
nedbrud, et strømsvigt eller en dræbt proces mister intet, der allerede er skrevet; en linje, der er afbrudt af et nedbrud, springes over,
når filen læses, og hver linje før den står ved magt.

Hver linje har de samme grundkolonner:

| Kolonne | Type | Hvad den er |
|---|---|---|
| `time` | tal | sekunder siden sessionens start (4 decimaler), eller spillets eget ur, hvor adapteren giver det videre |
| `ms` | heltal | vægtid, i Unix-millisekunder |
| `event` | tekst | hvad der skete: `position`, `spawn`, `death`, `kill`, `lap`, `teleport`, `session_start`, ... |
| `x`, `y`, `z` | tal | hvor, i spillets egne enheder og akser (se `axes` i `meta.json`); kun til stede, når alle tre er kendt og endelige |
| `player` | tekst | hvem: et navn, et id, eller `me` for personen, der spiller (se [Spillerens egne rækker](#the-players-own-rows)) |
| `team` | tekst | deres side, når spillet siger det |
| `session` | tekst | kampen, runden, etapen, livet eller flyvningen, rækken hører til, når spillet siger det |

Ethvert andet felt, spillet rapporterer, følger under sit eget navn (`speed_kmh`, `gear`, `lap_time`, `weapon`, `victim`, `hero`, ...).
Felter uden en værdi udelades, og det samme gælder tal, der ikke er endelige. To syntetiske linjer:

```json
{"time":12.3456,"ms":1777660501123,"event":"position","x":-412.5,"y":12.1,"z":233.0,"player":"me","session":"1","speed_kmh":187.4,"gear":5}
{"time":15.0,"ms":1777660503667,"event":"lap","x":-380.2,"y":12.0,"z":250.9,"player":"me","session":"1","lap_time":92.418,"lap":3}
```

Rækker uden position (en dræbermeddelelse, et level-up, en statistikændring) bliver i `events.jsonl` og tæller i statistikken. Kun
rækker med en position kommer med i tabellen.

### Spillerens egne rækker {#the-players-own-rows}

Det er kilden, der siger, hvem der spiller; det gættes aldrig. En række er spillerens egen, når

- dens `player` er `me`: de fleste adaptere, hvis kilde er spillerens eget spil (telemetri fra egen bil eller eget fly, en
  spiltilstandsintegration, en journal);
- den bærer `own_car` 1: racingspil, der optager hver bil under dens førers navn (EA SPORTS F1 efter spillets indeks for spillerbilen,
  RaceRoom efter dets egen plads, Automobilista 2 og Project CARS 2 efter den viste deltager), markerer spillerens bil sådan og beholder
  førerens navn i `player`;
- dens `player` er sessionens `player` i `meta.json`: det navn, kilden giver spilleren - Elite Dangerous' kommandør (journalen er altid
  spillerens), eller en League of Legends-replays linje for Riot-ID'et i indstillingerne.

War Thunder og Rocket League navngiver hver spiller og siger ikke, hvem du er; med dit navn i indstillingen `player_names` (se
[Indstillinger](installing-and-running.md#settings)) bliver dine rækker `me`. [NVIDIA-højdepunkter](nvidia-highlights.md) slår et øjeblik op
i netop disse rækker.

## heat.parquet {#heatparquet}

Når en session lukkes, skrives de rækker i `events.jsonl`, der har `x`, `y` og `z`, til `heat.parquet`. Det er den tabel, 3DHeat-fremviseren
åbner. Har sessionen ingen positioner, skrives ingen tabel.

- Kolonnerne er `time`, `ms`, `event`, `x`, `y`, `z`, `player`, `team`, `session`, efterfulgt af hvert andet felt i den rækkefølge, det først
  dukker op.
- `x`, `y`, `z` og `time` er 64-bit kommatal, og `ms` er et 64-bit heltal. En yderligere kolonne, hvis værdier alle er tal, er et 64-bit
  kommatal; enhver anden kolonne er ordbogskodet tekst (manglende værdier er tom tekst, og lister eller objekter skrives som JSON-tekst).
- Filens metadata har en nøgle `heat3d` med læseinstruktionerne, så fremviseren selv kan kortlægge kolonner og akser (et eksempel, med listen
  `extra` forkortet):

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

`up` er spillets op-akse, `flipX`/`flipY`/`flipZ` spejler en akse, så en venstrehåndet verden ikke tegnes spejlvendt, og `scale` er
fremviserens enhedsskala: fremviseren ganger hver position med den, når den indlæser tabellen (0.01 gør centimeter til meter). Hver adapter
skriver 1 og beholder spillets egne enheder - meter for de fleste, Source-enheder (tommer) for Counter-Strike 2, Unreal-enheder (centimeter)
for Rocket League - fordi et level, der er eksporteret fra spillet, er i de samme enheder, så rækkerne lander på det; CS2-konverterens egne
tabeller siger det samme. `units` i `meta.json` siger, hvad én enhed er. Hver spilside lister sine værdier under "Positions and axes".

Flysimulatorerne (DCS World, Microsoft Flight Simulator, X-Plane, IL-2's Tacview-optagelser) lægger deres rækker på jorden, og deres fodnote
siger, hvor, så fremviseren kan lægge den virkelige verden under dem:

```json
"geo": {"lat0": 42.0, "lon0": 42.0, "projection": "tangent-plane", "east": "x", "north": "z", "up": "y"}
```

`lat0`/`lon0` (grader) er origo for det flade kort, rækkerne ligger i; `east`, `north` og `up` navngiver kolonnerne med meter øst og nord
for det og højden over havet. Origo er første fix for X-Plane og MSFS, optagelsens referencepunkt for IL-2 og teatrets faste origo for DCS
(første fix afrundet til hele grader på et teater, watcheren ikke kender). En tabel uden et sted på jorden har ingen `geo`-nøgle, og alt
andet i fodnoten er det samme i begge tilfælde.

`heat.parquet` kan altid genopbygges fra `events.jsonl` med `python -m heat3d_watch table <session folder>` (se
[Kommandoer](commands.md#table)). Det er nyttigt, når `pyarrow` manglede, mens sessionen blev optaget.

## meta.json {#metajson}

`meta.json` opsummerer sessionen. Den skrives, når sessionen åbnes, højst hvert 30. sekund, mens hændelser eller statistik kommer ind, og når
sessionen lukkes. Statistikken holdes kun i hukommelsen mellem skrivningerne, så et nedbrud kan miste højst det sidste halve minut af dem.

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

En session, hvis kilde navngiver spilleren (se [Spillerens egne rækker](#the-players-own-rows)), har også `"player"`: det navn, spillerens
egne rækker bærer. En session på jorden (flysimulatorerne) har også `"geo": {"lat0": .., "lon0": ..}`, som fodnotens `geo` gentager.

- `started` / `ended`: lokal tid til sekundet; `ended` er `null`, mens sessionen kører.
- `events`: hvor mange gange hver hændelse skete, hyppigst først. `positions` er antallet af rækker med en position.
- `stats`: sessionens tal. En adapter sætter hvert, lægger til det eller holder maksimum eller minimum.
- Alt andet, adapteren ved om omgangen, følger på øverste niveau: banen, kortet, missionen, kamp-id'et, Steam-app-id'et, replay-filen,
  hukommelsesprofilen og dens build. En session, der er afsluttet ved gendannelse, har `"recovered": true`.

## watcher.sqlite {#watchersqlite}

`watcher.sqlite` er statistikdatabasen. En række tilføjes for hver session, når den lukkes. De tre tabeller er almindelige, så ethvert
SQL-værktøj, notesbog eller regneark kan læse dem uden watcheren:

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

At optage en session igen (gendannelse, et replay konverteret igen) erstatter dens rækker. `multiplayer` er adapterens flag (nogle adaptere
sætter det pr. session, for eksempel DCS ud fra missionen), ikke en kontrol af, om du var online. En sand/falsk-værdi i `stats` gemmes som tekst.

Et eksempel på en forespørgsel, den bedste omgang pr. spil over alle sessioner (lavere er bedre):

```sql
SELECT s.game, MIN(t.value) AS best_lap
FROM stats t JOIN sessions s ON s.id = t.session
WHERE t.key = 'best_lap'
GROUP BY s.game;
```

`python -m heat3d_watch stats` udskriver totaler fra disse tabeller (se [Kommandoer](commands.md#stats)); dens kolonne `best` er den laveste
værdi for tider, der gemmes som bedste, og for placeringer, og den højeste for resten.

## Gendannelse efter et nedbrud {#recovery-after-a-crash}

Når `run` starter, leder den efter sessioner, en tidligere watcher efterlod åbne: en `meta.json` uden `ended` og en `events.jsonl` med mindst
én linje. Den afslutter hver af dem:

- antallet af hændelser og positioner tælles igen fra `events.jsonl`, og en afbrudt linje springes over;
- slutningen er vægtiden for den sidste linje (`ms`);
- statistikken er den fra den sidste `meta.json`-skrivning (højst 30 sekunder gammel);
- `"recovered": true` tilføjes, `heat.parquet` skrives, og sessionen går ind i `watcher.sqlite`.

Loggen siger "finished N session(s) left open by an earlier run". Låsefilen forhindrer, at en anden watcher "gendanner" sessionerne i en,
der stadig kører.

## CSV-eksport {#csv-export}
![stats --csv og table](../assets/img/csv-and-table.svg)


```bash
python -m heat3d_watch stats --csv out
```

skriver `out\sessions.csv`, `out\events.csv` og `out\stats.csv`. Hver fil er én tabel af `watcher.sqlite`, komplet, med en overskriftsrække,
som UTF-8. Tider er Unix-sekunder, som i databasen. `--game` begrænser ikke eksporten; hver session skrives.

## Åbn en session i 3DHeat-fremviseren {#opening-a-session-in-the-3dheat-viewer}

Fremviseren: [github.com/Holdi601/3DHeat](https://github.com/Holdi601/3DHeat), dokumentation [holdi601.github.io/3DHeat](https://holdi601.github.io/3DHeat/)
- dens side om [`.3dheat`-containeren](https://holdi601.github.io/3DHeat/container.html) beskriver formatet med én fil pr. kamp, som
replay-konverterne kan skrive.

Åbn en sessions `heat.parquet` i 3DHeat-fremviseren. Fodnoten fortæller fremviseren, hvilken kolonne der er position, tid, spiller, hold og
session, og hvilken vej der er op, så intet skal kortlægges i hånden. Positioner er i spillets egne verdenskoordinater. Tegnet over et level,
der er eksporteret med de andre 3DHeat-værktøjer (for eksempel fra [3DHeat GameFiles](https://github.com/Holdi601/3DHeat-GameFiles)), lander de,
hvor det skete.

- **Heatmaps** bruger hver række med en position, filtreret efter `event`, `player`, `team` eller `session` som enhver anden kolonne.
- **Linjevarme** tegner en linje fra hver af en spillers rækker til hans næste, og i afspilning er hver spiller et punkt, der bevæger sig
  langs ruten med en hale bagved. Fremviserens panel Ruter vælger, ud fra kolonnen `event`, hvilke hændelser der **starter** en rute, og hvilke
  der **afslutter** en. Watcheren skriver de afgrænsende hændelser som rækker med en position, så de kan vælges der:
  - starter: `spawn`, `respawn`, `session_start`. En start lukker den rute, der var åben, uden at tegne en linje til det nye sted.
  - slutter: `death`, `finish`, `session_end` og `teleport`. Linjen løber op til selve slutrækken, som er det sted, spilleren døde, stoppede
    eller blev taget væk fra.

  Et hop - et sted nået uden at rejse derhen - er to rækker: `teleport` ved stedet, der blev **forladt**, og en start ved stedet, der blev
  **nået**, lige efter. Racingadaptere skriver en, når bilen flyttede sig længere, end den kunne have kørt (et tilbagespol eller flashback, en
  nulstilling til vejen, tilbage til depotet, en hurtigrejse), med `spawn` ved ankomsten (`respawn` for BeamNGs nulstilling); `teleport`-rækken
  bærer ankomsten som `to_x`, `to_y`, `to_z` og afstanden som `metres`, startrækken `after: "teleport"`. Lastbilsadapterne gør det samme for en
  færge, et tog eller en indlæst gemning, og flyadapterne for et hop, intet fly kunne flyve. Så når `teleport` er blandt slutningerne og `spawn`
  blandt starterne - hvilket fremviseren selv foreslår - slutter en rute, hvor hoppet forlod, og den næste begynder, hvor det ankom, og ingen linje
  krydser kortet. En rute krydser aldrig en ændring i kolonnen `session`. En positionsrække skrives et par gange i sekundet (10 Hz for de fleste
  telemetrier), hvilket giver en jævn linje.
- Kolonnen `session` deler en omgang op i dens runder, etaper, liv eller kroppe (Elite Dangerous holder galaksrækker og hver planets
  overfladerækker adskilt på den måde). Vælg én i fremviseren for kun at se den del.

Hvad fremviseren gør med rækkerne - filtre, farver, afspilning - er beskrevet i fremviserens egen dokumentation. Counter-Strike 2-demo-sessioner
åbnes gennem konverterens `<map>/<match>.parquet` og `<match>.match.json` i fremviserens faner Heatmap og Kamp. iRacings positioner kommer fra
`.ibt`-filerne, der står i sessionen, og som fremviseren selv læser.
