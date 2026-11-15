---
title: "Rocket League (gjendja e lojës)"
nav_order: 39
lang: "sq"
source: game-rocketleague-stats.md
source_hash: "fd70d0540bb9"
nav_exclude: true
search_exclude: true
---
# Rocket League (gjendja e lojës) {#rocket-league-game-state}

Ndërsa luan Rocket League, watcher ruan çfarë i raporton loja programeve në kompjuterin tënd, që t'i shohësh më vonë në një hartë në shikuesin 3DHeat.

*Detaje teknike: adaptori `rocketleague-stats`, lloji [`gsi`](sources-and-rules.md); punon sa kohë `RocketLeague.exe` është duke u ekzekutuar dhe kërkon të dhëna të reja çdo 0.05 s.*

## Çfarë regjistrohet {#what-is-recorded}

- goditjet e topit me vendin e topit (XYZ, njësi Unreal), kush e goditi dhe shpejtësitë
- golat me vendin e goditjes, shënuesin, asistuesin dhe shpejtësinë; goditjet e traversës me vendin
- stat feed (shkatërrime, shpëtime, goditje, shpëtime epike, ...), kickoff-et, riluajtjet, fillimi dhe fundi i ndeshjes, fituesi
- golat e tu, asistimet, shpëtimet, goditjet, demo-t, prekjet, rezultati dhe rezultatet e ekipeve, nga UpdateState
- rreshti i fundit i çdo lojtari në fund të ndeshjes
- rreshtat e tu si `me`: lojtari i emërtuar te cilësimet (`config --set player_names.rocketleague-stats=<name>`), përndryshe ai që e ndjek kamera e lojës jashtë riluajtjeve
- pa pozicione makinash: API nuk ka

## Nga vjen {#where-it-comes-from}

Stats API: rrjedhë JSON TCP nga 127.0.0.1:49123 (Port te &lt;RL>\TAGame\Config\TAStatsAPI.ini ose DefaultStatsAPI.ini)

## Si ta ndezësh {#how-to-switch-it-on}

`python -m heat3d_watch setup rocketleague-stats --apply` (vendos PacketSendRate=30), pastaj nise Rocket League

Shkruaje komandën në një terminal të hapur në dosjen e watcher-it (shih [Para se të fillosh](before-you-start.md)). Nëse dështon, rreshti i fundit tregon pse; [Instalimi dhe nisja](installing-and-running.md) përmban shkaqet më të zakonshme.

`python -m heat3d_watch setup rocketleague-stats` liston skedarët që do t'i ndryshonte; `python -m heat3d_watch setup rocketleague-stats --apply` i ndryshon, duke e ruajtur origjinalin si `<file>.heat3d-backup` (shih [Komandat](commands.md#setup)). Printon `rocketleague-stats: changed: ...` për çdo ndryshim, ose `rocketleague-stats: nothing to change` kur është tashmë i ndezur.

## Si funksionon {#how-it-works}

Rocket League: Stats API zyrtar, një soket lokal ku loja shkruan të dhënat e ndeshjes.

Ndizet te `<RL>\TAGame\Config\TAStatsAPI.ini` - ose `DefaultStatsAPI.ini`
kur ai nuk ekziston, që loja e lexon vetëm atëherë - nën
`[TAGame.MatchStatsExporter_TA]`:

```text
PacketSendRate   UpdateState messages per second; 0 (the default) switches the API off, at most 120
Port             the TCP port the game listens on, default 49123 (WebPort 49124 is a WebSocket copy)
```

Loja është serveri: një klient lidhet me 127.0.0.1:49123 dhe lexon një rrjedhë
objektesh JSON `{"Event": name, "Data": {...}}` (disa versione e dërgojnë Data si
varg JSON), njëri pas tjetrit pa ndarës. Ngjarjet dërgohen në tick-un kur ndodhin,
pavarësisht nga ritmi:

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

Vendet janë njësi Unreal (centimetra), Z lart; fusha është rreth 8200 x 10240
me portat te Y = +-5120. Pozicionet e makinave nuk janë pjesë e API: çfarë ka
vend është topi aty ku u godit, u shënua ose goditi traversën.

Çdo mesazh ruhet edhe i plotë (rregulli i konvertuesit të 3DHeat, docs/converters.md
në depon e shikuesit): `heat.raw.parquet`, `type` emri Event i mesazhit,
`text` objekti siç erdhi nga rrjedha. Një UpdateState bajt për bajt si ai
para tij (një ndeshje e pauzuar, një meny) ruhet një herë dhe numërohet te `unchanged_replies`
i meta.json. Mesazhet mes ndeshjeve presin në një backlog për sesionin e ndeshjes
tjetër; çfarë mbetet kur mbyllet loja merr një sesion më vete.
Karakteret mes objekteve që nuk janë JSON ruhen si "junk".

