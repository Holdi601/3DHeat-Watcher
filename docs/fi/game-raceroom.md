---
title: "RaceRoom Racing Experience (reaaliaikadata)"
nav_order: 37
lang: "fi"
source: game-raceroom.md
source_hash: "f3879cd40a67"
nav_exclude: true
search_exclude: true
---
# RaceRoom Racing Experience (reaaliaikadata) {#raceroom-racing-experience-live-data}

Kun pelaat RaceRoom Racing Experiencea, watcher tallentaa datan, jonka peli itse lähettää, jotta voit myöhemmin katsoa sen kartalla 3DHeat-katselimessa.

*Tekniset tiedot: sovitin `raceroom`, tyyppi [`telemetry`](sources-and-rules.md); se toimii, kun `RRRE64.exe` tai `RRRE.exe` on käynnissä, ja etsii uutta dataa 0,1 s välein.*

## Mitä tallennetaan {#what-is-recorded}

- jokaisen auton sijainti (maailman XYZ, m) 10 Hz:n taajuudella kuljettajan nimen mukaan, oma auto merkittynä, nopeus ja kilpailusijoitus; oman auton vaihde, kaasu ja jarru
- session alku pelin nimeämällä radalla; kierrokset autoittain kierrosajoin; maaliintulot; oman auton huoltopysähdykset
- teleportit (takaisin talliin, uudelleenkäynnistys): `teleport` siinä, missä auto oli, `spawn` siinä, missä se on nyt
- omat kierrokset, paras kierros, kilpailusijoitus, matka ja huippunopeus
- pelin koko jaettu muistisivu tiedostossa `heat.raw.parquet`, joka kerta kun se muuttuu
- oman auton rangaistuspisteet

## Mistä data tulee {#where-it-comes-from}

jaettu muisti $R3E (Sector3:n r3e.h, versio 3)

## Miten se kytketään päälle {#how-to-switch-it-on}

Mitään ei tarvitse kytkeä päälle: watcher lukee lähteen juuri sellaisena kuin peli tai alusta sen antaa.

## Miten se toimii {#how-it-works}

Jaettu muisti, jonka kilpapelit julkaisevat kojelautoja varten, luetaan vain lukuoikeudella, eikä sitä koskaan luoda.

Useat simulaattorit antavat telemetriansa nimettynä Windowsin tiedostokarttana, jonka peli luo ja jonka kuka tahansa saa lukea: Kunosin `Local\acpmf_*`-sivut (Assetto Corsa, ACC, AC Rally, AC EVO:n `Local\acevo_pmf_*`), iRacingin `Local\IRSDKMemMapFileName`, RaceRoomin `$R3E` ja Automobilista 2:n / Project CARS 2:n `$pcars2$`.

Miksi ei `mmap.mmap(-1, size, tagname=...)`, joka on tavallinen tapa Pythonissa: kun karttaa ei vielä ole, se *luo* sen, ja tässä luku on vain lukuoikeudella. Peli, joka käynnistyy sen jälkeen, avaa watcherin kartan omansa sijaan eikä pysty kirjoittamaan siihen, joten sen telemetria on kuollut, kunnes watcher vapauttaa kartan. Watcher käynnistää sovittimen heti, kun pelin prosessi ilmestyy, ja juuri silloin peli ei ole vielä luonut omaa karttaansa. Siksi tämä avaa kartan `OpenFileMappingW`:llä, joka löytää vain olemassa olevan kartan, kartoittaa sen `FILE_MAP_READ`-oikeudella ja ilmoittaa "ei vielä", jos karttaa ei ole. Sovittimet yrittävät uudelleen hetken kuluttua.

Mikään tässä ei voi kirjoittaa: näkymä kartoitetaan vain lukuoikeudella, ja siitä kopioidaan vain `ctypes.string_at`-kutsulla.

Kahta peliä luetaan tässä myös; jokainen rata-auto on niiden sivuilla.

#### RaceRoom Racing Experience - `$R3E` {#raceroom-racing-experience---r3e}

