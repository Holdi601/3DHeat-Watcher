---
title: "Counter-Strike 2 (spiltilstand)"
nav_order: 9
lang: "da"
source: game-cs2-gsi.md
source_hash: "2eda1106e11f"
nav_exclude: true
search_exclude: true
---
# Counter-Strike 2 (spiltilstand) {#counter-strike-2-game-state}

Mens du spiller Counter-Strike 2, gemmer watcheren det, spillet melder, i programmer på din egen computer, så du senere kan se det på et kort i 3DHeat-vieweren.

*Tekniske detaljer: adapter `cs2-gsi`, slags [`gsi`](sources-and-rules.md); den kører, mens `cs2.exe` kører, og kigger efter nye data hver 0,05 s.*

## Hvad der optages {#what-is-recorded}

- egen position (verdens XYZ, tommer) og synsretning, op til 10 Hz mens du er i live
- spawns (hver rundes første observation, og genopstandelser) og dødsfald (liv ned til 0, eller antallet af dødsfald)
- drab med det aktive våben, fra kampstatistikken
- runder (start, slut, vinder), bombe plantet/desarmeret/eksploderet, kampfaser og resultatet
- drab, assists, dødsfald, MVP'er, score, penge, skade, headshot-drab, vundne og tabte runder

## Hvor det kommer fra {#where-it-comes-from}

Game State Integration: HTTP-POST'er til 127.0.0.1:3311, sat op af &lt;CS2>\game\csgo\cfg\gamestate_integration_heat3d.cfg

## Sådan slår du det til {#how-to-switch-it-on}

`python -m heat3d_watch setup cs2-gsi --apply`, derefter start CS2 (den læser filen ved start)

Skriv kommandoen i en terminal, der er åbnet i watcherens mappe (se [Før du går i gang](before-you-start.md)). Hvis det fejler, siger den sidste linje hvorfor; [Installation og kørsel](installing-and-running.md) dækker de almindelige årsager.

