---
title: "Hearthstone (Logdateien)"
nav_order: 25
lang: de
source: game-hearthstone.md
source_hash: "e79c19776947"
nav_exclude: true
search_exclude: true
---
# Hearthstone (Logdateien) {#hearthstone-log-files}

Während du Hearthstone spielst, liest der Watcher die Dateien, die das Spiel schreibt, und speichert, was passiert ist. So kannst du es später als Statistik und Zeitleiste ansehen.

*Technische Details: Adapter `hearthstone`, Art [`log`](sources-and-rules.md); er läuft, solange `Hearthstone.exe` läuft, und sucht alle 0,5 s nach neuen Daten.*

## Was aufgezeichnet wird {#what-is-recorded}

- Spielbeginn und -ende mit dem Ergebnis (gewonnen, verloren, unentschieden), den Runden und dem Namen des Gegners
- jede Runde
- jede Zeile von Power.log und der anderen Logs, vollständig in heat.raw.parquet
- Partien, Siege, Niederlagen, Unentschieden, Runden, längste Partie

## Woher die Daten kommen {#where-it-comes-from}

&lt;Installation>\Logs\Power.log (oder Logs\Hearthstone_\*\Power.log), geschrieben, sobald %LOCALAPPDATA%\Blizzard\Hearthstone\log.config einen Abschnitt [Power] hat, und jedes andere \*.log, das das Spiel dort schreibt

## So schaltest du es ein {#how-to-switch-it-on}

`python -m heat3d_watch setup hearthstone --apply` ergänzt die Protokollierung [Power] in %LOCALAPPDATA%\Blizzard\Hearthstone\log.config (Sicherung wird angelegt); danach das Spiel neu starten

Gib den Befehl in einem Terminal ein, das im Ordner des Watchers geöffnet ist (siehe [Bevor du anfängst](before-you-start.md)). Schlägt er fehl, sagt die letzte Zeile warum; [Installation und Start](installing-and-running.md) beschreibt die üblichen Ursachen.

