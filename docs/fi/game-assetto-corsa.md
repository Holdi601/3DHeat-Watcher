---
title: "Assetto Corsa (reaaliaikadata)"
nav_order: 2
lang: "fi"
source: game-assetto-corsa.md
source_hash: "9132272cc104"
nav_exclude: true
search_exclude: true
---
# Assetto Corsa (reaaliaikadata) {#assetto-corsa-live-data}

Kun pelaat Assetto Corsaa, watcher tallentaa datan, jonka peli itse lähettää ulos. Voit katsoa sitä myöhemmin kartalta 3DHeat-katseluohjelmassa.

*Tekniset tiedot: sovitin `assetto-corsa`, tyyppi [`telemetry`](sources-and-rules.md); se toimii, kun `acs.exe` tai `acs_x86.exe` on käynnissä, ja hakee uutta dataa 0,1 s välein.*

## Mitä tallennetaan {#what-is-recorded}

- oman auton sijainti (maailman XYZ, m: renkaiden maakosketuspisteiden keskiarvo) 10 Hz:n taajuudella, nopeus, vaihde, kaasu ja jarru
- istunnon alku ja loppu, radan ja auton nimi pelin mukaan
- kierrokset pelin kierrolaskurin mukaan ja niiden kierrosaika
- hypyt (takaisin varikolle, uudelleenkäynnistys): `teleport` siitä, missä auto oli, `spawn` siitä, missä se on nyt
- kierrokset, paras kierros, matka, huippunopeus

## Mistä data tulee {#where-it-comes-from}

jaettu muisti Local\acpmf_physics, Local\acpmf_graphics, Local\acpmf_static

## Miten se kytketään päälle {#how-to-switch-it-on}

Mitään ei tarvitse kytkeä: watcher lukee lähteen sellaisena kuin peli tai alusta sen antaa.

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

#### Assetto Corsa, ACC, AC EVO, AC Rally {#assetto-corsa-acc-ac-evo-ac-rally}

Jaettu muisti, jonka peli kirjoittaa sovelluksille: `Local\acpmf_physics`,
`Local\acpmf_graphics`, `Local\acpmf_static` (AC EVO: `Local\acevo_pmf_*`).
Avataan vain luku -tilassa, ja vasta kun peli on luonut sen (`simracing_shm`). Sijainti on
neljän renkaan maakosketuspisteen keskiarvo, maailman metreinä, Y ylös.
Kierrokset pelin laskurin mukaan (AC, ACC) tai lähtöpisteen uudelleen ylittämisen mukaan
(AC EVO, AC Rally), kuten `kunos.py` tekee kierrostallentajalle.

#### Kaikki tallennetaan {#everything-kept}

Rivejä tulee muutama sekunnissa; pelit lähettävät paljon enemmän. Jokainen UDP-paketti, joka saapuu - valikoissa,
kierrosten välissä, myös sellaiset, joita mikään dekoodaaja ei lue - tallennetaan muuttamattomana
session `heat.raw.parquet`-tiedostoon sen muodon nimellä (`dash-horizon`,
`session_update`, `extradata3`, `H3D1`, ...). Jokainen jaetun muistin sivu (koko alue, ei vain
dekoodatut tavut) tallennetaan joka kerta, kun se muuttuu, kartoituksen nimellä
(`acpmf_physics`, ...). `used` merkitsee sen, mistä tuli myös rivejä; `meta.json`:n
`selfCheck.completeness` laskee jokaisen tyypin (3DHeatin muunnossääntö).

Saman moduulin kautta toimivat myös: [Assetto Corsa Competizione (reaaliaikadata)](game-assetto-corsa-competizione.md), [Assetto Corsa EVO (reaaliaikadata)](game-assetto-corsa-evo.md), [Assetto Corsa Rally (reaaliaikadata)](game-assetto-corsa-rally.md), [BeamNG.drive (reaaliaikadata)](game-beamng.md), [DiRT Rally 2.0 (reaaliaikadata)](game-dirt-rally-2.md), [EA SPORTS WRC (reaaliaikadata)](game-ea-wrc.md), [Forza Horizon 4 (reaaliaikadata)](game-forza-horizon-4.md), [Forza Horizon 5 (reaaliaikadata)](game-forza-horizon-5.md), [Forza Horizon 6 (reaaliaikadata)](game-forza-horizon-6.md), [Forza Motorsport (reaaliaikadata)](game-forza-motorsport.md), [Richard Burns Rally (reaaliaikadata)](game-richard-burns-rally.md).

## Sijainnit ja akselit {#positions-and-axes}

| | |
|---|---|
| Sijainnit tallennetaan | kyllä |
| Ylösakseli | `y` |
| Yksiköt | metriä |
| Peilattu katseluohjelmaa varten | ei mitään |
| Yksikköskaala (`scale`: katseluohjelma kertoo sijainnit tällä) | 1 |

