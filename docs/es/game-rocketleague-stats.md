---
title: "Rocket League (estado de juego)"
nav_order: 39
lang: "es"
source: game-rocketleague-stats.md
source_hash: "fd70d0540bb9"
nav_exclude: true
search_exclude: true
---
# Rocket League (estado de juego) {#rocket-league-game-state}

Mientras juegas a Rocket League, el watcher guarda lo que el juego informa a los programas de tu propio ordenador, para que después puedas verlo en un mapa del visor de 3DHeat.

*Detalles técnicos: adaptador `rocketleague-stats`, tipo [`gsi`](sources-and-rules.md); se ejecuta mientras `RocketLeague.exe` está en marcha y busca datos nuevos cada 0,05 s.*

## Qué se graba {#what-is-recorded}

- los golpes al balón con el lugar del balón (XYZ, unidades de Unreal), quién lo golpeó y las velocidades
- goles con el lugar del impacto, quién marcó, quién asistió y la velocidad; golpes al larguero con el lugar
- el flujo de estadísticas (demoliciones, paradas, tiros, paradas épicas, ...), saques de centro, repeticiones, inicio y fin de partida, ganador
- autogoles, asistencias, paradas, tiros, demoliciones, toques, marcador y marcadores de equipo, desde UpdateState
- la línea final de cada jugador al terminar la partida
- tus propias filas como `me`: el jugador indicado en los ajustes (`config --set player_names.rocketleague-stats=<nombre>`); si no, el que sigue la cámara del juego fuera de las repeticiones
- ninguna posición de coches: la API no las tiene

## De dónde viene {#where-it-comes-from}

API de estadísticas: flujo JSON por TCP desde 127.0.0.1:49123 (puerto en &lt;RL>\TAGame\Config\TAStatsAPI.ini o DefaultStatsAPI.ini)

## Cómo activarlo {#how-to-switch-it-on}

`python -m heat3d_watch setup rocketleague-stats --apply` (pone PacketSendRate=30), y luego arranca Rocket League

Escribe el comando en una terminal abierta en la carpeta del watcher (ver [Antes de empezar](before-you-start.md)). Si falla, la última línea dice por qué; [Instalación y ejecución](installing-and-running.md) cubre las causas habituales.

