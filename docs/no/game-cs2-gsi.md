---
title: "Counter-Strike 2 (spilltilstand)"
nav_order: 9
lang: "no"
source: game-cs2-gsi.md
source_hash: "2eda1106e11f"
nav_exclude: true
search_exclude: true
---
# Counter-Strike 2 (spilltilstand) {#counter-strike-2-game-state}

Mens du spiller Counter-Strike 2, lagrer watcheren det spillet melder til programmer på din egen datamaskin, slik at du senere kan se på det på et kart i 3DHeat-vieweren.

*Tekniske detaljer: adapter `cs2-gsi`, type [`gsi`](sources-and-rules.md); den kjører mens `cs2.exe` går og ser etter nye data hvert 0,05 s.*

## Hva som tas opp {#what-is-recorded}

- egen posisjon (verden XYZ, tommer) og synsretning, opptil 10 ganger i sekundet mens du lever
- spawn (første gang hver runde sees, og gjenoppstandelser) og dødsfall (helse til 0, eller antall dødsfall)
- drap med aktivt våpen, fra kampstatistikken
- runder (start, slutt, vinner), bombe plantet/desarmert/eksplodert, kampfaser og resultat
- drap, assists, dødsfall, MVP-er, poengsum, penger, skade, hodeskuddsdrap, runder vunnet og tapt

## Hvor det kommer fra {#where-it-comes-from}

Game State Integration: HTTP-POST til 127.0.0.1:3311, satt opp av &lt;CS2>\game\csgo\cfg\gamestate_integration_heat3d.cfg

## Slik slår du det på {#how-to-switch-it-on}

`python -m heat3d_watch setup cs2-gsi --apply`, start deretter CS2 (spillet leser filen ved oppstart)

Skriv kommandoen i en terminal som er åpnet i watcher-mappen (se [Før du starter](before-you-start.md)). Hvis den feiler, sier siste linje hvorfor. [Installere og kjøre](installing-and-running.md) dekker de vanlige årsakene.

