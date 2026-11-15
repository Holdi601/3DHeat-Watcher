---
title: "Rocket League (spelstatus)"
nav_order: 39
lang: "sv"
source: game-rocketleague-stats.md
source_hash: "fd70d0540bb9"
nav_exclude: true
search_exclude: true
---
# Rocket League (spelstatus) {#rocket-league-game-state}

När du spelar Rocket League sparar watchern det som spelet rapporterar till program på din egen dator, så att du senare kan titta på det på en karta i 3DHeat-visaren.

*Tekniska detaljer: adapter `rocketleague-stats`, slag [`gsi`](sources-and-rules.md); den körs medan `RocketLeague.exe` är igång och letar efter ny data var 0,05 s.*

## Vad som spelas in {#what-is-recorded}

- bollträffar med bollens plats (XYZ, Unreal-enheter), vem som träffade och hastigheterna
- mål med nedslagsplatsen, målskytt, assistent och hastighet; stolpträffar med platsen
- statistikflödet (demoleringar, räddningar, skott, episka räddningar, ...), avsparkar, repriser, matchstart och slut, vinnare
- egna mål, assists, räddningar, skott, demos, bollkontakter, poängen och lagens poäng, från UpdateState
- varje spelares slutrad vid matchens slut
- dina egna rader som `me`: spelaren som anges i inställningarna (`config --set player_names.rocketleague-stats=<namn>`), annars den som spelets kamera följer utanför repriser
- inga bilpositioner: API:t har inga

## Var datan kommer ifrån {#where-it-comes-from}

Stats API: TCP-JSON-ström från 127.0.0.1:49123 (Port i &lt;RL>\TAGame\Config\TAStatsAPI.ini eller DefaultStatsAPI.ini)

## Så slår du på det {#how-to-switch-it-on}

`python -m heat3d_watch setup rocketleague-stats --apply` (sätter PacketSendRate=30), starta sedan Rocket League

Skriv kommandot i en terminal som öppnats i watcherns mapp (se [Innan du börjar](before-you-start.md)). Om det misslyckas säger sista raden varför; [Installera och köra](installing-and-running.md) går igenom de vanliga orsakerna.

