---
title: "War Thunder (spelstatus)"
nav_order: 46
lang: "sv"
source: game-warthunder-webmap.md
source_hash: "34a876e38f09"
nav_exclude: true
search_exclude: true
---
# War Thunder (spelstatus) {#war-thunder-game-state}

Medan du spelar War Thunder sparar watchern det som spelet rapporterar till program på din egen dator, så att du senare kan titta på det på en karta i 3DHeat-visaren.

*Teknisk information: adaptern `warthunder-webmap`, typ [`gsi`](sources-and-rules.md); den körs medan `aces.exe` är igång och letar efter ny data var 0,5 s.*

## Vad som spelas in {#what-is-recorded}

- egen position (kartans öst/norr i meter; höjd från /state i flygplan, annars 0) två gånger per sekund, kurs, hastighet
- spawn, och att det egna fordonet lämnar kartan (förstört, landat, tillbaka till hangaren), en sortie vardera
- andra flygplan och markenheter på minikartan som positioner med spårade id:n och sida (ingen höjd)
- flygfält, erövringszoner och baser en gång, och zoner som byter sida
- kill- och skadeflödets rader (vem, fordon, verb); spelarens kills och dödsfall när ditt namn är inställt (`config --set player_names.warthunder-webmap=<name>`)
- spawn, sträcka, högsta höjd, högsta sanna lufthastighet, fordon; kills och dödsfall när ditt namn är inställt
- varje svar från webbkartan sparat helt i heat.raw.parquet - hela /state och /indicators, chatten, slagfältets mål och kartans bild inräknade; mellan slagen i en egen session

## Varifrån det kommer {#where-it-comes-from}

spelets lokala webbkarta, <http://127.0.0.1:8111> (/map_info.json, /map_obj.json, /state, /indicators, /hudmsg, /gamechat, /mission.json, /map.img)

## Så slår du på det {#how-to-switch-it-on}

Inget behöver slås på: watchern läser källan så som spelet eller plattformen tillhandahåller den.

## Så fungerar det {#how-it-works}

War Thunder: spelets egen lokala webbkarta på <http://127.0.0.1:8111>.

Spelet serverar sidan som en andra skärm eller en telefon kan visa (”webbkartan”), och JSON:en bakom den, medan det körs - i alla lägen, även flerspelar:

```text
/map_info.json   {"map_min": [x, y], "map_max": [x, y], "grid_steps", "grid_zero", "map_generation",
                  "hud_type", "valid"}: the map's extent in metres; valid false in the hangar
/map_obj.json    [{"type": aircraft|ground_model|airfield|capture_zone|bombing_point|defending_point|
                  respawn_base_*|..., "icon": Player|Fighter|Bomber|Mediumtank|SPAA|..., "color": "#rrggbb",
                  "x", "y" (0..1 of the map picture, y down), "dx", "dy" (direction),
                  airfields "sx", "sy", "ex", "ey"}]: what the minimap shows, the player's own
                  vehicle with icon "Player"; no ids, no heights
/state           {"valid", "H, m", "TAS, km/h", "IAS, km/h", "M", "Vy, m/s", ...}: flight values,
                  valid only in an aircraft
/indicators      {"valid", "army": air|tank|..., "type": the vehicle}
/hudmsg?lastEvt=N&lastDmg=M   {"events": [...], "damage": [...]} newer than the ids given, each
                  {"id", "msg", "sender", "enemy", "mode", "time"}; damage lines read like
                  "Name (Vehicle) shot down Name (Vehicle)"
/gamechat?lastId=N  the chat newer than the id given, [{"id", "msg", "sender", "enemy", "mode", "time"}]
/mission.json    the battle's objectives and their status
/map.img         the map's picture the page draws the objects on
```

Varje svar sparas helt i sessionens råa sidovagn under sin endpoint (map_info, map_obj, state, indicators, hudmsg, gamechat, mission, map_img); mellan slagen går svaren till en egen session.

En kartposition blir meter med utsträckningen: u = min_x + x \* (max_x - min_x) öster, v = max_y - y \* (max_y - min_y) norr (bildens y går nedåt). Raderna är x = u, y = höjd (den egna flygplanets "H, m"; 0 för allt annat), z = v, så Y är uppåt; z speglas för visaren så att norr inte ritas söderut.

