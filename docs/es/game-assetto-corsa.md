---
title: "Assetto Corsa (datos en vivo)"
nav_order: 2
lang: es
source: game-assetto-corsa.md
source_hash: "9132272cc104"
nav_exclude: true
search_exclude: true
---
# Assetto Corsa (datos en vivo) {#assetto-corsa-live-data}

Mientras juegas a Assetto Corsa, el watcher guarda los datos que el propio juego envía hacia fuera, para que después puedas verlos en un mapa del visor de 3DHeat.

*Detalles técnicos: adaptador `assetto-corsa`, tipo [`telemetry`](sources-and-rules.md); se ejecuta mientras `acs.exe` o `acs_x86.exe` está en marcha y busca datos nuevos cada 0,1 s.*

## Qué se graba {#what-is-recorded}

- posición de tu coche (XYZ en el mundo, m: media de los puntos de contacto de los neumáticos) a 10 Hz, con velocidad, marcha, acelerador y freno
- inicio y fin de la sesión, con la pista y el coche que indica el juego
- vueltas según el contador de vueltas del juego, con su tiempo de vuelta
- teletransportes (volver a boxes, un reinicio): `teleport` donde estaba el coche, `spawn` donde está ahora
- vueltas, mejor vuelta, distancia y velocidad máxima

## De dónde viene {#where-it-comes-from}

memoria compartida Local\acpmf_physics, Local\acpmf_graphics, Local\acpmf_static

## Cómo activarlo {#how-to-switch-it-on}

No hay que activar nada: el watcher lee la fuente tal como la entrega el juego o la plataforma.

## Cómo funciona {#how-it-works}

La telemetría propia de los juegos de carreras: Forza, los juegos de Assetto Corsa, los juegos de rally y BeamNG, grabada como recorridos, vueltas y etapas.

Todos estos juegos publican su telemetría a propósito, para paneles y simuladores de movimiento. No se inyecta nada y no se lee nada que el juego no entregue. La decodificación no está escrita dos veces: son los grabadores de vueltas de gamecapture, en `heat3d_capture/telemetry` de 3DHeat GameCapture, copiados en `heat3d_watch/decoders` (probados allí con paquetes construidos a partir de los formatos publicados). Este módulo convierte sus fotogramas en filas del watcher: la posición del coche unas pocas veces por segundo con su velocidad, marcha y pedales, un evento por vuelta o etapa, y los números que un piloto lleva: vueltas, mejor vuelta, distancia y velocidad máxima.

#### Forza (Horizon 4/5/6, Motorsport) {#forza-horizon-456-motorsport}

Salida "Data Out" por UDP, activada en los ajustes de HUD y de jugabilidad del juego, a 127.0.0.1 puerto 5300, formato Dash. Un paquete por tick de simulación; el desplazamiento del bloque del panel se encuentra a partir de los propios paquetes (`forza.detect_layout`). Metros del mundo, Y hacia arriba. El mundo es de sistema izquierdo y se dibuja tal como llega, igual que lo hace el grabador de vueltas (documentación "Data Out" de Forza Motorsport y Forza Horizon). El juego envía a un solo puerto, y FH Companion y otras apps de Data Out escuchan en ese mismo puerto. Dos programas no pueden compartirlo: en Windows, el socket ligado a 127.0.0.1 recibe los paquetes, y el que está ligado a todas las direcciones en el mismo puerto no recibe ninguno, da igual cuál llegó primero. Por eso el watcher espera un poco después de que arranque el juego antes de tomar el puerto, nunca se lo quita a una app que lo tenga, y lo suelta en cuanto otra app empieza a escuchar en él. Mientras tiene el puerto, reenvía cada paquete sin cambios a 127.0.0.1:5301: pon el campo de puerto de FH Companion (su pestaña de telemetría) en 5301 y ambos graban.

#### Assetto Corsa, ACC, AC EVO, AC Rally {#assetto-corsa-acc-ac-evo-ac-rally}

Memoria compartida que el juego escribe para las apps: `Local\acpmf_physics`, `Local\acpmf_graphics`, `Local\acpmf_static` (AC EVO: `Local\acevo_pmf_*`). Se abre solo en lectura y solo cuando el juego ya la ha creado (`simracing_shm`). La posición es la media de los cuatro puntos de contacto de los neumáticos, en metros del mundo, Y hacia arriba. Las vueltas se cuentan con el contador del juego (AC, ACC) o al pasar otra vez por el punto de salida (AC EVO, AC Rally), igual que hace `kunos.py` para el grabador de vueltas.

#### Todo lo que se guarda {#everything-kept}

Las filas son unas pocas por segundo; los juegos envían bastante más. Cada paquete UDP que llega, en los menús, entre vueltas o los que ningún decodificador lee, se guarda entero en `heat.raw.parquet` de la sesión, con su formato (`dash-horizon`, `session_update`, `extradata3`, `H3D1`, ...). Cada página de memoria compartida (toda la región asignada, no solo los bytes decodificados) se guarda cada vez que cambia, con el nombre de su región (`acpmf_physics`, ...). `used` marca lo que también se convirtió en filas. `selfCheck.completeness` de meta.json cuenta cada tipo (regla de conversión de 3DHeat).

