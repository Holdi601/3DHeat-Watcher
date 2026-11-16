---
title: "Elite Dangerous (file di log)"
nav_order: 18
lang: "it"
source: game-elite.md
source_hash: "bb5bcf75553a"
nav_exclude: true
search_exclude: true
---
# Elite Dangerous (file di log) {#elite-dangerous-log-files}

Mentre giochi a Elite Dangerous, il watcher legge i file che il gioco scrive e salva ciò che è successo, così puoi guardarlo più tardi su una mappa nel visualizzatore 3DHeat.

*Dettagli tecnici: adattatore `elite`, tipo [`log`](sources-and-rules.md); gira mentre `EliteDangerous64.exe` è in esecuzione e cerca nuovi dati ogni 0,25 s.*

## Cosa viene registrato {#what-is-recorded}

- ogni evento del giornale, sotto il suo nome nel giornale, con i suoi campi semplici
- posizione galattica (StarPos, anni luce) a salti, località, spawn, morti, attracchi, atterraggi
- spawn su LoadGame/Resurrect, morte su Died, attracco/sgancio, touchdown/liftoff, salto, session_end
- percorso di superficie di un pianeta da Status.json: latitudine, longitudine, altitudine, direzione, e metri in un piano tangente per corpo celeste (sessione = nome del corpo), con gli altri campi semplici di Status.json (Flags, Flags2, GuiFocus, LegalState, ...)
- ogni riga del giornale e ogni file di supporto intero in heat.raw.parquet
- salti, distanza percorsa con i salti, morti, uccisioni, crediti guadagnati, missioni completate, corpi scansionati, sistemi visitati, attracchi, atterraggi

## Da dove arriva {#where-it-comes-from}

Journal del giocatore %USERPROFILE%\Saved Games\Frontier Developments\Elite Dangerous\Journal.\*.log (il file più recente, seguito mentre viene scritto), Status.json e gli altri file di supporto \*.json (Market, Outfitting, Shipyard, NavRoute, Cargo, ModulesInfo, ShipLocker, Backpack, FCMaterials) nella stessa cartella

## Come attivarlo {#how-to-switch-it-on}

Non serve attivare nulla: il watcher legge la fonte così come il gioco o la piattaforma la fornisce.

## Come funziona {#how-it-works}

Elite Dangerous: il Player Journal e Status.json che il gioco scrive mentre è in esecuzione.

