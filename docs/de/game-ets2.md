---
title: "Euro Truck Simulator 2 (Live-Daten)"
nav_order: 19
lang: "de"
source: game-ets2.md
source_hash: "537f0daeedbf"
nav_exclude: true
search_exclude: true
---
# Euro Truck Simulator 2 (Live-Daten) {#euro-truck-simulator-2-live-data}

Während du Euro Truck Simulator 2 spielst, speichert der Watcher die Daten, die das Spiel selbst herausgibt. So kannst du sie später auf einer Karte im 3DHeat-Viewer ansehen.

*Technische Details: Adapter `ets2`, Art [`telemetry`](sources-and-rules.md); er läuft, solange `eurotrucks2.exe` läuft, und sucht alle 0,1 s nach neuen Daten.*

## Was aufgezeichnet wird {#what-is-recorded}

- die Weltposition des Lkw (x nach Osten, y nach oben, z nach Süden, m) mit 10 Hz während der Fahrt, alle 5 s im Stand; Richtung, Geschwindigkeit, Kilometerzähler
- begonnene Aufträge (Fracht, Start, Ziel), abgeschlossene (Ertrag, XP, km), abgebrochene; Strafen, Mautstellen, Fähren, Züge, Tankstopps
- Fähren, Züge und geladene Speicherstände unterbrechen die Route (teleport, spawn)
- Distanz, Höchstgeschwindigkeit, Lieferungen, Ertrag, XP, Strafen
- der ganze gemeinsame Speicher des Plugins in `heat.raw.parquet`, jedes Mal, wenn er sich ändert

## Woher die Daten kommen {#where-it-comes-from}

gemeinsamer Speicher Local\SCSTelemetry, geschrieben vom RenCloud-scs-sdk-plugin (Revision 12) in &lt;Spiel>\bin\win_x64\plugins

## So schaltest du es ein {#how-to-switch-it-on}

scs-telemetry.dll (Revision 12) von github.com/RenCloud/scs-sdk-plugin nach &lt;Spiel>\bin\win_x64\plugins kopieren; das Spiel fragt bei jedem Start einmal, ob das SDK erlaubt wird

## So funktioniert es {#how-it-works}

Euro Truck Simulator 2 und American Truck Simulator: das SCS-Telemetrie-SDK, über das RenCloud-Plugin.

