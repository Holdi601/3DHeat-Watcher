---
title: "Momentos destacados de NVIDIA (plataforma)"
nav_order: 34
lang: "es"
source: game-nvidia-highlights.md
source_hash: "5d45211c0e37"
nav_exclude: true
search_exclude: true
---
# Momentos destacados de NVIDIA (plataforma) {#nvidia-highlights-platform}

El watcher guarda lo que NVIDIA Highlights conserva sobre tus juegos, para que luego puedas ver tu historial en un mapa del visor de 3DHeat.

*Detalles técnicos: adaptador `nvidia-highlights`, tipo [`platform`](sources-and-rules.md); se ejecuta todo el tiempo (no espera a que se inicie un juego) y busca datos nuevos cada 10 s.*

## Qué se graba {#what-is-recorded}

- cada clip, momento destacado o captura nuevos: juego, archivo, tipo, duración y el instante (ms de reloj)
- el id y el nombre del momento destacado cuando el juego lo registró en NVIDIA
- dónde estaba el jugador en ese momento, cuando otro adaptador grabó entonces el mismo juego
- las peticiones de momento destacado que escriben los juegos con GfeSDK, incluso cuando no se guarda ningún clip

## De dónde sale {#where-it-comes-from}

%LOCALAPPDATA%\NVIDIA Corporation\NVIDIA Overlay\UGCTracker.json, GallerySettings.json, Highlights\\&lt;juego>\config.json; los clips en la carpeta de capturas (%USERPROFILE%\Videos\NVIDIA\\&lt;Juego>\\\*.mp4) y &lt;temp>\Highlights\\&lt;juego>; %LOCALAPPDATA%\NVIDIA Corporation\GfeSDK\\&lt;exe>_&lt;pid>.log

## Cómo activarlo {#how-to-switch-it-on}

NVIDIA App: Instant Replay o Highlights activado, clips guardados con una tecla rápida o por el juego

## Cómo funciona {#how-it-works}

Lo que el lanzador y el controlador gráfico guardan sobre el juego: las estadísticas de Steam,
los logros, el tiempo de juego y las líneas de tiempo, y los clips y momentos destacados de NVIDIA.

Ninguna de estas fuentes necesita que el juego colabore ni que esté en marcha, así que los tres
adaptadores de aquí están siempre activos y miran unos pocos archivos cada pocos segundos.

#### Momentos destacados y clips de NVIDIA (`nvidia-highlights`) {#nvidia-highlights-and-clips-nvidia-highlights}

Lo que guarda NVIDIA App / GeForce Experience, todo bajo
`%LOCALAPPDATA%\NVIDIA Corporation\NVIDIA Overlay`:
```text
UGCTracker.json      el índice de la galería: {"UGC": [{id, path, type (video,
                     image), subType (InstantReplay, Normal, ...), date
                     (UTC, cuando se escribió el archivo), profileName, drsName
                     (el exe), shortName, msDuration, ...}], "apps", "info"}
GallerySettings.json settings.currentDirectoryV2 (dónde se guardan los clips),
                     settings.tempDirectory (los momentos destacados esperan en
                     <temp>\Highlights\<juego> hasta guardarse)
Highlights\<juego>\config.json  los tipos de momento destacado que registró un juego:
                     {"highlights": {id: {significance, highlightTags,
                     name: {locale: texto}}}, profileName, drsName, shortName}
```
y los propios archivos de clip, `<carpeta de capturas>\<Juego>\<Juego> aaaa.mm.dd -
hh.mm.ss.ff.DVR.mp4` (capturas: `<Juego> Screenshot aaaa.mm.dd - ...png`), siendo la hora del nombre
la hora local en que se guardó el clip. Los juegos con GfeSDK también escriben
sus llamadas de momento destacado en `%LOCALAPPDATA%\NVIDIA Corporation\GfeSDK\<exe>_<pid>.log`.

Lo que esto puede y no puede dar: un juego que admite NVIDIA Highlights (GfeSDK) registra los tipos
de momento una vez (un id como "kill", una importancia, etiquetas, un nombre para mostrar)
y luego solo dice "highlight <id>, desde <ms> antes de ahora hasta <ms> después". No hay posiciones, ni partida o ronda, ni rival, ni
datos propios: el SDK no tiene campo para nada de eso. Un clip guardado añade un archivo, un nombre de
juego, una duración y una hora. Así que lo que se graba es "este tipo de momento, en este juego, a esta hora",
y un lugar solo buscando la hora en la grabación de otro adaptador del mismo juego
(`position_at`), cosa que este adaptador hace con cada clip que graba.
<https://developer.nvidia.com/highlights>

Cada adaptador guarda lo que ya ha visto en `<datos>\state\<id>.json`, así que un reinicio
no graba nada dos veces.

