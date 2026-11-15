---
title: "Rocket League (stav hry)"
nav_order: 40
lang: "cs"
source: game-rocketleague-stats.md
source_hash: "3da6ea772068"
nav_exclude: true
search_exclude: true
---
# Rocket League (stav hry) {#rocket-league-game-state}

Když hrajete Rocket League, Watcher ukládá, co hra hlásí programům na vašem počítači, abyste se na to mohli později podívat na mapě v prohlížeči 3DHeat.

*Technické podrobnosti: adaptér `rocketleague-stats`, druh [`gsi`](sources-and-rules.md); běží, když je spuštěný `RocketLeague.exe`, a hledá nová data každých 0,05 s.*

## Co se zaznamenává {#what-is-recorded}

- zásahy do míče s místem míče (XYZ, jednotky Unreal), kdo ho zasáhl a rychlosti
- góly s místem nárazu, střelcem, nahrávačem a rychlostí; zásahy do břevna s místem
- statistický kanál (demolice, zákroky, střely, epické zákroky, ...), výkopy, repláye, začátek a konec zápasu, vítěz
- vlastní góly, asistence, zákroky, střely, demolice, dotyky, skóre a skóre týmů z UpdateState
- konečný řádek každého hráče na konci zápasu
- vaše vlastní řádky jako `me`: hráč pojmenovaný v nastavení (`config --set player_names.rocketleague-stats=<name>`), jinak ten, kterého kamera hry sleduje mimo repláye
- žádné pozice aut: API je nemá

## Odkud to pochází {#where-it-comes-from}

API statistik: proud JSON přes TCP z 127.0.0.1:49123 (port v &lt;RL>\TAGame\Config\TAStatsAPI.ini nebo DefaultStatsAPI.ini)

## Jak to zapnout {#how-to-switch-it-on}

`python -m heat3d_watch setup rocketleague-stats --apply` (nastaví PacketSendRate=30), pak spusťte Rocket League

Příkaz napište do terminálu otevřeného ve složce Watcheru (viz [Než začnete](before-you-start.md)). Pokud selže, poslední řádek řekne proč; [Instalace a spuštění](installing-and-running.md) popisuje obvyklé příčiny.

