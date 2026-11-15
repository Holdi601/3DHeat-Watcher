---
title: NVIDIA Highlights
nav_order: 8
lang: "es"
source: nvidia-highlights.md
source_hash: "a3b769ab065c"
nav_exclude: true
search_exclude: true
---
# NVIDIA Highlights {#nvidia-highlights}

Algunos juegos piden al controlador gráfico NVIDIA que guarde un clip corto cuando ocurre algo, como una baja.
El watcher anota cada uno de esos momentos y, cuando puede, lo sitúa en el mapa donde ocurrió.

El adaptador `nvidia-highlights` registra los clips, los highlights y las capturas que guarda NVIDIA App (o
GeForce Experience), y da a cada uno un lugar en el mapa cuando puede. Esta página explica qué puede y qué no puede
ofrecer NVIDIA Highlights, qué archivos lee el watcher y cómo un highlight
obtiene una posición. La página generada del adaptador es [NVIDIA highlights (plataforma)](game-nvidia-highlights.md).

## Lo que NVIDIA Highlights puede y no puede ofrecer {#what-nvidia-highlights-can-and-cannot-deliver}

Un juego compatible con NVIDIA Highlights habla con NVIDIA App a través de GfeSDK de NVIDIA. El SDK
solo transporta dos tipos de mensaje:

1. **Una vez, al inicio**: los tipos de highlight que usará el juego - un id (como `kill`), una importancia, etiquetas y un
   nombre para mostrar en cada idioma. NVIDIA App los guarda por juego.
2. **En un momento de juego**: "highlight `<id>`, desde `<ms>` antes de ahora hasta `<ms>` después". Ese es
   todo el mensaje: el id de un tipo que el juego registró, y dos desplazamientos de tiempo que indican a
   NVIDIA App qué tramo de su grabación continua conservar.

El SDK **no tiene ningún campo para nada más**: ni posición, ni partida o ronda, ni rival, ni arma, ni
marcador, ni datos personalizados de ningún tipo. Un juego no puede poner una posición en un highlight aunque quisiera.
Cuando se guarda el clip, NVIDIA App añade un archivo, un nombre de juego, una duración y una hora.

Así que un highlight solo puede decir "este tipo de momento, en este juego, a esta hora". Todo lo demás
tiene que venir de otra parte.

## Lo que lee el watcher {#what-the-watcher-reads}

Todo se lee de archivos que NVIDIA App escribe para su propia galería. Nada habla con el controlador
ni con la aplicación. La carpeta de NVIDIA Overlay es
`%LOCALAPPDATA%\NVIDIA Corporation\NVIDIA Overlay`.

| Archivo | Lo que se toma de él |
|---|---|
| `UGCTracker.json` | el índice de la galería: cada clip y captura con su ruta, tipo (vídeo, imagen), subtipo (`InstantReplay`, ...), fecha, el nombre de perfil del juego, el ejecutable y su nombre corto, y la duración (`msDuration`) |
| `GallerySettings.json` | `settings.currentDirectoryV2`, la carpeta de captura, y `settings.tempDirectory`, donde esperan los highlights (`<temp>\Highlights\<game>`) hasta que se guardan |
| `Highlights\<game>\config.json` | los tipos de highlight que registró cada juego: id, y el nombre para mostrar en inglés (o el id si el juego no dio ninguno) |
| la carpeta de captura (por defecto `%USERPROFILE%\Videos\NVIDIA`) y `<temp>\Highlights` | los propios archivos de clip y captura (`.mp4`, `.mkv`, `.mov`, `.png`, `.jpg`, `.jpeg`), una carpeta por juego |
| `%LOCALAPPDATA%\NVIDIA Corporation\GfeSDK\<exe>_<pid>.log` | las peticiones que registran los juegos con GfeSDK - líneas `Posted Request HL...` - así que un highlight que pidió el juego queda registrado aunque no se guardara ningún clip. Las peticiones de configuración (`HLConfigure`, `HLGetConfig`, `HLGetUserSettings`, `HLSetDefaultLocale`) se omiten. |

Por cada elemento nuevo, el adaptador escribe una fila: `highlight` para un vídeo, `screenshot` para una imagen, o
`highlight_request` para una línea del registro de GfeSDK. Sus campos:

