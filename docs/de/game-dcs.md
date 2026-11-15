---
title: "DCS World (Live-Daten)"
nav_order: 10
lang: "de"
source: game-dcs.md
source_hash: "87cba160674e"
nav_exclude: true
search_exclude: true
---
# DCS World (Live-Daten) {#dcs-world-live-data}

Während du DCS World spielst, speichert der Watcher die Daten, die das Spiel selbst herausgibt, damit du sie dir später auf einer Karte im 3DHeat-Viewer ansehen kannst.

*Technische Details: Adapter `dcs`, Art [`telemetry`](sources-and-rules.md); er läuft, solange `DCS.exe` läuft, und sucht alle 0,1 s nach neuen Daten.*

## Was aufgezeichnet wird {#what-is-recorded}

- eigene Position mit 10 Hz als Meter nach Osten, oben und Norden vom Ursprung des Schauplatzes (aus Breiten-/Längengrad und Höhe); lat/lon/alt und DCS' eigene Weltmeter (dcs_x Norden, dcs_y oben, dcs_z Osten) als Spalten
- Fluglage, angezeigte und wahre Geschwindigkeit, Mach, Vertikalgeschwindigkeit, Anstellwinkel und Schiebewinkel, magnetischer Kurs, AGL und Radarhöhe, g auf drei Achsen, Geschwindigkeit und Drehraten, in der Luft, die Position der Kamera und ihr Vorwärtsvektor, Flugzeugtyp
- Starts und Landungen mit dem Flugplatz; Abstürze, Schleudersitz-Auslösungen, Pilotentode
- Abschüsse und Abgeschossenwerden mit beiden Einheitentypen und der Waffe; andere Spielereignisse, wie sie gegeben sind
- Leben pro Mission (spawn ... session_end), Abschüsse, Tode, Strecke, höchste Höhe, höchstes g
- jede Zeile, die der Hook sendet, vollständig in heat.raw.parquet behalten, dazu ein Sekundenauszug der Export-Tabellen des Flugzeugs (Triebwerke, Fahrwerk und Klappen, Nutzlast, Gegenmaßnahmen, Route, Navigation) und jeder andere Callback (Pause, Chat, Spieler, die beitreten, Laden der Mission)

## Woher es kommt {#where-it-comes-from}

der Hook des Watchers %USERPROFILE%\Saved Games\DCS\*\Scripts\Hooks\heat3d-watch.lua, UDP-Zeilen an 127.0.0.1:41993

## So schaltest du es ein {#how-to-switch-it-on}

python -m heat3d_watch setup dcs --apply (legt Scripts\Hooks\heat3d-watch.lua an), dann DCS neu starten

Gib den Befehl in einem Terminal ein, das im Ordner des Watchers geöffnet ist (siehe [Vor dem Start](before-you-start.md)). Wenn er fehlschlägt, sagt die letzte Zeile, warum; [Installation und Start](installing-and-running.md) beschreibt die üblichen Ursachen.

