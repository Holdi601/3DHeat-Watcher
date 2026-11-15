---
title: "VALORANT (Wiederholungen)"
nav_order: 45
lang: de
source: game-valorant-replays.md
source_hash: "10a648aabdf1"
nav_exclude: true
search_exclude: true
---
# VALORANT (Wiederholungen) {#valorant-replays}

Nach einem Spiel von VALORANT macht der Watcher aus der Wiederholung, die das Spiel gespeichert hat, Dateien, die du als Statistik und Zeitleiste ansehen kannst.

*Technische Details: Adapter `valorant-replays`, Art [`replay`](sources-and-rules.md); er läuft immer (er wartet nicht darauf, dass ein Spiel startet) und sucht alle 5 s nach neuen Daten.*

## Was aufgezeichnet wird {#what-is-recorded}

- die Karte, die Spiel-ID und die gewählten Agenten; der Infoblock der Wiederholung (Länge, Versionen, Name, Aufnahmezeit, Komprimierungs- und Verschlüsselungsflags)
- die Ereigniszeitleiste des Servers: Abschüsse (Töter und Opfer als Netzwerk-IDs), Beginn der Runden, gelegte, entschärfte und explodierende Spikes, eingesetzte Ultimates, Seitenwechsel – jeweils mit ID und Metadaten
- jeder Abschnitt der Datei vollständig in heat.raw.parquet; nicht decodiert: Positionen, Namen oder Punktestände – sie stehen im verschleierten Datenstrom

## Woher die Daten kommen {#where-it-comes-from}

Wiederholungen, die VALORANT speichert: %LOCALAPPDATA%/VALORANT/Saved/Demos/\*.vrf (nur die Teile, die nicht verschleiert sind)

## So schaltest du es ein {#how-to-switch-it-on}

speichere eine Wiederholung in VALORANT (Karriere > Spiel > Wiederholung herunterladen)

## So funktioniert es {#how-it-works}

League of Legends und Valorant, Wiederholungen: was davon sich unverschlüsselt lesen lässt.

Beide Spiele speichern Wiederholungen auf der Festplatte des Spielers, und beide schützen den Inhalt: Das Spielgeschehen Moment für Moment ist verschleiert, und bei jedem Patch anders, damit es nicht zum Schummeln benutzt werden kann. Um dort hindurchzukommen, müsste man den Code des Spiels selbst auseinandernehmen, was Riots Nutzungsbedingungen untersagen (Nutzungsbedingungen 3.1 und 7.1) – deshalb geschieht es hier nicht. Was jede Datei unverschlüsselt enthält, wird gelesen, und der Rest wird unverändert behalten: jeder Teil der Datei, vollständig, in der `heat.raw.parquet` der Sitzung (Regel des 3DHeat-Konverters, docs/converters.md im Repository des Viewers), gezählt in `selfCheck.completeness` der meta.json.

#### Valorant (.vrf) {#valorant-vrf}

`%LOCALAPPDATA%\VALORANT\Saved\Demos\*.vrf`, eine lokale Wiederholung der Unreal Engine (Layout von vrfkit, Apache-2.0, und ValorantReplayParser, MIT). Unverschlüsselt liegen vor: der Infoblock der Wiederholung (Länge, Netzwerkversion, Changelist, ihr Name, wann sie aufgezeichnet wurde, ob sie komprimiert oder verschlüsselt ist), die Karte, die Spiel-ID und die gewählten Agenten (im Kopf), und die eigene Ereigniszeitleiste des Servers – Abschüsse (Töter und Opfer als Netzwerk-IDs, nicht als Namen), Beginn der Runden, gelegte, entschärfte und explodierende Spikes, eingesetzte Ultimates, Seitenwechsel – jeweils mit Zeit, ID und Metadaten. Positionen, Namen, Punktestände und alles andere stehen im verschleierten Datenstrom (die Chunks mit den Wiederholungsdaten und Checkpoints), der vollständig behalten und nicht gelesen wird.

Dasselbe Modul bedient auch: [League of Legends (Wiederholungen)](game-lol-replays.md).

## Positionen und Achsen {#positions-and-axes}

| | |
|---|---|
| Positionen werden aufgezeichnet | nein |
| Hochachse | `z` |
| Einheiten | VALORANT-Welteinheiten |
| Für den Viewer gespiegelt | nein |
| Einheitenskala (`scale`: der Viewer multipliziert die Positionen damit) | 1 |

