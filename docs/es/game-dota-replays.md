---
title: "Dota 2 (repeticiones)"
nav_order: 12
lang: "es"
source: game-dota-replays.md
source_hash: "c0ed25c261f6"
nav_exclude: true
search_exclude: true
---
# Dota 2 (repeticiones) {#dota-2-replays}

Después de una partida de Dota 2, el watcher convierte la repetición que guardó el juego en archivos que puedes ver en un mapa del visor de 3DHeat.

*Detalles técnicos: adaptador `dota-replays`, tipo [`replay`](sources-and-rules.md); se ejecuta todo el tiempo (no espera a que empiece una partida) y busca datos nuevos cada 5 s.*

## Qué se graba {#what-is-recorded}

- la posición, altura, salud y nivel de cada héroe, 7,5 veces por segundo mientras está vivo
- bajas y muertes donde ocurrieron; torres, cuarteles, Roshan y Tormentors donde cayeron; wards donde se colocaron
- los pings del mapa, dibujos del mapa y órdenes (mover, atacar, lanzar, comprar, ...) de cada jugador donde apuntaban
- el marcador y la línea de cada jugador; la del jugador con sesión iniciada, como estadísticas
- todo lo demás que contiene la repetición, guardado completo junto a la tabla: cada fotograma y mensaje de red, cada cambio de propiedad de entidad, cada entrada de tabla de cadenas

## De dónde viene {#where-it-comes-from}

repeticiones que guarda Dota 2: &lt;Dota>/game/dota/replays/&lt;id de partida>.dem (descargadas en el cliente, o con `dota-replay <id de partida>`)

## Cómo activarlo {#how-to-switch-it-on}

descarga la repetición de una partida en Dota 2, o baja una pública: `python -m heat3d_watch dota-replay <id de partida>`; instala el lector: github.com/Holdi601/3DHeat-Ext-DotaReplay (`heat3d-dota-replay`, trae gem-dota)

Escribe el comando en una terminal abierta en la carpeta del watcher (véase [Antes de empezar](before-you-start.md)). Si falla, la última línea dice por qué; [Instalación y uso](installing-and-running.md) recoge las causas habituales.

Ajustes desde variables de entorno:

- `HEAT3D_DOTA_REPLAY`: la carpeta del lector (un clon o una versión descomprimida), cuando no está instalado o junto al watcher

## Cómo funciona {#how-it-works}

Repeticiones y demos: lo que guarda un juego de una partida, convertido una vez terminada la partida.

Una repetición contiene todo lo que una interfaz en vivo oculta en los juegos multijugador -
la posición de cada jugador, cada baja donde ocurrió- y es un archivo que el juego escribe para sus
jugadores, así que leerlo no toca nada del juego. El watcher mira las carpetas donde los juegos las
guardan, espera a que un archivo nuevo deje de crecer (si no, el juego aún lo está escribiendo), y lo
convierte en un hilo de trabajo, para que una conversión larga nunca detenga el resto del watcher.

La primera vez que se ve una carpeta, las repeticiones que ya contiene solo se anotan, no se convierten:
un jugador con años de demos vería el watcher ocupado durante un día. `python -m heat3d_watch
replays <adaptador> [carpeta]` convierte las existentes bajo petición.

#### Dota 2 {#dota-2}

