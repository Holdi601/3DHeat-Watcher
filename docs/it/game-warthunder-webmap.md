---
title: "War Thunder (stato di gioco)"
nav_order: 47
lang: "it"
source: game-warthunder-webmap.md
source_hash: "d6026c277030"
nav_exclude: true
search_exclude: true
---
# War Thunder (stato di gioco) {#war-thunder-game-state}

Mentre giochi a War Thunder, il watcher salva ciò che il gioco comunica ai programmi sul tuo computer, così puoi guardarlo più tardi su una mappa nel visualizzatore di 3DHeat.

*Dettagli tecnici: adattatore `warthunder-webmap`, tipo [`gsi`](sources-and-rules.md); gira mentre `aces.exe` è in esecuzione e cerca nuovi dati ogni 0,5 s.*

## Cosa viene registrato {#what-is-recorded}

- la propria posizione (est/nord sulla mappa in metri; altezza da /state se sei su un aereo, altrimenti 0) due volte al secondo, direzione, velocità
- spawn e l'uscita del proprio mezzo dalla mappa (distrutto, atterrato, tornato all'hangar), una sortita per ciascuno
- altri aerei e unità di terra sulla minimappa come posizioni con id tracciati e lato (senza altezza)
- aeroporti, zone di cattura e basi una volta sola, e le zone che cambiano lato
- le righe del feed di uccisioni e danni (chi, mezzo, verbo); le uccisioni e le morti del giocatore quando il tuo nome è impostato (`config --set player_names.warthunder-webmap=<nome>`)
- spawn, distanza, altitudine massima, velocità vera massima, mezzo; uccisioni e morti con il tuo nome impostato
- ogni risposta della mappa web conservata intera in heat.raw.parquet - /state e /indicators completi, la chat, gli obiettivi della battaglia e l'immagine della mappa compresi; tra una battaglia e l'altra in una sessione tutta sua

## Da dove arriva {#where-it-comes-from}

la mappa web locale del gioco, <http://127.0.0.1:8111> (/map_info.json, /map_obj.json, /state, /indicators, /hudmsg, /gamechat, /mission.json, /map.img)

## Come attivarlo {#how-to-switch-it-on}

Non serve attivare nulla: il watcher legge la fonte così come il gioco o la piattaforma la fornisce.

## Come funziona {#how-it-works}

War Thunder: la mappa web locale del gioco su <http://127.0.0.1:8111>.

Il gioco serve la pagina che un secondo schermo o un telefono può mostrare (la "mappa web"), e il JSON che c'è dietro, mentre è in esecuzione - in ogni modalità, multigiocatore compreso:

```text
/map_info.json   {"map_min": [x, y], "map_max": [x, y], "grid_steps", "grid_zero", "map_generation",
                  "hud_type", "valid"}: l'estensione della mappa in metri; valid false in hangar
/map_obj.json   [{"type": aircraft|ground_model|airfield|capture_zone|bombing_point|defending_point|
                  respawn_base_*|..., "icon": Player|Fighter|Bomber|Mediumtank|SPAA|..., "color": "#rrggbb",
                  "x", "y" (0..1 dell'immagine della mappa, y verso il basso), "dx", "dy" (direzione),
                  airfield "sx", "sy", "ex", "ey"}]: ciò che mostra la minimappa, il proprio mezzo con icon "Player"; nessun id, nessuna altezza
/state           {"valid", "H, m", "TAS, km/h", "IAS, km/h", "M", "Vy, m/s", ...}: valori di volo,
                  validi solo in un aereo
/indicators      {"valid", "army": air|tank|..., "type": il mezzo}
/hudmsg?lastEvt=N&lastDmg=M   {"events": [...], "damage": [...]} più recenti degli id dati, ciascuno
                  {"id", "msg", "sender", "enemy", "mode", "time"}; le righe di danno hanno la forma
                  "Nome (Mezzo) shot down Nome (Mezzo)"
/gamechat?lastId=N  la chat più recente dell'id dato, [{"id", "msg", "sender", "enemy", "mode", "time"}]
/mission.json    gli obiettivi della battaglia e il loro stato
/map.img         l'immagine della mappa su cui la pagina disegna gli oggetti
```

