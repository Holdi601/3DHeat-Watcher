---
title: "Microsoft Flight Simulator 2024 (dati in tempo reale)"
nav_order: 32
lang: "it"
source: game-msfs2024.md
source_hash: "011c18a23252"
nav_exclude: true
search_exclude: true
---
# Microsoft Flight Simulator 2024 (dati in tempo reale) {#microsoft-flight-simulator-2024-live-data}

Mentre giochi a Microsoft Flight Simulator 2024, il watcher salva i dati che il gioco stesso invia all'esterno, così puoi guardarli più tardi su una mappa nel visualizzatore di 3DHeat.

*Dettagli tecnici: adattatore `msfs2024`, tipo [`telemetry`](sources-and-rules.md); gira mentre `FlightSimulator2024.exe` è in esecuzione e cerca nuovi dati ogni 0,1 s.*

## Cosa viene registrato {#what-is-recorded}

- la posizione del proprio velivolo a ogni frame del simulatore, campionata a 10 Hz (latitudine/longitudine/altitudine come metri est/alto/nord rispetto al primo punto; lat/lon/alt conservate come colonne)
- assetto, velocità indicata, velocità al suolo, AGL, g, a terra o no; velocità vera, Mach, velocità verticale, AoA, angolo di derapata, prua magnetica, velocità sugli assi del corpo, accelerazioni e velocità di rotazione a circa 10 Hz
- peso, carburante, flap, carrello, spoiler, freno di stazionamento, pilota automatico, manetta, giri, meteo, velocità della simulazione, ora e stato della camera una volta al secondo; il titolo del velivolo, il tipo ATC, il modello e l'id
- decolli, atterraggi, schianti, voli iniziati e terminati (session_start/session_end)
- tempo di volo, tempo in aria, distanza, altezza massima, g massimo, atterraggi
- ogni messaggio SimConnect conservato intero in heat.raw.parquet

## Da dove arriva {#where-it-comes-from}

SimConnect tramite il SimConnect.dll del giocatore (la cartella del simulatore, oppure %MSFS2024_SDK%\SimConnect SDK\lib)

## Come attivarlo {#how-to-switch-it-on}

nulla nel simulatore; serve SimConnect.dll - MSFS 2020 ce l'ha nella sua cartella, i giocatori di MSFS 2024 installano l'SDK di MSFS 2024

## Come funziona {#how-it-works}

Microsoft Flight Simulator 2020 e 2024: SimConnect, tramite il SimConnect.dll del giocatore.

SimConnect è l'API client pubblicata del simulatore (documentazione dell'SDK:
<https://docs.flightsimulator.com/html/Programming_Tools/SimConnect/SimConnect_SDK.htm>,
<https://docs.flightsimulator.com/msfs2024/html/6_Programming_APIs/SimConnect/SimConnect_SDK.htm>).
Il watcher non include la DLL: carica quella che arriva con il simulatore o con il suo SDK - MSFS 2020 mette `SimConnect.dll` nella sua cartella di installazione; MSFS 2024 su Steam fornisce solo la sua versione interna, quindi i giocatori del 2024 installano l'SDK di MSFS 2024 (`<SDK>\SimConnect SDK\lib\SimConnect.dll`; il simulatore 2024 accetta anche i client del 2020).

Le chiamate, da SimConnect.h, restituiscono tutte un HRESULT (0 = S_OK):

```text
SimConnect_Open(HANDLE*, LPCSTR name, HWND, DWORD, HANDLE, DWORD config)
SimConnect_AddToDataDefinition(HANDLE, DWORD define, LPCSTR var, LPCSTR units,
                               SIMCONNECT_DATATYPE (FLOAT64 = 4), float epsilon, DWORD datum)
SimConnect_RequestDataOnSimObject(HANDLE, DWORD request, DWORD define, DWORD object (0 = user),
                                  SIMCONNECT_PERIOD (SIM_FRAME = 3), DWORD flags, DWORD origin,
                                  DWORD interval, DWORD limit)
SimConnect_SubscribeToSystemEvent(HANDLE, DWORD event, LPCSTR name)
SimConnect_GetNextDispatch(HANDLE, SIMCONNECT_RECV**, DWORD*)   E_FAIL quando non c'è nulla in attesa
SimConnect_Close(HANDLE)
```