`python -m heat3d_watch setup cs2-gsi` viser, hvilke filer den ville ændre; `python -m heat3d_watch setup cs2-gsi --apply` ændrer dem og gemmer originalen som `<file>.heat3d-backup` (se [Kommandoer](commands.md#setup)). Den skriver `cs2-gsi: changed: ...` for hver ændring, eller `cs2-gsi: nothing to change`, når den allerede er slået til.

Indstillinger fra miljøvariabler:

- `HEAT3D_CS2_GSI_PORT`: porten spillet sender til (standard 3311); spillets cfg-fil skal nævne den samme port

## Sådan virker det {#how-it-works}

Valve Game State Integration: Counter-Strike 2 og Dota 2 fortæller en lokal webserver, hvad der sker.

Begge spil læser hver `gamestate_integration_*.cfg` i deres cfg-mappe, når de starter, og sender derefter et JSON-dokument til hver fils `uri`, når tilstanden ændrer sig (højst hver `throttle` sekund, og hver `heartbeat` sekund når intet ændrer sig). Watcheren er den webserver: den lytter kun på 127.0.0.1, svarer hver POST med 200 med det samme og laver arbejdet i sin egen poll-tråd.

```text
Counter-Strike 2  <CS2>\game\csgo\cfg\gamestate_integration_heat3d.cfg      port 3311
Dota 2            <Dota>\game\dota\cfg\gamestate_integration\gamestate_integration_heat3d.cfg   port 3312
```

Hvad en spiller sendes - og dermed hvad der kan optages - er det, spillet bestemmer, at en spiller må se:

- CS2: `provider` (den egne steamid), `map` (navn, tilstand warmup/live/
  intermission/gameover, runde, score for team_ct/team_t), `round` (fase
  freezetime/live/over, bombe plantet/eksploderet/desarmeret, win_team), `player` (den spiller der *ses*: en selv når du er i live, en holdkammerat efter død) med
  `state` (liv, rustning, penge, round_kills, round_killhs, round_totaldmg),
  `match_stats` (drab, assists, dødsfald, mvps, score), `position` og `forward`
  som "x, y, z"-strenge i verdensenheder (tommer, Z op), `weapons`; `bomb` kun for
  tilskuere. Andre spilleres positioner (`allplayers_*`) sendes kun til
  tilskuere og GOTV, så de bliver ikke bedt om.
- Dota 2: `map` (matchid, game_state, game_time, clock_time, win_team), `player`
  (kills, deaths, assists, last_hits, denies, gold, gpm, xpm, team_name), `hero`
  (xpos/ypos i verdensenheder, level, alive, respawn_seconds), `buildings`
  (liv per tårn/barakke/ancient), `roshan`, `events` (roshan_killed,
  aegis_picked_up, ...). Der er ingen højde: z er 0. Også bedt om og gemt hele:
  `abilities`, `items`, `draft`, `wearables`, `minimap`, `couriers`,
  `neutralitems`, `league` (spillet sender det, spillerens egen klient har; hvilke
  af dem der indeholder noget under spil frem for tilskuer er ikke testet).

Hvert dokument gemmes også helt (3DHeat-konverterens regel,
docs/converters.md i viewerens repository): `heat.raw.parquet`, `type`
"gsi", `text` er JSON'en som sendt - kun cfg-filens token er slettet, den er
watcherens egen hemmelighed, ikke spildata. Dokumenter der sendes, mens ingen kamp er åben
(menuer, indlæsning, mellem kampe), venter i en `Backlog` og går ind i den næste
kamps session, før dens start; det der er tilbage, når spillet lukker, får en
session for sig selv, som kun indeholder dem. Ulæselige sendinger og sendinger med
forkert token gemmes også ("gsi-unreadable", "gsi-bad-auth").

Kilder: <https://developer.valvesoftware.com/wiki/Counter-Strike:_Global_Offensive_Game_State_Integration>
(formatet CS2 beholdt), <https://github.com/antonpup/CounterStrike2GSI> og
<https://github.com/antonpup/Dota2GSI> (feltlister; MIT, kun læst for fakta).

Det samme modul betjener også: [Dota 2 (spiltilstand)](game-dota2-gsi.md).

## Positioner og akser {#positions-and-axes}

| | |
|---|---|
| Positioner optaget | ja |
| Opadakse | `z` |
| Enheder | tommer (Hammer-enheder) |
| Spejlet for viewer | `y` |
| Enhedsskala (`scale`: viewer ganger positionerne med den) | 1 |

Disse går ind i hver sessions `meta.json` (`axes`) og, når sessionen har positioner, i `heat.parquet`s footer, så 3DHeat-viewer selv drejer og skalerer rækkerne - se [Dataene](the-data.md).

## Multiplayer {#multiplayer}

- Markeret som spillet online (`multiplayer`): **ja**. `games --markdown` viser dette som "allowed (reads only what the game publishes)".
- Slags `gsi`: den læser kun det, spillet eller platformen udleverer (en game-state-integration eller lokal API, spillet serverer), så den optager også i online-spil, ligesom offline; flaget afgør kun, om hukommelsen nogensinde må læses.
- Hukommelse: **aldrig** læst af denne adapter. Kun `memory`-adaptere læser hukommelse, og aldrig for et spil markeret som spillet online - se [Kilder og regler](sources-and-rules.md).

## Statistik der optages {#statistics-recorded}

Statistiknøglerne, som denne adapters kode sætter med navn (hver sessions `stats` i `meta.json` og tabellen `stats` i `watcher.sqlite`):

`bad_auth`, `bad_packets`, `dropped_packets`, `money`, `result`, `score_other`, `score_own`

En nøgle i klammer udfyldes under kørslen (`score.{team}` er én nøgle pr. hold). Nøgler som koden tager fra en tabel over spillets felter eller fra spillets egne statistiknavne står ikke på listen; "Hvad der optages" ovenfor nævner dem.

## Fuldstændighed {#completeness}

Watcheren følger 3DHeats [konverterregel](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md): det kilden indeholder bliver læst eller gemt, aldrig smidt væk. Ud over rækkerne gemmes hver pakke, side, linje eller svar adapteren modtager, helt i sessionens `heat.raw.parquet` (kolonnerne `time`, `ms`, `type`, `used`, `payload`, `text` og derefter felter der gemmes efter navn; `used` markerer det, der også blev til rækker), og `meta.json`s `selfCheck.completeness` tæller hver `type` - `lost` er 0.

**Læst**

- den iagttagne spillers position, synsretning, liv, rustning, penge, aktive våben, hjelm, defuse kit, flash/røg/ild-mængder og værdien af udstyr, på hver positionsrække mens det er spillerens egen (provider steamid = spillerens steamid)
- spawns, dødsfald (liv ned til 0, eller dødstallet fra kampstatistikken), drab (når drabstallet stiger)
- kampfaser, runder (freeze time, live, over, vinder), bombe plantet/desarmeret/eksploderet, resultatet
- drab, assists, dødsfald, MVP'er, score, penge, skade, headshot-drab, vundne og tabte runder som statistik

**Gemt rå**

- `gsi`: hvert dokument spillet sender, helt, som sendt (`text`), `used` sand når det blev læst i en kamp - provider (version, tidsstempel), map (tilstand, holdnavne, runder tabt i træk, timeouts, seriesejre, `round_wins` med hver runds vindebetingelse), round, den iagttagne spiller (klan, observatørplads, aktivitet, hvert våben med skin, ammunition og reserve), bomb, nedtællinger for faser og spillets egen `previously`/`added`-forskel fra posten før
- dokumenter fra menuer, indlæsning og mellem kampe: gemt på samme måde, til deres eget tidspunkt før næste kamps start; efter sidste kamp, i en session for sig selv (`raw_only` i meta.json)
- `gsi-unreadable`: en post der ikke er et JSON-objekt, dens bytes som `payload` og `length`
- `gsi-bad-auth`: en post med et andet token end cfg-filens

**Ikke tilgængeligt**

- andre spillere (`allplayers_*`) og granater (`allgrenades`): spillet sender dem kun til tilskuere og GOTV, og watcheren beder ikke om dem ([Kilder og regler](sources-and-rules.md)); en demo har alle spillere - se [Counter-Strike 2 (replays)](game-cs2-demos.md)
- tilstande mellem posterne: spillet sender højst hver 0,1 s (`throttle`) og kun ved en ændring, ellers hvert 10. s (`heartbeat`)
- cfg-filens token, slettet i hvert gemt dokument: watcherens egen hemmelighed, ikke spildata
- poster ud over 10.000 der venter (watcheren er gået i stå) tælles som `dropped_packets` og gemmes ikke; en post over 4 MB gemmes som `gsi-unreadable` med sin længde, men uden bytes

**Størrelse**: et spillers dokument er 2-4 KB, sendt op til 10 gange i sekundet, mens noget ændrer sig: cirka 30-150 MB i timen i `raw.bin`, mens kampen kører, og en tiendedel eller mindre i den zstd-komprimerede `heat.raw.parquet` (estimeret ud fra det offentliggjorte format, ikke målt på spillet)

## Verificeret {#verified}

testet på dokumenter i det offentliggjorte GSI-format, sendt til den kørende adapter; installationen og opslag af cfg-mappen testet på en lokal installation; ikke testet mod det kørende spil

## Kilde {#source}

[heat3d_watch/adapters/gsi.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/gsi.py)

<!-- Generated from the adapter by tools/gen_game_pages.py; change the adapter and run it again rather than editing this page. -->
