---
title: "World of Warships (tallenteet)"
nav_order: 48
lang: "fi"
source: game-wows-replays.md
source_hash: "44a041452521"
nav_exclude: true
search_exclude: true
---
# World of Warships (tallenteet) {#world-of-warships-replays}

Kun World of Warships -ottelu on päättynyt, vahti muuttaa pelin tallentaman tallenteen tiedostoiksi, joita voi katsella kartalla 3DHeat-katselimessa.

*Tekniset tiedot: sovitin `wows-replays`, laji [`replay`](sources-and-rules.md); se toimii koko ajan (ei odota pelin alkua) ja etsii uutta dataa 5 s välein.*

## Mitä tallennetaan {#what-is-recorded}

- jokaisen laivan sijainti ja suunta niin kauan kuin tallentava asiakas näki sen (noin 6–7 kertaa sekunnissa liikkuessa), pelaajan oma laiva koko ajan
- pelaaja, liittolainen tai vihollinen, sekä laiva (tallentavan pelaajan laiva nimeltä, muut pelin laivanumeron mukaan); uponneet laivat siellä, missä ne upposivat, ja niiden tappajat siellä, missä nämä seisoivat
- kartta; tallentavan pelaajan laiva, tapot ja selviytyminen tilastoina

## Mistä se tulee {#where-it-comes-from}

World of Warshipsin tallentamat tallenteet: &lt;World of Warships>/replays/\*.wowsreplay (tallenteet päällä), muuntaa ulkoinen muunnin `heat3d-wows-replay` (exporters/ext/wows-replay)

## Miten se otetaan käyttöön {#how-to-switch-it-on}

ota tallenteen tallennus päälle World of Warshipsissa (`isReplayEnabled` sen preferences.xml-tiedostossa tai pelin oma asetus, jos sellainen on) ja asenna muunnin: pip install -e &lt;3DHeat>/exporters/ext/wows-replay

Asetukset ympäristömuuttujista:

- `HEAT3D_WOWS_REPLAY`: muuntimen kansio (kloonaus tai purettu julkaisu), kun se ei ole asennettu tai vahdin vieressä

## Miten se toimii {#how-it-works}

Tallenteet ja demot: mitä peli tallentaa ottelusta, muunnetaan kun ottelu on ohi.

Tallenne sisältää kaiken, minkä elävä näkymä pitää moninpeleissä piilossa — jokaisen pelaajan sijainnin, jokaisen tappon siellä, missä se tapahtui — ja se on tiedosto, jonka peli kirjoittaa pelaajilleen, joten sen lukeminen ei kosketa peliin mitenkään. Vahti katsoo kansioita, joihin pelit tallentavat ne, odottaa että uusi tiedosto lakkaa kasvamasta (muuten peli kirjoittaa sitä vielä) ja muuntaa sen työsäikeessä, jotta pitkä muunnos ei pysäytä muuta vahtia.

Kun kansio nähdään ensimmäisen kerran, siinä jo olevia tallenteita vain merkitään, niitä ei muunneta: pelaajalla, jolla on vuosien demot, vahti olisi muuten kiireinen päivän ajan. `python -m heat3d_watch replays <adapter> [folder]` muuntaa olemassa olevat pyynnöstä.

#### World of Tanks ja World of Warships {#world-of-tanks-and-world-of-warships}

Molemmat tallentavat jokaisen taistelun tallenteen kansioon `<game>/replays/`, kun tallennus on päällä (`*.wotreplay`, `*.wowsreplay`). Asennukset löytyvät Wargaming Game Centerin listasta, `C:/Games/World_of_Tanks*` ja `World_of_Warships*`, sekä Steamista. Kuten War Thunderissa, vahti ei lue tiedostoja itse: kummankin ulkoinen muunnin lukee (`exporters/ext/wot-replay`, komento `heat3d-wot-replay`; `exporters/ext/wows-replay`, komento `heat3d-wows-replay`), erillään, jotta Wargamingin ehtoihin liittyvä ongelma koskee vain sitä muunninta. Kun muunnin löytyy PATH:lta, on asennettu tai vahdin vieressä, se muuntaa jokaisen uuden tallenteen tiedostoiksi `<map>/<match>.parquet` ja `<match>.match.json` sessiokansioon; kun se puuttuu, vahti kertoo kerran, miten se asennetaan. Tallentavan pelaajan rivi (ajoneuvo tai laiva, tapot, vahinko (World of Tanks), selvisikö hän ja tulos (World of Tanks)) tulee session tilastoiksi. Mitä kukin muunnin lukee ja mitä ei, on sen README:ssä.

