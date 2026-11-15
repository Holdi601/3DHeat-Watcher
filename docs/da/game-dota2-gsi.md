---
title: "Dota 2 (spiltilstand)"
nav_order: 13
lang: "da"
source: game-dota2-gsi.md
source_hash: "100a0d704bbe"
nav_exclude: true
search_exclude: true
---
# Dota 2 (spiltilstand) {#dota-2-game-state}

Mens du spiller Dota 2, gemmer watcheren det, spillet melder, i programmer på din egen computer, så du senere kan se det på et kort i 3DHeat-vieweren.

*Tekniske detaljer: adapter `dota2-gsi`, slags [`gsi`](sources-and-rules.md); den kører, mens `dota2.exe` kører, og kigger efter nye data hver 0,05 s.*

## Hvad der optages {#what-is-recorded}

- egen helts position (verdens X/Y, Dota-enheder; ingen højde) mens du er i live
- spawn, dødsfald (med genopstandelsestid) og genopstandelser for egen helt
- drab, fra at drabstallet stiger
- ødelagte bygninger, Roshan, spilhændelser (roshan_killed, aegis_picked_up, ...), spiltilstande, resultat
- drab, dødsfald, assists, last hits, denies, guld, GPM, XPM, level, helt

## Hvor det kommer fra {#where-it-comes-from}

Game State Integration: HTTP-POST'er til 127.0.0.1:3312, sat op af &lt;Dota>\game\dota\cfg\gamestate_integration\gamestate_integration_heat3d.cfg

## Sådan slår du det til {#how-to-switch-it-on}

`python -m heat3d_watch setup dota2-gsi --apply`, derefter start Dota 2 (den læser filen ved start)

Skriv kommandoen i en terminal, der er åbnet i watcherens mappe (se [Før du går i gang](before-you-start.md)). Hvis det fejler, siger den sidste linje hvorfor; [Installation og kørsel](installing-and-running.md) dækker de almindelige årsager.

