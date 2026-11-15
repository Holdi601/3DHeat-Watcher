---
title: "Assetto Corsa EVO (Live-Daten)"
nav_order: 4
lang: "de"
source: game-assetto-corsa-evo.md
source_hash: "b14d46c10e85"
nav_exclude: true
search_exclude: true
---
# Assetto Corsa EVO (Live-Daten) {#assetto-corsa-evo-live-data}

Während du Assetto Corsa EVO spielst, speichert der Watcher die Daten, die das Spiel selbst herausgibt. So kannst du sie später auf einer Karte im 3DHeat-Viewer ansehen.

*Technische Details: Adapter `assetto-corsa-evo`, Art [`telemetry`](sources-and-rules.md); er läuft, solange `AssettoCorsaEVO.exe` läuft, und sucht alle 0,1 s nach neuen Daten.*

## Was aufgezeichnet wird {#what-is-recorded}

- Position deines eigenen Autos (Welt-XYZ, m: Mittelwert der Reifen-Aufstandspunkte) mit 10 Hz, zusammen mit Geschwindigkeit, Gang, Gas und Bremse
- Start und Ende der Session mit der Strecke und dem Auto, die das Spiel nennt
- Runden, wenn das Auto dort vorbeifährt, wo die Fahrt begann, in dieselbe Richtung
- Teleports (zurück an die Box, ein Neustart): `teleport` dort, wo das Auto war, `spawn` dort, wo es jetzt ist
- Runden, Bestrunde, Distanz, Höchstgeschwindigkeit

## Woher die Daten kommen {#where-it-comes-from}

gemeinsamer Speicher Local\acevo_pmf_physics, Local\acevo_pmf_static

## So schaltest du es ein {#how-to-switch-it-on}

Du musst nichts einschalten: Der Watcher liest die Quelle so, wie das Spiel oder die Plattform sie bereitstellt.

## So funktioniert es {#how-it-works}

Die eigene Telemetrie der Rennspiele: Forza, die Assetto-Corsa-Spiele, die Rally-Spiele und BeamNG, aufgezeichnet als Strecken, Runden und Etappen.

Jedes Spiel hier veröffentlicht seine Telemetrie absichtlich, für Dashboards und Bewegungssimulatoren. Nichts wird eingeschleust, und es wird nichts gelesen, was das Spiel nicht selbst herausgibt. Die Dekodierung wird nicht doppelt geschrieben: Sie stammt aus den Rundenaufzeichnern von gamecapture in `heat3d_capture/telemetry` von 3DHeat GameCapture, kopiert nach `heat3d_watch/decoders` (dort getestet mit Paketen, die aus den veröffentlichten Layouts gebaut wurden). Dieses Modul macht daraus die Zeilen des Watchers: die Position des Autos mehrmals pro Sekunde mit Geschwindigkeit, Gang und Pedalen, ein Ereignis pro Runde oder Etappe und die Zahlen, die ein Fahrer sich merkt: Runden, Bestrunde, Distanz, Höchstgeschwindigkeit.

#### Forza (Horizon 4/5/6, Motorsport) {#forza-horizon-456-motorsport}

„Data Out“-UDP, eingeschaltet im HUD und in den Spieleinstellungen des Spiels, an 127.0.0.1 Port 5300, Format Dash. Ein Paket pro Simulationstick; der Offset des Dash-Blocks wird aus den Paketen ermittelt (`forza.detect_layout`). Welt in Metern, Y nach oben; die Welt ist linkshändig und wird so gezeichnet, wie sie gesendet wird, wie es auch der Rundenaufzeichner tut (die „Data Out“-Dokumentation von Forza Motorsport und Forza Horizon). Das Spiel sendet an einen Port, und FH Companion und andere Data-Out-Apps hören auf denselben. Zwei Programme können ihn nicht gemeinsam nutzen: Unter Windows bekommt der an 127.0.0.1 gebundene Socket die Pakete, und ein Socket, der an alle Adressen auf demselben Port gebunden ist, bekommt keine, egal wer zuerst da war. Deshalb wartet der Watcher kurz, nachdem das Spiel gestartet ist, bevor er den Port belegt, nimmt ihn nie einer App weg, die ihn schon hält, und gibt ihn sofort frei, wenn eine andere App auf ihm zu lauschen beginnt. Solange der Watcher den Port hält, leitet er jedes Paket unverändert an 127.0.0.1:5301 weiter. Stell das Port-Feld von FH Companion (dessen Telemetrie-Reiter) auf 5301, dann zeichnen beide auf.

