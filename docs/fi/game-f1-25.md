---
title: "EA SPORTS F1 25 (live-data)"
nav_order: 16
lang: "fi"
source: game-f1-25.md
source_hash: "7476dbb3b308"
nav_exclude: true
search_exclude: true
---
# EA SPORTS F1 25 (live-data) {#ea-sports-f1-25-live-data}

Kun pelaat EA SPORTS F1 25:tä, watcher tallentaa pelin lähettämän datan, jotta voit myöhemmin katsoa sen kartalla 3DHeat-katselimessa.

*Tekniset tiedot: adapteri `f1-25`, tyyppi [`telemetry`](sources-and-rules.md); se toimii, kun `F1_25.exe` on käynnissä, ja etsii uutta dataa 0,1 s välein.*

## Mitä tallennetaan {#what-is-recorded}

- jokaisen auton sijainti (maailman XYZ, m) 10 Hz:n taajuudella, kuljettajan nimen, tiimin ja oman auton mukaan (`own_car` 1, pelaajan autoindeksistä), nopeus, vaihde, kaasu, jarru, ohjaus, kierrosluku, DRS, kääntö, nousu ja kallistus (astetta) sekä g-voimat
- kierrokset autoittain kierrosajan ja kilpailusijoituksen kanssa; maaliin tulot ja keskeytykset
- pelin kilpailutapahtumat: session alku ja loppu, nopein kierros, rangaistukset, ohitukset, törmäykset, turvaauto, punainen lippu, lähtövalot, ruudullinen lippu, voittaja, takaisinkelaukset (`teleport` missä auto oli, `spawn` minne se palasi)
- radan, session tyypin, kierrosten ja kuljettajien tiedot jokaisesta sessiosta
- oman auton kierrokset, paras kierros, kilpailu- ja lähtösijoitus, pysähdykset, rangaistukset, ohitukset, törmäykset, matka ja huippunopeus
- jokainen pelin lähettämä paketti kokonaisena tiedostossa `heat.raw.parquet`, myös ne, joita ei lueta riveiksi

## Mistä tiedot tulevat {#where-it-comes-from}

UDP-telemetria 127.0.0.1:20777 (Documents\My Games\F1 25\hardwaresettings\hardware_settings_config.xml)

## Kuinka se käynnistetään {#how-to-switch-it-on}

Pelissä: Asetukset > Telemetria-asetukset > UDP-telemetria päälle, IP 127.0.0.1, portti 20777. Tai `python -m heat3d_watch setup f1-25 --apply` (muokkaa tiedostoa hardware_settings_config.xml, varmuuskopio tehdään ensin; pelin on oltava suljettu). Jos toinen sovellus pitää porttia 20777 hallussaan, watcher jättää portin sille.

Kirjoita komento terminaaliin, joka on avattu watcherin kansiossa (katso [Ennen aloittamista](before-you-start.md)). Jos se epäonnistuu, viimeinen rivi kertoo syyn; [Asennus ja käynnistys](installing-and-running.md) kattaa yleisimmät syyt.

