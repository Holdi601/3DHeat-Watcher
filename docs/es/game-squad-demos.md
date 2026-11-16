---
title: "Squad (repeticiones)"
nav_order: 40
lang: "es"
source: game-squad-demos.md
source_hash: "a908f7e6d9c3"
nav_exclude: true
search_exclude: true
---
# Squad (repeticiones) {#squad-replays}

Después de una partida de Squad, el watcher convierte la repetición que guardó el juego en archivos que puedes ver sobre un mapa en el visor de 3DHeat.

*Detalles técnicos: adaptador `squad-demos`, tipo [`replay`](sources-and-rules.md); funciona todo el tiempo (no espera a que empiece una partida) y busca datos nuevos cada 5 s.*

## Qué se graba {#what-is-recorded}

- la posición de cada jugador, el giro de su cuerpo y su velocidad cada vez que el servidor lo replica (hasta 8 veces por segundo), a pie y en vehículos terrestres
- el nombre, el equipo, la facción y la escuadra de cada jugador, siguiendo los cambios de equipo
- no: el movimiento de los helicópteros, las bajas y los desplegables - véase el README del lector

## De dónde viene {#where-it-comes-from}

demos de servidor que Squad graba con el comando de administrador AdminDemoRec: &lt;servidor>/SquadGame/Saved/Demos/\*.replay, leídas por el lector externo `heat3d-squad-demo` (exporters/ext/squad-demo)

## Cómo activarlo {#how-to-switch-it-on}

graba en el servidor: da al administrador el permiso `demos` en Admins.cfg, y después AdminDemoRec &lt;nombre> y AdminDemoStop en la consola del juego; copia la demo aquí e instala el lector: pip install -e &lt;3DHeat>/exporters/ext/squad-demo

Ajustes desde variables de entorno:

- `HEAT3D_SQUAD_DEMO`: la carpeta del conversor (un clon o una versión descomprimida), cuando no está instalado ni junto al watcher

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

#### Squad {#squad}

Los servidores dedicados de Squad graban una demo de una partida cuando un
administrador con el permiso `demos` ejecuta AdminDemoRec &lt;nombre> (y
AdminDemoStop), en `<servidor>/SquadGame/Saved/Demos/<nombre>.replay`: una
repetición de red de Unreal Engine que contiene lo que el servidor replicó,
incluido el movimiento de cada jugador. El watcher no las lee por sí mismo: lo
hace un lector externo (el lector de demos de Squad de 3DHeat,
`exporters/ext/squad-demo`, comando `heat3d-squad-demo`), separado para que un
problema en él no afecte a nada más. Se ejecuta en cada demo nueva de las carpetas
donde escribe un servidor local, o en una carpeta que añaden los ajustes para las
demos copiadas de un servidor alquilado, y deja en la carpeta de la sesión
`<mapa>/<partida>.parquet` y `<partida>.match.json`. La capa, el mapa, el número de
jugadores y la duración de la partida pasan a ser las estadísticas de la sesión.

El mismo módulo sirve también a: [Counter-Strike 2 (repeticiones)](game-cs2-demos.md), [Dota 2 (repeticiones)](game-dota-replays.md), [War Thunder (repeticiones)](game-warthunder-replays.md), [World of Tanks (repeticiones)](game-wot-replays.md), [World of Warships (repeticiones)](game-wows-replays.md).

## Posiciones y ejes {#positions-and-axes}

| | |
|---|---|
| Posiciones grabadas | sí |
| Eje hacia arriba | `z` |
| Unidades | unidades de Unreal (centímetros) |
| Reflejado para el visor | ninguno |
| Escala de unidades (`scale`: el visor multiplica las posiciones por ella) | 1 |

Esto va al `meta.json` de cada sesión (`axes`) y, cuando la sesión tiene posiciones, al pie de `heat.parquet`, así que el visor de 3DHeat gira y escala las filas por sí mismo: véase [Los datos](the-data.md).

## Multijugador {#multiplayer}

- Marcado como jugado en línea (`multiplayer`): **sí**. `games --markdown` lo muestra como "permitido (solo lee lo que publica el juego)".
- Tipo `replay`: lee solo lo que el juego o la plataforma entrega (las repeticiones y demos que guarda el juego), así que graba también en el juego en línea; la marca solo decide si la memoria puede leerse alguna vez.
- Memoria: **nunca** la lee este adaptador. Solo los adaptadores `memory` leen la memoria, y nunca en un juego marcado como jugado en línea: véase [Fuentes y reglas](sources-and-rules.md).

## Estadísticas registradas {#statistics-recorded}

Claves de estadística que el código de este adaptador fija por nombre (el `stats` de cada sesión en `meta.json` y la tabla `stats` de `watcher.sqlite`):

`layer`, `map`, `match_seconds`, `players`

Una clave entre llaves se completa en tiempo de ejecución (`score.{team}` es una clave por equipo). Las claves que el código toma de una tabla de campos del juego o de los nombres de estadísticas propios del juego no aparecen en esta lista; "Qué se graba" más arriba las nombra.

## Completitud {#completeness}

El conversor que ejecuta este adaptador sigue la [regla de conversores](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md) de 3DHeat: lo que contiene la repetición se lee o se guarda, nunca se descarta - se lee en la tabla y en el documento de la partida, y todo lo demás se guarda completo en archivos auxiliares junto a ellos, contado en `selfCheck.completeness` del documento de la partida. La documentación del propio conversor enumera lo que lee, lo que guarda en bruto y lo que no puede leer.

## Verificación {#verified}

el lector se comprueba con demos públicas de servidores (el movimiento concuerda con la velocidad que lleva; el equipo de cada fila coincide con la facción de su soldado) y con pruebas sobre demos generadas; este gancho, con pruebas usando un comando de sustitución

## Fuente {#source}

[heat3d_watch/adapters/replays.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/replays.py)

<!-- Generated from the adapter by tools/gen_game_pages.py; change the adapter and run it again rather than editing this page. -->
