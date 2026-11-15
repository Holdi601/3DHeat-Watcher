---
title: "Rocket League (Spielzustand)"
nav_order: 40
lang: de
source: game-rocketleague-stats.md
source_hash: "3da6ea772068"
nav_exclude: true
search_exclude: true
---
# Rocket League (Spielzustand) {#rocket-league-game-state}

Während du Rocket League spielst, speichert der Watcher, was das Spiel an Programme auf deinem eigenen Computer meldet, damit du es dir später auf einer Karte im 3DHeat-Viewer ansehen kannst.

*Technische Details: Adapter `rocketleague-stats`, Art [`gsi`](sources-and-rules.md); er läuft, solange `RocketLeague.exe` läuft, und sucht alle 0,05 s nach neuen Daten.*

## Was aufgezeichnet wird {#what-is-recorded}

- Ballberührungen mit dem Ort des Balls (XYZ, Unreal-Einheiten), wer ihn berührt hat, und die Geschwindigkeiten
- Tore mit dem Ort des Aufpralls, Torschütze, Vorlagengeber und Geschwindigkeit; Lattentreffer mit dem Ort
- Statistik-Feed (Demolierungen, Paraden, Schüsse, epische Paraden, ...), Anstöße, Wiederholungen, Spielbeginn und -ende, Gewinner
- Eigentore, Vorlagen, Paraden, Schüsse, Demos, Berührungen, Spielstand und Teamstände aus UpdateState
- die Endzeile jedes Spielers am Spielende
- deine eigenen Zeilen als `me`: der Spieler, den du in den Einstellungen nennst (`config --set player_names.rocketleague-stats=<name>`), sonst der, dem die Kamera des Spiels außerhalb der Wiederholungen folgt
- keine Autopositionen: die API hat keine

## Woher die Daten kommen {#where-it-comes-from}

Stats-API: TCP-JSON-Strom von 127.0.0.1:49123 (Port in &lt;RL>\TAGame\Config\TAStatsAPI.ini oder DefaultStatsAPI.ini)

## So schaltest du es ein {#how-to-switch-it-on}

`python -m heat3d_watch setup rocketleague-stats --apply` (setzt PacketSendRate=30), danach Rocket League starten

Gib den Befehl in einem Terminal ein, das im Ordner des Watchers geöffnet ist (siehe [Bevor du anfängst](before-you-start.md)). Wenn er fehlschlägt, sagt die letzte Zeile, warum; [Installation und Start](installing-and-running.md) behandelt die üblichen Ursachen.

