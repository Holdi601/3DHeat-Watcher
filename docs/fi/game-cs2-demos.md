---
title: "Counter-Strike 2 (tallenteet)"
nav_order: 8
lang: "fi"
source: game-cs2-demos.md
source_hash: "82fe00f0f2f0"
nav_exclude: true
search_exclude: true
---
# Counter-Strike 2 (tallenteet) {#counter-strike-2-replays}

Kun Counter-Strike 2 -ottelu on päättynyt, vahti muuttaa pelin tallentaman tallenteen tiedostoiksi, joita voi katsella kartalla 3DHeat-katselimessa.

*Tekniset tiedot: sovitin `cs2-demos`, laji [`replay`](sources-and-rules.md); se toimii koko ajan (ei odota pelin alkua) ja etsii uutta dataa 5 s välein.*

## Mitä tallennetaan {#what-is-recorded}

- jokaisen pelaajan sijainti, katselusuunta, terveys ja raha (joka 8. tikki)
- tappot, kuolemat, vahinko, kranaatit, pommin asetukset ja purkamiset siellä, missä ne tapahtuivat
- kierrokset, tulos ja talous; sisäänkirjautuneen pelaajan tulostaulun rivi tilastoina

## Mistä se tulee {#where-it-comes-from}

CS2:n tallentamat demot: &lt;CS2>/game/csgo/replays/\*.dem (ladattu ottelohistoriasta) ja &lt;CS2>/game/csgo/\*.dem (tallennetut)

## Miten se otetaan käyttöön {#how-to-switch-it-on}

lataa ottelun demo CS2:ssa (Watch > Your Matches) tai tallenna se konsolin komennolla `record`

Asetukset ympäristömuuttujista:

- `HEAT3D_CS2`: 3DHeat CS2 -kansio, kun se ei ole vahdin vieressä tai asennettuna

## Miten se toimii {#how-it-works}

Tallenteet ja demot: mitä peli tallentaa ottelusta, muunnetaan kun ottelu on ohi.

Tallenne sisältää kaiken, minkä elävä näkymä pitää moninpeleissä piilossa — jokaisen pelaajan sijainnin, jokaisen tappon siellä, missä se tapahtui — ja se on tiedosto, jonka peli kirjoittaa pelaajilleen, joten sen lukeminen ei kosketa peliin mitenkään. Vahti katsoo kansioita, joihin pelit tallentavat ne, odottaa että uusi tiedosto lakkaa kasvamasta (muuten peli kirjoittaa sitä vielä) ja muuntaa sen työsäikeessä, jotta pitkä muunnos ei pysäytä muuta vahtia.

Kun kansio nähdään ensimmäisen kerran, siinä jo olevia tallenteita vain merkitään, niitä ei muunneta: pelaajalla, jolla on vuosien demot, vahti olisi muuten kiireinen päivän ajan. `python -m heat3d_watch replays <adapter> [folder]` muuntaa olemassa olevat pyynnöstä.

#### Counter-Strike 2 {#counter-strike-2}

CS2 tallentaa pelaajan ottelohistoriasta (Watch-välilehti) ladatut demot kansioon `<CS2>/game/csgo/replays/` ja `record`-konsolikomennolla tallennetut kansioon `<CS2>/game/csgo/`. Jokainen muunnetaan tämän repositorion omalla CS2-muuntimella (3DHeat CS2, github.com/Holdi601/3DHeat-CS2: jokaisen pelaajan sijainti, katselusuunta, terveys ja raha joka kahdeksas tikki; tappot, kuolemat, vahinko, kranaatit, pommit ja purkamiset siellä, missä ne tapahtuivat; kierrokset, tulos ja talous) sessiokansioon taulukkona `<map>/<match>.parquet` ja yhteenvetona `<match>.match.json`, joita katselimen Lämpökartta- ja Ottelu-välilehdet lukevat. Ottelun tulostaulusta tulee session tilastot sille pelaajalle, jonka Steam-tili on kirjautuneena tälle koneelle (Steamin `loginusers.vdf`-tiedostosta), selkeillä nimillä: tappot, kuolemat, avustukset, ADR, KAST, headshot-prosentti, avausrunnat ja clutchit, sekä tulos ja kierrokset.

Saman moduulin kautta toimivat myös: [Dota 2 (tallenteet)](game-dota-replays.md), [Squad (tallenteet)](game-squad-demos.md), [War Thunder (tallenteet)](game-warthunder-replays.md), [World of Tanks (tallenteet)](game-wot-replays.md), [World of Warships (tallenteet)](game-wows-replays.md).

## Sijainnit ja akselit {#positions-and-axes}

| | |
|---|---|
| Sijainnit tallennettu | kyllä |
| Ylösakseli | `z` |
| Yksiköt | tuumat (Source-yksiköt) |
| Peilattu katselimelle | `y` |
| Yksikkömittakaava (`scale`: katselin kertoo sijainnit sillä) | 1 |

Nämä tulevat kunkin session `meta.json`-tiedoston kohtaan `axes` ja, kun sessiossa on sijainteja, `heat.parquet`-tiedoston alatunnisteeseen, joten 3DHeat-katselin kääntää ja skaalaa rivit itse — katso [Data](the-data.md).

## Moninpeli {#multiplayer}

- Merkitty pelatuksi verkossa (`multiplayer`): **kyllä**. `games --markdown` näyttää tämän muodossa "allowed (reads only what the game publishes)".
- Laji `replay`: se lukee vain sen, minkä peli tai alusta antaa ulos (pelin tallentamat tallenteet ja demot), joten se tallentaa myös verkkopelissä eikä vain offline-pelissä; lippu päättää vain, saako muistia koskaan lukea.
- Muisti: **ei koskaan**. Tämä sovitin ei lue muistia. Vain `memory`-sovittimet lukevat muistia, eikä koskaan peliltä, joka on merkitty pelatuksi verkossa — katso [Lähteet ja säännöt](sources-and-rules.md).

## Tilastot {#statistics-recorded}

Tilastoavaimet, jotka tämän sovittimen koodi asettaa nimeltä (kunkin session `stats` `meta.json`-tiedostossa ja `watcher.sqlite`-tiedoston `stats`-taulussa):

`map`, `rounds`, `score.{team}`, `won`

Aaltosulkeissa oleva avain täydennetään ajon aikana (`score.{team}` on yksi avain joukkuetta kohti). Avaimet, jotka koodi ottaa pelin kentistä tai pelin omista tilastonimistä taulukosta, eivät ole tässä luettelossa; kohdassa "Mitä tallennetaan" ne mainitaan.

## Täydellisyys {#completeness}

Muunnin, jota tämä sovitin ajaa, noudattaa 3DHeatin [muunnossääntöä](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md): mitä tallenne sisältää, se luetaan tai säilytetään, sitä ei koskaan pudoteta — luettuna taulukkoon ja ottelun asiakirjaan, kaikki muu kokonaisena sivutiedostoina niiden vieressä, ja laskettuna ottelun asiakirjan `selfCheck.completeness`-kohtaan. Muuntimen oma dokumentaatio luettelee, mitä se lukee, säilyttää raakana ja ei osaa lukea.

## Todennettu {#verified}

Muunnin on testattu oikeilla turnausdemoilla; kansion vahti ja tilastot testeillä.

## Lähde {#source}

[heat3d_watch/adapters/replays.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/replays.py)

<!-- Generated from the adapter by tools/gen_game_pages.py; change the adapter and run it again rather than editing this page. -->
