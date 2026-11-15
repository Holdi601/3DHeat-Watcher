---
title: "Dota 2 (stanje igre)"
nav_order: 13
lang: "hr"
source: game-dota2-gsi.md
source_hash: "100a0d704bbe"
nav_exclude: true
search_exclude: true
---
# Dota 2 (stanje igre) {#dota-2-game-state}

Dok igrate Dota 2, watcher sprema ono što igra javlja programima na vašem računalu, pa to kasnije možete pogledati na karti u 3DHeat pregledniku.

*Tehnički podaci: adapter `dota2-gsi`, vrsta [`gsi`](sources-and-rules.md); radi dok je `dota2.exe` pokrenut i traži nove podatke svakih 0,05 s.*

## Što se bilježi {#what-is-recorded}

- pozicija vašeg heroja (svjetske X/Y, Dota jedinice; bez visine) dok je živ
- pojavljivanje, smrti (s vremenom ponovnog pojavljivanja) i ponovna pojavljivanja vašeg heroja
- ubojstva, iz rasta broja ubojstava
- uništene građevine, Roshan, događaji igre (roshan_killed, aegis_picked_up, ...), stanja igre, rezultat
- ubojstva, smrti, asistencije, zadnji udarci, odbijanja, zlato, GPM, XPM, razina, heroj

## Odakle dolazi {#where-it-comes-from}

Game State Integration: HTTP POST zahtjevi na 127.0.0.1:3312, podešeni datotekom &lt;Dota>\game\dota\cfg\gamestate_integration\gamestate_integration_heat3d.cfg

## Kako ga uključiti {#how-to-switch-it-on}

`python -m heat3d_watch setup dota2-gsi --apply`, zatim pokrenite Dota 2 (igra datoteku čita pri pokretanju)

Upišite naredbu u terminal otvoren u mapi watchera (vidi [Prije nego što počnete](before-you-start.md)). Ako ne uspije, zadnji redak kaže zašto; [Instalacija i pokretanje](installing-and-running.md) opisuje najčešće uzroke.

