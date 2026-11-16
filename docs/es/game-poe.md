---
title: "Path of Exile (archivos de registro)"
nav_order: 35
lang: "es"
source: game-poe.md
source_hash: "b5783b5a5690"
nav_exclude: true
search_exclude: true
---
# Path of Exile (archivos de registro) {#path-of-exile-log-files}

Mientras juegas a Path of Exile, el watcher lee los archivos que escribe el juego y guarda lo que ha pasado, para que luego puedas verlo como estadísticas y como una línea de tiempo.

*Detalles técnicos: adaptador `poe`, tipo [`log`](sources-and-rules.md); se ejecuta mientras `PathOfExile.exe`, `PathOfExile_x64.exe`, `PathOfExileSteam.exe`, `PathOfExile_x64Steam.exe`, `PathOfExileEGS.exe`, `PathOfExile_x64EGS.exe`, `PathOfExile_KG.exe` o `PathOfExile_x64_KG.exe` está en marcha y busca datos nuevos cada 0,5 s.*

## Qué se graba {#what-is-recorded}

- zonas a las que se entra, con el nivel de área, el id de área y su semilla
- subidas de nivel, con clase y nivel
- muertes ("has been slain")
- jugadores que entran y salen del área, susurros recibidos y enviados, solicitudes de intercambio, intercambios aceptados
- cada línea de Client.txt de esta sesión, completa, en heat.raw.parquet
- muertes, niveles ganados, nivel máximo, zonas visitadas, zonas distintas, susurros, solicitudes de intercambio, intercambios

## De dónde sale {#where-it-comes-from}

&lt;instalación>\logs\Client.txt de Path of Exile o Path of Exile 2 (se sigue; la carpeta de instalación es la del ejecutable en marcha)

## Cómo activarlo {#how-to-switch-it-on}

No hace falta activar nada: el watcher lee la fuente tal como la entrega el juego o la plataforma.

## Cómo funciona {#how-it-works}

Path of Exile y Path of Exile 2: el registro del cliente, `<instalación>\logs\Client.txt`.

Ambos juegos añaden líneas a un único Client.txt en su carpeta de instalación mientras
estén instalados (crece entre inicios). Las líneas tienen este aspecto:

```text
2024/01/01 12:00:00 123456789 cff94598 [INFO Client 1234] : You have entered Lioneye's Watch.
2024/01/01 12:00:00 123456789 cff94598 [DEBUG Client 1234] Generating level 2 area "1_1_2" with seed 1
2024/01/01 12:00:00 123456789 cff94598 [INFO Client 1234] : Name (Witch) is now level 2
2024/01/01 12:00:00 123456789 cff94598 [INFO Client 1234] : Name has been slain.
2024/01/01 12:00:00 123456789 cff94598 [INFO Client 1234] @From Name: Hi, I would like to buy your ...
```

- hora local, un contador en milisegundos, un hash, el nivel y el hilo, y después
  lo que muestra la ventana del chat. Los mensajes son los del cliente en inglés; un cliente
  en otro idioma los escribe traducidos y aquí no se entienden. Nada da una posición. El formato
  no lo documenta Grinding Gear Games; es el registro de texto plano del juego, tal como lo leen
  desde hace años las herramientas de la comunidad (ayudantes de intercambio, guías de nivel); por ejemplo
  <https://github.com/klayveR/poe-log-monitor> (MIT) para la lista de eventos.

La carpeta de instalación es la del ejecutable en marcha; sin uno, se buscan las bibliotecas de Steam
y la carpeta predeterminada del cliente independiente.

Cada línea de esta sesión se guarda completa en el archivo bruto de la sesión (regla del convertidor
de 3DHeat), tenga o no sentido aquí: `type` es el nivel y el registrador entre sus corchetes
(`INFO Client`, `DEBUG Client`, `WARN Client`, ...); una línea con marca de tiempo sin corchetes es
`untagged`, y una línea sin marca de tiempo, `untimed`.

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

`bad_lines`, `character_class`, `deaths`, `level`, `levels_gained`, `trade_requests_received`, `trade_requests_sent`, `trades`, `whispers`, `zones_distinct`, `zones_entered`

Una clave entre llaves se completa en tiempo de ejecución (`score.{team}` es una clave por equipo). Las claves que el código toma de una tabla de campos del juego o de sus nombres de estadística no aparecen en esta lista; "Qué se graba" más arriba las nombra.

## Completitud {#completeness}

El watcher sigue la [regla del convertidor](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md) de 3DHeat: lo que la fuente contiene se lee o se guarda, nunca se descarta. Además de las filas, cada paquete, página, línea o respuesta que recibe el adaptador se guarda completo en `heat.raw.parquet` de la sesión (columnas `time`, `ms`, `type`, `used`, `payload`, `text`, y cualquier campo guardado por nombre; `used` marca lo que también se convirtió en filas), y `selfCheck.completeness` de `meta.json` cuenta cada `type`; `lost` es 0.

**Se lee**

- `You have entered <zona>`, con el nivel de área, el id de área y la semilla de la línea `Generating level` anterior
- `<nombre> (<clase>) is now level <n>`, `<nombre> has been slain`, jugadores que entran y salen del área, susurros recibidos y enviados (con indicación de si son una solicitud de intercambio), intercambios aceptados y cancelados

**Se guarda en bruto**

- cada línea de esta sesión, completa, `type` = el nivel y el registrador entre sus corchetes (`INFO Client`, `DEBUG Client`, `WARN Client`, `CRIT Client`, ...), `used` cuando se convirtió en fila: el chat global, de intercambio, de grupo y de gremio, `Connecting to instance server`, los avisos de AFK y no molestar, las respuestas a comandos de chat como `/played` y `/deaths`, las líneas de carga y de motor del cliente; se guardan, todavía no se convierten en filas
- una línea con marca de tiempo sin corchetes (`***** LOG FILE OPENING *****`) como `untagged`, y una línea sin marca de tiempo como `untimed`

**No disponible**

- posiciones: nada en el registro da ninguna
- lo que escribe un cliente en otro idioma: las líneas se guardan, pero solo los mensajes en inglés se convierten en filas
- líneas de inicios anteriores: Client.txt crece entre inicios; se dejan las líneas con marca de tiempo anterior a esta ejecución del juego (ya se guardaron cuando se jugaron)
- muertes de enemigos, daño, botín y el árbol de pasivas: el juego no los registra

**Tamaño**: Client.txt crece unos 0,3-3 MB por hora (sobre todo por las líneas DEBUG al cargar áreas, y más con chat de intercambio muy activo); zstd en heat.raw.parquet lo deja en aproximadamente una décima parte

## Verificado {#verified}

probado con líneas sintéticas de Client.txt en el formato del juego; sin probar contra el juego

## Fuente {#source}

[heat3d_watch/adapters/poe.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/poe.py)

<!-- Generated from the adapter by tools/gen_game_pages.py; change the adapter and run it again rather than editing this page. -->
