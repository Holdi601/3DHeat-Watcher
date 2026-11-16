---
title: "Mapa de Dota 2"
nav_order: 6.5
lang: "es"
source: dota-map.md
source_hash: "6c7a1c39d1bf"
nav_exclude: true
search_exclude: true
---
# El mapa de Dota 2 como nivel (`dota-map`) {#dota-2s-map-as-a-level-dota-map}

El mapa de Dota 2 en 3D - el terreno, los acantilados, el agua, cada árbol y los
edificios, en el marco y las unidades en que se dibujan las [tablas de repeticiones de Dota 2](game-dota-replays.md) -
lo hace su propia herramienta, **3DHeat Dota**
([3DHeat-Ext-Dota](https://github.com/Holdi601/3DHeat-Ext-Dota),
[documentación](https://holdi601.github.io/3DHeat-Ext-Dota/)), un proyecto
propio fuera del watcher.

Instálala una vez, como indica su página [Antes de empezar](https://holdi601.github.io/3DHeat-Ext-Dota/before-you-start.html)
(paquete de Python, más la línea de comandos de Source2Viewer), y luego ejecuta
una de estas dos opciones:

```bash
heat3d-dota-maps level -o dota.glb
```

o, a través del watcher,

```bash
python -m heat3d_watch dota-map [<mapa>] -o <archivo.glb> [--game CARPETA] [--source2viewer EJECUTABLE] [--detail UNIDADES]
```

que ejecuta `heat3d-dota-maps level` con las mismas opciones y pasa su salida y
su código de salida tal cual. El watcher encuentra la herramienta como el comando
`heat3d-dota-maps` en `PATH`, como el paquete `heat3d_ext_dota` instalado, o como
su carpeta de código en `HEAT3D_DOTA_MAPS` o junto al watcher (`exporters/ext/dota-maps`
en una copia de 3DHeat). El watcher no importa nada de ella; solo la ejecuta.
Si no está en ninguno de esos sitios, `dota-map` indica dónde conseguirla y sale con el código 2.

Carga el archivo `.glb` en el panel **Fondo / nivel** del visor (**Modelo 3D…**)
bajo una tabla de Dota; el visor reconoce el archivo por sus partes, lo guarda en
su biblioteca de niveles, y a partir de entonces su botón **Mapa de Dota 2** lo carga.
Cómo se hace el nivel, sus partes y cómo se comprobó:
[Crear un nivel](https://holdi601.github.io/3DHeat-Ext-Dota/level.html).
