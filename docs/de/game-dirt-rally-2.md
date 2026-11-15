---
title: "DiRT Rally 2.0 (Live-Daten)"
nav_order: 11
lang: "de"
source: game-dirt-rally-2.md
source_hash: "367131ff990b"
nav_exclude: true
search_exclude: true
---
# DiRT Rally 2.0 (Live-Daten)

Während du DiRT Rally 2.0 spielst, speichert der Watcher die Daten, die das Spiel selbst ausgibt, damit du sie dir später auf einer Karte im 3DHeat-Viewer ansehen kannst.

*Technische Details: Adapter `dirt-rally-2`, Art [`telemetry`](sources-and-rules.md); er läuft, solange `dirtrally2.exe` läuft, und sucht alle 0,1 s nach neuen Daten.*

## Was aufgezeichnet wird

- Position des eigenen Autos (Welt-XYZ, m) mit 10 Hz, dazu Geschwindigkeit, Gang, Gas, Bremse, Distanz in der Wertungsprüfung
- Start der Wertungsprüfung (wenn die Stoppuhr der Prüfung losläuft), Ziel mit der Prüfzeit, Neustarts
- Teleports (ein Zurücksetzen auf die Straße): `teleport` an der Stelle, wo das Auto war, `spawn` an der Stelle, wo es jetzt ist
- Wertungsprüfungen, Bestzeit einer Prüfung, Distanz, Höchstgeschwindigkeit

## Woher die Daten kommen

UDP 127.0.0.1:20777, extradata=3 (Documents\My Games\DiRT Rally 2.0\hardwaresettings\hardware_settings_config.xml); solange eine andere App Port 20777 belegt, überlässt der Watcher ihr den Port

## So schaltest du es ein

`python -m heat3d_watch setup dirt-rally-2 --apply` setzt &lt;udp enabled="true" extradata="3"> (vorher gesichert)

Gib den Befehl in einem Terminal ein, das im Ordner des Watchers geöffnet ist (siehe [Bevor du anfängst](before-you-start.md)). Wenn er fehlschlägt, sagt die letzte Zeile, warum; [Installation und Start](installing-and-running.md) behandelt die üblichen Ursachen.

