---
title: "Hearthstone (loggfiler)"
nav_order: 25
lang: "sv"
source: game-hearthstone.md
source_hash: "e79c19776947"
nav_exclude: true
search_exclude: true
---
# Hearthstone (loggfiler) {#hearthstone-log-files}

När du spelar Hearthstone läser watchern de filer spelet skriver och sparar vad som hände, så att du senare kan titta på det som statistik och en tidslinje.

*Tekniska detaljer: adapter `hearthstone`, slag [`log`](sources-and-rules.md); den körs medan `Hearthstone.exe` är igång och letar efter ny data var 0,5 s.*

## Vad som spelas in {#what-is-recorded}

- spelets start och slut, med resultatet (vunnen, förlorad, oavgjord), turer och motståndarens namn
- varje tur
- varje rad i Power.log och de andra loggarna helt i `heat.parquet` (i `heat.raw.parquet`)
- spel, vinster, förluster, oavgjorda, turer, längsta spel

## Var datan kommer ifrån {#where-it-comes-from}

&lt;install>\Logs\Power.log (eller Logs\Hearthstone_\*\Power.log), skriven när %LOCALAPPDATA%\Blizzard\Hearthstone\log.config har ett [Power]-avsnitt, och varje annan \*.log som spelet skriver där

## Så slår du på det {#how-to-switch-it-on}

`python -m heat3d_watch setup hearthstone --apply` lägger till [Power]-loggning i %LOCALAPPDATA%\Blizzard\Hearthstone\log.config (säkerhetskopia sparas); starta om spelet

Skriv kommandot i en terminal som öppnats i watcherns mapp (se [Innan du börjar](before-you-start.md)). Om det misslyckas säger den sista raden varför; [Installation och körning](installing-and-running.md) går igenom de vanliga orsakerna.

