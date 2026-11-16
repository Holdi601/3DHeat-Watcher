---
title: "World of Tanks (repeticiones)"
nav_order: 47
lang: "es"
source: game-wot-replays.md
source_hash: "2fa28633a0ee"
nav_exclude: true
search_exclude: true
---
# World of Tanks (repeticiones) {#world-of-tanks-replays}

Después de una partida de World of Tanks, el watcher convierte la repetición que guardó el juego en archivos que puedes ver sobre un mapa en el visor de 3DHeat.

*Detalles técnicos: adaptador `wot-replays`, tipo [`replay`](sources-and-rules.md); funciona todo el tiempo (no espera a que empiece una partida) y busca datos nuevos cada 5 s.*

## Qué se graba {#what-is-recorded}

- la posición y el rumbo de cada vehículo unas 10 veces por segundo mientras el cliente que grabó lo conocía: el de su propio equipo todo el tiempo, un enemigo mientras está avistado
- jugador, equipo y vehículo (nación:tanque) de cada uno; muertes donde cayó la víctima y bajas donde estaba el asesino, con una precisión de cerca de un segundo, según los resultados
- el mapa; las bajas, el daño, la supervivencia y el resultado del jugador que grabó, como estadísticas

## De dónde viene {#where-it-comes-from}

repeticiones que guarda World of Tanks: &lt;World of Tanks>/replays/\*.wotreplay (con la grabación de batallas activada), convertidas por el conversor externo `heat3d-wot-replay` (exporters/ext/wot-replay)

## Cómo activarlo {#how-to-switch-it-on}

activa la grabación de batallas en los ajustes de World of Tanks (General > Grabar batallas) e instala el conversor: pip install -e &lt;3DHeat>/exporters/ext/wot-replay

Ajustes desde variables de entorno:

- `HEAT3D_WOT_REPLAY`: la carpeta del conversor (un clon o una versión descomprimida), cuando no está instalado ni junto al watcher

## Cómo funciona {#how-it-works}

Repeticiones y demos: lo que guarda un juego de una partida, convertido una vez que la partida ha terminado.

Una repetición contiene todo lo que una interfaz en vivo se reserva en los juegos multijugador -
la posición de cada jugador, cada baja donde ocurrió- y es un archivo que el
juego escribe para sus jugadores, así que leerlo no toca nada del juego. El
watcher mira las carpetas donde los juegos las guardan, espera a que un archivo
nuevo deje de crecer (si no, el juego todavía lo está escribiendo) y lo convierte
en un hilo de trabajo, de modo que una conversión larga nunca detiene el resto
del watcher.

La primera vez que se ve una carpeta, las repeticiones que ya hay en ella solo
se anotan, no se convierten: un jugador con años de demos vería el watcher
ocupado durante un día. `python -m heat3d_watch replays <adaptador> [carpeta]`
convierte las que ya existen cuando se le pide.

#### World of Tanks y World of Warships {#world-of-tanks-and-world-of-warships}

Ambos guardan una repetición de cada batalla en `<juego>/replays/` cuando la
grabación está activada (`*.wotreplay`, `*.wowsreplay`); las instalaciones se
encuentran por la lista del Wargaming Game Center, `C:/Games/World_of_Tanks*` /
`World_of_Warships*`, y por Steam. Como con War Thunder, el watcher no lee los
archivos por sí mismo: lo hace un conversor externo de cada uno
(`exporters/ext/wot-replay`, comando `heat3d-wot-replay`; `exporters/ext/wows-replay`,
comando `heat3d-wows-replay`), cada uno un proyecto propio.
Si se encuentra en el PATH, está instalado o
junto al watcher, convierte cada repetición nueva en `<mapa>/<partida>.parquet` y
`<partida>.match.json` en la carpeta de la sesión; si falta, el watcher dice una vez
cómo instalarlo. La línea del jugador que grabó - vehículo o barco, bajas, daño
(World of Tanks), si sobrevivió, y el resultado (World of Tanks) - pasa a ser las
estadísticas de la sesión. Lo que lee cada conversor, y lo que no, está en su README.

El mismo módulo sirve también a: [Counter-Strike 2 (repeticiones)](game-cs2-demos.md), [Dota 2 (repeticiones)](game-dota-replays.md), [Squad (repeticiones)](game-squad-demos.md), [War Thunder (repeticiones)](game-warthunder-replays.md), [World of Warships (repeticiones)](game-wows-replays.md).

## Posiciones y ejes {#positions-and-axes}

| | |
|---|---|
| Posiciones grabadas | sí |
| Eje hacia arriba | `y` |
| Unidades | metros (x este, y arriba, z norte) |
| Reflejado para el visor | `z` |
| Escala de unidades (`scale`: el visor multiplica las posiciones por ella) | 1 |

Esto va al `meta.json` de cada sesión (`axes`) y, cuando la sesión tiene posiciones, al pie de `heat.parquet`, así que el visor de 3DHeat gira y escala las filas por sí mismo: véase [Los datos](the-data.md).

## Multijugador {#multiplayer}

- Marcado como jugado en línea (`multiplayer`): **sí**. `games --markdown` lo muestra como "permitido (solo lee lo que publica el juego)".
- Tipo `replay`: lee solo lo que el juego o la plataforma entrega (las repeticiones y demos que guarda el juego), así que graba también en el juego en línea; la marca solo decide si la memoria puede leerse alguna vez.
- Memoria: **nunca** la lee este adaptador. Solo los adaptadores `memory` leen la memoria, y nunca en un juego marcado como jugado en línea: véase [Fuentes y reglas](sources-and-rules.md).

## Estadísticas registradas {#statistics-recorded}

Claves de estadística que el código de este adaptador fija por nombre (el `stats` de cada sesión en `meta.json` y la tabla `stats` de `watcher.sqlite`):

`map`, `survived`, `vehicle`, `won`

Una clave entre llaves se completa en tiempo de ejecución (`score.{team}` es una clave por equipo). Las claves que el código toma de una tabla de campos del juego o de los nombres de estadísticas propios del juego no aparecen en esta lista; "Qué se graba" más arriba las nombra.

## Completitud {#completeness}

El conversor que ejecuta este adaptador sigue la [regla de conversores](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md) de 3DHeat: lo que contiene la repetición se lee o se guarda, nunca se descarta - se lee en la tabla y en el documento de la partida, y todo lo demás se guarda completo en archivos auxiliares junto a ellos, contado en `selfCheck.completeness` del documento de la partida. La documentación del propio conversor enumera lo que lee, lo que guarda en bruto y lo que no puede leer.

## Verificación {#verified}

el conversor se comprueba con repeticiones públicas de varias versiones del juego y con pruebas sobre repeticiones generadas; este gancho, con pruebas usando un comando de sustitución

## Fuente {#source}

[heat3d_watch/adapters/replays.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/replays.py)

<!-- Generated from the adapter by tools/gen_game_pages.py; change the adapter and run it again rather than editing this page. -->