| Campo | Qué es |
|---|---|
| `ms` | el momento: la hora del nombre de archivo (`<Game> 2026.05.01 - 20.31.28.115.DVR.mp4`, la hora local en que se guardó el clip), si no la fecha del índice, si no la fecha de modificación del archivo |
| `game` | el nombre de perfil de NVIDIA, el nombre de la carpeta o el juego del nombre del archivo |
| `clip`, `media` | la ruta del archivo; `video`, `image` o `file` |
| `kind` | `InstantReplay`, `Screenshot`, `Highlight` (de la carpeta temporal de highlights) o el subtipo del índice |
| `duration_s`, `clip_start_ms` | la duración, del índice o de la propia cabecera del vídeo (`moov/mvhd`, encontrada sin leer el vídeo); el momento en que empieza el clip |
| `highlight_id`, `highlight_name` | el tipo de highlight, cuando algo lo nombra (véase abajo) |
| `exe` | el ejecutable del juego, del índice |
| `x`, `y`, `z`, `session`, `position_from`, `position_lag_ms` | la posición prestada, cuando se encontró una (véase abajo) |

Las estadísticas de la sesión son `clips`, `screenshots`, `clip_seconds` y `placed` (elementos que
obtuvieron una posición).

**El id del highlight** no está escrito en ningún lugar documentado. El adaptador prueba dos
no documentados: un campo de la entrada de la galería cuyo nombre contiene "highlight", y - solo para archivos de la
carpeta temporal de highlights - uno de los ids registrados por el juego (de al menos 4 caracteres) que
aparezca en el nombre del archivo. Un clip guardado lleva el nombre del juego, que podría contener un id como "kill"
por casualidad, así que su nombre no se busca. Estas dos vías no se han visto funcionar en una máquina real
todavía: no ha aparecido ningún clip con id de highlight, ni ninguna línea de petición de GfeSDK, en las
pruebas del adaptador. El índice de la galería, la configuración, las definiciones de highlight y los clips se probaron con archivos reales.

### Cuándo se registran los elementos {#when-items-are-recorded}

- Un clip sigue escribiéndose un rato después de la pulsación de tecla. El adaptador espera a que un archivo tenga el
  mismo tamaño y la misma hora en dos comprobaciones (cada 10 s) y tenga al menos 5 s de antigüedad.
- La primera vez que se ejecuta el adaptador, todo lo que ya está en la galería y en los registros solo se anota, no se registra,
  para que años de clips antiguos no inunden las estadísticas. Lo que ha visto se guarda en
  `<data>\state\nvidia-highlights.json`, así que un reinicio no registra nada dos veces.
- Los elementos se agrupan en una sesión por juego. La sesión de un juego se cierra tras 30 minutos sin un elemento nuevo, y termina
  en su último momento y no cuando se cerró el juego. Los momentos separados más de 30 minutos van a
  sesiones distintas.

## Cómo obtiene un highlight una posición {#how-a-highlight-gets-a-position}

El highlight en sí no tiene lugar. El adaptador busca el momento en las otras grabaciones que hizo el
watcher del mismo juego en el mismo instante:

