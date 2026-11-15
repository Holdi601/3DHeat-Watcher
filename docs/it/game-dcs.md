---
title: "DCS World (dati in tempo reale)"
nav_order: 10
lang: "it"
source: game-dcs.md
source_hash: "87cba160674e"
nav_exclude: true
search_exclude: true
---
# DCS World (dati in tempo reale) {#dcs-world-live-data}

Mentre giochi a DCS World, il watcher salva i dati che il gioco stesso invia all'esterno, così puoi guardarli più tardi su una mappa nel visualizzatore di 3DHeat.

*Dettagli tecnici: adattatore `dcs`, tipo [`telemetry`](sources-and-rules.md); gira mentre `DCS.exe` è in esecuzione e cerca nuovi dati ogni 0,1 s.*

## Cosa viene registrato {#what-is-recorded}

- la tua posizione a 10 Hz come metri est/alto/nord rispetto all'origine del teatro (dalla latitudine/longitudine/altitudine); lat/lon/alt e i metri del mondo di DCS (dcs_x nord, dcs_y alto, dcs_z est) come colonne
- assetto, velocità indicata e vera, Mach, velocità verticale, angolo d'attacco e di derapata, prua magnetica, AGL e altezza radar, g su tre assi, velocità e velocità di rotazione, in volo, posizione della camera e vettore di direzione, tipo di velivolo
- decolli e atterraggi con l'aeroporto; schianti, eiezioni, morti del pilota
- uccisioni e abbattimenti con entrambi i tipi di unità e l'arma; altri eventi di gioco come forniti
- vite per missione (spawn ... session_end), uccisioni, morti, distanza, altezza massima, g massimo
- ogni riga inviata dall'hook conservata intera in heat.raw.parquet, con un dump al secondo delle tabelle di esportazione del velivolo (motori, carrello e flap, carico, contromisure, rotta, navigazione) e ogni altro callback (pausa, chat, giocatori che entrano, caricamento della missione)

## Da dove arriva {#where-it-comes-from}

l'hook del watcher %USERPROFILE%\Saved Games\DCS\*\Scripts\Hooks\heat3d-watch.lua, righe UDP a 127.0.0.1:41993

## Come attivarlo {#how-to-switch-it-on}

python -m heat3d_watch setup dcs --apply (aggiunge Scripts\Hooks\heat3d-watch.lua), poi riavvia DCS

Scrivi il comando in un terminale aperto nella cartella del watcher (vedi [Prima di iniziare](before-you-start.md)). Se fallisce, l'ultima riga dice il motivo; [Installazione e avvio](installing-and-running.md) descrive le cause più comuni.

`python -m heat3d_watch setup dcs` elenca i file che verrebbero modificati; `python -m heat3d_watch setup dcs --apply` li modifica, tenendo l'originale come `<file>.heat3d-backup` (vedi [Comandi](commands.md#setup)). Stampa `dcs: changed: ...` per ogni modifica, oppure `dcs: nothing to change` quando è già attivo.

## Come funziona {#how-it-works}

DCS World: un piccolo script hook del watcher, che invia righe UDP a 127.0.0.1:41993.

DCS esegue all'avvio i file Lua in `Saved Games\DCS*\Scripts\Hooks\`; un hook può leggere le funzioni di esportazione (`Export.Lo*`) e ricevere i callback della simulazione (`DCS.setUserCallbacks`: onSimulationStart/Frame/Stop, onGameEvent) - vedi `<DCS>\API\DCS_ControlAPI.html` e <https://wiki.hoggitworld.com/view/DCS_Export_Script>. `setup` scrive lì `heat3d-watch.lua` (un file suo: Export.lua e gli hook di altri strumenti non vengono toccati), che invia dieci righe al secondo, più una al secondo, e una per ogni evento di gioco o callback, senza mai aspettare una risposta. La porta è la 41993 così l'hook di JoyPro (41992) e Tacview (42674) continuano a funzionare accanto. Le righe (campi separati da ';'):

```text
hello;v=2                                       l'hook è stato caricato
start;mission=..;map=..;me=<id giocatore>;name=..;mp=0|1;file=..;server=0|1
mis;t=..;date.Day=..;start_time=..;weather...   data, ora di inizio e meteo della missione, appiattiti
p;t=<model s>;x=;y=;z=;lat=;lon=;alt=;hdg=;pitch=;bank=;ias=;agl=;g=;type=;tas=;mach=;vv=;aoa=;aos=;
  mhdg=;ralt=;gx=;gz=;vx=;vy=;vz=;wx=;wy=;wz=;air=;cx=;cy=;cz=;cfx=;cfy=;cfz=
d;t=..;self.Name=..;eng.RPM.left=..;mech.gear.value=..;pay.Stations.1.count=..;...   una volta al secondo
ev;t=..;name=<nome onGameEvent>;args=a|b|c      ogni onGameEvent
cb;t=..;name=<callback>;args=a|b                ogni altro callback (pausa, chat, giocatori, caricamento)
noexport;t=..                                   il server vieta l'esportazione del proprio velivolo
stop;t=..                                       la missione è finita
```

