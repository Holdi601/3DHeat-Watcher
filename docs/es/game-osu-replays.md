---
title: "osu! (repeticiones)"
nav_order: 35
lang: es
source: game-osu-replays.md
source_hash: "9a1c74c4d5e0"
nav_exclude: true
search_exclude: true
---
# osu! (repeticiones) {#osu-replays}

Después de una partida de osu!, el watcher convierte la repetición que guardó el juego en archivos que puedes ver en un mapa del visor de 3DHeat.

*Detalles técnicos: adaptador `osu-replays`, tipo [`replay`](sources-and-rules.md); se ejecuta todo el tiempo (no espera a que se inicie un juego) y busca datos nuevos cada 5 s.*

## Qué se graba {#what-is-recorded}

- la trayectoria del cursor sobre el campo de juego (x 0..512, y 0..384) y las teclas pulsadas, en cada fotograma
- puntuación, combo, 300s/100s/50s/gekis/katus/fallos, precisión, mods, combo perfecto
- la barra de vida durante la jugada, los hashes del mapa y de la repetición, la semilla aleatoria, el id de puntuación en línea

## De dónde sale {#where-it-comes-from}

repeticiones que guarda osu! (estable): %LOCALAPPDATA%/osu!/Data/r/\*.osr (cada jugada) y osu!/Replays/\*.osr (exportadas)

## Cómo activarlo {#how-to-switch-it-on}

No hace falta activar nada: el watcher lee la fuente tal como la entrega el juego o la plataforma.

## Cómo funciona {#how-it-works}

Repeticiones y demos: lo que un juego guarda de una partida, convertido cuando la partida ha terminado.

Una repetición guarda todo lo que una interfaz en vivo se guarda en los juegos multijugador:
la posición de cada jugador, cada muerte donde ocurrió; y es un archivo que el
juego escribe para sus jugadores, así que leerlo no toca nada del juego. El watcher mira las carpetas
donde los juegos las guardan, espera a que un archivo nuevo deje de crecer (si no, el juego todavía
lo está escribiendo) y lo convierte en un hilo de trabajo, para que una conversión larga nunca detenga
el resto del watcher.

La primera vez que se ve una carpeta, las repeticiones que ya contiene solo se anotan, no se convierten:
un jugador con años de demos encontraría el watcher ocupado durante un día. `python -m heat3d_watch replays <adaptador> [carpeta]` convierte las
existentes cuando se pide.

#### osu! {#osu}

osu! (estable) guarda cada jugada en `osu!/Data/r/*.osr` y las exportadas en
`osu!/Replays/`. El watcher las lee él mismo, según el formato que publica la wiki de osu!: la trayectoria
del cursor y las teclas en cada fotograma, la línea de puntuación, la barra de vida, la semilla y el
id de puntuación; el archivo se guarda completo al lado, por partes, en
`heat.raw.parquet` de la sesión.

El mismo módulo también sirve para: [Counter-Strike 2 (repeticiones)](game-cs2-demos.md), [Dota 2 (repeticiones)](game-dota-replays.md), [Squad (repeticiones)](game-squad-demos.md), [War Thunder (repeticiones)](game-warthunder-replays.md), [World of Tanks (repeticiones)](game-wot-replays.md), [World of Warships (repeticiones)](game-wows-replays.md).

## Posiciones y ejes {#positions-and-axes}

| | |
|---|---|
| Posiciones grabadas | sí |
| Eje hacia arriba | `y` |
| Unidades | píxeles de osu! (campo de juego 512 x 384) |
| Reflejado para el visor | `z` |
| Escala de unidades (`scale`: el visor multiplica las posiciones por ella) | 1 |

Esto va a `meta.json` (`axes`) de cada sesión y, cuando la sesión tiene posiciones, al pie de `heat.parquet`, así que el visor de 3DHeat gira y escala las filas por sí mismo; mira [Los datos](the-data.md).

## Multijugador {#multiplayer}

- Marcado como jugado en línea (`multiplayer`): **sí**. `games --markdown` lo muestra como "permitido (solo lee lo que publica el juego)".
- Tipo `replay`: solo lee lo que el juego o la plataforma entregan (repeticiones y demos que guarda el juego), así que graba también en línea, igual que sin conexión; la marca solo decide si se puede leer la memoria.
- Memoria: este adaptador **nunca** la lee. Solo los adaptadores `memory` leen memoria, y nunca en un juego marcado como jugado en línea; mira [Fuentes y reglas](sources-and-rules.md).

## Estadísticas que se graban {#statistics-recorded}

Claves de estadística que el código de este adaptador asigna por nombre (el `stats` de cada sesión en `meta.json` y la tabla `stats` de `watcher.sqlite`):

`accuracy`, `full_combo`

Una clave entre llaves se completa en tiempo de ejecución (`score.{team}` es una clave por equipo). Las claves que el código toma de una tabla de campos del juego o de sus nombres de estadística no aparecen en esta lista; "Qué se graba" más arriba las nombra.

## Completitud {#completeness}

El watcher sigue la [regla del convertidor](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md) de 3DHeat: lo que la fuente contiene se lee o se guarda, nunca se descarta. Además de las filas, cada paquete, página, línea o respuesta que recibe el adaptador se guarda completo en `heat.raw.parquet` de la sesión (columnas `time`, `ms`, `type`, `used`, `payload`, `text`, y cualquier campo guardado por nombre; `used` marca lo que también se convirtió en filas), y `selfCheck.completeness` de `meta.json` cuenta cada `type`; `lost` es 0.

**Se lee**

- cada fotograma: una fila en su instante (los milisegundos sumados), x e y sobre el campo de juego, `keys` los bits de teclas (ratón 1 y 2, teclas 1 y 2, humo); en mania, x guarda las teclas pulsadas en vez de un lugar
- la cabecera, cada campo: modo, versión, el MD5 del mapa (el archivo nombra el mapa solo por él), el jugador, el MD5 de la repetición, 300s, 100s, 50s, gekis, katus, fallos, puntuación, combo máximo, combo perfecto, mods (por nombre en `osu.modNames` de meta.json), la hora de la jugada; como estadísticas y en `osu` de meta.json
- el gráfico de la barra de vida: una fila `life` por punto (tiempo, vida 0..1)
- el fotograma `-12345`: la semilla aleatoria (`osu.seed`); el id de puntuación en línea (`osu.scoreId`); con Target Practice, su precisión (`osu.targetPracticeAccuracy`)

**Se guarda en bruto**

- el archivo completo, por partes, en heat.raw.parquet (`offset` donde empieza cada una, así las partes son el archivo): `header`, `replay_data` (los fotogramas comprimidos con LZMA tal como se guardan), `score_id`, `mod_info`, y `trailing` para lo que sigue a las partes que describe el formato (las exportaciones de osu!lazer añaden datos ahí): se guarda, no se lee

**No disponible**

- el propio mapa (objetos de golpe, temporización): no está en una repetición; se nombra solo por su MD5
- las repeticiones de osu!lazer: se guardan en su base de datos, no como archivos

**Tamaño**: el archivo bruto de la sesión tiene aproximadamente el tamaño de la repetición (decenas a cientos de kilobytes)

## Verificado {#verified}

probado con repeticiones construidas según el formato .osr publicado; osu!lazer guarda las repeticiones en su propio almacén y no se lee

## Fuente {#source}

[heat3d_watch/adapters/replays.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/replays.py)

<!-- Generated from the adapter by tools/gen_game_pages.py; change the adapter and run it again rather than editing this page. -->
