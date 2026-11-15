---
title: "EA SPORTS F1 25 (lifandi gögn)"
nav_order: 16
lang: "is"
source: game-f1-25.md
source_hash: "7476dbb3b308"
nav_exclude: true
search_exclude: true
---
# EA SPORTS F1 25 (lifandi gögn) {#ea-sports-f1-25-live-data}

Meðan þú spilar EA SPORTS F1 25 vistar watcher gögnin sem leikurinn sendir sjálfur út, svo þú getir skoðað þau síðar á korti í 3DHeat-skoðaranum.

*Tæknilegar upplýsingar: millistykki `f1-25`, gerð [`telemetry`](sources-and-rules.md); það keyrir meðan `F1_25.exe` er í gangi og leitar að nýjum gögnum á 0,1 s fresti.*

## Hvað er skráð {#what-is-recorded}

- staða hvers bíls (heimshnit XYZ, m) á 10 Hz, eftir nafni ökumanns, liði, eigin bíll merktur (`own_car` 1, úr vísi bíls spilarans), með hraða, gír, inngjöf, bremsu, stýri, snúningshraða (rpm), DRS, yaw, pitch, roll (gráður) og g-kröftum
- hringir á hvern bíl með hringtíma og keppnisstöðu; mark og úrsagnir
- keppnisatburðir leiksins: upphaf og endir lotu, hraðasti hringur, refsingar, framúrakstur, árekstrar, öryggisbíll, rautt flagg, ræsiljós, köflótt flagg, sigurvegari, flashbacks (`teleport` þar sem bíllinn var, `spawn` þangað sem hann fór aftur)
- braut, gerð lotu, hringir og ökumenn hverrar lotu
- eigin hringir, besti hringur, keppnis- og rásröðun, þjónustustopp (pit stops), refsingar, framúrakstur, árekstrar, vegalengd, hámarkshraði
- hver pakki sem leikurinn sendir, í heild, í `heat.raw.parquet` - líka þeir sem eru ekki lesnir í raðir

## Hvaðan það kemur {#where-it-comes-from}

UDP-fjarmæling 127.0.0.1:20777 (Documents\My Games\F1 25\hardwaresettings\hardware_settings_config.xml)

## Hvernig á að kveikja á því {#how-to-switch-it-on}

Í leiknum: Settings > Telemetry Settings > UDP Telemetry On, IP 127.0.0.1, port 20777 - eða `python -m heat3d_watch setup f1-25 --apply` (breytir hardware_settings_config.xml, tekur fyrst afrit; leikurinn þarf að vera lokaður). Meðan annað forrit heldur 20777 lætur watcher það hafa gáttina

Sláðu skipunina inn í terminal sem er opnaður í möppu watcher (sjá [Áður en þú byrjar](before-you-start.md)). Ef hún mistekst segir síðasta línan hvers vegna; [Uppsetning og keyrsla](installing-and-running.md) fer yfir algengustu orsakirnar.

