---
title: "NVIDIA-Highlights (Plattform)"
nav_order: 34
lang: de
source: game-nvidia-highlights.md
source_hash: "5d45211c0e37"
nav_exclude: true
search_exclude: true
---
# NVIDIA-Highlights (Plattform) {#nvidia-highlights-platform}

Der Watcher speichert, was NVIDIA-Highlights über deine Spiele festhält, damit du deine Geschichte später auf einer Karte im 3DHeat-Viewer ansehen kannst.

*Technische Details: Adapter `nvidia-highlights`, Art [`platform`](sources-and-rules.md); er läuft die ganze Zeit (er wartet nicht, bis ein Spiel startet) und sucht alle 10 s nach neuen Daten.*

## Was aufgezeichnet wird {#what-is-recorded}

- jeder neue Clip, jedes Highlight oder Screenshot: Spiel, Datei, Art, Länge und der Zeitpunkt (Uhrzeit in ms)
- die ID und der Name des Highlights, wenn das Spiel es bei NVIDIA registriert hat
- wo sich der Spieler in diesem Moment befand, wenn ein anderer Adapter dasselbe Spiel zu dieser Zeit aufgezeichnet hat
- Highlight-Anfragen, die GfeSDK-Spiele protokollieren, auch wenn kein Clip gespeichert wird

## Woher die Daten kommen {#where-it-comes-from}

%LOCALAPPDATA%\NVIDIA Corporation\NVIDIA Overlay\UGCTracker.json, GallerySettings.json, Highlights\\&lt;Spiel>\config.json; Clips im Aufnahmeordner (%USERPROFILE%\Videos\NVIDIA\\&lt;Spiel>\\\*.mp4) und &lt;Temp>\Highlights\\&lt;Spiel>; %LOCALAPPDATA%\NVIDIA Corporation\GfeSDK\\&lt;exe>_&lt;pid>.log

## So schaltest du es ein {#how-to-switch-it-on}

NVIDIA App: Sofortwiederholung oder Highlights eingeschaltet, Clips werden per Tastenkürzel oder vom Spiel gespeichert

## So funktioniert es {#how-it-works}

Was der Launcher und der Grafiktreiber über das Spielen festhalten: Steam-Statistiken, Erfolge, Spielzeit und Zeitleisten sowie NVIDIA-Highlights und Clips.

Keine dieser Quellen braucht, dass ein Spiel mitwirkt oder läuft. Deshalb sind die drei Adapter hier immer an und schauen alle paar Sekunden in ein paar Dateien.

#### NVIDIA-Highlights und Clips (`nvidia-highlights`) {#nvidia-highlights-and-clips-nvidia-highlights}

Was NVIDIA App bzw. GeForce Experience speichert, alles unter `%LOCALAPPDATA%\NVIDIA Corporation\NVIDIA Overlay`:
```text
UGCTracker.json      der Galerie-Index: {"UGC": [{id, path, type (video,
                     image), subType (InstantReplay, Normal, ...), date
                     (UTC, wann die Datei geschrieben wurde), profileName, drsName
                     (die exe), shortName, msDuration, ...}], "apps", "info"}
GallerySettings.json settings.currentDirectoryV2 (wohin Clips gespeichert werden),
                     settings.tempDirectory (Highlights warten in
                     <Temp>\Highlights\<Spiel>, bis sie gespeichert werden)
Highlights\<Spiel>\config.json  die Highlight-Arten, die ein Spiel registriert hat:
                     {"highlights": {id: {significance, highlightTags,
                     name: {locale: text}}}, profileName, drsName, shortName}
```
und die Clip-Dateien selbst, `<Aufnahmeordner>\<Spiel>\<Spiel> jjjj.mm.tt -
hh.mm.ss.ff.DVR.mp4` (Screenshots: `<Spiel> Screenshot jjjj.mm.tt - ...png`); die Zeit im Namen ist die Ortszeit, zu der der Clip gespeichert wurde. GfeSDK-Spiele protokollieren ihre Highlight-Aufrufe außerdem in `%LOCALAPPDATA%\NVIDIA Corporation\GfeSDK\<exe>_<pid>.log`.

