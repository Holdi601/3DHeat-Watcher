---
title: "X-Plane (reaaliaikadata)"
nav_order: 49
lang: "fi"
source: game-xplane.md
source_hash: "be1c5b21d2ef"
nav_exclude: true
search_exclude: true
---
# X-Plane (reaaliaikadata) {#x-plane-live-data}

Kun pelaat X-Planea, watcher tallentaa datan, jonka peli itse lähettää ulos. Voit katsoa sitä myöhemmin kartalta 3DHeat-katseluohjelmassa.

*Tekniset tiedot: sovitin `xplane`, tyyppi [`telemetry`](sources-and-rules.md); se toimii, kun `X-Plane.exe` on käynnissä, ja hakee uutta dataa 0,1 s välein.*

## Mitä tallennetaan {#what-is-recorded}

- oma sijainti 10 Hz:llä (leveys-, pituusaste ja korkeus metreinä itään/ylös/pohjoiseen ensimmäisestä kiinnityksestä; leveys-, pituusaste ja korkeus sarakkeina)
- asento, mitattu ja todellinen lentonopeus, maanopeus, Mach, pystynopeus, AoA, luisto, magneettinen suunta, AGL, g (normaali, akselin suuntainen, sivuttainen), nopeus ja kiertonopeudet, läpät, ilmajarru, kaasu, maassa-tieto
- painot (yhteensä, polttoaine, hyötykuorma), vaihdekahva, autopilotti, moottorin kierrosluku ja N1, simulaation aika ja päivämäärä, tauko, simulaation nopeus, uusinta, ulkolämpötila ja merenpinnan paine (X-Plane 12) kerran sekunnissa
- lentoonlähdöt, laskeutumiset, törmäykset, lentojen nollaukset (session_start/session_end lennoittain)
- lentoaika, ilmassa oloaika, matka, suurin korkeus, suurin g, laskeutumiset
- jokainen X-Planen lähettämä vastaus kokonaisena heat.raw.parquet-tiedostossa

## Mistä data tulee {#where-it-comes-from}

X-Planen UDP-rajapinta osoitteessa 127.0.0.1:49000 (RREF-datarefit ja RPOS-sijainti, vastataan watcherille)

## Miten se kytketään päälle {#how-to-switch-it-on}

X-Plane 12: Settings > Network > Accept incoming connections (X-Plane 11 vastaa oletuksena)

## Miten se toimii {#how-it-works}

X-Plane 11 ja 12: simulaattorin oma UDP-rajapinta portissa 49000.

