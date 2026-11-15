---
title: "EA SPORTS F1 24 (datos en vivo)"
nav_order: 15
lang: es
source: game-f1-24.md
source_hash: "a189298930fc"
nav_exclude: true
search_exclude: true
---
# EA SPORTS F1 24 (datos en vivo) {#ea-sports-f1-24-live-data}

Mientras juegas EA SPORTS F1 24, el watcher guarda los datos que el propio juego envía, para que puedas verlos más tarde en un mapa del visor de 3DHeat.

*Detalles técnicos: adaptador `f1-24`, tipo [`telemetry`](sources-and-rules.md); se ejecuta mientras `F1_24.exe` está en marcha y busca datos nuevos cada 0,1 s.*

## Qué se graba {#what-is-recorded}

- la posición (XYZ del mundo, m) de cada coche a 10 Hz, por nombre de piloto, equipo, con el coche propio marcado (`own_car` 1, a partir del índice del coche del jugador), con velocidad, marcha, acelerador, freno, dirección, rpm, DRS, guiñada, cabeceo, alabeo (grados) y fuerzas g
- vueltas por coche con el tiempo de vuelta y la posición en carrera; llegadas y abandonos
- los eventos de carrera del juego: inicio y fin de sesión, vuelta rápida, penalizaciones, adelantamientos, colisiones, coche de seguridad, bandera roja, luces de salida, bandera a cuadros, ganador, rebobinados (`teleport` donde estaba el coche, `spawn` adonde volvió)
- circuito, tipo de sesión, vueltas y pilotos de cada sesión
- vueltas propias, mejor vuelta, posición en carrera y en parrilla, paradas en boxes, penalizaciones, adelantamientos, colisiones, distancia, velocidad máxima
- cada paquete que envía el juego, completo, en `heat.raw.parquet` - también los que no se convierten en filas

## De dónde viene {#where-it-comes-from}

telemetría UDP 127.0.0.1:20777 (Documentos\My Games\F1 24\hardwaresettings\hardware_settings_config.xml)

## Cómo activarlo {#how-to-switch-it-on}

En el juego: Ajustes > Ajustes de telemetría > Telemetría UDP activada, IP 127.0.0.1, puerto 20777 - o `python -m heat3d_watch setup f1-24 --apply` (edita hardware_settings_config.xml, con copia de seguridad previa; el juego debe estar cerrado). Mientras otra aplicación tenga el 20777, el watcher deja el puerto a esa aplicación

Escribe el comando en una terminal abierta en la carpeta del watcher (véase [Antes de empezar](before-you-start.md)). Si falla, la última línea dice por qué; [Instalación y uso](installing-and-running.md) recoge las causas habituales.

