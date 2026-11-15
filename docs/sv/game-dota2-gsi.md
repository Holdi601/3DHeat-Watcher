---
title: "Dota 2 (spelstatus)"
nav_order: 13
lang: "sv"
source: game-dota2-gsi.md
source_hash: "100a0d704bbe"
nav_exclude: true
search_exclude: true
---
# Dota 2 (spelstatus) {#dota-2-game-state}

Medan du spelar Dota 2 sparar watchern det som spelet rapporterar till program på din egen dator, så att du senare kan titta på det på en karta i 3DHeat-visaren.

*Teknisk information: adaptern `dota2-gsi`, typ [`gsi`](sources-and-rules.md); den körs medan `dota2.exe` är igång och letar efter ny data var 0,05 s.*

## Vad som spelas in {#what-is-recorded}

- egen hjältes position (världens X/Y, Dota-enheter; ingen höjd) medan den lever
- spawn, dödsfall (med återupplivningstid) och återuppståndelser för egen hjälte
- kills, från att kill-antalet ökar
- förstörda byggnader, Roshan, spelhändelser (roshan_killed, aegis_picked_up, ...), spelllägen, resultat
- kills, dödsfall, assists, last hits, denies, guld, GPM, XPM, nivå, hjälte

## Varifrån det kommer {#where-it-comes-from}

Game State Integration: HTTP-POST till 127.0.0.1:3312, inställt i &lt;Dota>\game\dota\cfg\gamestate_integration\gamestate_integration_heat3d.cfg

## Så slår du på det {#how-to-switch-it-on}

`python -m heat3d_watch setup dota2-gsi --apply`, starta sedan Dota 2 (det läser filen vid start)

Skriv kommandot i en terminal som är öppen i watcherns mapp (se [Innan du börjar](before-you-start.md)). Om det misslyckas säger sista raden varför; [Installera och köra](installing-and-running.md) beskriver de vanligaste orsakerna.

