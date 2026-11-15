---
title: "Project CARS 2 (reaaliaikadata)"
nav_order: 36
lang: "fi"
source: game-project-cars-2.md
source_hash: "278eb9594615"
nav_exclude: true
search_exclude: true
---
# Project CARS 2 (reaaliaikadata) {#project-cars-2-live-data}

Kun pelaat Project CARS 2:ta, watcher tallentaa datan, jonka peli itse lähettää, jotta voit myöhemmin katsoa sen kartalla 3DHeat-katselimessa.

*Tekniset tiedot: sovitin `project-cars-2`, tyyppi [`telemetry`](sources-and-rules.md); se toimii, kun `pCARS2AVX.exe` tai `pCARS2.exe` on käynnissä, ja etsii uutta dataa 0,1 s välein.*

## Mitä tallennetaan {#what-is-recorded}

- jokaisen auton sijainti (maailman XYZ, m) 10 Hz:n taajuudella kuljettajan nimen mukaan, oma auto merkittynä, nopeus ja kilpailusijoitus; oman auton vaihde, kaasu ja jarru
- session alku pelin nimeämällä radalla; kierrokset autoittain kierrosajoin; maaliintulot; oman auton huoltopysähdykset
- teleportit (takaisin talliin, uudelleenkäynnistys): `teleport` siinä, missä auto oli, `spawn` siinä, missä se on nyt
- omat kierrokset, paras kierros, kilpailusijoitus, matka ja huippunopeus
- pelin koko jaettu muistisivu tiedostossa `heat.raw.parquet`, joka kerta kun se muuttuu

## Mistä data tulee {#where-it-comes-from}

jaettu muisti $pcars2$ (SMS:n SharedMemory.h)

## Miten se kytketään päälle {#how-to-switch-it-on}

Pelissä: Options > System > Shared Memory: "Project CARS 2"

## Miten se toimii {#how-it-works}

Jaettu muisti, jonka kilpapelit julkaisevat kojelautoja varten, luetaan vain lukuoikeudella, eikä sitä koskaan luoda.

Useat simulaattorit antavat telemetriansa nimettynä Windowsin tiedostokarttana, jonka peli luo ja jonka kuka tahansa saa lukea: Kunosin `Local\acpmf_*`-sivut (Assetto Corsa, ACC, AC Rally, AC EVO:n `Local\acevo_pmf_*`), iRacingin `Local\IRSDKMemMapFileName`, RaceRoomin `$R3E` ja Automobilista 2:n / Project CARS 2:n `$pcars2$`.

Miksi ei `mmap.mmap(-1, size, tagname=...)`, joka on tavallinen tapa Pythonissa: kun karttaa ei vielä ole, se *luo* sen, ja tässä luku on vain lukuoikeudella. Peli, joka käynnistyy sen jälkeen, avaa watcherin kartan omansa sijaan eikä pysty kirjoittamaan siihen, joten sen telemetria on kuollut, kunnes watcher vapauttaa kartan. Watcher käynnistää sovittimen heti, kun pelin prosessi ilmestyy, ja juuri silloin peli ei ole vielä luonut omaa karttaansa. Siksi tämä avaa kartan `OpenFileMappingW`:llä, joka löytää vain olemassa olevan kartan, kartoittaa sen `FILE_MAP_READ`-oikeudella ja ilmoittaa "ei vielä", jos karttaa ei ole. Sovittimet yrittävät uudelleen hetken kuluttua.

Mikään tässä ei voi kirjoittaa: näkymä kartoitetaan vain lukuoikeudella, ja siitä kopioidaan vain `ctypes.string_at`-kutsulla.

Kahta peliä luetaan tässä myös; jokainen rata-auto on niiden sivuilla.

#### Automobilista 2 / Project CARS 2 - `$pcars2$` {#automobilista-2--project-cars-2---pcars2}

SMS:n `SharedMemory.h` (toimitetaan pelin kansiossa Support\SharedMemory; AMS2: Options > System > Shared Memory "Project CARS 2"), `#pragma pack(4)`. `mParticipantInfo[64]` alkaa tavusta 28, 100 tavua kukin: mIsActive, mName[64], mWorldPosition[3] (m, Y ylös), mCurrentLapDistance, mRacePosition, mLapsCompleted, mCurrentLap, mCurrentSector; mViewedParticipantIndex (20) on pelaajan auto; osallistujakohtaisesti mLastLapTimes (9200), mRaceStates (9520), mSpeeds (10800); pelaajan mBestLapTime (6716), mLastLapTime (6720), mSpeed (6848), mBrake, mThrottle, mGear; mSequenceNumber (7320) on pariton, kun peli kirjoittaa. Offsetit laskettiin kahdesta toisistaan riippumattomasta otsakkeen kopiosta (pelin oma kopio ei ole asennettuna tässä), ja ne täsmäävät.

Molemmat sivut tallennetaan lisäksi kokonaisina (docs/converters.md, "Live sources"): koko kartta, jokainen luku, jonka tavut eroavat viimeksi tallennetusta kopiosta, session raakatiedostossa tyypillä `type` `r3e` tai `pcars2`. Mukana on jokainen kuljettajapaikka ja jokainen otsakkeen kenttä, myös ne, joita ei lueta tässä, joten myöhempi dekooderi tarvitsee vain raakatiedoston.

Samaa moduulia käyttävät myös: [Automobilista 2 (reaaliaikadata)](game-automobilista-2.md), [RaceRoom Racing Experience (reaaliaikadata)](game-raceroom.md).

