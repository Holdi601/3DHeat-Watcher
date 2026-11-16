---
title: "RaceRoom Racing Experience (dati in tempo reale)"
nav_order: 37
lang: "it"
source: game-raceroom.md
source_hash: "f3879cd40a67"
nav_exclude: true
search_exclude: true
---
# RaceRoom Racing Experience (dati in tempo reale) {#raceroom-racing-experience-live-data}

Mentre giochi a RaceRoom Racing Experience, il watcher salva i dati che il gioco stesso invia, così puoi guardarli più tardi su una mappa nel visualizzatore 3DHeat.

*Dettagli tecnici: adattatore `raceroom`, tipo [`telemetry`](sources-and-rules.md); funziona mentre `RRRE64.exe` o `RRRE.exe` è in esecuzione e cerca nuovi dati ogni 0,1 s.*

## Cosa viene registrato {#what-is-recorded}

- posizione di ogni auto (XYZ nel mondo, m) a 10 Hz per nome del pilota, con la tua auto contrassegnata, con velocità e posizione in gara; marcia, acceleratore e freno della tua auto
- inizio sessione con la pista che il gioco indica; giri per auto con il tempo sul giro; arrivi; tuoi pit stop
- teletrasporti (ritorno ai box, un riavvio): `teleport` dove si trovava l'auto, `spawn` dove si trova ora
- tuoi giri, giro migliore, posizione in gara, distanza, velocità massima
- l'intera pagina di memoria condivisa del gioco in `heat.raw.parquet`, ogni volta che cambia
- i tuoi punti incidente

## Da dove arriva {#where-it-comes-from}

memoria condivisa $R3E (r3e.h di Sector3, versione 3)

## Come attivarlo {#how-to-switch-it-on}

Non serve attivare nulla: il watcher legge la fonte così come il gioco o la piattaforma la fornisce.

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

#### RaceRoom Racing Experience - `$R3E` {#raceroom-racing-experience---r3e}

`r3e.h` di Sector3 (github.com/sector3studios/r3e-api, sample-c/src/r3e.h,
versione 3.6), `#pragma pack(1)`. L'intestazione dice dove iniziano i piloti
e quanto è grande ciascuno (`all_drivers_offset`, `driver_data_size`), quindi la
parte per pilota - nome, slot, posto, posizione nel mondo (float x y z, m),
giri completati, tempo del giro corrente, stato di arrivo, corsia dei box, velocità - viene letta
con quelli. I campi propri del giocatore (giro migliore e precedente, posizione in gara,
punti incidente, marcia, pedali, nomi di pista e tracciato) vengono letti agli offset della 3.6
solo quando `all_drivers_offset` è il 2008 che quel layout gli assegna. Y è considerato in alto;
l'intestazione non lo dice.

Lo stesso modulo serve anche: [Automobilista 2 (dati in tempo reale)](game-automobilista-2.md), [Project CARS 2 (dati in tempo reale)](game-project-cars-2.md).

## Posizioni e assi {#positions-and-axes}

| | |
|---|---|
| Posizioni registrate | sì |
| Asse verticale | `y` |
| Unità | metri; Y in alto supposto (r3e.h non lo dice) |
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

- per slot di pilota (secondo l'offset e la dimensione dell'intestazione): nome, slot, stato di arrivo, posto, posizione nel mondo, giri completati, tempo del giro corrente, corsia dei box, velocità
- i campi propri del giocatore, solo quando la pagina è nel layout r3e.h 3.6: nomi di pista e tracciato, tipo di sessione, posizione in gara, giro migliore e precedente, punti incidente, marcia, acceleratore, freno, lo slot del giocatore
- offset ricavati da r3e.h 3.6 di Sector3 e verificati su una pagina costruita da esso nei test; non ancora verificati con il gioco

**Conservato grezzo**

- `r3e`: l'intera mappatura di $R3E, ogni lettura i cui byte differiscono dalla copia conservata per ultima - ogni campo di r3e.h: la fisica del giocatore (orientamento, velocità, accelerazioni, forze G), motore, carburante, gomme, freni, danni, flag, menu dei pit, tempi di settore, l'intero blocco dati di ogni slot di pilota (classe, modello, squadra, tempi di settore, distacchi, penalità, gomme)
- `used` è vero per una pagina letta in righe; falso per una pagina nei menu, in pausa, in un replay, di un altro layout o presa mentre viene scritta (`torn` 1); `unchanged_reads` in meta.json conta le letture identiche byte per byte alla copia conservata prima

**Non disponibile**

- gli input e la fisica degli altri piloti: la pagina dà solo quelli del giocatore
- i tempi sul giro esatti delle altre auto: uno slot ha solo il tempo del giro in corso, quindi un giro è l'ultimo tempo in corso visto (con una precisione di circa 0,1 s)
- i campi propri del giocatore su un layout diverso dalla 3.6: conservati grezzi, non letti, finché non vengono verificati

**Dimensione**: la pagina pesa 44 KB (r3e.h 3.6; la mappatura è arrotondata a pagine intere da 4 KB), fino a 10 volte al secondo mentre si guida: circa 1,6 GB all'ora prima della compressione; gli slot dei piloti vuoti e i campi che non cambiano si comprimono molto bene con zstd (non ancora misurato su una sessione reale)

## Verificato {#verified}

testato su una pagina costruita nel test da r3e.h 3.6 (offset ricavati dall'intestazione ufficiale); non ancora testato con il gioco; i tempi sul giro delle altre auto sono l'ultimo tempo del giro in corso visto (con una precisione di circa 0,1 s)

## Fonte {#source}

[heat3d_watch/adapters/simracing_shm.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/simracing_shm.py)

<!-- Generato dall'adattatore da tools/gen_game_pages.py; per cambiarlo modifica l'adattatore ed eseguilo di nuovo invece di modificare questa pagina. -->
