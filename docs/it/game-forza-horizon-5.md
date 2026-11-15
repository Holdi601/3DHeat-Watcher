---
title: "Forza Horizon 5 (dati in tempo reale)"
nav_order: 22
lang: "it"
source: game-forza-horizon-5.md
source_hash: "0083724478e7"
nav_exclude: true
search_exclude: true
---
# Forza Horizon 5 (dati in tempo reale) {#forza-horizon-5-live-data}

Mentre giochi a Forza Horizon 5, il watcher salva i dati che il gioco stesso invia, così puoi guardarli più tardi su una mappa nel visualizzatore 3DHeat.

*Dettagli tecnici: adattatore `forza-horizon-5`, tipo [`telemetry`](sources-and-rules.md); gira mentre `ForzaHorizon5.exe` è in esecuzione e cerca nuovi dati ogni 0,1 s.*

## Cosa viene registrato {#what-is-recorded}

- posizione della tua auto (XYZ nel mondo, m) a 10 Hz, con velocità, marcia, acceleratore, freno, giro
- inizio e fine della guida (session_start/session_end), giri con il tempo sul giro del gioco
- inizio e arrivo della gara con la posizione in gara
- teletrasporti (riavvolgimento, viaggio rapido): `teleport` dove si trovava l'auto, `spawn` dove si trova ora
- giri, miglior giro, distanza, velocità massima, gare

## Da dove arriva {#where-it-comes-from}

Forza Data Out, UDP 127.0.0.1:5300 (formato Dash); ogni pacchetto inoltrato invariato a 127.0.0.1:5301

## Come attivarlo {#how-to-switch-it-on}

Nel gioco: Impostazioni > HUD e Gioco > Data Out Attivo, IP 127.0.0.1, porta 5300 (Motorsport: formato Dash). FH Companion o un'altra app Data Out: imposta la sua porta su 5301, il watcher inoltra ogni pacchetto; mentre un'altra app ascolta sulla 5300, il watcher lascia la porta a lei e non registra nulla

## Come funziona {#how-it-works}

La telemetria dei giochi di corsa: Forza, i giochi Assetto Corsa, i giochi di rally
e BeamNG, registrati come percorsi, giri e tappe.

Ogni gioco qui pubblica la sua telemetria apposta, per cruscotti e
simulatori di movimento; niente viene iniettato e non si legge nulla che il gioco non
renda disponibile. La decodifica non è scritta due volte: sono i registratori di giri di
gamecapture in
`heat3d_capture/telemetry` di 3DHeat GameCapture, copiati in `heat3d_watch/decoders` (testati lì con pacchetti costruiti
dai layout pubblicati). Questo modulo trasforma i loro fotogrammi nelle righe del
watcher: la posizione dell'auto alcune volte al secondo con velocità, marcia e pedali,
un evento per ogni giro o tappa, e i numeri che un pilota tiene d'occhio: giri, miglior giro,
distanza, velocità massima.

#### Forza (Horizon 4/5/6, Motorsport) {#forza-horizon-456-motorsport}

UDP "Data Out", attivato nelle impostazioni HUD e Gioco del gioco, verso
127.0.0.1 porta 5300, formato Dash. Un pacchetto per ogni tick della simulazione; l'offset del blocco dash
viene ricavato dai pacchetti (`forza.detect_layout`). Metri del mondo, Y in alto; il mondo è
mancino e viene disegnato così come inviato, come fa il registratore dei giri
(documentazione "Data Out" di Forza Motorsport e Forza Horizon).
Il gioco invia a una sola porta, e FH Companion e le altre app Data Out ascoltano
sulla stessa. Due programmi non possono condividerla: su Windows il socket legato
a 127.0.0.1 riceve i pacchetti, e uno legato a tutti gli indirizzi sulla stessa
porta non ne riceve nessuno, qualunque sia partito per primo. Quindi il watcher aspetta un po'
dopo l'avvio del gioco prima di prendere la porta, non la toglie mai a un'app che la
tiene e la lascia non appena un'altra app inizia ad ascoltare lì.
Mentre tiene la porta, inoltra ogni pacchetto invariato a
127.0.0.1:5301: imposta la casella della porta di FH Companion (la sua scheda telemetria) su 5301 e
registrano entrambi.

#### Tutto ciò che viene conservato {#everything-kept}

