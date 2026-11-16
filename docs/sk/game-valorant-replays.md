---
title: "VALORANT (replaye)"
nav_order: 45
lang: "sk"
source: game-valorant-replays.md
source_hash: "10a648aabdf1"
nav_exclude: true
search_exclude: true
---
# VALORANT (replaye) {#valorant-replays}

Po zápase VALORANT watcher prevedie replay, ktorý hra uložila, do súborov, ktoré si môžete pozrieť ako štatistiky a časovú os.

*Technické údaje: adaptér `valorant-replays`, typ [`replay`](sources-and-rules.md); beží stále (nečaká, kým sa spustí hra) a hľadá nové dáta každých 5 s.*

## Čo sa zaznamenáva {#what-is-recorded}

- mapa, ID zápasu a vybraní agenti; informačný blok replaye (dĺžka, verzie, názov, čas nahrávania, príznaky kompresie a šifrovania)
- časová os udalostí servera: zabitia (vrah a obeť ako ID v sieti), začiatky kôl, položené spike, zneškodnené a vybuchnuté spike, použité ultimáty, prehadzovanie strán - každé s ID a metadátami
- každý blok súboru celý v heat.raw.parquet; nedekódované: polohy, mená ani skóre - tie sú v zamaskovanom prúde

## Odkiaľ to berie {#where-it-comes-from}

replaye, ktoré ukladá VALORANT: %LOCALAPPDATA%/VALORANT/Saved/Demos/\*.vrf (len časti, ktoré nie sú zamaskované)

## Ako to zapnúť {#how-to-switch-it-on}

uložte replay vo VALORANT (kariéra > zápas > stiahnuť replay)

## Ako to funguje {#how-it-works}

Replaye League of Legends a VALORANT: čo sa z nich dá prečítať tak, ako sú.

Obe hry ukladajú replaye na disk hráča a obe chránia to, čo je vo vnútri: dáta hry od okamihu k okamihu sú zamaskované a pri každej záplate inak, aby sa nedali použiť na podvádzanie. Táto časť sa nikde v 3DHeat nedekóduje. Čo každý súbor nesie otvorene, sa načíta, a zvyšok sa uchová tak, ako je: každá časť súboru celá v `heat.raw.parquet` relácie (pravidlo konvertorov 3DHeat, docs/converters.md v repozitári prehliadača), počítaná v `selfCheck.completeness` v meta.json.

#### Valorant (.vrf) {#valorant-vrf}

`%LOCALAPPDATA%\VALORANT\Saved\Demos\*.vrf`, lokálny replay Unreal Engine (rozloženie podľa vrfkit, Apache-2.0, a ValorantReplayParser, MIT). Otvorene: informačný blok replaye (dĺžka, verzia siete, changelist, jeho názov, kedy bol nahraný, či je komprimovaný alebo zašifrovaný), mapa, ID zápasu a vybraní agenti (v hlavičke) a časová os udalostí, ktorú zapisuje server - zabitia (vrah a obeť ako ID v sieti, nie mená), začiatky kôl, položené spike, zneškodnené a vybuchnuté spike, použité ultimáty, prehadzovanie strán - každá s časom, ID a metadátami. Polohy, mená, skóre a všetko ostatné sú v zamaskovanom prúde (bloky replaye a kontrolné body), ktorý je uchovaný celý a nečítaný.

Ten istý modul slúži aj: [League of Legends (replaye)](game-lol-replays.md).

## Polohy a osi {#positions-and-axes}

| | |
|---|---|
| Zaznamenané polohy | nie |
| Osa nahor | `z` |
| Jednotky | svetové jednotky VALORANT |
| Zrkadlenie pre prehliadač | žiadne |
| Mierka jednotiek (`scale`: prehliadač ňou násobí polohy) | 1 |

Tieto hodnoty idú do `meta.json` každej relácie (`axes`) a, keď relácia obsahuje polohy, do päty `heat.parquet`, takže 3DHeat prehliadač ich otáča a škáluje sám - pozrite [Dáta](the-data.md).

