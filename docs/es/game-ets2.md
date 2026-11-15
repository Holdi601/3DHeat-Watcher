---
title: "Euro Truck Simulator 2 (datos en vivo)"
nav_order: 19
lang: es
source: game-ets2.md
source_hash: "537f0daeedbf"
nav_exclude: true
search_exclude: true
---
# Euro Truck Simulator 2 (datos en vivo) {#euro-truck-simulator-2-live-data}

Mientras juegas a Euro Truck Simulator 2, el watcher guarda los datos que el propio juego envía, para que luego puedas verlos en un mapa del visor de 3DHeat.

*Detalles técnicos: adaptador `ets2`, tipo [`telemetry`](sources-and-rules.md); se ejecuta mientras `eurotrucks2.exe` está en marcha y busca datos nuevos cada 0,1 s.*

## Qué se graba {#what-is-recorded}

- la posición del camión en el mundo (x este, y arriba, z sur, m) 10 veces por segundo mientras se mueve, y cada 5 s mientras está parado; rumbo, velocidad, odómetro
- trabajos iniciados (carga, origen, destino), entregados (ingresos, XP, km), cancelados; multas, peajes, transbordadores, trenes, repostajes
- transbordadores, trenes y partidas cargadas cortan la ruta (teleport, spawn)
- distancia, velocidad máxima, entregas, ingresos, XP, multas
- la memoria compartida completa del plugin en `heat.raw.parquet`, cada vez que cambia

## De dónde sale {#where-it-comes-from}

memoria compartida Local\SCSTelemetry escrita por el plugin scs-sdk-plugin de RenCloud (revisión 12) en &lt;juego>\bin\win_x64\plugins

## Cómo activarlo {#how-to-switch-it-on}

instala scs-telemetry.dll (revisión 12) desde github.com/RenCloud/scs-sdk-plugin en &lt;juego>\bin\win_x64\plugins; el juego pide permiso para el SDK una vez en cada inicio

## Cómo funciona {#how-it-works}

Euro Truck Simulator 2 y American Truck Simulator: el SDK de telemetría de SCS, a través del plugin de RenCloud.

