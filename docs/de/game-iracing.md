---
title: "iRacing (Live-Daten)"
nav_order: 28
lang: de
source: game-iracing.md
source_hash: "894d9bc4081f"
nav_exclude: true
search_exclude: true
---
# iRacing (Live-Daten) {#iracing-live-data}

Während du iRacing spielst, speichert der Watcher die Daten, die das Spiel selbst ausgibt, damit du sie dir später als Statistik und Zeitleiste ansehen kannst.

*Technische Details: Adapter `iracing`, Art [`telemetry`](sources-and-rules.md); er läuft, solange `iRacingSim64DX11.exe` oder `iRacingSim64.exe` läuft, und sucht alle 0,1 s nach neuen Daten.*

## Was aufgezeichnet wird {#what-is-recorded}

- das Fahren mit 5 Hz ohne Position (iRacing liefert live keine): Geschwindigkeit, Gang, Gas, Bremse, Runde, Anteil an der Runde, Platzierung im Rennen und in der Klasse, Vorfälle
- Sitzungsstart, Ein- und Aussteigen, Ein- und Ausfahrt in die Boxengasse, Runden mit Rundenzeit, Vorfälle mit ihren Strafpunkten, Zielflagge, Ziel
- die .ibt-Telemetriedateien, die während der Sitzung geschrieben werden (Breite, Länge, Höhe – der Viewer liest sie)
- Runden, Bestrunde, Vorfälle, Platzierung im Rennen, Boxenstopps, Distanz, Höchstgeschwindigkeit
- der gesamte gemeinsame Speicher in `heat.raw.parquet`: Kopf, Variablenköpfe, Sitzungsinformationen, jede gelesene Telemetriezeile

## Woher die Daten kommen {#where-it-comes-from}

gemeinsamer Speicher Local\IRSDKMemMapFileName (das iRacing SDK); .ibt-Dateien in %USERPROFILE%\Documents\iRacing\telemetry

## So schaltest du es ein {#how-to-switch-it-on}

Für die Live-Daten musst du nichts tun. Für Positionen: im Auto die Telemetrie aufzeichnen (Alt+L) oder irsdkLog=1 in app.ini setzen

## So funktioniert es {#how-it-works}

iRacing, live: der gemeinsame Speicher des iRacing SDK, nativ gelesen.

iRacing veröffentlicht seine Telemetrie für Apps in einer benannten Dateizuordnung,
`Local\IRSDKMemMapFileName`, die der Simulator beim Laufen anlegt (und bei jeder Aktualisierung
`Local\IRSDKDataValidEvent` signalisiert, was hier nicht nötig ist: der Watcher schaut zehnmal pro Sekunde nach).
Das Layout ist die `irsdk_defines.h` des SDK, auch von pyirsdk (MIT) befolgt – hier aus diesen Fakten neu geschrieben:

```text
irsdk_header (little-endian int32s)
    0 ver, 4 status (bit 0: connected), 8 tickRate,
    12 sessionInfoUpdate, 16 sessionInfoLen, 20 sessionInfoOffset,
    24 numVars, 28 varHeaderOffset, 32 numBuf, 36 bufLen, 40 pad[2],
    48 varBuf[4]: { tickCount, bufOffset, pad[2] } (16 bytes each)
irsdk_varHeader (144 bytes, numVars of them at varHeaderOffset)
    0 type (0 char, 1 bool, 2 int, 3 bitfield, 4 float, 5 double),
    4 offset (into a line), 8 count, 12 countAsTime + 3 pad,
    16 name[32], 48 desc[64], 112 unit[32]
session info: YAML text at sessionInfoOffset, rewritten when
    sessionInfoUpdate changes (track, sessions, drivers)
```

Der Simulator schreibt `numBuf` Zeilen reihum; die neueste ist die mit dem höchsten
tickCount, und eine Zeile wird erneut gelesen, wenn sich ihr tickCount während des
Kopierens geändert hat.

