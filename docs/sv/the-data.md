---
title: Datan
nav_order: 5
lang: "sv"
source: the-data.md
source_hash: "6150cdc022fc"
nav_exclude: true
search_exclude: true
---
# Datan {#the-data}

All inspelning är vanliga filer i datamappen (`%LOCALAPPDATA%\3DHeat\Watcher` om inget annat är ändrat, se [Installera och köra](installing-and-running.md#where-everything-is)). Du kan läsa, kopiera eller ta bort dem utan watchern. En `.jsonl`-fil är vanlig text, en händelse per rad (Anteckningar öppnar den); en `.parquet`-fil är en tabell som 3DHeat-visaren öppnar (Excel gör inte det – `stats --csv` skriver CSV-filer för kalkylblad).

## Sessionsmappar {#session-folders}
![en sessionsmapp](../assets/img/session-folder.svg)

En **session** är en sittning med en källa: från den stund spelet först säger något tills det slutar (spelet stängs, en match tar slut, ett körpass eller en flygning återställs – varje adapters sida säger vad som startar och avslutar dess sessioner). Varje session får en mapp:

```text
<data>\sessions\<game>\<YYYY-MM-DD_HH-MM-SS>_<adapter id>\
    events.jsonl
    heat.parquet
    meta.json
```

- `<game>` är spelets namn med varje tecken utom bokstäver, siffror, `.`, `_` och `-` ersatt med `-` (högst 60 tecken): `EA-SPORTS-F1-25`, `Counter-Strike-2`. Adaptrar som täcker många spel (Steams statistik, Steam Timeline, NVIDIA-höjdpunkter) sorterar varje session under det spel den tillhör.
- Tiden är sessionens start i lokal tid. Sessioner som beskriver det förflutna (en replay som konverteras efter matchen, en Steam-statistikfil) använder tiden som spelet eller filen anger. Två sessioner som startar under samma sekund får `_2`, `_3`, ... efter sig.
- Sessionens id i statistikdatabasen är `<game folder>/<session folder>`.

En session där absolut inget spelades in (spelet stod i sina menyer, eller kraschade vid start) raderas när den stängs, så att varje start inte lämnar en tom mapp kvar.

Vissa sessioner har fler filer. En Counter-Strike 2-demosession har konverterarens egen tabell och sammanfattning (`<map>/<match>.parquet`, `<match>.match.json`). En iRacing-session listar de `.ibt`-filer simulatorn skrev under sittningen som `telemetry_file`-händelser.

## events.jsonl {#eventsjsonl}

`events.jsonl` har ett JSON-objekt per rad, en rad per händelse, skriven i samma ögonblick som händelsen sker. Filen är radbuffrad, så en krasch, ett strömavbrott eller en dödad process förlorar inget som redan skrivits; en rad som avbrutits av en krasch hoppas över när filen läses, och varje rad före den står kvar.

Varje rad har samma baskolumner:

| Kolumn | Typ | Vad den är |
|---|---|---|
| `time` | tal | sekunder sedan sessionen började (4 decimaler), eller spelets egen klocka där adaptern skickar den vidare |
| `ms` | heltal | väggklocktid, Unix-millisekunder |
| `event` | text | vad som hände: `position`, `spawn`, `death`, `kill`, `lap`, `teleport`, `session_start`, ... |
| `x`, `y`, `z` | tal | var, i spelets egna enheter och axlar (se `axes` i `meta.json`); finns bara när alla tre är kända och ändliga |
| `player` | text | vem: ett namn, ett id, eller `me` för personen som spelar (se [Spelarens egna rader](#the-players-own-rows)) |
| `team` | text | deras sida, när spelet säger det |
| `session` | text | matchen, rundan, etappen, livet eller flygningen som raden hör till, när spelet säger det |

Alla andra fält spelet rapporterar följer under sitt eget namn (`speed_kmh`, `gear`, `lap_time`, `weapon`, `victim`, `hero`, ...). Fält utan värde utelämnas, och så även tal som inte är ändliga. Två syntetiska rader:

```json
{"time":12.3456,"ms":1777660501123,"event":"position","x":-412.5,"y":12.1,"z":233.0,"player":"me","session":"1","speed_kmh":187.4,"gear":5}
{"time":15.0,"ms":1777660503667,"event":"lap","x":-380.2,"y":12.0,"z":250.9,"player":"me","session":"1","lap_time":92.418,"lap":3}
```

Rader utan position (en killfeed-rad, en nivåhöjning, en statistikändring) stannar i `events.jsonl` och räknas i statistiken. Bara rader med en position går in i tabellen.

### Spelarens egna rader {#the-players-own-rows}

Vilka rader som är personen som spelar anges av källan, aldrig gissat. En rad är spelarens egen när

- dess `player` är `me`: de flesta adaptrar, vars källa är spelarens egna spel (telemetri från den egna bilen eller flygplanet, en spelstatusintegration, en journal);
- den bär `own_car` 1: racingspelen som spelar in varje bil under dess förares namn (EA SPORTS F1 efter spelets spelarbilsindex, RaceRoom efter dess egna plats, Automobilista 2 och Project CARS 2 efter den visade deltagaren) markerar spelarens bil på det sättet och behåller förarens namn i `player`;
- dess `player` är sessionens `player` i `meta.json`: namnet källan ger spelaren – Elite Dangerous-befälhavaren (journalen är alltid spelarens), eller en League of Legends-replays rad för Riot-ID:t i inställningarna.

War Thunder och Rocket League namnger varje spelare och säger inte vilken som är du; med ditt namn i inställningen `player_names` (se [Inställningar](installing-and-running.md#settings)) blir dina rader `me`. [NVIDIA-höjdpunkter](nvidia-highlights.md) slår upp ett ögonblick i just dessa rader.

## heat.parquet {#heatparquet}

När en session stängs skrivs raderna i `events.jsonl` som har `x`, `y` och `z` till `heat.parquet`. Det är tabellen 3DHeat-visaren öppnar. Om sessionen saknar positioner skrivs ingen tabell.

- Kolumnerna är `time`, `ms`, `event`, `x`, `y`, `z`, `player`, `team`, `session`, följt av varje annat fält i den ordning det först förekommer.
- `x`, `y`, `z` och `time` är 64-bitars flyttal och `ms` är ett 64-bitars heltal. En ytterligare kolumn vars värden alla är tal är ett 64-bitars flyttal; varje annan kolumn är ordboksskriven text (saknade värden är tom text, och listor eller objekt skrivs som JSON-text).
- Filens metadata har en nyckel `heat3d` med läsanvisningarna, så att visaren kopplar kolumner och axlar själv (ett exempel, med listan `extra` förkortad):

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

`up` är spelets upp-axel, `flipX`/`flipY`/`flipZ` speglar en axel så att en vänsterhänt värld inte ritas spegelvänd, och `scale` är visarens enhetsskala: visaren multiplicerar varje position med den när den läser in tabellen (0.01 skulle göra centimeter till meter). Varje adapter skriver 1 och behåller spelets egna enheter – meter för de flesta, Source-enheter (tum) för Counter-Strike 2, Unreal-enheter (centimeter) för Rocket League – eftersom en nivå exporterad från spelet är i just de enheterna, så raderna hamnar på den. `units` i `meta.json` säger vad en enhet är. Varje spels sida listar sina värden under "Positions and axes".

Flygsimmarna (DCS World, Microsoft Flight Simulator, X-Plane, IL-2:s Tacview-inspelningar) lägger sina rader på jordklotet, och sidfoten säger var, så att visaren kan lägga den verkliga världen under dem:

```json
"geo": {"lat0": 42.0, "lon0": 42.0, "projection": "tangent-plane", "east": "x", "north": "z", "up": "y"}
```

`lat0`/`lon0` (grader) är origo för den platta kartan raderna ligger i; `east`, `north` och `up` anger de kolumner som håller meter österut och norrut från den och höjden över havet. Origo är första fixen för X-Plane och MSFS, inspelningens referenspunkt för IL-2, och teaterns fasta origo för DCS (första fixen avrundad till hela grader på en teater watchern inte känner till). En tabell utan plats på jordklotet har ingen `geo`-nyckel, och allt annat i sidfoten är detsamma i båda fallen.

`heat.parquet` kan alltid byggas om från `events.jsonl` med `python -m heat3d_watch table <session folder>` (se [Kommandon](commands.md#table)). Det är användbart när `pyarrow` saknades medan sessionen spelades in.

## meta.json {#metajson}

`meta.json` sammanfattar sessionen. Den skrivs när sessionen öppnas, högst var 30:e sekund medan händelser eller statistik kommer in, och när sessionen stängs. Statistiken hålls bara i minnet mellan skrivningarna, så en krasch kan förlora högst den sista halvminuten av den.

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

En session vars källa anger spelaren (se [Spelarens egna rader](#the-players-own-rows)) har också `"player"`: namnet som spelarens egna rader bär. En session på jordklotet (flygsimmarna) har dessutom `"geo": {"lat0": .., "lon0": ..}`, origo som sidfotens `geo` upprepar.

- `started` / `ended`: lokal tid till sekunden; `ended` är `null` medan sessionen körs.
- `events`: hur många gånger varje händelse inträffade, vanligast först. `positions` är antalet rader med en position.
- `stats`: sessionens siffror. En adapter sätter var och en, lägger till i den, eller behåller det högsta eller lägsta värdet.
- Allt annat adaptern vet om sittningen följer på översta nivån: banan, kartan, uppdraget, match-id:t, Steams app-id, replayfilen, minnesprofilen och versionen. En session som avslutats av återställning har `"recovered": true`.

## watcher.sqlite {#watchersqlite}

`watcher.sqlite` är statistikdatabasen. En rad läggs till för varje session när den stängs. De tre tabellerna är vanliga, så vilket SQL-verktyg, anteckningsbok eller kalkylblad som helst kan läsa dem utan watchern:

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

Att spela in en session igen (återställning, en replay konverterad på nytt) ersätter dess rader. `multiplayer` är adapterns flagga (vissa adaptrar sätter den per session, till exempel DCS utifrån uppdraget), inte en kontroll av om du var online. Ett sant/falskt-värde i `stats` lagras som text.

Ett exempelfråga, den bästa varvtiden per spel över alla sessioner (lägre är bättre):

```sql
SELECT s.game, MIN(t.value) AS best_lap
FROM stats t JOIN sessions s ON s.id = t.session
WHERE t.key = 'best_lap'
GROUP BY s.game;
```

`python -m heat3d_watch stats` skriver ut summor från dessa tabeller (se [Kommandon](commands.md#stats)); dess kolumn `best` är det lägsta värdet för tider som sparas som bästa och för placeringar, det högsta för resten.

## Återställning efter en krasch {#recovery-after-a-crash}

När `run` startar letar den efter sessioner som en tidigare watcher lämnade öppna: en `meta.json` utan `ended`, och en `events.jsonl` med minst en rad. Den avslutar var och en:

- händelseräknarna och antalet positioner räknas om från `events.jsonl`, och en avskuren rad hoppas över;
- slutet är väggklocktiden för den sista raden (`ms`);
- statistiken är den från den senaste skrivningen av `meta.json` (högst 30 sekunder gammal);
- `"recovered": true` läggs till, `heat.parquet` skrivs, och sessionen går in i `watcher.sqlite`.

Loggen säger "finished N session(s) left open by an earlier run". Låsfilen hindrar en andra watcher från att "återställa" sessionerna hos en som fortfarande kör.

## CSV-export {#csv-export}
![stats --csv och table](../assets/img/csv-and-table.svg)

```bash
python -m heat3d_watch stats --csv out
```

skriver `out\sessions.csv`, `out\events.csv` och `out\stats.csv`. Varje fil är en tabell i `watcher.sqlite`, komplett, med en rubrikrad, som UTF-8. Tider är Unix-sekunder som i databasen. `--game` begränsar inte exporten; varje session skrivs.

## Öppna en session i 3DHeat-visaren {#opening-a-session-in-the-3dheat-viewer}

Visaren: [github.com/Holdi601/3DHeat](https://github.com/Holdi601/3DHeat), dokumentationen [holdi601.github.io/3DHeat](https://holdi601.github.io/3DHeat/) – dess sida om [`.3dheat`-containern](https://holdi601.github.io/3DHeat/container.html) beskriver formatet med en fil per match som replay-konverterarna kan skriva.

Öppna en sessions `heat.parquet` i 3DHeat-visaren. Sidfoten säger åt visaren vilken kolumn som är position, tid, spelare, lag och session, och vilket håll som är upp, så att inget behöver kopplas för hand. Positionerna är i spelets egna världskoordinater. Ritade över en nivå exporterad med de andra 3DHeat-verktygen (till exempel från [3DHeat GameFiles](https://github.com/Holdi601/3DHeat-GameFiles)) hamnar de där det hände.

- **Värmekartor** använder varje rad med en position, filtrerad på `event`, `player`, `team` eller `session` precis som vilken annan kolumn som helst.
- **Linjevärme** ritar en linje från varje spelares rad till nästa, och i uppspelningen är varje spelare en punkt som rör sig längs rutten med en svans bakom. Visarens panel Rutter väljer, utifrån kolumnen `event`, vilka händelser som **startar** en rutt och vilka som **avslutar** en. Watchern skriver avgränsningshändelserna som rader med en position, så att de kan väljas där:
  - starter: `spawn`, `respawn`, `session_start`. En start stänger rutten som var öppen utan att rita en linje till den nya platsen.
  - slut: `death`, `finish`, `session_end` och `teleport`. Linjen går fram till slutraden själv, det vill säga där spelaren dog, stannade eller togs bort.

  Ett hopp – en plats som nås utan att resa dit – är två rader: `teleport` på platsen som **lämnades**, och en start på platsen som **nåddes**, direkt efter. Racingadaptrarna skriver en varje gång bilen förflyttade sig längre än den kunde ha kört (en spolning bakåt eller ett flashback, en återställning till vägen, tillbaka till depån, en snabbresa), med `spawn` vid ankomsten (`respawn` för BeamNGs återställning); `teleport`-raden bär ankomsten som `to_x`, `to_y`, `to_z` och avståndet som `metres`, startraden `after: "teleport"`. Lastbilsadaptrarna gör detsamma för en färja, ett tåg eller en laddad sparfil, och flygadaptrarna för ett hopp som inget flygplan kunde flyga. Så, med `teleport` bland slutet och `spawn` bland starterna – vilket visaren föreslår av sig självt – slutar en rutt där hoppet lämnade och nästa börjar där det kom fram, och ingen linje korsar kartan. En rutt korsar aldrig en förändring i kolumnen `session`. En positionsrad skrivs några gånger per sekund (10 Hz för de flesta telemetrier), vilket ger en jämn linje.
- Kolumnen `session` delar upp en sittning i dess omgångar, etapper, liv eller kroppar (Elite Dangerous håller galaxrader och varje planets ytrader åtskilda på det sättet). Välj en i visaren för att titta på just den delen.

Vad visaren gör med raderna – filter, färger, uppspelning – beskrivs i visarens egen dokumentation. Counter-Strike 2-demosessioner öppnas via konverterarens `<map>/<match>.parquet` och `<match>.match.json` i visarens flikar Värmekarta och Match. iRacings positioner kommer från `.ibt`-filerna som listas i sessionen, som visaren läser själv.