`python -m heat3d_watch setup rocketleague-stats` listet die Dateien auf, die er ändern würde; `python -m heat3d_watch setup rocketleague-stats --apply` ändert sie und sichert das Original als `<file>.heat3d-backup` (siehe [Befehle](commands.md#setup)). Für jede Änderung gibt er `rocketleague-stats: changed: ...` aus, oder `rocketleague-stats: nothing to change`, wenn es schon eingeschaltet ist.

## So funktioniert es {#how-it-works}

Rocket League: die offizielle Stats-API, ein lokaler Socket, an den das Spiel Spieldaten schreibt.

Eingeschaltet in `<RL>\TAGame\Config\TAStatsAPI.ini` – oder `DefaultStatsAPI.ini`, wenn jene nicht existiert, was das Spiel nur dann liest – unter `[TAGame.MatchStatsExporter_TA]`:

```text
PacketSendRate   UpdateState messages per second; 0 (the default) switches the API off, at most 120
Port             the TCP port the game listens on, default 49123 (WebPort 49124 is a WebSocket copy)
```

Das Spiel ist der Server: Ein Client verbindet sich mit 127.0.0.1:49123 und liest einen Strom von JSON-Objekten `{"Event": name, "Data": {...}}` (manche Builds senden Data als JSON-Zeichenkette), einen nach dem anderen ohne Trennzeichen. Ereignisse werden im Tick gesendet, in dem sie geschehen, unabhängig von der Rate:

```text
UpdateState   MatchGuid, Players[] (Name, PrimaryId, Shortcut, TeamNum 0 blue / 1 orange,
              Score, Goals, Shots, Assists, Saves, Touches, CarTouches, Demos; car state
              only for spectators), Game (Teams[], TimeSeconds, bOvertime, Ball {Speed,
              TeamNum}, bReplay, bHasWinner, Winner, Arena, bHasTarget, Target)
BallHit       Players[] (Name, Shortcut, TeamNum), Ball {PreHitSpeed, PostHitSpeed, Location {X,Y,Z}}
GoalScored    GoalSpeed, GoalTime, ImpactLocation {X,Y,Z}, Scorer, Assister, BallLastTouch
CrossbarHit   BallLocation {X,Y,Z}, BallSpeed, ImpactForce, BallLastTouch
StatfeedEvent EventName, Type, MainTarget, SecondaryTarget
MatchEnded    WinnerTeamNum
MatchCreated, MatchInitialized, CountdownBegin, RoundStarted, GoalReplayStart/WillEnd/End,
MatchPaused/Unpaused, PodiumStart, ReplayCreated, MatchDestroyed, ClockUpdatedSeconds
```

Orte sind Unreal-Einheiten (Zentimeter), Z nach oben; das Spielfeld ist etwa 8200 x 10240 groß, mit den Toren bei Y = ±5120. Positionen der Autos gehören nicht zur API: Einen Ort haben nur der Ball, dort wo er berührt, getroffen oder an die Latte gespielt wurde.

Jede Nachricht wird außerdem vollständig behalten (Regel des 3DHeat-Konverters, docs/converters.md im Repository des Viewers): `heat.raw.parquet`, `type` ist der Ereignisname der Nachricht, `text` das Objekt, so wie es aus dem Strom kam. Ein UpdateState, der Byte für Byte dem davor entspricht (ein pausiertes Spiel, ein Menü), wird einmal behalten und in `unchanged_replies` der meta.json gezählt. Nachrichten zwischen Spielen warten in einem Rückstau auf die Sitzung des nächsten Spiels; was übrig ist, wenn das Spiel schließt, bekommt eine eigene Sitzung. Zeichen zwischen Objekten, die kein JSON sind, werden als "junk" behalten.

Quellen: <https://www.rocketleague.com/en/developer/stats-api> (die offizielle Seite); Schreibweise der Felder und das TCP-Rahmenformat geprüft gegen den Client rlstatsapi (<https://docs.rs/crate/rlstatsapi>, MIT; nur für die Fakten gelesen).

## Positionen und Achsen {#positions-and-axes}

| | |
|---|---|
| Positionen werden aufgezeichnet | ja |
| Hochachse | `z` |
| Einheiten | Unreal-Einheiten (Zentimeter) |
| Für den Viewer gespiegelt | nein |
| Einheitenskala (`scale`: der Viewer multipliziert die Positionen damit) | 1 |

Diese Angaben gehen in die `meta.json` (`axes`) jeder Sitzung und, wenn die Sitzung Positionen hat, in die Fußzeile der `heat.parquet`, damit der 3DHeat-Viewer die Zeilen selbst dreht und skaliert – siehe [Die Daten](the-data.md).

## Mehrspieler {#multiplayer}

- Als online gespielt markiert (`multiplayer`): **ja**. `games --markdown` zeigt dies als "allowed (reads only what the game publishes)".
- Art `gsi`: Es liest nur, was das Spiel oder die Plattform herausgibt (eine Spielzustands-Integration oder lokale API, die das Spiel anbietet), daher zeichnet es auch im Online-Spiel auf wie offline; die Markierung entscheidet nur, ob jemals Speicher gelesen werden darf.
- Speicher: Dieser Adapter liest **niemals** Speicher. Nur `memory`-Adapter lesen Speicher, und nie bei einem Spiel, das als online gespielt markiert ist – siehe [Quellen und Regeln](sources-and-rules.md).

## Aufgezeichnete Statistiken {#statistics-recorded}

Statistikschlüssel, die der Code dieses Adapters namentlich setzt (jeweils die `stats` der Sitzung in `meta.json` und die Tabelle `stats` von `watcher.sqlite`):

`bad_packets`, `demolished`, `other_goals`, `overtime`, `result`, `team_goals`

Ein Schlüssel in geschweiften Klammern wird zur Laufzeit vervollständigt (`score.{team}` ist ein Schlüssel pro Team). Schlüssel, die der Code aus einer Tabelle der Felder des Spiels oder aus den eigenen Statistiknamen des Spiels übernimmt, stehen nicht in dieser Liste; "Was aufgezeichnet wird" oben nennt sie.

## Vollständigkeit {#completeness}

Der Watcher folgt der [Konverterregel](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md) von 3DHeat: Was die Quelle enthält, wird gelesen oder behalten, nie verworfen. Neben den Zeilen wird jedes Paket, jede Seite, jede Zeile oder jede Antwort, die der Adapter empfängt, vollständig in der `heat.raw.parquet` der Sitzung behalten (Spalten `time`, `ms`, `type`, `used`, `payload`, `text`, dann jedes nach Name behaltene Feld; `used` markiert, was auch zu Zeilen wurde), und `selfCheck.completeness` in der `meta.json` zählt jeden `type` – `lost` ist 0.

**Gelesen**

- BallHit (Ort, Wer, Team, Geschwindigkeiten vor und nach dem Schlag), GoalScored (Ort des Aufpralls, Torschütze, Vorlage, Geschwindigkeit, Torzeit), CrossbarHit (Ort, letzte Berührung, Geschwindigkeit, Kraft), StatfeedEvent (Ereignis, Typ, Haupt- und Nebenziel), MatchEnded (Gewinner, Ergebnis); der Name jedes anderen Ereignisses als Zeile
- aus UpdateState: die Arena, das Ziel der Kamera außerhalb der Wiederholungen (wer `me` ist), Teamstände, Tore, Vorlagen, Paraden, Schüsse, Demos, Berührungen, Autoberührungen und Spielstand jedes Spielers (die eigenen als Statistik, alle als `player_result` am Spielende); Verlängerung aus ClockUpdatedSeconds

**Roh behalten**

- jede Nachricht vollständig, so wie sie aus dem Strom kam (`text`), unter ihrem eigenen Ereignisnamen: `UpdateState` (PrimaryId und Shortcut jedes Spielers, die Uhr, Geschwindigkeit und Team des Balls, Teamnamen und -farben, Wiederholungs- und Gewinnerflags und der Zustand der Autos, wo das Spiel ihn sendet), `BallHit`, `GoalScored` (mit der letzten Berührung des Balls), `CrossbarHit`, `StatfeedEvent`, `MatchCreated`, `MatchInitialized`, `CountdownBegin`, `RoundStarted`, `GoalReplayStart`, `GoalReplayWillEnd`, `GoalReplayEnd`, `MatchPaused`, `MatchUnpaused`, `MatchEnded`, `PodiumStart`, `ReplayCreated`, `MatchDestroyed`, `ClockUpdatedSeconds` und jedes Ereignis, das eine spätere Version hinzufügt
- ein UpdateState, der Byte für Byte dem davor entspricht (pausiert, Menüs), wird einmal behalten und gezählt (`unchanged_replies` in meta.json)
- Nachrichten zwischen Spielen: zu ihrer eigenen Zeit vor dem Start des nächsten Spiels; nach dem letzten Spiel in einer eigenen Sitzung (`raw_only` in meta.json)
- `unreadable`: ein Objekt, das keine Nachricht der Stats-API ist; `junk`: Zeichen zwischen den Objekten

**Nicht verfügbar**

- Positionen der Autos und Zustand der Autos während des Spiels: das Spiel sendet sie nur an Zuschauer
- UpdateState zwischen zwei Sendungen: das Spiel sendet PacketSendRate pro Sekunde (`setup` setzt 30, das Spiel erlaubt bis 120); die Ereignisse werden im Tick gesendet, in dem sie geschehen
- die WebSocket-Kopie auf WebPort (49124): dieselben Nachrichten wie der TCP-Port, nicht doppelt gelesen

**Größe**: ein UpdateState ist 1–3 KB für sechs Spieler, 30 pro Sekunde: etwa 100–300 MB pro Stunde in `raw.bin`, solange ein Spiel läuft, und ein Zehntel oder weniger in der zstd-komprimierten `heat.raw.parquet` (geschätzt aus dem dokumentierten Format, nicht am Spiel gemessen)

## Geprüft {#verified}

an Nachrichten im dokumentierten Format getestet, die ein lokaler Fake-Server sendete; nicht gegen das Spiel selbst getestet

## Quelle {#source}

[heat3d_watch/adapters/rocketleague.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/rocketleague.py)

<!-- Generated from the adapter by tools/gen_game_pages.py; change the adapter and run it again rather than editing this page. -->