`python -m heat3d_watch setup dota2-gsi` visar vilka filer som skulle ändras; `python -m heat3d_watch setup dota2-gsi --apply` ändrar dem och sparar originalet som `<file>.heat3d-backup` (se [Kommandon](commands.md#setup)). Den skriver `dota2-gsi: changed: ...` för varje ändring, eller `dota2-gsi: nothing to change` när det redan är på.

Inställningar från miljövariabler:

- `HEAT3D_DOTA_GSI_PORT`: porten spelet postar till (standard 3312); spelets cfg-fil måste ange samma port

## Så fungerar det {#how-it-works}

Valves Game State Integration: Counter-Strike 2 och Dota 2 berättar för en lokal webbserver vad som händer.

Båda spelen läser varje `gamestate_integration_*.cfg` i sin cfg-mapp när de startar, och skickar sedan ett JSON-dokument till varje fils `uri` när läget ändras (högst var `throttle` sekund, och var `heartbeat` sekund när inget ändras). Watchern är den webbservern: den lyssnar bara på 127.0.0.1, svarar med 200 på varje POST direkt och gör jobbet i sin egen poll-tråd.

```text
Counter-Strike 2  <CS2>\game\csgo\cfg\gamestate_integration_heat3d.cfg      port 3311
Dota 2            <Dota>\game\dota\cfg\gamestate_integration\gamestate_integration_heat3d.cfg   port 3312
```

Vad en spelare skickas - och därmed vad som kan spelas in - bestämmer spelet, utifrån vad en spelare får se:

- CS2: `provider` (det egna steamid:t), `map` (namn, läge, fas warmup/live/
  intermission/gameover, runda, team_ct/team_t-poäng), `round` (fas
  freezetime/live/over, bomb planted/exploded/defused, win_team), `player` (den
  spelare som *bevakas*: en själv när man lever, en lagkamrat efter döden) med
  `state` (health, armor, money, round_kills, round_killhs, round_totaldmg),
  `match_stats` (kills, assists, deaths, mvps, score), `position` och `forward`
  som strängar "x, y, z" i världsenheter (tum, Z uppåt), `weapons`; `bomb` bara för
  åskådare. Andra spelares positioner (`allplayers_*`) skickas bara till
  åskådare och GOTV, så de begärs inte.
- Dota 2: `map` (matchid, game_state, game_time, clock_time, win_team), `player`
  (kills, deaths, assists, last_hits, denies, gold, gpm, xpm, team_name), `hero`
  (xpos/ypos i världsenheter, level, alive, respawn_seconds), `buildings`
  (hälsa per torn/kaserner/ancient), `roshan`, `events` (roshan_killed,
  aegis_picked_up, ...). Det finns ingen höjd: z är 0. Begärs också, och sparas
  hela: `abilities`, `items`, `draft`, `wearables`, `minimap`, `couriers`,
  `neutralitems`, `league` (spelet skickar det spelarens egen klient har;
  vilka av dem som innehåller något under spelet, och inte när man åskådar, är
  inte testat).

Varje dokument sparas också helt (3DHeats omvandlarregel,
docs/converters.md i visarens repository): `heat.raw.parquet`, `type`
"gsi", `text` är JSON:en som den postades - bara cfg-filens token är gjord
oläsbar, den är watcherns egen hemlighet, inte spelets data. Dokument som postas
när ingen match är öppen (menyer, laddning, mellan matcher) väntar i en `Backlog`
och hamnar i nästa matchs session, före dess start; det som blir kvar när spelet
stängs får en egen session som bara innehåller dem. Oläsbara postningar och
postningar med fel token sparas också ("gsi-unreadable", "gsi-bad-auth").

Källor: <https://developer.valvesoftware.com/wiki/Counter-Strike:_Global_Offensive_Game_State_Integration>
(formatet CS2 behöll), <https://github.com/antonpup/CounterStrike2GSI> och
<https://github.com/antonpup/Dota2GSI> (fältlistor; MIT, lästa bara för fakta).

Samma modul används också av: [Counter-Strike 2 (spelstatus)](game-cs2-gsi.md).

## Positioner och axlar {#positions-and-axes}

| | |
|---|---|
| Positioner sparas | ja |
| Uppåtaxel | `z` |
| Enheter | Dota-världsenheter (z alltid 0) |
| Speglad för visaren | `y` |
| Enhetsskala (`scale`: visaren multiplicerar positionerna med den) | 1 |

Dessa läggs i varje sessions `meta.json` (`axes`) och, när sessionen har positioner, i `heat.parquet`:s footer, så att 3DHeat-visaren vrider och skalar raderna själv - se [Datan](the-data.md).

## Multiplayer {#multiplayer}

- Markerad som spelad online (`multiplayer`): **ja**. `games --markdown` visar detta som "tillåten (läser bara det spelet publicerar)".
- Typ `gsi`: den läser bara det spelet eller plattformen lämnar ut (en game-state integration eller lokal API som spelet erbjuder), så den spelar in även i onlinespel så väl som offline; flaggan avgör bara om minnet någonsin får läsas.
- Minne: läses **aldrig** av den här adaptern. Bara `memory`-adaptrar läser minne, och aldrig för ett spel som är markerat som spelat online - se [Källor och regler](sources-and-rules.md).

## Statistik som sparas {#statistics-recorded}

Statistiknycklar som adapterns kod sätter med namn (varje sessions `stats` i `meta.json` och tabellen `stats` i `watcher.sqlite`):

`bad_auth`, `bad_packets`, `dropped_packets`, `hero`, `level`, `result`, `roshan_kills_seen`

En nyckel inom klammerparenteser fylls i vid körning (`score.{team}` är en nyckel per lag). Nycklar som koden tar från en tabell med spelets fält eller från spelets egna statistiknamn finns inte med i den här listan; "Vad som spelas in" ovan nämner dem.

## Fullständighet {#completeness}

Watchern följer 3DHeats [omvandlarregel](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md): det källan innehåller läses eller sparas, aldrig slängs. Utöver raderna sparas varje paket, sida, rad eller svar som adaptern tar emot helt i sessionens `heat.raw.parquet` (kolumnerna `time`, `ms`, `type`, `used`, `payload`, `text`, plus eventuella fält som sparas med namn; `used` markerar det som också blev rader), och `meta.json`:s `selfCheck.completeness` räknar varje `type` - `lost` är 0.

**Läses**

- egen hjältes position (x/y), levande, nivå, hälsa, max hälsa, mana, max mana; spawn, dödsfall med återupplivningstiden, återuppståndelser
- kills (när kill-antalet ökar); kills, dödsfall, assists, last hits, denies, guld, GPM, XPM, nettovärde, nivå och hjälte som statistik
- förstörda byggnader, Roshan nere och tillbaka, varje post i `events` en gång, spelllägen, vinnaren

**Sparas råa**

- `gsi`: varje dokument spelet postar, helt, som det postades (`text`), `used` sant när det lästes under en match - alla femton komponenter som cfg-filen begär: provider, map (dag/natt, pausad, ward-nedkylningar, poäng), player (tillförlitligt och otillförlitligt guld, svit, kill-lista, utfärdade kommandon, ...), hero (buffar, talanger, Aghanim, attribut), abilities, items, buildings, roshan, events, draft, wearables, minimap, couriers, neutralitems, league och spelets `previously`/`added`-diff
- dokument från menyer, laddning och mellan matcher: sparas på samma sätt, vid sin egen tid före nästa matchs start; efter sista matchen, i en egen session (`raw_only` i meta.json)
- `gsi-unreadable`: en post som inte är ett JSON-objekt, dess bytes som `payload` och `length`
- `gsi-bad-auth`: en post med en annan token än cfg-filens

**Inte tillgängligt**

- höjd: spelet skickar bara x och y
- de andra hjältarna under spelet: spelet skickar egen hjälte, och varje spelares bara till åskådare (sparas då råa, inte ritas); flera komponenter (draft, minimap, couriers) bär bara det spelarens egen klient har - vilket under spelet är otestat
- tillstånd mellan postningar: högst en var 0,1 s (`throttle`), var 10 s när inget ändras
- cfg-filens token, gjord oläsbar i varje sparat dokument: watcherns egen hemlighet, inte spelets data
- postningar över 10 000 som väntar (watchern har stannat) räknas som `dropped_packets`, inte sparas; en post över 4 MB sparas som `gsi-unreadable` med sin längd men utan sina bytes

**Storlek**: med alla komponenter är ett spelardokument cirka 5-15 KB, postat upp till 10 gånger per sekund (klockan ändras vid varje post): ungefär 100-500 MB per timme i `raw.bin` medan matchen pågår, ungefär en tiondel i den zstd-komprimerade `heat.raw.parquet`; en åskådares, med alla spelare och minimapen, är flera gånger det (uppskattat från det publicerade formatet, inte mätt på spelet)

## Verifierad {#verified}

testad på dokument i det publicerade GSI-formatet postade till den körande adaptern; inte testad mot det körande spelet

## Källa {#source}

[heat3d_watch/adapters/gsi.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/gsi.py)

<!-- Generated from the adapter by tools/gen_game_pages.py; change the adapter and run it again rather than editing this page. -->
