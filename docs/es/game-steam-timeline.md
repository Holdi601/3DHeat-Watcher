---
title: "Línea de tiempo de Steam (plataforma)"
nav_order: 44
lang: "es"
source: game-steam-timeline.md
source_hash: "3878efe0d7f1"
nav_exclude: true
search_exclude: true
---
# Línea de tiempo de Steam (plataforma) {#steam-timeline-platform}

El watcher guarda lo que la Línea de tiempo de Steam conserva sobre tus juegos, para que puedas mirar tu historial más tarde como estadísticas y como línea de tiempo.

*Detalles técnicos: adaptador `steam-timeline`, tipo [`platform`](sources-and-rules.md); funciona todo el tiempo (no espera a que empiece un juego) y busca datos nuevos cada 10 s.*

## Qué se graba {#what-is-recorded}

- una sesión por archivo de línea de tiempo: su inicio y su fin (session_start, session_end)
- los logros desbloqueados durante la partida, con su hora
- los cambios de modo de juego (jugando, preparación, menús, pantalla de carga)
- los eventos que los juegos añaden mediante ISteamTimeline, con título y descripción, bajo el nombre de su icono
- las fases de juego (una partida, una misión) con sus etiquetas; los eventos dentro de una llevan su id como session
- las descripciones de estado que el juego muestra en la línea de tiempo ("Ronda 3")
- los propios errores de grabación de Steam

## De dónde viene {#where-it-comes-from}

%STEAM%\userdata\\&lt;cuenta>\gamerecordings\timelines\timeline_&lt;appid>&lt;fecha>_&lt;hora>.json

## Cómo activarlo {#how-to-switch-it-on}

Steam > Ajustes > Grabación de juegos: graba en segundo plano o a demanda (entonces Steam escribe las líneas de tiempo)

## Cómo funciona {#how-it-works}

Lo que el lanzador y el controlador gráfico guardan sobre la partida: las
estadísticas, los logros, el tiempo de juego y las líneas de tiempo de Steam, y
los destacados y clips de NVIDIA.

Ninguna de estas fuentes necesita que un juego colabore ni que esté en marcha, así
que los tres adaptadores de aquí están siempre activos y miran unos pocos archivos
cada pocos segundos.

#### Línea de tiempo de Steam (`steam-timeline`) {#steam-timeline-steam-timeline}

`<Steam>\userdata\<cuenta>\gamerecordings\timelines\timeline_<appid><aaaammdd>_<hhmmss>.json`,
escrito mientras la Grabación de juegos de Steam está activada. El archivo es JSON
con números en forma de texto: "daterecorded" (segundos Unix), "starttime"/"endtime"
(ms) y "entries", cada una {"id", "time" (ms desde daterecorded), "type", ...}. Tipos
vistos en archivos reales:
```text
achievement        achievement_name - Steam añade estos para cada juego
gamemode           mode, un ETimelineGameMode: 1 jugando, 2 preparación, 3 menús,
                   4 pantalla de carga
error              description - de Steam ("#GameRecording_RecordingFailed")
event              AddInstantaneousTimelineEvent/AddRangeTimelineEvent de un juego:
                   title, description, icon, priority, duration (ms),
                   possible_clip - "Mataste a <nombre>" / "con el <arma>"
state_description  title - SetTimelineTooltip ("Ronda 3")
phase              un tramo StartGamePhase..EndGamePhase: duration (ms), tags
                   [{name, icon, group, priority}] (modo, mapa ...)
```
El formato del archivo es de Steam y no está documentado; los campos son los
parámetros de la API. Cualquier otro tipo se guarda con su propio nombre y sus campos.
<https://partner.steamgames.com/doc/api/ISteamTimeline>
<https://partner.steamgames.com/doc/features/timeline>

El mismo módulo sirve también a: [Destacados de NVIDIA (plataforma)](game-nvidia-highlights.md), [Estadísticas de Steam (plataforma)](game-steam-stats.md).

