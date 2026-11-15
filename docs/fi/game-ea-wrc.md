---
title: "EA SPORTS WRC (reaaliaikadata)"
nav_order: 17
lang: "fi"
source: game-ea-wrc.md
source_hash: "c97300f65c43"
nav_exclude: true
search_exclude: true
---
# EA SPORTS WRC (reaaliaikadata) {#ea-sports-wrc-live-data}

Kun pelaat EA SPORTS WRC:tä, watcher tallentaa datan, jonka peli itse lähettää ulos. Voit katsoa sitä myöhemmin kartalta 3DHeat-katseluohjelmassa.

*Tekniset tiedot: sovitin `ea-wrc`, tyyppi [`telemetry`](sources-and-rules.md); se toimii, kun `WRC.exe` on käynnissä, ja hakee uutta dataa 0,1 s välein.*

## Mitä tallennetaan {#what-is-recorded}

- oman auton sijainti (maailman XYZ, m) 10 Hz:n taajuudella nopeuden, vaihteen, kaasun, jarrun ja erikoiskokeen matkan kanssa
- erikoiskokeen alku (erikoiskokeen kello alkaa), loppu kellon aikaan, uudelleenkäynnistykset
- hypyt (paluu tielle): `teleport` siitä, missä auto oli, `spawn` siitä, missä se on nyt
- erikoiskokeet, paras erikoiskoeaika, matka, huippunopeus

## Mistä data tulee {#where-it-comes-from}

UDP 127.0.0.1:20777, WRC:n oletusrakenteen `wrc` session_update-paketti (Documents\My Games\WRC\telemetry\config.json); kun toinen sovellus pitää porttia 20777, watcher jättää portin sille

## Miten se kytketään päälle {#how-to-switch-it-on}

`python -m heat3d_watch setup ea-wrc --apply` kytkee session_update-paketin päälle config.json-tiedostossa (varmuuskopio ensin)

Kirjoita komento terminaaliin, joka on avattu watcherin kansiossa (katso [Ennen aloitusta](before-you-start.md)). Jos se epäonnistuu, viimeinen rivi kertoo syyn; [Asennus ja käynnistys](installing-and-running.md) kertoo yleisimmät syyt.