SCS publica un SDK de telemetría (<https://modding.scssoft.com/wiki/Documentation/Engine/SDK/Telemetry>)
para los plugins que el jugador pone en `<juego>\bin\win_x64\plugins\`. El juego en sí no
publica nada; el plugin muy usado de <https://github.com/RenCloud/scs-sdk-plugin>
(MIT) copia los canales del SDK a la memoria compartida `Local\SCSTelemetry`
(32 KiB), con el diseño de `scs-telemetry/inc/scs-telemetry-common.hpp`. Esto lee la
revisión 12 de ese diseño (PLUGIN_REVID 12) y nada más: el plugin
escribe su revisión en el desplazamiento 40, y cualquier otra revisión se deja sin leer
antes que leerla mal. Desplazamientos usados (las zonas tal como las marca la cabecera; alineación natural):

```text
   0  bool sdkActive          4  bool paused
  40  u32  telemetry_plugin_revision, version_major, version_minor, game (1 ETS2, 2 ATS)
  64  u32  common_ui.time_abs (minutos en el juego)
 504  i32  truck_i.gear
 640  i32  gameplay_i.jobDeliveredEarnedXp
 948  f32  truck_f.speed (m/s); 952 engineRpm; 1056 truckOdometer (km)
1460  f32  gameplay_f.jobDeliveredDistanceKm
2200  f64  truck_dp.coordinateX/Y/Z (m), rotationX/Y/Z (heading, pitch, roll in turns, 0..1)
2300  char[64] config_s: truckBrand +64, truckName +192, cargo +320, cityDst +448, compDst +576,
      citySrc +704, compSrc +832; 3436 gameplay_s.fineOffence[32]
4200  i64  gameplay_ll: jobCancelledPenalty, jobDeliveredRevenue, fineAmount, tollgatePayAmount,
      ferryPayAmount, trainPayAmount
4300  bool special_b: onJob, jobFinished, jobCancelled, jobDelivered, fined, tollgate, ferry,
      train, refuel, refuelPayed
```

La colocación del camión en el mundo es el sistema de coordenadas de SCS: x este, y arriba, z sur, en metros
(derecho, con y hacia arriba; el visor lo dibuja tal cual). Los transbordadores, los trenes y cargar
una partida mueven el camión sin conducir: la ruta se corta ahí.

La memoria completa (los 32 KiB del plugin: cada zona de arriba y las que no se
leen, como la configuración del camión, las ruedas, el desgaste, los demás canales del camión y
lo que la revisión coloca después del byte 4400, los remolques) se guarda en el archivo bruto de la sesión cada vez que cambia,
`type` `SCSTelemetry` con la `revision` al lado; una página de otra
revisión también, completa en vez de leerla mal.

El mismo módulo también sirve para: [American Truck Simulator (datos en vivo)](game-ats.md).

## Posiciones y ejes {#positions-and-axes}

| | |
|---|---|
| Posiciones grabadas | sí |
| Eje hacia arriba | `y` |
| Unidades | metros (mundo de SCS: x este, y arriba, z sur) |
| Reflejado para el visor | ninguno |
| Escala de unidades (`scale`: el visor multiplica las posiciones por ella) | 1 |

Esto va a `meta.json` (`axes`) de cada sesión y, cuando la sesión tiene posiciones, al pie de `heat.parquet`, así que el visor de 3DHeat gira y escala las filas por sí mismo; mira [Los datos](the-data.md).

## Multijugador {#multiplayer}

- Marcado como jugado en línea (`multiplayer`): **sí**. `games --markdown` lo muestra como "permitido (solo lee lo que publica el juego)".
- Tipo `telemetry`: solo lee lo que el juego o la plataforma entregan (un puerto UDP o memoria compartida que publica el juego), así que graba también en línea, igual que sin conexión; la marca solo decide si se puede leer la memoria.
- Memoria: este adaptador **nunca** la lee. Solo los adaptadores `memory` leen memoria, y nunca en un juego marcado como jugado en línea; mira [Fuentes y reglas](sources-and-rules.md).

## Estadísticas que se graban {#statistics-recorded}

Claves de estadística que el código de este adaptador asigna por nombre (el `stats` de cada sesión en `meta.json` y la tabla `stats` de `watcher.sqlite`):

`deliveries`, `distance_km`, `fines`, `fines_total`, `jobs_cancelled`, `max_speed_kmh`, `refuels`, `revenue`, `tolls_total`, `xp`

Una clave entre llaves se completa en tiempo de ejecución (`score.{team}` es una clave por equipo). Las claves que el código toma de una tabla de campos del juego o de sus nombres de estadística no aparecen en esta lista; "Qué se graba" más arriba las nombra.

## Completitud {#completeness}

El watcher sigue la [regla del convertidor](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md) de 3DHeat: lo que la fuente contiene se lee o se guarda, nunca se descarta. Además de las filas, cada paquete, página, línea o respuesta que recibe el adaptador se guarda completo en `heat.raw.parquet` de la sesión (columnas `time`, `ms`, `type`, `used`, `payload`, `text`, y cualquier campo guardado por nombre; `used` marca lo que también se convirtió en filas), y `selfCheck.completeness` de `meta.json` cuenta cada `type`; `lost` es 0.

**Se lee**

- estado de SDK y de pausa, revisión del plugin, juego y versión, hora en el juego, posición y rumbo del camión en el mundo, velocidad, odómetro, marca y nombre del camión, carga, ciudad y empresa de origen y destino, ingresos del trabajo, XP y distancia, penalización por cancelación, multas y su delito, peajes, transbordadores, trenes, las marcas de eventos especiales (filas, eventos y estadísticas)
- ahora también en las filas de posición: `pitch` y `roll` (grados, a partir de las vueltas del SDK), `gear` y `rpm`
- desplazamientos comprobados con una transcripción campo por campo de la cabecera de la revisión 12 del plugin, cuyos inicios de zona se comprueban en las pruebas; todavía no contra el juego

**Se guarda en bruto**

- `SCSTelemetry`: los 32 KiB completos de la memoria del plugin, en cada lectura cuyos bytes difieren de la copia guardada la última vez (`unchanged_reads` en meta.json cuenta las demás), con la `revision` al lado: cada zona (configuración del camión y del remolque, los canales del camión: pedales, dirección, combustible, AdBlue, presiones, temperaturas, desgaste, luces, ruedas), los vectores de colocación y aceleración, las cadenas de trabajo y de juego, y todo lo que la revisión coloca después del byte 4400 (los remolques); `used` es verdadero mientras el SDK esté activo y la revisión sea 12
- una página de otra revisión del plugin se guarda completa con `used` en falso, en vez de leerla mal

**No disponible**

- todo lo que el plugin no copia del SDK, y todo mientras el plugin no esté instalado: el juego no publica telemetría propia
- otros jugadores con camión en TruckersMP o en convoyes: el SDK solo da el camión del jugador

**Tamaño**: 32 KiB hasta 10 veces por segundo mientras se conduce (cada lectura cambia entonces): unos 1,2 GB por hora antes de comprimir, una copia mientras está en pausa; la mayor parte de la página son ceros y configuración que no cambia, así que zstd la reduce muchas veces (aún no medido en una sesión real)

## Verificado {#verified}

probado con memoria compartida creada a partir del diseño de la cabecera de la revisión 12 del plugin; sin probar contra el juego

## Fuente {#source}

[heat3d_watch/adapters/ets2.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/ets2.py)

<!-- Generated from the adapter by tools/gen_game_pages.py; change the adapter and run it again rather than editing this page. -->
