---
title: "iRacing (datos en vivo)"
nav_order: 28
lang: "es"
source: game-iracing.md
source_hash: "894d9bc4081f"
nav_exclude: true
search_exclude: true
---
# iRacing (datos en vivo) {#iracing-live-data}

Mientras juegas a iRacing, el watcher guarda los datos que el propio juego envía hacia fuera, para que después los veas como estadísticas y una línea de tiempo.

*Detalles técnicos: adaptador `iracing`, tipo [`telemetry`](sources-and-rules.md); se ejecuta mientras `iRacingSim64DX11.exe` o `iRacingSim64.exe` está en marcha y busca datos nuevos cada 0,1 s.*

## Qué se graba {#what-is-recorded}

- la conducción a 5 Hz sin posición (iRacing no da posición en vivo): velocidad, marcha, acelerador, freno, vuelta, parte de la vuelta, posición en carrera y en clase, incidentes
- inicio de sesión, subir y bajar del coche, entrada y salida del pit lane, vueltas con su tiempo, incidentes con sus puntos, bandera de cuadros, llegada
- los archivos de telemetría .ibt escritos durante la sesión (latitud, longitud, altitud: el visor los lee)
- vueltas, mejor vuelta, incidentes, posición en carrera, paradas en boxes, distancia y velocidad máxima
- toda la memoria compartida en `heat.raw.parquet`: cabecera, cabeceras de variables, información de sesión y cada línea de telemetría leída

## De dónde viene {#where-it-comes-from}

memoria compartida Local\IRSDKMemMapFileName (el SDK de iRacing); archivos .ibt en %USERPROFILE%\Documents\iRacing\telemetry

## Cómo activarlo {#how-to-switch-it-on}

Nada para los datos en vivo. Para las posiciones: graba la telemetría en el coche (Alt+L) o pon irsdkLog=1 en app.ini

## Cómo funciona {#how-it-works}

iRacing, en vivo: la memoria compartida del SDK de iRacing, leída de forma nativa.

iRacing publica su telemetría para las apps en un mapeo de archivo con nombre, `Local\IRSDKMemMapFileName`, que el simulador crea mientras funciona (y señala `Local\IRSDKDataValidEvent` en cada actualización; eso no hace falta aquí, porque el watcher lee diez veces por segundo). El formato es el de `irsdk_defines.h` del SDK, que también sigue pyirsdk (MIT); aquí se escribe de nuevo a partir de esos datos:

```text
irsdk_header (little-endian int32s)
    0 ver, 4 status (bit 0: connected), 8 tickRate,
    12 sessionInfoUpdate, 16 sessionInfoLen, 20 sessionInfoOffset,
    24 numVars, 28 varHeaderOffset, 32 numBuf, 36 bufLen, 40 pad[2],
    48 varBuf[4]: { tickCount, bufOffset, pad[2] } (16 bytes each)
irsdk_varHeader (144 bytes, numVars of them at varHeaderOffset)
    0 type (0 char, 1 bool, 2 int, 3 bitfield, 4 float, 5 double),
    4 offset (into a line), 8 count, 12 countAsTime + 3 pad,
    16 name[32], 48 desc[64], 112 unit[32]
session info: YAML text at sessionInfoOffset, rewritten when
    sessionInfoUpdate changes (track, sessions, drivers)
```

El simulador escribe `numBuf` líneas en orden circular; la más reciente es la de mayor tickCount, y una línea se vuelve a tomar si su tickCount cambió mientras se copiaba.

Los datos en vivo no tienen posición mundial: latitud, longitud y altitud solo están en los archivos `.ibt` que iRacing graba en `Documents\iRacing\telemetry` (Alt+L en el coche, o `irsdkLog=1`), que el visor de 3DHeat lee por su cuenta. Así que aquí se graba la conducción como eventos sin coordenadas (velocidad, vuelta, parte de la vuelta recorrida, posición en carrera, incidentes), además de vueltas, incidentes, paradas en boxes y la bandera de cuadros; y al final, los archivos `.ibt` escritos durante la sesión como eventos `telemetry_file`, para que el visor los abra.

Junto a las filas se guarda todo el mapa de memoria en el archivo bruto de la sesión (`heat.raw.parquet`): la parte fija de la cabecera (`header`, cada vez que cambia), las cabeceras de variables (`var_headers`, completas, y como JSON en `text`, cada vez que cambia el formato), el YAML de información de sesión (`session_info`, su texto cada vez que se mueve `sessionInfoUpdate`) y la línea de telemetría más reciente (`telemetry`, cada variable de ella, en cada lectura que encuentra un tick nuevo). Las cabeceras de variables y una línea bastan para que un decodificador posterior lea cualquier variable.

Fuente: el SDK de iRacing (irsdk_defines.h, documentación del foro "iRacing SDK"); kutu/pyirsdk (MIT) para confirmar los desplazamientos.

## Posiciones y ejes {#positions-and-axes}

| | |
|---|---|
| Posiciones grabadas | no |
| Eje hacia arriba | `y` |
| Unidades | sin posiciones en vivo; los archivos .ibt traen latitud/longitud/altitud |
| Reflejado para el visor | ninguno |
| Escala de unidad (`scale`: el visor multiplica las posiciones por ella) | 1 |

