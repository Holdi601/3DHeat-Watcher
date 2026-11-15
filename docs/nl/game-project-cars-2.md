---
title: "Project CARS 2 (livegegevens)"
nav_order: 37
lang: "nl"
source: game-project-cars-2.md
source_hash: "a1990b93b7d1"
nav_exclude: true
search_exclude: true
---
# Project CARS 2 (livegegevens) {#project-cars-2-live-data}

Terwijl je Project CARS 2 speelt, slaat de watcher de gegevens op die het spel zelf uitstuurt, zodat je ze later op een kaart in de 3DHeat-viewer kunt bekijken.

*Technische details: adapter `project-cars-2`, soort [`telemetry`](sources-and-rules.md); hij draait zolang `pCARS2AVX.exe` of `pCARS2.exe` actief is en zoekt elke 0,1 s naar nieuwe gegevens.*

## Wat wordt opgenomen {#what-is-recorded}

- de positie van elke auto (wereld XYZ, m) op 10 Hz, per naam van de bestuurder, de eigen auto gemarkeerd, met snelheid en positie in de race; eigen versnelling, gas, rem
- begin van de sessie met de baan zoals het spel die noemt; ronden per auto met rondetijd; finishes; eigen pitstops
- teleports (terug naar de pits, een herstart): `teleport` waar de auto was, `spawn` waar hij nu is
- eigen ronden, beste ronde, positie in de race, afstand, topsnelheid
- de volledige pagina van het gedeelde geheugen van het spel in `heat.raw.parquet`, telkens als hij verandert

## Waar het vandaan komt {#where-it-comes-from}

gedeeld geheugen $pcars2$ (SMS SharedMemory.h)

## Hoe je het aanzet {#how-to-switch-it-on}

In het spel: Options > System > Shared Memory: "Project CARS 2"

## Hoe het werkt {#how-it-works}

Gedeeld geheugen dat racespellen publiceren voor dashboards, alleen-lezen geopend - en nooit aangemaakt.

Verschillende simulators geven hun telemetrie uit als een benoemde Windows-bestandskoppeling die het spel aanmaakt en iedereen mag lezen: de pagina's `Local\acpmf_*` van Kunos (Assetto Corsa, ACC, AC Rally, `Local\acevo_pmf_*` van AC EVO), `Local\IRSDKMemMapFileName` van iRacing, `$R3E` van RaceRoom, `$pcars2$` van Automobilista 2 / Project CARS 2.

Waarom niet `mmap.mmap(-1, size, tagname=...)`, de gebruikelijke manier in Python: als de koppeling nog niet bestaat, *maakt* die er een aan - hier alleen-lezen. Een spel dat daarna start opent de koppeling van de watcher in plaats van zijn eigen te maken, en kan er dan niet naar schrijven, dus zijn telemetrie is dood tot de watcher hem loslaat. De watcher start een adapter zodra het proces van het spel verschijnt, precies het moment waarop het spel zijn koppeling nog niet heeft gemaakt. Daarom opent dit met `OpenFileMappingW`, dat alleen een bestaande koppeling vindt, mapt hem met `FILE_MAP_READ`, en meldt "nog niet aanwezig" anders; de adapters proberen het even later opnieuw.

Hier kan niets schrijven: de weergave is alleen-lezen gekoppeld en wordt alleen met `ctypes.string_at` gekopieerd.

Twee spellen worden hier ook gelezen; elke auto op de baan staat in hun pagina's.

#### Automobilista 2 / Project CARS 2 - `$pcars2$` {#automobilista-2--project-cars-2---pcars2}

SMS's `SharedMemory.h` (meegeleverd in de map Support\SharedMemory van het spel; AMS2: Options > System > Shared Memory "Project CARS 2"), `#pragma pack(4)`. `mParticipantInfo[64]` vanaf byte 28, 100 bytes per stuk: mIsActive, mName[64], mWorldPosition[3] (m, Y omhoog), mCurrentLapDistance, mRacePosition, mLapsCompleted, mCurrentLap, mCurrentSector; mViewedParticipantIndex (20) is de auto van de speler; per deelnemer mLastLapTimes (9200), mRaceStates (9520), mSpeeds (10800); de mBestLapTime (6716), mLastLapTime (6720), mSpeed (6848), mBrake, mThrottle, mGear van de speler; mSequenceNumber (7320) is oneven terwijl het spel schrijft. De offsets zijn uitgewerkt uit twee onafhankelijke kopieën van de header (de eigen kopie van het spel is hier niet geïnstalleerd), die overeenkomen.

Beide pagina's worden verder helemaal bewaard (docs/converters.md, "Live sources"): het volledige geheugen, elke lezing waarvan de bytes verschillen van de kopie die als laatste bewaard is, in het ruwe bijbestand van de sessie onder `type` `r3e` of `pcars2` - elke deelnemerspositie en elk veld van de struct, ook die welke hier niet gelezen worden, zodat een latere decoder alleen het bijbestand nodig heeft.

De module werkt ook voor: [Automobilista 2 (livegegevens)](game-automobilista-2.md), [RaceRoom Racing Experience (livegegevens)](game-raceroom.md).

