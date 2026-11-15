---
title: "Automobilista 2 (živá data)"
nav_order: 6
lang: "cs"
source: game-automobilista-2.md
source_hash: "5e3ca1507524"
nav_exclude: true
search_exclude: true
---
# Automobilista 2 (živá data) {#automobilista-2-live-data}

Když hrajete Automobilista 2, Watcher uloží data, která hra sama posílá ven, abyste se na ně mohli později podívat na mapě v prohlížeči 3DHeat.

*Technické podrobnosti: adaptér `automobilista-2`, druh [`telemetry`](sources-and-rules.md); běží, dokud běží `AMS2AVX.exe` nebo `AMS2.exe`, a hledá nová data každých 0,1 s.*

## Co se zaznamenává {#what-is-recorded}

- pozice každého auta (světové XYZ, m) 10krát za sekundu, podle jména řidiče, vlastní auto označeno, s rychlostí a pozicí v závodě; vlastní rychlostní stupeň, plyn, brzda
- začátek relace s tratí, jak ji hra pojmenovala; kola každého auta s časem kola; dojezdy; vlastní zastávky v boxech
- teleporty (návrat do boxů, restart): `teleport`, kde auto bylo, `spawn`, kde je nyní
- vlastní kola, nejlepší kolo, pozice v závodě, vzdálenost, nejvyšší rychlost
- celá sdílená paměť hry v `heat.raw.parquet`, při každé změně

## Odkud to pochází {#where-it-comes-from}

sdílená paměť $pcars2$ (layout SMS SharedMemory.h)

## Jak to zapnout {#how-to-switch-it-on}

Ve hře: Options > System > Shared Memory: „Project CARS 2“

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

#### Automobilista 2 / Project CARS 2 - `$pcars2$` {#automobilista-2--project-cars-2---pcars2}

SMS `SharedMemory.h` (je dodán ve složce hry Support\SharedMemory;
AMS2: Options > System > Shared Memory „Project CARS 2“), `#pragma pack(4)`.
`mParticipantInfo[64]` od bajtu 28, každý po 100 bajtech: mIsActive, mName[64],
mWorldPosition[3] (m, Y nahoru), mCurrentLapDistance, mRacePosition,
mLapsCompleted, mCurrentLap, mCurrentSector; mViewedParticipantIndex (20)
je auto hráče; pro každého účastníka mLastLapTimes (9200), mRaceStates
(9520), mSpeeds (10800); hráčovo mBestLapTime (6716), mLastLapTime
(6720), mSpeed (6848), mBrake, mThrottle, mGear; mSequenceNumber (7320) je
liché, dokud hra zapisuje. Offsety byly odvozeny ze dvou
nezávislých kopií hlavičky (vlastní kopie hry není zde nainstalovaná),
které se shodují.

Obě stránky se navíc ukládají celé (docs/converters.md, „Live sources“): celé
mapování, při každém čtení, jehož bajty se liší od naposledy uložené kopie, v
surovém doprovodném souboru relace pod `type` `r3e` nebo `pcars2` - každý slot
řidiče a každé pole struktury, i ta, která se zde nečtou, takže pozdější dekodér
potřebuje jen tento soubor.

Stejný modul slouží také: [Project CARS 2 (živá data)](game-project-cars-2.md), [RaceRoom Racing Experience (živá data)](game-raceroom.md).

## Pozice a osy {#positions-and-axes}

| | |
|---|---|
| Zaznamenané pozice | ano |
| Osa nahoru | `y` |
| Jednotky | metry |
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

- pro každého účastníka (až 64): aktivní, jméno, světová pozice, pozice v závodě, dokončená kola; jeho poslední čas kola, stav v závodě a rychlost
- auto hráče (mViewedParticipantIndex), stav hry a relace, umístění a varianta tratě, nejlepší a poslední kolo, rychlost, brzda, plyn, rychlostní stupeň; mSequenceNumber přeskočí kopii zachycenou uprostřed zápisu
- offsety z dvou nezávislých kopií SharedMemory.h od SMS, které se shodují, ověřené na stránce sestavené z nich v testech; zatím ne proti hře

**Uchováno surové**

- `pcars2`: celé mapování $pcars2$ - struktura jde výrazně za 11 312 bajtů, které se zde čtou - při každém čtení, jehož bajty se liší od naposledy uložené kopie: orientace každého účastníka, časy sektorů, názvy aut a tříd, režimy a příznaky boxů, fyzika hráče, pneumatiky, odpružení, poškození, počasí a vše, co přidaly pozdější verze Automobilisty 2
- `used` je pravda pro stránku čtenou do řádků; nepravda pro stránku v menu, při pauze, v replayi, jiného layoutu, nebo zachycenou uprostřed zápisu (`torn` 1); `unchanged_reads` v meta.json počítá čtení, která jsou bajt po bajtu stejná jako kopie uložená předtím

**Nedostupné**

- vstupy a fyzika ostatních účastníků: stránka dává jen prohlížené auto
- vše, když je v hře vypnuta možnost sdílené paměti (Automobilista 2 pak nic nezapisuje)

**Velikost**: mapování má asi 20 až 30 KB (podle verze hry), až 10krát za sekundu při jízdě: zhruba 0,7 až 1,1 GB za hodinu před kompresí; zstd zmenší prázdné sloty účastníků a jména, která se nemění, na zlomek (na reálné jízdě zatím neměřeno)

## Ověřeno {#verified}

testováno na stránce sestavené v testu; offsety z dvou nezávislých kopií SharedMemory.h, které se shodují, ne z kopie, kterou hra dodává; zatím neotestováno ve hře

## Zdroj {#source}

[heat3d_watch/adapters/simracing_shm.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/simracing_shm.py)

<!-- Vygenerováno z adaptéru nástrojem tools/gen_game_pages.py; změňte adaptér a spusťte generování znovu, místo úpravy této stránky. -->
