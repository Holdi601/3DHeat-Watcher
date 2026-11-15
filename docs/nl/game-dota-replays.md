---
title: "Dota 2 (replays)"
nav_order: 12
lang: "nl"
source: game-dota-replays.md
source_hash: "958b1e1855e8"
nav_exclude: true
search_exclude: true
---
# Dota 2 (replays) {#dota-2-replays}

Na een wedstrijd Dota 2 zet de watcher de replay die het spel heeft opgeslagen om in bestanden die je op een kaart in de 3DHeat-viewer kunt bekijken.

*Technische details: adapter `dota-replays`, soort [`replay`](sources-and-rules.md); hij draait de hele tijd (hij wacht niet tot een spel start) en zoekt elke 5 s naar nieuwe gegevens.*

## Wat wordt opgenomen {#what-is-recorded}

- de positie, hoogte, gezondheid en het level van elke held, 7,5 keer per seconde terwijl hij leeft
- kills en doden waar ze gebeurden; torens, barakken, Roshan en Tormentors waar ze vielen; wards waar ze geplaatst werden
- de kaartpings, kaarttekeningen en bevelen (verplaatsen, aanvallen, gebruiken, kopen, ...) van elke speler, waar ze heen wezen
- de score en de regel van elke speler; die van de ingelogde speler als statistieken
- al het andere dat de replay bevat, heel bewaard naast de tabel: elk frame en elk netwerkbericht, elke wijziging van een entiteitseigenschap, elk item uit de stringtabel

## Waar het vandaan komt {#where-it-comes-from}

replays die Dota 2 opslaat: &lt;Dota>/game/dota/replays/&lt;match id>.dem (gedownload in de client, of met `dota-replay <match id>`)

## Zo zet je het aan {#how-to-switch-it-on}

download de replay van een wedstrijd in Dota 2, of haal een openbare op: `python -m heat3d_watch dota-replay <match id>`; vereist `pip install gem-dota`

Typ het commando in een terminal die geopend is in de map van de watcher (zie [Voordat je begint](before-you-start.md)). Als het mislukt, zegt de laatste regel waarom. [Installeren en uitvoeren](installing-and-running.md) beschrijft de gewone oorzaken.

## Hoe het werkt {#how-it-works}

Replays en demo's: wat een spel van een wedstrijd opslaat, omgezet zodra de wedstrijd voorbij is.

Een replay bevat alles wat een live-interface in meerspelerspellen achterhoudt - de positie van elke speler, elke kill waar hij gebeurde - en het is een bestand dat het spel voor zijn spelers schrijft. Het lezen ervan raakt dus niets in het spel aan. De watcher kijkt in de mappen waar spellen ze opslaan, wacht tot een nieuw bestand niet meer groeit (het spel schrijft er anders nog in), en zet het om in een werkthread, zodat een lange conversie de rest van de watcher nooit ophoudt.

De eerste keer dat een map gezien wordt, worden de replays die er al in staan alleen genoteerd, niet omgezet: anders zou een speler met jaren aan demo's de watcher een dag lang bezighouden. `python -m heat3d_watch replays <adapter> [folder]` zet de bestaande op verzoek om.

#### Dota 2 {#dota-2}

Dota 2 slaat de replays op die een speler downloadt (de details van een wedstrijd, of Kijken > Replays) in `<Dota>/game/dota/replays/<match id>.dem`. Valve bewaart de replay van elke openbare wedstrijd enkele weken op zijn servers, en `python -m heat3d_watch dota-replay <match id>` haalt er een op via zijn id via OpenDota. Elk wordt gelezen met gem (github.com/whanyu1212/gem-dota, MIT, `pip install gem-dota`) in een eigen proces (`heat3d_watch/decoders/dota_replay.py`): de positie, hoogte, gezondheid, het level, de kijkrichting, mana, ervaring, attributen en items van elke held 7,5 keer per seconde terwijl hij leeft; kills en doden waar ze gebeurden; torens, barakken, Roshan en Tormentors waar ze vielen; elke ward waar hij geplaatst werd en waar hij eindigde; de regels uit het gevechtslogboek over de helden (schade, genezing, vaardigheden, items, aankopen, runes, goud, ervaring, modifiers); en de kaartpings, kaarttekeningen en bevelen van elke speler - in `dota/<match>.parquet`; elke andere eenheid (creeps, summons, illusies, couriers, gebouwen) elke seconde in `<match>.units.parquet`; het hele gevechtslogboek in `<match>.combatlog.parquet`; en de wedstrijd, de chat, de draft, alles wat de parser verder haalt en het eindscorebord van het spel zelf in `<match>.match.json`, in de sessiemap. Al het andere dat de replay bevat, wordt heel naast die bewaard (de converterregel van 3DHeat): elk frame en elk netwerkbericht in `<match>.packets.parquet`, elke wijziging van een entiteitseigenschap in `<match>.entities.parquet`, elk item uit de stringtabel in `<match>.strings.parquet`, geteld in de `selfCheck.completeness` van het wedstrijddocument. Posities zijn de wereldeenheden van Dota, dezelfde die de game-state integration meldt. De scoreboardregel van de ingelogde speler wordt de statistiek van de sessie: kills, deaths, assists, last hits, denies, nettowaarde, GPM, XPM, heldenschade, wards, en of de wedstrijd gewonnen is. Een nieuwe Dota-patch kan de entiteiten van de replay veranderen voordat gem volgt; een replay die gem niet tot het einde kan lezen, wordt tot waar het komt omgezet en in de samenvatting als `incomplete` gemarkeerd.

