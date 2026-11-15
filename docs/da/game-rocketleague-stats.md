---
title: "Rocket League (spiltilstand)"
nav_order: 39
lang: "da"
source: game-rocketleague-stats.md
source_hash: "fd70d0540bb9"
nav_exclude: true
search_exclude: true
---
# Rocket League (spiltilstand) {#rocket-league-game-state}

Mens du spiller Rocket League, gemmer watcheren det, spillet melder til programmer på din egen computer, så du senere kan se det på et kort i 3DHeat-vieweren.

*Tekniske detaljer: adapter `rocketleague-stats`, type [`gsi`](sources-and-rules.md); den kører, mens `RocketLeague.exe` kører, og leder efter nye data hver 0.05 s.*

## Hvad der registreres {#what-is-recorded}

- boldtræf med boldens sted (XYZ, Unreal-enheder), hvem der ramte den, og hastighederne
- mål med nedslagsstedet, målscorer, assistgiver og hastighed; stolpe-træf med stedet
- statistikfeed (nedlægninger, redninger, afslutninger, episke redninger, ...), kickoffs, replays, kampstart og -slut, vinder
- egne mål, assists, redninger, afslutninger, nedlægninger, berøringer, score og holdenes score, fra UpdateState
- hver spillers endelige linje ved kampens slutning
- dine egne rækker som `me`: spilleren navngivet i indstillingerne (`config --set player_names.rocketleague-stats=<name>`), ellers den spiller kameraet følger uden for replays
- ingen bilpositioner: API'et har dem ikke

## Hvor data kommer fra {#where-it-comes-from}

Stats API: TCP JSON-strøm fra 127.0.0.1:49123 (port i <RL>\TAGame\Config\TAStatsAPI.ini eller DefaultStatsAPI.ini)

## Sådan slår du det til {#how-to-switch-it-on}

`python -m heat3d_watch setup rocketleague-stats --apply` (sætter PacketSendRate=30), start derefter Rocket League

Skriv kommandoen i en terminal, der er åbnet i watcherens mappe (se [Før du går i gang](before-you-start.md)). Hvis den fejler, siger den sidste linje hvorfor; [Installation og kørsel](installing-and-running.md) dækker de almindelige årsager.