#### Alles wird gespeichert {#everything-kept}

Die Zeilen kommen einige pro Sekunde; die Spiele senden weit mehr. Jedes UDP-Paket, das ankommt – in den Menüs, zwischen den Runden, auch solche, die kein Dekodierer liest –, wird vollständig in der `heat.raw.parquet` der Session gespeichert, unter seinem Format (`dash-horizon`, `session_update`, `extradata3`, `H3D1`, ...). Jede Seite des gemeinsamen Speichers (der ganze Bereich, nicht nur die dekodierten Bytes) wird bei jeder Änderung unter dem Namen ihres Bereichs gespeichert (`acpmf_physics`, ...). `used` markiert, was auch zu Zeilen wurde; `selfCheck.completeness` in `meta.json` zählt jede Art (die Konverterregel von 3DHeat).

Dasselbe Modul bedient auch: [Assetto Corsa (Live-Daten)](game-assetto-corsa.md), [Assetto Corsa Competizione (Live-Daten)](game-assetto-corsa-competizione.md), [Assetto Corsa Rally (Live-Daten)](game-assetto-corsa-rally.md), [BeamNG.drive (Live-Daten)](game-beamng.md), [DiRT Rally 2.0 (Live-Daten)](game-dirt-rally-2.md), [EA SPORTS WRC (Live-Daten)](game-ea-wrc.md), [Forza Horizon 4 (Live-Daten)](game-forza-horizon-4.md), [Forza Horizon 5 (Live-Daten)](game-forza-horizon-5.md), [Forza Horizon 6 (Live-Daten)](game-forza-horizon-6.md), [Forza Motorsport (Live-Daten)](game-forza-motorsport.md), [Richard Burns Rally (Live-Daten)](game-richard-burns-rally.md).

## Positionen und Achsen {#positions-and-axes}

| | |
|---|---|
| Positionen aufgezeichnet | ja |
| Oben-Achse | `y` |
| Einheiten | Meter |
| Für den Viewer gespiegelt | keine |
| Einheitenskala (`scale`: der Viewer multipliziert die Positionen damit) | 1 |

Diese Werte landen in der `meta.json` jeder Session (`axes`) und, wenn die Session Positionen hat, im Footer der `heat.parquet`. So dreht und skaliert der 3DHeat-Viewer die Zeilen selbst – siehe [Die Daten](the-data.md).

## Mehrspieler {#multiplayer}

- Als online gespielt markiert (`multiplayer`): **ja**. `games --markdown` zeigt das als „allowed (reads only what the game publishes)“.
- Art `telemetry`: Es liest nur, was das Spiel oder die Plattform herausgibt (ein UDP-Port oder gemeinsamer Speicher, den das Spiel veröffentlicht). Deshalb zeichnet es auch im Online-Spiel auf, nicht nur offline. Die Markierung entscheidet nur, ob Speicher überhaupt gelesen werden darf.
- Speicher: Dieser Adapter liest **nie** den Speicher. Nur `memory`-Adapter lesen Speicher, und nie bei einem Spiel, das als online gespielt markiert ist – siehe [Quellen und Regeln](sources-and-rules.md).

## Aufgezeichnete Statistiken {#statistics-recorded}

Statistik-Schlüssel, die der Code dieses Adapters beim Namen setzt (das `stats` jeder Session in `meta.json` und die Tabelle `stats` in `watcher.sqlite`):