`python -m heat3d_watch setup f1-25` listaa tiedostot, jotka se muuttaisi; `python -m heat3d_watch setup f1-25 --apply` tekee muutokset ja tallentaa alkuperäisen tiedostona `<file>.heat3d-backup` (katso [Komennot](commands.md#setup)). Se tulostaa `f1-25: changed: ...` jokaisesta muutoksesta tai `f1-25: nothing to change`, jos asetus on jo päällä.

## Miten se toimii {#how-it-works}

EA SPORTS F1 23, F1 24 ja F1 25: virallinen UDP-telemetria, jokainen rata-auto.

Pelit lähettävät sen itse (Asetukset > Telemetria-asetukset tai `Documents/My Games/<F1 xx>/hardwaresettings/hardware_settings_config.xml`, `<udp enabled="true" ip="127.0.0.1" port="20777" sendRate="20" format="2025" ...>`). Little-endian, pakattu, 29 tavun otsikko jokaisessa paketissa (sama vuosien 2023, 2024 ja 2025 muodoissa):

```text
uint16 packetFormat, uint8 gameYear, gameMajorVersion, gameMinorVersion,
packetVersion, packetId, uint64 sessionUID, float sessionTime,
uint32 frameIdentifier, overallFrameIdentifier, uint8 playerCarIndex,
secondaryPlayerCarIndex
```

Luettavat tiedot paketti-tunnuksen mukaan:

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

Jokainen paketti säilytetään myös kokonaisena sellaisenaan session raakatiedostossa (`heat.raw.parquet`, `type` on paketin nimi - `motion`, `car_status` ... - sarakkeina `format`, `packet_id`, `frame` ja `session_uid`). Mukana ovat sekä yllä luetut että ne, joita mikään ei vielä lue: 5 Car Setups, 7 Car Status, 8 Final Classification, 9 Lobby Info, 10 Car Damage, 11 Session History, 12 Tyre Sets, 13 Motion Ex, 14 Time Trial, 15 Lap Positions, mikä tahansa myöhempi tunnus sekä paketit muodossa, jota tämä ei lue. Myöhempi dekooderi tarvitsee siis vain raakatiedoston.

Jokaisen auton sijainti on Motion-paketissa, myös verkossa, siinä missä peli sen itse luovuttaa. Vain polttoaine, ERS, vauriot ja renkaiden tiedot pidetään pois pelaajilta, joilla "Your Telemetry" on rajoitettu. Jokainen auto tallennetaan noin 10 Hz:llä sen kuljettajan nimellä ("car N", kunnes nimet saapuvat), tiimin nimellä, ja pelaajan oma auto merkitään `own`-tunnisteella.

Lähteet: EA:n "F1 25 UDP Specification" (forums.ea.com, F1 games info hub), F1 23- ja F1 24 -määritykset sekä samat taulukot peilattuina projektissa MacManley/f1-25-udp (MIT). Testien paketit on rakennettu näistä asetteluista.

Sama moduuli palvelee myös: [EA SPORTS F1 23 (live-data)](game-f1-23.md), [EA SPORTS F1 24 (live-data)](game-f1-24.md).

## Sijainnit ja akselit {#positions-and-axes}

| | |
|---|---|
| Sijainnit tallennettu | kyllä |
| Ylösakseli | `y` |
| Yksiköt | metriä |
| Peilattu katselimelle | ei mitään |
| Yksikkökerroin (`scale`: katselin kertoo sijainnit sillä) | 1 |

Nämä menevät kunkin session `meta.json`-tiedostoon (`axes`) ja, kun sessiossa on sijainteja, tiedoston `heat.parquet` alatunnisteeseen. Siksi 3DHeat-katselin kääntää ja skaalaa rivit itse; katso [Data](the-data.md).

## Moninpeli {#multiplayer}

- Merkitty pelatuksi verkossa (`multiplayer`): **kyllä**. `games --markdown` näyttää tämän tekstillä "allowed (reads only what the game publishes)".
- Tyyppi `telemetry`: se lukee vain sen, minkä peli tai alusta luovuttaa (UDP-portti tai jaettu muisti, jonka peli julkaisee). Se tallentaa siis myös verkkopelit, samoin kuin offline-pelit. Lippu päättää vain, saako muistia koskaan lukea.
- Muisti: **ei koskaan**. Tämä sovitin ei lue muistia. Vain `memory`-sovittimet lukevat muistia, eikä koskaan verkkopeliksi merkitystä pelistä. Katso [Lähteet ja säännöt](sources-and-rules.md).

## Tallennetut tilastot {#statistics-recorded}

Tilastoavaimet, jotka tämän sovittimen koodi asettaa nimeltä (kunkin session `stats` tiedostossa `meta.json` ja `watcher.sqlite`-tiedoston taulussa `stats`):

`best_lap`, `collisions`, `distance_km`, `fastest_laps`, `finishes`, `flashbacks`, `grid_position`, `laps`, `overtaken`, `overtakes`, `penalties`, `penalty_seconds`, `pit_stops`, `race_position`, `sessions`, `top_speed_kmh`, `wins`

Aaltosulkeissa oleva avain täydennetään ajon aikana (`score.{team}` on yksi avain joukkuetta kohden). Avaimet, jotka koodi ottaa pelin kenttien taulukosta tai pelin omista tilastonimistä, eivät ole tässä luettelossa; yllä oleva "Mitä tallennetaan" -osio nimeää ne.

## Täydellisyys {#completeness}

Watcher noudattaa 3DHeatin [muuntimen sääntöä](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md): lähteessä oleva tieto luetaan tai säilytetään, sitä ei koskaan jätetä pois. Rivien lisäksi jokainen paketti, sivu, rivi tai vastaus, jonka sovitin vastaanottaa, säilytetään kokonaisena session tiedostossa `heat.raw.parquet` (sarakkeet `time`, `ms`, `type`, `used`, `payload`, `text` ja kaikki nimellä säilytetyt kentät; `used` merkitsee ne, joista tuli myös rivejä). Tiedoston `meta.json` kohdan `selfCheck.completeness` laskuri kertoo jokaisen `type`-arvon määrän, ja `lost` on 0.

**Luetaan**

- 0 Motion: jokaisen auton maailman sijainti ja nopeus sekä nyt myös kääntö, nousu ja kallistus (astetta, spesifikaation radiaaneista) sekä sivu-, pituus- ja pystysuuntainen g-voima, jokaisen auton sijaintirivillä
- 1 Session: rata, session tyyppi, kierrosten kokonaismäärä, radan pituus, verkossa tai ei (meta.json `sessions`)
- 2 Lap Data: viimeinen kierrosaika, kierrosnumero, kilpailu- ja lähtösijoitus, pysähdykset, rangaistukset, tuloksen tila (kierrokset, maaliintulot, keskeytykset, tilastot)
- 3 Event: jokainen koodi paitsi BUTN omana rivinään, tietoineen
- 4 Participants: kuljettajien nimet, tiimit, aktiivisten autojen määrä (rivien `player` ja `team`, meta.json `drivers`)
- 6 Car Telemetry: nopeus, vaihde, kaasu ja jarru sekä nyt myös ohjaus (-1..1), kierrosluku ja DRS jokaisen auton sijaintirivillä
- tarkistettu EA:n julkaistuja UDP-määrityksiä vasten vuosien 2023, 2024 ja 2025 muodoille (pakettikoot varmistetaan testeissä); ei vielä pelin omaa dataa vasten

**Säilytetään raakana**

- jokainen paketti kokonaisena tiedostossa `heat.raw.parquet`, `payload` on datagrammi ja `type` tunnuksen nimi: `motion`, `session`, `lap_data`, `event`, `participants`, `car_setups`, `car_telemetry`, `car_status`, `final_classification`, `lobby_info`, `car_damage`, `session_history`, `tyre_sets`, `motion_ex`, `time_trial`, `lap_positions` (`packet <n>` tunnukselle, jota määritykset eivät vielä lista); sarakkeet `format` (2023/2024/2025), `packet_id`, `frame`, `session_uid`
- `used` on tosi edellä luetuille paketeille (Motion, Session, Lap Data, Participants, Car Telemetry ja muut Event-koodit kuin BUTN). Loput eli autojen asetukset, auton tila (polttoaine, ERS, renkaiden koostumus ja ikä, liput), lopputulos, lobby, auton vauriot, session historia (jokaisen auton jokainen kierros- ja sektoriaika), renkaiden sarjat, motion ex (oman auton jousitus, pyörien nopeudet, paikallinen nopeus, kulmanopeus ja kiihtyvyys), time trial, lap positions sekä BUTN-painikkeiden tapahtumat säilytetään myöhempää dekooderia varten
- `format <vuosi>`: paketti ennen vuotta 2023 (toinen otsikkoasettelu), kokonaisena; `short`: datagrammi, joka on lyhyempi kuin 29 tavun otsikko, kokonaisena

**Ei saatavilla**

- muiden pelaajien polttoaine, ERS, vauriot ja renkaiden sarjat verkossa, kun heidän "Your Telemetry" on rajoitettu: peli lähettää niille nollia
- paketit, jotka lähetettiin, kun watcher ei ollut käynnissä tai kun toinen sovellus piti porttia 20777 hallussaan: UDP-liikennettä ei peli tallenna

**Koko**: 60 Hz:n lähetysnopeudella jokainen paketti on noin 0,38 Mt/s (Motion, Lap Data, Car Telemetry, Car Status ja Motion Ex 60 Hz:llä, Session History ja Tyre Sets 20/s, Car Damage 10/s, Session ja Car Setups 2/s), lisäksi noin 0,03 Mt/s kohteiden otsikoita. Tämä on noin 1,5 Gt tunnissa ajoa ennen pakkausta ja noin 0,55 Gt oletusnopeudella 20 Hz. zstd pienentää sen murto-osaan; tyhjät autopaikat ja toistuvat arvot pakkautuvat hyvin. Ei vielä mitattu oikealla sessiolla.

## Todennettu {#verified}

testattu paketeilla vuosien 2023, 2024 ja 2025 muodoissa, jotka on rakennettu EA:n julkaistusta määrityksestä ja lähetetty UDP:llä. Peliä vastaan ei ole testattu.

## Lähde {#source}

[heat3d_watch/adapters/f1.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/f1.py)

<!-- Generated from the adapter by tools/gen_game_pages.py; change the adapter and run it again rather than editing this page. -->
