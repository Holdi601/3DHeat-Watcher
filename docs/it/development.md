---
title: Sviluppo
nav_order: 12
lang: "it"
source: development.md
source_hash: "cb213e22ddea"
nav_exclude: true
search_exclude: true
---
# Sviluppo {#development}

Questa pagina serve per aggiungere un gioco: come si costruisce un adattatore, come si prova e come si scrive la sua documentazione.

## Il repository {#the-repository}

| Percorso | Cosa contiene |
|---|---|
| `heat3d_watch/cli.py` | i comandi ([Comandi](commands.md)) |
| `heat3d_watch/watcher.py` | il ciclo in background: lista dei processi, un thread per adattatore, aggiornamenti |
| `heat3d_watch/session.py` | una registrazione: `events.jsonl`, `heat.parquet`, `meta.json`, recupero |
| `heat3d_watch/db.py` | `watcher.sqlite` |
| `heat3d_watch/config.py` | le impostazioni e la cartella dei dati |
| `heat3d_watch/safety.py`, `heat3d_watch/memory.py` | i controlli sulla memoria e il lettore in sola lettura ([Lettura della memoria](memory-reading.md)) |
| `heat3d_watch/notify.py` | notifiche di Windows |
| `heat3d_watch/adapters/` | un modulo per gioco o per famiglia di giochi; i moduli che iniziano con `_` sono funzioni di supporto condivise |
| `heat3d_watch/decoders/` | i decodificatori della telemetria di guida, copiati dai registratori dei giri di 3DHeat GameCapture |
| `heat3d_update/` | l'aggiornatore ([Aggiornamenti](updates.md)) |
| `mods/beamng/heat3d/` | la mod di protocollo di BeamNG che installa `setup beamng` |
| `tests/` | i test |
| `tools/gen_game_pages.py` | scrive le pagine dei giochi di questa documentazione |

## Un adattatore {#an-adattatore}

Un adattatore è una dataclass derivata da `heat3d_watch.adapters.base.Adapter`. I suoi campi dicono cos'è; i suoi metodi fanno il lavoro.

