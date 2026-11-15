---
title: "Elite Dangerous (lokitiedostot)"
nav_order: 18
lang: "fi"
source: game-elite.md
source_hash: "bb5bcf75553a"
nav_exclude: true
search_exclude: true
---
# Elite Dangerous (lokitiedostot) {#elite-dangerous-log-files}

Kun pelaat Elite Dangerousta, watcher lukee pelin kirjoittamat tiedostot ja tallentaa, mitä tapahtui, jotta voit katsoa sitä myöhemmin kartalta 3DHeat-katseluohjelmassa.

*Tekniset tiedot: sovitin `elite`, tyyppi [`log`](sources-and-rules.md); se toimii, kun `EliteDangerous64.exe` on käynnissä, ja hakee uutta dataa 0,25 s välein.*

## Mitä tallennetaan {#what-is-recorded}

- jokainen matkapäiväkirjan tapahtuma sen päiväkirjanimellä ja sen yksinkertaisilla kentillä
- galaksin sijainti (StarPos, valovuosia) hyppyissä, paikoissa, syntymisissä, kuolemissa, telakoinnissa ja laskeutumisessa
- syntymä LoadGame/Resurrect-tapahtumassa, kuolema Died-tapahtumassa, telakointi ja irtautuminen, kosketus ja irtoaminen, hyppy, session_end
- planeetan pinnan reitti Status.json-tiedostosta: leveysaste, pituusaste, korkeus, suunta ja metrit tangenttitasossa kullekin kappaleelle (sessio = kappaleen nimi), Status.json-tiedoston muut yksinkertaiset kentät (Flags, Flags2, GuiFocus, LegalState, ...)
- jokainen päiväkirjarivi ja jokainen seurantatiedosto kokonaisena heat.raw.parquet-tiedostossa
- hypyt, hypyn matka, kuolemat, tappot, saadut krediitit, suoritetut tehtävät, skannatut kappaleet, vierailtu järjestelmät, telakoinnit, laskeutumiset

## Mistä data tulee {#where-it-comes-from}

Pelaajan päiväkirja %USERPROFILE%\Saved Games\Frontier Developments\Elite Dangerous\Journal.\*.log (uusin tiedosto, seurataan sen kirjoittuessa), Status.json ja muut seurantatiedostot \*.json (Market, Outfitting, Shipyard, NavRoute, Cargo, ModulesInfo, ShipLocker, Backpack, FCMaterials) samassa kansiossa

## Miten se kytketään päälle {#how-to-switch-it-on}

Mitään ei tarvitse kytkeä: watcher lukee lähteen sellaisena kuin peli tai alusta sen antaa.

## Miten se toimii {#how-it-works}

Elite Dangerous: pelaajan päiväkirja ja Status.json, jotka peli kirjoittaa sen käydessä.