Live-Daten haben keine Weltposition – Breite, Länge und Höhe stehen nur in den
.ibt-Dateien, die iRacing unter `Documents\iRacing\telemetry` protokolliert (Alt+L im
Auto oder `irsdkLog=1`), und die liest der 3DHeat-Viewer selbst. Deshalb zeichnet dies
das Fahren als Ereignisse ohne Koordinaten auf – Geschwindigkeit, Runde, der Anteil der
Runde, Platzierung im Rennen, Vorfälle – dazu Runden, Vorfälle, Boxenstopps und die
Zielflagge, und am Ende die .ibt-Dateien, die während der Sitzung geschrieben wurden,
als Ereignisse `telemetry_file`, damit der Viewer sie öffnen kann.

Neben den Zeilen wird der gesamte Speicherabbild in der Roh-Beilage der Sitzung
(`heat.raw.parquet`) behalten: der feste Teil des Kopfes (`header`, jedes Mal, wenn er sich
ändert), die Variablenköpfe (`var_headers`, vollständig und in `text` als JSON, jedes Mal,
wenn sich das Layout ändert), die Sitzungsinformation als YAML (`session_info`, ihr Text,
wenn sich `sessionInfoUpdate` bewegt) und die neueste Telemetriezeile (`telemetry`, jede
Variable darin, bei jedem Lesevorgang, der einen neuen Tick findet). Die Variablenköpfe
und eine Zeile sind alles, was ein späterer Decoder braucht, um jede Variable zu lesen.

Quelle: das iRacing SDK (irsdk_defines.h, Dokumentation im Forum "iRacing SDK");
kutu/pyirsdk (MIT) zur Bestätigung der Offsets.

## Positionen und Achsen {#positions-and-axes}

| | |
|---|---|
| Positionen werden aufgezeichnet | nein |
| Hochachse | `y` |
| Einheiten | keine Positionen live; die .ibt-Dateien enthalten Breite/Länge/Höhe |
| Für den Viewer gespiegelt | nein |
| Einheitenskala (`scale`: der Viewer multipliziert die Positionen damit) | 1 |

Diese Angaben gehen in die `meta.json` (`axes`) jeder Sitzung und, wenn die Sitzung Positionen hat, in die Fußzeile der `heat.parquet`, damit der 3DHeat-Viewer die Zeilen selbst dreht und skaliert – siehe [Die Daten](the-data.md).

## Mehrspieler {#multiplayer}

- Als online gespielt markiert (`multiplayer`): **ja**. `games --markdown` zeigt dies als "allowed (reads only what the game publishes)".
- Art `telemetry`: Es liest nur, was das Spiel oder die Plattform herausgibt (ein UDP-Port oder gemeinsamer Speicher, den das Spiel veröffentlicht), daher zeichnet es auch im Online-Spiel auf wie offline; die Markierung entscheidet nur, ob jemals Speicher gelesen werden darf.
- Speicher: Dieser Adapter liest **niemals** Speicher. Nur `memory`-Adapter lesen Speicher, und nie bei einem Spiel, das als online gespielt markiert ist – siehe [Quellen und Regeln](sources-and-rules.md).

## Aufgezeichnete Statistiken {#statistics-recorded}

Statistikschlüssel, die der Code dieses Adapters namentlich setzt (jeweils die `stats` der Sitzung in `meta.json` und die Tabelle `stats` von `watcher.sqlite`):

`best_lap`, `distance_km`, `finishes`, `incidents`, `laps`, `pit_stops`, `race_position`, `sessions`, `top_speed_kmh`

Ein Schlüssel in geschweiften Klammern wird zur Laufzeit vervollständigt (`score.{team}` ist ein Schlüssel pro Team). Schlüssel, die der Code aus einer Tabelle der Felder des Spiels oder aus den eigenen Statistiknamen des Spiels übernimmt, stehen nicht in dieser Liste; "Was aufgezeichnet wird" oben nennt sie.

## Vollständigkeit {#completeness}

Der Watcher folgt der [Konverterregel](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md) von 3DHeat: Was die Quelle enthält, wird gelesen oder behalten, nie verworfen. Neben den Zeilen wird jedes Paket, jede Seite, jede Zeile oder jede Antwort, die der Adapter empfängt, vollständig in der `heat.raw.parquet` der Sitzung behalten (Spalten `time`, `ms`, `type`, `used`, `payload`, `text`, dann jedes nach Name behaltene Feld; `used` markiert, was auch zu Zeilen wurde), und `selfCheck.completeness` in der `meta.json` zählt jeden `type` – `lost` ist 0.

