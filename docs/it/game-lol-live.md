---
title: "League of Legends (stato di gioco)"
nav_order: 29
lang: "it"
source: game-lol-live.md
source_hash: "75c67c6fe84f"
nav_exclude: true
search_exclude: true
---
# League of Legends (stato di gioco) {#league-of-legends-game-state}

Mentre giochi a League of Legends, il watcher salva ciò che il gioco comunica ai programmi sul tuo computer, così puoi guardarlo più tardi come statistiche e una timeline.

*Dettagli tecnici: adattatore `lol-live`, tipo [`gsi`](sources-and-rules.md); funziona mentre `League of Legends.exe` è in esecuzione e cerca nuovi dati ogni 0,5 s.*

## Cosa viene registrato {#what-is-recorded}

- nessuna posizione: l'API non ne ha
- feed delle uccisioni: uccisioni, morti e assist del giocatore, uccisioni di altri campioni con uccisore, vittima, assistenti
- draghi, araldi, baroni, torri, inibitori, multiuccisioni, aces, primo sangue, inizio e fine partita
- uccisioni, morti, assist, punteggio creep, punteggio ward, livello, oro, campione, tempo di gioco, risultato del giocatore
- obiettivi conquistati dalla squadra del giocatore

## Da dove arriva {#where-it-comes-from}

Live Client Data API del client di gioco, <https://127.0.0.1:2999/liveclientdata/> (allgamedata, eventdata), durante una partita

## Come attivarlo {#how-to-switch-it-on}

Non serve attivare nulla: il watcher legge la fonte così come il gioco o la piattaforma la fornisce.

## Come funziona {#how-it-works}

League of Legends: la Live Client Data API che il client di gioco serve durante una partita.

Mentre una partita è in corso (anche in modalità allenamento e spettatore), `League of
Legends.exe` risponde su <https://127.0.0.1:2999> con ciò che il giocatore può vedere
nell'interfaccia del gioco:

```text
/liveclientdata/allgamedata          activePlayer (riotId, level, currentGold, championStats),
                                     allPlayers (championName, team ORDER/CHAOS, level,
                                     scores: kills, deaths, assists, creepScore, wardScore),
                                     events, gameData (gameMode, gameTime s, mapName)
/liveclientdata/eventdata?eventID=N  {"Events": [...]} dal EventID N in poi: GameStart,
                                     MinionsSpawning, FirstBlood, FirstBrick, TurretKilled,
                                     InhibKilled, InhibRespawningSoon, InhibRespawned,
                                     DragonKill, HeraldKill, BaronKill, ChampionKill
                                     (KillerName, VictimName, Assisters), Multikill
                                     (KillStreak), Ace (Acer, AcingTeam), GameEnd (Result)
```

