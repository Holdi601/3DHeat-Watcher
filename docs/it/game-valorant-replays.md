---
title: "VALORANT (replay)"
nav_order: 44
lang: "it"
source: game-valorant-replays.md
source_hash: "617e23a33a4c"
nav_exclude: true
search_exclude: true
---
# VALORANT (replay) {#valorant-replays}

Dopo una partita di VALORANT, il watcher trasforma il replay salvato dal gioco in file che puoi guardare come statistiche e una cronologia.

*Dettagli tecnici: adattatore `valorant-replays`, tipo [`replay`](sources-and-rules.md); gira sempre (non aspetta che un gioco si avvii) e cerca nuovi dati ogni 5 s.*

## Cosa viene registrato {#what-is-recorded}

- la mappa, l'id della partita e gli agenti scelti; il blocco informativo del replay (durata, versioni, nome, data di registrazione, flag di compressione e cifratura)
- la cronologia degli eventi del server: uccisioni (uccisore e vittima come id di rete), inizi di round, spike piazzate, disinnescate ed esplose, ultimate usate, cambi di lato - ognuno con il suo id e i suoi metadati
- ogni chunk del file conservato intero in heat.raw.parquet; non decodificato: posizioni, nomi o punteggi - sono nel flusso offuscato

## Da dove arriva {#where-it-comes-from}

i replay che salva VALORANT: %LOCALAPPDATA%/VALORANT/Saved/Demos/\*.vrf (solo le parti non offuscate)

## Come attivarlo {#how-to-switch-it-on}

salva un replay in VALORANT (carriera > partita > scarica replay) e installa il lettore: github.com/Holdi601/3DHeat-Ext-Riot (`heat3d-riot-replays`)

Impostazioni dalle variabili d'ambiente:

- `HEAT3D_RIOT_REPLAYS`: la cartella del lettore (un clone o una release estratta), quando non è installato o non si trova accanto al watcher

## Come funziona {#how-it-works}

League of Legends e Valorant replay: ciò che di essi si può leggere così com'è.

