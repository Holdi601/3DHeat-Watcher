---
title: "Star Citizen (archivos de registro)"
nav_order: 42
lang: es
source: game-starcitizen.md
source_hash: "6528f948d2e5"
nav_exclude: true
search_exclude: true
---
# Star Citizen (archivos de registro) {#star-citizen-log-files}

Mientras juegas a Star Citizen, el watcher lee los archivos que escribe el juego y guarda lo que ha pasado, para que luego puedas verlo como estadísticas y como una línea de tiempo.

*Detalles técnicos: adaptador `starcitizen`, tipo [`log`](sources-and-rules.md); se ejecuta mientras `StarCitizen.exe` está en marcha y busca datos nuevos cada 0,5 s.*

## Qué se graba {#what-is-recorded}

- muertes con víctima, asesino, arma, tipo de daño y zona (jugadores y PNJ)
- vehículos inutilizados y destruidos, con piloto, causa y zona
- destinos de viaje cuántico, cambios de sistema solar, apariciones, reapariciones, incapacitaciones
- cada línea de Game.log, completa, en heat.raw.parquet
- muertes (de jugadores y de PNJ), suicidios, vehículos destruidos y perdidos, saltos cuánticos

## De dónde sale {#where-it-comes-from}

&lt;instalación>\StarCitizen\LIVE\Game.log (la carpeta de la versión del StarCitizen.exe en marcha), solo el archivo de registro que escribe el juego; es un juego con Easy Anti-Cheat: no se toca su proceso

## Cómo activarlo {#how-to-switch-it-on}

No hace falta activar nada: el watcher lee la fuente tal como la entrega el juego o la plataforma.

## Cómo funciona {#how-it-works}

Star Citizen: el registro propio del cliente, `<instalación>\StarCitizen\LIVE\Game.log`.