Was das liefern kann und was nicht: Ein Spiel, das NVIDIA-Highlights unterstützt (GfeSDK), registriert Highlight-Arten einmal – eine ID wie „kill“, eine Bedeutung, Tags, einen Anzeigenamen – und sagt später nur noch „Highlight <id>, von <ms> vor jetzt bis <ms> nach jetzt“. Es gibt keine Positionen, keine Partie oder Runde, keinen Gegner, keine eigenen Daten: Das SDK hat für nichts davon ein Feld. Ein gespeicherter Clip fügt eine Datei, einen Spielnamen, eine Länge und eine Zeit hinzu. Aufgezeichnet wird also „diese Art von Moment, in diesem Spiel, zu dieser Zeit“ – und ein Ort nur, indem die Zeit in der Aufzeichnung eines anderen Adapters für dasselbe Spiel nachgeschlagen wird (`position_at`), was dieser Adapter für jeden aufgezeichneten Clip tut. <https://developer.nvidia.com/highlights>

Jeder Adapter merkt sich, was er schon gesehen hat, in `<Daten>\state\<id>.json`, damit ein Neustart nichts doppelt aufzeichnet.

Jede Session speichert außerdem vollständig, woher ihre Zeilen stammen (Konverterregel von 3DHeat, docs/converters.md im Repository des Viewers), in `heat.raw.parquet`: die Bytes der Statistikdatei und ihres Schemas und den localconfig-Block des Spiels (steam-stats; eine Statistikdatei, die der Dekodierer nicht lesen kann, bekommt eine Session, die nur ihre Bytes enthält), die Kopfzeile der Zeitleisten-Datei und jeden Eintrag als JSON (steam-timeline), jeden Galerie-Eintrag eines Clips, die Highlight-Definitionen des Spiels und jede GfeSDK-Protokollzeile, auch die, die keine Highlight-Anfrage sind (nvidia-highlights).

Dasselbe Modul bedient auch: [Steam-Statistiken (Plattform)](game-steam-stats.md), [Steam Timeline (Plattform)](game-steam-timeline.md).

## Positionen und Achsen {#positions-and-axes}

| | |
|---|---|
| Positionen aufgezeichnet | nur geliehen: der Ort, den eine andere Aufzeichnung desselben Spiels für diesen Moment hat |
| Oben-Achse | `y` |
| Einheiten | Meter |
| Für den Viewer gespiegelt | keine |
| Einheitenskala (`scale`: der Viewer multipliziert die Positionen damit) | 1 |

Diese Werte landen in der `meta.json` jeder Session (`axes`) und, wenn die Session Positionen hat, im Footer der `heat.parquet`. So dreht und skaliert der 3DHeat-Viewer die Zeilen selbst – siehe [Die Daten](the-data.md).

## Mehrspieler {#multiplayer}

- Als online gespielt markiert (`multiplayer`): **nein**. `games --markdown` zeigt das als „single-player“.
- Art `platform`: Es liest nur, was das Spiel oder die Plattform herausgibt (was Steam oder der Grafiktreiber aufbewahrt), deshalb zeichnet es auch im Online-Spiel auf, nicht nur offline. Die Markierung entscheidet nur, ob Speicher überhaupt gelesen werden darf.
- Speicher: Dieser Adapter liest **nie** den Speicher. Nur `memory`-Adapter lesen Speicher, und nie bei einem Spiel, das als online gespielt markiert ist – siehe [Quellen und Regeln](sources-and-rules.md).

## Aufgezeichnete Statistiken {#statistics-recorded}

Statistik-Schlüssel, die der Code dieses Adapters beim Namen setzt (das `stats` jeder Session in `meta.json` und die Tabelle `stats` in `watcher.sqlite`):

