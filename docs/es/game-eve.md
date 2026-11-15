---
title: "EVE Online (archivos de registro)"
nav_order: 20
lang: "es"
source: game-eve.md
source_hash: "a5ab6c312c86"
nav_exclude: true
search_exclude: true
---
# EVE Online (archivos de registro) {#eve-online-log-files}

Mientras juegas a EVE Online, el watcher lee los archivos que escribe el juego y guarda lo que ha pasado, para que luego puedas verlo como estadísticas y como una línea de tiempo.

*Detalles técnicos: adaptador `eve`, tipo [`log`](sources-and-rules.md); se ejecuta mientras `exefile.exe` está en marcha y busca datos nuevos cada 0,5 s.*

## Qué se graba {#what-is-recorded}

- daño causado y recibido con el otro barco, piloto, etiqueta de la corporación, arma y calidad del impacto
- fallos causados y recibidos
- recompensas cobradas (muertes de PNJ) con ISK
- saltos entre sistemas
- cada línea del registro de juego y del chat, completa, en heat.raw.parquet
- daño causado y recibido, impactos, fallos, muertes con recompensa e ISK, saltos

## De dónde sale {#where-it-comes-from}

%USERPROFILE%\Documents\EVE\logs\Gamelogs\\\*.txt y los Chatlogs\\\*.txt junto a ellos (todos los archivos escritos desde que arrancó el cliente)

## Cómo activarlo {#how-to-switch-it-on}

No hace falta activar nada: el watcher lee la fuente tal como la entrega el juego o la plataforma.

## Cómo funciona {#how-it-works}

EVE Online: los registros del cliente, `Documents\EVE\logs\Gamelogs\*.txt`.

El cliente escribe un archivo por personaje y por inicio de sesión,
`<yyyymmdd>_<hhmmss>[_<id del personaje>].txt`; el registro en archivo está activado por defecto. Varios clientes
abiertos a la vez escriben cada uno el suyo, así que se siguen todos los archivos escritos desde que
arrancó el juego. Cabecera y líneas (la hora de EVE es UTC):

```text
------------------------------------------------------------
  Gamelog
  Listener: Character Name
  Session Started: 2024.07.02 19:41:40
------------------------------------------------------------
[ 2024.07.02 20:31:28 ] (combat) <color=0xff00ffff><b>200</b> <color=0x77ffffff><font size=10>to</font>
    <b><color=0xffffffff>Pilot[TICK](../Ship)</b><font size=10><color=0x77ffffff> - Weapon - Penetrates
[ 2024.06.25 15:20:01 ] (combat) <color=0xffcc0000><b>375</b> ... from ... - Weapon - Hits
[ 2024.06.25 15:21:00 ] (bounty) <font size=12><b><color=0xff00aa00>15,000 ISK</b> added to next bounty payout
[ 2024.06.25 15:30:00 ] (None) Jumping from System A to System B
```

