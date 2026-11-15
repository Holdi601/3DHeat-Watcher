---
title: "Path of Exile (logy)"
nav_order: 36
lang: "sk"
source: game-poe.md
source_hash: "9facfd5a1551"
nav_exclude: true
search_exclude: true
---
# Path of Exile (logy) {#path-of-exile-log-files}

Počas hry Path of Exile watcher číta súbory, ktoré hra zapisuje, a ukladá, čo sa stalo, aby ste sa na to neskôr mohli pozrieť ako na štatistiky a časovú os.

*Technické údaje: adaptér `poe`, typ [`log`](sources-and-rules.md); beží, kým beží `PathOfExile.exe`, `PathOfExile_x64.exe`, `PathOfExileSteam.exe`, `PathOfExile_x64Steam.exe`, `PathOfExileEGS.exe`, `PathOfExile_x64EGS.exe`, `PathOfExile_KG.exe` alebo `PathOfExile_x64_KG.exe`, a hľadá nové dáta každých 0,5 s.*

## Čo sa zaznamenáva {#what-is-recorded}

- vstupy do zón s úrovňou oblasti, ID oblasti a jej seed
- zvýšenia úrovne s povolaním a úrovňou
- smrti („has been slain“)
- hráči, ktorí vstúpia do oblasti a odídu z nej, šepty dnu a von, žiadosti o obchod, prijaté obchody
- každý riadok Client.txt tejto relácie celý v heat.raw.parquet
- smrti, získané úrovne, najvyššia úroveň, navštívené zóny, rôzne zóny, šepty, žiadosti o obchod, obchody

## Odkiaľ to berie {#where-it-comes-from}

&lt;inštalácia>\logs\Client.txt Path of Exile alebo Path of Exile 2 (sleduje sa; priečinok inštalácie je priečinok spusteného programu)

## Ako to zapnúť {#how-to-switch-it-on}

Nič netreba zapínať: watcher číta zdroj tak, ako ho hra alebo platforma poskytuje.

## Ako to funguje {#how-it-works}

Path of Exile a Path of Exile 2: log klienta, `<inštalácia>\logs\Client.txt`.

Obe hry pripisujú do jedného Client.txt vo svojom priečinku inštalácie, pokiaľ sú nainštalované (rastie cez spustenia). Riadky vyzerajú takto

```text
2024/01/01 12:00:00 123456789 cff94598 [INFO Client 1234] : You have entered Lioneye's Watch.
2024/01/01 12:00:00 123456789 cff94598 [DEBUG Client 1234] Generating level 2 area "1_1_2" with seed 1
2024/01/01 12:00:00 123456789 cff94598 [INFO Client 1234] : Name (Witch) is now level 2
2024/01/01 12:00:00 123456789 cff94598 [INFO Client 1234] : Name has been slain.
2024/01/01 12:00:00 123456789 cff94598 [INFO Client 1234] @From Name: Hi, I would like to buy your ...
```

- miestny čas, počítadlo milisekúnd, hash, úroveň a vlákno, potom to, čo ukazuje okno chatu. Správy sú z anglického klienta; klient v inom jazyku ich zapisuje preložené a tu sa nerozpoznajú. Nič nedáva polohu. Formát nezdokumentovala Grinding Gear Games; je to obyčajný textový log hry, ktorý čítajú komunitné nástroje (obchodní pomocníci, sprievodcovia úrovňami) už roky – napr. <https://github.com/klayveR/poe-log-monitor> (MIT) pre zoznam udalostí.

Priečinok inštalácie je priečinok spusteného programu; bez neho sa prehľadajú knižnice Steamu a predvolený priečinok samostatného klienta.

Každý riadok tejto relácie sa uchová celý v surovom sprievodnom súbore relácie (pravidlo konvertorov 3DHeat), bez ohľadu na to, či tu niečo znamená: `type` je úroveň a logger v jej zátvorkách (`INFO Client`, `DEBUG Client`, `WARN Client`, ...), riadok s časovou značkou bez zátvoriek je `untagged`, riadok bez časovej značky `untimed`.

## Polohy a osi {#positions-and-axes}

| | |
|---|---|
| Zaznamenané polohy | nie |
| Os nahor | `y` |
| Jednotky | polohy sa nezaznamenávajú |
| Zrkadlenie pre prehliadač | žiadne |
| Mierka jednotiek (`scale`: prehliadač polohy touto hodnotou násobí) | 1 |