Saman moduulin kautta toimivat myös: [Counter-Strike 2 (tallenteet)](game-cs2-demos.md), [Dota 2 (tallenteet)](game-dota-replays.md), [Squad (tallenteet)](game-squad-demos.md), [War Thunder (tallenteet)](game-warthunder-replays.md), [World of Tanks (tallenteet)](game-wot-replays.md).

## Sijainnit ja akselit {#positions-and-axes}

| | |
|---|---|
| Sijainnit tallennettu | kyllä |
| Ylösakseli | `y` |
| Yksiköt | World of Warshipsin maailmayksiköt (x itä, y ylös, z pohjoinen; yksi on 15 m rungon geometrian mukaan, 30 m pelin kantamien mukaan) |
| Peilattu katselimelle | `z` |
| Yksikkömittakaava (`scale`: katselin kertoo sijainnit sillä) | 1 |

Nämä tulevat kunkin session `meta.json`-tiedoston kohtaan `axes` ja, kun sessiossa on sijainteja, `heat.parquet`-tiedoston alatunnisteeseen, joten 3DHeat-katselin kääntää ja skaalaa rivit itse — katso [Data](the-data.md).

## Moninpeli {#multiplayer}

- Merkitty pelatuksi verkossa (`multiplayer`): **kyllä**. `games --markdown` näyttää tämän muodossa "allowed (reads only what the game publishes)".
- Laji `replay`: se lukee vain sen, minkä peli tai alusta antaa ulos (pelin tallentamat tallenteet ja demot), joten se tallentaa myös verkkopelissä eikä vain offline-pelissä; lippu päättää vain, saako muistia koskaan lukea.
- Muisti: **ei koskaan**. Tämä sovitin ei lue muistia. Vain `memory`-sovittimet lukevat muistia, eikä koskaan peliltä, joka on merkitty pelatuksi verkossa — katso [Lähteet ja säännöt](sources-and-rules.md).

## Tilastot {#statistics-recorded}

Tilastoavaimet, jotka tämän sovittimen koodi asettaa nimeltä (kunkin session `stats` `meta.json`-tiedostossa ja `watcher.sqlite`-tiedoston `stats`-taulussa):

`map`, `survived`, `vehicle`, `won`

Aaltosulkeissa oleva avain täydennetään ajon aikana (`score.{team}` on yksi avain joukkuetta kohti). Avaimet, jotka koodi ottaa pelin kentistä tai pelin omista tilastonimistä taulukosta, eivät ole tässä luettelossa; kohdassa "Mitä tallennetaan" ne mainitaan.

## Täydellisyys {#completeness}

Muunnin, jota tämä sovitin ajaa, noudattaa 3DHeatin [muunnossääntöä](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md): mitä tallenne sisältää, se luetaan tai säilytetään, sitä ei koskaan pudoteta — luettuna taulukkoon ja ottelun asiakirjaan, kaikki muu kokonaisena sivutiedostoina niiden vieressä, ja laskettuna ottelun asiakirjan `selfCheck.completeness`-kohtaan. Muuntimen oma dokumentaatio luettelee, mitä se lukee, säilyttää raakana ja ei osaa lukea.

## Todennettu {#verified}

Muunnin on tarkistettu julkisilla tallenteilla useista peliversioista ja testeillä rakennetuilla tallenteilla; tämä koukku testeillä korvaavalla komennolla.

## Lähde {#source}

[heat3d_watch/adapters/replays.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/replays.py)

<!-- Generated from the adapter by tools/gen_game_pages.py; change the adapter and run it again rather than editing this page. -->
