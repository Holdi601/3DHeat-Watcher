---
title: "War Thunder (replay)"
nav_order: 45
lang: "it"
source: game-warthunder-replays.md
source_hash: "4bf6e2f218cb"
nav_exclude: true
search_exclude: true
---
# War Thunder (replay) {#war-thunder-replays}

Dopo una partita di War Thunder, il watcher trasforma il replay che il gioco ha salvato in file che puoi guardare su una mappa nel visualizzatore 3DHeat.

*Dettagli tecnici: adattatore `warthunder-replays`, tipo [`replay`](sources-and-rules.md); resta sempre attivo (non aspetta l'avvio di un gioco) e cerca nuovi dati ogni 5 s.*

## Cosa viene registrato {#what-is-recorded}

- la posizione e l'assetto di ogni aereo circa 4 volte al secondo (quanti ne contiene il replay)
- le posizioni delle unità di terra dalla sincronizzazione di terra del replay (nei replay del 2026; non in quelli del 2025)
- chi era ogni unità (giocatore, id del veicolo, squadra) quando un'uccisione o un colpo la nomina; uccisioni, morti e colpi nel punto in cui sono avvenuti; chat; la mappa
- uccisioni, morti, punteggio e conquiste dell'autore del replay come statistiche

## Da dove arriva {#where-it-comes-from}

i replay che War Thunder salva: &lt;War Thunder&gt;/Replays/\*.wrpl (con il salvataggio dei replay attivo), convertiti dal convertitore esterno `heat3d-wt-replay` (exporters/ext/warthunder-replay)

## Come attivarlo {#how-to-switch-it-on}

attiva il salvataggio dei replay nelle opzioni di War Thunder e installa il convertitore: pip install -e &lt;3DHeat&gt;/exporters/ext/warthunder-replay

Impostazioni dalle variabili d'ambiente:

- `HEAT3D_WT_REPLAY`: la cartella del convertitore (un clone o una versione estratta), quando non è installato o non si trova accanto al watcher

## Come funziona {#how-it-works}

Replay e demo: ciò che un gioco salva di una partita, convertito una volta che la partita è finita.

Un replay contiene tutto ciò che un'interfaccia in tempo reale trattiene nei giochi multiplayer - la posizione di ogni giocatore, ogni uccisione nel punto in cui è avvenuta - ed è un file che il gioco scrive per i suoi giocatori, quindi leggerlo non tocca nulla nel gioco. Il watcher controlla le cartelle in cui i giochi li salvano, attende che un nuovo file smetta di crescere (altrimenti il gioco lo sta ancora scrivendo) e lo converte in un thread di lavoro, così una conversione lunga non blocca il resto del watcher.

La prima volta che una cartella viene vista, i replay già presenti vengono solo registrati, non convertiti: chi ha anni di demo troverebbe altrimenti il watcher occupato per un giorno. `python -m heat3d_watch replays <id adattatore> [cartella]` converte quelli esistenti su richiesta.

#### War Thunder {#war-thunder}

War Thunder salva il replay di ogni battaglia in `<War Thunder>/Replays/*.wrpl` quando il salvataggio dei replay è attivo nelle sue opzioni. Il watcher non li legge da solo: lo fa un convertitore esterno (il convertitore dei replay di War Thunder 3DHeat, `exporters/ext/warthunder-replay`, comando `heat3d-wt-replay`), un progetto a sé. Quando il comando è nel PATH, oppure il pacchetto è installato o si trova accanto al watcher, ogni nuovo replay passa da lì e produce nella cartella della sessione `<mappa>/<partita>.parquet` e `<partita>.match.json`; quando non lo è, il watcher lo segnala una volta con le istruzioni per installarlo e lascia la cartella com'è. Ciò che il convertitore legge, e ciò che non legge, è nel suo README. La riga dell'autore del replay nei risultati - uccisioni, uccisioni a terra, morti, assist, punteggio, conquiste - diventa le statistiche della sessione.

Lo stesso modulo serve anche: [Counter-Strike 2 (replay)](game-cs2-demos.md), [Dota 2 (replay)](game-dota-replays.md), [Squad (replay)](game-squad-demos.md), [World of Tanks (replay)](game-wot-replays.md), [World of Warships (replay)](game-wows-replays.md).

## Posizioni e assi {#positions-and-axes}

| | |
|---|---|
| Posizioni registrate | sì |
| Asse verticale | `y` |
| Unità | metri (x est, y alto, z nord) |
| Specchiato per il visualizzatore | `z` |
| Scala delle unità (`scale`: il visualizzatore moltiplica le posizioni per questo valore) | 1 |

Questi valori vanno in `meta.json` di ogni sessione (`axes`) e, quando la sessione ha posizioni, nel footer di `heat.parquet`, così il visualizzatore 3DHeat ruota e scala le righe da solo - vedi [I dati](the-data.md).

## Multigiocatore {#multiplayer}

- Segnato come giocato online (`multiplayer`): **sì**. `games --markdown` lo mostra come "consentito (legge solo ciò che il gioco pubblica)".
- Tipo `replay`: legge solo ciò che il gioco o la piattaforma consegnano (replay e demo che il gioco salva), quindi registra anche nel gioco online oltre che offline; il contrassegno decide soltanto se la memoria può mai essere letta.
- Memoria: **mai** letta da questo adattatore. Solo gli adattatori `memory` leggono la memoria, e mai per un gioco segnato come giocato online - vedi [Fonti e regole](sources-and-rules.md).

## Statistiche registrate {#statistics-recorded}

Chiavi di statistica che il codice di questo adattatore imposta per nome (`stats` di ogni sessione in `meta.json` e la tabella `stats` di `watcher.sqlite`):

`map`

Una chiave tra parentesi graffe viene completata durante l'esecuzione (`score.{team}` è una chiave per ogni squadra). Le chiavi che il codice prende da una tabella dei campi del gioco o dai nomi di statistica del gioco non sono in questo elenco; "Cosa viene registrato" sopra le nomina.

## Completezza {#completeness}

Il convertitore che questo adattatore esegue segue la [regola del convertitore](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md) di 3DHeat: ciò che il replay contiene viene letto o conservato, mai scartato - letto nella tabella e nel documento della partita, tutto il resto conservato intero nei dati grezzi accanto ad essi, conteggiato in `selfCheck.completeness` del documento della partita. La documentazione del convertitore elenca ciò che legge, conserva grezzo e non sa leggere.

## Verificato {#verified}

il convertitore è controllato su replay pubblici di più versioni del gioco (uccisioni e nomi concordano con i risultati) e dai test su replay costruiti; questo collegamento è testato con un comando sostitutivo

## Fonte {#source}

[heat3d_watch/adapters/replays.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/replays.py)

<!-- Generato dall'adattatore da tools/gen_game_pages.py; per cambiarlo modifica l'adattatore ed eseguilo di nuovo invece di modificare questa pagina. -->