Entrambi i giochi salvano i replay sul disco del giocatore, e proteggono ciò che c'è dentro:
i dati di gioco momento per momento sono offuscati, e in modo diverso a ogni patch,
per impedire che vengano usati per barare. Superarlo significa smontare il codice del
gioco stesso, cosa che i termini di Riot vietano (Condizioni d'uso 3.1 e 7.1)
- quindi in 3DHeat non si fa in nessun punto. Viene letto ciò che ogni file contiene in chiaro, e il resto
viene conservato così com'è: ogni parte del file, intera, in `heat.raw.parquet` della
sessione (regola del convertitore di 3DHeat, docs/converters.md nel repository del
visualizzatore), conteggiata in `selfCheck.completeness` di meta.json.

Il watcher non legge i file da sé: lo fa un lettore esterno (3DHeat
Riot, github.com/Holdi601/3DHeat-Ext-Riot, `exporters/ext/riot-replays`,
comando `heat3d-riot-replays`), tenuto separato perché un problema con i termini di Riot
tocchi solo quel lettore. Se viene trovato nel PATH, installato o accanto al watcher, legge
ogni nuovo replay; se manca, il watcher dice una volta come installarlo. Ciò che il lettore
legge, il watcher lo registra nella sessione; la timeline Match-V5 qui sotto viene
scaricata dal watcher stesso, perché non è nel file.

#### Valorant (.vrf) {#valorant-vrf}

`%LOCALAPPDATA%\VALORANT\Saved\Demos\*.vrf`, un replay locale di Unreal Engine. In chiaro:
il blocco informativo del replay (durata, versione di rete, changelist, il suo nome,
quando è stato registrato, se è compresso o cifrato), la mappa, l'id della partita e
gli agenti scelti (nell'intestazione), e la cronologia degli eventi del server -
uccisioni (uccisore e vittima come id di rete, non come nomi), inizi di round, spike
piazzate, disinnescate ed esplose, ultimate usate, cambi di lato - ognuno con il suo
tempo, id e metadati. Posizioni, nomi, punteggi e tutto il resto sono nel flusso
offuscato (i chunk dei dati di replay e dei checkpoint), che viene conservato intero e non letto.

Lo stesso modulo serve anche: [League of Legends (replay)](game-lol-replays.md).

## Posizioni e assi {#positions-and-axes}

| | |
|---|---|
| Posizioni registrate | no |
| Asse verticale | `z` |
| Unità | unità del mondo di VALORANT |
| Specchiato per il visualizzatore | nessuno |
| Scala delle unità (`scale`: il visualizzatore moltiplica le posizioni per questo valore) | 1 |

Questi valori finiscono in `meta.json` di ogni sessione (`axes`) e, quando la sessione ha posizioni, nel footer di `heat.parquet`, così il visualizzatore 3DHeat ruota e scala le righe da solo: vedi [I dati](the-data.md).

## Multigiocatore {#multiplayer}

- Segnato come giocato online (`multiplayer`): **sì**. `games --markdown` lo mostra come "consentito (legge solo ciò che il gioco pubblica)".
- Tipo `replay`: legge solo ciò che il gioco o la piattaforma rende disponibile (replay e demo che il gioco salva), quindi registra anche nel gioco online oltre che offline; il contrassegno decide solo se la memoria può mai essere letta.
- Memoria: **mai** letta da questo adattatore. Solo gli adattatori `memory` leggono la memoria, e mai per un gioco segnato come giocato online: vedi [Fonti e regole](sources-and-rules.md).

## Statistiche registrate {#statistics-recorded}

Chiavi statistiche che il codice di questo adattatore imposta per nome (`stats` di ogni sessione in `meta.json` e la tabella `stats` di `watcher.sqlite`):

`kills_in_match`, `map`, `match_seconds`, `rounds`, `spikes_planted`

Una chiave tra parentesi graffe viene completata durante l'esecuzione (`score.{team}` è una chiave per ogni squadra). Le chiavi che il codice prende da una tabella dei campi del gioco o dai nomi statistici del gioco non sono in questo elenco; "Cosa viene registrato" sopra le nomina.

## Completezza {#completeness}

Il watcher segue la [regola del convertitore](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md) di 3DHeat: ciò che la sorgente contiene viene letto o conservato, mai scartato. Oltre alle righe, ogni pacchetto, pagina, riga o risposta che l'adattatore riceve viene conservato intero in `heat.raw.parquet` della sessione (colonne `time`, `ms`, `type`, `used`, `payload`, `text`, poi ogni campo conservato per nome; `used` segna ciò che è diventato anche riga), e `selfCheck.completeness` in `meta.json` conta ogni `type`: `lost` è 0.

**Letto**

- il blocco informativo, ogni campo (meta.json `vrf`): versione del file, versioni personalizzate, durata, versione di rete, changelist, nome, flag di diretta, data di registrazione, flag di compressione e cifratura, la chiave come è memorizzata
- il chunk di intestazione: la mappa, l'id della partita e gli agenti scelti (riconosciuti dalla loro forma)
- ogni chunk di evento: id, gruppo, metadati, tempo di inizio e di fine, e dei suoi dati il nome dell'evento, il suo tempo in secondi e i numeri che lo precedono (id di rete di uccisore e vittima) - una riga ciascuno

**Conservato grezzo**

- ogni chunk intero, nell'ordine del file (`offset`), così le parti sono il file: `info`, `header`, `event <gruppo>`, `replay_data`, `checkpoint`, `chunk <n>` per un tipo che il layout non nomina, `trailing` per i byte dopo l'ultimo chunk completo

**Non disponibile**

- posizioni, nomi, punteggi, abilità, ogni fotogramma del gioco: i chunk dei dati di replay e dei checkpoint sono offuscati; leggerli significa smontare il client, cosa che i termini di Riot vietano. Conservati interi, non letti
- il contenuto di un replay cifrato: attraversato e conservato intero, nulla letto all'interno

**Dimensione**: i dati grezzi della sessione occupano circa quanto il replay stesso: il flusso offuscato non si comprime

## Verificato {#verified}

il lettore (heat3d-riot-replays) è costruito dal layout del contenitore documentato da vrfkit (Apache-2.0); non ancora testato su un replay reale, non ce n'era nessuno disponibile - controlla prima di leggere e salta ciò che non corrisponde

## Sorgente {#source}

[heat3d_watch/adapters/riot_replays.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/riot_replays.py)

<!-- Generato dall'adattatore da tools/gen_game_pages.py; per cambiarlo modifica l'adattatore ed eseguilo di nuovo invece di modificare questa pagina. -->
