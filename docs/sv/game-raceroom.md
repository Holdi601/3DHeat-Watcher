---
title: "RaceRoom Racing Experience (livedata)"
nav_order: 37
lang: "sv"
source: game-raceroom.md
source_hash: "f3879cd40a67"
nav_exclude: true
search_exclude: true
---
# RaceRoom Racing Experience (livedata) {#raceroom-racing-experience-live-data}

När du kör RaceRoom Racing Experience sparar watchern den data som spelet själv skickar ut, så att du senare kan titta på den på en karta i 3DHeat-visaren.

*Tekniska detaljer: adapter `raceroom`, slag [`telemetry`](sources-and-rules.md); den körs medan `RRRE64.exe` eller `RRRE.exe` är igång och letar efter ny data var 0,1 s.*

## Vad som spelas in {#what-is-recorded}

- varje bils position (världens XYZ, m) 10 gånger per sekund, per förarnamn, egen bil markerad, med hastighet och placering i loppet; egen växel, gas, broms
- sessionens start med banan som spelet anger; varv per bil med varvtid; målgångar; egna depåstopp
- teleporteringar (tillbaka till depån, en omstart): `teleport` där bilen var, `spawn` där den är nu
- egna varv, bästa varv, placering i loppet, sträcka, högsta hastighet
- spelets hela delade minnessida i `heat.raw.parquet`, varje gång den ändras
- egna incidentpoäng

## Var datan kommer ifrån {#where-it-comes-from}

delat minne $R3E (Sector3:s r3e.h, version 3)

## Så slår du på det {#how-to-switch-it-on}

Inget behöver slås på: watchern läser källan så som spelet eller plattformen tillhandahåller den.

## Så fungerar det {#how-it-works}

Delat minne som racingspel publicerar för instrumentpaneler, öppnat skrivskyddat - och aldrig skapat.

Flera simulatorer lämnar ut sin telemetri som en namngiven Windows-filmappning som spelet skapar och vem som helst får läsa: Kunos `Local\acpmf_*`-sidor (Assetto Corsa, ACC, AC Rally, AC EVO:s `Local\acevo_pmf_*`), iRacings `Local\IRSDKMemMapFileName`, RaceRooms `$R3E`, Automobilista 2 / Project CARS 2:s `$pcars2$`.

Varför inte `mmap.mmap(-1, size, tagname=...)`, som är det vanliga sättet i Python: när mappningen ännu inte finns *skapar* den en - här skrivskyddat. Ett spel som startar efter det öppnar watchens mappning i stället för att göra sin egen och kan då inte skriva till den, så dess telemetri är död tills watchen släpper taget. Watchen startar en adapter så snart spelets process syns, vilket är exakt det ögonblick då spelet ännu inte har skapat sin mappning. Därför öppnar denna med `OpenFileMappingW`, som bara någonsin hittar en befintlig mappning, mappar den med `FILE_MAP_READ`, och rapporterar "inte där än" annars; adaptrarna försöker igen en stund senare.

Ingenting här kan skriva: vyn är mappad skrivskyddat och kopieras bara ut ur med `ctypes.string_at`.

Två spel läses här också; varje bil på banan finns på deras sidor.

#### RaceRoom Racing Experience - `$R3E` {#raceroom-racing-experience---r3e}

Sector3:s `r3e.h` (github.com/sector3studios/r3e-api, sample-c/src/r3e.h, version 3.6), `#pragma pack(1)`. Huvudet anger var förarna börjar och hur stor en är (`all_drivers_offset`, `driver_data_size`), så förardelen - namn, plats, placering, världsposition (float x y z, m), avklarade varv, aktuell varvtid, målstatus, depåbana, hastighet - läses med dem. Spelarens egna fält (bästa och föregående varv, placering i loppet, incidentpoäng, växel, pedaler, bana- och layoutnamn) läses vid sina 3.6-offset bara när `all_drivers_offset` är 2008, som den layouten lägger den på. Y tas som uppåt; huvudet säger inte det.

Samma modul används också av: [Automobilista 2 (livedata)](game-automobilista-2.md), [Project CARS 2 (livedata)](game-project-cars-2.md).

## Positioner och axlar {#positions-and-axes}

| | |
|---|---|
| Positioner sparas | ja |
| Upp-axel | `y` |
| Enheter | meter; Y uppåt antaget (r3e.h anger inte det) |
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

- per förarplats (efter huvudets egen offset och storlek): namn, plats, målstatus, placering, världsposition, avklarade varv, aktuell varvtid, depåbana, hastighet
- spelarens egna fält, bara när sidan har r3e.h 3.6-layouten: bana- och layoutnamn, sessionstyp, placering i loppet, bästa och föregående varv, incidentpoäng, växel, gas, broms, spelarens plats
- offseten tagna ur Sector3:s r3e.h 3.6 och kontrollerade på en sida byggd av den i testerna; ännu inte mot spelet

**Sparas råa**

- `r3e`: hela $R3E-mappningen, varje läsning vars byte skiljer sig från den senast sparade kopian - varje fält i r3e.h: spelarens fysik (orientering, hastigheter, accelerationer, g-krafter), motor, bränsle, däck, bromsar, skador, flaggor, depåmeny, sektortider, varje förarplats hela förardata (klass, modell, lag, sektortider, avstånd, straff, däck)
- `used` är sann för en sida som lästs till rader; falsk för en i menyerna, pausad, i en repris, med annan layout, eller fångad mitt i skrivningen (`torn` 1); `unchanged_reads` i meta.json räknar de läsningar som var byte för byte samma som kopian som sparades före

**Finns inte**

- andra förares reglage och fysik: sidan ger bara spelarens egna
- andra bilars exakta varvtider: en plats har bara sin pågående varvtid, så ett varv är den senaste pågående tiden som sågs (på ungefär 0,1 s)
- spelarens egna fält på en annan layout än 3.6: sparas råa, läses inte förrän de är kontrollerade

**Storlek**: sidan är 44 KB (r3e.h 3.6; mappningen avrundas upp till hela 4 KB-sidor), upp till 10 gånger per sekund under körning: ungefär 1,6 GB per timme före komprimering; tomma förarplatser och oföränderliga fält komprimeras mycket väl med zstd (ännu inte mätt på en verklig session)

## Verifierat {#verified}

testad på en sida byggd i testet från r3e.h 3.6 (offseter tagna ur den officiella huvudfilen); ännu inte testad mot spelet; andra bilars varvtider är den senaste pågående varvtiden som sågs (på ungefär 0,1 s)

## Källa {#source}

[heat3d_watch/adapters/simracing_shm.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/simracing_shm.py)

<!-- Generated from the adapter by tools/gen_game_pages.py; change the adapter and run it again rather than editing this page. -->
