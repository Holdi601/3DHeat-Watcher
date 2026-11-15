---
title: "Forza Motorsport (reaaliaikadata)"
nav_order: 24
lang: "fi"
source: game-forza-motorsport.md
source_hash: "d411fbb6ebea"
nav_exclude: true
search_exclude: true
---
# Forza Motorsport (reaaliaikadata) {#forza-motorsport-live-data}

Kun pelaat Forza Motorsportia, watcher tallentaa datan, jonka peli itse lähettää ulos. Voit katsoa sitä myöhemmin kartalta 3DHeat-katseluohjelmassa.

*Tekniset tiedot: sovitin `forza-motorsport`, tyyppi [`telemetry`](sources-and-rules.md); se toimii, kun `forza_steamworks_release_final.exe`, `forza_gaming.desktop.x64_release_final.exe` tai `ForzaMotorsport7.exe` on käynnissä, ja hakee uutta dataa 0,1 s välein.*

## Mitä tallennetaan {#what-is-recorded}

- oman auton sijainti (maailman XYZ, m) 10 Hz:n taajuudella nopeuden, vaihteen, kaasun, jarrun ja kierroksen kanssa
- ajon alku ja loppu (session_start/session_end), kierrokset pelin kierrosajalla
- kilpailun alku ja maali kilpailun sijoituksella
- hypyt (kelaus, pikamatka): `teleport` siitä, missä auto oli, `spawn` siitä, missä se on nyt
- kierrokset, paras kierros, matka, huippunopeus, kilpailut

## Mistä data tulee {#where-it-comes-from}

Forza Data Out, UDP 127.0.0.1:5300 (Dash-muoto); jokainen paketti välitetään muuttamattomana osoitteeseen 127.0.0.1:5301

## Miten se kytketään päälle {#how-to-switch-it-on}

Pelissä: Settings > HUD and Gameplay > Data Out On, IP 127.0.0.1, portti 5300 (Motorsport: muoto Dash). FH Companion tai muu Data Out -sovellus: aseta sen portti arvoon 5301 - watcher välittää jokaisen paketin eteenpäin; kun toinen sovellus kuuntelee porttia 5300, watcher jättää portin sille eikä tallenna mitään

## Miten se toimii {#how-it-works}

Kilpailupelien omaa telemetriaa: Forza, Assetto Corsa -pelit, rallipelit
ja BeamNG, tallennettuna reitteinä, kierroksina ja erikoiskokeina.

Kaikki tässä mainitut pelit julkaisevat telemetriansa tarkoituksella, mittaristoille
ja liikkeenohjausjärjestelmille. Mitään ei injektoida, eikä peli jaa ulos mitään, mitä ei ole
tarkoitettu luettavaksi. Dekoodausta ei ole kirjoitettu kahteen kertaan: se on GameCapturen
kierrostallentajat 3DHeat GameCapturen `heat3d_capture/telemetry`-kansiosta, kopioituna
`heat3d_watch/decoders`-kansioon (testattu siellä julkaistuja rakenteita vastaavilla paketeilla), ja
tämä moduuli muuttaa niiden kehykset watcherin riveiksi: auton sijainti muutaman kerran
sekunnissa nopeuden, vaihteen ja polkimien kanssa, tapahtuma jokaisesta kierroksesta tai
erikoiskokeesta sekä ne luvut, joita kuljettaja pitää kirjaa: kierrokset, paras kierros,
matka, huippunopeus.

#### Forza (Horizon 4/5/6, Motorsport) {#forza-horizon-456-motorsport}

