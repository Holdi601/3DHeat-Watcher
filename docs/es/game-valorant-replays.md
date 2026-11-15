---
title: "VALORANT (repeticiones)"
nav_order: 45
lang: "es"
source: game-valorant-replays.md
source_hash: "10a648aabdf1"
nav_exclude: true
search_exclude: true
---
# VALORANT (repeticiones) {#valorant-replays}

Después de una partida de VALORANT, el watcher convierte la repetición que guardó el juego en archivos que puedes ver como estadísticas y una línea de tiempo.

*Detalles técnicos: adaptador `valorant-replays`, tipo [`replay`](sources-and-rules.md); se ejecuta todo el tiempo (no espera a que empiece una partida) y busca datos nuevos cada 5 s.*

## Qué se graba {#what-is-recorded}

- el mapa, el id de la partida y los agentes elegidos; el bloque de información de la repetición (duración, versiones, nombre, fecha de grabación, indicadores de compresión y cifrado)
- la línea de tiempo de eventos del servidor: muertes (asesino y víctima como ids de red), inicios de ronda, spikes plantados, desactivados y explotados, ultimates usados, cambios de bando; cada uno con su id y sus metadatos
- cada fragmento del archivo guardado entero en heat.raw.parquet; no se decodifica: posiciones, nombres o marcadores, que están en el flujo ofuscado

## De dónde viene {#where-it-comes-from}

las repeticiones que guarda VALORANT: `%LOCALAPPDATA%/VALORANT/Saved/Demos/\*.vrf` (solo las partes que no están ofuscadas)

## Cómo activarlo {#how-to-switch-it-on}

guarda una repetición en VALORANT (carrera > partida > descargar repetición)

## Cómo funciona {#how-it-works}

Repeticiones de League of Legends y VALORANT: lo que de ellas se puede leer tal cual.

Ambos juegos guardan las repeticiones en el disco del jugador, y los dos protegen lo que va dentro: los datos de la partida momento a momento están ofuscados, y de forma distinta con cada parche, para impedir que se usen para hacer trampa. Para atravesarlo habría que desensamblar el código del propio juego, algo que prohíben las condiciones de Riot (Términos de Servicio 3.1 y 7.1), así que aquí no se hace. Lo que cada archivo lleva a la vista se lee, y el resto se guarda tal como está: cada parte del archivo, entera, en `heat.raw.parquet` de la sesión (regla de conversión de 3DHeat, docs/converters.md en el repositorio del visor), contada en `selfCheck.completeness` de meta.json.

#### Valorant (.vrf) {#valorant-vrf}

`%LOCALAPPDATA%\VALORANT\Saved\Demos\*.vrf`, una repetición local de Unreal Engine (estructura de vrfkit, Apache-2.0, y ValorantReplayParser, MIT). A la vista: el bloque de información de la repetición (duración, versión de red, changelist, su nombre, cuándo se grabó, si está comprimida o cifrada), el mapa, el id de la partida y los agentes elegidos (en la cabecera), y la línea de tiempo de eventos del propio servidor: muertes (asesino y víctima como ids de red, no como nombres), inicios de ronda, spikes plantados, desactivados y explotados, ultimates usados, cambios de bando, cada uno con su tiempo, id y metadatos. Las posiciones, nombres, marcadores y todo lo demás están en el flujo ofuscado (los fragmentos de datos de repetición y de checkpoint), que se guarda entero sin leer.

El mismo módulo también sirve a: [League of Legends (repeticiones)](game-lol-replays.md).

## Posiciones y ejes {#positions-and-axes}

| | |
|---|---|
| Posiciones grabadas | no |
| Eje hacia arriba | `z` |
| Unidades | unidades del mundo de VALORANT |
| Reflejado para el visor | ninguno |
| Escala de unidad (`scale`: el visor multiplica las posiciones por ella) | 1 |

Esto va al `meta.json` de cada sesión (`axes`) y, cuando la sesión tiene posiciones, al pie de `heat.parquet`, para que el visor de 3DHeat gire y escale las filas por sí solo; ver [Los datos](the-data.md).

## Multijugador {#multiplayer}

- Marcado como jugado en línea (`multiplayer`): **sí**. `games --markdown` muestra esto como "permitido (solo lee lo que publica el juego)".
- Tipo `replay`: solo lee lo que el juego o la plataforma entregan (las repeticiones y demos que guarda el juego), así que graba también en el juego en línea, además del juego sin conexión. La marca solo decide si la memoria puede leerse alguna vez.
- Memoria: **nunca** la lee este adaptador. Solo los adaptadores `memory` leen memoria, y nunca en un juego marcado como jugado en línea; ver [Fuentes y reglas](sources-and-rules.md).

## Estadísticas registradas {#statistics-recorded}

Claves de estadística que el código de este adaptador asigna por nombre (el `stats` de cada sesión en `meta.json` y la tabla `stats` de `watcher.sqlite`):

`kills_in_match`, `map`, `match_seconds`, `rounds`, `spikes_planted`

Una clave entre llaves se completa en tiempo de ejecución (`score.{team}` es una clave por equipo). Las claves que el código toma de una tabla de campos del juego o de sus propios nombres de estadística no aparecen en esta lista; "Qué se graba" de arriba las nombra.

## Completitud {#completeness}

El watcher sigue la [regla de conversión](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md) de 3DHeat: lo que trae la fuente se lee o se guarda, nunca se descarta. Además de las filas, cada paquete, página, línea o respuesta que recibe el adaptador se guarda entero en `heat.raw.parquet` de la sesión (columnas `time`, `ms`, `type`, `used`, `payload`, `text`, y cualquier campo guardado por nombre; `used` marca lo que también se volvió filas), y `selfCheck.completeness` de `meta.json` cuenta cada `type`: `lost` es 0.

**Se lee**

- el bloque de información, cada campo (`vrf` en meta.json): versión del archivo, versiones personalizadas, duración, versión de red, changelist, nombre, indicador de en directo, fecha de grabación, indicadores de comprimido y cifrado, la clave tal como está guardada
- el fragmento de cabecera: el mapa, el id de la partida y los agentes elegidos (buscados por su forma)
- cada fragmento de eventos: id, grupo, metadatos, tiempo de inicio y de fin, y de sus datos, el nombre del evento, su tiempo en segundos y los números que lo preceden (ids de red del asesino y la víctima); una fila por cada uno

**Se guarda en bruto**

- cada fragmento entero, en orden de archivo (`offset`), de modo que las partes son el archivo: `info`, `header`, `event <grupo>`, `replay_data`, `checkpoint`, `chunk <n>` para un tipo que la estructura no nombra, `trailing` para los bytes que siguen al último fragmento completo

**No disponible**

- posiciones, nombres, marcadores, habilidades, cada fotograma del juego: los fragmentos de datos de repetición y de checkpoint están ofuscados; leerlos implicaría desensamblar el cliente, algo que prohíben las condiciones de Riot. Se guardan enteros, sin leer
- el contenido de una repetición cifrada: se recorre y se guarda entera, sin leer nada de dentro

**Tamaño**: la copia en bruto ocupa aproximadamente lo mismo que la propia repetición: el flujo ofuscado no se comprime

## Verificado {#verified}

Construido a partir de la estructura del contenedor documentada por vrfkit (Apache-2.0); sin probar con una repetición real, porque no había ninguna disponible: el lector comprueba antes de leer y omite lo que no coincide

## Fuente {#source}

[heat3d_watch/adapters/riot_replays.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/riot_replays.py)

<!-- Generated from the adapter by tools/gen_game_pages.py; change the adapter and run it again rather than editing this page. -->
