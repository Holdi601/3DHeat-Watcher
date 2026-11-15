---
title: "Automobilista 2 (direkte data)"
nav_order: 6
lang: "no"
source: game-automobilista-2.md
source_hash: "5e3ca1507524"
nav_exclude: true
search_exclude: true
---
# Automobilista 2 (direkte data) {#automobilista-2-live-data}

Mens du spiller Automobilista 2, lagrer watcheren dataene spillet selv sender ut, slik at du senere kan se på dem på et kart i 3DHeat-vieweren.

*Tekniske detaljer: adapter `automobilista-2`, type [`telemetry`](sources-and-rules.md); den kjører mens `AMS2AVX.exe` eller `AMS2.exe` går og ser etter nye data hvert 0,1 s.*

## Hva som tas opp {#what-is-recorded}

- hver bils posisjon (verdensposisjon XYZ, m) 10 ganger i sekundet etter førerens navn, egen bil markert, med fart og posisjon i løpet; eget gir, gass og brems
- øktstart med banen spillet oppgir; runder per bil med rundetid; målgang; egne pit-stopp
- teleporteringer (tilbake til boksen, en omstart): `teleport` der bilen var, `spawn` der den er nå
- egne runder, beste runde, posisjon i løpet, distanse, toppfart
- spillets hele delte minneside i `heat.raw.parquet`, hver gang den endrer seg

## Hvor det kommer fra {#where-it-comes-from}

