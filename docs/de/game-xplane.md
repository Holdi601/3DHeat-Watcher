---
title: "X-Plane (Live-Daten)"
nav_order: 50
lang: de
source: game-xplane.md
source_hash: "4e7246cce10c"
nav_exclude: true
search_exclude: true
---
# X-Plane (Live-Daten) {#x-plane-live-data}

Während du X-Plane spielst, speichert der Watcher die Daten, die das Spiel selbst ausgibt, damit du sie dir später auf einer Karte im 3DHeat-Viewer ansehen kannst.

*Technische Details: Adapter `xplane`, Art [`telemetry`](sources-and-rules.md); er läuft, solange `X-Plane.exe` läuft, und sucht alle 0,1 s nach neuen Daten.*

## Was aufgezeichnet wird {#what-is-recorded}

- eigene Position mit 10 Hz (Breite/Länge/Höhe als Meter nach Osten/oben/Norden vom ersten Messpunkt; Breite, Länge und Höhe als Spalten behalten)
- Fluglage, angezeigte und wahre Fluggeschwindigkeit, Bodengeschwindigkeit, Mach, Vertikalgeschwindigkeit, AoA, Schiebewinkel, magnetischer Kurs, AGL, g (normal, axial, seitlich), Geschwindigkeit und Drehraten, Klappen, Luftbremsen, Schub, Bodenkontakt
- Gewichte (gesamt, Treibstoff, Zuladung), Fahrwerkshebel, Autopilot, Motordrehzahl und N1, Simulationszeit und -datum, Pause, Simulationsgeschwindigkeit, Wiederholung, Außentemperatur und Luftdruck auf Meereshöhe (X-Plane 12) einmal pro Sekunde
- Starts, Landungen, Abstürze, Flugzurücksetzungen (session_start/session_end pro Flug)
- Flugzeit, Zeit in der Luft, Distanz, größte Höhe, höchste g-Kraft, Landungen
- jede Antwort, die X-Plane sendet, vollständig in heat.raw.parquet

## Woher die Daten kommen {#where-it-comes-from}

die UDP-Schnittstelle von X-Plane auf 127.0.0.1:49000 (RREF-Datarefs und RPOS-Position, dem Watcher beantwortet)

## So schaltest du es ein {#how-to-switch-it-on}

X-Plane 12: Einstellungen > Netzwerk > Eingehende Verbindungen annehmen (X-Plane 11 antwortet standardmäßig)

## So funktioniert es {#how-it-works}

X-Plane 11 und 12: die eigene UDP-Schnittstelle des Simulators auf Port 49000.

