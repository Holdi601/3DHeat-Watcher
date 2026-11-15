---
title: "Project CARS 2 (živé dáta)"
nav_order: 37
lang: "sk"
source: game-project-cars-2.md
source_hash: "a1990b93b7d1"
nav_exclude: true
search_exclude: true
---
# Project CARS 2 (živé dáta) {#project-cars-2-live-data}

Počas hry Project CARS 2 watcher ukladá dáta, ktoré samotná hra posiela von, aby ste ich neskôr mohli pozrieť na mape v 3DHeat prehliadači.

*Technické údaje: adaptér `project-cars-2`, typ [`telemetry`](sources-and-rules.md); beží, kým beží `pCARS2AVX.exe` alebo `pCARS2.exe`, a hľadá nové dáta každých 0,1 s.*

## Čo sa zaznamenáva {#what-is-recorded}

- poloha každého auta (svetové XYZ, m) 10-krát za sekundu podľa mena vodiča, vlastné auto označené, s rýchlosťou a pozíciou v pretekoch; vlastný rýchlostný stupeň, plyn, brzda
- začiatok relácie s traťou, ktorú hra uvádza; kolá podľa auta s časom kola; dojazdy; vlastné zastávky v boxoch
- teleporty (späť do boxov, reštart): `teleport`, kde auto bolo, `spawn`, kde je teraz
- vlastné kolá, najlepšie kolo, pozícia v pretekoch, vzdialenosť, najvyššia rýchlosť
- celá zdieľaná pamäť hry v `heat.raw.parquet` pri každej zmene

## Odkiaľ to berie {#where-it-comes-from}

zdieľaná pamäť $pcars2$ (SMS SharedMemory.h)

## Ako to zapnúť {#how-to-switch-it-on}

V hre: Options > System > Shared Memory: „Project CARS 2“

## Ako to funguje {#how-it-works}

Zdieľaná pamäť, ktorú závodné simulácie zverejňujú pre palubné displeje, otvorená len na čítanie – a nikdy sa nevytvára.

Viaceré simulácie sprístupňujú svoju telemetriu ako pomenované mapovanie súboru vo Windows, ktoré hra vytvára a ktoré môže čítať ktokoľvek: stránky Kunosu `Local\acpmf_*` (Assetto Corsa, ACC, AC Rally, `Local\acevo_pmf_*` pre AC EVO), `Local\IRSDKMemMapFileName` pre iRacing, `$R3E` pre RaceRoom, `$pcars2$` pre Automobilista 2 / Project CARS 2.

Prečo nie `mmap.mmap(-1, size, tagname=...)`, čo je v Pythone obvyklý spôsob: ak mapovanie ešte neexistuje, *vytvorí* ho – tu iba na čítanie. Hra spustená potom otvorí mapovanie watchera namiesto svojho a nemôže doň zapisovať, takže jej telemetria je mŕtva, kým watcher neuvoľní. Watcher spustí adaptér hneď, ako sa objaví proces hry, a presne vtedy hra ešte nevytvorila svoje mapovanie. Preto toto otvára `OpenFileMappingW`, ktoré nájde len existujúce mapovanie, namapuje ho s `FILE_MAP_READ` a inak nahlási „ešte tam nie je“; adaptéry to skúsia znova o chvíľu.

Nič tu nemôže zapisovať: pohľad je namapovaný len na čítanie a kopíruje sa z neho len cez `ctypes.string_at`.

Dve hry sa tu čítajú aj takto; každé auto na trati je v ich stránkach.

#### Automobilista 2 / Project CARS 2 - `$pcars2$` {#automobilista-2--project-cars-2---pcars2}

SMS `SharedMemory.h` (dodáva sa v priečinku Support\SharedMemory hry; AMS2: Options > System > Shared Memory „Project CARS 2“), `#pragma pack(4)`. `mParticipantInfo[64]` od bajtu 28, po 100 bajtoch: mIsActive, mName[64], mWorldPosition[3] (m, y nahor), mCurrentLapDistance, mRacePosition, mLapsCompleted, mCurrentLap, mCurrentSector; mViewedParticipantIndex (20) je auto hráča; pre každého účastníka mLastLapTimes (9200), mRaceStates (9520), mSpeeds (10800); hráčov mBestLapTime (6716), mLastLapTime (6720), mSpeed (6848), mBrake, mThrottle, mGear; mSequenceNumber (7320) je nepárne, kým hra zapisuje. Posuny sa odvodili z dvoch nezávislých kópií hlavičky (vlastná kópia hry tu nie je nainštalovaná), ktoré sa zhodujú.

Obe stránky sa navyše uchovajú celé (docs/converters.md, „Live sources“): celé mapovanie, pri každom čítaní, ktorého bajty sa líšia od kópie uchovanej naposledy, v surovom sprievodnom súbore relácie pod `type` `r3e` alebo `pcars2` – každý slot vodiča a každé pole štruktúry, aj tie, ktoré sa tu nečítajú, takže neskorší dekodér potrebuje len sprievodný súbor.

Rovnaký modul slúži aj: [Automobilista 2 (živé dáta)](game-automobilista-2.md), [RaceRoom Racing Experience (živé dáta)](game-raceroom.md).