SCS veröffentlicht ein Telemetrie-SDK (<https://modding.scssoft.com/wiki/Documentation/Engine/SDK/Telemetry>) für Plugins, die der Spieler in `<Spiel>\bin\win_x64\plugins\` ablegt. Das Spiel selbst veröffentlicht nichts; das weit verbreitete Plugin von <https://github.com/RenCloud/scs-sdk-plugin> (MIT) kopiert die Kanäle des SDK in den gemeinsamen Speicher `Local\SCSTelemetry` (32 KiB), dessen Aufbau in `scs-telemetry/inc/scs-telemetry-common.hpp` steht. Gelesen wird Revision 12 dieses Aufbaus (PLUGIN_REVID 12) und sonst nichts: Das Plugin schreibt seine Revision an Offset 40, und jede andere Revision bleibt ungelesen, statt falsch gelesen zu werden. Verwendete Offsets (Zonen so, wie der Header sie markiert; natürliche Ausrichtung):

```text
   0  bool sdkActive          4  bool paused
  40  u32  telemetry_plugin_revision, version_major, version_minor, game (1 ETS2, 2 ATS)
  64  u32  common_ui.time_abs (in-game minutes)
 504  i32  truck_i.gear
 640  i32  gameplay_i.jobDeliveredEarnedXp
 948  f32  truck_f.speed (m/s); 952 engineRpm; 1056 truckOdometer (km)
1460  f32  gameplay_f.jobDeliveredDistanceKm
2200  f64  truck_dp.coordinateX/Y/Z (m), rotationX/Y/Z (heading, pitch, roll in turns, 0..1)
2300  char[64] config_s: truckBrand +64, truckName +192, cargo +320, cityDst +448, compDst +576,
      citySrc +704, compSrc +832; 3436 gameplay_s.fineOffence[32]
4200  i64  gameplay_ll: jobCancelledPenalty, jobDeliveredRevenue, fineAmount, tollgatePayAmount,
      ferryPayAmount, trainPayAmount
4300  bool special_b: onJob, jobFinished, jobCancelled, jobDelivered, fined, tollgate, ferry,
      train, refuel, refuelPayed
```

Die Weltposition des Lkw ist das Weltkoordinatensystem von SCS: x nach Osten, y nach oben, z nach Süden, in Metern (rechtshändig, y nach oben – der Viewer zeichnet es so, wie es ist). Fähren, Züge und das Laden eines Speicherstands bewegen den Lkw, ohne dass gefahren wird: Dort wird die Route unterbrochen.

Der ganze Speicherbereich des Plugins (32 KiB: jede oben genannte Zone und die nicht gelesenen – Konfiguration des Lkw, Räder, Verschleiß, die übrigen Kanäle des Lkw und alles, was die Revision nach Byte 4400 anlegt, die Anhänger) wird bei jeder Änderung in der Roh-Beilage der Session gespeichert, `type` `SCSTelemetry` mit der `revision` daneben – auch eine Seite einer anderen Revision wird vollständig gespeichert, statt falsch gelesen zu werden.

Dasselbe Modul bedient auch: [American Truck Simulator (Live-Daten)](game-ats.md).

## Positionen und Achsen {#positions-and-axes}

| | |
|---|---|
| Positionen aufgezeichnet | ja |
| Oben-Achse | `y` |
| Einheiten | Meter (SCS-Welt: x nach Osten, y nach oben, z nach Süden) |
| Für den Viewer gespiegelt | keine |
| Einheitenskala (`scale`: der Viewer multipliziert die Positionen damit) | 1 |

Diese Werte landen in der `meta.json` jeder Session (`axes`) und, wenn die Session Positionen hat, im Footer der `heat.parquet`. So dreht und skaliert der 3DHeat-Viewer die Zeilen selbst – siehe [Die Daten](the-data.md).

## Mehrspieler {#multiplayer}

- Als online gespielt markiert (`multiplayer`): **ja**. `games --markdown` zeigt das als „allowed (reads only what the game publishes)“.
- Art `telemetry`: Es liest nur, was das Spiel oder die Plattform herausgibt (ein UDP-Port oder gemeinsamer Speicher, den das Spiel veröffentlicht). Deshalb zeichnet es auch im Online-Spiel auf, nicht nur offline. Die Markierung entscheidet nur, ob Speicher überhaupt gelesen werden darf.
- Speicher: Dieser Adapter liest **nie** den Speicher. Nur `memory`-Adapter lesen Speicher, und nie bei einem Spiel, das als online gespielt markiert ist – siehe [Quellen und Regeln](sources-and-rules.md).

## Aufgezeichnete Statistiken {#statistics-recorded}

Statistik-Schlüssel, die der Code dieses Adapters beim Namen setzt (das `stats` jeder Session in `meta.json` und die Tabelle `stats` in `watcher.sqlite`):

`deliveries`, `distance_km`, `fines`, `fines_total`, `jobs_cancelled`, `max_speed_kmh`, `refuels`, `revenue`, `tolls_total`, `xp`

Ein Schlüssel in geschweiften Klammern wird zur Laufzeit vervollständigt (`score.{team}` ist ein Schlüssel pro Team). Schlüssel, die der Code aus einer Tabelle der Spielfelder oder aus den eigenen Statistiknamen des Spiels übernimmt, stehen nicht in dieser Liste; „Was aufgezeichnet wird“ oben nennt sie.

## Vollständigkeit {#completeness}

Der Watcher folgt der [Konverterregel](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md) von 3DHeat: Was die Quelle enthält, wird gelesen oder gespeichert, nie weggelassen. Außer den Zeilen wird jedes Paket, jede Seite, jede Zeile und jede Antwort, die der Adapter bekommt, vollständig in der `heat.raw.parquet` der Session gespeichert (Spalten `time`, `ms`, `type`, `used`, `payload`, `text` und alle Felder, die nach Namen behalten werden; `used` markiert, was auch zu Zeilen wurde). `selfCheck.completeness` in `meta.json` zählt jeden `type`; `lost` ist 0.

**Gelesen**

- Status von SDK und Pause, Revision des Plugins, Spiel und Version, Ingame-Zeit, Weltposition und Richtung des Lkw, Geschwindigkeit, Kilometerzähler, Marke und Name des Lkw, Fracht, Start- und Zielstadt und -firma, Ertrag, XP und Distanz des Auftrags, Abbruchstrafe, Strafen und ihr Vergehen, Mautstellen, Fähren, Züge, die besonderen Ereignis-Flags (Zeilen, Ereignisse und Statistiken)
- neu auch auf den Positionszeilen: `pitch` und `roll` (Grad, aus den Umdrehungen des SDK), `gear` und `rpm`
- Offsets geprüft gegen eine Feld-für-Feld-Abschrift des Headers von Plugin-Revision 12, deren Zonenanfänge im Test festgeschrieben sind; noch nicht gegen das Spiel geprüft

**Roh gespeichert**

- `SCSTelemetry`: der ganze 32-KiB-Speicher des Plugins, bei jedem Lesevorgang, dessen Bytes sich von der zuletzt gespeicherten Kopie unterscheiden (`unchanged_reads` in meta.json zählt die anderen); `revision` daneben. Jede Zone: Konfiguration von Lkw und Anhänger, die Kanäle des Lkw (Pedale, Lenkung, Kraftstoff, AdBlue, Drücke, Temperaturen, Verschleiß, Licht, Räder), Platzierungs- und Beschleunigungsvektoren, Auftrags- und Spielzeichenketten und alles, was die Revision nach Byte 4400 anlegt (die Anhänger). `used` ist wahr, solange das SDK aktiv ist und die Revision 12 ist
- eine Seite einer anderen Plugin-Revision wird vollständig gespeichert, mit `used` falsch, statt falsch gelesen zu werden

**Nicht verfügbar**

- alles, was das Plugin nicht aus dem SDK kopiert, und alles, solange das Plugin nicht installiert ist: Das Spiel veröffentlicht keine eigene Telemetrie
- Lkw anderer Spieler bei TruckersMP oder in Konvois: Das SDK liefert nur den eigenen Lkw des Spielers

**Größe**: 32 KiB bis zu 10-mal pro Sekunde während der Fahrt (dann unterscheidet sich jedes Lesen): etwa 1,2 GB pro Stunde vor der Komprimierung, im Stand nur eine Kopie; der größte Teil der Seite besteht aus Nullen und Konfiguration, die sich nicht ändert, daher schrumpft zstd sie um ein Vielfaches (noch nicht an einer echten Session gemessen)

## Geprüft {#verified}

getestet mit gemeinsamem Speicher, der aus dem Header-Layout von Plugin-Revision 12 gebaut wurde; noch nicht gegen das Spiel getestet

## Quelle {#source}

[heat3d_watch/adapters/ets2.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/ets2.py)

<!-- Aus dem Adapter erzeugt von tools/gen_game_pages.py; ändere den Adapter und führe das Skript erneut aus, statt diese Seite zu bearbeiten. -->
