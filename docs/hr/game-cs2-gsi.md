---
title: "Counter-Strike 2 (stanje igre)"
nav_order: 9
lang: "hr"
source: game-cs2-gsi.md
source_hash: "2eda1106e11f"
nav_exclude: true
search_exclude: true
---
# Counter-Strike 2 (stanje igre) {#counter-strike-2-game-state}

Dok igrate Counter-Strike 2, watcher sprema ono što igra javlja programima na vašem računalu, pa to kasnije možete pogledati na karti u 3DHeat pregledniku.

*Tehnički podaci: adapter `cs2-gsi`, vrsta [`gsi`](sources-and-rules.md); radi dok je `cs2.exe` pokrenut i traži nove podatke svakih 0,05 s.*

## Što se bilježi {#what-is-recorded}

- vlastita pozicija (svjetske koordinate XYZ, u inčima) i smjer gledanja do 10 puta u sekundi dok ste živi
- pojavljivanja (prvo viđenje u svakoj rundi, ponovna pojavljivanja) i smrti (zdravlje na 0, ili broj smrti)
- ubojstva s aktivnim oružjem, iz statistike utakmice
- runde (početak, kraj, pobjednik), bomba postavljena, deaktivirana ili eksplodirala, faze utakmice i rezultat
- ubojstva, asistencije, smrti, MVP-ovi, rezultat, novac, šteta, ubojstva u glavu, pobijedene i izgubljene runde

## Odakle dolazi {#where-it-comes-from}

Game State Integration: HTTP POST zahtjevi na 127.0.0.1:3311, podešeni datotekom &lt;CS2>\game\csgo\cfg\gamestate_integration_heat3d.cfg

## Kako ga uključiti {#how-to-switch-it-on}

`python -m heat3d_watch setup cs2-gsi --apply`, zatim pokrenite CS2 (igra datoteku čita pri pokretanju)

Upišite naredbu u terminal otvoren u mapi watchera (vidi [Prije nego što počnete](before-you-start.md)). Ako ne uspije, zadnji redak kaže zašto; [Instalacija i pokretanje](installing-and-running.md) opisuje najčešće uzroke.

