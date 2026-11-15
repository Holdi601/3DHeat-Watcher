---
title: "Dota 2 (stanje igre)"
nav_order: 13
lang: "bs"
source: game-dota2-gsi.md
source_hash: "100a0d704bbe"
nav_exclude: true
search_exclude: true
---
# Dota 2 (stanje igre) {#dota-2-game-state}

Dok igrate Dota 2, watcher sprema ono što igra javlja programima na vašem vlastitom računaru, da to poslije možete pogledati na mapi u pregledniku 3DHeat.

*Tehnički detalji: adapter `dota2-gsi`, vrsta [`gsi`](sources-and-rules.md); radi dok radi `dota2.exe` i svakih 0,05 s traži nove podatke.*

## Šta se snima {#what-is-recorded}

- pozicija vlastitog heroja (svjetski X/Y, Dota jedinice; bez visine) dok je živ
- spawn, smrti (s vremenom respawna) i respawnovi vlastitog heroja
- ubistva, iz rasta broja ubistava
- uništene zgrade, Roshan, događaji igre (roshan_killed, aegis_picked_up, ...), stanja igre, rezultat
- ubistva, smrti, asistencije, last hitovi, denyji, zlato, GPM, XPM, nivo, heroj

## Odakle dolazi {#where-it-comes-from}

Game State Integration: HTTP POST-ovi na 127.0.0.1:3312, podešeni datotekom &lt;Dota>\game\dota\cfg\gamestate_integration\gamestate_integration_heat3d.cfg

## Kako to uključiti {#how-to-switch-it-on}

`python -m heat3d_watch setup dota2-gsi --apply`, zatim pokrenite Dota 2 (čita datoteku pri pokretanju)

Komandu upišite u terminal otvoren u folderu watchera (vidite [Prije nego počnete](before-you-start.md)). Ako ne uspije, zadnja linija kaže zašto; [Instalacija i pokretanje](installing-and-running.md) opisuje uobičajene uzroke.

