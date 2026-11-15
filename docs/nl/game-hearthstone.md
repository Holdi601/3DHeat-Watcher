---
title: "Hearthstone (logbestanden)"
nav_order: 25
lang: "nl"
source: game-hearthstone.md
source_hash: "e79c19776947"
nav_exclude: true
search_exclude: true
---
# Hearthstone (logbestanden) {#hearthstone-log-files}

Terwijl je Hearthstone speelt, leest de watcher de bestanden die het spel schrijft en bewaart hij wat er gebeurde, zodat je het later kunt bekijken als statistieken en een tijdlijn.

*Technische details: adapter `hearthstone`, soort [`log`](sources-and-rules.md); hij draait zolang `Hearthstone.exe` draait en zoekt elke 0,5 s naar nieuwe gegevens.*

## Wat wordt opgenomen {#what-is-recorded}

- begin en einde van het spel, met de uitslag (gewonnen, verloren, gelijkspel), de beurten en de naam van de tegenstander
- elke beurt
- elke regel van Power.log en de andere logs helemaal, in heat.raw.parquet
- spellen, overwinningen, nederlagen, gelijkspelen, beurten, langste spel

## Waar het vandaan komt {#where-it-comes-from}

&lt;install>\Logs\Power.log (of Logs\Hearthstone_\*\Power.log), geschreven zodra %LOCALAPPDATA%\Blizzard\Hearthstone\log.config een [Power]-sectie heeft, en elk ander \*.log dat het spel daar schrijft

## Hoe je het aanzet {#how-to-switch-it-on}

`python -m heat3d_watch setup hearthstone --apply` voegt [Power]-logging toe aan %LOCALAPPDATA%\Blizzard\Hearthstone\log.config (back-up bewaard); start het spel opnieuw

Typ het commando in een terminal die geopend is in de map van de watcher (zie [Voordat je begint](before-you-start.md)). Als het mislukt, zegt de laatste regel waarom; [Installeren en draaien](installing-and-running.md) behandelt de gebruikelijke oorzaken.

