---
title: "Counter-Strike 2 (stato di gioco)"
nav_order: 9
lang: "it"
source: game-cs2-gsi.md
source_hash: "2eda1106e11f"
nav_exclude: true
search_exclude: true
---
# Counter-Strike 2 (stato di gioco) {#counter-strike-2-game-state}

Mentre giochi a Counter-Strike 2, il watcher salva ciò che il gioco comunica ai programmi sul tuo computer, così puoi guardarlo più tardi su una mappa nel visualizzatore di 3DHeat.

*Dettagli tecnici: adattatore `cs2-gsi`, tipo [`gsi`](sources-and-rules.md); gira mentre `cs2.exe` è in esecuzione e cerca nuovi dati ogni 0,05 s.*

## Cosa viene registrato {#what-is-recorded}

- la tua posizione (XYZ nel mondo, in pollici) e la direzione di sguardo fino a 10 volte al secondo mentre sei vivo
- spawn (il primo avvistamento di ogni round, e i ritorni in vita) e morti (vita a 0, oppure il numero di morti)
- uccisioni con l'arma attiva, dalle statistiche della partita
- round (inizio, fine, vincitore), bomba piazzata, disinnescata o esplosa, fasi della partita e risultato
- uccisioni, assist, morti, MVP, punteggio, denaro, danni, uccisioni alla testa, round vinti e persi

## Da dove arriva {#where-it-comes-from}

Game State Integration: richieste HTTP POST a 127.0.0.1:3311, configurate dal file &lt;CS2&gt;\game\csgo\cfg\gamestate_integration_heat3d.cfg

## Come attivarlo {#how-to-switch-it-on}

