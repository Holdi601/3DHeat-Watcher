---
title: "Richard Burns Rally (dati in tempo reale)"
nav_order: 38
lang: "it"
source: game-richard-burns-rally.md
source_hash: "4f2a2e46f8c8"
nav_exclude: true
search_exclude: true
---
# Richard Burns Rally (dati in tempo reale) {#richard-burns-rally-live-data}

Mentre giochi a Richard Burns Rally, il watcher salva i dati che il gioco stesso invia, così puoi guardarli più tardi su una mappa nel visualizzatore 3DHeat.

*Dettagli tecnici: adattatore `richard-burns-rally`, tipo [`telemetry`](sources-and-rules.md); funziona mentre `RichardBurnsRally_SSE.exe` o `RichardBurnsRally.exe` è in esecuzione e cerca nuovi dati ogni 0,1 s.*

## Cosa viene registrato {#what-is-recorded}

- posizione della tua auto (XYZ nel mondo, m) a 10 Hz con velocità, marcia, acceleratore, freno, distanza nella tappa
- inizio tappa (partenza dell'orologio di tappa), arrivo con il tempo di tappa, riavvii
- teletrasporti (un ritorno sulla strada): `teleport` dove si trovava l'auto, `spawn` dove si trova ora
- tappe, miglior tempo di tappa, distanza, velocità massima

## Da dove arriva {#where-it-comes-from}

telemetria UDP del plugin NGP, 127.0.0.1:6776 (RichardBurnsRally.ini [NGP] udpTelemetry=1)

## Come attivarlo {#how-to-switch-it-on}

RSF/NGP: in RichardBurnsRally.ini, sezione [NGP], imposta udpTelemetry=1 e l'endpoint su 127.0.0.1:6776

## Come funziona {#how-it-works}

La telemetria dei giochi di guida: Forza, i giochi Assetto Corsa, i giochi rally
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

#### EA SPORTS WRC, DiRT Rally 2.0, Richard Burns Rally {#ea-sports-wrc-dirt-rally-20-richard-burns-rally}

UDP: `Documents/My Games/WRC/telemetry/config.json` di WRC (il pacchetto `session_update`
della struttura `wrc`), `hardware_settings_config.xml` di DiRT
(`<udp enabled="true" extradata="3" port="20777">`), il plugin NGP di RBR
(`udpTelemetry=1`, porta 6776). Tappe secondo l'orologio di tappa del gioco
(`rally.StageSplitter`). RBR non documenta i suoi assi: l'asse verticale è quello lungo cui la
tappa varia meno, deciso alla chiusura della sessione.

#### Tutto conservato {#everything-kept}

Le righe sono alcune al secondo; il gioco ne invia molte di più. Ogni pacchetto
UDP che arriva - nei menu, tra un giro e l'altro, quelli che nessun decodificatore
legge - viene conservato intero in `heat.raw.parquet` della sessione sotto il suo
formato (`dash-horizon`, `session_update`, `extradata3`, `H3D1`, ...), e ogni pagina
di memoria condivisa (l'intera mappatura, non solo i byte decodificati) ogni volta che
cambia, sotto il nome della sua mappatura (`acpmf_physics`, ...). `used` segna
ciò che è diventato anche riga; `selfCheck.completeness` in `meta.json` conta ogni tipo
(regola del convertitore di 3DHeat).

Lo stesso modulo serve anche: [Assetto Corsa (dati in tempo reale)](game-assetto-corsa.md), [Assetto Corsa Competizione (dati in tempo reale)](game-assetto-corsa-competizione.md), [Assetto Corsa EVO (dati in tempo reale)](game-assetto-corsa-evo.md), [Assetto Corsa Rally (dati in tempo reale)](game-assetto-corsa-rally.md), [BeamNG.drive (dati in tempo reale)](game-beamng.md), [DiRT Rally 2.0 (dati in tempo reale)](game-dirt-rally-2.md), [EA SPORTS WRC (dati in tempo reale)](game-ea-wrc.md), [Forza Horizon 4 (dati in tempo reale)](game-forza-horizon-4.md), [Forza Horizon 5 (dati in tempo reale)](game-forza-horizon-5.md), [Forza Horizon 6 (dati in tempo reale)](game-forza-horizon-6.md), [Forza Motorsport (dati in tempo reale)](game-forza-motorsport.md).

## Posizioni e assi {#positions-and-axes}

| | |
|---|---|
| Posizioni registrate | sì |
| Asse verticale | `y` |
| Unità | metri; asse verticale deciso dalla guida (RBR non documenta i suoi assi) |
| Specchiato per il visualizzatore | nessuno |
| Scala delle unità (`scale`: il visualizzatore moltiplica le posizioni per questo valore) | 1 |

Questi valori finiscono in `meta.json` di ogni sessione (`axes`) e, quando la sessione ha posizioni, nel footer di `heat.parquet`, così il visualizzatore 3DHeat ruota e scala le righe da solo - vedi [I dati](the-data.md).

## Multigiocatore {#multiplayer}

- Segnato come giocato online (`multiplayer`): **no**. `games --markdown` lo mostra come "giocatore singolo".
- Tipo `telemetry`: legge solo ciò che il gioco o la piattaforma consegna (una porta UDP o una memoria condivisa che il gioco pubblica), quindi registra anche nel gioco online oltre che offline; il flag decide solo se la memoria può mai essere letta.
- Memoria: **mai** letta da questo adattatore. Solo gli adattatori `memory` leggono la memoria, e mai per un gioco segnato come giocato online - vedi [Fonti e regole](sources-and-rules.md).

## Statistiche registrate {#statistics-recorded}

Chiavi di statistica che il codice di questo adattatore imposta per nome (`stats` di ogni sessione in `meta.json` e la tabella `stats` di `watcher.sqlite`):

`best_lap`, `best_stage`, `distance_km`, `laps`, `stages`, `top_speed_kmh`

Una chiave tra parentesi graffe viene completata durante l'esecuzione (`score.{team}` è una chiave per squadra). Le chiavi che il codice prende da una tabella dei campi del gioco o dai nomi di statistica del gioco non sono in questo elenco; "Cosa viene registrato" sopra le nomina.

## Completezza {#completeness}

Il watcher segue la [regola del convertitore](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md) di 3DHeat: ciò che la fonte contiene viene letto o conservato, mai scartato. Oltre alle righe, ogni pacchetto, pagina, riga o risposta che l'adattatore riceve viene conservato intero in `heat.raw.parquet` della sessione (colonne `time`, `ms`, `type`, `used`, `payload`, `text`, poi ogni campo conservato per nome; `used` segna ciò che è diventato anche riga), e `selfCheck.completeness` in `meta.json` conta ogni `type` - `lost` è 0.

**Letto**

- righe a 10 Hz: posizione, velocità, marcia, acceleratore, freno, distanza nella tappa, imbardata, giri al minuto, sterzo; inizio tappa, arrivo con il tempo di tappa, riavvii

**Conservato grezzo**

- ogni pacchetto che arriva alla porta, intero, alla frequenza del gioco, sotto il suo formato: `telemetry` (TelemetryData di NGP, 664 byte), `rbr <n>-byte` per tutto il resto
- nel pacchetto oltre alle righe: assetto, le velocità e le accelerazioni dell'auto, per ruota deflessione e forza della sospensione, l'avanzamento della tappa e la distanza dalla fine; il resto dei 664 byte (blocchi di motore, gomme e freni per ruota) non è ancora decodificato da nessuna parte

**Non disponibile**

- le altre auto: i giochi inviano solo l'auto del giocatore
- l'unità di velocità e gli assi: non documentati - la velocità viene ricavata dalle posizioni, l'asse verticale dalla guida

**Dimensione**: circa 160 MB all'ora a 60 pacchetti al secondo (664 byte più un'intestazione di 70 byte per elemento); zstd ne conserva una frazione

## Verificato {#verified}

decodifica del registratore di giri di gamecapture (testato su pacchetti costruiti dai layout documentati); adattatore testato su pacchetti costruiti nel test, inviati via UDP; non ancora testato con il gioco

## Fonte {#source}

[heat3d_watch/adapters/racing.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/racing.py)

<!-- Generato dall'adattatore da tools/gen_game_pages.py; per cambiarlo modifica l'adattatore ed eseguilo di nuovo invece di modificare questa pagina. -->
