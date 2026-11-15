---
title: "Path of Exile (loggfiler)"
nav_order: 35
lang: "sv"
source: game-poe.md
source_hash: "b5783b5a5690"
nav_exclude: true
search_exclude: true
---
# Path of Exile (loggfiler) {#path-of-exile-log-files}

När du spelar Path of Exile läser watchern de filer spelet skriver och sparar vad som hände, så att du senare kan titta på det som statistik och en tidslinje.

*Tekniska detaljer: adapter `poe`, slag [`log`](sources-and-rules.md); den körs medan `PathOfExile.exe`, `PathOfExile_x64.exe`, `PathOfExileSteam.exe`, `PathOfExile_x64Steam.exe`, `PathOfExileEGS.exe`, `PathOfExile_x64EGS.exe`, `PathOfExile_KG.exe` eller `PathOfExile_x64_KG.exe` är igång och letar efter ny data var 0,5 s.*

## Vad som spelas in {#what-is-recorded}

- zoner man går in i, med områdesnivå, områdes-id och dess seed
- nivåhöjningar med klass och nivå
- dödsfall ("has been slain")
- spelare som går in i och lämnar området, viskningar in och ut, handelsförfrågningar, accepterade byten
- varje rad i Client.txt för den här sessionen helt i `heat.raw.parquet`
- dödsfall, nivåer uppnådda, högsta nivå, zoner man gått in i, olika zoner, viskningar, handelsförfrågningar, byten

## Var datan kommer ifrån {#where-it-comes-from}

&lt;install>\logs\Client.txt för Path of Exile eller Path of Exile 2 (följs; installationsmappen är den körande programfilens)

## Så slår du på det {#how-to-switch-it-on}

Inget behöver slås på: watchern läser källan så som spelet eller plattformen tillhandahåller den.

## Så fungerar det {#how-it-works}

Path of Exile och Path of Exile 2: klientloggen, `<install>\logs\Client.txt`.

Båda spelen lägger till i en gemensam Client.txt i sin installationsmapp så länge de är installerade (den växer över starterna). Raderna ser ut så här:

```text
2024/01/01 12:00:00 123456789 cff94598 [INFO Client 1234] : You have entered Lioneye's Watch.
2024/01/01 12:00:00 123456789 cff94598 [DEBUG Client 1234] Generating level 2 area "1_1_2" with seed 1
2024/01/01 12:00:00 123456789 cff94598 [INFO Client 1234] : Name (Witch) is now level 2
2024/01/01 12:00:00 123456789 cff94598 [INFO Client 1234] : Name has been slain.
2024/01/01 12:00:00 123456789 cff94598 [INFO Client 1234] @From Name: Hi, I would like to buy your ...
```

- lokal tid, en millisekundräknare, en hash, nivån och tråden, sedan det chattfönstret visar. Meddelandena är den engelska klientens; en klient på annat språk skriver dem översatta och förstås inte här. Ingenting ger en position. Formatet är inte dokumenterat av Grinding Gear Games; det är spelets vanliga textlogg, så som communityverktyg (handelshjälpare, nivåguider) har läst den i många år - t.ex. <https://github.com/klayveR/poe-log-monitor> (MIT) för händelselistan.

Installationsmappen är den körande programfilens; utan den söks Steam-biblioteken och den fristående klientens standardmapp.

Varje rad i den här sessionen sparas helt i sessionens råa sidfil (3DHeats konverterarregel), oavsett om den betyder något här: `type` är nivån och loggaren i dess hakparenteser (`INFO Client`, `DEBUG Client`, `WARN Client`, ...), en tidsstämplad rad utan hakparenteser är `untagged`, en rad utan tidsstämpel `untimed`.

## Positioner och axlar {#positions-and-axes}

| | |
|---|---|
| Positioner sparas | nej |
| Upp-axel | `y` |
| Enheter | inga positioner registreras |
| Speglad för visaren | ingen |
| Enhetsskala (`scale`: visaren multiplicerar positionerna med den) | 1 |

