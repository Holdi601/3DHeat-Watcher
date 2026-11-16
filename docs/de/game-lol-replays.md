---
title: "League of Legends (Wiederholungen)"
nav_order: 30
lang: "de"
source: game-lol-replays.md
source_hash: "6a86dc8a45bb"
nav_exclude: true
search_exclude: true
---
# League of Legends (Wiederholungen) {#league-of-legends-replays}

Nach einem Spiel von League of Legends macht der Watcher aus der Wiederholung, die das Spiel gespeichert hat, Dateien, die du auf einer Karte im 3DHeat-Viewer ansehen kannst.

*Technische Details: Adapter `lol-replays`, Art [`replay`](sources-and-rules.md); er läuft immer (er wartet nicht darauf, dass ein Spiel startet) und sucht alle 5 s nach neuen Daten.*

## Was aufgezeichnet wird {#what-is-recorded}

- der Champion, die Rolle, das Team, Abschüsse, Tode, Assists, Gold, Schaden an Champions und das Ergebnis jedes Spielers sowie jede andere Zahl der Endstatistik
- deine eigene Zeile als Statistik, und deine Zeilen als deine markiert (meta.json `player`), mit deiner Riot-ID in den Einstellungen
- mit deinem eigenen Riot-API-Schlüssel: die Position jedes Spielers jede Minute mit den Statistiken der Minute und jedes Ereignis der Zeitleiste (Abschüsse dort, wo sie passierten, Gebäude, Monster, Wards, Gegenstände, Fähigkeiten), zur Uhrzeit, die die Zeitleiste angibt
- jeder Teil der Wiederholungsdatei vollständig in heat.raw.parquet; nicht decodiert: das Spielgeschehen Moment für Moment, das gegen Schummeln verschlüsselt und verschleiert ist

## Woher die Daten kommen {#where-it-comes-from}

Wiederholungen, die der League-Client speichert: %USERPROFILE%/Documents/League of Legends/Replays/\*.rofl (nur die einfachen Metadaten am Spielende); mit deinem eigenen Riot-API-Schlüssel die offizielle Zeitleiste des Spiels aus der Match-V5-API von Riot

## So schaltest du es ein {#how-to-switch-it-on}

Speichere eine Wiederholung im League-Client (Spielverlauf > Herunterladen) und installiere den Leser: github.com/Holdi601/3DHeat-Ext-Riot (`heat3d-riot-replays`); für Positionen setze riot_api_key und riot_platform mit `config --set`

Einstellungen aus Umgebungsvariablen:

- `HEAT3D_RIOT_REPLAYS`: der Ordner des Lesers (ein Klon oder entpacktes Release), wenn er nicht installiert ist oder nicht neben dem Watcher liegt

## So funktioniert es {#how-it-works}

League of Legends und Valorant, Wiederholungen: was davon sich unverschlüsselt lesen lässt.

Beide Spiele speichern Wiederholungen auf der Festplatte des Spielers, und beide schützen den Inhalt: Das Spielgeschehen Moment für Moment ist verschleiert, und bei jedem Patch anders, damit es nicht zum Schummeln benutzt werden kann. Dieser Teil wird nirgends in 3DHeat dekodiert. Was jede Datei unverschlüsselt enthält, wird gelesen, und der Rest wird unverändert behalten: jeder Teil der Datei, vollständig, in der `heat.raw.parquet` der Sitzung (Regel des 3DHeat-Konverters, docs/converters.md im Repository des Viewers), gezählt in `selfCheck.completeness` der meta.json.

Der Watcher liest die Dateien nicht selbst: Das tut ein externer Leser (3DHeat Riot, github.com/Holdi601/3DHeat-Ext-Riot, `exporters/ext/riot-replays`, Befehl `heat3d-riot-replays`), ein eigenes Projekt. Auf dem PATH, installiert oder neben dem Watcher gefunden, liest er jedes neue Replay; fehlt er, sagt der Watcher einmal, wie man ihn installiert. Was der Leser liest, schreibt der Watcher in die Sitzung; die Match-V5-Zeitleiste unten holt der Watcher selbst, weil sie nicht in der Datei steht.