Burimet: <https://www.rocketleague.com/en/developer/stats-api> (faqja zyrtare);
shkronjat e mëdha/të vogla të fushave dhe kornizimi TCP u konfirmuan me klientin rlstatsapi
(<https://docs.rs/crate/rlstatsapi>, MIT; lexuar vetëm për fakte).

## Pozicionet dhe boshtet {#positions-and-axes}

| | |
|---|---|
| Pozicionet e regjistruara | po |
| Boshti lart | `z` |
| Njësitë | njësi Unreal (centimetra) |
| Pasqyruar për shikuesin | asnjë |
| Shkalla e njësisë (`scale`: shikuesi i shumëzon pozicionet me të) | 1 |

Këto hyjnë te `meta.json` i çdo sesioni (`axes`) dhe, kur sesioni ka pozicione, te fundi (footer) i `heat.parquet`, kështu që shikuesi 3DHeat i rrotullon dhe i shkallëzon rreshtat vetë - shih [Të dhënat](the-data.md).

## Lojë me shumë lojtarë {#multiplayer}

- Shënuar si lojë që luhet online (`multiplayer`): **po**. `games --markdown` e shfaq këtë si "allowed (reads only what the game publishes)".
- Lloji `gsi`: lexon vetëm atë që loja ose platforma e jep vetë (një integrim i gjendjes së lojës ose një API lokale që loja e ofron), kështu që regjistron si në lojën online ashtu edhe offline; shenja vendos vetëm nëse memoria lejohet ndonjëherë të lexohet.
- Memoria: **asnjëherë** nuk lexohet nga ky adaptor. Vetëm adaptorët `memory` lexojnë memorie, dhe kurrë për një lojë të shënuar si e luajtur online - shih [Burimet dhe rregullat](sources-and-rules.md).

## Statistikat e regjistruara {#statistics-recorded}

Çelësat e statistikave që kodi i këtij adaptori i vendos me emër (`stats` i çdo sesioni te `meta.json` dhe tabela `stats` e `watcher.sqlite`):

`bad_packets`, `demolished`, `other_goals`, `overtime`, `result`, `team_goals`

Një çelës në kllapa gjarpërore plotësohet gjatë punës (`score.{team}` është një çelës për çdo ekip). Çelësat që kodi i merr nga një tabelë me fushat e lojës ose nga emrat e statistikave të vetë lojës nuk janë në këtë listë; "Çfarë regjistrohet" më sipër i emërton.

## Plotësia {#completeness}

Watcher ndjek [rregullin e konvertuesit](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md) të 3DHeat: çfarë mban burimi lexohet ose ruhet, kurrë nuk hidhet. Përveç rreshtave, çdo paketë, faqe, rresht ose përgjigje që e merr adaptori ruhet e plotë te `heat.raw.parquet` i sesionit (kolonat `time`, `ms`, `type`, `used`, `payload`, `text`, pastaj çdo fushë e ruajtur me emër; `used` shënon çfarë u bë edhe rreshta), dhe `selfCheck.completeness` i `meta.json` numëron çdo `type` - `lost` është 0.

**Lexuar**

- BallHit (vendi, kush, ekipi, shpejtësitë para dhe pas), GoalScored (vendi i goditjes, shënuesi, asistuesi, shpejtësia, ora e golit), CrossbarHit (vendi, prekja e fundit, shpejtësia, forca), StatfeedEvent (ngjarja, lloji, objektivi kryesor dhe dytësor), MatchEnded (fituesi, rezultati), emri i çdo ngjarjeje tjetër si rresht
- nga UpdateState: arena, objektivi i kamerës jashtë riluajtjeve (kush është `me`), rezultatet e ekipeve, golat, asistimet, shpëtimet, goditjet, demo-t, prekjet, prekjet e makinës dhe rezultati i çdo lojtari (të tuat si statistika, të të gjithëve si `player_result` në fund të ndeshjes); overtime nga ClockUpdatedSeconds

**Ruajtur të papërpunuara**

- çdo mesazh i plotë siç erdhi nga rrjedha (`text`), nën emrin e vet Event: `UpdateState` (PrimaryId dhe Shortcut i çdo lojtari, ora, shpejtësia dhe ekipi i topit, emrat dhe ngjyrat e ekipeve, flamujt e riluajtjes dhe të fituesit, dhe gjendja e makinës ku e dërgon loja), `BallHit`, `GoalScored` (me prekjen e fundit të topit), `CrossbarHit`, `StatfeedEvent`, `MatchCreated`, `MatchInitialized`, `CountdownBegin`, `RoundStarted`, `GoalReplayStart`, `GoalReplayWillEnd`, `GoalReplayEnd`, `MatchPaused`, `MatchUnpaused`, `MatchEnded`, `PodiumStart`, `ReplayCreated`, `MatchDestroyed`, `ClockUpdatedSeconds` dhe çdo ngjarje që shton një version i mëvonshëm
- një UpdateState bajt për bajt si ai para tij (pauzë, menyra) ruhet një herë dhe numërohet (`unchanged_replies` te meta.json)
- mesazhet mes ndeshjeve: në kohën e tyre para nisjes së ndeshjes tjetër; pas ndeshjes së fundit, në një sesion më vete (`raw_only` te meta.json)
- `unreadable`: një objekt që nuk është mesazh i Stats API; `junk`: karaktere mes objekteve

**Nuk ofrohet**

- pozicionet e makinave dhe gjendja e makinës gjatë lojës: loja i dërgon vetëm te shikuesit (spectators)
- UpdateState mes dy dërgimeve: loja dërgon PacketSendRate në sekondë (`setup` vendos 30, loja lejon deri në 120); ngjarjet dërgohen në tick-un kur ndodhin
- kopja WebSocket te WebPort (49124): të njëjtat mesazhe si porta TCP, nuk lexohet dy herë

**Madhësia**: një UpdateState është 1-3 KB për gjashtë lojtarë, 30 në sekondë: rreth 100-300 MB në orë te `raw.bin` sa kohë zhvillohet një ndeshje, një e dhjeta ose më pak te `heat.raw.parquet` me zstd (vlerësuar nga formati i dokumentuar, jo i matur me lojën)

## Verifikuar {#verified}

u provua me mesazhe në formatin e dokumentuar të dërguara nga një server lokal i rremë; i paprovuar me lojën

## Burimi {#source}

[heat3d_watch/adapters/rocketleague.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/rocketleague.py)

<!-- Generated from the adapter by tools/gen_game_pages.py; change the adapter and run it again rather than editing this page. -->