`python -m heat3d_watch setup rocketleague-stats` viser de filer, den ville ændre; `python -m heat3d_watch setup rocketleague-stats --apply` ændrer dem og gemmer originalen som `<file>.heat3d-backup` (se [Kommandoer](commands.md#setup)). Den skriver `rocketleague-stats: changed: ...` for hver ændring, eller `rocketleague-stats: nothing to change`, når den allerede er slået til.

## Sådan virker det {#how-it-works}

Rocket League: det officielle Stats API, en lokal socket spillet skriver kampdata til.

Slået til i `<RL>\TAGame\Config\TAStatsAPI.ini` - eller `DefaultStatsAPI.ini`,
når den første ikke findes, hvilket spillet kun læser i så fald - under
`[TAGame.MatchStatsExporter_TA]`:

```text
PacketSendRate   UpdateState messages per second; 0 (the default) switches the API off, at most 120
Port             the TCP port the game listens on, default 49123 (WebPort 49124 is a WebSocket copy)
```

Spillet er serveren: en klient forbinder til 127.0.0.1:49123 og læser en strøm
af JSON-objekter `{"Event": name, "Data": {...}}` (nogle builds sender Data som en
JSON-streng), én efter én uden skilletegn. Hændelser sendes på det tik, de sker, uafhængigt af
takten:

```text
UpdateState   MatchGuid, Players[] (Name, PrimaryId, Shortcut, TeamNum 0 blue / 1 orange,
              Score, Goals, Shots, Assists, Saves, Touches, CarTouches, Demos; car state
              only for spectators), Game (Teams[], TimeSeconds, bOvertime, Ball {Speed,
              TeamNum}, bReplay, bHasWinner, Winner, Arena, bHasTarget, Target)
BallHit       Players[] (Name, Shortcut, TeamNum), Ball {PreHitSpeed, PostHitSpeed, Location {X,Y,Z}}
GoalScored    GoalSpeed, GoalTime, ImpactLocation {X,Y,Z}, Scorer, Assister, BallLastTouch
CrossbarHit   BallLocation {X,Y,Z}, BallSpeed, ImpactForce, BallLastTouch
StatfeedEvent EventName, Type, MainTarget, SecondaryTarget
MatchEnded    WinnerTeamNum
MatchCreated, MatchInitialized, CountdownBegin, RoundStarted, GoalReplayStart/WillEnd/End,
MatchPaused/Unpaused, PodiumStart, ReplayCreated, MatchDestroyed, ClockUpdatedSeconds
```

Positioner er Unreal-enheder (centimeter), Z op; banen er cirka 8200 x 10240
med målene ved Y = +-5120. Bilernes positioner er ikke en del af API'et: det, der har et
sted, er bolden, hvor den blev ramt, scoret eller ramte stolpen.

Hver besked gemmes også hel (3DHeats konverterregel, docs/converters.md
i viewerens repository): `heat.raw.parquet`, `type` er beskedens Event-navn, `text` objektet
som det kom fra strømmen. En UpdateState, der er byte for byte den foregående (en pauset kamp, en menu), gemmes én gang
og tælles i meta.jsons `unchanged_replies`. Beskeder mellem kampe venter i en kø til den næste
kamps session; det, der er tilbage, når spillet lukkes, får en session for sig selv.
Tegn mellem objekterne, som ikke er JSON, gemmes som "junk".

Kilder: <https://www.rocketleague.com/en/developer/stats-api> (den officielle side);
feltnavnenes skrivemåde og TCP-rammen bekræftet mod rlstatsapi-klienten
(<https://docs.rs/crate/rlstatsapi>, MIT; læst kun for fakta).

## Positioner og akser {#positions-and-axes}

| | |
|---|---|
| Positioner registreret | ja |
| Op-akse | `z` |
| Enheder | Unreal-enheder (centimeter) |
| Spejlet for vieweren | ingen |
| Enhedsskala (`scale`: vieweren ganger positionerne med den) | 1 |

Disse går ind i hver sessions `meta.json` (`axes`) og, når sessionen har positioner, ind i `heat.parquet`s footer, så 3DHeat-vieweren selv drejer og skalerer rækkerne - se [Dataene](the-data.md).

## Flerspiller {#multiplayer}

- Markeret som spillet online (`multiplayer`): **ja**. `games --markdown` viser dette som "tilladt (læser kun det spillet udleverer)".
- Type `gsi`: den læser kun det, spillet eller platformen udleverer (en game-state-integration eller lokal API spillet tilbyder), så den optager også i onlinespil såvel som offline; flaget afgør kun, om hukommelse nogensinde må læses.
- Hukommelse: **aldrig** læst af denne adapter. Kun `memory`-adaptere læser hukommelse, og aldrig for et spil markeret som spillet online - se [Kilder og regler](sources-and-rules.md).

## Statistik der registreres {#statistics-recorded}

Statistiknøgler, som denne adapters kode sætter ved navn (hver sessions `stats` i `meta.json` og tabellen `stats` i `watcher.sqlite`):

`bad_packets`, `demolished`, `other_goals`, `overtime`, `result`, `team_goals`

En nøgle i klammer udfyldes under kørslen (`score.{team}` er én nøgle pr. hold). Nøgler som koden tager fra en tabel over spillets felter eller fra spillets egne statistiknavne står ikke på listen; "Hvad der registreres" ovenfor nævner dem.

## Fuldstændighed {#completeness}

Watcheren følger 3DHeats [konverterregel](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md): det kilden indeholder, læses eller gemmes, aldrig smidt væk. Ud over rækkerne gemmes hver pakke, side, linje eller svar, adapteren modtager, hel i sessionens `heat.raw.parquet` (kolonnerne `time`, `ms`, `type`, `used`, `payload`, `text`, plus ethvert felt gemt under sit navn; `used` markerer det, der også blev rækker), og `meta.json`s `selfCheck.completeness` tæller hver `type` - `lost` er 0.

**Læst**

- BallHit (sted, hvem, hold, hastigheder før og efter), GoalScored (nedslagssted, målscorer, assistgiver, hastighed, måltid), CrossbarHit (sted, sidste berøring, hastighed, kraft), StatfeedEvent (hændelse, type, hoved- og sekundært mål), MatchEnded (vinder, resultat), hver anden hændelses navn som en række
- fra UpdateState: arenaen, kameraets mål uden for replays (hvem `me` er), holdenes score, hver spillers mål, assists, redninger, afslutninger, nedlægninger, berøringer, bilberøringer og score (egne som statistik, alles som `player_result`-række ved kampens slutning); overtid fra ClockUpdatedSeconds

**Gemt råt**

- hver besked hel, som den kom fra strømmen (`text`), under sit eget Event-navn: `UpdateState` (hver spillers PrimaryId og Shortcut, uret, boldens hastighed og hold, holdnavne og farver, replay- og vinderflag, og bilens tilstand hvor spillet sender den), `BallHit`, `GoalScored` (med boldens sidste berøring), `CrossbarHit`, `StatfeedEvent`, `MatchCreated`, `MatchInitialized`, `CountdownBegin`, `RoundStarted`, `GoalReplayStart`, `GoalReplayWillEnd`, `GoalReplayEnd`, `MatchPaused`, `MatchUnpaused`, `MatchEnded`, `PodiumStart`, `ReplayCreated`, `MatchDestroyed`, `ClockUpdatedSeconds` og enhver hændelse en senere build tilføjer
- en UpdateState, der er byte for byte den foregående (pauset, menuer), gemmes én gang og tælles (`unchanged_replies` i meta.json)
- beskeder mellem kampe: på deres eget tidspunkt før den næste kamps start; efter den sidste kamp, i en session for sig selv (`raw_only` i meta.json)
- `unreadable`: et objekt der ikke er en Stats API-besked; `junk`: tegn mellem objekterne

**Ikke tilgængeligt**

- bilpositioner og bilens tilstand under spil: spillet sender dem kun til tilskuere
- UpdateState mellem to udsendelser: spillet sender PacketSendRate pr. sekund (`setup` sætter 30, spillet tillader op til 120); hændelserne sendes på det tik, de sker
- WebSocket-kopien på WebPort (49124): de samme beskeder som TCP-porten, ikke læst to gange

**Størrelse**: en UpdateState er 1-3 KB for seks spillere, 30 i sekundet: cirka 100-300 MB i timen i `raw.bin`, mens en kamp kører, og en tiendedel eller mindre i den zstd-komprimerede `heat.raw.parquet` (estimeret ud fra det dokumenterede format, ikke målt på spillet)

## Verificeret {#verified}

testet på beskeder i det dokumenterede format sendt af en falsk lokal server; ikke testet mod spillet

## Kilde {#source}

[heat3d_watch/adapters/rocketleague.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/rocketleague.py)

<!-- Generated from the adapter by tools/gen_game_pages.py; change the adapter and run it again rather than editing this page. -->
