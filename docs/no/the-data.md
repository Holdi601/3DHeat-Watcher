---
title: Dataene
nav_order: 5
lang: "no"
source: the-data.md
source_hash: "6150cdc022fc"
nav_exclude: true
search_exclude: true
---
# Dataene {#the-data}

Alle opptak er vanlige filer i datamappen (`%LOCALAPPDATA%\3DHeat\Watcher` med mindre den er endret, se [Installere og kjøre](installing-and-running.md#where-everything-is)). Du kan lese, kopiere eller slette dem uten watcheren. En `.jsonl`-fil er vanlig tekst, én hendelse per linje (Notisblokk åpner den); en `.parquet`-fil er en tabell som 3DHeat-visningen åpner (Excel gjør ikke det - `stats --csv` skriver CSV-filer for regneark).

## Øktmapper {#session-folders}
![a session folder](../assets/img/session-folder.svg)

En **økt** er én sitting med én kilde: fra det øyeblikket spillet først sier noe, til det stopper (spillet lukkes, en kamp slutter, en kjøring eller flyvning tilbakestilles - hver adapters side sier hva som starter og avslutter økter). Hver økt får en mappe:

```text
<data>\sessions\<game>\<YYYY-MM-DD_HH-MM-SS>_<adapter id>\
    events.jsonl
    heat.parquet
    meta.json
```

- `<game>` er spillets navn med hvert tegn som ikke er bokstaver, siffer, `.`, `_` eller `-` erstattet med `-` (høyst 60 tegn): `EA-SPORTS-F1-25`, `Counter-Strike-2`. Adaptere som dekker mange spill (Steam-statistikk, Steam Timeline, NVIDIA-høydepunkter) fører hver økt under spillet den hører til.
- Tiden er øktens start i lokal tid. Økter som beskriver fortiden (et replay konvertert etter kampen, en Steam-statistikkfil) bruker tidspunktet spillet eller filen oppgir. To økter som starter i samme sekund får `_2`, `_3`, ... lagt til.
- Øktens id, i statistikkdatabasen, er `<game folder>/<session folder>`.

En økt der ingenting i det hele tatt ble tatt opp (spillet sto i menyene, eller krasjet ved start), slettes når den lukkes, så hver start ikke etterlater en tom mappe.

Noen økter har flere filer. En Counter-Strike 2-demo-økt har konverterens egen tabell og oppsummering (`<map>/<match>.parquet`, `<match>.match.json`). En iRacing-økt lister `.ibt`-filene simulatoren skrev under sittingen som `telemetry_file`-hendelser.

## events.jsonl {#eventsjsonl}

`events.jsonl` har ett JSON-objekt per linje, én linje per hendelse, skrevet i det øyeblikket hendelsen skjer. Filen er linjebufret, så en krasj, et strømbrudd eller en drept prosess mister ikke noe som allerede er skrevet; en linje som ble kuttet av en krasj, hoppes over når filen leses, og hver linje før den står fast.

Hver linje har de samme grunnkolonnene:

| Kolonne | Type | Hva den er |
|---|---|---|
| `time` | tall | sekunder siden økten startet (4 desimaler), eller spillets egen klokke der adapteren gir den videre |
| `ms` | heltall | klokkeslett, Unix-millisekunder |
| `event` | tekst | hva som skjedde: `position`, `spawn`, `death`, `kill`, `lap`, `teleport`, `session_start`, ... |
| `x`, `y`, `z` | tall | hvor, i spillets egne enheter og akser (se `axes` i `meta.json`); bare til stede når alle tre er kjent og endelige |
| `player` | tekst | hvem: et navn, en id, eller `me` for personen som spiller (se [Spillerens egne rader](#the-players-own-rows)) |
| `team` | tekst | deres side, når spillet sier det |
| `session` | tekst | kampen, runden, etappen, livet eller flyvningen raden hører til, når spillet sier det |

Ethvert annet felt spillet rapporterer, følger under sitt eget navn (`speed_kmh`, `gear`, `lap_time`, `weapon`, `victim`, `hero`, ...). Felter uten verdi utelates, og det samme gjelder tall som ikke er endelige. To syntetiske linjer:

```json
{"time":12.3456,"ms":1777660501123,"event":"position","x":-412.5,"y":12.1,"z":233.0,"player":"me","session":"1","speed_kmh":187.4,"gear":5}
{"time":15.0,"ms":1777660503667,"event":"lap","x":-380.2,"y":12.0,"z":250.9,"player":"me","session":"1","lap_time":92.418,"lap":3}
```

Rader uten posisjon (en drapslinje i feeden, et nivåopp, en statistikkendring) blir i `events.jsonl` og telles i statistikken. Bare rader med posisjon går inn i tabellen.

### Spillerens egne rader {#the-players-own-rows}

Hvilke rader som tilhører personen som spiller, sier kilden, de gjettes aldri. En rad er spillerens egen når

- `player` er `me`: de fleste adaptere, der kilden er spillerens egen spill (telemetri fra egen bil eller fly, en spilltilstandsintegrasjon, en journal);
- den har `own_car` 1: racingspillene som tar opp hver bil under førerens navn (EA SPORTS F1 etter spillerens bilindeks, RaceRoom etter sin egen plass, Automobilista 2 og Project CARS 2 etter den viste deltakeren) merker spillerens bil på denne måten og beholder førerens navn i `player`;
- `player` er øktens `player` i `meta.json`: navnet kilden gir spilleren - Elite Dangerous' kommandør (journalen er alltid spillerens), eller en League of Legends-replays linje med Riot-ID-en i innstillingene.

War Thunder og Rocket League navngir hver spiller og sier ikke hvem som er deg; med ditt navn i innstillingen `player_names` (se [Innstillinger](installing-and-running.md#settings)) blir radene dine `me`. [NVIDIA-høydepunkter](nvidia-highlights.md) slår et øyeblikk opp i nettopp disse radene.

## heat.parquet {#heatparquet}

Når en økt lukkes, skrives radene i `events.jsonl` som har `x`, `y` og `z`, til `heat.parquet`. Dette er tabellen 3DHeat-visningen åpner. Har økten ingen posisjoner, skrives ingen tabell.

- Kolonnene er `time`, `ms`, `event`, `x`, `y`, `z`, `player`, `team`, `session`, fulgt av alle andre felter i den rekkefølgen de først dukker opp.
- `x`, `y`, `z` og `time` er 64-bits flyttall, og `ms` er et 64-bits heltall. En annen kolonne der alle verdiene er tall, er et 64-bits flyttall; enhver annen kolonne er tekst med ordbokskoding (manglende verdier er tom tekst, og lister eller objekter skrives som JSON-tekst).
- Filens metadata har en nøkkel `heat3d` med leseinstruksjonene, slik at visningen selv kan knytte kolonner og akser (et eksempel, med listen `extra` forkortet):

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

`up` er spillets opp-akse, `flipX`/`flipY`/`flipZ` speiler en akse slik at en venstrehendt verden ikke tegnes speilvendt, og `scale` er visningens enhetsskala: visningen multipliserer hver posisjon med den når den laster tabellen (0.01 gjør centimeter til meter). Hver adapter skriver 1 og beholder spillets egne enheter - meter for de fleste, Source-enheter (tommer) for Counter-Strike 2, Unreal-enheter (centimeter) for Rocket League - fordi et nivå eksportert fra spillet er i de samme enhetene, så radene havner på det; CS2-konverterens egne tabeller sier det samme. `units` i `meta.json` sier hva én enhet er. Hver spillside lister sine verdier under «Positions and axes».

Flysimulatorene (DCS World, Microsoft Flight Simulator, X-Plane, IL-2s Tacview-opptak) legger radene sine på jorden, og fotnoten deres sier hvor, slik at visningen kan legge det virkelige landskapet under dem:

```json
"geo": {"lat0": 42.0, "lon0": 42.0, "projection": "tangent-plane", "east": "x", "north": "z", "up": "y"}
```

`lat0`/`lon0` (grader) er origo for flatkartet radene ligger i; `east`, `north` og `up` navngir kolonnene som holder meter øst og nord for det, og høyden over havet. Origo er første fiks for X-Plane og MSFS, opptakets referansepunkt for IL-2, og teatrets faste origo for DCS (første fiks avrundet til hele grader på et teater watcheren ikke kjenner). En tabell uten sted på jorden har ingen `geo`-nøkkel, og alt annet i fotnoten er det samme uansett.

`heat.parquet` kan alltid bygges på nytt fra `events.jsonl` med `python -m heat3d_watch table <session folder>` (se [Kommandoer](commands.md#table)). Dette er nyttig når `pyarrow` manglet mens økten ble tatt opp.

## meta.json {#metajson}

`meta.json` oppsummerer økten. Den skrives når økten åpnes, høyst hvert 30. sekund mens hendelser eller statistikk kommer inn, og når økten lukkes. Statistikken holdes bare i minnet mellom disse skrivingene, så en krasj kan miste høyst det siste halve minuttet av dem.

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

En økt der kilden navngir spilleren (se [Spillerens egne rader](#the-players-own-rows)), har også `"player"`: navnet spillerens egne rader bærer. En økt på jorden (flysimulatorene) har også `"geo": {"lat0": .., "lon0": ..}`, som fotnotens `geo` gjentar.

- `started` / `ended`: lokal tid, nøyaktig til sekundet; `ended` er `null` mens økten kjører.
- `events`: hvor mange ganger hver hendelse skjedde, hyppigst først. `positions` er antall rader med en posisjon.
- `stats`: øktens tall. En adapter setter hvert ett, legger til i det, eller beholder maksimum eller minimum.
- Det adapteren ellers vet om sittingen, følger på toppnivå: banen, kartet, oppdraget, kamp-id-en, Steam-app-id-en, replayfilen, minneprofilen og bygget. En økt fullført ved gjenoppretting har `"recovered": true`.

## watcher.sqlite {#watchersqlite}

`watcher.sqlite` er statistikkdatabasen. En rad legges til for hver økt når den lukkes. De tre tabellene er vanlige, så ethvert SQL-verktøy, notatbok eller regneark kan lese dem uten watcheren:

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

Å ta opp en økt på nytt (gjenoppretting, et replay konvertert på nytt) erstatter radene. `multiplayer` er adapterens flagg (noen adaptere setter det per økt, for eksempel DCS fra oppdraget), ikke en sjekk av om du var på nett. En sann/usann-verdi i `stats` lagres som tekst.

Et eksempel på en spørring, den beste runden per spill over alle økter (lavere er bedre):

```sql
SELECT s.game, MIN(t.value) AS best_lap
FROM stats t JOIN sessions s ON s.id = t.session
WHERE t.key = 'best_lap'
GROUP BY s.game;
```

`python -m heat3d_watch stats` skriver totaler fra disse tabellene (se [Kommandoer](commands.md#stats)); kolonnen `best` er den laveste verdien for tider holdt som beste og for plasseringer, og den høyeste for resten.

## Gjenoppretting etter en krasj {#recovery-after-a-crash}

Når `run` starter, ser den etter økter en tidligere watcher lot stå åpne: en `meta.json` uten `ended`, og en `events.jsonl` med minst én linje. Den fullfører hver av dem:

- antall hendelser og antall posisjoner telles på nytt fra `events.jsonl`, og en linje som er kuttet av, hoppes over;
- slutten er veggklokkens tid for siste linje (`ms`);
- statistikken er den fra den siste skrivingen av `meta.json` (høyst 30 sekunder gammel);
- `"recovered": true` legges til, `heat.parquet` skrives, og økten går inn i `watcher.sqlite`.

Loggen sier «finished N session(s) left open by an earlier run». Låsefilen hindrer at en watcher som fortsatt kjører, «gjenoppretter» øktene til en annen.

## CSV-eksport {#csv-export}
![stats --csv and table](../assets/img/csv-and-table.svg)

```bash
python -m heat3d_watch stats --csv out
```

skriver `out\sessions.csv`, `out\events.csv` og `out\stats.csv`. Hver fil er én tabell i `watcher.sqlite`, komplett, med en overskriftsrad, som UTF-8. Tidspunkter er Unix-sekunder, som i databasen. `--game` begrenser ikke eksporten; hver økt skrives.

## Åpne en økt i 3DHeat-visningen {#opening-a-session-in-the-3dheat-viewer}

Visningen: [github.com/Holdi601/3DHeat](https://github.com/Holdi601/3DHeat), dokumentasjonen [holdi601.github.io/3DHeat](https://holdi601.github.io/3DHeat/) - dens [`.3dheat`-beholder](https://holdi601.github.io/3DHeat/container.html)-side beskriver formatet med én fil per kamp som replay-konverterne kan skrive.

Åpne en økts `heat.parquet` i 3DHeat-visningen. Fotnoten forteller visningen hvilken kolonne som er posisjonen, tiden, spilleren, siden og laget, og hvilken vei som er opp, så ingenting må knyttes for hånd. Posisjoner er i spillets egne verdenskoordinater. Tegnet over et nivå eksportert med de andre 3DHeat-verktøyene (for eksempel fra [3DHeat GameFiles](https://github.com/Holdi601/3DHeat-GameFiles)), havner de der det skjedde.

- **Varmekart** bruker hver rad med en posisjon, filtrert på `event`, `player`, `team` eller `session` som alle andre kolonner.
- **Linjevarme** tegner en linje fra hver av en spillers rader til neste, og i avspilling er hver spiller et punkt som beveger seg langs ruten med en hale bak seg. Ruter-panelet i visningen velger, ut fra kolonnen `event`, hvilke hendelser som **starter** en rute og hvilke som **avslutter** en. Watcheren skriver avgrensende hendelser som rader med posisjon, slik at de kan velges der:
  - starter: `spawn`, `respawn`, `session_start`. En start lukker ruten som var åpen, uten å tegne en linje til det nye stedet.
  - avslutter: `death`, `finish`, `session_end` og `teleport`. Linjen går opp til selve sluttraden, der spilleren døde, stoppet eller ble tatt bort.

  Et hopp - et sted nådd uten å reise dit - er to rader: `teleport` der stedet ble **forlatt**, og en start der stedet ble **nådd**, rett etter. Racingadapterne skriver en når bilen beveget seg lenger enn den kunne ha kjørt (en spoling tilbake eller en flashback, en tilbakestilling til veien, tilbake til pit, en hurtigreise), med `spawn` ved ankomsten (`respawn` for BeamNGs tilbakestilling); `teleport`-raden bærer ankomsten som `to_x`, `to_y`, `to_z` og avstanden som `metres`, startraden `after: "teleport"`. Lastebiladapterne gjør det samme for en ferge, et tog eller en innlastet lagring, og flyadapterne for et hopp ingen fly kunne ha tatt. Så med `teleport` blant avslutningene og `spawn` blant starterne - det visningen foreslår av seg selv - avsluttes en rute der hoppet forlot stedet, og den neste begynner der det kom frem, og ingen linje krysser kartet. En rute går aldri over en endring i kolonnen `session`. En posisjonsrad skrives noen ganger per sekund (10 Hz for det meste av telemetrien), og det gir en jevn linje.
- Kolonnen `session` deler en sitting i dens runder, etapper, liv eller kropper (Elite Dangerous holder galaksrader og hver planets overflaterader fra hverandre på denne måten). Velg én i visningen for å se bare den delen.

Hva visningen gjør med radene - filtre, farger, avspilling - beskrives i visningens egen dokumentasjon. Counter-Strike 2-demoøkter åpnes gjennom konverterens `<map>/<match>.parquet` og `<match>.match.json` i visningens varme- og kampfaner. iRacings posisjoner kommer fra `.ibt`-filene som står i økten, som visningen leser selv.
