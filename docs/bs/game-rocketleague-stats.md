---
title: "Rocket League (stanje igre)"
nav_order: 40
lang: "bs"
source: game-rocketleague-stats.md
source_hash: "3da6ea772068"
nav_exclude: true
search_exclude: true
---
# Rocket League (stanje igre) {#rocket-league-game-state}

Dok igrate Rocket League, watcher sprema ono što igra javlja programima na vašem vlastitom računaru, da to kasnije možete pogledati na mapi u preglednik 3DHeat-u.

*Tehnički detalji: adapter `rocketleague-stats`, vrsta [`gsi`](sources-and-rules.md); radi dok je pokrenut `RocketLeague.exe` i svakih 0,05 s traži nove podatke.*

## Šta se bilježi {#what-is-recorded}

- udarci u loptu s mjestom lopte (XYZ, Unreal jedinice), ko ju je udario i brzine
- golovi s mjestom udara, strijelcem, asistentom i brzinom; udarci u prečku s mjestom
- stat feed (demolitions, saves, shots, epic saves, ...), kickoffs, replays, početak i kraj meča, pobjednik
- vlastiti golovi, asistencije, odbrane, šutevi, demos, dodiri, rezultat i rezultati timova, iz UpdateState
- završna linija svakog igrača na kraju meča
- vaši vlastiti redovi kao `me`: igrač imenovan u postavkama (`config --set player_names.rocketleague-stats=<name>`), inače onaj kojeg kamera igre prati izvan replay-a
- bez položaja auta: API ih nema

## Odakle dolazi {#where-it-comes-from}

Stats API: TCP JSON tok sa 127.0.0.1:49123 (Port u &lt;RL>\TAGame\Config\TAStatsAPI.ini ili DefaultStatsAPI.ini)

## Kako ga uključiti {#how-to-switch-it-on}

`python -m heat3d_watch setup rocketleague-stats --apply` (postavlja PacketSendRate=30), zatim pokrenite Rocket League

Upišite komandu u terminal otvoren u folderu watcher-a (vidite [Prije nego počnete](before-you-start.md)). Ako ne uspije, zadnji red kaže zašto; [Instalacija i pokretanje](installing-and-running.md) pokriva uobičajene uzroke.

