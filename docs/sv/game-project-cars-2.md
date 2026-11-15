---
title: "Project CARS 2 (livedata)"
nav_order: 36
lang: "sv"
source: game-project-cars-2.md
source_hash: "278eb9594615"
nav_exclude: true
search_exclude: true
---
# Project CARS 2 (livedata) {#project-cars-2-live-data}

När du kör Project CARS 2 sparar watchern den data som spelet själv skickar ut, så att du senare kan titta på den på en karta i 3DHeat-visaren.

*Tekniska detaljer: adapter `project-cars-2`, slag [`telemetry`](sources-and-rules.md); den körs medan `pCARS2AVX.exe` eller `pCARS2.exe` är igång och letar efter ny data var 0,1 s.*

## Vad som spelas in {#what-is-recorded}

- varje bils position (världens XYZ, m) 10 gånger per sekund, per förarnamn, egen bil markerad, med hastighet och placering i loppet; egen växel, gas, broms
- sessionens start med banan som spelet anger; varv per bil med varvtid; målgångar; egna depåstopp
- teleporteringar (tillbaka till depån, en omstart): `teleport` där bilen var, `spawn` där den är nu
- egna varv, bästa varv, placering i loppet, sträcka, högsta hastighet
- spelets hela delade minnessida i `heat.raw.parquet`, varje gång den ändras

## Var datan kommer ifrån {#where-it-comes-from}

delat minne $pcars2$ (SMS SharedMemory.h)

## Så slår du på det {#how-to-switch-it-on}

I spelet: Options > System > Shared Memory: "Project CARS 2"

## Så fungerar det {#how-it-works}

Delat minne som racingspel publicerar för instrumentpaneler, öppnat skrivskyddat - och aldrig skapat.

Flera simulatorer lämnar ut sin telemetri som en namngiven Windows-filmappning som spelet skapar och vem som helst får läsa: Kunos `Local\acpmf_*`-sidor (Assetto Corsa, ACC, AC Rally, AC EVO:s `Local\acevo_pmf_*`), iRacings `Local\IRSDKMemMapFileName`, RaceRooms `$R3E`, Automobilista 2 / Project CARS 2:s `$pcars2$`.

Varför inte `mmap.mmap(-1, size, tagname=...)`, som är det vanliga sättet i Python: när mappningen ännu inte finns *skapar* den en - här skrivskyddat. Ett spel som startar efter det öppnar watchens mappning i stället för att göra sin egen och kan då inte skriva till den, så dess telemetri är död tills watchen släpper taget. Watchen startar en adapter så snart spelets process syns, vilket är exakt det ögonblick då spelet ännu inte har skapat sin mappning. Därför öppnar denna med `OpenFileMappingW`, som bara någonsin hittar en befintlig mappning, mappar den med `FILE_MAP_READ`, och rapporterar "inte där än" annars; adaptrarna försöker igen en stund senare.

Ingenting här kan skriva: vyn är mappad skrivskyddat och kopieras bara ut ur med `ctypes.string_at`.

Två spel läses här också; varje bil på banan finns på deras sidor.

#### Automobilista 2 / Project CARS 2 - `$pcars2$` {#automobilista-2--project-cars-2---pcars2}

SMS:s `SharedMemory.h` (levereras i spelets mapp Support\SharedMemory; AMS2: Options > System > Shared Memory "Project CARS 2"), `#pragma pack(4)`. `mParticipantInfo[64]` från byte 28, 100 byte var: mIsActive, mName[64], mWorldPosition[3] (m, Y upp), mCurrentLapDistance, mRacePosition, mLapsCompleted, mCurrentLap, mCurrentSector; mViewedParticipantIndex (20) är spelarens bil; per deltagare mLastLapTimes (9200), mRaceStates (9520), mSpeeds (10800); spelarens mBestLapTime (6716), mLastLapTime (6720), mSpeed (6848), mBrake, mThrottle, mGear; mSequenceNumber (7320) är udda medan spelet skriver. Offseten togs fram ur två oberoende kopior av huvudet (spelets egna kopia är inte installerad här), som stämmer överens.

Båda sidorna sparas dessutom helt (docs/converters.md, "Live sources"): hela mappningen, varje läsning vars byte skiljer sig från den senast sparade kopian, i sessionens råa sidfil under `type` `r3e` eller `pcars2` - varje förarplats och varje fält i strukturen, även de som inte läses här, så att en senare avkodare bara behöver sidfilen.

Samma modul används också av: [Automobilista 2 (livedata)](game-automobilista-2.md), [RaceRoom Racing Experience (livedata)](game-raceroom.md).

