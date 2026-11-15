---
title: "Hearthstone (loggfiler)"
nav_order: 25
lang: "no"
source: game-hearthstone.md
source_hash: "e79c19776947"
nav_exclude: true
search_exclude: true
---
# Hearthstone (loggfiler) {#hearthstone-log-files}

Mens du spiller Hearthstone, leser watcheren filene spillet skriver, og lagrer det som skjedde, slik at du senere kan se på det som statistikk og en tidslinje.

*Tekniske detaljer: adapter `hearthstone`, type [`log`](sources-and-rules.md); den kjører mens `Hearthstone.exe` går og ser etter nye data hvert 0,5 s.*

## Hva som tas opp {#what-is-recorded}

- spillstart og -slutt, med resultat (vunnet, tapt, uavgjort), runder og motstanderens navn
- hver runde
- hver linje i Power.log og de andre loggene hel i `heat.raw.parquet`
- spill, seiere, tap, uavgjort, runder, lengste spill

## Hvor det kommer fra {#where-it-comes-from}

&lt;installasjon>\Logs\Power.log (eller Logs\Hearthstone_\*\Power.log), skrevet når %LOCALAPPDATA%\Blizzard\Hearthstone\log.config har en [Power]-seksjon, og hver annen \*.log spillet skriver der

## Slik slår du det på {#how-to-switch-it-on}

`python -m heat3d_watch setup hearthstone --apply` legger til [Power]-logging i %LOCALAPPDATA%\Blizzard\Hearthstone\log.config (sikkerhetskopi lagres); start spillet på nytt

Skriv kommandoen i en terminal åpnet i watcherens mappe (se [Før du starter](before-you-start.md)). Hvis den feiler, sier siste linje hvorfor; [Installere og kjøre](installing-and-running.md) dekker de vanlige årsakene.

