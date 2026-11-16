---
title: "Assetto Corsa EVO (dati in tempo reale)"
nav_order: 4
lang: "it"
source: game-assetto-corsa-evo.md
source_hash: "b14d46c10e85"
nav_exclude: true
search_exclude: true
---
# Assetto Corsa EVO (dati in tempo reale) {#assetto-corsa-evo-live-data}

Mentre giochi ad Assetto Corsa EVO, il watcher salva i dati che il gioco stesso invia, così puoi guardarli più tardi su una mappa nel visualizzatore 3DHeat.

*Dettagli tecnici: adattatore `assetto-corsa-evo`, tipo [`telemetry`](sources-and-rules.md); funziona mentre `AssettoCorsaEVO.exe` è in esecuzione e cerca nuovi dati ogni 0,1 s.*

## Cosa viene registrato {#what-is-recorded}

- posizione della tua auto (XYZ nel mondo, m: media dei punti di contatto delle gomme) a 10 Hz con velocità, marcia, acceleratore, freno
- inizio e fine della sessione con la pista e l'auto che il gioco indica
- giri quando l'auto passa dove è iniziata la guida, nella stessa direzione
- teletrasporti (ritorno ai box, un riavvio): `teleport` dove si trovava l'auto, `spawn` dove si trova ora
- giri, giro migliore, distanza, velocità massima

## Da dove arriva {#where-it-comes-from}

memoria condivisa Local\acevo_pmf_physics, Local\acevo_pmf_static

## Come attivarlo {#how-to-switch-it-on}

Non serve attivare nulla: il watcher legge la fonte così come il gioco o la piattaforma la fornisce.

## Come funziona {#how-it-works}

La telemetria dei giochi di corsa: Forza, i giochi Assetto Corsa, i giochi rally
e BeamNG, registrata come percorsi, giri e tappe.

Ogni gioco qui pubblica la propria telemetria di proposito, per dashboard e
simulatori di movimento; non si inietta nulla e non si legge nulla che il gioco
non consegni. La decodifica non è scritta due volte: sono i registratori di giri
di gamecapture in `heat3d_capture/telemetry` di 3DHeat GameCapture, copiati in
`heat3d_watch/decoders` (testati lì con pacchetti costruiti dai layout pubblicati),
e questo modulo trasforma i loro fotogrammi in righe del watcher: la posizione
dell'auto alcune volte al secondo con velocità, marcia e pedali, un evento per
ogni giro o tappa, e i numeri che un pilota tiene d'occhio: giri, giro migliore,
distanza, velocità massima.

#### Forza (Horizon 4/5/6, Motorsport) {#forza-horizon-456-motorsport}

"Data Out" UDP, attivato nelle impostazioni HUD e Gioco del gioco, verso
127.0.0.1 porta 5300, formato Dash. Un pacchetto per ogni tick di simulazione; l'offset
del blocco dash si ricava dai pacchetti (`forza.detect_layout`). Metri nel mondo,
Y in alto; il mondo è mancino e viene disegnato come inviato, come fa il
registratore di giri (documentazione "Data Out" di Forza Motorsport e Forza Horizon).
Il gioco invia a una sola porta, e FH Companion e le altre app Data Out
ascoltano sulla stessa. Due programmi non possono condividerla: su Windows il socket
legato a 127.0.0.1 riceve i pacchetti e quello legato a tutti gli indirizzi sulla
stessa porta non ne riceve nessuno, chiunque sia partito per primo. Quindi il
watcher aspetta un po' dopo l'avvio del gioco prima di prendere la porta, non la
toglie mai a un'app che la tiene, e la lascia non appena un'altra app inizia ad
ascoltarla lì. Mentre la tiene, inoltra ogni pacchetto invariato a
127.0.0.1:5301 - imposta la casella porta di FH Companion (la sua scheda telemetria) su 5301
e registrano entrambi.

#### Tutto conservato {#everything-kept}

