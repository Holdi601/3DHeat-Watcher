---
title: "RaceRoom Racing Experience (živé dáta)"
nav_order: 38
lang: "sk"
source: game-raceroom.md
source_hash: "ffd0499ca059"
nav_exclude: true
search_exclude: true
---
# RaceRoom Racing Experience (živé dáta) {#raceroom-racing-experience-live-data}

Počas hry RaceRoom Racing Experience watcher ukladá dáta, ktoré samotná hra posiela von, aby ste ich neskôr mohli pozrieť na mape v 3DHeat prehliadači.

*Technické údaje: adaptér `raceroom`, typ [`telemetry`](sources-and-rules.md); beží, kým beží `RRRE64.exe` alebo `RRRE.exe`, a hľadá nové dáta každých 0,1 s.*

## Čo sa zaznamenáva {#what-is-recorded}

- poloha každého auta (svetové XYZ, m) 10-krát za sekundu podľa mena vodiča, vlastné auto označené, s rýchlosťou a pozíciou v pretekoch; vlastný rýchlostný stupeň, plyn, brzda
- začiatok relácie s traťou, ktorú hra uvádza; kolá podľa auta s časom kola; dojazdy; vlastné zastávky v boxoch
- teleporty (späť do boxov, reštart): `teleport`, kde auto bolo, `spawn`, kde je teraz
- vlastné kolá, najlepšie kolo, pozícia v pretekoch, vzdialenosť, najvyššia rýchlosť
- celá zdieľaná pamäť hry v `heat.raw.parquet` pri každej zmene
- vlastné body za incidenty

## Odkiaľ to berie {#where-it-comes-from}

zdieľaná pamäť $R3E (r3e.h verzie 3 od Sector3)

## Ako to zapnúť {#how-to-switch-it-on}

Nič netreba zapínať: watcher číta zdroj tak, ako ho hra alebo platforma poskytuje.

## Ako to funguje {#how-it-works}

Zdieľaná pamäť, ktorú závodné simulácie zverejňujú pre palubné displeje, otvorená len na čítanie – a nikdy sa nevytvára.

Viaceré simulácie sprístupňujú svoju telemetriu ako pomenované mapovanie súboru vo Windows, ktoré hra vytvára a ktoré môže čítať ktokoľvek: stránky Kunosu `Local\acpmf_*` (Assetto Corsa, ACC, AC Rally, `Local\acevo_pmf_*` pre AC EVO), `Local\IRSDKMemMapFileName` pre iRacing, `$R3E` pre RaceRoom, `$pcars2$` pre Automobilista 2 / Project CARS 2.

Prečo nie `mmap.mmap(-1, size, tagname=...)`, čo je v Pythone obvyklý spôsob: ak mapovanie ešte neexistuje, *vytvorí* ho – tu iba na čítanie. Hra spustená potom otvorí mapovanie watchera namiesto svojho a nemôže doň zapisovať, takže jej telemetria je mŕtva, kým watcher neuvoľní. Watcher spustí adaptér hneď, ako sa objaví proces hry, a presne vtedy hra ešte nevytvorila svoje mapovanie. Preto toto otvára `OpenFileMappingW`, ktoré nájde len existujúce mapovanie, namapuje ho s `FILE_MAP_READ` a inak nahlási „ešte tam nie je“; adaptéry to skúsia znova o chvíľu.

Nič tu nemôže zapisovať: pohľad je namapovaný len na čítanie a kopíruje sa z neho len cez `ctypes.string_at`.

Dve hry sa tu čítajú aj takto; každé auto na trati je v ich stránkach.

#### RaceRoom Racing Experience - `$R3E` {#raceroom-racing-experience---r3e}

