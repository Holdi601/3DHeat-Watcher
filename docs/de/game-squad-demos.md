---
title: "Squad (Replays)"
nav_order: 41
lang: de
source: game-squad-demos.md
source_hash: "82c24e6df01c"
nav_exclude: true
search_exclude: true
---
# Squad (Replays) {#squad-replays}

Nach einem Match von Squad macht der Watcher aus dem Replay, das das Spiel gespeichert hat, Dateien, die du auf einer Karte im 3DHeat-Viewer ansehen kannst.

*Technische Details: Adapter `squad-demos`, Art [`replay`](sources-and-rules.md); er läuft immer (er wartet nicht auf den Start eines Spiels) und sucht alle 5 s nach neuen Daten.*

## Was aufgezeichnet wird {#what-is-recorded}

- Position, Körperdrehung und Geschwindigkeit jedes Spielers, jedes Mal wenn der Server sie repliziert (bis zu 8-mal pro Sekunde), zu Fuß und in Bodenfahrzeugen
- Name, Team, Fraktion und Trupp jedes Spielers, mit Teamwechseln
- nicht: Bewegung von Helikoptern, Kills und Einsatzgegenstände. Siehe die README des Readers.

## Woher es kommt {#where-it-comes-from}

Server-Demos, die Squad mit dem Admin-Befehl AdminDemoRec aufzeichnet: &lt;server>/SquadGame/Saved/Demos/\*.replay, gelesen vom externen Reader `heat3d-squad-demo` (exporters/ext/squad-demo)

## So schaltest du es ein {#how-to-switch-it-on}

Aufnahme auf dem Server: Gib dem Admin die Berechtigung `demos` in der Admins.cfg und gib dann in der Konsole des Spiels `AdminDemoRec <name>` und `AdminDemoStop` ein. Kopiere die Demo hierher und installiere den Reader: pip install -e &lt;3DHeat>/exporters/ext/squad-demo

Einstellungen aus Umgebungsvariablen:

- `HEAT3D_SQUAD_DEMO`: der Ordner des Konverters (ein Klon oder ein entpacktes Release), wenn er nicht installiert ist oder nicht neben dem Watcher liegt

## So funktioniert es {#how-it-works}

Replays und Demos: Was ein Spiel von einem Match speichert, wird umgewandelt, sobald das Match vorbei ist.

Ein Replay enthält alles, was eine Live-Ansicht in Mehrspielerspielen zurückhält: jede Position jedes Spielers, jeden Kill dort, wo er passiert ist. Es ist eine Datei, die das Spiel für seine Spieler schreibt, deshalb berührt das Lesen nichts im Spiel. Der Watcher schaut in die Ordner, in denen Spiele sie speichern, wartet, bis eine neue Datei nicht mehr wächst (sonst schreibt das Spiel noch daran), und wandelt sie in einem eigenen Thread um. So hält eine lange Umwandlung den restlichen Watcher nicht auf.

Beim ersten Sehen eines Ordners werden die dort vorhandenen Replays nur vermerkt, nicht umgewandelt. Ein Spieler mit jahrelangen Demos würde sonst einen Tag lang einen beschäftigten Watcher haben. `python -m heat3d_watch replays <adapter> [folder]` wandelt die vorhandenen auf Anfrage um.

#### Squad {#squad}

Die dedizierten Server von Squad zeichnen eine Demo eines Matches auf, wenn ein Admin mit der Berechtigung `demos` `AdminDemoRec <name>` (und `AdminDemoStop`) ausführt. Sie landet unter `<server>/SquadGame/Saved/Demos/<name>.replay`. Das ist ein Netzwerk-Replay der Unreal Engine mit allem, was der Server repliziert hat, einschließlich der gesamten Bewegung jedes Spielers. Der Watcher liest sie nicht selbst. Das macht ein externer Reader (3DHeat Squad-Demo-Reader, `exporters/ext/squad-demo`, Befehl `heat3d-squad-demo`), der getrennt gehalten wird, damit ein Problem mit ihm nichts anderes berührt. Er läuft für jede neue Demo in den Ordnern, in die ein lokaler Server schreibt, oder in einem Ordner, den die Einstellungen für Demos ergänzen, die von einem gemieteten Server kopiert wurden. Das Ergebnis landet im Sitzungsordner als `<map>/<match>.parquet` und `<match>.match.json`. Layer, Karte, Spielerzahl und Matchdauer werden zur Statistik der Sitzung.

