---
title: "DCS World (datos en vivo)"
nav_order: 10
lang: "es"
source: game-dcs.md
source_hash: "87cba160674e"
nav_exclude: true
search_exclude: true
---
# DCS World (datos en vivo) {#dcs-world-live-data}

Mientras juegas DCS World, el watcher guarda los datos que el propio juego envía, para que puedas verlos más tarde en un mapa del visor de 3DHeat.

*Detalles técnicos: adaptador `dcs`, tipo [`telemetry`](sources-and-rules.md); se ejecuta mientras `DCS.exe` está en marcha y busca datos nuevos cada 0,1 s.*

## Qué se graba {#what-is-recorded}

- posición propia a 10 Hz, en metros al este/arriba/norte del origen del teatro (a partir de latitud/longitud/altitud); lat/lon/alt y los metros del mundo de DCS (dcs_x norte, dcs_y arriba, dcs_z este) como columnas
- actitud, velocidad indicada y verdadera, Mach, velocidad vertical, ángulo de ataque y resbalamiento, rumbo magnético, AGL y altura de radar, g en los tres ejes, velocidad y velocidades de giro, en el aire, posición y vector hacia delante de la cámara, tipo de aeronave
- despegues y aterrizajes con el aeródromo; accidentes, eyecciones, muertes de pilotos
- bajas y derribos con ambos tipos de unidad y el arma; otros eventos del juego tal como llegan
- vidas por misión (spawn ... session_end), bajas, muertes, distancia, altitud máxima, g máxima
- cada línea que envía el hook guardada completa en heat.raw.parquet, con un volcado cada segundo de las tablas de exportación de la aeronave (motores, tren y flaps, carga, contramedidas, ruta, navegación) y todos los demás callbacks (pausa, chat, jugadores que se unen, carga de misión)

## De dónde viene {#where-it-comes-from}

el hook del watcher %USERPROFILE%\Saved Games\DCS\*\Scripts\Hooks\heat3d-watch.lua, líneas UDP a 127.0.0.1:41993

## Cómo activarlo {#how-to-switch-it-on}

python -m heat3d_watch setup dcs --apply (añade Scripts\Hooks\heat3d-watch.lua), y después reinicia DCS

Escribe el comando en una terminal abierta en la carpeta del watcher (véase [Antes de empezar](before-you-start.md)). Si falla, la última línea dice por qué; [Instalación y uso](installing-and-running.md) recoge las causas habituales.

