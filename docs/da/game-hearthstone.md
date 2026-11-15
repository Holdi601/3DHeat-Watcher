---
title: "Hearthstone (logfiler)"
nav_order: 25
lang: "da"
source: game-hearthstone.md
source_hash: "e79c19776947"
nav_exclude: true
search_exclude: true
---
# Hearthstone (logfiler) {#hearthstone-log-files}

Mens du spiller Hearthstone, læser watcheren de filer, spillet skriver, og gemmer det, der skete, så du senere kan se det som statistik og en tidslinje.

*Tekniske detaljer: adapter `hearthstone`, type [`log`](sources-and-rules.md); den kører, mens `Hearthstone.exe` kører, og leder efter nye data hver 0.5 s.*

## Hvad der registreres {#what-is-recorded}

- spillets start og slut med resultatet (vundet, tabt, uafgjort), runder og modstanderens navn
- hver runde
- hver linje i Power.log og de andre logs hel i heat.raw.parquet
- spil, sejre, nederlag, uafgjorte, runder, længste spil

## Hvor data kommer fra {#where-it-comes-from}

&lt;install>\Logs\Power.log (eller Logs\Hearthstone_\*\Power.log), skrevet når %LOCALAPPDATA%\Blizzard\Hearthstone\log.config har et [Power]-afsnit, og alle andre \*.log, spillet skriver der

## Sådan slår du det til {#how-to-switch-it-on}

`python -m heat3d_watch setup hearthstone --apply` tilføjer [Power]-logning til %LOCALAPPDATA%\Blizzard\Hearthstone\log.config (sikkerhedskopi gemmes); genstart spillet

Skriv kommandoen i en terminal, der er åbnet i watcherens mappe (se [Før du starter](before-you-start.md)). Hvis den fejler, siger den sidste linje hvorfor; [Installation og kørsel](installing-and-running.md) dækker de almindelige årsager.

