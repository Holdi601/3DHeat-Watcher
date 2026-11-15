---
title: "World of Tanks (replayer)"
nav_order: 47
lang: "sv"
source: game-wot-replays.md
source_hash: "c3fbbeebfee0"
nav_exclude: true
search_exclude: true
---
# World of Tanks (replayer) {#world-of-tanks-replays}

Efter en match i World of Tanks gör watchern om repriserna som spelet sparat till filer du kan titta på på en karta i 3DHeat-visaren.

*Tekniska detaljer: adapter `wot-replays`, typ [`replay`](sources-and-rules.md); den körs hela tiden (den väntar inte på att ett spel startar) och letar efter ny data var 5 s.*

## Vad som spelas in {#what-is-recorded}

- varje fordons position och riktning ungefär 10 gånger per sekund medan inspelningsklienten kände till det: sitt eget lag hela tiden, en fiende medan den är upptäckt
- spelare, lag och fordon (nation:stridsvagn) för var och en; dödsfall där offret föll och kills där dråparen stod, på ungefär en sekund, från resultaten
- kartan; inspelarens kills, skada, överlevnad och resultat som statistik

## Var den kommer ifrån {#where-it-comes-from}

repriser World of Tanks sparar: &lt;World of Tanks>/replays/\*.wotreplay (med stridsinspelning på), omvandlas av den externa omvandlaren `heat3d-wot-replay` (exporters/ext/wot-replay)

## Så slår du på det {#how-to-switch-it-on}

slå på stridsinspelning i World of Tanks inställningar (General > Record battles) och installera omvandlaren: pip install -e &lt;3DHeat>/exporters/ext/wot-replay

Inställningar via miljövariabler:

- `HEAT3D_WOT_REPLAY`: omvandlarens mapp (en klon eller uppackad utgåva), när den inte är installerad eller bredvid watchern

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

#### World of Tanks och World of Warships {#world-of-tanks-and-world-of-warships}

Båda sparar en repris av varje strid till `<spel>/replays/` när inspelning är på (`*.wotreplay`,
`*.wowsreplay`); installationerna hittas via Wargaming Game Centers lista, `C:/Games/World_of_Tanks*` /
`World_of_Warships*`, och Steam. Precis som med War Thunder läser watchern inte filerna själv: en
extern omvandlare gör det för vardera (`exporters/ext/wot-replay`, kommandot `heat3d-wot-replay`;
`exporters/ext/wows-replay`, kommandot `heat3d-wows-replay`), hållna separat så att ett problem med
Wargamings villkor bara berör den omvandlaren. Hittas på PATH, är installerad eller ligger bredvid
watchern, gör den varje ny repris till `<map>/<match>.parquet` och `<match>.match.json` i
sessionsmappen; saknas den säger watchern en gång hur den installeras. Inspelarens rad – fordon eller
fartyg, kills, skada (World of Tanks), om hen överlevde och resultatet (World of Tanks) – blir
sessionens statistik. Vad varje omvandlare läser, och vad den inte gör, står i dess README.

Samma modul används även av: [Counter-Strike 2 (replayer)](game-cs2-demos.md), [Dota 2 (replayer)](game-dota-replays.md), [Squad (replayer)](game-squad-demos.md), [War Thunder (replayer)](game-warthunder-replays.md), [World of Warships (replayer)](game-wows-replays.md).

## Positioner och axlar {#positions-and-axes}

| | |
|---|---|
| Positioner registreras | ja |
| Upåtaxel | `y` |
| Enheter | meter (x öst, y upp, z norr) |
| Speglad för visaren | `z` |
| Enhetsskala (`scale`: visaren multiplicerar positionerna med den) | 1 |

Dessa läggs i varje sessions `meta.json` (`axes`) och, när sessionen har positioner, i `heat.parquet`s fotnot, så att 3DHeat-visaren vrider och skalar raderna själv – se [Data](the-data.md).

## Flerspelarläge {#multiplayer}

- Markerad som spelad online (`multiplayer`): **ja**. `games --markdown` visar detta som "allowed (reads only what the game publishes)".
- Typ `replay`: den läser bara det spelet eller plattformen lämnar ut (repriser och demos som spelet sparar), så den spelar in även i onlinespel som offline; flaggan avgör bara om minnet någonsin får läsas.
- Minne: läses **aldrig** av denna adapter. Bara `memory`-adaptrar läser minne, och aldrig för ett spel markerat som spelat online – se [Källor och regler](sources-and-rules.md).

## Statistik som registreras {#statistics-recorded}

Statistiknycklar som adapterns kod sätter med namn (varje sessions `stats` i `meta.json` och tabellen `stats` i `watcher.sqlite`):

`map`, `survived`, `vehicle`, `won`

En nyckel inom klammer fylls i vid körning (`score.{team}` är en nyckel per lag). Nycklar som koden tar från en tabell över spelets fält eller från spelets egna statistiknamn finns inte med i listan; "Vad som spelas in" ovan nämner dem.

## Fullständighet {#completeness}

Omvandlaren som adaptern kör följer 3DHeats [omvandlarregel](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md): det som repriserna innehåller läses eller behålls, aldrig kastas bort – läses in i tabellen och matchdokumentet, allt annat behålls helt i sidofiler bredvid dem och räknas i matchdokumentets `selfCheck.completeness`. Omvandlarens egen dokumentation listar vad den läser, sparar råa och inte kan läsa.

## Verifierad {#verified}

omvandlaren kontrolleras på publika repriser från flera spelversioner och med tester på byggda repriser; denna krok med tester med ett stand-in-kommando

## Källa {#source}

[heat3d_watch/adapters/replays.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/replays.py)

<!-- Generated from the adapter by tools/gen_game_pages.py; change the adapter and run it again rather than editing this page. -->