Ogni messaggio inizia con SIMCONNECT_RECV {DWORD dwSize, dwVersion, dwID}
(#pragma pack 1). Quelli letti qui:

```text
1  EXCEPTION       dwException, dwSendID, dwIndex
2  OPEN            szApplicationName[256], poi i DWORD di versione
3  QUIT            il simulatore si sta chiudendo
4  EVENT           uGroupID, uEventID, dwData
6  EVENT_FILENAME  EVENT + szFileName[260], dwFlags        (FlightLoaded)
8  SIMOBJECT_DATA  dwRequestID, dwObjectID, dwDefineID, dwFlags, dwentrynumber,
                   dwoutof, dwDefineCount, poi i valori (FLOAT64 ciascuno qui)
```

Variabili di simulazione (unità richieste così che non serva alcuna conversione): PLANE
LATITUDE/LONGITUDE (gradi), PLANE ALTITUDE (metri, sul livello del mare), PLANE ALT ABOVE GROUND (metri),
PLANE PITCH/BANK DEGREES e PLANE HEADING DEGREES TRUE (gradi; i segni sono quelli di SimConnect - muso in su
significa beccheggio negativo), AIRSPEED INDICATED e GROUND VELOCITY (nodi), G FORCE (gforce), SIM ON GROUND (booleano).
Eventi di sistema: SimStart, SimStop, Crashed, FlightLoaded, AircraftLoaded,
Pause, CrashReset, PositionChanged, FlightSaved, Sim.

Altre tre definizioni di dati chiedono il resto del volo (`MOTION_VARS`,
ogni sesto frame del simulatore), lo stato più lento del velivolo (`STATE_VARS`, una volta al
secondo) e i suoi nomi (`NAME_VARS`, stringhe di 256 byte, quando cambiano); ognuna è una definizione
a sé, quindi una variabile che una versione del simulatore non conosce costa solo quel blocco. Ogni messaggio viene conservato intero nel file accessorio grezzo della sessione.

Le posizioni vanno nella stessa mappa piatta di X-Plane (x est, y altitudine, z nord, in metri dal primo punto della sessione); quel punto è il `geo` della sessione, in meta.json e nel footer della tabella.

Lo stesso modulo serve anche: [Microsoft Flight Simulator 2020 (dati in tempo reale)](game-msfs2020.md).

## Posizioni e assi {#positions-and-axes}

| | |
|---|---|
| Posizioni registrate | sì |
| Asse verso l'alto | `y` |
| Unità | metri (est, altitudine, nord dal primo punto) |
| Specchiato per il visualizzatore | `z` |
| Scala delle unità (`scale`: il visualizzatore moltiplica le posizioni per questo valore) | 1 |

Questi valori finiscono in `meta.json` (`axes`) di ogni sessione e, quando la sessione ha delle posizioni, nel footer di `heat.parquet`, così il visualizzatore di 3DHeat ruota e scala le righe da solo - vedi [I dati](the-data.md).

## Multigiocatore {#multiplayer}

- Segnato come giocato online (`multiplayer`): **sì**. `games --markdown` lo mostra come "consentito (legge solo ciò che il gioco pubblica)".
- Tipo `telemetry`: legge solo ciò che il gioco o la piattaforma consegna (una porta UDP o una memoria condivisa che il gioco pubblica), quindi registra anche nel gioco online oltre che offline; il flag decide solo se la memoria può mai essere letta.
- Memoria: **mai** letta da questo adattatore. Solo gli adattatori `memory` leggono la memoria, e mai per un gioco segnato come giocato online - vedi [Fonti e regole](sources-and-rules.md).

## Statistiche registrate {#statistics-recorded}

Chiavi statistiche che il codice di questo adattatore imposta per nome (`stats` di ogni sessione in `meta.json` e la tabella `stats` di `watcher.sqlite`):

`airborne_time`, `bad_packets`, `crashes`, `distance_km`, `flight_time`, `max_altitude_m`, `max_g`, `{event}s`

Una chiave tra parentesi graffe viene completata durante l'esecuzione (`score.{team}` è una chiave per squadra). Le chiavi che il codice prende da una tabella dei campi del gioco o dai nomi statistici del gioco non sono in questo elenco; "Cosa viene registrato" qui sopra le nomina.

## Completezza {#completeness}

Il watcher segue la [regola del convertitore](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md) di 3DHeat: ciò che la fonte contiene viene letto o conservato, mai scartato. Oltre alle righe, ogni pacchetto, pagina, riga o risposta che l'adattatore riceve viene conservato intero in `heat.raw.parquet` della sessione (colonne `time`, `ms`, `type`, `used`, `payload`, `text`, poi ogni campo conservato per nome; `used` segna ciò che è diventato anche righe), e `selfCheck.completeness` in `meta.json` conta ogni `type` - `lost` è 0.

**Letto**

- SIMOBJECT_DATA della definizione di posizione (ogni frame del simulatore): latitudine, longitudine, altitudine, AGL, beccheggio, rollio, prua vera, IAS, velocità al suolo, g, a terra - l'ultimo frame del campionamento come riga, ogni frame per i contatti al suolo e i decolli
- SIMOBJECT_DATA della definizione del moto (circa 10 Hz: TAS, Mach, velocità verticale, AoA, angolo di derapata, prua magnetica, velocità sul corpo, accelerazione e velocità di rotazione su tre assi) e della definizione di stato (1 Hz: pesi, carburante, flap, carrello, spoiler, freno di stazionamento, pilota automatico, motori, manetta e giri, temperatura esterna, vento, pressione al livello del mare, velocità della simulazione, ora zulu e locale, stato della camera) sulle righe così come ricevuti l'ultima volta
- SIMOBJECT_DATA della definizione dei nomi (titolo, tipo ATC, modello e id) in meta.json e nella colonna `aircraft` delle righe; OPEN (applicazione e versione) in meta.json
- EVENT e EVENT_FILENAME: SimStart, SimStop, Crashed, FlightLoaded (il file di volo) e AircraftLoaded (il file del velivolo) come voli, schianti e meta.json
- QUIT termina la sessione

**Conservato grezzo**

- ogni messaggio che SimConnect invia al watcher, intero come `payload`, sotto il nome del suo SIMCONNECT_RECV_ID: `SIMOBJECT_DATA`, `EVENT`, `EVENT_FILENAME`, `OPEN`, `QUIT`, `EXCEPTION` (una variabile o un evento che il simulatore non ha accettato, con l'id di invio e l'indice), qualsiasi altro id con il suo nome o `RECV_<id>`
- ciò che solo il file accessorio grezzo contiene: la posizione di ogni frame del simulatore tra una riga e l'altra, gli eventi Pause, Sim, CrashReset, PositionChanged e FlightSaved, una definizione che il simulatore ha accorciato (una variabile che non conosceva: il blocco allora non viene letto per nome); `requests` in meta.json elenca ogni variabile e unità di ogni definizione, in ordine, così i payload si leggono anche senza questo modulo

**Non disponibile**

- altri velivoli (traffico IA, altri giocatori online): SimConnect_RequestDataOnSimObjectType interrogherebbe ogni velivolo in un raggio - più carico per il simulatore, e voli di altri giocatori
- il blocco del moto a ogni frame del simulatore: viene richiesto ogni sesto frame (circa 10 Hz, la frequenza delle righe), il che tiene il flusso grezzo a circa un quinto della dimensione; il blocco di posizione resta a ogni frame
- le migliaia di altre variabili del simulatore (radio, luci, strumenti di ogni motore, guasti): una definizione contiene ciò che chiede; le liste chiedono il volo, lo stato del velivolo e l'ora della simulazione
- osservazioni meteo, strutture (aeroporti, VOR), dati client dei componenti aggiuntivi: richieste separate, non fatte

**Dimensione**: circa 30-55 MB all'ora prima di zstd: il blocco di posizione a ogni frame del simulatore (circa 200 byte con il suo frame, 30-60 al secondo), il blocco del moto a circa 10 Hz (circa 240 byte), il blocco di stato una volta al secondo; zstd riduce i double di diverse volte

## Verificato {#verified}

decodifica dei messaggi testata su buffer costruiti dai layout di SimConnect.h; la connessione SimConnect dal vivo non è testata

## Sorgente {#source}

[heat3d_watch/adapters/msfs.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/msfs.py)

<!-- Generated from the adattatore by tools/gen_game_pages.py; change the adattatore and run it again rather than editing this page. -->
