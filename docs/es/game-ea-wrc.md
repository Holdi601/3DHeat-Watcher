---
title: "EA SPORTS WRC (datos en vivo)"
nav_order: 17
lang: "es"
source: game-ea-wrc.md
source_hash: "c97300f65c43"
nav_exclude: true
search_exclude: true
---
# EA SPORTS WRC (datos en vivo)

Mientras juegas a EA SPORTS WRC, el watcher guarda los datos que el propio juego envía, para que luego puedas verlos en un mapa del visor de 3DHeat.

*Detalles técnicos: adaptador `ea-wrc`, tipo [`telemetry`](sources-and-rules.md); se ejecuta mientras `WRC.exe` está en marcha y busca datos nuevos cada 0,1 s.*

## Qué se graba

- la posición del coche propio (XYZ en el mundo, m) 10 veces por segundo, con velocidad, marcha, acelerador, freno y distancia del tramo
- inicio del tramo (cuando arranca el cronómetro del tramo), llegada con el tiempo del tramo, reinicios
- teletransportes (un regreso a la carretera): `teleport` donde estaba el coche, `spawn` donde está ahora
- tramos, mejor tiempo de tramo, distancia, velocidad máxima

## De dónde sale

UDP 127.0.0.1:20777, el paquete `session_update` de la estructura `wrc` por defecto (Documents\My Games\WRC\telemetry\config.json); mientras otra aplicación tenga el puerto 20777, el watcher deja el puerto a esa aplicación

## Cómo activarlo

`python -m heat3d_watch setup ea-wrc --apply` activa el paquete `session_update` en config.json (antes hace una copia de seguridad)

Escribe el comando en una terminal abierta en la carpeta del watcher (ver [Antes de empezar](before-you-start.md)). Si falla, la última línea dice por qué; [Instalar y ejecutar](installing-and-running.md) recoge las causas más habituales.

