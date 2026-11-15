---
title: "Die Daten"
nav_order: 5
lang: "de"
source: the-data.md
source_hash: "6150cdc022fc"
nav_exclude: true
search_exclude: true
---
# Die Daten {#the-data}

Alle Aufnahmen sind einfache Dateien im Datenordner (`%LOCALAPPDATA%\3DHeat\Watcher`, sofern nichts anderes
eingestellt ist, siehe [Installieren und Starten](installing-and-running.md#where-everything-is)). Du kannst sie
ohne den Watcher lesen, kopieren oder löschen. Eine `.jsonl`-Datei ist Klartext, eine Zeile pro Ereignis (Notepad
öffnet sie); eine `.parquet`-Datei ist eine Tabelle, die der 3DHeat-Viewer öffnet (Excel nicht – `stats --csv`
schreibt CSV-Dateien für Tabellenkalkulationen).

## Sitzungsordner {#session-folders}
![ein Sitzungsordner](../assets/img/session-folder.svg)


Eine **Sitzung** ist ein Durchgang mit einer Quelle: vom Moment, in dem das Spiel zum ersten Mal etwas sagt, bis es
aufhört (das Spiel wird geschlossen, ein Match endet, eine Fahrt oder ein Flug wird zurückgesetzt – auf der Seite
jedes Adapters steht, was eine Sitzung beginnt und beendet). Jede Sitzung bekommt einen Ordner:

```text
<data>\sessions\<game>\<YYYY-MM-DD_HH-MM-SS>_<adapter id>\
    events.jsonl
    heat.parquet
    meta.json
```

- `<game>` ist der Name des Spiels, wobei jedes Zeichen außer Buchstaben, Ziffern, `.`, `_` und `-` durch `-` ersetzt
  wird (höchstens 60 Zeichen): `EA-SPORTS-F1-25`, `Counter-Strike-2`. Adapter, die viele Spiele abdecken (Steam-Statistiken,
  Steam-Timeline, NVIDIA-Highlights), legen jede Sitzung unter dem Spiel ab, zu dem sie gehört.
- Die Zeit ist der Beginn der Sitzung in Ortszeit. Sitzungen, die die Vergangenheit beschreiben (ein Replay, das nach
  dem Match umgewandelt wird, eine Statistikdatei von Steam), nehmen die Zeit, die das Spiel oder die Datei angibt. Zwei
  Sitzungen, die in derselben Sekunde beginnen, bekommen `_2`, `_3`, ... angehängt.
- Die ID der Sitzung in der Statistik-Datenbank ist `<game folder>/<session folder>`.

Eine Sitzung, in der gar nichts aufgezeichnet wurde (das Spiel saß in seinen Menüs, oder es stürzte beim Start ab),
wird beim Schließen gelöscht, damit nicht bei jedem Start ein leerer Ordner bleibt.

Manche Sitzungen enthalten weitere Dateien. Eine Counter-Strike-2-Demo-Sitzung enthält die eigene Tabelle und
Zusammenfassung des Konverters (`<map>/<match>.parquet`, `<match>.match.json`). Eine iRacing-Sitzung listet die
`.ibt`-Dateien, die das Spiel während des Durchgangs geschrieben hat, als `telemetry_file`-Ereignisse.

## events.jsonl {#eventsjsonl}

`events.jsonl` hat ein JSON-Objekt pro Zeile, eine Zeile pro Ereignis, geschrieben in dem Moment, in dem das Ereignis
passiert. Die Datei ist zeilengepuffert, daher verliert ein Absturz, ein Stromausfall oder ein beendeter Prozess nichts,
was schon geschrieben war; eine Zeile, die durch einen Absturz abgeschnitten wurde, wird beim Lesen übersprungen, und
jede Zeile davor bleibt bestehen.

Jede Zeile hat dieselben Grundspalten:

| Spalte | Typ | Was sie ist |
|---|---|---|
| `time` | Zahl | Sekunden seit Beginn der Sitzung (4 Nachkommastellen), oder die eigene Uhr des Spiels, wo der Adapter sie weitergibt |
| `ms` | Ganzzahl | Uhrzeit, Unix-Millisekunden |
| `event` | Text | was passiert ist: `position`, `spawn`, `death`, `kill`, `lap`, `teleport`, `session_start`, ... |
| `x`, `y`, `z` | Zahl | wo, in den eigenen Einheiten und Achsen des Spiels (siehe `axes` in `meta.json`); nur vorhanden, wenn alle drei bekannt und endlich sind |
| `player` | Text | wer: ein Name, eine ID, oder `me` für die Person, die spielt (siehe [Die eigenen Zeilen des Spielers](#the-players-own-rows)) |
| `team` | Text | ihre Seite, wenn das Spiel sie angibt |
| `session` | Text | das Match, die Runde, die Etappe, das Leben oder der Flug, zu dem die Zeile gehört, wenn das Spiel es angibt |

Jedes andere Feld, das das Spiel meldet, folgt unter seinem eigenen Namen (`speed_kmh`, `gear`, `lap_time`, `weapon`,
`victim`, `hero`, ...). Felder ohne Wert werden weggelassen, und ebenso Zahlen, die nicht endlich sind. Zwei erfundene
Zeilen:

```json
{"time":12.3456,"ms":1777660501123,"event":"position","x":-412.5,"y":12.1,"z":233.0,"player":"me","session":"1","speed_kmh":187.4,"gear":5}
{"time":15.0,"ms":1777660503667,"event":"lap","x":-380.2,"y":12.0,"z":250.9,"player":"me","session":"1","lap_time":92.418,"lap":3}
```

Zeilen ohne Position (eine Zeile aus dem Abschussprotokoll, ein Stufenaufstieg, eine Änderung der Werte) bleiben in
`events.jsonl` und zählen in der Statistik. Nur Zeilen mit einer Position kommen in die Tabelle.

### Die eigenen Zeilen des Spielers {#the-players-own-rows}

Welche Zeilen zur spielenden Person gehören, sagt die Quelle; es wird nie geraten. Eine Zeile gehört dem Spieler, wenn

- ihr `player` `me` ist: die meisten Adapter, deren Quelle das eigene Spiel des Spielers ist (Telemetrie des eigenen
  Autos oder Flugzeugs, eine Spielzustands-Integration, ein Journal);
- sie `own_car` 1 trägt: die Rennspiele, die jedes Auto unter dem Namen seines Fahrers aufzeichnen (EA SPORTS F1 nach dem
  Spielerindex des Autos im Spiel, RaceRoom nach dem eigenen Platz, Automobilista 2 und Project CARS 2 nach dem betrachteten
  Teilnehmer), markieren das Auto des Spielers so und behalten den Namen des Fahrers in `player`;
- ihr `player` der `player` der Sitzung in `meta.json` ist: der Name, den die Quelle dem Spieler gibt – der Kommandant von
  Elite Dangerous (das Journal gehört immer dem Spieler), eine Zeile des Riot-ID-Eintrags aus den Einstellungen in einem
  League-of-Legends-Replay.

War Thunder und Rocket League nennen jeden Spieler und sagen nicht, wer du bist; mit deinem Namen in der Einstellung
`player_names` (siehe [Einstellungen](installing-and-running.md#settings)) werden deine Zeilen zu `me`.
[NVIDIA-Highlights](nvidia-highlights.md) schlagen einen Moment genau in diesen Zeilen nach.

## heat.parquet {#heatparquet}

Wenn eine Sitzung schließt, werden die Zeilen von `events.jsonl`, die `x`, `y` und `z` haben, in `heat.parquet`
geschrieben. Das ist die Tabelle, die der 3DHeat-Viewer öffnet. Hat die Sitzung keine Positionen, wird keine Tabelle
geschrieben.

- Die Spalten sind `time`, `ms`, `event`, `x`, `y`, `z`, `player`, `team`, `session`, gefolgt von jedem anderen Feld in der
  Reihenfolge, in der es zuerst erscheint.
- `x`, `y`, `z` und `time` sind 64-Bit-Fließkommazahlen, und `ms` ist eine 64-Bit-Ganzzahl. Eine weitere Spalte, deren
  Werte alle Zahlen sind, ist eine 64-Bit-Fließkommazahl; jede andere Spalte ist wörterbuchkodierter Text (fehlende Werte
  sind leerer Text, und Listen oder Objekte werden als JSON-Text geschrieben).
- Die Metadaten der Datei haben einen Schlüssel `heat3d` mit den Leseanweisungen, damit der Viewer Spalten und Achsen
  selbst zuordnet (ein Beispiel, die Liste `extra` gekürzt):

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

`up` ist die Hochachse des Spiels, `flipX`/`flipY`/`flipZ` spiegeln eine Achse, damit eine linkshändige Welt nicht
gespiegelt gezeichnet wird, und `scale` ist der Maßstab der Einheiten für den Viewer: Der Viewer multipliziert jede
Position damit, wenn er die Tabelle lädt (0,01 würde Zentimeter in Meter verwandeln). Jeder Adapter schreibt 1 und behält
die eigenen Einheiten des Spiels – für die meisten Meter, für Counter-Strike 2 Source-Einheiten (Zoll), für Rocket League
Unreal-Einheiten (Zentimeter) –, weil ein aus dem Spiel exportiertes Level in genau diesen Einheiten liegt und die Zeilen
dadurch darauf landen; die eigenen Tabellen des CS2-Konverters sagen dasselbe. `units` in `meta.json` sagt, was eine
Einheit ist. Die Seite jedes Spiels listet seine Werte unter „Positions and axes“.

Die Flugsimulatoren (DCS World, Microsoft Flight Simulator, X-Plane, die Tacview-Aufzeichnungen von IL-2) legen ihre
Zeilen auf die Erde, und ihre Fußzeile sagt, wo, damit der Viewer die echte Welt unter sie legen kann:

```json
"geo": {"lat0": 42.0, "lon0": 42.0, "projection": "tangent-plane", "east": "x", "north": "z", "up": "y"}
```

`lat0`/`lon0` (Grad) sind der Ursprung der flachen Karte, in der die Zeilen liegen; `east`, `north` und `up` nennen die
Spalten mit den Metern nach Osten und Norden davon und der Höhe über dem Meeresspiegel. Der Ursprung ist der erste Fix
bei X-Plane und MSFS, der Bezugspunkt der Aufzeichnung bei IL-2, und der feste Ursprung des Schauplatzes bei DCS (der
erste Fix, auf ganze Grad gerundet, für einen Schauplatz, den der Watcher nicht kennt). Eine Tabelle ohne Ort auf der Erde
hat keinen Schlüssel `geo`, und alles andere in der Fußzeile ist in beiden Fällen gleich.

`heat.parquet` kann jederzeit aus `events.jsonl` mit
`python -m heat3d_watch table <session folder>` neu gebaut werden (siehe [Befehle](commands.md#table)). Das ist nützlich,
wenn `pyarrow` fehlte, während die Sitzung aufgenommen wurde.

## meta.json {#metajson}

`meta.json` fasst die Sitzung zusammen. Sie wird beim Öffnen der Sitzung geschrieben, höchstens alle 30 Sekunden, während
Ereignisse oder Statistiken eingehen, und beim Schließen. Statistiken werden nur zwischen diesen Schreibvorgängen im
Speicher gehalten, daher kann ein Absturz höchstens die letzte halbe Minute davon verlieren.

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

Eine Sitzung, deren Quelle den Spieler nennt (siehe [Die eigenen Zeilen des Spielers](#the-players-own-rows)), hat außerdem
`"player"`: den Namen, den die eigenen Zeilen des Spielers tragen. Eine Sitzung auf der Erde (die Flugsimulatoren) hat
außerdem `"geo": {"lat0": .., "lon0": ..}`, den Ursprung, den die Fußzeile ihres `geo` wiederholt.

- `started` / `ended`: Ortszeit auf die Sekunde genau; `ended` ist `null`, solange die Sitzung läuft.
- `events`: wie oft jedes Ereignis passiert ist, das häufigste zuerst. `positions` ist die Anzahl der Zeilen mit einer
  Position.
- `stats`: die Zahlen der Sitzung. Ein Adapter setzt jede davon, addiert dazu oder behält das Maximum oder Minimum.
- Was der Adapter sonst über den Durchgang weiß, folgt auf der obersten Ebene: die Strecke, die Karte, die Mission, die
  Match-ID, die Steam-App-ID, die Replay-Datei, das Speicherprofil und die Version. Eine Sitzung, die durch Wiederherstellung
  beendet wurde, hat `"recovered": true`.

## watcher.sqlite {#watchersqlite}

`watcher.sqlite` ist die Statistik-Datenbank. Eine Zeile wird für jede Sitzung beim Schließen hinzugefügt. Die drei Tabellen
sind einfach, daher kann jedes SQL-Werkzeug, Notebook oder jede Tabellenkalkulation sie ohne den Watcher lesen:

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

Eine Sitzung erneut aufzunehmen (Wiederherstellung, ein Replay, das erneut umgewandelt wird), ersetzt ihre Zeilen.
`multiplayer` ist das Flag des Adapters (manche Adapter setzen es pro Sitzung, zum Beispiel DCS aus der Mission), keine
Prüfung, ob du online warst. Ein Wahr/Falsch-Wert in `stats` wird als Text gespeichert.

Ein Beispiel für eine Abfrage, die beste Runde je Spiel über alle Sitzungen (niedriger ist besser):

```sql
SELECT s.game, MIN(t.value) AS best_lap
FROM stats t JOIN sessions s ON s.id = t.session
WHERE t.key = 'best_lap'
GROUP BY s.game;
```

`python -m heat3d_watch stats` gibt Summen aus diesen Tabellen aus (siehe [Befehle](commands.md#stats)); seine Spalte
`best` ist der niedrigste Wert für Zeiten, die als Bestwert gehalten werden, und für Platzierungen, der höchste für den
Rest.

## Wiederherstellung nach einem Absturz {#recovery-after-a-crash}

Wenn `run` startet, sucht er nach Sitzungen, die ein früherer Watcher offen gelassen hat: eine `meta.json` ohne `ended`
und eine `events.jsonl` mit mindestens einer Zeile. Er beendet jede davon:

- die Anzahl der Ereignisse und der Positionen wird aus `events.jsonl` neu gezählt, und eine abgeschnittene Zeile wird
  übersprungen;
- das Ende ist die Uhrzeit der letzten Zeile (`ms`);
- die Statistiken sind die des letzten Schreibvorgangs von `meta.json` (höchstens 30 Sekunden alt);
- `"recovered": true` wird hinzugefügt, `heat.parquet` wird geschrieben, und die Sitzung kommt in `watcher.sqlite`.

Das Protokoll sagt „finished N session(s) left open by an earlier run“. Die Sperrdatei verhindert, dass ein zweiter
Watcher die Sitzungen eines laufenden anderen „wiederherstellt“.

## CSV-Export {#csv-export}
![stats --csv und table](../assets/img/csv-and-table.svg)


```bash
python -m heat3d_watch stats --csv out
```

schreibt `out\sessions.csv`, `out\events.csv` und `out\stats.csv`. Jede Datei ist eine vollständige Tabelle aus
`watcher.sqlite` mit einer Kopfzeile, als UTF-8. Zeiten sind Unix-Sekunden wie in der Datenbank. `--game` schränkt den
Export nicht ein; jede Sitzung wird geschrieben.

## Eine Sitzung im 3DHeat-Viewer öffnen {#opening-a-session-in-the-3dheat-viewer}

Der Viewer: [github.com/Holdi601/3DHeat](https://github.com/Holdi601/3DHeat), die Dokumentation
[holdi601.github.io/3DHeat](https://holdi601.github.io/3DHeat/) – ihre Seite zum
[`.3dheat`-Container](https://holdi601.github.io/3DHeat/container.html) beschreibt das Format „ein Match in einer Datei“,
das die Replay-Konverter schreiben können.

Öffne das `heat.parquet` einer Sitzung im 3DHeat-Viewer. Die Fußzeile sagt dem Viewer, welche Spalte die Position, die
Zeit, der Spieler, das Team und die Sitzung ist und wo oben ist, daher muss nichts von Hand zugeordnet werden. Positionen
liegen in den eigenen Weltkoordinaten des Spiels. Über ein Level, das mit den anderen 3DHeat-Werkzeugen exportiert wurde
(zum Beispiel aus [3DHeat GameFiles](https://github.com/Holdi601/3DHeat-GameFiles)), landen sie dort, wo sie passiert sind.

- **Heatmaps** nutzen jede Zeile mit einer Position, gefiltert nach `event`, `player`, `team` oder `session` wie jede
  andere Spalte.
- **Linien** zeichnen von jeder Zeile eines Spielers eine Linie zu seiner nächsten, und beim Abspielen bewegt sich jeder
  Spieler als Punkt mit einem Schweif die Route entlang. Das Routen-Panel des Viewers wählt anhand der Spalte `event` aus,
  welche Ereignisse eine Route **beginnen** und welche sie **beenden**. Der Watcher schreibt die begrenzenden Ereignisse als
  Zeilen mit einer Position, damit sie dort gewählt werden können:
  - Starts: `spawn`, `respawn`, `session_start`. Ein Start schließt die Route, die offen war, ohne eine Linie zum neuen Ort
    zu zeichnen.
  - Enden: `death`, `finish`, `session_end` und `teleport`. Die Linie läuft bis zur Endzeile selbst, dort, wo der Spieler
    starb, anhielt oder weggebracht wurde.

  Ein Sprung – ein Ort, der erreicht wird, ohne dorthin zu fahren – besteht aus zwei Zeilen: `teleport` an dem Ort, den man
  **verlassen** hat, und einem Start an dem Ort, der **erreicht** wurde, direkt danach. Die Rennadapter schreiben einen,
  wann immer sich das Auto weiter bewegt hat, als es hätte fahren können (ein Zurückspulen oder Flashback, ein Reset auf die
  Straße, zurück an die Box, eine Schnellreise), mit `spawn` an der Ankunft (`respawn` bei BeamNGs Reset); die `teleport`-Zeile
  trägt die Ankunft als `to_x`, `to_y`, `to_z` und die Strecke als `metres`, die Startzeile `after: "teleport"`. Die
  Lkw-Adapter tun dasselbe für eine Fähre, einen Zug oder einen geladenen Spielstand, die Flugadapter für einen Sprung, den kein
  Flugzeug fliegen könnte. Mit `teleport` unter den Enden und `spawn` unter den Starts – was der Viewer selbst vorschlägt –
  endet eine Route dort, wo der Sprung wegführte, und die nächste beginnt dort, wo er ankam, und keine Linie kreuzt die Karte.
  Eine Route läuft nie über einen Wechsel der Spalte `session`. Eine Positionszeile wird einige Male pro Sekunde geschrieben
  (bei den meisten Telemetrien 10 Hz), was eine glatte Linie ergibt.
- Die Spalte `session` teilt einen Durchgang in seine Runden, Etappen, Leben oder Körper (Elite Dangerous hält so die
  Galaxiezeilen und die Oberflächenzeilen jedes Planeten auseinander). Wähle eine im Viewer aus, um nur diesen Teil
  anzusehen.

Was der Viewer mit den Zeilen macht – Filter, Farben, Abspielen – beschreibt die eigene Dokumentation des Viewers.
Counter-Strike-2-Demo-Sitzungen werden über die `<map>/<match>.parquet` und `<match>.match.json` des Konverters im Viewer
in den Tabs Heatmap und Match geöffnet. Die Positionen von iRacing kommen aus den `.ibt`-Dateien, die in der Sitzung
aufgeführt sind; die liest der Viewer selbst.