X-Plane vastaa jokaiselle, joka kysyy osoitteessa 127.0.0.1:49000, pyydetyllä taajuudella, pyynnön lähettäneen
osoitteen ja portin kautta (X-Planen dokumentti "Exchanging Data with X-Plane", toimitettu kansiossa `<X-Plane>\Instructions\`):

```text
RREF  "RREF\0" + int32 freq + int32 index + char[400] dataref path (413 bytes).
      The answer is "RREF" + one internal byte + (int32 index, float32 value)
      pairs; freq 0 stops it.
RPOS  "RPOS\0" + the rate as a NUL-terminated ASCII string ("10\0"). The
      answer is "RPOS" + one internal byte + double lon, lat, elevation (m
      MSL) + float AGL (m), pitch, true heading, roll (deg), vx east, vy up,
      vz south (m/s), P, Q, R (rad/s), tightly packed.
```

RPOS antaa leveys- ja pituusasteen doubleina, joten se ohjaa sijaintia; RREF tuo loput ja korvaa RPOS:n, kun RPOS ei tule. Datarefit (nimet kuten X-Plane 12:n `Resources\plugins\DataRefs.txt`-tiedostossa,
<https://developer.x-plane.com/datarefs/>):

```text
sim/flightmodel/position/latitude, longitude, elevation  deg, deg, m MSL
sim/flightmodel/position/true_theta, true_phi, true_psi  pitch, roll, true heading (deg)
sim/flightmodel/position/indicated_airspeed              knots
sim/flightmodel/position/groundspeed                     m/s
sim/flightmodel/position/y_agl                           m above ground
sim/flightmodel/forces/g_nrml                            g, normal to the wings
sim/flightmodel/failures/onground_any                    1 on the ground
sim/flightmodel2/misc/has_crashed                        1 crashed
sim/time/total_flight_time_sec                           since the flight was reset
```

ja loppu lennosta samalla taajuudella (todellinen lentonopeus, pystynopeus, AoA,
luisto, magneettinen suunta, Mach, akselin suuntainen ja sivuttainen g, kiertonopeudet, läpät,
ilmajarru, kaasu: `DATAREFS`), ja koneen hitaampi tila kerran sekunnissa (painot, vaihdekahva, autopilotti, moottorit, simulaation aika,
tauko ja nopeus, sää: `SLOW_DATAREFS`). Jokainen datagrammi tallennetaan myös kokonaisena session
raakatiedostoon, ja meta.json kertoo, mikä dataref on kunkin RREF-indeksin takana.

X-Plane 12 hyväksyy nämä vain, kun Settings > Network > "Accept incoming connections" on päällä. Sijainnit menevät litteään
karttaan lennon ensimmäisen kiinnityksen (`Tangent`) ympärille: x itään, z pohjoiseen metreinä, y merenpinnasta mitattu
korkeus - joten tasalento pysyy tasona, miten pitkälle se meneekin, mitä todellinen tangenttitaso kaartaisi alas maapallon mukana. Kartan origo on session `geo`:
meta.json ja taulukon alatunnisteessa, joten katseluohjelma voi asettaa oikean maailman lennon alle.

Tämä moduuli sisältää myös, mitä muut lentosimulaattorit jakavat: litteän kartan, lentokirjanpidon (lentoonlähdöt, laskeutumiset,
törmäykset, matka), UDP-soketin ja Steam-kirjastolistan.

## Sijainnit ja akselit {#positions-and-axes}

| | |
|---|---|
| Sijainnit tallennetaan | kyllä |
| Ylösakseli | `y` |
| Yksiköt | metriä (itään, korkeus, pohjoiseen ensimmäisestä kiinnityksestä) |
| Peilattu katseluohjelmaa varten | `z` |
| Yksikköskaala (`scale`: katseluohjelma kertoo sijainnit tällä) | 1 |

Nämä menevät jokaisen session `meta.json`-tiedoston kohtaan `axes` ja, kun sessiossa on sijainteja, `heat.parquet`-tiedoston alatunnisteeseen, joten 3DHeat-katseluohjelma kääntää ja skaalaa rivit itse - katso [Data](the-data.md).

## Moninpeli {#multiplayer}

- Merkitty pelatuksi verkossa (`multiplayer`): **ei**. `games --markdown` näyttää tämän muodossa "yksinpeli".
- Tyyppi `telemetry`: se lukee vain sen, minkä peli tai alusta antaa ulos (UDP-portin tai jaetun muistin, jonka peli julkaisee), joten se tallentaa myös verkkopelissä, aivan kuten offline-pelissäkin; lippu päättää vain sen, saako muistia koskaan lukea.
- Muisti: tämä sovitin **ei koskaan** lue muistia. Vain `memory`-sovittimet lukevat muistia, eikä koskaan peliin, joka on merkitty pelatuksi verkossa - katso [Lähteet ja säännöt](sources-and-rules.md).

## Tilastot {#statistics-recorded}

Tilastoavaimet, jotka tämän sovittimen koodi asettaa nimeltä (jokaisen session `stats` `meta.json`-tiedostossa ja taulukossa `stats` tiedostossa `watcher.sqlite`):

`airborne_time`, `bad_packets`, `crashes`, `distance_km`, `flight_time`, `max_altitude_m`, `max_g`, `{event}s`

Aaltosulkeissa oleva avain täydennetään ajon aikana (`score.{team}` on yksi avain joukkuetta kohden). Avaimet, jotka koodi ottaa pelin kenttätaulukosta tai pelin omista tilastonimistä, eivät ole tässä luettelossa; "Mitä tallennetaan" -osio nimeää ne.

## Täydellisyys {#completeness}

Watcher noudattaa 3DHeatin [muunnossääntöä](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md): mitä lähde pitää sisällään, se luetaan tai tallennetaan, eikä sitä koskaan jätetä pois. Rivien lisäksi jokainen paketti, sivu, rivi tai vastaus, jonka sovitin vastaanottaa, tallennetaan muuttamattomana session `heat.raw.parquet`-tiedostoon (sarakkeet `time`, `ms`, `type`, `used`, `payload`, `text` ja kaikki nimellä säilytetyt kentät; `used` merkitsee ne, mistä tuli myös rivejä), ja `meta.json`:n `selfCheck.completeness` laskee jokaisen `type`-arvon - `lost` on 0.

**Luettu**

- RPOS (10 Hz): pituus- ja leveysaste, korkeus, AGL, pitch, todellinen suunta, roll, nopeus (itä, ylös, etelä) ja kiertonopeudet P/Q/R - kaikki riveillä
- RREF (10 Hz): `DATAREFS`-listan 27 datarefiä - sijainti, asento, IAS, maanopeus, TAS, pystynopeus, AoA, luisto, magneettinen suunta, Mach, g normaali/akselin suuntainen/sivuttainen, kiertonopeudet, läpät, ilmajarru, kaasu, AGL, törmäys, maassa, lentoaika - riveillä
- RREF (1 Hz): `SLOW_DATAREFS`-listan 20 datarefiä - painot, vaihdekahva, autopilotin servot, simulaation aika ja päivämäärä, tauko, simulaation nopeus, uusinta, moottorien määrä, moottoreiden 1-4 kierrosluku, moottoreiden 1-2 N1, ulkoilman lämpötila, merenpinnan paine - riveillä viimeksi vastaanotettuina

**Tallennettu raakana**

- jokainen datagrammi kokonaisena `payload`-kenttänä neljän kirjaimen otsikkonsa alla: `RREF` ja `RPOS` (käytetty, kun kysely teki rivin; valikoissa ja ilman sijaintia ne eivät tee riviä), muu, minkä X-Plane lähettää watcherin portille, omalla otsikollaan tai nimellä `unknown`; meta.json:n `requests` kertoo, mikä dataref on kunkin RREF-indeksin takana, joten payloadit luetaan ilman tätä moduulia

**Ei saatavilla**

- kaikki muut datarefit (X-Planella niitä on tuhansia): RREF lähettää vain pyydetyt, yksi tilaus kullekin; lista pyytää lennon, koneen tilan ja simulaation ajan - lisää ohjaamon yksityiskohtia (radiot, valot, jokaisen moottorin mittarit, viat) moninkertaistaisi pyynnöt
- koneen nimi ja ICAO-tyyppi: tavutaulukkona olevat datarefit, joista RREF lähettää yhden floatin per merkki
- muut lentokoneet (tekoäly ja moninpeli): sim/multiplayer/position-datarefeja ei ole pyydetty
- DATA-tuloste (Settings > Data Output): se lähettää kiinteään osoitteeseen, joka on valittu simulaattorissa, ei sille, joka kysyy; RREF ja RPOS kattavat sen, minkä watcher lukee

**Koko**: noin 17 MB tunnissa ennen zstd:tä (RREF ja RPOS 10 Hz:llä, noin 220 ja 70 tavua plus kehys kumpikin, hidas RREF kerran sekunnissa), jos X-Plane lähettää jokaisen kyselyn arvot yhdessä paketissa niin kuin se tekee; zstd pienentää floatit useita kertoja

## Testattu {#verified}

testattu väärennettyä paikallista X-Planea vasten, joka vastaa RREF/RPOS-kyselyihin X-Plane 12:n 'Exchanging Data with X-Plane' -dokumentin mukaan; datarefien nimet tarkistettu X-Plane 12:n DataRefs.txt-tiedostosta; ei testattu käynnissä olevaa simulaattoria vastaan

## Lähde {#source}

[heat3d_watch/adapters/xplane.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/xplane.py)

<!-- Generated from the adapter by tools/gen_game_pages.py; change the adapter and run it again rather than editing this page. -->
