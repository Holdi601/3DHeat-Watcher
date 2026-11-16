---
title: "World of Warships (replay)"
nav_order: 48
lang: "it"
source: game-wows-replays.md
source_hash: "44a041452521"
nav_exclude: true
search_exclude: true
---
# World of Warships (replay) {#world-of-warships-replays}

Dopo una partita di World of Warships, il watcher trasforma il replay che il gioco ha salvato in file che puoi guardare su una mappa nel visualizzatore 3DHeat.

*Dettagli tecnici: adattatore `wows-replays`, tipo [`replay`](sources-and-rules.md); resta sempre attivo (non aspetta l'avvio di un gioco) e cerca nuovi dati ogni 5 s.*

## Cosa viene registrato {#what-is-recorded}

- la posizione e la direzione di ogni nave mentre il client di registrazione la vedeva (circa 6-7 volte al secondo mentre si muove), la nave del giocatore per tutto il tempo
- alleato o nemico, e nave (quella del giocatore che ha registrato per nome, le altre per il numero di nave del gioco); navi affondate dove sono affondate e i loro assassini dove si trovavano
- la mappa; la nave, le uccisioni e la sopravvivenza del giocatore che ha registrato come statistiche

## Da dove arriva {#where-it-comes-from}

i replay che World of Warships salva: &lt;World of Warships&gt;/replays/\*.wowsreplay (con i replay attivi), convertiti dal convertitore esterno `heat3d-wows-replay` (exporters/ext/wows-replay)

## Come attivarlo {#how-to-switch-it-on}

attiva la registrazione dei replay in World of Warships (`isReplayEnabled` nel suo preferences.xml, oppure l'impostazione del gioco dove esiste) e installa il convertitore: pip install -e &lt;3DHeat&gt;/exporters/ext/wows-replay

Impostazioni dalle variabili d'ambiente:

- `HEAT3D_WOWS_REPLAY`: la cartella del convertitore (un clone o una versione estratta), quando non è installato o non si trova accanto al watcher

## Come funziona {#how-it-works}

Replay e demo: ciò che un gioco salva di una partita, convertito una volta che la partita è finita.

Un replay contiene tutto ciò che un'interfaccia in tempo reale trattiene nei giochi multiplayer - la posizione di ogni giocatore, ogni uccisione nel punto in cui è avvenuta - ed è un file che il gioco scrive per i suoi giocatori, quindi leggerlo non tocca nulla nel gioco. Il watcher controlla le cartelle in cui i giochi li salvano, attende che un nuovo file smetta di crescere (altrimenti il gioco lo sta ancora scrivendo) e lo converte in un thread di lavoro, così una conversione lunga non blocca il resto del watcher.

La prima volta che una cartella viene vista, i replay già presenti vengono solo registrati, non convertiti: chi ha anni di demo troverebbe altrimenti il watcher occupato per un giorno. `python -m heat3d_watch replays <id adattatore> [cartella]` converte quelli esistenti su richiesta.

#### World of Tanks e World of Warships {#world-of-tanks-and-world-of-warships}

Entrambi salvano il replay di ogni battaglia in `<gioco>/replays/` quando la registrazione è attiva (`*.wotreplay`, `*.wowsreplay`); le installazioni si trovano tramite l'elenco del Wargaming Game Center, `C:/Games/World_of_Tanks*` / `World_of_Warships*`, e Steam. Come per War Thunder, il watcher non legge i file da solo: lo fa un convertitore esterno per ciascuno (`exporters/ext/wot-replay`, comando `heat3d-wot-replay`; `exporters/ext/wows-replay`, comando `heat3d-wows-replay`), tenuto separato in modo che un problema con le condizioni di Wargaming tocchi solo quel convertitore. Trovato nel PATH, installato o accanto al watcher, trasforma ogni nuovo replay in `<mappa>/<partita>.parquet` e `<partita>.match.json` nella cartella della sessione; se manca, il watcher lo segnala una volta con le istruzioni per installarlo. La riga del giocatore che ha registrato - veicolo o nave, uccisioni, danni (World of Tanks), se è sopravvissuto e il risultato (World of Tanks) - diventa le statistiche della sessione. Ciò che ogni convertitore legge, e ciò che non legge, è nel suo README.

Lo stesso modulo serve anche: [Counter-Strike 2 (replay)](game-cs2-demos.md), [Dota 2 (replay)](game-dota-replays.md), [Squad (replay)](game-squad-demos.md), [War Thunder (replay)](game-warthunder-replays.md), [World of Tanks (replay)](game-wot-replays.md).

## Posizioni e assi {#positions-and-axes}

| | |
|---|---|
| Posizioni registrate | sì |
| Asse verticale | `y` |
| Unità | unità del mondo di World of Warships (x est, y alto, z nord; una unità è 15 m per la geometria dello scafo, 30 m per le distanze del gioco) |
| Specchiato per il visualizzatore | `z` |
| Scala delle unità (`scale`: il visualizzatore moltiplica le posizioni per questo valore) | 1 |

Questi valori vanno in `meta.json` di ogni sessione (`axes`) e, quando la sessione ha posizioni, nel footer di `heat.parquet`, così il visualizzatore 3DHeat ruota e scala le righe da solo - vedi [I dati](the-data.md).

## Multigiocatore {#multiplayer}

- Segnato come giocato online (`multiplayer`): **sì**. `games --markdown` lo mostra come "consentito (legge solo ciò che il gioco pubblica)".
- Tipo `replay`: legge solo ciò che il gioco o la piattaforma consegnano (replay e demo che il gioco salva), quindi registra anche nel gioco online oltre che offline; il contrassegno decide soltanto se la memoria può mai essere letta.
- Memoria: **mai** letta da questo adattatore. Solo gli adattatori `memory` leggono la memoria, e mai per un gioco segnato come giocato online - vedi [Fonti e regole](sources-and-rules.md).

## Statistiche registrate {#statistics-recorded}

Chiavi di statistica che il codice di questo adattatore imposta per nome (`stats` di ogni sessione in `meta.json` e la tabella `stats` di `watcher.sqlite`):

`map`, `survived`, `vehicle`, `won`

Una chiave tra parentesi graffe viene completata durante l'esecuzione (`score.{team}` è una chiave per ogni squadra). Le chiavi che il codice prende da una tabella dei campi del gioco o dai nomi di statistica del gioco non sono in questo elenco; "Cosa viene registrato" sopra le nomina.

## Completezza {#completeness}

Il convertitore che questo adattatore esegue segue la [regola del convertitore](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md) di 3DHeat: ciò che il replay contiene viene letto o conservato, mai scartato - letto nella tabella e nel documento della partita, tutto il resto conservato intero nei dati grezzi accanto ad essi, conteggiato in `selfCheck.completeness` del documento della partita. La documentazione del convertitore elenca ciò che legge, conserva grezzo e non sa leggere.

## Verificato {#verified}

il convertitore è controllato su replay pubblici di più versioni del gioco e dai test su replay costruiti; questo collegamento è testato con un comando sostitutivo

## Fonte {#source}

[heat3d_watch/adapters/replays.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/replays.py)

<!-- Generato dall'adattatore da tools/gen_game_pages.py; per cambiarlo modifica l'adattatore ed eseguilo di nuovo invece di modificare questa pagina. -->
