---
title: "Dota 2 (replayer)"
nav_order: 12
lang: "sv"
source: game-dota-replays.md
source_hash: "88539ee6dc65"
nav_exclude: true
search_exclude: true
---
# Dota 2 (replayer) {#dota-2-replays}

Efter en match i Dota 2 gör watchern om replayen som spelet sparade till filer som du kan titta på på en karta i 3DHeat-visaren.

*Teknisk information: adaptern `dota-replays`, typ [`replay`](sources-and-rules.md); den körs hela tiden (den väntar inte på att ett spel ska starta) och letar efter ny data var 5 s.*

## Vad som spelas in {#what-is-recorded}

- varje hjältes position, höjd, hälsa och nivå, 7,5 gånger per sekund medan den lever
- kills och dödsfall där de skedde; torn, kaserner, Roshan och Tormentors där de föll; wards där de placerades
- varje spelares kartmarkeringar, kartritningar och order (flytta, attackera, använd förmåga, köp, ...) där de pekade
- poängen och varje spelares rad; den inloggade spelarens som statistik
- allt annat som replayen innehåller, sparat helt bredvid tabellen: varje ram och nätverksmeddelande, varje ändring av entitetens egenskaper, varje post i strängtabellen

## Varifrån det kommer {#where-it-comes-from}

replayer som Dota 2 sparar: &lt;Dota>/game/dota/replays/&lt;match id>.dem (nedladdade i klienten, eller med `dota-replay <match id>`)

## Så slår du på det {#how-to-switch-it-on}

ladda ner en matchs replay i Dota 2, eller hämta en offentlig: `python -m heat3d_watch dota-replay <match id>`; installera läsaren: github.com/Holdi601/3DHeat-Ext-DotaReplay (`heat3d-dota-replay`, tar med gem-dota)

Skriv kommandot i en terminal som är öppen i watcherns mapp (se [Innan du börjar](before-you-start.md)). Om det misslyckas säger sista raden varför; [Installera och köra](installing-and-running.md) beskriver de vanligaste orsakerna.

Inställningar från miljövariabler:

- `HEAT3D_DOTA_REPLAY`: läsarens mapp (en klonad eller uppackad utgåva), när den inte är installerad eller bredvid watchern

## Så fungerar det {#how-it-works}

Replayer och demos: vad ett spel sparar av en match, omvandlat när matchen är över.

En replay innehåller allt som ett levande gränssnitt håller tillbaka i flerspelarspel - varje spelares position, varje kill där den skedde - och den är en fil som spelet skriver åt sina spelare, så att läsningen inte rör något i spelet. Watchern tittar i de mappar spel sparar dem i, väntar tills en ny fil slutat växa (spelet skriver fortfarande på den annars), och omvandlar den i en arbetstråd, så att en lång omvandling aldrig stoppar resten av watchern.

Första gången en mapp ses noteras bara de replayer som redan finns i den, de omvandlas inte: en spelare med år av demos skulle annars få watchern upptagen i ett dygn. `python -m heat3d_watch replays <adapter> [folder]` omvandlar de befintliga på begäran.

#### Dota 2 {#dota-2}