Le righe sono poche al secondo; i giochi ne inviano molte di più. Ogni pacchetto UDP
che arriva (nei menu, tra un giro e l'altro, quelli che nessun decodificatore legge) viene conservato intero
in `heat.raw.parquet` della sessione, sotto il suo formato (`dash-horizon`,
`session_update`, `extradata3`, `H3D1`, ...), e ogni pagina di memoria condivisa
(l'intera mappatura, non solo i byte decodificati) ogni volta che cambia, sotto
il nome della sua mappatura (`acpmf_physics`, ...). `used` segna ciò che è diventato anche
righe; `selfCheck.completeness` in `meta.json` conta ogni tipo (regola del convertitore di 3DHeat).

Lo stesso modulo serve anche: [Assetto Corsa (dati in tempo reale)](game-assetto-corsa.md), [Assetto Corsa Competizione (dati in tempo reale)](game-assetto-corsa-competizione.md), [Assetto Corsa EVO (dati in tempo reale)](game-assetto-corsa-evo.md), [Assetto Corsa Rally (dati in tempo reale)](game-assetto-corsa-rally.md), [BeamNG.drive (dati in tempo reale)](game-beamng.md), [DiRT Rally 2.0 (dati in tempo reale)](game-dirt-rally-2.md), [EA SPORTS WRC (dati in tempo reale)](game-ea-wrc.md), [Forza Horizon 4 (dati in tempo reale)](game-forza-horizon-4.md), [Forza Horizon 6 (dati in tempo reale)](game-forza-horizon-6.md), [Forza Motorsport (dati in tempo reale)](game-forza-motorsport.md), [Richard Burns Rally (dati in tempo reale)](game-richard-burns-rally.md).

## Posizioni e assi {#positions-and-axes}

| | |
|---|---|
| Posizioni registrate | sì |
| Asse verticale | `y` |
| Unità | metri; il mondo di Forza è mancino, disegnato così come inviato, come fa il registratore dei giri |
| Specchiato per il visualizzatore | nessuno |
| Scala delle unità (`scale`: il visualizzatore moltiplica le posizioni per questo valore) | 1 |

Questi valori finiscono in `meta.json` di ogni sessione (`axes`) e, quando la sessione ha posizioni, nel footer di `heat.parquet`, così il visualizzatore 3DHeat ruota e scala le righe da solo: vedi [I dati](the-data.md).

## Multigiocatore {#multiplayer}

- Segnato come giocato online (`multiplayer`): **sì**. `games --markdown` lo mostra come "consentito (legge solo ciò che il gioco pubblica)".
- Tipo `telemetry`: legge solo ciò che il gioco o la piattaforma rende disponibile (una porta UDP o la memoria condivisa che il gioco pubblica), quindi registra anche nel gioco online oltre che offline; il contrassegno decide solo se la memoria può mai essere letta.
- Memoria: **mai** letta da questo adattatore. Solo gli adattatori `memory` leggono la memoria, e mai per un gioco segnato come giocato online: vedi [Fonti e regole](sources-and-rules.md).

## Statistiche registrate {#statistics-recorded}

Chiavi statistiche che il codice di questo adattatore imposta per nome (`stats` di ogni sessione in `meta.json` e la tabella `stats` di `watcher.sqlite`):

`best_lap`, `distance_km`, `laps`, `races`, `top_speed_kmh`

Una chiave tra parentesi graffe viene completata durante l'esecuzione (`score.{team}` è una chiave per ogni squadra). Le chiavi che il codice prende da una tabella dei campi del gioco o dai nomi statistici del gioco non sono in questo elenco; "Cosa viene registrato" sopra le nomina.

## Completezza {#completeness}

Il watcher segue la [regola del convertitore](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md) di 3DHeat: ciò che la sorgente contiene viene letto o conservato, mai scartato. Oltre alle righe, ogni pacchetto, pagina, riga o risposta che l'adattatore riceve viene conservato intero in `heat.raw.parquet` della sessione (colonne `time`, `ms`, `type`, `used`, `payload`, `text`, poi ogni campo conservato per nome; `used` segna ciò che è diventato anche riga), e `selfCheck.completeness` in `meta.json` conta ogni `type`: `lost` è 0.

**Letto**

- righe a 10 Hz: posizione, velocità, marcia, acceleratore, freno, giro, imbardata/beccheggio/rollio (rad), giri motore, sterzo (-1..1); session_start con l'ordinale, la classe, il PI e la trasmissione dell'auto; giri con il tempo sul giro del gioco; posizione in gara

**Conservato grezzo**

- ogni pacchetto che raggiunge la porta, intero, alla frequenza del gioco (uno per tick della simulazione), sotto il suo formato: `dash-horizon` (324 byte, Forza Horizon), `dash` (311, Motorsport 7), `dash-fm2023` (331, Forza Motorsport 2023: usura degli pneumatici e id della pista), `sled` (232, senza posizione), `<n>-byte` per tutto il resto, inclusi i pacchetti dei menu (isRaceOn 0), i pacchetti trattenuti finché il layout dash non è confermato e i circa 13 byte del pacchetto Horizon che nessun layout pubblicato nomina
- il blocco Sled con ogni canale per ruota (rapporto di slittamento, angolo di slittamento, slittamento combinato, sospensione, velocità della ruota, vibrazione, pozzanghere), accelerazioni, velocità angolare, potenza, coppia, boost, carburante, temperature degli pneumatici, frizione, freno a mano, linea di guida, differenza di frenata dell'IA: tutto nei pacchetti, decodificato da `decoders/fulllap.decode_full` a partire da essi

**Non disponibile**

- altre auto: Data Out descrive solo l'auto del giocatore
- il nome della pista o del percorso: Forza Horizon non ne invia mai uno; Motorsport 2023 invia solo un numero di pista
- pacchetti mentre un'altra app (FH Companion) tiene la porta UDP 5300: il watcher lascia la porta a lei

**Dimensione**: circa 85 MB all'ora prima della compressione (60 pacchetti al secondo di 324 byte più un'intestazione di 70 byte per elemento); i pacchetti consecutivi differiscono poco, quindi zstd ne mantiene una frazione

## Verificato {#verified}

decodifica del registratore di giri di gamecapture (testata su pacchetti costruiti dal layout Data Out); l'adattatore testato su pacchetti sintetici e su traiettorie di giri registrate riprodotte come pacchetti; non ancora testato con il gioco

## Sorgente {#source}

[heat3d_watch/adapters/racing.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/racing.py)

<!-- Generated from the adattatore by tools/gen_game_pages.py; change the adattatore and run it again rather than editing this page. -->
