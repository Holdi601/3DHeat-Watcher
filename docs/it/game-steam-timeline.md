---
title: "Steam Timeline (piattaforma)"
nav_order: 44
lang: "it"
source: game-steam-timeline.md
source_hash: "3878efe0d7f1"
nav_exclude: true
search_exclude: true
---
# Steam Timeline (piattaforma) {#steam-timeline-platform}

Il watcher salva ciò che Steam Timeline conserva sui tuoi giochi, così puoi consultare in seguito la tua cronologia come statistiche e come linea temporale.

*Dettagli tecnici: adattatore `steam-timeline`, tipo [`platform`](sources-and-rules.md); resta sempre attivo (non aspetta l'avvio di un gioco) e cerca nuovi dati ogni 10 s.*

## Cosa viene registrato {#what-is-recorded}

- una sessione per file di linea temporale: il suo inizio e la sua fine (session_start, session_end)
- obiettivi sbloccati durante il gioco, con l'ora
- cambi di modalità di gioco (in gioco, in preparazione, menu, schermata di caricamento)
- eventi che i giochi aggiungono tramite ISteamTimeline, con titolo e descrizione, sotto il nome della loro icona
- fasi di gioco (una partita, una missione) con i loro tag; gli eventi dentro una fase portano il suo id come session
- descrizioni di stato che il gioco mostra sulla linea temporale ("Round 3")
- gli errori di registrazione di Steam stessa

## Da dove arriva {#where-it-comes-from}

%STEAM%\userdata\\&lt;account&gt;\gamerecordings\timelines\timeline_&lt;appid&gt;&lt;data&gt;_&lt;ora&gt;.json

## Come attivarlo {#how-to-switch-it-on}

Steam > Impostazioni > Registrazione di gioco: registra in background o su richiesta (Steam scrive allora le linee temporali)

## Come funziona {#how-it-works}

Ciò che il launcher e il driver della scheda grafica conservano sul gioco: statistiche, obiettivi, tempo di gioco e linee temporali di Steam, e highlight e clip di NVIDIA.

Nessuna di queste fonti richiede che un gioco collabori o sia in esecuzione, quindi i tre adattatori qui sono sempre attivi e guardano pochi file ogni pochi secondi.

#### Steam Timeline (`steam-timeline`) {#steam-timeline-steam-timeline}

`<Steam>\userdata\<account>\gamerecordings\timelines\timeline_<appid><aaaammgg>_<hhmmss>.json`, scritto mentre la Registrazione di gioco di Steam è attiva. Il file è JSON con numeri in forma di stringa: "daterecorded" (secondi Unix), "starttime"/"endtime" (ms) e "entries", ciascuna {"id", "time" (ms da daterecorded), "type", ...}. Tipi visti nei file reali:
```text
achievement        achievement_name - Steam li aggiunge per ogni gioco
gamemode           mode, un ETimelineGameMode: 1 in gioco, 2 in preparazione,
                   3 menu, 4 schermata di caricamento
error              description - di Steam ("#GameRecording_RecordingFailed")
event              un AddInstantaneousTimelineEvent/AddRangeTimelineEvent di un
                   gioco: title, description, icon, priority, duration (ms),
                   possible_clip - "Hai ucciso <nome>" / "con la <arma>"
state_description  title - SetTimelineTooltip ("Round 3")
phase              un intervallo StartGamePhase..EndGamePhase: duration (ms),
                   tags [{name, icon, group, priority}] (modalità, mappa ...)
```
Il layout del file è di Steam e non è documentato; i campi sono i parametri dell'API. Ogni altro tipo viene registrato sotto il suo nome con i suoi campi.
<https://partner.steamgames.com/doc/api/ISteamTimeline>
<https://partner.steamgames.com/doc/features/timeline>

Lo stesso modulo serve anche: [NVIDIA highlights (piattaforma)](game-nvidia-highlights.md), [Statistiche Steam (piattaforma)](game-steam-stats.md).

## Posizioni e assi {#positions-and-axes}

| | |
|---|---|
| Posizioni registrate | no |
| Asse verso l'alto | `y` |
| Unità | metri |
| Specchiato per il visualizzatore | nessuno |
| Scala delle unità (`scale`: il visualizzatore moltiplica le posizioni per questo valore) | 1 |

Questi valori vanno in `meta.json` di ogni sessione (`axes`) e, quando la sessione ha posizioni, nel footer di `heat.parquet`, così il visualizzatore 3DHeat ruota e scala le righe da solo - vedi [I dati](the-data.md).

## Multigiocatore {#multiplayer}

- Segnato come giocato online (`multiplayer`): **no**. `games --markdown` lo mostra come "giocatore singolo".
- Tipo `platform`: legge solo ciò che il gioco o la piattaforma consegnano (ciò che Steam o il driver della scheda grafica conserva), quindi registra anche nel gioco online oltre che offline; il contrassegno decide soltanto se la memoria può mai essere letta.
- Memoria: **mai** letta da questo adattatore. Solo gli adattatori `memory` leggono la memoria, e mai per un gioco segnato come giocato online - vedi [Fonti e regole](sources-and-rules.md).

## Statistiche registrate {#statistics-recorded}

Chiavi di statistica che il codice di questo adattatore imposta per nome (`stats` di ogni sessione in `meta.json` e la tabella `stats` di `watcher.sqlite`):

`achievements`, `game_mode_changes`, `phases`, `recorded_seconds`, `timeline_events`

Una chiave tra parentesi graffe viene completata durante l'esecuzione (`score.{team}` è una chiave per ogni squadra). Le chiavi che il codice prende da una tabella dei campi del gioco o dai nomi di statistica del gioco non sono in questo elenco; "Cosa viene registrato" sopra le nomina.

## Completezza {#completeness}

Il watcher segue la [regola del convertitore](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md) di 3DHeat: ciò che la fonte contiene viene letto o conservato, mai scartato. Oltre alle righe, ogni pacchetto, pagina, riga o risposta che l'adattatore riceve viene conservato intero nel file `heat.raw.parquet` della sessione (colonne `time`, `ms`, `type`, `used`, `payload`, `text`, poi ogni campo conservato per nome; `used` segna ciò che è diventato anche righe), e `selfCheck.completeness` in `meta.json` conta ogni `type` - `lost` è 0.

**Letto**

- ogni voce una volta, come riga al suo momento: il suo tipo, ogni campo semplice (titolo, descrizione, icona, priorità, durata, possible_clip, nome dell'obiettivo, modalità, ...), i tag di una fase per gruppo, il nome visualizzato dell'obiettivo dallo schema delle statistiche; l'inizio e la fine del file

**Conservato grezzo**

- ogni voce intera come JSON sotto il `type` di Steam (`gamemode`, `achievement`, `event`, `state_description`, `phase`, `error`, ogni altro): i campi annidati - l'icona e la priorità di un tag, tutto ciò che un Steam successivo aggiunge - sono solo qui
- `timeline`: i campi propri del file (daterecorded, starttime, endtime, ogni altro), quando la sessione si apre e di nuovo quando cambiano

**Non disponibile**

- la registrazione stessa (video): Steam la conserva nelle sue cartelle; la sessione rimanda al file della linea temporale per nome
- una lettura di un file che Steam sta scrivendo e che non si può analizzare nemmeno con la fine chiusa: conteggiata (`bad` nello stato dell'adattatore) e riletta alla modifica successiva, dove vengono prese le sue voci

**Dimensione**: alcune centinaia di voci da 100-300 byte per ora di gioco: ben sotto 1 MB per ora

## Verificato {#verified}

testato su file reali di linea temporale da un'installazione locale: voci di obiettivo, gamemode, errore e gli eventi, le descrizioni di stato e le fasi propri dei giochi; il formato del file non è documentato

## Fonte {#source}

[heat3d_watch/adapters/platform.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/platform.py)

<!-- Generato dall'adattatore da tools/gen_game_pages.py; per cambiarlo modifica l'adattatore ed eseguilo di nuovo invece di modificare questa pagina. -->
