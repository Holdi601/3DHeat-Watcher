---
title: "Steam-statistik (plattform)"
nav_order: 42
lang: "sv"
source: game-steam-stats.md
source_hash: "09ecf3611c02"
nav_exclude: true
search_exclude: true
---
# Steam-statistik (plattform) {#steam-statistics-platform}

Watchern sparar det Steam-statistiken håller om dina spel, så att du senare kan titta på din historik som statistik och en tidslinje.

*Tekniska detaljer: adapter `steam-stats`, typ [`platform`](sources-and-rules.md); den körs hela tiden (den väntar inte på att ett spel startar) och letar efter ny data var 30 s.*

## Vad som spelas in {#what-is-recorded}

- varje statistik ett spel sparar i Steam (dess egna namn och värden), per spel, när den ändras
- prestationsupplåsningar med visningsnamn, beskrivning och upplåsningstid
- statistikändringar med gammalt värde, nytt värde och skillnad
- speltid (minuter, senaste två veckorna) och senast spelad tid

## Var den kommer ifrån {#where-it-comes-from}

Steams lokala statistikcache %STEAM%\appcache\stats\UserGameStats_&lt;account>_&lt;appid>.bin med UserGameStatsSchema_&lt;appid>.bin; speltid från %STEAM%\userdata\\&lt;account>\config\localconfig.vdf (%STEAM% från HKCU\Software\Valve\Steam SteamPath)

## Så slår du på det {#how-to-switch-it-on}

Ingenting behöver slås på: watchern läser källan så som spelet eller plattformen tillhandahåller den.

## Så fungerar det {#how-it-works}

Det launchern och grafikdrivrutinen sparar om spelandet: Steams statistik, prestationer, speltid och tidslinjer samt NVIDIAs höjdpunkter och klipp.

Ingen av dessa källor behöver att ett spel samarbetar eller körs, så de tre adaptrarna här är alltid på och tittar i ett par filer var några sekunder.

#### Steam-statistik (`steam-stats`) {#steam-statistics-steam-stats}

`<Steam>\appcache\stats\UserGameStats_<account>_<appid>.bin`, skrivs om av Steam-klienten varje gång ett spel sparar sin statistik, avkodas med schemat `UserGameStatsSchema_<appid>.bin` bredvid det (binära KeyValues, se `_steam.py`). Statistik är heltal eller decimaltal som spelet definierar dem; prestationer är bitar med en upplåsningstid i Unix-sekunder. Speltid finns i `<Steam>\userdata\<account>\config\localconfig.vdf` under apps/&lt;appid>: Playtime och Playtime2wks i minuter, LastPlayed i Unix-sekunder. Steam hittas via HKCU\Software\Valve\Steam SteamPath.
Stats API: <https://partner.steamgames.com/doc/features/achievements>

Samma modul används även för: [NVIDIA-höjdpunkter (plattform)](game-nvidia-highlights.md), [Steam Timeline (plattform)](game-steam-timeline.md).

## Positioner och axlar {#positions-and-axes}

| | |
|---|---|
| Positioner registreras | nej |
| Upåtaxel | `y` |
| Enheter | meter |
| Speglad för visaren | ingen |
| Enhetsskala (`scale`: visaren multiplicerar positionerna med den) | 1 |

Dessa läggs i varje sessions `meta.json` (`axes`) och, när sessionen har positioner, i `heat.parquet`s fotnot, så att 3DHeat-visaren vrider och skalar raderna själv – se [Data](the-data.md).

## Flerspelarläge {#multiplayer}

- Markerad som spelad online (`multiplayer`): **nej**. `games --markdown` visar detta som "single-player".
- Typ `platform`: den läser bara det spelet eller plattformen lämnar ut (det Steam eller grafikdrivrutinen sparar), så den spelar in även i onlinespel som offline; flaggan avgör bara om minnet någonsin får läsas.
- Minne: läses **aldrig** av denna adapter. Bara `memory`-adaptrar läser minne, och aldrig för ett spel markerat som spelat online – se [Källor och regler](sources-and-rules.md).

## Statistik som registreras {#statistics-recorded}

Statistiknycklar som adapterns kod sätter med namn (varje sessions `stats` i `meta.json` och tabellen `stats` i `watcher.sqlite`):

`achievements_total`, `achievements_unlocked`, `last_played`, `playtime_2wks_minutes`, `playtime_minutes`

En nyckel inom klammer fylls i vid körning (`score.{team}` är en nyckel per lag). Nycklar som koden tar från en tabell över spelets fält eller från spelets egna statistiknamn finns inte med i listan; "Vad som spelas in" ovan nämner dem.

## Fullständighet {#completeness}

Watchern följer 3DHeats [omvandlarregel](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md): det som källan innehåller läses eller behålls, aldrig kastas bort. Förutom raderna sparas varje paket, sida, rad eller svar som adaptern tar emot helt i sessionens `heat.raw.parquet` (kolumnerna `time`, `ms`, `type`, `used`, `payload`, `text` och sedan eventuella fält som behålls med namn; `used` markerar det som också blev rader), och `meta.json`s `selfCheck.completeness` räknar varje `type` – `lost` är 0.

**Läst**

- varje statistik i statistikfilen med sitt API-namn (int, float, avgrate), varje prestationsbit med sin upplåsningstid, namngiven och beskriven av schemat
- ändringar mot den senaste läsningen (gammalt, nytt, skillnad), nya upplåsningar; speltid, tvåveckorsspeltid och senast spelad från localconfig.vdf

**Behållet råa**

- `UserGameStats`: statistikfilens bytes, hela, varje gång den spelas in (`crc`, `PendingChanges`, prestationsbitar som schemat inte längre definierar och varje nyckel avkodaren hoppar över finns i den)
- `UserGameStatsSchema`: schemafilens bytes bredvid, så att statistiken kan avkodas enbart från sessionen (varje statistiks och prestations namn på alla språk, ikoner, flaggor)
- `localconfig_app`: spelets hela block ur localconfig.vdf som JSON (molnsynkens tillstånd, startalternativ, märken och varje annan nyckel Steam håller per spel) när dess speltid spelas in
- en statistikfil avkodaren inte kan läsa (avbruten mitt i skrivningen, eller ett nytt format): dess bytes och schemat i en session utan rader (`used` falskt; `unreadable` i meta.json)

**Inte tillgängligt**

- resten av localconfig.vdf (vänner, chatt, Steam-inställningar): inte spelets, och privat
- statistikvärden mellan två skrivningar: Steam skriver om filen när spelet sparar sin statistik, oftast när det stängs
- globala prestationsprocent och andra spelares statistik: de finns på Steams servrar, inte här

**Storlek**: några KB per inspelat pass, plus schemat (upp till några hundra KB för ett spel med många prestationer) – långt under 1 MB per timme spelat; zstd krymper schemats text med hälften eller mer

## Verifierad {#verified}

testad på riktiga statistikfiler och scheman från en lokal installation; ändringsdetektering testad på filer byggda i det binära KeyValues-formatet

## Källa {#source}

[heat3d_watch/adapters/platform.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/platform.py)

<!-- Generated from the adapter by tools/gen_game_pages.py; change the adapter and run it again rather than editing this page. -->
