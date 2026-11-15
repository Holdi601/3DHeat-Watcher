---
title: "EA SPORTS F1 24 (živé dáta)"
nav_order: 15
lang: "sk"
source: game-f1-24.md
source_hash: "a189298930fc"
nav_exclude: true
search_exclude: true
---
# EA SPORTS F1 24 (živé dáta) {#ea-sports-f1-24-live-data}

Keď hráte EA SPORTS F1 24, watcher ukladá dáta, ktoré samotná hra vysiela, aby ste si ich neskôr mohli pozrieť na mape vo vieweri 3DHeat.

*Technické podrobnosti: adaptér `f1-24`, druh [`telemetry`](sources-and-rules.md); beží, kým beží `F1_24.exe`, a hľadá nové dáta každých 0,1 s.*

## Čo sa zaznamenáva {#what-is-recorded}

- pozícia každého auta (svetové XYZ, m) 10-krát za sekundu, podľa mena jazdca, tímu, vlastné auto označené (`own_car` 1, z indexu hráčovho auta), s rýchlosťou, rýchlostným stupňom, plynom, brzdou, zatáčaním, otáčkami, DRS, odchýlkou, náklonom a pitch (stupne) a g-silami
- kolá každého auta s časom kola a pozíciou v pretekoch; cieľ a odstúpenia
- herné udalosti pretekov: začiatok a koniec relácie, najrýchlejšie kolo, tresty, predbiehanie, kolízie, safety car, červená vlajka, štartovacie svetlá, šachovnicová vlajka, víťaz, flashbacky (`teleport`, kde auto bolo, `spawn`, kam sa vrátilo)
- trať, typ relácie, kolá a jazdci každej relácie
- vlastné kolá, najlepšie kolo, pozícia v pretekoch a na štarte, zastávky v boxoch, tresty, predbiehania, kolízie, vzdialenosť, najvyššia rýchlosť
- každý paket, ktorý hra posiela, celý, v `heat.raw.parquet` – aj tie, ktoré sa nečítajú do riadkov

## Odkiaľ to pochádza {#where-it-comes-from}

UDP telemetria 127.0.0.1:20777 (Documents\My Games\F1 24\hardwaresettings\hardware_settings_config.xml)

## Ako to zapnúť {#how-to-switch-it-on}

V hre: Settings > Telemetry Settings > UDP Telemetry On, IP 127.0.0.1, port 20777 – alebo `python -m heat3d_watch setup f1-24 --apply` (upraví hardware_settings_config.xml, najprv zálohuje; hra musí byť zatvorená). Ak port 20777 drží iná aplikácia, watcher ho nechá tej aplikácii

Príkaz zadajte v termináli otvorenom v priečinku watchera (pozrite [Pred začiatkom](before-you-start.md)). Ak zlyhá, posledný riadok povie prečo; [Inštalácia a spustenie](installing-and-running.md) popisuje najčastejšie príčiny.

