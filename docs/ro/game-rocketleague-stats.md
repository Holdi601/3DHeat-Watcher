---
title: "Rocket League (starea jocului)"
nav_order: 40
lang: "ro"
source: game-rocketleague-stats.md
source_hash: "3da6ea772068"
nav_exclude: true
search_exclude: true
---
# Rocket League (starea jocului) {#rocket-league-game-state}

Cât timp jucați Rocket League, watcher-ul salvează ce raportează jocul către programele de pe propriul calculator, ca să le puteți vedea mai târziu pe o hartă în vizualizatorul 3DHeat.

*Detalii tehnice: adaptorul `rocketleague-stats`, tipul [`gsi`](sources-and-rules.md); rulează cât timp `RocketLeague.exe` este pornit și caută date noi la fiecare 0,05 s.*

## Ce se înregistrează {#what-is-recorded}

- lovirile mingii cu locul mingii (XYZ, unități Unreal), cine a lovit-o și vitezele
- golurile cu locul impactului, marcatorul, pasatorul și viteza; loviturile de bară transversală cu locul
- feed-ul de statistici (demolări, parade, șuturi, parade epice, ...), lovituri de începere, reluări, începutul și sfârșitul meciului, câștigătorul
- autogoluri, pase decisive, parade, șuturi, demolări, atingeri, scorul și scorurile echipelor, din UpdateState
- linia finală a fiecărui jucător la sfârșitul meciului
- rândurile tale ca `me`: jucătorul numit în setări (`config --set player_names.rocketleague-stats=<nume>`), altfel cel pe care îl urmărește camera jocului în afara reluărilor
- fără poziții ale mașinilor: API-ul nu le are

## De unde vine {#where-it-comes-from}

API-ul de statistici: stream JSON TCP de la 127.0.0.1:49123 (portul din &lt;RL>\TAGame\Config\TAStatsAPI.ini sau DefaultStatsAPI.ini)

## Cum se activează {#how-to-switch-it-on}

`python -m heat3d_watch setup rocketleague-stats --apply` (setează PacketSendRate=30), apoi porniți Rocket League

Scrieți comanda într-un terminal deschis în folderul watcher-ului (vedeți [Înainte de a începe](before-you-start.md)). Dacă eșuează, ultima linie spune de ce; [Instalarea și rularea](installing-and-running.md) acoperă cauzele obișnuite.

