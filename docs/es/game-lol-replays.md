---
title: "League of Legends (repeticiones)"
nav_order: 30
lang: "es"
source: game-lol-replays.md
source_hash: "6a86dc8a45bb"
nav_exclude: true
search_exclude: true
---
# League of Legends (repeticiones) {#league-of-legends-replays}

Después de una partida de League of Legends, el watcher convierte la repetición que guardó el juego en archivos que puedes ver en un mapa del visor de 3DHeat.

*Detalles técnicos: adaptador `lol-replays`, tipo [`replay`](sources-and-rules.md); se ejecuta todo el tiempo (no espera a que empiece una partida) y busca datos nuevos cada 5 s.*

## Qué se graba {#what-is-recorded}

- el campeón, rol, equipo, muertes, bajas, asistencias, oro, daño a campeones y resultado de cada jugador, y cada otro número de la tabla de resultados final
- tu línea como estadísticas, y tus filas marcadas como tuyas (`player` en meta.json), con tu Riot ID en los ajustes
- con tu propia clave de la API de Riot: la posición de cada jugador cada minuto con las estadísticas de ese minuto, y cada evento de la línea de tiempo (muertes donde ocurrieron, edificios, monstruos, wards, objetos, habilidades), en la hora de reloj que da la línea de tiempo
- cada parte del archivo de la repetición guardada entera en heat.raw.parquet; no se decodifica: la partida momento a momento, que va cifrada y ofuscada contra las trampas

## De dónde viene {#where-it-comes-from}

las repeticiones que guarda el cliente de League: `%USERPROFILE%/Documents/League of Legends/Replays/\*.rofl` (solo los metadatos sencillos del final de la partida); con tu propia clave de la API de Riot, la línea de tiempo oficial de la partida de la API Match-V5 de Riot

## Cómo activarlo {#how-to-switch-it-on}

guarda una repetición en el cliente de League (historial de partidas > descargar) e instala el lector: github.com/Holdi601/3DHeat-Ext-Riot (`heat3d-riot-replays`); para las posiciones, pon riot_api_key y riot_platform con `config --set`

Ajustes desde variables de entorno:

- `HEAT3D_RIOT_REPLAYS`: la carpeta del lector (un clon o una versión descomprimida), cuando no está instalado o junto al watcher

## Cómo funciona {#how-it-works}

Repeticiones de League of Legends y VALORANT: lo que de ellas se puede leer tal cual.

Ambos juegos guardan las repeticiones en el disco del jugador, y los dos protegen lo que va dentro: los datos de la partida momento a momento están ofuscados, y de forma distinta con cada parche, para impedir que se usen para hacer trampa. Esa parte no se decodifica en ningún sitio de 3DHeat. Lo que cada archivo lleva a la vista se lee, y el resto se guarda tal como está: cada parte del archivo, entera, en `heat.raw.parquet` de la sesión (regla de conversión de 3DHeat, docs/converters.md en el repositorio del visor), contada en `selfCheck.completeness` de meta.json.

El watcher no lee los archivos por sí mismo: lo hace un lector externo (3DHeat Riot, github.com/Holdi601/3DHeat-Ext-Riot, `exporters/ext/riot-replays`, comando `heat3d-riot-replays`), un proyecto propio. Si lo encuentra en el PATH, instalado o junto al watcher, lee cada repetición nueva; si falta, el watcher indica una sola vez cómo instalarlo. Lo que lee, el watcher lo registra en la sesión; la línea de tiempo Match-V5 de más abajo la descarga el propio watcher, porque no está en el archivo.

#### League of Legends (.rofl) {#league-of-legends-rofl}

`%USERPROFILE%\Documents\League of Legends\Replays\*.rofl`. Las dos versiones del contenedor llevan la tabla de resultados final como JSON sin cifrar (`statsJson`): para cada uno de los diez jugadores, el campeón, muertes, bajas, asistencias, oro, daño a campeones, objetos, equipo, rol, victoria, su Riot ID, y cada otro número que el juego suma (más de cien por jugador); todos pasan a la fila `player_result` del jugador. ROFL1 (parche 14.9 y anteriores) lo tiene tras una cabecera fija (`RIOT\0\0`, una firma de 256 bytes y luego las longitudes); ROFL2 (14.11 en adelante, `RIOT\2\0`) lo tiene al final del archivo, con su longitud en los últimos cuatro bytes (lo indica un ingeniero de Riot, ReplayBook número 299). La cabecera de carga de ROFL1 (id de partida, longitud, cuentas de fragmentos y keyframes, longitud de la clave del fragmento) y su tabla de fragmentos (id, tipo, longitud, siguiente fragmento, desplazamiento) están a la vista y se leen; los propios fragmentos van cifrados y se guardan enteros sin leer.

Las posiciones no vienen del archivo. Con una clave de desarrollador de Riot del propio jugador (`riot_api_key` en los ajustes; una clave personal está pensada justo para esto, "mostrar tus estadísticas (propias)"), se descarga de la API Match-V5 de Riot la línea de tiempo oficial de la partida: la posición de cada jugador una vez por minuto con todo lo que el fotograma de ese minuto dice de él (oro, experiencia, nivel, súbditos, estadísticas de campeón y de daño), y cada evento de la línea de tiempo (muertes, edificios, monstruos élite, wards, objetos, habilidades, niveles), cada uno como una fila, colocada donde ocurrió cuando tiene lugar. Sin clave no se descarga nada y no se envía nada.

