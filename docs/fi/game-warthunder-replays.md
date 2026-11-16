---
title: "War Thunder (tallenteet)"
nav_order: 45
lang: "fi"
source: game-warthunder-replays.md
source_hash: "4bf6e2f218cb"
nav_exclude: true
search_exclude: true
---
# War Thunder (tallenteet) {#war-thunder-replays}

Kun War Thunder -taistelu on päättynyt, vahti muuttaa pelin tallentaman tallenteen tiedostoiksi, joita voi katsella kartalla 3DHeat-katselimessa.

*Tekniset tiedot: sovitin `warthunder-replays`, laji [`replay`](sources-and-rules.md); se toimii koko ajan (ei odota pelin alkua) ja etsii uutta dataa 5 s välein.*

## Mitä tallennetaan {#what-is-recorded}

- jokaisen ilma-aluksen sijainti ja asento noin 4 kertaa sekunnissa (niin monta kuin tallenne sisältää)
- maayksiköiden sijainnit tallenteen maasynkronoinnista (vuoden 2026 tallenteissa; ei vuoden 2025 tallenteissa)
- kuka kukin yksikkö oli (pelaaja, ajoneuvon tunnus, joukkue) siellä, missä tappo tai osuma sen nimeää; tappot, kuolemat ja osumat siellä, missä ne tapahtuivat; chat; kartta
- tallenteen tekijän tapot, kuolemat, pisteet ja valtaukset tilastoina

## Mistä se tulee {#where-it-comes-from}

War Thunderin tallentamat tallenteet: &lt;War Thunder>/Replays/\*.wrpl (kun tallennus on päällä), muuntaa ulkoinen muunnin `heat3d-wt-replay` (exporters/ext/warthunder-replay)

## Miten se otetaan käyttöön {#how-to-switch-it-on}

ota tallenteiden tallennus päälle War Thunderin asetuksissa ja asenna muunnin: pip install -e &lt;3DHeat>/exporters/ext/warthunder-replay

Asetukset ympäristömuuttujista:

- `HEAT3D_WT_REPLAY`: muuntimen kansio (kloonaus tai purettu julkaisu), kun se ei ole asennettu tai vahdin vieressä

## Miten se toimii {#how-it-works}

Tallenteet ja demot: mitä peli tallentaa ottelusta, muunnetaan kun ottelu on ohi.

Tallenne sisältää kaiken, minkä elävä näkymä pitää moninpeleissä piilossa — jokaisen pelaajan sijainnin, jokaisen tappon siellä, missä se tapahtui — ja se on tiedosto, jonka peli kirjoittaa pelaajilleen, joten sen lukeminen ei kosketa peliin mitenkään. Vahti katsoo kansioita, joihin pelit tallentavat ne, odottaa että uusi tiedosto lakkaa kasvamasta (muuten peli kirjoittaa sitä vielä) ja muuntaa sen työsäikeessä, jotta pitkä muunnos ei pysäytä muuta vahtia.

Kun kansio nähdään ensimmäisen kerran, siinä jo olevia tallenteita vain merkitään, niitä ei muunneta: pelaajalla, jolla on vuosien demot, vahti olisi muuten kiireinen päivän ajan. `python -m heat3d_watch replays <adapter> [folder]` muuntaa olemassa olevat pyynnöstä.

#### War Thunder {#war-thunder}

War Thunder tallentaa jokaisen taistelun tallenteen kansioon `<War Thunder>/Replays/*.wrpl`, kun tallennus on päällä sen asetuksissa. Vahti ei lue niitä itse: ulkoinen muunnin lukee (3DHeat War Thunder -tallennemuunnin, `exporters/ext/warthunder-replay`, komento `heat3d-wt-replay`), oma projektinsa. Kun komento on PATH:lla, tai paketti on asennettu tai vahdin vieressä, jokainen uusi tallenne ajetaan sen läpi sessiokansioon `<map>/<match>.parquet`- ja `<match>.match.json`-tiedostoina. Kun se ei ole, vahti kertoo kerran, miten se asennetaan, ja jättää kansion rauhaan. Mitä muunnin lukee ja mitä ei, on sen README:ssä. Tallenteen tekijän rivi tuloksista (tapot, maayksikkötapot, kuolemat, avustukset, pisteet, valtaukset) tulee session tilastoiksi.

