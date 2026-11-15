---
title: "IL-2 Sturmovik: Great Battles (datos en vivo)"
nav_order: 26
lang: es
source: game-il2.md
source_hash: "b6c4de7dcc14"
nav_exclude: true
search_exclude: true
---
# IL-2 Sturmovik: Great Battles (datos en vivo) {#il-2-sturmovik-great-battles-live-data}

Mientras juegas a IL-2 Sturmovik: Great Battles, el watcher guarda los datos que el propio juego envía, para que luego puedas verlos como estadísticas y una línea de tiempo.

*Detalles técnicos: adaptador `il2`, tipo [`telemetry`](sources-and-rules.md); se ejecuta mientras `Il-2.exe` o `IL2Series.exe` está en marcha y busca datos nuevos cada 0,1 s.*

## Qué se graba {#what-is-recorded}

- salidas: el avión tomado (spawn) y el momento en que deja de salir información (session_end); sin posición en el mundo, porque el juego no la envía
- bombas y cohetes lanzados (masa), impactos y daños recibidos, explosiones, ráfagas de disparo; posiciones relativas al avión
- velocidad aerodinámica equivalente, altura sobre el terreno (AGL), velocidad vertical, g, rpm del motor una vez por segundo, con todos los demás indicadores que trae el paquete (presión del colector, vibración del motor, estado y presión de los tren de marchas, ángulo de ataque, ángulo de derrape, aceleración x/y/z, vibración de la cabina, flaps, aerofrenos)
- salidas, munición disparada, bombas, cohetes, impactos recibidos, velocidad máxima, g máximo, tiempo de vuelo; título del servidor y nombre del piloto en línea
- cada paquete de telemetría guardado entero en heat.raw.parquet

## De dónde sale {#where-it-comes-from}

la salida de telemetría del juego por UDP a 127.0.0.1:41995 ([KEY = telemetrydevice] en &lt;juego>\data\startup.cfg)

## Cómo activarlo {#how-to-switch-it-on}

python -m heat3d_watch setup il2 --apply (añade addrN = "127.0.0.1:41995", enable = true), reinicia IL-2

Escribe el comando en una terminal abierta en la carpeta del watcher (ver [Antes de empezar](before-you-start.md)). Si falla, la última línea dice por qué; [Instalar y ejecutar](installing-and-running.md) recoge las causas más habituales.

