---
title: "Counter-Strike 2 (replay)"
nav_order: 8
lang: "it"
source: game-cs2-demos.md
source_hash: "d115f9085302"
nav_exclude: true
search_exclude: true
---
# Counter-Strike 2 (replay) {#counter-strike-2-replays}

Dopo una partita di Counter-Strike 2, il watcher trasforma il replay che il gioco ha salvato in file che puoi guardare su una mappa nel visualizzatore 3DHeat.

*Dettagli tecnici: adattatore `cs2-demos`, tipo [`replay`](sources-and-rules.md); resta sempre attivo (non aspetta l'avvio di un gioco) e cerca nuovi dati ogni 5 s.*

## Cosa viene registrato {#what-is-recorded}

- la posizione, la direzione dello sguardo, la salute e il denaro di ogni giocatore (ogni 8° tick)
- uccisioni, morti, danni, granate, piazzamenti e disinneschi nel punto in cui sono avvenuti
- round, punteggio, economia; la riga del tabellone del giocatore con l'account Steam connesso come statistiche

## Da dove arriva {#where-it-comes-from}

i demo che CS2 salva: &lt;CS2&gt;/game/csgo/replays/\*.dem (scaricati dallo storico delle partite) e &lt;CS2&gt;/game/csgo/\*.dem (registrati)

## Come attivarlo {#how-to-switch-it-on}

scarica il demo di una partita in CS2 (Guarda > Le tue partite), oppure registrane uno con il comando da console `record`

Impostazioni dalle variabili d'ambiente:

- `HEAT3D_CS2`: la cartella di 3DHeat CS2, quando non si trova accanto al watcher o non è installata

## Come funziona {#how-it-works}

Replay e demo: ciò che un gioco salva di una partita, convertito una volta che la partita è finita.

Un replay contiene tutto ciò che un'interfaccia in tempo reale trattiene nei giochi multiplayer - la posizione di ogni giocatore, ogni uccisione nel punto in cui è avvenuta - ed è un file che il gioco scrive per i suoi giocatori, quindi leggerlo non tocca nulla nel gioco. Il watcher controlla le cartelle in cui i giochi li salvano, attende che un nuovo file smetta di crescere (altrimenti il gioco lo sta ancora scrivendo) e lo converte in un thread di lavoro, così una conversione lunga non blocca il resto del watcher.

La prima volta che una cartella viene vista, i replay già presenti vengono solo registrati, non convertiti: chi ha anni di demo troverebbe altrimenti il watcher occupato per un giorno. `python -m heat3d_watch replays <id adattatore> [cartella]` converte quelli esistenti su richiesta.

#### Counter-Strike 2 {#counter-strike-2}

CS2 salva i demo che un giocatore scarica dallo storico delle partite (scheda Guarda) in `<CS2>/game/csgo/replays/` e quelli registrati con il comando da console `record` in `<CS2>/game/csgo/`. Ciascuno viene convertito con il convertitore CS2 di questo repository (3DHeat CS2, github.com/Holdi601/3DHeat-CS2: la posizione, la direzione dello sguardo, la salute e il denaro di ogni giocatore ogni otto tick; uccisioni, morti, danni, granate, piazzamenti e disinneschi nel punto in cui sono avvenuti; round, punteggio, economia) nella cartella della sessione, come tabella `<mappa>/<partita>.parquet` e riepilogo `<partita>.match.json` che le schede Mappa di calore e Partita del visualizzatore leggono. Il tabellone della partita diventa le statistiche della sessione: per il giocatore il cui account Steam è connesso su questo computer (da `loginusers.vdf` di Steam) con i nomi semplici - uccisioni, morti, assist, ADR, KAST, percentuale di headshot, primi kill, clutch - e il punteggio e i round.

Lo stesso modulo serve anche: [Dota 2 (replay)](game-dota-replays.md), [osu! (replay)](game-osu-replays.md), [Squad (replay)](game-squad-demos.md), [War Thunder (replay)](game-warthunder-replays.md), [World of Tanks (replay)](game-wot-replays.md), [World of Warships (replay)](game-wows-replays.md).

## Posizioni e assi {#positions-and-axes}

| | |
|---|---|
| Posizioni registrate | sì |
| Asse verso l'alto | `z` |
| Unità | pollici (unità Source) |
| Specchiato per il visualizzatore | `y` |
| Scala delle unità (`scale`: il visualizzatore moltiplica le posizioni per questo valore) | 1 |

Questi valori vanno in `meta.json` di ogni sessione (`axes`) e, quando la sessione ha posizioni, nel footer di `heat.parquet`, così il visualizzatore 3DHeat ruota e scala le righe da solo - vedi [I dati](the-data.md).

## Multigiocatore {#multiplayer}

- Segnato come giocato online (`multiplayer`): **sì**. `games --markdown` lo mostra come "consentito (legge solo ciò che il gioco pubblica)".
- Tipo `replay`: legge solo ciò che il gioco o la piattaforma consegnano (replay e demo che il gioco salva), quindi registra anche nel gioco online oltre che offline; il contrassegno decide soltanto se la memoria può mai essere letta.
- Memoria: **mai** letta da questo adattatore. Solo gli adattatori `memory` leggono la memoria, e mai per un gioco segnato come giocato online - vedi [Fonti e regole](sources-and-rules.md).

## Statistiche registrate {#statistics-recorded}

Chiavi di statistica che il codice di questo adattatore imposta per nome (`stats` di ogni sessione in `meta.json` e la tabella `stats` di `watcher.sqlite`):

`map`, `rounds`, `score.{team}`, `won`

Una chiave tra parentesi graffe viene completata durante l'esecuzione (`score.{team}` è una chiave per ogni squadra). Le chiavi che il codice prende da una tabella dei campi del gioco o dai nomi di statistica del gioco non sono in questo elenco; "Cosa viene registrato" sopra le nomina.

## Completezza {#completeness}

Il convertitore che questo adattatore esegue segue la [regola del convertitore](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md) di 3DHeat: ciò che il replay contiene viene letto o conservato, mai scartato - letto nella tabella e nel documento della partita, tutto il resto conservato intero in file accessori accanto ad essi, conteggiato in `selfCheck.completeness` del documento della partita. La documentazione del convertitore elenca ciò che legge, conserva grezzo e non sa leggere.

## Verificato {#verified}

il convertitore è testato su demo di tornei reali; la cartella controllata e le statistiche dai test

## Fonte {#source}

[heat3d_watch/adapters/replays.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/replays.py)

<!-- Generato dall'adattatore da tools/gen_game_pages.py; per cambiarlo modifica l'adattatore ed eseguilo di nuovo invece di modificare questa pagina. -->