Non ci sono posizioni: l'API non ne ha, quindi una sessione di League è fatta di eventi e
statistiche, senza una tabella di calore. Il certificato è autofirmato, dalla radice di Riot stessa
(`riotgames.pem`, pubblicata su
<https://static.developer.riotgames.com/docs/lol/riotgames.pem>). Le sue condizioni d'uso
non sono dichiarate, quindi non viene distribuito: mettilo in `<dati>\riotgames.pem` e
la connessione viene verificata con esso; senza, la verifica è disattivata - e solo
mai per 127.0.0.1, l'unico indirizzo a cui parla questo adattatore.

La politica di Riot consente agli strumenti di mostrare ciò che il giocatore potrebbe sapere dal gioco
stesso, e nient'altro calcolato al di là di esso (niente timer dei nemici): questo registra il feed
delle uccisioni e il punteggio che il giocatore vede, e i numeri del giocatore stesso.

Ogni risposta viene anche conservata intera (regola del convertitore di 3DHeat, docs/converters.md nel
repository del visualizzatore): `heat.raw.parquet`, `type` l'endpoint
("allgamedata", "eventdata"), `text` il JSON come l'ha inviato il client, `status`
quando non era 200. Una risposta identica byte per byte a quella precedente del suo endpoint (la lista
degli eventi mentre non succede nulla) viene conservata una volta e contata in `unchanged_replies` di
meta.json. allgamedata contiene già ciò che danno gli altri endpoint (activeplayer\*, playerlist, playerscores, playeritems, playersummonerspells,
playermainrunes, gamestats), quindi non vengono interrogati a parte. Le risposte prima
di una partita (la schermata di caricamento) aspettano in un backlog e vanno nella sessione della partita;
dopo GameEnd la sessione resta aperta finché il client non si chiude, così le risposte della schermata finale
vengono conservate con essa.

Fonte: <https://developer.riotgames.com/docs/lol#game-client-api>

## Posizioni e assi {#positions-and-axes}

| | |
|---|---|
| Posizioni registrate | no |
| Asse verticale | `z` |
| Unità | nessuna (nessuna posizione) |
| Specchiato per il visualizzatore | nessuno |
| Scala delle unità (`scale`: il visualizzatore moltiplica le posizioni per questo valore) | 1 |

Questi valori finiscono in `meta.json` di ogni sessione (`axes`) e, quando la sessione ha posizioni, nel footer di `heat.parquet`, così il visualizzatore 3DHeat ruota e scala le righe da solo - vedi [I dati](the-data.md).

## Multigiocatore {#multiplayer}

- Segnato come giocato online (`multiplayer`): **sì**. `games --markdown` lo mostra come "consentito (legge solo ciò che il gioco pubblica)".
- Tipo `gsi`: legge solo ciò che il gioco o la piattaforma consegna (un'integrazione di stato di gioco o un'API locale che il gioco serve), quindi registra anche nel gioco online oltre che offline; il flag decide solo se la memoria può mai essere letta.
- Memoria: **mai** letta da questo adattatore. Solo gli adattatori `memory` leggono la memoria, e mai per un gioco segnato come giocato online - vedi [Fonti e regole](sources-and-rules.md).

## Statistiche registrate {#statistics-recorded}

Chiavi di statistica che il codice di questo adattatore imposta per nome (`stats` di ogni sessione in `meta.json` e la tabella `stats` di `watcher.sqlite`):

`bad_packets`, `champion`, `game_time`, `gold`, `level`, `result`

Una chiave tra parentesi graffe viene completata durante l'esecuzione (`score.{team}` è una chiave per squadra). Le chiavi che il codice prende da una tabella dei campi del gioco o dai nomi di statistica del gioco non sono in questo elenco; "Cosa viene registrato" sopra le nomina.

## Completezza {#completeness}

Il watcher segue la [regola del convertitore](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md) di 3DHeat: ciò che la fonte contiene viene letto o conservato, mai scartato. Oltre alle righe, ogni pacchetto, pagina, riga o risposta che l'adattatore riceve viene conservato intero in `heat.raw.parquet` della sessione (colonne `time`, `ms`, `type`, `used`, `payload`, `text`, poi ogni campo conservato per nome; `used` segna ciò che è diventato anche riga), e `selfCheck.completeness` in `meta.json` conta ogni `type` - `lost` è 0.

**Letto**

- il feed delle uccisioni da eventdata: ogni evento una volta, con i suoi campi con nome decodificati (uccisore, vittima e assistenti con campione e squadra, strutture e il loro lato, tipo di drago, furti, multiuccisioni, aces, primo sangue, il risultato) e ogni altro campo di un evento sulla sua riga con il proprio nome
- da allgamedata: uccisioni, morti, assist, punteggio creep, punteggio ward, livello, oro, campione, tempo di gioco, modalità e mappa di gioco

**Conservato grezzo**

- `allgamedata`: ogni risposta intera (`text`), ogni 2 s - activePlayer (abilità, ogni statistica del campione, rune complete, oro, livello), allPlayers (oggetti con slot e prezzi, rune, incantesimi da evocatore, punteggi, livello, morto e timer di rinascita, skin, corsia, bot), gli eventi, gameData (modalità, tempo, mappa, terreno); `used` vero mentre la partita è in corso, falso nella schermata finale
- `eventdata`: ogni risposta intera, richiesta ogni 0,5 s dal prossimo id evento in poi; `used` vero quando ha portato nuovi eventi
- una risposta identica byte per byte a quella precedente del suo endpoint viene conservata una volta e contata (`unchanged_replies` in meta.json); le risposte di errore (il RESOURCE_NOT_FOUND della schermata di caricamento) vengono conservate con il loro `status`, prima dell'inizio della partita

**Non disponibile**

- posizioni: l'API non ne ha (niente minimappa, niente coordinate)
- gli altri endpoint (activeplayer, activeplayername, activeplayerabilities, activeplayerrunes, playerlist, playerscores, playersummonerspells, playermainrunes, playeritems, gamestats): ognuno serve una parte di allgamedata, quindi non vengono interrogati
- la Replay API (`/replay/*` sulla stessa porta): riproduce i replay e le partite guardate una volta attivata in game.cfg, non fa parte di una partita giocata
- gli endpoint del lockfile del client di League: non sono un'API pubblicata (Fonti e regole)
- valori tra due letture: l'API risponde quando viene interrogata e non invia spontaneamente; il punteggio viene chiesto ogni 2 s, gli eventi ogni 0,5 s

**Dimensione**: allgamedata pesa 15-40 KB (contiene l'intera lista degli eventi, che cresce) ogni 2 s: circa 30-70 MB all'ora in `raw.bin`; eventdata aggiunge poco, perché le risposte identiche vengono contate, non memorizzate; zstd riduce il JSON ripetuto in `heat.raw.parquet` a qualche MB all'ora (stimato dal formato documentato)

## Verificato {#verified}

testato con un server locale finto che serve risposte nel formato documentato; non ancora testato con il gioco

## Fonte {#source}

[heat3d_watch/adapters/lol.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/lol.py)

<!-- Generated from the adattatore by tools/gen_game_pages.py; change the adattatore and run it again rather than editing this page. -->
