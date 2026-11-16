---
title: "Squad (tallenteet)"
nav_order: 40
lang: "fi"
source: game-squad-demos.md
source_hash: "ddec19ea89bf"
nav_exclude: true
search_exclude: true
---
# Squad (tallenteet) {#squad-replays}

Kun Squad-ottelu on päättynyt, vahti muuttaa pelin tallentaman tallenteen tiedostoiksi, joita voi katsella kartalla 3DHeat-katselimessa.

*Tekniset tiedot: sovitin `squad-demos`, laji [`replay`](sources-and-rules.md); se toimii koko ajan (ei odota pelin alkua) ja etsii uutta dataa 5 s välein.*

## Mitä tallennetaan {#what-is-recorded}

- jokaisen pelaajan sijainti, rungon kiertokulma (body yaw) ja nopeus joka kerta, kun palvelin replikoi ne (enintään 8 kertaa sekunnissa), jalan ja maayksiköissä
- jokaisen pelaajan nimi, joukkue, faktio ja ryhmä (squad), seuraten joukkueenvaihdoksia
- ei: helikoptereiden liike, tappot ja asennettavat esineet — katso lukijan README

## Mistä se tulee {#where-it-comes-from}

palvelimen demot, jotka Squad tallentaa ylläpitäjän komennolla AdminDemoRec: &lt;server>/SquadGame/Saved/Demos/\*.replay, luetaan ulkoisella lukijalla `heat3d-squad-demo` (exporters/ext/squad-demo)

## Miten se otetaan käyttöön {#how-to-switch-it-on}

tallenna palvelimella: anna ylläpitäjälle `demos`-oikeus tiedostossa Admins.cfg, sitten pelin konsolissa AdminDemoRec &lt;name> ja AdminDemoStop; kopioi demo tänne ja asenna lukija: pip install -e &lt;3DHeat>/exporters/ext/squad-demo

Asetukset ympäristömuuttujista:

- `HEAT3D_SQUAD_DEMO`: muuntimen kansio (kloonaus tai purettu julkaisu), kun se ei ole asennettu tai vahdin vieressä

## Miten se toimii {#how-it-works}

Tallenteet ja demot: mitä peli tallentaa ottelusta, muunnetaan kun ottelu on ohi.

Tallenne sisältää kaiken, minkä elävä näkymä pitää moninpeleissä piilossa — jokaisen pelaajan sijainnin, jokaisen tappon siellä, missä se tapahtui — ja se on tiedosto, jonka peli kirjoittaa pelaajilleen, joten sen lukeminen ei kosketa peliin mitenkään. Vahti katsoo kansioita, joihin pelit tallentavat ne, odottaa että uusi tiedosto lakkaa kasvamasta (muuten peli kirjoittaa sitä vielä) ja muuntaa sen työsäikeessä, jotta pitkä muunnos ei pysäytä muuta vahtia.

Kun kansio nähdään ensimmäisen kerran, siinä jo olevia tallenteita vain merkitään, niitä ei muunneta: pelaajalla, jolla on vuosien demot, vahti olisi muuten kiireinen päivän ajan. `python -m heat3d_watch replays <adapter> [folder]` muuntaa olemassa olevat pyynnöstä.

#### Squad {#squad}

Squadin dedikoidut palvelimet tallentavat ottelun demon, kun ylläpitäjä, jolla on `demos`-oikeus, ajaa komennon AdminDemoRec &lt;name> (ja AdminDemoStop), kansioon `<server>/SquadGame/Saved/Demos/<name>.replay`. Se on Unreal Enginen verkkotallenne, joka sisältää sen, minkä palvelin replikoi, myös jokaisen pelaajan liikkeen. Vahti ei lue niitä itse: sen lukee ulkoinen lukija (3DHeat Squad demo -lukija, `exporters/ext/squad-demo`, komento `heat3d-squad-demo`), oma projektinsa. Lukijaa ajetaan jokaiselle uudelle demolle kansioissa, joihin paikallinen palvelin kirjoittaa, tai kansiossa, jonka asetukset lisäävät vuokratulta palvelimelta kopioituja demoja varten, ja tulos menee sessiokansioon `<map>/<match>.parquet`- ja `<match>.match.json`-tiedostoina. Taso, kartta, pelaajamäärä ja ottelun kesto tulevat session tilastoiksi.

