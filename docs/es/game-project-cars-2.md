---
title: "Project CARS 2 (datos en vivo)"
nav_order: 36
lang: "es"
source: game-project-cars-2.md
source_hash: "278eb9594615"
nav_exclude: true
search_exclude: true
---
# Project CARS 2 (datos en vivo) {#project-cars-2-live-data}

Mientras juegas a Project CARS 2, el watcher guarda los datos que el propio juego envía, para que luego puedas verlos en un mapa del visor de 3DHeat.

*Detalles técnicos: adaptador `project-cars-2`, tipo [`telemetry`](sources-and-rules.md); se ejecuta mientras `pCARS2AVX.exe` o `pCARS2.exe` está en marcha y busca datos nuevos cada 0,1 s.*

## Qué se graba {#what-is-recorded}

- la posición de cada coche (XYZ en el mundo, m) 10 veces por segundo, por nombre del piloto, con el coche propio marcado, con velocidad y posición en carrera; marcha, acelerador y freno del coche propio
- inicio de sesión con la pista que indica el juego; vueltas por coche con su tiempo de vuelta; llegadas; paradas en boxes propias
- teletransportes (de vuelta a boxes, un reinicio): `teleport` donde estaba el coche, `spawn` donde está ahora
- vueltas propias, mejor vuelta, posición en carrera, distancia, velocidad máxima
- la página de memoria compartida completa del juego en `heat.raw.parquet`, cada vez que cambia

## De dónde sale {#where-it-comes-from}

memoria compartida $pcars2$ (SMS SharedMemory.h)

## Cómo activarlo {#how-to-switch-it-on}

En el juego: Opciones > Sistema > Memoria compartida: "Project CARS 2"

## Cómo funciona {#how-it-works}

Memoria compartida que los juegos de carreras publican para paneles, abierta en solo lectura y
nunca creada.

Varias simulaciones entregan su telemetría como una asignación de archivo de Windows con nombre que el
juego crea y que cualquiera puede leer: las páginas `Local\acpmf_*` de Kunos (Assetto Corsa,
ACC, AC Rally, `Local\acevo_pmf_*` de AC EVO), `Local\IRSDKMemMapFileName` de iRacing,
`$R3E` de RaceRoom, `$pcars2$` de Automobilista 2 / Project CARS 2.

¿Por qué no `mmap.mmap(-1, size, tagname=...)`, que es la forma habitual en Python? Cuando
la asignación todavía no existe, *la crea*, aquí en solo lectura. Un juego
que arranca después abre la asignación del watcher en vez de crear la suya, y
luego no puede escribir en ella, así que su telemetría queda muerta hasta que el watcher la suelta.
El watcher inicia un adaptador en cuanto aparece el proceso del juego, que es
justo el momento en que el juego todavía no ha creado su asignación. Por eso esto abre con
`OpenFileMappingW`, que solo encuentra una asignación existente, la mapea con
`FILE_MAP_READ` e informa de "todavía no está" en otro caso; los adaptadores lo vuelven a intentar
un momento después.

Nada de aquí puede escribir: la vista se mapea en solo lectura y solo se copia
con `ctypes.string_at`.

Aquí se leen también dos juegos; cada coche en pista está en sus páginas.

#### Automobilista 2 / Project CARS 2 - `$pcars2$` {#automobilista-2--project-cars-2---pcars2}

SharedMemory.h de SMS (incluido en la carpeta Support\SharedMemory del juego;
AMS2: Opciones > Sistema > Memoria compartida "Project CARS 2"), `#pragma pack(4)`.
`mParticipantInfo[64]` desde el byte 28, 100 bytes cada uno: mIsActive, mName[64],
mWorldPosition[3] (m, Y hacia arriba), mCurrentLapDistance, mRacePosition,
mLapsCompleted, mCurrentLap, mCurrentSector; mViewedParticipantIndex (20)
es el coche del jugador; por participante, mLastLapTimes (9200), mRaceStates
(9520), mSpeeds (10800); la mejor vuelta del jugador mBestLapTime (6716), mLastLapTime
(6720), mSpeed (6848), mBrake, mThrottle, mGear; mSequenceNumber (7320) es
impar mientras el juego escribe. Los desplazamientos se dedujeron de dos
copias independientes de la cabecera (la copia del propio juego no está instalada
aquí), que coinciden.

