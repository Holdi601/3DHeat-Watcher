---
title: "Hearthstone (file di log)"
nav_order: 25
lang: "it"
source: game-hearthstone.md
source_hash: "e79c19776947"
nav_exclude: true
search_exclude: true
---
# Hearthstone (file di log) {#hearthstone-log-files}

Mentre giochi a Hearthstone, il watcher legge i file che il gioco scrive e salva ciò che è successo, così puoi guardarlo più tardi come statistiche e una timeline.

*Dettagli tecnici: adattatore `hearthstone`, tipo [`log`](sources-and-rules.md); funziona mentre `Hearthstone.exe` è in esecuzione e cerca nuovi dati ogni 0,5 s.*

## Cosa viene registrato {#what-is-recorded}

- inizio e fine della partita, con il risultato (vinta, persa, pareggiata), i turni e il nome dell'avversario
- ogni turno
- ogni riga di Power.log e degli altri log intera in heat.raw.parquet
- partite, vittorie, sconfitte, pareggi, turni, partita più lunga

## Da dove arriva {#where-it-comes-from}

&lt;installazione&gt;\Logs\Power.log (o Logs\Hearthstone_\*\Power.log), scritto una volta che %LOCALAPPDATA%\Blizzard\Hearthstone\log.config ha una sezione [Power], e ogni altro \*.log che il gioco scrive lì

## Come attivarlo {#how-to-switch-it-on}

`python -m heat3d_watch setup hearthstone --apply` aggiunge la registrazione [Power] a %LOCALAPPDATA%\Blizzard\Hearthstone\log.config (con copia di backup); riavvia il gioco

Digita il comando in un terminale aperto nella cartella del watcher (vedi [Prima di iniziare](before-you-start.md)). Se non riesce, l'ultima riga dice perché; [Installazione ed esecuzione](installing-and-running.md) descrive le cause più comuni.

`python -m heat3d_watch setup hearthstone` elenca i file che cambierebbe; `python -m heat3d_watch setup hearthstone --apply` li cambia, conservando l'originale come `<file>.heat3d-backup` (vedi [Comandi](commands.md#setup)). Stampa `hearthstone: changed: ...` per ogni modifica, oppure `hearthstone: nothing to change` se è già attivo.

## Come funziona {#how-it-works}

Hearthstone: il Power.log del gioco, che scrive quando `log.config` lo chiede.

