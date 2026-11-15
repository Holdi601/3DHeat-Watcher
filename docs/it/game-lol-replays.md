---
title: "League of Legends (replay)"
nav_order: 30
lang: "it"
source: game-lol-replays.md
source_hash: "216b88922360"
nav_exclude: true
search_exclude: true
---
# League of Legends (replay) {#league-of-legends-replays}

Dopo una partita di League of Legends, il watcher trasforma il replay salvato dal gioco in file che puoi guardare su una mappa nel visualizzatore 3DHeat.

*Dettagli tecnici: adattatore `lol-replays`, tipo [`replay`](sources-and-rules.md); gira sempre (non aspetta che un gioco si avvii) e cerca nuovi dati ogni 5 s.*

## Cosa viene registrato {#what-is-recorded}

- il campione, il ruolo, la squadra, uccisioni, morti, assist, oro, danni ai campioni ed esito di ogni giocatore, e ogni altro numero della tabella finale di fine partita
- la tua riga come statistiche, e le tue righe contrassegnate come tue (`player` in meta.json), con il tuo Riot ID nelle impostazioni
- con la tua chiave API Riot: la posizione di ogni giocatore ogni minuto con le statistiche di quel minuto, e ogni evento della timeline (uccisioni dove sono avvenute, edifici, mostri, sentinelle, oggetti, abilità), all'ora dell'orologio che la timeline indica
- ogni parte del file di replay conservata intera in heat.raw.parquet; non decodificato: il gioco momento per momento, che è cifrato e offuscato contro i trucchi

## Da dove arriva {#where-it-comes-from}

i replay che salva il client di League: %USERPROFILE%/Documents/League of Legends/Replays/\*.rofl (solo i metadati semplici di fine partita); con la tua chiave API Riot, la timeline ufficiale della partita dall'API Match-V5 di Riot

## Come attivarlo {#how-to-switch-it-on}

salva un replay nel client di League (cronologia partite > scarica); per le posizioni imposta riot_api_key e riot_platform con `config --set`

## Come funziona {#how-it-works}

League of Legends e Valorant replay: ciò che di essi si può leggere così com'è.

Entrambi i giochi salvano i replay sul disco del giocatore, e proteggono ciò che c'è dentro:
i dati di gioco momento per momento sono offuscati, e in modo diverso a ogni patch,
per impedire che vengano usati per barare. Superarlo significa smontare il codice del
gioco stesso, cosa che i termini di Riot vietano (Condizioni d'uso 3.1 e 7.1)
- quindi qui non si fa. Viene letto ciò che ogni file contiene in chiaro, e il resto
viene conservato così com'è: ogni parte del file, intera, in `heat.raw.parquet` della
sessione (regola del convertitore di 3DHeat, docs/converters.md nel repository del
visualizzatore), conteggiata in `selfCheck.completeness` di meta.json.

#### League of Legends (.rofl) {#league-of-legends-rofl}

`%USERPROFILE%\Documents\League of Legends\Replays\*.rofl`. Entrambe le versioni del
contenitore portano la tabella finale come JSON semplice (`statsJson`): per ciascuno dei
dieci giocatori il campione, uccisioni, morti, assist, oro, danni ai campioni, oggetti,
squadra, ruolo, vittoria, il loro Riot ID, e ogni altro numero che il gioco totalizza
(più di cento per giocatore); tutti diventano la riga `player_result` del giocatore.
ROFL1 (patch 14.9 e precedenti) lo ha dopo un'intestazione fissa (`RIOT\0\0`, una firma
di 256 byte, poi le lunghezze); ROFL2 (dalla 14.11, `RIOT\2\0`) alla fine del file, con la
sua lunghezza negli ultimi quattro byte (indicato da un ingegnere di Riot, ReplayBook
issue 299). L'intestazione del payload di ROFL1 (id partita, lunghezza, numero di chunk e
keyframe, lunghezza della chiave del chunk) e la sua tabella di chunk (id, tipo, lunghezza,
chunk successivo, offset) sono in chiaro e vengono lette; i chunk stessi sono cifrati, e
conservati interi senza essere letti. Layout da roflxd.cs (MIT).

Le posizioni non vengono dal file. Con una chiave per sviluppatori Riot del giocatore
(`riot_api_key` nelle impostazioni; una chiave personale serve esattamente a questo,
"mostrare le statistiche (proprie) del giocatore"), la timeline ufficiale della partita
viene scaricata dall'API Match-V5 di Riot: la posizione di ogni giocatore una volta al
minuto con tutto ciò che il fotogramma di quel minuto dice di loro (oro, esperienza,
livello, minion, statistiche del campione e dei danni), e ogni evento della timeline -
uccisioni, edifici, mostri elite, sentinelle, oggetti, abilità, livelli - come riga,
dove ha un luogo, nel luogo in cui è avvenuto. Senza chiave non viene scaricato nulla e non viene inviato nulla.

Lo stesso modulo serve anche: [VALORANT (replay)](game-valorant-replays.md).