## Posiciones y ejes {#positions-and-axes}

| | |
|---|---|
| Posiciones registradas | no |
| Eje vertical | `y` |
| Unidades | metros |
| Reflejado para el visor | ninguno |
| Escala de unidades (`scale`: el visor multiplica las posiciones por ella) | 1 |

Esto va al `meta.json` de cada sesión (`axes`) y, cuando la sesión tiene posiciones, al pie de `heat.parquet`, así que el visor de 3DHeat gira y escala las filas por sí mismo: véase [Los datos](the-data.md).

## Multijugador {#multiplayer}

- Marcado como jugado en línea (`multiplayer`): **no**. `games --markdown` lo muestra como "un jugador".
- Tipo `platform`: lee solo lo que el juego o la plataforma entrega (lo que guardan Steam o el controlador gráfico), así que graba también en el juego en línea; la marca solo decide si la memoria puede leerse alguna vez.
- Memoria: **nunca** la lee este adaptador. Solo los adaptadores `memory` leen la memoria, y nunca en un juego marcado como jugado en línea: véase [Fuentes y reglas](sources-and-rules.md).

## Estadísticas registradas {#statistics-recorded}

Claves de estadística que el código de este adaptador fija por nombre (el `stats` de cada sesión en `meta.json` y la tabla `stats` de `watcher.sqlite`):

`achievements`, `game_mode_changes`, `phases`, `recorded_seconds`, `timeline_events`

Una clave entre llaves se completa en tiempo de ejecución (`score.{team}` es una clave por equipo). Las claves que el código toma de una tabla de campos del juego o de los nombres de estadísticas propios del juego no aparecen en esta lista; "Qué se graba" más arriba las nombra.

## Completitud {#completeness}

El watcher sigue la [regla de conversores](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md) de 3DHeat: lo que contiene la fuente se lee o se guarda, nunca se descarta. Además de las filas, cada paquete, página, línea o respuesta que recibe el adaptador se guarda completo en el `heat.raw.parquet` de la sesión (columnas `time`, `ms`, `type`, `used`, `payload`, `text`, y los campos que se guardan por nombre); `used` marca lo que también se convirtió en filas, y `selfCheck.completeness` de `meta.json` cuenta cada `type` - `lost` es 0.

**Leído**

- cada entrada una vez, como fila en su momento: su tipo, cada campo plano (title, description, icon, priority, duration, possible_clip, nombre del logro, mode, ...), las etiquetas de una fase agrupadas por grupo, el nombre visible del logro según el esquema de estadísticas; el inicio y el fin del archivo

**Guardado en bruto**

- cada entrada completa como JSON bajo el `type` propio de Steam (`gamemode`, `achievement`, `event`, `state_description`, `phase`, `error`, cualquier otro): los campos anidados - el icono y la prioridad de una etiqueta, y lo que añada después Steam - solo están aquí
- `timeline`: los campos propios del archivo (daterecorded, starttime, endtime, cualquier otro), cuando se abre la sesión y de nuevo cuando cambian

**No disponible**

- la grabación en sí (el vídeo): Steam la guarda en sus propias carpetas; la sesión se refiere al archivo de línea de tiempo por su nombre
- una lectura de un archivo que Steam está escribiendo y que no se puede analizar ni cuando se cierra su final: se cuenta (`bad` en el estado del adaptador) y se vuelve a leer en el siguiente cambio, donde se toman sus entradas

**Tamaño**: unos cientos de entradas de 100 a 300 bytes por hora de juego: muy por debajo de 1 MB por hora

## Verificación {#verified}

probado con archivos de línea de tiempo reales de una instalación local: entradas de logro, modo de juego, error, y los eventos, descripciones de estado y fases propios de los juegos; el formato del archivo no está documentado

## Fuente {#source}

[heat3d_watch/adapters/platform.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/platform.py)

<!-- Generated from the adapter by tools/gen_game_pages.py; change the adapter and run it again rather than editing this page. -->