Tieto údaje idú do `meta.json` každej relácie (`axes`) a, ak má relácia polohy, do päty súboru `heat.parquet`, takže 3DHeat prehliadač si riadky sám otočí a zmení ich mierku – pozrite [Dáta](the-data.md).

## Viachráčová hra {#multiplayer}

- Označené ako hrané online (`multiplayer`): **áno**. `games --markdown` to zobrazí ako „povolené (číta len to, čo hra zverejňuje)“.
- Typ `log`: číta len to, čo hra alebo platforma vydáva (súbory, ktoré hra zapisuje počas behu), takže zaznamenáva aj v online hre, nielen offline; príznak rozhoduje len o tom, či sa pamäť smie čítať.
- Pamäť: adaptér ju **nikdy** nečíta. Pamäť čítajú len adaptéry typu `memory` a nikdy pre hru označenú ako hranú online – pozrite [Zdroje a pravidlá](sources-and-rules.md).

## Zaznamenané štatistiky {#statistics-recorded}

Kľúče štatistík, ktoré kód tohto adaptéra nastavuje podľa mena (štatistiky každej relácie `stats` v `meta.json` a tabuľka `stats` v `watcher.sqlite`):

`bad_lines`, `character_class`, `deaths`, `level`, `levels_gained`, `trade_requests_received`, `trade_requests_sent`, `trades`, `whispers`, `zones_distinct`, `zones_entered`

Kľúč v zložených zátvorkách sa dopĺňa za behu (`score.{team}` je jeden kľúč na tím). Kľúče, ktoré kód berie z tabuľky polí hry alebo z názvov štatistík hry, v tomto zozname nie sú; „Čo sa zaznamenáva“ vyššie ich pomenúva.

## Úplnosť {#completeness}

Watcher sa riadi [pravidlom konvertorov](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md) 3DHeat: to, čo zdroj obsahuje, sa číta alebo uchováva, nikdy sa nezahadzuje. Okrem riadkov sa každý paket, stránka, riadok alebo odpoveď, ktorú adaptér dostane, uchová celá v `heat.raw.parquet` relácie (stĺpce `time`, `ms`, `type`, `used`, `payload`, `text` a ďalšie polia, ktoré sa uchovávajú podľa mena; `used` označuje to, čo sa stalo aj riadkami), a `selfCheck.completeness` v `meta.json` počíta každý `type` – `lost` je 0.

**Čítané**

- `You have entered <zóna>`, s úrovňou oblasti, ID oblasti a seedom z riadku `Generating level` pred ním
- `<meno> (<povolanie>) is now level <n>`, `<meno> has been slain`, hráči, ktorí vstupujú do oblasti a odchádzajú z nej, šepty dnu a von (s tým, či ide o žiadosť o obchod), prijaté a zrušené obchody

**Uchované surové**

- každý riadok tejto relácie celý, `type` = úroveň a logger v jej zátvorkách (`INFO Client`, `DEBUG Client`, `WARN Client`, `CRIT Client`, ...), `used` tam, kde sa stal riadkom: globálny, obchodný, skupinový a cechový chat, `Connecting to instance server`, oznámenia AFK a DND, odpovede na chatové príkazy ako `/played` a `/deaths`, riadky načítania a motora klienta – uchované, zatiaľ nie premenené na riadky
- riadok s časovou značkou bez zátvoriek (`***** LOG FILE OPENING *****`) ako `untagged`, riadok bez časovej značky ako `untimed`

**Nedostupné**

- polohy: nič v logu nijakú nedáva
- čo píše klient v inom jazyku: riadky sa uchovajú, ale na riadky sa premieňajú len anglické správy
- riadky skorších spustení: Client.txt rastie cez spustenia; riadky s časom zapísaným pred týmto spustením hry sa nechávajú (uchovali sa, keď sa hralo)
- zabitia, poškodenie, koristi a pasívny strom: hra ich nezapisuje

**Veľkosť**: Client.txt rastie zhruba 0,3 až 3 MB za hodinu (najviac z riadkov DEBUG pri načítaní oblastí, viac pri rušnom obchodnom chate); zstd v heat.raw.parquet ho zmenší zhruba na desatinu

## Overené {#verified}

testované na syntetických riadkoch Client.txt v hernom formáte; neotestované proti hre

## Zdroj {#source}

[heat3d_watch/adapters/poe.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/poe.py)

<!-- Generované z adaptéra nástrojom tools/gen_game_pages.py; zmeňte adaptér a spustite to znova, namiesto úpravy tejto stránky. -->