`python -m heat3d_watch setup dcs` listet die Dateien auf, die er ändern würde; `python -m heat3d_watch setup dcs --apply` ändert sie und hebt das Original als `<file>.heat3d-backup` auf (siehe [Befehle](commands.md#setup)). Er gibt für jede Änderung `dcs: changed: ...` aus oder `dcs: nothing to change`, wenn er schon eingeschaltet ist.

## Wie es funktioniert {#how-it-works}

DCS World: ein kleines Hook-Skript des Watchers selbst, das UDP-Zeilen an 127.0.0.1:41993 sendet.

DCS führt beim Start Lua-Dateien in `Saved Games\DCS*\Scripts\Hooks\` aus; ein Hook kann die Export-Funktionen (`Export.Lo*`) lesen und die Callbacks der Simulation empfangen (`DCS.setUserCallbacks`: onSimulationStart/Frame/Stop, onGameEvent) - siehe `<DCS>\API\DCS_ControlAPI.html` und <https://wiki.hoggitworld.com/view/DCS_Export_Script>. `setup` schreibt `heat3d-watch.lua` dorthin (eine eigene Datei: Export.lua und die Hooks anderer Tools bleiben unberührt). Sie sendet zehn Zeilen pro Sekunde, eine weitere pro Sekunde und eine pro Spielereignis oder Callback, ohne je auf eine Antwort zu warten. Der Port ist 41993, damit der Hook von JoyPro (41992) und Tacview (42674) daneben weiter funktioniert. Die Zeilen (Felder durch ';' getrennt):

```text
hello;v=2                                       the hook was loaded
start;mission=..;map=..;me=<player id>;name=..;mp=0|1;file=..;server=0|1
mis;t=..;date.Day=..;start_time=..;weather...   the mission's date, start time and weather, flattened
p;t=<model s>;x=;y=;z=;lat=;lon=;alt=;hdg=;pitch=;bank=;ias=;agl=;g=;type=;tas=;mach=;vv=;aoa=;aos=;
  mhdg=;ralt=;gx=;gz=;vx=;vy=;vz=;wx=;wy=;wz=;air=;cx=;cy=;cz=;cfx=;cfy=;cfz=
d;t=..;self.Name=..;eng.RPM.left=..;mech.gear.value=..;pay.Stations.1.count=..;...   once a second
ev;t=..;name=<onGameEvent name>;args=a|b|c      every onGameEvent
cb;t=..;name=<callback>;args=a|b                every other callback (pause, chat, players, loading)
noexport;t=..                                   the server forbids ownship export
stop;t=..                                       the mission ended
```

`p` ist LoGetSelfData: Position x/y/z - DCS' eigene Weltmeter, x Norden, y oben, z Osten - plus LatLongAlt (Grad, m), Heading/Pitch/Bank (Radiant), mit LoGetIndicatedAirSpeed (m/s), LoGetAltitudeAboveGroundLevel (m) und LoGetAccelerationUnits() x/y/z (g); und, wie `Scripts\Export.lua` sie dokumentiert, LoGetTrueAirSpeed (m/s), LoGetMachNumber, LoGetVerticalVelocity (m/s), LoGetAngleOfAttack und LoGetAngleOfSideSlip (rad), LoGetMagneticYaw (rad), LoGetRadarAltimeter (m), LoGetVectorVelocity (Welt-m/s), LoGetAngularVelocity (rad/s), LoGetInAir sowie der Punkt und der Vorwärtsvektor von LoGetCameraPosition (Weltmeter). `d` ist ein Sekundenauszug ganzer Tabellen, in Schlüssel mit Punkten abgeflacht: LoGetSelfData (Land, Koalition, Einheiten- und Gruppennamen, Typstufen, Flags), LoGetEngineInfo, LoGetMechInfo, LoGetPayloadInfo, LoGetSnares, LoGetWingInfo, LoGetVectorWindVelocity, LoGetFMData, LoGetNavigationInfo, LoGetRoute, LoGetMCPState, LoGetControlPanel_HSI, LoGetRadioBeaconsStatus und einige Zahlen (Pause, Zeitbeschleunigung, Sitz, Druck, Abweichungen). Der Watcher behält jede Zeile vollständig im Roh-Beiblatt; `p` wird außerdem zu den Zeilen.

Positionen landen in derselben flachen Karte wie die der anderen Flugsimulatoren (`Tangent`: x Osten, y Höhe über dem Meeresspiegel, z Norden, Meter), aus LatLongAlt, um den festen Ursprung des Schauplatzes (`THEATRES`, aus der `map` der Startzeile). So teilt sich jede Mission auf einem Schauplatz eine Karte, unter die der Viewer die echte Welt legen kann. Ein Schauplatz, der nicht in der Tabelle steht, nimmt Breite und Länge des ersten Fixes, auf ganze Grad gerundet. DCS' eigene x/y/z werden als `dcs_x`, `dcs_y`, `dcs_z` behalten; ein Fix ohne LatLongAlt kann nicht platziert werden und wird nur gezählt (`fixes_without_latlon`). Der Ursprung ist `geo` der Session, in meta.json und im Footer der Tabelle.

Die Argumente von onGameEvent, wie DCS_ControlAPI sie liefert: takeoff/landing (playerID, unit_missionID, airdromeName), crash/eject/pilot_death (playerID, unit_missionID), kill (killerPlayerID, killerUnitType, killerSide, victimPlayerID, victimUnitType, victimSide, weaponName), self_kill (playerID), change_slot (playerID, slotID, prevSide), mission_end (winner, msg).

Ein Mehrspieler-Server kann das Exportieren der eigenen Flugzeugdaten verbieten (LoIsOwnshipExportAllowed ist false); dann gibt es keine Positionen, nur Ereignisse, und die Session sagt das.

## Positionen und Achsen {#positions-and-axes}

| | |
|---|---|
| Positionen aufgezeichnet | ja |
| Oben-Achse | `y` |
| Einheiten | Meter (Osten, Höhe, Norden vom Ursprung des Schauplatzes) |
| Für den Viewer gespiegelt | `z` |
| Einheitenfaktor (`scale`: der Viewer multipliziert Positionen damit) | 1 |

Diese landen in der `meta.json` jeder Session (`axes`) und, wenn die Session Positionen hat, im Footer von `heat.parquet`, damit der 3DHeat-Viewer die Zeilen selbst dreht und skaliert - siehe [Die Daten](the-data.md).

## Mehrspieler {#multiplayer}

- Als online gespielt markiert (`multiplayer`): **ja**. `games --markdown` zeigt das als "erlaubt (liest nur, was das Spiel veröffentlicht)".
- Art `telemetry`: Er liest nur, was das Spiel oder die Plattform herausgibt (ein UDP-Port oder Shared Memory, das das Spiel veröffentlicht), deshalb zeichnet er auch im Online-Spiel auf wie offline; die Markierung entscheidet nur, ob Speicher jemals gelesen werden darf.
- Speicher: **nie** von diesem Adapter gelesen. Nur `memory`-Adapter lesen Speicher, und nie bei einem Spiel, das als online gespielt markiert ist - siehe [Quellen und Regeln](sources-and-rules.md).

## Erfasste Statistiken {#statistics-recorded}

Statistik-Schlüssel, die der Code dieses Adapters namentlich setzt (das `stats` jeder Session in `meta.json` und die Tabelle `stats` in `watcher.sqlite`):

`airborne_time`, `bad_packets`, `crashes`, `deaths`, `distance_km`, `ejections`, `export_blocked`, `fixes_without_latlon`, `flight_time`, `kills`, `max_altitude_m`, `max_g`, `shot_down`, `{event}s`

Ein Schlüssel in geschweiften Klammern wird zur Laufzeit vervollständigt (`score.{team}` ist ein Schlüssel pro Team). Schlüssel, die der Code aus einer Tabelle der Spielfelder oder aus den eigenen Statistiknamen des Spiels übernimmt, stehen nicht in dieser Liste; "Was aufgezeichnet wird" oben nennt sie.

## Vollständigkeit {#completeness}

Der Watcher folgt der [Konverterregel](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md) von 3DHeat: Was die Quelle enthält, wird gelesen oder behalten, nie weggelassen. Neben den Zeilen wird jedes Paket, jede Seite, jede Zeile oder Antwort, die der Adapter erhält, vollständig in der `heat.raw.parquet` der Session behalten (Spalten `time`, `ms`, `type`, `used`, `payload`, `text`, dann jedes nach Namen behaltene Feld; `used` markiert, was auch zu Zeilen wurde), und `selfCheck.completeness` in der `meta.json` zählt jeden `type` - `lost` ist 0.

**Gelesen**

- `p` (10 Hz): Position, LatLongAlt, Fluglage, IAS, AGL, g (x/y/z), Flugzeugtyp, und vom Hook 2 TAS, Mach, Vertikalgeschwindigkeit, AoA, Schiebewinkel, magnetischer Kurs, Radarhöhe, Weltgeschwindigkeit, Drehraten, in-air sowie Kamerapunkt und Vorwärtsvektor - alle als Spalten der Zeilen (Einheiten wie Export.lua sie angibt)
- `start`: Mission, Schauplatz, eigene Spieler-ID und Name, Mehrspieler, Missionsdatei, Server; `mis`: Datum und Startzeit der Mission in meta.json
- `ev`: jedes onGameEvent als Zeile (takeoff, landing, crash, eject, pilot_death, kill, self_kill, change_slot, connect, disconnect, friendly_fire, mission_end, jeder andere Name wie gegeben)
- `noexport` und `stop` als Zeilen und in meta.json

**Roh behalten**

- jede Zeile, die der Hook sendet, vollständig, als `text` unter ihrer Art: `hello`, `start`, `mis`, `p`, `d`, `ev`, `cb`, `noexport`, `stop`; eine Zeile jeder anderen Art unter `unknown`
- `d` (1 Hz, nur roh): LoGetSelfData vollständig (Land, Koalition, Einheiten- und Gruppenname, Typstufen, Flags), LoGetEngineInfo, LoGetMechInfo, LoGetPayloadInfo, LoGetSnares, LoGetWingInfo, Windvektor, LoGetFMData, LoGetNavigationInfo, LoGetRoute, LoGetMCPState, HSI, Funkfeuer, Pause, Zeitbeschleunigung, Sitz, Druck, Abweichungen - in Schlüssel mit Punkten abgeflacht
- `mis`: die Wettertabelle der Mission, abgeflacht; `cb`: onSimulationPause/Resume, onMissionLoad\*, onNet\*, onPlayerConnect/Disconnect/Start/Stop/ChangeSlot, onChatMessage, onTriggerMessage, onRadioMessage, onRadioCommand, onShowMessage mit ihren Argumenten

**Nicht verfügbar**

- andere Einheiten (LoGetWorldObjects, LoGetObjectById) und Sensordaten (LoGetTargetInformation, LoGetLockedTargetInformation, LoGetTWSInfo, LoGetWingTargets, LoGetSightingSystemInfo): nicht angefragt - jedes Objekt einer Mission mit 10 Hz ist im eigenen Takt von DCS teuer, und ein Server sperrt sie (allow_object_export, allow_sensor_export); Tacview zeichnet sie auf
- die ganze Missionstabelle (DCS.getCurrentMission enthält jede Einheit und jeden Trigger, Megabytes): nur ihr Datum, ihre Startzeit, das Wetter, der Einsatz, der Schauplatz und die Version werden gesendet
- die onPlayerTry\*-Callbacks: sie antworten DCS (erlauben oder verweigern), deshalb lässt der Hook sie in Ruhe
- Adressen und UCIDs anderer Spieler: net.get_player_info gibt sie nur an einen Server, und sie gehören nicht dem Spieler zum Behalten
- Einträge einer Tabelle über 800 Schlüssel oder 6 Ebenen Tiefe in einer `d`-Zeile werden abgeschnitten, damit eine Zeile ein Datagramm bleibt

**Größe**: etwa 20 MB pro Stunde an `p`-Zeilen (10 pro Sekunde, etwa 500 Bytes je mit Rahmen) und 15-40 MB an `d`-Auszügen (einer pro Sekunde, 4-10 KB je nach Nutzlast und Route des Flugzeugs), vor zstd; die wiederholten Schlüssel komprimieren etwa zehnfach

## Geprüft {#verified}

Zeilenformat mit synthetischen Datagrammen getestet; der Lua-Hook ist in DCS ungetestet (nach der DCS-Hook- und Export-API und der Liste der Lo\*-Funktionen aus Scripts\Export.lua geschrieben, nicht ausgeführt)

## Quelle {#source}

[heat3d_watch/adapters/dcs.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/dcs.py)

<!-- Generated from the adapter by tools/gen_game_pages.py; change the adapter and run it again rather than editing this page. -->
