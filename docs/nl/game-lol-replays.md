---
title: "League of Legends (replays)"
nav_order: 30
lang: "nl"
source: game-lol-replays.md
source_hash: "216b88922360"
nav_exclude: true
search_exclude: true
---
# League of Legends (replays) {#league-of-legends-replays}

Na een wedstrijd van League of Legends zet de watcher het replay dat het spel heeft opgeslagen om in bestanden die je op een kaart in de 3DHeat-viewer kunt bekijken.

*Technische details: adapter `lol-replays`, soort [`replay`](sources-and-rules.md); hij draait altijd (hij wacht niet tot een spel start) en zoekt elke 5 s naar nieuwe gegevens.*

## Wat wordt opgenomen {#what-is-recorded}

- de kampioen van elke speler, rol, team, kills, deaths, assists, goud, schade aan kampioenen en resultaat, en elk ander getal van het scorebord aan het eind van het spel
- je eigen regel als statistieken, en je eigen rijen met jouw naam (meta.json `player`), met je Riot ID in de instellingen
- met je eigen Riot API-sleutel: de positie van elke speler elke minuut met de statistieken van die minuut, en elke gebeurtenis van de tijdlijn (kills op de plek waar ze gebeurden, gebouwen, monsters, wards, items, vaardigheden), op de kloktijd die de tijdlijn geeft
- elk deel van het replaybestand geheel bewaard in heat.raw.parquet; niet gedecodeerd: het spel van moment tot moment, dat versleuteld en tegen valsspelen verhuld is

## Waar het vandaan komt {#where-it-comes-from}

replays die de League-client opslaat: %USERPROFILE%/Documents/League of Legends/Replays/\*.rofl (alleen de gewone metadata van na het spel); met je eigen Riot API-sleutel de officiële tijdlijn van de wedstrijd uit de Match-V5 API van Riot

## Hoe je het aanzet {#how-to-switch-it-on}

sla een replay op in de League-client (wedstrijdgeschiedenis > downloaden); voor posities stel je riot_api_key en riot_platform in met `config --set`

## Hoe het werkt {#how-it-works}

League of Legends- en VALORANT-replays: wat ervan zonder meer gelezen kan worden.

Beide spellen slaan replays op de schijf van de speler op, en beide beschermen wat erin zit:
de gegevens van het spel van moment tot moment zijn verhuld, en bij elke patch anders,
zodat ze niet gebruikt kunnen worden om te valsspelen. Erdoorheen komen betekent de
eigen code van het spel uit elkaar halen, wat de gebruiksvoorwaarden van Riot verbieden (Terms of Service 3.1 en 7.1)
- daarom wordt dat hier niet gedaan. Wat elk bestand open bevat, wordt gelezen, en de rest
wordt bewaard zoals het is: elk deel van het bestand, geheel, in de `heat.raw.parquet` van de sessie
(de converterregel van 3DHeat, docs/converters.md in de repository van de
viewer), geteld in `selfCheck.completeness` van meta.json.

#### League of Legends (.rofl) {#league-of-legends-rofl}

`%USERPROFILE%\Documents\League of Legends\Replays\*.rofl`. Beide containerversies bevatten het
scorebord van na het spel als gewone JSON (`statsJson`): voor elk van de tien
spelers de kampioen, kills, deaths, assists, goud, schade aan kampioenen, items, team, rol, winst, hun Riot ID, en elk ander
getal dat het spel optelt (meer dan honderd per speler); alles wordt de `player_result`-rij van de speler. ROFL1 (patch 14.9 en eerder) heeft het na een vaste
header (`RIOT\0\0`, een handtekening van 256 bytes, dan de lengtes); ROFL2 (14.11 en later,
`RIOT\2\0`) aan het eind van het bestand, de lengte in de laatste vier bytes (door een
Riot-ingenieur opgegeven, ReplayBook-probleem 299). De payload-header van ROFL1 (game-id,
lengte, aantal chunks en keyframes, de lengte van de chunksleutel) en de tabel met chunks
(id, type, lengte, volgende chunk, offset) staan open en worden gelezen; de chunks zelf zijn
versleuteld en worden geheel bewaard, ongelezen. Indelingen uit
roflxd.cs (MIT).

Posities komen niet uit het bestand. Met een eigen Riot-ontwikkelaarssleutel van de speler
(`riot_api_key` in de instellingen; een persoonlijke sleutel is precies hiervoor bedoeld,
"showing (self) player stats"), wordt de officiële tijdlijn van de wedstrijd opgehaald uit
de Match-V5 API van Riot: de positie van elke speler elke minuut met alles wat het beeld van die
minuut over hen zegt (goud, ervaring, niveau, minions, kampioen- en schadestatistieken), en
elke gebeurtenis van de tijdlijn - kills, gebouwen, elite-monsters, wards, items, vaardigheden,
niveaus - elk als rij, op de plek waar die gebeurde wanneer die een plaats heeft. Zonder sleutel
wordt niets opgehaald en niets verzonden.

De module werkt ook voor: [VALORANT (replays)](game-valorant-replays.md).

## Posities en assen {#positions-and-axes}

