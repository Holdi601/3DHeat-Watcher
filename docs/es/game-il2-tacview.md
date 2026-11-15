---
title: "IL-2 Sturmovik: Great Battles (repeticiones)"
nav_order: 27
lang: "es"
source: game-il2-tacview.md
source_hash: "0bb23bddee03"
nav_exclude: true
search_exclude: true
---
# IL-2 Sturmovik: Great Battles (repeticiones) {#il-2-sturmovik-great-battles-replays}

Después de una partida de IL-2 Sturmovik: Great Battles, el watcher convierte la repetición que guardó el juego en archivos que puedes ver en un mapa del visor de 3DHeat.

*Detalles técnicos: adaptador `il2-tacview`, tipo [`replay`](sources-and-rules.md); se ejecuta todo el tiempo (no espera a que empiece una partida) y busca datos nuevos cada 5 s.*

## Qué se graba {#what-is-recorded}

- cada avión, vehículo y barco de la grabación: posiciones una vez por segundo (metros al este/arriba/norte del punto de referencia de la grabación; lat/lon/alt como columnas)
- apariciones, destrucciones (muerte) y salidas (abandona), despegues y aterrizajes cuando la grabación los tiene
- objetos, destruidos, despegues, aterrizajes y duración por grabación
- cada línea de la grabación guardada entera en heat.raw.parquet, con el reloj de las filas

## De dónde viene {#where-it-comes-from}

las grabaciones Tacview que hace el propio juego, `<juego>\data\Tracks\*.acmi` (texto ACMI 2.x, sin comprimir o comprimido en zip)

## Cómo activarlo {#how-to-switch-it-on}

python -m heat3d_watch setup il2-tacview --apply (tacviewrecord = 1 en [KEY = track_record])

Escribe el comando en una terminal abierta en la carpeta del watcher (ver [Antes de empezar](before-you-start.md)). Si falla, la última línea dice por qué; [Instalación y ejecución](installing-and-running.md) cubre las causas habituales.

