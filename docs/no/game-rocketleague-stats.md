---
title: "Rocket League (spilltilstand)"
nav_order: 39
lang: "no"
source: game-rocketleague-stats.md
source_hash: "fd70d0540bb9"
nav_exclude: true
search_exclude: true
---
# Rocket League (spilltilstand) {#rocket-league-game-state}

Mens du spiller Rocket League, lagrer watcheren det spillet melder til programmer på din egen datamaskin, slik at du kan se på det senere på et kart i 3DHeat-vieweren.

*Tekniske detaljer: adapter `rocketleague-stats`, type [`gsi`](sources-and-rules.md); den kjører mens `RocketLeague.exe` kjører, og ser etter nye data hvert 0,05 s.*

## Hva som lagres {#what-is-recorded}

- ballberøringer med ballens sted (XYZ, Unreal-enheter), hvem som traff den og fartene
- mål med nedslagsstedet, målscorer, målgiver og fart; stolpetreff med stedet
- statistikkstrømmen (demolerte, redninger, skudd, episke redninger, ...), avspark, repriser, kampstart og -slutt, vinner
- egne mål, målgivelser, redninger, skudd, demoleringer, berøringer, poengsum og lagenes poengsum, fra UpdateState
- hver spillers sluttlinje ved kampslutt
- dine egne rader som `me`: spilleren som er oppgitt i innstillingene (`config --set player_names.rocketleague-stats=<navn>`), ellers den spillerkameraet til spillet følger utenfor repriser
- ingen bilposisjoner: API-en har ingen

## Hvor dataene kommer fra {#where-it-comes-from}

Stats API: TCP-JSON-strøm fra 127.0.0.1:49123 (porten i &lt;RL>\TAGame\Config\TAStatsAPI.ini eller DefaultStatsAPI.ini)

## Slik slår du det på {#how-to-switch-it-on}

`python -m heat3d_watch setup rocketleague-stats --apply` (setter PacketSendRate=30), start deretter Rocket League

Skriv kommandoen i en terminal som er åpnet i watcherens mappe (se [Før du starter](before-you-start.md)). Hvis den feiler, sier siste linje hvorfor; [Installere og kjøre](installing-and-running.md) dekker de vanligste årsakene.

