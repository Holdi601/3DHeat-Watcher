---
title: "Star Citizen (Logdateien)"
nav_order: 42
lang: de
source: game-starcitizen.md
source_hash: "6528f948d2e5"
nav_exclude: true
search_exclude: true
---
# Star Citizen (Logdateien) {#star-citizen-log-files}

Während du Star Citizen spielst, liest der Watcher die Dateien, die das Spiel schreibt, und speichert, was passiert ist. So kannst du es später als Statistik und Zeitleiste ansehen.

*Technische Details: Adapter `starcitizen`, Art [`log`](sources-and-rules.md); er läuft, solange `StarCitizen.exe` läuft, und sucht alle 0,5 s nach neuen Daten.*

## Was aufgezeichnet wird {#what-is-recorded}

- Tode mit Opfer, Killer, Waffe, Schadensart und Zone (Spieler und NPCs)
- deaktivierte und zerstörte Fahrzeuge, mit Fahrer, Ursache und Zone
- Ziele von Quantensprüngen, Wechsel des Sonnensystems, Spawns, Wiederbelebungen, Handlungsunfähigkeit
- jede Zeile der Game.log, vollständig in heat.raw.parquet
- Abschüsse (Spieler und NPC), Tode, Selbstmorde, zerstörte und verlorene Fahrzeuge, Quantensprünge

## Woher die Daten kommen {#where-it-comes-from}

&lt;Installation>\StarCitizen\LIVE\Game.log (der Build-Ordner der laufenden StarCitizen.exe), nur die Protokolldatei, die das Spiel schreibt – ein Spiel mit Easy Anti-Cheat: Nichts fasst seinen Prozess an

## So schaltest du es ein {#how-to-switch-it-on}

Du musst nichts einschalten: Der Watcher liest die Quelle so, wie das Spiel oder die Plattform sie bereitstellt.

## So funktioniert es {#how-it-works}

Star Citizen: das eigene Protokoll des Clients, `<Installation>\StarCitizen\LIVE\Game.log`.

