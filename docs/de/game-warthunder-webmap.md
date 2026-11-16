---
title: "War Thunder (Spielstand)"
nav_order: 46
lang: "de"
source: game-warthunder-webmap.md
source_hash: "34a876e38f09"
nav_exclude: true
search_exclude: true
---
# War Thunder (Spielstand) {#war-thunder-game-state}

Während du War Thunder spielst, speichert der Watcher, was das Spiel an Programme auf deinem eigenen Computer meldet, damit du es dir später auf einer Karte im 3DHeat-Viewer ansehen kannst.

*Technische Details: Adapter `warthunder-webmap`, Art [`gsi`](sources-and-rules.md); er läuft, solange `aces.exe` läuft, und sucht alle 0,5 s nach neuen Daten.*

## Was aufgezeichnet wird {#what-is-recorded}

- eigene Position (Karte Osten/Norden in Metern; Höhe aus /state im Flugzeug, sonst 0), zweimal pro Sekunde, Kurs, Geschwindigkeit
- Spawns und das Verlassen der Karte durch das eigene Fahrzeug (zerstört, gelandet, zurück in den Hangar), je einen Einsatz
- andere Flugzeuge und Bodeneinheiten auf der Minimap als Positionen mit verfolgten IDs und Seite (ohne Höhe)
- Flugplätze, Eroberungszonen und Basen einmal, und Zonen, die die Seite wechseln
- Zeilen des Kill-Feeds und des Schadensfeeds (wer, Fahrzeug, Verb); die Kills und Tode des Spielers, wenn dein Name gesetzt ist (`config --set player_names.warthunder-webmap=<name>`)
- Spawns, Strecke, größte Höhe, größte wahre Geschwindigkeit, Fahrzeug; Kills und Tode, wenn dein Name gesetzt ist
- jede Antwort der Web-Karte vollständig in heat.raw.parquet behalten - das ganze /state und /indicators, der Chat, die Ziele der Schlacht und das Bild der Karte eingeschlossen; zwischen den Schlachten eine eigene Session

## Woher es kommt {#where-it-comes-from}

die lokale Web-Karte des Spiels, <http://127.0.0.1:8111> (/map_info.json, /map_obj.json, /state, /indicators, /hudmsg, /gamechat, /mission.json, /map.img)

## So schaltest du es ein {#how-to-switch-it-on}

Nichts muss eingeschaltet werden: Der Watcher liest die Quelle so, wie das Spiel oder die Plattform sie bereitstellt.

## Wie es funktioniert {#how-it-works}

War Thunder: die lokale Web-Karte des Spiels auf <http://127.0.0.1:8111>.

Das Spiel bietet die Seite an, die ein zweiter Bildschirm oder ein Handy zeigen kann (die "Web-Karte"), und die JSON-Daten dahinter, während es läuft - in jedem Modus, auch im Mehrspielermodus:

```text
/map_info.json   {"map_min": [x, y], "map_max": [x, y], "grid_steps", "grid_zero", "map_generation",
                  "hud_type", "valid"}: the map's extent in metres; valid false in the hangar
/map_obj.json    [{"type": aircraft|ground_model|airfield|capture_zone|bombing_point|defending_point|
                  respawn_base_*|..., "icon": Player|Fighter|Bomber|Mediumtank|SPAA|..., "color": "#rrggbb",
                  "x", "y" (0..1 of the map picture, y down), "dx", "dy" (direction),
                  airfields "sx", "sy", "ex", "ey"}]: what the minimap shows, the player's own
                  vehicle with icon "Player"; no ids, no heights
/state           {"valid", "H, m", "TAS, km/h", "IAS, km/h", "M", "Vy, m/s", ...}: flight values,
                  valid only in an aircraft
/indicators      {"valid", "army": air|tank|..., "type": the vehicle}
/hudmsg?lastEvt=N&lastDmg=M   {"events": [...], "damage": [...]} newer than the ids given, each
                  {"id", "msg", "sender", "enemy", "mode", "time"}; damage lines read like
                  "Name (Vehicle) shot down Name (Vehicle)"
/gamechat?lastId=N  the chat newer than the id given, [{"id", "msg", "sender", "enemy", "mode", "time"}]
/mission.json    the battle's objectives and their status
/map.img         the map's picture the page draws the objects on
```