Cada sesión también guarda, completo, aquello de lo que salen sus filas (regla del convertidor de 3DHeat,
docs/converters.md en el repositorio del visor), en `heat.raw.parquet`:
los bytes del archivo de estadísticas y de su esquema y el bloque localconfig del juego
(steam-stats; un archivo de estadísticas que el decodificador no puede leer da una sesión que solo
contiene sus bytes), el encabezado del archivo de la línea de tiempo y cada entrada en JSON
(steam-timeline), la entrada de índice de cada clip, las definiciones de momentos destacados del juego
y cada línea de los registros de GfeSDK, también las que no son peticiones de momento destacado
(nvidia-highlights).

El mismo módulo también sirve para: [Estadísticas de Steam (plataforma)](game-steam-stats.md), [Steam Timeline (plataforma)](game-steam-timeline.md).

## Posiciones y ejes {#positions-and-axes}

| | |
|---|---|
| Posiciones grabadas | solo prestadas: el lugar que tiene otra grabación del mismo juego para ese momento |
| Eje hacia arriba | `y` |
| Unidades | metros |
| Reflejado para el visor | ninguno |
| Escala de unidades (`scale`: el visor multiplica las posiciones por ella) | 1 |

Esto va a `meta.json` (`axes`) de cada sesión y, cuando la sesión tiene posiciones, al pie de `heat.parquet`, así que el visor de 3DHeat gira y escala las filas por sí mismo; mira [Los datos](the-data.md).

## Multijugador {#multiplayer}

- Marcado como jugado en línea (`multiplayer`): **no**. `games --markdown` lo muestra como "un jugador".
- Tipo `platform`: solo lee lo que la plataforma entrega (lo que guardan Steam o el controlador gráfico), así que graba también en línea, igual que sin conexión; la marca solo decide si se puede leer la memoria.
- Memoria: este adaptador **nunca** la lee. Solo los adaptadores `memory` leen memoria, y nunca en un juego marcado como jugado en línea; mira [Fuentes y reglas](sources-and-rules.md).

## Estadísticas que se graban {#statistics-recorded}

Claves de estadística que el código de este adaptador asigna por nombre (el `stats` de cada sesión en `meta.json` y la tabla `stats` de `watcher.sqlite`):

`clip_seconds`, `clips`, `placed`, `screenshots`

Una clave entre llaves se completa en tiempo de ejecución (`score.{team}` es una clave por equipo). Las claves que el código toma de una tabla de campos del juego o de sus nombres de estadística no aparecen en esta lista; "Qué se graba" más arriba las nombra.

## Completitud {#completeness}

El watcher sigue la [regla del convertidor](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md) de 3DHeat: lo que la fuente contiene se lee o se guarda, nunca se descarta. Además de las filas, cada paquete, página, línea o respuesta que recibe el adaptador se guarda completo en `heat.raw.parquet` de la sesión (columnas `time`, `ms`, `type`, `used`, `payload`, `text`, y cualquier campo guardado por nombre; `used` marca lo que también se convirtió en filas), y `selfCheck.completeness` de `meta.json` cuenta cada `type`; `lost` es 0.

**Se lee**

- cada clip y captura nuevos: juego, archivo, tipo, soporte, duración (índice, o si no la cabecera del MP4), el instante a partir del nombre del archivo, el id y el nombre del momento destacado cuando el juego los registró, y el lugar del jugador en ese momento según la grabación de otro adaptador
- las peticiones de momento destacado de GfeSDK (cada `Posted Request HL...`, salvo las llamadas de configuración) con su hora

**Se guarda en bruto**

- `UGC`: la entrada completa del clip en el índice de la galería UGCTracker.json, cada campo que escribe NVIDIA
- `clip_file`: para un clip que el índice no lista, la ruta del archivo, su tamaño, su hora y su carpeta
- `highlights_config`: el `Highlights\<juego>\config.json` del juego tal como está escrito (importancia, etiquetas, nombres en cada idioma), una vez por sesión
- `gfesdk_log`: cada línea de los registros de GfeSDK leídos después de la primera ejecución, `used` verdadero para las peticiones de momento destacado y falso para el resto (configuración, ajustes de vídeo, mensajes propios del SDK)

**No disponible**

- los propios clips y capturas: el vídeo y las imágenes se quedan donde los guardó NVIDIA; las filas nombran el archivo
- lo que había antes de la primera ejecución del adaptador: se da por visto, así que años de clips no se convierten en sesiones de golpe (`baseline`; False los graba)
- `apps` e `info` de UGCTracker.json y GallerySettings.json: ajustes de la aplicación, no momentos de juego; se usa la carpeta de capturas que nombran
- posiciones, rondas, rivales: GfeSDK no tiene campos para ellos

**Tamaño**: unos 1 KB por clip y unas pocas KB de definiciones y líneas de registro por cada inicio de juego: muy por debajo de 1 MB por hora

## Verificado {#verified}

probado con un índice de galería, ajustes, definiciones de momentos destacados y clips reales de una instalación local; las líneas de petición de momento destacado de GfeSDK y los ids de momento en los clips no están probados

## Fuente {#source}

[heat3d_watch/adapters/platform.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/platform.py)

<!-- Generated from the adapter by tools/gen_game_pages.py; change the adapter and run it again rather than editing this page. -->
