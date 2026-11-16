---
title: "Steam-Zeitleiste (Plattform)"
nav_order: 43
lang: "de"
source: game-steam-timeline.md
source_hash: "3a502e4ad09e"
nav_exclude: true
search_exclude: true
---
# Steam-Zeitleiste (Plattform) {#steam-timeline-platform}

Der Watcher speichert, was die Steam-Zeitleiste über deine Spiele festhält, damit du deinen Verlauf später als Statistik und Zeitleiste ansehen kannst.

*Technische Details: Adapter `steam-timeline`, Art [`platform`](sources-and-rules.md); er läuft immer (er wartet nicht auf den Start eines Spiels) und sucht alle 10 s nach neuen Daten.*

## Was aufgezeichnet wird {#what-is-recorded}

- eine Sitzung pro Zeitleisten-Datei: ihr Anfang und Ende (session_start, session_end)
- Erfolge, die während des Spielens freigeschaltet wurden, mit Zeit
- Wechsel des Spielmodus (spielen, Vorbereitung, Menüs, Ladebildschirm)
- Ereignisse, die Spiele über ISteamTimeline hinzufügen, mit Titel und Beschreibung, unter dem Namen ihres Symbols
- Spielphasen (ein Match, eine Mission) mit ihren Tags; Ereignisse darin tragen ihre ID als session
- Zustandsbeschreibungen, die das Spiel auf der Zeitleiste zeigt („Runde 3“)
- Steams eigene Aufnahmefehler

## Woher es kommt {#where-it-comes-from}

%STEAM%\userdata\\&lt;account>\gamerecordings\timelines\timeline_&lt;appid>&lt;date>_&lt;time>.json

## So schaltest du es ein {#how-to-switch-it-on}

Steam > Settings > Game Recording: im Hintergrund oder auf Abruf aufnehmen (dann schreibt Steam die Zeitleisten).

## So funktioniert es {#how-it-works}

Was der Launcher und der Grafiktreiber über das Spielen festhalten: Steam-Statistiken, Erfolge, Spielzeit und Zeitleisten sowie die Highlights und Clips von NVIDIA.

Keine dieser Quellen braucht, dass ein Spiel mitarbeitet oder läuft. Deshalb sind die drei Adapter hier immer an und schauen alle paar Sekunden in ein paar Dateien.

#### Steam-Zeitleiste (`steam-timeline`) {#steam-timeline-steam-timeline}

`<Steam>\userdata\<account>\gamerecordings\timelines\timeline_<appid><yyyymmdd>_<hhmmss>.json`, geschrieben während die Steam-Spielaufnahme eingeschaltet ist. Die Datei ist JSON mit Zahlen als Text: "daterecorded" (Unix-Sekunden), "starttime"/"endtime" (ms) und "entries", jeweils {"id", "time" (ms seit daterecorded), "type", ...}. Typen, die in echten Dateien vorkommen:
```text
achievement        achievement_name - Steam fügt diese für jedes Spiel hinzu
gamemode           mode, ein ETimelineGameMode: 1 spielen, 2 Vorbereitung,
                   3 Menüs, 4 Ladebildschirm
error              description - Steams eigene („#GameRecording_RecordingFailed“)
event              AddInstantaneousTimelineEvent/AddRangeTimelineEvent eines Spiels:
                   title, description, icon, priority, duration (ms),
                   possible_clip - „Du hast <name> getötet“ / „mit der <waffe>“
state_description  title - SetTimelineTooltip („Runde 3“)
phase              eine Spanne StartGamePhase..EndGamePhase: duration (ms), tags
                   [{name, icon, group, priority}] (Modus, Karte ...)
```
Das Dateiformat ist das von Steam und nicht dokumentiert. Die Felder sind die Parameter der API. Jeder andere Typ wird unter seinem eigenen Namen mit seinen Feldern aufgezeichnet.
<https://partner.steamgames.com/doc/api/ISteamTimeline>
<https://partner.steamgames.com/doc/features/timeline>

Dasselbe Modul bedient außerdem: [NVIDIA-Highlights (Plattform)](game-nvidia-highlights.md), [Steam-Statistiken (Plattform)](game-steam-stats.md).

## Positionen und Achsen {#positions-and-axes}

| | |
|---|---|
| Positionen aufgezeichnet | nein |
| Hochachse | `y` |
| Einheiten | Meter |
| Für den Viewer gespiegelt | keine |
| Einheitenfaktor (`scale`: der Viewer multipliziert die Positionen damit) | 1 |

