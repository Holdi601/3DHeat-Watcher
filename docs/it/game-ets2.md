---
title: "Euro Truck Simulator 2 (dati in tempo reale)"
nav_order: 19
lang: "it"
source: game-ets2.md
source_hash: "537f0daeedbf"
nav_exclude: true
search_exclude: true
---
# Euro Truck Simulator 2 (dati in tempo reale) {#euro-truck-simulator-2-live-data}

Mentre giochi ad Euro Truck Simulator 2, il watcher salva i dati che il gioco stesso invia, così puoi guardarli più tardi su una mappa nel visualizzatore 3DHeat.

*Dettagli tecnici: adattatore `ets2`, tipo [`telemetry`](sources-and-rules.md); funziona mentre `eurotrucks2.exe` è in esecuzione e cerca nuovi dati ogni 0,1 s.*

## Cosa viene registrato {#what-is-recorded}

- la posizione nel mondo del camion (x est, y in alto, z sud, m) a 10 Hz mentre si muove, ogni 5 s mentre è fermo; direzione, velocità, contachilometri
- lavori iniziati (carico, partenza, destinazione), consegnati (ricavo, XP, km), annullati; multe, pedaggi, traghetti, treni, rifornimenti
- traghetti, treni e salvataggi caricati interrompono il percorso (teleport, spawn)
- distanza, velocità massima, consegne, ricavi, XP, multe
- l'intera memoria condivisa del plugin in `heat.raw.parquet`, ogni volta che cambia

## Da dove arriva {#where-it-comes-from}

memoria condivisa Local\SCSTelemetry scritta dal plugin RenCloud scs-sdk-plugin (revisione 12) in &lt;gioco&gt;\bin\win_x64\plugins

## Come attivarlo {#how-to-switch-it-on}

installa scs-telemetry.dll (revisione 12) da github.com/RenCloud/scs-sdk-plugin in &lt;gioco&gt;\bin\win_x64\plugins; il gioco chiede una volta per avvio di consentire l'SDK

## Come funziona {#how-it-works}

Euro Truck Simulator 2 e American Truck Simulator: l'SDK di telemetria di SCS, tramite il plugin RenCloud.

