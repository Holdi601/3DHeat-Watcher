---
title: "League of Legends (repriser)"
nav_order: 30
lang: "sv"
source: game-lol-replays.md
source_hash: "6a86dc8a45bb"
nav_exclude: true
search_exclude: true
---
# League of Legends (repriser) {#league-of-legends-replays}

Efter en match i League of Legends gör watchern om den repris spelet sparade till filer som du kan titta på på en karta i 3DHeat-visaren.

*Tekniska detaljer: adapter `lol-replays`, slag [`replay`](sources-and-rules.md); den körs hela tiden (den väntar inte på att ett spel startar) och letar efter ny data var 5 s.*

## Vad som spelas in {#what-is-recorded}

- varje spelares champion, roll, lag, dödssiffror, dödsfall, assists, guld, skada mot champions och resultat, och varje annan siffra i slutrutans poänglista
- din egen rad som statistik, och dina rader märkta som dina (meta.json `player`), med ditt Riot-ID i inställningarna
- med din egen Riot API-nyckel: varje spelares position varje minut med minutens statistik, och varje händelse i tidslinjen (dödsfall där de skedde, byggnader, monster, vakter, föremål, förmågor), vid väggklockans tid som tidslinjen anger
- varje del av reprisfilen sparad helt i heat.raw.parquet; inte avkodat: spelet ögonblick för ögonblick, som är krypterat och förvrängt mot fusk

## Var datan kommer ifrån {#where-it-comes-from}

reprisar som League-klienten sparar: %USERPROFILE%/Documents/League of Legends/Replays/\*.rofl (bara den enkla metadata från slutet av matchen); med din egen Riot API-nyckel, matchens officiella tidslinje från Riots Match-V5-API

## Så slår du på det {#how-to-switch-it-on}

spara en repris i League-klienten (matchhistorik > ladda ner) och installera läsaren: github.com/Holdi601/3DHeat-Ext-Riot (`heat3d-riot-replays`); för positioner sätt riot_api_key och riot_platform med `config --set`

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

#### League of Legends (.rofl) {#league-of-legends-rofl}

`%USERPROFILE%\Documents\League of Legends\Replays\*.rofl`. Båda containerversionerna bär
slutrutans poänglista som ren JSON (`statsJson`): för var och en av
de tio spelarna champion, dödsfall, dödsfall, assists, guld, skada mot
champions, föremål, lag, roll, vinst, deras Riot-ID, och varje annan siffra som
spelet summerar (över hundra per spelare); alla blir spelarens
`player_result`-rad. ROFL1 (patch 14.9 och tidigare) har den efter en fast rubrik
(`RIOT\0\0`, en 256 byte lång signatur, sedan längderna); ROFL2 (14.11 och senare,
`RIOT\2\0`) i slutet av filen, dess längd i de sista fyra byten (uppgett
av en Riot-ingenjör, ReplayBook issue 299). ROFL1:s nyttolastrubrik (spel-id,
längd, antal chunkar och keyframes, chunknyckelns längd) och dess tabell över
chunkar (id, typ, längd, nästa chunk, offset) ligger öppet och läses; själva
chunkarna är krypterade och sparas helt, oläst.

Positionerna kommer inte från filen. Med en Riot-utvecklarnyckel som spelaren
själv har (`riot_api_key` i inställningarna; en personlig nyckel är avsedd just för detta,
"visa (egen) spelarstatistik"), hämtas matchens officiella tidslinje från
Riots Match-V5-API: varje spelares position en gång per minut med allt minutens bild säger om
dem (guld, erfarenhet, nivå, minions, champion- och skadestatistik), och varje
händelse i tidslinjen - dödsfall, byggnader, elitmonster, vakter, föremål, förmågor, nivåer -
en rad vardera, där den hände när den har en plats. Utan nyckel hämtas inget och skickas inget.

Samma modul används också av: [VALORANT (repriser)](game-valorant-replays.md).

## Positioner och axlar {#positions-and-axes}

| | |
|---|---|
| Positioner sparas | ja |
| Upp-axel | `y` |
| Enheter | Summoner's Rift kartenheter (ungefär 15000 över) |
| Speglad för visaren | ingen |
| Enhetsskala (`scale`: visaren multiplicerar positionerna med den) | 1 |