Dota 2 sparar de replayer en spelare laddar ner (en matchs detaljer, eller Watch > Replays) i `<Dota>/game/dota/replays/<match id>.dem`; Valve behåller varje offentlig matchs replay på sina servrar i några veckor, och `python -m heat3d_watch dota-replay <match id>` hämtar en med dess id via OpenDota. Watchern läser dem inte själv: en extern läsare gör det (3DHeat Dota Replay, github.com/Holdi601/3DHeat-Ext-DotaReplay, `exporters/ext/dota-replay`, kommandot `heat3d-dota-replay`, som läser via gem-dota, MIT), ett eget projekt, och körs i en egen process för varje ny replay när den finns i PATH, är installerad eller bredvid watchern; saknas den säger watchern en gång hur den installeras. Den skriver varje hjältes position, höjd, hälsa, nivå, riktning, mana, erfarenhet, attribut och föremål 7,5 gånger per sekund medan den lever, kills och dödsfall där de skedde, torn, kaserner, Roshan och Tormentors där de föll, varje ward där den placerades och där den tog slut, stridsloggens poster om hjältarna (skada, helande, förmågor, föremål, köp, runor, guld, erfarenhet, modifierare), och varje spelares kartmarkeringar, kartritningar och order - i `dota/<match>.parquet`; varje annan enhet (creeps, summons, illusioner, couriers, byggnader) en gång per sekund i `<match>.units.parquet`; hela stridsloggen i `<match>.combatlog.parquet`; och matchen, chatten, draften, allt annat som parsern hämtar och spelets egen slutrapport för matchen i `<match>.match.json`, i sessionsmappen. Allt annat replayen innehåller sparas helt bredvid dem (3DHeats omvandlarregel): varje ram och nätverksmeddelande i `<match>.packets.parquet`, varje ändring av entitetens egenskaper i `<match>.entities.parquet`, varje post i strängtabellen i `<match>.strings.parquet`, räknat i matchdokumentets `selfCheck.completeness`. Positionerna är Dotas världsenheter, samma som spelstatusintegrationen rapporterar. Den inloggade spelarens rad i scoreboardet blir sessionens statistik: kills, dödsfall, assists, last hits, denies, nettovärde, GPM, XPM, skada till hjältar, wards, och om matchen vanns. En ny Dota-patch kan ändra replayens entiteter innan gem hänger med; en replay som gem inte kan läsa till slut omvandlas så långt den går och markeras `incomplete` i sin sammanfattning.

Samma modul används också av: [Counter-Strike 2 (replayer)](game-cs2-demos.md), [Squad (replayer)](game-squad-demos.md), [War Thunder (replayer)](game-warthunder-replays.md), [World of Tanks (replayer)](game-wot-replays.md), [World of Warships (replayer)](game-wows-replays.md).

## Positioner och axlar {#positions-and-axes}

| | |
|---|---|
| Positioner sparas | ja |
| Uppåtaxel | `z` |
| Enheter | Dota-världsenheter (Hammer-enheter; kartan är cirka 16400 över) |
| Speglad för visaren | `y` |
| Enhetsskala (`scale`: visaren multiplicerar positionerna med den) | 1 |

Dessa läggs i varje sessions `meta.json` (`axes`) och, när sessionen har positioner, i `heat.parquet`:s footer, så att 3DHeat-visaren vrider och skalar raderna själv - se [Datan](the-data.md).

## Multiplayer {#multiplayer}

- Markerad som spelad online (`multiplayer`): **ja**. `games --markdown` visar detta som "tillåten (läser bara det spelet publicerar)".
- Typ `replay`: den läser bara det spelet eller plattformen lämnar ut (replayer och demos som spelet sparar), så den spelar in även i onlinespel så väl som offline; flaggan avgör bara om minnet någonsin får läsas.
- Minne: läses **aldrig** av den här adaptern. Bara `memory`-adaptrar läser minne, och aldrig för ett spel som är markerat som spelat online - se [Källor och regler](sources-and-rules.md).

## Statistik som sparas {#statistics-recorded}

Statistiknycklar som adapterns kod sätter med namn (varje sessions `stats` i `meta.json` och tabellen `stats` i `watcher.sqlite`):

`duration`, `hero`, `score.{team}`, `team`, `won`

En nyckel inom klammerparenteser fylls i vid körning (`score.{team}` är en nyckel per lag). Nycklar som koden tar från en tabell med spelets fält eller från spelets egna statistiknamn finns inte med i den här listan; "Vad som spelas in" ovan nämner dem.

## Fullständighet {#completeness}

Omvandlaren följer 3DHeats [omvandlarregel](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md): det replayen innehåller läses eller sparas, aldrig slängs. Utöver tabellen sparas allt annat replayen innehåller helt i sidovagnar bredvid den, i sessionens mapp `dota/` - `<match>.packets.parquet`, `<match>.entities.parquet`, `<match>.strings.parquet` (kolumnerna `time`, `tick`, `type`, `name`, `entity`, `decoded`, `payload`, när de gäller) - och matchdokumentets (`<match>.match.json`) `selfCheck.completeness` räknar varje `type` - `lost` är 0.

**Läses**

