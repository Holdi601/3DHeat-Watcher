---
title: "EA SPORTS F1 24 (live data)"
nav_order: 15
lang: "nl"
source: game-f1-24.md
source_hash: "a189298930fc"
nav_exclude: true
search_exclude: true
---
# EA SPORTS F1 24 (live data) {#ea-sports-f1-24-live-data}

Terwijl je EA SPORTS F1 24 speelt, slaat de watcher de data op die het spel zelf uitstuurt. Zo kun je die later op een kaart in de 3DHeat-viewer bekijken.

*Technische details: adapter `f1-24`, soort [`telemetry`](sources-and-rules.md); hij draait zolang `F1_24.exe` actief is en zoekt elke 0,1 s naar nieuwe gegevens.*

## Wat wordt opgenomen {#what-is-recorded}

- de positie van elke auto (wereld-XYZ, m) tien keer per seconde, per coureursnaam, team, de eigen auto gemarkeerd (`own_car` 1, uit de index van de speler-auto); met snelheid, versnelling, gas, rem, stuur, toerental, DRS, gier, stamp, rol (graden) en g-krachten
- ronden per auto met de rondetijd en de positie in de race; finishes en uitvallen
- de raceonderdelen van het spel: begin en einde van de sessie, snelste ronde, straffen, inhaalacties, botsingen, safety car, rode vlag, startlichten, finishvlag, winnaar, flashbacks (`teleport` waar de auto was, `spawn` waar hij naartoe ging)
- baan, sessietype, ronden en coureurs van elke sessie
- eigen ronden, beste ronde, positie in de race en op de grid, pitstops, straffen, inhaalacties, botsingen, afstand, topsnelheid
- elk pakket dat het spel stuurt, heel, in `heat.raw.parquet` - ook de pakketten die niet in rijen gelezen worden

## Waar het vandaan komt {#where-it-comes-from}

UDP-telemetrie 127.0.0.1:20777 (Documents\My Games\F1 24\hardwaresettings\hardware_settings_config.xml)

## Zo zet je het aan {#how-to-switch-it-on}

In het spel: Instellingen > Telemetrie-instellingen > UDP-telemetrie aan, IP 127.0.0.1, poort 20777 - of `python -m heat3d_watch setup f1-24 --apply` (past hardware_settings_config.xml aan, eerst een back-up; het spel moet dicht zijn). Zolang een andere app poort 20777 vasthoudt, laat de watcher de poort aan die app over

Typ het commando in een terminal die geopend is in de map van de watcher (zie [Voordat je begint](before-you-start.md)). Als het mislukt, zegt de laatste regel waarom. [Installeren en uitvoeren](installing-and-running.md) beschrijft de gewone oorzaken.

