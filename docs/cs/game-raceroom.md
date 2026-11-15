---
title: "RaceRoom Racing Experience (živá data)"
nav_order: 38
lang: "cs"
source: game-raceroom.md
source_hash: "ffd0499ca059"
nav_exclude: true
search_exclude: true
---
# RaceRoom Racing Experience (živá data) {#raceroom-racing-experience-live-data}

Když hrajete RaceRoom Racing Experience, Watcher uloží data, která hra sama posílá ven, abyste se na ně mohli později podívat na mapě v prohlížeči 3DHeat.

*Technické podrobnosti: adaptér `raceroom`, druh [`telemetry`](sources-and-rules.md); běží, dokud běží `RRRE64.exe` nebo `RRRE.exe`, a hledá nová data každých 0,1 s.*

## Co se zaznamenává {#what-is-recorded}

- pozice každého auta (světové XYZ, m) 10krát za sekundu, podle jména řidiče, vlastní auto označeno, s rychlostí a pozicí v závodě; vlastní rychlostní stupeň, plyn, brzda
- začátek relace s tratí, jak ji hra pojmenovala; kola každého auta s časem kola; dojezdy; vlastní zastávky v boxech
- teleporty (návrat do boxů, restart): `teleport`, kde auto bylo, `spawn`, kde je nyní
- vlastní kola, nejlepší kolo, pozice v závodě, vzdálenost, nejvyšší rychlost
- celá sdílená paměť hry v `heat.raw.parquet`, při každé změně
- vlastní body za incidenty

## Odkud to pochází {#where-it-comes-from}

sdílená paměť $R3E (r3e.h od Sector3, verze 3)

## Jak to zapnout {#how-to-switch-it-on}

Nic se nemusí zapínat: Watcher čte zdroj tak, jak ho hra nebo platforma poskytuje.

## Jak to funguje {#how-it-works}

Sdílená paměť, kterou závodní simulátory zveřejňují pro palubní desky, otevřená jen ke čtení - a
nikdy nevytvořená.

Několik simulátorů vydává svou telemetrii jako pojmenované mapování souboru ve Windows, které hra
vytvoří a které může číst kdokoli: stránky Kunosu `Local\acpmf_*` (Assetto Corsa,
ACC, AC Rally, AC EVO `Local\acevo_pmf_*`), `Local\IRSDKMemMapFileName` od iRacingu,
`$R3E` od RaceRoomu, `$pcars2$` od Automobilisty 2 / Project CARS 2.

Proč ne `mmap.mmap(-1, size, tagname=...)`, obvyklý způsob v Pythonu: když mapování
ještě neexistuje, *vytvoří* ho - zde jen ke čtení. Hra spuštěná potom
otevře mapování Watcheru místo svého vlastního a pak do něj nemůže zapisovat, takže její
telemetrie je mrtvá, dokud Watcher nepustí. Watcher spustí adaptér hned,
jakmile se objeví proces hry, a přesně v tu chvíli hra ještě nevytvořila své mapování.
Proto toto otevírá `OpenFileMappingW`, které najde jen existující mapování,
namapuje ho s `FILE_MAP_READ` a jinak hlásí „zatím tu není“; adaptéry to zkusí
znovu o chvíli později.

Nic zde nemůže zapisovat: pohled je namapován jen ke čtení a z něj se kopíruje
jen pomocí `ctypes.string_at`.

Dvě hry se čtou i zde; každé auto na trati je na jejich stránkách.

#### RaceRoom Racing Experience - `$R3E` {#raceroom-racing-experience---r3e}

Sector3 `r3e.h` (github.com/sector3studios/r3e-api, sample-c/src/r3e.h,
verze 3.6), `#pragma pack(1)`. Hlavička říká, kde začínají řidiči a jak velký je jeden
(`all_drivers_offset`, `driver_data_size`), takže část pro každého řidiče - jméno, slot,
místo, světová pozice (float x y z, m), dokončená kola, aktuální čas kola, stav
dojezdu, pozice v boxech, rychlost - se čte podle nich. Vlastní pole hráče (nejlepší
a předchozí kolo, pozice v závodě, body za incidenty, rychlostní stupeň, pedály, názvy
tratě a varianty) se čtou na svých offsetech 3.6, jen když je `all_drivers_offset` na
hodnotě 2008, na které ho tento layout umisťuje. Y se bere jako nahoru; hlavička to neříká.

Stejný modul slouží také: [Automobilista 2 (živá data)](game-automobilista-2.md), [Project CARS 2 (živá data)](game-project-cars-2.md).

## Pozice a osy {#positions-and-axes}

| | |
|---|---|
| Zaznamenané pozice | ano |
| Osa nahoru | `y` |
| Jednotky | metry; předpokládá se Y nahoru (r3e.h to neříká) |
| Zrcadleno pro prohlížeč | žádné |
| Měřítko jednotek (`scale`: prohlížeč pozice tímto násobí) | 1 |