Sijainti: `%USERPROFILE%\Saved Games\Frontier Developments\Elite Dangerous\`

* `Journal.<yyyy-mm-ddThhmmss>.<part>.log` - yksi JSON-objekti per rivi, yksi tiedosto
  pelikerran käynnistystä kohden (pitkä sessio jatkuu osassa .02, .03 ...). Jokaisella rivillä
  on `timestamp` (UTC, ISO 8601) ja `event`. Galaktiset sijainnit ovat järjestelmän
  `StarPos` [x, y, z] valovuosina Solista tapahtumissa `FSDJump`,
  `Location` ja `CarrierJump`. Elitin galaktinen koordinaatisto on y ylös (kohti
  galaktista pohjoista), z kohti galaktista keskustaa ja x kohti galaktista pituuspiiriä
  270 - vasenkätinen koordinaatisto, joten katseluohjelma peilaa z:n, jotta se piirtyy oikein päin.
* `Status.json` - kirjoitetaan kokonaisena uudelleen aina, kun aluksen tila muuttuu: `Flags`,
  ja planeetan lähellä `Latitude`, `Longitude` (astetta), `Altitude` (metriä),
  `Heading`, `BodyName` ja `PlanetRadius` (metriä).
* Muut seurantatiedostot, joista jokainen kirjoitetaan kokonaisena uudelleen, kun vastaava
  päiväkirjatapahtuma kirjoitetaan: `Market.json`, `Outfitting.json`, `Shipyard.json`,
  `NavRoute.json`, `Cargo.json`, `ModulesInfo.json`, `ShipLocker.json`,
  `Backpack.json`, `FCMaterials.json`. Jokainen kansion `*.json`-tiedosto, jonka peli kirjoittaa
  tässä istunnossa, tallennetaan kokonaisena joka kerta, kun se muuttuu (3DHeatin muunnossääntö:
  mitä lähde pitää sisällään, se luetaan tai tallennetaan), tiedostonimellään.

Jokainen päiväkirjarivi tallennetaan kokonaisena session raakatiedostoon sen
`event`-nimellä, jokainen seurantatiedosto tiedostonimellään; rivi, joka ei ole JSON, tallennetaan nimellä
`unparsed`.

Pinnan sijainnit sijoitetaan kappaleittain paikalliseen tangenttitasoon metreinä: kappaleen ensimmäinen
kiinnitys on sen origo, x itään, z pohjoiseen, y ylös (korkeus), samalla kätisyydellä kuin galaksin
koordinaatisto, ja rivien `session` on kappaleen nimi, joten ajo tai kävely planeetalla piirtyy omana reittinään.
Galaksirivien session on "galaxy". Molemmat mittakaavat ovat yhdessä taulukossa; valitse sessio
katseluohjelmassa.

Muoto: Frontierin "Elite Dangerous Player Journal" -käsikirja (julkaistu jokaisen päivityksen mukana
virallisilla foorumeilla, <https://forums.frontier.co.uk/> - "Journal Manual", v4.x), tapahtumat ja kentät
kuten siellä on dokumentoitu; Status.json-liput saman käsikirjan "Status File" -luvun mukaan.

## Sijainnit ja akselit {#positions-and-axes}

| | |
|---|---|
| Sijainnit tallennetaan | kyllä |
| Ylösakseli | `y` |
| Yksiköt | valovuosia (galaksirivit, sessio 'galaxy'); metriä itään/ylös/pohjoiseen ensimmäisestä kiinnityksestä kappaleella (pintarivit, sessio = kappaleen nimi) |
| Peilattu katseluohjelmaa varten | `z` |
| Yksikköskaala (`scale`: katseluohjelma kertoo sijainnit tällä) | 1 |

Nämä menevät jokaisen session `meta.json`-tiedoston kohtaan `axes` ja, kun sessiossa on sijainteja, `heat.parquet`-tiedoston alatunnisteeseen, joten 3DHeat-katseluohjelma kääntää ja skaalaa rivit itse - katso [Data](the-data.md).

## Moninpeli {#multiplayer}

- Merkitty pelatuksi verkossa (`multiplayer`): **kyllä**. `games --markdown` näyttää tämän muodossa "sallittu (lukee vain sen, minkä peli julkaisee)".
- Tyyppi `log`: se lukee vain sen, minkä peli tai alusta antaa ulos (tiedostot, joita peli kirjoittaa sen käydessä), joten se tallentaa myös verkkopelissä, aivan kuten offline-pelissäkin; lippu päättää vain sen, saako muistia koskaan lukea.
- Muisti: tämä sovitin **ei koskaan** lue muistia. Vain `memory`-sovittimet lukevat muistia, eikä koskaan peliin, joka on merkitty pelatuksi verkossa - katso [Lähteet ja säännöt](sources-and-rules.md).

## Tilastot {#statistics-recorded}

Tilastoavaimet, jotka tämän sovittimen koodi asettaa nimeltä (jokaisen session `stats` `meta.json`-tiedostossa ja taulukossa `stats` tiedostossa `watcher.sqlite`):

`bad_lines`, `bodies_scanned`, `carrier_jumps`, `credits`, `credits_earned`, `deaths`, `distance_ly`, `dockings`, `jumps`, `kills`, `landings`, `missions_completed`, `ship`, `surface_fixes`, `systems_visited`

Aaltosulkeissa oleva avain täydennetään ajon aikana (`score.{team}` on yksi avain joukkuetta kohden). Avaimet, jotka koodi ottaa pelin kenttätaulukosta tai pelin omista tilastonimistä, eivät ole tässä luettelossa; "Mitä tallennetaan" -osio nimeää ne.

## Täydellisyys {#completeness}

Watcher noudattaa 3DHeatin [muunnossääntöä](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md): mitä lähde pitää sisällään, se luetaan tai tallennetaan, eikä sitä koskaan jätetä pois. Rivien lisäksi jokainen paketti, sivu, rivi tai vastaus, jonka sovitin vastaanottaa, tallennetaan muuttamattomana session `heat.raw.parquet`-tiedostoon (sarakkeet `time`, `ms`, `type`, `used`, `payload`, `text` ja kaikki nimellä säilytetyt kentät; `used` merkitsee ne, mistä tuli myös rivejä), ja `meta.json`:n `selfCheck.completeness` laskee jokaisen `type`-arvon - `lost` on 0.

**Luettu**

- jokainen päiväkirjarivi rivinä sen `event`-nimellä yksinkertaisine kenttineen (pelin paikallistettu teksti, kun peli sen antaa; yli 300 merkin tekstit katkaistaan rivillä)
- galaksirivit (StarPos) tapahtumissa FSDJump, CarrierJump, Location, LoadGame, Resurrect, Died, Docked, Undocked, Touchdown, Liftoff, Shutdown; pintarivit Status.json-tiedostosta sekä Touchdown- ja Liftoff-tapahtumista
- Status.json-tiedoston yksinkertaiset kentät (Flags, Flags2, GuiFocus, LegalState, Cargo, FireGroup, Oxygen, Health, Temperature, Gravity, SelectedWeapon, ...) pintariveillä
- tilastot: hypyt, matka, kuolemat, tappot, saadut krediitit, tehtävät, skannatut kappaleet, vierailtu järjestelmät, telakoinnit, laskeutumiset

**Tallennettu raakana**

- jokainen päiväkirjarivi kokonaisena, `type` = sen `event` (FSDJump, Scan, Music, ReceiveText, ...), `used` tosi: listat ja oliot, joita rivit eivät sisällä (StarPos, Factions, Rewards, Killers, Materials, Modules, ...), ovat vain täällä
- päiväkirjarivi, joka ei ole JSON, `type` `unparsed`
- jokainen seurantatiedosto kokonaisena joka kerta, kun peli kirjoittaa sen uudelleen, `type` = sen tiedostonimi: `Status.json` (`used`, kun se teki pintarivin), `Market.json`, `Outfitting.json`, `Shipyard.json`, `NavRoute.json`, `Cargo.json`, `ModulesInfo.json`, `ShipLocker.json`, `Backpack.json`, `FCMaterials.json` ja mikä tahansa muu `*.json`, jonka peli kirjoittaa sinne

**Ei saatavilla**

- sijainti hyppyjen välissä (järjestelmän sisällä, supercruisessa tai normaalissa avaruudessa): peli kirjoittaa vain järjestelmän StarPos-arvon ja planeetan lähellä leveys-, pituusasteen ja korkeuden
- muiden alusten ja pelaajien sijainnit: päiväkirja on komentajan oma kertomus
- nopeus, kaasu ja muu lentotelemetria: peli ei kirjoita niitä
- aiempien istuntojen päiväkirjat ja seurantatiedostot: tallennetaan, kun niitä pelattiin (seuraaja alkaa tiedoston lopusta, jos tiedosto on vanhempi kuin tämä pelikerta)
- Frontierin yhteyskäyttöliittymä (cAPI): vaatii pelaajan Frontier-kirjautumisen; ei ole tiedosto, jonka peli kirjoittaa

**Koko**: noin 1-5 MB raakatekstiä tunnissa: päiväkirja 0,2-2 MB, Status.json (alle 1 KB, kirjoitetaan jopa joka sekunti) 1-2 MB, markkina-, varustelu- ja telakkasarja 20-150 KB per vierailtu asema; zstd heat.raw.parquet-tiedostossa tekee siitä noin kymmenesosan

## Testattu {#verified}

jäsennin toistettu todellisista päiväkirjatiedostoista paikallisesta asennuksesta (tapahtumamäärät täsmäävät tilastoihin); Status.json-pintakiinnitykset testattu vain synteettisillä kuvilla

## Lähde {#source}

[heat3d_watch/adapters/elite.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/elite.py)

<!-- Generated from the adapter by tools/gen_game_pages.py; change the adapter and run it again rather than editing this page. -->