"Data Out" -UDP, joka kytketään päälle pelin HUD- ja Gameplay-asetuksissa, osoitteeseen
127.0.0.1 portti 5300, muoto Dash. Yksi paketti jokaista simulaation tikkiä kohden; dash-lohkon
siirtymä löydetään paketeista (`forza.detect_layout`). Maailman metrit, Y ylös; maailma on
vasenkätinen, ja se piirretään lähetetyssä muodossa, kuten kierrostallentaja tekee (Forza Motorsportin ja
Forza Horizonin "Data Out" -dokumentaatio).
Peli lähettää yhteen porttiin, ja FH Companion ja muut Data Out -sovellukset kuuntelevat samaa.
Kaksi ohjelmaa ei voi jakaa sitä: Windowsissa 127.0.0.1-osoitteeseen sidottu
soketti saa paketit, ja samaan porttiin kaikkiin osoitteisiin sidottu ei saa mitään, siitä riippumatta
kumpi tuli ensin. Siksi watcher odottaa hetken pelin käynnistymisen jälkeen ennen kuin ottaa portin,
ei koskaan ota sitä sovellukselta, joka pitää siitä kiinni, ja vapauttaa sen heti, kun toinen sovellus
alkaa kuunnella sitä. Kun watcher pitää porttia, se välittää jokaisen paketin muuttamattomana
osoitteeseen 127.0.0.1:5301 - aseta FH Companionin porttikenttä (sen telemetria-välilehdellä) arvoon 5301,
niin molemmat tallentavat.

#### Kaikki tallennetaan {#everything-kept}

Rivejä tulee muutama sekunnissa; pelit lähettävät paljon enemmän. Jokainen UDP-paketti, joka saapuu - valikoissa,
kierrosten välissä, myös sellaiset, joita mikään dekoodaaja ei lue - tallennetaan muuttamattomana
session `heat.raw.parquet`-tiedostoon sen muodon nimellä (`dash-horizon`,
`session_update`, `extradata3`, `H3D1`, ...). Jokainen jaetun muistin sivu (koko alue, ei vain
dekoodatut tavut) tallennetaan joka kerta, kun se muuttuu, kartoituksen nimellä
(`acpmf_physics`, ...). `used` merkitsee sen, mistä tuli myös rivejä; `meta.json`:n
`selfCheck.completeness` laskee jokaisen tyypin (3DHeatin muunnossääntö).

Saman moduulin kautta toimivat myös: [Assetto Corsa (reaaliaikadata)](game-assetto-corsa.md), [Assetto Corsa Competizione (reaaliaikadata)](game-assetto-corsa-competizione.md), [Assetto Corsa EVO (reaaliaikadata)](game-assetto-corsa-evo.md), [Assetto Corsa Rally (reaaliaikadata)](game-assetto-corsa-rally.md), [BeamNG.drive (reaaliaikadata)](game-beamng.md), [DiRT Rally 2.0 (reaaliaikadata)](game-dirt-rally-2.md), [EA SPORTS WRC (reaaliaikadata)](game-ea-wrc.md), [Forza Horizon 4 (reaaliaikadata)](game-forza-horizon-4.md), [Forza Horizon 5 (reaaliaikadata)](game-forza-horizon-5.md), [Forza Horizon 6 (reaaliaikadata)](game-forza-horizon-6.md), [Richard Burns Rally (reaaliaikadata)](game-richard-burns-rally.md).

## Sijainnit ja akselit {#positions-and-axes}

| | |
|---|---|
| Sijainnit tallennetaan | kyllä |
| Ylösakseli | `y` |
| Yksiköt | metriä; Forzan maailma on vasenkätinen, piirretään lähetetyssä muodossa kuten kierrostallentaja tekee |
| Peilattu katseluohjelmaa varten | ei mitään |
| Yksikköskaala (`scale`: katseluohjelma kertoo sijainnit tällä) | 1 |

Nämä menevät jokaisen session `meta.json`-tiedoston kohtaan `axes` ja, kun sessiossa on sijainteja, `heat.parquet`-tiedoston alatunnisteeseen, joten 3DHeat-katseluohjelma kääntää ja skaalaa rivit itse - katso [Data](the-data.md).

## Moninpeli {#multiplayer}

- Merkitty pelatuksi verkossa (`multiplayer`): **kyllä**. `games --markdown` näyttää tämän muodossa "sallittu (lukee vain sen, minkä peli julkaisee)".
- Tyyppi `telemetry`: se lukee vain sen, minkä peli tai alusta antaa ulos (UDP-portin tai jaetun muistin, jonka peli julkaisee), joten se tallentaa myös verkkopelissä, aivan kuten offline-pelissäkin; lippu päättää vain sen, saako muistia koskaan lukea.
- Muisti: tämä sovitin **ei koskaan** lue muistia. Vain `memory`-sovittimet lukevat muistia, eikä koskaan peliin, joka on merkitty pelatuksi verkossa - katso [Lähteet ja säännöt](sources-and-rules.md).