`p` è LoGetSelfData: Position x/y/z - i metri del mondo di DCS, x nord, y alto, z est - più LatLongAlt (gradi, m), Heading/Pitch/Bank (radianti), con LoGetIndicatedAirSpeed (m/s), LoGetAltitudeAboveGroundLevel (m) e LoGetAccelerationUnits() x/y/z (g); e, come li documenta `Scripts\Export.lua`, LoGetTrueAirSpeed (m/s), LoGetMachNumber, LoGetVerticalVelocity (m/s), LoGetAngleOfAttack e LoGetAngleOfSideSlip (rad), LoGetMagneticYaw (rad), LoGetRadarAltimeter (m), LoGetVectorVelocity (m/s nel mondo), LoGetAngularVelocity (rad/s), LoGetInAir, e il punto e il vettore di direzione di LoGetCameraPosition (metri nel mondo). `d` è un dump al secondo di intere tabelle, appiattite in chiavi con il punto: LoGetSelfData (paese, coalizione, nomi di unità e gruppo, livelli del tipo, flag), LoGetEngineInfo, LoGetMechInfo, LoGetPayloadInfo, LoGetSnares, LoGetWingInfo, LoGetVectorWindVelocity, LoGetFMData, LoGetNavigationInfo, LoGetRoute, LoGetMCPState, LoGetControlPanel_HSI, LoGetRadioBeaconsStatus e alcuni numeri (pausa, accelerazione del tempo, sedile, pressione, deviazioni). Il watcher conserva ogni riga intera nel file accessorio grezzo; `p` diventa anche le righe.

Le posizioni vanno nella stessa mappa piatta degli altri simulatori di volo (`Tangent`: x est, y altitudine sul livello del mare, z nord, metri) a partire da LatLongAlt, attorno all'origine fissa del teatro (`THEATRES`, dal `map` della riga di avvio), così ogni missione su un teatro condivide una mappa, e una su cui il visualizzatore può disegnare il mondo reale. Un teatro non presente nella tabella prende la latitudine e la longitudine del primo dato, arrotondate a gradi interi. Le x/y/z proprie di DCS vengono conservate come `dcs_x`, `dcs_y`, `dcs_z`; un dato senza LatLongAlt non può essere posizionato e viene solo contato (`fixes_without_latlon`). L'origine è il `geo` della sessione, in meta.json e nel footer della tabella.

Gli argomenti di onGameEvent, come li fornisce DCS_ControlAPI: takeoff/landing (playerID, unit_missionID, airdromeName), crash/eject/pilot_death (playerID, unit_missionID), kill (killerPlayerID, killerUnitType, killerSide, victimPlayerID, victimUnitType, victimSide, weaponName), self_kill (playerID), change_slot (playerID, slotID, prevSide), mission_end (winner, msg).

Un server multigiocatore può vietare l'esportazione del proprio velivolo (LoIsOwnshipExportAllowed è false); in quel caso non ci sono posizioni, solo eventi, e la sessione lo dice.

## Posizioni e assi {#positions-and-axes}