Sector3:n `r3e.h` (github.com/sector3studios/r3e-api, sample-c/src/r3e.h, versio 3.6), `#pragma pack(1)`. Otsakkeessa kerrotaan, mistä kuljettajat alkavat ja kuinka suuri yksi on (`all_drivers_offset`, `driver_data_size`), joten kuljettajakohtainen osa, eli nimi, paikka, kilpailusijoitus, maailmasijainti (float x y z, m), suoritetut kierrokset, nykyisen kierroksen aika, maaliintulon tila, huoltokaista ja nopeus, luetaan niiden avulla. Pelaajan omat kentät (paras ja edellinen kierros, kilpailusijoitus, rangaistuspisteet, vaihde, pedaalit, radan ja asettelun nimet) luetaan niiden 3.6-offseteista vain silloin, kun `all_drivers_offset` on se 2008, johon tämä asettelu sen asettaa. Y oletetaan ylös, koska otsake ei sano sitä.

Samaa moduulia käyttävät myös: [Automobilista 2 (reaaliaikadata)](game-automobilista-2.md), [Project CARS 2 (reaaliaikadata)](game-project-cars-2.md).

## Sijainnit ja akselit {#positions-and-axes}

| | |
|---|---|
| Sijainnit tallennettu | kyllä |
| Ylösakseli | `y` |
| Yksiköt | metriä; Y ylös oletettu (r3e.h ei kerro) |
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

- kuljettajakohtaisesti (otsakkeen omalla offsetilla ja koolla): nimi, paikka, maaliintulon tila, sijoitus, maailmasijainti, suoritetut kierrokset, nykyisen kierroksen aika, huoltokaista, nopeus
- pelaajan omat kentät, vain kun sivu on r3e.h 3.6 -asettelu: radan ja asettelun nimet, istuntotyyppi, kilpailusijoitus, paras ja edellinen kierros, rangaistuspisteet, vaihde, kaasu, jarru, pelaajan paikka
- offsetit laskettu Sector3:n r3e.h 3.6:sta ja tarkistettu sivulla, joka rakennettiin siitä testeissä; ei vielä pelistä

**Tallennettu raakana**

- `r3e`: koko $R3E-kartta, jokainen luku, jonka tavut eroavat viimeksi tallennetusta kopiosta, kaikki r3e.h:n kentät: pelaajan fysiikka (suuntaus, nopeudet, kiihtyvyydet, g-voimat), moottori, polttoaine, renkaat, jarrut, vauriot, liput, huoltovalikko, sektoriajat, jokaisen kuljettajapaikan koko kuljettajatieto (luokka, malli, joukkue, sektoriajat, välit, rangaistukset, renkaat)
- `used` on tosi, kun sivu luetaan riveiksi; epätosi, kun sivu on valikoissa, tauolla, toistossa, toisessa asettelussa tai kirjoituksen keskeltä (`torn` 1). `unchanged_reads` meta.json:ssa laskee lukemat, jotka olivat tavu tavulta samat kuin aiemmin tallennettu kopio

**Ei saatavilla**

- muiden kuljettajien syötteet ja fysiikka: sivu antaa vain pelaajan omat tiedot
- muiden autojen tarkat kierrosajat: paikalla on vain sen käynnissä oleva kierrosaika, joten kierros on viimeksi nähty käynnissä oleva aika (noin 0,1 s tarkkuudella)
- pelaajan omat kentät muulla asettelulla kuin 3.6: tallennetaan raakana, ei lueta, ennen kuin ne on tarkistettu

**Koko**: sivu on 44 KB (r3e.h 3.6; kartta pyöristetään kokonaisiin 4 KB:n sivuihin), jopa 10 kertaa sekunnissa ajaessa: noin 1,6 Gt tunnissa ennen pakkausta; tyhjät kuljettajapaikat ja muuttumattomat kentät pakkautuvat zstd:llä hyvin (ei vielä mitattu oikeasta sessiosta)

## Todennettu {#verified}

Testattu sivulla, joka rakennettiin testissä r3e.h 3.6:sta (offsetit laskettu virallisesta otsakkeesta). Peliä vastaan ei ole testattu. Muiden autojen kierrosajat ovat viimeksi nähty käynnissä oleva kierrosaika (noin 0,1 s tarkkuudella).

## Lähdekoodi {#source}

[heat3d_watch/adapters/simracing_shm.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/simracing_shm.py)

<!-- Generated from the adapter by tools/gen_game_pages.py; change the adapter and run it again rather than editing this page. -->