`python -m heat3d_watch setup cs2-gsi --apply`, poi avvia CS2 (il gioco legge il file all'avvio)

Scrivi il comando in un terminale aperto nella cartella del watcher (vedi [Prima di iniziare](before-you-start.md)). Se fallisce, l'ultima riga dice il motivo; [Installazione e avvio](installing-and-running.md) descrive le cause più comuni.

`python -m heat3d_watch setup cs2-gsi` elenca i file che verrebbero modificati; `python -m heat3d_watch setup cs2-gsi --apply` li modifica, tenendo l'originale come `<file>.heat3d-backup` (vedi [Comandi](commands.md#setup)). Stampa `cs2-gsi: changed: ...` per ogni modifica, oppure `cs2-gsi: nothing to change` quando è già attivo.

Impostazioni dalle variabili d'ambiente:

- `HEAT3D_CS2_GSI_PORT`: la porta a cui il gioco invia i dati (predefinita 3311); il file cfg del gioco deve indicare la stessa porta

## Come funziona {#how-it-works}

Valve Game State Integration: Counter-Strike 2 e Dota 2 comunicano a un server web locale ciò che succede.

Entrambi i giochi leggono ogni `gamestate_integration_*.cfg` nella loro cartella cfg all'avvio, e da quel momento inviano un documento JSON all'`uri` di ogni file ogni volta che lo stato cambia (al massimo ogni `throttle` secondi, e ogni `heartbeat` secondi quando non cambia nulla). Il watcher è quel server web: ascolta solo su 127.0.0.1, risponde subito con 200 a ogni POST e fa il lavoro nel suo thread di controllo.

```text
Counter-Strike 2  <CS2>\game\csgo\cfg\gamestate_integration_heat3d.cfg      porta 3311
Dota 2            <Dota>\game\dota\cfg\gamestate_integration\gamestate_integration_heat3d.cfg   porta 3312
```

Ciò che viene inviato a un giocatore - e quindi ciò che può essere registrato - è quello che il gioco decide che un giocatore può vedere:

- CS2: `provider` (il tuo steamid), `map` (nome, modalità, fase warmup/live/intermission/gameover, round, punteggio team_ct/team_t), `round` (fase freezetime/live/over, bomba piazzata/esplosa/disinnescata, win_team), `player` (il giocatore *osservato*: te stesso mentre sei vivo, un compagno di squadra dopo la morte) con `state` (vita, armatura, denaro, round_kills, round_killhs, round_totaldmg), `match_stats` (uccisioni, assist, morti, mvps, punteggio), `position` e `forward` come stringhe "x, y, z" in unità del mondo (pollici, Z verso l'alto), `weapons`; `bomb` solo per gli spettatori. Le posizioni degli altri giocatori (`allplayers_*`) vengono inviate solo a spettatori e GOTV, quindi non vengono richieste.
- Dota 2: `map` (matchid, game_state, game_time, clock_time, win_team), `player` (uccisioni, morti, assist, last_hits, denies, gold, gpm, xpm, team_name), `hero` (xpos/ypos in unità del mondo, livello, vivo, respawn_seconds), `buildings` (vita per torre/caserma/ancient), `roshan`, `events` (roshan_killed, aegis_picked_up, ...). Non c'è altezza: z è 0. Vengono anche richiesti e conservati interi: `abilities`, `items`, `draft`, `wearables`, `minimap`, `couriers`, `neutralitems`, `league` (il gioco invia ciò che ha il client del giocatore; non è ancora verificato quali di questi contengano dati durante il gioco e non in modalità spettatore).

Ogni documento viene anche conservato intero (regola del convertitore di 3DHeat, docs/converters.md nel repository del visualizzatore): `heat.raw.parquet`, `type` "gsi", `text` il JSON così come inviato - con solo il token del file cfg cancellato, perché è il segreto del watcher, non un dato di gioco. I documenti inviati mentre non è aperta nessuna partita (menu, caricamenti, tra una partita e l'altra) restano in attesa in un `Backlog` e finiscono nella sessione della partita successiva, prima del suo inizio; ciò che resta quando il gioco si chiude ottiene una sessione tutta sua, che contiene solo quelli. Anche i post non leggibili e quelli con un token sbagliato vengono conservati ("gsi-unreadable", "gsi-bad-auth").

Fonti: <https://developer.valvesoftware.com/wiki/Counter-Strike:_Global_Offensive_Game_State_Integration> (il formato che CS2 ha mantenuto), <https://github.com/antonpup/CounterStrike2GSI> e <https://github.com/antonpup/Dota2GSI> (elenchi dei campi; licenza MIT, letti solo per i fatti).

Lo stesso modulo serve anche: [Dota 2 (stato di gioco)](game-dota2-gsi.md).

## Posizioni e assi {#positions-and-axes}

| | |
|---|---|
| Posizioni registrate | sì |
| Asse verso l'alto | `z` |
| Unità | pollici (unità di Hammer) |
| Specchiato per il visualizzatore | `y` |
| Scala delle unità (`scale`: il visualizzatore moltiplica le posizioni per questo valore) | 1 |

Questi valori finiscono in `meta.json` (`axes`) di ogni sessione e, quando la sessione ha delle posizioni, nel footer di `heat.parquet`, così il visualizzatore di 3DHeat ruota e scala le righe da solo - vedi [I dati](the-data.md).

## Multigiocatore {#multiplayer}

- Segnato come giocato online (`multiplayer`): **sì**. `games --markdown` lo mostra come "consentito (legge solo ciò che il gioco pubblica)".
- Tipo `gsi`: legge solo ciò che il gioco o la piattaforma consegna (una game-state integration o un'API locale che il gioco offre), quindi registra anche nel gioco online oltre che offline; il flag decide solo se la memoria può mai essere letta.
- Memoria: **mai** letta da questo adattatore. Solo gli adattatori `memory` leggono la memoria, e mai per un gioco segnato come giocato online - vedi [Fonti e regole](sources-and-rules.md).

## Statistiche registrate {#statistics-recorded}

Chiavi statistiche che il codice di questo adattatore imposta per nome (`stats` di ogni sessione in `meta.json` e la tabella `stats` di `watcher.sqlite`):

`bad_auth`, `bad_packets`, `dropped_packets`, `money`, `result`, `score_other`, `score_own`

Una chiave tra parentesi graffe viene completata durante l'esecuzione (`score.{team}` è una chiave per squadra). Le chiavi che il codice prende da una tabella dei campi del gioco o dai nomi statistici del gioco non sono in questo elenco; "Cosa viene registrato" qui sopra le nomina.

## Completezza {#completeness}

Il watcher segue la [regola del convertitore](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md) di 3DHeat: ciò che la fonte contiene viene letto o conservato, mai scartato. Oltre alle righe, ogni pacchetto, pagina, riga o risposta che l'adattatore riceve viene conservato intero in `heat.raw.parquet` della sessione (colonne `time`, `ms`, `type`, `used`, `payload`, `text`, poi ogni campo conservato per nome; `used` segna ciò che è diventato anche righe), e `selfCheck.completeness` in `meta.json` conta ogni `type` - `lost` è 0.

**Letto**

- la posizione del giocatore osservato, la direzione di sguardo, vita, armatura, denaro, arma attiva, elmetto, kit di disinnesco, quantità di flash/fumo/fuoco e valore dell'equipaggiamento, su ogni riga di posizione mentre è il giocatore stesso (steamid del provider = steamid del giocatore)
- spawn, morti (vita a 0, oppure il numero di morti delle statistiche), uccisioni (il conteggio delle uccisioni che cresce)
- fasi della partita, round (tempo di freeze, in corso, finito, vincitore), bomba piazzata, disinnescata, esplosa, il risultato
- uccisioni, assist, morti, MVP, punteggio, denaro, danni, uccisioni alla testa, round vinti e persi come statistiche

**Conservato grezzo**

- `gsi`: ogni documento inviato dal gioco, intero, così come inviato (`text`), con `used` vero quando è stato letto durante una partita - provider (versione, timestamp), map (modalità, nomi delle squadre, sconfitte consecutive, timeout, vittorie della serie, `round_wins` con la condizione di vittoria di ogni round), round, il giocatore osservato (clan, slot dell'osservatore, attività, ogni arma con skin, munizioni e riserva), bomba, conto alla rovescia delle fasi, e la differenza `previously`/`added` del gioco rispetto al post precedente
- documenti da menu, caricamenti e tra una partita e l'altra: conservati allo stesso modo, nel loro momento, prima dell'inizio della partita successiva; dopo l'ultima partita, in una sessione tutta loro (`raw_only` in meta.json)
- `gsi-unreadable`: un post che non è un oggetto JSON, con i suoi byte come `payload` e la sua `length`
- `gsi-bad-auth`: un post con un token diverso da quello del file cfg

**Non disponibile**

- altri giocatori (`allplayers_*`) e granate (`allgrenades`): il gioco li invia solo a spettatori e GOTV, e il watcher non li richiede (vedi Fonti e regole); un demo contiene ogni giocatore - vedi [Counter-Strike 2 (replay)](game-cs2-demos.md)
- stati tra un post e l'altro: il gioco invia al massimo ogni 0,1 s (`throttle`) e solo quando lo stato cambia, altrimenti ogni 10 s (`heartbeat`)
- il token del file cfg, cancellato in ogni documento conservato: è il segreto del watcher, non un dato di gioco
- i post oltre 10.000 in attesa (il watcher si è bloccato) vengono contati come `dropped_packets` e non conservati; un post oltre 4 MB viene conservato come `gsi-unreadable` con la sua lunghezza, ma senza i byte

**Dimensione**: il documento di un giocatore è di 2-4 KB, inviato fino a 10 volte al secondo mentre qualcosa cambia: circa 30-150 MB all'ora in `raw.bin` durante la partita, un decimo o meno in `heat.raw.parquet` compresso con zstd (stimato dal formato pubblicato, non misurato sul gioco)

## Verificato {#verified}

testato su documenti nel formato GSI pubblicato, inviati all'adattatore in esecuzione; installazione e ricerca della cartella cfg testate su un'installazione locale; non ancora testato con il gioco in esecuzione

## Sorgente {#source}

[heat3d_watch/adapters/gsi.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/gsi.py)

<!-- Generated from the adattatore by tools/gen_game_pages.py; change the adattatore and run it again rather than editing this page. -->