## Tilastot {#statistics-recorded}

Tilastoavaimet, jotka tämän sovittimen koodi asettaa nimeltä (jokaisen session `stats` `meta.json`-tiedostossa ja taulukossa `stats` tiedostossa `watcher.sqlite`):

`best_lap`, `distance_km`, `laps`, `races`, `top_speed_kmh`

Aaltosulkeissa oleva avain täydennetään ajon aikana (`score.{team}` on yksi avain joukkuetta kohden). Avaimet, jotka koodi ottaa pelin kenttätaulukosta tai pelin omista tilastonimistä, eivät ole tässä luettelossa; "Mitä tallennetaan" -osio nimeää ne.

## Täydellisyys {#completeness}

Watcher noudattaa 3DHeatin [muunnossääntöä](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md): mitä lähde pitää sisällään, se luetaan tai tallennetaan, eikä sitä koskaan jätetä pois. Rivien lisäksi jokainen paketti, sivu, rivi tai vastaus, jonka sovitin vastaanottaa, tallennetaan muuttamattomana session `heat.raw.parquet`-tiedostoon (sarakkeet `time`, `ms`, `type`, `used`, `payload`, `text` ja kaikki nimellä säilytetyt kentät; `used` merkitsee ne, mistä tuli myös rivejä), ja `meta.json`:n `selfCheck.completeness` laskee jokaisen `type`-arvon - `lost` on 0.

**Luettu**

- rivit 10 Hz:llä: sijainti, nopeus, vaihde, kaasu, jarru, kierros, kääntymiskulma/kallistukset/rullaus (rad), kierrosluku, ohjaus (-1..1); session_start auton järjestysnumerolla, luokalla, PI:llä ja vetojärjestelmällä; kierrokset pelin kierrosajalla; kilpailun sijoitus

**Tallennettu raakana**

- jokainen paketti, joka saapuu portille, muuttamattomana pelin nopeudella (yksi per simulaation tikki), muoto: `dash-horizon` (324 tavua, Forza Horizon), `dash` (311, Motorsport 7), `dash-fm2023` (331, Forza Motorsport 2023: renkaiden kuluminen ja radan tunnus), `sled` (232, ei sijaintia), `<n>-byte` kaikelle muulle - mukaan lukien valikkopaketit (isRaceOn 0), paketit, jotka pidetään, kunnes rivimuoto on todistettu, ja ne noin 13 tavua Horizon-paketista, joita mikään julkaistu muoto ei nimeä
- Sled-lohkon jokainen pyöräkanava (luistosuhde, luistokulma, yhdistetty luisto, jousitus, pyörän nopeus, rumble, lätäkkö), kiihtyvyydet, kulmanopeus, teho, vääntömomentti, boost, polttoaine, renkaiden lämpötilat, kytkin, käsijarru, ajolinja, AI:n jarrueron: kaikki paketeissa ja dekoodataan niistä `decoders/fulllap.decode_full`-funktiolla

**Ei saatavilla**

- muut autot: Data Out kuvaa vain pelaajan auton
- radan tai reitin nimi: Forza Horizon ei lähetä sitä koskaan; Motorsport 2023 lähettää vain radan numeron
- paketit, kun toinen sovellus (FH Companion) pitää UDP-porttia 5300: watcher jättää portin sille

**Koko**: noin 85 MB tunnissa ennen pakkausta (60 pakettia sekunnissa, 324 tavua plus 70 tavun kohdeotsikko); peräkkäiset paketit eroavat vähän, joten zstd säilyttää murto-osan

## Testattu {#verified}

dekoodaus on gamecapturen kierrostallentajan (testattu Data Out -rakenteen mukaisilla paketeilla); sovitin testattu synteettisillä paketeilla ja tallennetuilla kierrosradoilla, jotka toistettiin paketteina; ei testattu itse pelin kanssa

## Lähde {#source}

[heat3d_watch/adapters/racing.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/racing.py)

<!-- Generated from the adapter by tools/gen_game_pages.py; change the adapter and run it again rather than editing this page. -->
