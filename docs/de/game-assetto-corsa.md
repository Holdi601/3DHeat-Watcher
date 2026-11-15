---
title: "Assetto Corsa (Live-Daten)"
nav_order: 2
lang: de
source: game-assetto-corsa.md
source_hash: "9132272cc104"
nav_exclude: true
search_exclude: true
---
# Assetto Corsa (Live-Daten) {#assetto-corsa-live-data}

Während du Assetto Corsa spielst, speichert der Watcher die Daten, die das Spiel selbst ausgibt, damit du sie dir später auf einer Karte im 3DHeat-Viewer ansehen kannst.

*Technische Details: Adapter `assetto-corsa`, Art [`telemetry`](sources-and-rules.md); er läuft, solange `acs.exe` oder `acs_x86.exe` läuft, und sucht alle 0,1 s nach neuen Daten.*

## Was aufgezeichnet wird {#what-is-recorded}

- Position des eigenen Autos (Welt-XYZ, m: Mittelwert der Reifen-Aufstandspunkte) mit 10 Hz, dazu Geschwindigkeit, Gang, Gas, Bremse
- Sitzungsstart und -ende mit der Strecke und dem Auto, die das Spiel nennt
- Runden nach dem Rundenzähler des Spiels, mit seiner Rundenzeit
- Teleports (zurück an die Box, ein Neustart): `teleport` an der Stelle, wo das Auto war, `spawn` an der Stelle, wo es jetzt ist
- Runden, Bestrunde, Distanz, Höchstgeschwindigkeit

## Woher die Daten kommen {#where-it-comes-from}

Gemeinsamer Speicher Local\acpmf_physics, Local\acpmf_graphics, Local\acpmf_static

## So schaltest du es ein {#how-to-switch-it-on}

Du musst nichts einschalten: Der Watcher liest die Quelle so, wie das Spiel oder die Plattform sie bereitstellt.

## So funktioniert es {#how-it-works}

Die eigene Telemetrie der Rennspiele: Forza, die Assetto-Corsa-Spiele, die Rallye-Spiele und BeamNG, aufgezeichnet als Strecken, Runden und Etappen.

Jedes dieser Spiele veröffentlicht seine Telemetrie absichtlich, für Dashboards und Bewegungssimulatoren; nichts wird eingeschleust, und nichts, was das Spiel nicht herausgibt, wird gelesen. Die Decodierung ist nicht doppelt geschrieben: Es sind die Rundenrekorder von gamecapture in
3DHeat GameCapture `heat3d_capture/telemetry`, kopiert nach `heat3d_watch/decoders` (dort mit Paketen getestet, die aus den veröffentlichten Layouts gebaut wurden). Dieses Modul macht daraus die Zeilen des Watchers: die Position des Autos mehrmals pro Sekunde mit Geschwindigkeit, Gang und Pedalen, ein Ereignis pro Runde oder Etappe und die Zahlen, die ein Fahrer behält: Runden, Bestrunde, Distanz, Höchstgeschwindigkeit.

#### Forza (Horizon 4/5/6, Motorsport) {#forza-horizon-456-motorsport}

"Data Out" per UDP, eingeschaltet in den HUD- und Gameplay-Einstellungen des Spiels, an 127.0.0.1 Port 5300, Format Dash. Ein Paket pro Simulationstick; der Offset des Dash-Blocks wird aus den Paketen ermittelt (`forza.detect_layout`). Welt-Meter, Y nach oben; die Welt ist linkshändig und wird so gezeichnet, wie sie gesendet wird, wie es der Rundenrekorder tut (Dokumentation "Data Out" von Forza Motorsport und Forza Horizon).
Das Spiel sendet an einen einzigen Port, und FH Companion und andere Data-Out-Apps hören auf denselben. Zwei Programme können ihn nicht gemeinsam nutzen: Unter Windows bekommt der an 127.0.0.1 gebundene Socket die Pakete, und ein an alle Adressen auf demselben Port gebundener bekommt keine, egal wer zuerst war. Deshalb wartet der Watcher nach dem Start des Spiels kurz, bevor er den Port belegt, nimmt ihn nie einer App weg, die ihn hält, und gibt ihn sofort frei, sobald eine andere App dort zu hören beginnt. Solange er den Port hält, leitet er jedes Paket unverändert an 127.0.0.1:5301 weiter – stelle das Port-Feld von FH Companion (Reiter Telemetrie) auf 5301, dann zeichnen beide auf.

#### Assetto Corsa, ACC, AC EVO, AC Rally {#assetto-corsa-acc-ac-evo-ac-rally}

Gemeinsamer Speicher, den das Spiel für Apps schreibt: `Local\acpmf_physics`, `Local\acpmf_graphics`, `Local\acpmf_static` (AC EVO: `Local\acevo_pmf_*`). Er wird nur lesend geöffnet und erst, wenn das Spiel ihn angelegt hat (`simracing_shm`). Die Position ist der Mittelwert der vier Reifen-Aufstandspunkte, Welt-Meter, Y nach oben. Runden nach dem Zähler des Spiels (AC, ACC) oder durch erneutes Passieren des Startpunkts (AC EVO, AC Rally), so wie `kunos.py` es für den Rundenrekorder macht.

#### Alles behalten {#everything-kept}

