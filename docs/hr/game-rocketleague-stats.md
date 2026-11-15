---
title: "Rocket League (stanje igre)"
nav_order: 40
lang: "hr"
source: game-rocketleague-stats.md
source_hash: "3da6ea772068"
nav_exclude: true
search_exclude: true
---
# Rocket League (stanje igre) {#rocket-league-game-state}

Dok igrate Rocket League, watcher sprema ono što igra javlja programima na vašem računalu, pa to kasnije možete pogledati na karti u 3DHeat pregledniku.

*Tehnički podaci: adapter `rocketleague-stats`, vrsta [`gsi`](sources-and-rules.md); radi dok je `RocketLeague.exe` pokrenut i traži nove podatke svakih 0,05 s.*

## Što se bilježi {#what-is-recorded}

- udarci u loptu s mjestom lopte (XYZ, Unreal jedinice), tko je udario i brzine
- golovi s mjestom udarca, strijelac, asistent i brzina; udarci u prečku s mjestom
- feed statistike (ruševine, obrane, udarci, epske obrane, ...), početak igre, ponavljanja, početak i kraj meča, pobjednik
- vlastiti golovi, asistencije, obrane, udarci, ruševine, dodiri, rezultat i rezultati timova, iz UpdateState
- završni redak svakog igrača na kraju meča
- vaši vlastiti retci kao `me`: igrač naveden u postavkama (`config --set player_names.rocketleague-stats=<name>`), inače onaj kojeg kamera igre prati izvan repriza
- nema položaja automobila: API ih nema

## Odakle dolaze {#where-it-comes-from}

Stats API: TCP JSON tok s 127.0.0.1:49123 (Port u &lt;RL>\TAGame\Config\TAStatsAPI.ini ili DefaultStatsAPI.ini)

## Kako ga uključiti {#how-to-switch-it-on}

`python -m heat3d_watch setup rocketleague-stats --apply` (postavlja PacketSendRate=30), zatim pokrenite Rocket League

Naredbu upišite u terminal otvoren u mapi watchera (pogledajte [Prije nego što počnete](before-you-start.md)). Ako ne uspije, zadnji redak kaže zašto; [Instalacija i pokretanje](installing-and-running.md) pokriva uobičajene uzroke.

