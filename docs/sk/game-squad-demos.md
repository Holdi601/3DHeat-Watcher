---
title: "Squad (replaye)"
nav_order: 41
lang: "sk"
source: game-squad-demos.md
source_hash: "82c24e6df01c"
nav_exclude: true
search_exclude: true
---
# Squad (replaye) {#squad-replays}

Po zápase Squad watcher premení replay, ktorý hra uložila, na súbory, ktoré si môžete pozrieť na mape vo vieweri 3DHeat.

*Technické podrobnosti: adaptér `squad-demos`, druh [`replay`](sources-and-rules.md); beží stále (nečaká, kým sa spustí hra) a hľadá nové dáta každých 5 s.*

## Čo sa zaznamenáva {#what-is-recorded}

- pozícia každého hráča, uhol tela a rýchlosť zakaždým, keď ju server replikuje (až 8-krát za sekundu), pešo aj v pozemných vozidlách
- meno, tím, frakcia a skupina každého hráča, s nasledovaním zmien tímu
- nie: pohyb helikoptér, zabitia a rozmiestniteľné zariadenia - pozrite README čítačky

## Odkiaľ to pochádza {#where-it-comes-from}

serverové dema, ktoré Squad nahráva administrátorským príkazom AdminDemoRec: &lt;server>/SquadGame/Saved/Demos/\*.replay, číta ich externá čítačka `heat3d-squad-demo` (exporters/ext/squad-demo)

## Ako to zapnúť {#how-to-switch-it-on}

nahrávajte na serveri: dajte administrátorovi oprávnenie `demos` v Admins.cfg, potom v konzole hry AdminDemoRec &lt;name> a AdminDemoStop; demo skopírujte sem a nainštalujte čítačku: pip install -e &lt;3DHeat>/exporters/ext/squad-demo

Nastavenia z premenných prostredia:

- `HEAT3D_SQUAD_DEMO`: priečinok konvertora (klon alebo rozbalené vydanie), keď nie je nainštalovaný ani vedľa watchera

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

#### Squad {#squad}

Dedikované servery Squad nahrávajú demo zápasu, keď administrátor s oprávnením
`demos` spustí AdminDemoRec &lt;name> (a AdminDemoStop), do
`<server>/SquadGame/Saved/Demos/<name>.replay` - je to sieťový replay Unreal Engine
obsahujúci to, čo server replikoval, vrátane pohybu každého hráča. Watcher ich
nečíta sám: číta ich externá čítačka (3DHeat Squad demo reader,
`exporters/ext/squad-demo`, príkaz `heat3d-squad-demo`), oddelená, aby problém
s ňou nezasiahol nič iné. Spúšťa sa na každom novom deme v priečinkoch, kam
zapisuje lokálny server, alebo v priečinku, ktorý nastavenia pridajú pre dema
skopírované z prenajatého servera, a výsledok ide do priečinka relácie ako
`<map>/<match>.parquet` a `<match>.match.json`. Vrstva, mapa, počet hráčov
a dĺžka zápasu sa stanú štatistikami relácie.

Ten istý modul slúži aj pre: [Counter-Strike 2 (replaye)](game-cs2-demos.md), [Dota 2 (replaye)](game-dota-replays.md), [osu! (replaye)](game-osu-replays.md), [War Thunder (replaye)](game-warthunder-replays.md), [World of Tanks (replaye)](game-wot-replays.md), [World of Warships (replaye)](game-wows-replays.md).

## Pozície a osi {#positions-and-axes}

| | |
|---|---|
| Pozície sa zaznamenávajú | áno |
| Os nahor | `z` |
| Jednotky | jednotky Unreal (centimetre) |
| Zrkadlené pre viewer | žiadne |
| Mierka jednotiek (`scale`: viewer násobí pozície touto hodnotou) | 1 |

Tieto hodnoty sa zapíšu do `meta.json` každej relácie (`axes`) a, ak relácia obsahuje pozície, do päty `heat.parquet`, takže viewer 3DHeat otáča a mierni riadky sám - pozrite [Dáta](the-data.md).

## Viachráčová hra {#multiplayer}

- Označené ako hrané online (`multiplayer`): **áno**. `games --markdown` to zobrazí ako "povolené (číta len to, čo hra zverejňuje)".
- Druh `replay`: číta len to, čo hra alebo platforma vydáva (replaye a dema, ktoré hra ukladá), takže zaznamenáva aj online hru, aj hru offline; príznak rozhoduje len o tom, či sa pamäť smie čítať.
- Pamäť: adaptér ju **nikdy** nečíta. Pamäť čítajú len adaptéry `memory` a nikdy pre hru označenú ako hranú online - pozrite [Zdroje a pravidlá](sources-and-rules.md).

## Zaznamenané štatistiky {#statistics-recorded}

Kľúče štatistík, ktoré kód tohto adaptéra nastavuje podľa mena (`stats` každej relácie v `meta.json` a tabuľka `stats` v `watcher.sqlite`):

`layer`, `map`, `match_seconds`, `players`

Kľúč v zložených zátvorkách sa dopĺňa pri behu (`score.{team}` je jeden kľúč pre každý tím). Kľúče, ktoré kód berie z tabuľky polí hry alebo z mien štatistík hry, v tomto zozname nie sú; "Čo sa zaznamenáva" vyššie ich uvádza.

## Úplnosť {#completeness}

Konvertor, ktorý tento adaptér spúšťa, dodržiava [pravidlo konvertorov](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md) 3DHeat: to, čo replay obsahuje, sa číta alebo uchováva, nikdy sa nezahadzuje - prečíta sa do tabuľky a dokumentu zápasu, všetko ostatné sa uchová celé v sprievodných súboroch vedľa nich a počíta sa v `selfCheck.completeness` dokumentu zápasu. Vlastná dokumentácia konvertora uvádza, čo číta, čo uchováva surové a čo nedokáže prečítať.

## Overené {#verified}

čítačka je overená na verejných serverových demách (pohyb sa zhoduje s rýchlosťou, ktorú nesie; tím každého riadku sa zhoduje s frakciou jeho vojaka) a testami na zostavených demách; tento hák je overený len testami s náhradným príkazom

## Zdroj {#source}

[heat3d_watch/adapters/replays.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/replays.py)

<!-- Generated from the adapter by tools/gen_game_pages.py; change the adapter and run it again rather than editing this page. -->
