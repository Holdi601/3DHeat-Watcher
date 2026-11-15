---
title: "Richard Burns Rally (Live-Daten)"
nav_order: 39
lang: de
source: game-richard-burns-rally.md
source_hash: "1b9866f5a1f6"
nav_exclude: true
search_exclude: true
---
# Richard Burns Rally (Live-Daten) {#richard-burns-rally-live-data}

Während du Richard Burns Rally spielst, speichert der Watcher die Daten, die das Spiel selbst herausgibt. So kannst du sie später auf einer Karte im 3DHeat-Viewer ansehen.

*Technische Details: Adapter `richard-burns-rally`, Art [`telemetry`](sources-and-rules.md); er läuft, solange `RichardBurnsRally_SSE.exe` oder `RichardBurnsRally.exe` läuft, und sucht alle 0,1 s nach neuen Daten.*

## Was aufgezeichnet wird {#what-is-recorded}

- Position deines eigenen Autos (Welt-XYZ, m) mit 10 Hz, zusammen mit Geschwindigkeit, Gang, Gas, Bremse und Etappenstrecke
- Etappenstart (die Etappenuhr beginnt), Ende mit der Etappenzeit, Neustarts
- Teleports (Zurücksetzen auf die Straße): `teleport` dort, wo das Auto war, `spawn` dort, wo es jetzt ist
- Etappen, Bestzeit einer Etappe, Distanz, Höchstgeschwindigkeit

## Woher die Daten kommen {#where-it-comes-from}

UDP-Telemetrie des NGP-Plugins, 127.0.0.1:6776 (RichardBurnsRally.ini [NGP] udpTelemetry=1)

## So schaltest du es ein {#how-to-switch-it-on}

RSF/NGP: In RichardBurnsRally.ini im Abschnitt [NGP] `udpTelemetry=1` setzen und den Endpunkt auf 127.0.0.1:6776

## So funktioniert es {#how-it-works}

Die eigene Telemetrie der Rennspiele: Forza, die Assetto-Corsa-Spiele, die Rally-Spiele und BeamNG, aufgezeichnet als Strecken, Runden und Etappen.

Jedes Spiel hier veröffentlicht seine Telemetrie absichtlich, für Dashboards und Bewegungssimulatoren. Nichts wird eingeschleust, und es wird nichts gelesen, was das Spiel nicht selbst herausgibt. Die Dekodierung wird nicht doppelt geschrieben: Sie stammt aus den Rundenaufzeichnern von gamecapture in `heat3d_capture/telemetry` von 3DHeat GameCapture, kopiert nach `heat3d_watch/decoders` (dort getestet mit Paketen, die aus den veröffentlichten Layouts gebaut wurden). Dieses Modul macht daraus die Zeilen des Watchers: die Position des Autos mehrmals pro Sekunde mit Geschwindigkeit, Gang und Pedalen, ein Ereignis pro Runde oder Etappe und die Zahlen, die ein Fahrer sich merkt: Runden, Bestrunde, Distanz, Höchstgeschwindigkeit.

#### Forza (Horizon 4/5/6, Motorsport) {#forza-horizon-456-motorsport}

„Data Out“-UDP, eingeschaltet im HUD und in den Spieleinstellungen des Spiels, an 127.0.0.1 Port 5300, Format Dash. Ein Paket pro Simulationstick; der Offset des Dash-Blocks wird aus den Paketen ermittelt (`forza.detect_layout`). Welt in Metern, Y nach oben; die Welt ist linkshändig und wird so gezeichnet, wie sie gesendet wird, wie es auch der Rundenaufzeichner tut (die „Data Out“-Dokumentation von Forza Motorsport und Forza Horizon). Das Spiel sendet an einen Port, und FH Companion und andere Data-Out-Apps hören auf denselben. Zwei Programme können ihn nicht gemeinsam nutzen: Unter Windows bekommt der an 127.0.0.1 gebundene Socket die Pakete, und ein Socket, der an alle Adressen auf demselben Port gebunden ist, bekommt keine, egal wer zuerst da war. Deshalb wartet der Watcher kurz, nachdem das Spiel gestartet ist, bevor er den Port belegt, nimmt ihn nie einer App weg, die ihn schon hält, und gibt ihn sofort frei, wenn eine andere App auf ihm zu lauschen beginnt. Solange der Watcher den Port hält, leitet er jedes Paket unverändert an 127.0.0.1:5301 weiter. Stell das Port-Feld von FH Companion (dessen Telemetrie-Reiter) auf 5301, dann zeichnen beide auf.

