---
title: "EA SPORTS F1 25 (direkte data)"
nav_order: 16
lang: "no"
source: game-f1-25.md
source_hash: "7476dbb3b308"
nav_exclude: true
search_exclude: true
---
# EA SPORTS F1 25 (direkte data) {#ea-sports-f1-25-live-data}

Mens du spiller EA SPORTS F1 25, lagrer watcheren dataene spillet selv sender ut, slik at du senere kan se på dem på et kart i 3DHeat-vieweren.

*Tekniske detaljer: adapter `f1-25`, type [`telemetry`](sources-and-rules.md); den kjører mens `F1_25.exe` går og ser etter nye data hvert 0,1 s.*

## Hva som tas opp {#what-is-recorded}

- hver bils posisjon (verden XYZ, m) 10 ganger i sekundet, etter førernavn, lag, egen bil markert (`own_car` 1, fra spillerens bilindeks), med fart, gir, gass, brems, styring, turtall, DRS, gir, stigning, rulling (grader) og g-krefter
- runder per bil med rundetid og løpsposisjon; målgang og oppgivelser
- spillets løpshendelser: øktstart og -slutt, raskeste runde, straffer, forbikjøringer, kollisjoner, sikkerhetsbil, rødt flagg, startlys, målflagg, vinner, tilbakespoling (`teleport` der bilen var, `spawn` der den ble satt tilbake)
- bane, øktype, runder og førere i hver økt
- egne runder, beste runde, løps- og startposisjon, pitstopp, straffer, forbikjøringer, kollisjoner, distanse, toppfart
- hver pakke spillet sender, hel, i `heat.raw.parquet` - også de som ikke leses inn i rader

## Hvor det kommer fra {#where-it-comes-from}

UDP-telemetri 127.0.0.1:20777 (Documents\My Games\F1 25\hardwaresettings\hardware_settings_config.xml)

## Slik slår du det på {#how-to-switch-it-on}

I spillet: Settings > Telemetry Settings > UDP Telemetry On, IP 127.0.0.1, port 20777 - eller `python -m heat3d_watch setup f1-25 --apply` (endrer hardware_settings_config.xml, sikkerhetskopiert først; spillet må være lukket). Mens et annet program holder 20777, lar watcheren porten være hos det

Skriv kommandoen i en terminal som er åpnet i watcher-mappen (se [Før du starter](before-you-start.md)). Hvis den feiler, sier siste linje hvorfor. [Installere og kjøre](installing-and-running.md) dekker de vanlige årsakene.