`python -m heat3d_watch setup f1-24` muestra los archivos que cambiaría; `python -m heat3d_watch setup f1-24 --apply` los cambia y guarda el original como `<archivo>.heat3d-backup` (véase [Comandos](commands.md#setup)). Escribe `f1-24: changed: ...` por cada cambio, o `f1-24: nothing to change` si ya está activado.

## Cómo funciona {#how-it-works}

EA SPORTS F1 23, F1 24 y F1 25: la telemetría UDP oficial, cada coche en pista.

El juego la envía por sí mismo (Ajustes > Ajustes de telemetría, o
`Documents/My Games/<F1 xx>/hardwaresettings/hardware_settings_config.xml`,
`<udp enabled="true" ip="127.0.0.1" port="20777" sendRate="20" format="2025" ...>`).
Little-endian, empaquetado, una cabecera de 29 bytes en cada paquete (la misma en los formatos 2023,
2024 y 2025):

```text
uint16 packetFormat, uint8 gameYear, gameMajorVersion, gameMinorVersion,
packetVersion, packetId, uint64 sessionUID, float sessionTime,
uint32 frameIdentifier, overallFrameIdentifier, uint8 playerCarIndex,
secondaryPlayerCarIndex
```

Lo que se lee, por id de paquete:

```text
0 Motion        CarMotionData[22], 60 bytes each: world position x y z
                (metres; Y is up), world velocity, forward and right
                vectors (int16 / 32767), g-forces, yaw pitch roll
1 Session       weather, temperatures, total laps, track length, session
                type, track id, ... network game
2 Lap Data      LapData[22]: last lap time, lap distance, race position,
                current lap number, pit stops, penalties, grid position,
                driver and result status. 50 bytes per car in 2023; 57 in
                2024 and 2025, which added the minutes parts of the deltas
                and the speed trap.
3 Event         a four-letter code and a union of details: SSTA SEND FTLP
                RTMT DRSE DRSD TMPT CHQF RCWN PENA SPTP STLG LGOT DTSV SGSV
                FLBK BUTN RDFL OVTK SCAR COLL
4 Participants  ParticipantData[22]: AI or human, driver, team, race
                number, name (48 bytes in 2023 and 2024, 32 in 2025; 58,
                60 and 57 bytes per car)
6 Car Telemetry CarTelemetryData[22], 60 bytes: speed km/h, throttle,
                steer, brake, clutch, gear, rpm, DRS ...
```

Cada paquete también se guarda completo, tal como llegó, en el archivo auxiliar sin procesar de la sesión
(`heat.raw.parquet`, `type` el nombre del paquete - `motion`, `car_status` ... -
con `format`, `packet_id`, `frame` y `session_uid`): los leídos arriba y los que nada lee aún: 5 Car Setups, 7 Car Status, 8 Final Classification, 9 Lobby
Info, 10 Car Damage, 11 Session History, 12 Tyre Sets, 13 Motion Ex, 14 Time
Trial, 15 Lap Positions, cualquier id posterior, y los paquetes en un formato que este módulo no lee. Así, un decodificador posterior solo necesita el archivo auxiliar.

La posición de cada coche está en el paquete Motion - también en línea, cuando el juego la entrega (solo el combustible, la ERS, los daños y los juegos de neumáticos quedan reservados para los jugadores con "Tu telemetría" restringida). Cada coche se registra a unos 10 Hz bajo su nombre de piloto ("car N" hasta que llegan los nombres), el equipo por nombre, y el coche del jugador marcado como `own`.

Fuentes: "F1 25 UDP Specification" de EA (forums.ea.com, centro de información de los juegos F1),
las especificaciones de F1 23 y F1 24; las mismas tablas reflejadas en
MacManley/f1-25-udp (MIT). Los paquetes de las pruebas se construyen a partir de estos diseños.

El mismo módulo también sirve a: [EA SPORTS F1 23 (datos en vivo)](game-f1-23.md), [EA SPORTS F1 25 (datos en vivo)](game-f1-25.md).

## Posiciones y ejes {#positions-and-axes}

| | |
|---|---|
| Posiciones registradas | sí |
| Eje vertical | `y` |
| Unidades | metros |
| Invertido para el visor | ninguno |
| Escala de unidad (`scale`: el visor multiplica las posiciones por ella) | 1 |

Estos valores van al `meta.json` de cada sesión (`axes`) y, cuando la sesión tiene posiciones, al pie de `heat.parquet`, así que el visor de 3DHeat gira y escala las filas por sí mismo; véase [Los datos](the-data.md).

## Multijugador {#multiplayer}

- Marcado como jugado en línea (`multiplayer`): **sí**. `games --markdown` lo muestra como "permitido (lee solo lo que publica el juego)".
- Tipo `telemetry`: lee solo lo que el juego o la plataforma entregan (un puerto UDP o memoria compartida que publica el juego), así que graba también en el juego en línea; la marca solo decide si la memoria puede leerse alguna vez.
- Memoria: **nunca** la lee este adaptador. Solo los adaptadores `memory` leen memoria, y nunca en un juego marcado como jugado en línea; véase [Fuentes y reglas](sources-and-rules.md).

## Estadísticas registradas {#statistics-recorded}

Claves de estadística que el código de este adaptador asigna por nombre (el `stats` de cada sesión en `meta.json` y la tabla `stats` de `watcher.sqlite`):

`best_lap`, `collisions`, `distance_km`, `fastest_laps`, `finishes`, `flashbacks`, `grid_position`, `laps`, `overtaken`, `overtakes`, `penalties`, `penalty_seconds`, `pit_stops`, `race_position`, `sessions`, `top_speed_kmh`, `wins`

Una clave entre llaves se completa en tiempo de ejecución (`score.{team}` es una clave por equipo). Las claves que el código toma de una tabla de campos del juego o de sus propios nombres de estadística no están en esta lista; "Qué se graba" arriba las nombra.

## Completitud {#completeness}

El watcher sigue la [regla de conversión](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md) de 3DHeat: lo que trae la fuente se lee o se guarda, nunca se descarta. Además de las filas, cada paquete, página, línea o respuesta que recibe el adaptador se guarda completo en `heat.raw.parquet` de la sesión (columnas `time`, `ms`, `type`, `used`, `payload`, `text`, y los campos guardados por nombre; `used` marca lo que también se convirtió en filas), y `selfCheck.completeness` de `meta.json` cuenta cada `type` - `lost` es 0.

**Leído**

- 0 Motion: la posición y velocidad del mundo de cada coche, y ahora también guiñada, cabeceo, alabeo (grados, a partir de los radianes de la especificación) y las fuerzas g lateral, longitudinal y vertical, en las filas de posición de cada coche
- 1 Session: circuito, tipo de sesión, vueltas totales, longitud del circuito, en línea o no (`sessions` de meta.json)
- 2 Lap Data: último tiempo de vuelta, número de vuelta, posición en carrera y en parrilla, paradas en boxes, penalizaciones, estado del resultado (vueltas, llegadas, abandonos, estadísticas)
- 3 Event: cada código excepto BUTN como fila propia, con sus detalles
- 4 Participants: nombres de pilotos, equipos, número de coches activos (`player` y `team` de las filas, `drivers` de meta.json)
- 6 Car Telemetry: velocidad, marcha, acelerador, freno, y ahora también dirección (-1..1), rpm y DRS, en las filas de posición de cada coche
- comprobado con las especificaciones UDP publicadas por EA para los formatos 2023, 2024 y 2025 (tamaños de paquete verificados en las pruebas); todavía no contra el juego

**Guardado sin procesar**

- cada paquete completo en `heat.raw.parquet`, `payload` el datagrama, `type` el nombre de su id: `motion`, `session`, `lap_data`, `event`, `participants`, `car_setups`, `car_telemetry`, `car_status`, `final_classification`, `lobby_info`, `car_damage`, `session_history`, `tyre_sets`, `motion_ex`, `time_trial`, `lap_positions` (`packet <n>` para un id que las especificaciones aún no listan); columnas `format` (2023/2024/2025), `packet_id`, `frame`, `session_uid`
- `used` es verdadero para los paquetes leídos arriba (Motion, Session, Lap Data, Participants, Car Telemetry, y los códigos de Event distintos de BUTN); el resto - ajustes de coche, estado del coche (combustible, ERS, compuesto y edad de neumáticos, banderas), clasificación final, lobby, daños del coche, historial de sesión (cada tiempo de vuelta y sector por coche), juegos de neumáticos, motion ex (suspensión del coche propio, velocidades de rueda, velocidad local, velocidad y aceleración angular), contrarreloj, posiciones de vuelta, eventos de botón BUTN - se guardan para un decodificador posterior
- `format <año>`: un paquete de un formato anterior a 2023 (otra disposición de cabecera), completo; `short`: un datagrama más corto que la cabecera de 29 bytes, completo

**No disponible**

- el combustible, la ERS, los daños y los juegos de neumáticos de otros jugadores en línea cuando su "Tu telemetría" está restringida: el juego envía ceros para ellos
- paquetes enviados mientras el watcher no está en marcha, o mientras otra aplicación tiene el puerto 20777: UDP no lo guarda el juego

**Tamaño**: a una frecuencia de envío de 60 Hz, cada paquete ocupa unos 0,38 MB/s (Motion, Lap Data, Car Telemetry, Car Status y Motion Ex a 60 Hz, Session History y Tyre Sets a 20/s, Car Damage a 10/s, Session y Car Setups a 2/s) más unos 0,03 MB/s de cabeceras de elementos: unos 1,5 GB por hora de conducción antes de comprimir, unos 0,55 GB a los 20 Hz por defecto; zstd lo reduce a una fracción (las plazas de coche vacías y los valores repetidos se comprimen bien; aún no medido en una sesión real)

## Verificado {#verified}

probado con paquetes en los formatos 2023, 2024 y 2025 construidos a partir de la especificación publicada por EA, enviados por UDP; sin probar contra el juego

## Fuente {#source}

[heat3d_watch/adapters/f1.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/f1.py)

<!-- Generado a partir del adaptador por tools/gen_game_pages.py; cambia el adaptador y vuelve a ejecutarlo en lugar de editar esta página. -->
