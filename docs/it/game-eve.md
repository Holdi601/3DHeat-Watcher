---
title: "EVE Online (file di log)"
nav_order: 20
lang: "it"
source: game-eve.md
source_hash: "a5ab6c312c86"
nav_exclude: true
search_exclude: true
---
# EVE Online (file di log) {#eve-online-log-files}

Mentre giochi a EVE Online, il watcher legge i file che il gioco scrive e salva ciò che è successo, così puoi guardarlo più tardi come statistiche e una timeline.

*Dettagli tecnici: adattatore `eve`, tipo [`log`](sources-and-rules.md); funziona mentre `exefile.exe` è in esecuzione e cerca nuovi dati ogni 0,5 s.*

## Cosa viene registrato {#what-is-recorded}

- danni inflitti e subiti con l'altra nave, il pilota, il sigla della corporazione, l'arma e la qualità del colpo
- colpi mancati inflitti e subiti
- taglie riscosse (uccisioni di NPC) con ISK
- salti tra sistemi
- ogni riga dei gamelog e dei chat log intera in heat.raw.parquet
- danni inflitti e subiti, colpi, uccisioni con taglia e ISK, salti

## Da dove arriva {#where-it-comes-from}

%USERPROFILE%\Documents\EVE\logs\Gamelogs\\\*.txt e i Chatlogs\\\*.txt accanto (ogni file scritto dall'avvio del client)

## Come attivarlo {#how-to-switch-it-on}

Non serve attivare nulla: il watcher legge la fonte così come il gioco o la piattaforma la fornisce.

## Come funziona {#how-it-works}

EVE Online: i log di gioco del client, `Documents\EVE\logs\Gamelogs\*.txt`.

Il client scrive un file per personaggio per ogni accesso,
`<yyyymmdd>_<hhmmss>[_<id personaggio>].txt`; la registrazione su file è attiva di default. Più
client aperti insieme scrivono ciascuno il proprio, quindi viene seguito ogni file scritto dall'avvio del
gioco. Intestazione e righe (l'ora di EVE è UTC):

```text
------------------------------------------------------------
  Gamelog
  Listener: Character Name
  Session Started: 2024.07.02 19:41:40
------------------------------------------------------------
[ 2024.07.02 20:31:28 ] (combat) <color=0xff00ffff><b>200</b> <color=0x77ffffff><font size=10>to</font>
    <b><color=0xffffffff>Pilot[TICK](../Ship)</b><font size=10><color=0x77ffffff> - Weapon - Penetrates
[ 2024.06.25 15:20:01 ] (combat) <color=0xffcc0000><b>375</b> ... from ... - Weapon - Hits
[ 2024.06.25 15:21:00 ] (bounty) <font size=12><b><color=0xff00aa00>15,000 ISK</b> added to next bounty payout
[ 2024.06.25 15:30:00 ] (None) Jumping from System A to System B
```

(la riga combat è una sola riga nel file). I tag di formattazione vengono rimossi prima
del confronto. Il file è stato in UTF-8 e in UTF-16 nel corso degli anni; vengono letti entrambi.
Il formato non è documentato da CCP; è il log in testo semplice del client, letto come
gli strumenti della comunità per il combat log lo leggono (ad es. <https://docs.rs/crate/eve-log-parser>).
Nessuna posizione.

Accanto, `Documents\EVE\logs\Chatlogs\<canale>_<yyyymmdd>_<hhmmss>[_<id>].txt`:
un file per canale di chat per accesso (quando il log della chat è attivo, come di default nel client),
UTF-16, un'intestazione con il nome del canale e del listener, poi
`[ yyyy.mm.dd hh:mm:ss ] Mittente > messaggio`.

Ogni riga di entrambi viene conservata intera nei dati grezzi della sessione (regola del convertitore
di 3DHeat): una riga di gamelog sotto il suo canale tra parentesi (`combat`,
`notify`, `bounty`, `None`, ...), una riga di chat come `chat` con il suo canale, le
righe di intestazione come `gamelog header` / `chatlog header`.

## Posizioni e assi {#positions-and-axes}

| | |
|---|---|
| Posizioni registrate | no |
| Asse verticale | `y` |
| Unità | nessuna posizione registrata |
| Specchiato per il visualizzatore | nessuno |
| Scala delle unità (`scale`: il visualizzatore moltiplica le posizioni per questo valore) | 1 |

Questi valori finiscono in `meta.json` di ogni sessione (`axes`) e, quando la sessione ha posizioni, nel footer di `heat.parquet`, così il visualizzatore 3DHeat ruota e scala le righe da solo - vedi [I dati](the-data.md).

## Multigiocatore {#multiplayer}

- Segnato come giocato online (`multiplayer`): **sì**. `games --markdown` lo mostra come "consentito (legge solo ciò che il gioco pubblica)".
- Tipo `log`: legge solo ciò che il gioco o la piattaforma consegna (file che il gioco scrive mentre è in esecuzione), quindi registra anche nel gioco online oltre che offline; il flag decide solo se la memoria può mai essere letta.
- Memoria: **mai** letta da questo adattatore. Solo gli adattatori `memory` leggono la memoria, e mai per un gioco segnato come giocato online - vedi [Fonti e regole](sources-and-rules.md).

## Statistiche registrate {#statistics-recorded}

Chiavi di statistica che il codice di questo adattatore imposta per nome (`stats` di ogni sessione in `meta.json` e la tabella `stats` di `watcher.sqlite`):

`bad_lines`, `bounty_isk`, `bounty_kills`, `damage_dealt`, `damage_received`, `hits_dealt`, `hits_received`, `jumps`, `misses_dealt`, `misses_received`

Una chiave tra parentesi graffe viene completata durante l'esecuzione (`score.{team}` è una chiave per squadra). Le chiavi che il codice prende da una tabella dei campi del gioco o dai nomi di statistica del gioco non sono in questo elenco; "Cosa viene registrato" sopra le nomina.

## Completezza {#completeness}

Il watcher segue la [regola del convertitore](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md) di 3DHeat: ciò che la fonte contiene viene letto o conservato, mai scartato. Oltre alle righe, ogni pacchetto, pagina, riga o risposta che l'adattatore riceve viene conservato intero in `heat.raw.parquet` della sessione (colonne `time`, `ms`, `type`, `used`, `payload`, `text`, poi ogni campo conservato per nome; `used` segna ciò che è diventato anche riga), e `selfCheck.completeness` in `meta.json` conta ogni `type` - `lost` è 0.

**Letto**

- gamelog `(combat)`: colpi inflitti e subiti (quantità, altro pilota, sigla della corporazione, nave, arma, qualità del colpo) e mancati in entrambi i sensi
- gamelog `(bounty)`: pagamenti di taglie con ISK, e le righe `Jumping from A to B`
- Listener nell'intestazione del gamelog: di chi è il log

**Conservato grezzo**

- ogni riga del gamelog intera, `type` = il suo canale tra parentesi (`combat`, `notify`, `info`, `bounty`, `mining`, `question`, `hint`, `warning`, `None`, ...), con `file` e `listener`; `used` dove è diventata una riga; le righe di intestazione come `gamelog header`
- ogni riga del chat log intera (Local, corporazione, flotta, canali privati, gli avvisi `EVE System` come il cambio del canale Local dopo un salto), `type` `chat`, con `channel`, `listener` e `file`; le righe di intestazione come `chatlog header`. Non ancora trasformate in righe
- i tag di formattazione (`<color>`, `<b>`, `<font>`) restano nel testo grezzo; le righe ne sono prive

**Non disponibile**

- posizioni: il client non ne scrive nei suoi log
- i combattimenti di altri piloti: un gamelog è quello del listener
- i log dei precedenti accessi: ogni accesso scrive nuovi file; quelli più vecchi di questa esecuzione del client non vengono riletti
- la chat quando il giocatore ha disattivato il log della chat nelle impostazioni del client
- i file di cache e di impostazioni del client: non sono log, e non sono documentati

**Dimensione**: un gamelog pesa 0,1-2 MB all'ora (soprattutto in combattimento); i chat log dipendono dai canali aperti - un canale Local o di flotta molto attivo 0,5-3 MB all'ora; zstd in heat.raw.parquet lo riduce a circa un decimo

## Verificato {#verified}

testato su righe di gamelog sintetiche nel formato pubblicato dai parser della comunità; non ancora testato con il gioco

## Fonte {#source}

[heat3d_watch/adapters/eve.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/eve.py)

<!-- Generated from the adattatore by tools/gen_game_pages.py; change the adattatore and run it again rather than editing this page. -->