Nämä menevät jokaisen session `meta.json`-tiedoston kohtaan `axes` ja, kun sessiossa on sijainteja, `heat.parquet`-tiedoston alatunnisteeseen, joten 3DHeat-katseluohjelma kääntää ja skaalaa rivit itse - katso [Data](the-data.md).

## Moninpeli {#multiplayer}

- Merkitty pelatuksi verkossa (`multiplayer`): **kyllä**. `games --markdown` näyttää tämän muodossa "sallittu (lukee vain sen, minkä peli julkaisee)".
- Tyyppi `telemetry`: se lukee vain sen, minkä peli tai alusta antaa ulos (UDP-portin tai jaetun muistin, jonka peli julkaisee), joten se tallentaa myös verkkopelissä, aivan kuten offline-pelissäkin; lippu päättää vain sen, saako muistia koskaan lukea.
- Muisti: tämä sovitin **ei koskaan** lue muistia. Vain `memory`-sovittimet lukevat muistia, eikä koskaan peliin, joka on merkitty pelatuksi verkossa - katso [Lähteet ja säännöt](sources-and-rules.md).

## Tilastot {#statistics-recorded}

Tilastoavaimet, jotka tämän sovittimen koodi asettaa nimeltä (jokaisen session `stats` `meta.json`-tiedostossa ja taulukossa `stats` tiedostossa `watcher.sqlite`):

`best_lap`, `best_stage`, `distance_km`, `laps`, `race_position`, `stages`, `top_speed_kmh`

Aaltosulkeissa oleva avain täydennetään ajon aikana (`score.{team}` on yksi avain joukkuetta kohden). Avaimet, jotka koodi ottaa pelin kenttätaulukosta tai pelin omista tilastonimistä, eivät ole tässä luettelossa; "Mitä tallennetaan" -osio nimeää ne.

## Täydellisyys {#completeness}

Watcher noudattaa 3DHeatin [muunnossääntöä](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md): mitä lähde pitää sisällään, se luetaan tai tallennetaan, eikä sitä koskaan jätetä pois. Rivien lisäksi jokainen paketti, sivu, rivi tai vastaus, jonka sovitin vastaanottaa, tallennetaan muuttamattomana session `heat.raw.parquet`-tiedostoon (sarakkeet `time`, `ms`, `type`, `used`, `payload`, `text` ja kaikki nimellä säilytetyt kentät; `used` merkitsee ne, mistä tuli myös rivejä), ja `meta.json`:n `selfCheck.completeness` laskee jokaisen `type`-arvon - `lost` on 0.

**Luettu**

- rivit 10 Hz:llä fysiikkasivulta: sijainti (renkaiden maakosketuspisteiden keskiarvo), nopeus, vaihde, kaasu, jarru, kääntymiskulma/kallistukset/rullaus (rad), kierrosluku, ohjaus (sellaisena kuin sivulla on); session alku radan ja auton kanssa staattiselta sivulta; kierrokset, kilpailun sijoitus

**Tallennettu raakana**

- jokainen sivu kokonaisena - koko kartoitusalue, ei vain dekoodatut tavut - joka kerta, kun sen tavut muuttuvat, watcherin 10 Hz:n lukukerralla: `acpmf_physics`, `acpmf_graphics`, `acpmf_static`; lukukerta, joka on tavu tavulta sama kuin edellinen, lasketaan meta.json:n `unchanged_reads`-kenttään eikä tallenneta uudelleen
- kaikki, mikä on dekoodattu vain kierrostiedostoja varten (`decoders/kunos.py`: renkaittain luistot, kuormat, paineet, lämpötilat, kallistukset, jousitus, kosketuspisteet, jarrulämpötilat, luistosuhde ja -kulma; maailman ja paikallinen nopeus, kulmanopeus, avustimet), on noilla sivuilla

**Ei saatavilla**

- muiden autojen sijainnit: sivut kuvaavat vain pelaajan auton (ACC:n graphics-sivulla on joissakin versioissa auto-id:t ja koordinaatit muille autoille - ne tallennetaan raakana sivulle, eivät dekoodata)
- fysiikkatikit watcherin lukujen välillä: peli kirjoittaa sivun uudelleen fysiikkataajuudellaan (jopa 333 Hz), ja watcher lukee 10 kertaa sekunnissa

**Koko**: noin 150-300 MB tunnissa ennen pakkausta (4 KB:n alue per sivu, enintään 10 muutosta sekunnissa); sivut ovat enimmäkseen nollia, ja zstd säilyttää pienen murto-osan

## Testattu {#verified}

dekoodaus on gamecapturen kierrostallentajan (testattu synteettisillä sivuilla); sovitin testattu testissä rakennetulla jaetulla muistilla dokumentoidun rakenteen mukaan; ei testattu pelin kanssa

## Lähde {#source}

[heat3d_watch/adapters/racing.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/racing.py)

<!-- Generated from the adapter by tools/gen_game_pages.py; change the adapter and run it again rather than editing this page. -->