`python -m heat3d_watch setup ea-wrc` muestra los archivos que cambiaría; `python -m heat3d_watch setup ea-wrc --apply` los cambia, guardando el original como `<archivo>.heat3d-backup` (ver [Comandos](commands.md#setup)). Imprime `ea-wrc: changed: ...` por cada cambio, o `ea-wrc: nothing to change` cuando ya está activado.

## Cómo funciona

La telemetría propia de los juegos de carreras: Forza, los juegos de Assetto Corsa, los juegos de rally y BeamNG, grabada como trazados, vueltas y tramos.

Todos estos juegos publican su telemetría a propósito, para paneles y para simuladores de movimiento; no se inyecta nada y no se lee nada que el juego no entregue. La decodificación no se escribe dos veces: son los grabadores de vueltas de gamecapture, que están en `heat3d_capture/telemetry` de 3DHeat GameCapture, copiados a `heat3d_watch/decoders` (probados allí con paquetes creados a partir de los formatos publicados). Este módulo convierte sus fotogramas en las filas del watcher: la posición del coche varias veces por segundo con su velocidad, marcha y pedales, un evento por vuelta o tramo, y los números que anota el piloto: vueltas, mejor vuelta, distancia y velocidad máxima.

#### Forza (Horizon 4/5/6, Motorsport)

UDP "Data Out", que se activa en el HUD y en los ajustes de juego, hacia 127.0.0.1 puerto 5300, formato Dash. Un paquete por tick de simulación; el desplazamiento del bloque de datos del dash se encuentra a partir de los paquetes (`forza.detect_layout`). Metros del mundo, Y hacia arriba; el mundo es zurdo y se dibuja tal como llega, igual que lo hace el grabador de vueltas (documentación "Data Out" de Forza Motorsport y de Forza Horizon). El juego envía a un solo puerto, y FH Companion y otras aplicaciones Data Out escuchan en ese mismo puerto. Dos programas no pueden compartirlo: en Windows, el socket enlazado a 127.0.0.1 recibe los paquetes y el enlazado a todas las direcciones en el mismo puerto no recibe ninguno, sea cual sea el que llegó primero. Por eso el watcher espera un poco después de que arranque el juego antes de tomar el puerto, nunca se lo quita a una aplicación que ya lo tiene, y lo suelta en cuanto otra aplicación empieza a escuchar en él. Mientras tiene el puerto, reenvía cada paquete sin cambios a 127.0.0.1:5301: pon el campo de puerto de FH Companion (su pestaña de telemetría) en 5301 y ambos graban.

#### Todo lo que se guarda

Las filas son unas pocas por segundo; los juegos envían muchos más datos. Cada paquete UDP que llega (en los menús, entre vueltas, los que ningún decodificador lee) se guarda entero en `heat.raw.parquet` de la sesión, bajo su formato (`dash-horizon`, `session_update`, `extradata3`, `H3D1`, ...), y cada página de memoria compartida (toda la asignación, no solo los bytes decodificados) cada vez que cambia, bajo el nombre de su asignación (`acpmf_physics`, ...). `used` marca lo que también se convirtió en filas; `selfCheck.completeness` de `meta.json` cuenta cada tipo (regla de conversores de 3DHeat).

El mismo módulo también sirve a: [Assetto Corsa (datos en vivo)](game-assetto-corsa.md), [Assetto Corsa Competizione (datos en vivo)](game-assetto-corsa-competizione.md), [Assetto Corsa EVO (datos en vivo)](game-assetto-corsa-evo.md), [Assetto Corsa Rally (datos en vivo)](game-assetto-corsa-rally.md), [BeamNG.drive (datos en vivo)](game-beamng.md), [DiRT Rally 2.0 (datos en vivo)](game-dirt-rally-2.md), [Forza Horizon 4 (datos en vivo)](game-forza-horizon-4.md), [Forza Horizon 5 (datos en vivo)](game-forza-horizon-5.md), [Forza Horizon 6 (datos en vivo)](game-forza-horizon-6.md), [Forza Motorsport (datos en vivo)](game-forza-motorsport.md), [Richard Burns Rally (datos en vivo)](game-richard-burns-rally.md).

## Posiciones y ejes

| | |
|---|---|
| Posiciones grabadas | sí |
| Eje hacia arriba | `y` |
| Unidades | metros |
| Reflejado para el visor | ninguno |
| Escala de unidad (`scale`: el visor multiplica las posiciones por ella) | 1 |

Esto va al `meta.json` de cada sesión (`axes`) y, cuando la sesión tiene posiciones, al pie (footer) de `heat.parquet`, así que el visor de 3DHeat gira y escala las filas por sí mismo; ver [Los datos](the-data.md).

## Multijugador

- Marcado como jugado en línea (`multiplayer`): **sí**. `games --markdown` lo muestra como "permitido (lee solo lo que publica el juego)".
- Tipo `telemetry`: lee solo lo que el juego o la plataforma entregan (un puerto UDP o memoria compartida que el juego publica), así que graba también en el juego en línea; la marca solo decide si se puede leer la memoria en algún momento.
- Memoria: **nunca** la lee este adaptador. Solo los adaptadores `memory` leen memoria, y nunca en un juego marcado como jugado en línea; ver [Fuentes y reglas](sources-and-rules.md).

## Estadísticas grabadas

Claves de estadística que el código de este adaptador fija por nombre (el `stats` de cada sesión en `meta.json` y la tabla `stats` de `watcher.sqlite`):

`best_lap`, `best_stage`, `distance_km`, `laps`, `stages`, `top_speed_kmh`

Una clave entre llaves se completa en tiempo de ejecución (`score.{team}` es una clave por equipo). Las claves que el código toma de una tabla de campos del juego o de sus propios nombres de estadística no están en esta lista; "Qué se graba" más arriba las nombra.

## Completitud

El watcher sigue la [regla de conversores](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md) de 3DHeat: lo que la fuente contiene se lee o se guarda, nunca se descarta. Además de las filas, cada paquete, página, línea o respuesta que recibe el adaptador se guarda entero en `heat.raw.parquet` de la sesión (columnas `time`, `ms`, `type`, `used`, `payload`, `text`, y los campos que se guardan por nombre; `used` marca lo que también se convirtió en filas), y `selfCheck.completeness` de `meta.json` cuenta cada `type`: `lost` es 0.

**Leído**

- filas a 10 Hz: posición, velocidad, marcha, acelerador, freno, distancia del tramo, guiñada, rpm, dirección; inicio del tramo, llegada con el tiempo del tramo, reinicios

**Guardado en bruto**

- cada paquete que llega al puerto, entero, a la velocidad del juego, bajo su formato: `session_update` (la estructura `wrc` por defecto, 237 bytes), `wrc <n>-byte` para cualquier otro paquete que envíe la configuración
- en el paquete, más allá de las filas: velocidad y aceleración del mundo, los ejes del coche, la posición y velocidad de cada cubo de rueda, velocidad del punto de contacto, temperatura de los frenos, embrague, freno de mano, el tiempo del juego; 22 bytes (desplazamientos 16-36 y 40) que ninguna lista de canales publicada nombra

**No disponible**

- otros coches: los juegos envían solo el coche del jugador
- los otros estructuras y paquetes que puede definir la configuración de telemetría (session_start, session_end, pause): `setup` solo activa `session_update`; cualquier otro paquete enviado al puerto se guarda

**Tamaño**: unos 65 MB por hora a 60 paquetes por segundo (237 bytes más una cabecera de elemento de 70 bytes; la tasa -1 de la configuración envía uno por fotograma, así que más con una tasa de fotogramas mayor); zstd guarda una fracción

## Verificado

la decodificación es la del grabador de vueltas de gamecapture (probada con paquetes creados a partir de los formatos documentados); el adaptador, probado con paquetes creados en la prueba y enviados por UDP; sin probar contra el juego

## Fuente

[heat3d_watch/adapters/racing.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/racing.py)

<!-- Generated from the adapter by tools/gen_game_pages.py; change the adapter and run it again rather than editing this page. -->
