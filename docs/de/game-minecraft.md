---
title: "Minecraft (Logdateien)"
nav_order: 33
lang: "de"
source: game-minecraft.md
source_hash: "35cfea9d36a0"
nav_exclude: true
search_exclude: true
---
# Minecraft (Logdateien) {#minecraft-log-files}

Während du Minecraft spielst, liest der Watcher die Dateien, die das Spiel schreibt, und speichert, was passiert ist, damit du es dir später auf einer Karte im 3DHeat-Viewer ansehen kannst.

*Technische Details: Adapter `minecraft`, Art [`log`](sources-and-rules.md); er läuft, solange `javaw.exe` oder `java.exe` läuft, und sucht alle 0,5 s nach neuen Daten.*

## Was aufgezeichnet wird {#what-is-recorded}

- Position des eigenen und der anderen Spieler (Blöcke = m, y nach oben) jedes Mal, wenn die Welt speichert; die Dimension als Sitzung
- Spawn mit Position, wenn sich ein Spieler am (integrierten) Server anmeldet
- Beitritte, Austritte, Tode mit der Todesmeldung, Fortschritte, Chatzeilen
- Tode, Fortschritte, Chatnachrichten; aus der Statistikdatei: Spielzeit, Distanz, Mob- und Spielerabschüsse, Sprünge, Schaden, abgebaute Blöcke, hergestellte Gegenstände (Anteil dieser Sitzung)
- jede Logzeile und jede gespeicherte Statistik-, Fortschritts- und Spielerdatei vollständig in heat.raw.parquet

## Woher die Daten kommen {#where-it-comes-from}

%APPDATA%\\.minecraft\logs\latest.log (verfolgt), saves\\&lt;Welt>\stats\\&lt;uuid>.json und saves\\&lt;Welt>\playerdata\\&lt;uuid>.dat / level.dat (gzip-NBT), gelesen, wenn das Spiel sie speichert

## So schaltest du es ein {#how-to-switch-it-on}

Du musst nichts einschalten: Der Watcher liest die Quelle so, wie das Spiel oder die Plattform sie bereitstellt.

## So funktioniert es {#how-it-works}

Minecraft (Java Edition): die Log-, Statistik- und Spielerdateien, die das Spiel schreibt.

