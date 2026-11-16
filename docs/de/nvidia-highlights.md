---
title: NVIDIA-Highlights
nav_order: 8
lang: "de"
source: nvidia-highlights.md
source_hash: "cd2a5cc2c5fd"
nav_exclude: true
search_exclude: true
---
# NVIDIA-Highlights {#nvidia-highlights}

Manche Spiele bitten deinen NVIDIA-Grafiktreiber, ein kurzes Video zu speichern, wenn etwas passiert, etwa ein Kill.
Der Watcher vermerkt jeden dieser Momente und setzt ihn, wenn er kann, auf die Karte, dorthin, wo er passierte.

Der Adapter `nvidia-highlights` zeichnet die Clips, Highlights und Screenshots auf, die die NVIDIA-App (oder GeForce Experience) speichert, und gibt jedem einen Ort auf der Karte, wenn er einen finden kann. Diese Seite erklärt, was NVIDIA-Highlights liefern kann und was nicht, welche Dateien der Watcher liest und wie ein Highlight zu einer Position kommt. Die erzeugte Seite des Adapters ist [NVIDIA-Highlights (Plattform)](game-nvidia-highlights.md).

## Was NVIDIA-Highlights liefern kann und was nicht {#what-nvidia-highlights-can-and-cannot-deliver}

Ein Spiel, das NVIDIA-Highlights unterstützt, spricht über GfeSDK mit der NVIDIA-App. Das SDK trägt nur zwei Arten von Nachrichten:

1. **Einmal, beim Start**: die Highlight-Arten, die das Spiel benutzen wird - eine ID (etwa `kill`), eine Bedeutung, Schlagwörter und einen Anzeigenamen je Sprache. Die NVIDIA-App speichert sie je Spiel.
2. **In einem Moment des Spiels**: "Highlight `<id>`, von `<ms>` vor jetzt bis `<ms>` nach jetzt". Das ist die ganze Nachricht: die ID einer Art, die das Spiel angemeldet hat, und zwei Zeitversätze, die der NVIDIA-App sagen, welches Stück ihrer laufenden Aufnahme sie behalten soll.

Das SDK hat **kein Feld für irgendetwas anderes**: keine Position, kein Match oder keine Runde, keinen Gegner, keine Waffe, keinen Punktestand, keine eigenen Daten jeder Art. Ein Spiel kann selbst dann keine Position in ein Highlight legen, wenn es wollte. Wenn der Clip gespeichert wird, fügt die NVIDIA-App eine Datei, einen Spielnamen, eine Länge und eine Zeit hinzu.

Ein Highlight kann also nur sagen: "diese Art von Moment, in diesem Spiel, zu dieser Zeit". Alles Weitere muss von woanders kommen.

## Was der Watcher liest {#what-the-watcher-reads}

Alles wird aus Dateien gelesen, die die NVIDIA-App für ihre eigene Galerie schreibt. Nichts spricht mit dem Treiber oder der App. Der Ordner des NVIDIA Overlay ist
`%LOCALAPPDATA%\NVIDIA Corporation\NVIDIA Overlay`.

| Datei | Was daraus entnommen wird |
|---|---|
| `UGCTracker.json` | der Galerie-Index: jeder Clip und Screenshot mit Pfad, Art (Video, Bild), Unterart (`InstantReplay`, ...), Datum, dem Profilnamen des Spiels, Programm und Kurzname und der Länge (`msDuration`) |
| `GallerySettings.json` | `settings.currentDirectoryV2`, der Aufnahmeordner, und `settings.tempDirectory`, wo Highlights warten (`<temp>\Highlights\<game>`), bis sie gespeichert werden |
| `Highlights\<game>\config.json` | die Highlight-Arten, die jedes Spiel angemeldet hat: ID und der englische Anzeigename (oder die ID, wenn das Spiel keinen gab) |
| der Aufnahmeordner (Standard `%USERPROFILE%\Videos\NVIDIA`) und `<temp>\Highlights` | die Clip- und Screenshot-Dateien selbst (`.mp4`, `.mkv`, `.mov`, `.png`, `.jpg`, `.jpeg`), ein Ordner je Spiel |
| `%LOCALAPPDATA%\NVIDIA Corporation\GfeSDK\<exe>_<pid>.log` | die Anfragen, die GfeSDK-Spiele protokollieren - Zeilen `Posted Request HL...` - damit ein Highlight, das das Spiel angefragt hat, auch dann festgehalten wird, wenn kein Clip behalten wurde. Konfigurationsanfragen (`HLConfigure`, `HLGetConfig`, `HLGetUserSettings`, `HLSetDefaultLocale`) werden übersprungen. |

Für jedes neue Element schreibt der Adapter eine Zeile: `highlight` für ein Video, `screenshot` für ein Bild oder `highlight_request` für eine GfeSDK-Protokollzeile. Ihre Felder:

