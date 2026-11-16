---
title: "World of Warships (replaye)"
nav_order: 49
lang: "sk"
source: game-wows-replays.md
source_hash: "c822aca3f6fe"
nav_exclude: true
search_exclude: true
---
# World of Warships (replaye) {#world-of-warships-replays}

Po bitke vo World of Warships watcher premení replay, ktorý hra uložila, na súbory, ktoré si môžete pozrieť na mape vo vieweri 3DHeat.

*Technické podrobnosti: adaptér `wows-replays`, druh [`replay`](sources-and-rules.md); beží stále (nečaká, kým sa spustí hra) a hľadá nové dáta každých 5 s.*

## Čo sa zaznamenáva {#what-is-recorded}

- pozícia a smer každej lode, kým ju nahrávací klient videl (asi 6 až 7-krát za sekundu, keď sa pohybuje); vlastná loď hráča po celý čas
- hráč, spojenec alebo nepriateľ, a loď (loď nahrávajúceho hráča podľa mena, ostatné podľa čísla lode v hre); potopené lode tam, kde sa potopili, a ich zabijaci tam, kde stáli
- mapa; loď, zabitia a prežitie nahrávajúceho hráča ako štatistiky

## Odkiaľ to pochádza {#where-it-comes-from}

replaye, ktoré World of Warships ukladá: &lt;World of Warships>/replays/\*.wowsreplay (so zapnutými replaymi), prevádza ich externý konvertor `heat3d-wows-replay` (exporters/ext/wows-replay)

## Ako to zapnúť {#how-to-switch-it-on}

zapnite nahrávanie replayov vo World of Warships (`isReplayEnabled` v jej preferences.xml, alebo vlastné nastavenie hry, ak ho má) a nainštalujte konvertor: pip install -e &lt;3DHeat>/exporters/ext/wows-replay

Nastavenia z premenných prostredia:

- `HEAT3D_WOWS_REPLAY`: priečinok konvertora (klon alebo rozbalené vydanie), keď nie je nainštalovaný ani vedľa watchera

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

Ten istý modul slúži aj pre: [Counter-Strike 2 (replaye)](game-cs2-demos.md), [Dota 2 (replaye)](game-dota-replays.md), [osu! (replaye)](game-osu-replays.md), [Squad (replaye)](game-squad-demos.md), [War Thunder (replaye)](game-warthunder-replays.md), [World of Tanks (replaye)](game-wot-replays.md).

## Pozície a osi {#positions-and-axes}

| | |
|---|---|
| Pozície sa zaznamenávajú | áno |
| Os nahor | `y` |
| Jednotky | svetové jednotky World of Warships (x na východ, y nahor, z na sever; jedna je 15 m podľa geometrie trupu, 30 m podľa herných dostrelov) |
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