#### EA SPORTS WRC, DiRT Rally 2.0, Richard Burns Rally {#ea-sports-wrc-dirt-rally-20-richard-burns-rally}

UDP: WRC über `Documents/My Games/WRC/telemetry/config.json` (das Paket `session_update` der Struktur `wrc`), DiRT über `hardware_settings_config.xml` (`<udp enabled="true" extradata="3" port="20777">`), RBR über das NGP-Plugin (`udpTelemetry=1`, Port 6776). Etappen nach der Etappenuhr des Spiels (`rally.StageSplitter`). RBR dokumentiert seine Achsen nicht: Die Oben-Achse ist die, entlang der sich die Etappe am wenigsten verändert; das wird entschieden, wenn die Session schließt.

#### Alles wird gespeichert {#everything-kept}

Die Zeilen kommen einige pro Sekunde; die Spiele senden weit mehr. Jedes UDP-Paket, das ankommt – in den Menüs, zwischen den Runden, auch solche, die kein Dekodierer liest –, wird vollständig in der `heat.raw.parquet` der Session gespeichert, unter seinem Format (`dash-horizon`, `session_update`, `extradata3`, `H3D1`, ...). Jede Seite des gemeinsamen Speichers (der ganze Bereich, nicht nur die dekodierten Bytes) wird bei jeder Änderung unter dem Namen ihres Bereichs gespeichert (`acpmf_physics`, ...). `used` markiert, was auch zu Zeilen wurde; `selfCheck.completeness` in `meta.json` zählt jede Art (die Konverterregel von 3DHeat).

Dasselbe Modul bedient auch: [Assetto Corsa (Live-Daten)](game-assetto-corsa.md), [Assetto Corsa Competizione (Live-Daten)](game-assetto-corsa-competizione.md), [Assetto Corsa EVO (Live-Daten)](game-assetto-corsa-evo.md), [Assetto Corsa Rally (Live-Daten)](game-assetto-corsa-rally.md), [BeamNG.drive (Live-Daten)](game-beamng.md), [DiRT Rally 2.0 (Live-Daten)](game-dirt-rally-2.md), [EA SPORTS WRC (Live-Daten)](game-ea-wrc.md), [Forza Horizon 4 (Live-Daten)](game-forza-horizon-4.md), [Forza Horizon 5 (Live-Daten)](game-forza-horizon-5.md), [Forza Horizon 6 (Live-Daten)](game-forza-horizon-6.md), [Forza Motorsport (Live-Daten)](game-forza-motorsport.md).

## Positionen und Achsen {#positions-and-axes}

| | |
|---|---|
| Positionen aufgezeichnet | ja |
| Oben-Achse | `y` |
| Einheiten | Meter; Oben-Achse aus der Fahrt bestimmt (RBR dokumentiert seine Achsen nicht) |
| Für den Viewer gespiegelt | keine |
| Einheitenskala (`scale`: der Viewer multipliziert die Positionen damit) | 1 |

Diese Werte landen in der `meta.json` jeder Session (`axes`) und, wenn die Session Positionen hat, im Footer der `heat.parquet`. So dreht und skaliert der 3DHeat-Viewer die Zeilen selbst – siehe [Die Daten](the-data.md).

## Mehrspieler {#multiplayer}

