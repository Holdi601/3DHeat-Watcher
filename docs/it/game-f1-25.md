---
title: "EA SPORTS F1 25 (dati in tempo reale)"
nav_order: 16
lang: "it"
source: game-f1-25.md
source_hash: "7476dbb3b308"
nav_exclude: true
search_exclude: true
---
# EA SPORTS F1 25 (dati in tempo reale) {#ea-sports-f1-25-live-data}

Mentre giochi a EA SPORTS F1 25, il watcher salva i dati che il gioco stesso invia all'esterno, così puoi guardarli più tardi su una mappa nel visualizzatore di 3DHeat.

*Dettagli tecnici: adattatore `f1-25`, tipo [`telemetry`](sources-and-rules.md); gira mentre `F1_25.exe` è in esecuzione e cerca nuovi dati ogni 0,1 s.*

## Cosa viene registrato {#what-is-recorded}

- la posizione di ogni auto (XYZ nel mondo, m) a 10 Hz, per nome del pilota, squadra, con l'auto del giocatore segnata (`own_car` 1, dall'indice dell'auto del giocatore), con velocità, marcia, acceleratore, freno, sterzo, giri, DRS, imbardata, beccheggio, rollio (gradi) e forze g
- giri per auto con il tempo sul giro e la posizione in gara; arrivi e ritiri
- gli eventi di gara del gioco: inizio e fine sessione, giro veloce, penalità, sorpassi, collisioni, safety car, bandiera rossa, semafori di partenza, bandiera a scacchi, vincitore, flashback (`teleport` dove si trovava l'auto, `spawn` dove è tornata)
- tracciato, tipo di sessione, giri e piloti di ogni sessione
- i propri giri, il giro migliore, posizione in gara e in griglia, pit stop, penalità, sorpassi, collisioni, distanza, velocità massima
- ogni pacchetto inviato dal gioco, intero, in `heat.raw.parquet` - anche quelli non letti nelle righe

## Da dove arriva {#where-it-comes-from}

telemetria UDP 127.0.0.1:20777 (Documents\My Games\F1 25\hardwaresettings\hardware_settings_config.xml)

## Come attivarlo {#how-to-switch-it-on}

Nel gioco: Impostazioni > Impostazioni telemetria > UDP Telemetry attivo, IP 127.0.0.1, porta 20777 - oppure `python -m heat3d_watch setup f1-25 --apply` (modifica hardware_settings_config.xml, con backup prima; il gioco deve essere chiuso). Mentre un'altra app usa la 20777, il watcher lascia la porta a quell'app

Scrivi il comando in un terminale aperto nella cartella del watcher (vedi [Prima di iniziare](before-you-start.md)). Se fallisce, l'ultima riga dice il motivo; [Installazione e avvio](installing-and-running.md) descrive le cause più comuni.

`python -m heat3d_watch setup f1-25` elenca i file che verrebbero modificati; `python -m heat3d_watch setup f1-25 --apply` li modifica, tenendo l'originale come `<file>.heat3d-backup` (vedi [Comandi](commands.md#setup)). Stampa `f1-25: changed: ...` per ogni modifica, oppure `f1-25: nothing to change` quando è già attivo.

## Come funziona {#how-it-works}

EA SPORTS F1 23, F1 24 e F1 25: la telemetria UDP ufficiale, ogni auto in pista.

Il gioco la invia da solo (Impostazioni > Impostazioni telemetria, oppure
`Documents/My Games/<F1 xx>/hardwaresettings/hardware_settings_config.xml`,
`<udp enabled="true" ip="127.0.0.1" port="20777" sendRate="20" format="2025" ...>`).
Little-endian, compatto, un'intestazione di 29 byte in ogni pacchetto (uguale nei formati 2023,
2024 e 2025):

```text
uint16 packetFormat, uint8 gameYear, gameMajorVersion, gameMinorVersion,
packetVersion, packetId, uint64 sessionUID, float sessionTime,
uint32 frameIdentifier, overallFrameIdentifier, uint8 playerCarIndex,
secondaryPlayerCarIndex
```

Cosa viene letto, per id di pacchetto:

