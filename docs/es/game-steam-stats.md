---
title: "Estadísticas de Steam (plataforma)"
nav_order: 43
lang: "es"
source: game-steam-stats.md
source_hash: "24fa6512bd6d"
nav_exclude: true
search_exclude: true
---
# Estadísticas de Steam (plataforma) {#steam-statistics-platform}

El watcher guarda lo que las estadísticas de Steam conservan sobre tus juegos, para que puedas mirar tu historial más tarde como estadísticas y como línea de tiempo.

*Detalles técnicos: adaptador `steam-stats`, tipo [`platform`](sources-and-rules.md); funciona todo el tiempo (no espera a que empiece un juego) y busca datos nuevos cada 30 s.*

## Qué se graba {#what-is-recorded}

- cada estadística que un juego guarda en Steam (sus propios nombres y valores), por juego, cuando cambia
- los logros desbloqueados, con su nombre visible, su descripción y la hora de desbloqueo
- los cambios de estadística, con el valor anterior, el nuevo y la diferencia
- el tiempo de juego (minutos, últimas dos semanas) y la hora de la última partida

## De dónde viene {#where-it-comes-from}

la caché local de estadísticas de Steam %STEAM%\appcache\stats\UserGameStats_&lt;cuenta>_&lt;appid>.bin con UserGameStatsSchema_&lt;appid>.bin; el tiempo de juego, de %STEAM%\userdata\\&lt;cuenta>\config\localconfig.vdf (%STEAM% desde HKCU\Software\Valve\Steam SteamPath)

## Cómo activarlo {#how-to-switch-it-on}

No hay que activar nada: el watcher lee la fuente tal como la entrega el juego o la plataforma.

## Cómo funciona {#how-it-works}

Lo que el lanzador y el controlador gráfico guardan sobre la partida: las
estadísticas, los logros, el tiempo de juego y las líneas de tiempo de Steam, y
los destacados y clips de NVIDIA.

Ninguna de estas fuentes necesita que un juego colabore ni que esté en marcha, así
que los tres adaptadores de aquí están siempre activos y miran unos pocos archivos
cada pocos segundos.

#### Estadísticas de Steam (`steam-stats`) {#steam-statistics-steam-stats}

`<Steam>\appcache\stats\UserGameStats_<cuenta>_<appid>.bin`, que el cliente de
Steam reescribe cada vez que un juego guarda sus estadísticas, decodificado con
el esquema `UserGameStatsSchema_<appid>.bin` que está junto a él (KeyValues
binario, véase `_steam.py`). Las estadísticas son enteros o decimales según las
defina el juego; los logros son bits con una hora de desbloqueo en segundos Unix.
El tiempo de juego está en `<Steam>\userdata\<cuenta>\config\localconfig.vdf`
bajo apps/&lt;appid>: Playtime y Playtime2wks en minutos, LastPlayed en segundos
Unix. Steam se encuentra por HKCU\Software\Valve\Steam SteamPath.
API de estadísticas: <https://partner.steamgames.com/doc/features/achievements>

El mismo módulo sirve también a: [Destacados de NVIDIA (plataforma)](game-nvidia-highlights.md), [Línea de tiempo de Steam (plataforma)](game-steam-timeline.md).

## Posiciones y ejes {#positions-and-axes}

| | |
|---|---|
| Posiciones registradas | no |
| Eje vertical | `y` |
| Unidades | metros |
| Reflejado para el visor | ninguno |
| Escala de unidades (`scale`: el visor multiplica las posiciones por ella) | 1 |

Esto va al `meta.json` de cada sesión (`axes`) y, cuando la sesión tiene posiciones, al pie de `heat.parquet`, así que el visor de 3DHeat gira y escala las filas por sí mismo: véase [Los datos](the-data.md).

## Multijugador {#multiplayer}

