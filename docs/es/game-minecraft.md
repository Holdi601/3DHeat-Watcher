---
title: "Minecraft (archivos de registro)"
nav_order: 33
lang: "es"
source: game-minecraft.md
source_hash: "35cfea9d36a0"
nav_exclude: true
search_exclude: true
---
# Minecraft (archivos de registro) {#minecraft-log-files}

Mientras juegas a Minecraft, el watcher lee los archivos que escribe el juego y guarda lo que ha pasado, para que luego puedas verlo en un mapa del visor de 3DHeat.

*Detalles técnicos: adaptador `minecraft`, tipo [`log`](sources-and-rules.md); se ejecuta mientras `javaw.exe` o `java.exe` está en marcha y busca datos nuevos cada 0,5 s.*

## Qué se graba {#what-is-recorded}

- la posición propia y la de los demás jugadores (bloques = m, y hacia arriba) cada vez que el mundo se guarda, con la dimensión como sesión
- aparición con posición cuando un jugador entra en el servidor (integrado)
- entradas, salidas, muertes con el mensaje de muerte, logros, líneas de chat
- muertes, logros, mensajes de chat; del archivo de estadísticas: tiempo de juego, distancia, bajas de monstruos y jugadores, saltos, daño, bloques minados, objetos fabricados (la parte de esta sesión)
- cada línea del registro y cada estadística, logro y archivo de jugador guardados, enteros, en heat.raw.parquet

## De dónde sale {#where-it-comes-from}

%APPDATA%\\.minecraft\logs\latest.log (seguido), saves\\&lt;mundo>\stats\\&lt;uuid>.json y saves\\&lt;mundo>\playerdata\\&lt;uuid>.dat / level.dat (NBT comprimido con gzip), leídos cuando el juego los guarda

## Cómo activarlo {#how-to-switch-it-on}

No hace falta activar nada: el watcher lee la fuente tal como la entrega el juego o la plataforma.

## Cómo funciona {#how-it-works}

Minecraft (Java Edition): el registro, las estadísticas y los archivos de jugador que escribe el juego.