## Posizioni e assi {#positions-and-axes}

| | |
|---|---|
| Posizioni registrate | sì |
| Asse verticale | `y` |
| Unità | unità della mappa di Summoner's Rift (circa 15.000 da un capo all'altro) |
| Specchiato per il visualizzatore | nessuno |
| Scala delle unità (`scale`: il visualizzatore moltiplica le posizioni per questo valore) | 1 |

Questi valori finiscono in `meta.json` di ogni sessione (`axes`) e, quando la sessione ha posizioni, nel footer di `heat.parquet`, così il visualizzatore 3DHeat ruota e scala le righe da solo: vedi [I dati](the-data.md).

## Multigiocatore {#multiplayer}

- Segnato come giocato online (`multiplayer`): **sì**. `games --markdown` lo mostra come "consentito (legge solo ciò che il gioco pubblica)".
- Tipo `replay`: legge solo ciò che il gioco o la piattaforma rende disponibile (replay e demo che il gioco salva), quindi registra anche nel gioco online oltre che offline; il contrassegno decide solo se la memoria può mai essere letta.
- Memoria: **mai** letta da questo adattatore. Solo gli adattatori `memory` leggono la memoria, e mai per un gioco segnato come giocato online: vedi [Fonti e regole](sources-and-rules.md).

## Statistiche registrate {#statistics-recorded}

Chiavi statistiche che il codice di questo adattatore imposta per nome (`stats` di ogni sessione in `meta.json` e la tabella `stats` di `watcher.sqlite`):

`champion`, `game_seconds`, `won`

Una chiave tra parentesi graffe viene completata durante l'esecuzione (`score.{team}` è una chiave per ogni squadra). Le chiavi che il codice prende da una tabella dei campi del gioco o dai nomi statistici del gioco non sono in questo elenco; "Cosa viene registrato" sopra le nomina.

## Completezza {#completeness}

Il watcher segue la [regola del convertitore](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md) di 3DHeat: ciò che la sorgente contiene viene letto o conservato, mai scartato. Oltre alle righe, ogni pacchetto, pagina, riga o risposta che l'adattatore riceve viene conservato intero in `heat.raw.parquet` della sessione (colonne `time`, `ms`, `type`, `used`, `payload`, `text`, poi ogni campo conservato per nome; `used` segna ciò che è diventato anche riga), e `selfCheck.completeness` in `meta.json` conta ogni `type`: `lost` è 0.

**Letto**

- il JSON dei metadati: durata della partita, versione, id dell'ultimo chunk e del keyframe, e `statsJson` - ogni campo della tabella finale di ogni giocatore sulla sua riga `player_result` (i numeri scritti come testo vengono letti come numeri)
- ROFL1: il blocco delle lunghezze, l'intestazione del payload (id partita, durata, numero di keyframe e di chunk, id dei chunk di avvio e di inizio partita, intervallo dei keyframe, la chiave del chunk come è memorizzata) e la tabella dei chunk (id, tipo, lunghezza, chunk successivo, offset) - in `rofl` di meta.json e nel `text` delle righe grezze
- ROFL2: la stringa di versione
- la timeline Match-V5 (solo con la propria chiave API): ogni fotogramma di partecipante su una riga `position` (o `participant_frame` senza un luogo) con tutti i suoi campi appiattiti (`championStats.armor`, `damageStats.totalDamageDone`, `currentGold`, `xp`, ...); ogni evento come riga col nome del suo tipo, posizionato dove ha una `position`, CHAMPION_KILL come uccisione e morte

**Conservato grezzo**

- ogni parte del .rofl, intera, nell'ordine del file (`offset`), così le parti sono il file: `magic`, `signature`, `lengths`, `metadata`, `payload_header`, `chunk_header`, `chunk`, `keyframe` (ROFL1); `body`, `metadata`, `metadata_length` (ROFL2); ogni tratto che nessuna parte copre come `unknown`
- la timeline intera: `timeline <type>` per ogni evento, `timeline participantFrame` per il fotogramma di ogni giocatore (`participant` il suo id), `timeline` per il resto

**Non disponibile**

- il gioco stesso (posizioni, abilità, ogni unità, momento per momento): i chunk di ROFL1 e il body di ROFL2 sono cifrati e i pacchetti al loro interno sono offuscati a ogni patch; superarlo significa smontare il client, cosa che i termini di Riot vietano (3.1, 7.1). Conservato intero, non letto
- posizioni senza la tua chiave API Riot: il file non ne ha in chiaro

**Dimensione**: il file accessorio grezzo è circa della dimensione del replay stesso: i chunk cifrati non si comprimono

## Verificato {#verified}

il lettore dei metadati testato su file costruiti secondo i layout di roflxd.cs (MIT); la timeline sul JSON documentato di Match-V5; nessun replay reale era disponibile per il controllo

## Sorgente {#source}

[heat3d_watch/adapters/riot_replays.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/riot_replays.py)

<!-- Generated from the adattatore by tools/gen_game_pages.py; change the adattatore and run it again rather than editing this page. -->
