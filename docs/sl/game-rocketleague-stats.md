---
title: "Rocket League (stanje igre)"
nav_order: 40
lang: "sl"
source: game-rocketleague-stats.md
source_hash: "3da6ea772068"
nav_exclude: true
search_exclude: true
---
# Rocket League (stanje igre) {#rocket-league-game-state}

Medtem ko igrate Rocket League, watcher shrani, kar igra poroča programom na vašem računalniku, da jih lahko kasneje pogledate na zemljevidu v pregledovalniku 3DHeat.

*Tehnične podrobnosti: adapter `rocketleague-stats`, vrsta [`gsi`](sources-and-rules.md); teče, ko je `RocketLeague.exe` zagnan, in išče nove podatke vsakih 0,05 s.*

## Kaj se zapiše {#what-is-recorded}

- zadetki žoge s mestom žoge (XYZ, enote Unreal), kdo jo je zadel, in hitrosti
- goli z mestom udarca, strelcem, podajalcem in hitrostjo; zadetki prečke z mestom
- statistični tok (rušenja, obrambe, streli, epske obrambe ...), začetki, ponovitve, začetek in konec tekme, zmagovalec
- lastni avtogoli, asistence, obrambe, streli, rušenja, dotiki, rezultat in rezultati ekip iz UpdateState
- končna vrstica vsakega igralca ob koncu tekme
- vaše vrstice kot `me`: igralec, imenovan v nastavitvah (`config --set player_names.rocketleague-stats=<ime>`), sicer tisti, ki mu sledi igrina kamera zunaj ponovitev
- ni položajev avtomobilov: API jih nima

## Od kod prihaja {#where-it-comes-from}

Stats API: TCP JSON tok z 127.0.0.1:49123 (vrata v &lt;RL&gt;\TAGame\Config\TAStatsAPI.ini ali DefaultStatsAPI.ini)

## Kako vklopiti {#how-to-switch-it-on}

`python -m heat3d_watch setup rocketleague-stats --apply` (nastavi PacketSendRate=30), nato zaženite Rocket League

Ukaz vtipkajte v terminalu, odprtem v mapi watcherja (glej [Preden začneš](before-you-start.md)). Če ne uspe, zadnja vrstica pove, zakaj; [Namestitev in zagon](installing-and-running.md) pokriva običajne vzroke.

