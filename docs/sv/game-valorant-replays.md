---
title: "VALORANT (repriser)"
nav_order: 44
lang: "sv"
source: game-valorant-replays.md
source_hash: "a2c4144797e9"
nav_exclude: true
search_exclude: true
---
# VALORANT (repriser) {#valorant-replays}

Efter en match i VALORANT gör watchern om den repris spelet sparade till filer som du kan titta på som statistik och en tidslinje.

*Tekniska detaljer: adapter `valorant-replays`, slag [`replay`](sources-and-rules.md); den körs hela tiden (den väntar inte på att ett spel startar) och letar efter ny data var 5 s.*

## Vad som spelas in {#what-is-recorded}

- kartan, matchens id och de agenter som valts; reprisens infoblock (längd, versioner, namn, inspelningstid, komprimerings- och krypteringsflaggor)
- serverns händelsetidslinje: dödsfall (dödare och offer som nätverks-id), rundor som startar, spikar planterade, avinaktiverade och exploderande, använda ultimate-förmågor, sidbyten - var och en med sitt id och sin metadata
- varje chunk i filen sparad helt i heat.raw.parquet; inte avkodat: positioner, namn eller poäng - de finns i den förvrängda strömmen

## Var datan kommer ifrån {#where-it-comes-from}

reprisar som VALORANT sparar: %LOCALAPPDATA%/VALORANT/Saved/Demos/\*.vrf (bara de delar som inte är förvrängda)

## Så slår du på det {#how-to-switch-it-on}

spara en repris i VALORANT (karriär > match > ladda ner repris) och installera läsaren: github.com/Holdi601/3DHeat-Ext-Riot (`heat3d-riot-replays`)

Inställningar från miljövariabler:

- `HEAT3D_RIOT_REPLAYS`: läsarens mapp (en klon eller ett uppackat release), när den inte är installerad eller bredvid watchern

## Så fungerar det {#how-it-works}

League of Legends- och Valorant-repriser: vad av dem som kan läsas som de är.

Båda spelen sparar reprisar på spelarens disk, och båda skyddar det som finns
inuti: den ögonblick-för-ögonblick-speldatan är förvrängd, och olika för varje patch,
för att hindra att den används för att fuska. Den delen avkodas inte
någonstans i 3DHeat. Vad varje fil bär öppet
läses, och resten sparas som det är: varje del av filen, helt, i sessionens
`heat.raw.parquet` (3DHeats konverterarregel, docs/converters.md i
visarens förråd), räknad i meta.json:s `selfCheck.completeness`.

watchern läser inte filerna själv: en extern läsare gör det (3DHeat
Riot, github.com/Holdi601/3DHeat-Ext-Riot, `exporters/ext/riot-replays`,
kommandot `heat3d-riot-replays`), ett eget projekt. Hittas den på PATH, är installerad eller bredvid watchern, läser den
varje ny repris; saknas den säger watchern en gång hur den installeras. Vad
den läser sparar watchern i sessionen; Match-V5-tidslinjen nedan hämtas
av watchern själv, eftersom den inte finns i filen.

#### Valorant (.vrf) {#valorant-vrf}

`%LOCALAPPDATA%\VALORANT\Saved\Demos\*.vrf`, en lokal Unreal Engine-repris. Det öppna:
reprisens infoblock (längd, nätverksversion, changelist, dess namn, när
den spelades in, om den är komprimerad eller krypterad), kartan, matchens id och
de valda agenterna (i rubriken), och serverns egen händelsetidslinje - dödsfall
(dödare och offer som nätverks-id, inte namn), rundor som startar, spikar planterade,
avinaktiverade och exploderande, använda ultimate-förmågor, sidbyten - var och en med sin tid,
id och metadata. Positioner, namn, poäng och allt annat finns i den förvrängda
strömmen (repriens data- och checkpoint-chunkar), som sparas helt och inte läses.

Samma modul används också av: [League of Legends (repriser)](game-lol-replays.md).