`python -m heat3d_watch setup hearthstone` lister filene den ville endret; `python -m heat3d_watch setup hearthstone --apply` endrer dem og beholder originalen som `<fil>.heat3d-backup` (se [Kommandoer](commands.md#setup)). Den skriver `hearthstone: changed: ...` for hver endring, eller `hearthstone: nothing to change` når den allerede er på.

## Slik fungerer det {#how-it-works}

Hearthstone: spillets Power.log, som det skriver når `log.config` ber om det.

Hearthstone leser `%LOCALAPPDATA%\Blizzard\Hearthstone\log.config` ved start; en `[Power]`-seksjon med `LogLevel=1` og `FilePrinting=true` får den til å skrive hvert spills tilstandsendringer til `<installasjon>\Logs\Power.log` (nyere klienter legger hver starts logger i en egen mappe, `Logs\Hearthstone_<dato>\`). Dette er den dokumenterte feilsøkingsloggingen kortstokksportere har slått på siden 2014 (Hearthstone Deck Trackers oppsett skriver samme seksjon). `setup()` legger til seksjonen, med en sikkerhetskopi av filen slik den var; spillet må startes på nytt for å lese den.

Linjene som brukes, alle fra `GameState.DebugPrintPower()` (`PowerTaskList`-linjene gjentar dem og hoppes over):

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

Spillerens egen side er den hvis startende hånd har sine kort navngitt (motstanderens er skjult), ellers siden som ikke er AI (konto 0) eller "UNKNOWN HUMAN PLAYER". Linjene har bare klokkeslett; datoen er dagens. Ingen posisjoner.

Hver linje i Power.log tas vare på hel i øktens rå sidefil (3DHeats konverteringsregel), `PowerTaskList`-gjentakelsene, valg, alternativer og enhetsoppdateringer inkludert: `type` er metoden som skrev den (`GameState.DebugPrintPower`, `PowerTaskList.DebugPrintPower`, `GameState.DebugPrintOptions`, ...). Enhver annen logg spillet skriver ved siden av den - `LoadingScreen.log`, `Decks.log`, `Zone.log`, `Arena.log`, ..., hver der når log.config ber om det (kortstokksportere slår ofte på dem) - følges på samme måte og tas vare på med sitt navn i `log`.

## Posisjoner og akser {#positions-and-axes}

| | |
|---|---|
| Posisjoner tatt opp | nei |
| Opp-akse | `y` |
| Enheter | ingen posisjoner tatt opp |
| Speilet for vieweren | ingen |
| Enhetsskala (`scale`: vieweren ganger posisjonene med den) | 1 |

Disse legges i hver økts `meta.json` (`axes`) og, når økten har posisjoner, i `heat.parquet`s fotnote, slik at 3DHeat-vieweren selv vender og skalerer radene - se [Dataene](the-data.md).

## Flerspiller {#multiplayer}

- Merket som spilt på nett (`multiplayer`): **ja**. `games --markdown` viser dette som "tillatt (leser bare det spillet publiserer)".
- Type `log`: den leser bare det spillet eller plattformen gir ut (filer spillet skriver mens det kjører), så den tar opp også i nettspill, ikke bare frakoblet; flagget avgjør bare om minne noensinne får leses.
- Minne: **aldri** lest av denne adapteren. Bare `memory`-adaptere leser minne, og aldri for et spill merket som spilt på nett - se [Kilder og regler](sources-and-rules.md).

## Statistikk som registreres {#statistics-recorded}

Statistikknøkler som adapterens kode setter med navn (hver økts `stats` i `meta.json` og tabellen `stats` i `watcher.sqlite`):

`bad_lines`, `games`, `longest_game_turns`, `losses`, `ties`, `turns`, `wins`

En nøkkel i klammer fullføres ved kjøretid (`score.{team}` er én nøkkel per lag). Nøkler som koden henter fra en tabell over spillets felt, eller fra spillets egne statistikknavn, står ikke på denne listen; "Hva som tas opp" over nevner dem.

## Fullstendighet {#completeness}

Watcheren følger 3DHeats [konverteringsregel](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md): det kilden inneholder, leses eller tas vare på, og slippes aldri. I tillegg til radene tas hver pakke, side, linje eller svar adapteren mottar, vare på hel i øktens `heat.raw.parquet` (kolonnene `time`, `ms`, `type`, `used`, `payload`, `text`, og alle felt tatt vare på med navn; `used` markerer det som også ble rader), og `meta.json`s `selfCheck.completeness` teller hver `type` - `lost` er 0.

**Leses**

- `CREATE_GAME`, spillerne (entitet, spiller-id, konto; konto 0 er AI-en) og deres navn (`DebugPrintGame`)
- hvilken side som er spillerens, ut fra de navngitte kortene i startende hånd
- `TAG_CHANGE` for TURN, PLAYSTATE (won, lost, tied) og STATE COMPLETE: runder, resultat, motstander

**Tatt vare på rått**

- hver Power.log-linje hel, `type` = metoden som skrev den (`GameState.DebugPrintPower`, `PowerTaskList.DebugPrintPower`, `GameState.DebugPrintGame`, `GameState.DebugPrintOptions`, `GameState.SendChoices`, `GameState.DebugPrintEntityChoices`, `PowerProcessor.DoTaskListForCard`, ...), `log` `Power`, `used` der den ble en rad: hvert kort spilt, trukket og avslørt, hver tagendring, angrep, alternativ og valg er her, ikke i rader ennå
- hver linje i de andre loggene i samme mappe (`LoadingScreen`, `Decks`, `Zone`, `Arena`, `Achievements`, `FullScreenFX`, ... - hva log.config slår på), samme `type`-er, med loggens navn i `log`
- en linje uten nivå og klokkeslett som `untimed`, en uten metode som `untagged`

**Ikke tilgjengelig**

- posisjoner: et kortspill har ingen
- motstanderens skjulte kort: loggen nevner et kort først når det er avslørt
- logger log.config ikke slår på: `setup` spør bare om [Power]; de andre loggene kommer når et annet verktøy (en kortstokksporer) har slått dem på
- logger fra tidligere starter: hver start skriver en ny mappe; de som er eldre enn denne kjøringen av spillet, leses ikke på nytt

**Størrelse**: Power.log med Verbose er omtrent 1-5 MB per spill, 10-40 MB i timen med spilling; de andre loggene legger lite til; zstd i `heat.raw.parquet` gjør det omtrent en tiendedel eller mindre (linjene gjentar seg mye)

## Verifisert {#verified}

testet på syntetiske Power.log-linjer i spillets format; ikke testet mot spillet

## Kilde {#source}

[heat3d_watch/adapters/hearthstone.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/hearthstone.py)

<!-- Generated from the adapter by tools/gen_game_pages.py; change the adapter and run it again rather than editing this page. -->
