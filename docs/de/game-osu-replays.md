---
title: "osu! (Wiederholungen)"
nav_order: 35
lang: de
source: game-osu-replays.md
source_hash: "9a1c74c4d5e0"
nav_exclude: true
search_exclude: true
---
# osu! (Wiederholungen) {#osu-replays}

Nach einer Partie von osu! macht der Watcher aus der Wiederholung, die das Spiel gespeichert hat, Dateien, die du auf einer Karte im 3DHeat-Viewer ansehen kannst.

*Technische Details: Adapter `osu-replays`, Art [`replay`](sources-and-rules.md); er läuft die ganze Zeit (er wartet nicht, bis ein Spiel startet) und sucht alle 5 s nach neuen Daten.*

## Was aufgezeichnet wird {#what-is-recorded}

- der Weg des Cursors über das Spielfeld (x 0..512, y 0..384) und die gehaltenen Tasten, jedes Bild
- Punktzahl, Combo, 300er/100er/50er/Gekis/Katus/Fehlschläge, Genauigkeit, Mods, Full Combo
- der Lebensbalken über das Spiel, die Hashes der Beatmap und der Wiederholung, der Zufallsstartwert, die ID des Online-Ergebnisses

## Woher die Daten kommen {#where-it-comes-from}

Wiederholungen, die osu! (Stable) speichert: %LOCALAPPDATA%/osu!/Data/r/\*.osr (jede Partie) und osu!/Replays/\*.osr (exportiert)

## So schaltest du es ein {#how-to-switch-it-on}

Du musst nichts einschalten: Der Watcher liest die Quelle so, wie das Spiel oder die Plattform sie bereitstellt.

## So funktioniert es {#how-it-works}

Wiederholungen und Demos: was ein Spiel von einer Partie speichert, nach Ende der Partie umgewandelt.

Eine Wiederholung enthält alles, was eine Live-Oberfläche bei Mehrspielerspielen zurückhält – die Position jedes Spielers, jeden Abschuss dort, wo er passiert ist – und sie ist eine Datei, die das Spiel für seine Spieler schreibt. Deshalb berührt das Lesen nichts im Spiel. Der Watcher schaut in die Ordner, in denen Spiele sie speichern, wartet, bis eine neue Datei nicht mehr wächst (sonst schreibt das Spiel noch daran), und wandelt sie in einem Arbeitsthread um, damit eine lange Umwandlung den Rest des Watchers nicht aufhält.

Die Wiederholungen, die beim ersten Blick auf einen Ordner schon darin liegen, werden nur vorgemerkt, nicht umgewandelt; sonst würde ein Spieler mit jahrelangen Demos den Watcher einen Tag lang beschäftigt finden. `python -m heat3d_watch replays <Adapter> [Ordner]` wandelt die vorhandenen auf Anfrage um.

#### osu! {#osu}

osu! (Stable) speichert jede Partie in `osu!/Data/r/*.osr` und die exportierten in `osu!/Replays/`. Der Watcher liest sie selbst, nach dem Format, das das osu!-Wiki veröffentlicht: der Weg des Cursors und die Tasten jedes Bild, die Punktzeile, der Lebensbalken, der Startwert und die Ergebnis-ID; die Datei wird vollständig daneben, Teil für Teil, in der `heat.raw.parquet` der Session gespeichert.

Dasselbe Modul bedient auch: [Counter-Strike 2 (Wiederholungen)](game-cs2-demos.md), [Dota 2 (Wiederholungen)](game-dota-replays.md), [Squad (Wiederholungen)](game-squad-demos.md), [War Thunder (Wiederholungen)](game-warthunder-replays.md), [World of Tanks (Wiederholungen)](game-wot-replays.md), [World of Warships (Wiederholungen)](game-wows-replays.md).

## Positionen und Achsen {#positions-and-axes}

| | |
|---|---|
| Positionen aufgezeichnet | ja |
| Oben-Achse | `y` |
| Einheiten | osu!-Pixel (Spielfeld 512 x 384) |
| Für den Viewer gespiegelt | `z` |
| Einheitenskala (`scale`: der Viewer multipliziert die Positionen damit) | 1 |

Diese Werte landen in der `meta.json` jeder Session (`axes`) und, wenn die Session Positionen hat, im Footer der `heat.parquet`. So dreht und skaliert der 3DHeat-Viewer die Zeilen selbst – siehe [Die Daten](the-data.md).

## Mehrspieler {#multiplayer}