Das Spiel schreibt Game.log bei jedem Start neu (die vorige wandert nach `logbackups\`). Nur diese Datei wird gelesen: Star Citizen läuft mit Easy Anti-Cheat, und hier wird nichts an den Prozess des Spiels gelassen. Zeilen beginnen mit einem UTC-Zeitstempel und einer Stufe, dann einem Tag in spitzen Klammern:

```text
<2025-04-13T17:17:51.279Z> [Notice] <Actor Death> CActor::Kill: 'Victim' [200146297631] in zone
    'ANVL_Hornet_F7A_Mk2_2677329226210' killed by 'Killer' [202061381370] using
    'GATS_BallisticGatling_S3_2677329225797' [Class unknown] with damage type 'VehicleDestruction'
    from direction x: 0.000000, y: 0.000000, z: 0.000000 [Team_ActorTech][Actor]
<...> [Notice] <Vehicle Destruction> CVehicle::OnAdvanceDestroyLevel: Vehicle 'ANVL_Arrow_123' [123] in zone
    'OOC_Stanton_1_Hurston' [pos x: 1.0, y: 2.0, z: 3.0 vel x: 0, y: 0, z: 0] driven by 'Driver' [456]
    advanced from destroy level 0 to 2 caused by 'Attacker' [789] with 'Combat' [Team_VehicleFeatures][Vehicle]
<...> [Notice] <AccountLoginCharacterStatus_Character> Character: createdAt 1 - updatedAt 2 - geid 3 -
    accountId 4 - name Handle - state STATE_CURRENT [Team_GameServices][Login]
<...> [Notice] <Quantum Navtarget> CSCItemQuantumDrive::RmMulticastOnQTToPoint : Local client user
    Handle[200000000001] received QT data for Entity:AEGS_Gladius_123[123] to Target Stanton1b ...
<...> [Notice] <Changing Solar System> ... Client entity Handle ... changing system from Stanton to Pyro ...
```

(Hier umbrochen; in der Datei steht jede Zeile einzeln.) Die Zone eines Todes ist meist das Schiff, in dem das Opfer saß, nicht ein Ort. Das Format ist von Cloud Imperium nicht dokumentiert und ändert sich zwischen den Patches; die Muster folgen den Zeilen, die Community-Abschusszähler lesen (z. B. <https://github.com/DimmaDont/all-slain>, MIT – nur Fakten), und was nicht passt, wird übersprungen, nicht geraten. Die `pos` eines Fahrzeugs ist zonenbezogen und wird nur als Text gespeichert: Es werden keine Koordinaten gezeichnet.

Jede Zeile wird vollständig in der Roh-Beilage der Session gespeichert (Konverterregel von 3DHeat), ob sie passt oder nicht: `type` ist der Tag der Zeile in spitzen Klammern (`Actor Death`, `Spawn Flow`, ...), sonst ihr erstes Wort in Klammern (`Notice`, `CSessionManager::OnClientSpawned`), sonst `untagged`; eine Zeile ohne Zeitstempel ist `untimed`.

## Positionen und Achsen {#positions-and-axes}

| | |
|---|---|
| Positionen aufgezeichnet | nein |
| Oben-Achse | `y` |
| Einheiten | keine Positionen aufgezeichnet |
| Für den Viewer gespiegelt | keine |
| Einheitenskala (`scale`: der Viewer multipliziert die Positionen damit) | 1 |

Diese Werte landen in der `meta.json` jeder Session (`axes`) und, wenn die Session Positionen hat, im Footer der `heat.parquet`. So dreht und skaliert der 3DHeat-Viewer die Zeilen selbst – siehe [Die Daten](the-data.md).

## Mehrspieler {#multiplayer}

- Als online gespielt markiert (`multiplayer`): **ja**. `games --markdown` zeigt das als „allowed (reads only what the game publishes)“.
- Art `log`: Es liest nur, was das Spiel oder die Plattform herausgibt (Dateien, die das Spiel während des Laufs schreibt). Deshalb zeichnet es auch im Online-Spiel auf, nicht nur offline. Die Markierung entscheidet nur, ob Speicher überhaupt gelesen werden darf.
- Speicher: Dieser Adapter liest **nie** den Speicher. Nur `memory`-Adapter lesen Speicher, und nie bei einem Spiel, das als online gespielt markiert ist – siehe [Quellen und Regeln](sources-and-rules.md).

## Aufgezeichnete Statistiken {#statistics-recorded}

Statistik-Schlüssel, die der Code dieses Adapters beim Namen setzt (das `stats` jeder Session in `meta.json` und die Tabelle `stats` in `watcher.sqlite`):

`bad_lines`, `deaths`, `incapacitations`, `kills`, `npc_kills`, `player_kills`, `quantum_jumps`, `suicides`, `system_jumps`, `vehicles_destroyed`, `vehicles_lost`

Ein Schlüssel in geschweiften Klammern wird zur Laufzeit vervollständigt (`score.{team}` ist ein Schlüssel pro Team). Schlüssel, die der Code aus einer Tabelle der Spielfelder oder aus den eigenen Statistiknamen des Spiels übernimmt, stehen nicht in dieser Liste; „Was aufgezeichnet wird“ oben nennt sie.

## Vollständigkeit {#completeness}

Der Watcher folgt der [Konverterregel](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md) von 3DHeat: Was die Quelle enthält, wird gelesen oder gespeichert, nie weggelassen. Außer den Zeilen wird jedes Paket, jede Seite, jede Zeile und jede Antwort, die der Adapter bekommt, vollständig in der `heat.raw.parquet` der Session gespeichert (Spalten `time`, `ms`, `type`, `used`, `payload`, `text` und alle Felder, die nach Namen behalten werden; `used` markiert, was auch zu Zeilen wurde). `selfCheck.completeness` in `meta.json` zählt jeden `type`; `lost` ist 0.

**Gelesen**

- `<Actor Death>`: Opfer, Killer, Waffe und ihre Klasse, Schadensart, Zone; NPC oder Spieler
- `<Vehicle Destruction>`: Fahrzeug, Zone, zonenbezogene Position als Text, Fahrer, Ursache, Art, Zerstörungsstufe
- `<Quantum Navtarget>`-Ziele, `<Changing Solar System>`, `OnClientSpawned`, Wiederbelebungen im Krankenhaus, Handlungsunfähigkeit mit ihren Ursachen, `EndSession`
- das Handle des Spielers aus `<AccountLoginCharacterStatus_Character>` oder der Anmeldezeile

**Roh gespeichert**

- jede Game.log-Zeile vollständig, `type` = ihr Tag in spitzen Klammern (`Actor Death`, `Vehicle Destruction`, `Spawn Flow`, `Jump Drive State Changed`, `SHUDEvent_OnNotification`, `RequestLocationInventory`, ...), sonst ihr erstes Wort in Klammern (`Notice`, `CSessionManager::OnClientSpawned`, ...), sonst `untagged`; Zeilen ohne Zeitstempel (der Kopf des Logs, umgebrochener Text) als `untimed`; `used`, wo die Zeile zu einer Zeile wurde

**Nicht verfügbar**

- Positionen: Das Protokoll gibt in keinem Format, das sich zeichnen lässt, eine an (die `pos` eines zerstörten Fahrzeugs ist auf eine Zone bezogen, deren Ort nicht protokolliert wird)
- alles aus dem Prozess oder Netzwerk des Spiels: Star Citizen läuft mit Easy Anti-Cheat; nur die Protokolldatei wird gelesen
- Logs früherer Starts (`logbackups`): Die Game.log jedes Starts wird gespeichert, wenn sie gespielt wurde
- Zeilen in einem Format, das ein Patch ändert: roh gespeichert, neu dekodiert, sobald das neue Format bekannt ist

**Größe**: Game.log wächst etwa 5–15 MB pro Stunde Spiel (mehr in belebten Gebieten und bei Fehlern); zstd macht in heat.raw.parquet etwa ein Zehntel daraus

## Geprüft {#verified}

getestet mit synthetischen Game.log-Zeilen im Format, das Community-Tracker dokumentieren; noch nicht gegen das Spiel getestet

## Quelle {#source}

[heat3d_watch/adapters/starcitizen.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/starcitizen.py)

<!-- Aus dem Adapter erzeugt von tools/gen_game_pages.py; ändere den Adapter und führe das Skript erneut aus, statt diese Seite zu bearbeiten. -->
