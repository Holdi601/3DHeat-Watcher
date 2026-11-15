---
title: "IL-2 Sturmovik: Great Battles (Live-Daten)"
nav_order: 26
lang: "de"
source: game-il2.md
source_hash: "b6c4de7dcc14"
nav_exclude: true
search_exclude: true
---
# IL-2 Sturmovik: Great Battles (Live-Daten) {#il-2-sturmovik-great-battles-live-data}

Während du IL-2 Sturmovik: Great Battles spielst, speichert der Watcher die Daten, die das Spiel selbst ausgibt, damit du sie dir später als Statistik und Zeitleiste ansehen kannst.

*Technische Details: Adapter `il2`, Art [`telemetry`](sources-and-rules.md); er läuft, solange `Il-2.exe` oder `IL2Series.exe` läuft, und sucht alle 0,1 s nach neuen Daten.*

## Was aufgezeichnet wird {#what-is-recorded}

- Einsätze: das übernommene Flugzeug (spawn) und wann die Ausgabe aufhört (session_end) – keine Weltposition: das Spiel sendet keine
- abgeworfene Bomben und abgefeuerte Raketen (Masse), Treffer und erlittener Schaden, Explosionen, Feuerstöße der Bordwaffen – Positionen lokal zum Flugzeug
- scheinbare Fluggeschwindigkeit (EAS), AGL, Vertikalgeschwindigkeit, g, Motordrehzahl einmal pro Sekunde, dazu jeder andere Indikator im Paket (Ladedruck, Motorvibration, Fahrwerkszustand und -druck, AoA, Schiebewinkel, Beschleunigung x/y/z, Cockpitvibration, Klappen, Luftbremsen)
- Einsätze, abgefeuerte Schüsse, Bomben, Raketen, erlittene Treffer, Höchstgeschwindigkeit, höchste g-Kraft, Flugzeit; Servername und Pilotenname im Netz
- jedes Telemetriepaket vollständig in heat.raw.parquet

## Woher die Daten kommen {#where-it-comes-from}

die UDP-Telemetrieausgabe des Spiels an 127.0.0.1:41995 ([KEY = telemetrydevice] in &lt;Spiel>\data\startup.cfg)

## So schaltest du es ein {#how-to-switch-it-on}

python -m heat3d_watch setup il2 --apply (fügt addrN = "127.0.0.1:41995", enable = true hinzu), dann IL-2 neu starten

Gib den Befehl in einem Terminal ein, das im Ordner des Watchers geöffnet ist (siehe [Bevor du anfängst](before-you-start.md)). Wenn er fehlschlägt, sagt die letzte Zeile, warum; [Installation und Start](installing-and-running.md) behandelt die üblichen Ursachen.