Dove: `%USERPROFILE%\Saved Games\Frontier Developments\Elite Dangerous\`

* `Journal.<yyyy-mm-ddThhmmss>.<part>.log` - un oggetto JSON per riga, un file per ogni avvio (una sessione lunga continua nella parte .02, .03 ...). Ogni riga
  ha `timestamp` (UTC, ISO 8601) ed `event`. Le posizioni galattiche sono il
  `StarPos` [x, y, z] del sistema, in anni luce da Sol, su `FSDJump`,
  `Location` e `CarrierJump`. Il sistema galattico di Elite ha y in alto (verso
  il nord galattico), z verso il nucleo galattico e x verso la longitudine galattica
  270: un sistema mancino, quindi il visualizzatore specchia z per disegnarlo nel verso giusto.
* `Status.json` - riscritto per intero ogni volta che cambia lo stato della nave: `Flags`,
  e vicino a un pianeta `Latitude`, `Longitude` (gradi), `Altitude` (metri),
  `Heading`, `BodyName` e `PlanetRadius` (metri).
* Gli altri file di supporto, ognuno riscritto per intero quando viene scritto il
  corrispondente evento del giornale: `Market.json`, `Outfitting.json`, `Shipyard.json`,
  `NavRoute.json`, `Cargo.json`, `ModulesInfo.json`, `ShipLocker.json`,
  `Backpack.json`, `FCMaterials.json`. Ogni `*.json` della cartella che il gioco scrive in questa sessione
  viene conservato intero ogni volta che cambia (regola del convertitore di 3DHeat:
  ciò che la fonte contiene viene letto o conservato), sotto il suo nome di file.

Ogni riga del giornale viene conservata intera nel file accessorio grezzo della sessione
sotto il suo `event`, ogni file di supporto sotto il suo nome di file; una riga che non è JSON
sotto `unparsed`.

Le posizioni di superficie vengono messe in un piano tangente locale per corpo, in metri: il
primo rilevamento su un corpo è la sua origine, x verso est, z verso nord, y in alto (altitudine), con la stessa
lateralità del sistema galattico, e le righe portano il nome del corpo come
`session`, così una guida o una camminata su un pianeta si disegna come un percorso a sé. Le righe
galattiche hanno sessione "galaxy". Le due scale stanno in una sola tabella; scegli la
sessione nel visualizzatore.

Formato: manuale "Elite Dangerous Player Journal" di Frontier (pubblicato a ogni
aggiornamento sui forum ufficiali, <https://forums.frontier.co.uk/> - "Journal Manual",
v4.x), eventi e campi come documentati lì; i flag di Status.json secondo il capitolo "Status File"
dello stesso manuale.

## Posizioni e assi {#positions-and-axes}

| | |
|---|---|
| Posizioni registrate | sì |
| Asse verticale | `y` |
| Unità | anni luce (righe galattiche, sessione 'galaxy'); metri est/alto/nord dal primo rilevamento su un corpo (righe di superficie, sessione = nome del corpo) |
| Specchiato per il visualizzatore | `z` |
| Scala delle unità (`scale`: il visualizzatore moltiplica le posizioni per questo valore) | 1 |

Questi valori finiscono in `meta.json` di ogni sessione (`axes`) e, quando la sessione ha posizioni, nel footer di `heat.parquet`, così il visualizzatore 3DHeat ruota e scala le righe da solo: vedi [I dati](the-data.md).

## Multigiocatore {#multiplayer}

- Segnato come giocato online (`multiplayer`): **sì**. `games --markdown` lo mostra come "consentito (legge solo ciò che il gioco pubblica)".
- Tipo `log`: legge solo ciò che il gioco o la piattaforma rende disponibile (file che il gioco scrive mentre è in esecuzione), quindi registra anche nel gioco online oltre che offline; il flag decide solo se la memoria può mai essere letta.
- Memoria: **mai** letta da questo adattatore. Solo gli adattatori `memory` leggono la memoria, e mai per un gioco segnato come giocato online: vedi [Fonti e regole](sources-and-rules.md).

## Statistiche registrate {#statistics-recorded}

Chiavi statistiche che il codice di questo adattatore imposta per nome (`stats` di ogni sessione in `meta.json` e la tabella `stats` di `watcher.sqlite`):

`bad_lines`, `bodies_scanned`, `carrier_jumps`, `credits`, `credits_earned`, `deaths`, `distance_ly`, `dockings`, `jumps`, `kills`, `landings`, `missions_completed`, `ship`, `surface_fixes`, `systems_visited`

Una chiave tra parentesi graffe viene completata durante l'esecuzione (`score.{team}` è una chiave per ogni squadra). Le chiavi che il codice prende da una tabella dei campi del gioco o dai nomi statistici del gioco non sono in questo elenco; "Cosa viene registrato" sopra le nomina.

## Completezza {#completeness}

Il watcher segue la [regola del convertitore](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md) di 3DHeat: ciò che la fonte contiene viene letto o conservato, mai scartato. Oltre alle righe, ogni pacchetto, pagina, riga o risposta che l'adattatore riceve viene conservato intero in `heat.raw.parquet` della sessione (colonne `time`, `ms`, `type`, `used`, `payload`, `text`, poi ogni campo conservato per nome; `used` segna ciò che è diventato anche riga), e `selfCheck.completeness` in `meta.json` conta ogni `type`: `lost` è 0.

**Letto**

- ogni riga del giornale come riga sotto il suo `event`, con i suoi campi semplici (il testo localizzato dove il gioco ne dà uno; testi più lunghi di 300 caratteri vengono tagliati nella riga)
- righe galattiche (StarPos) su FSDJump, CarrierJump, Location, LoadGame, Resurrect, Died, Docked, Undocked, Touchdown, Liftoff, Shutdown; righe di superficie da Status.json e Touchdown/Liftoff
- i campi semplici di Status.json (Flags, Flags2, GuiFocus, LegalState, Cargo, FireGroup, Oxygen, Health, Temperature, Gravity, SelectedWeapon, ...) sulle righe di superficie
- le statistiche: salti, distanza, morti, uccisioni, crediti guadagnati, missioni, corpi scansionati, sistemi visitati, attracchi, atterraggi

**Conservato grezzo**

- ogni riga del giornale intera, `type` = il suo `event` (FSDJump, Scan, Music, ReceiveText, ...), `used` vero: le liste e gli oggetti che le righe lasciano fuori (StarPos, Factions, Rewards, Killers, Materials, Modules, ...) sono solo qui
- una riga del giornale che non è JSON, `type` `unparsed`
- ogni file di supporto intero ogni volta che il gioco lo riscrive, `type` = il suo nome di file: `Status.json` (`used` quando ha creato una riga di superficie), `Market.json`, `Outfitting.json`, `Shipyard.json`, `NavRoute.json`, `Cargo.json`, `ModulesInfo.json`, `ShipLocker.json`, `Backpack.json`, `FCMaterials.json`, e ogni altro `*.json` che il gioco scrive lì

**Non disponibile**

- posizione tra un salto e l'altro (dentro un sistema, in supercrociera o nello spazio normale): il gioco scrive solo lo StarPos del sistema e, vicino a un pianeta, latitudine, longitudine e altitudine
- posizioni di altre navi e di altri giocatori: il giornale è il resoconto del solo comandante
- velocità, acceleratore e altra telemetria di volo: il gioco non le scrive
- giornale e file di supporto delle sessioni precedenti: conservati quando sono stati giocati (il lettore parte dalla fine di un file più vecchio di questa esecuzione del gioco)
- l'API web companion di Frontier (cAPI): richiede l'accesso con l'account Frontier del giocatore; non è un file che il gioco scrive

**Dimensione**: circa 1-5 MB di testo grezzo all'ora: il giornale 0,2-2 MB, Status.json (sotto 1 KB, riscritto fino a ogni secondo) 1-2 MB, un insieme market/outfitting/shipyard 20-150 KB per ogni stazione visitata; zstd in heat.raw.parquet lo riduce a circa un decimo

## Verificato {#verified}

parser riprodotto su file di giornale reali di un'installazione locale (i conteggi degli eventi corrispondono alle statistiche); i rilevamenti di superficie di Status.json testati solo su istantanee sintetiche

## Fonte {#source}

[heat3d_watch/adapters/elite.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/elite.py)

<!-- Generated from the adattatore by tools/gen_game_pages.py; change the adattatore and run it again rather than editing this page. -->