- Als online gespielt markiert (`multiplayer`): **nein**. `games --markdown` zeigt das als „single-player“.
- Art `telemetry`: Es liest nur, was das Spiel oder die Plattform herausgibt (ein UDP-Port oder gemeinsamer Speicher, den das Spiel veröffentlicht). Deshalb zeichnet es auch im Online-Spiel auf, nicht nur offline. Die Markierung entscheidet nur, ob Speicher überhaupt gelesen werden darf.
- Speicher: Dieser Adapter liest **nie** den Speicher. Nur `memory`-Adapter lesen Speicher, und nie bei einem Spiel, das als online gespielt markiert ist – siehe [Quellen und Regeln](sources-and-rules.md).

## Aufgezeichnete Statistiken {#statistics-recorded}

Statistik-Schlüssel, die der Code dieses Adapters beim Namen setzt (das `stats` jeder Session in `meta.json` und die Tabelle `stats` in `watcher.sqlite`):

`best_lap`, `best_stage`, `distance_km`, `laps`, `stages`, `top_speed_kmh`

Ein Schlüssel in geschweiften Klammern wird zur Laufzeit vervollständigt (`score.{team}` ist ein Schlüssel pro Team). Schlüssel, die der Code aus einer Tabelle der Spielfelder oder aus den eigenen Statistiknamen des Spiels übernimmt, stehen nicht in dieser Liste; „Was aufgezeichnet wird“ oben nennt sie.

## Vollständigkeit {#completeness}

Der Watcher folgt der [Konverterregel](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md) von 3DHeat: Was die Quelle enthält, wird gelesen oder gespeichert, nie weggelassen. Außer den Zeilen wird jedes Paket, jede Seite, jede Zeile und jede Antwort, die der Adapter bekommt, vollständig in der `heat.raw.parquet` der Session gespeichert (Spalten `time`, `ms`, `type`, `used`, `payload`, `text` und alle Felder, die nach Namen behalten werden; `used` markiert, was auch zu Zeilen wurde). `selfCheck.completeness` in `meta.json` zählt jeden `type`; `lost` ist 0.

**Gelesen**

- Zeilen mit 10 Hz: Position, Geschwindigkeit, Gang, Gas, Bremse, Etappenstrecke, Gieren, Drehzahl, Lenkung; Etappenstart, Etappenende mit der Etappenzeit, Neustarts

**Roh gespeichert**

- jedes Paket, das am Port ankommt, vollständig, mit der Rate des Spiels: `telemetry` (die 664-Byte-TelemetryData des NGP), `rbr <n>-byte` für alles andere
- im Paket neben den Zeilen: Lage des Autos, die eigenen Geschwindigkeiten und Beschleunigungen des Autos, Federweg und Kraft je Rad, der Fortschritt der Etappe und die Strecke bis zu ihrem Ende; der Rest der 664 Byte (Motor, Reifen- und Bremsblöcke je Rad) wird noch nirgends dekodiert

**Nicht verfügbar**

- andere Autos: Die Spiele senden nur das Auto des Spielers
- seine Geschwindigkeitseinheit und Achsen: nicht dokumentiert – die Geschwindigkeit wird aus den Positionen genommen, die Oben-Achse aus der Fahrt

**Größe**: etwa 160 MB pro Stunde bei 60 Paketen pro Sekunde (664 Byte plus ein 70-Byte-Kopf pro Eintrag); zstd behält nur einen Bruchteil

## Geprüft {#verified}

Die Dekodierung stammt vom Rundenaufzeichner von gamecapture (getestet mit Paketen, die aus den dokumentierten Layouts gebaut wurden); der Adapter wurde mit im Test gebauten Paketen geprüft, die über UDP gesendet wurden; noch nicht gegen das Spiel getestet

## Quelle {#source}

[heat3d_watch/adapters/racing.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/racing.py)

<!-- Aus dem Adapter erzeugt von tools/gen_game_pages.py; ändere den Adapter und führe das Skript erneut aus, statt diese Seite zu bearbeiten. -->
