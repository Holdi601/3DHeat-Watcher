---
title: "Counter-Strike 2 (estado de juego)"
nav_order: 9
lang: "es"
source: game-cs2-gsi.md
source_hash: "2eda1106e11f"
nav_exclude: true
search_exclude: true
---
# Counter-Strike 2 (estado de juego) {#counter-strike-2-game-state}

Mientras juegas Counter-Strike 2, el watcher guarda lo que el juego informa a programas de tu propio ordenador, para que puedas verlo más tarde en un mapa del visor de 3DHeat.

*Detalles técnicos: adaptador `cs2-gsi`, tipo [`gsi`](sources-and-rules.md); se ejecuta mientras `cs2.exe` está en marcha y busca datos nuevos cada 0,05 s.*

## Qué se graba {#what-is-recorded}

- posición propia (XYZ del mundo, en pulgadas) y dirección de la vista hasta 10 veces por segundo mientras estás vivo
- apariciones (la primera vez que se ve cada ronda, reapariciones) y muertes (la salud llega a 0, o el recuento de muertes)
- bajas con el arma activa, según las estadísticas de la partida
- rondas (inicio, fin, ganador), bomba colocada, desactivada o explotada, fases de la partida y el resultado
- bajas, asistencias, muertes, MVP, marcador, dinero, daño, bajas de cabeza, rondas ganadas y perdidas

## De dónde viene {#where-it-comes-from}

Game State Integration: envíos HTTP (POST) a 127.0.0.1:3311 configurados por &lt;CS2>\game\csgo\cfg\gamestate_integration_heat3d.cfg

## Cómo activarlo {#how-to-switch-it-on}

`python -m heat3d_watch setup cs2-gsi --apply`, y después inicia CS2 (el juego lee el archivo al arrancar)

Escribe el comando en una terminal abierta en la carpeta del watcher (véase [Antes de empezar](before-you-start.md)). Si falla, la última línea dice por qué; [Instalación y uso](installing-and-running.md) recoge las causas habituales.

