---
title: "Microsoft Flight Simulator 2020 (Live-Daten)"
nav_order: 31
lang: de
source: game-msfs2020.md
source_hash: "9b9e8389114b"
nav_exclude: true
search_exclude: true
---
# Microsoft Flight Simulator 2020 (Live-Daten) {#microsoft-flight-simulator-2020-live-data}

Während du Microsoft Flight Simulator 2020 spielst, speichert der Watcher die Daten, die das Spiel selbst herausgibt, damit du sie dir später auf einer Karte im 3DHeat-Viewer ansehen kannst.

*Technische Details: Adapter `msfs2020`, Art [`telemetry`](sources-and-rules.md); er läuft, solange `FlightSimulator.exe` läuft, und sucht alle 0,1 s nach neuen Daten.*

## Was aufgezeichnet wird {#what-is-recorded}

- Position des eigenen Flugzeugs bei jedem Simulationsframe, mit 10 Hz abgetastet (Breiten-/Längengrad/Höhe als Meter nach Osten, oben und Norden vom ersten Fix; lat/lon/alt als Spalten behalten)
- Fluglage, angezeigte Fahrt, Bodengeschwindigkeit, AGL, g, am Boden; wahre Geschwindigkeit, Mach, Vertikalgeschwindigkeit, AoA, Schiebewinkel, magnetischer Kurs, Körpergeschwindigkeiten, Beschleunigungen und Drehraten mit etwa 10 Hz
- Gewicht, Treibstoff, Klappen, Fahrwerk, Spoiler, Feststellbremse, Autopilot, Gas, Drehzahl, Wetter, Simulationsrate, Zeit und Kamerazustand einmal pro Sekunde; Titel des Flugzeugs und ATC-Typ, Modell und ID
- Starts, Landungen, Abstürze, begonnene und beendete Flüge (session_start/session_end)
- Flugzeit, Zeit in der Luft, Strecke, höchste Höhe, höchstes g, Landungen
- jede SimConnect-Nachricht vollständig in heat.raw.parquet

## Woher es kommt {#where-it-comes-from}

SimConnect über die eigene SimConnect.dll des Spielers (der Simulator-Ordner oder %MSFS_SDK%\SimConnect SDK\lib)

## So schaltest du es ein {#how-to-switch-it-on}

nichts; SimConnect.dll kommt mit MSFS 2020 (oder dem MSFS-SDK)

## Wie es funktioniert {#how-it-works}

Microsoft Flight Simulator 2020 und 2024: SimConnect, über die eigene SimConnect.dll des Spielers.