| | |
|---|---|
| Posities opgenomen | ja |
| Omhoog-as | `y` |
| Eenheden | kaarteenheden van Summoner's Rift (ongeveer 15.000 breed) |
| Gespiegeld voor de viewer | geen |
| Eenheidsschaal (`scale`: de viewer vermenigvuldigt posities hiermee) | 1 |

Deze gaan in de `meta.json` van elke sessie (`axes`) en, wanneer de sessie posities heeft, in de footer van `heat.parquet`, zodat de 3DHeat-viewer de rijen zelf draait en schaalt - zie [De data](the-data.md).

## Multiplayer {#multiplayer}

- Als online gespeeld gemarkeerd (`multiplayer`): **ja**. `games --markdown` toont dit als "allowed (reads only what the game publishes)".
- Soort `replay`: hij leest alleen wat het spel of platform uitgeeft (replays en demo's die het spel opslaat), dus hij neemt ook op bij online spel, net als offline; de vlag bepaalt alleen of geheugen ooit gelezen mag worden.
- Geheugen: **nooit** gelezen door deze adapter. Alleen `memory`-adapters lezen geheugen, en nooit voor een spel dat als online gespeeld is gemarkeerd - zie [Bronnen en regels](sources-and-rules.md).

## Opgenomen statistieken {#statistics-recorded}

Statistiekensleutels die de code van deze adapter bij naam instelt (de `stats` van elke sessie in `meta.json` en de tabel `stats` in `watcher.sqlite`):

`champion`, `game_seconds`, `won`

Een sleutel tussen accolades wordt tijdens het draaien ingevuld (`score.{team}` is één sleutel per team). Sleutels die de code uit een tabel met velden van het spel of uit de eigen statistiekennamen van het spel haalt, staan niet in deze lijst; "Wat wordt opgenomen" hierboven noemt ze.

## Volledigheid {#completeness}

De watcher volgt de [converterregel](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md) van 3DHeat: wat de bron bevat wordt gelezen of bewaard, nooit weggelaten. Naast de rijen wordt elk pakket, elke pagina, regel of antwoord die de adapter ontvangt ongewijzigd bewaard in de `heat.raw.parquet` van de sessie (kolommen `time`, `ms`, `type`, `used`, `payload`, `text`, plus elk veld dat op naam is bewaard; `used` markeert wat ook rijen is geworden), en `selfCheck.completeness` in `meta.json` telt elk `type` - `lost` is 0.

**Gelezen**

- de metadata-JSON: speelduur, versie, id's van de laatste chunk en keyframe, en `statsJson` - elk veld van het scorebord van elke speler op hun `player_result`-rij (getallen als tekst worden als getallen gelezen)
- ROFL1: het lengteblok, de payload-header (game-id, speelduur, aantal keyframes en chunks, id's van de start- en spelstart-chunk, keyframe-interval, de chunksleutel zoals hij is opgeslagen) en de tabel met chunks (id, type, lengte, volgende chunk, offset) - in meta.json `rofl` en in de `text` van de ruwe rijen
- ROFL2: de versiestring
- de Match-V5-tijdlijn (alleen met je eigen API-sleutel): elk deelnemersframe op een `position`-rij (of `participant_frame` zonder plaats) met al zijn velden plat gemaakt (`championStats.armor`, `damageStats.totalDamageDone`, `currentGold`, `xp`, ...); elke gebeurtenis als rij die naar haar type heet, geplaatst waar ze een `position` heeft, CHAMPION_KILL als een kill en een dood

**Ongewijzigd bewaard**

- elk deel van de .rofl, geheel, in de volgorde van het bestand (`offset`), zodat de delen het bestand zijn: `magic`, `signature`, `lengths`, `metadata`, `payload_header`, `chunk_header`, `chunk`, `keyframe` (ROFL1); `body`, `metadata`, `metadata_length` (ROFL2); elk stuk dat geen deel dekt als `unknown`
- de tijdlijn geheel: `timeline <type>` voor elke gebeurtenis, `timeline participantFrame` voor elk frame van een speler (`participant` zijn id), `timeline` voor de rest

**Niet beschikbaar**

- het spel zelf (posities, vaardigheden, elke eenheid, van moment tot moment): de chunks van ROFL1 en de body van ROFL2 zijn versleuteld en de pakketten erin worden bij elke patch verhuld; erdoorheen komen betekent de client uit elkaar halen, wat de voorwaarden van Riot verbieden (3.1, 7.1). Geheel bewaard, niet gelezen
- posities zonder je eigen Riot API-sleutel: het bestand heeft er open geen

**Grootte**: het ruwe bijbestand is ongeveer zo groot als het replay zelf: de versleutelde chunks worden niet kleiner

## Geverifieerd {#verified}

de metadata-lezer getest op bestanden die volgens de indelingen in roflxd.cs (MIT) zijn gemaakt; de tijdlijn op de gedocumenteerde JSON van Match-V5; er was geen echt replay om tegen te controleren

## Bron {#source}

[heat3d_watch/adapters/riot_replays.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/riot_replays.py)

<!-- Generated from the adapter by tools/gen_game_pages.py; change the adapter and run it again rather than editing this page. -->
