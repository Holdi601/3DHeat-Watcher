---
title: "Assetto Corsa (dati in tempo reale)"
nav_order: 2
lang: "it"
source: game-assetto-corsa.md
source_hash: "9132272cc104"
nav_exclude: true
search_exclude: true
---
# Assetto Corsa (dati in tempo reale) {#assetto-corsa-live-data}

Mentre giochi ad Assetto Corsa, il watcher salva i dati che il gioco stesso invia, così puoi guardarli più tardi su una mappa nel visualizzatore 3DHeat.

*Dettagli tecnici: adattatore `assetto-corsa`, tipo [`telemetry`](sources-and-rules.md); gira mentre `acs.exe` o `acs_x86.exe` è in esecuzione e cerca nuovi dati ogni 0,1 s.*

## Cosa viene registrato {#what-is-recorded}

- posizione della tua auto (XYZ nel mondo, m: media dei punti di contatto delle gomme) a 10 Hz, con velocità, marcia, acceleratore, freno
- inizio e fine della sessione, con il tracciato e l'auto che il gioco indica
- giri, secondo il contagiri del gioco, con il suo tempo sul giro
- teletrasporti (ritorno ai box, un riavvio): `teleport` dove si trovava l'auto, `spawn` dove si trova ora
- giri, giro migliore, distanza, velocità massima

## Da dove arriva {#where-it-comes-from}

memoria condivisa Local\acpmf_physics, Local\acpmf_graphics, Local\acpmf_static

## Come attivarlo {#how-to-switch-it-on}

Non serve attivare nulla: il watcher legge la fonte così come il gioco o la piattaforma la fornisce.

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
un evento per ogni giro o tappa, e i numeri che un pilota tiene d'occhio: giri, giro migliore,
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

#### Assetto Corsa, ACC, AC EVO, AC Rally {#assetto-corsa-acc-ac-evo-ac-rally}

Memoria condivisa che il gioco scrive per le app: `Local\acpmf_physics`,
`Local\acpmf_graphics`, `Local\acpmf_static` (AC EVO: `Local\acevo_pmf_*`).
Aperta in sola lettura e solo quando il gioco l'ha creata (`simracing_shm`). La
posizione è la media dei quattro punti di contatto delle gomme, in metri del mondo, Y in alto.
Giri dal contagiri del gioco (AC, ACC) oppure passando di nuovo il punto di partenza
(AC EVO, AC Rally), come fa `kunos.py` per il registratore dei giri.

#### Tutto ciò che viene conservato {#everything-kept}