`best_lap`, `best_stage`, `distance_km`, `laps`, `race_position`, `stages`, `top_speed_kmh`

Ein Schlüssel in geschweiften Klammern wird zur Laufzeit vervollständigt (`score.{team}` ist ein Schlüssel pro Team). Schlüssel, die der Code aus einer Tabelle der Spielfelder oder aus den eigenen Statistiknamen des Spiels übernimmt, stehen nicht in dieser Liste; „Was aufgezeichnet wird“ oben nennt sie.

## Vollständigkeit {#completeness}

Der Watcher folgt der [Konverterregel](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md) von 3DHeat: Was die Quelle enthält, wird gelesen oder gespeichert, nie weggelassen. Außer den Zeilen wird jedes Paket, jede Seite, jede Zeile und jede Antwort, die der Adapter bekommt, vollständig in der `heat.raw.parquet` der Session gespeichert (Spalten `time`, `ms`, `type`, `used`, `payload`, `text` und alle Felder, die nach Namen behalten werden; `used` markiert, was auch zu Zeilen wurde). `selfCheck.completeness` in `meta.json` zählt jeden `type`; `lost` ist 0.

**Gelesen**

- Zeilen mit 10 Hz aus der Physikseite: Position (Mittelwert der Reifen-Aufstandspunkte), Geschwindigkeit, Gang, Gas, Bremse, Gieren/Nicken/Rollen (rad), Drehzahl, Lenkung (so wie die Seite sie hat); Sessionstart mit Strecke und Auto aus der statischen Seite; Runden, Rennposition

**Roh gespeichert**

- jede Seite vollständig – der ganze Speicherbereich, nicht nur die dekodierten Bytes – jedes Mal, wenn sich ihre Bytes ändern, beim 10-Hz-Lesen des Watchers: `acevo_pmf_physics`, `acevo_pmf_static`; ein erneutes Lesen, das Byte für Byte dem letzten entspricht, wird in `unchanged_reads` der meta.json gezählt und nicht noch einmal gespeichert
- alles, was nur für Rundendateien dekodiert wird (`decoders/kunos.py`: Schlupf, Last, Druck, Temperaturen, Sturz, Federung, Aufstandspunkte, Bremstemperaturen, Schlupfverhältnis und -winkel jedes Rads; Welt- und Lokalgeschwindigkeit, Winkelgeschwindigkeit, Fahrhilfen) steht in diesen Seiten

**Nicht verfügbar**

- Positionen anderer Autos: Die Seiten beschreiben nur dein eigenes Auto (die Grafikseite von ACC hat in manchen Versionen Auto-IDs und Koordinaten für andere – sie stehen in der Rohseite, werden aber nicht dekodiert)
- Physik-Ticks zwischen den Lesevorgängen des Watchers: Das Spiel schreibt die Seite mit seiner Physikrate neu (bis 333 Hz), der Watcher liest 10-mal pro Sekunde
- eine Rundenzählung oder die Rundenzeit des Spiels: Die Seiten, die AC EVO liefert, haben keine Grafikseite; Runden werden anhand der Position getrennt

**Größe**: etwa 150–300 MB pro Stunde vor der Komprimierung (eine 4-KB-Region pro Seite bei bis zu 10 Änderungen pro Sekunde); die Seiten bestehen meist aus Nullen, und zstd behält nur einen kleinen Bruchteil

## Geprüft {#verified}

Die Dekodierung stammt vom Rundenaufzeichner von gamecapture (getestet mit synthetischen Seiten); der Adapter wurde mit einem im Test aus dem dokumentierten Layout gebauten gemeinsamen Speicher geprüft; noch nicht gegen das Spiel getestet; der Name der ausführbaren Datei stammt aus Berichten von Spielern

## Quelle {#source}

[heat3d_watch/adapters/racing.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/racing.py)

<!-- Aus dem Adapter erzeugt von tools/gen_game_pages.py; ändere den Adapter und führe das Skript erneut aus, statt diese Seite zu bearbeiten. -->
