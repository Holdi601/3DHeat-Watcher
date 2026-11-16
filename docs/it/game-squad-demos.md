---
title: "Squad (replay)"
nav_order: 40
lang: "it"
source: game-squad-demos.md
source_hash: "ddec19ea89bf"
nav_exclude: true
search_exclude: true
---
# Squad (replay) {#squad-replays}

Dopo una partita di Squad, il watcher trasforma il replay che il gioco ha salvato in file che puoi guardare su una mappa nel visualizzatore 3DHeat.

*Dettagli tecnici: adattatore `squad-demos`, tipo [`replay`](sources-and-rules.md); resta sempre attivo (non aspetta l'avvio di un gioco) e cerca nuovi dati ogni 5 s.*

## Cosa viene registrato {#what-is-recorded}

- la posizione, l'imbardata del corpo e la velocità di ogni giocatore ogni volta che il server la replica (fino a 8 volte al secondo), a piedi e su veicoli di terra
- il nome, la squadra, la fazione e il plotone di ogni giocatore, seguendo i cambi di squadra
- non: il movimento degli elicotteri, uccisioni e dispositivi piazzati - vedi il README del lettore

## Da dove arriva {#where-it-comes-from}

i demo di server che Squad registra con il comando da amministratore AdminDemoRec: &lt;server&gt;/SquadGame/Saved/Demos/\*.replay, letti dal lettore esterno `heat3d-squad-demo` (exporters/ext/squad-demo)

## Come attivarlo {#how-to-switch-it-on}

registra sul server: dai all'amministratore il permesso `demos` in Admins.cfg, poi AdminDemoRec &lt;nome&gt; e AdminDemoStop nella console del gioco; copia qui il demo e installa il lettore: pip install -e &lt;3DHeat&gt;/exporters/ext/squad-demo

Impostazioni dalle variabili d'ambiente:

- `HEAT3D_SQUAD_DEMO`: la cartella del convertitore (un clone o una versione estratta), quando non è installato o non si trova accanto al watcher

## Come funziona {#how-it-works}

Replay e demo: ciò che un gioco salva di una partita, convertito una volta che la partita è finita.

Un replay contiene tutto ciò che un'interfaccia in tempo reale trattiene nei giochi multiplayer - la posizione di ogni giocatore, ogni uccisione nel punto in cui è avvenuta - ed è un file che il gioco scrive per i suoi giocatori, quindi leggerlo non tocca nulla nel gioco. Il watcher controlla le cartelle in cui i giochi li salvano, attende che un nuovo file smetta di crescere (altrimenti il gioco lo sta ancora scrivendo) e lo converte in un thread di lavoro, così una conversione lunga non blocca il resto del watcher.

La prima volta che una cartella viene vista, i replay già presenti vengono solo registrati, non convertiti: chi ha anni di demo troverebbe altrimenti il watcher occupato per un giorno. `python -m heat3d_watch replays <id adattatore> [cartella]` converte quelli esistenti su richiesta.

#### Squad {#squad}

I server dedicati di Squad registrano un demo di una partita quando un amministratore con il permesso `demos` esegue AdminDemoRec &lt;nome&gt; (e AdminDemoStop), in `<server>/SquadGame/Saved/Demos/<nome>.replay` - un replay di rete di Unreal Engine che contiene ciò che il server ha replicato, compreso il movimento di ogni giocatore.

Il watcher non li legge da solo: lo fa un lettore esterno (il lettore demo 3DHeat Squad, `exporters/ext/squad-demo`, comando `heat3d-squad-demo`), un progetto a sé. Viene eseguito su ogni nuovo demo nelle cartelle in cui scrive un server locale, oppure in una cartella aggiunta nelle impostazioni per i demo copiati da un server noleggiato, e produce nella cartella della sessione `<mappa>/<partita>.parquet` e `<partita>.match.json`. Il livello, la mappa, il numero di giocatori e la durata della partita diventano le statistiche della sessione.

Lo stesso modulo serve anche: [Counter-Strike 2 (replay)](game-cs2-demos.md), [Dota 2 (replay)](game-dota-replays.md), [War Thunder (replay)](game-warthunder-replays.md), [World of Tanks (replay)](game-wot-replays.md), [World of Warships (replay)](game-wows-replays.md).

## Posizioni e assi {#positions-and-axes}

| | |
|---|---|
| Posizioni registrate | sì |
| Asse verticale | `z` |
| Unità | unità Unreal (centimetri) |
| Specchiato per il visualizzatore | nessuno |
| Scala delle unità (`scale`: il visualizzatore moltiplica le posizioni per questo valore) | 1 |

Questi valori vanno in `meta.json` di ogni sessione (`axes`) e, quando la sessione ha posizioni, nel footer di `heat.parquet`, così il visualizzatore 3DHeat ruota e scala le righe da solo - vedi [I dati](the-data.md).

## Multigiocatore {#multiplayer}

- Segnato come giocato online (`multiplayer`): **sì**. `games --markdown` lo mostra come "consentito (legge solo ciò che il gioco pubblica)".
- Tipo `replay`: legge solo ciò che il gioco o la piattaforma consegnano (replay e demo che il gioco salva), quindi registra anche nel gioco online oltre che offline; il contrassegno decide soltanto se la memoria può mai essere letta.
- Memoria: **mai** letta da questo adattatore. Solo gli adattatori `memory` leggono la memoria, e mai per un gioco segnato come giocato online - vedi [Fonti e regole](sources-and-rules.md).

## Statistiche registrate {#statistics-recorded}

Chiavi di statistica che il codice di questo adattatore imposta per nome (`stats` di ogni sessione in `meta.json` e la tabella `stats` di `watcher.sqlite`):

`layer`, `map`, `match_seconds`, `players`

Una chiave tra parentesi graffe viene completata durante l'esecuzione (`score.{team}` è una chiave per ogni squadra). Le chiavi che il codice prende da una tabella dei campi del gioco o dai nomi di statistica del gioco non sono in questo elenco; "Cosa viene registrato" sopra le nomina.

## Completezza {#completeness}

Il convertitore che questo adattatore esegue segue la [regola del convertitore](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md) di 3DHeat: ciò che il replay contiene viene letto o conservato, mai scartato - letto nella tabella e nel documento della partita, tutto il resto conservato intero nei dati grezzi accanto ad essi, conteggiato in `selfCheck.completeness` del documento della partita. La documentazione del convertitore elenca ciò che legge, conserva grezzo e non sa leggere.

## Verificato {#verified}

il lettore è controllato su demo pubblici di server (il movimento concorda con la velocità che porta con sé; la squadra di ogni riga corrisponde alla fazione del suo soldato) e dai test su demo costruiti; questo collegamento è testato con un comando sostitutivo

## Fonte {#source}

[heat3d_watch/adapters/replays.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/replays.py)

<!-- Generato dall'adattatore da tools/gen_game_pages.py; per cambiarlo modifica l'adattatore ed eseguilo di nuovo invece di modificare questa pagina. -->
