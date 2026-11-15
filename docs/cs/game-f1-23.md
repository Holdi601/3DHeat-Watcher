---
title: "EA SPORTS F1 23 (živá data)"
nav_order: 14
lang: "cs"
source: game-f1-23.md
source_hash: "d7b523188e51"
nav_exclude: true
search_exclude: true
---
# EA SPORTS F1 23 (živá data) {#ea-sports-f1-23-live-data}

Když hrajete EA SPORTS F1 23, Watcher ukládá data, která samotná hra vysílá, abyste se na ně mohli později podívat na mapě v prohlížeči 3DHeat.

*Technické podrobnosti: adaptér `f1-23`, druh [`telemetry`](sources-and-rules.md); běží, dokud běží `F1_23.exe`, a hledá nová data každých 0,1 s.*

## Co se zaznamenává {#what-is-recorded}

- pozice každého auta (světové XYZ, m) 10krát za sekundu, podle jména jezdce, týmu, vlastní auto označeno (`own_car` 1, podle indexu hráčova auta), s rychlostí, rychlostním stupněm, plynem, brzdou, řízením, otáčkami, DRS, zatáčením, sklonem a náklonem (stupně) a g-silami
- kola na každé auto s časem kola a pozicí v závodě; cíle a odstoupení
- herní události závodu: začátek a konec relace, nejrychlejší kolo, tresty, předjetí, kolize, safety car, červená vlajka, startovní světla, šachovnicová vlajka, vítěz, flashbacky (`teleport`, kde auto bylo, `spawn`, kam se vrátilo)
- trať, typ relace, počet kol a jezdci každé relace
- vlastní kola, nejlepší kolo, pozice v závodě a na startu, zastávky v boxech, tresty, předjetí, kolize, vzdálenost, nejvyšší rychlost
- každý paket, který hra posílá, celý, v `heat.raw.parquet` – i ty, které se nenačítají do řádků

## Odkud to pochází {#where-it-comes-from}

UDP telemetrie 127.0.0.1:20777 (Dokumenty\My Games\F1 23\hardwaresettings\hardware_settings_config.xml)

## Jak to zapnout {#how-to-switch-it-on}

Ve hře: Settings > Telemetry Settings > UDP Telemetry On, IP 127.0.0.1, port 20777 – nebo `python -m heat3d_watch setup f1-23 --apply` (upraví hardware_settings_config.xml, nejdřív se zálohuje; hra musí být zavřená). Dokud port 20777 drží jiná aplikace, Watcher ho jí nechá

Příkaz napište do terminálu otevřeného ve složce Watcheru (viz [Než začnete](before-you-start.md)). Pokud selže, poslední řádek vysvětlí proč; [Instalace a spuštění](installing-and-running.md) popisuje obvyklé příčiny.

