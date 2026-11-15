---
title: "Counter-Strike 2 (replays)"
nav_order: 8
lang: "nl"
source: game-cs2-demos.md
source_hash: "d115f9085302"
nav_exclude: true
search_exclude: true
---
# Counter-Strike 2 (replays) {#counter-strike-2-replays}

Na een wedstrijd van Counter-Strike 2 zet de watcher de replay die het spel heeft opgeslagen om in bestanden die je op een kaart in de 3DHeat-viewer kunt bekijken.

*Technische details: adapter `cs2-demos`, soort [`replay`](sources-and-rules.md); hij draait altijd (hij wacht niet tot een spel start) en kijkt elke 5 s naar nieuwe gegevens.*

## Wat wordt opgenomen {#what-is-recorded}

- de positie, kijkrichting, gezondheid en geld van elke speler (elke 8e tick)
- kills, doden, schade, granaten, bommen planten en ontmantelen, op de plek waar ze gebeurden
- rondes, score, economie; de scoreboardregel van de ingelogde speler als statistieken

## Waar het vandaan komt {#where-it-comes-from}

demo's die CS2 opslaat: &lt;CS2>/game/csgo/replays/\*.dem (gedownload uit de wedstrijdgeschiedenis) en &lt;CS2>/game/csgo/\*.dem (opgenomen)

## Zo zet je het aan {#how-to-switch-it-on}

download de demo van een wedstrijd in CS2 (Watch > Your Matches), of neem er een op met de console-opdracht `record`

Instellingen via omgevingsvariabelen:

- `HEAT3D_CS2`: de map van 3DHeat CS2, als die niet naast de watcher staat of niet geïnstalleerd is

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

#### Counter-Strike 2 {#counter-strike-2}

CS2 slaat de demo's die een speler downloadt uit de wedstrijdgeschiedenis (tabblad
watch) op in `<CS2>/game/csgo/replays/`, en demo's die met de console-opdracht
`record` zijn opgenomen in `<CS2>/game/csgo/`. Elk bestand wordt omgezet met de eigen
CS2-converter van deze repository (3DHeat CS2, github.com/Holdi601/3DHeat-CS2: de
positie, kijkrichting, gezondheid en het geld van elke speler elke achtste tick; kills,
doden, schade, granaten, bommen planten en ontmantelen op de plek waar ze gebeurden;
rondes, score, economie) naar de sessiemap, als de tabel `<map>/<match>.parquet` en de
samenvatting `<match>.match.json` die de tabbladen Heatmap en Match van de viewer lezen.
Het scoreboard van de wedstrijd wordt de statistiek van de sessie: voor de speler wiens
Steam-account op deze computer is ingelogd (uit Steam's `loginusers.vdf`), onder hun
gewone namen - kills, doden, assists, ADR, KAST, percentage headshots, openingskills,
clutches - en de score en de rondes.

Dezelfde module dient ook: [Dota 2 (replays)](game-dota-replays.md), [osu! (replays)](game-osu-replays.md), [Squad (replays)](game-squad-demos.md), [War Thunder (replays)](game-warthunder-replays.md), [World of Tanks (replays)](game-wot-replays.md), [World of Warships (replays)](game-wows-replays.md).

## Posities en assen {#positions-and-axes}

| | |
|---|---|
| Posities opgenomen | ja |
| Omhoog-as | `z` |
| Eenheden | inches (Source-eenheden) |
| Gespiegeld voor de viewer | `y` |
| Eenheidsschaal (`scale`: de viewer vermenigvuldigt posities hiermee) | 1 |

Deze gaan in het `meta.json` (`axes`) van elke sessie en, als de sessie posities heeft, in de footer van `heat.parquet`, zodat de 3DHeat-viewer de rijen zelf draait en schaalt - zie [De gegevens](the-data.md).

## Multiplayer {#multiplayer}

- Gemarkeerd als online gespeeld (`multiplayer`): **ja**. `games --markdown` toont dit als "allowed (reads only what the game publishes)".
- Soort `replay`: hij leest alleen wat het spel of platform aflevert (replays en demo's die het spel opslaat), dus hij legt ook online spel vast, net als offline spel; de vlag bepaalt alleen of geheugen ooit gelezen mag worden.
- Geheugen: wordt door deze adapter **nooit** gelezen. Alleen `memory`-adapters lezen geheugen, en nooit voor een spel dat als online gespeeld is gemarkeerd - zie [Bronnen en regels](sources-and-rules.md).

## Opgenomen statistieken {#statistics-recorded}

Statistiekensleutels die de code van deze adapter bij naam instelt (de `stats` van elke sessie in `meta.json` en de tabel `stats` van `watcher.sqlite`):

`map`, `rounds`, `score.{team}`, `won`

Een sleutel tussen accolades wordt tijdens het draaien ingevuld (`score.{team}` is één sleutel per team). Sleutels die de code uit een tabel met de velden van het spel of uit de eigen statistiekennamen van het spel haalt, staan niet in deze lijst; "Wat wordt opgenomen" hierboven noemt die.

## Volledigheid {#completeness}

De converter die deze adapter draait volgt de [converterregel](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md) van 3DHeat: wat de replay bevat wordt gelezen of bewaard, nooit weggegooid - gelezen in de tabel en het wedstrijddocument, al het andere bewaard als geheel in bijbestanden ernaast, geteld in `selfCheck.completeness` van het wedstrijddocument. De eigen documentatie van de converter somt op wat hij leest, ruw bewaart en niet kan lezen.

## Getest {#verified}

de converter is getest op echte toernooidemo's; het lezen van de kaart en de statistieken door tests

## Bron {#source}

[heat3d_watch/adapters/replays.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/replays.py)

<!-- Gegenereerd uit de adapter door tools/gen_game_pages.py; wijzig de adapter en draai het opnieuw in plaats van deze pagina te bewerken. -->
