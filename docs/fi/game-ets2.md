---
title: "Euro Truck Simulator 2 (reaaliaikadata)"
nav_order: 19
lang: "fi"
source: game-ets2.md
source_hash: "537f0daeedbf"
nav_exclude: true
search_exclude: true
---
# Euro Truck Simulator 2 (reaaliaikadata) {#euro-truck-simulator-2-live-data}

Kun pelaat Euro Truck Simulator 2:ta, watcher tallentaa datan, jonka peli itse lähettää, jotta voit myöhemmin katsoa sen kartalla 3DHeat-katselimessa.

*Tekniset tiedot: sovitin `ets2`, tyyppi [`telemetry`](sources-and-rules.md); se toimii, kun `eurotrucks2.exe` on käynnissä, ja etsii uutta dataa 0,1 s välein.*

## Mitä tallennetaan {#what-is-recorded}

- rekan maailmansijainti (x itä, y ylös, z etelä, m) 10 Hz:n taajuudella liikkuessa ja 5 s välein seisoessa; suunta, nopeus, mittarilukema
- aloitetut työt (rahti, lähtö, kohde), toimitetut (palkkio, XP, km) ja peruutetut; sakot, tullit, lautat, junat ja tankkaukset
- lautat, junat ja ladatut tallennukset katkaisevat reitin (teleport, spawn)
- matka, huippunopeus, toimitukset, palkkiot, XP ja sakot
- pluginin koko jaettu muisti tiedostossa `heat.raw.parquet`, joka kerta kun se muuttuu

## Mistä data tulee {#where-it-comes-from}

jaettu muisti Local\SCSTelemetry, jonka kirjoittaa RenCloudin scs-sdk-plugin (revisio 12) kansiossa &lt;game>\bin\win_x64\plugins

## Miten se kytketään päälle {#how-to-switch-it-on}

Asenna scs-telemetry.dll (revisio 12) osoitteesta github.com/RenCloud/scs-sdk-plugin kansioon &lt;game>\bin\win_x64\plugins. Peli kysyy kerran käynnistyksessä, sallitaanko SDK.

## Miten se toimii {#how-it-works}

Euro Truck Simulator 2 ja American Truck Simulator: SCS:n telemetria-SDK, RenCloudin lisäosan kautta.

