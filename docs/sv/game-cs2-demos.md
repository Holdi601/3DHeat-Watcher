---
title: "Counter-Strike 2 (replayer)"
nav_order: 8
lang: "sv"
source: game-cs2-demos.md
source_hash: "82fe00f0f2f0"
nav_exclude: true
search_exclude: true
---
# Counter-Strike 2 (replayer) {#counter-strike-2-replays}

Efter en match i Counter-Strike 2 gör watchern om repriserna som spelet sparat till filer du kan titta på på en karta i 3DHeat-visaren.

*Tekniska detaljer: adapter `cs2-demos`, typ [`replay`](sources-and-rules.md); den körs hela tiden (den väntar inte på att ett spel startar) och letar efter ny data var 5 s.*

## Vad som spelas in {#what-is-recorded}

- varje spelares position, siktriktning, hälsa och pengar (var åttonde tick)
- kills, dödsfall, skada, granater, bombplanteringar och bombavbrytningar där de skedde
- rundor, poäng, ekonomi; den inloggade spelarens resultatrad som statistik

## Var den kommer ifrån {#where-it-comes-from}

demos CS2 sparar: &lt;CS2>/game/csgo/replays/\*.dem (nedladdade från matchhistoriken) och &lt;CS2>/game/csgo/\*.dem (inspelade)

## Så slår du på det {#how-to-switch-it-on}

ladda ner en matchs demo i CS2 (Watch > Your Matches), eller spela in en med konsolkommandot `record`

Inställningar via miljövariabler:

- `HEAT3D_CS2`: mappen med 3DHeat CS2, när den inte ligger bredvid watchern eller är installerad

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

#### Counter-Strike 2 {#counter-strike-2}

CS2 sparar de demos en spelare laddar ner från matchhistoriken (fliken Watch) till
`<CS2>/game/csgo/replays/` och de som spelats in med konsolkommandot `record` till
`<CS2>/game/csgo/`. Varje fil omvandlas med repots egen CS2-omvandlare (3DHeat CS2,
github.com/Holdi601/3DHeat-CS2: varje spelares position, siktriktning, hälsa och pengar var
åttonde tick; kills, dödsfall, skada, granater, bombplanteringar och bombavbrytningar där de skedde;
rundor, poäng, ekonomi) till sessionsmappen, som tabellen `<map>/<match>.parquet` och sammanfattningen
`<match>.match.json` som visarens flikar Värmekarta och Match läser. Matchens scoreboard blir sessionens
statistik: för spelaren vars Steam-konto är inloggat på den här datorn (från Steams `loginusers.vdf`)
under dess vanliga namn – kills, dödsfall, assists, ADR, KAST, andel huvudskott, öppningsdödsfall,
clutches – samt poäng och rundor.

Samma modul används även av: [Dota 2 (replayer)](game-dota-replays.md), [Squad (replayer)](game-squad-demos.md), [War Thunder (replayer)](game-warthunder-replays.md), [World of Tanks (replayer)](game-wot-replays.md), [World of Warships (replayer)](game-wows-replays.md).

## Positioner och axlar {#positions-and-axes}

| | |
|---|---|
| Positioner registreras | ja |
| Upåtaxel | `z` |
| Enheter | tum (Source-enheter) |
| Speglad för visaren | `y` |
| Enhetsskala (`scale`: visaren multiplicerar positionerna med den) | 1 |

Dessa läggs i varje sessions `meta.json` (`axes`) och, när sessionen har positioner, i `heat.parquet`s fotnot, så att 3DHeat-visaren vrider och skalar raderna själv – se [Data](the-data.md).

## Flerspelarläge {#multiplayer}

- Markerad som spelad online (`multiplayer`): **ja**. `games --markdown` visar detta som "allowed (reads only what the game publishes)".
- Typ `replay`: den läser bara det spelet eller plattformen lämnar ut (repriser och demos som spelet sparar), så den spelar in även i onlinespel som offline; flaggan avgör bara om minnet någonsin får läsas.
- Minne: läses **aldrig** av denna adapter. Bara `memory`-adaptrar läser minne, och aldrig för ett spel markerat som spelat online – se [Källor och regler](sources-and-rules.md).

## Statistik som registreras {#statistics-recorded}

Statistiknycklar som adapterns kod sätter med namn (varje sessions `stats` i `meta.json` och tabellen `stats` i `watcher.sqlite`):

`map`, `rounds`, `score.{team}`, `won`

En nyckel inom klammer fylls i vid körning (`score.{team}` är en nyckel per lag). Nycklar som koden tar från en tabell över spelets fält eller från spelets egna statistiknamn finns inte med i listan; "Vad som spelas in" ovan nämner dem.

## Fullständighet {#completeness}

Omvandlaren som adaptern kör följer 3DHeats [omvandlarregel](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md): det som repriserna innehåller läses eller behålls, aldrig kastas bort – läses in i tabellen och matchdokumentet, allt annat behålls helt i sidofiler bredvid dem och räknas i matchdokumentets `selfCheck.completeness`. Omvandlarens egen dokumentation listar vad den läser, sparar råa och inte kan läsa.

## Verifierad {#verified}

omvandlaren testas på riktiga turneringsdemos; mappbevakningen och statistiken med tester

## Källa {#source}

[heat3d_watch/adapters/replays.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/replays.py)

<!-- Generated from the adapter by tools/gen_game_pages.py; change the adapter and run it again rather than editing this page. -->