El mismo módulo también sirve a: [Assetto Corsa Competizione (datos en vivo)](game-assetto-corsa-competizione.md), [Assetto Corsa EVO (datos en vivo)](game-assetto-corsa-evo.md), [Assetto Corsa Rally (datos en vivo)](game-assetto-corsa-rally.md), [BeamNG.drive (datos en vivo)](game-beamng.md), [DiRT Rally 2.0 (datos en vivo)](game-dirt-rally-2.md), [EA SPORTS WRC (datos en vivo)](game-ea-wrc.md), [Forza Horizon 4 (datos en vivo)](game-forza-horizon-4.md), [Forza Horizon 5 (datos en vivo)](game-forza-horizon-5.md), [Forza Horizon 6 (datos en vivo)](game-forza-horizon-6.md), [Forza Motorsport (datos en vivo)](game-forza-motorsport.md), [Richard Burns Rally (datos en vivo)](game-richard-burns-rally.md).

## Posiciones y ejes {#positions-and-axes}

| | |
|---|---|
| Posiciones grabadas | sí |
| Eje hacia arriba | `y` |
| Unidades | metros |
| Reflejado para el visor | ninguno |
| Escala de unidad (`scale`: el visor multiplica las posiciones por ella) | 1 |

Esto va al `meta.json` de cada sesión (`axes`) y, cuando la sesión tiene posiciones, al pie de `heat.parquet`, para que el visor de 3DHeat gire y escale las filas por sí solo; ver [Los datos](the-data.md).

## Multijugador {#multiplayer}

- Marcado como jugado en línea (`multiplayer`): **sí**. `games --markdown` muestra esto como "permitido (solo lee lo que publica el juego)".
- Tipo `telemetry`: solo lee lo que el juego o la plataforma entregan (un puerto UDP o la memoria compartida que publica el juego), así que graba también en el juego en línea, además del juego sin conexión. La marca solo decide si la memoria puede leerse alguna vez.
- Memoria: **nunca** la lee este adaptador. Solo los adaptadores `memory` leen memoria, y nunca en un juego marcado como jugado en línea; ver [Fuentes y reglas](sources-and-rules.md).

## Estadísticas registradas {#statistics-recorded}

Claves de estadística que el código de este adaptador asigna por nombre (el `stats` de cada sesión en `meta.json` y la tabla `stats` de `watcher.sqlite`):

`best_lap`, `best_stage`, `distance_km`, `laps`, `race_position`, `stages`, `top_speed_kmh`

Una clave entre llaves se completa en tiempo de ejecución (`score.{team}` es una clave por equipo). Las claves que el código toma de una tabla de campos del juego o de sus propios nombres de estadística no aparecen en esta lista; "Qué se graba" de arriba las nombra.

## Completitud {#completeness}

El watcher sigue la [regla de conversión](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md) de 3DHeat: lo que trae la fuente se lee o se guarda, nunca se descarta. Además de las filas, cada paquete, página, línea o respuesta que recibe el adaptador se guarda entero en `heat.raw.parquet` de la sesión (columnas `time`, `ms`, `type`, `used`, `payload`, `text`, y cualquier campo guardado por nombre; `used` marca lo que también se volvió filas), y `selfCheck.completeness` de `meta.json` cuenta cada `type`: `lost` es 0.

**Se lee**

- filas a 10 Hz desde la página de física: posición (media de los puntos de contacto de los neumáticos), velocidad, marcha, acelerador, freno, guiñada/cabeceo/alabeo (rad), rpm, dirección (tal como la tiene la página); inicio de sesión con la pista y el coche de la página estática; vueltas, posición en carrera

**Se guarda en bruto**

- cada página entera (toda la región de memoria, no solo los bytes decodificados) cada vez que cambian sus bytes, en la lectura de 10 Hz del watcher: `acpmf_physics`, `acpmf_graphics`, `acpmf_static`. Una relectura byte a byte igual a la anterior se cuenta en `unchanged_reads` de meta.json y no se guarda otra vez
- todo lo que se decodifica solo para los archivos de vuelta (`decoders/kunos.py`: deslizamiento, carga, presión, temperaturas, caída, suspensión, puntos de contacto, temperaturas de freno, relación y ángulo de deslizamiento por rueda; velocidad mundial y local, velocidad angular, ayudas) está en esas páginas

**No disponible**

- posiciones de otros coches: las páginas describen solo el coche del jugador (la página de gráficos de ACC tiene ids y coordenadas de otros coches en algunas versiones, guardados en la página en bruto sin decodificar)
- los ticks de física entre lecturas del watcher: el juego reescribe la página a su ritmo de física (hasta 333 Hz) y el watcher lee 10 veces por segundo

**Tamaño**: unos 150-300 MB por hora antes de comprimir (una región de 4 KB por página con hasta 10 cambios por segundo); las páginas están casi llenas de ceros y zstd deja una pequeña fracción

## Verificado {#verified}

La decodificación es la del grabador de vueltas de gamecapture (probada con páginas sintéticas); el adaptador, probado con memoria compartida construida en la prueba a partir del formato documentado; sin probar contra el juego

## Fuente {#source}

[heat3d_watch/adapters/racing.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/racing.py)

<!-- Generated from the adapter by tools/gen_game_pages.py; change the adapter and run it again rather than editing this page. -->