`python -m heat3d_watch setup f1-25` lister filene den ville endret. `python -m heat3d_watch setup f1-25 --apply` endrer dem og tar vare på originalen som `<file>.heat3d-backup` (se [Kommandoer](commands.md#setup)). Den skriver `f1-25: changed: ...` for hver endring, eller `f1-25: nothing to change` når det allerede er slått på.

## Slik fungerer det {#how-it-works}

EA SPORTS F1 23, F1 24 og F1 25: den offisielle UDP-telemetrien, hver bil på banen.

Spillene sender den selv (Settings > Telemetry Settings, eller `Documents/My Games/<F1 xx>/hardwaresettings/hardware_settings_config.xml`, `<udp enabled="true" ip="127.0.0.1" port="20777" sendRate="20" format="2025" ...>`). Little-endian, pakket, en 29-byte header på hver pakke (den samme i formatene 2023, 2024 og 2025):

```text
uint16 packetFormat, uint8 gameYear, gameMajorVersion, gameMinorVersion,
packetVersion, packetId, uint64 sessionUID, float sessionTime,
uint32 frameIdentifier, overallFrameIdentifier, uint8 playerCarIndex,
secondaryPlayerCarIndex
```

Det som leses, etter pakke-id:

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

Hver pakke tas også vare på hel, slik den kom, i øktens rå sidefil (`heat.raw.parquet`, `type` er pakkens navn - `motion`, `car_status` ... - med `format`, `packet_id`, `frame` og `session_uid`) - de som leses over, og de ingenting leser ennå: 5 Car Setups, 7 Car Status, 8 Final Classification, 9 Lobby Info, 10 Car Damage, 11 Session History, 12 Tyre Sets, 13 Motion Ex, 14 Time Trial, 15 Lap Positions, alle senere id-er, og pakker i et format som dette ikke leser. En senere dekoder trenger altså bare sidefilen.

Hver bils posisjon står i Motion-pakken - også på nett, der spillet selv gir den ut (bare drivstoff, ERS, skade og dekksett holdes tilbake for spillere med begrenset "Your Telemetry"). Hver bil tas opp omtrent 10 Hz under sitt deltakernavn ("car N" til navnene kommer), laget med navn, og spillerens egen bil markert `own`.

Kilder: EAs "F1 25 UDP Specification" (forums.ea.com, F1 games info hub), F1 23- og F1 24-spesifikasjonene; de samme tabellene speilet i MacManley/f1-25-udp (MIT). Testpakker er bygget fra disse oppsettene.

Samme modul brukes også av: [EA SPORTS F1 23 (direkte data)](game-f1-23.md), [EA SPORTS F1 24 (direkte data)](game-f1-24.md).

## Posisjoner og akser {#positions-and-axes}

| | |
|---|---|
| Posisjoner registreres | ja |
| Opp-akse | `y` |
| Enheter | meter |
| Speilet for visningen | ingen |
| Enhetsskala (`scale`: visningen ganger posisjonene med den) | 1 |

Disse havner i hver økts `meta.json` (`axes`) og, når økten har posisjoner, i `heat.parquet`s footer, slik at 3DHeat-vieweren snur og skalerer radene selv - se [Dataene](the-data.md).

## Flerspiller {#multiplayer}

- Merket som spilt på nett (`multiplayer`): **ja**. `games --markdown` viser dette som "allowed (reads only what the game publishes)".
- Type `telemetry`: den leser bare det spillet eller plattformen gir ut (en UDP-port eller delt minne som spillet publiserer), så den tar opp også i nettspill, både på nett og offline; flagget avgjør bare om minnet noen gang kan leses.
- Minne: **aldri** lest av denne adapteren. Bare `memory`-adaptere leser minne, og aldri for et spill som er merket som spilt på nett - se [Kilder og regler](sources-and-rules.md).

## Statistikk som registreres {#statistics-recorded}

Statistikknøkler som denne adapterens kode setter med navn (hver økts `stats` i `meta.json` og tabellen `stats` i `watcher.sqlite`):

`best_lap`, `collisions`, `distance_km`, `fastest_laps`, `finishes`, `flashbacks`, `grid_position`, `laps`, `overtaken`, `overtakes`, `penalties`, `penalty_seconds`, `pit_stops`, `race_position`, `sessions`, `top_speed_kmh`, `wins`

En nøkkel i klammer fylles ut ved kjøretid (`score.{team}` er én nøkkel per lag). Nøkler som koden henter fra en tabell over spillets felt eller fra spillets egne statistikknavn står ikke i denne listen; "Hva som tas opp" over nevner dem.

## Fullstendighet {#completeness}

Watcheren følger 3DHeats [konverteringsregel](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md): det kilden inneholder, leses eller tas vare på, og slettes aldri. I tillegg til radene tas hver pakke, side, linje eller svar adapteren mottar, vare på hel i øktens `heat.raw.parquet` (kolonnene `time`, `ms`, `type`, `used`, `payload`, `text`, pluss felt som tas vare på med navn; `used` markerer det som også ble til rader), og `selfCheck.completeness` i `meta.json` teller hver `type` - `lost` er 0.

**Leses**

- 0 Motion: hver bils verdensposisjon og hastighet, og nå også stigning, rulling, gir (grader, fra spesifikasjonens radianer) og side-, lengde- og vertikal g-kraft, på hver bils posisjonsrader
- 1 Session: bane, øktype, totalt antall runder, banelengde, på nett eller ikke (meta.json `sessions`)
- 2 Lap Data: siste rundetid, rundenummer, løps- og startposisjon, pitstopp, straffer, resultatstatus (runder, målgang, oppgivelser, statistikk)
- 3 Event: hver kode unntatt BUTN som en egen rad, med detaljene sine
- 4 Participants: førernavn, lag, antall aktive biler (radenes `player` og `team`, meta.json `drivers`)
- 6 Car Telemetry: fart, gir, gass, brems, og nå også styring (-1..1), turtall og DRS, på hver bils posisjonsrader
- sjekket mot EAs publiserte UDP-spesifikasjoner for formatene 2023, 2024 og 2025 (pakkestørrelser påstått i testene); ikke ennå mot spillet

**Tatt vare på rått**

- hver pakke hel i `heat.raw.parquet`, `payload` er datagrammet, `type` er id-ens navn: `motion`, `session`, `lap_data`, `event`, `participants`, `car_setups`, `car_telemetry`, `car_status`, `final_classification`, `lobby_info`, `car_damage`, `session_history`, `tyre_sets`, `motion_ex`, `time_trial`, `lap_positions` (`packet <n>` for en id spesifikasjonene ikke lister ennå); kolonnene `format` (2023/2024/2025), `packet_id`, `frame`, `session_uid`
- `used` er sann for pakkene som leses over (Motion, Session, Lap Data, Participants, Car Telemetry, og Event-koder unntatt BUTN); resten - bilsetup, bilstatus (drivstoff, ERS, dekkblanding og -alder, flagg), sluttklassement, lobby, bilskade, øktens historikk (hver runde- og sektortid per bil), dekksett, motion ex (den egne bilens fjæring, hjulhastigheter, lokal hastighet, vinkelhastighet og akselerasjon), time trial, lap positions, BUTN-knapphendelser - tas vare på for en senere dekoder
- `format <year>`: en pakke i et format før 2023 (et annet headeroppsett), hel; `short`: et datagram kortere enn 29-byte-headeren, helt

**Ikke tilgjengelig**

- andre spilleres drivstoff, ERS, skade og dekksett på nett når deres "Your Telemetry" er begrenset: spillet sender nuller for dem
- pakker sendt mens watcheren ikke kjører, eller mens et annet program holder port 20777: UDP lagres ikke av spillet

**Størrelse**: ved en sendefrekvens på 60 Hz er hver pakke omtrent 0,38 MB/s (Motion, Lap Data, Car Telemetry, Car Status og Motion Ex på 60 Hz, Session History og Tyre Sets 20 ganger i sekundet, Car Damage 10 ganger, Session og Car Setups 2 ganger) pluss omtrent 0,03 MB/s med elementoverskrifter: omtrent 1,5 GB per time med kjøring før komprimering, omtrent 0,55 GB ved standard 20 Hz; zstd gir en brøkdel av det (tomme bilplasser og gjentatte verdier komprimeres godt; ikke målt på en ekte økt ennå)

## Verifisert {#verified}

testet på pakker i formatene 2023, 2024 og 2025 bygget fra EAs publiserte spesifikasjon, sendt over UDP; ikke testet mot spillet

## Kilde {#source}

[heat3d_watch/adapters/f1.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/f1.py)

<!-- Generated from the adapter by tools/gen_game_pages.py; change the adapter and run it again rather than editing this page. -->