`python -m heat3d_watch setup cs2-gsi` navodi datoteke koje bi promijenio; `python -m heat3d_watch setup cs2-gsi --apply` ih mijenja i čuva original kao `<file>.heat3d-backup` (vidi [Naredbe](commands.md#setup)). Za svaku promjenu ispisuje `cs2-gsi: changed: ...`, a kad je već uključeno, `cs2-gsi: nothing to change`.

Postavke iz varijabli okruženja:

- `HEAT3D_CS2_GSI_PORT`: port na koji igra šalje podatke (zadano 3311); cfg datoteka igre mora navesti isti port

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

Izvori: <https://developer.valvesoftware.com/wiki/Counter-Strike:_Global_Offensive_Game_State_Integration> (format koji je CS2 zadržao), <https://github.com/antonpup/CounterStrike2GSI> i <https://github.com/antonpup/Dota2GSI> (popisi polja; MIT, pročitano samo radi činjenica).

Isti modul služi i za: [Dota 2 (stanje igre)](game-dota2-gsi.md).

## Pozicije i osi {#positions-and-axes}

| | |
|---|---|
| Pozicije se bilježe | da |
| Os prema gore | `z` |
| Jedinice | inči (Hammer jedinice) |
| Zrcaljeno za preglednik | `y` |
| Mjerilo jedinice (`scale`: preglednik pozicije množi njime) | 1 |

Ovo ide u `meta.json` svake sesije (`axes`) i, kad sesija ima pozicije, u podnožje `heat.parquet`, pa 3DHeat preglednik sam okreće i skalira retke - vidi [Podaci](the-data.md).

## Više igrača {#multiplayer}

- Označeno kao igra na mreži (`multiplayer`): **da**. `games --markdown` to prikazuje kao "allowed (reads only what the game publishes)".
- Vrsta `gsi`: čita samo ono što igra ili platforma daje (game-state integration ili lokalni API koji igra poslužuje), pa bilježi i u igri na mreži i izvan nje; zastavica odlučuje samo smije li se ikad čitati memorija.
- Memorija: ovaj adapter je **nikad** ne čita. Samo adapteri `memory` čitaju memoriju, i nikad za igru označenu kao igra na mreži - vidi [Izvori i pravila](sources-and-rules.md).

## Statistika koja se bilježi {#statistics-recorded}

Ključevi statistike koje kod ovog adaptera postavlja po imenu (`stats` svake sesije u `meta.json` i tablica `stats` u `watcher.sqlite`):

`bad_auth`, `bad_packets`, `dropped_packets`, `money`, `result`, `score_other`, `score_own`

Ključ u vitičastim zagradama dovršava se pri radu (`score.{team}` je jedan ključ za svaki tim). Ključevi koje kod uzima iz tablice polja igre ili iz vlastitih imena statistike igre nisu na ovom popisu; navedeni su u odjeljku "Što se bilježi" gore.

## Potpunost {#completeness}

Watcher slijedi [pravilo pretvarača 3DHeata](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md): ono što izvor sadrži se čita ili čuva, nikad se ne odbacuje. Osim redaka, svaki paket, stranica, redak ili odgovor koji adapter primi čuva se cjelovito u `heat.raw.parquet` sesije (stupci `time`, `ms`, `type`, `used`, `payload`, `text`, pa svako polje koje je sačuvano po imenu; `used` označava što je postalo i retkom), a `selfCheck.completeness` u `meta.json` broji svaki `type` - `lost` je 0.

**Čita se**

- vlastita pozicija praćenog igrača, smjer gledanja, zdravlje, oklop, novac, aktivno oružje, kaciga, komplet za deaktivaciju, količine bljeskalica/dima/vatre i vrijednost opreme, na svakom retku pozicije dok je to vlastiti igrač (steamid pružatelja = steamid igrača)
- pojavljivanja, smrti (zdravlje na 0, ili broj smrti iz statistike utakmice), ubojstva (rast broja ubojstava)
- faze utakmice, runde (vrijeme zaleđivanja, uživo, završeno, pobjednik), bomba postavljena, deaktivirana, eksplodirala, rezultat
- ubojstva, asistencije, smrti, MVP-ovi, rezultat, novac, šteta, ubojstva u glavu, pobijedene i izgubljene runde kao statistika

**Čuva se u izvornom obliku**

- `gsi`: svaki dokument koji igra šalje, cjelovit, kako je poslan (`text`), `used` je true kad je pročitan tijekom utakmice - pružatelj (verzija, vremenska oznaka), map (način, imena timova, uzastopni gubici rundi, istek vremena, pobjede u seriji, `round_wins` sa uvjetom pobjede svake runde), round, praćeni igrač (klan, slot promatrača, aktivnost, svako oružje sa skinom, streljivom i rezervom), bomba, odbrojavanja faza, i razliku `previously`/`added` koju igra šalje u odnosu na prethodni POST
- dokumenti iz izbornika, učitavanja i između utakmica: čuvaju se na isti način, u vlastitom trenutku prije početka sljedeće utakmice; nakon zadnje utakmice, u vlastitoj sesiji (`raw_only` u meta.json)
- `gsi-unreadable`: POST koji nije JSON objekt, njegovi bajtovi kao `payload` i `length`
- `gsi-bad-auth`: POST s drugim tokenom od tokena iz cfg datoteke

**Nije dostupno**

- drugi igrači (`allplayers_*`) i granate (`allgrenades`): igra ih šalje samo promatračima i GOTV-u, a watcher ih ne traži (Izvori i pravila); demo ima svakog igrača - vidi [Counter-Strike 2 (replay-i)](game-cs2-demos.md)
- stanja između POST-ova: igra šalje najviše svakih 0,1 s (`throttle`) i samo pri promjeni, a inače svakih 10 s (`heartbeat`)
- token iz cfg datoteke, zamijenjen prazninom u svakom sačuvanom dokumentu: tajna watchera, a ne podatak igre
- POST-ovi preko 10.000 na čekanju (watcher je zapeo) broje se kao `dropped_packets` i ne čuvaju se; POST veći od 4 MB čuva se kao `gsi-unreadable` s duljinom, ali bez bajtova

**Veličina**: dokument jednog igrača je 2-4 KB, šalje se do 10 puta u sekundi dok se nešto mijenja: oko 30-150 MB na sat u `raw.bin` dok utakmica traje, a desetina toga ili manje u zstd `heat.raw.parquet` (procijenjeno iz objavljenog formata, nije izmjereno na igri)

## Provjereno {#verified}

testirano na dokumentima u objavljenom GSI formatu poslanim pokrenutom adapteru; pronalaženje instalacije i cfg mape testirano na lokalnoj instalaciji; nije testirano s pokrenutom igrom

## Izvor {#source}

[heat3d_watch/adapters/gsi.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/gsi.py)

<!-- Generated from the adapter by tools/gen_game_pages.py; change the adapter and run it again rather than editing this page. -->
