---
title: "Rocket League (stato di gioco)"
nav_order: 39
lang: "it"
source: game-rocketleague-stats.md
source_hash: "fd70d0540bb9"
nav_exclude: true
search_exclude: true
---
# Rocket League (stato di gioco) {#rocket-league-game-state}

Mentre giochi a Rocket League, il watcher salva ciò che il gioco riferisce ai programmi sul tuo computer, così puoi guardarlo più tardi su una mappa nel visualizzatore 3DHeat.

*Dettagli tecnici: adattatore `rocketleague-stats`, tipo [`gsi`](sources-and-rules.md); gira mentre `RocketLeague.exe` è in esecuzione e cerca nuovi dati ogni 0,05 s.*

## Cosa viene registrato {#what-is-recorded}

- tocchi della palla con il punto della palla (XYZ, unità Unreal), chi l'ha toccata e le velocità
- gol con il punto dell'impatto, il marcatore, l'assistente e la velocità; colpi alla traversa con il punto
- feed statistico (demolizioni, parate, tiri, parate epiche, ...), calci d'inizio, replay, inizio e fine partita, vincitore
- autogol, assist, parate, tiri, demolizioni, tocchi, punteggio e punteggi di squadra, da UpdateState
- la riga finale di ogni giocatore alla fine della partita
- le tue righe come `me`: il giocatore indicato nelle impostazioni (`config --set player_names.rocketleague-stats=<nome>`), altrimenti quello che la telecamera del gioco segue fuori dai replay
- nessuna posizione delle auto: l'API non ne ha

## Da dove arriva {#where-it-comes-from}

API statistiche: flusso JSON TCP da 127.0.0.1:49123 (porta in &lt;RL&gt;\TAGame\Config\TAStatsAPI.ini o DefaultStatsAPI.ini)

## Come attivarlo {#how-to-switch-it-on}

`python -m heat3d_watch setup rocketleague-stats --apply` (imposta PacketSendRate=30), poi avvia Rocket League

Digita il comando in un terminale aperto nella cartella del watcher (vedi [Prima di iniziare](before-you-start.md)). Se fallisce, l'ultima riga dice perché; [Installazione e avvio](installing-and-running.md) elenca le cause più comuni.

`python -m heat3d_watch setup rocketleague-stats` elenca i file che cambierebbe; `python -m heat3d_watch setup rocketleague-stats --apply` li cambia, conservando l'originale come `<file>.heat3d-backup` (vedi [Comandi](commands.md#setup)). Stampa `rocketleague-stats: changed: ...` per ogni modifica, oppure `rocketleague-stats: nothing to change` quando è già attivo.

## Come funziona {#how-it-works}

Rocket League: l'API statistiche ufficiale, un socket locale su cui il gioco scrive i dati della partita.

Si attiva in `<RL>\TAGame\Config\TAStatsAPI.ini` - oppure `DefaultStatsAPI.ini`
quando il primo non esiste, cosa che il gioco legge solo in quel caso - sotto
`[TAGame.MatchStatsExporter_TA]`:

```text
PacketSendRate   messaggi UpdateState al secondo; 0 (predefinito) spegne l'API, al massimo 120
Port             la porta TCP su cui il gioco è in ascolto, predefinita 49123 (WebPort 49124 è una copia WebSocket)
```

Il gioco è il server: un client si connette a 127.0.0.1:49123 e legge un flusso
di oggetti JSON `{"Event": nome, "Data": {...}}` (alcune versioni inviano Data come
stringa JSON), uno dopo l'altro senza separatori. Gli eventi vengono inviati nel tick
in cui accadono, indipendentemente dalla frequenza:

```text
UpdateState   MatchGuid, Players[] (Name, PrimaryId, Shortcut, TeamNum 0 blu / 1 arancione,
              Score, Goals, Shots, Assists, Saves, Touches, CarTouches, Demos; stato dell'auto
              solo per gli spettatori), Game (Teams[], TimeSeconds, bOvertime, Ball {Speed,
              TeamNum}, bReplay, bHasWinner, Winner, Arena, bHasTarget, Target)
BallHit       Players[] (Name, Shortcut, TeamNum), Ball {PreHitSpeed, PostHitSpeed, Location {X,Y,Z}}
GoalScored    GoalSpeed, GoalTime, ImpactLocation {X,Y,Z}, Scorer, Assister, BallLastTouch
CrossbarHit   BallLocation {X,Y,Z}, BallSpeed, ImpactForce, BallLastTouch
StatfeedEvent EventName, Type, MainTarget, SecondaryTarget
MatchEnded    WinnerTeamNum
MatchCreated, MatchInitialized, CountdownBegin, RoundStarted, GoalReplayStart/WillEnd/End,
MatchPaused/Unpaused, PodiumStart, ReplayCreated, MatchDestroyed, ClockUpdatedSeconds
```

Le posizioni sono unità Unreal (centimetri), Z in alto; il campo è circa 8200 x 10240
con le porte a Y = +-5120. Le posizioni delle auto non fanno parte dell'API: ha un luogo
solo la palla, dove è stata colpita, segnata o ha colpito la traversa.

Ogni messaggio viene anche conservato intero (regola del convertitore di 3DHeat,
docs/converters.md nel repository del visualizzatore): `heat.raw.parquet`, `type` il nome
dell'evento del messaggio, `text` l'oggetto così come è arrivato dal flusso. Un
UpdateState identico byte per byte al precedente (partita in pausa, menu) viene
conservato una volta sola e conteggiato in `unchanged_replies` di meta.json. I messaggi
tra una partita e l'altra attendono in un arretrato per la sessione della partita
successiva; ciò che resta quando il gioco si chiude ottiene una sessione tutta sua.
I caratteri tra un oggetto e l'altro che non sono JSON vengono conservati come "junk".

