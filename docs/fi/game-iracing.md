---
title: "iRacing (reaaliaikadata)"
nav_order: 28
lang: "fi"
source: game-iracing.md
source_hash: "894d9bc4081f"
nav_exclude: true
search_exclude: true
---
# iRacing (reaaliaikadata) {#iracing-live-data}

Kun pelaat iRacingia, watcher tallentaa datan, jonka peli itse lähettää ulos. Voit katsoa sitä myöhemmin tilastoina ja aikajanana.

*Tekniset tiedot: sovitin `iracing`, tyyppi [`telemetry`](sources-and-rules.md); se toimii, kun `iRacingSim64DX11.exe` tai `iRacingSim64.exe` on käynnissä, ja hakee uutta dataa 0,1 s välein.*

## Mitä tallennetaan {#what-is-recorded}

- ajaminen 5 Hz:llä ilman sijaintia (iRacing ei anna sijaintia reaaliajassa): nopeus, vaihde, kaasu, jarru, kierros, osuus kierroksesta, kilpailun ja luokan sijoitus, rikkeet
- session alku, auton nousu ja nousu ulos, kuoppakaistalle meno ja sieltä poistuminen, kierrokset kierrosajoineen, rikkeet pistemäärineen, ruutulippu, maali
- session aikana kirjoitetut .ibt-telemetriatiedostot (leveysaste, pituusaste, korkeus - katseluohjelma lukee ne)
- kierrokset, paras kierros, rikkeet, kilpailun sijoitus, huoltopysähdykset, matka, huippunopeus
- koko jaettu muisti heat.raw.parquet-tiedostossa: otsikko, muuttujaotsikot, sessiotiedot, jokainen luettu telemetriarivi

## Mistä data tulee {#where-it-comes-from}

jaettu muisti Local\IRSDKMemMapFileName (iRacing SDK); .ibt-tiedostot kansiosta %USERPROFILE%\Documents\iRacing\telemetry

## Miten se kytketään päälle {#how-to-switch-it-on}

Reaaliaikadataan ei tarvitse kytkeä mitään. Sijainteja varten: tallenna telemetria autossa (Alt+L) tai aseta irsdkLog=1 tiedostoon app.ini

## Miten se toimii {#how-it-works}

iRacing reaaliajassa: iRacing SDK:n jaettu muisti, luettu suoraan.

iRacing julkaisee telemetriansa sovelluksille nimetyssä tiedostokuvauksessa,
`Local\IRSDKMemMapFileName`, jonka simulaattori luo sen käydessä (ja joka
signaloi `Local\IRSDKDataValidEvent`-tapahtumalla jokaisesta päivityksestä, mitä ei tarvita tässä:
watcher katsoo kymmenen kertaa sekunnissa). Asettelu on SDK:n `irsdk_defines.h`, jota seuraa myös pyirsdk (MIT) -
kirjoitettu tässä uudelleen näistä tosiasioista:

```text
irsdk_header (little-endian int32s)
    0 ver, 4 status (bit 0: connected), 8 tickRate,
    12 sessionInfoUpdate, 16 sessionInfoLen, 20 sessionInfoOffset,
    24 numVars, 28 varHeaderOffset, 32 numBuf, 36 bufLen, 40 pad[2],
    48 varBuf[4]: { tickCount, bufOffset, pad[2] } (16 bytes each)
irsdk_varHeader (144 bytes, numVars of them at varHeaderOffset)
    0 type (0 char, 1 bool, 2 int, 3 bitfield, 4 float, 5 double),
    4 offset (into a line), 8 count, 12 countAsTime + 3 pad,
    16 name[32], 48 desc[64], 112 unit[32]
session info: YAML text at sessionInfoOffset, rewritten when
    sessionInfoUpdate changes (track, sessions, drivers)
```

Simulaattori kirjoittaa `numBuf` riviä kiertävästi; uusin on se, jolla on
suurin tickCount, ja rivi luetaan uudelleen, jos sen tickCount muuttui sen kopioinnin aikana.