SimConnect ist die veröffentlichte Client-API des Simulators (SDK-Dokumentation:
<https://docs.flightsimulator.com/html/Programming_Tools/SimConnect/SimConnect_SDK.htm>,
<https://docs.flightsimulator.com/msfs2024/html/6_Programming_APIs/SimConnect/SimConnect_SDK.htm>).
Der Watcher liefert die DLL nicht mit: Er lädt die, die mit dem Simulator oder seinem SDK kam - MSFS 2020 legt `SimConnect.dll` in seinen Installationsordner; MSFS 2024 enthält auf Steam nur seine interne Version, deshalb installieren Spieler von 2024 das MSFS-2024-SDK
(`<SDK>\SimConnect SDK\lib\SimConnect.dll`; der Simulator 2024 nimmt auch 2020-Clients an).

Die Aufrufe aus SimConnect.h, alle geben einen HRESULT zurück (0 = S_OK):

```text
SimConnect_Open(HANDLE*, LPCSTR name, HWND, DWORD, HANDLE, DWORD config)
SimConnect_AddToDataDefinition(HANDLE, DWORD define, LPCSTR var, LPCSTR units,
                               SIMCONNECT_DATATYPE (FLOAT64 = 4), float epsilon, DWORD datum)
SimConnect_RequestDataOnSimObject(HANDLE, DWORD request, DWORD define, DWORD object (0 = user),
                                  SIMCONNECT_PERIOD (SIM_FRAME = 3), DWORD flags, DWORD origin,
                                  DWORD interval, DWORD limit)
SimConnect_SubscribeToSystemEvent(HANDLE, DWORD event, LPCSTR name)
SimConnect_GetNextDispatch(HANDLE, SIMCONNECT_RECV**, DWORD*)   E_FAIL when nothing waits
SimConnect_Close(HANDLE)
```

Jede Nachricht beginnt mit SIMCONNECT_RECV {DWORD dwSize, dwVersion, dwID}
(#pragma pack 1). Die hier gelesenen:

```text
1  EXCEPTION       dwException, dwSendID, dwIndex
2  OPEN            szApplicationName[256], then version DWORDs
3  QUIT            the sim is closing
4  EVENT           uGroupID, uEventID, dwData
6  EVENT_FILENAME  EVENT + szFileName[260], dwFlags        (FlightLoaded)
8  SIMOBJECT_DATA  dwRequestID, dwObjectID, dwDefineID, dwFlags, dwentrynumber,
                   dwoutof, dwDefineCount, then the values (FLOAT64 each here)
```

Simulationsvariablen (die Einheiten sind so angefragt, dass keine Umrechnung nötig ist): PLANE
LATITUDE/LONGITUDE (Grad), PLANE ALTITUDE (Meter, über dem Meeresspiegel), PLANE
ALT ABOVE GROUND (Meter), PLANE PITCH/BANK DEGREES und PLANE HEADING DEGREES
TRUE (Grad; SimConnects eigene Vorzeichen - Nase oben ist negativer Nick), AIRSPEED
INDICATED und GROUND VELOCITY (Knoten), G FORCE (gforce), SIM ON GROUND (bool).
Systemereignisse: SimStart, SimStop, Crashed, FlightLoaded, AircraftLoaded,
Pause, CrashReset, PositionChanged, FlightSaved, Sim.

Drei weitere Datendefinitionen fragen den Rest des Flugs ab (`MOTION_VARS`,
jeden sechsten Simulationsframe), den langsameren Zustand des Flugzeugs (`STATE_VARS`, einmal
pro Sekunde) und seine Namen (`NAME_VARS`, 256-Byte-Zeichenketten, wenn sie sich ändern); jede
ist eine eigene Definition, sodass eine Variable, die eine Simulatorversion nicht kennt, nur
diesen Block kostet. Jede Nachricht wird vollständig im Roh-Beiblatt der Session behalten.

Positionen landen in derselben flachen Karte wie die von X-Plane (x Osten, y Höhe, z Norden,
in Metern vom ersten Fix der Sitzung); dieser Fix ist `geo` der Session, in meta.json und im Footer der Tabelle.

Dasselbe Modul bedient außerdem: [Microsoft Flight Simulator 2024 (Live-Daten)](game-msfs2024.md).

## Positionen und Achsen {#positions-and-axes}

| | |
|---|---|
| Positionen aufgezeichnet | ja |
| Oben-Achse | `y` |
| Einheiten | Meter (Osten, Höhe, Norden vom ersten Fix) |
| Für den Viewer gespiegelt | `z` |
| Einheitenfaktor (`scale`: der Viewer multipliziert Positionen damit) | 1 |

Diese landen in der `meta.json` jeder Session (`axes`) und, wenn die Session Positionen hat, im Footer von `heat.parquet`, damit der 3DHeat-Viewer die Zeilen selbst dreht und skaliert - siehe [Die Daten](the-data.md).

## Mehrspieler {#multiplayer}

- Als online gespielt markiert (`multiplayer`): **ja**. `games --markdown` zeigt das als "erlaubt (liest nur, was das Spiel veröffentlicht)".
- Art `telemetry`: Er liest nur, was das Spiel oder die Plattform herausgibt (ein UDP-Port oder Shared Memory, das das Spiel veröffentlicht), deshalb zeichnet er auch im Online-Spiel auf wie offline; die Markierung entscheidet nur, ob Speicher jemals gelesen werden darf.
- Speicher: **nie** von diesem Adapter gelesen. Nur `memory`-Adapter lesen Speicher, und nie bei einem Spiel, das als online gespielt markiert ist - siehe [Quellen und Regeln](sources-and-rules.md).

## Erfasste Statistiken {#statistics-recorded}

Statistik-Schlüssel, die der Code dieses Adapters namentlich setzt (das `stats` jeder Session in `meta.json` und die Tabelle `stats` in `watcher.sqlite`):

`airborne_time`, `bad_packets`, `crashes`, `distance_km`, `flight_time`, `max_altitude_m`, `max_g`, `{event}s`

Ein Schlüssel in geschweiften Klammern wird zur Laufzeit vervollständigt (`score.{team}` ist ein Schlüssel pro Team). Schlüssel, die der Code aus einer Tabelle der Spielfelder oder aus den eigenen Statistiknamen des Spiels übernimmt, stehen nicht in dieser Liste; "Was aufgezeichnet wird" oben nennt sie.

## Vollständigkeit {#completeness}

Der Watcher folgt der [Konverterregel](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md) von 3DHeat: Was die Quelle enthält, wird gelesen oder behalten, nie weggelassen. Neben den Zeilen wird jedes Paket, jede Seite, jede Zeile oder Antwort, die der Adapter erhält, vollständig in der `heat.raw.parquet` der Session behalten (Spalten `time`, `ms`, `type`, `used`, `payload`, `text`, dann jedes nach Namen behaltene Feld; `used` markiert, was auch zu Zeilen wurde), und `selfCheck.completeness` in der `meta.json` zählt jeden `type` - `lost` ist 0.

**Gelesen**

- SIMOBJECT_DATA der Positionsdefinition (jeder Simulationsframe): Breite, Länge, Höhe, AGL, Nick, Querneigung, wahrer Kurs, IAS, Bodengeschwindigkeit, g, am Boden - der letzte Frame der Abfrage als Zeile, jeder Frame für Aufsetzer und Starts
- SIMOBJECT_DATA der Bewegungsdefinition (etwa 10 Hz: TAS, Mach, Vertikalgeschwindigkeit, AoA, Schiebewinkel, magnetischer Kurs, Körpergeschwindigkeit, Beschleunigung und Drehrate auf drei Achsen) und der Zustandsdefinition (1 Hz: Gewichte, Treibstoff, Klappen, Fahrwerk, Spoiler, Feststellbremse, Autopilot, Triebwerke, Gas und Drehzahl, Außentemperatur, Wind, Luftdruck auf Meereshöhe, Simulationsrate, Zulu- und Ortszeit, Kamerazustand) als Zeilen, wie zuletzt erhalten
- SIMOBJECT_DATA der Namensdefinition (Titel, ATC-Typ, Modell und ID) in meta.json und als `aircraft` der Zeilen; OPEN (Anwendung und Version) in meta.json
- EVENT und EVENT_FILENAME: SimStart, SimStop, Crashed, FlightLoaded (die Flugdatei) und AircraftLoaded (die Flugzeugdatei) als Flüge, Abstürze und meta.json
- QUIT beendet die Session

**Roh behalten**

- jede Nachricht, die SimConnect dem Watcher übergibt, vollständig als `payload`, unter ihrem SIMCONNECT_RECV_ID-Namen: `SIMOBJECT_DATA`, `EVENT`, `EVENT_FILENAME`, `OPEN`, `QUIT`, `EXCEPTION` (eine Variable oder ein Ereignis, das der Simulator nicht angenommen hat, mit Sendungs-ID und Index), jede andere ID nach Namen oder `RECV_<id>`
- was nur das Roh-Beiblatt enthält: jeder Simulationsframe der Position zwischen den Zeilen, die Ereignisse Pause, Sim, CrashReset, PositionChanged und FlightSaved, eine Definition, die der Simulator abgebrochen hat (eine Variable, die er nicht kannte: der Block wird dann nicht nach Namen gelesen); `requests` in meta.json listet jede Definition mit ihren Variablen und Einheiten in der Reihenfolge, sodass die Nutzdaten auch ohne dieses Modul lesbar sind

**Nicht verfügbar**

- andere Flugzeuge (KI-Verkehr, andere Spieler online): SimConnect_RequestDataOnSimObjectType würde jedes Flugzeug in einem Radius abfragen - mehr Last für den Simulator und fremde Flüge
- der Bewegungsblock bei jedem Simulationsframe: er wird jeden sechsten Frame angefragt (etwa 10 Hz, die Rate der Zeilen), was den Rohstrom auf etwa ein Fünftel hält; der Positionsblock bleibt bei jedem Frame
- die tausenden anderen Simulationsvariablen (Funkgeräte, Lichter, jede Triebwerksanzeige, Defekte): eine Definition enthält, was sie anfragt; die Listen fragen den Flug, den Zustand des Flugzeugs und die Zeit des Simulators ab
- Wetterbeobachtungen, Einrichtungen (Flughäfen, VORs), Clientdaten von Erweiterungen: eigene Abfragen, nicht gemacht

**Größe**: etwa 30-55 MB pro Stunde vor zstd: der Positionsblock bei jedem Simulationsframe (etwa 200 Bytes mit seinem Rahmen, 30-60 pro Sekunde), der Bewegungsblock mit etwa 10 Hz (etwa 240 Bytes), der Zustandsblock einmal pro Sekunde; zstd verkleinert die Doubles mehrfach

## Geprüft {#verified}

Nachrichtendekodierung mit Puffern getestet, die aus den Layouts von SimConnect.h gebaut wurden; die live SimConnect-Verbindung ist ungetestet

## Quelle {#source}

[heat3d_watch/adapters/msfs.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/msfs.py)

<!-- Generated from the adapter by tools/gen_game_pages.py; change the adapter and run it again rather than editing this page. -->
