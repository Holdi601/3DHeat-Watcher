---
title: "World of Warships (Replays)"
nav_order: 49
lang: "de"
source: game-wows-replays.md
source_hash: "c822aca3f6fe"
nav_exclude: true
search_exclude: true
---
# World of Warships (Replays) {#world-of-warships-replays}

Nach einem Match von World of Warships macht der Watcher aus dem Replay, das das Spiel gespeichert hat, Dateien, die du auf einer Karte im 3DHeat-Viewer ansehen kannst.

*Technische Details: Adapter `wows-replays`, Art [`replay`](sources-and-rules.md); er läuft immer (er wartet nicht auf den Start eines Spiels) und sucht alle 5 s nach neuen Daten.*

## Was aufgezeichnet wird {#what-is-recorded}

- Position und Richtung jedes Schiffs, solange der aufzeichnende Client es sah (etwa 6 bis 7-mal pro Sekunde, wenn es fährt); das eigene Schiff des Spielers durchgehend
- Spieler, Verbündeter oder Gegner, und Schiff (das des aufzeichnenden Spielers mit Namen, die anderen mit der Schiffsnummer des Spiels); versenkte Schiffe dort, wo sie sanken, und ihre Angreifer dort, wo sie standen
- die Karte; Schiff, Kills und Überleben des aufzeichnenden Spielers als Statistik

## Woher es kommt {#where-it-comes-from}

Replays, die World of Warships speichert: &lt;World of Warships>/replays/\*.wowsreplay (mit eingeschalteten Replays), umgewandelt vom externen Konverter `heat3d-wows-replay` (exporters/ext/wows-replay)

## So schaltest du es ein {#how-to-switch-it-on}

Schalte die Replay-Aufzeichnung in World of Warships ein (`isReplayEnabled` in der preferences.xml oder die eigene Einstellung des Spiels, wo es sie gibt) und installiere den Konverter: pip install -e &lt;3DHeat>/exporters/ext/wows-replay

Einstellungen aus Umgebungsvariablen:

- `HEAT3D_WOWS_REPLAY`: der Ordner des Konverters (ein Klon oder ein entpacktes Release), wenn er nicht installiert ist oder nicht neben dem Watcher liegt

## So funktioniert es {#how-it-works}

Replays und Demos: Was ein Spiel von einem Match speichert, wird umgewandelt, sobald das Match vorbei ist.

Ein Replay enthält alles, was eine Live-Ansicht in Mehrspielerspielen zurückhält: jede Position jedes Spielers, jeden Kill dort, wo er passiert ist. Es ist eine Datei, die das Spiel für seine Spieler schreibt, deshalb berührt das Lesen nichts im Spiel. Der Watcher schaut in die Ordner, in denen Spiele sie speichern, wartet, bis eine neue Datei nicht mehr wächst (sonst schreibt das Spiel noch daran), und wandelt sie in einem eigenen Thread um. So hält eine lange Umwandlung den restlichen Watcher nicht auf.

Beim ersten Sehen eines Ordners werden die dort vorhandenen Replays nur vermerkt, nicht umgewandelt. Ein Spieler mit jahrelangen Demos würde sonst einen Tag lang einen beschäftigten Watcher haben. `python -m heat3d_watch replays <adapter> [folder]` wandelt die vorhandenen auf Anfrage um.

#### World of Tanks und World of Warships {#world-of-tanks-and-world-of-warships}

Beide speichern ein Replay jeder Schlacht unter `<game>/replays/`, wenn die Aufzeichnung eingeschaltet ist (`*.wotreplay`, `*.wowsreplay`). Die Installationen findet der Watcher über die Liste des Wargaming Game Center (`C:/Games/World_of_Tanks*` bzw. `World_of_Warships*`) und über Steam. Wie bei War Thunder liest der Watcher die Dateien nicht selbst. Das macht je ein externer Konverter (`exporters/ext/wot-replay`, Befehl `heat3d-wot-replay`; `exporters/ext/wows-replay`, Befehl `heat3d-wows-replay`). Sie sind getrennt, damit ein Problem mit den Bedingungen von Wargaming nur den jeweiligen Konverter betrifft. Ist der Befehl im PATH, installiert oder neben dem Watcher, macht er aus jedem neuen Replay `<map>/<match>.parquet` und `<match>.match.json` im Sitzungsordner. Fehlt er, sagt der Watcher einmal, wie man ihn installiert. Die Zeile des aufzeichnenden Spielers - Fahrzeug oder Schiff, Kills, Schaden (World of Tanks), ob er überlebt hat, und das Ergebnis (World of Tanks) - wird zur Statistik der Sitzung. Was jeder Konverter liest und was nicht, steht in seiner README.