`python -m heat3d_watch setup f1-25` sýnir þær skrár sem það myndi breyta; `python -m heat3d_watch setup f1-25 --apply` breytir þeim og geymir frumritið sem `<file>.heat3d-backup` (sjá [Skipanir](commands.md#setup)). Það skrifar `f1-25: changed: ...` fyrir hverja breytingu, eða `f1-25: nothing to change` þegar kveikt er nú þegar.

## Hvernig það virkar {#how-it-works}

EA SPORTS F1 23, F1 24 og F1 25: opinbera UDP-fjarmælingin, allir bílar á brautinni.

Leikirnir senda hana sjálfir (Settings > Telemetry Settings, eða
`Documents/My Games/<F1 xx>/hardwaresettings/hardware_settings_config.xml`,
`<udp enabled="true" ip="127.0.0.1" port="20777" sendRate="20" format="2025" ...>`).
Little-endian, pakkað, 29 bæta haus á hverjum pakka (sá sami í sniðunum 2023,
2024 og 2025):

```text
uint16 packetFormat, uint8 gameYear, gameMajorVersion, gameMinorVersion,
packetVersion, packetId, uint64 sessionUID, float sessionTime,
uint32 frameIdentifier, overallFrameIdentifier, uint8 playerCarIndex,
secondaryPlayerCarIndex
```

Það sem er lesið, eftir pakkaauðkenni:

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

Hver pakki er einnig geymdur í heild, eins og hann kom, í hráu hliðarskrá lotunnar
(`heat.raw.parquet`, `type` heiti pakkans - `motion`, `car_status` ... -
með `format`, `packet_id`, `frame` og `session_uid`) - bæði þeir sem eru lesnir hér að ofan og þeir sem
enginn les enn: 5 Car Setups, 7 Car Status, 8 Final Classification, 9 Lobby
Info, 10 Car Damage, 11 Session History, 12 Tyre Sets, 13 Motion Ex, 14 Time
Trial, 15 Lap Positions, öll síðari auðkenni, og pakkar á sniði sem þetta
les ekki. Síðari afkóðari þarf því aðeins hliðarskrána.

Staða hvers bíls er í Motion-pakkanum - líka á netinu, þar sem leikurinn
gefur hana sjálfur út (aðeins eldsneyti, ERS, skemmdir og dekkjasett eru haldin eftir
fyrir spilara sem hafa takmarkað "Your Telemetry"). Hver bíll er skráður á
um 10 Hz undir nafni þátttakanda ("car N" þar til nöfnin berast), liðið
með nafni, og bíll spilarans sjálfs merktur `own`.

Heimildir: "F1 25 UDP Specification" frá EA (forums.ea.com, F1 games info hub),
lýsingar F1 23 og F1 24; sömu töflur speglaðar í
MacManley/f1-25-udp (MIT). Pakkar í prófunum eru smíðaðir eftir þessum sniðum.

Sama eining þjónar líka: [EA SPORTS F1 23 (lifandi gögn)](game-f1-23.md), [EA SPORTS F1 24 (lifandi gögn)](game-f1-24.md).

## Staðsetningar og ásar {#positions-and-axes}

| | |
|---|---|
| Staðsetningar skráðar | já |
| Upp-ás | `y` |
| Einingar | metrar |
| Speglað fyrir skoðarann | ekkert |
| Einingakvarði (`scale`: skoðarinn margfaldar staðsetningar með honum) | 1 |

Þetta fer í `meta.json` (`axes`) hverrar lotu og, þegar lotan hefur staðsetningar, í fót `heat.parquet`, svo 3DHeat-skoðarinn snýr og kvarðar raðirnar sjálfur - sjá [Gögnin](the-data.md).

## Fjölspilun {#multiplayer}

- Merkt sem spilað á netinu (`multiplayer`): **já**. `games --markdown` sýnir þetta sem "allowed (reads only what the game publishes)".
- Gerð `telemetry`: það les aðeins það sem leikurinn eða vettvangurinn lætur í té (UDP-gátt eða samnýtt minni sem leikurinn birtir), svo það skráir bæði í netspilun og án nets; merkið ræður aðeins hvort minni megi nokkurn tíma lesa.
- Minni: **aldrei** lesið af þessu millistykki. Aðeins `memory`-millistykki lesa minni, og aldrei fyrir leik sem er merktur spilaður á netinu - sjá [Heimildir og reglur](sources-and-rules.md).

## Skráð tölfræði {#statistics-recorded}

Tölfræðilyklar sem kóði þessa millistykkis setur með nafni (`stats` hverrar lotu í `meta.json` og `stats`-taflan í `watcher.sqlite`):

`best_lap`, `collisions`, `distance_km`, `fastest_laps`, `finishes`, `flashbacks`, `grid_position`, `laps`, `overtaken`, `overtakes`, `penalties`, `penalty_seconds`, `pit_stops`, `race_position`, `sessions`, `top_speed_kmh`, `wins`

Lykill í slaufusvigum er fylltur út við keyrslu (`score.{team}` er einn lykill fyrir hvert lið). Lyklar sem kóðinn tekur úr töflu yfir reiti leiksins eða úr eigin tölfræðiheitum leiksins eru ekki á þessum lista; "Hvað er skráð" hér að ofan nefnir þá.

## Heilleiki {#completeness}

Watcher fylgir [breytireglu](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md) 3DHeat: það sem heimildin geymir er lesið eða varðveitt, aldrei sleppt. Auk raðanna er hver pakki, síða, lína eða svar sem millistykkið fær geymt í heild í `heat.raw.parquet` lotunnar (dálkarnir `time`, `ms`, `type`, `used`, `payload`, `text`, svo hver reitur sem geymdur er með nafni; `used` merkir það sem varð líka að röðum), og `selfCheck.completeness` í `meta.json` telur hvert `type` - `lost` er 0.

**Lesið**

- 0 Motion: heimsstaða og hraði hvers bíls, og nú einnig yaw, pitch, roll (gráður, úr radíönum í lýsingunni) og hliðar-, lengdar- og lóðrétt g-kraftur, á stöðuröðum hvers bíls
- 1 Session: braut, gerð lotu, heildarfjöldi hringja, lengd brautar, á netinu eða ekki (`sessions` í meta.json)
- 2 Lap Data: síðasti hringtími, hringnúmer, keppnis- og rásröðun, þjónustustopp, refsingar, niðurstöðustaða (hringir, mörk, úrsagnir, tölfræði)
- 3 Event: hver kóði nema BUTN sem sín eigin röð, með upplýsingum sínum
- 4 Participants: nöfn ökumanna, lið, fjöldi virkra bíla (`player` og `team` raðanna, `drivers` í meta.json)
- 6 Car Telemetry: hraði, gír, inngjöf, bremsa, og nú einnig stýri (-1..1), rpm og DRS, á stöðuröðum hvers bíls
- borið saman við útgefnar UDP-lýsingar EA fyrir sniðin 2023, 2024 og 2025 (pakkastærðir staðfestar í prófunum); ekki enn gegn leiknum

**Geymt óunnið**

- hver pakki í heild í `heat.raw.parquet`, `payload` er datagrammið, `type` heiti auðkennis þess: `motion`, `session`, `lap_data`, `event`, `participants`, `car_setups`, `car_telemetry`, `car_status`, `final_classification`, `lobby_info`, `car_damage`, `session_history`, `tyre_sets`, `motion_ex`, `time_trial`, `lap_positions` (`packet <n>` fyrir auðkenni sem lýsingarnar telja ekki enn upp); dálkarnir `format` (2023/2024/2025), `packet_id`, `frame`, `session_uid`
- `used` er satt fyrir pakkana sem eru lesnir hér að ofan (Motion, Session, Lap Data, Participants, Car Telemetry, og Event-kóða aðra en BUTN); hitt - car setups, car status (eldsneyti, ERS, gerð og aldur dekkja, merki), final classification, lobby, car damage, session history (hver hring- og sectortími á bíl), tyre sets, motion ex (fjöðrun eigin bíls, hjólahraði, staðbundinn hraði, snúningshraði og hröðun), time trial, lap positions, BUTN-hnappaatburðir - er geymt fyrir síðari afkóðara
- `format <year>`: pakki á sniði fyrir 2023 (annað hausskipulag), í heild; `short`: datagram styttra en 29 bæta hausinn, í heild

**Ekki tiltækt**

- eldsneyti, ERS, skemmdir og dekkjasett annarra spilara á netinu þegar "Your Telemetry" þeirra er takmarkað: leikurinn sendir núll fyrir þá
- pakkar sem eru sendir meðan watcher keyrir ekki, eða meðan annað forrit heldur gátt 20777: leikurinn geymir ekki UDP

**Stærð**: við sendingartíðni 60 Hz er hver pakki um 0,38 MB/s (Motion, Lap Data, Car Telemetry, Car Status og Motion Ex á 60 Hz, Session History og Tyre Sets á 20/s, Car Damage á 10/s, Session og Car Setups á 2/s) auk um 0,03 MB/s af atriðahausum: um 1,5 GB á klukkustund af akstri fyrir þjöppun, um 0,55 GB við sjálfgefin 20 Hz; zstd minnkar það niður í brot af því (tóm bílasæti og endurtekin gildi þjappast vel; ekki enn mælt á raunverulegri lotu)

## Staðfest {#verified}

prófað á pökkum á sniðunum 2023, 2024 og 2025 smíðuðum eftir útgefinni lýsingu EA, sendum yfir UDP; óprófað gegn leiknum

## Heimild {#source}

[heat3d_watch/adapters/f1.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/f1.py)

<!-- Generated from the adapter by tools/gen_game_pages.py; change the adapter and run it again rather than editing this page. -->