`python -m heat3d_watch setup rocketleague-stats` navodi datoteke koje bi promijenio; `python -m heat3d_watch setup rocketleague-stats --apply` ih mijenja, a original čuva kao `<file>.heat3d-backup` (vidite [Komande](commands.md#setup)). Ispisuje `rocketleague-stats: changed: ...` za svaku promjenu, ili `rocketleague-stats: nothing to change` kad je već uključeno.

## Kako radi {#how-it-works}

Rocket League: službeni Stats API, lokalni socket u koji igra piše podatke o meču.

Uključuje se u `<RL>\TAGame\Config\TAStatsAPI.ini` - ili u `DefaultStatsAPI.ini`
kad ta ne postoji, koju igra čita samo tada - pod
`[TAGame.MatchStatsExporter_TA]`:

```text
PacketSendRate   UpdateState messages per second; 0 (the default) switches the API off, at most 120
Port             the TCP port the game listens on, default 49123 (WebPort 49124 is a WebSocket copy)
```

Igra je server: klijent se spaja na 127.0.0.1:49123 i čita tok
JSON objekata `{"Event": name, "Data": {...}}` (neke verzije šalju Data kao
JSON niz), jedan za drugim bez separatora. Događaji se šalju u
tick u kojem se dese, neovisno o brzini slanja:

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

Lokacije su Unreal jedinice (centimetri), Z gore; teren je otprilike 8200 x 10240
s golovima na Y = +-5120. Položaji auta nisu dio API-ja: mjesto imaju
lopta tamo gdje je udarena, gdje je zabijen gol ili gdje je pogodila prečku.

Svaka poruka se također čuva cijela (3DHeat-ovo pravilo konvertera, docs/converters.md
u repozitoriju preglednika): `heat.raw.parquet`, `type` je naziv Event
poruke, `text` je objekt onako kako je stigao iz toka. UpdateState bajt po bajt
isti kao prethodni (pauzirani meč, meni) čuva se jednom i broji u `unchanged_replies` u meta.json.
Poruke između mečeva čekaju u backlogu za sesiju sljedećeg
meča; ono što ostane kad se igra zatvori dobija vlastitu sesiju.
Znakovi između objekata koji nisu JSON čuvaju se kao "junk".

Izvori: <https://www.rocketleague.com/en/developer/stats-api> (službena stranica);
pisanje polja (velika/mala slova) i TCP uokvirivanje potvrđeni prema klijentu rlstatsapi
(<https://docs.rs/crate/rlstatsapi>, MIT; čitano samo zbog činjenica).

## Položaji i ose {#positions-and-axes}

| | |
|---|---|
| Položaji se bilježe | da |
| Osa gore | `z` |
| Jedinice | Unreal jedinice (centimetri) |
| Zrcaljeno za preglednik | nijedna |
| Skala jedinica (`scale`: preglednik njome množi položaje) | 1 |

Ovo ide u `meta.json` svake sesije (`axes`) i, kad sesija ima položaje, u podnožje datoteke `heat.parquet`, pa preglednik 3DHeat sam okreće i skalira redove - vidite [Podaci](the-data.md).

## Multiplayer {#multiplayer}

- Označena kao igrana online (`multiplayer`): **da**. `games --markdown` to prikazuje kao "allowed (reads only what the game publishes)".
- Vrsta `gsi`: čita samo ono što igra ili platforma daje (integraciju stanja igre ili lokalni API koji igra služi), pa snima i u online igri kao i offline; oznaka odlučuje samo smije li se memorija ikad čitati.
- Memorija: ovaj je adapter **nikad** ne čita. Memoriju čitaju samo `memory` adapteri, i nikad za igru označenu kao igranu online - vidite [Izvori i pravila](sources-and-rules.md).

## Zabilježena statistika {#statistics-recorded}

Ključevi statistike koje kod ovog adaptera postavlja po imenu (`stats` svake sesije u `meta.json` i tabela `stats` u `watcher.sqlite`):

`bad_packets`, `demolished`, `other_goals`, `overtime`, `result`, `team_goals`

Ključ u vitičastim zagradama dovršava se pri izvođenju (`score.{team}` je jedan ključ po timu). Ključevi koje kod uzima iz tabele polja igre ili iz vlastitih naziva statistike igre nisu na ovom popisu; "Šta se bilježi" iznad ih navodi.

## Potpunost {#completeness}

Watcher slijedi 3DHeat-ovo [pravilo konvertera](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md): ono što izvor sadrži se čita ili čuva, nikad ne odbacuje. Osim redova, svaki paket, stranica, linija ili odgovor koji adapter primi čuva se cijel u `heat.raw.parquet` sesije (kolone `time`, `ms`, `type`, `used`, `payload`, `text`, pa svako polje čuvano po imenu; `used` označava šta je također postalo redovi), a `selfCheck.completeness` u `meta.json` broji svaki `type` - `lost` je 0.

**Čita se**

- BallHit (mjesto, ko, tim, brzine prije i poslije), GoalScored (mjesto udara, strijelac, asistent, brzina, vrijeme gola), CrossbarHit (mjesto, zadnji dodir, brzina, sila), StatfeedEvent (događaj, vrsta, glavna i sekundarna meta), MatchEnded (pobjednik, rezultat), naziv svakog drugog događaja kao red
- iz UpdateState: arena, meta kamere izvan replay-a (ko je `me`), rezultati timova, golovi, asistencije, odbrane, šutevi, demos, dodiri, dodiri auta i rezultat svakog igrača (vlastiti kao statistika, svačiji kao `player_result` na kraju meča); produžetak iz ClockUpdatedSeconds

**Čuva se sirovo**

- svaka poruka cijela onako kako je stigla iz toka (`text`), pod svojim nazivom Event: `UpdateState` (PrimaryId i Shortcut svakog igrača, sat, brzina i tim lopte, nazivi i boje timova, oznake replay-a i pobjednika, te stanje auta gdje ga igra šalje), `BallHit`, `GoalScored` (sa zadnjim dodirom lopte), `CrossbarHit`, `StatfeedEvent`, `MatchCreated`, `MatchInitialized`, `CountdownBegin`, `RoundStarted`, `GoalReplayStart`, `GoalReplayWillEnd`, `GoalReplayEnd`, `MatchPaused`, `MatchUnpaused`, `MatchEnded`, `PodiumStart`, `ReplayCreated`, `MatchDestroyed`, `ClockUpdatedSeconds` i svaki događaj koji doda neka kasnija verzija
- UpdateState bajt po bajt isti kao prethodni (pauza, meniji) čuva se jednom i broji (`unchanged_replies` u meta.json)
- poruke između mečeva: u svoje vrijeme prije početka sljedećeg meča; poslije zadnjeg meča, u vlastitoj sesiji (`raw_only` u meta.json)
- `unreadable`: objekt koji nije poruka Stats API-ja; `junk`: znakovi između objekata

**Nije dostupno**

- položaji i stanje auta tokom igranja: igra ih šalje samo gledaocima
- UpdateState između dva slanja: igra šalje PacketSendRate puta u sekundi (`setup` postavlja 30, igra dopušta do 120); događaji se šalju u tick u kojem se dese
- WebSocket kopija na WebPort (49124): iste poruke kao na TCP portu, ne čita se dvaput

**Veličina**: UpdateState je 1-3 KB za šest igrača, 30 u sekundi: oko 100-300 MB na sat u `raw.bin` dok traje meč, desetina ili manje u zstd `heat.raw.parquet` (procijenjeno iz dokumentiranog formata, nije izmjereno na igri)

## Provjereno {#verified}

testirano na porukama u dokumentiranom formatu koje šalje lažni lokalni server; nije testirano na igri

## Izvor {#source}

[heat3d_watch/adapters/rocketleague.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/rocketleague.py)

<!-- Generated from the adapter by tools/gen_game_pages.py; change the adapter and run it again rather than editing this page. -->