| Campo | Predefinito | Cos'è |
|---|---|---|
| `id` | `""` | breve e stabile: le cartelle di sessione, `disabled`, `replay_folders` e `player_names` si riferiscono a lui |
| `game` | `""` | il nome del gioco come lo scrivono le persone; le sessioni sono archiviate sotto questo nome |
| `kind` | `"telemetry"` | uno tra `telemetry`, `gsi`, `log`, `replay`, `platform`, `memory` ([Fonti e regole](sources-and-rules.md)) |
| `exes` | `()` | nomi di eseguibili (in qualsiasi maiuscolo/minuscolo) che indicano che il gioco è in esecuzione. Vuoto: l'adattatore è sempre attivo (`always` è vero) |
| `multiplayer` | `True` | il gioco si gioca online: la sua memoria non viene mai letta |
| `source` | `""` | da dove vengono i numeri, detto una volta |
| `records` | `()` | cosa viene registrato, una voce per tipo di cosa |
| `enable` | `""` | come attivare la fonte; vuoto quando non serve nulla |
| `interval` | `0.1` | secondi tra un'interrogazione e l'altra |
| `axes` | `Axes()` | l'asse verticale del mondo, gli assi specchiati, la scala di unità del visualizzatore (lasciala a 1) e una nota sulle unità |
| `verified` | `""` | cosa è stato verificato, onestamente (vedi sotto) |
| `completeness` | `{}` | il resoconto della fonte secondo la [regola del convertitore](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md) di 3DHeat: `read` (cosa diventa righe), `raw` (cosa viene conservato intero, e sotto quale `type`), `missing` (cosa la fonte non fornisce, e perché), `size` (quanto pesa in un'ora il flusso grezzo). La sezione "Completezza" della pagina del gioco è scritta a partire da essa |

`source`, `records`, `enable`, `verified` e `completeness` sono documentazione, non decorazione. `games` le stampa, `games --markdown` produce la tabella in [Tutti i giochi in una tabella](watcher.md), e le pagine dei giochi sono generate da esse. Scrivile in modo che dicano esattamente ciò che fa il codice.

I metodi, tutti facoltativi:

| Metodo | Chiamato da | Cosa dovrebbe fare |
|---|---|---|
| `missing(self) -> str \| None` | `games`, `status` e prima dell'avvio | dire perché l'adattatore non può girare qui (una DLL non trovata, una cartella mancante), oppure `None` |
| `setup(self, ctx, *, apply) -> list[str]` | `setup` | attivare l'output proprio del gioco; restituire una riga per ogni modifica, e cambiare i file solo quando `apply` è vero. Salvare un file come `<file>.heat3d-backup` prima della sua prima modifica, e non sovrascrivere mai quel backup. Sovrascrivere il metodo solo quando c'è qualcosa da attivare: `can_setup` (vero quando `setup` è sovrascritto) decide se `setup` lo esegue oppure dice che non c'è nulla da cambiare; una classe che serve più giochi sovrascrive `can_setup` per quelli che non può configurare (`RallyAdapter` per Richard Burns Rally). |
| `start(self, ctx)` | quando compare il processo del gioco (adattatori sempre attivi: quando parte `run`) | aprire socket, trovare file, ricordare da dove cominciare |
| `poll(self, ctx)` | ogni `interval` secondi, nel thread proprio dell'adattatore | prendere ciò che il gioco ha detto dall'ultima interrogazione e registrarlo |
| `stop(self, ctx)` | quando il gioco non c'è più o il watcher si ferma | chiudere sessioni e socket |

Ogni adattatore gira nel proprio thread (`Runner`). Un'eccezione in `poll` viene registrata e l'adattatore attende `min(5, interval × 10 + 0.5)` secondi prima della prossima interrogazione. Dopo 20 errori di seguito, oppure un errore in `start`, l'adattatore viene fermato e non riparte finché l'id del processo del gioco non cambia.
`missing()` viene controllato a ogni scansione, quindi deve essere leggero.

Un oggetto adattatore viene riutilizzato quando il suo gioco riparte, quindi `start` deve azzerare tutto ciò che una esecuzione precedente ha lasciato.

### Registrazione {#registering-it}

Metti il modulo in `heat3d_watch/adapters/` ed elenca gli adattatori alla sua fine:

```python
ADAPTERS = [MyAdapter(id="mygame", game="My Game", ...)]
```

`adapters.load()` importa ogni modulo del pacchetto (tranne `base` e i nomi che iniziano con `_`) e raccoglie i loro `ADAPTERS`. Due adattatori con lo stesso id bloccano il caricamento con un `ValueError`. Un modulo che non si importa (una dipendenza mancante) lascia fuori i suoi giochi, e `games` lo segnala con l'errore, così il problema di un gioco non ferma gli altri.

## Context e Session {#context-and-session}

`start`, `poll`, `stop` e `setup` ricevono un `Context`:

| Membro | Cos'è |
|---|---|
| `settings` | i `Settings` ([Installazione e avvio](installing-and-running.md#settings)) |
| `data` | la cartella dei dati |
| `pid`, `exe` | l'id del processo del gioco e il percorso dell'eseguibile, quando l'adattatore è stato avviato per un gioco in esecuzione; la cartella di installazione è accanto a `exe` |
| `open(adattatore, *, game=None, when=None, axes=..., source=..., multiplayer=..., meta=..., geo=None)` | una nuova `Session`. `game` sostituisce il nome del gioco dell'adattatore (per gli adattatori che coprono molti giochi); `when` imposta l'inizio per le sessioni che descrivono il passato; `axes`, `source` e `multiplayer` prendono il valore dell'adattatore; `meta` è un dizionario scritto in `meta.json`; `geo` (`{"lat0": .., "lon0": ..}`, oppure impostato dopo in `session.geo`) colloca una sessione su mappa piatta sulla Terra, in `meta.json` e nel piè di pagina della tabella |
| `close(session)` | chiude una sessione: la tabella, `heat.raw.parquet`, `meta.json`, la sua riga in `watcher.sqlite`. Una sessione senza eventi né elementi grezzi viene eliminata; una con soli elementi grezzi viene mantenuta (niente tabella, nessuna riga nel database). Accetta `None`. Restituisce il percorso della tabella oppure `None`. |

Una `Session` registra:

| Membro | Cosa fa |
|---|---|
| `event(name, *, t=None, ms=None, x=None, y=None, z=None, player=None, team=None, session=None, **attrs)` | una riga. `t` predefinito sono i secondi dall'inizio della sessione, `ms` predefinito è l'ora attuale. Una posizione conta solo quando `x`, `y` e `z` sono tutti indicati e finiti. Gli attributi `None` vengono omessi. |
| `position(x, y, z, **kw)` | un evento chiamato `position` |
| `raw(type, payload=None, *, text=None, used=False, t=None, ms=None, **fields)` | conservare intera una cosa inviata dalla fonte: i byte di un pacchetto o di una pagina (`payload`), una riga o una risposta JSON com'era (`text`), oppure i valori di una lettura per nome (`fields`, ognuno nella sua colonna). `type` è la parola della fonte per quella cosa (un id di pacchetto, il nome di una mappatura, un evento di giornale, un endpoint); `used` dice che è diventata anche righe. Incorniciata in `raw.bin` nel momento della chiamata, scritta come `heat.raw.parquet` (zstd) alla chiusura o al recupero della sessione, e conteggiata per `type` in `selfCheck.completeness` di `meta.json` |
| `stat(key, value, how="set")` | una statistica: `set` la imposta, `add` le somma, mantiene il `max` o il `min` |
| `now()` | secondi dall'inizio della sessione |
| `meta` | un dizionario scritto in `meta.json` |
| `started`, `ended`, `folder`, `id`, `counts`, `positions` | quando, dove, e cosa è stato registrato finora |

`event`, `stat` e `raw` sono thread-safe e possono essere chiamati da un thread di lavoro.

**Ogni adattatore conserva tutto ciò che la sua fonte invia.** Le righe sono ciò che il visualizzatore disegna; non sono la registrazione. Ogni pacchetto che arriva a una porta, ogni pagina di memoria condivisa letta (l'intera mappatura, ogni volta che cambia), ogni riga di un log o di uno script di esportazione (anche quelle che l'adattatore ignora), ogni risposta JSON o documento inviato va in `session.raw(...)` appena arriva - che diventi o no una riga - e nulla viene diradato sotto la frequenza con cui l'adattatore legge. Un elemento che arriva prima che una sessione sia aperta ne apre una (una sessione con soli elementi grezzi viene mantenuta), oppure viene trattenuto finché una non si apre; non viene mai scartato. I campi che si decodificano facilmente e il cui significato è certo finiscono anche nelle righe. Questa è la [regola del convertitore](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md) di 3DHeat: un flusso in diretta è perso nel momento stesso in cui viene inviato, quindi ciò che un adattatore non conserva è perso per sempre, e ciò che conserva intero può essere decodificato il giorno in cui qualcuno ne capisce il formato. La dimensione è il prezzo; zstd e la codifica a dizionario la contengono, senza lasciare fuori nulla. Il test di ogni adattatore invia qualcosa che non usa e verifica che torni intero da `heat.raw.parquet`, e che `selfCheck.completeness.lost` sia 0. `racing.Driving.raw` fa lo stesso per gli adattatori di corsa (e apre la sessione), e `racing.Pages` conserva le pagine di memoria condivisa ogni volta che cambiano i loro byte, contando in `unchanged_reads` di `meta.json` le riletture che non hanno trovato nulla di nuovo.

Convenzioni su cui si basa il resto del sistema:

- **Le righe del giocatore sono segnate, secondo quanto dice la fonte.** `player="me"` dove la fonte è quella del giocatore; dove ogni giocatore è registrato con un nome, `own_car=1` sulle righe dell'auto del giocatore (dall'indice del giocatore nel gioco oppure dal partecipante inquadrato), oppure il nome del giocatore come `session.meta["player"]` (scritto subito in `meta.json`) quando la fonte nomina il giocatore. Mai indovinare: dove la fonte non lo dice, prendi il nome da un'impostazione (`player_names`, `riot_id`) oppure non segnare nulla. [NVIDIA highlights](nvidia-highlights.md) prendono posizioni solo da queste righe (`platform.own_row`). Gli altri giocatori si riconoscono dal nome o dall'id.
- **I percorsi sono delimitati da eventi con posizione**: `spawn`, `respawn` e `session_start` ne iniziano uno; `death`, `finish`, `session_end` e `teleport` ne chiudono uno. Ogni volta che il giocatore si sposta senza viaggiare (un reset, un riavvolgimento, un viaggio rapido, un salvataggio caricato), scrivi `teleport` nel punto lasciato e poi un inizio (`spawn`, oppure `respawn` per un reset che il gioco nomina) nel punto raggiunto, così il calore a linee del visualizzatore chiude un percorso e ne apre un altro invece di tracciare una linea attraverso la mappa. `Driving.jumped` lo fa per i veicoli.
- **Le posizioni restano nelle coordinate e nelle unità del mondo del gioco**, descritte da `axes`. Non convertirle in un altro sistema di riferimento a meno che il gioco non fornisca alcun mondo utilizzabile (i simulatori di volo mettono latitudine e longitudine su una mappa piatta, `Tangent`, attorno al primo punto fisso - DCS attorno all'origine fissa del suo teatro - e passano `geo=tangent.geo()` a `open`, così il piè di pagina dice dove sulla Terra si trova la mappa). `axes.scale` è la scala di unità del visualizzatore - moltiplica ogni posizione - e resta 1, così le righe combaciano con un livello esportato dallo stesso gioco nelle stesse unità; scrivi l'unità in `axes.units`.
- **Le chiavi statistiche** sono minuscole con trattini bassi, e portano la loro unità dove ne serve una (`distance_km`, `top_speed_kmh`, `max_altitude_m`, `duration_s`). Un tempo tenuto come migliore inizia con `best_` (mantenuto con `min`), un piazzamento finisce con `_position`: `stats` mostra il più basso di questi come migliore, e il più alto di ogni altra chiave (`db.lower_is_better`).

## Funzioni di supporto {#helpers}

| Funzione | Modulo | Per |
|---|---|---|
| `Follower(find, since, stamp=None)`, `game_started(pid)`, `newest(paths)`, `read_shared(path)`, `steam_libraries()` | `_logfollow` | seguire un log scritto dal gioco: letture condivise, solo le righe di questa sessione, file nuovi e sostituiti, solo righe complete |
| `UdpPort(port, forward=None, grace=0.0, recheck=3.0)` con `try_open(who)`, `receive()`, `close()` | `racing` | una porta UDP di telemetria su 127.0.0.1, presa solo se libera, lasciata a un altro programma su richiesta, facoltativamente inoltrata |
| `Driving(adattatore, ctx, hz=10.0, jump=50.0)` con `sample(...)`, `event(...)`, `lap(...)`, `count(...)`, `close()` | `racing` | sessioni di veicoli: posizioni a frequenza fissa, distanza, velocità massima, giri; a un salto, `teleport` dove era l'auto e `spawn` dove si trova ora (`jumped(...)`) |
| `SharedView.open(name)` | `simracing_shm` | la memoria condivisa con nome di un gioco, in sola lettura, mai creata |
| `ReplayAdapter` (`patterns`, `folders(ctx)`, `convert(path, ctx)`) | `replays` | una cartella di replay sorvegliata: i file vengono convertiti una volta smesso di crescere, in un thread di lavoro; la prima occhiata si limita a notare cosa c'è, e `convert_existing(ctx, folder=None)` - il comando [`replays`](commands.md#replays) - converte quelli su richiesta |
| `load_state`, `save_state` | `platform` | ricordare cosa un adattatore sempre attivo ha già visto, in `<data>\state\<id>.json` |
| `FlightLog`, `Tangent` | `xplane` | contabilità di volo (decolli, atterraggi, schianti, distanza) e la mappa piatta attorno al primo punto fisso (`Tangent.geo()` è il `geo` della sessione) |
| `backup_once(path)` | `gsi`, `racing` | la regola `<file>.heat3d-backup` |
| File di Steam | `_steam` | KeyValues binari e testuali, la cartella di Steam dal registro |

Un adattatore di log minimo, a titolo di esempio (un gioco inventato):

```python
from dataclasses import dataclass, field
from pathlib import Path

from ..session import Axes, Session
from ._logfollow import Follower, game_started, newest
from .base import Adapter, Context


@dataclass
class ExampleAdapter(Adapter):
    _session: Session | None = field(default=None, repr=False)
    _follow: Follower | None = field(default=None, repr=False)

    def start(self, ctx: Context) -> None:
        log = (ctx.exe.parent if ctx.exe else Path(".")) / "logs" / "game.log"
        self._session = None
        self._follow = Follower(lambda: newest(p for p in [log] if p.exists()), game_started(ctx.pid))

    def poll(self, ctx: Context) -> None:
        for line in self._follow.lines() if self._follow else []:
            if line.startswith("DIED "):
                if self._session is None:
                    self._session = ctx.open(self)
                self._session.event("death", player="me")
                self._session.stat("deaths", 1, "add")

    def stop(self, ctx: Context) -> None:
        self.poll(ctx)
        ctx.close(self._session)
        self._session = None


ADAPTERS = [
    ExampleAdapter(
        id="example",
        game="Example Game",
        kind="log",
        exes=("ExampleGame.exe",),
        source=r"<install>\logs\game.log (followed)",
        records=("deaths",),
        interval=0.5,
        axes=Axes(units="no positions recorded"),
        verified="tested on synthetic log lines in the game's format; untested against the game",
    )
]
```

Apri la sessione con la prima cosa degna di essere registrata, non in `start`, così un gioco fermo nei menu non lascia nulla (una sessione vuota viene comunque eliminata).

## Test {#tests}

```bash
python -m pytest
```

`tests/conftest.py` dà a ogni test una cartella dati usa e getta (`HEAT3D_WATCH_HOME`) e disattiva i controlli di aggiornamento e le notifiche (`HEAT3D_NO_UPDATE`, `HEAT3D_NO_TOAST`). Un test di adattatore costruisce l'output del gioco dal suo formato pubblicato - pacchetti dalla specifica, righe di log nel formato del gioco, file nel layout documentato - e pilota l'adattatore direttamente (abbreviato da `tests/test_poe.py`; `data` e `install` sono cartelle temporanee):

```python
from dataclasses import replace
from heat3d_watch.adapters import poe
from heat3d_watch.adapters.base import Context
from heat3d_watch.config import Settings
from heat3d_watch.session import read_rows

ctx = Context(Settings(data=str(data)), data, exe=install / "PathOfExileSteam.exe")
a = replace(poe.ADAPTERS[0])   # a fresh copy of the adattatore
a.start(ctx); a.poll(ctx); a.stop(ctx)
[session] = list((data / "sessions").glob("*/*"))
rows = read_rows(session)      # then check the rows and meta.json's stats
```

Gli adattatori di rete si testano contro un server locale finto, oppure con pacchetti inviati via UDP all'adattatore. I test che controllano dati reali di gioco sul computer dello sviluppatore sono marcati `@pytest.mark.local` e vengono saltati dove quei dati mancano. Quei dati non entrano mai nel repository. `test_core.py` contiene anche il test che fallisce se nel pacchetto compare codice che potrebbe scrivere in un altro processo (`test_memory_reading_cannot_write`).

## Un `verified` onesto {#an-honest-verified}

`verified` dice cosa è stato controllato e come, e cosa no. Viene mostrato da `games` e in ogni pagina di gioco, e i giocatori si fidano di esso. Esempi dal codice:

- "tested on packets in the 2023, 2024 and 2025 formats built from EA's published specification, sent over UDP; untested against the game"
- "tested on documents in the published GSI format posted to the running adattatore; untested against the running game"
- "tested on real stats files and schemas from a local install; change detection tested on files built in the binary KeyValues format"

Scrivi "untested against the game" finché l'adattatore non ha registrato il gioco in esecuzione. Dichiara solo il metodo e la tolleranza: mai una mappa, un id partita, un nome di giocatore, una data, la dimensione di un corpus o un conteggio esatto da file reali, e mai "this machine" (chi legge non conosce quella macchina). Nomina la fonte di ogni offset e di ogni layout, e dì dove due fonti sono state confrontate. Non dichiarare mai più di quanto è stato fatto. Un formato che è stato indovinato o preso da strumenti della comunità va detto così.

## Le pagine dei giochi {#the-game-pages}

Ogni pagina sotto [Giochi](games.md) è generata dagli adattatori, quindi corrisponde sempre al codice. Dopo aver aggiunto o cambiato un adattatore, rigenerale dalla cartella del repository:

```bash
HEAT3D_NO_UPDATE=1 python tools/gen_game_pages.py
```

(In PowerShell: `$env:HEAT3D_NO_UPDATE = "1"; python tools/gen_game_pages.py`.) Aggiungi `--check` per soltanto confrontare: non scrive nulla ed esce con 1 quando una pagina non è aggiornata (anche la tabella dei giochi di `docs/watcher.md`).

Lo script:

- carica gli adattatori con `heat3d_watch.adapters.load()`, su una cartella dati temporanea vuota, così nessun profilo di memoria o impostazione del tuo computer finisce nelle pagine. Gli adattatori di memoria vengono lasciati fuori, perché vengono dai profili dei giocatori;
- si rifiuta di scrivere qualsiasi cosa se un modulo di adattatore non si importa (le pagine perderebbero quei giochi);
- scrive `docs/game-<id adattatore>.md` per ogni adattatore e `docs/games.md` con la tabella di panoramica, ed elimina le pagine degli adattatori che non esistono più;
- prende "Cosa viene registrato", "Da dove viene", "Come attivarlo", gli assi, il flag multigiocatore e "Verificato" dai campi dell'adattatore;
- trasforma la docstring del modulo in "Come funziona". Scrivi le docstring nello stile di testo semplice che i moduli già usano, e che lo script converte: paragrafi; elenchi con `*`, `-` o `1.`; layout ed esempi rientrati sotto la riga che li introduce (diventano blocchi di codice); un titolo sottolineato con trattini, oppure una breve riga di titolo con il suo testo rientrato subito sotto (diventano titoli);
- elenca le chiavi statistiche che il codice dell'adattatore imposta per nome - `.stat("key", ...)`, entrambi i lati di un'espressione `if`, e i pattern di f-string come `score.{team}` - nelle classi dell'adattatore e nelle funzioni di supporto che usa. Le chiavi prese da una variabile (una tabella dei campi del gioco) non vengono elencate;
- decide "Positions" dal `axes.units` dell'adattatore (una nota che inizia con "no" o "none" significa nessuna posizione) e da ciò che il suo codice scrive.

Non modificare le pagine generate a mano: cambia l'adattatore ed esegui di nuovo lo script. La tabella in [Tutti i giochi in una tabella](watcher.md) è l'output di `python -m heat3d_watch games --markdown`.