Wo (`%APPDATA%\.minecraft\`):

* `logs\latest.log` – das Log des Spiels, bei jedem Start neu (das alte wird in eine datierte .log.gz gepackt). Zeilen `[hh:mm:ss] [thread/LEVEL]: message` (Mod-Loader schreiben `[ddMMMyyyy hh:mm:ss.mmm] [thread/LEVEL] [logger/]: ...`). Was Spieler im Chat sehen, steht darin: Beitritte und Austritte, Todesmeldungen, Fortschritte, Chat – der integrierte Server einer Einzelspielerwelt schreibt dieselben Zeilen noch einmal, daher zählt eine Zeile, die sich innerhalb derselben Sekunde wiederholt, nur einmal. "Setting user: <name>" nennt den Spieler; die Meldung des Servers "<name>[...] logged in with entity id N at (x, y, z)" zeigt, wo er erschien.
* `saves\<Welt>\stats\<uuid>.json` – der Statistikbildschirm, geschrieben, wenn die Welt speichert (automatisches Speichern alle paar Minuten und beim Verlassen): `stats` -> `minecraft:custom` (play_time in Ticks, mob_kills, \*_one_cm-Distanzen, jump, ...), `minecraft:mined`, `minecraft:crafted`, ... Summen für die Welt; die Werte der Sitzung sind die Differenz zu dem, was die Datei beim Start des Spiels sagte. Format: <https://minecraft.wiki/w/Statistics>
* `saves\<Welt>\playerdata\<uuid>.dat` (und `level.dat` -> Data -> Player beim Einzelspielerhost) – gzip-komprimiertes NBT, bei denselben Speicherungen geschrieben: `Pos` [x, y, z] als Doubles, `Rotation` [Gier, Nicken], `Dimension` ("minecraft:overworld"; ein int 0/-1/1 vor 1.16). NBT nach <https://minecraft.wiki/w/NBT_format> – hier von einem kleinen eigenen Leser gelesen.
* `saves\<Welt>\advancements\<uuid>.json` – der Fortschritt des Fortschrittsbildschirms, bei denselben Speicherungen geschrieben.

Koordinaten sind Blöcke, ein Block ein Meter, y nach oben; x nach Osten, z nach Süden – ein rechtshändiges System, so gezeichnet, wie es ist. Positionen kommen nur, wenn die Welt speichert, daher ist eine Route nur ein paar Punkte pro automatischer Speicherung, keine Spur; die Dimension ist die `session`, daher wird der Nether nicht über die Oberwelt gezeichnet.

Alles Gelesene wird vollständig in der Roh-Beilage der Sitzung behalten (Regel des 3DHeat-Konverters): jede Logzeile unter ihrer Stufe (`INFO`, `WARN`, `ERROR`, ...; eine Zeile ohne den Kopf in Klammern, etwa ein Stacktrace, als `untagged`), und jede gespeicherte Datei unter ihrer Art (`stats`, `advancements`, `playerdata`, `level.dat`) – JSON als Text, NBT als seine Bytes. Die Zahlen einer Statistikdatei sind nur gegen das zu verstehen, was sie beim Start des Spiels sagte, daher wird auch diese erste Fassung behalten (`baseline`), beim ersten Mal, wenn sich die Datei ändert.

## Positionen und Achsen {#positions-and-axes}

| | |
|---|---|
| Positionen werden aufgezeichnet | ja |
| Hochachse | `y` |
| Einheiten | Blöcke (1 Block = 1 m) |
| Für den Viewer gespiegelt | nein |
| Einheitenskala (`scale`: der Viewer multipliziert die Positionen damit) | 1 |

Diese Angaben gehen in die `meta.json` (`axes`) jeder Sitzung und, wenn die Sitzung Positionen hat, in die Fußzeile der `heat.parquet`, damit der 3DHeat-Viewer die Zeilen selbst dreht und skaliert – siehe [Die Daten](the-data.md).

## Mehrspieler {#multiplayer}

- Als online gespielt markiert (`multiplayer`): **ja**. `games --markdown` zeigt dies als "allowed (reads only what the game publishes)".
- Art `log`: Es liest nur, was das Spiel oder die Plattform herausgibt (Dateien, die das Spiel während des Laufs schreibt), daher zeichnet es auch im Online-Spiel auf wie offline; die Markierung entscheidet nur, ob jemals Speicher gelesen werden darf.
- Speicher: Dieser Adapter liest **niemals** Speicher. Nur `memory`-Adapter lesen Speicher, und nie bei einem Spiel, das als online gespielt markiert ist – siehe [Quellen und Regeln](sources-and-rules.md).

## Aufgezeichnete Statistiken {#statistics-recorded}

Statistikschlüssel, die der Code dieses Adapters namentlich setzt (jeweils die `stats` der Sitzung in `meta.json` und die Tabelle `stats` von `watcher.sqlite`):

`advancements`, `bad_files`, `bad_lines`, `chat_messages`, `deaths`, `joins`, `others_deaths`, `world`

Ein Schlüssel in geschweiften Klammern wird zur Laufzeit vervollständigt (`score.{team}` ist ein Schlüssel pro Team). Schlüssel, die der Code aus einer Tabelle der Felder des Spiels oder aus den eigenen Statistiknamen des Spiels übernimmt, stehen nicht in dieser Liste; "Was aufgezeichnet wird" oben nennt sie.

## Vollständigkeit {#completeness}

Der Watcher folgt der [Konverterregel](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md) von 3DHeat: Was die Quelle enthält, wird gelesen oder behalten, nie verworfen. Neben den Zeilen wird jedes Paket, jede Seite, jede Zeile oder jede Antwort, die der Adapter empfängt, vollständig in der `heat.raw.parquet` der Sitzung behalten (Spalten `time`, `ms`, `type`, `used`, `payload`, `text`, dann jedes nach Name behaltene Feld; `used` markiert, was auch zu Zeilen wurde), und `selfCheck.completeness` in der `meta.json` zählt jeden `type` – `lost` ist 0.

**Gelesen**

- latest.log: der Name des Spielers (`Setting user`), Anmeldungen mit Position, Beitritte, Austritte, Tode mit der Todesmeldung, Fortschritte, Chatzeilen, das Anhalten des Servers
- stats/<uuid>.json: Spielzeit, Distanz, Mob- und Spielerabschüsse, Sprünge, verursachter und erlittener Schaden, abgebaute Blöcke, hergestellte Gegenstände – der Anteil dieser Sitzung
- playerdata/<uuid>.dat und level.dat (NBT): Position, Dimension, Gier, Nicken, Gesundheit, XP-Stufe

**Roh behalten**

- jede latest.log-Zeile vollständig, `type` = ihre Stufe (`INFO`, `WARN`, `ERROR`, `DEBUG`, `FATAL`), mit dem Thread des Loggers in `thread`, `used`, wo daraus eine Zeile wurde; eine Zeile ohne den Kopf in Klammern (ein Stacktrace, ein Banner eines Mods) als `untagged`
- jede stats/<uuid>.json vollständig als Text, `type` `stats` (`used`: seine Zahlen stehen in der Statistik), mit ihrer ersten Fassung seit dem Start des Spiels als `baseline`
- jede advancements/<uuid>.json vollständig als Text, `type` `advancements` (jedes Kriterium und wann es erfüllt wurde; noch nicht in Zeilen umgewandelt)
- jede playerdata/<uuid>.dat und level.dat vollständig als Bytes (gzip-NBT), `type` `playerdata` / `level.dat`, `used`, wo daraus eine Position wurde: Inventar, Endertruhe, Effekte, Spawnpunkt, Spielregeln, Weltseed und Weltzeit stehen nur hier
- jede gespeicherte Datei hat `world` und `file` (ihr Pfad unter `saves`)

**Nicht verfügbar**

- eine Positionsspur: das Spiel schreibt die Position des Spielers nur, wenn die Welt speichert (alle paar Minuten und beim Verlassen)
- Positionen auf einem Server, den jemand anderes betreibt: dessen Weltdateien liegen auf dem Server, nicht hier; dann wird nur das Log gelesen
- die Welt selbst (Region-Dateien .mca, Entitäten, data/\*.dat-Karten und Raids): groß, und es ist das Gelände, nicht das Spiel
- Logs früherer Sitzungen (logs/\*.log.gz): behalten, wenn sie gespielt wurden
- Bedrock Edition: sie schreibt kein solches Log und keine solchen Dateien

**Größe**: latest.log 0,1–2 MB pro Stunde (mit Mods mehr); eine Statistikdatei 5–50 KB und eine Spielerdatei 5–100 KB pro automatischer Speicherung, level.dat 1–20 KB – insgesamt etwa 1–5 MB pro Stunde; zstd in heat.raw.parquet macht den Text etwa auf ein Zehntel (die NBT-Dateien sind schon gzip-komprimiert)

## Geprüft {#verified}

an synthetischen Logzeilen, Statistik-JSON und NBT-Dateien getestet, die aus den veröffentlichten Formaten gebaut wurden; nicht gegen das Spiel selbst getestet

## Quelle {#source}

[heat3d_watch/adapters/minecraft.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/minecraft.py)

<!-- Generated from the adapter by tools/gen_game_pages.py; change the adapter and run it again rather than editing this page. -->