- Marcado como jugado en línea (`multiplayer`): **no**. `games --markdown` lo muestra como "un jugador".
- Tipo `platform`: lee solo lo que el juego o la plataforma entrega (lo que guardan Steam o el controlador gráfico), así que graba también en el juego en línea; la marca solo decide si la memoria puede leerse alguna vez.
- Memoria: **nunca** la lee este adaptador. Solo los adaptadores `memory` leen la memoria, y nunca en un juego marcado como jugado en línea: véase [Fuentes y reglas](sources-and-rules.md).

## Estadísticas registradas {#statistics-recorded}

Claves de estadística que el código de este adaptador fija por nombre (el `stats` de cada sesión en `meta.json` y la tabla `stats` de `watcher.sqlite`):

`achievements_total`, `achievements_unlocked`, `last_played`, `playtime_2wks_minutes`, `playtime_minutes`

Una clave entre llaves se completa en tiempo de ejecución (`score.{team}` es una clave por equipo). Las claves que el código toma de una tabla de campos del juego o de los nombres de estadísticas propios del juego no aparecen en esta lista; "Qué se graba" más arriba las nombra.

## Completitud {#completeness}

El watcher sigue la [regla de conversores](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md) de 3DHeat: lo que contiene la fuente se lee o se guarda, nunca se descarta. Además de las filas, cada paquete, página, línea o respuesta que recibe el adaptador se guarda completo en el `heat.raw.parquet` de la sesión (columnas `time`, `ms`, `type`, `used`, `payload`, `text`, y los campos que se guardan por nombre); `used` marca lo que también se convirtió en filas, y `selfCheck.completeness` de `meta.json` cuenta cada `type` - `lost` es 0.

**Leído**

- cada estadística del archivo de estadísticas por su nombre en la API (entero, decimal, avgrate), cada bit de logro con su hora de desbloqueo, con nombre y descripción según el esquema
- los cambios respecto a la última lectura (anterior, nuevo, diferencia), los nuevos desbloqueos; el tiempo de juego, el de las dos últimas semanas y la última partida, de localconfig.vdf

**Guardado en bruto**

- `UserGameStats`: los bytes del archivo de estadísticas, completos, cada vez que se registra (el `crc`, `PendingChanges`, los bits de logro que el esquema ya no define y cualquier clave que el decodificador omita están dentro)
- `UserGameStatsSchema`: los bytes del archivo de esquema junto a él, para que las estadísticas puedan decodificarse solo desde la sesión (los nombres de cada estadística y logro en todos los idiomas, iconos, indicadores)
- `localconfig_app`: el bloque completo del juego en localconfig.vdf como JSON (estado de la sincronización en la nube, opciones de inicio, insignias y cualquier otra clave que Steam guarde por juego) cuando se registra su tiempo de juego
- un archivo de estadísticas que el decodificador no puede leer (cortado a mitad de escritura, o con un formato nuevo): sus bytes y el esquema en una sesión sin filas (`used` falso; `unreadable` en meta.json)

**No disponible**

- el resto de localconfig.vdf (amigos, chat, ajustes de Steam): no es del juego, y es privado
- los valores de estadística entre dos escrituras: Steam reescribe el archivo cuando el juego guarda sus estadísticas, normalmente al cerrarse
- los porcentajes globales de logros y las estadísticas de otros jugadores: están en los servidores de Steam, no aquí

**Tamaño**: unos pocos KB por sesión de juego registrada, más el esquema (hasta unos cientos de KB para un juego con muchos logros) - muy por debajo de 1 MB por hora de juego; zstd reduce a la mitad o más el texto del esquema

## Verificación {#verified}

probado con archivos de estadísticas y esquemas reales de una instalación local; detección de cambios probada con archivos generados en formato KeyValues binario

## Fuente {#source}

[heat3d_watch/adapters/platform.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/platform.py)

<!-- Generated from the adapter by tools/gen_game_pages.py; change the adapter and run it again rather than editing this page. -->
