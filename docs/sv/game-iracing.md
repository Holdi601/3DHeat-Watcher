---
title: "iRacing (livedata)"
nav_order: 28
lang: "sv"
source: game-iracing.md
source_hash: "894d9bc4081f"
nav_exclude: true
search_exclude: true
---
# iRacing (livedata) {#iracing-live-data}

När du kör iRacing sparar watchern den data som spelet själv skickar ut, så att du senare kan titta på den som statistik och en tidslinje.

*Tekniska detaljer: adapter `iracing`, slag [`telemetry`](sources-and-rules.md); den körs medan `iRacingSim64DX11.exe` eller `iRacingSim64.exe` är igång och letar efter ny data var 0,1 s.*

## Vad som spelas in {#what-is-recorded}

- körningen 5 gånger per sekund utan position (iRacing ger ingen live): hastighet, växel, gas, broms, varv, andel av varvet, placering i loppet och klass, incidenter
- sessionens start, att stiga in och ur bilen, in- och utfart till depåfilen, flagga vid målflaggan, varv med varvtid, incidenter med sina poäng, rutig flagga, målgång
- .ibt-telemetrifilerna som skrivs under passet (latitud, longitud, höjd - visaren läser dem)
- varv, bästa varv, incidenter, placering i loppet, depåstopp, sträcka, högsta hastighet
- hela det delade minnet i `heat.raw.parquet`: huvud, variabelhuvuden, sessionsinformation, varje telemetrirad som lästs

## Var datan kommer ifrån {#where-it-comes-from}

delat minne Local\IRSDKMemMapFileName (iRacing SDK); .ibt-filer i %USERPROFILE%\Documents\iRacing\telemetry

## Så slår du på det {#how-to-switch-it-on}

Inget behöver slås på för livedatan. För positioner: logga telemetri i bilen (Alt+L) eller sätt irsdkLog=1 i app.ini

## Så fungerar det {#how-it-works}

iRacing, live: iRacing SDK:s delade minne, läst direkt.

iRacing publicerar sin telemetri för appar i en namngiven filmappning,
`Local\IRSDKMemMapFileName`, som simulatorn skapar medan den körs (och signalerar
`Local\IRSDKDataValidEvent` vid varje uppdatering, vilket inte behövs här: watchen
läser tio gånger per sekund). Layouten är SDK:ns `irsdk_defines.h`,
också följd av pyirsdk (MIT) - skriven på nytt här utifrån dessa fakta:

```text
irsdk_header (little-endian int32s)
    0 ver, 4 status (bit 0: connected), 8 tickRate,
    12 sessionInfoUpdate, 16 sessionInfoLen, 20 sessionInfoOffset,
    24 numVars, 28 varHeaderOffset, 32 numBuf, 36 bufLen, 40 pad[2],
    48 varBuf[4]: { tickCount, bufOffset, pad[2] } (16 bytes each)
irsdk_varHeader (144 bytes, numVars of them at varHeaderOffset)
    0 type (0 char, 1 bool, 2 int, 3 bitfield, 4 float, 5 double),
    4 offset (into a line), 8 count, 12 countAsTime + 3 pad,
    16 name[32], 48 desc[64], 112 unit[32]
session info: YAML text at sessionInfoOffset, rewritten when
    sessionInfoUpdate changes (track, sessions, drivers)
```

Simulatorn skriver `numBuf` rader i tur och ordning; den nyaste är den med
högsta tickCount, och en rad läses om om dess tickCount ändrades medan den kopierades.

Live-datan har ingen världsposition - latitud, longitud och höjd finns bara i
.ibt-filerna som iRacing loggar till `Documents\iRacing\telemetry` (Alt+L i bilen,
eller `irsdkLog=1`), som 3DHeat-visaren läser själv. Så det här sparar körningen
som händelser utan koordinater - hastighet, varv, andelen av varvet som är gjord,
placering i loppet, incidenter - plus varv, incidenter, depåstopp och målflaggan, och
i slutet de .ibt-filer som skrivits under passet som `telemetry_file`-händelser, för
visaren att öppna.

Vid sidan av raderna sparas hela minneskartan i sessionens råa sidofil
(`heat.raw.parquet`): rubrikens fasta del (`header`, varje gång den ändras), variabelrubrikerna
(`var_headers`, hela, och som JSON i `text`, varje gång layouten ändras), sessionsinformationens
YAML (`session_info`, dess text varje gång `sessionInfoUpdate` rör sig) och den
nyaste telemetriraden (`telemetry`, varje variabel i den, vid varje läsning som hittar en ny tick). Variabelrubrikerna
och en rad är allt en senare avkodare behöver för att läsa vilken variabel som helst.

Källa: iRacing SDK (irsdk_defines.h, forumdokumentationen "iRacing SDK");
kutu/pyirsdk (MIT) för bekräftelse av offseten.

## Positioner och axlar {#positions-and-axes}

| | |
|---|---|
| Positioner sparas | nej |
| Upp-axel | `y` |
| Enheter | inga positioner live; .ibt-filerna bär latitud/longitud/höjd |
| Speglad för visaren | ingen |
| Enhetsskala (`scale`: visaren multiplicerar positionerna med den) | 1 |

