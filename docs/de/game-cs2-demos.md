---
title: "Counter-Strike 2 (Replays)"
nav_order: 8
lang: de
source: game-cs2-demos.md
source_hash: "d115f9085302"
nav_exclude: true
search_exclude: true
---
# Counter-Strike 2 (Replays) {#counter-strike-2-replays}

Nach einem Match von Counter-Strike 2 macht der Watcher aus dem Replay, das das Spiel gespeichert hat, Dateien, die du auf einer Karte im 3DHeat-Viewer ansehen kannst.

*Technische Details: Adapter `cs2-demos`, Art [`replay`](sources-and-rules.md); er läuft immer (er wartet nicht auf den Start eines Spiels) und sucht alle 5 s nach neuen Daten.*

## Was aufgezeichnet wird {#what-is-recorded}

- Position, Blickrichtung, Gesundheit und Geld jedes Spielers (jeder 8. Tick)
- Kills, Tode, Schaden, Granaten, Bombenlegen und Entschärfen, dort wo sie passiert sind
- Runden, Spielstand, Wirtschaft; die Scoreboard-Zeile des angemeldeten Spielers als Statistik

## Woher es kommt {#where-it-comes-from}

Demos, die CS2 speichert: &lt;CS2>/game/csgo/replays/\*.dem (aus dem Spielverlauf heruntergeladen) und &lt;CS2>/game/csgo/\*.dem (aufgenommen)

## So schaltest du es ein {#how-to-switch-it-on}

Lade die Demo eines Matches in CS2 herunter (Watch > Your Matches) oder nimm eines mit dem Konsolenbefehl `record` auf.

Einstellungen aus Umgebungsvariablen:

- `HEAT3D_CS2`: der Ordner von 3DHeat CS2, wenn er nicht neben dem Watcher liegt oder nicht installiert ist

## So funktioniert es {#how-it-works}

Replays und Demos: Was ein Spiel von einem Match speichert, wird umgewandelt, sobald das Match vorbei ist.

Ein Replay enthält alles, was eine Live-Ansicht in Mehrspielerspielen zurückhält: jede Position jedes Spielers, jeden Kill dort, wo er passiert ist. Es ist eine Datei, die das Spiel für seine Spieler schreibt, deshalb berührt das Lesen nichts im Spiel. Der Watcher schaut in die Ordner, in denen Spiele sie speichern, wartet, bis eine neue Datei nicht mehr wächst (sonst schreibt das Spiel noch daran), und wandelt sie in einem eigenen Thread um. So hält eine lange Umwandlung den restlichen Watcher nicht auf.

Beim ersten Sehen eines Ordners werden die dort vorhandenen Replays nur vermerkt, nicht umgewandelt. Ein Spieler mit jahrelangen Demos würde sonst einen Tag lang einen beschäftigten Watcher haben. `python -m heat3d_watch replays <adapter> [folder]` wandelt die vorhandenen auf Anfrage um.

#### Counter-Strike 2 {#counter-strike-2}

CS2 speichert die Demos, die ein Spieler im Reiter Watch aus dem Spielverlauf herunterlädt, unter `<CS2>/game/csgo/replays/`. Die mit dem Konsolenbefehl `record` aufgenommenen legt es unter `<CS2>/game/csgo/` ab. Jede wird mit dem eigenen CS2-Konverter dieses Repositorys umgewandelt (3DHeat CS2, github.com/Holdi601/3DHeat-CS2: Position, Blickrichtung, Gesundheit und Geld jedes Spielers jeden achten Tick; Kills, Tode, Schaden, Granaten, Bombenlegen und Entschärfen dort, wo sie passiert sind; Runden, Spielstand, Wirtschaft). Das Ergebnis landet im Sitzungsordner als Tabelle `<map>/<match>.parquet` und Zusammenfassung `<match>.match.json`, die die Reiter Heatmap und Match des Viewers lesen. Das Scoreboard des Matches wird zur Statistik der Sitzung: für den Spieler, dessen Steam-Konto auf diesem Rechner angemeldet ist (aus Steams `loginusers.vdf`), unter den einfachen Namen - Kills, Tode, Assists, ADR, KAST, Headshot-Quote, Eröffnungs-Kills, Clutches - dazu Spielstand und Runden.

Dasselbe Modul bedient außerdem: [Dota 2 (Replays)](game-dota-replays.md), [osu! (Replays)](game-osu-replays.md), [Squad (Replays)](game-squad-demos.md), [War Thunder (Replays)](game-warthunder-replays.md), [World of Tanks (Replays)](game-wot-replays.md), [World of Warships (Replays)](game-wows-replays.md).

## Positionen und Achsen {#positions-and-axes}

| | |
|---|---|
| Positionen aufgezeichnet | ja |
| Hochachse | `z` |
| Einheiten | Zoll (Source-Einheiten) |
| Für den Viewer gespiegelt | `y` |
| Einheitenfaktor (`scale`: der Viewer multipliziert die Positionen damit) | 1 |

Diese Werte stehen in der `meta.json` jeder Sitzung (`axes`) und, wenn die Sitzung Positionen hat, im Fuß der `heat.parquet`. So dreht und skaliert der 3DHeat-Viewer die Zeilen selbst. Siehe [Die Daten](the-data.md).

## Mehrspieler {#multiplayer}

- Als Online-Spiel markiert (`multiplayer`): **ja**. `games --markdown` zeigt das als „erlaubt (liest nur, was das Spiel veröffentlicht)“.
- Art `replay`: Er liest nur, was das Spiel oder die Plattform herausgibt (Replays und Demos, die das Spiel speichert). Deshalb zeichnet er auch im Online-Spiel auf, nicht nur offline. Die Markierung entscheidet nur, ob jemals Speicher gelesen werden darf.
- Speicher: **nie** von diesem Adapter gelesen. Nur Adapter der Art `memory` lesen Speicher, und nie bei einem als Online-Spiel markierten Spiel. Siehe [Quellen und Regeln](sources-and-rules.md).

## Erfasste Statistiken {#statistics-recorded}

Statistikschlüssel, die der Code dieses Adapters namentlich setzt (`stats` jeder Sitzung in `meta.json` und die Tabelle `stats` der `watcher.sqlite`):

`map`, `rounds`, `score.{team}`, `won`

Ein Schlüssel in geschweiften Klammern wird zur Laufzeit ergänzt (`score.{team}` ist ein Schlüssel pro Team). Schlüssel, die der Code aus einer Tabelle der Spielfelder oder aus den eigenen Statistiknamen des Spiels nimmt, stehen nicht in dieser Liste. Was aufgezeichnet wird, steht oben und nennt sie.

## Vollständigkeit {#completeness}

Der Konverter, den dieser Adapter ausführt, folgt der [Konverterregel](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md) von 3DHeat: Was das Replay enthält, wird gelesen oder behalten, nie verworfen. Es wird in die Tabelle und das Match-Dokument gelesen, alles Übrige bleibt ganz in Begleitdateien daneben erhalten und wird im `selfCheck.completeness` des Match-Dokuments gezählt. Die eigene Dokumentation des Konverters listet auf, was er liest, roh behält und nicht lesen kann.

## Geprüft {#verified}

Der Konverter ist an echten Turnier-Demos getestet. Die Ordnerüberwachung und die Statistiken sind durch Tests geprüft.

## Quelle {#source}

[heat3d_watch/adapters/replays.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/replays.py)

<!-- Generated from the adapter by tools/gen_game_pages.py; change the adapter and run it again rather than editing this page. -->
