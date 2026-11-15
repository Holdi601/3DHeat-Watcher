---
title: "War Thunder (estado de juego)"
nav_order: 47
lang: es
source: game-warthunder-webmap.md
source_hash: "d6026c277030"
nav_exclude: true
search_exclude: true
---
# War Thunder (estado de juego) {#war-thunder-game-state}

Mientras juegas War Thunder, el watcher guarda lo que el juego informa a programas de tu propio ordenador, para que puedas verlo más tarde en un mapa del visor de 3DHeat.

*Detalles técnicos: adaptador `warthunder-webmap`, tipo [`gsi`](sources-and-rules.md); se ejecuta mientras `aces.exe` está en marcha y busca datos nuevos cada 0,5 s.*

## Qué se graba {#what-is-recorded}

- la posición propia (este/norte del mapa en metros; altura desde /state en aeronave, si no 0) dos veces por segundo, rumbo, velocidad
- apariciones y la salida del vehículo propio del mapa (destruido, aterrizado, de vuelta al hangar), una salida cada vez
- otras aeronaves y unidades terrestres en el minimapa como posiciones con ids seguidos y bando (sin altura)
- aeródromos, zonas de captura y bases una vez, y las zonas que cambian de bando
- líneas del feed de bajas y daños (quién, vehículo, verbo); las bajas y muertes del jugador cuando se configura tu nombre (`config --set player_names.warthunder-webmap=<nombre>`)
- apariciones, distancia, altitud máxima, velocidad verdadera máxima, vehículo; bajas y muertes si tu nombre está configurado
- cada respuesta del mapa web guardada completa en heat.raw.parquet - el /state y /indicators completos, el chat, los objetivos de la batalla y la imagen del mapa incluidos; entre batallas, en una sesión propia

## De dónde viene {#where-it-comes-from}

el mapa web local del juego, <http://127.0.0.1:8111> (/map_info.json, /map_obj.json, /state, /indicators, /hudmsg, /gamechat, /mission.json, /map.img)

## Cómo activarlo {#how-to-switch-it-on}

No hace falta activar nada: el watcher lee la fuente tal como la entrega el juego o la plataforma.

## Cómo funciona {#how-it-works}

War Thunder: el mapa web local del propio juego en <http://127.0.0.1:8111>.

El juego sirve la página que puede mostrar una segunda pantalla o un teléfono (el "mapa web"), y el JSON que hay detrás, mientras se ejecuta - en todos los modos, también el multijugador:

```text
/map_info.json   {"map_min": [x, y], "map_max": [x, y], "grid_steps", "grid_zero", "map_generation",
                  "hud_type", "valid"}: extensiÃ³n del mapa en metros; valid false en el hangar
/map_obj.json    [{"type": aircraft|ground_model|airfield|capture_zone|bombing_point|defending_point|
                  respawn_base_*|..., "icon": Player|Fighter|Bomber|Mediumtank|SPAA|..., "color": "#rrggbb",
                  "x", "y" (0..1 of the map picture, y down), "dx", "dy" (direction),
                  airfields "sx", "sy", "ex", "ey"}]: lo que muestra el minimapa; el propio vehÃ­culo del jugador
                  con el icono "Player"; sin ids ni alturas
/state           {"valid", "H, m", "TAS, km/h", "IAS, km/h", "M", "Vy, m/s", ...}: valores de vuelo,
                  vÃ¡lido solo en una aeronave
/indicators      {"valid", "army": air|tank|..., "type": el vehÃ­culo}
/hudmsg?lastEvt=N&lastDmg=M   {"events": [...], "damage": [...]} mÃ¡s nuevos que los ids indicados, cada uno
                  {"id", "msg", "sender", "enemy", "mode", "time"}; las lÃ­neas de daÃ±o tienen la forma
                  "Name (Vehicle) shot down Name (Vehicle)"
/gamechat?lastId=N  el chat mÃ¡s nuevo que el id indicado, [{"id", "msg", "sender", "enemy", "mode", "time"}]
/mission.json    los objetivos de la batalla y su estado
/map.img         la imagen del mapa sobre la que la pÃ¡gina dibuja los objetos
```

Cada respuesta se guarda completa en el archivo auxiliar sin procesar de la sesión bajo su endpoint
(map_info, map_obj, state, indicators, hudmsg, gamechat, mission, map_img);
entre batallas, las respuestas van a una sesión propia.

Una posición del mapa se convierte en metros con la extensión: u = min_x + x \* (max_x - min_x)
este, v = max_y - y \* (max_y - min_y) norte (la y de la imagen baja hacia abajo). Las filas son
x = u, y = altura (el "H, m" de la propia aeronave; 0 para todo lo demás), z = v, así que
Y es hacia arriba; z se invierte para el visor, para que el norte no se dibuje hacia el sur.

