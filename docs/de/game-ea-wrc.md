---
title: "EA SPORTS WRC (Live-Daten)"
nav_order: 17
lang: "de"
source: game-ea-wrc.md
source_hash: "c97300f65c43"
nav_exclude: true
search_exclude: true
---
# EA SPORTS WRC (Live-Daten) {#ea-sports-wrc-live-data}

Während du EA SPORTS WRC spielst, speichert der Watcher die Daten, die das Spiel selbst ausgibt, damit du sie dir später auf einer Karte im 3DHeat-Viewer ansehen kannst.

*Technische Details: Adapter `ea-wrc`, Art [`telemetry`](sources-and-rules.md); er läuft, solange `WRC.exe` läuft, und sucht alle 0,1 s nach neuen Daten.*

## Was aufgezeichnet wird {#what-is-recorded}

- Position des eigenen Autos (Welt-XYZ, m) mit 10 Hz, dazu Geschwindigkeit, Gang, Gas, Bremse, Distanz in der Wertungsprüfung
- Start der Wertungsprüfung (wenn die Stoppuhr der Prüfung losläuft), Ziel mit der Prüfzeit, Neustarts
- Teleports (ein Zurücksetzen auf die Straße): `teleport` an der Stelle, wo das Auto war, `spawn` an der Stelle, wo es jetzt ist
- Wertungsprüfungen, Bestzeit einer Prüfung, Distanz, Höchstgeschwindigkeit

## Woher die Daten kommen {#where-it-comes-from}

UDP 127.0.0.1:20777, das Standard-Paket `session_update` der Struktur `wrc` (Documents\My Games\WRC\telemetry\config.json); solange eine andere App Port 20777 belegt, überlässt der Watcher ihr den Port

## So schaltest du es ein {#how-to-switch-it-on}

`python -m heat3d_watch setup ea-wrc --apply` schaltet das Paket `session_update` in config.json ein (vorher gesichert)

Gib den Befehl in einem Terminal ein, das im Ordner des Watchers geöffnet ist (siehe [Bevor du anfängst](before-you-start.md)). Wenn er fehlschlägt, sagt die letzte Zeile, warum; [Installation und Start](installing-and-running.md) behandelt die üblichen Ursachen.

