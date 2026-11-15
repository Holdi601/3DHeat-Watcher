---
title: "Star Citizen (file di log)"
nav_order: 42
lang: "it"
source: game-starcitizen.md
source_hash: "6528f948d2e5"
nav_exclude: true
search_exclude: true
---
# Star Citizen (file di log) {#star-citizen-log-files}

Mentre giochi a Star Citizen, il watcher legge i file che il gioco scrive e salva ciò che è successo, così puoi guardarlo più tardi come statistiche e una timeline.

*Dettagli tecnici: adattatore `starcitizen`, tipo [`log`](sources-and-rules.md); funziona mentre `StarCitizen.exe` è in esecuzione e cerca nuovi dati ogni 0,5 s.*

## Cosa viene registrato {#what-is-recorded}

- morti con vittima, uccisore, arma, tipo di danno e zona (giocatori e NPC)
- veicoli messi fuori uso e distrutti, con pilota, causa e zona
- destinazioni dei viaggi quantistici, cambi di sistema solare, comparse, rinascite, incapacitazioni
- ogni riga di Game.log intera in heat.raw.parquet
- uccisioni (giocatori e NPC), morti, suicidi, veicoli distrutti e persi, salti quantistici

## Da dove arriva {#where-it-comes-from}

&lt;installazione&gt;\StarCitizen\LIVE\Game.log (la cartella di build dell'eseguibile StarCitizen.exe in esecuzione), solo il file di log che scrive il gioco - un gioco con Easy Anti-Cheat: niente tocca il suo processo

## Come attivarlo {#how-to-switch-it-on}

Non serve attivare nulla: il watcher legge la fonte così come il gioco o la piattaforma la fornisce.

## Come funziona {#how-it-works}

Star Citizen: il log del client, `<installazione>\StarCitizen\LIVE\Game.log`.

Il gioco riscrive Game.log da zero a ogni avvio (quello precedente va in
`logbackups\`). Viene letto solo quel file: Star Citizen usa Easy Anti-Cheat, e
nulla qui si avvicina al processo del gioco. Le righe iniziano con una data UTC e
un livello, poi un tag tra parentesi angolari:

```text
<2025-04-13T17:17:51.279Z> [Notice] <Actor Death> CActor::Kill: 'Victim' [200146297631] in zone
    'ANVL_Hornet_F7A_Mk2_2677329226210' killed by 'Killer' [202061381370] using
    'GATS_BallisticGatling_S3_2677329225797' [Class unknown] with damage type 'VehicleDestruction'
    from direction x: 0.000000, y: 0.000000, z: 0.000000 [Team_ActorTech][Actor]
<...> [Notice] <Vehicle Destruction> CVehicle::OnAdvanceDestroyLevel: Vehicle 'ANVL_Arrow_123' [123] in zone
    'OOC_Stanton_1_Hurston' [pos x: 1.0, y: 2.0, z: 3.0 vel x: 0, y: 0, z: 0] driven by 'Driver' [456]
    advanced from destroy level 0 to 2 caused by 'Attacker' [789] with 'Combat' [Team_VehicleFeatures][Vehicle]
<...> [Notice] <AccountLoginCharacterStatus_Character> Character: createdAt 1 - updatedAt 2 - geid 3 -
    accountId 4 - name Handle - state STATE_CURRENT [Team_GameServices][Login]
<...> [Notice] <Quantum Navtarget> CSCItemQuantumDrive::RmMulticastOnQTToPoint : Local client user
    Handle[200000000001] received QT data for Entity:AEGS_Gladius_123[123] to Target Stanton1b ...
<...> [Notice] <Changing Solar System> ... Client entity Handle ... changing system from Stanton to Pyro ...
```

(qui andate a capo; nel file ogni riga sta su una sola linea). La zona di una morte è di solito
la nave su cui sedeva la vittima, non un luogo. Il formato non è documentato da Cloud
Imperium e cambia tra una patch e l'altra; i pattern seguono le righe che leggono i tracker di
uccisioni della comunità (ad es. <https://github.com/DimmaDont/all-slain>, MIT - solo
fatti), e ciò che non corrisponde viene saltato, non indovinato. La `pos` di un veicolo è relativa
alla zona e viene conservata solo come testo: nessuna coordinata viene disegnata.

Ogni riga viene conservata intera nei dati grezzi della sessione (regola del convertitore di
3DHeat), corrisponda o no: `type` è il tag della riga tra parentesi angolari (`Actor
Death`, `Spawn Flow`, ...), altrimenti la sua prima parola tra parentesi (`Notice`,
`CSessionManager::OnClientSpawned`), altrimenti `untagged`; una riga senza data è `untimed`.

## Posizioni e assi {#positions-and-axes}

| | |
|---|---|
| Posizioni registrate | no |
| Asse verticale | `y` |
| Unità | nessuna posizione registrata |
| Specchiato per il visualizzatore | nessuno |
| Scala delle unità (`scale`: il visualizzatore moltiplica le posizioni per questo valore) | 1 |

Questi valori finiscono in `meta.json` di ogni sessione (`axes`) e, quando la sessione ha posizioni, nel footer di `heat.parquet`, così il visualizzatore 3DHeat ruota e scala le righe da solo - vedi [I dati](the-data.md).

## Multigiocatore {#multiplayer}

- Segnato come giocato online (`multiplayer`): **sì**. `games --markdown` lo mostra come "consentito (legge solo ciò che il gioco pubblica)".
- Tipo `log`: legge solo ciò che il gioco o la piattaforma consegna (file che il gioco scrive mentre è in esecuzione), quindi registra anche nel gioco online oltre che offline; il flag decide solo se la memoria può mai essere letta.
- Memoria: **mai** letta da questo adattatore. Solo gli adattatori `memory` leggono la memoria, e mai per un gioco segnato come giocato online - vedi [Fonti e regole](sources-and-rules.md).

## Statistiche registrate {#statistics-recorded}

Chiavi di statistica che il codice di questo adattatore imposta per nome (`stats` di ogni sessione in `meta.json` e la tabella `stats` di `watcher.sqlite`):

`bad_lines`, `deaths`, `incapacitations`, `kills`, `npc_kills`, `player_kills`, `quantum_jumps`, `suicides`, `system_jumps`, `vehicles_destroyed`, `vehicles_lost`

Una chiave tra parentesi graffe viene completata durante l'esecuzione (`score.{team}` è una chiave per squadra). Le chiavi che il codice prende da una tabella dei campi del gioco o dai nomi di statistica del gioco non sono in questo elenco; "Cosa viene registrato" sopra le nomina.

## Completezza {#completeness}

Il watcher segue la [regola del convertitore](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md) di 3DHeat: ciò che la fonte contiene viene letto o conservato, mai scartato. Oltre alle righe, ogni pacchetto, pagina, riga o risposta che l'adattatore riceve viene conservato intero in `heat.raw.parquet` della sessione (colonne `time`, `ms`, `type`, `used`, `payload`, `text`, poi ogni campo conservato per nome; `used` segna ciò che è diventato anche riga), e `selfCheck.completeness` in `meta.json` conta ogni `type` - `lost` è 0.

**Letto**

- `<Actor Death>`: vittima, uccisore, arma e sua classe, tipo di danno, zona; NPC o giocatore
- `<Vehicle Destruction>`: veicolo, zona, posizione relativa alla zona come testo, pilota, causa, modo, livello di distruzione
- `<Quantum Navtarget>` destinazioni, `<Changing Solar System>`, `OnClientSpawned`, rinascite negli ospedali, incapacitazioni con le loro cause, `EndSession`
- l'handle del giocatore da `<AccountLoginCharacterStatus_Character>` o dalla riga di accesso

**Conservato grezzo**

- ogni riga di Game.log intera, `type` = il suo tag tra parentesi angolari (`Actor Death`, `Vehicle Destruction`, `Spawn Flow`, `Jump Drive State Changed`, `SHUDEvent_OnNotification`, `RequestLocationInventory`, ...), altrimenti la sua prima parola tra parentesi (`Notice`, `CSessionManager::OnClientSpawned`, ...), altrimenti `untagged`; le righe senza data (l'intestazione del log, il testo a capo) come `untimed`; `used` dove la riga è diventata una riga

**Non disponibile**

- posizioni: il log non ne dà in un fotogramma che si possa disegnare (la `pos` di un veicolo distrutto è relativa a una zona il cui luogo non viene registrato)
- tutto ciò che viene dal processo o dalla rete del gioco: Star Citizen usa Easy Anti-Cheat; si legge solo il file di log
- i log dei precedenti avvii (`logbackups`): il Game.log di ogni avvio viene conservato quando viene giocato
- righe in un formato che una patch cambia: conservate grezze, decodificate di nuovo quando si conosce la nuova forma

**Dimensione**: Game.log cresce di circa 5-15 MB all'ora di gioco (di più in zone affollate e con errori); zstd in heat.raw.parquet lo riduce a circa un decimo

## Verificato {#verified}

testato su righe sintetiche di Game.log nel formato documentato dai tracker della comunità; non ancora testato con il gioco

## Fonte {#source}

[heat3d_watch/adapters/starcitizen.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/starcitizen.py)

<!-- Generated from the adattatore by tools/gen_game_pages.py; change the adattatore and run it again rather than editing this page. -->