Dezelfde module levert ook: [Counter-Strike 2 (replays)](game-cs2-demos.md), [osu! (replays)](game-osu-replays.md), [Squad (replays)](game-squad-demos.md), [War Thunder (replays)](game-warthunder-replays.md), [World of Tanks (replays)](game-wot-replays.md), [World of Warships (replays)](game-wows-replays.md).

## Posities en assen {#positions-and-axes}

| | |
|---|---|
| Posities opgenomen | ja |
| Omhoog-as | `z` |
| Eenheden | Dota-wereldeenheden (Hammer-eenheden; de kaart is ongeveer 16.400 breed) |
| Gespiegeld voor de viewer | `y` |
| Eenheidsschaal (`scale`: de viewer vermenigvuldigt posities ermee) | 1 |

Deze gaan in het `meta.json` (`axes`) van elke sessie en, als de sessie posities heeft, in de footer van `heat.parquet`. Zo draait en schaalt de 3DHeat-viewer de rijen zelf - zie [De gegevens](the-data.md).

## Meerspelers {#multiplayer}

- Gemarkeerd als online gespeeld (`multiplayer`): **ja**. `games --markdown` toont dit als "allowed (reads only what the game publishes)".
- Soort `replay`: het leest alleen wat het spel of platform uitgeeft (replays en demo's die het spel opslaat), dus het legt ook online spel vast, net als offline. De vlag bepaalt alleen of geheugen ooit gelezen mag worden.
- Geheugen: wordt door deze adapter **nooit** gelezen. Alleen `memory`-adapters lezen geheugen, en nooit voor een spel dat als online gespeeld is gemarkeerd - zie [Bronnen en regels](sources-and-rules.md).

## Opgenomen statistieken {#statistics-recorded}

Statistiekensleutels die de code van deze adapter bij naam zet (de `stats` van elke sessie in `meta.json` en de tabel `stats` in `watcher.sqlite`):

`duration`, `hero`, `score.{team}`, `team`, `won`

Een sleutel tussen accolades wordt tijdens het draaien ingevuld (`score.{team}` is een sleutel per team). Sleutels die de code uit een tabel met velden van het spel of uit de eigen statistiekennamen van het spel haalt, staan niet in deze lijst; "Wat wordt opgenomen" hierboven noemt die wel.

## Volledigheid {#completeness}

De converter volgt de [converterregel](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md) van 3DHeat: wat de replay bevat, wordt gelezen of bewaard, nooit weggegooid. Naast de tabel wordt alles wat de replay bevat heel bewaard in bijbestanden ernaast in de map `dota/` van de sessie - `<match>.packets.parquet`, `<match>.entities.parquet`, `<match>.strings.parquet` (kolommen `time`, `tick`, `type`, `name`, `entity`, `decoded`, `payload`, waar van toepassing) - en de `selfCheck.completeness` van het wedstrijddocument (`<match>.match.json`) telt elk `type` - `lost` is 0.

**Gelezen**

- de tabel (`dota/<match>.parquet`): de positie, hoogte, gezondheid, het level, de kijkrichting, mana, ervaring, attributen, pantser, snelheid, schade, items en de cursor van de speler, 7,5 keer per seconde; kills, deaths, doelen, wards, de regels uit het gevechtslogboek over helden; kaartpings (`ping`, DOTA_UM_LocationPing), kaarttekeningen (`map_line`, DOTA_UM_MapLine) en elk bevel aan een eenheid (`order`, DOTA_UM_SpectatorPlayerUnitOrders: `other` het type bevel, `value` de vaardigheid- of item-id, `text` de klasse van het doel; op het bevolen punt, anders bij de held)
- `<match>.units.parquet`: elke andere eenheid elke seconde; `<match>.combatlog.parquet`: het hele gevechtslogboek zoals gem het leest, elk veld
- het wedstrijddocument: alles wat gem haalt, en heel de eigen records van de replay - `fileHeader` (DEM_FileHeader), `fileInfo` (DEM_FileInfo: afspeellengte, de naam, held, Steam-id en team van elke speler), `matchDetails` (DOTA_UM_MatchDetails: het eindscorebord van de game coordinator, de cijfers van elke speler, items, schade per type, picks en bans) en `matchMetadata` (DOTA_UM_MatchMetadata)
- `selfCheck.crossCheck`: kills, deaths, assists, level, last hits en denies zoals uit de stream gelezen, vergeleken met `matchDetails`, per speler

**Heel bewaard**

- `<match>.packets.parquet`: elk frame dat geen pakket is (`type` `frame <n>`) en elk netwerkbericht (`message <n>`, `name` van Valve), heel in `payload`, in bestandsvolgorde (`seq`, `frame`), met `decoded` het protobuf als JSON (een bytes-veld als zijn lengte); elk berichttype gedecodeerd: svc_PacketEntities (de entiteitenstroom), DOTA_UM_SpectatorPlayerUnitOrders, UM_ParticleManager, de berichten van het gevechtslogboek, GE_SosStartSoundEvent, DOTA_UM_TE_\* (projectielen, animaties, bloed), DOTA_UM_OverheadEvent, DOTA_UM_UnitEvent, svc_UpdateStringTable, net_Tick, ...; de send-tabellen, klassenlijst en serverinfo die een latere entiteitsdecoder nodig heeft zitten erbij
- `<match>.entities.parquet`: elke eigenschap van elke entiteit telkens als ze veranderde (`type` de eigenschap, `name` de klasse, `entity` de index; `value`, `vector` of `decoded`), de hele toestand bij het aanmaken, en elk aanmaken, binnenkomen, verlaten en verwijderen - miljoenen rijen voor een hele wedstrijd
- `<match>.strings.parquet`: elk item uit de stringtabel van elke update en elke volledige momentopname, de waarde heel; `userinfo`, `ActiveModifiers` en `EconItems` gedecodeerd uit hun protobufs
- `selfCheck.completeness` in het wedstrijddocument telt frames en berichten op hun Valve-naam, items uit het gevechtslogboek (`combatlog <type>`), spelgebeurtenissen (`gameevent <name>`), items uit de stringtabel (`stringtable <name>`) en entiteitsupdates (`entity <class>`); een paar worden alleen ruw bewaard (volledige momentopnamen van entiteiten die gem overslaat omdat het ze uit de delta's opbouwt, en items van tabellen waarvan de waarden niets leest), lost 0

**Niet beschikbaar**

- spraak: de replay heeft de spraakinstelling maar geen spraakdata
- namen achter hashes en id's: geluiden en deeltjes worden benoemd met hashes van de bestanden van het spel, vaardigheden met id's; de replay draagt de namen niet (items worden benoemd via de catalogus van gem waar die er een heeft)
- alles wat alleen de eigen clients van de spelers wisten (hun camera, hun scherm) buiten wat de server uitzond; de cursor en elk bevel zitten erin

**Grootte**: de bijbestanden samen zijn iets groter dan de replay zelf, de pakketten en de entiteiten het grootst; een hele wedstrijd duurt één of twee minuten in één proces

## Geverifieerd {#verified}

gecontroleerd op de replay van een openbare wedstrijd: kills, deaths, assists, level, last hits en denies komen overeen met het eigen eindscorebord van het spel voor alle tien spelers; elk bericht in het pakketbijbestand wordt byte voor byte opnieuw geserialiseerd; de tabel en statistieken met tests op synthetische data

## Bron {#source}

[heat3d_watch/adapters/replays.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/replays.py)

<!-- Gegenereerd uit de adapter door tools/gen_game_pages.py; wijzig de adapter en voer het opnieuw uit in plaats van deze pagina te bewerken. -->