## Positioner och axlar {#positions-and-axes}

| | |
|---|---|
| Positioner sparas | ja |
| Upp-axel | `y` |
| Enheter | meter |
| Speglad för visaren | ingen |
| Enhetsskala (`scale`: visaren multiplicerar positionerna med den) | 1 |

Dessa läggs i varje sessions `meta.json` (`axes`) och, när sessionen har positioner, i `heat.parquet`:s fotnot, så att 3DHeat-visaren vrider och skalar raderna själv - se [Datan](the-data.md).

## Flerspelarläge {#multiplayer}

- Markerat som spelat online (`multiplayer`): **ja**. `games --markdown` visar detta som "allowed (reads only what the game publishes)".
- Slag `telemetry`: den läser bara det spelet eller plattformen lämnar ut (en UDP-port eller delat minne som spelet publicerar), så den spelar in även i onlinespel som offline; flaggan avgör bara om minne någonsin får läsas.
- Minne: **aldrig** läst av den här adaptern. Bara `memory`-adaptrar läser minne, och aldrig för ett spel som är markerat som spelat online - se [Källor och regler](sources-and-rules.md).

## Statistik som sparas {#statistics-recorded}

Statistiknycklar som den här adapterns kod sätter med namn (varje sessions `stats` i `meta.json` och tabellen `stats` i `watcher.sqlite`):

`best_lap`, `distance_km`, `finishes`, `incidents`, `laps`, `pit_stops`, `race_position`, `top_speed_kmh`

En nyckel i klammer fylls i vid körning (`score.{team}` är en nyckel per lag). Nycklar som koden tar från en tabell med spelets fält eller från spelets egna statistiknamn finns inte i listan; "Vad som spelas in" ovan nämner dem.

## Fullständighet {#completeness}

watchern följer 3DHeats [konverterarregel](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md): det källan innehåller läses eller sparas, aldrig slängs. Utöver raderna sparas varje paket, sida, rad eller svar som adaptern tar emot helt i sessionens `heat.raw.parquet` (kolumnerna `time`, `ms`, `type`, `used`, `payload`, `text` och sedan eventuella fält som sparats med namn; `used` markerar det som också blev rader), och `meta.json`:s `selfCheck.completeness` räknar varje `type` - `lost` är 0.

**Läses**

- per deltagare (upp till 64): aktiv, namn, världsposition, placering, avklarade varv; dess senaste varvtid, tävlingsläge och hastighet
- spelarens bil (mViewedParticipantIndex), spel- och sessionsläge, banans plats och variant, bästa och senaste varv, hastighet, broms, gas, växel; mSequenceNumber för att hoppa över en kopia som fångats mitt i skrivningen
- offseten från två oberoende kopior av SMS:s SharedMemory.h som stämmer överens, kontrollerade på en sida byggd av dem i testerna; ännu inte mot spelet

**Sparas råa**

- `pcars2`: hela $pcars2$-mappningen - strukturen sträcker sig långt förbi de 11 312 byte som läses här - varje läsning vars byte skiljer sig från den senast sparade kopian: varje deltagares orientering, sektortider, bil- och klassnamn, depålägen och flaggor, spelarens fysik, däck, fjädring, skador, väder och allt som senare Project CARS 2-versioner lagt till
- `used` är sann för en sida som lästs till rader; falsk för en i menyerna, pausad, i en repris, med annan layout, eller fångad mitt i skrivningen (`torn` 1); `unchanged_reads` i meta.json räknar de läsningar som var byte för byte samma som kopian som sparades före

**Finns inte**

- andra deltagares reglage och fysik: sidan ger bara den visade bilens
- allt medan spelets alternativ för delat minne är av (Project CARS 2 skriver då ingenting)

**Storlek**: mappningen är ungefär 20 till 30 KB (beroende på spelets version), upp till 10 gånger per sekund under körning: ungefär 0,7 till 1,1 GB per timme före komprimering; zstd krymper de tomma deltagarplatserna och de oföränderliga namnen till en bråkdel (ännu inte mätt på en verklig session)

## Verifierat {#verified}

testad på en sida byggd i testet; offseten från två oberoende kopior av SharedMemory.h som stämmer överens, inte från kopian som spelet levereras med; ännu inte testad mot spelet

## Källa {#source}

[heat3d_watch/adapters/simracing_shm.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/simracing_shm.py)

<!-- Generated from the adapter by tools/gen_game_pages.py; change the adapter and run it again rather than editing this page. -->
