---
title: "League of Legends (Spielzustand)"
nav_order: 29
lang: "de"
source: game-lol-live.md
source_hash: "75c67c6fe84f"
nav_exclude: true
search_exclude: true
---
# League of Legends (Spielzustand) {#league-of-legends-game-state}

Während du League of Legends spielst, speichert der Watcher, was das Spiel an Programme auf deinem eigenen Computer meldet. So kannst du es später als Statistik und Zeitleiste ansehen.

*Technische Details: Adapter `lol-live`, Art [`gsi`](sources-and-rules.md); er läuft, solange `League of Legends.exe` läuft, und sucht alle 0,5 s nach neuen Daten.*

## Was aufgezeichnet wird {#what-is-recorded}

- keine Positionen: Die API hat keine
- Killfeed: Abschüsse, Tode und Assists des Spielers, Abschüsse anderer Champions mit Killer, Opfer, Helfern
- Drachen, Herolde, Barone, Türme, Inhibitoren, Mehrfachabschüsse, Asse, Erstblut, Spielbeginn und -ende
- eigene Abschüsse, Tode, Assists, Minionpunkte, Wächterpunkte, Stufe, Gold, Champion, Spielzeit, Ergebnis
- Ziele, die das Team des Spielers eingenommen hat

## Woher die Daten kommen {#where-it-comes-from}

Live-Client-Data-API des Spiel-Clients, <https://127.0.0.1:2999/liveclientdata/> (allgamedata, eventdata), während einer Partie

## So schaltest du es ein {#how-to-switch-it-on}

Du musst nichts einschalten: Der Watcher liest die Quelle so, wie das Spiel oder die Plattform sie bereitstellt.

## So funktioniert es {#how-it-works}

League of Legends: die Live-Client-Data-API, die der Spiel-Client während einer Partie bereitstellt.

Während eine Partie läuft (auch im Übungswerkzeug und im Zuschauermodus), antwortet `League of Legends.exe` unter <https://127.0.0.1:2999> mit dem, was der Spieler in der eigenen Oberfläche des Spiels sehen kann:

```text
/liveclientdata/allgamedata          activePlayer (riotId, level, currentGold, championStats),
                                     allPlayers (championName, team ORDER/CHAOS, level,
                                     scores: kills, deaths, assists, creepScore, wardScore),
                                     events, gameData (gameMode, gameTime s, mapName)
/liveclientdata/eventdata?eventID=N  {"Events": [...]} ab EventID N: GameStart,
                                     MinionsSpawning, FirstBlood, FirstBrick, TurretKilled,
                                     InhibKilled, InhibRespawningSoon, InhibRespawned,
                                     DragonKill, HeraldKill, BaronKill, ChampionKill
                                     (KillerName, VictimName, Assisters), Multikill
                                     (KillStreak), Ace (Acer, AcingTeam), GameEnd (Result)
```