Diese Werte stehen in der `meta.json` jeder Sitzung (`axes`) und, wenn die Sitzung Positionen hat, im Fuß der `heat.parquet`. So dreht und skaliert der 3DHeat-Viewer die Zeilen selbst. Siehe [Die Daten](the-data.md).

## Mehrspieler {#multiplayer}

- Als Online-Spiel markiert (`multiplayer`): **nein**. `games --markdown` zeigt das als „Einzelspieler“.
- Art `platform`: Er liest nur, was das Spiel oder die Plattform herausgibt (was Steam oder der Grafiktreiber festhält). Deshalb zeichnet er auch im Online-Spiel auf, nicht nur offline. Die Markierung entscheidet nur, ob jemals Speicher gelesen werden darf.
- Speicher: **nie** von diesem Adapter gelesen. Nur Adapter der Art `memory` lesen Speicher, und nie bei einem als Online-Spiel markierten Spiel. Siehe [Quellen und Regeln](sources-and-rules.md).

## Erfasste Statistiken {#statistics-recorded}

Statistikschlüssel, die der Code dieses Adapters namentlich setzt (`stats` jeder Sitzung in `meta.json` und die Tabelle `stats` der `watcher.sqlite`):

`achievements`, `game_mode_changes`, `phases`, `recorded_seconds`, `timeline_events`

Ein Schlüssel in geschweiften Klammern wird zur Laufzeit ergänzt (`score.{team}` ist ein Schlüssel pro Team). Schlüssel, die der Code aus einer Tabelle der Spielfelder oder aus den eigenen Statistiknamen des Spiels nimmt, stehen nicht in dieser Liste. Was aufgezeichnet wird, steht oben und nennt sie.

## Vollständigkeit {#completeness}

Der Watcher folgt der [Konverterregel](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md) von 3DHeat: Was die Quelle enthält, wird gelesen oder behalten, nie verworfen. Neben den Zeilen wird jedes Paket, jede Seite, jede Zeile und jede Antwort, die der Adapter erhält, ganz in der `heat.raw.parquet` der Sitzung behalten (Spalten `time`, `ms`, `type`, `used`, `payload`, `text`, dazu jedes nach Namen behaltene Feld; `used` markiert, was auch zu Zeilen wurde). Der `selfCheck.completeness` in `meta.json` zählt jeden `type`. `lost` ist 0.

**Gelesen**

- jeder Eintrag einmal, als Zeile zu seiner Zeit: sein Typ, jedes einfache Feld (Titel, Beschreibung, Symbol, Priorität, Dauer, possible_clip, Name des Erfolgs, Modus ...), die Tags einer Phase nach Gruppe, der Anzeigename des Erfolgs aus dem Statistikschema; Anfang und Ende der Datei

**Roh behalten**

- jeder Eintrag ganz als JSON unter Steams eigenem `type` (`gamemode`, `achievement`, `event`, `state_description`, `phase`, `error`, jeder andere): verschachtelte Felder, das Symbol und die Priorität eines Tags, alles was ein späterer Steam hinzufügt, stehen nur hier
- `timeline`: die eigenen Felder der Datei (daterecorded, starttime, endtime, alle anderen), wenn die Sitzung öffnet und wenn sie sich ändern

**Nicht verfügbar**

- die Aufnahme selbst (Video): Steam bewahrt sie in eigenen Ordnern auf; die Sitzung verweist auf die Zeitleisten-Datei über ihren Namen
- das Lesen einer Datei, die Steam gerade schreibt und die selbst mit abgeschlossenem Ende nicht zu lesen ist: wird gezählt (`bad` im Zustand des Adapters) und beim nächsten Änderungsschritt erneut gelesen, dann werden ihre Einträge übernommen

**Größe**: einige hundert Einträge zu 100 bis 300 Bytes pro Stunde Spielzeit. Insgesamt weit unter 1 MB pro Stunde.

## Geprüft {#verified}

Getestet an echten Zeitleisten-Dateien aus einer lokalen Installation: Erfolg, Spielmodus, Fehler sowie die eigenen Ereignis-, Zustandsbeschreibungs- und Phasen-Einträge der Spiele. Das Dateiformat selbst ist nicht dokumentiert.

## Quelle {#source}

[heat3d_watch/adapters/platform.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/platform.py)

<!-- Generated from the adapter by tools/gen_game_pages.py; change the adapter and run it again rather than editing this page. -->