Dota 2 guarda las repeticiones que descarga un jugador (los detalles de una partida, o Ver > Repeticiones)
en `<Dota>/game/dota/replays/<id de partida>.dem`; Valve conserva la repetición de cada partida pública en
sus servidores durante unas semanas, y `python -m heat3d_watch dota-replay <id de partida>` descarga una por
su id a través de OpenDota. El watcher no las lee por sí mismo: lo hace un lector externo (3DHeat Dota Replay,
github.com/Holdi601/3DHeat-Ext-DotaReplay, `exporters/ext/dota-replay`, comando `heat3d-dota-replay`, que lee
con gem-dota, MIT), separado para que un problema con él no afecte a nada más, y se ejecuta en un proceso propio
con cada repetición nueva cuando está en el PATH, instalado o junto al watcher; si falta, el watcher indica una
sola vez cómo instalarlo. Escribe la posición, altura, salud, nivel, orientación, maná, experiencia, atributos
y objetos de cada héroe 7,5 veces por segundo mientras está vivo; bajas y muertes donde ocurrieron; torres,
cuarteles, Roshan y Tormentors donde cayeron; cada ward donde se colocó y donde terminó; las entradas del
registro de combate sobre los héroes (daño, curaciones, habilidades, objetos, compras, runas, oro, experiencia,
modificadores), y los pings, dibujos y órdenes de cada jugador - en `dota/<partida>.parquet`; cada otra unidad
(criaturas, invocaciones, ilusiones, mensajeros, edificios) una vez por segundo en `<partida>.units.parquet`;
el registro de combate completo en `<partida>.combatlog.parquet`; y la partida, el chat, el draft, todo lo
demás que extrae el analizador y el registro de fin de partida del juego en `<partida>.match.json`, en la
carpeta de la sesión. Lo demás que contiene la repetición se guarda completo junto a ellos (regla de
conversión de 3DHeat): cada fotograma y mensaje de red en `<partida>.packets.parquet`, cada cambio de
propiedad de entidad en `<partida>.entities.parquet`, cada entrada de tabla de cadenas en
`<partida>.strings.parquet`, contado en `selfCheck.completeness` del documento de la partida. Las posiciones
son las unidades del mundo de Dota, las mismas que informa la game-state integration. La línea del marcador
del jugador con sesión iniciada se convierte en las estadísticas de la sesión: bajas, muertes, asistencias,
últimos golpes, negaciones, valor neto, GPM, XPM, daño a héroes, wards, y si la partida se ganó. Una nueva
versión de parche de Dota puede cambiar las entidades de la repetición antes de que gem las siga; una
repetición que gem no puede leer hasta el final se convierte hasta donde llega y se marca como `incomplete`
en su resumen.

El mismo módulo también sirve a: [Counter-Strike 2 (repeticiones)](game-cs2-demos.md), [Squad (repeticiones)](game-squad-demos.md), [War Thunder (repeticiones)](game-warthunder-replays.md), [World of Tanks (repeticiones)](game-wot-replays.md), [World of Warships (repeticiones)](game-wows-replays.md).

## Posiciones y ejes {#positions-and-axes}

| | |
|---|---|
| Posiciones registradas | sí |
| Eje vertical | `z` |
| Unidades | unidades del mundo de Dota (unidades de Hammer; el mapa mide unos 16400 de lado) |
| Invertido para el visor | `y` |
| Escala de unidad (`scale`: el visor multiplica las posiciones por ella) | 1 |

Estos valores van al `meta.json` de cada sesión (`axes`) y, cuando la sesión tiene posiciones, al pie de `heat.parquet`, así que el visor de 3DHeat gira y escala las filas por sí mismo; véase [Los datos](the-data.md).

## Multijugador {#multiplayer}

- Marcado como jugado en línea (`multiplayer`): **sí**. `games --markdown` lo muestra como "permitido (lee solo lo que publica el juego)".
- Tipo `replay`: lee solo lo que el juego o la plataforma entregan (repeticiones y demos que guarda el juego), así que graba también en el juego en línea; la marca solo decide si la memoria puede leerse alguna vez.
- Memoria: **nunca** la lee este adaptador. Solo los adaptadores `memory` leen memoria, y nunca en un juego marcado como jugado en línea; véase [Fuentes y reglas](sources-and-rules.md).

## Estadísticas registradas {#statistics-recorded}

Claves de estadística que el código de este adaptador asigna por nombre (el `stats` de cada sesión en `meta.json` y la tabla `stats` de `watcher.sqlite`):

`duration`, `hero`, `score.{team}`, `team`, `won`

Una clave entre llaves se completa en tiempo de ejecución (`score.{team}` es una clave por equipo). Las claves que el código toma de una tabla de campos del juego o de sus propios nombres de estadística no están en esta lista; "Qué se graba" arriba las nombra.

## Completitud {#completeness}

El conversor sigue la [regla de conversión](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md) de 3DHeat: lo que trae la repetición se lee o se guarda, nunca se descarta. Además de la tabla, todo lo demás que contiene la repetición se guarda completo en archivos auxiliares junto a ella, en la carpeta `dota/` de la sesión - `<partida>.packets.parquet`, `<partida>.entities.parquet`, `<partida>.strings.parquet` (columnas `time`, `tick`, `type`, `name`, `entity`, `decoded`, `payload`, según corresponda) - y `selfCheck.completeness` del documento de la partida (`<partida>.match.json`) cuenta cada `type` - `lost` es 0.

**Leído**