Los colores muestran los bandos tal como los ve el jugador: propio amarillo (#faC81E por defecto),
escuadrón verde, aliados azul (#174DFF), enemigos rojo (#f40C00); las paletas para daltonismo
cambian esos colores, así que decide el matiz, no el valor exacto. El juego no nombra a nadie en el
mapa y no da ids a los objetos: otros objetos reciben ids aquí siguiéndolos de sondeo en sondeo (el
más cercano del mismo tipo e icono), lo que puede intercambiar dos aeronaves del mismo tipo que pasan
muy cerca. El nombre propio del jugador tampoco está en la API: indícalo en los ajustes
(`config --set player_names.warthunder-webmap=<tu nombre>`) y las líneas del feed de bajas sobre el
jugador pasan a ser bajas y muertes; sin él se guardan como feed de bajas.

Fuentes: la página propia del juego en <http://127.0.0.1:8111> y su JSON; datos de los campos según
documenta el proyecto JoyPro 2 (docs/telemetry-recording.md; GPL, usado solo para los datos).

## Posiciones y ejes {#positions-and-axes}

| | |
|---|---|
| Posiciones registradas | sí |
| Eje vertical | `y` |
| Unidades | metros (este/norte del mapa; altura solo para la aeronave propia) |
| Invertido para el visor | `z` |
| Escala de unidad (`scale`: el visor multiplica las posiciones por ella) | 1 |

Estos valores van al `meta.json` de cada sesión (`axes`) y, cuando la sesión tiene posiciones, al pie de `heat.parquet`, así que el visor de 3DHeat gira y escala las filas por sí mismo; véase [Los datos](the-data.md).

## Multijugador {#multiplayer}

- Marcado como jugado en línea (`multiplayer`): **sí**. `games --markdown` lo muestra como "permitido (lee solo lo que publica el juego)".
- Tipo `gsi`: lee solo lo que el juego o la plataforma entregan (una game-state integration o una API local que sirve el juego), así que graba también en el juego en línea; la marca solo decide si la memoria puede leerse alguna vez.
- Memoria: **nunca** la lee este adaptador. Solo los adaptadores `memory` leen memoria, y nunca en un juego marcado como jugado en línea; véase [Fuentes y reglas](sources-and-rules.md).

## Estadísticas registradas {#statistics-recorded}

Claves de estadística que el código de este adaptador asigna por nombre (el `stats` de cada sesión en `meta.json` y la tabla `stats` de `watcher.sqlite`):

`bad_packets`, `deaths`, `distance_m`, `hits_dealt`, `hits_taken`, `kills`, `max_altitude_m`, `max_tas_kmh`, `spawns`, `vehicle`

Una clave entre llaves se completa en tiempo de ejecución (`score.{team}` es una clave por equipo). Las claves que el código toma de una tabla de campos del juego o de sus propios nombres de estadística no están en esta lista; "Qué se graba" arriba las nombra.

## Completitud {#completeness}

El watcher sigue la [regla de conversión](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md) de 3DHeat: lo que trae la fuente se lee o se guarda, nunca se descarta. Además de las filas, cada paquete, página, línea o respuesta que recibe el adaptador se guarda completo en `heat.raw.parquet` de la sesión (columnas `time`, `ms`, `type`, `used`, `payload`, `text`, y los campos guardados por nombre; `used` marca lo que también se convirtió en filas), y `selfCheck.completeness` de `meta.json` cuenta cada `type` - `lost` es 0.

**Leído**

- /map_info.json: la extensión y la cuadrícula del mapa (metros, el id del mapa) en meta.json; uno no válido termina la batalla
- /map_obj.json (dos veces por segundo): la aeronave propia, otras aeronaves y unidades terrestres (ids seguidos, bando por el color, icono, rumbo, color) y aeródromos, zonas y bases como filas
- /state (dos veces por segundo, en aeronave): altura, TAS, IAS, Mach y Vy en las filas propias
- /indicators (cada 2 s): bando y tipo de vehículo
- /hudmsg (una vez por segundo): líneas del feed de bajas y daños como bajas, muertes, impactos y filas de feed; otros eventos del HUD como filas

**Guardado sin procesar**

- cada respuesta completa, `text` el JSON tal como lo envió el juego, bajo su endpoint: `map_info`, `map_obj`, `state`, `indicators`, `hudmsg`, `gamechat`, `mission`; `map_img` los bytes de la imagen del mapa como `payload`, una vez por batalla
- lo que solo tiene el archivo auxiliar sin procesar: cada campo de /state más allá de los cinco leídos (AoA, AoS, Ny, Wx, acelerador, rpm, combustible, ... - el conjunto difiere de una aeronave a otra), cada campo de /indicators (los instrumentos de cabina de las aeronaves, la velocidad, marchas, tripulación y estabilizador de los tanques), las otras claves de los objetos del mapa (color[], blink, icon_bg, extremos de aeródromo), sender, enemy y mode de hudmsg, el chat (/gamechat, una vez por segundo), los objetivos de la batalla y su estado (/mission.json, cada 10 s en batalla), líneas dichas antes de que arrancara el watcher
- entre batallas (hangar, carga) las respuestas van a una sesión propia, marcada `between_battles` en meta.json, que no tiene filas

**No disponible**

- nombres, ids y alturas de los vehículos de otros jugadores: el mapa web no los tiene (los ids se dan aquí siguiendo los objetos de sondeo en sondeo); el feed de bajas nombra a los jugadores sin posiciones
- todo lo que está fuera del mapa web: las repeticiones del juego las lee el conversor de repeticiones de War Thunder, y la memoria del juego nunca se lee (es un juego en línea)
- /map_obj.json más de dos veces por segundo: la frecuencia de sondeo se mantiene baja para no cargar el servidor web propio del juego

**Tamaño**: unos 50-120 MB por hora de JSON antes de zstd en batalla (map_obj de 5-15 KB dos veces por segundo, state de unos 1,5 KB dos veces por segundo, indicators cada 2 s, el chat y las líneas del HUD pequeñas) más la imagen del mapa una vez por batalla (menos de 2 MB); 1-2 MB por hora entre batallas (la vista del mapa dos veces por segundo, el HUD y el chat una vez, cada uno una respuesta corta); zstd reduce el JSON repetido más de diez veces

## Verificado {#verified}

probado con un servidor local simulado que sirve respuestas en el formato del mapa web del juego; sin probar contra el juego en marcha

## Fuente {#source}

[heat3d_watch/adapters/warthunder.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/warthunder.py)

<!-- Generado a partir del adaptador por tools/gen_game_pages.py; cambia el adaptador y vuelve a ejecutarlo en lugar de editar esta página. -->