Saman moduulin kautta toimivat myös: [Counter-Strike 2 (tallenteet)](game-cs2-demos.md), [Dota 2 (tallenteet)](game-dota-replays.md), [Squad (tallenteet)](game-squad-demos.md), [World of Tanks (tallenteet)](game-wot-replays.md), [World of Warships (tallenteet)](game-wows-replays.md).

## Sijainnit ja akselit {#positions-and-axes}

| | |
|---|---|
| Sijainnit tallennettu | kyllä |
| Ylösakseli | `y` |
| Yksiköt | metriä (x itä, y ylös, z pohjoinen) |
| Peilattu katselimelle | `z` |
| Yksikkömittakaava (`scale`: katselin kertoo sijainnit sillä) | 1 |

Nämä tulevat kunkin session `meta.json`-tiedoston kohtaan `axes` ja, kun sessiossa on sijainteja, `heat.parquet`-tiedoston alatunnisteeseen, joten 3DHeat-katselin kääntää ja skaalaa rivit itse — katso [Data](the-data.md).

## Moninpeli {#multiplayer}

- Merkitty pelatuksi verkossa (`multiplayer`): **kyllä**. `games --markdown` näyttää tämän muodossa "allowed (reads only what the game publishes)".
- Laji `replay`: se lukee vain sen, minkä peli tai alusta antaa ulos (pelin tallentamat tallenteet ja demot), joten se tallentaa myös verkkopelissä eikä vain offline-pelissä; lippu päättää vain, saako muistia koskaan lukea.
- Muisti: **ei koskaan**. Tämä sovitin ei lue muistia. Vain `memory`-sovittimet lukevat muistia, eikä koskaan peliltä, joka on merkitty pelatuksi verkossa — katso [Lähteet ja säännöt](sources-and-rules.md).

## Tilastot {#statistics-recorded}

Tilastoavaimet, jotka tämän sovittimen koodi asettaa nimeltä (kunkin session `stats` `meta.json`-tiedostossa ja `watcher.sqlite`-tiedoston `stats`-taulussa):

`map`

Aaltosulkeissa oleva avain täydennetään ajon aikana (`score.{team}` on yksi avain joukkuetta kohti). Avaimet, jotka koodi ottaa pelin kentistä tai pelin omista tilastonimistä taulukosta, eivät ole tässä luettelossa; kohdassa "Mitä tallennetaan" ne mainitaan.

## Täydellisyys {#completeness}

Muunnin, jota tämä sovitin ajaa, noudattaa 3DHeatin [muunnossääntöä](https://github.com/Holdi601/3DHeat/blob/main/docs/converters.md): mitä tallenne sisältää, se luetaan tai säilytetään, sitä ei koskaan pudoteta — luettuna taulukkoon ja ottelun asiakirjaan, kaikki muu kokonaisena sivutiedostoina niiden vieressä, ja laskettuna ottelun asiakirjan `selfCheck.completeness`-kohtaan. Muuntimen oma dokumentaatio luettelee, mitä se lukee, säilyttää raakana ja ei osaa lukea.

## Todennettu {#verified}

Muunnin on tarkistettu julkisilla tallenteilla useista peliversioista (tappot ja nimet täsmäävät tuloksiin) ja testeillä rakennetuilla tallenteilla; tämä koukku testeillä korvaavalla komennolla.

## Lähde {#source}

[heat3d_watch/adapters/replays.py](https://github.com/Holdi601/3DHeat-Watcher/blob/main/heat3d_watch/adapters/replays.py)

<!-- Generated from the adapter by tools/gen_game_pages.py; change the adapter and run it again rather than editing this page. -->
