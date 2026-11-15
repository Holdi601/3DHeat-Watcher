---
title: "Counter-Strike 2 (replaye)"
nav_order: 8
lang: "sk"
source: game-cs2-demos.md
source_hash: "d115f9085302"
nav_exclude: true
search_exclude: true
---
# Counter-Strike 2 (replaye) {#counter-strike-2-replays}

Po zápase Counter-Strike 2 watcher premení replay, ktorý hra uložila, na súbory, ktoré si môžete pozrieť na mape vo vieweri 3DHeat.

*Technické podrobnosti: adaptér `cs2-demos`, druh [`replay`](sources-and-rules.md); beží stále (nečaká, kým sa spustí hra) a hľadá nové dáta každých 5 s.*

## Čo sa zaznamenáva {#what-is-recorded}

- pozícia, smer pohľadu, zdravie a peniaze každého hráča (každý 8. tick)
- zabitia, smrti, poškodenie, granáty, položenie a odzbrojenie bomby tam, kde sa stali
- kolá, skóre, ekonomika; riadok štatistík prihláseného hráča z tabuľky výsledkov

## Odkiaľ to pochádza {#where-it-comes-from}

dema, ktoré CS2 ukladá: &lt;CS2>/game/csgo/replays/\*.dem (stiahnuté z histórie zápasov) a &lt;CS2>/game/csgo/\*.dem (nahrané)

## Ako to zapnúť {#how-to-switch-it-on}

stiahnite demo zápasu v CS2 (Watch > Your Matches), alebo ho nahrajte príkazom konzoly `record`

Nastavenia z premenných prostredia:

- `HEAT3D_CS2`: priečinok 3DHeat CS2, keď nie je vedľa watchera ani nainštalovaný

## Ako to funguje {#how-it-works}

Replaye a dema: to, čo hra uloží o zápase, prevedené až po skončení zápasu.

Replay obsahuje všetko, čo živé rozhranie vo viachráčových hrách zadržiava -
pozíciu každého hráča, každé zabitie tam, kde sa stalo. Je to súbor, ktorý
hra zapisuje pre svojich hráčov, takže jeho čítanie do hry nezasiahne. Watcher
sleduje priečinky, kam ich hry ukladajú, počká, kým sa nový súbor prestane
zväčšovať (inak by ho hra ešte zapisovala), a prevádza ho vo worker vlákne,
takže dlhý prevod nikdy nezdrží zvyšok watchera.

Pri prvom zistení priečinka sa replaye, ktoré sú v ňom už uložené, iba
zaznamenajú, nie prevedú: hráč s rokmi dem by inak našiel watcher zaneprázdnený
celý deň. `python -m heat3d_watch replays <adapter> [folder]` prevedie existujúce
na požiadanie.

#### Counter-Strike 2 {#counter-strike-2}

CS2 ukladá dema, ktoré hráč stiahne z histórie zápasov (karta watch), do
`<CS2>/game/csgo/replays/`, a dema nahrané príkazom konzoly `record` do
`<CS2>/game/csgo/`. Každé sa prevedie vlastným konvertorom CS2 tohto repozitára
(3DHeat CS2, github.com/Holdi601/3DHeat-CS2: pozícia, smer pohľadu, zdravie
a peniaze každého hráča každý ôsmy tick; zabitia, smrti, poškodenie, granáty,
položenie a odzbrojenie bomby tam, kde sa stali; kolá, skóre, ekonomika) do
priečinka relácie ako tabuľka `<map>/<match>.parquet` a súhrn `<match>.match.json`,
ktoré čítajú karty Heatmapa a Zápas vo vieweri. Tabuľka výsledkov zápasu sa stane
štatistikami relácie: pre hráča, ktorého Steam účet je prihlásený na tomto počítači
(zo súboru `loginusers.vdf` v Steame), pod jeho bežnými menami - zabitia, smrti,
asistencie, ADR, KAST, percento headshotov, prvé zabitia, clutchy - a skóre
a kolá.

Ten istý modul slúži aj pre: [Dota 2 (replaye)](game-dota-replays.md), [osu! (replaye)](game-osu-replays.md), [Squad (replaye)](game-squad-demos.md), [War Thunder (replaye)](game-warthunder-replays.md), [World of Tanks (replaye)](game-wot-replays.md), [World of Warships (replaye)](game-wows-replays.md).

## Pozície a osi {#positions-and-axes}

| | |
|---|---|
| Pozície sa zaznamenávajú | áno |
| Os nahor | `z` |
| Jednotky | palce (jednotky Source) |
| Zrkadlené pre viewer | `y` |
| Mierka jednotiek (`scale`: viewer násobí pozície touto hodnotou) | 1 |

Tieto hodnoty sa zapíšu do `meta.json` každej relácie (`axes`) a, ak relácia obsahuje pozície, do päty `heat.parquet`, takže viewer 3DHeat otáča a mierni riadky sám - pozrite [Dáta](the-data.md).

## Viachráčová hra {#multiplayer}

- Označené ako hrané online (`multiplayer`): **áno**. `games --markdown` to zobrazí ako "povolené (číta len to, čo hra zverejňuje)".
- Druh `replay`: číta len to, čo hra alebo platforma vydáva (replaye a dema, ktoré hra ukladá), takže zaznamenáva aj online hru, aj hru offline; príznak rozhoduje len o tom, či sa pamäť smie čítať.
- Pamäť: adaptér ju **nikdy** nečíta. Pamäť čítajú len adaptéry `memory` a nikdy pre hru označenú ako hranú online - pozrite [Zdroje a pravidlá](sources-and-rules.md).

## Zaznamenané štatistiky {#statistics-recorded}

Kľúče štatistík, ktoré kód tohto adaptéra nastavuje podľa mena (`stats` každej relácie v `meta.json` a tabuľka `stats` v `watcher.sqlite`):

`map`, `rounds`, `score.{team}`, `won`

Kľúč v zložených zátvorkách sa dopĺňa pri behu (`score.{team}` je jeden kľúč pre každý tím). Kľúče, ktoré kód berie z tabuľky polí hry alebo z mien štatistík hry, v tomto zozname nie sú; "Čo sa zaznamenáva" vyššie ich uvádza.

## Úplnosť {#completeness}

Konvertor, ktorý tento adaptér spúšťa, dodržiava [pravidlo konvertorov](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md) 3DHeat: to, čo replay obsahuje, sa číta alebo uchováva, nikdy sa nezahadzuje - prečíta sa do tabuľky a dokumentu zápasu, všetko ostatné sa uchová celé v sprievodných súboroch vedľa nich a počíta sa v `selfCheck.completeness` dokumentu zápasu. Vlastná dokumentácia konvertora uvádza, čo číta, čo uchováva surové a čo nedokáže prečítať.

## Overené {#verified}

konvertor je otestovaný na skutočných turnajových demách; sledovanie priečinka a štatistiky testami

## Zdroj {#source}

[heat3d_watch/adapters/replays.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/replays.py)

<!-- Generated from the adapter by tools/gen_game_pages.py; change the adapter and run it again rather than editing this page. -->