`python -m heat3d_watch setup il2-tacview` lista los archivos que cambiaría; `python -m heat3d_watch setup il2-tacview --apply` los cambia, guardando el original como `<file>.heat3d-backup` (ver [Comandos](commands.md#setup)). Muestra `il2-tacview: changed: ...` por cada cambio, o `il2-tacview: nothing to change` si ya está activado.

## Cómo funciona {#how-it-works}

IL-2 Sturmovik: Great Battles: la salida de telemetría por UDP del juego y sus propias grabaciones Tacview.

1. Telemetría ("Telemetry output of IL2 v4.003", revisión 1.2, incluida como `<juego>\Doc\UDP_Output\Il2_TeleOutput.pdf`). Se activa en `<juego>\data\startup.cfg`, sección `[KEY = telemetrydevice]`: `addr`, `addr1`, ... = "IP[:puerto]" (varios destinos a la vez), `decimation` (50 Hz / n), `enable`, `port`. `setup` añade un destino, 127.0.0.1:41995 (JoyPro usa 41994; el puerto por defecto del juego es 4322), y activa la salida. Paquetes, little-endian:

   ```text
   DWORD  Packet_ID 0x54000101
   WORD   Size
   DWORD  Tick (1/50 s)
   BYTE   Indicators_Count, then SIndicator {WORD id, BYTE n, n x 32-bit float}
   BYTE   Events_Count,     then SEvent     {WORD id, BYTE size, size bytes}
   ```

   Indicadores: 0 ENG_RPM, 1 ENG_MP, 2/3 vibración del motor, 4 LGEARS_STATE, 5 LGEARS_PRESS, 6 EAS (m/s), 7 AOA (rad), 8 ACCELERATION (xyz incluida la gravedad), 9 COCKPIT_SHAKE, 10 AGL (m), 11 FLAPS, 12 AIR_BRAKES, 13 AOS (rad), 14 VERTICAL_SPEED (m/s). Eventos (empaquetados de 2 bytes): 0 SET_FOCUS (STRING: un byte de longitud + ASCII), 1 SETUP_ENG {short index, short id, float pos[3], float max_rpm}, 2 SETUP_GUN {short index, float pos[3], float projectile mass, float muzzle velocity}, 3 SETUP_LGEAR {short index, short id, float pos[3]}, 4 DROP_BOMB y 5 ROCKET_LAUNCH {float pos[3], float mass, WORD flags}, 6 HIT y 7 DAMAGE {float pos[3], float force[3]}, 8 EXPLOSION {float pos[3], float radius}, 9 GUN_FIRE {BYTE gun}, 10 SRV_ADDR, 11 SRV_TITLE, 12 SRS_ADDR (STRING), 13 CLIENT_DAT {long client, long server client, char name[32]}, 14 CTRL_DAT {long parent, short coalition}. Las posiciones de los eventos son locales al avión del jugador; el flujo no tiene posición mundial en absoluto, así que son eventos y números, no un recorrido.

2. Grabación Tacview: `tacviewrecord = 1` en `[KEY = track_record]` hace que el juego escriba `<juego>\data\Tracks\*.acmi` (en multijugador decide el servidor). Un archivo terminado se convierte: cada avión, vehículo y barco con sus posiciones, aparición y retirada (destruido o desaparecido), despegues y aterrizajes cuando la grabación los tiene. Formato ACMI 2.x en texto, sin comprimir o en zip, según <https://www.tacview.net/documentation/acmi/en/>: las líneas "#t" mueven el reloj, las líneas "id,Key=Value,..." fijan propiedades (ids hexadecimales, comas escapadas "\\,", una "\\" al final continúa la línea), "-id" elimina un objeto, el objeto 0 lleva los globales (ReferenceLongitude/Latitude, RecordingTime, ...) y los eventos ("Event=Destroyed\|id\|text"). T = Lon\|Lat\|Alt[\|U\|V] o Lon\|Lat\|Alt\|Roll\|Pitch\|Yaw[\|U\|V\|Heading], longitud y latitud relativas a la referencia; los campos vacíos no cambian. Las posiciones van a un mapa plano alrededor del punto de referencia: x al este, y altitud, z al norte, en metros. El punto de referencia es el `geo` de la sesión, guardado en meta.json y en el pie de la tabla, para que el visor pueda poner el mundo real bajo las trayectorias.

El mismo módulo también sirve a: [IL-2 Sturmovik: Great Battles (datos en vivo)](game-il2.md).

## Posiciones y ejes {#positions-and-axes}

| | |
|---|---|
| Posiciones grabadas | sí |
| Eje hacia arriba | `y` |
| Unidades | metros (este, altitud, norte desde la primera posición fijada) |
| Reflejado para el visor | `z` |
| Escala de unidad (`scale`: el visor multiplica las posiciones por ella) | 1 |

Esto va al `meta.json` de cada sesión (`axes`) y, cuando la sesión tiene posiciones, al pie de `heat.parquet`, para que el visor de 3DHeat gire y escale las filas por sí solo; ver [Los datos](the-data.md).

## Multijugador {#multiplayer}

- Marcado como jugado en línea (`multiplayer`): **sí**. `games --markdown` muestra esto como "permitido (solo lee lo que publica el juego)".
- Tipo `replay`: solo lee lo que el juego o la plataforma entregan (las repeticiones y demos que guarda el juego), así que graba también en el juego en línea, además del juego sin conexión. La marca solo decide si la memoria puede leerse alguna vez.
- Memoria: **nunca** la lee este adaptador. Solo los adaptadores `memory` leen memoria, y nunca en un juego marcado como jugado en línea; ver [Fuentes y reglas](sources-and-rules.md).

## Estadísticas registradas {#statistics-recorded}

Claves de estadística que el código de este adaptador asigna por nombre (el `stats` de cada sesión en `meta.json` y la tabla `stats` de `watcher.sqlite`):

`destroyed`, `duration_s`, `objects`, `{r.event}s`

Una clave entre llaves se completa en tiempo de ejecución (`score.{team}` es una clave por equipo). Las claves que el código toma de una tabla de campos del juego o de sus propios nombres de estadística no aparecen en esta lista; "Qué se graba" de arriba las nombra.

## Completitud {#completeness}

El watcher sigue la [regla de conversión](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md) de 3DHeat: lo que trae la fuente se lee o se guarda, nunca se descarta. Además de las filas, cada paquete, página, línea o respuesta que recibe el adaptador se guarda entero en `heat.raw.parquet` de la sesión (columnas `time`, `ms`, `type`, `used`, `payload`, `text`, y cualquier campo guardado por nombre; `used` marca lo que también se volvió filas), y `selfCheck.completeness` de `meta.json` cuenta cada `type`: `lost` es 0.

**Se lee**

- la T de cada objeto (longitud, latitud, altitud, alabeo, cabeceo, guiñada, U, V, heading) como posiciones una vez por segundo por objeto, con Name, Type, Pilot, Coalition/Color, Country, Group y Parent
- apariciones, retiradas (muerte cuando antes llegó un evento Destroyed, si no salida), eventos TakenOff y Landed, y eventos Message y Bookmark como filas
- los globales ReferenceLongitude/Latitude (el origen del mapa), RecordingTime/ReferenceTime (cuándo), DataSource, DataRecorder y Title en meta.json

**Se guarda en bruto**

- cada línea lógica no vacía entera como `text` (una línea continuada con una "\\" al final se une, como la lee ACMI), bajo su tipo: `header` (FileType, FileVersion), `comment`, `time` (#t), `remove` (-id), `global` y `event` (objeto 0), `object` (id,Key=Value,...)
- lo que solo guarda la copia en bruto: las posiciones entre las filas de una vez por segundo, las armas, proyectiles, bengalas, chaff y otros objetos que no se dibujan como trayectorias, cada propiedad restante (telemetría como IAS, AOA, gases, combustible, cuando la grabación los tiene), otros globales (Comments, Briefing, Author, Category), y eventos distintos de los que se leen (Timeout, LeftArea, ...)

**No disponible**

- nada de lo que tenga la grabación; lo que el juego no escribe en sus grabaciones no está en ellas

**Tamaño**: aproximadamente el texto de la propia grabación más unos 70 bytes por línea, antes de zstd: una grabación de 100 MB ocupa unos 150-250 MB en bruto, que zstd reduce casi al tamaño de la grabación comprimida en zip

## Verificado {#verified}

Probado con archivos ACMI 2.2 sintéticos (en texto y en zip); sin probar con una grabación del juego

## Fuente {#source}

[heat3d_watch/adapters/il2.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/il2.py)

<!-- Generated from the adapter by tools/gen_game_pages.py; change the adapter and run it again rather than editing this page. -->