#### League of Legends (.rofl) {#league-of-legends-rofl}

`%USERPROFILE%\Documents\League of Legends\Replays\*.rofl`. Beide Containerversionen tragen die Endstatistik als unverschlüsseltes JSON (`statsJson`): für jeden der zehn Spieler den Champion, Abschüsse, Tode, Assists, Gold, Schaden an Champions, Gegenstände, Team, Rolle, Sieg, ihre Riot-ID und jede andere Zahl, die das Spiel summiert (über hundert pro Spieler); alle werden zur Zeile `player_result` des Spielers. ROFL1 (Patch 14.9 und früher) hat sie nach einem festen Kopf (`RIOT\0\0`, einer 256-Byte-Signatur, dann die Längen); ROFL2 (ab 14.11, `RIOT\2\0`) am Dateiende, seine Länge in den letzten vier Bytes (laut einem Riot-Ingenieur, ReplayBook-Ausgabe 299). Der Nutzdatenkopf von ROFL1 (Spiel-ID, Länge, Anzahl der Chunks und Keyframes, Länge des Chunk-Schlüssels) und seine Tabelle der Chunks (ID, Typ, Länge, nächster Chunk, Offset) liegen offen und werden gelesen; die Chunks selbst sind verschlüsselt und werden unverändert und ungelesen vollständig behalten.

Positionen kommen nicht aus der Datei. Mit einem eigenen Riot-Entwicklerschlüssel des Spielers (`riot_api_key` in den Einstellungen; ein persönlicher Schlüssel ist genau dafür gedacht, "showing (self) player stats") wird die offizielle Zeitleiste des Spiels aus der Match-V5-API von Riot geholt: die Position jedes Spielers einmal pro Minute mit allem, was der Rahmen der Minute über ihn sagt (Gold, Erfahrung, Stufe, Minions, Champion- und Schadensstatistik), und jedes Ereignis der Zeitleiste – Abschüsse, Gebäude, Elite-Monster, Wards, Gegenstände, Fähigkeiten, Stufen – als eigene Zeile, dort, wo es passiert ist, wenn es einen Ort hat. Ohne Schlüssel wird nichts geholt und nichts gesendet.

Dasselbe Modul bedient auch: [VALORANT (Wiederholungen)](game-valorant-replays.md).

## Positionen und Achsen {#positions-and-axes}

| | |
|---|---|
| Positionen werden aufgezeichnet | ja |
| Hochachse | `y` |
| Einheiten | Karteneinheiten des Summoner's Rift (etwa 15000 von Rand zu Rand) |
| Für den Viewer gespiegelt | nein |
| Einheitenskala (`scale`: der Viewer multipliziert die Positionen damit) | 1 |

Diese Angaben gehen in die `meta.json` (`axes`) jeder Sitzung und, wenn die Sitzung Positionen hat, in die Fußzeile der `heat.parquet`, damit der 3DHeat-Viewer die Zeilen selbst dreht und skaliert – siehe [Die Daten](the-data.md).

## Mehrspieler {#multiplayer}

- Als online gespielt markiert (`multiplayer`): **ja**. `games --markdown` zeigt dies als "allowed (reads only what the game publishes)".
- Art `replay`: Es liest nur, was das Spiel oder die Plattform herausgibt (Wiederholungen und Demos, die das Spiel speichert), daher zeichnet es auch im Online-Spiel auf wie offline; die Markierung entscheidet nur, ob jemals Speicher gelesen werden darf.
- Speicher: Dieser Adapter liest **niemals** Speicher. Nur `memory`-Adapter lesen Speicher, und nie bei einem Spiel, das als online gespielt markiert ist – siehe [Quellen und Regeln](sources-and-rules.md).

## Aufgezeichnete Statistiken {#statistics-recorded}

Statistikschlüssel, die der Code dieses Adapters namentlich setzt (jeweils die `stats` der Sitzung in `meta.json` und die Tabelle `stats` von `watcher.sqlite`):

