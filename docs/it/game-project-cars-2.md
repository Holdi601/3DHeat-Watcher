---
title: "Project CARS 2 (dati in tempo reale)"
nav_order: 37
lang: "it"
source: game-project-cars-2.md
source_hash: "a1990b93b7d1"
nav_exclude: true
search_exclude: true
---
# Project CARS 2 (dati in tempo reale) {#project-cars-2-live-data}

Mentre giochi a Project CARS 2, il watcher salva i dati che il gioco stesso invia, così puoi guardarli più tardi su una mappa nel visualizzatore 3DHeat.

*Dettagli tecnici: adattatore `project-cars-2`, tipo [`telemetry`](sources-and-rules.md); funziona mentre `pCARS2AVX.exe` o `pCARS2.exe` è in esecuzione e cerca nuovi dati ogni 0,1 s.*

## Cosa viene registrato {#what-is-recorded}

- posizione di ogni auto (XYZ nel mondo, m) a 10 Hz per nome del pilota, con la tua auto contrassegnata, con velocità e posizione in gara; marcia, acceleratore e freno della tua auto
- inizio sessione con la pista che il gioco indica; giri per auto con il tempo sul giro; arrivi; tuoi pit stop
- teletrasporti (ritorno ai box, un riavvio): `teleport` dove si trovava l'auto, `spawn` dove si trova ora
- tuoi giri, giro migliore, posizione in gara, distanza, velocità massima
- l'intera pagina di memoria condivisa del gioco in `heat.raw.parquet`, ogni volta che cambia

## Da dove arriva {#where-it-comes-from}

memoria condivisa $pcars2$ (SMS SharedMemory.h)

## Come attivarlo {#how-to-switch-it-on}

Nel gioco: Opzioni > Sistema > Memoria condivisa: "Project CARS 2"

## Come funziona {#how-it-works}

Memoria condivisa che i giochi di guida pubblicano per le dashboard, aperta in sola lettura - e
mai creata.

Diversi simulatori consegnano la loro telemetria come una mappatura di file di Windows
con nome che il gioco crea e che chiunque può leggere: le pagine `Local\acpmf_*` di Kunos (Assetto Corsa,
ACC, AC Rally, `Local\acevo_pmf_*` di AC EVO), `Local\IRSDKMemMapFileName` di iRacing,
`$R3E` di RaceRoom, `$pcars2$` di Automobilista 2 / Project CARS 2.

Perché non `mmap.mmap(-1, size, tagname=...)`, il modo Python più usato: quando
la mappatura non esiste ancora, ne *crea* una - qui in sola lettura. Un gioco
avviato dopo apre la mappatura del watcher invece di farne una propria e poi
non può scriverci, quindi la sua telemetria resta morta finché il watcher non la lascia.
Il watcher avvia un adattatore appena compare il processo del gioco, che è esattamente il
momento in cui il gioco non ha ancora creato la sua mappatura. Quindi questo apre con
`OpenFileMappingW`, che trova solo una mappatura già esistente, la mappa con
`FILE_MAP_READ` e altrimenti risponde "non ancora presente"; gli adattatori riprovano
poco dopo.

Niente qui può scrivere: la vista è mappata in sola lettura e viene copiata
solo con `ctypes.string_at`.

Due giochi sono letti anche qui; ogni auto in pista è nelle loro pagine.

#### Automobilista 2 / Project CARS 2 - `$pcars2$` {#automobilista-2--project-cars-2---pcars2}

`SharedMemory.h` di SMS (fornito nella cartella Support\SharedMemory del gioco;
AMS2: Opzioni > Sistema > Memoria condivisa "Project CARS 2"), `#pragma pack(4)`.
`mParticipantInfo[64]` dal byte 28, 100 byte ciascuno: mIsActive, mName[64],
mWorldPosition[3] (m, Y in alto), mCurrentLapDistance, mRacePosition,
mLapsCompleted, mCurrentLap, mCurrentSector; mViewedParticipantIndex (20)
è l'auto del giocatore; per partecipante mLastLapTimes (9200), mRaceStates
(9520), mSpeeds (10800); il mBestLapTime (6716), mLastLapTime
(6720), mSpeed (6848), mBrake, mThrottle, mGear del giocatore; mSequenceNumber (7320) è
dispari mentre il gioco scrive. Gli offset sono stati ricavati da due
copie indipendenti dell'intestazione (la copia del gioco non è installata
qui), che concordano.

Entrambe le pagine sono conservate intere oltre a tutto il resto (docs/converters.md, "Live sources"): la
mappatura intera, ogni lettura i cui byte differiscono dalla copia conservata per ultima, nei dati grezzi della
sessione sotto `type` `r3e` o `pcars2` - ogni slot di pilota e ogni campo della struttura,
anche quelli non letti qui, così un decodificatore futuro ha bisogno solo dei dati grezzi.

