---
title: "Microsoft Flight Simulator 2024 (datos en vivo)"
nav_order: 32
lang: "es"
source: game-msfs2024.md
source_hash: "011c18a23252"
nav_exclude: true
search_exclude: true
---
# Microsoft Flight Simulator 2024 (datos en vivo) {#microsoft-flight-simulator-2024-live-data}

Mientras juegas Microsoft Flight Simulator 2024, el watcher guarda los datos que el propio juego envía, para que puedas verlos más tarde en un mapa del visor de 3DHeat.

*Detalles técnicos: adaptador `msfs2024`, tipo [`telemetry`](sources-and-rules.md); se ejecuta mientras `FlightSimulator2024.exe` está en marcha y busca datos nuevos cada 0,1 s.*

## Qué se graba {#what-is-recorded}

- la posición de la aeronave propia en cada fotograma del simulador, tomada a 10 Hz (latitud/longitud/altitud como metros al este/arriba/norte del primer punto fijo; lat/lon/alt guardadas como columnas)
- actitud, velocidad indicada, velocidad sobre el suelo, AGL, g, en el suelo; velocidad verdadera, Mach, velocidad vertical, AoA, resbalamiento, rumbo magnético, velocidades del cuerpo, aceleraciones y velocidades de giro a unos 10 Hz
- peso, combustible, flaps, tren, spoilers, freno de estacionamiento, piloto automático, acelerador, rpm, meteorología, velocidad de simulación, hora y estado de la cámara una vez por segundo; el título de la aeronave y su tipo, modelo e id de ATC
- despegues, aterrizajes, accidentes, vuelos iniciados y terminados (session_start/session_end)
- tiempo de vuelo, tiempo en el aire, distancia, altitud máxima, g máxima, aterrizajes
- cada mensaje de SimConnect guardado completo en heat.raw.parquet

## De dónde viene {#where-it-comes-from}

SimConnect a través de la SimConnect.dll propia del jugador (la carpeta del simulador, o %MSFS2024_SDK%\SimConnect SDK\lib)

## Cómo activarlo {#how-to-switch-it-on}

nada en el simulador; necesita SimConnect.dll - MSFS 2020 la tiene en su carpeta, los jugadores de MSFS 2024 instalan el SDK de MSFS 2024

## Cómo funciona {#how-it-works}

Microsoft Flight Simulator 2020 y 2024: SimConnect, a través de la SimConnect.dll propia del jugador.

