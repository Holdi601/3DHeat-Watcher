---
title: "Hearthstone (archivos de registro)"
nav_order: 25
lang: es
source: game-hearthstone.md
source_hash: "e79c19776947"
nav_exclude: true
search_exclude: true
---
# Hearthstone (archivos de registro) {#hearthstone-log-files}

Mientras juegas a Hearthstone, el watcher lee los archivos que escribe el juego y guarda lo que ha pasado, para que luego puedas verlo como estadísticas y como una línea de tiempo.

*Detalles técnicos: adaptador `hearthstone`, tipo [`log`](sources-and-rules.md); se ejecuta mientras `Hearthstone.exe` está en marcha y busca datos nuevos cada 0,5 s.*

## Qué se graba {#what-is-recorded}

- inicio y fin de cada partida, con el resultado (ganada, perdida, empatada), los turnos y el nombre del rival
- cada turno
- cada línea de Power.log y de los demás registros, completa, en heat.raw.parquet
- partidas, victorias, derrotas, empates, turnos, la partida más larga

## De dónde sale {#where-it-comes-from}

&lt;instalación>\Logs\Power.log (o Logs\Hearthstone_\*\Power.log), que se escribe una vez que %LOCALAPPDATA%\Blizzard\Hearthstone\log.config tiene una sección [Power], y todos los demás \*.log que el juego escribe ahí

## Cómo activarlo {#how-to-switch-it-on}

`python -m heat3d_watch setup hearthstone --apply` añade el registro [Power] a %LOCALAPPDATA%\Blizzard\Hearthstone\log.config (se guarda una copia de seguridad); reinicia el juego

Escribe el comando en una terminal abierta en la carpeta del watcher (mira [Antes de empezar](before-you-start.md)). Si falla, la última línea dice por qué; [Instalación y uso](installing-and-running.md) recoge las causas habituales.

