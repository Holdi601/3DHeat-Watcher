---
title: "Path of Exile (file di log)"
nav_order: 36
lang: "it"
source: game-poe.md
source_hash: "9facfd5a1551"
nav_exclude: true
search_exclude: true
---
# Path of Exile (file di log) {#path-of-exile-log-files}

Mentre giochi a Path of Exile, il watcher legge i file che il gioco scrive e salva ciò che è successo, così puoi guardarlo più tardi come statistiche e una timeline.

*Dettagli tecnici: adattatore `poe`, tipo [`log`](sources-and-rules.md); funziona mentre `PathOfExile.exe`, `PathOfExile_x64.exe`, `PathOfExileSteam.exe`, `PathOfExile_x64Steam.exe`, `PathOfExileEGS.exe`, `PathOfExile_x64EGS.exe`, `PathOfExile_KG.exe` o `PathOfExile_x64_KG.exe` è in esecuzione e cerca nuovi dati ogni 0,5 s.*

## Cosa viene registrato {#what-is-recorded}

- zone entrate con il livello dell'area, l'id dell'area e il suo seed
- salite di livello con classe e livello
- morti ("has been slain")
- giocatori che entrano ed escono dall'area, sussurri in entrata e in uscita, richieste di scambio, scambi accettati
- ogni riga di Client.txt di questa sessione intera in heat.raw.parquet
- morti, livelli guadagnati, livello massimo, zone entrate, zone distinte, sussurri, richieste di scambio, scambi

## Da dove arriva {#where-it-comes-from}

&lt;installazione&gt;\logs\Client.txt di Path of Exile o Path of Exile 2 (seguito; la cartella di installazione è quella dell'eseguibile in esecuzione)

## Come attivarlo {#how-to-switch-it-on}

Non serve attivare nulla: il watcher legge la fonte così come il gioco o la piattaforma la fornisce.

## Come funziona {#how-it-works}

Path of Exile e Path of Exile 2: il log del client, `<installazione>\logs\Client.txt`.

Entrambi i giochi aggiungono in coda un unico Client.txt nella loro cartella di installazione finché sono installati (cresce tra un avvio e l'altro). Le righe hanno questa forma

```text
2024/01/01 12:00:00 123456789 cff94598 [INFO Client 1234] : You have entered Lioneye's Watch.
2024/01/01 12:00:00 123456789 cff94598 [DEBUG Client 1234] Generating level 2 area "1_1_2" with seed 1
2024/01/01 12:00:00 123456789 cff94598 [INFO Client 1234] : Name (Witch) is now level 2
2024/01/01 12:00:00 123456789 cff94598 [INFO Client 1234] : Name has been slain.
2024/01/01 12:00:00 123456789 cff94598 [INFO Client 1234] @From Name: Hi, I would like to buy your ...
```

- ora locale, un contatore in millisecondi, un hash, il livello e il thread, poi ciò che mostra la
  finestra della chat. I messaggi sono quelli del client inglese; un client in un'altra lingua li scrive
  tradotti e qui non vengono capiti. Nulla dà una posizione. Il formato non è documentato da Grinding Gear Games; è il
  log in testo semplice del gioco, come lo leggono da anni gli strumenti della comunità (strumenti di scambio, guide ai livelli) - ad es.
  <https://github.com/klayveR/poe-log-monitor> (MIT) per l'elenco degli eventi.

La cartella di installazione è quella dell'eseguibile in esecuzione; senza di esso vengono cercate le librerie di Steam e la cartella predefinita del client standalone.

Ogni riga di questa sessione viene conservata intera nei dati grezzi della sessione (regola del convertitore di
3DHeat), che abbia o no un significato qui: `type` è il livello e il logger tra le sue parentesi
(`INFO Client`, `DEBUG Client`, `WARN Client`, ...), una riga con data ma senza parentesi è
`untagged`, una riga senza data `untimed`.

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

`bad_lines`, `character_class`, `deaths`, `level`, `levels_gained`, `trade_requests_received`, `trade_requests_sent`, `trades`, `whispers`, `zones_distinct`, `zones_entered`

Una chiave tra parentesi graffe viene completata durante l'esecuzione (`score.{team}` è una chiave per squadra). Le chiavi che il codice prende da una tabella dei campi del gioco o dai nomi di statistica del gioco non sono in questo elenco; "Cosa viene registrato" sopra le nomina.

## Completezza {#completeness}

Il watcher segue la [regola del convertitore](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md) di 3DHeat: ciò che la fonte contiene viene letto o conservato, mai scartato. Oltre alle righe, ogni pacchetto, pagina, riga o risposta che l'adattatore riceve viene conservato intero in `heat.raw.parquet` della sessione (colonne `time`, `ms`, `type`, `used`, `payload`, `text`, poi ogni campo conservato per nome; `used` segna ciò che è diventato anche riga), e `selfCheck.completeness` in `meta.json` conta ogni `type` - `lost` è 0.

**Letto**

- `You have entered <zona>`, con il livello dell'area, l'id dell'area e il seed della riga `Generating level` che la precede
- `<nome> (<classe>) is now level <n>`, `<nome> has been slain`, giocatori che entrano ed escono dall'area, sussurri in entrata e in uscita (con l'indicazione se sono una richiesta di scambio), scambi accettati e annullati

**Conservato grezzo**

- ogni riga di questa sessione intera, `type` = il livello e il logger tra le parentesi (`INFO Client`, `DEBUG Client`, `WARN Client`, `CRIT Client`, ...), `used` dove è diventata una riga: chat globale, di scambio, di gruppo e di gilda, `Connecting to instance server`, avvisi AFK e DND, le risposte ai comandi di chat come `/played` e `/deaths`, le righe di caricamento e del motore del client - conservate, non ancora trasformate in righe
- una riga con data ma senza parentesi (`***** LOG FILE OPENING *****`) come `untagged`, una riga senza data come `untimed`

**Non disponibile**

- posizioni: nulla nel log ne dà una
- ciò che scrive un client in un'altra lingua: le righe vengono conservate, ma solo i messaggi inglesi diventano righe
- le righe dei precedenti avvii: Client.txt cresce tra un avvio e l'altro; le righe datate prima di questa esecuzione del gioco vengono lasciate (sono state conservate quando sono state giocate)
- uccisioni, danni, bottino e l'albero passivo: il gioco non li registra

**Dimensione**: Client.txt cresce di circa 0,3-3 MB all'ora (soprattutto per le righe DEBUG durante il caricamento delle aree, di più con una chat di scambio molto attiva); zstd in heat.raw.parquet lo riduce a circa un decimo

## Verificato {#verified}

testato su righe sintetiche di Client.txt nel formato del gioco; non ancora testato con il gioco

## Fonte {#source}

[heat3d_watch/adapters/poe.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/poe.py)

<!-- Generated from the adattatore by tools/gen_game_pages.py; change the adattatore and run it again rather than editing this page. -->
