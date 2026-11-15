---
title: "War Thunder (repeticiones)"
nav_order: 46
lang: "es"
source: game-warthunder-replays.md
source_hash: "81f03926431d"
nav_exclude: true
search_exclude: true
---
# War Thunder (repeticiones) {#war-thunder-replays}

Después de una partida de War Thunder, el watcher convierte la repetición que guardó el juego en archivos que puedes ver sobre un mapa en el visor de 3DHeat.

*Detalles técnicos: adaptador `warthunder-replays`, tipo [`replay`](sources-and-rules.md); funciona todo el tiempo (no espera a que empiece una partida) y busca datos nuevos cada 5 s.*

## Qué se graba {#what-is-recorded}

- la posición y la actitud de cada avión unas 4 veces por segundo (las que contenga la repetición)
- las posiciones de las unidades terrestres, de la sincronización terrestre de la repetición (en repeticiones de 2026; no en las de 2025)
- quién era cada unidad (jugador, id del vehículo, equipo) cuando una baja o un impacto la nombra; bajas, muertes y impactos donde ocurrieron; el chat; el mapa
- las bajas, muertes, puntuación y capturas del autor de la repetición como estadísticas

## De dónde viene {#where-it-comes-from}

repeticiones que guarda War Thunder: &lt;War Thunder>/Replays/\*.wrpl (con el guardado de repeticiones activado), convertidas por el conversor externo `heat3d-wt-replay` (exporters/ext/warthunder-replay)

## Cómo activarlo {#how-to-switch-it-on}

activa el guardado de repeticiones en las opciones de War Thunder e instala el conversor: pip install -e &lt;3DHeat>/exporters/ext/warthunder-replay

Ajustes desde variables de entorno:

- `HEAT3D_WT_REPLAY`: la carpeta del conversor (un clon o una versión descomprimida), cuando no está instalado ni junto al watcher

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

#### War Thunder {#war-thunder}

War Thunder guarda una repetición de cada batalla en `<War Thunder>/Replays/*.wrpl`
cuando el guardado de repeticiones está activado en sus opciones. El watcher no
las lee por sí mismo: lo hace un conversor externo (el conversor de repeticiones de
War Thunder de 3DHeat, `exporters/ext/warthunder-replay`, comando
`heat3d-wt-replay`), separado para que un problema en él no afecte a nada más.
Cuando el comando está en el PATH, o el paquete está instalado o junto al watcher,
cada repetición nueva pasa por él y deja en la carpeta de la sesión
`<mapa>/<partida>.parquet` y `<partida>.match.json`; cuando no lo está, el watcher
dice una vez cómo instalarlo y deja la carpeta en paz. Lo que lee el conversor, y
lo que no, está en su README. La línea de resultados del autor de la repetición -
bajas, bajas terrestres, muertes, asistencias, puntuación, capturas - pasa a ser
las estadísticas de la sesión.

El mismo módulo sirve también a: [Counter-Strike 2 (repeticiones)](game-cs2-demos.md), [Dota 2 (repeticiones)](game-dota-replays.md), [osu! (repeticiones)](game-osu-replays.md), [Squad (repeticiones)](game-squad-demos.md), [World of Tanks (repeticiones)](game-wot-replays.md), [World of Warships (repeticiones)](game-wows-replays.md).

## Posiciones y ejes {#positions-and-axes}

| | |
|---|---|
| Posiciones registradas | sí |
| Eje vertical | `y` |
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

`map`

Una clave entre llaves se completa en tiempo de ejecución (`score.{team}` es una clave por equipo). Las claves que el código toma de una tabla de campos del juego o de los nombres de estadísticas propios del juego no aparecen en esta lista; "Qué se graba" más arriba las nombra.

## Completitud {#completeness}

El conversor que ejecuta este adaptador sigue la [regla de conversores](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md) de 3DHeat: lo que contiene la repetición se lee o se guarda, nunca se descarta - se lee en la tabla y en el documento de la partida, y todo lo demás se guarda completo en archivos auxiliares junto a ellos, contado en `selfCheck.completeness` del documento de la partida. La documentación del propio conversor enumera lo que lee, lo que guarda en bruto y lo que no puede leer.

## Verificación {#verified}

el conversor se comprueba con repeticiones públicas de varias versiones del juego (las bajas y los nombres concuerdan con los resultados) y con pruebas sobre repeticiones generadas; este gancho, con pruebas usando un comando de sustitución

## Fuente {#source}

[heat3d_watch/adapters/replays.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/replays.py)

<!-- Generated from the adapter by tools/gen_game_pages.py; change the adapter and run it again rather than editing this page. -->
