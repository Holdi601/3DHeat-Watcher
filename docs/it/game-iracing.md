---
title: "iRacing (dati in tempo reale)"
nav_order: 28
lang: "it"
source: game-iracing.md
source_hash: "894d9bc4081f"
nav_exclude: true
search_exclude: true
---
# iRacing (dati in tempo reale) {#iracing-live-data}

Mentre giochi a iRacing, il watcher salva i dati che il gioco stesso invia, così puoi guardarli più tardi come statistiche e una timeline.

*Dettagli tecnici: adattatore `iracing`, tipo [`telemetry`](sources-and-rules.md); gira mentre `iRacingSim64DX11.exe` o `iRacingSim64.exe` è in esecuzione e cerca nuovi dati ogni 0,1 s.*

## Cosa viene registrato {#what-is-recorded}

- la guida a 5 Hz senza posizione (iRacing non ne dà in diretta): velocità, marcia, acceleratore, freno, giro, quota del giro, posizione in gara e di classe, incidenti
- inizio sessione, salita e discesa dall'auto, ingresso e uscita dalla corsia box, bandiera a scacchi, arrivo; giri con il tempo sul giro, incidenti con i loro punti
- i file di telemetria .ibt scritti durante la sessione (latitudine, longitudine, altitudine - il visualizzatore li legge)
- giri, miglior giro, incidenti, posizione in gara, soste ai box, distanza, velocità massima
- l'intera memoria condivisa in `heat.raw.parquet`: intestazione, intestazioni delle variabili, informazioni di sessione, ogni riga di telemetria letta

## Da dove arriva {#where-it-comes-from}

memoria condivisa Local\IRSDKMemMapFileName (l'SDK di iRacing); file .ibt in %USERPROFILE%\Documents\iRacing\telemetry

## Come attivarlo {#how-to-switch-it-on}

Nulla per i dati in diretta. Per le posizioni: registra la telemetria in auto (Alt+L) oppure imposta irsdkLog=1 in app.ini

## Come funziona {#how-it-works}

iRacing, in diretta: l'SDK di memoria condivisa di iRacing, letto in modo nativo.

iRacing pubblica la sua telemetria per le app in una mappatura di file con nome,
`Local\IRSDKMemMapFileName`, che il simulatore crea mentre è in esecuzione (e segnala
`Local\IRSDKDataValidEvent` a ogni aggiornamento, cosa qui non necessaria: il
watcher legge dieci volte al secondo). Il layout è quello di `irsdk_defines.h`
dell'SDK, seguito anche da pyirsdk (MIT) - riscritto qui a partire da quei fatti:

```text
irsdk_header (little-endian int32s)
    0 ver, 4 status (bit 0: connected), 8 tickRate,
    12 sessionInfoUpdate, 16 sessionInfoLen, 20 sessionInfoOffset,
    24 numVars, 28 varHeaderOffset, 32 numBuf, 36 bufLen, 40 pad[2],
    48 varBuf[4]: { tickCount, bufOffset, pad[2] } (16 bytes each)
irsdk_varHeader (144 bytes, numVars of them at varHeaderOffset)
    0 type (0 char, 1 bool, 2 int, 3 bitfield, 4 float, 5 double),
    4 offset (into a line), 8 count, 12 countAsTime + 3 pad,
    16 name[32], 48 desc[64], 112 unit[32]
session info: YAML text at sessionInfoOffset, rewritten when
    sessionInfoUpdate changes (track, sessions, drivers)
```

Il simulatore scrive `numBuf` righe a rotazione; la più recente è quella con il
tickCount più alto, e una riga viene letta di nuovo se il suo tickCount è cambiato
mentre veniva copiata.

I dati in diretta non hanno posizione nel mondo: latitudine, longitudine e altitudine
sono solo nei file `.ibt` che iRacing registra in `Documents\iRacing\telemetry` (Alt+L
in auto, oppure `irsdkLog=1`), che il visualizzatore 3DHeat legge da solo. Quindi qui
la guida viene registrata come eventi senza coordinate - velocità, giro, quota del giro
percorsa, posizione in gara, incidenti - più giri, incidenti, soste ai box e la bandiera
a scacchi, e alla fine i file `.ibt` scritti durante la sessione come eventi
`telemetry_file`, perché il visualizzatore li apra.

Accanto alle righe viene conservata l'intera mappa di memoria, nel file accessorio grezzo della
sessione (`heat.raw.parquet`): la parte fissa dell'intestazione (`header`, ogni volta che
cambia), le intestazioni delle variabili (`var_headers`, intere, e come JSON in `text`,
ogni volta che il layout cambia), il testo YAML delle informazioni di sessione
(`session_info`, il suo testo ogni volta che `sessionInfoUpdate` si muove) e la riga di
telemetria più recente (`telemetry`, ogni variabile, a ogni lettura che trova un tick
nuovo). Le intestazioni delle variabili e una riga bastano a un decodificatore successivo
per leggere ogni variabile.

Fonte: l'SDK di iRacing (irsdk_defines.h, documentazione del forum "iRacing SDK");
kutu/pyirsdk (MIT) per la conferma degli offset.

## Posizioni e assi {#positions-and-axes}

| | |
|---|---|
| Posizioni registrate | no |
| Asse verticale | `y` |
| Unità | nessuna posizione in diretta; i file .ibt hanno latitudine/longitudine/altitudine |
| Specchiato per il visualizzatore | nessuno |
| Scala delle unità (`scale`: il visualizzatore moltiplica le posizioni per questo valore) | 1 |

