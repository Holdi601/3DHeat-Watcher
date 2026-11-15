---
title: "IL-2 Sturmovik: Great Battles (dati in tempo reale)"
nav_order: 26
lang: "it"
source: game-il2.md
source_hash: "b6c4de7dcc14"
nav_exclude: true
search_exclude: true
---
# IL-2 Sturmovik: Great Battles (dati in tempo reale) {#il-2-sturmovik-great-battles-live-data}

Mentre giochi a IL-2 Sturmovik: Great Battles, il watcher salva i dati che il gioco stesso invia, così puoi guardarli più tardi come statistiche e una cronologia.

*Dettagli tecnici: adattatore `il2`, tipo [`telemetry`](sources-and-rules.md); gira mentre `Il-2.exe` o `IL2Series.exe` è in esecuzione e cerca nuovi dati ogni 0,1 s.*

## Cosa viene registrato {#what-is-recorded}

- sortite: l'aereo preso (spawn) e il momento in cui l'uscita si ferma (session_end) - nessuna posizione nel mondo: il gioco non ne invia una
- bombe e razzi sganciati (massa), colpi e danni subiti, esplosioni, raffiche di cannone - posizioni locali all'aereo
- velocità indicata equivalente, AGL, velocità verticale, g, giri motore una volta al secondo, con ogni altro indicatore che il pacchetto contiene (pressione del collettore, vibrazione del motore, stato e pressione del carrello, AoA, derapata, accelerazione x/y/z, vibrazione della cabina, flap, aerofreni)
- sortite, colpi sparati, bombe, razzi, colpi subiti, velocità massima, g massimo, tempo di volo; titolo del server e nome del pilota online
- ogni pacchetto di telemetria conservato intero in heat.raw.parquet

## Da dove arriva {#where-it-comes-from}

l'uscita UDP di telemetria del gioco verso 127.0.0.1:41995 ([KEY = telemetrydevice] in &lt;gioco&gt;\data\startup.cfg)

## Come attivarlo {#how-to-switch-it-on}

python -m heat3d_watch setup il2 --apply (aggiunge addrN = "127.0.0.1:41995", enable = true), poi riavvia IL-2

Digita il comando in un terminale aperto nella cartella del watcher (vedi [Prima di iniziare](before-you-start.md)). Se fallisce, l'ultima riga dice perché; [Installazione e avvio](installing-and-running.md) elenca le cause più comuni.

`python -m heat3d_watch setup il2` elenca i file che cambierebbe; `python -m heat3d_watch setup il2 --apply` li cambia, conservando l'originale come `<file>.heat3d-backup` (vedi [Comandi](commands.md#setup)). Stampa `il2: changed: ...` per ogni modifica, oppure `il2: nothing to change` quando è già attivo.

## Come funziona {#how-it-works}

IL-2 Sturmovik: Great Battles - l'uscita UDP di telemetria del gioco e le sue registrazioni Tacview.

