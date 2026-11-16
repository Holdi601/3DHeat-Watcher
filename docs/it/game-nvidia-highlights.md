---
title: "NVIDIA highlights (piattaforma)"
nav_order: 34
lang: "it"
source: game-nvidia-highlights.md
source_hash: "5d45211c0e37"
nav_exclude: true
search_exclude: true
---
# NVIDIA highlights (piattaforma) {#nvidia-highlights-platform}

Il watcher salva ciò che NVIDIA highlights conserva dei tuoi giochi, così puoi guardare la tua cronologia più tardi su una mappa nel visualizzatore 3DHeat.

*Dettagli tecnici: adattatore `nvidia-highlights`, tipo [`platform`](sources-and-rules.md); funziona sempre (non aspetta che un gioco si avvii) e cerca nuovi dati ogni 10 s.*

## Cosa viene registrato {#what-is-recorded}

- ogni nuova clip, highlight o screenshot: gioco, file, tipo, durata e il momento (ms dell'orologio)
- l'id e il nome dell'highlight quando il gioco l'ha registrato presso NVIDIA
- dove si trovava il giocatore in quel momento, quando un altro adattatore ha registrato lo stesso gioco in quel momento
- le richieste di highlight dei giochi che usano GfeSDK, anche quando non viene conservata alcuna clip

## Da dove arriva {#where-it-comes-from}

%LOCALAPPDATA%\NVIDIA Corporation\NVIDIA Overlay\UGCTracker.json, GallerySettings.json, Highlights\\&lt;gioco&gt;\config.json; le clip nella cartella di cattura (%USERPROFILE%\Videos\NVIDIA\\&lt;Gioco&gt;\\\*.mp4) e &lt;temp&gt;\Highlights\\&lt;gioco&gt;; %LOCALAPPDATA%\NVIDIA Corporation\GfeSDK\\&lt;exe&gt;_&lt;pid&gt;.log

## Come attivarlo {#how-to-switch-it-on}

App NVIDIA: Instant Replay o Highlights attivati, clip salvate con un tasto rapido o dal gioco

## Come funziona {#how-it-works}

Ciò che il launcher e il driver della scheda grafica conservano della tua attività: statistiche di Steam,
obiettivi, tempo di gioco e timeline, e highlights e clip di NVIDIA.

Nessuna di queste fonti richiede che un gioco collabori o sia in esecuzione, quindi i tre
adattatori qui sono sempre attivi e guardano pochi file ogni pochi secondi.

#### Highlights e clip NVIDIA (`nvidia-highlights`) {#nvidia-highlights-and-clips-nvidia-highlights}

Ciò che conservano NVIDIA App / GeForce Experience, tutto sotto
`%LOCALAPPDATA%\NVIDIA Corporation\NVIDIA Overlay`:
```text
UGCTracker.json      l'indice della galleria: {"UGC": [{id, path, type (video,
                     image), subType (InstantReplay, Normal, ...), date
                     (UTC, quando il file è stato scritto), profileName, drsName
                     (l'exe), shortName, msDuration, ...}], "apps", "info"}
GallerySettings.json settings.currentDirectoryV2 (dove vengono salvate le clip),
                     settings.tempDirectory (gli highlight attendono in
                     <temp>\Highlights\<gioco> finché non vengono salvati)
Highlights\<gioco>\config.json  i tipi di highlight che un gioco ha registrato:
                     {"highlights": {id: {significance, highlightTags,
                     name: {locale: text}}}, profileName, drsName, shortName}
```
e i file delle clip stesse, `<cartella di cattura>\<Gioco>\<Gioco> yyyy.mm.dd -
hh.mm.ss.ff.DVR.mp4` (screenshot: `<Gioco> Screenshot yyyy.mm.dd - ...png`), e l'ora nel nome
è l'ora locale in cui la clip è stata salvata. I giochi GfeSDK registrano anche le loro chiamate di highlight in
`%LOCALAPPDATA%\NVIDIA Corporation\GfeSDK\<exe>_<pid>.log`.

Cosa può e non può dare questo: un gioco che supporta NVIDIA Highlights
(GfeSDK) registra i tipi di highlight una volta - un id come "kill", una
significance, dei tag, un nome da mostrare - e poi dice solo "highlight <id>,
da <ms> prima di adesso a <ms> dopo". Non ci sono posizioni, nessuna partita o round, nessun avversario, nessun dato
personalizzato: l'SDK non ha un campo per nulla di ciò. Una clip salvata aggiunge
un file, un nome di gioco, una durata e un orario. Quindi ciò che viene registrato è "questo tipo di
momento, in questo gioco, a quest'ora" - e un luogo solo cercando l'ora nella registrazione di un altro
adattatore dello stesso gioco (`position_at`), cosa che questo adattatore fa per ogni clip che registra.
<https://developer.nvidia.com/highlights>

Ogni adattatore conserva ciò che ha già visto in `<dati>\state\<id>.json`, quindi un riavvio
non registra nulla due volte.

Ogni sessione conserva anche, intero, ciò da cui provengono le sue righe (regola del convertitore di 3DHeat,
docs/converters.md nel repository del visualizzatore), in `heat.raw.parquet`:
i byte del file delle statistiche e del suo schema e il blocco localconfig del gioco
(steam-stats; un file di statistiche che il decodificatore non sa leggere produce una sessione con i soli
byte), i byte del file della timeline e ogni voce come JSON (steam-timeline),
la voce di indice di ogni clip della galleria, le definizioni di highlight del gioco e ogni riga di log GfeSDK
(nvidia-highlights), anche quelle che non sono richieste di highlight.

Lo stesso modulo serve anche: [Statistiche Steam (piattaforma)](game-steam-stats.md), [Steam Timeline (piattaforma)](game-steam-timeline.md).

## Posizioni e assi {#positions-and-axes}

| | |
|---|---|
| Posizioni registrate | solo prese in prestito: il luogo che un'altra registrazione dello stesso gioco ha per quel momento |
| Asse verticale | `y` |
| Unità | metri |
| Specchiato per il visualizzatore | nessuno |
| Scala delle unità (`scale`: il visualizzatore moltiplica le posizioni per questo valore) | 1 |

Questi valori finiscono in `meta.json` di ogni sessione (`axes`) e, quando la sessione ha posizioni, nel footer di `heat.parquet`, così il visualizzatore 3DHeat ruota e scala le righe da solo - vedi [I dati](the-data.md).

## Multigiocatore {#multiplayer}

- Segnato come giocato online (`multiplayer`): **no**. `games --markdown` lo mostra come "giocatore singolo".
- Tipo `platform`: legge solo ciò che il gioco o la piattaforma consegna (ciò che Steam o il driver della scheda grafica conservano), quindi registra anche nel gioco online oltre che offline; il flag decide solo se la memoria può mai essere letta.
- Memoria: **mai** letta da questo adattatore. Solo gli adattatori `memory` leggono la memoria, e mai per un gioco segnato come giocato online - vedi [Fonti e regole](sources-and-rules.md).

## Statistiche registrate {#statistics-recorded}

Chiavi di statistica che il codice di questo adattatore imposta per nome (`stats` di ogni sessione in `meta.json` e la tabella `stats` di `watcher.sqlite`):

`clip_seconds`, `clips`, `placed`, `screenshots`

Una chiave tra parentesi graffe viene completata durante l'esecuzione (`score.{team}` è una chiave per squadra). Le chiavi che il codice prende da una tabella dei campi del gioco o dai nomi di statistica del gioco non sono in questo elenco; "Cosa viene registrato" sopra le nomina.

## Completezza {#completeness}

Il watcher segue la [regola del convertitore](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md) di 3DHeat: ciò che la fonte contiene viene letto o conservato, mai scartato. Oltre alle righe, ogni pacchetto, pagina, riga o risposta che l'adattatore riceve viene conservato intero in `heat.raw.parquet` della sessione (colonne `time`, `ms`, `type`, `used`, `payload`, `text`, poi ogni campo conservato per nome; `used` segna ciò che è diventato anche riga), e `selfCheck.completeness` in `meta.json` conta ogni `type` - `lost` è 0.

**Letto**

- ogni nuova clip e screenshot: gioco, file, tipo, supporto, durata (indice, altrimenti l'intestazione MP4), il momento dal nome del file, l'id e il nome dell'highlight dove il gioco li ha registrati, e il posto del giocatore in quel momento da una registrazione di un altro adattatore
- richieste di highlight GfeSDK (ogni `Posted Request HL...` tranne le chiamate di configurazione) con il loro orario

**Conservato grezzo**

- `UGC`: la voce intera della clip nell'indice della galleria UGCTracker.json, ogni campo che NVIDIA scrive
- `clip_file`: per una clip che l'indice non elenca, il percorso del file, la dimensione, l'ora e la cartella
- `highlights_config`: `Highlights\<gioco>\config.json` del gioco così com'è scritto (significance, tag, nomi in ogni lingua), una volta per sessione
- `gfesdk_log`: ogni riga dei log GfeSDK letti dopo la prima esecuzione, `used` vero per le richieste di highlight e falso per il resto (configurazione, impostazioni video, i messaggi dell'SDK stesso)

**Non disponibile**

- le clip e gli screenshot stessi: video e immagini restano dove NVIDIA li ha salvati; le righe ne indicano il file
- ciò che c'era prima della prima esecuzione dell'adattatore: considerato già visto, così anni di clip non diventano sessioni in un colpo solo (`baseline`; False le registra)
- `apps` e `info` di UGCTracker.json e GallerySettings.json: le impostazioni dell'app, non momenti di gioco; si usa la cartella di cattura che indicano
- posizioni, round, avversari: la GfeSDK non ha campi per loro

**Dimensione**: circa 1 KB per clip e qualche KB di definizioni e righe di log per avvio di gioco: ben sotto 1 MB all'ora

## Verificato {#verified}

testato su un vero indice della galleria, impostazioni, definizioni di highlight e clip di un'installazione locale; le righe di richiesta di highlight GfeSDK e gli id degli highlight nelle clip non sono ancora testati

## Fonte {#source}

[heat3d_watch/adapters/platform.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/platform.py)

<!-- Generated from the adattatore by tools/gen_game_pages.py; change the adattatore and run it again rather than editing this page. -->
