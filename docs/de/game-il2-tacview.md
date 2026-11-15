---
title: "IL-2 Sturmovik: Great Battles (Wiederholungen)"
nav_order: 27
lang: "de"
source: game-il2-tacview.md
source_hash: "0bb23bddee03"
nav_exclude: true
search_exclude: true
---
# IL-2 Sturmovik: Great Battles (Wiederholungen) {#il-2-sturmovik-great-battles-replays}

Nach einem Gefecht von IL-2 Sturmovik: Great Battles macht der Watcher aus der Wiederholung, die das Spiel gespeichert hat, Dateien, die du auf einer Karte im 3DHeat-Viewer ansehen kannst.

*Technische Details: Adapter `il2-tacview`, Art [`replay`](sources-and-rules.md); er läuft immer (er wartet nicht darauf, dass ein Spiel startet) und sucht alle 5 s nach neuen Daten.*

## Was aufgezeichnet wird {#what-is-recorded}

- jedes Flugzeug, Fahrzeug und Schiff der Aufnahme: Positionen einmal pro Sekunde (Meter nach Osten/oben/Norden vom Bezugspunkt der Aufnahme; Breite/Länge/Höhe als Spalten)
- Erscheinen, Zerstörungen (Tod) und Abgänge (left), Starts und Landungen, wenn sie aufgezeichnet wurden
- Objekte, Zerstörungen, Starts, Landungen und Länge pro Aufnahme
- jede Zeile der Aufnahme vollständig in heat.raw.parquet, auf der Uhr der Zeilen

## Woher die Daten kommen {#where-it-comes-from}

die eigenen Tacview-Aufnahmen des Spiels &lt;Spiel>\data\Tracks\\\*.acmi (ACMI-2.x-Text, einfach oder gezippt)

## So schaltest du es ein {#how-to-switch-it-on}

python -m heat3d_watch setup il2-tacview --apply (tacviewrecord = 1 in [KEY = track_record])

Gib den Befehl in einem Terminal ein, das im Ordner des Watchers geöffnet ist (siehe [Bevor du anfängst](before-you-start.md)). Wenn er fehlschlägt, sagt die letzte Zeile, warum; [Installation und Start](installing-and-running.md) behandelt die üblichen Ursachen.