## Polohy a osi {#positions-and-axes}

| | |
|---|---|
| Zaznamenané polohy | áno |
| Os nahor | `y` |
| Jednotky | metre |
| Zrkadlenie pre prehliadač | žiadne |
| Mierka jednotiek (`scale`: prehliadač polohy touto hodnotou násobí) | 1 |

Tieto údaje idú do `meta.json` každej relácie (`axes`) a, ak má relácia polohy, do päty súboru `heat.parquet`, takže 3DHeat prehliadač si riadky sám otočí a zmení ich mierku – pozrite [Dáta](the-data.md).

## Viachráčová hra {#multiplayer}

- Označené ako hrané online (`multiplayer`): **áno**. `games --markdown` to zobrazí ako „povolené (číta len to, čo hra zverejňuje)“.
- Typ `telemetry`: číta len to, čo hra alebo platforma vydáva (UDP port alebo zdieľaná pamäť, ktorú hra zverejňuje), takže zaznamenáva aj v online hre, nielen offline; príznak rozhoduje len o tom, či sa pamäť smie čítať.
- Pamäť: adaptér ju **nikdy** nečíta. Pamäť čítajú len adaptéry typu `memory` a nikdy pre hru označenú ako hranú online – pozrite [Zdroje a pravidlá](sources-and-rules.md).

## Zaznamenané štatistiky {#statistics-recorded}

Kľúče štatistík, ktoré kód tohto adaptéra nastavuje podľa mena (štatistiky každej relácie `stats` v `meta.json` a tabuľka `stats` v `watcher.sqlite`):

`best_lap`, `distance_km`, `finishes`, `incidents`, `laps`, `pit_stops`, `race_position`, `top_speed_kmh`

Kľúč v zložených zátvorkách sa dopĺňa za behu (`score.{team}` je jeden kľúč na tím). Kľúče, ktoré kód berie z tabuľky polí hry alebo z názvov štatistík hry, v tomto zozname nie sú; „Čo sa zaznamenáva“ vyššie ich pomenúva.

## Úplnosť {#completeness}

Watcher sa riadi [pravidlom konvertorov](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md) 3DHeat: to, čo zdroj obsahuje, sa číta alebo uchováva, nikdy sa nezahadzuje. Okrem riadkov sa každý paket, stránka, riadok alebo odpoveď, ktorú adaptér dostane, uchová celá v `heat.raw.parquet` relácie (stĺpce `time`, `ms`, `type`, `used`, `payload`, `text` a ďalšie polia, ktoré sa uchovávajú podľa mena; `used` označuje to, čo sa stalo aj riadkami), a `selfCheck.completeness` v `meta.json` počíta každý `type` – `lost` je 0.

**Čítané**

- za každého účastníka (až 64): aktívny, meno, svetová poloha, pozícia v pretekoch, dokončené kolá; jeho posledný čas kola, stav pretekov a rýchlosť
- auto hráča (mViewedParticipantIndex), stav hry a relácie, poloha a variant trate, najlepšie a posledné kolo, rýchlosť, brzda, plyn, rýchlostný stupeň; mSequenceNumber na preskočenie kópie zachytenej uprostred zápisu
- posuny z dvoch nezávislých kópií SMS SharedMemory.h, ktoré sa zhodujú, overené na stránke zostavenej z nich v testoch; zatiaľ nie proti hre

**Uchované surové**

- `pcars2`: celé mapovanie $pcars2$ – štruktúra presahuje 11 312 bajtov, ktoré sa tu čítajú – pri každom čítaní, ktorého bajty sa líšia od kópie uchovanej naposledy: orientácia každého účastníka, časy sektorov, názvy áut a tried, režimy a príznaky boxov, fyzika hráča, pneumatiky, odpruženie, poškodenie, počasie a všetko, čo neskoršie verzie Project CARS 2 pripojili
- `used` je pravda pre stránku prečítanú do riadkov; nepravda pre stránku v menu, pri pauze, v replayi, iného rozloženia alebo zachytenú uprostred zápisu (`torn` 1); `unchanged_reads` v meta.json počíta čítania, ktoré boli bajt po bajte rovnaké ako kópia uchovaná predtým

**Nedostupné**

- vstupy a fyzika iných účastníkov: stránka dáva len sledované auto
- všetko, kým je v hre vypnutá možnosť zdieľanej pamäte (Project CARS 2 vtedy nič nezapisuje)

**Veľkosť**: mapovanie má približne 20 až 30 KB (podľa verzie hry), až 10-krát za sekundu počas jazdy: zhruba 0,7 až 1,1 GB za hodinu pred kompresiou; zstd zmenší prázdne sloty účastníkov a nemenné mená na zlomok (na skutočnej relácii ešte nezmerané)

## Overené {#verified}

testované na stránke zostavenej v teste; posuny z dvoch nezávislých kópií SharedMemory.h, ktoré sa zhodujú, nie z kópie, ktorú dodáva hra; neotestované proti hre

## Zdroj {#source}

[heat3d_watch/adapters/simracing_shm.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/simracing_shm.py)

<!-- Generované z adaptéra nástrojom tools/gen_game_pages.py; zmeňte adaptér a spustite to znova, namiesto úpravy tejto stránky. -->
