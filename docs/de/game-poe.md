---
title: "Path of Exile (Logdateien)"
nav_order: 36
lang: "de"
source: game-poe.md
source_hash: "9facfd5a1551"
nav_exclude: true
search_exclude: true
---
# Path of Exile (Logdateien) {#path-of-exile-log-files}

Während du Path of Exile spielst, liest der Watcher die Dateien, die das Spiel schreibt, und speichert, was passiert ist. So kannst du es später als Statistik und Zeitleiste ansehen.

*Technische Details: Adapter `poe`, Art [`log`](sources-and-rules.md); er läuft, solange `PathOfExile.exe`, `PathOfExile_x64.exe`, `PathOfExileSteam.exe`, `PathOfExile_x64Steam.exe`, `PathOfExileEGS.exe`, `PathOfExile_x64EGS.exe`, `PathOfExile_KG.exe` oder `PathOfExile_x64_KG.exe` läuft, und sucht alle 0,5 s nach neuen Daten.*

## Was aufgezeichnet wird {#what-is-recorded}

- betretene Gebiete mit Gebietsstufe, Gebiets-ID und ihrem Seed
- Stufenaufstiege mit Klasse und Stufe
- Tode („has been slain“)
- Spieler, die das Gebiet betreten und verlassen, Flüstern rein und raus, Handelsanfragen, angenommene Handel
- jede Zeile der Client.txt dieser Sitzung, vollständig in heat.raw.parquet
- Tode, gewonnene Stufen, höchste Stufe, betretene Gebiete, verschiedene Gebiete, Flüstern, Handelsanfragen, Handel

## Woher die Daten kommen {#where-it-comes-from}

&lt;Installation>\logs\Client.txt von Path of Exile oder Path of Exile 2 (wird verfolgt; der Installationsordner ist der des laufenden Programms)

## So schaltest du es ein {#how-to-switch-it-on}

Du musst nichts einschalten: Der Watcher liest die Quelle so, wie das Spiel oder die Plattform sie bereitstellt.

## So funktioniert es {#how-it-works}

Path of Exile und Path of Exile 2: das Client-Protokoll, `<Installation>\logs\Client.txt`.

Beide Spiele hängen an eine gemeinsame Client.txt in ihrem Installationsordner, solange sie installiert sind (sie wächst über alle Starts hinweg). Die Zeilen sehen so aus:

```text
2024/01/01 12:00:00 123456789 cff94598 [INFO Client 1234] : You have entered Lioneye's Watch.
2024/01/01 12:00:00 123456789 cff94598 [DEBUG Client 1234] Generating level 2 area "1_1_2" with seed 1
2024/01/01 12:00:00 123456789 cff94598 [INFO Client 1234] : Name (Witch) is now level 2
2024/01/01 12:00:00 123456789 cff94598 [INFO Client 1234] : Name has been slain.
2024/01/01 12:00:00 123456789 cff94598 [INFO Client 1234] @From Name: Hi, I would like to buy your ...
```

- Ortszeit, ein Millisekundenzähler, ein Hash, die Stufe und der Thread, dann das, was das Chatfenster zeigt. Die Meldungen sind die des englischen Clients; ein Client in einer anderen Sprache schreibt übersetzte Meldungen, die hier nicht verstanden werden. Nichts gibt eine Position. Das Format ist von Grinding Gear Games nicht dokumentiert; es ist das Klartext-Protokoll des Spiels, so gelesen, wie Community-Werkzeuge (Handelshelfer, Stufenführer) es seit Jahren lesen – z. B. <https://github.com/klayveR/poe-log-monitor> (MIT) für die Ereignisliste.

Der Installationsordner ist der des laufenden Programms; ohne einen werden die Steam-Bibliotheken und der Standardordner des eigenständigen Clients durchsucht.

