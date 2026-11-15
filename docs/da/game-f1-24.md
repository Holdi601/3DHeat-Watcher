---
title: "EA SPORTS F1 24 (live-data)"
nav_order: 15
lang: "da"
source: game-f1-24.md
source_hash: "a189298930fc"
nav_exclude: true
search_exclude: true
---
# EA SPORTS F1 24 (live-data) {#ea-sports-f1-24-live-data}

Mens du spiller EA SPORTS F1 24, gemmer watcheren de data, spillet selv sender ud, så du senere kan se dem på et kort i 3DHeat-vieweren.

*Tekniske detaljer: adapter `f1-24`, slags [`telemetry`](sources-and-rules.md); den kører, mens `F1_24.exe` kører, og kigger efter nye data hvert 0,1 s.*

## Hvad der optages {#what-is-recorded}

- hver bils position (verdens XYZ, m) 10 gange i sekundet, efter førerens navn, hold, med egen bil markeret (`own_car` 1, fra spillerens bilindeks), med hastighed, gear, gas, bremse, styring, omdrejninger, DRS, giering, stigning, rulning (grader) og g-kræfter
- omgange pr. bil med omgangstid og placering i løbet; mål og udgåelser
- spillets løbshændelser: sessionens start og slut, hurtigste omgang, straffe, overhalinger, kollisioner, safety car, rødt flag, startlys, ternet flag, vinder, flashbacks (`teleport` hvor bilen var, `spawn` hvor den kom tilbage til)
- bane, sessionstype, omgange og førere i hver session
- egne omgange, bedste omgang, placering i løb og startgrid, pitstops, straffe, overhalinger, kollisioner, distance, topfart
- hver pakke spillet sender, helt, i `heat.raw.parquet` - også dem der ikke bliver læst til rækker

## Hvor det kommer fra {#where-it-comes-from}

UDP-telemetri 127.0.0.1:20777 (Documents\My Games\F1 24\hardwaresettings\hardware_settings_config.xml)

## Sådan slår du det til {#how-to-switch-it-on}

I spillet: Settings > Telemetry Settings > UDP Telemetry On, IP 127.0.0.1, port 20777 - eller `python -m heat3d_watch setup f1-24 --apply` (redigerer hardware_settings_config.xml, sikkerhedskopieret først; spillet skal være lukket). Mens et andet program holder 20777, lader watcheren porten være til det

Skriv kommandoen i en terminal, der er åbnet i watcherens mappe (se [Før du går i gang](before-you-start.md)). Hvis det fejler, siger den sidste linje hvorfor; [Installation og kørsel](installing-and-running.md) dækker de almindelige årsager.

