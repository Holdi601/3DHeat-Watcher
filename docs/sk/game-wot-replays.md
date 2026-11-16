---
title: "World of Tanks (replaye)"
nav_order: 48
lang: "sk"
source: game-wot-replays.md
source_hash: "4cff18c29936"
nav_exclude: true
search_exclude: true
---
# World of Tanks (replaye) {#world-of-tanks-replays}

Po bitke vo World of Tanks watcher premení replay, ktorý hra uložila, na súbory, ktoré si môžete pozrieť na mape vo vieweri 3DHeat.

*Technické podrobnosti: adaptér `wot-replays`, druh [`replay`](sources-and-rules.md); beží stále (nečaká, kým sa spustí hra) a hľadá nové dáta každých 5 s.*

## Čo sa zaznamenáva {#what-is-recorded}

- pozícia a smer každého vozidla asi 10-krát za sekundu, kým ho nahrávací klient poznal: vlastný tím po celý čas, nepriateľ, kým je spozorovaný
- hráč, tím a vozidlo (národ:tank) každého z nich; smrti tam, kde obeť padla, a zabitia tam, kde stál zabijak, s presnosťou na asi sekundu, z výsledkov
- mapa; zabitia, poškodenie, prežitie a výsledok nahrávajúceho hráča ako štatistiky

## Odkiaľ to pochádza {#where-it-comes-from}

replaye, ktoré World of Tanks ukladá: &lt;World of Tanks>/replays/\*.wotreplay (so zapnutým nahrávaním bitiek), prevádza ich externý konvertor `heat3d-wot-replay` (exporters/ext/wot-replay)

## Ako to zapnúť {#how-to-switch-it-on}

zapnite nahrávanie bitiek v nastaveniach World of Tanks (General > Record battles) a nainštalujte konvertor: pip install -e &lt;3DHeat>/exporters/ext/wot-replay

Nastavenia z premenných prostredia:

- `HEAT3D_WOT_REPLAY`: priečinok konvertora (klon alebo rozbalené vydanie), keď nie je nainštalovaný ani vedľa watchera

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

#### World of Tanks a World of Warships {#world-of-tanks-and-world-of-warships}

Obe ukladajú replay každej bitky do `<game>/replays/`, keď je nahrávanie zapnuté
(`*.wotreplay`, `*.wowsreplay`); inštalácie sa hľadajú cez zoznam Wargaming
Game Center, `C:/Games/World_of_Tanks*` / `World_of_Warships*`, a Steam. Ako pri
War Thunder, watcher súbory sám nečíta: číta ich externý konvertor každej z nich
(`exporters/ext/wot-replay`, príkaz `heat3d-wot-replay`; `exporters/ext/wows-replay`,
príkaz `heat3d-wows-replay`), každý
samostatný projekt. Keď sa nájde v PATH, je nainštalovaný alebo vedľa
watchera, premení každý nový replay na `<map>/<match>.parquet` a `<match>.match.json`
v priečinku relácie; keď chýba, watcher raz napíše, ako ho nainštalovať. Riadok
nahrávajúceho hráča - vozidlo alebo loď, zabitia, poškodenie (World of Tanks),
či prežil, a výsledok (World of Tanks) - sa stane štatistikami relácie. Čo každý
konvertor číta a čo nie, je v jeho README.

Ten istý modul slúži aj pre: [Counter-Strike 2 (replaye)](game-cs2-demos.md), [Dota 2 (replaye)](game-dota-replays.md), [osu! (replaye)](game-osu-replays.md), [Squad (replaye)](game-squad-demos.md), [War Thunder (replaye)](game-warthunder-replays.md), [World of Warships (replaye)](game-wows-replays.md).

## Pozície a osi {#positions-and-axes}

| | |
|---|---|
| Pozície sa zaznamenávajú | áno |
| Os nahor | `y` |
| Jednotky | metre (x na východ, y nahor, z na sever) |
| Zrkadlené pre viewer | `z` |
| Mierka jednotiek (`scale`: viewer násobí pozície touto hodnotou) | 1 |

Tieto hodnoty sa zapíšu do `meta.json` každej relácie (`axes`) a, ak relácia obsahuje pozície, do päty `heat.parquet`, takže viewer 3DHeat otáča a mierni riadky sám - pozrite [Dáta](the-data.md).

## Viachráčová hra {#multiplayer}

- Označené ako hrané online (`multiplayer`): **áno**. `games --markdown` to zobrazí ako "povolené (číta len to, čo hra zverejňuje)".
- Druh `replay`: číta len to, čo hra alebo platforma vydáva (replaye a dema, ktoré hra ukladá), takže zaznamenáva aj online hru, aj hru offline; príznak rozhoduje len o tom, či sa pamäť smie čítať.
- Pamäť: adaptér ju **nikdy** nečíta. Pamäť čítajú len adaptéry `memory` a nikdy pre hru označenú ako hranú online - pozrite [Zdroje a pravidlá](sources-and-rules.md).

## Zaznamenané štatistiky {#statistics-recorded}

Kľúče štatistík, ktoré kód tohto adaptéra nastavuje podľa mena (`stats` každej relácie v `meta.json` a tabuľka `stats` v `watcher.sqlite`):

`map`, `survived`, `vehicle`, `won`

Kľúč v zložených zátvorkách sa dopĺňa pri behu (`score.{team}` je jeden kľúč pre každý tím). Kľúče, ktoré kód berie z tabuľky polí hry alebo z mien štatistík hry, v tomto zozname nie sú; "Čo sa zaznamenáva" vyššie ich uvádza.

## Úplnosť {#completeness}

Konvertor, ktorý tento adaptér spúšťa, dodržiava [pravidlo konvertorov](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md) 3DHeat: to, čo replay obsahuje, sa číta alebo uchováva, nikdy sa nezahadzuje - prečíta sa do tabuľky a dokumentu zápasu, všetko ostatné sa uchová celé v sprievodných súboroch vedľa nich a počíta sa v `selfCheck.completeness` dokumentu zápasu. Vlastná dokumentácia konvertora uvádza, čo číta, čo uchováva surové a čo nedokáže prečítať.

## Overené {#verified}

konvertor je overený na verejných replayoch z viacerých verzií hry a testami na zostavených replayoch; tento hák je overený len testami s náhradným príkazom

## Zdroj {#source}

[heat3d_watch/adapters/replays.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/replays.py)

<!-- Generated from the adapter by tools/gen_game_pages.py; change the adapter and run it again rather than editing this page. -->