```text
0 Motion        CarMotionData[22], 60 byte ciascuno: posizione nel mondo x y z
                (metri; Y verso l'alto), velocità nel mondo, vettori avanti e
                destra (int16 / 32767), forze g, imbardata beccheggio rollio
1 Session       meteo, temperature, giri totali, lunghezza del tracciato, tipo di
                sessione, id del tracciato, ... partita in rete
2 Lap Data      LapData[22]: tempo dell'ultimo giro, distanza percorsa nel giro,
                posizione in gara, numero del giro attuale, pit stop, penalità,
                posizione in griglia, stato di pilota e risultato. 50 byte per auto nel
                2023; 57 nel 2024 e nel 2025, che hanno aggiunto le parti in minuti dei
                delta e la trappola di velocità.
3 Event         un codice di quattro lettere e un'unione di dettagli: SSTA SEND FTLP
                RTMT DRSE DRSD TMPT CHQF RCWN PENA SPTP STLG LGOT DTSV SGSV
                FLBK BUTN RDFL OVTK SCAR COLL
4 Participants  ParticipantData[22]: IA o umano, pilota, squadra, numero di
                gara, nome (48 byte nel 2023 e nel 2024, 32 nel 2025; 58,
                60 e 57 byte per auto)
6 Car Telemetry CarTelemetryData[22], 60 byte: velocità km/h, acceleratore,
                sterzo, freno, frizione, marcia, giri, DRS ...
```

Ogni pacchetto viene anche conservato intero, così come è arrivato, nel file accessorio grezzo della sessione (`heat.raw.parquet`, `type` il nome del pacchetto - `motion`, `car_status` ... - con `format`, `packet_id`, `frame` e `session_uid`) - quelli letti sopra e quelli che nessuno legge ancora: 5 Car Setups, 7 Car Status, 8 Final Classification, 9 Lobby Info, 10 Car Damage, 11 Session History, 12 Tyre Sets, 13 Motion Ex, 14 Time Trial, 15 Lap Positions, qualsiasi id successivo, e i pacchetti in un formato che questo non legge. Quindi un decoder successivo ha bisogno solo del file accessorio.

La posizione di ogni auto è nel pacchetto Motion - anche online, dove il gioco la trasmette lui stesso (solo i dati di carburante, ERS, danni e set di gomme sono trattenuti per i giocatori con "Your Telemetry" limitata). Ogni auto viene registrata a circa 10 Hz con il nome del partecipante ("car N" finché non arrivano i nomi), la squadra per nome, e l'auto del giocatore segnata come `own`.

Fonti: "F1 25 UDP Specification" di EA (forums.ea.com, sezione informativa dei giochi F1), le specifiche di F1 23 e F1 24; le stesse tabelle riprese in MacManley/f1-25-udp (MIT). I pacchetti nei test sono costruiti da questi layout.

Lo stesso modulo serve anche: [EA SPORTS F1 23 (dati in tempo reale)](game-f1-23.md), [EA SPORTS F1 24 (dati in tempo reale)](game-f1-24.md).

## Posizioni e assi {#positions-and-axes}

| | |
|---|---|
| Posizioni registrate | sì |
| Asse verso l'alto | `y` |
| Unità | metri |
| Specchiato per il visualizzatore | nessuno |
| Scala delle unità (`scale`: il visualizzatore moltiplica le posizioni per questo valore) | 1 |

Questi valori finiscono in `meta.json` (`axes`) di ogni sessione e, quando la sessione ha delle posizioni, nel footer di `heat.parquet`, così il visualizzatore di 3DHeat ruota e scala le righe da solo - vedi [I dati](the-data.md).

## Multigiocatore {#multiplayer}

- Segnato come giocato online (`multiplayer`): **sì**. `games --markdown` lo mostra come "consentito (legge solo ciò che il gioco pubblica)".
- Tipo `telemetry`: legge solo ciò che il gioco o la piattaforma consegna (una porta UDP o una memoria condivisa che il gioco pubblica), quindi registra anche nel gioco online oltre che offline; il flag decide solo se la memoria può mai essere letta.
- Memoria: **mai** letta da questo adattatore. Solo gli adattatori `memory` leggono la memoria, e mai per un gioco segnato come giocato online - vedi [Fonti e regole](sources-and-rules.md).

## Statistiche registrate {#statistics-recorded}

Chiavi statistiche che il codice di questo adattatore imposta per nome (`stats` di ogni sessione in `meta.json` e la tabella `stats` di `watcher.sqlite`):

`best_lap`, `collisions`, `distance_km`, `fastest_laps`, `finishes`, `flashbacks`, `grid_position`, `laps`, `overtaken`, `overtakes`, `penalties`, `penalty_seconds`, `pit_stops`, `race_position`, `sessions`, `top_speed_kmh`, `wins`

Una chiave tra parentesi graffe viene completata durante l'esecuzione (`score.{team}` è una chiave per squadra). Le chiavi che il codice prende da una tabella dei campi del gioco o dai nomi statistici del gioco non sono in questo elenco; "Cosa viene registrato" qui sopra le nomina.

