---
title: "RaceRoom Racing Experience (datos en vivo)"
nav_order: 38
lang: es
source: game-raceroom.md
source_hash: "ffd0499ca059"
nav_exclude: true
search_exclude: true
---
# RaceRoom Racing Experience (datos en vivo) {#raceroom-racing-experience-live-data}

Mientras juegas a RaceRoom Racing Experience, el watcher guarda los datos que el propio juego envía, para que luego puedas verlos en un mapa del visor de 3DHeat.

*Detalles técnicos: adaptador `raceroom`, tipo [`telemetry`](sources-and-rules.md); se ejecuta mientras `RRRE64.exe` o `RRRE.exe` está en marcha y busca datos nuevos cada 0,1 s.*

## Qué se graba {#what-is-recorded}

- la posición de cada coche (XYZ en el mundo, m) 10 veces por segundo, por nombre del piloto, con el coche propio marcado, con velocidad y posición en carrera; marcha, acelerador y freno del coche propio
- inicio de sesión con la pista que indica el juego; vueltas por coche con su tiempo de vuelta; llegadas; paradas en boxes propias
- teletransportes (de vuelta a boxes, un reinicio): `teleport` donde estaba el coche, `spawn` donde está ahora
- vueltas propias, mejor vuelta, posición en carrera, distancia, velocidad máxima
- la página de memoria compartida completa del juego en `heat.raw.parquet`, cada vez que cambia
- puntos de incidente propios

## De dónde sale {#where-it-comes-from}

memoria compartida $R3E (r3e.h de Sector3, versión 3)

## Cómo activarlo {#how-to-switch-it-on}

No hace falta activar nada: el watcher lee la fuente tal como la entrega el juego o la plataforma.

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

#### RaceRoom Racing Experience - `$R3E` {#raceroom-racing-experience---r3e}

r3e.h de Sector3 (github.com/sector3studios/r3e-api, sample-c/src/r3e.h,
versión 3.6), `#pragma pack(1)`. La cabecera indica dónde empiezan los pilotos
y cuánto ocupa cada uno (`all_drivers_offset`, `driver_data_size`), así que la
parte de cada piloto (nombre, ranura, posición, posición en el mundo (float x y z, m),
vueltas completadas, tiempo de vuelta actual, estado de llegada, calle de boxes, velocidad) se lee
con esos datos. Los campos propios del jugador (mejor y anterior vuelta, posición en carrera,
puntos de incidente, marcha, pedales, nombres de pista y de trazado) se leen en sus
desplazamientos de la 3.6 solo cuando `all_drivers_offset` es el 2008 que ese diseño le asigna.
Se toma Y como arriba; la cabecera no lo dice.

El mismo módulo también sirve para: [Automobilista 2 (datos en vivo)](game-automobilista-2.md), [Project CARS 2 (datos en vivo)](game-project-cars-2.md).

## Posiciones y ejes {#positions-and-axes}

| | |
|---|---|
| Posiciones grabadas | sí |
| Eje hacia arriba | `y` |
| Unidades | metros; se supone Y hacia arriba (r3e.h no lo dice) |
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

- por ranura de piloto (según el tamaño y el desplazamiento que indica la cabecera): nombre, ranura, estado de llegada, posición, posición en el mundo, vueltas completadas, tiempo de vuelta actual, calle de boxes, velocidad
- los campos propios del jugador, solo cuando la página es del diseño r3e.h 3.6: nombres de pista y de trazado, tipo de sesión, posición en carrera, mejor y anterior vuelta, puntos de incidente, marcha, acelerador, freno, la ranura del jugador
- desplazamientos sacados de r3e.h 3.6 de Sector3 y comprobados con una página construida a partir de él en las pruebas; todavía no contra el juego

**Se guarda en bruto**

- `r3e`: la memoria completa de $R3E, en cada lectura cuyos bytes difieren de la copia guardada la última vez: cada campo de r3e.h: la física del jugador (orientación, velocidades, aceleraciones, fuerzas g), motor, combustible, neumáticos, frenos, daños, banderas, menú de boxes, tiempos de sector, y los datos completos de cada ranura de piloto (clase, modelo, equipo, tiempos de sector, diferencias, penalizaciones, neumáticos)
- `used` es verdadero para una página leída en filas; falso para una de los menús, en pausa, en una repetición, de otro diseño o tomada a mitad de escritura (`torn` 1); `unchanged_reads` en meta.json cuenta las lecturas que eran byte a byte iguales a la copia guardada antes

**No disponible**

- las entradas y la física de otros pilotos: la página solo da las del propio jugador
- los tiempos de vuelta exactos de otros coches: una ranura solo tiene su tiempo de vuelta en curso, así que una vuelta es el último tiempo en curso visto (con una precisión de unos 0,1 s)
- los campos propios del jugador en un diseño distinto de 3.6: se guardan en bruto, sin leer, hasta comprobarlos

**Tamaño**: la página mide 44 KB (r3e.h 3.6; la asignación se redondea a páginas completas de 4 KB), hasta 10 veces por segundo mientras se conduce: unos 1,6 GB por hora antes de comprimir; las ranuras de pilotos vacías y los campos que no cambian se comprimen muy bien con zstd (aún no medido en una sesión real)

## Verificado {#verified}

probado con una página construida en la prueba a partir de r3e.h 3.6 (desplazamientos sacados de la cabecera oficial); sin probar contra el juego; los tiempos de vuelta de otros coches son el último tiempo de vuelta en curso visto (con una precisión de unos 0,1 s)

## Fuente {#source}

[heat3d_watch/adapters/simracing_shm.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/simracing_shm.py)

<!-- Generated from the adapter by tools/gen_game_pages.py; change the adapter and run it again rather than editing this page. -->