`python -m heat3d_watch setup hearthstone` viser, hvilke filer den ville ændre; `python -m heat3d_watch setup hearthstone --apply` ændrer dem og gemmer originalen som `<fil>.heat3d-backup` (se [Kommandoer](commands.md#setup)). Den skriver `hearthstone: changed: ...` for hver ændring, eller `hearthstone: nothing to change`, når den allerede er slået til.

## Sådan virker det {#how-it-works}

Hearthstone: spillets Power.log, som det skriver, når `log.config` beder om det.

Hearthstone læser `%LOCALAPPDATA%\Blizzard\Hearthstone\log.config` ved start;
et `[Power]`-afsnit med `LogLevel=1` og `FilePrinting=true` får det til at skrive
hver spilles tilstandsændringer til `<install>\Logs\Power.log` (nyere klienter lægger
hver starts logs i en mappe for sig selv, `Logs\Hearthstone_<dato>\`). Dette er den
dokumenterede fejlsøgningslogning, kortsporings-værktøjer har slået til siden 2014
(Hearthstone Deck Trackers opsætning skriver det samme afsnit). `setup()` tilføjer
afsnittet med en sikkerhedskopi af filen, som den var; spillet skal genstartes, før det læses.

Linjerne der bruges, alle fra `GameState.DebugPrintPower()` (`PowerTaskList`-linjerne
gentager dem og springes over):

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

Spillerens egen side er den, hvis startshånd har sine kort navngivet
(modstanderens er skjult), ellers den side, der ikke er AI'en (konto 0) eller
"UNKNOWN HUMAN PLAYER". Linjerne har kun tidspunktet på dagen; datoen er i dag.
Ingen positioner.

Hver linje i Power.log gemmes hel i kørslens rå sidefil (3DHeats konverterregel),
med `PowerTaskList`-gentagelserne, valgmulighederne og entitetsopdateringerne med;
`type` er den metode, der skrev den (`GameState.DebugPrintPower`,
`PowerTaskList.DebugPrintPower`, `GameState.DebugPrintOptions`, ...). Enhver anden log,
spillet skriver ved siden af den - `LoadingScreen.log`, `Decks.log`, `Zone.log`,
`Arena.log`, ... - hver der er slået til, når log.config beder om det (kortsporingsværktøjer
gør ofte det), følges på samme måde og gemmes med sit navn i `log`.

## Positioner og akser {#positions-and-axes}

| | |
|---|---|
| Positioner registreret | nej |
| Op-akse | `y` |
| Enheder | ingen positioner registreret |
| Spejlet til vieweren | ingen |
| Enhedsskala (`scale`: vieweren ganger positionerne med den) | 1 |

Disse går ind i hver kørsels `meta.json` (`axes`) og, når kørslen har positioner, i `heat.parquet`s footer, så 3DHeat-vieweren selv drejer og skalerer rækkerne - se [Dataene](the-data.md).

## Flerspiller {#multiplayer}

- Markeret som spillet online (`multiplayer`): **ja**. `games --markdown` viser det som "tilladt (læser kun det spillet udgiver)".
- Type `log`: den læser kun det spillet eller platformen udleverer (filer spillet skriver, mens det kører), så den optager også i onlinespil og offline; flaget afgør kun, om hukommelse nogensinde må læses.
- Hukommelse: læses **aldrig** af denne adapter. Kun `memory`-adaptere læser hukommelse, og aldrig for et spil markeret som spillet online - se [Kilder og regler](sources-and-rules.md).

## Registrerede statistikker {#statistics-recorded}

Statistiknøgler, som adapterens kode sætter ved navn (hver kørsels `stats` i `meta.json` og tabellen `stats` i `watcher.sqlite`):

`bad_lines`, `games`, `longest_game_turns`, `losses`, `ties`, `turns`, `wins`

En nøgle i klammer udfyldes under kørslen (`score.{team}` er én nøgle pr. hold). Nøgler som koden tager fra en tabel over spillets felter eller fra spillets egne statistiknavne står ikke på listen; "Hvad der registreres" ovenfor nævner dem.

## Fuldstændighed {#completeness}

Watcheren følger 3DHeats [konverterregel](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md): det kilden indeholder, læses eller gemmes, og aldrig smides væk. Ud over rækkerne gemmes hver pakke, side, linje eller svar, adapteren modtager, hel i kørslens `heat.raw.parquet` (kolonnerne `time`, `ms`, `type`, `used`, `payload`, `text` og derefter felter, der gemmes under deres navn; `used` markerer, hvad der også blev til rækker), og `selfCheck.completeness` i `meta.json` tæller hver `type` - `lost` er 0.

**Læst**

- `CREATE_GAME`, spillerne (entitet, spiller-id, konto; konto 0 er AI'en) og deres navne (`DebugPrintGame`)
- hvilken side der er spillerens, ud fra de navngivne kort i startshånden
- `TAG_CHANGE` for TURN, PLAYSTATE (vundet, tabt, uafgjort) og STATE COMPLETE: runder, resultat, modstander

**Gemt råt**

- hver Power.log-linje hel, `type` = metoden, der skrev den (`GameState.DebugPrintPower`, `PowerTaskList.DebugPrintPower`, `GameState.DebugPrintGame`, `GameState.DebugPrintOptions`, `GameState.SendChoices`, `GameState.DebugPrintEntityChoices`, `PowerProcessor.DoTaskListForCard`, ...), `log` `Power`, `used` hvor den blev til en række: hvert kort spillet, trukket og afsløret, hver tilstandsændring, angreb, valg og valgmulighed står her, endnu ikke i rækker
- hver linje i de andre logs i samme mappe (`LoadingScreen`, `Decks`, `Zone`, `Arena`, `Achievements`, `FullScreenFX`, ... - hvad log.config nu slår til), samme `type`'er, med logets navn i `log`
- en linje uden niveau og tidspunkt på dagen som `untimed`, en uden metode som `untagged`

**Ikke tilgængeligt**

- positioner: et kortspil har ingen
- modstanderens skjulte kort: loggen navngiver et kort først, når det er afsløret
- logs, log.config ikke slår til: `setup` beder kun om [Power]; de andre logs kommer, når et andet værktøj (et kortsporingsværktøj) har slået dem til
- logs fra tidligere starter: hver start skriver en ny mappe; dem, der er ældre end denne kørsel af spillet, læses ikke igen

**Størrelse**: Power.log med Verbose fylder cirka 1-5 MB pr. spil, 10-40 MB i timen spillet; de andre logs tilføjer lidt; zstd i heat.raw.parquet gør det cirka til en tiendedel eller mindre (linjerne gentager sig meget)

## Verificeret {#verified}

testet på syntetiske Power.log-linjer i spillets format; ikke testet mod spillet

## Kilde {#source}

[heat3d_watch/adapters/hearthstone.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/hearthstone.py)

<!-- Genereret fra adapteren af tools/gen_game_pages.py; ret adapteren og kør den igen i stedet for at redigere denne side. -->