Dessa läggs i varje sessions `meta.json` (`axes`) och, när sessionen har positioner, i `heat.parquet`:s fotnot, så att 3DHeat-visaren vrider och skalar raderna själv - se [Datan](the-data.md).

## Flerspelarläge {#multiplayer}

- Markerat som spelat online (`multiplayer`): **ja**. `games --markdown` visar detta som "tillåtet (läser bara det spelet publicerar)".
- Slag `telemetry`: den läser bara det spelet eller plattformen lämnar ut (en UDP-port eller delat minne som spelet publicerar), så den spelar in även i onlinespel som offline; flaggan avgör bara om minne någonsin får läsas.
- Minne: **aldrig** läst av den här adaptern. Bara `memory`-adaptrar läser minne, och aldrig för ett spel som är markerat som spelat online - se [Källor och regler](sources-and-rules.md).

## Statistik som sparas {#statistics-recorded}

Statistiknycklar som den här adapterns kod sätter med namn (varje sessions `stats` i `meta.json` och tabellen `stats` i `watcher.sqlite`):

`best_lap`, `distance_km`, `finishes`, `incidents`, `laps`, `pit_stops`, `race_position`, `sessions`, `top_speed_kmh`

En nyckel i klammer fylls i vid körning (`score.{team}` är en nyckel per lag). Nycklar som koden tar från en tabell med spelets fält eller från spelets egna statistiknamn finns inte i listan; "Vad som spelas in" ovan nämner dem.

## Fullständighet {#completeness}

watchern följer 3DHeats [konverterarregel](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md): det källan innehåller läses eller sparas, aldrig slängs. Utöver raderna sparas varje paket, sida, rad eller svar som adaptern tar emot helt i sessionens `heat.raw.parquet` (kolumnerna `time`, `ms`, `type`, `used`, `payload`, `text` och sedan eventuella fält som sparats med namn; `used` markerar det som också blev rader), och `meta.json`:s `selfCheck.completeness` räknar varje `type` - `lost` är 0.

**Läses**

- från den nyaste telemetriraden: speltid, nummer, tillstånd och id, på banan, replay, varv, varv avklarade, andel och meter av varvet, sista och bästa varv, hastighet, växel, gas, broms, varvtal, depåvägen, banans underlag, placering i loppet och klass, egen incidenträknare (raderna `driving` 5 gånger per sekund och händelserna)
- nu också på `driving`-raderna: `steering_angle`, `yaw`, `yaw_north`, `pitch`, `roll` (grader, av simulatorns radianer - bara när variabelrubriken anger enheten som rad), `fuel_l` (enhet l), `lat_accel` och `lon_accel` (enhet m/s^2)
- från sessionsinformations-YAML:en: spelarens bilindex, bana och konfiguration, sessionstyper, varje förares namn, bil, lag och nummer (session_start-rader, meta.json)
- kontrollerat mot ett block byggt utifrån irsdk_defines.h i testerna; ännu inte mot simulatorn

**Sparas råa**

- `telemetry`: den nyaste raden helt, varje variabel som simulatorn publicerar (CarIdx-arrayerna för varje bil, däck, fjädring, de höghastighets-`_ST`-arrayerna där simulatorn har dem ...), vid varje läsning som hittar en ny tick; `tick` är simulatorns tickräknare; `used` är falskt medan en replay spelas
- `var_headers`: variabelrubrikerna helt (144 byte vardera) och, i `text`, som JSON (namn, typ, offset, antal, enhet, beskrivning), varje gång layouten ändras - tillräckligt för att läsa varje variabel i varje sparad rad
- `session_info`: YAML-texten helt varje gång dess uppdateringsräknare rör sig (helgen, sessioner och resultat, förare, bilinställning, radio, kameralistor), `update` är räknaren
- `header`: de 112 byte långa irsdk-rubriken helt varje gång den ändras (version, status, takt, offset, radernas ticks)

**Finns inte**

- en världsposition live: det delade minnet har ingen; latitud, longitud och höjd finns bara i .ibt-filerna (när loggningen är på), som visaren läser - watchern anger de som skrivits under passet
- ticks mellan två läsningar: simulatorn skriver 60 rader per sekund i 3 eller 4 platser och watchen läser 10 gånger per sekund, så de flesta ticks skrivs över innan de kan läsas; .ibt-filen har varje tick när loggningen är på

**Storlek**: en telemetrirad är några KB (ungefär 5 till 10 KB med alla bilars arrayer), sparad upp till 10 gånger per sekund, plus rubriken (112 byte) lika ofta och sessionsinformations-YAML:en (tiotals KB) när den ändras: ungefär 0,2 till 0,4 GB per timme på banan före komprimering; zstd gör det till en bråkdel (ännu inte mätt på ett riktigt pass)

## Verifierat {#verified}

testad på ett delat minnesblock byggt i testet från irsdk-layouten; ännu inte testad mot simulatorn

## Källa {#source}

[heat3d_watch/adapters/iracing.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/iracing.py)

<!-- Generated from the adapter by tools/gen_game_pages.py; change the adapter and run it again rather than editing this page. -->