`python -m heat3d_watch setup dirt-rally-2` listet die Dateien auf, die er ändern würde; `python -m heat3d_watch setup dirt-rally-2 --apply` ändert sie und sichert das Original als `<file>.heat3d-backup` (siehe [Befehle](commands.md#setup)). Für jede Änderung gibt er `dirt-rally-2: changed: ...` aus, oder `dirt-rally-2: nothing to change`, wenn es schon eingeschaltet ist.

## So funktioniert es

Die eigene Telemetrie der Rennspiele: Forza, die Assetto-Corsa-Spiele, die Rallye-Spiele und BeamNG, aufgezeichnet als Strecken, Runden und Etappen.

Jedes dieser Spiele veröffentlicht seine Telemetrie absichtlich, für Dashboards und Bewegungssimulatoren; nichts wird eingeschleust, und nichts, was das Spiel nicht herausgibt, wird gelesen. Die Decodierung ist nicht doppelt geschrieben: Es sind die Rundenrekorder von gamecapture in
3DHeat GameCapture `heat3d_capture/telemetry`, kopiert nach `heat3d_watch/decoders` (dort mit Paketen getestet, die aus den veröffentlichten Layouts gebaut wurden). Dieses Modul macht daraus die Zeilen des Watchers: die Position des Autos mehrmals pro Sekunde mit Geschwindigkeit, Gang und Pedalen, ein Ereignis pro Runde oder Etappe und die Zahlen, die ein Fahrer behält: Runden, Bestrunde, Distanz, Höchstgeschwindigkeit.

#### Forza (Horizon 4/5/6, Motorsport)

"Data Out" per UDP, eingeschaltet in den HUD- und Gameplay-Einstellungen des Spiels, an 127.0.0.1 Port 5300, Format Dash. Ein Paket pro Simulationstick; der Offset des Dash-Blocks wird aus den Paketen ermittelt (`forza.detect_layout`). Welt-Meter, Y nach oben; die Welt ist linkshändig und wird so gezeichnet, wie sie gesendet wird, wie es der Rundenrekorder tut (Dokumentation "Data Out" von Forza Motorsport und Forza Horizon).
Das Spiel sendet an einen einzigen Port, und FH Companion und andere Data-Out-Apps hören auf denselben. Zwei Programme können ihn nicht gemeinsam nutzen: Unter Windows bekommt der an 127.0.0.1 gebundene Socket die Pakete, und ein an alle Adressen auf demselben Port gebundener bekommt keine, egal wer zuerst war. Deshalb wartet der Watcher nach dem Start des Spiels kurz, bevor er den Port belegt, nimmt ihn nie einer App weg, die ihn hält, und gibt ihn sofort frei, sobald eine andere App dort zu hören beginnt. Solange er den Port hält, leitet er jedes Paket unverändert an 127.0.0.1:5301 weiter – stelle das Port-Feld von FH Companion (Reiter Telemetrie) auf 5301, dann zeichnen beide auf.

#### Alles behalten

Die Zeilen kommen einige pro Sekunde; die Spiele senden weit mehr. Jedes UDP-Paket, das ankommt – in den Menüs, zwischen Runden, auch solche, die kein Decoder liest – wird vollständig in der `heat.raw.parquet` der Sitzung behalten, unter seinem Format (`dash-horizon`, `session_update`, `extradata3`, `H3D1`, ...). Jede Seite des gemeinsamen Speichers (die ganze Zuordnung, nicht nur die decodierten Bytes) wird bei jeder Änderung unter dem Namen ihrer Zuordnung behalten (`acpmf_physics`, ...). `used` markiert, was auch zu Zeilen wurde; `selfCheck.completeness` in der `meta.json` zählt jede Art (Regel des 3DHeat-Konverters).

Dasselbe Modul bedient auch: [Assetto Corsa (Live-Daten)](game-assetto-corsa.md), [Assetto Corsa Competizione (Live-Daten)](game-assetto-corsa-competizione.md), [Assetto Corsa EVO (Live-Daten)](game-assetto-corsa-evo.md), [Assetto Corsa Rally (Live-Daten)](game-assetto-corsa-rally.md), [BeamNG.drive (Live-Daten)](game-beamng.md), [EA SPORTS WRC (Live-Daten)](game-ea-wrc.md), [Forza Horizon 4 (Live-Daten)](game-forza-horizon-4.md), [Forza Horizon 5 (Live-Daten)](game-forza-horizon-5.md), [Forza Horizon 6 (Live-Daten)](game-forza-horizon-6.md), [Forza Motorsport (Live-Daten)](game-forza-motorsport.md), [Richard Burns Rally (Live-Daten)](game-richard-burns-rally.md).

## Positionen und Achsen

| | |
|---|---|
| Positionen werden aufgezeichnet | ja |
| Hochachse | `y` |
| Einheiten | Meter |
| Für den Viewer gespiegelt | nein |
| Einheitenskala (`scale`: der Viewer multipliziert die Positionen damit) | 1 |

Diese Angaben gehen in die `meta.json` (`axes`) jeder Sitzung und, wenn die Sitzung Positionen hat, in die Fußzeile der `heat.parquet`, damit der 3DHeat-Viewer die Zeilen selbst dreht und skaliert – siehe [Die Daten](the-data.md).

## Mehrspieler

- Als online gespielt markiert (`multiplayer`): **ja**. `games --markdown` zeigt dies als "allowed (reads only what the game publishes)".
- Art `telemetry`: Es liest nur, was das Spiel oder die Plattform herausgibt (ein UDP-Port oder gemeinsamer Speicher, den das Spiel veröffentlicht), daher zeichnet es auch im Online-Spiel auf wie offline; die Markierung entscheidet nur, ob jemals Speicher gelesen werden darf.
- Speicher: Dieser Adapter liest **niemals** Speicher. Nur `memory`-Adapter lesen Speicher, und nie bei einem Spiel, das als online gespielt markiert ist – siehe [Quellen und Regeln](sources-and-rules.md).

## Aufgezeichnete Statistiken

Statistikschlüssel, die der Code dieses Adapters namentlich setzt (jeweils die `stats` der Sitzung in `meta.json` und die Tabelle `stats` von `watcher.sqlite`):

`best_lap`, `best_stage`, `distance_km`, `laps`, `stages`, `top_speed_kmh`

Ein Schlüssel in geschweiften Klammern wird zur Laufzeit vervollständigt (`score.{team}` ist ein Schlüssel pro Team). Schlüssel, die der Code aus einer Tabelle der Felder des Spiels oder aus den eigenen Statistiknamen des Spiels übernimmt, stehen nicht in dieser Liste; "Was aufgezeichnet wird" oben nennt sie.

## Vollständigkeit

Der Watcher folgt der [Konverterregel](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md) von 3DHeat: Was die Quelle enthält, wird gelesen oder behalten, nie verworfen. Neben den Zeilen wird jedes Paket, jede Seite, jede Zeile oder jede Antwort, die der Adapter empfängt, vollständig in der `heat.raw.parquet` der Sitzung behalten (Spalten `time`, `ms`, `type`, `used`, `payload`, `text`, dann jedes nach Name behaltene Feld; `used` markiert, was auch zu Zeilen wurde), und `selfCheck.completeness` in der `meta.json` zählt jeden `type` – `lost` ist 0.

**Gelesen**

- Zeilen mit 10 Hz: Position, Geschwindigkeit, Gang, Gas, Bremse, Distanz in der Prüfung, Gieren, Drehzahl, Lenkung; Start der Prüfung, Ziel mit der Prüfzeit, Neustarts

**Roh behalten**

- jedes Paket, das den Port erreicht, vollständig, in der Rate des Spiels, unter seinem Format: `extradata3` (66 Floats, 264 Bytes), `extradata3-64` (das 64er von DiRT Rally), sonst `<n>-byte`
- im Paket über die Zeilen hinaus: alle 66 Floats – Geschwindigkeit in Weltkoordinaten, Seiten- und Vorwärtsvektoren, Federungsposition und Geschwindigkeit pro Rad, Geschwindigkeit der Aufstandsfläche und Bremstemperatur, g-Kräfte, Runden, Länge der Prüfung; die Floats ohne feststehenden Namen stehen in den Rundendateien als `float<i>`

**Nicht verfügbar**

- andere Autos: das Spiel sendet nur das Auto des Spielers
- ein Handbremskanal: das Paket hat keinen

**Größe**: etwa 70 MB pro Stunde bei 60 Paketen pro Sekunde (264 Bytes plus ein 70-Byte-Kopf pro Eintrag); zstd behält einen Bruchteil

## Geprüft

Decodierung ist die des Rundenrekorders von gamecapture (an Paketen getestet, die aus den dokumentierten Layouts gebaut wurden); der Adapter wurde mit Paketen getestet, die im Test gebaut und über UDP gesendet wurden; nicht gegen das Spiel selbst getestet

## Quelle

[heat3d_watch/adapters/racing.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/racing.py)

<!-- Generated from the adapter by tools/gen_game_pages.py; change the adapter and run it again rather than editing this page. -->