Reaaliaikadatassa ei ole maailman sijaintia - leveysaste, pituusaste ja korkeus ovat vain
.ibt-tiedostoissa, joihin iRacing kirjaa kansioon `Documents\iRacing\telemetry` (Alt+L autossa tai
`irsdkLog=1`), ja 3DHeat-katseluohjelma lukee ne itse. Tämä tallentaa siis ajamisen
tapahtumina ilman koordinaatteja - nopeus, kierros, osuus kierroksesta, kilpailun sijoitus,
rikkeet - sekä kierrokset, rikkeet, huoltopysähdykset ja ruutulipun, ja lopussa session aikana kirjoitetut
.ibt-tiedostot `telemetry_file`-tapahtumina, jotta katseluohjelma voi avata ne.

Rivien lisäksi koko muistikartta tallennetaan session raakatiedostoon
(`heat.raw.parquet`): otsikon kiinteä osa (`header`, joka kerta, kun se muuttuu), muuttujaotsikot
(`var_headers`, kokonaisina ja JSON-muodossa kentässä `text`, joka kerta, kun asettelu muuttuu), sessiotiedot
YAML-muodossa (`session_info`, sen teksti joka kerta, kun `sessionInfoUpdate` liikkuu) ja uusin
telemetriarivi (`telemetry`, jokainen sen muuttuja, jokaisella lukukerralla, joka löytää uuden tickin). Muuttujaotsikot
ja yksi rivi riittävät, jotta myöhempi dekooderi lukee minkä tahansa muuttujan.

Lähde: iRacing SDK (irsdk_defines.h, "iRacing SDK" -foorumin dokumentaatio);
kutu/pyirsdk (MIT) offsettien vahvistamiseen.

## Sijainnit ja akselit {#positions-and-axes}

| | |
|---|---|
| Sijainnit tallennetaan | ei |
| Ylösakseli | `y` |
| Yksiköt | ei sijainteja reaaliajassa; .ibt-tiedostot sisältävät leveys-, pituusasteen ja korkeuden |
| Peilattu katseluohjelmaa varten | ei mitään |
| Yksikköskaala (`scale`: katseluohjelma kertoo sijainnit tällä) | 1 |

Nämä menevät jokaisen session `meta.json`-tiedoston kohtaan `axes` ja, kun sessiossa on sijainteja, `heat.parquet`-tiedoston alatunnisteeseen, joten 3DHeat-katseluohjelma kääntää ja skaalaa rivit itse - katso [Data](the-data.md).

## Moninpeli {#multiplayer}

- Merkitty pelatuksi verkossa (`multiplayer`): **kyllä**. `games --markdown` näyttää tämän muodossa "sallittu (lukee vain sen, minkä peli julkaisee)".
- Tyyppi `telemetry`: se lukee vain sen, minkä peli tai alusta antaa ulos (UDP-portin tai jaetun muistin, jonka peli julkaisee), joten se tallentaa myös verkkopelissä, aivan kuten offline-pelissäkin; lippu päättää vain sen, saako muistia koskaan lukea.
- Muisti: tämä sovitin **ei koskaan** lue muistia. Vain `memory`-sovittimet lukevat muistia, eikä koskaan peliin, joka on merkitty pelatuksi verkossa - katso [Lähteet ja säännöt](sources-and-rules.md).

## Tilastot {#statistics-recorded}

Tilastoavaimet, jotka tämän sovittimen koodi asettaa nimeltä (jokaisen session `stats` `meta.json`-tiedostossa ja taulukossa `stats` tiedostossa `watcher.sqlite`):

`best_lap`, `distance_km`, `finishes`, `incidents`, `laps`, `pit_stops`, `race_position`, `sessions`, `top_speed_kmh`

Aaltosulkeissa oleva avain täydennetään ajon aikana (`score.{team}` on yksi avain joukkuetta kohden). Avaimet, jotka koodi ottaa pelin kenttätaulukosta tai pelin omista tilastonimistä, eivät ole tässä luettelossa; "Mitä tallennetaan" -osio nimeää ne.

## Täydellisyys {#completeness}