Fonti: <https://www.rocketleague.com/en/developer/stats-api> (la pagina ufficiale);
capitalizzazione dei campi e framing TCP confermati con il client rlstatsapi
(<https://docs.rs/crate/rlstatsapi>, MIT; letto solo per i fatti).

## Posizioni e assi {#positions-and-axes}

| | |
|---|---|
| Posizioni registrate | sì |
| Asse verticale | `z` |
| Unità | unità Unreal (centimetri) |
| Specchiato per il visualizzatore | nessuno |
| Scala delle unità (`scale`: il visualizzatore moltiplica le posizioni per questo valore) | 1 |

Questi valori finiscono in `meta.json` di ogni sessione (`axes`) e, quando la sessione ha posizioni, nel footer di `heat.parquet`, così il visualizzatore 3DHeat ruota e scala le righe da solo: vedi [I dati](the-data.md).

## Multigiocatore {#multiplayer}

- Segnato come giocato online (`multiplayer`): **sì**. `games --markdown` lo mostra come "consentito (legge solo ciò che il gioco pubblica)".
- Tipo `gsi`: legge solo ciò che il gioco o la piattaforma rende disponibile (un'integrazione di stato di gioco o un'API locale che il gioco serve), quindi registra anche nel gioco online oltre che offline; il contrassegno decide solo se la memoria può mai essere letta.
- Memoria: **mai** letta da questo adattatore. Solo gli adattatori `memory` leggono la memoria, e mai per un gioco segnato come giocato online: vedi [Fonti e regole](sources-and-rules.md).

## Statistiche registrate {#statistics-recorded}

Chiavi statistiche che il codice di questo adattatore imposta per nome (`stats` di ogni sessione in `meta.json` e la tabella `stats` di `watcher.sqlite`):

`bad_packets`, `demolished`, `other_goals`, `overtime`, `result`, `team_goals`

Una chiave tra parentesi graffe viene completata durante l'esecuzione (`score.{team}` è una chiave per ogni squadra). Le chiavi che il codice prende da una tabella dei campi del gioco o dai nomi statistici del gioco non sono in questo elenco; "Cosa viene registrato" sopra le nomina.

## Completezza {#completeness}

Il watcher segue la [regola del convertitore](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md) di 3DHeat: ciò che la sorgente contiene viene letto o conservato, mai scartato. Oltre alle righe, ogni pacchetto, pagina, riga o risposta che l'adattatore riceve viene conservato intero in `heat.raw.parquet` della sessione (colonne `time`, `ms`, `type`, `used`, `payload`, `text`, poi ogni campo conservato per nome; `used` segna ciò che è diventato anche riga), e `selfCheck.completeness` in `meta.json` conta ogni `type`: `lost` è 0.

**Letto**

- BallHit (luogo, chi, squadra, velocità prima e dopo), GoalScored (luogo dell'impatto, marcatore, assistente, velocità, tempo del gol), CrossbarHit (luogo, ultimo tocco, velocità, forza), StatfeedEvent (evento, tipo, bersaglio principale e secondario), MatchEnded (vincitore, esito), il nome di ogni altro evento come riga
- da UpdateState: l'arena, il bersaglio della telecamera fuori dai replay (chi è `me`), i punteggi di squadra, gol, assist, parate, tiri, demolizioni, tocchi, tocchi con l'auto e punteggio di ogni giocatore (quelli propri come statistiche, quelli di tutti come `player_result` alla fine della partita); il supplementare da ClockUpdatedSeconds

**Conservato grezzo**

- ogni messaggio intero così come è arrivato dal flusso (`text`), sotto il suo nome di evento: `UpdateState` (il PrimaryId e lo Shortcut di ogni giocatore, l'orologio, la velocità e la squadra della palla, i nomi e i colori delle squadre, i flag di replay e di vincitore, e lo stato dell'auto dove il gioco lo invia), `BallHit`, `GoalScored` (con l'ultimo tocco della palla), `CrossbarHit`, `StatfeedEvent`, `MatchCreated`, `MatchInitialized`, `CountdownBegin`, `RoundStarted`, `GoalReplayStart`, `GoalReplayWillEnd`, `GoalReplayEnd`, `MatchPaused`, `MatchUnpaused`, `MatchEnded`, `PodiumStart`, `ReplayCreated`, `MatchDestroyed`, `ClockUpdatedSeconds` e ogni evento che una build successiva aggiunge
- un UpdateState identico byte per byte al precedente (in pausa, menu) viene conservato una volta e conteggiato (`unchanged_replies` in meta.json)
- messaggi tra le partite: al loro momento, prima dell'inizio della partita successiva; dopo l'ultima partita, in una sessione tutta sua (`raw_only` in meta.json)
- `unreadable`: un oggetto che non è un messaggio dell'API statistiche; `junk`: caratteri tra un oggetto e l'altro

**Non disponibile**

- stato e posizioni delle auto mentre si gioca: il gioco li invia solo agli spettatori
- UpdateState tra due invii: il gioco invia PacketSendRate al secondo (`setup` imposta 30, il gioco consente fino a 120); gli eventi vengono inviati nel tick in cui accadono
- la copia WebSocket su WebPort (49124): gli stessi messaggi della porta TCP, non letti due volte

**Dimensione**: un UpdateState è di 1-3 KB per sei giocatori, 30 al secondo: circa 100-300 MB all'ora in `raw.bin` mentre una partita è in corso, un decimo o meno nel `heat.raw.parquet` zstd (stimato dal formato documentato, non misurato sul gioco)

## Verificato {#verified}

testato su messaggi nel formato documentato inviati da un server locale finto; non ancora testato con il gioco

## Fonte {#source}

[heat3d_watch/adapters/rocketleague.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/rocketleague.py)

<!-- Generato dall'adattatore da tools/gen_game_pages.py; per cambiarlo modifica l'adattatore ed eseguilo di nuovo invece di modificare questa pagina. -->