Dessa läggs i varje sessions `meta.json` (`axes`) och, när sessionen har positioner, i `heat.parquet`:s fotnot, så att 3DHeat-visaren vrider och skalar raderna själv - se [Datan](the-data.md).

## Flerspelarläge {#multiplayer}

- Markerat som spelat online (`multiplayer`): **ja**. `games --markdown` visar detta som "allowed (reads only what the game publishes)".
- Slag `log`: den läser bara det spelet eller plattformen lämnar ut (filer som spelet skriver medan det körs), så den spelar in även i onlinespel som offline; flaggan avgör bara om minne någonsin får läsas.
- Minne: **aldrig** läst av den här adaptern. Bara `memory`-adaptrar läser minne, och aldrig för ett spel som är markerat som spelat online - se [Källor och regler](sources-and-rules.md).

## Statistik som sparas {#statistics-recorded}

Statistiknycklar som den här adapterns kod sätter med namn (varje sessions `stats` i `meta.json` och tabellen `stats` i `watcher.sqlite`):

`bad_lines`, `character_class`, `deaths`, `level`, `levels_gained`, `trade_requests_received`, `trade_requests_sent`, `trades`, `whispers`, `zones_distinct`, `zones_entered`

En nyckel i klammer fylls i vid körning (`score.{team}` är en nyckel per lag). Nycklar som koden tar från en tabell med spelets fält eller från spelets egna statistiknamn finns inte i listan; "Vad som spelas in" ovan nämner dem.

## Fullständighet {#completeness}

watchern följer 3DHeats [konverterarregel](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md): det källan innehåller läses eller sparas, aldrig slängs. Utöver raderna sparas varje paket, sida, rad eller svar som adaptern tar emot helt i sessionens `heat.raw.parquet` (kolumnerna `time`, `ms`, `type`, `used`, `payload`, `text` och sedan eventuella fält som sparats med namn; `used` markerar det som också blev rader), och `meta.json`:s `selfCheck.completeness` räknar varje `type` - `lost` är 0.

**Läses**

- `You have entered <zone>` med områdesnivå, områdes-id och seed från raden `Generating level` före den
- `<name> (<class>) is now level <n>`, `<name> has been slain`, spelare som går in i och lämnar området, viskningar in och ut (med om de är en handelsförfrågan), accepterade och avbrutna byten

**Sparas råa**

- varje rad i den här sessionen helt, `type` = nivån och loggaren i dess hakparenteser (`INFO Client`, `DEBUG Client`, `WARN Client`, `CRIT Client`, ...), `used` där den blev en rad: global-, handels-, grupp- och gildechatt, `Connecting to instance server`, AFK- och DND-meddelanden, svaren på chattkommandon som `/played` och `/deaths`, klientens laddnings- och motorrader - sparade, ännu inte gjorda till rader
- en tidsstämplad rad utan hakparenteser (`***** LOG FILE OPENING *****`) som `untagged`, en rad utan tidsstämpel som `untimed`

**Finns inte**

- positioner: ingenting i loggen ger någon
- vad en klient på annat språk skriver: raderna sparas, men bara de engelska meddelandena görs till rader
- rader från tidigare starter: Client.txt växer över starterna; rader stämplade före den här körningen av spelet lämnas (de sparades när de spelades)
- dödanden, skada, byte och det passiva trädet: spelet loggar dem inte

**Storlek**: Client.txt växer ungefär 0,3-3 MB per timme (mest från DEBUG-rader under områdesladdning, mer med livlig handelschatt); zstd i `heat.parquet` gör det ungefär en tiondel

## Verifierat {#verified}

testad på syntetiska Client.txt-rader i spelets format; ännu inte testad mot spelet

## Källa {#source}

[heat3d_watch/adapters/poe.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/poe.py)

<!-- Generated from the adapter by tools/gen_game_pages.py; change the adapter and run it again rather than editing this page. -->
