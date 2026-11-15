---
title: "Elite Dangerous (archivos de registro)"
nav_order: 18
lang: "es"
source: game-elite.md
source_hash: "bb5bcf75553a"
nav_exclude: true
search_exclude: true
---
# Elite Dangerous (archivos de registro) {#elite-dangerous-log-files}

Mientras juegas a Elite Dangerous, el watcher lee los archivos que escribe el juego y guarda lo que ha pasado, para que luego puedas verlo en un mapa del visor de 3DHeat.

*Detalles técnicos: adaptador `elite`, tipo [`log`](sources-and-rules.md); se ejecuta mientras `EliteDangerous64.exe` está en marcha y busca datos nuevos cada 0,25 s.*

## Qué se graba {#what-is-recorded}

- cada evento del diario de a bordo, con su nombre del diario y sus campos sencillos
- posición en la galaxia (StarPos, años luz) en saltos, ubicaciones, apariciones, muertes, atraques y aterrizajes
- aparición en LoadGame/Resurrect, muerte en Died, atracado/desatracado, toma de contacto/despegue, salto, session_end
- ruta de superficie del planeta desde Status.json: latitud, longitud, altitud, rumbo, y metros en un plano tangente por cuerpo (sesión = nombre del cuerpo), con los demás campos sencillos de Status.json (Flags, Flags2, GuiFocus, LegalState, ...)
- cada línea del diario y cada archivo complementario entero en heat.raw.parquet
- saltos, distancia saltada, muertes, bajas, créditos ganados, misiones completadas, cuerpos escaneados, sistemas visitados, atraques, aterrizajes

## De dónde sale {#where-it-comes-from}

Diario del jugador %USERPROFILE%\Saved Games\Frontier Developments\Elite Dangerous\Journal.\*.log (el archivo más nuevo, seguido mientras se escribe), Status.json y los demás archivos complementarios \*.json (Market, Outfitting, Shipyard, NavRoute, Cargo, ModulesInfo, ShipLocker, Backpack, FCMaterials) de la misma carpeta

## Cómo activarlo {#how-to-switch-it-on}

No hace falta activar nada: el watcher lee la fuente tal como la entrega el juego o la plataforma.

## Cómo funciona {#how-it-works}

Elite Dangerous: el diario del jugador y Status.json que escribe el juego mientras se ejecuta.

