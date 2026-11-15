---
title: "World of Warships (repeticiones)"
nav_order: 49
lang: "es"
source: game-wows-replays.md
source_hash: "c822aca3f6fe"
nav_exclude: true
search_exclude: true
---
# World of Warships (repeticiones) {#world-of-warships-replays}

Después de una partida de World of Warships, el watcher convierte la repetición que guardó el juego en archivos que puedes ver sobre un mapa en el visor de 3DHeat.

*Detalles técnicos: adaptador `wows-replays`, tipo [`replay`](sources-and-rules.md); funciona todo el tiempo (no espera a que empiece una partida) y busca datos nuevos cada 5 s.*

## Qué se graba {#what-is-recorded}

- la posición y el rumbo de cada barco mientras el cliente que grabó lo veía (unas 6 o 7 veces por segundo mientras se mueve), el barco del propio jugador todo el tiempo
- aliado o enemigo, y el barco (el del jugador que grabó por su nombre, los demás por el número de barco del juego); los barcos hundidos donde se hundieron y sus atacantes donde estaban
- el mapa; el barco, las bajas y la supervivencia del jugador que grabó, como estadísticas

## De dónde viene {#where-it-comes-from}

repeticiones que guarda World of Warships: &lt;World of Warships>/replays/\*.wowsreplay (con las repeticiones activadas), convertidas por el conversor externo `heat3d-wows-replay` (exporters/ext/wows-replay)

## Cómo activarlo {#how-to-switch-it-on}

activa la grabación de repeticiones en World of Warships (`isReplayEnabled` en su preferences.xml, o el ajuste propio del juego donde lo tenga) e instala el conversor: pip install -e &lt;3DHeat>/exporters/ext/wows-replay

Ajustes desde variables de entorno:

- `HEAT3D_WOWS_REPLAY`: la carpeta del conversor (un clon o una versión descomprimida), cuando no está instalado ni junto al watcher

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

#### World of Tanks y World of Warships {#world-of-tanks-and-world-of-warships}

Ambos guardan una repetición de cada batalla en `<juego>/replays/` cuando la
grabación está activada (`*.wotreplay`, `*.wowsreplay`); las instalaciones se
encuentran por la lista del Wargaming Game Center, `C:/Games/World_of_Tanks*` /
`World_of_Warships*`, y por Steam. Como con War Thunder, el watcher no lee los
archivos por sí mismo: lo hace un conversor externo de cada uno
(`exporters/ext/wot-replay`, comando `heat3d-wot-replay`; `exporters/ext/wows-replay`,
comando `heat3d-wows-replay`), separados para que un problema con las condiciones de
Wargaming afecte solo a ese conversor. Si se encuentra en el PATH, está instalado o
junto al watcher, convierte cada repetición nueva en `<mapa>/<partida>.parquet` y
`<partida>.match.json` en la carpeta de la sesión; si falta, el watcher dice una vez
cómo instalarlo. La línea del jugador que grabó - vehículo o barco, bajas, daño
(World of Tanks), si sobrevivió, y el resultado (World of Tanks) - pasa a ser las
estadísticas de la sesión. Lo que lee cada conversor, y lo que no, está en su README.

El mismo módulo sirve también a: [Counter-Strike 2 (repeticiones)](game-cs2-demos.md), [Dota 2 (repeticiones)](game-dota-replays.md), [osu! (repeticiones)](game-osu-replays.md), [Squad (repeticiones)](game-squad-demos.md), [War Thunder (repeticiones)](game-warthunder-replays.md), [World of Tanks (repeticiones)](game-wot-replays.md).

## Posiciones y ejes {#positions-and-axes}

| | |
|---|---|
| Posiciones registradas | sí |
| Eje vertical | `y` |
| Unidades | unidades del mundo de World of Warships (x este, y arriba, z norte; una equivale a 15 m según la geometría del casco, y a 30 m según los alcances del juego) |
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