`python -m heat3d_watch setup rocketleague-stats` našteje datoteke, ki bi se spremenile; `python -m heat3d_watch setup rocketleague-stats --apply` jih spremeni, original pa ohrani kot `<file>.heat3d-backup` (glej [Ukazi](commands.md#setup)). Izpiše `rocketleague-stats: changed: ...` za vsako spremembo ali `rocketleague-stats: nothing to change`, če je že vklopljeno.

## Kako deluje {#how-it-works}

Rocket League: uradni Stats API, lokalna vtičnica, na katero igra zapisuje podatke tekme.

Vklopljeno v `<RL>\TAGame\Config\TAStatsAPI.ini` - ali `DefaultStatsAPI.ini`, kadar prva ne obstaja, kar igra prebere samo takrat - pod `[TAGame.MatchStatsExporter_TA]`:

```text
PacketSendRate   UpdateState messages per second; 0 (the default) switches the API off, at most 120
Port             the TCP port the game listens on, default 49123 (WebPort 49124 is a WebSocket copy)
```

Igra je strežnik: odjemalec se poveže na 127.0.0.1:49123 in bere tok JSON predmetov `{"Event": ime, "Data": {...}}` (nekatere različice pošljejo Data kot JSON niz), enega za drugim brez ločil. Dogodki se pošljejo v taktu, ko se zgodijo, neodvisno od hitrosti:

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

Lokacije so enote Unreal (centimetri), Z navzgor; polje je okoli 8200 x 10240, z golovi pri Y = +-5120. Položaji avtomobilov niso del API-ja: imajo mesto samo žoga, kjer je bila zadeta, zadeta gol ali zadela prečko.

Vsako sporočilo se shrani tudi cel (pravilo pretvornika 3DHeat, docs/converters.md v repozitoriju pregledovalnikja): `heat.raw.parquet`, `type` je ime dogodka sporočila, `text` je predmet, kakor je prišel s toka. UpdateState, bajt za bajtom enak prejšnjemu (zaustavljena tekma, meni), se shrani enkrat in se šteje v `unchanged_replies` v meta.json. Sporočila med tekmami čakajo v zaostanku za začetek naslednje tekme; kar ostane, ko se igra zapre, dobi svojo sejo. Znaki med predmeti, ki niso JSON, se shranijo kot "junk".

Viri: <https://www.rocketleague.com/en/developer/stats-api> (uradna stran); imena polj in okvir TCP potrjena z odjemalcem rlstatsapi (<https://docs.rs/crate/rlstatsapi>, MIT; prebrano samo zaradi dejstev).

## Položaji in osi {#positions-and-axes}

| | |
|---|---|
| Položaji zabeleženi | da |
| Navpična os | `z` |
| Enote | enote Unreal (centimetri) |
| Zrcaljeno za pregledovalnik | brez |
| Merilo enote (`scale`: pregledovalnik položaje pomnoži z njim) | 1 |

To gre v `meta.json` vsake seje (`axes`) in, kadar seja ima položaje, v nogo `heat.parquet`, zato pregledovalnik sam obrne in premeri vrstice - glej [Podatki](the-data.md).

## Več igralcev {#multiplayer}

- Označeno kot igranje na spletu (`multiplayer`): **da**. `games --markdown` to prikaže kot "dovoljeno (bere samo to, kar igra objavi)".
- Vrsta `gsi`: bere samo to, kar igra ali platforma ponudi (vmesnik za stanje igre ali lokalni API, ki ga igra streže), zato zapisuje tudi pri igranju na spletu, ne samo brez njega; zastavica odloča samo, ali sme kdaj brati pomnilnik.
- Pomnilnik: **nikoli** ga ta adapter ne bere. Pomnilnik berejo samo adapterji `memory`, in nikoli za igro, označeno kot igranje na spletu - glej [Viri in pravila](sources-and-rules.md).

## Zabeležena statistika {#statistics-recorded}

Statistične ključe, ki jih koda tega adapterja nastavi po imenu (`stats` v `meta.json` vsake seje in tabela `stats` v `watcher.sqlite`):

`bad_packets`, `demolished`, `other_goals`, `overtime`, `result`, `team_goals`

Ključ v zavitih oklepajih se dokonča med izvajanjem (`score.{team}` je en ključ za vsako ekipo). Ključi, ki jih koda vzame iz tabele igrinih polj ali iz igrinih lastnih imen statistike, na tem seznamu niso; "Kaj se zapiše" zgoraj jih navaja.

## Popolnost {#completeness}

Watcher sledi [pravilu pretvornika](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md) 3DHeat: kar vir vsebuje, se prebere ali shrani, nikoli se ne zavrže. Poleg vrstic se vsak paket, stran, vrstica ali odgovor, ki ga adapter prejme, shrani cel v `heat.raw.parquet` seje (stolpci `time`, `ms`, `type`, `used`, `payload`, `text` in vsako polje, shranjeno po imenu; `used` označi, kaj je postalo tudi vrstica), `selfCheck.completeness` v `meta.json` pa šteje vsak `type` - `lost` je 0.

**Prebrano**

- BallHit (mesto, kdo, ekipa, hitrosti pred in po udarcu), GoalScored (mesto udarca, strelec, podajalec, hitrost, čas gola), CrossbarHit (mesto, zadnji dotik, hitrost, sila), StatfeedEvent (dogodek, tip, glavna in stranska tarča), MatchEnded (zmagovalec, izid), vsak drug dogodek kot vrstica z imenom dogodka
- iz UpdateState: arena, tarča kamere zunaj ponovitev (kdo je `me`), rezultati ekip, vsakega igralca goli, asistence, obrambe, streli, rušenja, dotiki, dotiki avtomobilov in rezultat (lastni kot statistika, vsi kot `player_result` ob koncu tekme); overtime iz ClockUpdatedSeconds

**Shranjeno surovo**

- vsako sporočilo celo, kakor je prišlo s toka (`text`), pod imenom svojega dogodka: `UpdateState` (PrimaryId in Shortcut vsakega igralca, ura, hitrost žoge in ekipa, imena in barve ekip, zastavice ponovitve in zmagovalca, stanje avtomobila tam, kjer ga igra pošlje), `BallHit`, `GoalScored` (z zadnjim dotikom žoge), `CrossbarHit`, `StatfeedEvent`, `MatchCreated`, `MatchInitialized`, `CountdownBegin`, `RoundStarted`, `GoalReplayStart`, `GoalReplayWillEnd`, `GoalReplayEnd`, `MatchPaused`, `MatchUnpaused`, `MatchEnded`, `PodiumStart`, `ReplayCreated`, `MatchDestroyed`, `ClockUpdatedSeconds` in vsak dogodek, ki ga kasnejša različica doda
- UpdateState, bajt za bajtom enak prejšnjemu (pavza, meniji), se shrani enkrat in šteje (`unchanged_replies` v meta.json)
- sporočila med tekmami: ob svojem času pred začetkom naslednje tekme; po zadnji tekmi v svoji seji (`raw_only` v meta.json)
- `unreadable`: predmet, ki ni sporočilo Stats API; `junk`: znaki med predmeti

**Ni na voljo**

- položaji avtomobilov in stanje avtomobila med igranjem: igra jih pošlje samo gledalcem
- UpdateState med dvema pošiljanjema: igra pošlje PacketSendRate na sekundo (`setup` nastavi 30, igra dovoli do 120); dogodki se pošljejo v taktu, ko se zgodijo
- kopija WebSocket na WebPort (49124): enaka sporočila kot na TCP vratih, ne preberejo se dvakrat

**Velikost**: UpdateState je 1-3 KB za šest igralcev, 30 na sekundo: približno 100-300 MB na uro v `raw.bin`, medtem ko tekma teče, in desetino ali manj v zstd `heat.raw.parquet` (ocenjeno po dokumentiranem formatu, ni izmerjeno na igri)

## Preverjeno {#verified}

preizkušeno na sporočilih v dokumentiranem formatu, poslanih z lažnim lokalnim strežnikom; še nepreizkušeno z igro

## Vir {#source}

[heat3d_watch/adapters/rocketleague.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/rocketleague.py)

<!-- Generated from the adapter by tools/gen_game_pages.py; change the adapter and run it again rather than editing this page. -->