`python -m heat3d_watch setup il2-tacview` listet die Dateien auf, die er ändern würde; `python -m heat3d_watch setup il2-tacview --apply` ändert sie und sichert das Original als `<file>.heat3d-backup` (siehe [Befehle](commands.md#setup)). Für jede Änderung gibt er `il2-tacview: changed: ...` aus, oder `il2-tacview: nothing to change`, wenn es schon eingeschaltet ist.

## So funktioniert es {#how-it-works}

IL-2 Sturmovik: Great Battles – die Telemetrie-UDP-Ausgabe des Spiels und seine eigenen Tacview-Aufnahmen.

1. Telemetrie ("Telemetry output of IL2 v4.003", Revision 1.2, mitgeliefert als
   `<Spiel>\Doc\UDP_Output\Il2_TeleOutput.pdf`). Eingeschaltet in
   `<Spiel>\data\startup.cfg`, Abschnitt `[KEY = telemetrydevice]`: `addr`,
   `addr1`, ... = "IP[:port]" (mehrere Ziele gleichzeitig), `decimation` (50 Hz /
   n), `enable`, `port`. `setup` fügt ein Ziel hinzu, 127.0.0.1:41995 (JoyPro nutzt
   41994, der Standard des Spiels ist 4322), und schaltet die Ausgabe ein. Pakete,
   Little-Endian:

   ```text
   DWORD  Packet_ID 0x54000101
   WORD   Size
   DWORD  Tick (1/50 s)
   BYTE   Indicators_Count, then SIndicator {WORD id, BYTE n, n x 32-bit float}
   BYTE   Events_Count,     then SEvent     {WORD id, BYTE size, size bytes}
   ```

   Indikatoren: 0 ENG_RPM, 1 ENG_MP, 2/3 Motorvibration, 4 LGEARS_STATE, 5
   LGEARS_PRESS, 6 EAS (m/s), 7 AOA (rad), 8 ACCELERATION (xyz inkl. Schwerkraft),
   9 COCKPIT_SHAKE, 10 AGL (m), 11 FLAPS, 12 AIR_BRAKES, 13 AOS (rad), 14
   VERTICAL_SPEED (m/s). Ereignisse (2 Byte gepackt): 0 SET_FOCUS (STRING: Längenbyte
   + ASCII), 1 SETUP_ENG {short index, short id, float pos[3], float
   max_rpm}, 2 SETUP_GUN {short index, float pos[3], float projectile mass,
   float muzzle velocity}, 3 SETUP_LGEAR {short index, short id, float
   pos[3]}, 4 DROP_BOMB und 5 ROCKET_LAUNCH
   {float pos[3], float mass, WORD flags}, 6 HIT und 7 DAMAGE {float pos[3],
   float force[3]}, 8 EXPLOSION {float pos[3], float radius}, 9 GUN_FIRE {BYTE
   gun}, 10 SRV_ADDR, 11 SRV_TITLE, 12 SRS_ADDR (STRING), 13 CLIENT_DAT {long
   client, long server client, char name[32]}, 14 CTRL_DAT {long parent, short
   coalition}. Ereignispositionen sind lokal zum Flugzeug des Spielers; der Strom
   hat gar keine Weltposition – das sind also Ereignisse und Zahlen, keine Spur.

2. Tacview-Aufnahme: `tacviewrecord = 1` in `[KEY = track_record]` lässt das Spiel
   `<Spiel>\data\Tracks\*.acmi` schreiben (im Mehrspielerspiel entscheidet der Server).
   Eine fertige Datei wird umgewandelt: jedes Flugzeug, Fahrzeug und Schiff mit seinen
   Positionen, Erscheinen und Entfernen (zerstört oder verschwunden), Starts und
   Landungen, wenn die Aufnahme sie hat. ACMI-2.x-Textformat, einfach oder gezippt,
   nach <https://www.tacview.net/documentation/acmi/en/> – Zeilen "#t" bewegen die
   Uhr, Zeilen "id,Key=Value,..." setzen Eigenschaften (hexadezimale IDs, Kommas
   mit "\\," maskiert, ein nachgestelltes "\\" setzt die Zeile fort), "-id" entfernt
   ein Objekt, Objekt 0 trägt die globalen Werte (ReferenceLongitude/Latitude,
   RecordingTime, ...) und die Ereignisse ("Event=Destroyed\|id\|text"). T = Lon\|Lat\|Alt[\|U\|V] oder
   Lon\|Lat\|Alt\|Roll\|Pitch\|Yaw[\|U\|V\|Heading], Länge und Breite relativ zum
   Bezugspunkt, leere Felder bleiben unverändert. Positionen kommen in eine flache Karte
   um den Bezugspunkt: x nach Osten, y Höhe, z nach Norden, in Metern. Der Bezugspunkt
   ist das `geo` der Sitzung, in meta.json und in der Fußzeile der Tabelle mitgeführt,
   damit der Viewer die echte Welt unter die Spuren legen kann.

Dasselbe Modul bedient auch: [IL-2 Sturmovik: Great Battles (Live-Daten)](game-il2.md).

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

- Als online gespielt markiert (`multiplayer`): **ja**. `games --markdown` zeigt dies als "allowed (reads only what the game publishes)".
- Art `replay`: Es liest nur, was das Spiel oder die Plattform herausgibt (Wiederholungen und Demos, die das Spiel speichert), daher zeichnet es auch im Online-Spiel auf wie offline; die Markierung entscheidet nur, ob jemals Speicher gelesen werden darf.
- Speicher: Dieser Adapter liest **niemals** Speicher. Nur `memory`-Adapter lesen Speicher, und nie bei einem Spiel, das als online gespielt markiert ist – siehe [Quellen und Regeln](sources-and-rules.md).

## Aufgezeichnete Statistiken {#statistics-recorded}

Statistikschlüssel, die der Code dieses Adapters namentlich setzt (jeweils die `stats` der Sitzung in `meta.json` und die Tabelle `stats` von `watcher.sqlite`):

`destroyed`, `duration_s`, `objects`, `{r.event}s`

Ein Schlüssel in geschweiften Klammern wird zur Laufzeit vervollständigt (`score.{team}` ist ein Schlüssel pro Team). Schlüssel, die der Code aus einer Tabelle der Felder des Spiels oder aus den eigenen Statistiknamen des Spiels übernimmt, stehen nicht in dieser Liste; "Was aufgezeichnet wird" oben nennt sie.

## Vollständigkeit {#completeness}

Der Watcher folgt der [Konverterregel](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md) von 3DHeat: Was die Quelle enthält, wird gelesen oder behalten, nie verworfen. Neben den Zeilen wird jedes Paket, jede Seite, jede Zeile oder jede Antwort, die der Adapter empfängt, vollständig in der `heat.raw.parquet` der Sitzung behalten (Spalten `time`, `ms`, `type`, `used`, `payload`, `text`, dann jedes nach Name behaltene Feld; `used` markiert, was auch zu Zeilen wurde), und `selfCheck.completeness` in der `meta.json` zählt jeden `type` – `lost` ist 0.

**Gelesen**

- die Position (T: Länge, Breite, Höhe, Rollen, Nicken, Gieren, U, V, Kurs) jedes Objekts einmal pro Sekunde und Objekt, mit Name, Typ, Pilot, Koalition/Farbe, Land, Gruppe und Eltern
- Erscheinen, Entfernungen (Tod, wenn zuerst ein Destroyed-Ereignis kam, sonst left), Ereignisse TakenOff und Landed, Message- und Bookmark-Ereignisse als Zeilen
- die Globalwerte ReferenceLongitude/Latitude (der Ursprung der Karte), RecordingTime/ReferenceTime (wann), DataSource, DataRecorder und Title in meta.json

**Roh behalten**

- jede nicht leere logische Zeile vollständig als `text` (eine mit nachgestelltem Backslash fortgesetzte Zeile wird zusammengefügt, wie ACMI sie liest), unter ihrer Art: `header` (FileType, FileVersion), `comment`, `time` (#t), `remove` (-id), `global` und `event` (Objekt 0), `object` (id,Key=Value,...)
- was nur der Roh-Speicher hält: die Positionen zwischen den einmal pro Sekunde geschriebenen Zeilen, Waffen, Geschosse, Leuchtraketen, Düppel und andere Objekte, die nicht als Spuren gezeichnet werden, jede andere Eigenschaft (Telemetrie wie IAS, AOA, Gas, Treibstoff, wo die Aufnahme sie hat), andere Globalwerte (Comments, Briefing, Author, Category), Ereignisse außer den gelesenen (Timeout, LeftArea, ...)

**Nicht verfügbar**

- alles, was die Aufnahme nicht enthält; was das Spiel nicht in seine Aufnahmen schreibt, ist nicht darin

**Größe**: etwa der eigene Text der Aufnahme plus rund 70 Bytes pro Zeile, vor zstd: eine 100-MB-Aufnahme ergibt etwa 150–250 MB Rohdaten, die zstd fast auf die Größe der gezippten Aufnahme bringt

## Geprüft {#verified}

an synthetischen ACMI-2.2-Dateien getestet (Text und gezippt); nicht an einer Aufnahme aus dem Spiel getestet

## Quelle {#source}

[heat3d_watch/adapters/il2.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/il2.py)

<!-- Generated from the adapter by tools/gen_game_pages.py; change the adapter and run it again rather than editing this page. -->
