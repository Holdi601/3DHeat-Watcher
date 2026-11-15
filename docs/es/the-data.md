---
title: Los datos
nav_order: 5
lang: es
source: the-data.md
source_hash: "6150cdc022fc"
nav_exclude: true
search_exclude: true
---
# Los datos {#the-data}

Todas las grabaciones son archivos simples en la carpeta de datos (`%LOCALAPPDATA%\3DHeat\Watcher` salvo que se
cambie, véase [Instalación y ejecución](installing-and-running.md#where-everything-is)). Puedes leerlos, copiarlos o
borrarlos sin el watcher. Un archivo `.jsonl` es texto plano, un evento por línea (lo abre el Bloc de notas); un
archivo `.parquet` es una tabla que abre el visor de 3DHeat (Excel no lo abre: `stats --csv` escribe archivos CSV para
hojas de cálculo).

## Carpetas de sesión {#session-folders}
![una carpeta de sesión](../assets/img/session-folder.svg)


Una **sesión** es una partida con una sola fuente: desde el momento en que el juego dice algo por primera vez hasta
que se detiene (el juego se cierra, termina una partida, se reinicia una conducción o un vuelo; la página de cada
adaptador dice qué inicia y termina sus sesiones). Cada sesión recibe una carpeta:

```text
<data>\sessions\<game>\<YYYY-MM-DD_HH-MM-SS>_<adapter id>\
    events.jsonl
    heat.parquet
    meta.json
```

- `<game>` es el nombre del juego con cada carácter distinto de letras, dígitos, `.`, `_` y `-` sustituido por `-`
  (como máximo 60 caracteres): `EA-SPORTS-F1-25`, `Counter-Strike-2`. Los adaptadores que cubren muchos juegos
  (estadísticas de Steam, Steam Timeline, destacados de NVIDIA) archivan cada sesión bajo el juego al que pertenece.
- La hora es el inicio de la sesión en hora local. Las sesiones que describen el pasado (una repetición convertida
  después de la partida, un archivo de estadísticas de Steam) usan la hora que da el juego o el archivo. A dos sesiones
  que empiezan en el mismo segundo se les añade `_2`, `_3`, ...
- El id de la sesión, en la base de datos de estadísticas, es `<game folder>/<session folder>`.

Una sesión en la que no se grabó nada (el juego estuvo en sus menús, o falló al arrancar) se borra al cerrarse, para
que cada inicio no deje una carpeta vacía.

Algunas sesiones contienen más archivos. Una sesión de demo de Counter-Strike 2 contiene la tabla y el resumen propios
del conversor (`<map>/<match>.parquet`, `<match>.match.json`). Una sesión de iRacing lista los archivos `.ibt` que el
simulador escribió durante la sesión como eventos `telemetry_file`.

## events.jsonl {#eventsjsonl}

`events.jsonl` tiene un objeto JSON por línea, una línea por evento, escrito en el momento en que ocurre el evento. El
archivo es de búfer por línea, así que un fallo, un corte de luz o un proceso terminado no pierde nada de lo ya
escrito; una línea cortada por un fallo se omite al leer el archivo, y todas las líneas anteriores se conservan.

Cada línea tiene las mismas columnas base:

| Columna | Tipo | Qué es |
|---|---|---|
| `time` | número | segundos desde el inicio de la sesión (4 decimales), o el reloj propio del juego cuando el adaptador lo pasa |
| `ms` | entero | hora de reloj, milisegundos Unix |
| `event` | texto | qué pasó: `position`, `spawn`, `death`, `kill`, `lap`, `teleport`, `session_start`, ... |
| `x`, `y`, `z` | número | dónde, en las unidades y ejes propios del juego (véase `axes` en `meta.json`); solo está presente cuando se conocen las tres y son finitas |
| `player` | texto | quién: un nombre, un id, o `me` para la persona que juega (véase [Las filas propias del jugador](#the-players-own-rows)) |
| `team` | texto | su bando, cuando lo dice el juego |
| `session` | texto | la partida, ronda, etapa, vida o vuelo al que pertenece la fila, cuando lo dice el juego |

Cualquier otro campo que informe el juego sigue con su propio nombre (`speed_kmh`, `gear`, `lap_time`, `weapon`,
`victim`, `hero`, ...). Los campos sin valor se omiten, y también los números que no son finitos. Dos líneas
sintéticas:

```json
{"time":12.3456,"ms":1777660501123,"event":"position","x":-412.5,"y":12.1,"z":233.0,"player":"me","session":"1","speed_kmh":187.4,"gear":5}
{"time":15.0,"ms":1777660503667,"event":"lap","x":-380.2,"y":12.0,"z":250.9,"player":"me","session":"1","lap_time":92.418,"lap":3}
```

Las filas sin posición (una línea del feed de eliminaciones, una subida de nivel, un cambio de estadística) se quedan
en `events.jsonl` y cuentan en las estadísticas. Solo las filas con posición pasan a la tabla.

### Las filas propias del jugador {#the-players-own-rows}

Qué filas son de la persona que juega lo dice la fuente, nunca se adivina. Una fila es la propia del jugador cuando

- su `player` es `me`: la mayoría de los adaptadores, cuya fuente es el propio juego del jugador (telemetría del coche
  o avión propio, una integración de estado del juego, un diario);
- lleva `own_car` 1: los juegos de carreras que graban cada coche con el nombre de su piloto (EA SPORTS F1 por el índice
  de coche del jugador del juego, RaceRoom por su propia ranura, Automobilista 2 y Project CARS 2 por el participante
  visto) marcan así el coche del jugador y mantienen el nombre del piloto en `player`;
- su `player` es el `player` de la sesión en `meta.json`: el nombre que la fuente da al jugador: el comandante de Elite
  Dangerous (el diario es siempre del jugador), una línea de repetición de League of Legends con el Riot ID de los
  ajustes.

War Thunder y Rocket League nombran a cada jugador y no dicen cuál eres tú; con tu nombre en el ajuste `player_names`
(véase [Ajustes](installing-and-running.md#settings)) tus filas pasan a ser `me`. [Destacados de NVIDIA](nvidia-highlights.md)
busca un momento exactamente en estas filas.

## heat.parquet {#heatparquet}

Cuando una sesión se cierra, las filas de `events.jsonl` que tienen `x`, `y` y `z` se escriben en `heat.parquet`. Es la
tabla que abre el visor de 3DHeat. Si la sesión no tiene posiciones, no se escribe ninguna tabla.

- Las columnas son `time`, `ms`, `event`, `x`, `y`, `z`, `player`, `team`, `session`, seguidas de cada otro campo en el
  orden en que aparece por primera vez.
- `x`, `y`, `z` y `time` son números en coma flotante de 64 bits, y `ms` es un entero de 64 bits. Una columna adicional
  cuyos valores son todos números es un número en coma flotante de 64 bits; cualquier otra columna es texto con
  codificación de diccionario (los valores que faltan son texto vacío, y las listas u objetos se escriben como texto
  JSON).
- Los metadatos del archivo tienen una clave `heat3d` con las instrucciones de lectura, así que el visor asigna las
  columnas y los ejes por sí mismo (un ejemplo, con la lista `extra` abreviada):

```json
{
  "version": 1,
  "kind": "heat3d-watch",
  "game": "EA SPORTS F1 25",
  "axes": {"up": "y", "flipX": false, "flipY": false, "flipZ": false, "scale": 1.0},
  "columns": {
    "x": "x", "y": "y", "z": "z",
    "time": "time", "timeUnit": "seconds",
    "personId": "player", "teamId": "team", "sessionId": "session",
    "extra": ["event", "speed_kmh", "gear", "lap_time", "lap"]
  }
}
```

`up` es el eje vertical del juego, `flipX`/`flipY`/`flipZ` reflejan un eje para que un mundo de sistema izquierdo no se
dibuje reflejado, y `scale` es la escala de unidades del visor: el visor multiplica cada posición por ella al cargar la
tabla (0.01 convertiría centímetros en metros). Cada adaptador escribe 1 y conserva las unidades propias del juego
—metros en la mayoría, unidades Source (pulgadas) en Counter-Strike 2, unidades Unreal (centímetros) en Rocket
League—, porque un nivel exportado del juego está en esas mismas unidades, y así las filas caen sobre él; las tablas
propias del conversor de CS2 dicen lo mismo. `units` en `meta.json` indica qué es una unidad. La página de cada juego
enumera sus valores bajo "Posiciones y ejes".

Los simuladores de vuelo (DCS World, Microsoft Flight Simulator, X-Plane, las grabaciones Tacview de IL-2) colocan sus
filas sobre la Tierra, y su pie indica dónde, para que el visor pueda poner el mundo real debajo:

```json
"geo": {"lat0": 42.0, "lon0": 42.0, "projection": "tangent-plane", "east": "x", "north": "z", "up": "y"}
```

`lat0`/`lon0` (grados) son el origen del mapa plano en el que están las filas; `east`, `north` y `up` nombran las
columnas que contienen los metros al este y al norte de él y la altitud sobre el nivel del mar. El origen es el primer
punto fijo en X-Plane y MSFS, el punto de referencia de la grabación en IL-2, y el origen fijo del teatro en DCS (el
primer punto fijo redondeado a grados enteros en un teatro que el watcher no conoce). Una tabla sin lugar en la Tierra
no tiene clave `geo`, y lo demás del pie es igual en cualquier caso.

`heat.parquet` siempre se puede reconstruir a partir de `events.jsonl` con `python -m heat3d_watch table <session folder>`
(véase [Comandos](commands.md#table)). Esto es útil cuando faltaba `pyarrow` mientras se grababa la sesión.

## meta.json {#metajson}

`meta.json` resume la sesión. Se escribe cuando la sesión se abre, como máximo cada 30 segundos mientras llegan eventos o
estadísticas, y cuando la sesión se cierra. Las estadísticas solo se guardan en memoria entre esas escrituras, así que
un fallo puede perder como mucho el último medio minuto de ellas.

```json
{
  "format": "heat3d-watch-session",
  "version": 1,
  "watcher": "1.0.2",
  "game": "EA SPORTS F1 25",
  "adapter": "f1-25",
  "source": "UDP telemetry 127.0.0.1:20777 (...)",
  "multiplayer": true,
  "started": "2026-05-01T20:15:03",
  "ended": "2026-05-01T21:02:11",
  "seconds": 2828.0,
  "axes": {"up": "y", "flip_x": false, "flip_y": false, "flip_z": false, "scale": 1.0, "units": "metres"},
  "events": {"position": 52110, "lap": 412, "teleport": 3},
  "positions": 52530,
  "stats": {"laps": 20, "best_lap": 91.874, "distance_km": 106.3, "race_position": 4},
  "track": "..."
}
```

Una sesión cuya fuente nombra al jugador (véase [Las filas propias del jugador](#the-players-own-rows)) también tiene
`"player"`: el nombre que llevan las filas propias del jugador. Una sesión sobre la Tierra (los simuladores de vuelo)
también tiene `"geo": {"lat0": .., "lon0": ..}`, el origen que repite el `geo` de su pie.

- `started` / `ended`: hora local con precisión de segundo; `ended` es `null` mientras la sesión está en marcha.
- `events`: cuántas veces ocurrió cada evento, del más frecuente al menos. `positions` es el número de filas con posición.
- `stats`: los números de la sesión. Un adaptador fija cada uno, le suma, o guarda el máximo o el mínimo.
- Lo demás que el adaptador sabe de la sesión va en el nivel superior: la pista, el mapa, la misión, el id de la partida,
  el id de aplicación de Steam, el archivo de repetición, el perfil de memoria y la versión. Una sesión terminada por
  recuperación tiene `"recovered": true`.

## watcher.sqlite {#watchersqlite}

`watcher.sqlite` es la base de datos de estadísticas. Se añade una fila por cada sesión cuando se cierra. Las tres tablas
son simples, así que cualquier herramienta SQL, cuaderno u hoja de cálculo puede leerlas sin el watcher:

```sql
CREATE TABLE sessions (
  id TEXT PRIMARY KEY,          -- <game folder>/<session folder>
  game TEXT NOT NULL,
  adapter TEXT NOT NULL,
  started REAL NOT NULL,        -- Unix seconds
  ended REAL,                   -- Unix seconds
  seconds REAL,
  folder TEXT NOT NULL,         -- the session folder's full path
  events INTEGER NOT NULL DEFAULT 0,
  positions INTEGER NOT NULL DEFAULT 0,
  multiplayer INTEGER NOT NULL DEFAULT 0,
  source TEXT
);
CREATE TABLE events (           -- per session, how many times each event happened
  session TEXT NOT NULL REFERENCES sessions(id) ON DELETE CASCADE,
  event TEXT NOT NULL,
  count INTEGER NOT NULL,
  PRIMARY KEY (session, event)
);
CREATE TABLE stats (            -- per session, every number the game reported or the watcher counted
  session TEXT NOT NULL REFERENCES sessions(id) ON DELETE CASCADE,
  key TEXT NOT NULL,
  value REAL,                   -- numbers
  text TEXT,                    -- everything else (a map name, a result, a hero)
  PRIMARY KEY (session, key)
);
```

Volver a grabar una sesión (recuperación, una repetición convertida de nuevo) reemplaza sus filas. `multiplayer` es la
marca del adaptador (algunos adaptadores la fijan por sesión, por ejemplo DCS según la misión), no una comprobación de si
estabas en línea. Un valor verdadero/falso en `stats` se guarda como texto.

Una consulta de ejemplo: la mejor vuelta por juego en todas las sesiones (cuanto menor, mejor):

```sql
SELECT s.game, MIN(t.value) AS best_lap
FROM stats t JOIN sessions s ON s.id = t.session
WHERE t.key = 'best_lap'
GROUP BY s.game;
```

`python -m heat3d_watch stats` muestra totales de estas tablas (véase [Comandos](commands.md#stats)); su columna `best`
es el valor más bajo para los tiempos guardados como mejor y para los puestos, y el más alto para el resto.

## Recuperación tras un fallo {#recovery-after-a-crash}

Cuando arranca `run`, busca las sesiones que dejó abiertas un watcher anterior: un `meta.json` sin `ended` y un
`events.jsonl` con al menos una línea. Termina cada una así:

- los recuentos de eventos y el número de posiciones se vuelven a contar desde `events.jsonl`, omitiendo una línea
  cortada;
- el final es la hora de reloj de la última línea (`ms`);
- las estadísticas son las de la última escritura de `meta.json` (como máximo de 30 segundos de antigüedad);
- se añade `"recovered": true`, se escribe `heat.parquet`, y la sesión pasa a `watcher.sqlite`.

El registro dice "finished N session(s) left open by an earlier run". El archivo de bloqueo evita que un segundo
watcher "recupere" las sesiones de uno que sigue en marcha.

## Exportar a CSV {#csv-export}
![stats --csv y table](../assets/img/csv-and-table.svg)


```bash
python -m heat3d_watch stats --csv out
```

Esto escribe `out\sessions.csv`, `out\events.csv` y `out\stats.csv`. Cada archivo es una tabla completa de
`watcher.sqlite`, con una fila de encabezado, en UTF-8. Los tiempos son segundos Unix, como en la base de datos.
`--game` no limita la exportación; se escribe cada sesión.

## Abrir una sesión en el visor de 3DHeat {#opening-a-session-in-the-3dheat-viewer}

El visor: [github.com/Holdi601/3DHeat](https://github.com/Holdi601/3DHeat), documentación
[holdi601.github.io/3DHeat](https://holdi601.github.io/3DHeat/); su página
[contenedor `.3dheat`](https://holdi601.github.io/3DHeat/container.html) describe el formato de un archivo por partida
que pueden escribir los conversores de repeticiones.

Abre el `heat.parquet` de una sesión en el visor de 3DHeat. El pie indica al visor qué columna es la posición, el tiempo,
el jugador, el equipo y la sesión, y cuál es el sentido de arriba, así que no hay que asignar nada a mano. Las posiciones
están en las coordenadas propias del mundo del juego. Dibujadas sobre un nivel exportado con las otras herramientas de
3DHeat (por ejemplo desde [3DHeat GameFiles](https://github.com/Holdi601/3DHeat-GameFiles)), caen donde ocurrieron.

- **Los mapas de calor** usan cada fila con posición, filtrada por `event`, `player`, `team` o `session` como cualquier
  otra columna.
- **El mapa de calor de líneas** dibuja una línea desde cada fila de un jugador hasta la siguiente, y en la reproducción
  cada jugador es un punto que se mueve por la ruta con una estela detrás. El panel **Rutas** del visor elige, a partir de
  la columna `event`, qué eventos **inician** una ruta y cuáles la **terminan**. El watcher escribe los eventos límite
  como filas con posición, así que se pueden elegir ahí:
  - inicios: `spawn`, `respawn`, `session_start`. Un inicio cierra la ruta que estaba abierta sin dibujar una línea hasta
    el lugar nuevo.
  - finales: `death`, `finish`, `session_end` y `teleport`. La línea llega hasta la propia fila final, que es donde el
    jugador murió, se detuvo o fue retirado.

  Un salto —llegar a un lugar sin viajar hasta allí— son dos filas: `teleport` en el lugar **dejado**, y un inicio en el
  lugar **al que se llegó**, justo después. Los adaptadores de carreras escriben una cada vez que el coche se movió más
  lejos de lo que podía haber conducido (un rebobinado o flashback, un reinicio a la carretera, vuelta a boxes, un viaje
  rápido), con `spawn` en la llegada (`respawn` para el reinicio de BeamNG); la fila `teleport` lleva la llegada como
  `to_x`, `to_y`, `to_z` y la distancia como `metres`, y la fila de inicio `after: "teleport"`. Los adaptadores de camiones
  hacen lo mismo con un ferry, un tren o una partida cargada, y los de vuelo con un salto que ningún avión podría haber
  hecho. Así que con `teleport` entre los finales y `spawn` entre los inicios —lo que el visor sugiere por sí mismo— una
  ruta termina donde dejó el salto y la siguiente empieza donde llegó, y ninguna línea cruza el mapa. Una ruta nunca cruza
  un cambio de la columna `session`. Una fila de posición se escribe varias veces por segundo (10 Hz para la mayoría de la
  telemetría), lo que da una línea suave.
- La columna `session` divide una partida en sus rondas, etapas, vidas o cuerpos (Elite Dangerous separa así las filas de
  la galaxia y las de la superficie de cada planeta). Elige una en el visor para mirar solo esa parte.

Lo que hace el visor con las filas —filtros, colores, reproducción— lo describe la documentación propia del visor. Las
sesiones de demos de Counter-Strike 2 se abren mediante el `<map>/<match>.parquet` y el `<match>.match.json` del
conversor, en las pestañas **Mapa de calor** y **Partida** del visor. Las posiciones de iRacing vienen de los archivos
`.ibt` listados en la sesión, que el visor lee por sí mismo.