Ambas páginas se guardan completas además (docs/converters.md, "Live sources"): la
memoria completa, en cada lectura cuyos bytes difieren de la copia guardada la última vez, en el
archivo bruto de la sesión bajo `type` `r3e` o `pcars2`: cada ranura de piloto y
cada campo de la estructura, también los que aquí no se leen, para que un decodificador posterior
solo necesite el archivo bruto.

El mismo módulo también sirve para: [Automobilista 2 (datos en vivo)](game-automobilista-2.md), [RaceRoom Racing Experience (datos en vivo)](game-raceroom.md).

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

`best_lap`, `distance_km`, `finishes`, `incidents`, `laps`, `pit_stops`, `race_position`, `top_speed_kmh`

Una clave entre llaves se completa en tiempo de ejecución (`score.{team}` es una clave por equipo). Las claves que el código toma de una tabla de campos del juego o de sus nombres de estadística no aparecen en esta lista; "Qué se graba" más arriba las nombra.

## Completitud {#completeness}

El watcher sigue la [regla del convertidor](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md) de 3DHeat: lo que la fuente contiene se lee o se guarda, nunca se descarta. Además de las filas, cada paquete, página, línea o respuesta que recibe el adaptador se guarda completo en `heat.raw.parquet` de la sesión (columnas `time`, `ms`, `type`, `used`, `payload`, `text`, y cualquier campo guardado por nombre; `used` marca lo que también se convirtió en filas), y `selfCheck.completeness` de `meta.json` cuenta cada `type`; `lost` es 0.

**Se lee**

- por participante (hasta 64): activo, nombre, posición en el mundo, posición en carrera, vueltas completadas; su último tiempo de vuelta, estado de carrera y velocidad
- el coche del jugador (mViewedParticipantIndex), estado del juego y de la sesión, ubicación y variante de la pista, mejor y última vuelta, velocidad, freno, acelerador, marcha; mSequenceNumber para saltarse una copia tomada a mitad de escritura
- desplazamientos de dos copias independientes de SharedMemory.h de SMS que coinciden, comprobados con una página construida a partir de ellas en las pruebas; todavía no contra el juego

**Se guarda en bruto**

- `pcars2`: la memoria completa de $pcars2$ (la estructura va bastante más allá de los 11.312 bytes que aquí se leen), en cada lectura cuyos bytes difieren de la copia guardada la última vez: la orientación de cada participante, tiempos de sector, nombres de coche y de clase, modos y banderas de boxes, la física del jugador, neumáticos, suspensión, daños, clima y todo lo que versiones posteriores de Project CARS 2 hayan añadido
- `used` es verdadero para una página leída en filas; falso para una de los menús, en pausa, en una repetición, de otro diseño o tomada a mitad de escritura (`torn` 1); `unchanged_reads` en meta.json cuenta las lecturas que eran byte a byte iguales a la copia guardada antes

**No disponible**

- las entradas y la física de otros participantes: la página solo da el coche visto
- todo mientras la opción de memoria compartida del juego esté desactivada (Project CARS 2 no escribe nada entonces)

**Tamaño**: la memoria mide unos 20 a 30 KB (según la versión del juego), hasta 10 veces por segundo mientras se conduce: aproximadamente 0,7 a 1,1 GB por hora antes de comprimir; zstd reduce las ranuras vacías de participantes y los nombres que no cambian a una fracción (aún no medido en una sesión real)

## Verificado {#verified}

probado con una página construida en la prueba; desplazamientos de dos copias independientes de SharedMemory.h que coinciden, no de la copia que trae el juego; sin probar contra el juego

## Fuente {#source}

[heat3d_watch/adapters/simracing_shm.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/simracing_shm.py)

<!-- Generated from the adapter by tools/gen_game_pages.py; change the adapter and run it again rather than editing this page. -->
