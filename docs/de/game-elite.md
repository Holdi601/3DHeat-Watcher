---
title: "Elite Dangerous (Logdateien)"
nav_order: 18
lang: de
source: game-elite.md
source_hash: "bb5bcf75553a"
nav_exclude: true
search_exclude: true
---
# Elite Dangerous (Logdateien) {#elite-dangerous-log-files}

Während du Elite Dangerous spielst, liest der Watcher die Dateien, die das Spiel schreibt, und speichert, was passiert ist, damit du es dir später auf einer Karte im 3DHeat-Viewer ansehen kannst.

*Technische Details: Adapter `elite`, Art [`log`](sources-and-rules.md); er läuft, solange `EliteDangerous64.exe` läuft, und sucht alle 0,25 s nach neuen Daten.*

## Was aufgezeichnet wird {#what-is-recorded}

- jedes Journal-Ereignis unter seinem Journal-Namen, mit seinen einfachen Feldern
- Position in der Galaxie (StarPos, Lichtjahre) bei Sprüngen, Standorten, Spawns, Toden, Andocken, Landen
- Spawn bei LoadGame/Resurrect, Tod bei Died, angedockt/abgedockt, Aufsetzen/Abheben, Sprung, session_end
- Route an der Planetenoberfläche aus Status.json: Breite, Länge, Höhe, Kurs und Meter in einer Tangentialebene pro Himmelskörper (Sitzung = Name des Körpers), dazu die übrigen einfachen Felder von Status.json (Flags, Flags2, GuiFocus, LegalState, ...)
- jede Journal-Zeile und jede Begleitdatei vollständig in heat.raw.parquet
- Sprünge, zurückgelegte Distanz bei Sprüngen, Tode, Abschüsse, verdiente Credits, abgeschlossene Missionen, gescannte Himmelskörper, besuchte Systeme, Andockvorgänge, Landungen

## Woher die Daten kommen {#where-it-comes-from}

Spielerjournal %USERPROFILE%\Saved Games\Frontier Developments\Elite Dangerous\Journal.\*.log (neueste Datei, wird beim Schreiben verfolgt), Status.json und die übrigen Begleit-\*.json-Dateien (Market, Outfitting, Shipyard, NavRoute, Cargo, ModulesInfo, ShipLocker, Backpack, FCMaterials) im selben Ordner

## So schaltest du es ein {#how-to-switch-it-on}

Du musst nichts einschalten: Der Watcher liest die Quelle so, wie das Spiel oder die Plattform sie bereitstellt.

## So funktioniert es {#how-it-works}

Elite Dangerous: das Spielerjournal und Status.json, die das Spiel während des Laufs schreibt.