Die Zeilen kommen einige pro Sekunde; die Spiele senden weit mehr. Jedes UDP-Paket, das ankommt – in den Menüs, zwischen Runden, auch solche, die kein Decoder liest – wird vollständig in der `heat.raw.parquet` der Sitzung behalten, unter seinem Format (`dash-horizon`, `session_update`, `extradata3`, `H3D1`, ...). Jede Seite des gemeinsamen Speichers (die ganze Zuordnung, nicht nur die decodierten Bytes) wird bei jeder Änderung unter dem Namen ihrer Zuordnung behalten (`acpmf_physics`, ...). `used` markiert, was auch zu Zeilen wurde; `selfCheck.completeness` in der `meta.json` zählt jede Art (Regel des 3DHeat-Konverters).

Dasselbe Modul bedient auch: [Assetto Corsa Competizione (Live-Daten)](game-assetto-corsa-competizione.md), [Assetto Corsa EVO (Live-Daten)](game-assetto-corsa-evo.md), [Assetto Corsa Rally (Live-Daten)](game-assetto-corsa-rally.md), [BeamNG.drive (Live-Daten)](game-beamng.md), [DiRT Rally 2.0 (Live-Daten)](game-dirt-rally-2.md), [EA SPORTS WRC (Live-Daten)](game-ea-wrc.md), [Forza Horizon 4 (Live-Daten)](game-forza-horizon-4.md), [Forza Horizon 5 (Live-Daten)](game-forza-horizon-5.md), [Forza Horizon 6 (Live-Daten)](game-forza-horizon-6.md), [Forza Motorsport (Live-Daten)](game-forza-motorsport.md), [Richard Burns Rally (Live-Daten)](game-richard-burns-rally.md).

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

`best_lap`, `best_stage`, `distance_km`, `laps`, `race_position`, `stages`, `top_speed_kmh`

Ein Schlüssel in geschweiften Klammern wird zur Laufzeit vervollständigt (`score.{team}` ist ein Schlüssel pro Team). Schlüssel, die der Code aus einer Tabelle der Felder des Spiels oder aus den eigenen Statistiknamen des Spiels übernimmt, stehen nicht in dieser Liste; "Was aufgezeichnet wird" oben nennt sie.

## Vollständigkeit {#completeness}

Der Watcher folgt der [Konverterregel](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md) von 3DHeat: Was die Quelle enthält, wird gelesen oder behalten, nie verworfen. Neben den Zeilen wird jedes Paket, jede Seite, jede Zeile oder jede Antwort, die der Adapter empfängt, vollständig in der `heat.raw.parquet` der Sitzung behalten (Spalten `time`, `ms`, `type`, `used`, `payload`, `text`, dann jedes nach Name behaltene Feld; `used` markiert, was auch zu Zeilen wurde), und `selfCheck.completeness` in der `meta.json` zählt jeden `type` – `lost` ist 0.

**Gelesen**

- Zeilen mit 10 Hz aus der Physikseite: Position (Mittelwert der Reifen-Aufstandspunkte), Geschwindigkeit, Gang, Gas, Bremse, Gieren/Nicken/Rollen (rad), Drehzahl, Lenkung (so wie die Seite sie hat); Sitzungsstart mit Strecke und Auto aus der statischen Seite; Runden, Platzierung im Rennen

**Roh behalten**

- jede Seite vollständig – die ganze Zuordnungsregion, nicht nur die decodierten Bytes – jedes Mal, wenn sich ihre Bytes ändern, beim Lesetakt des Watchers von 10 Hz: `acpmf_physics`, `acpmf_graphics`, `acpmf_static`; ein erneutes Lesen, das Byte für Byte dem letzten entspricht, wird in `unchanged_reads` der meta.json gezählt und nicht noch einmal gespeichert
- alles, was nur für Rundendateien decodiert wird (`decoders/kunos.py`: Schlupf, Last, Druck, Temperaturen, Sturz, Federung, Aufstandspunkte, Bremstemperaturen, Schlupfverhältnis und -winkel pro Rad; Geschwindigkeit und Winkelgeschwindigkeit in Welt- und Fahrzeugkoordinaten, Hilfen) steht in diesen Seiten

**Nicht verfügbar**

- Positionen anderer Autos: die Seiten beschreiben nur das Auto des Spielers (die Grafikseite von ACC hat in einigen Versionen Auto-IDs und Koordinaten für andere – im Roh-Speicher behalten, nicht decodiert)
- Physik-Ticks zwischen den Lesevorgängen des Watchers: das Spiel schreibt die Seite in seiner Physikrate neu (bis zu 333 Hz), und der Watcher liest 10-mal pro Sekunde

**Größe**: etwa 150–300 MB pro Stunde vor der Komprimierung (eine 4-KB-Region pro Seite bei bis zu 10 Änderungen pro Sekunde); die Seiten bestehen meist aus Nullen, und zstd behält nur einen kleinen Bruchteil

## Geprüft {#verified}

Decodierung ist die des Rundenrekorders von gamecapture (an synthetischen Seiten getestet); der Adapter wurde mit gemeinsamem Speicher getestet, der im Test aus dem dokumentierten Layout gebaut wurde; nicht gegen das Spiel selbst getestet

## Quelle {#source}

[heat3d_watch/adapters/racing.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/racing.py)

<!-- Generated from the adapter by tools/gen_game_pages.py; change the adapter and run it again rather than editing this page. -->
