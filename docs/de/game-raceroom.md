---
title: "RaceRoom Racing Experience (Live-Daten)"
nav_order: 37
lang: "de"
source: game-raceroom.md
source_hash: "f3879cd40a67"
nav_exclude: true
search_exclude: true
---
# RaceRoom Racing Experience (Live-Daten) {#raceroom-racing-experience-live-data}

Während du RaceRoom Racing Experience spielst, speichert der Watcher die Daten, die das Spiel selbst herausgibt. So kannst du sie später auf einer Karte im 3DHeat-Viewer ansehen.

*Technische Details: Adapter `raceroom`, Art [`telemetry`](sources-and-rules.md); er läuft, solange `RRRE64.exe` oder `RRRE.exe` läuft, und sucht alle 0,1 s nach neuen Daten.*

## Was aufgezeichnet wird {#what-is-recorded}

- die Position jedes Autos (Welt-XYZ, m) mit 10 Hz, nach Fahrername; das eigene Auto ist markiert; mit Geschwindigkeit und Rennposition; eigener Gang, Gas, Bremse
- Sessionstart mit der Strecke, die das Spiel nennt; Runden je Auto mit Rundenzeit; Zielankünfte; eigene Boxenstopps
- Teleports (zurück an die Box, ein Neustart): `teleport` dort, wo das Auto war, `spawn` dort, wo es jetzt ist
- eigene Runden, Bestrunde, Rennposition, Distanz, Höchstgeschwindigkeit
- die ganze gemeinsame Speicherseite des Spiels in `heat.raw.parquet`, jedes Mal, wenn sie sich ändert
- eigene Vorfallpunkte

## Woher die Daten kommen {#where-it-comes-from}

gemeinsamer Speicher $R3E (r3e.h von Sector3, Version 3)

## So schaltest du es ein {#how-to-switch-it-on}

Du musst nichts einschalten: Der Watcher liest die Quelle so, wie das Spiel oder die Plattform sie bereitstellt.

## So funktioniert es {#how-it-works}

Gemeinsamer Speicher, den Rennspiele für Dashboards veröffentlichen, nur lesend geöffnet – und nie angelegt.

Mehrere Simulatoren geben ihre Telemetrie als benannte Windows-Dateizuordnung heraus, die das Spiel anlegt und die jeder lesen darf: Kunos' `Local\acpmf_*`-Seiten (Assetto Corsa, ACC, AC Rally, AC EVO `Local\acevo_pmf_*`), iRacings `Local\IRSDKMemMapFileName`, RaceRooms `$R3E` und `$pcars2$` von Automobilista 2 / Project CARS 2.

Warum nicht `mmap.mmap(-1, size, tagname=...)`, der übliche Weg in Python: Wenn die Zuordnung noch nicht existiert, *legt* sie diesen Aufruf eine an – hier nur lesend. Ein Spiel, das danach startet, öffnet dann die Zuordnung des Watchers, statt seine eigene anzulegen, und kann nicht darauf schreiben; seine Telemetrie ist tot, bis der Watcher sie wieder loslässt. Der Watcher startet einen Adapter, sobald der Prozess des Spiels erscheint – genau dann hat das Spiel seine Zuordnung noch nicht angelegt. Deshalb öffnet dies mit `OpenFileMappingW`, das nur eine bestehende Zuordnung findet, sie mit `FILE_MAP_READ` abbildet und sonst „noch nicht da“ meldet; die Adapter versuchen es einen Moment später erneut.

Hier kann nichts schreiben: Die Ansicht ist nur lesend abgebildet und wird nur mit `ctypes.string_at` kopiert.

Zwei Spiele werden hier zusätzlich gelesen; jedes Auto auf der Strecke steht in ihren Seiten.

#### RaceRoom Racing Experience - `$R3E` {#raceroom-racing-experience---r3e}

r3e.h von Sector3 (github.com/sector3studios/r3e-api, sample-c/src/r3e.h, Version 3.6), `#pragma pack(1)`. Der Header sagt, wo die Fahrer beginnen und wie groß einer ist (`all_drivers_offset`, `driver_data_size`), deshalb wird der Teil je Fahrer – Name, Platz, Position, Weltposition (float x y z, m), abgeschlossene Runden, aktuelle Rundenzeit, Zielstatus, Boxengasse, Geschwindigkeit – über diese Angaben gelesen. Die eigenen Felder des Spielers (Bestrunde und letzte Runde, Rennposition, Vorfallpunkte, Gang, Pedale, Namen von Strecke und Layout) werden nur an ihren Offsets der Version 3.6 gelesen, und nur wenn `all_drivers_offset` dort steht, wo das Layout von 2008 es hinlegt. Y wird als oben angenommen; der Header sagt es nicht.

Dasselbe Modul bedient auch: [Automobilista 2 (Live-Daten)](game-automobilista-2.md), [Project CARS 2 (Live-Daten)](game-project-cars-2.md).

## Positionen und Achsen {#positions-and-axes}

| | |
|---|---|
| Positionen aufgezeichnet | ja |
| Oben-Achse | `y` |
| Einheiten | Meter; Y nach oben angenommen (r3e.h sagt es nicht) |
| Für den Viewer gespiegelt | keine |
| Einheitenskala (`scale`: der Viewer multipliziert die Positionen damit) | 1 |

Diese Werte landen in der `meta.json` jeder Session (`axes`) und, wenn die Session Positionen hat, im Footer der `heat.parquet`. So dreht und skaliert der 3DHeat-Viewer die Zeilen selbst – siehe [Die Daten](the-data.md).