`python -m heat3d_watch setup ea-wrc` listet die Dateien auf, die er ändern würde; `python -m heat3d_watch setup ea-wrc --apply` ändert sie und sichert das Original als `<file>.heat3d-backup` (siehe [Befehle](commands.md#setup)). Für jede Änderung gibt er `ea-wrc: changed: ...` aus, oder `ea-wrc: nothing to change`, wenn es schon eingeschaltet ist.

## So funktioniert es {#how-it-works}

Die eigene Telemetrie der Rennspiele: Forza, die Assetto-Corsa-Spiele, die Rallye-Spiele und BeamNG, aufgezeichnet als Strecken, Runden und Etappen.

Jedes dieser Spiele veröffentlicht seine Telemetrie absichtlich, für Dashboards und Bewegungssimulatoren; nichts wird eingeschleust, und nichts, was das Spiel nicht herausgibt, wird gelesen. Die Decodierung ist nicht doppelt geschrieben: Es sind die Rundenrekorder von gamecapture in
3DHeat GameCapture `heat3d_capture/telemetry`, kopiert nach `heat3d_watch/decoders` (dort mit Paketen getestet, die aus den veröffentlichten Layouts gebaut wurden). Dieses Modul macht daraus die Zeilen des Watchers: die Position des Autos mehrmals pro Sekunde mit Geschwindigkeit, Gang und Pedalen, ein Ereignis pro Runde oder Etappe und die Zahlen, die ein Fahrer behält: Runden, Bestrunde, Distanz, Höchstgeschwindigkeit.

#### Forza (Horizon 4/5/6, Motorsport) {#forza-horizon-456-motorsport}

"Data Out" per UDP, eingeschaltet in den HUD- und Gameplay-Einstellungen des Spiels, an 127.0.0.1 Port 5300, Format Dash. Ein Paket pro Simulationstick; der Offset des Dash-Blocks wird aus den Paketen ermittelt (`forza.detect_layout`). Welt-Meter, Y nach oben; die Welt ist linkshändig und wird so gezeichnet, wie sie gesendet wird, wie es der Rundenrekorder tut (Dokumentation "Data Out" von Forza Motorsport und Forza Horizon).
Das Spiel sendet an einen einzigen Port, und FH Companion und andere Data-Out-Apps hören auf denselben. Zwei Programme können ihn nicht gemeinsam nutzen: Unter Windows bekommt der an 127.0.0.1 gebundene Socket die Pakete, und ein an alle Adressen auf demselben Port gebundener bekommt keine, egal wer zuerst war. Deshalb wartet der Watcher nach dem Start des Spiels kurz, bevor er den Port belegt, nimmt ihn nie einer App weg, die ihn hält, und gibt ihn sofort frei, sobald eine andere App dort zu hören beginnt. Solange er den Port hält, leitet er jedes Paket unverändert an 127.0.0.1:5301 weiter – stelle das Port-Feld von FH Companion (Reiter Telemetrie) auf 5301, dann zeichnen beide auf.

#### EA SPORTS WRC, DiRT Rally 2.0, Richard Burns Rally {#ea-sports-wrc-dirt-rally-20-richard-burns-rally}

UDP: die Datei `Documents/My Games/WRC/telemetry/config.json` von WRC (das Paket `session_update` der Struktur `wrc`), die Datei `hardware_settings_config.xml` von DiRT (`<udp enabled="true" extradata="3" port="20777">`), das NGP-Plugin von RBR (`udpTelemetry=1`, Port 6776). Etappen nach der Stoppuhr der Etappe des Spiels (`rally.StageSplitter`). RBR dokumentiert seine Achsen nicht: Die Hochachse ist diejenige, entlang der sich die Etappe am wenigsten verändert; sie wird beim Schließen der Sitzung festgelegt.

#### Alles behalten {#everything-kept}

Die Zeilen kommen einige pro Sekunde; die Spiele senden weit mehr. Jedes UDP-Paket, das ankommt – in den Menüs, zwischen Runden, auch solche, die kein Decoder liest – wird vollständig in der `heat.raw.parquet` der Sitzung behalten, unter seinem Format (`dash-horizon`, `session_update`, `extradata3`, `H3D1`, ...). Jede Seite des gemeinsamen Speichers (die ganze Zuordnung, nicht nur die decodierten Bytes) wird bei jeder Änderung unter dem Namen ihrer Zuordnung behalten (`acpmf_physics`, ...). `used` markiert, was auch zu Zeilen wurde; `selfCheck.completeness` in der `meta.json` zählt jede Art (Regel des 3DHeat-Konverters).

Dasselbe Modul bedient auch: [Assetto Corsa (Live-Daten)](game-assetto-corsa.md), [Assetto Corsa Competizione (Live-Daten)](game-assetto-corsa-competizione.md), [Assetto Corsa EVO (Live-Daten)](game-assetto-corsa-evo.md), [Assetto Corsa Rally (Live-Daten)](game-assetto-corsa-rally.md), [BeamNG.drive (Live-Daten)](game-beamng.md), [DiRT Rally 2.0 (Live-Daten)](game-dirt-rally-2.md), [Forza Horizon 4 (Live-Daten)](game-forza-horizon-4.md), [Forza Horizon 5 (Live-Daten)](game-forza-horizon-5.md), [Forza Horizon 6 (Live-Daten)](game-forza-horizon-6.md), [Forza Motorsport (Live-Daten)](game-forza-motorsport.md), [Richard Burns Rally (Live-Daten)](game-richard-burns-rally.md).

## Positionen und Achsen {#positions-and-axes}

| | |
|---|---|
| Positionen werden aufgezeichnet | ja |
| Hochachse | `y` |
| Einheiten | Meter |
| Für den Viewer gespiegelt | nein |
| Einheitenskala (`scale`: der Viewer multipliziert die Positionen damit) | 1 |

Diese Angaben gehen in die `meta.json` (`axes`) jeder Sitzung und, wenn die Sitzung Positionen hat, in die Fußzeile der `heat.parquet`, damit der 3DHeat-Viewer die Zeilen selbst dreht und skaliert – siehe [Die Daten](the-data.md).

## Mehrspieler {#multiplayer}

- Als online gespielt markiert (`multiplayer`): **ja**. `games --markdown` zeigt dies als "allowed (reads only what the game publishes)".
- Art `telemetry`: Es liest nur, was das Spiel oder die Plattform herausgibt (ein UDP-Port oder gemeinsamer Speicher, den das Spiel veröffentlicht), daher zeichnet es auch im Online-Spiel auf wie offline; die Markierung entscheidet nur, ob jemals Speicher gelesen werden darf.
- Speicher: Dieser Adapter liest **niemals** Speicher. Nur `memory`-Adapter lesen Speicher, und nie bei einem Spiel, das als online gespielt markiert ist – siehe [Quellen und Regeln](sources-and-rules.md).

## Aufgezeichnete Statistiken {#statistics-recorded}

Statistikschlüssel, die der Code dieses Adapters namentlich setzt (jeweils die `stats` der Sitzung in `meta.json` und die Tabelle `stats` von `watcher.sqlite`):

`best_lap`, `best_stage`, `distance_km`, `laps`, `stages`, `top_speed_kmh`

Ein Schlüssel in geschweiften Klammern wird zur Laufzeit vervollständigt (`score.{team}` ist ein Schlüssel pro Team). Schlüssel, die der Code aus einer Tabelle der Felder des Spiels oder aus den eigenen Statistiknamen des Spiels übernimmt, stehen nicht in dieser Liste; "Was aufgezeichnet wird" oben nennt sie.

## Vollständigkeit {#completeness}

Der Watcher folgt der [Konverterregel](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md) von 3DHeat: Was die Quelle enthält, wird gelesen oder behalten, nie verworfen. Neben den Zeilen wird jedes Paket, jede Seite, jede Zeile oder jede Antwort, die der Adapter empfängt, vollständig in der `heat.raw.parquet` der Sitzung behalten (Spalten `time`, `ms`, `type`, `used`, `payload`, `text`, dann jedes nach Name behaltene Feld; `used` markiert, was auch zu Zeilen wurde), und `selfCheck.completeness` in der `meta.json` zählt jeden `type` – `lost` ist 0.

**Gelesen**

- Zeilen mit 10 Hz: Position, Geschwindigkeit, Gang, Gas, Bremse, Distanz in der Prüfung, Gieren, Drehzahl, Lenkung; Start der Prüfung, Ziel mit der Prüfzeit, Neustarts

**Roh behalten**

- jedes Paket, das den Port erreicht, vollständig, in der Rate des Spiels, unter seinem Format: `session_update` (die Standardstruktur `wrc`, 237 Bytes), `wrc <n>-byte` für jedes andere Paket, das die Konfiguration sendet
- im Paket über die Zeilen hinaus: Weltgeschwindigkeit und -beschleunigung, die Achsen des Autos, Position und Geschwindigkeit der Radnabe pro Rad, Geschwindigkeit der Aufstandsfläche, Bremstemperatur, Kupplung, Handbremse, die Spielzeit; 22 Bytes (Offsets 16–36 und 40), die keine veröffentlichte Kanalliste benennt

**Nicht verfügbar**

- andere Autos: das Spiel sendet nur das Auto des Spielers
- die übrigen Strukturen und Pakete, die die Telemetrie-Konfiguration festlegen kann (session_start, session_end, pause): `setup` schaltet nur `session_update` ein; jedes andere Paket, das an den Port gesendet wird, wird behalten

**Größe**: etwa 65 MB pro Stunde bei 60 Paketen pro Sekunde (237 Bytes plus ein 70-Byte-Kopf pro Eintrag; die Rate -1 der Konfiguration sendet eines pro Bild, also mehr bei höherer Bildrate); zstd behält einen Bruchteil

## Geprüft {#verified}

Decodierung ist die des Rundenrekorders von gamecapture (an Paketen getestet, die aus den dokumentierten Layouts gebaut wurden); der Adapter wurde mit Paketen getestet, die im Test gebaut und über UDP gesendet wurden; nicht gegen das Spiel selbst getestet

## Quelle {#source}

[heat3d_watch/adapters/racing.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/racing.py)

<!-- Generated from the adapter by tools/gen_game_pages.py; change the adapter and run it again rather than editing this page. -->