Hearthstone legge `%LOCALAPPDATA%\Blizzard\Hearthstone\log.config` all'avvio;
una sezione `[Power]` con `LogLevel=1` e `FilePrinting=true` lo fa scrivere ogni
cambio di stato di ogni partita in `<installazione>\Logs\Power.log` (i client più recenti mettono
i log di ogni avvio in una cartella propria, `Logs\Hearthstone_<data>\`). Questa è la registrazione di debug
documentata che i deck tracker usano dal 2014 (la configurazione di Hearthstone Deck Tracker scrive la
stessa sezione). `setup()` aggiunge la sezione, con una copia di backup del file com'era; il gioco
deve essere riavviato per leggerla.

Le righe usate, tutte da `GameState.DebugPrintPower()` (le righe `PowerTaskList`
le ripetono e vengono saltate):

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

La parte del giocatore è quella la cui mano iniziale ha le carte con il nome
(quelle dell'avversario sono nascoste), altrimenti il lato che non è l'IA (account 0) o
"UNKNOWN HUMAN PLAYER". Le righe riportano solo l'ora del giorno; la data è quella di oggi.
Nessuna posizione.

Ogni riga di Power.log viene conservata intera nei dati grezzi della sessione (regola del
convertitore di 3DHeat), comprese le ripetizioni di `PowerTaskList`, le opzioni, le scelte e gli
aggiornamenti di entità: `type` è il metodo che l'ha scritta (`GameState.DebugPrintPower`,
`PowerTaskList.DebugPrintPower`, `GameState.DebugPrintOptions`, ...). Ogni altro
log che il gioco scrive accanto - `LoadingScreen.log`, `Decks.log`, `Zone.log`,
`Arena.log`, ..., ciascuno presente quando log.config lo chiede (spesso lo fanno i deck tracker) -
viene seguito allo stesso modo e conservato con il suo nome in `log`.

## Posizioni e assi {#positions-and-axes}

| | |
|---|---|
| Posizioni registrate | no |
| Asse verticale | `y` |
| Unità | nessuna posizione registrata |
| Specchiato per il visualizzatore | nessuno |
| Scala delle unità (`scale`: il visualizzatore moltiplica le posizioni per questo valore) | 1 |

Questi valori finiscono in `meta.json` di ogni sessione (`axes`) e, quando la sessione ha posizioni, nel footer di `heat.parquet`, così il visualizzatore 3DHeat ruota e scala le righe da solo - vedi [I dati](the-data.md).

## Multigiocatore {#multiplayer}

- Segnato come giocato online (`multiplayer`): **sì**. `games --markdown` lo mostra come "consentito (legge solo ciò che il gioco pubblica)".
- Tipo `log`: legge solo ciò che il gioco o la piattaforma consegna (file che il gioco scrive mentre è in esecuzione), quindi registra anche nel gioco online oltre che offline; il flag decide solo se la memoria può mai essere letta.
- Memoria: **mai** letta da questo adattatore. Solo gli adattatori `memory` leggono la memoria, e mai per un gioco segnato come giocato online - vedi [Fonti e regole](sources-and-rules.md).

## Statistiche registrate {#statistics-recorded}

Chiavi di statistica che il codice di questo adattatore imposta per nome (`stats` di ogni sessione in `meta.json` e la tabella `stats` di `watcher.sqlite`):

`bad_lines`, `games`, `longest_game_turns`, `losses`, `ties`, `turns`, `wins`

Una chiave tra parentesi graffe viene completata durante l'esecuzione (`score.{team}` è una chiave per squadra). Le chiavi che il codice prende da una tabella dei campi del gioco o dai nomi di statistica del gioco non sono in questo elenco; "Cosa viene registrato" sopra le nomina.

## Completezza {#completeness}

Il watcher segue la [regola del convertitore](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md) di 3DHeat: ciò che la fonte contiene viene letto o conservato, mai scartato. Oltre alle righe, ogni pacchetto, pagina, riga o risposta che l'adattatore riceve viene conservato intero in `heat.raw.parquet` della sessione (colonne `time`, `ms`, `type`, `used`, `payload`, `text`, poi ogni campo conservato per nome; `used` segna ciò che è diventato anche riga), e `selfCheck.completeness` in `meta.json` conta ogni `type` - `lost` è 0.

**Letto**

- `CREATE_GAME`, i giocatori (entità, id giocatore, account; l'account 0 è l'IA) e i loro nomi (`DebugPrintGame`)
- di quale lato è il giocatore, dalle carte con il nome della mano iniziale
- `TAG_CHANGE` di TURN, PLAYSTATE (vinta, persa, pareggiata) e STATE COMPLETE: turni, risultato, avversario

**Conservato grezzo**

- ogni riga di Power.log intera, `type` = il metodo che l'ha scritta (`GameState.DebugPrintPower`, `PowerTaskList.DebugPrintPower`, `GameState.DebugPrintGame`, `GameState.DebugPrintOptions`, `GameState.SendChoices`, `GameState.DebugPrintEntityChoices`, `PowerProcessor.DoTaskListForCard`, ...), `log` `Power`, `used` dove è diventata una riga: ogni carta giocata, pescata e rivelata, ogni cambio di tag, attacco, opzione e scelta è qui, non ancora in righe
- ogni riga degli altri log nella stessa cartella (`LoadingScreen`, `Decks`, `Zone`, `Arena`, `Achievements`, `FullScreenFX`, ... - tutti quelli che log.config attiva), stessi `type`, con il nome del log in `log`
- una riga senza livello e ora del giorno come `untimed`, una senza metodo come `untagged`

**Non disponibile**

- posizioni: un gioco di carte non ne ha
- le carte nascoste dell'avversario: il log nomina una carta solo quando è rivelata
- i log che log.config non attiva: `setup` chiede solo [Power]; gli altri arrivano quando un altro strumento (un deck tracker) li ha attivati
- i log dei precedenti avvii: ogni avvio scrive una nuova cartella; quelli più vecchi di questa esecuzione del gioco non vengono riletti

**Dimensione**: Power.log con Verbose pesa circa 1-5 MB per partita, 10-40 MB all'ora di gioco; gli altri log aggiungono poco; zstd in heat.raw.parquet lo riduce a circa un decimo o meno (le righe si ripetono molto)

## Verificato {#verified}

testato su righe sintetiche di Power.log nel formato del gioco; non ancora testato con il gioco

## Fonte {#source}

[heat3d_watch/adapters/hearthstone.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/hearthstone.py)

<!-- Generated from the adattatore by tools/gen_game_pages.py; change the adattatore and run it again rather than editing this page. -->