`python -m heat3d_watch setup hearthstone` listet die Dateien auf, die es ändern würde; `python -m heat3d_watch setup hearthstone --apply` ändert sie und behält das Original als `<Datei>.heat3d-backup` (siehe [Befehle](commands.md#setup)). Für jede Änderung gibt es `hearthstone: changed: ...` aus, oder `hearthstone: nothing to change`, wenn es schon eingeschaltet ist.

## So funktioniert es {#how-it-works}

Hearthstone: das Power.log des Spiels, das geschrieben wird, sobald `log.config` es verlangt.

Hearthstone liest `%LOCALAPPDATA%\Blizzard\Hearthstone\log.config` beim Start. Ein Abschnitt `[Power]` mit `LogLevel=1` und `FilePrinting=true` lässt das Spiel jede Zustandsänderung jeder Partie nach `<Installation>\Logs\Power.log` schreiben (neuere Clients legen die Protokolle jedes Starts in einen eigenen Ordner, `Logs\Hearthstone_<Datum>\`). Das ist die dokumentierte Debug-Protokollierung, die Decktracker seit 2014 einschalten (das Setup des Hearthstone Deck Tracker schreibt denselben Abschnitt). `setup()` ergänzt den Abschnitt und sichert die Datei vorher, so wie sie war; das Spiel muss neu gestartet werden, um ihn zu lesen.

Die verwendeten Zeilen stammen alle aus `GameState.DebugPrintPower()` (die Zeilen `PowerTaskList` wiederholen sie und werden übersprungen):

```text
D 20:15:01.1234567 GameState.DebugPrintPower() - CREATE_GAME
D 20:15:01.1234567 GameState.DebugPrintPower() -     Player EntityID=2 PlayerID=1 GameAccountId=[hi=1 lo=2]
D 20:15:01.1234567 GameState.DebugPrintGame() - PlayerID=1, PlayerName=Name#1234
D 20:15:02.1234567 GameState.DebugPrintPower() -     FULL_ENTITY - Updating [entityName=... id=4 zone=HAND
                   zonePos=0 cardId=CS2_029 player=1] CardID=CS2_029
D 20:16:00.1234567 GameState.DebugPrintPower() - TAG_CHANGE Entity=GameEntity tag=TURN value=3
D 20:25:00.1234567 GameState.DebugPrintPower() - TAG_CHANGE Entity=Name#1234 tag=PLAYSTATE value=WON
D 20:25:00.1234567 GameState.DebugPrintPower() - TAG_CHANGE Entity=GameEntity tag=STATE value=COMPLETE
```

Die Seite des Spielers ist die, deren Starthand benannte Karten hat (die des Gegners sind verdeckt); sonst die Seite, die nicht die KI (Konto 0) oder „UNKNOWN HUMAN PLAYER“ ist. Zeilen tragen nur die Uhrzeit; das Datum ist das heutige. Keine Positionen.

Jede Zeile von Power.log wird vollständig in der Roh-Beilage der Session gespeichert (Konverterregel von 3DHeat), einschließlich der Wiederholungen von `PowerTaskList`, Optionen, Auswahlen und Entitäts-Updates: `type` ist die Methode, die sie geschrieben hat (`GameState.DebugPrintPower`, `PowerTaskList.DebugPrintPower`, `GameState.DebugPrintOptions`, ...). Jedes andere Log, das das Spiel daneben schreibt – `LoadingScreen.log`, `Decks.log`, `Zone.log`, `Arena.log`, ..., jeweils dann, wenn log.config es verlangt (Decktracker schalten sie oft ein) –, wird genauso verfolgt und mit seinem Namen in `log` gespeichert.

## Positionen und Achsen {#positions-and-axes}

| | |
|---|---|
| Positionen aufgezeichnet | nein |
| Oben-Achse | `y` |
| Einheiten | keine Positionen aufgezeichnet |
| Für den Viewer gespiegelt | keine |
| Einheitenskala (`scale`: der Viewer multipliziert die Positionen damit) | 1 |

Diese Werte landen in der `meta.json` jeder Session (`axes`) und, wenn die Session Positionen hat, im Footer der `heat.parquet`. So dreht und skaliert der 3DHeat-Viewer die Zeilen selbst – siehe [Die Daten](the-data.md).

## Mehrspieler {#multiplayer}

- Als online gespielt markiert (`multiplayer`): **ja**. `games --markdown` zeigt das als „allowed (reads only what the game publishes)“.
- Art `log`: Es liest nur, was das Spiel oder die Plattform herausgibt (Dateien, die das Spiel während des Laufs schreibt). Deshalb zeichnet es auch im Online-Spiel auf, nicht nur offline. Die Markierung entscheidet nur, ob Speicher überhaupt gelesen werden darf.
- Speicher: Dieser Adapter liest **nie** den Speicher. Nur `memory`-Adapter lesen Speicher, und nie bei einem Spiel, das als online gespielt markiert ist – siehe [Quellen und Regeln](sources-and-rules.md).

## Aufgezeichnete Statistiken {#statistics-recorded}

Statistik-Schlüssel, die der Code dieses Adapters beim Namen setzt (das `stats` jeder Session in `meta.json` und die Tabelle `stats` in `watcher.sqlite`):

`bad_lines`, `games`, `longest_game_turns`, `losses`, `ties`, `turns`, `wins`

Ein Schlüssel in geschweiften Klammern wird zur Laufzeit vervollständigt (`score.{team}` ist ein Schlüssel pro Team). Schlüssel, die der Code aus einer Tabelle der Spielfelder oder aus den eigenen Statistiknamen des Spiels übernimmt, stehen nicht in dieser Liste; „Was aufgezeichnet wird“ oben nennt sie.

## Vollständigkeit {#completeness}

Der Watcher folgt der [Konverterregel](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md) von 3DHeat: Was die Quelle enthält, wird gelesen oder gespeichert, nie weggelassen. Außer den Zeilen wird jedes Paket, jede Seite, jede Zeile und jede Antwort, die der Adapter bekommt, vollständig in der `heat.raw.parquet` der Session gespeichert (Spalten `time`, `ms`, `type`, `used`, `payload`, `text` und alle Felder, die nach Namen behalten werden; `used` markiert, was auch zu Zeilen wurde). `selfCheck.completeness` in `meta.json` zählt jeden `type`; `lost` ist 0.

**Gelesen**

- `CREATE_GAME`, die Spieler (Entität, Spieler-ID, Konto; Konto 0 ist die KI) und ihre Namen (`DebugPrintGame`)
- welche Seite die des Spielers ist, aus den benannten Karten der Starthand
- `TAG_CHANGE` von TURN, PLAYSTATE (won, lost, tied) und STATE COMPLETE: Runden, Ergebnis, Gegner

**Roh gespeichert**

- jede Zeile von Power.log vollständig, `type` = die Methode, die sie geschrieben hat (`GameState.DebugPrintPower`, `PowerTaskList.DebugPrintPower`, `GameState.DebugPrintGame`, `GameState.DebugPrintOptions`, `GameState.SendChoices`, `GameState.DebugPrintEntityChoices`, `PowerProcessor.DoTaskListForCard`, ...), `log` `Power`, `used`, wo sie zu einer Zeile wurde: jede gespielte, gezogene und aufgedeckte Karte, jede Tag-Änderung, jeder Angriff, jede Option und jede Auswahl steht hier, noch nicht in Zeilen
- jede Zeile der anderen Logs im selben Ordner (`LoadingScreen`, `Decks`, `Zone`, `Arena`, `Achievements`, `FullScreenFX`, ... – was log.config einschaltet), mit denselben `type`s, mit dem Namen des Logs in `log`
- eine Zeile ohne Level und Uhrzeit als `untimed`, eine ohne Methode als `untagged`

**Nicht verfügbar**

- Positionen: Ein Kartenspiel hat keine
- die verdeckten Karten des Gegners: Das Log benennt eine Karte erst, wenn sie aufgedeckt ist
- Logs, die log.config nicht einschaltet: `setup` fragt nur nach [Power]; die anderen Logs kommen, wenn ein anderes Werkzeug (ein Decktracker) sie eingeschaltet hat
- Logs früherer Starts: Jeder Start schreibt einen neuen Ordner; die älter als dieser Lauf des Spiels sind, werden nicht noch einmal gelesen

**Größe**: Power.log mit Verbose ist etwa 1–5 MB pro Partie, 10–40 MB pro Stunde Spiel; die anderen Logs fügen wenig hinzu; zstd macht in heat.raw.parquet etwa ein Zehntel oder weniger daraus (die Zeilen wiederholen sich stark)

## Geprüft {#verified}

getestet mit synthetischen Power.log-Zeilen im Format des Spiels; noch nicht gegen das Spiel getestet

## Quelle {#source}

[heat3d_watch/adapters/hearthstone.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/hearthstone.py)

<!-- Aus dem Adapter erzeugt von tools/gen_game_pages.py; ändere den Adapter und führe das Skript erneut aus, statt diese Seite zu bearbeiten. -->