`python -m heat3d_watch setup dota2-gsi` navodi datoteke koje bi promijenio; `python -m heat3d_watch setup dota2-gsi --apply` ih mijenja i čuva original kao `<file>.heat3d-backup` (vidite [Komande](commands.md#setup)). Za svaku promjenu ispisuje `dota2-gsi: changed: ...`, ili `dota2-gsi: nothing to change` kad je već uključeno.

Postavke iz varijabli okruženja:

- `HEAT3D_DOTA_GSI_PORT`: port na koji igra šalje (zadano 3312); cfg datoteka igre mora navesti isti port

## Kako radi {#how-it-works}

Valve Game State Integration: Counter-Strike 2 i Dota 2 javljaju lokalnom web serveru šta se dešava.

Obje igre pri pokretanju čitaju svaku datoteku `gamestate_integration_*.cfg` u svom cfg folderu,
a otad šalju JSON dokument POST-om na `uri` svake datoteke kad god se
stanje promijeni (najviše svakih `throttle` sekundi, i svakih `heartbeat` sekundi
kad se ništa ne mijenja). Watcher je taj web server: sluša samo na 127.0.0.1,
na svaki POST odmah odgovara s 200 i posao obavlja u vlastitoj poll niti.

```text
Counter-Strike 2  <CS2>\game\csgo\cfg\gamestate_integration_heat3d.cfg      port 3311
Dota 2            <Dota>\game\dota\cfg\gamestate_integration\gamestate_integration_heat3d.cfg   port 3312
```

Šta se igraču šalje - a time i šta se može snimiti - jeste ono što igra
dopušta da igrač vidi:

- CS2: `provider` (vlastiti steamid), `map` (ime, način, faza warmup/live/
  intermission/gameover, runda, rezultat team_ct/team_t), `round` (faza
  freezetime/live/over, bomba postavljena/eksplodirala/deaktivirana, win_team), `player` (igrač
  koji se *gleda*: vi sami dok ste živi, saigrač nakon smrti) sa
  `state` (zdravlje, armor, novac, round_kills, round_killhs, round_totaldmg),
  `match_stats` (kills, assists, deaths, mvps, score), `position` i `forward`
  kao stringovi "x, y, z" u svjetskim jedinicama (inči, Z gore), `weapons`; `bomb` samo za
  gledaoce. Pozicije drugih igrača (`allplayers_*`) šalju se samo
  gledaocima i GOTV-u, pa se ne traže.
- Dota 2: `map` (matchid, game_state, game_time, clock_time, win_team), `player`
  (kills, deaths, assists, last_hits, denies, gold, gpm, xpm, team_name), `hero`
  (xpos/ypos u svjetskim jedinicama, level, alive, respawn_seconds), `buildings`
  (zdravlje po tornju/barakama/ancientu), `roshan`, `events` (roshan_killed,
  aegis_picked_up, ...). Visine nema: z je 0. Traže se i čuvaju cijeli:
  `abilities`, `items`, `draft`, `wearables`, `minimap`, `couriers`,
  `neutralitems`, `league` (igra šalje ono što ima igračev vlastiti klijent;
  koji od njih nešto sadrže dok igrate, a ne gledate, nije testirano).

Svaki dokument se čuva i cijeli (pravilo konvertera programa 3DHeat,
docs/converters.md u repozitoriju preglednika): `heat.raw.parquet`, `type`
"gsi", `text` je JSON onako kako je poslan - samo je token iz cfg datoteke zacrnjen, jer je to
vlastita tajna watchera, a ne podatak igre. Dokumenti poslani dok nijedan meč nije otvoren
(meniji, učitavanje, između mečeva) čekaju u `Backlog` i idu u sesiju sljedećeg
meča, prije njenog početka; ono što ostane kad se igra zatvori dobiva
vlastitu sesiju koja drži samo to. Nečitljivi postovi i postovi s
pogrešnim tokenom također se čuvaju ("gsi-unreadable", "gsi-bad-auth").

Izvori: <https://developer.valvesoftware.com/wiki/Counter-Strike:_Global_Offensive_Game_State_Integration>
(format koji je CS2 zadržao), <https://github.com/antonpup/CounterStrike2GSI> i
<https://github.com/antonpup/Dota2GSI> (liste polja; MIT, čitano samo radi činjenica).

Isti modul služi i: [Counter-Strike 2 (stanje igre)](game-cs2-gsi.md).

## Pozicije i ose {#positions-and-axes}

| | |
|---|---|
| Pozicije se snimaju | da |
| Osa gore | `z` |
| Jedinice | Dotine svjetske jedinice (z je uvijek 0) |
| Zrcaljeno za preglednik | `y` |
| Skala jedinica (`scale`: preglednik njome množi pozicije) | 1 |

Ovo ide u `meta.json` svake sesije (`axes`) i, kad sesija ima pozicije, u podnožje datoteke `heat.parquet`, pa preglednik 3DHeat sam rotira i skalira redove - vidite [Podaci](the-data.md).

## Multiplayer {#multiplayer}

- Označeno kao igrano online (`multiplayer`): **da**. `games --markdown` to prikazuje kao "dozvoljeno (čita samo ono što igra objavljuje)".
- Vrsta `gsi`: čita samo ono što igra ili platforma daje (game-state integracija ili lokalni API koji igra služi), pa snima i u online igri kao i offline; zastavica odlučuje samo smije li se memorija ikad čitati.
- Memorija: ovaj adapter je **nikad** ne čita. Memoriju čitaju samo `memory` adapteri, i to nikad za igru označenu kao igranu online - vidite [Izvori i pravila](sources-and-rules.md).

## Zabilježene statistike {#statistics-recorded}

Ključevi statistika koje kod ovog adaptera postavlja po imenu (`stats` svake sesije u `meta.json` i tabela `stats` u `watcher.sqlite`):

`bad_auth`, `bad_packets`, `dropped_packets`, `hero`, `level`, `result`, `roshan_kills_seen`

Ključ u vitičastim zagradama dovršava se za vrijeme rada (`score.{team}` je jedan ključ po timu). Ključevi koje kod uzima iz tabele polja igre ili iz igrinih vlastitih imena statistika nisu na ovoj listi; "Šta se snima" iznad ih navodi.

## Potpunost {#completeness}

Watcher slijedi 3DHeatovo [pravilo konvertera](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md): ono što izvor drži čita se ili čuva, nikad ne odbacuje. Osim redova, svaki paket, stranica, linija ili odgovor koji adapter primi čuva se cijel u `heat.raw.parquet` sesije (kolone `time`, `ms`, `type`, `used`, `payload`, `text`, zatim svako polje čuvano po imenu; `used` označava šta je postalo i redovi), a `selfCheck.completeness` u `meta.json` broji svaki `type` - `lost` je 0.

**Čita se**

- pozicija (x/y) vlastitog heroja, živ, nivo, zdravlje, najveće zdravlje, mana, najveća mana; spawn, smrti s vremenom respawna, respawnovi
- ubistva (broj ubistava raste); ubistva, smrti, asistencije, last hitovi, denyji, zlato, GPM, XPM, net worth, nivo i heroj kao statistike
- uništene zgrade, Roshan pao i vratio se, svaki unos u `events` jednom, stanja igre, pobjednik

**Čuva se sirovo**

- `gsi`: svaki dokument koji igra pošalje, cijel, onako kako je poslan (`text`), `used` je true kad je pročitan u meču - svih petnaest komponenti koje cfg datoteka traži: provider, map (dan/noć, pauza, cooldowni wardova, rezultati), player (pouzdano i nepouzdano zlato, nizovi, lista ubistava, izdate komande, ...), hero (buffovi, talenti, Aghanim, atributi), abilities, items, buildings, roshan, events, draft, wearables, minimap, couriers, neutralitems, league, i igrin `previously`/`added` diff
- dokumenti iz menija, učitavanja i između mečeva: čuvaju se na isti način, u svom vremenu prije početka sljedećeg meča; poslije zadnjeg meča, u vlastitoj sesiji (`raw_only` u meta.json)
- `gsi-unreadable`: post koji nije JSON objekt, njegovi bajtovi kao `payload` i `length`
- `gsi-bad-auth`: post s drugim tokenom od onog u cfg datoteci

**Nije dostupno**

- visina: igra šalje samo x i y
- ostali heroji dok igrate: igra šalje vlastitog heroja, a svakog igrača samo gledaocima (tada se čuva sirovo, ne crta); nekoliko komponenti (draft, minimap, couriers) nosi samo ono što ima igračev vlastiti klijent - što je dok igrate netestirano
- stanja između postova: najviše jedan svakih 0,1 s (`throttle`), svakih 10 s kad se ništa ne mijenja
- token iz cfg datoteke, zacrnjen u svakom sačuvanom dokumentu: vlastita tajna watchera, a ne podatak igre
- postovi preko 10.000 na čekanju (watcher je zastao) broje se kao `dropped_packets` i ne čuvaju se; post veći od 4 MB čuva se kao `gsi-unreadable` s dužinom, ali bez bajtova

**Veličina**: sa svim komponentama dokument jednog igrača je oko 5-15 KB, šalje se do 10 puta u sekundi (sat se mijenja pri svakom postu): oko 100-500 MB na sat u `raw.bin` dok meč traje, otprilike desetina toga u zstd `heat.raw.parquet`; gledaočev, sa svakim igračem i minimapom, nekoliko puta toliko (procijenjeno iz objavljenog formata, nije mjereno na igri)

## Provjereno {#verified}

testirano na dokumentima u objavljenom GSI formatu poslanim adapteru koji radi; neprovjereno na igri koja radi

## Izvor {#source}

[heat3d_watch/adapters/gsi.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/gsi.py)

<!-- Generated from the adapter by tools/gen_game_pages.py; change the adapter and run it again rather than editing this page. -->