El juego escribe Game.log desde cero en cada inicio (el anterior pasa a
`logbackups\`). Solo se lee ese archivo: Star Citizen usa Easy Anti-Cheat, y
nada de aquí se acerca al proceso del juego. Las líneas empiezan con una marca de tiempo UTC y
un nivel, y después una etiqueta entre paréntesis angulares:

```text
<2025-04-13T17:17:51.279Z> [Notice] <Actor Death> CActor::Kill: 'Victim' [200146297631] in zone
    'ANVL_Hornet_F7A_Mk2_2677329226210' killed by 'Killer' [202061381370] using
    'GATS_BallisticGatling_S3_2677329225797' [Class unknown] with damage type 'VehicleDestruction'
    from direction x: 0.000000, y: 0.000000, z: 0.000000 [Team_ActorTech][Actor]
<...> [Notice] <Vehicle Destruction> CVehicle::OnAdvanceDestroyLevel: Vehicle 'ANVL_Arrow_123' [123] in zone
    'OOC_Stanton_1_Hurston' [pos x: 1.0, y: 2.0, z: 3.0 vel x: 0, y: 0, z: 0] driven by 'Driver' [456]
    advanced from destroy level 0 to 2 caused by 'Attacker' [789] with 'Combat' [Team_VehicleFeatures][Vehicle]
<...> [Notice] <AccountLoginCharacterStatus_Character> Character: createdAt 1 - updatedAt 2 - geid 3 -
    accountId 4 - name Handle - state STATE_CURRENT [Team_GameServices][Login]
<...> [Notice] <Quantum Navtarget> CSCItemQuantumDrive::RmMulticastOnQTToPoint : Local client user
    Handle[200000000001] received QT data for Entity:AEGS_Gladius_123[123] to Target Stanton1b ...
<...> [Notice] <Changing Solar System> ... Client entity Handle ... changing system from Stanton to Pyro ...
```

(aquí se parten en varias líneas; en el archivo, cada una ocupa una sola línea). La zona de una muerte suele ser la
nave en la que iba la víctima, no un lugar. El formato no lo documenta Cloud
Imperium y cambia entre parches; los patrones siguen las líneas que leen los rastreadores de
muertes de la comunidad (por ejemplo <https://github.com/DimmaDont/all-slain>, MIT; solo hechos),
y lo que no encaja se salta, no se adivina. El `pos` de un vehículo es relativo a la zona
y se guarda solo como texto: no se dibuja ninguna coordenada.

Cada línea se guarda completa en el archivo bruto de la sesión (regla del convertidor de
3DHeat), encaje o no: `type` es la etiqueta de la línea entre paréntesis angulares (`Actor
Death`, `Spawn Flow`, ...); si no la tiene, su primera palabra entre corchetes (`Notice`,
`CSessionManager::OnClientSpawned`); si tampoco, `untagged`. Una línea sin marca de tiempo es `untimed`.

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

`bad_lines`, `deaths`, `incapacitations`, `kills`, `npc_kills`, `player_kills`, `quantum_jumps`, `suicides`, `system_jumps`, `vehicles_destroyed`, `vehicles_lost`

Una clave entre llaves se completa en tiempo de ejecución (`score.{team}` es una clave por equipo). Las claves que el código toma de una tabla de campos del juego o de sus nombres de estadística no aparecen en esta lista; "Qué se graba" más arriba las nombra.

## Completitud {#completeness}

El watcher sigue la [regla del convertidor](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md) de 3DHeat: lo que la fuente contiene se lee o se guarda, nunca se descarta. Además de las filas, cada paquete, página, línea o respuesta que recibe el adaptador se guarda completo en `heat.raw.parquet` de la sesión (columnas `time`, `ms`, `type`, `used`, `payload`, `text`, y cualquier campo guardado por nombre; `used` marca lo que también se convirtió en filas), y `selfCheck.completeness` de `meta.json` cuenta cada `type`; `lost` es 0.

**Se lee**

- `<Actor Death>`: víctima, asesino, arma y su clase, tipo de daño, zona; PNJ o jugador
- `<Vehicle Destruction>`: vehículo, zona, posición relativa a la zona como texto, piloto, causa, modo, nivel de destrucción
- objetivos `<Quantum Navtarget>`, `<Changing Solar System>`, `OnClientSpawned`, reapariciones en el hospital, incapacitaciones con sus causas, `EndSession`
- el identificador del jugador (handle), de `<AccountLoginCharacterStatus_Character>` o de la línea de inicio de sesión

**Se guarda en bruto**

- cada línea de Game.log completa, `type` = su etiqueta entre paréntesis angulares (`Actor Death`, `Vehicle Destruction`, `Spawn Flow`, `Jump Drive State Changed`, `SHUDEvent_OnNotification`, `RequestLocationInventory`, ...), si no, su primera palabra entre corchetes (`Notice`, `CSessionManager::OnClientSpawned`, ...), si no, `untagged`; las líneas sin marca de tiempo (la cabecera del registro, el texto partido) como `untimed`; `used` cuando la línea se convirtió en fila

**No disponible**

- posiciones: el registro no da ninguna en un marco que se pueda dibujar (el `pos` de un vehículo destruido es relativo a una zona cuyo lugar no se registra)
- nada del proceso del juego ni de la red: Star Citizen usa Easy Anti-Cheat; solo se lee el archivo de registro
- registros de inicios anteriores (`logbackups`): el Game.log de cada inicio se guarda cuando se juega
- líneas en un formato que un parche cambia: se guardan en bruto y se decodifican de nuevo cuando se conozca la nueva forma

**Tamaño**: Game.log crece unos 5-15 MB por hora de juego (más en zonas concurridas y con errores); zstd en heat.raw.parquet lo deja en aproximadamente una décima parte

## Verificado {#verified}

probado con líneas sintéticas de Game.log en el formato que documentan los rastreadores de la comunidad; sin probar contra el juego

## Fuente {#source}

[heat3d_watch/adapters/starcitizen.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/starcitizen.py)

<!-- Generated from the adapter by tools/gen_game_pages.py; change the adapter and run it again rather than editing this page. -->