Ogni risposta viene conservata intera nel file accessorio grezzo della sessione sotto il suo endpoint (map_info, map_obj, state, indicators, hudmsg, gamechat, mission, map_img); tra una battaglia e l'altra le risposte vanno in una sessione tutta loro.

Una posizione sulla mappa diventa metri con l'estensione: u = min_x + x \* (max_x - min_x) est, v = max_y - y \* (max_y - min_y) nord (la y dell'immagine scende). Le righe sono x = u, y = altezza (`H, m` del proprio aereo; 0 per tutto il resto), z = v, quindi Y è verso l'alto; z è specchiata per il visualizzatore così che il nord non venga disegnato a sud.

I colori distinguono i lati come li vede il giocatore: il proprio in giallo (#faC81E di default), squadra in verde, alleati in blu (#174DFF), nemici in rosso (#f40C00); le palette per il daltonismo li cambiano, quindi conta la tonalità, non il valore esatto. Il gioco non dà nomi alle unità sulla mappa e non dà id agli oggetti: qui gli altri oggetti ricevono gli id seguendoli da una richiesta all'altra (il più vicino dello stesso tipo e icona), il che può scambiare due aerei dello stesso tipo che passano vicini. Anche il nome del giocatore non è nell'API: va indicato nelle impostazioni (`config --set player_names.warthunder-webmap=<tuo nome>`) e le righe del feed di uccisioni che riguardano il giocatore diventano uccisioni e morti; senza, vengono registrate come feed di uccisioni.

Fonti: la pagina del gioco stesso su <http://127.0.0.1:8111> e il suo JSON; i dati di fatto come documentati dal progetto JoyPro 2 (docs/telemetry-recording.md; GPL, usato solo per i fatti).

## Posizioni e assi {#positions-and-axes}

| | |
|---|---|
| Posizioni registrate | sì |
| Asse verso l'alto | `y` |
| Unità | metri (est/nord della mappa; altezza solo per il proprio aereo) |
| Specchiato per il visualizzatore | `z` |
| Scala delle unità (`scale`: il visualizzatore moltiplica le posizioni per questo valore) | 1 |

Questi valori finiscono in `meta.json` (`axes`) di ogni sessione e, quando la sessione ha delle posizioni, nel footer di `heat.parquet`, così il visualizzatore di 3DHeat ruota e scala le righe da solo - vedi [I dati](the-data.md).

## Multigiocatore {#multiplayer}

- Segnato come giocato online (`multiplayer`): **sì**. `games --markdown` lo mostra come "consentito (legge solo ciò che il gioco pubblica)".
- Tipo `gsi`: legge solo ciò che il gioco o la piattaforma consegna (una game-state integration o un'API locale che il gioco offre), quindi registra anche nel gioco online oltre che offline; il flag decide solo se la memoria può mai essere letta.
- Memoria: **mai** letta da questo adattatore. Solo gli adattatori `memory` leggono la memoria, e mai per un gioco segnato come giocato online - vedi [Fonti e regole](sources-and-rules.md).

## Statistiche registrate {#statistics-recorded}

Chiavi statistiche che il codice di questo adattatore imposta per nome (`stats` di ogni sessione in `meta.json` e la tabella `stats` di `watcher.sqlite`):

`bad_packets`, `deaths`, `distance_m`, `hits_dealt`, `hits_taken`, `kills`, `max_altitude_m`, `max_tas_kmh`, `spawns`, `vehicle`

Una chiave tra parentesi graffe viene completata durante l'esecuzione (`score.{team}` è una chiave per squadra). Le chiavi che il codice prende da una tabella dei campi del gioco o dai nomi statistici del gioco non sono in questo elenco; "Cosa viene registrato" qui sopra le nomina.

## Completezza {#completeness}

Il watcher segue la [regola del convertitore](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md) di 3DHeat: ciò che la fonte contiene viene letto o conservato, mai scartato. Oltre alle righe, ogni pacchetto, pagina, riga o risposta che l'adattatore riceve viene conservato intero in `heat.raw.parquet` della sessione (colonne `time`, `ms`, `type`, `used`, `payload`, `text`, poi ogni campo conservato per nome; `used` segna ciò che è diventato anche righe), e `selfCheck.completeness` in `meta.json` conta ogni `type` - `lost` è 0.

**Letto**

- /map_info.json: l'estensione della mappa e la griglia (metri, l'id della mappa) in meta.json; una non valida termina la battaglia
- /map_obj.json (due volte al secondo): il proprio mezzo, altri aerei e unità di terra (id tracciati, lato dal colore, icona, direzione, colore) e aeroporti, zone e basi come righe
- /state (due volte al secondo, in un aereo): altezza, TAS, IAS, Mach e Vy sulle righe proprie
- /indicators (ogni 2 s): tipo di armata e di mezzo
- /hudmsg (una volta al secondo): le righe del feed di uccisioni e danni come uccisioni, morti, colpi e righe del feed; gli altri eventi HUD come righe

**Conservato grezzo**

- ogni risposta intera, `text` il JSON così come l'ha inviato il gioco, sotto il suo endpoint: `map_info`, `map_obj`, `state`, `indicators`, `hudmsg`, `gamechat`, `mission`; `map_img` i byte dell'immagine della mappa come `payload`, una volta per battaglia
- ciò che solo il file accessorio grezzo contiene: ogni campo di /state oltre i cinque letti (AoA, AoS, Ny, Wx, manetta, giri, carburante, ... - l'insieme cambia da un aereo all'altro), ogni campo di /indicators (gli strumenti di cabina degli aerei, la velocità, la marcia, l'equipaggio e lo stabilizzatore dei carri), le altre chiavi degli oggetti della mappa (color[], blink, icon_bg, estremità degli aeroporti), sender, enemy e mode di hudmsg, la chat (/gamechat, una volta al secondo), gli obiettivi della battaglia e il loro stato (/mission.json, ogni 10 s in battaglia), le righe dette prima che il watcher partisse
- tra le battaglie (hangar, caricamento) le risposte vanno in una sessione tutta loro, segnata `between_battles` in meta.json, che non ha righe

**Non disponibile**

- nomi, id e altezze dei mezzi degli altri giocatori: la mappa web non li ha (gli id qui sono dati seguendo gli oggetti da una richiesta all'altra); il feed di uccisioni nomina i giocatori senza posizioni
- tutto ciò che è fuori dalla mappa web: i replay del gioco sono letti dal convertitore dei replay di War Thunder, e la memoria del gioco non viene mai letta (gioco online)
- /map_obj.json più di due volte al secondo: la frequenza delle richieste resta bassa, così il server web del gioco non viene sovraccaricato

**Dimensione**: circa 50-120 MB all'ora di JSON prima di zstd in battaglia (map_obj 5-15 KB due volte al secondo, state circa 1,5 KB due volte al secondo, indicators ogni 2 s, la chat e le righe HUD piccole) più l'immagine della mappa una volta per battaglia (sotto 2 MB); 1-2 MB all'ora tra una battaglia e l'altra (l'aspetto della mappa due volte al secondo, HUD e chat una volta, ogni risposta breve); zstd riduce bene il JSON ripetuto di oltre dieci volte

## Verificato {#verified}

testato con un server locale finto che serve risposte nel formato della mappa web del gioco; non ancora testato con il gioco in esecuzione

## Sorgente {#source}

[heat3d_watch/adapters/warthunder.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/warthunder.py)

<!-- Generated from the adattatore by tools/gen_game_pages.py; change the adattatore and run it again rather than editing this page. -->