Sector3 `r3e.h` (github.com/sector3studios/r3e-api, sample-c/src/r3e.h, verzia 3.6), `#pragma pack(1)`. Hlavička hovorí, kde začínajú vodiči a aká je veľká jedna položka (`all_drivers_offset`, `driver_data_size`), takže časť pre každého vodiča – meno, slot, pozícia, svetová poloha (float x y z, m), dokončené kolá, aktuálny čas kola, stav dojazdu, boxová ulička, rýchlosť – sa číta podľa nich. Vlastné polia hráča (najlepšie a predchádzajúce kolo, pozícia v pretekoch, body za incidenty, rýchlostný stupeň, pedále, názvy trate a variantu) sa čítajú na posunoch verzie 3.6, len keď je `all_drivers_offset` na hodnote 2008, na ktorú ho to rozloženie kladie. Y sa berie ako nahor; hlavička to nehovorí.

Rovnaký modul slúži aj: [Automobilista 2 (živé dáta)](game-automobilista-2.md), [Project CARS 2 (živé dáta)](game-project-cars-2.md).

## Polohy a osi {#positions-and-axes}

| | |
|---|---|
| Zaznamenané polohy | áno |
| Os nahor | `y` |
| Jednotky | metre; predpokladá sa Y nahor (r3e.h to nehovorí) |
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

- za každý slot vodiča (podľa vlastného posunu a veľkosti hlavičky): meno, slot, stav dojazdu, pozícia, svetová poloha, dokončené kolá, aktuálny čas kola, boxová ulička, rýchlosť
- vlastné polia hráča, len keď je stránka rozložením r3e.h 3.6: názvy trate a variantu, typ relácie, pozícia v pretekoch, najlepšie a predchádzajúce kolo, body za incidenty, rýchlostný stupeň, plyn, brzda, slot hráča
- posuny odvodené z r3e.h 3.6 od Sector3 a overené na stránke zostavenej z neho v testoch; zatiaľ nie proti hre

**Uchované surové**

- `r3e`: celé mapovanie $R3E, pri každom čítaní, ktorého bajty sa líšia od kópie uchovanej naposledy – každé pole r3e.h: fyzika hráča (orientácia, rýchlosti, zrýchlenia, G-sily), motor, palivo, pneumatiky, brzdy, poškodenie, príznaky, ponuka pitstopu, časy sektorov, celé údaje o vodičovi pre každý slot vodiča (trieda, model, tím, časy sektorov, odstupy, tresty, pneumatiky)
- `used` je pravda pre stránku prečítanú do riadkov; nepravda pre stránku v menu, pri pauze, v replayi, iného rozloženia alebo zachytenú uprostred zápisu (`torn` 1); `unchanged_reads` v meta.json počíta čítania, ktoré boli bajt po bajte rovnaké ako kópia uchovaná predtým

**Nedostupné**

- vstupy a fyzika iných vodičov: stránka dáva len vlastné auto hráča
- presné časy kôl iných áut: slot má len svoj bežiaci čas kola, takže kolo je posledný zaznamenaný bežiaci čas (na asi 0,1 s)
- vlastné polia hráča na inom rozložení než 3.6: uchované surovo, nečítané, kým sa neoverí

**Veľkosť**: stránka má 44 KB (r3e.h 3.6; mapovanie sa zaokrúhli na celé 4 KB stránky), až 10-krát za sekundu počas jazdy: približne 1,6 GB za hodinu pred kompresiou; prázdne sloty vodičov a nemenné polia sa zstd veľmi dobre zmenšia (na skutočnej relácii ešte nezmerané)

## Overené {#verified}

testované na stránke zostavenej v teste z r3e.h 3.6 (posuny odvodené z oficiálnej hlavičky); neotestované proti hre; časy kôl iných áut sú posledný zaznamenaný bežiaci čas kola (na asi 0,1 s)

## Zdroj {#source}

[heat3d_watch/adapters/simracing_shm.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/simracing_shm.py)

<!-- Generované z adaptéra nástrojom tools/gen_game_pages.py; zmeňte adaptér a spustite to znova, namiesto úpravy tejto stránky. -->