`python -m heat3d_watch setup dcs` muestra los archivos que cambiaría; `python -m heat3d_watch setup dcs --apply` los cambia y guarda el original como `<archivo>.heat3d-backup` (véase [Comandos](commands.md#setup)). Escribe `dcs: changed: ...` por cada cambio, o `dcs: nothing to change` si ya está activado.

## Cómo funciona {#how-it-works}

DCS World: un pequeño script hook propio del watcher que envía líneas UDP a 127.0.0.1:41993.

DCS ejecuta al arrancar los archivos Lua de `Saved Games\DCS*\Scripts\Hooks\`; un hook puede leer las funciones de exportación (`Export.Lo*`) y recibir los callbacks de la simulación (`DCS.setUserCallbacks`: onSimulationStart/Frame/Stop, onGameEvent); véase `<DCS>\API\DCS_ControlAPI.html` y <https://wiki.hoggitworld.com/view/DCS_Export_Script>.
`setup` escribe `heat3d-watch.lua` ahí (su propio archivo: Export.lua y los hooks de otras herramientas no se tocan), que envía diez líneas por segundo, una más por segundo, y una por cada evento del juego o callback, sin esperar nunca respuesta. El puerto es 41993 para que el hook de JoyPro (41992) y Tacview (42674) sigan funcionando junto a él. Las líneas (campos separados por ';'):

```text
hello;v=2                                       the hook was loaded
start;mission=..;map=..;me=<player id>;name=..;mp=0|1;file=..;server=0|1
mis;t=..;date.Day=..;start_time=..;weather...   the mission's date, start time and weather, flattened
p;t=<model s>;x=;y=;z=;lat=;lon=;alt=;hdg=;pitch=;bank=;ias=;agl=;g=;type=;tas=;mach=;vv=;aoa=;aos=;
  mhdg=;ralt=;gx=;gz=;vx=;vy=;vz=;wx=;wy=;wz=;air=;cx=;cy=;cz=;cfx=;cfy=;cfz=
d;t=..;self.Name=..;eng.RPM.left=..;mech.gear.value=..;pay.Stations.1.count=..;...   once a second
ev;t=..;name=<onGameEvent name>;args=a|b|c      every onGameEvent
cb;t=..;name=<callback>;args=a|b                every other callback (pause, chat, players, loading)
noexport;t=..                                   the server forbids ownship export
stop;t=..                                       the mission ended
```

`p` es LoGetSelfData: Position x/y/z - metros del mundo de DCS, x norte, y arriba, z este - más LatLongAlt (grados, m), Heading/Pitch/Bank (radianes), con LoGetIndicatedAirSpeed (m/s), LoGetAltitudeAboveGroundLevel (m) y LoGetAccelerationUnits() x/y/z (g); y, tal como documenta `Scripts\Export.lua`, LoGetTrueAirSpeed (m/s), LoGetMachNumber, LoGetVerticalVelocity (m/s), LoGetAngleOfAttack y LoGetAngleOfSideSlip (rad), LoGetMagneticYaw (rad), LoGetRadarAltimeter (m), LoGetVectorVelocity (m/s del mundo), LoGetAngularVelocity (rad/s), LoGetInAir, y el punto y el vector hacia delante de LoGetCameraPosition (metros del mundo). `d` es un volcado cada segundo de tablas completas, aplanadas en claves con puntos: LoGetSelfData (país, coalición, nombres de unidad y grupo, niveles de tipo, indicadores), LoGetEngineInfo, LoGetMechInfo, LoGetPayloadInfo, LoGetSnares, LoGetWingInfo, LoGetVectorWindVelocity, LoGetFMData, LoGetNavigationInfo, LoGetRoute, LoGetMCPState, LoGetControlPanel_HSI, LoGetRadioBeaconsStatus y algunos números (pausa, aceleración del tiempo, asiento, presión, desviaciones). El watcher guarda cada línea completa en el archivo auxiliar sin procesar; `p` también se convierte en las filas.

Las posiciones van al mismo mapa plano que los otros simuladores de vuelo (`Tangent`: x este, y altitud sobre el nivel del mar, z norte, en metros) a partir de LatLongAlt, alrededor del origen fijo del teatro (`THEATRES`, tomado del `map` de la línea de inicio), de modo que cada misión en un mismo teatro comparte un mapa, y uno sobre el que el visor puede colocar el mundo real. Un teatro que no esté en la tabla toma la latitud y longitud de la primera posición redondeadas a grados enteros. Las x/y/z propias de DCS se guardan como `dcs_x`, `dcs_y`, `dcs_z`; una posición sin LatLongAlt no puede situarse y solo se cuenta (`fixes_without_latlon`). El origen es el `geo` de la sesión, en meta.json y en el pie de la tabla.

Los argumentos de onGameEvent, tal como los da DCS_ControlAPI: takeoff/landing (playerID, unit_missionID, airdromeName), crash/eject/pilot_death (playerID, unit_missionID), kill (killerPlayerID, killerUnitType, killerSide, victimPlayerID, victimUnitType, victimSide, weaponName), self_kill (playerID), change_slot (playerID, slotID, prevSide), mission_end (winner, msg).

Un servidor multijugador puede prohibir la exportación de la propia aeronave (LoIsOwnshipExportAllowed es false); entonces no hay posiciones, solo eventos, y la sesión lo indica.

## Posiciones y ejes {#positions-and-axes}

| | |
|---|---|
| Posiciones registradas | sí |
| Eje vertical | `y` |
| Unidades | metros (este, altitud, norte desde el origen del teatro) |
| Invertido para el visor | `z` |
| Escala de unidad (`scale`: el visor multiplica las posiciones por ella) | 1 |

Estos valores van al `meta.json` de cada sesión (`axes`) y, cuando la sesión tiene posiciones, al pie de `heat.parquet`, así que el visor de 3DHeat gira y escala las filas por sí mismo; véase [Los datos](the-data.md).

## Multijugador {#multiplayer}

- Marcado como jugado en línea (`multiplayer`): **sí**. `games --markdown` lo muestra como "permitido (lee solo lo que publica el juego)".
- Tipo `telemetry`: lee solo lo que el juego o la plataforma entregan (un puerto UDP o memoria compartida que publica el juego), así que graba también en el juego en línea; la marca solo decide si la memoria puede leerse alguna vez.
- Memoria: **nunca** la lee este adaptador. Solo los adaptadores `memory` leen memoria, y nunca en un juego marcado como jugado en línea; véase [Fuentes y reglas](sources-and-rules.md).

## Estadísticas registradas {#statistics-recorded}

Claves de estadística que el código de este adaptador asigna por nombre (el `stats` de cada sesión en `meta.json` y la tabla `stats` de `watcher.sqlite`):

`airborne_time`, `bad_packets`, `crashes`, `deaths`, `distance_km`, `ejections`, `export_blocked`, `fixes_without_latlon`, `flight_time`, `kills`, `max_altitude_m`, `max_g`, `shot_down`, `{event}s`

Una clave entre llaves se completa en tiempo de ejecución (`score.{team}` es una clave por equipo). Las claves que el código toma de una tabla de campos del juego o de sus propios nombres de estadística no están en esta lista; "Qué se graba" arriba las nombra.

## Completitud {#completeness}

El watcher sigue la [regla de conversión](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md) de 3DHeat: lo que trae la fuente se lee o se guarda, nunca se descarta. Además de las filas, cada paquete, página, línea o respuesta que recibe el adaptador se guarda completo en `heat.raw.parquet` de la sesión (columnas `time`, `ms`, `type`, `used`, `payload`, `text`, y los campos guardados por nombre; `used` marca lo que también se convirtió en filas), y `selfCheck.completeness` de `meta.json` cuenta cada `type` - `lost` es 0.

**Leído**

- `p` (10 Hz): posición, LatLongAlt, actitud, IAS, AGL, g (x/y/z), tipo de aeronave, y de la segunda versión del hook el TAS, Mach, velocidad vertical, AoA, resbalamiento, rumbo magnético, altura de radar, velocidad del mundo, velocidades de giro, en el aire y el punto/vector hacia delante de la cámara - todo como columnas de las filas (unidades tal como las da Export.lua)
- `start`: misión, teatro, id y nombre del jugador propio, multijugador, archivo de misión, servidor; `mis`: la fecha y hora de inicio de la misión a meta.json
- `ev`: cada onGameEvent como fila (takeoff, landing, crash, eject, pilot_death, kill, self_kill, change_slot, connect, disconnect, friendly_fire, mission_end, cualquier otro nombre tal como llega)
- `noexport` y `stop` como filas y en meta.json

**Guardado sin procesar**

- cada línea que envía el hook, completa, como `text` bajo su tipo: `hello`, `start`, `mis`, `p`, `d`, `ev`, `cb`, `noexport`, `stop`; una línea de cualquier otro tipo bajo `unknown`
- `d` (1 Hz, solo sin procesar): LoGetSelfData completo (país, coalición, nombre de unidad y de grupo, niveles de tipo, indicadores), LoGetEngineInfo, LoGetMechInfo, LoGetPayloadInfo, LoGetSnares, LoGetWingInfo, vector de viento, LoGetFMData, LoGetNavigationInfo, LoGetRoute, LoGetMCPState, HSI, radiobalizas, pausa, aceleración del tiempo, asiento, presión, desviaciones - aplanados en claves con puntos
- `mis`: la tabla meteorológica de la misión, aplanada; `cb`: onSimulationPause/Resume, onMissionLoad\*, onNet\*, onPlayerConnect/Disconnect/Start/Stop/ChangeSlot, onChatMessage, onTriggerMessage, onRadioMessage, onRadioCommand, onShowMessage con sus argumentos

**No disponible**

- otras unidades (LoGetWorldObjects, LoGetObjectById) y datos de sensores (LoGetTargetInformation, LoGetLockedTargetInformation, LoGetTWSInfo, LoGetWingTargets, LoGetSightingSystemInfo): no se piden - cada objeto de una misión a 10 Hz es costoso dentro del propio marco de DCS, y un servidor los filtra (allow_object_export, allow_sensor_export); Tacview los graba
- la tabla completa de la misión (DCS.getCurrentMission contiene cada unidad y disparador, megabytes): solo se envían su fecha, hora de inicio, meteorología, salida, teatro y versión
- los callbacks onPlayerTry\*: contestan a DCS (permitir o rechazar), así que el hook no los toca
- las direcciones y UCID de otros jugadores: net.get_player_info las da solo a un servidor, y no son del jugador para guardarlas
- las entradas de una tabla más allá de 800 claves o 6 niveles de profundidad en una línea `d` se cortan, para que una línea siga siendo un datagrama

**Tamaño**: unos 20 MB por hora de líneas `p` (10 por segundo, unos 500 bytes cada una con su marco) y 15-40 MB de volcados `d` (uno por segundo, 4-10 KB según la carga y la ruta de la aeronave), antes de zstd; las claves repetidas se comprimen unas diez veces

## Verificado {#verified}

formato de línea probado con datagramas sintéticos; el hook Lua no está probado dentro de DCS (escrito a partir de la API de hooks y exportación de DCS y de la lista de funciones Lo\* de Scripts\Export.lua, no ejecutado)

## Fuente {#source}

[heat3d_watch/adapters/dcs.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/dcs.py)

<!-- Generado a partir del adaptador por tools/gen_game_pages.py; cambia el adaptador y vuelve a ejecutarlo en lugar de editar esta página. -->
