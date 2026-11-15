---
title: Desarrollo
nav_order: 12
lang: "es"
source: development.md
source_hash: "cb213e22ddea"
nav_exclude: true
search_exclude: true
---
# Desarrollo {#development}

Esta página es para añadir un juego: cómo se construye un adaptador, cómo se prueba y cómo se genera su
documentación.

## El repositorio {#the-repository}

| Ruta | Qué contiene |
|---|---|
| `heat3d_watch/cli.py` | los comandos ([Comandos](commands.md)) |
| `heat3d_watch/watcher.py` | el bucle en segundo plano: lista de procesos, un hilo por adaptador, actualizaciones |
| `heat3d_watch/session.py` | una grabación: `events.jsonl`, `heat.parquet`, `meta.json`, recuperación |
| `heat3d_watch/db.py` | `watcher.sqlite` |
| `heat3d_watch/config.py` | los ajustes y la carpeta de datos |
| `heat3d_watch/safety.py`, `heat3d_watch/memory.py` | las comprobaciones de memoria y el lector de solo lectura ([Lectura de memoria](memory-reading.md)) |
| `heat3d_watch/notify.py` | notificaciones de Windows |
| `heat3d_watch/adapters/` | un módulo por juego o familia de juegos; los módulos que empiezan por `_` son ayudas compartidas |
| `heat3d_watch/decoders/` | los decodificadores de telemetría de carreras, copiados de los grabadores de vueltas de 3DHeat GameCapture |
| `heat3d_update/` | el actualizador ([Actualizaciones](updates.md)) |
| `mods/beamng/heat3d/` | el mod de protocolo de BeamNG que instala `setup beamng` |
| `tests/` | las pruebas |
| `tools/gen_game_pages.py` | escribe las páginas de juegos de esta documentación |

## Un adaptador {#an-adapter}

Un adaptador es una dataclass derivada de `heat3d_watch.adapters.base.Adapter`. Sus campos dicen qué es; sus
métodos hacen el trabajo.

| Campo | Por defecto | Qué es |
|---|---|---|
| `id` | `""` | corto y estable: las carpetas de sesión, `disabled`, `replay_folders` y `player_names` se refieren a él |
| `game` | `""` | el nombre del juego como lo escribe la gente; las sesiones se archivan bajo él |
| `kind` | `"telemetry"` | uno de `telemetry`, `gsi`, `log`, `replay`, `platform`, `memory` ([Fuentes y reglas](sources-and-rules.md)) |
| `exes` | `()` | nombres de ejecutable (sin distinguir mayúsculas) que indican que el juego está en marcha. Vacío: el adaptador siempre está activo (`always` es verdadero) |
| `multiplayer` | `True` | el juego se juega en línea: su memoria nunca se lee |
| `source` | `""` | de dónde vienen los números, dicho una vez |
| `records` | `()` | qué se graba, un elemento por tipo de cosa |
| `enable` | `""` | cómo activar la fuente; vacío si no hace falta nada |
| `interval` | `0.1` | segundos entre consultas |
| `axes` | `Axes()` | el eje vertical del mundo, los ejes reflejados, la escala de unidades del visor (dejar en 1) y una nota sobre las unidades |
| `verified` | `""` | lo que se ha comprobado, con honestidad (véase abajo) |
| `completeness` | `{}` | el detalle de la fuente según la [regla de conversores](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md) de 3DHeat: `read` (lo que se convierte en filas), `raw` (lo que se guarda entero, bajo qué `type`), `missing` (lo que la fuente no da, y por qué), `size` (cuánto ocupa el flujo bruto por hora). La sección "Completeness" de la página del juego se escribe a partir de él |

`source`, `records`, `enable`, `verified` y `completeness` son documentación, no adorno. `games` los muestra,
`games --markdown` genera la tabla de [Todos los juegos en una tabla](watcher.md), y las páginas de cada juego
se generan a partir de ellos. Escríbelos de forma que digan exactamente lo que hace el código.

Los métodos, todos opcionales:

| Método | Se llama | Qué debe hacer |
|---|---|---|
| `missing(self) -> str \| None` | por `games`, `status` y antes de arrancar | decir por qué el adaptador no puede ejecutarse aquí (no se encuentra una DLL, falta una carpeta), o `None` |
| `setup(self, ctx, *, apply) -> list[str]` | por `setup` | activar la salida propia del juego; devolver una línea por cambio, y cambiar archivos solo cuando `apply` es verdadero. Guarda una copia de seguridad del archivo como `<file>.heat3d-backup` antes de su primer cambio, y nunca sobrescribas esa copia. Sobrescribe el método solo cuando haya algo que activar: `can_setup` (verdadero cuando `setup` está sobrescrito) decide si `setup` lo ejecuta o indica que no hay nada que cambiar; una clase que sirve a varios juegos sobrescribe `can_setup` para los que no puede configurar (`RallyAdapter` para Richard Burns Rally). |
| `start(self, ctx)` | cuando aparece el proceso del juego (adaptadores siempre activos: cuando arranca `run`) | abrir sockets, buscar archivos, recordar desde dónde empezar |
| `poll(self, ctx)` | cada `interval` segundos, en el hilo propio del adaptador | recoger lo que dijo el juego desde la última consulta y grabarlo |
| `stop(self, ctx)` | cuando el juego ya no está o el watcher se detiene | cerrar sesiones y sockets |

Cada adaptador se ejecuta en su propio hilo (`Runner`). Una excepción en `poll` se registra y el adaptador
espera `min(5, interval × 10 + 0.5)` segundos antes de la siguiente consulta. Tras 20 fallos seguidos, o un
fallo en `start`, el adaptador se detiene y no vuelve a arrancar hasta que cambie el id del proceso del juego.
`missing()` se comprueba en cada revisión, así que debe ser barato.

Un objeto adaptador se reutiliza cuando su juego vuelve a arrancar, así que `start` debe reiniciar todo lo que
dejó una ejecución anterior.

### Registrarlo {#registering-it}

Pon el módulo en `heat3d_watch/adapters/` y enumera los adaptadores al final:

```python
ADAPTERS = [MyAdapter(id="mygame", game="My Game", ...)]
```

`adapters.load()` importa cada módulo del paquete (salvo `base` y los nombres que empiezan por `_`) y reúne sus
`ADAPTERS`. Dos adaptadores con el mismo id detienen la carga con un `ValueError`. Un módulo que no se puede
importar (una dependencia que falta) deja fuera a sus juegos y `games` lo indica con el error, así que un
problema de un juego no detiene a los demás.

## Contexto y sesión {#context-and-session}

`start`, `poll`, `stop` y `setup` reciben un `Context`:

| Miembro | Qué es |
|---|---|
| `settings` | los `Settings` ([Instalación y ejecución](installing-and-running.md#settings)) |
| `data` | la carpeta de datos |
| `pid`, `exe` | el id del proceso del juego y la ruta de su ejecutable, cuando el adaptador se arrancó para un juego en marcha; la carpeta de instalación está junto a `exe` |
| `open(adapter, *, game=None, when=None, axes=..., source=..., multiplayer=..., meta=..., geo=None)` | una `Session` nueva. `game` sustituye el nombre del juego del adaptador (para adaptadores que cubren muchos juegos); `when` fija el inicio para sesiones que describen el pasado; `axes`, `source` y `multiplayer` toman por defecto los del adaptador; `meta` es un diccionario que se escribe en `meta.json`; `geo` (`{"lat0": .., "lon0": ..}`, o fijar `session.geo` más tarde) coloca una sesión de mapa plano sobre la Tierra, en `meta.json` y en el pie de la tabla |
| `close(session)` | termina una sesión: la tabla, `heat.raw.parquet`, `meta.json` y su línea en `watcher.sqlite`. Una sesión sin eventos ni elementos brutos se borra; una con solo elementos brutos se conserva (sin tabla, sin línea en la base de datos). Acepta `None`. Devuelve la ruta de la tabla o `None`. |

Una `Session` registra:

| Miembro | Qué hace |
|---|---|
| `event(name, *, t=None, ms=None, x=None, y=None, z=None, player=None, team=None, session=None, **attrs)` | una fila. `t` por defecto son los segundos desde el inicio de la sesión, `ms` por defecto el momento actual. Una posición cuenta solo cuando `x`, `y` y `z` están todos dados y son finitos. Los atributos `None` se omiten. |
| `position(x, y, z, **kw)` | un evento llamado `position` |
| `raw(type, payload=None, *, text=None, used=False, t=None, ms=None, **fields)` | guarda entero algo que envió la fuente: los bytes de un paquete o página (`payload`), una línea o una respuesta JSON tal como llegó (`text`), o los valores de una lectura por nombre (`fields`, cada uno en su propia columna). `type` es la palabra de la fuente para ello (un id de paquete, el nombre de una asignación, un evento del diario, un endpoint); `used` indica que también se convirtió en filas. Se encuadra en `raw.bin` en el momento de la llamada, se escribe como `heat.raw.parquet` (zstd) al cerrar o recuperar la sesión, y se cuenta por `type` en `selfCheck.completeness` de `meta.json` |
| `stat(key, value, how="set")` | una estadística: `set` la fija, `add` le suma, guarda el `max` o el `min` |
| `now()` | segundos desde el inicio de la sesión |
| `meta` | un diccionario que se escribe en `meta.json` |
| `started`, `ended`, `folder`, `id`, `counts`, `positions` | cuándo, dónde, y qué se ha grabado hasta ahora |

`event`, `stat` y `raw` son seguros entre hilos y se pueden llamar desde un hilo de trabajo.

**Cada adaptador guarda todo lo que envía su fuente.** Las filas son lo que dibuja el visor; no son el registro.
Cada paquete que llega a un puerto, cada página de memoria compartida leída (la página entera, cada vez que
cambia), cada línea de un registro o de un script de exportación (también las que el adaptador ignora), cada
respuesta JSON o documento enviado va a `session.raw(...)` a medida que llega, tenga o no una fila, y nada se
reduce por debajo de la frecuencia a la que lee el adaptador. Un elemento que llega antes de que se abra una
sesión abre una (una sesión con solo elementos brutos se conserva), o se retiene hasta que se abre una; nunca se
descarta. Los campos que son baratos de decodificar y seguros en su significado también van a las filas. Esta
es la [regla de conversores](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md) de 3DHeat: un
flujo en vivo se pierde en cuanto se envía, así que lo que un adaptador no guarda se pierde para siempre, y lo
que guarda entero puede decodificarse el día que alguien lo entienda. El tamaño es el precio; zstd y la
codificación por diccionario lo mantienen bajo, sin dejar cosas fuera. La prueba de cada adaptador envía algo
que no usa y comprueba que vuelve entero desde `heat.raw.parquet`, y que `selfCheck.completeness.lost` es 0.
`racing.Driving.raw` hace lo mismo para los adaptadores de carreras (y abre la sesión), y `racing.Pages` guarda
las páginas de memoria compartida siempre que cambian sus bytes, contando en `unchanged_reads` de `meta.json`
las relecturas que no encontraron nada nuevo.

Convenciones de las que depende el resto del sistema:

- **Las filas propias del jugador se marcan según lo que diga la fuente.** `player="me"` cuando la fuente es la
  del propio jugador; cuando cada jugador se graba con un nombre, `own_car=1` en las filas del coche del jugador
  (por el índice de jugador del juego o el participante visto), o el nombre del jugador como
  `session.meta["player"]` (escrito en `meta.json` de inmediato) cuando la fuente nombra al jugador. Nunca
  adivines: si la fuente no lo dice, toma el nombre de un ajuste (`player_names`, `riot_id`) o no marques nada.
  [Destacados de NVIDIA](nvidia-highlights.md) toma posiciones solo de esas filas (`platform.own_row`). Los demás
  jugadores se identifican por su nombre o id.
- **Las rutas están delimitadas por eventos con posición**: `spawn`, `respawn` y `session_start` inician una;
  `death`, `finish`, `session_end` y `teleport` la terminan. Siempre que el jugador se mueva sin viajar (un
  reinicio, un rebobinado, un viaje rápido, una partida cargada), escribe `teleport` en el lugar que dejó y luego
  un inicio (`spawn`, o `respawn` para un reinicio que el juego nombra) en el lugar al que llegó, de modo que el
  mapa de calor de líneas del visor termine una ruta y empiece la siguiente en lugar de dibujar una línea a través
  del mapa. `Driving.jumped` lo hace para los vehículos.
- **Las posiciones se mantienen en las coordenadas y unidades propias del mundo del juego**, descritas por
  `axes`. No las conviertas a otro marco salvo que el juego no dé un marco mundial utilizable (los simuladores de
  vuelo colocan latitud y longitud en un mapa plano, `Tangent`, alrededor del primer punto fijo —DCS alrededor del
  origen fijo de su teatro— y pasan `geo=tangent.geo()` a `open`, de modo que el pie indica dónde está el mapa en
  la Tierra). `axes.scale` es la escala de unidades del visor —multiplica cada posición por ella— y se mantiene en
  1, para que las filas coincidan con un nivel exportado del mismo juego en las mismas unidades; indica la unidad
  en `axes.units`.
- **Las claves de estadística** van en minúsculas con guiones bajos, y llevan su unidad cuando la hay
  (`distance_km`, `top_speed_kmh`, `max_altitude_m`, `duration_s`). Un tiempo guardado como mejor empieza por
  `best_` (se guarda con `min`), y un puesto termina en `_position`: `stats` muestra el menor de estos como mejor,
  y el mayor de cualquier otra clave (`db.lower_is_better`).

## Ayudas {#helpers}

| Ayuda | Módulo | Para |
|---|---|---|
| `Follower(find, since, stamp=None)`, `game_started(pid)`, `newest(paths)`, `read_shared(path)`, `steam_libraries()` | `_logfollow` | seguir un registro que escribe el juego: lecturas compartidas, solo las líneas de esta sesión, archivos nuevos y reemplazados, solo líneas completas |
| `UdpPort(port, forward=None, grace=0.0, recheck=3.0)` con `try_open(who)`, `receive()`, `close()` | `racing` | un puerto de telemetría UDP en 127.0.0.1, tomado solo cuando está libre, cedido a otro programa, opcionalmente retransmitido |
| `Driving(adapter, ctx, hz=10.0, jump=50.0)` con `sample(...)`, `event(...)`, `lap(...)`, `count(...)`, `close()` | `racing` | sesiones de vehículos: posiciones a una frecuencia fija, distancia, velocidad máxima, vueltas; en un salto, `teleport` donde estaba el coche y `spawn` donde está (`jumped(...)`) |
| `SharedView.open(name)` | `simracing_shm` | la memoria compartida con nombre de un juego, de solo lectura, nunca se crea |
| `ReplayAdapter` (`patterns`, `folders(ctx)`, `convert(path, ctx)`) | `replays` | una carpeta de repeticiones vigilada: los archivos se convierten cuando dejan de crecer, en un hilo de trabajo; la primera mirada solo anota lo que hay, y `convert_existing(ctx, folder=None)` —el comando [`replays`](commands.md#replays)— convierte esos bajo petición |
| `load_state`, `save_state` | `platform` | recordar lo que ha visto un adaptador siempre activo, en `<data>\state\<id>.json` |
| `FlightLog`, `Tangent` | `xplane` | registro de vuelos (despegues, aterrizajes, accidentes, distancia) y el mapa plano alrededor del primer punto fijo (`Tangent.geo()` es el `geo` de la sesión) |
| `backup_once(path)` | `gsi`, `racing` | la regla de `<file>.heat3d-backup` |
| Archivos de Steam | `_steam` | KeyValues binarios y de texto, la carpeta de Steam desde el registro |

Un adaptador de registro mínimo, como ilustración (un juego inventado):

```python
from dataclasses import dataclass, field
from pathlib import Path

from ..session import Axes, Session
from ._logfollow import Follower, game_started, newest
from .base import Adapter, Context


@dataclass
class ExampleAdapter(Adapter):
    _session: Session | None = field(default=None, repr=False)
    _follow: Follower | None = field(default=None, repr=False)

    def start(self, ctx: Context) -> None:
        log = (ctx.exe.parent if ctx.exe else Path(".")) / "logs" / "game.log"
        self._session = None
        self._follow = Follower(lambda: newest(p for p in [log] if p.exists()), game_started(ctx.pid))

    def poll(self, ctx: Context) -> None:
        for line in self._follow.lines() if self._follow else []:
            if line.startswith("DIED "):
                if self._session is None:
                    self._session = ctx.open(self)
                self._session.event("death", player="me")
                self._session.stat("deaths", 1, "add")

    def stop(self, ctx: Context) -> None:
        self.poll(ctx)
        ctx.close(self._session)
        self._session = None


ADAPTERS = [
    ExampleAdapter(
        id="example",
        game="Example Game",
        kind="log",
        exes=("ExampleGame.exe",),
        source=r"<install>\logs\game.log (followed)",
        records=("deaths",),
        interval=0.5,
        axes=Axes(units="no positions recorded"),
        verified="tested on synthetic log lines in the game's format; untested against the game",
    )
]
```

Abre la sesión con lo primero que merezca la pena grabar, no en `start`, para que un juego que se queda en sus
menús no deje nada (de todos modos se borra una sesión vacía).

## Pruebas {#tests}

```bash
python -m pytest
```

`tests/conftest.py` da a cada prueba una carpeta de datos desechable (`HEAT3D_WATCH_HOME`) y desactiva las
comprobaciones de actualización y las notificaciones (`HEAT3D_NO_UPDATE`, `HEAT3D_NO_TOAST`). Una prueba de
adaptador construye la salida del juego a partir de su formato publicado —paquetes según la especificación,
líneas de registro en el formato del juego, archivos en el diseño documentado— y maneja el adaptador
directamente (abreviado de `tests/test_poe.py`; `data` e `install` son carpetas temporales):

```python
from dataclasses import replace
from heat3d_watch.adapters import poe
from heat3d_watch.adapters.base import Context
from heat3d_watch.config import Settings
from heat3d_watch.session import read_rows

ctx = Context(Settings(data=str(data)), data, exe=install / "PathOfExileSteam.exe")
a = replace(poe.ADAPTERS[0])   # a fresh copy of the adapter
a.start(ctx); a.poll(ctx); a.stop(ctx)
[session] = list((data / "sessions").glob("*/*"))
rows = read_rows(session)      # then check the rows and meta.json's stats
```

Los adaptadores de red se prueban contra un servidor local falso o con paquetes enviados por UDP al adaptador.
Las pruebas que comprueban datos reales del juego en la máquina del desarrollador llevan la marca
`@pytest.mark.local` y se omiten cuando esos datos no están. Esos datos nunca entran en el repositorio.
`test_core.py` contiene además la prueba que falla si aparece en el paquete algún código que podría escribir en
otro proceso (`test_memory_reading_cannot_write`).

## Un `verified` honesto {#an-honest-verified}

`verified` dice qué se comprobó y cómo, y qué no. Lo muestra `games` y cada página de juego, y los jugadores
confían en ello. Ejemplos del código:

- "probado con paquetes en los formatos de 2023, 2024 y 2025 construidos a partir de la especificación publicada
  por EA, enviados por UDP; no probado contra el juego"
- "probado con documentos en el formato GSI publicado, enviados al adaptador en marcha; no probado contra el juego
  en marcha"
- "probado con archivos de estadísticas y esquemas reales de una instalación local; detección de cambios probada
  con archivos construidos en el formato binario KeyValues"

Di "no probado contra el juego" hasta que el adaptador haya grabado el juego en marcha. Indica solo el método y la
tolerancia: nunca un mapa, un id de partida, un nombre de jugador, una fecha, el tamaño de un corpus ni un recuento
exacto de archivos reales, y nunca "esta máquina" (los lectores no la conocen). Nombra la fuente de cada
desplazamiento y diseño, y di dónde se compararon dos fuentes. Nunca afirmes más de lo que se hizo. Un formato que
se adivinó o se tomó de herramientas de la comunidad se dice que es eso.

## Las páginas de juegos {#the-game-pages}

Cada página de [Juegos](games.md) se genera a partir de los adaptadores, así que siempre coincide con el código.
Después de añadir o cambiar un adaptador, vuelve a generarlas desde la carpeta del repositorio:

```bash
HEAT3D_NO_UPDATE=1 python tools/gen_game_pages.py
```

(En PowerShell: `$env:HEAT3D_NO_UPDATE = "1"; python tools/gen_game_pages.py`.) Añade `--check` para solo
comparar: no escribe nada y sale con 1 cuando una página está desactualizada (también la tabla de juegos de
`docs/watcher.md`).

El script:

- carga los adaptadores con `heat3d_watch.adapters.load()`, contra una carpeta de datos temporal vacía, de modo
  que ningún perfil de memoria ni ajuste de tu máquina acabe en las páginas. Los adaptadores de memoria se dejan
  fuera, ya que vienen de los perfiles propios de cada jugador;
- no escribe nada si un módulo de adaptador no se puede importar (las páginas perderían esos juegos);
- escribe `docs/game-<adapter id>.md` para cada adaptador y `docs/games.md` con la tabla general, y borra las
  páginas de los adaptadores que ya no existen;
- toma "Qué se graba", "De dónde viene", "Cómo activarlo", los ejes, la marca de multijugador y
  "Verified" de los campos del adaptador;
- convierte el docstring del módulo en "How it works". Escribe los docstrings en el estilo de texto plano que ya
  usan los módulos, que el script convierte: párrafos; listas con `*`, `-` o `1.`; diseños y ejemplos sangrados
  bajo la línea que los presenta (se convierten en bloques de código); un título subrayado con guiones, o una
  línea de título corta con su texto sangrado justo debajo (se convierten en encabezados);
- enumera las claves de estadística que el código del adaptador fija por nombre —`.stat("key", ...)`, ambos lados
  de una expresión `if` y patrones de f-string como `score.{team}`— en las clases del adaptador y en las ayudas
  que usa. Las claves tomadas de una variable (una tabla de campos del juego) no se enumeran;
- decide "Positions" a partir de `axes.units` del adaptador (una nota que empieza por "no" o "none" significa que
  no hay posiciones) y de lo que escribe su código.

No edites a mano las páginas generadas: cambia el adaptador y vuelve a ejecutar el script. La tabla de
[Todos los juegos en una tabla](watcher.md) es la salida de `python -m heat3d_watch games --markdown`.