`python -m heat3d_watch setup hearthstone` listar filerna det skulle ändra; `python -m heat3d_watch setup hearthstone --apply` ändrar dem och sparar originalet som `<file>.heat3d-backup` (se [Kommandon](commands.md#setup)). Den skriver `hearthstone: changed: ...` för varje ändring, eller `hearthstone: nothing to change` när den redan är påslagen.

## Så fungerar det {#how-it-works}

Hearthstone: spelets Power.log, som det skriver när `log.config` begär det.

Hearthstone läser `%LOCALAPPDATA%\Blizzard\Hearthstone\log.config` vid start; ett `[Power]`-avsnitt med `LogLevel=1` och `FilePrinting=true` får det att skriva varje spels tillståndsändringar till `<install>\Logs\Power.log` (nyare klienter lägger varje starts loggar i en egen mapp, `Logs\Hearthstone_<date>\`). Det här är den dokumenterade felsökningsloggning som kortspårare har slagit på sedan 2014 (Hearthstone Deck Trackers installation skriver samma avsnitt). `setup()` lägger till avsnittet, med en säkerhetskopia av filen som den var; spelet behöver startas om för att läsa den.

Raderna som används, alla från `GameState.DebugPrintPower()` (`PowerTaskList`-raderna upprepar dem och hoppas över):

```text
D 20:15:01.1234567 GameState.DebugPrintPower() - CREATE_GAME
D 20:15:01.1234567 GameState.DebugPrintPower() -     Player EntityID=2 PlayerID=1 GameAccountId=[hi=1 lo=2]
D 20:15:01.1234567 GameState.DebugPrintGame() - PlayerID=1, PlayerName=Name#1234
D 20:15:02.1234567 GameState.DebugPrintPower() -     FULL_ENTITY - Updating [entityName=... id=4 zone=HAND
                   zonePos=0 cardId=CS2_029 player=1] CardID=CS2_029
D 20:16:00.1234567 GameState.DebugPrintPower() - TAG_CHANGE Entity=GameEntity tag=TURN value=3
D 20:25:00.1234567 GameState.DebugPrintPower() - TAG_CHANGE Entity=Name#1234 tag=PLAYSTATE value=WON
D 20:25:00.1234567 GameState.DebugPrintPower() - TAG_CHANGE Entity=GameEntity tag=STATE value=COMPLETE
```

Spelarens egen sida är den vars startkorthand har sina kort namngivna (motståndarens är dolda), annars den sida som inte är AI:n (konto 0) eller "UNKNOWN HUMAN PLAYER". Raderna bär bara tiden på dygnet; datumet är dagens. Inga positioner.

Varje rad i Power.log sparas helt i sessionens råa sidfil (3DHeats konverterarregel), med `PowerTaskList`-upprepningarna, alternativ, val och entitetsuppdateringar inräknade: `type` är metoden som skrev den (`GameState.DebugPrintPower`, `PowerTaskList.DebugPrintPower`, `GameState.DebugPrintOptions`, ...). Varje annan logg som spelet skriver bredvid den - `LoadingScreen.log`, `Decks.log`, `Zone.log`, `Arena.log`, ..., var och en där när log.config begär det (kortspårare gör ofta det) - följs på samma sätt och sparas med sitt namn i `log`.

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

`bad_lines`, `games`, `longest_game_turns`, `losses`, `ties`, `turns`, `wins`

En nyckel i klammer fylls i vid körning (`score.{team}` är en nyckel per lag). Nycklar som koden tar från en tabell med spelets fält eller från spelets egna statistiknamn finns inte i listan; "Vad som spelas in" ovan nämner dem.

## Fullständighet {#completeness}

watchern följer 3DHeats [konverterarregel](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md): det källan innehåller läses eller sparas, aldrig slängs. Utöver raderna sparas varje paket, sida, rad eller svar som adaptern tar emot helt i sessionens `heat.raw.parquet` (kolumnerna `time`, `ms`, `type`, `used`, `payload`, `text` och sedan eventuella fält som sparats med namn; `used` markerar det som också blev rader), och `meta.json`:s `selfCheck.completeness` räknar varje `type` - `lost` är 0.

**Läses**

- `CREATE_GAME`, spelarna (entitet, spelar-id, konto; konto 0 är AI:n) och deras namn (`DebugPrintGame`)
- vilken sida som är spelarens, ur de namngivna korten i startkorthanden
- `TAG_CHANGE` för TURN, PLAYSTATE (won, lost, tied) och STATE COMPLETE: turer, resultat, motståndare

**Sparas råa**

- varje Power.log-rad helt, `type` = metoden som skrev den (`GameState.DebugPrintPower`, `PowerTaskList.DebugPrintPower`, `GameState.DebugPrintGame`, `GameState.DebugPrintOptions`, `GameState.SendChoices`, `GameState.DebugPrintEntityChoices`, `PowerProcessor.DoTaskListForCard`, ...), `log` `Power`, `used` där den blev en rad: varje kort som spelats, dragits och visats, varje taggändring, attack, alternativ och val finns här, ännu inte i rader
- varje rad i de andra loggarna i samma mapp (`LoadingScreen`, `Decks`, `Zone`, `Arena`, `Achievements`, `FullScreenFX`, ... - vilka log.config än slår på), samma `type`, med loggens namn i `log`
- en rad utan nivå och tid på dygnet som `untimed`, en utan metod som `untagged`

**Finns inte**

- positioner: ett kortspel har inga
- motståndarens dolda kort: loggen namnger ett kort först när det har visats
- loggar som log.config inte slår på: `setup` frågar bara efter [Power]; de andra loggarna kommer när ett annat verktyg (en kortspårare) har slagit på dem
- loggar från tidigare starter: varje start skriver en ny mapp; de som är äldre än den här körningen av spelet läses inte igen

**Storlek**: Power.log med Verbose är ungefär 1-5 MB per spel, 10-40 MB per timme spelande; de andra loggarna tillför lite; zstd i `heat.raw.parquet` gör det ungefär en tiondel eller mindre (raderna upprepar sig mycket)

## Verifierat {#verified}

testad på syntetiska Power.log-rader i spelets format; ännu inte testad mot spelet

## Källa {#source}

[heat3d_watch/adapters/hearthstone.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/hearthstone.py)

<!-- Generated from the adapter by tools/gen_game_pages.py; change the adapter and run it again rather than editing this page. -->
