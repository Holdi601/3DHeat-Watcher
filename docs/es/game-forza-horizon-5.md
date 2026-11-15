---
title: "Forza Horizon 5 (datos en vivo)"
nav_order: 22
lang: es
source: game-forza-horizon-5.md
source_hash: "0083724478e7"
nav_exclude: true
search_exclude: true
---
# Forza Horizon 5 (datos en vivo) {#forza-horizon-5-live-data}

Mientras juegas a Forza Horizon 5, el watcher guarda los datos que el propio juego envía, para que luego puedas verlos en un mapa del visor de 3DHeat.

*Detalles técnicos: adaptador `forza-horizon-5`, tipo [`telemetry`](sources-and-rules.md); se ejecuta mientras `ForzaHorizon5.exe` está en marcha y busca datos nuevos cada 0,1 s.*

## Qué se graba {#what-is-recorded}

- la posición del coche propio (XYZ en el mundo, m) 10 veces por segundo, con velocidad, marcha, acelerador, freno y vuelta
- inicio y fin de la conducción (session_start/session_end), vueltas con el tiempo de vuelta del juego
- inicio y llegada de carrera con la posición en carrera
- teletransportes (rebobinado, viaje rápido): `teleport` donde estaba el coche, `spawn` donde está ahora
- vueltas, mejor vuelta, distancia, velocidad máxima, carreras

## De dónde sale {#where-it-comes-from}

Forza Data Out, UDP 127.0.0.1:5300 (formato Dash); cada paquete se reenvía sin cambios a 127.0.0.1:5301

## Cómo activarlo {#how-to-switch-it-on}

En el juego: Ajustes > HUD y jugabilidad > Data Out Activado, IP 127.0.0.1, puerto 5300 (Motorsport: formato Dash). FH Companion u otra aplicación Data Out: pon su puerto en 5301; el watcher pasa cada paquete. Mientras otra aplicación escuche en el 5300, el watcher deja el puerto a esa aplicación y no graba nada

## Cómo funciona {#how-it-works}

La telemetría propia de los juegos de carreras: Forza, los juegos de Assetto Corsa, los juegos de rally y BeamNG, grabada como trazados, vueltas y tramos.

Todos estos juegos publican su telemetría a propósito, para paneles y para simuladores de movimiento; no se inyecta nada y no se lee nada que el juego no entregue. La decodificación no se escribe dos veces: son los grabadores de vueltas de gamecapture, que están en `heat3d_capture/telemetry` de 3DHeat GameCapture, copiados a `heat3d_watch/decoders` (probados allí con paquetes creados a partir de los formatos publicados). Este módulo convierte sus fotogramas en las filas del watcher: la posición del coche varias veces por segundo con su velocidad, marcha y pedales, un evento por vuelta o tramo, y los números que anota el piloto: vueltas, mejor vuelta, distancia y velocidad máxima.

#### Forza (Horizon 4/5/6, Motorsport) {#forza-horizon-456-motorsport}

UDP "Data Out", que se activa en el HUD y en los ajustes de juego, hacia 127.0.0.1 puerto 5300, formato Dash. Un paquete por tick de simulación; el desplazamiento del bloque de datos del dash se encuentra a partir de los paquetes (`forza.detect_layout`). Metros del mundo, Y hacia arriba; el mundo es zurdo y se dibuja tal como llega, igual que lo hace el grabador de vueltas (documentación "Data Out" de Forza Motorsport y de Forza Horizon). El juego envía a un solo puerto, y FH Companion y otras aplicaciones Data Out escuchan en ese mismo puerto. Dos programas no pueden compartirlo: en Windows, el socket enlazado a 127.0.0.1 recibe los paquetes y el enlazado a todas las direcciones en el mismo puerto no recibe ninguno, sea cual sea el que llegó primero. Por eso el watcher espera un poco después de que arranque el juego antes de tomar el puerto, nunca se lo quita a una aplicación que ya lo tiene, y lo suelta en cuanto otra aplicación empieza a escuchar en él. Mientras tiene el puerto, reenvía cada paquete sin cambios a 127.0.0.1:5301: pon el campo de puerto de FH Companion (su pestaña de telemetría) en 5301 y ambos graban.

#### Todo lo que se guarda {#everything-kept}

Las filas son unas pocas por segundo; los juegos envían muchos más datos. Cada paquete UDP que llega (en los menús, entre vueltas, los que ningún decodificador lee) se guarda entero en `heat.raw.parquet` de la sesión, bajo su formato (`dash-horizon`, `session_update`, `extradata3`, `H3D1`, ...), y cada página de memoria compartida (toda la asignación, no solo los bytes decodificados) cada vez que cambia, bajo el nombre de su asignación (`acpmf_physics`, ...). `used` marca lo que también se convirtió en filas; `selfCheck.completeness` de `meta.json` cuenta cada tipo (regla de conversores de 3DHeat).