`python -m heat3d_watch setup dota2-gsi` navodi datoteke koje bi promijenio; `python -m heat3d_watch setup dota2-gsi --apply` ih mijenja i čuva original kao `<file>.heat3d-backup` (vidi [Naredbe](commands.md#setup)). Za svaku promjenu ispisuje `dota2-gsi: changed: ...`, a kad je već uključeno, `dota2-gsi: nothing to change`.

Postavke iz varijabli okruženja:

- `HEAT3D_DOTA_GSI_PORT`: port na koji igra šalje podatke (zadano 3312); cfg datoteka igre mora navesti isti port

## Kako radi {#how-it-works}

Valve Game State Integration: Counter-Strike 2 i Dota 2 javljaju lokalnom web poslužitelju što se događa.

Obje igre čitaju svaku `gamestate_integration_*.cfg` datoteku u svojoj cfg mapi pri pokretanju i od tada šalju JSON dokument na `uri` svake datoteke kad god se stanje promijeni (najviše svakih `throttle` sekundi, a svakih `heartbeat` sekundi kad se ništa ne mijenja). Watcher je taj web poslužitelj: sluša samo na 127.0.0.1, na svaki POST odmah odgovara s 200 i posao obavlja u svojoj niti za provjeru.

```text
Counter-Strike 2  <CS2>\game\csgo\cfg\gamestate_integration_heat3d.cfg      port 3311
Dota 2            <Dota>\game\dota\cfg\gamestate_integration\gamestate_integration_heat3d.cfg   port 3312
```

Što igrač dobiva, pa tako i što se može snimiti, odlučuje igra prema tome što igrač smije vidjeti:

- CS2: `provider` (vaš steamid), `map` (ime, način, faza warmup/live/intermission/gameover, runda, rezultat team_ct/team_t), `round` (faza freezetime/live/over, bomb planted/exploded/defused, win_team), `player` (igrač koji se *gleda*: vi dok ste živi, suigrač nakon smrti) s `state` (zdravlje, oklop, novac, round_kills, round_killhs, round_totaldmg), `match_stats` (ubojstva, asistencije, smrti, mvps, rezultat), `position` i `forward` kao nizovi "x, y, z" u svjetskim jedinicama (inči, Z prema gore), `weapons`; `bomb` samo za promatrače. Pozicije ostalih igrača (`allplayers_*`) šalju se samo promatračima i GOTV-u, pa se ne traže.
- Dota 2: `map` (matchid, game_state, game_time, clock_time, win_team), `player` (kills, deaths, assists, last_hits, denies, gold, gpm, xpm, team_name), `hero` (xpos/ypos u svjetskim jedinicama, level, alive, respawn_seconds), `buildings` (zdravlje po tornju, vojarni i drevnoj građevini), `roshan`, `events` (roshan_killed, aegis_picked_up, ...). Visina ne postoji: z je 0. Također se traže i čuvaju cjelovito: `abilities`, `items`, `draft`, `wearables`, `minimap`, `couriers`, `neutralitems`, `league` (igra šalje ono što igračev vlastiti klijent ima; koji od njih nešto drže dok igrate, a ne gledate, nije provjereno).

Svaki dokument čuva se i cjelovito (pravilo pretvarača 3DHeata, docs/converters.md u repozitoriju preglednika): `heat.raw.parquet`, `type` "gsi", `text` je JSON kako je poslan - samo token iz cfg datoteke je zamijenjen prazninom, jer je to tajna watchera, a ne podatak igre. Dokumenti poslani dok nijedna utakmica nije otvorena (izbornici, učitavanje, između utakmica) čekaju u `Backlog` i idu u sesiju sljedeće utakmice, prije njezina početka; što ostane kad se igra zatvori dobiva vlastitu sesiju koja sadrži samo njih. Nečitljivi POST-ovi i POST-ovi s krivim tokenom također se čuvaju ("gsi-unreadable", "gsi-bad-auth").

Isti modul služi i za: [Counter-Strike 2 (stanje igre)](game-cs2-gsi.md).

## Pozicije i osi {#positions-and-axes}

| | |
|---|---|
| Pozicije se bilježe | da |
| Os prema gore | `z` |
| Jedinice | Dota svjetske jedinice (z je uvijek 0) |
| Zrcaljeno za preglednik | `y` |
| Mjerilo jedinice (`scale`: preglednik pozicije množi njime) | 1 |

Ovo ide u `meta.json` svake sesije (`axes`) i, kad sesija ima pozicije, u podnožje `heat.parquet`, pa 3DHeat preglednik sam okreće i skalira retke - vidi [Podaci](the-data.md).

## Više igrača {#multiplayer}

- Označeno kao igra na mreži (`multiplayer`): **da**. `games --markdown` to prikazuje kao "allowed (reads only what the game publishes)".
- Vrsta `gsi`: čita samo ono što igra ili platforma daje (game-state integration ili lokalni API koji igra poslužuje), pa bilježi i u igri na mreži i izvan nje; zastavica odlučuje samo smije li se ikad čitati memorija.
- Memorija: ovaj adapter je **nikad** ne čita. Samo adapteri `memory` čitaju memoriju, i nikad za igru označenu kao igra na mreži - vidi [Izvori i pravila](sources-and-rules.md).

## Statistika koja se bilježi {#statistics-recorded}

Ključevi statistike koje kod ovog adaptera postavlja po imenu (`stats` svake sesije u `meta.json` i tablica `stats` u `watcher.sqlite`):

`bad_auth`, `bad_packets`, `dropped_packets`, `hero`, `level`, `result`, `roshan_kills_seen`

Ključ u vitičastim zagradama dovršava se pri radu (`score.{team}` je jedan ključ za svaki tim). Ključevi koje kod uzima iz tablice polja igre ili iz vlastitih imena statistike igre nisu na ovom popisu; navedeni su u odjeljku "Što se bilježi" gore.

## Potpunost {#completeness}

Watcher slijedi [pravilo pretvarača 3DHeata](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md): ono što izvor sadrži se čita ili čuva, nikad se ne odbacuje. Osim redaka, svaki paket, stranica, redak ili odgovor koji adapter primi čuva se cjelovito u `heat.raw.parquet` sesije (stupci `time`, `ms`, `type`, `used`, `payload`, `text`, pa svako polje koje je sačuvano po imenu; `used` označava što je postalo i retkom), a `selfCheck.completeness` u `meta.json` broji svaki `type` - `lost` je 0.

**Čita se**

- pozicija (x/y) vlastitog heroja, živ, razina, zdravlje, najveće zdravlje, mana, najveća mana; pojavljivanje, smrti s vremenom ponovnog pojavljivanja, ponovna pojavljivanja
- ubojstva (rast broja ubojstava); ubojstva, smrti, asistencije, zadnji udarci, odbijanja, zlato, GPM, XPM, neto vrijednost, razina i heroj kao statistika
- uništene građevine, Roshan dolje i natrag, svaki unos iz `events` jednom, stanja igre, pobjednik

**Čuva se u izvornom obliku**

- `gsi`: svaki dokument koji igra šalje, cjelovit, kako je poslan (`text`), `used` je true kad je pročitan tijekom utakmice - svih petnaest komponenti koje cfg datoteka traži: provider, map (dan/noć, pauza, odbrojavanja čuvara, rezultati), player (pouzdano i nepouzdano zlato, nizovi, popis ubojstava, izdane naredbe, ...), hero (bufovi, talenti, Aghanim-ovi, atributi), abilities, items, buildings, roshan, events, draft, wearables, minimap, couriers, neutralitems, league, i razliku `previously`/`added` koju igra šalje u odnosu na prethodni POST
- dokumenti iz izbornika, učitavanja i između utakmica: čuvaju se na isti način, u vlastitom trenutku prije početka sljedeće utakmice; nakon zadnje utakmice, u vlastitoj sesiji (`raw_only` u meta.json)
- `gsi-unreadable`: POST koji nije JSON objekt, njegovi bajtovi kao `payload` i `length`
- `gsi-bad-auth`: POST s drugim tokenom od tokena iz cfg datoteke

**Nije dostupno**

- visina: igra šalje samo x i y
- ostali heroji dok igrate: igra šalje vlastitog heroja, a svakog igrača samo promatračima (tada se čuva sirovo, ne crta se); nekoliko komponenti (draft, minimap, couriers) nosi samo ono što ima vlastiti klijent igrača - što, dok igrate, nije provjereno
- stanja između POST-ova: najviše jedno svakih 0,1 s (`throttle`), svakih 10 s kad se ništa ne mijenja
- token iz cfg datoteke, zamijenjen prazninom u svakom sačuvanom dokumentu: tajna watchera, a ne podatak igre
- POST-ovi preko 10.000 na čekanju (watcher je zapeo) broje se kao `dropped_packets` i ne čuvaju se; POST veći od 4 MB čuva se kao `gsi-unreadable` s duljinom, ali bez bajtova

**Veličina**: sa svim komponentama dokument jednog igrača je oko 5-15 KB, šalje se do 10 puta u sekundi (sat se mijenja pri svakom POST-u): oko 100-500 MB na sat u `raw.bin` dok utakmica traje, otprilike desetina toga u zstd `heat.raw.parquet`; gledateljev, sa svim igračima i minimapom, nekoliko puta više (procijenjeno iz objavljenog formata, nije izmjereno na igri)

## Provjereno {#verified}

testirano na dokumentima u objavljenom GSI formatu poslanim pokrenutom adapteru; nije testirano s pokrenutom igrom

## Izvor {#source}

[heat3d_watch/adapters/gsi.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/gsi.py)

<!-- Generated from the adapter by tools/gen_game_pages.py; change the adapter and run it again rather than editing this page. -->