- Als online gespielt markiert (`multiplayer`): **ja**. `games --markdown` zeigt das als „allowed (reads only what the game publishes)“.
- Art `replay`: Es liest nur, was das Spiel oder die Plattform herausgibt (Wiederholungen und Demos, die das Spiel speichert). Deshalb zeichnet es auch im Online-Spiel auf, nicht nur offline. Die Markierung entscheidet nur, ob Speicher überhaupt gelesen werden darf.
- Speicher: Dieser Adapter liest **nie** den Speicher. Nur `memory`-Adapter lesen Speicher, und nie bei einem Spiel, das als online gespielt markiert ist – siehe [Quellen und Regeln](sources-and-rules.md).

## Aufgezeichnete Statistiken {#statistics-recorded}

Statistik-Schlüssel, die der Code dieses Adapters beim Namen setzt (das `stats` jeder Session in `meta.json` und die Tabelle `stats` in `watcher.sqlite`):

`accuracy`, `full_combo`

Ein Schlüssel in geschweiften Klammern wird zur Laufzeit vervollständigt (`score.{team}` ist ein Schlüssel pro Team). Schlüssel, die der Code aus einer Tabelle der Spielfelder oder aus den eigenen Statistiknamen des Spiels übernimmt, stehen nicht in dieser Liste; „Was aufgezeichnet wird“ oben nennt sie.

## Vollständigkeit {#completeness}

Der Watcher folgt der [Konverterregel](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md) von 3DHeat: Was die Quelle enthält, wird gelesen oder gespeichert, nie weggelassen. Außer den Zeilen wird jedes Paket, jede Seite, jede Zeile und jede Antwort, die der Adapter bekommt, vollständig in der `heat.raw.parquet` der Session gespeichert (Spalten `time`, `ms`, `type`, `used`, `payload`, `text` und alle Felder, die nach Namen behalten werden; `used` markiert, was auch zu Zeilen wurde). `selfCheck.completeness` in `meta.json` zählt jeden `type`; `lost` ist 0.

**Gelesen**

- jedes Bild: eine Zeile zu seiner Zeit (Millisekunden aufsummiert), x und y auf dem Spielfeld, `keys` die Tastenbits (Maus 1 und 2, Tasten 1 und 2, Rauch); im Mania-Modus hält x die gedrückten Tasten statt einer Stelle
- der Kopf, jedes Feld: Modus, Version, der MD5 der Beatmap (die Datei nennt die Beatmap nur darüber), der Spieler, der MD5 der Wiederholung, 300er, 100er, 50er, Gekis, Katus, Fehlschläge, Punktzahl, maximale Combo, Full Combo, Mods (mit Namen in meta.json `osu.modNames`), die Zeit der Partie – als Statistiken und in meta.json `osu`
- der Graph des Lebensbalkens: eine `life`-Zeile pro Punkt (Zeit, Leben 0..1)
- das Bild `-12345`: der Zufallsstartwert (`osu.seed`); die Online-Ergebnis-ID (`osu.scoreId`); im Trainingsmodus die Genauigkeit (`osu.targetPracticeAccuracy`)

**Roh gespeichert**

- die Datei vollständig, Teil für Teil, in heat.raw.parquet (`offset`, wo jeder beginnt, damit die Teile die Datei ergeben): `header`, `replay_data` (die LZMA-komprimierten Bilder, wie gespeichert), `score_id`, `mod_info` und `trailing` für alles, was auf die vom Format beschriebenen Teile folgt (die Exporte von osu!lazer legen dort Daten ab) – gespeichert, nicht gelesen

**Nicht verfügbar**

- die Beatmap selbst (Treffer-Objekte, Timing): Sie steckt nicht in einer Wiederholung; sie wird nur über ihren MD5 genannt
- die Wiederholungen von osu!lazer: Sie liegen in dessen Datenbank, nicht als Dateien

**Größe**: Die Roh-Beilage ist etwa so groß wie die Wiederholung (zehn bis hundert Kilobyte)

## Geprüft {#verified}

getestet mit Wiederholungen, die nach dem veröffentlichten .osr-Format gebaut wurden; osu!lazer speichert Wiederholungen in einem eigenen Speicher und wird nicht gelesen

## Quelle {#source}

[heat3d_watch/adapters/replays.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/replays.py)

<!-- Aus dem Adapter erzeugt von tools/gen_game_pages.py; ändere den Adapter und führe das Skript erneut aus, statt diese Seite zu bearbeiten. -->
