---
title: "Automobilista 2 (Live-Daten)"
nav_order: 6
lang: de
source: game-automobilista-2.md
source_hash: "5e3ca1507524"
nav_exclude: true
search_exclude: true
---
# Automobilista 2 (Live-Daten) {#automobilista-2-live-data}

Während du Automobilista 2 spielst, speichert der Watcher die Daten, die das Spiel selbst herausgibt. So kannst du sie später auf einer Karte im 3DHeat-Viewer ansehen.

*Technische Details: Adapter `automobilista-2`, Art [`telemetry`](sources-and-rules.md); er läuft, solange `AMS2AVX.exe` oder `AMS2.exe` läuft, und sucht alle 0,1 s nach neuen Daten.*

## Was aufgezeichnet wird {#what-is-recorded}

- die Position jedes Autos (Welt-XYZ, m) mit 10 Hz, nach Fahrername; das eigene Auto ist markiert; mit Geschwindigkeit und Rennposition; eigener Gang, Gas, Bremse
- Sessionstart mit der Strecke, die das Spiel nennt; Runden je Auto mit Rundenzeit; Zielankünfte; eigene Boxenstopps
- Teleports (zurück an die Box, ein Neustart): `teleport` dort, wo das Auto war, `spawn` dort, wo es jetzt ist
- eigene Runden, Bestrunde, Rennposition, Distanz, Höchstgeschwindigkeit
- die ganze gemeinsame Speicherseite des Spiels in `heat.raw.parquet`, jedes Mal, wenn sie sich ändert

## Woher die Daten kommen {#where-it-comes-from}

gemeinsamer Speicher $pcars2$ (Aufbau nach SMS SharedMemory.h)

## So schaltest du es ein {#how-to-switch-it-on}

Im Spiel: Optionen > System > Shared Memory: „Project CARS 2“

## So funktioniert es {#how-it-works}

Gemeinsamer Speicher, den Rennspiele für Dashboards veröffentlichen, nur lesend geöffnet – und nie angelegt.

Mehrere Simulatoren geben ihre Telemetrie als benannte Windows-Dateizuordnung heraus, die das Spiel anlegt und die jeder lesen darf: Kunos' `Local\acpmf_*`-Seiten (Assetto Corsa, ACC, AC Rally, AC EVO `Local\acevo_pmf_*`), iRacings `Local\IRSDKMemMapFileName`, RaceRooms `$R3E` und `$pcars2$` von Automobilista 2 / Project CARS 2.

Warum nicht `mmap.mmap(-1, size, tagname=...)`, der übliche Weg in Python: Wenn die Zuordnung noch nicht existiert, *legt* sie diesen Aufruf eine an – hier nur lesend. Ein Spiel, das danach startet, öffnet dann die Zuordnung des Watchers, statt seine eigene anzulegen, und kann nicht darauf schreiben; seine Telemetrie ist tot, bis der Watcher sie wieder loslässt. Der Watcher startet einen Adapter, sobald der Prozess des Spiels erscheint – genau dann hat das Spiel seine Zuordnung noch nicht angelegt. Deshalb öffnet dies mit `OpenFileMappingW`, das nur eine bestehende Zuordnung findet, sie mit `FILE_MAP_READ` abbildet und sonst „noch nicht da“ meldet; die Adapter versuchen es einen Moment später erneut.

Hier kann nichts schreiben: Die Ansicht ist nur lesend abgebildet und wird nur mit `ctypes.string_at` kopiert.

Zwei Spiele werden hier zusätzlich gelesen; jedes Auto auf der Strecke steht in ihren Seiten.

#### Automobilista 2 / Project CARS 2 - `$pcars2$` {#automobilista-2--project-cars-2---pcars2}

SMS' `SharedMemory.h` (liegt im Ordner Support\SharedMemory des Spiels; AMS2: Optionen > System > Shared Memory „Project CARS 2“), `#pragma pack(4)`. `mParticipantInfo[64]` ab Byte 28, je 100 Byte: mIsActive, mName[64], mWorldPosition[3] (m, Y nach oben), mCurrentLapDistance, mRacePosition, mLapsCompleted, mCurrentLap, mCurrentSector; mViewedParticipantIndex (20) ist das eigene Auto; je Teilnehmer mLastLapTimes (9200), mRaceStates (9520), mSpeeds (10800); die eigene mBestLapTime (6716), mLastLapTime (6720), mSpeed (6848), mBrake, mThrottle, mGear; mSequenceNumber (7320) ist ungerade, während das Spiel schreibt. Die Offsets wurden aus zwei unabhängigen Kopien des Headers erarbeitet (das eigene Exemplar des Spiels ist hier nicht installiert), die übereinstimmen.

