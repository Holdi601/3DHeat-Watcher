---
title: "Dota 2 (replay)"
nav_order: 12
lang: "it"
source: game-dota-replays.md
source_hash: "88539ee6dc65"
nav_exclude: true
search_exclude: true
---
# Dota 2 (replay) {#dota-2-replays}

Dopo una partita di Dota 2, il watcher trasforma il replay salvato dal gioco in file che puoi guardare su una mappa nel visualizzatore 3DHeat.

*Dettagli tecnici: adattatore `dota-replays`, tipo [`replay`](sources-and-rules.md); gira sempre (non aspetta l'avvio di una partita) e cerca nuovi dati ogni 5 s.*

## Cosa viene registrato {#what-is-recorded}

- posizione, altezza, vita e livello di ogni eroe, 7,5 volte al secondo mentre è vivo
- uccisioni e morti dove sono avvenute; torri, caserme, Roshan e Tormentor dove sono caduti; ward dove sono state piazzate
- i ping sulla mappa, i disegni sulla mappa e gli ordini (movimento, attacco, incantesimo, acquisto, ...) di ogni giocatore, dove puntavano
- il punteggio e la riga di ogni giocatore; quella del giocatore con cui hai effettuato l'accesso come statistiche
- tutto il resto che il replay contiene, conservato intero accanto alla tabella: ogni frame e messaggio di rete, ogni cambio di proprietà di entità, ogni voce delle tabelle di stringhe

## Da dove arriva {#where-it-comes-from}

i replay che Dota 2 salva: &lt;Dota&gt;/game/dota/replays/&lt;id partita&gt;.dem (scaricati dal client, oppure con `dota-replay <id partita>`)

## Come attivarlo {#how-to-switch-it-on}

scarica il replay di una partita in Dota 2, oppure recuperane uno pubblico: `python -m heat3d_watch dota-replay <id partita>`; installa il lettore: github.com/Holdi601/3DHeat-Ext-DotaReplay (`heat3d-dota-replay`, porta con sé gem-dota)

Scrivi il comando in un terminale aperto nella cartella del watcher (vedi [Prima di iniziare](before-you-start.md)). Se fallisce, l'ultima riga dice il motivo; [Installazione e avvio](installing-and-running.md) descrive le cause più comuni.

Impostazioni dalle variabili d'ambiente:

- `HEAT3D_DOTA_REPLAY`: la cartella del lettore (un clone o una release estratta), quando non è installato o non si trova accanto al watcher

## Come funziona {#how-it-works}

Replay e demo: ciò che un gioco salva di una partita, convertito una volta che la partita è finita.

Un replay contiene tutto ciò che un'interfaccia in diretta trattiene nei giochi multigiocatore - la posizione di ogni giocatore, ogni uccisione dove è avvenuta - ed è un file che il gioco scrive per i suoi giocatori, quindi leggerlo non tocca nulla nel gioco. Il watcher controlla le cartelle dove i giochi li salvano, aspetta che un nuovo file smetta di crescere (altrimenti il gioco lo sta ancora scrivendo) e lo converte in un thread di lavoro, così una conversione lunga non blocca il resto del watcher.

La prima volta che una cartella viene vista, i replay già presenti vengono solo annotati, non convertiti: un giocatore con anni di demo troverebbe altrimenti il watcher occupato per un giorno. `python -m heat3d_watch replays <id adattatore> [cartella]` converte quelli esistenti su richiesta.

#### Dota 2 {#dota-2}

Dota 2 salva i replay che il giocatore scarica (i dettagli di una partita, oppure Guarda > Replay) in `<Dota>/game/dota/replays/<id partita>.dem`; Valve conserva il replay di ogni partita pubblica sui suoi server per alcune settimane, e `python -m heat3d_watch dota-replay <id partita>` ne recupera uno dal suo id tramite OpenDota. Il watcher non li legge da sé: lo fa un lettore esterno (3DHeat Dota Replay, github.com/Holdi601/3DHeat-Ext-DotaReplay, `exporters/ext/dota-replay`, comando `heat3d-dota-replay`, che legge tramite gem-dota, MIT), un progetto a sé, eseguito in un processo proprio su ogni nuovo replay quando si trova nel PATH, è installato o si trova accanto al watcher; se manca, il watcher dice una volta come installarlo. Il lettore scrive posizione, altezza, vita, livello, direzione, mana, esperienza, attributi e oggetti di ogni eroe 7,5 volte al secondo mentre è vivo; uccisioni e morti dove sono avvenuti; torri, caserme, Roshan e Tormentor dove sono caduti; ogni ward dove è stata piazzata e dove è finita; le voci del combat log sugli eroi (danni, cure, abilità, oggetti, acquisti, rune, oro, esperienza, modificatori); e i ping sulla mappa, i disegni e gli ordini di ogni giocatore - nel file `dota/<match>.parquet`; ogni altra unità (creep, evocazioni, illusioni, corrieri, edifici) una volta al secondo in `<match>.units.parquet`; l'intero combat log in `<match>.combatlog.parquet`; e la partita, la chat, il draft, tutto ciò che il parser estrae e il riepilogo di fine partita del gioco in `<match>.match.json`, nella cartella della sessione. Tutto il resto che il replay contiene viene conservato intero accanto a questi (regola del convertitore di 3DHeat): ogni frame e messaggio di rete in `<match>.packets.parquet`, ogni cambio di proprietà di entità in `<match>.entities.parquet`, ogni voce della tabella di stringhe in `<match>.strings.parquet`, contati in `selfCheck.completeness` del documento della partita. Le posizioni sono nelle unità del mondo di Dota, le stesse che riporta la game-state integration. La riga del punteggio del giocatore con cui hai effettuato l'accesso diventa le statistiche della sessione: uccisioni, morti, assist, last hit, denies, valore netto, GPM, XPM, danni agli eroi, ward, e se la partita è stata vinta. Una nuova patch di Dota può cambiare le entità del replay prima che gem la segua; un replay che gem non riesce a leggere fino in fondo viene convertito fin dove arriva e segnato come `incomplete` nel suo riepilogo.

Lo stesso modulo serve anche: [Counter-Strike 2 (replay)](game-cs2-demos.md), [Squad (replay)](game-squad-demos.md), [War Thunder (replay)](game-warthunder-replays.md), [World of Tanks (replay)](game-wot-replays.md), [World of Warships (replay)](game-wows-replays.md).

## Posizioni e assi {#positions-and-axes}

| | |
|---|---|
| Posizioni registrate | sì |
| Asse verticale | `z` |
| Unità | unità del mondo di Dota (unità di Hammer; la mappa è larga circa 16400) |
| Specchiato per il visualizzatore | `y` |
| Scala delle unità (`scale`: il visualizzatore moltiplica le posizioni per questo valore) | 1 |

Questi valori finiscono in `meta.json` (`axes`) di ogni sessione e, quando la sessione ha delle posizioni, nel footer di `heat.parquet`, così il visualizzatore 3DHeat ruota e scala le righe da solo - vedi [I dati](the-data.md).

## Multigiocatore {#multiplayer}

- Segnato come giocato online (`multiplayer`): **sì**. `games --markdown` lo mostra come "consentito (legge solo ciò che il gioco pubblica)".
- Tipo `replay`: legge solo ciò che il gioco o la piattaforma consegna (replay e demo che il gioco salva), quindi registra anche nel gioco online oltre che offline; il flag decide solo se la memoria può mai essere letta.
- Memoria: **mai** letta da questo adattatore. Solo gli adattatori `memory` leggono la memoria, e mai per un gioco segnato come giocato online - vedi [Fonti e regole](sources-and-rules.md).

## Statistiche registrate {#statistics-recorded}

Chiavi statistiche che il codice di questo adattatore imposta per nome (`stats` di ogni sessione in `meta.json` e la tabella `stats` di `watcher.sqlite`):

`duration`, `hero`, `score.{team}`, `team`, `won`

Una chiave tra parentesi graffe viene completata durante l'esecuzione (`score.{team}` è una chiave per squadra). Le chiavi che il codice prende da una tabella dei campi del gioco o dai nomi statistici del gioco non sono in questo elenco; "Cosa viene registrato" qui sopra le nomina.

## Completezza {#completeness}

Il convertitore segue la [regola del convertitore](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md) di 3DHeat: ciò che il replay contiene viene letto o conservato, mai scartato. Oltre alla tabella, tutto il resto che il replay contiene viene conservato intero in file accessori accanto ad essa, nella cartella `dota/` della sessione - `<match>.packets.parquet`, `<match>.entities.parquet`, `<match>.strings.parquet` (colonne `time`, `tick`, `type`, `name`, `entity`, `decoded`, `payload`, come si applicano) - e `selfCheck.completeness` del documento della partita (`<match>.match.json`) conta ogni `type` - `lost` è 0.

**Letto**

- la tabella (`dota/<match>.parquet`): posizione, altezza, vita, livello, direzione, mana, esperienza, attributi, armatura, velocità, danni, oggetti e cursore del giocatore di ogni eroe, 7,5 volte al secondo; uccisioni, morti, obiettivi, ward, le voci del combat log sugli eroi; i ping sulla mappa (`ping`, DOTA_UM_LocationPing), i disegni sulla mappa (`map_line`, DOTA_UM_MapLine) e ogni ordine di unità (`order`, DOTA_UM_SpectatorPlayerUnitOrders: `other` il tipo di ordine, `value` l'id dell'abilità o dell'oggetto, `text` la classe del bersaglio; nel punto dell'ordine, altrimenti sull'eroe)
- `<match>.units.parquet`: ogni altra unità una volta al secondo; `<match>.combatlog.parquet`: l'intero combat log come lo legge gem, ogni campo
- il documento della partita: tutto ciò che gem estrae, e interi i record del replay stesso - `fileHeader` (DEM_FileHeader), `fileInfo` (DEM_FileInfo: durata della riproduzione, nome, eroe, Steam id e squadra di ogni giocatore), `matchDetails` (DOTA_UM_MatchDetails: il tabellone di fine partita del game coordinator, i numeri di ogni giocatore, oggetti, danni per tipo, scelte e ban) e `matchMetadata` (DOTA_UM_MatchMetadata)
- `selfCheck.crossCheck`: uccisioni, morti, assist, livello, last hit e denies come letti dal flusso, confrontati con `matchDetails`, per giocatore

**Conservato grezzo**

- `<match>.packets.parquet`: ogni frame che non è un pacchetto (`type` `frame <n>`) e ogni messaggio di rete (`message <n>`, `name` il nome di Valve), intero in `payload`, nell'ordine del file (`seq`, `frame`), con `decoded` il protobuf come JSON (un campo di byte dato come la sua lunghezza), ogni tipo di messaggio decodificato: svc_PacketEntities (il flusso delle entità), DOTA_UM_SpectatorPlayerUnitOrders, UM_ParticleManager, i messaggi del combat log, GE_SosStartSoundEvent, DOTA_UM_TE_\* (proiettili, animazioni, sangue), DOTA_UM_OverheadEvent, DOTA_UM_UnitEvent, svc_UpdateStringTable, net_Tick, ...; le tabelle di invio, la lista delle classi e le informazioni del server che un decoder successivo delle entità richiede sono tra questi
- `<match>.entities.parquet`: ogni proprietà di ogni entità ogni volta che cambia (`type` la proprietà, `name` la classe, `entity` il suo indice; `value`, `vector` o `decoded`), il suo stato completo alla creazione, e ogni creazione, ingresso, uscita ed eliminazione - milioni di righe per una partita intera
- `<match>.strings.parquet`: ogni voce della tabella di stringhe da ogni aggiornamento e da ogni snapshot completo, il valore intero; `userinfo`, `ActiveModifiers` e `EconItems` decodificati dai loro protobuf
- `selfCheck.completeness` nel documento della partita conta frame e messaggi con il nome di Valve, le voci del combat log (`combatlog <type>`), gli eventi di gioco (`gameevent <name>`), le voci della tabella di stringhe (`stringtable <name>`) e gli aggiornamenti delle entità (`entity <class>`); alcuni sono conservati solo grezzi (gli snapshot completi delle entità che gem salta perché ricostruisce dai delta, e le voci di tabelle i cui valori nessuno legge), perdita 0

**Non disponibile**

- la voce: il replay ha la configurazione della voce ma non i dati vocali
- nomi dietro hash e id: suoni e particelle sono nominati con gli hash dei file del gioco, le abilità con id; il replay non porta i nomi (gli oggetti sono nominati tramite il catalogo di gem dove ce l'ha)
- tutto ciò che conoscevano solo i client dei giocatori (la loro camera, il loro schermo) oltre a ciò che il server ha trasmesso; il cursore e ogni ordine ci sono

**Dimensione**: i file accessori insieme sono un po' più grandi del replay stesso, i più grandi sono i pacchetti e le entità; una partita intera richiede uno o due minuti in un unico processo

## Verificato {#verified}

verificato su un replay di una partita pubblica: uccisioni, morti, assist, livello, last hit e denies coincidono con il riepilogo di fine partita del gioco per tutti e dieci i giocatori; ogni messaggio nel file accessorio dei pacchetti viene riserializzato byte per byte; la tabella e le statistiche sono testate con dati sintetici

## Fonte {#source}

[heat3d_watch/adapters/replays.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/replays.py)

<!-- Generated from the adapter by tools/gen_game_pages.py; change the adapter and run it again rather than editing this page. -->