| Feld | Was es ist |
|---|---|
| `ms` | der Moment: die Zeit im Dateinamen (`<Game> 2026.05.01 - 20.31.28.115.DVR.mp4`, die Ortszeit, als der Clip gespeichert wurde), sonst das Datum des Index, sonst die Änderungszeit der Datei |
| `game` | das Profil des NVIDIA-Spiels, der Name des Ordners oder der Spielname aus dem Dateinamen |
| `clip`, `media` | der Pfad der Datei; `video`, `image` oder `file` |
| `kind` | `InstantReplay`, `Screenshot`, `Highlight` (aus dem temporären Highlight-Ordner) oder die Unterart aus dem Index |
| `duration_s`, `clip_start_ms` | die Länge, aus dem Index oder aus dem eigenen Header des Videos (`moov/mvhd`, ohne das Video zu lesen); der Moment, in dem der Clip beginnt |
| `highlight_id`, `highlight_name` | die Highlight-Art, wenn etwas sie nennt (siehe unten) |
| `exe` | das Programm des Spiels, aus dem Index |
| `x`, `y`, `z`, `session`, `position_from`, `position_lag_ms` | die geliehene Position, wenn eine gefunden wurde (siehe unten) |

Die Sitzungsstatistiken sind `clips`, `screenshots`, `clip_seconds` und `placed` (Elemente, die eine Position bekamen).

**Die Highlight-ID** steht an keiner dokumentierten Stelle. Der Adapter probiert zwei undokumentierte Wege: ein Feld des Galerie-Eintrags, dessen Name "highlight" enthält, und - nur für Dateien im temporären Highlight-Ordner - eine der angemeldeten IDs des Spiels (mindestens 4 Zeichen lang), die im Dateinamen vorkommt. Ein gespeicherter Clip ist nach dem Spiel benannt, und der Name könnte zufällig eine ID wie "kill" enthalten, deshalb wird im Namen eines gespeicherten Clips nicht danach gesucht. Diese beiden Wege haben auf einem echten Rechner noch nicht funktioniert: Es gab weder einen Clip mit einer Highlight-ID noch eine GfeSDK-Anfragezeile, als der Adapter getestet wurde. Der Galerie-Index, die Einstellungen, die Highlight-Definitionen und die Clips wurden an echten Dateien getestet.

### Wann Elemente aufgenommen werden {#when-items-are-recorded}

- Ein Clip wird noch eine Weile nach dem Tastendruck geschrieben. Der Adapter wartet, bis eine Datei bei zwei Blicken (alle 10 s) dieselbe Größe und Zeit hat und mindestens 5 s alt ist.
- Beim ersten Start des Adapters wird alles, was schon in der Galerie und den Protokollen steht, nur vermerkt, nicht aufgenommen, damit jahrelange alte Clips die Statistik nicht überfluten. Was er gesehen hat, wird in `<data>\state\nvidia-highlights.json` gehalten, damit ein Neustart nichts doppelt aufnimmt.
- Elemente werden zu einer Session je Spiel gruppiert. Die Session eines Spiels schließt sich nach 30 Minuten ohne neues Element und endet bei ihrem letzten Moment, nicht erst, wenn das Spiel schließt. Momente, die mehr als 30 Minuten auseinanderliegen, gehen in getrennte Sessions.

## Wie ein Highlight zu einer Position kommt {#how-a-highlight-gets-a-position}

Das Highlight selbst hat keinen Ort. Der Adapter sucht den Moment in den anderen Aufnahmen, die der Watcher vom selben Spiel zur selben Zeit gemacht hat:

1. **Dasselbe Spiel**: die Session-Ordner unter `<data>\sessions\`, deren Spielname zum Namen des Highlights passt. Namen werden in Kleinbuchstaben verglichen, nur Buchstaben und Ziffern. Sie passen, wenn sie gleich sind oder wenn der kürzere mindestens 5 Zeichen hat und im längeren enthalten ist (`Counter-Strike 2` und `Counter-Strike-2`).
2. **Dieselbe Zeit**: Sessions, deren Start und Ende (aus `meta.json`, mit einer Sekunde Spielraum an beiden Enden) den Moment umfassen. Sessions, die ohne Positionen endeten, und die eigenen Sessions des Adapters werden übersprungen.
3. **Die eigene Zeile des Spielers**: in dessen `events.jsonl` die späteste eigene Zeile des Spielers mit einer Position, zum Moment oder davor und höchstens 5 Sekunden davor. Eine Zeile gilt als eigene, wenn ihre Quelle es sagt: `"player": "me"` oder `"own_car": 1` (Rennspiele, die jedes Auto nach seinem Fahrer aufzeichnen) oder ein `player`, das der `player` der Session in `meta.json` ist (der Name, den die Quelle dem Spieler gibt). Siehe [Die eigenen Zeilen des Spielers](the-data.md#the-players-own-rows).

Wird eine Zeile gefunden, bekommt das Highlight ihre `x`, `y`, `z`, seine `session` (oder den Namen des Ordners), `position_from` (der Ordner, aus dem sie kommt) und `position_lag_ms` (wie lange vor dem Moment diese Zeile lag). Die Highlight-Session übernimmt die Achsen dieser Aufnahme, damit sie gleich herum gezeichnet wird. Wird keine Zeile gefunden, bleibt das Highlight ein Moment auf der Zeitleiste ohne Ort.

Wissenswert zur geliehenen Position:

- **Sie ist, wo du warst, als der Clip gespeichert wurde**, nicht, wo die Handlung begann. Der Moment ist die Speicherzeit im Dateinamen, die bei einem Instant Replay ihr Ende ist. `clip_start_ms` sagt, wann der Clip beginnt.
- **Eine andere Quelle muss dasselbe Spiel zur selben Zeit aufgezeichnet haben.** Die, die die eigenen Zeilen des Spielers markieren und so ein Highlight platzieren können: Counter-Strike 2 und Dota 2 per Game-State-Integration, Forza, die Assetto-Corsa-Spiele, EA SPORTS WRC, DiRT Rally 2.0, Richard Burns Rally, BeamNG.drive, Euro Truck Simulator 2, American Truck Simulator, DCS World, X-Plane, Microsoft Flight Simulator, War Thunder, Minecraft und Speicherprofile (als `me`); F1 23/24/25, RaceRoom, Automobilista 2 und Project CARS 2 (die Zeilen deines Autos tragen `own_car` 1, nach dem Autoindex des Spiels, seinem eigenen Platz oder dem betrachteten Teilnehmer); Elite Dangerous (der Name des Kommandanten, in `meta.json` als `player`, da das Journal immer das des Spielers ist).
- **Ein Replay wird nach dem Match umgewandelt**, deshalb kann es nur einen Clip platzieren, der nach der Umwandlung nachgeschlagen wird: Der Clip wird bei seiner Aufnahme platziert, und ein später gespeichertes Replay wird nicht erneut angesehen. Replays aus League of Legends nennen deine Zeilen nach der Riot-ID in den Einstellungen und bekommen mit einem Riot-API-Schlüssel die Uhrzeit, die die Zeitleiste des Matches angibt, sodass sie dann gefunden werden. Eine CS2-Demo kann ein Highlight überhaupt nicht platzieren: Ihre Positionen stehen in der eigenen Tabelle des Konverters, nicht in `events.jsonl`, und eine Demo hat die Ticks des Spiels, aber keine Uhrzeit, mit der sich der Moment eines Clips abgleichen ließe.
- In Rocket League sind die einzigen Zeilen mit einem Ort die Ball-Ereignisse. Ein Ballkontakt von dir ist eine Zeile von dir, sodass ein Highlight dort platziert werden kann, wo du den Ball zuletzt getroffen hast.
- Spiele ganz ohne positionale Quelle (Overwatch 2, Call of Duty, Hunt: Showdown, ...) behalten ihre Highlights als Zeitleiste von Momenten.

## Warum Speicher in Mehrspielerspielen keine Position liefern kann {#why-memory-cannot-give-a-position-in-multiplayer}

Der andere Weg zu einer Position wäre, sie aus dem Speicher zu lesen. Keiner der beiden Speicher funktioniert:

- **Der Speicher von NVIDIA enthält keine Position.** Die NVIDIA-App erhält, was GfeSDK trägt - eine Highlight-ID und zwei Zeitversätze - plus das Video, das sie aufnimmt. Auf NVIDIAs Seite gibt es nirgends eine Position zu lesen. (Der Watcher liest den Speicher von NVIDIA ohnehin nicht; er liest die oben genannten Dateien.)
- **Der Speicher des Spiels ist in Mehrspielerspielen tabu.** Die Position steht im Prozess des Spiels, aber der Watcher liest nie den Speicher eines Mehrspielerspiels: Ein Speicheradapter für ein als online gespieltes Spiel wird abgelehnt, bevor etwas geöffnet wird (siehe [Speicher lesen](memory-reading.md)). Mehrspielerspiele laufen unter Anti-Cheat-Systemen (Easy Anti-Cheat, BattlEye, Vanguard, ...), die es als Betrug behandeln, wenn ein anderes Programm den Prozess des Spiels öffnet, und das kann zu einer Kontosperre führen. Ein Highlight in einem Mehrspielerspiel bekommt deshalb einen Ort nur aus dem, was das Spiel herausgibt: seiner Game-State-Integration oder Telemetrie, aufgezeichnet von einem anderen Adapter zur selben Zeit.