`python -m heat3d_watch setup rocketleague-stats` listar vilka filer den skulle ändra; `python -m heat3d_watch setup rocketleague-stats --apply` ändrar dem och sparar originalet som `<fil>.heat3d-backup` (se [Kommandon](commands.md#setup)). Den skriver `rocketleague-stats: changed: ...` för varje ändring, eller `rocketleague-stats: nothing to change` när den redan är påslagen.

## Så fungerar det {#how-it-works}

Rocket League: det officiella Stats API:t, ett lokalt uttag dit spelet skriver matchdata.

Påslaget i `<RL>\TAGame\Config\TAStatsAPI.ini` - eller `DefaultStatsAPI.ini`
när den inte finns, vilket spelet bara läser då - under
`[TAGame.MatchStatsExporter_TA]`:

```text
PacketSendRate   UpdateState-meddelanden per sekund; 0 (standard) stänger av API:t, högst 120
Port             TCP-porten spelet lyssnar på, standard 49123 (WebPort 49124 är en WebSocket-kopia)
```

Spelet är servern: en klient ansluter till 127.0.0.1:49123 och läser en ström
av JSON-objekt `{"Event": namn, "Data": {...}}` (en del versioner skickar Data som en
JSON-sträng), ett efter ett utan separatorer. Händelser skickas i den tick de inträffar, oberoende av
takten:

```text
UpdateState   MatchGuid, Players[] (Name, PrimaryId, Shortcut, TeamNum 0 blå / 1 orange,
              Score, Goals, Shots, Assists, Saves, Touches, CarTouches, Demos; bilens tillstånd
              bara för åskådare), Game (Teams[], TimeSeconds, bOvertime, Ball {Speed,
              TeamNum}, bReplay, bHasWinner, Winner, Arena, bHasTarget, Target)
BallHit       Players[] (Name, Shortcut, TeamNum), Ball {PreHitSpeed, PostHitSpeed, Location {X,Y,Z}}
GoalScored    GoalSpeed, GoalTime, ImpactLocation {X,Y,Z}, Scorer, Assister, BallLastTouch
CrossbarHit   BallLocation {X,Y,Z}, BallSpeed, ImpactForce, BallLastTouch
StatfeedEvent EventName, Type, MainTarget, SecondaryTarget
MatchEnded    WinnerTeamNum
MatchCreated, MatchInitialized, CountdownBegin, RoundStarted, GoalReplayStart/WillEnd/End,
MatchPaused/Unpaused, PodiumStart, ReplayCreated, MatchDestroyed, ClockUpdatedSeconds
```

Platser är Unreal-enheter (centimeter), Z uppåt; planen är ungefär 8200 x 10240
med målen vid Y = +-5120. Bilarnas positioner är inte en del av API:t: det som har
en plats är bollen där den träffades, gjorde mål eller träffade stolpen.

Varje meddelande sparas också helt (3DHeats konverterarregel, docs/converters.md
i visarens förråd): `heat.raw.parquet`, `type` är meddelandets händelsenamn, `text` objektet
så som det kom från strömmen. En UpdateState som är byte för byte samma som den
före (en pausad match, en meny) sparas en gång och räknas i meta.json:s
`unchanged_replies`. Meddelanden mellan matcher väntar i en kö till nästa matchs
session; det som är kvar när spelet stängs får en egen session. Tecken mellan
objekt som inte är JSON sparas som "junk".

Källor: <https://www.rocketleague.com/en/developer/stats-api> (den officiella sidan);
fältens skrivning och TCP-ramningen bekräftade mot rlstatsapi-klienten
(<https://docs.rs/crate/rlstatsapi>, MIT; läst bara för fakta).

## Positioner och axlar {#positions-and-axes}

| | |
|---|---|
| Positioner sparas | ja |
| Upp-axel | `z` |
| Enheter | Unreal-enheter (centimeter) |
| Speglad för visaren | ingen |
| Enhetsskala (`scale`: visaren multiplicerar positionerna med den) | 1 |

Dessa läggs i varje sessions `meta.json` (`axes`) och, när sessionen har positioner, i `heat.parquet`:s fotnot, så att 3DHeat-visaren vrider och skalar raderna själv - se [Datan](the-data.md).

## Flerspelarläge {#multiplayer}

- Markerat som spelat online (`multiplayer`): **ja**. `games --markdown` visar detta som "tillåtet (läser bara det spelet publicerar)".
- Slag `gsi`: den läser bara det spelet eller plattformen lämnar ut (ett gränssnitt för spelstatus eller ett lokalt API som spelet tillhandahåller), så den spelar in även i onlinespel som offline; flaggan avgör bara om minne någonsin får läsas.
- Minne: **aldrig** läst av den här adaptern. Bara `memory`-adaptrar läser minne, och aldrig för ett spel som är markerat som spelat online - se [Källor och regler](sources-and-rules.md).

## Statistik som sparas {#statistics-recorded}

Statistiknycklar som den här adapterns kod sätter med namn (varje sessions `stats` i `meta.json` och tabellen `stats` i `watcher.sqlite`):

`bad_packets`, `demolished`, `other_goals`, `overtime`, `result`, `team_goals`

En nyckel i klammer fylls i vid körning (`score.{team}` är en nyckel per lag). Nycklar som koden tar från en tabell med spelets fält eller från spelets egna statistiknamn finns inte i listan; "Vad som spelas in" ovan nämner dem.

## Fullständighet {#completeness}

watchern följer 3DHeats [konverterarregel](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md): det källan innehåller läses eller sparas, aldrig slängs. Utöver raderna sparas varje paket, sida, rad eller svar som adaptern tar emot helt i sessionens `heat.raw.parquet` (kolumnerna `time`, `ms`, `type`, `used`, `payload`, `text` och sedan eventuella fält som sparats med namn; `used` markerar det som också blev rader), och `meta.json`:s `selfCheck.completeness` räknar varje `type` - `lost` är 0.

**Läses**

- BallHit (plats, vem, lag, hastigheter före och efter), GoalScored (nedslagsplats, målskytt, assistent, hastighet, måltid), CrossbarHit (plats, sista kontakt, hastighet, kraft), StatfeedEvent (händelse, typ, huvud- och sekundärt mål), MatchEnded (vinnare, resultat), varje annan händelses namn som en rad
- från UpdateState: arenan, kamerans mål utanför repriser (vem `me` är), lagens poäng, varje spelares mål, assists, räddningar, skott, demos, bollkontakter, bilkontakter och poäng (den egna som statistik, allas som `player_result` vid matchens slut); övertid från ClockUpdatedSeconds

**Sparas råa**

- varje meddelande helt så som det kom från strömmen (`text`), under sitt eget Event-namn: `UpdateState` (varje spelares PrimaryId och Shortcut, klockan, bollens hastighet och lag, lagnamn och färger, repris- och vinnarflaggor, och bilens tillstånd där spelet skickar det), `BallHit`, `GoalScored` (med bollens sista kontakt), `CrossbarHit`, `StatfeedEvent`, `MatchCreated`, `MatchInitialized`, `CountdownBegin`, `RoundStarted`, `GoalReplayStart`, `GoalReplayWillEnd`, `GoalReplayEnd`, `MatchPaused`, `MatchUnpaused`, `MatchEnded`, `PodiumStart`, `ReplayCreated`, `MatchDestroyed`, `ClockUpdatedSeconds` och varje händelse en senare version lägger till
- en UpdateState som är byte för byte samma som den före (pausad, menyer) sparas en gång och räknas (`unchanged_replies` i meta.json)
- meddelanden mellan matcher: vid sin egen tid före nästa matchs start; efter den sista matchen, i en egen session (`raw_only` i meta.json)
- `unreadable`: ett objekt som inte är ett Stats API-meddelande; `junk`: tecken mellan objekt

**Finns inte**

- bilpositioner och bilens tillstånd medan man spelar: spelet skickar dem bara till åskådare
- UpdateState mellan två utskick: spelet skickar PacketSendRate per sekund (setup sätter 30, spelet tillåter upp till 120); händelserna skickas i den tick de inträffar
- WebSocket-kopian på WebPort (49124): samma meddelanden som TCP-porten, inte lästa två gånger

**Storlek**: en UpdateState är 1-3 KB för sex spelare, 30 per sekund: ungefär 100-300 MB per timme i `raw.bin` medan en match pågår, en tiondel eller mindre i zstd-filen `heat.raw.parquet` (uppskattat från det dokumenterade formatet, inte mätt på spelet)

## Verifierat {#verified}

testad på meddelanden i det dokumenterade formatet, skickade av en falsk lokal server; ännu inte testad mot spelet

## Källa {#source}

[heat3d_watch/adapters/rocketleague.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/rocketleague.py)

<!-- Generated from the adapter by tools/gen_game_pages.py; change the adapter and run it again rather than editing this page. -->