1. **El mismo juego**: las carpetas de sesión bajo `<data>\sessions\` cuyo nombre de juego coincide con el del
   highlight. Los nombres se comparan en minúsculas, solo con letras y dígitos. Coinciden cuando son
   iguales, o cuando el más corto tiene al menos 5 caracteres y está contenido en el más largo
   (`Counter-Strike 2` y `Counter-Strike-2`).
2. **La misma hora**: las sesiones cuyo inicio y fin (de `meta.json`, con un segundo de margen en
   ambos extremos) cubren el momento. Se omiten las sesiones que terminaron sin posiciones, y las propias
   sesiones del adaptador.
3. **La fila propia del jugador**: en su `events.jsonl`, la más reciente de las filas propias del jugador con
   posición, en el momento o antes, y no más de 5 segundos antes. Una fila es propia del jugador
   cuando su fuente lo indica: `"player": "me"`, o `"own_car": 1` (juegos de carreras que registran cada coche
   por su piloto), o un `player` que es el `player` de la sesión en `meta.json` (el nombre que da la
   fuente al jugador). Véase [Las filas propias del jugador](the-data.md#the-players-own-rows).

Si se encuentra una fila, el highlight recibe sus `x`, `y`, `z`, su `session` (o el nombre de la
carpeta), `position_from` (la carpeta de donde vino) y `position_lag_ms` (cuánto antes del momento estaba
esa fila). La sesión del highlight toma los ejes de esa grabación, así que se dibuja igual. Si no se encuentra
ninguna fila, el highlight se queda como un momento en la línea de tiempo, sin lugar.

Cosas que hay que saber sobre la posición prestada:

- **Es donde estabas cuando se guardó el clip**, no donde empezó la acción. El momento es la hora de guardado del nombre de archivo, que en una Repetición instantánea es su final. `clip_start_ms` indica cuándo empieza el clip.
- **Otro adaptador tiene que haber estado grabando el mismo juego en ese momento.** Los que marcan las filas propias del jugador, y así pueden situar un highlight: la game-state integration de Counter-Strike 2 y Dota 2, Forza, los juegos de Assetto Corsa, EA SPORTS WRC, DiRT Rally 2.0, Richard Burns Rally, BeamNG.drive, Euro Truck Simulator 2, American Truck Simulator, DCS World, X-Plane, Microsoft Flight Simulator, War Thunder, Minecraft y los perfiles de memoria (como `me`); F1 23/24/25, RaceRoom, Automobilista 2 y Project CARS 2 (las filas de tu coche llevan `own_car` 1, según el índice de coche del jugador del juego, su propia ranura o el participante visto); Elite Dangerous (el nombre del comandante, en `meta.json` como `player`, ya que el diario siempre es del jugador).
- **Una repetición se convierte después de la partida**, así que solo puede situar un clip que se busque después de la conversión: el clip se sitúa cuando se graba, y una repetición guardada más tarde no se vuelve a mirar. Las repeticiones de League of Legends etiquetan sus filas con el Riot ID de los ajustes y, con una clave de la API de Riot, les dan la hora de reloj que indica la línea de tiempo de la partida, así que se encuentran entonces. Una demo de CS2 no puede situar un highlight en absoluto: sus posiciones están en la tabla propia del conversor, no en `events.jsonl`, y una demo tiene los ticks del juego pero no una hora de reloj con la que comparar el momento de un clip.
- En Rocket League las únicas filas con lugar son los eventos del balón. Un golpe tuyo al balón es una fila tuya, así que un highlight puede situarse donde tocaste el balón por última vez.
- Los juegos sin ninguna fuente posicional (Overwatch 2, Call of Duty, Hunt: Showdown, ...) guardan sus highlights como una línea de tiempo de momentos.

## Por qué la memoria no puede dar una posición en multijugador {#why-memory-cannot-give-a-position-in-multiplayer}

La otra forma de obtener una posición sería leerla de la memoria. Ninguna de las dos memorias funciona:

- **La memoria de NVIDIA no tiene posición.** NVIDIA App recibe lo que transporta GfeSDK - un id de highlight y dos desplazamientos de tiempo - más el vídeo que graba. No hay posición en ningún lugar del lado de NVIDIA que leer. (El watcher no lee la memoria de NVIDIA de todos modos; lee los archivos de arriba.)
- **La memoria del juego está fuera de alcance en multijugador.** La posición está en el proceso del juego, pero el watcher nunca lee la memoria de un juego multijugador: un adaptador de memoria para un juego marcado como jugado en línea se rechaza antes de abrir nada (véase [Lectura de memoria](memory-reading.md)). Los juegos multijugador se ejecutan bajo anti-trampas (Easy Anti-Cheat, BattlEye, Vanguard, ...) que consideran trampa que otro programa abra el proceso del juego, lo que puede llevar a suspender la cuenta. Además, leer el estado del juego desde fuera es algo que prohíben las condiciones de los juegos. Un highlight en un juego multijugador, por tanto, solo obtiene un lugar a partir de lo que publica el juego: su game-state integration o su telemetría, grabada por otro adaptador en el mismo momento.