Questi valori finiscono in `meta.json` di ogni sessione (`axes`) e, quando la sessione ha posizioni, nel footer di `heat.parquet`, così il visualizzatore 3DHeat ruota e scala le righe da solo: vedi [I dati](the-data.md).

## Multigiocatore {#multiplayer}

- Segnato come giocato online (`multiplayer`): **sì**. `games --markdown` lo mostra come "consentito (legge solo ciò che il gioco pubblica)".
- Tipo `telemetry`: legge solo ciò che il gioco o la piattaforma rende disponibile (una porta UDP o la memoria condivisa che il gioco pubblica), quindi registra anche nel gioco online oltre che offline; il contrassegno decide solo se la memoria può mai essere letta.
- Memoria: **mai** letta da questo adattatore. Solo gli adattatori `memory` leggono la memoria, e mai per un gioco segnato come giocato online: vedi [Fonti e regole](sources-and-rules.md).

## Statistiche registrate {#statistics-recorded}

Chiavi statistiche che il codice di questo adattatore imposta per nome (`stats` di ogni sessione in `meta.json` e la tabella `stats` di `watcher.sqlite`):

`best_lap`, `distance_km`, `finishes`, `incidents`, `laps`, `pit_stops`, `race_position`, `sessions`, `top_speed_kmh`

Una chiave tra parentesi graffe viene completata durante l'esecuzione (`score.{team}` è una chiave per ogni squadra). Le chiavi che il codice prende da una tabella dei campi del gioco o dai nomi statistici del gioco non sono in questo elenco; "Cosa viene registrato" sopra le nomina.

## Completezza {#completeness}

Il watcher segue la [regola del convertitore](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md) di 3DHeat: ciò che la sorgente contiene viene letto o conservato, mai scartato. Oltre alle righe, ogni pacchetto, pagina, riga o risposta che l'adattatore riceve viene conservato intero in `heat.raw.parquet` della sessione (colonne `time`, `ms`, `type`, `used`, `payload`, `text`, poi ogni campo conservato per nome; `used` segna ciò che è diventato anche riga), e `selfCheck.completeness` in `meta.json` conta ogni `type`: `lost` è 0.

**Letto**

- dall'ultima riga di telemetria: tempo di sessione, numero, stato e id, in pista, replay, giro, giri completati, quota e metri del giro, ultimo e miglior giro, velocità, marcia, acceleratore, freno, giri motore, corsia box, superficie della pista, posizione in gara e di classe, numero di incidenti dell'auto (le righe `driving` a 5 Hz e gli eventi)
- ora anche sulle righe `driving`: `steering_angle`, `yaw`, `yaw_north`, `pitch`, `roll` (gradi, dai radianti del simulatore - solo quando l'intestazione della variabile dà l'unità come rad), `fuel_l` (unità l), `lat_accel` e `lon_accel` (unità m/s^2)
- dal YAML delle informazioni di sessione: l'indice dell'auto del giocatore, pista e configurazione, tipi di sessione, nome, auto, squadra e numero di ogni pilota (righe session_start, meta.json)
- verificato con un blocco costruito da irsdk_defines.h nei test; non ancora verificato con il simulatore

**Conservato grezzo**

- `telemetry`: l'ultima riga intera, ogni variabile che il simulatore pubblica (gli array CarIdx di ogni auto, pneumatici, sospensioni, gli array ad alta frequenza `_ST` dove il simulatore li ha ...), a ogni lettura che trova un tick nuovo; `tick` il conteggio dei tick del simulatore; `used` è falso mentre un replay è in riproduzione
- `var_headers`: le intestazioni delle variabili intere (144 byte ciascuna) e, in `text`, come JSON (nome, tipo, offset, conteggio, unità, descrizione), ogni volta che il layout cambia - abbastanza per leggere ogni variabile di ogni riga conservata
- `session_info`: il testo YAML intero ogni volta che il suo contatore di aggiornamento si muove (weekend, sessioni e risultati, piloti, assetto dell'auto, radio, elenchi delle inquadrature), `update` il contatore
- `header`: l'intestazione di 112 byte intera ogni volta che cambia (versione, stato, frequenza dei tick, offset, i tick delle righe)

**Non disponibile**

- una posizione nel mondo in diretta: la memoria condivisa non ne ha; latitudine, longitudine e altitudine sono solo nei file .ibt (con la registrazione attiva), che il visualizzatore legge: il watcher indica quelli scritti durante la sessione
- i tick tra due letture: il simulatore scrive 60 righe al secondo in 3 o 4 slot e il watcher legge 10 volte al secondo, quindi la maggior parte dei tick viene sovrascritta prima di poter essere letta; il file .ibt ha ogni tick quando la registrazione è attiva

**Dimensione**: una riga di telemetria è di qualche KB (circa 5-10 KB con gli array di ogni auto), conservata fino a 10 volte al secondo, più l'intestazione (112 byte) altrettanto spesso e il YAML delle informazioni di sessione (decine di KB) quando cambia: circa 0,2-0,4 GB all'ora in pista prima della compressione; zstd lo riduce a una frazione (non ancora misurato su una sessione reale)

## Verificato {#verified}

testato su un blocco di memoria condivisa costruito nel test dal layout irsdk; non ancora testato con il simulatore

## Sorgente {#source}

[heat3d_watch/adapters/iracing.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/iracing.py)

<!-- Generated from the adattatore by tools/gen_game_pages.py; change the adattatore and run it again rather than editing this page. -->
