---
title: "War Thunder (Replays)"
nav_order: 46
lang: de
source: game-warthunder-replays.md
source_hash: "81f03926431d"
nav_exclude: true
search_exclude: true
---
# War Thunder (Replays) {#war-thunder-replays}

Nach einem Match von War Thunder macht der Watcher aus dem Replay, das das Spiel gespeichert hat, Dateien, die du auf einer Karte im 3DHeat-Viewer ansehen kannst.

*Technische Details: Adapter `warthunder-replays`, Art [`replay`](sources-and-rules.md); er läuft immer (er wartet nicht auf den Start eines Spiels) und sucht alle 5 s nach neuen Daten.*

## Was aufgezeichnet wird {#what-is-recorded}

- Position und Lage jedes Flugzeugs etwa 4-mal pro Sekunde (so viele, wie das Replay enthält)
- Positionen der Bodeneinheiten aus der Bodensynchronisation des Replays (bei Replays von 2026; nicht bei denen von 2025)
- wer jede Einheit war (Spieler, Fahrzeug-ID, Team), wo ein Kill oder Treffer sie benennt; Kills, Tode und Treffer dort, wo sie passiert sind; Chat; die Karte
- Kills, Tode, Punkte und Eroberungen des Replay-Autors als Statistik

## Woher es kommt {#where-it-comes-from}

Replays, die War Thunder speichert: &lt;War Thunder>/Replays/\*.wrpl (mit eingeschaltetem Speichern von Replays), umgewandelt vom externen Konverter `heat3d-wt-replay` (exporters/ext/warthunder-replay)

## So schaltest du es ein {#how-to-switch-it-on}

Schalte in War Thunders Optionen das Speichern von Replays ein und installiere den Konverter: pip install -e &lt;3DHeat>/exporters/ext/warthunder-replay

Einstellungen aus Umgebungsvariablen:

- `HEAT3D_WT_REPLAY`: der Ordner des Konverters (ein Klon oder ein entpacktes Release), wenn er nicht installiert ist oder nicht neben dem Watcher liegt

## So funktioniert es {#how-it-works}

Replays und Demos: Was ein Spiel von einem Match speichert, wird umgewandelt, sobald das Match vorbei ist.

Ein Replay enthält alles, was eine Live-Ansicht in Mehrspielerspielen zurückhält: jede Position jedes Spielers, jeden Kill dort, wo er passiert ist. Es ist eine Datei, die das Spiel für seine Spieler schreibt, deshalb berührt das Lesen nichts im Spiel. Der Watcher schaut in die Ordner, in denen Spiele sie speichern, wartet, bis eine neue Datei nicht mehr wächst (sonst schreibt das Spiel noch daran), und wandelt sie in einem eigenen Thread um. So hält eine lange Umwandlung den restlichen Watcher nicht auf.

Beim ersten Sehen eines Ordners werden die dort vorhandenen Replays nur vermerkt, nicht umgewandelt. Ein Spieler mit jahrelangen Demos würde sonst einen Tag lang einen beschäftigten Watcher haben. `python -m heat3d_watch replays <adapter> [folder]` wandelt die vorhandenen auf Anfrage um.

#### War Thunder {#war-thunder}

War Thunder speichert ein Replay jeder Schlacht unter `<War Thunder>/Replays/*.wrpl`, wenn das Speichern von Replays in den Optionen eingeschaltet ist. Der Watcher liest sie nicht selbst. Das macht ein externer Konverter (3DHeat-War-Thunder-Replay-Konverter, `exporters/ext/warthunder-replay`, Befehl `heat3d-wt-replay`), der getrennt gehalten wird, damit ein Problem mit ihm nichts anderes berührt. Ist der Befehl im PATH, oder ist das Paket installiert oder liegt neben dem Watcher, läuft jedes neue Replay durch ihn. Das Ergebnis landet im Sitzungsordner als `<map>/<match>.parquet` und `<match>.match.json`. Ist er nicht da, sagt der Watcher einmal, wie man ihn installiert, und lässt den Ordner in Ruhe. Was der Konverter liest und was nicht, steht in seiner README. Die Ergebniszeile des Autors des Replays - Kills, Bodenkills, Tode, Assists, Punkte, Eroberungen - wird zur Statistik der Sitzung.

Dasselbe Modul bedient außerdem: [Counter-Strike 2 (Replays)](game-cs2-demos.md), [Dota 2 (Replays)](game-dota-replays.md), [osu! (Replays)](game-osu-replays.md), [Squad (Replays)](game-squad-demos.md), [World of Tanks (Replays)](game-wot-replays.md), [World of Warships (Replays)](game-wows-replays.md).

## Positionen und Achsen {#positions-and-axes}

| | |
|---|---|
| Positionen aufgezeichnet | ja |
| Hochachse | `y` |
| Einheiten | Meter (x Ost, y oben, z Nord) |
| Für den Viewer gespiegelt | `z` |
| Einheitenfaktor (`scale`: der Viewer multipliziert die Positionen damit) | 1 |

Diese Werte stehen in der `meta.json` jeder Sitzung (`axes`) und, wenn die Sitzung Positionen hat, im Fuß der `heat.parquet`. So dreht und skaliert der 3DHeat-Viewer die Zeilen selbst. Siehe [Die Daten](the-data.md).

## Mehrspieler {#multiplayer}

- Als Online-Spiel markiert (`multiplayer`): **ja**. `games --markdown` zeigt das als „erlaubt (liest nur, was das Spiel veröffentlicht)“.
- Art `replay`: Er liest nur, was das Spiel oder die Plattform herausgibt (Replays und Demos, die das Spiel speichert). Deshalb zeichnet er auch im Online-Spiel auf, nicht nur offline. Die Markierung entscheidet nur, ob jemals Speicher gelesen werden darf.
- Speicher: **nie** von diesem Adapter gelesen. Nur Adapter der Art `memory` lesen Speicher, und nie bei einem als Online-Spiel markierten Spiel. Siehe [Quellen und Regeln](sources-and-rules.md).

## Erfasste Statistiken {#statistics-recorded}

Statistikschlüssel, die der Code dieses Adapters namentlich setzt (`stats` jeder Sitzung in `meta.json` und die Tabelle `stats` der `watcher.sqlite`):

`map`

Ein Schlüssel in geschweiften Klammern wird zur Laufzeit ergänzt (`score.{team}` ist ein Schlüssel pro Team). Schlüssel, die der Code aus einer Tabelle der Spielfelder oder aus den eigenen Statistiknamen des Spiels nimmt, stehen nicht in dieser Liste. Was aufgezeichnet wird, steht oben und nennt sie.

## Vollständigkeit {#completeness}

Der Konverter, den dieser Adapter ausführt, folgt der [Konverterregel](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md) von 3DHeat: Was das Replay enthält, wird gelesen oder behalten, nie verworfen. Es wird in die Tabelle und das Match-Dokument gelesen, alles Übrige bleibt ganz in Begleitdateien daneben erhalten und wird im `selfCheck.completeness` des Match-Dokuments gezählt. Die eigene Dokumentation des Konverters listet auf, was er liest, roh behält und nicht lesen kann.

## Geprüft {#verified}

Der Konverter ist an öffentlichen Replays aus mehreren Spielversionen geprüft (Kills und Namen stimmen mit den Ergebnissen überein) und durch Tests an gebauten Replays. Dieser Hook ist durch Tests mit einem Ersatzbefehl geprüft.

## Quelle {#source}

[heat3d_watch/adapters/replays.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/replays.py)

<!-- Generated from the adapter by tools/gen_game_pages.py; change the adapter and run it again rather than editing this page. -->