Esto va al `meta.json` de cada sesión (`axes`) y, cuando la sesión tiene posiciones, al pie de `heat.parquet`, para que el visor de 3DHeat gire y escale las filas por sí solo; ver [Los datos](the-data.md).

## Multijugador {#multiplayer}

- Marcado como jugado en línea (`multiplayer`): **sí**. `games --markdown` muestra esto como "permitido (solo lee lo que publica el juego)".
- Tipo `telemetry`: solo lee lo que el juego o la plataforma entregan (un puerto UDP o la memoria compartida que publica el juego), así que graba también en el juego en línea, además del juego sin conexión. La marca solo decide si la memoria puede leerse alguna vez.
- Memoria: **nunca** la lee este adaptador. Solo los adaptadores `memory` leen memoria, y nunca en un juego marcado como jugado en línea; ver [Fuentes y reglas](sources-and-rules.md).

## Estadísticas registradas {#statistics-recorded}

Claves de estadística que el código de este adaptador asigna por nombre (el `stats` de cada sesión en `meta.json` y la tabla `stats` de `watcher.sqlite`):

`best_lap`, `distance_km`, `finishes`, `incidents`, `laps`, `pit_stops`, `race_position`, `sessions`, `top_speed_kmh`

Una clave entre llaves se completa en tiempo de ejecución (`score.{team}` es una clave por equipo). Las claves que el código toma de una tabla de campos del juego o de sus propios nombres de estadística no aparecen en esta lista; "Qué se graba" de arriba las nombra.

## Completitud {#completeness}

El watcher sigue la [regla de conversión](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md) de 3DHeat: lo que trae la fuente se lee o se guarda, nunca se descarta. Además de las filas, cada paquete, página, línea o respuesta que recibe el adaptador se guarda entero en `heat.raw.parquet` de la sesión (columnas `time`, `ms`, `type`, `used`, `payload`, `text`, y cualquier campo guardado por nombre; `used` marca lo que también se volvió filas), y `selfCheck.completeness` de `meta.json` cuenta cada `type`: `lost` es 0.

**Se lee**

- de la línea de telemetría más reciente: tiempo de sesión, número, estado e id, en pista, repetición, vuelta, vueltas completadas, parte y metros de la vuelta, última y mejor vuelta, velocidad, marcha, acelerador, freno, rpm, pit road, superficie de la pista, posición en carrera y en clase, tu número de incidentes (las filas `driving` a 5 Hz y los eventos)
- ahora también en las filas `driving`: `steering_angle`, `yaw`, `yaw_north`, `pitch`, `roll` (grados, a partir de los radianes del simulador; solo cuando la cabecera de la variable indica la unidad rad), `fuel_l` (unidad l), `lat_accel` y `lon_accel` (unidad m/s^2)
- del YAML de información de sesión: el índice de tu coche, la pista y su configuración, los tipos de sesión, el nombre, coche, equipo y número de cada piloto (filas session_start, meta.json)
- comprobado con un bloque construido a partir de irsdk_defines.h en las pruebas; todavía no contra el simulador

**Se guarda en bruto**

- `telemetry`: la línea más reciente entera, cada variable que publica el simulador (los arrays CarIdx de todos los coches, neumáticos, suspensión, los arrays de alta frecuencia `_ST` donde el simulador los tiene ...), en cada lectura que encuentra un tick nuevo; `tick` es el contador de ticks del simulador; `used` es falso mientras se reproduce una repetición
- `var_headers`: las cabeceras de variables enteras (144 bytes cada una) y, en `text`, como JSON (nombre, tipo, desplazamiento, cuenta, unidad, descripción), cada vez que cambia el formato: basta para leer cualquier variable de cada línea guardada
- `session_info`: el YAML entero cada vez que se mueve su contador de actualización (fin de semana, sesiones y resultados, pilotos, puesta a punto del coche, radio, listas de cámaras), `update` es el contador
- `header`: la cabecera de 112 bytes entera cada vez que cambia (versión, estado, frecuencia de ticks, desplazamientos, los ticks de las líneas)

**No disponible**

- una posición mundial en vivo: la memoria compartida no la tiene; latitud, longitud y altitud solo están en los archivos .ibt (con el registro activado), que el visor lee; el watcher nombra los que se escribieron durante la sesión
- los ticks entre dos lecturas: el simulador escribe 60 líneas por segundo en 3 o 4 huecos y el watcher lee 10 veces por segundo, así que la mayoría de los ticks se sobrescriben antes de poder leerse; el archivo .ibt tiene cada tick cuando el registro está activado

**Tamaño**: una línea de telemetría ocupa unos pocos KB (unos 5 a 10 KB con los arrays de todos los coches), se guarda hasta 10 veces por segundo, más la cabecera (112 bytes) con la misma frecuencia y el YAML de sesión (decenas de KB) cuando cambia: unos 0,2 a 0,4 GB por hora en pista antes de comprimir; zstd lo reduce a una fracción (aún no medido en una sesión real)

## Verificado {#verified}

Probado con un bloque de memoria compartida construido en la prueba a partir del formato irsdk; sin probar contra el simulador

## Fuente {#source}

[heat3d_watch/adapters/iracing.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/iracing.py)

<!-- Generated from the adapter by tools/gen_game_pages.py; change the adapter and run it again rather than editing this page. -->
