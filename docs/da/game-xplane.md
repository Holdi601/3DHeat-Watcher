---
title: "X-Plane (live-data)"
nav_order: 49
lang: "da"
source: game-xplane.md
source_hash: "be1c5b21d2ef"
nav_exclude: true
search_exclude: true
---
# X-Plane (live-data) {#x-plane-live-data}

Mens du spiller X-Plane, gemmer watcheren de data, som spillet selv sender ud, så du senere kan se dem på et kort i 3DHeat-vieweren.

*Tekniske detaljer: adapter `xplane`, type [`telemetry`](sources-and-rules.md); den kører, mens `X-Plane.exe` kører, og leder efter nye data hver 0.1 s.*

## Hvad der registreres {#what-is-recorded}

- egen position 10 gange i sekundet (breddegrad/længdegrad/højde som meter øst/op/nord fra det første fix; bredde-, længde- og højdegrad gemt som kolonner)
- attitude, angivet og sand lufthastighed, jordhastighed, Mach, lodret hastighed, AoA, sideglidning, magnetisk kurs, AGL, g (normal, aksial, side), hastigheds- og rotationsrater, klapper, luftbremse, gas, på jorden
- vægte (total, brændstof, last), landingsstelshåndtag, autopilot, motoromdrejninger og N1, simulatorens tid og dato, pause, simulatorhastighed, replay, udetemperatur og havniveautryk (X-Plane 12) én gang i sekundet
- afgange, landinger, styrt, nulstillinger af flyvninger (session_start/session_end pr. flyvning)
- flyvetid, luftbåren tid, distance, højeste højde, højeste g, landinger
- hvert svar X-Plane sender gemt helt i heat.raw.parquet

## Hvor data kommer fra {#where-it-comes-from}

X-Planes UDP-grænseflade på 127.0.0.1:49000 (RREF-datarefs og RPOS-position, besvaret til watcheren)

## Sådan slår du det til {#how-to-switch-it-on}

X-Plane 12: Settings > Network > Accept incoming connections (X-Plane 11 svarer som standard)

## Sådan virker det {#how-it-works}

X-Plane 11 og 12: simulatorens egen UDP-grænseflade på port 49000.

