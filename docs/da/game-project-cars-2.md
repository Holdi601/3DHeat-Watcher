---
title: "Project CARS 2 (live-data)"
nav_order: 36
lang: "da"
source: game-project-cars-2.md
source_hash: "278eb9594615"
nav_exclude: true
search_exclude: true
---
# Project CARS 2 (live-data) {#project-cars-2-live-data}

Mens du spiller Project CARS 2, gemmer watcheren de data, som spillet selv sender ud, så du senere kan se dem på et kort i 3DHeat-vieweren.

*Tekniske detaljer: adapter `project-cars-2`, type [`telemetry`](sources-and-rules.md); den kører, mens `pCARS2AVX.exe` eller `pCARS2.exe` kører, og leder efter nye data hver 0.1 s.*

## Hvad der registreres {#what-is-recorded}

- hver bils position (verdens XYZ, m) 10 gange i sekundet pr. kørernavn, egen bil markeret, med hastighed og løbsplacering; egen gear, gas, bremse
- kørslens start med banen, spillet angiver; runder pr. bil med rundetid; mål; egne depotstop
- teleportering (tilbage til depotet, en genstart): `teleport` der hvor bilen var, `spawn` der hvor den er nu
- egne runder, bedste runde, løbsplacering, distance, topfart
- spillets hele side med delt hukommelse i `heat.raw.parquet`, hver gang den ændrer sig

## Hvor data kommer fra {#where-it-comes-from}

delt hukommelse $pcars2$ (SMS SharedMemory.h)

## Sådan slår du det til {#how-to-switch-it-on}

I spillet: Options > System > Shared Memory: "Project CARS 2"

## Sådan virker det {#how-it-works}

Delt hukommelse, som racingspil udgiver til dashboards, åbnet skrivebeskyttet - og
aldrig oprettet.

Flere simulatorer udleverer deres telemetri som en navngivet Windows-filmapning, som
spillet opretter, og som alle må læse: Kunos' `Local\acpmf_*`-sider (Assetto Corsa,
ACC, AC Rally, AC EVO's `Local\acevo_pmf_*`), iRacings
`Local\IRSDKMemMapFileName`, RaceRooms `$R3E`, Automobilista 2 / Project CARS 2's
`$pcars2$`.

Hvorfor ikke `mmap.mmap(-1, size, tagname=...)`, den sædvanlige måde i Python: når
mappingen ikke findes endnu, *opretter* den en - her skrivebeskyttet. Et spil, der
starter bagefter, åbner watcherens mapping i stedet for at lave sin egen og
kan så ikke skrive til den, så dets telemetri er død, indtil watcheren giver slip.
Watcheren starter en adapter, så snart spillets proces dukker op, og det er
præcis det øjeblik, hvor spillet endnu ikke har lavet sin mapping. Derfor åbnes der med
`OpenFileMappingW`, som kun finder en eksisterende mapping, mappes med
`FILE_MAP_READ`, og ellers meldes "ikke der endnu"; adapterne prøver igen et øjeblik senere.

Intet her kan skrive: visningen er mappet skrivebeskyttet og kopieres kun ud af med
`ctypes.string_at`.

To spil læses også her; hver bil på banen er på deres sider.

#### Automobilista 2 / Project CARS 2 - `$pcars2$` {#automobilista-2--project-cars-2---pcars2}

SMS' `SharedMemory.h` (leveret i spillets mappe Support\SharedMemory;
AMS2: Options > System > Shared Memory "Project CARS 2"), `#pragma pack(4)`.
`mParticipantInfo[64]` fra byte 28, 100 byte hver: mIsActive, mName[64],
mWorldPosition[3] (m, Y op), mCurrentLapDistance, mRacePosition,
mLapsCompleted, mCurrentLap, mCurrentSector; mViewedParticipantIndex (20)
er spillerens bil; pr. deltager mLastLapTimes (9200), mRaceStates
(9520), mSpeeds (10800); spillerens mBestLapTime (6716), mLastLapTime
(6720), mSpeed (6848), mBrake, mThrottle, mGear; mSequenceNumber (7320) er
ulige, mens spillet skriver. Forskydningerne er udledt af to uafhængige kopier af
headeren (spillets egen kopi er ikke installeret her), som stemmer overens.

Begge sider gemmes desuden hele (docs/converters.md, "Live sources"): hele mappingen,
hver læsning hvis bytes afviger fra den kopi, der sidst blev gemt, i kørslens rå sidefil under `type`
`r3e` eller `pcars2` - hver deltagerplads og hvert felt i strukturen, også dem der ikke læses her,
så en senere afkoder kun behøver sidefilen.