Färger visar sidorna så som spelaren ser dem: egen gul (#faC81E som standard), squad grön, allierade blå (#174DFF), fiender röd (#f40C00); färgblindspaletter ändrar dem, så nyansen avgör, inte det exakta värdet. Spelet namnger ingen på kartan och ger objekt inga id: andra objekt får id här genom att följa dem från poll till poll (närmaste av samma typ och ikon), vilket kan byta plats på två flygplan av samma typ som passerar nära varandra. Spelarens eget namn finns inte heller i API:t: ange det i inställningarna (`config --set player_names.warthunder-webmap=<ditt namn>`) så blir kill-flödets rader om spelaren till kills och dödsfall; utan det spelas de in som kill-flödet.

Källor: spelets egen sida på <http://127.0.0.1:8111> och dess JSON; faktauppgifter om fälten så som dokumenterats av projektet JoyPro 2 (docs/telemetry-recording.md; GPL, använt bara för fakta).

## Positioner och axlar {#positions-and-axes}

| | |
|---|---|
| Positioner sparas | ja |
| Uppåtaxel | `y` |
| Enheter | meter (kartans öst/norr; höjd bara för egen flygplan) |
| Speglad för visaren | `z` |
| Enhetsskala (`scale`: visaren multiplicerar positionerna med den) | 1 |

Dessa läggs i varje sessions `meta.json` (`axes`) och, när sessionen har positioner, i `heat.parquet`:s footer, så att 3DHeat-visaren vrider och skalar raderna själv - se [Datan](the-data.md).

## Multiplayer {#multiplayer}

- Markerad som spelad online (`multiplayer`): **ja**. `games --markdown` visar detta som "tillåten (läser bara det spelet publicerar)".
- Typ `gsi`: den läser bara det spelet eller plattformen lämnar ut (en game-state integration eller lokal API som spelet erbjuder), så den spelar in även i onlinespel så väl som offline; flaggan avgör bara om minnet någonsin får läsas.
- Minne: läses **aldrig** av den här adaptern. Bara `memory`-adaptrar läser minne, och aldrig för ett spel som är markerat som spelat online - se [Källor och regler](sources-and-rules.md).

## Statistik som sparas {#statistics-recorded}

Statistiknycklar som adapterns kod sätter med namn (varje sessions `stats` i `meta.json` och tabellen `stats` i `watcher.sqlite`):

`bad_packets`, `deaths`, `distance_m`, `hits_dealt`, `hits_taken`, `kills`, `max_altitude_m`, `max_tas_kmh`, `spawns`, `vehicle`

En nyckel inom klammerparenteser fylls i vid körning (`score.{team}` är en nyckel per lag). Nycklar som koden tar från en tabell med spelets fält eller från spelets egna statistiknamn finns inte med i den här listan; "Vad som spelas in" ovan nämner dem.

## Fullständighet {#completeness}

Watchern följer 3DHeats [omvandlarregel](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md): det källan innehåller läses eller sparas, aldrig slängs. Utöver raderna sparas varje paket, sida, rad eller svar som adaptern tar emot helt i sessionens `heat.raw.parquet` (kolumnerna `time`, `ms`, `type`, `used`, `payload`, `text`, plus eventuella fält som sparas med namn; `used` markerar det som också blev rader), och `meta.json`:s `selfCheck.completeness` räknar varje `type` - `lost` är 0.

**Läses**

- /map_info.json: kartans utsträckning och rutnät (meter, kartans id) till meta.json; en ogiltig avslutar slaget
- /map_obj.json (två gånger per sekund): det egna fordonet, andra flygplan och markenheter (spårade id:n, sida från färgen, ikon, kurs, färg) och flygfält, zoner och baser som rader
- /state (två gånger per sekund, i ett flygplan): höjd, TAS, IAS, Mach och Vy på de egna raderna
- /indicators (var 2:e s): arméslag och fordonstyp
- /hudmsg (en gång per sekund): kill- och skadeflödets rader som kills, dödsfall, träffar och flödesrader; andra HUD-händelser som rader

**Sparas råa**

- varje svar helt, `text` är JSON:en så som spelet skickade den, under sin endpoint: `map_info`, `map_obj`, `state`, `indicators`, `hudmsg`, `gamechat`, `mission`; `map_img` är kartbildens bytes som `payload`, en gång per slag
- det bara den råa sidovagnen har: varje /state-fält utöver de fem som läses (AoA, AoS, Ny, Wx, gas, varvtal, bränsle, ... - ett flygplans uppsättning skiljer sig från ett annats), varje /indicators-fält (flygplanens instrument i cockpit, tankfartygens hastighet, växel, besättning och stabilisator), kartobjektens andra nycklar (color[], blink, icon_bg, flygfältens ändar), hudmsg:s sender, enemy och mode, chatten (/gamechat, en gång per sekund), slagets mål och deras status (/mission.json, var 10 s i ett slag), rader som sagts innan watchern startade
- mellan slagen (hangar, laddning) går svaren till en egen session, markerad `between_battles` i meta.json, som saknar rader

**Inte tillgängligt**

- namn, id och höjder för andra spelares fordon: webbkartan har inga (id:n ges här genom att följa objekt från poll till poll); kill-flödet namnger spelare utan positioner
- allt utanför webbkartan: spelets replayer läses av omvandlaren för War Thunder-replayer, och spelets minne läses aldrig (ett onlinespel)
- /map_obj.json oftare än två gånger per sekund: avfrågningstakten hålls låg, så att spelets egen webbserver inte belastas

**Storlek**: cirka 50-120 MB per timme JSON före zstd i ett slag (map_obj 5-15 KB två gånger per sekund, state cirka 1,5 KB två gånger per sekund, indicators var 2:e s, chatt- och HUD-raderna små) plus kartbilden en gång per slag (under 2 MB); 1-2 MB per timme mellan slagen (kartans utseende två gånger per sekund, HUD och chatt en gång, vardera ett kort svar); zstd minskar upprepad JSON väl över tiofaldigt

## Verifierad {#verified}

testad mot en falsk lokal server som svarar i formatet för spelets webbkarta; inte testad mot det körande spelet

## Källa {#source}

[heat3d_watch/adapters/warthunder.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/warthunder.py)

<!-- Generated from the adapter by tools/gen_game_pages.py; change the adapter and run it again rather than editing this page. -->