`python -m heat3d_watch setup f1-24` viser, hvilke filer den ville ændre; `python -m heat3d_watch setup f1-24 --apply` ændrer dem og gemmer originalen som `<file>.heat3d-backup` (se [Kommandoer](commands.md#setup)). Den skriver `f1-24: changed: ...` for hver ændring, eller `f1-24: nothing to change`, når den allerede er slået til.

## Sådan virker det {#how-it-works}

EA SPORTS F1 23, F1 24 og F1 25: den officielle UDP-telemetri, hver bil på banen.

Spillene sender den selv (Settings > Telemetry Settings, eller
`Documents/My Games/<F1 xx>/hardwaresettings/hardware_settings_config.xml`,
`<udp enabled="true" ip="127.0.0.1" port="20777" sendRate="20" format="2025" ...>`).
Little-endian, pakket, en 29-byte header på hver pakke (den samme i 2023-, 2024- og 2025-formaterne):

```text
uint16 packetFormat, uint8 gameYear, gameMajorVersion, gameMinorVersion,
packetVersion, packetId, uint64 sessionUID, float sessionTime,
uint32 frameIdentifier, overallFrameIdentifier, uint8 playerCarIndex,
secondaryPlayerCarIndex
```

Hvad der læses, efter pakke-id:

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

Hver pakke gemmes også helt, som den kom, i sessionens rå sidecar
(`heat.raw.parquet`, `type` pakkens navn - `motion`, `car_status` ... -
med `format`, `packet_id`, `frame` og `session_uid`) - dem der læses ovenfor og dem
ingen læser endnu: 5 Car Setups, 7 Car Status, 8 Final Classification, 9 Lobby
Info, 10 Car Damage, 11 Session History, 12 Tyre Sets, 13 Motion Ex, 14 Time
Trial, 15 Lap Positions, ethvert senere id, og pakker i et format denne ikke
læser. Så en senere afkoder behøver kun sidecar'en.

Hver bils position står i Motion-pakken - også online, hvor spillet selv udleverer
den (kun brændstof, ERS, skade og dæksæt-data holdes tilbage for spillere, hvis "Your
Telemetry" er begrænset). Hver bil optages cirka 10 Hz under sit deltagernavn ("car N",
indtil navnene kommer), holdet efter navn, og spillerens egen bil markeres `own`.

Kilder: EA's "F1 25 UDP Specification" (forums.ea.com, F1 games info hub),
F1 23- og F1 24-specifikationerne; de samme tabeller spejlet i
MacManley/f1-25-udp (MIT). Pakker i tests er bygget ud fra disse layouts.

Det samme modul betjener også: [EA SPORTS F1 23 (live-data)](game-f1-23.md), [EA SPORTS F1 25 (live-data)](game-f1-25.md).

## Positioner og akser {#positions-and-axes}

| | |
|---|---|
| Positioner optaget | ja |
| Opadakse | `y` |
| Enheder | meter |
| Spejlet for viewer | ingen |
| Enhedsskala (`scale`: viewer ganger positionerne med den) | 1 |

Disse går ind i hver sessions `meta.json` (`axes`) og, når sessionen har positioner, i `heat.parquet`s footer, så 3DHeat-viewer selv drejer og skalerer rækkerne - se [Dataene](the-data.md).

## Multiplayer {#multiplayer}

- Markeret som spillet online (`multiplayer`): **ja**. `games --markdown` viser dette som "allowed (reads only what the game publishes)".
- Slags `telemetry`: den læser kun det, spillet eller platformen udleverer (en UDP-port eller delt hukommelse, spillet udgiver), så den optager også i online-spil, ligesom offline; flaget afgør kun, om hukommelsen nogensinde må læses.
- Hukommelse: **aldrig** læst af denne adapter. Kun `memory`-adaptere læser hukommelse, og aldrig for et spil markeret som spillet online - se [Kilder og regler](sources-and-rules.md).

## Statistik der optages {#statistics-recorded}

Statistiknøglerne, som denne adapters kode sætter med navn (hver sessions `stats` i `meta.json` og tabellen `stats` i `watcher.sqlite`):

`best_lap`, `collisions`, `distance_km`, `fastest_laps`, `finishes`, `flashbacks`, `grid_position`, `laps`, `overtaken`, `overtakes`, `penalties`, `penalty_seconds`, `pit_stops`, `race_position`, `sessions`, `top_speed_kmh`, `wins`

En nøgle i klammer udfyldes under kørslen (`score.{team}` er én nøgle pr. hold). Nøgler som koden tager fra en tabel over spillets felter eller fra spillets egne statistiknavne står ikke på listen; "Hvad der optages" ovenfor nævner dem.

## Fuldstændighed {#completeness}

Watcheren følger 3DHeats [konverterregel](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md): det kilden indeholder bliver læst eller gemt, aldrig smidt væk. Ud over rækkerne gemmes hver pakke, side, linje eller svar adapteren modtager, helt i sessionens `heat.raw.parquet` (kolonnerne `time`, `ms`, `type`, `used`, `payload`, `text` og derefter felter der gemmes efter navn; `used` markerer det, der også blev til rækker), og `meta.json`s `selfCheck.completeness` tæller hver `type` - `lost` er 0.

**Læst**

- 0 Motion: hver bils verdensposition og hastighed, og nu også giering, stigning, rulning (grader, fra specifikationens radianer) og lateral-, længde- og lodret g-kraft, på hver bils positionsrækker
- 1 Session: bane, sessionstype, samlede omgange, banelængde, online eller ej (meta.json `sessions`)
- 2 Lap Data: sidste omgangstid, omgangsnummer, placering i løb og startgrid, pitstops, straffe, resultatstatus (omgange, mål, udgåelser, statistik)
- 3 Event: hver kode undtagen BUTN som sin egen række, med sine detaljer
- 4 Participants: førernavne, hold, antal aktive biler (rækkernes `player` og `team`, meta.json `drivers`)
- 6 Car Telemetry: hastighed, gear, gas, bremse, og nu også styring (-1..1), omdrejninger og DRS, på hver bils positionsrækker
- kontrolleret mod EA's offentliggjorte UDP-specifikationer for 2023-, 2024- og 2025-formaterne (pakkestørrelser påstået i testene); endnu ikke mod spillet

**Gemt rå**

- hver pakke helt i `heat.raw.parquet`, `payload` datagrammet, `type` dens id's navn: `motion`, `session`, `lap_data`, `event`, `participants`, `car_setups`, `car_telemetry`, `car_status`, `final_classification`, `lobby_info`, `car_damage`, `session_history`, `tyre_sets`, `motion_ex`, `time_trial`, `lap_positions` (`packet <n>` for et id specifikationerne endnu ikke lister); kolonnerne `format` (2023/2024/2025), `packet_id`, `frame`, `session_uid`
- `used` er sand for pakkerne læst ovenfor (Motion, Session, Lap Data, Participants, Car Telemetry, og Event-koder andet end BUTN); resten - bilopsætninger, bilstatus (brændstof, ERS, dækforbindelse og -alder, flag), slutklassement, lobby, bilskade, sessionshistorik (hver omgangs- og sektortid pr. bil), dæksæt, motion ex (den egne bils affjedring, hjulhastigheder, lokal hastighed, vinkelhastighed og acceleration), time trial, lap positions, BUTN-knaphændelser - gemmes til en senere afkoder
- `format <year>`: en pakke i et format før 2023 (et andet headerlayout), helt; `short`: et datagram kortere end den 29-byte header, helt

**Ikke tilgængeligt**

- andre spilleres brændstof, ERS, skade og dæksæt online, når deres "Your Telemetry" er begrænset: spillet sender nuller for dem
- pakker sendt, mens watcheren ikke kører, eller mens et andet program holder port 20777: UDP gemmes ikke af spillet

**Størrelse**: ved en sendehastighed på 60 Hz er hver pakke cirka 0,38 MB/s (Motion, Lap Data, Car Telemetry, Car Status og Motion Ex ved 60 Hz, Session History og Tyre Sets 20 gange i sekundet, Car Damage 10 gange i sekundet, Session og Car Setups 2 gange i sekundet) plus cirka 0,03 MB/s af pakkehoveder: cirka 1,5 GB i timen kørsel før komprimering, cirka 0,55 GB ved standarden på 20 Hz; zstd bringer det ned til en brøkdel af det (tomme bilpladser og gentagne værdier komprimeres godt; endnu ikke målt på en rigtig session)

## Verificeret {#verified}

testet på pakker i 2023-, 2024- og 2025-formaterne bygget ud fra EA's offentliggjorte specifikation, sendt over UDP; ikke testet mod spillet

## Kilde {#source}

[heat3d_watch/adapters/f1.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/f1.py)

<!-- Generated from the adapter by tools/gen_game_pages.py; change the adapter and run it again rather than editing this page. -->
