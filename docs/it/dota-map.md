---
title: "Mappa di Dota 2"
nav_order: 6.5
lang: "it"
source: dota-map.md
source_hash: "3dcde11c7784"
nav_exclude: true
search_exclude: true
---
# La mappa di Dota 2 come livello (`dota-map`) {#dota-2s-map-as-a-level-dota-map}

La mappa di Dota 2 in 3D - terreno, scogliere, acqua, ogni albero e gli edifici, nel sistema di riferimento e nelle unità in cui sono disegnate le [tabelle dei replay di Dota 2](game-dota-replays.md) - è creata dal suo strumento, **3DHeat Dota**
([3DHeat-Ext-Dota](https://github.com/Holdi601/3DHeat-Ext-Dota),
[documentazione](https://holdi601.github.io/3DHeat-Ext-Dota/)). Legge i file di gioco di Valve, quindi resta fuori dal watcher: se un giorno dovrà essere tolto, il watcher resta com'è.

Installalo una volta, come dice la sua pagina [Prima di iniziare](https://holdi601.github.io/3DHeat-Ext-Dota/before-you-start.html)
(pacchetto Python, più la riga di comando di Source2Viewer), poi esegui

```bash
heat3d-dota-maps level -o dota.glb
```

oppure, tramite il watcher,

```bash
python -m heat3d_watch dota-map [<map>] -o <file.glb> [--game FOLDER] [--source2viewer EXE] [--detail UNITS]
```

che esegue `heat3d-dota-maps level` con le stesse opzioni e passa oltre il suo file di output e il suo stato di uscita. Il watcher trova lo strumento come comando `heat3d-dota-maps` nel `PATH`, come pacchetto `heat3d_ext_dota` installato, oppure come sua cartella dei sorgenti in `HEAT3D_DOTA_MAPS` o accanto al watcher (`exporters/ext/dota-maps` in una copia di 3DHeat). Nulla di esso viene importato nel watcher; viene solo eseguito. Se non si trova da nessuna parte, `dota-map` stampa dove scaricarlo ed esce con codice 2.

Carica il file `.glb` nel pannello **Sfondo / livello** della viewer (**Modello 3D…**) sotto una tabella di Dota; la viewer riconosce il file dalle sue parti, lo tiene nella sua libreria dei livelli, e da allora il suo pulsante **Mappa di Dota 2** lo carica. Come viene creato il livello, le sue parti e come è stato verificato:
[Creare un livello](https://holdi601.github.io/3DHeat-Ext-Dota/level.html).