`python -m heat3d_watch setup rocketleague-stats` lista los archivos que cambiaría; `python -m heat3d_watch setup rocketleague-stats --apply` los cambia, guardando el original como `<file>.heat3d-backup` (ver [Comandos](commands.md#setup)). Muestra `rocketleague-stats: changed: ...` por cada cambio, o `rocketleague-stats: nothing to change` si ya está activado.

## Cómo funciona {#how-it-works}

Rocket League: la API oficial de estadísticas, un socket local al que el juego escribe los datos de la partida.

Se activa en `<RL>\TAGame\Config\TAStatsAPI.ini`, o en `DefaultStatsAPI.ini` cuando el primero no existe (el juego solo lee ese caso), bajo `[TAGame.MatchStatsExporter_TA]`:

```text
PacketSendRate   UpdateState messages per second; 0 (the default) switches the API off, at most 120
Port             the TCP port the game listens on, default 49123 (WebPort 49124 is a WebSocket copy)
```

El juego es el servidor: un cliente se conecta a 127.0.0.1:49123 y lee un flujo de objetos JSON `{"Event": nombre, "Data": {...}}` (algunas versiones envían Data como cadena JSON), uno tras otro, sin separadores. Los eventos se envían en el tick en que ocurren, sin importar la frecuencia:

```text
UpdateState   MatchGuid, Players[] (Name, PrimaryId, Shortcut, TeamNum 0 blue / 1 orange,
              Score, Goals, Shots, Assists, Saves, Touches, CarTouches, Demos; car state
              only for spectators), Game (Teams[], TimeSeconds, bOvertime, Ball {Speed,
              TeamNum}, bReplay, bHasWinner, Winner, Arena, bHasTarget, Target)
BallHit       Players[] (Name, Shortcut, TeamNum), Ball {PreHitSpeed, PostHitSpeed, Location {X,Y,Z}}
GoalScored    GoalSpeed, GoalTime, ImpactLocation {X,Y,Z}, Scorer, Assister, BallLastTouch
CrossbarHit   BallLocation {X,Y,Z}, BallSpeed, ImpactForce, BallLastTouch
StatfeedEvent EventName, Type, MainTarget, SecondaryTarget
MatchEnded    WinnerTeamNum
MatchCreated, MatchInitialized, CountdownBegin, RoundStarted, GoalReplayStart/WillEnd/End,
MatchPaused/Unpaused, PodiumStart, ReplayCreated, MatchDestroyed, ClockUpdatedSeconds
```

Las posiciones van en unidades de Unreal (centímetros), Z hacia arriba; el campo mide unos 8200 x 10240, con las porterías en Y = ±5120. Las posiciones de los coches no forman parte de la API: lo único con posición es el balón, donde se golpeó, marcó o tocó el larguero.

Cada mensaje también se guarda entero (regla de conversión de 3DHeat, docs/converters.md en el repositorio del visor): `heat.raw.parquet`, con `type` igual al nombre del Event del mensaje y `text` el objeto tal como llegó del flujo. Un UpdateState idéntico byte a byte al anterior (una partida en pausa, un menú) se guarda una vez y se cuenta en `unchanged_replies` de meta.json. Los mensajes entre partidas esperan en cola para la sesión de la siguiente partida; lo que queda cuando se cierra el juego recibe una sesión propia. Los caracteres entre objetos que no son JSON se guardan como "junk".

Fuentes: <https://www.rocketleague.com/en/developer/stats-api> (la página oficial); el uso de mayúsculas de los campos y el encuadre TCP se confirmaron con el cliente rlstatsapi (<https://docs.rs/crate/rlstatsapi>, MIT; leído solo para los hechos).

## Posiciones y ejes {#positions-and-axes}

| | |
|---|---|
| Posiciones grabadas | sí |
| Eje hacia arriba | `z` |
| Unidades | unidades de Unreal (centímetros) |
| Reflejado para el visor | ninguno |
| Escala de unidad (`scale`: el visor multiplica las posiciones por ella) | 1 |

Esto va al `meta.json` de cada sesión (`axes`) y, cuando la sesión tiene posiciones, al pie de `heat.parquet`, para que el visor de 3DHeat gire y escale las filas por sí solo; ver [Los datos](the-data.md).

## Multijugador {#multiplayer}

- Marcado como jugado en línea (`multiplayer`): **sí**. `games --markdown` muestra esto como "permitido (solo lee lo que publica el juego)".
- Tipo `gsi`: solo lee lo que el juego o la plataforma entregan (una integración de estado de juego o una API local que sirve el juego), así que graba también en el juego en línea, además del juego sin conexión. La marca solo decide si la memoria puede leerse alguna vez.
- Memoria: **nunca** la lee este adaptador. Solo los adaptadores `memory` leen memoria, y nunca en un juego marcado como jugado en línea; ver [Fuentes y reglas](sources-and-rules.md).

## Estadísticas registradas {#statistics-recorded}

Claves de estadística que el código de este adaptador asigna por nombre (el `stats` de cada sesión en `meta.json` y la tabla `stats` de `watcher.sqlite`):

`bad_packets`, `demolished`, `other_goals`, `overtime`, `result`, `team_goals`

Una clave entre llaves se completa en tiempo de ejecución (`score.{team}` es una clave por equipo). Las claves que el código toma de una tabla de campos del juego o de sus propios nombres de estadística no aparecen en esta lista; "Qué se graba" de arriba las nombra.

## Completitud {#completeness}

El watcher sigue la [regla de conversión](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md) de 3DHeat: lo que trae la fuente se lee o se guarda, nunca se descarta. Además de las filas, cada paquete, página, línea o respuesta que recibe el adaptador se guarda entero en `heat.raw.parquet` de la sesión (columnas `time`, `ms`, `type`, `used`, `payload`, `text`, y cualquier campo guardado por nombre; `used` marca lo que también se volvió filas), y `selfCheck.completeness` de `meta.json` cuenta cada `type`: `lost` es 0.

**Se lee**

- BallHit (lugar, quién, equipo, velocidades antes y después), GoalScored (lugar del impacto, quién marcó, asistencia, velocidad, tiempo del gol), CrossbarHit (lugar, último toque, velocidad, fuerza), StatfeedEvent (evento, tipo, objetivo principal y secundario), MatchEnded (ganador, resultado); el nombre de cualquier otro evento como fila
- de UpdateState: la arena, el objetivo de la cámara fuera de las repeticiones (quién es `me`), los marcadores de equipo, los goles, asistencias, paradas, tiros, demoliciones, toques, toques de coche y marcador de cada jugador (los tuyos como estadísticas, los de todos como `player_result` al final de la partida); la prórroga, desde ClockUpdatedSeconds

**Se guarda en bruto**

- cada mensaje entero tal como llegó del flujo (`text`), bajo su propio nombre de Event: `UpdateState` (el PrimaryId y el Shortcut de cada jugador, el reloj, la velocidad y el equipo del balón, nombres y colores de equipos, indicadores de repetición y ganador, y el estado del coche cuando el juego lo envía), `BallHit`, `GoalScored` (con el último toque del balón), `CrossbarHit`, `StatfeedEvent`, `MatchCreated`, `MatchInitialized`, `CountdownBegin`, `RoundStarted`, `GoalReplayStart`, `GoalReplayWillEnd`, `GoalReplayEnd`, `MatchPaused`, `MatchUnpaused`, `MatchEnded`, `PodiumStart`, `ReplayCreated`, `MatchDestroyed`, `ClockUpdatedSeconds` y cualquier evento que añada una versión posterior
- un UpdateState idéntico byte a byte al anterior (en pausa, en menús) se guarda una vez y se cuenta (`unchanged_replies` en meta.json)
- mensajes entre partidas: en su propio momento antes del inicio de la siguiente partida; tras la última partida, en una sesión propia (`raw_only` en meta.json)
- `unreadable`: un objeto que no es un mensaje de la API de estadísticas; `junk`: caracteres entre objetos

**No disponible**

- posiciones de los coches ni su estado mientras se juega: el juego solo los envía a los espectadores
- UpdateState entre dos envíos: el juego envía PacketSendRate por segundo (`setup` pone 30; el juego admite hasta 120); los eventos se envían en el tick en que ocurren
- la copia WebSocket en WebPort (49124): los mismos mensajes que el puerto TCP, sin leerlos dos veces

**Tamaño**: un UpdateState ocupa de 1 a 3 KB con seis jugadores, 30 por segundo: unos 100-300 MB por hora en `raw.bin` mientras dura una partida, y una décima parte o menos en el `heat.raw.parquet` comprimido con zstd (estimado a partir del formato documentado, no medido en el juego)

## Verificado {#verified}

probado con mensajes en el formato documentado enviados por un servidor local falso; sin probar contra el juego

## Fuente {#source}

[heat3d_watch/adapters/rocketleague.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/rocketleague.py)

<!-- Generated from the adapter by tools/gen_game_pages.py; change the adapter and run it again rather than editing this page. -->