`python -m heat3d_watch setup hearthstone` toont welke bestanden het zou veranderen; `python -m heat3d_watch setup hearthstone --apply` verandert ze en bewaart het origineel als `<file>.heat3d-backup` (zie [Commando's](commands.md#setup)). Het toont `hearthstone: changed: ...` voor elke wijziging, of `hearthstone: nothing to change` als het al aan staat.

## Hoe het werkt {#how-it-works}

Hearthstone: het Power.log van het spel, dat het schrijft zodra `log.config` erom vraagt.

Hearthstone leest `%LOCALAPPDATA%\Blizzard\Hearthstone\log.config` bij het starten; een `[Power]`-sectie met `LogLevel=1` en `FilePrinting=true` zorgt dat het elke statuswijziging van elk spel schrijft naar `<install>\Logs\Power.log` (nieuwere clients zetten de logs van elke start in een eigen map, `Logs\Hearthstone_<date>\`). Dit is de gedocumenteerde debug-logging die deck trackers sinds 2014 aanzetten (de instelling van Hearthstone Deck Tracker schrijft dezelfde sectie). `setup()` voegt de sectie toe, met een back-up van het bestand zoals het was; het spel moet opnieuw starten om hem te lezen.

De gebruikte regels, allemaal van `GameState.DebugPrintPower()` (de `PowerTaskList`-regels herhalen ze en worden overgeslagen):

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

De eigen kant van de speler is die waarvan de startkaarten bij naam zijn genoemd (die van de tegenstander zijn verborgen), anders de kant die niet de AI is (account 0) of "UNKNOWN HUMAN PLAYER". Regels dragen alleen de tijd van de dag; de datum is die van vandaag. Geen posities.

Elke regel van Power.log wordt helemaal bewaard in de ruwe bijlage van de sessie (de converterregel van 3DHeat), de `PowerTaskList`-herhalingen, opties, keuzes en entiteitsupdates inbegrepen: `type` is de methode die hem schreef (`GameState.DebugPrintPower`, `PowerTaskList.DebugPrintPower`, `GameState.DebugPrintOptions`, ...). Elk ander log dat het spel ernaast schrijft - `LoadingScreen.log`, `Decks.log`, `Zone.log`, `Arena.log`, ..., elk daar zodra log.config erom vraagt (deck trackers doen dat vaak) - wordt op dezelfde manier gevolgd en met zijn naam in `log` bewaard.

## Posities en assen {#positions-and-axes}

| | |
|---|---|
| Posities opgenomen | nee |
| Opwaartse as | `y` |
| Eenheden | geen posities opgenomen |
| Gespiegeld voor de viewer | geen |
| Eenheidsschaal (`scale`: de viewer vermenigvuldigt posities daarmee) | 1 |

Deze gaan naar de `meta.json` van elke sessie (`axes`) en, als de sessie posities heeft, naar de footer van `heat.parquet`, zodat de 3DHeat-viewer de rijen zelf draait en schaalt - zie [De data](the-data.md).

## Multiplayer {#multiplayer}

- Gemarkeerd als online gespeeld (`multiplayer`): **ja**. `games --markdown` toont dit als "allowed (reads only what the game publishes)".
- Soort `log`: hij leest alleen wat het spel of platform uitgeeft (bestanden die het spel schrijft terwijl het draait), dus hij legt ook online spel vast, net als offline spel; de vlag bepaalt alleen of geheugen ooit gelezen mag worden.
- Geheugen: **nooit** gelezen door deze adapter. Alleen `memory`-adapters lezen geheugen, en nooit voor een spel dat als online gespeeld is gemarkeerd - zie [Bronnen en regels](sources-and-rules.md).

## Opgenomen statistieken {#statistics-recorded}

Statistiekensleutels die de code van deze adapter bij naam zet (de `stats` van elke sessie in `meta.json` en de `stats`-tabel van `watcher.sqlite`):

`bad_lines`, `games`, `longest_game_turns`, `losses`, `ties`, `turns`, `wins`

Een sleutel tussen accolades wordt tijdens het draaien ingevuld (`score.{team}` is één sleutel per team). Sleutels die de code uit een tabel met de velden van het spel of uit de eigen statistiekennamen van het spel haalt, staan niet in deze lijst; "Wat wordt opgenomen" hierboven noemt ze.

## Volledigheid {#completeness}

De watcher volgt de [converterregel](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md) van 3DHeat: wat de bron bevat wordt gelezen of bewaard, nooit weggegooid. Naast de rijen wordt elk pakket, elke pagina, regel of elk antwoord dat de adapter ontvangt helemaal bewaard in de `heat.raw.parquet` van de sessie (kolommen `time`, `ms`, `type`, `used`, `payload`, `text`, plus elk veld dat op naam wordt bewaard; `used` markeert wat ook rijen werd), en `selfCheck.completeness` in `meta.json` telt elk `type` - `lost` is 0.

**Gelezen**

- `CREATE_GAME`, de spelers (entiteit, speler-id, account; account 0 is de AI) en hun namen (`DebugPrintGame`)
- wiens kant de speler is, uit de benoemde kaarten van de startkaarten
- `TAG_CHANGE` van TURN, PLAYSTATE (gewonnen, verloren, gelijkspel) en STATE COMPLETE: beurten, uitslag, tegenstander

**Ruw bewaard**

- elke Power.log-regel helemaal, `type` = de methode die hem schreef (`GameState.DebugPrintPower`, `PowerTaskList.DebugPrintPower`, `GameState.DebugPrintGame`, `GameState.DebugPrintOptions`, `GameState.SendChoices`, `GameState.DebugPrintEntityChoices`, `PowerProcessor.DoTaskListForCard`, ...), `log` `Power`, `used` waar hij een rij werd: elke gespeelde, getrokken en onthulde kaart, elke tagwijziging, aanval, optie en keuze staat hier, nog niet in rijen
- elke regel van de andere logs in dezelfde map (`LoadingScreen`, `Decks`, `Zone`, `Arena`, `Achievements`, `FullScreenFX`, ... - wat log.config ook aanzet), dezelfde `type`s, met de naam van het log in `log`
- een regel zonder het niveau en de tijd van de dag als `untimed`, een regel zonder methode als `untagged`

**Niet beschikbaar**

- posities: een kaartspel heeft er geen
- de verborgen kaarten van de tegenstander: het log noemt een kaart pas als hij onthuld is
- logs die log.config niet aanzet: `setup` vraagt alleen om [Power]; de andere logs komen wanneer een ander hulpmiddel (een deck tracker) ze aanzet
- logs van eerdere starts: elke start schrijft een nieuwe map; die ouder zijn dan deze run van het spel worden niet opnieuw gelezen

**Grootte**: Power.log met Verbose is ongeveer 1-5 MB per spel, 10-40 MB per uur spelen; de andere logs voegen weinig toe; zstd in heat.raw.parquet maakt het ongeveer een tiende of minder (de regels herhalen zich veel)

## Gecontroleerd {#verified}

getest op verzonnen Power.log-regels in het formaat van het spel; nog niet getest tegen het spel

## Bron {#source}

[heat3d_watch/adapters/hearthstone.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/hearthstone.py)

<!-- Generated from the adapter by tools/gen_game_pages.py; change the adapter and run it again rather than editing this page. -->
