---
title: "EA SPORTS F1 24 (livedata)"
nav_order: 15
lang: "sv"
source: game-f1-24.md
source_hash: "a189298930fc"
nav_exclude: true
search_exclude: true
---
# EA SPORTS F1 24 (livedata) {#ea-sports-f1-24-live-data}

Medan du spelar EA SPORTS F1 24 sparar watchern den data som spelet själv skickar ut, så att du senare kan titta på den på en karta i 3DHeat-visaren.

*Teknisk information: adaptern `f1-24`, typ [`telemetry`](sources-and-rules.md); den körs medan `F1_24.exe` är igång och letar efter ny data var 0,1 s.*

## Vad som spelas in {#what-is-recorded}

- varje bils position (världens XYZ, m) 10 gånger per sekund, efter förarens namn, lag, egen bil markerad (`own_car` 1, från spelarbilens index), med hastighet, växel, gas, broms, styrning, varvtal, DRS, gir, stigning, rulle (grader) och g-krafter
- varv per bil med varvtiden och placeringen i loppet; målgångar och uppgivanden
- spelets lopphändelser: sessionens start och slut, snabbaste varv, straff, omkörningar, kollisioner, säkerhetsbil, röd flagg, startlampor, rutig flagg, vinnare, flashbacks (`teleport` där bilen var, `spawn` dit den gick tillbaka)
- bana, sessionstyp, varv och förare i varje session
- egna varv, bästa varv, lopp- och startplacering, depåstopp, straff, omkörningar, kollisioner, sträcka, högsta hastighet
- varje paket spelet skickar, helt, i `heat.raw.parquet` - även de som inte läses in som rader

## Varifrån det kommer {#where-it-comes-from}

UDP-telemetri 127.0.0.1:20777 (Dokument\My Games\F1 24\hardwaresettings\hardware_settings_config.xml)

## Så slår du på det {#how-to-switch-it-on}

I spelet: Inställningar > Telemetriinställningar > UDP-telemetri på, IP 127.0.0.1, port 20777 - eller `python -m heat3d_watch setup f1-24 --apply` (ändrar hardware_settings_config.xml, säkerhetskopieras först; spelet måste vara stängt). Medan ett annat program har port 20777 lämnar watchern porten åt det

Skriv kommandot i en terminal som är öppen i watcherns mapp (se [Innan du börjar](before-you-start.md)). Om det misslyckas säger sista raden varför; [Installera och köra](installing-and-running.md) beskriver de vanligaste orsakerna.

