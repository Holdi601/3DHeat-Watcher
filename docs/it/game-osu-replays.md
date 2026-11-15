---
title: "osu! (replay)"
nav_order: 35
lang: "it"
source: game-osu-replays.md
source_hash: "9a1c74c4d5e0"
nav_exclude: true
search_exclude: true
---
# osu! (replay) {#osu-replays}

Dopo una partita di osu!, il watcher trasforma il replay salvato dal gioco in file che puoi guardare su una mappa nel visualizzatore 3DHeat.

*Dettagli tecnici: adattatore `osu-replays`, tipo [`replay`](sources-and-rules.md); funziona sempre (non aspetta che un gioco si avvii) e cerca nuovi dati ogni 5 s.*

## Cosa viene registrato {#what-is-recorded}

- il percorso del cursore sul campo di gioco (x 0..512, y 0..384) e i tasti tenuti premuti, per ogni frame
- punteggio, combo, 300/100/50, gekis/katu, errori, precisione, mod, full combo
- la barra della vita durante la partita, gli hash della mappa e del replay, il seed casuale, l'id del punteggio online

## Da dove arriva {#where-it-comes-from}

replay salvati da osu! (versione stable): %LOCALAPPDATA%/osu!/Data/r/\*.osr (ogni partita) e osu!/Replays/\*.osr (esportati)

## Come attivarlo {#how-to-switch-it-on}

Non serve attivare nulla: il watcher legge la fonte così come il gioco o la piattaforma la fornisce.

## Come funziona {#how-it-works}

Replay e demo: ciò che un gioco salva di una partita, convertito una volta finita la partita.

Un replay contiene tutto ciò che un'interfaccia live trattiene nei giochi multigiocatore -
la posizione di ogni giocatore, ogni uccisione dove è avvenuta - ed è un file che il
gioco scrive per i suoi giocatori, quindi leggerlo non tocca nulla nel gioco. Il
watcher osserva le cartelle in cui i giochi li salvano, aspetta che un nuovo file
smetta di crescere (altrimenti il gioco lo sta ancora scrivendo), e lo converte in un
thread di lavoro, così una conversione lunga non blocca il resto del watcher.

La prima volta che viene vista una cartella, i replay già presenti vengono solo annotati, non
convertiti: un giocatore con anni di demo troverebbe altrimenti il watcher occupato per un giorno.
`python -m heat3d_watch replays <id adattatore> [cartella]` converte quelli esistenti su richiesta.

#### osu! {#osu}

osu! (versione stable) salva ogni partita in `osu!/Data/r/*.osr` e quelli esportati in
`osu!/Replays/`. Il watcher li legge da sé, secondo il formato pubblicato dalla wiki di osu!: il percorso del
cursore e i tasti a ogni frame, la riga del punteggio, la barra della vita, il seed e l'id del punteggio; il file viene
conservato intero accanto, parte per parte, in `heat.raw.parquet` della sessione.

Lo stesso modulo serve anche: [Counter-Strike 2 (replay)](game-cs2-demos.md), [Dota 2 (replay)](game-dota-replays.md), [Squad (replay)](game-squad-demos.md), [War Thunder (replay)](game-warthunder-replays.md), [World of Tanks (replay)](game-wot-replays.md), [World of Warships (replay)](game-wows-replays.md).

## Posizioni e assi {#positions-and-axes}

| | |
|---|---|
| Posizioni registrate | sì |
| Asse verticale | `y` |
| Unità | pixel di osu! (campo di gioco 512 x 384) |
| Specchiato per il visualizzatore | `z` |
| Scala delle unità (`scale`: il visualizzatore moltiplica le posizioni per questo valore) | 1 |

Questi valori finiscono in `meta.json` di ogni sessione (`axes`) e, quando la sessione ha posizioni, nel footer di `heat.parquet`, così il visualizzatore 3DHeat ruota e scala le righe da solo - vedi [I dati](the-data.md).

## Multigiocatore {#multiplayer}

- Segnato come giocato online (`multiplayer`): **sì**. `games --markdown` lo mostra come "consentito (legge solo ciò che il gioco pubblica)".
- Tipo `replay`: legge solo ciò che il gioco o la piattaforma consegna (replay e demo che il gioco salva), quindi registra anche nel gioco online oltre che offline; il flag decide solo se la memoria può mai essere letta.
- Memoria: **mai** letta da questo adattatore. Solo gli adattatori `memory` leggono la memoria, e mai per un gioco segnato come giocato online - vedi [Fonti e regole](sources-and-rules.md).

## Statistiche registrate {#statistics-recorded}

Chiavi di statistica che il codice di questo adattatore imposta per nome (`stats` di ogni sessione in `meta.json` e la tabella `stats` di `watcher.sqlite`):

`accuracy`, `full_combo`

Una chiave tra parentesi graffe viene completata durante l'esecuzione (`score.{team}` è una chiave per squadra). Le chiavi che il codice prende da una tabella dei campi del gioco o dai nomi di statistica del gioco non sono in questo elenco; "Cosa viene registrato" sopra le nomina.

## Completezza {#completeness}

Il watcher segue la [regola del convertitore](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md) di 3DHeat: ciò che la fonte contiene viene letto o conservato, mai scartato. Oltre alle righe, ogni pacchetto, pagina, riga o risposta che l'adattatore riceve viene conservato intero in `heat.raw.parquet` della sessione (colonne `time`, `ms`, `type`, `used`, `payload`, `text`, poi ogni campo conservato per nome; `used` segna ciò che è diventato anche riga), e `selfCheck.completeness` in `meta.json` conta ogni `type` - `lost` è 0.

**Letto**

- ogni frame: una riga al suo istante (millisecondi sommati), x e y sul campo di gioco, `keys` i bit dei tasti (mouse 1 e 2, tasti 1 e 2, smoke); in mania x contiene i tasti premuti invece di una posizione
- l'intestazione, ogni campo: modalità, versione, l'MD5 della mappa (il file nomina la mappa solo con questo), il giocatore, l'MD5 del replay, 300, 100, 50, gekis, katu, errori, punteggio, combo massima, full combo, mod (per nome in `osu.modNames` di meta.json), l'ora della partita - come statistiche e in `osu` di meta.json
- il grafico della barra della vita: una riga `life` per punto (tempo, vita 0..1)
- il frame `-12345`: il seed casuale (`osu.seed`); l'id del punteggio online (`osu.scoreId`); con Target Practice, la sua precisione (`osu.targetPracticeAccuracy`)

**Conservato grezzo**

- il file intero, parte per parte, in heat.raw.parquet (`offset` dove inizia ciascuna, così le parti sono il file): `header`, `replay_data` (i frame compressi con LZMA come sono memorizzati), `score_id`, `mod_info`, e `trailing` per ciò che segue le parti descritte dal formato (gli export di osu!lazer vi aggiungono dati) - conservato, non letto

**Non disponibile**

- la mappa stessa (oggetti da colpire, tempi): non è in un replay; è nominata solo dal suo MD5
- i replay di osu!lazer: sono nel suo database, non come file

**Dimensione**: i dati grezzi conservati hanno più o meno la dimensione del replay (decine o centinaia di kilobyte)

## Verificato {#verified}

testato su replay costruiti nel formato .osr pubblicato; osu!lazer conserva i replay nel proprio archivio e non viene letto

## Fonte {#source}

[heat3d_watch/adapters/replays.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/replays.py)

<!-- Generated from the adattatore by tools/gen_game_pages.py; change the adattatore and run it again rather than editing this page. -->
