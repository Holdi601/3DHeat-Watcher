---
title: "Counter-Strike 2 (repeticiones)"
nav_order: 8
lang: "es"
source: game-cs2-demos.md
source_hash: "d115f9085302"
nav_exclude: true
search_exclude: true
---
# Counter-Strike 2 (repeticiones) {#counter-strike-2-replays}

Después de una partida de Counter-Strike 2, el watcher convierte la repetición que guardó el juego en archivos que puedes ver sobre un mapa en el visor de 3DHeat.

*Detalles técnicos: adaptador `cs2-demos`, tipo [`replay`](sources-and-rules.md); funciona todo el tiempo (no espera a que empiece una partida) y busca datos nuevos cada 5 s.*

## Qué se graba {#what-is-recorded}

- la posición de cada jugador, hacia dónde mira, su vida y su dinero (cada 8 ticks)
- bajas, muertes, daño, granadas, colocaciones y desactivaciones de bomba, en el lugar donde ocurrieron
- rondas, marcador, economía; la línea del marcador del jugador con sesión iniciada como estadísticas

## De dónde viene {#where-it-comes-from}

las demos que guarda CS2: &lt;CS2>/game/csgo/replays/\*.dem (descargadas del historial de partidas) y &lt;CS2>/game/csgo/\*.dem (grabadas)

## Cómo activarlo {#how-to-switch-it-on}

descarga la demo de una partida en CS2 (Ver > Tus partidas), o grábala con el comando de consola `record`

Ajustes desde variables de entorno:

- `HEAT3D_CS2`: la carpeta de 3DHeat CS2, cuando no está junto al watcher ni instalada

## Cómo funciona {#how-it-works}

Repeticiones y demos: lo que guarda un juego de una partida, convertido una vez que la partida ha terminado.

Una repetición contiene todo lo que una interfaz en vivo se guarda en los juegos multijugador -
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

#### Counter-Strike 2 {#counter-strike-2}

CS2 guarda en `<CS2>/game/csgo/replays/` las demos que el jugador descarga del
historial de partidas (pestaña de partidas), y en `<CS2>/game/csgo/` las que se
graban con el comando de consola `record`. Cada una se convierte con el propio
conversor de CS2 de este repositorio (3DHeat CS2, github.com/Holdi601/3DHeat-CS2:
la posición de cada jugador, hacia dónde mira, su vida y su dinero cada ocho ticks;
bajas, muertes, daño, granadas, colocaciones y desactivaciones donde ocurrieron;
rondas, marcador, economía) en la carpeta de la sesión, como la tabla
`<mapa>/<partida>.parquet` y el resumen `<partida>.match.json` que leen las
pestañas de mapa de calor y de partida del visor. El marcador de la partida pasa a
ser las estadísticas de la sesión: para el jugador cuya cuenta de Steam está con
sesión iniciada en este equipo (desde `loginusers.vdf` de Steam), con sus nombres
sencillos - bajas, muertes, asistencias, ADR, KAST, porcentaje de aciertos en la
cabeza, primeras bajas, remontadas - y el marcador y las rondas.

El mismo módulo sirve también a: [Dota 2 (repeticiones)](game-dota-replays.md), [osu! (repeticiones)](game-osu-replays.md), [Squad (repeticiones)](game-squad-demos.md), [War Thunder (repeticiones)](game-warthunder-replays.md), [World of Tanks (repeticiones)](game-wot-replays.md), [World of Warships (repeticiones)](game-wows-replays.md).

## Posiciones y ejes {#positions-and-axes}

| | |
|---|---|
| Posiciones registradas | sí |
| Eje vertical | `z` |
| Unidades | pulgadas (unidades de Source) |
| Reflejado para el visor | `y` |
| Escala de unidades (`scale`: el visor multiplica las posiciones por ella) | 1 |

Esto va al `meta.json` de cada sesión (`axes`) y, cuando la sesión tiene posiciones, al pie de `heat.parquet`, así que el visor de 3DHeat gira y escala las filas por sí mismo: véase [Los datos](the-data.md).

## Multijugador {#multiplayer}

- Marcado como jugado en línea (`multiplayer`): **sí**. `games --markdown` lo muestra como "permitido (solo lee lo que publica el juego)".
- Tipo `replay`: lee solo lo que el juego o la plataforma entrega (las repeticiones y demos que guarda el juego), así que graba también en el juego en línea; la marca solo decide si la memoria puede leerse alguna vez.
- Memoria: **nunca** la lee este adaptador. Solo los adaptadores `memory` leen la memoria, y nunca en un juego marcado como jugado en línea: véase [Fuentes y reglas](sources-and-rules.md).

## Estadísticas registradas {#statistics-recorded}

Claves de estadística que el código de este adaptador fija por nombre (el `stats` de cada sesión en `meta.json` y la tabla `stats` de `watcher.sqlite`):

`map`, `rounds`, `score.{team}`, `won`

Una clave entre llaves se completa en tiempo de ejecución (`score.{team}` es una clave por equipo). Las claves que el código toma de una tabla de campos del juego o de los nombres de estadísticas propios del juego no aparecen en esta lista; "Qué se graba" más arriba las nombra.

## Completitud {#completeness}

El conversor que ejecuta este adaptador sigue la [regla de conversores](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md) de 3DHeat: lo que contiene la repetición se lee o se guarda, nunca se descarta - se lee en la tabla y en el documento de la partida, y todo lo demás se guarda completo en archivos auxiliares junto a ellos, contado en `selfCheck.completeness` del documento de la partida. La documentación del propio conversor enumera lo que lee, lo que guarda en bruto y lo que no puede leer.

## Verificación {#verified}

el conversor se prueba con demos reales de torneos; el seguimiento de la carpeta y las estadísticas, con pruebas

## Fuente {#source}

[heat3d_watch/adapters/replays.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/replays.py)

<!-- Generated from the adapter by tools/gen_game_pages.py; change the adapter and run it again rather than editing this page. -->