`python -m heat3d_watch setup cs2-gsi` muestra los archivos que cambiaría; `python -m heat3d_watch setup cs2-gsi --apply` los cambia y guarda el original como `<archivo>.heat3d-backup` (véase [Comandos](commands.md#setup)). Escribe `cs2-gsi: changed: ...` por cada cambio, o `cs2-gsi: nothing to change` si ya está activado.

Ajustes desde variables de entorno:

- `HEAT3D_CS2_GSI_PORT`: el puerto al que envía el juego (por defecto 3311); el archivo cfg del juego debe indicar el mismo puerto

## Cómo funciona {#how-it-works}

Valve Game State Integration: Counter-Strike 2 y Dota 2 comunican a un servidor web local lo que ocurre.

Ambos juegos leen cada `gamestate_integration_*.cfg` de su carpeta cfg al arrancar y, a partir de ahí, envían un documento JSON (POST) a la `uri` de cada archivo cada vez que cambia el estado (como máximo cada `throttle` segundos, y cada `heartbeat` segundos cuando no cambia nada). El watcher es ese servidor web: escucha solo en 127.0.0.1, responde 200 a cada POST al instante y hace el trabajo en su propio hilo de sondeo.

```text
Counter-Strike 2  <CS2>\game\csgo\cfg\gamestate_integration_heat3d.cfg      port 3311
Dota 2            <Dota>\game\dota\cfg\gamestate_integration\gamestate_integration_heat3d.cfg   port 3312
```

Lo que recibe un jugador, y por tanto lo que puede grabarse, lo decide el juego según lo que el jugador puede ver:

- CS2: `provider` (el steamid propio), `map` (nombre, modo, fase warmup/live/intermission/gameover, ronda, marcador team_ct/team_t), `round` (fase freezetime/live/over, bomba plantada/explotada/desactivada, win_team), `player` (el jugador que se está *observando*: uno mismo mientras estás vivo, un compañero tras morir) con `state` (health, armor, money, round_kills, round_killhs, round_totaldmg), `match_stats` (kills, assists, deaths, mvps, score), `position` y `forward` como cadenas "x, y, z" en unidades del mundo (pulgadas, Z hacia arriba), `weapons`; `bomb` solo para espectadores. Las posiciones de los demás jugadores (`allplayers_*`) solo se envían a espectadores y GOTV, así que no se piden.
- Dota 2: `map` (matchid, game_state, game_time, clock_time, win_team), `player` (kills, deaths, assists, last_hits, denies, gold, gpm, xpm, team_name), `hero` (xpos/ypos en unidades del mundo, level, alive, respawn_seconds), `buildings` (salud por torre, cuartel y ancestro), `roshan`, `events` (roshan_killed, aegis_picked_up, ...). No hay altura: z es 0. También se piden y se guardan completos: `abilities`, `items`, `draft`, `wearables`, `minimap`, `couriers`, `neutralitems`, `league` (el juego envía lo que tiene el cliente del propio jugador; cuáles de ellos traen datos mientras se juega y no se observa aún no está probado).

Cada documento también se guarda completo (regla de conversión de 3DHeat, docs/converters.md en el repositorio del visor): `heat.raw.parquet`, `type` "gsi", `text` el JSON tal como se envió; solo el token del archivo cfg se oculta, porque es el secreto propio del watcher y no un dato del juego. Los documentos enviados mientras no hay ninguna partida abierta (menús, carga, entre partidas) esperan en cola y pasan a la sesión de la siguiente partida, antes de su inicio; lo que queda cuando se cierra el juego recibe una sesión propia que solo los contiene. Las entregas que no se pueden leer y las que llevan un token incorrecto también se guardan ("gsi-unreadable", "gsi-bad-auth").

Fuentes: <https://developer.valvesoftware.com/wiki/Counter-Strike:_Global_Offensive_Game_State_Integration>
(el formato que CS2 mantuvo), <https://github.com/antonpup/CounterStrike2GSI> y
<https://github.com/antonpup/Dota2GSI> (listas de campos; MIT, leídos solo para los datos).

El mismo módulo también sirve a: [Dota 2 (estado de juego)](game-dota2-gsi.md).

## Posiciones y ejes {#positions-and-axes}

| | |
|---|---|
| Posiciones registradas | sí |
| Eje vertical | `z` |
| Unidades | pulgadas (unidades de Hammer) |
| Invertido para el visor | `y` |
| Escala de unidad (`scale`: el visor multiplica las posiciones por ella) | 1 |

Estos valores van al `meta.json` de cada sesión (`axes`) y, cuando la sesión tiene posiciones, al pie de `heat.parquet`, así que el visor de 3DHeat gira y escala las filas por sí mismo; véase [Los datos](the-data.md).

## Multijugador {#multiplayer}

- Marcado como jugado en línea (`multiplayer`): **sí**. `games --markdown` lo muestra como "permitido (lee solo lo que publica el juego)".
- Tipo `gsi`: lee solo lo que el juego o la plataforma entregan (una game-state integration o una API local que sirve el juego), así que graba también en el juego en línea; la marca solo decide si la memoria puede leerse alguna vez.
- Memoria: **nunca** la lee este adaptador. Solo los adaptadores `memory` leen memoria, y nunca en un juego marcado como jugado en línea; véase [Fuentes y reglas](sources-and-rules.md).

## Estadísticas registradas {#statistics-recorded}

Claves de estadística que el código de este adaptador asigna por nombre (el `stats` de cada sesión en `meta.json` y la tabla `stats` de `watcher.sqlite`):

`bad_auth`, `bad_packets`, `dropped_packets`, `money`, `result`, `score_other`, `score_own`

Una clave entre llaves se completa en tiempo de ejecución (`score.{team}` es una clave por equipo). Las claves que el código toma de una tabla de campos del juego o de sus propios nombres de estadística no están en esta lista; "Qué se graba" arriba las nombra.

## Completitud {#completeness}

El watcher sigue la [regla de conversión](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md) de 3DHeat: lo que trae la fuente se lee o se guarda, nunca se descarta. Además de las filas, cada paquete, página, línea o respuesta que recibe el adaptador se guarda completo en `heat.raw.parquet` de la sesión (columnas `time`, `ms`, `type`, `used`, `payload`, `text`, y los campos guardados por nombre; `used` marca lo que también se convirtió en filas), y `selfCheck.completeness` de `meta.json` cuenta cada `type` - `lost` es 0.

**Leído**

- la posición, dirección de la vista, salud, armadura, dinero, arma activa, casco, kit de desactivación, cantidades de flash/humo/fuego y valor del equipo del jugador observado, en cada fila de posición mientras sea el propio jugador (steamid del provider = steamid del jugador)
- apariciones, muertes (salud a 0, o el recuento de muertes de las estadísticas de la partida), bajas (el recuento de bajas que sube)
- fases de la partida, rondas (tiempo de compra, en vivo, terminada, ganador), bomba plantada/desactivada/explotada, el resultado
- bajas, asistencias, muertes, MVP, marcador, dinero, daño, bajas de cabeza, rondas ganadas y perdidas como estadísticas

**Guardado sin procesar**

- `gsi`: cada documento que envía el juego, completo, tal como se envió (`text`); `used` es verdadero cuando se leyó durante una partida - provider (versión, marca de tiempo), map (modo, nombres de equipo, derrotas seguidas por ronda, tiempos muertos, victorias de serie, `round_wins` con la condición de victoria de cada ronda), round, el jugador observado (clan, puesto de observador, actividad, cada arma con skin, munición y reserva), bomb, cuentas atrás de fase, y el diff `previously`/`added` del juego respecto a la entrega anterior
- documentos de menús, carga y entre partidas: se guardan de la misma forma, en su propio momento antes del inicio de la siguiente partida; tras la última partida, en una sesión propia (`raw_only` en meta.json)
- `gsi-unreadable`: una entrega que no es un objeto JSON, con sus bytes como `payload` y `length`
- `gsi-bad-auth`: una entrega con otro token que el del archivo cfg

**No disponible**

- otros jugadores (`allplayers_*`) y granadas (`allgrenades`): el juego solo los envía a espectadores y GOTV, y el watcher no los pide (Fuentes y reglas); una demo tiene a todos los jugadores; véase [Counter-Strike 2 (repeticiones)](game-cs2-demos.md)
- estados entre entregas: el juego envía como máximo cada 0,1 s (`throttle`) y solo al cambiar, y cada 10 s (`heartbeat`) en otro caso
- el token del archivo cfg, oculto en cada documento guardado: el secreto propio del watcher, no un dato del juego
- entregas por encima de 10.000 en espera (el watcher se ha atascado) se cuentan como `dropped_packets` y no se guardan; una entrega de más de 4 MB se guarda como `gsi-unreadable` con su longitud pero sin sus bytes

**Tamaño**: un documento de un jugador ocupa 2-4 KB, se envía hasta 10 veces por segundo mientras algo cambia: unos 30-150 MB por hora en `raw.bin` mientras dura la partida, una décima parte o menos en `heat.raw.parquet` comprimido con zstd (estimado a partir del formato publicado, no medido en el juego)

## Verificado {#verified}

probado con documentos en el formato GSI publicado, enviados al adaptador en marcha; la instalación y la búsqueda de la carpeta cfg probadas en una instalación local; sin probar contra el juego en marcha

## Fuente {#source}

[heat3d_watch/adapters/gsi.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/gsi.py)

<!-- Generado a partir del adaptador por tools/gen_game_pages.py; cambia el adaptador y vuelve a ejecutarlo en lugar de editar esta página. -->