Det samme modul bruges også af: [Automobilista 2 (live-data)](game-automobilista-2.md), [RaceRoom Racing Experience (live-data)](game-raceroom.md).

## Positioner og akser {#positions-and-axes}

| | |
|---|---|
| Positioner registreret | ja |
| Op-akse | `y` |
| Enheder | meter |
| Spejlet til vieweren | ingen |
| Enhedsskala (`scale`: vieweren ganger positionerne med den) | 1 |

Disse går ind i hver kørsels `meta.json` (`axes`) og, når kørslen har positioner, i `heat.parquet`s footer, så 3DHeat-vieweren selv drejer og skalerer rækkerne - se [Dataene](the-data.md).

## Flerspiller {#multiplayer}

- Markeret som spillet online (`multiplayer`): **ja**. `games --markdown` viser det som "tilladt (læser kun det spillet udgiver)".
- Type `telemetry`: den læser kun det spillet eller platformen udleverer (en UDP-port eller delt hukommelse spillet udgiver), så den optager også i onlinespil og offline; flaget afgør kun, om hukommelse nogensinde må læses.
- Hukommelse: læses **aldrig** af denne adapter. Kun `memory`-adaptere læser hukommelse, og aldrig for et spil markeret som spillet online - se [Kilder og regler](sources-and-rules.md).

## Registrerede statistikker {#statistics-recorded}

Statistiknøgler, som adapterens kode sætter ved navn (hver kørsels `stats` i `meta.json` og tabellen `stats` i `watcher.sqlite`):

`best_lap`, `distance_km`, `finishes`, `incidents`, `laps`, `pit_stops`, `race_position`, `top_speed_kmh`

En nøgle i klammer udfyldes under kørslen (`score.{team}` er én nøgle pr. hold). Nøgler som koden tager fra en tabel over spillets felter eller fra spillets egne statistiknavne står ikke på listen; "Hvad der registreres" ovenfor nævner dem.

## Fuldstændighed {#completeness}

Watcheren følger 3DHeats [konverterregel](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md): det kilden indeholder, læses eller gemmes, og aldrig smides væk. Ud over rækkerne gemmes hver pakke, side, linje eller svar, adapteren modtager, hel i kørslens `heat.raw.parquet` (kolonnerne `time`, `ms`, `type`, `used`, `payload`, `text` og derefter felter, der gemmes under deres navn; `used` markerer, hvad der også blev til rækker), og `selfCheck.completeness` i `meta.json` tæller hver `type` - `lost` er 0.

**Læst**

- pr. deltager (op til 64): aktiv, navn, position i verden, løbsplacering, gennemførte runder; dens sidste rundetid, løbstilstand og hastighed
- spillerens bil (mViewedParticipantIndex), spillets og sessionens tilstand, banens placering og variant, bedste og sidste runde, hastighed, bremse, gas, gear; mSequenceNumber til at springe en kopi over, der fanges midt i en skrivning
- forskydninger fra to uafhængige kopier af SMS' SharedMemory.h, som stemmer overens, kontrolleret på en side bygget ud fra dem i testene; endnu ikke mod spillet

**Gemt råt**

- `pcars2`: hele $pcars2$-mappingen - strukturen går langt ud over de 11.312 bytes, der læses her - hver læsning hvis bytes afviger fra den kopi, der sidst blev gemt: hver deltagers orientering, sektortider, bil- og klassenavne, depottilstande og flag, spillerens fysik, dæk, ophæng, skader, vejr og alt, senere Project CARS 2-versioner har tilføjet
- `used` er sand for en side læst til rækker; falsk for en i menuerne, på pause, i et replay, af et andet layout, eller fanget midt i en skrivning (`torn` 1); `unchanged_reads` i meta.json tæller de læsninger, der var byte for byte den kopi, der var gemt før

**Ikke tilgængeligt**

- andre deltageres input og fysik: siden giver kun den viste bils
- alt, mens spillets indstilling for delt hukommelse er slået fra (Project CARS 2 skriver intet da)

**Størrelse**: mappingen er cirka 20 til 30 KB (afhængigt af spillets version), op til 10 gange i sekundet under kørsel: cirka 0,7 til 1,1 GB i timen før komprimering; zstd skruer de tomme deltagerpladser og de uændrede navne ned til en brøkdel (endnu ikke målt på en rigtig kørsel)

## Verificeret {#verified}

testet på en side bygget i testen; forskydninger fra to uafhængige kopier af SharedMemory.h, som stemmer overens, ikke fra den kopi spillet leverer; ikke testet mod spillet

## Kilde {#source}

[heat3d_watch/adapters/simracing_shm.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/simracing_shm.py)

<!-- Genereret fra adapteren af tools/gen_game_pages.py; ret adapteren og kør den igen i stedet for at redigere denne side. -->