Jede Antwort wird vollständig im Roh-Beiblatt der Session unter ihrem Endpunkt behalten (map_info, map_obj, state, indicators, hudmsg, gamechat, mission, map_img); zwischen den Schlachten gehen die Antworten in eine eigene Session.

Eine Kartenposition wird mit der Ausdehnung zu Metern: u = min_x + x \* (max_x - min_x) Osten, v = max_y - y \* (max_y - min_y) Norden (das y des Bildes läuft nach unten). Zeilen sind x = u, y = Höhe (das "H, m" des eigenen Flugzeugs; 0 für alles andere), z = v, sodass Y nach oben zeigt; z ist für den Viewer gespiegelt, damit Norden nicht nach unten gezeichnet wird.

Farben zeigen die Seiten, so wie der Spieler sie sieht: eigene Seite gelb (standardmäßig #faC81E), Staffel grün, Verbündete blau (#174DFF), Gegner rot (#f40C00); Farbenblind-Paletten ändern sie, deshalb entscheidet der Farbton, nicht der genaue Wert. Das Spiel benennt niemanden auf der Karte und gibt Objekten keine IDs: Andere Objekte bekommen hier IDs, indem sie von Abfrage zu Abfrage verfolgt werden (das nächste Objekt desselben Typs und Symbols), was zwei Flugzeuge desselben Typs vertauschen kann, die dicht aneinander vorbeifliegen. Der eigene Name des Spielers steht ebenfalls nicht in der API: Gib ihn in den Einstellungen an (`config --set player_names.warthunder-webmap=<dein Name>`), dann werden Kill-Feed-Zeilen über den Spieler zu Kills und Toden; ohne ihn werden sie als Kill-Feed aufgezeichnet.

Quellen: die eigene Seite des Spiels auf <http://127.0.0.1:8111> und ihr JSON; Feldfakten, wie sie das Projekt JoyPro 2 dokumentiert (docs/telemetry-recording.md; GPL, nur für Fakten benutzt).

## Positionen und Achsen {#positions-and-axes}

| | |
|---|---|
| Positionen aufgezeichnet | ja |
| Oben-Achse | `y` |
| Einheiten | Meter (Karte Osten/Norden; Höhe nur für das eigene Flugzeug) |
| Für den Viewer gespiegelt | `z` |
| Einheitenfaktor (`scale`: der Viewer multipliziert Positionen damit) | 1 |

Diese landen in der `meta.json` jeder Session (`axes`) und, wenn die Session Positionen hat, im Footer von `heat.parquet`, damit der 3DHeat-Viewer die Zeilen selbst dreht und skaliert - siehe [Die Daten](the-data.md).

## Mehrspieler {#multiplayer}

- Als online gespielt markiert (`multiplayer`): **ja**. `games --markdown` zeigt das als "erlaubt (liest nur, was das Spiel veröffentlicht)".
- Art `gsi`: Er liest nur, was das Spiel oder die Plattform herausgibt (eine Game-State-Integration oder lokale API, die das Spiel bereitstellt), deshalb zeichnet er auch im Online-Spiel auf wie offline; die Markierung entscheidet nur, ob Speicher jemals gelesen werden darf.
- Speicher: **nie** von diesem Adapter gelesen. Nur `memory`-Adapter lesen Speicher, und nie bei einem Spiel, das als online gespielt markiert ist - siehe [Quellen und Regeln](sources-and-rules.md).

## Erfasste Statistiken {#statistics-recorded}

Statistik-Schlüssel, die der Code dieses Adapters namentlich setzt (das `stats` jeder Session in `meta.json` und die Tabelle `stats` in `watcher.sqlite`):

`bad_packets`, `deaths`, `distance_m`, `hits_dealt`, `hits_taken`, `kills`, `max_altitude_m`, `max_tas_kmh`, `spawns`, `vehicle`

Ein Schlüssel in geschweiften Klammern wird zur Laufzeit vervollständigt (`score.{team}` ist ein Schlüssel pro Team). Schlüssel, die der Code aus einer Tabelle der Spielfelder oder aus den eigenen Statistiknamen des Spiels übernimmt, stehen nicht in dieser Liste; "Was aufgezeichnet wird" oben nennt sie.

## Vollständigkeit {#completeness}

Der Watcher folgt der [Konverterregel](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md) von 3DHeat: Was die Quelle enthält, wird gelesen oder behalten, nie weggelassen. Neben den Zeilen wird jedes Paket, jede Seite, jede Zeile oder Antwort, die der Adapter erhält, vollständig in der `heat.raw.parquet` der Session behalten (Spalten `time`, `ms`, `type`, `used`, `payload`, `text`, dann jedes nach Namen behaltene Feld; `used` markiert, was auch zu Zeilen wurde), und `selfCheck.completeness` in der `meta.json` zählt jeden `type` - `lost` ist 0.

**Gelesen**

- /map_info.json: Ausdehnung und Gitter der Karte (Meter, die Karten-ID) in meta.json; eine ungültige beendet die Schlacht
- /map_obj.json (zweimal pro Sekunde): das eigene Fahrzeug, andere Flugzeuge und Bodeneinheiten (verfolgte IDs, Seite aus der Farbe, Symbol, Kurs, Farbe) und Flugplätze, Zonen und Basen als Zeilen
- /state (zweimal pro Sekunde, im Flugzeug): Höhe, TAS, IAS, Mach und Vy auf den eigenen Zeilen
- /indicators (alle 2 s): Heer und Fahrzeugtyp
- /hudmsg (einmal pro Sekunde): Zeilen des Kill- und Schadensfeeds als Kills, Tode, Treffer und Feed-Zeilen; andere HUD-Ereignisse als Zeilen

**Roh behalten**

- jede Antwort vollständig, `text` das JSON, wie das Spiel es sendete, unter ihrem Endpunkt: `map_info`, `map_obj`, `state`, `indicators`, `hudmsg`, `gamechat`, `mission`; `map_img` die Bytes des Kartenbilds als `payload`, einmal pro Schlacht
- was nur das Roh-Beiblatt enthält: jedes /state-Feld außer den fünf gelesenen (AoA, AoS, Ny, Wx, Gas, Drehzahl, Treibstoff, ... - die Menge unterscheidet sich von Flugzeug zu Flugzeug), jedes /indicators-Feld (die Cockpit-Instrumente von Flugzeugen, Geschwindigkeit, Gang, Besatzung und Stabilisator von Panzern), die anderen Schlüssel der Kartenobjekte (color[], blink, icon_bg, Flugplatz-Enden), sender, enemy und mode aus hudmsg, der Chat (/gamechat, einmal pro Sekunde), die Ziele der Schlacht und ihr Status (/mission.json, alle 10 s in einer Schlacht), Zeilen, die vor dem Start des Watchers gesagt wurden
- zwischen den Schlachten (Hangar, Laden) gehen die Antworten in eine eigene Session, in meta.json als `between_battles` markiert, die keine Zeilen hat

**Nicht verfügbar**

- Namen, IDs und Höhen der Fahrzeuge anderer Spieler: die Web-Karte hat sie nicht (IDs werden hier vergeben, indem Objekte von Abfrage zu Abfrage verfolgt werden); der Kill-Feed nennt Spieler ohne Positionen
- alles außerhalb der Web-Karte: die Replays des Spiels liest der Konverter für War-Thunder-Replays, und der Speicher des Spiels wird nie gelesen (ein Online-Spiel)
- /map_obj.json häufiger als zweimal pro Sekunde: die Abfragerate bleibt niedrig, damit der eigene Webserver des Spiels nicht belastet wird

**Größe**: etwa 50-120 MB pro Stunde JSON vor zstd in einer Schlacht (map_obj 5-15 KB zweimal pro Sekunde, state etwa 1,5 KB zweimal pro Sekunde, indicators alle 2 s, Chat und HUD-Zeilen klein) plus das Kartenbild einmal pro Schlacht (unter 2 MB); 1-2 MB pro Stunde zwischen den Schlachten (das Kartenbild zweimal pro Sekunde, HUD und Chat einmal, jeweils eine kurze Antwort); zstd verkleinert wiederholtes JSON mehr als zehnfach

## Geprüft {#verified}

gegen einen lokalen Fake-Server getestet, der Antworten im Format der Web-Karte des Spiels liefert; am laufenden Spiel ungetestet

## Quelle {#source}

[heat3d_watch/adapters/warthunder.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/warthunder.py)

<!-- Generated from the adapter by tools/gen_game_pages.py; change the adapter and run it again rather than editing this page. -->