`python -m heat3d_watch setup f1-23` vypíše soubory, které by změnil; `python -m heat3d_watch setup f1-23 --apply` je změní a původní soubor ponechá jako `<file>.heat3d-backup` (viz [Příkazy](commands.md#setup)). Pro každou změnu vypíše `f1-23: changed: ...`, nebo `f1-23: nothing to change`, když je to už zapnuté.

## Jak to funguje {#how-it-works}

EA SPORTS F1 23, F1 24 a F1 25: oficiální UDP telemetrie, každé auto na trati.

Hry ji posílají samy (Settings > Telemetry Settings, nebo
`Dokumenty/My Games/<F1 xx>/hardwaresettings/hardware_settings_config.xml`,
`<udp enabled="true" ip="127.0.0.1" port="20777" sendRate="20" format="2025" ...>`).
Little-endian, zhuštěné, 29bajtová hlavička na každém paketu (stejná ve formátech 2023,
2024 a 2025):

```text
uint16 packetFormat, uint8 gameYear, gameMajorVersion, gameMinorVersion,
packetVersion, packetId, uint64 sessionUID, float sessionTime,
uint32 frameIdentifier, overallFrameIdentifier, uint8 playerCarIndex,
secondaryPlayerCarIndex
```

Co se čte, podle id paketu:

```text
0 Motion        CarMotionData[22], 60 bytes each: world position x y z
                (metres; Y is up), world velocity, forward and right
                vectors (int16 / 32767), g-forces, yaw pitch roll
1 Session       weather, temperatures, total laps, track length, session
                type, track id, ... network game
2 Lap Data      LapData[22]: last lap time, lap distance, race position,
                current lap number, pit stops, penalties, grid position,
                driver and result status. 50 bytes per car in 2023; 57 in
                2024 and 2025, which added the minutes parts of the deltas
                and the speed trap.
3 Event         a four-letter code and a union of details: SSTA SEND FTLP
                RTMT DRSE DRSD TMPT CHQF RCWN PENA SPTP STLG LGOT DTSV SGSV
                FLBK BUTN RDFL OVTK SCAR COLL
4 Participants  ParticipantData[22]: AI or human, driver, team, race
                number, name (48 bytes in 2023 and 2024, 32 in 2025; 58,
                60 and 57 bytes per car)
6 Car Telemetry CarTelemetryData[22], 60 bytes: speed km/h, throttle,
                steer, brake, clutch, gear, rpm, DRS ...
```

Každý paket se také uchová celý, tak jak přišel, ve vedlejším surovém souboru relace (`heat.raw.parquet`, `type` je název paketu – `motion`, `car_status` ... –, s `format`, `packet_id`, `frame` a `session_uid`) – ty, které jsou výše, i ty, které zatím nikdo nečte: 5 Car Setups, 7 Car Status, 8 Final Classification, 9 Lobby Info, 10 Car Damage, 11 Session History, 12 Tyre Sets, 13 Motion Ex, 14 Time Trial, 15 Lap Positions, každé pozdější id a pakety ve formátu, který tento kód nečte. Pozdější dekodér tedy potřebuje jen vedlejší soubor.

Pozice každého auta je v paketu Motion – i online, kde ji hra sama vydává (jen palivo, ERS, poškození a data sad pneumatik se zadržují u hráčů, jejichž „Your Telemetry“ je omezená). Každé auto se zaznamenává zhruba 10krát za sekundu pod jménem účastníka („car N“, dokud se jména nedostanou), tým podle názvu a vlastní auto hráče se označí `own`.

Zdroje: „F1 25 UDP Specification“ od EA (forums.ea.com, informační centrum F1 her), specifikace F1 23 a F1 24; stejné tabulky zrcadlí MacManley/f1-25-udp (MIT). Pakety v testech jsou postavené podle těchto rozložení.

Stejný modul slouží také: [EA SPORTS F1 24 (živá data)](game-f1-24.md), [EA SPORTS F1 25 (živá data)](game-f1-25.md).

## Pozice a osy {#positions-and-axes}

| | |
|---|---|
| Zaznamenané pozice | ano |
| Osa nahoru | `y` |
| Jednotky | metry |
| Zrcadleno pro prohlížeč | žádné |
| Měřítko jednotek (`scale`: prohlížeč pozice tímto násobí) | 1 |

Tyto hodnoty se zapisují do `meta.json` každé relace (`axes`) a, když relace má pozice, do patičky `heat.parquet`, takže prohlížeč 3DHeat otáčí a měřítkuje řádky sám – viz [Data](the-data.md).

## Více hráčů {#multiplayer}

- Označeno jako hraná online (`multiplayer`): **ano**. `games --markdown` to ukáže jako „povoleno (čte jen to, co hra zveřejňuje)“.
- Druh `telemetry`: čte jen to, co hra nebo platforma vydává (UDP port nebo sdílená paměť, kterou hra zveřejňuje), takže nahrává i v online hře, stejně jako offline; příznak rozhoduje jen o tom, zda se smí číst paměť.
- Paměť: tento adaptér ji **nikdy** nečte. Paměť čtou jen adaptéry `memory` a nikdy u hry označené jako hraná online – viz [Zdroje a pravidla](sources-and-rules.md).

## Zaznamenané statistiky {#statistics-recorded}

Klíče statistik, které kód tohoto adaptéru nastavuje podle jména (každé relace `stats` v `meta.json` a tabulka `stats` v `watcher.sqlite`):

`best_lap`, `collisions`, `distance_km`, `fastest_laps`, `finishes`, `flashbacks`, `grid_position`, `laps`, `overtaken`, `overtakes`, `penalties`, `penalty_seconds`, `pit_stops`, `race_position`, `sessions`, `top_speed_kmh`, `wins`

Klíč ve složených závorkách se doplní za běhu (`score.{team}` je jeden klíč na každý tým). Klíče, které kód bere z tabulky polí hry nebo z jejích vlastních názvů statistik, v tomto seznamu nejsou; výše v „Co se zaznamenává“ jsou uvedené jménem.

## Úplnost {#completeness}

Watcher dodržuje [pravidlo převodníků](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md) 3DHeat: co zdroj obsahuje, se načte nebo uchová, nikdy se nezahodí. Kromě řádků se každý paket, stránka, řádek nebo odpověď, kterou adaptér dostane, uchovává celý v `heat.raw.parquet` relace (sloupce `time`, `ms`, `type`, `used`, `payload`, `text` a případná pole uchovaná podle jména; `used` označuje, co se také stalo řádky), a `selfCheck.completeness` v `meta.json` počítá každý `type` – `lost` je 0.

**Načteno**

- 0 Motion: světová pozice a rychlost každého auta a nově i zatáčení, sklon a náklon (stupně, z radiánů ve specifikaci) a boční, podélná a vertikální g-síla, u řádků pozice každého auta
- 1 Session: trať, typ relace, počet kol, délka trati, online nebo ne (`sessions` v meta.json)
- 2 Lap Data: čas posledního kola, číslo kola, pozice v závodě a na startu, zastávky v boxech, tresty, stav výsledku (kola, cíle, odstoupení, statistiky)
- 3 Event: každý kód kromě BUTN jako vlastní řádek se svými podrobnostmi
- 4 Participants: jména jezdců, týmy, počet aktivních aut (`player` a `team` v řádcích, `drivers` v meta.json)
- 6 Car Telemetry: rychlost, rychlostní stupeň, plyn, brzda, a nově také řízení (-1..1), otáčky a DRS, u řádků pozice každého auta
- ověřeno proti zveřejněným specifikacím UDP od EA pro formáty 2023, 2024 a 2025 (velikosti paketů ověřené v testech); zatím ne proti hře

**Uchováno surové**

- každý paket celý v `heat.raw.parquet`, `payload` je datagram, `type` název jeho id: `motion`, `session`, `lap_data`, `event`, `participants`, `car_setups`, `car_telemetry`, `car_status`, `final_classification`, `lobby_info`, `car_damage`, `session_history`, `tyre_sets`, `motion_ex`, `time_trial`, `lap_positions` (`packet <n>` pro id, které specifikace zatím neuvádějí); sloupce `format` (2023/2024/2025), `packet_id`, `frame`, `session_uid`
- `used` je true u paketů čtených výše (Motion, Session, Lap Data, Participants, Car Telemetry a kódy událostí jiné než BUTN); zbytek – nastavení vozu, stav vozu (palivo, ERS, typ a stáří pneumatik, příznaky), konečná klasifikace, lobby, poškození vozu, historie relace (každý čas kola a sektoru na auto), sady pneumatik, motion ex (zavěšení vlastního auta, rychlosti kol, lokální rychlost, úhlová rychlost a zrychlení), time trial, pozice v kolech, události tlačítek BUTN – se uchovává pro pozdější dekodér
- `format <year>`: paket ve formátu před rokem 2023 (jiné rozložení hlavičky), celý; `short`: datagram kratší než 29bajtová hlavička, celý

**Nedostupné**

- palivo, ERS, poškození a sady pneumatik ostatních hráčů online, když je jejich „Your Telemetry“ omezená: hra jim posílá nuly
- pakety poslané, když Watcher neběží, nebo když jiná aplikace drží port 20777: UDP hra neukládá

**Velikost**: při přenosové frekvenci 60 Hz má každý paket asi 0,38 MB/s (Motion, Lap Data, Car Telemetry, Car Status a Motion Ex na 60 Hz, Session History a Tyre Sets 20krát za sekundu, Car Damage 10krát, Session a Car Setups 2krát) plus asi 0,03 MB/s hlaviček položek: asi 1,5 GB za hodinu jízdy před kompresí, asi 0,55 GB při výchozích 20 Hz; zstd to zmenší na zlomek (prázdné sloty aut a opakované hodnoty se dobře stlačí; na skutečné relace zatím neměřeno)

## Ověřeno {#verified}

testováno na paketech ve formátech 2023, 2024 a 2025 postavených podle zveřejněné specifikace EA, poslaných přes UDP; neotestováno proti hře

## Zdroj {#source}

[heat3d_watch/adapters/f1.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/f1.py)

<!-- Vygenerováno z adaptéru nástrojem tools/gen_game_pages.py; změňte adaptér a spusťte ho znovu, místo úprav této stránky. -->
