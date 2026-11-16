---
title: "X-Plane (dati in tempo reale)"
nav_order: 49
lang: "it"
source: game-xplane.md
source_hash: "be1c5b21d2ef"
nav_exclude: true
search_exclude: true
---
# X-Plane (dati in tempo reale) {#x-plane-live-data}

Mentre giochi a X-Plane, il watcher salva i dati che il gioco stesso invia, così puoi guardarli più tardi su una mappa nel visualizzatore 3DHeat.

*Dettagli tecnici: adattatore `xplane`, tipo [`telemetry`](sources-and-rules.md); gira mentre `X-Plane.exe` è in esecuzione e cerca nuovi dati ogni 0,1 s.*

## Cosa viene registrato {#what-is-recorded}

- posizione propria a 10 Hz (latitudine/longitudine/altitudine come metri est/alto/nord dal primo rilevamento; lat/lon/alt conservate come colonne)
- assetto, velocità indicata e vera, velocità al suolo, Mach, velocità verticale, AoA, derapata, rotta magnetica, AGL, g (normali, assiali, laterali), velocità e velocità di rotazione, flap, aerofreni, acceleratore, a terra
- pesi (totale, carburante, carico), leva del carrello, pilota automatico, giri motore e N1, tempo e data del simulatore, pausa, velocità del simulatore, replay, temperatura esterna e pressione al livello del mare (X-Plane 12) una volta al secondo
- decolli, atterraggi, schianti, reset del volo (session_start/session_end per volo)
- tempo di volo, tempo in volo, distanza, quota massima, g massimo, atterraggi
- ogni risposta che X-Plane invia conservata intera in heat.raw.parquet

## Da dove arriva {#where-it-comes-from}

l'interfaccia UDP di X-Plane su 127.0.0.1:49000 (RREF dataref e RPOS posizione, risposte al watcher)

## Come attivarlo {#how-to-switch-it-on}

X-Plane 12: Impostazioni > Rete > Accetta connessioni in entrata (X-Plane 11 risponde di default)

## Come funziona {#how-it-works}

X-Plane 11 e 12: l'interfaccia UDP del simulatore sulla porta 49000.