`python -m heat3d_watch setup il2` muestra los archivos que cambiaría; `python -m heat3d_watch setup il2 --apply` los cambia, guardando el original como `<archivo>.heat3d-backup` (ver [Comandos](commands.md#setup)). Imprime `il2: changed: ...` por cada cambio, o `il2: nothing to change` cuando ya está activado.

## Cómo funciona {#how-it-works}

IL-2 Sturmovik: Great Battles: la salida de telemetría del juego por UDP, y sus propias grabaciones de Tacview.

1. Telemetría ("Telemetry output of IL2 v4.003", revisión 1.2, incluida como `<juego>\Doc\UDP_Output\Il2_TeleOutput.pdf`). Se activa en `<juego>\data\startup.cfg`, sección `[KEY = telemetrydevice]`: `addr`, `addr1`, ... = "IP[:puerto]" (varios destinos a la vez), `decimation` (50 Hz / n), `enable`, `port`. `setup` añade un destino, 127.0.0.1:41995 (JoyPro usa 41994; el puerto por defecto del juego es 4322), y activa la salida. Paquetes, little-endian:

   ```text
   DWORD  Packet_ID 0x54000101
   WORD   Size
   DWORD  Tick (1/50 s)
   BYTE   Indicators_Count, then SIndicator {WORD id, BYTE n, n x 32-bit float}
   BYTE   Events_Count,     then SEvent     {WORD id, BYTE size, size bytes}
   ```

   Indicadores: 0 ENG_RPM, 1 ENG_MP, 2/3 vibración del motor, 4 LGEARS_STATE, 5 LGEARS_PRESS, 6 EAS (m/s), 7 AOA (rad), 8 ACCELERATION (xyz incluida la gravedad), 9 COCKPIT_SHAKE, 10 AGL (m), 11 FLAPS, 12 AIR_BRAKES, 13 AOS (rad), 14 VERTICAL_SPEED (m/s). Eventos (empaquetados de 2 bytes): 0 SET_FOCUS (STRING: un byte de longitud + ASCII), 1 SETUP_ENG {short index, short id, float pos[3], float max_rpm}, 2 SETUP_GUN {short index, float pos[3], float projectile mass, float muzzle velocity}, 3 SETUP_LGEAR {short index, short id, float pos[3]}, 4 DROP_BOMB y 5 ROCKET_LAUNCH {float pos[3], float mass, WORD flags}, 6 HIT y 7 DAMAGE {float pos[3], float force[3]}, 8 EXPLOSION {float pos[3], float radius}, 9 GUN_FIRE {BYTE gun}, 10 SRV_ADDR, 11 SRV_TITLE, 12 SRS_ADDR (STRING), 13 CLIENT_DAT {long client, long server client, char name[32]}, 14 CTRL_DAT {long parent, short coalition}. Las posiciones de los eventos son relativas al avión del jugador; el flujo no tiene ninguna posición en el mundo, así que son eventos y números, no un trazado.

2. Grabación de Tacview: `tacviewrecord = 1` en `[KEY = track_record]` hace que el juego escriba `<juego>\data\Tracks\*.acmi` (en multijugador lo decide el servidor). Un archivo terminado se convierte: cada avión, vehículo y barco con sus posiciones, aparición y retirada (destruido o desaparecido), despegues y aterrizajes cuando la grabación los tiene. Formato de texto ACMI 2.x, plano o comprimido, según <https://www.tacview.net/documentation/acmi/en/>: las líneas "#t" mueven el reloj, las líneas "id,Clave=Valor,..." fijan propiedades (ids hexadecimales, comas escapadas "\\,", una "\\" al final continúa la línea), "-id" elimina un objeto, el objeto 0 guarda los globales (ReferenceLongitude/Latitude, RecordingTime, ...) y los eventos ("Event=Destroyed\|id\|texto"). T = Lon\|Lat\|Alt[\|U\|V] o Lon\|Lat\|Alt\|Roll\|Pitch\|Yaw[\|U\|V\|Heading], longitud y latitud relativas a la referencia, los campos vacíos no cambian. Las posiciones van a un mapa plano alrededor del punto de referencia: x este, y altitud, z norte, en metros. El punto de referencia es el `geo` de la sesión, guardado en meta.json y en el pie de la tabla, así que el visor puede colocar el mundo real bajo los trazados.

El mismo módulo también sirve a: [IL-2 Sturmovik: Great Battles (repeticiones)](game-il2-tacview.md).

## Posiciones y ejes {#positions-and-axes}

| | |
|---|---|
| Posiciones grabadas | no |
| Eje hacia arriba | `y` |
| Unidades | ninguna: la telemetría no tiene posiciones en el mundo |
| Reflejado para el visor | ninguno |
| Escala de unidad (`scale`: el visor multiplica las posiciones por ella) | 1 |

Esto va al `meta.json` de cada sesión (`axes`) y, cuando la sesión tiene posiciones, al pie (footer) de `heat.parquet`, así que el visor de 3DHeat gira y escala las filas por sí mismo; ver [Los datos](the-data.md).

## Multijugador {#multiplayer}

- Marcado como jugado en línea (`multiplayer`): **sí**. `games --markdown` lo muestra como "permitido (lee solo lo que publica el juego)".
- Tipo `telemetry`: lee solo lo que el juego o la plataforma entregan (un puerto UDP o memoria compartida que el juego publica), así que graba también en el juego en línea; la marca solo decide si se puede leer la memoria en algún momento.
- Memoria: **nunca** la lee este adaptador. Solo los adaptadores `memory` leen memoria, y nunca en un juego marcado como jugado en línea; ver [Fuentes y reglas](sources-and-rules.md).

## Estadísticas grabadas {#statistics-recorded}

Claves de estadística que el código de este adaptador fija por nombre (el `stats` de cada sesión en `meta.json` y la tabla `stats` de `watcher.sqlite`):

`bad_packets`, `bombs_dropped`, `damage_taken`, `explosions`, `flight_time`, `hits_taken`, `max_agl_m`, `max_eas_kmh`, `max_g`, `ordnance_kg`, `rockets_fired`, `rounds_fired`, `sorties`

Una clave entre llaves se completa en tiempo de ejecución (`score.{team}` es una clave por equipo). Las claves que el código toma de una tabla de campos del juego o de sus propios nombres de estadística no están en esta lista; "Qué se graba" más arriba las nombra.

## Completitud {#completeness}

El watcher sigue la [regla de conversores](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md) de 3DHeat: lo que la fuente contiene se lee o se guarda, nunca se descarta. Además de las filas, cada paquete, página, línea o respuesta que recibe el adaptador se guarda entero en `heat.raw.parquet` de la sesión (columnas `time`, `ms`, `type`, `used`, `payload`, `text`, y los campos que se guardan por nombre; `used` marca lo que también se convirtió en filas), y `selfCheck.completeness` de `meta.json` cuenta cada `type`: `lost` es 0.

**Leído**

- SET_FOCUS (el avión tomado: una salida), DROP_BOMB y ROCKET_LAUNCH (masa, posición relativa), HIT y DAMAGE (posición relativa, fuerza), EXPLOSION (posición relativa, radio), GUN_FIRE (disparos por consulta) como filas
- SETUP_ENG (índice, id, posición relativa, rpm máximas), SETUP_GUN (índice, posición relativa, masa del proyectil, velocidad de salida) y SETUP_LGEAR (índice, id, posición relativa) como filas: los motores, cañones y patas del tren del avión al empezar la salida
- SRV_TITLE, SRV_ADDR, SRS_ADDR y CLIENT_DAT (nombre del piloto) en meta.json; la coalición de CTRL_DAT como equipo de la salida
- los quince indicadores de la especificación en la fila `state` de una vez por segundo (un valor como número, uno por motor, pata de tren o eje como lista); velocidad, g y AGL máximos de cada paquete

**Guardado en bruto**

- cada datagrama entero como `payload`, bajo su Packet_ID: `0x54000101` para la telemetría (usado cuando hizo una fila o una entrada de meta.json), cualquier otro id como él mismo, un datagrama demasiado corto para uno como `short`
- lo que solo tiene el archivo auxiliar en bruto: los indicadores entre las filas de una vez por segundo (el juego los envía a 50 Hz / decimation), un evento SETUP más corto que el diseño de la especificación, ids de evento que la especificación no lista

**No disponible**

- una posición en el mundo: la salida de telemetría no tiene ninguna (las posiciones de los eventos son relativas al avión); el adaptador il2-tacview lee las posiciones de las grabaciones Tacview del propio juego
- otros aviones y jugadores: la salida describe solo el avión propio del jugador

**Tamaño**: unos 8 MB por hora con los 10 Hz de `setup` (decimation 5; un paquete ocupa unos 160 bytes más su marco), 40 MB a los 50 Hz completos del juego, antes de zstd; zstd reduce los flotantes repetitivos a una fracción

## Verificado {#verified}

probado con paquetes creados a partir de la especificación Il2_TeleOutput del propio juego (rev. 1.2); las ediciones de startup.cfg, probadas en una copia del archivo; sin probar contra el juego en marcha

## Fuente {#source}

[heat3d_watch/adapters/il2.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/il2.py)

<!-- Generated from the adapter by tools/gen_game_pages.py; change the adapter and run it again rather than editing this page. -->