`python -m heat3d_watch setup dota2-gsi` viser, hvilke filer den ville ændre; `python -m heat3d_watch setup dota2-gsi --apply` ændrer dem og gemmer originalen som `<file>.heat3d-backup` (se [Kommandoer](commands.md#setup)). Den skriver `dota2-gsi: changed: ...` for hver ændring, eller `dota2-gsi: nothing to change`, når den allerede er slået til.

Indstillinger fra miljøvariabler:

- `HEAT3D_DOTA_GSI_PORT`: porten spillet sender til (standard 3312); spillets cfg-fil skal nævne den samme port

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

Det samme modul betjener også: [Counter-Strike 2 (spiltilstand)](game-cs2-gsi.md).

## Positioner og akser {#positions-and-axes}

| | |
|---|---|
| Positioner optaget | ja |
| Opadakse | `z` |
| Enheder | Dota-verdensenheder (z altid 0) |
| Spejlet for viewer | `y` |
| Enhedsskala (`scale`: viewer ganger positionerne med den) | 1 |

Disse går ind i hver sessions `meta.json` (`axes`) og, når sessionen har positioner, i `heat.parquet`s footer, så 3DHeat-viewer selv drejer og skalerer rækkerne - se [Dataene](the-data.md).

## Multiplayer {#multiplayer}

- Markeret som spillet online (`multiplayer`): **ja**. `games --markdown` viser dette som "allowed (reads only what the game publishes)".
- Slags `gsi`: den læser kun det, spillet eller platformen udleverer (en game-state-integration eller lokal API, spillet serverer), så den optager også i online-spil, ligesom offline; flaget afgør kun, om hukommelsen nogensinde må læses.
- Hukommelse: **aldrig** læst af denne adapter. Kun `memory`-adaptere læser hukommelse, og aldrig for et spil markeret som spillet online - se [Kilder og regler](sources-and-rules.md).

## Statistik der optages {#statistics-recorded}

Statistiknøglerne, som denne adapters kode sætter med navn (hver sessions `stats` i `meta.json` og tabellen `stats` i `watcher.sqlite`):

`bad_auth`, `bad_packets`, `dropped_packets`, `hero`, `level`, `result`, `roshan_kills_seen`

En nøgle i klammer udfyldes under kørslen (`score.{team}` er én nøgle pr. hold). Nøgler som koden tager fra en tabel over spillets felter eller fra spillets egne statistiknavne står ikke på listen; "Hvad der optages" ovenfor nævner dem.

## Fuldstændighed {#completeness}

Watcheren følger 3DHeats [konverterregel](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md): det kilden indeholder bliver læst eller gemt, aldrig smidt væk. Ud over rækkerne gemmes hver pakke, side, linje eller svar adapteren modtager, helt i sessionens `heat.raw.parquet` (kolonnerne `time`, `ms`, `type`, `used`, `payload`, `text` og derefter felter der gemmes efter navn; `used` markerer det, der også blev til rækker), og `meta.json`s `selfCheck.completeness` tæller hver `type` - `lost` er 0.

**Læst**

- den egne helts position (x/y), i live, level, liv, maks. liv, mana, maks. mana; spawn, dødsfald med genopstandelsestid, genopstandelser
- drab (når drabstallet stiger); drab, dødsfald, assists, last hits, denies, guld, GPM, XPM, nettoværdi, level og helt som statistik
- ødelagte bygninger, Roshan nede og oppe igen, hver post i `events` én gang, spiltilstande, vinderen

**Gemt rå**

- `gsi`: hvert dokument spillet sender, helt, som sendt (`text`), `used` sand når det blev læst i en kamp - alle femten komponenter cfg-filen beder om: provider, map (dag/nat, pauset, ward-nedkølinger, scores), player (pålideligt og upålideligt guld, rækker, dræbeliste, udstedte kommandoer, ...), hero (buffs, talenter, Aghanims, attributter), abilities, items, buildings, roshan, events, draft, wearables, minimap, couriers, neutralitems, league og spillets `previously`/`added`-forskel
- dokumenter fra menuer, indlæsning og mellem kampe: gemt på samme måde, til deres eget tidspunkt før næste kamps start; efter sidste kamp, i en session for sig selv (`raw_only` i meta.json)
- `gsi-unreadable`: en post der ikke er et JSON-objekt, dens bytes som `payload` og `length`
- `gsi-bad-auth`: en post med et andet token end cfg-filens

**Ikke tilgængeligt**

- højde: spillet sender kun x og y
- de andre helte under spil: spillet sender egen helt, og hver spillers kun til tilskuere (gemt rå da, ikke tegnet); flere komponenter (draft, minimap, couriers) bærer kun det, spillerens egen klient har - hvilket under spil er utestet
- tilstande mellem posterne: højst én hver 0,1 s (`throttle`), hvert 10. s når intet ændrer sig
- cfg-filens token, slettet i hvert gemt dokument: watcherens egen hemmelighed, ikke spildata
- poster ud over 10.000 der venter (watcheren er gået i stå) tælles som `dropped_packets` og gemmes ikke; en post over 4 MB gemmes som `gsi-unreadable` med sin længde, men uden bytes

**Størrelse**: med alle komponenter er en spillers dokument cirka 5-15 KB, sendt op til 10 gange i sekundet (uret ændrer sig ved hver post): cirka 100-500 MB i timen i `raw.bin`, mens kampen kører, cirka en tiendedel i `heat.raw.parquet` (zstd); en tilskuers, med alle spillere og minimappet, flere gange det (estimeret ud fra det offentliggjorte format, ikke målt på spillet)

## Verificeret {#verified}

testet på dokumenter i det offentliggjorte GSI-format, sendt til den kørende adapter; ikke testet mod det kørende spil

## Kilde {#source}

[heat3d_watch/adapters/gsi.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/gsi.py)

<!-- Generated from the adapter by tools/gen_game_pages.py; change the adapter and run it again rather than editing this page. -->
