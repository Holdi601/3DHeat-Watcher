---
title: "X-Plane (livedata)"
nav_order: 49
lang: "sv"
source: game-xplane.md
source_hash: "be1c5b21d2ef"
nav_exclude: true
search_exclude: true
---
# X-Plane (livedata) {#x-plane-live-data}

När du flyger i X-Plane sparar watchern den data som spelet själv skickar ut, så att du senare kan titta på den på en karta i 3DHeat-visaren.

*Tekniska detaljer: adapter `xplane`, slag [`telemetry`](sources-and-rules.md); den körs medan `X-Plane.exe` är igång och letar efter ny data var 0,1 s.*

## Vad som spelas in {#what-is-recorded}

- egen position 10 gånger per sekund (latitud/longitud/höjd som meter öster/upp/norr från första positionen; lat/lon/höjd sparade som kolumner)
- attityd, visad och sann lufthastighet, markhastighet, Mach, vertikal hastighet, anfallsvinkel, sidglidning, magnetisk kurs, AGL, g (normal, axiell, sida), hastighet och rotationshastigheter, klaffar, luftbromsar, gas, på marken
- vikter (totalt, bränsle, last), landställets handtag, autopilot, motorvarvtal och N1, simulatorns tid och datum, paus, simulatorns hastighet, repris, utetemperatur och havsnivåtryck (X-Plane 12) en gång per sekund
- start, landningar, krascher, flygåterställningar (session_start/session_end per flygning)
- flygtid, tid i luften, sträcka, högsta höjd, högsta g, landningar
- varje svar som X-Plane skickar sparat helt i heat.raw.parquet

## Var datan kommer ifrån {#where-it-comes-from}

X-Planes UDP-gränssnitt på 127.0.0.1:49000 (RREF-datarefs och RPOS-position, besvarade till watchern)

## Så slår du på det {#how-to-switch-it-on}

X-Plane 12: Inställningar > Nätverk > Acceptera inkommande anslutningar (X-Plane 11 svarar som standard)

## Så fungerar det {#how-it-works}

X-Plane 11 och 12: simulatorns egna UDP-gränssnitt på port 49000.