`python -m heat3d_watch setup cs2-gsi` lister filene den ville endret. `python -m heat3d_watch setup cs2-gsi --apply` endrer dem og tar vare på originalen som `<file>.heat3d-backup` (se [Kommandoer](commands.md#setup)). Den skriver `cs2-gsi: changed: ...` for hver endring, eller `cs2-gsi: nothing to change` når det allerede er slått på.

Innstillinger fra miljøvariabler:

- `HEAT3D_CS2_GSI_PORT`: porten spillet sender til (standard 3311); cfg-filen i spillet må oppgi samme port

## Slik fungerer det {#how-it-works}

Valve Game State Integration: Counter-Strike 2 og Dota 2 forteller en lokal webtjener hva som skjer.

Begge spillene leser hver `gamestate_integration_*.cfg` i cfg-mappen sin når de starter, og fra da av sender de et JSON-dokument til hver fils `uri` hver gang tilstanden endrer seg (høyst hver `throttle` sekunder, og hver `heartbeat` sekunder når ingenting endrer seg). Watcheren er den webtjeneren: den lytter bare på 127.0.0.1, svarer 200 på hver POST med en gang og gjør jobben i sin egen poll-tråd.

```text
Counter-Strike 2  <CS2>\game\csgo\cfg\gamestate_integration_heat3d.cfg      port 3311
Dota 2            <Dota>\game\dota\cfg\gamestate_integration\gamestate_integration_heat3d.cfg   port 3312
```

Hva en spiller får tilsendt - og dermed hva som kan tas opp - bestemmes av hva spillet mener en spiller har lov til å se:

- CS2: `provider` (din egen steamid), `map` (navn, modus, fase warmup/live/intermission/gameover, runde, team_ct/team_t-poengsum), `round` (fase freezetime/live/over, bombe plantet/eksplodert/desarmert, win_team), `player` (spilleren som *blir fulgt*: deg selv mens du lever, en lagkamerat etter at du er død) med `state` (health, armor, money, round_kills, round_killhs, round_totaldmg), `match_stats` (kills, assists, deaths, mvps, score), `position` og `forward` som strenger "x, y, z" i verdensenheter (tommer, Z opp), `weapons`; `bomb` bare for tilskuere. Andre spilleres posisjoner (`allplayers_*`) sendes bare til tilskuere og GOTV, så de blir ikke bedt om.
- Dota 2: `map` (matchid, game_state, game_time, clock_time, win_team), `player` (kills, deaths, assists, last_hits, denies, gold, gpm, xpm, team_name), `hero` (xpos/ypos i verdensenheter, level, alive, respawn_seconds), `buildings` (helse per tårn/kaserne/ancient), `roshan`, `events` (roshan_killed, aegis_picked_up, ...). Det finnes ingen høyde: z er 0. Også bedt om, og tatt vare på helt: `abilities`, `items`, `draft`, `wearables`, `minimap`, `couriers`, `neutralitems`, `league` (spillet sender det din egen klient har; hvilke av dem som har innhold mens du spiller og ikke bare ser på, er ikke testet).

Hvert dokument tas også vare på helt (konverteringsregelen til 3DHeat, docs/converters.md i viewerens repository): `heat.raw.parquet`, `type` "gsi", `text` er JSON-en slik den ble postet - bare cfg-filens token er blanket, for den er watcherens egen hemmelighet, ikke spilldata. Dokumenter som postes mens ingen kamp er åpen (menyer, lasting, mellom kamper) venter i en `Backlog` og går inn i neste kamps økt, før starten; det som er igjen når spillet lukkes, får en egen økt med bare dem. Uleselige poster og poster med feil token tas også vare på ("gsi-unreadable", "gsi-bad-auth").

Kilder: <https://developer.valvesoftware.com/wiki/Counter-Strike:_Global_Offensive_Game_State_Integration> (formatet CS2 beholdt), <https://github.com/antonpup/CounterStrike2GSI> og <https://github.com/antonpup/Dota2GSI> (feltlister; MIT, lest bare for fakta).

Samme modul brukes også av: [Dota 2 (spilltilstand)](game-dota2-gsi.md).

## Posisjoner og akser {#positions-and-axes}

| | |
|---|---|
| Posisjoner registreres | ja |
| Opp-akse | `z` |
| Enheter | tommer (Hammer-enheter) |
| Speilet for visningen | `y` |
| Enhetsskala (`scale`: visningen ganger posisjonene med den) | 1 |

Disse havner i hver økts `meta.json` (`axes`) og, når økten har posisjoner, i `heat.parquet`s footer, slik at 3DHeat-vieweren snur og skalerer radene selv - se [Dataene](the-data.md).

## Flerspiller {#multiplayer}

- Merket som spilt på nett (`multiplayer`): **ja**. `games --markdown` viser dette som "allowed (reads only what the game publishes)".
- Type `gsi`: den leser bare det spillet eller plattformen gir ut (en game-state integration eller lokal API som spillet tilbyr), så den tar opp også i nettspill, både på nett og offline; flagget avgjør bare om minnet noen gang kan leses.
- Minne: **aldri** lest av denne adapteren. Bare `memory`-adaptere leser minne, og aldri for et spill som er merket som spilt på nett - se [Kilder og regler](sources-and-rules.md).

## Statistikk som registreres {#statistics-recorded}

Statistikknøkler som denne adapterens kode setter med navn (hver økts `stats` i `meta.json` og tabellen `stats` i `watcher.sqlite`):

`bad_auth`, `bad_packets`, `dropped_packets`, `money`, `result`, `score_other`, `score_own`

En nøkkel i klammer fylles ut ved kjøretid (`score.{team}` er én nøkkel per lag). Nøkler som koden henter fra en tabell over spillets felt eller fra spillets egne statistikknavn står ikke i denne listen; "Hva som tas opp" over nevner dem.

## Fullstendighet {#completeness}

Watcheren følger 3DHeats [konverteringsregel](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md): det kilden inneholder, leses eller tas vare på, og slettes aldri. I tillegg til radene tas hver pakke, side, linje eller svar adapteren mottar, vare på hel i øktens `heat.raw.parquet` (kolonnene `time`, `ms`, `type`, `used`, `payload`, `text`, pluss felt som tas vare på med navn; `used` markerer det som også ble til rader), og `selfCheck.completeness` i `meta.json` teller hver `type` - `lost` er 0.

**Leses**

- den fulgte spillerens posisjon, synsretning, helse, rustning, penger, aktivt våpen, hjelm, desarmeringssett, blits/røyk/brann-mengder og utstyrsverdi, på hver posisjonsrad mens det er spillerens egen (provider steamid = player steamid)
- spawn, dødsfall (helse til 0, eller dødsantallet i kampstatistikken), drap (når drapstallet øker)
- kampfaser, runder (fryse-tid, live, over, vinner), bombe plantet/desarmert/eksplodert, resultatet
- drap, assists, dødsfall, MVP-er, poengsum, penger, skade, hodeskuddsdrap, runder vunnet og tapt som statistikk

**Tatt vare på rått**

- `gsi`: hvert dokument spillet sender, helt, slik det ble postet (`text`), `used` sann når det ble lest i en kamp - provider (versjon, tidsstempel), map (modus, lagnavn, påfølgende rundetap, timeouts, serieseire, `round_wins` med hver rundes vinnerbetingelse), round, den fulgte spilleren (klan, observatørplass, aktivitet, hvert våpen med skin, ammunisjon og reserve), bomb, nedtellinger for faser, og spillets egen `previously`/`added`-forskjell fra posten før
- dokumenter fra menyer, lasting og mellom kamper: tatt vare på på samme måte, til sitt eget tidspunkt før neste kamps start; etter siste kamp i en egen økt (`raw_only` i meta.json)
- `gsi-unreadable`: en post som ikke er et JSON-objekt, med bytene som `payload` og `length`
- `gsi-bad-auth`: en post med en annen token enn cfg-filens

**Ikke tilgjengelig**

- andre spillere (`allplayers_*`) og granater (`allgrenades`): spillet sender dem bare til tilskuere og GOTV, og watcheren ber ikke om dem (Kilder og regler); en demo har alle spillere - se [Counter-Strike 2 (repriser)](game-cs2-demos.md)
- tilstander mellom postene: spillet poster høyst hver 0,1 s (`throttle`) og bare ved endring, ellers hver 10 s (`heartbeat`)
- cfg-filens token, blanket i hvert tatt vare på dokument: watcherens egen hemmelighet, ikke spilldata
- poster utover 10 000 som venter (watcheren har hengt seg) telles som `dropped_packets` og tas ikke vare på; en post over 4 MB tas vare på som `gsi-unreadable` med lengden, men uten bytene

**Størrelse**: et spillers dokument er 2-4 KB, postet opptil 10 ganger i sekundet mens noe endrer seg: omtrent 30-150 MB per time i `raw.bin` mens kampen pågår, en tidel av det eller mindre i zstd-komprimert `heat.raw.parquet` (estimert fra det publiserte formatet, ikke målt på spillet)

## Verifisert {#verified}

testet på dokumenter i det publiserte GSI-formatet postet til den kjørende adapteren; installasjon og oppslag av cfg-mappen testet på en lokal installasjon; ikke testet mot det kjørende spillet

## Kilde {#source}

[heat3d_watch/adapters/gsi.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/gsi.py)

<!-- Generated from the adapter by tools/gen_game_pages.py; change the adapter and run it again rather than editing this page. -->