Beide Seiten werden außerdem vollständig gespeichert (docs/converters.md, „Live sources“): der ganze Speicherbereich, bei jedem Lesevorgang, dessen Bytes sich von der zuletzt gespeicherten Kopie unterscheiden, in der Roh-Beilage der Session unter `type` `r3e` oder `pcars2` – jeder Fahrerplatz und jedes Feld der Struktur, auch die, die hier nicht gelesen werden, damit ein späterer Dekodierer nur die Beilage braucht.

Dasselbe Modul bedient auch: [Project CARS 2 (Live-Daten)](game-project-cars-2.md), [RaceRoom Racing Experience (Live-Daten)](game-raceroom.md).

## Positionen und Achsen {#positions-and-axes}

| | |
|---|---|
| Positionen aufgezeichnet | ja |
| Oben-Achse | `y` |
| Einheiten | Meter |
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

- je Teilnehmer (bis 64): aktiv, Name, Weltposition, Rennposition, abgeschlossene Runden; seine letzte Rundenzeit, sein Rennstatus und seine Geschwindigkeit
- das eigene Auto (mViewedParticipantIndex), Spiel- und Sessionstatus, Ort und Variante der Strecke, Bestrunde und letzte Runde, Geschwindigkeit, Bremse, Gas, Gang; mSequenceNumber, um eine Kopie zu überspringen, die gerade geschrieben wird
- Offsets aus zwei unabhängigen Kopien von SMS' SharedMemory.h, die übereinstimmen, geprüft an einer Seite, die im Test daraus gebaut wurde; noch nicht gegen das Spiel geprüft

**Roh gespeichert**

- `pcars2`: der ganze `$pcars2$`-Speicherbereich – die Struktur reicht weit über die 11.312 Byte hinaus, die hier gelesen werden – bei jedem Lesevorgang, dessen Bytes sich von der zuletzt gespeicherten Kopie unterscheiden: Ausrichtung jedes Teilnehmers, Sektorzeiten, Namen von Auto und Klasse, Boxenmodi und Flags, Physik, Reifen, Federung, Schäden und Wetter des eigenen Autos und alles, was spätere Versionen von Automobilista 2 angehängt haben
- `used` ist wahr für eine Seite, die in Zeilen gelesen wurde; falsch für eine Seite in den Menüs, bei Pause, in einer Wiederholung, in einem anderen Layout oder wenn sie gerade geschrieben wurde (`torn` 1); `unchanged_reads` in meta.json zählt die Lesevorgänge, die Byte für Byte der zuvor gespeicherten Kopie entsprechen

**Nicht verfügbar**

- Eingaben und Physik anderer Teilnehmer: Die Seite gibt nur das angesehene Auto her
- alles, solange die Option für gemeinsamen Speicher im Spiel aus ist (Automobilista 2 schreibt dann nichts)

**Größe**: Der Speicherbereich ist je nach Version des Spiels etwa 20 bis 30 KB groß und wird bis zu 10-mal pro Sekunde während der Fahrt gelesen: grob 0,7 bis 1,1 GB pro Stunde vor der Komprimierung; zstd schrumpft die leeren Teilnehmerplätze und die gleichbleibenden Namen auf einen Bruchteil (noch nicht an einer echten Session gemessen)

## Geprüft {#verified}

getestet an einer im Test gebauten Seite; Offsets aus zwei unabhängigen Kopien von SharedMemory.h, die übereinstimmen, nicht aus der Kopie, die das Spiel mitliefert; noch nicht gegen das Spiel getestet

## Quelle {#source}

[heat3d_watch/adapters/simracing_shm.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/simracing_shm.py)

<!-- Aus dem Adapter erzeugt von tools/gen_game_pages.py; ändere den Adapter und führe das Skript erneut aus, statt diese Seite zu bearbeiten. -->
