---
title: "RaceRoom Racing Experience (livegegevens)"
nav_order: 38
lang: "nl"
source: game-raceroom.md
source_hash: "ffd0499ca059"
nav_exclude: true
search_exclude: true
---
# RaceRoom Racing Experience (livegegevens) {#raceroom-racing-experience-live-data}

Terwijl je RaceRoom Racing Experience speelt, slaat de watcher de gegevens op die het spel zelf uitstuurt, zodat je ze later op een kaart in de 3DHeat-viewer kunt bekijken.

*Technische details: adapter `raceroom`, soort [`telemetry`](sources-and-rules.md); hij draait zolang `RRRE64.exe` of `RRRE.exe` actief is en zoekt elke 0,1 s naar nieuwe gegevens.*

## Wat wordt opgenomen {#what-is-recorded}

- de positie van elke auto (wereld XYZ, m) op 10 Hz, per naam van de bestuurder, de eigen auto gemarkeerd, met snelheid en positie in de race; eigen versnelling, gas, rem
- begin van de sessie met de baan zoals het spel die noemt; ronden per auto met rondetijd; finishes; eigen pitstops
- teleports (terug naar de pits, een herstart): `teleport` waar de auto was, `spawn` waar hij nu is
- eigen ronden, beste ronde, positie in de race, afstand, topsnelheid
- de volledige pagina van het gedeelde geheugen van het spel in `heat.raw.parquet`, telkens als hij verandert
- eigen incidentpunten

## Waar het vandaan komt {#where-it-comes-from}

gedeeld geheugen $R3E (r3e.h van Sector3, versie 3)

## Hoe je het aanzet {#how-to-switch-it-on}

Niets hoeft aangezet te worden: de watcher leest de bron zoals het spel of platform die aanbiedt.

## Hoe het werkt {#how-it-works}

Gedeeld geheugen dat racespellen publiceren voor dashboards, alleen-lezen geopend - en nooit aangemaakt.

Verschillende simulators geven hun telemetrie uit als een benoemde Windows-bestandskoppeling die het spel aanmaakt en iedereen mag lezen: de pagina's `Local\acpmf_*` van Kunos (Assetto Corsa, ACC, AC Rally, `Local\acevo_pmf_*` van AC EVO), `Local\IRSDKMemMapFileName` van iRacing, `$R3E` van RaceRoom, `$pcars2$` van Automobilista 2 / Project CARS 2.

Waarom niet `mmap.mmap(-1, size, tagname=...)`, de gebruikelijke manier in Python: als de koppeling nog niet bestaat, *maakt* die er een aan - hier alleen-lezen. Een spel dat daarna start opent de koppeling van de watcher in plaats van zijn eigen te maken, en kan er dan niet naar schrijven, dus zijn telemetrie is dood tot de watcher hem loslaat. De watcher start een adapter zodra het proces van het spel verschijnt, precies het moment waarop het spel zijn koppeling nog niet heeft gemaakt. Daarom opent dit met `OpenFileMappingW`, dat alleen een bestaande koppeling vindt, mapt hem met `FILE_MAP_READ`, en meldt "nog niet aanwezig" anders; de adapters proberen het even later opnieuw.

Hier kan niets schrijven: de weergave is alleen-lezen gekoppeld en wordt alleen met `ctypes.string_at` gekopieerd.

Twee spellen worden hier ook gelezen; elke auto op de baan staat in hun pagina's.

#### RaceRoom Racing Experience - `$R3E` {#raceroom-racing-experience---r3e}

r3e.h van Sector3 (github.com/sector3studios/r3e-api, sample-c/src/r3e.h, versie 3.6), `#pragma pack(1)`. De kop zegt waar de bestuurders beginnen en hoe groot er één is (`all_drivers_offset`, `driver_data_size`), dus het deel per bestuurder - naam, slot, plaats, wereldpositie (float x y z, m), voltooide ronden, huidige rondetijd, finishstatus, pitlane, snelheid - wordt daarmee gelezen. De eigen velden van de speler (beste en vorige ronde, positie in de race, incidentpunten, versnelling, pedalen, namen van baan en layout) worden alleen gelezen op hun offsets van 3.6, en alleen als `all_drivers_offset` de 2008 is waar die indeling hem zet. Y wordt als omhoog aangenomen; de kop zegt dat niet.

De module werkt ook voor: [Automobilista 2 (livegegevens)](game-automobilista-2.md), [Project CARS 2 (livegegevens)](game-project-cars-2.md).

## Posities en assen {#positions-and-axes}

| | |
|---|---|
| Posities opgenomen | ja |
| Omhoog-as | `y` |
| Eenheden | meter; Y omhoog aangenomen (r3e.h zegt het niet) |
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

- per bestuurderspositie (volgens de eigen offset en grootte van de kop): naam, slot, finishstatus, plaats, wereldpositie, voltooide ronden, huidige rondetijd, pitlane, snelheid
- de eigen velden van de speler, alleen als de pagina de indeling r3e.h 3.6 heeft: namen van baan en layout, sessietype, positie in de race, beste en vorige ronde, incidentpunten, versnelling, gas, rem, het slot van de speler
- offsets uitgewerkt uit r3e.h 3.6 van Sector3 en gecontroleerd op een pagina die in de tests daaruit is opgebouwd; nog niet tegen het spel

**Ruw bewaard**

- `r3e`: het volledige $R3E-geheugen, elke lezing waarvan de bytes verschillen van de kopie die als laatste bewaard is - elk veld van r3e.h: de fysica van de speler (oriëntatie, snelheden, versnellingen, g-krachten), motor, brandstof, banden, remmen, schade, vlaggen, pitmenu, sectortijden, de volledige bestuurdersdata van elk bestuurderslot (klasse, model, team, sectortijden, achterstanden, straffen, banden)
- `used` is waar voor een pagina die in rijen is gelezen; onwaar voor een pagina in de menu's, bij pauze, in een replay, van een andere indeling, of midden in het schrijven gepakt (`torn` 1); `unchanged_reads` in meta.json telt de lezingen die byte voor byte gelijk zijn aan de kopie die eerder bewaard is

**Niet beschikbaar**

- de invoer en fysica van andere bestuurders: de pagina geeft alleen die van de speler zelf
- exacte rondetijden van andere auto's: een slot heeft alleen zijn lopende rondetijd, dus een ronde is de laatste lopende tijd die gezien is (tot ongeveer 0,1 s)
- de eigen velden van de speler op een andere indeling dan 3.6: bewaard als ruwe gegevens, niet gelezen tot ze gecontroleerd zijn

**Grootte**: de pagina is 44 KB (r3e.h 3.6; het geheugen is afgerond op hele pagina's van 4 KB), tot 10 keer per seconde tijdens het rijden: ongeveer 1,6 GB per uur voor compressie; lege bestuurdersplekken en velden die niet veranderen worden door zstd heel goed gecomprimeerd (nog niet gemeten op een echte sessie)

## Getest {#verified}

getest op een pagina die in de test is opgebouwd uit r3e.h 3.6 (offsets uitgewerkt uit de officiële header); nog niet getest tegen het spel; rondetijden van andere auto's zijn de laatste lopende rondetijd die gezien is (tot ongeveer 0,1 s)

## Bron {#source}

[heat3d_watch/adapters/simracing_shm.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/simracing_shm.py)

<!-- Generated from the adapter by tools/gen_game_pages.py; change the adapter and run it again rather than editing this page. -->