`python -m heat3d_watch setup ea-wrc` luettelee tiedostot, joita se muuttaisi; `python -m heat3d_watch setup ea-wrc --apply` muuttaa ne ja säilyttää alkuperäisen nimellä `<file>.heat3d-backup` (katso [Komennot](commands.md#setup)). Se tulostaa `ea-wrc: changed: ...` jokaisesta muutoksesta tai `ea-wrc: nothing to change`, jos asetus on jo päällä.

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

#### DiRT Rally 2.0, Richard Burns Rally {#ea-sports-wrc-dirt-rally-20-richard-burns-rally}

UDP: WRC:n `Documents/My Games/WRC/telemetry/config.json` (`wrc`-rakenteen
`session_update`-paketti), DiRT:n `hardware_settings_config.xml`
(`<udp enabled="true" extradata="3" port="20777">`), RBR:n NGP-liitännäinen
(`udpTelemetry=1`, portti 6776). Erikoiskokeet pelin erikoiskokeen kellon mukaan
(`rally.StageSplitter`). RBR ei dokumentoi akseleitaan: ylösakseli on se, jota erikoiskoe vaihtelee
vähiten, ja se päätetään, kun sessio päättyy.

#### Kaikki tallennetaan {#everything-kept}

Rivejä tulee muutama sekunnissa; pelit lähettävät paljon enemmän. Jokainen UDP-paketti, joka saapuu - valikoissa,
kierrosten välissä, myös sellaiset, joita mikään dekoodaaja ei lue - tallennetaan muuttamattomana
session `heat.raw.parquet`-tiedostoon sen muodon nimellä (`dash-horizon`,
`session_update`, `extradata3`, `H3D1`, ...). Jokainen jaetun muistin sivu (koko alue, ei vain
dekoodatut tavut) tallennetaan joka kerta, kun se muuttuu, kartoituksen nimellä
(`acpmf_physics`, ...). `used` merkitsee sen, mistä tuli myös rivejä; `meta.json`:n
`selfCheck.completeness` laskee jokaisen tyypin (3DHeatin muunnossääntö).

Saman moduulin kautta toimivat myös: [Assetto Corsa (reaaliaikadata)](game-assetto-corsa.md), [Assetto Corsa Competizione (reaaliaikadata)](game-assetto-corsa-competizione.md), [Assetto Corsa EVO (reaaliaikadata)](game-assetto-corsa-evo.md), [Assetto Corsa Rally (reaaliaikadata)](game-assetto-corsa-rally.md), [BeamNG.drive (reaaliaikadata)](game-beamng.md), [DiRT Rally 2.0 (reaaliaikadata)](game-dirt-rally-2.md), [Forza Horizon 4 (reaaliaikadata)](game-forza-horizon-4.md), [Forza Horizon 5 (reaaliaikadata)](game-forza-horizon-5.md), [Forza Horizon 6 (reaaliaikadata)](game-forza-horizon-6.md), [Forza Motorsport (reaaliaikadata)](game-forza-motorsport.md), [Richard Burns Rally (reaaliaikadata)](game-richard-burns-rally.md).

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

`best_lap`, `best_stage`, `distance_km`, `laps`, `stages`, `top_speed_kmh`

Aaltosulkeissa oleva avain täydennetään ajon aikana (`score.{team}` on yksi avain joukkuetta kohden). Avaimet, jotka koodi ottaa pelin kenttätaulukosta tai pelin omista tilastonimistä, eivät ole tässä luettelossa; "Mitä tallennetaan" -osio nimeää ne.

## Täydellisyys {#completeness}

Watcher noudattaa 3DHeatin [muunnossääntöä](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md): mitä lähde pitää sisällään, se luetaan tai tallennetaan, eikä sitä koskaan jätetä pois. Rivien lisäksi jokainen paketti, sivu, rivi tai vastaus, jonka sovitin vastaanottaa, tallennetaan muuttamattomana session `heat.raw.parquet`-tiedostoon (sarakkeet `time`, `ms`, `type`, `used`, `payload`, `text` ja kaikki nimellä säilytetyt kentät; `used` merkitsee ne, mistä tuli myös rivejä), ja `meta.json`:n `selfCheck.completeness` laskee jokaisen `type`-arvon - `lost` on 0.

**Luettu**

- rivit 10 Hz:llä: sijainti, nopeus, vaihde, kaasu, jarru, erikoiskokeen matka, kääntymiskulma, kierrosluku, ohjaus; erikoiskokeen alku, loppu erikoiskokeen ajalla, uudelleenkäynnistykset

**Tallennettu raakana**

- jokainen paketti, joka saapuu portille, muuttamattomana pelin nopeudella; muoto: `session_update` (oletusrakenne `wrc`, 237 tavua), `wrc <n>-byte` mille tahansa muulle paketille, jonka config lähettää
- rivien lisäksi paketissa: maailman nopeus ja kiihtyvyys, auton akselit, renkaittain napojen asema ja nopeus, kosketuslaikan nopeus, jarrulämpötila, kytkin, käsijarru, pelin kello; 22 tavua (siirtymät 16-36 ja 40), joita mikään julkaistu kanavaluettelo ei nimeä

**Ei saatavilla**

- muut autot: pelit lähettävät vain pelaajan auton
- muut rakenteet ja paketit, joita telemetria-asetus voi määrittää (session_start, session_end, pause): `setup` kytkee päälle vain `session_update`-paketin; mikä tahansa muu portille lähetetty paketti tallennetaan

**Koko**: noin 65 MB tunnissa 60 paketilla sekunnissa (237 tavua plus 70 tavun kohdeotsikko; configin -1-taajuus lähettää yhden kehystä kohden, joten enemmän suuremmalla kehystaajuudella); zstd säilyttää murto-osan

## Testattu {#verified}

dekoodaus on gamecapturen kierrostallentajan (testattu dokumentoitujen rakenteiden mukaisilla paketeilla); sovitin testattu testissä rakennetuilla paketeilla, jotka lähetettiin UDP:llä; ei testattu pelin kanssa

## Lähde {#source}

[heat3d_watch/adapters/racing.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/racing.py)

<!-- Generated from the adapter by tools/gen_game_pages.py; change the adapter and run it again rather than editing this page. -->