Dónde: `%USERPROFILE%\Saved Games\Frontier Developments\Elite Dangerous\`

* `Journal.<aaaa-mm-ddThhmmss>.<parte>.log` - un objeto JSON por línea, un archivo por cada arranque (una sesión larga continúa en la parte .02, .03 ...). Cada línea tiene `timestamp` (UTC, ISO 8601) y `event`. Las posiciones en la galaxia son el `StarPos` [x, y, z] del sistema, en años luz desde Sol, en `FSDJump`, `Location` y `CarrierJump`. El marco galáctico de Elite tiene y hacia arriba (hacia el norte galáctico), z hacia el núcleo galáctico y x hacia la longitud galáctica 270: es un marco zurdo, así que el visor invierte z para dibujarlo en el sentido correcto.
* `Status.json` - se reescribe entero cada vez que cambia el estado de la nave: `Flags`, y cerca de un planeta `Latitude`, `Longitude` (grados), `Altitude` (metros), `Heading`, `BodyName` y `PlanetRadius` (metros).
* Los demás archivos complementarios, cada uno reescrito entero cuando se escribe el evento del diario que le corresponde: `Market.json`, `Outfitting.json`, `Shipyard.json`, `NavRoute.json`, `Cargo.json`, `ModulesInfo.json`, `ShipLocker.json`, `Backpack.json`, `FCMaterials.json`. Cada `*.json` de la carpeta que el juego escribe en esta sesión se guarda entero cada vez que cambia (regla de conversores de 3DHeat: lo que la fuente contiene se lee o se guarda, nunca se descarta), bajo su nombre de archivo.

Cada línea del diario se guarda entera en el archivo auxiliar en bruto de la sesión bajo su `event`, cada archivo complementario bajo su nombre de archivo; una línea que no es JSON, bajo `unparsed`.

Las posiciones de superficie se colocan en un plano tangente local por cuerpo, en metros: el primer punto fijo en un cuerpo es su origen, x al este, z al norte, y hacia arriba (altitud), con la misma lateralidad que el marco galáctico, y las filas llevan el nombre del cuerpo como su `session`, así que una conducción o un paseo por un planeta se dibuja como un trazado propio. Las filas galácticas tienen la sesión "galaxy". Las dos escalas viven en una sola tabla; elige la sesión en el visor.

Formato: el manual "Elite Dangerous Player Journal" de Frontier (publicado con cada actualización en los foros oficiales, <https://forums.frontier.co.uk/> - "Journal Manual", v4.x), con eventos y campos según ese manual; las banderas de Status.json según el capítulo "Status File" del mismo manual.

## Posiciones y ejes {#positions-and-axes}

| | |
|---|---|
| Posiciones grabadas | sí |
| Eje hacia arriba | `y` |
| Unidades | años luz (filas galácticas, sesión 'galaxy'); metros al este/arriba/norte del primer punto fijo en un cuerpo (filas de superficie, sesión = nombre del cuerpo) |
| Reflejado para el visor | `z` |
| Escala de unidad (`scale`: el visor multiplica las posiciones por ella) | 1 |

Esto va al `meta.json` de cada sesión (`axes`) y, cuando la sesión tiene posiciones, al pie (footer) de `heat.parquet`, así que el visor de 3DHeat gira y escala las filas por sí mismo; ver [Los datos](the-data.md).

## Multijugador {#multiplayer}

- Marcado como jugado en línea (`multiplayer`): **sí**. `games --markdown` lo muestra como "permitido (lee solo lo que publica el juego)".
- Tipo `log`: lee solo lo que el juego o la plataforma entregan (archivos que el juego escribe mientras se ejecuta), así que graba también en el juego en línea; la marca solo decide si se puede leer la memoria en algún momento.
- Memoria: **nunca** la lee este adaptador. Solo los adaptadores `memory` leen memoria, y nunca en un juego marcado como jugado en línea; ver [Fuentes y reglas](sources-and-rules.md).

## Estadísticas grabadas {#statistics-recorded}

Claves de estadística que el código de este adaptador fija por nombre (el `stats` de cada sesión en `meta.json` y la tabla `stats` de `watcher.sqlite`):

`bad_lines`, `bodies_scanned`, `carrier_jumps`, `credits`, `credits_earned`, `deaths`, `distance_ly`, `dockings`, `jumps`, `kills`, `landings`, `missions_completed`, `ship`, `surface_fixes`, `systems_visited`

Una clave entre llaves se completa en tiempo de ejecución (`score.{team}` es una clave por equipo). Las claves que el código toma de una tabla de campos del juego o de sus propios nombres de estadística no están en esta lista; "Qué se graba" más arriba las nombra.

## Completitud {#completeness}

El watcher sigue la [regla de conversores](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md) de 3DHeat: lo que la fuente contiene se lee o se guarda, nunca se descarta. Además de las filas, cada paquete, página, línea o respuesta que recibe el adaptador se guarda entero en `heat.raw.parquet` de la sesión (columnas `time`, `ms`, `type`, `used`, `payload`, `text`, y los campos que se guardan por nombre; `used` marca lo que también se convirtió en filas), y `selfCheck.completeness` de `meta.json` cuenta cada `type`: `lost` es 0.

**Leído**

- cada línea del diario como una fila bajo su `event`, con sus campos sencillos (el texto localizado cuando el juego lo da; los textos de más de 300 caracteres se cortan en la fila)
- filas galácticas (StarPos) en FSDJump, CarrierJump, Location, LoadGame, Resurrect, Died, Docked, Undocked, Touchdown, Liftoff, Shutdown; filas de superficie desde Status.json y Touchdown/Liftoff
- los campos sencillos de Status.json (Flags, Flags2, GuiFocus, LegalState, Cargo, FireGroup, Oxygen, Health, Temperature, Gravity, SelectedWeapon, ...) en las filas de superficie
- las estadísticas: saltos, distancia, muertes, bajas, créditos ganados, misiones, cuerpos escaneados, sistemas visitados, atraques, aterrizajes

**Guardado en bruto**

- cada línea del diario entera, `type` = su `event` (FSDJump, Scan, Music, ReceiveText, ...), `used` verdadero: las listas y objetos que las filas dejan fuera (StarPos, Factions, Rewards, Killers, Materials, Modules, ...) solo están aquí
- una línea del diario que no es JSON, `type` `unparsed`
- cada archivo complementario entero cada vez que el juego lo reescribe, `type` = su nombre de archivo: `Status.json` (`used` cuando hizo una fila de superficie), `Market.json`, `Outfitting.json`, `Shipyard.json`, `NavRoute.json`, `Cargo.json`, `ModulesInfo.json`, `ShipLocker.json`, `Backpack.json`, `FCMaterials.json`, y cualquier otro `*.json` que el juego escriba allí

**No disponible**

- la posición entre saltos (dentro de un sistema, en supercrucero o en el espacio normal): el juego escribe solo el StarPos del sistema y, cerca de un planeta, la latitud, la longitud y la altitud
- las posiciones de otras naves y de otros jugadores: el diario es el relato del propio comandante
- velocidad, acelerador y otra telemetría de vuelo: el juego no las escribe
- diarios y archivos complementarios de sesiones anteriores: se guardan cuando se jugaron (el seguidor empieza al final de un archivo más antiguo que esta ejecución del juego)
- la API web complementaria de Frontier (cAPI): necesita el inicio de sesión de Frontier del jugador; no es un archivo que escriba el juego

**Tamaño**: unos 1-5 MB de texto bruto por hora: el diario 0,2-2 MB, Status.json (menos de 1 KB, reescrito hasta cada segundo) 1-2 MB, un conjunto de mercado/equipamiento/astillero 20-150 KB por estación visitada; zstd en heat.raw.parquet lo deja en aproximadamente una décima parte

## Verificado {#verified}

el analizador reproducido sobre archivos de diario reales de una instalación local (los recuentos de eventos coinciden con las estadísticas); las posiciones de superficie de Status.json, probadas solo con instantáneas sintéticas

## Fuente {#source}

[heat3d_watch/adapters/elite.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/elite.py)

<!-- Generated from the adapter by tools/gen_game_pages.py; change the adapter and run it again rather than editing this page. -->