SCS pubblica un SDK di telemetria (<https://modding.scssoft.com/wiki/Documentation/Engine/SDK/Telemetry>)
per i plugin che il giocatore mette in `<gioco>\bin\win_x64\plugins\`. Il gioco
stesso non pubblica nulla; il plugin molto usato da <https://github.com/RenCloud/scs-sdk-plugin>
(MIT) copia i canali dell'SDK nella memoria condivisa `Local\SCSTelemetry`
(32 KiB), con il layout descritto in `scs-telemetry/inc/scs-telemetry-common.hpp`. Questo legge
la revisione 12 di quel layout (PLUGIN_REVID 12) e nient'altro: il plugin
scrive la sua revisione all'offset 40, e qualsiasi altra revisione viene lasciata non letta
piuttosto che letta male. Offset usati (zone come le indica l'intestazione; allineamento naturale):

```text
   0  bool sdkActive          4  bool paused
  40  u32  telemetry_plugin_revision, version_major, version_minor, game (1 ETS2, 2 ATS)
  64  u32  common_ui.time_abs (in-game minutes)
 504  i32  truck_i.gear
 640  i32  gameplay_i.jobDeliveredEarnedXp
 948  f32  truck_f.speed (m/s); 952 engineRpm; 1056 truckOdometer (km)
1460  f32  gameplay_f.jobDeliveredDistanceKm
2200  f64  truck_dp.coordinateX/Y/Z (m), rotationX/Y/Z (heading, pitch, roll in turns, 0..1)
2300  char[64] config_s: truckBrand +64, truckName +192, cargo +320, cityDst +448, compDst +576,
      citySrc +704, compSrc +832; 3436 gameplay_s.fineOffence[32]
4200  i64  gameplay_ll: jobCancelledPenalty, jobDeliveredRevenue, fineAmount, tollgatePayAmount,
      ferryPayAmount, trainPayAmount
4300  bool special_b: onJob, jobFinished, jobCancelled, jobDelivered, fined, tollgate, ferry,
      train, refuel, refuelPayed
```

La posizione del camion nel mondo è il sistema di SCS: x est, y in alto, z sud, metri
(destrorso, y in alto - il visualizzatore la disegna così com'è). Traghetti, treni e il
caricamento di un salvataggio spostano il camion senza guidare: il percorso viene interrotto lì.

L'intera mappatura (i 32 KiB del plugin: ogni zona qui sopra e quelle non lette - configurazione del
camion, ruote, usura, gli altri canali del camion, e ciò che la revisione contiene dopo il byte 4400, i
rimorchi) viene conservata nei dati grezzi della sessione ogni volta che cambia, `type`
`SCSTelemetry` con `revision` accanto - anche una pagina di un'altra revisione viene conservata
intera piuttosto che letta male.

Lo stesso modulo serve anche: [American Truck Simulator (dati in tempo reale)](game-ats.md).

## Posizioni e assi {#positions-and-axes}

| | |
|---|---|
| Posizioni registrate | sì |
| Asse verticale | `y` |
| Unità | metri (mondo SCS: x est, y in alto, z sud) |
| Specchiato per il visualizzatore | nessuno |
| Scala delle unità (`scale`: il visualizzatore moltiplica le posizioni per questo valore) | 1 |

Questi valori finiscono in `meta.json` di ogni sessione (`axes`) e, quando la sessione ha posizioni, nel footer di `heat.parquet`, così il visualizzatore 3DHeat ruota e scala le righe da solo - vedi [I dati](the-data.md).

## Multigiocatore {#multiplayer}

- Segnato come giocato online (`multiplayer`): **sì**. `games --markdown` lo mostra come "consentito (legge solo ciò che il gioco pubblica)".
- Tipo `telemetry`: legge solo ciò che il gioco o la piattaforma consegna (una porta UDP o una memoria condivisa che il gioco pubblica), quindi registra anche nel gioco online oltre che offline; il flag decide solo se la memoria può mai essere letta.
- Memoria: **mai** letta da questo adattatore. Solo gli adattatori `memory` leggono la memoria, e mai per un gioco segnato come giocato online - vedi [Fonti e regole](sources-and-rules.md).

## Statistiche registrate {#statistics-recorded}

Chiavi di statistica che il codice di questo adattatore imposta per nome (`stats` di ogni sessione in `meta.json` e la tabella `stats` di `watcher.sqlite`):

`deliveries`, `distance_km`, `fines`, `fines_total`, `jobs_cancelled`, `max_speed_kmh`, `refuels`, `revenue`, `tolls_total`, `xp`

Una chiave tra parentesi graffe viene completata durante l'esecuzione (`score.{team}` è una chiave per squadra). Le chiavi che il codice prende da una tabella dei campi del gioco o dai nomi di statistica del gioco non sono in questo elenco; "Cosa viene registrato" sopra le nomina.

## Completezza {#completeness}

Il watcher segue la [regola del convertitore](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md) di 3DHeat: ciò che la fonte contiene viene letto o conservato, mai scartato. Oltre alle righe, ogni pacchetto, pagina, riga o risposta che l'adattatore riceve viene conservato intero in `heat.raw.parquet` della sessione (colonne `time`, `ms`, `type`, `used`, `payload`, `text`, poi ogni campo conservato per nome; `used` segna ciò che è diventato anche riga), e `selfCheck.completeness` in `meta.json` conta ogni `type` - `lost` è 0.

**Letto**

- stato di SDK e pausa, revisione del plugin, gioco e versione, ora di gioco, posizione e direzione del camion nel mondo, velocità, contachilometri, marca e nome del camion, carico, città e azienda di partenza e destinazione, ricavo del lavoro, XP e distanza, penale per annullamento, multe e relativa infrazione, pedaggi, traghetti, treni, i flag degli eventi speciali (righe, eventi e statistiche)
- ora anche nelle righe di posizione: `pitch` e `roll` (gradi, dalle rotazioni dell'SDK), `gear` e `rpm`
- offset verificati con una trascrizione campo per campo dell'intestazione della revisione 12 del plugin, con gli inizi delle zone affermati nei test; non ancora verificati con il gioco

**Conservato grezzo**

- `SCSTelemetry`: i 32 KiB interi della mappatura del plugin, ogni lettura i cui byte differiscono dalla copia conservata per ultima (`unchanged_reads` in meta.json conta le altre), con `revision` accanto: ogni zona - configurazione del camion e del rimorchio, i canali del camion (pedali, sterzo, carburante, AdBlue, pressioni, temperature, usura, luci, ruote), vettori di posizione e accelerazione, stringhe di lavoro e di gioco, e tutto ciò che la revisione contiene dopo il byte 4400 (i rimorchi); `used` è vero finché l'SDK è attivo e la revisione è 12
- una pagina di un'altra revisione del plugin viene conservata intera con `used` falso invece di essere letta male

**Non disponibile**

- tutto ciò che il plugin non copia dall'SDK, e tutto mentre il plugin non è installato: il gioco non pubblica una telemetria propria
- i camion di altri giocatori in TruckersMP o nelle carovane: l'SDK dà solo il camion del giocatore

**Dimensione**: 32 KiB fino a 10 volte al secondo mentre si guida (ogni lettura differisce allora): circa 1,2 GB all'ora prima della compressione, una sola copia in pausa; la maggior parte della pagina è fatta di zeri e configurazione che non cambia, quindi zstd la riduce di molte volte (non ancora misurato su una sessione reale)

## Verificato {#verified}

testato su memoria condivisa costruita dal layout di intestazione della revisione 12 del plugin; non ancora testato con il gioco

## Fonte {#source}

[heat3d_watch/adapters/ets2.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/ets2.py)

<!-- Generated from the adattatore by tools/gen_game_pages.py; change the adattatore and run it again rather than editing this page. -->