`python -m heat3d_watch setup rocketleague-stats` vypíše soubory, které by změnil; `python -m heat3d_watch setup rocketleague-stats --apply` je opravdu změní a původní soubor uloží jako `<file>.heat3d-backup` (viz [Příkazy](commands.md#setup)). Pro každou změnu vypíše `rocketleague-stats: changed: ...`, nebo `rocketleague-stats: nothing to change`, když je už zapnuto.

## Jak to funguje {#how-it-works}

Rocket League: oficiální Stats API, lokální socket, do kterého hra zapisuje údaje o zápasu.

Zapíná se v `<RL>\TAGame\Config\TAStatsAPI.ini` – nebo v `DefaultStatsAPI.ini`,
když ten první neexistuje, a hra čte jen ten – pod
`[TAGame.MatchStatsExporter_TA]`:

```text
PacketSendRate   UpdateState messages per second; 0 (the default) switches the API off, at most 120
Port             the TCP port the game listens on, default 49123 (WebPort 49124 is a WebSocket copy)
```

Hra je server: klient se připojí na 127.0.0.1:49123 a čte proud
JSON objektů `{"Event": name, "Data": {...}}` (některé verze posílají Data jako
JSON řetězec), jeden za druhým, bez oddělovačů. Události se posílají v tiku, kdy
se stanou, nezávisle na rychlosti:

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

Souřadnice jsou v jednotkách Unreal (centimetry), osa Z nahoru; hřiště má asi 8200 x 10240
s brankami v Y = ±5120. Pozice aut nejsou součástí API: místo má jen míč tam, kde byl
zasažen, dal gól nebo zasáhl břevno.

Každá zpráva se uloží celá také (pravidlo převaděče 3DHeat, docs/converters.md
v repozitáři prohlížeče): `heat.raw.parquet`, `type` je název události `Event` ze zprávy,
`text` je objekt tak, jak přišel z proudu. UpdateState, který je bajt po bajtu
stejný jako ten předchozí (pozastavený zápas, menu), se uloží jednou a počítá se
v `unchanged_replies` v meta.json. Zprávy mezi zápasy čekají v zásobníku na
začátek dalšího zápasu; co zbude, když se hra zavře, dostane vlastní relaci.
Znaky mezi objekty, které nejsou JSON, se ukládají jako „junk“.

Zdroje: <https://www.rocketleague.com/en/developer/stats-api> (oficiální stránka);
velikost polí a rámování TCP ověřeno podle klienta rlstatsapi
(<https://docs.rs/crate/rlstatsapi>, MIT; použito jen pro fakta).

## Pozice a osy {#positions-and-axes}

| | |
|---|---|
| Zaznamenané pozice | ano |
| Osa nahoru | `z` |
| Jednotky | jednotky Unreal (centimetry) |
| Zrcadleno pro prohlížeč | žádné |
| Měřítko jednotek (`scale`: prohlížeč pozice tímto násobí) | 1 |

Tyto údaje se zapíšou do `meta.json` každé relace (`axes`) a, pokud má relace pozice, do zápatí `heat.parquet`, takže prohlížeč 3DHeat otáčí a měřítko řádků nastavuje sám – viz [Data](the-data.md).

## Více hráčů {#multiplayer}

- Označeno jako hraná online (`multiplayer`): **ano**. `games --markdown` to ukazuje jako „povoleno (čte jen to, co hra zveřejňuje)“.
- Druh `gsi`: čte jen to, co hra nebo platforma vydává (integrace stavu hry nebo lokální API, které hra poskytuje), takže zaznamenává i v online hře, nejen offline; příznak rozhoduje jen o tom, zda se paměť smí vůbec číst.
- Paměť: tento adaptér ji **nikdy** nečte. Paměť čtou jen adaptéry typu `memory` a nikdy u hry označené jako hraná online – viz [Zdroje a pravidla](sources-and-rules.md).

## Zaznamenané statistiky {#statistics-recorded}

Klíče statistik, které kód tohoto adaptéru nastavuje podle názvu (u každé relace `stats` v `meta.json` a v tabulce `stats` souboru `watcher.sqlite`):

`bad_packets`, `demolished`, `other_goals`, `overtime`, `result`, `team_goals`

Klíč ve složených závorkách se doplní za běhu (`score.{team}` je jeden klíč pro každý tým). Klíče, které kód bere z tabulky polí hry nebo z jejích vlastních názvů statistik, v tomto seznamu nejsou; výše v části „Co se zaznamenává“ jsou pojmenovány.

## Úplnost {#completeness}

Watcher se řídí [pravidlem převaděče](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md) 3DHeat: co zdroj obsahuje, se přečte nebo uloží, nikdy se nezahodí. Kromě řádků se každý paket, stránka, řádek nebo odpověď, které adaptér přijme, uloží celý do `heat.raw.parquet` relace (sloupce `time`, `ms`, `type`, `used`, `payload`, `text` a případná pole uložená podle názvu; `used` označuje, co se také stalo řádky) a `selfCheck.completeness` v `meta.json` počítá každý `type` – `lost` je 0.

**Načteno**

- BallHit (místo, kdo, tým, rychlosti před a po), GoalScored (místo nárazu, střelec, nahrávač, rychlost, čas gólu), CrossbarHit (místo, poslední dotyk, rychlost, síla), StatfeedEvent (událost, typ, hlavní a vedlejší cíl), MatchEnded (vítěz, výsledek), název každé další události jako řádek
- z UpdateState: aréna, cíl kamery mimo repláye (kdo je `me`), skóre týmů, góly, asistence, zákroky, střely, demolice, dotyky a dotyky s autem a skóre každého hráče (vlastní jako statistiky, všech jako `player_result` na konci zápasu); přesčas z ClockUpdatedSeconds

**Uchováno surové**

- každá zpráva celá, tak jak přišla z proudu (`text`), pod svým názvem události: `UpdateState` (PrimaryId a Shortcut každého hráče, hodiny, rychlost míče a jeho tým, názvy a barvy týmů, příznaky replaye a vítěze a stav auta, pokud ho hra posílá), `BallHit`, `GoalScored` (s posledním dotykem míče), `CrossbarHit`, `StatfeedEvent`, `MatchCreated`, `MatchInitialized`, `CountdownBegin`, `RoundStarted`, `GoalReplayStart`, `GoalReplayWillEnd`, `GoalReplayEnd`, `MatchPaused`, `MatchUnpaused`, `MatchEnded`, `PodiumStart`, `ReplayCreated`, `MatchDestroyed`, `ClockUpdatedSeconds` a každou událost, kterou přidá pozdější verze
- UpdateState, který je bajt po bajtu stejný jako ten předchozí (pozastavení, menu), se uloží jednou a počítá se (`unchanged_replies` v meta.json)
- zprávy mezi zápasy: v jejich vlastním čase před začátkem dalšího zápasu; po posledním zápasu v jeho vlastní relaci (`raw_only` v meta.json)
- `unreadable`: objekt, který není zprávou Stats API; `junk`: znaky mezi objekty

**Nedostupné**

- pozice a stav aut během hry: hra je posílá jen divákům
- UpdateState mezi dvěma odesláními: hra posílá PacketSendRate za sekundu (`setup` nastaví 30, hra dovolí až 120); události se posílají v tiku, kdy se stanou
- kopie WebSocket na WebPort (49124): stejné zprávy jako na portu TCP, nečtou se dvakrát

**Velikost**: UpdateState má 1–3 KB pro šest hráčů, 30 za sekundu: asi 100–300 MB za hodinu v `raw.bin`, zatímco běží zápas, a desetinu nebo méně v zstd `heat.raw.parquet` (odhad z dokumentovaného formátu, neměřeno ve hře)

## Ověřeno {#verified}

testováno na zprávách v dokumentovaném formátu, které posílal falešný lokální server; netestováno proti hře

## Zdroj {#source}

[heat3d_watch/adapters/rocketleague.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/rocketleague.py)

<!-- Generated from the adapter by tools/gen_game_pages.py; change the adapter and run it again rather than editing this page. -->