- la tabla (`dota/<partida>.parquet`): la posición, altura, salud, nivel, orientación, maná, experiencia, atributos, armadura, velocidad, daño, objetos y el cursor del jugador de cada héroe, 7,5 veces por segundo; bajas, muertes, objetivos, wards, las entradas del registro de combate sobre héroes; los pings del mapa (`ping`, DOTA_UM_LocationPing), los dibujos del mapa (`map_line`, DOTA_UM_MapLine) y cada orden de unidad (`order`, DOTA_UM_SpectatorPlayerUnitOrders: `other` el tipo de orden, `value` el id de la habilidad u objeto, `text` la clase del objetivo; en el punto ordenado, si no en el héroe)
- `<partida>.units.parquet`: cada otra unidad una vez por segundo; `<partida>.combatlog.parquet`: el registro de combate completo tal como lo lee gem, cada campo
- el documento de la partida: todo lo que extrae gem, y completos los registros propios de la repetición - `fileHeader` (DEM_FileHeader), `fileInfo` (DEM_FileInfo: duración de reproducción, nombre, héroe, id de Steam y equipo de cada jugador), `matchDetails` (DOTA_UM_MatchDetails: el marcador de fin de partida del coordinador del juego, las cifras de cada jugador, objetos, daño por tipo, elecciones y bloqueos) y `matchMetadata` (DOTA_UM_MatchMetadata)
- `selfCheck.crossCheck`: bajas, muertes, asistencias, nivel, últimos golpes y negaciones tal como se leen del flujo, comparados con `matchDetails`, por jugador

**Guardado sin procesar**

- `<partida>.packets.parquet`: cada fotograma que no es un paquete (`type` `frame <n>`) y cada mensaje de red (`message <n>`, con el nombre que da Valve en `name`), completo en `payload`, en el orden del archivo (`seq`, `frame`), con `decoded` el protobuf como JSON (un campo de bytes como su longitud); se decodifica cada tipo de mensaje: svc_PacketEntities (el flujo de entidades), DOTA_UM_SpectatorPlayerUnitOrders, UM_ParticleManager, los mensajes del registro de combate, GE_SosStartSoundEvent, DOTA_UM_TE_\* (proyectiles, animaciones, sangre), DOTA_UM_OverheadEvent, DOTA_UM_UnitEvent, svc_UpdateStringTable, net_Tick, ...; las tablas de envío, la lista de clases y la información del servidor que necesita después un decodificador de entidades están entre ellas
- `<partida>.entities.parquet`: cada propiedad de cada entidad cada vez que cambia (`type` la propiedad, `name` la clase, `entity` su índice; `value`, `vector` o `decoded`), su estado completo al crearse, y cada creación, entrada, salida y eliminación - millones de filas por partida completa
- `<partida>.strings.parquet`: cada entrada de tabla de cadenas de cada actualización y de cada instantánea completa, el valor completo; `userinfo`, `ActiveModifiers` y `EconItems` decodificados de sus protobufs
- `selfCheck.completeness` del documento de la partida cuenta fotogramas y mensajes por su nombre de Valve, entradas del registro de combate (`combatlog <type>`), eventos del juego (`gameevent <name>`), entradas de tabla de cadenas (`stringtable <name>`) y actualizaciones de entidades (`entity <class>`); algunas se guardan solo sin procesar (instantáneas completas de entidades que gem omite porque reconstruye a partir de los cambios, y entradas de tablas cuyos valores nada lee), pérdida 0

**No disponible**

- voz: la repetición tiene la configuración de voz, pero no los datos de voz
- nombres detrás de hashes e ids: sonidos y partículas se nombran por hashes de los archivos del juego, las habilidades por ids; la repetición no lleva los nombres (los objetos se nombran con el catálogo de gem donde lo tiene)
- todo lo que solo conocían los clientes de los propios jugadores (su cámara, su pantalla) más allá de lo que emitió el servidor; el cursor y cada orden sí están

**Tamaño**: los archivos auxiliares juntos son algo mayores que la propia repetición, siendo los más grandes los paquetes y las entidades; una partida completa tarda uno o dos minutos en un solo proceso

## Verificado {#verified}

comprobado con la repetición de una partida pública: bajas, muertes, asistencias, nivel, últimos golpes y negaciones coinciden con el registro de fin de partida del juego para los diez jugadores; cada mensaje del archivo auxiliar de paquetes se vuelve a serializar byte a byte; la tabla y las estadísticas con pruebas sobre datos sintéticos

## Fuente {#source}

[heat3d_watch/adapters/replays.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/replays.py)

<!-- Generado a partir del adaptador por tools/gen_game_pages.py; cambia el adaptador y vuelve a ejecutarlo en lugar de editar esta página. -->