## Sijainnit ja akselit {#positions-and-axes}

| | |
|---|---|
| Sijainnit tallennettu | kyllä |
| Ylösakseli | `y` |
| Yksiköt | metriä |
| Peilattu katselinta varten | ei mitään |
| Yksikköskaala (`scale`: katselin kertoo sijainnit sillä) | 1 |

Nämä menevät kunkin session `meta.json`:n kohtaan `axes` ja, kun sessiossa on sijainteja, `heat.parquet`:n footeriin. Näin 3DHeat-katselin kääntää ja skaalaa rivit itse, katso [Data](the-data.md).

## Moninpeli {#multiplayer}

- Merkitty pelatuksi verkossa (`multiplayer`): **kyllä**. `games --markdown` näyttää tämän muodossa "allowed (reads only what the game publishes)".
- Tyyppi `telemetry`: se lukee vain sen, minkä peli tai alusta antaa ulos (UDP-portin tai jaetun muistin, jonka peli julkaisee). Siksi se tallentaa myös verkkopelissä, aivan kuten offline-pelissä. Lippu ratkaisee vain sen, saako muistia koskaan lukea.
- Muisti: tämän sovittimen lukema **ei koskaan**. Vain `memory`-sovittimet lukevat muistia, eikä koskaan peliin, joka on merkitty verkkopeliksi. Katso [Lähteet ja säännöt](sources-and-rules.md).

## Tilastot {#statistics-recorded}

Tilastoavaimet, jotka tämän sovittimen koodi asettaa nimeltä (session `stats` tiedostossa `meta.json` ja taulussa `stats` tiedostossa `watcher.sqlite`):

`best_lap`, `distance_km`, `finishes`, `incidents`, `laps`, `pit_stops`, `race_position`, `top_speed_kmh`

Aaltosulkeissa oleva avain täydentyy ajon aikana (`score.{team}` on yksi avain per joukkue). Avaimet, jotka koodi ottaa pelin kenttien taulukosta tai pelin omista tilastonimistä, eivät ole tässä listassa. Kohdassa "Mitä tallennetaan" ne on nimetty.

## Täydellisyys {#completeness}

Watcher noudattaa 3DHeatin [muunninsääntöä](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md): se, mitä lähde sisältää, luetaan tai tallennetaan, eikä mitään pudoteta. Rivien lisäksi jokainen paketti, sivu, rivi tai vastaus, jonka sovitin vastaanottaa, tallennetaan sellaisenaan session tiedostoon `heat.raw.parquet` (sarakkeet `time`, `ms`, `type`, `used`, `payload`, `text` ja sen jälkeen nimellä säilytetyt kentät; `used` merkitsee ne, joista tuli myös rivejä). `meta.json`:n `selfCheck.completeness` laskee jokaisen `type`-arvon, ja `lost` on 0.

**Luettu**

- osallistujakohtaisesti (enintään 64): aktiivisuus, nimi, maailmasijainti, kilpailusijoitus, suoritetut kierrokset; viimeinen kierrosaika, kilpailutila ja nopeus
- pelaajan auto (mViewedParticipantIndex), pelin ja session tila, radan sijainti ja variantti, paras ja viimeisin kierros, nopeus, jarru, kaasu, vaihde; mSequenceNumber ohittaa kopion, joka otettiin kesken kirjoituksen
- offsetit kahdesta toisistaan riippumattomasta SMS:n SharedMemory.h-kopiosta, jotka täsmäävät; testattu sivulla, joka rakennettiin niistä testeissä; ei vielä pelistä

**Tallennettu raakana**

- `pcars2`: koko $pcars2$-kartta (rakenne jatkuu paljon yli tässä luetut 11 312 tavua), jokainen luku, jonka tavut eroavat viimeksi tallennetusta kopiosta: jokaisen osallistujan suuntaus, sektoriajat, auton ja luokan nimet, huoltotilat ja liput, pelaajan fysiikka, renkaat, jousitus, vauriot, sää ja kaikki myöhemmät Project CARS 2 -versiot lisäämät kentät
- `used` on tosi, kun sivu luetaan riveiksi; epätosi, kun sivu on valikoissa, tauolla, toistossa, toisessa asettelussa tai kirjoituksen keskeltä (`torn` 1). `unchanged_reads` meta.json:ssa laskee lukemat, jotka olivat tavu tavulta samat kuin aiemmin tallennettu kopio

**Ei saatavilla**

- muiden osallistujien syötteet ja fysiikka: sivu antaa vain katsotun auton tiedot
- kaikki, kun pelin jaetun muistin asetus on pois päältä (Project CARS 2 ei kirjoita mitään silloin)

**Koko**: kartta on noin 20–30 KB (pelin version mukaan), jopa 10 kertaa sekunnissa ajaessa: noin 0,7–1,1 Gt tunnissa ennen pakkausta. zstd pienentää tyhjät osallistujapaikat ja muuttumattomat nimet murto-osaan (ei vielä mitattu oikeasta sessiosta).

## Todennettu {#verified}

Testattu sivulla, joka rakennettiin testissä. Offsetit kahdesta toisistaan riippumattomasta SharedMemory.h-kopiosta, jotka täsmäävät, eivät pelin mukana tulevasta kopiosta. Peliä vastaan ei ole testattu.

## Lähdekoodi {#source}

[heat3d_watch/adapters/simracing_shm.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/simracing_shm.py)

<!-- Generated from the adapter by tools/gen_game_pages.py; change the adapter and run it again rather than editing this page. -->