Saman moduulin kautta toimivat myös: [Counter-Strike 2 (tallenteet)](game-cs2-demos.md), [Dota 2 (tallenteet)](game-dota-replays.md), [War Thunder (tallenteet)](game-warthunder-replays.md), [World of Tanks (tallenteet)](game-wot-replays.md), [World of Warships (tallenteet)](game-wows-replays.md).

## Sijainnit ja akselit {#positions-and-axes}

| | |
|---|---|
| Sijainnit tallennettu | kyllä |
| Ylösakseli | `z` |
| Yksiköt | Unreal-yksiköt (senttimetrit) |
| Peilattu katselimelle | ei mitään |
| Yksikkömittakaava (`scale`: katselin kertoo sijainnit sillä) | 1 |

Nämä tulevat kunkin session `meta.json`-tiedoston kohtaan `axes` ja, kun sessiossa on sijainteja, `heat.parquet`-tiedoston alatunnisteeseen, joten 3DHeat-katselin kääntää ja skaalaa rivit itse — katso [Data](the-data.md).

## Moninpeli {#multiplayer}

- Merkitty pelatuksi verkossa (`multiplayer`): **kyllä**. `games --markdown` näyttää tämän muodossa "allowed (reads only what the game publishes)".
- Laji `replay`: se lukee vain sen, minkä peli tai alusta antaa ulos (pelin tallentamat tallenteet ja demot), joten se tallentaa myös verkkopelissä eikä vain offline-pelissä; lippu päättää vain, saako muistia koskaan lukea.
- Muisti: **ei koskaan**. Tämä sovitin ei lue muistia. Vain `memory`-sovittimet lukevat muistia, eikä koskaan peliltä, joka on merkitty pelatuksi verkossa — katso [Lähteet ja säännöt](sources-and-rules.md).

## Tilastot {#statistics-recorded}

Tilastoavaimet, jotka tämän sovittimen koodi asettaa nimeltä (kunkin session `stats` `meta.json`-tiedostossa ja `watcher.sqlite`-tiedoston `stats`-taulussa):

`layer`, `map`, `match_seconds`, `players`

Aaltosulkeissa oleva avain täydennetään ajon aikana (`score.{team}` on yksi avain joukkuetta kohti). Avaimet, jotka koodi ottaa pelin kentistä tai pelin omista tilastonimistä taulukosta, eivät ole tässä luettelossa; kohdassa "Mitä tallennetaan" ne mainitaan.

## Täydellisyys {#completeness}

Muunnin, jota tämä sovitin ajaa, noudattaa 3DHeatin [muunnossääntöä](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md): mitä tallenne sisältää, se luetaan tai säilytetään, sitä ei koskaan pudoteta — luettuna taulukkoon ja ottelun asiakirjaan, kaikki muu kokonaisena sivutiedostoina niiden vieressä, ja laskettuna ottelun asiakirjan `selfCheck.completeness`-kohtaan. Muuntimen oma dokumentaatio luettelee, mitä se lukee, säilyttää raakana ja ei osaa lukea.

## Todennettu {#verified}

Lukija on tarkistettu julkisilla palvelindemoilla (liike täsmää mukana kulkevan nopeuden kanssa; jokaisen rivin joukkue vastaa sen sotilaan faktiota) ja testeillä rakennetuilla demoilla; tämä koukku testeillä korvaavalla komennolla.

## Lähde {#source}

[heat3d_watch/adapters/replays.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/replays.py)

<!-- Generated from the adapter by tools/gen_game_pages.py; change the adapter and run it again rather than editing this page. -->