1. Telemetria ("Telemetry output of IL2 v4.003", revisione 1.2, distribuita come
   `<gioco>\Doc\UDP_Output\Il2_TeleOutput.pdf`). Attivata in
   `<gioco>\data\startup.cfg`, sezione `[KEY = telemetrydevice]`: `addr`,
   `addr1`, ... = "IP[:porta]" (più destinazioni insieme), `decimation` (50 Hz /
   n), `enable`, `port`. `setup` aggiunge una destinazione, 127.0.0.1:41995 (JoyPro usa
   41994, la porta predefinita del gioco è 4322), e attiva l'uscita. Pacchetti,
   little-endian:

   ```text
   DWORD  Packet_ID 0x54000101
   WORD   Size
   DWORD  Tick (1/50 s)
   BYTE   Indicators_Count, then SIndicator {WORD id, BYTE n, n x 32-bit float}
   BYTE   Events_Count,     then SEvent     {WORD id, BYTE size, size bytes}
   ```

   Indicatori: 0 ENG_RPM, 1 ENG_MP, 2/3 vibrazione del motore, 4 LGEARS_STATE, 5
   LGEARS_PRESS, 6 EAS (m/s), 7 AOA (rad), 8 ACCELERATION (xyz compresa la gravità),
   9 COCKPIT_SHAKE, 10 AGL (m), 11 FLAPS, 12 AIR_BRAKES, 13 AOS (rad), 14
   VERTICAL_SPEED (m/s). Eventi (impacchettati a 2 byte): 0 SET_FOCUS (STRING: byte di
   lunghezza + ASCII), 1 SETUP_ENG {short index, short id, float pos[3], float
   max_rpm}, 2 SETUP_GUN {short index, float pos[3], float projectile mass,
   float muzzle velocity}, 3 SETUP_LGEAR {short index, short id, float
   pos[3]}, 4 DROP_BOMB e 5 ROCKET_LAUNCH
   {float pos[3], float mass, WORD flags}, 6 HIT e 7 DAMAGE {float pos[3],
   float force[3]}, 8 EXPLOSION {float pos[3], float radius}, 9 GUN_FIRE {BYTE
   gun}, 10 SRV_ADDR, 11 SRV_TITLE, 12 SRS_ADDR (STRING), 13 CLIENT_DAT {long
   client, long server client, char name[32]}, 14 CTRL_DAT {long parent, short
   coalition}. Le posizioni degli eventi sono locali all'aereo del giocatore; il flusso
   non ha alcuna posizione nel mondo: quindi sono eventi e numeri, non una traccia.

2. Registrazione Tacview: `tacviewrecord = 1` in `[KEY = track_record]` fa scrivere al
   gioco `<gioco>\data\Tracks\*.acmi` (in multigiocatore decide il server).
   Un file finito viene convertito: ogni aereo, veicolo e nave con le sue posizioni,
   comparsa e rimozione (distrutto o scomparso), decolli e atterraggi quando la
   registrazione li ha. Formato testo ACMI 2.x, semplice o compresso in zip, secondo
   <https://www.tacview.net/documentation/acmi/en/> - le righe "#t" spostano l'orologio,
   le righe "id,Key=Value,..." impostano le proprietà (id esadecimali, virgole escapate
   "\\,", una "\\" finale continua la riga), "-id" rimuove un oggetto, l'oggetto 0 contiene
   i globali (ReferenceLongitude/Latitude, RecordingTime, ...) e gli eventi
   ("Event=Destroyed\|id\|text"). T = Lon\|Lat\|Alt[\|U\|V] oppure
   Lon\|Lat\|Alt\|Roll\|Pitch\|Yaw[\|U\|V\|Heading], longitudine e latitudine rispetto
   al riferimento, campi vuoti invariati. Le posizioni finiscono in una mappa piatta attorno al
   punto di riferimento: x est, y altitudine, z nord, in metri. Il punto di riferimento è il
   `geo` della sessione, riportato in meta.json e nel footer della tabella, così il
   visualizzatore può mettere il mondo reale sotto le tracce.

Lo stesso modulo serve anche: [IL-2 Sturmovik: Great Battles (replay)](game-il2-tacview.md).

## Posizioni e assi {#positions-and-axes}

| | |
|---|---|
| Posizioni registrate | no |
| Asse verticale | `y` |
| Unità | nessuna: la telemetria non ha posizioni nel mondo |
| Specchiato per il visualizzatore | nessuno |
| Scala delle unità (`scale`: il visualizzatore moltiplica le posizioni per questo valore) | 1 |

Questi valori finiscono in `meta.json` di ogni sessione (`axes`) e, quando la sessione ha posizioni, nel footer di `heat.parquet`, così il visualizzatore 3DHeat ruota e scala le righe da solo: vedi [I dati](the-data.md).

## Multigiocatore {#multiplayer}

- Segnato come giocato online (`multiplayer`): **sì**. `games --markdown` lo mostra come "consentito (legge solo ciò che il gioco pubblica)".
- Tipo `telemetry`: legge solo ciò che il gioco o la piattaforma rende disponibile (una porta UDP o la memoria condivisa che il gioco pubblica), quindi registra anche nel gioco online oltre che offline; il contrassegno decide solo se la memoria può mai essere letta.
- Memoria: **mai** letta da questo adattatore. Solo gli adattatori `memory` leggono la memoria, e mai per un gioco segnato come giocato online: vedi [Fonti e regole](sources-and-rules.md).