`python -m heat3d_watch setup rocketleague-stats` arată ce fișiere ar schimba; `python -m heat3d_watch setup rocketleague-stats --apply` le schimbă, păstrând originalul ca `<file>.heat3d-backup` (vedeți [Comenzile](commands.md#setup)). Afișează `rocketleague-stats: changed: ...` pentru fiecare schimbare sau `rocketleague-stats: nothing to change` când este deja activat.

## Cum funcționează {#how-it-works}

Rocket League: API-ul oficial de statistici, un socket local în care jocul scrie datele meciului.

Se activează în `<RL>\TAGame\Config\TAStatsAPI.ini` - sau `DefaultStatsAPI.ini` când acela nu există, pe care jocul îl citește doar atunci - sub `[TAGame.MatchStatsExporter_TA]`:

```text
PacketSendRate   mesaje UpdateState pe secundă; 0 (implicit) oprește API-ul, cel mult 120
Port             portul TCP pe care ascultă jocul, implicit 49123 (WebPort 49124 este o copie WebSocket)
```

Jocul este serverul: un client se conectează la 127.0.0.1:49123 și citește un stream de obiecte JSON `{"Event": nume, "Data": {...}}` (unele versiuni trimit Data ca șir JSON), unul după altul, fără separatoare. Evenimentele sunt trimise în tickul în care se întâmplă, indiferent de rată:

```text
UpdateState   MatchGuid, Players[] (Name, PrimaryId, Shortcut, TeamNum 0 albastru / 1 portocaliu,
              Score, Goals, Shots, Assists, Saves, Touches, CarTouches, Demos; starea mașinii
              doar pentru spectatori), Game (Teams[], TimeSeconds, bOvertime, Ball {Speed,
              TeamNum}, bReplay, bHasWinner, Winner, Arena, bHasTarget, Target)
BallHit       Players[] (Name, Shortcut, TeamNum), Ball {PreHitSpeed, PostHitSpeed, Location {X,Y,Z}}
GoalScored    GoalSpeed, GoalTime, ImpactLocation {X,Y,Z}, Scorer, Assister, BallLastTouch
CrossbarHit   BallLocation {X,Y,Z}, BallSpeed, ImpactForce, BallLastTouch
StatfeedEvent EventName, Type, MainTarget, SecondaryTarget
MatchEnded    WinnerTeamNum
MatchCreated, MatchInitialized, CountdownBegin, RoundStarted, GoalReplayStart/WillEnd/End,
MatchPaused/Unpaused, PodiumStart, ReplayCreated, MatchDestroyed, ClockUpdatedSeconds
```

Locațiile sunt în unități Unreal (centimetri), Z în sus; terenul are cam 8200 x 10240, cu porțile la Y = ±5120. Pozițiile mașinilor nu fac parte din API: ce are un loc este mingea acolo unde a fost lovită, marcată sau a lovit bara transversală.

Fiecare mesaj este păstrat și întreg (regula convertorului 3DHeat, docs/converters.md din repository-ul vizualizatorului): `heat.raw.parquet`, `type` numele evenimentului din mesaj, `text` obiectul așa cum a venit din stream. Un UpdateState identic octet cu octet cu cel dinainte (un meci pus pe pauză, un meniu) se păstrează o dată și se numără în `unchanged_replies` din meta.json. Mesajele dintre meciuri așteaptă într-o restanță pentru sesiunea următorului meci; ce rămâne când se închide jocul primește o sesiune proprie.

Caracterele dintre obiecte care nu sunt JSON se păstrează ca „junk".

Surse: <https://www.rocketleague.com/en/developer/stats-api> (pagina oficială); casing-ul câmpurilor și cadrarea TCP confirmate după clientul rlstatsapi (<https://docs.rs/crate/rlstatsapi>, MIT; citit doar pentru fapte).

## Poziții și axe {#positions-and-axes}

| | |
|---|---|
| Poziții înregistrate | da |
| Axa verticală | `z` |
| Unități | unități Unreal (centimetri) |
| Oglindit pentru vizualizator | niciunul |
| Scara unității (`scale`: vizualizatorul înmulțește pozițiile cu ea) | 1 |

Acestea intră în `meta.json` al fiecărei sesiuni (`axes`) și, când sesiunea are poziții, în subsolul `heat.parquet`, ca vizualizatorul 3DHeat să rotească și să scaleze rândurile singur; vedeți [Datele](the-data.md).

## Multiplayer {#multiplayer}

- Marcat ca jucat online (`multiplayer`): **da**. `games --markdown` arată asta ca „permis (citește doar ce publică jocul)".
- Tipul `gsi`: citește doar ce oferă jocul sau platforma (o integrare de stare a jocului sau un API local pe care îl servește jocul), deci înregistrează și în jocul online, nu doar offline; marcajul decide doar dacă memoria poate fi citită vreodată.
- Memoria: **niciodată** citită de acest adaptor. Doar adaptoarele de tip `memory` citesc memoria, și niciodată pentru un joc marcat ca jucat online; vedeți [Surse și reguli](sources-and-rules.md).

## Statistici înregistrate {#statistics-recorded}

Cheile de statistici pe care codul adaptorului le setează pe nume (fiecare `stats` din sesiune, în `meta.json`, și tabelul `stats` din `watcher.sqlite`):

`bad_packets`, `demolished`, `other_goals`, `overtime`, `result`, `team_goals`

O cheie între acolade se completează la rulare (`score.{team}` este câte o cheie pentru fiecare echipă). Cheile pe care codul le ia dintr-un tabel de câmpuri ale jocului sau din numele statisticilor proprii ale jocului nu sunt în listă; „Ce se înregistrează" de mai sus le numește.

## Completitudine {#completeness}

Watcher-ul urmează regula de convertor a 3DHeat: ce conține sursa este citit sau păstrat, niciodată eliminat. Pe lângă rânduri, fiecare pachet, pagină, linie sau răspuns pe care îl primește adaptorul este păstrat întreg în `heat.raw.parquet` al sesiunii (coloanele `time`, `ms`, `type`, `used`, `payload`, `text`, apoi orice câmp păstrat pe nume; `used` marchează ce a devenit și rând), iar `selfCheck.completeness` din `meta.json` numără fiecare `type`; `lost` este 0.

**Citit**

- BallHit (locul, cine, echipa, vitezele înainte și după), GoalScored (locul impactului, marcatorul, pasatorul, viteza, timpul golului), CrossbarHit (locul, ultima atingere, viteza, forța), StatfeedEvent (eveniment, tip, ținta principală și cea secundară), MatchEnded (câștigătorul, rezultatul), numele fiecărui alt eveniment ca rând
- din UpdateState: arena, ținta camerei în afara reluărilor (cine este `me`), scorurile echipelor, golurile, pasele decisive, parările, șuturile, demolările, atingerile, atingerile de mașină și scorul fiecărui jucător (al tău ca statistici, al tuturor ca `player_result` la sfârșitul meciului); prelungirea din ClockUpdatedSeconds

**Păstrat brut**

- fiecare mesaj întreg, așa cum a venit din stream (`text`), sub numele lui de Event: `UpdateState` (PrimaryId și Shortcut ale fiecărui jucător, ceasul, viteza și echipa mingii, numele și culorile echipelor, indicatorii de reluare și de câștigător, și starea mașinii acolo unde jocul o trimite), `BallHit`, `GoalScored` (cu ultima atingere a mingii), `CrossbarHit`, `StatfeedEvent`, `MatchCreated`, `MatchInitialized`, `CountdownBegin`, `RoundStarted`, `GoalReplayStart`, `GoalReplayWillEnd`, `GoalReplayEnd`, `MatchPaused`, `MatchUnpaused`, `MatchEnded`, `PodiumStart`, `ReplayCreated`, `MatchDestroyed`, `ClockUpdatedSeconds` și orice eveniment pe care îl adaugă o versiune ulterioară
- un UpdateState identic octet cu cel dinainte (pe pauză, în meniuri) se păstrează o dată și se numără (`unchanged_replies` în meta.json)
- mesajele dintre meciuri: la momentul lor, înainte de începutul meciului următor; după ultimul meci, într-o sesiune proprie (`raw_only` în meta.json)
- `unreadable`: un obiect care nu este mesaj al API-ului de statistici; `junk`: caracterele dintre obiecte

**Nu este disponibil**

- pozițiile mașinilor și starea mașinii în timpul jocului: jocul le trimite doar spectatorilor
- UpdateState între două trimiteri: jocul trimite PacketSendRate pe secundă (`setup` setează 30, jocul permite până la 120); evenimentele sunt trimise în tickul în care se întâmplă
- copia WebSocket de pe WebPort (49124): aceleași mesaje ca pe portul TCP, nu se citesc de două ori

**Dimensiune**: un UpdateState are 1-3 KB pentru șase jucători, de 30 de ori pe secundă: aproximativ 100-300 MB pe oră în `raw.bin` cât timp rulează un meci, o zecime sau mai puțin în `heat.raw.parquet` zstd (estimat după formatul documentat, nemăsurat pe joc)

## Verificat {#verified}

testat pe mesaje în formatul documentat, trimise de un server local fals; netestat cu jocul

## Sursă {#source}

[heat3d_watch/adapters/rocketleague.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/rocketleague.py)

<!-- Generated from the adapter by tools/gen_game_pages.py; change the adapter and run it again rather than editing this page. -->
