---
title: "League of Legends (estado de la partida)"
nav_order: 29
lang: "es"
source: game-lol-live.md
source_hash: "75c67c6fe84f"
nav_exclude: true
search_exclude: true
---
# League of Legends (estado de la partida) {#league-of-legends-game-state}

Mientras juegas a League of Legends, el watcher guarda lo que el juego informa a los programas de tu propio ordenador, para que luego puedas verlo como estadísticas y como una línea de tiempo.

*Detalles técnicos: adaptador `lol-live`, tipo [`gsi`](sources-and-rules.md); se ejecuta mientras `League of Legends.exe` está en marcha y busca datos nuevos cada 0,5 s.*

## Qué se graba {#what-is-recorded}

- sin posiciones: la API no las tiene
- registro de muertes: muertes y asistencias del jugador, y las muertes de otros campeones con quién mató, a quién y quién asistió
- dragones, heraldos, barones, torres, inhibidores, multimuertes, ases, primera sangre, inicio y fin de partida
- muertes propias, asistencias, puntuación de creeps, puntuación de vigilancia, nivel, oro, campeón, tiempo de partida, resultado
- objetivos conseguidos por el equipo del jugador

## De dónde sale {#where-it-comes-from}

API de datos del cliente en vivo del juego, <https://127.0.0.1:2999/liveclientdata/> (allgamedata, eventdata), durante una partida

## Cómo activarlo {#how-to-switch-it-on}

No hace falta activar nada: el watcher lee la fuente tal como la entrega el juego o la plataforma.

## Cómo funciona {#how-it-works}

League of Legends: la API de datos en vivo que el cliente del juego sirve durante una partida.

Mientras se juega una partida (también en el modo práctica y en el modo espectador), `League of
Legends.exe` responde en <https://127.0.0.1:2999> con lo que el jugador puede ver en la
propia interfaz del juego:

```text
/liveclientdata/allgamedata          activePlayer (riotId, level, currentGold, championStats),
                                     allPlayers (championName, team ORDER/CHAOS, level,
                                     scores: kills, deaths, assists, creepScore, wardScore),
                                     events, gameData (gameMode, gameTime s, mapName)
/liveclientdata/eventdata?eventID=N  {"Events": [...]} desde EventID N en adelante: GameStart,
                                     MinionsSpawning, FirstBlood, FirstBrick, TurretKilled,
                                     InhibKilled, InhibRespawningSoon, InhibRespawned,
                                     DragonKill, HeraldKill, BaronKill, ChampionKill
                                     (KillerName, VictimName, Assisters), Multikill
                                     (KillStreak), Ace (Acer, AcingTeam), GameEnd (Result)
```

