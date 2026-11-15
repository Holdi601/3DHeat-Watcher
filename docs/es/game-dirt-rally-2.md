---
title: "DiRT Rally 2.0 (datos en vivo)"
nav_order: 11
lang: "es"
source: game-dirt-rally-2.md
source_hash: "367131ff990b"
nav_exclude: true
search_exclude: true
---
# DiRT Rally 2.0 (datos en vivo) {#dirt-rally-20-live-data}

Mientras juegas a DiRT Rally 2.0, el watcher guarda los datos que el propio juego envía hacia fuera, para que después puedas verlos en un mapa del visor de 3DHeat.

*Detalles técnicos: adaptador `dirt-rally-2`, tipo [`telemetry`](sources-and-rules.md); se ejecuta mientras `dirtrally2.exe` está en marcha y busca datos nuevos cada 0,1 s.*

## Qué se graba {#what-is-recorded}

- posición de tu coche (XYZ en el mundo, m) a 10 Hz, con velocidad, marcha, acelerador, freno y distancia en la etapa
- inicio de etapa (cuando arranca el reloj de la etapa), llegada con el tiempo de etapa, reinicios
- teletransportes (un reinicio a la carretera): `teleport` donde estaba el coche, `spawn` donde está ahora
- etapas, mejor tiempo de etapa, distancia y velocidad máxima

## De dónde viene {#where-it-comes-from}

UDP 127.0.0.1:20777, extradata=3 (Documents\My Games\DiRT Rally 2.0\hardwaresettings\hardware_settings_config.xml). Mientras otra app tenga el puerto 20777, el watcher se lo deja a ella

## Cómo activarlo {#how-to-switch-it-on}

`python -m heat3d_watch setup dirt-rally-2 --apply` pone &lt;udp enabled="true" extradata="3"> (antes guarda una copia)

Escribe el comando en una terminal abierta en la carpeta del watcher (ver [Antes de empezar](before-you-start.md)). Si falla, la última línea dice por qué; [Instalación y ejecución](installing-and-running.md) cubre las causas habituales.

