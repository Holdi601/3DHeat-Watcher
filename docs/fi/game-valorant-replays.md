---
title: "VALORANT (replayt)"
nav_order: 44
lang: "fi"
source: game-valorant-replays.md
source_hash: "a2c4144797e9"
nav_exclude: true
search_exclude: true
---
# VALORANT (replayt) {#valorant-replays}

Kun ottelu VALORANTissa päättyy, watcher muuttaa pelin tallentaman replayn tiedostoiksi, joita voit katsoa tilastoina ja aikajanana.

*Tekniset tiedot: sovitin `valorant-replays`, tyyppi [`replay`](sources-and-rules.md); se toimii koko ajan (ei odota pelin käynnistymistä) ja hakee uutta dataa 5 s välein.*

## Mitä tallennetaan {#what-is-recorded}

- kartta, ottelun tunnus ja valitut agentit; replayn tietolohko (pituus, versiot, nimi, tallennusaika, pakkaus- ja salausliput)
- palvelimen tapahtumaaikajana: tapot (tappaja ja uhri verkkotunnuksina), kierrosten alut, piikit asetettu, purettu ja räjähtänyt, ultimate-kyvyt käytetty, puolten vaihdot - kukin tunnuksensa ja metatietojensa kanssa
- jokainen tiedoston osa kokonaisena heat.raw.parquet-tiedostossa; ei dekoodattuna: sijainnit, nimet tai pisteet - ne ovat hämärretyssä virrassa

## Mistä data tulee {#where-it-comes-from}

replayt, jotka VALORANT tallentaa: %LOCALAPPDATA%/VALORANT/Saved/Demos/\*.vrf (vain ne osat, jotka eivät ole hämärrettyjä)

## Miten se kytketään päälle {#how-to-switch-it-on}

tallenna replay VALORANTissa (ura > ottelu > lataa replay) ja asenna lukija: github.com/Holdi601/3DHeat-Ext-Riot (`heat3d-riot-replays`)

Asetukset ympäristömuuttujista:

- `HEAT3D_RIOT_REPLAYS`: lukijan kansio (kloonaus tai purettu julkaisu), kun se ei ole asennettu tai watcherin vieressä

## Miten se toimii {#how-it-works}

League of Legends- ja Valorant-replayt: se osa, joka niistä voidaan lukea sellaisenaan.

Molemmat pelit tallentavat replayt pelaajan levylle, ja molemmat suojaavat sisältönsä:
hetkeltä toiselle tapahtuva pelidata on hämärretty, ja hämäröinti vaihtuu joka päivityksen mukana,
jotta sitä ei voi käyttää huijaamiseen. Tätä osaa ei pureta
missään 3DHeatissa. Se, mitä kukin tiedosto
kertoo avoimesti, luetaan, ja loppu tallennetaan sellaisenaan: jokainen tiedoston osa kokonaisena
session `heat.raw.parquet`-tiedostossa (3DHeatin muunnossääntö, docs/converters.md katseluohjelman
repositoriossa), ja se lasketaan meta.json:n `selfCheck.completeness`-kentässä.

Watcher ei lue tiedostoja itse: sen tekee ulkoinen lukija (3DHeat
Riot, github.com/Holdi601/3DHeat-Ext-Riot, `exporters/ext/riot-replays`,
komento `heat3d-riot-replays`), oma projektinsa. Jos lukija löytyy PATHista, on asennettu tai watcherin vieressä, se lukee jokaisen uuden replayn;
jos sitä ei ole, watcher kertoo kerran, miten se asennetaan. Mitä lukija lukee, sen watcher tallentaa
sessioon; alla oleva Match-V5-aikajana haetaan watcherin itsensä toimesta, koska sitä ei ole tiedostossa.

#### Valorant (.vrf) {#valorant-vrf}

`%LOCALAPPDATA%\VALORANT\Saved\Demos\*.vrf`, Unreal Engine -paikallinen replay. Avoimena:
replayn tietolohko (pituus, verkkoversio, muutoslista, nimi, milloin se tallennettiin, onko se pakattu tai salattu),
kartta, ottelun tunnus ja valitut agentit (otsikossa), sekä palvelimen oma tapahtumaaikajana - tapot
(tappaja ja uhri verkkotunnuksina, ei nimina), kierrosten alut, piikit asetettu, purettu ja räjähtänyt,
ultimate-kyvyt käytetty, puolten vaihdot - kukin ajallaan, tunnuksellaan ja metatiedoillaan. Sijainnit, nimet, pisteet ja kaikki muu
ovat hämärretyssä virrassa (replay-data- ja checkpoint-osissa), joka tallennetaan kokonaisena eikä lueta.

Samaa moduulia käyttää myös: [League of Legends (replayt)](game-lol-replays.md).

## Sijainnit ja akselit {#positions-and-axes}