`python -m heat3d_watch setup f1-24` laat zien welke bestanden het zou wijzigen. `python -m heat3d_watch setup f1-24 --apply` wijzigt ze en bewaart het origineel als `<file>.heat3d-backup` (zie [Commando's](commands.md#setup)). Het toont `f1-24: changed: ...` voor elke wijziging, of `f1-24: nothing to change` als het al aan staat.

## Hoe het werkt {#how-it-works}

EA SPORTS F1 23, F1 24 en F1 25: de officiële UDP-telemetrie, elke auto op de baan.

Het spel stuurt die zelf (Instellingen > Telemetrie-instellingen, of
`Documents/My Games/<F1 xx>/hardwaresettings/hardware_settings_config.xml`,
`<udp enabled="true" ip="127.0.0.1" port="20777" sendRate="20" format="2025" ...>`).
Little-endian, gepakt, een kop van 29 bytes op elk pakket (hetzelfde in de formaten 2023,
2024 en 2025):

```text
uint16 packetFormat, uint8 gameYear, gameMajorVersion, gameMinorVersion,
packetVersion, packetId, uint64 sessionUID, float sessionTime,
uint32 frameIdentifier, overallFrameIdentifier, uint8 playerCarIndex,
secondaryPlayerCarIndex
```

Wat er gelezen wordt, per pakket-id:

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

Elk pakket wordt ook heel bewaard, zoals het binnenkwam, in de ruwe bijlage van de sessie (`heat.raw.parquet`, `type` de naam van het pakket - `motion`, `car_status` ... - met `format`, `packet_id`, `frame` en `session_uid`) - de pakketten die hierboven gelezen worden en die welke nog niets leest: 5 Car Setups, 7 Car Status, 8 Final Classification, 9 Lobby Info, 10 Car Damage, 11 Session History, 12 Tyre Sets, 13 Motion Ex, 14 Time Trial, 15 Lap Positions, elk later id, en pakketten in een formaat dat dit niet leest. Zo heeft een latere decoder alleen de bijlage nodig.

Elke positie van elke auto zit in het Motion-pakket - ook online, waar het spel het zelf uitgeeft (alleen brandstof, ERS, schade en banden-gegevens worden achtergehouden bij spelers van wie "Your Telemetry" beperkt is). Elke auto wordt ongeveer 10 keer per seconde vastgelegd onder zijn naam van de deelnemer ("car N" tot de namen binnenkomen), het team bij naam, en de auto van de speler gemarkeerd als `own`.

Bronnen: EA's "F1 25 UDP Specification" (forums.ea.com, F1 games info hub),
de F1 23- en F1 24-specificaties; dezelfde tabellen gespiegeld in
MacManley/f1-25-udp (MIT). Pakketten in tests zijn gebouwd uit deze indelingen.

Dezelfde module levert ook: [EA SPORTS F1 23 (live data)](game-f1-23.md), [EA SPORTS F1 25 (live data)](game-f1-25.md).

## Posities en assen {#positions-and-axes}

| | |
|---|---|
| Posities opgenomen | ja |
| Omhoog-as | `y` |
| Eenheden | meter |
| Gespiegeld voor de viewer | geen |
| Eenheidsschaal (`scale`: de viewer vermenigvuldigt posities ermee) | 1 |

Deze gaan in het `meta.json` (`axes`) van elke sessie en, als de sessie posities heeft, in de footer van `heat.parquet`. Zo draait en schaalt de 3DHeat-viewer de rijen zelf - zie [De gegevens](the-data.md).

## Meerspelers {#multiplayer}

- Gemarkeerd als online gespeeld (`multiplayer`): **ja**. `games --markdown` toont dit als "allowed (reads only what the game publishes)".
- Soort `telemetry`: het leest alleen wat het spel of platform uitgeeft (een UDP-poort of gedeeld geheugen dat het spel publiceert), dus het legt ook online spel vast, net als offline. De vlag bepaalt alleen of geheugen ooit gelezen mag worden.
- Geheugen: wordt door deze adapter **nooit** gelezen. Alleen `memory`-adapters lezen geheugen, en nooit voor een spel dat als online gespeeld is gemarkeerd - zie [Bronnen en regels](sources-and-rules.md).

## Opgenomen statistieken {#statistics-recorded}

Statistiekensleutels die de code van deze adapter bij naam zet (de `stats` van elke sessie in `meta.json` en de tabel `stats` in `watcher.sqlite`):

`best_lap`, `collisions`, `distance_km`, `fastest_laps`, `finishes`, `flashbacks`, `grid_position`, `laps`, `overtaken`, `overtakes`, `penalties`, `penalty_seconds`, `pit_stops`, `race_position`, `sessions`, `top_speed_kmh`, `wins`

Een sleutel tussen accolades wordt tijdens het draaien ingevuld (`score.{team}` is een sleutel per team). Sleutels die de code uit een tabel met velden van het spel of uit de eigen statistiekennamen van het spel haalt, staan niet in deze lijst; "Wat wordt opgenomen" hierboven noemt die wel.

## Volledigheid {#completeness}

De watcher volgt de [converterregel](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md) van 3DHeat: wat de bron bevat, wordt gelezen of bewaard, nooit weggegooid. Naast de rijen wordt elk pakket, elke pagina, regel of antwoord dat de adapter ontvangt, heel bewaard in `heat.raw.parquet` van de sessie (kolommen `time`, `ms`, `type`, `used`, `payload`, `text`, plus elk veld dat op naam bewaard is; `used` markeert wat ook rijen werd). De `selfCheck.completeness` in `meta.json` telt elk `type` - `lost` is 0.

**Gelezen**

- 0 Motion: de wereldpositie en -snelheid van elke auto, en nu ook gier, stamp, rol (graden, van de radialen in de specificatie) en de laterale, longitudinale en verticale g-kracht, op de positierijen van elke auto
- 1 Session: baan, sessietype, totaal aantal ronden, lengte van de baan, online of niet (`sessions` in meta.json)
- 2 Lap Data: laatste rondetijd, rondenummer, positie in de race en op de grid, pitstops, straffen, eindresultaat (ronden, finishes, uitvallen, statistieken)
- 3 Event: elke code behalve BUTN als eigen rij, met zijn details
- 4 Participants: namen van coureurs, teams, aantal actieve auto's (`player` en `team` van de rijen, `drivers` in meta.json)
- 6 Car Telemetry: snelheid, versnelling, gas, rem, en nu ook stuur (-1..1), toerental en DRS, op de positierijen van elke auto
- gecontroleerd tegen de gepubliceerde UDP-specificaties van EA voor de formaten 2023, 2024 en 2025 (pakketgroottes getest in de tests); nog niet tegen het spel

**Heel bewaard**

- elk pakket heel in `heat.raw.parquet`, `payload` het datagram, `type` de naam van zijn id: `motion`, `session`, `lap_data`, `event`, `participants`, `car_setups`, `car_telemetry`, `car_status`, `final_classification`, `lobby_info`, `car_damage`, `session_history`, `tyre_sets`, `motion_ex`, `time_trial`, `lap_positions` (`packet <n>` voor een id dat de specificaties nog niet noemen); kolommen `format` (2023/2024/2025), `packet_id`, `frame`, `session_uid`
- `used` is true voor de pakketten die hierboven gelezen worden (Motion, Session, Lap Data, Participants, Car Telemetry, en Event-codes behalve BUTN); de rest - auto-opstellingen, auto-status (brandstof, ERS, bandensoort en -leeftijd, vlaggen), eindklassement, lobby, autoschade, sessiegeschiedenis (elke ronde- en sectortijd per auto), bandensets, motion ex (de ophanging, wielsnelheden, lokale snelheid, hoeksnelheid en versnelling van de eigen auto), time trial, rondeposities, BUTN-knopgebeurtenissen - wordt voor een latere decoder bewaard
- `format <year>`: een pakket in een formaat van voor 2023 (andere kopindeling), heel; `short`: een datagram korter dan de kop van 29 bytes, heel

**Niet beschikbaar**

- brandstof, ERS, schade en bandensets van andere spelers online wanneer hun "Your Telemetry" beperkt is: het spel stuurt nullen voor hen
- pakketten die verstuurd worden terwijl de watcher niet draait, of terwijl een andere app poort 20777 vasthoudt: UDP wordt door het spel niet opgeslagen

**Grootte**: bij een verzendsnelheid van 60 Hz is elk pakket samen ongeveer 0,38 MB/s (Motion, Lap Data, Car Telemetry, Car Status en Motion Ex op 60 Hz, Session History en Tyre Sets 20 keer per seconde, Car Damage 10 keer per seconde, Session en Car Setups 2 keer per seconde) plus ongeveer 0,03 MB/s aan itemkoppen: ongeveer 1,5 GB per uur rijden vóór compressie, ongeveer 0,55 GB bij de standaard 20 Hz; zstd brengt het terug tot een fractie daarvan (lege autoplaatsen en herhaalde waarden comprimeren goed; nog niet gemeten op een echte sessie)

## Geverifieerd {#verified}

getest op pakketten in de formaten 2023, 2024 en 2025, gebouwd uit de gepubliceerde specificatie van EA, verstuurd over UDP; niet getest tegen het spel

## Bron {#source}

[heat3d_watch/adapters/f1.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/f1.py)

<!-- Gegenereerd uit de adapter door tools/gen_game_pages.py; wijzig de adapter en voer het opnieuw uit in plaats van deze pagina te bewerken. -->
