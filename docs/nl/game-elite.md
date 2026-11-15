---
title: "Elite Dangerous (logbestanden)"
nav_order: 18
lang: "nl"
source: game-elite.md
source_hash: "bb5bcf75553a"
nav_exclude: true
search_exclude: true
---
# Elite Dangerous (logbestanden) {#elite-dangerous-log-files}

Terwijl je Elite Dangerous speelt, leest de watcher de bestanden die het spel schrijft en slaat op wat er gebeurde, zodat je het later op een kaart in de 3DHeat-viewer kunt bekijken.

*Technische details: adapter `elite`, soort [`log`](sources-and-rules.md); hij draait zolang `EliteDangerous64.exe` loopt en zoekt elke 0,25 s naar nieuwe gegevens.*

## Wat wordt opgenomen {#what-is-recorded}

- elke journaalgebeurtenis, onder zijn journaalnaam, met zijn gewone velden
- positie in de melkweg (StarPos, lichtjaren) bij sprongen, locaties, spawns, doden, aandokken, landen
- spawn bij LoadGame/Resurrect, dood bij Died, aan-/afdokken, touchdown/liftoff, sprong, session_end
- route over het planeetoppervlak uit Status.json: breedtegraad, lengtegraad, hoogte, koers, en meters in een raakvlak per hemellichaam (sessie = naam van het hemellichaam), met de overige eenvoudige velden van Status.json (Flags, Flags2, GuiFocus, LegalState, ...)
- elke journaalregel en elk companion-bestand geheel in `heat.raw.parquet`
- sprongen, afgelegde sprongafstand, doden, kills, verdiende credits, voltooide missies, gescande hemellichamen, bezochte systemen, aandokkingen, landingen

## Waar het vandaan komt {#where-it-comes-from}

Spelersjournaal %USERPROFILE%\Saved Games\Frontier Developments\Elite Dangerous\Journal.\*.log (nieuwste bestand, gevolgd terwijl het wordt geschreven), Status.json en de andere companion-\*.json-bestanden (Market, Outfitting, Shipyard, NavRoute, Cargo, ModulesInfo, ShipLocker, Backpack, FCMaterials) in dezelfde map

## Hoe je het aanzet {#how-to-switch-it-on}

Je hoeft niets aan te zetten: de watcher leest de bron zoals het spel of het platform die aanbiedt.

## Hoe het werkt {#how-it-works}

Elite Dangerous: het spelersjournaal en Status.json die het spel schrijft terwijl het draait.