Le righe sono alcune al secondo; il gioco ne invia molte di più. Ogni pacchetto
UDP che arriva - nei menu, tra un giro e l'altro, quelli che nessun decodificatore
legge - viene conservato intero in `heat.raw.parquet` della sessione sotto il suo
formato (`dash-horizon`, `session_update`, `extradata3`, `H3D1`, ...), e ogni pagina
di memoria condivisa (l'intera mappatura, non solo i byte decodificati) ogni volta che
cambia, sotto il nome della sua mappatura (`acpmf_physics`, ...). `used` segna ciò
che è diventato anche riga; `selfCheck.completeness` in `meta.json` conta ogni tipo
(regola del convertitore di 3DHeat).

Lo stesso modulo serve anche: [Assetto Corsa (dati in tempo reale)](game-assetto-corsa.md), [Assetto Corsa Competizione (dati in tempo reale)](game-assetto-corsa-competizione.md), [Assetto Corsa Rally (dati in tempo reale)](game-assetto-corsa-rally.md), [BeamNG.drive (dati in tempo reale)](game-beamng.md), [DiRT Rally 2.0 (dati in tempo reale)](game-dirt-rally-2.md), [EA SPORTS WRC (dati in tempo reale)](game-ea-wrc.md), [Forza Horizon 4 (dati in tempo reale)](game-forza-horizon-4.md), [Forza Horizon 5 (dati in tempo reale)](game-forza-horizon-5.md), [Forza Horizon 6 (dati in tempo reale)](game-forza-horizon-6.md), [Forza Motorsport (dati in tempo reale)](game-forza-motorsport.md), [Richard Burns Rally (dati in tempo reale)](game-richard-burns-rally.md).

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

`best_lap`, `best_stage`, `distance_km`, `laps`, `race_position`, `stages`, `top_speed_kmh`

Una chiave tra parentesi graffe viene completata durante l'esecuzione (`score.{team}` è una chiave per squadra). Le chiavi che il codice prende da una tabella dei campi del gioco o dai nomi di statistica del gioco non sono in questo elenco; "Cosa viene registrato" sopra le nomina.

## Completezza {#completeness}

Il watcher segue la [regola del convertitore](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md) di 3DHeat: ciò che la fonte contiene viene letto o conservato, mai scartato. Oltre alle righe, ogni pacchetto, pagina, riga o risposta che l'adattatore riceve viene conservato intero in `heat.raw.parquet` della sessione (colonne `time`, `ms`, `type`, `used`, `payload`, `text`, poi ogni campo conservato per nome; `used` segna ciò che è diventato anche riga), e `selfCheck.completeness` in `meta.json` conta ogni `type` - `lost` è 0.

**Letto**

- righe a 10 Hz dalla pagina fisica: posizione (media dei punti di contatto delle gomme), velocità, marcia, acceleratore, freno, imbardata/beccheggio/rollio (rad), giri al minuto, sterzo (come la pagina lo riporta); inizio sessione con pista e auto dalla pagina statica; giri, posizione in gara

**Conservato grezzo**

- ogni pagina intera - l'intera regione mappata, non solo i byte decodificati - ogni volta che i suoi byte cambiano, alla lettura di 10 Hz del watcher: `acevo_pmf_physics`, `acevo_pmf_static`; una rilettura identica byte per byte all'ultima è contata in `unchanged_reads` di meta.json, non memorizzata di nuovo
- tutto ciò che viene decodificato solo per i file dei giri (`decoders/kunos.py`: per ruota scorrimento, carico, pressione, temperature, camber, sospensione, punti di contatto, temperature dei freni, rapporto e angolo di scorrimento; velocità in mondo e locali, velocità angolare, aiuti) si trova in quelle pagine

**Non disponibile**

- posizioni delle altre auto: le pagine descrivono solo l'auto del giocatore (la pagina grafica di ACC ha in alcune versioni gli id e le coordinate delle altre auto - conservati nella pagina grezza, non decodificati)
- tick di fisica tra una lettura del watcher e l'altra: il gioco riscrive la pagina alla sua frequenza di fisica (fino a 333 Hz) e il watcher legge 10 volte al secondo
- un contagiri o il tempo sul giro del gioco: le pagine di AC EVO così come vengono lette non hanno una pagina grafica; i giri sono divisi in base alla posizione

**Dimensione**: circa 150-300 MB all'ora prima della compressione (una regione di 4 KB per pagina con fino a 10 cambiamenti al secondo); le pagine sono per lo più zeri e zstd ne conserva una piccola frazione

## Verificato {#verified}

decodifica del registratore di giri di gamecapture (testato su pagine sintetiche); adattatore testato su memoria condivisa costruita nel test dal layout documentato; non ancora testato con il gioco; il nome dell'eseguibile deriva dalle segnalazioni dei giocatori

## Fonte {#source}

[heat3d_watch/adapters/racing.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/racing.py)

<!-- Generated from the adattatore by tools/gen_game_pages.py; change the adattatore and run it again rather than editing this page. -->
