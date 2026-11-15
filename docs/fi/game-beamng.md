---
title: "BeamNG.drive (reaaliaikadata)"
nav_order: 7
lang: "fi"
source: game-beamng.md
source_hash: "1c23a869a62f"
nav_exclude: true
search_exclude: true
---
# BeamNG.drive (reaaliaikadata) {#beamngdrive-live-data}

Kun pelaat BeamNG.drive:a, watcher tallentaa datan, jonka peli itse lähettää, jotta voit myöhemmin katsoa sen kartalla 3DHeat-katselimessa.

*Tekniset tiedot: sovitin `beamng`, tyyppi [`telemetry`](sources-and-rules.md); se toimii, kun `BeamNG.drive.x64.exe` tai `BeamNG.drive.exe` on käynnissä, ja etsii uutta dataa 0,1 s välein.*

## Mitä tallennetaan {#what-is-recorded}

- oman auton sijainti (maailma, m, käännetty Y ylös -muotoon) 10 Hz:n taajuudella, nopeus, vaihde, kaasu ja jarru
- ajon alku, nollaukset (uudelleensijoitus) ja kierrokset siitä kohdasta, josta ajo alkoi
- kierrokset, paras kierros, matka ja huippunopeus

## Mistä data tulee {#where-it-comes-from}

UDP 127.0.0.1:4460 heat3d-protokollamodista (mods/beamng/heat3d tässä repositoriossa)

## Miten se kytketään päälle {#how-to-switch-it-on}

`python -m heat3d_watch setup beamng --apply` asentaa modin. Sen jälkeen: Options > Other > Protocols > "others"

Kirjoita komento terminaaliin, joka on avattu watcherin kansiossa (katso [Ennen aloittamista](before-you-start.md)). Jos se epäonnistuu, viimeinen rivi kertoo syyn; [Asennus ja käyttö](installing-and-running.md) kertoo yleisimmät syyt.