## Multiplayer {#multiplayer}

- Označené ako hrané online (`multiplayer`): **áno**. `games --markdown` to zobrazí ako „povolené (číta len to, čo hra zverejňuje)".
- Druh `replay`: číta len to, čo hra alebo platforma sprístupňuje (replaye a dema, ktoré hra uloží), takže zaznamenáva aj v online hre, nielen offline; príznak rozhoduje len o tom, či sa pamäť smie vôbec čítať.
- Pamäť: adaptér ju **nikdy** nečíta. Pamäť čítajú len adaptéry typu `memory` a nikdy pre hru označenú ako hranú online - pozrite [Zdroje a pravidlá](sources-and-rules.md).

## Zaznamenané štatistiky {#statistics-recorded}

Kľúče štatistík, ktoré kód tohto adaptéra nastavuje podľa mena (`stats` každej relácie v `meta.json` a tabuľka `stats` v `watcher.sqlite`):

`kills_in_match`, `map`, `match_seconds`, `rounds`, `spikes_planted`

Kľúč v zložených zátvorkách sa dopĺňa za behu (`score.{team}` je jeden kľúč pre každý tím). Kľúče, ktoré kód berie z tabuľky polí hry alebo z jej vlastných názvov štatistík, v tomto zozname nie sú; čo sa zaznamenáva, uvádza vyššie časť „Čo sa zaznamenáva".

## Úplnosť {#completeness}

Watcher sa riadi pravidlom konvertorov 3DHeat ([pravidlo konvertorov](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md)): čo zdroj obsahuje, sa načíta alebo uchová, nikdy sa nezahodí. Okrem riadkov sa každý paket, stránka, riadok alebo odpoveď, ktorú adaptér dostane, uchová celá v `heat.raw.parquet` relácie (stĺpce `time`, `ms`, `type`, `used`, `payload`, `text` a ďalšie polia uchované podľa mena; `used` označuje, čo sa stalo aj riadkami), a `selfCheck.completeness` v `meta.json` počíta každý `type` - `lost` je 0.

**Načítané**

- informačný blok, každé pole (meta.json `vrf`): verzia súboru, vlastné verzie, dĺžka, verzia siete, changelist, názov, príznak živého, čas nahrávania, príznaky komprimovaného a zašifrovaného, kľúč tak, ako je uložený
- blok hlavičky: mapa, ID zápasu a vybraní agenti (podľa ich tvaru)
- každý blok udalostí: ID, skupina, metadáta, čas začiatku a konca, a z jeho dát názov udalosti, čas v sekundách a čísla pred ním (ID v sieti vraha a obete) - každý ako riadok

**Uchované surové**

- každý blok celý, v poradí v súbore (`offset`), takže časti sú súbor: `info`, `header`, `event <group>`, `replay_data`, `checkpoint`, `chunk <n>` pre typ, ktorý rozloženie nepomenúva, `trailing` pre bajty za posledným celým blokom

**Nie je k dispozícii**

- polohy, mená, skóre, schopnosti, každý rámec hry: bloky dát replaye a kontrolné body sú zamaskované. Uchované celé, nečítané
- obsah zašifrovaného replaye: prejdený a uchovaný celý, vnútri nič nečítané

**Veľkosť**: surový sprievodný súbor má približne veľkosť samotného replaye: zamaskovaný prúd sa nedá skomprimovať

## Overené {#verified}

zostavené podľa rozloženia kontajnera zdokumentovaného vrfkit (Apache-2.0); nevyskúšané na skutočnom replayi, žiadny nebol k dispozícii - pred čítaním kontroluje a preskočí, čo sa nezhoduje

## Zdroj {#source}

[heat3d_watch/adapters/riot_replays.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/riot_replays.py)

<!-- Generated from the adapter by tools/gen_game_pages.py; change the adapter and run it again rather than editing this page. -->