Dónde (`%APPDATA%\.minecraft\`):

* `logs\latest.log` - el registro del juego, nuevo en cada arranque (el anterior se empaqueta en un .log.gz con fecha). Líneas `[hh:mm:ss] [hilo/NIVEL]: mensaje` (los cargadores de mods escriben `[ddMMMyyyy hh:mm:ss.mmm] [hilo/NIVEL] [registrador/]: ...`). Lo que ven los jugadores en el chat está aquí: entradas y salidas, mensajes de muerte, logros, chat. El servidor integrado de un mundo de un jugador escribe las mismas líneas una vez más, así que una línea repetida dentro del mismo segundo cuenta una vez. "Setting user: &lt;nombre>" nombra al jugador; la línea "&lt;nombre>[...] logged in with entity id N at (x, y, z)" del servidor indica dónde apareció.
* `saves\<mundo>\stats\<uuid>.json` - la pantalla de estadísticas, escrita cuando el mundo se guarda (autoguardado cada pocos minutos, y al salir): `stats` -> `minecraft:custom` (play_time en ticks, mob_kills, \*_one_cm distancias, jump, ...), `minecraft:mined`, `minecraft:crafted`, ... Totales del mundo; las cifras de la sesión son la diferencia con lo que decía el archivo cuando arrancó el juego. Formato: <https://minecraft.wiki/w/Statistics>
* `saves\<mundo>\playerdata\<uuid>.dat` (y `level.dat` -> Data -> Player para un anfitrión de un jugador) - NBT comprimido con gzip, escrito en los mismos guardados: `Pos` [x, y, z] como dobles, `Rotation` [yaw, pitch], `Dimension` ("minecraft:overworld"; un int 0/-1/1 antes de la 1.16). NBT según <https://minecraft.wiki/w/NBT_format>; aquí lo lee un pequeño lector propio.
* `saves\<mundo>\advancements\<uuid>.json` - el progreso de la pantalla de logros, escrito en los mismos guardados.

Las coordenadas son bloques, un bloque por metro, y hacia arriba; x este, z sur: un marco dextrógiro, dibujado tal cual. Las posiciones llegan solo cuando el mundo se guarda, así que un recorrido son unos pocos puntos por autoguardado, no una estela; la dimensión es la `session`, así que el Nether no se dibuja sobre el Mundo Superior.

Todo lo leído se guarda entero en el archivo auxiliar en bruto de la sesión (regla de conversores de 3DHeat): cada línea del registro bajo su nivel (`INFO`, `WARN`, `ERROR`, ...; una línea sin la cabecera entre corchetes, como una traza de pila, como `untagged`), y cada archivo guardado bajo su tipo (`stats`, `advancements`, `playerdata`, `level.dat`): JSON como texto, NBT como sus bytes. Las cifras de un archivo de estadísticas solo se entienden frente a lo que decía al arrancar el juego, así que esa primera copia también se guarda (`baseline`), la primera vez que el archivo cambia.

## Posiciones y ejes {#positions-and-axes}

| | |
|---|---|
| Posiciones grabadas | sí |
| Eje hacia arriba | `y` |
| Unidades | bloques (1 bloque = 1 m) |
| Reflejado para el visor | ninguno |
| Escala de unidad (`scale`: el visor multiplica las posiciones por ella) | 1 |

Esto va al `meta.json` de cada sesión (`axes`) y, cuando la sesión tiene posiciones, al pie (footer) de `heat.parquet`, así que el visor de 3DHeat gira y escala las filas por sí mismo; ver [Los datos](the-data.md).

## Multijugador {#multiplayer}

- Marcado como jugado en línea (`multiplayer`): **sí**. `games --markdown` lo muestra como "permitido (lee solo lo que publica el juego)".
- Tipo `log`: lee solo lo que el juego o la plataforma entregan (archivos que el juego escribe mientras se ejecuta), así que graba también en el juego en línea; la marca solo decide si se puede leer la memoria en algún momento.
- Memoria: **nunca** la lee este adaptador. Solo los adaptadores `memory` leen memoria, y nunca en un juego marcado como jugado en línea; ver [Fuentes y reglas](sources-and-rules.md).

## Estadísticas grabadas {#statistics-recorded}

Claves de estadística que el código de este adaptador fija por nombre (el `stats` de cada sesión en `meta.json` y la tabla `stats` de `watcher.sqlite`):

`advancements`, `bad_files`, `bad_lines`, `chat_messages`, `deaths`, `joins`, `others_deaths`, `world`

Una clave entre llaves se completa en tiempo de ejecución (`score.{team}` es una clave por equipo). Las claves que el código toma de una tabla de campos del juego o de sus propios nombres de estadística no están en esta lista; "Qué se graba" más arriba las nombra.

## Completitud {#completeness}

El watcher sigue la [regla de conversores](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md) de 3DHeat: lo que la fuente contiene se lee o se guarda, nunca se descarta. Además de las filas, cada paquete, página, línea o respuesta que recibe el adaptador se guarda entero en `heat.raw.parquet` de la sesión (columnas `time`, `ms`, `type`, `used`, `payload`, `text`, y los campos que se guardan por nombre; `used` marca lo que también se convirtió en filas), y `selfCheck.completeness` de `meta.json` cuenta cada `type`: `lost` es 0.

**Leído**

- latest.log: el nombre del jugador (`Setting user`), entradas con posición, entradas, salidas, muertes con el mensaje de muerte, logros, líneas de chat, la parada del servidor
- stats/&lt;uuid>.json: tiempo de juego, distancia, bajas de monstruos y jugadores, saltos, daño causado y recibido, bloques minados, objetos fabricados: la parte de esta sesión
- playerdata/&lt;uuid>.dat y level.dat (NBT): posición, dimensión, yaw, pitch, salud, nivel de experiencia

**Guardado en bruto**

- cada línea de latest.log entera, `type` = su nivel (`INFO`, `WARN`, `ERROR`, `DEBUG`, `FATAL`) con el hilo del registrador en `thread`, `used` cuando se convirtió en fila; una línea sin la cabecera entre corchetes (una traza de pila, el banner de un mod) como `untagged`
- cada stats/&lt;uuid>.json entero como texto, `type` `stats` (`used`: sus cifras están en las estadísticas), con su primera copia desde el arranque del juego como `baseline`
- cada advancements/&lt;uuid>.json entero como texto, `type` `advancements` (cada criterio y cuándo se cumplió; todavía no se convierte en filas)
- cada playerdata/&lt;uuid>.dat y level.dat entero como bytes (NBT comprimido con gzip), `type` `playerdata` / `level.dat`, `used` cuando dio una posición: el inventario, el cofre de ender, los efectos, el punto de aparición, las reglas del juego, la semilla del mundo y la hora solo están aquí
- cada archivo guardado tiene `world` y `file` (su ruta dentro de `saves`)

**No disponible**

- un recorrido de posiciones: el juego escribe la posición del jugador solo cuando el mundo se guarda (cada pocos minutos y al salir)
- posiciones en un servidor que aloja otra persona: sus archivos de mundo están en el servidor, no aquí; en ese caso solo se lee el registro
- el mundo en sí (archivos de región .mca, entidades, mapas data/\*.dat y incursiones): grande, y es el terreno, no la partida
- los registros de sesiones anteriores (logs/\*.log.gz): se guardan cuando se jugaron
- Bedrock Edition: no escribe ese registro ni esos archivos

**Tamaño**: latest.log 0,1-2 MB por hora (más con mods); un archivo de estadísticas 5-50 KB y un archivo de jugador 5-100 KB por autoguardado, level.dat 1-20 KB: unos 1-5 MB por hora en total; zstd en heat.raw.parquet deja el texto en aproximadamente una décima parte (los archivos NBT ya van comprimidos con gzip)

## Verificado {#verified}

probado con líneas de registro sintéticas, JSON de estadísticas y archivos NBT creados a partir de los formatos publicados; sin probar contra el juego

## Fuente {#source}

[heat3d_watch/adapters/minecraft.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/minecraft.py)

<!-- Generated from the adapter by tools/gen_game_pages.py; change the adapter and run it again rather than editing this page. -->
