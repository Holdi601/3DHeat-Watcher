---
title: "X-Plane (datos en vivo)"
nav_order: 50
lang: "es"
source: game-xplane.md
source_hash: "4e7246cce10c"
nav_exclude: true
search_exclude: true
---
# X-Plane (datos en vivo) {#x-plane-live-data}

Mientras juegas a X-Plane, el watcher guarda los datos que el propio juego envía hacia fuera, para que después puedas verlos en un mapa del visor de 3DHeat.

*Detalles técnicos: adaptador `xplane`, tipo [`telemetry`](sources-and-rules.md); se ejecuta mientras `X-Plane.exe` está en marcha y busca datos nuevos cada 0,1 s.*

## Qué se graba {#what-is-recorded}

- tu propia posición a 10 Hz (latitud/longitud/altitud como metros al este/arriba/norte desde la primera posición fijada; lat/lon/alt guardadas como columnas)
- actitud, velocidad indicada y verdadera, velocidad sobre el suelo, Mach, velocidad vertical, AoA, resbalamiento, rumbo magnético, AGL, g (normal, axial, lateral), velocidades y tasas de rotación, flaps, aerofrenos, gases, en tierra
- pesos (total, combustible, carga), palanca del tren, piloto automático, rpm del motor y N1, tiempo y fecha del simulador, pausa, velocidad de simulación, repetición, temperatura exterior y presión a nivel del mar (X-Plane 12) una vez por segundo
- despegues, aterrizajes, accidentes, reinicios de vuelo (session_start/session_end por vuelo)
- tiempo de vuelo, tiempo en el aire, distancia, altitud máxima, g máxima, aterrizajes
- cada respuesta que envía X-Plane guardada entera en heat.raw.parquet

## De dónde viene {#where-it-comes-from}

la interfaz UDP de X-Plane en 127.0.0.1:49000 (datarefs RREF y posición RPOS, respondidos al watcher)

## Cómo activarlo {#how-to-switch-it-on}

X-Plane 12: Settings > Network > Accept incoming connections (X-Plane 11 responde por defecto)

## Cómo funciona {#how-it-works}

X-Plane 11 y 12: la interfaz UDP propia del simulador, en el puerto 49000.