(la línea de combate es una sola línea en el archivo). Las etiquetas de formato se quitan antes
de comparar. El archivo ha sido UTF-8 y UTF-16 a lo largo de los años; se leen ambos.
CCP no documenta el formato; es el registro de texto plano del cliente, leído como lo leen
las herramientas de la comunidad para registros de combate (por ejemplo <https://docs.rs/crate/eve-log-parser>).
Sin posiciones.

Junto a él, `Documents\EVE\logs\Chatlogs\<canal>_<yyyymmdd>_<hhmmss>[_<id>].txt`:
un archivo por canal de chat y por inicio de sesión (cuando el registro del chat está activado, que es lo habitual en el cliente), en UTF-16, con una cabecera que indica el canal y el listener, y después
`[ yyyy.mm.dd hh:mm:ss ] Remitente > mensaje`.

Cada línea de ambos se guarda completa en el archivo bruto de la sesión (regla del convertidor de 3DHeat):
una línea del registro de juego bajo su canal entre corchetes (`combat`,
`notify`, `bounty`, `None`, ...), una línea de chat como `chat` con su canal, las
líneas de cabecera como `gamelog header` / `chatlog header`.

## Posiciones y ejes {#positions-and-axes}

| | |
|---|---|
| Posiciones grabadas | no |
| Eje hacia arriba | `y` |
| Unidades | sin posiciones grabadas |
| Reflejado para el visor | ninguno |
| Escala de unidades (`scale`: el visor multiplica las posiciones por ella) | 1 |

Esto va a `meta.json` (`axes`) de cada sesión y, cuando la sesión tiene posiciones, al pie de `heat.parquet`, así que el visor de 3DHeat gira y escala las filas por sí mismo; mira [Los datos](the-data.md).

## Multijugador {#multiplayer}

- Marcado como jugado en línea (`multiplayer`): **sí**. `games --markdown` lo muestra como "permitido (solo lee lo que publica el juego)".
- Tipo `log`: solo lee lo que el juego o la plataforma entregan (archivos que escribe el juego mientras se ejecuta), así que graba también en línea, igual que sin conexión; la marca solo decide si se puede leer la memoria.
- Memoria: este adaptador **nunca** la lee. Solo los adaptadores `memory` leen memoria, y nunca en un juego marcado como jugado en línea; mira [Fuentes y reglas](sources-and-rules.md).

## Estadísticas que se graban {#statistics-recorded}

Claves de estadística que el código de este adaptador asigna por nombre (el `stats` de cada sesión en `meta.json` y la tabla `stats` de `watcher.sqlite`):

`bad_lines`, `bounty_isk`, `bounty_kills`, `damage_dealt`, `damage_received`, `hits_dealt`, `hits_received`, `jumps`, `misses_dealt`, `misses_received`

Una clave entre llaves se completa en tiempo de ejecución (`score.{team}` es una clave por equipo). Las claves que el código toma de una tabla de campos del juego o de sus nombres de estadística no aparecen en esta lista; "Qué se graba" más arriba las nombra.

## Completitud {#completeness}

El watcher sigue la [regla del convertidor](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md) de 3DHeat: lo que la fuente contiene se lee o se guarda, nunca se descarta. Además de las filas, cada paquete, página, línea o respuesta que recibe el adaptador se guarda completo en `heat.raw.parquet` de la sesión (columnas `time`, `ms`, `type`, `used`, `payload`, `text`, y cualquier campo guardado por nombre; `used` marca lo que también se convirtió en filas), y `selfCheck.completeness` de `meta.json` cuenta cada `type`; `lost` es 0.

**Se lee**

- del registro de juego, las líneas `(combat)` de impactos causados y recibidos (cantidad, otro piloto, etiqueta de la corporación, nave, arma, calidad del impacto) y los fallos en ambos sentidos
- del registro de juego, los pagos `(bounty)` con ISK, y las líneas `Jumping from A to B`
- el Listener de la cabecera del registro de juego: de quién es el registro

**Se guarda en bruto**

- cada línea del registro de juego completa, `type` = su canal entre corchetes (`combat`, `notify`, `info`, `bounty`, `mining`, `question`, `hint`, `warning`, `None`, ...), con `file` y `listener`; `used` cuando se convirtió en fila; las líneas de cabecera como `gamelog header`
- cada línea del registro de chat completa (Local, corporación, flota, canales privados, los avisos `EVE System` como el cambio de canal Local al saltar), `type` `chat`, con `channel`, `listener` y `file`; las líneas de cabecera como `chatlog header`. Todavía no se convierten en filas
- las etiquetas de formato (`<color>`, `<b>`, `<font>`) se quedan en el texto bruto; las filas las tienen quitadas

**No disponible**

- posiciones: el cliente no escribe ninguna en sus registros
- combates de otros pilotos: un registro de juego es del listener
- registros de inicios de sesión anteriores: cada inicio de sesión escribe archivos nuevos; los más antiguos que esta ejecución del cliente no se vuelven a leer
- el chat cuando el jugador ha desactivado el registro del chat en los ajustes del cliente
- los archivos de caché y de ajustes del cliente: no son registros, y no están documentados

**Tamaño**: un registro de juego ocupa 0,1-2 MB por hora (sobre todo en combate); los registros de chat dependen de los canales abiertos: un canal Local o de flota muy activo, 0,5-3 MB por hora; zstd en heat.raw.parquet lo deja en aproximadamente una décima parte

## Verificado {#verified}

probado con líneas sintéticas de registro de juego en el formato que publican los analizadores de la comunidad; sin probar contra el juego

## Fuente {#source}

[heat3d_watch/adapters/eve.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/eve.py)

<!-- Generated from the adapter by tools/gen_game_pages.py; change the adapter and run it again rather than editing this page. -->
