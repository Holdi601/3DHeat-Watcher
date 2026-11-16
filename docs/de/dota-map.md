---
title: "Dota-2-Karte"
nav_order: 6.5
lang: "de"
source: dota-map.md
source_hash: "3dcde11c7784"
nav_exclude: true
search_exclude: true
---
# Die Dota-2-Karte als Level (`dota-map`) {#dota-2s-map-as-a-level-dota-map}

Die Dota-2-Karte in 3D - Boden, Klippen, Wasser, jeder Baum und die Gebäude, im Rahmen und in den Einheiten, in denen die [Dota-2-Replay-Tabellen](game-dota-replays.md) gezeichnet sind - wird von einem eigenen Werkzeug erstellt, **3DHeat Dota** ([3DHeat-Ext-Dota](https://github.com/Holdi601/3DHeat-Ext-Dota), [Dokumentation](https://holdi601.github.io/3DHeat-Ext-Dota/)). Es liest Valves Spieldateien, deshalb wird es vom Watcher ferngehalten: Falls es je entfernt werden muss, bleibt der Watcher bestehen.

Installiere es einmal, wie es die Seite [Bevor du anfängst](https://holdi601.github.io/3DHeat-Ext-Dota/before-you-start.html) beschreibt (Python-Paket plus die Kommandozeile von Source2Viewer). Danach führst du entweder

```bash
heat3d-dota-maps level -o dota.glb
```

aus oder, über den Watcher,

```bash
python -m heat3d_watch dota-map [<map>] -o <file.glb> [--game FOLDER] [--source2viewer EXE] [--detail UNITS]
```

Das startet `heat3d-dota-maps level` mit denselben Optionen und gibt dessen Ausgabe und Exit-Status unverändert weiter. Der Watcher findet das Werkzeug als Befehl `heat3d-dota-maps` im `PATH`, als installiertes Paket `heat3d_ext_dota` oder als seinen Quellordner in `HEAT3D_DOTA_MAPS` oder neben dem Watcher (`exporters/ext/dota-maps` in einer 3DHeat-Kopie). Nichts davon wird in den Watcher importiert; es wird nur ausgeführt. Ist das Werkzeug nirgends zu finden, zeigt `dota-map` an, wo du es bekommst, und beendet sich mit Code 2.

Lade die `.glb`-Datei im Viewer im Bereich **Hintergrund / Level** (**3D-Modell…**) unter einer Dota-Tabelle: Der Viewer erkennt die Datei an ihren Teilen, legt sie in seiner Level-Bibliothek ab, und seine Schaltfläche **Dota-2-Karte** lädt sie ab dann. Wie das Level entsteht, welche Teile es hat und wie es geprüft wurde: [Ein Level bauen](https://holdi601.github.io/3DHeat-Ext-Dota/level.html).