`python -m heat3d_watch setup f1-24` vypíše, ktoré súbory by zmenil; `python -m heat3d_watch setup f1-24 --apply` ich zmení a pôvodný súbor uloží ako `<file>.heat3d-backup` (pozrite [Príkazy](commands.md#setup)). Pre každú zmenu vypíše `f1-24: changed: ...`, alebo `f1-24: nothing to change`, keď je to už zapnuté.

## Ako to funguje {#how-it-works}

EA SPORTS F1 23, F1 24 a F1 25: oficiálna UDP telemetria, každé auto na trati.

Hry ju posielajú samy (Settings > Telemetry Settings, alebo
`Documents/My Games/<F1 xx>/hardwaresettings/hardware_settings_config.xml`,
`<udp enabled="true" ip="127.0.0.1" port="20777" sendRate="20" format="2025" ...>`).
Little-endian, zbalené, 29-bajtová hlavička v každom pakete (rovnaká vo formátoch 2023,
2024 a 2025):

```text
uint16 packetFormat, uint8 gameYear, gameMajorVersion, gameMinorVersion,
packetVersion, packetId, uint64 sessionUID, float sessionTime,
uint32 frameIdentifier, overallFrameIdentifier, uint8 playerCarIndex,
secondaryPlayerCarIndex
```

Čo sa číta, podľa id paketu:

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

Každý paket sa tiež uchová celý, tak ako prišiel, v surovom sprievodnom súbore relácie
(`heat.raw.parquet`, `type` názov paketu – `motion`, `car_status` ... –
s `format`, `packet_id`, `frame` a `session_uid`) – tie, ktoré sa čítajú vyššie, aj tie,
ktoré zatiaľ nič nečíta: 5 Car Setups, 7 Car Status, 8 Final Classification, 9 Lobby
Info, 10 Car Damage, 11 Session History, 12 Tyre Sets, 13 Motion Ex, 14 Time
Trial, 15 Lap Positions, každé neskoršie id a pakety vo formáte, ktorý watcher nečíta.
Neskorší dekodér teda potrebuje len sprievodný súbor.

Pozícia každého auta je v pakete Motion – aj online, kde ju hra sama vydáva (len palivo, ERS, poškodenie a sady pneumatík sa zadržiavajú
pre hráčov, ktorých „Your Telemetry“ je obmedzená). Každé auto sa zaznamenáva asi 10 Hz
pod menom účastníka („car N“, kým sa mená neobjavia), tím podľa názvu a vlastné auto hráča
označené `own`.

Zdroje: EA „F1 25 UDP Specification“ (forums.ea.com, F1 games info hub),
špecifikácie F1 23 a F1 24; tie isté tabuľky zrkadlí MacManley/f1-25-udp (MIT). Pakety v testoch sú postavené podľa týchto rozložení.

Rovnaký modul slúži aj: [EA SPORTS F1 23 (živé dáta)](game-f1-23.md), [EA SPORTS F1 25 (živé dáta)](game-f1-25.md).

## Pozície a osi {#positions-and-axes}

| | |
|---|---|
| Pozície sa zaznamenávajú | áno |
| Os nahor | `y` |
| Jednotky | metre |
| Zrkadlené pre viewer | žiadne |
| Mierka (`scale`: viewer pozície násobí týmto číslom) | 1 |

Tieto hodnoty idú do `meta.json` každej relácie (`axes`) a, ak relácia obsahuje pozície, do päty `heat.parquet`, takže viewer 3DHeat riadky otáča a mení mierku sám – pozrite [Dáta](the-data.md).

## Viachráčová hra {#multiplayer}

- Označené ako hraná online (`multiplayer`): **áno**. `games --markdown` to zobrazí ako „povolené (číta len to, čo hra zverejňuje)“.
- Druh `telemetry`: číta len to, čo hra alebo platforma vydáva (UDP port alebo zdieľaná pamäť, ktorú hra zverejňuje), takže zaznamenáva aj online hru, aj offline; príznak rozhoduje len o tom, či sa smie čítať pamäť.
- Pamäť: tento adaptér ju **nikdy** nečíta. Pamäť čítajú len adaptéry `memory` a nikdy pre hru označenú ako hranú online – pozrite [Pravidlá a zdroje](sources-and-rules.md).

## Zaznamenané štatistiky {#statistics-recorded}

Štatistické kľúče, ktoré kód tohto adaptéra nastavuje podľa názvu (`stats` každej relácie v `meta.json` a tabuľka `stats` v `watcher.sqlite`):

`best_lap`, `collisions`, `distance_km`, `fastest_laps`, `finishes`, `flashbacks`, `grid_position`, `laps`, `overtaken`, `overtakes`, `penalties`, `penalty_seconds`, `pit_stops`, `race_position`, `sessions`, `top_speed_kmh`, `wins`

Kľúč v zložených zátvorkách sa doplní až za behu (`score.{team}` je jeden kľúč pre každý tím). Kľúče, ktoré kód berie z tabuľky polí hry alebo z vlastných názvov štatistík hry, v tomto zozname nie sú; „Čo sa zaznamenáva“ vyššie ich uvádza.

## Úplnosť {#completeness}

Watcher sa riadi [pravidlom konvertorov](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md) 3DHeat: čo zdroj obsahuje, sa prečíta alebo uchová, nikdy sa nezahodí. Okrem riadkov sa každý paket, stránka, riadok alebo odpoveď, ktorú adaptér dostane, uchová celý v `heat.raw.parquet` relácie (stĺpce `time`, `ms`, `type`, `used`, `payload`, `text` a potom každé pole, ktoré sa podľa názvu ponechalo; `used` označuje, čo sa stalo aj riadkami), a `selfCheck.completeness` v `meta.json` počíta každý `type` – `lost` je 0.

**Prečítané**

- 0 Motion: svetová pozícia a rýchlosť každého auta, teraz aj odchýlka, náklon, pitch (stupne, z radiánov špecifikácie) a bočné, pozdĺžne a vertikálne g-sily, na riadkoch pozície každého auta
- 1 Session: trať, typ relácie, celkový počet kôl, dĺžka trate, online alebo nie (`sessions` v meta.json)
- 2 Lap Data: čas posledného kola, číslo kola, pozícia v pretekoch a na štarte, zastávky v boxoch, tresty, stav výsledku (kolá, cieľ, odstúpenia, štatistiky)
- 3 Event: každý kód okrem BUTN ako vlastný riadok, s jeho podrobnosťami
- 4 Participants: mená jazdcov, tímy, počet aktívnych áut (`player` a `team` v riadkoch, `drivers` v meta.json)
- 6 Car Telemetry: rýchlosť, rýchlostný stupeň, plyn, brzda, teraz aj zatáčanie (-1..1), otáčky a DRS, na riadkoch pozície každého auta
- overené podľa zverejnených špecifikácií UDP od EA pre formáty 2023, 2024 a 2025 (veľkosti paketov overené v testoch); zatiaľ nie voči samotnej hre

**Uchované surové**

- každý paket celý v `heat.raw.parquet`, `payload` je datagram, `type` názov jeho id: `motion`, `session`, `lap_data`, `event`, `participants`, `car_setups`, `car_telemetry`, `car_status`, `final_classification`, `lobby_info`, `car_damage`, `session_history`, `tyre_sets`, `motion_ex`, `time_trial`, `lap_positions` (`packet <n>` pre id, ktoré špecifikácie zatiaľ neuvádzajú); stĺpce `format` (2023/2024/2025), `packet_id`, `frame`, `session_uid`
- `used` je pravda pre pakety prečítané vyššie (Motion, Session, Lap Data, Participants, Car Telemetry a kódy Event okrem BUTN); zvyšok – nastavenia áut, stav auta (palivo, ERS, zmes a vek pneumatík, príznaky), konečná klasifikácia, lobby, poškodenie auta, história relácie (každý čas kola a sektora pre každé auto), sady pneumatík, motion ex (zavesenie vlastného auta, rýchlosti kolies, lokálna rýchlosť, uhlová rýchlosť a zrýchlenie), time trial, pozície kôl, udalosti tlačidiel BUTN – sa uchovajú pre neskorší dekodér
- `format <year>`: paket vo formáte pred rokom 2023 (iné rozloženie hlavičky), celý; `short`: datagram kratší ako 29-bajtová hlavička, celý

**Nie je k dispozícii**

- palivo, ERS, poškodenie a sady pneumatík iných hráčov online, keď ich „Your Telemetry“ je obmedzená: hra posiela nuly
- pakety poslané, keď watcher nebeží, alebo keď iná aplikácia drží port 20777: UDP hra neukladá

**Veľkosť**: pri rýchlosti odosielania 60 Hz je každý paket asi 0,38 MB/s (Motion, Lap Data, Car Telemetry, Car Status a Motion Ex pri 60 Hz, Session History a Tyre Sets 20/s, Car Damage 10/s, Session a Car Setups 2/s) plus asi 0,03 MB/s hlavičiek položiek: asi 1,5 GB za hodinu jazdy pred kompresiou, asi 0,55 GB pri predvolených 20 Hz; zstd to zmenší na zlomok (prázdne miesta áut a opakujúce sa hodnoty sa dobre komprimujú; na skutočnej relácii zatiaľ nemerané)

## Overené {#verified}

testované na paketoch vo formátoch 2023, 2024 a 2025, postavených podľa zverejnenej špecifikácie EA, odoslaných cez UDP; netestované voči hre

## Zdroj {#source}

[heat3d_watch/adapters/f1.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/f1.py)

<!-- Generated from the adapter by tools/gen_game_pages.py; change the adapter and run it again rather than editing this page. -->
