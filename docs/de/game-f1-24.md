---
title: "EA SPORTS F1 24 (Live-Daten)"
nav_order: 15
lang: de
source: game-f1-24.md
source_hash: "a189298930fc"
nav_exclude: true
search_exclude: true
---
# EA SPORTS F1 24 (Live-Daten) {#ea-sports-f1-24-live-data}

Während du EA SPORTS F1 24 spielst, speichert der Watcher die Daten, die das Spiel selbst herausgibt, damit du sie dir später auf einer Karte im 3DHeat-Viewer ansehen kannst.

*Technische Details: Adapter `f1-24`, Art [`telemetry`](sources-and-rules.md); er läuft, solange `F1_24.exe` läuft, und sucht alle 0,1 s nach neuen Daten.*

## Was aufgezeichnet wird {#what-is-recorded}

- die Position jedes Autos (Welt-XYZ, m) mit 10 Hz, nach Fahrername, Team, das eigene Auto markiert (`own_car` 1, aus dem Index des Spielerautos), mit Geschwindigkeit, Gang, Gas, Bremse, Lenkung, Drehzahl, DRS, Gier, Nick und Rollen (Grad) und g-Kräften
- Runden je Auto mit der Rundenzeit und der Platzierung im Rennen; Zielankünfte und Ausfälle
- die Renn-Ereignisse des Spiels: Sessionstart und -ende, schnellste Runde, Strafen, Überholmanöver, Kollisionen, Safety Car, rote Flagge, Startampeln, Zielflagge, Sieger, Flashbacks (`teleport`, wo das Auto war, `spawn`, wohin es zurückkehrte)
- Strecke, Sessiontyp, Runden und Fahrer jeder Session
- eigene Runden, Bestzeit, Renn- und Startplatz, Boxenstopps, Strafen, Überholmanöver, Kollisionen, Strecke, Höchstgeschwindigkeit
- jedes Paket, das das Spiel sendet, vollständig in `heat.raw.parquet` - auch die, die nicht in Zeilen gelesen werden

## Woher es kommt {#where-it-comes-from}

UDP-Telemetrie 127.0.0.1:20777 (Documents\My Games\F1 24\hardwaresettings\hardware_settings_config.xml)

## So schaltest du es ein {#how-to-switch-it-on}

Im Spiel: Einstellungen > Telemetrie-Einstellungen > UDP-Telemetrie an, IP 127.0.0.1, Port 20777 - oder `python -m heat3d_watch setup f1-24 --apply` (ändert hardware_settings_config.xml, vorher gesichert; das Spiel muss geschlossen sein). Solange ein anderes Programm Port 20777 belegt, lässt der Watcher ihm den Port

Gib den Befehl in einem Terminal ein, das im Ordner des Watchers geöffnet ist (siehe [Vor dem Start](before-you-start.md)). Wenn er fehlschlägt, sagt die letzte Zeile, warum; [Installation und Start](installing-and-running.md) beschreibt die üblichen Ursachen.