SCS julkaisee telemetria-SDK:n (<https://modding.scssoft.com/wiki/Documentation/Engine/SDK/Telemetry>) lisäosille, jotka pelaaja laittaa kansioon `<game>\bin\win_x64\plugins\`. Peli itse ei julkaise mitään. Laajalti käytetty lisäosa osoitteesta <https://github.com/RenCloud/scs-sdk-plugin> (MIT) kopioi SDK:n kanavat jaettuun muistiin `Local\SCSTelemetry` (32 KiB), jonka asettelu on tiedostossa `scs-telemetry/inc/scs-telemetry-common.hpp`. Tämä lukee tämän asettelun revisiota 12 (PLUGIN_REVID 12) eikä muuta: lisäosa kirjoittaa revisionsa offsettiin 40, ja muu revisio jätetään lukematta sen sijaan, että se luettaisiin väärin. Käytetyt offsetit (vyöhykkeet niin kuin otsake ne merkitsee; luonnollinen tasaus):

```text
   0  bool sdkActive          4  bool paused
  40  u32  telemetry_plugin_revision, version_major, version_minor, game (1 ETS2, 2 ATS)
  64  u32  common_ui.time_abs (in-game minutes)
 504  i32  truck_i.gear
 640  i32  gameplay_i.jobDeliveredEarnedXp
 948  f32  truck_f.speed (m/s); 952 engineRpm; 1056 truckOdometer (km)
1460  f32  gameplay_f.jobDeliveredDistanceKm
2200  f64  truck_dp.coordinateX/Y/Z (m), rotationX/Y/Z (heading, pitch, roll in turns, 0..1)
2300  char[64] config_s: truckBrand +64, truckName +192, cargo +320, cityDst +448, compDst +576,
      citySrc +704, compSrc +832; 3436 gameplay_s.fineOffence[32]
4200  i64  gameplay_ll: jobCancelledPenalty, jobDeliveredRevenue, fineAmount, tollgatePayAmount,
      ferryPayAmount, trainPayAmount
4300  bool special_b: onJob, jobFinished, jobCancelled, jobDelivered, fined, tollgate, ferry,
      train, refuel, refuelPayed
```

Rekan maailmasijainti on SCS:n maailmakehys: x itä, y ylös, z etelä, metreinä (oikeakätinen, y ylös; katselin piirtää sen sellaisenaan). Lautat, junat ja tallennuksen lataaminen siirtävät rekan ajamatta: reitti katkaistaan siinä kohdassa.

Koko jaettu muisti (lisäosan 32 KiB: kaikki yllä olevat vyöhykkeet ja ne, joita ei lueta, eli rekan asetukset, pyörät, kuluminen, rekan muut kanavat sekä se, mitä revisio asettaa tavun 4400 jälkeen, perävaunut) tallennetaan session raakatiedostoon joka kerta, kun se muuttuu, tyypillä `type` `SCSTelemetry` ja `revision` sen vieressä. Toisen revision sivu tallennetaan kokonaisena, eikä sitä lueta väärin.

Samaa moduulia käyttää myös: [American Truck Simulator (reaaliaikadata)](game-ats.md).

## Sijainnit ja akselit {#positions-and-axes}

| | |
|---|---|
| Sijainnit tallennettu | kyllä |
| Ylösakseli | `y` |
| Yksiköt | metriä (SCS:n maailma: x itä, y ylös, z etelä) |
| Peilattu katselinta varten | ei mitään |
| Yksikköskaala (`scale`: katselin kertoo sijainnit sillä) | 1 |

Nämä menevät kunkin session `meta.json`:n kohtaan `axes` ja, kun sessiossa on sijainteja, `heat.parquet`:n footeriin. Näin 3DHeat-katselin kääntää ja skaalaa rivit itse, katso [Data](the-data.md).

## Moninpeli {#multiplayer}

- Merkitty pelatuksi verkossa (`multiplayer`): **kyllä**. `games --markdown` näyttää tämän muodossa "allowed (reads only what the game publishes)".
- Tyyppi `telemetry`: se lukee vain sen, minkä peli tai alusta antaa ulos (UDP-portin tai jaetun muistin, jonka peli julkaisee). Siksi se tallentaa myös verkkopelissä, aivan kuten offline-pelissä. Lippu ratkaisee vain sen, saako muistia koskaan lukea.
- Muisti: tämän sovittimen lukema **ei koskaan**. Vain `memory`-sovittimet lukevat muistia, eikä koskaan peliin, joka on merkitty verkkopeliksi. Katso [Lähteet ja säännöt](sources-and-rules.md).

## Tilastot {#statistics-recorded}

Tilastoavaimet, jotka tämän sovittimen koodi asettaa nimeltä (session `stats` tiedostossa `meta.json` ja taulussa `stats` tiedostossa `watcher.sqlite`):

`deliveries`, `distance_km`, `fines`, `fines_total`, `jobs_cancelled`, `max_speed_kmh`, `refuels`, `revenue`, `tolls_total`, `xp`

Aaltosulkeissa oleva avain täydentyy ajon aikana (`score.{team}` on yksi avain per joukkue). Avaimet, jotka koodi ottaa pelin kenttien taulukosta tai pelin omista tilastonimistä, eivät ole tässä listassa. Kohdassa "Mitä tallennetaan" ne on nimetty.

## Täydellisyys {#completeness}

Watcher noudattaa 3DHeatin [muunninsääntöä](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md): se, mitä lähde sisältää, luetaan tai tallennetaan, eikä mitään pudoteta. Rivien lisäksi jokainen paketti, sivu, rivi tai vastaus, jonka sovitin vastaanottaa, tallennetaan sellaisenaan session tiedostoon `heat.raw.parquet` (sarakkeet `time`, `ms`, `type`, `used`, `payload`, `text` ja sen jälkeen nimellä säilytetyt kentät; `used` merkitsee ne, joista tuli myös rivejä). `meta.json`:n `selfCheck.completeness` laskee jokaisen `type`-arvon, ja `lost` on 0.

**Luettu**

- SDK:n ja tauon tila, pluginin revisio, peli ja versio, pelin sisäinen aika, rekan maailmasijainti ja suunta, nopeus, mittarilukema, rekan merkki ja nimi, rahti, lähde- ja kohdekaupunki sekä yritys, työn palkkio, XP ja matka, peruutussakko, sakot ja niiden rikkomus, tullit, lautat, junat, erikoistapahtumien liput (rivit, tapahtumat ja tilastot)
- nyt myös sijaintirivillä: `pitch` ja `roll` (asteina SDK:n kierroksista), `gear` ja `rpm`
- offsetit tarkistettu SDK:n revision 12 otsakkeen kenttä kerrallaan tehdystä kirjoituksesta, jonka vyöhykkeiden alut testit varmistavat; ei vielä pelistä

**Tallennettu raakana**

- `SCSTelemetry`: pluginin koko 32 KiB:n muistialue, jokainen luku, jonka tavut eroavat viimeksi tallennetusta kopiosta (meta.json:n `unchanged_reads` laskee muut), ja `revision` sen vieressä: jokainen vyöhyke, rekan ja perävaunun asetukset, rekan kanavat (polkimet, ohjaus, polttoaine, AdBlue, paineet, lämpötilat, kuluminen, valot, pyörät), sijainti- ja kiihtyvyysvektorit, työ- ja pelimerkkijonot sekä kaikki, mitä revisio asettaa tavun 4400 jälkeen (perävaunut). `used` on tosi, kun SDK on aktiivinen ja revisio on 12
- toisen pluginirevision sivu tallennetaan kokonaisena, `used` epätosi, sen sijaan että se luettaisiin väärin

**Ei saatavilla**

- kaikki, mitä plugin ei kopioi SDK:sta, ja kaikki, kun plugin ei ole asennettu: peli ei julkaise omaa telemetriaa
- muiden pelaajien kuorma-autot TruckersMP:ssä tai saattueissa: SDK antaa vain pelaajan oman rekan

**Koko**: 32 KiB jopa 10 kertaa sekunnissa ajaessa (jokainen luku eroaa silloin): noin 1,2 Gt tunnissa ennen pakkausta, yksi kopio tauon aikana. Suurin osa sivusta on nollia ja asetuksia, jotka eivät muutu, joten zstd pienentää sitä moninkertaisesti (ei vielä mitattu oikeasta sessiosta).

## Todennettu {#verified}

Testattu jaetulla muistilla, joka rakennettiin pluginin revision 12 otsakeasettelusta. Peliä vastaan ei ole testattu.

## Lähdekoodi {#source}

[heat3d_watch/adapters/ets2.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/ets2.py)

<!-- Generated from the adapter by tools/gen_game_pages.py; change the adapter and run it again rather than editing this page. -->