- tabellen (`dota/<match>.parquet`): varje hjältes position, höjd, hälsa, nivå, riktning, mana, erfarenhet, attribut, rustning, hastighet, skada, föremål och spelarens markör 7,5 gånger per sekund; kills, dödsfall, mål, wards, stridsloggens poster om hjältar; kartmarkeringar (`ping`, DOTA_UM_LocationPing), kartritningar (`map_line`, DOTA_UM_MapLine) och varje enhetsorder (`order`, DOTA_UM_SpectatorPlayerUnitOrders: `other` ordertypen, `value` förmågans eller föremålets id, `text` målets klass; vid den beordrade punkten, annars vid hjälten)
- `<match>.units.parquet`: varje annan enhet en gång per sekund; `<match>.combatlog.parquet`: hela stridsloggen så som gem läser den, varje fält
- matchdokumentet: allt gem hämtar, och helt replayens egna poster - `fileHeader` (DEM_FileHeader), `fileInfo` (DEM_FileInfo: uppspelningens längd, varje spelares namn, hjälte, Steam-id, lag), `matchDetails` (DOTA_UM_MatchDetails: spelkoordinatorns slutscoreboard, varje spelares siffror, föremål, skada per typ, val och bans) och `matchMetadata` (DOTA_UM_MatchMetadata)
- `selfCheck.crossCheck`: kills, dödsfall, assists, nivå, last hits och denies som lästs ur strömmen mot `matchDetails`, per spelare

**Sparas råa**

- `<match>.packets.parquet`: varje ram som inte är ett paket (`type` `frame <n>`) och varje nätverksmeddelande (`message <n>`, `name` Valves), helt i `payload`, i filens ordning (`seq`, `frame`), med `decoded` protobuf:en som JSON (ett bytefält anges med sin längd), varje meddelandetyp avkodad: svc_PacketEntities (entitetsströmmen), DOTA_UM_SpectatorPlayerUnitOrders, UM_ParticleManager, stridsloggsmeddelandena, GE_SosStartSoundEvent, DOTA_UM_TE_\* (projektiler, animationer, blod), DOTA_UM_OverheadEvent, DOTA_UM_UnitEvent, svc_UpdateStringTable, net_Tick, ...; de sändtabeller, klasslista och serverinfo som en senare entitetsavkodare behöver finns bland dem
- `<match>.entities.parquet`: varje entitets varje egenskap varje gång den ändrades (`type` egenskapen, `name` klassen, `entity` dess index; `value`, `vector` eller `decoded`), dess hela tillstånd när den skapades, och varje skapande, inträde, utträde och borttagning - miljontals rader för en hel match
- `<match>.strings.parquet`: varje post i strängtabellen från varje uppdatering och varje fullständig ögonblicksbild, värdet helt; `userinfo`, `ActiveModifiers` och `EconItems` avkodade från deras protobufs
- `selfCheck.completeness` i matchdokumentet räknar ramar och meddelanden efter Valves namn, stridsloggsposter (`combatlog <type>`), spelhändelser (`gameevent <name>`), strängtabellsposter (`stringtable <name>`) och entitetsuppdateringar (`entity <class>`); några sparas bara råa (fullständiga entitetsögonblicksbilder som gem hoppar över eftersom den bygger upp från ändringarna, och poster i tabeller vars värden ingenting läser), lost 0

**Inte tillgängligt**

- röst: replayen har rösttillståndet men inga röstdata
- namn bakom hashar och id:n: ljud och partiklar namnges med hashar av spelets filer, förmågor med id:n; replayen bär inte namnen (föremål namnges genom gems katalog där den har dem)
- något bara spelarnas egna klienter visste (deras kamera, deras skärm) utöver vad servern sände ut; markören och varje order finns med

**Storlek**: sidovagnarna tillsammans är något större än replayen själv, paketen och entiteterna är de största; en hel match tar en till två minuter i en process

## Verifierad {#verified}

kontrollerad på en offentlig matchs replay: kills, dödsfall, assists, nivå, last hits och denies stämmer med spelets egen slutrapport för alla tio spelare; varje meddelande i paketens sidovagn serialiseras om byte för byte; tabellen och statistiken genom tester på syntetisk data

## Källa {#source}

[heat3d_watch/adapters/replays.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/replays.py)

<!-- Generated from the adapter by tools/gen_game_pages.py; change the adapter and run it again rather than editing this page. -->
