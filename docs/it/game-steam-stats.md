---
title: "Statistiche Steam (piattaforma)"
nav_order: 42
lang: "it"
source: game-steam-stats.md
source_hash: "09ecf3611c02"
nav_exclude: true
search_exclude: true
---
# Statistiche Steam (piattaforma) {#steam-statistics-platform}

Il watcher salva ciò che le statistiche di Steam conservano sui tuoi giochi, così puoi consultare in seguito la tua cronologia come statistiche e come linea temporale.

*Dettagli tecnici: adattatore `steam-stats`, tipo [`platform`](sources-and-rules.md); resta sempre attivo (non aspetta l'avvio di un gioco) e cerca nuovi dati ogni 30 s.*

## Cosa viene registrato {#what-is-recorded}

- ogni statistica che un gioco memorizza in Steam (i suoi nomi e valori), per gioco, quando cambia
- sblocchi di obiettivi con nome visualizzato, descrizione e ora di sblocco
- cambi di statistica con valore precedente, nuovo valore e differenza
- tempo di gioco (minuti, ultime due settimane) e ora dell'ultima partita

## Da dove arriva {#where-it-comes-from}

la cache locale delle statistiche di Steam %STEAM%\appcache\stats\UserGameStats_&lt;account&gt;_&lt;appid&gt;.bin con UserGameStatsSchema_&lt;appid&gt;.bin; il tempo di gioco da %STEAM%\userdata\\&lt;account&gt;\config\localconfig.vdf (%STEAM% da HKCU\Software\Valve\Steam SteamPath)

## Come attivarlo {#how-to-switch-it-on}

Non serve attivare nulla: il watcher legge la fonte così come il gioco o la piattaforma la fornisce.

## Come funziona {#how-it-works}

Ciò che il launcher e il driver della scheda grafica conservano sul gioco: statistiche, obiettivi, tempo di gioco e linee temporali di Steam, e highlight e clip di NVIDIA.

Nessuna di queste fonti richiede che un gioco collabori o sia in esecuzione, quindi i tre adattatori qui sono sempre attivi e guardano pochi file ogni pochi secondi.

#### Statistiche Steam (`steam-stats`) {#steam-statistics-steam-stats}

`<Steam>\appcache\stats\UserGameStats_<account>_<appid>.bin`, riscritto dal client Steam ogni volta che un gioco memorizza le sue statistiche, decodificato con lo schema `UserGameStatsSchema_<appid>.bin` accanto ad esso (KeyValues binario, vedi `_steam.py`). Le statistiche sono interi o decimali come le definisce il gioco; gli obiettivi sono bit con un'ora di sblocco in secondi Unix. Il tempo di gioco è in `<Steam>\userdata\<account>\config\localconfig.vdf` sotto apps/&lt;appid&gt;: Playtime e Playtime2wks in minuti, LastPlayed in secondi Unix. Steam si trova tramite HKCU\Software\Valve\Steam SteamPath.
API delle statistiche: <https://partner.steamgames.com/doc/features/achievements>

Lo stesso modulo serve anche: [NVIDIA highlights (piattaforma)](game-nvidia-highlights.md), [Steam Timeline (piattaforma)](game-steam-timeline.md).

## Posizioni e assi {#positions-and-axes}

| | |
|---|---|
| Posizioni registrate | no |
| Asse verticale | `y` |
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

`achievements_total`, `achievements_unlocked`, `last_played`, `playtime_2wks_minutes`, `playtime_minutes`

Una chiave tra parentesi graffe viene completata durante l'esecuzione (`score.{team}` è una chiave per ogni squadra). Le chiavi che il codice prende da una tabella dei campi del gioco o dai nomi di statistica del gioco non sono in questo elenco; "Cosa viene registrato" sopra le nomina.

## Completezza {#completeness}

Il watcher segue la [regola del convertitore](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md) di 3DHeat: ciò che la fonte contiene viene letto o conservato, mai scartato. Oltre alle righe, ogni pacchetto, pagina, riga o risposta che l'adattatore riceve viene conservato intero nel file `heat.raw.parquet` della sessione (colonne `time`, `ms`, `type`, `used`, `payload`, `text`, poi ogni campo conservato per nome; `used` segna ciò che è diventato anche righe), e `selfCheck.completeness` in `meta.json` conta ogni `type` - `lost` è 0.

**Letto**

- ogni statistica del file di statistiche con il suo nome API (int, float, avgrate), ogni bit di obiettivo con la sua ora di sblocco, con nome e descrizione dallo schema
- cambi rispetto all'ultima lettura (precedente, nuovo, differenza), nuovi sblocchi; tempo di gioco, tempo delle ultime due settimane e ultima partita da localconfig.vdf

**Conservato grezzo**

- `UserGameStats`: i byte del file di statistiche, interi, ogni volta che viene registrato (il `crc`, `PendingChanges`, i bit di obiettivo che lo schema non definisce più e ogni chiave che il decodificatore salta sono lì dentro)
- `UserGameStatsSchema`: i byte del file dello schema accanto ad esso, così le statistiche possono essere decodificate dalla sola sessione (i nomi di ogni statistica e obiettivo in tutte le lingue, icone, flag)
- `localconfig_app`: l'intero blocco del gioco da localconfig.vdf come JSON (stato della sincronizzazione cloud, opzioni di avvio, badge e ogni altra chiave che Steam conserva per gioco) quando ne viene registrato il tempo di gioco
- un file di statistiche che il decodificatore non sa leggere (tagliato a metà durante la scrittura, o un layout nuovo): i suoi byte e lo schema in una sessione senza righe (`used` falso; `unreadable` in meta.json)

**Non disponibile**

- il resto di localconfig.vdf (amici, chat, impostazioni di Steam): non riguarda il gioco, ed è privato
- i valori delle statistiche tra due scritture: Steam riscrive il file quando il gioco memorizza le sue statistiche, di solito alla chiusura
- le percentuali globali degli obiettivi e le statistiche di altri giocatori: si trovano sui server di Steam, non qui

**Dimensione**: alcuni KB per ogni sessione registrata, più lo schema (fino a qualche centinaio di KB per un gioco con molti obiettivi) - ben sotto 1 MB per ora di gioco; zstd riduce il testo dello schema della metà o più

## Verificato {#verified}

testato su file di statistiche e schemi reali da un'installazione locale; rilevamento dei cambi testato su file costruiti nel formato KeyValues binario

## Fonte {#source}

[heat3d_watch/adapters/platform.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/platform.py)

<!-- Generato dall'adattatore da tools/gen_game_pages.py; per cambiarlo modifica l'adattatore ed eseguilo di nuovo invece di modificare questa pagina. -->
