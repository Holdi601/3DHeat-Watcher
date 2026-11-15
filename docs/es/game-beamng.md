---
title: "BeamNG.drive (datos en vivo)"
nav_order: 7
lang: "es"
source: game-beamng.md
source_hash: "1c23a869a62f"
nav_exclude: true
search_exclude: true
---
# BeamNG.drive (datos en vivo) {#beamngdrive-live-data}

Mientras juegas a BeamNG.drive, el watcher guarda los datos que el propio juego envía, para que luego puedas verlos en un mapa del visor de 3DHeat.

*Detalles técnicos: adaptador `beamng`, tipo [`telemetry`](sources-and-rules.md); se ejecuta mientras `BeamNG.drive.x64.exe` o `BeamNG.drive.exe` está en marcha y busca datos nuevos cada 0,1 s.*

## Qué se graba {#what-is-recorded}

- la posición del coche propio (en el mundo, m, girada para que Y apunte hacia arriba) 10 veces por segundo, con velocidad, marcha, acelerador y freno
- inicio de la conducción, reinicios (reaparición), vueltas pasado el punto donde empezó la conducción
- vueltas, mejor vuelta, distancia, velocidad máxima

## De dónde sale {#where-it-comes-from}

UDP 127.0.0.1:4460 desde el mod de protocolo heat3d (mods/beamng/heat3d en este repositorio)

## Cómo activarlo {#how-to-switch-it-on}

`python -m heat3d_watch setup beamng --apply` instala el mod; luego Opciones > Otros > Protocolos > "others"

Escribe el comando en una terminal abierta en la carpeta del watcher (mira [Antes de empezar](before-you-start.md)). Si falla, la última línea dice por qué; [Instalación y uso](installing-and-running.md) recoge las causas habituales.