**Gelesen**

- aus der neuesten Telemetriezeile: Sitzungszeit, Nummer, Zustand und ID, auf der Strecke, Wiederholung, Runde, abgeschlossene Runden, Anteil und Meter der Runde, letzte und beste Runde, Geschwindigkeit, Gang, Gas, Bremse, Drehzahl, Boxengasse, Streckenbelag, Platzierung im Rennen und in der Klasse, eigene Vorfallzahl (die Zeilen `driving` mit 5 Hz und die Ereignisse)
- jetzt auch auf den Zeilen `driving`: `steering_angle`, `yaw`, `yaw_north`, `pitch`, `roll` (Grad, aus den Radiant des Simulators – nur wenn der Variablenkopf die Einheit als rad angibt), `fuel_l` (Einheit l), `lat_accel` und `lon_accel` (Einheit m/s^2)
- aus der YAML der Sitzungsinformation: der Fahrzeugindex des Spielers, Strecke und Konfiguration, Sitzungsarten, Name, Auto, Team und Nummer jedes Fahrers (Zeilen session_start, meta.json)
- in den Tests gegen einen aus irsdk_defines.h gebauten Block geprüft; noch nicht gegen den Simulator

**Roh behalten**

- `telemetry`: die neueste Zeile vollständig, jede Variable, die der Simulator veröffentlicht (die CarIdx-Arrays jedes Autos, Reifen, Federung, die hochfrequenten `_ST`-Arrays, wo der Simulator sie hat ...), bei jedem Lesevorgang, der einen neuen Tick findet; `tick` die Tickzahl des Simulators; `used` ist falsch, solange eine Wiederholung läuft
- `var_headers`: die Variablenköpfe vollständig (je 144 Bytes) und in `text` als JSON (Name, Typ, Offset, Anzahl, Einheit, Beschreibung), jedes Mal, wenn sich das Layout ändert – genug, um jede Variable jeder behaltenen Zeile zu lesen
- `session_info`: die YAML-Text vollständig, jedes Mal, wenn sich ihr Aktualisierungszähler bewegt (Wochenende, Sitzungen und Ergebnisse, Fahrer, Fahrzeugeinstellung, Funk, Kameralisten)
- `header`: der 112-Byte-Kopf von iRacing vollständig, jedes Mal, wenn er sich ändert (Version, Status, Tickrate, Offsets, die Ticks der Zeilen)

**Nicht verfügbar**

- eine Weltposition live: der gemeinsame Speicher hat keine; Breite, Länge und Höhe stehen nur in den .ibt-Dateien (bei eingeschalteter Protokollierung), die der Viewer liest – der Watcher nennt die während der Sitzung geschriebenen
- die Ticks zwischen zwei Lesevorgängen: der Simulator schreibt 60 Zeilen pro Sekunde in 3 oder 4 Plätze, und der Watcher liest zehnmal pro Sekunde, daher werden die meisten Ticks überschrieben, bevor sie gelesen werden können; die .ibt-Datei hat jeden Tick, wenn die Protokollierung eingeschaltet ist

**Größe**: eine Telemetriezeile ist einige KB (etwa 5 bis 10 KB mit allen Arrays jedes Autos), bis zu 10-mal pro Sekunde behalten, dazu der Kopf (112 Bytes) genauso oft und die YAML der Sitzungsinformation (zehn KB) jedes Mal, wenn sie sich ändert: etwa 0,2 bis 0,4 GB pro Stunde auf der Strecke vor der Komprimierung; zstd bringt es auf einen Bruchteil (noch nicht an einer echten Sitzung gemessen)

## Geprüft {#verified}

an einem im Test aus dem irsdk-Layout gebauten Speicherblock getestet; nicht gegen den Simulator getestet

## Quelle {#source}

[heat3d_watch/adapters/iracing.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/iracing.py)

<!-- Generated from the adapter by tools/gen_game_pages.py; change the adapter and run it again rather than editing this page. -->