No hay posiciones: la API no las tiene, así que una sesión de League son eventos y
estadísticas, sin tabla de calor. El certificado es autofirmado, de la propia
raíz de Riot (`riotgames.pem`, publicado en
<https://static.developer.riotgames.com/docs/lol/riotgames.pem>). Sus condiciones
de uso no están indicadas, así que no se incluye: colócalo en `<datos>\riotgames.pem` y
la conexión se verifica con él; sin él, la verificación está desactivada, y solo
para 127.0.0.1, la única dirección a la que habla este adaptador.

La política de Riot permite a las herramientas mostrar lo que el jugador podría saber
por el propio juego, y nada calculado más allá de eso (sin temporizadores de enemigos): esto graba el
registro de muertes y el marcador que ve el jugador, y sus propios números.

Cada respuesta también se guarda completa (regla del convertidor de 3DHeat, docs/converters.md en
el repositorio del visor): `heat.raw.parquet`, `type` el endpoint
("allgamedata", "eventdata"), `text` el JSON tal como lo envió el cliente, `status`
cuando no fue 200. Una respuesta byte a byte igual a la anterior de su endpoint (la lista de
eventos mientras no pasa nada) se guarda una vez y se cuenta en `unchanged_replies` de meta.json.
allgamedata contiene todo lo que sirven los demás endpoints (activeplayer\*, playerlist, playerscores,
playeritems, playersummonerspells, playermainrunes, gamestats), así que no se les pregunta por separado.
Las respuestas antes de una partida (la pantalla de carga) esperan en una cola
y pasan a la sesión de la partida; después de GameEnd la sesión queda abierta hasta que se cierra
el cliente, así que las respuestas de la pantalla final se guardan con ella.

Fuente: <https://developer.riotgames.com/docs/lol#game-client-api>

## Posiciones y ejes {#positions-and-axes}

| | |
|---|---|
| Posiciones grabadas | no |
| Eje hacia arriba | `z` |
| Unidades | ninguna (sin posiciones) |
| Reflejado para el visor | ninguno |
| Escala de unidades (`scale`: el visor multiplica las posiciones por ella) | 1 |

Esto va a `meta.json` (`axes`) de cada sesión y, cuando la sesión tiene posiciones, al pie de `heat.parquet`, así que el visor de 3DHeat gira y escala las filas por sí mismo; mira [Los datos](the-data.md).

## Multijugador {#multiplayer}

- Marcado como jugado en línea (`multiplayer`): **sí**. `games --markdown` lo muestra como "permitido (solo lee lo que publica el juego)".
- Tipo `gsi`: solo lee lo que el juego o la plataforma entregan (una integración de estado de juego o una API local que sirve el juego), así que graba también en línea, igual que sin conexión; la marca solo decide si se puede leer la memoria.
- Memoria: este adaptador **nunca** la lee. Solo los adaptadores `memory` leen memoria, y nunca en un juego marcado como jugado en línea; mira [Fuentes y reglas](sources-and-rules.md).

## Estadísticas que se graban {#statistics-recorded}

Claves de estadística que el código de este adaptador asigna por nombre (el `stats` de cada sesión en `meta.json` y la tabla `stats` de `watcher.sqlite`):

`bad_packets`, `champion`, `game_time`, `gold`, `level`, `result`

Una clave entre llaves se completa en tiempo de ejecución (`score.{team}` es una clave por equipo). Las claves que el código toma de una tabla de campos del juego o de sus nombres de estadística no aparecen en esta lista; "Qué se graba" más arriba las nombra.

## Completitud {#completeness}

El watcher sigue la [regla del convertidor](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md) de 3DHeat: lo que la fuente contiene se lee o se guarda, nunca se descarta. Además de las filas, cada paquete, página, línea o respuesta que recibe el adaptador se guarda completo en `heat.raw.parquet` de la sesión (columnas `time`, `ms`, `type`, `used`, `payload`, `text`, y cualquier campo guardado por nombre; `used` marca lo que también se convirtió en filas), y `selfCheck.completeness` de `meta.json` cuenta cada `type`; `lost` es 0.

**Se lee**

- el registro de muertes de eventdata: cada evento una vez, con sus campos con nombre decodificados (quien mata, la víctima y los asistentes con campeón y equipo, estructuras y su bando, tipo de dragón, robos, multimuertes, ases, primera sangre, el resultado) y cada otro campo de un evento en su fila, con su propio nombre
- de allgamedata: las muertes propias, asistencias, puntuación de creeps, puntuación de vigilancia, nivel, oro, campeón, el tiempo de partida, el modo y el mapa de juego

**Se guarda en bruto**

- `allgamedata`: cada respuesta completa (`text`), cada 2 s: activePlayer (habilidades, cada estadística del campeón, runas completas, oro, nivel), allPlayers (objetos con ranuras y precios, runas, hechizos de invocador, puntuaciones, nivel, muerto y temporizador de reaparición, aspecto, calle, bot), los eventos, gameData (modo, tiempo, mapa, terreno); `used` verdadero mientras la partida está en curso, falso en la pantalla final
- `eventdata`: cada respuesta completa, pedida cada 0,5 s desde el siguiente id de evento; `used` verdadero cuando trajo eventos nuevos
- una respuesta byte a byte igual a la anterior de su endpoint se guarda una vez y se cuenta (`unchanged_replies` en meta.json); las respuestas de error (el RESOURCE_NOT_FOUND de la pantalla de carga) se guardan con su `status`, antes del inicio de la partida

**No disponible**

- posiciones: la API no tiene (ni minimapa, ni coordenadas)
- los demás endpoints (activeplayer, activeplayername, activeplayerabilities, activeplayerrunes, playerlist, playerscores, playersummonerspells, playermainrunes, playeritems, gamestats): cada uno sirve una parte de allgamedata, así que no se les pregunta
- la API de repeticiones (`/replay/*` en el mismo puerto): reproduce repeticiones y partidas vistas como espectador una vez activada en game.cfg; no forma parte de una partida jugada
- los endpoints del archivo de bloqueo del cliente de League: no es una API publicada (Fuentes y reglas)
- valores entre dos lecturas: la API responde cuando se le pide y no envía nada por su cuenta; el marcador se pide cada 2 s, los eventos cada 0,5 s

**Tamaño**: allgamedata ocupa 15-40 KB (incluye la lista completa de eventos, que crece) cada 2 s: unos 30-70 MB por hora en `raw.bin`; eventdata añade poco, porque las respuestas iguales se cuentan, no se guardan; zstd reduce el JSON repetido en `heat.raw.parquet` a unos pocos MB por hora (estimado a partir del formato documentado)

## Verificado {#verified}

probado con un servidor local falso que sirve respuestas en el formato documentado; sin probar contra el juego

## Fuente {#source}

[heat3d_watch/adapters/lol.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/lol.py)

<!-- Generated from the adapter by tools/gen_game_pages.py; change the adapter and run it again rather than editing this page. -->
