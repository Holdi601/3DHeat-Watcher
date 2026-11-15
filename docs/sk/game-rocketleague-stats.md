---
title: "Rocket League (stav hry)"
nav_order: 40
lang: "sk"
source: game-rocketleague-stats.md
source_hash: "3da6ea772068"
nav_exclude: true
search_exclude: true
---
# Rocket League (stav hry) {#rocket-league-game-state}

Počas hry Rocket League watcher ukladá, čo hra hlási programom vo vašom počítači, aby ste to neskôr mohli pozrieť na mape v 3DHeat prehliadači.

*Technické údaje: adaptér `rocketleague-stats`, typ [`gsi`](sources-and-rules.md); beží, kým beží `RocketLeague.exe`, a hľadá nové dáta každých 0,05 s.*

## Čo sa zaznamenáva {#what-is-recorded}

- zásahy lopty s miestom lopty (XYZ, jednotky Unreal), kto zasiahol a rýchlosti
- góly s miestom nárazu, strelcom, prihrávajúcim a rýchlosťou; zásahy do prečnice s miestom
- štatistický kanál (demolácie, zákroky, strely, epické zákroky, ...), výkopy, repriky, začiatok a koniec zápasu, víťaz
- vlastné góly, asistencie, zákroky, strely, demá, doteky, skóre a skóre tímov, z UpdateState
- posledný riadok každého hráča na konci zápasu
- vaše vlastné riadky ako `me`: hráč pomenovaný v nastaveniach (`config --set player_names.rocketleague-stats=<name>`), inak ten, ktorého kamera sleduje mimo repríz
- žiadne polohy áut: API ich nemá

## Odkiaľ to berie {#where-it-comes-from}

Stats API: prúd JSON cez TCP z 127.0.0.1:49123 (port v <RL>\TAGame\Config\TAStatsAPI.ini alebo DefaultStatsAPI.ini)

## Ako to zapnúť {#how-to-switch-it-on}

`python -m heat3d_watch setup rocketleague-stats --apply` (nastaví PacketSendRate=30), potom spustite Rocket League

Príkaz napíšte do terminálu otvoreného v priečinku watchera (pozrite [Pred začiatkom](before-you-start.md)). Ak zlyhá, posledný riadok povie prečo; [Inštalácia a spustenie](installing-and-running.md) popisuje obvyklé príčiny.