## Statistiche registrate {#statistics-recorded}

Chiavi statistiche che il codice di questo adattatore imposta per nome (`stats` di ogni sessione in `meta.json` e la tabella `stats` di `watcher.sqlite`):

`bad_packets`, `bombs_dropped`, `damage_taken`, `explosions`, `flight_time`, `hits_taken`, `max_agl_m`, `max_eas_kmh`, `max_g`, `ordnance_kg`, `rockets_fired`, `rounds_fired`, `sorties`

Una chiave tra parentesi graffe viene completata durante l'esecuzione (`score.{team}` è una chiave per ogni squadra). Le chiavi che il codice prende da una tabella dei campi del gioco o dai nomi statistici del gioco non sono in questo elenco; "Cosa viene registrato" sopra le nomina.

## Completezza {#completeness}

Il watcher segue la [regola del convertitore](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md) di 3DHeat: ciò che la sorgente contiene viene letto o conservato, mai scartato. Oltre alle righe, ogni pacchetto, pagina, riga o risposta che l'adattatore riceve viene conservato intero in `heat.raw.parquet` della sessione (colonne `time`, `ms`, `type`, `used`, `payload`, `text`, poi ogni campo conservato per nome; `used` segna ciò che è diventato anche riga), e `selfCheck.completeness` in `meta.json` conta ogni `type`: `lost` è 0.

**Letto**

- SET_FOCUS (l'aereo preso: una sortita), DROP_BOMB e ROCKET_LAUNCH (massa, posizione locale), HIT e DAMAGE (posizione locale, forza), EXPLOSION (posizione locale, raggio), GUN_FIRE (colpi per interrogazione) come righe
- SETUP_ENG (indice, id, posizione locale, giri massimi), SETUP_GUN (indice, posizione locale, massa del proiettile, velocità alla bocca) e SETUP_LGEAR (indice, id, posizione locale) come righe: i motori, i cannoni e le gambe del carrello dell'aereo all'inizio della sortita
- SRV_TITLE, SRV_ADDR, SRS_ADDR e CLIENT_DAT (nome del pilota) in meta.json; la coalizione di CTRL_DAT come squadra della sortita
- tutti e quindici gli indicatori della specifica sulla riga `state` una volta al secondo (un valore come numero, uno per motore, gamba del carrello o asse come lista); velocità, g e AGL massimi da ogni pacchetto

**Conservato grezzo**

- ogni datagramma intero come `payload`, sotto il suo Packet_ID: `0x54000101` per la telemetria (usato quando ha creato una riga o una voce di meta.json), ogni altro id come è, un datagramma piÃ¹ corto dell'intestazione viene conservato come `short`
- ciò che solo il file accessorio grezzo contiene: gli indicatori tra le righe una volta al secondo (il gioco li invia a 50 Hz / decimation), un evento SETUP più corto del layout della specifica, id di eventi che la specifica non elenca

**Non disponibile**

- una posizione nel mondo: l'uscita di telemetria non ne ha; l'adattatore il2-tacview legge le posizioni dalle registrazioni Tacview del gioco
- altri aerei e giocatori: l'uscita descrive solo l'aereo del giocatore

**Dimensione**: circa 8 MB all'ora alla frequenza di 10 Hz di setup (decimation 5; un pacchetto è di circa 160 byte più il suo frame), 40 MB alla piena frequenza di 50 Hz del gioco, prima di zstd; zstd riduce i float ripetitivi a una frazione

## Verificato {#verified}

testato su pacchetti costruiti dalla specifica Il2_TeleOutput del gioco (rev 1.2); modifiche a startup.cfg testate su una copia del file; non ancora testato con il gioco in esecuzione

## Sorgente {#source}

[heat3d_watch/adapters/il2.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/il2.py)

<!-- Generated from the adattatore by tools/gen_game_pages.py; change the adattatore and run it again rather than editing this page. -->
