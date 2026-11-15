---
title: "Assetto Corsa Rally (datos en vivo)"
nav_order: 5
lang: "es"
source: game-assetto-corsa-rally.md
source_hash: "09b8a6d66e31"
nav_exclude: true
search_exclude: true
---
# Assetto Corsa Rally (datos en vivo) {#assetto-corsa-rally-live-data}

Mientras juegas a Assetto Corsa Rally, el watcher guarda los datos que el propio juego envía, para que luego puedas verlos en un mapa del visor de 3DHeat.

*Detalles técnicos: adaptador `assetto-corsa-rally`, tipo [`telemetry`](sources-and-rules.md); se ejecuta mientras `acr.exe`, `ACR-Win64-Shipping.exe`, `AssettoCorsaRally.exe` o `acrally-Win64-Shipping.exe` está en marcha y busca datos nuevos cada 0,1 s.*

## Qué se graba {#what-is-recorded}

- la posición del coche propio (XYZ en el mundo, m: media de los puntos de contacto de los neumáticos) 10 veces por segundo, con velocidad, marcha, acelerador y freno
- inicio y fin de la sesión, con la pista y el coche que indica el juego
- tramos: uno termina donde el coche se detiene después, con el tiempo que tardó
- teletransportes (de vuelta a boxes, un reinicio): `teleport` donde estaba el coche, `spawn` donde está ahora
- vueltas, mejor vuelta, distancia, velocidad máxima

## De dónde sale {#where-it-comes-from}

memoria compartida Local\acpmf_physics, Local\acpmf_static (las mismas páginas que AC y ACC)

## Cómo activarlo {#how-to-switch-it-on}

No hace falta activar nada: el watcher lee la fuente tal como la entrega el juego o la plataforma.

## Cómo funciona {#how-it-works}

La telemetría propia de los juegos de carreras: Forza, los juegos de Assetto Corsa, los juegos de rally y BeamNG, grabada como trazados, vueltas y tramos.

Todos estos juegos publican su telemetría a propósito, para paneles y para
simuladores de movimiento; no se inyecta nada y no se lee nada que el juego no entregue. La
decodificación no se escribe dos veces: son los grabadores de vueltas de gamecapture, que están en
`heat3d_capture/telemetry` de 3DHeat GameCapture, copiados a `heat3d_watch/decoders` (probados allí con paquetes creados a partir
de los formatos publicados). Este módulo convierte sus fotogramas en las filas del watcher:
la posición del coche varias veces por segundo con su velocidad, marcha y pedales,
un evento por vuelta o tramo, y los números que anota el piloto: vueltas, mejor vuelta,
distancia y velocidad máxima.

#### Forza (Horizon 4/5/6, Motorsport) {#forza-horizon-456-motorsport}

UDP "Data Out", que se activa en el HUD y en los ajustes de juego del propio juego, hacia
127.0.0.1 puerto 5300, formato Dash. Un paquete por tick de simulación; el desplazamiento
del bloque del panel se encuentra a partir de los paquetes (`forza.detect_layout`). Metros del
mundo, Y hacia arriba; el mundo es zurdo y se dibuja tal como llega, igual que lo hace el
grabador de vueltas (documentación "Data Out" de Forza Motorsport y de Forza Horizon).
El juego envía a un solo puerto, y FH Companion y otras aplicaciones Data Out escuchan
en ese mismo. Dos programas no pueden compartirlo: en Windows, el socket enlazado
a 127.0.0.1 recibe los paquetes y el enlazado a todas las direcciones en el mismo
puerto no recibe ninguno, sea cual sea el que llegó primero. Por eso el watcher espera un poco
tras arrancar el juego antes de tomar el puerto, nunca lo quita a una aplicación que
lo tiene, y lo suelta en cuanto otra aplicación empieza a escuchar en él.
Mientras tiene el puerto, reenvía cada paquete sin cambios a
127.0.0.1:5301: pon el campo de puerto de FH Companion (su pestaña de telemetría) en 5301 y
ambos graban.

#### Todo lo que se guarda {#everything-kept}

Las filas son unas pocas por segundo; los juegos envían muchos más datos. Cada paquete UDP que
llega (en los menús, entre vueltas, los que ningún decodificador lee) se guarda completo
en `heat.raw.parquet` de la sesión, bajo su formato (`dash-horizon`,
`session_update`, `extradata3`, `H3D1`, ...), y cada página de memoria compartida
(toda la asignación, no solo los bytes decodificados) cada vez que cambia, bajo
el nombre de su asignación (`acpmf_physics`, ...). `used` marca lo que también se convirtió en
filas; `selfCheck.completeness` de `meta.json` cuenta cada tipo (regla del convertidor de 3DHeat).