delt minne $pcars2$ (SMS' SharedMemory.h-layout)

## Slik slår du det på {#how-to-switch-it-on}

I spillet: Options > System > Shared Memory: "Project CARS 2"

## Slik fungerer det {#how-it-works}

Delt minne som racingspill publiserer for dashbord, åpnet skrivebeskyttet - og aldri opprettet.

Flere simulatorer leverer telemetrien sin som en navngitt Windows-filmapping som spillet oppretter og alle kan lese: Kunos' `Local\acpmf_*`-sider (Assetto Corsa, ACC, AC Rally, AC EVOs `Local\acevo_pmf_*`), iRacings `Local\IRSDKMemMapFileName`, RaceRooms `$R3E`, Automobilista 2 / Project CARS 2s `$pcars2$`.

Hvorfor ikke `mmap.mmap(-1, size, tagname=...)`, som er den vanlige måten i Python: når mappingen ikke finnes ennå, *oppretter* den en - her skrivebeskyttet. Et spill som startes etterpå åpner watcherens mapping i stedet for å lage sin egen, og kan da ikke skrive til den, så telemetrien er død til watcheren slipper den. Watcheren starter en adapter så snart spillets prosess dukker opp, og det er nettopp øyeblikket spillet ikke har laget sin mapping ennå. Derfor åpner dette med `OpenFileMappingW`, som bare finner en eksisterende mapping, mapper den med `FILE_MAP_READ`, og melder "ikke der ennå" ellers; adapterne prøver igjen litt senere.

Ingenting her kan skrive: visningen er mappet skrivebeskyttet og kopieres bare ut av med `ctypes.string_at`.

To spill leses her også; hver bil på banen står i deres sider.

#### Automobilista 2 / Project CARS 2 - `$pcars2$` {#automobilista-2--project-cars-2---pcars2}

SMS' `SharedMemory.h` (levert i spillets Support\SharedMemory-mappe; AMS2: Options > System > Shared Memory "Project CARS 2"), `#pragma pack(4)`. `mParticipantInfo[64]` fra byte 28, 100 byte hver: mIsActive, mName[64], mWorldPosition[3] (m, Y opp), mCurrentLapDistance, mRacePosition, mLapsCompleted, mCurrentLap, mCurrentSector; mViewedParticipantIndex (20) er spillerens bil; per deltaker mLastLapTimes (9200), mRaceStates (9520), mSpeeds (10800); spillerens mBestLapTime (6716), mLastLapTime (6720), mSpeed (6848), mBrake, mThrottle, mGear; mSequenceNumber (7320) er oddetall mens spillet skriver. Forskyvningene ble regnet ut fra to uavhengige kopier av headeren (spillets egen kopi er ikke installert her), som stemmer overens.

Begge sidene tas også vare på hele (docs/converters.md, "Live sources"): hele området, hver lesing hvis bytes avviker fra kopien sist tatt vare på, i øktens rå sidefil under `type` `r3e` eller `pcars2` - hver deltakerplass og hvert felt i strukturen, også de som ikke leses her, slik at en senere dekoder bare trenger sidefilen.

Samme modul brukes også av: [Project CARS 2 (direkte data)](game-project-cars-2.md), [RaceRoom Racing Experience (direkte data)](game-raceroom.md).

## Posisjoner og akser {#positions-and-axes}

| | |
|---|---|
| Posisjoner tatt opp | ja |
| Opp-akse | `y` |
| Enheter | meter |
| Speilet for vieweren | ingen |
| Enhetsskala (`scale`: vieweren ganger posisjonene med den) | 1 |

Disse legges i hver økts `meta.json` (`axes`) og, når økten har posisjoner, i `heat.parquet`s fotnote, slik at 3DHeat-vieweren selv vender og skalerer radene - se [Dataene](the-data.md).

## Flerspiller {#multiplayer}

- Merket som spilt på nett (`multiplayer`): **ja**. `games --markdown` viser dette som "tillatt (leser bare det spillet publiserer)".
- Type `telemetry`: den leser bare det spillet eller plattformen gir ut (en UDP-port eller delt minne spillet publiserer), så den tar opp også i nettspill, ikke bare frakoblet; flagget avgjør bare om minne noensinne får leses.
- Minne: **aldri** lest av denne adapteren. Bare `memory`-adaptere leser minne, og aldri for et spill merket som spilt på nett - se [Kilder og regler](sources-and-rules.md).

## Statistikk som registreres {#statistics-recorded}

Statistikknøkler som adapterens kode setter med navn (hver økts `stats` i `meta.json` og tabellen `stats` i `watcher.sqlite`):

`best_lap`, `distance_km`, `finishes`, `incidents`, `laps`, `pit_stops`, `race_position`, `top_speed_kmh`

En nøkkel i klammer fullføres ved kjøretid (`score.{team}` er én nøkkel per lag). Nøkler som koden henter fra en tabell over spillets felt, eller fra spillets egne statistikknavn, står ikke på denne listen; "Hva som tas opp" over nevner dem.

## Fullstendighet {#completeness}

Watcheren følger 3DHeats [konverteringsregel](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md): det kilden inneholder, leses eller tas vare på, og slippes aldri. I tillegg til radene tas hver pakke, side, linje eller svar adapteren mottar, vare på hel i øktens `heat.raw.parquet` (kolonnene `time`, `ms`, `type`, `used`, `payload`, `text`, og alle felt tatt vare på med navn; `used` markerer det som også ble rader), og `meta.json`s `selfCheck.completeness` teller hver `type` - `lost` er 0.

**Leses**

- per deltaker (opptil 64): aktiv, navn, verdensposisjon, posisjon i løpet, fullførte runder; dens siste rundetid, løpstatus og fart
- spillerens bil (mViewedParticipantIndex), spill- og øktstatus, banens sted og variant, beste og siste runde, fart, brems, gass, gir; mSequenceNumber for å hoppe over en kopi tatt midt i en skriving
- forskyvninger fra to uavhengige kopier av SMS' SharedMemory.h som stemmer overens, kontrollert på en side bygd fra dem i testene; ikke ennå mot spillet

**Tatt vare på rått**

- `pcars2`: hele $pcars2$-minneområdet - strukturen går langt utover de 11 312 bytene som leses her - hver lesing hvis bytes avviker fra kopien sist tatt vare på: hver deltakers orientering, sektortider, bil- og klassenavn, pit-moduser og flagg, spillerens fysikk, dekk, fjæring, skade, vær og alt senere Automobilista 2-versjoner har lagt til
- `used` er sann for en side lest til rader; usann for en i menyene, på pause, i en repriser, av en annen layout, eller skrevet midt i (`torn` 1); `unchanged_reads` i meta.json teller lesingene som var byte for byte kopien tatt før

**Ikke tilgjengelig**

- andre deltakeres innganger og fysikk: siden gir bare den viste bilens
- alt mens spillets delte minne-valg er av (Automobilista 2 skriver da ingenting)

**Størrelse**: minneområdet er omtrent 20 til 30 KB (etter spillets versjon), opptil 10 ganger i sekundet mens man kjører: omtrent 0,7 til 1,1 GB i timen før komprimering; zstd krymper de tomme deltakerplassene og de navnene som ikke endrer seg til en brøkdel (ikke ennå målt på en ekte økt)

## Verifisert {#verified}

testet på en side bygd i testen; forskyvninger fra to uavhengige kopier av SharedMemory.h som stemmer overens, ikke fra kopien spillet leveres med; ikke testet mot spillet

## Kilde {#source}

[heat3d_watch/adapters/simracing_shm.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/simracing_shm.py)

<!-- Generated from the adapter by tools/gen_game_pages.py; change the adapter and run it again rather than editing this page. -->