## Mehrspieler {#multiplayer}

- Als online gespielt markiert (`multiplayer`): **ja**. `games --markdown` zeigt das als „allowed (reads only what the game publishes)“.
- Art `telemetry`: Es liest nur, was das Spiel oder die Plattform herausgibt (ein UDP-Port oder gemeinsamer Speicher, den das Spiel veröffentlicht). Deshalb zeichnet es auch im Online-Spiel auf, nicht nur offline. Die Markierung entscheidet nur, ob Speicher überhaupt gelesen werden darf.
- Speicher: Dieser Adapter liest **nie** den Speicher. Nur `memory`-Adapter lesen Speicher, und nie bei einem Spiel, das als online gespielt markiert ist – siehe [Quellen und Regeln](sources-and-rules.md).

## Aufgezeichnete Statistiken {#statistics-recorded}

Statistik-Schlüssel, die der Code dieses Adapters beim Namen setzt (das `stats` jeder Session in `meta.json` und die Tabelle `stats` in `watcher.sqlite`):

`best_lap`, `distance_km`, `finishes`, `incidents`, `laps`, `pit_stops`, `race_position`, `top_speed_kmh`

Ein Schlüssel in geschweiften Klammern wird zur Laufzeit vervollständigt (`score.{team}` ist ein Schlüssel pro Team). Schlüssel, die der Code aus einer Tabelle der Spielfelder oder aus den eigenen Statistiknamen des Spiels übernimmt, stehen nicht in dieser Liste; „Was aufgezeichnet wird“ oben nennt sie.

## Vollständigkeit {#completeness}

Der Watcher folgt der [Konverterregel](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md) von 3DHeat: Was die Quelle enthält, wird gelesen oder gespeichert, nie weggelassen. Außer den Zeilen wird jedes Paket, jede Seite, jede Zeile und jede Antwort, die der Adapter bekommt, vollständig in der `heat.raw.parquet` der Session gespeichert (Spalten `time`, `ms`, `type`, `used`, `payload`, `text` und alle Felder, die nach Namen behalten werden; `used` markiert, was auch zu Zeilen wurde). `selfCheck.completeness` in `meta.json` zählt jeden `type`; `lost` ist 0.

**Gelesen**

- je Fahrerplatz (nach Offset und Größe aus dem Header): Name, Platz, Zielstatus, Platzierung, Weltposition, abgeschlossene Runden, aktuelle Rundenzeit, Boxengasse, Geschwindigkeit
- die eigenen Felder des Spielers, nur wenn die Seite dem Layout r3e.h 3.6 entspricht: Namen von Strecke und Layout, Sessionart, Rennposition, Bestrunde und letzte Runde, Vorfallpunkte, Gang, Gas, Bremse, der eigene Platz des Spielers
- Offsets aus r3e.h 3.6 von Sector3 erarbeitet und an einer Seite geprüft, die im Test daraus gebaut wurde; noch nicht gegen das Spiel geprüft

**Roh gespeichert**

- `r3e`: der ganze $R3E-Speicherbereich, bei jedem Lesevorgang, dessen Bytes sich von der zuletzt gespeicherten Kopie unterscheiden – jedes Feld von r3e.h: Physik des Spielers (Ausrichtung, Geschwindigkeiten, Beschleunigungen, g-Kräfte), Motor, Kraftstoff, Reifen, Bremsen, Schäden, Flags, Boxenmenü, Sektorzeiten, die ganzen Fahrerdaten jedes Fahrerplatzes (Klasse, Modell, Team, Sektorzeiten, Abstände, Strafen, Reifen)
- `used` ist wahr für eine Seite, die in Zeilen gelesen wurde; falsch für eine Seite in den Menüs, bei Pause, in einer Wiederholung, in einem anderen Layout oder wenn sie gerade geschrieben wurde (`torn` 1); `unchanged_reads` in meta.json zählt die Lesevorgänge, die Byte für Byte der zuvor gespeicherten Kopie entsprechen

**Nicht verfügbar**

- Eingaben und Physik anderer Fahrer: Die Seite gibt nur die des Spielers
- die exakten Rundenzeiten anderer Autos: Ein Platz hat nur seine laufende Rundenzeit, deshalb ist eine Runde die zuletzt gesehene laufende Zeit (auf etwa 0,1 s genau)
- die eigenen Felder des Spielers bei einem anderen Layout als 3.6: roh gespeichert, nicht gelesen, bis sie geprüft sind

**Größe**: Die Seite ist 44 KB groß (r3e.h 3.6; der Speicherbereich ist auf ganze 4-KB-Seiten aufgerundet) und wird bis zu 10-mal pro Sekunde während der Fahrt gelesen: etwa 1,6 GB pro Stunde vor der Komprimierung; leere Fahrerplätze und gleichbleibende Felder komprimiert zstd sehr gut (noch nicht an einer echten Session gemessen)

## Geprüft {#verified}

getestet an einer im Test aus r3e.h 3.6 gebauten Seite (Offsets aus dem offiziellen Header erarbeitet); noch nicht gegen das Spiel getestet; die Rundenzeiten anderer Autos sind die zuletzt gesehene laufende Rundenzeit (auf etwa 0,1 s genau)

## Quelle {#source}

[heat3d_watch/adapters/simracing_shm.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/simracing_shm.py)

<!-- Aus dem Adapter erzeugt von tools/gen_game_pages.py; ändere den Adapter und führe das Skript erneut aus, statt diese Seite zu bearbeiten. -->
