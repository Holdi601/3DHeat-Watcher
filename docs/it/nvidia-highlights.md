---
title: NVIDIA Highlights
nav_order: 8
lang: "it"
source: nvidia-highlights.md
source_hash: "a3b769ab065c"
nav_exclude: true
search_exclude: true
---
# NVIDIA Highlights {#nvidia-highlights}

Alcuni giochi chiedono al driver grafico NVIDIA di salvare un breve video quando succede qualcosa, come un'uccisione.
Il watcher annota ciascuno di questi momenti e, quando può, lo mette sulla mappa dove è avvenuto.

L'adattatore `nvidia-highlights` registra i clip, gli highlight e gli screenshot che l'app NVIDIA (o GeForce Experience) salva, e assegna a ciascuno un luogo sulla mappa quando può. Questa pagina spiega cosa può e cosa non può fornire NVIDIA Highlights, quali file legge il watcher e come un highlight ottiene una posizione. La pagina generata dell'adattatore è [NVIDIA highlights (piattaforma)](game-nvidia-highlights.md).

## Cosa possono e cosa non possono fornire NVIDIA Highlights {#what-nvidia-highlights-can-and-cannot-deliver}

Un gioco che supporta NVIDIA Highlights parla con l'app NVIDIA tramite il GfeSDK di NVIDIA. L'SDK trasporta solo due tipi di messaggio:

1. **Una volta, all'avvio**: i tipi di highlight che il gioco userà - un id (come `kill`), una rilevanza, dei tag e un nome visualizzato per lingua. L'app NVIDIA li memorizza per gioco.
2. **In un momento di gioco**: "highlight `<id>`, da `<ms>` prima di ora a `<ms>` dopo". Questo è tutto il messaggio: l'id di un tipo che il gioco ha registrato, e due scarti temporali che dicono all'app NVIDIA quale tratto della sua registrazione continua tenere.

L'SDK **non ha un campo per nient'altro**: nessuna posizione, nessuna partita o round, nessun avversario, nessuna arma, nessun punteggio, nessun dato personalizzato di alcun tipo. Un gioco non può mettere una posizione in un highlight, anche se lo volesse. Quando il clip viene salvato, l'app NVIDIA aggiunge un file, un nome del gioco, una durata e un orario.

Quindi tutto ciò che un highlight può dire è "questo tipo di momento, in questo gioco, a quest'ora". Tutto il resto deve venire da un'altra parte.

## Cosa legge il watcher {#what-the-watcher-reads}

Tutto viene letto dai file che l'app NVIDIA scrive per la sua galleria. Non si parla mai con il driver o con l'app. La cartella Overlay di NVIDIA è `%LOCALAPPDATA%\NVIDIA Corporation\NVIDIA Overlay`.

| File | Cosa se ne ricava |
|---|---|
| `UGCTracker.json` | l'indice della galleria: ogni clip e screenshot con il suo percorso, tipo (video, immagine), sottotipo (`InstantReplay`, ...), data, nome del profilo del gioco, eseguibile e nome breve, e durata (`msDuration`) |
| `GallerySettings.json` | `settings.currentDirectoryV2`, la cartella di acquisizione, e `settings.tempDirectory`, dove restano in attesa gli highlight (`<temp>\Highlights\<game>`) finché non vengono salvati |
| `Highlights\<game>\config.json` | i tipi di highlight che ogni gioco ha registrato: id, e il nome visualizzato in inglese (oppure l'id, quando il gioco non ne ha dato uno) |
| la cartella di acquisizione (predefinita `%USERPROFILE%\Videos\NVIDIA`) e `<temp>\Highlights` | i file stessi dei clip e degli screenshot (`.mp4`, `.mkv`, `.mov`, `.png`, `.jpg`, `.jpeg`), una cartella per gioco |
| `%LOCALAPPDATA%\NVIDIA Corporation\GfeSDK\<exe>_<pid>.log` | le richieste che i giochi GfeSDK scrivono nel log - le righe `Posted Request HL...` - così un highlight che il gioco ha richiesto viene registrato anche quando non è stato conservato alcun clip. Le richieste di configurazione (`HLConfigure`, `HLGetConfig`, `HLGetUserSettings`, `HLSetDefaultLocale`) vengono saltate. |

Per ogni nuovo elemento l'adattatore scrive una riga: `highlight` per un video, `screenshot` per un'immagine, o `highlight_request` per una riga del log GfeSDK. I suoi campi:

| Campo | Cos'è |
|---|---|
| `ms` | il momento: l'orario nel nome del file (`<Game> 2026.05.01 - 20.31.28.115.DVR.mp4`, l'ora locale in cui il clip è stato salvato), altrimenti la data dell'indice, altrimenti la data di modifica del file |
| `game` | il nome del profilo NVIDIA, il nome della cartella o il gioco dal nome del file |
| `clip`, `media` | il percorso del file; `video`, `image` o `file` |
| `kind` | `InstantReplay`, `Screenshot`, `Highlight` (dalla cartella temporanea degli highlight) oppure il sottotipo dell'indice |
| `duration_s`, `clip_start_ms` | la durata, dall'indice o dall'intestazione del video stesso (`moov/mvhd`, trovata senza leggere il video); il momento in cui il clip inizia |
| `highlight_id`, `highlight_name` | il tipo di highlight, quando qualcosa lo nomina (vedi sotto) |
| `exe` | l'eseguibile del gioco, dall'indice |
| `x`, `y`, `z`, `session`, `position_from`, `position_lag_ms` | la posizione presa in prestito, quando ne è stata trovata una (vedi sotto) |