Dasselbe Modul bedient außerdem: [Counter-Strike 2 (Replays)](game-cs2-demos.md), [Dota 2 (Replays)](game-dota-replays.md), [osu! (Replays)](game-osu-replays.md), [Squad (Replays)](game-squad-demos.md), [War Thunder (Replays)](game-warthunder-replays.md), [World of Tanks (Replays)](game-wot-replays.md).

## Positionen und Achsen {#positions-and-axes}

| | |
|---|---|
| Positionen aufgezeichnet | ja |
| Hochachse | `y` |
| Einheiten | Weltkoordinaten von World of Warships (x Ost, y oben, z Nord; eine Einheit ist nach Rumpfgeometrie 15 m, nach den Reichweiten des Spiels 30 m) |
| Für den Viewer gespiegelt | `z` |
| Einheitenfaktor (`scale`: der Viewer multipliziert die Positionen damit) | 1 |

Diese Werte stehen in der `meta.json` jeder Sitzung (`axes`) und, wenn die Sitzung Positionen hat, im Fuß der `heat.parquet`. So dreht und skaliert der 3DHeat-Viewer die Zeilen selbst. Siehe [Die Daten](the-data.md).

## Mehrspieler {#multiplayer}

- Als Online-Spiel markiert (`multiplayer`): **ja**. `games --markdown` zeigt das als „erlaubt (liest nur, was das Spiel veröffentlicht)“.
- Art `replay`: Er liest nur, was das Spiel oder die Plattform herausgibt (Replays und Demos, die das Spiel speichert). Deshalb zeichnet er auch im Online-Spiel auf, nicht nur offline. Die Markierung entscheidet nur, ob jemals Speicher gelesen werden darf.
- Speicher: **nie** von diesem Adapter gelesen. Nur Adapter der Art `memory` lesen Speicher, und nie bei einem als Online-Spiel markierten Spiel. Siehe [Quellen und Regeln](sources-and-rules.md).

## Erfasste Statistiken {#statistics-recorded}

Statistikschlüssel, die der Code dieses Adapters namentlich setzt (`stats` jeder Sitzung in `meta.json` und die Tabelle `stats` der `watcher.sqlite`):

`map`, `survived`, `vehicle`, `won`

Ein Schlüssel in geschweiften Klammern wird zur Laufzeit ergänzt (`score.{team}` ist ein Schlüssel pro Team). Schlüssel, die der Code aus einer Tabelle der Spielfelder oder aus den eigenen Statistiknamen des Spiels nimmt, stehen nicht in dieser Liste. Was aufgezeichnet wird, steht oben und nennt sie.

## Vollständigkeit {#completeness}

Der Konverter, den dieser Adapter ausführt, folgt der [Konverterregel](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md) von 3DHeat: Was das Replay enthält, wird gelesen oder behalten, nie verworfen. Es wird in die Tabelle und das Match-Dokument gelesen, alles Übrige bleibt ganz in Begleitdateien daneben erhalten und wird im `selfCheck.completeness` des Match-Dokuments gezählt. Die eigene Dokumentation des Konverters listet auf, was er liest, roh behält und nicht lesen kann.

## Geprüft {#verified}

Der Konverter ist an öffentlichen Replays aus mehreren Spielversionen und durch Tests an gebauten Replays geprüft. Dieser Hook ist durch Tests mit einem Ersatzbefehl geprüft.

## Quelle {#source}

[heat3d_watch/adapters/replays.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/replays.py)

<!-- Generated from the adapter by tools/gen_game_pages.py; change the adapter and run it again rather than editing this page. -->
