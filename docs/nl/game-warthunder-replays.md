---
title: "War Thunder (replays)"
nav_order: 46
lang: "nl"
source: game-warthunder-replays.md
source_hash: "81f03926431d"
nav_exclude: true
search_exclude: true
---
# War Thunder (replays) {#war-thunder-replays}

Na een gevecht in War Thunder zet de watcher de replay die het spel heeft opgeslagen om in bestanden die je op een kaart in de 3DHeat-viewer kunt bekijken.

*Technische details: adapter `warthunder-replays`, soort [`replay`](sources-and-rules.md); hij draait altijd (hij wacht niet tot een spel start) en kijkt elke 5 s naar nieuwe gegevens.*

## Wat wordt opgenomen {#what-is-recorded}

- de positie en houding van elk vliegtuig ongeveer 4 keer per seconde (zoveel als de replay bevat)
- posities van grondeenheden uit de grondsynchronisatie van de replay (in replays van 2026; niet in die van 2025)
- wie elke eenheid was (speler, voertuig-id, team) waar een kill of treffer haar noemt; kills, doden en treffers op de plek waar ze gebeurden; chat; de kaart
- de kills, doden, score en veroveringen van de maker van de replay als statistieken

## Waar het vandaan komt {#where-it-comes-from}

replays die War Thunder opslaat: &lt;War Thunder>/Replays/\*.wrpl (met replays opslaan aan), omgezet door de externe converter `heat3d-wt-replay` (exporters/ext/warthunder-replay)

## Zo zet je het aan {#how-to-switch-it-on}

zet in de opties van War Thunder het opslaan van replays aan en installeer de converter: pip install -e &lt;3DHeat>/exporters/ext/warthunder-replay

Instellingen via omgevingsvariabelen:

- `HEAT3D_WT_REPLAY`: de map van de converter (een kloon of uitgepakte release), als die niet geïnstalleerd is of niet naast de watcher staat

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

#### War Thunder {#war-thunder}

War Thunder slaat een replay van elk gevecht op in `<War Thunder>/Replays/*.wrpl`
wanneer het opslaan van replays aan staat in de opties. De watcher leest die zelf niet:
een externe converter doet dat (de 3DHeat War Thunder-replayconverter,
`exporters/ext/warthunder-replay`, opdracht `heat3d-wt-replay`), apart gehouden zodat
een probleem daarmee niets anders raakt. Als de opdracht op het PAD staat, of het
pakket is geïnstalleerd of staat naast de watcher, wordt elke nieuwe replay erdoor
gehaald en levert hij de sessiemap op als `<map>/<match>.parquet` en `<match>.match.json`;
als dat niet zo is, zegt de watcher één keer hoe de converter geïnstalleerd wordt en
laat de map met rust. Wat de converter wel en niet leest, staat in zijn README. De
uitslagregel van de maker van de replay - kills, grondkills, doden, assists, score,
veroveringen - wordt de statistiek van de sessie.

Dezelfde module dient ook: [Counter-Strike 2 (replays)](game-cs2-demos.md), [Dota 2 (replays)](game-dota-replays.md), [osu! (replays)](game-osu-replays.md), [Squad (replays)](game-squad-demos.md), [World of Tanks (replays)](game-wot-replays.md), [World of Warships (replays)](game-wows-replays.md).

## Posities en assen {#positions-and-axes}

| | |
|---|---|
| Posities opgenomen | ja |
| Omhoog-as | `y` |
| Eenheden | meter (x oost, y omhoog, z noord) |
| Gespiegeld voor de viewer | `z` |
| Eenheidsschaal (`scale`: de viewer vermenigvuldigt posities hiermee) | 1 |

Deze gaan in het `meta.json` (`axes`) van elke sessie en, als de sessie posities heeft, in de footer van `heat.parquet`, zodat de 3DHeat-viewer de rijen zelf draait en schaalt - zie [De gegevens](the-data.md).

## Multiplayer {#multiplayer}

- Gemarkeerd als online gespeeld (`multiplayer`): **ja**. `games --markdown` toont dit als "allowed (reads only what the game publishes)".
- Soort `replay`: hij leest alleen wat het spel of platform aflevert (replays en demo's die het spel opslaat), dus hij legt ook online spel vast, net als offline spel; de vlag bepaalt alleen of geheugen ooit gelezen mag worden.
- Geheugen: wordt door deze adapter **nooit** gelezen. Alleen `memory`-adapters lezen geheugen, en nooit voor een spel dat als online gespeeld is gemarkeerd - zie [Bronnen en regels](sources-and-rules.md).

## Opgenomen statistieken {#statistics-recorded}

Statistiekensleutels die de code van deze adapter bij naam instelt (de `stats` van elke sessie in `meta.json` en de tabel `stats` van `watcher.sqlite`):

`map`

Een sleutel tussen accolades wordt tijdens het draaien ingevuld (`score.{team}` is één sleutel per team). Sleutels die de code uit een tabel met de velden van het spel of uit de eigen statistiekennamen van het spel haalt, staan niet in deze lijst; "Wat wordt opgenomen" hierboven noemt die.

## Volledigheid {#completeness}

De converter die deze adapter draait volgt de [converterregel](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md) van 3DHeat: wat de replay bevat wordt gelezen of bewaard, nooit weggegooid - gelezen in de tabel en het wedstrijddocument, al het andere bewaard als geheel in bijbestanden ernaast, geteld in `selfCheck.completeness` van het wedstrijddocument. De eigen documentatie van de converter somt op wat hij leest, ruw bewaart en niet kan lezen.

## Getest {#verified}

de converter is gecontroleerd op openbare replays uit verschillende spelversies (kills en namen kloppen met de uitslagen) en door tests op gebouwde replays; deze hook door tests met een vervangende opdracht

## Bron {#source}

[heat3d_watch/adapters/replays.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/replays.py)

<!-- Gegenereerd uit de adapter door tools/gen_game_pages.py; wijzig de adapter en draai het opnieuw in plaats van deze pagina te bewerken. -->