El mismo módulo también sirve a: [VALORANT (repeticiones)](game-valorant-replays.md).

## Posiciones y ejes {#positions-and-axes}

| | |
|---|---|
| Posiciones grabadas | sí |
| Eje hacia arriba | `y` |
| Unidades | unidades del mapa de la Grieta del Invocador (unos 15000 de lado a lado) |
| Reflejado para el visor | ninguno |
| Escala de unidad (`scale`: el visor multiplica las posiciones por ella) | 1 |

Esto va al `meta.json` de cada sesión (`axes`) y, cuando la sesión tiene posiciones, al pie de `heat.parquet`, para que el visor de 3DHeat gire y escale las filas por sí solo; ver [Los datos](the-data.md).

## Multijugador {#multiplayer}

- Marcado como jugado en línea (`multiplayer`): **sí**. `games --markdown` muestra esto como "permitido (solo lee lo que publica el juego)".
- Tipo `replay`: solo lee lo que el juego o la plataforma entregan (las repeticiones y demos que guarda el juego), así que graba también en el juego en línea, además del juego sin conexión. La marca solo decide si la memoria puede leerse alguna vez.
- Memoria: **nunca** la lee este adaptador. Solo los adaptadores `memory` leen memoria, y nunca en un juego marcado como jugado en línea; ver [Fuentes y reglas](sources-and-rules.md).

## Estadísticas registradas {#statistics-recorded}

Claves de estadística que el código de este adaptador asigna por nombre (el `stats` de cada sesión en `meta.json` y la tabla `stats` de `watcher.sqlite`):

`champion`, `game_seconds`, `won`

Una clave entre llaves se completa en tiempo de ejecución (`score.{team}` es una clave por equipo). Las claves que el código toma de una tabla de campos del juego o de sus propios nombres de estadística no aparecen en esta lista; "Qué se graba" de arriba las nombra.

## Completitud {#completeness}

El watcher sigue la [regla de conversión](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md) de 3DHeat: lo que trae la fuente se lee o se guarda, nunca se descarta. Además de las filas, cada paquete, página, línea o respuesta que recibe el adaptador se guarda entero en `heat.raw.parquet` de la sesión (columnas `time`, `ms`, `type`, `used`, `payload`, `text`, y cualquier campo guardado por nombre; `used` marca lo que también se volvió filas), y `selfCheck.completeness` de `meta.json` cuenta cada `type`: `lost` es 0.

**Se lee**

- el JSON de metadatos: duración de la partida, versión, ids del último fragmento y del último keyframe, y `statsJson`: cada campo de la tabla de resultados de cada jugador, en su fila `player_result` (los números escritos como texto se leen como números)
- ROFL1: el bloque de longitudes, la cabecera de carga (id de partida, duración, cuentas de keyframes y fragmentos, ids de los fragmentos de arranque e inicio de partida, intervalo de keyframes, la clave del fragmento tal como está guardada) y la tabla de fragmentos (id, tipo, longitud, siguiente fragmento, desplazamiento): en `rofl` de meta.json y en el `text` de las filas en bruto
- ROFL2: la cadena de versión
- la línea de tiempo Match-V5 (solo con tu propia clave de la API): cada fotograma de participante en una fila `position` (o `participant_frame` si no tiene lugar), con todos sus campos aplanados (`championStats.armor`, `damageStats.totalDamageDone`, `currentGold`, `xp`, ...); cada evento como una fila con el nombre de su tipo, colocada donde tiene `position`; CHAMPION_KILL como una baja y una muerte

**Se guarda en bruto**

- cada parte del .rofl, entera, en orden de archivo (`offset`), de modo que las partes son el archivo: `magic`, `signature`, `lengths`, `metadata`, `payload_header`, `chunk_header`, `chunk`, `keyframe` (ROFL1); `body`, `metadata`, `metadata_length` (ROFL2); cualquier trozo que no cubra ninguna parte, como `unknown`
- la línea de tiempo entera: `timeline <type>` para cada evento, `timeline participantFrame` para el fotograma de cada jugador (`participant` es su id), `timeline` para el resto

**No disponible**

- el propio juego (posiciones, habilidades, cada unidad, momento a momento): los fragmentos de ROFL1 y el body de ROFL2 van cifrados, y los paquetes de dentro están ofuscados con cada parche. Se guarda entero, no se lee
- posiciones sin tu propia clave de la API de Riot: el archivo no las tiene a la vista

**Tamaño**: la copia en bruto ocupa aproximadamente lo mismo que la propia repetición: los fragmentos cifrados no se comprimen

## Verificado {#verified}

El lector (heat3d-riot-replays) probado con archivos construidos según las estructuras de roflxd.cs (MIT); la línea de tiempo, según el JSON documentado de Match-V5; no había ninguna repetición real con la que comprobarlo

## Fuente {#source}

[heat3d_watch/adapters/riot_replays.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/riot_replays.py)

<!-- Generated from the adapter by tools/gen_game_pages.py; change the adapter and run it again rather than editing this page. -->
