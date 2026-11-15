---
title: "IL-2 Sturmovik: Great Battles (replay)"
nav_order: 27
lang: "it"
source: game-il2-tacview.md
source_hash: "0bb23bddee03"
nav_exclude: true
search_exclude: true
---
# IL-2 Sturmovik: Great Battles (replay) {#il-2-sturmovik-great-battles-replays}

Dopo una partita di IL-2 Sturmovik: Great Battles, il watcher trasforma il replay salvato dal gioco in file che puoi guardare su una mappa nel visualizzatore 3DHeat.

*Dettagli tecnici: adattatore `il2-tacview`, tipo [`replay`](sources-and-rules.md); gira sempre (non aspetta che un gioco si avvii) e cerca nuovi dati ogni 5 s.*

## Cosa viene registrato {#what-is-recorded}

- ogni aereo, veicolo e nave della registrazione: posizioni una volta al secondo (metri est/alto/nord dal punto di riferimento della registrazione; lat/lon/alt come colonne)
- comparse, distruzioni (morte) e uscite (left), decolli e atterraggi quando sono registrati
- oggetti, distrutti, decolli, atterraggi e durata per registrazione
- ogni riga della registrazione conservata intera in heat.raw.parquet, sull'orologio delle righe

## Da dove arriva {#where-it-comes-from}

le registrazioni Tacview che il gioco stesso salva &lt;gioco&gt;\data\Tracks\\\*.acmi (testo ACMI 2.x, semplice o compresso in zip)

## Come attivarlo {#how-to-switch-it-on}

python -m heat3d_watch setup il2-tacview --apply (tacviewrecord = 1 in [KEY = track_record])

Digita il comando in un terminale aperto nella cartella del watcher (vedi [Prima di iniziare](before-you-start.md)). Se fallisce, l'ultima riga dice perché; [Installazione e avvio](installing-and-running.md) elenca le cause più comuni.

`python -m heat3d_watch setup il2-tacview` elenca i file che cambierebbe; `python -m heat3d_watch setup il2-tacview --apply` li cambia, conservando l'originale come `<file>.heat3d-backup` (vedi [Comandi](commands.md#setup)). Stampa `il2-tacview: changed: ...` per ogni modifica, oppure `il2-tacview: nothing to change` quando è già attivo.

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

Lo stesso modulo serve anche: [IL-2 Sturmovik: Great Battles (dati in tempo reale)](game-il2.md).

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

- Segnato come giocato online (`multiplayer`): **sì**. `games --markdown` lo mostra come "consentito (legge solo ciò che il gioco pubblica)".
- Tipo `replay`: legge solo ciò che il gioco o la piattaforma rende disponibile (replay e demo che il gioco salva), quindi registra anche nel gioco online oltre che offline; il contrassegno decide solo se la memoria può mai essere letta.
- Memoria: **mai** letta da questo adattatore. Solo gli adattatori `memory` leggono la memoria, e mai per un gioco segnato come giocato online: vedi [Fonti e regole](sources-and-rules.md).

## Statistiche registrate {#statistics-recorded}

Chiavi statistiche che il codice di questo adattatore imposta per nome (`stats` di ogni sessione in `meta.json` e la tabella `stats` di `watcher.sqlite`):

`destroyed`, `duration_s`, `objects`, `{r.event}s`

Una chiave tra parentesi graffe viene completata durante l'esecuzione (`score.{team}` è una chiave per ogni squadra). Le chiavi che il codice prende da una tabella dei campi del gioco o dai nomi statistici del gioco non sono in questo elenco; "Cosa viene registrato" sopra le nomina.

## Completezza {#completeness}

Il watcher segue la [regola del convertitore](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md) di 3DHeat: ciò che la sorgente contiene viene letto o conservato, mai scartato. Oltre alle righe, ogni pacchetto, pagina, riga o risposta che l'adattatore riceve viene conservato intero in `heat.raw.parquet` della sessione (colonne `time`, `ms`, `type`, `used`, `payload`, `text`, poi ogni campo conservato per nome; `used` segna ciò che è diventato anche riga), e `selfCheck.completeness` in `meta.json` conta ogni `type`: `lost` è 0.

**Letto**

- la T di ogni oggetto (longitudine, latitudine, altitudine, rollio, beccheggio, imbardata, U, V, direzione) come posizioni una volta al secondo per oggetto, con Name, Type, Pilot, Coalition/Color, Country, Group e Parent
- comparse, rimozioni (morte quando prima è arrivato un evento Destroyed, altrimenti left), eventi TakenOff e Landed, eventi Message e Bookmark come righe
- i globali ReferenceLongitude/Latitude (l'origine della mappa), RecordingTime/ReferenceTime (quando), DataSource, DataRecorder e Title in meta.json

**Conservato grezzo**

- ogni riga logica non vuota intera come `text` (una riga continuata con una barra rovesciata finale è unita, come la legge ACMI), sotto il suo tipo: `header` (FileType, FileVersion), `comment`, `time` (#t), `remove` (-id), `global` ed `event` (oggetto 0), `object` (id,Key=Value,...)
- ciò che solo il file accessorio grezzo contiene: le posizioni tra le righe una volta al secondo, armi, proiettili, bengala, chaff e altri oggetti non disegnati come tracce, ogni altra proprietà (telemetria come IAS, AOA, acceleratore, carburante dove la registrazione li ha), altri globali (Comments, Briefing, Author, Category), eventi diversi da quelli letti (Timeout, LeftArea, ...)

**Non disponibile**

- nulla di ciò che la registrazione contiene; ciò che il gioco non scrive nelle sue registrazioni non c'è

**Dimensione**: circa il testo della registrazione più circa 70 byte per riga, prima di zstd: una registrazione da 100 MB produce circa 150-250 MB grezzi, che zstd riporta vicino alle dimensioni della registrazione compressa in zip

## Verificato {#verified}

testato su file ACMI 2.2 sintetici (testo e zip); non ancora testato su una registrazione del gioco

## Sorgente {#source}

[heat3d_watch/adapters/il2.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/il2.py)

<!-- Generated from the adattatore by tools/gen_game_pages.py; change the adattatore and run it again rather than editing this page. -->