`python -m heat3d_watch setup beamng` lista los archivos que cambiaría; `python -m heat3d_watch setup beamng --apply` los cambia, guardando el original como `<archivo>.heat3d-backup` (mira [Comandos](commands.md#setup)). Imprime `beamng: changed: ...` por cada cambio, o `beamng: nothing to change` cuando ya está activado.

## Cómo funciona {#how-it-works}

La telemetría propia de los juegos de carreras: Forza, los juegos de Assetto Corsa, los juegos de rally y BeamNG, grabada como trazados, vueltas y tramos.

Todos estos juegos publican su telemetría a propósito, para paneles y para
simuladores de movimiento; no se inyecta nada y no se lee nada que el juego no entregue. La
decodificación no se escribe dos veces: son los grabadores de vueltas de gamecapture, que están en
`heat3d_capture/telemetry` de 3DHeat GameCapture, copiados a `heat3d_watch/decoders` (probados allí con paquetes creados a partir
de los formatos publicados). Este módulo convierte sus fotogramas en las filas del watcher:
la posición del coche varias veces por segundo con su velocidad, marcha y pedales,
un evento por vuelta o tramo, y los números que anota el piloto: vueltas, mejor vuelta,
distancia y velocidad máxima.

#### Forza (Horizon 4/5/6, Motorsport) {#forza-horizon-456-motorsport}

UDP "Data Out", que se activa en el HUD y en los ajustes de juego del propio juego, hacia
127.0.0.1 puerto 5300, formato Dash. Un paquete por tick de simulación; el desplazamiento
del bloque del panel se encuentra a partir de los paquetes (`forza.detect_layout`). Metros del
mundo, Y hacia arriba; el mundo es zurdo y se dibuja tal como llega, igual que lo hace el
grabador de vueltas (documentación "Data Out" de Forza Motorsport y de Forza Horizon).
El juego envía a un solo puerto, y FH Companion y otras aplicaciones Data Out escuchan
en ese mismo. Dos programas no pueden compartirlo: en Windows, el socket enlazado
a 127.0.0.1 recibe los paquetes y el enlazado a todas las direcciones en el mismo
puerto no recibe ninguno, sea cual sea el que llegó primero. Por eso el watcher espera un poco
tras arrancar el juego antes de tomar el puerto, nunca lo quita a una aplicación que
lo tiene, y lo suelta en cuanto otra aplicación empieza a escuchar en él.
Mientras tiene el puerto, reenvía cada paquete sin cambios a
127.0.0.1:5301: pon el campo de puerto de FH Companion (su pestaña de telemetría) en 5301 y
ambos graban.

#### BeamNG.drive {#beamngdrive}

El mod de protocolo `heat3d` que incluye gamecapture (UDP 4460, Opciones > Otros >
Protocolos > "others"); el mundo de BeamNG, con Z hacia arriba, se gira para que Y apunte hacia arriba, como lo hace `beamng.py`.

#### Todo lo que se guarda {#everything-kept}

Las filas son unas pocas por segundo; los juegos envían muchos más datos. Cada paquete UDP que
llega (en los menús, entre vueltas, los que ningún decodificador lee) se guarda completo
en `heat.raw.parquet` de la sesión, bajo su formato (`dash-horizon`,
`session_update`, `extradata3`, `H3D1`, ...), y cada página de memoria compartida
(toda la asignación, no solo los bytes decodificados) cada vez que cambia, bajo
el nombre de su asignación (`acpmf_physics`, ...). `used` marca lo que también se convirtió en
filas; `selfCheck.completeness` de `meta.json` cuenta cada tipo (regla del convertidor de 3DHeat).

El mismo módulo también sirve para: [Assetto Corsa (datos en vivo)](game-assetto-corsa.md), [Assetto Corsa Competizione (datos en vivo)](game-assetto-corsa-competizione.md), [Assetto Corsa EVO (datos en vivo)](game-assetto-corsa-evo.md), [Assetto Corsa Rally (datos en vivo)](game-assetto-corsa-rally.md), [DiRT Rally 2.0 (datos en vivo)](game-dirt-rally-2.md), [EA SPORTS WRC (datos en vivo)](game-ea-wrc.md), [Forza Horizon 4 (datos en vivo)](game-forza-horizon-4.md), [Forza Horizon 5 (datos en vivo)](game-forza-horizon-5.md), [Forza Horizon 6 (datos en vivo)](game-forza-horizon-6.md), [Forza Motorsport (datos en vivo)](game-forza-motorsport.md), [Richard Burns Rally (datos en vivo)](game-richard-burns-rally.md).

## Posiciones y ejes {#positions-and-axes}

| | |
|---|---|
| Posiciones grabadas | sí |
| Eje hacia arriba | `y` |
| Unidades | metros (el mundo de BeamNG, con Z hacia arriba, girado sobre X, como lo hace el grabador de vueltas) |
| Reflejado para el visor | ninguno |
| Escala de unidades (`scale`: el visor multiplica las posiciones por ella) | 1 |

Esto va a `meta.json` (`axes`) de cada sesión y, cuando la sesión tiene posiciones, al pie de `heat.parquet`, así que el visor de 3DHeat gira y escala las filas por sí mismo; mira [Los datos](the-data.md).

## Multijugador {#multiplayer}

- Marcado como jugado en línea (`multiplayer`): **no**. `games --markdown` lo muestra como "un jugador".
- Tipo `telemetry`: solo lee lo que el juego o la plataforma entregan (un puerto UDP o memoria compartida que publica el juego), así que graba también en línea, igual que sin conexión; la marca solo decide si se puede leer la memoria.
- Memoria: este adaptador **nunca** la lee. Solo los adaptadores `memory` leen memoria, y nunca en un juego marcado como jugado en línea; mira [Fuentes y reglas](sources-and-rules.md).

## Estadísticas que se graban {#statistics-recorded}

Claves de estadística que el código de este adaptador asigna por nombre (el `stats` de cada sesión en `meta.json` y la tabla `stats` de `watcher.sqlite`):

`best_lap`, `distance_km`, `laps`, `top_speed_kmh`

Una clave entre llaves se completa en tiempo de ejecución (`score.{team}` es una clave por equipo). Las claves que el código toma de una tabla de campos del juego o de sus nombres de estadística no aparecen en esta lista; "Qué se graba" más arriba las nombra.

## Completitud {#completeness}

El watcher sigue la [regla del convertidor](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md) de 3DHeat: lo que la fuente contiene se lee o se guarda, nunca se descarta. Además de las filas, cada paquete, página, línea o respuesta que recibe el adaptador se guarda completo en `heat.raw.parquet` de la sesión (columnas `time`, `ms`, `type`, `used`, `payload`, `text`, y cualquier campo guardado por nombre; `used` marca lo que también se convirtió en filas), y `selfCheck.completeness` de `meta.json` cuenta cada `type`; `lost` es 0.

**Se lee**

- filas a 10 Hz: posición, velocidad, marcha, acelerador, freno, yaw, rpm, dirección; inicio de la conducción, reinicios, vueltas

**Se guarda en bruto**

- cada paquete que llega al puerto, completo, a los 100 Hz del mod: `H3D1` (la estructura de 160 bytes del mod: reloj, posición, velocidad, ejes del coche, velocidad de giro, nueve entradas, velocidad superficial por rueda, rotación, carga y material del suelo), `<n>-byte` para cualquier otra cosa

**No disponible**

- lo que el mod no envía: BeamNG no tiene un paquete de telemetría fijo, así que los canales son los que eligió el mod heat3d (otros vehículos, daños y el nombre del mapa no están)

**Tamaño**: unos 80 MB por hora antes de comprimir (100 paquetes por segundo de 160 bytes más una cabecera de 70 bytes por elemento)

## Verificado {#verified}

la decodificación es la del grabador de vueltas de gamecapture (probada con paquetes construidos a partir de la estructura del mod); el adaptador probado con esos paquetes; el mod no está probado en el juego

## Fuente {#source}

[heat3d_watch/adapters/racing.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/racing.py)

<!-- Generated from the adapter by tools/gen_game_pages.py; change the adapter and run it again rather than editing this page. -->
