---
title: I dati
nav_order: 5
lang: "it"
source: the-data.md
source_hash: "6150cdc022fc"
nav_exclude: true
search_exclude: true
---
# I dati {#the-data}

Tutte le registrazioni sono file semplici nella cartella dei dati (`%LOCALAPPDATA%\3DHeat\Watcher` salvo modifiche, vedi [Installazione e avvio](installing-and-running.md#where-everything-is)). Puoi leggerli, copiarli o eliminarli senza il watcher. Un file `.jsonl` è testo semplice, una riga per evento (si apre con Blocco note); un file `.parquet` è una tabella che il visualizzatore di 3DHeat apre (Excel non lo apre - `stats --csv` scrive file CSV per i fogli di calcolo).

## Cartelle di sessione {#session-folders}
![una cartella di sessione](../assets/img/session-folder.svg)


Una **sessione** è una seduta con una sola fonte: dal momento in cui il gioco dice per la prima volta qualcosa fino a quando si ferma (il gioco si chiude, una partita finisce, una guida o un volo vengono azzerati - la pagina di ogni adattatore dice cosa avvia e chiude le sue sessioni). Ogni sessione ha una cartella:

```text
<data>\sessions\<game>\<YYYY-MM-DD_HH-MM-SS>_<adapter id>\
    events.jsonl
    heat.parquet
    meta.json
```

- `<game>` è il nome del gioco con ogni carattere diverso da lettere, cifre, `.`, `_` e `-` sostituito da `-` (al massimo 60 caratteri): `EA-SPORTS-F1-25`, `Counter-Strike-2`. Gli adattatori che coprono molti giochi (statistiche di Steam, Timeline di Steam, highlight NVIDIA) archiviano ogni sessione sotto il gioco a cui appartiene.
- L'ora è l'inizio della sessione in ora locale. Le sessioni che descrivono il passato (un replay convertito dopo la partita, un file di statistiche di Steam) usano l'ora che il gioco o il file indicano. Due sessioni che iniziano nello stesso secondo ricevono `_2`, `_3`, ... in coda.
- L'id della sessione, nel database delle statistiche, è `<cartella del gioco>/<cartella della sessione>`.

Una sessione in cui non è stato registrato proprio nulla (il gioco è rimasto nei menu, oppure si è bloccato all'avvio) viene eliminata alla chiusura, così ogni avvio non lascia una cartella vuota.

Alcune sessioni contengono altri file. Una sessione di una demo di Counter-Strike 2 contiene la tabella e il riepilogo del convertitore (`<map>/<match>.parquet`, `<match>.match.json`). Una sessione di iRacing elenca i file `.ibt` che il simulatore ha scritto durante la seduta come eventi `telemetry_file`.

## events.jsonl {#eventsjsonl}

`events.jsonl` contiene un oggetto JSON per riga, una riga per evento, scritta nel momento in cui l'evento accade. Il file è a buffer di riga, quindi un crash, un'interruzione di corrente o un processo terminato non fanno perdere nulla di ciò che era già scritto; una riga troncata da un crash viene saltata quando il file viene letto, e ogni riga prima di essa resta valida.

Ogni riga ha le stesse colonne di base:

| Colonna | Tipo | Cos'è |
|---|---|---|
| `time` | numero | secondi dall'inizio della sessione (4 decimali), oppure l'orologio proprio del gioco dove l'adattatore lo passa |
| `ms` | intero | ora dell'orologio, millisecondi Unix |
| `event` | testo | cosa è successo: `position`, `spawn`, `death`, `kill`, `lap`, `teleport`, `session_start`, ... |
| `x`, `y`, `z` | numero | dove, nelle unità e negli assi del gioco (vedi `axes` in `meta.json`); presente solo quando tutti e tre sono noti e finiti |
| `player` | testo | chi: un nome, un id, oppure `me` per la persona che gioca (vedi [Le righe del giocatore](#the-players-own-rows)) |
| `team` | testo | la loro squadra, quando il gioco la indica |
| `session` | testo | la partita, il round, la tappa, la vita o il volo a cui appartiene la riga, quando il gioco lo dice |

Ogni altro campo che il gioco riporta segue con il suo nome (`speed_kmh`, `gear`, `lap_time`, `weapon`, `victim`, `hero`, ...). I campi senza valore vengono omessi, e così i numeri che non sono finiti. Due righe sintetiche:

```json
{"time":12.3456,"ms":1777660501123,"event":"position","x":-412.5,"y":12.1,"z":233.0,"player":"me","session":"1","speed_kmh":187.4,"gear":5}
{"time":15.0,"ms":1777660503667,"event":"lap","x":-380.2,"y":12.0,"z":250.9,"player":"me","session":"1","lap_time":92.418,"lap":3}
```

Le righe senza posizione (una riga del flusso di uccisioni, un salto di livello, un cambio di statistica) restano in `events.jsonl` e contano nelle statistiche. Solo le righe con una posizione entrano nella tabella.

### Le righe del giocatore {#the-players-own-rows}

È la fonte a dire quali righe appartengono alla persona che gioca; non si indovina mai. Una riga è del giocatore quando

- il suo `player` è `me`: la maggior parte degli adattatori, la cui fonte è il gioco stesso del giocatore (telemetria della propria auto o aereo, un'integrazione di stato di gioco, un giornale);
- porta `own_car` 1: i giochi di corsa che registrano ogni auto con il nome del suo pilota (EA SPORTS F1 dall'indice dell'auto del giocatore nel gioco, RaceRoom dal suo slot proprio, Automobilista 2 e Project CARS 2 dal partecipante inquadrato) segnano l'auto del giocatore in questo modo e tengono il nome del pilota in `player`;
- il suo `player` è il `player` della sessione in `meta.json`: il nome che la fonte dà al giocatore - il comandante di Elite Dangerous (il giornale è sempre quello del giocatore), oppure la riga di un replay di League of Legends che corrisponde al Riot ID nelle impostazioni.

War Thunder e Rocket League nominano ogni giocatore e non dicono quale sei tu; con il tuo nome nell'impostazione `player_names` (vedi [Impostazioni](installing-and-running.md#settings)) le tue righe diventano `me`. [NVIDIA highlights](nvidia-highlights.md) cercano un momento proprio in queste righe.

## heat.parquet {#heatparquet}

Quando una sessione si chiude, le righe di `events.jsonl` che hanno `x`, `y` e `z` vengono scritte in `heat.parquet`. È la tabella che apre il visualizzatore di 3DHeat. Se la sessione non ha posizioni, non viene scritta nessuna tabella.

- Le colonne sono `time`, `ms`, `event`, `x`, `y`, `z`, `player`, `team`, `session`, seguite da ogni altro campo nell'ordine in cui compare per la prima volta.
- `x`, `y`, `z` e `time` sono numeri in virgola mobile a 64 bit, e `ms` è un intero a 64 bit. Una colonna ulteriore i cui valori sono tutti numeri è un numero in virgola mobile a 64 bit; ogni altra colonna è testo a dizionario (i valori mancanti sono testo vuoto, e liste o oggetti sono scritti come testo JSON).
- I metadati del file hanno una chiave `heat3d` con le istruzioni di lettura, così il visualizzatore mappa colonne e assi da solo (un esempio, con la lista `extra` abbreviata):

```json
{
  "version": 1,
  "kind": "heat3d-watch",
  "game": "EA SPORTS F1 25",
  "axes": {"up": "y", "flipX": false, "flipY": false, "flipZ": false, "scale": 1.0},
  "columns": {
    "x": "x", "y": "y", "z": "z",
    "time": "time", "timeUnit": "seconds",
    "personId": "player", "teamId": "team", "sessionId": "session",
    "extra": ["event", "speed_kmh", "gear", "lap_time", "lap"]
  }
}
```

`up` è l'asse verticale del gioco, `flipX`/`flipY`/`flipZ` specchiano un asse così un mondo mancino non viene disegnato specchiato, e `scale` è la scala di unità del visualizzatore: il visualizzatore moltiplica ogni posizione per questo valore quando carica la tabella (0,01 trasformerebbe centimetri in metri). Ogni adattatore scrive 1 e conserva le unità del gioco - metri per la maggior parte, unità Source (pollici) per Counter-Strike 2, unità Unreal (centimetri) per Rocket League - perché un livello esportato dal gioco è in quelle stesse unità, quindi le righe ci cadono sopra; anche le tabelle del convertitore di CS2 lo dicono. `units` in `meta.json` dice cosa vale un'unità. La pagina di ogni gioco elenca i suoi valori sotto "Positions and axes".

I simulatori di volo (DCS World, Microsoft Flight Simulator, X-Plane, le registrazioni Tacview di IL-2) mettono le loro righe sulla Terra, e il loro piè di pagina dice dove, così il visualizzatore può stendere il vero mondo sotto di esse:

```json
"geo": {"lat0": 42.0, "lon0": 42.0, "projection": "tangent-plane", "east": "x", "north": "z", "up": "y"}
```

`lat0`/`lon0` (gradi) sono l'origine della mappa piatta in cui stanno le righe; `east`, `north` e `up` indicano le colonne che contengono i metri a est e a nord da essa e l'altitudine sul livello del mare. L'origine è il primo punto fisso per X-Plane e MSFS, il punto di riferimento della registrazione per IL-2, e l'origine fissa del teatro per DCS (il primo punto fisso arrotondato ai gradi interi, su un teatro che il watcher non conosce). Una tabella senza una collocazione sulla Terra non ha la chiave `geo`, e tutto il resto del piè di pagina è lo stesso in ogni caso.

`heat.parquet` può sempre essere ricostruito da `events.jsonl` con `python -m heat3d_watch table <cartella della sessione>` (vedi [Comandi](commands.md#table)). È utile quando `pyarrow` mancava mentre la sessione veniva registrata.

## meta.json {#metajson}

`meta.json` riassume la sessione. Viene scritto quando la sessione si apre, al massimo ogni 30 secondi mentre arrivano eventi o statistiche, e quando la sessione si chiude. Le statistiche vengono tenute in memoria solo tra una scrittura e l'altra, quindi un crash può far perdere al massimo gli ultimi mezzo minuto.

```json
{
  "format": "heat3d-watch-session",
  "version": 1,
  "watcher": "1.0.2",
  "game": "EA SPORTS F1 25",
  "adapter": "f1-25",
  "source": "UDP telemetry 127.0.0.1:20777 (...)",
  "multiplayer": true,
  "started": "2026-05-01T20:15:03",
  "ended": "2026-05-01T21:02:11",
  "seconds": 2828.0,
  "axes": {"up": "y", "flip_x": false, "flip_y": false, "flip_z": false, "scale": 1.0, "units": "metres"},
  "events": {"position": 52110, "lap": 412, "teleport": 3},
  "positions": 52530,
  "stats": {"laps": 20, "best_lap": 91.874, "distance_km": 106.3, "race_position": 4},
  "track": "..."
}
```

Una sessione la cui fonte indica il giocatore (vedi [Le righe del giocatore](#the-players-own-rows)) ha anche `"player"`: il nome che portano le righe del giocatore. Una sessione sulla Terra (i simulatori di volo) ha anche `"geo": {"lat0": .., "lon0": ..}`, l'origine che ripete il `geo` del piè di pagina.

- `started` / `ended`: ora locale fino al secondo; `ended` è `null` mentre la sessione è in corso.
- `events`: quante volte è accaduto ogni evento, dal più frequente. `positions` è il numero di righe con una posizione.
- `stats`: i numeri della sessione. Un adattatore ne imposta ciascuno, lo somma, oppure mantiene il massimo o il minimo.
- Tutto ciò che l'adattatore sa in più sulla seduta compare al primo livello: il tracciato, la mappa, la missione, l'id della partita, l'id dell'app Steam, il file del replay, il profilo di memoria e la build. Una sessione chiusa dal recupero ha `"recovered": true`.

## watcher.sqlite {#watchersqlite}

`watcher.sqlite` è il database delle statistiche. Una riga viene aggiunta per ogni sessione quando si chiude. Le tre tabelle sono semplici, quindi qualsiasi strumento SQL, notebook o foglio di calcolo può leggerle senza il watcher:

```sql
CREATE TABLE sessions (
  id TEXT PRIMARY KEY,          -- <game folder>/<session folder>
  game TEXT NOT NULL,
  adapter TEXT NOT NULL,
  started REAL NOT NULL,        -- Unix seconds
  ended REAL,                   -- Unix seconds
  seconds REAL,
  folder TEXT NOT NULL,         -- the session folder's full path
  events INTEGER NOT NULL DEFAULT 0,
  positions INTEGER NOT NULL DEFAULT 0,
  multiplayer INTEGER NOT NULL DEFAULT 0,
  source TEXT
);
CREATE TABLE events (           -- per session, how many times each event happened
  session TEXT NOT NULL REFERENCES sessions(id) ON DELETE CASCADE,
  event TEXT NOT NULL,
  count INTEGER NOT NULL,
  PRIMARY KEY (session, event)
);
CREATE TABLE stats (            -- per session, every number the game reported or the watcher counted
  session TEXT NOT NULL REFERENCES sessions(id) ON DELETE CASCADE,
  key TEXT NOT NULL,
  value REAL,                   -- numbers
  text TEXT,                    -- everything else (a map name, a result, a hero)
  PRIMARY KEY (session, key)
);
```

Registrare di nuovo una sessione (recupero, un replay convertito di nuovo) sostituisce le sue righe. `multiplayer` è il flag dell'adattatore (alcuni adattatori lo impostano per sessione, per esempio DCS dalla missione), non una verifica che tu fossi online. Un valore vero/falso in `stats` viene memorizzato come testo.

Un esempio di query, il giro più veloce per gioco su tutte le sessioni (più basso è meglio):

```sql
SELECT s.game, MIN(t.value) AS best_lap
FROM stats t JOIN sessions s ON s.id = t.session
WHERE t.key = 'best_lap'
GROUP BY s.game;
```

`python -m heat3d_watch stats` stampa i totali da queste tabelle (vedi [Comandi](commands.md#stats)); la sua colonna `best` è il valore più basso per i tempi tenuti come migliori e per i piazzamenti, il più alto per il resto.

## Recupero dopo un crash {#recovery-after-a-crash}

Quando `run` parte, cerca le sessioni che un watcher precedente ha lasciato aperte: un `meta.json` senza `ended`, e un `events.jsonl` con almeno una riga. Ne completa ognuna:

- i conteggi degli eventi e il numero di posizioni vengono ricalcolati da `events.jsonl`, saltando una riga troncata;
- la fine è l'ora dell'orologio dell'ultima riga (`ms`);
- le statistiche sono quelle dell'ultima scrittura di `meta.json` (al massimo di 30 secondi fa);
- viene aggiunto `"recovered": true`, viene scritto `heat.parquet`, e la sessione entra in `watcher.sqlite`.

Il log dice "finished N session(s) left open by an earlier run". Il file di lock impedisce a un secondo watcher di "recuperare" le sessioni di uno che è ancora in esecuzione.

## Esportazione CSV {#csv-export}
![stats --csv e table](../assets/img/csv-and-table.svg)


```bash
python -m heat3d_watch stats --csv out
```

scrive `out\sessions.csv`, `out\events.csv` e `out\stats.csv`. Ogni file è una tabella di `watcher.sqlite`, completa, con una riga di intestazione, in UTF-8. Gli orari sono secondi Unix come nel database. `--game` non restringe l'esportazione; viene scritta ogni sessione.

## Aprire una sessione nel visualizzatore di 3DHeat {#opening-a-session-in-the-3dheat-viewer}

Il visualizzatore: [github.com/Holdi601/3DHeat](https://github.com/Holdi601/3DHeat), documentazione [holdi601.github.io/3DHeat](https://holdi601.github.io/3DHeat/) - la sua pagina sul [contenitore `.3dheat`](https://holdi601.github.io/3DHeat/container.html) descrive il formato di un file per partita che possono scrivere i convertitori di replay.

Apri il `heat.parquet` di una sessione nel visualizzatore di 3DHeat. Il piè di pagina dice al visualizzatore quale colonna è la posizione, il tempo, il giocatore, la squadra e la sessione, e da che parte è l'alto, quindi non c'è nulla da mappare a mano. Le posizioni sono nelle coordinate del mondo proprie del gioco. Disegnate sopra un livello esportato con gli altri strumenti di 3DHeat (per esempio da [3DHeat GameFiles](https://github.com/Holdi601/3DHeat-GameFiles)), finiscono dove sono avvenute.

- Le **mappe di calore** usano ogni riga con una posizione, filtrate per `event`, `player`, `team` o `session` come qualsiasi altra colonna.
- Il **calore a linee** disegna una linea da ogni riga di un giocatore alla successiva, e in riproduzione ogni giocatore è un punto che si muove lungo il percorso con una scia dietro. Il pannello **Percorsi** del visualizzatore sceglie, dalla colonna `event`, quali eventi **iniziano** un percorso e quali ne **chiudono** uno. Il watcher scrive gli eventi che delimitano i percorsi come righe con una posizione, così possono essere scelti lì:
  - inizi: `spawn`, `respawn`, `session_start`. Un inizio chiude il percorso che era aperto senza tracciare una linea fino al nuovo punto;
  - fini: `death`, `finish`, `session_end` e `teleport`. La linea arriva fino alla riga di fine stessa, che è il punto in cui il giocatore è morto, si è fermato o è stato portato via.

  Un salto - un punto raggiunto senza viaggiarci - sono due righe: `teleport` nel punto **lasciato**, e un inizio nel punto **raggiunto**, subito dopo. Gli adattatori di corsa scrivono una coppia ogni volta che l'auto si è spostata più lontano di quanto avrebbe potuto guidare (un riavvolgimento o flashback, un reset sulla strada, un ritorno ai box, un viaggio rapido), con `spawn` all'arrivo (`respawn` per il reset di BeamNG); la riga `teleport` porta l'arrivo come `to_x`, `to_y`, `to_z` e la distanza come `metres`, la riga di inizio `after: "teleport"`. Gli adattatori dei camion fanno lo stesso per un traghetto, un treno o un salvataggio caricato, e quelli di volo per un salto che nessun aereo potrebbe fare. Quindi, con `teleport` tra le fini e `spawn` tra gli inizi - che è ciò che il visualizzatore suggerisce da solo - un percorso finisce dove il salto l'ha lasciato e il successivo comincia dove è arrivato, e nessuna linea attraversa la mappa. Un percorso non attraversa mai un cambio della colonna `session`. Una riga di posizione viene scritta alcune volte al secondo (10 Hz per la maggior parte della telemetria), il che dà una linea continua.
- La colonna `session` divide una seduta nei suoi round, tappe, vite o corpi (Elite Dangerous tiene separate in questo modo le righe della galassia e quelle della superficie di ogni pianeta). Scegline una nel visualizzatore per guardare solo quella parte.

Ciò che il visualizzatore fa con le righe - filtri, colori, riproduzione - è descritto nella documentazione del visualizzatore stesso. Le sessioni di demo di Counter-Strike 2 si aprono tramite il `<map>/<match>.parquet` e il `<match>.match.json` del convertitore, nelle schede **Mappa di calore** e **Partita** del visualizzatore. Le posizioni di iRacing vengono dai file `.ibt` elencati nella sessione, che il visualizzatore legge da sé.
