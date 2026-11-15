---
title: "Elite Dangerous (loggfiler)"
nav_order: 18
lang: "sv"
source: game-elite.md
source_hash: "bb5bcf75553a"
nav_exclude: true
search_exclude: true
---
# Elite Dangerous (loggfiler) {#elite-dangerous-log-files}

När du spelar Elite Dangerous läser watchern de filer som spelet skriver och sparar vad som hände, så att du senare kan titta på det på en karta i 3DHeat-visaren.

*Tekniska detaljer: adapter `elite`, slag [`log`](sources-and-rules.md); den körs medan `EliteDangerous64.exe` är igång och letar efter ny data var 0,25 s.*

## Vad som spelas in {#what-is-recorded}

- varje journalhändelse, under sitt journalnamn, med sina enkla fält
- galaxposition (StarPos, ljusår) vid hopp, platser, uppståndelser, dödsfall, dockning, landning
- uppstånd vid LoadGame/Resurrect, dödsfall vid Died, dockad/avdockad, touchdown/liftoff, hopp, session_end
- ytrutt på planeten från Status.json: latitud, longitud, höjd, kurs, och meter i ett tangentplan per kropp (session = kroppens namn), med Status.json:s övriga enkla fält (Flags, Flags2, GuiFocus, LegalState, ...)
- varje journalrad och varje följdfil helt i heat.raw.parquet
- hopp, sträcka hoppad, dödsfall, dödande, intjänade krediter, avslutade uppdrag, skannade kroppar, besökta system, dockningar, landningar

## Var datan kommer ifrån {#where-it-comes-from}

Spelarjournalen %USERPROFILE%\Saved Games\Frontier Developments\Elite Dangerous\Journal.\*.log (nyaste filen, följs när den skrivs), Status.json och de övriga följdfilerna \*.json (Market, Outfitting, Shipyard, NavRoute, Cargo, ModulesInfo, ShipLocker, Backpack, FCMaterials) i samma mapp

## Så slår du på det {#how-to-switch-it-on}

Inget behöver slås på: watchern läser källan så som spelet eller plattformen tillhandahåller den.

## Så fungerar det {#how-it-works}

Elite Dangerous: spelarjournalen och Status.json som spelet skriver medan det körs.