Dessa läggs i varje sessions `meta.json` (`axes`) och, när sessionen har positioner, i `heat.parquet`:s fotnot, så att 3DHeat-visaren vrider och skalar raderna själv - se [Datan](the-data.md).

## Flerspelarläge {#multiplayer}

- Markerat som spelat online (`multiplayer`): **ja**. `games --markdown` visar detta som "tillåtet (läser bara det spelet publicerar)".
- Slag `replay`: den läser bara det spelet eller plattformen lämnar ut (repriser och demon som spelet sparar), så den spelar in även i onlinespel som offline; flaggan avgör bara om minne någonsin får läsas.
- Minne: **aldrig** läst av den här adaptern. Bara `memory`-adaptrar läser minne, och aldrig för ett spel som är markerat som spelat online - se [Källor och regler](sources-and-rules.md).

## Statistik som sparas {#statistics-recorded}

Statistiknycklar som den här adapterns kod sätter med namn (varje sessions `stats` i `meta.json` och tabellen `stats` i `watcher.sqlite`):

`champion`, `game_seconds`, `won`

En nyckel i klammer fylls i vid körning (`score.{team}` är en nyckel per lag). Nycklar som koden tar från en tabell med spelets fält eller från spelets egna statistiknamn finns inte i listan; "Vad som spelas in" ovan nämner dem.

## Fullständighet {#completeness}

watchern följer 3DHeats [konverterarregel](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md): det källan innehåller läses eller sparas, aldrig slängs. Utöver raderna sparas varje paket, sida, rad eller svar som adaptern tar emot helt i sessionens `heat.raw.parquet` (kolumnerna `time`, `ms`, `type`, `used`, `payload`, `text` och sedan eventuella fält som sparats med namn; `used` markerar det som också blev rader), och `meta.json`:s `selfCheck.completeness` räknar varje `type` - `lost` är 0.

**Läses**

- metadata-JSON:en: spelets längd, version, sista chunk- och keyframe-id, och `statsJson` - varje fält i varje spelares poänglista på deras `player_result`-rad (siffror givna som text läses som tal)
- ROFL1: längdblocket, nyttolastrubriken (spel-id, spelets längd, antal keyframes och chunkar, start- och spelstartens chunk-id, keyframe-intervall, chunknyckeln så som den är lagrad) och chunktabellen (id, typ, längd, nästa chunk, offset) - i meta.json `rofl` och de råa radernas `text`
- ROFL2: versionssträngen
- Match-V5-tidslinjen (bara med egen API-nyckel): varje deltagarbild på en `position`-rad (eller `participant_frame` utan plats) med alla dess fält utplattade (`championStats.armor`, `damageStats.totalDamageDone`, `currentGold`, `xp`, ...); varje händelse som en rad namngiven efter sin typ, placerad där den har en `position`, CHAMPION_KILL som ett dödsfall och ett dödsfall

**Sparas råa**

- varje del av .rofl, helt, i filens ordning (`offset`), så att delarna är filen: `magic`, `signature`, `lengths`, `metadata`, `payload_header`, `chunk_header`, `chunk`, `keyframe` (ROFL1); `body`, `metadata`, `metadata_length` (ROFL2); varje stycke som ingen del täcker som `unknown`
- tidslinjen helt: `timeline <type>` för varje händelse, `timeline participantFrame` för varje spelares bild (`participant` är dess id), `timeline` för resten

**Finns inte**

- spelet självt (positioner, förmågor, varje enhet, ögonblick för ögonblick): ROFL1:s chunkar och ROFL2:s body är krypterade och paketen inuti förvrängda med varje patch. Sparat helt, inte läst
- positioner utan din egen Riot API-nyckel: filen har inga i det öppna

**Storlek**: den råa sidofilen är ungefär reprisens egen storlek: de krypterade chunkarna komprimeras inte

## Verifierat {#verified}

läsaren (heat3d-riot-replays) testad på filer byggda efter layouterna i roflxd.cs (MIT); tidslinjen efter Match-V5:s dokumenterade JSON; ingen riktig repris fanns att kontrollera mot

## Källa {#source}

[heat3d_watch/adapters/riot_replays.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/riot_replays.py)

<!-- Generated from the adapter by tools/gen_game_pages.py; change the adapter and run it again rather than editing this page. -->
