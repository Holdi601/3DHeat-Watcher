---
title: "VALORANT (replays)"
nav_order: 45
lang: "nl"
source: game-valorant-replays.md
source_hash: "10a648aabdf1"
nav_exclude: true
search_exclude: true
---
# VALORANT (replays) {#valorant-replays}

Na een wedstrijd van VALORANT zet de watcher het replay dat het spel heeft opgeslagen om in bestanden die je kunt bekijken als statistieken en een tijdlijn.

*Technische details: adapter `valorant-replays`, soort [`replay`](sources-and-rules.md); hij draait altijd (hij wacht niet tot een spel start) en zoekt elke 5 s naar nieuwe gegevens.*

## Wat wordt opgenomen {#what-is-recorded}

- de kaart, het wedstrijd-id en de gekozen agents; het infoblok van het replay (lengte, versies, naam, opnametijd, vlaggen voor compressie en versleuteling)
- de gebeurtenissentijdlijn van de server: kills (moordenaar en slachtoffer als netwerk-id's), rondes die beginnen, spikes geplant, ontmanteld en ontploft, ultimates gebruikt, wisselen van kant - elk met zijn id en metadata
- elk deel van het bestand geheel bewaard in heat.raw.parquet; niet gedecodeerd: posities, namen of standen - die staan in de verhulde stroom

## Waar het vandaan komt {#where-it-comes-from}

replays die VALORANT opslaat: %LOCALAPPDATA%/VALORANT/Saved/Demos/\*.vrf (alleen de delen die niet verhuld zijn)

## Hoe je het aanzet {#how-to-switch-it-on}

sla een replay op in VALORANT (carrière > wedstrijd > replay downloaden)

## Hoe het werkt {#how-it-works}

League of Legends- en VALORANT-replays: wat ervan zonder meer gelezen kan worden.

Beide spellen slaan replays op de schijf van de speler op, en beide beschermen wat erin zit:
de gegevens van het spel van moment tot moment zijn verhuld, en bij elke patch anders,
zodat ze niet gebruikt kunnen worden om te valsspelen. Dat deel wordt nergens in
3DHeat gedecodeerd. Wat elk bestand open bevat, wordt gelezen, en de rest
wordt bewaard zoals het is: elk deel van het bestand, geheel, in de `heat.raw.parquet` van de sessie
(de converterregel van 3DHeat, docs/converters.md in de repository van de
viewer), geteld in `selfCheck.completeness` van meta.json.

#### Valorant (.vrf) {#valorant-vrf}

`%LOCALAPPDATA%\VALORANT\Saved\Demos\*.vrf`, een lokaal replay van de Unreal Engine
(indeling van vrfkit, Apache-2.0, en ValorantReplayParser, MIT). Open staat: het
infoblok van het replay (lengte, netwerkversie, changelist, de naam, wanneer het is opgenomen,
of het is gecomprimeerd of versleuteld), de kaart, het wedstrijd-id en de
gekozen agents (in de header), en de eigen gebeurtenissentijdlijn van de server - kills
(moordenaar en slachtoffer als netwerk-id's, geen namen), rondes die beginnen, spikes geplant,
ontmanteld en ontploft, ultimates gebruikt, wisselen van kant - elk met zijn tijd,
id en metadata. Posities, namen, standen en al het andere staan in de verhulde stroom
(de replaydata- en checkpoint-chunks), die geheel wordt bewaard en niet wordt gelezen.

De module werkt ook voor: [League of Legends (replays)](game-lol-replays.md).

## Posities en assen {#positions-and-axes}

| | |
|---|---|
| Posities opgenomen | nee |
| Omhoog-as | `z` |
| Eenheden | wereldeenheden van VALORANT |
| Gespiegeld voor de viewer | geen |
| Eenheidsschaal (`scale`: de viewer vermenigvuldigt posities hiermee) | 1 |

Deze gaan in de `meta.json` van elke sessie (`axes`) en, wanneer de sessie posities heeft, in de footer van `heat.parquet`, zodat de 3DHeat-viewer de rijen zelf draait en schaalt - zie [De data](the-data.md).

## Multiplayer {#multiplayer}

- Als online gespeeld gemarkeerd (`multiplayer`): **ja**. `games --markdown` toont dit als "allowed (reads only what the game publishes)".
- Soort `replay`: hij leest alleen wat het spel of platform uitgeeft (replays en demo's die het spel opslaat), dus hij neemt ook op bij online spel, net als offline; de vlag bepaalt alleen of geheugen ooit gelezen mag worden.
- Geheugen: **nooit** gelezen door deze adapter. Alleen `memory`-adapters lezen geheugen, en nooit voor een spel dat als online gespeeld is gemarkeerd - zie [Bronnen en regels](sources-and-rules.md).

## Opgenomen statistieken {#statistics-recorded}

Statistiekensleutels die de code van deze adapter bij naam instelt (de `stats` van elke sessie in `meta.json` en de tabel `stats` in `watcher.sqlite`):

`kills_in_match`, `map`, `match_seconds`, `rounds`, `spikes_planted`

Een sleutel tussen accolades wordt tijdens het draaien ingevuld (`score.{team}` is één sleutel per team). Sleutels die de code uit een tabel met velden van het spel of uit de eigen statistiekennamen van het spel haalt, staan niet in deze lijst; "Wat wordt opgenomen" hierboven noemt ze.

## Volledigheid {#completeness}

De watcher volgt de [converterregel](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md) van 3DHeat: wat de bron bevat wordt gelezen of bewaard, nooit weggelaten. Naast de rijen wordt elk pakket, elke pagina, regel of antwoord die de adapter ontvangt ongewijzigd bewaard in de `heat.raw.parquet` van de sessie (kolommen `time`, `ms`, `type`, `used`, `payload`, `text`, plus elk veld dat op naam is bewaard; `used` markeert wat ook rijen is geworden), en `selfCheck.completeness` in `meta.json` telt elk `type` - `lost` is 0.

**Gelezen**

- het infoblok, elk veld (meta.json `vrf`): bestandsversie, eigen versies, lengte, netwerkversie, changelist, naam, livevlag, opnametijd, vlaggen voor compressie en versleuteling, de sleutel zoals hij is opgeslagen
- het header-chunk: de kaart, het wedstrijd-id en de gekozen agents (opgezocht aan de hand van hun vorm)
- elk gebeurtenis-chunk: id, groep, metadata, begin- en eindtijd, en uit de data de naam van de gebeurtenis, de tijd in seconden en de getallen ervoor (de netwerk-id's van moordenaar en slachtoffer) - elk een rij

**Ongewijzigd bewaard**

- elk chunk geheel, in de volgorde van het bestand (`offset`), zodat de delen het bestand zijn: `info`, `header`, `event <group>`, `replay_data`, `checkpoint`, `chunk <n>` voor een type dat de indeling niet noemt, `trailing` voor bytes na het laatste hele chunk

**Niet beschikbaar**

- posities, namen, standen, vaardigheden, elk frame van het spel: de replaydata- en checkpoint-chunks zijn verhuld. Geheel bewaard, niet gelezen
- de inhoud van een versleuteld replay: doorlopen en geheel bewaard, binnenin niets gelezen

**Grootte**: het ruwe bijbestand is ongeveer zo groot als het replay zelf: de verhulde stroom wordt niet kleiner

## Geverifieerd {#verified}

gebouwd volgens de containerindeling die vrfkit (Apache-2.0) beschrijft; niet getest op een echt replay, er was er geen beschikbaar - er wordt gecontroleerd vóór het lezen en wat niet past wordt overgeslagen

## Bron {#source}

[heat3d_watch/adapters/riot_replays.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/riot_replays.py)

<!-- Generated from the adapter by tools/gen_game_pages.py; change the adapter and run it again rather than editing this page. -->