Jede Zeile dieser Sitzung wird vollständig in der Roh-Beilage der Session gespeichert (Konverterregel von 3DHeat), ob sie hier etwas bedeutet oder nicht: `type` ist Stufe und Logger in ihren Klammern (`INFO Client`, `DEBUG Client`, `WARN Client`, ...), eine Zeile mit Zeitstempel ohne Klammern ist `untagged`, eine Zeile ohne Zeitstempel `untimed`.

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

`bad_lines`, `character_class`, `deaths`, `level`, `levels_gained`, `trade_requests_received`, `trade_requests_sent`, `trades`, `whispers`, `zones_distinct`, `zones_entered`

Ein Schlüssel in geschweiften Klammern wird zur Laufzeit vervollständigt (`score.{team}` ist ein Schlüssel pro Team). Schlüssel, die der Code aus einer Tabelle der Spielfelder oder aus den eigenen Statistiknamen des Spiels übernimmt, stehen nicht in dieser Liste; „Was aufgezeichnet wird“ oben nennt sie.

## Vollständigkeit {#completeness}

Der Watcher folgt der [Konverterregel](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md) von 3DHeat: Was die Quelle enthält, wird gelesen oder gespeichert, nie weggelassen. Außer den Zeilen wird jedes Paket, jede Seite, jede Zeile und jede Antwort, die der Adapter bekommt, vollständig in der `heat.raw.parquet` der Session gespeichert (Spalten `time`, `ms`, `type`, `used`, `payload`, `text` und alle Felder, die nach Namen behalten werden; `used` markiert, was auch zu Zeilen wurde). `selfCheck.completeness` in `meta.json` zählt jeden `type`; `lost` ist 0.

**Gelesen**

- `You have entered <Zone>`, mit der Gebietsstufe, der Gebiets-ID und dem Seed der `Generating level`-Zeile davor
- `<Name> (<Klasse>) is now level <n>`, `<Name> has been slain`, Spieler, die das Gebiet betreten und verlassen, Flüstern rein und raus (mit der Angabe, ob es eine Handelsanfrage ist), angenommener und abgebrochener Handel

**Roh gespeichert**

- jede Zeile dieser Sitzung vollständig, `type` = Stufe und Logger in ihren Klammern (`INFO Client`, `DEBUG Client`, `WARN Client`, `CRIT Client`, ...), `used`, wo sie zu einer Zeile wurde: globaler, Handels-, Gruppen- und Gildenchat, `Connecting to instance server`, Hinweise zu AFK und DND, die Antworten auf Chatbefehle wie `/played` und `/deaths`, die Lade- und Engine-Zeilen des Clients – gespeichert, noch nicht zu Zeilen gemacht
- eine Zeile mit Zeitstempel ohne Klammern (`***** LOG FILE OPENING *****`) als `untagged`, eine Zeile ohne Zeitstempel als `untimed`

**Nicht verfügbar**

- Positionen: Nichts im Protokoll gibt eine
- was ein Client in einer anderen Sprache schreibt: Die Zeilen werden gespeichert, aber nur die englischen Meldungen werden zu Zeilen
- Zeilen früherer Starts: Client.txt wächst über alle Starts hinweg; Zeilen, die vor diesem Lauf des Spiels datiert sind, bleiben liegen (sie wurden beim Spielen schon gespeichert)
- Tötungen, Schaden, Beute und der Passivbaum: Das Spiel protokolliert sie nicht

**Größe**: Client.txt wächst etwa 0,3–3 MB pro Stunde (meist durch DEBUG-Zeilen beim Laden von Gebieten, mehr bei lebhaftem Handelschat); zstd macht in heat.raw.parquet etwa ein Zehntel daraus

## Geprüft {#verified}

getestet mit synthetischen Client.txt-Zeilen im Format des Spiels; noch nicht gegen das Spiel getestet

## Quelle {#source}

[heat3d_watch/adapters/poe.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/poe.py)

<!-- Aus dem Adapter erzeugt von tools/gen_game_pages.py; ändere den Adapter und führe das Skript erneut aus, statt diese Seite zu bearbeiten. -->