Lo stesso modulo serve anche: [Automobilista 2 (dati in tempo reale)](game-automobilista-2.md), [RaceRoom Racing Experience (dati in tempo reale)](game-raceroom.md).

## Posizioni e assi {#positions-and-axes}

| | |
|---|---|
| Posizioni registrate | sì |
| Asse verticale | `y` |
| Unità | metri |
| Specchiato per il visualizzatore | nessuno |
| Scala delle unità (`scale`: il visualizzatore moltiplica le posizioni per questo valore) | 1 |

Questi valori finiscono in `meta.json` di ogni sessione (`axes`) e, quando la sessione ha posizioni, nel footer di `heat.parquet`, così il visualizzatore 3DHeat ruota e scala le righe da solo - vedi [I dati](the-data.md).

## Multigiocatore {#multiplayer}

- Segnato come giocato online (`multiplayer`): **sì**. `games --markdown` lo mostra come "consentito (legge solo ciò che il gioco pubblica)".
- Tipo `telemetry`: legge solo ciò che il gioco o la piattaforma consegna (una porta UDP o una memoria condivisa che il gioco pubblica), quindi registra anche nel gioco online oltre che offline; il flag decide solo se la memoria può mai essere letta.
- Memoria: **mai** letta da questo adattatore. Solo gli adattatori `memory` leggono la memoria, e mai per un gioco segnato come giocato online - vedi [Fonti e regole](sources-and-rules.md).

## Statistiche registrate {#statistics-recorded}

Chiavi di statistica che il codice di questo adattatore imposta per nome (`stats` di ogni sessione in `meta.json` e la tabella `stats` di `watcher.sqlite`):

`best_lap`, `distance_km`, `finishes`, `incidents`, `laps`, `pit_stops`, `race_position`, `top_speed_kmh`

Una chiave tra parentesi graffe viene completata durante l'esecuzione (`score.{team}` è una chiave per squadra). Le chiavi che il codice prende da una tabella dei campi del gioco o dai nomi di statistica del gioco non sono in questo elenco; "Cosa viene registrato" sopra le nomina.

## Completezza {#completeness}

Il watcher segue la [regola del convertitore](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md) di 3DHeat: ciò che la fonte contiene viene letto o conservato, mai scartato. Oltre alle righe, ogni pacchetto, pagina, riga o risposta che l'adattatore riceve viene conservato intero in `heat.raw.parquet` della sessione (colonne `time`, `ms`, `type`, `used`, `payload`, `text`, poi ogni campo conservato per nome; `used` segna ciò che è diventato anche riga), e `selfCheck.completeness` in `meta.json` conta ogni `type` - `lost` è 0.

**Letto**

- per partecipante (fino a 64): attivo, nome, posizione nel mondo, posizione in gara, giri completati; il suo ultimo tempo sul giro, stato di gara e velocità
- l'auto del giocatore (mViewedParticipantIndex), stato di gioco e sessione, posizione e variante della pista, giro migliore e ultimo, velocità, freno, acceleratore, marcia; mSequenceNumber per saltare una copia presa mentre viene scritta
- offset da due copie indipendenti di SharedMemory.h di SMS che concordano, verificati su una pagina costruita con esse nei test; non ancora verificati con il gioco

**Conservato grezzo**

- `pcars2`: l'intera mappatura di $pcars2$ - la struttura va ben oltre gli 11.312 byte letti qui - ogni lettura i cui byte differiscono dalla copia conservata per ultima: l'orientamento di ogni partecipante, i tempi di settore, i nomi di auto e classe, le modalità e i flag dei pit, la fisica del giocatore, gomme, sospensioni, danni, meteo e tutto ciò che le versioni successive di Project CARS 2 hanno aggiunto
- `used` è vero per una pagina letta in righe; falso per una pagina nei menu, in pausa, in un replay, di un altro layout o presa mentre viene scritta (`torn` 1); `unchanged_reads` in meta.json conta le letture identiche byte per byte alla copia conservata prima

**Non disponibile**

- gli input e la fisica degli altri partecipanti: la pagina dà solo l'auto osservata
- tutto mentre l'opzione di memoria condivisa del gioco è disattivata (Project CARS 2 non scrive nulla allora)

**Dimensione**: la mappatura è di circa 20-30 KB (secondo la versione del gioco), fino a 10 volte al secondo mentre si guida: circa 0,7-1,1 GB all'ora prima della compressione; zstd riduce gli slot dei partecipanti vuoti e i nomi che non cambiano a una frazione (non ancora misurato su una sessione reale)

## Verificato {#verified}

testato su una pagina costruita nel test; offset da due copie indipendenti di SharedMemory.h che concordano, non dalla copia che fornisce il gioco; non ancora testato con il gioco

## Fonte {#source}

[heat3d_watch/adapters/simracing_shm.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/simracing_shm.py)

<!-- Generated from the adattatore by tools/gen_game_pages.py; change the adattatore and run it again rather than editing this page. -->