El mismo módulo también sirve para: [Assetto Corsa (datos en vivo)](game-assetto-corsa.md), [Assetto Corsa Competizione (datos en vivo)](game-assetto-corsa-competizione.md), [Assetto Corsa EVO (datos en vivo)](game-assetto-corsa-evo.md), [BeamNG.drive (datos en vivo)](game-beamng.md), [DiRT Rally 2.0 (datos en vivo)](game-dirt-rally-2.md), [EA SPORTS WRC (datos en vivo)](game-ea-wrc.md), [Forza Horizon 4 (datos en vivo)](game-forza-horizon-4.md), [Forza Horizon 5 (datos en vivo)](game-forza-horizon-5.md), [Forza Horizon 6 (datos en vivo)](game-forza-horizon-6.md), [Forza Motorsport (datos en vivo)](game-forza-motorsport.md), [Richard Burns Rally (datos en vivo)](game-richard-burns-rally.md).

## Posiciones y ejes {#positions-and-axes}

| | |
|---|---|
| Posiciones grabadas | sí |
| Eje hacia arriba | `y` |
| Unidades | metros |
| Reflejado para el visor | ninguno |
| Escala de unidades (`scale`: el visor multiplica las posiciones por ella) | 1 |

Esto va a `meta.json` (`axes`) de cada sesión y, cuando la sesión tiene posiciones, al pie de `heat.parquet`, así que el visor de 3DHeat gira y escala las filas por sí mismo; mira [Los datos](the-data.md).

## Multijugador {#multiplayer}

- Marcado como jugado en línea (`multiplayer`): **sí**. `games --markdown` lo muestra como "permitido (solo lee lo que publica el juego)".
- Tipo `telemetry`: solo lee lo que el juego o la plataforma entregan (un puerto UDP o memoria compartida que publica el juego), así que graba también en línea, igual que sin conexión; la marca solo decide si se puede leer la memoria.
- Memoria: este adaptador **nunca** la lee. Solo los adaptadores `memory` leen memoria, y nunca en un juego marcado como jugado en línea; mira [Fuentes y reglas](sources-and-rules.md).

## Estadísticas que se graban {#statistics-recorded}

Claves de estadística que el código de este adaptador asigna por nombre (el `stats` de cada sesión en `meta.json` y la tabla `stats` de `watcher.sqlite`):

`best_lap`, `best_stage`, `distance_km`, `laps`, `race_position`, `stages`, `top_speed_kmh`

Una clave entre llaves se completa en tiempo de ejecución (`score.{team}` es una clave por equipo). Las claves que el código toma de una tabla de campos del juego o de sus nombres de estadística no aparecen en esta lista; "Qué se graba" más arriba las nombra.

## Completitud {#completeness}

El watcher sigue la [regla del convertidor](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md) de 3DHeat: lo que la fuente contiene se lee o se guarda, nunca se descarta. Además de las filas, cada paquete, página, línea o respuesta que recibe el adaptador se guarda completo en `heat.raw.parquet` de la sesión (columnas `time`, `ms`, `type`, `used`, `payload`, `text`, y cualquier campo guardado por nombre; `used` marca lo que también se convirtió en filas), y `selfCheck.completeness` de `meta.json` cuenta cada `type`; `lost` es 0.

**Se lee**

- filas a 10 Hz de la página de física: posición (media de los puntos de contacto de los neumáticos), velocidad, marcha, acelerador, freno, yaw/pitch/roll (rad), rpm, dirección (tal como la tiene la página); inicio de sesión con la pista y el coche de la página estática; vueltas, posición en carrera

**Se guarda en bruto**

- cada página completa (toda la región de memoria, no solo los bytes decodificados) cada vez que cambian sus bytes, en las lecturas de 10 Hz del watcher: `acpmf_physics`, `acpmf_static`; una relectura byte a byte igual a la anterior se cuenta en `unchanged_reads` de meta.json y no se guarda otra vez
- todo lo decodificado solo para los archivos de vuelta (`decoders/kunos.py`: deslizamiento por rueda, carga, presión, temperaturas, caída, suspensión, puntos de contacto, temperaturas de freno, relación y ángulo de deslizamiento; velocidad mundial y local, velocidad angular, ayudas) está en esas páginas

**No disponible**

- posiciones de otros coches: las páginas describen solo el coche del jugador (la página gráfica de ACC tiene identificadores y coordenadas de otros coches en algunas versiones, guardadas en la página en bruto, sin decodificar)
- ticks de física entre las lecturas del watcher: el juego reescribe la página a su frecuencia de física (hasta 333 Hz) y el watcher lee 10 veces por segundo
- un reloj de tramo o el tiempo de tramo del juego: AC Rally no publica página gráfica; los tramos terminan donde se detiene el coche

**Tamaño**: unos 150-300 MB por hora antes de comprimir (una región de 4 KB por página con hasta 10 cambios por segundo); las páginas son sobre todo ceros y zstd guarda una pequeña fracción

## Verificado {#verified}

la decodificación es la del grabador de vueltas de gamecapture (probada con páginas sintéticas); el adaptador probado con memoria compartida creada en la prueba a partir del formato documentado; sin probar contra el juego; el nombre del ejecutable no está confirmado

## Fuente {#source}

[heat3d_watch/adapters/racing.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/racing.py)

<!-- Generated from the adapter by tools/gen_game_pages.py; change the adapter and run it again rather than editing this page. -->
