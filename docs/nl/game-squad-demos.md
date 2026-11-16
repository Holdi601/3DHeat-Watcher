---
title: "Squad (replays)"
nav_order: 41
lang: "nl"
source: game-squad-demos.md
source_hash: "82c24e6df01c"
nav_exclude: true
search_exclude: true
---
# Squad (replays) {#squad-replays}

Na een wedstrijd van Squad zet de watcher de replay die het spel heeft opgeslagen om in bestanden die je op een kaart in de 3DHeat-viewer kunt bekijken.

*Technische details: adapter `squad-demos`, soort [`replay`](sources-and-rules.md); hij draait altijd (hij wacht niet tot een spel start) en kijkt elke 5 s naar nieuwe gegevens.*

## Wat wordt opgenomen {#what-is-recorded}

- de positie, de draaihoek (yaw) en de snelheid van elke speler, elke keer dat de server die doorgeeft (tot 8 keer per seconde), te voet en in grondvoertuigen
- de naam, het team, de factie en de squad van elke speler, met bijhouding van teamwisselingen
- niet: de beweging van helikopters, kills en plaatsbare voorwerpen - zie de README van de lezer

## Waar het vandaan komt {#where-it-comes-from}

serverdemo's die Squad opneemt met het beheerdersbevel AdminDemoRec: &lt;server>/SquadGame/Saved/Demos/\*.replay, gelezen door de externe lezer `heat3d-squad-demo` (exporters/ext/squad-demo)

## Zo zet je het aan {#how-to-switch-it-on}

neem op de server op: geef de beheerder de bevoegdheid `demos` in Admins.cfg, en typ daarna AdminDemoRec &lt;naam> en AdminDemoStop in de console van het spel; kopieer de demo hiernaartoe en installeer de lezer: pip install -e &lt;3DHeat>/exporters/ext/squad-demo

Instellingen via omgevingsvariabelen:

- `HEAT3D_SQUAD_DEMO`: de map van de converter (een kloon of uitgepakte release), als die niet geïnstalleerd is of niet naast de watcher staat

## Hoe het werkt {#how-it-works}

Replays en demo's: wat een spel van een wedstrijd opslaat, na afloop van de wedstrijd omgezet.

Een replay bevat alles wat een live-interface in multiplayerspellen achterhoudt -
de positie van elke speler, elke kill op de plek waar die gebeurde - en het is een
bestand dat het spel voor zijn spelers schrijft, dus het lezen ervan raakt het spel
niet aan. De watcher kijkt in de mappen waar spellen ze opslaan, wacht tot een nieuw
bestand niet meer groeit (het spel schrijft er anders nog in), en zet het om in een
werkthread, zodat een lange omzetting de rest van de watcher nooit ophoudt.

De eerste keer dat een map wordt gezien, worden de replays die er al in staan alleen
genoteerd, niet omgezet: een speler met jaren aan demo's zou de watcher anders een
dag lang bezig houden. `python -m heat3d_watch replays <adapter> [folder]` zet de
bestaande replays op verzoek om.

#### Squad {#squad}

De dedicated servers van Squad nemen een demo van een wedstrijd op wanneer een
beheerder met de bevoegdheid `demos` AdminDemoRec &lt;naam> uitvoert (en AdminDemoStop),
in `<server>/SquadGame/Saved/Demos/<naam>.replay` - een netwerkreplay van de Unreal
Engine met wat de server heeft doorgegeven, inclusief elke beweging van elke speler.
De watcher leest die zelf niet: een externe lezer doet dat (de 3DHeat Squad-demolezer,
`exporters/ext/squad-demo`, opdracht `heat3d-squad-demo`), een eigen project.
Hij draait op elke nieuwe demo in de mappen waar
een lokale server naartoe schrijft, of in een map die de instellingen toevoegen voor
demo's die van een gehuurde server zijn gekopieerd, en levert de sessiemap op als
`<map>/<match>.parquet` en `<match>.match.json`. De laag, de kaart, het aantal spelers
en de wedstrijdduur worden de statistieken van de sessie.

Dezelfde module dient ook: [Counter-Strike 2 (replays)](game-cs2-demos.md), [Dota 2 (replays)](game-dota-replays.md), [osu! (replays)](game-osu-replays.md), [War Thunder (replays)](game-warthunder-replays.md), [World of Tanks (replays)](game-wot-replays.md), [World of Warships (replays)](game-wows-replays.md).

## Posities en assen {#positions-and-axes}

| | |
|---|---|
| Posities opgenomen | ja |
| Omhoog-as | `z` |
| Eenheden | Unreal-eenheden (centimeter) |
| Gespiegeld voor de viewer | geen |
| Eenheidsschaal (`scale`: de viewer vermenigvuldigt posities hiermee) | 1 |

Deze gaan in het `meta.json` (`axes`) van elke sessie en, als de sessie posities heeft, in de footer van `heat.parquet`, zodat de 3DHeat-viewer de rijen zelf draait en schaalt - zie [De gegevens](the-data.md).

## Multiplayer {#multiplayer}

- Gemarkeerd als online gespeeld (`multiplayer`): **ja**. `games --markdown` toont dit als "allowed (reads only what the game publishes)".
- Soort `replay`: hij leest alleen wat het spel of platform aflevert (replays en demo's die het spel opslaat), dus hij legt ook online spel vast, net als offline spel; de vlag bepaalt alleen of geheugen ooit gelezen mag worden.
- Geheugen: wordt door deze adapter **nooit** gelezen. Alleen `memory`-adapters lezen geheugen, en nooit voor een spel dat als online gespeeld is gemarkeerd - zie [Bronnen en regels](sources-and-rules.md).

## Opgenomen statistieken {#statistics-recorded}

Statistiekensleutels die de code van deze adapter bij naam instelt (de `stats` van elke sessie in `meta.json` en de tabel `stats` van `watcher.sqlite`):

`layer`, `map`, `match_seconds`, `players`

Een sleutel tussen accolades wordt tijdens het draaien ingevuld (`score.{team}` is één sleutel per team). Sleutels die de code uit een tabel met de velden van het spel of uit de eigen statistiekennamen van het spel haalt, staan niet in deze lijst; "Wat wordt opgenomen" hierboven noemt die.

## Volledigheid {#completeness}

De converter die deze adapter draait volgt de [converterregel](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md) van 3DHeat: wat de replay bevat wordt gelezen of bewaard, nooit weggegooid - gelezen in de tabel en het wedstrijddocument, al het andere bewaard als geheel in bijbestanden ernaast, geteld in `selfCheck.completeness` van het wedstrijddocument. De eigen documentatie van de converter somt op wat hij leest, ruw bewaart en niet kan lezen.

## Getest {#verified}

de lezer is gecontroleerd op openbare serverdemo's (de beweging klopt met de snelheid die hij meedraagt; het team van elke rij klopt met de factie van de soldaat) en door tests op gebouwde demo's; deze hook door tests met een vervangende opdracht

## Bron {#source}

[heat3d_watch/adapters/replays.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/replays.py)

<!-- Gegenereerd uit de adapter door tools/gen_game_pages.py; wijzig de adapter en draai het opnieuw in plaats van deze pagina te bewerken. -->