Le righe sono poche al secondo; i giochi ne inviano molte di più. Ogni pacchetto UDP
che arriva (nei menu, tra un giro e l'altro, quelli che nessun decodificatore legge) viene conservato intero
in `heat.raw.parquet` della sessione, sotto il suo formato (`dash-horizon`,
`session_update`, `extradata3`, `H3D1`, ...), e ogni pagina di memoria condivisa
(l'intera mappatura, non solo i byte decodificati) ogni volta che cambia, sotto
il nome della sua mappatura (`acpmf_physics`, ...). `used` segna ciò che è diventato anche
righe; `selfCheck.completeness` in `meta.json` conta ogni tipo (regola del convertitore di 3DHeat).

Lo stesso modulo serve anche: [Assetto Corsa Competizione (dati in tempo reale)](game-assetto-corsa-competizione.md), [Assetto Corsa EVO (dati in tempo reale)](game-assetto-corsa-evo.md), [Assetto Corsa Rally (dati in tempo reale)](game-assetto-corsa-rally.md), [BeamNG.drive (dati in tempo reale)](game-beamng.md), [DiRT Rally 2.0 (dati in tempo reale)](game-dirt-rally-2.md), [EA SPORTS WRC (dati in tempo reale)](game-ea-wrc.md), [Forza Horizon 4 (dati in tempo reale)](game-forza-horizon-4.md), [Forza Horizon 5 (dati in tempo reale)](game-forza-horizon-5.md), [Forza Horizon 6 (dati in tempo reale)](game-forza-horizon-6.md), [Forza Motorsport (dati in tempo reale)](game-forza-motorsport.md), [Richard Burns Rally (dati in tempo reale)](game-richard-burns-rally.md).

## Posizioni e assi {#positions-and-axes}

| | |
|---|---|
| Posizioni registrate | sì |
| Asse verticale | `y` |
| Unità | metri |
| Specchiato per il visualizzatore | nessuno |
| Scala delle unità (`scale`: il visualizzatore moltiplica le posizioni per questo valore) | 1 |

Questi valori finiscono in `meta.json` di ogni sessione (`axes`) e, quando la sessione ha posizioni, nel footer di `heat.parquet`, così il visualizzatore 3DHeat ruota e scala le righe da solo: vedi [I dati](the-data.md).

## Multigiocatore {#multiplayer}

- Segnato come giocato online (`multiplayer`): **sì**. `games --markdown` lo mostra come "consentito (legge solo ciò che il gioco pubblica)".
- Tipo `telemetry`: legge solo ciò che il gioco o la piattaforma rende disponibile (una porta UDP o la memoria condivisa che il gioco pubblica), quindi registra anche nel gioco online oltre che offline; il flag decide solo se la memoria può mai essere letta.
- Memoria: **mai** letta da questo adattatore. Solo gli adattatori `memory` leggono la memoria, e mai per un gioco segnato come giocato online: vedi [Fonti e regole](sources-and-rules.md).

## Statistiche registrate {#statistics-recorded}

Chiavi statistiche che il codice di questo adattatore imposta per nome (`stats` di ogni sessione in `meta.json` e la tabella `stats` di `watcher.sqlite`):

`best_lap`, `best_stage`, `distance_km`, `laps`, `race_position`, `stages`, `top_speed_kmh`

Una chiave tra parentesi graffe viene completata durante l'esecuzione (`score.{team}` è una chiave per ogni squadra). Le chiavi che il codice prende da una tabella dei campi del gioco o dai nomi statistici del gioco non sono in questo elenco; "Cosa viene registrato" sopra le nomina.

## Completezza {#completeness}

Il watcher segue la [regola del convertitore](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md) di 3DHeat: ciò che la fonte contiene viene letto o conservato, mai scartato. Oltre alle righe, ogni pacchetto, pagina, riga o risposta che l'adattatore riceve viene conservato intero in `heat.raw.parquet` della sessione (colonne `time`, `ms`, `type`, `used`, `payload`, `text`, poi ogni campo conservato per nome; `used` segna ciò che è diventato anche riga), e `selfCheck.completeness` in `meta.json` conta ogni `type`: `lost` è 0.

**Letto**

- righe a 10 Hz dalla pagina di fisica: posizione (media dei punti di contatto delle gomme), velocità, marcia, acceleratore, freno, imbardata/beccheggio/rollio (rad), giri al minuto, sterzo (come lo riporta la pagina); inizio sessione con tracciato e auto dalla pagina statica; giri, posizione in gara

**Conservato grezzo**

- ogni pagina intera (l'intera regione di memoria, non solo i byte decodificati) ogni volta che i suoi byte cambiano, alla lettura del watcher a 10 Hz: `acpmf_physics`, `acpmf_graphics`, `acpmf_static`; una rilettura identica byte per byte all'ultima viene contata in `unchanged_reads` di meta.json, non salvata di nuovo
- tutto ciò che viene decodificato solo per i file dei giri (`decoders/kunos.py`: slittamento, carico, pressione, temperature, camber, sospensioni, punti di contatto, temperature dei freni, rapporto e angolo di slittamento per ogni ruota; velocità del mondo e locale, velocità angolare, aiuti) è in quelle pagine

**Non disponibile**

- posizioni delle altre auto: le pagine descrivono solo l'auto del giocatore (la pagina grafica di ACC ha in alcune versioni gli id e le coordinate delle altre auto, conservati nella pagina grezza, non decodificati)
- i tick di fisica tra una lettura del watcher e l'altra: il gioco riscrive la pagina alla sua frequenza di fisica (fino a 333 Hz) e il watcher legge 10 volte al secondo

**Dimensione**: circa 150-300 MB all'ora prima della compressione (una regione di 4 KB per pagina fino a 10 cambiamenti al secondo); le pagine sono per lo più zeri e zstd ne mantiene una piccola frazione

## Verificato {#verified}

decodifica del registratore di giri di gamecapture (testata su pagine sintetiche); l'adattatore testato su memoria condivisa costruita nel test dal layout documentato; non ancora testato con il gioco

## Fonte {#source}

[heat3d_watch/adapters/racing.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/racing.py)

<!-- Generated from the adattatore by tools/gen_game_pages.py; change the adattatore and run it again rather than editing this page. -->