`python -m heat3d_watch setup f1-24` visar vilka filer som skulle ändras; `python -m heat3d_watch setup f1-24 --apply` ändrar dem och sparar originalet som `<file>.heat3d-backup` (se [Kommandon](commands.md#setup)). Den skriver `f1-24: changed: ...` för varje ändring, eller `f1-24: nothing to change` när det redan är på.

## Så fungerar det {#how-it-works}

EA SPORTS F1 23, F1 24 och F1 25: den officiella UDP-telemetrin, varje bil på banan.

Spelen skickar den själva (Inställningar > Telemetriinställningar, eller `Dokument/My Games/<F1 xx>/hardwaresettings/hardware_settings_config.xml`, `<udp enabled="true" ip="127.0.0.1" port="20777" sendRate="20" format="2025" ...>`). Little-endian, packat, en 29-byte header på varje paket (samma i formaten 2023, 2024 och 2025):

```text
uint16 packetFormat, uint8 gameYear, gameMajorVersion, gameMinorVersion,
packetVersion, packetId, uint64 sessionUID, float sessionTime,
uint32 frameIdentifier, overallFrameIdentifier, uint8 playerCarIndex,
secondaryPlayerCarIndex
```

Vad som läses, efter paket-id:

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

Varje paket sparas också helt, som det kom, i sessionens råa sidovagn (`heat.raw.parquet`, `type` är paketets namn - `motion`, `car_status` ... - med `format`, `packet_id`, `frame` och `session_uid`) - de som lästs ovan och de som ingenting läser ännu: 5 Car Setups, 7 Car Status, 8 Final Classification, 9 Lobby Info, 10 Car Damage, 11 Session History, 12 Tyre Sets, 13 Motion Ex, 14 Time Trial, 15 Lap Positions, alla senare id:n, och paket i ett format som inte läses. En senare avkodare behöver alltså bara sidovagnen.

Varje bils position finns i Motion-paketet - även online, där spelet själv lämnar ut den (bara bränsle-, ERS-, skade- och däckdata hålls tillbaka för spelare vars "Din telemetri" är begränsad). Varje bil spelas in i cirka 10 Hz under sitt deltagarnamn ("car N" tills namnen kommer), laget med namn, och spelarens egen bil markerad `own`.

Källor: EA:s "F1 25 UDP Specification" (forums.ea.com, F1-spelens infohubb), specifikationerna för F1 23 och F1 24; samma tabeller speglade i MacManley/f1-25-udp (MIT). Paket i testerna byggs från dessa layouter.

Samma modul används också av: [EA SPORTS F1 23 (livedata)](game-f1-23.md), [EA SPORTS F1 25 (livedata)](game-f1-25.md).

## Positioner och axlar {#positions-and-axes}

| | |
|---|---|
| Positioner sparas | ja |
| Uppåtaxel | `y` |
| Enheter | meter |
| Speglad för visaren | ingen |
| Enhetsskala (`scale`: visaren multiplicerar positionerna med den) | 1 |

Dessa läggs i varje sessions `meta.json` (`axes`) och, när sessionen har positioner, i `heat.parquet`:s footer, så att 3DHeat-visaren vrider och skalar raderna själv - se [Datan](the-data.md).

## Multiplayer {#multiplayer}

- Markerad som spelad online (`multiplayer`): **ja**. `games --markdown` visar detta som "tillåten (läser bara det spelet publicerar)".
- Typ `telemetry`: den läser bara det spelet eller plattformen lämnar ut (en UDP-port eller delat minne som spelet publicerar), så den spelar in även i onlinespel så väl som offline; flaggan avgör bara om minnet någonsin får läsas.
- Minne: läses **aldrig** av den här adaptern. Bara `memory`-adaptrar läser minne, och aldrig för ett spel som är markerat som spelat online - se [Källor och regler](sources-and-rules.md).

## Statistik som sparas {#statistics-recorded}

Statistiknycklar som adapterns kod sätter med namn (varje sessions `stats` i `meta.json` och tabellen `stats` i `watcher.sqlite`):

`best_lap`, `collisions`, `distance_km`, `fastest_laps`, `finishes`, `flashbacks`, `grid_position`, `laps`, `overtaken`, `overtakes`, `penalties`, `penalty_seconds`, `pit_stops`, `race_position`, `sessions`, `top_speed_kmh`, `wins`

En nyckel inom klammerparenteser fylls i vid körning (`score.{team}` är en nyckel per lag). Nycklar som koden tar från en tabell med spelets fält eller från spelets egna statistiknamn finns inte med i den här listan; "Vad som spelas in" ovan nämner dem.

## Fullständighet {#completeness}

Watchern följer 3DHeats [omvandlarregel](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md): det källan innehåller läses eller sparas, aldrig slängs. Utöver raderna sparas varje paket, sida, rad eller svar som adaptern tar emot helt i sessionens `heat.raw.parquet` (kolumnerna `time`, `ms`, `type`, `used`, `payload`, `text`, plus eventuella fält som sparas med namn; `used` markerar det som också blev rader), och `meta.json`:s `selfCheck.completeness` räknar varje `type` - `lost` är 0.

**Läses**

- 0 Motion: varje bils världsposition och hastighet, och nu även gir, stigning, rulle (grader, från specifikationens radianer) och lateral-, longitudinell- och vertikal g-kraft, på varje bils positionsrader
- 1 Session: bana, sessionstyp, totalt antal varv, banlängd, online eller inte (meta.json `sessions`)
- 2 Lap Data: senaste varvtid, varvnummer, lopp- och startplacering, depåstopp, straff, resultatstatus (varv, målgångar, uppgivanden, statistik)
- 3 Event: varje kod utom BUTN som en egen rad, med sina detaljer
- 4 Participants: förarnamn, lag, antal aktiva bilar (radernas `player` och `team`, meta.json `drivers`)
- 6 Car Telemetry: hastighet, växel, gas, broms, och nu även styrning (-1..1), varvtal och DRS, på varje bils positionsrader
- kontrollerat mot EA:s publicerade UDP-specifikationer för formaten 2023, 2024 och 2025 (paketstorlekar kontrollerade i testerna); ännu inte mot spelet

**Sparas råa**

- varje paket helt i `heat.raw.parquet`, `payload` är datagrammet, `type` är id:ts namn: `motion`, `session`, `lap_data`, `event`, `participants`, `car_setups`, `car_telemetry`, `car_status`, `final_classification`, `lobby_info`, `car_damage`, `session_history`, `tyre_sets`, `motion_ex`, `time_trial`, `lap_positions` (`packet <n>` för ett id som specifikationerna inte listar ännu); kolumnerna `format` (2023/2024/2025), `packet_id`, `frame`, `session_uid`
- `used` är sant för paketen som lästs ovan (Motion, Session, Lap Data, Participants, Car Telemetry, och Event-koder utom BUTN); resten - bilinställningar, bilstatus (bränsle, ERS, däckmix och ålder, flaggor), slutresultat, lobby, bilskador, sessionshistorik (varje varv- och sektortid per bil), däckuppsättningar, motion ex (egen bils fjädring, hjulhastigheter, lokal hastighet, vinkelhastighet och acceleration), time trial, lap positions, BUTN-knapphändelser - sparas för en senare avkodare
- `format <year>`: ett paket i ett format före 2023 (annan headerlayout), helt; `short`: ett datagram kortare än 29-byte-headern, helt

**Inte tillgängligt**

- andra spelares bränsle, ERS, skador och däckuppsättningar online när deras "Din telemetri" är begränsad: spelet skickar nollor för dem
- paket som skickas medan watchern inte körs, eller medan ett annat program har port 20777: UDP lagras inte av spelet

**Storlek**: vid en skickfrekvens på 60 Hz är varje paket cirka 0,38 MB/s (Motion, Lap Data, Car Telemetry, Car Status och Motion Ex 60 gånger per sekund, Session History och Tyre Sets 20 per sekund, Car Damage 10 per sekund, Session och Car Setups 2 per sekund) plus cirka 0,03 MB/s av postrubriker: cirka 1,5 GB per timme körning före komprimering, cirka 0,55 GB vid standarden 20 Hz; zstd gör det till en bråkdel av det (tomma bilplatser och upprepade värden komprimeras väl; inte ännu mätt på en riktig session)

## Verifierad {#verified}

testad på paket i formaten 2023, 2024 och 2025 byggda från EA:s publicerade specifikation, skickade över UDP; inte testad mot spelet

## Källa {#source}

[heat3d_watch/adapters/f1.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/f1.py)

<!-- Generated from the adapter by tools/gen_game_pages.py; change the adapter and run it again rather than editing this page. -->