`python -m heat3d_watch setup f1-24` listet die Dateien auf, die er ändern würde; `python -m heat3d_watch setup f1-24 --apply` ändert sie und hebt das Original als `<file>.heat3d-backup` auf (siehe [Befehle](commands.md#setup)). Er gibt für jede Änderung `f1-24: changed: ...` aus oder `f1-24: nothing to change`, wenn er schon eingeschaltet ist.

## Wie es funktioniert {#how-it-works}

EA SPORTS F1 23, F1 24 und F1 25: die offizielle UDP-Telemetrie, jedes Auto auf der Strecke.

Die Spiele senden sie selbst (Einstellungen > Telemetrie-Einstellungen, oder
`Documents/My Games/<F1 xx>/hardwaresettings/hardware_settings_config.xml`,
`<udp enabled="true" ip="127.0.0.1" port="20777" sendRate="20" format="2025" ...>`).
Little-endian, gepackt, ein 29-Byte-Header in jedem Paket (derselbe in den Formaten 2023,
2024 und 2025):

```text
uint16 packetFormat, uint8 gameYear, gameMajorVersion, gameMinorVersion,
packetVersion, packetId, uint64 sessionUID, float sessionTime,
uint32 frameIdentifier, overallFrameIdentifier, uint8 playerCarIndex,
secondaryPlayerCarIndex
```

Was gelesen wird, nach Paket-ID:

```text
0 Motion        CarMotionData[22], 60 bytes each: world position x y z
                (metres; Y is up), world velocity, forward and right
                vectors (int16 / 32767), g-forces, yaw pitch roll
1 Session       weather, temperatures, total laps, track length, session
                type, track id, ... network game
2 Lap Data      LapData[22]: last lap time, lap distance, race position,
                current lap number, pit stops, penalties, grid position,
                driver and result status. 50 bytes per car in 2023; 57 in
                2024 and 2025, which added the minutes parts of the deltas
                and the speed trap.
3 Event         a four-letter code and a union of details: SSTA SEND FTLP
                RTMT DRSE DRSD TMPT CHQF RCWN PENA SPTP STLG LGOT DTSV SGSV
                FLBK BUTN RDFL OVTK SCAR COLL
4 Participants  ParticipantData[22]: AI or human, driver, team, race
                number, name (48 bytes in 2023 and 2024, 32 in 2025; 58,
                60 and 57 bytes per car)
6 Car Telemetry CarTelemetryData[22], 60 bytes: speed km/h, throttle,
                steer, brake, clutch, gear, rpm, DRS ...
```

Jedes Paket wird außerdem vollständig und unverändert im Roh-Beiblatt der Session behalten
(`heat.raw.parquet`, `type` der Name des Pakets - `motion`, `car_status` ... -
mit `format`, `packet_id`, `frame` und `session_uid`) - die oben gelesenen und die, die
noch niemand liest: 5 Car Setups, 7 Car Status, 8 Final Classification, 9 Lobby
Info, 10 Car Damage, 11 Session History, 12 Tyre Sets, 13 Motion Ex, 14 Time
Trial, 15 Lap Positions, jede spätere ID und Pakete in einem Format, das dieser Watcher nicht liest. Ein späterer Decoder braucht also nur das Beiblatt.

Die Position jedes Autos steht im Motion-Paket - auch online, wo das Spiel sie selbst herausgibt (nur Kraftstoff, ERS, Schaden und Reifensatz-Daten werden für Spieler zurückgehalten, deren "Deine Telemetrie" eingeschränkt ist). Jedes Auto wird etwa mit 10 Hz unter seinem Fahrernamen aufgezeichnet ("car N", bis die Namen eintreffen), das Team nach Namen, und das Auto des Spielers als `own` markiert.

Quellen: EAs "F1 25 UDP Specification" (forums.ea.com, F1-Games-Infohub), die F1-23- und F1-24-Spezifikationen; dieselben Tabellen gespiegelt in MacManley/f1-25-udp (MIT). Pakete in Tests sind nach diesen Layouts gebaut.

Dasselbe Modul bedient außerdem: [EA SPORTS F1 23 (Live-Daten)](game-f1-23.md), [EA SPORTS F1 25 (Live-Daten)](game-f1-25.md).

## Positionen und Achsen {#positions-and-axes}

| | |
|---|---|
| Positionen aufgezeichnet | ja |
| Oben-Achse | `y` |
| Einheiten | Meter |
| Für den Viewer gespiegelt | keine |
| Einheitenfaktor (`scale`: der Viewer multipliziert Positionen damit) | 1 |

Diese landen in der `meta.json` jeder Session (`axes`) und, wenn die Session Positionen hat, im Footer von `heat.parquet`, damit der 3DHeat-Viewer die Zeilen selbst dreht und skaliert - siehe [Die Daten](the-data.md).

## Mehrspieler {#multiplayer}

- Als online gespielt markiert (`multiplayer`): **ja**. `games --markdown` zeigt das als "erlaubt (liest nur, was das Spiel veröffentlicht)".
- Art `telemetry`: Er liest nur, was das Spiel oder die Plattform herausgibt (ein UDP-Port oder Shared Memory, das das Spiel veröffentlicht), deshalb zeichnet er auch im Online-Spiel auf wie offline; die Markierung entscheidet nur, ob Speicher jemals gelesen werden darf.
- Speicher: **nie** von diesem Adapter gelesen. Nur `memory`-Adapter lesen Speicher, und nie bei einem Spiel, das als online gespielt markiert ist - siehe [Quellen und Regeln](sources-and-rules.md).

## Erfasste Statistiken {#statistics-recorded}

Statistik-Schlüssel, die der Code dieses Adapters namentlich setzt (das `stats` jeder Session in `meta.json` und die Tabelle `stats` in `watcher.sqlite`):

`best_lap`, `collisions`, `distance_km`, `fastest_laps`, `finishes`, `flashbacks`, `grid_position`, `laps`, `overtaken`, `overtakes`, `penalties`, `penalty_seconds`, `pit_stops`, `race_position`, `sessions`, `top_speed_kmh`, `wins`

Ein Schlüssel in geschweiften Klammern wird zur Laufzeit vervollständigt (`score.{team}` ist ein Schlüssel pro Team). Schlüssel, die der Code aus einer Tabelle der Spielfelder oder aus den eigenen Statistiknamen des Spiels übernimmt, stehen nicht in dieser Liste; "Was aufgezeichnet wird" oben nennt sie.

## Vollständigkeit {#completeness}

Der Watcher folgt der [Konverterregel](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md) von 3DHeat: Was die Quelle enthält, wird gelesen oder behalten, nie weggelassen. Neben den Zeilen wird jedes Paket, jede Seite, jede Zeile oder Antwort, die der Adapter erhält, vollständig in der `heat.raw.parquet` der Session behalten (Spalten `time`, `ms`, `type`, `used`, `payload`, `text`, dann jedes nach Namen behaltene Feld; `used` markiert, was auch zu Zeilen wurde), und `selfCheck.completeness` in der `meta.json` zählt jeden `type` - `lost` ist 0.

**Gelesen**

- 0 Motion: Weltposition und Geschwindigkeit jedes Autos, und jetzt auch Gier, Nick, Rollen (Grad, aus den Radiant der Spezifikation) und die seitliche, längs und vertikale g-Kraft, bei jeder Positionszeile des Autos
- 1 Session: Strecke, Sessiontyp, Rundenzahl, Streckenlänge, online oder nicht (meta.json `sessions`)
- 2 Lap Data: letzte Rundenzeit, Rundennummer, Renn- und Startplatz, Boxenstopps, Strafen, Ergebnisstatus (Runden, Zielankünfte, Ausfälle, Statistiken)
- 3 Event: jeder Code außer BUTN als eigene Zeile, mit seinen Details
- 4 Participants: Fahrernamen, Teams, Anzahl aktiver Autos (`player` und `team` der Zeilen, meta.json `drivers`)
- 6 Car Telemetry: Geschwindigkeit, Gang, Gas, Bremse, und jetzt auch Lenkung (-1..1), Drehzahl und DRS, bei jeder Positionszeile des Autos
- geprüft gegen EAs veröffentlichte UDP-Spezifikationen für die Formate 2023, 2024 und 2025 (Paketgrößen in den Tests geprüft); noch nicht am Spiel

**Roh behalten**

- jedes Paket vollständig in `heat.raw.parquet`, `payload` das Datagramm, `type` der Name seiner ID: `motion`, `session`, `lap_data`, `event`, `participants`, `car_setups`, `car_telemetry`, `car_status`, `final_classification`, `lobby_info`, `car_damage`, `session_history`, `tyre_sets`, `motion_ex`, `time_trial`, `lap_positions` (`packet <n>` für eine ID, die die Spezifikationen noch nicht aufführen); Spalten `format` (2023/2024/2025), `packet_id`, `frame`, `session_uid`
- `used` ist wahr für die oben gelesenen Pakete (Motion, Session, Lap Data, Participants, Car Telemetry und Event-Codes außer BUTN); der Rest - Autoeinstellungen, Autostatus (Kraftstoff, ERS, Reifenmischung und -alter, Flags), Endergebnis, Lobby, Schaden am Auto, Sitzungsverlauf (jede Runden- und Sektorzeit je Auto), Reifensätze, motion ex (Federung des eigenen Autos, Radgeschwindigkeiten, lokale Geschwindigkeit, Winkelgeschwindigkeit und Beschleunigung), Zeitfahren, Rundenpositionen, BUTN-Tastenereignisse - wird für einen späteren Decoder behalten
- `format <year>`: ein Paket in einem Format vor 2023 (anderes Header-Layout), vollständig; `short`: ein Datagramm kürzer als der 29-Byte-Header, vollständig

**Nicht verfügbar**

- Kraftstoff, ERS, Schaden und Reifensätze anderer Spieler online, wenn deren "Deine Telemetrie" eingeschränkt ist: das Spiel sendet für sie Nullen
- Pakete, die gesendet werden, während der Watcher nicht läuft, oder während ein anderes Programm Port 20777 belegt: UDP wird vom Spiel nicht gespeichert

**Größe**: bei einer Sendefrequenz von 60 Hz ist jedes Paket etwa 0,38 MB/s groß (Motion, Lap Data, Car Telemetry, Car Status und Motion Ex mit 60 Hz, Session History und Tyre Sets mit 20/s, Car Damage mit 10/s, Session und Car Setups mit 2/s) plus etwa 0,03 MB/s an Elementköpfen: etwa 1,5 GB pro Stunde Fahrt vor der Komprimierung, etwa 0,55 GB bei der Standardrate von 20 Hz; zstd bringt es auf einen Bruchteil davon (leere Auto-Plätze und wiederholte Werte komprimieren gut; an einer echten Session noch nicht gemessen)

## Geprüft {#verified}

mit Paketen in den Formaten 2023, 2024 und 2025 getestet, die aus EAs veröffentlichter Spezifikation gebaut und über UDP gesendet wurden; am Spiel ungetestet

## Quelle {#source}

[heat3d_watch/adapters/f1.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/f1.py)

<!-- Generated from the adapter by tools/gen_game_pages.py; change the adapter and run it again rather than editing this page. -->