## Completezza {#completeness}

Il watcher segue la [regola del convertitore](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md) di 3DHeat: ciò che la fonte contiene viene letto o conservato, mai scartato. Oltre alle righe, ogni pacchetto, pagina, riga o risposta che l'adattatore riceve viene conservato intero in `heat.raw.parquet` della sessione (colonne `time`, `ms`, `type`, `used`, `payload`, `text`, poi ogni campo conservato per nome; `used` segna ciò che è diventato anche righe), e `selfCheck.completeness` in `meta.json` conta ogni `type` - `lost` è 0.

**Letto**

- 0 Motion: posizione e velocità nel mondo di ogni auto, e ora anche imbardata, beccheggio, rollio (gradi, dai radianti della specifica) e le forze g laterale, longitudinale e verticale, su ogni riga di posizione dell'auto
- 1 Session: tracciato, tipo di sessione, giri totali, lunghezza del tracciato, online o no (`sessions` in meta.json)
- 2 Lap Data: tempo dell'ultimo giro, numero del giro, posizione in gara e in griglia, pit stop, penalità, stato del risultato (giri, arrivi, ritiri, statistiche)
- 3 Event: ogni codice tranne BUTN come riga propria, con i suoi dettagli
- 4 Participants: nomi dei piloti, squadre, numero di auto attive (`player` e `team` delle righe, `drivers` in meta.json)
- 6 Car Telemetry: velocità, marcia, acceleratore, freno, e ora anche sterzo (-1..1), giri e DRS, su ogni riga di posizione dell'auto
- verificato con le specifiche UDP pubblicate da EA per i formati 2023, 2024 e 2025 (dimensioni dei pacchetti verificate nei test); non ancora con il gioco

**Conservato grezzo**

- ogni pacchetto intero in `heat.raw.parquet`, `payload` il datagramma, `type` il nome del suo id: `motion`, `session`, `lap_data`, `event`, `participants`, `car_setups`, `car_telemetry`, `car_status`, `final_classification`, `lobby_info`, `car_damage`, `session_history`, `tyre_sets`, `motion_ex`, `time_trial`, `lap_positions` (`packet <n>` per un id che le specifiche non elencano ancora); colonne `format` (2023/2024/2025), `packet_id`, `frame`, `session_uid`
- `used` è vero per i pacchetti letti sopra (Motion, Session, Lap Data, Participants, Car Telemetry, e i codici Event diversi da BUTN); gli altri - setup delle auto, stato dell'auto (carburante, ERS, mescola e età delle gomme, flag), classifica finale, lobby, danni alle auto, storico della sessione (ogni tempo di giro e di settore per auto), set di gomme, motion ex (sospensione, velocità delle ruote, velocità locale, velocità angolare e accelerazione dell'auto del giocatore), time trial, posizioni nei giri, eventi dei pulsanti BUTN - sono conservati per un decoder successivo
- `format <year>`: un pacchetto in un formato precedente al 2023 (un'altra intestazione), intero; `short`: un datagramma più corto dell'intestazione di 29 byte, intero

**Non disponibile**

- carburante, ERS, danni e set di gomme degli altri piloti online, quando la loro "Your Telemetry" è limitata: il gioco invia zeri per loro
- pacchetti inviati mentre il watcher non è in esecuzione, o mentre un'altra app usa la porta 20777: l'UDP non viene memorizzato dal gioco

**Dimensione**: con una frequenza di invio di 60 Hz ogni pacchetto occupa circa 0,38 MB/s (Motion, Lap Data, Car Telemetry, Car Status e Motion Ex a 60 Hz, Session History e Tyre Sets 20 al secondo, Car Damage 10 al secondo, Session e Car Setups 2 al secondo) più circa 0,03 MB/s di intestazioni: circa 1,5 GB all'ora di guida prima della compressione, circa 0,55 GB con i 20 Hz predefiniti; zstd lo riduce a una frazione (gli slot delle auto vuoti e i valori ripetuti si comprimono bene; non ancora misurato su una sessione reale)

## Verificato {#verified}

testato su pacchetti nei formati 2023, 2024 e 2025 costruiti dalla specifica UDP pubblicata da EA, inviati via UDP; non ancora testato con il gioco

## Sorgente {#source}

[heat3d_watch/adapters/f1.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/f1.py)

<!-- Generated from the adattatore by tools/gen_game_pages.py; change the adattatore and run it again rather than editing this page. -->
