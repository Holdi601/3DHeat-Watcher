---
title: "DiRT Rally 2.0 (dati in tempo reale)"
nav_order: 11
lang: "it"
source: game-dirt-rally-2.md
source_hash: "367131ff990b"
nav_exclude: true
search_exclude: true
---
# DiRT Rally 2.0 (dati in tempo reale) {#dirt-rally-20-live-data}

Mentre giochi a DiRT Rally 2.0, il watcher salva i dati che il gioco stesso invia, così puoi guardarli più tardi su una mappa nel visualizzatore 3DHeat.

*Dettagli tecnici: adattatore `dirt-rally-2`, tipo [`telemetry`](sources-and-rules.md); gira mentre `dirtrally2.exe` è in esecuzione e cerca nuovi dati ogni 0,1 s.*

## Cosa viene registrato {#what-is-recorded}

- posizione della tua auto (XYZ nel mondo, m) a 10 Hz, con velocità, marcia, acceleratore, freno, distanza nella tappa
- inizio tappa (quando parte l'orologio della tappa), arrivo con il tempo della tappa, riavvii
- teletrasporti (un ripristino sulla strada): `teleport` dove si trovava l'auto, `spawn` dove si trova ora
- tappe, miglior tempo di tappa, distanza, velocità massima

## Da dove arriva {#where-it-comes-from}

UDP 127.0.0.1:20777, extradata=3 (Documents\My Games\DiRT Rally 2.0\hardwaresettings\hardware_settings_config.xml); mentre un'altra app tiene la porta 20777, il watcher la lascia a lei

## Come attivarlo {#how-to-switch-it-on}

`python -m heat3d_watch setup dirt-rally-2 --apply` imposta &lt;udp enabled="true" extradata="3"&gt; (prima viene fatta una copia di sicurezza)

Digita il comando in un terminale aperto nella cartella del watcher (vedi [Prima di iniziare](before-you-start.md)). Se fallisce, l'ultima riga dice perché; [Installazione e avvio](installing-and-running.md) elenca le cause più comuni.

`python -m heat3d_watch setup dirt-rally-2` elenca i file che cambierebbe; `python -m heat3d_watch setup dirt-rally-2 --apply` li cambia, conservando l'originale come `<file>.heat3d-backup` (vedi [Comandi](commands.md#setup)). Stampa `dirt-rally-2: changed: ...` per ogni modifica, oppure `dirt-rally-2: nothing to change` quando è già attivo.

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

#### EA SPORTS WRC, DiRT Rally 2.0, Richard Burns Rally {#ea-sports-wrc-dirt-rally-20-richard-burns-rally}

UDP: il file `Documents/My Games/WRC/telemetry/config.json` di WRC (il pacchetto `session_update`
della struttura `wrc`), il file `hardware_settings_config.xml` di DiRT
(`<udp enabled="true" extradata="3" port="20777">`), il plugin NGP di RBR
(`udpTelemetry=1`, porta 6776). Tappe dall'orologio di tappa del gioco
(`rally.StageSplitter`). RBR non documenta i suoi assi: l'asse verticale è
quello lungo il quale la tappa varia di meno, deciso alla chiusura della sessione.

#### Tutto ciò che viene conservato {#everything-kept}

Le righe sono poche al secondo; i giochi ne inviano molte di più. Ogni pacchetto UDP
che arriva (nei menu, tra un giro e l'altro, quelli che nessun decodificatore legge) viene conservato intero
in `heat.raw.parquet` della sessione, sotto il suo formato (`dash-horizon`,
`session_update`, `extradata3`, `H3D1`, ...), e ogni pagina di memoria condivisa
(l'intera mappatura, non solo i byte decodificati) ogni volta che cambia, sotto
il nome della sua mappatura (`acpmf_physics`, ...). `used` segna ciò che è diventato anche
righe; `selfCheck.completeness` in `meta.json` conta ogni tipo (regola del convertitore di 3DHeat).

Lo stesso modulo serve anche: [Assetto Corsa (dati in tempo reale)](game-assetto-corsa.md), [Assetto Corsa Competizione (dati in tempo reale)](game-assetto-corsa-competizione.md), [Assetto Corsa EVO (dati in tempo reale)](game-assetto-corsa-evo.md), [Assetto Corsa Rally (dati in tempo reale)](game-assetto-corsa-rally.md), [BeamNG.drive (dati in tempo reale)](game-beamng.md), [EA SPORTS WRC (dati in tempo reale)](game-ea-wrc.md), [Forza Horizon 4 (dati in tempo reale)](game-forza-horizon-4.md), [Forza Horizon 5 (dati in tempo reale)](game-forza-horizon-5.md), [Forza Horizon 6 (dati in tempo reale)](game-forza-horizon-6.md), [Forza Motorsport (dati in tempo reale)](game-forza-motorsport.md), [Richard Burns Rally (dati in tempo reale)](game-richard-burns-rally.md).

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

`best_lap`, `best_stage`, `distance_km`, `laps`, `stages`, `top_speed_kmh`

Una chiave tra parentesi graffe viene completata durante l'esecuzione (`score.{team}` è una chiave per ogni squadra). Le chiavi che il codice prende da una tabella dei campi del gioco o dai nomi statistici del gioco non sono in questo elenco; "Cosa viene registrato" sopra le nomina.

## Completezza {#completeness}

Il watcher segue la [regola del convertitore](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md) di 3DHeat: ciò che la fonte contiene viene letto o conservato, mai scartato. Oltre alle righe, ogni pacchetto, pagina, riga o risposta che l'adattatore riceve viene conservato intero in `heat.raw.parquet` della sessione (colonne `time`, `ms`, `type`, `used`, `payload`, `text`, poi ogni campo conservato per nome; `used` segna ciò che è diventato anche riga), e `selfCheck.completeness` in `meta.json` conta ogni `type`: `lost` è 0.

**Letto**

- righe a 10 Hz: posizione, velocità, marcia, acceleratore, freno, distanza nella tappa, imbardata, giri al minuto, sterzo; inizio tappa, arrivo con il tempo della tappa, riavvii

**Conservato grezzo**

- ogni pacchetto che raggiunge la porta, intero, alla frequenza del gioco, sotto il suo formato: `extradata3` (66 float, 264 byte), `extradata3-64` (64 di DiRT Rally), `<n>-byte` negli altri casi
- nel pacchetto oltre alle righe: tutti i 66 float: velocità del mondo, vettori laterale e frontale, posizione e velocità della sospensione di ogni ruota, velocità dell'impronta e temperatura dei freni, accelerazioni g, giri, lunghezza della tappa; i float senza un nome stabilito sono nei file dei giri come `float<i>`

**Non disponibile**

- altre auto: i giochi inviano solo l'auto del giocatore
- un canale del freno a mano: il pacchetto non ne ha

**Dimensione**: circa 70 MB all'ora a 60 pacchetti al secondo (264 byte più un'intestazione di 70 byte per elemento); zstd ne mantiene una frazione

## Verificato {#verified}

decodifica del registratore di giri di gamecapture (testata su pacchetti costruiti dai layout documentati); l'adattatore testato su pacchetti costruiti nel test, inviati via UDP; non ancora testato con il gioco

## Fonte {#source}

[heat3d_watch/adapters/racing.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/racing.py)

<!-- Generated from the adattatore by tools/gen_game_pages.py; change the adattatore and run it again rather than editing this page. -->