## Posities en assen {#positions-and-axes}

| | |
|---|---|
| Posities opgenomen | ja |
| Omhoog-as | `y` |
| Eenheden | meter |
| Gespiegeld voor de viewer | geen |
| Eenheidsschaal (`scale`: de viewer vermenigvuldigt posities ermee) | 1 |

Dit gaat in het `meta.json` (`axes`) van elke sessie en, als de sessie posities heeft, in de footer van `heat.parquet`. De 3DHeat-viewer draait en schaalt de rijen daardoor zelf - zie [De data](the-data.md).

## Multiplayer {#multiplayer}

- Gemarkeerd als online gespeeld (`multiplayer`): **ja**. `games --markdown` toont dit als "allowed (reads only what the game publishes)".
- Soort `telemetry`: hij leest alleen wat het spel of platform uitgeeft (een UDP-poort of gedeeld geheugen dat het spel publiceert), dus hij legt ook online spel vast; de vlag bepaalt alleen of geheugen ooit gelezen mag worden.
- Geheugen: **nooit** gelezen door deze adapter. Alleen `memory`-adapters lezen geheugen, en nooit voor een spel dat als online gespeeld is gemarkeerd - zie [Bronnen en regels](sources-and-rules.md).

## Opgenomen statistieken {#statistics-recorded}

Statistiekensleutels die de code van deze adapter bij naam instelt (elke `stats` van de sessie in `meta.json` en de tabel `stats` van `watcher.sqlite`):

`best_lap`, `distance_km`, `finishes`, `incidents`, `laps`, `pit_stops`, `race_position`, `top_speed_kmh`

Een sleutel tussen accolades wordt tijdens het draaien ingevuld (`score.{team}` is één sleutel per team). Sleutels die de code uit een tabel met de velden van het spel of uit de eigen statistiekennamen van het spel haalt, staan niet in deze lijst; "Wat wordt opgenomen" hierboven noemt ze.

## Volledigheid {#completeness}

De watcher volgt de [converterregel](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md) van 3DHeat: wat de bron bevat wordt gelezen of bewaard, nooit weggegooid. Naast de rijen wordt elk pakket, elke pagina, regel of elk antwoord dat de adapter ontvangt, ongewijzigd bewaard in `heat.raw.parquet` van de sessie (kolommen `time`, `ms`, `type`, `used`, `payload`, `text`, plus elk veld dat op naam bewaard wordt; `used` markeert wat ook rijen werd). `selfCheck.completeness` in `meta.json` telt elk `type` - `lost` is 0.

**Gelezen**

- per deelnemer (tot 64): actief, naam, wereldpositie, positie in de race, voltooide ronden; zijn laatste rondetijd, racestatus en snelheid
- de auto van de speler (mViewedParticipantIndex), spel- en sessiestatus, plaats en variant van de baan, beste en laatste ronde, snelheid, rem, gas, versnelling; mSequenceNumber om een kopie over te slaan die midden in het schrijven gepakt is
- offsets uit twee onafhankelijke kopieën van SMS's SharedMemory.h die overeenkomen, gecontroleerd op een pagina die in de tests uit die kopieën is opgebouwd; nog niet tegen het spel

**Ruw bewaard**

- `pcars2`: het volledige $pcars2$-geheugen - de struct loopt ver door voorbij de 11.312 bytes die hier gelezen worden - elke lezing waarvan de bytes verschillen van de kopie die als laatste bewaard is: de oriëntatie van elke deelnemer, sectortijden, namen van auto en klasse, pitmodi en vlaggen, de fysica van de speler, banden, ophanging, schade, weer en alles wat latere versies van Project CARS 2 hebben toegevoegd
- `used` is waar voor een pagina die in rijen is gelezen; onwaar voor een pagina in de menu's, bij pauze, in een replay, van een andere indeling, of midden in het schrijven gepakt (`torn` 1); `unchanged_reads` in meta.json telt de lezingen die byte voor byte gelijk zijn aan de kopie die eerder bewaard is

**Niet beschikbaar**

- de invoer en fysica van andere deelnemers: de pagina geeft alleen die van de bekeken auto
- alles terwijl de optie gedeeld geheugen van het spel uit staat (Project CARS 2 schrijft dan niets)

**Grootte**: het geheugen is ongeveer 20 tot 30 KB (naar versie van het spel), tot 10 keer per seconde tijdens het rijden: ruwweg 0,7 tot 1,1 GB per uur voor compressie; zstd maakt de lege deelnemersplekken en de namen die niet veranderen tot een fractie (nog niet gemeten op een echte sessie)

## Getest {#verified}

getest op een pagina die in de test is opgebouwd; offsets uit twee onafhankelijke kopieën van SharedMemory.h die overeenkomen, niet uit de kopie die het spel meelevert; nog niet getest tegen het spel

## Bron {#source}

[heat3d_watch/adapters/simracing_shm.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/simracing_shm.py)

<!-- Generated from the adapter by tools/gen_game_pages.py; change the adapter and run it again rather than editing this page. -->