Dasselbe Modul bedient außerdem: [Counter-Strike 2 (Replays)](game-cs2-demos.md), [Dota 2 (Replays)](game-dota-replays.md), [osu! (Replays)](game-osu-replays.md), [War Thunder (Replays)](game-warthunder-replays.md), [World of Tanks (Replays)](game-wot-replays.md), [World of Warships (Replays)](game-wows-replays.md).

## Positionen und Achsen {#positions-and-axes}

| | |
|---|---|
| Positionen aufgezeichnet | ja |
| Hochachse | `z` |
| Einheiten | Unreal-Einheiten (Zentimeter) |
| Für den Viewer gespiegelt | keine |
| Einheitenfaktor (`scale`: der Viewer multipliziert die Positionen damit) | 1 |

Diese Werte stehen in der `meta.json` jeder Sitzung (`axes`) und, wenn die Sitzung Positionen hat, im Fuß der `heat.parquet`. So dreht und skaliert der 3DHeat-Viewer die Zeilen selbst. Siehe [Die Daten](the-data.md).

## Mehrspieler {#multiplayer}

- Als Online-Spiel markiert (`multiplayer`): **ja**. `games --markdown` zeigt das als „erlaubt (liest nur, was das Spiel veröffentlicht)“.
- Art `replay`: Er liest nur, was das Spiel oder die Plattform herausgibt (Replays und Demos, die das Spiel speichert). Deshalb zeichnet er auch im Online-Spiel auf, nicht nur offline. Die Markierung entscheidet nur, ob jemals Speicher gelesen werden darf.
- Speicher: **nie** von diesem Adapter gelesen. Nur Adapter der Art `memory` lesen Speicher, und nie bei einem als Online-Spiel markierten Spiel. Siehe [Quellen und Regeln](sources-and-rules.md).

## Erfasste Statistiken {#statistics-recorded}

Statistikschlüssel, die der Code dieses Adapters namentlich setzt (`stats` jeder Sitzung in `meta.json` und die Tabelle `stats` der `watcher.sqlite`):

`layer`, `map`, `match_seconds`, `players`

Ein Schlüssel in geschweiften Klammern wird zur Laufzeit ergänzt (`score.{team}` ist ein Schlüssel pro Team). Schlüssel, die der Code aus einer Tabelle der Spielfelder oder aus den eigenen Statistiknamen des Spiels nimmt, stehen nicht in dieser Liste. Was aufgezeichnet wird, steht oben und nennt sie.

## Vollständigkeit {#completeness}

Der Konverter, den dieser Adapter ausführt, folgt der [Konverterregel](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md) von 3DHeat: Was das Replay enthält, wird gelesen oder behalten, nie verworfen. Es wird in die Tabelle und das Match-Dokument gelesen, alles Übrige bleibt ganz in Begleitdateien daneben erhalten und wird im `selfCheck.completeness` des Match-Dokuments gezählt. Die eigene Dokumentation des Konverters listet auf, was er liest, roh behält und nicht lesen kann.

## Geprüft {#verified}

Der Reader ist an öffentlichen Server-Demos geprüft (die Bewegung stimmt mit der mitgelieferten Geschwindigkeit überein; das Team jeder Zeile stimmt mit der Fraktion ihres Soldaten überein) und durch Tests an gebauten Demos. Dieser Hook ist durch Tests mit einem Ersatzbefehl geprüft.

## Quelle {#source}

[heat3d_watch/adapters/replays.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/replays.py)

<!-- Generated from the adapter by tools/gen_game_pages.py; change the adapter and run it again rather than editing this page. -->
