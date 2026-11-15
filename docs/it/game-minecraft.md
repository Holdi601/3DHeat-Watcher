---
title: "Minecraft (file di log)"
nav_order: 33
lang: "it"
source: game-minecraft.md
source_hash: "35cfea9d36a0"
nav_exclude: true
search_exclude: true
---
# Minecraft (file di log) {#minecraft-log-files}

Mentre giochi a Minecraft, il watcher legge i file che il gioco scrive e salva ciò che è successo, così puoi guardarlo più tardi su una mappa nel visualizzatore 3DHeat.

*Dettagli tecnici: adattatore `minecraft`, tipo [`log`](sources-and-rules.md); gira mentre `javaw.exe` o `java.exe` è in esecuzione e cerca nuovi dati ogni 0,5 s.*

## Cosa viene registrato {#what-is-recorded}

- posizione tua e degli altri giocatori (blocchi = m, y in alto) ogni volta che il mondo viene salvato, con la dimensione come sessione
- spawn con posizione quando un giocatore entra nel server (integrato)
- ingressi, uscite, morti con il messaggio di morte, avanzamenti, righe di chat
- morti, avanzamenti, messaggi di chat; dal file delle statistiche: tempo di gioco, distanza, uccisioni di mob e di giocatori, salti, danni, blocchi estratti, oggetti creati (quota di questa sessione)
- ogni riga di log e ogni file salvato di statistiche, avanzamenti e giocatore intero in heat.raw.parquet

## Da dove arriva {#where-it-comes-from}

%APPDATA%\\.minecraft\logs\latest.log (seguito), saves\\&lt;mondo&gt;\stats\\&lt;uuid&gt;.json e saves\\&lt;mondo&gt;\playerdata\\&lt;uuid&gt;.dat / level.dat (NBT compresso in gzip), letti quando il gioco li salva

## Come attivarlo {#how-to-switch-it-on}

Non serve attivare nulla: il watcher legge la sorgente così come il gioco o la piattaforma la fornisce.

## Come funziona {#how-it-works}

Minecraft (Java Edition): il log, le statistiche e i file dei giocatori che il gioco scrive.