Le statistiche della sessione sono `clips`, `screenshots`, `clip_seconds` e `placed` (elementi che hanno ottenuto una posizione).

**L'id dell'highlight** non è scritto in nessun punto documentato. L'adattatore prova due modi non documentati: un campo della voce della galleria il cui nome contiene "highlight", e - solo per i file nella cartella temporanea degli highlight - uno degli id registrati dal gioco (lungo almeno 4 caratteri) che compare nel nome del file. Un clip salvato prende il nome dal gioco, che potrebbe contenere per caso un id come "kill", quindi il suo nome non viene cercato. Questi due modi non si sono ancora visti funzionare su una macchina reale: nessun clip con un id di highlight, e nessuna riga di richiesta GfeSDK, si è presentato dove l'adattatore è stato testato. L'indice della galleria, le impostazioni, le definizioni degli highlight e i clip sono stati testati su file reali.

### Quando vengono registrati gli elementi {#when-items-are-recorded}

- Un clip continua a essere scritto per un po' dopo la pressione del tasto. L'adattatore aspetta che un file abbia la stessa dimensione e lo stesso orario in due controlli (ogni 10 s) e che abbia almeno 5 s.
- La prima volta che l'adattatore viene eseguito, tutto ciò che è già nella galleria e nei log viene solo annotato, non registrato, così anni di vecchi clip non riempiono le statistiche. Ciò che ha visto viene conservato in `<data>\state\nvidia-highlights.json`, così un riavvio non registra nulla due volte.
- Gli elementi vengono raggruppati in una sessione per gioco. La sessione di un gioco si chiude dopo 30 minuti senza un nuovo elemento, e finisce al suo ultimo momento invece che alla chiusura del gioco. I momenti distanti più di 30 minuti vanno in sessioni separate.

## Come un highlight ottiene una posizione {#how-a-highlight-gets-a-position}

L'highlight in sé non ha un luogo. L'adattatore cerca il momento nelle altre registrazioni che il watcher ha fatto dello stesso gioco nello stesso tempo:

1. **Lo stesso gioco**: le cartelle di sessione sotto `<data>\sessions\` il cui nome di gioco corrisponde a quello dell'highlight. I nomi vengono confrontati in minuscolo, solo lettere e cifre. Corrispondono quando sono uguali, oppure quando il più corto ha almeno 5 caratteri ed è contenuto nel più lungo (`Counter-Strike 2` e `Counter-Strike-2`).
2. **Lo stesso momento**: le sessioni il cui inizio e fine (da `meta.json`, con un secondo di margine a entrambi i lati) coprono il momento. Le sessioni finite senza posizioni, e le sessioni dell'adattatore stesso, vengono saltate.
3. **La riga propria del giocatore**: nel suo `events.jsonl`, l'ultima delle righe proprie del giocatore con una posizione, al momento o prima, e non più di 5 secondi prima. Una riga è propria quando la sua fonte lo dice: `"player": "me"`, oppure `"own_car": 1` (giochi di gara che registrano ogni auto per il suo pilota), oppure un `player` che è il `player` della sessione in `meta.json` (il nome che la fonte dà al giocatore). Vedi [Le righe proprie del giocatore](the-data.md#the-players-own-rows).

Se viene trovata una riga, l'highlight riceve i suoi `x`, `y`, `z`, la sua `session` (o il nome della cartella), `position_from` (la cartella da cui arriva) e `position_lag_ms` (quanto prima del momento era quella riga). La sessione dell'highlight prende gli assi di quella registrazione, così viene disegnata nello stesso verso. Se non viene trovata alcuna riga, l'highlight resta un momento sulla linea del tempo senza un luogo.

Cose da sapere sulla posizione presa in prestito:

- **È dove eri quando il clip è stato salvato**, non dove è iniziata l'azione. Il momento è l'orario di salvataggio nel nome del file, che per un Instant Replay è la sua fine. `clip_start_ms` dice quando inizia il clip.
- **Un altro adattatore deve aver registrato lo stesso gioco nello stesso periodo.** Quelli che segnano le righe proprie del giocatore, e quindi possono collocare un highlight: la game-state integration di Counter-Strike 2 e Dota 2, Forza, i giochi Assetto Corsa, EA SPORTS WRC, DiRT Rally 2.0, Richard Burns Rally, BeamNG.drive, Euro Truck Simulator 2, American Truck Simulator, DCS World, X-Plane, Microsoft Flight Simulator, War Thunder, Minecraft e i profili di memoria (come `me`); F1 23/24/25, RaceRoom, Automobilista 2 e Project CARS 2 (le righe della tua auto portano `own_car` 1, secondo l'indice dell'auto del giocatore nel gioco, il suo slot o il partecipante visualizzato); Elite Dangerous (il nome del comandante, in `meta.json` come `player`, perché il giornale è sempre quello del giocatore).
- **Un replay viene convertito dopo la partita**, quindi può collocare solo un clip che viene cercato dopo la conversione: il clip viene collocato quando viene registrato, e un replay salvato più tardi non viene ricontrollato. I replay di League of Legends assegnano le loro righe al Riot ID delle impostazioni e, con una chiave API Riot, danno loro l'orario reale indicato dalla timeline della partita, così vengono trovati allora. Un demo di CS2 non può collocare affatto un highlight: le sue posizioni sono nella tabella del convertitore, non in `events.jsonl`, e un demo ha i tick del gioco ma nessun orario reale con cui confrontare il momento di un clip.
- In Rocket League le uniche righe con un luogo sono gli eventi della palla. Un colpo alla palla da parte tua è una riga tua, quindi un highlight può essere collocato dove hai colpito la palla per ultimo.
- I giochi senza alcuna fonte posizionale (Overwatch 2, Call of Duty, Hunt: Showdown, ...) tengono i loro highlight come una linea del tempo di momenti.

## Perché la memoria non può dare una posizione nel multigiocatore {#why-memory-cannot-give-a-position-in-multiplayer}

L'altro modo per ottenere una posizione sarebbe leggerla dalla memoria. Nessuna delle due memorie funziona:

- **La memoria di NVIDIA non contiene alcuna posizione.** L'app NVIDIA riceve ciò che il GfeSDK trasporta - un id di highlight e due scarti temporali - più il video che registra. Non c'è nessuna posizione da leggere dal lato di NVIDIA. (Il watcher comunque non legge la memoria di NVIDIA; legge i file sopra.)
- **La memoria del gioco è fuori dai limiti nel multigiocatore.** La posizione è nel processo del gioco, ma il watcher non legge mai la memoria di un gioco multigiocatore: un adattatore di memoria per un gioco segnato come giocato online viene rifiutato prima ancora che venga aperto qualcosa (vedi [Lettura della memoria](memory-reading.md)). I giochi multigiocatore girano sotto anti-cheat (Easy Anti-Cheat, BattlEye, Vanguard, ...) che trattano un altro programma che apre il processo del gioco come un imbroglio, cosa che può far bannare l'account. Leggere lo stato del gioco dall'esterno è anche ciò che i termini dei giochi vietano. Un highlight in un gioco multigiocatore riceve quindi un luogo solo da ciò che il gioco pubblica: la sua game-state integration o la sua telemetria, registrate da un altro adattatore nello stesso momento.