Wo: `%USERPROFILE%\Saved Games\Frontier Developments\Elite Dangerous\`

* `Journal.<yyyy-mm-ddThhmmss>.<part>.log` – ein JSON-Objekt pro Zeile, eine Datei pro Start (eine lange Sitzung setzt sich in Teil .02, .03 ... fort). Jede Zeile hat `timestamp` (UTC, ISO 8601) und `event`. Galaxie-Positionen sind das `StarPos` [x, y, z] des Systems, in Lichtjahren von Sol, bei `FSDJump`, `Location` und `CarrierJump`. Das galaktische Koordinatensystem von Elite hat y nach oben (zur galaktischen Nordseite), z zum galaktischen Kern und x zur galaktischen Länge 270 – ein linkshändiges System, daher spiegelt der Viewer z, damit es richtig herum gezeichnet wird.
* `Status.json` – wird jedes Mal ganz neu geschrieben, wenn sich der Zustand des Schiffs ändert: `Flags` und in der Nähe eines Planeten `Latitude`, `Longitude` (Grad), `Altitude` (Meter), `Heading`, `BodyName` und `PlanetRadius` (Meter).
* Die übrigen Begleitdateien, jede wird ganz neu geschrieben, wenn das passende Journal-Ereignis geschrieben wird: `Market.json`, `Outfitting.json`, `Shipyard.json`, `NavRoute.json`, `Cargo.json`, `ModulesInfo.json`, `ShipLocker.json`, `Backpack.json`, `FCMaterials.json`. Jede `*.json` des Ordners, die das Spiel in dieser Sitzung schreibt, wird bei jeder Änderung vollständig unter ihrem Dateinamen behalten (Regel des 3DHeat-Konverters: Was die Quelle enthält, wird gelesen oder behalten).

Jede Journal-Zeile wird vollständig in der Roh-Beilage der Sitzung unter ihrem `event` behalten, jede Begleitdatei unter ihrem Dateinamen; eine Zeile, die kein JSON ist, unter `unparsed`.

Positionen an der Oberfläche werden pro Himmelskörper in eine lokale Tangentialebene gelegt, in Metern: Der erste Messpunkt auf einem Körper ist sein Ursprung, x nach Osten, z nach Norden, y nach oben (Höhe), mit derselben Händigkeit wie das galaktische System. Die Zeilen tragen den Namen des Körpers als `session`, damit eine Fahrt oder ein Spaziergang auf einem Planeten als eigene Route gezeichnet wird. Galaxie-Zeilen haben die Sitzung "galaxy". Beide Maßstäbe liegen in einer Tabelle; die Sitzung wählst du im Viewer.

Format: Das Handbuch "Elite Dangerous Player Journal" von Frontier (mit jedem Update in den offiziellen Foren veröffentlicht, <https://forums.frontier.co.uk/> – "Journal Manual", v4.x); Ereignisse und Felder wie dort beschrieben; die Flags von Status.json nach dem Kapitel "Status File" desselben Handbuchs.

## Positionen und Achsen {#positions-and-axes}

| | |
|---|---|
| Positionen werden aufgezeichnet | ja |
| Hochachse | `y` |
| Einheiten | Lichtjahre (Galaxie-Zeilen, Sitzung 'galaxy'); Meter östlich/oben/nördlich des ersten Messpunkts auf einem Körper (Oberflächen-Zeilen, Sitzung = Name des Körpers) |
| Für den Viewer gespiegelt | `z` |
| Einheitenskala (`scale`: der Viewer multipliziert die Positionen damit) | 1 |

Diese Angaben gehen in die `meta.json` (`axes`) jeder Sitzung und, wenn die Sitzung Positionen hat, in die Fußzeile der `heat.parquet`, damit der 3DHeat-Viewer die Zeilen selbst dreht und skaliert – siehe [Die Daten](the-data.md).

## Mehrspieler {#multiplayer}

- Als online gespielt markiert (`multiplayer`): **ja**. `games --markdown` zeigt dies als "allowed (reads only what the game publishes)".
- Art `log`: Es liest nur, was das Spiel oder die Plattform herausgibt (Dateien, die das Spiel während des Laufs schreibt), daher zeichnet es auch im Online-Spiel auf wie offline; die Markierung entscheidet nur, ob jemals Speicher gelesen werden darf.
- Speicher: Dieser Adapter liest **niemals** Speicher. Nur `memory`-Adapter lesen Speicher, und nie bei einem Spiel, das als online gespielt markiert ist – siehe [Quellen und Regeln](sources-and-rules.md).

## Aufgezeichnete Statistiken {#statistics-recorded}

Statistikschlüssel, die der Code dieses Adapters namentlich setzt (jeweils die `stats` der Sitzung in `meta.json` und die Tabelle `stats` von `watcher.sqlite`):

`bad_lines`, `bodies_scanned`, `carrier_jumps`, `credits`, `credits_earned`, `deaths`, `distance_ly`, `dockings`, `jumps`, `kills`, `landings`, `missions_completed`, `ship`, `surface_fixes`, `systems_visited`

Ein Schlüssel in geschweiften Klammern wird zur Laufzeit vervollständigt (`score.{team}` ist ein Schlüssel pro Team). Schlüssel, die der Code aus einer Tabelle der Felder des Spiels oder aus den eigenen Statistiknamen des Spiels übernimmt, stehen nicht in dieser Liste; "Was aufgezeichnet wird" oben nennt sie.

## Vollständigkeit {#completeness}

Der Watcher folgt der [Konverterregel](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md) von 3DHeat: Was die Quelle enthält, wird gelesen oder behalten, nie verworfen. Neben den Zeilen wird jedes Paket, jede Seite, jede Zeile oder jede Antwort, die der Adapter empfängt, vollständig in der `heat.raw.parquet` der Sitzung behalten (Spalten `time`, `ms`, `type`, `used`, `payload`, `text`, dann jedes nach Name behaltene Feld; `used` markiert, was auch zu Zeilen wurde), und `selfCheck.completeness` in der `meta.json` zählt jeden `type` – `lost` ist 0.

**Gelesen**

- jede Journal-Zeile als Zeile unter ihrem `event`, mit ihren einfachen Feldern (der lokalisierte Text, wo das Spiel einen liefert; Texte über 300 Zeichen werden in der Zeile gekürzt)
- Galaxie-Zeilen (StarPos) bei FSDJump, CarrierJump, Location, LoadGame, Resurrect, Died, Docked, Undocked, Touchdown, Liftoff, Shutdown; Oberflächen-Zeilen aus Status.json und Touchdown/Liftoff
- die einfachen Felder von Status.json (Flags, Flags2, GuiFocus, LegalState, Cargo, FireGroup, Oxygen, Health, Temperature, Gravity, SelectedWeapon, ...) auf den Oberflächen-Zeilen
- die Statistiken: Sprünge, Distanz, Tode, Abschüsse, verdiente Credits, Missionen, gescannte Körper, besuchte Systeme, Andockvorgänge, Landungen

**Roh behalten**

- jede Journal-Zeile vollständig, `type` = ihr `event` (FSDJump, Scan, Music, ReceiveText, ...), `used` true: die Listen und Objekte, die die Zeilen auslassen (StarPos, Factions, Rewards, Killers, Materials, Modules, ...), gibt es nur hier
- eine Journal-Zeile, die kein JSON ist, `type` `unparsed`
- jede Begleitdatei vollständig, jedes Mal wenn das Spiel sie neu schreibt, `type` = ihr Dateiname: `Status.json` (`used`, wenn daraus eine Oberflächen-Zeile wurde), `Market.json`, `Outfitting.json`, `Shipyard.json`, `NavRoute.json`, `Cargo.json`, `ModulesInfo.json`, `ShipLocker.json`, `Backpack.json`, `FCMaterials.json` und jede andere `*.json`, die das Spiel dort schreibt

**Nicht verfügbar**

- Position zwischen den Sprüngen (im System, im Supercruise oder im Normalraum): das Spiel schreibt nur das StarPos des Systems und in der Nähe eines Planeten Breite, Länge und Höhe
- Positionen anderer Schiffe und Spieler: das Journal ist der Bericht des Kommandanten über sich selbst
- Geschwindigkeit, Schub und andere Flugtelemetrie: das Spiel schreibt sie nicht
- Journale und Begleitdateien früherer Sitzungen: behalten, wenn sie gespielt wurden (der Verfolger beginnt am Ende einer Datei, die älter ist als dieser Lauf des Spiels)
- die Begleit-Web-API von Frontier (cAPI): braucht die Anmeldung des Spielers bei Frontier; keine Datei, die das Spiel schreibt

**Größe**: etwa 1–5 MB Rohtext pro Stunde: das Journal 0,2–2 MB, Status.json (unter 1 KB, bis zu jede Sekunde neu geschrieben) 1–2 MB, ein Satz aus Markt/Ausrüstung/Werft 20–150 KB pro besuchter Station; zstd in heat.raw.parquet macht es etwa ein Zehntel

## Geprüft {#verified}

Parser über echte Journaldateien aus einer lokalen Installation abgespielt (Ereignisanzahl stimmt mit den Statistiken überein); Oberflächen-Positionen aus Status.json nur an synthetischen Schnappschüssen getestet

## Quelle {#source}

[heat3d_watch/adapters/elite.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/elite.py)

<!-- Generated from the adapter by tools/gen_game_pages.py; change the adapter and run it again rather than editing this page. -->