Watcher noudattaa 3DHeatin [muunnossääntöä](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md): mitä lähde pitää sisällään, se luetaan tai tallennetaan, eikä sitä koskaan jätetä pois. Rivien lisäksi jokainen paketti, sivu, rivi tai vastaus, jonka sovitin vastaanottaa, tallennetaan muuttamattomana session `heat.raw.parquet`-tiedostoon (sarakkeet `time`, `ms`, `type`, `used`, `payload`, `text` ja kaikki nimellä säilytetyt kentät; `used` merkitsee ne, mistä tuli myös rivejä), ja `meta.json`:n `selfCheck.completeness` laskee jokaisen `type`-arvon - `lost` on 0.

**Luettu**

- uusimmasta telemetriariviltä: session aika, numero, tila ja tunnus, radalla, replay, kierros, suoritetut kierrokset, kierroksen osuus ja metrit, viimeinen ja paras kierros, nopeus, vaihde, kaasu, jarru, kierrosluku, kuoppakaista, radan pinta, kilpailun ja luokan sijoitus, oman rikkeiden määrä (`driving`-rivit 5 Hz:llä ja tapahtumat)
- nyt myös `driving`-riveillä: `steering_angle`, `yaw`, `yaw_north`, `pitch`, `roll` (astetta, simulaattorin radiaaneista - vain kun muuttujaotsikko antaa yksiköksi rad), `fuel_l` (yksikkö l), `lat_accel` ja `lon_accel` (yksikkö m/s^2)
- sessiotiedoista YAML-muodossa: pelaajan autoindeksi, rata ja kokoonpano, sessiotyypit, kunkin kuljettajan nimi, auto, tiimi ja numero (session_start-rivit, meta.json)
- tarkistettu testeissä irsdk_defines.h:sta rakennettua lohkoa vastaan; ei vielä simulaattoria vastaan

**Tallennettu raakana**

- `telemetry`: uusin rivi kokonaisena, jokainen simulaattorin julkaisema muuttuja (CarIdx-taulukot jokaisesta autosta, renkaat, jousitus, nopeat `_ST`-taulukot siellä, missä simulaattorilla niitä on ...), jokaisella lukukerralla, joka löytää uuden tickin; `tick` simulaattorin tickimäärä; `used` on epätosi, kun replay toistuu
- `var_headers`: muuttujaotsikot kokonaisina (144 tavua kukin) ja kentässä `text` JSON-muodossa (nimi, tyyppi, offset, määrä, yksikkö, kuvaus), joka kerta, kun asettelu muuttuu - riittävästi lukemaan jokaisen tallennetun rivin jokaisen muuttujan
- `session_info`: YAML-teksti kokonaisena, joka kerta kun sen päivityslaskuri muuttuu (viikonloppu, sessiot ja tulokset, kuljettajat, auton asetukset, radio, kameralistat), `update` on laskuri
- `header`: 112 tavun irsdk-otsikko kokonaisena, joka kerta kun se muuttuu (versio, tila, tickrate, offsetit, rivien tickit)

**Ei saatavilla**

- sijainti reaaliajassa: jaetussa muistissa ei ole sitä; leveys-, pituusaste ja korkeus ovat vain .ibt-tiedostoissa (kun kirjaus on päällä), joita katseluohjelma lukee - watcher nimeää ne, jotka kirjoitettiin session aikana
- tickit kahden lukukerran välillä: simulaattori kirjoittaa 60 riviä sekunnissa 3 tai 4 paikkaan ja watcher lukee 10 kertaa sekunnissa, joten suurin osa tickeistä ylikirjoittuu ennen lukemista; .ibt-tiedostossa on jokainen tick, kun kirjaus on päällä

**Koko**: telemetriarivi on muutama KB (noin 5-10 KB, kun mukana ovat kaikkien autojen taulukot), tallennetaan jopa 10 kertaa sekunnissa, plus otsikko (112 tavua) yhtä usein ja sessiotiedot YAML (kymmeniä KB), kun ne muuttuvat: noin 0,2-0,4 GB radalla tunnissa ennen pakkausta; zstd pienentää sen murto-osaan (ei vielä mitattu oikeasta sessiosta)

## Testattu {#verified}

testattu jaetun muistin lohkolla, joka on rakennettu testissä irsdk-asettelun mukaan; ei testattu simulaattorin kanssa

## Lähde {#source}

[heat3d_watch/adapters/iracing.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/iracing.py)

<!-- Generated from the adapter by tools/gen_game_pages.py; change the adapter and run it again rather than editing this page. -->