`clip_seconds`, `clips`, `placed`, `screenshots`

Ein Schlüssel in geschweiften Klammern wird zur Laufzeit vervollständigt (`score.{team}` ist ein Schlüssel pro Team). Schlüssel, die der Code aus einer Tabelle der Spielfelder oder aus den eigenen Statistiknamen des Spiels übernimmt, stehen nicht in dieser Liste; „Was aufgezeichnet wird“ oben nennt sie.

## Vollständigkeit {#completeness}

Der Watcher folgt der [Konverterregel](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md) von 3DHeat: Was die Quelle enthält, wird gelesen oder gespeichert, nie weggelassen. Außer den Zeilen wird jedes Paket, jede Seite, jede Zeile und jede Antwort, die der Adapter bekommt, vollständig in der `heat.raw.parquet` der Session gespeichert (Spalten `time`, `ms`, `type`, `used`, `payload`, `text` und alle Felder, die nach Namen behalten werden; `used` markiert, was auch zu Zeilen wurde). `selfCheck.completeness` in `meta.json` zählt jeden `type`; `lost` ist 0.

**Gelesen**

- jeder neue Clip und Screenshot: Spiel, Datei, Art, Medium, Länge (aus dem Index, sonst aus dem MP4-Kopf), der Zeitpunkt aus dem Dateinamen, die ID und der Name des Highlights, wenn das Spiel sie registriert hat, und der Ort des Spielers zu diesem Zeitpunkt aus der Aufzeichnung eines anderen Adapters
- GfeSDK-Highlight-Anfragen (jede `Posted Request HL...`, außer den Konfigurationsaufrufen) mit ihrer Zeit

**Roh gespeichert**

- `UGC`: der vollständige Eintrag des Clips aus dem Galerie-Index UGCTracker.json, jedes Feld, das NVIDIA schreibt
- `clip_file`: für einen Clip, den der Index nicht auflistet, Pfad, Größe, Zeit und Ordner der Datei
- `highlights_config`: die Datei `Highlights\<Spiel>\config.json` des Spiels, wie sie geschrieben ist (Bedeutung, Tags, Namen in jeder Sprache), einmal pro Session
- `gfesdk_log`: jede Zeile der GfeSDK-Protokolle, die nach dem ersten Lauf gelesen werden; `used` ist wahr für die Highlight-Anfragen und falsch für den Rest (Konfiguration, Videoeinstellungen, die eigenen Meldungen des SDK)

**Nicht verfügbar**

- die Clips und Screenshots selbst: Video und Bilder bleiben dort, wo NVIDIA sie gespeichert hat; die Zeilen nennen die Datei
- was vor dem ersten Lauf des Adapters war: Es gilt als schon gesehen, damit Jahre an Clips nicht auf einmal zu Sessions werden (`baseline`; False zeichnet sie auf)
- `apps` und `info` in UGCTracker.json und GallerySettings.json: die Einstellungen der App, keine Momente des Spiels; der Aufnahmeordner, den sie nennen, wird verwendet
- Positionen, Runden, Gegner: Das GfeSDK hat dafür kein Feld

**Größe**: etwa 1 KB pro Clip und ein paar KB an Definitionen und Protokollzeilen pro Spielstart; deutlich unter 1 MB pro Stunde

## Geprüft {#verified}

getestet mit einem echten Galerie-Index, Einstellungen, Highlight-Definitionen und Clips einer lokalen Installation; die GfeSDK-Zeilen für Highlight-Anfragen und die Highlight-IDs in Clips sind noch nicht getestet

## Quelle {#source}

[heat3d_watch/adapters/platform.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/platform.py)

<!-- Aus dem Adapter erzeugt von tools/gen_game_pages.py; ändere den Adapter und führe das Skript erneut aus, statt diese Seite zu bearbeiten. -->