`python -m heat3d_watch setup il2` listet die Dateien auf, die er ändern würde; `python -m heat3d_watch setup il2 --apply` ändert sie und sichert das Original als `<file>.heat3d-backup` (siehe [Befehle](commands.md#setup)). Für jede Änderung gibt er `il2: changed: ...` aus, oder `il2: nothing to change`, wenn es schon eingeschaltet ist.

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

Dasselbe Modul bedient auch: [IL-2 Sturmovik: Great Battles (Wiederholungen)](game-il2-tacview.md).

## Positionen und Achsen {#positions-and-axes}

| | |
|---|---|
| Positionen werden aufgezeichnet | nein |
| Hochachse | `y` |
| Einheiten | keine: die Telemetrie hat keine Weltpositionen |
| Für den Viewer gespiegelt | nein |
| Einheitenskala (`scale`: der Viewer multipliziert die Positionen damit) | 1 |

Diese Angaben gehen in die `meta.json` (`axes`) jeder Sitzung und, wenn die Sitzung Positionen hat, in die Fußzeile der `heat.parquet`, damit der 3DHeat-Viewer die Zeilen selbst dreht und skaliert – siehe [Die Daten](the-data.md).

## Mehrspieler {#multiplayer}

- Als online gespielt markiert (`multiplayer`): **ja**. `games --markdown` zeigt dies als "allowed (reads only what the game publishes)".
- Art `telemetry`: Es liest nur, was das Spiel oder die Plattform herausgibt (ein UDP-Port oder gemeinsamer Speicher, den das Spiel veröffentlicht), daher zeichnet es auch im Online-Spiel auf wie offline; die Markierung entscheidet nur, ob jemals Speicher gelesen werden darf.
- Speicher: Dieser Adapter liest **niemals** Speicher. Nur `memory`-Adapter lesen Speicher, und nie bei einem Spiel, das als online gespielt markiert ist – siehe [Quellen und Regeln](sources-and-rules.md).

## Aufgezeichnete Statistiken {#statistics-recorded}

Statistikschlüssel, die der Code dieses Adapters namentlich setzt (jeweils die `stats` der Sitzung in `meta.json` und die Tabelle `stats` von `watcher.sqlite`):

`bad_packets`, `bombs_dropped`, `damage_taken`, `explosions`, `flight_time`, `hits_taken`, `max_agl_m`, `max_eas_kmh`, `max_g`, `ordnance_kg`, `rockets_fired`, `rounds_fired`, `sorties`

Ein Schlüssel in geschweiften Klammern wird zur Laufzeit vervollständigt (`score.{team}` ist ein Schlüssel pro Team). Schlüssel, die der Code aus einer Tabelle der Felder des Spiels oder aus den eigenen Statistiknamen des Spiels übernimmt, stehen nicht in dieser Liste; "Was aufgezeichnet wird" oben nennt sie.

## Vollständigkeit {#completeness}

Der Watcher folgt der [Konverterregel](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md) von 3DHeat: Was die Quelle enthält, wird gelesen oder behalten, nie verworfen. Neben den Zeilen wird jedes Paket, jede Seite, jede Zeile oder jede Antwort, die der Adapter empfängt, vollständig in der `heat.raw.parquet` der Sitzung behalten (Spalten `time`, `ms`, `type`, `used`, `payload`, `text`, dann jedes nach Name behaltene Feld; `used` markiert, was auch zu Zeilen wurde), und `selfCheck.completeness` in der `meta.json` zählt jeden `type` – `lost` ist 0.

**Gelesen**

- SET_FOCUS (das übernommene Flugzeug: ein Einsatz), DROP_BOMB und ROCKET_LAUNCH (Masse, lokale Position), HIT und DAMAGE (lokale Position, Kraft), EXPLOSION (lokale Position, Radius), GUN_FIRE (Schüsse pro Abfrage) als Zeilen
- SETUP_ENG (Index, ID, lokale Position, maximale Drehzahl), SETUP_GUN (Index, lokale Position, Geschossmasse, Mündungsgeschwindigkeit) und SETUP_LGEAR (Index, ID, lokale Position) als Zeilen: die Motoren, Waffen und Fahrwerksbeine des Flugzeugs zu Beginn des Einsatzes
- SRV_TITLE, SRV_ADDR, SRS_ADDR und CLIENT_DAT (Pilotenname) in meta.json; die Koalition aus CTRL_DAT als Team des Einsatzes
- alle fünfzehn Indikatoren der Spezifikation in der einmal pro Sekunde geschriebenen Zeile `state` (ein Wert als Zahl, je Motor, Fahrwerksbein oder Achse als Liste); Höchstgeschwindigkeit, g und AGL aus jedem Paket

**Roh behalten**

- jedes Datagramm vollständig als `payload`, unter seiner Packet_ID: `0x54000101` für Telemetrie (verwendet, wenn daraus eine Zeile oder ein meta.json-Eintrag wurde), jede andere ID als sie selbst, ein Datagramm, das zu kurz für eines ist, als `short`
- was nur der Roh-Speicher hält: die Indikatoren zwischen den einmal pro Sekunde geschriebenen Zeilen (das Spiel sendet sie mit 50 Hz / Decimation), ein SETUP-Ereignis, das kürzer ist als das Layout der Spezifikation, Ereignis-IDs, die die Spezifikation nicht auflistet

**Nicht verfügbar**

- eine Weltposition: die Telemetrieausgabe hat keine (Ereignispositionen sind lokal zum Flugzeug); der Adapter il2-tacview liest Positionen aus den eigenen Tacview-Aufnahmen des Spiels
- andere Flugzeuge und Spieler: die Ausgabe beschreibt nur das eigene Flugzeug des Spielers

**Größe**: etwa 8 MB pro Stunde bei den 10 Hz der Einrichtung (Decimation 5; ein Paket ist etwa 160 Bytes plus sein Rahmen), 40 MB bei den vollen 50 Hz des Spiels, vor zstd; zstd schrumpft die sich wiederholenden Floats auf einen Bruchteil

## Geprüft {#verified}

an Paketen getestet, die aus der eigenen Spezifikation des Spiels (Il2_TeleOutput, Rev. 1.2) gebaut wurden; Änderungen an startup.cfg an einer Kopie der Datei getestet; nicht gegen das laufende Spiel getestet

## Quelle {#source}

[heat3d_watch/adapters/il2.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/il2.py)

<!-- Generated from the adapter by tools/gen_game_pages.py; change the adapter and run it again rather than editing this page. -->