X-Plane risponde a chiunque chieda su 127.0.0.1:49000, alla frequenza richiesta, all'
indirizzo e alla porta da cui arriva la richiesta (documento "Exchanging Data with
X-Plane" di X-Plane, distribuito in `<X-Plane>\Instructions\`):

```text
RREF  "RREF\0" + int32 freq + int32 index + char[400] dataref path (413 bytes).
      The answer is "RREF" + one internal byte + (int32 index, float32 value)
      pairs; freq 0 stops it.
RPOS  "RPOS\0" + the rate as a NUL-terminated ASCII string ("10\0"). The
      answer is "RPOS" + one internal byte + double lon, lat, elevation (m
      MSL) + float AGL (m), pitch, true heading, roll (deg), vx east, vy up,
      vz south (m/s), P, Q, R (rad/s), tightly packed.
```

RPOS dà latitudine e longitudine come double (RREF solo come float, a mezzo metro di
distanza), quindi guida la posizione; RREF porta il resto e fa da supplente quando RPOS
non arriva. Dataref (nomi come nel `Resources\plugins\DataRefs.txt` di X-Plane 12,
<https://developer.x-plane.com/datarefs/>):

```text
sim/flightmodel/position/latitude, longitude, elevation  deg, deg, m MSL
sim/flightmodel/position/true_theta, true_phi, true_psi  pitch, roll, true heading (deg)
sim/flightmodel/position/indicated_airspeed              knots
sim/flightmodel/position/groundspeed                     m/s
sim/flightmodel/position/y_agl                           m above ground
sim/flightmodel/forces/g_nrml                            g, normal to the wings
sim/flightmodel/failures/onground_any                    1 on the ground
sim/flightmodel2/misc/has_crashed                        1 crashed
sim/time/total_flight_time_sec                           since the flight was reset
```

e il resto del volo alla stessa frequenza (velocità vera, velocità verticale, AoA,
derapata, rotta magnetica, Mach, g assiali e laterali, velocità di rotazione, flap,
aerofreni, acceleratore: `DATAREFS`), con lo stato più lento dell'aereo una volta al
secondo (pesi, leva del carrello, servi del pilota automatico, motori, tempo del
simulatore, pausa e velocità, meteo: `SLOW_DATAREFS`). Ogni datagramma viene anche
conservato intero nei dati grezzi della sessione, e meta.json indica il dataref
dietro ogni indice RREF.

X-Plane 12 accetta queste richieste solo con Impostazioni > Rete > "Accetta connessioni
in entrata" attivo. Le posizioni finiscono in una mappa piatta attorno al primo rilevamento
della sessione (`Tangent`): x est, z nord in metri, y l'altitudine sul livello del mare - così un
volo livellato resta livellato per quanto lontano vada, cosa che un vero piano tangente
piegherebbe verso il basso con la terra. Il punto di origine della mappa è il `geo` della
sessione: meta.json e il footer della tabella lo riportano, così il visualizzatore può
mettere il mondo reale sotto il volo.

Questo modulo contiene anche ciò che condividono gli altri simulatori di volo: la mappa
piatta, la gestione dei voli (decolli, atterraggi, schianti, distanza), il socket UDP e
l'elenco della libreria Steam.

## Posizioni e assi {#positions-and-axes}

| | |
|---|---|
| Posizioni registrate | sì |
| Asse verticale | `y` |
| Unità | metri (est, altitudine, nord dal primo rilevamento) |
| Specchiato per il visualizzatore | `z` |
| Scala delle unità (`scale`: il visualizzatore moltiplica le posizioni per questo valore) | 1 |

Questi valori finiscono in `meta.json` di ogni sessione (`axes`) e, quando la sessione ha posizioni, nel footer di `heat.parquet`, così il visualizzatore 3DHeat ruota e scala le righe da solo: vedi [I dati](the-data.md).

## Multigiocatore {#multiplayer}

- Segnato come giocato online (`multiplayer`): **no**. `games --markdown` lo mostra come "giocatore singolo".
- Tipo `telemetry`: legge solo ciò che il gioco o la piattaforma rende disponibile (una porta UDP o la memoria condivisa che il gioco pubblica), quindi registra anche nel gioco online oltre che offline; il contrassegno decide solo se la memoria può mai essere letta.
- Memoria: **mai** letta da questo adattatore. Solo gli adattatori `memory` leggono la memoria, e mai per un gioco segnato come giocato online: vedi [Fonti e regole](sources-and-rules.md).

## Statistiche registrate {#statistics-recorded}

Chiavi statistiche che il codice di questo adattatore imposta per nome (`stats` di ogni sessione in `meta.json` e la tabella `stats` di `watcher.sqlite`):

`airborne_time`, `bad_packets`, `crashes`, `distance_km`, `flight_time`, `max_altitude_m`, `max_g`, `{event}s`

Una chiave tra parentesi graffe viene completata durante l'esecuzione (`score.{team}` è una chiave per ogni squadra). Le chiavi che il codice prende da una tabella dei campi del gioco o dai nomi statistici del gioco non sono in questo elenco; "Cosa viene registrato" sopra le nomina.

## Completezza {#completeness}

Il watcher segue la [regola del convertitore](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md) di 3DHeat: ciò che la sorgente contiene viene letto o conservato, mai scartato. Oltre alle righe, ogni pacchetto, pagina, riga o risposta che l'adattatore riceve viene conservato intero in `heat.raw.parquet` della sessione (colonne `time`, `ms`, `type`, `used`, `payload`, `text`, poi ogni campo conservato per nome; `used` segna ciò che è diventato anche riga), e `selfCheck.completeness` in `meta.json` conta ogni `type`: `lost` è 0.

**Letto**

- RPOS (10 Hz): longitudine, latitudine, elevazione, AGL, beccheggio, rotta vera, rollio, velocità (est, alto, sud) e velocità di rotazione P/Q/R - tutto sulle righe
- RREF (10 Hz): i 27 dataref di `DATAREFS` - posizione, assetto, IAS, velocità al suolo, TAS, velocità verticale, AoA, derapata, rotta magnetica, Mach, g normali/assiali/laterali, velocità di rotazione, flap, aerofreni, acceleratore, AGL, schiantato, a terra, tempo di volo - sulle righe
- RREF (1 Hz): i 20 dataref di `SLOW_DATAREFS` - pesi, leva del carrello, servi del pilota automatico, tempo e data del simulatore, pausa, velocità del simulatore, replay, numero di motori, giri dei motori 1-4, N1 dei motori 1-2, temperatura esterna dell'aria, pressione al livello del mare - sulle righe come ultimi ricevuti

**Conservato grezzo**

- ogni datagramma intero come `payload`, sotto la sua intestazione di quattro lettere: `RREF` e `RPOS` (usati quando la richiesta ha creato una riga; nei menu, senza un rilevamento, non ne creano), qualunque altra cosa X-Plane invii alla porta del watcher sotto la sua intestazione o `unknown`; `requests` in meta.json dice quale dataref è ogni indice RREF, così i payload si leggono senza questo modulo

**Non disponibile**

- ogni altro dataref (X-Plane ne ha migliaia): RREF invia solo ciò che viene richiesto, una sottoscrizione ciascuno; l'elenco chiede il volo, lo stato dell'aereo e il tempo del simulatore - più dettagli di cabina (radio, luci, ogni strumento motore, avarie) moltiplicherebbero le richieste
- il nome dell'aereo e il tipo ICAO: dataref a array di byte, che RREF invia come un float per carattere
- altri aerei (IA e multigiocatore): i dataref sim/multiplayer/position non sono richiesti
- l'uscita DATA (Impostazioni > Uscita dati): invia a un indirizzo fisso scelto nel simulatore, non a chi lo chiede; RREF e RPOS coprono ciò che il watcher legge

**Dimensione**: circa 17 MB all'ora prima di zstd (RREF e RPOS a 10 Hz, circa 220 e 70 byte più un frame ciascuno, il lento RREF una volta al secondo), se X-Plane invia i valori di ogni interrogazione in un solo pacchetto come fa; zstd riduce i float di diverse volte

## Verificato {#verified}

testato contro un finto X-Plane che risponde a RREF/RPOS secondo "Exchanging Data with X-Plane" di X-Plane 12; nomi dei dataref verificati su DataRefs.txt di X-Plane 12; non ancora testato con il simulatore in esecuzione

## Fonte {#source}

[heat3d_watch/adapters/xplane.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/xplane.py)

<!-- Generato dall'adattatore da tools/gen_game_pages.py; per cambiarlo modifica l'adattatore ed eseguilo di nuovo invece di modificare questa pagina. -->