X-Plane svarar den som frågar på 127.0.0.1:49000, i den takt som efterfrågas, till
adressen och porten som förfrågan kom från (X-Planes dokument "Exchanging Data with
X-Plane", levererat i `<X-Plane>\Instructions\`):

```text
RREF  "RREF\0" + int32 freq + int32 index + char[400] dataref path (413 bytes).
      The answer is "RREF" + one internal byte + (int32 index, float32 value)
      pairs; freq 0 stops it.
RPOS  "RPOS\0" + the rate as a NUL-terminated ASCII string ("10\0"). The
      answer is "RPOS" + one internal byte + double lon, lat, elevation (m
      MSL) + float AGL (m), pitch, true heading, roll (deg), vx east, vy up,
      vz south (m/s), P, Q, R (rad/s), tightly packed.
```

RPOS ger latitud och longitud som doubles (RREF bara som floats, en halv meter
ifrån varandra), så den driver positionen; RREF tar med resten och träder in när
RPOS uteblir. Datarefs (namn som i X-Plane 12:s `Resources\plugins\DataRefs.txt`,
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

och resten av flygningen i samma takt (sann lufthastighet, vertikal hastighet, anfallsvinkel,
sidglidning, magnetisk kurs, Mach, axiell och sido-g, rotationshastigheter, klaffar,
luftbromsar, gas: `DATAREFS`), med flygplanets långsammare tillstånd en gång per
sekund (vikter, landställets handtag, autopilot, motorer, simulatorns tid, paus och
hastighet, väder: `SLOW_DATAREFS`). Varje datagram sparas också helt i
sessionens råa sidofil, och meta.json anger vilken dataref varje RREF-index är.

X-Plane 12 accepterar detta bara med Inställningar > Nätverk > "Acceptera inkommande
anslutningar" påslagen. Positionerna läggs i en platt karta kring sessionens första
fix (`Tangent`): x österut, z norrut i meter, y höjden över havet - så en rak flygning
förblir rak hur långt den än går, vilket ett verkligt tangentplan skulle böja nedåt med jorden.
Kartans origo är sessionens `geo`: meta.json och tabellens fotnot bär den, så att visaren kan
lägga den verkliga världen under flygningen.

Den här modulen innehåller också det som de andra flygsimulatorerna delar: den platta kartan,
flygbokföringen (start, landningar, krascher, sträcka), UDP-uttaget och
Steam-bibliotekslistan.

## Positioner och axlar {#positions-and-axes}

| | |
|---|---|
| Positioner sparas | ja |
| Upp-axel | `y` |
| Enheter | meter (öster, höjd, norr från första positionen) |
| Speglad för visaren | `z` |
| Enhetsskala (`scale`: visaren multiplicerar positionerna med den) | 1 |

Dessa läggs i varje sessions `meta.json` (`axes`) och, när sessionen har positioner, i `heat.parquet`:s fotnot, så att 3DHeat-visaren vrider och skalar raderna själv - se [Datan](the-data.md).

## Flerspelarläge {#multiplayer}

- Markerat som spelat online (`multiplayer`): **nej**. `games --markdown` visar detta som "enspelar".
- Slag `telemetry`: den läser bara det spelet eller plattformen lämnar ut (en UDP-port eller delat minne som spelet publicerar), så den spelar in även i onlinespel som offline; flaggan avgör bara om minne någonsin får läsas.
- Minne: **aldrig** läst av den här adaptern. Bara `memory`-adaptrar läser minne, och aldrig för ett spel som är markerat som spelat online - se [Källor och regler](sources-and-rules.md).

## Statistik som sparas {#statistics-recorded}

Statistiknycklar som den här adapterns kod sätter med namn (varje sessions `stats` i `meta.json` och tabellen `stats` i `watcher.sqlite`):

`airborne_time`, `bad_packets`, `crashes`, `distance_km`, `flight_time`, `max_altitude_m`, `max_g`, `{event}s`

En nyckel i klammer fylls i vid körning (`score.{team}` är en nyckel per lag). Nycklar som koden tar från en tabell med spelets fält eller från spelets egna statistiknamn finns inte i listan; "Vad som spelas in" ovan nämner dem.

## Fullständighet {#completeness}

watchern följer 3DHeats [konverterarregel](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md): det källan innehåller läses eller sparas, aldrig slängs. Utöver raderna sparas varje paket, sida, rad eller svar som adaptern tar emot helt i sessionens `heat.raw.parquet` (kolumnerna `time`, `ms`, `type`, `used`, `payload`, `text` och sedan eventuella fält som sparats med namn; `used` markerar det som också blev rader), och `meta.json`:s `selfCheck.completeness` räknar varje `type` - `lost` är 0.

**Läses**

- RPOS (10 Hz): longitud, latitud, höjd, AGL, pitch, sann kurs, roll, hastighet (öst, upp, syd) och rotationshastigheter P/Q/R - allt på raderna
- RREF (10 Hz): de 27 datarefs i `DATAREFS` - position, attityd, IAS, markhastighet, TAS, vertikal hastighet, anfallsvinkel, sidglidning, magnetisk kurs, Mach, g normal/axiell/sida, rotationshastigheter, klaffar, luftbromsar, gas, AGL, kraschad, på marken, flygtid - på raderna
- RREF (1 Hz): de 20 datarefs i `SLOW_DATAREFS` - vikter, landställets handtag, autopilotservon, simulatorns tid och datum, paus, simulatorns hastighet, repris, antal motorer, varvtal för motorerna 1-4, N1 för motorerna 1-2, utetemperatur, havsnivåtryck - på raderna som senast togs emot

**Sparas råa**

- varje datagram helt som `payload`, under sin fyrbokstavsrubrik: `RREF` och `RPOS` (använda när avfrågningen gav en rad; i menyerna, utan fix, ger de ingen), annat som X-Plane skickar till watcherns port under sin egen rubrik eller `unknown`; meta.json:s `requests` anger vilken dataref varje RREF-index är, så nyttolasterna läses utan den här modulen

**Finns inte**

- alla andra datarefs (X-Plane har tusentals): RREF skickar bara det som efterfrågas, en prenumeration var; listan efterfrågar flygningen, flygplanets tillstånd och simulatorns tid - mer cockpitdetalj (radior, lampor, varje motors mätare, fel) skulle multiplicera förfrågningarna
- flygplanets namn och ICAO-typ: byte-array-datarefs, som RREF skickar ett flyttal per tecken
- andra flygplan (AI och flerspelar): sim/multiplayer/position-datarefs som inte efterfrågas
- DATA-utgången (Inställningar > Datautgång): den skickar till en fast adress som väljs i simulatorn, inte till den som frågar; RREF och RPOS täcker det watchern läser

**Storlek**: ungefär 17 MB per timme före zstd (RREF och RPOS vid 10 Hz, ungefär 220 och 70 byte plus en ram vardera, den långsamma RREF en gång per sekund), om X-Plane skickar varje avfrågnings värden i ett paket som det gör; zstd minskar flyttalen flera gånger

## Verifierat {#verified}

testad mot en falsk X-Plane som svarar på RREF/RPOS enligt X-Plane 12:s "Exchanging Data with X-Plane"; dataref-namnen kontrollerade mot X-Plane 12:s DataRefs.txt; ännu inte testad mot den körande simulatorn

## Källa {#source}

[heat3d_watch/adapters/xplane.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/xplane.py)

<!-- Generated from the adapter by tools/gen_game_pages.py; change the adapter and run it again rather than editing this page. -->