`python -m heat3d_watch setup rocketleague-stats` viser filene den ville endret; `python -m heat3d_watch setup rocketleague-stats --apply` endrer dem og beholder originalen som `<file>.heat3d-backup` (se [Kommandoer](commands.md#setup)). Den skriver `rocketleague-stats: changed: ...` for hver endring, eller `rocketleague-stats: nothing to change` når den allerede er på.

## Slik fungerer det {#how-it-works}

Rocket League: det offisielle Stats API-et, et lokalt uttak spillet skriver kampdata til.

Slått på i `<RL>\TAGame\Config\TAStatsAPI.ini` - eller `DefaultStatsAPI.ini`
når den ikke finnes, som spillet bare leser da - under
`[TAGame.MatchStatsExporter_TA]`:

```text
PacketSendRate   UpdateState-meldinger per sekund; 0 (standard) slår av API-et, høyst 120
Port             TCP-porten spillet lytter på, standard 49123 (WebPort 49124 er en WebSocket-kopi)
```

Spillet er tjeneren: en klient kobler seg til 127.0.0.1:49123 og leser en strøm
av JSON-objekter `{"Event": navn, "Data": {...}}` (noen bygg sender Data som en
JSON-streng), etter hverandre uten skilletegn. Hendelser sendes på tikket de skjer,
uavhengig av takten:

```text
UpdateState   MatchGuid, Players[] (Name, PrimaryId, Shortcut, TeamNum 0 blå / 1 oransje,
              Score, Goals, Shots, Assists, Saves, Touches, CarTouches, Demos; bilstate
              bare for tilskuere), Game (Teams[], TimeSeconds, bOvertime, Ball {Speed,
              TeamNum}, bReplay, bHasWinner, Winner, Arena, bHasTarget, Target)
BallHit       Players[] (Name, Shortcut, TeamNum), Ball {PreHitSpeed, PostHitSpeed, Location {X,Y,Z}}
GoalScored    GoalSpeed, GoalTime, ImpactLocation {X,Y,Z}, Scorer, Assister, BallLastTouch
CrossbarHit   BallLocation {X,Y,Z}, BallSpeed, ImpactForce, BallLastTouch
StatfeedEvent EventName, Type, MainTarget, SecondaryTarget
MatchEnded    WinnerTeamNum
MatchCreated, MatchInitialized, CountdownBegin, RoundStarted, GoalReplayStart/WillEnd/End,
MatchPaused/Unpaused, PodiumStart, ReplayCreated, MatchDestroyed, ClockUpdatedSeconds
```

Posisjoner er Unreal-enheter (centimeter), Z opp; banen er omtrent 8200 x 10240
med målene ved Y = +-5120. Bilenes posisjoner er ikke en del av API-et: det som har et
sted, er ballen der den ble truffet, scoret eller traff stolpen.

Hver melding lagres også hel (3DHeat sin regel for konvertering, docs/converters.md
i vieweren sitt depot): `heat.raw.parquet`, `type` er meldingens Event-navn, `text` er objektet slik det kom fra strømmen. En UpdateState som er byte for byte lik den før
(en pauset kamp, en meny) lagres én gang og telles i meta.json sitt
`unchanged_replies`. Meldinger mellom kamper venter i en kø til neste kamps økt; det som er igjen når spillet lukkes, får en egen økt.
Tegn mellom objekter som ikke er JSON, lagres som «junk».

Kilder: <https://www.rocketleague.com/en/developer/stats-api> (den offisielle siden);
feltenes skrivemåte og TCP-rammene bekreftet mot rlstatsapi-klienten
(<https://docs.rs/crate/rlstatsapi>, MIT; lest for fakta alene).

## Posisjoner og akser {#positions-and-axes}

| | |
|---|---|
| Posisjoner lagres | ja |
| Opp-akse | `z` |
| Enheter | Unreal-enheter (centimeter) |
| Speilvendt for vieweren | ingen |
| Enhetsskala (`scale`: vieweren ganger posisjonene med den) | 1 |

Disse havner i hver økts `meta.json` (`axes`) og, når økten har posisjoner, i `heat.parquet` sin footer, så 3DHeat-vieweren snur og skalerer radene selv - se [Dataene](the-data.md).

## Flerspiller {#multiplayer}

- Merket som spilt på nett (`multiplayer`): **ja**. `games --markdown` viser dette som «tillatt (leser bare det spillet publiserer)».
- Type `gsi`: den leser bare det spillet eller plattformen gir ut (et spilltilstand-grensesnitt eller lokalt API spillet tilbyr), så den tar opp også i nettspill, ikke bare offline; flagget avgjør bare om minne noensinne kan leses.
- Minne: **aldri** lest av denne adapteren. Bare `memory`-adaptere leser minne, og aldri for et spill merket som spilt på nett - se [Kilder og regler](sources-and-rules.md).

## Statistikk som lagres {#statistics-recorded}

Statistikknøklene denne adapterens kode setter med navn (hver økts `stats` i `meta.json` og tabellen `stats` i `watcher.sqlite`):

`bad_packets`, `demolished`, `other_goals`, `overtime`, `result`, `team_goals`

En nøkkel i klammeparenteser blir fullført under kjøring (`score.{team}` er én nøkkel per lag). Nøkler som koden henter fra en tabell med spillets felter eller fra spillets egne statistikknavn, står ikke på listen; «Hva som lagres» over nevner dem.

## Fullstendighet {#completeness}

Watcheren følger 3DHeat sin [regel for konvertering](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md): det kilden inneholder, leses eller lagres, og slettes aldri. I tillegg til radene blir hver pakke, side, linje eller respons adapteren mottar, lagret uendret i øktens `heat.raw.parquet` (kolonnene `time`, `ms`, `type`, `used`, `payload`, `text`, og alle felt som beholdes med navn; `used` markerer det som også ble til rader), og `selfCheck.completeness` i `meta.json` teller hver `type` - `lost` er 0.

**Leses**

- BallHit (sted, hvem, lag, fart før og etter), GoalScored (nedslagssted, målscorer, målgiver, fart, måltid), CrossbarHit (sted, sist berørt, fart, kraft), StatfeedEvent (hendelse, type, hoved- og sekundærmål), MatchEnded (vinner, resultat), hvert annet hendelsesnavn som en rad
- fra UpdateState: arenaen, kameraets mål utenfor repriser (hvem `me` er), lagenes poengsum, hver spillers mål, målgivelser, redninger, skudd, demoleringer, berøringer, bilberøringer og poengsum (egen som statistikk, alles som `player_result` ved kampens slutt); overtid fra ClockUpdatedSeconds

**Lagres uendret**

- hver melding hel slik den kom fra strømmen (`text`), under sitt eget Event-navn: `UpdateState` (hver spillers PrimaryId og Shortcut, klokken, ballens fart og lag, lagnavn og farger, flagg for repriser og vinner, og bilstate der spillet sender den), `BallHit`, `GoalScored` (med ballens sist berørt), `CrossbarHit`, `StatfeedEvent`, `MatchCreated`, `MatchInitialized`, `CountdownBegin`, `RoundStarted`, `GoalReplayStart`, `GoalReplayWillEnd`, `GoalReplayEnd`, `MatchPaused`, `MatchUnpaused`, `MatchEnded`, `PodiumStart`, `ReplayCreated`, `MatchDestroyed`, `ClockUpdatedSeconds` og enhver hendelse et senere bygg legger til
- en UpdateState som er byte for byte lik den før (pauset, menyer) lagres én gang og telles (`unchanged_replies` i meta.json)
- meldinger mellom kampene: på sitt eget tidspunkt før neste kamps start; etter siste kamp, i en egen økt (`raw_only` i meta.json)
- `unreadable`: et objekt som ikke er en Stats API-melding; `junk`: tegn mellom objekter

**Ikke tilgjengelig**

- bilposisjoner og bilstate under spilling: spillet sender dem bare til tilskuere
- UpdateState mellom to sendinger: spillet sender PacketSendRate per sekund (`setup` setter 30, spillet tillater opptil 120); hendelsene sendes på tikket de skjer
- WebSocket-kopien på WebPort (49124): de samme meldingene som TCP-porten, ikke lest to ganger

**Størrelse**: en UpdateState er 1-3 KB for seks spillere, 30 i sekundet: omtrent 100-300 MB per time i `raw.bin` mens en kamp går, en tidel eller mindre i den zstd-komprimerte `heat.raw.parquet` (anslått fra det dokumenterte formatet, ikke målt på spillet)

## Verifisert {#verified}

testet på meldinger i det dokumenterte formatet sendt av en falsk lokal server; ikke testet mot spillet

## Kilde {#source}

[heat3d_watch/adapters/rocketleague.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/rocketleague.py)

<!-- Generated from the adapter by tools/gen_game_pages.py; change the adapter and run it again rather than editing this page. -->