Diese Angaben gehen in die `meta.json` (`axes`) jeder Sitzung und, wenn die Sitzung Positionen hat, in die Fußzeile der `heat.parquet`, damit der 3DHeat-Viewer die Zeilen selbst dreht und skaliert – siehe [Die Daten](the-data.md).

## Mehrspieler {#multiplayer}

- Als online gespielt markiert (`multiplayer`): **ja**. `games --markdown` zeigt dies als "allowed (reads only what the game publishes)".
- Art `replay`: Es liest nur, was das Spiel oder die Plattform herausgibt (Wiederholungen und Demos, die das Spiel speichert), daher zeichnet es auch im Online-Spiel auf wie offline; die Markierung entscheidet nur, ob jemals Speicher gelesen werden darf.
- Speicher: Dieser Adapter liest **niemals** Speicher. Nur `memory`-Adapter lesen Speicher, und nie bei einem Spiel, das als online gespielt markiert ist – siehe [Quellen und Regeln](sources-and-rules.md).

## Aufgezeichnete Statistiken {#statistics-recorded}

Statistikschlüssel, die der Code dieses Adapters namentlich setzt (jeweils die `stats` der Sitzung in `meta.json` und die Tabelle `stats` von `watcher.sqlite`):

`kills_in_match`, `map`, `match_seconds`, `rounds`, `spikes_planted`

Ein Schlüssel in geschweiften Klammern wird zur Laufzeit vervollständigt (`score.{team}` ist ein Schlüssel pro Team). Schlüssel, die der Code aus einer Tabelle der Felder des Spiels oder aus den eigenen Statistiknamen des Spiels übernimmt, stehen nicht in dieser Liste; "Was aufgezeichnet wird" oben nennt sie.

## Vollständigkeit {#completeness}

Der Watcher folgt der [Konverterregel](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md) von 3DHeat: Was die Quelle enthält, wird gelesen oder behalten, nie verworfen. Neben den Zeilen wird jedes Paket, jede Seite, jede Zeile oder jede Antwort, die der Adapter empfängt, vollständig in der `heat.raw.parquet` der Sitzung behalten (Spalten `time`, `ms`, `type`, `used`, `payload`, `text`, dann jedes nach Name behaltene Feld; `used` markiert, was auch zu Zeilen wurde), und `selfCheck.completeness` in der `meta.json` zählt jeden `type` – `lost` ist 0.

**Gelesen**

- der Infoblock, jedes Feld (meta.json `vrf`): Dateiversion, benutzerdefinierte Versionen, Länge, Netzwerkversion, Changelist, Name, Live-Flag, Aufnahmezeit, Flags für komprimiert und verschlüsselt, der Schlüssel wie gespeichert
- der Kopf-Chunk: die Karte, die Spiel-ID und die gewählten Agenten (über ihre Form erkannt)
- jeder Ereignis-Chunk: ID, Gruppe, Metadaten, Start- und Endzeit, und aus seinen Daten der Name des Ereignisses, seine Zeit in Sekunden und die Zahlen davor (Netzwerk-IDs von Töter und Opfer) – jeweils eine Zeile

**Roh behalten**

- jeder Chunk vollständig, in Dateireihenfolge (`offset`), sodass die Teile die Datei ergeben: `info`, `header`, `event <group>`, `replay_data`, `checkpoint`, `chunk <n>` für einen Typ, den das Layout nicht benennt, `trailing` für Bytes nach dem letzten vollständigen Chunk

**Nicht verfügbar**

- Positionen, Namen, Punktestände, Fähigkeiten, jeder Rahmen des Spiels: die Chunks mit den Wiederholungsdaten und Checkpoints sind verschleiert; sie zu lesen hieße, den Client auseinanderzunehmen, was Riots Nutzungsbedingungen untersagen. Vollständig behalten, nicht gelesen
- der Inhalt einer verschlüsselten Wiederholung: durchlaufen und vollständig behalten, nichts darin gelesen

**Größe**: der Roh-Speicher ist etwa so groß wie die Wiederholung selbst: der verschleierte Datenstrom lässt sich nicht komprimieren

## Geprüft {#verified}

aus dem Containerlayout gebaut, das vrfkit (Apache-2.0) dokumentiert; nicht an einer echten Wiederholung getestet, da keine bereitstand – der Adapter prüft vor dem Lesen und überspringt, was nicht passt

## Quelle {#source}

[heat3d_watch/adapters/riot_replays.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/riot_replays.py)

<!-- Generated from the adapter by tools/gen_game_pages.py; change the adapter and run it again rather than editing this page. -->