`python -m heat3d_watch setup dirt-rally-2` lista los archivos que cambiaría; `python -m heat3d_watch setup dirt-rally-2 --apply` los cambia, guardando el original como `<file>.heat3d-backup` (ver [Comandos](commands.md#setup)). Muestra `dirt-rally-2: changed: ...` por cada cambio, o `dirt-rally-2: nothing to change` si ya está activado.

## Cómo funciona {#how-it-works}

La telemetría propia de los juegos de carreras: Forza, los juegos de Assetto Corsa, los juegos de rally y BeamNG, grabada como recorridos, vueltas y etapas.

Todos estos juegos publican su telemetría a propósito, para paneles y simuladores de movimiento. No se inyecta nada y no se lee nada que el juego no entregue. La decodificación no está escrita dos veces: son los grabadores de vueltas de gamecapture, en `heat3d_capture/telemetry` de 3DHeat GameCapture, copiados en `heat3d_watch/decoders` (probados allí con paquetes construidos a partir de los formatos publicados). Este módulo convierte sus fotogramas en filas del watcher: la posición del coche unas pocas veces por segundo con su velocidad, marcha y pedales, un evento por vuelta o etapa, y los números que un piloto lleva: vueltas, mejor vuelta, distancia y velocidad máxima.

#### Forza (Horizon 4/5/6, Motorsport) {#forza-horizon-456-motorsport}

Salida "Data Out" por UDP, activada en los ajustes de HUD y de jugabilidad del juego, a 127.0.0.1 puerto 5300, formato Dash. Un paquete por tick de simulación; el desplazamiento del bloque del panel se encuentra a partir de los propios paquetes (`forza.detect_layout`). Metros del mundo, Y hacia arriba. El mundo es de sistema izquierdo y se dibuja tal como llega, igual que lo hace el grabador de vueltas (documentación "Data Out" de Forza Motorsport y Forza Horizon). El juego envía a un solo puerto, y FH Companion y otras apps de Data Out escuchan en ese mismo puerto. Dos programas no pueden compartirlo: en Windows, el socket ligado a 127.0.0.1 recibe los paquetes, y el que está ligado a todas las direcciones en el mismo puerto no recibe ninguno, da igual cuál llegó primero. Por eso el watcher espera un poco después de que arranque el juego antes de tomar el puerto, nunca se lo quita a una app que lo tenga, y lo suelta en cuanto otra app empieza a escuchar en él. Mientras tiene el puerto, reenvía cada paquete sin cambios a 127.0.0.1:5301: pon el campo de puerto de FH Companion (su pestaña de telemetría) en 5301 y ambos graban.

#### EA SPORTS WRC, DiRT Rally 2.0, Richard Burns Rally {#ea-sports-wrc-dirt-rally-20-richard-burns-rally}

UDP: `Documents/My Games/WRC/telemetry/config.json` de WRC (el paquete `session_update` de la estructura `wrc`), `hardware_settings_config.xml` de DiRT (`<udp enabled="true" extradata="3" port="20777">`), el plugin NGP de RBR (`udpTelemetry=1`, puerto 6776). Las etapas se separan con el reloj de etapa del juego (`rally.StageSplitter`). RBR no documenta sus ejes: el eje hacia arriba es el que menos varía a lo largo de la etapa, y se decide al cerrar la sesión.

#### Todo lo que se guarda {#everything-kept}

Las filas son unas pocas por segundo; los juegos envían bastante más. Cada paquete UDP que llega, en los menús, entre vueltas o los que ningún decodificador lee, se guarda entero en `heat.raw.parquet` de la sesión, con su formato (`dash-horizon`, `session_update`, `extradata3`, `H3D1`, ...). Cada página de memoria compartida (toda la región asignada, no solo los bytes decodificados) se guarda cada vez que cambia, con el nombre de su región (`acpmf_physics`, ...). `used` marca lo que también se convirtió en filas. `selfCheck.completeness` de meta.json cuenta cada tipo (regla de conversión de 3DHeat).

El mismo módulo también sirve a: [Assetto Corsa (datos en vivo)](game-assetto-corsa.md), [Assetto Corsa Competizione (datos en vivo)](game-assetto-corsa-competizione.md), [Assetto Corsa EVO (datos en vivo)](game-assetto-corsa-evo.md), [Assetto Corsa Rally (datos en vivo)](game-assetto-corsa-rally.md), [BeamNG.drive (datos en vivo)](game-beamng.md), [EA SPORTS WRC (datos en vivo)](game-ea-wrc.md), [Forza Horizon 4 (datos en vivo)](game-forza-horizon-4.md), [Forza Horizon 5 (datos en vivo)](game-forza-horizon-5.md), [Forza Horizon 6 (datos en vivo)](game-forza-horizon-6.md), [Forza Motorsport (datos en vivo)](game-forza-motorsport.md), [Richard Burns Rally (datos en vivo)](game-richard-burns-rally.md).

## Posiciones y ejes {#positions-and-axes}

| | |
|---|---|
| Posiciones grabadas | sí |
| Eje hacia arriba | `y` |
| Unidades | metros |
| Reflejado para el visor | ninguno |
| Escala de unidad (`scale`: el visor multiplica las posiciones por ella) | 1 |

Esto va al `meta.json` de cada sesión (`axes`) y, cuando la sesión tiene posiciones, al pie de `heat.parquet`, para que el visor de 3DHeat gire y escale las filas por sí solo; ver [Los datos](the-data.md).

## Multijugador {#multiplayer}

- Marcado como jugado en línea (`multiplayer`): **sí**. `games --markdown` muestra esto como "permitido (solo lee lo que publica el juego)".
- Tipo `telemetry`: solo lee lo que el juego o la plataforma entregan (un puerto UDP o la memoria compartida que publica el juego), así que graba también en el juego en línea, además del juego sin conexión. La marca solo decide si la memoria puede leerse alguna vez.
- Memoria: **nunca** la lee este adaptador. Solo los adaptadores `memory` leen memoria, y nunca en un juego marcado como jugado en línea; ver [Fuentes y reglas](sources-and-rules.md).

## Estadísticas registradas {#statistics-recorded}

Claves de estadística que el código de este adaptador asigna por nombre (el `stats` de cada sesión en `meta.json` y la tabla `stats` de `watcher.sqlite`):

`best_lap`, `best_stage`, `distance_km`, `laps`, `stages`, `top_speed_kmh`

Una clave entre llaves se completa en tiempo de ejecución (`score.{team}` es una clave por equipo). Las claves que el código toma de una tabla de campos del juego o de sus propios nombres de estadística no aparecen en esta lista; "Qué se graba" de arriba las nombra.

## Completitud {#completeness}

El watcher sigue la [regla de conversión](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md) de 3DHeat: lo que trae la fuente se lee o se guarda, nunca se descarta. Además de las filas, cada paquete, página, línea o respuesta que recibe el adaptador se guarda entero en `heat.raw.parquet` de la sesión (columnas `time`, `ms`, `type`, `used`, `payload`, `text`, y cualquier campo guardado por nombre; `used` marca lo que también se volvió filas), y `selfCheck.completeness` de `meta.json` cuenta cada `type`: `lost` es 0.

**Se lee**

- filas a 10 Hz: posición, velocidad, marcha, acelerador, freno, distancia en la etapa, guiñada, rpm, dirección; inicio de etapa, llegada con el tiempo de etapa, reinicios

**Se guarda en bruto**

- cada paquete que llega al puerto, entero, a la velocidad del juego, con su formato: `extradata3` (66 floats, 264 bytes), `extradata3-64` (el de DiRT Rally, de 64) y `<n>-byte` en los demás casos
- dentro del paquete, además de las filas: los 66 floats completos (velocidad mundial, vectores lateral y frontal, posición y velocidad de suspensión por rueda, velocidad de la huella de contacto y temperatura de freno, fuerzas G, vueltas, longitud de la etapa); los floats sin nombre fijado están en los archivos de vuelta como `float<i>`

**No disponible**

- otros coches: el juego envía solo el coche del jugador
- un canal del freno de mano: el paquete no lo tiene

**Tamaño**: unos 70 MB por hora a 60 paquetes por segundo (264 bytes más una cabecera de 70 bytes por elemento); zstd guarda una fracción

## Verificado {#verified}

La decodificación es la del grabador de vueltas de gamecapture (probada con paquetes construidos a partir de los formatos documentados); el adaptador, probado con paquetes construidos en la prueba y enviados por UDP; sin probar contra el juego

## Fuente {#source}

[heat3d_watch/adapters/racing.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/racing.py)

<!-- Generated from the adapter by tools/gen_game_pages.py; change the adapter and run it again rather than editing this page. -->