Waar: `%USERPROFILE%\Saved Games\Frontier Developments\Elite Dangerous\`

* `Journal.<yyyy-mm-ddThhmmss>.<part>.log` - één JSON-object per regel, één bestand per start van het spel (een lange sessie gaat verder in deel .02, .03 ...). Elke regel heeft `timestamp` (UTC, ISO 8601) en `event`. Posities in de melkweg zijn de `StarPos` [x, y, z] van het systeem, in lichtjaren vanaf Sol, bij `FSDJump`, `Location` en `CarrierJump`. Het galactische assenstelsel van Elite is y omhoog (richting galactisch noorden), z richting het galactische centrum en x richting galactische lengtegraad 270 - een linkshandig stelsel, dus de viewer spiegelt z om het goed rond te tekenen.
* `Status.json` - telkens geheel herschreven als de staat van het schip verandert: `Flags`, en dichtbij een planeet `Latitude`, `Longitude` (graden), `Altitude` (meter), `Heading`, `BodyName` en `PlanetRadius` (meter).
* De andere companion-bestanden, elk geheel herschreven wanneer de bijbehorende journaalgebeurtenis wordt geschreven: `Market.json`, `Outfitting.json`, `Shipyard.json`, `NavRoute.json`, `Cargo.json`, `ModulesInfo.json`, `ShipLocker.json`, `Backpack.json`, `FCMaterials.json`. Elk `*.json`-bestand van de map dat het spel in deze sessie schrijft, wordt geheel bewaard telkens als het verandert (de converterregel van 3DHeat: wat de bron bevat wordt gelezen of bewaard), onder zijn bestandsnaam.

Elke journaalregel wordt ongewijzigd bewaard in het ruwe bijbestand van de sessie, onder zijn `event`; elk companion-bestand onder zijn bestandsnaam; een regel die geen JSON is onder `unparsed`.

Posities op het oppervlak worden in een lokaal raakvlak per hemellichaam gezet, in meters: het eerste vaste punt op een hemellichaam is zijn oorsprong, x oost, z noord, y omhoog (hoogte), met dezelfde handigheid als het galactische stelsel. De rijen dragen de naam van het hemellichaam als `session`, zodat een rit of wandeling op een planeet als eigen route wordt getekend. Galactische rijen hebben sessie "galaxy". De twee schalen staan in één tabel; kies de sessie in de viewer.

Formaat: de "Elite Dangerous Player Journal"-handleiding van Frontier (bij elke update op het officiële forum gepubliceerd, <https://forums.frontier.co.uk/> - "Journal Manual", v4.x), gebeurtenissen en velden zoals daar beschreven; Status.json-vlaggen volgens het hoofdstuk "Status File" van dezelfde handleiding.

## Posities en assen {#positions-and-axes}

| | |
|---|---|
| Posities opgenomen | ja |
| Omhoog-as | `y` |
| Eenheden | lichtjaren (rijen van de melkweg, sessie 'galaxy'); meter oost/omhoog/noord vanaf het eerste vaste punt op een hemellichaam (rijen van het oppervlak, sessie = naam van het hemellichaam) |
| Gespiegeld voor de viewer | `z` |
| Eenheidsschaal (`scale`: de viewer vermenigvuldigt posities hiermee) | 1 |

Deze gaan in de `meta.json` van elke sessie (`axes`) en, wanneer de sessie posities heeft, in de footer van `heat.parquet`, zodat de 3DHeat-viewer de rijen zelf draait en schaalt - zie [De data](the-data.md).

## Multiplayer {#multiplayer}

- Als online gespeeld gemarkeerd (`multiplayer`): **ja**. `games --markdown` toont dit als "allowed (reads only what the game publishes)".
- Soort `log`: hij leest alleen wat het spel of platform uitgeeft (bestanden die het spel schrijft terwijl het draait), dus hij neemt ook op bij online spel, net als offline; de vlag bepaalt alleen of geheugen ooit gelezen mag worden.
- Geheugen: **nooit** gelezen door deze adapter. Alleen `memory`-adapters lezen geheugen, en nooit voor een spel dat als online gespeeld is gemarkeerd - zie [Bronnen en regels](sources-and-rules.md).

## Opgenomen statistieken {#statistics-recorded}

Statistiekensleutels die de code van deze adapter bij naam instelt (de `stats` van elke sessie in `meta.json` en de tabel `stats` in `watcher.sqlite`):

`bad_lines`, `bodies_scanned`, `carrier_jumps`, `credits`, `credits_earned`, `deaths`, `distance_ly`, `dockings`, `jumps`, `kills`, `landings`, `missions_completed`, `ship`, `surface_fixes`, `systems_visited`

Een sleutel tussen accolades wordt tijdens het draaien ingevuld (`score.{team}` is één sleutel per team). Sleutels die de code uit een tabel met velden van het spel of uit de eigen statistiekennamen van het spel haalt, staan niet in deze lijst; "Wat wordt opgenomen" hierboven noemt ze.

## Volledigheid {#completeness}

De watcher volgt de [converterregel](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md) van 3DHeat: wat de bron bevat wordt gelezen of bewaard, nooit weggelaten. Naast de rijen wordt elk pakket, elke pagina, regel of antwoord die de adapter ontvangt ongewijzigd bewaard in de `heat.raw.parquet` van de sessie (kolommen `time`, `ms`, `type`, `used`, `payload`, `text`, plus elk veld dat op naam is bewaard; `used` markeert wat ook rijen is geworden), en `selfCheck.completeness` in `meta.json` telt elk `type` - `lost` is 0.

**Gelezen**

- elke journaalregel als rij onder zijn `event`, met zijn gewone velden (de vertaalde tekst waar het spel die geeft; teksten langer dan 300 tekens worden in de rij ingekort)
- rijen van de melkweg (StarPos) bij FSDJump, CarrierJump, Location, LoadGame, Resurrect, Died, Docked, Undocked, Touchdown, Liftoff, Shutdown; rijen van het oppervlak uit Status.json en Touchdown/Liftoff
- de eenvoudige velden van Status.json (Flags, Flags2, GuiFocus, LegalState, Cargo, FireGroup, Oxygen, Health, Temperature, Gravity, SelectedWeapon, ...) bij de rijen van het oppervlak
- de statistieken: sprongen, afstand, doden, kills, verdiende credits, missies, gescande hemellichamen, bezochte systemen, aandokkingen, landingen

**Ongewijzigd bewaard**

- elke journaalregel geheel, `type` = zijn `event` (FSDJump, Scan, Music, ReceiveText, ...), `used` waar; de lijsten en objecten die de rijen weglaten (StarPos, Factions, Rewards, Killers, Materials, Modules, ...) staan alleen hier
- een journaalregel die geen JSON is, `type` `unparsed`
- elk companion-bestand geheel telkens als het spel het herschrijft, `type` = zijn bestandsnaam: `Status.json` (`used` als het een rij van het oppervlak maakte), `Market.json`, `Outfitting.json`, `Shipyard.json`, `NavRoute.json`, `Cargo.json`, `ModulesInfo.json`, `ShipLocker.json`, `Backpack.json`, `FCMaterials.json`, en elk ander `*.json` dat het spel daar schrijft

**Niet beschikbaar**

- positie tussen sprongen (binnen een systeem, in supercruise of normale ruimte): het spel schrijft alleen de StarPos van het systeem en, dichtbij een planeet, breedtegraad, lengtegraad en hoogte
- posities van andere schepen en spelers: het journaal is het verhaal van de commandant zelf
- snelheid, gas en andere vluchttelemetrie: het spel schrijft die niet
- journaals en companion-bestanden van eerdere sessies: bewaard wanneer ze gespeeld werden (de volger begint aan het eind van een bestand dat ouder is dan deze run van het spel)
- de companion-webAPI van Frontier (cAPI): heeft de aanmelding van de speler bij Frontier nodig; geen bestand dat het spel schrijft

**Grootte**: ongeveer 1-5 MB ruwe tekst per uur: het journaal 0,2-2 MB, Status.json (minder dan 1 KB, tot elke seconde herschreven) 1-2 MB, een set markt/outfitting/shipyard 20-150 KB per bezocht station; zstd in heat.raw.parquet maakt het ongeveer een tiende

## Geverifieerd {#verified}

parser opnieuw afgespeeld over echte journaalbestanden van een lokale installatie (aantallen gebeurtenissen kloppen met de statistieken); Status.json-posities op het oppervlak alleen getest met gesimuleerde momentopnamen

## Bron {#source}

[heat3d_watch/adapters/elite.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/elite.py)

<!-- Generated from the adapter by tools/gen_game_pages.py; change the adapter and run it again rather than editing this page. -->