`champion`, `game_seconds`, `won`

Ein Schlüssel in geschweiften Klammern wird zur Laufzeit vervollständigt (`score.{team}` ist ein Schlüssel pro Team). Schlüssel, die der Code aus einer Tabelle der Felder des Spiels oder aus den eigenen Statistiknamen des Spiels übernimmt, stehen nicht in dieser Liste; "Was aufgezeichnet wird" oben nennt sie.

## Vollständigkeit {#completeness}

Der Watcher folgt der [Konverterregel](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md) von 3DHeat: Was die Quelle enthält, wird gelesen oder behalten, nie verworfen. Neben den Zeilen wird jedes Paket, jede Seite, jede Zeile oder jede Antwort, die der Adapter empfängt, vollständig in der `heat.raw.parquet` der Sitzung behalten (Spalten `time`, `ms`, `type`, `used`, `payload`, `text`, dann jedes nach Name behaltene Feld; `used` markiert, was auch zu Zeilen wurde), und `selfCheck.completeness` in der `meta.json` zählt jeden `type` – `lost` ist 0.

**Gelesen**

- das Metadaten-JSON: Spieldauer, Version, Ids des letzten Chunks und Keyframes sowie `statsJson` – jedes Feld der Endstatistik jedes Spielers auf dessen Zeile `player_result` (Zahlen, die als Text stehen, werden als Zahlen gelesen)
- ROFL1: der Längenblock, der Nutzdatenkopf (Spiel-ID, Spieldauer, Anzahl der Keyframes und Chunks, Start- und Spiel-Start-Chunk-IDs, Keyframe-Intervall, der Chunk-Schlüssel wie gespeichert) und die Chunk-Tabelle (ID, Typ, Länge, nächster Chunk, Offset) – in meta.json unter `rofl` und im `text` der Roh-Zeilen
- ROFL2: die Versionszeichenkette
- die Match-V5-Zeitleiste (nur mit eigenem API-Schlüssel): jeder Teilnehmerrahmen als Zeile `position` (oder `participant_frame` ohne Ort) mit allen seinen Feldern flach ausgeschrieben (`championStats.armor`, `damageStats.totalDamageDone`, `currentGold`, `xp`, ...); jedes Ereignis als Zeile, benannt nach seinem Typ, dort platziert, wo es eine `position` hat; CHAMPION_KILL als Abschuss und Tod

**Roh behalten**

- jeder Teil der .rofl vollständig, in Dateireihenfolge (`offset`), sodass die Teile die Datei ergeben: `magic`, `signature`, `lengths`, `metadata`, `payload_header`, `chunk_header`, `chunk`, `keyframe` (ROFL1); `body`, `metadata`, `metadata_length` (ROFL2); jeder Bereich, den kein Teil abdeckt, als `unknown`
- die Zeitleiste vollständig: `timeline <type>` für jedes Ereignis, `timeline participantFrame` für den Rahmen jedes Spielers (`participant` seine ID), `timeline` für den Rest

**Nicht verfügbar**

- das Spiel selbst (Positionen, Fähigkeiten, jede Einheit, Moment für Moment): die Chunks von ROFL1 und der Body von ROFL2 sind verschlüsselt, und die Pakete darin werden bei jedem Patch verschleiert. Vollständig behalten, nicht gelesen
- Positionen ohne deinen eigenen Riot-API-Schlüssel: die Datei hat keine im Klartext

**Größe**: der Roh-Speicher ist etwa so groß wie die Wiederholung selbst: die verschlüsselten Chunks lassen sich nicht komprimieren

## Geprüft {#verified}

der Leser (heat3d-riot-replays) an Dateien getestet, die nach den Layouts in roflxd.cs (MIT) gebaut wurden; die Zeitleiste am dokumentierten JSON von Match-V5; es stand keine echte Wiederholung zum Vergleich bereit

## Quelle {#source}

[heat3d_watch/adapters/riot_replays.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/riot_replays.py)

<!-- Generated from the adapter by tools/gen_game_pages.py; change the adapter and run it again rather than editing this page. -->