## Positioner och axlar {#positions-and-axes}

| | |
|---|---|
| Positioner sparas | nej |
| Upp-axel | `z` |
| Enheter | VALORANT-världsenheter |
| Speglad för visaren | ingen |
| Enhetsskala (`scale`: visaren multiplicerar positionerna med den) | 1 |

Dessa läggs i varje sessions `meta.json` (`axes`) och, när sessionen har positioner, i `heat.parquet`:s fotnot, så att 3DHeat-visaren vrider och skalar raderna själv - se [Datan](the-data.md).

## Flerspelarläge {#multiplayer}

- Markerat som spelat online (`multiplayer`): **ja**. `games --markdown` visar detta som "tillåtet (läser bara det spelet publicerar)".
- Slag `replay`: den läser bara det spelet eller plattformen lämnar ut (repriser och demon som spelet sparar), så den spelar in även i onlinespel som offline; flaggan avgör bara om minne någonsin får läsas.
- Minne: **aldrig** läst av den här adaptern. Bara `memory`-adaptrar läser minne, och aldrig för ett spel som är markerat som spelat online - se [Källor och regler](sources-and-rules.md).

## Statistik som sparas {#statistics-recorded}

Statistiknycklar som den här adapterns kod sätter med namn (varje sessions `stats` i `meta.json` och tabellen `stats` i `watcher.sqlite`):

`kills_in_match`, `map`, `match_seconds`, `rounds`, `spikes_planted`

En nyckel i klammer fylls i vid körning (`score.{team}` är en nyckel per lag). Nycklar som koden tar från en tabell med spelets fält eller från spelets egna statistiknamn finns inte i listan; "Vad som spelas in" ovan nämner dem.

## Fullständighet {#completeness}

watchern följer 3DHeats [konverterarregel](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md): det källan innehåller läses eller sparas, aldrig slängs. Utöver raderna sparas varje paket, sida, rad eller svar som adaptern tar emot helt i sessionens `heat.raw.parquet` (kolumnerna `time`, `ms`, `type`, `used`, `payload`, `text` och sedan eventuella fält som sparats med namn; `used` markerar det som också blev rader), och `meta.json`:s `selfCheck.completeness` räknar varje `type` - `lost` är 0.

**Läses**

- infoblocket, varje fält (meta.json `vrf`): filversion, egna versioner, längd, nätverksversion, changelist, namn, livflagga, inspelningstid, flaggor för komprimerad och krypterad, nyckeln så som den är lagrad
- rubrikchunken: kartan, matchens id och de valda agenterna (igenkända på sin form)
- varje händelsechunk: id, grupp, metadata, start- och sluttid, och ur dess data händelsens namn, dess tid i sekunder och siffrorna före den (dödare och offer som nätverks-id) - en rad vardera

**Sparas råa**

- varje chunk helt, i filens ordning (`offset`), så att delarna är filen: `info`, `header`, `event <grupp>`, `replay_data`, `checkpoint`, `chunk <n>` för en typ som layouten inte namnger, `trailing` för byte efter den sista hela chunken

**Finns inte**

- positioner, namn, poäng, förmågor, varje bildruta från spelet: repriens data- och checkpoint-chunkar är förvrängda. Sparat helt, inte läst
- en krypterad repris innehåll: genomgången och sparad helt, inget läst inuti

**Storlek**: den råa sidofilen är ungefär reprisens egen storlek: den förvrängda strömmen komprimeras inte

## Verifierat {#verified}

läsaren (heat3d-riot-replays) är byggd efter containerlayouten som dokumenterats av vrfkit (Apache-2.0); ej testad på en riktig repris, ingen fanns tillgänglig - kontrollerar innan den läser och hoppar över det som inte stämmer

## Källa {#source}

[heat3d_watch/adapters/riot_replays.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/riot_replays.py)

<!-- Generated from the adapter by tools/gen_game_pages.py; change the adapter and run it again rather than editing this page. -->