| | |
|---|---|
| Posizioni registrate | sì |
| Asse verso l'alto | `y` |
| Unità | metri (est, altitudine, nord dall'origine del teatro) |
| Specchiato per il visualizzatore | `z` |
| Scala delle unità (`scale`: il visualizzatore moltiplica le posizioni per questo valore) | 1 |

Questi valori finiscono in `meta.json` (`axes`) di ogni sessione e, quando la sessione ha delle posizioni, nel footer di `heat.parquet`, così il visualizzatore di 3DHeat ruota e scala le righe da solo - vedi [I dati](the-data.md).

## Multigiocatore {#multiplayer}

- Segnato come giocato online (`multiplayer`): **sì**. `games --markdown` lo mostra come "consentito (legge solo ciò che il gioco pubblica)".
- Tipo `telemetry`: legge solo ciò che il gioco o la piattaforma consegna (una porta UDP o una memoria condivisa che il gioco pubblica), quindi registra anche nel gioco online oltre che offline; il flag decide solo se la memoria può mai essere letta.
- Memoria: **mai** letta da questo adattatore. Solo gli adattatori `memory` leggono la memoria, e mai per un gioco segnato come giocato online - vedi [Fonti e regole](sources-and-rules.md).

## Statistiche registrate {#statistics-recorded}

Chiavi statistiche che il codice di questo adattatore imposta per nome (`stats` di ogni sessione in `meta.json` e la tabella `stats` di `watcher.sqlite`):

`airborne_time`, `bad_packets`, `crashes`, `deaths`, `distance_km`, `ejections`, `export_blocked`, `fixes_without_latlon`, `flight_time`, `kills`, `max_altitude_m`, `max_g`, `shot_down`, `{event}s`

Una chiave tra parentesi graffe viene completata durante l'esecuzione (`score.{team}` è una chiave per squadra). Le chiavi che il codice prende da una tabella dei campi del gioco o dai nomi statistici del gioco non sono in questo elenco; "Cosa viene registrato" qui sopra le nomina.

## Completezza {#completeness}

Il watcher segue la [regola del convertitore](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md) di 3DHeat: ciò che la fonte contiene viene letto o conservato, mai scartato. Oltre alle righe, ogni pacchetto, pagina, riga o risposta che l'adattatore riceve viene conservato intero in `heat.raw.parquet` della sessione (colonne `time`, `ms`, `type`, `used`, `payload`, `text`, poi ogni campo conservato per nome; `used` segna ciò che è diventato anche righe), e `selfCheck.completeness` in `meta.json` conta ogni `type` - `lost` è 0.

**Letto**

- `p` (10 Hz): posizione, LatLongAlt, assetto, IAS, AGL, g (x/y/z), tipo di velivolo, e TAS, Mach, velocità verticale, AoA, angolo di derapata, prua magnetica, altezza radar, velocità nel mondo, velocità di rotazione, in volo e punto/direzione della camera dell'hook 2 - tutti come colonne delle righe (unità come le dà Export.lua)
- `start`: missione, teatro, id e nome del proprio giocatore, multigiocatore, file della missione, server; `mis`: data e ora di inizio della missione in meta.json
- `ev`: ogni onGameEvent come riga (takeoff, landing, crash, eject, pilot_death, kill, self_kill, change_slot, connect, disconnect, friendly_fire, mission_end, qualsiasi altro nome come fornito)
- `noexport` e `stop` come righe e in meta.json

**Conservato grezzo**

- ogni riga inviata dall'hook, intera, come `text` sotto il suo tipo: `hello`, `start`, `mis`, `p`, `d`, `ev`, `cb`, `noexport`, `stop`; una riga di qualsiasi altro tipo sotto `unknown`
- `d` (1 Hz, solo grezzo): LoGetSelfData intero (paese, coalizione, nome di unità e gruppo, livelli del tipo, flag), LoGetEngineInfo, LoGetMechInfo, LoGetPayloadInfo, LoGetSnares, LoGetWingInfo, vettore del vento, LoGetFMData, LoGetNavigationInfo, LoGetRoute, LoGetMCPState, HSI, radiofari, pausa, accelerazione del tempo, sedile, pressione, deviazioni - appiattiti in chiavi con il punto
- `mis`: la tabella meteo della missione, appiattita; `cb`: onSimulationPause/Resume, onMissionLoad\*, onNet\*, onPlayerConnect/Disconnect/Start/Stop/ChangeSlot, onChatMessage, onTriggerMessage, onRadioMessage, onRadioCommand, onShowMessage con i loro argomenti

**Non disponibile**

- altre unità (LoGetWorldObjects, LoGetObjectById) e dati dei sensori (LoGetTargetInformation, LoGetLockedTargetInformation, LoGetTWSInfo, LoGetWingTargets, LoGetSightingSystemInfo): non richiesti - ogni oggetto di una missione a 10 Hz è costoso dentro il frame di DCS, e un server li regola (allow_object_export, allow_sensor_export); Tacview li registra
- l'intera tabella della missione (DCS.getCurrentMission contiene ogni unità e trigger, megabyte): vengono inviati solo data, ora di inizio, meteo, sortita, teatro e versione
- i callback onPlayerTry\*: rispondono a DCS (consentire o rifiutare), quindi l'hook non li tocca
- indirizzi e UCID degli altri giocatori: net.get_player_info li dà solo a un server, e non sono dati da conservare
- le voci di una tabella oltre 800 chiavi o 6 livelli di profondità in una riga `d` vengono tagliate, così una riga resta un unico datagramma

**Dimensione**: circa 20 MB all'ora di righe `p` (10 al secondo, circa 500 byte ciascuna con il suo frame) e 15-40 MB di dump `d` (uno al secondo, 4-10 KB a seconda del carico e della rotta del velivolo), prima di zstd; le chiavi ripetute si comprimono circa dieci volte

## Verificato {#verified}

formato delle righe testato con datagrammi sintetici; l'hook Lua non è testato dentro DCS (scritto dall'API hook/export di DCS e dall'elenco delle funzioni Lo\* in `Scripts\Export.lua`, non eseguito)

## Sorgente {#source}

[heat3d_watch/adapters/dcs.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/dcs.py)

<!-- Generated from the adattatore by tools/gen_game_pages.py; change the adattatore and run it again rather than editing this page. -->