Dove (`%APPDATA%\.minecraft\`):

* `logs\latest.log` - il log del gioco, nuovo a ogni avvio (quello vecchio viene
  compresso in un .log.gz con la data). Righe `[hh:mm:ss] [thread/LEVEL]: messaggio`
  (i mod loader scrivono `[ddMMMyyyy hh:mm:ss.mmm] [thread/LEVEL] [logger/]: ...`).
  Quello che i giocatori vedono in chat è qui: ingressi e uscite, messaggi di morte,
  avanzamenti, chat - il server integrato di un mondo in singolo giocatore scrive le
  stesse righe ancora una volta, quindi una riga ripetuta nello stesso secondo conta una
  volta sola. "Setting user: <nome>" indica il giocatore; la riga del server
  "<nome>[...] logged in with entity id N at (x, y, z)" dice dove è apparso.
* `saves\<mondo>\stats\<uuid>.json` - la schermata delle statistiche, scritta quando
  il mondo viene salvato (salvataggio automatico ogni pochi minuti, e all'uscita): `stats` ->
  `minecraft:custom` (play_time in tick, mob_kills, \*_one_cm distanze, jump,
  ...), `minecraft:mined`, `minecraft:crafted`, ... Totali per il mondo; le cifre della
  sessione sono la differenza rispetto a ciò che il file diceva all'avvio del gioco. Formato: <https://minecraft.wiki/w/Statistics>
* `saves\<mondo>\playerdata\<uuid>.dat` (e `level.dat` -> Data -> Player per un host
  in singolo giocatore) - NBT compresso in gzip, scritto nei medesimi salvataggi:
  `Pos` [x, y, z] come double, `Rotation` [yaw, pitch], `Dimension`
  ("minecraft:overworld"; un int 0/-1/1 prima della 1.16). NBT secondo
  <https://minecraft.wiki/w/NBT_format> - letto qui da un piccolo lettore nostro.
* `saves\<mondo>\advancements\<uuid>.json` - l'avanzamento della schermata degli
  avanzamenti, scritto nei medesimi salvataggi.

Le coordinate sono blocchi, un blocco è un metro, y in alto; x est, z sud - un sistema
destrorso, disegnato così com'è. Le posizioni arrivano solo quando il mondo viene salvato, quindi un
percorso è di pochi punti per ogni salvataggio automatico, non una scia; la dimensione è la
`session`, così il Nether non viene disegnato sopra l'Overworld.

Tutto ciò che viene letto è conservato intero nel file accessorio grezzo della sessione (regola
del convertitore di 3DHeat): ogni riga di log sotto il suo livello (`INFO`, `WARN`,
`ERROR`, ...; una riga senza l'intestazione tra parentesi, come una traccia dello stack,
come `untagged`), e ogni file salvato sotto il suo tipo (`stats`, `advancements`,
`playerdata`, `level.dat`) - JSON come testo, NBT come byte. I numeri di un file delle
statistiche si capiscono solo rispetto a ciò che diceva all'avvio del gioco, quindi anche
quella prima copia viene conservata (`baseline`), la prima volta che il file cambia.

## Posizioni e assi {#positions-and-axes}

| | |
|---|---|
| Posizioni registrate | sì |
| Asse verticale | `y` |
| Unità | blocchi (1 blocco = 1 m) |
| Specchiato per il visualizzatore | nessuno |
| Scala delle unità (`scale`: il visualizzatore moltiplica le posizioni per questo valore) | 1 |

Questi valori finiscono in `meta.json` di ogni sessione (`axes`) e, quando la sessione ha posizioni, nel footer di `heat.parquet`, così il visualizzatore 3DHeat ruota e scala le righe da solo: vedi [I dati](the-data.md).

## Multigiocatore {#multiplayer}

- Segnato come giocato online (`multiplayer`): **sì**. `games --markdown` lo mostra come "consentito (legge solo ciò che il gioco pubblica)".
- Tipo `log`: legge solo ciò che il gioco o la piattaforma rende disponibile (file che il gioco scrive mentre è in esecuzione), quindi registra anche nel gioco online oltre che offline; il contrassegno decide solo se la memoria può mai essere letta.
- Memoria: **mai** letta da questo adattatore. Solo gli adattatori `memory` leggono la memoria, e mai per un gioco segnato come giocato online: vedi [Fonti e regole](sources-and-rules.md).

## Statistiche registrate {#statistics-recorded}

Chiavi statistiche che il codice di questo adattatore imposta per nome (`stats` di ogni sessione in `meta.json` e la tabella `stats` di `watcher.sqlite`):

`advancements`, `bad_files`, `bad_lines`, `chat_messages`, `deaths`, `joins`, `others_deaths`, `world`

Una chiave tra parentesi graffe viene completata durante l'esecuzione (`score.{team}` è una chiave per ogni squadra). Le chiavi che il codice prende da una tabella dei campi del gioco o dai nomi statistici del gioco non sono in questo elenco; "Cosa viene registrato" sopra le nomina.

## Completezza {#completeness}

Il watcher segue la [regola del convertitore](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md) di 3DHeat: ciò che la sorgente contiene viene letto o conservato, mai scartato. Oltre alle righe, ogni pacchetto, pagina, riga o risposta che l'adattatore riceve viene conservato intero in `heat.raw.parquet` della sessione (colonne `time`, `ms`, `type`, `used`, `payload`, `text`, poi ogni campo conservato per nome; `used` segna ciò che è diventato anche riga), e `selfCheck.completeness` in `meta.json` conta ogni `type`: `lost` è 0.

**Letto**

- latest.log: il nome del giocatore (`Setting user`), gli accessi con posizione, ingressi, uscite, morti con il messaggio di morte, avanzamenti, righe di chat, l'arresto del server
- stats/<uuid>.json: tempo di gioco, distanza, uccisioni di mob e di giocatori, salti, danni inflitti e subiti, blocchi estratti, oggetti creati - quota di questa sessione
- playerdata/<uuid>.dat e level.dat (NBT): posizione, dimensione, imbardata, beccheggio, salute, livello di esperienza

**Conservato grezzo**

- ogni riga di latest.log intera, `type` = il suo livello (`INFO`, `WARN`, `ERROR`, `DEBUG`, `FATAL`) con il thread del logger in `thread`, `used` dove è diventata una riga; una riga senza l'intestazione tra parentesi (una traccia dello stack, un banner di un mod) come `untagged`
- ogni stats/<uuid>.json intero come testo, `type` `stats` (`used`: i suoi numeri sono nelle statistiche), con la sua prima copia dall'avvio del gioco come `baseline`
- ogni advancements/<uuid>.json intero come testo, `type` `advancements` (ogni criterio e quando è stato soddisfatto; non ancora trasformato in righe)
- ogni playerdata/<uuid>.dat e level.dat intero come byte (NBT gzip), `type` `playerdata` / `level.dat`, `used` dove ha dato una posizione: inventario, baule dell'Ender, effetti, punto di spawn, regole di gioco, seed del mondo e ora sono solo qui
- ogni file salvato ha `world` e `file` (il suo percorso sotto `saves`)

**Non disponibile**

- una scia di posizioni: il gioco scrive la posizione del giocatore solo quando il mondo viene salvato (ogni pochi minuti e all'uscita)
- posizioni su un server ospitato da altri: i suoi file del mondo sono sul server, non qui; in quel caso si legge solo il log
- il mondo stesso (file regione .mca, entità, mappe data/\*.dat e raid): grandi, e il terreno, non il gioco
- i log delle sessioni precedenti (logs/\*.log.gz): conservati quando sono stati giocati
- Bedrock Edition: non scrive questo tipo di log o file

**Dimensione**: latest.log 0,1-2 MB all'ora (di più con i mod); un file di statistiche 5-50 KB e un file di giocatore 5-100 KB per salvataggio automatico, level.dat 1-20 KB - circa 1-5 MB all'ora in tutto; zstd in heat.raw.parquet riduce il testo a circa un decimo (i file NBT sono già in gzip)

## Verificato {#verified}

testato su righe di log sintetiche, JSON di statistiche e file NBT costruiti dai formati pubblicati; non ancora testato con il gioco

## Sorgente {#source}

[heat3d_watch/adapters/minecraft.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/minecraft.py)

<!-- Generated from the adattatore by tools/gen_game_pages.py; change the adattatore and run it again rather than editing this page. -->