SimConnect es la API cliente publicada del simulador (documentación del SDK:
<https://docs.flightsimulator.com/html/Programming_Tools/SimConnect/SimConnect_SDK.htm>,
<https://docs.flightsimulator.com/msfs2024/html/6_Programming_APIs/SimConnect/SimConnect_SDK.htm>).
El watcher no incluye la DLL: carga la que viene con el simulador o con su SDK - MSFS 2020 pone `SimConnect.dll` en su carpeta de instalación; MSFS 2024 en Steam solo trae la suya interna, así que los jugadores de 2024 instalan el SDK de MSFS 2024
(`<SDK>\SimConnect SDK\lib\SimConnect.dll`; el simulador de 2024 también acepta clientes de 2020).

Las llamadas, de SimConnect.h, devuelven todas un HRESULT (0 = S_OK):

```text
SimConnect_Open(HANDLE*, LPCSTR name, HWND, DWORD, HANDLE, DWORD config)
SimConnect_AddToDataDefinition(HANDLE, DWORD define, LPCSTR var, LPCSTR units,
                               SIMCONNECT_DATATYPE (FLOAT64 = 4), float epsilon, DWORD datum)
SimConnect_RequestDataOnSimObject(HANDLE, DWORD request, DWORD define, DWORD object (0 = user),
                                  SIMCONNECT_PERIOD (SIM_FRAME = 3), DWORD flags, DWORD origin,
                                  DWORD interval, DWORD limit)
SimConnect_SubscribeToSystemEvent(HANDLE, DWORD event, LPCSTR name)
SimConnect_GetNextDispatch(HANDLE, SIMCONNECT_RECV**, DWORD*)   E_FAIL when nothing waits
SimConnect_Close(HANDLE)
```

Cada mensaje empieza con SIMCONNECT_RECV {DWORD dwSize, dwVersion, dwID}
(#pragma pack 1). Los que se leen aquí:

```text
1  EXCEPTION       dwException, dwSendID, dwIndex
2  OPEN            szApplicationName[256], then version DWORDs
3  QUIT            the sim is closing
4  EVENT           uGroupID, uEventID, dwData
6  EVENT_FILENAME  EVENT + szFileName[260], dwFlags        (FlightLoaded)
8  SIMOBJECT_DATA  dwRequestID, dwObjectID, dwDefineID, dwFlags, dwentrynumber,
                   dwoutof, dwDefineCount, then the values (FLOAT64 each here)
```

Variables de simulación (unidades pedidas para que no haga falta conversión): PLANE
LATITUDE/LONGITUDE (grados), PLANE ALTITUDE (metros, sobre el nivel del mar), PLANE
ALT ABOVE GROUND (metros), PLANE PITCH/BANK DEGREES y PLANE HEADING DEGREES
TRUE (grados; los signos propios de SimConnect - morro arriba es cabeceo negativo), AIRSPEED
INDICATED y GROUND VELOCITY (nudos), G FORCE (gforce), SIM ON GROUND (booleano).
Eventos de sistema: SimStart, SimStop, Crashed, FlightLoaded, AircraftLoaded,
Pause, CrashReset, PositionChanged, FlightSaved, Sim.

Tres definiciones de datos más piden el resto del vuelo (`MOTION_VARS`,
cada sexto fotograma de simulación), el estado más lento de la aeronave (`STATE_VARS`, una vez por
segundo) y sus nombres (`NAME_VARS`, cadenas de 256 bytes, cuando cambian); cada una es su propia
definición, así que una variable que una versión del simulador no conoce cuesta solo ese bloque. Cada mensaje se guarda completo en el archivo auxiliar sin procesar de la sesión.

Las posiciones van al mismo mapa plano que X-Plane (x este, y altitud, z norte, en metros desde el primer punto fijo de la sesión); ese punto es el `geo` de la sesión, en meta.json y al pie de la tabla.

El mismo módulo también sirve a: [Microsoft Flight Simulator 2020 (datos en vivo)](game-msfs2020.md).

## Posiciones y ejes {#positions-and-axes}

| | |
|---|---|
| Posiciones registradas | sí |
| Eje vertical | `y` |
| Unidades | metros (este, altitud, norte desde el primer punto fijo) |
| Invertido para el visor | `z` |
| Escala de unidad (`scale`: el visor multiplica las posiciones por ella) | 1 |

Estos valores van al `meta.json` de cada sesión (`axes`) y, cuando la sesión tiene posiciones, al pie de `heat.parquet`, así que el visor de 3DHeat gira y escala las filas por sí mismo; véase [Los datos](the-data.md).

## Multijugador {#multiplayer}

- Marcado como jugado en línea (`multiplayer`): **sí**. `games --markdown` lo muestra como "permitido (lee solo lo que publica el juego)".
- Tipo `telemetry`: lee solo lo que el juego o la plataforma entregan (un puerto UDP o memoria compartida que publica el juego), así que graba también en el juego en línea; la marca solo decide si la memoria puede leerse alguna vez.
- Memoria: **nunca** la lee este adaptador. Solo los adaptadores `memory` leen memoria, y nunca en un juego marcado como jugado en línea; véase [Fuentes y reglas](sources-and-rules.md).

## Estadísticas registradas {#statistics-recorded}

Claves de estadística que el código de este adaptador asigna por nombre (el `stats` de cada sesión en `meta.json` y la tabla `stats` de `watcher.sqlite`):

`airborne_time`, `bad_packets`, `crashes`, `distance_km`, `flight_time`, `max_altitude_m`, `max_g`, `{event}s`

Una clave entre llaves se completa en tiempo de ejecución (`score.{team}` es una clave por equipo). Las claves que el código toma de una tabla de campos del juego o de sus propios nombres de estadística no están en esta lista; "Qué se graba" arriba las nombra.

## Completitud {#completeness}

El watcher sigue la [regla de conversión](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md) de 3DHeat: lo que trae la fuente se lee o se guarda, nunca se descarta. Además de las filas, cada paquete, página, línea o respuesta que recibe el adaptador se guarda completo en `heat.raw.parquet` de la sesión (columnas `time`, `ms`, `type`, `used`, `payload`, `text`, y los campos guardados por nombre; `used` marca lo que también se convirtió en filas), y `selfCheck.completeness` de `meta.json` cuenta cada `type` - `lost` es 0.

**Leído**

- SIMOBJECT_DATA de la definición de posición (en cada fotograma del simulador): latitud, longitud, altitud, AGL, cabeceo, alabeo, rumbo verdadero, IAS, velocidad sobre el suelo, g, en el suelo - el último fotograma del sondeo como fila, y cada fotograma para tomas de contacto y despegues
- SIMOBJECT_DATA de la definición de movimiento (unos 10 Hz: TAS, Mach, velocidad vertical, AoA, resbalamiento, rumbo magnético, velocidad del cuerpo, aceleración y velocidad de giro en tres ejes) y de la definición de estado (1 Hz: pesos, combustible, flaps, tren, spoilers, freno de estacionamiento, piloto automático, motores, acelerador y rpm, temperatura exterior, viento, presión a nivel del mar, velocidad de simulación, hora zulu y local, estado de la cámara) en las filas tal como se recibieron por última vez
- SIMOBJECT_DATA de la definición de nombres (título, tipo ATC, modelo e id) en meta.json y en `aircraft` de las filas; OPEN (aplicación y versión) en meta.json
- EVENT y EVENT_FILENAME: SimStart, SimStop, Crashed, FlightLoaded (el archivo de vuelo) y AircraftLoaded (el archivo de la aeronave) como vuelos, accidentes y meta.json
- QUIT termina la sesión

**Guardado sin procesar**

- cada mensaje que entrega SimConnect al watcher, completo como `payload`, bajo el nombre de su SIMCONNECT_RECV_ID: `SIMOBJECT_DATA`, `EVENT`, `EVENT_FILENAME`, `OPEN`, `QUIT`, `EXCEPTION` (una variable o evento que el simulador no aceptó, con el id de envío y el índice), cualquier otro id por su nombre o `RECV_<id>`
- lo que solo tiene el archivo auxiliar sin procesar: la posición de cada fotograma del simulador entre las filas, los eventos Pause, Sim, CrashReset, PositionChanged y FlightSaved, una definición que el simulador acortó (una variable que no conocía: el bloque entonces no se lee por nombre); `requests` de meta.json lista las variables y unidades de cada definición en orden, así que las cargas útiles se leen sin este módulo

**No disponible**

- otras aeronaves (tráfico IA, otros jugadores en línea): SimConnect_RequestDataOnSimObjectType sondearía cada aeronave en un radio - más carga para el simulador, y los vuelos de otros jugadores
- el bloque de movimiento en cada fotograma: se pide cada sexto fotograma (unos 10 Hz, la frecuencia de las filas), lo que mantiene el flujo sin procesar cerca de una quinta parte del tamaño; el bloque de posición sigue en cada fotograma
- las miles de otras variables de simulación (radios, luces, todos los indicadores de motor, fallos): una definición contiene lo que pide; las listas piden el vuelo, el estado de la aeronave y la hora de la simulación
- observaciones meteorológicas, instalaciones (aeropuertos, VOR), datos de cliente de complementos: peticiones separadas, no hechas

**Tamaño**: unos 30-55 MB por hora antes de zstd: el bloque de posición en cada fotograma (unos 200 bytes con su marco, 30-60 por segundo), el bloque de movimiento a unos 10 Hz (unos 240 bytes), el bloque de estado una vez por segundo; zstd reduce varias veces los dobles

## Verificado {#verified}

decodificación de mensajes probada con búferes construidos a partir de los diseños de SimConnect.h; la conexión SimConnect en vivo no está probada

## Fuente {#source}

[heat3d_watch/adapters/msfs.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/msfs.py)

<!-- Generado a partir del adaptador por tools/gen_game_pages.py; cambia el adaptador y vuelve a ejecutarlo en lugar de editar esta página. -->