Es gibt keine Positionen: Die API hat keine, deshalb besteht eine League-Session aus Ereignissen und Statistiken, ohne Heat-Tabelle. Das Zertifikat ist selbst signiert, von Riots eigenem Stammzertifikat (`riotgames.pem`, veröffentlicht unter <https://static.developer.riotgames.com/docs/lol/riotgames.pem>). Seine Nutzungsbedingungen sind nicht angegeben, deshalb wird es nicht mitgeliefert: Lege es unter `<Daten>\riotgames.pem` ab, dann wird die Verbindung damit geprüft; ohne es ist die Prüfung ausgeschaltet – und nur für 127.0.0.1, die einzige Adresse, mit der dieser Adapter spricht.

Riots Richtlinie erlaubt Werkzeugen, zu zeigen, was der Spieler aus dem Spiel selbst wissen kann, und nichts, was darüber hinaus berechnet wird (keine Timer des Gegners): Das hier zeichnet den Killfeed und die Anzeigetafel auf, die der Spieler sieht, und die eigenen Zahlen des Spielers.

Jede Antwort wird außerdem vollständig gespeichert (Konverterregel von 3DHeat, docs/converters.md im Repository des Viewers): `heat.raw.parquet`, `type` ist der Endpunkt („allgamedata“, „eventdata“), `text` das JSON, wie der Client es gesendet hat, `status`, wenn es nicht 200 war. Eine Antwort, die Byte für Byte der vorherigen ihres Endpunkts entspricht (die Ereignisliste, solange nichts passiert), wird einmal gespeichert und in `unchanged_replies` der meta.json gezählt. allgamedata enthält alles, was die anderen Endpunkte liefern (activeplayer\*, playerlist, playerscores, playeritems, playersummonerspells, playermainrunes, gamestats), deshalb werden sie nicht einzeln abgefragt. Antworten vor einer Partie (der Ladebildschirm) warten in einem Rückstau und gehen in die Session der Partie; nach GameEnd bleibt die Session offen, bis der Client beendet wird, damit die Antworten des Endbildschirms mit ihr gespeichert werden.

Quelle: <https://developer.riotgames.com/docs/lol#game-client-api>

## Positionen und Achsen {#positions-and-axes}

| | |
|---|---|
| Positionen aufgezeichnet | nein |
| Oben-Achse | `z` |
| Einheiten | keine (keine Positionen) |
| Für den Viewer gespiegelt | keine |
| Einheitenskala (`scale`: der Viewer multipliziert die Positionen damit) | 1 |

Diese Werte landen in der `meta.json` jeder Session (`axes`) und, wenn die Session Positionen hat, im Footer der `heat.parquet`. So dreht und skaliert der 3DHeat-Viewer die Zeilen selbst – siehe [Die Daten](the-data.md).

## Mehrspieler {#multiplayer}

- Als online gespielt markiert (`multiplayer`): **ja**. `games --markdown` zeigt das als „allowed (reads only what the game publishes)“.
- Art `gsi`: Es liest nur, was das Spiel oder die Plattform herausgibt (eine Spielzustands-Anbindung oder lokale API, die das Spiel bereitstellt). Deshalb zeichnet es auch im Online-Spiel auf, nicht nur offline. Die Markierung entscheidet nur, ob Speicher überhaupt gelesen werden darf.
- Speicher: Dieser Adapter liest **nie** den Speicher. Nur `memory`-Adapter lesen Speicher, und nie bei einem Spiel, das als online gespielt markiert ist – siehe [Quellen und Regeln](sources-and-rules.md).

## Aufgezeichnete Statistiken {#statistics-recorded}

Statistik-Schlüssel, die der Code dieses Adapters beim Namen setzt (das `stats` jeder Session in `meta.json` und die Tabelle `stats` in `watcher.sqlite`):

`bad_packets`, `champion`, `game_time`, `gold`, `level`, `result`

Ein Schlüssel in geschweiften Klammern wird zur Laufzeit vervollständigt (`score.{team}` ist ein Schlüssel pro Team). Schlüssel, die der Code aus einer Tabelle der Spielfelder oder aus den eigenen Statistiknamen des Spiels übernimmt, stehen nicht in dieser Liste; „Was aufgezeichnet wird“ oben nennt sie.

## Vollständigkeit {#completeness}

Der Watcher folgt der [Konverterregel](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md) von 3DHeat: Was die Quelle enthält, wird gelesen oder gespeichert, nie weggelassen. Außer den Zeilen wird jedes Paket, jede Seite, jede Zeile und jede Antwort, die der Adapter bekommt, vollständig in der `heat.raw.parquet` der Session gespeichert (Spalten `time`, `ms`, `type`, `used`, `payload`, `text` und alle Felder, die nach Namen behalten werden; `used` markiert, was auch zu Zeilen wurde). `selfCheck.completeness` in `meta.json` zählt jeden `type`; `lost` ist 0.

**Gelesen**

- der Killfeed aus eventdata: jedes Ereignis einmal, seine benannten Felder entschlüsselt (Killer, Opfer und Helfer mit Champion und Team, Bauwerke und ihre Seite, Drachenart, Übernahmen, Mehrfachabschüsse, Asse, Erstblut, das Ergebnis); jedes andere Feld eines Ereignisses steht in seiner Zeile unter seinem eigenen Namen
- aus allgamedata: eigene Abschüsse, Tode, Assists, Minionpunkte, Wächterpunkte, Stufe, Gold, Champion, die Spielzeit, Spielmodus und Karte

**Roh gespeichert**

- `allgamedata`: jede Antwort vollständig (`text`), alle 2 s – activePlayer (Fähigkeiten, jeder Champion-Wert, volle Runen, Gold, Stufe), allPlayers (Gegenstände mit Slots und Preisen, Runen, Beschwörerzauber, Punkte, Stufe, tot und Timer bis zum Wiederbeleben, Skin, Lane, Bot), die Ereignisse, gameData (Modus, Zeit, Karte, Gelände); `used` ist wahr, solange die Partie läuft, falsch auf dem Endbildschirm
- `eventdata`: jede Antwort vollständig, alle 0,5 s ab der nächsten Ereignis-ID angefragt; `used` ist wahr, wenn sie neue Ereignisse brachte
- eine Antwort, die Byte für Byte der vorherigen ihres Endpunkts entspricht, wird einmal gespeichert und gezählt (`unchanged_replies` in meta.json); Fehlerantworten (das RESOURCE_NOT_FOUND des Ladebildschirms) werden mit ihrem `status` vor dem Start der Partie gespeichert

**Nicht verfügbar**

- Positionen: Die API hat keine (keine Minikarte, keine Koordinaten)
- die anderen Endpunkte (activeplayer, activeplayername, activeplayerabilities, activeplayerrunes, playerlist, playerscores, playersummonerspells, playermainrunes, playeritems, gamestats): Jeder liefert einen Teil von allgamedata, deshalb werden sie nicht abgefragt
- die Replay-API (`/replay/*` am selben Port): Sie spielt Wiederholungen und beobachtete Partien ab, sobald sie in game.cfg eingeschaltet ist; sie gehört nicht zu einer gespielten Partie
- die Endpunkte der Lockdatei des League-Clients: keine veröffentlichte API (siehe Quellen und Regeln)
- Werte zwischen zwei Abfragen: Die API antwortet, wenn sie gefragt wird, und schickt nichts von sich aus; die Anzeigetafel wird alle 2 s abgefragt, die Ereignisse alle 0,5 s

**Größe**: allgamedata ist 15–40 KB (es enthält die ganze, wachsende Ereignisliste) alle 2 s: etwa 30–70 MB pro Stunde in `raw.bin`; eventdata fügt wenig hinzu, weil unveränderte Antworten gezählt und nicht gespeichert werden; zstd schrumpft das wiederholte JSON in `heat.raw.parquet` auf wenige MB pro Stunde (geschätzt aus dem dokumentierten Format)

## Geprüft {#verified}

getestet gegen einen lokalen Fake-Server, der Antworten im dokumentierten Format liefert; noch nicht gegen das Spiel getestet

## Quelle {#source}

[heat3d_watch/adapters/lol.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/lol.py)

<!-- Aus dem Adapter erzeugt von tools/gen_game_pages.py; ändere den Adapter und führe das Skript erneut aus, statt diese Seite zu bearbeiten. -->