X-Plane antwortet jedem, der auf 127.0.0.1:49000 fragt, mit der gewünschten Rate, an die Adresse und den Port, von denen die Anfrage kam (das Dokument "Exchanging Data with X-Plane" von X-Plane, mitgeliefert in `<X-Plane>\Instructions\`):

```text
RREF  "RREF\0" + int32 freq + int32 index + char[400] dataref path (413 bytes).
      The answer is "RREF" + one internal byte + (int32 index, float32 value)
      pairs; freq 0 stops it.
RPOS  "RPOS\0" + the rate as a NUL-terminated ASCII string ("10\0"). The
      answer is "RPOS" + one internal byte + double lon, lat, elevation (m
      MSL) + float AGL (m), pitch, true heading, roll (deg), vx east, vy up,
      vz south (m/s), P, Q, R (rad/s), tightly packed.
```

RPOS liefert Breite und Länge als Doubles (RREF nur als Floats, etwa einen halben Meter auseinander), daher steuert RPOS die Position; RREF bringt den Rest und springt ein, wenn RPOS ausbleibt. Datarefs (Namen wie in X-Plane 12s `Resources\plugins\DataRefs.txt`, <https://developer.x-plane.com/datarefs/>):

```text
sim/flightmodel/position/latitude, longitude, elevation  deg, deg, m MSL
sim/flightmodel/position/true_theta, true_phi, true_psi  pitch, roll, true heading (deg)
sim/flightmodel/position/indicated_airspeed              knots
sim/flightmodel/position/groundspeed                     m/s
sim/flightmodel/position/y_agl                           m above ground
sim/flightmodel/forces/g_nrml                            g, normal to the wings
sim/flightmodel/failures/onground_any                    1 on the ground
sim/flightmodel2/misc/has_crashed                        1 crashed
sim/time/total_flight_time_sec                           since the flight was reset
```

Der Rest des Flugs kommt mit derselben Rate (wahre Fluggeschwindigkeit, Vertikalgeschwindigkeit, AoA, Schiebewinkel, magnetischer Kurs, Mach, axiale und seitliche g, Drehraten, Klappen, Luftbremsen, Schub: `DATAREFS`), der langsamere Zustand des Flugzeugs einmal pro Sekunde (Gewichte, Fahrwerkshebel, Autopilot-Servos, Motoren, die Simulationszeit, Pause und Geschwindigkeit, Wetter: `SLOW_DATAREFS`). Jedes Datagramm wird außerdem vollständig in der Roh-Beilage der Sitzung behalten, und meta.json nennt den Dataref hinter jedem RREF-Index.

X-Plane 12 nimmt diese nur an, wenn Einstellungen > Netzwerk > "Eingehende Verbindungen annehmen" eingeschaltet ist. Positionen kommen in eine flache Karte um den ersten Messpunkt der Sitzung (`Tangent`): x nach Osten, z nach Norden in Metern, y die Höhe über dem Meeresspiegel – so bleibt ein Geradeausflug gerade, egal wie weit er geht, was eine echte Tangentialebene mit der Erdkrümmung nach unten biegen würde. Der Ursprung der Karte ist das `geo` der Sitzung: meta.json und die Fußzeile der Tabelle tragen es, damit der Viewer die echte Welt unter den Flug legen kann.

Dieses Modul enthält außerdem, was die anderen Flugsimulatoren teilen: die flache Karte, die Flugbuchführung (Starts, Landungen, Abstürze, Distanz), den UDP-Socket und die Steam-Bibliotheksliste.

## Positionen und Achsen {#positions-and-axes}

| | |
|---|---|
| Positionen werden aufgezeichnet | ja |
| Hochachse | `y` |
| Einheiten | Meter (Osten, Höhe, Norden vom ersten Messpunkt) |
| Für den Viewer gespiegelt | `z` |
| Einheitenskala (`scale`: der Viewer multipliziert die Positionen damit) | 1 |

Diese Angaben gehen in die `meta.json` (`axes`) jeder Sitzung und, wenn die Sitzung Positionen hat, in die Fußzeile der `heat.parquet`, damit der 3DHeat-Viewer die Zeilen selbst dreht und skaliert – siehe [Die Daten](the-data.md).

## Mehrspieler {#multiplayer}

- Als online gespielt markiert (`multiplayer`): **nein**. `games --markdown` zeigt dies als "single-player".
- Art `telemetry`: Es liest nur, was das Spiel oder die Plattform herausgibt (ein UDP-Port oder gemeinsamer Speicher, den das Spiel veröffentlicht), daher zeichnet es auch im Online-Spiel auf wie offline; die Markierung entscheidet nur, ob jemals Speicher gelesen werden darf.
- Speicher: Dieser Adapter liest **niemals** Speicher. Nur `memory`-Adapter lesen Speicher, und nie bei einem Spiel, das als online gespielt markiert ist – siehe [Quellen und Regeln](sources-and-rules.md).

## Aufgezeichnete Statistiken {#statistics-recorded}

Statistikschlüssel, die der Code dieses Adapters namentlich setzt (jeweils die `stats` der Sitzung in `meta.json` und die Tabelle `stats` von `watcher.sqlite`):

`airborne_time`, `bad_packets`, `crashes`, `distance_km`, `flight_time`, `max_altitude_m`, `max_g`, `{event}s`

Ein Schlüssel in geschweiften Klammern wird zur Laufzeit vervollständigt (`score.{team}` ist ein Schlüssel pro Team). Schlüssel, die der Code aus einer Tabelle der Felder des Spiels oder aus den eigenen Statistiknamen des Spiels übernimmt, stehen nicht in dieser Liste; "Was aufgezeichnet wird" oben nennt sie.

## Vollständigkeit {#completeness}

Der Watcher folgt der [Konverterregel](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md) von 3DHeat: Was die Quelle enthält, wird gelesen oder behalten, nie verworfen. Neben den Zeilen wird jedes Paket, jede Seite, jede Zeile oder jede Antwort, die der Adapter empfängt, vollständig in der `heat.raw.parquet` der Sitzung behalten (Spalten `time`, `ms`, `type`, `used`, `payload`, `text`, dann jedes nach Name behaltene Feld; `used` markiert, was auch zu Zeilen wurde), und `selfCheck.completeness` in der `meta.json` zählt jeden `type` – `lost` ist 0.

**Gelesen**

- RPOS (10 Hz): Länge, Breite, Höhe, AGL, Nicken, wahrer Kurs, Rollen, Geschwindigkeit (Osten, oben, Süden) und Drehraten P/Q/R – alles auf den Zeilen
- RREF (10 Hz): die 27 Datarefs von `DATAREFS` – Position, Fluglage, IAS, Bodengeschwindigkeit, TAS, Vertikalgeschwindigkeit, AoA, Schiebewinkel, magnetischer Kurs, Mach, g normal/axial/seitlich, Drehraten, Klappen, Luftbremsen, Schub, AGL, abgestürzt, am Boden, Flugzeit – auf den Zeilen
- RREF (1 Hz): die 20 Datarefs von `SLOW_DATAREFS` – Gewichte, Fahrwerkshebel, Autopilot-Servos, Simulationszeit und -datum, Pause, Simulationsgeschwindigkeit, Wiederholung, Anzahl der Motoren, Drehzahl der Motoren 1–4, N1 der Motoren 1–2, Außenlufttemperatur, Luftdruck auf Meereshöhe – auf den Zeilen, wie zuletzt empfangen

**Roh behalten**

- jedes Datagramm vollständig als `payload`, unter seinem vierbuchstabigen Kopf: `RREF` und `RPOS` (verwendet, wenn die Abfrage eine Zeile erzeugte; in den Menüs, ohne Position, erzeugen sie keine), alles andere, was X-Plane an den Port des Watchers sendet, unter seinem eigenen Kopf oder als `unknown`; `requests` in meta.json sagt, welcher Dataref zu jedem RREF-Index gehört, damit die Nutzdaten ohne dieses Modul lesbar sind

**Nicht verfügbar**

- jeder andere Dataref (X-Plane hat Tausende): RREF sendet nur, was angefragt wird, eine Anmeldung je Dataref; die Liste fragt den Flug, den Zustand des Flugzeugs und die Simulationszeit ab – mehr Cockpit-Details (Funkgeräte, Lampen, jede Motoranzeige, Ausfälle) würden die Anfragen vervielfachen
- der Name des Flugzeugs und sein ICAO-Typ: Datarefs als Byte-Array, die RREF als je einen Float pro Zeichen sendet
- andere Flugzeuge (KI und Mehrspieler): die sim/multiplayer/position-Datarefs werden nicht angefragt
- die DATA-Ausgabe (Einstellungen > Datenausgabe): sie sendet an eine feste, im Simulator gewählte Adresse, nicht an den, der fragt; RREF und RPOS decken ab, was der Watcher liest

**Größe**: etwa 17 MB pro Stunde vor zstd (RREF und RPOS mit 10 Hz, etwa 220 und 70 Bytes plus ein Rahmen je Abfrage, das langsame RREF einmal pro Sekunde), wenn X-Plane die Werte jeder Abfrage in einem Paket sendet, wie es das tut; zstd verkleinert die Floats mehrfach

## Geprüft {#verified}

an einem Fake-X-Plane getestet, der RREF/RPOS nach "Exchanging Data with X-Plane" von X-Plane 12 beantwortet; Dataref-Namen gegen die DataRefs.txt von X-Plane 12 geprüft; nicht gegen den laufenden Simulator getestet

## Quelle {#source}

[heat3d_watch/adapters/xplane.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/xplane.py)

<!-- Generated from the adapter by tools/gen_game_pages.py; change the adapter and run it again rather than editing this page. -->
