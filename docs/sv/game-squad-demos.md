---
title: "Squad (replayer)"
nav_order: 40
lang: "sv"
source: game-squad-demos.md
source_hash: "a908f7e6d9c3"
nav_exclude: true
search_exclude: true
---
# Squad (replayer) {#squad-replays}

Efter en match i Squad gör watchern om repriserna som spelet sparat till filer du kan titta på på en karta i 3DHeat-visaren.

*Tekniska detaljer: adapter `squad-demos`, typ [`replay`](sources-and-rules.md); den körs hela tiden (den väntar inte på att ett spel startar) och letar efter ny data var 5 s.*

## Vad som spelas in {#what-is-recorded}

- varje spelares position, kroppens gir och hastighet varje gång servern replikerar den (upp till 8 gånger per sekund), till fots och i markfordon
- varje spelares namn, lag, fraktion och grupp, även vid lagbyten
- inte: helikopters rörelse, kills och utplacerbara föremål – se läsarens README

## Var den kommer ifrån {#where-it-comes-from}

server-demos Squad spelar in med adminkommandot AdminDemoRec: &lt;server>/SquadGame/Saved/Demos/\*.replay, läses av den externa läsaren `heat3d-squad-demo` (exporters/ext/squad-demo)

## Så slår du på det {#how-to-switch-it-on}

spela in på servern: ge adminen behörigheten `demos` i Admins.cfg, kör sedan AdminDemoRec &lt;name> och AdminDemoStop i spelets konsol; kopiera demot hit och installera läsaren: pip install -e &lt;3DHeat>/exporters/ext/squad-demo

Inställningar via miljövariabler:

- `HEAT3D_SQUAD_DEMO`: omvandlarens mapp (en klon eller uppackad utgåva), när den inte är installerad eller bredvid watchern

## Så fungerar det {#how-it-works}

Repriser och demos: det ett spel sparar av en match, omvandlas när matchen är slut.

En repris innehåller allt ett live-gränssnitt håller inne med i onlinespel med flera spelare –
varje spelares position, varje kill där den skedde – och det är en fil som spelet skriver för sina
spelare, så att läsa den rör ingenting i spelet. Watchern tittar i mapparna spelen sparar dem i,
väntar tills en ny fil slutat växa (spelet skriver annars fortfarande på den) och omvandlar den i en
arbetstråd, så att en lång omvandling aldrig stannar resten av watchern.

Första gången en mapp ses noteras de repriser som redan finns i den bara, de omvandlas inte: en
spelare med år av demos skulle annars få watchern upptagen i en dag. `python -m heat3d_watch replays <adapter> [folder]`
omvandlar de befintliga när du begär det.

#### Squad {#squad}

Squads dedikerade servrar spelar in ett demo av en match när en admin med behörigheten `demos` kör
AdminDemoRec &lt;name> (och AdminDemoStop), till `<server>/SquadGame/Saved/Demos/<name>.replay` – en
Unreal Engine-nätverksrepris som innehåller det servern replikerade, varje spelares rörelse
inräknad. Watchern läser dem inte själv: en extern läsare gör det (3DHeat Squad demo-läsare,
`exporters/ext/squad-demo`, kommandot `heat3d-squad-demo`), hållen separat så att ett problem med
den inte påverkar något annat. Den körs på varje nytt demo i de mappar en lokal server skriver till,
eller i en mapp inställningarna lägger till för demos som kopierats från en hyrd server, till
sessionsmappen som `<map>/<match>.parquet` och `<match>.match.json`. Layer, karta, antal spelare och
matchlängd blir sessionens statistik.

Samma modul används även av: [Counter-Strike 2 (replayer)](game-cs2-demos.md), [Dota 2 (replayer)](game-dota-replays.md), [War Thunder (replayer)](game-warthunder-replays.md), [World of Tanks (replayer)](game-wot-replays.md), [World of Warships (replayer)](game-wows-replays.md).

## Positioner och axlar {#positions-and-axes}

| | |
|---|---|
| Positioner registreras | ja |
| Upåtaxel | `z` |
| Enheter | Unreal-enheter (centimeter) |
| Speglad för visaren | ingen |
| Enhetsskala (`scale`: visaren multiplicerar positionerna med den) | 1 |

Dessa läggs i varje sessions `meta.json` (`axes`) och, när sessionen har positioner, i `heat.parquet`s fotnot, så att 3DHeat-visaren vrider och skalar raderna själv – se [Data](the-data.md).

## Flerspelarläge {#multiplayer}

- Markerad som spelad online (`multiplayer`): **ja**. `games --markdown` visar detta som "allowed (reads only what the game publishes)".
- Typ `replay`: den läser bara det spelet eller plattformen lämnar ut (repriser och demos som spelet sparar), så den spelar in även i onlinespel som offline; flaggan avgör bara om minnet någonsin får läsas.
- Minne: läses **aldrig** av denna adapter. Bara `memory`-adaptrar läser minne, och aldrig för ett spel markerat som spelat online – se [Källor och regler](sources-and-rules.md).

## Statistik som registreras {#statistics-recorded}

Statistiknycklar som adapterns kod sätter med namn (varje sessions `stats` i `meta.json` och tabellen `stats` i `watcher.sqlite`):

`layer`, `map`, `match_seconds`, `players`

En nyckel inom klammer fylls i vid körning (`score.{team}` är en nyckel per lag). Nycklar som koden tar från en tabell över spelets fält eller från spelets egna statistiknamn finns inte med i listan; "Vad som spelas in" ovan nämner dem.

## Fullständighet {#completeness}

Omvandlaren som adaptern kör följer 3DHeats [omvandlarregel](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md): det som repriserna innehåller läses eller behålls, aldrig kastas bort – läses in i tabellen och matchdokumentet, allt annat behålls helt i sidofiler bredvid dem och räknas i matchdokumentets `selfCheck.completeness`. Omvandlarens egen dokumentation listar vad den läser, sparar råa och inte kan läsa.

## Verifierad {#verified}

läsaren kontrolleras på publika serverdemos (rörelsen stämmer med hastigheten den bär; varje rads lag stämmer med dess soldats fraktion) och med tester på byggda demos; denna krok med tester med ett stand-in-kommando

## Källa {#source}

[heat3d_watch/adapters/replays.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/replays.py)

<!-- Generated from the adapter by tools/gen_game_pages.py; change the adapter and run it again rather than editing this page. -->