Var: `%USERPROFILE%\Saved Games\Frontier Developments\Elite Dangerous\`

* `Journal.<yyyy-mm-ddThhmmss>.<part>.log` - ett JSON-objekt per rad, en fil per start
  (en lång session fortsätter i del .02, .03 ...). Varje rad har
  `timestamp` (UTC, ISO 8601) och `event`. Galaxpositioner är systemets
  `StarPos` [x, y, z], i ljusår från Sol, på `FSDJump`,
  `Location` och `CarrierJump`. Elites galaktiska ram har y uppåt (mot
  galaktiska norr), z mot galaxens centrum och x mot galaktisk longitud
  270 - en vänsterhänt ram, så visaren spegelvänder z för att rita den rätt
  håll.
* `Status.json` - skrivs om hela när skeppets tillstånd ändras: `Flags`,
  och nära en planet `Latitude`, `Longitude` (grader), `Altitude` (meter),
  `Heading`, `BodyName` och `PlanetRadius` (meter).
* De övriga följdfilerna, var och en skriven om hela när motsvarande journalhändelse
  skrivs: `Market.json`, `Outfitting.json`, `Shipyard.json`,
  `NavRoute.json`, `Cargo.json`, `ModulesInfo.json`, `ShipLocker.json`,
  `Backpack.json`, `FCMaterials.json`. Varje `*.json` i mappen som spelet
  skriver under denna körning sparas helt varje gång den ändras (3DHeats
  konverterarregel: det källan innehåller läses eller sparas), under sitt filnamn.

Varje journalrad sparas helt i sessionens råa sidofil under sin `event`, varje följdfil under sitt filnamn; en rad som inte är JSON under `unparsed`.

Ytpositioner läggs i ett lokalt tangentplan per kropp, i meter: den första positionen på en kropp är dess ursprung, x österut, z norrut, y upp (höjd), samma händedrag som galaxramen, och raderna bär kroppens namn som sin `session` så att en körning eller en vandring på en planet ritas som en egen rutt. Galaxrader har sessionen "galaxy". De två skalorna ligger i en tabell; välj session i visaren.

Format: Frontiers manual "Elite Dangerous Player Journal" (publicerad med varje uppdatering på de officiella forumen, <https://forums.frontier.co.uk/> - "Journal Manual", v4.x), händelser och fält enligt den; Status.json:s flaggor enligt samma manuals kapitel "Status File".

## Positioner och axlar {#positions-and-axes}

| | |
|---|---|
| Positioner sparas | ja |
| Upp-axel | `y` |
| Enheter | ljusår (galaxrader, session 'galaxy'); meter öster/upp/norr från första positionen på en kropp (ytrader, session = kroppens namn) |
| Speglad för visaren | `z` |
| Enhetsskala (`scale`: visaren multiplicerar positionerna med den) | 1 |

Dessa läggs i varje sessions `meta.json` (`axes`) och, när sessionen har positioner, i `heat.parquet`:s fotnot, så att 3DHeat-visaren vrider och skalar raderna själv - se [Datan](the-data.md).

## Flerspelarläge {#multiplayer}

- Markerat som spelat online (`multiplayer`): **ja**. `games --markdown` visar detta som "tillåtet (läser bara det spelet publicerar)".
- Slag `log`: den läser bara det spelet eller plattformen lämnar ut (filer som spelet skriver medan det körs), så den spelar in även i onlinespel som offline; flaggan avgör bara om minne någonsin får läsas.
- Minne: **aldrig** läst av den här adaptern. Bara `memory`-adaptrar läser minne, och aldrig för ett spel som är markerat som spelat online - se [Källor och regler](sources-and-rules.md).

## Statistik som sparas {#statistics-recorded}

Statistiknycklar som den här adapterns kod sätter med namn (varje sessions `stats` i `meta.json` och tabellen `stats` i `watcher.sqlite`):

`bad_lines`, `bodies_scanned`, `carrier_jumps`, `credits`, `credits_earned`, `deaths`, `distance_ly`, `dockings`, `jumps`, `kills`, `landings`, `missions_completed`, `ship`, `surface_fixes`, `systems_visited`

En nyckel i klammer fylls i vid körning (`score.{team}` är en nyckel per lag). Nycklar som koden tar från en tabell med spelets fält eller från spelets egna statistiknamn finns inte i listan; "Vad som spelas in" ovan nämner dem.

## Fullständighet {#completeness}

watchern följer 3DHeats [konverterarregel](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md): det källan innehåller läses eller sparas, aldrig slängs. Utöver raderna sparas varje paket, sida, rad eller svar som adaptern tar emot helt i sessionens `heat.raw.parquet` (kolumnerna `time`, `ms`, `type`, `used`, `payload`, `text` och sedan eventuella fält som sparats med namn; `used` markerar det som också blev rader), och `meta.json`:s `selfCheck.completeness` räknar varje `type` - `lost` är 0.

**Läses**

- varje journalrad som en rad under sin `event`, med sina enkla fält (den lokaliserade texten där spelet ger en; texter längre än 300 tecken kapas i raden)
- galaxrader (StarPos) vid FSDJump, CarrierJump, Location, LoadGame, Resurrect, Died, Docked, Undocked, Touchdown, Liftoff, Shutdown; ytrader från Status.json och Touchdown/Liftoff
- Status.json:s enkla fält (Flags, Flags2, GuiFocus, LegalState, Cargo, FireGroup, Oxygen, Health, Temperature, Gravity, SelectedWeapon, ...) på ytraderna
- statistiken: hopp, sträcka, dödsfall, dödande, intjänade krediter, uppdrag, skannade kroppar, besökta system, dockningar, landningar

**Sparas råa**

- varje journalrad helt, `type` = dess `event` (FSDJump, Scan, Music, ReceiveText, ...), `used` sant: listorna och objekten som raderna utelämnar (StarPos, Factions, Rewards, Killers, Materials, Modules, ...) finns bara här
- en journalrad som inte är JSON, `type` `unparsed`
- varje följdfil helt varje gång spelet skriver om den, `type` = dess filnamn: `Status.json` (`used` när den gav en ytrad), `Market.json`, `Outfitting.json`, `Shipyard.json`, `NavRoute.json`, `Cargo.json`, `ModulesInfo.json`, `ShipLocker.json`, `Backpack.json`, `FCMaterials.json`, och varje annan `*.json` som spelet skriver där

**Finns inte**

- position mellan hoppen (inne i ett system, i supercruise eller i normalrymden): spelet skriver bara systemets StarPos och, nära en planet, latitud, longitud och höjd
- andra skepp och spelares positioner: journalen är befälhavarens egen redogörelse
- hastighet, gas och annan flygtelemetri: spelet skriver inte dem
- journaler och följdfiler från tidigare sessioner: sparas när de spelades (följaren startar vid slutet av en fil som är äldre än den här körningen av spelet)
- Frontiers webb-API för kompanjonen (cAPI): kräver spelarens Frontier-inloggning; inte en fil som spelet skriver

**Storlek**: ungefär 1-5 MB rå text per timme: journalen 0,2-2 MB, Status.json (under 1 KB, skriven om upp till en gång per sekund) 1-2 MB, en uppsättning för marknad/utrustning/varv 20-150 KB per station som besöks; zstd i heat.raw.parquet gör det ungefär en tiondel

## Verifierat {#verified}

tolkaren spelad om över riktiga journalfiler från en lokal installation (händelseantalen stämmer med statistiken); ytfixeringar i Status.json testade endast på syntetiska ögonblicksbilder

## Källa {#source}

[heat3d_watch/adapters/elite.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/elite.py)

<!-- Generated from the adapter by tools/gen_game_pages.py; change the adapter and run it again rather than editing this page. -->