`python -m heat3d_watch setup rocketleague-stats` vypíše súbory, ktoré by zmenil; `python -m heat3d_watch setup rocketleague-stats --apply` ich zmení a pôvodný súbor nechá ako `<file>.heat3d-backup` (pozrite [Príkazy](commands.md#setup)). Pri každej zmene vypíše `rocketleague-stats: changed: ...`, alebo `rocketleague-stats: nothing to change`, ak je už zapnuté.

## Ako to funguje {#how-it-works}

Rocket League: oficiálne Stats API, lokálny soket, do ktorého hra zapisuje údaje o zápase.

Zapína sa v `<RL>\TAGame\Config\TAStatsAPI.ini` - alebo v `DefaultStatsAPI.ini`, keď ten prvý neexistuje, lebo hra číta len ten - v sekcii `[TAGame.MatchStatsExporter_TA]`:

```text
PacketSendRate   UpdateState messages per second; 0 (the default) switches the API off, at most 120
Port             the TCP port the game listens on, default 49123 (WebPort 49124 is a WebSocket copy)
```

Hra je server: klient sa pripojí na 127.0.0.1:49123 a číta prúd JSON objektov `{"Event": name, "Data": {...}}` (niektoré verzie posielajú Data ako JSON reťazec), jeden za druhým bez oddeľovačov. Udalosti sa posielajú v tiku, keď sa stanú, nezávisle od frekvencie:

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

Polohy sú v jednotkách Unreal (centimetre), Z smerom nahor; ihrisko má okolo 8200 x 10240 s bránkami pri Y = ±5120. Polohy áut nie sú súčasťou API: má miesto len lopta tam, kde bola zasiahnutá, gólovaná alebo zasiahla brvno.

Každá správa sa uchováva aj celá (pravidlo konvertorov 3DHeat, docs/converters.md v repozitári prehliadača): `heat.raw.parquet`, `type` je názov udalosti správy, `text` objekt tak, ako prišiel z prúdu. UpdateState, ktorý je bajt po bajte rovnaký ako predchádzajúci (pozastavený zápas, menu), sa uchová raz a počíta sa v `unchanged_replies` v meta.json. Správy medzi zápasmi čakajú v zásobníku na reláciu ďalšieho zápasu; čo zostane, keď hra skončí, dostane vlastnú reláciu. Znaky medzi objektmi, ktoré nie sú JSON, sa uchovajú ako „junk".

Zdroje: <https://www.rocketleague.com/en/developer/stats-api> (oficiálna stránka); veľkosť písmen v poliach a rámcovanie TCP potvrdené podľa klienta rlstatsapi (<https://docs.rs/crate/rlstatsapi>, MIT; čítané len kvôli faktom).

## Polohy a osi {#positions-and-axes}

| | |
|---|---|
| Zaznamenané polohy | áno |
| Osa nahor | `z` |
| Jednotky | jednotky Unreal (centimetre) |
| Zrkadlenie pre prehliadač | žiadne |
| Mierka jednotiek (`scale`: prehliadač ňou násobí polohy) | 1 |

Tieto hodnoty idú do `meta.json` každej relácie (`axes`) a, keď relácia obsahuje polohy, do päty `heat.parquet`, takže 3DHeat prehliadač ich otáča a škáluje sám - pozrite [Dáta](the-data.md).

## Multiplayer {#multiplayer}

- Označené ako hrané online (`multiplayer`): **áno**. `games --markdown` to zobrazí ako „povolené (číta len to, čo hra zverejňuje)".
- Druh `gsi`: číta len to, čo hra alebo platforma sprístupňuje (integrácia stavu hry alebo lokálne API, ktoré hra poskytuje), takže zaznamenáva aj v online hre, nielen offline; príznak rozhoduje len o tom, či sa pamäť smie vôbec čítať.
- Pamäť: adaptér ju **nikdy** nečíta. Pamäť čítajú len adaptéry typu `memory` a nikdy pre hru označenú ako hranú online - pozrite [Zdroje a pravidlá](sources-and-rules.md).

## Zaznamenané štatistiky {#statistics-recorded}

Kľúče štatistík, ktoré kód tohto adaptéra nastavuje podľa mena (`stats` každej relácie v `meta.json` a tabuľka `stats` v `watcher.sqlite`):

`bad_packets`, `demolished`, `other_goals`, `overtime`, `result`, `team_goals`

Kľúč v zložených zátvorkách sa dopĺňa za behu (`score.{team}` je jeden kľúč pre každý tím). Kľúče, ktoré kód berie z tabuľky polí hry alebo z jej vlastných názvov štatistík, v tomto zozname nie sú; čo sa zaznamenáva, uvádza vyššie časť „Čo sa zaznamenáva".

## Úplnosť {#completeness}

Watcher sa riadi pravidlom konvertorov 3DHeat ([pravidlo konvertorov](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md)): čo zdroj obsahuje, sa načíta alebo uchová, nikdy sa nezahodí. Okrem riadkov sa každý paket, stránka, riadok alebo odpoveď, ktorú adaptér dostane, uchová celá v `heat.raw.parquet` relácie (stĺpce `time`, `ms`, `type`, `used`, `payload`, `text` a ďalšie polia uchované podľa mena; `used` označuje, čo sa stalo aj riadkami), a `selfCheck.completeness` v `meta.json` počíta každý `type` - `lost` je 0.

**Načítané**

- BallHit (miesto, kto, tím, rýchlosti pred a po), GoalScored (miesto nárazu, strelec, asistujúci, rýchlosť, čas gólu), CrossbarHit (miesto, posledný dotyk, rýchlosť, sila), StatfeedEvent (udalosť, typ, hlavný a sekundárny cieľ), MatchEnded (víťaz, výsledok), názov každej ďalšej udalosti ako riadok
- z UpdateState: aréna, cieľ kamery mimo repríz (kto je `me`), skóre tímov, góly, asistencie, zákroky, strely, demá, doteky, doteky autom a skóre každého hráča (vlastné ako štatistiky, všetkých ako `player_result` na konci zápasu); pretekanie z ClockUpdatedSeconds

**Uchované surové**

- každá správa celá, tak ako prišla z prúdu (`text`), pod svojím názvom udalosti Event: `UpdateState` (PrimaryId a Shortcut každého hráča, hodiny, rýchlosť a tím lopty, názvy a farby tímov, príznaky repríz a víťaza, a stav auta, ak ho hra posiela), `BallHit`, `GoalScored` (s posledným dotykom lopty), `CrossbarHit`, `StatfeedEvent`, `MatchCreated`, `MatchInitialized`, `CountdownBegin`, `RoundStarted`, `GoalReplayStart`, `GoalReplayWillEnd`, `GoalReplayEnd`, `MatchPaused`, `MatchUnpaused`, `MatchEnded`, `PodiumStart`, `ReplayCreated`, `MatchDestroyed`, `ClockUpdatedSeconds` a každú udalosť, ktorú pridá neskoršia verzia
- UpdateState, ktorý je bajt po bajte rovnaký ako predchádzajúci (pozastavené, menu), sa uchová raz a počíta sa (`unchanged_replies` v meta.json)
- správy medzi zápasmi: v ich vlastnom čase pred začiatkom ďalšieho zápasu; po poslednom zápase v ich vlastnej relácii (`raw_only` v meta.json)
- `unreadable`: objekt, ktorý nie je správou Stats API; `junk`: znaky medzi objektmi

**Nie je k dispozícii**

- stav áut a polohy áut počas hry: hra ich posiela len divákom
- UpdateState medzi dvoma odoslaniami: hra posiela PacketSendRate za sekundu (`setup` nastaví 30, hra dovolí až 120); udalosti sa posielajú v tiku, keď sa stanú
- kópia WebSocket na WebPort (49124): tie isté správy ako na porte TCP, nečítané dvakrát

**Veľkosť**: UpdateState má 1-3 KB pri šiestich hráčoch, 30 za sekundu: približne 100-300 MB za hodinu v `raw.bin`, keď zápas beží, a desatina alebo menej v zstd `heat.raw.parquet` (odhad z zdokumentovaného formátu, nezmerané na hre)

## Overené {#verified}

overené na správach v zdokumentovanom formáte, ktoré poslal falošný lokálny server; nevyskúšané na samotnej hre

## Zdroj {#source}

[heat3d_watch/adapters/rocketleague.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/rocketleague.py)

<!-- Generated from the adapter by tools/gen_game_pages.py; change the adapter and run it again rather than editing this page. -->