El mismo módulo también sirve a: [Assetto Corsa (datos en vivo)](game-assetto-corsa.md), [Assetto Corsa Competizione (datos en vivo)](game-assetto-corsa-competizione.md), [Assetto Corsa EVO (datos en vivo)](game-assetto-corsa-evo.md), [Assetto Corsa Rally (datos en vivo)](game-assetto-corsa-rally.md), [BeamNG.drive (datos en vivo)](game-beamng.md), [DiRT Rally 2.0 (datos en vivo)](game-dirt-rally-2.md), [EA SPORTS WRC (datos en vivo)](game-ea-wrc.md), [Forza Horizon 4 (datos en vivo)](game-forza-horizon-4.md), [Forza Horizon 6 (datos en vivo)](game-forza-horizon-6.md), [Forza Motorsport (datos en vivo)](game-forza-motorsport.md), [Richard Burns Rally (datos en vivo)](game-richard-burns-rally.md).

## Posiciones y ejes {#positions-and-axes}

| | |
|---|---|
| Posiciones grabadas | sí |
| Eje hacia arriba | `y` |
| Unidades | metros; el mundo de Forza es zurdo, se dibuja tal como llega, igual que el grabador de vueltas |
| Reflejado para el visor | ninguno |
| Escala de unidad (`scale`: el visor multiplica las posiciones por ella) | 1 |

Esto va al `meta.json` de cada sesión (`axes`) y, cuando la sesión tiene posiciones, al pie (footer) de `heat.parquet`, así que el visor de 3DHeat gira y escala las filas por sí mismo; ver [Los datos](the-data.md).

## Multijugador {#multiplayer}

- Marcado como jugado en línea (`multiplayer`): **sí**. `games --markdown` lo muestra como "permitido (lee solo lo que publica el juego)".
- Tipo `telemetry`: lee solo lo que el juego o la plataforma entregan (un puerto UDP o memoria compartida que el juego publica), así que graba también en el juego en línea; la marca solo decide si se puede leer la memoria en algún momento.
- Memoria: **nunca** la lee este adaptador. Solo los adaptadores `memory` leen memoria, y nunca en un juego marcado como jugado en línea; ver [Fuentes y reglas](sources-and-rules.md).

## Estadísticas grabadas {#statistics-recorded}

Claves de estadística que el código de este adaptador fija por nombre (el `stats` de cada sesión en `meta.json` y la tabla `stats` de `watcher.sqlite`):

`best_lap`, `distance_km`, `laps`, `races`, `top_speed_kmh`

Una clave entre llaves se completa en tiempo de ejecución (`score.{team}` es una clave por equipo). Las claves que el código toma de una tabla de campos del juego o de sus propios nombres de estadística no están en esta lista; "Qué se graba" más arriba las nombra.

## Completitud {#completeness}

El watcher sigue la [regla de conversores](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md) de 3DHeat: lo que la fuente contiene se lee o se guarda, nunca se descarta. Además de las filas, cada paquete, página, línea o respuesta que recibe el adaptador se guarda entero en `heat.raw.parquet` de la sesión (columnas `time`, `ms`, `type`, `used`, `payload`, `text`, y los campos que se guardan por nombre; `used` marca lo que también se convirtió en filas), y `selfCheck.completeness` de `meta.json` cuenta cada `type`: `lost` es 0.

**Leído**

- filas a 10 Hz: posición, velocidad, marcha, acelerador, freno, vuelta, guiñada/cabeceo/alabeo (rad), rpm, dirección (-1..1); session_start con el ordinal, la clase, el PI y el tren de potencia del coche; vueltas con el tiempo de vuelta del juego; posición en carrera

**Guardado en bruto**

- cada paquete que llega al puerto, entero, a la velocidad del juego (un paquete por tick de simulación), bajo su formato: `dash-horizon` (324 bytes, Forza Horizon), `dash` (311, Motorsport 7), `dash-fm2023` (331, Forza Motorsport 2023: desgaste de neumáticos e id de pista), `sled` (232, sin posición), `<n>-byte` para cualquier otro, incluidos los paquetes de menú (isRaceOn 0), los paquetes retenidos hasta que se demuestra el diseño del dash, y los unos 13 bytes del paquete de Horizon que ningún diseño publicado nombra
- el bloque Sled con cada canal de rueda (relación de deslizamiento, ángulo de deslizamiento, deslizamiento combinado, suspensión, velocidad de rueda, rumble, charco), aceleraciones, velocidad angular, potencia, par, turbo, combustible, temperaturas de neumáticos, embrague, freno de mano, línea de conducción, diferencia de freno de IA: todo está en los paquetes, y `decoders/fulllap.decode_full` lo decodifica a partir de ellos

**No disponible**

- otros coches: Data Out describe solo el coche del jugador
- el nombre de la pista o de la ruta: Forza Horizon nunca lo envía; Motorsport 2023 envía solo un número de pista
- los paquetes mientras otra aplicación (FH Companion) tiene el UDP 5300: el watcher deja el puerto a esa aplicación

**Tamaño**: unos 85 MB por hora antes de comprimir (60 paquetes por segundo de 324 bytes más una cabecera de elemento de 70 bytes); los paquetes consecutivos apenas difieren, así que zstd guarda una fracción

## Verificado {#verified}

la decodificación es la del grabador de vueltas de gamecapture (probada con paquetes creados a partir del diseño Data Out); el adaptador, probado con paquetes sintéticos y con trayectorias de vueltas grabadas reproducidas como paquetes; sin probar contra el propio juego

## Fuente {#source}

[heat3d_watch/adapters/racing.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/racing.py)

<!-- Generated from the adapter by tools/gen_game_pages.py; change the adapter and run it again rather than editing this page. -->