Tyto hodnoty se zapíší do `meta.json` (`axes`) každé relace a, pokud relace obsahuje pozice, do zápatí `heat.parquet`, takže prohlížeč 3DHeat otáčí a měřítko řádků upravuje sám - viz [Data](the-data.md).

## Více hráčů {#multiplayer}

- Označeno jako hraná online (`multiplayer`): **ano**. `games --markdown` to ukazuje jako „povoleno (čte jen to, co hra zveřejňuje)“.
- Druh `telemetry`: čte jen to, co hra nebo platforma vydává (UDP port nebo sdílená paměť, kterou hra zveřejňuje), takže zaznamenává i v online hře i offline; příznak rozhoduje jen o tom, zda se paměť smí vůbec číst.
- Paměť: tento adaptér ji **nikdy** nečte. Paměť čtou jen adaptéry `memory`, a nikdy u hry označené jako hraná online - viz [Zdroje a pravidla](sources-and-rules.md).

## Zaznamenané statistiky {#statistics-recorded}

Klíče statistik, které kód tohoto adaptéru nastavuje podle názvu (`stats` každé relace v `meta.json` a tabulka `stats` v `watcher.sqlite`):

`best_lap`, `distance_km`, `finishes`, `incidents`, `laps`, `pit_stops`, `race_position`, `top_speed_kmh`

Klíč ve složených závorkách se doplní za běhu (`score.{team}` je jeden klíč pro každý tým). Klíče, které kód bere z tabulky polí hry nebo z jejích vlastních názvů statistik, v tomto seznamu nejsou; výše v „Co se zaznamenává“ jsou uvedeny.

## Úplnost {#completeness}

Watcher se řídí [pravidlem převodníků](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md): co zdroj obsahuje, se přečte nebo uloží, nikdy se nezahodí. Kromě řádků se každý paket, stránka, řádek nebo odpověď, kterou adaptér přijme, uloží celý do `heat.raw.parquet` relace (sloupce `time`, `ms`, `type`, `used`, `payload`, `text` a případná pole uložená podle názvu; `used` označuje, co se také stalo řádky), a `selfCheck.completeness` v `meta.json` počítá každý `type` - `lost` je 0.

**Načteno**

- pro každý slot řidiče (podle vlastního offsetu a velikosti hlavičky): jméno, slot, stav dojezdu, místo, světová pozice, dokončená kola, aktuální čas kola, pozice v boxech, rychlost
- vlastní pole hráče, jen když stránka má layout r3e.h 3.6: názvy tratě a varianty, typ relace, pozice v závodě, nejlepší a předchozí kolo, body za incidenty, rychlostní stupeň, plyn, brzda, slot hráče
- offsety odvozené z r3e.h 3.6 od Sector3 a ověřené na stránce sestavené z něj v testech; zatím ne proti hře

**Uchováno surové**

- `r3e`: celé mapování $R3E, při každém čtení, jehož bajty se liší od naposledy uložené kopie - každé pole r3e.h: fyzika hráče (orientace, rychlosti, zrychlení, g-síly), motor, palivo, pneumatiky, brzdy, poškození, příznaky, menu boxů, časy sektorů, celá data řidiče z každého slotu (třída, model, tým, časy sektorů, rozdíly, tresty, pneumatiky)
- `used` je pravda pro stránku čtenou do řádků; nepravda pro stránku v menu, při pauze, v replayi, jiného layoutu, nebo zachycenou uprostřed zápisu (`torn` 1); `unchanged_reads` v meta.json počítá čtení, která jsou bajt po bajtu stejná jako kopie uložená předtím

**Nedostupné**

- vstupy a fyzika ostatních jezdců: stránka dává jen vlastní data hráče
- přesné časy kol ostatních aut: slot má jen svůj probíhající čas kola, takže kolo je poslední zachycený probíhající čas (na asi 0,1 s)
- vlastní pole hráče v jiném layoutu než 3.6: uložena surově, nečtou se, dokud se neověří

**Velikost**: stránka má 44 KB (r3e.h 3.6; mapování se zaokrouhluje na celé 4KB stránky), až 10krát za sekundu při jízdě: asi 1,6 GB za hodinu před kompresí; prázdné sloty řidičů a pole, která se nemění, se zstd komprimují velmi dobře (na reálné jízdě zatím neměřeno)

## Ověřeno {#verified}

testováno na stránce sestavené v testu z r3e.h 3.6 (offsety odvozeny z oficiální hlavičky); zatím neotestováno ve hře; časy kol ostatních aut jsou poslední zachycený probíhající čas kola (na asi 0,1 s)

## Zdroj {#source}

[heat3d_watch/adapters/simracing_shm.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/simracing_shm.py)

<!-- Vygenerováno z adaptéru nástrojem tools/gen_game_pages.py; změňte adaptér a spusťte generování znovu, místo úpravy této stránky. -->