X-Plane svarer enhver, der spørger på 127.0.0.1:49000, med den takt der bedes om, til
den adresse og port forespørgslen kom fra (X-Planes dokument "Exchanging Data with
X-Plane", leveret i `<X-Plane>\Instructions\`):

```text
RREF  "RREF\0" + int32 freq + int32 index + char[400] dataref path (413 bytes).
      The answer is "RREF" + one internal byte + (int32 index, float32 value)
      pairs; freq 0 stops it.
RPOS  "RPOS\0" + the rate as a NUL-terminated ASCII string ("10\0"). The
      answer is "RPOS" + one internal byte + double lon, lat, elevation (m
      MSL) + float AGL (m), pitch, true heading, roll (deg), vx east, vy up,
      vz south (m/s), P, Q, R (rad/s), tightly packed.
```

RPOS giver breddegrad og længdegrad som doubles (RREF kun som floats, en halv meter
fra hinanden), så den driver positionen; RREF leverer resten og træder til, når
RPOS udebliver. Datarefs (navne som i X-Plane 12's `Resources\plugins\DataRefs.txt`,
<https://developer.x-plane.com/datarefs/>):

```text
sim/flightmodel/position/latitude, longitude, elevation  deg, deg, m MSL
sim/flightmodel/position/true_theta, true_phi, true_psi  pitch, roll, true heading (deg)
sim/flightmodel/position/indicated_airspeed              knots
sim/flightmodel/position/groundspeed                     m/s
sim/flightmodel/position/y_agl                           m above ground
sim/flightmodel/forces/g_nrml                            g, normal to the wings
sim/flightmodel/failures/onground_any                    1 on the ground
sim/flightmodel2/misc/has_crashed                        1 crashed
sim/time/total_flight_time_sec                           since the flight was reset
```

og resten af flyvningen i samme takt (sand lufthastighed, lodret hastighed, AoA,
sideglidning, magnetisk kurs, Mach, aksial og side-g, rotationsrater, klapper,
luftbremse, gas: `DATAREFS`), med flyets langsommere tilstand én gang i sekundet
(vægte, landingsstelshåndtag, autopilot, motorer, simulatorens tid, pause og
hastighed, vejr: `SLOW_DATAREFS`). Hver datagram gemmes også hel i
sessionens råsidefil, og meta.json navngiver dataref'en bag hvert RREF-indeks.

X-Plane 12 accepterer kun disse, når Settings > Network > "Accept incoming
connections" er slået til. Positioner lægges i et fladt kort omkring sessionens første fix
(`Tangent`): x øst, z nord i meter, y højden over havet - så en vandret flyvning forbliver vandret, uanset hvor langt den går, hvilket et sandt tangentplan ville bøje nedad med jordens krumning. Kortets udgangspunkt er sessionens `geo`: meta.json
og tabellens footer bærer det, så vieweren kan lægge den rigtige verden under
flyvningen.

Modulet rummer også det, de andre flysimulatorer deler: det flade kort, flyvebogholderiet (afgange, landinger, styrt, distance), UDP-socketen og Steam-biblioteksliste.

## Positioner og akser {#positions-and-axes}

| | |
|---|---|
| Positioner registreret | ja |
| Op-akse | `y` |
| Enheder | meter (øst, højde, nord fra det første fix) |
| Spejlet for vieweren | `z` |
| Enhedsskala (`scale`: vieweren ganger positionerne med den) | 1 |

Disse går ind i hver sessions `meta.json` (`axes`) og, når sessionen har positioner, ind i `heat.parquet`s footer, så 3DHeat-vieweren selv drejer og skalerer rækkerne - se [Dataene](the-data.md).

## Flerspiller {#multiplayer}

- Markeret som spillet online (`multiplayer`): **nej**. `games --markdown` viser dette som "enkeltspiller".
- Type `telemetry`: den læser kun det, spillet eller platformen udleverer (en UDP-port eller delt hukommelse spillet udgiver), så den optager også i onlinespil såvel som offline; flaget afgør kun, om hukommelse nogensinde må læses.
- Hukommelse: **aldrig** læst af denne adapter. Kun `memory`-adaptere læser hukommelse, og aldrig for et spil markeret som spillet online - se [Kilder og regler](sources-and-rules.md).

## Statistik der registreres {#statistics-recorded}

Statistiknøgler, som denne adapters kode sætter ved navn (hver sessions `stats` i `meta.json` og tabellen `stats` i `watcher.sqlite`):

`airborne_time`, `bad_packets`, `crashes`, `distance_km`, `flight_time`, `max_altitude_m`, `max_g`, `{event}s`

En nøgle i klammer udfyldes under kørslen (`score.{team}` er én nøgle pr. hold). Nøgler som koden tager fra en tabel over spillets felter eller fra spillets egne statistiknavne står ikke på listen; "Hvad der registreres" ovenfor nævner dem.

## Fuldstændighed {#completeness}

Watcheren følger 3DHeats [konverterregel](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md): det kilden indeholder, læses eller gemmes, aldrig smidt væk. Ud over rækkerne gemmes hver pakke, side, linje eller svar, adapteren modtager, hel i sessionens `heat.raw.parquet` (kolonnerne `time`, `ms`, `type`, `used`, `payload`, `text`, plus ethvert felt gemt under sit navn; `used` markerer det, der også blev rækker), og `meta.json`s `selfCheck.completeness` tæller hver `type` - `lost` er 0.

**Læst**

- RPOS (10 Hz): længdegrad, breddegrad, højde, AGL, pitch, sand kurs, roll, hastighed (øst, op, syd) og rotationsrater P/Q/R - alt på rækkerne
- RREF (10 Hz): de 27 datarefs i `DATAREFS` - position, attitude, IAS, jordhastighed, TAS, lodret hastighed, AoA, sideglidning, magnetisk kurs, Mach, g normal/aksial/side, rotationsrater, klapper, luftbremse, gas, AGL, styrt, på jorden, flyvetid - på rækkerne
- RREF (1 Hz): de 20 datarefs i `SLOW_DATAREFS` - vægte, landingsstelshåndtag, autopilotservoer, simulatorens tid og dato, pause, simulatorhastighed, replay, antal motorer, omdrejninger for motor 1-4, N1 for motor 1-2, udelufttemperatur, havniveautryk - på rækkerne som sidst modtaget

**Gemt råt**

- hver datagram hel som `payload`, under sin firebogstavs-header: `RREF` og `RPOS` (brugt, når forespørgslen lavede en række; i menuerne, uden et fix, laver de ingen), alt andet X-Plane sender til watcherens port under sin egen header eller `unknown`; meta.jsons `requests` siger, hvilken dataref hvert RREF-indeks er, så payloadene kan læses uden dette modul

**Ikke tilgængeligt**

- alle andre datarefs (X-Plane har tusindvis): RREF sender kun det, der bedes om, ét abonnement ad gangen; listen beder om flyvningen, flyets tilstand og simulatorens tid - mere cockpitdetalje (radioer, lys, hver motors målere, fejl) ville gange forespørgslerne
- flyets navn og ICAO-type: byte-array-datarefs, som RREF sender én float pr. tegn
- andre fly (AI og multiplayer): sim/multiplayer/position-datarefs ikke efterspurgt
- DATA-udgangen (Settings > Data Output): den sender til en fast adresse valgt i simulatoren, ikke til den, der spørger; RREF og RPOS dækker det, watcheren læser

**Størrelse**: cirka 17 MB i timen før zstd (RREF og RPOS 10 gange i sekundet, cirka 220 og 70 bytes plus en ramme hver, den langsomme RREF én gang i sekundet), hvis X-Plane sender hver forespørgsels værdier i én pakke, som den gør; zstd reducerer floats flere gange

## Verificeret {#verified}

testet mod en falsk X-Plane, der svarer på RREF/RPOS efter X-Plane 12's 'Exchanging Data with X-Plane'; dataref-navne kontrolleret mod X-Plane 12's DataRefs.txt; ikke testet mod den kørende simulator

## Kilde {#source}

[heat3d_watch/adapters/xplane.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/xplane.py)

<!-- Generated from the adapter by tools/gen_game_pages.py; change the adapter and run it again rather than editing this page. -->