| | |
|---|---|
| Sijainnit tallennetaan | ei |
| Ylösakseli | `z` |
| Yksiköt | VALORANT-maailman yksiköt |
| Peilattu katseluohjelmaa varten | ei mitään |
| Yksikköskaala (`scale`: katseluohjelma kertoo sijainnit tällä) | 1 |

Nämä menevät jokaisen session `meta.json`-tiedoston kohtaan `axes` ja, kun sessiossa on sijainteja, `heat.parquet`-tiedoston alatunnisteeseen, joten 3DHeat-katseluohjelma kääntää ja skaalaa rivit itse - katso [Data](the-data.md).

## Moninpeli {#multiplayer}

- Merkitty pelatuksi verkossa (`multiplayer`): **kyllä**. `games --markdown` näyttää tämän muodossa "sallittu (lukee vain sen, minkä peli julkaisee)".
- Tyyppi `replay`: se lukee vain sen, minkä peli tai alusta antaa ulos (pelin tallentamat tallenteet ja demot), joten se tallentaa myös verkkopelissä, aivan kuten offline-pelissäkin; lippu päättää vain sen, saako muistia koskaan lukea.
- Muisti: tämä sovitin **ei koskaan** lue muistia. Vain `memory`-sovittimet lukevat muistia, eikä koskaan peliin, joka on merkitty pelatuksi verkossa - katso [Lähteet ja säännöt](sources-and-rules.md).

## Tilastot {#statistics-recorded}

Tilastoavaimet, jotka tämän sovittimen koodi asettaa nimeltä (jokaisen session `stats` `meta.json`-tiedostossa ja taulukossa `stats` tiedostossa `watcher.sqlite`):

`kills_in_match`, `map`, `match_seconds`, `rounds`, `spikes_planted`

Aaltosulkeissa oleva avain täydennetään ajon aikana (`score.{team}` on yksi avain joukkuetta kohden). Avaimet, jotka koodi ottaa pelin kenttätaulukosta tai pelin omista tilastonimistä, eivät ole tässä luettelossa; "Mitä tallennetaan" -osio nimeää ne.

## Täydellisyys {#completeness}

Watcher noudattaa 3DHeatin [muunnossääntöä](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md): mitä lähde pitää sisällään, se luetaan tai tallennetaan, eikä sitä koskaan jätetä pois. Rivien lisäksi jokainen paketti, sivu, rivi tai vastaus, jonka sovitin vastaanottaa, tallennetaan muuttamattomana session `heat.raw.parquet`-tiedostoon (sarakkeet `time`, `ms`, `type`, `used`, `payload`, `text` ja kaikki nimellä säilytetyt kentät; `used` merkitsee ne, mistä tuli myös rivejä), ja `meta.json`:n `selfCheck.completeness` laskee jokaisen `type`-arvon - `lost` on 0.

**Luettu**

- tietolohko, jokainen kenttä (meta.json `vrf`): tiedoston versio, mukautetut versiot, pituus, verkkoversio, muutoslista, nimi, live-lippu, tallennusaika, pakkaus- ja salauslippu, tallennettu avain
- otsikko-osio: kartta, ottelun tunnus ja valitut agentit (tunnistettuina muotonsa perusteella)
- jokainen tapahtumaosio: tunnus, ryhmä, metatiedot, alku- ja loppuaika, ja sen datasta tapahtuman nimi, sen aika sekunneissa ja sitä edeltävät luvut (tappajan ja uhrin verkkotunnukset) - rivi kullekin

**Tallennettu raakana**

- jokainen osa kokonaisena tiedoston järjestyksessä (`offset`), joten osat ovat tiedosto: `info`, `header`, `event <group>`, `replay_data`, `checkpoint`, `chunk <n>` tyypille, jota asettelu ei nimeä, `trailing` tavuille viimeisen kokonaisen osan jälkeen

**Ei saatavilla**

- sijainnit, nimet, pisteet, kyvyt, jokainen pelin kehys: replay-data- ja checkpoint-osat ovat hämärrettyjä. Tallennettu kokonaisena, ei luettu
- salatun replayn sisältö: käyty läpi ja tallennettu kokonaisena, sisältöä ei luettu

**Koko**: raakatallenne on noin replayn oman kokoinen: hämärretty virta ei pakkaudu

## Testattu {#verified}

lukija (heat3d-riot-replays) on rakennettu vrfkitin (Apache-2.0) dokumentoiman konttirakenteen mukaan; ei testattu oikealla replayllä, sellaista ei ollut saatavilla - tarkistaa ennen lukemista ja ohittaa sen, mikä ei täsmää

## Lähde {#source}

[heat3d_watch/adapters/riot_replays.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/riot_replays.py)

<!-- Generated from the adapter by tools/gen_game_pages.py; change the adapter and run it again rather than editing this page. -->