X-Plane responde a quien pregunte en 127.0.0.1:49000, a la velocidad pedida, a la dirección y el puerto de donde llegó la petición (documento "Exchanging Data with X-Plane" de X-Plane, incluido en `<X-Plane>\Instructions\`):

```text
RREF  "RREF\0" + int32 freq + int32 index + char[400] dataref path (413 bytes).
      The answer is "RREF" + one internal byte + (int32 index, float32 value)
      pairs; freq 0 stops it.
RPOS  "RPOS\0" + the rate as a NUL-terminated ASCII string ("10\0"). The
      answer is "RPOS" + one internal byte + double lon, lat, elevation (m
      MSL) + float AGL (m), pitch, true heading, roll (deg), vx east, vy up,
      vz south (m/s), P, Q, R (rad/s), tightly packed.
```

RPOS da la latitud y la longitud como dobles (RREF solo como flotantes, a medio metro de distancia), así que RPOS es el que maneja la posición; RREF trae el resto y hace de respaldo cuando RPOS no llega. Datarefs (nombres como en `Resources\plugins\DataRefs.txt` de X-Plane 12, <https://developer.x-plane.com/datarefs/>):

```text
sim/flightmodel/position/latitude, longitude, elevation  deg, deg, m MSL
sim/flightmodel/position/true_theta, true_phi, true_psi  pitch, roll, true heading (deg)
sim/flightmodel/position/indicated_airspeed              knots
sim/flightmodel/position/groundspeed                     m/s
sim/flightmodel/position/y_agl                           m above ground
sim/flightmodel/forces/g_nrml                            g, normal to the wings
sim/flightmodel/failures/onground_any                    1 on the ground
sim/flightmodel2/misc/has_crashed                        1 crashed
sim/time/total_flight_time_sec                           since the flight was reset
```

El resto del vuelo llega a la misma velocidad (velocidad verdadera, velocidad vertical, AoA, resbalamiento, rumbo magnético, Mach, g axial y lateral, tasas de rotación, flaps, aerofrenos, gases: `DATAREFS`), y el estado más lento del avión una vez por segundo (pesos, palanca del tren, servos del piloto automático, tiempo del simulador, pausa y velocidad, clima: `SLOW_DATAREFS`). Cada datagrama también se guarda entero en el archivo bruto de la sesión, y meta.json indica el dataref de cada índice RREF.

X-Plane 12 solo acepta esto con Settings > Network > "Accept incoming connections" activado. Las posiciones van a un mapa plano alrededor de la primera posición fijada de la sesión (`Tangent`): x al este, z al norte en metros, y la altitud sobre el nivel del mar. Así un vuelo horizontal se queda horizontal aunque llegue lejos, algo que un plano tangente real haría caer con la curvatura de la Tierra. El origen del mapa es el `geo` de la sesión: meta.json y el pie de la tabla lo guardan, para que el visor pueda poner el mundo real bajo el vuelo.

Este módulo también recoge lo que comparten los demás simuladores de vuelo: el mapa plano, el registro de vuelos (despegues, aterrizajes, accidentes, distancia), el socket UDP y la lista de la biblioteca de Steam.

## Posiciones y ejes {#positions-and-axes}

| | |
|---|---|
| Posiciones grabadas | sí |
| Eje hacia arriba | `y` |
| Unidades | metros (este, altitud, norte desde la primera posición fijada) |
| Reflejado para el visor | `z` |
| Escala de unidad (`scale`: el visor multiplica las posiciones por ella) | 1 |

Esto va al `meta.json` de cada sesión (`axes`) y, cuando la sesión tiene posiciones, al pie de `heat.parquet`, para que el visor de 3DHeat gire y escale las filas por sí solo; ver [Los datos](the-data.md).

## Multijugador {#multiplayer}

- Marcado como jugado en línea (`multiplayer`): **no**. `games --markdown` muestra esto como "single-player".
- Tipo `telemetry`: solo lee lo que el juego o la plataforma entregan (un puerto UDP o la memoria compartida que publica el juego), así que graba también en el juego en línea, además del juego sin conexión. La marca solo decide si la memoria puede leerse alguna vez.
- Memoria: **nunca** la lee este adaptador. Solo los adaptadores `memory` leen memoria, y nunca en un juego marcado como jugado en línea; ver [Fuentes y reglas](sources-and-rules.md).

## Estadísticas registradas {#statistics-recorded}

Claves de estadística que el código de este adaptador asigna por nombre (el `stats` de cada sesión en `meta.json` y la tabla `stats` de `watcher.sqlite`):

`airborne_time`, `bad_packets`, `crashes`, `distance_km`, `flight_time`, `max_altitude_m`, `max_g`, `{event}s`

Una clave entre llaves se completa en tiempo de ejecución (`score.{team}` es una clave por equipo). Las claves que el código toma de una tabla de campos del juego o de sus propios nombres de estadística no aparecen en esta lista; "Qué se graba" de arriba las nombra.

## Completitud {#completeness}

El watcher sigue la [regla de conversión](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md) de 3DHeat: lo que trae la fuente se lee o se guarda, nunca se descarta. Además de las filas, cada paquete, página, línea o respuesta que recibe el adaptador se guarda entero en `heat.raw.parquet` de la sesión (columnas `time`, `ms`, `type`, `used`, `payload`, `text`, y cualquier campo guardado por nombre; `used` marca lo que también se volvió filas), y `selfCheck.completeness` de `meta.json` cuenta cada `type`: `lost` es 0.

**Se lee**

- RPOS (10 Hz): longitud, latitud, elevación, AGL, cabeceo, rumbo verdadero, alabeo, velocidad (este, arriba, sur) y tasas de rotación P/Q/R, todo en las filas
- RREF (10 Hz): los 27 datarefs de `DATAREFS` (posición, actitud, IAS, velocidad sobre el suelo, TAS, velocidad vertical, AoA, resbalamiento, rumbo magnético, Mach, g normal/axial/lateral, tasas de rotación, flaps, aerofrenos, gases, AGL, accidentado, en tierra, tiempo de vuelo), en las filas
- RREF (1 Hz): los 20 datarefs de `SLOW_DATAREFS` (pesos, palanca del tren, servos del piloto automático, tiempo y fecha del simulador, pausa, velocidad de simulación, repetición, número de motores, rpm de los motores 1-4, N1 de los motores 1-2, temperatura del aire exterior, presión a nivel del mar), en las filas tal como se recibieron por última vez

**Se guarda en bruto**

- cada datagrama entero como `payload`, bajo su cabecera de cuatro letras: `RREF` y `RPOS` (usados cuando la consulta generó una fila; en los menús, sin posición, no generan ninguna), y cualquier otra cosa que X-Plane envíe al puerto del watcher, bajo su propia cabecera o como `unknown`; `requests` de meta.json indica qué dataref es cada índice RREF, así que los payloads se leen sin este módulo

**No disponible**

- cualquier otro dataref (X-Plane tiene miles): RREF envía solo lo que se pide, una suscripción por cada uno; la lista pide el vuelo, el estado del avión y el tiempo del simulador. Más detalle de cabina (radios, luces, cada indicador de motor, fallos) multiplicaría las peticiones
- el nombre del avión y su tipo ICAO: son datarefs de matriz de bytes, que RREF envía como un flotante por carácter
- otros aviones (IA y multijugador): los datarefs sim/multiplayer/position no se piden
- la salida DATA (Settings > Data Output): envía a una dirección fija elegida en el simulador, no a quien pregunta; RREF y RPOS cubren lo que lee el watcher

**Tamaño**: unos 17 MB por hora antes de zstd (RREF y RPOS a 10 Hz, de unos 220 y 70 bytes más un marco cada uno, y el RREF lento una vez por segundo), si X-Plane envía los valores de cada consulta en un paquete, como hace; zstd reduce los flotantes varias veces

## Verificado {#verified}

Probado contra un X-Plane falso que responde a RREF/RPOS según 'Exchanging Data with X-Plane' de X-Plane 12; nombres de datarefs comprobados con DataRefs.txt de X-Plane 12; sin probar contra el simulador en marcha

## Fuente {#source}

[heat3d_watch/adapters/xplane.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/xplane.py)

<!-- Generated from the adapter by tools/gen_game_pages.py; change the adapter and run it again rather than editing this page. -->