`python -m heat3d_watch setup beamng` listaa tiedostot, joita se muuttaisi; `python -m heat3d_watch setup beamng --apply` muuttaa ne ja säilyttää alkuperäisen nimellä `<file>.heat3d-backup` (katso [Komennot](commands.md#setup)). Jokaisesta muutoksesta se tulostaa `beamng: changed: ...`, tai `beamng: nothing to change`, jos se on jo päällä.

## Miten se toimii {#how-it-works}

Kilpailupelien oma telemetria: Forza, Assetto Corsa -pelit, rallipelit ja BeamNG, tallennettuna reitteinä, kierroksina ja erikoiskokeina.

Jokainen tässä mainittu peli julkaisee telemetriansa tarkoituksella, kojelautoja ja liikkuvia ohjausjärjestelmiä varten. Mitään ei injektoida, eikä mitään luoda, mitä peli ei jaa ulos. Dekoodausta ei kirjoiteta kahteen kertaan: se on gamecapturen kierrostallentimet kansiossa `heat3d_capture/telemetry` (3DHeat GameCapture), kopioituna kansioon `heat3d_watch/decoders` (testattu siellä julkaistuja asetteluja vastaavilla paketeilla). Tämä moduuli muuttaa niiden kehykset watcherin riveiksi: auton sijainnin muutaman kerran sekunnissa nopeuden, vaihteen ja pedaalien kanssa, tapahtuman jokaisesta kierroksesta tai erikoiskokeesta sekä ne luvut, jotka kuljettaja pitää: kierrokset, paras kierros, matka ja huippunopeus.

#### Forza (Horizon 4/5/6, Motorsport) {#forza-horizon-456-motorsport}

"Data Out" UDP, kytketty päälle pelin HUD- ja Gameplay-asetuksissa, osoitteeseen 127.0.0.1 portti 5300, muoto Dash. Yksi paketti per simulaatiotikki; dash-lohkon offset löytyy paketeista (`forza.detect_layout`). Maailman metrit, Y ylös. Maailma on vasenkätinen, ja se piirretään sellaisena kuin se lähetetään, kuten kierrostallennin tekee (Forza Motorsportin ja Forza Horizonin "Data Out" -dokumentaatio).
Peli lähettää yhteen porttiin, ja FH Companion ja muut Data Out -sovellukset kuuntelevat samaa porttia. Kaksi ohjelmaa ei voi jakaa sitä: Windowsissa 127.0.0.1:een sidottu socket saa paketit, ja samaan porttiin kaikille osoitteille sidottu socket ei saa mitään, kumpi tahansa tuli ensin. Siksi watcher odottaa hetken pelin käynnistymisen jälkeen ennen kuin ottaa portin, ei koskaan ota sitä sovellukselta, joka sitä jo pitää, ja vapauttaa sen heti, kun toinen sovellus alkaa kuunnella siinä. Kun watcher pitää porttia, se välittää jokaisen paketin muuttamattomana osoitteeseen 127.0.0.1:5301. Aseta FH Companionin porttikenttä (sen telemetria-välilehdellä) arvoon 5301, niin molemmat tallentavat.

#### BeamNG.drive {#beamngdrive}

`heat3d`-protokollamodi, jonka gamecapture toimittaa (UDP 4460, Options > Other > Protocols > "others"). BeamNG:n Z ylös -maailma käännetään Y ylös -muotoon samoin kuin `beamng.py` tekee.

#### Kaikki tallennetaan {#everything-kept}

Rivejä tulee muutama sekunnissa, mutta pelit lähettävät paljon enemmän. Jokainen saapuva UDP-paketti, myös valikoissa, kierrosten välissä ja paketit, joita mikään dekooderi ei lue, tallennetaan sellaisenaan session tiedostoon `heat.raw.parquet` omalla muodollaan (`dash-horizon`, `session_update`, `extradata3`, `H3D1` ...). Jokainen jaetun muistin sivu tallennetaan koko muistialueena, ei vain dekoodattuina tavuina, aina kun se muuttuu, ja nimenä on muistialueen nimi (`acpmf_physics` ...). `used` merkitsee ne, joista tuli myös rivejä. `meta.json`:n `selfCheck.completeness` laskee jokaisen tyypin (3DHeatin muunninsääntö).

Samaa moduulia käyttävät myös: [Assetto Corsa (reaaliaikadata)](game-assetto-corsa.md), [Assetto Corsa Competizione (reaaliaikadata)](game-assetto-corsa-competizione.md), [Assetto Corsa EVO (reaaliaikadata)](game-assetto-corsa-evo.md), [Assetto Corsa Rally (reaaliaikadata)](game-assetto-corsa-rally.md), [DiRT Rally 2.0 (reaaliaikadata)](game-dirt-rally-2.md), [EA SPORTS WRC (reaaliaikadata)](game-ea-wrc.md), [Forza Horizon 4 (reaaliaikadata)](game-forza-horizon-4.md), [Forza Horizon 5 (reaaliaikadata)](game-forza-horizon-5.md), [Forza Horizon 6 (reaaliaikadata)](game-forza-horizon-6.md), [Forza Motorsport (reaaliaikadata)](game-forza-motorsport.md), [Richard Burns Rally (reaaliaikadata)](game-richard-burns-rally.md).

## Sijainnit ja akselit {#positions-and-axes}

| | |
|---|---|
| Sijainnit tallennettu | kyllä |
| Ylösakseli | `y` |
| Yksiköt | metriä (BeamNG:n Z ylös -maailma käännetty X-akselin ympäri, kuten kierrostallennin tekee) |
| Peilattu katselinta varten | ei mitään |
| Yksikköskaala (`scale`: katselin kertoo sijainnit sillä) | 1 |

Nämä menevät kunkin session `meta.json`:n kohtaan `axes` ja, kun sessiossa on sijainteja, `heat.parquet`:n footeriin. Näin 3DHeat-katselin kääntää ja skaalaa rivit itse, katso [Data](the-data.md).

## Moninpeli {#multiplayer}

- Merkitty pelatuksi verkossa (`multiplayer`): **ei**. `games --markdown` näyttää tämän muodossa "single-player".
- Tyyppi `telemetry`: se lukee vain sen, minkä peli tai alusta antaa ulos (UDP-portin tai jaetun muistin, jonka peli julkaisee). Siksi se tallentaa myös verkkopelissä, aivan kuten offline-pelissä. Lippu ratkaisee vain sen, saako muistia koskaan lukea.
- Muisti: tämän sovittimen lukema **ei koskaan**. Vain `memory`-sovittimet lukevat muistia, eikä koskaan peliin, joka on merkitty verkkopeliksi. Katso [Lähteet ja säännöt](sources-and-rules.md).

## Tilastot {#statistics-recorded}

Tilastoavaimet, jotka tämän sovittimen koodi asettaa nimeltä (session `stats` tiedostossa `meta.json` ja taulussa `stats` tiedostossa `watcher.sqlite`):

`best_lap`, `distance_km`, `laps`, `top_speed_kmh`

Aaltosulkeissa oleva avain täydentyy ajon aikana (`score.{team}` on yksi avain per joukkue). Avaimet, jotka koodi ottaa pelin kenttien taulukosta tai pelin omista tilastonimistä, eivät ole tässä listassa. Kohdassa "Mitä tallennetaan" ne on nimetty.

## Täydellisyys {#completeness}

Watcher noudattaa 3DHeatin [muunninsääntöä](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md): se, mitä lähde sisältää, luetaan tai tallennetaan, eikä mitään pudoteta. Rivien lisäksi jokainen paketti, sivu, rivi tai vastaus, jonka sovitin vastaanottaa, tallennetaan sellaisenaan session tiedostoon `heat.raw.parquet` (sarakkeet `time`, `ms`, `type`, `used`, `payload`, `text` ja sen jälkeen nimellä säilytetyt kentät; `used` merkitsee ne, joista tuli myös rivejä). `meta.json`:n `selfCheck.completeness` laskee jokaisen `type`-arvon, ja `lost` on 0.

**Luettu**

- rivit 10 Hz:n taajuudella: sijainti, nopeus, vaihde, kaasu, jarru, yaw, kierrosluku, ohjaus; ajon alku, nollaukset, kierrokset

**Tallennettu raakana**

- jokainen paketti, joka saavuttaa portin, kokonaisena, modin 100 Hz:n taajuudella: `H3D1` (modin 160 tavun rakenne: kello, sijainti, nopeus, auton akselit, yaw-nopeus, yhdeksän syötettä, kunkin pyörän pintanopeus, pyörimisnopeus, kuorma ja maan materiaali), `<n>-byte` kaikelle muulle

**Ei saatavilla**

- se, mitä modi ei lähetä: BeamNG:lla ei ole kiinteää telemetriapakettia, joten kanavat ovat ne, jotka heat3d-modi on valinnut (muut ajoneuvot, vauriot ja kartan nimi eivät ole siinä)

**Koko**: noin 80 Mt tunnissa ennen pakkausta (100 pakettia sekunnissa, 160 tavua kukin, plus 70 tavun kohdeotsake)

## Todennettu {#verified}

Dekoodaus on gamecapturen kierrostallentimen (testattu paketeilla, jotka rakennettiin modin rakenteesta). Sovitin on testattu tällaisilla paketeilla. Modi on testaamaton pelissä.

## Lähdekoodi {#source}

[heat3d_watch/adapters/racing.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/racing.py)

<!-- Generated from the adapter by tools/gen_game_pages.py; change the adapter and run it again rather than editing this page. -->