`python -m heat3d_watch setup hearthstone` lista los archivos que cambiaría; `python -m heat3d_watch setup hearthstone --apply` los cambia, guardando el original como `<archivo>.heat3d-backup` (mira [Comandos](commands.md#setup)). Imprime `hearthstone: changed: ...` por cada cambio, o `hearthstone: nothing to change` cuando ya está activado.

## Cómo funciona {#how-it-works}

Hearthstone: el Power.log del juego, que escribe en cuanto `log.config` lo pide.

Hearthstone lee `%LOCALAPPDATA%\Blizzard\Hearthstone\log.config` al arrancar;
una sección `[Power]` con `LogLevel=1` y `FilePrinting=true` hace que escriba
todos los cambios de estado de cada partida en `<instalación>\Logs\Power.log` (las versiones nuevas
guardan los registros de cada inicio en una carpeta propia, `Logs\Hearthstone_<fecha>\`). Esta
es la depuración documentada que usan los rastreadores de mazos desde 2014
(el asistente de Hearthstone Deck Tracker escribe la misma sección). `setup()` añade la
sección, con una copia de seguridad del archivo tal como estaba; el juego necesita reiniciarse para leerla.

Las líneas que se usan, todas de `GameState.DebugPrintPower()` (las líneas `PowerTaskList`
repiten estas y se omiten):

```text
D 20:15:01.1234567 GameState.DebugPrintPower() - CREATE_GAME
D 20:15:01.1234567 GameState.DebugPrintPower() -     Player EntityID=2 PlayerID=1 GameAccountId=[hi=1 lo=2]
D 20:15:01.1234567 GameState.DebugPrintGame() - PlayerID=1, PlayerName=Name#1234
D 20:15:02.1234567 GameState.DebugPrintPower() -     FULL_ENTITY - Updating [entityName=... id=4 zone=HAND
                   zonePos=0 cardId=CS2_029 player=1] CardID=CS2_029
D 20:16:00.1234567 GameState.DebugPrintPower() - TAG_CHANGE Entity=GameEntity tag=TURN value=3
D 20:25:00.1234567 GameState.DebugPrintPower() - TAG_CHANGE Entity=Name#1234 tag=PLAYSTATE value=WON
D 20:25:00.1234567 GameState.DebugPrintPower() - TAG_CHANGE Entity=GameEntity tag=STATE value=COMPLETE
```

El lado del jugador es aquel cuyas cartas de la mano inicial tienen nombre
(las del rival están ocultas); si no, el lado que no es la IA (cuenta 0) ni
"UNKNOWN HUMAN PLAYER". Las líneas solo llevan la hora del día; la fecha es la de hoy.
Sin posiciones.

Cada línea de Power.log se guarda completa en el archivo bruto de la sesión (regla del convertidor de 3DHeat),
incluidas las repeticiones de `PowerTaskList`, las opciones, las elecciones y las actualizaciones de entidades:
`type` es el método que la escribió (`GameState.DebugPrintPower`,
`PowerTaskList.DebugPrintPower`, `GameState.DebugPrintOptions`, ...). Cualquier otro
registro que el juego escriba junto a él (`LoadingScreen.log`, `Decks.log`, `Zone.log`,
`Arena.log`, ..., cada uno presente cuando log.config lo pide; los rastreadores de mazos
suelen pedirlo) se sigue igual y se guarda con su nombre en `log`.

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

`bad_lines`, `games`, `longest_game_turns`, `losses`, `ties`, `turns`, `wins`

Una clave entre llaves se completa en tiempo de ejecución (`score.{team}` es una clave por equipo). Las claves que el código toma de una tabla de campos del juego o de sus nombres de estadística no aparecen en esta lista; "Qué se graba" más arriba las nombra.

## Completitud {#completeness}

El watcher sigue la [regla del convertidor](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md) de 3DHeat: lo que la fuente contiene se lee o se guarda, nunca se descarta. Además de las filas, cada paquete, página, línea o respuesta que recibe el adaptador se guarda completo en `heat.raw.parquet` de la sesión (columnas `time`, `ms`, `type`, `used`, `payload`, `text`, y cualquier campo guardado por nombre; `used` marca lo que también se convirtió en filas), y `selfCheck.completeness` de `meta.json` cuenta cada `type`; `lost` es 0.

**Se lee**

- `CREATE_GAME`, los jugadores (entidad, id de jugador, cuenta; la cuenta 0 es la IA) y sus nombres (`DebugPrintGame`)
- de qué lado es el del jugador, a partir de las cartas con nombre de la mano inicial
- `TAG_CHANGE` de TURN, PLAYSTATE (won, lost, tied) y STATE COMPLETE: turnos, resultado, rival

**Se guarda en bruto**

- cada línea de Power.log completa, `type` = el método que la escribió (`GameState.DebugPrintPower`, `PowerTaskList.DebugPrintPower`, `GameState.DebugPrintGame`, `GameState.DebugPrintOptions`, `GameState.SendChoices`, `GameState.DebugPrintEntityChoices`, `PowerProcessor.DoTaskListForCard`, ...), `log` `Power`, `used` cuando se convirtió en fila: cada carta jugada, robada y revelada, cada cambio de etiqueta, ataque, opción y elección está aquí, todavía sin convertir en filas
- cada línea de los demás registros de la misma carpeta (`LoadingScreen`, `Decks`, `Zone`, `Arena`, `Achievements`, `FullScreenFX`, ... lo que active log.config), con los mismos `type`, y el nombre del registro en `log`
- una línea sin el nivel ni la hora del día como `untimed`, y una sin método como `untagged`

**No disponible**

- posiciones: un juego de cartas no las tiene
- las cartas ocultas del rival: el registro solo nombra una carta cuando se revela
- los registros que log.config no activa: `setup` solo pide [Power]; los demás llegan cuando otra herramienta (un rastreador de mazos) los ha activado
- registros de ejecuciones anteriores del juego: cada ejecución escribe una carpeta nueva; las más antiguas que esta ejecución del juego no se vuelven a leer

**Tamaño**: Power.log con Verbose ocupa unos 1-5 MB por partida, 10-40 MB por hora de juego; los demás registros añaden poco; zstd en heat.raw.parquet lo deja en una décima parte o menos (las líneas se repiten mucho)

## Verificado {#verified}

probado con líneas sintéticas de Power.log en el formato del juego; sin probar contra el juego

## Fuente {#source}

[heat3d_watch/adapters/hearthstone.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/hearthstone.py)

<!-- Generated from the adapter by tools/gen_game_pages.py; change the adapter and run it again rather than editing this page. -->