`python -m heat3d_watch setup rocketleague-stats` navodi datoteke koje bi promijenio; `python -m heat3d_watch setup rocketleague-stats --apply` ih mijenja, a izvornik čuva kao `<file>.heat3d-backup` (pogledajte [Naredbe](commands.md#setup)). Za svaku promjenu ispisuje `rocketleague-stats: changed: ...`, ili `rocketleague-stats: nothing to change` kad je već uključeno.

## Kako radi {#how-it-works}

Rocket League: službeni Stats API, lokalna utičnica u koju igra piše podatke o mečevima.

Uključuje se u `<RL>\TAGame\Config\TAStatsAPI.ini` - ili `DefaultStatsAPI.ini`
kad ona ne postoji, što igra čita samo tada - pod
`[TAGame.MatchStatsExporter_TA]`:

```text
PacketSendRate   UpdateState poruka u sekundi; 0 (zadano) isključuje API, najviše 120
Port             TCP port na kojem igra sluša, zadano 49123 (WebPort 49124 je WebSocket kopija)
```

Igra je server: klijent se spaja na 127.0.0.1:49123 i čita tok JSON objekata
`{"Event": name, "Data": {...}}` (neke verzije šalju Data kao JSON niz), jedan za
drugim bez separatora. Događaji se šalju u trenutku kad se dogode, neovisno o brzini:

```text
UpdateState   MatchGuid, Players[] (Name, PrimaryId, Shortcut, TeamNum 0 plavi / 1 narančasti,
              Score, Goals, Shots, Assists, Saves, Touches, CarTouches, Demos; stanje
              automobila samo za gledatelje), Game (Teams[], TimeSeconds, bOvertime, Ball {Speed,
              TeamNum}, bReplay, bHasWinner, Winner, Arena, bHasTarget, Target)
BallHit       Players[] (Name, Shortcut, TeamNum), Ball {PreHitSpeed, PostHitSpeed, Location {X,Y,Z}}
GoalScored    GoalSpeed, GoalTime, ImpactLocation {X,Y,Z}, Scorer, Assister, BallLastTouch
CrossbarHit   BallLocation {X,Y,Z}, BallSpeed, ImpactForce, BallLastTouch
StatfeedEvent EventName, Type, MainTarget, SecondaryTarget
MatchEnded    WinnerTeamNum
MatchCreated, MatchInitialized, CountdownBegin, RoundStarted, GoalReplayStart/WillEnd/End,
MatchPaused/Unpaused, PodiumStart, ReplayCreated, MatchDestroyed, ClockUpdatedSeconds
```

Položaji su u Unreal jedinicama (centimetri), Z gore; polje je oko 8200 x 10240
s golovima na Y = +-5120. Položaji automobila nisu dio API-ja: ima mjesto samo lopta
tamo gdje je udarena, zabijena ili pogodila prečku.

Svaka poruka čuva se i cijela (pravilo pretvarača 3DHeat, docs/converters.md u
repozitoriju preglednika): `heat.raw.parquet`, `type` je naziv Event-a poruke, `text`
je objekt onako kako je došao iz toka. UpdateState bajt po bajt jednak prethodnom
(pauzirani meč, izbornik) čuva se jednom i broji se u `unchanged_replies` u
meta.json-u. Poruke između mečeva čekaju u zaostatku za sljedeću sesiju meča; što
ostane kad se igra zatvori dobiva vlastitu sesiju. Znakovi između objekata koji nisu
JSON čuvaju se kao "junk".

Izvori: <https://www.rocketleague.com/en/developer/stats-api> (službena stranica);
nazivi polja i okvir TCP-a potvrđeni prema rlstatsapi klijentu
(<https://docs.rs/crate/rlstatsapi>, MIT; pročitan samo radi činjenica).

## Položaji i osi {#positions-and-axes}

| | |
|---|---|
| Položaji se bilježe | da |
| Os gore | `z` |
| Jedinice | Unreal jedinice (centimetri) |
| Zrcaljenje za preglednik | nema |
| Mjerilo jedinica (`scale`: preglednik množi položaje s njim) | 1 |

Ovo ulazi u `meta.json` (`axes`) svake sesije i, kad sesija ima položaje, u podnožje `heat.parquet`, pa preglednik 3DHeat sam okreće i skalira retke - pogledajte [Podaci](the-data.md).

## Više igrača {#multiplayer}

- Označeno kao igranje na mreži (`multiplayer`): **da**. `games --markdown` to prikazuje kao "dopušteno (čita samo ono što igra objavljuje)".
- Vrsta `gsi`: čita samo ono što igra ili platforma predaje (sučelje za integraciju stanja igre ili lokalni API koji igra poslužuje), pa bilježi i u igri na mreži i izvan nje; oznaka odlučuje samo smije li se ikad čitati memorija.
- Memorija: ovaj adapter je **nikad** ne čita. Samo adapteri vrste `memory` čitaju memoriju, i nikad za igru označenu kao igranu na mreži - pogledajte [Izvori i pravila](sources-and-rules.md).

## Zabilježena statistika {#statistics-recorded}

Ključevi statistike koje kod ovog adaptera postavlja po imenu (`stats` svake sesije u `meta.json` i tablica `stats` u `watcher.sqlite`):

`bad_packets`, `demolished`, `other_goals`, `overtime`, `result`, `team_goals`

Ključ u vitičastim zagradama dovršava se pri radu (`score.{team}` je jedan ključ po timu). Ključevi koje kod uzima iz tablice polja igre ili iz vlastitih naziva statistike igre nisu na ovom popisu; "Što se bilježi" gore ih navodi.

## Potpunost {#completeness}

Watcher slijedi [pravilo pretvarača](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md) iz 3DHeat-a: što izvor sadrži, to se čita ili čuva, nikad se ne odbacuje. Osim redaka, svaki paket, stranica, redak ili odgovor koji adapter primi čuva se cijel u `heat.raw.parquet` sesije (stupci `time`, `ms`, `type`, `used`, `payload`, `text`, pa svako polje sačuvano po imenu; `used` označava što je ujedno postalo retcima), a `selfCheck.completeness` u `meta.json` broji svaki `type` - `lost` je 0.

**Čita se**

- BallHit (mjesto, tko, tim, brzine prije i poslije), GoalScored (mjesto udarca, strijelac, asistent, brzina, vrijeme gola), CrossbarHit (mjesto, zadnji dodir, brzina, sila), StatfeedEvent (događaj, vrsta, glavna i sporedna meta), MatchEnded (pobjednik, rezultat), naziv svakog drugog događaja kao redak
- iz UpdateState: arena, meta kamere izvan repriza (tko je `me`), rezultati timova, golovi, asistencije, obrane, udarci, ruševine, dodiri, dodiri automobila i rezultat svakog igrača (vlastiti kao statistika, svih kao `player_result` na kraju meča); prekovremeno iz ClockUpdatedSeconds

**Čuva se sirovo**

- svaka poruka cijela kako je došla iz toka (`text`), pod svojim Event nazivom: `UpdateState` (PrimaryId i Shortcut svakog igrača, sat, brzina i tim lopte, nazivi i boje timova, zastavice repriza i pobjednika, te stanje automobila gdje ga igra šalje), `BallHit`, `GoalScored` (sa zadnjim dodirom lopte), `CrossbarHit`, `StatfeedEvent`, `MatchCreated`, `MatchInitialized`, `CountdownBegin`, `RoundStarted`, `GoalReplayStart`, `GoalReplayWillEnd`, `GoalReplayEnd`, `MatchPaused`, `MatchUnpaused`, `MatchEnded`, `PodiumStart`, `ReplayCreated`, `MatchDestroyed`, `ClockUpdatedSeconds` i svaki događaj koji kasnija verzija doda
- UpdateState bajt po bajt jednak prethodnom (pauza, izbornici) čuva se jednom i broji se (`unchanged_replies` u meta.json)
- poruke između mečeva: u svoje vrijeme prije početka sljedećeg meča; nakon zadnjeg meča, u vlastitoj sesiji (`raw_only` u meta.json)
- `unreadable`: objekt koji nije poruka Stats API-ja; `junk`: znakovi između objekata

**Nije dostupno**

- položaji automobila i stanje automobila tijekom igre: igra ih šalje samo gledateljima
- UpdateState između dva slanja: igra šalje PacketSendRate u sekundi (`setup` postavlja 30, igra dopušta do 120); događaji se šalju u trenutku kad se dogode
- WebSocket kopija na WebPort (49124): iste poruke kao na TCP portu, ne čitaju se dvaput

**Veličina**: UpdateState je 1-3 KB za šest igrača, 30 u sekundi: oko 100-300 MB po satu u `raw.bin` dok meč traje, a desetina ili manje u zstd `heat.raw.parquet` (procijenjeno prema dokumentiranom formatu, nije izmjereno na igri)

## Provjereno {#verified}

testirano na porukama u dokumentiranom formatu koje šalje lažni lokalni server; nije testirano na samoj igri

## Izvor {#source}

[heat3d_watch/adapters/rocketleague.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/rocketleague.py)

<!-- Generirano iz adaptera pomoću tools/gen_game_pages.py; promijenite adapter i ponovno ga pokrenite umjesto uređivanja ove stranice. -->
